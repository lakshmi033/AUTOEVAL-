
import os
import sys
from sqlalchemy.orm import Session
from database import engine, Base, SessionLocal
from models import User, Classroom, Enrollment
from auth import get_password_hash

def init_db():
    print("WARNING: This script will WIPE and REBUILD the database.")
    print("Data Persistence Guarantee: deterministic seeding.")
    
    # 1. Reset Database
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # 2. Create Teacher
        print("Creating Teacher...")
        teacher_pass = get_password_hash("teacher123")
        teacher = User(
            email="teacher@school.com",
            hashed_password=teacher_pass,
            full_name="Head Teacher",
            role="teacher"
        )
        db.add(teacher)
        db.commit()
        db.refresh(teacher)

        # 3. Create 3 Classes
        print("Creating Classrooms...")
        class_names = ["Class A", "Class B", "Class C"]
        classrooms = []
        for name in class_names:
            c = Classroom(name=name, teacher_id=teacher.id)
            db.add(c)
            classrooms.append(c)
        db.commit()
        for c in classrooms:
            db.refresh(c)

        # 4. Create 90 Students
        print("Creating 90 Students...")
        student_pass = get_password_hash("student123")
        
        student_names = [
            "James Smith", "Maria Garcia", "Robert Johnson", "Lisa Rodriguez", "Michael Williams", 
            "Sarah Martinez", "William Brown", "Kimberly Davis", "David Jones", "Jennifer Lopez",
            "Richard Miller", "Susan Wilson", "Joseph Moore", "Karen Taylor", "Thomas Anderson", 
            "Nancy Thomas", "Charles Jackson", "Margaret White", "Christopher Harris", "Betty Martin",
            "Daniel Thompson", "Sandra Clark", "Matthew Robinson", "Ashley Lewis", "Anthony Lee", 
            "Dorothy Walker", "Mark Hall", "Kimberly Allen", "Donald Young", "Donna Hernandez",
            "Steven King", "Emily Wright", "Paul Lopez", "Carol Hill", "Andrew Scott", 
            "Michelle Green", "Joshua Adams", "Amanda Baker", "Kenneth Gonzalez", "Melissa Nelson",
            "Kevin Carter", "Deborah Mitchell", "Brian Perez", "Stephanie Roberts", "George Turner", 
            "Rebecca Phillips", "Edward Campbell", "Sharon Parker", "Ronald Evans", "Laura Edwards",
            "Timothy Collins", "Cynthia Stewart", "Jason Sanchez", "Kathleen Morris", "Jeffrey Rogers", 
            "Amy Reed", "Ryan Cook", "Shirley Morgan", "Jacob Bell", "Angela Murphy",
            "Gary Bailey", "Helen Rivera", "Nicholas Cooper", "Anna Richardson", "Eric Cox", 
            "Brenda Howard", "Stephen Ward", "Pamela Torres", "Jonathan Peterson", "Nicole Gray",
            "Larry Ramirez", "Samantha James", "Justin Watson", "Katherine Brooks", "Scott Kelly", 
            "Christine Sanders", "Frank Price", "Debra Bennett", "Brandon Wood", "Rachel Barnes",
            "Raymond Ross", "Carolyn Henderson", "Gregory Coleman", "Janet Jenkins", "Benjamin Perry", 
            "Maria Powell", "Samuel Long", "Heather Patterson", "Patrick Hughes", "Diane Flores",
            "Olivia Moore", "Liam Taylor", "Emma Anderson", "Noah Thomas", "Ava Jackson",
            "Lucas White", "Sophia Harris", "Mason Martin", "Mia Thompson", "Ethan Clark"
        ]
        
        # Trim or ensure at least 90
        student_names = student_names[:90]
        
        student_idx = 0
        
        for c in classrooms:
            print(f"  -> Filling {c.name}")
            for roll in range(1, 31):
                if student_idx >= len(student_names):
                    break
                    
                full_name = student_names[student_idx]
                
                name_parts = full_name.lower().split()
                if len(name_parts) >= 2:
                    email_prefix = f"{name_parts[0]}.{name_parts[-1]}"
                else:
                    email_prefix = name_parts[0]
                
                email = f"{email_prefix}@school.com"
                
                # Check duplication
                existing = db.query(User).filter(User.email == email).first()
                if existing:
                    email = f"{email_prefix}{student_idx}@school.com"
                
                student = User(
                    email=email,
                    hashed_password=student_pass,
                    full_name=full_name,
                    role="student",
                    is_evaluated=False
                )
                db.add(student)
                db.flush() 

                # Enroll with Roll Number
                enroll = Enrollment(
                    student_id=student.id, 
                    classroom_id=c.id,
                    roll_number=roll
                )
                db.add(enroll)
                
                student_idx += 1
            db.commit()

        print("\n" + "="*50)
        print("DATABASE REBUILD COMPLETE")
        print(f"Teacher: teacher@school.com / teacher123")
        print(f"Students: 30 per class (Class A, B, C)")
        print(f"Roll Numbers: 1-30 sequentially")
        print(f"Total Students: {student_idx}")
        print("===========================")

    except Exception as e:
        print(f"ERROR: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
