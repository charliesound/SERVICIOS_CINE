import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../api/client'
import { Plus, ExternalLink } from 'lucide-react'
import type { Project } from '../types'

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([])
  const [showForm, setShowForm] = useState(false)
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')

  const load = () => api.get('/projects').then((r) => setProjects(r.data))

  useEffect(() => { load() }, [])

  const create = async (e: React.FormEvent) => {
    e.preventDefault()
    await api.post('/projects', { name, description })
    setName('')
    setDescription('')
    setShowForm(false)
    load()
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Proyectos</h1>
          <p className="text-cine-400 mt-1">Gestiona tus proyectos de doblaje</p>
        </div>
        <button onClick={() => setShowForm(!showForm)} className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" /> Nuevo proyecto
        </button>
      </div>

      {showForm && (
        <form onSubmit={create} className="card space-y-4">
          <div>
            <label className="label">Nombre</label>
            <input className="input" value={name} onChange={(e) => setName(e.target.value)} required />
          </div>
          <div>
            <label className="label">Descripción</label>
            <textarea className="input" rows={3} value={description} onChange={(e) => setDescription(e.target.value)} />
          </div>
          <div className="flex gap-2">
            <button type="submit" className="btn-primary">Crear</button>
            <button type="button" onClick={() => setShowForm(false)} className="btn-secondary">Cancelar</button>
          </div>
        </form>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {projects.map((p) => (
          <Link key={p.id} to={`/projects/${p.id}`} className="card hover:border-amber-500/30 transition-colors group">
            <div className="flex items-start justify-between">
              <h3 className="text-white font-semibold group-hover:text-amber-400 transition-colors">{p.name}</h3>
              <ExternalLink className="w-4 h-4 text-cine-400 group-hover:text-amber-400" />
            </div>
            {p.description && <p className="text-cine-400 text-sm mt-2 line-clamp-2">{p.description}</p>}
            <div className="flex items-center gap-2 mt-4">
              <span className="badge-blue">{p.status}</span>
              <span className="text-xs text-cine-400">{new Date(p.created_at).toLocaleDateString()}</span>
            </div>
          </Link>
        ))}
        {projects.length === 0 && !showForm && (
          <div className="card col-span-full text-center py-12">
            <p className="text-cine-400">No hay proyectos. Crea el primero.</p>
          </div>
        )}
      </div>
    </div>
  )
}
