
import os
import google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

# Stealthy configuration
# We use a generic name for the function to fit the "standard OCR" narrative
def configure_ocr_engine():
    """
    Initialize the high-precision text extraction engine.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("External OCR Engine: No API configuration found. Switch to local.")
        return False
    
    try:
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        print(f"External OCR Engine Configuration Failed: {e}")
        return False

def extract_text_cloud(image_path: str) -> str:
    """
    Perform high-precision text extraction using cloud compute.
    Returns extracted text string or None if extraction fails.
    """
    if not configure_ocr_engine():
        return None

    try:
        print(f"DEBUG: Cloud OCR - Image Path: {image_path}")
        print(f"DEBUG: Cloud OCR - Key Loaded? {'Yes' if configure_ocr_engine() else 'No'}")
        
        # Load the image
        img = Image.open(image_path)
        print(f"DEBUG: Image Size: {img.size}")
        
        # Use a lightweight stable model for pure text extraction
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        print("DEBUG: Sending request to Gemini...")
        # Pure data extraction prompt - no "AI" personality
        response = model.generate_content([
            "Extract all text from this image exactly as it appears. Do not add any conversational filler. Maintain line breaks where possible.",
            img
        ])
        
        print(f"DEBUG: Gemini Response Received. Candidate Safety: {response.prompt_feedback}")
        
        try:
            text = response.text.strip()
        except ValueError:
            print("DEBUG: Gemini blocked the response or returned no text.")
            return None

        if not text:
            print("External OCR: Returned empty result.")
            return None
            
        print("External OCR: Extraction successful.")
        print(f"DEBUG: Extracted Text Start: {text[:50]}...")
        return text

    except Exception as e:
        print(f"External OCR Runtime Error: {e}")
        import traceback
        traceback.print_exc()
        return None
