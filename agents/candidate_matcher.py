"""
Candidate Matcher Agent
-----------------------
Input  : state["parsed_resumes"], state["job_requirements"]
Output : state["candidate_scores"]  — sorted list, highest score first
"""

import json
import time
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from config.settings import get_llm
from config.monitoring import log_agent
from agents.state import HiringState

_PROMPT = ChatPromptTemplate.from_template("""
You are a senior technical recruiter scoring a candidate against job requirements.
Return ONLY valid JSON — no markdown, no extra text.

Job Requirements:
{requirements}

Candidate Profile:
{candidate}

Scoring rubric:
  90-100: Perfect match — all requirements met, exceeds in key areas
  75-89 : Strong match — most requirements met
  60-74 : Decent match — some gaps, but trainable
  40-59 : Weak match — significant gaps
  0-39  : Poor match — fundamental requirements missing

JSON schema to return:
{{
  "score":                  <integer 0-100>,
  "recommendation":         "STRONGLY_RECOMMEND|RECOMMEND|MAYBE|REJECT",
  "reasoning":              "<3 concise sentences>",
  "strengths":              ["strength1", "strength2"],
  "gaps":                   ["gap1"],
  "skill_match_percentage": <integer 0-100>,
  "experience_match":       "exceeds|meets|below"
}}
""")


@log_agent("candidate_matcher", "score_candidates")
def candidate_matcher_node(state: HiringState) -> dict:
    llm = get_llm(temperature=0)
    chain = _PROMPT | llm | JsonOutputParser()

    requirements = state.get("job_requirements", {})
    scores = []

    for candidate in state.get("parsed_resumes", []):
        if candidate.get("parse_error"):
            continue
        t0 = time.time()
        try:
            profile = {
                "name":             candidate.get("full_name"),
                "skills":           candidate.get("skills", []),
                "experience_years": candidate.get("total_experience_years", 0),
                "current_title":    candidate.get("current_title"),
                "education":        candidate.get("education", []),
            }
            result = chain.invoke({
                "requirements": json.dumps(requirements, indent=2),
                "candidate":    json.dumps(profile,      indent=2),
            })
            result["candidate_name"]  = candidate.get("full_name", "Unknown")
            result["candidate_email"] = candidate.get("email", "")
            result["file_name"]       = candidate.get("file_name", "")
            elapsed = int((time.time() - t0) * 1000)
            print(f"  [Matcher] ✅ {result['candidate_name']} → {result.get('score')}/100 ({elapsed}ms)")
            scores.append(result)
        except Exception as exc:
            print(f"  [Matcher] ❌ {candidate.get('full_name')}: {exc}")

    scores.sort(key=lambda x: x.get("score", 0), reverse=True)
    return {"candidate_scores": scores, "current_agent": "candidate_matcher"}
