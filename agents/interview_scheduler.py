"""
Interview Scheduler Agent
--------------------------
Input  : state["human_approved_candidates"], state["job_requirements"]
Output : state["interview_schedule"]

SMTP is disabled for now (SMTP_ENABLED=false in .env).
When enabled, each candidate receives a personalised email invitation.
"""

import os
import json
import uuid
from datetime import datetime, timedelta, timezone
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from config.settings import get_llm, SMTP_ENABLED
from agents.state import HiringState

_Q_PROMPT = ChatPromptTemplate.from_template("""
Generate exactly 5 targeted technical interview questions for this candidate
based on the job requirements. Focus on their skill gaps and experience depth.
Return ONLY a JSON array of 5 question strings.

Candidate: {candidate}
Job Requirements: {requirements}
""")


def _generate_questions(candidate: dict, requirements: dict) -> list[str]:
    llm = get_llm(temperature=0.3)
    chain = _Q_PROMPT | llm | JsonOutputParser()
    try:
        return chain.invoke({
            "candidate":    json.dumps(candidate),
            "requirements": json.dumps(requirements),
        })
    except Exception:
        return [
            "Walk me through your most complex Python project.",
            "How do you ensure code quality in a fast-moving team?",
            "Describe your experience with cloud deployment.",
            "How do you handle production incidents?",
            "What recent technology have you taught yourself?",
        ]


def _send_email_stub(candidate: dict, schedule_entry: dict):
    """Placeholder — replace with real SMTP logic when SMTP_ENABLED=true."""
    print(
        f"  [Scheduler]   📧 (stub) invite → {candidate.get('candidate_email')} "
        f"on {schedule_entry['interview_date']}"
    )


def interview_scheduler_node(state: HiringState) -> dict:
    approved   = state.get("human_approved_candidates", [])
    reqs       = state.get("job_requirements", {})
    base_date  = datetime.now(timezone.utc) + timedelta(days=3)
    schedule   = []

    for i, candidate in enumerate(approved):
        interview_date = (base_date + timedelta(days=i * 2)).strftime("%Y-%m-%d")
        questions      = _generate_questions(candidate, reqs)
        entry = {
            "candidate_name":  candidate.get("candidate_name", "Unknown"),
            "candidate_email": candidate.get("candidate_email", ""),
            "interview_date":  interview_date,
            "interview_time":  "10:00 AM UTC",
            "meeting_link":    f"https://meet.example.com/{uuid.uuid4().hex[:8]}",
            "interview_type":  "technical",
            "ai_questions":    questions,
            "email_sent":      False,
        }

        if SMTP_ENABLED:
            _send_email_stub(candidate, entry)
            entry["email_sent"] = True

        schedule.append(entry)
        print(f"  [Scheduler] ✅ {entry['candidate_name']} → {interview_date}")

    return {"interview_schedule": schedule, "current_agent": "interview_scheduler"}
