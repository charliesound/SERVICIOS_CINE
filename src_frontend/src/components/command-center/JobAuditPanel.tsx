import { t } from '@/i18n'
import { X, CheckCircle, Clock } from 'lucide-react'

interface AuditEvent {
  id: string
  event: string
  amount: number
  date: string
}

interface JobAuditPanelProps {
  jobId: string
  isOpen: boolean
  onClose: () => void
}

const mockAuditEvents: Record<string, AuditEvent[]> = {
  'job_123': [
    { id: '1', event: 'estimated', amount: 50, date: '2026-06-09T10:00:00Z' },
    { id: '2', event: 'reserved', amount: 50, date: '2026-06-09T10:01:00Z' },
    { id: '3', event: 'consumed', amount: 48, date: '2026-06-09T10:15:00Z' },
    { id: '4', event: 'released', amount: 2, date: '2026-06-09T10:15:05Z' }
  ],
  'job_124': [
    { id: '5', event: 'estimated', amount: 120, date: '2026-06-09T10:30:00Z' },
    { id: '6', event: 'reserved', amount: 120, date: '2026-06-09T10:31:00Z' }
  ]
}

export default function JobAuditPanel({ jobId, isOpen, onClose }: JobAuditPanelProps) {
  if (!isOpen) return null

  const events = mockAuditEvents[jobId] || []

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="bg-dark-200 border border-white/10 rounded-2xl w-full max-w-md shadow-2xl overflow-hidden flex flex-col">
        <div className="flex items-center justify-between p-4 border-b border-white/10 bg-dark-300/50">
          <div>
            <h3 className="font-semibold text-white">{t('internal.commandCenter.aiJobs.jobs.audit.title')}</h3>
            <p className="text-xs text-slate-400 font-mono mt-0.5">{jobId}</p>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-white/5 rounded-lg text-slate-400 hover:text-white transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-4 flex-1 overflow-y-auto max-h-[60vh]">
          {events.length === 0 ? (
            <div className="text-center py-8 text-slate-500">
              <Clock className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <p>{t('internal.commandCenter.aiJobs.jobs.audit.emptyAudit')}</p>
            </div>
          ) : (
            <div className="space-y-4 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-white/10 before:to-transparent">
              {events.map((evt) => (
                <div key={evt.id} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                  <div className="flex items-center justify-center w-10 h-10 rounded-full border-4 border-dark-200 bg-dark-300 text-slate-500 shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 z-10">
                    <CheckCircle className="w-4 h-4 text-amber-500" />
                  </div>
                  <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] card p-3 border-white/5 shadow-md">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-bold text-white capitalize text-sm">{evt.event}</span>
                      <span className="text-amber-400 font-mono text-sm font-medium">{evt.amount} CR</span>
                    </div>
                    <p className="text-xs text-slate-500">{new Date(evt.date).toLocaleTimeString()}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="p-4 border-t border-white/10 bg-dark-300/50 flex justify-end">
          <button onClick={onClose} className="btn-secondary text-sm px-4 py-2">
            {t('internal.commandCenter.aiJobs.jobs.actions.close')}
          </button>
        </div>
      </div>
    </div>
  )
}
