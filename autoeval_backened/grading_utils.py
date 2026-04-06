import json
import os

POLICY_FILE = os.path.join(os.path.dirname(__file__), "grading_policy.json")

def load_policy():
    """Loads the grading policy from the JSON file."""
    try:
        with open(POLICY_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"[Grading Utility] ERROR: Could not load policy file: {e}")
        # Default fallback if file is missing
        return {
            "pass_mark": 20,
            "max_marks": 50,
            "grade_bands": [
                {"min": 45, "max": 50, "grade": "A+"},
                {"min": 40, "max": 44, "grade": "A"},
                {"min": 35, "max": 39, "grade": "B+"},
                {"min": 30, "max": 34, "grade": "B"},
                {"min": 25, "max": 29, "grade": "C"},
                {"min": 20, "max": 24, "grade": "D"},
                {"min": 0, "max": 19, "grade": "F"}
            ]
        }

def calculate_grade_and_status(score_ratio, custom_max=None):
    """
    Calculates grade and PASS/FAIL status based on score_ratio (0.0 to 1.0).
    Returns (grade, status, explain_log).
    """
    policy = load_policy()
    max_marks = custom_max if custom_max is not None else policy.get("max_marks", 50)
    pass_mark = policy.get("pass_mark", 20)
    
    obtained_marks = round(score_ratio * max_marks, 1)
    percentage = round(score_ratio * 100, 2)
    
    grade = "F"
    applied_band = {}
    
    # Sort bands descending by min to handle floating point numbers perfectly
    grade_bands = policy.get("grade_bands", [])
    if not isinstance(grade_bands, list):
        grade_bands = []
        
    sorted_bands = sorted(grade_bands, key=lambda x: x.get("min", 0) if isinstance(x, dict) else 0, reverse=True)
    for band in sorted_bands:
        if obtained_marks >= band["min"]:
            grade = band["grade"]
            applied_band = band
            break
            
    # 2. Determine Pass/Fail (Policy-Driven)
    status = "PASS" if obtained_marks >= pass_mark else "FAIL"
    
    # 3. Validation Logic (Security Check)
    # Ensure no grade 'F' can PASS if pass_mark is higher than F range max
    # And ensure no passing grade can FAIL
    if grade != "F" and status == "FAIL":
        print(f"[Grading Utility] WARNING: Inconsistency detected! Grade {grade} but STATUS FAIL for marks {obtained_marks}")
    if grade == "F" and status == "PASS" and obtained_marks < pass_mark:
         print(f"[Grading Utility] CRITICAL: Grade F passed incorrectly for marks {obtained_marks}")

    explain_log = (
        f"--- Grading Logic Execution ---\n"
        f"Total Obtained = {obtained_marks} / {max_marks}\n"
        f"Percentage = {percentage}%\n"
        f"Grade Band Applied = {grade} ({applied_band.get('min',0)}-{applied_band.get('max',0)})\n"
        f"Pass Threshold = {pass_mark}\n"
        f"Final Decision = {status}\n"
        f"-------------------------------"
    )
    
    print(explain_log)
    
    return grade, status, explain_log
