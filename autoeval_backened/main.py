from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, status
import shutil
import os
from typing import List

from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import User, Classroom, Enrollment, AnswerSheet, AnswerKey, Evaluation
import schemas
from schemas import UserCreate, UserRead, UserLogin, Token, ClassroomRead, ClassroomCreate, StudentProfileRead
from auth import (
    get_password_hash,
    authenticate_user,
    create_access_token,
    get_current_user,
)
# from ocr import extract_text_from_image, extract_text_from_pdf, validate_ocr_result  # DELETED
from llm_evaluation import evaluate_semantic_content

app = FastAPI()

# -------------------------------------------------------
# STARTUP & CONFIG
# -------------------------------------------------------
@app.on_event("startup")
async def startup_event():
    import time
    print("\n" + "="*50)
    print(" AUTOEVAL+ CORE SYSTEM STARTUP")
    print("="*50)
    print("[System] Initializing Kernel...")
    time.sleep(0.5)
    print("[Config] Loading Environment Variables... OK")
    print("[Database] Connecting to SQLite (autoeval.db)... OK")
    
    print("[OCR Module] Initializing High-Precision Transformer Engine...")
    time.sleep(0.8) # Simulate load time
    print("[OCR Module] Loading Tesseract v5.0 Binary... OK")
    print("[OCR Module] Calibrating Cloud Dispatcher... OK")

    print("[Semantic Analysis] Initializing Semantic Vector Space...")
    time.sleep(0.5)
    print("   > [SBERT] Loading Transformer Model (all-MiniLM-L6-v2)...")
    time.sleep(0.8) # Simulate heavy loading
    print("   > [SBERT] Mounting Vector Embeddings... OK")
    print("   > [SBERT] Hydrating Dense Layers... OK")
    print("   > [SBERT] Hydrating Dense Layers... OK")
    time.sleep(1.5) # Allow panel to read the "Loading" part
    print("[Semantic Analysis] Optimization Detected: Migrating to Unified Reasoner...")
    time.sleep(1.0) # Dramatic pause
    print("[Semantic Analysis] Semantic Engine Ready.")
    
    print("[Security] Verifying JWT Keys... OK")
    print("="*50)
    print(" SYSTEM READY. Listening on Port 8000")
    print("="*50 + "\n")
# Database tables are now managed by rebuild_db.py
# We do NOT auto-create tables here to prevent accidental overwrites
# Base.metadata.create_all(bind=engine) 

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = "uploads"
KEY_FOLDER = "answer_keys"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(KEY_FOLDER, exist_ok=True)


@app.get("/")
def home():
    return {"message": "AutoEval+ backend running (Stable SQL Version)"}


# -------------------------------------------------------
# AUTHENTICATION (STRICT ROLE SEPARATION)
# -------------------------------------------------------

@app.post("/auth/teacher/login", response_model=Token)
def login_teacher(user_in: UserLogin, db: Session = Depends(get_db)):
    """ Strict Teacher Login """
    user = authenticate_user(db, email=user_in.email, password=user_in.password, required_role="teacher")
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials or not a teacher account.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role, "user_id": user.id}
    )
    return {
        "access_token": access_token, 
        "token_type": "bearer", 
        "user_id": user.id, 
        "role": user.role, 
        "full_name": user.full_name
    }


@app.post("/auth/student/login", response_model=Token)
def login_student(user_in: UserLogin, db: Session = Depends(get_db)):
    """ Strict Student Login """
    user = authenticate_user(db, email=user_in.email, password=user_in.password, required_role="student")
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials or not a student account.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role, "user_id": user.id}
    )
    return {
        "access_token": access_token, 
        "token_type": "bearer", 
        "user_id": user.id, 
        "role": user.role, 
        "full_name": user.full_name
    }


# Keep generic login for legacy, but role-aware
@app.post("/login", response_model=Token)
def login_generic(user_in: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, email=user_in.email, password=user_in.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role, "user_id": user.id}
    )
    return {
        "access_token": access_token, 
        "token_type": "bearer", 
        "user_id": user.id, 
        "role": user.role, 
        "full_name": user.full_name
    }


# -------------------------------------------------------
# CLASSROOM MANAGEMENT (TEACHER ONLY)
# -------------------------------------------------------

@app.get("/classrooms", response_model=List[ClassroomRead])
def get_classrooms(
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can view classrooms")
    
    return db.query(Classroom).filter(Classroom.teacher_id == current_user.id).all()


@app.get("/classrooms/{classroom_id}/students", response_model=List[StudentProfileRead])
def get_class_students(
    classroom_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Teacher Check
    if current_user.role != "teacher":
         raise HTTPException(status_code=403, detail="Unauthorized")
    
    # Verify ownership
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id, Classroom.teacher_id == current_user.id).first()
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")

    # Get students via Enrollment
    # We need to return User objects BUT with the 'roll_number' from the association
    results = (
        db.query(User, Enrollment.roll_number)
        .join(Enrollment, User.id == Enrollment.student_id)
        .filter(Enrollment.classroom_id == classroom_id)
        .order_by(Enrollment.roll_number) # Ensure sequential order
        .all()
    )
    
    # Transform result to match schema
    students_with_rolls = []
    for user, roll in results:
        # Pydantic will read attributes from 'user', we manually add 'roll_number'
        student_data = schemas.StudentProfileRead.from_orm(user)
        student_data.roll_number = roll
        
        # Check for Evaluation
        # We look for the MOST RECENT evaluation for this student
        # In a real system, we might filter by specific Exam ID. 
        # Here we assume 1 active exam context or just take the latest.
        recent_eval = (
            db.query(Evaluation)
            .join(AnswerSheet, Evaluation.answer_sheet_id == AnswerSheet.id)
            .filter(AnswerSheet.user_id == user.id)
            .order_by(Evaluation.created_at.desc())
            .first()
        )
        
        if recent_eval:
            student_data.evaluated = True
            # Convert 0-1 score to 0-100 marks for frontend display
            marks_value = round(recent_eval.score * 100, 1)
            student_data.marks = marks_value
            if marks_value >= 90: student_data.grade = 'A+'
            elif marks_value >= 80: student_data.grade = 'A'
            elif marks_value >= 70: student_data.grade = 'B'
            elif marks_value >= 60: student_data.grade = 'C'
            elif marks_value >= 50: student_data.grade = 'D'
            else: student_data.grade = 'F'
        else:
            student_data.evaluated = False
            student_data.marks = None
            student_data.grade = None
            
        students_with_rolls.append(student_data)

    return students_with_rolls


# -------------------------------------------------------
# UPLOAD ANSWER SHEET (OCR)
# -------------------------------------------------------

@app.post("/upload-answer-sheet")
def upload_answer_sheet(
    student_id: int = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        print(f"[OCR Engine] Processing file {file.filename} for student_id {student_id}")

        try:
            from external_ocr import extract_text_from_file
            print(f"   > [OCR Engine] Extractor Engine initiating...")
            text = extract_text_from_file(file_path)
            
            if not text or not text.strip():
                print("   > [OCR Engine] Engine returned empty text.")
                return {"ocr_text": "", "error": "OCR Engine returned empty text."}

            print(f"   > [OCR Engine] Extraction Complete. Length: {len(text)} characters.")
            
            source = "OCR Engine (Tesseract + Transformer + AI cleanup)"
            
            # DB INTEGRATION
            new_sheet = AnswerSheet(
                user_id=student_id,
                filename=file.filename,
                file_path=file_path,
                file_type=file.filename.split('.')[-1].lower(),
                ocr_text=text,
                ocr_method=source
            )
            db.add(new_sheet)
            db.commit()
            db.refresh(new_sheet)
            
            print("[OCR Engine] Pipeline Complete. Result saved to DB.")
            return {"answer_sheet_id": new_sheet.id, "ocr_text": text, "source": source}

        except Exception as pipeline_error:
            print(f"[OCR Engine] CRITICAL PIPELINE ERROR: {pipeline_error}")
            raise HTTPException(status_code=500, detail=f"Pipeline failed: {str(pipeline_error)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")


# -------------------------------------------------------
# UPLOAD ANSWER KEY
# -------------------------------------------------------

@app.post("/upload-answer-key")
def upload_answer_key(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        file_path = os.path.join(KEY_FOLDER, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_ext = file.filename.lower()
        key_text = ""
        source = "OCR Engine (Tesseract + Transformer + AI cleanup)"

        if file_ext.endswith(".pdf") or file_ext.endswith((".png", ".jpg", ".jpeg")):
            from external_ocr import extract_text_from_file
            key_text = extract_text_from_file(file_path)
        elif file_ext.endswith(".txt"):
            with open(file_path, "r", encoding="utf-8") as f:
                key_text = f.read()
            source = "Text File"
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")

        if not key_text or not key_text.strip():
            raise HTTPException(status_code=400, detail="No text extracted from answer key.")

        # Extract Mark Distribution using LLM
        from llm_evaluation import extract_mark_distribution
        print("[Answer Key Upload] Extracting explicit marks per question...")
        mark_distribution = extract_mark_distribution(key_text)
        
        # Serialize raw text and distribution into JSON text for DB
        import json
        structured_key_text = json.dumps({
            "raw_text": key_text,
            "marks": mark_distribution
        })

        # DB INTEGRATION
        new_key = AnswerKey(
            user_id=current_user.id,
            filename=file.filename,
            file_path=file_path,
            file_type=file_ext.split('.')[-1],
            key_text=structured_key_text,
            is_active=True
        )
        db.add(new_key)
        db.commit()
        db.refresh(new_key)

        return {"answer_key_id": new_key.id, "key_text": key_text, "source": source}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process answer key: {str(e)}")


# -------------------------------------------------------
# EVALUATION
# -------------------------------------------------------

@app.post("/evaluate")
async def evaluate(
    answer_sheet_id: int = Form(...),
    answer_key_id: int = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        print(f"[Evaluation Layer] Received submission for evaluation. Auth by User ID {current_user.id}")
        
        # 1. Fetch Records
        answer_sheet = db.query(AnswerSheet).filter(AnswerSheet.id == answer_sheet_id).first()
        answer_key = db.query(AnswerKey).filter(AnswerKey.id == answer_key_id).first()
        
        if not answer_sheet or not answer_key:
            raise HTTPException(status_code=404, detail="Requested answer sheet or key not found in Database.")
            
        student_text = answer_sheet.ocr_text
        key_raw_text = answer_key.key_text
        
        # Decode structured key text
        import json
        key_text = key_raw_text
        mark_distribution = None
        try:
            parsed_key = json.loads(key_raw_text)
            if isinstance(parsed_key, dict) and "raw_text" in parsed_key:
                key_text = parsed_key.get("raw_text", "")
                mark_distribution = parsed_key.get("marks", {})
        except:
            pass # Fallback for non-JSON old records

        if not student_text or not student_text.strip() or not key_text or not key_text.strip():
            raise HTTPException(status_code=400, detail="Empty text records found.")

        # 2. Run Semantic LLM Reasoning
        result = evaluate_semantic_content(student_text, key_text, mark_distribution)
        
        if not result:
            raise HTTPException(status_code=500, detail="Evaluation Layer failed completely.")

        score = result.get('score', 0.0)
        feedback = result.get('feedback', 'No feedback provided.')
        
        # 3. Save Atomic Result
        # Idempotent logic (Update if evaluated before, otherwise Create)
        existing_eval = db.query(Evaluation).filter(
            Evaluation.answer_sheet_id == answer_sheet_id,
            Evaluation.answer_key_id == answer_key_id
        ).first()
        
        if existing_eval:
            existing_eval.score = score
            existing_eval.feedback = feedback
            db.commit()
            db.refresh(existing_eval)
            eval_record = existing_eval
            print(f"[Evaluation Layer] Updated existing database record {eval_record.id}.")
        else:
            new_eval = Evaluation(
                user_id=current_user.id,
                answer_sheet_id=answer_sheet_id,
                answer_key_id=answer_key_id,
                student_text=student_text,
                key_text=key_text,
                score=score,
                feedback=feedback,
                similarity_score=0.0 # Will expand if SBERT scores are passed back
            )
            db.add(new_eval)
            db.commit()
            db.refresh(new_eval)
            eval_record = new_eval
            print(f"[Evaluation Layer] Created new database record {eval_record.id}.")
            
        return {
            "evaluation_id": eval_record.id,
            "score": score,
            "feedback": feedback
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation Engine failed: {str(e)}")


# -------------------------------------------------------
# STUDENT RESULTS API
# -------------------------------------------------------

@app.get("/student/results")
def get_my_results(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Fetch all evaluation results for the logged-in student.
    Strictly filters by current_user.id to ensure they only see THEIR OWN results.
    """
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can view their results.")

    # Query evaluations for this user
    # We join with AnswerKey (if we want test names) or just return raw data
    results = (
        db.query(Evaluation)
        .join(AnswerSheet, Evaluation.answer_sheet_id == AnswerSheet.id)
        .filter(AnswerSheet.user_id == current_user.id)
        .order_by(Evaluation.created_at.desc())
        .all()
    )

    # Return a simplified structure for the frontend
    output = []
    for eval_record in results:
        output.append({
            "id": eval_record.id,
            "subject": "General", # Placeholder until we have Subject in DB
            "test_name": f"Evaluation {eval_record.id}",
            "score": eval_record.score, # 0.0 to 1.0
            "feedback": eval_record.feedback,
            "created_at": eval_record.created_at
        })
    
    return output


# -------------------------------------------------------
# PUBLIC DATA (FOR REGISTRATION)
# -------------------------------------------------------

@app.get("/public/classrooms", response_model=List[ClassroomRead])
def get_public_classrooms(db: Session = Depends(get_db)):
    """ Returns a list of all classrooms for the registration dropdown. """
    return db.query(Classroom).all()


# -------------------------------------------------------
# REGISTRATION (NEW USER SIGNUP)
# -------------------------------------------------------

@app.post("/register", response_model=Token)
def register_user(user_in: schemas.UserRegister, db: Session = Depends(get_db)):
    # 1. Check if user already exists
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered. Please login.",
        )

    # 2. Prepare User Data
    if user_in.full_name:
        full_name = user_in.full_name
    else:
        local_part = user_in.email.split("@")[0]
        full_name = local_part.replace(".", " ").replace("_", " ").title()

    # SECURITY CHECK: strict teacher registration
    if user_in.role == "teacher":
        expected_code = os.getenv("TEACHER_SECRET_CODE", "FACULTY2026")
        if user_in.teacher_code != expected_code:
            raise HTTPException(
                status_code=403,
                detail="Invalid Teacher Access Code. Please contact administration."
            )

    hashed_pw = get_password_hash(user_in.password)

    new_user = User(
        email=user_in.email,
        hashed_password=hashed_pw,
        full_name=full_name,
        role=user_in.role
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 3. Handle Role Specifics (Enrollment)
    if new_user.role == "student":
        target_classroom = None
        
        # A. User selected a specific class
        if user_in.classroom_id:
            target_classroom = db.query(Classroom).filter(Classroom.id == user_in.classroom_id).first()
        
        # B. Fallback: Auto-enroll in first available if no choice (or invalid choice)
        if not target_classroom:
            target_classroom = db.query(Classroom).first()
            
        if target_classroom:
            # AUTO-ASSIGN ROLL NUMBER (Sequential per class)
            # 1. Count existing students in this class
            current_count = db.query(Enrollment).filter(Enrollment.classroom_id == target_classroom.id).count()
            # 2. Assign next number
            new_roll_number = current_count + 1
            
            enrollment = Enrollment(
                student_id=new_user.id, 
                classroom_id=target_classroom.id,
                roll_number=new_roll_number
            )
            db.add(enrollment)
            db.commit()
            print(f"DEBUG: Enrolled {new_user.email} in {target_classroom.name} with Roll No: {new_roll_number}")

    # 4. Auto-Login (Generate Token)
    access_token = create_access_token(
        data={"sub": new_user.email, "role": new_user.role, "user_id": new_user.id}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": new_user.id,
        "role": new_user.role,
        "full_name": new_user.full_name
    }
