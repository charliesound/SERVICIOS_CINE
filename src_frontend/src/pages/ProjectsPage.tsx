import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { projectsApi, type Project } from '@/api'
import { PlusCircle, FileText, ArrowRight } from 'lucide-react'

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    projectsApi.list().then((res) => {
      setProjects(res.projects)
      setIsLoading(false)
    }).catch(() => setIsLoading(false))
  }, [])

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold">Proyectos</h1>
          <p className="text-gray-400 text-sm mt-1">
            {projects.length} proyecto{projects.length !== 1 ? 's' : ''}
          </p>
        </div>
        <Link
          to="/projects/new"
          className="btn-primary flex items-center gap-2"
        >
          <PlusCircle className="w-4 h-4" />
          Nuevo proyecto
        </Link>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-20">
          <div className="flex items-center gap-3 text-amber-400">
            <svg className="animate-spin w-6 h-6" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
            <span className="text-sm">Cargando proyectos...</span>
          </div>
        </div>
      ) : projects.length === 0 ? (
        <div className="text-center py-20">
          <div className="w-16 h-16 rounded-2xl bg-amber-500/10 flex items-center justify-center mx-auto mb-4">
            <FileText className="w-8 h-8 text-amber-400" />
          </div>
          <h2 className="text-xl font-semibold mb-2">Sin proyectos</h2>
          <p className="text-gray-400 mb-6 max-w-md mx-auto">
            Crea tu primer proyecto y pega el guion para empezar a analizarlo con CID.
          </p>
          <Link to="/projects/new" className="btn-primary inline-flex items-center gap-2">
            <PlusCircle className="w-4 h-4" />
            Crear primer proyecto
          </Link>
        </div>
      ) : (
        <div className="space-y-3">
          {projects.map((project) => (
            <Link
              key={project.id}
              to={`/projects/${project.id}`}
              className="card bg-dark-200/80 border border-white/5 p-5 hover:border-amber-500/20 transition-colors flex items-center justify-between group"
            >
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-amber-500/10 flex items-center justify-center">
                  <FileText className="w-6 h-6 text-amber-400" />
                </div>
                <div>
                  <h3 className="font-semibold group-hover:text-amber-400 transition-colors">
                    {project.name}
                  </h3>
                  <div className="flex items-center gap-3 mt-1">
                    <span className="text-xs text-gray-500 capitalize">{project.status}</span>
                    {project.script_text && (
                      <span className="text-xs text-green-400">✓ Guion</span>
                    )}
                    {!project.script_text && (
                      <span className="text-xs text-gray-500">Sin guion</span>
                    )}
                  </div>
                </div>
              </div>
              <ArrowRight className="w-5 h-5 text-gray-600 group-hover:text-amber-400 transition-colors" />
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
