import { useState } from 'react'
import { Trash2, Image, Clock, AlertTriangle, CheckCircle2, Loader2, Copy, GitBranch } from 'lucide-react'
import { storyboardApi } from '@/api/storyboard'
import { AuthenticatedStoryboardShotImage } from '@/components/storyboard/AuthenticatedStoryboardShotImage'
import type { DirtyShot, StoryboardTraceRecord } from '@/types/storyboard'
import { getStoryboardShotDisplayText, getStoryboardUiLocale } from '@/utils/storyboardText'

interface ShotCardProps {
  shot: DirtyShot
  onUpdate: (shotId: string, updates: Partial<DirtyShot>) => void
  onDelete: (shotId: string) => void
  onOpenPicker: (shotId: string) => void
  isSaving: boolean
}

const RENDER_STATUS_CONFIG: Record<string, { label: string; color: string; icon: typeof Clock }> = {
  completed: { label: 'Render completado', color: 'text-green-400 bg-green-500/10', icon: CheckCircle2 },
  render_pending: { label: 'Render pendiente', color: 'text-amber-400 bg-amber-500/10', icon: Clock },
  no_asset: { label: 'Sin imagen', color: 'text-slate-500 bg-white/5', icon: AlertTriangle },
}

function hasStoryboardImageCandidate(shot: DirtyShot): boolean {
  const metadata = (shot.metadata_json || {}) as Record<string, unknown>
  const metadataPath = ['rendered_image_path', 'output_path', 'image_path', 'storage_path'].some((key) => {
    const value = metadata[key]
    return typeof value === 'string' && value.trim().length > 0
  })
  return Boolean(shot.asset_id || shot.thumbnail_url || shot.image_url || shot.preview_url || metadataPath)
}

function traceValue(value: unknown): string {
  if (value === null || value === undefined || value === '') return 'No disponible'
  if (typeof value === 'boolean') return value ? 'Sí' : 'No'
  return String(value)
}

function shortTraceValue(value: unknown, maxLength = 160): string {
  const text = traceValue(value)
  return text.length > maxLength ? `${text.slice(0, maxLength)}...` : text
}

export function ShotCard({ shot, onUpdate, onDelete, onOpenPicker, isSaving }: ShotCardProps) {
  const [localText, setLocalText] = useState(shot.narrative_text || getStoryboardShotDisplayText(shot, getStoryboardUiLocale()))
  const renderStatus = shot.render_status || 'no_asset'
  const statusCfg = RENDER_STATUS_CONFIG[renderStatus] || RENDER_STATUS_CONFIG.no_asset
  const StatusIcon = statusCfg.icon
  const hasImage = hasStoryboardImageCandidate(shot)
  const [traceOpen, setTraceOpen] = useState(false)
  const [traceDetailOpen, setTraceDetailOpen] = useState(false)
  const [trace, setTrace] = useState<StoryboardTraceRecord | null>(null)
  const [isTraceLoading, setIsTraceLoading] = useState(false)
  const [traceError, setTraceError] = useState<string | null>(null)
  const [copyStatus, setCopyStatus] = useState<string | null>(null)

  const handleTextBlur = () => {
    if (localText !== shot.narrative_text) {
      onUpdate(shot.id, { narrative_text: localText, isDirty: true })
    }
  }

  const handleToggleTrace = async () => {
    const nextOpen = !traceOpen
    setTraceOpen(nextOpen)
    if (!nextOpen || trace || isTraceLoading) return

    setIsTraceLoading(true)
    setTraceError(null)
    try {
      const data = await storyboardApi.getShotTrace(shot.project_id, shot.id)
      setTrace(data)
    } catch (err: any) {
      setTraceError(err?.response?.data?.detail || err?.message || 'No se pudo cargar la trazabilidad')
    } finally {
      setIsTraceLoading(false)
    }
  }

  const handleCopyPrompt = async () => {
    const prompt = trace?.prompt_trace.positive_prompt_enriched || trace?.prompt_trace.original_narrative || ''
    if (!prompt) {
      setCopyStatus('Prompt no disponible')
      return
    }
    try {
      await navigator.clipboard.writeText(prompt)
      setCopyStatus('Prompt copiado')
    } catch {
      setCopyStatus('No se pudo copiar')
    }
  }

  return (
    <div className="bg-dark-200/80 border border-white/10 rounded-xl overflow-hidden hover:border-amber-500/20 transition-colors">
      <div className="aspect-video bg-dark-300 relative group">
        {hasImage ? (
          <>
            <AuthenticatedStoryboardShotImage
              projectId={shot.project_id}
              shotId={shot.id}
              alt={shot.asset_file_name || 'Shot preview'}
              className="w-full h-full object-cover"
              fallbackLabel="Sin miniatura"
            />
            <button
              onClick={() => onOpenPicker(shot.id)}
              className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center"
            >
              <div className="flex items-center gap-2 bg-amber-500 text-black px-4 py-2 rounded-lg font-medium">
                <Image className="w-4 h-4" />
                Change Asset
              </div>
            </button>
          </>
        ) : (
          <div className="w-full h-full flex flex-col items-center justify-center text-gray-500 px-4">
            {renderStatus === 'render_pending' ? (
              <>
                <Loader2 className="w-10 h-10 mb-2 animate-spin text-amber-400/60" />
                <span className="text-sm text-amber-300/70 text-center">Render pendiente</span>
                <span className="text-[10px] text-slate-600 mt-1 text-center">Imagen pendiente de generar o asociar</span>
              </>
            ) : (
              <>
                <Image className="w-12 h-12 mb-2 opacity-40" />
                <span className="text-sm text-slate-500">Imagen pendiente de generar o asociar</span>
                <button
                  onClick={() => onOpenPicker(shot.id)}
                  className="mt-2 text-amber-400 hover:text-amber-300 text-sm"
                >
                  Select asset
                </button>
              </>
            )}
          </div>
        )}
        {shot.isDirty && (
          <div className="absolute top-2 right-2 w-2 h-2 bg-amber-500 rounded-full" title="Unsaved changes" />
        )}
        {renderStatus !== 'completed' && (
          <div className="absolute top-2 left-2">
            <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-lg text-[10px] font-medium border ${statusCfg.color} border-current/20`}>
              <StatusIcon className="w-3 h-3" />
              {statusCfg.label}
            </span>
          </div>
        )}
      </div>

      <div className="p-4 space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-xs text-gray-500">Shot {shot.sequence_order}</span>
          <div className="flex items-center gap-2">
            {shot.isDirty && (
              <span className="text-xs text-amber-400">Modified</span>
            )}
            <button
              onClick={() => onDelete(shot.id)}
              disabled={isSaving}
              className="p-1.5 text-gray-500 hover:text-red-400 hover:bg-red-400/10 rounded-lg transition-colors disabled:opacity-50"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>

        <textarea
          value={localText}
          onChange={(e) => setLocalText(e.target.value)}
          onBlur={handleTextBlur}
          placeholder="Enter narrative text..."
          disabled={isSaving}
          className="w-full bg-dark-300 border border-white/10 rounded-lg p-3 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-amber-500/50 resize-none disabled:opacity-50"
          rows={3}
        />

        {(shot.render_job_id || shot.generation_job_id) && (
          <div className="space-y-1 text-[10px] text-slate-600">
            {shot.render_job_id && (
              <p className="flex items-center gap-1">
                <Clock className="w-3 h-3" />
                Render job: <span className="text-slate-400 font-mono">{shot.render_job_id.substring(0, 12)}...</span>
              </p>
            )}
            {shot.generation_job_id && (
              <p className="flex items-center gap-1">
                <span>Gen job:</span>
                <span className="text-slate-400 font-mono">{shot.generation_job_id.substring(0, 12)}...</span>
              </p>
            )}
          </div>
        )}

        <div className="rounded-lg border border-white/10 bg-dark-300/40">
          <button
            type="button"
            onClick={handleToggleTrace}
            className="flex w-full items-center justify-between px-3 py-2 text-xs text-slate-300 hover:text-white"
          >
            <span className="inline-flex items-center gap-1.5">
              <GitBranch className="w-3.5 h-3.5 text-amber-400" />
              Trazabilidad
            </span>
            <span>{traceOpen ? 'Ocultar' : 'Ver'}</span>
          </button>

          {traceOpen && (
            <div className="space-y-3 border-t border-white/10 px-3 py-3 text-[11px] text-slate-300">
              {isTraceLoading && (
                <div className="flex items-center gap-2 text-amber-300">
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  Cargando trazabilidad...
                </div>
              )}

              {traceError && <p className="text-red-300">{traceError}</p>}

              {!isTraceLoading && !traceError && trace && (
                <>
                  <div className="space-y-1.5">
                    <p><span className="text-slate-500">Prompt:</span> {shortTraceValue(trace.prompt_trace.positive_prompt_enriched || trace.prompt_trace.original_narrative)}</p>
                    <p><span className="text-slate-500">Workflow:</span> {traceValue(trace.workflow_trace.workflow_key)} · {traceValue(trace.workflow_trace.workflow_profile_executed || trace.workflow_trace.workflow_profile)}</p>
                    <p><span className="text-slate-500">Fallback:</span> {trace.workflow_trace.fallback_applied ? traceValue(trace.workflow_trace.fallback_reason) : 'No'}</p>
                    <p><span className="text-slate-500">Modelo:</span> {traceValue(trace.model_trace.model_family)} · {traceValue(trace.model_trace.checkpoint)}</p>
                    <p><span className="text-slate-500">Parámetros:</span> seed {traceValue(trace.model_trace.seed)} · steps {traceValue(trace.model_trace.steps)} · cfg {traceValue(trace.model_trace.cfg)} · sampler {traceValue(trace.model_trace.sampler)}</p>
                    <p><span className="text-slate-500">Render job:</span> {traceValue(trace.render_job_id)}</p>
                    <p><span className="text-slate-500">Media asset:</span> {traceValue(trace.asset_trace.media_asset_id)}</p>
                    <p><span className="text-slate-500">Versión:</span> v{trace.version_trace.current_version} {trace.version_trace.has_previous_versions ? '· hay indicios de versiones anteriores' : '· sin versiones anteriores detectadas'}</p>
                  </div>

                  <div className="flex flex-wrap gap-2">
                    <button
                      type="button"
                      onClick={handleCopyPrompt}
                      className="inline-flex items-center gap-1 rounded-lg border border-white/10 px-2 py-1 text-[11px] text-slate-200 hover:bg-white/5"
                    >
                      <Copy className="w-3 h-3" />
                      Copiar prompt
                    </button>
                    <button
                      type="button"
                      onClick={() => setTraceDetailOpen((open) => !open)}
                      className="rounded-lg border border-white/10 px-2 py-1 text-[11px] text-slate-200 hover:bg-white/5"
                    >
                      {traceDetailOpen ? 'Ocultar detalle técnico' : 'Ver detalle técnico'}
                    </button>
                    {copyStatus && <span className="px-2 py-1 text-[11px] text-amber-300">{copyStatus}</span>}
                  </div>

                  {traceDetailOpen && (
                    <pre className="max-h-52 overflow-auto rounded-lg border border-white/10 bg-black/30 p-2 text-[10px] text-slate-400">
                      {JSON.stringify(trace, null, 2)}
                    </pre>
                  )}
                </>
              )}

              {!isTraceLoading && !traceError && !trace && (
                <p className="text-slate-500">No disponible</p>
              )}
            </div>
          )}
        </div>

        <div className="flex gap-2">
          <select
            value={shot.shot_type || ''}
            onChange={(e) => onUpdate(shot.id, { shot_type: e.target.value, isDirty: true })}
            disabled={isSaving}
            className="flex-1 bg-dark-300 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-amber-500/50 disabled:opacity-50"
          >
            <option value="">Shot Type</option>
            <option value="WS">Wide Shot</option>
            <option value="MS">Medium Shot</option>
            <option value="CU">Close Up</option>
            <option value="ECU">Extreme Close Up</option>
            <option value="OTS">Over the Shoulder</option>
            <option value="LS">Long Shot</option>
            <option value="POV">Point of View</option>
          </select>
          <select
            value={shot.visual_mode || ''}
            onChange={(e) => onUpdate(shot.id, { visual_mode: e.target.value, isDirty: true })}
            disabled={isSaving}
            className="flex-1 bg-dark-300 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-amber-500/50 disabled:opacity-50"
          >
            <option value="">Visual Mode</option>
            <option value="sketch">Sketch</option>
            <option value="render">Render</option>
            <option value="reference">Reference</option>
          </select>
        </div>
      </div>
    </div>
  )
}
