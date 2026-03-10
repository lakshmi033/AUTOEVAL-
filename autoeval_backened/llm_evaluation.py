
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
        
        ### GRADING INSTRUCTIONS:
        For EACH question, do the following steps. DO NOT perform any arithmetic yourself.
        
        **STEP 1: LIST KEY CONCEPTS**
        - From the Answer Key for this specific question, list ONLY the major distinct scorable concepts.
        - Use roughly 1 concept per mark available (so a 3-mark question gets ~3-4 concepts, a 7-mark question gets ~7-9 concepts MAXIMUM).
        - Store these as: `key_concepts` — a list of short concept labels.
        
        **STEP 2: MATCH CONCEPTS**
        - Check which of these key_concepts are clearly and substantively present in the student's answer.
        - Set `matched_count` = number of matched concepts (integer).
        - Do NOT give credit for bare keyword mentions. The student must demonstrate understanding.
        
        **STEP 3: SHORT ANSWER DETECTION**
        - For questions worth 5 or more marks: if the student's text is very short (fewer than 3 sentences or lacks depth), set `short_answer_cap` to true.
        
        **STEP 4: FACTUAL PENALTIES**
        - If the student stated something directly contradicting the answer key, set `penalty` to a non-zero float (e.g., 0.5). Otherwise 0.0.
        
        **STEP 5: REASONING NOTE**
        - Write one sentence explaining your decision in `reasoning`.
        
        ### OUTPUT FORMAT (JSON ONLY, all questions must appear):
        {{
            "question_evaluations": {{
                "1": {{
                    "key_concepts": ["Concept A", "Concept B", "Concept C"],
                    "matched_count": 2,
                    "short_answer_cap": false,
                    "penalty": 0.0,
                    "reasoning": "Student covered A and B but missed C."
                }},
                "6": {{
                    "key_concepts": ["Concept A", "Concept B", "Concept C", "Concept D", "Concept E", "Concept F", "Concept G"],
                    "matched_count": 2,
                    "short_answer_cap": true,
                    "penalty": 0.5,
                    "reasoning": "Short answer, only touched A and B."
                }}
            }}
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
                
                # -------------------------------------------------------
                # PYTHON MATH ENGINE — All arithmetic done here, not in LLM
                # -------------------------------------------------------
                if 'question_evaluations' in result and mark_distribution:
                    total_obtained = 0.0
                    question_scores = {}
                    feedback_lines = [f"Global SBERT Score: {sbert_score:.2f}\n"]
                    
                    for q_num, data in result['question_evaluations'].items():
                        try:
                            # 1. Fetch max marks
                            max_marks = float(mark_distribution.get(str(q_num), 3.0))
                            
                            # 2. Derive total_concepts from the actual listed array — never trust an LLM-given integer
                            key_concepts = data.get('key_concepts', [])
                            total = float(len(key_concepts)) if key_concepts else float(data.get('total_concepts', 1))
                            if total <= 0: total = 1.0
                            matched = float(data.get('matched_count', data.get('matched_concepts', 0)))
                            matched = min(matched, total)  # Cannot match more than total
                            
                            # 3. Pure coverage ratio formula
                            coverage_ratio = matched / total
                            base_marks = coverage_ratio * max_marks
                            
                            # 4. Short-answer hard cap for high-value questions
                            short_cap = data.get('short_answer_cap', data.get('short_answer_cap_triggered', False))
                            cap_applied = False
                            if short_cap and max_marks >= 5.0 and base_marks > (max_marks * 0.43):
                                base_marks = round(max_marks * 0.43, 1)  # Cap at ~3/7 = 43%
                                cap_applied = True
                            
                            # 5. Apply factual penalty
                            penalty = float(data.get('penalty', data.get('factual_penalty_deduction', 0.0)))
                            final_q_mark = max(0.0, base_marks - penalty)
                            final_q_mark = round(final_q_mark, 1)
                            
                            question_scores[q_num] = final_q_mark
                            total_obtained += final_q_mark
                            
                            # 6. Build feedback line — Python injects the actual marks
                            concepts_str = ", ".join(key_concepts) if key_concepts else "(not listed)"
                            penalty_str = f"-{penalty} Marks" if penalty > 0 else "None"
                            cap_str = " [Short-Answer Cap Applied]" if cap_applied else ""
                            reasoning = data.get('reasoning', '')
                            feedback_lines.append(
                                f"Q{q_num}:\n"
                                f"- Concepts: [{concepts_str}]\n"
                                f"- Coverage: {int(matched)}/{int(total)} concepts matched\n"
                                f"- Marks: {final_q_mark}/{max_marks}{cap_str}\n"
                                f"- Penalty: {penalty_str}\n"
                                f"- Reasoning: {reasoning}\n"
                            )
                            
                            print(f"[Math Engine] Q{q_num}: {matched}/{total} concepts | {final_q_mark}/{max_marks} marks")
                            
                        except Exception as calc_err:
                            print(f"[Math Engine] Error calculating Q{q_num}: {calc_err}")
                            pass
                    
                    # Store results
                    result['question_scores'] = question_scores
                    result['feedback'] = "\n".join(feedback_lines)
                    
                    total_max = sum(mark_distribution.values())
                    if total_max > 0:
                        calculated_score = total_obtained / total_max
                        result['score'] = max(0.0, min(1.0, float(calculated_score)))
                        print(f"[Math Engine] FINAL: {total_obtained:.1f}/{total_max:.0f} = {calculated_score*100:.1f}%")
                    else:
                        result['score'] = 0.0
                        
                # Fallback for old format
                elif 'question_scores' in result and mark_distribution:
                    total_obtained = sum([float(v) for v in result['question_scores'].values() if str(v).replace('.','').isdigit()])
                    total_max = sum(mark_distribution.values())
                    result['score'] = max(0.0, min(1.0, float(total_obtained / total_max) if total_max > 0 else 0.0))
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
