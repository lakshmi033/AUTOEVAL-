
import requests
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_login(email, password, endpoint, expected_status, description):
    print(f"TEST: {description}")
    print(f"  -> POST {endpoint} Payload: {email} / ********")
    try:
        response = requests.post(f"{BASE_URL}{endpoint}", json={"email": email, "password": password}, timeout=5)
        status = response.status_code
        print(f"  -> Status: {status}")
        
        if status == expected_status:
            print("  -> RESULT: PASS")
            return True
        else:
            print(f"  -> RESULT: FAIL (Expected {expected_status}, got {status})")
            print(f"  -> Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"  -> ERROR: {e}")
        return False

def verify():
    print("="*60)
    print("VERIFICATION: Login Persistence & Role Safety")
    print("="*60)
    
    passes = 0
    total = 4
    
    # 1. Valid Teacher Login
    if test_login("teacher@school.com", "teacher123", "/auth/teacher/login", 200, "Valid Teacher Login"):
        passes += 1
        
    # 2. Valid Student Login
    if test_login("james.smith@school.com", "student123", "/auth/student/login", 200, "Valid Student Login"):
        passes += 1

    # 3. Student trying Teacher Login (Must Fail)
    if test_login("james.smith@school.com", "student123", "/auth/teacher/login", 401, "Role Safety: Student -> Teacher Endpoint"):
        passes += 1
        
    # 4. Teacher trying Student Login (Must Fail)
    if test_login("teacher@school.com", "teacher123", "/auth/student/login", 401, "Role Safety: Teacher -> Student Endpoint"):
        passes += 1

    print("\n" + "="*60)
    print(f"SUMMARY: {passes}/{total} Tests Passed")
    print("="*60)

if __name__ == "__main__":
    verify()
