"""
Centralised settings — all agents and backend import from here.
Reads from .env; validates required keys at startup.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── LLM Selection ────────────────────────────────────────────────────────────
# "groq" and "gemini" are FREE. "openai" / "anthropic" cost money.
DEFAULT_LLM_PROVIDER: str = os.getenv("DEFAULT_LLM_PROVIDER", "groq")

# ── Model names per provider ─────────────────────────────────────────────────
GROQ_MODEL:      str = os.getenv("GROQ_MODEL",      "llama-3.3-70b-versatile")
GEMINI_MODEL:    str = os.getenv("GEMINI_MODEL",     "gemini-2.0-flash")
OPENAI_MODEL:    str = os.getenv("OPENAI_MODEL",     "gpt-4o-mini")
ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL",  "claude-3-haiku-20240307")

# ── API Keys ─────────────────────────────────────────────────────────────────
GROQ_API_KEY:      str = os.getenv("GROQ_API_KEY",      "")
GOOGLE_API_KEY:    str = os.getenv("GOOGLE_API_KEY",    "")
OPENAI_API_KEY:    str = os.getenv("OPENAI_API_KEY",    "")
ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
TAVILY_API_KEY:    str = os.getenv("TAVILY_API_KEY",    "")
PINECONE_API_KEY:  str = os.getenv("PINECONE_API_KEY",  "")
LANGCHAIN_API_KEY: str = os.getenv("LANGCHAIN_API_KEY", "")

# ── Embedding: use local sentence-transformers (free, no API needed) ──────────
EMBEDDING_PROVIDER: str = os.getenv("EMBEDDING_PROVIDER", "local")
OPENAI_EMBEDDING_MODEL: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

# ── Database ─────────────────────────────────────────────────────────────────
DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./hiring_copilot.db")

# ── Redis (optional — used for checkpointing) ────────────────────────────────
REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# ── App ───────────────────────────────────────────────────────────────────────
SECRET_KEY:    str = os.getenv("SECRET_KEY", "dev-secret-change-in-production-64-chars!!")
APP_ENV:       str = os.getenv("APP_ENV", "development")
DEBUG:         bool = os.getenv("DEBUG", "true").lower() == "true"
UPLOAD_DIR:    str = os.getenv("UPLOAD_DIR", "./uploads/resumes")
MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
RESUME_MAX_CHARS: int = int(os.getenv("RESUME_MAX_CHARS", "3000"))
INTERVIEW_QUESTIONS_COUNT: int = int(os.getenv("INTERVIEW_QUESTIONS_COUNT", "5"))
CORS_ORIGINS: list[str] = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")
SMTP_ENABLED: bool = os.getenv("SMTP_ENABLED", "false").lower() == "true"

# ── LangSmith ────────────────────────────────────────────────────────────────
LANGCHAIN_TRACING_V2: bool = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
LANGCHAIN_PROJECT: str = os.getenv("LANGCHAIN_PROJECT", "ai-hiring-copilot")


def get_llm(temperature: float = 0, provider: str | None = None):
    """
    Factory that returns the configured LLM.
    Default provider is controlled by DEFAULT_LLM_PROVIDER in .env.
    Both groq and gemini are free-tier.
    """
    chosen = provider or DEFAULT_LLM_PROVIDER

    if chosen == "groq":
        from langchain_groq import ChatGroq
        return ChatGroq(model=GROQ_MODEL, temperature=temperature, api_key=GROQ_API_KEY)

    if chosen == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(model=GEMINI_MODEL, temperature=temperature, google_api_key=GOOGLE_API_KEY)

    if chosen == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model=OPENAI_MODEL, temperature=temperature, api_key=OPENAI_API_KEY)

    if chosen == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(model=ANTHROPIC_MODEL, temperature=temperature, api_key=ANTHROPIC_API_KEY)

    raise ValueError(f"Unknown LLM provider: {chosen}. Choose groq | gemini | openai | anthropic")


def get_embeddings():
    """
    Returns the embedding model.
    'local' uses sentence-transformers (100% free, runs on your machine).
    'openai' uses text-embedding-3-small (costs money).
    """
    if EMBEDDING_PROVIDER == "openai":
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(model=OPENAI_EMBEDDING_MODEL, api_key=OPENAI_API_KEY)

    # Default: local sentence-transformers — free, no API key needed
    from langchain_community.embeddings import HuggingFaceEmbeddings
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")


def validate_config() -> list[str]:
    """Returns list of missing keys for the chosen provider."""
    required = {
        "groq":    [("GROQ_API_KEY", GROQ_API_KEY)],
        "gemini":  [("GOOGLE_API_KEY", GOOGLE_API_KEY)],
        "openai":  [("OPENAI_API_KEY", OPENAI_API_KEY)],
        "anthropic": [("ANTHROPIC_API_KEY", ANTHROPIC_API_KEY)],
    }
    missing = [name for name, val in required.get(DEFAULT_LLM_PROVIDER, []) if not val]
    return missing


if __name__ == "__main__":
    print(f"Provider : {DEFAULT_LLM_PROVIDER}")
    print(f"DB       : {DATABASE_URL}")
    print(f"Embeddings: {EMBEDDING_PROVIDER}")
    missing = validate_config()
    if missing:
        print(f"⚠️  Missing keys: {missing}")
    else:
        print("✅ Config OK")
        llm = get_llm()
        resp = llm.invoke("Reply with exactly: AI Hiring Co-Pilot ready!")
        print(f"LLM test : {resp.content}")
