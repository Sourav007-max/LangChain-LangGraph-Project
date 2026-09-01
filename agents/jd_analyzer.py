"""
JD Analyzer Agent
-----------------
Input  : state["job_description_raw"]
Output : state["job_requirements"]  — structured JSON of what the job needs
"""

import time
from langchain_core.output_parsers import JsonOutputParser
from config.settings import get_llm
from config.monitoring import log_agent
from agents.state import HiringState
from agents.prompts import JD_ANALYSIS_PROMPT

_PROMPT = JD_ANALYSIS_PROMPT


@log_agent("jd_analyzer", "analyze_jd")
def jd_analyzer_node(state: HiringState) -> dict:
    t0 = time.time()
    llm = get_llm(temperature=0)
    chain = _PROMPT | llm | JsonOutputParser()

    try:
        result = chain.invoke({"jd_text": state["job_description_raw"]})
        elapsed = int((time.time() - t0) * 1000)
        skill_count = len(result.get("required_skills", []))
        print(f"  [JD Analyzer] ✅ {skill_count} required skills extracted ({elapsed}ms)")
        return {"job_requirements": result, "current_agent": "jd_analyzer"}
    except Exception as exc:
        print(f"  [JD Analyzer] ❌ {exc}")
        return {
            "errors": [f"JD analysis failed: {exc}"],
            "job_requirements": {"required_skills": [], "min_experience_years": 0},
            "current_agent": "jd_analyzer",
        }
