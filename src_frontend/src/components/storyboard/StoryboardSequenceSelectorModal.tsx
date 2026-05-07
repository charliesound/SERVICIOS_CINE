import { useMemo, useState } from 'react'
import { AlertCircle, Check, Layers, Search, X } from 'lucide-react'
import type { StoryboardSceneCandidate, StoryboardSequence, StoryboardSelectionMode } from '@/types/storyboard'

export interface StoryboardSelectionValue {
  mode: StoryboardSelectionMode
  sequenceId?: string | null
  sequenceIds?: string[]
  sceneNumbers?: number[]
  sceneStart?: number | null
  sceneEnd?: number | null
  overwrite: boolean
  regenerateExisting: boolean
}

interface StoryboardSequenceSelectorModalProps {
  open: boolean
  isLoading: boolean
  error?: string | null
  scenes: StoryboardSceneCandidate[]
  sequences: StoryboardSequence[]
  onClose: () => void
  onConfirm: (selection: StoryboardSelectionValue) => void
}

const MODE_LABELS: Array<{ value: StoryboardSelectionMode; title: string; description: string }> = [
  { value: 'FULL_SCRIPT', title: 'Storyboard completo', description: 'Genera todo el guion detectado.' },
  { value: 'SEQUENCE', title: 'Solo una secuencia', description: 'Elige una secuencia concreta.' },
  { value: 'SELECTED_SCENES', title: 'Varias escenas / secuencias', description: 'Selecciona escenas sueltas o por secuencia.' },
  { value: 'SCENE_RANGE', title: 'Rango de escenas', description: 'Genera desde una escena inicial a otra final.' },
]

export function StoryboardSequenceSelectorModal({
  open,
  isLoading,
  error,
  scenes,
  sequences,
  onClose,
  onConfirm,
}: StoryboardSequenceSelectorModalProps) {
  const [mode, setMode] = useState<StoryboardSelectionMode>('SELECTED_SCENES')
  const [search, setSearch] = useState('')
  const [selectedSceneNumbers, setSelectedSceneNumbers] = useState<number[]>([])
  const [selectedSequenceId, setSelectedSequenceId] = useState<string>('')
  const [selectedSequenceIds, setSelectedSequenceIds] = useState<string[]>([])
  const [rangeStart, setRangeStart] = useState<string>('1')
  const [rangeEnd, setRangeEnd] = useState<string>('3')
  const [regenerateExisting, setRegenerateExisting] = useState(false)
  const [overwrite, setOverwrite] = useState(true)

  const filteredScenes = useMemo(() => {
    const q = search.trim().toLowerCase()
    if (!q) return scenes
    return scenes.filter((scene) =>
      `${scene.scene_number} ${scene.scene_heading} ${scene.narrative_text || ''}`.toLowerCase().includes(q)
    )
  }, [scenes, search])

  const selectedCount = selectedSceneNumbers.length

  if (!open) return null

  const toggleScene = (sceneNumber: number) => {
    setSelectedSceneNumbers((prev) => prev.includes(sceneNumber) ? prev.filter((n) => n !== sceneNumber) : [...prev, sceneNumber].sort((a, b) => a - b))
  }

  const toggleSequenceScenes = (sequenceId: string, includedScenes: number[]) => {
    setSelectedSequenceIds((prev) => prev.includes(sequenceId) ? prev.filter((id) => id !== sequenceId) : [...prev, sequenceId])
    setSelectedSceneNumbers((prev) => {
      const next = new Set(prev)
      const allIncluded = includedScenes.every((scene) => next.has(scene))
      if (allIncluded) {
        includedScenes.forEach((scene) => next.delete(scene))
      } else {
        includedScenes.forEach((scene) => next.add(scene))
      }
      return Array.from(next).sort((a, b) => a - b)
    })
  }

  const buildSelection = (): StoryboardSelectionValue => {
    if (mode === 'FULL_SCRIPT') {
      return { mode, overwrite, regenerateExisting }
    }
    if (mode === 'SEQUENCE') {
      return { mode, sequenceId: selectedSequenceId || null, overwrite, regenerateExisting }
    }
    if (mode === 'SCENE_RANGE') {
      return {
        mode,
        sceneStart: Number(rangeStart || '1'),
        sceneEnd: Number(rangeEnd || rangeStart || '1'),
        overwrite,
        regenerateExisting,
      }
    }
    return {
      mode,
      sceneNumbers: selectedSceneNumbers,
      sequenceIds: selectedSequenceIds,
      overwrite,
      regenerateExisting,
    }
  }

  const canConfirm = (() => {
    if (isLoading) return false
    if (mode === 'FULL_SCRIPT') return scenes.length > 0
    if (mode === 'SEQUENCE') return !!selectedSequenceId
    if (mode === 'SCENE_RANGE') return Number(rangeStart) > 0 && Number(rangeEnd) >= Number(rangeStart)
    return selectedSceneNumbers.length > 0
  })()

  return (
    <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="w-full max-w-5xl rounded-3xl border border-white/10 bg-[#0f1013] shadow-2xl overflow-hidden">
        <div className="flex items-start justify-between gap-4 border-b border-white/10 px-6 py-5">
          <div>
            <h3 className="text-lg font-semibold text-white">Seleccionar secuencias para storyboard</h3>
            <p className="text-sm text-gray-400 mt-1">{scenes.length} escenas detectadas. Generar muchas escenas puede tardar varios minutos.</p>
          </div>
          <button type="button" onClick={onClose} className="rounded-xl p-2 text-gray-400 hover:bg-white/5 hover:text-white transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-[280px_1fr] gap-0 min-h-[560px]">
          <div className="border-r border-white/10 p-5 space-y-4 bg-white/[0.02]">
            {MODE_LABELS.map((item) => (
              <button
                key={item.value}
                type="button"
                onClick={() => setMode(item.value)}
                className={`w-full text-left rounded-2xl border px-4 py-3 transition-colors ${mode === item.value ? 'border-amber-400/40 bg-amber-500/10' : 'border-white/10 hover:border-white/20 bg-transparent'}`}
              >
                <div className="font-medium text-white">{item.title}</div>
                <div className="text-xs text-gray-400 mt-1 leading-relaxed">{item.description}</div>
              </button>
            ))}

            <div className="rounded-2xl border border-white/10 p-4 space-y-3">
              <div className="text-sm text-gray-300 font-medium">Resumen</div>
              <div className="text-xs text-gray-400">{selectedCount} de {scenes.length} escenas seleccionadas</div>
              <label className="flex items-center gap-2 text-xs text-gray-300">
                <input type="checkbox" checked={regenerateExisting} onChange={(e) => setRegenerateExisting(e.target.checked)} />
                Regenerar escenas ya existentes
              </label>
              <label className="flex items-center gap-2 text-xs text-gray-300">
                <input type="checkbox" checked={overwrite} onChange={(e) => setOverwrite(e.target.checked)} />
                Sobrescribir storyboard previo
              </label>
            </div>
          </div>

          <div className="p-5 space-y-4">
            {error && (
              <div className="rounded-2xl border border-red-500/20 bg-red-500/10 p-3 text-sm text-red-300 flex items-center gap-2">
                <AlertCircle className="w-4 h-4" />
                {error}
              </div>
            )}

            {mode === 'SEQUENCE' && (
              <div className="space-y-3">
                {sequences.map((sequence) => (
                  <button
                    key={sequence.sequence_id}
                    type="button"
                    onClick={() => setSelectedSequenceId(sequence.sequence_id)}
                    className={`w-full rounded-2xl border p-4 text-left transition-colors ${selectedSequenceId === sequence.sequence_id ? 'border-amber-400/40 bg-amber-500/10' : 'border-white/10 hover:border-white/20'}`}
                  >
                    <div className="flex items-center justify-between gap-3">
                      <div>
                        <div className="text-sm font-medium text-white">Secuencia {sequence.sequence_number}: {sequence.title}</div>
                        <div className="text-xs text-gray-400 mt-1">Escenas {sequence.included_scenes.join(', ') || 'sin datos'} · {sequence.storyboard_status}</div>
                      </div>
                      {selectedSequenceId === sequence.sequence_id && <Check className="w-4 h-4 text-amber-300" />}
                    </div>
                  </button>
                ))}
              </div>
            )}

            {mode === 'SCENE_RANGE' && (
              <div className="grid grid-cols-2 gap-3 max-w-md">
                <label className="space-y-2 text-sm text-gray-300">
                  <span>Escena inicial</span>
                  <input className="input w-full" value={rangeStart} onChange={(e) => setRangeStart(e.target.value)} />
                </label>
                <label className="space-y-2 text-sm text-gray-300">
                  <span>Escena final</span>
                  <input className="input w-full" value={rangeEnd} onChange={(e) => setRangeEnd(e.target.value)} />
                </label>
              </div>
            )}

            {(mode === 'SELECTED_SCENES' || mode === 'FULL_SCRIPT') && (
              <>
                <div className="flex flex-wrap items-center gap-2">
                  <div className="relative flex-1 min-w-[240px]">
                    <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
                    <input
                      value={search}
                      onChange={(e) => setSearch(e.target.value)}
                      placeholder="Buscar escena o texto..."
                      className="input w-full pl-9"
                    />
                  </div>
                  <button type="button" onClick={() => setSelectedSceneNumbers(scenes.map((scene) => scene.scene_number))} className="px-3 py-2 text-sm rounded-xl border border-white/10 hover:bg-white/5">Seleccionar todo</button>
                  <button type="button" onClick={() => setSelectedSceneNumbers([])} className="px-3 py-2 text-sm rounded-xl border border-white/10 hover:bg-white/5">Limpiar selección</button>
                  <button type="button" onClick={() => setSelectedSceneNumbers(scenes.slice(0, 3).map((scene) => scene.scene_number))} className="px-3 py-2 text-sm rounded-xl border border-white/10 hover:bg-white/5">Primeras 3 escenas</button>
                  <button type="button" onClick={() => setSelectedSceneNumbers(scenes.slice(0, 5).map((scene) => scene.scene_number))} className="px-3 py-2 text-sm rounded-xl border border-white/10 hover:bg-white/5">Primeras 5 escenas</button>
                </div>

                {sequences.length > 0 && mode === 'SELECTED_SCENES' && (
                  <div className="rounded-2xl border border-white/10 p-3">
                    <div className="flex items-center gap-2 text-sm text-gray-300 mb-3">
                      <Layers className="w-4 h-4" />
                      Selección rápida por secuencia
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {sequences.map((sequence) => (
                        <button
                          key={sequence.sequence_id}
                          type="button"
                          onClick={() => toggleSequenceScenes(sequence.sequence_id, sequence.included_scenes)}
                          className={`px-3 py-2 rounded-xl text-xs border transition-colors ${selectedSequenceIds.includes(sequence.sequence_id) ? 'border-amber-400/40 bg-amber-500/10 text-amber-200' : 'border-white/10 text-gray-300 hover:bg-white/5'}`}
                        >
                          S{sequence.sequence_number} · {sequence.title}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                <div className="max-h-[360px] overflow-auto rounded-2xl border border-white/10 divide-y divide-white/5">
                  {filteredScenes.map((scene) => {
                    const checked = selectedSceneNumbers.includes(scene.scene_number)
                    return (
                      <label key={scene.scene_number} className="flex items-start gap-3 px-4 py-3 cursor-pointer hover:bg-white/[0.03]">
                        <input
                          type="checkbox"
                          checked={checked}
                          onChange={() => toggleScene(scene.scene_number)}
                          className="mt-1"
                        />
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 flex-wrap">
                            <span className="text-xs font-semibold text-amber-300">ESC {String(scene.scene_number).padStart(2, '0')}</span>
                            <span className="text-sm font-medium text-white truncate">{scene.scene_heading}</span>
                            {scene.storyboard_status && (
                              <span className={`text-[10px] px-2 py-0.5 rounded-full ${scene.storyboard_status === 'generated' ? 'bg-emerald-500/10 text-emerald-300' : scene.storyboard_status === 'without_image' ? 'bg-amber-500/10 text-amber-300' : 'bg-white/10 text-gray-300'}`}>
                                {scene.storyboard_status === 'generated' ? 'Ya generado' : scene.storyboard_status === 'without_image' ? 'Sin imagen' : 'Pendiente'}
                              </span>
                            )}
                          </div>
                          {scene.narrative_text && (
                            <p className="text-xs text-gray-400 mt-1 line-clamp-2">{scene.narrative_text}</p>
                          )}
                        </div>
                      </label>
                    )
                  })}
                </div>
              </>
            )}
          </div>
        </div>

        <div className="border-t border-white/10 px-6 py-4 flex items-center justify-between gap-3">
          <div className="text-xs text-gray-500">{selectedCount} de {scenes.length} escenas seleccionadas</div>
          <div className="flex items-center gap-2">
            <button type="button" onClick={onClose} className="px-4 py-2 text-sm rounded-xl border border-white/10 hover:bg-white/5">Cancelar</button>
            {mode !== 'FULL_SCRIPT' && (
              <button type="button" disabled={!canConfirm} onClick={() => onConfirm(buildSelection())} className="px-4 py-2 text-sm rounded-xl border border-amber-500/20 bg-amber-500 text-black font-medium disabled:opacity-40">
                Generar seleccionadas
              </button>
            )}
            <button type="button" onClick={() => onConfirm({ mode: 'FULL_SCRIPT', overwrite, regenerateExisting })} className="px-4 py-2 text-sm rounded-xl border border-white/10 hover:bg-white/5 text-white">
              Generar storyboard completo
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
