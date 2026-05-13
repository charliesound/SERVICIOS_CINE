import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import api from '../api/client'
import { Plus, Play, AlertTriangle, CheckCircle, Clock } from 'lucide-react'
import type { Project, DubbingJob, DubbingMode } from '../types'

const statusColors: Record<string, string> = {
  uploaded: 'badge-gray',
  pending_legal_check: 'badge-yellow',
  blocked_legal: 'badge-red',
  transcribing: 'badge-blue',
  translating: 'badge-blue',
  generating_voice: 'badge-blue',
  lipsyncing: 'badge-blue',
  mixing: 'badge-blue',
  awaiting_approval: 'badge-yellow',
  approved: 'badge-green',
  rejected: 'badge-red',
  exported: 'badge-green',
  failed: 'badge-red',
}

export default function ProjectDetailPage() {
  const { id } = useParams()
  const [project, setProject] = useState<Project | null>(null)
  const [jobs, setJobs] = useState<DubbingJob[]>([])
  const [showForm, setShowForm] = useState(false)
  const [mode, setMode] = useState<DubbingMode>('doblaje_humano_asistido')
  const [sourceLang, setSourceLang] = useState('es')
  const [targetLang, setTargetLang] = useState('en')

  useEffect(() => {
    api.get(`/projects/${id}`).then((r) => setProject(r.data))
    api.get(`/dubbing-jobs/project/${id}`).then((r) => setJobs(r.data))
  }, [id])

  const createJob = async (e: React.FormEvent) => {
    e.preventDefault()
    const res = await api.post(`/dubbing-jobs/project/${id}`, {
      mode,
      source_language: sourceLang,
      target_language: targetLang,
    })
    setShowForm(false)
    setJobs((prev) => [...prev, res.data])
  }

  const startJob = async (jobId: number) => {
    const res = await api.post(`/dubbing-jobs/${jobId}/start`)
    api.get(`/dubbing-jobs/project/${id}`).then((r) => setJobs(r.data))
  }

  return (
    <div className="space-y-6">
      <div>
        <Link to="/projects" className="text-cine-400 hover:text-white text-sm">&larr; Volver a proyectos</Link>
        <h1 className="text-2xl font-bold text-white mt-2">{project?.name || 'Cargando...'}</h1>
      </div>

      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-white">Trabajos de doblaje</h2>
        <button onClick={() => setShowForm(!showForm)} className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" /> Nuevo job
        </button>
      </div>

      {showForm && (
        <form onSubmit={createJob} className="card space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">Modo</label>
              <select className="input" value={mode} onChange={(e) => setMode(e.target.value as DubbingMode)}>
                <option value="doblaje_humano_asistido">Doblaje humano asistido</option>
                <option value="voz_original_ia_autorizada">Voz original IA autorizada</option>
              </select>
            </div>
            <div>
              <label className="label">Idioma origen</label>
              <select className="input" value={sourceLang} onChange={(e) => setSourceLang(e.target.value)}>
                <option value="es">Español</option>
                <option value="en">Inglés</option>
                <option value="fr">Francés</option>
                <option value="de">Alemán</option>
                <option value="it">Italiano</option>
                <option value="pt">Portugués</option>
              </select>
            </div>
            <div>
              <label className="label">Idioma destino</label>
              <select className="input" value={targetLang} onChange={(e) => setTargetLang(e.target.value)}>
                <option value="en">Inglés</option>
                <option value="es">Español</option>
                <option value="fr">Francés</option>
                <option value="de">Alemán</option>
                <option value="it">Italiano</option>
                <option value="pt">Portugués</option>
              </select>
            </div>
          </div>
          <div className="flex gap-2">
            <button type="submit" className="btn-primary">Crear job</button>
            <button type="button" onClick={() => setShowForm(false)} className="btn-secondary">Cancelar</button>
          </div>
        </form>
      )}

      <div className="space-y-3">
        {jobs.map((job) => (
          <div key={job.id} className={`card ${job.legal_blocked ? 'border-legal-red/50' : ''}`}>
            <div className="flex items-start justify-between">
              <div>
                <div className="flex items-center gap-2">
                  <span className={`${statusColors[job.status] || 'badge-gray'}`}>{job.status.replace(/_/g, ' ')}</span>
                  <span className="badge-blue">{job.mode === 'voz_original_ia_autorizada' ? 'IA' : 'Humano'}</span>
                </div>
                <p className="text-white font-medium mt-2">{job.source_language} &rarr; {job.target_language}</p>
                {job.legal_blocked && (
                  <div className="flex items-center gap-2 mt-2 text-legal-red text-sm">
                    <AlertTriangle className="w-4 h-4" />
                    <span>Bloqueado: {job.legal_block_reason}</span>
                  </div>
                )}
              </div>
              <div className="flex items-center gap-2">
                <Link to={`/dubbing-jobs/${job.id}`} className="btn-secondary text-sm">Ver</Link>
                {job.status === 'uploaded' && (
                  <button onClick={() => startJob(job.id)} className="btn-primary text-sm flex items-center gap-1">
                    <Play className="w-3 h-3" /> Iniciar
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
        {jobs.length === 0 && (
          <div className="card text-center py-12">
            <p className="text-cine-400">No hay trabajos de doblaje en este proyecto</p>
          </div>
        )}
      </div>
    </div>
  )
}
