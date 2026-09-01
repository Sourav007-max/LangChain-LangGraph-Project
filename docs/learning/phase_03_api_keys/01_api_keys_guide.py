"""
=============================================================================
  PHASE 3 — API KEYS SETUP
  AI Hiring Co-Pilot: Multi-Agent Recruitment Platform using LangGraph
=============================================================================

WHY SO MANY API KEYS?
──────────────────────
  Each service provides a SPECIALIZED capability:
  • OpenAI/Gemini/Groq  → Different LLMs for different tasks
  • Pinecone/Weaviate   → Vector databases for resume search
  • Tavily/SerpAPI      → Real-time web search for market data
  • LangSmith           → Monitor and debug all agent calls

  We won't use ALL of them simultaneously.
  We pick the BEST tool for each specific task.
=============================================================================
"""

# ─────────────────────────────────────────────────────────────────────────────
# API 1 — OPENAI
# ─────────────────────────────────────────────────────────────────────────────
"""
WHAT IT DOES:
──────────────
  The most powerful and reliable LLM API.
  GPT-4o is our PRIMARY model for complex reasoning tasks:
    → Resume parsing and extraction
    → Candidate evaluation
    → Interview question generation
    → Report writing

FREE TIER:
───────────
  NO free tier (as of 2024). You need to add credit.
  Recommended: Add $10-20 to start.
  
  COST ESTIMATE for our project (development):
    → gpt-4o-mini: $0.15 per 1M input tokens (~$0.001 per resume parse)
    → gpt-4o:      $2.50 per 1M input tokens (~$0.01 per resume parse)
  
  Processing 1000 resumes with gpt-4o-mini ≈ $1 total
  Very affordable for development!

STEP-BY-STEP SETUP:
────────────────────
  1. Go to: https://platform.openai.com/signup
  2. Create account (use Google/Microsoft login for convenience)
  3. Verify email
  4. Go to: https://platform.openai.com/api-keys
  5. Click "Create new secret key"
  6. Name it: "ai-hiring-copilot-dev"
  7. COPY THE KEY IMMEDIATELY — you can't see it again!
  8. Go to: https://platform.openai.com/settings/billing
  9. Add payment method + add $10-20 credit
  10. Set a SPENDING LIMIT: $20/month (prevents surprise bills!)
      → Settings → Limits → Set monthly spending limit

IN YOUR .env FILE:
───────────────────
  OPENAI_API_KEY=sk-proj-your-actual-key-here
  OPENAI_MODEL=gpt-4o
  OPENAI_EMBEDDING_MODEL=text-embedding-3-small

⚠️ SECURITY: API keys start with "sk-proj-" or "sk-"
   If you ever accidentally push to GitHub, immediately:
   1. Rotate the key (delete + create new)
   2. Check for unauthorized usage in usage dashboard
"""

# ─────────────────────────────────────────────────────────────────────────────
# API 2 — ANTHROPIC (CLAUDE)
# ─────────────────────────────────────────────────────────────────────────────
"""
WHAT IT DOES:
──────────────
  Claude 3.5 Sonnet is EXCELLENT for:
    → Long document analysis (200K token context)
    → Reading full resumes + JD in ONE call
    → Nuanced evaluation with detailed reasoning
    → Safety-focused outputs (less hallucination)

  We'll use Claude for: Final candidate evaluation reports

FREE TIER:
───────────
  YES! Claude.ai has a free web interface.
  For API: No free tier, but very affordable.
  
  COST: Claude 3.5 Sonnet: $3 per 1M input tokens

STEP-BY-STEP SETUP:
────────────────────
  1. Go to: https://console.anthropic.com/
  2. Sign up / Log in
  3. Click "Get API Keys" → "Create Key"
  4. Name it: "hiring-copilot-dev"
  5. Copy the key (starts with "sk-ant-")
  6. Add billing: https://console.anthropic.com/settings/billing
     Add $10 credit to start

IN YOUR .env FILE:
───────────────────
  ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
  ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
"""

# ─────────────────────────────────────────────────────────────────────────────
# API 3 — GOOGLE GEMINI
# ─────────────────────────────────────────────────────────────────────────────
"""
WHAT IT DOES:
──────────────
  Gemini 1.5 Pro is GREAT for:
    → Multimodal tasks (read scanned PDFs as images)
    → Very long context (1M token window)
    → FREE tier available with generous limits
    → Integration with Google Workspace (Gmail for scheduling)

  We'll use Gemini for: Reading scanned/image-based resumes

FREE TIER:
───────────
  ✅ YES! Very generous free tier:
    → 1,500 requests/day for Gemini 1.5 Flash (free)
    → 50 requests/day for Gemini 1.5 Pro (free)
  
  For development, the free tier is MORE than enough!

STEP-BY-STEP SETUP:
────────────────────
  1. Go to: https://aistudio.google.com/
  2. Sign in with Google account
  3. Click "Get API Key" (top right)
  4. Click "Create API key"
  5. Select or create a Google Cloud project
  6. Copy your API key (starts with "AIza")
  7. No billing needed for free tier!

IN YOUR .env FILE:
───────────────────
  GOOGLE_API_KEY=AIza-your-actual-key-here
  GEMINI_MODEL=gemini-1.5-pro
"""

# ─────────────────────────────────────────────────────────────────────────────
# API 4 — GROQ
# ─────────────────────────────────────────────────────────────────────────────
"""
WHAT IT DOES:
──────────────
  Groq runs open-source models (Llama, Mixtral) on CUSTOM HARDWARE.
  Result: Inference speeds 10-20x FASTER than OpenAI.
  
  Perfect for:
    → High-volume, simple tasks (initial resume filtering)
    → Real-time streaming responses in the UI
    → Cost-sensitive operations (it's very cheap)
    → Tasks where speed matters more than absolute quality

FREE TIER:
───────────
  ✅ YES! Groq has a generous free tier:
    → 6,000 tokens/minute (free)
    → 100,000 tokens/day (Llama 3.1 70B, free)
  
  This covers ALL development needs for free!

STEP-BY-STEP SETUP:
────────────────────
  1. Go to: https://console.groq.com/
  2. Sign up with GitHub (recommended)
  3. Go to "API Keys" in left sidebar
  4. Click "Create API Key"
  5. Name: "hiring-copilot-dev"
  6. Copy key (starts with "gsk_")

IN YOUR .env FILE:
───────────────────
  GROQ_API_KEY=gsk_your-actual-key-here
  GROQ_MODEL=llama-3.1-70b-versatile

MODEL COMPARISON (When to Use Which):
───────────────────────────────────────
  ┌──────────────────┬───────────────┬────────────────────────────────────────┐
  │ Model            │ Speed         │ Best Use in Our Platform               │
  ├──────────────────┼───────────────┼────────────────────────────────────────┤
  │ GPT-4o           │ Moderate      │ Complex evaluation, final decisions    │
  │ Claude 3.5       │ Moderate      │ Long-form report generation            │
  │ Gemini 1.5 Pro   │ Moderate      │ Scanned PDF / image resume parsing     │
  │ Groq Llama 3.1   │ VERY FAST     │ Initial screening, real-time UI        │
  │ GPT-4o-mini      │ Fast          │ Skill extraction, simple tasks         │
  └──────────────────┴───────────────┴────────────────────────────────────────┘
"""

# ─────────────────────────────────────────────────────────────────────────────
# API 5 — TAVILY (AI SEARCH)
# ─────────────────────────────────────────────────────────────────────────────
"""
WHAT IT DOES:
──────────────
  Tavily is an AI-optimized search API.
  Unlike Google Search, it returns CLEAN, STRUCTURED results
  specifically designed for LLM consumption.
  
  Our agents will use it to:
    → Research company backgrounds when analyzing JDs
    → Find salary benchmarks for different roles
    → Look up candidate's public profiles (LinkedIn)
    → Get current tech skill market data

FREE TIER:
───────────
  ✅ YES! 1,000 free searches/month
  Paid: $30/month for 5,000 searches

STEP-BY-STEP SETUP:
────────────────────
  1. Go to: https://tavily.com/
  2. Click "Get Started" / "Sign Up"
  3. Create account
  4. Go to Dashboard → API Keys
  5. Copy your API key (starts with "tvly-")

IN YOUR .env FILE:
───────────────────
  TAVILY_API_KEY=tvly-your-actual-key-here
"""

# ─────────────────────────────────────────────────────────────────────────────
# API 6 — PINECONE (VECTOR DATABASE)
# ─────────────────────────────────────────────────────────────────────────────
"""
WHAT IT DOES:
──────────────
  Pinecone stores EMBEDDINGS (numerical representations of resumes).
  This enables SEMANTIC SEARCH:
    → "Find candidates similar to this top performer"
    → "Find Python developers even if resume says 'Django expert'"
    → Similarity search across 100,000 resumes in milliseconds

FREE TIER:
───────────
  ✅ YES! Pinecone Starter Plan:
    → 1 index (enough for development)
    → 100MB storage (~500,000 resume vectors)
    → Unlimited queries
    → No credit card required!

STEP-BY-STEP SETUP:
────────────────────
  1. Go to: https://www.pinecone.io/
  2. Click "Sign Up Free"
  3. Log in with Google
  4. Click "Create Index":
     → Name: hiring-copilot-resumes
     → Dimensions: 1536 (for OpenAI text-embedding-3-small)
     → Metric: cosine
     → Cloud: AWS
     → Region: us-east-1
  5. Click "API Keys" in left sidebar
  6. Copy your API key

IN YOUR .env FILE:
───────────────────
  PINECONE_API_KEY=pcsk_your-actual-key-here
  PINECONE_INDEX_NAME=hiring-copilot-resumes
  PINECONE_ENVIRONMENT=us-east-1-aws
"""

# ─────────────────────────────────────────────────────────────────────────────
# API 7 — LANGSMITH (MONITORING & DEBUGGING)
# ─────────────────────────────────────────────────────────────────────────────
"""
WHAT IT DOES:
──────────────
  LangSmith is the OBSERVABILITY platform for LangChain/LangGraph.
  Every LLM call, every agent step, every tool call is LOGGED.
  
  It allows you to:
    → See exactly what prompt was sent to the LLM
    → See the exact response received
    → Measure latency and cost per agent
    → Debug failures — see which step went wrong
    → Create test datasets and run evaluations
    → Track performance over time

  THIS IS NOT OPTIONAL in production — it's essential for debugging!

FREE TIER:
───────────
  ✅ YES! Free developer plan:
    → 5,000 traces/month free
    → For production: $39/month

STEP-BY-STEP SETUP:
────────────────────
  1. Go to: https://smith.langchain.com/
  2. Sign up / Log in
  3. Create organization: "ai-hiring-copilot"
  4. Create project: "hiring-copilot-dev"
  5. Click "Settings" → "API Keys"
  6. Create new API key
  7. Copy key (starts with "lsv2_")

IN YOUR .env FILE:
───────────────────
  LANGCHAIN_TRACING_V2=true
  LANGCHAIN_API_KEY=lsv2_your-actual-key-here
  LANGCHAIN_PROJECT=ai-hiring-copilot
  LANGCHAIN_ENDPOINT=https://api.smith.langchain.com

HOW IT WORKS (Automatic!):
────────────────────────────
  Once LANGCHAIN_TRACING_V2=true is set in your .env,
  EVERY LangChain/LangGraph call is automatically traced.
  No extra code needed!
  
  You'll see a trace like this in LangSmith dashboard:
  
  ┌─────────────────────────────────────────────┐
  │  Workflow: process_candidate               │
  │  ├── ResumeParserAgent (1.2s, $0.003)      │
  │  │   ├── prompt: "Extract skills from..."  │
  │  │   └── response: {skills: [...]}         │
  │  ├── CandidateMatcherAgent (0.8s, $0.002)  │
  │  └── EvaluatorAgent (2.1s, $0.008)         │
  │  Total: 4.1s, $0.013                       │
  └─────────────────────────────────────────────┘
"""

# ─────────────────────────────────────────────────────────────────────────────
# SECURITY BEST PRACTICES FOR API KEYS
# ─────────────────────────────────────────────────────────────────────────────
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║               🔐 API KEY SECURITY — CRITICAL RULES                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

RULE 1: NEVER hardcode keys in Python files
  ❌ WRONG:  openai.api_key = "sk-proj-abc123..."
  ✅ RIGHT:  openai.api_key = os.getenv("OPENAI_API_KEY")

RULE 2: NEVER commit .env to Git
  ✅ Always check .gitignore includes .env
  ✅ Use .env.example with dummy values for documentation

RULE 3: Use environment-specific keys
  ✅ Dev key: limited spending limits, can be rotated freely
  ✅ Prod key: strict limits, monitored, separated from dev

RULE 4: Set spending limits on ALL APIs
  → OpenAI: platform.openai.com → Settings → Limits
  → Anthropic: console.anthropic.com → Settings → Limits
  → Set hard limits LOWER than your budget

RULE 5: Rotate keys regularly
  → Dev keys: every 90 days
  → Production keys: every 30 days

RULE 6: Monitor for suspicious usage
  → Set up billing alerts at 50%, 80%, 100% of budget
  → Check usage dashboards weekly

RULE 7: Never log API keys
  ✅ CORRECT logging:
     logger.info("OpenAI API key configured: sk-proj-***")
  ❌ WRONG logging:
     logger.info(f"API key: {OPENAI_API_KEY}")

WHAT TO DO IF KEY IS COMPROMISED:
───────────────────────────────────
  1. IMMEDIATELY rotate the key (delete + create new)
  2. Check usage logs for unauthorized calls
  3. If credit was used, contact API provider support
  4. Review git history: git log --all -p | grep "sk-"
  5. If committed to GitHub: rotate key, it's already compromised
     (GitHub scans for leaked keys and notifies providers!)
"""


# ─────────────────────────────────────────────────────────────────────────────
# CONFIG LOADER — How to use .env in Python
# ─────────────────────────────────────────────────────────────────────────────

# This is the pattern we'll use throughout the entire project:
from dotenv import load_dotenv
import os

# Always call this at the TOP of your main files
load_dotenv()

class APIConfig:
    """Centralized API configuration with validation."""
    
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")
    OPENAI_EMBEDDING_MODEL: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
    
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
    
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")
    
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")
    
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
    PINECONE_INDEX_NAME: str = os.getenv("PINECONE_INDEX_NAME", "hiring-copilot-resumes")
    
    LANGCHAIN_API_KEY: str = os.getenv("LANGCHAIN_API_KEY", "")
    LANGCHAIN_PROJECT: str = os.getenv("LANGCHAIN_PROJECT", "ai-hiring-copilot")
    
    @classmethod
    def validate_required_keys(cls) -> list[str]:
        """Returns list of missing required API keys."""
        required = {
            "OPENAI_API_KEY": cls.OPENAI_API_KEY,
        }
        missing = [name for name, val in required.items() if not val]
        return missing
    
    @classmethod
    def print_status(cls):
        """Print configuration status (never prints actual key values)."""
        keys = {
            "OpenAI":      bool(cls.OPENAI_API_KEY),
            "Anthropic":   bool(cls.ANTHROPIC_API_KEY),
            "Google":      bool(cls.GOOGLE_API_KEY),
            "Groq":        bool(cls.GROQ_API_KEY),
            "Tavily":      bool(cls.TAVILY_API_KEY),
            "Pinecone":    bool(cls.PINECONE_API_KEY),
            "LangSmith":   bool(cls.LANGCHAIN_API_KEY),
        }
        print("\n API Key Status:")
        print(" " + "─" * 30)
        for name, configured in keys.items():
            status = "✅ Configured" if configured else "❌ Missing"
            print(f"  {name:<15} {status}")
        print(" " + "─" * 30)


if __name__ == "__main__":
    APIConfig.print_status()
    
    missing = APIConfig.validate_required_keys()
    if missing:
        print(f"\n⚠️  Missing required keys: {missing}")
        print("   Please add them to your .env file")
    else:
        print("\n✅ All required API keys are configured!")
