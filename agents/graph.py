"""
Phase 9 — Complete Multi-Agent LangGraph Workflow
==================================================
Assembles all agents into a single compiled graph with:
  • Conditional routing
  • Human-in-the-loop interrupt (before human_review node)
  • SQLite checkpointing (no Redis required for development)
  • Streaming support

Usage:
    from agents.graph import build_graph, run_workflow, resume_workflow
"""

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver   # SQLite-backed in prod

from agents.state              import HiringState
from agents.jd_analyzer        import jd_analyzer_node
from agents.resume_parser      import resume_parser_node
from agents.candidate_matcher  import candidate_matcher_node
from agents.shortlisting       import shortlisting_node
from agents.interview_scheduler import interview_scheduler_node
from agents.reporter           import report_generator_node


# ─────────────────────────────────────────────────────────────────────────────
# Human-in-the-loop node (pure passthrough — interrupt happens BEFORE it runs)
# ─────────────────────────────────────────────────────────────────────────────

def human_review_node(state: HiringState) -> dict:
    """
    This node runs AFTER the recruiter resumes the workflow.
    By the time execution reaches here, human_approved_candidates
    has already been injected via graph.update_state().
    """
    approved = state.get("human_approved_candidates", state.get("shortlisted_candidates", []))
    print(f"  [Human Review] ✅ Recruiter approved {len(approved)} candidate(s)")
    return {
        "human_approved_candidates": approved,
        "human_decision":            state.get("human_decision", "approve"),
        "current_agent":             "human_review",
    }


# ─────────────────────────────────────────────────────────────────────────────
# Routing functions
# ─────────────────────────────────────────────────────────────────────────────

def _route_after_parsing(state: HiringState) -> str:
    """Skip matching if nothing was parsed successfully."""
    usable = [r for r in state.get("parsed_resumes", []) if not r.get("parse_error")]
    return "candidate_matcher" if usable else "report_generator"


def _route_after_shortlisting(state: HiringState) -> str:
    """Skip human review if no candidates met the score threshold."""
    return "human_review" if state.get("shortlisted_candidates") else "report_generator"


def _route_after_human_review(state: HiringState) -> str:
    decision = state.get("human_decision", "approve")
    if decision == "reject_all":
        return "report_generator"
    if decision == "request_more":
        return "resume_parser"          # loop back for more resumes
    return "interview_scheduler"        # "approve" — default path


# ─────────────────────────────────────────────────────────────────────────────
# Build & compile graph
# ─────────────────────────────────────────────────────────────────────────────

# MemorySaver stores checkpoints in-process (perfect for dev / testing).
# Swap for SqliteSaver or RedisSaver in production.
_checkpointer = MemorySaver()


def build_graph():
    """
    Returns a compiled LangGraph StateGraph.

    Graph topology:
        START
          ↓
        jd_analyzer
          ↓
        resume_parser  ──(no usable resumes)──► report_generator ──► END
          ↓
        candidate_matcher
          ↓
        shortlisting ──(no shortlist)──► report_generator ──► END
          ↓
        [INTERRUPT]
        human_review ──(reject_all)──► report_generator ──► END
          │          ──(request_more)─► resume_parser  (loop)
          ↓ (approve)
        interview_scheduler
          ↓
        report_generator
          ↓
         END
    """
    wf = StateGraph(HiringState)

    wf.add_node("jd_analyzer",          jd_analyzer_node)
    wf.add_node("resume_parser",         resume_parser_node)
    wf.add_node("candidate_matcher",     candidate_matcher_node)
    wf.add_node("shortlisting",          shortlisting_node)
    wf.add_node("human_review",          human_review_node)
    wf.add_node("interview_scheduler",   interview_scheduler_node)
    wf.add_node("report_generator",      report_generator_node)

    wf.add_edge(START, "jd_analyzer")
    wf.add_edge("jd_analyzer", "resume_parser")

    wf.add_conditional_edges(
        "resume_parser", _route_after_parsing,
        {"candidate_matcher": "candidate_matcher", "report_generator": "report_generator"},
    )
    wf.add_edge("candidate_matcher", "shortlisting")

    wf.add_conditional_edges(
        "shortlisting", _route_after_shortlisting,
        {"human_review": "human_review", "report_generator": "report_generator"},
    )

    wf.add_conditional_edges(
        "human_review", _route_after_human_review,
        {
            "interview_scheduler": "interview_scheduler",
            "report_generator":    "report_generator",
            "resume_parser":       "resume_parser",
        },
    )

    wf.add_edge("interview_scheduler", "report_generator")
    wf.add_edge("report_generator", END)

    return wf.compile(
        checkpointer=_checkpointer,
        interrupt_before=["human_review"],  # pause here for recruiter review
    )


# Singleton — import this everywhere
graph = build_graph()


# ─────────────────────────────────────────────────────────────────────────────
# Helper functions used by the FastAPI backend
# ─────────────────────────────────────────────────────────────────────────────

def run_workflow(thread_id: str, initial_state: dict) -> dict:
    """
    Start the workflow.  Runs until the human_review interrupt.
    Returns the current state snapshot.
    """
    config = {"configurable": {"thread_id": thread_id}}
    for _ in graph.stream(initial_state, config=config, stream_mode="values"):
        pass   # stream drives execution; state is checkpointed automatically
    return graph.get_state(config).values


def resume_workflow(thread_id: str, approved_candidates: list, decision: str = "approve", feedback: str = "") -> dict:
    """
    Resume after human review.
    Injects the recruiter's decision and runs to completion.
    """
    config = {"configurable": {"thread_id": thread_id}}
    graph.update_state(
        config,
        {
            "human_approved_candidates": approved_candidates,
            "human_decision":            decision,
            "human_feedback":            feedback,
        },
        as_node="human_review",
    )
    for _ in graph.stream(None, config=config, stream_mode="values"):
        pass
    return graph.get_state(config).values


def get_workflow_state(thread_id: str) -> dict:
    """Read current checkpointed state without running the graph."""
    config = {"configurable": {"thread_id": thread_id}}
    snapshot = graph.get_state(config)
    return snapshot.values if snapshot else {}
