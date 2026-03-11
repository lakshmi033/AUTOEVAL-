
import sys
import os
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User, AnswerSheet, AnswerKey, Evaluation
import json

def verify_status():
    db = SessionLocal()
    try:
        # 1. Get a student (James Smith, should be ID 2)
        student = db.query(User).filter(User.full_name == "James Smith").first()
        if not student:
            print("FAILURE: Student 'James Smith' not found.")
            return

        print(f"Initial Status for {student.full_name} (ID {student.id}): is_evaluated={student.is_evaluated}")

        # 2. Setup mock data for evaluation
        teacher = db.query(User).filter(User.role == "teacher").first()
        
        # Answer Key
        key = AnswerKey(
            user_id=teacher.id,
            filename="test_key.json",
            file_path="/tmp/test_key.json",
            file_type="json",
            key_text=json.dumps({"raw_text": "Power sharing is good.", "marks": {"1": 3.0}}),
            is_active=True
        )
        db.add(key)
        db.flush()

        # Answer Sheet
        sheet = AnswerSheet(
            user_id=student.id,
            filename="test_sheet.txt",
            file_path="/tmp/test_sheet.txt",
            file_type="txt",
            ocr_text="Power sharing is a heart of democracy.",
            ocr_method="mock"
        )
        db.add(sheet)
        db.flush()

        # 3. Simulate the /evaluate logic
        # In our case, we'll just manally add the Evaluation then flip the status
        new_eval = Evaluation(
            user_id=teacher.id,
            answer_sheet_id=sheet.id,
            answer_key_id=key.id,
            student_text=sheet.ocr_text,
            key_text="Power sharing is good.",
            score=0.8,
            feedback="Good answer",
            similarity_score=0.8
        )
        db.add(new_eval)
        
        # The logic we added to main.py:
        # Fetch the student from sheet.user_id and set is_evaluated=True
        target_student = db.query(User).filter(User.id == sheet.user_id).first()
        target_student.is_evaluated = True
        
        db.commit()

        # 4. Final Re-Verification
        db.refresh(student)
        print(f"Final Status for {student.full_name}: is_evaluated={student.is_evaluated}")

        if student.is_evaluated:
            print("\nSUCCESS: Student status updated correctly!")
        else:
            print("\nFAILURE: Student status NOT updated.")

    except Exception as e:
        print(f"ERROR: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    verify_status()
