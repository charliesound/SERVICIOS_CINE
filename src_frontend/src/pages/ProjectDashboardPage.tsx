import { useMemo, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import {
  Clapperboard,
  DollarSign,
  Film,
  FolderGit2,
  Layers,
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

type BranchConfig = {
  key: BranchKey
  titleKey: string
  descriptionKey: string
  icon: typeof Film
  notes: string[]
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
                  <span className={`rounded-full px-3 py-1 text-xs font-semibold ${isActive ? 'bg-amber-400/15 text-amber-200' : 'bg-white/8 text-slate-300'}`}>
                    {isActive ? t('internal.commandCenter.activeBranch') : t('internal.commandCenter.openBranch')}
                  </span>
                </div>
                <h3 className="mt-4 text-lg font-semibold text-white">{t(branch.titleKey)}</h3>
                <p className="mt-2 text-sm leading-6 text-slate-400">{t(branch.descriptionKey)}</p>
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
            </div>
            <div className="mt-5 rounded-2xl border border-dashed border-white/10 bg-dark-300/40 p-5 text-sm text-slate-400">
              {t('internal.commandCenter.branchImpactPlaceholder')}
            </div>
            <p className="mt-3 text-xs font-semibold uppercase tracking-[0.2em] text-amber-300">
              {t('internal.commandCenter.comingSoon')}
            </p>
          </div>

          <div className="rounded-[1.8rem] border border-white/8 bg-white/[0.03] p-6">
            <div className="flex items-center gap-3">
              <Sparkles className="h-5 w-5 text-amber-300" />
              <div>
                <h2 className="heading-md">{t('internal.commandCenter.creditPoolTitle')}</h2>
                <p className="text-slate-400">{t('internal.commandCenter.creditPoolDescription')}</p>
              </div>
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
            </div>
            <p className="mt-3 text-xs font-semibold uppercase tracking-[0.2em] text-amber-300">
              {t('internal.commandCenter.comingSoon')}
            </p>
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
