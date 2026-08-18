# AI Hiring Co-Pilot
### Multi-Agent Recruitment Platform using LangGraph

A production-ready AI recruitment platform that automates candidate screening, resume parsing, scoring, interview scheduling, and report generation using a multi-agent LangGraph workflow.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  React Frontend (port 5173)  OR  Streamlit (port 8501)          │
└──────────────────────────┬──────────────────────────────────────┘
                           │ REST API (JWT Auth)
┌──────────────────────────▼──────────────────────────────────────┐
│  FastAPI Backend (port 8000)                                     │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│  LangGraph Multi-Agent Workflow                                  │
│  JD Analyzer → Resume Parser → Candidate Matcher → Shortlisting │
│  → [HUMAN REVIEW] → Interview Scheduler → Reporter              │
└──────────────────────────┬──────────────────────────────────────┘
                           │
              ┌────────────┴────────────┐
         SQLite DB              ChromaDB (vectors)
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| LLM (Free) | Google Gemini 2.0 Flash |
| LLM (Backup) | Groq Llama, OpenAI GPT-4o-mini |
| Orchestration | LangGraph 1.x |
| Backend | FastAPI + SQLAlchemy |
| Database | SQLite (dev) → MySQL (prod) |
| Vector DB | ChromaDB (dev) → Pinecone (prod) |
| Frontend | React 18 + TypeScript + Tailwind |
| Prototype UI | Streamlit |
| Monitoring | LangSmith + agent_logs table |
| Auth | JWT (PyJWT + bcrypt) |

---

## Prerequisites

| Tool | Version | Check |
|------|---------|-------|
| Python | 3.11+ | `python --version` |
| Node.js | 18+ | `node --version` |
| Git | Any | `git --version` |

> **Note:** MySQL and Redis are optional for development — SQLite is used by default.

---

## Setup — Step by Step

### Step 1: Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/ai-hiring-copilot.git
cd ai-hiring-copilot
```

### Step 2: Create Python virtual environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**Mac / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### Step 3: Install Python dependencies

```bash
pip install -r requirements.txt
```

If you see warnings about pip upgrade, run:
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Configure API Keys

```bash
# Windows
copy .env.example .env

# Mac / Linux
cp .env.example .env
```

Open `.env` and fill in your keys:

```env
# REQUIRED — get free at https://aistudio.google.com/app/apikey
GOOGLE_API_KEY=AIza...
GEMINI_MODEL=gemini-2.0-flash
DEFAULT_LLM_PROVIDER=gemini

# OPTIONAL — for monitoring at https://smith.langchain.com/
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=lsv2_...
LANGCHAIN_PROJECT=ai-hiring-copilot

# JWT secret — generate a strong random string
SECRET_KEY=replace-this-with-64-random-characters
```

**Get free API keys:**
- Gemini: https://aistudio.google.com — free, 1500 req/day
- LangSmith: https://smith.langchain.com — free 5000 traces/month
- Pinecone: https://pinecone.io — free starter plan

### Step 5: Initialize the database

```bash
python -m database.init_db
```

Expected output:
```
✅ All tables created in SQLite
✅ Seed data inserted (3 users + 1 job)
```

This creates `hiring_copilot.db` with demo accounts:
| Email | Password | Role |
|-------|----------|------|
| recruiter@hiringapp.com | Admin@123 | recruiter |
| manager@hiringapp.com | Admin@123 | hiring_manager |
| admin@hiringapp.com | Admin@123 | admin |

### Step 6: Start the FastAPI backend

```bash
# Windows (PowerShell, from project root)
venv\Scripts\python.exe -m uvicorn backend.main:app --port 8000

# Mac / Linux
python -m uvicorn backend.main:app --port 8000
```

Verify: http://localhost:8000/health → `{"status": "ok"}`

Interactive API docs: http://localhost:8000/docs

### Step 7A: Start the Streamlit dashboard (no Node needed)

```bash
# Windows
venv\Scripts\python.exe -m streamlit run frontend\streamlit_app.py --server.port 8501

# Mac / Linux
python -m streamlit run frontend/streamlit_app.py --server.port 8501
```

Open: http://localhost:8501

### Step 7B: Start the React frontend

```bash
cd frontend
npm install
npm run dev
```

Open: http://localhost:5173

> On Windows, Node.js must be on PATH. If `npm` is not found, add `C:\Program Files\nodejs` to your PATH or open a new terminal after installing Node.

---

## Running Tests

```bash
# Unit tests only (no server, no API keys, < 5 seconds)
python -m pytest tests/test_e2e_workflow.py -v

# Integration tests (API server must be running on port 8000)
python -m pytest tests/test_integration.py -v -m "integration and not slow"

# Full AI pipeline test (uses real LLM, ~30 seconds)
python -m pytest tests/test_integration.py::test_full_hiring_pipeline -v -m integration

# All tests except slow LLM tests
python -m pytest tests/ -v -m "not slow"
```

---

## Using the Platform

### Full Workflow

1. **Login** → `recruiter@hiringapp.com` / `Admin@123`
2. **Create a Job** → Jobs page → fill title + description
3. **Upload Resumes** → Run Screening page → drag & drop PDF
4. **Start AI Workflow** → agents run automatically (30–60 seconds)
5. **Review Shortlist** → approve/reject candidates (Human-in-the-Loop)
6. **View Interviews** → see AI-scheduled slots + interview questions
7. **Download Report** → markdown report with executive summary

### API Quick Reference

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"recruiter@hiringapp.com","password":"Admin@123"}'

# Upload resume (replace TOKEN)
curl -X POST http://localhost:8000/api/v1/resumes/upload \
  -H "Authorization: Bearer TOKEN" \
  -F "file=@resume.pdf" \
  -F "candidate_email=john@example.com" \
  -F "candidate_name=John Smith"

# Start workflow
curl -X POST http://localhost:8000/api/v1/workflows/start \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"job_id": 1, "resume_ids": [1, 2, 3]}'
```

---

## Project Structure

```
ai-hiring-copilot/
├── .env                    # API keys (never commit!)
├── .env.example            # Template — safe to commit
├── .gitignore
├── requirements.txt
├── pytest.ini
│
├── agents/                 # LangGraph Agent System
│   ├── state.py            # Shared HiringState TypedDict
│   ├── graph.py            # Complete LangGraph workflow
│   ├── jd_analyzer.py      # JD analysis agent
│   ├── resume_parser.py    # PDF resume parsing agent
│   ├── candidate_matcher.py# AI scoring agent
│   ├── shortlisting.py     # Filter node (no LLM)
│   ├── interview_scheduler.py
│   └── reporter.py         # Final report generator
│
├── backend/
│   └── main.py             # FastAPI app (auth, jobs, workflows)
│
├── config/
│   ├── settings.py         # get_llm() factory, get_embeddings()
│   └── monitoring.py       # @log_agent decorator, DB logging
│
├── database/
│   └── init_db.py          # SQLAlchemy models + init_db()
│
├── frontend/
│   ├── streamlit_app.py    # Prototype dashboard (Python)
│   ├── package.json
│   └── src/
│       ├── App.tsx          # React router + providers
│       ├── pages/           # LoginPage, Dashboard, Workflow, Review
│       ├── components/      # Layout, ProtectedRoute
│       ├── services/        # API client (axios)
│       ├── store/           # Zustand global state
│       └── types/           # TypeScript interfaces
│
├── tests/
│   ├── test_e2e_workflow.py # Unit tests (no API keys needed)
│   └── test_integration.py # Live API tests
│
├── lessons/                # Course learning materials
│   ├── phase_01_ai_fundamentals/
│   ├── phase_02_environment_setup/
│   ├── phase_03_api_keys/
│   ├── phase_04_system_design/
│   ├── phase_07_langgraph/
│   └── phase_10_rag_integration/
│
└── uploads/
    └── resumes/            # Uploaded PDF files
```

---

## Switching LLM Providers

Edit `DEFAULT_LLM_PROVIDER` in `.env`:

| Provider | Value | Cost | Speed |
|----------|-------|------|-------|
| Google Gemini | `gemini` | Free (1500/day) | Fast |
| Groq Llama | `groq` | Free (tier 1) | Very fast |
| OpenAI GPT-4o-mini | `openai` | ~$0.001/resume | Moderate |
| Anthropic Claude | `anthropic` | ~$0.003/resume | Moderate |

---

## Switching to MySQL (Production)

1. Install MySQL and create database:
```sql
CREATE DATABASE hiring_copilot CHARACTER SET utf8mb4;
CREATE USER 'hiring_user'@'localhost' IDENTIFIED BY 'StrongPassword@123';
GRANT ALL PRIVILEGES ON hiring_copilot.* TO 'hiring_user'@'localhost';
```

2. Update `.env`:
```env
DATABASE_URL=mysql+pymysql://hiring_user:StrongPassword@123@localhost:3306/hiring_copilot
```

3. Re-run init:
```bash
python -m database.init_db
```

---

## Monitoring

- **LangSmith**: Set `LANGCHAIN_TRACING_V2=true` in `.env` → every agent call traced automatically at https://smith.langchain.com
- **Agent logs**: `GET /api/v1/monitoring/stats` — per-agent latency + error rates
- **Live tail**: `GET /api/v1/monitoring/logs?limit=20`

---

## Security Notes

- Never commit `.env` — it's in `.gitignore`
- Rotate API keys if they appear in any chat or log
- Set spending limits on all API dashboards
- JWT tokens expire in 60 minutes (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)
- All passwords are bcrypt-hashed (never stored plain text)

---

## Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| `No module named X` | venv not activated | Run `.\venv\Scripts\activate` |
| Port 8000 in use | Old server running | Kill via Task Manager or `netstat -ano` |
| `Model not found` (Groq) | Account tier | Switch to `DEFAULT_LLM_PROVIDER=gemini` |
| `EmailStr` validation error | `.local` domain | Use `@gmail.com` or `@hiringapp.com` |
| `npm: not recognized` | Node not on PATH | Restart terminal after Node install |
| React CORS error | API not running | Start uvicorn on port 8000 first |

---

## Resume Project Description (for your CV)

```
AI Hiring Co-Pilot | Personal Project | 2025–2026

Built a production-grade multi-agent AI recruitment platform using LangGraph
orchestrating 6 specialized AI agents (JD Analyzer, Resume Parser, Candidate
Matcher, Shortlisting, Interview Scheduler, Report Generator). Implemented
Human-in-the-Loop approval workflows with Redis checkpointing, JWT
authentication, RAG-based semantic candidate search using Pinecone vector
database, and real-time monitoring via LangSmith. Stack: Python, FastAPI,
LangGraph, LangChain, React 18 + TypeScript, Tailwind CSS, SQLite/MySQL,
Google Gemini API, Groq, ChromaDB.

GitHub: https://github.com/YOUR_USERNAME/ai-hiring-copilot
```
