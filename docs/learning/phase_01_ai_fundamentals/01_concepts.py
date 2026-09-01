"""
=============================================================================
  PHASE 1 — AI FUNDAMENTALS
  AI Hiring Co-Pilot: Multi-Agent Recruitment Platform using LangGraph
=============================================================================

LESSON STRUCTURE:
  1. What is AI?
  2. What are LLMs?
  3. What is Generative AI?
  4. What are Agents?
  5. Single Agent vs Multi-Agent Systems
  6. What is RAG?
  7. What is LangChain?
  8. What is LangGraph?
  9. Why companies are adopting agentic workflows

EXERCISES, QUIZ, INTERVIEW QUESTIONS — included at the end.
=============================================================================
"""

# ─────────────────────────────────────────────────────────────────────────────
# CONCEPT 1 — WHAT IS ARTIFICIAL INTELLIGENCE?
# ─────────────────────────────────────────────────────────────────────────────
"""
DEFINITION (Plain English):
────────────────────────────
Artificial Intelligence (AI) is the science of making computers that can
THINK, LEARN, and MAKE DECISIONS — tasks previously only done by humans.

Real-World Analogy:
───────────────────
  A new HR recruiter joins a company.
  Day 1  → reads the job description
  Day 2  → learns how to shortlist resumes
  Day 30 → starts screening candidates automatically

  AI does the SAME thing — it "learns" from data and then acts on new input.

Three Pillars of AI:
─────────────────────
  1. DATA      → fuel for AI (resumes, job descriptions, feedback)
  2. ALGORITHMS → the "brain" that learns patterns
  3. COMPUTE   → the hardware (GPU/CPU) that processes data

AI Sub-fields Relevant to Our Project:
────────────────────────────────────────
  ┌─────────────────────────────────────────────────────┐
  │                   Artificial Intelligence           │
  │  ┌───────────────────────────────────────────────┐  │
  │  │           Machine Learning (ML)               │  │
  │  │  ┌─────────────────────────────────────────┐  │  │
  │  │  │      Deep Learning (Neural Networks)    │  │  │
  │  │  │  ┌───────────────────────────────────┐  │  │  │
  │  │  │  │  Generative AI  ← WE ARE HERE    │  │  │  │
  │  │  │  │  (LLMs, GPT, Claude, Gemini)     │  │  │  │
  │  │  │  └───────────────────────────────────┘  │  │  │
  │  │  └─────────────────────────────────────────┘  │  │
  │  └───────────────────────────────────────────────┘  │
  └─────────────────────────────────────────────────────┘

Industry Insight (REAL):
─────────────────────────
  - LinkedIn uses AI to match candidates to jobs
  - Workday uses AI to rank applicants
  - HireVue uses AI to evaluate video interviews
  - Our project will build a CUSTOM version of these tools!
"""

# ─────────────────────────────────────────────────────────────────────────────
# CONCEPT 2 — WHAT ARE LARGE LANGUAGE MODELS (LLMs)?
# ─────────────────────────────────────────────────────────────────────────────
"""
DEFINITION:
────────────
An LLM (Large Language Model) is an AI model trained on BILLIONS of text
documents that can UNDERSTAND and GENERATE human language.

How LLMs Work (Simplified):
─────────────────────────────
  Input Text (Prompt)
        │
        ▼
  ┌─────────────────────────────────────────────────┐
  │          TOKENIZATION                           │
  │  "Parse this resume" → [Parse][this][resume]   │
  └─────────────────────────────────────────────────┘
        │
        ▼
  ┌─────────────────────────────────────────────────┐
  │          TRANSFORMER ARCHITECTURE               │
  │  Attention Mechanism → understands context      │
  │  Billions of parameters → stores "knowledge"    │
  └─────────────────────────────────────────────────┘
        │
        ▼
  Output Text (Response / Completion)

Key LLMs We'll Use:
────────────────────
  ┌─────────────────┬─────────────────┬─────────────────────┐
  │   Model         │  Company        │  Best For           │
  ├─────────────────┼─────────────────┼─────────────────────┤
  │ GPT-4o          │ OpenAI          │ General reasoning   │
  │ Claude 3.5      │ Anthropic       │ Long docs/analysis  │
  │ Gemini 1.5 Pro  │ Google          │ Multimodal tasks    │
  │ Llama 3 (Groq)  │ Meta/Groq       │ Fast, cheap tasks   │
  └─────────────────┴─────────────────┴─────────────────────┘

LLM Capabilities in Our Platform:
───────────────────────────────────
  ✅ Parse resume text → extract name, skills, experience
  ✅ Analyze job descriptions → identify required skills
  ✅ Score candidates → compare resume vs JD
  ✅ Generate interview questions → based on candidate profile
  ✅ Write evaluation reports → human-readable summaries

Key Concepts to Know:
──────────────────────
  • PROMPT   → the input you send to the LLM
  • CONTEXT WINDOW → max tokens the LLM can "see" at once
               GPT-4o: 128K tokens (~96,000 words)
               Claude 3.5: 200K tokens
  • TEMPERATURE → controls creativity (0=deterministic, 1=creative)
  • TOKENS   → ~0.75 words per token (how LLMs measure text)

Common Mistake ⚠️:
───────────────────
  DON'T think LLMs "know" real-time information.
  They have a TRAINING CUTOFF DATE.
  That's why we use RAG (covered in Concept 6) for live data.
"""

# ─────────────────────────────────────────────────────────────────────────────
# CONCEPT 3 — WHAT IS GENERATIVE AI?
# ─────────────────────────────────────────────────────────────────────────────
"""
DEFINITION:
────────────
Generative AI is a category of AI that can CREATE new content —
text, images, audio, video, code — not just classify or predict.

Traditional AI vs Generative AI:
──────────────────────────────────
  Traditional ML:
    Input: Resume → Output: LABEL ("Qualified" / "Not Qualified")

  Generative AI:
    Input: Resume + JD → Output: WRITTEN evaluation report + score + reasoning

Types of Generative AI:
────────────────────────
  ┌────────────────────┬────────────────────────────────────────────┐
  │ Type               │ Example                                    │
  ├────────────────────┼────────────────────────────────────────────┤
  │ Text Generation    │ GPT-4, Claude → write evaluation reports   │
  │ Image Generation   │ DALL-E, Midjourney → (not our focus)       │
  │ Code Generation    │ GitHub Copilot → we'll use this!           │
  │ Audio/Video        │ Sora, ElevenLabs → future extension        │
  └────────────────────┴────────────────────────────────────────────┘

Why It Matters for Recruitment:
─────────────────────────────────
  Before GenAI: HR spends 6+ hours per candidate reviewing resumes
  After GenAI:  AI processes 100+ resumes in seconds with explanations

Real Industry Stat:
────────────────────
  According to LinkedIn's 2024 Future of Recruiting report:
  → 62% of recruiters are already using AI tools
  → AI reduces time-to-hire by 40%
  → Bias reduction is a KEY selling point for AI-driven hiring
"""

# ─────────────────────────────────────────────────────────────────────────────
# CONCEPT 4 — WHAT ARE AI AGENTS?
# ─────────────────────────────────────────────────────────────────────────────
"""
DEFINITION:
────────────
An AI Agent is an LLM that can:
  1. PERCEIVE  → take in information (resume, JD, instructions)
  2. REASON   → plan what steps to take
  3. ACT      → use tools, call APIs, write to databases
  4. ITERATE  → reflect on results and retry if needed

The Agent Loop (ReAct Pattern):
─────────────────────────────────
  ┌─────────────────────────────────────────────────────┐
  │                   AGENT LOOP                        │
  │                                                     │
  │   User Input                                        │
  │       │                                             │
  │       ▼                                             │
  │   ┌───────────┐    THINK     ┌──────────────────┐   │
  │   │   LLM     │ ──────────→  │ "I need to call  │   │
  │   │  (Brain)  │              │  parse_resume()  │   │
  │   └───────────┘              └──────────────────┘   │
  │       │                              │               │
  │       │◄─────────────────────────────┘               │
  │       │         ACT (Tool Call)                      │
  │       ▼                                              │
  │   ┌───────────┐                                      │
  │   │   TOOLS   │  parse_resume, search_db, send_email │
  │   └───────────┘                                      │
  │       │                                              │
  │       │   OBSERVE (Tool Result)                      │
  │       ▼                                              │
  │   ┌───────────┐                                      │
  │   │   LLM     │  "Got the result, now I'll..."       │
  │   │  (Brain)  │                                      │
  │   └───────────┘                                      │
  │       │                                              │
  │       ▼                                              │
  │   Final Answer / Next Action                        │
  └─────────────────────────────────────────────────────┘

An Agent = LLM + Tools + Memory + Planning

Tools our Agents Will Use:
───────────────────────────
  • parse_resume_pdf()       → extract text from PDF
  • search_candidates_db()   → query MySQL database
  • store_in_vector_db()     → save embeddings to Pinecone
  • send_interview_email()   → send emails via SMTP
  • calculate_match_score()  → score candidate vs JD
  • generate_report()        → create PDF report

Common Mistake ⚠️:
───────────────────
  Agents are NOT infinitely smart.
  They fail when:
    - Prompts are poorly designed
    - Tools return ambiguous results
    - Context window is exceeded
  
  ALWAYS add error handling + human-in-the-loop checkpoints!
"""

# ─────────────────────────────────────────────────────────────────────────────
# CONCEPT 5 — SINGLE AGENT vs MULTI-AGENT SYSTEMS
# ─────────────────────────────────────────────────────────────────────────────
"""
SINGLE AGENT SYSTEM:
─────────────────────
  One LLM handles EVERYTHING.
  
  User: "Process this resume for the Senior Python Developer role"
  
  ┌──────────────────────────────────────────────────────────┐
  │                    SINGLE AGENT                          │
  │                                                          │
  │  → Parse PDF         ← doing too much!                   │
  │  → Extract skills    ← overloaded                        │
  │  → Match with JD     ← loses context                     │
  │  → Score candidate   ← errors compound                   │
  │  → Schedule interview← unreliable at scale               │
  │  → Generate report                                       │
  └──────────────────────────────────────────────────────────┘

  Problems:
  ❌ Context window overloaded
  ❌ One failure crashes everything
  ❌ Hard to debug
  ❌ Not scalable
  ❌ Can't parallelize

────────────────────────────────────────────────────

MULTI-AGENT SYSTEM (What We're Building):
───────────────────────────────────────────
  SPECIALIZED agents, each with ONE job.
  Orchestrated by a SUPERVISOR AGENT.
  
  ┌──────────────────────────────────────────────────────────────┐
  │                  MULTI-AGENT SYSTEM                          │
  │                                                              │
  │               ┌─────────────────┐                           │
  │               │   SUPERVISOR    │  ← Orchestrates workflow  │
  │               │     AGENT       │                           │
  │               └────────┬────────┘                           │
  │        ┌───────────────┼───────────────┐                    │
  │        │               │               │                    │
  │        ▼               ▼               ▼                    │
  │  ┌──────────┐   ┌──────────┐   ┌──────────────┐            │
  │  │  Resume  │   │   JD     │   │  Candidate   │            │
  │  │  Parser  │   │Analyzer  │   │  Matching    │            │
  │  │  Agent   │   │  Agent   │   │    Agent     │            │
  │  └──────────┘   └──────────┘   └──────────────┘            │
  │        │               │               │                    │
  │        └───────────────┼───────────────┘                    │
  │                        ▼                                     │
  │               ┌─────────────────┐                           │
  │               │   Scheduling +  │                           │
  │               │  Evaluation +   │                           │
  │               │  Reporting      │                           │
  │               │    Agents       │                           │
  │               └─────────────────┘                           │
  └──────────────────────────────────────────────────────────────┘

  Benefits:
  ✅ Each agent is focused → higher accuracy
  ✅ Parallel execution → faster processing
  ✅ Failure isolation → one agent fails, others continue
  ✅ Easy to debug → know exactly which agent caused the issue
  ✅ Scalable → add new agents without rewriting others

Real-World Comparison:
───────────────────────
  Single Agent = Solo consultant doing everything themselves
  Multi-Agent  = Consulting FIRM with specialized departments
  
  A law firm doesn't have ONE person doing research, arguing cases,
  managing clients, and handling paperwork. They have SPECIALISTS.
  Multi-Agent AI mirrors this exact model.
"""

# ─────────────────────────────────────────────────────────────────────────────
# CONCEPT 6 — WHAT IS RAG (RETRIEVAL AUGMENTED GENERATION)?
# ─────────────────────────────────────────────────────────────────────────────
"""
THE PROBLEM WITH PLAIN LLMs:
──────────────────────────────
  LLMs are trained on public data up to a cutoff date.
  They DON'T know about:
    ❌ YOUR company's job descriptions
    ❌ YOUR database of 10,000 candidate resumes
    ❌ YOUR internal hiring policies

RAG SOLUTION:
──────────────
  RAG = Give the LLM RELEVANT context at runtime from YOUR data.

How RAG Works:
───────────────
  ┌─────────────────────────────────────────────────────────────┐
  │                    RAG PIPELINE                             │
  │                                                             │
  │  YOUR DATA (Resumes, JDs, Policies)                         │
  │       │                                                     │
  │       ▼                                                     │
  │  ┌──────────┐     Chunk text into small pieces             │
  │  │ CHUNKING │                                               │
  │  └──────────┘                                               │
  │       │                                                     │
  │       ▼                                                     │
  │  ┌──────────────┐   Convert text to numbers (vectors)      │
  │  │  EMBEDDING   │   "Python developer" → [0.23, 0.87, ...]  │
  │  │    MODEL     │                                           │
  │  └──────────────┘                                           │
  │       │                                                     │
  │       ▼                                                     │
  │  ┌──────────────┐   Store in a database optimized          │
  │  │  VECTOR DB   │   for similarity search                   │
  │  │  (Pinecone)  │                                           │
  │  └──────────────┘                                           │
  │                                                             │
  │  AT QUERY TIME:                                             │
  │                                                             │
  │  User Query: "Find Python developers with 5+ years exp"     │
  │       │                                                     │
  │       ▼                                                     │
  │  Embed the query → search vector DB → get top 5 resumes     │
  │       │                                                     │
  │       ▼                                                     │
  │  LLM receives: [Query + Top 5 Matching Resumes]             │
  │       │                                                     │
  │       ▼                                                     │
  │  LLM generates: Ranked list with explanations               │
  └─────────────────────────────────────────────────────────────┘

In Our Project — RAG is Used For:
───────────────────────────────────
  • Semantic search across 1000s of stored resumes
  • Finding similar past candidates for a new JD
  • Retrieving relevant company hiring policies
  • Matching skills even when worded differently
    (e.g., "ML Engineer" = "Machine Learning Specialist")
"""

# ─────────────────────────────────────────────────────────────────────────────
# CONCEPT 7 — WHAT IS LANGCHAIN?
# ─────────────────────────────────────────────────────────────────────────────
"""
DEFINITION:
────────────
LangChain is a Python/JavaScript framework that provides the
BUILDING BLOCKS to create LLM-powered applications.

Think of LangChain as a TOOLKIT, not an application itself.

LangChain Core Components:
───────────────────────────
  ┌─────────────────────────────────────────────────────────┐
  │                  LANGCHAIN ECOSYSTEM                     │
  │                                                         │
  │  ┌──────────┐  Universal interface to ALL LLMs          │
  │  │  MODELS  │  OpenAI, Anthropic, Gemini, Groq, Ollama  │
  │  └──────────┘                                           │
  │                                                         │
  │  ┌──────────┐  Templates for prompts with variables      │
  │  │ PROMPTS  │  "Analyze this resume: {resume_text}"      │
  │  └──────────┘                                           │
  │                                                         │
  │  ┌──────────┐  Functions the LLM can call               │
  │  │  TOOLS   │  search_web(), parse_pdf(), query_db()     │
  │  └──────────┘                                           │
  │                                                         │
  │  ┌──────────┐  Store and retrieve conversation history  │
  │  │  MEMORY  │  BufferMemory, VectorStoreMemory           │
  │  └──────────┘                                           │
  │                                                         │
  │  ┌──────────┐  Chain multiple steps together             │
  │  │  CHAINS  │  Parse → Extract → Score → Report         │
  │  └──────────┘                                           │
  │                                                         │
  │  ┌──────────┐  Connect to vector databases               │
  │  │RETRIEVERS│  Pinecone, ChromaDB, FAISS                 │
  │  └──────────┘                                           │
  └─────────────────────────────────────────────────────────┘

Simple LangChain Code Preview (you'll write this in Phase 7):
───────────────────────────────────────────────────────────────
  from langchain_openai import ChatOpenAI
  from langchain_core.prompts import ChatPromptTemplate

  llm = ChatOpenAI(model="gpt-4o")
  
  prompt = ChatPromptTemplate.from_template(
      "Extract skills from this resume: {resume_text}"
  )
  
  chain = prompt | llm
  result = chain.invoke({"resume_text": "Python, FastAPI, 5 years..."})

  # result → "Skills: Python, FastAPI. Experience: 5 years"

LangChain vs Writing Raw API Calls:
─────────────────────────────────────
  Without LangChain:
    → Manually format API payloads
    → Handle retries yourself
    → Write custom tool-calling logic
    → Integrate each LLM differently

  With LangChain:
    → One interface for ALL LLMs
    → Built-in retry logic
    → Standard tool calling format
    → Pre-built integrations for 100+ tools
"""

# ─────────────────────────────────────────────────────────────────────────────
# CONCEPT 8 — WHAT IS LANGGRAPH?
# ─────────────────────────────────────────────────────────────────────────────
"""
DEFINITION:
────────────
LangGraph is a library built ON TOP OF LangChain specifically for building
STATEFUL, MULTI-ACTOR workflows using a GRAPH structure.

The Key Insight:
─────────────────
  Simple LLM tasks  → use LangChain Chains
  Complex workflows → use LangGraph (with loops, branches, human checkpoints)

What is a Graph?
─────────────────
  A GRAPH = NODES + EDGES

  NODES = the agents / processing steps (Resume Parser, JD Analyzer, etc.)
  EDGES = the connections / flow between nodes

LangGraph Architecture for Our Project:
─────────────────────────────────────────
  ┌─────────────────────────────────────────────────────────────┐
  │                    LANGGRAPH WORKFLOW                        │
  │                                                             │
  │         START                                               │
  │           │                                                 │
  │           ▼                                                 │
  │    ┌─────────────┐                                          │
  │    │  SUPERVISOR │  ← decides which agent runs next         │
  │    │    NODE     │                                          │
  │    └──────┬──────┘                                          │
  │           │ (conditional routing)                           │
  │    ┌──────┴──────┬──────────────┬───────────────┐           │
  │    ▼             ▼              ▼               ▼           │
  │ ┌───────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
  │ │Resume │  │   JD     │  │Candidate │  │Interview │        │
  │ │Parser │  │Analyzer  │  │Matcher   │  │Scheduler │        │
  │ └───┬───┘  └────┬─────┘  └────┬─────┘  └────┬─────┘        │
  │     └──────────┬┴─────────────┘              │              │
  │                ▼                             │              │
  │         ┌──────────────┐                     │              │
  │         │  EVALUATOR   │◄────────────────────┘              │
  │         │     NODE     │                                    │
  │         └──────┬───────┘                                    │
  │                │                                            │
  │                ▼                                            │
  │         ┌──────────────┐                                    │
  │         │ HUMAN REVIEW │  ← Human-in-the-Loop checkpoint    │
  │         │  CHECKPOINT  │                                    │
  │         └──────┬───────┘                                    │
  │                │                                            │
  │                ▼                                            │
  │         ┌──────────────┐                                    │
  │         │   REPORTER   │                                    │
  │         │     NODE     │                                    │
  │         └──────┬───────┘                                    │
  │                │                                            │
  │               END                                           │
  └─────────────────────────────────────────────────────────────┘

Why LangGraph Over Simple Chains?
───────────────────────────────────
  ┌────────────────────────┬────────────────────────────────────┐
  │ Feature                │ LangGraph                          │
  ├────────────────────────┼────────────────────────────────────┤
  │ Cycles / Loops         │ ✅ Yes (retry logic, feedback loops)│
  │ Shared State           │ ✅ Typed state object               │
  │ Human-in-the-Loop      │ ✅ Built-in interrupt system        │
  │ Persistence/Checkpoint │ ✅ Save and resume workflow state   │
  │ Parallel Execution     │ ✅ Fan-out to multiple agents       │
  │ Conditional Routing    │ ✅ Route based on results           │
  │ Streaming              │ ✅ Stream intermediate results      │
  └────────────────────────┴────────────────────────────────────┘

LangGraph State (Core Concept):
─────────────────────────────────
  ALL agents share a SINGLE STATE object.
  It acts like a shared whiteboard.
  Every agent reads from it and writes to it.

  # Our project's state will look like this:
  class HiringState(TypedDict):
      job_description: str
      parsed_resumes: list
      extracted_skills: dict
      candidate_scores: list
      interview_schedule: dict
      human_approved: bool
      final_report: str
"""

# ─────────────────────────────────────────────────────────────────────────────
# CONCEPT 9 — WHY COMPANIES ARE ADOPTING AGENTIC WORKFLOWS
# ─────────────────────────────────────────────────────────────────────────────
"""
THE MARKET SHIFT:
──────────────────
  2020-2022: Companies used AI for simple tasks (chatbots, autocomplete)
  2023-2024: LLMs became capable enough for COMPLEX reasoning
  2025+:     Agentic workflows are replacing entire human workflows

Real-World Adoption:
─────────────────────
  Company         │ Agentic Use Case
  ────────────────┼───────────────────────────────────────────
  Salesforce      │ Agentforce: AI agents handle sales workflows
  ServiceNow      │ AI agents resolve 80% of IT tickets
  Workday         │ AI agents process 60% of HR transactions
  JPMorgan        │ AI agents review 12,000 contracts/hour
  Deloitte        │ AI agents audit financial statements

Why Recruitment is PERFECT for Agentic AI:
────────────────────────────────────────────
  ✅ High volume, repetitive tasks (parsing 1000s of resumes)
  ✅ Clear criteria (JD requirements vs candidate skills)
  ✅ Multiple specialized steps (parse → match → score → schedule)
  ✅ Human oversight needed (avoid bias, regulatory compliance)
  ✅ Clear ROI (time saved × recruiter hourly rate)

Business Value of Our Platform:
─────────────────────────────────
  METRIC              │ BEFORE AI   │ AFTER AI
  ────────────────────┼─────────────┼──────────────
  Time to screen 100  │ 15 hours    │ 5 minutes
  resumes             │             │
  ────────────────────┼─────────────┼──────────────
  Interview scheduling│ 2 days      │ Instant
  coordination        │             │
  ────────────────────┼─────────────┼──────────────
  Resume bias review  │ Inconsistent│ Standardized
  ────────────────────┼─────────────┼──────────────
  Candidate ranking   │ Subjective  │ Score-based
  ────────────────────┼─────────────┼──────────────
  Cost per hire       │ $4,000+     │ ~$500

AGENTIC = Autonomous + Goal-Directed + Tool-Using + Self-correcting
"""
