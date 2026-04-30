import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { projectsApi, type Project } from '@/api'
import { useAuthStore } from '@/store'
import { useJobs } from '@/hooks'
import { useUserPlanStatus } from '@/hooks/usePlans'
import QueueStatusPanel from '@/components/QueueStatusPanel'
import { DEMO_PROJECTS } from '@/data/demo'
import { ArrowRight, Clock, CheckCircle, FolderOpen, Zap } from 'lucide-react'

export default function Dashboard() {
  const { user } = useAuthStore()
  const { data: jobs } = useJobs({ user_id: user?.user_id })
  const { data: planStatus } = useUserPlanStatus(user?.user_id || '', user?.plan || 'free')
  const [projects, setProjects] = useState<Project[]>([])

  useEffect(() => {
    projectsApi.list()
      .then((res) => setProjects(res.projects))
      .catch(() => setProjects([]))
  }, [])

  const recentJobs = jobs?.slice(0, 5) || []
  const demoFallback = DEMO_PROJECTS.slice(0, 3)
  const activeProjects = projects.filter((project) => ['active', 'desarrollo', 'preproduccion', 'produccion', 'postproduccion'].includes(project.status))
  const deliveredProjects = projects.filter((project) => project.status === 'entregado' || project.status === 'completed')
  const portfolioBudget = DEMO_PROJECTS.reduce((sum, project) => sum + (project.budget || 0), 0)
  const recentProjects = projects.slice(0, 3)

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="heading-xl">Dashboard</h1>
          <p className="text-slate-400 mt-1">Vista general de tus proyectos y del estado base del pipeline</p>
        </div>
        <Link to="/create" className="btn-primary flex items-center gap-2">
          <FolderOpen className="w-4 h-4" />
          Crear proyecto
        </Link>
      </div>

      {/* Stats Grid - foundation */}
      <div className="grid grid-cols-4 gap-4">
        <div className="stat-card group">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-amber-500/10 flex items-center justify-center">
              <FolderOpen className="w-5 h-5 text-amber-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{projects.length}</p>
               <p className="text-sm text-slate-400">Proyectos reales</p>
            </div>
          </div>
        </div>

        <div className="stat-card group">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-slate-700/30 flex items-center justify-center">
              <Clock className="w-5 h-5 text-slate-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{activeProjects.length}</p>
              <p className="text-sm text-slate-400">Activos</p>
            </div>
          </div>
        </div>

        <div className="stat-card group">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-green-500/10 flex items-center justify-center">
              <CheckCircle className="w-5 h-5 text-green-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{deliveredProjects.length}</p>
              <p className="text-sm text-slate-400">Entregados</p>
            </div>
          </div>
        </div>

        <div className="stat-card group">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-blue-500/10 flex items-center justify-center">
              <Zap className="w-5 h-5 text-blue-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{portfolioBudget.toLocaleString()}€</p>
              <p className="text-sm text-slate-400">Presupuesto</p>
            </div>
          </div>
        </div>
      </div>

      {planStatus && (
        <div className="card bg-gradient-to-r from-amber-500/5 to-transparent border-amber-500/20">
          <div className="flex items-start justify-between gap-6">
            <div>
              <p className="text-sm text-slate-400 mb-1">Plan y uso</p>
              <h2 className="text-xl font-semibold text-white capitalize">{planStatus.plan}</h2>
              <div className="mt-3 grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                <div className="rounded-xl bg-dark-300/50 p-3">
                  <p className="text-slate-500">Proyectos</p>
                  <p className="text-white font-semibold">
                    {planStatus.projects_count}/{planStatus.max_projects === -1 ? '∞' : planStatus.max_projects}
                  </p>
                </div>
                <div className="rounded-xl bg-dark-300/50 p-3">
                  <p className="text-slate-500">Jobs</p>
                  <p className="text-white font-semibold">
                    {planStatus.jobs_count}/{planStatus.max_total_jobs === -1 ? '∞' : planStatus.max_total_jobs}
                  </p>
                </div>
                <div className="rounded-xl bg-dark-300/50 p-3">
                  <p className="text-slate-500">Analisis</p>
                  <p className="text-white font-semibold">
                    {planStatus.analyses_count}/{planStatus.max_analyses === -1 ? '∞' : planStatus.max_analyses}
                  </p>
                </div>
                <div className="rounded-xl bg-dark-300/50 p-3">
                  <p className="text-slate-500">Storyboards</p>
                  <p className="text-white font-semibold">
                    {planStatus.storyboards_count}/{planStatus.max_storyboards === -1 ? '∞' : planStatus.max_storyboards}
                  </p>
                </div>
              </div>
            </div>

            <div className="text-right min-w-[180px]">
              <p className="text-xs uppercase tracking-wider text-slate-500 mb-2">Export</p>
              <p className={`text-sm font-medium ${planStatus.export_json ? 'text-green-400' : 'text-amber-400'}`}>
                {planStatus.export_json ? 'JSON incluido' : 'Upgrade requerido'}
              </p>
              <p className={`mt-1 text-xs font-medium ${planStatus.export_zip ? 'text-green-400' : 'text-slate-500'}`}>
                {planStatus.export_zip ? 'ZIP comercial incluido' : 'ZIP disponible desde planes con export'}
              </p>
              <Link to="/plans" className="btn-secondary mt-4 inline-flex items-center gap-2 text-sm">
                Ver planes <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </div>
        </div>
      )}

      {/* Projects foundation */}
      <div className="card card-hover">
        <div className="flex items-center justify-between mb-4">
          <h2 className="heading-md">Proyectos Recientes</h2>
          <Link to="/history" className="btn-ghost flex items-center gap-1 text-sm">
            Ver historial <ArrowRight className="w-4 h-4" />
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {(recentProjects.length > 0 ? recentProjects : demoFallback).map((project) => (
            <article key={project.id} className="rounded-2xl border border-white/10 bg-dark-300/60 p-5">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h3 className="text-lg font-semibold text-white">{project.name}</h3>
                  <p className="mt-1 text-sm text-slate-400">{project.description}</p>
                </div>
                <span className="rounded-full bg-amber-500/10 px-3 py-1 text-xs font-medium capitalize text-amber-400">
                  {project.status}
                </span>
              </div>

              {'type' in project && 'genre' in project && 'duration_minutes' in project && 'budget' in project && (
                <>
                  <div className="mt-4 flex flex-wrap gap-2 text-xs text-slate-400">
                    <span className="rounded-full bg-white/5 px-2.5 py-1">{project.type}</span>
                    <span className="rounded-full bg-white/5 px-2.5 py-1">{project.genre}</span>
                    <span className="rounded-full bg-white/5 px-2.5 py-1">{project.duration_minutes} min</span>
                  </div>

                  <p className="mt-4 text-sm font-medium text-white">
                    Presupuesto: {project.budget.toLocaleString()}EUR
                  </p>
                </>
              )}
            </article>
          ))}
        </div>
      </div>

      {/* Queue Panel */}
      <div className="card card-hover">
        <div className="flex items-center justify-between mb-4">
          <h2 className="heading-md">Queue Status</h2>
          <Link to="/queue" className="btn-ghost flex items-center gap-1 text-sm">
            View all <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
        <QueueStatusPanel />
      </div>

      {/* Recent Jobs */}
      {recentJobs.length > 0 && (
        <div className="card card-hover">
          <div className="flex items-center justify-between mb-4">
            <h2 className="heading-md">Recent Projects</h2>
            <Link to="/queue" className="btn-ghost flex items-center gap-1 text-sm">
              View all <ArrowRight className="w-4 h-4" />
            </Link>
          </div>

          <div className="space-y-2">
            {recentJobs.map((job) => (
              <div 
                key={job.job_id} 
                className="flex items-center justify-between p-4 bg-dark-300/50 rounded-xl hover:bg-dark-300 transition-colors"
              >
                <div className="flex items-center gap-4">
                  <div className="w-8 h-8 rounded-lg bg-amber-500/10 flex items-center justify-center">
                    <span className="text-amber-400 text-xs font-bold">
                      {job.task_type.charAt(0).toUpperCase()}
                    </span>
                  </div>
                  <div>
                    <p className="font-mono text-sm text-slate-300">{job.job_id}</p>
                    <p className="text-xs text-slate-500 capitalize">{job.task_type}</p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                    job.status === 'succeeded' ? 'bg-green-500/10 text-green-400' :
                    job.status === 'failed' ? 'bg-red-500/10 text-red-400' :
                    job.status === 'running' ? 'bg-blue-500/10 text-blue-400' :
                    'bg-amber-500/10 text-amber-400'
                  }`}>
                    {job.status}
                  </span>
                  <span className="text-xs text-slate-500">
                    {new Date(job.created_at).toLocaleTimeString()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
