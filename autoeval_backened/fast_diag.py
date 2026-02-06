
import os
import sys
import time
sys.path.append(os.getcwd())
from ocr import segment_lines, extract_text_with_trocr
from PIL import Image

img_path = r"C:\Users\sonys\.gemini\antigravity\brain\f974865a-d60b-4a43-9b79-364738fb5789\uploaded_image_1767262711717.png"

print("--- Fast Diagnostic ---")
if os.path.exists(img_path):
    pil_img = Image.open(img_path).convert("RGB")
    print("Image loaded.")
    
    t0 = time.time()
    lines = segment_lines(pil_img)
    dt = time.time() - t0
    print(f"Segmentation took {dt:.2f}s. Found {len(lines)} lines.")
    
    if lines:
        print("Testing TrOCR on FIRST line only...")
        t0 = time.time()
        text = extract_text_with_trocr(lines[0])
        dt = time.time() - t0
        print(f"TrOCR result: '{text}' (took {dt:.2f}s)")
    else:
        print("No lines found.")
else:
    print("File not found.")
