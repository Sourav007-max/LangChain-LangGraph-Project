import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import toast from 'react-hot-toast'
import { Eye, EyeOff, Bot, Zap, Users, BarChart3, CheckCircle2 } from 'lucide-react'
import { authService } from '@/services/hiring'
import useStore from '@/store/useStore'
import { Spinner } from '@/components/ui'

const schema = z.object({
  email:    z.string().email('Enter a valid email'),
  password: z.string().min(8, 'Minimum 8 characters'),
})
type FormData = z.infer<typeof schema>

const FEATURES = [
  { Icon: Zap,        text: 'AI scores 100 resumes in under 2 minutes' },
  { Icon: Users,      text: 'Multi-agent pipeline with human approval' },
  { Icon: BarChart3,  text: 'Real-time hiring analytics dashboard' },
  { Icon: CheckCircle2, text: 'Auto-schedules interviews via email' },
]

export default function LoginPage() {
  const navigate  = useNavigate()
  const setAuth   = useStore((s) => s.setAuth)
  const [loading, setLoading]       = useState(false)
  const [showPassword, setShowPassword] = useState(false)

  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { email: 'recruiter@hiringapp.com', password: 'Admin@123' },
  })

  const onSubmit = async (data: FormData) => {
    setLoading(true)
    try {
      const res = await authService.login(data.email, data.password)
      const { access_token, full_name, role, user_id } = res.data
      localStorage.setItem('access_token', access_token)
      setAuth(access_token, { id: user_id, email: data.email, full_name, role: role as any })
      toast.success(`Welcome back, ${full_name}!`)
      navigate('/dashboard')
    } catch (err: any) {
      toast.error(err.response?.data?.detail ?? 'Invalid credentials')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex">

      {/* â”€â”€ Left panel â€” branding â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */}
      <div className="hidden lg:flex lg:w-5/12 xl:w-1/2 flex-col justify-between p-10 bg-[hsl(222,47%,11%)] text-white">
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center h-9 w-9 rounded-xl bg-blue-600">
            <Bot size={20} className="text-white" />
          </div>
          <div>
            <p className="font-bold text-lg leading-tight">AI Hiring Co-Pilot</p>
            <p className="text-xs text-blue-300">Multi-Agent Recruitment Platform</p>
          </div>
        </div>

        <div>
          <h2 className="text-3xl xl:text-4xl font-bold leading-tight">
            Hire smarter.<br />
            <span className="text-blue-400">Not harder.</span>
          </h2>
          <p className="mt-4 text-white/60 text-sm leading-relaxed max-w-sm">
            AI agents screen, score, and shortlist candidates automatically â€” leaving you more time for
            what matters: choosing the right person.
          </p>

          <ul className="mt-8 space-y-3">
            {FEATURES.map(({ Icon, text }) => (
              <li key={text} className="flex items-center gap-3 text-sm text-white/70">
                <div className="h-6 w-6 rounded-md bg-blue-600/30 flex items-center justify-center flex-shrink-0">
                  <Icon size={13} className="text-blue-400" />
                </div>
                {text}
              </li>
            ))}
          </ul>
        </div>

        <p className="text-xs text-white/25">Â© 2026 AI Hiring Co-Pilot Â· Powered by LangGraph + Gemini</p>
      </div>

      {/* â”€â”€ Right panel â€” form â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */}
      <div className="flex-1 flex items-center justify-center px-6 py-12 bg-[hsl(var(--background))]">
        <div className="w-full max-w-[400px] animate-fade-up">

          {/* Mobile logo */}
          <div className="flex items-center gap-2.5 mb-8 lg:hidden">
            <div className="h-8 w-8 rounded-lg bg-blue-600 flex items-center justify-center">
              <Bot size={17} className="text-white" />
            </div>
            <p className="font-bold text-gray-900">AI Hiring Co-Pilot</p>
          </div>

          <div className="mb-8">
            <h1 className="text-2xl font-bold text-gray-900">Sign in to your account</h1>
            <p className="text-sm text-gray-500 mt-1">Enter your credentials below to continue</p>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            {/* Email */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Email address</label>
              <input
                {...register('email')}
                type="email"
                autoComplete="email"
                className="input-base"
                placeholder="you@company.com"
              />
              {errors.email && (
                <p className="text-red-500 text-xs mt-1.5 flex items-center gap-1">
                  <span>âš </span> {errors.email.message}
                </p>
              )}
            </div>

            {/* Password */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Password</label>
              <div className="relative">
                <input
                  {...register('password')}
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="current-password"
                  className="input-base pr-10"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(v => !v)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
              {errors.password && (
                <p className="text-red-500 text-xs mt-1.5 flex items-center gap-1">
                  <span>âš </span> {errors.password.message}
                </p>
              )}
            </div>

            <button type="submit" disabled={loading} className="btn-primary w-full py-3">
              {loading ? <><Spinner size="sm" /> Signing inâ€¦</> : 'Sign in'}
            </button>
          </form>

          <div className="mt-8 p-4 rounded-xl bg-blue-50 border border-blue-100">
            <p className="text-xs font-semibold text-blue-700 mb-2">Demo credentials</p>
            <div className="grid grid-cols-2 gap-2 text-xs text-blue-600">
              <div><span className="text-blue-400">Email:</span> recruiter@hiringapp.com</div>
              <div><span className="text-blue-400">Pass:</span> Admin@123</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
