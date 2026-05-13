import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../api/client'
import { useAuthStore } from '../stores/authStore'
import { FolderOpen, FileText, Mic, AlertTriangle, CheckCircle } from 'lucide-react'
import type { Project, VoiceContract, DubbingJob } from '../types'

export default function DashboardPage() {
  const user = useAuthStore((s) => s.user)
  const [projects, setProjects] = useState<Project[]>([])
  const [contracts, setContracts] = useState<VoiceContract[]>([])

  useEffect(() => {
    api.get('/projects').then((r) => setProjects(r.data)).catch(() => {})
    api.get('/contracts').then((r) => setContracts(r.data)).catch(() => {})
  }, [])

  const activeContracts = contracts.filter((c) => c.is_active)
  const expiringSoon = contracts.filter((c) => {
    if (!c.is_active) return false
    const daysLeft = (new Date(c.expiry_date).getTime() - Date.now()) / (1000 * 60 * 60 * 24)
    return daysLeft > 0 && daysLeft < 30
  })

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white">Dashboard</h1>
        <p className="text-cine-400 mt-1">Bienvenido, {user?.name}</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card">
          <FolderOpen className="w-8 h-8 text-amber-500 mb-3" />
          <p className="text-2xl font-bold text-white">{projects.length}</p>
          <p className="text-cine-400 text-sm">Proyectos</p>
        </div>
        <div className="card">
          <FileText className="w-8 h-8 text-blue-400 mb-3" />
          <p className="text-2xl font-bold text-white">{activeContracts.length}</p>
          <p className="text-cine-400 text-sm">Contratos activos</p>
        </div>
        <div className="card">
          <AlertTriangle className="w-8 h-8 text-yellow-400 mb-3" />
          <p className="text-2xl font-bold text-white">{expiringSoon.length}</p>
          <p className="text-cine-400 text-sm">Por expirar (&lt;30d)</p>
        </div>
        <div className="card">
          <CheckCircle className="w-8 h-8 text-green-400 mb-3" />
          <p className="text-2xl font-bold text-white">{user?.role}</p>
          <p className="text-cine-400 text-sm">Tu rol</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-lg font-semibold text-white mb-4">Proyectos recientes</h2>
          {projects.length === 0 ? (
            <p className="text-cine-400 text-sm">No hay proyectos aún</p>
          ) : (
            <div className="space-y-2">
              {projects.slice(0, 5).map((p) => (
                <Link key={p.id} to={`/projects/${p.id}`} className="block p-3 rounded-lg bg-cine-700/50 hover:bg-cine-700 transition-colors">
                  <p className="text-white font-medium">{p.name}</p>
                  <p className="text-cine-400 text-xs">{p.status}</p>
                </Link>
              ))}
            </div>
          )}
          <Link to="/projects" className="btn-secondary mt-4 inline-block text-sm">Ver todos</Link>
        </div>

        <div className="card">
          <h2 className="text-lg font-semibold text-white mb-4">Alertas legales</h2>
          {expiringSoon.length === 0 ? (
            <p className="text-cine-400 text-sm">Sin alertas</p>
          ) : (
            <div className="space-y-2">
              {expiringSoon.map((c) => (
                <div key={c.id} className="p-3 rounded-lg bg-yellow-500/5 border border-yellow-500/20">
                  <p className="text-white font-medium">{c.contract_ref}</p>
                  <p className="text-yellow-400 text-xs">Expira: {new Date(c.expiry_date).toLocaleDateString()}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
