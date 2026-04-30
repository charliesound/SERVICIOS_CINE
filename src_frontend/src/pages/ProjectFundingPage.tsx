import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import FundingOpportunitiesDashboard from '@/components/FundingOpportunitiesDashboard'
import ProjectFundingPanel from '@/components/ProjectFundingPanel'
import { ArrowLeft, Briefcase, WalletCards } from 'lucide-react'

export default function ProjectFundingPage() {
  const { projectId } = useParams<{ projectId: string }>()
  const [activeTab, setActiveTab] = useState<'opportunities' | 'private'>('opportunities')

  if (!projectId) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen">
        <p className="text-gray-400">Proyecto no encontrado</p>
        <Link to="/projects" className="mt-4 text-blue-400 hover:underline">
          Volver a proyectos
        </Link>
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
          <h1 className="text-2xl font-bold text-white">Financiación del proyecto</h1>
          <p className="text-gray-400">Consulta oportunidades enriquecidas y conserva la gestión de financiación privada</p>
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
