from grading_utils import calculate_grade_and_status

def test_boundaries():
    test_cases = [
        {"ratio": 19/50, "expected_grade": "F", "expected_status": "FAIL"},
        {"ratio": 20/50, "expected_grade": "D", "expected_status": "PASS"},
        {"ratio": 24/50, "expected_grade": "D", "expected_status": "PASS"},
        {"ratio": 24.9/50, "expected_grade": "D", "expected_status": "PASS"},
        {"ratio": 25/50, "expected_grade": "C", "expected_status": "PASS"},
        {"ratio": 44/50, "expected_grade": "A", "expected_status": "PASS"},
        {"ratio": 45/50, "expected_grade": "A+", "expected_status": "PASS"},
        {"ratio": 1/50, "expected_grade": "F", "expected_status": "FAIL"},
    ]

    print("\n--- Running Grading Logic Boundary Tests ---")
    all_passed = True
    for case in test_cases:
        grade, status, _ = calculate_grade_and_status(case["ratio"], 50)
        marks = round(float(case["ratio"] * 50), 1)
        
        match = (grade == case["expected_grade"] and status == case["expected_status"])
        result_icon = "✅" if match else "❌"
        
        print(f"{result_icon} Marks: {marks:4} | Expected: {case['expected_grade']}/{case['expected_status']} | Got: {grade}/{status}")
        
        if not match:
            all_passed = False

    if all_passed:
        print("\n🏆 ALL BOUNDARY TESTS PASSED!")
    else:
        print("\n⚠️ SOME TESTS FAILED. Please check grading_policy.json.")

if __name__ == "__main__":
    test_boundaries()
