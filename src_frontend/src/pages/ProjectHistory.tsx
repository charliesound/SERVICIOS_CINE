import { useState } from 'react'
import { useAuthStore } from '@/store'
import { useJobs } from '@/hooks'
import { Search, Download, Calendar, Clock, CheckCircle, AlertCircle, Play, Eye, Link as LinkIcon } from 'lucide-react'
import { Link } from 'react-router-dom'
import clsx from 'clsx'

const statusConfig: Record<string, { color: string; bg: string; label: string; icon: any }> = {
  queued: { color: 'text-amber-400', bg: 'bg-amber-500/10', label: 'Queued', icon: Clock },
  running: { color: 'text-blue-400', bg: 'bg-blue-500/10', label: 'Processing', icon: Play },
  succeeded: { color: 'text-green-400', bg: 'bg-green-500/10', label: 'Completed', icon: CheckCircle },
  failed: { color: 'text-red-400', bg: 'bg-red-500/10', label: 'Failed', icon: AlertCircle },
}

interface ProjectHistoryFilters {
  search: string
  status: string
  dateRange: string
}

export default function ProjectHistory() {
  const { user } = useAuthStore()
  const { data: jobs } = useJobs({ user_id: user?.user_id })
  const [filters, setFilters] = useState<ProjectHistoryFilters>({
    search: '',
    status: 'all',
    dateRange: '30',
  })
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')

  const filteredJobs = jobs?.filter(job => {
    const matchesSearch = !filters.search || 
      job.job_id.toLowerCase().includes(filters.search.toLowerCase()) ||
      job.task_type.toLowerCase().includes(filters.search.toLowerCase())
    const matchesStatus = filters.status === 'all' || job.status === filters.status
    return matchesSearch && matchesStatus
  }) || []

  const copyProjectLink = (jobId: string) => {
    const url = `${window.location.origin}/projects/${jobId}`
    navigator.clipboard.writeText(url)
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="heading-lg flex items-center gap-3">
            <Calendar className="w-6 h-6 text-amber-400" />
            Project History
          </h1>
          <p className="text-slate-400 mt-1">View and manage all your generated projects</p>
        </div>
        <button className="btn-secondary flex items-center gap-2">
          <Download className="w-4 h-4" />
          Export
        </button>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="flex flex-wrap gap-4">
          <div className="flex-1 min-w-[250px]">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
              <input
                type="text"
                value={filters.search}
                onChange={(e) => setFilters({ ...filters, search: e.target.value })}
                placeholder="Search projects..."
                className="input pl-10"
              />
            </div>
          </div>
          
          <div className="flex gap-2">
            <select
              value={filters.status}
              onChange={(e) => setFilters({ ...filters, status: e.target.value })}
              className="input w-auto"
            >
              <option value="all">All Status</option>
              <option value="succeeded">Completed</option>
              <option value="failed">Failed</option>
              <option value="running">Processing</option>
              <option value="queued">Queued</option>
            </select>

            <select
              value={filters.dateRange}
              onChange={(e) => setFilters({ ...filters, dateRange: e.target.value })}
              className="input w-auto"
            >
              <option value="7">Last 7 days</option>
              <option value="30">Last 30 days</option>
              <option value="90">Last 90 days</option>
              <option value="all">All time</option>
            </select>

            <div className="flex rounded-xl border border-white/10 overflow-hidden">
              <button
                onClick={() => setViewMode('grid')}
                className={clsx(
                  'p-2 transition-colors',
                  viewMode === 'grid' ? 'bg-amber-500/10 text-amber-400' : 'bg-white/5 text-slate-400 hover:text-white'
                )}
              >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
                </svg>
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={clsx(
                  'p-2 transition-colors',
                  viewMode === 'list' ? 'bg-amber-500/10 text-amber-400' : 'bg-white/5 text-slate-400 hover:text-white'
                )}
              >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Results count */}
      <div className="flex items-center justify-between text-sm">
        <span className="text-slate-400">
          Showing <span className="text-white font-medium">{filteredJobs.length}</span> projects
        </span>
      </div>

      {/* Projects Grid/List */}
      {filteredJobs.length === 0 ? (
        <div className="card text-center py-16">
          <div className="w-16 h-16 rounded-2xl bg-amber-500/10 flex items-center justify-center mx-auto mb-4">
            <Search className="w-8 h-8 text-amber-400" />
          </div>
          <h3 className="text-lg font-semibold text-white mb-2">No projects found</h3>
          <p className="text-slate-400">Try adjusting your search or filters</p>
        </div>
      ) : viewMode === 'grid' ? (
        <div className="grid grid-cols-3 gap-4">
          {filteredJobs.map((job) => {
            const statusStyle = statusConfig[job.status] || statusConfig.queued
            return (
              <div key={job.job_id} className="card card-hover group">
                <div className="flex items-start justify-between mb-4">
                  <div className="w-10 h-10 rounded-xl bg-amber-500/10 flex items-center justify-center">
                    <span className="text-amber-400 font-bold">
                      {job.task_type.charAt(0).toUpperCase()}
                    </span>
                  </div>
                  <span className={clsx('px-2.5 py-1 rounded-full text-xs font-medium border', statusStyle.bg, statusStyle.color, statusStyle.color.replace('text-', 'border-'))}>
                    {statusStyle.label}
                  </span>
                </div>
                
                <h3 className="font-semibold text-white mb-1 truncate">{job.job_id}</h3>
                <p className="text-sm text-slate-500 capitalize mb-4">{job.task_type}</p>
                
                <div className="flex items-center justify-between pt-4 border-t border-white/5">
                  <span className="text-xs text-slate-500">
                    {new Date(job.created_at).toLocaleDateString()}
                  </span>
                  <div className="flex gap-2">
                    <button 
                      onClick={() => copyProjectLink(job.job_id)}
                      className="p-1.5 rounded-lg bg-white/5 text-slate-400 hover:text-amber-400 hover:bg-amber-500/10 transition-all"
                      title="Copy link"
                    >
                      <LinkIcon className="w-4 h-4" />
                    </button>
                    <Link 
                      to={`/queue?job=${job.job_id}`}
                      className="p-1.5 rounded-lg bg-white/5 text-slate-400 hover:text-white hover:bg-white/10 transition-all"
                      title="View details"
                    >
                      <Eye className="w-4 h-4" />
                    </Link>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      ) : (
        <div className="card p-0 overflow-hidden">
          <table className="w-full">
            <thead className="bg-dark-300/50 border-b border-white/5">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-400 uppercase">Project</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-400 uppercase">Type</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-400 uppercase">Status</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-400 uppercase">Created</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-slate-400 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {filteredJobs.map((job) => {
                const statusStyle = statusConfig[job.status] || statusConfig.queued
                const StatusIcon: any = statusStyle.icon
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
                    <td className="px-4 py-4 text-sm text-slate-400 capitalize">{job.task_type}</td>
                    <td className="px-4 py-4">
                      <span className={clsx('inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border', statusStyle.bg, statusStyle.color, statusStyle.color.replace('text-', 'border-'))}>
                        <StatusIcon className="w-3 h-3" />
                        {statusStyle.label}
                      </span>
                    </td>
                    <td className="px-4 py-4 text-sm text-slate-500">
                      {new Date(job.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-4 py-4 text-right">
                      <div className="flex justify-end gap-2">
                        <button 
                          onClick={() => copyProjectLink(job.job_id)}
                          className="p-2 rounded-lg bg-white/5 text-slate-400 hover:text-amber-400 hover:bg-amber-500/10 transition-all"
                        >
                          <LinkIcon className="w-4 h-4" />
                        </button>
                        <Link 
                          to={`/queue?job=${job.job_id}`}
                          className="p-2 rounded-lg bg-white/5 text-slate-400 hover:text-white hover:bg-white/10 transition-all"
                        >
                          <Eye className="w-4 h-4" />
                        </Link>
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}