import { useEffect, useMemo, useState } from 'react'
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
  render: boolean
}

interface StoryboardSequenceSelectorModalProps {
  open: boolean
  isLoading: boolean
  error?: string | null
  scenes?: StoryboardSceneCandidate[]
  sequences?: StoryboardSequence[]
  renderImagesOnComplete?: boolean
  onRenderImagesChange?: (value: boolean) => void
  onClose: () => void
  onConfirm: (selection: StoryboardSelectionValue) => void
}

interface SequencePresentationItem {
  sequence: StoryboardSequence
  displayName: string
  sceneCount: number
  location: string | null
  characters: string[]
  intExt: string | null
  timeOfDay: string | null
  searchableText: string
}

const MODE_LABELS: Array<{ value: StoryboardSelectionMode; title: string; description: string }> = [
  { value: 'SELECTED_SCENES', title: 'Varias secuencias', description: 'Selecciona varias secuencias visibles y genera solo ese bloque.' },
  { value: 'SEQUENCE', title: 'Solo una secuencia', description: 'Elige una secuencia concreta.' },
  { value: 'SINGLE_SCENE', title: 'Una sola escena', description: 'Genera una escena concreta.' },
  { value: 'SCENE_RANGE', title: 'Rango de escenas', description: 'Genera desde una escena inicial a otra final.' },
  { value: 'FULL_SCRIPT', title: 'Storyboard completo', description: 'Genera todo el guion detectado.' },
]

function normalizeText(value: string): string {
  return value
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
}

function extractHeadingMeta(sceneHeading?: string | null): { intExt: string | null; timeOfDay: string | null } {
  const heading = (sceneHeading || '').trim()
  if (!heading) return { intExt: null, timeOfDay: null }

  const intExtMatch = heading.match(/\b(INT\/EXT|EXT\/INT|INT|EXT)\.?\b/i)
  const timeMatch = heading.match(/\b(DIA|DÍA|DAY|NOCHE|NIGHT|TARDE|AFTERNOON|MORNING|MANANA|MAÑANA|EVENING)\b/i)

  return {
    intExt: intExtMatch ? intExtMatch[1].toUpperCase().replace('.', '') : null,
    timeOfDay: timeMatch ? timeMatch[1].toUpperCase() : null,
  }
}

function buildSequencePresentationItems(
  sequences: StoryboardSequence[],
  scenes: StoryboardSceneCandidate[]
): SequencePresentationItem[] {
  return sequences.map((sequence) => {
    const relatedScenes = scenes.filter((scene) => scene.sequence_id === sequence.sequence_id)
    const firstScene = relatedScenes[0]
    const headingMeta = extractHeadingMeta(firstScene?.scene_heading)
    const displayName = sequence.title || `Secuencia ${sequence.sequence_number}`
    const location = sequence.location || firstScene?.scene_heading || null
    const characters = sequence.characters || []
    const includedScenes = sequence.included_scenes || []
    const sceneCount = includedScenes.length || relatedScenes.length
    const searchableText = normalizeText([
      sequence.sequence_number,
      displayName,
      sequence.summary,
      location,
      characters.join(' '),
      headingMeta.intExt,
      headingMeta.timeOfDay,
    ].filter(Boolean).join(' '))

    return {
      sequence,
      displayName,
      sceneCount,
      location,
      characters,
      intExt: headingMeta.intExt,
      timeOfDay: headingMeta.timeOfDay,
      searchableText,
    }
  })
}

export function StoryboardSequenceSelectorModal({
  open,
  isLoading,
  error,
  scenes = [],
  sequences = [],
  renderImagesOnComplete = false,
  onRenderImagesChange,
  onClose,
  onConfirm,
}: StoryboardSequenceSelectorModalProps) {
  const [mode, setMode] = useState<StoryboardSelectionMode>('SELECTED_SCENES')
  const [search, setSearch] = useState('')
  const [selectedSequenceId, setSelectedSequenceId] = useState<string>('')
  const [selectedSequenceIds, setSelectedSequenceIds] = useState<string[]>([])
  const [selectedSingleSceneNumber, setSelectedSingleSceneNumber] = useState<number | null>(null)
  const [rangeStart, setRangeStart] = useState<string>('1')
  const [rangeEnd, setRangeEnd] = useState<string>('3')
  const [regenerateExisting, setRegenerateExisting] = useState(false)
  const [overwrite, setOverwrite] = useState(true)

  useEffect(() => {
    if (!open) return
    setSearch('')
    setSelectedSequenceIds([])
    setSelectedSequenceId('')
    setSelectedSingleSceneNumber(null)
    setRangeStart('1')
    setRangeEnd('3')
    setMode('SELECTED_SCENES')
    setRegenerateExisting(false)
    setOverwrite(true)
  }, [open])

  const sequenceItems = useMemo(
    () => buildSequencePresentationItems(sequences, scenes),
    [scenes, sequences]
  )

  const filteredSequenceItems = useMemo(() => {
    const query = normalizeText(search.trim())
    if (!query) return sequenceItems
    return sequenceItems.filter((item) => item.searchableText.includes(query))
  }, [search, sequenceItems])

  const filteredScenes = useMemo(() => {
    const query = normalizeText(search.trim())
    if (!query) return scenes
    return scenes.filter((scene) => normalizeText([
      scene.scene_number,
      scene.scene_heading,
      scene.sequence_title,
      scene.narrative_text || '',
    ].join(' ')).includes(query))
  }, [scenes, search])

  const selectedSceneNumbersForMulti = useMemo(() => {
    const next = new Set<number>()
    selectedSequenceIds.forEach((sequenceId) => {
      const match = sequences.find((sequence) => sequence.sequence_id === sequenceId)
      ;(match?.included_scenes || []).forEach((sceneNumber) => next.add(sceneNumber))
    })
    return Array.from(next).sort((a, b) => a - b)
  }, [selectedSequenceIds, sequences])

  const visibleSequenceIds = filteredSequenceItems.map((item) => item.sequence.sequence_id)
  const selectedSequenceCount = (selectedSequenceIds ?? []).length

  if (!open) return null

  const toggleSequence = (sequenceId: string) => {
    setSelectedSequenceIds((prev) => prev.includes(sequenceId)
      ? prev.filter((id) => id !== sequenceId)
      : [...prev, sequenceId]
    )
  }

  const handleSelectAll = () => {
    setSelectedSequenceIds(sequences.map((sequence) => sequence.sequence_id))
  }

  const handleSelectVisible = () => {
    setSelectedSequenceIds(Array.from(new Set([...selectedSequenceIds, ...visibleSequenceIds])))
  }

  const handleClearSelection = () => {
    setSelectedSequenceIds([])
  }

  const buildSelection = (): StoryboardSelectionValue => {
    if (mode === 'FULL_SCRIPT') {
      return { mode, overwrite, regenerateExisting, render: renderImagesOnComplete }
    }
    if (mode === 'SEQUENCE') {
      return { mode, sequenceId: selectedSequenceId || null, overwrite, regenerateExisting, render: renderImagesOnComplete }
    }
    if (mode === 'SINGLE_SCENE') {
      return {
        mode,
        sceneNumbers: selectedSingleSceneNumber != null ? [selectedSingleSceneNumber] : [],
        overwrite,
        regenerateExisting,
        render: renderImagesOnComplete,
      }
    }
    if (mode === 'SCENE_RANGE') {
      return {
        mode,
        sceneStart: Number(rangeStart || '1'),
        sceneEnd: Number(rangeEnd || rangeStart || '1'),
        overwrite,
        regenerateExisting,
        render: renderImagesOnComplete,
      }
    }
    return {
      mode,
      sequenceIds: selectedSequenceIds,
      sceneNumbers: selectedSceneNumbersForMulti,
      overwrite,
      regenerateExisting,
      render: renderImagesOnComplete,
    }
  }

  const canConfirm = (() => {
    if (isLoading) return false
    if (mode === 'FULL_SCRIPT') return (scenes ?? []).length > 0
    if (mode === 'SEQUENCE') return !!selectedSequenceId
    if (mode === 'SINGLE_SCENE') return selectedSingleSceneNumber != null
    if (mode === 'SCENE_RANGE') return Number(rangeStart) > 0 && Number(rangeEnd) >= Number(rangeStart)
    return (selectedSequenceIds ?? []).length > 0
  })()

  const primaryButtonLabel = (() => {
    if (mode === 'FULL_SCRIPT') return 'Generar storyboard completo'
    if (mode === 'SEQUENCE') return 'Generar storyboard de la secuencia'
    if (mode === 'SINGLE_SCENE') return 'Generar storyboard de la escena'
    if (mode === 'SCENE_RANGE') return 'Generar storyboard del rango'
    return `Generar storyboard de secuencias seleccionadas${selectedSequenceCount > 0 ? ` (${selectedSequenceCount})` : ''}`
  })()

  const helperStatus = (() => {
    if (mode === 'SELECTED_SCENES') return `${selectedSequenceCount} secuencias seleccionadas · ${(selectedSceneNumbersForMulti ?? []).length} escenas cubiertas`
    if (mode === 'SEQUENCE') return selectedSequenceId ? '1 secuencia seleccionada' : 'Selecciona una secuencia'
    if (mode === 'SINGLE_SCENE') return selectedSingleSceneNumber != null ? `Escena ${selectedSingleSceneNumber} seleccionada` : 'Selecciona una escena'
    if (mode === 'SCENE_RANGE') return `Rango ${rangeStart || '1'}-${rangeEnd || rangeStart || '1'}`
    return `${(scenes ?? []).length} escenas detectadas`
  })()

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 backdrop-blur-sm">
      <div className="flex h-[88vh] w-full max-w-6xl flex-col overflow-hidden rounded-3xl border border-white/10 bg-[#0f1013] shadow-2xl">
        <div className="flex items-start justify-between gap-4 border-b border-white/10 px-6 py-5">
          <div>
            <h3 className="text-lg font-semibold text-white">Seleccionar secuencias para storyboard</h3>
            <p className="mt-1 text-sm text-gray-400">Controla exactamente qué secuencias quieres generar sin disparar el storyboard completo por error.</p>
          </div>
          <button type="button" onClick={onClose} className="rounded-xl p-2 text-gray-400 transition-colors hover:bg-white/5 hover:text-white">
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="grid min-h-0 flex-1 grid-cols-1 lg:grid-cols-[300px_minmax(0,1fr)]">
          <aside className="border-b border-white/10 bg-white/[0.02] p-5 lg:border-b-0 lg:border-r lg:border-white/10">
            <div className="space-y-4">
              {MODE_LABELS.map((item) => (
                <button
                  key={item.value}
                  type="button"
                  onClick={() => setMode(item.value)}
                  className={`w-full rounded-2xl border px-4 py-3 text-left transition-colors ${mode === item.value ? 'border-amber-400/40 bg-amber-500/10' : 'border-white/10 bg-transparent hover:border-white/20'}`}
                >
                  <div className="font-medium text-white">{item.title}</div>
                  <div className="mt-1 text-xs leading-relaxed text-gray-400">{item.description}</div>
                </button>
              ))}

              <div className="rounded-2xl border border-white/10 p-4 space-y-3">
                <div className="text-sm font-medium text-gray-300">Resumen</div>
                <div className="text-xs text-gray-400">{helperStatus}</div>
                <label className="flex items-center gap-2 text-xs text-gray-300">
                  <input type="checkbox" checked={regenerateExisting} onChange={(event) => setRegenerateExisting(event.target.checked)} />
                  Regenerar escenas ya existentes
                </label>
                <label className="flex items-center gap-2 text-xs text-gray-300">
                  <input type="checkbox" checked={overwrite} onChange={(event) => setOverwrite(event.target.checked)} />
                  Sobrescribir storyboard previo
                </label>
                <label className="flex items-center gap-2 text-xs text-gray-300">
                  <input type="checkbox" checked={renderImagesOnComplete} onChange={(event) => onRenderImagesChange?.(event.target.checked)} />
                  Renderizar imágenes al terminar
                </label>
              </div>
            </div>
          </aside>

          <section className="flex min-h-0 flex-col">
            <div className="border-b border-white/10 p-5">
              {error && (
                <div className="mb-4 flex items-center gap-2 rounded-2xl border border-red-500/20 bg-red-500/10 p-3 text-sm text-red-300">
                  <AlertCircle className="h-4 w-4" />
                  {error}
                </div>
              )}

              <div className="flex flex-wrap items-center gap-2">
                <div className="relative min-w-[240px] flex-1">
                  <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-500" />
                  <input
                    value={search}
                    onChange={(event) => setSearch(event.target.value)}
                    placeholder="Buscar por número, título, localización, personajes, INT/EXT o DÍA/NOCHE..."
                    className="input w-full pl-9"
                  />
                </div>

                {mode === 'SELECTED_SCENES' && (
                  <>
                    <button type="button" onClick={handleSelectAll} className="rounded-xl border border-white/10 px-3 py-2 text-sm hover:bg-white/5">Seleccionar todas</button>
                    <button type="button" onClick={handleClearSelection} className="rounded-xl border border-white/10 px-3 py-2 text-sm hover:bg-white/5">Limpiar selección</button>
                    <button type="button" onClick={handleSelectVisible} disabled={(visibleSequenceIds ?? []).length === 0} className="rounded-xl border border-white/10 px-3 py-2 text-sm hover:bg-white/5 disabled:opacity-40">Seleccionar visibles</button>
                  </>
                )}
              </div>
            </div>

            <div className="min-h-0 flex-1 overflow-y-auto p-5">
              {mode === 'SEQUENCE' && (
                <div className="space-y-3">
                  {filteredSequenceItems.map((item) => {
                    const isSelected = selectedSequenceId === item.sequence.sequence_id
                    return (
                      <button
                        key={item.sequence.sequence_id}
                        type="button"
                        onClick={() => setSelectedSequenceId(item.sequence.sequence_id)}
                        className={`w-full rounded-2xl border p-4 text-left transition-colors ${isSelected ? 'border-amber-400/40 bg-amber-500/10' : 'border-white/10 hover:border-white/20'}`}
                      >
                        <div className="flex items-start justify-between gap-3">
                          <div className="min-w-0 flex-1">
                            <div className="flex flex-wrap items-center gap-2">
                              <span className="text-xs font-semibold text-amber-300">SEQ {item.sequence.sequence_number}</span>
                              <span className="truncate text-sm font-medium text-white">{item.displayName}</span>
                            </div>
                            <div className="mt-2 flex flex-wrap gap-2 text-[11px] text-gray-400">
                              <span>{item.sceneCount} escenas</span>
                              {item.location && <span>{item.location}</span>}
                              {item.intExt && <span>{item.intExt}</span>}
                              {item.timeOfDay && <span>{item.timeOfDay}</span>}
                            </div>
                            {(item.characters ?? []).length > 0 && (
                              <div className="mt-2 flex flex-wrap gap-1">
                                {item.characters.slice(0, 6).map((character) => (
                                  <span key={character} className="rounded-full bg-white/5 px-2 py-0.5 text-[10px] text-slate-300">{character}</span>
                                ))}
                              </div>
                            )}
                          </div>
                          {isSelected && <Check className="h-4 w-4 text-amber-300" />}
                        </div>
                      </button>
                    )
                  })}
                </div>
              )}

              {mode === 'SELECTED_SCENES' && (
                <div className="space-y-3">
                  <div className="flex items-center gap-2 text-sm text-gray-300">
                    <Layers className="h-4 w-4" />
                    {selectedSequenceCount} secuencias seleccionadas
                  </div>

                  {(filteredSequenceItems ?? []).length === 0 ? (
                    <div className="rounded-2xl border border-dashed border-white/10 px-4 py-8 text-sm text-slate-500">
                      No hay secuencias visibles con el filtro actual.
                    </div>
                  ) : (
                    filteredSequenceItems.map((item) => {
                      const isSelected = selectedSequenceIds.includes(item.sequence.sequence_id)
                      return (
                        <label
                          key={item.sequence.sequence_id}
                          className={`flex cursor-pointer items-start gap-3 rounded-2xl border p-4 transition-colors ${isSelected ? 'border-amber-400/40 bg-amber-500/10' : 'border-white/10 hover:border-white/20'}`}
                        >
                          <input
                            type="checkbox"
                            checked={isSelected}
                            onChange={() => toggleSequence(item.sequence.sequence_id)}
                            className="mt-1"
                          />
                          <div className="min-w-0 flex-1">
                            <div className="flex flex-wrap items-center gap-2">
                              <span className="text-xs font-semibold text-amber-300">SEQ {item.sequence.sequence_number}</span>
                              <span className="truncate text-sm font-medium text-white">{item.displayName}</span>
                              <span className="rounded-full bg-white/5 px-2 py-0.5 text-[10px] text-slate-300">{item.sceneCount} escenas</span>
                            </div>
                            <div className="mt-2 flex flex-wrap gap-2 text-[11px] text-gray-400">
                              {item.location && <span>{item.location}</span>}
                              {item.intExt && <span>{item.intExt}</span>}
                              {item.timeOfDay && <span>{item.timeOfDay}</span>}
                              <span>{item.sequence.storyboard_status}</span>
                            </div>
                            {(item.characters ?? []).length > 0 && (
                              <div className="mt-2 flex flex-wrap gap-1">
                                {item.characters.slice(0, 8).map((character) => (
                                  <span key={character} className="rounded-full bg-white/5 px-2 py-0.5 text-[10px] text-slate-300">{character}</span>
                                ))}
                              </div>
                            )}
                          </div>
                        </label>
                      )
                    })
                  )}
                </div>
              )}

              {mode === 'SINGLE_SCENE' && (
                <div className="rounded-2xl border border-white/10 divide-y divide-white/5 overflow-hidden">
                  {filteredScenes.map((scene) => {
                    const checked = selectedSingleSceneNumber === scene.scene_number
                    return (
                      <label key={scene.scene_number} className="flex cursor-pointer items-start gap-3 px-4 py-3 hover:bg-white/[0.03]">
                        <input
                          type="radio"
                          name="single-scene"
                          checked={checked}
                          onChange={() => setSelectedSingleSceneNumber(scene.scene_number)}
                          className="mt-1"
                        />
                        <div className="min-w-0 flex-1">
                          <div className="flex flex-wrap items-center gap-2">
                            <span className="text-xs font-semibold text-amber-300">ESC {String(scene.scene_number).padStart(2, '0')}</span>
                            <span className="truncate text-sm font-medium text-white">{scene.scene_heading}</span>
                          </div>
                          {scene.narrative_text && <p className="mt-1 line-clamp-2 text-xs text-gray-400">{scene.narrative_text}</p>}
                        </div>
                      </label>
                    )
                  })}
                </div>
              )}

              {mode === 'SCENE_RANGE' && (
                <div className="grid max-w-md grid-cols-2 gap-3">
                  <label className="space-y-2 text-sm text-gray-300">
                    <span>Escena inicial</span>
                    <input className="input w-full" value={rangeStart} onChange={(event) => setRangeStart(event.target.value)} />
                  </label>
                  <label className="space-y-2 text-sm text-gray-300">
                    <span>Escena final</span>
                    <input className="input w-full" value={rangeEnd} onChange={(event) => setRangeEnd(event.target.value)} />
                  </label>
                </div>
              )}

              {mode === 'FULL_SCRIPT' && (
                <div className="rounded-2xl border border-amber-500/20 bg-amber-500/5 p-4 text-sm text-amber-100">
                  Este modo generará el storyboard para todo el material detectado. Úsalo solo si no necesitas selección parcial.
                </div>
              )}
            </div>

            <div className="sticky bottom-0 border-t border-white/10 bg-[#0f1013] px-6 py-4">
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div className="text-xs text-gray-500">{helperStatus}</div>
                <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
                  {!canConfirm && mode !== 'FULL_SCRIPT' && (
                    <span className="text-xs text-amber-300">Selecciona al menos una secuencia o una escena para continuar.</span>
                  )}
                  <button type="button" onClick={onClose} className="rounded-xl border border-white/10 px-4 py-2 text-sm hover:bg-white/5">Cancelar</button>
                  <button
                    type="button"
                    disabled={!canConfirm}
                    onClick={() => onConfirm(buildSelection())}
                    className="rounded-xl border border-amber-500/20 bg-amber-500 px-4 py-2 text-sm font-medium text-black disabled:opacity-40"
                  >
                    {primaryButtonLabel}
                  </button>
                </div>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  )
}
