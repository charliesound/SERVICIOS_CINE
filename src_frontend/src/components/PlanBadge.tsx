import clsx from 'clsx'
import { PlanInfo } from '@/types'

interface PlanBadgeProps {
  plan: string
  size?: 'sm' | 'md' | 'lg'
}

const planConfig: Record<string, { label: string; bg: string; text: string; border: string }> = {
  free: { label: 'Free', bg: 'bg-slate-500/10', text: 'text-slate-300', border: 'border-slate-500/20' },
  creator: { label: 'Creator', bg: 'bg-amber-500/10', text: 'text-amber-400', border: 'border-amber-500/20' },
  studio: { label: 'Studio', bg: 'bg-purple-500/10', text: 'text-purple-400', border: 'border-purple-500/20' },
  enterprise: { label: 'Enterprise', bg: 'bg-amber-500/20', text: 'text-amber-300', border: 'border-amber-400/30' },
}

const sizeConfig = {
  sm: 'text-xs px-2 py-0.5',
  md: 'text-xs px-2.5 py-1',
  lg: 'text-sm px-3 py-1.5',
}

export function PlanBadge({ plan, size = 'md' }: PlanBadgeProps) {
  const config = planConfig[plan] || planConfig.free

  return (
    <span className={clsx(
      'inline-flex items-center rounded-full font-medium border',
      config.bg, config.text, config.border,
      sizeConfig[size]
    )}>
      {config.label}
    </span>
  )
}

interface PlanLimitsProps {
  plan: PlanInfo
  compact?: boolean
}

export function PlanLimits({ plan, compact }: PlanLimitsProps) {
  const { limits } = plan

  return (
    <div className={clsx('space-y-3', compact ? 'text-sm' : 'text-base')}>
      <div className="flex items-center justify-between">
        <span className="text-slate-400">Active Jobs</span>
        <span className="font-medium text-white">
          {limits.max_active_jobs === -1 ? '∞' : limits.max_active_jobs}
        </span>
      </div>
      <div className="flex items-center justify-between">
        <span className="text-slate-400">Queued Jobs</span>
        <span className="font-medium text-white">
          {limits.max_queued_jobs === -1 ? '∞' : limits.max_queued_jobs}
        </span>
      </div>
      <div className="flex items-center justify-between">
        <span className="text-slate-400">Priority</span>
        <span className="font-medium text-amber-400">
          Level {limits.priority_score}
        </span>
      </div>
      {!compact && (
        <div className="pt-3 border-t border-white/5">
          <p className="text-slate-500 text-sm mb-2">Allowed Services</p>
          <div className="flex flex-wrap gap-1">
            {limits.allowed_task_types.map((type) => (
              <span key={type} className="px-2 py-1 bg-white/5 rounded text-xs text-slate-300 capitalize">
                {type}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}