
import requests

BASE_URL = "http://localhost:8000"

def test_public_classrooms():
    print("Testing /public/classrooms...")
    try:
        r = requests.get(f"{BASE_URL}/public/classrooms")
        if r.status_code == 200:
            print("SUCCESS:", r.json())
            return r.json()
        else:
            print("FAILED:", r.status_code, r.text)
            return []
    except Exception as e:
        print("ERROR:", e)
        return []

def test_register_with_class(class_id):
    if not class_id:
        print("Skipping registration test (no class ID)")
        return

    print(f"\nTesting /register with classroom_id={class_id}...")
    payload = {
        "email": f"student.class{class_id}@school.com",
        "password": "password123",
        "confirm_password": "password123", # Note: Schema doesn't have confirm_pw, main.py doesn't use it, but frontend checks it. Backend only needs 'password'.
        "role": "student",
        "roll_number": "ROLL123",
        "classroom_id": class_id,
        "full_name": "Class Selection Test"
    }
    
    try:
        r = requests.post(f"{BASE_URL}/register", json=payload)
        if r.status_code == 200:
            print("SUCCESS:", r.json())
        else:
            print("FAILED:", r.status_code, r.text)
    except Exception as e:
        print("ERROR:", e)

if __name__ == "__main__":
    classes = test_public_classrooms()
    if classes:
        # Pick the second class if available (to test non-default), else first
        target_class = classes[1]['id'] if len(classes) > 1 else classes[0]['id']
        test_register_with_class(target_class)
