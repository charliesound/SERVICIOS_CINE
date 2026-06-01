import { Link } from 'react-router-dom'
import { ArrowRight, CheckCircle2, Clapperboard, Film, Languages, Layers3, PlayCircle } from 'lucide-react'
import LanguageToggle from '@/components/common/LanguageToggle'
import { t, useLanguage } from '@/i18n'
import { useSeo } from '@/hooks/useSeo'

type ModuleItem = {
  key:
    | 'scriptIntelligence'
    | 'storyboardStudio'
    | 'productionBreakdown'
    | 'clientFeedbackMemory'
    | 'pitchDossier'
    | 'comfyuiWorkflow'
    | 'dubbingLocalization'
    | 'distributionAudience'
    | 'editorialNleBridge'
}

type FeatureCardProps = {
  title: string
  body: string
}

function Section({ id, title, subtitle, children }: { id: string; title: string; subtitle?: string; children: React.ReactNode }) {
  return (
    <section id={id} className="border-t border-white/8 py-20 first:border-t-0">
      <div className="mx-auto max-w-7xl px-5 md:px-8">
        <div className="max-w-3xl">
          <h2 className="text-3xl font-semibold tracking-tight text-white md:text-5xl">{title}</h2>
          {subtitle ? <p className="mt-4 text-lg leading-8 text-slate-300">{subtitle}</p> : null}
        </div>
        <div className="mt-10">{children}</div>
      </div>
    </section>
  )
}

function FeatureCard({ title, body }: FeatureCardProps) {
  return (
    <article className="rounded-3xl border border-white/10 bg-white/[0.04] p-6 shadow-[0_24px_80px_rgba(2,6,23,0.26)]">
      <h3 className="text-xl font-semibold text-white">{title}</h3>
      <p className="mt-3 leading-7 text-slate-300">{body}</p>
    </article>
  )
}

function ModuleCard({ title, description, badge }: { title: string; description: string; badge?: string }) {
  return (
    <article className="rounded-3xl border border-white/10 bg-[#0e1118] p-6 shadow-[0_24px_80px_rgba(2,6,23,0.24)]">
      <div className="flex items-start justify-between gap-3">
        <h3 className="text-xl font-semibold text-white">{title}</h3>
        {badge ? (
          <span className="rounded-full border border-amber-400/25 bg-amber-400/10 px-3 py-1 text-[10px] font-semibold uppercase tracking-[0.24em] text-amber-200">
            {badge}
          </span>
        ) : null}
      </div>
      <p className="mt-4 leading-7 text-slate-300">{description}</p>
    </article>
  )
}

export default function LandingPage() {
  const { language } = useLanguage()

  useSeo({
    title: `${t('common.brand.name')} | ${t('landing.hero.title')}`,
    description: t('landing.hero.subtitle'),
    path: '/',
    robots: 'index, follow',
  })

  const modules: ModuleItem[] = [
    { key: 'scriptIntelligence' },
    { key: 'storyboardStudio' },
    { key: 'productionBreakdown' },
    { key: 'clientFeedbackMemory' },
    { key: 'pitchDossier' },
    { key: 'comfyuiWorkflow' },
    { key: 'dubbingLocalization' },
    { key: 'distributionAudience' },
    { key: 'editorialNleBridge' },
  ]

  const problemCards = [
    { title: t('landing.problems.card1Title'), body: t('landing.problems.card1Body') },
    { title: t('landing.problems.card2Title'), body: t('landing.problems.card2Body') },
    { title: t('landing.problems.card3Title'), body: t('landing.problems.card3Body') },
    { title: t('landing.problems.card4Title'), body: t('landing.problems.card4Body') },
  ]

  const useCases = [
    { title: t('landing.useCases.case1Title'), body: t('landing.useCases.case1Body') },
    { title: t('landing.useCases.case2Title'), body: t('landing.useCases.case2Body') },
    { title: t('landing.useCases.case3Title'), body: t('landing.useCases.case3Body') },
    { title: t('landing.useCases.case4Title'), body: t('landing.useCases.case4Body') },
  ]

  const plans = [
    { title: t('landing.pricing.starterTitle'), body: t('landing.pricing.starterBody'), meta: t('landing.pricing.starterMeta') },
    { title: t('landing.pricing.suiteTitle'), body: t('landing.pricing.suiteBody'), meta: t('landing.pricing.suiteMeta') },
    { title: t('landing.pricing.enterpriseTitle'), body: t('landing.pricing.enterpriseBody'), meta: t('landing.pricing.enterpriseMeta') },
  ]

  return (
    <div className="min-h-screen bg-[#07090d] text-white">
      <header className="sticky top-0 z-40 border-b border-white/8 bg-[#07090d]/85 backdrop-blur-2xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-5 py-4 md:px-8">
          <Link to="/" className="flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-amber-300 to-amber-500 text-black shadow-[0_0_36px_rgba(245,158,11,0.22)]">
              <Clapperboard className="h-6 w-6" />
            </div>
            <div>
              <p className="text-xl font-bold tracking-tight text-white">{t('common.brand.name')}</p>
              <p className="text-[11px] uppercase tracking-[0.28em] text-amber-300/70">{t('common.brand.suite')}</p>
            </div>
          </Link>

          <nav className="hidden items-center gap-6 text-sm text-slate-300 lg:flex">
            <a href="#what" className="transition-colors hover:text-white">{t('landing.nav.what')}</a>
            <a href="#problems" className="transition-colors hover:text-white">{t('landing.nav.problems')}</a>
            <a href="#modules" className="transition-colors hover:text-white">{t('landing.nav.modules')}</a>
            <a href="#suite" className="transition-colors hover:text-white">{t('landing.nav.suite')}</a>
            <a href="#pricing" className="transition-colors hover:text-white">{t('landing.nav.pricing')}</a>
            <a href="#demo" className="transition-colors hover:text-white">{t('landing.nav.demo')}</a>
          </nav>

          <div className="flex items-center gap-3">
            <LanguageToggle />
            <Link to="/pricing" className="hidden rounded-full bg-amber-400 px-5 py-3 text-sm font-semibold text-black transition-transform hover:-translate-y-0.5 sm:inline-flex">
              {t('common.cta.requestDemo')}
            </Link>
          </div>
        </div>
      </header>

      <main>
        <section className="relative overflow-hidden border-b border-white/8 py-24 md:py-32">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(245,158,11,0.16),transparent_32%),radial-gradient(circle_at_80%_20%,rgba(59,130,246,0.14),transparent_26%)]" />
          <div className="mx-auto grid max-w-7xl items-center gap-14 px-5 md:px-8 lg:grid-cols-[1.2fr_0.8fr]">
            <div className="relative z-10">
              <div className="inline-flex items-center gap-2 rounded-full border border-amber-400/20 bg-amber-400/10 px-4 py-2 text-[11px] font-semibold uppercase tracking-[0.24em] text-amber-200">
                <Film className="h-3.5 w-3.5" />
                {t('landing.hero.eyebrow')}
              </div>
              <h1 className="mt-6 max-w-4xl text-4xl font-semibold leading-tight text-white md:text-6xl">
                {t('landing.hero.title')}
              </h1>
              <p className="mt-6 max-w-3xl text-lg leading-8 text-slate-300 md:text-xl">
                {t('landing.hero.subtitle')}
              </p>
              <div className="mt-8 flex flex-wrap gap-4">
                <Link to="/pricing" className="inline-flex items-center gap-2 rounded-full bg-amber-400 px-6 py-3 font-semibold text-black transition-transform hover:-translate-y-0.5">
                  {t('landing.hero.primary')}
                  <ArrowRight className="h-4 w-4" />
                </Link>
                <a href="#modules" className="inline-flex items-center gap-2 rounded-full border border-white/12 px-6 py-3 font-semibold text-white transition-colors hover:bg-white/6">
                  {t('landing.hero.secondary')}
                </a>
              </div>
              <p className="mt-6 max-w-2xl text-sm leading-7 text-slate-400">{t('landing.hero.support')}</p>
            </div>

            <div className="relative z-10 rounded-[2rem] border border-white/10 bg-white/[0.04] p-8 shadow-[0_30px_100px_rgba(0,0,0,0.3)]">
              <div className="flex items-center gap-3 text-amber-300">
                <Languages className="h-5 w-5" />
                <span className="text-sm font-semibold uppercase tracking-[0.24em]">{t('common.language.toggleLabel')}</span>
              </div>
              <p className="mt-4 text-3xl font-semibold text-white">{language.toUpperCase()}</p>
              <p className="mt-3 leading-7 text-slate-300">{t('landing.demo.body')}</p>
              <div className="mt-8 grid gap-4">
                <div className="rounded-2xl border border-white/8 bg-[#0d1117] p-4">
                  <p className="text-sm font-semibold text-white">{t('modules.editorialNleBridge.title')}</p>
                  <p className="mt-2 text-sm leading-6 text-slate-300">{t('modules.editorialNleBridge.nles')}</p>
                </div>
                <div className="rounded-2xl border border-white/8 bg-[#0d1117] p-4">
                  <p className="text-sm font-semibold text-white">{t('landing.cidSuite.title')}</p>
                  <p className="mt-2 text-sm leading-6 text-slate-300">{t('landing.cidSuite.point3')}</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        <Section id="what" title={t('landing.what.title')} subtitle={t('landing.what.body')}>
          <div className="grid gap-4 md:grid-cols-3">
            <FeatureCard title={t('landing.what.point1')} body={t('landing.what.body')} />
            <FeatureCard title={t('landing.what.point2')} body={t('landing.standalone.body')} />
            <FeatureCard title={t('landing.what.point3')} body={t('landing.cidSuite.body')} />
          </div>
        </Section>

        <Section id="problems" title={t('landing.problems.title')}>
          <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
            {problemCards.map((card) => (
              <FeatureCard key={card.title} title={card.title} body={card.body} />
            ))}
          </div>
        </Section>

        <Section id="modules" title={t('landing.modules.title')} subtitle={t('landing.modules.subtitle')}>
          <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
            {modules.map(({ key }) => (
              <ModuleCard
                key={key}
                title={t(`modules.${key}.title`)}
                description={t(`modules.${key}.description`)}
                badge={key === 'editorialNleBridge' ? t('landing.standalone.badge') : undefined}
              />
            ))}
          </div>
        </Section>

        <Section id="standalone" title={t('landing.standalone.title')} subtitle={t('landing.standalone.body')}>
          <div className="grid gap-5 lg:grid-cols-[0.9fr_1.1fr]">
            <FeatureCard title={t('modules.editorialNleBridge.title')} body={t('modules.editorialNleBridge.independent')} />
            <div className="rounded-3xl border border-white/10 bg-white/[0.04] p-8">
              <div className="inline-flex items-center gap-2 rounded-full border border-amber-400/20 bg-amber-400/10 px-3 py-2 text-[10px] font-semibold uppercase tracking-[0.22em] text-amber-200">
                <Layers3 className="h-3.5 w-3.5" />
                {t('landing.standalone.badge')}
              </div>
              <div className="mt-6 grid gap-4 md:grid-cols-2">
                {modules.map(({ key }) => (
                  <div key={key} className="rounded-2xl border border-white/8 bg-[#0d1117] p-4">
                    <p className="font-semibold text-white">{t(`modules.${key}.title`)}</p>
                    <p className="mt-2 text-sm leading-6 text-slate-300">{t(`modules.${key}.description`)}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </Section>

        <Section id="suite" title={t('landing.cidSuite.title')} subtitle={t('landing.cidSuite.body')}>
          <div className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
            <div className="rounded-3xl border border-white/10 bg-white/[0.04] p-8">
              <ul className="space-y-4">
                {[t('landing.cidSuite.point1'), t('landing.cidSuite.point2'), t('landing.cidSuite.point3')].map((point) => (
                  <li key={point} className="flex gap-3 text-slate-300">
                    <CheckCircle2 className="mt-1 h-5 w-5 shrink-0 text-amber-300" />
                    <span className="leading-7">{point}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div className="rounded-3xl border border-amber-400/20 bg-amber-400/10 p-8">
              <p className="text-sm font-semibold uppercase tracking-[0.24em] text-amber-100">{t('landing.cidSuite.includedLabel')}</p>
              <h3 className="mt-4 text-2xl font-semibold text-white">{t('modules.editorialNleBridge.title')}</h3>
              <p className="mt-4 leading-7 text-amber-50/90">{t('modules.editorialNleBridge.included')}</p>
              <p className="mt-4 leading-7 text-amber-50/90">{t('modules.editorialNleBridge.description')}</p>
            </div>
          </div>
        </Section>

        <Section id="use-cases" title={t('landing.useCases.title')}>
          <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
            {useCases.map((item) => (
              <FeatureCard key={item.title} title={item.title} body={item.body} />
            ))}
          </div>
        </Section>

        <Section id="pricing" title={t('landing.pricing.title')}>
          <div className="grid gap-5 md:grid-cols-3">
            {plans.map((plan) => (
              <article key={plan.title} className="rounded-3xl border border-white/10 bg-white/[0.04] p-8">
                <h3 className="text-2xl font-semibold text-white">{plan.title}</h3>
                <p className="mt-4 leading-7 text-slate-300">{plan.body}</p>
                <p className="mt-6 text-sm font-medium uppercase tracking-[0.22em] text-amber-200">{plan.meta}</p>
              </article>
            ))}
          </div>
        </Section>

        <Section id="demo" title={t('landing.demo.title')} subtitle={t('landing.demo.body')}>
          <div className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
            <div className="rounded-3xl border border-white/10 bg-white/[0.04] p-8">
              <ul className="space-y-4">
                {[t('landing.demo.point1'), t('landing.demo.point2'), t('landing.demo.point3')].map((point) => (
                  <li key={point} className="flex gap-3 text-slate-300">
                    <PlayCircle className="mt-1 h-5 w-5 shrink-0 text-amber-300" />
                    <span className="leading-7">{point}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="rounded-3xl border border-white/10 bg-[#0e1118] p-8">
              <div className="space-y-4">
                <Link to="/pricing" className="inline-flex w-full items-center justify-center gap-2 rounded-full bg-amber-400 px-6 py-4 font-semibold text-black transition-transform hover:-translate-y-0.5">
                  {t('common.cta.requestDemo')}
                  <ArrowRight className="h-4 w-4" />
                </Link>
                <Link to="/register/demo" className="inline-flex w-full items-center justify-center rounded-full border border-white/12 px-6 py-4 font-semibold text-white transition-colors hover:bg-white/6">
                  {t('common.cta.contact')}
                </Link>
                <Link to="/onboarding" className="inline-flex w-full items-center justify-center rounded-full border border-white/12 px-6 py-4 font-semibold text-white transition-colors hover:bg-white/6">
                  {t('common.cta.startOnboarding')}
                </Link>
              </div>
            </div>
          </div>
        </Section>
      </main>

      <footer className="border-t border-white/8 py-8">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 px-5 text-sm text-slate-400 md:flex-row md:items-center md:justify-between md:px-8">
          <p>{t('landing.footer.line')}</p>
          <div className="flex items-center gap-3">
            <LanguageToggle />
          </div>
        </div>
      </footer>
    </div>
  )
}
