/** Reusable primitive components — Badge, Avatar, Stat, Spinner, Empty */
import React from 'react'
import { clsx } from 'clsx'

// ── Badge ─────────────────────────────────────────────────────────────────
const BADGE_VARIANTS = {
  green:   'bg-emerald-50 text-emerald-700 ring-1 ring-emerald-200',
  yellow:  'bg-amber-50   text-amber-700   ring-1 ring-amber-200',
  red:     'bg-red-50     text-red-700     ring-1 ring-red-200',
  blue:    'bg-blue-50    text-blue-700    ring-1 ring-blue-200',
  gray:    'bg-gray-100   text-gray-600    ring-1 ring-gray-200',
  indigo:  'bg-indigo-50  text-indigo-700  ring-1 ring-indigo-200',
}

export function Badge({
  children, variant = 'gray', className,
}: { children: React.ReactNode; variant?: keyof typeof BADGE_VARIANTS; className?: string }) {
  return (
    <span className={clsx('inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium', BADGE_VARIANTS[variant], className)}>
      {children}
    </span>
  )
}

// ── Score badge (0–100) ───────────────────────────────────────────────────
export function ScoreBadge({ score }: { score: number }) {
  const variant = score >= 80 ? 'green' : score >= 65 ? 'yellow' : 'red'
  return <Badge variant={variant}>{score}/100</Badge>
}

// ── Avatar ────────────────────────────────────────────────────────────────
export function Avatar({ name, size = 'md' }: { name: string; size?: 'sm' | 'md' | 'lg' }) {
  const initials = name.split(' ').map(w => w[0]).slice(0, 2).join('').toUpperCase()
  const colors = ['bg-blue-500','bg-violet-500','bg-emerald-500','bg-amber-500','bg-pink-500']
  const color  = colors[name.charCodeAt(0) % colors.length]
  const sz     = { sm: 'h-7 w-7 text-xs', md: 'h-9 w-9 text-sm', lg: 'h-11 w-11 text-base' }[size]
  return (
    <div className={clsx('flex items-center justify-center rounded-full font-semibold text-white flex-shrink-0', color, sz)}>
      {initials}
    </div>
  )
}

// ── Spinner ───────────────────────────────────────────────────────────────
export function Spinner({ size = 'md', className }: { size?: 'sm' | 'md' | 'lg'; className?: string }) {
  const sz = { sm: 'h-4 w-4 border-2', md: 'h-5 w-5 border-2', lg: 'h-8 w-8 border-2' }[size]
  return (
    <div className={clsx('animate-spin rounded-full border-t-transparent border-blue-600', sz, className)} />
  )
}

// ── Progress bar ──────────────────────────────────────────────────────────
export function ProgressBar({ value, className }: { value: number; className?: string }) {
  const color = value >= 80 ? 'bg-emerald-500' : value >= 65 ? 'bg-amber-500' : 'bg-red-500'
  return (
    <div className={clsx('h-1.5 w-full bg-gray-100 rounded-full overflow-hidden', className)}>
      <div className={clsx('h-full rounded-full animate-grow transition-all', color)} style={{ width: `${value}%` }} />
    </div>
  )
}

// ── Stat card ─────────────────────────────────────────────────────────────
export function StatCard({
  label, value, icon, trend, color = 'blue',
}: {
  label: string; value: number | string; icon: React.ReactNode
  trend?: { value: number; label: string }; color?: 'blue' | 'green' | 'amber' | 'violet'
}) {
  const bg = {
    blue:   'bg-blue-50   text-blue-600',
    green:  'bg-emerald-50 text-emerald-600',
    amber:  'bg-amber-50  text-amber-600',
    violet: 'bg-violet-50 text-violet-600',
  }[color]

  return (
    <div className="card p-5 flex items-start gap-4 animate-fade-up">
      <div className={clsx('flex items-center justify-center h-10 w-10 rounded-lg flex-shrink-0', bg)}>
        {icon}
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-2xl font-bold text-gray-900 leading-none">{value}</p>
        <p className="text-sm text-gray-500 mt-1">{label}</p>
        {trend && (
          <p className={clsx('text-xs mt-1 font-medium', trend.value >= 0 ? 'text-emerald-600' : 'text-red-500')}>
            {trend.value >= 0 ? '↑' : '↓'} {Math.abs(trend.value)}% {trend.label}
          </p>
        )}
      </div>
    </div>
  )
}

// ── Empty state ───────────────────────────────────────────────────────────
export function EmptyState({ icon, title, body, action }: {
  icon: React.ReactNode; title: string; body: string; action?: React.ReactNode
}) {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-center animate-fade-up">
      <div className="flex items-center justify-center h-14 w-14 rounded-2xl bg-gray-100 text-gray-400 mb-4">
        {icon}
      </div>
      <h3 className="text-base font-semibold text-gray-900">{title}</h3>
      <p className="text-sm text-gray-500 mt-1 max-w-xs">{body}</p>
      {action && <div className="mt-5">{action}</div>}
    </div>
  )
}

// ── Section header ────────────────────────────────────────────────────────
export function PageHeader({ title, subtitle, action }: {
  title: string; subtitle?: string; action?: React.ReactNode
}) {
  return (
    <div className="flex items-start justify-between mb-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 tracking-tight">{title}</h1>
        {subtitle && <p className="text-sm text-gray-500 mt-0.5">{subtitle}</p>}
      </div>
      {action && <div className="ml-4 flex-shrink-0">{action}</div>}
    </div>
  )
}

// ── Step indicator ────────────────────────────────────────────────────────
export function StepIndicator({ steps, current }: {
  steps: string[]; current: number
}) {
  return (
    <div className="flex items-center gap-0 mb-8">
      {steps.map((step, i) => (
        <React.Fragment key={i}>
          <div className="flex flex-col items-center">
            <div className={clsx(
              'flex items-center justify-center h-8 w-8 rounded-full text-xs font-bold border-2 transition-colors',
              i < current  ? 'bg-blue-600 border-blue-600 text-white'
              : i === current ? 'bg-white border-blue-600 text-blue-600'
              :                 'bg-white border-gray-200 text-gray-400'
            )}>
              {i < current ? '✓' : i + 1}
            </div>
            <span className={clsx('text-xs mt-1 font-medium whitespace-nowrap',
              i <= current ? 'text-blue-600' : 'text-gray-400'
            )}>{step}</span>
          </div>
          {i < steps.length - 1 && (
            <div className={clsx('flex-1 h-0.5 mb-4 mx-2', i < current ? 'bg-blue-600' : 'bg-gray-200')} />
          )}
        </React.Fragment>
      ))}
    </div>
  )
}
