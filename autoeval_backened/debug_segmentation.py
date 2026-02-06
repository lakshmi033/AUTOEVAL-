from ocr_utils import segment_lines
from PIL import Image
import os
import cv2
import numpy as np

# Path to the user's uploaded image
IMAGE_PATH = r"C:/Users/sonys/.gemini/antigravity/brain/d30ec9cb-47a3-4c47-acb9-aab98b00ddfd/uploaded_image_1767463808973.png"
OUTPUT_DIR = "debug_crops"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def debug_run():
    print(f"Loading image: {IMAGE_PATH}")
    try:
        pil_img = Image.open(IMAGE_PATH)
    except Exception as e:
        print(f"Failed to open image: {e}")
        return

    # Run current segmentation
    print("Running segmentation...")
    crops = segment_lines(pil_img)
    print(f"Found {len(crops)} crops.")

    # Save crops
    for i, crop in enumerate(crops):
        crop_path = os.path.join(OUTPUT_DIR, f"line_{i:03d}.png")
        crop.save(crop_path)
        print(f"Saved {crop_path}")

    # Also save the dilated/thresholded image to see what the algorithm sees
    img = np.array(pil_img.convert("L"))
    thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 3))
    dilated = cv2.dilate(thresh, kernel, iterations=1)
    
    cv2.imwrite(os.path.join(OUTPUT_DIR, "debug_thresh.png"), thresh)
    cv2.imwrite(os.path.join(OUTPUT_DIR, "debug_dilated.png"), dilated)
    print("Saved debug intermediates.")

if __name__ == "__main__":
    debug_run()
