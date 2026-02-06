from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, status
import shutil
import os
from ocr import extract_text_from_image, extract_text_from_pdf, validate_ocr_result
from evaluation import evaluate_answer
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import User
from schemas import UserCreate, UserRead, UserLogin, Token
from auth import (
    get_password_hash,
    authenticate_user,
    create_access_token,
    get_current_user,
)

app = FastAPI()

# Create DB tables
Base.metadata.create_all(bind=engine)

# CORS
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
    return {"message": "AutoEval+ backend running"}


# -------------------------------------------------------
# USER AUTH
# -------------------------------------------------------

@app.post("/register", response_model=UserRead, status_code=201)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(
            status_code=400, detail="A user with this email already exists."
        )

    hashed = get_password_hash(user_in.password)

    user = User(email=user_in.email, hashed_password=hashed, role="user")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/login", response_model=Token)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, email=user_in.email, password=user_in.password)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user.email, "role": user.role}
    )
    return Token(access_token=access_token, token_type="bearer")


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

        print("\n" + "="*60)
        print("ANSWER SHEET UPLOAD DEBUG")
        print(f"File: {file.filename}")
        print(f"Type: {file.content_type}")
        print("="*60)

        # Perform OCR
        try:
            if file.filename.lower().endswith(".pdf"):
                print("Processing as PDF...")
                text = extract_text_from_pdf(file_path, debug=True)
            else:
                print("Processing as IMAGE...")
                text = extract_text_from_image(file_path, debug=True)

            print(f"OCR TEXT LENGTH: {len(text)}")

            if not text or not text.strip():
                return {
                    "ocr_text": "",
                    "error": "No text extracted. Ensure the image is clear."
                }

            return {"ocr_text": text}

        except Exception as ocr_error:
            error_msg = str(ocr_error)
            print("OCR Error:", error_msg)

            if "tesseract" in error_msg.lower():
                raise HTTPException(
                    status_code=500,
                    detail="Tesseract not installed or missing."
                )
            elif "torch" in error_msg.lower():
                raise HTTPException(
                    status_code=500,
                    detail=f"TrOCR model error: {error_msg}"
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"OCR failed: {error_msg}"
                )

    except Exception as e:
        print("Upload Error:", str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process file: {str(e)}"
        )


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

        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        print("\n" + "="*60)
        print("ANSWER KEY UPLOAD DEBUG")
        print(f"File: {file.filename}")
        print(f"Type: {file.content_type}")
        print("="*60)

        file_ext = file.filename.lower()
        key_text = ""

        # PDF
        if file_ext.endswith(".pdf"):
            print("Processing as PDF...")
            key_text = extract_text_from_pdf(file_path, debug=True)

        # TXT
        elif file_ext.endswith(".txt"):
            print("Processing as TXT...")
            with open(file_path, "r", encoding="utf-8") as f:
                key_text = f.read()

        # IMAGE
        elif file_ext.endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tiff", ".webp")):
            print("Processing as IMAGE...")
            key_text = extract_text_from_image(file_path, debug=True)

        else:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file type. Use PDF, TXT, PNG, JPG, JPEG, BMP, GIF, TIFF, WEBP."
            )

        # Empty check
        if not key_text or not key_text.strip():
            raise HTTPException(
                status_code=400,
                detail="No text extracted from answer key."
            )

        # Validate OCR result
        is_valid, err = validate_ocr_result(key_text, "Answer-Key-Final")
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid answer key text: {err}"
            )

        return {"key_text": key_text}

    except Exception as e:
        print("Answer key upload error:", str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process answer key: {str(e)}"
        )


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
        print("\n" + "="*60)
        print("EVALUATION DEBUG")
        print("="*60)

        if not student_text.strip():
            raise HTTPException(status_code=400, detail="Student text is empty.")

        if not key_text.strip():
            raise HTTPException(status_code=400, detail="Answer key text is empty.")

        try:
            result = evaluate_answer(student_text, key_text)
            return result

        except Exception as eval_error:
            raise HTTPException(
                status_code=500,
                detail=f"Evaluation failed: {str(eval_error)}"
            )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected evaluation error: {str(e)}"
        )
