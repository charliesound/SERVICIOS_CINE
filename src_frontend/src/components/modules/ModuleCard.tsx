import { Link } from 'react-router-dom'
import clsx from 'clsx'
import {
  ArrowRight,
  BadgeEuro,
  Briefcase,
  ClipboardList,
  Clapperboard,
  Cpu,
  FileSearch,
  FolderKanban,
  LayoutTemplate,
  MonitorPlay,
  PanelsTopLeft,
  Scale,
  ShieldCheck,
  Sparkles,
  Waypoints,
  AudioWaveform,
} from 'lucide-react'
import type { LucideIcon } from 'lucide-react'
import type { ModuleInfo } from '@/types'
import ModuleAccessBadge from './ModuleAccessBadge'
import ModulePackBadge from './ModulePackBadge'
import ModuleStatusBadge from './ModuleStatusBadge'

export interface ModuleCardAction {
  label: string
  href?: string
  helperText?: string
  disabled?: boolean
  variant?: 'primary' | 'secondary'
}

interface ModuleCardProps {
  module: ModuleInfo
  enabled: boolean | null
  action: ModuleCardAction
  lockedReasonLabel?: string | null
}

const iconMap: Record<string, LucideIcon> = {
  core: ShieldCheck,
  script_analysis: FileSearch,
  pitch_deck: Briefcase,
  storyboard_ai: Clapperboard,
  pipeline_builder: Sparkles,
  breakdown: FolderKanban,
  budget_lite: BadgeEuro,
  production_manager_lite: PanelsTopLeft,
  call_sheet: ClipboardList,
  legal_documents: Scale,
  funding_grants: Waypoints,
  postproduction: MonitorPlay,
  sound_post_ai: AudioWaveform,
  delivery_distribution: LayoutTemplate,
}

const categoryLabels: Record<string, string> = {
  foundation: 'Base operativa',
  development: 'Desarrollo',
  preproduction: 'Preproducción',
  orchestration: 'Orquestación',
  production: 'Producción',
  legal: 'Legal',
  funding: 'Financiación',
  postproduction: 'Postproducción',
  delivery: 'Entrega y distribución',
}

function RequirementBadge({ icon: Icon, label }: { icon: LucideIcon; label: string }) {
  return (
    <span className="inline-flex items-center gap-1.5 rounded-full border border-white/10 bg-white/[0.04] px-2.5 py-1 text-[11px] text-slate-200">
      <Icon className="h-3.5 w-3.5 text-amber-300" />
      {label}
    </span>
  )
}

export default function ModuleCard({ module, enabled, action, lockedReasonLabel }: ModuleCardProps) {
  const Icon = iconMap[module.key] || Cpu
  const actionClasses = action.variant === 'primary' ? 'btn-primary' : 'btn-secondary'

  return (
    <article className="card card-hover flex h-full flex-col overflow-hidden rounded-[1.6rem] border border-white/8 bg-dark-200/60 p-0">
      <div className="relative overflow-hidden border-b border-white/6 px-6 py-6">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(245,158,11,0.16),transparent_35%),radial-gradient(circle_at_bottom_left,rgba(56,189,248,0.09),transparent_30%)]" />
        <div className="relative flex items-start justify-between gap-4">
          <div className="flex items-start gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-white/10 bg-white/5 text-amber-300 shadow-[0_16px_34px_rgba(15,23,42,0.28)]">
              <Icon className="h-5 w-5" />
            </div>
            <div>
              <p className="editorial-kicker text-slate-500">{categoryLabels[module.category] || module.category}</p>
              <h2 className="mt-2 text-xl font-semibold text-white">{module.name}</h2>
            </div>
          </div>
          <ModuleAccessBadge enabled={enabled} />
        </div>
      </div>

      <div className="flex flex-1 flex-col gap-5 px-6 py-6">
        <p className="text-sm leading-7 text-slate-300">{module.short_description}</p>

        <div className="flex flex-wrap gap-2">
          <ModuleStatusBadge value={module.status} variant="technical" />
          <ModuleStatusBadge value={module.commercial_status} variant="commercial" />
          <ModulePackBadge pack={module.recommended_pack} />
          {module.requires_gpu && <RequirementBadge icon={Cpu} label="Requiere GPU" />}
          {module.requires_local_gpu_node && <RequirementBadge icon={Sparkles} label="Nodo local" />}
        </div>

        {module.dependencies.length > 0 && (
          <div className="rounded-2xl border border-white/6 bg-white/[0.03] p-4">
            <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-slate-500">Dependencias</p>
            <div className="mt-3 flex flex-wrap gap-2">
              {module.dependencies.map((dependency) => (
                <span key={dependency} className="inline-flex items-center rounded-full border border-white/10 bg-dark-300/60 px-2.5 py-1 text-xs text-slate-300">
                  {dependency.replace(/_/g, ' ')}
                </span>
              ))}
            </div>
          </div>
        )}

        <div className="mt-auto space-y-3 rounded-2xl border border-white/6 bg-white/[0.03] p-4">
          <p className="text-sm font-medium text-white">Precio según plan o activación comercial</p>
          {lockedReasonLabel ? <p className="text-sm text-slate-400">{lockedReasonLabel}</p> : null}
          {action.helperText ? <p className="text-sm text-slate-400">{action.helperText}</p> : null}

          {action.href && !action.disabled ? (
            <Link to={action.href} className={clsx(actionClasses, 'flex w-full items-center justify-center gap-2 text-sm')}>
              {action.label}
              <ArrowRight className="h-4 w-4" />
            </Link>
          ) : (
            <button type="button" disabled className="flex w-full items-center justify-center gap-2 rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm font-medium text-slate-500">
              {action.label}
            </button>
          )}
        </div>
      </div>
    </article>
  )
}
