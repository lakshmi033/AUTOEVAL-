import os
from external_ocr import configure_ocr_engine, extract_text_cloud
from dotenv import load_dotenv

load_dotenv()

print("--- ORC.space Connection Check ---")

if configure_ocr_engine():
    print("API Key found.")
    
    # Create a dummy image for testing if one doesn't exist, or just skip
    # For connection check, we just want to know if the key is loaded.
    # To test actual OCR, we'd need a file.
    
    print("Configuration: OK")
    print(f"Key: {os.environ.get('OCR_SPACE_API_KEY')[:5]}...")
else:
    print("FAILED: API Key not found.")
