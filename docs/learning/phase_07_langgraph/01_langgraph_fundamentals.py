"""
=============================================================================
  PHASE 7 — LANGGRAPH FUNDAMENTALS
  AI Hiring Co-Pilot: Multi-Agent Recruitment Platform using LangGraph
=============================================================================

This is the HEART of our project.
Master LangGraph = Master multi-agent AI systems.

LEARNING PATH:
  7.1  What is a State Machine? (Mental model)
  7.2  LangGraph State — the shared whiteboard
  7.3  Nodes — the agents/functions
  7.4  Edges — the connections (simple + conditional)
  7.5  Building your first graph (Hello World)
  7.6  Adding Memory (persistence)
  7.7  Human-in-the-Loop
  7.8  Tool Calling in Nodes
  7.9  Checkpointing with Redis
  7.10 Streaming results
=============================================================================
"""

# ─────────────────────────────────────────────────────────────────────────────
# 7.1 MENTAL MODEL — Think in Graphs
# ─────────────────────────────────────────────────────────────────────────────
"""
WHAT IS A STATE MACHINE?
─────────────────────────
Imagine a traffic light:

  RED ──(timer)──► GREEN ──(timer)──► YELLOW ──(timer)──► RED

  • States: RED, GREEN, YELLOW
  • Transitions: triggered by timer
  • One state at a time

LangGraph extends this idea:
  • States: contain ALL data for your workflow (resumes, scores, etc.)
  • Nodes: the processing steps (agents)
  • Edges: the transitions (always, or conditionally based on state)

WHY GRAPHS FOR AI WORKFLOWS?
──────────────────────────────
  Simple chains:   A → B → C (no loops, no branches, no re-tries)
  Graphs:          A → B → (if failed) → A   (loops, branches, re-tries)

  Recruitment workflow NEEDS:
  ✅ Loops: retry if parse fails
  ✅ Branches: if score > 70, shortlist; else reject
  ✅ Parallel: parse 50 resumes simultaneously
  ✅ Interrupts: pause for human review
"""

# ─────────────────────────────────────────────────────────────────────────────
# 7.2 LANGGRAPH STATE — The Shared Whiteboard
# ─────────────────────────────────────────────────────────────────────────────
"""
CONCEPT:
─────────
ALL agents in a LangGraph workflow read from and write to a SINGLE shared
state object. This is like a whiteboard every team member can see.

Key Rules:
  1. State is defined as a TypedDict (typed dictionary)
  2. Every node RECEIVES the state and RETURNS an updated state
  3. LangGraph MERGES returned values using "reducers"
  4. Default reducer: last-write-wins
  5. List reducer: appends new items (add_messages pattern)
"""

from typing import TypedDict, Annotated, Optional
from langgraph.graph.message import add_messages

# ─────────────────────────────────────────────────────────────────────────────
# OUR COMPLETE HIRING STATE (the shared whiteboard for all agents)
# ─────────────────────────────────────────────────────────────────────────────
class HiringState(TypedDict):
    """
    Shared state for the AI Hiring Co-Pilot workflow.
    Every agent reads from and writes to this state.
    
    FIELDS explained:
    """
    # ── Input Data ──────────────────────────────────────────────────────────
    job_id: int                          # which job we're processing
    job_description_raw: str             # original JD text
    resume_file_paths: list[str]         # paths to uploaded PDF files
    
    # ── JD Analysis Results ─────────────────────────────────────────────────
    job_requirements: Optional[dict]     # extracted by JD Analyzer Agent
    # Example: {
    #   "required_skills": ["Python", "FastAPI"],
    #   "min_experience": 4,
    #   "nice_to_have": ["Docker", "AWS"]
    # }
    
    # ── Resume Parsing Results ───────────────────────────────────────────────
    parsed_resumes: list[dict]           # list of extracted resume data
    # Example item: {
    #   "candidate_name": "John Smith",
    #   "email": "john@example.com",
    #   "skills": ["Python", "FastAPI"],
    #   "experience_years": 5,
    #   "file_path": "uploads/john_smith.pdf"
    # }
    
    # ── Matching & Scoring Results ───────────────────────────────────────────
    candidate_scores: list[dict]         # scored candidates
    # Example item: {
    #   "candidate_name": "John Smith",
    #   "score": 87,
    #   "reasoning": "Strong Python + FastAPI match...",
    #   "strengths": [...],
    #   "gaps": [...]
    # }
    
    # ── Shortlisting ────────────────────────────────────────────────────────
    shortlisted_candidates: list[dict]   # top N candidates after ranking
    
    # ── Human-in-the-Loop ───────────────────────────────────────────────────
    human_decision: Optional[str]        # "approve" | "reject" | "request_more"
    human_feedback: Optional[str]        # recruiter's notes
    human_approved_candidates: list[dict]  # candidates human approved
    
    # ── Interview Scheduling ─────────────────────────────────────────────────
    interview_schedule: list[dict]       # scheduled interviews
    # Example item: {
    #   "candidate_name": "John Smith",
    #   "interview_date": "2025-08-20",
    #   "time": "10:00 AM EST",
    #   "email_sent": True
    # }
    
    # ── Evaluation ──────────────────────────────────────────────────────────
    evaluations: list[dict]              # post-interview evaluations
    
    # ── Final Report ────────────────────────────────────────────────────────
    final_report: Optional[str]          # markdown report
    
    # ── Workflow Control ────────────────────────────────────────────────────
    current_agent: str                   # which agent is currently running
    errors: list[str]                    # error messages (uses reducer to append)
    retry_count: int                     # how many times we've retried
    
    # ── Conversation Messages (for supervisor) ───────────────────────────────
    messages: Annotated[list, add_messages]  # add_messages = append, not replace


# ─────────────────────────────────────────────────────────────────────────────
# 7.3 — NODES: Building Individual Agent Nodes
# ─────────────────────────────────────────────────────────────────────────────
"""
WHAT IS A NODE?
────────────────
  A node is ANY Python function that:
  1. Takes the current STATE as input
  2. Does some work (calls LLM, queries DB, etc.)
  3. Returns a PARTIAL state dict (only the keys it updated)

NODE SIGNATURE:
  def my_node(state: HiringState) -> dict:
      # do work
      return {"key_i_updated": new_value}

⚠️ CRITICAL: Return ONLY the keys you changed!
  LangGraph merges your return with the existing state.
  You don't need to return the entire state.
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import json

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# ── NODE 1: JD Analyzer ──────────────────────────────────────────────────────
def jd_analyzer_node(state: HiringState) -> dict:
    """
    Analyzes the job description and extracts structured requirements.
    
    INPUT:  state["job_description_raw"]
    OUTPUT: state["job_requirements"]
    """
    
    prompt = ChatPromptTemplate.from_template("""
    You are an expert technical recruiter. Analyze this job description and 
    extract the requirements in structured JSON format.
    
    Job Description:
    {jd_text}
    
    Return a JSON object with EXACTLY these keys:
    {{
        "required_skills": ["skill1", "skill2"],
        "nice_to_have_skills": ["skill1"],
        "min_experience_years": <integer>,
        "education_requirement": "bachelors|masters|any",
        "job_summary": "<2 sentence summary>",
        "key_responsibilities": ["resp1", "resp2"]
    }}
    
    Return ONLY valid JSON, no other text.
    """)
    
    chain = prompt | llm | JsonOutputParser()
    
    try:
        requirements = chain.invoke({"jd_text": state["job_description_raw"]})
        print(f"  ✅ JD Analyzer: Extracted {len(requirements.get('required_skills', []))} required skills")
        return {
            "job_requirements": requirements,
            "current_agent": "jd_analyzer"
        }
    except Exception as e:
        print(f"  ❌ JD Analyzer failed: {e}")
        return {
            "errors": [f"JD Analysis failed: {str(e)}"],
            "current_agent": "jd_analyzer"
        }


# ── NODE 2: Resume Parser ─────────────────────────────────────────────────────
def resume_parser_node(state: HiringState) -> dict:
    """
    Parses all uploaded resume files and extracts structured data.
    
    INPUT:  state["resume_file_paths"]
    OUTPUT: state["parsed_resumes"]
    """
    import pypdf
    
    parsed_resumes = []
    
    parse_prompt = ChatPromptTemplate.from_template("""
    You are an expert resume parser. Extract structured information from this resume.
    
    Resume Text:
    {resume_text}
    
    Return a JSON object with EXACTLY these keys:
    {{
        "full_name": "<name or null>",
        "email": "<email or null>",
        "phone": "<phone or null>",
        "linkedin": "<url or null>",
        "current_title": "<job title or null>",
        "total_experience_years": <number or null>,
        "skills": ["skill1", "skill2"],
        "education": [{{"degree": "...", "field": "...", "institution": "...", "year": ...}}],
        "work_experience": [{{"title": "...", "company": "...", "years": ..., "description": "..."}}],
        "certifications": ["cert1"]
    }}
    
    Return ONLY valid JSON.
    """)
    
    parse_chain = parse_prompt | llm | JsonOutputParser()
    
    for file_path in state["resume_file_paths"]:
        try:
            # Extract text from PDF
            reader = pypdf.PdfReader(file_path)
            raw_text = " ".join(page.extract_text() for page in reader.pages)
            
            # Parse with LLM
            parsed = parse_chain.invoke({"resume_text": raw_text[:4000]})  # limit tokens
            parsed["file_path"] = file_path
            parsed["raw_text"] = raw_text
            parsed_resumes.append(parsed)
            
            print(f"  ✅ Parsed: {parsed.get('full_name', 'Unknown')} — {file_path}")
        
        except Exception as e:
            print(f"  ❌ Failed to parse {file_path}: {e}")
            parsed_resumes.append({
                "file_path": file_path,
                "parse_error": str(e),
                "full_name": "Parse Failed"
            })
    
    return {
        "parsed_resumes": parsed_resumes,
        "current_agent": "resume_parser"
    }


# ── NODE 3: Candidate Matcher ─────────────────────────────────────────────────
def candidate_matcher_node(state: HiringState) -> dict:
    """
    Scores each candidate against job requirements.
    
    INPUT:  state["parsed_resumes"], state["job_requirements"]
    OUTPUT: state["candidate_scores"]
    """
    
    requirements = state["job_requirements"]
    candidate_scores = []
    
    scoring_prompt = ChatPromptTemplate.from_template("""
    You are a senior technical recruiter scoring a candidate against job requirements.
    
    JOB REQUIREMENTS:
    {requirements}
    
    CANDIDATE PROFILE:
    {candidate}
    
    Score this candidate from 0-100 and provide detailed reasoning.
    
    Return JSON with EXACTLY these keys:
    {{
        "score": <integer 0-100>,
        "recommendation": "STRONGLY_RECOMMEND|RECOMMEND|MAYBE|REJECT",
        "reasoning": "<3-4 sentences explaining the score>",
        "strengths": ["strength1", "strength2"],
        "gaps": ["gap1", "gap2"],
        "skill_match_percentage": <integer 0-100>,
        "experience_match": "exceeds|meets|below"
    }}
    
    Scoring Rubric:
    - 90-100: Perfect match, all requirements met, exceeds in key areas
    - 75-89:  Strong match, most requirements met
    - 60-74:  Decent match, some gaps but trainable
    - 40-59:  Weak match, significant gaps
    - 0-39:   Poor match, fundamental requirements missing
    
    Return ONLY valid JSON.
    """)
    
    scoring_chain = scoring_prompt | llm | JsonOutputParser()
    
    for candidate in state["parsed_resumes"]:
        if "parse_error" in candidate:
            continue
        
        try:
            score_result = scoring_chain.invoke({
                "requirements": json.dumps(requirements, indent=2),
                "candidate": json.dumps({
                    "name": candidate.get("full_name"),
                    "skills": candidate.get("skills", []),
                    "experience_years": candidate.get("total_experience_years"),
                    "current_title": candidate.get("current_title"),
                    "education": candidate.get("education", [])
                }, indent=2)
            })
            
            score_result["candidate_name"] = candidate.get("full_name")
            score_result["candidate_email"] = candidate.get("email")
            score_result["file_path"] = candidate.get("file_path")
            candidate_scores.append(score_result)
            
            print(f"  ✅ Scored: {candidate.get('full_name')} → {score_result.get('score')}/100")
        
        except Exception as e:
            print(f"  ❌ Scoring failed for {candidate.get('full_name')}: {e}")
    
    # Sort by score descending
    candidate_scores.sort(key=lambda x: x.get("score", 0), reverse=True)
    
    return {
        "candidate_scores": candidate_scores,
        "current_agent": "candidate_matcher"
    }


# ── NODE 4: Shortlisting ──────────────────────────────────────────────────────
def shortlisting_node(state: HiringState) -> dict:
    """
    Selects top candidates for human review.
    
    INPUT:  state["candidate_scores"]
    OUTPUT: state["shortlisted_candidates"]
    """
    MIN_SCORE = 60
    MAX_SHORTLIST = 10
    
    shortlisted = [
        c for c in state["candidate_scores"]
        if c.get("score", 0) >= MIN_SCORE
    ][:MAX_SHORTLIST]
    
    print(f"  ✅ Shortlisted {len(shortlisted)} of {len(state['candidate_scores'])} candidates")
    
    return {
        "shortlisted_candidates": shortlisted,
        "current_agent": "shortlisting"
    }


# ── NODE 5: Human Review (Interrupt Point) ────────────────────────────────────
def human_review_node(state: HiringState) -> dict:
    """
    This node is where the workflow PAUSES for human input.
    
    In LangGraph, we use interrupt() to pause here.
    The state is saved to Redis checkpoint.
    The recruiter reviews via the UI and resumes the workflow.
    
    INPUT:  state["shortlisted_candidates"]
    OUTPUT: state["human_approved_candidates"], state["human_decision"]
    """
    from langgraph.types import interrupt
    
    # Format shortlist for human review
    shortlist_summary = []
    for i, candidate in enumerate(state["shortlisted_candidates"], 1):
        shortlist_summary.append(
            f"{i}. {candidate['candidate_name']} — Score: {candidate['score']}/100\n"
            f"   Recommendation: {candidate['recommendation']}\n"
            f"   Reasoning: {candidate['reasoning']}"
        )
    
    # ── INTERRUPT: Workflow pauses here ──────────────────────────────────────
    # The UI shows shortlist_summary to the recruiter
    # Recruiter approves/modifies and resumes workflow
    human_response = interrupt({
        "question": "Please review the shortlisted candidates and approve for interviews",
        "shortlisted_candidates": state["shortlisted_candidates"],
        "summary": "\n\n".join(shortlist_summary)
    })
    
    # After human resumes the workflow, human_response contains their decision
    approved_candidates = human_response.get("approved_candidates", state["shortlisted_candidates"])
    
    return {
        "human_approved_candidates": approved_candidates,
        "human_decision": human_response.get("decision", "approve"),
        "human_feedback": human_response.get("feedback", ""),
        "current_agent": "human_review"
    }


# ── NODE 6: Interview Scheduler ───────────────────────────────────────────────
def interview_scheduler_node(state: HiringState) -> dict:
    """
    Generates interview slots and sends email invitations.
    
    INPUT:  state["human_approved_candidates"]
    OUTPUT: state["interview_schedule"]
    """
    from datetime import datetime, timedelta
    import random
    
    schedule = []
    base_date = datetime.now() + timedelta(days=3)  # start 3 days from now
    
    for i, candidate in enumerate(state["human_approved_candidates"]):
        interview_date = base_date + timedelta(days=i * 2)  # 2 days apart
        
        schedule_entry = {
            "candidate_name": candidate["candidate_name"],
            "candidate_email": candidate["candidate_email"],
            "interview_date": interview_date.strftime("%Y-%m-%d"),
            "interview_time": "10:00 AM EST",
            "meeting_link": f"https://meet.google.com/abc-defg-{random.randint(100, 999)}",
            "interview_type": "technical",
            "ai_questions": generate_interview_questions(candidate, state["job_requirements"])
        }
        schedule.append(schedule_entry)
        print(f"  ✅ Scheduled: {candidate['candidate_name']} → {interview_date.strftime('%Y-%m-%d')}")
    
    return {
        "interview_schedule": schedule,
        "current_agent": "interview_scheduler"
    }


def generate_interview_questions(candidate: dict, requirements: dict) -> list[str]:
    """Generate personalized interview questions for a candidate."""
    prompt = ChatPromptTemplate.from_template("""
    Generate 5 targeted technical interview questions for this candidate
    based on the job requirements.
    
    Candidate Profile: {candidate}
    Job Requirements: {requirements}
    
    Return a JSON array of 5 question strings.
    Focus on: skills gaps, experience depth, and technical problem-solving.
    """)
    
    chain = prompt | llm | JsonOutputParser()
    try:
        questions = chain.invoke({
            "candidate": json.dumps(candidate),
            "requirements": json.dumps(requirements)
        })
        return questions if isinstance(questions, list) else []
    except Exception:
        return [
            "Tell me about your experience with the technologies listed in your resume.",
            "Describe a challenging technical problem you solved recently.",
            "How do you approach debugging complex production issues?"
        ]


# ── NODE 7: Report Generator ──────────────────────────────────────────────────
def report_generator_node(state: HiringState) -> dict:
    """
    Generates a final hiring report summarizing the entire process.
    
    INPUT:  entire state
    OUTPUT: state["final_report"]
    """
    
    report_prompt = ChatPromptTemplate.from_template("""
    You are a senior HR analytics expert. Generate a comprehensive hiring report.
    
    Job ID: {job_id}
    Total Resumes Processed: {total_resumes}
    Shortlisted: {shortlisted_count}
    Approved by HR: {approved_count}
    Interviews Scheduled: {interviews_count}
    
    Top Candidates:
    {top_candidates}
    
    Generate a professional markdown report with:
    1. Executive Summary
    2. Candidate Pipeline Overview
    3. Top 3 Candidate Profiles with detailed assessment
    4. Skill Gap Analysis (what skills are rare in the applicant pool)
    5. Hiring Recommendation
    6. Next Steps
    
    Use professional language suitable for C-suite presentation.
    """)
    
    report_chain = report_prompt | llm
    
    top_3 = state["candidate_scores"][:3] if state["candidate_scores"] else []
    
    try:
        report = report_chain.invoke({
            "job_id": state["job_id"],
            "total_resumes": len(state["resume_file_paths"]),
            "shortlisted_count": len(state["shortlisted_candidates"]),
            "approved_count": len(state.get("human_approved_candidates", [])),
            "interviews_count": len(state.get("interview_schedule", [])),
            "top_candidates": json.dumps(top_3, indent=2)
        })
        
        return {
            "final_report": report.content,
            "current_agent": "report_generator"
        }
    except Exception as e:
        return {
            "errors": [f"Report generation failed: {str(e)}"],
            "current_agent": "report_generator"
        }


# ─────────────────────────────────────────────────────────────────────────────
# 7.4 — EDGES: Connecting Nodes
# ─────────────────────────────────────────────────────────────────────────────
"""
TWO TYPES OF EDGES:
────────────────────
  1. SIMPLE EDGES: Always go from A → B
     graph.add_edge("node_a", "node_b")

  2. CONDITIONAL EDGES: Go to different nodes based on state
     graph.add_conditional_edges(
         "node_a",
         routing_function,
         {"route_x": "node_x", "route_y": "node_y"}
     )
"""

def route_after_parsing(state: HiringState) -> str:
    """
    Routing function: decides where to go after parsing.
    
    If parsing failed → go to error handler
    If no resumes parsed → go to error handler
    Otherwise → go to matching
    """
    if state.get("errors") and len(state.get("parsed_resumes", [])) == 0:
        return "error_handler"
    
    if len(state.get("parsed_resumes", [])) == 0:
        return "error_handler"
    
    return "candidate_matcher"


def route_after_shortlisting(state: HiringState) -> str:
    """
    If no candidates meet threshold → end with no candidates report
    Otherwise → go to human review
    """
    if not state.get("shortlisted_candidates"):
        return "report_generator"  # no candidates → generate rejection report
    
    return "human_review"


def route_after_human_review(state: HiringState) -> str:
    """
    Human decided to:
    - approve → schedule interviews
    - reject all → generate rejection report
    - request_more → go back to resume parser with new files
    """
    decision = state.get("human_decision", "approve")
    
    if decision == "reject_all":
        return "report_generator"
    elif decision == "request_more":
        return "resume_parser"  # loop back!
    else:  # "approve"
        return "interview_scheduler"


# ─────────────────────────────────────────────────────────────────────────────
# 7.5 — BUILDING THE COMPLETE LANGGRAPH
# ─────────────────────────────────────────────────────────────────────────────

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.redis import RedisSaver

def build_hiring_workflow() -> StateGraph:
    """
    Assembles the complete AI Hiring Co-Pilot LangGraph workflow.
    
    GRAPH FLOW:
    START
      ↓
    jd_analyzer (parallel with resume_parser ideally)
      ↓
    resume_parser
      ↓
    candidate_matcher
      ↓
    shortlisting
      ↓ (conditional: no candidates → report_generator)
    human_review    ← INTERRUPT POINT
      ↓ (conditional: approve/reject_all/request_more)
    interview_scheduler
      ↓
    report_generator
      ↓
    END
    """
    
    # 1. Create the graph with our state
    workflow = StateGraph(HiringState)
    
    # 2. Add all nodes
    workflow.add_node("jd_analyzer", jd_analyzer_node)
    workflow.add_node("resume_parser", resume_parser_node)
    workflow.add_node("candidate_matcher", candidate_matcher_node)
    workflow.add_node("shortlisting", shortlisting_node)
    workflow.add_node("human_review", human_review_node)
    workflow.add_node("interview_scheduler", interview_scheduler_node)
    workflow.add_node("report_generator", report_generator_node)
    
    # 3. Add edges (the flow)
    workflow.add_edge(START, "jd_analyzer")              # start → analyze JD
    workflow.add_edge("jd_analyzer", "resume_parser")    # then parse resumes
    
    # Conditional: after parsing, check if we got results
    workflow.add_conditional_edges(
        "resume_parser",
        route_after_parsing,
        {
            "candidate_matcher": "candidate_matcher",
            "error_handler": END  # simplified: just end on error
        }
    )
    
    workflow.add_edge("candidate_matcher", "shortlisting")
    
    # Conditional: after shortlisting
    workflow.add_conditional_edges(
        "shortlisting",
        route_after_shortlisting,
        {
            "human_review": "human_review",
            "report_generator": "report_generator"
        }
    )
    
    # Conditional: after human review
    workflow.add_conditional_edges(
        "human_review",
        route_after_human_review,
        {
            "interview_scheduler": "interview_scheduler",
            "report_generator": "report_generator",
            "resume_parser": "resume_parser"  # loop back!
        }
    )
    
    workflow.add_edge("interview_scheduler", "report_generator")
    workflow.add_edge("report_generator", END)
    
    return workflow


def compile_graph_with_redis_checkpointing():
    """
    Compiles the graph with Redis checkpointing for persistence.
    
    Why Redis checkpointing?
    → Workflow state survives server restarts
    → Human-in-the-loop can take hours — state must be saved
    → Can replay/debug from any checkpoint
    """
    import os
    
    workflow = build_hiring_workflow()
    
    # Redis checkpointer saves state after EVERY node execution
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    with RedisSaver.from_conn_string(redis_url) as checkpointer:
        compiled_graph = workflow.compile(
            checkpointer=checkpointer,
            interrupt_before=["human_review"]  # pause BEFORE human_review runs
        )
    
    return compiled_graph


# ─────────────────────────────────────────────────────────────────────────────
# 7.6 — RUNNING THE WORKFLOW (Full Example)
# ─────────────────────────────────────────────────────────────────────────────

def run_hiring_workflow_example():
    """
    Complete example of running the hiring workflow.
    This is what Phase 9 will expand into the full system.
    """
    import uuid
    
    graph = compile_graph_with_redis_checkpointing()
    
    # Each workflow run needs a unique thread_id for checkpointing
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    # Initial state — inputs from the recruiter
    initial_state = {
        "job_id": 1,
        "job_description_raw": """
            Senior Python Developer
            Requirements: 5+ years Python, FastAPI, PostgreSQL, AWS, Docker
            Nice to have: LangChain, Kubernetes
        """,
        "resume_file_paths": [
            "uploads/john_smith.pdf",
            "uploads/jane_doe.pdf",
            "uploads/bob_johnson.pdf"
        ],
        "parsed_resumes": [],
        "candidate_scores": [],
        "shortlisted_candidates": [],
        "human_approved_candidates": [],
        "interview_schedule": [],
        "evaluations": [],
        "errors": [],
        "retry_count": 0,
        "messages": [],
        "current_agent": "start"
    }
    
    print("=" * 60)
    print("  AI HIRING CO-PILOT — Starting Workflow")
    print(f"  Thread ID: {thread_id}")
    print("=" * 60)
    
    # ── Phase 1: Run until human_review interrupt ─────────────────────────
    print("\n[Phase 1] Running automated agents...")
    
    for event in graph.stream(initial_state, config=config, stream_mode="values"):
        current_agent = event.get("current_agent", "")
        if current_agent:
            print(f"  → Agent completed: {current_agent}")
    
    # At this point, workflow is PAUSED at human_review
    print("\n⏸  Workflow paused for human review")
    print("   Recruiter reviews shortlist in UI...")
    
    # ── Phase 2: Human provides decision (simulated) ──────────────────────
    print("\n[Phase 2] Recruiter approved candidates, resuming workflow...")
    
    human_decision = {
        "decision": "approve",
        "approved_candidates": graph.get_state(config).values["shortlisted_candidates"][:3],
        "feedback": "These look great! Proceed with top 3."
    }
    
    # Resume workflow with human's decision
    graph.update_state(config, {"human_decision": "approve"}, as_node="human_review")
    
    for event in graph.stream(None, config=config, stream_mode="values"):
        current_agent = event.get("current_agent", "")
        if current_agent:
            print(f"  → Agent completed: {current_agent}")
    
    # ── Get final state ───────────────────────────────────────────────────
    final_state = graph.get_state(config).values
    
    print("\n" + "=" * 60)
    print("  WORKFLOW COMPLETE")
    print(f"  Candidates processed: {len(final_state.get('candidate_scores', []))}")
    print(f"  Shortlisted: {len(final_state.get('shortlisted_candidates', []))}")
    print(f"  Interviews scheduled: {len(final_state.get('interview_schedule', []))}")
    print("=" * 60)
    
    if final_state.get("final_report"):
        print("\n📄 FINAL REPORT GENERATED")
        print(final_state["final_report"][:500] + "...")
    
    return final_state


# ─────────────────────────────────────────────────────────────────────────────
# PHASE 7 QUIZ
# ─────────────────────────────────────────────────────────────────────────────
"""
Q1. What does a LangGraph Node receive as input and what must it return?
A:  It receives the complete current State, and returns a PARTIAL dict
    containing only the keys it updated. LangGraph merges this with
    existing state.

Q2. What is the difference between a simple edge and a conditional edge?
A:  Simple edge: always routes A → B regardless of state.
    Conditional edge: calls a routing function that inspects state
    and returns a string key, which maps to different destination nodes.

Q3. Why do we use interrupt() in the human_review_node?
A:  interrupt() pauses workflow execution at that point, saves state
    to the checkpointer (Redis), and waits for external input.
    This allows the recruiter to review via UI and resume when ready,
    even hours or days later.

Q4. What is the purpose of the 'add_messages' annotation in HiringState?
A:  The default behavior replaces the entire list. add_messages is a
    REDUCER that appends new messages instead of replacing. This
    maintains conversation history for the supervisor agent.

Q5. Why is thread_id important in LangGraph config?
A:  thread_id identifies a specific workflow run in the checkpointer.
    Multiple concurrent recruiters each get their own thread_id,
    allowing parallel independent workflows with isolated state.
"""
