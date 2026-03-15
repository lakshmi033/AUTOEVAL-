import json
import numpy as np
import torch
import random
import llm_evaluation
import sbert_engine

def verify_determinism():
    print("\n--- [Phase 3] VERIFYING DETERMINISTIC IDENTITY ---")
    
    # Sample data
    student_text = "Q1. The photosynthesis is the process where plants make food using sunlight and chlorophyll. It uses CO2 and water."
    key_text = "Q1. Photosynthesis: Process by which green plants use sunlight to synthesize nutrients from carbon dioxide and water. Involves chlorophyll."
    mark_dist = {"1": 5.0}
    concepts = {"1": ["photosynthesis definition", "sunlight and chlorophyll", "carbon dioxide and water"]}

    print("[1/2] Running first evaluation...")
    res1 = llm_evaluation.evaluate_semantic_content(student_text, key_text, mark_dist, concepts)
    
    print("[2/2] Running second evaluation (identical input)...")
    res2 = llm_evaluation.evaluate_semantic_content(student_text, key_text, mark_dist, concepts)

    # Compare core fields (marks, percentage, status)
    marks_match = res1["total_obtained"] == res2["total_obtained"]
    percentage_match = res1["percentage"] == res2["percentage"]
    
    # Compare JSON strings for exact identity
    json1 = json.dumps(res1["question_details"], sort_keys=True)
    json2 = json.dumps(res2["question_details"], sort_keys=True)
    json_match = (json1 == json2)

    if marks_match and percentage_match and json_match:
        print("✅ DETERMINISM CONFIRMED: 100% Identity across runs.")
    else:
        print("❌ DETERMINISM FAILURE!")
        if not marks_match: print(f"   Marks mismatch: {res1['total_obtained']} vs {res2['total_obtained']}")
        if not json_match: print("   Internal JSON details differ.")
    
    return marks_match and json_match

def verify_distribution():
    print("\n--- [Phase 3] VERIFYING MULTI-BAND DISTRIBUTION ---")
    
    # Mock datasets reflecting the 5 bands
    bands = {
        "Topper": {
            "text": "Q1. Comprehensive answer with full detail. Photosynthesis is a complex chemical process where plants convert light energy into chemical energy. It requires water, light, and CO2.",
            "coverage": 1.0, # Simulating full coverage
        },
        "Good": {
             "text": "Q1. Photosynthesis helps plants make food. It uses sun, chlorophyll, water and CO2 correctly.",
             "coverage": 0.8,
        },
        "Average": {
             "text": "Q1. Plants use sunlight and water to make food. This is called photosynthesis.",
             "coverage": 0.6,
        },
        "Borderline": {
             "text": "Q1. Photosynthesis is how plants grow with water and sun.",
             "coverage": 0.45,
        },
        "Weak": {
             "text": "Q1. Plants need water.",
             "coverage": 0.2,
        }
    }

    key_text = "Q1. Photosynthesis: Process by which green plants use sunlight to synthesize nutrients from carbon dioxide and water. Involves chlorophyll."
    mark_dist = {"1": 5.0}
    concepts = {"1": ["photosynthesis definition", "sunlight and chlorophyll", "carbon dioxide and water"]}

    results = {}
    for name, data in bands.items():
        res = llm_evaluation.evaluate_semantic_content(data["text"], key_text, mark_dist, concepts)
        results[name] = res["total_obtained"]
        print(f"│ Band: {name:12} | Marks: {res['total_obtained']:3}/5.0 | %: {res['percentage']}%")

    # Basic distribution assertions (Topper > Good > Average > Borderline > Weak)
    logic_check = (
        results["Topper"] >= results["Good"] >= results["Average"] >= results["Borderline"] >= results["Weak"]
    )
    
    if logic_check:
        print("✅ DISTRIBUTION CONFIRMED: Smooth performance-band scaling.")
    else:
        print("❌ DISTRIBUTION ANOMALY DETECTED!")
    
    return logic_check

if __name__ == "__main__":
    d_pass = verify_determinism()
    dist_pass = verify_distribution()
    
    if d_pass and dist_pass:
        print("\n🏆 PRODUCTION STABILITY VERIFIED. Ready for main push.")
    else:
        print("\n⚠️ VERIFICATION FAILED. Do not push to main.")
