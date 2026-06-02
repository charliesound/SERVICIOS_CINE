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

export default function LegalPrivacyPage() {
  const { t } = useLanguage()

  return (
    <LegalPageShell
      eyebrow={t('public.legal.privacy.eyebrow')}
      title={t('public.legal.privacy.title')}
      description={t('public.legal.privacy.description')}
    >
      <Section title={t('public.legal.privacy.sections.purpose.title')}>
        <p>{t('public.legal.privacy.sections.purpose.p1')}</p>
        <p>{t('public.legal.privacy.sections.purpose.p2')}</p>
      </Section>

      <Section title={t('public.legal.privacy.sections.data.title')}>
        <p>{t('public.legal.privacy.sections.data.p1')}</p>
        <p>{t('public.legal.privacy.sections.data.p2')}</p>
      </Section>

      <Section title={t('public.legal.privacy.sections.uses.title')}>
        <p>{t('public.legal.privacy.sections.uses.intro')}</p>
        <p>{t('public.legal.privacy.sections.uses.itemDemo')}</p>
        <p>{t('public.legal.privacy.sections.uses.itemAccess')}</p>
        <p>{t('public.legal.privacy.sections.uses.itemProjects')}</p>
        <p>{t('public.legal.privacy.sections.uses.itemTraceability')}</p>
      </Section>

      <Section title={t('public.legal.privacy.sections.basis.title')}>
        <p>{t('public.legal.privacy.sections.basis.p1')}</p>
      </Section>

      <Section title={t('public.legal.privacy.sections.retention.title')}>
        <p>{t('public.legal.privacy.sections.retention.p1')}</p>
        <p>{t('public.legal.privacy.sections.retention.p2')}</p>
      </Section>

      <Section title={t('public.legal.privacy.sections.providers.title')}>
        <p>{t('public.legal.privacy.sections.providers.p1')}</p>
      </Section>

      <Section title={t('public.legal.privacy.sections.rights.title')}>
        <p>{t('public.legal.privacy.sections.rights.p1')}</p>
        <p>{t('public.legal.privacy.sections.rights.p2')}</p>
      </Section>
    </LegalPageShell>
  )
}
