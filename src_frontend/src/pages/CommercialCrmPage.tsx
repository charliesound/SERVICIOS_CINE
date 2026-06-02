import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { t } from '@/i18n'
import { crmApi, CRMOpportunity, CRMTask, CRMSummary } from '../api/crm'

const OPPORTUNITY_STATUS = [
  { value: 'new', labelKey: 'internal.commercialCrmPage.status.new' },
  { value: 'prepared', labelKey: 'internal.commercialCrmPage.status.prepared' },
  { value: 'contacted', labelKey: 'internal.commercialCrmPage.status.contacted' },
  { value: 'follow_up', labelKey: 'internal.commercialCrmPage.status.followUp' },
  { value: 'interested', labelKey: 'internal.commercialCrmPage.status.interested' },
  { value: 'meeting_scheduled', labelKey: 'internal.commercialCrmPage.status.meetingScheduled' },
  { value: 'negotiating', labelKey: 'internal.commercialCrmPage.status.negotiating' },
  { value: 'accepted', labelKey: 'internal.commercialCrmPage.status.accepted' },
  { value: 'rejected', labelKey: 'internal.commercialCrmPage.status.rejected' },
  { value: 'closed', labelKey: 'internal.commercialCrmPage.status.closed' },
]

const PRIORITY_KEYS: Record<string, string> = {
  high: 'internal.commercialCrmPage.priority.high',
  medium: 'internal.commercialCrmPage.priority.medium',
  low: 'internal.commercialCrmPage.priority.low',
}

const TASK_STATUS_KEYS: Record<string, string> = {
  pending: 'internal.commercialCrmPage.taskStatus.pending',
  completed: 'internal.commercialCrmPage.taskStatus.completed',
}

function getPriorityLabel(priority: string) {
  return t(PRIORITY_KEYS[priority] || 'internal.commercialCrmPage.priority.unknown')
}

function getTaskStatusLabel(status: string) {
  return t(TASK_STATUS_KEYS[status] || 'internal.commercialCrmPage.taskStatus.unknown')
}

export default function CommercialCrmPage() {
  const { projectId } = useParams<{ projectId: string }>()
  const [summary, setSummary] = useState<CRMSummary | null>(null)
  const [opportunities, setOpportunities] = useState<CRMOpportunity[]>([])
  const [tasks, setTasks] = useState<CRMTask[]>([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('opportunities')

  useEffect(() => {
    loadData()
  }, [projectId])

  const loadData = async () => {
    if (!projectId) return
    try {
      const [summaryData, oppsData, tasksData] = await Promise.all([
        crmApi.getCrmSummary(projectId),
        crmApi.listOpportunities(projectId),
        crmApi.listTasks(projectId),
      ])
      setSummary(summaryData)
      setOpportunities(oppsData.opportunities || [])
      setTasks(tasksData.tasks || [])
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  const handleStatusChange = async (oppId: string, newStatus: string) => {
    if (!projectId) return
    try {
      await crmApi.updateOpportunityStatus(projectId, oppId, newStatus)
      loadData()
    } catch (e) {
      console.error(e)
    }
  }

  const handleCompleteTask = async (taskId: string) => {
    if (!projectId) return
    try {
      await crmApi.completeTask(projectId, taskId)
      loadData()
    } catch (e) {
      console.error(e)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">{t('internal.commercialCrmPage.loading')}</div>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">{t('internal.commercialCrmPage.title')}</h1>
        <p className="text-gray-600">{t('internal.commercialCrmPage.subtitle')}</p>
      </div>

      <div className="mb-4 p-3 bg-yellow-50 text-yellow-800 rounded text-sm">
        <em>{t('internal.commercialCrmPage.manualNotice')}</em>
      </div>

      <div className="mb-6 grid grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded shadow">
          <div className="text-2xl font-bold">{summary?.total_opportunities || 0}</div>
          <div className="text-sm text-gray-500">{t('internal.commercialCrmPage.stats.opportunities')}</div>
        </div>
        <div className="bg-white p-4 rounded shadow">
          <div className="text-2xl font-bold text-green-600">{summary?.interested_count || 0}</div>
          <div className="text-sm text-gray-500">{t('internal.commercialCrmPage.stats.interested')}</div>
        </div>
        <div className="bg-white p-4 rounded shadow">
          <div className="text-2xl font-bold text-yellow-600">{summary?.pending_count || 0}</div>
          <div className="text-sm text-gray-500">{t('internal.commercialCrmPage.stats.pending')}</div>
        </div>
        <div className="bg-white p-4 rounded shadow">
          <div className="text-2xl font-bold">{summary?.total_tasks || 0}</div>
          <div className="text-sm text-gray-500">{t('internal.commercialCrmPage.stats.tasks')}</div>
        </div>
      </div>

      <div className="mb-4 flex border-b">
        <button
          onClick={() => setActiveTab('opportunities')}
          className={`px-4 py-2 ${activeTab === 'opportunities' ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-500'}`}
        >
          {t('internal.commercialCrmPage.tabs.opportunities')}
        </button>
        <button
          onClick={() => setActiveTab('tasks')}
          className={`px-4 py-2 ${activeTab === 'tasks' ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-500'}`}
        >
          {t('internal.commercialCrmPage.tabs.tasks')}
        </button>
      </div>

      {activeTab === 'opportunities' && (
        <div className="overflow-x-auto">
          <table className="min-w-full bg-white border">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">{t('internal.commercialCrmPage.headers.type')}</th>
                <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">{t('internal.commercialCrmPage.headers.status')}</th>
                <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">{t('internal.commercialCrmPage.headers.priority')}</th>
                <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">{t('internal.commercialCrmPage.headers.fit')}</th>
                <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">{t('internal.commercialCrmPage.headers.nextAction')}</th>
                <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">{t('internal.commercialCrmPage.headers.actions')}</th>
              </tr>
            </thead>
            <tbody>
              {opportunities.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-gray-500">
                    {t('internal.commercialCrmPage.empty.opportunities')}
                  </td>
                </tr>
              ) : (
                opportunities.map((opp) => (
                  <tr key={opp.id} className="border-t">
                    <td className="px-4 py-2 text-sm">{opp.opportunity_type}</td>
                    <td className="px-4 py-2 text-sm">
                      <select
                        value={opp.status}
                        onChange={(e) => handleStatusChange(opp.id, e.target.value)}
                        className="border rounded px-2 py-1 text-sm"
                      >
                        {OPPORTUNITY_STATUS.map((s) => (
                          <option key={s.value} value={s.value}>{t(s.labelKey)}</option>
                        ))}
                      </select>
                    </td>
                    <td className="px-4 py-2 text-sm">
                      <span className={`px-2 py-1 rounded text-sm ${
                        opp.priority === 'high' ? 'bg-red-100 text-red-800' :
                        opp.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {getPriorityLabel(opp.priority)}
                      </span>
                    </td>
                    <td className="px-4 py-2 text-sm">{opp.fit_score}%</td>
                    <td className="px-4 py-2 text-sm">{opp.next_action || '-'}</td>
                    <td className="px-4 py-2 text-sm">
                      <button className="text-blue-600 hover:underline">{t('internal.commercialCrmPage.actions.view')}</button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}

      {activeTab === 'tasks' && (
        <div className="overflow-x-auto">
          <table className="min-w-full bg-white border">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">{t('internal.commercialCrmPage.headers.title')}</th>
                <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">{t('internal.commercialCrmPage.headers.priority')}</th>
                <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">{t('internal.commercialCrmPage.headers.dueDate')}</th>
                <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">{t('internal.commercialCrmPage.headers.status')}</th>
                <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">{t('internal.commercialCrmPage.headers.actions')}</th>
              </tr>
            </thead>
            <tbody>
              {tasks.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-4 py-8 text-center text-gray-500">
                    {t('internal.commercialCrmPage.empty.tasks')}
                  </td>
                </tr>
              ) : (
                tasks.map((task) => (
                  <tr key={task.id} className="border-t">
                    <td className="px-4 py-2 text-sm">{task.title}</td>
                    <td className="px-4 py-2 text-sm">
                      <span className={`px-2 py-1 rounded text-sm ${
                        task.priority === 'high' ? 'bg-red-100 text-red-800' :
                        task.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {getPriorityLabel(task.priority)}
                      </span>
                    </td>
                    <td className="px-4 py-2 text-sm">{task.due_date || '-'}</td>
                    <td className="px-4 py-2 text-sm">{getTaskStatusLabel(task.status)}</td>
                    <td className="px-4 py-2 text-sm">
                      {task.status === 'pending' && (
                        <button
                          onClick={() => handleCompleteTask(task.id)}
                          className="text-green-600 hover:underline"
                        >
                          {t('internal.commercialCrmPage.actions.complete')}
                        </button>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
