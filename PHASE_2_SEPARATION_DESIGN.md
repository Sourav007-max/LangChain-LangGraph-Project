# PHASE 2 — APPLICATION VS LEARNING SEPARATION
## Design Document (No Code Changes)

Date: 2026-08-28  
Based on: Phase 1 Audit Findings  
Status: **PLANNING ONLY — NO MODIFICATIONS YET**

---

## PART 1: COMPREHENSIVE INVENTORY & CATEGORIZATION

| # | Existing Item | Type | Current Location | Category | Proposed Location | Reason |
|---|---|---|---|---|---|---|
| 1 | `__init__.py` | File | Root | OPERATIONAL | Root | Package marker, required |
| 2 | `requirements.txt` | File | Root | OPERATIONAL | Root | Dependencies manifest, used by both app & learning |
| 3 | `pytest.ini` | File | Root | OPERATIONAL | Root | Test runner config, used for QA |
| 4 | `README.md` | File | Root | **MIXED** | Split (see below) | Contains both product intro & learning roadmap |
| 5 | `SETUP_GUIDE.md` | File | Root | LEARNING | `docs/guides/SETUP_GUIDE.md` | Installation instructions (for developers/learners) |
| 6 | `COURSE_OUTLINE.md` | File | Root | LEARNING | `docs/learning/COURSE_OUTLINE.md` | 14-phase learning curriculum |
| 7 | `INTERVIEW_PREP.md` | File | Root | LEARNING | `docs/learning/INTERVIEW_PREP.md` | Interview Q&A guide |
| 8 | `agents/` folder | Folder | Root/agents | OPERATIONAL | Root/agents | Core multi-agent workflow, product-critical |
| 9 | `agents/state.py` | File | agents/ | OPERATIONAL | agents/state.py | Shared state definition, used by all agents |
| 10 | `agents/graph.py` | File | agents/ | OPERATIONAL | agents/graph.py | LangGraph compilation & execution |
| 11 | `agents/jd_analyzer.py` | File | agents/ | OPERATIONAL | agents/jd_analyzer.py | Job requirement extraction agent |
| 12 | `agents/resume_parser.py` | File | agents/ | OPERATIONAL | agents/resume_parser.py | Resume parsing agent |
| 13 | `agents/candidate_matcher.py` | File | agents/ | OPERATIONAL | agents/candidate_matcher.py | Candidate scoring agent |
| 14 | `agents/shortlisting.py` | File | agents/ | OPERATIONAL | agents/shortlisting.py | Shortlist filtering (pure Python) |
| 15 | `agents/interview_scheduler.py` | File | agents/ | OPERATIONAL | agents/interview_scheduler.py | Interview question generation |
| 16 | `agents/reporter.py` | File | agents/ | OPERATIONAL | agents/reporter.py | Report generation agent |
| 17 | `backend/main.py` | File | backend/ | OPERATIONAL | backend/main.py | FastAPI REST API, product-critical |
| 18 | `frontend/` folder | Folder | Root/frontend | OPERATIONAL | Root/frontend | React + Streamlit user interfaces |
| 19 | `frontend/streamlit_app.py` | File | frontend/ | OPERATIONAL | frontend/streamlit_app.py | Prototype UI dashboard |
| 20 | `frontend/src/` folder | Folder | frontend/ | OPERATIONAL | frontend/src/ | React application code |
| 21 | `frontend/package.json` | File | frontend/ | OPERATIONAL | frontend/package.json | Node.js dependencies |
| 22 | `frontend/vite.config.ts` | File | frontend/ | OPERATIONAL | frontend/vite.config.ts | React build configuration |
| 23 | `frontend/tailwind.config.js` | File | frontend/ | OPERATIONAL | frontend/tailwind.config.js | Styling configuration |
| 24 | `frontend/src/App.tsx` | File | frontend/src/ | OPERATIONAL | frontend/src/App.tsx | React app root component |
| 25 | `frontend/src/pages/` | Folder | frontend/src/ | OPERATIONAL | frontend/src/pages/ | 6 UI pages (Login, Dashboard, etc.) |
| 26 | `frontend/src/components/` | Folder | frontend/src/ | OPERATIONAL | frontend/src/components/ | Reusable UI components |
| 27 | `frontend/src/services/` | Folder | frontend/src/ | OPERATIONAL | frontend/src/services/ | API clients |
| 28 | `frontend/src/store/` | Folder | frontend/src/ | OPERATIONAL | frontend/src/store/ | Zustand state management |
| 29 | `frontend/src/types/` | Folder | frontend/src/ | OPERATIONAL | frontend/src/types/ | TypeScript type definitions |
| 30 | `database/init_db.py` | File | database/ | OPERATIONAL | database/init_db.py | SQLAlchemy ORM models, product-critical |
| 31 | `database/sql/01_create_tables.sql` | File | database/sql/ | OPERATIONAL | database/sql/01_create_tables.sql | MySQL schema, product-critical |
| 32 | `config/settings.py` | File | config/ | OPERATIONAL | config/settings.py | LLM factory, API keys, configuration |
| 33 | `config/monitoring.py` | File | config/ | OPERATIONAL | config/monitoring.py | Agent logging, LangSmith integration |
| 34 | `tests/test_e2e_workflow.py` | File | tests/ | OPERATIONAL | tests/test_e2e_workflow.py | End-to-end workflow tests |
| 35 | `tests/test_integration.py` | File | tests/ | OPERATIONAL | tests/test_integration.py | Integration tests (real API + LLM) |
| 36 | `lessons/phase_01_ai_fundamentals/` | Folder | lessons/ | LEARNING | `docs/learning/phase_01_ai_fundamentals/` | AI fundamentals tutorial |
| 37 | `lessons/phase_02_environment_setup/` | Folder | lessons/ | LEARNING | `docs/learning/phase_02_environment_setup/` | Setup tutorial |
| 38 | `lessons/phase_03_api_keys/` | Folder | lessons/ | LEARNING | `docs/learning/phase_03_api_keys/` | API keys configuration tutorial |
| 39 | `lessons/phase_04_system_design/` | Folder | lessons/ | LEARNING | `docs/learning/phase_04_system_design/` | Architecture & system design tutorial |
| 40 | `lessons/phase_07_langgraph/` | Folder | lessons/ | LEARNING | `docs/learning/phase_07_langgraph/` | LangGraph fundamentals tutorial |
| 41 | `lessons/phase_10_rag_integration/` | Folder | lessons/ | LEARNING | `docs/learning/phase_10_rag_integration/` | RAG integration tutorial |

---

## PART 2: README.md SPLITTING STRATEGY

**Current README.md contains:**
1. Project overview (OPERATIONAL)
2. Architecture diagram (OPERATIONAL)
3. Tech stack table (OPERATIONAL)
4. Prerequisites (OPERATIONAL)
5. Setup steps (LEARNING)
6. API keys setup (LEARNING)
7. Running the app (OPERATIONAL)

**Proposed Split:**

### A. NEW: `README.md` (OPERATIONAL FOCUS)
**Purpose:** Quick start for users who want to USE the product

**Contents:**
- What is AI Hiring Co-Pilot? (2 paragraphs)
- Feature highlights (bullet list)
- Quick start (3 steps: clone → install → run)
- Demo credentials
- API documentation link
- Troubleshooting (quick reference)
- Link to learning docs

**Length:** ~150 lines

### B. NEW: `docs/guides/GETTING_STARTED.md` (LEARNING)
**Purpose:** Detailed setup for developers/learners

**Contents:**
- Installation (Windows/Mac/Linux with details)
- Dependency breakdown (what each library does)
- Configuration (.env setup with explanations)
- Running the backend
- Running the frontend
- Common issues & solutions

**Length:** ~300 lines (moved from SETUP_GUIDE.md)

### C. KEEP: `docs/learning/COURSE_OUTLINE.md` (LEARNING)
**Purpose:** Learning curriculum

**Contents:**
- 14-phase roadmap (unchanged)

### D. KEEP: `docs/learning/INTERVIEW_PREP.md` (LEARNING)
**Purpose:** Interview preparation

**Contents:**
- Interview Q&A (unchanged)

---

## PART 3: TARGET DIRECTORY STRUCTURE

```
LangChain-LangGraph-Project/
│
├── 📂 APPLICATION (Product Code)
│   ├── agents/                      # Core LangGraph workflow
│   │   ├── state.py                 # HiringState definition
│   │   ├── graph.py                 # Graph compilation
│   │   ├── jd_analyzer.py           # Agent 1
│   │   ├── resume_parser.py         # Agent 2
│   │   ├── candidate_matcher.py     # Agent 3
│   │   ├── shortlisting.py          # Agent 4
│   │   ├── interview_scheduler.py   # Agent 5
│   │   ├── reporter.py              # Agent 6
│   │   └── __init__.py
│   │
│   ├── backend/                     # FastAPI REST API
│   │   └── main.py                  # All endpoints
│   │
│   ├── frontend/                    # React + Streamlit UIs
│   │   ├── streamlit_app.py         # Prototype dashboard
│   │   ├── src/                     # React application
│   │   │   ├── pages/
│   │   │   ├── components/
│   │   │   ├── services/
│   │   │   ├── store/
│   │   │   ├── types/
│   │   │   ├── App.tsx
│   │   │   ├── main.tsx
│   │   │   └── index.css
│   │   ├── package.json
│   │   ├── vite.config.ts
│   │   ├── tailwind.config.js
│   │   ├── tsconfig.json
│   │   ├── postcss.config.js
│   │   └── index.html
│   │
│   ├── database/                    # Data models
│   │   ├── init_db.py               # ORM models + seeding
│   │   └── sql/
│   │       └── 01_create_tables.sql # MySQL schema
│   │
│   ├── config/                      # Configuration
│   │   ├── settings.py              # LLM factory, API keys
│   │   └── monitoring.py            # Logging, LangSmith
│   │
│   ├── tests/                       # Quality assurance
│   │   ├── test_e2e_workflow.py
│   │   └── test_integration.py
│   │
│   ├── uploads/                     # Resume file storage (runtime)
│   │   └── resumes/
│   │
│   ├── __init__.py
│   ├── requirements.txt              # Python dependencies
│   ├── pytest.ini                    # Test configuration
│   ├── .env                          # Local config (git-ignored)
│   └── .env.example                  # Config template
│
├── 📂 DOCS (Documentation)
│   │
│   ├── 📂 guides/                   # How-to guides
│   │   ├── GETTING_STARTED.md       # Installation & setup (was SETUP_GUIDE)
│   │   ├── QUICKSTART.md            # 5-minute quick start
│   │   ├── ARCHITECTURE.md          # System design overview
│   │   ├── API.md                   # REST API documentation
│   │   └── TROUBLESHOOTING.md       # Common issues & solutions
│   │
│   ├── 📂 learning/                 # Educational content
│   │   ├── COURSE_OUTLINE.md        # 14-phase curriculum (moved)
│   │   ├── INTERVIEW_PREP.md        # Interview Q&A (moved)
│   │   │
│   │   ├── phase_01_ai_fundamentals/
│   │   │   ├── 01_concepts.py
│   │   │   └── 02_exercises_quiz_interview.py
│   │   │
│   │   ├── phase_02_environment_setup/
│   │   │   └── 01_setup_guide.py
│   │   │
│   │   ├── phase_03_api_keys/
│   │   │   └── 01_api_keys_guide.py
│   │   │
│   │   ├── phase_04_system_design/
│   │   │   └── 01_system_design.py
│   │   │
│   │   ├── phase_07_langgraph/
│   │   │   └── 01_langgraph_fundamentals.py
│   │   │
│   │   └── phase_10_rag_integration/
│   │       └── 01_rag_implementation.py
│   │
│   └── README.md                    # Documentation index
│
├── README.md                         # Main project overview (OPERATIONAL-focused)
├── .gitignore
└── .env.example                      # Config template
```

---

## PART 4: TARGET NAVIGATION DESIGN

### A. FOR USERS (Want to Use the Product)

**Entry point:** Root `README.md`

**Navigation flow:**
```
README.md (project intro + quick start)
  ├─→ Run the app (3 commands)
  ├─→ See it in browser (localhost:5173)
  ├─→ Demo login (built-in credentials)
  ├─→ Try it:
  │    ├─ Create a job
  │    ├─ Upload resumes
  │    ├─ Run screening
  │    ├─ Review candidates
  │    └─ Schedule interviews
  │
  ├─→ Docs → API reference (for integrations)
  ├─→ Docs → Troubleshooting (if issues arise)
  └─→ GitHub Issues (for bug reports)
```

**Key principle:** Users should be able to run and use the product in <5 minutes without reading tutorials.

---

### B. FOR DEVELOPERS (Want to Understand How It Works)

**Entry point:** Root `README.md` → Link to `docs/guides/GETTING_STARTED.md`

**Navigation flow:**
```
docs/guides/GETTING_STARTED.md (setup details)
  ├─→ Installation (Windows/Mac/Linux)
  ├─→ Dependencies explained
  ├─→ Configuration (.env)
  ├─→ Running backend + frontend
  ├─→ Running tests
  │
  └─→ docs/guides/ARCHITECTURE.md (system overview)
       ├─→ Component diagram
       ├─→ Data flow
       ├─→ API endpoints
       └─→ Database schema
```

**Key principle:** Developers can understand the architecture without reading tutorials.

---

### C. FOR LEARNERS (Want to Learn AI/LangGraph/etc.)

**Entry point:** `docs/learning/COURSE_OUTLINE.md`

**Navigation flow:**
```
docs/learning/COURSE_OUTLINE.md (curriculum roadmap)
  ├─→ Phase 1: AI Fundamentals
  │    ├─ docs/learning/phase_01_ai_fundamentals/01_concepts.py
  │    └─ docs/learning/phase_01_ai_fundamentals/02_exercises_quiz_interview.py
  │
  ├─→ Phase 2: Environment Setup
  │    └─ docs/learning/phase_02_environment_setup/01_setup_guide.py
  │
  ├─→ Phase 3: API Keys
  │    └─ docs/learning/phase_03_api_keys/01_api_keys_guide.py
  │
  ├─→ Phase 4: System Design
  │    └─ docs/learning/phase_04_system_design/01_system_design.py
  │
  ├─→ Phase 7: LangGraph
  │    └─ docs/learning/phase_07_langgraph/01_langgraph_fundamentals.py
  │
  └─→ Phase 10: RAG Integration
       └─ docs/learning/phase_10_rag_integration/01_rag_implementation.py
```

**Key principle:** Learners follow the curriculum in order without being confused by product code.

---

### D. FOR INTERVIEWEES (Preparing for Job Interviews)

**Entry point:** `docs/learning/INTERVIEW_PREP.md`

**Navigation flow:**
```
docs/learning/INTERVIEW_PREP.md
  ├─→ Part 1: HR/Behavioural Questions
  │    ├─ "Tell me about this project"
  │    ├─ "Why did you build it?"
  │    ├─ "What's the most challenging part?"
  │    └─ (more Q&A)
  │
  ├─→ Part 2: Technical Deep Dives
  │    ├─ "Explain the LangGraph workflow"
  │    ├─ "How do you handle human-in-the-loop?"
  │    └─ (more Q&A)
  │
  └─→ Part 3: System Design Questions
       ├─ "How would you scale this?"
       ├─ "What production changes would you make?"
       └─ (more Q&A)
```

**Key principle:** Interviewees can prep by reading organized Q&A without being confused by tutorials.

---

## PART 5: FOLDER-LEVEL SEPARATION

### APPLICATION FILES (Currently Scattered)

**To stay in root:**
```
✓ requirements.txt      (lists both app + test dependencies)
✓ pytest.ini            (testing configuration)
✓ .env.example          (config template)
✓ README.md             (simplified, product-focused)
```

**To move/organize:**
```
❌ SETUP_GUIDE.md       → docs/guides/GETTING_STARTED.md
❌ COURSE_OUTLINE.md    → docs/learning/COURSE_OUTLINE.md
❌ INTERVIEW_PREP.md    → docs/learning/INTERVIEW_PREP.md
❌ lessons/             → docs/learning/
```

---

## PART 6: OPERATIONAL VS LEARNING CHECKLIST

### Must NOT Require Learning to Use Product
- ✅ Demo credentials pre-populated (no setup required)
- ✅ Can run `python -m backend.main` → works immediately
- ✅ Can visit localhost:5173 → React app loads
- ✅ Can see sample data (pre-seeded)
- ✅ Can create job → upload resume → run pipeline (no tutorials)
- ✅ Dashboard shows everything needed to use the app

### Learning Content Cleanly Separated
- ✅ All tutorials in `docs/learning/` (not in root)
- ✅ No docstrings in backend/frontend code (keep them focused)
- ✅ COURSE_OUTLINE explicitly links to phases
- ✅ Phase files can be run standalone (`python -m lessons.phase_01_ai_fundamentals.01_concepts`)
- ✅ Learners won't accidentally import app code when learning

---

## SUMMARY OF CHANGES

| What | Type | Impact | Priority |
|------|------|--------|----------|
| Move `lessons/` → `docs/learning/` | Folder rename | Low (internal structure) | HIGH |
| Move `SETUP_GUIDE.md` → `docs/guides/GETTING_STARTED.md` | File move | Low | HIGH |
| Move `COURSE_OUTLINE.md` → `docs/learning/COURSE_OUTLINE.md` | File move | Low | HIGH |
| Move `INTERVIEW_PREP.md` → `docs/learning/INTERVIEW_PREP.md` | File move | Low | HIGH |
| Simplify `README.md` (split content) | File edit | Medium (content reorganization) | HIGH |
| Create `docs/guides/ARCHITECTURE.md` | New file | Medium (new doc) | MEDIUM |
| Create `docs/guides/QUICKSTART.md` | New file | Medium (new doc) | MEDIUM |
| Create `docs/README.md` (navigation index) | New file | Low (new doc) | MEDIUM |
| No changes to operational code | N/A | None | N/A |
| No changes to backend/frontend/agents | N/A | None | N/A |
| No changes to database/config/tests | N/A | None | N/A |

---

## KEY PRINCIPLES FOR THIS SEPARATION

1. **Application runs without any tutorial** — User can use product immediately
2. **Learning is optional** — Tutorials are separate, never imported by app
3. **Clear navigation** — Each audience (user/developer/learner/interviewee) finds their path
4. **No circular dependencies** — Operational code never imports from `docs/`
5. **Single-purpose files** — Each file has one clear audience
6. **Minimal changes** — Mostly moving/organizing, not rewriting

---

## READY FOR PHASE 3

All items categorized. All locations proposed. All rationale provided.

**No code modifications made yet.**

Next phase: **Implement the reorganization** (move files, update imports, create new docs).
