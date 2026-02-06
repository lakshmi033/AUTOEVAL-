
import cv2
import numpy as np
from PIL import Image

def invert_if_dark(image: np.ndarray) -> np.ndarray:
    """
    Checks if image is dark (mean intensity < 128).
    If so, inverts it to be black text on white background.
    """
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
        
    mean_brightness = np.mean(gray)
    
    # If background is dark (low mean brightness), invert
    # We assume documents are usually bright.
    if mean_brightness < 128:
        return cv2.bitwise_not(image)
    return image

def segment_lines(pil_image: Image.Image):
    """
    Segments a full page image into text lines using morphological operations.
    Returns a list of PIL Image crops.
    """
    # Convert to grayscale numpy array
    img = np.array(pil_image.convert("L"))
    
    # Binarize (OTSU)
    thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Dilate to connect text horizontally
    # Kernel width > height to connect characters into lines
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 3))
    dilated = cv2.dilate(thresh, kernel, iterations=1)

    # Find contours
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filter small contours (noise)
    crops = []
    min_area = 100  # Adjust based on resolution
    
    # Sort contours top-to-bottom
    bounding_boxes = [cv2.boundingRect(c) for c in contours]
    # sort by y
    bounding_boxes.sort(key=lambda x: x[1])

    for x, y, w, h in bounding_boxes:
        if w * h > min_area:
            # Add some padding
            pad = 5
            x_start = max(0, x - pad)
            y_start = max(0, y - pad)
            x_end = min(img.shape[1], x + w + pad)
            y_end = min(img.shape[0], y + h + pad)
            
            # Crop from original PIL image
            crop = pil_image.crop((x_start, y_start, x_end, y_end))
            crops.append(crop)
            
    return crops
