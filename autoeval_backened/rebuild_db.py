
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

        # 3. Create 3 Classes (Generic Names)
        print("Creating Classrooms...")
        class_names = ["Classroom A", "Classroom B", "Classroom C"]
        classrooms = []
        for name in class_names:
            c = Classroom(name=name, teacher_id=teacher.id)
            db.add(c)
            classrooms.append(c)
        db.commit()
        for c in classrooms:
            db.refresh(c)

        # 4. Create 90 Students (Realistic Names)
        print("Creating 90 Students (Realistic Names)...")
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
            "Maria Powell", "Samuel Long", "Heather Patterson", "Patrick Hughes", "Diane Flores"
        ]
        
        student_idx = 0
        
        for c in classrooms:
            print(f"  -> Filling {c.name}")
            for _ in range(30):
                if student_idx >= len(student_names):
                    break
                    
                full_name = student_names[student_idx]
                
                # Generate realistic email: firstname.lastname@school.com
                # Handle spaces and cases
                name_parts = full_name.lower().split()
                if len(name_parts) >= 2:
                    email_prefix = f"{name_parts[0]}.{name_parts[-1]}"
                else:
                    email_prefix = name_parts[0]
                
                email = f"{email_prefix}@school.com"
                
                # Check duplication
                existing = db.query(User).filter(User.email == email).first()
                if existing:
                    # Fallback for duplicates (though list should be unique)
                    email = f"{email_prefix}{student_idx}@school.com"
                
                student = User(
                    email=email,
                    hashed_password=student_pass,
                    full_name=full_name,
                    role="student"
                )
                db.add(student)
                db.flush() # get id

                # Enroll
                enroll = Enrollment(student_id=student.id, classroom_id=c.id)
                db.add(enroll)
                
                student_idx += 1
            db.commit()

        print("\n" + "="*50)
        print("DATABASE REBUILD COMPLETE")
        print(f"Teacher: teacher@school.com / teacher123")
        print(f"Students Format: firstname.lastname@school.com / student123")
        print(f"Example Student: {student_names[0].replace(' ', '.').lower()}@school.com")
        print("Total Students: 90")
        print("===========================")

    except Exception as e:
        print(f"ERROR: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
