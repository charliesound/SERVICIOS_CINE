import { useState } from 'react'
import { Trash2, Image, Clock, AlertTriangle, CheckCircle2, Loader2 } from 'lucide-react'
import { AuthenticatedStoryboardShotImage } from '@/components/storyboard/AuthenticatedStoryboardShotImage'
import { StoryboardTracePanel } from '@/components/storyboard/StoryboardTracePanel'
import type { DirtyShot } from '@/types/storyboard'
import { resolveShotRenderState } from '@/types/storyboard'
import { getStoryboardShotDisplayText, getStoryboardUiLocale } from '@/utils/storyboardText'

interface ShotCardProps {
  shot: DirtyShot
  onUpdate: (shotId: string, updates: Partial<DirtyShot>) => void
  onDelete: (shotId: string) => void
  onOpenPicker: (shotId: string) => void
  isSaving: boolean
}


export function ShotCard({ shot, onUpdate, onDelete, onOpenPicker, isSaving }: ShotCardProps) {
  const [localText, setLocalText] = useState(shot.narrative_text || getStoryboardShotDisplayText(shot, getStoryboardUiLocale()))
  const renderState = resolveShotRenderState(shot)
  const isRenderPending = renderState.state === 'rendering'
  const hasImage = shot.has_image === true && !isRenderPending

  const handleTextBlur = () => {
    if (localText !== shot.narrative_text) {
      onUpdate(shot.id, { narrative_text: localText, isDirty: true })
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
            {isRenderPending ? (
              <>
                <Loader2 className="w-10 h-10 mb-2 animate-spin text-amber-400/60" />
                <span className="text-sm text-amber-300/70 text-center">Render pendiente</span>
                <span className="text-[10px] text-slate-600 mt-1 text-center">Imagen pendiente de generar o asociar</span>
              </>
            ) : renderState.state === 'failed' ? (
              <>
                <AlertTriangle className="w-10 h-10 mb-2 text-red-400/70" />
                <span className="text-sm text-red-300/80 text-center">Render fallido</span>
                <span className="text-[10px] text-slate-500 mt-1 text-center">Revisa el error o asigna un asset manualmente</span>
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
        <div className={`absolute top-2 left-2 ${renderState.pulse ? 'animate-pulse' : ''}`} title={shot.render_error || renderState.label}>
          <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-lg text-[10px] font-medium border ${renderState.color} border-current/20`}>
            {renderState.icon === 'check' && <CheckCircle2 className="w-3 h-3" />}
            {renderState.icon === 'clock' && <Clock className="w-3 h-3" />}
            {renderState.icon === 'alert' && <AlertTriangle className="w-3 h-3" />}
            {renderState.icon === 'image' && <Image className="w-3 h-3" />}
            {renderState.label}
          </span>
        </div>
      </div>

      <div className="p-4 space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-xs text-gray-500">Shot {shot.sequence_order}</span>
          <div className="flex items-center gap-2">
            <span className="text-[10px] text-cyan-300">v{shot.version}</span>
            {shot.generation_job_id && <span className="text-[10px] text-slate-500 font-mono">{shot.generation_job_id.slice(0, 8)}</span>}
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
            <p className="flex items-center gap-1">
              <span>Última generación:</span>
              <span className="text-slate-400">{new Date(shot.updated_at).toLocaleString()}</span>
            </p>
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

        {shot.render_error && (
          <div className="rounded-lg border border-red-500/20 bg-red-500/10 px-3 py-2 text-[11px] text-red-300">
            {shot.render_error}
          </div>
        )}

        <StoryboardTracePanel projectId={shot.project_id} shotId={shot.id} />

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
