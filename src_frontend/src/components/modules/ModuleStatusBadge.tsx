import clsx from 'clsx'

interface ModuleStatusBadgeProps {
  value: string
  variant?: 'technical' | 'commercial'
}

const STATUS_META: Record<string, { label: string; tone: string }> = {
  HECHO: { label: 'Hecho', tone: 'bg-emerald-500/12 text-emerald-300 border-emerald-400/20' },
  PARCIAL_AVANZADO: { label: 'Parcial avanzado', tone: 'bg-amber-500/12 text-amber-200 border-amber-400/20' },
  PARCIAL_INICIAL: { label: 'Parcial inicial', tone: 'bg-sky-500/12 text-sky-200 border-sky-400/20' },
  PENDIENTE: { label: 'Pendiente', tone: 'bg-slate-500/12 text-slate-300 border-slate-400/20' },
}

export default function ModuleStatusBadge({ value, variant = 'technical' }: ModuleStatusBadgeProps) {
  const meta = STATUS_META[value] || STATUS_META.PENDIENTE
  const prefix = variant === 'technical' ? 'Técnico' : 'Comercial'

  return (
    <span
      className={clsx(
        'inline-flex items-center rounded-full border px-2.5 py-1 text-[11px] font-medium tracking-wide',
        meta.tone,
      )}
    >
      {prefix}: {meta.label}
    </span>
  )
}
