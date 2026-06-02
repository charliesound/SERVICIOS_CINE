import { useLanguage } from '@/i18n'
import LegalPageShell from './LegalPageShell'

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="landing-panel rounded-[1.8rem] p-6 md:p-8">
      <h2 className="text-2xl font-semibold text-white">{title}</h2>
      <div className="mt-4 space-y-4 text-sm leading-8 text-slate-300 md:text-base">{children}</div>
    </section>
  )
}

export default function LegalAiContentPage() {
  const { t } = useLanguage()

  return (
    <LegalPageShell
      eyebrow={t('public.legal.aiContent.eyebrow')}
      title={t('public.legal.aiContent.title')}
      description={t('public.legal.aiContent.description')}
    >
      <Section title={t('public.legal.aiContent.sections.assisted.title')}>
        <p>{t('public.legal.aiContent.sections.assisted.p1')}</p>
      </Section>

      <Section title={t('public.legal.aiContent.sections.userMaterials.title')}>
        <p>{t('public.legal.aiContent.sections.userMaterials.p1')}</p>
      </Section>

      <Section title={t('public.legal.aiContent.sections.outputs.title')}>
        <p>{t('public.legal.aiContent.sections.outputs.p1')}</p>
      </Section>

      <Section title={t('public.legal.aiContent.sections.limitations.title')}>
        <p>{t('public.legal.aiContent.sections.limitations.p1')}</p>
        <p>{t('public.legal.aiContent.sections.limitations.p2')}</p>
      </Section>

      <Section title={t('public.legal.aiContent.sections.humanReview.title')}>
        <p>{t('public.legal.aiContent.sections.humanReview.p1')}</p>
      </Section>

      <Section title={t('public.legal.aiContent.sections.finalPolicy.title')}>
        <p>{t('public.legal.aiContent.sections.finalPolicy.p1')}</p>
      </Section>
    </LegalPageShell>
  )
}
