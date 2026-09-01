"""
=============================================================================
  PHASE 1 — HANDS-ON EXERCISES, QUIZ & INTERVIEW PREP
  AI Hiring Co-Pilot: Multi-Agent Recruitment Platform using LangGraph
=============================================================================
"""

# ─────────────────────────────────────────────────────────────────────────────
# HANDS-ON EXERCISE 1 — Your First LLM Call (No Framework)
# PURPOSE: Understand raw LLM interaction before we add abstractions
# ─────────────────────────────────────────────────────────────────────────────
"""
TASK: Call OpenAI API directly to parse a sample resume.
This shows you what LangChain does "under the hood".

PREREQUISITE: You will need an OpenAI API key (covered in Phase 3).
For now, READ and UNDERSTAND the code structure.
"""

import os
import json

# Exercise 1A: Understand what a PROMPT is
SAMPLE_RESUME = """
John Smith
Email: john.smith@email.com | Phone: +1-555-0123
LinkedIn: linkedin.com/in/johnsmith

EXPERIENCE:
Senior Software Engineer | TechCorp Inc. | 2020 - Present
- Built REST APIs using Python and FastAPI
- Led team of 5 engineers
- Reduced system latency by 40% using Redis caching

Junior Developer | StartupXYZ | 2018 - 2020
- Developed React frontend components
- Wrote SQL queries for PostgreSQL database

EDUCATION:
B.S. Computer Science | State University | 2018

SKILLS:
Python, FastAPI, React, PostgreSQL, Redis, Docker, AWS, Git
"""

SAMPLE_JD = """
Job Title: Senior Python Developer
Company: InnovateTech

Requirements:
- 4+ years of Python experience
- FastAPI or Django experience required
- Database experience (PostgreSQL preferred)
- Cloud experience (AWS or GCP)
- Team leadership experience preferred
- Docker/Kubernetes knowledge

Responsibilities:
- Design and build scalable APIs
- Mentor junior developers
- Collaborate with product team
"""

# ─── Exercise 1A: Write the prompt manually ───────────────────────────────
def exercise_1a_craft_a_prompt():
    """
    EXERCISE: Craft a prompt that tells the LLM to evaluate a candidate.
    
    A good prompt has 4 parts:
      1. ROLE    → who the LLM is pretending to be
      2. CONTEXT → the data it needs
      3. TASK    → what exactly to do
      4. FORMAT  → how to return results
    
    Study the template below and understand each section.
    """
    
    prompt_template = """
    ROLE:
    You are an expert technical recruiter with 10 years of experience
    evaluating software engineering candidates.
    
    CONTEXT:
    Job Description:
    {job_description}
    
    Candidate Resume:
    {resume}
    
    TASK:
    Evaluate this candidate for the job description above.
    
    Analyze:
    1. Skill match percentage (0-100%)
    2. Years of experience match
    3. Red flags (if any)
    4. Strengths
    5. Overall recommendation (STRONGLY RECOMMEND / RECOMMEND / REJECT)
    
    FORMAT:
    Return your response as a valid JSON object with these keys:
    - skill_match_score: integer (0-100)
    - experience_match: string ("Exceeds" | "Meets" | "Below")
    - strengths: list of strings
    - red_flags: list of strings
    - recommendation: string
    - reasoning: string (2-3 sentences)
    """
    
    formatted_prompt = prompt_template.format(
        job_description=SAMPLE_JD,
        resume=SAMPLE_RESUME
    )
    
    return formatted_prompt


# ─── Exercise 1B: Simulate what an agent does (no LLM needed yet) ─────────
def exercise_1b_simulate_agent_thinking():
    """
    EXERCISE: Trace through the agent thought process manually.
    
    This is called the ReAct (Reason + Act) pattern.
    Write out each step as if YOU were the agent.
    """
    
    agent_trace = {
        "thought_1": "I need to evaluate a candidate. First, I'll parse the resume.",
        "action_1": "CALL parse_resume(resume_text=SAMPLE_RESUME)",
        "observation_1": {
            "name": "John Smith",
            "email": "john.smith@email.com",
            "skills": ["Python", "FastAPI", "React", "PostgreSQL", "Redis", "Docker", "AWS"],
            "years_experience": 6,
            "current_role": "Senior Software Engineer"
        },
        
        "thought_2": "Now I have the parsed resume. Let me analyze the JD requirements.",
        "action_2": "CALL analyze_jd(jd_text=SAMPLE_JD)",
        "observation_2": {
            "required_skills": ["Python", "FastAPI/Django", "PostgreSQL", "AWS/GCP"],
            "min_experience": 4,
            "nice_to_have": ["Docker/Kubernetes", "Team leadership"]
        },
        
        "thought_3": "Now I can compare. John has ALL required skills and 6 years (>4 required).",
        "action_3": "CALL calculate_score(candidate=observation_1, requirements=observation_2)",
        "observation_3": {
            "skill_match": 95,
            "experience_match": "Exceeds",
            "recommendation": "STRONGLY RECOMMEND"
        },
        
        "final_answer": "John Smith is a STRONG candidate. 95% skill match. Recommend for interview."
    }
    
    return agent_trace


# ─── Exercise 1C: Design your first multi-agent flow ──────────────────────
def exercise_1c_design_multiagent_flow():
    """
    EXERCISE: Fill in the blanks for each agent's responsibility.
    Think about what INPUT each agent needs and what OUTPUT it produces.
    
    Answer key is provided below — try it yourself first!
    """
    
    # TODO: Fill in these blanks before looking at the answer key
    my_agent_design = {
        "agent_1": {
            "name": "Resume Parser Agent",
            "input":  "?????",  # What does it take as input?
            "output": "?????",  # What does it produce?
            "tools":  ["?????"] # What tools does it need?
        },
        "agent_2": {
            "name": "JD Analyzer Agent",
            "input":  "?????",
            "output": "?????",
            "tools":  ["?????"]
        },
        "agent_3": {
            "name": "Candidate Matching Agent",
            "input":  "?????",
            "output": "?????",
            "tools":  ["?????"]
        }
    }
    
    # ─── ANSWER KEY ───────────────────────────────────────────────────────
    answer_key = {
        "agent_1": {
            "name": "Resume Parser Agent",
            "input":  "Raw PDF resume file",
            "output": "Structured JSON (name, email, skills, experience)",
            "tools":  ["extract_pdf_text()", "llm_extract_structured_data()"]
        },
        "agent_2": {
            "name": "JD Analyzer Agent",
            "input":  "Raw job description text",
            "output": "Requirements dict (required skills, min experience, nice-to-haves)",
            "tools":  ["llm_analyze_jd()", "skill_taxonomy_lookup()"]
        },
        "agent_3": {
            "name": "Candidate Matching Agent",
            "input":  "Parsed resume + JD requirements",
            "output": "Match score (0-100), strengths, gaps, recommendation",
            "tools":  ["calculate_skill_overlap()", "llm_evaluate_fit()"]
        }
    }
    
    return answer_key


# ─────────────────────────────────────────────────────────────────────────────
# PHASE 1 QUIZ — Test Your Understanding
# ─────────────────────────────────────────────────────────────────────────────
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        PHASE 1 QUIZ (10 Questions)                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

Attempt the quiz before looking at answers. Score yourself.

Q1. What does "LLM" stand for?
    A) Large Learning Model
    B) Large Language Model  ✅
    C) Linear Logic Machine
    D) Low Latency Model

Q2. What is a "token" in the context of LLMs?
    A) An authentication key
    B) A unit of text (~0.75 words)  ✅
    C) A database record
    D) A network packet

Q3. What does "temperature=0" mean when calling an LLM?
    A) The model shuts down
    B) The model generates the most creative output
    C) The model generates the most deterministic/consistent output  ✅
    D) The model ignores the prompt

Q4. What is the PRIMARY advantage of a Multi-Agent System over a Single Agent?
    A) It uses less memory
    B) It is cheaper to run
    C) Specialization, parallelism, and fault isolation  ✅
    D) It requires no prompts

Q5. In RAG, what is stored in a Vector Database?
    A) SQL tables
    B) Raw PDF files
    C) Numerical vector representations (embeddings) of text  ✅
    D) API keys

Q6. What does LangGraph use to connect agents together?
    A) REST APIs
    B) Nodes and Edges (Graph structure)  ✅
    C) SQL joins
    D) WebSockets

Q7. What is the ReAct pattern?
    A) A React.js component pattern
    B) Reason + Act — the agent's think/act loop  ✅
    C) A retry mechanism for failed API calls
    D) A data validation pattern

Q8. What is the "context window" of an LLM?
    A) The visual area of the chat interface
    B) The maximum amount of text the LLM can process in one call  ✅
    C) The timeout for API requests
    D) The number of agents in the system

Q9. Which statement BEST describes LangChain's role?
    A) It is a vector database
    B) It is an LLM itself
    C) It is a framework providing building blocks for LLM apps  ✅
    D) It is a cloud hosting platform

Q10. In our Hiring Co-Pilot, what is the SUPERVISOR AGENT's job?
     A) Parse resumes
     B) Score candidates
     C) Orchestrate which agent runs next  ✅
     D) Send emails

────────────────────────────────────────
SCORING:
  9-10: Excellent! Ready for Phase 2.
  7-8:  Good. Review missed concepts.
  5-6:  Re-read concepts 4, 5, 7, 8.
  <5:   Re-read the entire Phase 1 lesson.
────────────────────────────────────────
"""

# ─────────────────────────────────────────────────────────────────────────────
# INTERVIEW QUESTIONS — Phase 1
# (Real questions asked at companies like Google, Microsoft, Anthropic)
# ─────────────────────────────────────────────────────────────────────────────
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║               PHASE 1 INTERVIEW QUESTIONS & MODEL ANSWERS                  ║
╚══════════════════════════════════════════════════════════════════════════════╝

─── BEGINNER LEVEL ────────────────────────────────────────────────────────────

Q: "Explain what an AI Agent is to a non-technical stakeholder."
A: "An AI Agent is like a smart digital employee. You give it a goal —
   like 'find the best candidates for this job' — and it figures out
   the steps to accomplish it, uses tools like searching databases or
   sending emails, and reports back with results. Unlike a simple
   chatbot that only answers questions, an agent can take autonomous
   multi-step actions."

Q: "What is the difference between LangChain and LangGraph?"
A: "LangChain provides the building blocks — LLM connectors, prompt
   templates, tools, and memory. LangGraph builds on LangChain to
   create complex, stateful workflows with multiple agents. Think of
   LangChain as individual LEGO bricks and LangGraph as the instruction
   manual for building a complex LEGO structure with those bricks."

─── INTERMEDIATE LEVEL ────────────────────────────────────────────────────────

Q: "When would you choose a Multi-Agent architecture over a single agent?"
A: "I'd choose Multi-Agent when: (1) the task is too complex for one
   context window, (2) subtasks can be parallelized for speed, (3) each
   subtask requires specialized expertise or different tools, or (4) I
   need fault isolation — if one agent fails, others continue. For simple
   Q&A or document summarization, a single agent is usually sufficient."

Q: "Explain RAG and its limitations."
A: "RAG augments LLM responses with retrieved external data, solving the
   knowledge cutoff problem. However, limitations include: (1) chunk
   quality — poor chunking degrades retrieval, (2) embedding model
   limitations — semantic search may miss exact matches, (3) context
   window constraints — you can only retrieve so much data, and
   (4) latency — each query requires a vector DB lookup before LLM call."

─── ADVANCED LEVEL ────────────────────────────────────────────────────────────

Q: "How would you handle hallucinations in a production recruitment AI system?"
A: "Multi-layered approach: (1) Structured output with JSON schemas — force
   the LLM to return validated formats. (2) Source attribution — require
   the agent to cite which part of the resume supports each claim.
   (3) Confidence scores — low confidence triggers human review.
   (4) Human-in-the-Loop checkpoints before any final hiring decision.
   (5) LangSmith tracing — log every LLM call to audit results.
   (6) Evaluation framework — run regression tests with known resume/JD
   pairs to catch model drift."

Q: "How does LangGraph's Human-in-the-Loop work at a technical level?"
A: "LangGraph uses interrupt() to pause workflow execution at a specific
   node. The state is checkpointed to a persistent store (like Redis or
   PostgreSQL). The workflow resumes when a human reviews and sends an
   approved signal via the update_state() method. This allows workflows
   that span hours or days — the state is persisted even if the server
   restarts."
"""

# ─────────────────────────────────────────────────────────────────────────────
# BEST PRACTICES — Phase 1
# ─────────────────────────────────────────────────────────────────────────────
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                          BEST PRACTICES                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝

1. PROMPT ENGINEERING
   ✅ Always specify a ROLE for the LLM (boosts accuracy 20-30%)
   ✅ Use structured output (JSON) — never parse free-form text in production
   ✅ Include few-shot examples in prompts for complex tasks
   ✅ Be explicit about edge cases ("if no skills found, return empty list")
   ❌ Never send raw user input directly to LLM (prompt injection risk!)

2. AGENT DESIGN
   ✅ One agent = one responsibility (Single Responsibility Principle)
   ✅ Design agents to be STATELESS where possible
   ✅ Add timeout and retry logic to every agent
   ✅ Log every agent action for debugging
   ❌ Don't make agents too fine-grained (overhead cost isn't worth it)

3. SECURITY (CRITICAL for HR systems)
   ✅ Never log PII (names, emails, phone numbers) in plain text logs
   ✅ Encrypt all candidate data at rest and in transit
   ✅ Implement RBAC (Role-Based Access Control) — not everyone sees all data
   ✅ Audit every AI decision for compliance (EEOC, GDPR)
   ❌ Never use AI score as the SOLE hiring criterion (legal liability)

4. MULTI-AGENT
   ✅ Always have a human checkpoint before final hiring decisions
   ✅ Design for agent failure — what happens if one agent is down?
   ✅ Use typed state (TypedDict) — prevents data corruption between agents
   ✅ Test each agent in isolation before integrating
"""

# ─────────────────────────────────────────────────────────────────────────────
# PHASE 2 PREVIEW
# ─────────────────────────────────────────────────────────────────────────────
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    ⏭  PHASE 2 PREVIEW: ENVIRONMENT SETUP                  ║
╚══════════════════════════════════════════════════════════════════════════════╝

In Phase 2 we will:
  1. ✅ Set up Python virtual environment
  2. ✅ Install all required packages (LangChain, LangGraph, FastAPI...)
  3. ✅ Configure MySQL database (installation + connection)
  4. ✅ Set up Redis (for caching and LangGraph checkpointing)
  5. ✅ Create GitHub repository for version control
  6. ✅ Create .env file with all configurations
  7. ✅ Run your FIRST working Python code that connects to OpenAI

By end of Phase 2:
  → Your machine will be 100% ready to build the platform
  → You'll understand WHY each tool is needed
  → You'll have a clean project folder structure

Let's build! 🚀
"""
