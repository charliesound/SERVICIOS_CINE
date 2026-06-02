import { Link } from 'react-router-dom'
import {
  ArrowRight,
  BadgeEuro,
  Briefcase,
  ClipboardList,
  FileStack,
  FileText,
  Film,
  FolderOpen,
  GitBranch,
  PlusCircle,
  Sparkles,
} from 'lucide-react'
import LandingReveal from '@/components/landing/LandingReveal'
import { useLanguage } from '@/i18n'
import { useSeo } from '@/hooks/useSeo'

const primaryActions = [
  { key: 'createProject', icon: PlusCircle, route: '/projects/new' },
  { key: 'myProjects', icon: FolderOpen, route: '/projects' },
  { key: 'documents', icon: FileText, route: '/documents' },
  { key: 'reports', icon: ClipboardList, route: '/reports/camera' },
] as const

const capabilityBlocks = [
  { key: 'budget', icon: BadgeEuro },
  { key: 'funding', icon: Briefcase },
  { key: 'storyboard', icon: Sparkles },
  { key: 'producerDossier', icon: FileStack },
  { key: 'editorialAssembly', icon: Film },
] as const

const recommendedFlowKeys = [
  'createProject',
  'uploadScript',
  'generateBudget',
  'reviewFunding',
  'createStoryboard',
  'prepareProducerDossier',
  'coordinateEditorialDelivery',
] as const

export default function ProducerStudioHubPage() {
  const { t } = useLanguage()

  useSeo({
    title: t('internal.producerStudioHub.seoTitle'),
    description: t('internal.producerStudioHub.seoDescription'),
    path: '/cid/producer',
    robots: 'noindex, nofollow',
  })

  return (
    <div className="space-y-8">
      <section className="relative overflow-hidden rounded-[2rem] border border-white/8 bg-dark-200/70 px-8 py-8 shadow-[0_28px_80px_rgba(2,6,23,0.32)]">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(245,158,11,0.18),transparent_28%),radial-gradient(circle_at_82%_16%,rgba(56,189,248,0.08),transparent_22%)]" />
        <div className="relative">
          <div className="inline-flex items-center gap-2 rounded-full border border-amber-400/20 bg-amber-400/10 px-4 py-2 text-[11px] font-semibold uppercase tracking-[0.24em] text-amber-100">
            <Briefcase className="h-3.5 w-3.5" />
            {t('internal.producerStudioHub.eyebrow')}
          </div>
          <h1 className="mt-6 text-4xl font-semibold tracking-tight text-white md:text-5xl">
            {t('internal.producerStudioHub.title')}
          </h1>
          <p className="mt-4 max-w-4xl text-lg leading-8 text-slate-300">
            {t('internal.producerStudioHub.subtitle')}
          </p>
        </div>
      </section>

      <section className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
        {primaryActions.map(({ key, icon: Icon, route }) => (
          <Link
            key={key}
            to={route}
            className="card group rounded-[1.6rem] border border-white/8 bg-white/[0.03] p-6 transition-all duration-200 hover:-translate-y-0.5 hover:border-amber-400/20 hover:bg-white/[0.05]"
          >
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-amber-400/10 text-amber-300">
              <Icon className="h-5 w-5" />
            </div>
            <h2 className="mt-5 text-xl font-semibold text-white">
              {t(`internal.producerStudioHub.actions.${key}.title`)}
            </h2>
            <p className="mt-3 text-sm leading-7 text-slate-400">
              {t(`internal.producerStudioHub.actions.${key}.description`)}
            </p>
            <span className="mt-5 inline-flex items-center gap-2 text-sm font-medium text-amber-300">
              {t(`internal.producerStudioHub.actions.${key}.cta`)}
              <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
            </span>
          </Link>
        ))}
      </section>

      <section className="rounded-[2rem] border border-white/8 bg-dark-200/60 p-8 shadow-[0_24px_64px_rgba(2,6,23,0.24)]">
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-sky-400/10 text-sky-300">
            <Sparkles className="h-5 w-5" />
          </div>
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-[0.24em] text-sky-200/80">
              {t('internal.producerStudioHub.capabilitiesEyebrow')}
            </p>
            <h2 className="mt-1 text-2xl font-semibold text-white">
              {t('internal.producerStudioHub.capabilitiesTitle')}
            </h2>
          </div>
        </div>

        <div className="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {capabilityBlocks.map(({ key, icon: Icon }) => (
            <LandingReveal key={key}>
              <div className="rounded-[1.5rem] border border-white/8 bg-white/[0.03] p-5">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-white/5 text-amber-300">
                  <Icon className="h-5 w-5" />
                </div>
                <h3 className="mt-4 text-lg font-semibold text-white">
                  {t(`internal.producerStudioHub.capabilities.${key}.title`)}
                </h3>
                <p className="mt-3 text-sm leading-7 text-slate-400">
                  {t(`internal.producerStudioHub.capabilities.${key}.text`)}
                </p>
              </div>
            </LandingReveal>
          ))}
        </div>
      </section>

      <section className="rounded-[2rem] border border-white/8 bg-gradient-to-br from-amber-500/10 via-white/[0.02] to-transparent p-8 shadow-[0_24px_64px_rgba(2,6,23,0.24)]">
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-amber-400/10 text-amber-300">
            <GitBranch className="h-5 w-5" />
          </div>
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-[0.24em] text-amber-200/80">
              {t('internal.producerStudioHub.flowEyebrow')}
            </p>
            <h2 className="mt-1 text-2xl font-semibold text-white">
              {t('internal.producerStudioHub.flowTitle')}
            </h2>
          </div>
        </div>

        <div className="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {recommendedFlowKeys.map((key, index) => (
            <div key={key} className="rounded-[1.4rem] border border-white/8 bg-white/[0.03] p-5">
              <div className="inline-flex rounded-full border border-amber-400/20 bg-amber-400/10 px-3 py-1 text-xs font-semibold text-amber-300">
                {String(index + 1).padStart(2, '0')}
              </div>
              <p className="mt-4 text-sm font-medium leading-6 text-white">
                {t(`internal.producerStudioHub.flow.steps.${key}`)}
              </p>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}
