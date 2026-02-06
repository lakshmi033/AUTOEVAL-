
import os
import sys

# Ensure current dir is in path
sys.path.append(os.getcwd())

from ocr import extract_text_from_image

# The image that caused the hang/empty output
img_path = r"C:\Users\sonys\.gemini\antigravity\brain\f974865a-d60b-4a43-9b79-364738fb5789\uploaded_image_1767262711717.png"

print(f"Testing OCR on: {img_path}")
if os.path.exists(img_path):
    try:
        text = extract_text_from_image(img_path)
        print("--- Result ---")
        print(text)
        print("--------------")
    except Exception as e:
        print(f"CRASHED: {e}")
else:
    print("File not found.")
