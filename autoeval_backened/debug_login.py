
import sqlite3
from passlib.context import CryptContext
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# 1. Setup DB connection
DATABASE_URL = "sqlite:///./autoeval.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

# 2. Setup Password Hasher
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

print("="*60)
print("LOGIN DEBUGGER")
print("="*60)

try:
    # 3. List all users
    result = db.execute(text("SELECT id, email, role, hashed_password, roll_number FROM users"))
    users = result.fetchall()
    
    if not users:
        print("ERROR: No users found in database!")
    else:
        print(f"Found {len(users)} users.")
        for u in users:
            uid, email, role, hashed_pwd, roll = u
            print(f"\n[User ID: {uid}]")
            print(f"  Email: {email}")
            print(f"  Role:  {role}")
            print(f"  Roll:  {roll}")
            print(f"  Hash:  {hashed_pwd[:20]}...")
            
            # 4. Test Password 'password123'
            is_valid = verify_password("password123", hashed_pwd)
            print(f"  Test 'password123': {'MATCH ✅' if is_valid else 'FAIL ❌'}")
            
            # 5. Test Password 'student123' (The other default)
            if not is_valid:
                is_valid_student = verify_password("student123", hashed_pwd)
                print(f"  Test 'student123':  {'MATCH ✅' if is_valid_student else 'FAIL ❌'}")

except Exception as e:
    print(f"CRITICAL ERROR: {e}")
finally:
    db.close()
