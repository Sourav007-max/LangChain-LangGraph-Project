"""
Shared LangGraph state — the single whiteboard every agent reads and writes.
Import this in every agent and in graph.py.
"""

from typing import TypedDict, Annotated, Optional
from langgraph.graph.message import add_messages


class HiringState(TypedDict):
    # ── Inputs ────────────────────────────────────────────────────────────────
    job_id:              int
    job_description_raw: str
    resume_texts:        list[str]   # plain text, one item per resume
    resume_metadata:     list[dict]  # {file_name, candidate_email, candidate_name}

    # ── JD Analysis ───────────────────────────────────────────────────────────
    job_requirements:    Optional[dict]
    # {required_skills, nice_to_have_skills, min_experience_years,
    #  education_requirement, job_summary, key_responsibilities}

    # ── Parsed Resumes ────────────────────────────────────────────────────────
    parsed_resumes:      list[dict]
    # [{full_name, email, current_title, total_experience_years,
    #   skills, education, work_experience}]

    # ── Scoring ───────────────────────────────────────────────────────────────
    candidate_scores:    list[dict]
    # [{candidate_name, email, score 0-100, recommendation,
    #   reasoning, strengths, gaps, skill_match_percentage}]

    # ── Shortlist & Human Review ──────────────────────────────────────────────
    shortlisted_candidates:    list[dict]
    human_decision:            Optional[str]   # "approve" | "reject_all" | "request_more"
    human_feedback:            Optional[str]
    human_approved_candidates: list[dict]

    # ── Interview Scheduling ──────────────────────────────────────────────────
    interview_schedule:  list[dict]
    # [{candidate_name, email, interview_date, time, meeting_link, ai_questions}]

    # ── Evaluation ────────────────────────────────────────────────────────────
    evaluations:         list[dict]

    # ── Final Output ──────────────────────────────────────────────────────────
    final_report:        Optional[str]

    # ── Workflow Control ──────────────────────────────────────────────────────
    current_agent:       str
    errors:              list[str]   # appended, never replaced
    retry_count:         int

    # ── Supervisor conversation history ──────────────────────────────────────
    messages: Annotated[list, add_messages]
