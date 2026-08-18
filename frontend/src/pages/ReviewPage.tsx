import React, { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import {
  CheckCircle2, XCircle, ChevronDown, ChevronUp,
  ThumbsUp, ThumbsDown, MessageSquare, ArrowRight,
} from 'lucide-react'
import { clsx } from 'clsx'
import { workflowService } from '@/services/hiring'
import useStore from '@/store/useStore'
import { PageHeader, ScoreBadge, ProgressBar, Badge, EmptyState, Spinner } from '@/components/ui'
import type { CandidateScore } from '@/types'

const REC_CONFIG: Record<string, { label: string; variant: React.ComponentProps<typeof Badge>['variant'] }> = {
  STRONGLY_RECOMMEND: { label: 'Highly Recommended', variant: 'green'  },
  RECOMMEND:          { label: 'Recommended',         variant: 'blue'   },
  MAYBE:              { label: 'Borderline',          variant: 'yellow' },
  REJECT:             { label: 'Not Recommended',     variant: 'red'    },
}

function CandidateCard({
  candidate, selected, onToggle,
}: { candidate: CandidateScore; selected: boolean; onToggle: () => void }) {
  const [expanded, setExpanded] = useState(false)
  const rec = REC_CONFIG[candidate.recommendation] ?? { label: candidate.recommendation, variant: 'gray' as const }

  return (
    <div className={clsx(
      'rounded-xl border-2 transition-all duration-200',
      selected ? 'border-blue-500 bg-blue-50/40 shadow-sm' : 'border-gray-200 bg-white hover:border-gray-300',
    )}>
      {/* Card header */}
      <div className="p-5">
        <div className="flex items-start gap-4">
          {/* Checkbox */}
          <button
            onClick={onToggle}
            className={clsx(
              'flex-shrink-0 mt-0.5 h-5 w-5 rounded border-2 flex items-center justify-center transition-all',
              selected ? 'bg-blue-600 border-blue-600' : 'border-gray-300 hover:border-blue-400',
            )}
          >
            {selected && <CheckCircle2 size={13} className="text-white" />}
          </button>

          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-3 flex-wrap">
              <div>
                <h3 className="font-semibold text-gray-900">{candidate.candidate_name}</h3>
                <p className="text-xs text-gray-500 mt-0.5">{candidate.candidate_email}</p>
              </div>
              <div className="flex items-center gap-2 flex-shrink-0">
                <ScoreBadge score={candidate.score} />
                <Badge variant={rec.variant as any}>{rec.label}</Badge>
              </div>
            </div>

            <ProgressBar value={candidate.score} className="mt-3" />

            <p className="text-sm text-gray-600 mt-3 leading-relaxed">{candidate.reasoning}</p>

            <div className="flex items-center gap-4 mt-3 text-xs text-gray-400">
              <span>Skill match: <span className="font-semibold text-gray-700">{candidate.skill_match_percentage}%</span></span>
              <span>Experience: <span className={clsx('font-semibold', {
                'text-emerald-600': candidate.experience_match === 'exceeds',
                'text-blue-600':    candidate.experience_match === 'meets',
                'text-amber-600':   candidate.experience_match === 'below',
              })}>{candidate.experience_match}</span></span>
            </div>
          </div>
        </div>
      </div>

      {/* Expand button */}
      <button
        onClick={() => setExpanded(v => !v)}
        className="w-full flex items-center justify-center gap-1.5 py-2 text-xs font-medium text-gray-400 hover:text-gray-600 border-t border-gray-100 hover:bg-gray-50 transition-colors rounded-b-xl"
      >
        {expanded ? <><ChevronUp size={13} /> Hide details</> : <><ChevronDown size={13} /> Show strengths & gaps</>}
      </button>

      {/* Expanded detail */}
      {expanded && (
        <div className="px-5 pb-5 grid grid-cols-2 gap-4 border-t border-gray-100 pt-4">
          <div>
            <p className="text-xs font-semibold text-emerald-700 mb-2 flex items-center gap-1.5">
              <ThumbsUp size={12} /> Strengths
            </p>
            <ul className="space-y-1">
              {candidate.strengths.map((s, i) => (
                <li key={i} className="text-xs text-gray-600 flex items-start gap-1.5">
                  <span className="text-emerald-500 mt-0.5 flex-shrink-0">âœ“</span> {s}
                </li>
              ))}
            </ul>
          </div>
          <div>
            <p className="text-xs font-semibold text-amber-700 mb-2 flex items-center gap-1.5">
              <ThumbsDown size={12} /> Gaps
            </p>
            {candidate.gaps.length ? (
              <ul className="space-y-1">
                {candidate.gaps.map((g, i) => (
                  <li key={i} className="text-xs text-gray-600 flex items-start gap-1.5">
                    <span className="text-amber-500 mt-0.5 flex-shrink-0">!</span> {g}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-xs text-gray-400 italic">No significant gaps</p>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default function ReviewPage() {
  const navigate          = useNavigate()
  const shortlisted       = useStore((s) => s.pendingShortlist)
  const activeThreadId    = useStore((s) => s.activeThreadId)
  const clearWorkflow     = useStore((s) => s.clearWorkflow)
  const setWorkflowOutput = useStore((s) => s.setWorkflowOutput)

  const [approvedSet, setApprovedSet] = useState<Set<string>>(
    () => new Set(shortlisted.filter((c) => c.score >= 75).map((c) => c.candidate_name))
  )
  const [feedback, setFeedback] = useState('')

  const toggle = (name: string) => setApprovedSet((prev) => {
    const next = new Set(prev); next.has(name) ? next.delete(name) : next.add(name); return next
  })

  const approveMutation = useMutation({
    mutationFn: (decision: 'approve' | 'reject_all') => {
      const approved = decision === 'reject_all'
        ? [] : shortlisted.filter((c) => approvedSet.has(c.candidate_name))
      return workflowService.approve(activeThreadId!, approved, decision, feedback)
    },
    onSuccess: (res, decision) => {
      setWorkflowOutput(res.data.interviews, res.data.report)
      clearWorkflow()
      if (decision === 'reject_all') {
        toast('Workflow closed.', { icon: 'âŒ' })
        navigate('/dashboard')
      } else {
        toast.success('Interviews scheduled!')
        navigate('/interviews')
      }
    },
    onError: (err: any) => toast.error(err.response?.data?.detail ?? 'Action failed'),
  })

  if (!shortlisted.length) {
    return (
      <EmptyState
        icon={<CheckCircle2 size={24} />}
        title="No candidates to review"
        body="Run a screening workflow first to see AI-shortlisted candidates here."
        action={<button onClick={() => navigate('/workflow')} className="btn-primary">Go to Screening <ArrowRight size={15} /></button>}
      />
    )
  }

  return (
    <div className="max-w-3xl mx-auto animate-fade-up space-y-5">
      <PageHeader
        title="Review Shortlist"
        subtitle={`AI identified ${shortlisted.length} candidate${shortlisted.length > 1 ? 's' : ''}. Select who to advance to interviews.`}
      />

      {/* Quick stats */}
      <div className="grid grid-cols-3 gap-3">
        <div className="card p-4 text-center">
          <p className="text-2xl font-bold text-gray-900">{shortlisted.length}</p>
          <p className="text-xs text-gray-500 mt-0.5">Shortlisted</p>
        </div>
        <div className="card p-4 text-center">
          <p className="text-2xl font-bold text-blue-600">{approvedSet.size}</p>
          <p className="text-xs text-gray-500 mt-0.5">Selected</p>
        </div>
        <div className="card p-4 text-center">
          <p className="text-2xl font-bold text-gray-900">
            {shortlisted.length ? Math.round(shortlisted.reduce((s, c) => s + c.score, 0) / shortlisted.length) : 0}
          </p>
          <p className="text-xs text-gray-500 mt-0.5">Avg Score</p>
        </div>
      </div>

      {/* Candidate cards */}
      <div className="space-y-3">
        {shortlisted.map((c) => (
          <CandidateCard
            key={c.candidate_name}
            candidate={c}
            selected={approvedSet.has(c.candidate_name)}
            onToggle={() => toggle(c.candidate_name)}
          />
        ))}
      </div>

      {/* Feedback */}
      <div className="card p-5">
        <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2.5">
          <MessageSquare size={15} /> Recruiter notes (optional)
        </label>
        <textarea
          value={feedback}
          onChange={(e) => setFeedback(e.target.value)}
          rows={2}
          className="input-base resize-none"
          placeholder="e.g. Top 2 candidates look great, skip C3 â€” too junior."
        />
      </div>

      {/* Actions */}
      <div className="flex gap-3 pb-4">
        <button
          onClick={() => approveMutation.mutate('approve')}
          disabled={approvedSet.size === 0 || approveMutation.isPending}
          className="btn-primary flex-1 py-3"
        >
          {approveMutation.isPending
            ? <><Spinner size="sm" /> Schedulingâ€¦</>
            : <><CheckCircle2 size={15} /> Approve {approvedSet.size} & Schedule Interviews</>}
        </button>
        <button
          onClick={() => approveMutation.mutate('reject_all')}
          disabled={approveMutation.isPending}
          className="btn-danger px-6 py-3"
        >
          <XCircle size={15} /> Reject All
        </button>
      </div>
    </div>
  )
}

// â”€â”€ Score badge â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€