import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import api from '../api/client'
import { AlertTriangle, CheckCircle, XCircle, Download } from 'lucide-react'
import type { DubbingJob, AuditLog } from '../types'

const statusLabels: Record<string, string> = {
  uploaded: 'Subido',
  pending_legal_check: 'Pendiente revisión legal',
  blocked_legal: 'Bloqueado legal',
  transcribing: 'Transcribiendo',
  translating: 'Traduciendo',
  generating_voice: 'Generando voz',
  lipsyncing: 'LipSync',
  mixing: 'Mezclando',
  awaiting_approval: 'Esperando aprobación',
  approved: 'Aprobado',
  rejected: 'Rechazado',
  exported: 'Exportado',
  failed: 'Error',
}

export default function DubbingJobDetailPage() {
  const { id } = useParams()
  const [job, setJob] = useState<DubbingJob | null>(null)
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([])
  const [comment, setComment] = useState('')

  useEffect(() => {
    api.get(`/dubbing-jobs/${id}`).then((r) => setJob(r.data))
    api.get(`/audit/job/${id}`).then((r) => setAuditLogs(r.data))
  }, [id])

  const approve = async () => {
    await api.post(`/dubbing-jobs/${id}/approve`, { decision: 'approved', comments: comment })
    api.get(`/dubbing-jobs/${id}`).then((r) => setJob(r.data))
    api.get(`/audit/job/${id}`).then((r) => setAuditLogs(r.data))
  }

  const reject = async () => {
    await api.post(`/dubbing-jobs/${id}/reject`, { decision: 'rejected', comments: comment })
    api.get(`/dubbing-jobs/${id}`).then((r) => setJob(r.data))
    api.get(`/audit/job/${id}`).then((r) => setAuditLogs(r.data))
  }

  if (!job) return <div className="text-cine-400">Cargando...</div>

  return (
    <div className="space-y-6 max-w-4xl">
      <Link to={`/projects/${job.project_id}`} className="text-cine-400 hover:text-white text-sm">&larr; Volver al proyecto</Link>

      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Job de doblaje #{job.id}</h1>
          <p className="text-cine-400 mt-1">{job.source_language} &rarr; {job.target_language}</p>
        </div>
        <span className={`badge-${job.status === 'blocked_legal' ? 'red' : job.status === 'approved' ? 'green' : job.status === 'failed' ? 'red' : 'blue'} text-sm`}>
          {statusLabels[job.status] || job.status}
        </span>
      </div>

      {job.legal_blocked && (
        <div className="bg-legal-red/10 border border-legal-red/20 rounded-xl p-4 flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-legal-red mt-0.5 shrink-0" />
          <div>
            <h3 className="font-semibold text-legal-red">Job bloqueado legalmente</h3>
            <p className="text-sm text-legal-red/80 mt-1">{job.legal_block_reason}</p>
          </div>
        </div>
      )}

      <div className="grid grid-cols-2 gap-4">
        <div className="card">
          <h3 className="text-sm font-medium text-cine-400 mb-3">Detalles</h3>
          <dl className="space-y-2 text-sm">
            <div className="flex justify-between"><span className="text-cine-400">Modo</span><span className="text-white">{job.mode}</span></div>
            <div className="flex justify-between"><span className="text-cine-400">Origen</span><span className="text-white">{job.source_language}</span></div>
            <div className="flex justify-between"><span className="text-cine-400">Destino</span><span className="text-white">{job.target_language}</span></div>
            <div className="flex justify-between"><span className="text-cine-400">Territorio</span><span className="text-white">{job.territory || '-'}</span></div>
            <div className="flex justify-between"><span className="text-cine-400">Uso</span><span className="text-white">{job.usage_type || '-'}</span></div>
            <div className="flex justify-between"><span className="text-cine-400">TTS</span><span className="text-white">{job.tts_provider_used || '-'}</span></div>
          </dl>
        </div>
        <div className="card">
          <h3 className="text-sm font-medium text-cine-400 mb-3">Timeline</h3>
          <div className="space-y-2">
            {auditLogs.slice(0, 8).map((log) => (
              <div key={log.id} className="flex items-start gap-2 text-xs">
                <span className="text-cine-500 mt-0.5">•</span>
                <div>
                  <span className="text-cine-300">{log.action}</span>
                  <span className="text-cine-500 ml-2">{new Date(log.created_at).toLocaleTimeString()}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {(job.status === 'awaiting_approval') && (
        <div className="card space-y-4">
          <h3 className="text-lg font-semibold text-white">Aprobación</h3>
          <textarea
            className="input"
            rows={3}
            placeholder="Comentarios sobre la revisión..."
            value={comment}
            onChange={(e) => setComment(e.target.value)}
          />
          <div className="flex gap-2">
            <button onClick={approve} className="btn-primary flex items-center gap-2">
              <CheckCircle className="w-4 h-4" /> Aprobar
            </button>
            <button onClick={reject} className="btn-danger flex items-center gap-2">
              <XCircle className="w-4 h-4" /> Rechazar
            </button>
          </div>
        </div>
      )}

      <div className="card">
        <h3 className="text-lg font-semibold text-white mb-4">Auditoría completa</h3>
        <div className="space-y-2 max-h-64 overflow-y-auto">
          {auditLogs.map((log) => (
            <div key={log.id} className="text-sm flex items-start gap-3 py-1.5 border-b border-cine-700/50 last:border-0">
              <span className="text-cine-500 text-xs font-mono shrink-0">{new Date(log.created_at).toLocaleString()}</span>
              <span className="text-cine-200">{log.action}</span>
              {log.details && <span className="text-cine-400 text-xs truncate">{log.details}</span>}
            </div>
          ))}
          {auditLogs.length === 0 && <p className="text-cine-400 text-sm">Sin registros de auditoría</p>}
        </div>
      </div>
    </div>
  )
}
