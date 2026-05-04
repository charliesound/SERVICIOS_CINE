import { useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import { LayoutDashboard, LogOut, ShieldCheck } from 'lucide-react'
import BrandHeroSection from '@/components/landing/BrandHeroSection'
import BrandPositioningSection from '@/components/landing/BrandPositioningSection'
import CidProductSpotlight from '@/components/landing/CidProductSpotlight'
import SpecializedSolutionsGrid from '@/components/landing/SpecializedSolutionsGrid'
import AudienceSection from '@/components/landing/AudienceSection'
import HowItWorksSection from '@/components/landing/HowItWorksSection'
import UseCasesSection from '@/components/landing/UseCasesSection'
import TrustLegalSection from '@/components/landing/TrustLegalSection'
import LandingFinalCta from '@/components/landing/LandingFinalCta'
import LandingAmbientScene from '@/components/landing/LandingAmbientScene'
import { landingContent } from '@/data/landingContent'
import { getPrimaryCIDTarget, useAuthStore } from '@/store'

export default function LandingPage() {
  const { isAuthenticated, user } = useAuthStore()
  const cidTarget = getPrimaryCIDTarget(user)
  const shellRef = useRef<HTMLDivElement | null>(null)

  const exploreCidTarget = isAuthenticated ? cidTarget : '/register/cid'
  const requestDemoTarget = '/register/demo'

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
    <div ref={shellRef} className="landing-shell landing-brand-shell min-h-screen text-white">
      <LandingAmbientScene />
      <div className="landing-noise" />
      <div className="landing-backdrop" />

      <header className="fixed inset-x-0 top-0 z-50 border-b border-white/10 bg-[#07111d]/55 backdrop-blur-2xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-5 py-4 md:px-6 lg:px-8">
          <Link to="/" className="flex items-center gap-3">
            <img
              src="/assets/ailinkcinema-logo.png"
              alt="AILinkCinema"
              className="h-11 w-11 rounded-2xl object-cover shadow-[0_0_32px_rgba(245,158,11,0.22)]"
            />
            <div>
              <p className="text-lg font-semibold tracking-tight text-white">AILinkCinema</p>
              <p className="font-mono text-[11px] uppercase tracking-[0.28em] text-slate-400">
                AI tools for cinema
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
        <BrandHeroSection
          content={landingContent.hero}
          exploreCidTarget={exploreCidTarget}
          requestDemoTarget={requestDemoTarget}
        />
        <BrandPositioningSection content={landingContent.about} />
        <CidProductSpotlight content={landingContent.cid} />
        <SpecializedSolutionsGrid content={landingContent.solutions} />
        <AudienceSection content={landingContent.audience} />
        <HowItWorksSection content={landingContent.howItWorks} />
        <UseCasesSection content={landingContent.useCases} />
        <TrustLegalSection content={landingContent.trustLegal} />
        <LandingFinalCta
          content={landingContent.finalCta}
          exploreCidTarget={exploreCidTarget}
          requestDemoTarget={requestDemoTarget}
        />
      </main>

      <footer className="border-t border-white/10 py-10">
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
