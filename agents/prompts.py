"""Shared prompt templates used by the hiring agents."""

from langchain_core.prompts import ChatPromptTemplate


JD_ANALYSIS_PROMPT = ChatPromptTemplate.from_template("""
You are an expert technical recruiter. Analyse this job description and extract
the requirements. Return ONLY valid JSON — no markdown, no extra text.

Job Description:
{jd_text}

JSON schema to return:
{{
  "required_skills":       ["skill1", "skill2"],
  "nice_to_have_skills":   ["skill1"],
  "min_experience_years":  <integer or 0>,
  "education_requirement": "any|bachelors|masters|phd",
  "job_summary":           "<two sentence summary>",
  "key_responsibilities":  ["resp1", "resp2", "resp3"]
}}
""")

RESUME_PARSING_PROMPT = ChatPromptTemplate.from_template("""
You are an expert resume parser. Extract structured data from this resume.
Return ONLY valid JSON — no markdown, no extra text.

Resume Text:
{resume_text}

JSON schema to return:
{{
  "full_name":               "<name or null>",
  "email":                   "<email or null>",
  "phone":                   "<phone or null>",
  "current_title":           "<current job title or null>",
  "total_experience_years":  <number or 0>,
  "skills":                  ["skill1", "skill2"],
  "education": [
    {{"degree": "...", "field": "...", "institution": "...", "year": <int or null>}}
  ],
  "work_experience": [
    {{"title": "...", "company": "...", "years": <float>, "description": "..."}}
  ],
  "certifications": ["cert1"]
}}
""")

CANDIDATE_SCORING_PROMPT = ChatPromptTemplate.from_template("""
You are a senior technical recruiter scoring a candidate against job requirements.
Return ONLY valid JSON — no markdown, no extra text.

Job Requirements:
{requirements}

Candidate Profile:
{candidate}

Scoring rubric:
  90-100: Perfect match — all requirements met, exceeds in key areas
  75-89 : Strong match — most requirements met
  60-74 : Decent match — some gaps, but trainable
  40-59 : Weak match — significant gaps
  0-39  : Poor match — fundamental requirements missing

JSON schema to return:
{{
  "score":                  <integer 0-100>,
  "recommendation":         "STRONGLY_RECOMMEND|RECOMMEND|MAYBE|REJECT",
  "reasoning":              "<3 concise sentences>",
  "strengths":              ["strength1", "strength2"],
  "gaps":                   ["gap1"],
  "skill_match_percentage": <integer 0-100>,
  "experience_match":       "exceeds|meets|below"
}}
""")

INTERVIEW_QUESTIONS_PROMPT = ChatPromptTemplate.from_template("""
Generate exactly {questions_count} targeted technical interview questions for this candidate
based on the job requirements. Focus on their skill gaps and experience depth.
Return ONLY a JSON array of {questions_count} question strings.

Candidate: {candidate}
Job Requirements: {requirements}
""")

REPORT_GENERATION_PROMPT = ChatPromptTemplate.from_template("""
You are a senior HR analytics expert. Write a professional hiring pipeline report
in clean Markdown. Use headers, bullet points, and a table where appropriate.

Data:
  Job ID              : {job_id}
  Total resumes       : {total_resumes}
  Parsed successfully : {parsed_count}
  Shortlisted         : {shortlisted_count}
  HR approved         : {approved_count}
  Interviews scheduled: {interviews_count}

Top candidates:
{top_candidates}

Skill gaps observed (skills required but rare in applicant pool):
{skill_gaps}

Structure the report with:
1. Executive Summary (3 sentences)
2. Pipeline Funnel (table: stage | count | conversion %)
3. Top 3 Candidate Profiles
4. Skill Gap Analysis
5. Hiring Recommendation
6. Suggested Next Steps
""")
