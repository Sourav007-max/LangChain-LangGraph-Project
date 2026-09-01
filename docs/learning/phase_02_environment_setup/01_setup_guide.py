"""
=============================================================================
  PHASE 2 — DEVELOPMENT ENVIRONMENT SETUP
  AI Hiring Co-Pilot: Multi-Agent Recruitment Platform using LangGraph
=============================================================================

WHAT WE'RE SETTING UP AND WHY:
  Tool              Why We Need It
  ──────────────────────────────────────────────────────────────────
  Python venv       Isolated dependencies — no version conflicts
  MySQL             Structured data (candidates, jobs, applications)
  Redis             Caching + LangGraph workflow checkpointing
  Git + GitHub      Version control — never lose your code
  .env file         Secure API key management

BY END OF THIS PHASE:
  ✅ Virtual environment created and activated
  ✅ All Python packages installed
  ✅ MySQL running and tested
  ✅ Redis running and tested
  ✅ GitHub repo initialized
  ✅ First connection test passing
=============================================================================
"""

# ─────────────────────────────────────────────────────────────────────────────
# STEP 1 — VIRTUAL ENVIRONMENT
# ─────────────────────────────────────────────────────────────────────────────
"""
WHY A VIRTUAL ENVIRONMENT?
───────────────────────────
Imagine you have two projects:
  Project A needs LangChain version 0.1
  Project B needs LangChain version 0.3

Without venv → installing 0.3 BREAKS project A.
With venv    → each project has its OWN isolated Python installation.

ANALOGY: It's like each project having its own apartment.
They share the same building (Python) but have separate rooms (packages).

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
COMMANDS (run in your terminal / PowerShell):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WINDOWS (PowerShell):
─────────────────────
  # Navigate to your project folder
  cd "C:\\Users\\sdhayapu\\OneDrive - Cisco\\Desktop\\Langchain-projects\\ai-hiring-copilot"

  # Create virtual environment
  python -m venv venv

  # Activate virtual environment  ← DO THIS EVERY TIME you open a terminal
  .\\venv\\Scripts\\activate

  # You should now see (venv) at the start of your prompt:
  # (venv) PS C:\\...\\ai-hiring-copilot>

  # Verify Python is from venv
  where python
  # Should show: ...\\ai-hiring-copilot\\venv\\Scripts\\python.exe

MAC / LINUX (Terminal):
───────────────────────
  cd ~/Desktop/Langchain-projects/ai-hiring-copilot
  python3 -m venv venv
  source venv/bin/activate

DEACTIVATE (when done working):
────────────────────────────────
  deactivate

⚠️ COMMON MISTAKE: Forgetting to activate venv before installing packages.
   Always check for (venv) in your terminal prompt!
"""

# ─────────────────────────────────────────────────────────────────────────────
# STEP 2 — INSTALL ALL PYTHON PACKAGES
# ─────────────────────────────────────────────────────────────────────────────
"""
WHY THESE PACKAGES?
────────────────────
  Package                  Purpose in Our Project
  ─────────────────────────────────────────────────────────────────────
  langchain                Core LLM framework — prompts, chains, tools
  langchain-openai         OpenAI GPT integration
  langchain-anthropic      Claude integration
  langchain-google-genai   Gemini integration
  langchain-groq           Groq (fast Llama) integration
  langgraph                Multi-agent workflow orchestration ← CORE
  langchain-community      Community integrations (MySQL, Redis etc.)
  fastapi                  High-performance REST API framework
  uvicorn                  ASGI server to run FastAPI
  sqlalchemy               Python ORM for database operations
  pymysql                  MySQL driver for Python
  redis                    Python Redis client
  pydantic                 Data validation (used heavily in FastAPI)
  python-dotenv            Load .env variables into Python
  pypdf                    Parse PDF resume files
  python-multipart         Handle file uploads in FastAPI
  openai                   Direct OpenAI API client
  pinecone-client          Pinecone vector database client
  sentence-transformers    Create text embeddings locally
  tiktoken                 Count tokens before sending to OpenAI
  celery                   Background task queue (async agent execution)
  passlib                  Password hashing for auth
  python-jose              JWT token creation/validation
  streamlit                Quick dashboard (for testing before React)
  pytest                   Testing framework
  httpx                    Async HTTP client for testing FastAPI

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INSTALL COMMAND (run after activating venv):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  pip install -r requirements.txt

  (The requirements.txt file is in your project root — see below)
"""

# ─────────────────────────────────────────────────────────────────────────────
# STEP 3 — MYSQL SETUP
# ─────────────────────────────────────────────────────────────────────────────
"""
WHY MYSQL?
───────────
MySQL is a RELATIONAL database — perfect for structured recruitment data:
  → Candidates have profiles (rows in a table)
  → Jobs have requirements (rows in another table)
  → Applications link candidates TO jobs (join table)
  → We need ACID compliance — no partial saves for candidate records

MYSQL vs POSTGRESQL (why we chose MySQL):
──────────────────────────────────────────
  Both are excellent. MySQL is chosen here because:
  ✅ Wider industry adoption in enterprise companies
  ✅ Easier Windows installation (MySQL Installer)
  ✅ MySQL Workbench is beginner-friendly
  ✅ Great documentation and community

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WINDOWS INSTALLATION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Step 1: Download MySQL Installer
  → Go to: https://dev.mysql.com/downloads/installer/
  → Download "mysql-installer-community-x.x.xx.x.msi"
  → Run the installer

Step 2: Installation Type
  → Select "Developer Default" (installs MySQL Server + MySQL Workbench)
  → Click "Next" through requirements
  → Click "Execute" to install

Step 3: Server Configuration
  → Config Type: "Development Computer"
  → Port: 3306 (keep default)
  → Root Password: Set a STRONG password, write it down!
    Example: MyHiringApp@2025 (DO NOT use this in production)
  → Create a user account:
    Username: hiring_user
    Password: HiringApp@Dev123
    Role: DB Admin (for development)

Step 4: Finish Installation
  → Complete the wizard
  → MySQL Server should start automatically

Step 5: Verify Installation (PowerShell):
  mysql -u root -p
  # Enter your root password
  # You should see: mysql>

  # In the MySQL prompt:
  SHOW DATABASES;
  # Should show: information_schema, mysql, performance_schema, sys
  EXIT;

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MAC INSTALLATION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  brew install mysql
  brew services start mysql
  mysql_secure_installation
  mysql -u root -p

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LINUX (Ubuntu/Debian):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  sudo apt update
  sudo apt install mysql-server
  sudo systemctl start mysql
  sudo mysql_secure_installation
  sudo mysql -u root -p

CREATE THE PROJECT DATABASE:
─────────────────────────────
  # In MySQL prompt or MySQL Workbench:
  CREATE DATABASE hiring_copilot CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
  CREATE USER 'hiring_user'@'localhost' IDENTIFIED BY 'HiringApp@Dev123';
  GRANT ALL PRIVILEGES ON hiring_copilot.* TO 'hiring_user'@'localhost';
  FLUSH PRIVILEGES;

⚠️ COMMON MISTAKE: Using root user in your application.
   ALWAYS create a dedicated user with MINIMUM required permissions!
"""

# ─────────────────────────────────────────────────────────────────────────────
# STEP 4 — REDIS SETUP
# ─────────────────────────────────────────────────────────────────────────────
"""
WHY REDIS?
───────────
Redis is an in-memory key-value store. In our project it handles:

  1. LangGraph Checkpointing:
     → Save workflow state between agent steps
     → Resume workflows that paused for human review
     → Survive server restarts without losing progress

  2. Caching:
     → Cache LLM responses (same resume = no need to re-call OpenAI)
     → Cache candidate scores to avoid redundant computation
     → Saves money! LLM calls cost money.

  3. Session Storage:
     → Store user sessions for the FastAPI backend

  4. Task Queue (with Celery):
     → Process 100 resumes in parallel background workers

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WINDOWS INSTALLATION (Two Options):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

OPTION A: WSL2 (Windows Subsystem for Linux) ← RECOMMENDED
  # Step 1: Enable WSL2 (PowerShell as Administrator)
  wsl --install

  # Step 2: After restart, open Ubuntu from Start Menu
  # Step 3: Install Redis in WSL2
  sudo apt update
  sudo apt install redis-server
  sudo service redis-server start

  # Step 4: Test
  redis-cli ping
  # Expected output: PONG

OPTION B: Memurai (Redis-compatible for Windows)
  → Download from: https://www.memurai.com/
  → Install the .msi
  → It runs as a Windows service automatically
  → Connect using: redis-cli -h localhost -p 6379

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MAC:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  brew install redis
  brew services start redis
  redis-cli ping

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LINUX:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  sudo apt install redis-server
  sudo systemctl enable redis
  sudo systemctl start redis
  redis-cli ping
"""

# ─────────────────────────────────────────────────────────────────────────────
# STEP 5 — GIT SETUP
# ─────────────────────────────────────────────────────────────────────────────
"""
WHY GIT?
─────────
  ✅ Never lose code (every change is saved)
  ✅ Experiment safely (create branches, revert mistakes)
  ✅ Collaborate with team (multiple devs, one codebase)
  ✅ Industry standard — every company uses Git
  ✅ Portfolio on GitHub shows employers your work

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
GIT CONFIGURATION (Run Once on Your Machine):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  git config --global user.name "Your Name"
  git config --global user.email "your@email.com"
  git config --global core.editor "code --wait"   # VS Code as default editor

INITIALIZE REPOSITORY:
───────────────────────
  cd "C:\\Users\\sdhayapu\\OneDrive - Cisco\\Desktop\\Langchain-projects\\ai-hiring-copilot"
  git init
  git add .
  git commit -m "Initial project setup — AI Hiring Co-Pilot"

PUSH TO GITHUB:
────────────────
  # Create repo on github.com first, then:
  git remote add origin https://github.com/YOUR_USERNAME/ai-hiring-copilot.git
  git branch -M main
  git push -u origin main

DAILY GIT WORKFLOW:
────────────────────
  git status                          # see what changed
  git add .                           # stage all changes
  git commit -m "descriptive message" # save snapshot
  git push                            # upload to GitHub

⚠️ CRITICAL: NEVER commit your .env file (it has API keys!)
   The .gitignore file below handles this automatically.
"""

# ─────────────────────────────────────────────────────────────────────────────
# STEP 6 — CONNECTION VERIFICATION
# ─────────────────────────────────────────────────────────────────────────────

def test_mysql_connection():
    """Run this AFTER completing MySQL setup to verify connection."""
    import pymysql
    
    try:
        connection = pymysql.connect(
            host="localhost",
            user="hiring_user",
            password="HiringApp@Dev123",  # use your actual password
            database="hiring_copilot",
            port=3306
        )
        print("✅ MySQL connection successful!")
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"   MySQL version: {version[0]}")
        
        connection.close()
        return True
    except Exception as e:
        print(f"❌ MySQL connection failed: {e}")
        print("   → Check: Is MySQL server running?")
        print("   → Check: Are credentials correct?")
        return False


def test_redis_connection():
    """Run this AFTER completing Redis setup to verify connection."""
    import redis
    
    try:
        r = redis.Redis(host="localhost", port=6379, decode_responses=True)
        r.ping()
        r.set("test_key", "AI Hiring Co-Pilot - Redis works!")
        value = r.get("test_key")
        print(f"✅ Redis connection successful!")
        print(f"   Test value: {value}")
        r.delete("test_key")
        return True
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        print("   → Check: Is Redis server running?")
        print("   → Check: WSL2/Memurai started?")
        return False


def test_openai_connection():
    """Run this AFTER setting up OpenAI API key in .env (Phase 3)."""
    from openai import OpenAI
    from dotenv import load_dotenv
    
    load_dotenv()
    client = OpenAI()
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say 'AI Hiring Co-Pilot ready!'"}],
            max_tokens=20
        )
        print(f"✅ OpenAI connection successful!")
        print(f"   Response: {response.choices[0].message.content}")
        return True
    except Exception as e:
        print(f"❌ OpenAI connection failed: {e}")
        print("   → Check: Is OPENAI_API_KEY set in .env?")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("  AI HIRING CO-PILOT — Environment Connection Test")
    print("=" * 60)
    
    print("\n[1/3] Testing MySQL...")
    test_mysql_connection()
    
    print("\n[2/3] Testing Redis...")
    test_redis_connection()
    
    print("\n[3/3] Testing OpenAI (requires .env setup from Phase 3)...")
    # test_openai_connection()  # uncomment after Phase 3
    
    print("\n" + "=" * 60)
    print("  If all ✅ → you are ready for Phase 3!")
    print("=" * 60)
