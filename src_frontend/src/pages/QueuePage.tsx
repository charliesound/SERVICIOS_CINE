import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { queueApi } from '@/api'
import { useQueueStatus, useJobs } from '@/hooks'
import { ListOrdered, RefreshCw, XCircle, RotateCcw, Clock, Play, CheckCircle, AlertCircle, Zap } from 'lucide-react'
import clsx from 'clsx'

const statusConfig: Record<string, { color: string; bg: string; label: string; icon: any }> = {
  queued: { color: 'text-amber-400', bg: 'bg-amber-500/10 border-amber-500/20', label: 'Queued', icon: Clock },
  running: { color: 'text-blue-400', bg: 'bg-blue-500/10 border-blue-500/20', label: 'Running', icon: Play },
  succeeded: { color: 'text-green-400', bg: 'bg-green-500/10 border-green-500/20', label: 'Completed', icon: CheckCircle },
  failed: { color: 'text-red-400', bg: 'bg-red-500/10 border-red-500/20', label: 'Failed', icon: AlertCircle },
  timeout: { color: 'text-orange-400', bg: 'bg-orange-500/10 border-orange-500/20', label: 'Timeout', icon: AlertCircle },
  canceled: { color: 'text-slate-400', bg: 'bg-slate-500/10 border-slate-500/20', label: 'Canceled', icon: XCircle },
}

export default function QueuePage() {
  const { data: queueStatus } = useQueueStatus()
  const { data: jobs, refetch: refetchJobs } = useJobs()
  const [filter, setFilter] = useState<string>('all')

  const cancelMutation = useMutation({
    mutationFn: (jobId: string) => queueApi.cancelJob(jobId),
    onSuccess: () => refetchJobs(),
  })

  const retryMutation = useMutation({
    mutationFn: (jobId: string) => queueApi.retryJob(jobId),
    onSuccess: () => refetchJobs(),
  })

  const filteredJobs = jobs?.filter(job => {
    if (filter === 'all') return true
    return job.status === filter
  }) || []

  const filterTabs = [
    { key: 'all', label: 'All' },
    { key: 'queued', label: 'Queued' },
    { key: 'running', label: 'Running' },
    { key: 'succeeded', label: 'Completed' },
    { key: 'failed', label: 'Failed' },
  ]

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="heading-lg flex items-center gap-3">
            <Zap className="w-6 h-6 text-amber-400" />
            Project Queue
          </h1>
          <p className="text-slate-400 mt-1">Monitor and manage your AI generation tasks</p>
        </div>
        <button 
          onClick={() => refetchJobs()} 
          className="btn-secondary flex items-center gap-2"
        >
          <RefreshCw className="w-4 h-4" />
          Refresh
        </button>
      </div>

      {/* Filter Tabs */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        {filterTabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setFilter(tab.key)}
            className={clsx(
              'px-4 py-2 rounded-xl text-sm font-medium transition-all whitespace-nowrap',
              filter === tab.key
                ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                : 'bg-white/5 text-slate-400 hover:bg-white/10 hover:text-white'
            )}
          >
            {tab.label}
            {tab.key !== 'all' && (
              <span className="ml-2 px-1.5 py-0.5 rounded bg-white/10 text-xs">
                {jobs?.filter(j => tab.key === 'all' || j.status === tab.key).length || 0}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Jobs Table */}
      {filteredJobs.length === 0 ? (
        <div className="card text-center py-16">
          <div className="w-16 h-16 rounded-2xl bg-amber-500/10 flex items-center justify-center mx-auto mb-4">
            <ListOrdered className="w-8 h-8 text-amber-400" />
          </div>
          <h3 className="text-lg font-semibold text-white mb-2">No projects found</h3>
          <p className="text-slate-400">Create a new project to get started</p>
        </div>
      ) : (
        <div className="card p-0 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-dark-300/50 border-b border-white/5">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Project</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Type</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Backend</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Status</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Created</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-slate-400 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {filteredJobs.map((job) => {
                  const statusStyle = statusConfig[job.status] || statusConfig.queued
                  const StatusIcon = statusStyle.icon
                  return (
                    <tr key={job.job_id} className="hover:bg-white/[0.02] transition-colors">
                      <td className="px-4 py-4">
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 rounded-lg bg-amber-500/10 flex items-center justify-center">
                            <span className="text-amber-400 text-xs font-bold">
                              {job.task_type.charAt(0).toUpperCase()}
                            </span>
                          </div>
                          <span className="font-mono text-sm text-slate-300">{job.job_id}</span>
                        </div>
                      </td>
                      <td className="px-4 py-4 text-sm text-slate-300 capitalize">{job.task_type}</td>
                      <td className="px-4 py-4 text-sm text-slate-400">{job.backend}</td>
                      <td className="px-4 py-4">
                        <span className={clsx('inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium border', statusStyle.bg, statusStyle.color)}>
                          <StatusIcon className="w-3 h-3" />
                          {statusStyle.label}
                        </span>
                      </td>
                      <td className="px-4 py-4 text-sm text-slate-500">
                        {new Date(job.created_at).toLocaleString()}
                      </td>
                      <td className="px-4 py-4 text-right">
                        <div className="flex justify-end gap-2">
                          {job.status === 'queued' && (
                            <button
                              onClick={() => cancelMutation.mutate(job.job_id)}
                              className="p-2 rounded-lg bg-white/5 text-slate-400 hover:text-red-400 hover:bg-red-500/10 transition-all"
                              title="Cancel"
                            >
                              <XCircle className="w-4 h-4" />
                            </button>
                          )}
                          {['failed', 'timeout', 'canceled'].includes(job.status) && (
                            <button
                              onClick={() => retryMutation.mutate(job.job_id)}
                              className="p-2 rounded-lg bg-white/5 text-slate-400 hover:text-green-400 hover:bg-green-500/10 transition-all"
                              title="Retry"
                            >
                              <RotateCcw className="w-4 h-4" />
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Backend Summary */}
      {queueStatus && (
        <div className="card">
          <h2 className="heading-md mb-4">Backend Status</h2>
          <div className="grid grid-cols-4 gap-4">
            {Object.entries(queueStatus.backends).map(([backend, status]) => (
              <div key={backend} className="p-4 rounded-xl bg-dark-300/50 border border-white/5 hover:border-amber-500/20 transition-all">
                <div className="flex items-center gap-2 mb-3">
                  <div className={clsx(
                    'w-2 h-2 rounded-full',
                    status.running > 0 ? 'bg-green-400' : 'bg-slate-500'
                  )} />
                  <p className="font-medium text-white capitalize">{backend}</p>
                </div>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-slate-500">Running</span>
                    <span className="text-blue-400 font-medium">{status.running}/{status.max_concurrent}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Queued</span>
                    <span className="text-amber-400 font-medium">{status.queue_size}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}