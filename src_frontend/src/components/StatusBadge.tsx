interface StatusBadgeProps {
  status: string
  label?: string
  size?: 'sm' | 'md' | 'lg'
}

const STATUS_CONFIG: Record<string, { bg: string; text: string; label: string }> = {
  ready: { bg: 'bg-green-100', text: 'text-green-800', label: 'Listo' },
  partial: { bg: 'bg-yellow-100', text: 'text-yellow-800', label: 'Parcial' },
  missing: { bg: 'bg-gray-100', text: 'text-gray-800', label: 'Pendiente' },
  warning: { bg: 'bg-orange-100', text: 'text-orange-800', label: 'Atención' },
  needs_review: { bg: 'bg-blue-100', text: 'text-blue-800', label: 'Revisar' },
  approved: { bg: 'bg-green-100', text: 'text-green-800', label: 'Aprobado' },
  pending: { bg: 'bg-yellow-100', text: 'text-yellow-800', label: 'Pendiente' },
  locked: { bg: 'bg-red-100', text: 'text-red-800', label: 'Bloqueado' },
  roadmap: { bg: 'bg-gray-100', text: 'text-gray-800', label: 'En roadmap' },
  generated: { bg: 'bg-green-100', text: 'text-green-800', label: 'Generado' },
  draft: { bg: 'bg-gray-100', text: 'text-gray-800', label: 'Borrador' },
  archived: { bg: 'bg-gray-100', text: 'text-gray-500', label: 'Archivado' },
  interested: { bg: 'bg-green-100', text: 'text-green-800', label: 'Interesada' },
  rejected: { bg: 'bg-red-100', text: 'text-red-800', label: 'Rechazada' },
}

export function StatusBadge({ status, label, size = 'md' }: StatusBadgeProps) {
  const config = STATUS_CONFIG[status] || STATUS_CONFIG.missing
  const displayLabel = label || config.label

  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2 py-1 text-sm',
    lg: 'px-3 py-1.5 text-base',
  }

  return (
    <span className={`inline-flex items-center rounded ${config.bg} ${config.text} ${sizeClasses[size]} font-medium`}>
      {displayLabel}
    </span>
  )
}