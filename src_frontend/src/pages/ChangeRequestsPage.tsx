import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { FileText, Check, X } from 'lucide-react'
import { useLanguage } from '@/i18n'

interface ChangeRequest {
  id: string
  source_type: string
  target_module: string
  change_type: string
  severity: string
  title: string
  summary: string
  status: string
  created_at: string
}

const STATUS_LABEL_KEYS: Record<string, string> = {
  proposed: 'internal.changeRequests.status.proposed',
  pending_approval: 'internal.changeRequests.status.pendingApproval',
  approved: 'internal.changeRequests.status.approved',
  rejected: 'internal.changeRequests.status.rejected',
  applied: 'internal.changeRequests.status.applied',
  cancelled: 'internal.changeRequests.status.cancelled',
}

const SEVERITY_LABEL_KEYS: Record<string, string> = {
  low: 'internal.changeRequests.severity.low',
  medium: 'internal.changeRequests.severity.medium',
  high: 'internal.changeRequests.severity.high',
  critical: 'internal.changeRequests.severity.critical',
}

export default function ChangeRequestsPage() {
  const { t } = useLanguage()
  const { projectId = '' } = useParams()
  const [changes, setChanges] = useState<ChangeRequest[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    fetchChanges()
  }, [projectId])

  async function fetchChanges() {
    try {
      setIsLoading(true)
      const response = await fetch(`/api/projects/${projectId}/change-requests`, {
        headers: { 'Content-Type': 'application/json' },
      })
      const data = await response.json()
      setChanges(data.change_requests || [])
    } catch (error) {
      console.error('Error fetching changes:', error)
    } finally {
      setIsLoading(false)
    }
  }

  async function approveChange(id: string) {
    try {
      await fetch(`/api/projects/${projectId}/change-requests/${id}/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ comment: '' }),
      })
      fetchChanges()
    } catch (error) {
      console.error('Error approving:', error)
    }
  }

  async function rejectChange(id: string) {
    try {
      await fetch(`/api/projects/${projectId}/change-requests/${id}/reject`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ comment: '' }),
      })
      fetchChanges()
    } catch (error) {
      console.error('Error rejecting:', error)
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-12">
        <div className="animate-spin w-8 h-8 border-2 border-amber-500 border-t-transparent rounded-full" />
      </div>
    )
  }

  const pendingChanges = changes.filter(
    c => c.status === 'proposed' || c.status === 'pending_approval'
  )
  const processedChanges = changes.filter(
    c => c.status === 'approved' || c.status === 'rejected' || c.status === 'applied'
  )

  const getStatusLabel = (status: string) => {
    const key = STATUS_LABEL_KEYS[status]
    return key ? t(key) : status
  }

  const getSeverityLabel = (severityValue: string) => {
    const key = SEVERITY_LABEL_KEYS[severityValue]
    return key ? t(key) : severityValue
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h1 className="heading-lg">{t('internal.changeRequests.title')}</h1>
          <p className="mt-1 text-slate-400">{t('internal.changeRequests.subtitle')}</p>
        </div>
        <Link to={`/projects/${projectId}/dashboard`} className="btn-secondary">
          {t('internal.changeRequests.backToDashboard')}
        </Link>
      </div>

      {pendingChanges.length > 0 && (
        <div className="space-y-4">
          <h2 className="heading-md">{t('internal.changeRequests.pendingApprovalTitle')}</h2>
          {pendingChanges.map(change => (
            <div key={change.id} className="card">
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <span className={`badge ${
                      change.severity === 'critical' ? 'badge-red' :
                      change.severity === 'high' ? 'badge-amber' :
                      'badge-blue'
                    }`}>
                      {getSeverityLabel(change.severity)}
                    </span>
                    <span className="text-sm text-slate-400">
                      {change.target_module}
                    </span>
                  </div>
                  <h3 className="font-medium mt-1">{change.title}</h3>
                  {change.summary && (
                    <p className="text-sm text-slate-400 mt-1">{change.summary}</p>
                  )}
                </div>
                <div className="flex gap-2">
                  <button onClick={() => approveChange(change.id)} className="btn-primary text-sm">
                    <Check className="w-4 h-4 mr-1" /> {t('internal.changeRequests.approve')}
                  </button>
                  <button onClick={() => rejectChange(change.id)} className="btn-secondary text-sm">
                    <X className="w-4 h-4 mr-1" /> {t('internal.changeRequests.reject')}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {processedChanges.length > 0 && (
        <div className="space-y-4">
          <h2 className="heading-md">{t('internal.changeRequests.historyTitle')}</h2>
          {processedChanges.map(change => (
            <div key={change.id} className="card">
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <span className={`badge ${
                      change.status === 'approved' ? 'badge-green' :
                      change.status === 'rejected' ? 'badge-red' :
                      'badge-blue'
                    }`}>
                      {getStatusLabel(change.status)}
                    </span>
                    <span className="text-sm text-slate-400">
                      {change.target_module}
                    </span>
                  </div>
                  <h3 className="font-medium mt-1">{change.title}</h3>
                </div>
                <span className="text-xs text-slate-500">
                  {change.created_at ? new Date(change.created_at).toLocaleDateString() : ''}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {changes.length === 0 && (
        <div className="card">
          <div className="text-center p-8">
            <FileText className="w-12 h-12 mx-auto mb-3 text-slate-500" />
            <p className="text-slate-400">{t('internal.changeRequests.empty')}</p>
          </div>
        </div>
      )}
    </div>
  )
}