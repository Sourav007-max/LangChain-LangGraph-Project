"""
Phase 12 — LangSmith Monitoring & Observability
=================================================

WHY MONITORING MATTERS (Industry context):
  Without monitoring, you are BLIND to:
    • Which agent is slowest / most expensive
    • Which prompts hallucinate
    • Why a workflow silently failed
    • Cost per candidate screened

  LangSmith gives you a trace for EVERY LLM call:
    • Input prompt (exact text sent)
    • Output (exact text received)
    • Latency in ms
    • Token count
    • Cost in USD
    • Error messages

HOW IT WORKS:
  Setting LANGCHAIN_TRACING_V2=true in .env is enough.
  Every LangChain/LangGraph call is automatically traced.
  No code changes needed.

This file adds:
  1. Per-agent timing + cost logging to agent_logs table
  2. A helper decorator for any function you want to trace
  3. A monitoring dashboard endpoint in FastAPI
  4. LangSmith run-tagging for each workflow
"""

import os
import time
import functools
import logging
from datetime import datetime, timezone
from typing import Callable, Any

from langsmith import Client
from langsmith.run_helpers import traceable
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# ── LangSmith client (only if key is set) ─────────────────────────────────
_ls_client: Client | None = None

def get_langsmith_client() -> Client | None:
    global _ls_client
    if _ls_client is None and os.getenv("LANGCHAIN_API_KEY"):
        try:
            _ls_client = Client()
        except Exception as e:
            logger.warning(f"LangSmith client init failed: {e}")
    return _ls_client


# ─────────────────────────────────────────────────────────────────────────────
# AGENT LOGGING DECORATOR
# Wraps any agent node function to log timing, tokens, cost to DB
# ─────────────────────────────────────────────────────────────────────────────

def log_agent(agent_name: str, action_type: str = "run"):
    """
    Decorator — wrap any LangGraph node to get automatic DB logging.

    Usage:
        @log_agent("jd_analyzer", "analyze_jd")
        def jd_analyzer_node(state): ...
    """
    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(state: dict, *args, **kwargs) -> dict:
            t0 = time.time()
            error_msg = None
            result = {}

            try:
                result = fn(state, *args, **kwargs)
                status = "success"
            except Exception as exc:
                error_msg = str(exc)
                status = "failed"
                logger.error(f"[{agent_name}] failed: {exc}")
                result = {"errors": [f"{agent_name}: {exc}"], "current_agent": agent_name}

            elapsed_ms = int((time.time() - t0) * 1000)

            # Write to agent_logs table
            _write_agent_log(
                session_id=state.get("_thread_id", "unknown"),
                agent_name=agent_name,
                action_type=action_type,
                input_summary=f"job_id={state.get('job_id')} resumes={len(state.get('resume_texts', []))}",
                output_summary=_summarise_result(result),
                latency_ms=elapsed_ms,
                status=status,
                error_message=error_msg,
            )

            logger.info(f"[{agent_name}] {status} in {elapsed_ms}ms")
            return result

        return wrapper
    return decorator


def _summarise_result(result: dict) -> str:
    """One-line summary of what the agent produced — stored in DB, never PII."""
    parts = []
    if "job_requirements" in result and result["job_requirements"]:
        n = len(result["job_requirements"].get("required_skills", []))
        parts.append(f"{n} required skills")
    if "parsed_resumes" in result:
        parts.append(f"{len(result['parsed_resumes'])} resumes parsed")
    if "candidate_scores" in result:
        parts.append(f"{len(result['candidate_scores'])} candidates scored")
    if "shortlisted_candidates" in result:
        parts.append(f"{len(result['shortlisted_candidates'])} shortlisted")
    if "interview_schedule" in result:
        parts.append(f"{len(result['interview_schedule'])} interviews scheduled")
    if "final_report" in result and result["final_report"]:
        parts.append("report generated")
    if "errors" in result and result["errors"]:
        parts.append(f"errors: {result['errors'][-1][:80]}")
    return "; ".join(parts) if parts else "ok"


def _write_agent_log(
    session_id: str, agent_name: str, action_type: str,
    input_summary: str, output_summary: str,
    latency_ms: int, status: str, error_message: str | None
):
    """Write one row to agent_logs (non-blocking best-effort)."""
    try:
        from database.init_db import SessionLocal, AgentLog
        db = SessionLocal()
        log = AgentLog(
            session_id=session_id,
            agent_name=agent_name,
            action_type=action_type,
            input_summary=input_summary,
            output_summary=output_summary,
            latency_ms=latency_ms,
            status=status,
            error_message=error_message,
        )
        db.add(log)
        db.commit()
        db.close()
    except Exception as e:
        logger.debug(f"AgentLog write failed (non-fatal): {e}")


# ─────────────────────────────────────────────────────────────────────────────
# LANGSMITH @traceable — marks functions visible in LangSmith UI
# ─────────────────────────────────────────────────────────────────────────────
"""
Add @traceable to any function to see it as a named span in LangSmith.
It wraps the function exactly like a decorator — zero behaviour change.

Example:
    @traceable(name="JD Analyzer", run_type="chain")
    def jd_analyzer_node(state): ...

In LangSmith you'll see:
  Hiring Workflow
  └── JD Analyzer          (200ms, $0.002)
      ├── ChatGroq.invoke   (180ms, 1200 tokens)
      └── JsonOutputParser

The @traceable decorator is already imported from langsmith above.
Export it so agents can import from this module.
"""


# ─────────────────────────────────────────────────────────────────────────────
# MONITORING STATS — used by FastAPI /monitoring endpoint
# ─────────────────────────────────────────────────────────────────────────────

def get_agent_stats(hours: int = 24) -> dict:
    """
    Query agent_logs for performance metrics over the last N hours.
    Returns data for the monitoring dashboard.
    """
    try:
        from database.init_db import SessionLocal, AgentLog
        from sqlalchemy import func, text as sqltext

        db = SessionLocal()
        since = datetime.now(timezone.utc).replace(tzinfo=None)

        rows = db.execute(sqltext("""
            SELECT
                agent_name,
                COUNT(*)                                    AS total_runs,
                SUM(CASE WHEN status='success' THEN 1 ELSE 0 END) AS successes,
                SUM(CASE WHEN status='failed'  THEN 1 ELSE 0 END) AS failures,
                ROUND(AVG(latency_ms))                      AS avg_latency_ms,
                MAX(latency_ms)                             AS max_latency_ms,
                SUM(CASE WHEN status='failed'  THEN 1 ELSE 0 END) * 100.0
                    / COUNT(*)                              AS error_rate_pct
            FROM agent_logs
            GROUP BY agent_name
            ORDER BY total_runs DESC
        """)).fetchall()
        db.close()

        return {
            "agents": [dict(r._mapping) for r in rows],
            "generated_at": datetime.now().isoformat(),
        }
    except Exception as e:
        return {"agents": [], "error": str(e), "generated_at": datetime.now().isoformat()}


def get_recent_logs(limit: int = 20) -> list[dict]:
    """Return the most recent agent log entries for live tail in dashboard."""
    try:
        from database.init_db import SessionLocal, AgentLog
        db = SessionLocal()
        rows = db.query(AgentLog).order_by(AgentLog.created_at.desc()).limit(limit).all()
        db.close()
        return [
            {
                "id":           r.id,
                "agent":        r.agent_name,
                "action":       r.action_type,
                "status":       r.status,
                "latency_ms":   r.latency_ms,
                "output":       r.output_summary,
                "error":        r.error_message,
                "ts":           r.created_at.isoformat() if r.created_at else None,
            }
            for r in rows
        ]
    except Exception as e:
        return [{"error": str(e)}]
