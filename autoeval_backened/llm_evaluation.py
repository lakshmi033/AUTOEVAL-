
import os
import json
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Groq
api_key = os.getenv("GROQ_API_KEY", "").strip()
if not api_key:
    # Fallback try manual read if dotenv failed
    try:
        with open(".env", "r") as f:
            for line in f:
                if line.startswith("GROQ_API_KEY="):
                    api_key = line.strip().split("=", 1)[1].strip('"')
    except:
        pass

if not api_key:
    print("[Evaluation Layer] WARNING: GROQ_API_KEY missing. Reasoning Layer disabled.")
    client = None
else:
    client = Groq(api_key=api_key)
    print(f"[Evaluation Layer] LLM Reasoning Client Initialized.")

import sbert_engine 

# ... (Existing imports)
import traceback

def extract_mark_distribution(key_text: str) -> dict:
    """
    Uses Groq Llama 3 to analyze the raw answer key text and extract the maximum marks 
    allocated for each question.
    Returns a dictionary mapping Question Numbers to their max marks. e.g. {"1": 3.0, "6": 7.0}
    """
    if not client:
        print("[Evaluation Layer] WARNING: Reasoning Client disabled. Cannot extract mark distribution.")
        return {}
        
    try:
        prompt = f"""
        You are an Answer Key Parser in an intelligent marking system.
        
        ### TASK:
        Analyze the following Answer Key text and extract the MAXIMUM MARKS allocated to EACH question.
        
        ### ANSWER KEY TEXT:
        {key_text}
        
        ### REQUIREMENTS:
        1. Find explicitly stated marks for each question (e.g., "(3 marks)", "[7M]", etc.).
        2. If a section has a blanket mark (e.g., "Section B: 7 marks each"), apply it to all questions in that section.
        3. If no marks are specified for ANY questions, gently default to 3.0.
        4. Output a STRICT JSON dictionary where keys are the specific integer question numbers (as strings) and values are the float maximum marks.
        
        ### OUTPUT FORMAT (JSON ONLY):
        {{
            "1": 3.0,
            "2": 3.0,
            "6": 7.0
        }}
        """
        
        models_to_try = [
            "llama-3.3-70b-versatile",
            "llama-3.1-70b-versatile"
        ]
        
        for model in models_to_try:
            try:
                completion = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.0,
                    max_tokens=1024,
                    response_format={"type": "json_object"}
                )
                
                text_response = completion.choices[0].message.content.strip()
                result = json.loads(text_response)
                
                # Normalize keys and values
                parsed = {}
                for k, v in result.items():
                    try:
                        parsed[str(int(str(k).replace("Q","").replace("q","").strip()))] = float(v)
                    except:
                        pass
                        
                print(f"[Evaluation Layer] Extracted Mark Distribution: {parsed}")
                return parsed
                
            except Exception as e:
                print(f"      [!] Groq parsing failed on {model}: {e}")
                continue
                
        return {}
        
    except Exception as e:
        print(f"[Evaluation Layer] Error extracting marks: {e}")
        return {}


def evaluate_semantic_content(student_text: str, key_text: str, mark_distribution: dict = None) -> dict:
    """
    Evaluates the student answer using Hybrid SBERT + Groq (Llama 3) Architecture.
    """
    if not client:
        print("WARNING: No LLM Client. Skipping LLM evaluation.")
        return None

    # ---------------------------------------------------------
    # STAGE 4: SBERT SEMANTIC BASELINE (ADDITIVE LAYER)
    # ---------------------------------------------------------
    print("[Semantic Analysis] Computing SBERT Vector Similarity...")
    try:
        sbert_score = sbert_engine.calculate_similarity_score(student_text, key_text)
        print(f"[Semantic Analysis] SBERT Baseline Score: {sbert_score:.4f}")
    except Exception as sb_e:
        print(f"WARNING: SBERT Layer failed ({sb_e}). Defaulting to 0.0.")
        sbert_score = 0.0

    try:
        mark_distribution_str = json.dumps(mark_distribution) if mark_distribution else "NOT PROVIDED - ASSUME 3.0 MARKS PER QUESTION IF MISSING FROM KEY TEXT"

        # Prompt for Groq Llama 3
        prompt = f"""
        You are an Advanced Academic Reasoning Engine in a Hybrid Evaluation System.
        
        ### TASK:
        Analyze the Student Answer vs Answer Key on a QUESTION-BY-QUESTION basis.
        
        ### INPUTS:
        **Answer Key:**
        {key_text}

        **Student Answer (Cleaned OCR):**
        {student_text}
        
        **GLOBAL SBERT BASELINE SCORE:** {sbert_score:.4f} (Range: 0.0 - 1.0)
        
        **PROVIDED MARK DISTRIBUTION:**
        {mark_distribution_str}
        
        ### ADVANCED HYBRID GRADING SYSTEM:
        Execute the following steps for EACH question:
        
        **STEP 1: CONCEPT-BASED WEIGHTING & EXTRACTION**
        - Dynamically extract the core concepts/keywords from the Answer Key for this specific question.
        - Do NOT hardcode concepts; derive them entirely from the text.
        - The question's Maximum Marks (from Provided Mark Distribution) are evenly or proportionally divided across these extracted concepts to determine the `concept_weight`.
        
        **STEP 2: SEMANTIC COVERAGE & REASONING (The 60/30/10 Formula)**
        For this question, determine three sub-scores (each from 0.0 to 1.0):
        - `semantic_similarity` (0.0-1.0): How closely aligned the student's semantic meaning is to the answer key. Use the GLOBAL SBERT score as an anchor, but adjust it per question.
        - `concept_coverage` (0.0-1.0): The ratio of key concepts successfully identified and explained by the student.
        - `reasoning_quality` (0.0-1.0): The depth, clarity, and logical flow of the student's answer.
        - **Calculate RAW RATIO:** `raw_ratio = (0.6 * semantic_similarity) + (0.3 * concept_coverage) + (0.1 * reasoning_quality)`
        
        **STEP 3: WRONG INFORMATION PENALTY**
        - If the student answer contains factual contradictions against the answer key (e.g., writing "PM is directly elected" instead of "appointed"), apply a penalty.
        - Penalty Rule: Subtract 50% of that specific wrong concept's weight from the question's total score.
        - Adjust the `raw_ratio` downward based on this penalty to produce the `final_ratio` (0.0 to 1.0). Never go below 0.0.
        
        **STEP 4: SCORE DISTRIBUTION RULES**
        Ensure the `final_ratio` accurately reflects academic realism and is not artificially compressed:
        - Excellent: 0.85 - 1.00
        - Good: 0.70 - 0.84
        - Partial: 0.40 - 0.69
        - Poor: 0.20 - 0.39
        - Incorrect: < 0.20
        
        **STEP 5: FINAL QUESTION MARKS CALCULATION & ROUNDING**
        - Multiply the `final_ratio` by the Maximum Marks for this question to get the `obtained_marks`.
        - Round the `obtained_marks` to EXACTLY 1 decimal place (e.g., 2.333 -> 2.3, 4.666 -> 4.7).
        
        ### OUTPUT FORMAT (JSON ONLY):
        {{
            "question_scores": {{"1": 2.0, "2": 2.3, "6": 4.7}},  # Dictionary of obtained_marks (rounded to 1 decimal) mapping string Question Number to float.
            "feedback": "Global SBERT Score: {sbert_score:.2f}\\n\\nQ1:\\n- Concepts Extracted: [A, B, C]\\n- Penalties: None (or describe contradiction, do NOT duplicate this line)\\n- Marks: X/Y (where X is 1-decimal obtained mark, Y is exactly from Provided Mark Distribution)\\n- Reasoning: ...\\n..."
        }}
        """

        # Try models in order of capability
        models_to_try = [
            "llama-3.3-70b-versatile",
            "llama-3.1-70b-versatile",
            "mixtral-8x7b-32768"
        ]

        # Use the first working model
        for model in models_to_try:
            try:
                completion = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.0, # Deterministic
                    max_tokens=4096,
                    response_format={"type": "json_object"} # Force JSON mode
                )
                
                text_response = completion.choices[0].message.content.strip()
                result = json.loads(text_response)
                
                # Perform mathematically exact aggregate calculation in Python 
                if 'question_scores' in result and mark_distribution:
                    total_obtained = 0.0
                    for q_num, ob_marks in result['question_scores'].items():
                        try:
                            total_obtained += float(ob_marks)
                        except:
                            pass
                    
                    total_max = sum(mark_distribution.values())
                    
                    if total_max > 0:
                        calculated_score = total_obtained / total_max
                        result['score'] = max(0.0, min(1.0, float(calculated_score)))
                    else:
                        result['score'] = 0.0
                        
                # Fallback if the LLM hallucinated the old format
                elif 'score' in result:
                    result['score'] = max(0.0, min(1.0, float(result['score'])))
                
                return result
            
            except Exception as model_err:
                print(f"      [!] Groq Model {model} failed: {model_err}")
                continue # Try next model
        print("[Evaluation Layer] ALL Reasoning Layer attempts failed.")
        return None

    except Exception as e:
        print(f"[Evaluation Layer] Critical Failure: {e}")
        return None
