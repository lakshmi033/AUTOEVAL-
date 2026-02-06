"""
OCR Setup Diagnostic Script
Run this to check if OCR dependencies are properly configured.
"""

import sys
import os

print("=" * 60)
print("OCR Setup Diagnostic")
print("=" * 60)
print()

# Check Python version
print("1. Python Version:")
print(f"   Python {sys.version}")
print()

# Check PIL/Pillow
print("2. PIL/Pillow:")
try:
    from PIL import Image
    print(f"   ✅ PIL version: {Image.__version__}")
except ImportError as e:
    print(f"   ❌ PIL not installed: {e}")
print()

# Check OpenCV
print("3. OpenCV:")
try:
    import cv2
    print(f"   ✅ OpenCV version: {cv2.__version__}")
except ImportError as e:
    print(f"   ❌ OpenCV not installed: {e}")
print()

# Check PyMuPDF
print("4. PyMuPDF (for PDF):")
try:
    import fitz
    print(f"   ✅ PyMuPDF installed")
except ImportError as e:
    print(f"   ❌ PyMuPDF not installed: {e}")
print()

# Check pytesseract
print("5. pytesseract:")
try:
    import pytesseract
    print(f"   ✅ pytesseract installed")
    
    # Check Tesseract executable
    print("   Checking Tesseract executable...")
    try:
        tesseract_cmd = pytesseract.pytesseract.tesseract_cmd
        print(f"   Tesseract path: {tesseract_cmd}")
        
        # Try to get version
        try:
            version = pytesseract.get_tesseract_version()
            print(f"   ✅ Tesseract version: {version}")
        except Exception as e:
            print(f"   ⚠️  Could not get Tesseract version: {e}")
            print(f"   Checking if file exists...")
            if os.path.exists(tesseract_cmd):
                print(f"   ✅ Tesseract executable found at: {tesseract_cmd}")
            else:
                print(f"   ❌ Tesseract executable NOT found at: {tesseract_cmd}")
                print(f"   Please install Tesseract OCR from:")
                print(f"   https://github.com/UB-Mannheim/tesseract/wiki")
    except Exception as e:
        print(f"   ❌ Tesseract not configured: {e}")
        print(f"   Common paths on Windows:")
        print(f"   - C:\\Program Files\\Tesseract-OCR\\tesseract.exe")
        print(f"   - C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe")
        print(f"   If installed, add to ocr.py:")
        print(f"   pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'")
        
except ImportError as e:
    print(f"   ❌ pytesseract not installed: {e}")
    print(f"   Install with: pip install pytesseract")
print()

# Check transformers/TrOCR
print("6. Transformers (for TrOCR):")
try:
    import transformers
    print(f"   ✅ transformers version: {transformers.__version__}")
except ImportError as e:
    print(f"   ❌ transformers not installed: {e}")
print()

# Check PyTorch
print("7. PyTorch:")
try:
    import torch
    print(f"   ✅ PyTorch version: {torch.__version__}")
    print(f"   CUDA available: {torch.cuda.is_available()}")
except ImportError as e:
    print(f"   ❌ PyTorch not installed: {e}")
print()

# Check TrOCR model loading
print("8. TrOCR Model:")
try:
    from transformers import TrOCRProcessor, VisionEncoderDecoderModel
    print("   Attempting to load TrOCR model (this may take a moment)...")
    processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-handwritten")
    model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-handwritten")
    print("   ✅ TrOCR model loaded successfully")
except Exception as e:
    print(f"   ⚠️  TrOCR model not loaded: {e}")
    print(f"   This is okay - it will download on first use")
print()

# Test image processing
print("9. Image Processing Test:")
try:
    import numpy as np
    from PIL import Image
    
    # Create a test image
    test_img = Image.new('RGB', (100, 100), color='white')
    print("   ✅ Can create PIL images")
    
    # Test OpenCV conversion
    img_array = np.array(test_img)
    print("   ✅ Can convert PIL to numpy array")
    
    # Test grayscale conversion
    import cv2
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    print("   ✅ Can convert to grayscale")
    
except Exception as e:
    print(f"   ❌ Image processing test failed: {e}")
print()

print("=" * 60)
print("Diagnostic Complete!")
print("=" * 60)
print()
print("If you see ❌ errors, install missing packages:")
print("  pip install -r requirements.txt")
print()
print("If Tesseract is not found:")
print("  1. Download from: https://github.com/UB-Mannheim/tesseract/wiki")
print("  2. Install to default location")
print("  3. Or update ocr.py with the correct path")

