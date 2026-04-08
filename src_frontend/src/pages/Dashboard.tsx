import { Link } from 'react-router-dom'
import { useAuthStore } from '@/store'
import { useJobs } from '@/hooks'
import QueueStatusPanel from '@/components/QueueStatusPanel'
import { PlusCircle, ArrowRight, Play, Clock, CheckCircle, XCircle, Zap } from 'lucide-react'

export default function Dashboard() {
  const { user } = useAuthStore()
  const { data: jobs } = useJobs({ user_id: user?.user_id })

  const recentJobs = jobs?.slice(0, 5) || []
  const activeJobs = jobs?.filter(j => ['queued', 'running'].includes(j.status)) || []
  const completedJobs = jobs?.filter(j => j.status === 'succeeded') || []
  const failedJobs = jobs?.filter(j => ['failed', 'timeout'].includes(j.status)) || []

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="heading-xl">Welcome back</h1>
          <p className="text-slate-400 mt-1">Ready to create something amazing?</p>
        </div>
        <Link to="/create" className="btn-primary flex items-center gap-2">
          <Zap className="w-4 h-4" />
          New Project
        </Link>
      </div>

      {/* Stats Grid - estilo MITO */}
      <div className="grid grid-cols-4 gap-4">
        <div className="stat-card group">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-amber-500/10 flex items-center justify-center">
              <Play className="w-5 h-5 text-amber-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{activeJobs.length}</p>
              <p className="text-sm text-slate-400">Active</p>
            </div>
          </div>
        </div>

        <div className="stat-card group">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-slate-700/30 flex items-center justify-center">
              <Clock className="w-5 h-5 text-slate-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{jobs?.length || 0}</p>
              <p className="text-sm text-slate-400">Total</p>
            </div>
          </div>
        </div>

        <div className="stat-card group">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-green-500/10 flex items-center justify-center">
              <CheckCircle className="w-5 h-5 text-green-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{completedJobs.length}</p>
              <p className="text-sm text-slate-400">Completed</p>
            </div>
          </div>
        </div>

        <div className="stat-card group">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-red-500/10 flex items-center justify-center">
              <XCircle className="w-5 h-5 text-red-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{failedJobs.length}</p>
              <p className="text-sm text-slate-400">Failed</p>
            </div>
          </div>
        </div>
      </div>

      {/* Queue Panel */}
      <div className="card card-hover">
        <div className="flex items-center justify-between mb-4">
          <h2 className="heading-md">Queue Status</h2>
          <Link to="/queue" className="btn-ghost flex items-center gap-1 text-sm">
            View all <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
        <QueueStatusPanel />
      </div>

      {/* Recent Jobs */}
      {recentJobs.length > 0 && (
        <div className="card card-hover">
          <div className="flex items-center justify-between mb-4">
            <h2 className="heading-md">Recent Projects</h2>
            <Link to="/queue" className="btn-ghost flex items-center gap-1 text-sm">
              View all <ArrowRight className="w-4 h-4" />
            </Link>
          </div>

          <div className="space-y-2">
            {recentJobs.map((job) => (
              <div 
                key={job.job_id} 
                className="flex items-center justify-between p-4 bg-dark-300/50 rounded-xl hover:bg-dark-300 transition-colors"
              >
                <div className="flex items-center gap-4">
                  <div className="w-8 h-8 rounded-lg bg-amber-500/10 flex items-center justify-center">
                    <span className="text-amber-400 text-xs font-bold">
                      {job.task_type.charAt(0).toUpperCase()}
                    </span>
                  </div>
                  <div>
                    <p className="font-mono text-sm text-slate-300">{job.job_id}</p>
                    <p className="text-xs text-slate-500 capitalize">{job.task_type}</p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                    job.status === 'succeeded' ? 'bg-green-500/10 text-green-400' :
                    job.status === 'failed' ? 'bg-red-500/10 text-red-400' :
                    job.status === 'running' ? 'bg-blue-500/10 text-blue-400' :
                    'bg-amber-500/10 text-amber-400'
                  }`}>
                    {job.status}
                  </span>
                  <span className="text-xs text-slate-500">
                    {new Date(job.created_at).toLocaleTimeString()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Empty state */}
      {recentJobs.length === 0 && (
        <div className="card text-center py-12">
          <div className="w-16 h-16 rounded-2xl bg-amber-500/10 flex items-center justify-center mx-auto mb-4">
            <Zap className="w-8 h-8 text-amber-400" />
          </div>
          <h3 className="text-lg font-semibold text-white mb-2">No projects yet</h3>
          <p className="text-slate-400 mb-6">Create your first project to get started</p>
          <Link to="/create" className="btn-primary inline-flex items-center gap-2">
            <PlusCircle className="w-4 h-4" />
            Create Project
          </Link>
        </div>
      )}
    </div>
  )
}