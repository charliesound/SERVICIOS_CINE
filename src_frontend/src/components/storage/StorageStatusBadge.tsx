import clsx from 'clsx'

interface StorageStatusBadgeProps {
  status: string
}

const statusStyles: Record<string, string> = {
  draft: 'bg-slate-500/10 text-slate-300 border border-slate-500/20',
  validated: 'bg-blue-500/10 text-blue-300 border border-blue-500/20',
  authorized: 'bg-green-500/10 text-green-300 border border-green-500/20',
  error: 'bg-red-500/10 text-red-300 border border-red-500/20',
  active: 'bg-amber-500/10 text-amber-300 border border-amber-500/20',
  invalid: 'bg-red-500/10 text-red-300 border border-red-500/20',
}

export default function StorageStatusBadge({ status }: StorageStatusBadgeProps) {
  return (
    <span className={clsx('badge capitalize', statusStyles[status] || statusStyles.draft)}>
      {status.replace(/_/g, ' ')}
    </span>
  )
}
