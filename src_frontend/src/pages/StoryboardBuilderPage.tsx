import { useState, useEffect, useCallback, useMemo } from 'react'
import { useParams } from 'react-router-dom'
import { Plus, Save, Loader2, ArrowLeft, Film, RefreshCw } from 'lucide-react'
import { storyboardApi } from '@/api/storyboard'
import { ShotCard } from '@/components/storyboard/ShotCard'
import { AssetPickerModal } from '@/components/storyboard/AssetPickerModal'
import type {
  DirtyShot,
  StoryboardGeneratePayload,
  StoryboardGenerationMode,
  StoryboardSequence,
  StoryboardShot,
} from '@/types/storyboard'

function toDirtyShot(shot: StoryboardShot): DirtyShot {
  return { ...shot, isDirty: false }
}

const MODE_OPTIONS: Array<{ value: StoryboardGenerationMode; label: string }> = [
  { value: 'FULL_SCRIPT', label: 'Guion completo' },
  { value: 'SEQUENCE', label: 'Por secuencia' },
  { value: 'SCENE_RANGE', label: 'Por rango de escenas' },
  { value: 'SINGLE_SCENE', label: 'Escena individual' },
]

export default function StoryboardBuilderPage() {
  const { projectId } = useParams<{ projectId: string }>()
  const [shots, setShots] = useState<DirtyShot[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [isGenerating, setIsGenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [pickerOpen, setPickerOpen] = useState(false)
  const [selectedShotId, setSelectedShotId] = useState<string | null>(null)
  const [sequences, setSequences] = useState<StoryboardSequence[]>([])
  const [selectedMode, setSelectedMode] = useState<StoryboardGenerationMode>('FULL_SCRIPT')
  const [selectedSequenceId, setSelectedSequenceId] = useState<string>('')
  const [sceneStart, setSceneStart] = useState('1')
  const [sceneEnd, setSceneEnd] = useState('1')
  const [singleScene, setSingleScene] = useState('1')
  const [stylePreset, setStylePreset] = useState('cinematic_realistic')
  const [shotsPerScene, setShotsPerScene] = useState(3)

  const fetchSequences = useCallback(async () => {
    if (!projectId) return
    try {
      const data = await storyboardApi.listSequences(projectId)
      setSequences(data)
      if (!selectedSequenceId && data.length > 0) {
        setSelectedSequenceId(data[0].sequence_id)
      }
    } catch (err) {
      console.error(err)
    }
  }, [projectId, selectedSequenceId])

  const fetchShots = useCallback(async () => {
    if (!projectId) return
    setIsLoading(true)
    setError(null)
    try {
      const data = await storyboardApi.listShots(projectId)
      setShots(data.map(toDirtyShot))
    } catch (err) {
      setError('Failed to load storyboard shots')
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }, [projectId])

  useEffect(() => {
    fetchShots()
    fetchSequences()
  }, [fetchShots, fetchSequences])

  const currentSequence = useMemo(
    () => sequences.find((sequence) => sequence.sequence_id === selectedSequenceId) || null,
    [sequences, selectedSequenceId]
  )

  const filteredShots = useMemo(() => {
    if (selectedMode === 'SEQUENCE' && selectedSequenceId) {
      return shots.filter((shot) => shot.sequence_id === selectedSequenceId)
    }
    if (selectedMode === 'SCENE_RANGE') {
      const start = Number(sceneStart || '0')
      const end = Number(sceneEnd || '0')
      return shots.filter((shot) => (shot.scene_number || 0) >= start && (shot.scene_number || 0) <= end)
    }
    if (selectedMode === 'SINGLE_SCENE') {
      const scene = Number(singleScene || '0')
      return shots.filter((shot) => (shot.scene_number || 0) === scene)
    }
    return shots
  }, [shots, selectedMode, selectedSequenceId, sceneStart, sceneEnd, singleScene])

  const handleGenerate = async (regenerateSequence = false) => {
    if (!projectId) return
    setIsGenerating(true)
    setError(null)
    try {
      if (regenerateSequence && selectedSequenceId) {
        await storyboardApi.regenerateSequence(projectId, selectedSequenceId, {
          style_preset: stylePreset,
          shots_per_scene: shotsPerScene,
        })
      } else {
        const payload: StoryboardGeneratePayload = {
          mode: selectedMode,
          sequence_id: selectedMode === 'SEQUENCE' ? selectedSequenceId : null,
          scene_start: selectedMode === 'SCENE_RANGE' ? Number(sceneStart) : selectedMode === 'SINGLE_SCENE' ? Number(singleScene) : null,
          scene_end: selectedMode === 'SCENE_RANGE' ? Number(sceneEnd) : selectedMode === 'SINGLE_SCENE' ? Number(singleScene) : null,
          selected_scene_ids: selectedMode === 'SINGLE_SCENE' ? [singleScene] : [],
          style_preset: stylePreset,
          shots_per_scene: shotsPerScene,
          overwrite: true,
        }
        await storyboardApi.generate(projectId, payload)
      }
      await Promise.all([fetchShots(), fetchSequences()])
    } catch (err) {
      console.error(err)
      setError('Failed to generate storyboard')
    } finally {
      setIsGenerating(false)
    }
  }

  const handleUpdateShot = (shotId: string, updates: Partial<DirtyShot>) => {
    setShots((prev) => prev.map((shot) => (shot.id === shotId ? { ...shot, ...updates } : shot)))
  }

  const handleDeleteShot = async (shotId: string) => {
    if (!projectId || isSaving) return
    try {
      await storyboardApi.deleteShot(projectId, shotId)
      setShots((prev) => prev.filter((shot) => shot.id !== shotId))
    } catch (err) {
      console.error('Failed to delete shot:', err)
    }
  }

  const handleAddShot = async () => {
    if (!projectId || isSaving) return
    try {
      const newShot = await storyboardApi.createShot(projectId, {
        sequence_id: currentSequence?.sequence_id,
        sequence_order: filteredShots.length + 1,
      })
      setShots((prev) => [...prev, toDirtyShot(newShot)])
    } catch (err) {
      console.error('Failed to create shot:', err)
    }
  }

  const handleSave = async () => {
    if (!projectId || isSaving) return
    const dirtyShots = shots.filter((s) => s.isDirty)
    if (dirtyShots.length === 0) return

    setIsSaving(true)
    try {
      for (const shot of dirtyShots) {
        await storyboardApi.updateShot(projectId, shot.id, {
          narrative_text: shot.narrative_text,
          asset_id: shot.asset_id,
          shot_type: shot.shot_type,
          visual_mode: shot.visual_mode,
          sequence_id: shot.sequence_id,
          sequence_order: shot.sequence_order,
        })
      }
      setShots((prev) => prev.map((s) => ({ ...s, isDirty: false })))
    } catch (err) {
      console.error('Failed to save shots:', err)
      await fetchShots()
    } finally {
      setIsSaving(false)
    }
  }

  const handleOpenPicker = (shotId: string) => {
    setSelectedShotId(shotId)
    setPickerOpen(true)
  }

  const handleSelectAsset = (assetId: string, previewUrl: string) => {
    if (!selectedShotId) return
    setShots((prev) =>
      prev.map((shot) =>
        shot.id === selectedShotId
          ? { ...shot, asset_id: assetId, thumbnail_url: previewUrl, isDirty: true }
          : shot
      )
    )
    setPickerOpen(false)
    setSelectedShotId(null)
  }

  const dirtyCount = shots.filter((s) => s.isDirty).length

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="flex items-center gap-3 text-amber-400">
          <Loader2 className="w-6 h-6 animate-spin" />
          <span>Loading storyboard...</span>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-dark-100">
      <div className="max-w-7xl mx-auto p-6 space-y-6">
        <div className="flex items-center justify-between mb-8 gap-4 flex-wrap">
          <div className="flex items-center gap-4">
            <a
              href={`/projects/${projectId}`}
              className="p-2 rounded-lg hover:bg-white/10 text-gray-400 hover:text-white transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
            </a>
            <div>
              <h1 className="text-2xl font-bold text-white flex items-center gap-3">
                <Film className="w-6 h-6 text-amber-400" />
                Storyboard Builder
              </h1>
              <p className="text-gray-400 text-sm mt-1">
                {filteredShots.length} shot{filteredShots.length !== 1 ? 's' : ''}
                {dirtyCount > 0 && <span className="text-amber-400 ml-2">• {dirtyCount} unsaved</span>}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => {
                fetchShots()
                fetchSequences()
              }}
              className="flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
              Refresh
            </button>
            <button
              onClick={handleAddShot}
              disabled={isSaving}
              className="flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-colors disabled:opacity-50"
            >
              <Plus className="w-4 h-4" />
              Add Shot
            </button>
            <button
              onClick={handleSave}
              disabled={isSaving || dirtyCount === 0}
              className="flex items-center gap-2 px-4 py-2 bg-amber-500 hover:bg-amber-400 text-black rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSaving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
              Guardar Storyboard
            </button>
          </div>
        </div>

        <section className="card bg-dark-200/80 border border-white/5 p-6 space-y-4">
          <div>
            <h2 className="text-lg font-semibold text-white">Modo de storyboard</h2>
            <p className="text-sm text-slate-400 mt-1">Elige generación completa, por secuencia o parcial.</p>
          </div>

          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <div>
              <label className="label">Modo</label>
              <select className="input" value={selectedMode} onChange={(event) => setSelectedMode(event.target.value as StoryboardGenerationMode)}>
                {MODE_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>{option.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="label">Style preset</label>
              <input className="input" value={stylePreset} onChange={(event) => setStylePreset(event.target.value)} />
            </div>
            <div>
              <label className="label">Shots por escena</label>
              <input className="input" type="number" min={1} max={8} value={shotsPerScene} onChange={(event) => setShotsPerScene(Number(event.target.value || 3))} />
            </div>
            {selectedMode === 'SEQUENCE' && (
              <div>
                <label className="label">Secuencia</label>
                <select className="input" value={selectedSequenceId} onChange={(event) => setSelectedSequenceId(event.target.value)}>
                  {sequences.map((sequence) => (
                    <option key={sequence.sequence_id} value={sequence.sequence_id}>
                      Secuencia {sequence.sequence_number} — {sequence.title}
                    </option>
                  ))}
                </select>
              </div>
            )}
            {selectedMode === 'SCENE_RANGE' && (
              <>
                <div>
                  <label className="label">Escena inicial</label>
                  <input className="input" type="number" min={1} value={sceneStart} onChange={(event) => setSceneStart(event.target.value)} />
                </div>
                <div>
                  <label className="label">Escena final</label>
                  <input className="input" type="number" min={1} value={sceneEnd} onChange={(event) => setSceneEnd(event.target.value)} />
                </div>
              </>
            )}
            {selectedMode === 'SINGLE_SCENE' && (
              <div>
                <label className="label">Escena</label>
                <input className="input" type="number" min={1} value={singleScene} onChange={(event) => setSingleScene(event.target.value)} />
              </div>
            )}
          </div>

          <div className="flex flex-wrap gap-3">
            <button
              onClick={() => handleGenerate(false)}
              disabled={isGenerating}
              className="btn-primary"
            >
              {isGenerating ? 'Generando...' : selectedMode === 'FULL_SCRIPT' ? 'Generar storyboard completo' : 'Generar storyboard parcial'}
            </button>
            {selectedMode === 'SEQUENCE' && selectedSequenceId && (
              <button
                onClick={() => handleGenerate(true)}
                disabled={isGenerating}
                className="btn-secondary"
              >
                Regenerar secuencia
              </button>
            )}
          </div>
        </section>

        <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {sequences.map((sequence) => (
            <article key={sequence.sequence_id} className="rounded-2xl border border-white/10 bg-dark-300/40 p-5">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h3 className="text-white font-semibold">Secuencia {sequence.sequence_number} — {sequence.title}</h3>
                  <p className="mt-1 text-sm text-slate-400">{sequence.summary}</p>
                </div>
                <span className="text-xs text-amber-400">v{sequence.current_version || 0}</span>
              </div>
              <div className="mt-3 text-xs text-slate-400 space-y-1">
                <p>Escenas: {sequence.included_scenes.join(', ')}</p>
                <p>Estado: {sequence.storyboard_status}</p>
                <p>Personajes: {sequence.characters.join(', ') || '—'}</p>
              </div>
              <div className="mt-4 flex gap-2">
                <button
                  className="btn-secondary"
                  onClick={() => {
                    setSelectedMode('SEQUENCE')
                    setSelectedSequenceId(sequence.sequence_id)
                  }}
                >
                  Ver esta secuencia
                </button>
              </div>
            </article>
          ))}
        </section>

        {error && (
          <div className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400">
            {error}
          </div>
        )}

        {filteredShots.length === 0 ? (
          <div className="text-center py-20">
            <Film className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-white mb-2">No shots yet</h2>
            <p className="text-gray-400 mb-6">Genera storyboard completo o parcial para empezar.</p>
            <button onClick={() => handleGenerate(false)} className="inline-flex items-center gap-2 px-4 py-2 bg-amber-500 hover:bg-amber-400 text-black rounded-lg font-medium transition-colors">
              <Plus className="w-4 h-4" />
              Generar storyboard
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {filteredShots.map((shot) => (
              <ShotCard
                key={shot.id}
                shot={shot}
                onUpdate={handleUpdateShot}
                onDelete={handleDeleteShot}
                onOpenPicker={handleOpenPicker}
                isSaving={isSaving}
              />
            ))}
          </div>
        )}

        <AssetPickerModal
          isOpen={pickerOpen}
          projectId={projectId || ''}
          currentAssetId={shots.find((s) => s.id === selectedShotId)?.asset_id}
          onSelect={handleSelectAsset}
          onClose={() => {
            setPickerOpen(false)
            setSelectedShotId(null)
          }}
        />
      </div>
    </div>
  )
}
