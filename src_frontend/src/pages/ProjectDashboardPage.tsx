import { useMemo } from 'react'
import { useParams, Link } from 'react-router-dom'
import { 
  FileText, Layers, DollarSign, TrendingUp, 
  Users, Building2, Film, FileSearch, 
  FolderOpen, Briefcase, ArrowRight, AlertTriangle
} from 'lucide-react'
import { useProjectDashboard } from '@/hooks'
import { StatusBadge } from '@/components/StatusBadge'
import DemoModePanel from '@/components/DemoModePanel'
import { t } from '@/i18n'

function getModuleIcon(moduleKey: string) {
  const icons: Record<string, React.ElementType> = {
    script: FileText,
    storyboard: Layers,
    breakdown: FileText,
    budget: DollarSign,
    funding: TrendingUp,
    producer_pack: Briefcase,
    distribution: Building2,
    crm: Users,
    media: Film,
    documents: FileSearch,
    editorial: FolderOpen,
  }
  return icons[moduleKey] || FileText
}

const MODULE_DISPLAY_NAMES: Record<string, string> = {
  script: t('internal.projectDashboard.modules.script'),
  storyboard: t('internal.projectDashboard.modules.storyboard'),
  breakdown: 'Desglose',
  budget: t('internal.projectDashboard.modules.budget'),
  funding: t('internal.projectDashboard.modules.funding'),
  producer_pack: 'Dossier para productores',
  distribution: t('internal.projectDashboard.modules.distribution'),
  crm: 'Seguimiento comercial',
  media: 'Media indexada',
  documents: 'Ingesta documental',
  editorial: t('internal.projectDashboard.modules.editorial'),
}

const DASHBOARD_PHASES = [
  {
    title: 'Desarrollo',
    description: t('internal.projectDashboard.groups.development.description'),
    keys: ['script', 'breakdown', 'storyboard'],
  },
  {
    title: t('internal.projectDashboard.groups.productionFunding.title'),
    description: t('internal.projectDashboard.groups.productionFunding.description'),
    keys: ['budget', 'funding'],
  },
  {
    title: 'Comercial',
    description: t('internal.projectDashboard.groups.commercial.description'),
    keys: ['producer_pack', 'distribution', 'crm'],
  },
  {
    title: t('internal.projectDashboard.groups.postproduction.title'),
    description: t('internal.projectDashboard.groups.postproduction.description'),
    keys: ['media', 'documents', 'editorial'],
  },
]

function getModuleRoute(key: string, projectId: string) {
  switch (key) {
    case 'script':
      return `/projects/${projectId}`
    case 'storyboard':
      return `/projects/${projectId}/storyboard-builder`
    case 'budget':
      return `/projects/${projectId}/budget`
    case 'funding':
      return `/projects/${projectId}/funding`
    case 'producer_pack':
      return `/projects/${projectId}/producer-pitch`
    case 'distribution':
      return `/projects/${projectId}/distribution`
    case 'crm':
      return `/projects/${projectId}/crm`
    case 'media':
      return `/ingest/scans`
    case 'documents':
      return `/projects/${projectId}/documents`
    case 'editorial':
      return `/projects/${projectId}/editorial`
    case 'breakdown':
      return `/projects/${projectId}`
    default:
      return `/projects/${projectId}`
  }
}

function normalizeStatus(status?: string) {
  if (!status) return 'missing'
  if (status === 'ready') return 'ready'
  if (status === 'partial') return 'partial'
  if (status === 'missing') return 'missing'
  if (status === 'warning') return 'warning'
  if (status === 'needs_review') return 'needs_review'
  if (status === 'approved') return 'approved'
  if (status === 'pending') return 'pending'
  if (status === 'locked') return 'locked'
  return 'missing'
}

export default function ProjectDashboardPage() {
  const { projectId = '' } = useParams()
  const dashboardQuery = useProjectDashboard(projectId)

  const modules = useMemo(() => {
    if (!dashboardQuery.data?.modules) return []
    return Object.entries(dashboardQuery.data.modules).map(([key, value]) => ({
      key,
      ...value,
    }))
  }, [dashboardQuery.data])

  const actions = useMemo(() => {
    return dashboardQuery.data?.recommended_next_actions || []
  }, [dashboardQuery.data])

  if (dashboardQuery.isLoading) {
    return (
      <div className="flex items-center justify-center p-12">
        <div className="animate-spin w-8 h-8 border-2 border-amber-500 border-t-transparent rounded-full" />
      </div>
    )
  }

  if (dashboardQuery.error) {
    return (
      <div className="card">
        <div className="text-red-400">{t('internal.projectDashboard.errorLoading')}</div>
        <Link to={`/projects/${projectId}`} className="btn-secondary mt-4">
          Volver al proyecto
        </Link>
      </div>
    )
  }

  const data = dashboardQuery.data

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="heading-lg">{data?.title || t('internal.common.project')}</h1>
            <span className="badge badge-amber">{data?.status || 'active'}</span>
          </div>
          <p className="mt-1 text-slate-400">
            Progreso general: {data?.overall_progress || 0}%
          </p>
        </div>
        <div className="flex gap-3">
          <Link to={`/projects/${projectId}`} className="btn-secondary">
            Ver proyecto
          </Link>
        </div>
      </div>

      {/* Global Progress Bar */}
      <div className="w-full bg-dark-300 rounded-xl h-3 overflow-hidden">
        <div 
          className="h-full bg-gradient-to-r from-amber-500 to-amber-400 transition-all duration-500"
          style={{ width: `${data?.overall_progress || 0}%` }}
        />
      </div>

      {/* Commercial Description */}
      <section className="space-y-4">
        <p className="text-slate-400 max-w-lg">
          {t('internal.projectDashboard.intro')}
        </p>
      </section>

      {/* Disclaimers */}
      <section className="space-y-2 text-xs text-slate-500">
        <p>{t('internal.projectDashboard.disclaimers.budget')}</p>
        <p>• Ayudas: “Verificar siempre con fuentes oficiales.”</p>
        <p>{t('internal.projectDashboard.disclaimers.distribution')}</p>
        <p>{t('internal.projectDashboard.disclaimers.crm')}</p>
        <p>{t('internal.projectDashboard.disclaimers.davinci')}</p>
      </section>

      {/* Demo Mode Panel */}
      <DemoModePanel projectId={projectId} />

      {/* Phases */}
      {DASHBOARD_PHASES.map((phase) => {
        const phaseModules = phase.keys
          .map((key) => modules.find((m) => m.key === key))
          .filter(Boolean)

        if (phaseModules.length === 0) return null

        return (
          <section key={phase.title} className="space-y-4">
            <h2 className="heading-md">{phase.title}</h2>
            <p className="text-slate-400">{phase.description}</p>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {phaseModules.map((module) => {
                if (!module) return null
                const Icon = getModuleIcon(module.key)
                const route = getModuleRoute(module.key, projectId)
                return (
                  <Link
                    key={module.key}
                    to={route}
                    className="card card-hover"
                  >
                    <div className="flex items-start gap-4">
                      <div className="p-3 rounded-xl bg-dark-300">
                        <Icon className="w-5 h-5 text-amber-400" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between gap-2">
                          <h3 className="font-semibold text-white capitalize">
                            {MODULE_DISPLAY_NAMES[module.key]}
                          </h3>
                          <StatusBadge status={normalizeStatus(module.status)} size="sm" />
                        </div>
                        <p className="mt-1 text-sm text-slate-400 truncate">
                          {module.summary}
                        </p>
                      </div>
                    </div>
                  </Link>
                )}
              )}
            </div>
          </section>
        )
      })}

      {/* Próximas acciones */}
      {actions.length > 0 && (
        <section className="space-y-4">
          <h2 className="heading-md">{t('internal.projectDashboard.nextActions')}</h2>
          <div className="space-y-2">
            {actions.map((action, i) => (
              <Link
                key={i}
                to={action.locked ? '#' : action.route}
                onClick={(e) => action.locked && e.preventDefault()}
                className={`flex items-center justify-between p-4 rounded-xl border transition-colors ${
                  action.locked 
                    ? 'border-gray-500/20 bg-gray-500/5 text-gray-500 cursor-not-allowed opacity-50'
                    : 'border-amber-500/20 bg-amber-500/5 hover:bg-amber-500/10 text-amber-200'
                }`}
              >
                <span>{action.label}</span>
                {action.locked ? (
                  <span className="text-xs px-2 py-1 rounded bg-gray-500/20">{t('internal.projectDashboard.noPermission')}</span>
                ) : (
                  <ArrowRight className="w-4 h-4" />
                )}
              </Link>
            ))}
          </div>
        </section>
      )}

      {/* Warnings */}
      {data?.warnings && data.warnings.length > 0 && (
        <section className="space-y-4">
          <h2 className="heading-md flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-amber-400" />
            Warnings
          </h2>
          <div className="space-y-2">
            {data.warnings.map((warning: string, i: number) => (
              <div key={i} className="p-4 rounded-xl border border-amber-500/20 bg-amber-500/5 text-amber-200">
                {warning}
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  )
}
