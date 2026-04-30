import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { crmApi, CRMOpportunity, CRMTask, CRMSummary } from '../api/crm'

const OPPORTUNITY_STATUS = [
  { value: 'new', label: 'Nueva' },
  { value: 'prepared', label: 'Preparada' },
  { value: 'contacted', label: 'Contactada' },
  { value: 'follow_up', label: 'Seguimiento' },
  { value: 'interested', label: 'Interesada' },
  { value: 'meeting_scheduled', label: 'Reunión' },
  { value: 'negotiating', label: 'Negociando' },
  { value: 'accepted', label: 'Aceptada' },
  { value: 'rejected', label: 'Rechazada' },
  { value: 'closed', label: 'Cerrada' },
]

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
        <div className="text-gray-500">Cargando...</div>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">CRM Comercial</h1>
        <p className="text-gray-600">Seguimiento de oportunidades comerciales</p>
      </div>

      <div className="mb-4 p-3 bg-yellow-50 text-yellow-800 rounded text-sm">
        <em>Registro manual de oportunidades. No envía correos automáticamente.</em>
      </div>

      <div className="mb-6 grid grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded shadow">
          <div className="text-2xl font-bold">{summary?.total_opportunities || 0}</div>
          <div className="text-sm text-gray-500">Oportunidades</div>
        </div>
        <div className="bg-white p-4 rounded shadow">
          <div className="text-2xl font-bold text-green-600">{summary?.interested_count || 0}</div>
          <div className="text-sm text-gray-500">Interesadas</div>
        </div>
        <div className="bg-white p-4 rounded shadow">
          <div className="text-2xl font-bold text-yellow-600">{summary?.pending_count || 0}</div>
          <div className="text-sm text-gray-500">Pendientes</div>
        </div>
        <div className="bg-white p-4 rounded shadow">
          <div className="text-2xl font-bold">{summary?.total_tasks || 0}</div>
          <div className="text-sm text-gray-500">Tareas</div>
        </div>
      </div>

      <div className="mb-4 flex border-b">
        <button
          onClick={() => setActiveTab('opportunities')}
          className={`px-4 py-2 ${activeTab === 'opportunities' ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-500'}`}
        >
          Oportunidades
        </button>
        <button
          onClick={() => setActiveTab('tasks')}
          className={`px-4 py-2 ${activeTab === 'tasks' ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-500'}`}
        >
          Tareas
        </button>
      </div>

      {activeTab === 'opportunities' && (
        <div className="overflow-x-auto">
          <table className="min-w-full bg-white border">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">Tipo</th>
                <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">Estado</th>
                <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">Prioridad</th>
                <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">Fit</th>
                <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">Próxima acción</th>
                <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {opportunities.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-gray-500">
                    No hay oportunidades comerciales.
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
                          <option key={s.value} value={s.value}>{s.label}</option>
                        ))}
                      </select>
                    </td>
                    <td className="px-4 py-2 text-sm">
                      <span className={`px-2 py-1 rounded text-sm ${
                        opp.priority === 'high' ? 'bg-red-100 text-red-800' :
                        opp.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {opp.priority}
                      </span>
                    </td>
                    <td className="px-4 py-2 text-sm">{opp.fit_score}%</td>
                    <td className="px-4 py-2 text-sm">{opp.next_action || '-'}</td>
                    <td className="px-4 py-2 text-sm">
                      <button className="text-blue-600 hover:underline">Ver</button>
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
                <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">Título</th>
                <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">Prioridad</th>
                <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">Fecha límite</th>
                <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">Estado</th>
                <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {tasks.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-4 py-8 text-center text-gray-500">
                    No hay tareas pendientes.
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
                        {task.priority}
                      </span>
                    </td>
                    <td className="px-4 py-2 text-sm">{task.due_date || '-'}</td>
                    <td className="px-4 py-2 text-sm capitalize">{task.status}</td>
                    <td className="px-4 py-2 text-sm">
                      {task.status === 'pending' && (
                        <button
                          onClick={() => handleCompleteTask(task.id)}
                          className="text-green-600 hover:underline"
                        >
                          Completar
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