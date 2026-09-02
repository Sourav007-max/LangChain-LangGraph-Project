"""
Database initialisation for SQLite (development).
Run once:  python -m database.init_db
Switches to MySQL/PostgreSQL in production by changing DATABASE_URL in .env.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from config.settings import DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency — yields a DB session and closes it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── SQLAlchemy models (ORM) ───────────────────────────────────────────────────
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float, ForeignKey, JSON
from datetime import datetime, timezone
from utils.crypto import hash_password


def _now():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"
    id            = Column(Integer, primary_key=True, autoincrement=True)
    email         = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name     = Column(String(255), nullable=False)
    role          = Column(String(50),  nullable=False, default="recruiter")
    is_active     = Column(Boolean, default=True)
    last_login    = Column(DateTime, nullable=True)
    created_at    = Column(DateTime, default=_now)


class Job(Base):
    __tablename__ = "jobs"
    id                = Column(Integer, primary_key=True, autoincrement=True)
    recruiter_id      = Column(Integer, ForeignKey("users.id"), nullable=False)
    title             = Column(String(255), nullable=False)
    department        = Column(String(100), nullable=True)
    location          = Column(String(255), nullable=True)
    job_type          = Column(String(50),  default="full_time")
    experience_level  = Column(String(50),  default="mid")
    salary_min        = Column(Float, nullable=True)
    salary_max        = Column(Float, nullable=True)
    description_raw   = Column(Text, nullable=False)
    description_parsed = Column(JSON, nullable=True)
    required_skills   = Column(JSON, nullable=True)
    min_experience_yrs = Column(Integer, nullable=True)
    status            = Column(String(50), default="active")
    deadline          = Column(String(20), nullable=True)
    created_at        = Column(DateTime, default=_now)
    updated_at        = Column(DateTime, default=_now, onupdate=_now)


class Candidate(Base):
    __tablename__ = "candidates"
    id           = Column(Integer, primary_key=True, autoincrement=True)
    email        = Column(String(255), unique=True, nullable=False)
    full_name    = Column(String(255), nullable=False)
    phone        = Column(String(30),  nullable=True)
    linkedin_url = Column(String(500), nullable=True)
    source       = Column(String(50),  default="direct")
    gdpr_consent = Column(Boolean, default=True)
    created_at   = Column(DateTime, default=_now)


class Resume(Base):
    __tablename__ = "resumes"
    id               = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id     = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    file_name        = Column(String(255), nullable=False)
    file_path        = Column(String(500), nullable=False)
    file_size_bytes  = Column(Integer, nullable=True)
    file_type        = Column(String(10), default="pdf")
    raw_text         = Column(Text, nullable=True)
    parsed_data      = Column(JSON, nullable=True)
    skills_extracted = Column(JSON, nullable=True)
    experience_years = Column(Float, nullable=True)
    current_title    = Column(String(255), nullable=True)
    embedding_id     = Column(String(100), nullable=True)
    parse_status     = Column(String(30), default="pending")
    parse_error      = Column(Text, nullable=True)
    uploaded_at      = Column(DateTime, default=_now)
    parsed_at        = Column(DateTime, nullable=True)


class Application(Base):
    __tablename__ = "applications"
    id               = Column(Integer, primary_key=True, autoincrement=True)
    job_id           = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    candidate_id     = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    resume_id        = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    status           = Column(String(50), default="applied")
    ai_score         = Column(Integer, nullable=True)
    ai_reasoning     = Column(Text, nullable=True)
    recruiter_notes  = Column(Text, nullable=True)
    applied_at       = Column(DateTime, default=_now)
    updated_at       = Column(DateTime, default=_now, onupdate=_now)


class AgentLog(Base):
    __tablename__ = "agent_logs"
    id               = Column(Integer, primary_key=True, autoincrement=True)
    session_id       = Column(String(100), nullable=False)
    agent_name       = Column(String(100), nullable=False)
    action_type      = Column(String(100), nullable=False)
    input_summary    = Column(Text, nullable=True)
    output_summary   = Column(Text, nullable=True)
    model_used       = Column(String(100), nullable=True)
    tokens_used      = Column(Integer, nullable=True)
    latency_ms       = Column(Integer, nullable=True)
    status           = Column(String(20), default="success")
    error_message    = Column(Text, nullable=True)
    entity_type      = Column(String(50), nullable=True)
    entity_id        = Column(Integer, nullable=True)
    created_at       = Column(DateTime, default=_now)


def init_db():
    """Create all tables and seed a demo admin user."""
    db_type = "MySQL" if "mysql" in DATABASE_URL else "SQLite"
    Base.metadata.create_all(bind=engine)
    print(f"All tables created in {db_type}")

    db = SessionLocal()
    try:
        # Skip seed if users already exist
        if db.query(User).count() > 0:
            print(" Seed data already present, skipping.")
            return

        users = [
            User(email="admin@hiringapp.com",     password_hash=hash_password("Admin@123"),     full_name="Admin User",     role="admin"),
            User(email="recruiter@hiringapp.com",  password_hash=hash_password("Admin@123"),     full_name="Sarah Recruiter", role="recruiter"),
            User(email="manager@hiringapp.com",    password_hash=hash_password("Admin@123"),     full_name="Mike Manager",   role="hiring_manager"),
        ]
        db.add_all(users)
        db.flush()

        job = Job(
            recruiter_id=users[1].id,
            title="Senior Python Developer",
            department="Engineering",
            location="Remote",
            description_raw=(
                "We need a Senior Python Developer with 5+ years experience. "
                "Requirements: Python, FastAPI, REST APIs, PostgreSQL or SQLite, Docker, AWS. "
                "Nice to have: LangChain, LangGraph, Redis."
            ),
            required_skills=["Python", "FastAPI", "Docker", "AWS"],
            min_experience_yrs=5,
            status="active",
        )
        db.add(job)
        db.commit()
        print("✅ Seed data inserted (3 users + 1 job)")
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
