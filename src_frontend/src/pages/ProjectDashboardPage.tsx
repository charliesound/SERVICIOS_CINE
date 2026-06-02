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
  breakdown: t('internal.projectDashboard.producer.modules.breakdown'),
  budget: t('internal.projectDashboard.modules.budget'),
  funding: t('internal.projectDashboard.modules.funding'),
  producer_pack: t('internal.projectDashboard.producer.modules.producerPack'),
  distribution: t('internal.projectDashboard.modules.distribution'),
  crm: t('internal.projectDashboard.producer.modules.crm'),
  media: t('internal.projectDashboard.producer.modules.media'),
  documents: t('internal.projectDashboard.producer.modules.documents'),
  editorial: t('internal.projectDashboard.modules.editorial'),
}

const DASHBOARD_PHASES = [
  {
    title: t('internal.projectDashboard.producer.groups.priority.title'),
    description: t('internal.projectDashboard.producer.groups.priority.description'),
    keys: ['budget', 'funding', 'producer_pack'],
    emphasis: 'primary',
  },
  {
    title: t('internal.projectDashboard.producer.groups.development.title'),
    description: t('internal.projectDashboard.producer.groups.development.description'),
    keys: ['script', 'breakdown', 'storyboard'],
    emphasis: 'secondary',
  },
  {
    title: t('internal.projectDashboard.producer.groups.commercial.title'),
    description: t('internal.projectDashboard.producer.groups.commercial.description'),
    keys: ['distribution', 'crm'],
    emphasis: 'secondary',
  },
  {
    title: t('internal.projectDashboard.producer.groups.operational.title'),
    description: t('internal.projectDashboard.producer.groups.operational.description'),
    keys: ['media', 'documents', 'editorial'],
    emphasis: 'secondary',
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

  const quickActions = useMemo(() => ([
    {
      key: 'budget',
      label: t('internal.projectDashboard.producer.quickActions.budget'),
      route: getModuleRoute('budget', projectId),
      icon: DollarSign,
    },
    {
      key: 'funding',
      label: t('internal.projectDashboard.producer.quickActions.funding'),
      route: getModuleRoute('funding', projectId),
      icon: TrendingUp,
    },
    {
      key: 'producerPack',
      label: t('internal.projectDashboard.producer.quickActions.producerPack'),
      route: getModuleRoute('producer_pack', projectId),
      icon: Briefcase,
    },
  ]), [projectId])

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
      <section className="relative overflow-hidden rounded-[2rem] border border-white/8 bg-dark-200/70 px-8 py-8 shadow-[0_28px_80px_rgba(2,6,23,0.32)]">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(245,158,11,0.16),transparent_28%),radial-gradient(circle_at_82%_16%,rgba(56,189,248,0.08),transparent_22%)]" />
        <div className="relative space-y-8">
          <div className="flex flex-col gap-6 xl:flex-row xl:items-end xl:justify-between">
            <div className="max-w-4xl">
              <p className="inline-flex items-center rounded-full border border-amber-400/20 bg-amber-400/10 px-4 py-2 text-[11px] font-semibold uppercase tracking-[0.24em] text-amber-100">
                {t('internal.projectDashboard.producer.heroEyebrow')}
              </p>
              <div className="mt-5 flex flex-wrap items-center gap-3">
                <h1 className="text-4xl font-semibold tracking-tight text-white md:text-5xl">
                  {data?.title || t('internal.common.project')}
                </h1>
                <span className="badge badge-amber">{data?.status || 'active'}</span>
              </div>
              <p className="mt-4 max-w-3xl text-lg leading-8 text-slate-300">
                {t('internal.projectDashboard.producer.heroSubtitle')}
              </p>
            </div>

            <div className="flex flex-wrap gap-3">
              <Link to={`/projects/${projectId}`} className="btn-secondary">
                {t('internal.projectDashboard.producer.viewProject')}
              </Link>
            </div>
          </div>

          <div className="grid gap-5 lg:grid-cols-[0.42fr_0.58fr]">
            <div className="rounded-[1.6rem] border border-white/8 bg-white/[0.04] p-6">
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-400">
                {t('internal.projectDashboard.producer.projectStatus')}
              </p>
              <div className="mt-3 flex items-center gap-3">
                <StatusBadge status={normalizeStatus(data?.status)} size="sm" />
                <span className="text-sm text-slate-300">{data?.status || 'active'}</span>
              </div>

              <div className="mt-6 flex items-center justify-between gap-4">
                <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-400">
                  {t('internal.projectDashboard.producer.overallProgress')}
                </p>
                <span className="text-sm font-medium text-white">{data?.overall_progress || 0}%</span>
              </div>
              <div className="mt-3 h-3 overflow-hidden rounded-xl bg-dark-300">
                <div
                  className="h-full bg-gradient-to-r from-amber-500 to-amber-400 transition-all duration-500"
                  style={{ width: `${data?.overall_progress || 0}%` }}
                />
              </div>
            </div>

            <div className="rounded-[1.6rem] border border-white/8 bg-white/[0.04] p-6">
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-400">
                {t('internal.projectDashboard.producer.quickActionsTitle')}
              </p>
              <div className="mt-4 grid gap-3 md:grid-cols-3">
                {quickActions.map(({ key, label, route, icon: Icon }) => (
                  <Link
                    key={key}
                    to={route}
                    className="rounded-2xl border border-amber-500/20 bg-amber-500/5 p-4 text-amber-100 transition-colors hover:bg-amber-500/10"
                  >
                    <Icon className="h-5 w-5 text-amber-300" />
                    <p className="mt-3 font-semibold text-white">{label}</p>
                    <span className="mt-2 inline-flex items-center gap-2 text-sm text-amber-300">
                      {t('internal.projectDashboard.producer.openAction')}
                      <ArrowRight className="h-4 w-4" />
                    </span>
                  </Link>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Commercial Description */}
      <section className="space-y-4">
        <p className="text-slate-400 max-w-lg">
          {t('internal.projectDashboard.intro')}
        </p>
      </section>

      <section className="rounded-[1.8rem] border border-white/8 bg-white/[0.03] p-6">
        <div className="flex items-center gap-3">
          <div className="rounded-2xl bg-amber-400/10 p-3 text-amber-300">
            <ArrowRight className="h-5 w-5" />
          </div>
          <div>
            <h2 className="heading-md">{t('internal.projectDashboard.producer.recommendedFlowTitle')}</h2>
            <p className="text-slate-400">{t('internal.projectDashboard.producer.recommendedFlowSubtitle')}</p>
          </div>
        </div>
        <div className="mt-6 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {['scriptBreakdown', 'budget', 'funding', 'storyboard', 'producerPack', 'distributionCrm'].map((step, index) => (
            <div key={step} className="rounded-2xl border border-white/8 bg-dark-300/60 p-4">
              <span className="inline-flex rounded-full border border-amber-400/20 bg-amber-400/10 px-3 py-1 text-xs font-semibold text-amber-300">
                {String(index + 1).padStart(2, '0')}
              </span>
              <p className="mt-3 text-sm font-medium text-white">
                {t(`internal.projectDashboard.producer.flow.${step}`)}
              </p>
            </div>
          ))}
        </div>
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
            <div className={`grid gap-4 ${phase.emphasis === 'primary' ? 'md:grid-cols-2 xl:grid-cols-3' : 'md:grid-cols-2 lg:grid-cols-3'}`}>
              {phaseModules.map((module) => {
                if (!module) return null
                const Icon = getModuleIcon(module.key)
                const route = getModuleRoute(module.key, projectId)
                return (
                  <Link
                    key={module.key}
                    to={route}
                    className={`card card-hover ${phase.emphasis === 'primary' ? 'border-amber-500/20 bg-amber-500/5' : ''}`}
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
            {t('internal.projectDashboard.producer.currentRisks')}
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
