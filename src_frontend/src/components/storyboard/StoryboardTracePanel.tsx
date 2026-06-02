import { Component, ReactNode, useState } from 'react'
import { Copy, GitBranch, Loader2 } from 'lucide-react'
import { storyboardApi } from '@/api/storyboard'
import type { StoryboardTraceRecord } from '@/types/storyboard'
import { t, useLanguage } from '@/i18n'

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
          {t('components.storyboard.tracePanel.unavailable')}
        </div>
      )
    }
    return this.props.children
  }
}

function traceValue(value: unknown, translate: (key: string) => string): string {
  if (value === null || value === undefined || value === '') return translate('components.storyboard.common.notAvailable')
  if (typeof value === 'boolean') return value ? translate('components.storyboard.common.yes') : translate('components.storyboard.common.no')
  return String(value)
}

function shortTraceValue(value: unknown, translate: (key: string) => string, maxLength = 160): string {
  const text = traceValue(value, translate)
  return text.length > maxLength ? `${text.slice(0, maxLength)}...` : text
}

function StoryboardTracePanelInner({ projectId, shotId, compact = false }: StoryboardTracePanelProps) {
  const { t } = useLanguage()
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
      setTraceError(t('components.storyboard.tracePanel.unavailable'))
      return
    }

    setIsTraceLoading(true)
    setTraceError(null)
    try {
      const data = await storyboardApi.getShotTrace(projectId, shotId)
      setTrace(data)
    } catch (err: unknown) {
      const apiError = err as { response?: { data?: { detail?: string } }; message?: string }
      setTraceError(apiError.response?.data?.detail || apiError.message || t('components.storyboard.tracePanel.loadError'))
    } finally {
      setIsTraceLoading(false)
    }
  }

  const handleCopyPrompt = async () => {
    const prompt = trace?.prompt_trace?.positive_prompt_enriched || trace?.prompt_trace?.original_narrative || ''
    if (!prompt) {
      setCopyStatus(t('components.storyboard.tracePanel.promptUnavailable'))
      return
    }
    try {
      await navigator.clipboard.writeText(prompt)
      setCopyStatus(t('components.storyboard.tracePanel.promptCopied'))
    } catch {
      setCopyStatus(t('components.storyboard.tracePanel.copyFailed'))
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
          {t('components.storyboard.tracePanel.traceability')}
        </span>
        <span>{traceOpen ? t('components.storyboard.common.hide') : t('components.storyboard.common.view')}</span>
      </button>

      {traceOpen && (
        <div className="space-y-3 border-t border-white/10 px-3 py-3 text-[11px] text-slate-300">
          {isTraceLoading && (
            <div className="flex items-center gap-2 text-amber-300">
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
              {t('components.storyboard.tracePanel.loading')}
            </div>
          )}

          {traceError && <p className="text-red-300">{traceError}</p>}

          {!isTraceLoading && !traceError && trace && (
            <>
              <div className="space-y-1.5">
                <p><span className="text-slate-500">{t('components.storyboard.tracePanel.sceneHeading')}</span> {traceValue(trace.prompt_trace?.source_scene_heading, t)}</p>
                <p><span className="text-slate-500">{t('components.storyboard.tracePanel.action')}</span> {shortTraceValue(trace.prompt_trace?.source_action_summary, t)}</p>
                <p><span className="text-slate-500">{t('components.storyboard.tracePanel.dialogue')}</span> {shortTraceValue(trace.prompt_trace?.source_dialogue_summary, t)}</p>
                <p><span className="text-slate-500">{t('components.storyboard.tracePanel.prompt')}</span> {shortTraceValue(trace.prompt_trace?.positive_prompt_enriched || trace.prompt_trace?.original_narrative, t)}</p>
                <p><span className="text-slate-500">{t('components.storyboard.tracePanel.workflow')}</span> {traceValue(trace.workflow_trace?.workflow_key, t)} · {traceValue(trace.workflow_trace?.workflow_profile_executed || trace.workflow_trace?.workflow_profile, t)}</p>
                <p><span className="text-slate-500">{t('components.storyboard.tracePanel.fallback')}</span> {trace.workflow_trace?.fallback_applied ? traceValue(trace.workflow_trace?.fallback_reason, t) : t('components.storyboard.common.no')}</p>
                <p><span className="text-slate-500">{t('components.storyboard.tracePanel.model')}:</span> {traceValue(trace.model_trace?.model_family, t)} · {traceValue(trace.model_trace?.checkpoint, t)}</p>
                <p><span className="text-slate-500">{t('components.storyboard.tracePanel.parameters')}:</span> seed {traceValue(trace.model_trace?.seed, t)} · steps {traceValue(trace.model_trace?.steps, t)} · cfg {traceValue(trace.model_trace?.cfg, t)} · sampler {traceValue(trace.model_trace?.sampler, t)} · scheduler {traceValue(trace.model_trace?.scheduler, t)} · {traceValue(trace.model_trace?.width, t)}x{traceValue(trace.model_trace?.height, t)}</p>
                <p><span className="text-slate-500">{t('components.storyboard.tracePanel.renderJob')}</span> {traceValue(trace.render_job_id, t)}</p>
                <p><span className="text-slate-500">{t('components.storyboard.tracePanel.mediaAsset')}</span> {traceValue(trace.asset_trace?.media_asset_id, t)}</p>
                <p><span className="text-slate-500">{t('components.storyboard.tracePanel.version')}:</span> v{traceValue(trace.version_trace?.current_version, t)} {trace.version_trace?.has_previous_versions ? `· ${t('components.storyboard.tracePanel.previousVersions')}` : `· ${t('components.storyboard.tracePanel.noPreviousVersions')}`}</p>
              </div>

              <div className="flex flex-wrap gap-2">
                <button
                  type="button"
                  onClick={handleCopyPrompt}
                  className="inline-flex items-center gap-1 rounded-lg border border-white/10 px-2 py-1 text-[11px] text-slate-200 hover:bg-white/5"
                >
                  <Copy className="w-3 h-3" />
                  {t('components.storyboard.tracePanel.copyPrompt')}
                </button>
                <button
                  type="button"
                  onClick={() => setTraceDetailOpen((open) => !open)}
                  className="rounded-lg border border-white/10 px-2 py-1 text-[11px] text-slate-200 hover:bg-white/5"
                >
                  {traceDetailOpen ? t('components.storyboard.tracePanel.hideTechnicalDetail') : t('components.storyboard.tracePanel.viewTechnicalDetail')}
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
            <p className="text-slate-500">{t('components.storyboard.common.notAvailable')}</p>
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
