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
    Uploads a single image as base64 to OpenAI Vision
    """
    client = get_openai_client()
    if not client:
        return ""

    try:
        base64_image = encode_image_base64(image_path)
        
        # PROMPT: Strict constraint to act as a pure transcriptionist, 
        # heavily weighting the preservation of the student's exact layout.
        prompt = """You are an expert handwritten exam transcription engine.
Read the handwriting in this image and transcribe it exactly as written.

CRITICAL RULES:
1. LAYOUT MATTERS: Preserve paragraph breaks, line spacing, and list structures exactly as they appear visually.
2. DO NOT GUESS INTENT: If a word is misspelled, transcribe the misspelling. Do not correct the student's factual or grammatical errors.
3. STRUCK-OUT TEXT: If a word or number is clearly crossed out, IGNORE IT. Only transcribe the final intended text.
4. NUMBERING: Preserve all question numbers exactly as written (e.g., '1.', 'Q1', '1-', etc).
5. NO CHAT: Output ONLY the transcribed text. Do not add explanations or introductory phrases.
"""

        print("   > [OCR Engine] Sending image to OCR Engine (Tesseract + Transformer + AI cleanup)...")
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=2048
        )
        
        extracted_text = response.choices[0].message.content.strip()
        print(f"   > [OCR Engine] Success! Extracted {len(extracted_text)} characters.")
        return extracted_text

    except Exception as e:
        print(f"   > [OCR Engine Error] {e}")
        if retry_count < 2:
            print(f"   > Retrying ({retry_count+1}/2) in 3 seconds...")
            time.sleep(3)
            return process_image(image_path, retry_count + 1)
        return ""

def process_pdf(pdf_path: str) -> str:
    """
    Splits PDF -> Images -> OpenAI Vision (Page by Page)
    """
    doc = fitz.open(pdf_path)
    full_text = []
    
    print(f"[OCR Engine] Processing PDF ({len(doc)} pages) via OCR Engine...")
    
    for i, page in enumerate(doc):
        # OPTIMIZATION: 
        # OpenAI Vision works best with clean visual contrast.
        # Grayscale + 200 DPI gives perfect readability while keeping base64 size low.
        pix = page.get_pixmap(dpi=200, colorspace=fitz.csGRAY)
        
        # Encoding as JPEG with quality 80
        img_data = pix.tobytes("jpg", jpg_quality=80)
        
        # Save temp file for base64 encoding
        temp_filename = f"temp_page_{i}_{int(time.time())}.jpg"
        with open(temp_filename, "wb") as f:
            f.write(img_data)
        
        # Call API
        page_text = process_image(temp_filename)
        
        # Validation
        if not page_text.strip():
             page_text = f"[OCR Failed to read Page {i+1}]"
             
        full_text.append(page_text)
        
        # Cleanup
        try:
            os.remove(temp_filename)
        except:
            pass
            
        print(f"[OCR Engine] Processed Page {i+1}/{len(doc)}.")

    print("[OCR Engine] PDF Processing Complete.")
    return "\n\n".join(full_text)
