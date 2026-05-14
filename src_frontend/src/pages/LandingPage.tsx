import { useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import { ArrowRight, Clapperboard, Film, LayoutDashboard, LogOut, ShieldCheck } from 'lucide-react'
import LandingHeroCinematic from '@/components/landing/LandingHeroCinematic'
import LandingProblemSolution from '@/components/landing/LandingProblemSolution'
import LandingStudioModules from '@/components/landing/LandingStudioModules'
import LandingScriptToPromptProof from '@/components/landing/LandingScriptToPromptProof'
import LandingPipelineBuilder from '@/components/landing/LandingPipelineBuilder'
import LandingStoryboardCanvas from '@/components/landing/LandingStoryboardCanvas'
import LandingCreativeControl from '@/components/landing/LandingCreativeControl'
import LandingDiferencial from '@/components/landing/LandingDiferencial'
import LandingAudienceB2B from '@/components/landing/LandingAudienceB2B'
import SpecializedSolutionsGrid from '@/components/landing/SpecializedSolutionsGrid'
import TrustLegalSection from '@/components/landing/TrustLegalSection'
import LandingPricingSection from '@/components/landing/LandingPricingSection'
import LandingFinalCta from '@/components/landing/LandingFinalCta'
import LandingReveal from '@/components/landing/LandingReveal'
import LandingAmbientScene from '@/components/landing/LandingAmbientScene'
import { landingContent } from '@/data/landingContent'
import { useSeo } from '@/hooks/useSeo'
import { getPrimaryCIDTarget, useAuthStore } from '@/store'
import { buildAbsoluteUrl, SEO_SITE_NAME } from '@/utils/seo'

function trackEvent(eventName: string, payload?: Record<string, unknown>) {
  if (typeof window !== 'undefined' && import.meta.env.DEV) {
    console.info(`[Track] ${eventName}`, payload ?? {})
  }
}

export default function LandingPage() {
  const { isAuthenticated, user } = useAuthStore()
  const cidTarget = getPrimaryCIDTarget(user)
  const shellRef = useRef<HTMLDivElement | null>(null)

  const exploreCidTarget = '/solutions/cid'
  const solutionsTarget = '/solutions'
  const requestDemoTarget = '/pricing'
   const description =
     'AILinkCinema: inteligencia artificial para cine, television y publicidad. Desde guion hasta entrega final con CID, el sistema de produccion audiovisual completo.'

  useSeo({
    title: 'Inteligencia artificial para cine y produccion audiovisual',
    description,
    path: '/',
    robots: 'index, follow',
    keywords: [
      'ia para cine',
      'software audiovisual',
      'produccion audiovisual',
      'storyboard con ia',
      'desglose de guion',
      'postproduccion audiovisual',
      'doblaje',
      'delivery audiovisual',
    ],
    structuredData: [
      {
        '@context': 'https://schema.org',
        '@type': 'WebSite',
        name: SEO_SITE_NAME,
        url: buildAbsoluteUrl('/'),
        description,
        inLanguage: 'es',
      },
      {
        '@context': 'https://schema.org',
        '@type': 'Organization',
        name: SEO_SITE_NAME,
        url: buildAbsoluteUrl('/'),
        logo: buildAbsoluteUrl('/assets/ailinkcinema-logo.png'),
        description,
      },
      {
        '@context': 'https://schema.org',
        '@type': 'SoftwareApplication',
        name: 'CID - Cine Inteligente Digital',
        applicationCategory: 'BusinessApplication',
        operatingSystem: 'Web',
        url: buildAbsoluteUrl('/solutions/cid'),
        description:
          'Plataforma premium para coordinar guion, storyboard, produccion, doblaje, postproduccion, distribucion y entrega dentro del pipeline audiovisual.',
      },
    ],
  })

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
    <div ref={shellRef} className="landing-shell landing-cinematic-shell min-h-screen text-white">
      <LandingAmbientScene />
      <div className="landing-noise" />
      <div className="landing-backdrop" />

      <header className="fixed inset-x-0 top-0 z-50 border-b border-white/5 bg-[#080808]/70 backdrop-blur-2xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-5 py-3 md:px-6 lg:px-8 lg:py-4">
          <Link to="/" className="flex items-center gap-3 md:gap-4">
            <img
              src="/assets/ailinkcinema-logo.png"
              alt="AILinkCinema"
              className="h-11 w-11 rounded-2xl object-cover shadow-[0_0_36px_rgba(245,158,11,0.28)] md:h-14 md:w-14"
            />
            <div>
              <p className="text-xl font-bold tracking-tight text-white md:text-2xl landing-brand-name">AILinkCinema</p>
              <p className="font-mono text-[10px] uppercase tracking-[0.28em] text-amber-400/60 md:text-[11px]">
                CID &mdash; Cine Inteligente Digital
              </p>
            </div>
          </Link>

          <nav className="hidden items-center gap-7 text-sm text-slate-300 xl:flex">
            {landingContent.header.nav.map((item) => (
              item.href.startsWith('#') ? (
                <a
                  key={item.href}
                  href={item.href}
                  className="transition-colors duration-300 hover:text-white"
                >
                  {item.label}
                </a>
              ) : (
                <Link
                  key={item.href}
                  to={item.href}
                  className="transition-colors duration-300 hover:text-white"
                >
                  {item.label}
                </Link>
              )
            ))}
          </nav>

          <div className="flex items-center gap-2 md:gap-3">
            {!isAuthenticated && (
              <Link
                to="/login"
                className="hidden rounded-full border border-white/10 px-4 py-2 text-sm text-slate-200 transition-colors hover:border-white/20 hover:bg-white/5 sm:inline-flex"
              >
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
              <Link to={requestDemoTarget} className="landing-cta-primary hidden sm:inline-flex">
                {landingContent.header.primaryCta}
              </Link>
            )}
          </div>
        </div>
      </header>

      <main>
        <LandingHeroCinematic
          content={{
            eyebrow: landingContent.hero.eyebrow,
            title: 'Cine Inteligente Digital',
            subtitle: landingContent.hero.subtitle,
          }}
          exploreCidTarget={exploreCidTarget}
          solutionsTarget={solutionsTarget}
          requestDemoTarget={requestDemoTarget}
        />

        <LandingProblemSolution />

        <LandingStudioModules />

        <LandingScriptToPromptProof />

        <LandingPipelineBuilder />

        <LandingStoryboardCanvas />

        <LandingCreativeControl />

        <LandingDiferencial />

        <LandingAudienceB2B />

        <section className="relative border-t border-white/5 py-24">
          <div className="mx-auto max-w-7xl px-5 md:px-6 lg:px-8">
            <LandingReveal>
              <div className="max-w-2xl">
                <p className="editorial-kicker text-amber-300/90">Soluciones por rol</p>
                <h2 className="mt-4 font-display text-4xl font-semibold leading-[0.92] text-white md:text-6xl">
                  Un flujo diseñado para cada perfil del equipo audiovisual.
                </h2>
                <p className="mt-4 max-w-2xl text-base leading-7 text-slate-300 md:text-lg md:leading-8">
                  Cada profesional encuentra en AILinkCinema las herramientas que necesita segun su
                  responsabilidad en el pipeline de produccion.
                </p>
              </div>
            </LandingReveal>

            <LandingReveal delay={60}>
              <div className="mt-14">
                <div className="grid gap-8 lg:grid-cols-2">
                  <div className="landing-brand-solution-card relative overflow-hidden rounded-[1.85rem] p-8 md:p-10">
                    <div className="relative z-10">
                      <div className="flex items-center gap-4">
                        <div className="flex h-14 w-14 items-center justify-center rounded-2xl border border-amber-400/20 bg-amber-400/10 text-amber-300">
                          <Clapperboard className="h-7 w-7" />
                        </div>
                        <div>
                          <span className="rounded-full border border-amber-400/20 bg-amber-400/10 px-3 py-1 text-[11px] uppercase tracking-[0.22em] text-amber-200">
                            Director / Realizador
                          </span>
                        </div>
                      </div>
                      <h3 className="mt-6 text-3xl font-semibold text-white md:text-4xl">
                        Director AI Studio
                      </h3>
                      <p className="mt-2 text-lg text-amber-200/80">Del guion a la vision del director.</p>
                      <p className="mt-4 max-w-2xl text-base leading-7 text-slate-300">
                        Convierte un guion en una vision cinematografica clara: analisis dramatico, tono visual,
                        secuencias clave, storyboard y dossier creativo para preproduccion o pitching.
                      </p>
                      <div className="mt-8 flex flex-wrap gap-3">
                        <Link
                          to="/soluciones/director"
                          className="landing-cta-primary"
                        >
                          Ver solucion para directores
                          <ArrowRight className="h-4 w-4" />
                        </Link>
                      </div>
                    </div>
                  </div>

                  <div className="landing-brand-solution-card relative overflow-hidden rounded-[1.85rem] p-8 md:p-10 border-white/10 bg-white/[0.02]">
                    <div className="relative z-10">
                      <div className="flex items-center gap-4">
                        <div className="flex h-14 w-14 items-center justify-center rounded-2xl border border-cyan-400/20 bg-cyan-400/10 text-cyan-300">
                          <Film className="h-7 w-7" />
                        </div>
                        <div>
                          <span className="rounded-full border border-cyan-400/20 bg-cyan-400/10 px-3 py-1 text-[11px] uppercase tracking-[0.22em] text-cyan-200">
                            Productor / Ejecutivo
                          </span>
                        </div>
                      </div>
                      <h3 className="mt-6 text-3xl font-semibold text-white md:text-4xl">
                        Producer AI Studio
                      </h3>
                      <p className="mt-2 text-lg text-cyan-200/80">Control total y viabilidad de produccion.</p>
                      <p className="mt-4 max-w-2xl text-base leading-7 text-slate-300">
                        Gestiona la viabilidad, presupuesto y planificacion de tu proyecto desde la fase de desarrollo.
                        Optimiza la financiacion y mantén el control operativo con inteligencia de industria.
                      </p>
                      <div className="mt-8 flex flex-wrap gap-3">
                        <Link
                          to="/soluciones/productor"
                          className="landing-cta-primary border-cyan-500/50 hover:bg-cyan-500/10"
                        >
                          Ver solucion para productores
                          <ArrowRight className="h-4 w-4" />
                        </Link>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </LandingReveal>
          </div>
        </section>

        <section id="soluciones" className="relative border-t border-white/5 py-24">
          <SpecializedSolutionsGrid content={landingContent.solutions} />
        </section>

        <LandingPricingSection content={landingContent.pricing} />

        <TrustLegalSection content={landingContent.trustLegal} />

        {/* CTA to /demo-cid */}
        <section className="relative border-t border-white/5 py-20">
          <div className="mx-auto max-w-5xl px-5 text-center md:px-8">
            <div className="landing-brand-final-cta rounded-[2.4rem] p-8 sm:p-10 lg:p-12">
              <p className="font-mono text-[11px] uppercase tracking-[0.28em] text-amber-300">
                ¿Tienes un guion en desarrollo?
              </p>
              <h2 className="mt-4 font-display text-3xl font-semibold leading-[1.1] text-white md:text-5xl">
                Prueba CID con tu proyecto y recibe un análisis visual y estratégico para pitching, financiación o producción.
              </h2>
              <div className="mt-8 flex flex-col items-center gap-3 sm:flex-row sm:justify-center">
                <Link
                  to="/demo-cid"
                  className="landing-cta-primary text-base"
                  onClick={() => trackEvent('click_home_to_demo_cid')}
                >
                  Probar CID con mi guion
                  <ArrowRight className="h-4 w-4" />
                </Link>
              </div>
            </div>
          </div>
        </section>

        <LandingFinalCta
          content={landingContent.finalCta}
          exploreCidTarget={exploreCidTarget}
          solutionsTarget={solutionsTarget}
          requestDemoTarget={requestDemoTarget}
        />
      </main>

      <footer className="border-t border-white/5 py-10">
        <div className="mx-auto grid max-w-7xl gap-8 px-5 md:px-6 lg:grid-cols-[1fr_auto] lg:items-center lg:px-8">
          <div>
            <p className="font-display text-3xl text-white">{landingContent.footer.brandLine}</p>
            <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-400">
              {landingContent.footer.description}
            </p>
          </div>

          <div className="flex flex-col gap-4 sm:items-end">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center lg:justify-end">
              {landingContent.footer.links.map((item) => (
                item.href.startsWith('#') ? (
                  <a key={item.href} href={item.href} className="text-sm text-slate-300 transition-colors hover:text-white">
                    {item.label}
                  </a>
                ) : (
                  <Link key={item.href} to={item.href} className="text-sm text-slate-300 transition-colors hover:text-white">
                    {item.label}
                  </Link>
                )
              ))}
            </div>
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center lg:justify-end">
              {landingContent.footer.legalLinks.map((item) => (
                <Link key={item.href} to={item.href} className="text-xs text-slate-500 transition-colors hover:text-slate-200">
                  {item.label}
                </Link>
              ))}
            </div>
          </div>
        </div>

        <div className="mx-auto mt-8 flex max-w-7xl items-center gap-3 px-5 text-sm text-slate-500 md:px-6 lg:px-8">
          <ShieldCheck className="h-4 w-4 text-amber-300" />
          <p>{landingContent.footer.legal}</p>
        </div>
      </footer>
    </div>
  )
}
