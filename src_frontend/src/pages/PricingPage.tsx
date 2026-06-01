import { Link } from 'react-router-dom'
import { ShieldCheck } from 'lucide-react'
import PublicHeader from '@/components/common/PublicHeader'
import LandingAmbientScene from '@/components/landing/LandingAmbientScene'
import SolutionHero from '@/components/solutions/SolutionHero'
import PricingModelBlock from '@/components/solutions/PricingModelBlock'
import SolutionGrid from '@/components/solutions/SolutionGrid'
import {
  allSolutions,
  pricingHeroContent,
  pricingOverview,
  pricingPageHighlights,
  publicFooterLinks,
  publicLegalLinks,
  solutionsMarketingNotes,
} from '@/data/solutionsContent'
import { useSeo } from '@/hooks/useSeo'
import { useLanguage } from '@/i18n'
import { buildAbsoluteUrl, buildBreadcrumbStructuredData } from '@/utils/seo'

export default function PricingPage() {
  const { t } = useLanguage()
  const description =
    'Precios de AILinkCinema para CID Core, modulos independientes y desarrollo a medida aplicado a preproduccion cinematografica.'

  useSeo({
    title: 'Precios de software IA para cine',
    description,
    path: '/pricing',
    robots: 'index, follow',
    keywords: ['precios software cine', 'precio storyboard ai', 'precio desglose guion', 'software audiovisual premium'],
    structuredData: [
      buildBreadcrumbStructuredData([
        { name: 'Inicio', path: '/' },
        { name: 'Precios', path: '/pricing' },
      ]),
      {
        '@context': 'https://schema.org',
        '@type': 'OfferCatalog',
        name: 'Catalogo de precios AILinkCinema',
        url: buildAbsoluteUrl('/pricing'),
        itemListElement: allSolutions.map((solution) => ({
          '@type': 'Offer',
          description: solution.priceLabel,
          itemOffered: {
            '@type': 'SoftwareApplication',
            name: solution.title,
            description: solution.description,
            url: buildAbsoluteUrl(solution.path),
          },
        })),
      },
    ],
  })

  return (
    <div className="landing-shell landing-brand-shell min-h-screen text-white">
      <LandingAmbientScene />
      <div className="landing-noise" />
      <div className="landing-backdrop" />

      <PublicHeader eyebrowKey="public.header.pricing" />

      <main>
        <SolutionHero
          eyebrow="AILinkCinema / Precios"
          title={pricingHeroContent.title}
          description={pricingHeroContent.description}
          primaryLabel={t('common.cta.viewCid')}
          primaryTo="/solutions/cid"
          secondaryLabel={t('common.cta.viewSolutions')}
          secondaryTo="/solutions"
          highlights={pricingPageHighlights}
        />

        <section className="relative pb-24">
          <div className="mx-auto max-w-7xl px-5 md:px-6 lg:px-8">
            <PricingModelBlock
              title={pricingOverview.cidSummary.title}
              priceLines={[pricingOverview.cidSummary.setup, pricingOverview.cidSummary.monthly]}
              description={pricingOverview.cidSummary.note}
              bullets={solutionsMarketingNotes}
              featured
            />

            <div className="mt-10 grid gap-6 xl:grid-cols-[0.54fr_0.46fr]">
              <section className="solution-card">
                <p className="solution-eyebrow text-cyan-200">{t('pages.pricing.customEyebrow')}</p>
                <h2 className="mt-3 text-3xl font-semibold text-white">{pricingOverview.customDevelopment.title}</h2>
                <p className="mt-4 text-sm leading-7 text-slate-300">{pricingOverview.customDevelopment.description}</p>
              </section>

              <section className="solution-card solution-card-featured">
                <p className="solution-eyebrow text-amber-300">{t('pages.pricing.ruleEyebrow')}</p>
                <h2 className="mt-3 text-3xl font-semibold text-white">{t('pages.pricing.ruleTitle')}</h2>
                <div className="mt-6 flex flex-wrap gap-2.5">
                  {solutionsMarketingNotes.map((note) => (
                    <span key={note} className="landing-pill text-slate-200">{note}</span>
                  ))}
                </div>
              </section>
            </div>
          </div>
        </section>

        <section className="relative border-y border-white/10 bg-[#09111c]/80 py-24">
          <div className="mx-auto max-w-7xl px-5 md:px-6 lg:px-8">
            <div className="mb-12 max-w-3xl">
              <p className="editorial-kicker text-amber-300">{t('pages.pricing.modulesEyebrow')}</p>
              <h2 className="mt-4 font-display text-4xl text-white md:text-6xl">{t('pages.pricing.modulesTitle')}</h2>
            </div>
            <SolutionGrid solutions={allSolutions} />
          </div>
        </section>
      </main>

      <footer className="border-t border-white/10 py-10">
        <div className="mx-auto grid max-w-7xl gap-8 px-5 md:px-6 lg:grid-cols-[1fr_auto] lg:items-center lg:px-8">
          <div>
            <p className="font-display text-3xl text-white">AILinkCinema</p>
            <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-400">{t('pages.pricing.footerText')}</p>
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
          <p>{t('pages.pricing.footerNote')}</p>
        </div>
      </footer>
    </div>
  )
}
