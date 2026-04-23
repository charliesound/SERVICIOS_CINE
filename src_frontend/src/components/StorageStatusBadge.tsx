import clsx from 'clsx'

interface StorageStatusBadgeProps {
  status: string
}

const statusStyles: Record<string, string> = {
  active: 'bg-green-500/10 text-green-300 border border-green-500/20',
  completed: 'bg-green-500/10 text-green-300 border border-green-500/20',
  indexed: 'bg-green-500/10 text-green-300 border border-green-500/20',
  inactive: 'bg-slate-500/10 text-slate-300 border border-slate-500/20',
  running: 'bg-blue-500/10 text-blue-300 border border-blue-500/20',
  error: 'bg-red-500/10 text-red-300 border border-red-500/20',
  failed: 'bg-red-500/10 text-red-300 border border-red-500/20',
  revoked: 'bg-red-500/10 text-red-300 border border-red-500/20',
  expired: 'bg-amber-500/10 text-amber-300 border border-amber-500/20',
}

export default function StorageStatusBadge({ status }: StorageStatusBadgeProps) {
  const normalizedStatus = status.trim().toLowerCase()

  return (
    <span
      className={clsx(
        'inline-flex items-center rounded-full px-2.5 py-1 text-xs font-medium capitalize',
        statusStyles[normalizedStatus] ?? 'bg-blue-500/10 text-blue-300 border border-blue-500/20',
      )}
    >
      {normalizedStatus}
    </span>
  )
}
