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

export default function LegalNoticePage() {
  const { t } = useLanguage()

  return (
    <LegalPageShell
      eyebrow={t('public.legal.notice.eyebrow')}
      title={t('public.legal.notice.title')}
      description={t('public.legal.notice.description')}
    >
      <Section title={t('public.legal.notice.sections.nature.title')}>
        <p>{t('public.legal.notice.sections.nature.p1')}</p>
        <p>{t('public.legal.notice.sections.nature.p2')}</p>
      </Section>

      <Section title={t('public.legal.notice.sections.responsible.title')}>
        <p>{t('public.legal.notice.sections.responsible.p1')}</p>
        <p>{t('public.legal.notice.sections.responsible.p2')}</p>
      </Section>

      <Section title={t('public.legal.notice.sections.content.title')}>
        <p>{t('public.legal.notice.sections.content.p1')}</p>
      </Section>

      <Section title={t('public.legal.notice.sections.availability.title')}>
        <p>{t('public.legal.notice.sections.availability.p1')}</p>
        <p>{t('public.legal.notice.sections.availability.p2')}</p>
      </Section>

      <Section title={t('public.legal.notice.sections.limitation.title')}>
        <p>{t('public.legal.notice.sections.limitation.p1')}</p>
      </Section>

      <Section title={t('public.legal.notice.sections.finalVersion.title')}>
        <p>{t('public.legal.notice.sections.finalVersion.p1')}</p>
      </Section>
    </LegalPageShell>
  )
}
