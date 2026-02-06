from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, status
import shutil
import os
from typing import List

from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import User, Classroom, Enrollment, AnswerSheet, AnswerKey, Evaluation
from schemas import UserCreate, UserRead, UserLogin, Token, ClassroomRead, ClassroomCreate, StudentProfileRead
from auth import (
    get_password_hash,
    authenticate_user,
    create_access_token,
    get_current_user,
)
from ocr import extract_text_from_image, extract_text_from_pdf, validate_ocr_result
from evaluation import evaluate_answer

app = FastAPI()

# -------------------------------------------------------
# STARTUP & CONFIG
# -------------------------------------------------------
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
    students = (
        db.query(User)
        .join(Enrollment, User.id == Enrollment.student_id)
        .filter(Enrollment.classroom_id == classroom_id)
        .all()
    )
    return students


# -------------------------------------------------------
# UPLOAD ANSWER SHEET (OCR)
# -------------------------------------------------------

@app.post("/upload-answer-sheet")
def upload_answer_sheet(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    try:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)

        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        print(f"DEBUG: Processing file {file.filename}")

        # Perform OCR
        try:
            if file.filename.lower().endswith(".pdf"):
                text = extract_text_from_pdf(file_path, debug=True)
            else:
                text = extract_text_from_image(file_path, debug=True)

            if not text or not text.strip():
                return {"ocr_text": "", "error": "No text extracted. Ensure the image is clear."}

            return {"ocr_text": text}

        except Exception as ocr_error:
            raise HTTPException(status_code=500, detail=f"OCR failed: {str(ocr_error)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")


# -------------------------------------------------------
# UPLOAD ANSWER KEY
# -------------------------------------------------------

@app.post("/upload-answer-key")
def upload_answer_key(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    try:
        file_path = os.path.join(KEY_FOLDER, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_ext = file.filename.lower()
        key_text = ""

        if file_ext.endswith(".pdf"):
            key_text = extract_text_from_pdf(file_path, debug=True)
        elif file_ext.endswith(".txt"):
            with open(file_path, "r", encoding="utf-8") as f:
                key_text = f.read()
        elif file_ext.endswith((".png", ".jpg", ".jpeg")):
            key_text = extract_text_from_image(file_path, debug=True)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")

        if not key_text or not key_text.strip():
            raise HTTPException(status_code=400, detail="No text extracted from answer key.")

        return {"key_text": key_text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process answer key: {str(e)}")


# -------------------------------------------------------
# EVALUATION
# -------------------------------------------------------

@app.post("/evaluate")
async def evaluate(
    student_text: str = Form(...),
    key_text: str = Form(...),
    current_user: User = Depends(get_current_user),
):
    try:
        if not student_text.strip() or not key_text.strip():
            raise HTTPException(status_code=400, detail="Empty text provided.")

        result = evaluate_answer(student_text, key_text)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")
