
import os
import json
from groq import Groq
from dotenv import load_dotenv
import traceback

# Load environment variables
load_dotenv()

# Configure Groq
api_key = os.getenv("GROQ_API_KEY", "").strip()
if not api_key:
    try:
        with open(".env", "r") as f:
            for line in f:
                if line.startswith("GROQ_API_KEY="):
                    api_key = line.strip().split("=", 1)[1].strip('"')
    except:
        pass

if not api_key:
    client = None
else:
    client = Groq(api_key=api_key)

import sbert_engine

def extract_mark_distribution(key_text: str) -> dict:
    """
    Robust extraction with API Resilience.
    """
    if not client: return {}
    model_primary = "llama-3.3-70b-versatile"
    model_fallback = "llama-3.1-8b-instant"
    
    prompt = f"""
    Analyze the following Answer Key text and extract the MAXIMUM MARKS per question.
    TEXT: {key_text}
    JSON OUTPUT FORMAT: {{"1": 3.0, "2": 7.0, ...}}
    """
    
    def attempt(model):
        completion = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0, seed=42, 
            max_tokens=1024,
            response_format={"type": "json_object"}
        )
        data = json.loads(completion.choices[0].message.content.strip())
        final_dist = {}
        for k, v in data.items():
            try:
                clean_k = str(k).lower().replace("q","").strip()
                if clean_k.isdigit(): final_dist[clean_k] = float(v)
            except: continue
        return final_dist

    try:
        return attempt(model_primary)
    except Exception as e:
        if "rate_limit" in str(e).lower() or "429" in str(e).lower():
            try: return attempt(model_fallback)
            except: return {}
        return {}

def extract_key_concepts_once(key_text: str, mark_distribution: dict) -> dict:
    """
    Robust concept extraction with API Resilience.
    """
    if not client: return {}
    model_primary = "llama-3.3-70b-versatile"
    model_fallback = "llama-3.1-8b-instant"
    
    prompt = f"""
    Identify 3-5 scorable concepts per question for the Answer Key.
    TEXT: {key_text}
    DISTRIBUTION: {json.dumps(mark_distribution)}
    JSON OUTPUT FORMAT: {{"1": ["concept a", "concept b"]}}
    """

    def attempt(model):
        completion = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0, seed=42,
            max_tokens=2048,
            response_format={"type": "json_object"}
        )
        return json.loads(completion.choices[0].message.content.strip())

    try:
        return attempt(model_primary)
    except Exception as e:
        if "rate_limit" in str(e).lower() or "429" in str(e).lower():
            try: return attempt(model_fallback)
            except: return {}
        return {}

def evaluate_semantic_content(student_text: str, key_text: str, mark_distribution: dict = None, pre_extracted_concepts: dict = None) -> dict:
    """
    Universal Stabilized Evaluation with Qualitative Scaling.
    Implements hyper-detailed logging for Step-by-Step Verification.
    """
    if not client: return None

    model_primary = "llama-3.3-70b-versatile"
    model_fallback = "llama-3.1-8b-instant"
    
    concepts_str = json.dumps(pre_extracted_concepts) if pre_extracted_concepts else "Extract scorable points dynamically."
    
    prompt = f"""
    You are a STERN ACADEMIC EXAMINER. Your goal is to grade student answers with maximum rigor.
    
    KEY: {key_text}
    STUDENT_FULL_TEXT: {student_text}
    LOCKED CONCEPTS: {concepts_str}
    
    STRICT GRADING RULES:
    1. ZERO TOLERANCE: Do not credit "intention" or "keywords". Credit only clear, logical explanations.
    2. CLASSIFICATION: For each concept in the LOCKED CONCEPTS, classify as:
       - "absent": Concept is missing, incorrect, or irrelevant.
       - "mentioned": Keyword/concept present but lacking depth or explanation.
       - "explained": Concept is clearly defined, logically explained, and accurate.
    3. REASONING QUALITY: Rate the student's writing quality on this scale:
       - 0.2: Very Weak (fragments, many errors, incoherent)
       - 0.4: Weak (minimal effort, lacks structure)
       - 0.6: Moderate (standard answer, lacks depth)
       - 0.8: Strong (clear, structured, accurate)
       - 1.0: Excellent (expert level, deep insight, examples)
    4. FACTUAL ERROR: Set "factual_error" to true if the student makes a false claim (e.g., "PM is directly elected").
    5. NO HALLUCINATION: Grade ONLY the concepts provided. Do not invent new criteria.
    
    JSON OUTPUT FORMAT:
    {{
        "question_evaluations": {{
            "1": {{
                "student_answer_segment": "...",
                "concepts_status": {{"concept_name": "absent/mentioned/explained"}},
                "reasoning_quality_score": 0.2,
                "factual_error": false,
                "reasoning": "...",
                "critically_short": false
            }}
        }}
    }}
    """

    print("\n" + "="*50)
    print("STEP 3: [STRICT EXAMINER PROMPT]")
    print(prompt)
    print("="*50 + "\n")

    # Model execution
    result = None
    try:
        completion = client.chat.completions.create(
            model=model_primary,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0, seed=42, 
            max_tokens=4096,
            response_format={"type": "json_object"}
        )
        raw_response = completion.choices[0].message.content.strip()
        print("\n" + "="*50)
        print("STEP 3: [RAW LLM RESPONSE]")
        print(raw_response)
        print("="*50 + "\n")
        result = json.loads(raw_response)
    except Exception as e:
        error_msg = str(e).lower()
        if "rate_limit" in error_msg or "429" in error_msg:
            print(f"[Evaluation] Rate limited. Falling back to {model_fallback}...")
            try:
                completion = client.chat.completions.create(
                    model=model_fallback,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.0, seed=42, 
                    max_tokens=4096,
                    response_format={"type": "json_object"}
                )
                raw_response = completion.choices[0].message.content.strip()
                result = json.loads(raw_response)
            except Exception as e2:
                print(f"[Evaluation] Fallback failed: {e2}")
                return None
        else:
            print(f"[Evaluation] API error: {e}")
            return None

    if not result: return None

    try:
        if not mark_distribution:
            # Default to 5.0 if not provided, though it should be handled by extract_mark_distribution
            mark_distribution = {str(i): 5.0 for i in range(1, 11)}

        total_obtained = 0.0
        question_scores = {}
        feedback_lines = []
        evals = result.get('question_evaluations', {})
        
        # PYTHON AUTHORITY: Strict Weights
        # 0.0 = Absent, 0.5 = Mentioned (Half credit), 1.0 = Explained (Full)
        status_map = {"absent": 0.0, "mentioned": 0.5, "explained": 1.0}

        print("\n" + "="*50)
        print("STEP 4: [STRICT SCORING CALCULATION]")
        
        for q_num, max_m in mark_distribution.items():
            try:
                q_id = str(q_num).strip().lower().replace("q", "").replace("question", "").strip()
                item = None
                for ek, ev in evals.items():
                    clean_ek = str(ek).lower().replace("q", "").replace("question", "").strip()
                    if clean_ek == q_id:
                        item = ev
                        break
                
                if not item:
                    print(f"Q{q_num}: [NOT FOUND]")
                    question_scores[str(q_num)] = 0.0
                    feedback_lines.append(f"Q{q_num} ΓÇö 0.0/{max_m} marks [Not Found]")
                    continue

                segment = item.get('student_answer_segment', '[Empty]')
                
                # Concept Coverage Calculation (Average of 0, 0.5, 1.0)
                status = item.get('concepts_status', {})
                coverage = sum(status_map.get(v.lower(), 0.0) for v in status.values()) / (len(status) if status else 1)
                
                # Reasoning Quality (Strictly from LLM classification)
                # Ensure it stays within [0.2, 1.0]
                llm_reasoning_score = float(item.get('reasoning_quality_score', 0.4))
                reas_quality = max(0.2, min(1.0, llm_reasoning_score))

                # SBERT Similarity
                from sbert_engine import calculate_similarity_score
                sim_score = calculate_similarity_score(segment, key_text) 
                
                # Hybrid Weights (Final Authority: Python)
                # score_ratio = 0.6 * sim + 0.3 * coverage + 0.1 * reasoning
                ratio = (0.6 * sim_score) + (0.3 * coverage) + (0.1 * reas_quality)
                marks = ratio * float(max_m)

                # STERN PENALTIES
                penalty_msg = ""
                # 1. Factual Error: -40% of Question Total
                if item.get('factual_error', False):
                    marks -= (0.4 * float(max_m))
                    penalty_msg += " [FACTUAL ERROR PENALTY: -40%]"
                
                # 2. Critically Short/Vague: -20% of Question Total
                if item.get('critically_short', False) or len(segment.split()) < 10:
                    marks -= (0.2 * float(max_m))
                    penalty_msg += " [VAGUE/SHORT PENALTY: -20%]"

                final_q = round(min(float(max_m), max(0.0, marks)), 1)
                
                print(f"Q{q_num}: Sim={sim_score:.2f}, Cov={coverage:.2f}, Qual={reas_quality:.2f} -> Ratio={ratio:.2f} | Final={final_q}{penalty_msg}")

                total_obtained += final_q
                question_scores[str(q_num)] = final_q

                debug_audit = (
                    f"DEBUG AUDIT:\n"
                    f"SBERT Similarity: {sim_score:.2f}\n"
                    f"Concept Coverage: {coverage:.2f}\n"
                    f"Reasoning Quality: {reas_quality:.2f}\n"
                    f"Score Ratio: {ratio:.2f}\n"
                    f"Marks Awarded: {final_q} / {max_m}{penalty_msg}\n"
                )

                feedback_lines.append(
                    f"Q{q_num} ΓÇö {final_q}/{max_m} marks\n"
                    f"{debug_audit}\n"
                    f"Feedback: {item.get('reasoning', 'No feedback')}"
                )
            except Exception as eq:
                print(f"Error scoring Q{q_num}: {eq}")
                continue

        result['question_scores'] = question_scores
        result['feedback'] = "\n".join(feedback_lines)
        
        t_total = sum(float(m) for m in mark_distribution.values())
        result['score'] = total_obtained / t_total if t_total > 0 else 0.0
        
        print(f"[Evaluation] Universal Script Completed: {total_obtained:.1f}/{t_total:.1f} ({result['score']*100:.1f}%)")
        return result

    except Exception as e:
        print(f"[Evaluation] Logic Error: {e}")
        traceback.print_exc()
        return None
