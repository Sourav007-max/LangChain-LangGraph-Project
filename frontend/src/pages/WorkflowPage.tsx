import React, { useState, useCallback } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { useDropzone } from 'react-dropzone'
import toast from 'react-hot-toast'
import { useNavigate } from 'react-router-dom'
import {
  Upload, X, CheckCircle2, FileText, ChevronRight,
  Cpu, Brain, Filter, Users, Rocket,
} from 'lucide-react'
import { jobService, resumeService, workflowService } from '@/services/hiring'
import useStore from '@/store/useStore'
import { PageHeader, StepIndicator, Spinner, Badge } from '@/components/ui'

interface UploadedResume { resume_id: number; name: string; email: string; fileName: string }

const AGENTS = [
  { icon: <Brain size={15} />,  label: 'JD Analyzer',         desc: 'Extracts requirements from job description' },
  { icon: <FileText size={15} />, label: 'Resume Parser',       desc: 'Parses PDF and extracts candidate data' },
  { icon: <Cpu size={15} />,    label: 'Candidate Matcher',    desc: 'Scores each candidate against JD' },
  { icon: <Filter size={15} />, label: 'Shortlisting',         desc: 'Filters candidates above score threshold' },
  { icon: <Users size={15} />,  label: 'â¸ Human Review',       desc: 'You approve the AI shortlist' },
]

export default function WorkflowPage() {
  const navigate          = useNavigate()
  const setWorkflowResult = useStore((s) => s.setWorkflowResult)

  const [step, setStep]               = useState(0)   // 0=job, 1=upload, 2=run
  const [selectedJobId, setSelectedJobId] = useState<number | null>(null)
  const [selectedJobTitle, setSelectedJobTitle] = useState('')
  const [candName, setCandName]       = useState('')
  const [candEmail, setCandEmail]     = useState('')
  const [uploaded, setUploaded]       = useState<UploadedResume[]>([])

  const { data: jobsData } = useQuery({
    queryKey: ['jobs', 'active'],
    queryFn: () => jobService.list('active').then((r) => r.data),
  })

  const uploadMutation = useMutation({
    mutationFn: (file: File) => resumeService.upload(file, candEmail, candName),
    onSuccess: (res, file) => {
      setUploaded((prev) => [...prev, {
        resume_id: res.data.resume_id, name: candName,
        email: candEmail, fileName: file.name,
      }])
      toast.success(`${file.name} uploaded`)
      setCandName(''); setCandEmail('')
    },
    onError: (err: any) => toast.error(err.response?.data?.detail ?? 'Upload failed'),
  })

  const onDrop = useCallback((files: File[]) => {
    if (!candName.trim() || !candEmail.trim()) {
      toast.error('Enter candidate name and email first')
      return
    }
    files.forEach((f) => uploadMutation.mutate(f))
  }, [candName, candEmail])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'], 'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'] },
    multiple: false,
    maxSize: 10 * 1024 * 1024,
  })

  const workflowMutation = useMutation({
    mutationFn: () => workflowService.start(selectedJobId!, uploaded.map((r) => r.resume_id)),
    onSuccess: (res) => {
      const { thread_id, shortlisted, total_scored } = res.data
      toast.success(`${total_scored} candidate${total_scored !== 1 ? 's' : ''} scored`)
      if (shortlisted?.length) {
        setWorkflowResult(thread_id, shortlisted)
        navigate('/review')
      } else {
        toast('No candidates met the score threshold.', { icon: 'âš ï¸' })
      }
    },
    onError: (err: any) => toast.error(err.response?.data?.detail ?? 'Workflow failed'),
  })

  const canAdvanceStep0 = !!selectedJobId
  const canAdvanceStep1 = uploaded.length > 0

  return (
    <div className="max-w-2xl mx-auto animate-fade-up space-y-6">
      <PageHeader
        title="Run AI Screening"
        subtitle="Upload resumes and let the AI pipeline evaluate every candidate."
      />

      <StepIndicator steps={['Select Job', 'Upload Resumes', 'Launch Pipeline']} current={step} />

      {/* â”€â”€ Step 0: Select job â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */}
      {step === 0 && (
        <div className="card p-6 space-y-4">
          <div className="flex items-center gap-2 mb-1">
            <div className="h-6 w-6 rounded-md bg-blue-600 flex items-center justify-center text-white text-xs font-bold">1</div>
            <h2 className="font-semibold text-gray-900">Choose a Job Opening</h2>
          </div>
          <p className="text-sm text-gray-500">Select the role you are screening candidates for.</p>

          {jobsData?.jobs.length === 0 && (
            <div className="text-sm text-amber-700 bg-amber-50 border border-amber-200 rounded-lg p-3">
              No active jobs found. <button onClick={() => navigate('/jobs')} className="underline font-medium">Create one first</button>.
            </div>
          )}

          <div className="grid gap-2">
            {jobsData?.jobs.map((job) => (
              <button
                key={job.id}
                onClick={() => { setSelectedJobId(job.id); setSelectedJobTitle(job.title) }}
                className={`flex items-center gap-3 p-4 rounded-xl border-2 text-left transition-all ${
                  selectedJobId === job.id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300 bg-white'
                }`}
              >
                <div className={`h-9 w-9 rounded-lg flex items-center justify-center flex-shrink-0 ${
                  selectedJobId === job.id ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-500'
                }`}>
                  <Rocket size={16} />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-gray-900 text-sm">{job.title}</p>
                  <p className="text-xs text-gray-500">{job.location ?? 'Remote'} Â· {job.job_type?.replace('_', ' ')}</p>
                </div>
                {selectedJobId === job.id && <CheckCircle2 size={18} className="text-blue-600 flex-shrink-0" />}
              </button>
            ))}
          </div>

          <button
            onClick={() => setStep(1)}
            disabled={!canAdvanceStep0}
            className="btn-primary w-full"
          >
            Continue <ChevronRight size={16} />
          </button>
        </div>
      )}

      {/* â”€â”€ Step 1: Upload resumes â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */}
      {step === 1 && (
        <div className="card p-6 space-y-5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="h-6 w-6 rounded-md bg-blue-600 flex items-center justify-center text-white text-xs font-bold">2</div>
              <h2 className="font-semibold text-gray-900">Upload Resumes</h2>
            </div>
            <Badge variant="blue">{selectedJobTitle}</Badge>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1.5">Candidate Full Name</label>
              <input value={candName} onChange={(e) => setCandName(e.target.value)}
                className="input-base" placeholder="Jane Smith" />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1.5">Candidate Email</label>
              <input value={candEmail} onChange={(e) => setCandEmail(e.target.value)}
                type="email" className="input-base" placeholder="jane@example.com" />
            </div>
          </div>

          <div {...getRootProps()} className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all ${
            isDragActive ? 'border-blue-500 bg-blue-50 scale-[1.01]' : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
          }`}>
            <input {...getInputProps()} />
            <div className="h-12 w-12 rounded-xl bg-blue-50 flex items-center justify-center mx-auto mb-3">
              <Upload size={22} className="text-blue-500" />
            </div>
            <p className="text-sm font-medium text-gray-700">
              {isDragActive ? 'Drop the file hereâ€¦' : 'Drag & drop PDF or DOCX'}
            </p>
            <p className="text-xs text-gray-400 mt-1">or <span className="text-blue-600 underline">browse files</span> Â· max 10 MB</p>
            {uploadMutation.isPending && <div className="flex justify-center mt-3"><Spinner /></div>}
          </div>

          {uploaded.length > 0 && (
            <div className="space-y-2">
              <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Queued ({uploaded.length})</p>
              {uploaded.map((r) => (
                <div key={r.resume_id} className="flex items-center gap-3 p-3 rounded-lg bg-emerald-50 border border-emerald-100">
                  <CheckCircle2 size={16} className="text-emerald-600 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">{r.name}</p>
                    <p className="text-xs text-gray-500 truncate">{r.fileName}</p>
                  </div>
                  <button onClick={() => setUploaded(prev => prev.filter(x => x.resume_id !== r.resume_id))}
                    className="text-gray-400 hover:text-red-500 transition-colors">
                    <X size={14} />
                  </button>
                </div>
              ))}
            </div>
          )}

          <div className="flex gap-3">
            <button onClick={() => setStep(0)} className="btn-ghost flex-1">Back</button>
            <button onClick={() => setStep(2)} disabled={!canAdvanceStep1} className="btn-primary flex-1">
              Continue <ChevronRight size={16} />
            </button>
          </div>
        </div>
      )}

      {/* â”€â”€ Step 2: Launch â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */}
      {step === 2 && (
        <div className="card p-6 space-y-5">
          <div className="flex items-center gap-2">
            <div className="h-6 w-6 rounded-md bg-blue-600 flex items-center justify-center text-white text-xs font-bold">3</div>
            <h2 className="font-semibold text-gray-900">Launch AI Pipeline</h2>
          </div>

          {/* Summary */}
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-gray-50 rounded-lg p-3">
              <p className="text-xs text-gray-500">Job</p>
              <p className="text-sm font-semibold text-gray-900 mt-0.5 truncate">{selectedJobTitle}</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-3">
              <p className="text-xs text-gray-500">Resumes queued</p>
              <p className="text-sm font-semibold text-gray-900 mt-0.5">{uploaded.length} candidate{uploaded.length !== 1 ? 's' : ''}</p>
            </div>
          </div>

          {/* Agent pipeline preview */}
          <div className="space-y-2">
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Agents that will run</p>
            {AGENTS.map((a, i) => (
              <div key={i} className="flex items-center gap-3 p-3 rounded-lg border border-gray-100 bg-white">
                <div className="h-7 w-7 rounded-md bg-blue-50 text-blue-600 flex items-center justify-center flex-shrink-0">{a.icon}</div>
                <div>
                  <p className="text-sm font-medium text-gray-900">{a.label}</p>
                  <p className="text-xs text-gray-400">{a.desc}</p>
                </div>
              </div>
            ))}
          </div>

          <div className="flex gap-3">
            <button onClick={() => setStep(1)} className="btn-ghost flex-1">Back</button>
            <button
              onClick={() => workflowMutation.mutate()}
              disabled={workflowMutation.isPending}
              className="btn-primary flex-1 py-3"
            >
              {workflowMutation.isPending
                ? <><Spinner size="sm" /> Agents workingâ€¦</>
                : <><Rocket size={15} /> Start AI Screening</>}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
