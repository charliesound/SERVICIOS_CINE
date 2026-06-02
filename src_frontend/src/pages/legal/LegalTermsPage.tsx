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

export default function LegalTermsPage() {
  const { t } = useLanguage()

  return (
    <LegalPageShell
      eyebrow={t('public.legal.terms.eyebrow')}
      title={t('public.legal.terms.title')}
      description={t('public.legal.terms.description')}
    >
      <Section title={t('public.legal.terms.sections.access.title')}>
        <p>{t('public.legal.terms.sections.access.p1')}</p>
        <p>{t('public.legal.terms.sections.access.p2')}</p>
      </Section>

      <Section title={t('public.legal.terms.sections.allowed.title')}>
        <p>{t('public.legal.terms.sections.allowed.intro')}</p>
        <p>{t('public.legal.terms.sections.allowed.itemExplore')}</p>
        <p>{t('public.legal.terms.sections.allowed.itemEvaluate')}</p>
        <p>{t('public.legal.terms.sections.allowed.itemMaterials')}</p>
        <p>{t('public.legal.terms.sections.allowed.itemCollaborate')}</p>
      </Section>

      <Section title={t('public.legal.terms.sections.forbidden.title')}>
        <p>{t('public.legal.terms.sections.forbidden.intro')}</p>
        <p>{t('public.legal.terms.sections.forbidden.itemIllegal')}</p>
        <p>{t('public.legal.terms.sections.forbidden.itemRights')}</p>
        <p>{t('public.legal.terms.sections.forbidden.itemSecurity')}</p>
        <p>{t('public.legal.terms.sections.forbidden.itemFinalService')}</p>
      </Section>

      <Section title={t('public.legal.terms.sections.productStatus.title')}>
        <p>{t('public.legal.terms.sections.productStatus.p1')}</p>
      </Section>

      <Section title={t('public.legal.terms.sections.accounts.title')}>
        <p>{t('public.legal.terms.sections.accounts.p1')}</p>
      </Section>

      <Section title={t('public.legal.terms.sections.materials.title')}>
        <p>{t('public.legal.terms.sections.materials.p1')}</p>
      </Section>

      <Section title={t('public.legal.terms.sections.future.title')}>
        <p>{t('public.legal.terms.sections.future.p1')}</p>
      </Section>
    </LegalPageShell>
  )
}
