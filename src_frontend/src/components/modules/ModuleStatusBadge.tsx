import clsx from 'clsx'
import { useLanguage } from '@/i18n'

interface ModuleStatusBadgeProps {
  value: string
  variant?: 'technical' | 'commercial'
}

const STATUS_META: Record<string, { labelKey: string; tone: string }> = {
  HECHO: { labelKey: 'components.modules.statusBadge.done', tone: 'bg-emerald-500/12 text-emerald-300 border-emerald-400/20' },
  PARCIAL_AVANZADO: { labelKey: 'components.modules.statusBadge.advancedPartial', tone: 'bg-amber-500/12 text-amber-200 border-amber-400/20' },
  PARCIAL_INICIAL: { labelKey: 'components.modules.statusBadge.initialPartial', tone: 'bg-sky-500/12 text-sky-200 border-sky-400/20' },
  PENDIENTE: { labelKey: 'components.modules.statusBadge.pending', tone: 'bg-slate-500/12 text-slate-300 border-slate-400/20' },
}

export default function ModuleStatusBadge({ value, variant = 'technical' }: ModuleStatusBadgeProps) {
  const { t } = useLanguage()
  const meta = STATUS_META[value] || STATUS_META.PENDIENTE
  const prefix = variant === 'technical' ? t('components.modules.statusBadge.technical') : t('components.modules.statusBadge.commercial')

  return (
    <span
      className={clsx(
        'inline-flex items-center rounded-full border px-2.5 py-1 text-[11px] font-medium tracking-wide',
        meta.tone,
      )}
    >
      {prefix}: {t(meta.labelKey)}
    </span>
  )
}
