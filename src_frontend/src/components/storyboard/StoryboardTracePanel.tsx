import { Component, ReactNode, useState } from 'react'
import { Copy, GitBranch, Loader2 } from 'lucide-react'
import { storyboardApi } from '@/api/storyboard'
import type { StoryboardTraceRecord } from '@/types/storyboard'

interface StoryboardTracePanelProps {
  projectId?: string | null
  shotId?: string | null
  compact?: boolean
}

interface TraceBoundaryProps {
  children: ReactNode
}

interface TraceBoundaryState {
  hasError: boolean
}

class StoryboardTraceErrorBoundary extends Component<TraceBoundaryProps, TraceBoundaryState> {
  state: TraceBoundaryState = { hasError: false }

  static getDerivedStateFromError(): TraceBoundaryState {
    return { hasError: true }
  }

  componentDidCatch(error: unknown) {
    if (import.meta.env.DEV) {
      console.warn('[StoryboardTracePanel] render failed:', error)
    }
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="rounded-lg border border-white/10 bg-dark-300/40 px-3 py-2 text-[11px] text-slate-500">
          Trazabilidad no disponible
        </div>
      )
    }
    return this.props.children
  }
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

function StoryboardTracePanelInner({ projectId, shotId, compact = false }: StoryboardTracePanelProps) {
  const [traceOpen, setTraceOpen] = useState(false)
  const [traceDetailOpen, setTraceDetailOpen] = useState(false)
  const [trace, setTrace] = useState<StoryboardTraceRecord | null>(null)
  const [isTraceLoading, setIsTraceLoading] = useState(false)
  const [traceError, setTraceError] = useState<string | null>(null)
  const [copyStatus, setCopyStatus] = useState<string | null>(null)

  const handleToggleTrace = async () => {
    const nextOpen = !traceOpen
    setTraceOpen(nextOpen)
    if (!nextOpen || trace || isTraceLoading) return
    if (!projectId || !shotId) {
      setTraceError('Trazabilidad no disponible')
      return
    }

    setIsTraceLoading(true)
    setTraceError(null)
    try {
      const data = await storyboardApi.getShotTrace(projectId, shotId)
      setTrace(data)
    } catch (err: unknown) {
      const apiError = err as { response?: { data?: { detail?: string } }; message?: string }
      setTraceError(apiError.response?.data?.detail || apiError.message || 'No se pudo cargar la trazabilidad')
    } finally {
      setIsTraceLoading(false)
    }
  }

  const handleCopyPrompt = async () => {
    const prompt = trace?.prompt_trace?.positive_prompt_enriched || trace?.prompt_trace?.original_narrative || ''
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
    <div className={`rounded-lg border border-white/10 bg-dark-300/40 ${compact ? 'mt-2' : ''}`}>
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
                <p><span className="text-slate-500">Prompt:</span> {shortTraceValue(trace.prompt_trace?.positive_prompt_enriched || trace.prompt_trace?.original_narrative)}</p>
                <p><span className="text-slate-500">Workflow:</span> {traceValue(trace.workflow_trace?.workflow_key)} · {traceValue(trace.workflow_trace?.workflow_profile_executed || trace.workflow_trace?.workflow_profile)}</p>
                <p><span className="text-slate-500">Fallback:</span> {trace.workflow_trace?.fallback_applied ? traceValue(trace.workflow_trace?.fallback_reason) : 'No'}</p>
                <p><span className="text-slate-500">Modelo:</span> {traceValue(trace.model_trace?.model_family)} · {traceValue(trace.model_trace?.checkpoint)}</p>
                <p><span className="text-slate-500">Parámetros:</span> seed {traceValue(trace.model_trace?.seed)} · steps {traceValue(trace.model_trace?.steps)} · cfg {traceValue(trace.model_trace?.cfg)} · sampler {traceValue(trace.model_trace?.sampler)}</p>
                <p><span className="text-slate-500">Render job:</span> {traceValue(trace.render_job_id)}</p>
                <p><span className="text-slate-500">Media asset:</span> {traceValue(trace.asset_trace?.media_asset_id)}</p>
                <p><span className="text-slate-500">Versión:</span> v{traceValue(trace.version_trace?.current_version)} {trace.version_trace?.has_previous_versions ? '· hay indicios de versiones anteriores' : '· sin versiones anteriores detectadas'}</p>
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
  )
}

export function StoryboardTracePanel(props: StoryboardTracePanelProps) {
  return (
    <StoryboardTraceErrorBoundary>
      <StoryboardTracePanelInner {...props} />
    </StoryboardTraceErrorBoundary>
  )
}
