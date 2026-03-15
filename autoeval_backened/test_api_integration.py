import json
from llm_evaluation import evaluate_semantic_content

MOCK_STUDENT = """
Q1. The PM of India is directly elected by the people. He is the head of the state.

Q2. Inflation is the rate at which the general level of prices for goods and services is rising. It reduces purchasing power.
"""

MOCK_KEY = """
Q1. The Prime Minister is the head of government, not the head of state. He is appointed by the President, usually the leader of the majority party, and not directly elected by the people.

Q2. Inflation refers to the sustained increase in the general price level of goods and services in an economy over a period of time. It results in a decrease in the purchasing power of money.
"""

MOCK_DIST = {"1": 5.0, "2": 5.0}

MOCK_CONCEPTS = {
    "1": ["appointed by president", "head of government", "not directly elected"],
    "2": ["sustained increase in price level", "decrease in purchasing power"]
}

if __name__ == "__main__":
    print("=== BACKEND API DETERMINISTIC RETRY VALIDATION ===")
    
    outputs = []
    for i in range(1, 4):
        print(f"\nRunning Backend Evaluation #{i}...")
        result = evaluate_semantic_content(
            student_text=MOCK_STUDENT, 
            key_text=MOCK_KEY, 
            mark_distribution=MOCK_DIST, 
            pre_extracted_concepts=MOCK_CONCEPTS
        )
        outputs.append(result)
    
    # Verify Identical
    is_identical = all(json.dumps(outputs[0], sort_keys=True) == json.dumps(out, sort_keys=True) for out in outputs)
    
    print("\n[VERIFICATION]")
    print(f"Are all JSON outputs mathematically identical across retries? {is_identical}")
    
    # Print Sample Output
    print("\n[SAMPLE JSON API OUTPUT]")
    print(json.dumps(outputs[0], indent=2))
