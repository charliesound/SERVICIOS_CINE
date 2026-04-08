import { useQuery } from '@tanstack/react-query'
import { queueApi } from '@/api'
import { Clock, CheckCircle, XCircle, Loader2, Gauge } from 'lucide-react'
import clsx from 'clsx'

const statusConfig: Record<string, { icon: typeof Clock; color: string; label: string }> = {
  queued: { icon: Clock, color: 'text-amber-400', label: 'Queued' },
  running: { icon: Loader2, color: 'text-blue-400', label: 'Running' },
  succeeded: { icon: CheckCircle, color: 'text-green-400', label: 'Completed' },
  failed: { icon: XCircle, color: 'text-red-400', label: 'Failed' },
  timeout: { icon: Clock, color: 'text-orange-400', label: 'Timeout' },
  canceled: { icon: XCircle, color: 'text-slate-400', label: 'Canceled' },
}

export default function QueueStatusPanel() {
  const { data: queueStatus, isLoading } = useQuery({
    queryKey: ['queue'],
    queryFn: queueApi.getStatus,
    refetchInterval: 3000,
  })

  if (isLoading) {
    return (
      <div className="space-y-4 animate-pulse">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-20 bg-slate-700/30 rounded-xl" />
        ))}
      </div>
    )
  }

  const hasBackends = queueStatus?.backends && Object.keys(queueStatus.backends).length > 0

  if (!hasBackends) {
    return (
      <div className="text-center py-8 text-slate-500">
        <Gauge className="w-10 h-10 mx-auto mb-3 opacity-50" />
        <p>No backends connected</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {queueStatus?.backends && Object.entries(queueStatus.backends).map(([backend, status]) => {
        const utilization = status.max_concurrent > 0 
          ? (status.running / status.max_concurrent) * 100 
          : 0
        
        return (
          <div key={backend} className="p-4 rounded-xl bg-dark-300/50 border border-white/5">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className={clsx(
                  'w-2 h-2 rounded-full',
                  status.running > 0 ? 'bg-green-400 animate-pulse' : 'bg-slate-500'
                )} />
                <span className="font-semibold text-white capitalize">{backend}</span>
              </div>
              <span className="text-sm text-slate-500">
                {status.running} running / {status.queue_size} queued
              </span>
            </div>

            {/* Progress Bar */}
            <div className="mb-4">
              <div className="flex justify-between text-xs text-slate-500 mb-2">
                <span>Capacity</span>
                <span className={utilization > 80 ? 'text-amber-400' : 'text-slate-400'}>
                  {Math.round(utilization)}%
                </span>
              </div>
              <div className="h-2 bg-dark-400 rounded-full overflow-hidden">
                <div
                  className={clsx(
                    'h-full rounded-full transition-all duration-500',
                    utilization > 80 ? 'bg-gradient-to-r from-amber-500 to-orange-500' :
                    utilization > 50 ? 'bg-amber-500' :
                    'bg-green-500'
                  )}
                  style={{ width: `${utilization}%` }}
                />
              </div>
            </div>

            {/* Queue Items */}
            {status.items.length > 0 && (
              <div className="space-y-2 pt-3 border-t border-white/5">
                {status.items.slice(0, 3).map((item) => {
                  const config = statusConfig[item.status] || statusConfig.queued
                  const Icon = config.icon
                  return (
                    <div key={item.job_id} className="flex items-center justify-between text-sm p-2 rounded-lg bg-white/5">
                      <span className="font-mono text-slate-400 text-xs">{item.job_id}</span>
                      <span className={clsx('flex items-center gap-1.5 text-xs', config.color)}>
                        <Icon className={clsx('w-3.5 h-3.5', item.status === 'running' && 'animate-spin')} />
                        {config.label}
                      </span>
                    </div>
                  )
                })}
                {status.items.length > 3 && (
                  <p className="text-xs text-slate-500 pl-2">
                    +{status.items.length - 3} more...
                  </p>
                )}
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}