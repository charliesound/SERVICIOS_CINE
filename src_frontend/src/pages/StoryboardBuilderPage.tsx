import { useState, useEffect, useCallback, useMemo } from 'react'
import { useParams } from 'react-router-dom'
import { Plus, Save, Loader2, ArrowLeft, Film, RefreshCw, Eye, FileText, ListChecks, Sparkles, AlertTriangle } from 'lucide-react'
import { storyboardApi } from '@/api/storyboard'
import { ShotCard } from '@/components/storyboard/ShotCard'
import { AssetPickerModal } from '@/components/storyboard/AssetPickerModal'
import type {
  CinematicShotMetadata,
  DirtyShot,
  FullScriptAnalysisResult,
  ScriptSequenceMapEntry,
  SequenceStoryboardPlan,
  StoryboardGeneratePayload,
  StoryboardSelectionMode,
  StoryboardSequence,
  StoryboardShot,
} from '@/types/storyboard'

function toDirtyShot(shot: StoryboardShot): DirtyShot {
  return { ...shot, isDirty: false }
}

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
  const [selectedMode] = useState<StoryboardSelectionMode>('FULL_SCRIPT')
  const [selectedSequenceId, setSelectedSequenceId] = useState<string>('')
  const [selectedSequenceIds, setSelectedSequenceIds] = useState<string[]>([])
  const [stylePreset] = useState('cinematic_realistic')
  const [shotsPerScene] = useState(3)
  const [directorLensId] = useState<string>('')
  const [montageProfileId] = useState<string>('')
  const [useCinematicIntelligence] = useState(false)
  const [useMontageIntelligence] = useState(false)
  const [validatePrompts] = useState(false)
  const [expandedMetadata, setExpandedMetadata] = useState<string | null>(null)

  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisResult, setAnalysisResult] = useState<FullScriptAnalysisResult | null>(null)
  const [selectedSequenceEntry, setSelectedSequenceEntry] = useState<ScriptSequenceMapEntry | null>(null)
  const [shotPlan, setShotPlan] = useState<SequenceStoryboardPlan | null>(null)
  const [isPlanning, setIsPlanning] = useState(false)
  const [activeTab, setActiveTab] = useState<'analyze' | 'sequences' | 'shots'>('analyze')

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
    () => sequences.find((s) => s.sequence_id === selectedSequenceId) || null,
    [sequences, selectedSequenceId]
  )

  const filteredShots = useMemo(() => {
    if (selectedMode === 'SEQUENCE' && selectedSequenceId) {
      return shots.filter((shot) => shot.sequence_id === selectedSequenceId)
    }
    return shots
  }, [shots, selectedMode, selectedSequenceId])

  const handleAnalyzeFullScript = async () => {
    if (!projectId) return
    setIsAnalyzing(true)
    setError(null)
    setAnalysisResult(null)
    setShotPlan(null)
    setSelectedSequenceEntry(null)
    try {
      const data = await storyboardApi.analyzeFullScript(projectId)
      setAnalysisResult(data)
      setActiveTab('analyze')
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || 'Error analyzing full script')
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handlePlanSequence = async (entry: ScriptSequenceMapEntry) => {
    if (!projectId) return
    setIsPlanning(true)
    setError(null)
    setSelectedSequenceEntry(entry)
    setShotPlan(null)
    try {
      const plan = await storyboardApi.planSequence(projectId, entry.sequence_id)
      setShotPlan(plan)
      setActiveTab('sequences')
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || 'Error planning sequence')
    } finally {
      setIsPlanning(false)
    }
  }

  const handleGenerateSequence = async (sequenceId: string) => {
    if (!projectId) return
    setIsGenerating(true)
    setError(null)
    try {
      await storyboardApi.generateBySequence(projectId, sequenceId, {
        style_preset: stylePreset,
        shots_per_scene: shotsPerScene,
        overwrite: true,
      })
      await Promise.all([fetchShots(), fetchSequences()])
      setActiveTab('shots')
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Error generating sequence')
    } finally {
      setIsGenerating(false)
    }
  }

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
          generation_mode: selectedMode,
          sequence_id: selectedMode === 'SEQUENCE' ? selectedSequenceId : undefined,
          style_preset: stylePreset,
          visual_mode: stylePreset,
          shots_per_scene: shotsPerScene,
          overwrite: true,
          director_lens_id: useCinematicIntelligence ? (directorLensId || undefined) : undefined,
          montage_profile_id: useMontageIntelligence ? (montageProfileId || undefined) : undefined,
          use_cinematic_intelligence: useCinematicIntelligence,
          use_montage_intelligence: useMontageIntelligence,
          validate_prompts: validatePrompts,
        }
        await storyboardApi.generate(projectId, payload)
      }
      await Promise.all([fetchShots(), fetchSequences()])
    } catch (err: any) {
      console.error(err)
      setError(err?.response?.data?.detail || 'Error generating storyboard')
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
            <button onClick={() => { fetchShots(); fetchSequences() }}
              className="flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-colors">
              <RefreshCw className="w-4 h-4" /> Refresh
            </button>
            <button onClick={handleAddShot} disabled={isSaving}
              className="flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-colors disabled:opacity-50">
              <Plus className="w-4 h-4" /> Add Shot
            </button>
            <button onClick={handleSave} disabled={isSaving || dirtyCount === 0}
              className="flex items-center gap-2 px-4 py-2 bg-amber-500 hover:bg-amber-400 text-black rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
              {isSaving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
              Guardar Storyboard
            </button>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex gap-1 border-b border-white/10 pb-1">
          {[
            { id: 'analyze' as const, label: '1. Analizar guion', icon: FileText },
            { id: 'sequences' as const, label: '2. Secuencias', icon: ListChecks },
            { id: 'shots' as const, label: '3. Planos generados', icon: Film },
          ].map((tab) => (
            <button key={tab.id} onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2.5 text-sm font-medium rounded-t-lg transition-all ${
                activeTab === tab.id
                  ? 'bg-amber-400/10 text-amber-300 border-b-2 border-amber-400'
                  : 'text-slate-400 hover:text-white hover:bg-white/5'
              }`}>
              <tab.icon className="w-4 h-4" /> {tab.label}
            </button>
          ))}
        </div>

        {/* TAB 1: Analyze Full Script */}
        {activeTab === 'analyze' && (
          <div className="space-y-6">
            <section className="card bg-dark-200/80 border border-white/5 p-6 space-y-4">
              <h2 className="text-lg font-semibold text-white">Análisis del guion completo</h2>
              <p className="text-sm text-slate-400">
                Analiza el guion completo para generar sinopsis, personajes, localizaciones y mapa de secuencias.
                Después podrás seleccionar una secuencia para planificar y generar su storyboard.
              </p>
              <button onClick={handleAnalyzeFullScript} disabled={isAnalyzing}
                className="inline-flex items-center gap-2 px-6 py-3 bg-amber-500/20 border border-amber-500/30 rounded-xl text-amber-300 font-medium hover:bg-amber-500/30 transition-all disabled:opacity-40">
                {isAnalyzing ? <Loader2 className="w-5 h-5 animate-spin" /> : <FileText className="w-5 h-5" />}
                {isAnalyzing ? 'Analizando guion completo...' : 'Analizar guion completo'}
              </button>
            </section>

            {analysisResult && (
              <>
                {/* Synopsis */}
                <section className="card bg-dark-200/80 border border-white/5 p-6 space-y-3">
                  <h3 className="text-base font-semibold text-amber-300 flex items-center gap-2">
                    <Sparkles className="w-4 h-4" /> Sinopsis
                  </h3>
                  <div className="grid gap-3 md:grid-cols-2">
                    <div className="space-y-2">
                      <p className="text-xs text-slate-400">Logline</p>
                      <p className="text-sm text-white">{analysisResult.synopsis.logline || '—'}</p>
                    </div>
                    <div className="space-y-2">
                      <p className="text-xs text-slate-400">Premisa</p>
                      <p className="text-sm text-white">{analysisResult.synopsis.premise || '—'}</p>
                    </div>
                    <div className="space-y-2">
                      <p className="text-xs text-slate-400">Tema</p>
                      <p className="text-sm text-white">{analysisResult.synopsis.theme || '—'}</p>
                    </div>
                    <div className="space-y-2">
                      <p className="text-xs text-slate-400">Género / Tono</p>
                      <p className="text-sm text-white">{analysisResult.synopsis.genre || '—'} • {analysisResult.synopsis.tone || '—'}</p>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <p className="text-xs text-slate-400">Sinopsis extendida</p>
                    <p className="text-sm text-white">{analysisResult.synopsis.synopsis_extended || '—'}</p>
                  </div>
                  <div className="grid gap-3 md:grid-cols-2">
                    <div>
                      <p className="text-xs text-slate-400 mb-1">Personajes principales</p>
                      <div className="flex flex-wrap gap-1">
                        {analysisResult.synopsis.main_characters.map((c, i) => (
                          <span key={i} className="px-2 py-0.5 text-xs bg-amber-400/10 text-amber-300 rounded-full">{c}</span>
                        ))}
                      </div>
                    </div>
                    <div>
                      <p className="text-xs text-slate-400 mb-1">Localizaciones principales</p>
                      <div className="flex flex-wrap gap-1">
                        {analysisResult.synopsis.main_locations.map((l, i) => (
                          <span key={i} className="px-2 py-0.5 text-xs bg-cyan-400/10 text-cyan-300 rounded-full">{l}</span>
                        ))}
                      </div>
                    </div>
                  </div>
                </section>

                {/* Sequence Map */}
                <section className="card bg-dark-200/80 border border-white/5 p-6 space-y-4">
                  <h3 className="text-base font-semibold text-amber-300 flex items-center gap-2">
                    <ListChecks className="w-4 h-4" /> Mapa de secuencias ({analysisResult.sequence_map.total_sequences} detectadas)
                  </h3>
                  <div className="grid gap-3">
                    {analysisResult.sequence_map.sequences.map((entry) => (
                      <div key={entry.sequence_id}
                        className="rounded-xl border border-white/10 bg-[#0a1016] p-4 hover:border-amber-500/30 transition-all">
                        <div className="flex items-start justify-between gap-4">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <span className="text-xs font-bold text-amber-400">#{entry.sequence_number}</span>
                              <h4 className="text-sm font-semibold text-white">{entry.title}</h4>
                              {entry.recommended_for_storyboard && (
                                <span className="px-1.5 py-0.5 text-[10px] font-medium bg-green-400/10 text-green-300 rounded">Recomendada</span>
                              )}
                            </div>
                            <p className="text-xs text-slate-400 mb-2">{entry.summary}</p>
                            <div className="flex flex-wrap gap-1 mb-2">
                              {entry.characters.map((ch, i) => (
                                <span key={i} className="px-1.5 py-0.5 text-[10px] bg-slate-700/50 text-slate-300 rounded">{ch}</span>
                              ))}
                            </div>
                            <div className="grid grid-cols-3 gap-2 text-[10px] text-slate-500">
                              <span>Función: {entry.dramatic_function}</span>
                              <span>Meta: {entry.emotional_goal}</span>
                              <span>Planos: {entry.suggested_shot_count}</span>
                            </div>
                          </div>
                          <button onClick={() => handlePlanSequence(entry)} disabled={isPlanning}
                            className="shrink-0 px-4 py-2 text-xs font-medium bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 rounded-xl hover:bg-cyan-500/20 transition-all disabled:opacity-40">
                            {isPlanning && selectedSequenceEntry?.sequence_id === entry.sequence_id
                              ? 'Planificando...' : 'Planificar storyboard'}
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </section>

                {/* Shot Plan */}
                {shotPlan && (
                  <section className="card bg-dark-200/80 border border-cyan-500/20 p-6 space-y-4">
                    <h3 className="text-base font-semibold text-cyan-300 flex items-center gap-2">
                      <Eye className="w-4 h-4" /> Plan de storyboard: {shotPlan.sequence_title}
                    </h3>
                    <p className="text-xs text-slate-400">{shotPlan.continuity_plan.join(' | ')}</p>
                    <div className="grid gap-2">
                      {shotPlan.shot_plan.map((shot) => (
                        <div key={shot.shot_number}
                          className="rounded-xl border border-white/10 bg-[#0a1016] p-3">
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-xs font-bold text-cyan-400">#{shot.shot_number} {shot.shot_type}</span>
                            <span className="text-[10px] text-slate-500">{shot.framing} • {shot.camera_angle} • {shot.camera_movement} • {shot.lens_suggestion}</span>
                          </div>
                          <p className="text-xs text-slate-300 mb-1">{shot.action || shot.prompt_brief}</p>
                          <p className="text-[10px] text-slate-500 italic">{shot.shot_plan_reason}</p>
                        </div>
                      ))}
                    </div>
                    <div className="flex gap-3">
                      <button onClick={() => selectedSequenceEntry && handleGenerateSequence(selectedSequenceEntry.sequence_id)}
                        disabled={isGenerating}
                        className="flex items-center gap-2 px-6 py-3 bg-amber-500/20 border border-amber-500/30 rounded-xl text-amber-300 font-medium hover:bg-amber-500/30 transition-all disabled:opacity-40">
                        {isGenerating ? <Loader2 className="w-5 h-5 animate-spin" /> : <Sparkles className="w-5 h-5" />}
                        {isGenerating ? 'Generando storyboard...' : 'Generar storyboard de esta secuencia'}
                      </button>
                    </div>
                  </section>
                )}
              </>
            )}
          </div>
        )}

        {/* TAB 2: Sequences */}
        {activeTab === 'sequences' && (
          <section className="card bg-dark-200/80 border border-white/5 p-6 space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-white">Secuencias del proyecto</h2>
              <button onClick={handleAnalyzeFullScript} disabled={isAnalyzing}
                className="flex items-center gap-2 px-4 py-2 text-sm bg-amber-500/10 border border-amber-500/30 text-amber-300 rounded-xl hover:bg-amber-500/20 transition-all">
                {isAnalyzing ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
                Re-analizar guion
              </button>
            </div>
            {sequences.length === 0 ? (
              <div className="text-center py-10">
                <p className="text-slate-400 mb-4">No hay secuencias disponibles. Analiza el guion completo primero.</p>
                <button onClick={handleAnalyzeFullScript} disabled={isAnalyzing}
                  className="inline-flex items-center gap-2 px-4 py-2 bg-amber-500/20 border border-amber-500/30 rounded-xl text-amber-300">
                  <FileText className="w-4 h-4" /> Analizar guion completo
                </button>
              </div>
            ) : (
              <>
                <div className="grid gap-3">
                  {sequences.map((seq) => (
                    <div key={seq.sequence_id}
                      className={`rounded-xl border p-4 transition-all cursor-pointer ${
                        selectedSequenceIds.includes(seq.sequence_id)
                          ? 'border-amber-500/50 bg-amber-400/10'
                          : 'border-white/10 bg-[#0a1016] hover:border-white/20'
                      }`}
                      onClick={() => {
                        setSelectedSequenceIds([seq.sequence_id])
                        setSelectedSequenceId(seq.sequence_id)
                      }}>
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <h3 className="text-sm font-semibold text-white">Secuencia {seq.sequence_number} — {seq.title}</h3>
                          <p className="text-xs text-slate-400 mt-1">{seq.summary}</p>
                        </div>
                        <span className="text-xs text-amber-400 shrink-0">v{seq.current_version || 0}</span>
                      </div>
                      <div className="mt-2 text-[10px] text-slate-500 space-y-0.5">
                        <p>Escenas: {seq.included_scenes.join(', ')}</p>
                        <p>Estado: {seq.storyboard_status}</p>
                      </div>
                    </div>
                  ))}
                </div>
                {selectedSequenceId && (
                  <div className="flex flex-wrap gap-3 pt-2">
                    <button onClick={() => handleGenerate(false)} disabled={isGenerating}
                      className="flex items-center gap-2 px-6 py-3 bg-amber-500/20 border border-amber-500/30 rounded-xl text-amber-300 font-medium hover:bg-amber-500/30 transition-all disabled:opacity-40">
                      {isGenerating ? <Loader2 className="w-5 h-5 animate-spin" /> : <Sparkles className="w-5 h-5" />}
                      Generar storyboard de esta secuencia
                    </button>
                    <button onClick={() => handleGenerate(true)} disabled={isGenerating}
                      className="flex items-center gap-2 px-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white font-medium hover:bg-white/20 transition-all disabled:opacity-40">
                      <RefreshCw className="w-4 h-4" /> Regenerar
                    </button>
                  </div>
                )}
              </>
            )}
          </section>
        )}

        {/* TAB 3: Generated Shots */}
        {activeTab === 'shots' && (
          <>
            <section className="card bg-dark-200/80 border border-white/5 p-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="text-lg font-semibold text-white">Planos generados</h2>
                  <p className="text-sm text-slate-400">{filteredShots.length} planos</p>
                </div>
                <div className="flex gap-2">
                  {selectedSequenceId && (
                    <button onClick={() => handleGenerate(true)} disabled={isGenerating}
                      className="flex items-center gap-2 px-4 py-2 text-sm bg-white/10 border border-white/20 text-white rounded-xl hover:bg-white/20 transition-all">
                      <RefreshCw className="w-4 h-4" /> Regenerar secuencia
                    </button>
                  )}
                  <select className="input text-sm w-auto" value={selectedSequenceId}
                    onChange={(e) => setSelectedSequenceId(e.target.value)}>
                    <option value="">Todas las secuencias</option>
                    {sequences.map((s) => (
                      <option key={s.sequence_id} value={s.sequence_id}>Secuencia {s.sequence_number} — {s.title}</option>
                    ))}
                  </select>
                </div>
              </div>
            </section>

            {filteredShots.length === 0 ? (
              <div className="text-center py-20">
                <Film className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                <h2 className="text-xl font-semibold text-white mb-2">No shots yet</h2>
                <p className="text-gray-400 mb-6">Selecciona una secuencia y genera su storyboard.</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {filteredShots.map((shot) => (
                  <div key={shot.id} className="space-y-1">
                    <ShotCard shot={shot} onUpdate={handleUpdateShot} onDelete={handleDeleteShot}
                      onOpenPicker={handleOpenPicker} isSaving={isSaving} />
                    {shot.metadata_json && (
                      <div>
                        <button onClick={() => setExpandedMetadata(expandedMetadata === shot.id ? null : shot.id)}
                          className="flex items-center gap-1.5 w-full px-3 py-1.5 text-xs text-amber-400/70 hover:text-amber-300 bg-dark-300/40 border border-white/5 rounded-lg transition-colors">
                          <Eye className="w-3 h-3" />
                          {expandedMetadata === shot.id ? 'Ocultar metadatos CID' : 'Ver metadatos cinematográficos'}
                        </button>
                        {expandedMetadata === shot.id && (
                          <div className="mt-1 p-3 bg-dark-300/60 border border-amber-500/20 rounded-lg text-xs text-slate-300 space-y-1.5 max-h-64 overflow-y-auto">
                            {(() => {
                              const meta = shot.metadata_json as CinematicShotMetadata
                              return (
                                <>
                                  {meta.source_scope && <p><span className="text-amber-400">Scope:</span> {meta.source_scope}</p>}
                                  {meta.sequence_title && <p><span className="text-amber-400">Secuencia:</span> {meta.sequence_title}</p>}
                                  {meta.shot_plan_reason && <p><span className="text-amber-400">Razón:</span> {meta.shot_plan_reason}</p>}
                                  {meta.director_lens_id && <p><span className="text-amber-400">Lente:</span> {meta.director_lens_id}</p>}
                                  {meta.cinematic_intent_id && <p><span className="text-amber-400">Intent ID:</span> {meta.cinematic_intent_id}</p>}
                                  {meta.shot_editorial_purpose && (
                                    <>
                                      <p><span className="text-amber-400">Propósito:</span> {String((meta.shot_editorial_purpose as Record<string, unknown>).purpose || '')}</p>
                                      <p><span className="text-amber-400">Corte:</span> {String((meta.shot_editorial_purpose as Record<string, unknown>).cut_reason || '')}</p>
                                    </>
                                  )}
                                  {meta.montage_intent && (
                                    <p><span className="text-amber-400">Montaje:</span> {String((meta.montage_intent as Record<string, unknown>).editorial_function || '')}</p>
                                  )}
                                  {meta.directorial_intent && (
                                    <p><span className="text-amber-400">Dirección:</span> {String((meta.directorial_intent as Record<string, unknown>).mise_en_scene || '').substring(0, 120)}</p>
                                  )}
                                  {meta.validation && (
                                    <p className={Boolean((meta.validation as Record<string, unknown>).is_valid) ? 'text-green-400' : 'text-red-400'}>
                                      Validación: {Boolean((meta.validation as Record<string, unknown>).is_valid) ? 'Válido' : 'Inválido'} (score: {String((meta.validation as Record<string, unknown>).score)})
                                    </p>
                                  )}
                                  {meta.script_visual_alignment && (
                                    <p><span className="text-cyan-400">Alignment:</span> {String((meta.script_visual_alignment as Record<string, unknown>).alignment_score || '')}</p>
                                  )}
                                </>
                              )
                            })()}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </>
        )}

        {error && (
          <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 shrink-0" /> {error}
          </div>
        )}

        <AssetPickerModal isOpen={pickerOpen} projectId={projectId || ''}
          currentAssetId={shots.find((s) => s.id === selectedShotId)?.asset_id}
          onSelect={handleSelectAsset}
          onClose={() => { setPickerOpen(false); setSelectedShotId(null) }} />
      </div>
    </div>
  )
}
