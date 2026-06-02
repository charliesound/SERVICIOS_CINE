import { useMemo } from 'react'
import { Link } from 'react-router-dom'
import { Layers3, Lock, Waypoints } from 'lucide-react'
import clsx from 'clsx'
import { useModuleCatalog, useMyModules } from '@/hooks'
import { useSeo } from '@/hooks/useSeo'
import { useAuthStore } from '@/store'
import type { ModuleInfo } from '@/types'
import { getApiErrorMessage } from '@/utils/apiErrors'
import ModuleCard, { type ModuleCardAction } from '@/components/modules/ModuleCard'
import { CID_CORE_FUTURE_PRODUCTS } from '@/config/cidCoreScope'
import { useLanguage } from '@/i18n'

type ModuleViewModel = ModuleInfo & {
  enabled: boolean | null
  locked_reason?: string | null
}

const planBadgeTone: Record<string, string> = {
  demo: 'badge-free',
  free: 'badge-free',
  creator: 'badge-creator',
  producer: 'badge-creator',
  studio: 'badge-studio',
  enterprise: 'badge-enterprise',
}

function formatPlanLabel(plan: string, t: (key: string) => string) {
  const labels: Record<string, string> = {
    demo: 'Demo',
    free: t('internal.modulesCatalog.freePlan'),
    creator: 'Creator',
    producer: 'Producer',
    studio: 'Studio',
    enterprise: 'Enterprise',
  }
  return labels[plan] || plan
}

function getLockedReasonLabel(reason: string | null | undefined, t: (key: string) => string) {
  if (!reason) return null
  if (reason === 'plan_feature_missing') return t('internal.modulesCatalog.planMissing')
  if (reason.startsWith('dependency_locked:')) {
    const dependency = reason.split(':', 2)[1]?.replace(/_/g, ' ')
    return dependency
      ? `Requiere activar primero ${dependency}`
      : t('internal.modulesCatalog.dependencyMissing')
  }
  return t('internal.modulesCatalog.commercialAccess')
}

function resolveModuleAction(module: ModuleViewModel, t: (key: string) => string): ModuleCardAction {
  if (module.enabled === false) {
    return {
      label: module.locked_reason?.startsWith('dependency_locked:') ? t('internal.modulesCatalog.requestActivation') : t('internal.modulesCatalog.upgradePlan'),
      href: module.locked_reason?.startsWith('dependency_locked:') ? '/pricing' : '/plans',
      helperText: t('internal.modulesCatalog.helpers.activateWithHigherPlan'),
      variant: 'secondary',
    }
  }

  switch (module.key) {
    case 'core':
      return {
        label: t('internal.modulesCatalog.openModule'),
        href: '/projects',
        helperText: t('internal.modulesCatalog.helpers.cidBaseFromProjects'),
        variant: 'primary',
      }
    case 'script_analysis':
      return {
        label: t('internal.modulesCatalog.openModule'),
        href: '/projects',
        helperText: t('internal.modulesCatalog.helpers.scriptAnalysisWorkspace'),
        variant: 'primary',
      }
    case 'pitch_deck':
    case 'storyboard_ai':
    case 'breakdown':
    case 'budget_lite':
    case 'funding_grants':
    case 'delivery_distribution':
      return {
        label: t('internal.modulesCatalog.openModule'),
        href: '/projects',
        helperText: t('internal.modulesCatalog.helpers.selectProjectRealFlow'),
        variant: 'primary',
      }
    case 'pipeline_builder':
      return {
        label: t('internal.modulesCatalog.openModule'),
        href: '/cid/pipeline-builder',
        helperText: 'Disponible como espacio operativo transversal dentro de CID.',
        variant: 'primary',
      }
    case 'legal_documents':
      return {
        label: t('internal.modulesCatalog.openModule'),
        href: '/documents',
        helperText: t('internal.modulesCatalog.helpers.documentalWorkspace'),
        variant: 'primary',
      }
    default:
      return {
        label: t('internal.modulesCatalog.comingSoon'),
        disabled: true,
        helperText: t('internal.modulesCatalog.helpers.commercialScreenNextUx'),
        variant: 'secondary',
      }
  }
}

function LoadingGrid() {
  return (
    <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
      {Array.from({ length: 6 }).map((_, index) => (
        <div key={index} className="card h-[330px] animate-pulse rounded-[1.6rem] border border-white/6 bg-white/[0.03]" />
      ))}
    </div>
  )
}

export default function ModulesCatalogPage() {
  const { t } = useLanguage()
  const { user } = useAuthStore()
  const catalogQuery = useModuleCatalog()
  const myModulesQuery = useMyModules()

  useSeo({
    title: t('internal.modulesCatalog.seoTitle'),
    description: t('internal.modulesCatalog.seoDescription'),
    path: '/modules',
    robots: 'noindex, nofollow',
  })

  const moduleView = useMemo(() => {
    const catalogModules = catalogQuery.data?.modules ?? []
    const accessMap = new Map<string, ModuleViewModel>()

    if (myModulesQuery.data) {
      for (const module of myModulesQuery.data.available_modules) {
        accessMap.set(module.key, { ...module, enabled: true })
      }
      for (const module of myModulesQuery.data.locked_modules) {
        accessMap.set(module.key, { ...module, enabled: false })
      }
    }

    return catalogModules.map<ModuleViewModel>((module) => {
      const access = accessMap.get(module.key)
      if (!access) {
        return {
          ...module,
          enabled: myModulesQuery.data ? false : null,
          locked_reason: myModulesQuery.data ? 'plan_feature_missing' : null,
        }
      }

      return {
        ...module,
        enabled: access.enabled,
        locked_reason: access.locked_reason ?? null,
      }
    })
  }, [catalogQuery.data, myModulesQuery.data])

  const availableModules = moduleView.filter((module) => module.enabled === true)
  const lockedModules = moduleView.filter((module) => module.enabled === false)
  const informationalModules = moduleView.filter((module) => module.enabled === null)

  const planName = myModulesQuery.data?.plan || user?.plan || 'free'
  const planLabel = formatPlanLabel(planName, t)
  const myModulesError = myModulesQuery.error
    ? getApiErrorMessage(myModulesQuery.error, t('internal.modulesCatalog.planAccessError'))
    : null

  if (catalogQuery.isLoading) {
    return (
      <div className="space-y-8">
        <div className="card overflow-hidden rounded-[2rem] border border-white/8 bg-white/[0.03] p-8">
          <div className="h-7 w-40 animate-pulse rounded bg-white/10" />
          <div className="mt-4 h-12 w-full max-w-3xl animate-pulse rounded bg-white/10" />
          <div className="mt-4 h-6 w-full max-w-4xl animate-pulse rounded bg-white/5" />
        </div>
        <LoadingGrid />
      </div>
    )
  }

  if (catalogQuery.error) {
    return (
      <div className="card rounded-[2rem] border border-rose-400/20 bg-rose-500/10 p-8">
        <p className="editorial-kicker text-rose-200">{t('internal.modulesCatalog.catalogEyebrow')}</p>
        <h1 className="mt-4 text-3xl font-semibold text-white">{t('internal.modulesCatalog.catalogErrorTitle')}</h1>
        <p className="mt-4 max-w-2xl text-slate-300">
          {getApiErrorMessage(catalogQuery.error, t('internal.modulesCatalog.catalogErrorFallback'))}
        </p>
        <div className="mt-6 flex gap-3">
          <button type="button" onClick={() => catalogQuery.refetch()} className="btn-primary">
            {t('internal.common.retry')}
          </button>
          <Link to="/projects" className="btn-secondary">
            {t('internal.modulesCatalog.backProjects')}
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <section className="relative overflow-hidden rounded-[2rem] border border-white/8 bg-dark-200/70 px-8 py-8 shadow-[0_28px_80px_rgba(2,6,23,0.32)]">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(245,158,11,0.16),transparent_28%),radial-gradient(circle_at_82%_16%,rgba(56,189,248,0.1),transparent_24%)]" />
        <div className="relative flex flex-col gap-8 xl:flex-row xl:items-end xl:justify-between">
          <div className="max-w-4xl">
            <div className="inline-flex items-center gap-2 rounded-full border border-amber-400/20 bg-amber-400/10 px-4 py-2 text-[11px] font-semibold uppercase tracking-[0.24em] text-amber-100">
              <Layers3 className="h-3.5 w-3.5" />
              {t('internal.modulesCatalog.eyebrow')}
            </div>
            <h1 className="mt-6 text-4xl font-semibold tracking-tight text-white md:text-5xl">{t('internal.modulesCatalog.title')}</h1>
              <p className="mt-4 max-w-3xl text-lg leading-8 text-slate-200">
              {t('internal.modulesCatalog.subtitle')}
              </p>
              <p className="mt-4 max-w-3xl text-sm leading-7 text-slate-400">
              {t('internal.modulesCatalog.scopeNote')}
              </p>
            </div>

          <div className="grid gap-4 sm:grid-cols-3 xl:min-w-[440px]">
            <div className="rounded-[1.4rem] border border-white/8 bg-white/[0.045] p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-slate-500">{t('internal.modulesCatalog.currentPlan')}</p>
              <div className="mt-3 flex items-center gap-3">
                <span className={clsx('badge', planBadgeTone[planName] || 'badge-free')}>
                  {planLabel}
                </span>
                <span className="text-sm text-slate-400">{t('internal.modulesCatalog.currentAccess')}</span>
              </div>
            </div>

            <div className="rounded-[1.4rem] border border-white/8 bg-white/[0.045] p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-slate-500">{t('internal.modulesCatalog.available')}</p>
              <p className="mt-3 text-3xl font-semibold text-white">{myModulesQuery.data?.total_available ?? availableModules.length}</p>
              <p className="mt-2 text-sm text-slate-400">{t('internal.modulesCatalog.availableHelp')}</p>
            </div>

            <div className="rounded-[1.4rem] border border-white/8 bg-white/[0.045] p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-slate-500">{t('internal.modulesCatalog.expand')}</p>
              <p className="mt-3 text-3xl font-semibold text-white">{myModulesQuery.data?.total_locked ?? lockedModules.length}</p>
              <p className="mt-2 text-sm text-slate-400">{t('internal.modulesCatalog.expandHelp')}</p>
            </div>
          </div>
        </div>
      </section>

      {myModulesError ? (
        <div className="rounded-[1.4rem] border border-cyan-400/20 bg-cyan-500/10 px-5 py-4 text-sm text-cyan-50">
          <div className="flex items-start gap-3">
            <Waypoints className="mt-0.5 h-5 w-5 text-cyan-200" />
            <div>
              <p className="font-semibold">{t('internal.modulesCatalog.infoModeTitle')}</p>
              <p className="mt-1 text-cyan-100/80">
                {myModulesError} {t('internal.modulesCatalog.infoModeText')}
              </p>
            </div>
          </div>
        </div>
      ) : null}

      <section className="rounded-[1.8rem] border border-cyan-400/20 bg-cyan-500/8 p-6 md:p-7 text-sm text-cyan-50">
        <p className="font-semibold text-cyan-100">{t('internal.modulesCatalog.outsideTitle')}</p>
        <p className="mt-2 max-w-3xl text-cyan-100/80">
          {t('internal.modulesCatalog.outsideText')}
        </p>
        <div className="mt-4 flex flex-wrap gap-2">
          {CID_CORE_FUTURE_PRODUCTS.map((product) => (
            <span key={product} className="landing-pill border-cyan-300/20 text-cyan-100">
              {product}
            </span>
          ))}
        </div>
      </section>

      {!myModulesError && myModulesQuery.isLoading ? (
        <section className="space-y-4">
          <div>
            <p className="editorial-kicker text-slate-300">{t('internal.modulesCatalog.planAccessEyebrow')}</p>
            <h2 className="mt-2 text-2xl font-semibold text-white">{t('internal.modulesCatalog.loadingAvailability')}</h2>
          </div>
          <LoadingGrid />
        </section>
      ) : null}

      {moduleView.length === 0 ? (
        <div className="card rounded-[1.8rem] p-10 text-center">
          <Lock className="mx-auto h-12 w-12 text-slate-500" />
          <h2 className="mt-4 text-2xl font-semibold text-white">{t('internal.modulesCatalog.emptyTitle')}</h2>
          <p className="mt-3 text-slate-400">{t('internal.modulesCatalog.emptyText')}</p>
        </div>
      ) : null}

      {!myModulesError && availableModules.length > 0 ? (
        <section className="space-y-5">
          <div className="flex items-end justify-between gap-4">
            <div>
              <p className="editorial-kicker text-emerald-200">{t('internal.modulesCatalog.activeAccess')}</p>
              <h2 className="mt-2 text-2xl font-semibold text-white">{t('internal.modulesCatalog.availableInPlan')}</h2>
            </div>
            <span className="text-sm text-slate-400">{availableModules.length} {t('internal.modulesCatalog.moduleCountLabel')}</span>
          </div>
          <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
            {availableModules.map((module) => (
              <ModuleCard
                key={module.key}
                module={module}
                enabled={module.enabled}
                action={resolveModuleAction(module, t)}
                lockedReasonLabel={getLockedReasonLabel(module.locked_reason, t)}
              />
            ))}
          </div>
        </section>
      ) : null}

      {!myModulesError && lockedModules.length > 0 ? (
        <section className="space-y-5">
          <div className="flex items-end justify-between gap-4">
            <div>
              <p className="editorial-kicker text-amber-200">{t('internal.modulesCatalog.commercialExpansion')}</p>
              <h2 className="mt-2 text-2xl font-semibold text-white">{t('internal.modulesCatalog.lockedTitle')}</h2>
            </div>
            <span className="text-sm text-slate-400">{lockedModules.length} {t('internal.modulesCatalog.moduleCountLabel')}</span>
          </div>
          <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
            {lockedModules.map((module) => (
              <ModuleCard
                key={module.key}
                module={module}
                enabled={module.enabled}
                action={resolveModuleAction(module, t)}
                lockedReasonLabel={getLockedReasonLabel(module.locked_reason, t)}
              />
            ))}
          </div>
        </section>
      ) : null}

      {myModulesError && informationalModules.length > 0 ? (
        <section className="space-y-5">
          <div>
            <p className="editorial-kicker text-slate-300">{t('internal.modulesCatalog.generalCatalog')}</p>
            <h2 className="mt-2 text-2xl font-semibold text-white">{t('internal.modulesCatalog.visibleModules')}</h2>
          </div>
          <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
            {informationalModules.map((module) => (
              <ModuleCard
                key={module.key}
                module={module}
                enabled={module.enabled}
                action={{
                  label: t('internal.modulesCatalog.requestActivation'),
                  href: '/pricing',
                  helperText: 'Acceso orientativo mientras se restablece la lectura de tu plan.',
                  variant: 'secondary',
                }}
              />
            ))}
          </div>
        </section>
      ) : null}

      <section className="rounded-[1.8rem] border border-white/8 bg-white/[0.03] p-6 md:p-7">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
          <div className="max-w-2xl">
            <p className="editorial-kicker text-amber-200">{t('internal.modulesCatalog.activationEyebrow')}</p>
            <h2 className="mt-2 text-2xl font-semibold text-white">{t('internal.modulesCatalog.activationTitle')}</h2>
            <p className="mt-3 text-sm leading-7 text-slate-400">
              {t('internal.modulesCatalog.activationText')}
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <Link to="/plans" className="btn-primary">{t('internal.common.viewPlans')}</Link>
            <Link to="/pricing" className="btn-secondary">{t('internal.modulesCatalog.requestActivation')}</Link>
          </div>
        </div>
      </section>
    </div>
  )
}
