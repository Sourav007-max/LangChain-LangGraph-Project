"""
AI Hiring Co-Pilot — FastAPI Backend
=====================================
Run:  uvicorn backend.main:app --reload --port 8000
Docs: http://localhost:8000/docs
"""

import os
import uuid
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
import jwt
import bcrypt as _bcrypt
from dotenv import load_dotenv

load_dotenv()

from database.init_db import init_db, get_db, User, Job, Candidate, Resume, Application, AgentLog
from agents.graph import run_workflow, resume_workflow, get_workflow_state
from config.settings import SECRET_KEY, CORS_ORIGINS, UPLOAD_DIR, MAX_FILE_SIZE_MB

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Auth helpers ──────────────────────────────────────────────────────────────
_bearer = HTTPBearer()
_JWT_ALG = "HS256"
_JWT_EXP = 60  # minutes


def _hash_pw(password: str) -> str:
    return _bcrypt.hashpw(password.encode(), _bcrypt.gensalt()).decode()


def _verify_pw(plain: str, hashed: str) -> bool:
    return _bcrypt.checkpw(plain.encode(), hashed.encode())


def _make_token(user_id: int, email: str, role: str) -> str:
    exp = datetime.now(timezone.utc) + timedelta(minutes=_JWT_EXP)
    return jwt.encode({"sub": str(user_id), "email": email, "role": role, "exp": exp},
                      SECRET_KEY, algorithm=_JWT_ALG)


def _decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[_JWT_ALG])
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Invalid token")


def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(_bearer),
    db: Session = Depends(get_db),
) -> dict:
    payload = _decode_token(creds.credentials)
    user = db.query(User).filter_by(id=int(payload["sub"]), is_active=True).first()
    if not user:
        raise HTTPException(401, "User not found or inactive")
    return {"id": user.id, "email": user.email, "role": user.role, "name": user.full_name}


def require_role(*roles: str):
    def checker(u: dict = Depends(get_current_user)):
        if u["role"] not in roles:
            raise HTTPException(403, f"Required role: {roles}")
        return u
    return checker


# ── Schemas ───────────────────────────────────────────────────────────────────
class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2)
    role: str = "recruiter"

class JobIn(BaseModel):
    title: str = Field(..., min_length=3)
    department: Optional[str] = None
    location: Optional[str] = None
    job_type: str = "full_time"
    experience_level: str = "mid"
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    description_raw: str = Field(..., min_length=30)
    min_experience_yrs: Optional[int] = None

class WorkflowStartIn(BaseModel):
    job_id: int
    resume_ids: list[int]

class HumanApproveIn(BaseModel):
    approved_candidates: list[dict]
    decision: str = "approve"
    feedback: Optional[str] = None


# ── App lifecycle ─────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    logger.info("✅ AI Hiring Co-Pilot API ready")
    yield


app = FastAPI(
    title="AI Hiring Co-Pilot",
    description="Multi-Agent Recruitment Platform using LangGraph",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health ─────────────────────────────────────────────────────────────────────
@app.get("/health", tags=["System"])
def health():
    return {"status": "ok", "ts": datetime.now().isoformat()}


# ── Auth ───────────────────────────────────────────────────────────────────────
@app.post("/api/v1/auth/register", tags=["Auth"])
def register(body: RegisterIn, db: Session = Depends(get_db)):
    if db.query(User).filter_by(email=body.email).first():
        raise HTTPException(409, "Email already registered")
    allowed = {"recruiter", "hiring_manager", "interviewer"}
    if body.role not in allowed:
        raise HTTPException(400, f"Role must be one of {allowed}")
    user = User(email=body.email, password_hash=_hash_pw(body.password),
                full_name=body.full_name, role=body.role)
    db.add(user); db.commit(); db.refresh(user)
    return {"access_token": _make_token(user.id, user.email, user.role),
            "token_type": "bearer", "user_id": user.id, "role": user.role}


@app.post("/api/v1/auth/login", tags=["Auth"])
def login(body: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(email=body.email).first()
    if not user or not _verify_pw(body.password, user.password_hash):
        raise HTTPException(401, "Invalid email or password")
    if not user.is_active:
        raise HTTPException(403, "Account deactivated")
    user.last_login = datetime.now(timezone.utc)
    db.commit()
    return {"access_token": _make_token(user.id, user.email, user.role),
            "token_type": "bearer", "user_id": user.id,
            "full_name": user.full_name, "role": user.role}


# ── Jobs ───────────────────────────────────────────────────────────────────────
@app.post("/api/v1/jobs", tags=["Jobs"])
def create_job(body: JobIn, u=Depends(require_role("recruiter", "admin")), db: Session = Depends(get_db)):
    job = Job(recruiter_id=u["id"], **body.model_dump())
    db.add(job); db.commit(); db.refresh(job)
    return {"job_id": job.id, "title": job.title}


@app.get("/api/v1/jobs", tags=["Jobs"])
def list_jobs(status: Optional[str] = None, _=Depends(get_current_user), db: Session = Depends(get_db)):
    q = db.query(Job)
    if status:
        q = q.filter_by(status=status)
    jobs = q.all()
    return {"jobs": [{"id": j.id, "title": j.title, "status": j.status,
                      "department": j.department, "location": j.location} for j in jobs]}


@app.get("/api/v1/jobs/{job_id}", tags=["Jobs"])
def get_job(job_id: int, _=Depends(get_current_user), db: Session = Depends(get_db)):
    job = db.query(Job).filter_by(id=job_id).first()
    if not job:
        raise HTTPException(404, "Job not found")
    return {"id": job.id, "title": job.title, "description_raw": job.description_raw,
            "required_skills": job.required_skills, "status": job.status}


# ── Resume upload ──────────────────────────────────────────────────────────────
@app.post("/api/v1/resumes/upload", tags=["Resumes"])
async def upload_resume(
    file: UploadFile = File(...),
    candidate_email: str = Form(...),
    candidate_name:  str = Form(...),
    u=Depends(require_role("recruiter", "admin")),
    db: Session = Depends(get_db),
):
    allowed_ct = {
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }
    if file.content_type not in allowed_ct:
        raise HTTPException(400, "Only PDF / DOCX accepted")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(413, f"File exceeds {MAX_FILE_SIZE_MB} MB")

    ext = (file.filename or "resume.pdf").rsplit(".", 1)[-1].lower()
    safe_name = f"{uuid.uuid4().hex}.{ext}"
    save_path = os.path.join(UPLOAD_DIR, safe_name)
    with open(save_path, "wb") as f:
        f.write(content)

    cand = db.query(Candidate).filter_by(email=candidate_email).first()
    if not cand:
        cand = Candidate(email=candidate_email, full_name=candidate_name)
        db.add(cand); db.flush()

    resume = Resume(candidate_id=cand.id, file_name=file.filename,
                    file_path=save_path, file_size_bytes=len(content), file_type=ext)
    db.add(resume); db.commit(); db.refresh(resume)
    return {"resume_id": resume.id, "candidate_id": cand.id, "status": "uploaded"}


# ── Workflow ───────────────────────────────────────────────────────────────────
@app.post("/api/v1/workflows/start", tags=["Workflow"])
def start_workflow(
    body: WorkflowStartIn,
    u=Depends(require_role("recruiter", "admin")),
    db: Session = Depends(get_db),
):
    job = db.query(Job).filter_by(id=body.job_id, status="active").first()
    if not job:
        raise HTTPException(404, "Active job not found")

    resume_texts, resume_metadata = [], []
    for rid in body.resume_ids:
        r = db.query(Resume).filter_by(id=rid).first()
        if not r or not os.path.exists(r.file_path):
            continue
        try:
            import pypdf
            reader = pypdf.PdfReader(r.file_path)
            text = " ".join(p.extract_text() or "" for p in reader.pages)
        except Exception:
            text = ""
        cand = db.query(Candidate).filter_by(id=r.candidate_id).first()
        resume_texts.append(text)
        resume_metadata.append({
            "file_name":       r.file_name,
            "candidate_email": cand.email if cand else "",
            "candidate_name":  cand.full_name if cand else "",
        })

    if not resume_texts:
        raise HTTPException(400, "No valid resumes found")

    thread_id = str(uuid.uuid4())
    initial_state = {
        "job_id": job.id, "job_description_raw": job.description_raw,
        "resume_texts": resume_texts, "resume_metadata": resume_metadata,
        "parsed_resumes": [], "candidate_scores": [],
        "shortlisted_candidates": [], "human_approved_candidates": [],
        "interview_schedule": [], "evaluations": [],
        "errors": [], "retry_count": 0, "messages": [],
        "current_agent": "start", "job_requirements": None,
        "human_decision": None, "human_feedback": None, "final_report": None,
    }

    state = run_workflow(thread_id, initial_state)
    shortlisted = state.get("shortlisted_candidates", [])
    return {
        "thread_id":    thread_id,
        "status":       "waiting_human_review" if shortlisted else "completed",
        "shortlisted":  shortlisted,
        "total_scored": len(state.get("candidate_scores", [])),
    }


@app.get("/api/v1/workflows/{thread_id}/state", tags=["Workflow"])
def workflow_state(thread_id: str, _=Depends(get_current_user)):
    state = get_workflow_state(thread_id)
    if not state:
        raise HTTPException(404, "Workflow not found")
    return {
        "thread_id": thread_id,
        "current_agent": state.get("current_agent"),
        "shortlisted":   state.get("shortlisted_candidates", []),
        "errors":        state.get("errors", []),
        "report_ready":  bool(state.get("final_report")),
    }


@app.post("/api/v1/workflows/{thread_id}/approve", tags=["Workflow"])
def approve_workflow(
    thread_id: str,
    body: HumanApproveIn,
    _=Depends(require_role("recruiter", "hiring_manager", "admin")),
):
    state = resume_workflow(
        thread_id,
        approved_candidates=body.approved_candidates,
        decision=body.decision,
        feedback=body.feedback or "",
    )
    return {
        "thread_id":  thread_id,
        "status":     "completed",
        "interviews": state.get("interview_schedule", []),
        "report":     state.get("final_report", ""),
    }


# ── Analytics ──────────────────────────────────────────────────────────────────
@app.get("/api/v1/analytics/dashboard", tags=["Analytics"])
def dashboard(_=Depends(get_current_user), db: Session = Depends(get_db)):
    return {
        "total_jobs":         db.query(Job).filter_by(status="active").count(),
        "total_candidates":   db.query(Candidate).count(),
        "total_applications": db.query(Application).count(),
        "generated_at":       datetime.now().isoformat(),
    }


# ── Monitoring ─────────────────────────────────────────────────────────────────
@app.get("/api/v1/monitoring/stats", tags=["Monitoring"])
def monitoring_stats(_=Depends(require_role("admin", "recruiter", "hiring_manager"))):
    """Per-agent performance: run count, error rate, avg latency."""
    from config.monitoring import get_agent_stats
    return get_agent_stats()


@app.get("/api/v1/monitoring/logs", tags=["Monitoring"])
def monitoring_logs(limit: int = 20, _=Depends(require_role("admin", "recruiter", "hiring_manager"))):
    """Live tail of recent agent executions."""
    from config.monitoring import get_recent_logs
    return {"logs": get_recent_logs(limit=limit), "generated_at": datetime.now().isoformat()}
