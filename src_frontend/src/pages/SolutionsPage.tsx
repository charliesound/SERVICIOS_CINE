import { Link } from 'react-router-dom'
import { ShieldCheck } from 'lucide-react'
import PublicHeader from '@/components/common/PublicHeader'
import LandingAmbientScene from '@/components/landing/LandingAmbientScene'
import SolutionHero from '@/components/solutions/SolutionHero'
import SolutionGrid from '@/components/solutions/SolutionGrid'
import PricingModelBlock from '@/components/solutions/PricingModelBlock'
import {
   allSolutions,
   pricingOverview,
   publicFooterLinks,
   publicLegalLinks,
   solutionsMarketingNotes,
   solutionsPageHighlights,
  } from '@/data/solutionsContent'
import { CID_CORE_FUTURE_PRODUCTS, isCidCoreCustomerVisibleSolution } from '@/config/cidCoreScope'
import { useSeo } from '@/hooks/useSeo'
import { useLanguage } from '@/i18n'
import { buildAbsoluteUrl, buildBreadcrumbStructuredData } from '@/utils/seo'

export default function SolutionsPage() {
  const { t } = useLanguage()
  const visibleSolutions = allSolutions.filter((solution) => isCidCoreCustomerVisibleSolution(solution.slug))
  const description =
    'Catalogo de soluciones IA para cine con foco en preproduccion: CID, desglose de guion, storyboard, planificacion, pitch, promo video y VFX.'

  useSeo({
    title: 'Soluciones IA para cine y audiovisual',
    description,
    path: '/solutions',
    robots: 'index, follow',
    keywords: ['soluciones ia cine', 'software preproduccion cinematografica', 'storyboard ai', 'desglose de guion', 'pitch audiovisual'],
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
          itemListElement: visibleSolutions.map((solution, index) => ({
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

      <PublicHeader eyebrowKey="public.header.solutions" ctaTo="/pricing" ctaKey="common.cta.viewPricing" />

       <main>
         <SolutionHero
           eyebrow={t('pages.solutions.heroEyebrow')}
           title={t('pages.solutions.heroTitle')}
            description={t('pages.solutions.heroDescription')}
           primaryLabel={t('common.cta.exploreCid')}
           primaryTo="/solutions/cid"
           secondaryLabel={t('common.cta.viewPricing')}
           secondaryTo="/pricing"
           highlights={solutionsPageHighlights}
         />

         <section className="relative pb-28">
           <div className="mx-auto max-w-7xl px-5 md:px-6 lg:px-8">
             <div className="mb-16 max-w-3xl">
               <p className="editorial-kicker text-amber-300">{t('pages.solutions.baseEyebrow')}</p>
               <h2 className="mt-6 font-display text-5xl text-white md:text-6xl">{t('pages.solutions.baseTitle')}</h2>
               <p className="mt-6 text-lg leading-9 text-slate-300 md:text-xl md:leading-10">
                 {t('pages.solutions.baseText')}
               </p>
             </div>

              <SolutionGrid solutions={visibleSolutions} />

              <div className="mt-10 rounded-[1.6rem] border border-cyan-400/20 bg-cyan-400/8 p-6 text-sm text-cyan-50">
                <p className="font-semibold text-cyan-100">{t('pages.solutions.futureTitle')}</p>
                <p className="mt-2 text-cyan-100/80">
                  {t('pages.solutions.futureText')}
                </p>
                <div className="mt-4 flex flex-wrap gap-2">
                  {CID_CORE_FUTURE_PRODUCTS.map((product) => (
                    <span key={product} className="landing-pill border-cyan-300/20 text-cyan-100">
                      {product}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </section>

         <section className="relative border-y border-white/10 bg-[#09111c]/80 py-28">
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
            <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-400">{t('pages.solutions.footerText')}</p>
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
          <p>{t('pages.solutions.footerNote')}</p>
        </div>
      </footer>
    </div>
  )
}
