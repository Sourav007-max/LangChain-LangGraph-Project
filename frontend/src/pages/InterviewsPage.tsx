import React, { useState } from 'react'
import useStore from '@/store/useStore'
import { useNavigate } from 'react-router-dom'
import {
  Calendar, Clock, Video, Mail, ChevronDown, ChevronUp,
  Download, HelpCircle, ArrowRight,
} from 'lucide-react'
import { clsx } from 'clsx'
import { PageHeader, Badge, EmptyState } from '@/components/ui'

export default function InterviewsPage() {
  const interviews = useStore((s) => s.lastInterviews)
  const report     = useStore((s) => s.lastReport)
  const navigate   = useNavigate()
  const [expandedReport, setExpandedReport] = useState(false)
  const [openIdx, setOpenIdx]               = useState<number | null>(null)

  if (!interviews.length) {
    return (
      <EmptyState
        icon={<Calendar size={24} />}
        title="No interviews scheduled yet"
        body="Complete a screening workflow and approve candidates to see scheduled interviews here."
        action={<button onClick={() => navigate('/workflow')} className="btn-primary">Start Screening <ArrowRight size={15} /></button>}
      />
    )
  }

  return (
    <div className="space-y-6 animate-fade-up">
      <div className="flex items-start justify-between">
        <PageHeader
          title="Interview Schedule"
          subtitle={`${interviews.length} interview${interviews.length !== 1 ? 's' : ''} scheduled`}
        />
        {report && (
          <button onClick={() => setExpandedReport(v => !v)} className="btn-ghost text-xs">
            {expandedReport ? 'Hide' : 'View'} AI Report
          </button>
        )}
      </div>

      <div className="space-y-4">
        {interviews.map((interview, i) => {
          const isOpen = openIdx === i
          return (
            <div key={i} className="card overflow-hidden">
              <div className="p-5 flex items-center gap-4">
                <div className="flex-shrink-0 text-center bg-blue-600 text-white rounded-xl p-3 w-16">
                  <p className="text-xs font-medium opacity-80">
                    {new Date(interview.interview_date).toLocaleString('en', { month: 'short' })}
                  </p>
                  <p className="text-2xl font-bold leading-none">
                    {new Date(interview.interview_date).getDate()}
                  </p>
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-2 flex-wrap">
                    <div>
                      <p className="font-semibold text-gray-900">{interview.candidate_name}</p>
                      <p className="text-xs text-gray-500 mt-0.5">{interview.candidate_email}</p>
                    </div>
                    <Badge variant="blue">{interview.interview_type?.replace('_', ' ')}</Badge>
                  </div>
                  <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                    <span className="flex items-center gap-1"><Clock size={11} /> {interview.interview_time}</span>
                    {interview.meeting_link && (
                      <a href={interview.meeting_link} target="_blank" rel="noreferrer"
                        className="flex items-center gap-1 text-blue-600 hover:text-blue-800 font-medium">
                        <Video size={11} /> Join meeting
                      </a>
                    )}
                    <span className={clsx('flex items-center gap-1', interview.email_sent ? 'text-emerald-600' : 'text-gray-400')}>
                      <Mail size={11} />
                      {interview.email_sent ? 'Invite sent' : 'Email not sent'}
                    </span>
                  </div>
                </div>

                <button onClick={() => setOpenIdx(isOpen ? null : i)} className="btn-ghost px-3 py-2 text-xs flex items-center gap-1">
                  <HelpCircle size={14} />
                  {isOpen ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                </button>
              </div>

              {isOpen && interview.ai_questions?.length > 0 && (
                <div className="border-t border-gray-100 px-5 py-4 bg-gray-50">
                  <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">AI-Generated Questions</p>
                  <ol className="space-y-2">
                    {interview.ai_questions.map((q, j) => (
                      <li key={j} className="flex items-start gap-2.5 text-sm">
                        <span className="flex-shrink-0 h-5 w-5 rounded-full bg-blue-100 text-blue-700 text-xs font-bold flex items-center justify-center mt-0.5">{j + 1}</span>
                        <span className="text-gray-700">{q}</span>
                      </li>
                    ))}
                  </ol>
                </div>
              )}
            </div>
          )
        })}
      </div>

      {report && expandedReport && (
        <div className="card p-6">
          <div className="flex items-center justify-between mb-5">
            <h2 className="section-title">AI Hiring Report</h2>
            <a href={`data:text/markdown;charset=utf-8,${encodeURIComponent(report)}`} download="hiring_report.md"
              className="btn-ghost text-xs gap-1.5">
              <Download size={13} /> Download
            </a>
          </div>
          <div className="whitespace-pre-wrap text-sm text-gray-700 leading-relaxed bg-gray-50 rounded-xl p-5 border border-gray-100">
            {report}
          </div>
        </div>
      )}

      {interviews.some(i => !i.email_sent) && (
        <div className="flex items-start gap-3 p-4 rounded-xl bg-amber-50 border border-amber-200 text-sm">
          <Mail size={16} className="text-amber-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-medium text-amber-800">Email invitations not sent</p>
            <p className="text-amber-700 mt-0.5 text-xs">
              Set <code className="bg-amber-100 px-1 rounded">SMTP_ENABLED=true</code> in <code className="bg-amber-100 px-1 rounded">.env</code> to enable automatic invites.
            </p>
          </div>
        </div>
      )}
    </div>
  )
}
