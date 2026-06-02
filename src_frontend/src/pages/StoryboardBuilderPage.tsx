import { useState, useEffect, useCallback, useMemo, useRef } from 'react'
import { useParams } from 'react-router-dom'
import { Download, ExternalLink, Plus, Save, Loader2, ArrowLeft, Film, RefreshCw, Eye, FileText, ListChecks, Sparkles, AlertTriangle, MessageSquare, Check, Upload, X, Users, Wrench, Clock, Image, CheckCircle2 } from 'lucide-react'
import { storyboardApi } from '@/api/storyboard'
import { AuthenticatedStoryboardShotImage } from '@/components/storyboard/AuthenticatedStoryboardShotImage'
import { ShotCard } from '@/components/storyboard/ShotCard'
import { AssetPickerModal } from '@/components/storyboard/AssetPickerModal'
import { StoryboardSequenceSelectorModal } from '@/components/storyboard/StoryboardSequenceSelectorModal'
import type { StoryboardSelectionValue } from '@/components/storyboard/StoryboardSequenceSelectorModal'
import DirectorFeedbackPanel from '@/components/storyboard/DirectorFeedbackPanel'
import { StoryboardSheetExportPanel } from '@/components/storyboard/StoryboardSheetExportPanel'
import { StoryboardTracePanel } from '@/components/storyboard/StoryboardTracePanel'
import { ActionProgressPanel } from '@/components/ActionProgressPanel'
import type { ActionProgressState } from '@/components/ActionProgressPanel'
import type {
  CinematicShotMetadata,
  DirtyShot,
  FullScriptAnalysisResult,
  ScriptUploadResult,
  SequenceStoryboardPlan,
  StoryboardAutoExportItem,
  StoryboardCreditEstimate,
  StoryboardGeneratePayload,
  StoryboardSceneCandidate,
  StoryboardSelectionMode,
  StoryboardSequence,
  StoryboardShot,
} from '@/types/storyboard'
import { resolveShotRenderState, hasActiveRenderShots } from '@/types/storyboard'
import { getStoryboardShotDisplayText, getStoryboardUiLocale } from '@/utils/storyboardText'
import { deriveCharacterBreakdown } from '@/utils/characterBreakdown'
import { CharacterBreakdownPanel } from '@/components/storyboard/CharacterBreakdownPanel'
import { CharacterBiblePanel } from '@/components/storyboard/CharacterBiblePanel'
import { useLanguage } from '@/i18n'

function toDirtyShot(shot: StoryboardShot): DirtyShot {
  return { ...shot, isDirty: false }
}

function extractSequenceNumber(value?: string | null): number | null {
  if (!value) return null
  const trimmed = value.trim()
  if (!trimmed) return null
  if (/^\d+$/.test(trimmed)) return Number(trimmed)
  const match = trimmed.match(/(?:seq|sequence|s)_?0*(\d+)$/i)
  return match ? Number(match[1]) : null
}

function resolveSequenceAlias(sequenceId: string, sequences: StoryboardSequence[]): StoryboardSequence | null {
  const direct = sequences.find((sequence) => sequence.sequence_id === sequenceId)
  if (direct) return direct
  const number = extractSequenceNumber(sequenceId)
  if (number == null) return null
  return sequences.find((sequence) => sequence.sequence_number === number) || null
}

function dedupeList(items: Array<string | null | undefined> = []): string[] {
  const seen = new Set<string>()
  return items.filter((item): item is string => {
    const key = item?.trim().toLowerCase()
    if (!key || seen.has(key)) return false
    seen.add(key)
    return true
  })
}

function getShotSequenceLabel(shot: StoryboardShot): string | null {
  const metadata = (shot.metadata_json || {}) as Record<string, unknown>
  const label = metadata.sequence_label || metadata.sequence_title || metadata.sequence_number || shot.sequence_id
  if (label == null || label === '') return null
  return String(label)
}

function shouldDisplayShotImage(shot: StoryboardShot): boolean {
  const st = resolveShotRenderState(shot)
  return shot.has_image === true && st.state !== 'rendering'
}


export default function StoryboardBuilderPage() {
  const { t } = useLanguage()
  const { projectId } = useParams<{ projectId: string }>()
  const storyboardLocale = getStoryboardUiLocale()
  const [shots, setShots] = useState<DirtyShot[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [isGenerating, setIsGenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [pickerOpen, setPickerOpen] = useState(false)
  const [selectedShotId, setSelectedShotId] = useState<string | null>(null)
  const [sequences, setSequences] = useState<StoryboardSequence[]>([])
  const [selectedMode, setSelectedMode] = useState<StoryboardSelectionMode>('FULL_SCRIPT')
  const [selectedSequenceId, setSelectedSequenceId] = useState<string>('')
  const [sequenceSelectorOpen, setSequenceSelectorOpen] = useState(false)
  const [sequenceSelectorError, setSequenceSelectorError] = useState<string | null>(null)
  const [stylePreset, setStylePreset] = useState('hand_drawn_storyboard')
  const [shotsPerScene] = useState(3)
  const [directorLensId] = useState<string>('')
  const [montageProfileId] = useState<string>('')
  const [useCinematicIntelligence] = useState(false)
  const [useMontageIntelligence] = useState(false)
  const [validatePrompts] = useState(false)
  const [expandedMetadata, setExpandedMetadata] = useState<string | null>(null)
  const [expandedFeedback, setExpandedFeedback] = useState<string | null>(null)

  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [isPlanningSequence, setIsPlanningSequence] = useState(false)
  const [analysisResult, setAnalysisResult] = useState<FullScriptAnalysisResult | null>(null)
  const [shotPlan, setShotPlan] = useState<SequenceStoryboardPlan | null>(null)
  const [activeTab, setActiveTab] = useState<'analyze' | 'sequences' | 'characters' | 'shots'>('analyze')
  const [regenerationProgress, setRegenerationProgress] = useState<ActionProgressState | null>(null)
  const [cinematicViewMode, setCinematicViewMode] = useState<'filmstrip' | 'contact_sheet'>('filmstrip')

  const scriptFileInputRef = useRef<HTMLInputElement | null>(null)
  const [selectedScriptFile, setSelectedScriptFile] = useState<File | null>(null)
  const [isUploadingScript, setIsUploadingScript] = useState(false)
  const [scriptUploadResult, setScriptUploadResult] = useState<ScriptUploadResult | null>(null)
  const [scriptUploadError, setScriptUploadError] = useState<string | null>(null)
  const [creditEstimate, setCreditEstimate] = useState<StoryboardCreditEstimate | null>(null)
  const [isEstimatingCredits, setIsEstimatingCredits] = useState(false)
  const [showCreditModal, setShowCreditModal] = useState(false)
  const [pendingGenerateAction, setPendingGenerateAction] = useState<(() => Promise<void>) | null>(null)
  const [autoExportSheet, setAutoExportSheet] = useState(true)
  const [renderImagesOnComplete, setRenderImagesOnComplete] = useState(false)
  const [autoExportResponse, setAutoExportResponse] = useState<StoryboardAutoExportItem[] | null>(null)
  const [sortBy, setSortBy] = useState<'number' | 'location' | 'characters' | 'status'>('number')
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc')
  const [groupBy, setGroupBy] = useState<'none' | 'sequence' | 'location' | 'character' | 'int_ext' | 'day_night'>('none')
  const [characterFilter, setCharacterFilter] = useState<string | null>(null)
  const [isRepairing, setIsRepairing] = useState(false)
  const [repairResult, setRepairResult] = useState<string | null>(null)
  const [isPollingRenderState, setIsPollingRenderState] = useState(false)

  const fetchSequences = useCallback(async () => {
    if (!projectId) return
    try {
      const data = await storyboardApi.listSequences(projectId)
      setSequences(data)
    } catch (err) {
      console.error(err)
    }
  }, [projectId])

  const fetchShots = useCallback(async (options?: { silent?: boolean }) => {
    if (!projectId) return
    const silent = options?.silent === true
    if (!silent) setIsLoading(true)
    setError(null)
    try {
      const data = await storyboardApi.listShots(projectId)
      setShots(data.map(toDirtyShot))
    } catch (err) {
      setError('Failed to load storyboard shots')
      console.error(err)
    } finally {
      if (!silent) setIsLoading(false)
    }
  }, [projectId])

  useEffect(() => {
    fetchShots()
    fetchSequences()
  }, [fetchShots, fetchSequences])

  const currentSequence = useMemo(
    () => resolveSequenceAlias(selectedSequenceId, sequences),
    [sequences, selectedSequenceId]
  )

  const selectorScenes = useMemo<StoryboardSceneCandidate[]>(() => {
    const byScene = new Map<number, StoryboardSceneCandidate>()

    for (const sequence of sequences) {
      for (const sceneNumber of sequence.included_scenes || []) {
        if (!byScene.has(sceneNumber)) {
          byScene.set(sceneNumber, {
            scene_number: sceneNumber,
            scene_heading: `${sequence.title || `Secuencia ${sequence.sequence_number}`}`,
            sequence_id: sequence.sequence_id,
            sequence_title: sequence.title,
            storyboard_status: sequence.storyboard_status === 'generated' ? 'generated' : 'pending',
            source: 'options',
          })
        }
      }
    }

    for (const shot of shots) {
      const sceneNumber = Number(shot.scene_number || shot.sequence_order || 0)
      if (!sceneNumber) continue
      const current = byScene.get(sceneNumber)
      byScene.set(sceneNumber, {
        scene_number: sceneNumber,
        scene_heading: current?.scene_heading || shot.scene_heading || getShotSequenceLabel(shot) || `Secuencia ${shot.sequence_id || sceneNumber}`,
        narrative_text: current?.narrative_text || shot.narrative_text,
        sequence_id: current?.sequence_id || shot.sequence_id,
        sequence_title: current?.sequence_title || getShotSequenceLabel(shot),
        storyboard_status: shot.asset_id ? 'generated' : (shot.has_image === true ? 'generated' : (current?.storyboard_status ?? 'without_image')),
        asset_id: shot.asset_id || null,
        thumbnail_url: shot.thumbnail_url || null,
        preview_url: shot.preview_url || null,
        asset_file_name: shot.asset_file_name || null,
        source: current?.source || 'parsed',
      })
    }

    return Array.from(byScene.values()).sort((a, b) => a.scene_number - b.scene_number)
  }, [sequences, shots])

  const filteredShots = useMemo(() => {
    if (selectedSequenceId) {
      return shots.filter((shot) => shot.sequence_id === selectedSequenceId)
    }
    return shots
  }, [shots, selectedSequenceId])

  const sequenceCharacters = useMemo(
    () => dedupeList(sequences.flatMap((sequence) => sequence.characters || [])),
    [sequences]
  )

  const orderedCinematicShots = useMemo(() => {
    let safe = [...filteredShots]
    if (characterFilter) {
      const q = characterFilter.toLowerCase()
      safe = safe.filter((shot) => {
        const meta = shot.metadata_json || {}
        const chars = meta.characters as string[] | undefined
        return chars?.some((c: string) => c.toLowerCase().includes(q))
      })
    }
    safe.sort((a, b) => {
      const dir = sortDirection === 'asc' ? 1 : -1
      if (sortBy === 'number') {
        const seqA = Number(a.sequence_order || 0)
        const seqB = Number(b.sequence_order || 0)
        if (seqA !== seqB) return (seqA - seqB) * dir
      }
      if (sortBy === 'location') {
        const locA = (a.metadata_json as Record<string, string> | undefined)?.location || a.scene_heading || ''
        const locB = (b.metadata_json as Record<string, string> | undefined)?.location || b.scene_heading || ''
        const cmp = locA.localeCompare(locB)
        if (cmp !== 0) return cmp * dir
      }
      if (sortBy === 'characters') {
        const charsA = ((a.metadata_json as Record<string, string[]> | undefined)?.characters || []).join(', ')
        const charsB = ((b.metadata_json as Record<string, string[]> | undefined)?.characters || []).join(', ')
        const cmp = charsA.localeCompare(charsB)
        if (cmp !== 0) return cmp * dir
      }
      if (sortBy === 'status') {
        const statusA = a.render_status || 'no_asset'
        const statusB = b.render_status || 'no_asset'
        const cmp = statusA.localeCompare(statusB)
        if (cmp !== 0) return cmp * dir
      }
      const sequenceA = (a.sequence_id || '').toLowerCase()
      const sequenceB = (b.sequence_id || '').toLowerCase()
      if (sequenceA < sequenceB) return -1
      if (sequenceA > sequenceB) return 1
      const orderA = Number(a.sequence_order || 0)
      const orderB = Number(b.sequence_order || 0)
      if (orderA !== orderB) return orderA - orderB
      const sceneA = Number(a.scene_number || 0)
      const sceneB = Number(b.scene_number || 0)
      if (sceneA !== sceneB) return sceneA - sceneB
      return a.id.localeCompare(b.id)
    })
    return safe
  }, [filteredShots, sortBy, sortDirection, characterFilter])

  const hasPendingRenderShots = useMemo(
    () => hasActiveRenderShots(shots),
    [shots]
  )

  useEffect(() => {
    if (!projectId || !hasPendingRenderShots) {
      setIsPollingRenderState(false)
      return
    }

    setIsPollingRenderState(true)
    const intervalId = window.setInterval(() => {
      void fetchShots({ silent: true })
    }, 4000)

    return () => {
      window.clearInterval(intervalId)
      setIsPollingRenderState(false)
    }
  }, [fetchShots, hasPendingRenderShots, projectId])

  const handleScriptFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] || null
    if (!file) return
    const ext = file.name.split('.').pop()?.toLowerCase()
    if (ext === 'doc') {
      setScriptUploadError(t('internal.storyboardBuilder.uploadResult.unsupportedDoc'))
      setSelectedScriptFile(null)
      event.target.value = ''
      return
    }
    setScriptUploadError(null)
    setScriptUploadResult(null)
    setSelectedScriptFile(file)
  }

  const handleUploadScript = async () => {
    if (!projectId || !selectedScriptFile) return
    setIsUploadingScript(true)
    setScriptUploadError(null)
    setScriptUploadResult(null)
    try {
      const result = await storyboardApi.uploadProjectScript(projectId, selectedScriptFile)
      setScriptUploadResult(result)
    } catch (err: any) {
      setScriptUploadError(err?.response?.data?.detail || err?.message || 'Error al subir el guion')
    } finally {
      setIsUploadingScript(false)
    }
  }

  const handleGenerateWithEstimate = async (generateFn: () => Promise<void>) => {
    if (!projectId) return
    setError(null)
    setIsEstimatingCredits(true)
    try {
      const estimate = await storyboardApi.estimateStoryboardCredits(projectId, {})
      setCreditEstimate(estimate)
      setPendingGenerateAction(() => generateFn)
      setShowCreditModal(true)
    } catch (err: any) {
      // If estimation endpoint is unavailable, proceed directly
      console.warn('Credit estimation unavailable, proceeding directly:', err)
      await generateFn()
    } finally {
      setIsEstimatingCredits(false)
    }
  }

  const handleConfirmGenerate = async () => {
    setShowCreditModal(false)
    setCreditEstimate(null)
    if (pendingGenerateAction) {
      await pendingGenerateAction()
      setPendingGenerateAction(null)
    }
  }

  const handleCancelGenerate = () => {
    setShowCreditModal(false)
    setCreditEstimate(null)
    setPendingGenerateAction(null)
  }

  const handleAnalyzeFullScript = async () => {
    if (!projectId) return
    setIsAnalyzing(true)
    setError(null)
    setAnalysisResult(null)
    setShotPlan(null)
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

  const handleGenerateSequence = async (sequenceId: string) => {
    if (!projectId) return
    setIsGenerating(true)
    setError(null)
    try {
      const canonicalSequence = resolveSequenceAlias(sequenceId, sequences)
      const requestedSequenceId = canonicalSequence?.sequence_id || sequenceId
      const response = await storyboardApi.generateBySequence(projectId, requestedSequenceId, {
        style_preset: stylePreset,
        shots_per_scene: shotsPerScene,
        overwrite: true,
        shots_per_sequence_mode: 'auto_cinematic',
        render: renderImagesOnComplete,
      })
      const resolvedResponseSequence = response.sequence_id
        ? resolveSequenceAlias(response.sequence_id, sequences)?.sequence_id || response.sequence_id
        : requestedSequenceId
      setSelectedSequenceId(resolvedResponseSequence)
      await Promise.all([fetchShots(), fetchSequences()])
      setActiveTab('shots')
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Error generating sequence')
    } finally {
      setIsGenerating(false)
    }
  }

  const handlePlanSequenceFromList = async (sequenceId = selectedSequenceId) => {
    if (!projectId || !sequenceId) {
      setSequenceSelectorError('Selecciona una secuencia antes de planificar el storyboard.')
      setSequenceSelectorOpen(true)
      return
    }

    const canonicalSequence = resolveSequenceAlias(sequenceId, sequences)
    const requestedSequenceId = canonicalSequence?.sequence_id || sequenceId

    setIsPlanningSequence(true)
    setError(null)
    setSequenceSelectorError(null)
    try {
      const plan = await storyboardApi.planSequence(projectId, requestedSequenceId)
      setShotPlan(plan)
      setSelectedSequenceId(plan.sequence_id || requestedSequenceId)
      setSelectedMode('SEQUENCE')
      setActiveTab('sequences')
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || 'Error planificando la secuencia')
    } finally {
      setIsPlanningSequence(false)
    }
  }

  const handleGenerateSelection = async (selection: StoryboardSelectionValue) => {
    if (!projectId) return
    setIsGenerating(true)
    setError(null)
    setRegenerationProgress(null)
    setAutoExportResponse(null)
    try {
      const canonicalSequence = selection.sequenceId
        ? resolveSequenceAlias(selection.sequenceId, sequences)
        : null
      const payload: StoryboardGeneratePayload = {
        mode: selection.mode,
        generation_mode: selection.mode,
        sequence_id: selection.mode === 'SEQUENCE' ? (canonicalSequence?.sequence_id || selection.sequenceId || undefined) : undefined,
        sequence_ids: selection.sequenceIds,
        scene_start: selection.sceneStart ?? undefined,
        scene_end: selection.sceneEnd ?? undefined,
        scene_numbers: selection.sceneNumbers,
        style_preset: stylePreset,
        visual_mode: stylePreset,
        shots_per_scene: shotsPerScene,
        overwrite: selection.overwrite,
        director_lens_id: useCinematicIntelligence ? (directorLensId || undefined) : undefined,
        montage_profile_id: useMontageIntelligence ? (montageProfileId || undefined) : undefined,
        use_cinematic_intelligence: useCinematicIntelligence,
        use_montage_intelligence: useMontageIntelligence,
        validate_prompts: validatePrompts,
        render: selection.render,
        auto_export_sheet: autoExportSheet,
        auto_export_formats: ['png', 'pdf'],
      }
      const job = await storyboardApi.generate(projectId, payload)
      if (job.sequence_id) {
        setSelectedSequenceId(resolveSequenceAlias(job.sequence_id, sequences)?.sequence_id || job.sequence_id)
      } else if (selection.mode === 'SEQUENCE' && selection.sequenceId) {
        setSelectedSequenceId(canonicalSequence?.sequence_id || selection.sequenceId)
      }
      setSelectedMode(selection.mode)
      if (job.auto_exports && job.auto_exports.length > 0) {
        setAutoExportResponse(job.auto_exports)
      }
      await Promise.all([fetchShots(), fetchSequences()])
      setActiveTab('shots')
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || 'Error generating storyboard')
    } finally {
      setIsGenerating(false)
    }
  }

  const handleConfirmSequenceSelection = (selection: StoryboardSelectionValue) => {
    if (selection.mode === 'SEQUENCE' && !selection.sequenceId) {
      setSequenceSelectorError('Selecciona una secuencia antes de generar el storyboard.')
      return
    }

    const canonicalSequence = selection.sequenceId ? resolveSequenceAlias(selection.sequenceId, sequences) : null
    setSequenceSelectorOpen(false)
    setSequenceSelectorError(null)
    setSelectedMode(selection.mode)
    if (selection.mode === 'SEQUENCE' && selection.sequenceId) {
      setSelectedSequenceId(canonicalSequence?.sequence_id || selection.sequenceId)
    }
    void handleGenerateWithEstimate(() => handleGenerateSelection(selection))
  }

  const handleGenerate = async (regenerateSequence = false) => {
    if (!projectId) return
    setIsGenerating(true)
    setError(null)
    setRegenerationProgress(null)
    setAutoExportResponse(null)
    try {
      if (regenerateSequence && selectedSequenceId) {
        setRegenerationProgress({
          title: 'Regenerar storyboard',
          status: 'queued',
          percent: 0,
          label: 'Iniciando regeneración...',
        })
        const result = await storyboardApi.regenerateSequence(projectId, selectedSequenceId, {
          style_preset: stylePreset,
          shots_per_scene: shotsPerScene,
          render: renderImagesOnComplete,
        })
        setRegenerationProgress({
          title: 'Regenerar storyboard',
          status: 'processing',
          percent: 50,
          label: `Generando storyboard — ${result.total_shots} planos en ${result.total_scenes} escenas`,
          helperText: (result.render_jobs ?? []).length > 0
            ? `${(result.render_jobs ?? []).length} render(s) encolados`
            : 'Estructura generada sin renders',
          jobId: result.job_id,
        })
        await Promise.all([fetchShots(), fetchSequences()])
        setRegenerationProgress({
          title: 'Regenerar storyboard',
          status: 'completed',
          percent: 100,
          label: 'Storyboard regenerado correctamente',
          helperText: result.total_shots > 0
            ? `${result.total_scenes} escenas, ${result.total_shots} planos generados. Assets: ${(result.generated_assets ?? []).length > 0 ? (result.generated_assets ?? []).join(', ') : 'solo estructura'}`
            : 'Storyboard regenerado',
          jobId: result.job_id,
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
          render: renderImagesOnComplete,
          auto_export_sheet: autoExportSheet,
          auto_export_formats: ['png', 'pdf'],
        }
        const job = await storyboardApi.generate(projectId, payload)
        if (job.auto_exports && job.auto_exports.length > 0) {
          setAutoExportResponse(job.auto_exports)
        }
        await Promise.all([fetchShots(), fetchSequences()])
      }
    } catch (err: any) {
      console.error(err)
      const msg = err?.response?.data?.detail || 'Error generating storyboard'
      setError(msg)
      setRegenerationProgress((current) =>
        current
          ? { ...current, status: 'failed', errorMessage: msg }
          : null
      )
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

  const handleRepairAssets = async () => {
    if (!projectId) return
    setIsRepairing(true)
    setRepairResult(null)
    try {
      const { default: api } = await import('@/api/client')
      const { data } = await api.post(`/projects/${projectId}/storyboard/repair-assets`)
      setRepairResult(
        `Reparados: ${data.repaired_count} | Omitidos: ${data.skipped_count} | Sin match: ${data.not_found_count}`
      )
      await fetchShots()
    } catch (err: any) {
      setRepairResult('Error: ' + (err?.response?.data?.detail || err.message))
    } finally {
      setIsRepairing(false)
    }
  }

  const dirtyCount = shots.filter((s) => s.isDirty).length

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="flex items-center gap-3 text-amber-400">
          <Loader2 className="w-6 h-6 animate-spin" />
          <span>{t('internal.storyboardBuilder.loading')}</span>
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
                {t('internal.storyboardBuilder.title')}
              </h1>
              <p className="text-gray-400 text-sm mt-1">
                {filteredShots.length} shot{filteredShots.length !== 1 ? 's' : ''}
                {dirtyCount > 0 && <span className="text-amber-400 ml-2">• {dirtyCount} {t('internal.storyboardBuilder.unsaved')}</span>}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 rounded-lg border border-white/10 bg-white/5 px-3 py-2">
              <label htmlFor="storyboard-style" className="text-xs text-slate-300">{t('internal.storyboardBuilder.styleLabel')}</label>
              <select
                id="storyboard-style"
                value={stylePreset}
                onChange={(event) => setStylePreset(event.target.value)}
                className="bg-transparent text-sm text-white outline-none"
              >
                <option value="hand_drawn_storyboard">{t('internal.storyboardBuilder.stylePresets.handDrawnStoryboard')}</option>
                <option value="rough_pencil_storyboard">{t('internal.storyboardBuilder.stylePresets.roughPencilStoryboard')}</option>
                <option value="ink_storyboard">{t('internal.storyboardBuilder.stylePresets.inkStoryboard')}</option>
                <option value="charcoal_storyboard">{t('internal.storyboardBuilder.stylePresets.charcoalStoryboard')}</option>
                <option value="graphic_novel_storyboard">{t('internal.storyboardBuilder.stylePresets.graphicNovelStoryboard')}</option>
                <option value="cinematic_realistic">{t('internal.storyboardBuilder.stylePresets.cinematicRealistic')}</option>
              </select>
            </div>
            <button onClick={() => { fetchShots(); fetchSequences() }}
              className="flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-colors">
              <RefreshCw className="w-4 h-4" /> {t('internal.storyboardBuilder.refresh')}
            </button>
            <button onClick={handleAddShot} disabled={isSaving}
              className="flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-colors disabled:opacity-50">
              <Plus className="w-4 h-4" /> {t('internal.storyboardBuilder.addShot')}
            </button>
            <button onClick={handleSave} disabled={isSaving || dirtyCount === 0}
              className="flex items-center gap-2 px-4 py-2 bg-amber-500 hover:bg-amber-400 text-black rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
              {isSaving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
              {t('internal.storyboardBuilder.saveStoryboard')}
            </button>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex gap-1 border-b border-white/10 pb-1">
          {[
            { id: 'analyze' as const, label: t('internal.storyboardBuilder.tabs.analyze'), icon: FileText },
            { id: 'sequences' as const, label: t('internal.storyboardBuilder.tabs.sequences'), icon: ListChecks },
            { id: 'characters' as const, label: t('internal.storyboardBuilder.tabs.characters'), icon: Users },
            { id: 'shots' as const, label: t('internal.storyboardBuilder.tabs.shots'), icon: Film },
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
            {/* Script Upload Section */}
            <section className="card bg-dark-200/80 border border-white/5 p-6 space-y-4">
              <h2 className="text-lg font-semibold text-white">{t('internal.storyboardBuilder.uploadScript')}</h2>
              <p className="text-sm text-slate-400">
                {t('internal.storyboardBuilder.uploadScriptHelp')}
              </p>
              <div className="flex items-center gap-3">
                <input
                  ref={scriptFileInputRef}
                  type="file"
                  accept=".pdf,.docx,.txt,.md"
                  onChange={handleScriptFileSelect}
                  className="hidden"
                />
                <button
                  onClick={() => scriptFileInputRef.current?.click()}
                  disabled={isUploadingScript}
                  className="flex items-center gap-2 px-4 py-2 text-sm border border-white/10 hover:border-white/20 rounded-xl transition-colors disabled:opacity-40"
                >
                  <Upload className="w-4 h-4" />
                  {isUploadingScript ? t('internal.projectDetail.uploading') : t('internal.storyboardBuilder.selectFile')}
                </button>
                {selectedScriptFile && (
                  <span className="text-sm text-slate-300 truncate max-w-[300px]">{selectedScriptFile.name}</span>
                )}
              </div>
              {selectedScriptFile && !scriptUploadResult && (
                <button onClick={handleUploadScript} disabled={isUploadingScript}
                  className="inline-flex items-center gap-2 px-6 py-2.5 bg-amber-500/20 border border-amber-500/30 rounded-xl text-amber-300 font-medium hover:bg-amber-500/30 transition-all disabled:opacity-40 text-sm">
                  {isUploadingScript ? <Loader2 className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
                  {isUploadingScript ? t('internal.storyboardBuilder.uploadingScript') : t('internal.storyboardBuilder.uploadScript')}
                </button>
              )}
              {scriptUploadResult && (
                <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-4 space-y-2">
                  <div className="flex items-center gap-2 text-emerald-400 text-sm font-medium">
                    <Check className="w-4 h-4" />
                    Guion subido correctamente
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                    <div>
                      <p className="text-xs text-slate-500">{t('internal.storyboardBuilder.uploadResult.format')}</p>
                      <p className="text-white font-medium">{scriptUploadResult.format}</p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-500">{t('internal.storyboardBuilder.uploadResult.words')}</p>
                      <p className="text-white font-medium">{scriptUploadResult.word_count.toLocaleString()}</p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-500">{t('internal.storyboardBuilder.uploadResult.characters')}</p>
                      <p className="text-white font-medium">{scriptUploadResult.character_count.toLocaleString()}</p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-500">{t('internal.storyboardBuilder.uploadResult.readyForAnalysis')}</p>
                      <p className={scriptUploadResult.ready_for_analysis ? 'text-emerald-400 font-medium' : 'text-amber-400 font-medium'}>
                        {scriptUploadResult.ready_for_analysis ? t('internal.storyboardBuilder.common.yes') : t('internal.storyboardBuilder.common.no')}
                      </p>
                    </div>
                  </div>
                </div>
              )}
              {scriptUploadError && (
                <div className="flex items-start gap-2 p-3 bg-red-500/10 border border-red-500/20 rounded-xl text-sm text-red-400">
                  <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
                  {scriptUploadError}
                </div>
              )}
            </section>

            <section className="card bg-dark-200/80 border border-white/5 p-6 space-y-4">
              <h2 className="text-lg font-semibold text-white">{t('internal.storyboardBuilder.fullScriptAnalysis')}</h2>
              <p className="text-sm text-slate-400">
                {t('internal.storyboardBuilder.fullScriptAnalysisHelp')}
              </p>
              <button onClick={handleAnalyzeFullScript} disabled={isAnalyzing}
                className="inline-flex items-center gap-2 px-6 py-3 bg-amber-500/20 border border-amber-500/30 rounded-xl text-amber-300 font-medium hover:bg-amber-500/30 transition-all disabled:opacity-40">
                {isAnalyzing ? <Loader2 className="w-5 h-5 animate-spin" /> : <FileText className="w-5 h-5" />}
                {isAnalyzing ? t('internal.storyboardBuilder.analyzingFullScript') : t('internal.storyboardBuilder.analyzeFullScript')}
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
                      <p className="text-xs text-slate-400">{t('internal.storyboardBuilder.analysis.logline')}</p>
                      <p className="text-sm text-white">{analysisResult.synopsis.logline || '—'}</p>
                    </div>
                    <div className="space-y-2">
                      <p className="text-xs text-slate-400">{t('internal.storyboardBuilder.analysis.premise')}</p>
                      <p className="text-sm text-white">{analysisResult.synopsis.premise || '—'}</p>
                    </div>
                    <div className="space-y-2">
                      <p className="text-xs text-slate-400">{t('internal.storyboardBuilder.analysis.theme')}</p>
                      <p className="text-sm text-white">{analysisResult.synopsis.theme || '—'}</p>
                    </div>
                    <div className="space-y-2">
                      <p className="text-xs text-slate-400">{t('internal.storyboardBuilder.analysis.genreTone')}</p>
                      <p className="text-sm text-white">{analysisResult.synopsis.genre || '—'} • {analysisResult.synopsis.tone || '—'}</p>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <p className="text-xs text-slate-400">{t('internal.storyboardBuilder.analysis.extendedSynopsis')}</p>
                    <p className="text-sm text-white">{analysisResult.synopsis.synopsis_extended || '—'}</p>
                  </div>
                  <div className="grid gap-3 md:grid-cols-2">
                    <div>
                      <p className="text-xs text-slate-400 mb-1">{t('internal.storyboardBuilder.analysis.mainCharacters')}</p>
                      <div className="flex flex-wrap gap-1">
                        {analysisResult.synopsis.main_characters.map((c, i) => (
                          <span key={i} className="px-2 py-0.5 text-xs bg-amber-400/10 text-amber-300 rounded-full">{c}</span>
                        ))}
                      </div>
                    </div>
                    <div>
                      <p className="text-xs text-slate-400 mb-1">{t('internal.storyboardBuilder.analysis.mainLocations')}</p>
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
                                <span className="px-1.5 py-0.5 text-[10px] font-medium bg-green-400/10 text-green-300 rounded">{t('internal.storyboardBuilder.analysis.recommended')}</span>
                              )}
                            </div>
                            <p className="text-xs text-slate-400 mb-2">{entry.summary}</p>
                            <div className="flex flex-wrap gap-1 mb-2">
                              {entry.location && (
                                <span className="px-1.5 py-0.5 text-[10px] bg-cyan-400/10 text-cyan-300 rounded">{entry.location}</span>
                              )}
                              {entry.characters.map((ch: string, i: number) => (
                                <span key={i} className="px-1.5 py-0.5 text-[10px] bg-amber-400/10 text-amber-300 rounded">{ch}</span>
                              ))}
                            </div>
                            <button onClick={() => {
                              setSelectedSequenceId(entry.sequence_id)
                              setActiveTab('shots')
                            }}
                              className="text-xs text-cyan-400 hover:text-cyan-300 transition-colors">
                              Ver plan de storyboard →
                            </button>
                          </div>
                          <div className="flex flex-col items-end gap-1">
                            <span className="text-[10px] text-slate-500">{entry.suggested_shot_count || 0} planos</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </section>
              </>
            )}

            {/* Template section */}
            <section className="card bg-dark-200/80 border border-white/5 p-6 space-y-4">
              <h2 className="text-lg font-semibold text-white">{t('internal.storyboardBuilder.selectSequence')}</h2>

              {/* Sequence cards grid */}
              <div className="grid gap-3">
                {sequences.map((seq) => (
                  <div key={seq.sequence_id}
                    onClick={() => setSelectedSequenceId(seq.sequence_id)}
                    className="rounded-xl border border-white/10 bg-[#0a1016] p-4 hover:border-amber-500/30 cursor-pointer transition-all">
                    <div className="flex items-center justify-between gap-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-xs font-bold text-amber-400">#{seq.sequence_number}</span>
                          <h4 className="text-sm font-semibold text-white">{seq.title}</h4>
                        </div>
                        <p className="text-xs text-slate-400 mb-2">{seq.summary || ''}</p>
                        <div className="flex flex-wrap gap-1 mb-2">
                          {seq.location && (
                            <span className="px-1.5 py-0.5 text-[10px] bg-cyan-400/10 text-cyan-300 rounded">{seq.location}</span>
                          )}
                          {seq.characters.map((ch: string, i: number) => (
                            <span key={i} className="px-1.5 py-0.5 text-[10px] bg-amber-400/10 text-amber-300 rounded">{ch}</span>
                          ))}
                        </div>
                      </div>
                      <div className="flex flex-col items-end gap-1">
                        <span className="text-[10px] text-slate-500">{seq.estimated_shots || 0} planos</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </section>

            {/* Shot plan */}
            {shotPlan && selectedSequenceId && (
              <section className="card bg-dark-200/80 border border-cyan-500/20 p-6 space-y-4">
                <h3 className="text-base font-semibold text-cyan-300 flex items-center gap-2">
                  <Eye className="w-4 h-4" /> Plan de storyboard: {shotPlan.sequence_title}
                </h3>
                {shotPlan.warnings && shotPlan.warnings.length > 0 && (
                  <div className="rounded-xl border border-amber-500/20 bg-amber-500/5 p-3 space-y-1">
                    <p className="text-xs font-medium text-amber-400">{t('internal.storyboardBuilder.analysis.warnings')}</p>
                    {shotPlan.warnings.map((w, i) => (
                      <p key={i} className="text-[11px] text-amber-300/70">{w}</p>
                    ))}
                  </div>
                )}
                <p className="text-xs text-slate-400">
                  <span className="text-cyan-400 font-medium">{shotPlan.shot_plan.length} planos</span> planificados
                </p>
                {shotPlan.continuity_plan.length > 0 && (
                  <p className="text-xs text-slate-500">{shotPlan.continuity_plan.join(' | ')}</p>
                )}
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
                  <button onClick={() => selectedSequenceId && handleGenerateWithEstimate(() => handleGenerateSequence(selectedSequenceId))}
                    disabled={isGenerating || isEstimatingCredits}
                    className="flex items-center gap-2 px-6 py-3 bg-amber-500/20 border border-amber-500/30 rounded-xl text-amber-300 font-medium hover:bg-amber-500/30 transition-all disabled:opacity-40">
                    {isGenerating || isEstimatingCredits ? <Loader2 className="w-5 h-5 animate-spin" /> : <Sparkles className="w-5 h-5" />}
                    {isGenerating ? t('internal.projectDetail.generating') : isEstimatingCredits ? t('internal.storyboardBuilder.credits.estimating') : t('internal.storyboardBuilder.generateSequenceStoryboard')}
                  </button>
                </div>
              </section>
            )}

            {/* Guard message when no sequence selected */}
            {sequences.length > 0 && !selectedSequenceId && (
              <div className="p-4 bg-amber-500/5 border border-amber-500/20 rounded-xl text-sm text-amber-300/80 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 shrink-0" />
                {t('internal.storyboardBuilder.selectSequenceFirst')}
              </div>
            )}
          </div>
        )}

        {/* TAB 2: Sequence selection */}
        {activeTab === 'sequences' && (
          <div className="space-y-6">
            <section className="card bg-dark-200/80 border border-white/5 p-6 space-y-5">
              <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                <div>
                  <h2 className="text-lg font-semibold text-white">{t('internal.storyboardBuilder.selectSequence')}</h2>
                  <p className="text-sm text-slate-400 mt-1">
                    {sequences.length} secuencias disponibles · {selectorScenes.length} escenas detectadas · {sequenceCharacters.length} personajes
                  </p>
                  {currentSequence && (
                    <p className="text-xs text-amber-300 mt-2">
                      Secuencia seleccionada: Secuencia {currentSequence.sequence_number} — {currentSequence.title}
                    </p>
                  )}
                </div>
                <div className="flex flex-wrap gap-2">
                  <button
                    type="button"
                    onClick={() => {
                      setSequenceSelectorError(null)
                      setSequenceSelectorOpen(true)
                    }}
                    className="inline-flex items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-sm font-medium text-white hover:bg-white/10"
                  >
                    <ListChecks className="w-4 h-4" />
                    {t('internal.storyboardBuilder.selectSequence')}
                  </button>
                  <button
                    type="button"
                    onClick={() => handlePlanSequenceFromList(selectedSequenceId)}
                    disabled={!selectedSequenceId || isPlanningSequence}
                    className="inline-flex items-center gap-2 rounded-xl border border-cyan-500/30 bg-cyan-500/10 px-4 py-2 text-sm font-medium text-cyan-300 hover:bg-cyan-500/20 disabled:opacity-40"
                  >
                    {isPlanningSequence ? <Loader2 className="w-4 h-4 animate-spin" /> : <Eye className="w-4 h-4" />}
                    {t('internal.storyboardBuilder.planStoryboard')}
                  </button>
                  <button
                    type="button"
                    onClick={() => selectedSequenceId && handleGenerateWithEstimate(() => handleGenerateSequence(selectedSequenceId))}
                    disabled={!selectedSequenceId || isGenerating || isEstimatingCredits}
                    className="inline-flex items-center gap-2 rounded-xl border border-amber-500/30 bg-amber-500/10 px-4 py-2 text-sm font-medium text-amber-300 hover:bg-amber-500/20 disabled:opacity-40"
                  >
                    {isGenerating || isEstimatingCredits ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
                    {t('internal.storyboardBuilder.generateSequenceStoryboard')}
                  </button>
                </div>
              </div>

              <label className="flex items-center gap-3 rounded-xl border border-cyan-500/20 bg-cyan-500/5 px-4 py-3 text-sm text-slate-200">
                <input
                  type="checkbox"
                  checked={renderImagesOnComplete}
                  onChange={(e) => setRenderImagesOnComplete(e.target.checked)}
                  className="w-4 h-4 rounded border-cyan-500/50 text-cyan-500 focus:ring-cyan-500/30"
                />
                <div>
                  <p className="font-medium text-white">{t('internal.storyboardBuilder.renderOnComplete')}</p>
                  <p className="text-xs text-slate-400">{t('internal.storyboardBuilder.renderOnCompleteHelp')}</p>
                </div>
              </label>

              {sequences.length === 0 ? (
                <div className="rounded-xl border border-amber-500/20 bg-amber-500/5 p-4 text-sm text-amber-200">
                  {t('internal.storyboardBuilder.noSequences')}
                </div>
              ) : (
                <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
                  {sequences.map((sequence) => {
                    const selected = selectedSequenceId === sequence.sequence_id
                    return (
                      <button
                        key={sequence.sequence_id}
                        type="button"
                        onClick={() => {
                          setSelectedSequenceId(sequence.sequence_id)
                          setSelectedMode('SEQUENCE')
                          setShotPlan(null)
                        }}
                        className={`rounded-2xl border p-4 text-left transition-colors ${selected ? 'border-amber-400/50 bg-amber-500/10' : 'border-white/10 bg-[#0a1016] hover:border-white/20'}`}
                      >
                        <div className="flex items-start justify-between gap-3">
                          <div>
                            <p className="text-xs font-bold uppercase tracking-[0.18em] text-amber-400">Secuencia {sequence.sequence_number}</p>
                            <h3 className="mt-1 text-sm font-semibold text-white">{sequence.title}</h3>
                          </div>
                          <span className="rounded-full bg-white/5 px-2 py-1 text-[10px] text-slate-300">{sequence.storyboard_status}</span>
                        </div>
                        <p className="mt-3 text-xs text-slate-400 line-clamp-3">{sequence.summary || 'Sin resumen disponible.'}</p>
                        <div className="mt-3 flex flex-wrap gap-1">
                          {sequence.location && <span className="rounded bg-cyan-400/10 px-1.5 py-0.5 text-[10px] text-cyan-300">{sequence.location}</span>}
                          {sequence.characters.slice(0, 5).map((character) => (
                            <span key={character} className="rounded bg-amber-400/10 px-1.5 py-0.5 text-[10px] text-amber-300">{character}</span>
                          ))}
                        </div>
                        <div className="mt-3 flex items-center justify-between text-[11px] text-slate-500">
                          <span>{sequence.included_scenes.length} escenas</span>
                          <span>{sequence.estimated_shots || 0} planos estimados</span>
                        </div>
                      </button>
                    )
                  })}
                </div>
              )}
            </section>

            {shotPlan && selectedSequenceId && (
              <section className="card bg-dark-200/80 border border-cyan-500/20 p-6 space-y-4">
                <h3 className="text-base font-semibold text-cyan-300 flex items-center gap-2">
                  <Eye className="w-4 h-4" /> Plan de storyboard: {shotPlan.sequence_title}
                </h3>
                <p className="text-xs text-slate-400">
                  <span className="text-cyan-400 font-medium">{shotPlan.shot_plan.length} planos</span> planificados para esta secuencia.
                </p>
                <div className="grid gap-2">
                  {shotPlan.shot_plan.map((shot) => (
                    <div key={shot.shot_number} className="rounded-xl border border-white/10 bg-[#0a1016] p-3">
                      <div className="flex items-center justify-between gap-3 mb-1">
                        <span className="text-xs font-bold text-cyan-400">Plano {shot.shot_number} · {shot.shot_type}</span>
                        <span className="text-[10px] text-slate-500">{shot.framing} · {shot.camera_angle}</span>
                      </div>
                      <p className="text-xs text-slate-300">{shot.action || shot.prompt_brief}</p>
                    </div>
                  ))}
                </div>
              </section>
            )}
          </div>
        )}

        {/* TAB Personajes */}
        {activeTab === 'characters' && (
          <div className="space-y-6">
            <section className="card bg-dark-200/80 border border-white/5 p-6">
              <h2 className="text-lg font-semibold text-white flex items-center gap-2">
                <Users className="w-4 h-4 text-cyan-400" />
                Personajes y desglose por secuencias
              </h2>
              <p className="text-sm text-slate-400 mt-1">
                {sequences.length > 0
                  ? `${deriveCharacterBreakdown(sequences).length} personajes detectados en ${sequences.length} secuencias`
                  : 'Analiza el guion completo para ver el desglose de personajes.'}
              </p>
            </section>
            {sequences.length > 0 ? (
              <div className="space-y-6">
                <CharacterBreakdownPanel
                  sequences={sequences}
                  onFilterByCharacter={(character) => {
                    setCharacterFilter(character)
                    setActiveTab('shots')
                  }}
                  onSelectSequencesByCharacter={(seqIds) => {
                    const found = sequences.find((s) => seqIds.includes(s.sequence_id))
                    if (found) {
                      setSelectedSequenceId(found.sequence_id)
                      setActiveTab('shots')
                    }
                  }}
                />
                {projectId && (
                  <CharacterBiblePanel
                    projectId={projectId}
                    suggestedCharacters={deriveCharacterBreakdown(sequences).map((entry) => entry.character)}
                  />
                )}
              </div>
            ) : (
              <div className="space-y-6">
                {projectId && <CharacterBiblePanel projectId={projectId} />}
                <div className="text-center py-10">
                  <p className="text-slate-400 mb-4">{t('internal.storyboardBuilder.noCharacterData')}</p>
                  <button onClick={handleAnalyzeFullScript} disabled={isAnalyzing}
                    className="inline-flex items-center gap-2 px-4 py-2 bg-amber-500/20 border border-amber-500/30 rounded-xl text-amber-300">
                    <FileText className="w-4 h-4" /> Analizar guion completo
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* TAB 3: Generated Shots */}
        {activeTab === 'shots' && (
          <>
            <section className="card bg-dark-200/80 border border-white/5 p-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="text-lg font-semibold text-white">{t('internal.storyboardBuilder.generatedShots')}</h2>
                  <p className="text-sm text-slate-400">{filteredShots.length} planos</p>
                </div>
                <div className="flex gap-2">
                  {selectedSequenceId && (
                    <button onClick={() => handleGenerate(true)} disabled={isGenerating}
                      className="flex items-center gap-2 px-4 py-2 text-sm bg-white/10 border border-white/20 text-white rounded-xl hover:bg-white/20 transition-all">
                      <RefreshCw className="w-4 h-4" /> {t('internal.storyboardBuilder.regenerateSequence')}
                    </button>
                  )}
                  <button
                    type="button"
                    onClick={handleRepairAssets}
                    disabled={isRepairing}
                    className="px-3 py-2 text-xs border border-cyan-500/30 bg-cyan-500/10 text-cyan-300 rounded-xl hover:bg-cyan-500/20 transition-all disabled:opacity-50 inline-flex items-center gap-1"
                  >
                    <Wrench className="w-3 h-3" />
                    {isRepairing ? 'Reparando...' : t('internal.storyboardBuilder.repairThumbnails')}
                  </button>
                  <select className="input text-sm w-auto" value={selectedSequenceId}
                    onChange={(e) => setSelectedSequenceId(e.target.value)}>
                    <option value="">{t('internal.storyboardBuilder.allSequences')}</option>
                    {sequences.map((s) => (
                      <option key={s.sequence_id} value={s.sequence_id}>Secuencia {s.sequence_number} — {s.title}</option>
                    ))}
                  </select>
                </div>
              </div>
              <div className="flex flex-wrap items-center gap-3 mb-4">
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value as typeof sortBy)}
                  className="rounded-xl border border-white/10 bg-dark-300/70 px-3 py-2 text-xs text-white outline-none"
                >
                  <option value="number">Número secuencia</option>
                  <option value="location">Localización</option>
                  <option value="characters">Personajes</option>
                  <option value="status">Estado</option>
                </select>
                <button
                  onClick={() => setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')}
                  className="px-3 py-2 text-xs border border-white/10 rounded-xl hover:bg-white/5 text-slate-300 transition-colors"
                >
                  {sortDirection === 'asc' ? '↑' : '↓'}
                </button>
                <select
                  value={groupBy}
                  onChange={(e) => setGroupBy(e.target.value as typeof groupBy)}
                  className="rounded-xl border border-white/10 bg-dark-300/70 px-3 py-2 text-xs text-white outline-none"
                >
                  <option value="none">Sin agrupar</option>
                  <option value="sequence">Por secuencia</option>
                  <option value="location">Por localización</option>
                  <option value="character">Por personaje</option>
                </select>
              </div>
              {repairResult && (
                <div className="px-4 py-2 text-xs bg-cyan-500/10 border border-cyan-500/20 rounded-xl text-cyan-300">
                  {repairResult}
                </div>
              )}
              {regenerationProgress && (
                <ActionProgressPanel
                  progress={regenerationProgress}
                  onRetry={() => handleGenerate(true)}
                  retryLabel="Reintentar regeneración"
                />
              )}
              {isPollingRenderState && (
                <div className="px-4 py-2 text-xs bg-amber-500/10 border border-amber-500/20 rounded-xl text-amber-300 inline-flex items-center gap-2">
                  <Loader2 className="w-3.5 h-3.5 animate-spin" /> Actualizando estado de renders...
                </div>
              )}
            </section>

            <section className="rounded-xl border border-amber-500/20 bg-amber-500/5 p-4">
              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={autoExportSheet}
                  onChange={(e) => setAutoExportSheet(e.target.checked)}
                  className="w-4 h-4 rounded border-amber-500/50 text-amber-500 focus:ring-amber-500/30"
                />
                <div>
                  <p className="text-sm font-medium text-white">Crear también Storyboard Sheet PNG/PDF</p>
                  <p className="text-xs text-slate-400">
                    Al generar el storyboard se crearán automáticamente los sheets editoriales
                  </p>
                </div>
              </label>
            </section>

            {autoExportResponse && autoExportResponse.length > 0 && (
              <section className="rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-4 space-y-3">
                <p className="text-xs font-medium uppercase tracking-[0.18em] text-emerald-400">Storyboard Sheet generado</p>
                <div className="flex flex-wrap gap-3">
                  {autoExportResponse.map((item) => {
                    const extension = item.output_format === 'pdf' ? 'pdf' : 'png'
                    const handleOpen = () => {
                      if (item.artifact_url) {
                        storyboardApi.fetchArtifactBlob(item.artifact_url)
                          .then((blob) => {
                            const url = URL.createObjectURL(blob)
                            window.open(url, '_blank', 'noopener,noreferrer')
                            setTimeout(() => URL.revokeObjectURL(url), 60000)
                          })
                          .catch(() => {})
                      }
                    }
                    const handleDownload = () => {
                      if (item.artifact_url) {
                        storyboardApi.fetchArtifactBlob(item.artifact_url)
                          .then((blob) => {
                            const url = URL.createObjectURL(blob)
                            const anchor = document.createElement('a')
                            anchor.href = url
                            anchor.download = `storyboard_sheet_auto.${extension}`
                            anchor.click()
                            URL.revokeObjectURL(url)
                          })
                          .catch(() => {})
                      }
                    }
                    return (
                      <div key={item.output_format} className="flex items-center gap-3 rounded-xl border border-white/10 bg-white/5 px-4 py-3">
                        <span className="text-sm font-medium text-white uppercase">{item.output_format}</span>
                        <span className="text-xs text-slate-400">{item.frame_count} frames · {item.page_count} páginas</span>
                        {item.artifact_url && (
                          <>
                            <button type="button" onClick={handleOpen}
                              className="inline-flex items-center gap-1 rounded-lg border border-white/10 bg-white/5 px-3 py-1.5 text-xs font-medium text-white hover:bg-white/10">
                              <Download className="h-3.5 w-3.5" />
                              Abrir
                            </button>
                            <button type="button" onClick={handleDownload}
                              className="inline-flex items-center gap-1 rounded-lg border border-amber-500/30 bg-amber-500/10 px-3 py-1.5 text-xs font-medium text-amber-300 hover:bg-amber-500/20">
                              <ExternalLink className="h-3.5 w-3.5" />
                              Descargar
                            </button>
                          </>
                        )}
                      </div>
                    )
                  })}
                </div>
              </section>
            )}

            {projectId && <StoryboardSheetExportPanel projectId={projectId} />}

            {sequences.length > 0 && !selectedSequenceId && filteredShots.length === 0 && (
              <div className="p-4 bg-amber-500/5 border border-amber-500/20 rounded-xl text-sm text-amber-300/80 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 shrink-0" />
                {t('internal.storyboardBuilder.selectSequenceFirstFromTab')}
              </div>
            )}

            {filteredShots.length === 0 ? (
              <div className="text-center py-20">
                <Film className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                <h2 className="text-xl font-semibold text-white mb-2">{t('internal.storyboardBuilder.noShotsTitle')}</h2>
                <p className="text-gray-400 mb-6">{t('internal.storyboardBuilder.noShotsText')}</p>
              </div>
            ) : (
              <div className="space-y-6">
                <section className="card bg-dark-200/80 border border-white/5 p-4">
                  <div className="flex items-center justify-between gap-3 mb-4">
                    <h3 className="text-white font-semibold">Storyboard cinematográfico</h3>
                    <div className="flex gap-2 text-xs">
                      <button
                        onClick={() => setCinematicViewMode('filmstrip')}
                        className={`px-3 py-1.5 rounded-lg border ${cinematicViewMode === 'filmstrip' ? 'border-amber-400 text-amber-300 bg-amber-500/10' : 'border-white/10 text-slate-300 bg-white/5'}`}
                      >
                        Filmstrip horizontal
                      </button>
                      <button
                        onClick={() => setCinematicViewMode('contact_sheet')}
                        className={`px-3 py-1.5 rounded-lg border ${cinematicViewMode === 'contact_sheet' ? 'border-amber-400 text-amber-300 bg-amber-500/10' : 'border-white/10 text-slate-300 bg-white/5'}`}
                      >
                        Contact sheet grid
                      </button>
                    </div>
                  </div>

                  {cinematicViewMode === 'filmstrip' ? (
                    <div className="overflow-x-auto rounded-xl border border-white/10 bg-[#050505] p-3">
                      <div className="flex gap-3 min-w-max pb-2">
                        {orderedCinematicShots.map((shot) => {
                          const metadata = (shot.metadata_json || {}) as Record<string, unknown>
                          const validationScore = metadata.validation_score ?? (metadata.validation_result as Record<string, unknown> | undefined)?.overall_match_score
                          const displayText = getStoryboardShotDisplayText(shot, storyboardLocale)
                          const renderState = resolveShotRenderState(shot)
                          return (
                            <div key={`filmstrip-${shot.id}`} className={`w-56 rounded-lg border border-white/10 bg-black overflow-hidden ${renderState.pulse ? 'animate-pulse border-amber-500/30' : ''}`} title={shot.render_error || renderState.label}>
                              <div className="aspect-video bg-black/40 relative">
                                <div className="absolute top-2 left-2 z-10">
                                  <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-lg text-[10px] font-medium border ${renderState.color} border-current/20`}>
                                    {renderState.icon === 'check' && <CheckCircle2 className="w-3 h-3" />}
                                    {renderState.icon === 'clock' && <Clock className="w-3 h-3" />}
                                    {renderState.icon === 'alert' && <AlertTriangle className="w-3 h-3" />}
                                    {renderState.icon === 'image' && <Image className="w-3 h-3" />}
                                    {renderState.label}
                                  </span>
                                </div>
                                {shouldDisplayShotImage(shot) ? (
                                  <AuthenticatedStoryboardShotImage
                                    projectId={projectId || shot.project_id}
                                    shotId={shot.id}
                                    alt={shot.asset_file_name || `shot-${shot.sequence_order}`}
                                    className="w-full h-full object-cover"
                                    fallbackLabel="Sin miniatura"
                                  />
                                ) : (
                                  <div className="flex h-full w-full items-center justify-center text-xs text-slate-500 px-3 text-center">
                                    {renderState.state === 'rendering' ? 'Render encolado' : renderState.state === 'failed' ? 'Render fallido' : 'Sin asset asociado'}
                                  </div>
                                )}
                              </div>
                              <div className="p-2 space-y-1 text-xs text-slate-300 border-t border-white/10">
                                <p><span className="text-slate-500">Secuencia:</span> {getShotSequenceLabel(shot) || shot.sequence_id || 'n/a'}</p>
                                <p><span className="text-slate-500">Escena fuente:</span> {shot.scene_number ?? 'n/a'}</p>
                                <p><span className="text-slate-500">Plano:</span> {shot.sequence_order}</p>
                                <p><span className="text-slate-500">Render:</span> {shot.render_status || 'no_asset'}</p>
                                {shot.render_error && <p className="text-red-300/80">{shot.render_error}</p>}
                                <p className="text-slate-200 line-clamp-3">{displayText}</p>
                                <p><span className="text-slate-500">Validación:</span> {validationScore != null ? String(validationScore) : 'n/a'}</p>
                                <StoryboardTracePanel projectId={projectId || shot.project_id} shotId={shot.id} compact />
                              </div>
                            </div>
                          )
                        })}
                      </div>
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                      {orderedCinematicShots.map((shot) => {
                        const metadata = (shot.metadata_json || {}) as Record<string, unknown>
                        const validationScore = metadata.validation_score ?? (metadata.validation_result as Record<string, unknown> | undefined)?.overall_match_score
                        const displayText = getStoryboardShotDisplayText(shot, storyboardLocale)
                        const renderState = resolveShotRenderState(shot)
                        return (
                          <div key={`grid-${shot.id}`} className={`rounded-lg border border-white/10 bg-dark-300/60 overflow-hidden ${renderState.pulse ? 'animate-pulse border-amber-500/30' : ''}`} title={shot.render_error || renderState.label}>
                            <div className="aspect-video bg-black/30 relative">
                              <div className="absolute top-2 left-2 z-10">
                                <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-lg text-[10px] font-medium border ${renderState.color} border-current/20`}>
                                  {renderState.icon === 'check' && <CheckCircle2 className="w-3 h-3" />}
                                  {renderState.icon === 'clock' && <Clock className="w-3 h-3" />}
                                  {renderState.icon === 'alert' && <AlertTriangle className="w-3 h-3" />}
                                  {renderState.icon === 'image' && <Image className="w-3 h-3" />}
                                  {renderState.label}
                                </span>
                              </div>
                              {shouldDisplayShotImage(shot) ? (
                                <AuthenticatedStoryboardShotImage
                                  projectId={projectId || shot.project_id}
                                  shotId={shot.id}
                                  alt={shot.asset_file_name || `shot-${shot.sequence_order}`}
                                  className="w-full h-full object-cover"
                                  fallbackLabel="Sin miniatura"
                                />
                              ) : (
                                <div className="flex h-full w-full items-center justify-center text-xs text-slate-500 px-3 text-center">
                                  {renderState.state === 'rendering' ? 'Render encolado' : renderState.state === 'failed' ? 'Render fallido' : 'Sin asset asociado'}
                                </div>
                              )}
                            </div>
                            <div className="p-2 space-y-1 text-xs text-slate-300">
                              <p><span className="text-slate-500">Secuencia:</span> {getShotSequenceLabel(shot) || shot.sequence_id || 'n/a'}</p>
                              <p><span className="text-slate-500">Escena fuente:</span> {shot.scene_number ?? 'n/a'}</p>
                              <p><span className="text-slate-500">Plano:</span> {shot.sequence_order}</p>
                              <p><span className="text-slate-500">Render:</span> {shot.render_status || 'no_asset'}</p>
                              {shot.render_error && <p className="text-red-300/80">{shot.render_error}</p>}
                              <p className="text-slate-200 line-clamp-3">{displayText}</p>
                              <p><span className="text-slate-500">Validación:</span> {validationScore != null ? String(validationScore) : 'n/a'}</p>
                              <StoryboardTracePanel projectId={projectId || shot.project_id} shotId={shot.id} compact />
                            </div>
                          </div>
                        )
                      })}
                    </div>
                  )}
                </section>

                <details>
                  <summary className="cursor-pointer text-sm text-slate-300 mb-3">Detalles de planos</summary>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                  {filteredShots.map((shot) => (
                    <div key={shot.id} className="space-y-1">
                      <ShotCard shot={shot} onUpdate={handleUpdateShot} onDelete={handleDeleteShot}
                        onOpenPicker={handleOpenPicker} isSaving={isSaving} />
                      <div className="flex gap-1">
                        <button onClick={() => setExpandedFeedback(expandedFeedback === shot.id ? null : shot.id)}
                          className="flex items-center gap-1.5 flex-1 px-3 py-1.5 text-xs text-cyan-400/70 hover:text-cyan-300 bg-dark-300/40 border border-white/5 rounded-lg transition-colors">
                          <MessageSquare className="w-3 h-3" />
                          {expandedFeedback === shot.id ? 'Cerrar notas' : 'Notas del director'}
                        </button>
                        {shot.metadata_json && (
                          <button onClick={() => setExpandedMetadata(expandedMetadata === shot.id ? null : shot.id)}
                            className="flex items-center gap-1.5 px-3 py-1.5 text-xs text-amber-400/70 hover:text-amber-300 bg-dark-300/40 border border-white/5 rounded-lg transition-colors">
                            <Eye className="w-3 h-3" />
                            {expandedMetadata === shot.id ? 'Ocultar' : 'Metadatos'}
                          </button>
                        )}
                      </div>
                      {expandedFeedback === shot.id && projectId && (
                        <DirectorFeedbackPanel shot={shot} projectId={projectId} />
                      )}
                      {expandedMetadata === shot.id && (
                        <div className="p-3 bg-dark-300/60 border border-amber-500/20 rounded-lg text-xs text-slate-300 space-y-1.5 max-h-64 overflow-y-auto">
                          {(() => {
                            const meta = shot.metadata_json as CinematicShotMetadata
                            const rawMeta = (shot.metadata_json || {}) as Record<string, unknown>
                            const promptSpec = rawMeta.prompt_spec as Record<string, unknown> | undefined
                            const positivePrompt = typeof promptSpec?.positive_prompt === 'string' ? promptSpec.positive_prompt : null
                            const workflowProfile = rawMeta.workflow_profile_executed || rawMeta.workflow_profile_requested || rawMeta.workflow_profile
                            const workflowKey = rawMeta.workflow_key || (rawMeta.workflow as Record<string, unknown> | undefined)?.workflow_key
                            return (
                              <>
                                <p><span className="text-amber-400">Versión:</span> {shot.version}</p>
                                {shot.asset_id && <p><span className="text-amber-400">Asset:</span> {shot.asset_id}</p>}
                                {shot.render_job_id && <p><span className="text-amber-400">Render job:</span> {shot.render_job_id}</p>}
                                {workflowProfile && <p><span className="text-amber-400">Workflow profile:</span> {String(workflowProfile)}</p>}
                                {workflowKey && <p><span className="text-amber-400">Workflow:</span> {String(workflowKey)}</p>}
                                {rawMeta.model_family && <p><span className="text-amber-400">Modelo:</span> {String(rawMeta.model_family)}</p>}
                                {rawMeta.beat_type && <p><span className="text-amber-400">Beat:</span> {String(rawMeta.beat_type)}</p>}
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
                                {positivePrompt && <p><span className="text-cyan-400">Prompt:</span> {positivePrompt.substring(0, 160)}</p>}
                              </>
                            )
                          })()}
                        </div>
                      )}
                    </div>
                  ))}
                  </div>
                </details>
              </div>
            )}
          </>
        )}

        {error && (
          <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 shrink-0" /> {error}
          </div>
        )}

        {/* Credit Estimation Modal */}
        {showCreditModal && creditEstimate && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
            <div className="w-full max-w-lg mx-4 rounded-2xl border border-white/10 bg-dark-200 p-6 shadow-2xl space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-white">Estimación de créditos</h3>
                <button onClick={handleCancelGenerate} className="p-1 rounded-lg hover:bg-white/10 text-slate-400 hover:text-white transition-colors">
                  <X className="w-5 h-5" />
                </button>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="rounded-xl bg-white/5 p-3">
                  <p className="text-xs text-slate-400">Escenas estimadas</p>
                  <p className="text-xl font-bold text-white">{creditEstimate.estimated_scenes}</p>
                </div>
                <div className="rounded-xl bg-white/5 p-3">
                  <p className="text-xs text-slate-400">Planos base</p>
                  <p className="text-xl font-bold text-white">{creditEstimate.base_shots}</p>
                </div>
                <div className="rounded-xl bg-white/5 p-3">
                  <p className="text-xs text-slate-400">Planos cobertura</p>
                  <p className="text-xl font-bold text-white">{creditEstimate.coverage_shots}</p>
                </div>
                <div className="rounded-xl bg-white/5 p-3">
                  <p className="text-xs text-slate-400">Total imágenes</p>
                  <p className="text-xl font-bold text-amber-400">{creditEstimate.total_images}</p>
                </div>
              </div>
              <div className="rounded-xl border border-amber-500/20 bg-amber-500/5 p-3">
                <div className="flex items-center justify-between">
                  <p className="text-sm font-medium text-amber-300">Créditos total</p>
                  <p className="text-2xl font-bold text-amber-400">{creditEstimate.total_credits}</p>
                </div>
              </div>
              {(creditEstimate.warnings ?? []).length > 0 && (
                <div className="rounded-xl border border-amber-500/20 bg-amber-500/5 p-3 space-y-1">
                  <p className="text-xs font-medium text-amber-400">{t('internal.storyboardBuilder.analysis.warnings')}</p>
                  {(creditEstimate.warnings ?? []).map((w, i) => (
                    <p key={i} className="text-xs text-amber-300/70">{w}</p>
                  ))}
                </div>
              )}
              {(creditEstimate.notes ?? []).length > 0 && (
                <div className="rounded-xl border border-white/10 bg-white/5 p-3 space-y-1">
                  <p className="text-xs font-medium text-slate-400">Notas</p>
                  {(creditEstimate.notes ?? []).map((n, i) => (
                    <p key={i} className="text-xs text-slate-300">{n}</p>
                  ))}
                </div>
              )}
              <div className="flex gap-3 pt-2">
                <button onClick={handleCancelGenerate}
                  className="flex-1 px-4 py-2.5 border border-white/10 text-slate-300 rounded-xl hover:bg-white/5 transition-colors text-sm font-medium">
                  Cancelar
                </button>
                <button onClick={handleConfirmGenerate}
                  className="flex-1 px-4 py-2.5 bg-amber-500 hover:bg-amber-400 text-black rounded-xl font-medium transition-colors text-sm">
                  Confirmar generación
                </button>
              </div>
            </div>
          </div>
        )}

        <StoryboardSequenceSelectorModal
          open={sequenceSelectorOpen}
          isLoading={isGenerating || isPlanningSequence || isEstimatingCredits}
          error={sequenceSelectorError}
          scenes={selectorScenes}
          sequences={sequences}
          renderImagesOnComplete={renderImagesOnComplete}
          onRenderImagesChange={setRenderImagesOnComplete}
          onClose={() => {
            setSequenceSelectorOpen(false)
            setSequenceSelectorError(null)
          }}
          onConfirm={handleConfirmSequenceSelection}
        />

        <AssetPickerModal isOpen={pickerOpen} projectId={projectId || ''}
          currentAssetId={shots.find((s) => s.id === selectedShotId)?.asset_id}
          onSelect={handleSelectAsset}
          onClose={() => { setPickerOpen(false); setSelectedShotId(null) }} />
      </div>
    </div>
  )
}
