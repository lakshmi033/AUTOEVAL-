
import os
import json
import time
from llm_evaluation import evaluate_semantic_content
from external_ocr import extract_text_from_file
from dotenv import load_dotenv

load_dotenv()

def run_final_verification():
    print("\n" + "="*60)
    print(" 🏁 AUTOEVAL+ FINAL SYSTEM VERIFICATION")
    print("="*60)

    # 1. TEST DATA
    student_text = """
    Q1. Power sharing is when power is divided between the legislature, executive, and judiciary. It reduces conflict.
    Q2. Federalism is division of power. It is a system. I think the Prime Minister is directly elected by the people.
    """
    key_text = """
    Q1: What is Power Sharing? (3 marks). Answer: Distribution of power among organs (leg, exec, jud). Reduces conflict.
    Q2: Define Federalism. (7 marks). Answer: Division of power between central and constituent units.
    """
    mark_dist = {"1": 3.0, "2": 7.0}
    concepts = {
        "1": ["organs distribution", "legislature/executive/judiciary", "reduces conflict"],
        "2": ["division of power", "central and constituent units"]
    }

    print("\n[STEP 1] Running Strict Evaluation (Run A)...")
    res1 = evaluate_semantic_content(student_text, key_text, mark_dist, concepts)
    
    # 2. VERIFY PENALTIES
    # Q2 has a factual error: "PM is directly elected"
    q2_score = res1.get('question_scores', {}).get('2', 0.0)
    print(f"\n[STRICTNESS CHECK] Q2 Score: {q2_score}/7.0")
    if "FACTUAL ERROR" in str(res1.get('feedback', '')):
        print("✅ PENALTY DETECTED: Factual error deduction successfully applied.")
    else:
        print("❌ PENALTY MISSING: Check factual error detection.")

    # 3. TWIN RUN CONSISTENCY
    print("\n[STEP 2] Running Consistency Check (Run B)...")
    res2 = evaluate_semantic_content(student_text, key_text, mark_dist, concepts)
    
    score_a = res1['score']
    score_b = res2['score']
    variance = abs(score_a - score_b)
    
    print(f"\n[STABILITY CHECK] Variance: {variance*100:.4f}%")
    if variance == 0:
        print("✅ SUCCESS: System is 100% Deterministic.")
    else:
        print("❌ STABILITY ISSUE: Non-zero variance detected.")

    print("\n" + "="*60)
    print(" VERIFICATION COMPLETE.")
    print(" If the results above are GREEN, you are ready to push to main.")
    print("="*60 + "\n")

if __name__ == "__main__":
    run_final_verification()
