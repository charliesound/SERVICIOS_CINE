import { Link } from 'react-router-dom'
import { LayoutDashboard, LogOut, ShieldCheck } from 'lucide-react'
import LandingAmbientScene from '@/components/landing/LandingAmbientScene'
import SolutionHero from '@/components/solutions/SolutionHero'
import PricingModelBlock from '@/components/solutions/PricingModelBlock'
import {
  cidPageHighlights,
  cidProduct,
  publicBrandLinks,
  publicFooterLinks,
  publicLegalLinks,
} from '@/data/solutionsContent'
import { getPrimaryCIDTarget, useAuthStore } from '@/store'

export default function CIDProductPage() {
  const { isAuthenticated, user } = useAuthStore()
  const cidTarget = getPrimaryCIDTarget(user)

  return (
    <div className="landing-shell landing-brand-shell min-h-screen text-white">
      <LandingAmbientScene />
      <div className="landing-noise" />
      <div className="landing-backdrop" />

      <header className="fixed inset-x-0 top-0 z-50 border-b border-white/10 bg-[#07111d]/55 backdrop-blur-2xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-5 py-4 md:px-6 lg:px-8">
          <Link to="/" className="flex items-center gap-3">
            <img src="/assets/ailinkcinema-logo.png" alt="AILinkCinema" className="h-11 w-11 rounded-2xl object-cover shadow-[0_0_32px_rgba(245,158,11,0.22)]" />
            <div>
              <p className="text-lg font-semibold tracking-tight text-white">AILinkCinema</p>
              <p className="font-mono text-[11px] uppercase tracking-[0.28em] text-slate-400">CID Product</p>
            </div>
          </Link>

          <nav className="hidden items-center gap-7 text-sm text-slate-300 xl:flex">
            {publicBrandLinks.map((item) => (
              <Link key={item.to} to={item.to} className="transition-colors duration-300 hover:text-white">
                {item.label}
              </Link>
            ))}
          </nav>

          <div className="flex items-center gap-2 md:gap-3">
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
              <Link to="/register/demo" className="landing-cta-primary hidden sm:inline-flex">
                Solicitar demo
              </Link>
            )}
          </div>
        </div>
      </header>

      <main>
        <SolutionHero
          eyebrow="Producto principal"
          title={cidProduct.title}
          description={cidProduct.heroDescription}
          primaryLabel="Solicitar demo"
          primaryTo="/register/demo"
          secondaryLabel="Ver precios"
          secondaryTo="/pricing"
          highlights={cidPageHighlights}
        />

        <section className="relative pb-24">
          <div className="mx-auto max-w-7xl px-5 md:px-6 lg:px-8">
            <PricingModelBlock
              title={cidProduct.pricing.headline}
              priceLines={[cidProduct.pricing.setup, cidProduct.pricing.monthly]}
              description={cidProduct.pricing.requirements}
              bullets={cidProduct.pricing.bullets}
              featured
            />

            <div className="mt-10 grid gap-6 xl:grid-cols-[0.48fr_0.52fr]">
              <section className="solution-card solution-card-featured">
                <p className="solution-eyebrow text-amber-300">Pipeline cubierto</p>
                <h2 className="mt-3 text-3xl font-semibold text-white">CID conecta el proyecto completo.</h2>
                <div className="mt-6 solution-phase-list">
                  {cidProduct.pipeline.map((phase, index) => (
                    <div key={phase} className="solution-phase-row">
                      <span className="solution-phase-index">0{index + 1}</span>
                      <span className="text-sm font-medium text-white">{phase}</span>
                    </div>
                  ))}
                </div>
              </section>

              <section className="solution-card">
                <p className="solution-eyebrow text-cyan-200">Incluye todos los modulos</p>
                <h2 className="mt-3 text-3xl font-semibold text-white">Los servicios independientes pueden entrar por separado o integrarse dentro de CID.</h2>
                <div className="mt-6 flex flex-wrap gap-2.5">
                  {cidProduct.includedModules.map((module) => (
                    <span key={module} className="landing-pill text-slate-200">
                      {module}
                    </span>
                  ))}
                </div>
                <p className="mt-6 text-sm leading-7 text-slate-300">
                  El setup inicial existe porque CID se adapta al flujo real de la produccion, al modelo de aprobaciones y a la forma de trabajar de cada equipo.
                </p>
              </section>
            </div>
          </div>
        </section>
      </main>

      <footer className="border-t border-white/10 py-10">
        <div className="mx-auto grid max-w-7xl gap-8 px-5 md:px-6 lg:grid-cols-[1fr_auto] lg:items-center lg:px-8">
          <div>
            <p className="font-display text-3xl text-white">AILinkCinema / CID</p>
            <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-400">Producto completo para desarrollo, produccion, post y entrega con todos los modulos conectados.</p>
          </div>

          <div className="flex flex-col gap-4 sm:items-end">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center lg:justify-end">
              {publicFooterLinks.map((item) => (
                <Link key={item.to} to={item.to} className="text-sm text-slate-300 transition-colors hover:text-white">
                  {item.label}
                </Link>
              ))}
            </div>
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center lg:justify-end">
              {publicLegalLinks.map((item) => (
                <Link key={item.to} to={item.to} className="text-xs text-slate-500 transition-colors hover:text-slate-200">
                  {item.label}
                </Link>
              ))}
            </div>
          </div>
        </div>

        <div className="mx-auto mt-8 flex max-w-7xl items-center gap-3 px-5 text-sm text-slate-500 md:px-6 lg:px-8">
          <ShieldCheck className="h-4 w-4 text-amber-300" />
          <p>CID tiene setup inicial porque se adapta al flujo real de cada produccion.</p>
        </div>
      </footer>
    </div>
  )
}
