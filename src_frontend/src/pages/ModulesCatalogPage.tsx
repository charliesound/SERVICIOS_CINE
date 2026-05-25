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

function formatPlanLabel(plan: string) {
  const labels: Record<string, string> = {
    demo: 'Demo',
    free: 'Gratis',
    creator: 'Creator',
    producer: 'Producer',
    studio: 'Studio',
    enterprise: 'Enterprise',
  }
  return labels[plan] || plan
}

function getLockedReasonLabel(reason?: string | null) {
  if (!reason) return null
  if (reason === 'plan_feature_missing') return 'No incluido en tu plan actual'
  if (reason.startsWith('dependency_locked:')) {
    const dependency = reason.split(':', 2)[1]?.replace(/_/g, ' ')
    return dependency
      ? `Requiere activar primero ${dependency}`
      : 'Requiere activar otro módulo primero'
  }
  return 'Acceso sujeto a activación comercial'
}

function resolveModuleAction(module: ModuleViewModel): ModuleCardAction {
  if (module.enabled === false) {
    return {
      label: module.locked_reason?.startsWith('dependency_locked:') ? 'Solicitar activación' : 'Mejorar plan',
      href: module.locked_reason?.startsWith('dependency_locked:') ? '/pricing' : '/plans',
      helperText: 'Activa este módulo a través de un plan superior o validación comercial.',
      variant: 'secondary',
    }
  }

  switch (module.key) {
    case 'core':
      return {
        label: 'Abrir módulo',
        href: '/projects',
        helperText: 'La base operativa de CID arranca desde tus proyectos y dashboard.',
        variant: 'primary',
      }
    case 'script_analysis':
      return {
        label: 'Abrir módulo',
        href: '/projects',
        helperText: 'Selecciona un proyecto y pulsa "Script Analysis Pro" desde la vista del proyecto para acceder al workspace dedicado.',
        variant: 'primary',
      }
    case 'pitch_deck':
    case 'storyboard_ai':
    case 'breakdown':
    case 'budget_lite':
    case 'funding_grants':
    case 'delivery_distribution':
      return {
        label: 'Abrir módulo',
        href: '/projects',
        helperText: 'Selecciona un proyecto para abrir el flujo real de este módulo.',
        variant: 'primary',
      }
    case 'pipeline_builder':
      return {
        label: 'Abrir módulo',
        href: '/cid/pipeline-builder',
        helperText: 'Disponible como espacio operativo transversal dentro de CID.',
        variant: 'primary',
      }
    case 'legal_documents':
      return {
        label: 'Abrir módulo',
        href: '/documents',
        helperText: 'La entrada actual es el workspace documental común del entorno CID.',
        variant: 'primary',
      }
    default:
      return {
        label: 'Próximamente',
        disabled: true,
        helperText: 'La pantalla comercial existe, pero su workspace dedicado llegará en el siguiente bloque UX.',
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
  const { user } = useAuthStore()
  const catalogQuery = useModuleCatalog()
  const myModulesQuery = useMyModules()

  useSeo({
    title: 'Módulos CID | Suite modular vendible',
    description: 'Explora la suite modular de CID Core y activa módulos de IA para desarrollo, guion, storyboard, presupuesto, financiación, pitch y planificación.',
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
  const planLabel = formatPlanLabel(planName)
  const myModulesError = myModulesQuery.error
    ? getApiErrorMessage(myModulesQuery.error, 'No pudimos resolver tu acceso por plan en este momento.')
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
        <p className="editorial-kicker text-rose-200">Catálogo CID</p>
        <h1 className="mt-4 text-3xl font-semibold text-white">No pudimos cargar el catálogo modular</h1>
        <p className="mt-4 max-w-2xl text-slate-300">
          {getApiErrorMessage(catalogQuery.error, 'Revisa la conexión con el backend y vuelve a intentarlo.')}
        </p>
        <div className="mt-6 flex gap-3">
          <button type="button" onClick={() => catalogQuery.refetch()} className="btn-primary">
            Reintentar
          </button>
          <Link to="/projects" className="btn-secondary">
            Volver a proyectos
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
              Suite modular CID
            </div>
            <h1 className="mt-6 text-4xl font-semibold tracking-tight text-white md:text-5xl">Módulos CID</h1>
              <p className="mt-4 max-w-3xl text-lg leading-8 text-slate-200">
              Activa los módulos visibles de CID Core para guion, storyboard, visual bible, presupuesto, financiación, pitch y previs básica.
              </p>
              <p className="mt-4 max-w-3xl text-sm leading-7 text-slate-400">
              Esta capa comercial prioriza el alcance de preproducción cinematográfica. Los laboratorios de dubbing, sound post y restoration se mantienen fuera del catálogo visible al cliente.
              </p>
            </div>

          <div className="grid gap-4 sm:grid-cols-3 xl:min-w-[440px]">
            <div className="rounded-[1.4rem] border border-white/8 bg-white/[0.045] p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Plan actual</p>
              <div className="mt-3 flex items-center gap-3">
                <span className={clsx('badge', planBadgeTone[planName] || 'badge-free')}>
                  {planLabel}
                </span>
                <span className="text-sm text-slate-400">Acceso comercial vigente</span>
              </div>
            </div>

            <div className="rounded-[1.4rem] border border-white/8 bg-white/[0.045] p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Disponibles</p>
              <p className="mt-3 text-3xl font-semibold text-white">{myModulesQuery.data?.total_available ?? availableModules.length}</p>
              <p className="mt-2 text-sm text-slate-400">Listos para abrir o activar por proyecto.</p>
            </div>

            <div className="rounded-[1.4rem] border border-white/8 bg-white/[0.045] p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Para ampliar</p>
              <p className="mt-3 text-3xl font-semibold text-white">{myModulesQuery.data?.total_locked ?? lockedModules.length}</p>
              <p className="mt-2 text-sm text-slate-400">Bloques activables por plan o activación comercial.</p>
            </div>
          </div>
        </div>
      </section>

      {myModulesError ? (
        <div className="rounded-[1.4rem] border border-cyan-400/20 bg-cyan-500/10 px-5 py-4 text-sm text-cyan-50">
          <div className="flex items-start gap-3">
            <Waypoints className="mt-0.5 h-5 w-5 text-cyan-200" />
            <div>
              <p className="font-semibold">Modo informativo activo</p>
              <p className="mt-1 text-cyan-100/80">
                {myModulesError} Mostramos el catálogo general mientras se recupera tu acceso por plan.
              </p>
            </div>
          </div>
        </div>
      ) : null}

      <section className="rounded-[1.8rem] border border-cyan-400/20 bg-cyan-500/8 p-6 md:p-7 text-sm text-cyan-50">
        <p className="font-semibold text-cyan-100">Fuera de CID Core</p>
        <p className="mt-2 max-w-3xl text-cyan-100/80">
          Dubbing, sound post y restoration se conservan como laboratorios o futuros productos separados. No se muestran al cliente final dentro del catálogo modular de CID Core.
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
            <p className="editorial-kicker text-slate-300">Acceso por plan</p>
            <h2 className="mt-2 text-2xl font-semibold text-white">Cargando disponibilidad modular</h2>
          </div>
          <LoadingGrid />
        </section>
      ) : null}

      {moduleView.length === 0 ? (
        <div className="card rounded-[1.8rem] p-10 text-center">
          <Lock className="mx-auto h-12 w-12 text-slate-500" />
          <h2 className="mt-4 text-2xl font-semibold text-white">Aún no hay módulos visibles</h2>
          <p className="mt-3 text-slate-400">Cuando el catálogo comercial esté publicado, aparecerá aquí para tu organización.</p>
        </div>
      ) : null}

      {!myModulesError && availableModules.length > 0 ? (
        <section className="space-y-5">
          <div className="flex items-end justify-between gap-4">
            <div>
              <p className="editorial-kicker text-emerald-200">Acceso activo</p>
              <h2 className="mt-2 text-2xl font-semibold text-white">Disponibles en tu plan</h2>
            </div>
            <span className="text-sm text-slate-400">{availableModules.length} módulo(s)</span>
          </div>
          <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
            {availableModules.map((module) => (
              <ModuleCard
                key={module.key}
                module={module}
                enabled={module.enabled}
                action={resolveModuleAction(module)}
                lockedReasonLabel={getLockedReasonLabel(module.locked_reason)}
              />
            ))}
          </div>
        </section>
      ) : null}

      {!myModulesError && lockedModules.length > 0 ? (
        <section className="space-y-5">
          <div className="flex items-end justify-between gap-4">
            <div>
              <p className="editorial-kicker text-amber-200">Expansión comercial</p>
              <h2 className="mt-2 text-2xl font-semibold text-white">Bloqueados / disponibles para ampliar</h2>
            </div>
            <span className="text-sm text-slate-400">{lockedModules.length} módulo(s)</span>
          </div>
          <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
            {lockedModules.map((module) => (
              <ModuleCard
                key={module.key}
                module={module}
                enabled={module.enabled}
                action={resolveModuleAction(module)}
                lockedReasonLabel={getLockedReasonLabel(module.locked_reason)}
              />
            ))}
          </div>
        </section>
      ) : null}

      {myModulesError && informationalModules.length > 0 ? (
        <section className="space-y-5">
          <div>
            <p className="editorial-kicker text-slate-300">Catálogo general</p>
            <h2 className="mt-2 text-2xl font-semibold text-white">Módulos visibles de la suite CID</h2>
          </div>
          <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
            {informationalModules.map((module) => (
              <ModuleCard
                key={module.key}
                module={module}
                enabled={module.enabled}
                action={{
                  label: 'Solicitar activación',
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
            <p className="editorial-kicker text-amber-200">Activación comercial</p>
            <h2 className="mt-2 text-2xl font-semibold text-white">¿Necesitas ampliar la suite?</h2>
            <p className="mt-3 text-sm leading-7 text-slate-400">
              Por ahora no mostramos pricing final por módulo. La activación se resuelve por plan, por pack o por validación comercial según el tipo de workflow y la dependencia operativa de cada módulo.
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <Link to="/plans" className="btn-primary">Ver planes</Link>
            <Link to="/pricing" className="btn-secondary">Solicitar activación</Link>
          </div>
        </div>
      </section>
    </div>
  )
}
