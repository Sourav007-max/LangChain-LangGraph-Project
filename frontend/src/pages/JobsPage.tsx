import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { Briefcase, Plus, X, MapPin, Clock, DollarSign, Rocket } from 'lucide-react'
import { jobService } from '@/services/hiring'
import { PageHeader, Badge, EmptyState, Spinner } from '@/components/ui'
import type { Job } from '@/types'

const STATUS_BADGE: Record<string, React.ComponentProps<typeof Badge>['variant']> = {
  active: 'green', paused: 'yellow', closed: 'gray', filled: 'blue', draft: 'gray',
}

const LEVEL_LABEL: Record<string, string> = {
  junior: 'Junior', mid: 'Mid-level', senior: 'Senior', lead: 'Lead', executive: 'Executive',
}

function JobCard({ job, onScreen }: { job: Job; onScreen: (id: number) => void }) {
  return (
    <div className="card p-5 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3">
          <div className="h-10 w-10 rounded-xl bg-blue-50 flex items-center justify-center flex-shrink-0">
            <Briefcase size={18} className="text-blue-600" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">{job.title}</h3>
            <div className="flex flex-wrap items-center gap-x-3 gap-y-1 mt-1.5 text-xs text-gray-500">
              {job.department && <span>{job.department}</span>}
              {job.location && <span className="flex items-center gap-1"><MapPin size={10} /> {job.location}</span>}
              {job.job_type && <span className="flex items-center gap-1"><Clock size={10} /> {job.job_type.replace('_', ' ')}</span>}
              {(job as any).salary_min && (
                <span className="flex items-center gap-1">
                  <DollarSign size={10} /> {((job as any).salary_min / 1000).toFixed(0)}k–{((job as any).salary_max / 1000).toFixed(0)}k
                </span>
              )}
            </div>
          </div>
        </div>
        <div className="flex flex-col items-end gap-2">
          <Badge variant={STATUS_BADGE[job.status] ?? 'gray'}>{job.status}</Badge>
          <Badge variant="gray">{LEVEL_LABEL[job.experience_level ?? 'mid'] ?? job.experience_level}</Badge>
        </div>
      </div>

      {job.required_skills?.length ? (
        <div className="flex flex-wrap gap-1.5 mt-4">
          {job.required_skills.slice(0, 6).map((skill) => (
            <span key={skill} className="px-2 py-0.5 bg-gray-100 text-gray-600 rounded text-xs">{skill}</span>
          ))}
          {job.required_skills.length > 6 && (
            <span className="px-2 py-0.5 bg-gray-100 text-gray-400 rounded text-xs">+{job.required_skills.length - 6}</span>
          )}
        </div>
      ) : null}

      <div className="flex items-center gap-2 mt-4 pt-4 border-t border-gray-100">
        <button onClick={() => onScreen(job.id)} className="btn-primary text-xs py-2 flex-1">
          <Rocket size={13} /> Screen Candidates
        </button>
      </div>
    </div>
  )
}

function CreateJobModal({ onClose }: { onClose: () => void }) {
  const qc = useQueryClient()
  const [form, setForm] = useState({
    title: '', department: '', location: '', job_type: 'full_time',
    experience_level: 'mid', salary_min: '', salary_max: '',
    description_raw: '', min_experience_yrs: '',
  })

  const mutation = useMutation({
    mutationFn: () => jobService.create({
      ...form,
      salary_min:        form.salary_min ? parseFloat(form.salary_min) : undefined,
      salary_max:        form.salary_max ? parseFloat(form.salary_max) : undefined,
      min_experience_yrs: form.min_experience_yrs ? parseInt(form.min_experience_yrs) : undefined,
    } as any),
    onSuccess: () => {
      toast.success('Job created!')
      qc.invalidateQueries({ queryKey: ['jobs'] })
      onClose()
    },
    onError: (err: any) => toast.error(err.response?.data?.detail ?? 'Failed to create job'),
  })

  const set = (k: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) =>
    setForm(f => ({ ...f, [k]: e.target.value }))

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm animate-fade-up">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b border-gray-100 px-6 py-4 flex items-center justify-between rounded-t-2xl">
          <h2 className="font-semibold text-gray-900">Create Job Opening</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 transition-colors"><X size={18} /></button>
        </div>

        <div className="p-6 space-y-5">
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1.5">Job Title *</label>
            <input value={form.title} onChange={set('title')} className="input-base" placeholder="Senior Python Developer" />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1.5">Department</label>
              <input value={form.department} onChange={set('department')} className="input-base" placeholder="Engineering" />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1.5">Location</label>
              <input value={form.location} onChange={set('location')} className="input-base" placeholder="Remote (US)" />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1.5">Job Type</label>
              <select value={form.job_type} onChange={set('job_type')} className="input-base">
                <option value="full_time">Full Time</option>
                <option value="part_time">Part Time</option>
                <option value="contract">Contract</option>
                <option value="internship">Internship</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1.5">Level</label>
              <select value={form.experience_level} onChange={set('experience_level')} className="input-base">
                <option value="junior">Junior</option>
                <option value="mid">Mid-level</option>
                <option value="senior">Senior</option>
                <option value="lead">Lead</option>
                <option value="executive">Executive</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1.5">Min Salary ($)</label>
              <input type="number" value={form.salary_min} onChange={set('salary_min')} className="input-base" placeholder="80000" />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1.5">Max Salary ($)</label>
              <input type="number" value={form.salary_max} onChange={set('salary_max')} className="input-base" placeholder="130000" />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1.5">Min Years Exp</label>
              <input type="number" value={form.min_experience_yrs} onChange={set('min_experience_yrs')} className="input-base" placeholder="3" />
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1.5">Job Description *</label>
            <textarea
              value={form.description_raw} onChange={set('description_raw')}
              rows={5} className="input-base resize-none"
              placeholder="Describe the role, requirements, and responsibilities…"
            />
            <p className="text-xs text-gray-400 mt-1">Minimum 30 characters · AI will extract required skills automatically</p>
          </div>
        </div>

        <div className="sticky bottom-0 bg-white border-t border-gray-100 px-6 py-4 flex gap-3 rounded-b-2xl">
          <button onClick={onClose} className="btn-ghost flex-1">Cancel</button>
          <button
            onClick={() => mutation.mutate()}
            disabled={!form.title || !form.description_raw || form.description_raw.length < 30 || mutation.isPending}
            className="btn-primary flex-1"
          >
            {mutation.isPending ? <><Spinner size="sm" /> Creating…</> : 'Create Job'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default function JobsPage() {
  const navigate    = useNavigate()
  const [showModal, setShowModal] = useState(false)
  const [filter, setFilter]       = useState<string>('all')

  const { data, isLoading } = useQuery({
    queryKey: ['jobs'],
    queryFn: () => jobService.list().then((r) => r.data),
  })

  const jobs = filter === 'all' ? (data?.jobs ?? []) : (data?.jobs ?? []).filter(j => j.status === filter)

  const goScreen = (jobId: number) => {
    navigate('/workflow')
  }

  const FILTERS = ['all', 'active', 'paused', 'filled', 'closed']

  return (
    <div className="animate-fade-up">
      <PageHeader
        title="Job Openings"
        subtitle="Manage your recruitment pipeline positions."
        action={
          <button onClick={() => setShowModal(true)} className="btn-primary">
            <Plus size={15} /> New Job
          </button>
        }
      />

      {/* Filter tabs */}
      <div className="flex items-center gap-1 mb-5 p-1 bg-gray-100 rounded-xl w-fit">
        {FILTERS.map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all capitalize ${
              filter === f ? 'bg-white shadow-sm text-gray-900' : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            {f === 'all' ? `All (${data?.jobs.length ?? 0})` : f}
          </button>
        ))}
      </div>

      {isLoading ? (
        <div className="grid md:grid-cols-2 gap-4">
          {[...Array(4)].map((_, i) => <div key={i} className="skeleton h-44 rounded-xl" />)}
        </div>
      ) : jobs.length ? (
        <div className="grid md:grid-cols-2 gap-4">
          {jobs.map((job) => <JobCard key={job.id} job={job} onScreen={goScreen} />)}
        </div>
      ) : (
        <EmptyState
          icon={<Briefcase size={22} />}
          title="No jobs found"
          body={filter === 'all' ? 'Create your first job opening to start screening candidates.' : `No ${filter} jobs found.`}
          action={filter === 'all' ? <button onClick={() => setShowModal(true)} className="btn-primary"><Plus size={15} /> Create First Job</button> : undefined}
        />
      )}

      {showModal && <CreateJobModal onClose={() => setShowModal(false)} />}
    </div>
  )
}
