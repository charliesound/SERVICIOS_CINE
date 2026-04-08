import { usePlansCatalog, useUserPlanStatus } from '@/hooks'
import { useAuthStore } from '@/store'
import { Check, Star, Crown, Zap } from 'lucide-react'
import clsx from 'clsx'

export default function PlansPage() {
  const { user } = useAuthStore()
  const { data: plans, isLoading } = usePlansCatalog()
  const { data: currentPlanStatus } = useUserPlanStatus(user?.user_id || '', user?.plan || 'free')

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

  const currentPlan = plans?.find(p => p.id === user?.plan)

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="heading-lg flex items-center justify-center gap-3">
          <Crown className="w-7 h-7 text-amber-400" />
          Pricing Plans
        </h1>
        <p className="text-slate-400 mt-2">Choose the plan that fits your creative needs</p>
      </div>

      {/* Current Plan Status */}
      {currentPlanStatus && (
        <div className="card bg-gradient-to-r from-amber-500/5 to-transparent border-amber-500/20">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-400 mb-1">Current Plan</p>
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
            </div>
            <div className="text-right">
              <p className="text-sm text-slate-400">Usage</p>
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
            </div>
          </div>
        </div>
      )}

      {/* Plans Grid */}
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
                  Popular
                </div>
              )}

              <div className="text-center mb-6 pt-2">
                <h3 className="text-xl font-bold text-white">{plan.display_name}</h3>
                <div className="mt-3">
                  <span className="text-4xl font-bold text-white">${plan.price}</span>
                  <span className="text-slate-400">/{plan.billing_period === 'monthly' ? 'mo' : plan.billing_period}</span>
                </div>
              </div>

              {/* Limits */}
              <div className="space-y-3 mb-6 p-4 rounded-xl bg-dark-300/50">
                <div className="flex justify-between text-sm">
                  <span className="text-slate-400">Active Jobs</span>
                  <span className="text-white font-medium">
                    {plan.limits.max_active_jobs === -1 ? '∞' : plan.limits.max_active_jobs}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-400">Queued Jobs</span>
                  <span className="text-white font-medium">
                    {plan.limits.max_queued_jobs === -1 ? '∞' : plan.limits.max_queued_jobs}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-400">Priority</span>
                  <span className="text-amber-400 font-medium">Level {plan.limits.priority_score}</span>
                </div>
              </div>

              {/* Features */}
              <div className="pt-4 border-t border-white/5">
                <p className="text-sm font-medium text-slate-300 mb-3">Includes:</p>
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

              {/* Task Types */}
              <div className="mt-4 pt-4 border-t border-white/5">
                <p className="text-xs text-slate-500 mb-2">Allowed types:</p>
                <div className="flex flex-wrap gap-1">
                  {plan.limits.allowed_task_types.map((type) => (
                    <span key={type} className="px-2 py-1 bg-white/5 rounded text-xs text-slate-400 capitalize">
                      {type}
                    </span>
                  ))}
                </div>
              </div>

              <button
                className={clsx(
                  'w-full mt-6 py-3 rounded-xl font-medium transition-all flex items-center justify-center gap-2',
                  isCurrentPlan
                    ? 'bg-white/5 text-slate-400 cursor-not-allowed'
                    : isPopular
                      ? 'btn-primary'
                      : 'btn-secondary'
                )}
                disabled={isCurrentPlan}
              >
                {isCurrentPlan ? (
                  'Current Plan'
                ) : (
                  <>
                    <Zap className="w-4 h-4" />
                    Select Plan
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