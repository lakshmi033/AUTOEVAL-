# models.py
"""
SQLAlchemy ORM models for AutoEval+.

Defines:
- User: user accounts for authentication
- AnswerSheet: uploaded answer sheets with OCR text
- AnswerKey: answer keys for evaluation
- Evaluation: evaluation results linking sheets and keys
"""

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, Float, func
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    """
    User accounts for authentication and authorization.

    Fields:
    - id: primary key
    - email: unique email address
    - hashed_password: bcrypt-hashed password
    - role: user role (kept for future use, not enforced currently)
    - is_active: soft-activation flag
    - created_at: timestamp of account creation
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="user")
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    answer_sheets = relationship("AnswerSheet", back_populates="user", cascade="all, delete-orphan")
    answer_keys = relationship("AnswerKey", back_populates="user", cascade="all, delete-orphan")
    evaluations = relationship("Evaluation", back_populates="user", cascade="all, delete-orphan")


class AnswerSheet(Base):
    """
    Answer sheets uploaded by users.

    Fields:
    - id: primary key
    - user_id: foreign key to users table
    - filename: original filename
    - file_path: storage path on server
    - file_type: image/pdf
    - ocr_text: extracted text from OCR
    - ocr_method: tesseract or trocr
    - created_at: upload timestamp
    """

    __tablename__ = "answer_sheets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)  # image/pdf
    ocr_text = Column(Text, nullable=True)  # Can be null if OCR fails
    ocr_method = Column(String(50), nullable=True)  # tesseract/trocr
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="answer_sheets")
    evaluations = relationship("Evaluation", back_populates="answer_sheet", cascade="all, delete-orphan")


class AnswerKey(Base):
    """
    Answer keys for evaluation.

    Fields:
    - id: primary key
    - user_id: foreign key to users table (who uploaded it)
    - filename: original filename
    - file_path: storage path on server
    - file_type: pdf/txt
    - key_text: extracted or read text
    - is_active: whether this is the current active key
    - created_at: upload timestamp
    """

    __tablename__ = "answer_keys"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)  # pdf/txt
    key_text = Column(Text, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="answer_keys")
    evaluations = relationship("Evaluation", back_populates="answer_key", cascade="all, delete-orphan")


class Evaluation(Base):
    """
    Evaluation results linking answer sheets and answer keys.

    Fields:
    - id: primary key
    - user_id: foreign key to users table (who performed evaluation)
    - answer_sheet_id: foreign key to answer_sheets table
    - answer_key_id: foreign key to answer_keys table
    - student_text: OCR text from answer sheet
    - key_text: text from answer key
    - score: similarity score (0.0 to 1.0)
    - feedback: evaluation feedback text
    - similarity_score: raw similarity value
    - created_at: evaluation timestamp
    """

    __tablename__ = "evaluations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    answer_sheet_id = Column(Integer, ForeignKey("answer_sheets.id"), nullable=False, index=True)
    answer_key_id = Column(Integer, ForeignKey("answer_keys.id"), nullable=False, index=True)
    student_text = Column(Text, nullable=False)
    key_text = Column(Text, nullable=False)
    score = Column(Float, nullable=False)  # 0.0 to 1.0
    feedback = Column(String(500), nullable=False)
    similarity_score = Column(Float, nullable=False)  # Raw similarity value
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="evaluations")
    answer_sheet = relationship("AnswerSheet", back_populates="evaluations")
    answer_key = relationship("AnswerKey", back_populates="evaluations")

