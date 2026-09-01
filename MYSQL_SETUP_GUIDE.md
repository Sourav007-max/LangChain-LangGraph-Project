# MySQL Database Setup Guide

## Current Status
The application is configured for **SQLite** in development (file-based, zero setup required).
To migrate to **MySQL**, follow these steps:

---

## Step 1: Install MySQL

### Windows (using Installer)
1. Download MySQL Community Server from [mysql.com](https://dev.mysql.com/downloads/mysql/)
2. Run the installer and follow the setup wizard
3. During installation:
   - Choose **Development Machine** setup type
   - Use **MySQL Server 8.0** (or newer)
   - Configure MySQL Server as a **Windows Service**
   - Set root password (e.g., `rootPassword123`)
4. After installation, open **MySQL Command Line Client** or use PowerShell

### Windows (using Chocolatey)
```powershell
choco install mysql --version=8.0
```

### Windows (using WSL2/Docker)
```bash
docker run --name mysql-hiring -e MYSQL_ROOT_PASSWORD=root -e MYSQL_DATABASE=hiring_copilot -p 3306:3306 -d mysql:8.0
```

---

## Step 2: Create Database User and Database

```sql
-- Connect as root
mysql -u root -p
-- Enter root password when prompted

-- Create database
CREATE DATABASE hiring_copilot;

-- Create dedicated user
CREATE USER 'hiring_user'@'localhost' IDENTIFIED BY 'hiring_password';

-- Grant permissions
GRANT ALL PRIVILEGES ON hiring_copilot.* TO 'hiring_user'@'localhost';

-- Apply changes
FLUSH PRIVILEGES;

-- Verify (should show 1 row)
SELECT user, host FROM mysql.user WHERE user='hiring_user';

-- Exit
EXIT;
```

---

## Step 3: Update `.env` Configuration

Edit `.env` in the project root:

```env
# ──────── MySQL Configuration ────────
# Switch DATABASE_URL to MySQL
DATABASE_URL=mysql+pymysql://hiring_user:hiring_password@localhost:3306/hiring_copilot

# These values match your MySQL setup above
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=hiring_user
MYSQL_PASSWORD=hiring_password
MYSQL_DATABASE=hiring_copilot

# Verify: Database URL format is: mysql+pymysql://user:password@host:port/database
```

---

## Step 4: Ensure Required Python Dependencies

The `requirements.txt` already includes:
- `sqlalchemy>=2.0.0` ✅
- `pymysql>=1.1.0` ✅

If needed, install manually:
```bash
pip install pymysql sqlalchemy
```

---

## Step 5: Initialize Database Tables

Run the initialization script to create all tables and seed demo data:

```bash
# From project root
python -m database.init_db
```

Expected output:
```
✅ All tables created in MySQL
ℹ️  Seed data already present, skipping.
```

To verify tables were created:
```bash
mysql -u hiring_user -p hiring_copilot -e "SHOW TABLES;"
# Enter password: hiring_password
```

Expected output:
```
+------------------------+
| Tables_in_hiring_copilot |
+------------------------+
| users                  |
| jobs                   |
| candidates             |
| resumes                |
| applications           |
| agent_logs             |
+------------------------+
```

---

## Step 6: Verify Connection

Start the backend and check logs:
```bash
cd c:\Projects\LangChain-LangGraph-Project
uvicorn backend.main:app --reload --port 8000
```

Look for:
```
✅ AI Hiring Co-Pilot API ready
INFO:sqlalchemy.engine.Engine: SELECT 1
```

If you see database connection errors, verify:
1. MySQL service is running
2. `.env` DATABASE_URL is correct
3. User credentials match your setup
4. Database `hiring_copilot` exists

---

## Step 7: Test with Demo Credentials

1. Start backend: `uvicorn backend.main:app --reload --port 8000`
2. Start frontend: `cd frontend && npm run dev`
3. Navigate to http://localhost:5173/login
4. Log in with:
   - Email: `recruiter@hiringapp.com`
   - Password: `Admin@123`
5. Create a job and upload a resume to verify database persistence

---

## Troubleshooting

### "Can't connect to MySQL server"
```bash
# Check if MySQL service is running
wsl -e sudo systemctl status mysql  # WSL
Get-Service mysql80                 # Windows (replace mysql80 with your version)
```

### "Access denied for user 'hiring_user'@'localhost'"
- Verify password in `.env` matches what you set in Step 2
- Check user exists: `mysql -u root -p -e "SELECT user, host FROM mysql.user;"`

### "Unknown database 'hiring_copilot'"
- Ensure database was created: `mysql -u root -p -e "SHOW DATABASES;"`
- Create it if missing: `mysql -u root -p -e "CREATE DATABASE hiring_copilot;"`

### "SQLAlchemy not recognizing MySQL dialect"
- Reinstall: `pip install --upgrade sqlalchemy pymysql`
- Restart backend after installation

---

## Switching Back to SQLite (Development)

If you want to revert to SQLite:

```env
# In .env
DATABASE_URL=sqlite:///./hiring_copilot.db
```

Then restart the backend. SQLite doesn't require any server setup.

---

## Production Deployment Notes

- Use **MySQL 8.0+** (supports JSON data type required for the schema)
- Enable SSL/TLS for remote connections
- Set strong passwords (minimum 16 characters)
- Create separate read-only users for analytics/reports
- Use connection pooling (SQLAlchemy's default is 5 connections)
- Enable query logging for debugging:
  ```sql
  SET GLOBAL general_log = 'ON';
  ```
- Consider managed MySQL services (AWS RDS, Google Cloud SQL) for production

---

## Current Architecture

The database schema supports:
- **Users**: Admin, Recruiter, Hiring Manager roles
- **Jobs**: Job descriptions with parsed requirements
- **Candidates**: Candidate profiles from resume uploads
- **Resumes**: Uploaded files (PDF/DOCX) with extracted text
- **Applications**: Job-candidate associations with AI scores
- **Agent Logs**: Workflow execution traces for debugging

All models are in `database/init_db.py` and use SQLAlchemy ORM.
The backend automatically creates tables and seeds demo data on startup.

---

## Questions?

Refer to:
- SQLAlchemy Docs: https://docs.sqlalchemy.org/
- MySQL Docs: https://dev.mysql.com/doc/
- LangChain LangGraph Checkpointing: https://langchain-ai.github.io/langgraph/
