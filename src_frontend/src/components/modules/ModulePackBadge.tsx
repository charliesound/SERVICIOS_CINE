import clsx from 'clsx'

interface ModulePackBadgeProps {
  pack?: string | null
}

export default function ModulePackBadge({ pack }: ModulePackBadgeProps) {
  if (!pack) return null

  return (
    <span className={clsx('inline-flex items-center rounded-full border border-cyan-400/20 bg-cyan-400/10 px-2.5 py-1 text-[11px] font-medium text-cyan-100')}>
      Pack: {pack}
    </span>
  )
}
