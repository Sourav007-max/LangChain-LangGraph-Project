# AI Hiring Co-Pilot — Complete Setup Guide
### From ZIP File to Running Application (Zero Errors)

> **Who this is for:** Anyone who received the project ZIP and wants to run it on their laptop.
> **Time required:** ~20 minutes on a fresh machine.

---

## Before You Start — Check Your OS

This guide covers **Windows**, **macOS**, and **Linux** side by side.
Look for your OS icon: 🪟 Windows · 🍎 macOS · 🐧 Linux

---

## Step 1 — Extract the ZIP

**Windows:**
```
Right-click the ZIP → Extract All → choose a folder with NO spaces in the path
✅ Good:  C:\Projects\ai-hiring-copilot
❌ Bad:   C:\My Documents\My Projects\ai hiring copilot
```

**macOS / Linux:**
```bash
unzip ai-hiring-copilot.zip -d ~/projects/
cd ~/projects/ai-hiring-copilot
```

> ⚠️ **Common mistake:** Spaces and OneDrive/iCloud sync folders cause random errors.
> If your path contains `OneDrive`, work directly on the local drive instead.

---

## Step 2 — Install Python 3.11 or Higher

### Check if Python is already installed

**Windows (PowerShell):**
```powershell
python --version
```

**macOS / Linux (Terminal):**
```bash
python3 --version
```

You need **Python 3.11, 3.12, or 3.13**. If you see 3.11+ → skip to Step 3.

### Install Python

**🪟 Windows:**
1. Go to https://www.python.org/downloads/
2. Click **"Download Python 3.12.x"** (the big yellow button)
3. Run the installer
4. ✅ **CRITICAL: Check "Add Python to PATH"** before clicking Install
5. Click **"Install Now"**
6. Open a **new** PowerShell window and run `python --version`

> If you see `python : command not found` after installing:
> - Open **System Properties → Environment Variables**
> - Add `C:\Users\YOUR_NAME\AppData\Local\Programs\Python\Python312` to PATH
> - Open a **new** terminal and try again

**🍎 macOS:**
```bash
brew install python@3.12
python3 --version
```
*(Install Homebrew first at https://brew.sh if needed)*

**🐧 Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3.12 python3.12-venv python3-pip
python3.12 --version
```

---

## Step 3 — Create the Virtual Environment

> 🔑 **Why venv?** Without it, packages from different projects conflict with each other.
> The venv creates an isolated Python environment just for this project.

Open a terminal **inside the project folder** and run:

**🪟 Windows (PowerShell):**
```powershell
cd "C:\Projects\ai-hiring-copilot"
python -m venv venv
```

**🍎 macOS / 🐧 Linux:**
```bash
cd ~/projects/ai-hiring-copilot
python3.12 -m venv venv
```

### Verify it was created
```
ai-hiring-copilot/
└── venv/           ← this folder should now exist
    ├── Scripts/    (Windows)
    └── bin/        (macOS/Linux)
```

---

## Step 4 — Activate the Virtual Environment

> ⚠️ **Most common error source.** You MUST activate the venv every time you open a new terminal.
> Look for `(venv)` at the start of your prompt — that's how you know it's active.

**🪟 Windows (PowerShell):**
```powershell
.\venv\Scripts\activate
```

Expected result: `(venv) PS C:\Projects\ai-hiring-copilot>`

**🪟 Windows — if you get "execution policy" error:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\venv\Scripts\activate
```

**🍎 macOS / 🐧 Linux:**
```bash
source venv/bin/activate
```

Expected result: `(venv) user@machine:~/projects/ai-hiring-copilot$`

### To deactivate later
```
deactivate
```

---

## Step 5 — Install Python Packages

Make sure you see `(venv)` in your prompt, then run:

```bash
pip install -r requirements.txt
```

This installs ~40 packages. Takes 2–5 minutes depending on internet speed.

### If pip install fails

**Error: `pip: command not found`**
```bash
python -m pip install -r requirements.txt
```

**Error: `Microsoft Visual C++ required` (Windows)**
```
Download and install: https://aka.ms/vs/17/release/vc_redist.x64.exe
Then retry: pip install -r requirements.txt
```

**Error: `SSL certificate verify failed` (corporate network)**
```bash
pip install -r requirements.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org
```

**Error: `ERROR: Could not build wheels for...`**
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### Verify key packages installed
```bash
python -c "import langchain, langgraph, fastapi, groq; print('All packages OK')"
```
Expected: `All packages OK`

---

## Step 6 — Set Up API Keys (.env file)

### Copy the template
**🪟 Windows:**
```powershell
copy .env.example .env
```

**🍎 macOS / 🐧 Linux:**
```bash
cp .env.example .env
```

### Edit the .env file
Open `.env` in VS Code or any text editor and fill in your keys.

**Minimum required to run (all free):**
```env
# Get free at: https://aistudio.google.com/app/apikey
GOOGLE_API_KEY=AIza...your-key-here

# The model to use (free tier)
GEMINI_MODEL=gemini-2.0-flash
DEFAULT_LLM_PROVIDER=gemini

# Generate a random 64-character string for JWT
SECRET_KEY=your-random-64-char-secret-key-change-this-now
```

### Generate a SECRET_KEY
**🪟 Windows:**
```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```
**🍎 macOS / 🐧 Linux:**
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```
Copy the output and paste it as your `SECRET_KEY` in `.env`.

### Free API keys to get
| Service | URL | What it does | Free limit |
|---------|-----|-------------|-----------|
| Google Gemini | https://aistudio.google.com | Main LLM | 1,500 req/day |
| LangSmith | https://smith.langchain.com | Monitor agents | 5,000 traces/month |
| Pinecone | https://pinecone.io | Vector search | 1 index free |

> ⚠️ **Never commit `.env` to Git.** It is already in `.gitignore` — do not remove it.

---

## Step 7 — Initialize the Database

```bash
python -m database.init_db
```

Expected output:
```
✅ All tables created in SQLite
✅ Seed data inserted (3 users + 1 job)
```

### If you see "bcrypt" or "passlib" error
```bash
pip install bcrypt==4.0.1
python -m database.init_db
```

### Verify the database was created
```bash
python -c "from database.init_db import SessionLocal, User; db=SessionLocal(); print(db.query(User).count(), 'users')"
```
Expected: `3 users`

### Demo accounts (created automatically)
| Email | Password | Role |
|-------|----------|------|
| recruiter@hiringapp.com | Admin@123 | Recruiter |
| manager@hiringapp.com | Admin@123 | Hiring Manager |
| admin@hiringapp.com | Admin@123 | Admin |

---

## Step 8 — Start the Backend API

**🪟 Windows:**
```powershell
venv\Scripts\python.exe -m uvicorn backend.main:app --port 8000
```

**🍎 macOS / 🐧 Linux:**
```bash
python -m uvicorn backend.main:app --port 8000
```

Expected output:
```
✅ All tables created in SQLite
ℹ️  Seed data already present, skipping.
INFO: ✅ AI Hiring Co-Pilot API ready
INFO: Uvicorn running on http://127.0.0.1:8000
```

### Verify the server is running
Open: http://localhost:8000/health → should return `{"status":"ok"}`

Interactive API docs: http://localhost:8000/docs

### If you see "Port 8000 already in use"
**🪟 Windows:**
```powershell
netstat -ano | findstr :8000
taskkill /PID <PID_NUMBER> /F
```
**🍎 macOS / 🐧 Linux:**
```bash
lsof -ti:8000 | xargs kill -9
```

### If you see "ModuleNotFoundError: No module named 'jwt'"
```bash
pip install PyJWT
```

### If you see "email-validator is not installed"
```bash
pip install "pydantic[email]"
```

---

## Step 9 — Start the Frontend

You need **two options** — pick one:

### Option A: Streamlit (Recommended for beginners — works immediately)

Open a **new terminal**, activate venv, then:

**🪟 Windows:**
```powershell
.\venv\Scripts\activate
venv\Scripts\python.exe -m streamlit run frontend\streamlit_app.py --server.port 8501
```

**🍎 macOS / 🐧 Linux:**
```bash
source venv/bin/activate
python -m streamlit run frontend/streamlit_app.py --server.port 8501
```

Open: http://localhost:8501

### Option B: React (Professional UI — requires Node.js)

**First, install Node.js 18+ from https://nodejs.org** (LTS version)

After installing, open a **new terminal** to pick up the PATH change, then:

```bash
cd frontend
npm install
npm run dev
```

Open: http://localhost:5173

**🪟 Windows — if `npm` is not found after installing Node:**
```powershell
# Add Node to PATH for this session
$env:PATH = "C:\Program Files\nodejs;" + $env:PATH
npm --version   # should show version number
npm install
npm run dev
```

Permanent fix: Close all terminals, open a new one — Node.js installer adds itself to PATH.

---

## Step 10 — Verify Everything Works

Run the automated check:

**🪟 Windows:**
```powershell
venv\Scripts\python.exe -c "
import httpx
r = httpx.get('http://localhost:8000/health', timeout=3)
print('Backend:', r.status_code, r.json()['status'])
r2 = httpx.post('http://localhost:8000/api/v1/auth/login', json={'email':'recruiter@hiringapp.com','password':'Admin@123'})
print('Login:', r2.status_code, 'role:', r2.json().get('role'))
"
```

Expected:
```
Backend: 200 ok
Login: 200 role: recruiter
```

---

## Quick Start Summary (TL;DR)

```bash
# 1. Extract ZIP, open terminal in project folder

# 2. Create and activate venv
python -m venv venv
.\venv\Scripts\activate          # Windows
# source venv/bin/activate       # macOS/Linux

# 3. Install packages
pip install -r requirements.txt

# 4. Copy env file and add GOOGLE_API_KEY
copy .env.example .env           # Windows
# cp .env.example .env           # macOS/Linux
# Edit .env: set GOOGLE_API_KEY and SECRET_KEY

# 5. Initialize database
python -m database.init_db

# 6. Start backend (terminal 1)
venv\Scripts\python.exe -m uvicorn backend.main:app --port 8000

# 7. Start frontend (terminal 2, venv activated)
venv\Scripts\python.exe -m streamlit run frontend\streamlit_app.py
# OR: cd frontend && npm install && npm run dev
```

---

## Troubleshooting Reference

| Error Message | Cause | Fix |
|---|---|---|
| `python: command not found` | Python not on PATH | Reinstall, check "Add to PATH" |
| `(venv)` not showing | venv not activated | Run activate script again |
| `No module named X` | Wrong Python used | Activate venv first, then install |
| `Port already in use` | Old server still running | Kill the old process (see Step 8) |
| `execution policy` (Windows) | PowerShell restriction | Run `Set-ExecutionPolicy RemoteSigned` |
| `SSL certificate error` | Corporate firewall | Use `--trusted-host` flag with pip |
| `npm: not found` | Node not installed or PATH not updated | Install Node.js, open new terminal |
| `EmailStr validation error` | `.local` domain rejected | Use `@gmail.com` or `@hiringapp.com` emails |
| `bcrypt error` | passlib + bcrypt version mismatch | `pip install bcrypt==4.0.1` |
| `Database is locked` | SQLite held by another process | Stop all uvicorn servers first |
| `LLM model not found` (Groq) | Groq plan limitation | Change `.env`: `DEFAULT_LLM_PROVIDER=gemini` |

---

## Running Tests

```bash
# Activate venv first, then:

# Unit tests — no API keys needed, ~5 seconds
python -m pytest tests/test_e2e_workflow.py -v

# Integration tests — backend server must be running
python -m pytest tests/test_integration.py -v -m "integration and not slow"

# Full AI pipeline test — uses Gemini API (~30 seconds)
python -m pytest tests/test_integration.py::test_full_hiring_pipeline -v -m integration
```

---

## Project Services at a Glance

| Service | URL | Command |
|---------|-----|---------|
| API Backend | http://localhost:8000/docs | `uvicorn backend.main:app --port 8000` |
| Streamlit UI | http://localhost:8501 | `streamlit run frontend/streamlit_app.py` |
| React UI | http://localhost:5173 | `cd frontend && npm run dev` |
