# 🔧 Install Tesseract OCR - Quick Guide

## The Problem
You're seeing this error:
```
TesseractNotFoundError: tesseract is not installed or it's not in your PATH
```

## ✅ Solution: Install Tesseract OCR

### Step 1: Download Tesseract
1. Go to: **https://github.com/UB-Mannheim/tesseract/wiki**
2. Download the Windows installer (latest version)
3. File will be named something like: `tesseract-ocr-w64-setup-5.x.x.exe`

### Step 2: Install Tesseract
1. **Run the installer**
2. **IMPORTANT**: During installation, check the box that says:
   - ✅ **"Add to PATH"** or **"Add Tesseract to system PATH"**
3. Install to default location: `C:\Program Files\Tesseract-OCR`

### Step 3: Verify Installation
Open a **NEW** PowerShell window and run:
```powershell
tesseract --version
```

You should see something like:
```
tesseract 5.x.x
```

### Step 4: Restart Backend
1. Stop your backend server (Ctrl+C)
2. Restart it:
```powershell
cd D:\MAJOR PROJECT\autoeval_backened
.\venv\Scripts\Activate.ps1
python -m uvicorn main:app --reload --port 8000
```

---

## 🔄 Alternative: Manual Path Configuration

If Tesseract is installed but not in PATH, or installed in a different location:

### Step 1: Find Tesseract Installation
Common locations:
- `C:\Program Files\Tesseract-OCR\tesseract.exe`
- `C:\Program Files (x86)\Tesseract-OCR\tesseract.exe`
- `C:\Users\YourName\AppData\Local\Programs\Tesseract-OCR\tesseract.exe`

### Step 2: Update `ocr.py`
Open `autoeval_backened/ocr.py` and find line 13. Uncomment and update:

```python
# Change this line (around line 13):
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# To this (with your actual path):
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

Replace the path with your actual Tesseract installation path.

### Step 3: Restart Backend
Restart your backend server after making changes.

---

## ✅ Test Installation

After installing, test with:
```powershell
cd D:\MAJOR PROJECT\autoeval_backened
.\venv\Scripts\Activate.ps1
python check_ocr_setup.py
```

This will verify Tesseract is working.

---

## 🚨 Still Having Issues?

1. **Check if Tesseract is installed:**
   ```powershell
   tesseract --version
   ```

2. **If command not found:**
   - Tesseract is not in PATH
   - Either reinstall with "Add to PATH" checked
   - Or manually set path in `ocr.py`

3. **Check backend terminal:**
   - Look for error messages
   - The improved error handling should show clearer messages now

---

## 📝 Quick Checklist

- [ ] Tesseract OCR downloaded from GitHub
- [ ] Tesseract installed with "Add to PATH" checked
- [ ] Verified with `tesseract --version` command
- [ ] Backend server restarted
- [ ] Tested OCR upload in frontend

---

**After installation, your OCR should work!** 🎉

