import { useState } from 'react'
import { Trash2, Image } from 'lucide-react'
import type { DirtyShot } from '@/types/storyboard'

interface ShotCardProps {
  shot: DirtyShot
  onUpdate: (shotId: string, updates: Partial<DirtyShot>) => void
  onDelete: (shotId: string) => void
  onOpenPicker: (shotId: string) => void
  isSaving: boolean
}

export function ShotCard({ shot, onUpdate, onDelete, onOpenPicker, isSaving }: ShotCardProps) {
  const [localText, setLocalText] = useState(shot.narrative_text || '')

  const handleTextBlur = () => {
    if (localText !== shot.narrative_text) {
      onUpdate(shot.id, { narrative_text: localText, isDirty: true })
    }
  }

  return (
    <div className="bg-dark-200/80 border border-white/10 rounded-xl overflow-hidden hover:border-amber-500/20 transition-colors">
      <div className="aspect-video bg-dark-300 relative group">
        {shot.thumbnail_url ? (
          <>
            <img
              src={shot.thumbnail_url}
              alt={shot.asset_file_name || 'Shot preview'}
              className="w-full h-full object-cover"
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
          <div className="w-full h-full flex flex-col items-center justify-center text-gray-500">
            <Image className="w-12 h-12 mb-2" />
            <span className="text-sm">No asset assigned</span>
            <button
              onClick={() => onOpenPicker(shot.id)}
              className="mt-2 text-amber-400 hover:text-amber-300 text-sm"
            >
              Select asset
            </button>
          </div>
        )}
        {shot.isDirty && (
          <div className="absolute top-2 right-2 w-2 h-2 bg-amber-500 rounded-full" title="Unsaved changes" />
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
