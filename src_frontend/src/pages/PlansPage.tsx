import { usePlansCatalog, useUserPlanStatus } from '@/hooks'
import { userApi } from '@/api'
import { useAuthStore } from '@/store'
import { useQueryClient } from '@tanstack/react-query'
import { Check, Crown, Star, Zap } from 'lucide-react'
import clsx from 'clsx'
import { useState } from 'react'

function getApiMessage(err: unknown, fallback: string) {
  const detail = (err as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (detail && typeof detail === 'object' && 'message' in detail) {
    return String((detail as { message?: unknown }).message || fallback)
  }
  return fallback
}

export default function PlansPage() {
  const queryClient = useQueryClient()
  const { user, refreshProfile } = useAuthStore()
  const { data: plans, isLoading } = usePlansCatalog()
  const { data: currentPlanStatus } = useUserPlanStatus(user?.user_id || '', user?.plan || 'free')
  const [updatingPlan, setUpdatingPlan] = useState<string | null>(null)
  const [planMessage, setPlanMessage] = useState('')
  const [planError, setPlanError] = useState('')

  if (isLoading) {
    return (
      <div className="space-y-8">
        <div className="text-center">
          <div className="h-10 w-64 bg-slate-700 rounded mx-auto mb-4 animate-pulse" />
          <div className="h-6 w-96 bg-slate-700/50 rounded mx-auto animate-pulse" />
        </div>
        <div className="grid grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="card animate-pulse">
              <div className="h-8 w-20 bg-slate-700 rounded mb-4" />
              <div className="h-4 w-full bg-slate-700 rounded" />
            </div>
          ))}
        </div>
      </div>
    )
  }

  const currentPlan = plans?.find((plan) => plan.id === user?.plan)

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="heading-lg flex items-center justify-center gap-3">
          <Crown className="w-7 h-7 text-amber-400" />
          Planes comerciales
        </h1>
        <p className="text-slate-400 mt-2">Activa el plan adecuado para tu organizacion y deja la demo operativa al instante.</p>
        <p className="text-xs text-slate-500 mt-2">Sprint 13 usa activacion interna inmediata. No se procesan pagos reales todavia.</p>
      </div>

      {planMessage && (
        <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-300">
          {planMessage}
        </div>
      )}

      {planError && (
        <div className="rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-300">
          {planError}
        </div>
      )}

      {currentPlanStatus && (
        <div className="card bg-gradient-to-r from-amber-500/5 to-transparent border-amber-500/20">
          <div className="flex items-start justify-between gap-6">
            <div>
              <p className="text-sm text-slate-400 mb-1">Plan actual</p>
              <div className="flex items-center gap-3">
                <span className="text-2xl font-bold text-white">{currentPlan?.display_name}</span>
                <span className={clsx(
                  'badge',
                  user?.plan === 'studio' ? 'badge-studio' :
                  user?.plan === 'enterprise' ? 'badge-enterprise' :
                  'badge-free'
                )}>
                  {user?.plan}
                </span>
              </div>
              <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                <div className="rounded-xl bg-dark-300/50 p-3">
                  <p className="text-slate-500">Proyectos</p>
                  <p className="text-white font-semibold">
                    {currentPlanStatus.projects_count}/{currentPlanStatus.max_projects === -1 ? '∞' : currentPlanStatus.max_projects}
                  </p>
                </div>
                <div className="rounded-xl bg-dark-300/50 p-3">
                  <p className="text-slate-500">Jobs</p>
                  <p className="text-white font-semibold">
                    {currentPlanStatus.jobs_count}/{currentPlanStatus.max_total_jobs === -1 ? '∞' : currentPlanStatus.max_total_jobs}
                  </p>
                </div>
                <div className="rounded-xl bg-dark-300/50 p-3">
                  <p className="text-slate-500">Analisis</p>
                  <p className="text-white font-semibold">
                    {currentPlanStatus.analyses_count}/{currentPlanStatus.max_analyses === -1 ? '∞' : currentPlanStatus.max_analyses}
                  </p>
                </div>
                <div className="rounded-xl bg-dark-300/50 p-3">
                  <p className="text-slate-500">Storyboards</p>
                  <p className="text-white font-semibold">
                    {currentPlanStatus.storyboards_count}/{currentPlanStatus.max_storyboards === -1 ? '∞' : currentPlanStatus.max_storyboards}
                  </p>
                </div>
              </div>
            </div>
            <div className="text-right">
              <p className="text-sm text-slate-400">Capacidad activa</p>
              <p className="text-2xl font-bold text-white">
                {currentPlanStatus.active_jobs + currentPlanStatus.queued_jobs}
                <span className="text-sm text-slate-500 font-normal">
                  /{
                    currentPlanStatus.max_active_jobs === -1 && currentPlanStatus.max_queued_jobs === -1
                      ? '∞'
                      : currentPlanStatus.max_active_jobs + currentPlanStatus.max_queued_jobs
                  }
                </span>
              </p>
              <p className={`mt-3 text-sm font-medium ${currentPlanStatus.export_json ? 'text-green-400' : 'text-amber-400'}`}>
                {currentPlanStatus.export_json ? 'Export JSON habilitado' : 'Upgrade necesario para exportar'}
              </p>
              <p className={`mt-1 text-xs font-medium ${currentPlanStatus.export_zip ? 'text-green-400' : 'text-slate-500'}`}>
                {currentPlanStatus.export_zip ? 'ZIP comercial incluido' : 'ZIP disponible desde planes con export'}
              </p>
              {currentPlanStatus.recommended_upgrade && (
                <p className="mt-1 text-xs text-slate-500">
                  Upgrade recomendado: <span className="text-amber-400 capitalize">{currentPlanStatus.recommended_upgrade}</span>
                </p>
              )}
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-4 gap-4">
        {plans?.map((plan) => {
          const isCurrentPlan = plan.id === user?.plan
          const isPopular = plan.id === 'studio'

          return (
            <div
              key={plan.id}
              className={clsx(
                'card relative transition-all duration-300',
                isPopular && 'border-amber-500/40 shadow-lg shadow-amber-500/10',
                isCurrentPlan && 'ring-2 ring-amber-500/30'
              )}
            >
              {isPopular && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 bg-gradient-to-r from-amber-500 to-amber-600 rounded-full text-xs font-semibold text-black flex items-center gap-1 shadow-lg">
                  <Star className="w-3 h-3" />
                  Recomendado
                </div>
              )}

              <div className="text-center mb-6 pt-2">
                <h3 className="text-xl font-bold text-white">{plan.display_name}</h3>
                <div className="mt-3">
                  <span className="text-4xl font-bold text-white">${plan.price}</span>
                  <span className="text-slate-400">/{plan.billing_period === 'monthly' ? 'mes' : plan.billing_period}</span>
                </div>
              </div>

              <div className="space-y-3 mb-6 p-4 rounded-xl bg-dark-300/50">
                <div className="flex justify-between text-sm">
                  <span className="text-slate-400">Jobs activos</span>
                  <span className="text-white font-medium">{plan.limits.max_active_jobs === -1 ? '∞' : plan.limits.max_active_jobs}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-400">Jobs en cola</span>
                  <span className="text-white font-medium">{plan.limits.max_queued_jobs === -1 ? '∞' : plan.limits.max_queued_jobs}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-400">Proyectos</span>
                  <span className="text-white font-medium">{plan.limits.max_projects === -1 ? '∞' : plan.limits.max_projects}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-400">Jobs totales</span>
                  <span className="text-white font-medium">{plan.limits.max_total_jobs === -1 ? '∞' : plan.limits.max_total_jobs}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-400">Analisis</span>
                  <span className="text-white font-medium">{plan.limits.max_analyses === -1 ? '∞' : plan.limits.max_analyses}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-400">Storyboards</span>
                  <span className="text-white font-medium">{plan.limits.max_storyboards === -1 ? '∞' : plan.limits.max_storyboards}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-400">Prioridad</span>
                  <span className="text-amber-400 font-medium">Nivel {plan.limits.priority_score}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-400">Export ZIP</span>
                  <span className={clsx('font-medium', plan.limits.export_zip ? 'text-green-400' : 'text-slate-500')}>
                    {plan.limits.export_zip ? 'Incluido' : 'No incluido'}
                  </span>
                </div>
              </div>

              <div className="pt-4 border-t border-white/5">
                <p className="text-sm font-medium text-slate-300 mb-3">Incluye:</p>
                <ul className="space-y-2">
                  {plan.features.map((feature) => (
                    <li key={feature} className="flex items-center gap-2 text-sm">
                      <div className="w-4 h-4 rounded-full bg-amber-500/10 flex items-center justify-center">
                        <Check className="w-3 h-3 text-amber-400" />
                      </div>
                      <span className="text-slate-300">{feature.replace(/_/g, ' ')}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="mt-4 pt-4 border-t border-white/5">
                <p className="text-xs text-slate-500 mb-2">Tipos permitidos:</p>
                <div className="flex flex-wrap gap-1">
                  {plan.limits.allowed_task_types.map((type) => (
                    <span key={type} className="px-2 py-1 bg-white/5 rounded text-xs text-slate-400 capitalize">
                      {type}
                    </span>
                  ))}
                </div>
              </div>

              <button
                onClick={async () => {
                  if (!user || isCurrentPlan) return
                  setPlanMessage('')
                  setPlanError('')
                  setUpdatingPlan(plan.id)
                  try {
                    const result = await userApi.updatePlan(user.user_id, plan.id)
                    await refreshProfile()
                    await queryClient.invalidateQueries({ queryKey: ['userPlan'] })
                    setPlanMessage(result.message)
                  } catch (err: unknown) {
                    setPlanError(getApiMessage(err, 'No se pudo activar el plan'))
                  } finally {
                    setUpdatingPlan(null)
                  }
                }}
                className={clsx(
                  'w-full mt-6 py-3 rounded-xl font-medium transition-all flex items-center justify-center gap-2',
                  isCurrentPlan
                    ? 'bg-white/5 text-slate-400 cursor-not-allowed'
                    : isPopular
                      ? 'btn-primary'
                      : 'btn-secondary'
                )}
                disabled={isCurrentPlan || updatingPlan === plan.id}
              >
                {isCurrentPlan ? (
                  'Plan actual'
                ) : updatingPlan === plan.id ? (
                  'Activando...'
                ) : (
                  <>
                    <Zap className="w-4 h-4" />
                    Activar plan
                  </>
                )}
              </button>
            </div>
          )
        })}
      </div>
    </div>
  )
}
