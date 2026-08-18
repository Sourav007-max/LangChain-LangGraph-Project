// All shared TypeScript types for the entire frontend

export interface User {
  id: number
  email: string
  full_name: string
  role: 'admin' | 'recruiter' | 'hiring_manager' | 'interviewer'
}

export interface AuthState {
  token: string | null
  user: User | null
}

export interface Job {
  id: number
  title: string
  department: string | null
  location: string | null
  job_type: string
  experience_level: string
  status: string
  description_raw?: string
  required_skills?: string[]
}

export interface Candidate {
  id: number
  email: string
  full_name: string
  source: string
}

export interface CandidateScore {
  candidate_name: string
  candidate_email: string
  score: number
  recommendation: 'STRONGLY_RECOMMEND' | 'RECOMMEND' | 'MAYBE' | 'REJECT'
  reasoning: string
  strengths: string[]
  gaps: string[]
  skill_match_percentage: number
  experience_match: 'exceeds' | 'meets' | 'below'
}

export interface InterviewSlot {
  candidate_name: string
  candidate_email: string
  interview_date: string
  interview_time: string
  meeting_link: string
  interview_type: string
  ai_questions: string[]
  email_sent: boolean
}

export interface WorkflowState {
  thread_id: string
  status: 'running' | 'waiting_human_review' | 'completed' | 'failed'
  shortlisted: CandidateScore[]
  total_scored: number
}

export interface DashboardStats {
  total_jobs: number
  total_candidates: number
  total_applications: number
  generated_at: string
}
