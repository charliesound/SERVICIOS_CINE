import { useEffect, useState } from 'react'
import api from '../api/client'
import { Search } from 'lucide-react'
import type { AuditLog } from '../types'

export default function AuditPage() {
  const [logs, setLogs] = useState<AuditLog[]>([])
  const [projectId, setProjectId] = useState('')
  const [jobId, setJobId] = useState('')

  const loadProjectLogs = async () => {
    if (!projectId) return
    const res = await api.get(`/audit/project/${projectId}`)
    setLogs(res.data)
  }

  const loadJobLogs = async () => {
    if (!jobId) return
    const res = await api.get(`/audit/job/${jobId}`)
    setLogs(res.data)
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Auditoría</h1>
        <p className="text-cine-400 mt-1">Trazabilidad legal completa del sistema</p>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="card">
          <label className="label">Filtrar por proyecto</label>
          <div className="flex gap-2">
            <input type="number" className="input" placeholder="ID del proyecto" value={projectId} onChange={(e) => setProjectId(e.target.value)} />
            <button onClick={loadProjectLogs} className="btn-primary"><Search className="w-4 h-4" /></button>
          </div>
        </div>
        <div className="card">
          <label className="label">Filtrar por job</label>
          <div className="flex gap-2">
            <input type="number" className="input" placeholder="ID del job" value={jobId} onChange={(e) => setJobId(e.target.value)} />
            <button onClick={loadJobLogs} className="btn-primary"><Search className="w-4 h-4" /></button>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="space-y-1 max-h-[60vh] overflow-y-auto">
          {logs.map((log) => (
            <div key={log.id} className="flex items-start gap-4 py-2.5 border-b border-cine-700/50 text-sm">
              <span className="text-cine-500 font-mono shrink-0 w-36">{new Date(log.created_at).toLocaleString()}</span>
              <span className="text-amber-400 font-medium shrink-0">{log.action}</span>
              <span className="text-cine-400">user:{log.user_id}</span>
              {log.entity_type && <span className="text-cine-400">{log.entity_type}:{log.entity_id}</span>}
              {log.details && <span className="text-cine-500 truncate">{log.details}</span>}
            </div>
          ))}
          {logs.length === 0 && (
            <p className="text-cine-400 text-center py-8">Selecciona un proyecto o job para ver su auditoría</p>
          )}
        </div>
      </div>
    </div>
  )
}
