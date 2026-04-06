import base64
import os
import time
import fitz  # PyMuPDF
from openai import OpenAI

# OCR Engine — AutoEval+
# Model: gpt-4o-mini (Vision for extraction, Text for cleanup)
# Architecture: Per-page raw extraction → Full-document single cleanup pass
# Determinism: temperature=0.0, seed=42 on ALL API calls

# ── FIXED OCR TRANSCRIPTION PROMPT (locked, no dynamic variation) ────────────
_OCR_RAW_PROMPT = """You are a literal transcription engine.
Transcribe every character and word from this image EXACTLY as seen.
- Do not correct spelling.
- Do not remove messy or struck-out text.
- Do not skip sentence endings or trailing fragments.
- Do not add any chat or explanations.
Output ONLY the transcription."""

# ── FIXED CLEANUP PROMPT (locked, no dynamic variation) ──────────────────────
# Scope: VISUAL NOISE REMOVAL ONLY. Spelling, grammar, vocabulary, facts
# and numbers must NEVER be altered. Treat all content as student handwriting.
_CLEANUP_PROMPT_TEMPLATE = """You are a deterministic OCR normalization engine performing VISUAL NOISE REMOVAL ONLY.

ALLOWED operations (character-level, non-semantic):
1. Normalize whitespace — merge broken spaces, fix stray line breaks inside words.
2. Fix character encoding artifacts — e.g., Ã→A, â€™→', broken Unicode glyphs.
3. Correct unambiguous OCR glyph noise — e.g., 'l' misread as '1' ONLY when the surrounding token is clearly alphabetic; '0'↔'O' ONLY when context is unambiguous.
4. Rejoin words split by line-wrap hyphenation — e.g., "consti-\ntution" → "constitution".

STRICTLY FORBIDDEN — zero exceptions:
- Spelling corrections of any kind.
- Grammar or fluency rewrites.
- Vocabulary substitution or paraphrasing.
- Fact correction or knowledge injection.
- Altering any numeric token: dates, coordinates, measurements, percentages, scientific values, roll numbers. Preserve them CHARACTER-FOR-CHARACTER.
- Adding, reordering, or removing any content.
- Applying subject knowledge, syllabus awareness, or domain heuristics.
- Merging content from different sections or questions.

NUMERIC INTEGRITY RULE:
If a token contains any digit (0-9), degree symbol (°), percentage (%), or mathematical operator — leave the ENTIRE token unchanged, exactly as extracted.

DOMAIN NEUTRALITY:
Do NOT use subject knowledge to make corrections. Treat all text as raw handwriting with no domain awareness.

UNCERTAINTY RULE:
If it is unclear whether a change is visual noise correction or semantic alteration — preserve the original token unchanged.

RAW TEXT:
{raw_text}

Output ONLY the normalized text. No explanations, no prefixes, no chat."""


def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        print("[OCR Engine] CRITICAL: OPENAI_API_KEY missing. OCR disabled.")
        return None
    return OpenAI(api_key=api_key)


# ─────────────────────────────────────────────────────────────────────────────
# CORE INTERNAL FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def _extract_raw_text_from_image(image_path: str, client: OpenAI, page_label: str = "") -> str:
    """
    Phase 1 ONLY — Literal transcription of a single image via Vision model.
    Returns raw, uncleaned text. Does NOT run cleanup.
    Deterministic: temperature=0.0, seed=42.
    """
    base64_image = encode_image_base64(image_path)
    label = f"[Page {page_label}] " if page_label else ""

    print(f"   > [OCR Engine] {label}Phase 1: Literal Extraction (300 DPI)...")

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": _OCR_RAW_PROMPT},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }
        ],
        max_tokens=4096,   # Raised from 2048 to prevent truncation on dense pages
        temperature=0.0,  # Deterministic
        seed=42            # Exact reproducibility (OpenAI requirement for determinism)
    )

    raw_text = response.choices[0].message.content.strip()
    print(f"   > [OCR Engine] {label}Raw text length: {len(raw_text)} chars")
    return raw_text


def _cleanup_text(merged_raw_text: str, client: OpenAI) -> str:
    """
    Phase 2 ONLY — Deterministic visual-noise-removal pass on the FULL merged document text.
    Called ONCE on the entire concatenated multi-page raw text.

    SCOPE: Whitespace normalization, encoding artifact repair, unambiguous glyph correction.
    FORBIDDEN: Spelling correction, vocabulary substitution, number alteration, semantic rewrites.
    Deterministic: temperature=0.0, seed=42.
    """
    raw_len = len(merged_raw_text)
    print(f"   > [OCR Engine] Phase 2: Full-Document Cleanup (input: {raw_len} chars)...")
    print(f"   > [OCR Trace] RAW token count (approx): {len(merged_raw_text.split())} words")

    # If the merged document is extremely long (> 12000 chars), chunk it
    # to avoid the output token limit cutting off the tail end of the document.
    if raw_len > 12000:
        print(f"   > [OCR Engine] Document is huge ({raw_len} chars). Using chunked cleanup to prevent truncation...")
        chunks = merged_raw_text.split("\n\n")
        cleaned_chunks = []

        current_chunk_text = ""
        for chunk in chunks:
            if len(current_chunk_text) + len(chunk) > 6000:
                if current_chunk_text.strip():
                    cleaned_chunks.append(_run_single_cleanup_call(current_chunk_text, client))
                current_chunk_text = chunk + "\n\n"
            else:
                current_chunk_text += chunk + "\n\n"

        if current_chunk_text.strip():
            cleaned_chunks.append(_run_single_cleanup_call(current_chunk_text, client))

        cleaned_text = "\n\n".join(cleaned_chunks)
    else:
        cleaned_text = _run_single_cleanup_call(merged_raw_text, client)

    cleaned_len = len(cleaned_text)

    # ── TOKEN-LEVEL TRACE ────────────────────────────────────────────────────
    # Log approximate token diff to detect unexpected semantic changes.
    raw_words   = set(merged_raw_text.split())
    clean_words = set(cleaned_text.split())
    added   = clean_words - raw_words
    removed = raw_words - clean_words
    print(f"   > [OCR Trace] CLEANED token count (approx): {len(cleaned_text.split())} words")
    print(f"   > [OCR Trace] Tokens added   (~): {len(added)}   sample: {list(added)[:5]}")
    print(f"   > [OCR Trace] Tokens removed (~): {len(removed)} sample: {list(removed)[:5]}")
    # ────────────────────────────────────────────────────────────────────────

    # ── SEMANTIC NEUTRALITY SAFEGUARD ───────────────────────────────────────
    # If cleanup returned less than 60% of input length, the LLM likely
    # rewrote or compressed content. Reject and fall back to raw OCR.
    if raw_len > 0 and cleaned_len < raw_len * 0.60:
        print(
            f"   > [OCR Engine] SAFETY FALLBACK: Cleanup returned {cleaned_len} chars vs {raw_len} raw "
            f"({round(cleaned_len/raw_len*100)}% of raw). Below 60% threshold — using raw text to protect literal content."
        )
        print(f"   > [OCR Trace] Fallback reason: output compression exceeds safety threshold.")
        return merged_raw_text
    # ────────────────────────────────────────────────────────────────────────

    print(f"   > [OCR Engine] Cleanup complete. Output: {cleaned_len} chars ({round(cleaned_len/raw_len*100)}% of raw)")
    return cleaned_text

def _run_single_cleanup_call(raw_text_chunk: str, client: OpenAI) -> str:
    """Helper method to run a single cleanup prompt."""
    cleanup_prompt = _CLEANUP_PROMPT_TEMPLATE.format(raw_text=raw_text_chunk)

    cleanup_res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": cleanup_prompt}],
        max_tokens=16384,   # Maxed out to 16k output tokens to guarantee all merged text fits
        temperature=0.0,    # Deterministic
        seed=42             # Exact reproducibility
    )
    return cleanup_res.choices[0].message.content.strip()


# ─────────────────────────────────────────────────────────────────────────────
# PUBLIC API
# ─────────────────────────────────────────────────────────────────────────────

def encode_image_base64(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def extract_text_from_file(file_path: str) -> str:
    """
    Master entry point. Routes PDF or Image to correct processor.
    """
    if file_path.lower().endswith(".pdf"):
        return process_pdf(file_path)
    else:
        return process_image(file_path)


def process_image(image_path: str, retry_count=0) -> str:
    """
    Single-image flow (non-PDF uploads).

    Guaranteed ordering:
      Step 1 — Literal transcription of the image (Phase 1)
      Step 2 — Content-preserving cleanup of the raw text (Phase 2)

    Cleanup runs on the full raw text of this image.
    Deterministic: temperature=0.0, seed=42 on both API calls.
    """
    client = get_openai_client()
    if not client:
        return ""

    try:
        raw_text = _extract_raw_text_from_image(image_path, client)

        print("\n" + "="*50)
        print("RAW OCR TEXT (before cleanup):")
        print(raw_text)
        print("="*50 + "\n")

        cleaned_text = _cleanup_text(raw_text, client)

        print("\n" + "="*50)
        print("CLEANED OCR TEXT:")
        print(cleaned_text)
        print("="*50 + "\n")

        return cleaned_text

    except Exception as e:
        print(f"   > [OCR Engine Error] {e}")
        if retry_count < 2:
            print(f"   > Retrying ({retry_count+1}/2) in 3 seconds...")
            time.sleep(3)
            return process_image(image_path, retry_count + 1)
        return ""


def process_pdf(pdf_path: str) -> str:
    """
    Multi-page PDF OCR — Cross-Page Continuation Safe.

    Guaranteed 3-step ordering:
      Step 1 — Extract raw text from ALL pages independently (Phase 1 per page).
               Cleanup is NOT run here. Trailing fragments at page boundaries are
               preserved exactly as transcribed.

      Step 2 — Concatenate ALL raw pages into one unified document string.
               This guarantees that Q2 starting on page 1 and continuing on page 2
               appears as one continuous block of text.

      Step 3 — Run cleanup ONCE on the full merged document (Phase 2 global).
               The cleanup model now sees the complete document with no artificial
               page boundaries, so it can never accidentally trim cross-page fragments.

    Segmentation runs downstream on this unified string (in llm_evaluation.py).
    Deterministic: temperature=0.0, seed=42 on every API call.
    """
    client = get_openai_client()
    if not client:
        return ""

    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    raw_pages = []

    print(f"[OCR] Page count detected: {total_pages}")
    print(f"[OCR Engine] Processing PDF ({total_pages} pages) at 300 DPI...")

    # ── STEP 1: Raw extraction from all pages ────────────────────────────────
    for i, page in enumerate(doc):
        pix = page.get_pixmap(dpi=300, colorspace=fitz.csGRAY)
        img_data = pix.tobytes("jpg", jpg_quality=85)
        temp_filename = f"temp_page_{i}_{int(time.time())}.jpg"

        with open(temp_filename, "wb") as f:
            f.write(img_data)

        try:
            page_raw = _extract_raw_text_from_image(image_path=temp_filename, client=client, page_label=f"{i+1}/{total_pages}")
        except Exception as e:
            print(f"[OCR Engine] ERROR on page {i+1}: {e}. Inserting placeholder.")
            page_raw = f"[OCR Failed to read Page {i+1}]"

        if not page_raw.strip():
            page_raw = f"[OCR returned blank for Page {i+1}]"

        print(f"[OCR DEBUG] Page {i+1} raw length: {len(page_raw)} chars")
        print(f"[OCR] Page {i+1} processed")
        raw_pages.append(page_raw)

        try:
            os.remove(temp_filename)
        except Exception:
            pass

    # ── STEP 2: Concatenate all raw pages ────────────────────────────────────
    merged_raw = "\n\n".join(raw_pages)
    print(f"[OCR DEBUG] Merged raw total length: {len(merged_raw)}")
    print(f"[OCR] Final merged length: {len(merged_raw)}")

    # ── MANDATORY DEBUG: Write full raw to file so we can confirm Q8-Q10 presence
    try:
        debug_path = os.path.join(os.path.dirname(pdf_path), "ocr_debug_full_raw.txt")
        with open(debug_path, "w", encoding="utf-8") as dbf:
            dbf.write(f"=== OCR DEBUG RAW TEXT DUMP ===\n")
            dbf.write(f"PDF: {pdf_path}\n")
            dbf.write(f"Total pages: {total_pages}\n")
            dbf.write(f"Merged raw length: {len(merged_raw)} chars\n")
            dbf.write("=" * 60 + "\n\n")
            dbf.write(merged_raw)
        print(f"[OCR DEBUG] Full raw text written to: {debug_path}")
    except Exception as dbg_err:
        print(f"[OCR DEBUG] Could not write debug file: {dbg_err}")

    print("\n" + "="*60)
    print("MERGED RAW OCR TEXT (all pages, before cleanup):")
    print(merged_raw)
    print("="*60 + "\n")

    # ── STEP 3: Single cleanup pass on the full document ─────────────────────
    final_text = _cleanup_text(merged_raw, client)
    print(f"[OCR DEBUG] Cleaned total length: {len(final_text)} chars")

    print("\n" + "="*60)
    print("FINAL CLEANED OCR TEXT (full document):")
    print(final_text)
    print("="*60 + "\n")

    print("[OCR Engine] PDF Processing Complete.")
    return final_text
