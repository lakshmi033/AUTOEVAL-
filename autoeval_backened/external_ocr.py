import base64
import os
import time
import fitz  # PyMuPDF
from openai import OpenAI

# We rely squarely on OpenAI's Vision Model to do Extraction + Cleanup in ONE step.
# Model: gpt-4o-mini
# This model natively understands spatial layout, handwriting, and struck-out text.

def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        print("[OCR Engine] CRITICAL: OPENAI_API_KEY missing. OCR disabled.")
        return None
    return OpenAI(api_key=api_key)

def extract_text_from_file(file_path: str) -> str:
    """
    Master function to handle PDF or Image -> OpenAI Vision
    """
    if file_path.lower().endswith(".pdf"):
        return process_pdf(file_path)
    else:
        return process_image(file_path)

def encode_image_base64(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def process_image(image_path: str, retry_count=0) -> str:
    """
    Two-Phase OCR: Literal Transcription -> Content-Preserving Cleanup
    """
    client = get_openai_client()
    if not client:
        return ""

    try:
        base64_image = encode_image_base64(image_path)
        
        # PHASE 1: LITERAL TRANSCRIPTION
        raw_prompt = """You are a literal transcription engine.
Transcribe every character and word from this image EXACTLY as seen.
- Do not correct spelling.
- Do not remove messy or struck-out text.
- Do not skip sentence endings.
- Do not add any chat or explanations.
Output ONLY the transcription."""

        print("   > [OCR Engine] Phase 1: Literal Extraction (300 DPI)...")
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [{"type": "text", "text": raw_prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]
                }
            ],
            max_tokens=2048,
            temperature=0.0 # Deterministic
        )
        
        raw_text = response.choices[0].message.content.strip()
        print("\n" + "="*50)
        print("RAW OCR TEXT (before cleanup):")
        print(raw_text)
        print("="*50 + "\n")

        # PHASE 2: CONTENT-PRESERVING CLEANUP
        # We use the text-only model for faster cleanup
        cleanup_prompt = f"""You are an OCR cleanup assistant.
Fix obvious spelling errors and broken words in the text below while preserving the layout.

CRITICAL RULES:
1. DO NOT REMOVE CONTENT: Do not remove or shorten any content, sentences, or word endings. 
2. PRESERVE LENGTH: The output must have the same semantic length as the input.
3. STRUCK-OUT: Only remove text if it is explicitly marked as struck out in the raw transcription (if any).
4. NO CHAT: Output ONLY the cleaned text.

RAW TEXT:
{raw_text}
"""
        print("   > [OCR Engine] Phase 2: Content-Preserving Cleanup...")
        cleanup_res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": cleanup_prompt}],
            max_tokens=2048,
            temperature=0.0
        )
        
        cleaned_text = cleanup_res.choices[0].message.content.strip()
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
    Splits PDF -> Images -> OpenAI Vision (Page by Page) at 300 DPI
    """
    doc = fitz.open(pdf_path)
    full_text = []
    
    print(f"[OCR Engine] Processing PDF ({len(doc)} pages) at 300 DPI...")
    
    for i, page in enumerate(doc):
        # Increased to 300 DPI for better handwriting recognition
        pix = page.get_pixmap(dpi=300, colorspace=fitz.csGRAY)
        
        img_data = pix.tobytes("jpg", jpg_quality=85) # High quality
        temp_filename = f"temp_page_{i}_{int(time.time())}.jpg"
        with open(temp_filename, "wb") as f:
            f.write(img_data)
        
        page_text = process_image(temp_filename)
        
        if not page_text.strip():
             page_text = f"[OCR Failed to read Page {i+1}]"
             
        full_text.append(page_text)
        
        try: os.remove(temp_filename)
        except: pass
            
        print(f"[OCR Engine] Processed Page {i+1}/{len(doc)}.")

    print("[OCR Engine] PDF Processing Complete.")
    return "\n\n".join(full_text)
