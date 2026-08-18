import api from './api'
import type { Job, DashboardStats, WorkflowState, InterviewSlot } from '@/types'

// ── Auth ──────────────────────────────────────────────────────────────────────
export const authService = {
  login: (email: string, password: string) =>
    api.post<{ access_token: string; full_name: string; role: string; user_id: number }>(
      '/auth/login', { email, password }
    ),
  register: (email: string, password: string, full_name: string, role: string) =>
    api.post('/auth/register', { email, password, full_name, role }),
}

// ── Jobs ──────────────────────────────────────────────────────────────────────
export const jobService = {
  list: (status?: string) =>
    api.get<{ jobs: Job[] }>('/jobs', { params: status ? { status } : {} }),
  get: (id: number) =>
    api.get<Job>(`/jobs/${id}`),
  create: (data: Omit<Job, 'id' | 'status'> & { description_raw: string; min_experience_yrs?: number }) =>
    api.post<{ job_id: number; title: string }>('/jobs', data),
}

// ── Resumes ───────────────────────────────────────────────────────────────────
export const resumeService = {
  upload: (file: File, candidate_email: string, candidate_name: string) => {
    const form = new FormData()
    form.append('file', file)
    form.append('candidate_email', candidate_email)
    form.append('candidate_name', candidate_name)
    return api.post<{ resume_id: number; candidate_id: number; status: string }>(
      '/resumes/upload', form, { headers: { 'Content-Type': 'multipart/form-data' } }
    )
  },
}

// ── Workflows ─────────────────────────────────────────────────────────────────
export const workflowService = {
  start: (job_id: number, resume_ids: number[]) =>
    api.post<WorkflowState>('/workflows/start', { job_id, resume_ids }),
  getState: (thread_id: string) =>
    api.get<WorkflowState>(`/workflows/${thread_id}/state`),
  approve: (thread_id: string, approved_candidates: object[], decision: string, feedback?: string) =>
    api.post<{ interviews: InterviewSlot[]; report: string }>(
      `/workflows/${thread_id}/approve`,
      { approved_candidates, decision, feedback }
    ),
}

// ── Analytics ─────────────────────────────────────────────────────────────────
export const analyticsService = {
  dashboard: () => api.get<DashboardStats>('/analytics/dashboard'),
}
