import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'
import Layout from '@/components/Layout'
import ProtectedRoute from '@/components/ProtectedRoute'
import LoginPage      from '@/pages/LoginPage'
import DashboardPage  from '@/pages/DashboardPage'
import JobsPage       from '@/pages/JobsPage'
import WorkflowPage   from '@/pages/WorkflowPage'
import ReviewPage     from '@/pages/ReviewPage'
import InterviewsPage from '@/pages/InterviewsPage'

const queryClient = new QueryClient({
  defaultOptions: { queries: { staleTime: 30_000, retry: 1 } },
})

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/*"
            element={
              <ProtectedRoute>
                <Layout>
                  <Routes>
                    <Route path="/"            element={<Navigate to="/dashboard" replace />} />
                    <Route path="/dashboard"   element={<DashboardPage />} />
                    <Route path="/jobs"        element={<JobsPage />} />
                    <Route path="/workflow"    element={<WorkflowPage />} />
                    <Route path="/review"      element={<ReviewPage />} />
                    <Route path="/interviews"  element={<InterviewsPage />} />
                  </Routes>
                </Layout>
              </ProtectedRoute>
            }
          />
        </Routes>
      </BrowserRouter>
      <Toaster
        position="top-right"
        toastOptions={{
          style: { fontFamily: 'Inter, system-ui, sans-serif', fontSize: '13px', borderRadius: '10px' },
          success: { iconTheme: { primary: '#10b981', secondary: '#fff' } },
          error:   { iconTheme: { primary: '#ef4444', secondary: '#fff' } },
        }}
      />
    </QueryClientProvider>
  )
}
