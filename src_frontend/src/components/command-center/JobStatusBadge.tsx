import clsx from 'clsx'
import { t } from '@/i18n'
import { Clock, Play, CheckCircle, AlertCircle, XCircle, Search, Save, Package, RefreshCw, Send, DollarSign } from 'lucide-react'

const badgeConfig: Record<string, { color: string; bg: string; icon: any }> = {
  created: { color: 'text-slate-400', bg: 'bg-slate-500/10 border-slate-500/20', icon: Package },
  estimated: { color: 'text-purple-400', bg: 'bg-purple-500/10 border-purple-500/20', icon: Search },
  credit_checked: { color: 'text-indigo-400', bg: 'bg-indigo-500/10 border-indigo-500/20', icon: CheckCircle },
  reserved: { color: 'text-amber-400', bg: 'bg-amber-500/10 border-amber-500/20', icon: Save },
  queued: { color: 'text-orange-400', bg: 'bg-orange-500/10 border-orange-500/20', icon: Clock },
  running: { color: 'text-blue-400', bg: 'bg-blue-500/10 border-blue-500/20', icon: Play },
  succeeded: { color: 'text-green-400', bg: 'bg-green-500/10 border-green-500/20', icon: CheckCircle },
  failed: { color: 'text-red-400', bg: 'bg-red-500/10 border-red-500/20', icon: AlertCircle },
  cancelled: { color: 'text-slate-400', bg: 'bg-slate-500/10 border-slate-500/20', icon: XCircle },
  consume_pending: { color: 'text-teal-400', bg: 'bg-teal-500/10 border-teal-500/20', icon: RefreshCw },
  consumed: { color: 'text-emerald-400', bg: 'bg-emerald-500/10 border-emerald-500/20', icon: DollarSign },
  release_pending: { color: 'text-pink-400', bg: 'bg-pink-500/10 border-pink-500/20', icon: RefreshCw },
  released: { color: 'text-rose-400', bg: 'bg-rose-500/10 border-rose-500/20', icon: Send },
  expired: { color: 'text-slate-500', bg: 'bg-slate-500/10 border-slate-500/20', icon: Clock },
}

export default function JobStatusBadge({ status }: { status: string }) {
  const config = badgeConfig[status] || badgeConfig['created']
  const Icon = config.icon

  return (
    <span className={clsx('inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium border whitespace-nowrap', config.bg, config.color)}>
      <Icon className="w-3 h-3" />
      {t(`internal.commandCenter.aiJobs.jobs.status.${status}`)}
    </span>
  )
}
