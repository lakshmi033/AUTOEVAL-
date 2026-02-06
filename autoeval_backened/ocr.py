from PIL import Image
import pytesseract
import fitz  # PyMuPDF
import io
import numpy as np
import cv2
import os
from typing import Tuple
from trocr import extract_text_with_trocr
from ocr_utils import invert_if_dark

# Configure Tesseract (Windows)
if os.name == "nt":
    possible_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ]
    for path in possible_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            break


# ----------------------------------------------------------
# Normalize text
# ----------------------------------------------------------
def normalize_text(text: str) -> str:
    if not text:
        return ""
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    return "\n".join(lines)


# ----------------------------------------------------------
# Validate OCR output
# ----------------------------------------------------------
def validate_ocr_result(text: str, source="OCR") -> Tuple[bool, str]:
    if not text or not text.strip():
        return False, f"{source}: Empty text"

    t = text.strip()

    if len(t) < 5:
        return False, f"{source}: Too short ({len(t)} chars)"

    no_space = t.replace(" ", "").replace("\n", "")
    if len(no_space) > 3:
        freq = {}
        for c in no_space:
            freq[c] = freq.get(c, 0) + 1
        common = max(freq, key=freq.get)
        if freq[common] / len(no_space) > 0.7:
            return False, f"{source}: Garbage pattern (repeated '{common}')"

    words = [w for w in t.split() if any(c.isalpha() for c in w)]
    if len(words) < 2:
        return False, f"{source}: Not enough meaningful words"

    digit_count = sum(c.isdigit() for c in t)
    count2 = len(t.replace(" ", ""))
    if count2 > 0 and digit_count / count2 > 0.7:
        return False, f"{source}: Mostly digits (garbage)"

    return True, ""


# ----------------------------------------------------------
# Preprocess for Tesseract
# ----------------------------------------------------------
def preprocess_for_tesseract(pil: Image.Image, aggressive=False):
    img = np.array(pil)

    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    else:
        gray = img.copy()

    gray = invert_if_dark(gray)

    h = gray.shape[0]
    scale = 2.0 if h < 500 else 1.5 if h < 1000 else 1.2
    gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

    if aggressive:
        _, gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    else:
        gray = cv2.adaptiveThreshold(gray, 255,
                                     cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                     cv2.THRESH_BINARY, 11, 2)

    gray = cv2.medianBlur(gray, 3)
    return gray


# ----------------------------------------------------------
# Detect handwriting (placeholder)
# ----------------------------------------------------------
def is_likely_handwritten(_img: Image.Image) -> bool:
    return False


# ----------------------------------------------------------
# Main: extract text from image
# ----------------------------------------------------------
def extract_text_from_image(path: str, debug=True) -> str:
    pil_img = Image.open(path)

    if debug:
        print("\n" + "=" * 60)
        print(f"OCR DEBUG: {os.path.basename(path)}")
        print(f"Size: {pil_img.size}, Mode: {pil_img.mode}")
        print("=" * 60)

    # 1. If handwritten → TrOCR
    if is_likely_handwritten(pil_img):
        try:
            trocr_text = extract_text_with_trocr(pil_img)
            raw = trocr_text or ""

            if debug:
                print("TrOCR RAW:", raw[:200])

            if raw:
                norm = normalize_text(raw)
                ok, msg = validate_ocr_result(norm, "TrOCR")
                if ok:
                    return norm
                else:
                    if debug:
                        print("TrOCR validation failed:", msg)

        except Exception as e:
            if debug:
                print("TrOCR failed:", str(e))

    # 2. Tesseract for printed text
    if debug:
        print("Using Tesseract OCR")

    best_text = ""
    best_score = -1

    preprocess_modes = [
        ("adaptive", False),
        ("otsu", True),
    ]

    psm_modes = [6, 3, 11, 12, 1]

    for prep_name, aggressive in preprocess_modes:
        if debug:
            print("Preprocess mode:", prep_name)

        try:
            gray = preprocess_for_tesseract(pil_img, aggressive)
        except Exception as e:
            if debug:
                print("Preprocess failed:", str(e))
            continue

        for psm in psm_modes:
            try:
                raw = pytesseract.image_to_string(
                    gray, config=f"--oem 3 --psm {psm}"
                )
                norm = normalize_text(raw)
                ok, msg = validate_ocr_result(norm, f"Tesseract-PSM{psm}")

                if ok:
                    words = [w for w in norm.split() if any(c.isalpha() for c in w)]
                    score = len(words) * 10 + len(norm)

                    if score > best_score:
                        best_score = score
                        best_text = norm

            except Exception as e:
                if debug:
                    print(f"PSM {psm} failed:", str(e))
                continue

    if best_text:
        if debug:
            print("\n" + "=" * 60)
            print("OCR SUCCESS")
            print(best_text[:200])
            print("=" * 60)
        return best_text

    raise Exception("Failed to extract meaningful text from image")


# ----------------------------------------------------------
# Extract text from PDF
# ----------------------------------------------------------
def extract_text_from_pdf(path: str, debug=True) -> str:
    doc = fitz.open(path)
    full = ""

    if debug:
        print("\n" + "=" * 60)
        print("PDF OCR:", os.path.basename(path))
        print("Pages:", len(doc))
        print("=" * 60)

    try:
        for i, page in enumerate(doc):
            if debug:
                print(f"-- Page {i+1} --")

            # 1. Direct extraction
            txt = page.get_text().strip()
            if txt and len(txt) > 10:
                norm = normalize_text(txt)
                ok, _ = validate_ocr_result(norm, f"PDF-Page{i+1}-Direct")
                if ok:
                    full += norm + "\n"
                    continue

            # 2. OCR scanned page
            if debug:
                print("Using OCR for scanned page")

            pix = page.get_pixmap(dpi=300)
            pil_img = Image.open(io.BytesIO(pix.tobytes("png")))

            temp = f"temp_pdf_page_{i}.png"
            pil_img.save(temp)

            try:
                txt2 = extract_text_from_image(temp, debug=False)
                ok, _ = validate_ocr_result(txt2, f"PDF-Page{i+1}-OCR")
                if ok:
                    full += txt2 + "\n"
            except:
                pass
            finally:
                if os.path.exists(temp):
                    os.remove(temp)

        doc.close()

        if not full.strip():
            raise Exception("No text extracted from PDF")

        ok, msg = validate_ocr_result(full, "PDF-Final")
        if not ok:
            raise Exception(msg)

        return full

    except Exception as e:
        doc.close()
        raise e
