"""
AutoEval+ Diagnostic Script - Deep Root Cause Analysis
Run from: d:\MAJOR PROJECT\autoeval_backened\
Command:  .\venv\Scripts\python.exe diag_check.py > diag_output.txt 2>&1
"""

import sys, os, json, re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from database import SessionLocal
from models import AnswerSheet, AnswerKey, Evaluation

db = SessionLocal()

out = []
def p(s=""):
    out.append(str(s))

p("=" * 70)
p("AUTOEVAL+ DIAGNOSTIC REPORT")
p("=" * 70)

# ---- ANSWER KEYS ----
p("\n\n--- ANSWER KEYS (latest 5) ---")
keys = db.query(AnswerKey).order_by(AnswerKey.id.desc()).limit(5).all()
if not keys:
    p("  No answer keys found in DB.")
else:
    for k in keys:
        p(f"\n  Key ID {k.id} | File: {k.filename} | Subject: {k.subject}")
        raw = k.key_text or ""
        p(f"  key_text length: {len(raw)} chars")
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                if "marks" in parsed:
                    marks = parsed["marks"]
                    concepts = parsed.get("concepts", {})
                    p(f"  [STRUCTURED] mark_distribution keys: {sorted(marks.keys(), key=lambda x: int(x) if str(x).isdigit() else x)}")
                    p(f"  [STRUCTURED] Total questions: {len(marks)}")
                    p(f"  [STRUCTURED] concepts keys: {sorted(concepts.keys(), key=lambda x: int(x) if str(x).isdigit() else x)}")
                else:
                    p(f"  [JSON but no 'marks' key] top-level keys: {list(parsed.keys())}")
            else:
                p(f"  [Non-dict JSON] type: {type(parsed)}")
        except Exception as e:
            p(f"  [NOT JSON] Parse error: {e}")
            p(f"  Raw preview (first 400): {raw[:400]!r}")

# ---- ANSWER SHEETS ----
p("\n\n--- ANSWER SHEETS (latest 5) ---")
sheets = db.query(AnswerSheet).order_by(AnswerSheet.id.desc()).limit(5).all()
if not sheets:
    p("  No answer sheets found in DB.")
else:
    for s in sheets:
        ocr = s.ocr_text or ""
        p(f"\n  Sheet ID {s.id} | Student ID {s.user_id} | File: {s.filename}")
        p(f"  OCR text length: {len(ocr)} chars")
        if ocr:
            p(f"  First 300 chars: {ocr[:300]!r}")
            p(f"  Last 400 chars: {ocr[-400:]!r}")

            # Regex segmentation simulation
            pattern_numeric = r'(?im)^\(?(\d{1,2})[.):\-]\s*(.*?)(?=^\(?\d{1,2}[.):\-]|\Z)'
            matches = re.findall(pattern_numeric, ocr, re.DOTALL)
            found_qs = sorted(set(str(m[0]).strip() for m in matches if str(m[0]).strip().isdigit()), key=int)
            p(f"  Regex segmentation result: {found_qs}")

            # Check for Q8/Q9/Q10 markers
            for q in ['8', '9', '10']:
                markers = [f'{q}.', f'{q})', f'Q{q}', f'Q.{q}', f'question {q}']
                found = any(m.lower() in ocr.lower() for m in markers)
                p(f"  Q{q} explicit marker in OCR: {'YES' if found else 'NO - content unlabeled'}")

            # Check raw content of last 1000 chars for any question presence
            last_chunk = ocr[-1000:]
            p(f"  Last 1000 chars: {last_chunk!r}")
        else:
            p("  WARNING: OCR text is EMPTY")

# ---- EVALUATIONS ----
p("\n\n--- EVALUATIONS (latest 5) ---")
evals = db.query(Evaluation).order_by(Evaluation.id.desc()).limit(5).all()
if not evals:
    p("  No evaluations found.")
else:
    for e in evals:
        p(f"\n  Eval ID {e.id} | Sheet ID {e.answer_sheet_id}")
        try:
            det = json.loads(e.question_details) if e.question_details else {}
            p(f"  Question keys evaluated: {sorted(det.keys(), key=lambda x: int(x) if str(x).isdigit() else x)}")
            p(f"  Total questions evaluated: {len(det)}")
            p(f"  Total marks: {e.total_marks}")
            p(f"  Marks obtained: {e.marks_obtained}")
        except Exception as ex:
            p(f"  Could not parse: {ex}")

# ---- DIAGNOSIS ----
p("\n\n--- ROOT CAUSE DIAGNOSIS ---")
if keys:
    try:
        parsed = json.loads(keys[0].key_text or "{}")
        if isinstance(parsed, dict) and "marks" in parsed:
            n = len(parsed["marks"])
            if n < 10:
                p(f"  CRITICAL BUG FOUND: Latest answer key has only {n} questions in mark_distribution.")
                p(f"  The LLM fallback only triggers for questions IN mark_distribution.")
                p(f"  If the answer key only got 7 questions, fallback never looks for Q8-Q10.")
                p(f"  ACTION: Answer key must be re-uploaded so all 10 questions are extracted.")
            else:
                p(f"  Answer key has {n} questions. mark_distribution is complete.")
        else:
            p("  Could not verify mark_distribution from latest key.")
    except:
        p("  Could not parse latest key for diagnosis.")

db.close()

p("\n" + "=" * 70)
p("END OF DIAGNOSTIC REPORT")
p("=" * 70)

# Write to file (UTF-8 safe)
output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "diag_output.txt")
with open(output_path, "w", encoding="utf-8") as f:
    f.write("\n".join(out))

print(f"Diagnostic written to: {output_path}")
# Also print to console (ASCII safe)
for line in out:
    try:
        print(line)
    except UnicodeEncodeError:
        print(line.encode("ascii", "replace").decode())
