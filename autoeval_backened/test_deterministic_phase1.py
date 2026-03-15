import os
import json
import re
from openai import OpenAI
from sbert_engine import calculate_similarity_score
from dotenv import load_dotenv

load_dotenv()

# Verify key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("ERROR: OPENAI_API_KEY missing from environment.")
    exit(1)

client = OpenAI(api_key=api_key)

# Mock Inputs for rigorous testing
MOCK_STUDENT_TEXT = """
Q1. The PM of India is directly elected by the people. He is the head of the state.

Q2. Inflation is the rate at which the general level of prices for goods and services is rising. It reduces purchasing power.
"""

MOCK_KEY_TEXT = """
Q1. The Prime Minister is the head of government, not the head of state. He is appointed by the President, usually the leader of the majority party, and not directly elected by the people.

Q2. Inflation refers to the sustained increase in the general price level of goods and services in an economy over a period of time. It results in a decrease in the purchasing power of money.
"""

MOCK_MARK_DISTRIBUTION = {
    "1": 5.0,
    "2": 5.0
}

# Frozen Concept Baseline
MOCK_CONCEPTS = {
    "1": ["appointed by President", "head of government", "not directly elected"],
    "2": ["sustained increase in price level", "decrease in purchasing power"]
}

def regex_segmentation(text):
    """
    STRICT DETERMINISTIC REGEX SEGMENTATION
    Matches Q1., Question 1, Ans 1, etc.
    """
    pattern = r'(?im)^(?:Q|Question|Ans|Answer)[\s\.\:\-]*(\d+)(.*?)(?=(?:^Q|Question|Ans|Answer)[\s\.\:\-]*\d+|\Z)'
    matches = re.findall(pattern, text, re.DOTALL)
    
    segments = {}
    for match in matches:
        q_num = str(match[0]).strip()
        content = match[1].strip()
        segments[q_num] = content
        
    return segments

def evaluate_question_logic(q_num, student_segment, key_segment, concepts_list, max_m):
    # 1. SBERT Similarity (Deterministic, identical normalization in sbert_engine)
    sim_score = calculate_similarity_score(student_segment, key_segment)
    
    # 2. Bounded OpenAI Classification
    prompt = f"""
    You are an academic classifier.
    Analyze the student's answer against the required concepts.
    
    STUDENT ANSWER: {student_segment}
    
    REQUIRED CONCEPTS:
    {json.dumps(concepts_list)}
    
    RULES:
    1. Classify each concept as EXACTLY ONE of: "absent", "mentioned", "explained".
    2. is_coherent: true if the answer is logically readable, false if gibberish.
    3. has_factual_error: true if the student makes a direct false claim contradicting standard facts (e.g. "PM is directly elected").
    
    JSON OUTPUT FORMAT:
    {{
        "concepts_status": {{"concept_name": "absent"}},
        "is_coherent": true,
        "has_factual_error": false,
        "reasoning_summary": "Brief explanation of classification."
    }}
    """
    
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        seed=42, # Determinism Enforcement
        response_format={"type": "json_object"}
    )
    
    result = json.loads(completion.choices[0].message.content)
    
    # 3. Python Response Normalization Layer
    status_map = {"absent": 0.0, "mentioned": 0.5, "explained": 1.0}
    normalized_concepts = {}
    for c in concepts_list:
        raw_val = result.get("concepts_status", {}).get(c, "absent").lower()
        if raw_val not in status_map:
            raw_val = "absent" # Normalizing unexpected outputs
        normalized_concepts[c] = raw_val
        
    is_coherent = bool(result.get("is_coherent", False))
    has_error = bool(result.get("has_factual_error", False))
    reasoning_summary = str(result.get("reasoning_summary", "No reasoning provided."))

    # 4. Fixed Hybrid Scoring Math
    W_SEMANTIC = 0.6
    W_COVERAGE = 0.3
    W_REASONING = 0.1
    
    coverage_ratio = sum(status_map[v] for v in normalized_concepts.values()) / max(len(concepts_list), 1)
    reasoning_score = 1.0 if is_coherent else 0.0
    
    raw_ratio = (W_SEMANTIC * sim_score) + (W_COVERAGE * coverage_ratio) + (W_REASONING * reasoning_score)
    
    # Bounded penalty logic
    penalty = 0.0
    if has_error:
        # Example D shows a 0.2 flat penalty for factual contradiction, up to 20% of the maximum
        # Actually in the plan it was `-0.20` ratio reduction.
        penalty = 0.2
        
    final_ratio = max(0.0, raw_ratio - penalty)
    final_marks = round(final_ratio * max_m, 1)
    
    return {
        "marks_obtained": final_marks,
        "sbert_score": sim_score,
        "coverage_ratio": coverage_ratio,
        "reasoning_score": reasoning_score,
        "penalty_applied": penalty,
        "factual_error": has_error,
        "concepts_status": normalized_concepts,
        "reasoning_summary": reasoning_summary
    }

def run_evaluation():
    student_segments = regex_segmentation(MOCK_STUDENT_TEXT)
    key_segments = regex_segmentation(MOCK_KEY_TEXT)
    
    total_obtained = 0.0
    total_max = 0.0
    question_details = {}
    feedback_lines = []
    
    for q_num, max_m in MOCK_MARK_DISTRIBUTION.items():
        total_max += max_m
        if q_num not in student_segments:
            question_details[q_num] = {"marks_obtained": 0.0, "reasoning_summary": "Missing answer segment."}
            feedback_lines.append(f"Q{q_num}: 0.0 / {max_m} — Missing segment.")
            continue
            
        student_seg = student_segments[q_num]
        key_seg = key_segments.get(q_num, "")
        concepts = MOCK_CONCEPTS.get(q_num, [])
        
        q_result = evaluate_question_logic(q_num, student_seg, key_seg, concepts, max_m)
        total_obtained += q_result["marks_obtained"]
        question_details[q_num] = q_result
        
        # Transparent Logging Shape
        fb = f"Feedback Q{q_num}: {q_result['marks_obtained']}/{max_m} Marks\n"
        fb += f"Calculation Trace: [SBERT: {q_result['sbert_score']:.2f} | Concept: {q_result['coverage_ratio']:.2f} | Reason: {q_result['reasoning_score']:.1f}] -> Penalty: -{q_result['penalty_applied']:.2f}\n"
        fb += f"Concepts Matched: {json.dumps(q_result['concepts_status'])}\n"
        fb += f"Examiner Note: {q_result['reasoning_summary']}\n"
        feedback_lines.append(fb)
        
    percentage = (total_obtained / total_max) * 100 if total_max > 0 else 0.0
    
    return {
        "score_ratio": total_obtained / total_max if total_max > 0 else 0.0,
        "total_obtained": total_obtained,
        "total_max": total_max,
        "percentage": percentage,
        "question_details": question_details,
        "feedback": "\n".join(feedback_lines)
    }

if __name__ == "__main__":
    print("=== BEGIN DETERMINISTIC ENGINE IN-MEMORY VALIDATION ===")
    
    # We will simulate "Retry" by looping 3 times. 
    # Must produce 100% identical floats and text every time.
    for i in range(1, 4):
        print(f"\n================ RUN {i}================")
        result = run_evaluation()
        print(f"Total Marks: {result['total_obtained']} / {result['total_max']}")
        print(f"Percentage: {result['percentage']:.1f}%")
        print("Feedback Breakdowns:")
        print(result['feedback'])

