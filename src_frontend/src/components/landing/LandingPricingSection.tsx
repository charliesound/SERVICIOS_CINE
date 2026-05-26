import { ArrowRight, Check, ChevronRight, Cpu, Coins, Zap, Sparkles } from 'lucide-react'
import { Link } from 'react-router-dom'
import clsx from 'clsx'
import LandingReveal from '@/components/landing/LandingReveal'
import LandingSectionHeading from '@/components/landing/LandingSectionHeading'

interface ExtraCreditPack {
  amount: number | null
  price: string
}

interface SetupFee {
  name: string
  price: string
}

interface Plan {
  id: string
  name: string
  price: string
  interval: string
  credits: number | null
  maxProjects: number | null
  features: readonly string[]
  extraCredits: ExtraCreditPack | readonly ExtraCreditPack[] | null
  badge: string | null
  ctaLabel: string
  highlighted: boolean
  setupFees?: readonly SetupFee[]
}

interface CreditExplainContent {
  title: string
  subtitle: string
  rules: readonly string[]
}

interface ExtraPackEntry {
  plan: string
  amount?: number
  desc?: string
  price: string
}

interface ExtraPacksContent {
  title: string
  description: string
  packs: readonly ExtraPackEntry[]
}

interface PricingContent {
  eyebrow: string
  title: string
  description: string
  tagline: string
  subtitle: string
  plans: readonly Plan[]
  creditExplain: CreditExplainContent
  extraPacks: ExtraPacksContent
}

interface LandingPricingSectionProps {
  content: PricingContent
}

function PlanCard({ plan, index }: { plan: Plan; index: number }) {
  const extras = plan.extraCredits
    ? Array.isArray(plan.extraCredits)
      ? plan.extraCredits
      : [plan.extraCredits]
    : []

  return (
    <LandingReveal delay={index * 60}>
      <div
        className={clsx(
          'relative flex h-full flex-col rounded-[2rem] border p-6 backdrop-blur-xl transition-all duration-500 sm:p-7',
          plan.highlighted
            ? 'border-amber-400/20 bg-gradient-to-b from-amber-400/[0.07] to-white/[0.03] shadow-[0_20px_80px_rgba(245,158,11,0.10)]'
            : 'border-white/10 bg-white/[0.04] hover:border-white/20 hover:bg-white/[0.06]',
        )}
      >
        {/* Badge */}
        {plan.badge && (
          <span
            className={clsx(
              'absolute -top-3 left-6 rounded-full px-4 py-1 text-[11px] font-semibold uppercase tracking-[0.18em] shadow-lg',
              plan.badge === 'Más recomendado'
                ? 'bg-gradient-to-r from-amber-400 to-amber-500 text-black'
                : plan.badge === 'Para productoras'
                  ? 'bg-gradient-to-r from-violet-400 to-fuchsia-500 text-white'
                  : 'bg-white/10 text-slate-200',
            )}
          >
            {plan.badge}
          </span>
        )}

        {/* Header */}
        <div className="flex items-start justify-between">
          <div>
            <p className="text-lg font-semibold text-white">{plan.name}</p>
            <div className="mt-2 flex items-baseline gap-1">
              <span className="font-display text-4xl font-semibold text-white">
                {plan.price}
              </span>
              <span className="text-sm text-slate-400">{plan.interval}</span>
            </div>
          </div>
        </div>

        {/* Credits / projects */}
        <div className="mt-4 flex gap-4 text-sm text-slate-300">
          {plan.credits && (
            <span className="flex items-center gap-1.5">
              <Cpu className="h-3.5 w-3.5 text-amber-300" />
              {plan.credits.toLocaleString()} créditos/mes
            </span>
          )}
          {plan.maxProjects && (
            <span className="flex items-center gap-1.5">
              <span className="h-3.5 w-3.5 rounded border border-slate-500 text-center text-[10px] leading-3 text-slate-400">
                P
              </span>
              {plan.maxProjects} proyecto{plan.maxProjects > 1 ? 's' : ''} activo{plan.maxProjects > 1 ? 's' : ''}
            </span>
          )}
          {plan.credits === null && plan.maxProjects === null && (
            <span className="text-xs text-slate-400">Configuración a medida</span>
          )}
        </div>

        {/* Features */}
        <ul className="mt-6 flex-1 space-y-3">
          {plan.features.map((feature) => (
            <li key={feature} className="flex items-start gap-3 text-sm leading-6 text-slate-300">
              <Check className="mt-0.5 h-4 w-4 shrink-0 text-amber-400" />
              <span>{feature}</span>
            </li>
          ))}
        </ul>

        {/* Extra credits */}
        {extras.length > 0 && (
          <div className="mt-5 rounded-xl border border-white/5 bg-white/[0.03] p-3">
            <p className="text-[11px] uppercase tracking-[0.18em] text-slate-500">
              Créditos extra
            </p>
            {extras.map((ex) => (
              <p key={`${ex.amount ?? 'custom'}-${ex.price}`} className="mt-1 text-sm text-slate-300">
                {ex.amount ? `+${ex.amount.toLocaleString()} por ${ex.price} €` : ex.price}
              </p>
            ))}
          </div>
        )}

        {/* Enterprise setup fees */}
        {plan.setupFees && plan.setupFees.length > 0 && (
          <div className="mt-5 rounded-xl border border-white/5 bg-white/[0.03] p-3">
            <p className="text-[11px] uppercase tracking-[0.18em] text-slate-500">
              Setup recomendado
            </p>
            {plan.setupFees.map((sf) => (
              <p key={sf.name} className="mt-1 flex justify-between text-sm text-slate-300">
                <span className="text-slate-400">{sf.name}</span>
                <span className="font-medium text-white">{sf.price} €</span>
              </p>
            ))}
          </div>
        )}

        {/* CTA */}
        <div className="mt-6">
          {plan.id === 'enterprise' ? (
            <Link
              to="/pricing"
              className="landing-cta-secondary inline-flex w-full items-center justify-center gap-2"
            >
              {plan.ctaLabel}
              <ChevronRight className="h-4 w-4" />
            </Link>
          ) : (
            <Link
              to="/register/demo"
              className={clsx(
                'inline-flex w-full items-center justify-center gap-2 rounded-full px-6 py-3.5 text-sm font-semibold transition-all duration-300',
                plan.highlighted
                  ? 'bg-gradient-to-r from-amber-300 to-amber-500 text-black hover:-translate-y-0.5 hover:shadow-[0_14px_40px_rgba(245,158,11,0.22)]'
                  : 'border border-white/10 bg-white/[0.04] text-white hover:-translate-y-0.5 hover:border-white/20',
              )}
            >
              {plan.ctaLabel}
              <ArrowRight className="h-4 w-4" />
            </Link>
          )}
        </div>
      </div>
    </LandingReveal>
  )
}

export default function LandingPricingSection({ content }: LandingPricingSectionProps) {
  const mainPlans = content.plans.filter((p) => p.id !== 'premium' && p.id !== 'enterprise')
  const premiumPlans = content.plans.filter((p) => p.id === 'premium' || p.id === 'enterprise')

  return (
    <section id="pricing" className="relative border-y border-white/10 bg-[#09111c]/76 py-24">
      <div className="mx-auto max-w-7xl px-5 md:px-6 lg:px-8">
        {/* Header */}
        <LandingReveal>
          <LandingSectionHeading
            eyebrow={content.eyebrow}
            title={content.title}
            description={content.description}
          />
        </LandingReveal>

        {/* Tagline */}
        <LandingReveal delay={60}>
          <div className="mx-auto mt-8 max-w-4xl space-y-4 text-center">
            <p className="font-display text-2xl font-semibold leading-tight text-white md:text-3xl">
              {content.tagline}
            </p>
            <p className="text-base leading-7 text-slate-300 md:text-lg">
              {content.subtitle}
            </p>
          </div>
        </LandingReveal>

        {/* Plan cards — main row (Starter, Pro, Studio) */}
        <div className="mt-14 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {mainPlans.map((plan, i) => (
            <PlanCard key={plan.id} plan={plan} index={i} />
          ))}
        </div>

        {/* Plan cards — premium row (Premium, Enterprise) */}
        <div className="mt-6 grid gap-6 md:grid-cols-2">
          {premiumPlans.map((plan, i) => (
            <PlanCard key={plan.id} plan={plan} index={i + mainPlans.length} />
          ))}
        </div>

        {/* Bottom CTAs */}
        <LandingReveal delay={120}>
          <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
            <Link to="/register/demo" className="landing-cta-primary text-base">
              Solicitar demo
              <ArrowRight className="h-4 w-4" />
            </Link>
            <Link to="/solutions/cid" className="landing-cta-secondary text-base">
              Explorar CID
              <ChevronRight className="h-4 w-4" />
            </Link>
            <Link to="/pricing" className="landing-cta-ghost text-base">
              Ver todos los precios
            </Link>
          </div>
        </LandingReveal>

        {/* Credit explain */}
        <LandingReveal delay={80}>
          <div className="landing-panel mt-20 rounded-[2rem] p-6 sm:p-8">
            <div className="flex items-center gap-3">
              <Cpu className="h-5 w-5 text-amber-300" />
              <p className="editorial-kicker text-amber-300/90">{content.creditExplain.title}</p>
            </div>
            <p className="mt-4 max-w-3xl text-sm leading-7 text-slate-300">
              {content.creditExplain.subtitle}
            </p>
            <ul className="mt-5 grid gap-3 sm:grid-cols-2">
              {content.creditExplain.rules.map((rule) => (
                <li
                  key={rule}
                  className="flex items-start gap-3 rounded-xl border border-white/5 bg-white/[0.03] px-4 py-3 text-sm leading-6 text-slate-300"
                >
                  <Zap className="mt-0.5 h-4 w-4 shrink-0 text-amber-400/70" />
                  <span>{rule}</span>
                </li>
              ))}
            </ul>
          </div>
        </LandingReveal>

        {/* Extra packs */}
        <LandingReveal delay={100}>
          <div className="landing-panel mt-6 rounded-[2rem] p-6 sm:p-8">
            <div className="flex items-center gap-3">
              <Coins className="h-5 w-5 text-amber-300" />
              <p className="editorial-kicker text-amber-300/90">{content.extraPacks.title}</p>
            </div>
            <p className="mt-4 max-w-3xl text-sm leading-7 text-slate-300">
              {content.extraPacks.description}
            </p>
            <div className="mt-5 overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-white/10 text-[11px] uppercase tracking-[0.18em] text-slate-500">
                    <th className="pb-2 pr-4 font-medium">Plan</th>
                    <th className="pb-2 pr-4 font-medium">Créditos extra</th>
                    <th className="pb-2 font-medium">Precio</th>
                  </tr>
                </thead>
                <tbody>
                  {content.extraPacks.packs.map((pack) => (
                    <tr key={`${pack.plan}-${pack.amount ?? pack.desc ?? pack.price}`} className="border-b border-white/5 last:border-0">
                      <td className="py-3 pr-4 text-white">{pack.plan}</td>
                      <td className="py-3 pr-4 text-slate-300">
                        {pack.amount ? `+${pack.amount.toLocaleString()} créditos` : pack.desc ?? '-'}
                      </td>
                      <td className="py-3 font-medium text-white">{pack.price}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="mt-5 flex items-center gap-2 text-xs text-slate-500">
              <Sparkles className="h-3 w-3" />
              <span>Los créditos extra tienen validez de 90 días desde su compra.</span>
            </div>
          </div>
        </LandingReveal>
      </div>
    </section>
  )
}
