import React, { useState } from 'react'
import { NavLink, useNavigate, useLocation } from 'react-router-dom'
import useStore from '@/store/useStore'
import { clsx } from 'clsx'
import {
  LayoutDashboard, Briefcase, Rocket, CheckSquare,
  Calendar, LogOut, Bot, Bell, ChevronRight, Menu, X,
} from 'lucide-react'
import { Avatar } from '@/components/ui'

const NAV = [
  { to: '/dashboard',  label: 'Dashboard',     Icon: LayoutDashboard, desc: 'Overview & metrics' },
  { to: '/jobs',       label: 'Jobs',           Icon: Briefcase,       desc: 'Manage job openings' },
  { to: '/workflow',   label: 'Run Screening',  Icon: Rocket,          desc: 'Upload & analyse resumes' },
  { to: '/review',     label: 'Review',         Icon: CheckSquare,     desc: 'Approve shortlisted candidates' },
  { to: '/interviews', label: 'Interviews',     Icon: Calendar,        desc: 'Scheduled sessions' },
]

const BREADCRUMB: Record<string, string> = {
  '/dashboard':  'Dashboard',
  '/jobs':       'Jobs',
  '/workflow':   'Run Screening',
  '/review':     'Review Shortlist',
  '/interviews': 'Interview Schedule',
}

export default function Layout({ children }: { children: React.ReactNode }) {
  const navigate         = useNavigate()
  const location         = useLocation()
  const user             = useStore((s) => s.user)
  const logout           = useStore((s) => s.logout)
  const pendingShortlist = useStore((s) => s.pendingShortlist)
  const [collapsed, setCollapsed] = useState(false)

  const handleLogout = () => {
    logout()
    localStorage.removeItem('access_token')
    navigate('/login')
  }

  const crumb = BREADCRUMB[location.pathname] ?? ''

  return (
    <div className="flex h-screen overflow-hidden bg-[hsl(var(--background))]">

      {/* ── Sidebar ───────────────────────────────────────────────────── */}
      <aside className={clsx(
        'flex flex-col h-full transition-all duration-300 flex-shrink-0',
        'bg-[hsl(222,47%,11%)] text-[hsl(210,40%,96%)]',
        collapsed ? 'w-16' : 'w-60',
      )}>

        {/* Logo */}
        <div className="flex items-center justify-between px-4 h-16 border-b border-white/10 flex-shrink-0">
          {!collapsed && (
            <div className="flex items-center gap-2.5">
              <div className="flex items-center justify-center h-8 w-8 rounded-lg bg-blue-600 flex-shrink-0">
                <Bot size={17} className="text-white" />
              </div>
              <div className="leading-tight">
                <p className="text-sm font-semibold text-white">Hiring Co-Pilot</p>
                <p className="text-[10px] text-blue-300">AI Recruitment</p>
              </div>
            </div>
          )}
          {collapsed && (
            <div className="flex items-center justify-center w-full">
              <div className="h-8 w-8 rounded-lg bg-blue-600 flex items-center justify-center">
                <Bot size={17} className="text-white" />
              </div>
            </div>
          )}
          {!collapsed && (
            <button onClick={() => setCollapsed(true)} className="text-white/40 hover:text-white transition-colors p-1 rounded">
              <Menu size={16} />
            </button>
          )}
        </div>

        {/* Nav items */}
        <nav className="flex-1 overflow-y-auto py-4 space-y-0.5 px-2">
          {NAV.map(({ to, label, Icon }) => (
            <NavLink
              key={to}
              to={to}
              title={collapsed ? label : undefined}
              className={({ isActive }) => clsx(
                'flex items-center gap-3 rounded-lg px-2.5 py-2 text-sm font-medium transition-all duration-150 group relative',
                isActive
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'text-white/60 hover:text-white hover:bg-white/8',
                collapsed && 'justify-center px-0',
              )}
            >
              <Icon size={17} className="flex-shrink-0" />
              {!collapsed && <span>{label}</span>}
              {!collapsed && to === '/review' && pendingShortlist.length > 0 && (
                <span className="ml-auto bg-red-500 text-white text-[10px] font-bold rounded-full h-4.5 w-4.5 flex items-center justify-center min-w-[18px] px-1">
                  {pendingShortlist.length}
                </span>
              )}
              {collapsed && to === '/review' && pendingShortlist.length > 0 && (
                <span className="absolute top-0.5 right-0.5 h-2.5 w-2.5 bg-red-500 rounded-full border border-[hsl(222,47%,11%)]" />
              )}
            </NavLink>
          ))}
        </nav>

        {/* User profile */}
        <div className="border-t border-white/10 p-3 flex-shrink-0">
          {collapsed ? (
            <button onClick={handleLogout} title="Logout" className="w-full flex justify-center p-2 text-white/40 hover:text-red-400 transition-colors rounded-lg hover:bg-white/8">
              <LogOut size={16} />
            </button>
          ) : (
            <div className="flex items-center gap-2.5">
              <Avatar name={user?.full_name ?? 'User'} size="sm" />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-white truncate">{user?.full_name}</p>
                <p className="text-[10px] text-white/40 capitalize truncate">{user?.role?.replace('_', ' ')}</p>
              </div>
              <button onClick={handleLogout} title="Logout" className="text-white/30 hover:text-red-400 transition-colors p-1 rounded">
                <LogOut size={14} />
              </button>
            </div>
          )}
        </div>
      </aside>

      {/* ── Main area ─────────────────────────────────────────────────── */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">

        {/* Top bar */}
        <header className="h-14 bg-white border-b border-gray-200 flex items-center justify-between px-6 flex-shrink-0">
          <div className="flex items-center gap-2 text-sm text-gray-500">
            {collapsed && (
              <button onClick={() => setCollapsed(false)} className="mr-2 text-gray-400 hover:text-gray-700 transition-colors">
                <ChevronRight size={16} />
              </button>
            )}
            <span className="font-semibold text-gray-900">{crumb}</span>
          </div>

          <div className="flex items-center gap-3">
            {pendingShortlist.length > 0 && (
              <button
                onClick={() => navigate('/review')}
                className="relative flex items-center gap-2 text-xs font-medium text-amber-700 bg-amber-50 border border-amber-200 px-3 py-1.5 rounded-full hover:bg-amber-100 transition-colors"
              >
                <Bell size={13} />
                {pendingShortlist.length} candidate{pendingShortlist.length > 1 ? 's' : ''} awaiting review
              </button>
            )}
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <Avatar name={user?.full_name ?? 'U'} size="sm" />
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto p-6 lg:p-8">
          {children}
        </main>
      </div>
    </div>
  )
}
