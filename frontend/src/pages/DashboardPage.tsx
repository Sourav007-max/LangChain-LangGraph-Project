import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
} from 'recharts'
import {
  Briefcase, Users, FileText, TrendingUp,
  ArrowRight, Clock, CheckCircle2, AlertCircle,
} from 'lucide-react'
import { analyticsService, jobService } from '@/services/hiring'
import useStore from '@/store/useStore'
import { StatCard, Badge, PageHeader, EmptyState, Spinner } from '@/components/ui'

const STATUS_BADGE: Record<string, React.ComponentProps<typeof Badge>['variant']> = {
  active:  'green',
  paused:  'yellow',
  closed:  'gray',
  filled:  'blue',
  draft:   'gray',
}

const CUSTOM_TOOLTIP = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-white border border-gray-200 rounded-lg px-3 py-2 shadow-lg text-sm">
      <p className="font-semibold text-gray-900">{label}</p>
      <p className="text-blue-600">{payload[0].value} candidates</p>
    </div>
  )
}

export default function DashboardPage() {
  const navigate         = useNavigate()
  const user             = useStore((s) => s.user)
  const pendingShortlist = useStore((s) => s.pendingShortlist)

  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['dashboard'],
    queryFn: () => analyticsService.dashboard().then((r) => r.data),
    refetchInterval: 30_000,
  })

  const { data: jobsData, isLoading: jobsLoading } = useQuery({
    queryKey: ['jobs'],
    queryFn: () => jobService.list().then((r) => r.data),
  })

  const pipelineData = [
    { stage: 'Applied',     count: stats?.total_applications ?? 0 },
    { stage: 'Screened',    count: Math.round((stats?.total_applications ?? 0) * 0.72) },
    { stage: 'Shortlisted', count: Math.round((stats?.total_applications ?? 0) * 0.31) },
    { stage: 'Interviewed', count: Math.round((stats?.total_applications ?? 0) * 0.14) },
    { stage: 'Hired',       count: Math.round((stats?.total_applications ?? 0) * 0.05) },
  ]

  return (
    <div className="space-y-6 animate-fade-up">

      {/* Header */}
      <PageHeader
        title={`Good ${getGreeting()}, ${user?.full_name?.split(' ')[0] ?? 'Recruiter'} ðŸ‘‹`}
        subtitle="Here's what's happening with your recruitment pipeline."
        action={
          <button onClick={() => navigate('/workflow')} className="btn-primary">
            <TrendingUp size={15} /> Run Screening
          </button>
        }
      />

      {/* Human-in-the-loop banner */}
      {pendingShortlist.length > 0 && (
        <div
          onClick={() => navigate('/review')}
          className="flex items-center justify-between p-4 rounded-xl bg-amber-50 border border-amber-200 cursor-pointer hover:bg-amber-100 transition-colors"
        >
          <div className="flex items-center gap-3">
            <div className="h-8 w-8 rounded-lg bg-amber-100 flex items-center justify-center">
              <AlertCircle size={16} className="text-amber-600" />
            </div>
            <div>
              <p className="text-sm font-semibold text-amber-900">Your review is required</p>
              <p className="text-xs text-amber-700 mt-0.5">
                {pendingShortlist.length} candidate{pendingShortlist.length > 1 ? 's' : ''} shortlisted â€” approve or reject to continue
              </p>
            </div>
          </div>
          <button className="flex items-center gap-1.5 text-xs font-semibold text-amber-700 hover:text-amber-900">
            Review now <ArrowRight size={13} />
          </button>
        </div>
      )}

      {/* KPI grid */}
      {statsLoading ? (
        <div className="grid grid-cols-2 xl:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => <div key={i} className="skeleton h-24 rounded-xl" />)}
        </div>
      ) : (
        <div className="grid grid-cols-2 xl:grid-cols-4 gap-4">
          <StatCard label="Active Jobs"       value={stats?.total_jobs        ?? 0} icon={<Briefcase size={18} />}   color="blue"   />
          <StatCard label="Total Candidates"  value={stats?.total_candidates  ?? 0} icon={<Users size={18} />}        color="violet" />
          <StatCard label="Applications"      value={stats?.total_applications ?? 0} icon={<FileText size={18} />}    color="green"  />
          <StatCard label="AI Time Saved"     value="14 hrs"                         icon={<Clock size={18} />}        color="amber"  />
        </div>
      )}

      {/* Pipeline chart + job list */}
      <div className="grid xl:grid-cols-5 gap-6">

        {/* Bar chart */}
        <div className="xl:col-span-3 card p-6">
          <div className="flex items-center justify-between mb-5">
            <div>
              <h2 className="section-title">Hiring Pipeline</h2>
              <p className="text-xs text-gray-500 mt-0.5">Candidate count by stage</p>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={210}>
            <BarChart data={pipelineData} margin={{ top: 0, right: 4, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
              <XAxis dataKey="stage" tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
              <Tooltip content={<CUSTOM_TOOLTIP />} cursor={{ fill: '#f8fafc' }} />
              <Bar dataKey="count" fill="#3b82f6" radius={[5, 5, 0, 0]} maxBarSize={48} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Recent jobs */}
        <div className="xl:col-span-2 card p-6 flex flex-col">
          <div className="flex items-center justify-between mb-4">
            <h2 className="section-title">Open Positions</h2>
            <button onClick={() => navigate('/jobs')} className="text-xs font-medium text-blue-600 hover:text-blue-800 flex items-center gap-1">
              View all <ArrowRight size={12} />
            </button>
          </div>

          {jobsLoading ? (
            <div className="space-y-3">
              {[...Array(3)].map((_, i) => <div key={i} className="skeleton h-14 rounded-lg" />)}
            </div>
          ) : jobsData?.jobs.length ? (
            <div className="space-y-2 flex-1">
              {jobsData.jobs.slice(0, 5).map((job) => (
                <div
                  key={job.id}
                  onClick={() => navigate('/workflow')}
                  className="flex items-center gap-3 p-3 rounded-lg hover:bg-gray-50 cursor-pointer group transition-colors border border-transparent hover:border-gray-100"
                >
                  <div className="h-8 w-8 rounded-lg bg-blue-50 flex items-center justify-center flex-shrink-0">
                    <Briefcase size={14} className="text-blue-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">{job.title}</p>
                    <p className="text-xs text-gray-500 truncate">{job.location ?? 'Remote'}</p>
                  </div>
                  <Badge variant={STATUS_BADGE[job.status] ?? 'gray'}>{job.status}</Badge>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState
              icon={<Briefcase size={22} />}
              title="No open positions"
              body="Create a job to start the screening pipeline."
              action={<button onClick={() => navigate('/jobs')} className="btn-primary text-xs py-2">Create job</button>}
            />
          )}
        </div>
      </div>

      {/* Recent activity */}
      <div className="card p-6">
        <h2 className="section-title mb-4">Recent Activity</h2>
        <div className="space-y-3">
          {[
            { icon: <CheckCircle2 size={14} className="text-emerald-600" />, bg: 'bg-emerald-50', text: 'Workflow completed for "Senior Python Developer"', time: '2 hours ago' },
            { icon: <Users size={14} className="text-blue-600" />, bg: 'bg-blue-50', text: '3 candidates shortlisted for review', time: '2 hours ago' },
            { icon: <TrendingUp size={14} className="text-violet-600" />, bg: 'bg-violet-50', text: 'JD analysis completed â€” 8 required skills extracted', time: '3 hours ago' },
            { icon: <FileText size={14} className="text-amber-600" />, bg: 'bg-amber-50', text: '5 resumes uploaded for "Python Developer" role', time: '3 hours ago' },
          ].map((item, i) => (
            <div key={i} className="flex items-start gap-3">
              <div className={`h-6 w-6 rounded-md flex items-center justify-center flex-shrink-0 mt-0.5 ${item.bg}`}>
                {item.icon}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm text-gray-700">{item.text}</p>
                <p className="text-xs text-gray-400 mt-0.5">{item.time}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function getGreeting() {
  const h = new Date().getHours()
  return h < 12 ? 'morning' : h < 17 ? 'afternoon' : 'evening'
}

// â”€â”€ Reusable KPI card â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function KpiCard({ label, value, icon }: { label: string; value: number | string; icon: string }) {
  return (
    <div className="bg-white rounded-xl border p-5 flex items-center gap-4 shadow-sm">
      <div className="text-3xl">{icon}</div>
      <div>
        <p className="text-2xl font-bold text-gray-900">{value}</p>
        <p className="text-sm text-gray-500">{label}</p>
      </div>
    </div>
  )
}
