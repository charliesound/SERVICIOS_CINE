import { Loader2, CheckCircle2, AlertCircle } from 'lucide-react'

interface JobProgressProps {
  progress_percent?: number | null
  progress_stage?: string | null
  status: string
  job_type: string
}

export function JobProgress({ progress_percent, progress_stage, status, job_type }: JobProgressProps) {
  if (status === 'completed') {
    return (
      <div className="flex items-center gap-2 text-sm text-emerald-400">
        <CheckCircle2 className="w-4 h-4" />
        <span>Completado</span>
      </div>
    )
  }
  if (status === 'failed') {
    return (
      <div className="flex items-center gap-2 text-sm text-red-400">
        <AlertCircle className="w-4 h-4" />
        <span>Fallido</span>
      </div>
    )
  }
  if (status === 'pending' || status === 'processing') {
    const pct = progress_percent ?? 0
    return (
      <div className="space-y-1">
        <div className="flex items-center justify-between text-xs text-gray-400">
          <span className="flex items-center gap-1">
            <Loader2 className="w-3 h-3 animate-spin" />
            {progress_stage || (job_type === 'analyze' ? 'Analizando guion...' : 'Generando storyboard...')}
          </span>
          <span>{pct}%</span>
        </div>
        <div className="w-full h-1.5 bg-white/10 rounded-full overflow-hidden">
          <div
            className="h-full bg-amber-500 transition-all duration-500"
            style={{ width: `${pct}%` }}
          />
        </div>
      </div>
    )
  }
  return null
}
