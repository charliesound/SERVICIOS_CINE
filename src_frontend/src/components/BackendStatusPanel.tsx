import { useQuery } from '@tanstack/react-query'
import { opsApi } from '@/api'
import { Server, Cpu, Wifi, WifiOff } from 'lucide-react'
import clsx from 'clsx'

const backendColors: Record<string, { bg: string; border: string; text: string }> = {
  still: { bg: 'bg-blue-500/10', border: 'border-blue-500/20', text: 'text-blue-400' },
  video: { bg: 'bg-purple-500/10', border: 'border-purple-500/20', text: 'text-purple-400' },
  dubbing: { bg: 'bg-green-500/10', border: 'border-green-500/20', text: 'text-green-400' },
  lab: { bg: 'bg-amber-500/10', border: 'border-amber-500/20', text: 'text-amber-400' },
}

export default function BackendStatusPanel() {
  const { data: instances, isLoading } = useQuery({
    queryKey: ['instances'],
    queryFn: opsApi.getInstances,
    refetchInterval: 10000,
  })

  if (isLoading) {
    return (
      <div className="space-y-4 animate-pulse">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="h-20 bg-slate-700/30 rounded-xl" />
        ))}
      </div>
    )
  }

  const hasBackends = instances?.backends && Object.keys(instances.backends).length > 0

  if (!hasBackends) {
    return (
      <div className="card text-center py-12">
        <div className="w-14 h-14 rounded-2xl bg-slate-700/30 flex items-center justify-center mx-auto mb-4">
          <Server className="w-7 h-7 text-slate-500" />
        </div>
        <h3 className="text-lg font-semibold text-white mb-2">No backends connected</h3>
        <p className="text-slate-500">Configure ComfyUI instances to enable AI generation</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {instances?.backends && Object.entries(instances.backends).map(([key, backend]) => {
        const colors = backendColors[key] || backendColors.lab
        
        return (
          <div
            key={key}
            className="p-4 rounded-xl bg-dark-300/50 border border-white/5 hover:border-amber-500/20 transition-all"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className={clsx('w-10 h-10 rounded-xl flex items-center justify-center border', colors.bg, colors.border)}>
                  <Cpu className={clsx('w-5 h-5', colors.text)} />
                </div>
                <div>
                  <p className="font-semibold text-white capitalize">{key}</p>
                  <p className="text-xs text-slate-500 font-mono">
                    {backend.host}:{backend.port}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-6">
                <div className="text-right">
                  <p className="text-lg font-bold text-white">
                    {backend.current_jobs}
                    <span className="text-slate-500 font-normal">/{backend.max_concurrent_jobs}</span>
                  </p>
                  <p className="text-xs text-slate-500">jobs</p>
                </div>

                <div className="flex items-center gap-2">
                  {backend.healthy ? (
                    <Wifi className="w-4 h-4 text-green-400" />
                  ) : (
                    <WifiOff className="w-4 h-4 text-red-400" />
                  )}
                  <div className={clsx(
                    'w-2.5 h-2.5 rounded-full',
                    backend.healthy ? 'bg-green-400 shadow-lg shadow-green-400/50' : 'bg-red-500'
                  )} />
                </div>
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}