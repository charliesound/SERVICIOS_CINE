import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { renderApi } from '@/api'
import { Clock, CheckCircle, AlertCircle, Play, Image, Video, Mic, FlaskConical, Share2 } from 'lucide-react'
import clsx from 'clsx'
import { useSeo } from '@/hooks/useSeo'

const statusConfig: Record<string, { color: string; bg: string; label: string; icon: any }> = {
  queued: { color: 'text-amber-400', bg: 'bg-amber-500/10 border-amber-500/20', label: 'Queued', icon: Clock },
  running: { color: 'text-blue-400', bg: 'bg-blue-500/10 border-blue-500/20', label: 'Processing', icon: Play },
  succeeded: { color: 'text-green-400', bg: 'bg-green-500/10 border-green-500/20', label: 'Completed', icon: CheckCircle },
  failed: { color: 'text-red-400', bg: 'bg-red-500/10 border-red-500/20', label: 'Failed', icon: AlertCircle },
  timeout: { color: 'text-orange-400', bg: 'bg-orange-500/10 border-orange-500/20', label: 'Timeout', icon: AlertCircle },
  canceled: { color: 'text-slate-400', bg: 'bg-slate-500/10 border-slate-500/20', label: 'Canceled', icon: Clock },
}

const taskIcons: Record<string, typeof Image> = {
  still: Image,
  video: Video,
  dubbing: Mic,
  experimental: FlaskConical,
}

export default function ClientPortal() {
  const { jobId } = useParams<{ jobId: string }>()
  
  const { data: job, isLoading, error } = useQuery({
    queryKey: ['job', jobId],
    queryFn: () => renderApi.getJob(jobId!),
    enabled: !!jobId,
    refetchInterval: 5000,
  })

  useSeo({
    title: job ? `${job.status} - Project ${jobId?.slice(0, 8)}` : 'Estado del proyecto',
    description: 'Vista privada para revisar el estado de una generacion o entrega audiovisual.',
    path: jobId ? `/project/${jobId}` : '/project',
    robots: 'noindex, nofollow',
  })

  if (isLoading) {
    return (
      <div className="min-h-screen bg-dark-300 flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 rounded-full border-2 border-amber-500/30 border-t-amber-500 animate-spin mx-auto mb-4" />
          <p className="text-slate-400">Loading project...</p>
        </div>
      </div>
    )
  }

  if (error || !job) {
    return (
      <div className="min-h-screen bg-dark-300 flex items-center justify-center">
        <div className="card text-center py-12 max-w-md">
          <div className="w-16 h-16 rounded-2xl bg-red-500/10 flex items-center justify-center mx-auto mb-4">
            <AlertCircle className="w-8 h-8 text-red-400" />
          </div>
          <h1 className="text-2xl font-bold text-white mb-2">Project Not Found</h1>
          <p className="text-slate-400">The project you're looking for doesn't exist or has been removed.</p>
        </div>
      </div>
    )
  }

  const statusStyle = statusConfig[job.status] || statusConfig.queued
  const StatusIcon = statusStyle.icon
  const TaskIcon = taskIcons[job.task_type] || Image

  return (
    <div className="min-h-screen bg-dark-300 flex items-center justify-center p-4">
      <div className="w-full max-w-2xl">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-400 to-amber-600 flex items-center justify-center">
              <TaskIcon className="w-5 h-5 text-black" />
            </div>
          </div>
          <h1 className="text-2xl font-bold text-white">Project Status</h1>
          <p className="text-slate-400 mt-1">Track your AI generation project</p>
        </div>

        {/* Project Card */}
        <div className="card">
          {/* Job ID */}
          <div className="flex items-center justify-between pb-4 border-b border-white/5 mb-6">
            <div>
              <p className="text-sm text-slate-500">Project ID</p>
              <p className="font-mono text-lg text-white">{job.job_id}</p>
            </div>
            <button
              onClick={() => navigator.clipboard.writeText(window.location.href)}
              className="p-2 rounded-lg bg-white/5 text-slate-400 hover:text-amber-400 hover:bg-amber-500/10 transition-all"
              title="Share link"
            >
              <Share2 className="w-5 h-5" />
            </button>
          </div>

          {/* Status */}
          <div className="text-center py-8">
            <div className={clsx(
              'w-20 h-20 rounded-2xl flex items-center justify-center mx-auto mb-4 border-2',
              statusStyle.bg
            )}>
              <StatusIcon className={clsx('w-10 h-10', statusStyle.color)} />
            </div>
            <h2 className={clsx('text-2xl font-bold mb-2', statusStyle.color)}>
              {statusStyle.label}
            </h2>
            <p className="text-slate-400 capitalize">{job.task_type} Generation</p>
            
            {job.status === 'running' && (
              <div className="mt-4">
                <div className="w-48 h-1 bg-dark-300 rounded-full mx-auto overflow-hidden">
                  <div className="h-full bg-blue-500 animate-pulse rounded-full" style={{ width: '60%' }} />
                </div>
                <p className="text-xs text-slate-500 mt-2">Processing your request...</p>
              </div>
            )}
          </div>

          {/* Details */}
          <div className="grid grid-cols-2 gap-4 pt-6 border-t border-white/5">
            <div className="p-4 rounded-xl bg-dark-300/50">
              <p className="text-sm text-slate-500 mb-1">Type</p>
              <p className="font-medium text-white capitalize">{job.task_type}</p>
            </div>
            <div className="p-4 rounded-xl bg-dark-300/50">
              <p className="text-sm text-slate-500 mb-1">Backend</p>
              <p className="font-medium text-white capitalize">{job.backend || 'Processing'}</p>
            </div>
            <div className="p-4 rounded-xl bg-dark-300/50">
              <p className="text-sm text-slate-500 mb-1">Created</p>
              <p className="font-medium text-white">{new Date(job.created_at).toLocaleString()}</p>
            </div>
            {job.completed_at && (
              <div className="p-4 rounded-xl bg-dark-300/50">
                <p className="text-sm text-slate-500 mb-1">Completed</p>
                <p className="font-medium text-white">{new Date(job.completed_at).toLocaleString()}</p>
              </div>
            )}
          </div>

          {/* Error message */}
          {job.error && (
            <div className="mt-6 p-4 rounded-xl bg-red-500/10 border border-red-500/20">
              <p className="text-sm text-red-400">{job.error}</p>
            </div>
          )}

          {/* Actions */}
          {job.status === 'failed' && (
            <div className="mt-6 pt-6 border-t border-white/5">
              <button className="btn-primary w-full">
                Retry Project
              </button>
            </div>
          )}
        </div>

        {/* Footer */}
        <p className="text-center text-slate-500 text-sm mt-8">
          Powered by AILinkCinema
        </p>
      </div>
    </div>
  )
}
