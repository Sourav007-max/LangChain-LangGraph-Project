"""
Resume Parser Agent
-------------------
Input  : state["resume_texts"]  (plain text, one per resume)
         state["resume_metadata"]  [{file_name, candidate_email, candidate_name}]
Output : state["parsed_resumes"]  — list of structured candidate dicts
"""

import time
from langchain_core.output_parsers import JsonOutputParser
from config.settings import get_llm, RESUME_MAX_CHARS
from config.monitoring import log_agent
from agents.state import HiringState
from agents.prompts import RESUME_PARSING_PROMPT

_PROMPT = RESUME_PARSING_PROMPT


@log_agent("resume_parser", "parse_resumes")
def resume_parser_node(state: HiringState) -> dict:
    llm = get_llm(temperature=0)
    chain = _PROMPT | llm | JsonOutputParser()

    parsed = []
    texts    = state.get("resume_texts", [])
    metadata = state.get("resume_metadata", [{}] * len(texts))

    for i, text in enumerate(texts):
        meta = metadata[i] if i < len(metadata) else {}
        t0 = time.time()
        try:
            result = chain.invoke({"resume_text": text[:RESUME_MAX_CHARS]})
            # Merge file metadata in case LLM missed the email
            result.setdefault("email", meta.get("candidate_email", ""))
            result.setdefault("full_name", meta.get("candidate_name", "Unknown"))
            result["file_name"] = meta.get("file_name", f"resume_{i+1}.pdf")
            elapsed = int((time.time() - t0) * 1000)
            print(f"  [Resume Parser] {result.get('full_name')} ({elapsed}ms)")
            parsed.append(result)
        except Exception as exc:
            print(f"  [Resume Parser] resume {i+1}: {exc}")
            parsed.append({
                "full_name":  meta.get("candidate_name", f"Candidate {i+1}"),
                "email":      meta.get("candidate_email", ""),
                "file_name":  meta.get("file_name", f"resume_{i+1}.pdf"),
                "skills":     [],
                "parse_error": str(exc),
            })

    return {"parsed_resumes": parsed, "current_agent": "resume_parser"}
