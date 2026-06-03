import { useMemo, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import {
  AlertTriangle,
  Check,
  Clapperboard,
  Coins,
  Cpu,
  DollarSign,
  Film,
  FolderGit2,
  Layers,
  Lock,
  Play,
  Shield,
  Sparkles,
  Users,
} from 'lucide-react'
import { useProjectDashboard } from '@/hooks'
import { StatusBadge } from '@/components/StatusBadge'
import { t } from '@/i18n'

type BranchKey = 'rama1' | 'rama2' | 'rama3'

type DashboardModuleView = {
  key: string
  status: string
  summary: string
}

type BranchMetricConfig = {
  labelKey: string
  moduleKey?: string
}

type BranchConfig = {
  key: BranchKey
  titleKey: string
  descriptionKey: string
  icon: typeof Film
  notes: string[]
  metrics: BranchMetricConfig[]
  modules: Array<{
    key: string
    route: string
  }>
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

function formatModuleLabel(key: string) {
  return key.replace(/_/g, ' ')
}

function getModuleLabel(key: string) {
  const translationKey = key === 'producer_pack'
    ? 'internal.commandCenter.modules.producerPack'
    : `internal.commandCenter.modules.${key}`
  const translated = t(translationKey)

  return translated === translationKey ? formatModuleLabel(key) : translated
}

function getMetricStatusLabel(status?: string) {
  if (!status) return t('internal.commandCenter.metricStates.comingSoon')

  const translationKey = `internal.commandCenter.metricStates.${status}`
  const translated = t(translationKey)

  return translated === translationKey
    ? t('internal.commandCenter.metricStates.inProgress')
    : translated
}

function getBranchState(modules: DashboardModuleView[]) {
  const statuses = modules.map((module) => module.status)

  if (statuses.length === 0) return 'starting'
  if (statuses.some((status) => status === 'missing' || status === 'warning' || status === 'locked')) return 'attention'
  if (statuses.every((status) => status === 'ready' || status === 'approved')) return 'healthy'
  return 'inProgress'
}

function getBranchStateClasses(state: string) {
  switch (state) {
    case 'healthy':
      return 'border-emerald-400/20 bg-emerald-400/10 text-emerald-200'
    case 'attention':
      return 'border-amber-400/20 bg-amber-400/10 text-amber-200'
    default:
      return 'border-sky-400/20 bg-sky-400/10 text-sky-200'
  }
}

function getBranchRiskKey(state: string) {
  switch (state) {
    case 'healthy':
      return 'internal.commandCenter.riskStates.low'
    case 'attention':
      return 'internal.commandCenter.riskStates.high'
    default:
      return 'internal.commandCenter.riskStates.medium'
  }
}

export default function ProjectDashboardPage() {
  const { projectId = '' } = useParams()
  const dashboardQuery = useProjectDashboard(projectId)
  const [activeBranch, setActiveBranch] = useState<BranchKey>('rama1')

  const modules = useMemo<Record<string, DashboardModuleView>>(() => {
    if (!dashboardQuery.data?.modules) return {}

    return Object.entries(dashboardQuery.data.modules).reduce<Record<string, DashboardModuleView>>((acc, [key, value]) => {
      acc[key] = {
        key,
        status: value.status,
        summary: value.summary,
      }
      return acc
    }, {})
  }, [dashboardQuery.data])

  const branches = useMemo<BranchConfig[]>(() => ([
    {
      key: 'rama1',
      titleKey: 'internal.commandCenter.branches.rama1.title',
      descriptionKey: 'internal.commandCenter.branches.rama1.description',
      icon: DollarSign,
      notes: [
        t('internal.commandCenter.branches.rama1.note1'),
        t('internal.commandCenter.branches.rama1.note2'),
      ],
      metrics: [
        { labelKey: 'internal.commandCenter.metrics.funding', moduleKey: 'funding' },
        { labelKey: 'internal.commandCenter.metrics.budget', moduleKey: 'budget' },
        { labelKey: 'internal.commandCenter.metrics.documents' },
        { labelKey: 'internal.commandCenter.metrics.preparationShoot' },
      ],
      modules: [
        { key: 'budget', route: `/projects/${projectId}/budget` },
        { key: 'funding', route: `/projects/${projectId}/funding` },
        { key: 'producer_pack', route: `/projects/${projectId}/producer-pitch` },
      ],
    },
    {
      key: 'rama2',
      titleKey: 'internal.commandCenter.branches.rama2.title',
      descriptionKey: 'internal.commandCenter.branches.rama2.description',
      icon: Clapperboard,
      notes: [
        t('internal.commandCenter.branches.rama2.note1'),
        t('internal.commandCenter.branches.rama2.note2'),
      ],
      metrics: [
        { labelKey: 'internal.commandCenter.metrics.script', moduleKey: 'script' },
        { labelKey: 'internal.commandCenter.metrics.breakdown', moduleKey: 'breakdown' },
        { labelKey: 'internal.commandCenter.metrics.storyboard', moduleKey: 'storyboard' },
        { labelKey: 'internal.commandCenter.metrics.continuity' },
      ],
      modules: [
        { key: 'script', route: `/projects/${projectId}` },
        { key: 'breakdown', route: `/projects/${projectId}/breakdown` },
        { key: 'storyboard', route: `/projects/${projectId}/storyboard-builder` },
      ],
    },
    {
      key: 'rama3',
      titleKey: 'internal.commandCenter.branches.rama3.title',
      descriptionKey: 'internal.commandCenter.branches.rama3.description',
      icon: Film,
      notes: [
        t('internal.commandCenter.branches.rama3.note1'),
        t('internal.commandCenter.branches.rama3.note2'),
      ],
      metrics: [
        { labelKey: 'internal.commandCenter.metrics.editorial', moduleKey: 'editorial' },
        { labelKey: 'internal.commandCenter.metrics.delivery' },
        { labelKey: 'internal.commandCenter.metrics.distribution', moduleKey: 'distribution' },
        { labelKey: 'internal.commandCenter.metrics.sales', moduleKey: 'crm' },
      ],
      modules: [
        { key: 'editorial', route: `/projects/${projectId}/editorial` },
        { key: 'distribution', route: `/projects/${projectId}/distribution` },
        { key: 'crm', route: `/projects/${projectId}/crm` },
      ],
    },
  ]), [projectId])

  if (dashboardQuery.isLoading) {
    return (
      <div className="flex items-center justify-center p-12">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-amber-500 border-t-transparent" />
      </div>
    )
  }

  if (dashboardQuery.error || !dashboardQuery.data) {
    return (
      <div className="card">
        <div className="text-red-400">{t('internal.projectDashboard.errorLoading')}</div>
        <Link to={`/projects/${projectId}`} className="btn-secondary mt-4">
          {t('internal.commandCenter.backToProject')}
        </Link>
      </div>
    )
  }

  const data = dashboardQuery.data
  const activeBranchConfig = branches.find((branch) => branch.key === activeBranch) ?? branches[0]
  const activeRole = data.role_dashboard?.active_role || t('internal.commandCenter.roleFallback')
  const activeModules = activeBranchConfig.modules.map((module) => modules[module.key]).filter(Boolean)
  const activeBranchState = getBranchState(activeModules)
  const nextActionModule = activeBranchConfig.modules.find((module) => {
    const status = modules[module.key]?.status
    return !status || !['ready', 'approved'].includes(status)
  }) ?? activeBranchConfig.modules[0]

  return (
    <div className="space-y-8">
      <section className="relative overflow-hidden rounded-[2rem] border border-white/8 bg-dark-200/70 px-6 py-6 shadow-[0_28px_80px_rgba(2,6,23,0.32)] md:px-8 md:py-8">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(245,158,11,0.16),transparent_28%),radial-gradient(circle_at_82%_16%,rgba(56,189,248,0.08),transparent_22%)]" />
        <div className="relative space-y-8">
          <div className="flex flex-col gap-6 xl:flex-row xl:items-end xl:justify-between">
            <div className="max-w-4xl">
              <p className="inline-flex items-center rounded-full border border-amber-400/20 bg-amber-400/10 px-4 py-2 text-[11px] font-semibold uppercase tracking-[0.24em] text-amber-100">
                {t('internal.commandCenter.eyebrow')}
              </p>
              <div className="mt-5 flex flex-wrap items-center gap-3">
                <h1 className="text-4xl font-semibold tracking-tight text-white md:text-5xl">
                  {data.title || t('internal.common.project')}
                </h1>
                <span className="badge badge-amber">{data.status || t('internal.commandCenter.statusFallback')}</span>
              </div>
              <p className="mt-4 max-w-3xl text-lg leading-8 text-slate-300">
                {t('internal.commandCenter.subtitle')}
              </p>
            </div>

            <div className="flex flex-wrap gap-3">
              <Link to={`/projects/${projectId}`} className="btn-secondary">
                {t('internal.commandCenter.openProject')}
              </Link>
            </div>
          </div>

          <div className="grid gap-5 lg:grid-cols-[0.42fr_0.58fr]">
            <div className="rounded-[1.6rem] border border-white/8 bg-white/[0.04] p-6">
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-400">
                {t('internal.commandCenter.projectStatus')}
              </p>
              <div className="mt-3 flex items-center gap-3">
                <StatusBadge status={normalizeStatus(data.status)} size="sm" />
                <span className="text-sm text-slate-300">{data.status || t('internal.commandCenter.statusFallback')}</span>
              </div>

              <div className="mt-6 flex items-center justify-between gap-4">
                <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-400">
                  {t('internal.commandCenter.overallProgress')}
                </p>
                <span className="text-sm font-medium text-white">{data.overall_progress || 0}%</span>
              </div>
              <div className="mt-3 h-3 overflow-hidden rounded-xl bg-dark-300">
                <div
                  className="h-full bg-gradient-to-r from-amber-500 to-amber-400 transition-all duration-500"
                  style={{ width: `${data.overall_progress || 0}%` }}
                />
              </div>
            </div>

            <div className="rounded-[1.6rem] border border-white/8 bg-white/[0.04] p-6">
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-400">
                {t('internal.commandCenter.contextTitle')}
              </p>
              <div className="mt-4 grid gap-3 md:grid-cols-3">
                <div className="rounded-2xl border border-white/8 bg-dark-300/60 p-4">
                  <Users className="h-5 w-5 text-amber-300" />
                  <p className="mt-3 text-sm text-slate-400">{t('internal.commandCenter.activeRole')}</p>
                  <p className="mt-1 font-semibold text-white">{activeRole}</p>
                </div>
                <div className="rounded-2xl border border-white/8 bg-dark-300/60 p-4">
                  <Shield className="h-5 w-5 text-amber-300" />
                  <p className="mt-3 text-sm text-slate-400">{t('internal.commandCenter.visibility')}</p>
                  <p className="mt-1 font-semibold text-white">{t('internal.commandCenter.visibilityValue')}</p>
                </div>
                <div className="rounded-2xl border border-white/8 bg-dark-300/60 p-4">
                  <Sparkles className="h-5 w-5 text-amber-300" />
                  <p className="mt-3 text-sm text-slate-400">{t('internal.commandCenter.creditPoolTitle')}</p>
                  <p className="mt-1 font-semibold text-white">{t('internal.commandCenter.creditPoolPlaceholder')}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="space-y-4">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <h2 className="heading-md">{t('internal.commandCenter.branchNavTitle')}</h2>
            <p className="text-slate-400">{t('internal.commandCenter.branchNavSubtitle')}</p>
          </div>
          <span className="inline-flex items-center gap-2 rounded-full border border-white/8 bg-white/[0.04] px-4 py-2 text-sm text-slate-300">
            <Layers className="h-4 w-4 text-amber-300" />
            {t('internal.commandCenter.branchNavHint')}
          </span>
        </div>

        <div className="grid gap-4 lg:grid-cols-3">
          {branches.map((branch) => {
            const Icon = branch.icon
            const isActive = branch.key === activeBranch

            return (
              <button
                key={branch.key}
                type="button"
                onClick={() => setActiveBranch(branch.key)}
                className={`rounded-[1.6rem] border p-5 text-left transition-colors ${isActive ? 'border-amber-500/30 bg-amber-500/10' : 'border-white/8 bg-white/[0.03] hover:bg-white/[0.06]'}`}
              >
                <div className="flex items-center justify-between gap-4">
                  <div className="rounded-2xl bg-dark-300/80 p-3 text-amber-300">
                    <Icon className="h-5 w-5" />
                  </div>
                  <span className={`rounded-full border px-3 py-1 text-xs font-semibold ${getBranchStateClasses(getBranchState(branch.modules.map((module) => modules[module.key]).filter(Boolean)))}`}>
                    {t(`internal.commandCenter.branchStates.${getBranchState(branch.modules.map((module) => modules[module.key]).filter(Boolean))}`)}
                  </span>
                </div>
                <h3 className="mt-4 text-lg font-semibold text-white">{t(branch.titleKey)}</h3>
                <p className="mt-2 text-sm leading-6 text-slate-400">{t(branch.descriptionKey)}</p>
                <div className="mt-4 grid grid-cols-2 gap-2">
                  {branch.metrics.map((metric) => {
                    const status = metric.moduleKey ? modules[metric.moduleKey]?.status : undefined
                    return (
                      <div key={metric.labelKey} className="rounded-xl border border-white/8 bg-dark-300/40 p-3">
                        <p className="text-[11px] uppercase tracking-[0.2em] text-slate-500">{t(metric.labelKey)}</p>
                        <p className="mt-2 text-sm font-semibold text-white">{getMetricStatusLabel(status)}</p>
                      </div>
                    )
                  })}
                </div>
                <div className="mt-4 space-y-2 text-sm">
                  <p className="text-slate-400">{t('internal.commandCenter.riskLabel')}</p>
                  <p className="font-medium text-white">{t(getBranchRiskKey(getBranchState(branch.modules.map((module) => modules[module.key]).filter(Boolean))))}</p>
                </div>
              </button>
            )
          })}
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <div className="rounded-[1.8rem] border border-white/8 bg-white/[0.03] p-6">
          <div className="flex items-center gap-3">
            <div className="rounded-2xl bg-amber-400/10 p-3 text-amber-300">
              <activeBranchConfig.icon className="h-5 w-5" />
            </div>
            <div>
              <h2 className="heading-md">{t(activeBranchConfig.titleKey)}</h2>
              <p className="text-slate-400">{t('internal.commandCenter.branchSummaryTitle')}</p>
            </div>
            <span className={`ml-auto rounded-full border px-3 py-1 text-xs font-semibold ${getBranchStateClasses(activeBranchState)}`}>
              {t(`internal.commandCenter.branchStates.${activeBranchState}`)}
            </span>
          </div>

          <div className="mt-6 grid gap-4 lg:grid-cols-[0.7fr_0.3fr]">
            <div className="rounded-2xl border border-white/8 bg-dark-300/40 p-4">
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-400">{t('internal.commandCenter.nextActionTitle')}</p>
              <Link to={nextActionModule.route} className="mt-3 block text-base font-semibold text-white underline-offset-4 hover:underline">
                {getModuleLabel(nextActionModule.key)}
              </Link>
              <p className="mt-2 text-sm text-slate-400">{t('internal.commandCenter.nextActionDescription')}</p>
            </div>
            <div className="rounded-2xl border border-white/8 bg-dark-300/40 p-4">
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-400">{t('internal.commandCenter.riskLabel')}</p>
              <p className="mt-3 text-base font-semibold text-white">{t(getBranchRiskKey(activeBranchState))}</p>
            </div>
          </div>

          <div className="mt-6 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
            {activeBranchConfig.modules.map((module) => {
              const moduleData = modules[module.key]

              return (
                <Link
                  key={module.key}
                  to={module.route}
                  className="rounded-2xl border border-white/8 bg-dark-300/60 p-4 transition-colors hover:bg-dark-300"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="text-sm font-semibold capitalize text-white">{getModuleLabel(module.key)}</p>
                      <p className="mt-2 text-sm text-slate-400">{moduleData?.summary || t('internal.commandCenter.moduleFallback')}</p>
                    </div>
                    <StatusBadge status={normalizeStatus(moduleData?.status)} size="sm" />
                  </div>
                </Link>
              )
            })}
          </div>

          <div className="mt-6 rounded-2xl border border-white/8 bg-dark-300/40 p-5">
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-400">
              {t('internal.commandCenter.branchNotes')}
            </p>
            <div className="mt-4 space-y-3 text-sm text-slate-300">
              {activeBranchConfig.notes.map((note) => (
                <p key={note}>{note}</p>
              ))}
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <div className="rounded-[1.8rem] border border-white/8 bg-white/[0.03] p-6">
            <div className="flex items-center gap-3">
              <FolderGit2 className="h-5 w-5 text-amber-300" />
              <div>
                <h2 className="heading-md">{t('internal.commandCenter.branchImpactTitle')}</h2>
                <p className="text-slate-400">{t('internal.commandCenter.branchImpactDescription')}</p>
              </div>
              <span className="ml-auto rounded-full border border-amber-400/20 bg-amber-400/10 px-3 py-1 text-xs font-semibold text-amber-200">
                {t('internal.commandCenter.comingSoon')}
              </span>
            </div>
            <div className="mt-5 rounded-2xl border border-dashed border-white/10 bg-dark-300/40 p-5 text-sm text-slate-400">
              <p>{t('internal.commandCenter.branchImpactPlaceholder')}</p>
              <p className="mt-3 text-slate-300">{t('internal.commandCenter.branchImpactNoWorkflow')}</p>
            </div>
            <div className="mt-5 grid gap-3 sm:grid-cols-2">
              {['pending', 'evaluating', 'approved', 'rejected'].map((state) => (
                <div key={state} className="rounded-2xl border border-white/8 bg-dark-300/40 p-4">
                  <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500">
                    {t(`internal.commandCenter.branchImpactStates.${state}`)}
                  </p>
                  <p className="mt-2 text-sm text-slate-300">{t(`internal.commandCenter.branchImpactStateDescriptions.${state}`)}</p>
                </div>
              ))}
            </div>
            <div className="mt-5 space-y-3">
              {['creativeBudget', 'productionCreative', 'postCostSales'].map((example) => (
                <div key={example} className="rounded-2xl border border-white/8 bg-dark-300/40 p-4">
                  <p className="text-sm font-semibold text-white">{t(`internal.commandCenter.branchImpactExamples.${example}.title`)}</p>
                  <p className="mt-2 text-sm text-slate-400">{t(`internal.commandCenter.branchImpactExamples.${example}.description`)}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-[1.8rem] border border-white/8 bg-white/[0.03] p-6">
            <div className="flex items-center gap-3">
              <Sparkles className="h-5 w-5 text-amber-300" />
              <div>
                <h2 className="heading-md">{t('internal.commandCenter.creditPoolTitle')}</h2>
                <p className="text-slate-400">{t('internal.commandCenter.creditPoolDescription')}</p>
              </div>
              <span className="ml-auto rounded-full border border-amber-400/20 bg-amber-400/10 px-3 py-1 text-xs font-semibold text-amber-200">
                {t('internal.commandCenter.comingSoon')}
              </span>
            </div>
            <div className="mt-5 grid gap-3 sm:grid-cols-2">
              <div className="rounded-2xl border border-white/8 bg-dark-300/40 p-4">
                <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-400">{t('internal.commandCenter.creditPoolAvailable')}</p>
                <p className="mt-2 text-2xl font-semibold text-white">{t('internal.commandCenter.creditPoolPlaceholder')}</p>
              </div>
              <div className="rounded-2xl border border-white/8 bg-dark-300/40 p-4">
                <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-400">{t('internal.commandCenter.creditPoolUsage')}</p>
                <p className="mt-2 text-2xl font-semibold text-white">{t('internal.commandCenter.notAvailableYet')}</p>
              </div>
              <div className="rounded-2xl border border-white/8 bg-dark-300/40 p-4">
                <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-400">{t('internal.commandCenter.creditPoolRemaining')}</p>
                <p className="mt-2 text-2xl font-semibold text-white">{t('internal.commandCenter.creditPoolPlaceholder')}</p>
              </div>
              <div className="rounded-2xl border border-white/8 bg-dark-300/40 p-4">
                <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-400">{t('internal.commandCenter.creditPoolAlerts')}</p>
                <p className="mt-2 text-2xl font-semibold text-white">{t('internal.commandCenter.notAvailableYet')}</p>
              </div>
            </div>
            <div className="mt-5 rounded-2xl border border-dashed border-white/10 bg-dark-300/40 p-5 text-sm text-slate-400">
              <p>{t('internal.commandCenter.creditPoolSeparateNote')}</p>
              <p className="mt-3 text-slate-300">{t('internal.commandCenter.creditPoolNoRealData')}</p>
            </div>
          </div>

          <div className="rounded-[1.8rem] border border-white/8 bg-white/[0.03] p-6">
            <div className="flex items-center gap-3">
              <Users className="h-5 w-5 text-amber-300" />
              <div>
                <h2 className="heading-md">{t('internal.commandCenter.futureVisibilityTitle')}</h2>
                <p className="text-slate-400">{t('internal.commandCenter.futureVisibilityDescription')}</p>
              </div>
            </div>
            <p className="mt-5 text-sm text-slate-300">{t('internal.commandCenter.futureVisibilityPlaceholder')}</p>
          </div>
        </div>
      </section>

      {/* Project AI Status Section */}
      <section className="relative overflow-hidden rounded-[2rem] border border-white/8 bg-dark-200/70 px-6 py-6 shadow-[0_28px_80px_rgba(2,6,23,0.32)] md:px-8 md:py-8">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(245,158,11,0.12),transparent_30%)]" />
        <div className="relative space-y-6">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div>
              <div className="flex items-center gap-3">
                <h2 className="text-2xl font-semibold tracking-tight text-white md:text-3xl">
                  {t('internal.commandCenter.aiEngine.title')}
                </h2>
                <span className="inline-flex items-center gap-1.5 rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-1 text-xs font-semibold text-emerald-200">
                  <span className="relative flex h-2 w-2">
                    <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75"></span>
                    <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-500"></span>
                  </span>
                  {t('internal.commandCenter.aiEngine.statusCard.active')}
                </span>
              </div>
              <p className="mt-2 text-slate-300">
                {t('internal.commandCenter.aiEngine.subtitle')}
              </p>
            </div>
          </div>

          <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
            {/* AI Engine Status & Mode Card */}
            <div className="rounded-[1.6rem] border border-white/8 bg-white/[0.04] p-6 flex flex-col justify-between">
              <div>
                <div className="flex items-center gap-2 text-amber-300">
                  <Cpu className="h-5 w-5" />
                  <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-400">
                    {t('internal.commandCenter.aiEngine.statusCard.title')}
                  </p>
                </div>
                <div className="mt-4">
                  <p className="text-lg font-semibold text-white">
                    {t('internal.commandCenter.aiEngine.modeCard.value')}
                  </p>
                  <p className="mt-1 text-sm text-slate-400">
                    {t('internal.commandCenter.aiEngine.modeCard.subtext')}
                  </p>
                </div>
              </div>
              <div className="mt-6 pt-4 border-t border-white/5">
                <p className="text-sm text-slate-300">
                  {t('internal.commandCenter.aiEngine.statusCard.activeSub')}
                </p>
              </div>
            </div>

            {/* Privacy Mode & Reliability Card */}
            <div className="rounded-[1.6rem] border border-white/8 bg-white/[0.04] p-6 flex flex-col justify-between">
              <div>
                <div className="flex items-center gap-2 text-amber-300">
                  <Shield className="h-5 w-5" />
                  <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-400">
                    {t('internal.commandCenter.aiEngine.privacyCard.title')}
                  </p>
                </div>
                <div className="mt-4 space-y-3">
                  <div>
                    <span className="inline-flex items-center gap-1 text-sm font-semibold text-white">
                      <Lock className="h-3.5 w-3.5 text-amber-400" />
                      {t('internal.commandCenter.aiEngine.privacyCard.value')}
                    </span>
                    <p className="mt-1 text-xs text-slate-400">
                      {t('internal.commandCenter.aiEngine.privacyCard.subtext')}
                    </p>
                  </div>
                  <div className="pt-2 border-t border-white/5 space-y-2">
                    <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
                      {t('internal.commandCenter.aiEngine.reliabilityCard.title')}
                    </p>
                    <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-slate-300">
                      <span className="flex items-center gap-1">
                        <Check className="h-3 w-3 text-emerald-400" />
                        {t('internal.commandCenter.aiEngine.reliabilityCard.value')}
                      </span>
                      <span>
                        {t('internal.commandCenter.aiEngine.reliabilityCard.queue').replace('{value}', t('internal.commandCenter.aiEngine.reliabilityCard.normal'))}
                      </span>
                      <span>
                        {t('internal.commandCenter.aiEngine.reliabilityCard.incidents').replace('{value}', t('internal.commandCenter.aiEngine.reliabilityCard.noIncidents'))}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Credit & Cost Visibility Card */}
            <div className="rounded-[1.6rem] border border-white/8 bg-white/[0.04] p-6 flex flex-col justify-between">
              <div>
                <div className="flex items-center gap-2 text-amber-300">
                  <Coins className="h-5 w-5" />
                  <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-400">
                    {t('internal.commandCenter.aiEngine.creditCard.title')}
                  </p>
                </div>
                <div className="mt-4 space-y-3">
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-400">{t('internal.commandCenter.aiEngine.creditCard.included').replace('{count}', '2000')}</span>
                    <span className="text-slate-400">{t('internal.commandCenter.aiEngine.creditCard.used').replace('{count}', '420')}</span>
                  </div>
                  {/* Progress Bar */}
                  <div className="h-2 overflow-hidden rounded-xl bg-dark-300">
                    <div className="h-full bg-gradient-to-r from-amber-500 to-amber-400" style={{ width: '79%' }} />
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-semibold text-white">
                      {t('internal.commandCenter.aiEngine.creditCard.remaining').replace('{count}', '1580')}
                    </span>
                    <span className="rounded-full bg-amber-400/10 px-2.5 py-1 text-[11px] font-semibold text-amber-200">
                      {t('internal.commandCenter.aiEngine.creditCard.intensity')}: {t('internal.commandCenter.aiEngine.creditCard.intensityValue')}
                    </span>
                  </div>
                </div>
              </div>
              <div className="mt-4 pt-3 border-t border-white/5 space-y-2">
                <p className="text-xs text-amber-200/90 font-medium">
                  {t('internal.commandCenter.aiEngine.creditCard.estimated').replace('{range}', '35–90')}
                </p>
                <p className="text-[11px] leading-relaxed text-slate-500 italic">
                  {t('internal.commandCenter.aiEngine.creditCard.disclaimer')}
                </p>
              </div>
            </div>
          </div>

          {/* Intense Task Warning Card */}
          <div className="flex gap-3 rounded-2xl border border-amber-500/20 bg-amber-500/5 p-4 text-amber-200 text-sm">
            <AlertTriangle className="h-5 w-5 shrink-0 text-amber-400" />
            <div>
              <h4 className="font-semibold">{t('internal.commandCenter.aiEngine.warningCard.title')}</h4>
              <p className="mt-1 text-xs text-amber-200/80 leading-relaxed">
                {t('internal.commandCenter.aiEngine.warningCard.description')}
              </p>
            </div>
          </div>

          {/* Result-Oriented Action Panel */}
          <div className="rounded-[1.6rem] border border-white/8 bg-white/[0.02] p-6 space-y-4">
            <div>
              <h3 className="text-lg font-semibold text-white">
                {t('internal.commandCenter.aiEngine.actionsPanel.title')}
              </h3>
              <p className="text-sm text-slate-400">
                {t('internal.commandCenter.aiEngine.actionsPanel.description')}
              </p>
            </div>
            <div className="grid gap-3 grid-cols-2 sm:grid-cols-3 md:grid-cols-4">
              <Link to={`/projects/${projectId}`} className="flex items-center gap-2 rounded-xl border border-white/8 bg-dark-300/40 p-3 hover:bg-dark-300/80 text-sm font-medium text-slate-200 hover:text-white transition-colors">
                <Play className="h-3.5 w-3.5 text-amber-400" />
                {t('internal.commandCenter.aiEngine.actionsPanel.actions.script')}
              </Link>
              <Link to={`/projects/${projectId}/storyboard-builder`} className="flex items-center gap-2 rounded-xl border border-white/8 bg-dark-300/40 p-3 hover:bg-dark-300/80 text-sm font-medium text-slate-200 hover:text-white transition-colors">
                <Play className="h-3.5 w-3.5 text-amber-400" />
                {t('internal.commandCenter.aiEngine.actionsPanel.actions.storyboard')}
              </Link>
              <Link to={`/projects/${projectId}/producer-pitch`} className="flex items-center gap-2 rounded-xl border border-white/8 bg-dark-300/40 p-3 hover:bg-dark-300/80 text-sm font-medium text-slate-200 hover:text-white transition-colors">
                <Play className="h-3.5 w-3.5 text-amber-400" />
                {t('internal.commandCenter.aiEngine.actionsPanel.actions.dossier')}
              </Link>
              <Link to={`/projects/${projectId}/funding`} className="flex items-center gap-2 rounded-xl border border-white/8 bg-dark-300/40 p-3 hover:bg-dark-300/80 text-sm font-medium text-slate-200 hover:text-white transition-colors">
                <Play className="h-3.5 w-3.5 text-amber-400" />
                {t('internal.commandCenter.aiEngine.actionsPanel.actions.funding')}
              </Link>
              <Link to={`/projects/${projectId}`} className="flex items-center gap-2 rounded-xl border border-white/8 bg-dark-300/40 p-3 hover:bg-dark-300/80 text-sm font-medium text-slate-200 hover:text-white transition-colors">
                <Play className="h-3.5 w-3.5 text-amber-400" />
                {t('internal.commandCenter.aiEngine.actionsPanel.actions.art')}
              </Link>
              <Link to={`/projects/${projectId}/delivery`} className="flex items-center gap-2 rounded-xl border border-white/8 bg-dark-300/40 p-3 hover:bg-dark-300/80 text-sm font-medium text-slate-200 hover:text-white transition-colors">
                <Play className="h-3.5 w-3.5 text-amber-400" />
                {t('internal.commandCenter.aiEngine.actionsPanel.actions.delivery')}
              </Link>
              <Link to={`/projects/${projectId}/reviews`} className="flex items-center gap-2 rounded-xl border border-white/8 bg-dark-300/40 p-3 hover:bg-dark-300/80 text-sm font-medium text-slate-200 hover:text-white transition-colors">
                <Play className="h-3.5 w-3.5 text-amber-400" />
                {t('internal.commandCenter.aiEngine.actionsPanel.actions.review')}
              </Link>
              <Link to={`/projects/${projectId}/distribution`} className="flex items-center gap-2 rounded-xl border border-white/8 bg-dark-300/40 p-3 hover:bg-dark-300/80 text-sm font-medium text-slate-200 hover:text-white transition-colors">
                <Play className="h-3.5 w-3.5 text-amber-400" />
                {t('internal.commandCenter.aiEngine.actionsPanel.actions.crm')}
              </Link>
            </div>
          </div>

          {/* Advanced Configuration Placeholder */}
          <div className="rounded-[1.6rem] border border-white/8 bg-white/[0.04] p-6 space-y-2">
            <h4 className="text-base font-semibold text-white flex items-center gap-2">
              <Lock className="h-4 w-4 text-slate-400" />
              {t('internal.commandCenter.aiEngine.advancedConfig.title')}
            </h4>
            <p className="text-sm text-slate-400">
              {t('internal.commandCenter.aiEngine.advancedConfig.description')}
            </p>
          </div>
        </div>
      </section>

      {data.warnings && data.warnings.length > 0 && (
        <section className="space-y-4">
          <h2 className="heading-md flex items-center gap-2">
            <Shield className="h-5 w-5 text-amber-400" />
            {t('internal.commandCenter.warningsTitle')}
          </h2>
          <div className="space-y-2">
            {data.warnings.map((warning, index) => (
              <div key={`${warning}-${index}`} className="rounded-xl border border-amber-500/20 bg-amber-500/5 p-4 text-amber-200">
                {warning}
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  )
}
