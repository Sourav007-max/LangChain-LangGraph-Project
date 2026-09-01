import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { User, CandidateScore, InterviewSlot } from '@/types'

interface AppStore {
  // Auth
  token: string | null
  user: User | null
  setAuth: (token: string, user: User) => void
  logout: () => void

  // Active workflow
  activeThreadId: string | null
  pendingShortlist: CandidateScore[]
  setWorkflowResult: (threadId: string, shortlisted: CandidateScore[]) => void
  clearWorkflow: () => void

  // Completed workflow output
  lastInterviews: InterviewSlot[]
  lastReport: string
  setWorkflowOutput: (interviews: InterviewSlot[], report: string) => void
}

const useStore = create<AppStore>()(
  persist(
    (set) => ({
      token: null,
      user: null,
      setAuth: (token, user) => set({ token, user }),
      logout: () => set({ token: null, user: null, activeThreadId: null, pendingShortlist: [] }),

      activeThreadId: null,
      pendingShortlist: [],
      setWorkflowResult: (threadId, shortlisted) =>
        set({ activeThreadId: threadId, pendingShortlist: shortlisted }),
      clearWorkflow: () => set({ activeThreadId: null, pendingShortlist: [] }),

      lastInterviews: [],
      lastReport: '',
      setWorkflowOutput: (interviews, report) => set({ lastInterviews: interviews, lastReport: report }),
    }),
    {
      name: 'hiring-copilot-store',
      // Only persist auth — never persist sensitive workflow data to localStorage
      partialize: (s) => ({ token: s.token, user: s.user, activeThreadId: s.activeThreadId }),
    }
  )
)

export default useStore
