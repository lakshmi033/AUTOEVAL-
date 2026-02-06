# ⚡ Quick Start Guide - AutoEval+

## 🎯 Fastest Way to Get Started

### Option 1: Automated Setup (Recommended)
```powershell
# Run the setup script
.\setup.ps1
```

### Option 2: Manual Setup

#### Backend Setup:
```powershell
cd autoeval_backened

# Remove old venv (if exists)
Remove-Item -Recurse -Force venv

# Create new venv
python -m venv venv

# Activate venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run backend
python -m uvicorn main:app --reload --port 8000
```

#### Frontend Setup (New Terminal):
```powershell
cd AUTOEVAL+

# Install dependencies
npm install

# Run frontend
npm run dev
```

---

## 🚀 Running in VS Code

### Method 1: Using Terminal (Easiest)

1. **Open VS Code** in `D:\MAJOR PROJECT`
2. **Open Terminal**: `Ctrl + ~`
3. **Terminal 1 - Backend:**
   ```powershell
   cd autoeval_backened
   .\venv\Scripts\Activate.ps1
   python -m uvicorn main:app --reload --port 8000
   ```
4. **Terminal 2 - Frontend** (Click `+` in terminal):
   ```powershell
   cd AUTOEVAL+
   npm run dev
   ```

### Method 2: Using VS Code Tasks

1. Press `Ctrl + Shift + P`
2. Type: `Tasks: Run Task`
3. Select: `Backend: Start Server`
4. Open new terminal and run: `Tasks: Run Task` → `Frontend: Start Dev Server`

---

## 🌐 Access URLs

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## ⚠️ Common Issues & Fixes

### Issue: Execution Policy Error
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue: Python Path Error
**Solution**: Delete `venv` folder and recreate it (the venv was created on a different machine)

### Issue: Module Not Found
**Solution**: Make sure venv is activated and install requirements:
```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Issue: Port Already in Use
**Solution**: Change port:
```powershell
python -m uvicorn main:app --reload --port 8001
```
Then update `BACKEND_URL` in `AUTOEVAL+/src/contexts/AuthContext.tsx` and `AUTOEVAL+/src/pages/Dashboard.tsx`

---

## 📋 Prerequisites Checklist

- [ ] Python 3.11+ installed (check: `python --version`)
- [ ] Node.js installed (check: `node --version`)
- [ ] Tesseract OCR installed (optional, for better OCR)

---

## 📚 Full Documentation

See `SETUP_INSTRUCTIONS.md` for detailed setup instructions.

---

**Happy Coding! 🎉**

