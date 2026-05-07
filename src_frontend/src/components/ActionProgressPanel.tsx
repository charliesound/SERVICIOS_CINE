import { AlertCircle, CheckCircle2, Loader2, RotateCcw } from 'lucide-react'

export interface ActionProgressState {
  title: string
  status: 'idle' | 'queued' | 'processing' | 'completed' | 'failed'
  percent: number
  label: string
  helperText?: string
  estimated?: boolean
  jobId?: string | null
  errorMessage?: string | null
}

interface ActionProgressPanelProps {
  progress: ActionProgressState | null
  onRetry?: () => void
  retryLabel?: string
}

export function ActionProgressPanel({ progress, onRetry, retryLabel }: ActionProgressPanelProps) {
  if (!progress || progress.status === 'idle') return null

  const isRunning = progress.status === 'queued' || progress.status === 'processing'
  const isCompleted = progress.status === 'completed'
  const isFailed = progress.status === 'failed'

  return (
    <div className="rounded-2xl border border-white/10 bg-dark-200/80 p-4 space-y-3" aria-busy={isRunning}>
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm font-semibold text-white">{progress.title}</p>
          <p className="text-xs text-gray-400 mt-1">{progress.label}</p>
          {progress.helperText && (
            <p className="text-xs text-gray-500 mt-1">{progress.helperText}</p>
          )}
          {progress.jobId && (
            <p className="text-[11px] text-gray-500 mt-1">job_id: {progress.jobId}</p>
          )}
        </div>
        {isRunning && <Loader2 className="w-4 h-4 animate-spin text-amber-400 mt-0.5" />}
        {isCompleted && <CheckCircle2 className="w-4 h-4 text-emerald-400 mt-0.5" />}
        {isFailed && <AlertCircle className="w-4 h-4 text-red-400 mt-0.5" />}
      </div>

      <div className="space-y-1">
        <div className="flex items-center justify-between text-xs text-gray-400">
          <span>{progress.estimated ? 'Progreso estimado' : 'Progreso real'}</span>
          <span>{Math.max(0, Math.min(100, progress.percent))}%</span>
        </div>
        <div className="w-full h-2 rounded-full bg-white/10 overflow-hidden">
          <div
            className={`h-full transition-all duration-500 ${isFailed ? 'bg-red-400' : isCompleted ? 'bg-emerald-400' : 'bg-amber-400'}`}
            style={{ width: `${Math.max(0, Math.min(100, progress.percent))}%` }}
          />
        </div>
      </div>

      {isFailed && progress.errorMessage && (
        <div className="rounded-xl border border-red-500/20 bg-red-500/10 px-3 py-2 text-sm text-red-300">
          {progress.errorMessage}
        </div>
      )}

      {isFailed && onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="inline-flex items-center gap-2 rounded-xl border border-amber-500/20 px-3 py-2 text-sm text-amber-300 hover:bg-amber-500/10 transition-colors"
        >
          <RotateCcw className="w-4 h-4" />
          {retryLabel || 'Reintentar'}
        </button>
      )}
    </div>
  )
}
