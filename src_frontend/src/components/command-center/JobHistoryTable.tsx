import { useState } from 'react'
import { t } from '@/i18n'
import { Search, XCircle } from 'lucide-react'
import JobStatusBadge from './JobStatusBadge'
import JobAuditPanel from './JobAuditPanel'

interface MockJob {
  id: string
  type: string
  status: string
  costs: {
    estimated: number
    reserved: number
    consumed: number
    released: number
  }
  createdAt: string
}

const mockJobs: MockJob[] = [
  {
    id: 'job_123',
    type: 'script_analysis',
    status: 'consumed',
    costs: { estimated: 50, reserved: 50, consumed: 48, released: 2 },
    createdAt: '2026-06-09T10:00:00Z'
  },
  {
    id: 'job_124',
    type: 'storyboard_gen',
    status: 'running',
    costs: { estimated: 120, reserved: 120, consumed: 0, released: 0 },
    createdAt: '2026-06-09T10:30:00Z'
  },
  {
    id: 'job_125',
    type: 'budget_estimation',
    status: 'queued',
    costs: { estimated: 15, reserved: 15, consumed: 0, released: 0 },
    createdAt: '2026-06-09T10:45:00Z'
  },
  {
    id: 'job_126',
    type: 'script_analysis',
    status: 'cancelled',
    costs: { estimated: 50, reserved: 0, consumed: 0, released: 50 },
    createdAt: '2026-06-08T15:20:00Z'
  },
  {
    id: 'job_127',
    type: 'storyboard_gen',
    status: 'failed',
    costs: { estimated: 200, reserved: 200, consumed: 40, released: 160 },
    createdAt: '2026-06-07T09:10:00Z'
  }
]

export default function JobHistoryTable() {
  const [selectedJobId, setSelectedJobId] = useState<string | null>(null)

  const handleCancel = (jobId: string) => {
    console.log('Mock cancel job:', jobId)
  }

  const isCancelable = (status: string) => {
    return ['created', 'estimated', 'credit_checked', 'reserved', 'queued'].includes(status)
  }

  return (
    <>
      <div className="card p-0 overflow-hidden border border-white/10 bg-dark-300/40">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-dark-300/80 border-b border-white/5">
              <tr>
                <th className="px-4 py-4 text-left text-xs font-semibold text-slate-400 uppercase tracking-wider">{t('internal.commandCenter.aiJobs.jobs.table.jobInfo')}</th>
                <th className="px-4 py-4 text-left text-xs font-semibold text-slate-400 uppercase tracking-wider">{t('internal.commandCenter.aiJobs.jobs.table.status')}</th>
                <th className="px-4 py-4 text-left text-xs font-semibold text-slate-400 uppercase tracking-wider">{t('internal.commandCenter.aiJobs.jobs.table.costs')}</th>
                <th className="px-4 py-4 text-left text-xs font-semibold text-slate-400 uppercase tracking-wider">{t('internal.commandCenter.aiJobs.jobs.table.createdAt')}</th>
                <th className="px-4 py-4 text-right text-xs font-semibold text-slate-400 uppercase tracking-wider">{t('internal.commandCenter.aiJobs.jobs.table.actions')}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {mockJobs.map((job) => (
                <tr key={job.id} className="hover:bg-white/[0.02] transition-colors group">
                  <td className="px-4 py-4">
                    <div className="flex flex-col">
                      <span className="font-mono text-sm text-white mb-1">{job.id}</span>
                      <span className="text-xs text-slate-500 capitalize">{job.type.replace('_', ' ')}</span>
                    </div>
                  </td>
                  <td className="px-4 py-4">
                    <JobStatusBadge status={job.status} />
                  </td>
                  <td className="px-4 py-4">
                    <div className="flex flex-col gap-1 text-xs font-mono">
                      <div className="flex justify-between w-32">
                        <span className="text-slate-500">{t('internal.commandCenter.aiJobs.jobs.costLabels.estimated')}</span>
                        <span className="text-slate-300">{job.costs.estimated} CR</span>
                      </div>
                      <div className="flex justify-between w-32">
                        <span className="text-slate-500">{t('internal.commandCenter.aiJobs.jobs.costLabels.reserved')}</span>
                        <span className="text-amber-400">{job.costs.reserved} CR</span>
                      </div>
                      <div className="flex justify-between w-32">
                        <span className="text-slate-500">{t('internal.commandCenter.aiJobs.jobs.costLabels.consumed')}</span>
                        <span className="text-emerald-400">{job.costs.consumed} CR</span>
                      </div>
                      <div className="flex justify-between w-32">
                        <span className="text-slate-500">{t('internal.commandCenter.aiJobs.jobs.costLabels.released')}</span>
                        <span className="text-slate-400">{job.costs.released} CR</span>
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-4 text-sm text-slate-400">
                    {new Date(job.createdAt).toLocaleString()}
                  </td>
                  <td className="px-4 py-4 text-right">
                    <div className="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button
                        onClick={() => setSelectedJobId(job.id)}
                        className="btn-ghost px-3 py-1.5 text-xs flex items-center gap-1.5"
                        title={t('internal.commandCenter.aiJobs.jobs.actions.viewAudit')}
                      >
                        <Search className="w-3.5 h-3.5" />
                        {t('internal.commandCenter.aiJobs.jobs.actions.viewAudit')}
                      </button>
                      <button
                        onClick={() => handleCancel(job.id)}
                        disabled={!isCancelable(job.status)}
                        className="btn-secondary px-3 py-1.5 text-xs flex items-center gap-1.5 disabled:opacity-30 disabled:cursor-not-allowed hover:bg-red-500/10 hover:text-red-400 hover:border-red-500/30"
                        title={t('internal.commandCenter.aiJobs.jobs.actions.cancel')}
                      >
                        <XCircle className="w-3.5 h-3.5" />
                        {t('internal.commandCenter.aiJobs.jobs.actions.cancel')}
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <JobAuditPanel
        jobId={selectedJobId || ''}
        isOpen={!!selectedJobId}
        onClose={() => setSelectedJobId(null)}
      />
    </>
  )
}
