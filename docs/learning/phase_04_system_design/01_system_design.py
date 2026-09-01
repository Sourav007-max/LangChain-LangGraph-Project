"""
=============================================================================
  PHASE 4 — SYSTEM DESIGN
  AI Hiring Co-Pilot: Multi-Agent Recruitment Platform using LangGraph
=============================================================================

This phase teaches you to THINK before you CODE.
System Design is the most important skill for senior engineers.
It answers: "WHAT are we building and HOW should it work?"
=============================================================================
"""

# ─────────────────────────────────────────────────────────────────────────────
# STEP 1 — REQUIREMENTS GATHERING
# ─────────────────────────────────────────────────────────────────────────────
"""
FUNCTIONAL REQUIREMENTS (What the system MUST do):
────────────────────────────────────────────────────
  FR-01: Recruiters can upload job descriptions (PDF/text)
  FR-02: Recruiters can upload candidate resumes (PDF/DOCX)
  FR-03: System parses resumes and extracts structured data
  FR-04: System analyzes JD and extracts requirements
  FR-05: System ranks candidates against JD with scores (0-100)
  FR-06: System generates AI explanations for each score
  FR-07: Recruiter can approve/reject shortlisted candidates
  FR-08: System auto-schedules interviews via email
  FR-09: Interviewers submit feedback through the platform
  FR-10: System generates final evaluation and recommendation
  FR-11: Dashboard shows pipeline analytics
  FR-12: Full audit trail of all AI decisions

NON-FUNCTIONAL REQUIREMENTS (How well it must work):
──────────────────────────────────────────────────────
  NFR-01: Process 100 resumes in < 5 minutes
  NFR-02: API response time < 2 seconds (95th percentile)
  NFR-03: System uptime 99.9% (8.7 hours downtime/year)
  NFR-04: Support 50 concurrent recruiters
  NFR-05: All PII data encrypted at rest and in transit
  NFR-06: GDPR compliant — candidates can request data deletion
  NFR-07: Bias detection report for every hiring decision
  NFR-08: All agent decisions auditable and explainable

USER STORIES (Who does what and why):
───────────────────────────────────────
  As a RECRUITER, I want to upload a JD and 50 resumes,
  so that I get a ranked shortlist in minutes instead of hours.

  As a HIRING MANAGER, I want to see AI scores WITH explanations,
  so that I can make informed decisions with full transparency.

  As a CANDIDATE, I want to receive timely interview invitations,
  so that I have a positive experience with the company.

  As a COMPLIANCE OFFICER, I want a full audit trail of AI decisions,
  so that I can demonstrate fair hiring practices to regulators.
"""

# ─────────────────────────────────────────────────────────────────────────────
# STEP 2 — COMPLETE SYSTEM ARCHITECTURE
# ─────────────────────────────────────────────────────────────────────────────
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║              AI HIRING CO-PILOT — COMPLETE ARCHITECTURE                    ║
╚══════════════════════════════════════════════════════════════════════════════╝

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                        CLIENT LAYER                                     │
  │                                                                         │
  │   ┌──────────────────────────────┐  ┌─────────────────────────────┐    │
  │   │   React + TypeScript         │  │  Streamlit (Prototype)      │    │
  │   │   + Tailwind + ShadCN        │  │  (Quick testing dashboard)  │    │
  │   │   Port: 3000                 │  │  Port: 8501                 │    │
  │   └──────────────────────────────┘  └─────────────────────────────┘    │
  └─────────────────────────────┬───────────────────────────────────────────┘
                                │  HTTPS / REST API
  ┌─────────────────────────────▼───────────────────────────────────────────┐
  │                       API GATEWAY LAYER                                 │
  │                                                                         │
  │              FastAPI Backend (Python)  Port: 8000                       │
  │              ┌──────────────────────────────────────┐                   │
  │              │  Auth (JWT) │ Rate Limiting │ CORS   │                   │
  │              │  Routing   │ Logging       │ Docs   │                   │
  │              └──────────────────────────────────────┘                   │
  └──────┬────────────────────┬────────────────────┬───────────────────────┘
         │                    │                    │
  ┌──────▼──────┐   ┌─────────▼──────┐   ┌────────▼────────┐
  │  File API   │   │  Recruitment   │   │   Analytics     │
  │  /upload    │   │  API /jobs     │   │   API /reports  │
  │  /parse     │   │  /candidates   │   │   /metrics      │
  └──────┬──────┘   └─────────┬──────┘   └────────┬────────┘
         │                    │                    │
  ┌──────▼────────────────────▼────────────────────▼────────────────────────┐
  │                     LANGGRAPH AGENT LAYER                                │
  │                                                                         │
  │  ┌─────────────────────────────────────────────────────────────────┐    │
  │  │                    SUPERVISOR AGENT                              │    │
  │  │          (Routes tasks to specialized agents)                   │    │
  │  └────┬──────────┬──────────┬──────────┬──────────┬───────────────┘    │
  │       │          │          │          │          │                     │
  │  ┌────▼───┐ ┌────▼───┐ ┌───▼────┐ ┌───▼────┐ ┌───▼────┐              │
  │  │Resume  │ │  JD    │ │Candid. │ │Sched.  │ │Eval.   │              │
  │  │Parser  │ │Analyz. │ │Matcher │ │Agent   │ │Agent   │              │
  │  └────┬───┘ └────┬───┘ └───┬────┘ └───┬────┘ └───┬────┘              │
  │       └──────────┴──────────┴──────────┴──────────┘                    │
  │                           │                                             │
  │  ┌────────────────────────▼────────────────────────────────────────┐   │
  │  │  HUMAN-IN-THE-LOOP CHECKPOINT                                   │   │
  │  │  (Recruiter reviews and approves/rejects AI recommendations)    │   │
  │  └────────────────────────┬────────────────────────────────────────┘   │
  │                           │                                             │
  │  ┌────────────────────────▼────────────────────────────────────────┐   │
  │  │  REPORTING AGENT → Final Report Generation                      │   │
  │  └─────────────────────────────────────────────────────────────────┘   │
  └──────────────────────────────────────────────────────────────────────────┘
         │                    │                    │
  ┌──────▼──────┐   ┌─────────▼──────┐   ┌────────▼────────┐
  │   MySQL DB  │   │  Pinecone      │   │  Redis Cache    │
  │  (Structured│   │  Vector DB     │   │  + LangGraph    │
  │   Data)     │   │  (Embeddings)  │   │  Checkpoints    │
  └─────────────┘   └────────────────┘   └─────────────────┘
         │                                       │
  ┌──────▼───────────────────────────────────────▼────────────────────────┐
  │                      MONITORING LAYER                                  │
  │                                                                        │
  │   LangSmith (Agent Traces)  │  Prometheus  │  Grafana Dashboards      │
  └────────────────────────────────────────────────────────────────────────┘


AGENT INTERACTION FLOW DIAGRAM:
─────────────────────────────────

  Recruiter
     │
     │ 1. Upload JD + Resumes
     ▼
  ┌─────────────────────────────────────────────────────────────────────┐
  │                         FastAPI Backend                             │
  │  • Validates files                                                  │
  │  • Stores in DB + file system                                       │
  │  • Triggers LangGraph workflow                                      │
  └──────────────────────────────┬──────────────────────────────────────┘
                                 │ 2. Start workflow
                                 ▼
                         ┌───────────────┐
                         │  SUPERVISOR   │
                         │    AGENT      │
                         └───────┬───────┘
                                 │ 3. Route to parsers
               ┌─────────────────┼──────────────────┐
               │                 │                  │
               ▼                 ▼                  ▼
       ┌──────────────┐ ┌───────────────┐  (parallel execution)
       │ Resume Parser│ │  JD Analyzer  │
       │ Agent        │ │  Agent        │
       │              │ │               │
       │ Input: PDF   │ │ Input: JD text│
       │ Output: JSON │ │ Output: reqs  │
       └──────┬───────┘ └───────┬───────┘
              │                 │
              └────────┬────────┘
                       │ 4. Parsed data stored in shared state
                       ▼
               ┌───────────────┐
               │   CANDIDATE   │
               │   MATCHING    │
               │     AGENT     │
               │               │
               │ Uses Pinecone │
               │ for semantic  │
               │ search        │
               └───────┬───────┘
                       │ 5. Scored candidates list
                       ▼
               ┌───────────────┐
               │    RANKING    │
               │     AGENT     │
               │               │
               │ Ranks top N   │
               │ candidates    │
               └───────┬───────┘
                       │ 6. Ranked shortlist
                       ▼
               ┌───────────────┐
               │ HUMAN-IN-THE  │ ◄── RECRUITER REVIEWS HERE
               │   LOOP        │     Approve / Reject / Ask for more
               └───────┬───────┘
                       │ 7. Approved candidates
                       ▼
               ┌───────────────┐
               │   INTERVIEW   │
               │  SCHEDULER    │
               │    AGENT      │
               │               │
               │ Sends emails  │
               │ Checks avail. │
               └───────┬───────┘
                       │ 8. Interviews scheduled
                       ▼
               ┌───────────────┐
               │  EVALUATION   │
               │    AGENT      │
               │               │
               │ Post-interview│
               │ assessment    │
               └───────┬───────┘
                       │ 9. Evaluation complete
                       ▼
               ┌───────────────┐
               │   REPORTING   │
               │    AGENT      │
               │               │
               │ Final hiring  │
               │ recommendation│
               └───────────────┘
"""

# ─────────────────────────────────────────────────────────────────────────────
# STEP 3 — PROJECT FOLDER STRUCTURE
# ─────────────────────────────────────────────────────────────────────────────
"""
ai-hiring-copilot/
│
├── .env                          # API keys (never commit!)
├── .env.example                  # Template (safe to commit)
├── .gitignore
├── requirements.txt
├── README.md
│
├── backend/                      # FastAPI Backend
│   ├── main.py                   # FastAPI app entry point
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py           # Pydantic Settings config
│   │   └── database.py           # MySQL + SQLAlchemy connection
│   │
│   ├── api/                      # API route handlers
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py           # Login, register, token
│   │   │   ├── jobs.py           # Job CRUD endpoints
│   │   │   ├── candidates.py     # Candidate CRUD endpoints
│   │   │   ├── resumes.py        # Resume upload + parsing
│   │   │   ├── applications.py   # Application management
│   │   │   ├── interviews.py     # Interview scheduling
│   │   │   └── reports.py        # Analytics + reports
│   │
│   ├── models/                   # SQLAlchemy database models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── job.py
│   │   ├── candidate.py
│   │   ├── resume.py
│   │   ├── application.py
│   │   ├── interview.py
│   │   ├── evaluation.py
│   │   └── agent_log.py
│   │
│   ├── schemas/                  # Pydantic request/response schemas
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── job.py
│   │   ├── candidate.py
│   │   └── resume.py
│   │
│   ├── services/                 # Business logic layer
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── job_service.py
│   │   ├── candidate_service.py
│   │   └── workflow_service.py   # Triggers LangGraph workflows
│   │
│   └── middleware/
│       ├── auth_middleware.py
│       ├── rate_limiter.py
│       └── error_handler.py
│
├── agents/                       # LangGraph Agent System
│   ├── __init__.py
│   ├── state.py                  # Shared HiringState TypedDict
│   ├── graph.py                  # LangGraph workflow definition
│   │
│   ├── supervisor/
│   │   ├── __init__.py
│   │   └── supervisor_agent.py
│   │
│   ├── resume_parser/
│   │   ├── __init__.py
│   │   ├── parser_agent.py
│   │   ├── pdf_extractor.py
│   │   └── prompts.py
│   │
│   ├── jd_analyzer/
│   │   ├── __init__.py
│   │   ├── analyzer_agent.py
│   │   └── prompts.py
│   │
│   ├── candidate_matcher/
│   │   ├── __init__.py
│   │   ├── matcher_agent.py
│   │   └── prompts.py
│   │
│   ├── interview_scheduler/
│   │   ├── __init__.py
│   │   ├── scheduler_agent.py
│   │   ├── email_sender.py
│   │   └── prompts.py
│   │
│   ├── evaluator/
│   │   ├── __init__.py
│   │   ├── evaluator_agent.py
│   │   └── prompts.py
│   │
│   └── reporter/
│       ├── __init__.py
│       ├── reporter_agent.py
│       └── prompts.py
│
├── tools/                        # LangChain Tools
│   ├── __init__.py
│   ├── pdf_tools.py              # PDF extraction tools
│   ├── database_tools.py         # MySQL query tools
│   ├── vector_store_tools.py     # Pinecone search tools
│   ├── email_tools.py            # Email sending tools
│   └── search_tools.py           # Tavily/SerpAPI tools
│
├── database/
│   ├── migrations/               # Alembic migrations
│   │   └── versions/
│   ├── alembic.ini
│   └── sql/
│       ├── 01_create_tables.sql
│       ├── 02_indexes.sql
│       └── 03_sample_data.sql
│
├── frontend/                     # React Application
│   ├── package.json
│   ├── src/
│   │   ├── App.tsx
│   │   ├── pages/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── services/             # API calls to FastAPI
│   │   └── store/                # State management
│   └── public/
│
├── tests/
│   ├── unit/
│   │   ├── test_resume_parser.py
│   │   └── test_jd_analyzer.py
│   ├── integration/
│   │   └── test_workflow.py
│   └── fixtures/
│       ├── sample_resumes/
│       └── sample_jds/
│
├── scripts/
│   ├── setup_db.py               # Initialize database
│   ├── seed_data.py              # Add sample data
│   └── test_connections.py       # Verify all connections
│
└── lessons/                      # This course content (you are here)
    ├── phase_01_ai_fundamentals/
    ├── phase_02_environment_setup/
    ├── phase_03_api_keys/
    ├── phase_04_system_design/    ← current
    └── ...
"""

# ─────────────────────────────────────────────────────────────────────────────
# PHASE 4 INTERVIEW QUESTIONS
# ─────────────────────────────────────────────────────────────────────────────
"""
Q: "How would you design a scalable multi-agent recruitment platform?"

MODEL ANSWER:
  "I'd use a microservices-inspired approach with LangGraph orchestration.
  The key design decisions are:
  
  1. SEPARATION OF CONCERNS: Each agent handles one task — parse, match,
     evaluate. This allows independent scaling and testing.
  
  2. SHARED STATE: LangGraph's state machine pattern ensures all agents
     work from a single source of truth, preventing data inconsistency.
  
  3. ASYNC PROCESSING: Resume processing via Celery workers — 100 resumes
     processed in parallel, not sequentially.
  
  4. HUMAN CHECKPOINTS: Before any hiring decision, a human must approve.
     This is both ethical and legally required in many jurisdictions.
  
  5. VECTOR SEARCH: Pinecone for semantic resume matching — finds
     'Machine Learning Engineer' even when resume says 'AI Specialist'.
  
  6. OBSERVABILITY: LangSmith tracing on every agent call — essential
     for debugging and demonstrating compliance to auditors."

Q: "What are the main technical risks in an AI hiring platform?"

MODEL ANSWER:
  "Three primary risks:
  
  1. BIAS: LLMs trained on historical data may perpetuate historical biases.
     Mitigation: Bias audit agent, diverse training data, human oversight.
  
  2. HALLUCINATION: LLM might generate false candidate qualifications.
     Mitigation: Always cite source from resume, structured JSON output,
     confidence scores with human review threshold.
  
  3. DATA PRIVACY: Resumes contain highly sensitive PII.
     Mitigation: Encryption at rest/transit, data minimization,
     right-to-deletion workflow, GDPR compliance audit."
"""
