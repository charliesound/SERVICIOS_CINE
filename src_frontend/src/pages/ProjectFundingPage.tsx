import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { AlertCircle, ArrowLeft, Briefcase, Loader2, WalletCards } from 'lucide-react'
import FundingOpportunitiesDashboard from '@/components/FundingOpportunitiesDashboard'
import ProjectFundingPanel from '@/components/ProjectFundingPanel'
import { projectsApi } from '@/api'
import { t } from '@/i18n'

export default function ProjectFundingPage() {
  const { projectId } = useParams<{ projectId: string }>()
  const [activeTab, setActiveTab] = useState<'opportunities' | 'private'>('opportunities')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!projectId) return
    setLoading(true)
    setError(null)
    projectsApi.get(projectId)
      .then(() => setLoading(false))
      .catch(() => {
        setError(t('internal.projectFundingPage.errors.loadProject'))
        setLoading(false)
      })
  }, [projectId])

  if (!projectId) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen">
        <p className="text-gray-400">{t('internal.projectFundingPage.projectNotFound')}</p>
        <Link to="/projects" className="mt-4 text-blue-400 hover:underline">
          Volver a proyectos
        </Link>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-amber-400" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-900">
        <div className="max-w-lg mx-auto pt-24 text-center">
          <AlertCircle className="w-12 h-12 mx-auto mb-4 text-red-400" />
          <h2 className="text-xl font-semibold text-white mb-2">{t('internal.projectFundingPage.errorTitle')}</h2>
          <p className="text-slate-400 mb-6">{error}</p>
          <div className="flex justify-center gap-3">
            <button onClick={() => { setError(null); setLoading(true); projectsApi.get(projectId!).then(() => setLoading(false)).catch(() => { setError(t('internal.projectFundingPage.errors.loadProject')); setLoading(false) }) }} className="btn-primary">
              Reintentar
            </button>
            <Link to="/projects" className="btn-secondary">
              Volver a proyectos
            </Link>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-900">
      <div className="max-w-6xl mx-auto p-6">
        <div className="mb-6">
          <Link
            to={`/projects/${projectId}`}
            className="inline-flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Volver al proyecto
          </Link>
        </div>

        <div className="mb-6">
          <h1 className="text-2xl font-bold text-white">{t('internal.projectFundingPage.title')}</h1>
          <p className="text-gray-400">{t('internal.projectFundingPage.subtitle')}</p>
        </div>

        <div className="mb-6 inline-flex rounded-2xl border border-white/10 bg-white/5 p-1">
          <button
            type="button"
            onClick={() => setActiveTab('opportunities')}
            className={`inline-flex items-center gap-2 rounded-xl px-4 py-2 text-sm transition ${
              activeTab === 'opportunities' ? 'bg-amber-400/15 text-amber-100' : 'text-gray-400 hover:text-white'
            }`}
          >
            <Briefcase className="h-4 w-4" />
            Oportunidades
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('private')}
            className={`inline-flex items-center gap-2 rounded-xl px-4 py-2 text-sm transition ${
              activeTab === 'private' ? 'bg-amber-400/15 text-amber-100' : 'text-gray-400 hover:text-white'
            }`}
          >
            <WalletCards className="h-4 w-4" />
            Fuentes privadas
          </button>
        </div>

        {activeTab === 'opportunities' ? (
          <FundingOpportunitiesDashboard projectId={projectId} />
        ) : (
          <ProjectFundingPanel projectId={projectId} />
        )}
      </div>
    </div>
  )
}
