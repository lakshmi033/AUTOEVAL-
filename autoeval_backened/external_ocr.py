import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def configure_ocr_engine():
    """
    Check for OCR.space API key.
    """
    api_key = os.environ.get("OCR_SPACE_API_KEY")
    if not api_key:
        print("External OCR Engine: No OCR_SPACE_API_KEY found.")
        return False
    return True

def extract_text_cloud(image_path: str) -> str:
    """
    Extract text using OCR.space API.
    """
    api_key = os.environ.get("OCR_SPACE_API_KEY")
    if not api_key:
        return None

    try:
        print(f"DEBUG: Cloud OCR (OCR.space) - Processing: {image_path}")
        
        # OCR.space API parameters
        payload = {
            'apikey': api_key,
            'language': 'eng',
            'isOverlayRequired': 'false',
            'detectOrientation': 'true',
            'scale': 'true',
            'OCREngine': '2'  # Engine 2 is often better for numbers/special chars
        }
        
        with open(image_path, 'rb') as f:
            # The API expects the file key to be 'filename' or just the file
            response = requests.post(
                'https://api.ocr.space/parse/image',
                files={'filename': f},
                data=payload,
                timeout=30
            )
            
        result = response.json()
        
        # Check for API errors
        if result.get('IsErroredOnProcessing'):
            error_msg = result.get('ErrorMessage')
            print(f"OCR.space API Error: {error_msg}")
            return None
            
        parsed_results = result.get('ParsedResults')
        if not parsed_results:
            print("OCR.space: No parsed results returned.")
            return None
            
        extracted_text = parsed_results[0].get('ParsedText')
        
        if not extracted_text:
            print("OCR.space: Returned empty text.")
            return None
            
        print("OCR.space: Extraction successful.")
        print(f"DEBUG: Extracted text start: {extracted_text[:50]}...")
        return extracted_text.strip()

    except Exception as e:
        print(f"OCR.space Runtime Error: {e}")
        return None
