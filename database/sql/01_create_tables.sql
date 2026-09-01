-- =============================================================================
--  PHASE 5 — DATABASE DESIGN (MySQL)
--  AI Hiring Co-Pilot: Multi-Agent Recruitment Platform using LangGraph
--
--  Run this file in MySQL Workbench or MySQL CLI:
--    mysql -u hiring_user -p hiring_copilot < 01_create_tables.sql
-- =============================================================================

-- Use the correct database
USE hiring_copilot;

-- Enable strict mode for data integrity
SET sql_mode = 'STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO';

-- =============================================================================
-- TABLE 1: users
-- WHY: Authentication and authorization for recruiters, managers, admins
-- =============================================================================
CREATE TABLE IF NOT EXISTS users (
    id            BIGINT UNSIGNED  NOT NULL AUTO_INCREMENT,
    email         VARCHAR(255)     NOT NULL,
    password_hash VARCHAR(255)     NOT NULL,               -- bcrypt hash, NEVER plaintext
    full_name     VARCHAR(255)     NOT NULL,
    role          ENUM('admin', 'recruiter', 'hiring_manager', 'interviewer') 
                                   NOT NULL DEFAULT 'recruiter',
    is_active     BOOLEAN          NOT NULL DEFAULT TRUE,
    last_login    DATETIME         NULL,
    created_at    DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    PRIMARY KEY (id),
    UNIQUE KEY uq_users_email (email),
    INDEX idx_users_role (role),
    INDEX idx_users_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- LESSON: Why utf8mb4?
-- Regular utf8 in MySQL only supports 3-byte characters.
-- utf8mb4 supports 4-byte characters (emojis, some Asian scripts).
-- Always use utf8mb4 for international applications.


-- =============================================================================
-- TABLE 2: jobs
-- WHY: Each job posting that requires recruitment
-- =============================================================================
CREATE TABLE IF NOT EXISTS jobs (
    id                  BIGINT UNSIGNED  NOT NULL AUTO_INCREMENT,
    recruiter_id        BIGINT UNSIGNED  NOT NULL,           -- who is managing this job
    title               VARCHAR(255)     NOT NULL,
    department          VARCHAR(100)     NULL,
    location            VARCHAR(255)     NULL,
    job_type            ENUM('full_time', 'part_time', 'contract', 'internship') 
                                         NOT NULL DEFAULT 'full_time',
    experience_level    ENUM('junior', 'mid', 'senior', 'lead', 'executive') 
                                         NOT NULL DEFAULT 'mid',
    salary_min          DECIMAL(10,2)    NULL,
    salary_max          DECIMAL(10,2)    NULL,
    currency            CHAR(3)          NOT NULL DEFAULT 'USD',
    description_raw     LONGTEXT         NOT NULL,           -- original JD text
    description_parsed  JSON             NULL,               -- AI-extracted requirements
    required_skills     JSON             NULL,               -- ["Python", "FastAPI", ...]
    nice_to_have_skills JSON             NULL,
    min_experience_yrs  TINYINT UNSIGNED NULL,
    status              ENUM('draft', 'active', 'paused', 'closed', 'filled') 
                                         NOT NULL DEFAULT 'draft',
    deadline            DATE             NULL,
    created_at          DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    PRIMARY KEY (id),
    FOREIGN KEY fk_jobs_recruiter (recruiter_id) REFERENCES users(id) ON DELETE RESTRICT,
    INDEX idx_jobs_status (status),
    INDEX idx_jobs_recruiter (recruiter_id),
    FULLTEXT INDEX ft_jobs_title_desc (title, description_raw)
    -- FULLTEXT index enables fast keyword search across job titles and descriptions
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- =============================================================================
-- TABLE 3: candidates
-- WHY: Core entity — every person who applies to any job
-- =============================================================================
CREATE TABLE IF NOT EXISTS candidates (
    id              BIGINT UNSIGNED  NOT NULL AUTO_INCREMENT,
    email           VARCHAR(255)     NOT NULL,
    full_name       VARCHAR(255)     NOT NULL,
    phone           VARCHAR(30)      NULL,
    linkedin_url    VARCHAR(500)     NULL,
    github_url      VARCHAR(500)     NULL,
    location        VARCHAR(255)     NULL,
    source          ENUM('direct', 'linkedin', 'referral', 'job_board', 'agency') 
                                     NOT NULL DEFAULT 'direct',
    gdpr_consent    BOOLEAN          NOT NULL DEFAULT FALSE,  -- MUST be true before processing
    created_at      DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    PRIMARY KEY (id),
    UNIQUE KEY uq_candidates_email (email),
    INDEX idx_candidates_source (source)
    -- NOTE: No full profile data here — detailed data lives in resumes table
    -- This follows data minimization principle (GDPR Art. 5)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- =============================================================================
-- TABLE 4: resumes
-- WHY: Each resume upload (candidate may have multiple versions)
-- =============================================================================
CREATE TABLE IF NOT EXISTS resumes (
    id                  BIGINT UNSIGNED  NOT NULL AUTO_INCREMENT,
    candidate_id        BIGINT UNSIGNED  NOT NULL,
    file_name           VARCHAR(255)     NOT NULL,
    file_path           VARCHAR(500)     NOT NULL,           -- secure server path
    file_size_bytes     INT UNSIGNED     NULL,
    file_type           ENUM('pdf', 'docx', 'doc', 'txt') NOT NULL DEFAULT 'pdf',
    raw_text            LONGTEXT         NULL,               -- extracted text from PDF
    parsed_data         JSON             NULL,               -- AI-structured extraction
    skills_extracted    JSON             NULL,               -- ["Python", "Docker", ...]
    experience_years    DECIMAL(4,1)     NULL,               -- 5.5 = 5 years 6 months
    education_level     ENUM('high_school', 'bachelors', 'masters', 'phd', 'other') NULL,
    current_title       VARCHAR(255)     NULL,
    embedding_id        VARCHAR(100)     NULL,               -- Pinecone vector ID
    is_active           BOOLEAN          NOT NULL DEFAULT TRUE,  -- latest resume version
    parse_status        ENUM('pending', 'processing', 'completed', 'failed') 
                                         NOT NULL DEFAULT 'pending',
    parse_error         TEXT             NULL,
    uploaded_at         DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP,
    parsed_at           DATETIME         NULL,
    
    PRIMARY KEY (id),
    FOREIGN KEY fk_resumes_candidate (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE,
    INDEX idx_resumes_candidate (candidate_id),
    INDEX idx_resumes_parse_status (parse_status),
    INDEX idx_resumes_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- =============================================================================
-- TABLE 5: applications
-- WHY: Links candidates to specific job openings (many-to-many)
-- =============================================================================
CREATE TABLE IF NOT EXISTS applications (
    id              BIGINT UNSIGNED  NOT NULL AUTO_INCREMENT,
    job_id          BIGINT UNSIGNED  NOT NULL,
    candidate_id    BIGINT UNSIGNED  NOT NULL,
    resume_id       BIGINT UNSIGNED  NOT NULL,
    status          ENUM(
                        'applied',          -- just submitted
                        'screening',        -- AI is processing
                        'shortlisted',      -- AI recommended, awaiting human review
                        'human_review',     -- recruiter is reviewing
                        'approved',         -- recruiter approved for interview
                        'rejected',         -- not moving forward
                        'interview_scheduled',
                        'interview_completed',
                        'offer_made',
                        'offer_accepted',
                        'offer_rejected',
                        'hired',
                        'withdrawn'
                    ) NOT NULL DEFAULT 'applied',
    ai_score        TINYINT UNSIGNED NULL,          -- 0-100 AI compatibility score
    ai_reasoning    TEXT             NULL,           -- explanation of score
    recruiter_notes TEXT             NULL,
    rejection_reason ENUM(
                        'skills_mismatch',
                        'experience_too_low',
                        'experience_too_high',
                        'location_mismatch',
                        'salary_mismatch',
                        'culture_fit',
                        'other'
                    ) NULL,
    applied_at      DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    PRIMARY KEY (id),
    UNIQUE KEY uq_applications (job_id, candidate_id),      -- one application per job per candidate
    FOREIGN KEY fk_app_job (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
    FOREIGN KEY fk_app_candidate (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE,
    FOREIGN KEY fk_app_resume (resume_id) REFERENCES resumes(id) ON DELETE RESTRICT,
    INDEX idx_applications_status (status),
    INDEX idx_applications_ai_score (ai_score),
    INDEX idx_applications_job (job_id),
    INDEX idx_applications_candidate (candidate_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- =============================================================================
-- TABLE 6: agent_logs
-- WHY: Full audit trail of every AI agent action (compliance + debugging)
-- =============================================================================
CREATE TABLE IF NOT EXISTS agent_logs (
    id              BIGINT UNSIGNED  NOT NULL AUTO_INCREMENT,
    session_id      VARCHAR(100)     NOT NULL,               -- LangGraph thread ID
    agent_name      VARCHAR(100)     NOT NULL,
    action_type     VARCHAR(100)     NOT NULL,               -- e.g., "parse_resume", "calculate_score"
    input_summary   TEXT             NULL,                   -- brief description of input (no PII)
    output_summary  TEXT             NULL,                   -- brief description of output
    model_used      VARCHAR(100)     NULL,                   -- e.g., "gpt-4o"
    tokens_used     INT UNSIGNED     NULL,
    latency_ms      INT UNSIGNED     NULL,
    cost_usd        DECIMAL(8,6)     NULL,
    status          ENUM('success', 'failed', 'retried') NOT NULL DEFAULT 'success',
    error_message   TEXT             NULL,
    langsmith_trace VARCHAR(500)     NULL,                   -- LangSmith trace URL
    entity_type     VARCHAR(50)      NULL,                   -- 'application', 'resume', 'job'
    entity_id       BIGINT UNSIGNED  NULL,
    created_at      DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (id),
    INDEX idx_agent_logs_session (session_id),
    INDEX idx_agent_logs_agent (agent_name),
    INDEX idx_agent_logs_entity (entity_type, entity_id),
    INDEX idx_agent_logs_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- =============================================================================
-- TABLE 9: skills (reference/taxonomy table)
-- WHY: Normalize skill names to avoid duplicates ("ML" vs "Machine Learning")
-- =============================================================================
CREATE TABLE IF NOT EXISTS skills (
    id          INT UNSIGNED     NOT NULL AUTO_INCREMENT,
    name        VARCHAR(100)     NOT NULL,
    category    ENUM('programming_language', 'framework', 'database', 'cloud', 
                     'soft_skill', 'tool', 'methodology', 'other') 
                                 NOT NULL DEFAULT 'other',
    aliases     JSON             NULL,   -- ["ML", "Machine Learning", "ML Engineering"]
    is_active   BOOLEAN          NOT NULL DEFAULT TRUE,
    
    PRIMARY KEY (id),
    UNIQUE KEY uq_skills_name (name),
    INDEX idx_skills_category (category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- =============================================================================
-- VIEWS — Useful queries pre-built
-- =============================================================================

-- View: Active pipeline per job
CREATE OR REPLACE VIEW v_job_pipeline AS
SELECT 
    j.id AS job_id,
    j.title AS job_title,
    j.status AS job_status,
    COUNT(a.id) AS total_applications,
    SUM(CASE WHEN a.status = 'applied' THEN 1 ELSE 0 END) AS new_applications,
    SUM(CASE WHEN a.status = 'shortlisted' THEN 1 ELSE 0 END) AS shortlisted,
    SUM(CASE WHEN a.status = 'interview_scheduled' THEN 1 ELSE 0 END) AS interviews_scheduled,
    SUM(CASE WHEN a.status = 'hired' THEN 1 ELSE 0 END) AS hired,
    AVG(a.ai_score) AS avg_ai_score
FROM jobs j
LEFT JOIN applications a ON j.id = a.job_id
GROUP BY j.id, j.title, j.status;

-- View: Candidate application history
CREATE OR REPLACE VIEW v_candidate_applications AS
SELECT
    c.id AS candidate_id,
    c.full_name,
    c.email,
    j.title AS job_title,
    a.status AS application_status,
    a.ai_score,
    a.applied_at
FROM candidates c
JOIN applications a ON c.id = a.candidate_id
JOIN jobs j ON a.job_id = j.id
ORDER BY a.applied_at DESC;


-- =============================================================================
-- SAMPLE DATA — for development and testing
-- =============================================================================

-- Insert admin user (password: Admin@123 — bcrypt hash shown below)
INSERT INTO users (email, password_hash, full_name, role) VALUES
('admin@hiringcopilot.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TqFzGcJTf4J7.aRGQLsxkGXkzm3q', 'Admin User', 'admin'),
('recruiter@hiringcopilot.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TqFzGcJTf4J7.aRGQLsxkGXkzm3q', 'Sarah Recruiter', 'recruiter'),
('manager@hiringcopilot.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TqFzGcJTf4J7.aRGQLsxkGXkzm3q', 'Mike Manager', 'hiring_manager');

-- Insert sample job
INSERT INTO jobs (recruiter_id, title, department, location, job_type, experience_level, 
                  salary_min, salary_max, description_raw, status, min_experience_yrs) VALUES
(2, 'Senior Python Developer', 'Engineering', 'Remote (US)', 'full_time', 'senior',
 120000, 160000,
 'We are looking for a Senior Python Developer with strong FastAPI and cloud experience. 
  Requirements: 5+ years Python, FastAPI or Django, PostgreSQL/MySQL, AWS/GCP, Docker.
  Nice to have: Kubernetes, LangChain, ML experience.',
 'active', 5);

-- Insert sample skills
INSERT INTO skills (name, category, aliases) VALUES
('Python', 'programming_language', '["py", "Python3", "python"]'),
('FastAPI', 'framework', '["fast-api", "Fast API"]'),
('LangChain', 'framework', '["lang-chain", "Langchain"]'),
('PostgreSQL', 'database', '["postgres", "psql", "PostgreSQL"]'),
('MySQL', 'database', '["mysql", "MariaDB"]'),
('Docker', 'tool', '["docker", "containerization"]'),
('AWS', 'cloud', '["Amazon Web Services", "amazon aws"]'),
('React', 'framework', '["ReactJS", "React.js"]'),
('TypeScript', 'programming_language', '["TS", "typescript"]');
