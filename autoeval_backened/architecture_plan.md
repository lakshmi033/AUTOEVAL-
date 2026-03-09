# Architecture: Hybrid Free-Tier (Stable)

## 1. The Engine: OCR.space (Free API)
- **Role**: Primary Text Extraction.
- **Why**: Proven capability on handwriting (User confirmed this worked before).
- **Limits**: 25,000 req/month (~800/day).
- **Implementation**: `external_ocr.py`
    - Logic: PDF -> Images -> API Call (Page-by-Page).
    - Throttling: 1.5s delay between pages to avoid free-tier rate limits.

## 2. The Cleanup: Gemini 1.5 Flash (Text Mode)
- **Role**: Spelling and Formatting Correction (Text-to-Text).
- **Why**: Text mode is faster/lighter than Vision mode. Fixes "Paver" -> "Power".
- **Reliability**:
    - **Page-wise**: We clean 1 page at a time (small context = low latency).
    - **Key Rotation**: User provides 4 keys. We cycle them.
    - **Strict Timeout**: 5s per page. If it stalls -> Return Raw OCR.
- **Implementation**: `cleanup_service.py`

## 3. The Fallback: Local Regex
- **Role**: Last line of defense.
- **Implementation**: `cleanup_local.py`
    - Fixes common issues (e.g., "1 ." -> "1.") instantly if Gemini fails.

## Workflow
1. User Uploads PDF.
2. `ocr_multiprocessor.py`: Splits PDF to images.
3. For each image:
    a. Call OCR.space -> Get `raw_text`.
    b. Call Gemini(raw_text) -> Get `clean_text`.
    c. If Gemini fails -> `clean_text = cleanup_local(raw_text)`.
4. Combine all pages -> Return.
