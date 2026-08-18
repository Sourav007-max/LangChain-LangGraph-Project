"""
Phase 13 — Integration Tests
==============================
Tests the LIVE system: API server must be running on port 8000.

Run ALL integration tests:
    pytest tests/test_integration.py -v -m integration

Run a single test:
    pytest tests/test_integration.py::test_full_hiring_pipeline -v -m integration

LESSON — Integration vs Unit tests:
  Unit tests  → mock everything, test one function in isolation (fast, no network)
  Integration → test real API + real DB + real LLM (slower, catches real bugs)

  Both are required. Unit tests catch logic bugs.
  Integration tests catch wiring bugs (e.g. wrong API endpoint, DB not seeded).
"""

import pytest
import httpx
import os
import tempfile
import io

BASE = os.getenv("API_BASE_URL", "http://localhost:8000")


# ─────────────────────────────────────────────────────────────────────────────
# FIXTURES — shared setup for all tests
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def client():
    """One httpx client reused across all tests in this session."""
    return httpx.Client(base_url=BASE, timeout=180)


@pytest.fixture(scope="session")
def auth_token(client):
    """Login once, reuse the token for all tests."""
    r = client.post("/api/v1/auth/login",
                    json={"email": "recruiter@hiringapp.com", "password": "Admin@123"})
    assert r.status_code == 200, f"Login failed: {r.json()}"
    return r.json()["access_token"]


@pytest.fixture(scope="session")
def headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture(scope="session")
def sample_resume_pdf() -> bytes:
    """
    Generate a minimal PDF in memory — no file on disk needed.
    Uses reportlab if available, otherwise creates a plain text file.
    """
    try:
        from reportlab.pdfgen import canvas
        buf = io.BytesIO()
        c = canvas.Canvas(buf)
        c.setFont("Helvetica", 11)
        lines = [
            "Alice Johnson  |  alice.johnson@example.com  |  +1-555-0199",
            "",
            "EXPERIENCE",
            "Senior Python Engineer | CloudTech Inc. | 2019-2025",
            "  - Built FastAPI microservices deployed on AWS ECS",
            "  - Led backend team of 6 engineers",
            "  - Implemented CI/CD pipelines with Docker and GitHub Actions",
            "",
            "Software Engineer | WebStartup | 2017-2019",
            "  - Python Django REST API development",
            "  - PostgreSQL database optimisation",
            "",
            "SKILLS",
            "Python, FastAPI, Django, Docker, AWS, PostgreSQL, Redis, Git, LangChain",
            "",
            "EDUCATION",
            "B.Sc. Computer Science | Tech University | 2017",
        ]
        y = 750
        for line in lines:
            c.drawString(50, y, line)
            y -= 18
        c.save()
        return buf.getvalue()
    except ImportError:
        # fallback: plain text file (accepted as text/plain by the test)
        return b"Alice Johnson  alice.johnson@example.com\nSKILLS: Python FastAPI Docker AWS"


# ─────────────────────────────────────────────────────────────────────────────
# TEST GROUP 1 — API Health & Auth
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.integration
def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


@pytest.mark.integration
def test_login_success(client):
    r = client.post("/api/v1/auth/login",
                    json={"email": "recruiter@hiringapp.com", "password": "Admin@123"})
    assert r.status_code == 200
    assert "access_token" in r.json()
    assert r.json()["role"] == "recruiter"


@pytest.mark.integration
def test_login_wrong_password(client):
    r = client.post("/api/v1/auth/login",
                    json={"email": "recruiter@hiringapp.com", "password": "wrongpassword"})
    assert r.status_code == 401


@pytest.mark.integration
def test_protected_route_without_token(client):
    r = client.get("/api/v1/jobs")
    assert r.status_code in (401, 403)  # HTTPBearer returns 401 or 403 depending on version


# ─────────────────────────────────────────────────────────────────────────────
# TEST GROUP 2 — Jobs CRUD
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.integration
def test_list_jobs(client, headers):
    r = client.get("/api/v1/jobs", headers=headers)
    assert r.status_code == 200
    assert "jobs" in r.json()


@pytest.mark.integration
def test_create_and_get_job(client, headers):
    payload = {
        "title":            "Integration Test Job — Python Engineer",
        "department":       "Engineering",
        "location":         "Remote",
        "job_type":         "full_time",
        "experience_level": "senior",
        "description_raw":  (
            "We need a Python engineer with FastAPI, Docker, and AWS experience. "
            "5+ years required. Nice to have: LangChain, Redis, Kubernetes."
        ),
        "min_experience_yrs": 5,
    }
    create_r = client.post("/api/v1/jobs", json=payload, headers=headers)
    assert create_r.status_code == 200
    job_id = create_r.json()["job_id"]

    get_r = client.get(f"/api/v1/jobs/{job_id}", headers=headers)
    assert get_r.status_code == 200
    assert get_r.json()["title"] == payload["title"]


# ─────────────────────────────────────────────────────────────────────────────
# TEST GROUP 3 — Resume Upload
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.integration
def test_resume_upload(client, headers, sample_resume_pdf):
    files  = {"file": ("alice_johnson.pdf", sample_resume_pdf, "application/pdf")}
    data   = {"candidate_email": "alice.test@example.com", "candidate_name": "Alice Johnson"}
    r = client.post("/api/v1/resumes/upload", files=files, data=data, headers=headers)
    assert r.status_code == 200
    assert "resume_id" in r.json()
    assert r.json()["status"] == "uploaded"


@pytest.mark.integration
def test_resume_upload_wrong_type(client, headers):
    """System must reject non-PDF files."""
    files = {"file": ("hack.exe", b"MZ\x00\x00", "application/octet-stream")}
    data  = {"candidate_email": "bad@example.com", "candidate_name": "Bad Actor"}
    r = client.post("/api/v1/resumes/upload", files=files, data=data, headers=headers)
    assert r.status_code == 400


# ─────────────────────────────────────────────────────────────────────────────
# TEST GROUP 4 — Analytics
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.integration
def test_dashboard(client, headers):
    r = client.get("/api/v1/analytics/dashboard", headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert "total_jobs" in data
    assert "total_candidates" in data


# ─────────────────────────────────────────────────────────────────────────────
# TEST GROUP 5 — Monitoring
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.integration
def test_monitoring_stats(client, headers):
    r = client.get("/api/v1/monitoring/stats", headers=headers)
    assert r.status_code == 200
    assert "agents" in r.json()


@pytest.mark.integration
def test_monitoring_logs(client, headers):
    r = client.get("/api/v1/monitoring/logs?limit=5", headers=headers)
    assert r.status_code == 200
    assert "logs" in r.json()


# ─────────────────────────────────────────────────────────────────────────────
# TEST GROUP 6 — Full AI Pipeline (requires GROQ_API_KEY)
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.integration
@pytest.mark.slow
def test_full_hiring_pipeline(client, headers, sample_resume_pdf):
    """
    End-to-end test:
    1. Create job
    2. Upload resume
    3. Start AI workflow → agents run → shortlist produced
    4. Approve shortlist → interviews scheduled → report generated

    Skipped automatically if GROQ_API_KEY is not set.
    """
    if not os.getenv("GROQ_API_KEY"):
        pytest.skip("GROQ_API_KEY not set — skipping live AI test")

    # ── Step 1: Create a job ──────────────────────────────────────────────
    job_r = client.post("/api/v1/jobs", headers=headers, json={
        "title":            "E2E Test — Senior Python Developer",
        "description_raw":  (
            "5+ years Python, FastAPI, Docker, AWS required. "
            "LangChain/LangGraph experience a plus."
        ),
        "min_experience_yrs": 4,
    })
    assert job_r.status_code == 200
    job_id = job_r.json()["job_id"]

    # ── Step 2: Upload resume ─────────────────────────────────────────────
    upload_r = client.post(
        "/api/v1/resumes/upload",
        files={"file": ("alice.pdf", sample_resume_pdf, "application/pdf")},
        data={"candidate_email": f"alice.e2e@example.com", "candidate_name": "Alice Johnson"},
        headers=headers,
    )
    assert upload_r.status_code == 200
    resume_id = upload_r.json()["resume_id"]

    # ── Step 3: Start workflow ────────────────────────────────────────────
    workflow_r = client.post("/api/v1/workflows/start", headers=headers,
                             json={"job_id": job_id, "resume_ids": [resume_id]})
    assert workflow_r.status_code == 200

    result     = workflow_r.json()
    thread_id  = result["thread_id"]
    shortlisted = result.get("shortlisted", [])

    assert result["total_scored"] >= 1, "At least one candidate should be scored"

    if not shortlisted:
        pytest.skip("No candidates met the threshold — check SHORTLIST_MIN_SCORE env var")

    # ── Step 4: Human approves top candidate ──────────────────────────────
    approve_r = client.post(
        f"/api/v1/workflows/{thread_id}/approve",
        headers=headers,
        json={
            "approved_candidates": shortlisted[:1],
            "decision": "approve",
            "feedback": "Integration test approval",
        },
    )
    assert approve_r.status_code == 200

    final = approve_r.json()
    assert final["status"] == "completed"
    assert len(final.get("interviews", [])) > 0, "Interview should be scheduled"
    assert final.get("report"), "Final report should be generated"

    print(f"\n✅ E2E test passed!")
    print(f"   Thread:      {thread_id}")
    print(f"   Candidates:  {result['total_scored']} scored, {len(shortlisted)} shortlisted")
    print(f"   Interviews:  {len(final['interviews'])} scheduled")
    print(f"   Report:      {len(final['report'])} chars")
