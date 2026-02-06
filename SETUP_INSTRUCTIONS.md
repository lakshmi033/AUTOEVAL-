# 🚀 AutoEval+ Setup Instructions for VS Code

## Prerequisites

### 1. Install Python
- Download Python 3.11 or 3.12 from [python.org](https://www.python.org/downloads/)
- **IMPORTANT**: During installation, check "Add Python to PATH"
- Verify installation:
  ```powershell
  python --version
  ```

### 2. Install Node.js
- Download Node.js (LTS version) from [nodejs.org](https://nodejs.org/)
- Verify installation:
  ```powershell
  node --version
  npm --version
  ```

### 3. Install Tesseract OCR (Required for OCR functionality)
- Download from: https://github.com/UB-Mannheim/tesseract/wiki
- Install to default location: `C:\Program Files\Tesseract-OCR`
- Add to PATH or note the installation path

---

## Backend Setup (autoeval_backened)

### Step 1: Open VS Code Terminal
1. Open VS Code
2. Open the project folder: `D:\MAJOR PROJECT`
3. Open terminal: `Ctrl + ~` or `Terminal > New Terminal`

### Step 2: Remove Old Virtual Environment
```powershell
cd autoeval_backened
Remove-Item -Recurse -Force venv
```

### Step 3: Create New Virtual Environment
```powershell
python -m venv venv
```

### Step 4: Activate Virtual Environment
```powershell
.\venv\Scripts\Activate.ps1
```

**If you get execution policy error:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then try activating again:
```powershell
.\venv\Scripts\Activate.ps1
```

You should see `(venv)` in your prompt.

### Step 5: Upgrade pip
```powershell
python -m pip install --upgrade pip
```

### Step 6: Install Dependencies
```powershell
pip install -r requirements.txt
```

**Note**: This will take 10-15 minutes as it downloads PyTorch and transformers models.

### Step 7: Configure Tesseract (if needed)
If Tesseract is not in PATH, edit `ocr.py` and add:
```python
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

### Step 8: Run Backend
```powershell
python -m uvicorn main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

**Keep this terminal running!**

---

## Frontend Setup (AUTOEVAL+)

### Step 1: Open New Terminal in VS Code
- Click `+` button in terminal panel or `Ctrl + Shift + ~`

### Step 2: Navigate to Frontend
```powershell
cd AUTOEVAL+
```

### Step 3: Install Dependencies
```powershell
npm install
```

This will take 2-3 minutes.

### Step 4: Run Frontend
```powershell
npm run dev
```

You should see:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

**Keep this terminal running too!**

---

## VS Code Configuration (Optional but Recommended)

### Create `.vscode/settings.json`:
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/autoeval_backened/venv/Scripts/python.exe",
  "python.terminal.activateEnvironment": true,
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true
  }
}
```

### Create `.vscode/launch.json` for debugging:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "main:app",
        "--reload",
        "--port",
        "8000"
      ],
      "jinja": true,
      "justMyCode": true,
      "cwd": "${workspaceFolder}/autoeval_backened"
    }
  ]
}
```

---

## Running the Project

### Method 1: Using VS Code Terminal (Recommended)

1. **Terminal 1 - Backend:**
   ```powershell
   cd autoeval_backened
   .\venv\Scripts\Activate.ps1
   python -m uvicorn main:app --reload --port 8000
   ```

2. **Terminal 2 - Frontend:**
   ```powershell
   cd AUTOEVAL+
   npm run dev
   ```

### Method 2: Using VS Code Tasks

Create `.vscode/tasks.json`:
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Start Backend",
      "type": "shell",
      "command": "python -m uvicorn main:app --reload --port 8000",
      "options": {
        "cwd": "${workspaceFolder}/autoeval_backened"
      },
      "problemMatcher": []
    },
    {
      "label": "Start Frontend",
      "type": "shell",
      "command": "npm run dev",
      "options": {
        "cwd": "${workspaceFolder}/AUTOEVAL+"
      },
      "problemMatcher": []
    },
    {
      "label": "Start Both",
      "dependsOn": ["Start Backend", "Start Frontend"],
      "problemMatcher": []
    }
  ]
}
```

Then run: `Ctrl + Shift + P` → "Tasks: Run Task" → "Start Both"

---

## Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs (Swagger UI)

---

## Troubleshooting

### Issue: "No Python at '...'"
**Solution**: The venv was created on a different machine. Delete `venv` folder and recreate it.

### Issue: "Execution Policy Error"
**Solution**: 
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue: "Module not found"
**Solution**: Make sure venv is activated and install requirements:
```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Issue: "Tesseract not found"
**Solution**: Install Tesseract and update path in `ocr.py`:
```python
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

### Issue: "Port 8000 already in use"
**Solution**: Change port in backend:
```powershell
python -m uvicorn main:app --reload --port 8001
```
Then update `BACKEND_URL` in frontend `AuthContext.tsx` and `Dashboard.tsx`.

### Issue: "npm install fails"
**Solution**: 
```powershell
npm cache clean --force
npm install
```

### Issue: Models download slowly
**Solution**: First run will download TrOCR and SBERT models (~500MB). This is normal and only happens once.

---

## Quick Start Commands

```powershell
# Backend
cd autoeval_backened
.\venv\Scripts\Activate.ps1
python -m uvicorn main:app --reload --port 8000

# Frontend (in new terminal)
cd AUTOEVAL+
npm run dev
```

---

## Project Structure

```
MAJOR PROJECT/
├── autoeval_backened/     # Backend (FastAPI)
│   ├── venv/              # Virtual environment
│   ├── main.py            # FastAPI app
│   ├── requirements.txt   # Python dependencies
│   └── ...
└── AUTOEVAL+/             # Frontend (React)
    ├── node_modules/      # Node dependencies
    ├── src/               # Source code
    └── package.json       # Node dependencies
```

---

## Next Steps

1. ✅ Backend running on port 8000
2. ✅ Frontend running on port 5173
3. ✅ Open http://localhost:5173 in browser
4. ✅ Register a new account
5. ✅ Upload answer sheets and test OCR

---

**Need Help?** Check the error messages and refer to the Troubleshooting section above.

