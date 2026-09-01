# PHASE 4 — TARGET ARCHITECTURE DESIGN
## Clean Layered Architecture for AI Hiring Co-Pilot

Date: 2026-08-28  
Status: **DESIGN ONLY — NO IMPLEMENTATION YET**  
Based on: Phase 1 (Audit), Phase 2 (Separation), Phase 3 (Cleanup)

---

## PART 1: CURRENT ARCHITECTURE (AS-IS)

### Problems with Current Structure

```
LangChain-LangGraph-Project/  (MESSY)
├── agents/                            ← Core agents mixed with tests
├── backend/
│   └── main.py                        ← 350 lines, no separation of concerns
├── frontend/
│   ├── streamlit_app.py               ← Duplicate UI (500 lines)
│   └── src/                           ← React (production UI)
├── database/
│   └── init_db.py                     ← Models + unused Interview/Evaluation + seeding
├── config/
│   ├── settings.py                    ← Embedding config unused
│   └── monitoring.py
├── lessons/                           ← Learning mixed with root
├── tests/
├── SETUP_GUIDE.md                     ← Learning doc mixed with root
├── COURSE_OUTLINE.md                  ← Learning doc mixed with root
├── INTERVIEW_PREP.md                  ← Learning doc mixed with root
├── README.md                          ← Mixed product + learning
├── requirements.txt                   ← All deps (prod + dev + learner)
└── pytest.ini
```

### Issues Identified

1. **No separation of layers** — Backend mixes routes, auth, business logic, data access
2. **Code duplication** — Password hashing in 2 places, PDF extraction inline
3. **Unused code** — Interview/Evaluation models, email stub, embedding function
4. **Mixed concerns** — Learning content in root; Streamlit duplicate UI
5. **Monolithic backend** — All 350+ lines in single main.py
6. **Monolithic requirements** — Prod + dev + learner deps mixed

### Current Data Flow

```
Frontend (React + Streamlit duplicate)
  ↓ HTTP/REST
Backend (main.py: routes + auth + logic)
  ↓
Agents (graph.py calls 6 agents sequentially)
  ↓
LLM calls (via get_llm factory)
  ↓
Database (10 ORM models, including unused Interview/Evaluation)
```

---

## PART 2: TARGET ARCHITECTURE (CLEAN)

### Design Principles

1. **Layered architecture** — Clear separation: UI → Controllers → Business Logic → Data
2. **Single responsibility** — Each module has one reason to change
3. **DRY** — No code duplication; utilities extracted
4. **Clean imports** — No circular dependencies
5. **Testability** — Business logic independent of frameworks
6. **Operational focus** — Learning content completely separated

### Target Layered Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          FRONTEND LAYER                          │
├─────────────────────────────────────────────────────────────────┤
│  React UI (production)                                           │
│  ├── Pages (6: Login, Dashboard, Jobs, Workflow, Review, Int.)  │
│  ├── Components (Layout, ProtectedRoute, UI primitives)         │
│  ├── Services (API client, hiring services)                     │
│  ├── Store (Zustand auth + workflow state)                      │
│  └── Types (TypeScript interfaces)                              │
└─────────────────────────────────────────────────────────────────┘
                              ↓ HTTP/REST
┌─────────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER (API)                      │
├─────────────────────────────────────────────────────────────────┤
│  FastAPI Backend (backend/main.py)                              │
│  ├── Routes (auth, jobs, resumes, workflows, analytics)        │
│  └── Dependency injection (Depends on services + DB session)   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                  BUSINESS LOGIC LAYER                            │
├─────────────────────────────────────────────────────────────────┤
│  Agents (agents/graph.py + 6 agent nodes)                       │
│  ├── LangGraph workflow orchestration                           │
│  ├── State management (HiringState)                             │
│  ├── Conditional routing                                        │
│  └── Human-in-the-loop interrupt                                │
│                                                                  │
│  Config (config/settings.py)                                    │
│  ├── LLM factory (get_llm)                                      │
│  ├── Feature flags (SMTP_ENABLED, etc.)                         │
│  └── Validation (validate_config)                               │
│                                                                  │
│  Utilities (utils/)                                             │
│  ├── crypto.py (password hashing + verification)               │
│  ├── pdf_utils.py (PDF text extraction)                         │
│  └── validation.py (input schemas)                              │
│                                                                  │
│  Monitoring (config/monitoring.py)                              │
│  ├── Agent logging decorator                                    │
│  ├── Performance metrics                                        │
│  └── LangSmith integration                                      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                     DATA ACCESS LAYER                            │
├─────────────────────────────────────────────────────────────────┤
│  Database (database/)                                            │
│  ├── ORM Models (User, Job, Candidate, Resume, Application)    │
│  ├── Database initialization + seeding                         │
│  ├── SQLAlchemy session management                              │
│  └── Schema DDL (MySQL)                                         │
│                                                                  │
│  External APIs (agents/*)                                       │
│  └── LLM provider calls (via get_llm factory)                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    INFRASTRUCTURE LAYER                          │
├─────────────────────────────────────────────────────────────────┤
│  SQLite (dev) / MySQL (prod)                                    │
│  LLM APIs (Groq, Gemini, OpenAI, Anthropic)                     │
│  File storage (./uploads/resumes/)                              │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                   SEPARATE: LEARNING LAYER                       │
├─────────────────────────────────────────────────────────────────┤
│  Documentation (docs/)                                          │
│  ├── guides/ (GETTING_STARTED, ARCHITECTURE, API, etc.)        │
│  ├── learning/ (COURSE_OUTLINE, INTERVIEW_PREP, phase_*/)      │
│  └── README.md (doc index)                                      │
│                                                                  │
│  Requirements (multiple files)                                  │
│  ├── requirements.txt (production only)                         │
│  ├── requirements-dev.txt (testing + tools)                     │
│  └── requirements-rag.txt (learner RAG phase)                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## PART 3: DETAILED COMPONENT DESIGN

### LAYER 1: FRONTEND (UI)

**Responsibility:** User interface + client-side routing + state management

**Structure:**
```
frontend/
├── src/
│   ├── pages/                         # 6 route pages
│   │   ├── LoginPage.tsx              # Auth page
│   │   ├── DashboardPage.tsx          # KPIs + pipeline overview
│   │   ├── JobsPage.tsx               # Job CRUD
│   │   ├── WorkflowPage.tsx           # Resume upload + launch
│   │   ├── ReviewPage.tsx             # Human approval of shortlist
│   │   └── InterviewsPage.tsx         # Interview display
│   │
│   ├── components/                    # Reusable components
│   │   ├── Layout.tsx                 # App shell + nav
│   │   ├── ProtectedRoute.tsx         # Auth guard
│   │   └── ui/index.tsx               # Primitives (Badge, Avatar, etc.)
│   │
│   ├── services/                      # API clients
│   │   ├── api.ts                     # Axios instance + interceptors
│   │   └── hiring.ts                  # Hiring API methods
│   │
│   ├── store/                         # Global state
│   │   └── useStore.ts                # Zustand: auth + workflow
│   │
│   ├── types/                         # TypeScript interfaces
│   │   └── index.ts                   # Shared types
│   │
│   ├── App.tsx                        # Router setup
│   ├── main.tsx                       # React entry
│   └── index.css                      # Global styles
│
├── package.json                       # Dependencies
├── vite.config.ts                     # Build config
├── tsconfig.json                      # TypeScript config
├── tailwind.config.js                 # Styling
├── postcss.config.js                  # PostCSS
└── index.html                         # HTML entry

❌ REMOVED:
└── streamlit_app.py                   # Duplicate UI (was here)
```

**Dependencies:**
- React 18, React Router, Axios, Zustand, TailwindCSS, Lucide Icons, Recharts, react-hook-form, react-dropzone, react-hot-toast

**Key Flow:**
1. User logs in → Zustand stores token
2. User navigates → Protected routes check token
3. User interacts → API calls via axios (auto-adds JWT)
4. Workflow runs → Poll `/workflows/{thread_id}/state` → Display results
5. User reviews → Call `/workflows/{thread_id}/approve` → Show interviews + report

---

### LAYER 2: APPLICATION/API (Routes)

**Responsibility:** HTTP routing + request validation + response formatting

**Structure:**
```
backend/
├── main.py                            # FastAPI app + all routes (REFACTORED)
│
│   ROUTES:
│   ├── POST /api/v1/auth/register     # User registration
│   ├── POST /api/v1/auth/login        # User authentication
│   ├── GET  /api/v1/jobs              # List jobs
│   ├── POST /api/v1/jobs              # Create job
│   ├── GET  /api/v1/jobs/{id}         # Get job details
│   ├── POST /api/v1/resumes/upload    # Upload resume
│   ├── POST /api/v1/workflows/start   # Launch workflow
│   ├── GET  /api/v1/workflows/{id}/state  # Poll state
│   ├── POST /api/v1/workflows/{id}/approve # Human approval
│   ├── GET  /api/v1/analytics/dashboard   # Dashboard KPIs
│   ├── GET  /api/v1/monitoring/stats      # Agent performance
│   └── GET  /api/v1/monitoring/logs       # Recent logs
│
│   DEPENDENCIES:
│   ├── Pydantic schemas (LoginIn, JobIn, WorkflowStartIn, etc.)
│   ├── Auth helpers (→ moved to utils/crypto.py)
│   ├── Database session (Depends(get_db))
│   ├── Agents (run_workflow, resume_workflow, get_workflow_state)
│   ├── Config (LLM factory, settings)
│   └── Utilities (pdf_utils)
```

**Design Pattern:** 
- Each route is a thin handler (5-20 lines)
- Calls business logic layer (agents or utils)
- Returns JSON response

**Example route structure:**
```python
@app.post("/api/v1/workflows/start")
def start_workflow(
    body: WorkflowStartIn,
    u=Depends(require_role("recruiter", "admin")),
    db: Session = Depends(get_db),
):
    # 1. Validate input (body is Pydantic-validated)
    # 2. Load data from DB (job, resumes)
    # 3. Call business logic (run_workflow)
    # 4. Return result
    return {...}
```

---

### LAYER 3: BUSINESS LOGIC

#### 3A: AGENTS (Workflow Orchestration)

**Responsibility:** Multi-agent LangGraph workflow

**Structure:**
```
agents/
├── state.py                           # HiringState TypedDict (single source of truth)
│
├── graph.py                           # LangGraph compilation
│   ├── build_graph()                  # Compile StateGraph
│   ├── run_workflow()                 # Execute until interrupt
│   ├── resume_workflow()              # Resume after human decision
│   ├── get_workflow_state()           # Read checkpoint
│   └── Routing functions (conditional edges)
│
├── jd_analyzer.py                     # Agent 1: Extract job requirements
├── resume_parser.py                   # Agent 2: Parse resumes
├── candidate_matcher.py               # Agent 3: Score candidates
├── shortlisting.py                    # Agent 4: Filter by threshold
├── interview_scheduler.py             # Agent 5: Generate questions + links
├── reporter.py                        # Agent 6: Generate report
│
└── prompts.py                         # ✨ NEW: Centralized LLM prompts
    ├── JD_ANALYSIS_PROMPT
    ├── RESUME_PARSING_PROMPT
    ├── CANDIDATE_SCORING_PROMPT
    ├── INTERVIEW_QUESTIONS_PROMPT
    └── REPORT_GENERATION_PROMPT
```

**Data Flow:**
```
HiringState (empty)
  ↓ job_description_raw, resume_texts, resume_metadata
Agent 1: JD Analyzer
  ↓ job_requirements
Agent 2: Resume Parser
  ↓ parsed_resumes
Agent 3: Candidate Matcher
  ↓ candidate_scores (sorted)
Agent 4: Shortlisting
  ↓ shortlisted_candidates (filtered)
[INTERRUPT: Human Review]
  ↓ human_approved_candidates, human_decision
Agent 5: Interview Scheduler
  ↓ interview_schedule
Agent 6: Reporter
  ↓ final_report
END
```

#### 3B: CONFIG (Centralized Settings)

**Responsibility:** Configuration + validation + LLM factory

**Structure:**
```
config/
├── settings.py                        # Configuration
│   ├── LLM provider setup (GROQ, GEMINI, OPENAI, ANTHROPIC)
│   ├── Database URL
│   ├── API keys
│   ├── Feature flags (SMTP_ENABLED, LANGCHAIN_TRACING_V2, etc.)
│   ├── get_llm(temperature, provider)  # Factory method
│   ├── validate_config()              # Check required keys
│   └── [REMOVE: get_embeddings(), EMBEDDING_PROVIDER, etc. → move to requirements-rag.txt]
│
└── monitoring.py                      # Observability
    ├── log_agent(agent_name, action)  # Decorator for agent logging
    ├── get_langsmith_client()         # Optional LangSmith
    ├── get_agent_stats()              # Performance metrics
    └── get_recent_logs()              # Recent agent logs
```

#### 3C: UTILITIES (Shared Logic)

**Responsibility:** Reusable functions (DRY principle)

**Structure:**
```
utils/                                 # ✨ NEW folder
├── __init__.py
│
├── crypto.py                          # ✨ NEW: Password operations (extracted from 2 places)
│   ├── hash_password(plain) → hashed
│   └── verify_password(plain, hashed) → bool
│
├── pdf_utils.py                       # ✨ NEW: PDF extraction (extracted from backend)
│   └── extract_resume_text(file_path) → str
│
└── validation.py                      # Input validation schemas
    ├── LoginIn
    ├── RegisterIn
    ├── JobIn
    ├── WorkflowStartIn
    └── HumanApproveIn
```

---

### LAYER 4: DATA ACCESS

#### 4A: DATABASE (ORM Models)

**Responsibility:** Data persistence + ORM

**Structure:**
```
database/
├── __init__.py
│
├── init_db.py                         # ✏️ MODIFIED: Remove Interview + Evaluation
│   ├── Base (DeclarativeBase)
│   ├── get_db() dependency
│   │
│   ├── ORM Models (KEEP):
│   │   ├── User (auth)
│   │   ├── Job (job postings)
│   │   ├── Candidate (candidate info)
│   │   ├── Resume (resume files + metadata)
│   │   ├── Application (application tracking)
│   │   └── AgentLog (monitoring)
│   │
│   ├── ❌ REMOVED:
│   │   ├── Interview (unused, phase 2)
│   │   └── Evaluation (unused, phase 2)
│   │
│   ├── init_db() (create tables + seed data)
│   └── _hash_pw() [deprecated - use utils/crypto.py]
│
└── sql/
    └── 01_create_tables.sql           # ✏️ MODIFIED: Remove Interview + Evaluation DDL
```

**Design Pattern:**
- SQLAlchemy ORM models
- SQLite (dev), MySQL (prod)
- Session-per-request pattern (FastAPI dependency)

---

### LAYER 5: LEARNING & DOCUMENTATION

**Responsibility:** Educational content (completely separated)

**Structure:**
```
docs/                                  # ✨ NEW folder (moved from root)
│
├── README.md                          # ✨ NEW: Doc index + navigation
│
├── guides/                            # ✨ NEW: How-to guides
│   ├── GETTING_STARTED.md             # ✨ NEW (was SETUP_GUIDE.md)
│   │   └── Installation + configuration + running the app
│   ├── QUICKSTART.md                  # ✨ NEW: 5-minute intro
│   ├── ARCHITECTURE.md                # ✨ NEW: System design + diagrams
│   ├── API.md                         # ✨ NEW: REST API documentation
│   └── TROUBLESHOOTING.md             # ✨ NEW: Common issues + solutions
│
└── learning/                          # ✨ MOVED from lessons/
    ├── COURSE_OUTLINE.md              # ✨ MOVED: 14-phase curriculum
    ├── INTERVIEW_PREP.md              # ✨ MOVED: Interview Q&A
    │
    ├── phase_01_ai_fundamentals/      # ✨ MOVED: AI concepts
    ├── phase_02_environment_setup/    # ✨ MOVED: Setup tutorial
    ├── phase_03_api_keys/             # ✨ MOVED: API keys setup
    ├── phase_04_system_design/        # ✨ MOVED: Architecture tutorial
    ├── phase_07_langgraph/            # ✨ MOVED: LangGraph tutorial
    └── phase_10_rag_integration/      # ✨ MOVED: RAG tutorial
```

---

## PART 4: MIGRATION MAP

### File-by-File Mapping

| Current Location | Target Location | Change Type | Reason |
|---|---|---|---|
| `agents/state.py` | `agents/state.py` | **KEEP** | HiringState definition (no change) |
| `agents/graph.py` | `agents/graph.py` | **KEEP** | Workflow orchestration (no change) |
| `agents/jd_analyzer.py` | `agents/jd_analyzer.py` | **KEEP** | Agent 1 (no change) |
| `agents/resume_parser.py` | `agents/resume_parser.py` | **SIMPLIFY** | Make truncation configurable |
| `agents/candidate_matcher.py` | `agents/candidate_matcher.py` | **KEEP** | Agent 3 (no change) |
| `agents/shortlisting.py` | `agents/shortlisting.py` | **KEEP** | Agent 4 (no change) |
| `agents/interview_scheduler.py` | `agents/interview_scheduler.py` | **SIMPLIFY** | Make questions count configurable |
| `agents/reporter.py` | `agents/reporter.py` | **KEEP** | Agent 6 (no change) |
| — | `agents/prompts.py` | **✨ CREATE** | Centralized prompts (new) |
| `backend/main.py` | `backend/main.py` | **KEEP** (refactor) | Routes structure (keep as-is, just cleaner) |
| — | `utils/__init__.py` | **✨ CREATE** | Utilities package |
| `database/init_db.py` (password) | `utils/crypto.py` | **✨ EXTRACT** | DRY: password hashing |
| `backend/main.py` (PDF logic) | `utils/pdf_utils.py` | **✨ EXTRACT** | DRY: PDF extraction |
| `database/init_db.py` | `database/init_db.py` | **MODIFY** | Remove Interview + Evaluation models |
| `database/sql/01_create_tables.sql` | `database/sql/01_create_tables.sql` | **MODIFY** | Remove Interview + Evaluation DDL |
| `config/settings.py` | `config/settings.py` | **SIMPLIFY** | Move embedding stuff to requirements-rag.txt |
| `config/monitoring.py` | `config/monitoring.py` | **KEEP** | Monitoring (no change) |
| `frontend/streamlit_app.py` | — | **❌ DELETE** | Duplicate of React UI |
| `frontend/src/pages/*.tsx` | `frontend/src/pages/*.tsx` | **KEEP** | React pages (no change) |
| `frontend/src/components/*.tsx` | `frontend/src/components/*.tsx` | **KEEP** | React components (no change) |
| `frontend/package.json` | `frontend/package.json` | **MODIFY** | Remove class-variance-authority |
| `frontend/src/services/api.ts` | `frontend/src/services/api.ts` | **KEEP** | API client (no change) |
| `frontend/src/store/useStore.ts` | `frontend/src/store/useStore.ts` | **KEEP** | Zustand store (no change) |
| `tests/test_e2e_workflow.py` | `tests/test_e2e_workflow.py` | **KEEP** | Tests (no change) |
| `tests/test_integration.py` | `tests/test_integration.py` | **KEEP** | Tests (no change) |
| `lessons/` | `docs/learning/` | **📂 MOVE** | Learning content separation |
| `SETUP_GUIDE.md` | `docs/guides/GETTING_STARTED.md` | **📄 MOVE** | Learning documentation |
| `COURSE_OUTLINE.md` | `docs/learning/COURSE_OUTLINE.md` | **📄 MOVE** | Learning curriculum |
| `INTERVIEW_PREP.md` | `docs/learning/INTERVIEW_PREP.md` | **📄 MOVE** | Learning content |
| `README.md` | `README.md` | **✏️ SIMPLIFY** | Product-focused only (no learning content) |
| — | `docs/README.md` | **✨ CREATE** | Doc index |
| — | `docs/guides/QUICKSTART.md` | **✨ CREATE** | Quick start guide |
| — | `docs/guides/ARCHITECTURE.md` | **✨ CREATE** | Architecture guide |
| — | `docs/guides/API.md` | **✨ CREATE** | API documentation |
| — | `docs/guides/TROUBLESHOOTING.md` | **✨ CREATE** | Troubleshooting guide |
| `requirements.txt` | `requirements.txt` | **✏️ SPLIT** | Production dependencies only |
| — | `requirements-dev.txt` | **✨ CREATE** | Dev dependencies (pytest, etc.) |
| — | `requirements-rag.txt` | **✨ CREATE** | Learner RAG phase dependencies |
| `pytest.ini` | `pytest.ini` | **KEEP** | Test config (no change) |
| `.env.example` | `.env.example` | **KEEP** | Config template (no change) |

---

## PART 5: TARGET DIRECTORY TREE

```
LangChain-LangGraph-Project/
│
├── 📂 agents/                          ← KEEP (core business logic)
│   ├── __init__.py
│   ├── state.py                        ✓ HiringState
│   ├── graph.py                        ✓ Graph + execution
│   ├── jd_analyzer.py                  ✓ Agent 1
│   ├── resume_parser.py                ✏️ Simplify truncation config
│   ├── candidate_matcher.py            ✓ Agent 3
│   ├── shortlisting.py                 ✓ Agent 4
│   ├── interview_scheduler.py          ✏️ Simplify questions config
│   ├── reporter.py                     ✓ Agent 6
│   └── prompts.py                      ✨ NEW: Centralized prompts
│
├── 📂 backend/                         ← KEEP (API layer)
│   ├── __init__.py
│   └── main.py                         ✓ FastAPI routes
│
├── 📂 frontend/                        ← KEEP (UI layer)
│   ├── src/
│   │   ├── pages/                      ✓ 6 route pages
│   │   ├── components/                 ✓ Layout, ProtectedRoute, ui/
│   │   ├── services/                   ✓ API client + hiring services
│   │   ├── store/                      ✓ Zustand state
│   │   ├── types/                      ✓ TypeScript types
│   │   ├── App.tsx                     ✓ Router
│   │   ├── main.tsx                    ✓ React entry
│   │   └── index.css                   ✓ Styles
│   ├── package.json                    ✏️ Remove class-variance-authority
│   ├── vite.config.ts                  ✓ Build config
│   ├── tsconfig.json                   ✓ TS config
│   ├── tailwind.config.js              ✓ Tailwind
│   ├── postcss.config.js               ✓ PostCSS
│   └── index.html                      ✓ Entry
│   └── (❌ REMOVED: streamlit_app.py)
│
├── 📂 database/                        ← KEEP (data access)
│   ├── __init__.py
│   ├── init_db.py                      ✏️ Remove Interview+Evaluation models
│   └── sql/
│       └── 01_create_tables.sql        ✏️ Remove Interview+Evaluation DDL
│
├── 📂 config/                          ← KEEP (configuration)
│   ├── __init__.py
│   ├── settings.py                     ✏️ Simplify (move embedding stuff)
│   └── monitoring.py                   ✓ Agent logging
│
├── 📂 utils/                           ✨ NEW (shared utilities)
│   ├── __init__.py
│   ├── crypto.py                       ✨ NEW: Password hashing (DRY)
│   ├── pdf_utils.py                    ✨ NEW: PDF extraction (DRY)
│   └── validation.py                   ✓ Pydantic schemas
│
├── 📂 tests/                           ← KEEP (QA)
│   ├── __init__.py
│   ├── test_e2e_workflow.py            ✓ End-to-end tests
│   └── test_integration.py             ✓ Integration tests
│
├── 📂 uploads/                         ← Runtime: Resume storage
│   └── resumes/
│
├── 📂 docs/                            ✨ NEW (learning + guides)
│   ├── README.md                       ✨ NEW: Doc index
│   │
│   ├── 📂 guides/
│   │   ├── GETTING_STARTED.md          ✨ NEW (moved from SETUP_GUIDE.md)
│   │   ├── QUICKSTART.md               ✨ NEW: 5-min intro
│   │   ├── ARCHITECTURE.md             ✨ NEW: System design
│   │   ├── API.md                      ✨ NEW: REST API docs
│   │   └── TROUBLESHOOTING.md          ✨ NEW: Common issues
│   │
│   └── 📂 learning/                    ✨ MOVED (from lessons/)
│       ├── COURSE_OUTLINE.md           ✨ MOVED
│       ├── INTERVIEW_PREP.md           ✨ MOVED
│       ├── phase_01_ai_fundamentals/   ✨ MOVED
│       ├── phase_02_environment_setup/ ✨ MOVED
│       ├── phase_03_api_keys/          ✨ MOVED
│       ├── phase_04_system_design/     ✨ MOVED
│       ├── phase_07_langgraph/         ✨ MOVED
│       └── phase_10_rag_integration/   ✨ MOVED
│
├── README.md                            ✏️ SIMPLIFIED: Product focus only
├── __init__.py
├── requirements.txt                     ✏️ SPLIT: Prod only
├── requirements-dev.txt                 ✨ NEW: Dev dependencies
├── requirements-rag.txt                 ✨ NEW: Learner RAG phase
├── pytest.ini                           ✓ Test config
├── .env.example                         ✓ Config template
└── .gitignore                           ✓ Version control
```

---

## PART 6: REQUIREMENTS FILE ORGANIZATION

### Current: requirements.txt (Mixed)
```
All 40+ dependencies together (prod + dev + learner)
```

### Target: Split into 3 Files

#### requirements.txt (PRODUCTION)
```
# Core production dependencies only

# LangChain/LLM
langchain>=0.3.0
langchain-core>=0.3.0
langgraph>=0.2.0
langchain-groq>=0.1.0
langchain-google-genai>=1.0.0

# Optional: Paid LLMs
langchain-openai>=0.1.0
langchain-anthropic>=0.1.0

# Optional: Production database
pymysql>=1.1.0

# Optional: Monitoring
langsmith>=0.1.0

# Web framework
fastapi>=0.110.0
uvicorn[standard]>=0.27.0

# Database
sqlalchemy>=2.0.0

# Auth
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4

# File processing
pypdf>=4.0.0

# Utilities
pydantic>=2.6.0
python-dotenv>=1.0.0
```

#### requirements-dev.txt (DEVELOPMENT)
```
-r requirements.txt

# Testing
pytest>=8.0.0
pytest-asyncio>=0.23.0
pytest-cov>=5.0.0

# HTTP client for tests
httpx>=0.27.0
```

#### requirements-rag.txt (LEARNER RAG PHASE)
```
-r requirements.txt

# Vector databases for phase_10
chromadb>=0.5.0
pinecone>=3.0.0

# Web search API
tavily-python>=0.3.0
```

---

## PART 7: API STRUCTURE (No Changes)

**Routing remains same; just cleaner backend code:**

```
POST   /api/v1/auth/register
POST   /api/v1/auth/login
GET    /api/v1/jobs
POST   /api/v1/jobs
GET    /api/v1/jobs/{id}
POST   /api/v1/resumes/upload
POST   /api/v1/workflows/start
GET    /api/v1/workflows/{id}/state
POST   /api/v1/workflows/{id}/approve
GET    /api/v1/analytics/dashboard
GET    /api/v1/monitoring/stats
GET    /api/v1/monitoring/logs
GET    /health
```

---

## PART 8: DEPENDENCY GRAPH

### No Circular Dependencies ✓

```
Frontend
  └─→ API (axios)
       └─→ Backend (FastAPI)
            ├─→ Agents (LangGraph)
            │   └─→ Config (LLM factory)
            │        └─→ External APIs (LLMs)
            ├─→ Database (SQLAlchemy)
            │   └─→ Infrastructure (SQLite/MySQL)
            └─→ Utils (crypto, pdf)

Separate Learning Layer
  └─→ Docs (static content, no runtime dependencies)
```

**Key: No bidirectional dependencies. Clean one-way flow.**

---

## PART 9: CHANGES SUMMARY

| Category | Count | Type | Impact |
|----------|-------|------|--------|
| Files to KEEP | 85+ | Structure | No work |
| Files to MOVE | 8 | Structure | Low risk (file moves) |
| Files to CREATE | 10 | New | Medium effort |
| Files to DELETE | 1 | Removal | Low (duplicate UI) |
| Files to MODIFY | 8 | Edits | Medium (clean code) |
| **TOTAL** | **112+** | **Mix** | **Clean & Organized** |

---

## PART 10: IMPLEMENTATION ORDER (For Phase 5)

**Recommended sequence (minimum risk, maximum value):**

1. **Phase 5A** — Extract utilities (crypto.py, pdf_utils.py)
   - Low risk, high reuse
   - Enables DRY principle
   - ~2 hours

2. **Phase 5B** — Modify database models (remove Interview+Evaluation)
   - Low risk, high cleanup
   - No code depends on them
   - ~1 hour

3. **Phase 5C** — Move learning content to docs/
   - No risk (file moves only)
   - Separation of concerns
   - ~1 hour

4. **Phase 5D** — Split requirements.txt
   - No risk (additive)
   - Better dependency management
   - ~30 minutes

5. **Phase 5E** — Delete Streamlit duplicate
   - No risk (no dependencies)
   - UI consolidation
   - ~15 minutes

6. **Phase 5F** — Simplify agent configs
   - Low risk (new env vars)
   - Flexibility improvement
   - ~1 hour

7. **Phase 5G** — Create documentation files
   - No risk (new content)
   - User experience improvement
   - ~2-3 hours (writing)

**Total effort:** ~8-10 hours  
**Total risk:** LOW  
**Total value:** HIGH

---

## COMPARISON: CURRENT VS TARGET

### Current Problems

```
❌ No clear separation of layers
❌ Duplicate code (password hashing, PDF extraction)
❌ Unused code (Interview, Evaluation models)
❌ Duplicate UI (Streamlit + React)
❌ Learning mixed with operational code
❌ Mixed dependencies (prod + dev + learner)
❌ Monolithic backend (all routes in one file)
❌ No clear component responsibilities
```

### Target Benefits

```
✅ Clear layered architecture (UI → API → Logic → Data)
✅ DRY: Utilities extracted to single location
✅ Clean: Unused code removed
✅ Single UI: React only (production-ready)
✅ Separation: Learning in docs/, operational in app/
✅ Organized: Dependencies split by purpose
✅ Maintainable: Each module has one responsibility
✅ Testable: Business logic isolated from framework
```

---

## STATUS

| Phase | Task | Status |
|-------|------|--------|
| Phase 1 | Audit | ✅ Complete |
| Phase 2 | Separation Design | ✅ Complete |
| Phase 3 | Cleanup Audit | ✅ Complete |
| Phase 4 | Architecture Design | ✅ **COMPLETE** |
| Phase 5 | **Implementation** | ⏳ Next |

**Architecture document saved:** `PHASE_4_TARGET_ARCHITECTURE.md`

**No code modifications made. Design is ready for Phase 5 implementation.**
