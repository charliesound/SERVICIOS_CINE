import clsx from 'clsx'

interface ModuleAccessBadgeProps {
  enabled: boolean | null
}

export default function ModuleAccessBadge({ enabled }: ModuleAccessBadgeProps) {
  const label = enabled === null ? 'Catálogo informativo' : enabled ? 'Disponible' : 'Bloqueado'
  const tone = enabled === null
    ? 'bg-slate-500/12 text-slate-200 border-slate-400/20'
    : enabled
      ? 'bg-emerald-500/12 text-emerald-300 border-emerald-400/20'
      : 'bg-rose-500/12 text-rose-200 border-rose-400/20'

  return (
    <span className={clsx('inline-flex items-center rounded-full border px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.18em]', tone)}>
      {label}
    </span>
  )
}
