"""
Phase 11A — Streamlit Dashboard
================================
Complete prototype UI for the AI Hiring Co-Pilot.

Run (with venv active):
    streamlit run frontend/streamlit_app.py

What this teaches:
  - Streamlit session state (replaces React useState)
  - API integration from a frontend
  - Multi-page navigation
  - File upload → backend pipeline → results display
  - Human-in-the-loop approval UI
"""

import streamlit as st
import httpx
import json
import os
from datetime import datetime

# ── Config ─────────────────────────────────────────────────────────────────
API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(
    page_title="AI Hiring Co-Pilot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Shared API client ───────────────────────────────────────────────────────
def api(method: str, path: str, **kwargs) -> httpx.Response:
    """Authenticated API call using token stored in session state."""
    headers = kwargs.pop("headers", {})
    if st.session_state.get("token"):
        headers["Authorization"] = f"Bearer {st.session_state.token}"
    try:
        return httpx.request(method, f"{API_BASE}{path}", headers=headers,
                             timeout=120, **kwargs)
    except httpx.ConnectError:
        st.error("⚠️ Cannot reach API server. Make sure it is running on port 8000.")
        st.stop()


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: LOGIN
# ═══════════════════════════════════════════════════════════════════════════
def page_login():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("## 🤖 AI Hiring Co-Pilot")
        st.markdown("*Multi-Agent Recruitment Platform*")
        st.divider()

        with st.form("login_form"):
            email = st.text_input("Email", value="recruiter@hiringapp.com")
            password = st.text_input("Password", type="password", value="Admin@123")
            submitted = st.form_submit_button("Login", use_container_width=True)

        if submitted:
            r = api("POST", "/api/v1/auth/login",
                    json={"email": email, "password": password})
            if r.status_code == 200:
                data = r.json()
                st.session_state.token     = data["access_token"]
                st.session_state.user_role = data["role"]
                st.session_state.user_name = data["full_name"]
                st.session_state.page      = "dashboard"
                st.rerun()
            else:
                st.error(f"Login failed: {r.json().get('detail', 'Unknown error')}")

        st.caption("Demo credentials: recruiter@hiringapp.com / Admin@123")


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════
def page_dashboard():
    st.markdown("## 📊 Recruitment Dashboard")

    r = api("GET", "/api/v1/analytics/dashboard")
    if r.status_code != 200:
        st.error("Could not load dashboard data")
        return

    data = r.json()

    # ── KPI Cards ────────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Active Jobs",        data.get("total_jobs", 0))
    col2.metric("Total Candidates",   data.get("total_candidates", 0))
    col3.metric("Applications",       data.get("total_applications", 0))
    col4.metric("Last Updated",       datetime.now().strftime("%H:%M"))

    st.divider()

    # ── Pipeline funnel ───────────────────────────────────────────────────
    st.markdown("### 🔄 Hiring Pipeline")

    # Fetch jobs to show pipeline per job
    jobs_r = api("GET", "/api/v1/jobs")
    if jobs_r.status_code == 200:
        jobs = jobs_r.json().get("jobs", [])
        if jobs:
            for job in jobs[:5]:
                with st.expander(f"**{job['title']}** — {job.get('location', 'Remote')} — `{job['status']}`"):
                    c1, c2, c3 = st.columns(3)
                    c1.write(f"**Department:** {job.get('department', 'N/A')}")
                    c2.write(f"**Status:** {job['status']}")
                    if st.button("View Applications", key=f"view_{job['id']}"):
                        st.session_state.selected_job_id = job["id"]
                        st.session_state.page = "workflow"
                        st.rerun()
        else:
            st.info("No active jobs. Create one in the Jobs page.")

    # ── Active workflows waiting for human review ─────────────────────────
    if st.session_state.get("pending_workflows"):
        st.divider()
        st.markdown("### ⏸ Workflows Awaiting Your Review")
        for wf in st.session_state.pending_workflows:
            with st.container(border=True):
                st.warning(f"**Thread:** `{wf['thread_id'][:16]}...` | "
                           f"**Shortlisted:** {wf['shortlisted_count']} candidates")
                if st.button("Review Now", key=f"review_{wf['thread_id']}"):
                    st.session_state.review_thread_id = wf["thread_id"]
                    st.session_state.review_shortlist  = wf["shortlisted"]
                    st.session_state.page = "review"
                    st.rerun()


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: JOBS
# ═══════════════════════════════════════════════════════════════════════════
def page_jobs():
    st.markdown("## 💼 Job Management")

    tab_list, tab_create = st.tabs(["Active Jobs", "➕ Create New Job"])

    # ── List jobs ─────────────────────────────────────────────────────────
    with tab_list:
        r = api("GET", "/api/v1/jobs")
        if r.status_code == 200:
            jobs = r.json().get("jobs", [])
            if jobs:
                for job in jobs:
                    with st.container(border=True):
                        c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
                        c1.markdown(f"**{job['title']}**")
                        c2.write(job.get("department", "—"))
                        c3.write(job.get("location", "Remote"))
                        c4.write(f"`{job['status']}`")
            else:
                st.info("No jobs yet. Create one below.")

    # ── Create job ────────────────────────────────────────────────────────
    with tab_create:
        with st.form("create_job_form"):
            title = st.text_input("Job Title *", placeholder="Senior Python Developer")
            col1, col2 = st.columns(2)
            department = col1.text_input("Department", placeholder="Engineering")
            location   = col2.text_input("Location", placeholder="Remote (US)")
            col3, col4 = st.columns(2)
            job_type = col3.selectbox("Type", ["full_time", "part_time", "contract", "internship"])
            exp_level = col4.selectbox("Level", ["junior", "mid", "senior", "lead"])
            col5, col6 = st.columns(2)
            sal_min = col5.number_input("Salary Min ($)", min_value=0, value=80000, step=5000)
            sal_max = col6.number_input("Salary Max ($)", min_value=0, value=130000, step=5000)
            min_exp = st.number_input("Minimum Years Experience", min_value=0, max_value=20, value=3)
            description = st.text_area(
                "Job Description *",
                height=200,
                placeholder="Describe the role, requirements, responsibilities...",
            )
            submitted = st.form_submit_button("Create Job", use_container_width=True)

        if submitted:
            if not title or not description:
                st.error("Title and Description are required.")
            else:
                r = api("POST", "/api/v1/jobs", json={
                    "title": title, "department": department, "location": location,
                    "job_type": job_type, "experience_level": exp_level,
                    "salary_min": sal_min, "salary_max": sal_max,
                    "description_raw": description, "min_experience_yrs": min_exp,
                })
                if r.status_code == 200:
                    st.success(f"✅ Job created! ID: {r.json()['job_id']}")
                    st.balloons()
                else:
                    st.error(f"Error: {r.json()}")


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: WORKFLOW — Upload resumes + trigger AI pipeline
# ═══════════════════════════════════════════════════════════════════════════
def page_workflow():
    st.markdown("## 🚀 Run AI Screening Workflow")

    # ── Step 1: Select job ────────────────────────────────────────────────
    st.markdown("### Step 1 — Select Job")
    jobs_r = api("GET", "/api/v1/jobs?status=active")
    jobs   = jobs_r.json().get("jobs", []) if jobs_r.status_code == 200 else []

    if not jobs:
        st.warning("No active jobs found. Create one in the Jobs page first.")
        return

    job_map = {f"{j['title']} (ID: {j['id']})": j["id"] for j in jobs}
    selected_job_label = st.selectbox("Choose a job", list(job_map.keys()))
    job_id = job_map[selected_job_label]

    # ── Step 2: Upload resumes ────────────────────────────────────────────
    st.markdown("### Step 2 — Upload Candidate Resumes")

    col1, col2 = st.columns(2)
    cand_name  = col1.text_input("Candidate Full Name")
    cand_email = col2.text_input("Candidate Email")
    uploaded_file = st.file_uploader(
        "Upload Resume (PDF or DOCX)", type=["pdf", "docx"],
        help="Max 10 MB per file"
    )

    if st.button("📤 Upload Resume") and uploaded_file:
        if not cand_name or not cand_email:
            st.error("Please enter candidate name and email.")
        else:
            files   = {"file": (uploaded_file.name, uploaded_file.getvalue(),
                                uploaded_file.type or "application/pdf")}
            data    = {"candidate_email": cand_email, "candidate_name": cand_name}
            headers = {"Authorization": f"Bearer {st.session_state.token}"}
            r = httpx.post(f"{API_BASE}/api/v1/resumes/upload",
                           files=files, data=data, headers=headers, timeout=30)
            if r.status_code == 200:
                resp = r.json()
                if "uploaded_resumes" not in st.session_state:
                    st.session_state.uploaded_resumes = []
                st.session_state.uploaded_resumes.append({
                    "resume_id": resp["resume_id"],
                    "name": cand_name,
                    "email": cand_email,
                })
                st.success(f"✅ Resume uploaded for {cand_name} (ID: {resp['resume_id']})")
            else:
                st.error(f"Upload failed: {r.json()}")

    # Show uploaded list
    if st.session_state.get("uploaded_resumes"):
        st.markdown("**Queued for screening:**")
        for r in st.session_state.uploaded_resumes:
            st.write(f"  • {r['name']} — {r['email']} (resume #{r['resume_id']})")

    # ── Step 3: Launch AI workflow ────────────────────────────────────────
    st.markdown("### Step 3 — Launch AI Screening")

    if st.button("🤖 Start AI Screening Workflow", use_container_width=True, type="primary"):
        queued = st.session_state.get("uploaded_resumes", [])
        if not queued:
            st.error("Upload at least one resume first.")
        else:
            with st.spinner("🧠 AI agents are working... (JD Analyzer → Resume Parser → Matcher → Shortlisting)"):
                resume_ids = [r["resume_id"] for r in queued]
                r = api("POST", "/api/v1/workflows/start",
                        json={"job_id": job_id, "resume_ids": resume_ids})

            if r.status_code == 200:
                result = r.json()
                thread_id   = result["thread_id"]
                shortlisted = result.get("shortlisted", [])
                st.success(f"✅ Workflow complete! Scored: {result.get('total_scored', 0)} candidates")

                if shortlisted:
                    st.info(f"⏸ **{len(shortlisted)} candidates shortlisted — your review is needed!**")
                    # Store for review page
                    pending = st.session_state.get("pending_workflows", [])
                    pending.append({
                        "thread_id":       thread_id,
                        "shortlisted":     shortlisted,
                        "shortlisted_count": len(shortlisted),
                    })
                    st.session_state.pending_workflows = pending
                    st.session_state.review_thread_id  = thread_id
                    st.session_state.review_shortlist   = shortlisted
                    st.session_state.uploaded_resumes   = []

                    if st.button("👉 Go to Review", type="primary"):
                        st.session_state.page = "review"
                        st.rerun()
                else:
                    st.warning("No candidates met the minimum score threshold.")
            else:
                st.error(f"Workflow failed: {r.json()}")


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: HUMAN-IN-THE-LOOP REVIEW
# ═══════════════════════════════════════════════════════════════════════════
def page_review():
    """
    LESSON: This is the Human-in-the-Loop checkpoint.
    The LangGraph workflow is PAUSED here.
    The recruiter reviews AI recommendations, modifies if needed, then resumes.
    This implements the interrupt() → update_state() → resume pattern.
    """
    st.markdown("## 🔍 Human Review — AI Shortlist")

    thread_id  = st.session_state.get("review_thread_id")
    shortlisted = st.session_state.get("review_shortlist", [])

    if not thread_id or not shortlisted:
        st.info("No pending reviews. Run a workflow first.")
        return

    st.info(f"**Thread:** `{thread_id}` | **AI shortlisted {len(shortlisted)} candidates** — review and approve below.")

    # ── Score breakdown ───────────────────────────────────────────────────
    st.markdown("### Candidate Scores")
    for c in shortlisted:
        score = c.get("score", 0)
        color = "🟢" if score >= 80 else ("🟡" if score >= 65 else "🔴")
        rec   = c.get("recommendation", "")
        with st.expander(f"{color} **{c.get('candidate_name', 'Unknown')}** — Score: {score}/100 — {rec}"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Strengths:**")
                for s in c.get("strengths", []):
                    st.write(f"  ✅ {s}")
            with col2:
                st.markdown("**Gaps:**")
                for g in c.get("gaps", []):
                    st.write(f"  ⚠️ {g}")
            st.markdown(f"**AI Reasoning:** {c.get('reasoning', 'N/A')}")
            st.progress(score / 100)

    st.divider()

    # ── Approve/Reject ────────────────────────────────────────────────────
    st.markdown("### Your Decision")
    feedback = st.text_area("Feedback / Notes (optional)",
                            placeholder="Top 2 candidates look great. Reject C3 — too junior.")

    approved_names = st.multiselect(
        "Select candidates to approve for interviews",
        options=[c.get("candidate_name", f"Candidate {i}") for i, c in enumerate(shortlisted)],
        default=[c.get("candidate_name") for c in shortlisted if c.get("score", 0) >= 75],
    )

    col1, col2 = st.columns(2)

    if col1.button("✅ Approve & Schedule Interviews", type="primary", use_container_width=True):
        approved = [c for c in shortlisted if c.get("candidate_name") in approved_names]
        with st.spinner("📅 AI is scheduling interviews and generating questions..."):
            r = api("POST", f"/api/v1/workflows/{thread_id}/approve", json={
                "approved_candidates": approved,
                "decision": "approve",
                "feedback": feedback,
            })
        if r.status_code == 200:
            result = r.json()
            st.success("✅ Interviews scheduled!")
            st.session_state.last_interviews = result.get("interviews", [])
            st.session_state.last_report     = result.get("report", "")
            # Remove from pending
            st.session_state.pending_workflows = [
                w for w in st.session_state.get("pending_workflows", [])
                if w["thread_id"] != thread_id
            ]
            st.session_state.review_thread_id = None
            st.session_state.page = "interviews"
            st.rerun()
        else:
            st.error(f"Error: {r.json()}")

    if col2.button("❌ Reject All", use_container_width=True):
        with st.spinner("Closing workflow..."):
            r = api("POST", f"/api/v1/workflows/{thread_id}/approve", json={
                "approved_candidates": [],
                "decision": "reject_all",
                "feedback": feedback or "All candidates rejected.",
            })
        if r.status_code == 200:
            st.info("Workflow closed. No interviews scheduled.")
            st.session_state.review_thread_id = None
            st.session_state.page = "dashboard"
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: INTERVIEWS
# ═══════════════════════════════════════════════════════════════════════════
def page_interviews():
    st.markdown("## 📅 Interview Schedule")

    interviews = st.session_state.get("last_interviews", [])

    if not interviews:
        st.info("No interviews scheduled yet. Complete a screening workflow first.")
        return

    st.success(f"✅ {len(interviews)} interview(s) scheduled")

    for i, interview in enumerate(interviews, 1):
        with st.container(border=True):
            col1, col2, col3 = st.columns([2, 1, 1])
            col1.markdown(f"**{i}. {interview.get('candidate_name', 'N/A')}**")
            col2.write(f"📅 {interview.get('interview_date', 'TBD')}")
            col3.write(f"⏰ {interview.get('interview_time', 'TBD')}")

            if interview.get("meeting_link"):
                st.markdown(f"🔗 Meeting: `{interview['meeting_link']}`")

            if interview.get("email_sent"):
                st.caption("📧 Email invitation sent")
            else:
                st.caption("📧 Email not sent (SMTP disabled — configure SMTP_ENABLED=true)")

            questions = interview.get("ai_questions", [])
            if questions:
                with st.expander("🧠 AI-Generated Interview Questions"):
                    for j, q in enumerate(questions, 1):
                        st.write(f"**Q{j}.** {q}")

    # ── Final report ──────────────────────────────────────────────────────
    report = st.session_state.get("last_report", "")
    if report:
        st.divider()
        st.markdown("## 📄 AI Hiring Report")
        st.markdown(report)
        st.download_button(
            "⬇️ Download Report",
            data=report,
            file_name=f"hiring_report_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
            mime="text/markdown",
        )


# ═══════════════════════════════════════════════════════════════════════════
# SIDEBAR + ROUTING
# ═══════════════════════════════════════════════════════════════════════════
def sidebar():
    with st.sidebar:
        st.markdown("### 🤖 AI Hiring Co-Pilot")
        if st.session_state.get("user_name"):
            st.caption(f"👤 {st.session_state.user_name} ({st.session_state.user_role})")
        st.divider()

        pages = {
            "dashboard":   "📊 Dashboard",
            "jobs":        "💼 Jobs",
            "workflow":    "🚀 Run Screening",
            "review":      "🔍 Review Shortlist",
            "interviews":  "📅 Interviews",
        }

        for key, label in pages.items():
            badge = ""
            if key == "review" and st.session_state.get("pending_workflows"):
                badge = f" 🔴 {len(st.session_state.pending_workflows)}"
            if st.button(f"{label}{badge}", key=f"nav_{key}", use_container_width=True):
                st.session_state.page = key
                st.rerun()

        st.divider()

        with st.expander("📡 API Status"):
            try:
                r = httpx.get(f"{API_BASE}/health", timeout=3)
                st.success(f"API online ✅")
            except Exception:
                st.error("API offline ❌")

        if st.button("🚪 Logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════
# MAIN ROUTER
# ═══════════════════════════════════════════════════════════════════════════
def main():
    # Initialise session defaults
    defaults = {
        "page": "login", "token": None, "user_role": None,
        "user_name": None, "uploaded_resumes": [],
        "pending_workflows": [], "last_interviews": [], "last_report": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    if not st.session_state.token:
        page_login()
        return

    sidebar()

    page = st.session_state.page
    if page == "dashboard":   page_dashboard()
    elif page == "jobs":      page_jobs()
    elif page == "workflow":  page_workflow()
    elif page == "review":    page_review()
    elif page == "interviews": page_interviews()
    else:
        page_dashboard()


if __name__ == "__main__":
    main()
