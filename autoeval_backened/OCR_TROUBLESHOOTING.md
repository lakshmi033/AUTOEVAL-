# OCR Troubleshooting Guide

## Common OCR Errors and Solutions

### Error: "OCR Failed Backend error while processing OCR"

This error can occur due to several reasons. Follow these steps to diagnose and fix:

---

## Step 1: Run Diagnostic Script

First, check if all dependencies are properly installed:

```powershell
cd autoeval_backened
.\venv\Scripts\Activate.ps1
python check_ocr_setup.py
```

This will show you:
- ✅ What's working
- ❌ What's missing
- ⚠️ What needs configuration

---

## Common Issues and Fixes

### Issue 1: Tesseract OCR Not Found

**Symptoms:**
- Error mentions "TesseractNotFoundError"
- Error: "Tesseract OCR is not installed or not found"

**Solution:**

1. **Install Tesseract OCR:**
   - Download from: https://github.com/UB-Mannheim/tesseract/wiki
   - Install to default location: `C:\Program Files\Tesseract-OCR`

2. **If Tesseract is installed but not found:**
   - Open `ocr.py`
   - Uncomment and update this line (around line 10):
   ```python
   pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
   ```
   - Replace the path with your actual Tesseract installation path

3. **Verify installation:**
   ```powershell
   python check_ocr_setup.py
   ```

---

### Issue 2: TrOCR Model Loading Error

**Symptoms:**
- Error mentions "torch" or "cuda"
- TrOCR fails to load

**Solution:**

1. **Check PyTorch installation:**
   ```powershell
   python -c "import torch; print(torch.__version__)"
   ```

2. **Reinstall PyTorch if needed:**
   ```powershell
   pip install torch --upgrade
   ```

3. **First-time model download:**
   - TrOCR models download automatically on first use (~500MB)
   - Ensure stable internet connection
   - Wait for download to complete

---

### Issue 3: Missing Python Packages

**Symptoms:**
- `ModuleNotFoundError` for any package
- Import errors

**Solution:**

```powershell
cd autoeval_backened
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

### Issue 4: Image Processing Errors

**Symptoms:**
- OpenCV errors
- PIL/Pillow errors

**Solution:**

```powershell
pip install opencv-python Pillow --upgrade
```

---

## Testing OCR Manually

### Test Tesseract:

```python
import pytesseract
from PIL import Image

# Test with a simple image
img = Image.open("path/to/test_image.png")
text = pytesseract.image_to_string(img)
print(text)
```

### Test TrOCR:

```python
from trocr import extract_text_with_trocr
from PIL import Image

img = Image.open("path/to/test_image.png")
text = extract_text_with_trocr(img)
print(text)
```

---

## Check Backend Logs

When OCR fails, check the backend terminal for detailed error messages:

1. Look for error messages starting with "OCR Error:"
2. Note the error type and message
3. Use this information to identify the specific issue

---

## Updated Error Handling

The OCR endpoints now have improved error handling:

- ✅ Clear error messages
- ✅ Specific error types identified
- ✅ Helpful suggestions for common issues
- ✅ Proper exception handling

---

## Quick Fixes Checklist

- [ ] Tesseract OCR installed and in PATH
- [ ] All Python packages installed (`pip install -r requirements.txt`)
- [ ] Virtual environment activated
- [ ] Backend server restarted after changes
- [ ] Check backend terminal for detailed error messages
- [ ] Run `python check_ocr_setup.py` to diagnose

---

## Still Having Issues?

1. **Check backend terminal** - Look for detailed error messages
2. **Run diagnostic script** - `python check_ocr_setup.py`
3. **Check file permissions** - Ensure uploads folder is writable
4. **Verify image format** - Supported: PNG, JPG, JPEG, PDF
5. **Check image quality** - Very blurry or low-res images may fail

---

## Contact

If issues persist, check:
- Backend terminal logs
- Browser console (F12)
- Network tab for API errors

