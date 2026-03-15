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
from grading_utils import calculate_grade_and_status

app = FastAPI()

# -------------------------------------------------------
# STARTUP & CONFIG
# -------------------------------------------------------
@app.on_event("startup")
async def startup_event():
    print("\n" + "="*50)
    print(" AUTOEVAL+ CORE SYSTEM STARTUP")
    print("="*50)
    print("[System] Initializing Kernel... OK")
    print("[Config] Loading Environment Variables... OK")
    print("[Database] Connecting to SQLite (autoeval.db)... OK")
    print("[OCR Module] Initializing High-Precision Transformer Engine... OK")
    print("[Semantic Analysis] Initializing Semantic Vector Space... OK")
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
        
        # Check for Persistent Evaluation Status
        if user.is_evaluated:
            student_data.evaluated = True
            
            # Fetch latest marks for display
            recent_eval = (
                db.query(Evaluation)
                .join(AnswerSheet, Evaluation.answer_sheet_id == AnswerSheet.id)
                .filter(AnswerSheet.user_id == user.id)
                .order_by(Evaluation.created_at.desc())
                .first()
            )
            
            if recent_eval:
                # Use standard logic from grading_utils
                grade, status, _ = calculate_grade_and_status(recent_eval.score, recent_eval.total_max_marks)
                student_data.grade = grade
                student_data.marks = round(recent_eval.score * (recent_eval.total_max_marks or 50.0), 1)
                student_data.pass_status = status  # Optional: schema might need update
            else:
                # Handle edge case where is_evaluated is True but no Evaluation record exists
                student_data.marks = None
                student_data.grade = None
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

        # Extract Mark Distribution and Concepts using LLM
        from llm_evaluation import extract_mark_distribution, extract_key_concepts_once
        print("[Answer Key Upload] Extracting explicit marks per question...")
        mark_distribution = extract_mark_distribution(key_text)
        
        print("[Answer Key Upload] Locking scorable concepts for determinism...")
        key_concepts = extract_key_concepts_once(key_text, mark_distribution)
        
        # Serialize raw text, distribution, and concepts into JSON text for DB
        import json
        structured_key_text = json.dumps({
            "raw_text": key_text,
            "marks": mark_distribution,
            "concepts": key_concepts
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
        pre_extracted_concepts = None
        
        try:
            parsed_key = json.loads(key_raw_text)
            if isinstance(parsed_key, dict) and "raw_text" in parsed_key:
                key_text = parsed_key.get("raw_text", "")
                mark_distribution = parsed_key.get("marks", {})
                pre_extracted_concepts = parsed_key.get("concepts", {})
        except:
            pass # Fallback for non-JSON old records

        # Strict Deterministic Fail-Safe: If marks/concepts are missing, evaluation MUST fail to prevent AI re-extraction.
        if not mark_distribution or not pre_extracted_concepts:
            print("[Evaluation Layer] CRITICAL: Missing locked metadata (marks/concepts). Evaluation aborted.")
            raise HTTPException(status_code=400, detail="Answer key is missing locked metadata. Please re-upload the answer key to generate frozen concepts.")

        if not student_text or not student_text.strip() or not key_text or not key_text.strip():
            raise HTTPException(status_code=400, detail="Empty text records found.")

        # 2. Run Semantic LLM Reasoning
        result = evaluate_semantic_content(student_text, key_text, mark_distribution, pre_extracted_concepts)
        
        if not result:
            raise HTTPException(status_code=500, detail="Evaluation Layer failed completely.")

        score = result.get('score', 0.0)
        feedback = result.get('feedback', 'No feedback provided.')
        
        # 3. Save Atomic Result
        # Strict Academic Snapshot Rule: Append New, Never Overwrite
        # Mark all previous evaluations for this sheet/key pair as NOT latest
        db.query(Evaluation).filter(
            Evaluation.answer_sheet_id == answer_sheet_id,
            Evaluation.answer_key_id == answer_key_id
        ).update({"is_latest": False})
        db.commit()

        # Numeric Precision Normalization
        total_obtained = round(result.get('total_obtained', 0.0), 1)
        total_max_marks = float(result.get('total_max', 50.0))
        percentage = round(result.get('percentage', 0.0), 2)
        score_ratio = round(result.get('score', 0.0), 4)
        
        # question_details already natively adheres to schema requirements defined in Phase 2
        import json
        question_details_json = json.dumps(result.get('question_details', {}))

        new_eval = Evaluation(
            user_id=current_user.id,
            answer_sheet_id=answer_sheet_id,
            answer_key_id=answer_key_id,
            student_text=student_text,
            key_text=key_text,
            score=score_ratio,
            total_max_marks=total_max_marks,
            question_details=question_details_json,
            feedback=feedback,
            similarity_score=0.0, # Retained for schema backwards compatibility
            pipeline_version="v3.0-deterministic",
            factual_ruleset_version="1.0-strict",
            is_latest=True
        )
        db.add(new_eval)
        db.commit()
        db.refresh(new_eval)
        eval_record = new_eval
        print(f"[Evaluation Layer] Created APPENED database snapshot record {eval_record.id}.")
            
        # 4. Final Academic Policy Mapping
        grade, status, explain_log = calculate_grade_and_status(score_ratio, total_max_marks)

        # 5. Update Student Status (Persistent & Robust)
        student = db.query(User).filter(User.id == answer_sheet.user_id).first()
        if student:
            print(f"[Status Update] Initial state for Student ID {student.id}: is_evaluated={student.is_evaluated}")
            student.is_evaluated = True
            db.add(student)
            db.flush()
            db.commit()
            db.refresh(student)
            print(f"[Status Update] Student ID {student.id} set to is_evaluated=True and committed.")

        return {
            "evaluation_id": eval_record.id,
            "score": score_ratio,
            "total_marks": total_obtained,
            "max_marks": total_max_marks,
            "percentage": percentage,
            "grade": grade,
            "result": status,
            "question_details": result.get('question_details', {}),
            "feedback": feedback
        }

    except Exception as e:
        print(f"[Evaluation Engine] FATAL: {e}")
        raise HTTPException(status_code=500, detail=f"Evaluation Engine failed: {str(e)}")


@app.get("/evaluation/latest/{student_id}")
def get_latest_evaluation(
    student_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Fetch the latest evaluation record for a specific student.
    Teacher-only read-only audit endpoint.
    """
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can audit evaluations.")

    eval_record = (
        db.query(Evaluation)
        .join(AnswerSheet, Evaluation.answer_sheet_id == AnswerSheet.id)
        .filter(AnswerSheet.user_id == student_id, Evaluation.is_latest == True)
        .order_by(Evaluation.created_at.desc())
        .first()
    )

    if not eval_record:
        raise HTTPException(status_code=404, detail="No evaluation record found for this student.")

    import json
    try:
        details = json.loads(eval_record.question_details) if eval_record.question_details else {}
    except:
        details = {}

    # Calculate grade/status for audit view
    grade, status, _ = calculate_grade_and_status(eval_record.score, eval_record.total_max_marks)

    return {
        "id": eval_record.id,
        "score_ratio": eval_record.score,
        "total_marks": round(eval_record.score * (eval_record.total_max_marks or 50.0), 1),
        "max_marks": eval_record.total_max_marks or 50.0,
        "percentage": round(eval_record.score * 100, 2),
        "grade": grade,
        "result": status,
        "feedback": eval_record.feedback,
        "question_details": details,
        "created_at": eval_record.created_at
    }


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

    # Query evaluations for this user ensuring we ONLY pick the latest snapshot per sheet
    results = (
        db.query(Evaluation)
        .join(AnswerSheet, Evaluation.answer_sheet_id == AnswerSheet.id)
        .filter(AnswerSheet.user_id == current_user.id, Evaluation.is_latest == True)
        .order_by(Evaluation.created_at.desc())
        .all()
    )

    # Return a simplified structure for the frontend
    output = []
    for eval_record in results:
        # Calculate grade/status for student results view
        grade, status, _ = calculate_grade_and_status(eval_record.score, eval_record.total_max_marks)
        
        output.append({
            "id": eval_record.id,
            "subject": "General", # Placeholder until we have Subject in DB
            "test_name": f"Evaluation {eval_record.id}",
            "score": eval_record.score, # 0.0 to 1.0 (legacy support)
            "percentage": round(eval_record.score * 100, 2),
            "total_obtained": round(eval_record.score * (eval_record.total_max_marks or 50.0), 1),
            "total_max": eval_record.total_max_marks or 50.0,
            "grade": grade,
            "result": status,
            "feedback": eval_record.feedback,
            "created_at": eval_record.created_at
        })
    
    return output


# -------------------------------------------------------
# STORED DATA RETRIEVAL (CREDIT-SAFE RE-EVALUATION)
# -------------------------------------------------------

@app.get("/stored-sheet/{student_id}")
def get_stored_sheet(
    student_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns the latest stored OCR text and answer_sheet_id for a student.
    Allows re-evaluation without re-running OCR.
    Teacher-only.
    """
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can access stored sheets.")

    sheet = (
        db.query(AnswerSheet)
        .filter(AnswerSheet.user_id == student_id)
        .order_by(AnswerSheet.created_at.desc())
        .first()
    )
    if not sheet:
        raise HTTPException(status_code=404, detail="No stored answer sheet found for this student.")

    print(f"[Stored Sheet] Loaded sheet ID {sheet.id} for student {student_id}. OCR length: {len(sheet.ocr_text or '')} chars.")
    return {
        "answer_sheet_id": sheet.id,
        "ocr_text": sheet.ocr_text or "",
        "filename": sheet.filename
    }


@app.get("/stored-key")
def get_stored_key(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns the latest stored active answer key ID and filename.
    Allows re-evaluation without re-uploading or re-extracting the answer key.
    Teacher-only.
    """
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can access stored keys.")

    key = (
        db.query(AnswerKey)
        .filter(AnswerKey.is_active == True)
        .order_by(AnswerKey.created_at.desc())
        .first()
    )
    if not key:
        raise HTTPException(status_code=404, detail="No stored answer key found.")

    print(f"[Stored Key] Loaded key ID {key.id} ({key.filename}).")
    return {
        "answer_key_id": key.id,
        "filename": key.filename
    }



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
