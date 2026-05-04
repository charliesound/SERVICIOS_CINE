import { Link, Navigate, useParams } from 'react-router-dom'
import { LayoutDashboard, LogOut, ShieldCheck } from 'lucide-react'
import LandingAmbientScene from '@/components/landing/LandingAmbientScene'
import SolutionHero from '@/components/solutions/SolutionHero'
import PricingModelBlock from '@/components/solutions/PricingModelBlock'
import {
  getSolutionBySlug,
  publicBrandLinks,
  publicFooterLinks,
  publicLegalLinks,
  solutionsMarketingNotes,
} from '@/data/solutionsContent'
import { getPrimaryCIDTarget, useAuthStore } from '@/store'

export default function SolutionDetailPage() {
  const { slug } = useParams<{ slug: string }>()
  const solution = slug ? getSolutionBySlug(slug) : null
  const { isAuthenticated, user } = useAuthStore()
  const cidTarget = getPrimaryCIDTarget(user)

  if (!solution) {
    return <Navigate to="/solutions" replace />
  }

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
              <p className="font-mono text-[11px] uppercase tracking-[0.28em] text-slate-400">Solution detail</p>
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
              <Link to="/pricing" className="landing-cta-primary hidden sm:inline-flex">
                Ver precios
              </Link>
            )}
          </div>
        </div>
      </header>

      <main>
        <SolutionHero
          eyebrow={solution.type}
          title={solution.title}
          description={solution.heroDescription}
          primaryLabel="Ver precios"
          primaryTo="/pricing"
          secondaryLabel="Ver CID"
          secondaryTo="/solutions/cid"
          highlights={solution.bullets}
        />

        <section className="relative pb-24">
          <div className="mx-auto max-w-7xl px-5 md:px-6 lg:px-8">
            <PricingModelBlock
              title={solution.shortTitle}
              priceLines={[solution.priceLabel]}
              description={solution.description}
              bullets={[
                solution.includedInCid ? 'Tambien puede quedar incluido dentro de CID.' : 'Puede formar parte del ecosistema AILinkCinema.',
                ...solutionsMarketingNotes.slice(0, 2),
              ]}
            />

            <div className="mt-10 grid gap-6 xl:grid-cols-[0.56fr_0.44fr]">
              <section className="solution-card solution-card-featured">
                <p className="solution-eyebrow text-amber-300">Que resuelve</p>
                <h2 className="mt-3 text-3xl font-semibold text-white">Una aplicacion clara para una necesidad concreta del pipeline.</h2>
                <p className="mt-4 text-sm leading-7 text-slate-300">{solution.heroDescription}</p>
                <div className="mt-6 flex flex-wrap gap-2.5">
                  {solution.bullets.map((bullet) => (
                    <span key={bullet} className="landing-pill text-slate-200">
                      {bullet}
                    </span>
                  ))}
                </div>
              </section>

              <section className="solution-card">
                <p className="solution-eyebrow text-cyan-200">Modelo comercial</p>
                <h2 className="mt-3 text-3xl font-semibold text-white">Puede contratarse por separado o entrar dentro de un despliegue CID.</h2>
                <p className="mt-4 text-sm leading-7 text-slate-300">
                  AILinkCinema estructura la oferta para que el cliente pueda entrar por un modulo puntual y ampliar despues a una solucion mas completa si el proyecto lo necesita.
                </p>
                <div className="mt-6 flex gap-3 flex-wrap">
                  <Link to="/solutions" className="landing-cta-secondary inline-flex">Ver todas las soluciones</Link>
                  <Link to="/register/demo" className="landing-cta-primary inline-flex">Solicitar demo</Link>
                </div>
              </section>
            </div>
          </div>
        </section>
      </main>

      <footer className="border-t border-white/10 py-10">
        <div className="mx-auto grid max-w-7xl gap-8 px-5 md:px-6 lg:grid-cols-[1fr_auto] lg:items-center lg:px-8">
          <div>
            <p className="font-display text-3xl text-white">AILinkCinema</p>
            <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-400">Apps especializadas con precio propio y posibilidad de integrarse dentro de CID.</p>
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
          <p>Modulo independiente con opcion de integrarse dentro del producto principal CID.</p>
        </div>
      </footer>
    </div>
  )
}
