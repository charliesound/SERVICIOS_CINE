import clsx from 'clsx'

interface DocumentStatusBadgeProps {
  status: string
}

const statusStyles: Record<string, string> = {
  registered: 'bg-slate-500/10 text-slate-300 border border-slate-500/20',
  extracted: 'bg-blue-500/10 text-blue-300 border border-blue-500/20',
  needs_review: 'bg-amber-500/10 text-amber-300 border border-amber-500/20',
  classified: 'bg-purple-500/10 text-purple-300 border border-purple-500/20',
  structured: 'bg-cyan-500/10 text-cyan-300 border border-cyan-500/20',
  approved: 'bg-green-500/10 text-green-300 border border-green-500/20',
  pending_ocr: 'bg-orange-500/10 text-orange-300 border border-orange-500/20',
  unsupported: 'bg-red-500/10 text-red-300 border border-red-500/20',
  completed: 'bg-blue-500/10 text-blue-300 border border-blue-500/20',
  failed: 'bg-red-500/10 text-red-300 border border-red-500/20',
  suggested: 'bg-violet-500/10 text-violet-300 border border-violet-500/20',
  pending_review: 'bg-amber-500/10 text-amber-300 border border-amber-500/20',
}

export default function DocumentStatusBadge({ status }: DocumentStatusBadgeProps) {
  return (
    <span className={clsx('badge capitalize', statusStyles[status] || statusStyles.registered)}>
      {status.replace(/_/g, ' ')}
    </span>
  )
}
