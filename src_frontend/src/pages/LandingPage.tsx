import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  ArrowRight,
  Check,
  ChevronRight,
  HelpCircle,
  LayoutDashboard,
  LogOut,
  Play,
  ShieldCheck,
  X,
} from 'lucide-react'
import LandingAmbientScene from '@/components/landing/LandingAmbientScene'
import LandingControlCenter from '@/components/landing/LandingControlCenter'
import LandingPipelineVisual from '@/components/landing/LandingPipelineVisual'
import LandingReveal from '@/components/landing/LandingReveal'
import LandingShowcasePlaceholder from '@/components/landing/LandingShowcasePlaceholder'
import { landingContent } from '@/data/landingContent'
import { getPrimaryCIDTarget, useAuthStore } from '@/store'

function SectionHeading({
  eyebrow,
  title,
  description,
  align = 'left',
}: {
  eyebrow: string
  title: string
  description: string
  align?: 'left' | 'center'
}) {
  return (
    <div className={align === 'center' ? 'mx-auto max-w-3xl text-center' : 'max-w-3xl'}>
      <p className="editorial-kicker text-amber-300/90">{eyebrow}</p>
      <h2 className="mt-4 font-display text-4xl font-semibold leading-[0.92] text-white md:text-6xl">{title}</h2>
      <p className="mt-5 text-base leading-8 text-slate-300 md:text-lg">{description}</p>
    </div>
  )
}

function Surface({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return <div className={`landing-panel ${className}`}>{children}</div>
}

function ActionButton({
  destination,
  variant,
  children,
}: {
  destination: string
  variant: 'primary' | 'secondary' | 'ghost'
  children: React.ReactNode
}) {
  const baseClassName =
    variant === 'primary'
      ? 'landing-cta-primary'
      : variant === 'secondary'
        ? 'landing-cta-secondary'
        : 'landing-cta-ghost'

  if (destination.startsWith('#')) {
    return (
      <a href={destination} className={baseClassName}>
        {children}
      </a>
    )
  }

  return (
    <Link to={destination} className={baseClassName}>
      {children}
    </Link>
  )
}

export default function LandingPage() {
  const { isAuthenticated, user } = useAuthStore()
  const cidTarget = getPrimaryCIDTarget(user)
  const [activeShowcase, setActiveShowcase] = useState(0)
  const shellRef = useRef<HTMLDivElement | null>(null)

  const {
    header,
    hero,
    controlCenter,
    trust,
    about,
    pipeline,
    modules,
    comparison,
    useCases,
    showcase,
    finalCta,
    faq,
    footer,
    proofIcons,
  } = landingContent

  const exploreCidTarget = isAuthenticated ? cidTarget : '/register/cid'
  const requestDemoTarget = '/register/demo'
  const activeShowcaseItem = showcase.items[activeShowcase]

  useEffect(() => {
    const shell = shellRef.current
    if (!shell) return

    let rafId = 0

    const updateParallax = () => {
      rafId = 0
      const scrollY = window.scrollY || 0
      shell.style.setProperty('--landing-parallax', `${Math.min(scrollY * 0.08, 48)}px`)
      shell.style.setProperty('--landing-parallax-soft', `${Math.min(scrollY * 0.04, 24)}px`)
    }

    const onScroll = () => {
      if (rafId) return
      rafId = window.requestAnimationFrame(updateParallax)
    }

    updateParallax()
    window.addEventListener('scroll', onScroll, { passive: true })

    return () => {
      window.removeEventListener('scroll', onScroll)
      if (rafId) {
        window.cancelAnimationFrame(rafId)
      }
    }
  }, [])

  return (
    <div ref={shellRef} className="landing-shell min-h-screen text-white">
      <LandingAmbientScene />
      <div className="landing-noise" />
      <div className="landing-backdrop" />

      <header className="fixed inset-x-0 top-0 z-50 border-b border-white/10 bg-[#07111d]/55 backdrop-blur-2xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-5 py-4 md:px-6 lg:px-8">
          <Link to="/" className="flex items-center gap-3">
            <img src="/assets/ailinkcinema-logo.png" alt="AILinkCinema" className="h-11 w-11 rounded-2xl object-cover shadow-[0_0_32px_rgba(245,158,11,0.22)]" />
            <div>
              <p className="text-lg font-semibold tracking-tight text-white">AILinkCinema</p>
              <p className="font-mono text-[11px] uppercase tracking-[0.28em] text-slate-400">premium CID experience</p>
            </div>
          </Link>

          <nav className="hidden items-center gap-7 text-sm text-slate-300 xl:flex">
            {header.nav.map((item) => (
              <a key={item.href} href={item.href} className="transition-colors duration-300 hover:text-white">
                {item.label}
              </a>
            ))}
          </nav>

          <div className="flex items-center gap-2 md:gap-3">
            {!isAuthenticated && (
              <Link to="/login" className="hidden rounded-full border border-white/10 px-4 py-2 text-sm text-slate-200 transition-colors hover:border-white/20 hover:bg-white/5 sm:inline-flex">
                Iniciar sesion
              </Link>
            )}

            {isAuthenticated ? (
              <>
                <Link to={cidTarget} className="landing-cta-secondary hidden sm:inline-flex">
                  <LayoutDashboard className="h-4 w-4" />
                  Entrar a CID
                </Link>
                <button
                  onClick={() => {
                    useAuthStore.getState().logout()
                    window.location.href = '/'
                  }}
                  className="inline-flex items-center gap-2 rounded-full px-3 py-2 text-sm text-slate-400 transition-colors hover:text-red-200"
                >
                  <LogOut className="h-4 w-4" />
                  Salir
                </button>
              </>
            ) : (
              <ActionButton destination={exploreCidTarget} variant="primary">
                Explorar CID
                <ArrowRight className="h-4 w-4" />
              </ActionButton>
            )}
          </div>
        </div>
      </header>

      <main>
        <section className="relative overflow-hidden pt-28 md:pt-36 lg:pt-40">
          <div className="landing-hero-radial" />
          <div className="mx-auto grid max-w-7xl gap-14 px-5 pb-24 md:px-6 lg:grid-cols-[1.02fr_0.98fr] lg:items-center lg:px-8 lg:pb-28">
            <div className="relative z-10">
              <LandingReveal>
                <div className="inline-flex items-center gap-2 rounded-full border border-amber-300/20 bg-amber-300/10 px-4 py-2 font-mono text-[11px] uppercase tracking-[0.28em] text-amber-200">
                  <Play className="h-3.5 w-3.5" />
                  {hero.eyebrow}
                </div>
              </LandingReveal>

              <LandingReveal delay={90} className="mt-7">
                <h1 className="max-w-5xl font-display text-5xl font-semibold leading-[0.88] tracking-[-0.04em] text-white sm:text-6xl md:text-7xl xl:text-[6.2rem]">
                  {hero.title}
                </h1>
              </LandingReveal>

              <LandingReveal delay={170} className="mt-6 max-w-2xl">
                <p className="text-lg font-medium leading-8 text-slate-100 md:text-2xl md:leading-10">{hero.subtitle}</p>
                <p className="mt-5 text-base leading-8 text-slate-400 md:text-lg">{hero.description}</p>
              </LandingReveal>

              <LandingReveal delay={250} className="mt-8 flex flex-col gap-3 sm:flex-row">
                <ActionButton destination={requestDemoTarget} variant="primary">
                  {header.primaryCta}
                  <ArrowRight className="h-4 w-4" />
                </ActionButton>
                <ActionButton destination={exploreCidTarget} variant="secondary">
                  {header.secondaryCta}
                  <ChevronRight className="h-4 w-4" />
                </ActionButton>
              </LandingReveal>

              <LandingReveal delay={320} className="mt-8 flex flex-wrap gap-2.5">
                {hero.pills.map((pill) => (
                  <span key={pill} className="landing-pill">
                    {pill}
                  </span>
                ))}
              </LandingReveal>

              <LandingReveal delay={380} className="mt-10 grid gap-3 sm:grid-cols-3">
                {hero.trustLine.map((item, index) => {
                  const ProofIcon = proofIcons[index % proofIcons.length]
                  return (
                    <div key={item} className="rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-4">
                      <ProofIcon className="h-4 w-4 text-amber-300" />
                      <p className="mt-3 text-sm leading-6 text-slate-200">{item}</p>
                    </div>
                  )
                })}
              </LandingReveal>
            </div>

            <LandingReveal delay={180} className="relative z-10 landing-parallax-float">
              <LandingControlCenter {...controlCenter} />
            </LandingReveal>
          </div>
        </section>

        <section className="relative py-8">
          <div className="mx-auto max-w-7xl px-5 md:px-6 lg:px-8">
            <Surface className="overflow-hidden rounded-[2rem] p-6 sm:p-8">
              <div className="grid gap-8 lg:grid-cols-[0.95fr_1.05fr] lg:items-end">
                <LandingReveal>
                  <SectionHeading eyebrow={trust.eyebrow} title={trust.title} description={trust.description} />
                </LandingReveal>

                <LandingReveal delay={120}>
                  <div className="grid gap-4 sm:grid-cols-3">
                    {trust.metrics.map((metric, index) => (
                      <div key={metric.label} className="rounded-[1.6rem] border border-white/10 bg-white/[0.04] p-5">
                        <p className="font-display text-5xl text-white">{metric.value}</p>
                        <p className="mt-3 text-sm font-semibold uppercase tracking-[0.18em] text-slate-200">{metric.label}</p>
                        <p className="mt-3 text-sm leading-7 text-slate-400">{metric.detail}</p>
                        <div className="mt-4 h-px bg-gradient-to-r from-amber-300/40 via-white/10 to-transparent" />
                        <p className="mt-4 text-[11px] uppercase tracking-[0.22em] text-slate-500">metric 0{index + 1}</p>
                      </div>
                    ))}
                  </div>
                </LandingReveal>
              </div>

              <LandingReveal delay={200} className="mt-6 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
                {trust.strips.map((item) => (
                  <div key={item} className="rounded-2xl border border-white/10 bg-black/20 px-4 py-4 text-sm leading-6 text-slate-300">
                    {item}
                  </div>
                ))}
              </LandingReveal>
            </Surface>
          </div>
        </section>

        <section id="producto" className="relative py-24">
          <div className="landing-section-glow left-[12%] top-24" />
          <div className="mx-auto grid max-w-7xl gap-10 px-5 md:px-6 lg:grid-cols-[0.96fr_1.04fr] lg:px-8">
            <LandingReveal>
              <SectionHeading eyebrow={about.eyebrow} title={about.title} description={about.description} />
            </LandingReveal>

            <div className="grid gap-5 sm:grid-cols-3 lg:grid-cols-1">
              {about.pillars.map((pillar, index) => {
                const Icon = pillar.icon
                return (
                  <LandingReveal key={pillar.title} delay={index * 110}>
                    <Surface className="rounded-[1.8rem] p-6">
                      <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-white/10 bg-white/5 text-amber-300">
                        <Icon className="h-5 w-5" />
                      </div>
                      <h3 className="mt-5 text-2xl font-semibold text-white">{pillar.title}</h3>
                      <p className="mt-3 text-sm leading-7 text-slate-300">{pillar.text}</p>
                    </Surface>
                  </LandingReveal>
                )
              })}
            </div>
          </div>
        </section>

        <section id="pipeline" className="relative border-y border-white/10 bg-[#09111c]/80 py-24">
          <div className="mx-auto max-w-7xl px-5 md:px-6 lg:px-8">
            <LandingReveal>
              <SectionHeading eyebrow={pipeline.eyebrow} title={pipeline.title} description={pipeline.description} align="center" />
            </LandingReveal>

            <div className="mt-14 grid gap-6 xl:grid-cols-[0.44fr_0.56fr] xl:items-start">
              <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-1">
                {pipeline.steps.map((step, index) => {
                  const Icon = step.icon
                  return (
                    <LandingReveal key={step.title} delay={index * 85}>
                      <Surface className="landing-step-card h-full rounded-[1.8rem] p-6">
                        <div className="flex items-center justify-between">
                          <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-white/10 bg-white/5 text-amber-300">
                            <Icon className="h-5 w-5" />
                          </div>
                          <span className="font-mono text-[11px] uppercase tracking-[0.24em] text-slate-500">{step.meta}</span>
                        </div>
                        <p className="mt-6 font-mono text-[11px] uppercase tracking-[0.3em] text-amber-300">0{index + 1}</p>
                        <h3 className="mt-3 font-display text-3xl text-white">{step.title}</h3>
                        <p className="mt-4 text-sm leading-7 text-slate-300">{step.text}</p>
                      </Surface>
                    </LandingReveal>
                  )
                })}
              </div>

              <LandingReveal delay={140} className="landing-parallax-soft xl:sticky xl:top-28">
                <LandingPipelineVisual steps={pipeline.steps} />
              </LandingReveal>
            </div>
          </div>
        </section>

        <section id="modulos" className="relative py-24">
          <div className="landing-section-glow right-[8%] top-28" />
          <div className="mx-auto max-w-7xl px-5 md:px-6 lg:px-8">
            <LandingReveal>
              <SectionHeading eyebrow={modules.eyebrow} title={modules.title} description={modules.description} />
            </LandingReveal>

            <div className="mt-14 grid gap-5 md:grid-cols-2 xl:grid-cols-3">
              {modules.items.map((item, index) => {
                const Icon = item.icon
                return (
                  <LandingReveal key={item.title} delay={index * 80}>
                    <Surface className="h-full rounded-[1.85rem] p-6">
                      <div className="flex items-center justify-between">
                        <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-white/10 bg-white/5 text-amber-300">
                          <Icon className="h-5 w-5" />
                        </div>
                        <span className="rounded-full border border-white/10 bg-white/[0.03] px-3 py-1 text-[11px] uppercase tracking-[0.22em] text-slate-400">module</span>
                      </div>
                      <h3 className="mt-5 text-2xl font-semibold text-white">{item.title}</h3>
                      <p className="mt-3 text-sm leading-7 text-slate-300">{item.description}</p>
                      <div className="mt-5 flex flex-wrap gap-2">
                        {item.bullets.map((bullet) => (
                          <span key={bullet} className="landing-pill text-slate-200">
                            {bullet}
                          </span>
                        ))}
                      </div>
                    </Surface>
                  </LandingReveal>
                )
              })}
            </div>
          </div>
        </section>

        <section className="relative border-y border-white/10 bg-[#09111c]/70 py-24">
          <div className="mx-auto max-w-7xl px-5 md:px-6 lg:px-8">
            <LandingReveal>
              <SectionHeading eyebrow={comparison.eyebrow} title={comparison.title} description={comparison.description} />
            </LandingReveal>

            <LandingReveal delay={120} className="mt-14 overflow-hidden rounded-[2rem] border border-white/10 bg-white/[0.04]">
              <div className="grid border-b border-white/10 bg-white/[0.03] px-6 py-5 md:grid-cols-[0.8fr_1.1fr_1.1fr] md:items-center md:px-8">
                <div className="font-mono text-[11px] uppercase tracking-[0.3em] text-slate-500">Comparativa</div>
                <div className="mt-3 flex items-center gap-2 text-sm font-semibold text-white md:mt-0">
                  <Check className="h-4 w-4 text-emerald-300" /> CID
                </div>
                <div className="mt-2 flex items-center gap-2 text-sm font-semibold text-slate-300 md:mt-0">
                  <X className="h-4 w-4 text-rose-300" /> Generadores de video simples
                </div>
              </div>

              {comparison.rows.map((row, index) => (
                <div key={row.label} className={`grid gap-5 px-6 py-6 md:grid-cols-[0.8fr_1.1fr_1.1fr] md:px-8 ${index !== comparison.rows.length - 1 ? 'border-b border-white/10' : ''}`}>
                  <div>
                    <p className="text-sm font-semibold uppercase tracking-[0.16em] text-slate-200">{row.label}</p>
                  </div>
                  <div className="rounded-[1.3rem] border border-emerald-300/15 bg-emerald-300/10 p-4 text-sm leading-7 text-emerald-50">
                    {row.cid}
                  </div>
                  <div className="rounded-[1.3rem] border border-rose-300/15 bg-rose-300/10 p-4 text-sm leading-7 text-rose-50">
                    {row.simple}
                  </div>
                </div>
              ))}
            </LandingReveal>
          </div>
        </section>

        <section id="casos" className="relative py-24">
          <div className="mx-auto max-w-7xl px-5 md:px-6 lg:px-8">
            <LandingReveal>
              <SectionHeading eyebrow={useCases.eyebrow} title={useCases.title} description={useCases.description} align="center" />
            </LandingReveal>

            <div className="mt-14 grid gap-5 md:grid-cols-2 xl:grid-cols-4">
              {useCases.items.map((item, index) => {
                const Icon = item.icon
                return (
                  <LandingReveal key={item.title} delay={index * 95}>
                    <Surface className="h-full rounded-[1.9rem] p-6">
                      <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-white/10 bg-white/5 text-amber-300">
                        <Icon className="h-5 w-5" />
                      </div>
                      <h3 className="mt-5 text-2xl font-semibold text-white">{item.title}</h3>
                      <p className="mt-3 text-sm leading-7 text-slate-300">{item.text}</p>
                      <ul className="mt-5 space-y-2 text-sm leading-6 text-slate-200">
                        {item.deliverables.map((deliverable) => (
                          <li key={deliverable} className="flex gap-3">
                            <Check className="mt-1 h-4 w-4 shrink-0 text-amber-300" />
                            <span>{deliverable}</span>
                          </li>
                        ))}
                      </ul>
                    </Surface>
                  </LandingReveal>
                )
              })}
            </div>
          </div>
        </section>

        <section className="relative border-y border-white/10 bg-[#09111c]/80 py-24">
          <div className="mx-auto max-w-7xl px-5 md:px-6 lg:px-8">
            <LandingReveal>
              <SectionHeading eyebrow={showcase.eyebrow} title={showcase.title} description={showcase.description} />
            </LandingReveal>

            <div className="mt-14 grid gap-6 xl:grid-cols-[0.42fr_0.58fr]">
              <div className="grid gap-4">
                {showcase.items.map((item, index) => (
                  <LandingReveal key={item.tab} delay={index * 90}>
                    <button
                      type="button"
                      onClick={() => setActiveShowcase(index)}
                      className={`w-full rounded-[1.7rem] border p-5 text-left transition-all duration-300 ${
                        activeShowcase === index
                          ? 'border-amber-300/30 bg-amber-300/10 shadow-[0_18px_60px_rgba(245,158,11,0.1)]'
                          : 'border-white/10 bg-white/[0.035] hover:border-white/20 hover:bg-white/[0.05]'
                      }`}
                    >
                      <p className="font-mono text-[11px] uppercase tracking-[0.26em] text-slate-500">{item.eyebrow}</p>
                      <h3 className="mt-3 text-2xl font-semibold text-white">{item.title}</h3>
                      <p className="mt-3 text-sm leading-7 text-slate-300">{item.description}</p>
                    </button>
                  </LandingReveal>
                ))}
              </div>

              <LandingReveal delay={140} className="landing-parallax-soft">
                <Surface className="relative overflow-hidden rounded-[2rem] p-5 sm:p-6">
                  <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(56,189,248,0.14),transparent_25%),radial-gradient(circle_at_bottom_left,rgba(245,158,11,0.18),transparent_32%)]" />
                  <div className="relative z-10 rounded-[1.7rem] border border-white/10 bg-[#0b1018]/85 p-5 backdrop-blur-xl sm:p-6">
                    <div className="flex flex-wrap items-center justify-between gap-4 border-b border-white/10 pb-4">
                      <div>
                        <p className="editorial-kicker text-amber-300">{activeShowcaseItem.tab}</p>
                        <h3 className="mt-3 font-display text-4xl text-white md:text-5xl">{activeShowcaseItem.title}</h3>
                      </div>
                      <div className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-1 text-[11px] uppercase tracking-[0.22em] text-slate-300">
                        premium mock
                      </div>
                    </div>

                    <div className="mt-6 grid gap-5 lg:grid-cols-[0.9fr_1.1fr] lg:items-center">
                      <div>
                        <p className="text-sm leading-7 text-slate-300">{activeShowcaseItem.description}</p>
                        <div className="mt-5 space-y-3">
                          {activeShowcaseItem.highlights.map((highlight) => (
                            <div key={highlight} className="flex items-start gap-3 rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-3">
                              <Check className="mt-1 h-4 w-4 shrink-0 text-amber-300" />
                              <span className="text-sm leading-6 text-slate-200">{highlight}</span>
                            </div>
                          ))}
                        </div>
                      </div>

                      <LandingShowcasePlaceholder variant={activeShowcaseItem.visual} />
                    </div>
                  </div>
                </Surface>
              </LandingReveal>
            </div>
          </div>
        </section>

        <section id="cta-final" className="relative py-24">
          <div className="landing-section-glow left-[22%] top-16" />
          <div className="mx-auto max-w-6xl px-5 md:px-6 lg:px-8">
            <LandingReveal>
              <Surface className="relative overflow-hidden rounded-[2.4rem] p-8 sm:p-10 lg:p-12">
                <div className="absolute inset-0 bg-[linear-gradient(120deg,rgba(245,158,11,0.14),transparent_42%,rgba(59,130,246,0.12)_100%)]" />
                <div className="relative z-10 grid gap-10 lg:grid-cols-[1fr_auto] lg:items-end">
                  <div>
                    <p className="editorial-kicker text-amber-300">{finalCta.eyebrow}</p>
                    <h2 className="mt-4 max-w-4xl font-display text-4xl font-semibold leading-[0.92] text-white md:text-6xl">
                      {finalCta.title}
                    </h2>
                    <p className="mt-5 max-w-3xl text-base leading-8 text-slate-200 md:text-lg">{finalCta.description}</p>
                    <div className="mt-6 flex flex-wrap gap-3">
                      {finalCta.bullets.map((bullet) => (
                        <span key={bullet} className="landing-pill">
                          {bullet}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="flex flex-col gap-3 sm:flex-row lg:flex-col">
                    <ActionButton destination={requestDemoTarget} variant="primary">
                      {finalCta.primaryCta}
                      <ArrowRight className="h-4 w-4" />
                    </ActionButton>
                    <ActionButton destination={exploreCidTarget} variant="secondary">
                      {finalCta.secondaryCta}
                      <ChevronRight className="h-4 w-4" />
                    </ActionButton>
                  </div>
                </div>
              </Surface>
            </LandingReveal>
          </div>
        </section>

        <section id="faq" className="relative border-t border-white/10 py-24">
          <div className="mx-auto max-w-5xl px-5 md:px-6 lg:px-8">
            <LandingReveal>
              <SectionHeading eyebrow={faq.eyebrow} title={faq.title} description={faq.description} align="center" />
            </LandingReveal>

            <div className="mt-14 grid gap-4">
              {faq.items.map((item, index) => (
                <LandingReveal key={item.question} delay={index * 80}>
                  <details className="group rounded-[1.6rem] border border-white/10 bg-white/[0.035] p-6 open:border-amber-300/30 open:bg-amber-300/[0.06]">
                    <summary className="flex cursor-pointer list-none items-center justify-between gap-4 text-left">
                      <span className="text-lg font-medium text-white">{item.question}</span>
                      <HelpCircle className="h-5 w-5 shrink-0 text-amber-300 transition-transform duration-300 group-open:rotate-45" />
                    </summary>
                    <p className="mt-4 text-sm leading-8 text-slate-300">{item.answer}</p>
                  </details>
                </LandingReveal>
              ))}
            </div>
          </div>
        </section>
      </main>

      <footer className="border-t border-white/10 py-10">
        <div className="mx-auto grid max-w-7xl gap-8 px-5 md:px-6 lg:grid-cols-[1fr_auto] lg:items-center lg:px-8">
          <div>
            <p className="font-display text-3xl text-white">{footer.brandLine}</p>
            <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-400">{footer.description}</p>
          </div>

          <div className="flex flex-col gap-4 sm:items-end">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center lg:justify-end">
              {footer.links.map((item) => (
                <Link key={item.href} to={item.href} className="text-sm text-slate-300 transition-colors hover:text-white">
                  {item.label}
                </Link>
              ))}
            </div>
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center lg:justify-end">
              {footer.legalLinks.map((item) => (
                <Link key={item.href} to={item.href} className="text-xs text-slate-500 transition-colors hover:text-slate-200">
                  {item.label}
                </Link>
              ))}
            </div>
          </div>
        </div>

        <div className="mx-auto mt-8 flex max-w-7xl items-center gap-3 px-5 text-sm text-slate-500 md:px-6 lg:px-8">
          <ShieldCheck className="h-4 w-4 text-amber-300" />
          <p>{footer.legal}</p>
        </div>
      </footer>
    </div>
  )
}
