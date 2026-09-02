# AI Hiring Co-Pilot

A recruiter-focused AI hiring platform that helps teams screen resumes, rank candidates, review shortlist decisions, and generate interview-ready outputs from a single workflow.

## Overview

AI Hiring Co-Pilot is a minimal but practical hiring workflow built for real-world recruitment operations. It combines a FastAPI backend, a React frontend, and a LangGraph multi-agent pipeline to automate the early stages of hiring: role analysis, resume extraction, candidate scoring, shortlist review, and interview preparation.

The goal is simple: reduce manual screening work while keeping the recruiter in control of the final decision.

## What the application does

- Creates and manages job openings
- Accepts resume uploads in PDF and DOCX format
- Extracts structured resume information
- Evaluates candidates against job requirements
- Builds and ranks a shortlist
- Allows recruiter approval or rejection before finalizing
- Generates interview questions and summary outputs
- Stores workflow data in a database for persistence

## Primary workflow

1. Recruiter logs in
2. Creates or selects a job
3. Uploads candidate resumes
4. AI analyzes the role and resumes
5. Candidates are scored and ranked
6. Recruiter reviews the shortlist
7. Approved candidates move to interview preparation

## Architecture

```text
React Frontend
    |
    v
FastAPI Backend
    |
    v
LangGraph Multi-Agent Workflow
    +-- JD Analyzer
    +-- Resume Parser
    +-- Candidate Matcher
    +-- Shortlisting
    +-- Human Review
    +-- Interview Scheduler
    +-- Report Generator
    |
    v
MySQL / SQLite Database
```

## Tech stack

- Frontend: React, TypeScript, Vite, Tailwind CSS, Zustand
- Backend: FastAPI, SQLAlchemy, JWT authentication
- AI orchestration: LangGraph, LangChain
- Models: Google Gemini, Groq, OpenAI-compatible providers
- Database: MySQL-ready, SQLite for local development
- Persistence: SQLAlchemy ORM

## Project structure

```text
LangChain-LangGraph-Project/
├── agents/
│   ├── graph.py
│   ├── jd_analyzer.py
│   ├── resume_parser.py
│   ├── candidate_matcher.py
│   ├── shortlisting.py
│   ├── interview_scheduler.py
│   ├── reporter.py
│   └── state.py
├── backend/
│   └── main.py
├── config/
│   ├── settings.py
│   └── monitoring.py
├── database/
│   └── init_db.py
├── frontend/
│   ├── src/
│   └── package.json
├── tests/
│   └── test_e2e_workflow.py
├── .env
├── .gitignore
├── requirements.txt
├── pytest.ini
├── README.md
```

## Features

### Recruiter workflow
- Create hiring jobs with structured requirements
- Upload multiple resumes
- Review AI-generated candidate rankings
- Approve or reject shortlisted candidates
- Generate interview questions and candidate summaries

### AI pipeline
- Parses job descriptions into role requirements
- Extracts resume text from PDF and DOCX files
- Matches candidate experience to role requirements
- Scores and ranks applicants
- Produces recruiter-ready report output

### Application quality
- JWT-based authentication
- database initialization and seed data
- API validation and error handling
- frontend route protection
- clean project separation between app logic, AI logic, and UI

## Demo credentials

```text
Email: recruiter@hiringapp.com
Password: Admin@123
```

## Prerequisites

- Python 3.11+
- Node.js 18+
- MySQL or SQLite
- Git

## Quick start

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd LangChain-LangGraph-Project
```

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Mac/Linux:

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install backend dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create or update `.env` with your database and AI settings.

For local development, the project supports SQLite by default. MySQL is also supported and configured via `DATABASE_URL`.

Example:

SECRET_KEY=your-secret-key
DEFAULT_LLM_PROVIDER=gemini
GOOGLE_API_KEY=your-google-key
```

### 5. Initialize the database

```bash
python -m database.init_db
```

### 6. Start the backend

```bash
uvicorn backend.main:app --reload --port 8000
```

### 7. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

Then open:

```text
http://localhost:5173
```

## Testing

```bash
pytest tests/ -q
```

The project includes workflow-focused tests for routing, scoring, and configuration logic.

## Operational status

This project is currently structured as a working prototype / MVP for AI-assisted recruitment. It is designed to be operational, understandable, and easy to extend, while remaining focused on the core recruiting workflow rather than broad product complexity.

## Known considerations

- API keys are intentionally kept outside the repo and managed with environment variables.
- MySQL is supported and validated for production-style persistence.
- The code is intended to remain minimal and recruiter-oriented rather than feature-heavy for the sake of it.

## Why this project matters

Hiring teams spend significant time reviewing CVs, screening applicants, and comparing candidates against role requirements. This project reduces that overhead by automating the repetitive early-stage screening work while leaving final decision-making with the recruiter.

## License

This project is provided as a learning and portfolio project for operational use and demonstration.

## Contact

For project discussions, collaboration, or hiring-related questions, connect through the repository owner profile or project contact details.