"""
Shortlisting Node  (not a full LLM agent — pure Python logic)
-----------------
Input  : state["candidate_scores"]
Output : state["shortlisted_candidates"]

Rules (configurable via env):
  MIN_SCORE   — minimum AI score to be considered  (default 60)
  MAX_SHORTLIST — max candidates sent for human review (default 10)
"""

import os
from agents.state import HiringState

MIN_SCORE     = int(os.getenv("SHORTLIST_MIN_SCORE",   "60"))
MAX_SHORTLIST = int(os.getenv("SHORTLIST_MAX_RESULTS", "10"))


def shortlisting_node(state: HiringState) -> dict:
    scores = state.get("candidate_scores", [])
    shortlisted = [c for c in scores if c.get("score", 0) >= MIN_SCORE][:MAX_SHORTLIST]

    print(
        f"  [Shortlisting] ✅ {len(shortlisted)} / {len(scores)} candidates "
        f"meet threshold (score ≥ {MIN_SCORE})"
    )

    return {"shortlisted_candidates": shortlisted, "current_agent": "shortlisting"}
