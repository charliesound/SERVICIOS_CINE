import { Link } from 'react-router-dom'
import { LayoutDashboard, LogOut, ShieldCheck } from 'lucide-react'
import LandingAmbientScene from '@/components/landing/LandingAmbientScene'
import SolutionHero from '@/components/solutions/SolutionHero'
import SolutionGrid from '@/components/solutions/SolutionGrid'
import PricingModelBlock from '@/components/solutions/PricingModelBlock'
import {
  allSolutions,
  pricingOverview,
  publicBrandLinks,
  publicFooterLinks,
  publicLegalLinks,
  solutionsHeroContent,
  solutionsMarketingNotes,
  solutionsPageHighlights,
} from '@/data/solutionsContent'
import { useSeo } from '@/hooks/useSeo'
import { getPrimaryCIDTarget, useAuthStore } from '@/store'
import { buildAbsoluteUrl, buildBreadcrumbStructuredData } from '@/utils/seo'

export default function SolutionsPage() {
  const { isAuthenticated, user } = useAuthStore()
  const cidTarget = getPrimaryCIDTarget(user)
  const description =
    'Catalogo de soluciones IA para cine y audiovisual: CID, desglose de guion, storyboard, planificacion de produccion, doblaje, sonido, promo video y VFX.'

  useSeo({
    title: 'Soluciones IA para cine y audiovisual',
    description,
    path: '/solutions',
    robots: 'index, follow',
    keywords: ['soluciones ia cine', 'software produccion audiovisual', 'storyboard ai', 'desglose de guion', 'doblaje audiovisual'],
    structuredData: [
      buildBreadcrumbStructuredData([
        { name: 'Inicio', path: '/' },
        { name: 'Soluciones', path: '/solutions' },
      ]),
      {
        '@context': 'https://schema.org',
        '@type': 'CollectionPage',
        name: 'Soluciones AILinkCinema',
        url: buildAbsoluteUrl('/solutions'),
        description,
        mainEntity: {
          '@type': 'ItemList',
          itemListElement: allSolutions.map((solution, index) => ({
            '@type': 'ListItem',
            position: index + 1,
            name: solution.title,
            url: buildAbsoluteUrl(solution.path),
            description: solution.description,
          })),
        },
      },
    ],
  })

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
              <p className="font-mono text-[11px] uppercase tracking-[0.28em] text-slate-400">Solutions</p>
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
          eyebrow="AILinkCinema / Soluciones"
          title={solutionsHeroContent.title}
          description={solutionsHeroContent.description}
          primaryLabel="Explorar CID"
          primaryTo="/solutions/cid"
          secondaryLabel="Ver precios"
          secondaryTo="/pricing"
          highlights={solutionsPageHighlights}
        />

        <section className="relative pb-24">
          <div className="mx-auto max-w-7xl px-5 md:px-6 lg:px-8">
            <div className="mb-12 max-w-3xl">
              <p className="editorial-kicker text-amber-300">Oferta base</p>
              <h2 className="mt-4 font-display text-4xl text-white md:text-6xl">Producto principal + modulos que tambien pueden vivir por separado.</h2>
              <p className="mt-5 text-base leading-8 text-slate-300 md:text-lg">
                AILinkCinema combina una capa completa de producto con aplicaciones especializadas para que cada equipo pueda entrar por una necesidad concreta o desplegar un flujo integral.
              </p>
            </div>

            <SolutionGrid solutions={allSolutions} />
          </div>
        </section>

        <section className="relative border-y border-white/10 bg-[#09111c]/80 py-24">
          <div className="mx-auto max-w-7xl px-5 md:px-6 lg:px-8">
            <PricingModelBlock
              title={pricingOverview.cidSummary.title}
              priceLines={[pricingOverview.cidSummary.setup, pricingOverview.cidSummary.monthly]}
              description={pricingOverview.cidSummary.note}
              bullets={solutionsMarketingNotes}
              featured
            />
          </div>
        </section>
      </main>

      <footer className="border-t border-white/10 py-10">
        <div className="mx-auto grid max-w-7xl gap-8 px-5 md:px-6 lg:grid-cols-[1fr_auto] lg:items-center lg:px-8">
          <div>
            <p className="font-display text-3xl text-white">AILinkCinema</p>
            <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-400">Producto principal, apps especializadas y desarrollo a medida para workflows cinematograficos reales.</p>
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
          <p>Cada modulo puede contratarse por separado y todos pueden integrarse dentro de CID.</p>
        </div>
      </footer>
    </div>
  )
}
