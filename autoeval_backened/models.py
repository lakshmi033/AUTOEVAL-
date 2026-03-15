# models.py
"""
SQLAlchemy ORM models for AutoEval+.

Defines:
- User: Authentication identity (Teacher/Student)
- Classroom: Classes managed by a teacher
- Enrollment: Link between Student and Classroom
- AnswerSheet: Student submissions
- AnswerKey: Teacher solution keys
- Evaluation: Results
"""

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, Float, func, UniqueConstraint
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    """
    Unified User model for both Teachers and Students.
    Role determines access permissions.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)  # 'teacher' or 'student'
    is_active = Column(Boolean, nullable=False, default=True)
    is_evaluated = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    # Teacher: Has many classrooms
    classrooms = relationship("Classroom", back_populates="teacher", cascade="all, delete-orphan")
    
    # Student: Has many enrollments (usually one per active class context)
    enrollments = relationship("Enrollment", back_populates="student", cascade="all, delete-orphan")

    # Common: Uploads
    answer_sheets = relationship("AnswerSheet", back_populates="user", cascade="all, delete-orphan")
    answer_keys = relationship("AnswerKey", back_populates="user", cascade="all, delete-orphan")
    evaluations = relationship("Evaluation", back_populates="user", cascade="all, delete-orphan")


class Classroom(Base):
    """
    A class managed by a single teacher.
    """
    __tablename__ = "classrooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    teacher = relationship("User", back_populates="classrooms")
    enrollments = relationship("Enrollment", back_populates="classroom", cascade="all, delete-orphan")


class Enrollment(Base):
    """
    Link between a Student and a Classroom.
    """
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    classroom_id = Column(Integer, ForeignKey("classrooms.id"), nullable=False, index=True)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # NEW: Class-specific Roll Number (1, 2, 3...)
    roll_number = Column(Integer, nullable=True) # Nullable for migration, but logic will enforce it

    # Relationships
    student = relationship("User", back_populates="enrollments")
    classroom = relationship("Classroom", back_populates="enrollments")

    # Constraint: A student can join a specific class only once
    __table_args__ = (UniqueConstraint('student_id', 'classroom_id', name='uq_student_class'),)


class AnswerSheet(Base):
    """
    Answer sheets uploaded by users (typically students).
    """
    __tablename__ = "answer_sheets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)  # image/pdf
    ocr_text = Column(Text, nullable=True)
    ocr_method = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="answer_sheets")
    evaluations = relationship("Evaluation", back_populates="answer_sheet", cascade="all, delete-orphan")


class AnswerKey(Base):
    """
    Answer keys uploaded by users (typically teachers).
    """
    __tablename__ = "answer_keys"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)
    key_text = Column(Text, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="answer_keys")
    evaluations = relationship("Evaluation", back_populates="answer_key", cascade="all, delete-orphan")


class Evaluation(Base):
    """
    Evaluation results.
    """
    __tablename__ = "evaluations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True) # Who ran the eval?
    answer_sheet_id = Column(Integer, ForeignKey("answer_sheets.id"), nullable=False, index=True)
    answer_key_id = Column(Integer, ForeignKey("answer_keys.id"), nullable=False, index=True)
    
    student_text = Column(Text, nullable=False)
    key_text = Column(Text, nullable=False)
    score = Column(Float, nullable=False) # Stores the percentage ratio
    total_max_marks = Column(Float, nullable=True) # Frozen max possible marks
    question_details = Column(Text, nullable=True) # Full JSON breakdown string
    pipeline_version = Column(String(50), nullable=False, default="v3.0-deterministic")
    factual_ruleset_version = Column(String(50), nullable=True, default="1.0-strict")
    is_latest = Column(Boolean, nullable=False, default=True) # Snapshot tracker
    
    feedback = Column(Text, nullable=False) # Increased from String(500) to Text to hold detailed breakdowns
    similarity_score = Column(Float, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="evaluations")
    answer_sheet = relationship("AnswerSheet", back_populates="evaluations")
    answer_key = relationship("AnswerKey", back_populates="evaluations")

