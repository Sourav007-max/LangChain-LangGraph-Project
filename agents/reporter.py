"""
Reporting Agent
---------------
Input  : full state (reads totals from every previous agent)
Output : state["final_report"]  — markdown string, ready to display in UI
"""

import json
from config.settings import get_llm
from config.monitoring import log_agent
from agents.state import HiringState
from agents.prompts import REPORT_GENERATION_PROMPT

_PROMPT = REPORT_GENERATION_PROMPT


def _find_skill_gaps(state: HiringState) -> list[str]:
    required = set(state.get("job_requirements", {}).get("required_skills", []))
    candidate_skills: set[str] = set()
    for c in state.get("parsed_resumes", []):
        candidate_skills.update(s.lower() for s in c.get("skills", []))
    return [s for s in required if s.lower() not in candidate_skills]


@log_agent("reporter", "generate_report")
def report_generator_node(state: HiringState) -> dict:
    llm = get_llm(temperature=0.2)
    chain = _PROMPT | llm

    top3 = state.get("candidate_scores", [])[:3]
    skill_gaps = _find_skill_gaps(state)

    try:
        response = chain.invoke({
            "job_id":           state.get("job_id", "N/A"),
            "total_resumes":    len(state.get("resume_texts", [])),
            "parsed_count":     len(state.get("parsed_resumes", [])),
            "shortlisted_count": len(state.get("shortlisted_candidates", [])),
            "approved_count":   len(state.get("human_approved_candidates", [])),
            "interviews_count": len(state.get("interview_schedule", [])),
            "top_candidates":   json.dumps(top3, indent=2),
            "skill_gaps":       json.dumps(skill_gaps),
        })
        report = response.content
        print("  [Reporter] Final report generated")
        return {"final_report": report, "current_agent": "report_generator"}
    except Exception as exc:
        print(f"  [Reporter] {exc}")
        return {
            "final_report": f"# Report Generation Failed\n\n{exc}",
            "current_agent": "report_generator",
        }
