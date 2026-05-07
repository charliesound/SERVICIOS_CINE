import { useEffect, useRef, useState, type ChangeEvent } from 'react'
import { useParams, Link } from 'react-router-dom'
import { projectsApi } from '@/api'
import { storyboardApi } from '@/api/storyboard'
import { useAuthStore } from '@/store'
import { useUserPlanStatus } from '@/hooks/usePlans'
import { getThumbnailUrl, isComfyAsset } from '@/vite-env'
import {
  ArrowLeft, FileText, Layers, Eye, Save,
  MapPin, Clock, Film, ChevronRight, Sparkles,
  History, RefreshCw, AlertCircle, CheckCircle2, Loader2,
  FileJson, FolderOpen, Download, Crown, Pencil, Upload
} from 'lucide-react'
import { JobProgress } from '@/components/JobProgress'
import { ActionProgressPanel, type ActionProgressState } from '@/components/ActionProgressPanel'
import { StoryboardSequenceSelectorModal, type StoryboardSelectionValue } from '@/components/storyboard/StoryboardSequenceSelectorModal'
import type { StoryboardSceneCandidate, StoryboardSequence, StoryboardShot } from '@/types/storyboard'
import ConceptArtDryRunPanel from '@/components/concept-art/ConceptArtDryRunPanel'

type Tab = 'script' | 'analysis' | 'storyboard' | 'concept-art' | 'history'

interface AnalysisResult {
  source: 'breakdown' | 'document'
  document_id?: string
  doc_type?: string
  confidence_score?: number | null
  structured_payload?: Record<string, unknown>
  status?: string
  scenes_count?: number
  characters_count?: number
  locations_count?: number
  sequences_count?: number
  summary?: Record<string, unknown>
  scenes?: Array<Record<string, unknown>>
}

interface Shot {
  shot_number: number
  shot_type: string
  description: string
  asset_id?: string | null
  thumbnail_url?: string | null
  preview_url?: string | null
  asset_file_name?: string | null
}

interface Scene {
  scene_number: number
  heading: string
  location: string
  time_of_day: string
  shots: Shot[]
}

interface StoryboardResult {
  project_id: string
  total_scenes: number
  scenes: Scene[]
}

interface JobHistoryEntry {
  id: string
  event_type: string
  status_from: string | null
  status_to: string | null
  message: string | null
  detail: string | null
  created_at: string | null
}

interface ProjectAsset {
  id: string
  project_id: string
  job_id: string | null
  file_name: string
  file_extension: string
  asset_type: string
  asset_source: string | null
  content_ref?: string | null
  metadata_json?: Record<string, unknown> | null
  status: string
  created_at: string | null
}

interface JobAssetEntry {
  id: string
  file_name: string
}

interface ProjectJob {
  id: string
  organization_id: string
  project_id: string
  job_type: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  result_data: Record<string, unknown> | null
  error_message: string | null
  progress_percent?: number | null
  progress_stage?: string | null
  progress_code?: string | null
  created_by: string | null
  created_at: string
  updated_at: string
  completed_at: string | null
  history: JobHistoryEntry[]
  assets: JobAssetEntry[]
}

const SHOT_TYPE_LABELS: Record<string, string> = {
  WS: 'Wide Shot',
  MS: 'Medium Shot',
  CU: 'Close-Up',
  ECU: 'Extreme Close-Up',
  OTS: 'Over the Shoulder',
  LS: 'Long Shot',
  PANNING: 'Panning',
  TRACKING: 'Tracking',
  POV: 'Point of View',
}

function ShotTypeBadge({ type }: { type: string }) {
  const label = SHOT_TYPE_LABELS[type] || type
  const colors: Record<string, string> = {
    WS: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
    MS: 'bg-green-500/10 text-green-400 border-green-500/20',
    CU: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
    ECU: 'bg-red-500/10 text-red-400 border-red-500/20',
    OTS: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
    LS: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20',
    PANNING: 'bg-orange-500/10 text-orange-400 border-orange-500/20',
    TRACKING: 'bg-pink-500/10 text-pink-400 border-pink-500/20',
    POV: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20',
  }
  const colorClass = colors[type] || 'bg-white/10 text-gray-300 border-white/20'
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-lg text-xs border font-medium ${colorClass}`}>
      <Film className="w-3 h-3" />
      {label}
    </span>
  )
}

function ConfidenceBar({ score }: { score: number | null }) {
  if (score === null) return <span className="text-gray-500 text-sm">N/A</span>
  const pct = Math.round(score * 100)
  const color = pct >= 70 ? 'bg-green-400' : pct >= 40 ? 'bg-amber-400' : 'bg-red-400'
  return (
    <div className="flex items-center gap-2">
      <div className="w-24 h-2 bg-white/10 rounded-full overflow-hidden">
        <div className={`h-full ${color} rounded-full`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-sm text-gray-300">{pct}%</span>
    </div>
  )
}

export default function ProjectDetailPage() {
  const { projectId } = useParams<{ projectId: string }>()
  const { user } = useAuthStore()
  const { data: planStatus } = useUserPlanStatus(user?.user_id || '', user?.plan || 'free')
  const [project, setProject] = useState<Awaited<ReturnType<typeof projectsApi.get>> | null>(null)
  const [scriptText, setScriptText] = useState('')
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [isStoryboarding, setIsStoryboarding] = useState(false)
  const [isUploadingScript, setIsUploadingScript] = useState(false)
  const [error, setError] = useState('')
  const [saveMsg, setSaveMsg] = useState('')
  const [successMsg, setSuccessMsg] = useState('')
  const [activeTab, setActiveTab] = useState<Tab>('script')
  const [analysisData, setAnalysisData] = useState<AnalysisResult | null>(null)
  const [storyboardData, setStoryboardData] = useState<StoryboardResult | null>(null)
  const [storyboardShots, setStoryboardShots] = useState<StoryboardShot[]>([])
  const [jobs, setJobs] = useState<ProjectJob[]>([])
  const [jobsLoading, setJobsLoading] = useState(false)
  const [retryingJobId, setRetryingJobId] = useState<string | null>(null)
  const [assets, setAssets] = useState<ProjectAsset[]>([])
  const [assetsLoading, setAssetsLoading] = useState(false)
  const [exportingFormat, setExportingFormat] = useState<'json' | 'zip' | null>(null)
  const [viewMode, setViewMode] = useState<'list' | 'grid' | 'presentation'>('list')
  const [analysisProgress, setAnalysisProgress] = useState<ActionProgressState | null>(null)
  const [storyboardProgress, setStoryboardProgress] = useState<ActionProgressState | null>(null)
  const [storyboardModalOpen, setStoryboardModalOpen] = useState(false)
  const [storyboardCandidates, setStoryboardCandidates] = useState<StoryboardSceneCandidate[]>([])
  const [storyboardSequences, setStoryboardSequences] = useState<StoryboardSequence[]>([])
  const [isLoadingStoryboardCandidates, setIsLoadingStoryboardCandidates] = useState(false)
  const [storyboardCandidateError, setStoryboardCandidateError] = useState<string | null>(null)
  const [selectedScriptFileName, setSelectedScriptFileName] = useState('')
  const fileInputRef = useRef<HTMLInputElement | null>(null)

  // Group assets by sequence from metadata_json
  const assetsBySequence = assets.reduce((acc, asset) => {
    const meta = asset.metadata_json as Record<string, unknown> | null
    const seqId = (meta?.sequence_id as string) || 'sin-secuencia'
    if (!acc[seqId]) {
      acc[seqId] = []
    }
    acc[seqId].push(asset)
    return acc
  }, {} as Record<string, ProjectAsset[]>)

  // Sort shots within each sequence by shot_order
  Object.keys(assetsBySequence).forEach(seqId => {
    assetsBySequence[seqId].sort((a, b) => {
      const metaA = a.metadata_json as Record<string, unknown> | null
      const metaB = b.metadata_json as Record<string, unknown> | null
      const orderA = (metaA?.shot_order as number) || 0
      const orderB = (metaB?.shot_order as number) || 0
      return orderA - orderB
    })
  })

  const parseApiError = (fallback: string) => (err: unknown): string => {
    const status = (err as { response?: { status?: number } })?.response?.status
    if (status === 401 || status === 403) return 'Sesion caducada. Vuelve a iniciar sesion.'
    const detail = (err as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail
    if (typeof detail === 'string') return detail
    if (detail && typeof detail === 'object' && 'message' in detail) {
      return String((detail as { message?: unknown }).message || fallback)
    }
    // Handle PLAN_EXPORT_BLOCKED error structure
    if (detail && typeof detail === 'object' && 'code' in detail) {
      return String((detail as { message?: unknown }).message || fallback)
    }
    return fallback
  }

  const showSuccess = (message: string) => {
    setSuccessMsg(message)
    window.setTimeout(() => setSuccessMsg(''), 2500)
  }

  const resolveShotVisual = (assetId?: string | null) => {
    if (!assetId || !projectId) return { thumbnail_url: null, preview_url: null, asset_file_name: null }
    const asset = assets.find((item) => item.id === assetId)
    const previewUrl = asset?.content_ref || `/api/projects/${projectId}/presentation/assets/${assetId}/preview`
    const thumbnailUrl = `/api/projects/${projectId}/presentation/assets/${assetId}/thumbnail`
    return {
      thumbnail_url: thumbnailUrl,
      preview_url: previewUrl,
      asset_file_name: asset?.file_name || null,
    }
  }

  const inferStoryboardStatus = (sceneNumber: number, sceneAssetIds: Array<string | null | undefined>) => {
    const assetIds = sceneAssetIds.filter(Boolean)
    if (assetIds.length > 0) return 'generated' as const
    const hasSceneShots = storyboardShots.some((shot) => (shot.scene_number || 0) === sceneNumber)
    if (hasSceneShots) return 'without_image' as const
    return 'pending' as const
  }

  const parseSceneCandidatesFromScript = (text: string): StoryboardSceneCandidate[] => {
    const lines = text.split(/\r?\n/)
    const candidates: StoryboardSceneCandidate[] = []
    const headingRegex = /^\s*(\d+)?\s*(INT\.|EXT\.|INT\/EXT\.|I\/E\.)/i
    for (let index = 0; index < lines.length; index += 1) {
      const line = lines[index].trim()
      if (!headingRegex.test(line)) continue
      const explicitNumber = line.match(/^(\d+)/)?.[1]
      const sceneNumber = explicitNumber ? Number(explicitNumber) : candidates.length + 1
      const nextLines = lines.slice(index + 1, index + 3).map((item) => item.trim()).filter(Boolean)
      candidates.push({
        scene_number: sceneNumber,
        scene_heading: line,
        narrative_text: nextLines.join(' '),
        source: 'parsed',
      })
    }
    return candidates
  }

  const buildSceneCandidates = (
    scenesDetected: Array<Record<string, unknown>>,
    sequences: StoryboardSequence[],
    source: 'options' | 'analysis' | 'parsed',
  ): StoryboardSceneCandidate[] => {
    const sequenceByScene = new Map<number, StoryboardSequence>()
    sequences.forEach((sequence) => {
      sequence.included_scenes.forEach((sceneNumber) => sequenceByScene.set(sceneNumber, sequence))
    })

    return scenesDetected.map((scene, index) => {
      const sceneNumber = Number(scene.scene_number || scene.number || index + 1)
      const sequence = sequenceByScene.get(sceneNumber)
      const relatedShots = storyboardShots.filter((shot) => (shot.scene_number || 0) === sceneNumber)
      const primaryAssetId = relatedShots.find((shot) => shot.asset_id)?.asset_id || null
      const visuals = resolveShotVisual(primaryAssetId)
      return {
        scene_number: sceneNumber,
        scene_heading: String(scene.heading || scene.scene_heading || `ESCENA ${sceneNumber}`),
        narrative_text: Array.isArray(scene.action_blocks)
          ? String(scene.action_blocks.slice(0, 2).join(' '))
          : String(scene.summary || scene.description || ''),
        sequence_id: sequence?.sequence_id || null,
        sequence_title: sequence?.title || null,
        storyboard_status: inferStoryboardStatus(sceneNumber, relatedShots.map((shot) => shot.asset_id)),
        asset_id: primaryAssetId,
        thumbnail_url: visuals.thumbnail_url,
        preview_url: visuals.preview_url,
        asset_file_name: visuals.asset_file_name,
        source,
      }
    })
  }

  const buildProgressState = (
    title: string,
    job: ProjectJob | undefined,
    fallbackLabel: string,
    helperText?: string,
    previousPercent = 0,
  ): ActionProgressState => {
    if (!job) {
      return {
        title,
        status: 'queued',
        percent: previousPercent || 0,
        label: fallbackLabel,
        helperText,
        estimated: true,
      }
    }
    const mappedStatus = job.status === 'pending'
      ? 'queued'
      : job.status === 'processing'
        ? 'processing'
        : job.status === 'completed'
          ? 'completed'
          : 'failed'
    const estimatedPercent = job.status === 'pending'
      ? 10
      : job.status === 'processing'
        ? Math.max(previousPercent || 25, 45)
        : job.status === 'completed'
          ? 100
          : previousPercent || 45
    return {
      title,
      status: mappedStatus,
      percent: typeof job.progress_percent === 'number' ? job.progress_percent : estimatedPercent,
      label: job.progress_stage || fallbackLabel,
      helperText,
      estimated: typeof job.progress_percent !== 'number',
      jobId: job.id,
      errorMessage: job.error_message,
    }
  }

  const mapStoryboardScopeToResult = (projectIdValue: string, shots: Array<{
    scene_number?: number
    scene_heading?: string
    sequence_id?: string
    sequence_order: number
    shot_type?: string
    narrative_text?: string
    asset_id?: string | null
  }>): StoryboardResult => {
    const groupedScenes = shots.reduce((acc, shot) => {
      const key = shot.scene_number || 0
      if (!acc[key]) {
        acc[key] = {
          scene_number: key,
          heading: shot.scene_heading || `ESCENA ${key}`,
          location: shot.sequence_id || '',
          time_of_day: '',
          shots: [],
        }
      }
      const visuals = resolveShotVisual(shot.asset_id)
      acc[key].shots.push({
        shot_number: shot.sequence_order,
        shot_type: shot.shot_type || 'MS',
        description: shot.narrative_text || 'Shot generado',
        asset_id: shot.asset_id,
        thumbnail_url: visuals.thumbnail_url,
        preview_url: visuals.preview_url,
        asset_file_name: visuals.asset_file_name,
      })
      return acc
    }, {} as Record<number, Scene>)

    return {
      project_id: projectIdValue,
      total_scenes: Object.keys(groupedScenes).length,
      scenes: Object.values(groupedScenes).sort((a, b) => a.scene_number - b.scene_number),
    }
  }

  const loadAnalysisState = async () => {
    if (!projectId) return
    try {
      const [summaryRaw, scenesRaw] = await Promise.all([
        projectsApi.getAnalysisSummary(projectId),
        projectsApi.getBreakdownScenes(projectId),
      ])
      const summary = summaryRaw as Record<string, unknown>
      if (summary?.status && summary.status !== 'not_found') {
        setAnalysisData({
          source: 'breakdown',
          status: String(summary.status || 'completed'),
          scenes_count: Number(summary.scenes_count || 0),
          characters_count: Number(summary.characters_count || 0),
          locations_count: Number(summary.locations_count || 0),
          sequences_count: Number(summary.sequences_count || 0),
          summary: (summary.summary as Record<string, unknown>) || {},
          scenes: scenesRaw.scenes,
        })
        return
      }
      const projectJobs = await projectsApi.getJobs(projectId)
      const fallbackJob = projectJobs.find((job) => job.job_type === 'analyze' && job.status === 'completed' && job.result_data)
      if (fallbackJob?.result_data) {
        const result = fallbackJob.result_data as Record<string, unknown>
        setAnalysisData({
          source: 'document',
          document_id: String(result.document_id || ''),
          doc_type: String(result.doc_type || 'unknown'),
          confidence_score: typeof result.confidence_score === 'number' ? result.confidence_score : null,
          structured_payload: (result.structured_payload as Record<string, unknown>) || {},
        })
        return
      }
      setAnalysisData(null)
    } catch {
      setAnalysisData(null)
    }
  }

  const loadStoryboardState = async () => {
    if (!projectId) return
    try {
      const storyboardScope = await storyboardApi.getStoryboard(projectId, { mode: 'FULL_SCRIPT' })
      setStoryboardShots(storyboardScope?.shots || [])
      if (!storyboardScope?.shots?.length) {
        setStoryboardData(null)
        return
      }
      setStoryboardData(mapStoryboardScopeToResult(projectId, storyboardScope.shots))
    } catch {
      setStoryboardShots([])
      setStoryboardData(null)
    }
  }

  const loadStoryboardCandidates = async () => {
    if (!projectId) return
    setIsLoadingStoryboardCandidates(true)
    setStoryboardCandidateError(null)
    try {
      const options = await storyboardApi.getOptions(projectId)
      const sequences = options.sequences || []
      setStoryboardSequences(sequences)
      if (options.scenes_detected?.length) {
        setStoryboardCandidates(buildSceneCandidates(options.scenes_detected as Array<Record<string, unknown>>, sequences, 'options'))
      } else {
        const parsed = parseSceneCandidatesFromScript(scriptText)
        setStoryboardCandidates(parsed)
      }
    } catch (err) {
      console.error('[ProjectDetail] storyboard candidates failed', err)
      const parsed = parseSceneCandidatesFromScript(scriptText)
      setStoryboardSequences([])
      setStoryboardCandidates(parsed)
      if (!parsed.length) {
        setStoryboardCandidateError('No se pudieron detectar escenas para storyboard')
      }
    } finally {
      setIsLoadingStoryboardCandidates(false)
    }
  }

  useEffect(() => {
    if (!projectId) return
    let active = true
    Promise.all([projectsApi.get(projectId), loadAnalysisState(), loadStoryboardState()])
      .then(([p]) => {
        if (!active) return
        setProject(p)
        setScriptText(p.script_text || '')
        loadJobs()
        loadAssets()
      })
      .catch(() => {})
      .finally(() => {
        if (active) setIsLoading(false)
      })
    return () => {
      active = false
    }
  }, [projectId])

  const loadJobs = async () => {
    if (!projectId) return
    setJobsLoading(true)
    try {
      const items = await projectsApi.getJobs(projectId)
      setJobs(items as unknown as ProjectJob[])
      return items as unknown as ProjectJob[]
    } catch {
      return [] as ProjectJob[]
    } finally {
      setJobsLoading(false)
    }
  }

  const loadAssets = async () => {
    if (!projectId) return
    setAssetsLoading(true)
    try {
      const result = await projectsApi.getAssets(projectId)
      setAssets(result)
      return result
    } catch {
      return [] as ProjectAsset[]
    } finally {
      setAssetsLoading(false)
    }
  }

  useEffect(() => {
    if (activeTab === 'history') {
      loadJobs()
      loadAssets()
    }
  }, [activeTab])

  useEffect(() => {
    if (!projectId || !storyboardShots.length) return
    setStoryboardData(mapStoryboardScopeToResult(projectId, storyboardShots))
  }, [assets, storyboardShots, projectId])

  const pollJobsUntilSettled = (
    jobType: 'analyze' | 'storyboard',
    onUpdate: (job?: ProjectJob) => void,
  ) => {
    const interval = window.setInterval(async () => {
      const items = await loadJobs()
      const latestJob = [...(items || [])]
        .filter((job) => job.job_type === jobType)
        .sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime())[0]
      onUpdate(latestJob)
      if (latestJob && ['completed', 'failed'].includes(latestJob.status)) {
        window.clearInterval(interval)
        await loadAssets()
        await loadStoryboardState()
        if (jobType === 'analyze') {
          await loadAnalysisState()
        }
      }
    }, 2000)
    return () => window.clearInterval(interval)
  }

  const handleSaveScript = async () => {
    if (!projectId) return
    setIsSaving(true)
    setError('')
    setSaveMsg('')
    try {
      const updated = await projectsApi.updateScript(projectId, { script_text: scriptText })
      setProject(updated)
      setSaveMsg('Guion guardado')
      setTimeout(() => setSaveMsg(''), 2000)
    } catch {
      setError('Error al guardar el guion')
    } finally {
      setIsSaving(false)
    }
  }

  const handleScriptFileChange = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!projectId || !file) return

    setIsUploadingScript(true)
    setError('')
    setSuccessMsg('')
    setSelectedScriptFileName(file.name)
    try {
      const extension = file.name.split('.').pop()?.toLowerCase() || ''
      if (extension === 'txt' || extension === 'md') {
        const text = await file.text()
        await projectsApi.intakeScript(projectId, { script_text: text })
        setScriptText(text)
      } else if (extension === 'pdf' || extension === 'docx') {
        const document = await projectsApi.uploadScriptDocument(projectId, file)
        if (document.extracted_text) {
          await projectsApi.intakeScript(projectId, { script_text: document.extracted_text })
          setScriptText(document.extracted_text)
        } else {
          throw new Error(document.error_message || 'No se pudo extraer texto del documento')
        }
      } else {
        throw new Error('Este formato requiere extracción backend. Usa .txt/.md por ahora.')
      }
      const updated = await projectsApi.get(projectId)
      setProject(updated)
      showSuccess('Guion cargado correctamente')
    } catch (err) {
      setError(parseApiError('No se pudo cargar el archivo de guion')(err))
    } finally {
      event.target.value = ''
      setIsUploadingScript(false)
    }
  }

  const handleAnalyzeScript = async () => {
    if (!projectId) {
      setError('No se encontro el proyecto para analizar')
      return
    }
    if (!scriptText.trim()) {
      setError('Carga un guion antes de analizar')
      setActiveTab('script')
      return
    }
    if (!confirm('Iniciar analisis del guion? Esto procesara el texto y extraera escenas, personajes y estructura.')) return

    setIsAnalyzing(true)
    setError('')
    setSuccessMsg('')
    setActiveTab('analysis')
    setAnalysisProgress({
      title: 'Analizar guion',
      status: 'queued',
      percent: 0,
      label: 'Preparando análisis...',
      helperText: 'Esperando creación del job de análisis.',
      estimated: true,
    })
    try {
      console.debug('[ProjectDetail] analyze click', { projectId })
      await projectsApi.updateScript(projectId, { script_text: scriptText })
      const stopPolling = pollJobsUntilSettled('analyze', (job) => {
        setAnalysisProgress((current) => buildProgressState(
          'Analizar guion',
          job,
          'Analizando guion...',
          job?.progress_stage ? undefined : 'Progreso estimado hasta que el backend devuelva porcentaje real.',
          current?.percent || 0,
        ))
      })
      const response = await projectsApi.analyze(projectId)
      console.debug('[ProjectDetail] analyze response', response)
      await loadAnalysisState()
      await loadJobs()
      setAnalysisProgress((current) => ({
        ...(current || { title: 'Analizar guion', estimated: false }),
        status: 'completed',
        percent: 100,
        label: 'Análisis completado',
        helperText: 'El resumen y las escenas ya están disponibles.',
      }))
      stopPolling()
      showSuccess('Análisis completado')
    } catch (err) {
      console.error('[ProjectDetail] analyze failed', err)
      setError(parseApiError('Error al analizar el guion. Asegurate de que el guion tenga contenido.')(err))
      setAnalysisProgress((current) => ({
        ...(current || { title: 'Analizar guion', percent: 0 }),
        status: 'failed',
        label: 'Error en análisis',
        errorMessage: parseApiError('Error al analizar el guion. Asegurate de que el guion tenga contenido.')(err),
      }))
      setActiveTab('script')
    } finally {
      setIsAnalyzing(false)
    }
  }

  const openStoryboardSelector = async () => {
    if (!projectId) {
      setError('No se encontro el proyecto para generar storyboard')
      return
    }
    if (!scriptText.trim()) {
      setError('Carga un guion antes de generar storyboard')
      setActiveTab('script')
      return
    }

    setError('')
    setSuccessMsg('')
    await loadStoryboardCandidates()
    setStoryboardModalOpen(true)
  }

  const handleGenerateStoryboard = () => {
    void openStoryboardSelector()
  }

  const confirmGenerateStoryboardSelection = async (selection: StoryboardSelectionValue) => {
    if (!projectId) return
    const selectedSceneNumbers = selection.sceneNumbers || []
    setIsStoryboarding(true)
    setStoryboardModalOpen(false)
    setError('')
    setSuccessMsg('')
    setActiveTab('storyboard')
    setStoryboardProgress({
      title: 'Generar storyboard',
      status: 'queued',
      percent: 0,
      label: 'Preparando storyboard...',
      helperText: selectedSceneNumbers.length > 0
        ? `Progreso estimado hasta que el backend devuelva progreso real por escena. ${selectedSceneNumbers.length} escenas seleccionadas.`
        : 'Preparando generación de storyboard.',
      estimated: true,
    })
    try {
      console.debug('[ProjectDetail] storyboard click', { projectId })
      await projectsApi.updateScript(projectId, { script_text: scriptText })
      if (!analysisData) {
        await projectsApi.analyze(projectId)
        await loadAnalysisState()
      }
      const generationMode = selection.mode
      const payload = {
        mode: generationMode,
        generation_mode: generationMode,
        sequence_id: generationMode === 'SEQUENCE' ? selection.sequenceId || null : null,
        sequence_ids: selection.sequenceIds || [],
        scene_start: generationMode === 'SCENE_RANGE' ? selection.sceneStart || null : generationMode === 'SINGLE_SCENE' ? selectedSceneNumbers[0] || null : null,
        scene_end: generationMode === 'SCENE_RANGE' ? selection.sceneEnd || null : generationMode === 'SINGLE_SCENE' ? selectedSceneNumbers[0] || null : null,
        selected_scene_ids: selectedSceneNumbers.map(String),
        scene_numbers: selectedSceneNumbers,
        style_preset: 'cinematic_realistic',
        visual_mode: 'cinematic_realistic',
        shots_per_scene: 1,
        max_scenes: generationMode === 'FULL_SCRIPT' ? 3 : selectedSceneNumbers.length || null,
        overwrite: selection.overwrite,
      }
      const stopPolling = pollJobsUntilSettled('storyboard', (job) => {
        setStoryboardProgress((current) => buildProgressState(
          'Generar storyboard',
          job,
          selectedSceneNumbers.length > 0
            ? `Procesando selección de ${selectedSceneNumbers.length} escena(s)`
            : 'Generando storyboard...',
          selectedSceneNumbers.length > 0
            ? `Progreso estimado hasta que el backend devuelva progreso real por escena. ${selectedSceneNumbers.length} escenas seleccionadas.`
            : 'Progreso estimado hasta que el backend devuelva progreso real.',
          current?.percent || 0,
        ))
      })
      const response = await storyboardApi.generate(projectId, {
        ...payload,
      })
      console.debug('[ProjectDetail] storyboard response', response)
      await loadJobs()
      await loadStoryboardState()
      await loadAssets()
      setStoryboardProgress((current) => ({
        ...(current || { title: 'Generar storyboard', estimated: false }),
        status: 'completed',
        percent: 100,
        label: 'Storyboard completado',
        helperText: response.total_scenes
          ? `${response.total_scenes} escenas y ${response.total_shots} planos generados.`
          : 'Storyboard completado correctamente.',
        jobId: response.job_id,
      }))
      stopPolling()
      showSuccess('Storyboard generado correctamente')
    } catch (err) {
      console.error('[ProjectDetail] storyboard failed', err)
      setError(parseApiError('Error al generar el storyboard. Asegurate de que el guion tenga contenido.')(err))
      setStoryboardProgress((current) => ({
        ...(current || { title: 'Generar storyboard', percent: 0 }),
        status: 'failed',
        label: 'Error generando storyboard',
        errorMessage: parseApiError('Error al generar el storyboard. Asegurate de que el guion tenga contenido.')(err),
      }))
      setActiveTab('script')
    } finally {
      setIsStoryboarding(false)
    }
  }

  const downloadExport = (blob: Blob, extension: 'json' | 'zip') => {
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${project?.name || 'project'}.${extension}`
    document.body.appendChild(a)
    a.click()
    a.remove()
    window.URL.revokeObjectURL(url)
  }

  const handleExport = async (format: 'json' | 'zip') => {
    if (!projectId) return
    setExportingFormat(format)
    setError('')
    try {
      if (format === 'zip') {
        // Use async export via delivery service
        const result = await projectsApi.triggerExport(projectId)
        // Poll for status
        pollExportStatus(result.job_id)
      } else {
        const blob = await projectsApi.exportJson(projectId)
        downloadExport(blob, format)
      }
    } catch (err) {
      setError(parseApiError(`No se pudo exportar el proyecto en ${format.toUpperCase()}.`)(err))
    } finally {
      setExportingFormat(null)
    }
  }

  const pollExportStatus = async (jobId: string) => {
    const checkStatus = async () => {
      try {
        const job = await projectsApi.getJobStatus(jobId)

        if (job.status === 'completed') {
          // Get the deliverable and download
          const deliverableId = typeof job.result_data?.deliverable_id === 'string'
            ? job.result_data.deliverable_id
            : null
          if (deliverableId) {
            const blob = await projectsApi.downloadDeliverable(deliverableId)
            downloadExport(blob, 'zip')
          }
        } else if (job.status === 'failed') {
          setError(parseApiError('La exportación ZIP ha fallado.')(null))
        } else {
          // Still running, poll again
          setTimeout(checkStatus, 2000)
        }
      } catch (err) {
        setTimeout(checkStatus, 2000)
      }
    }
    checkStatus()
  }

  // Polling simple para jobs activos cada 2 segundos
  useEffect(() => {
    if (!projectId) return
    const hasActiveJobs = jobs.some(j => j.status === 'pending' || j.status === 'processing')
    if (!hasActiveJobs) return

    const interval = setInterval(async () => {
      console.debug('[QA] Polling active jobs...')
      loadJobs()
      loadAssets()
      loadStoryboardState()
    }, 2000)
    return () => clearInterval(interval)
  }, [projectId, jobs])

  const TABS: { key: Tab; label: string; count?: number | null }[] = [
    { key: 'script', label: 'Guion' },
    {
      key: 'analysis',
      label: 'Analisis',
      count: analysisData ? 1 : null,
    },
    {
      key: 'storyboard',
      label: 'Storyboard',
      count: storyboardData ? storyboardData.total_scenes : null,
    },
    {
      key: 'concept-art',
      label: 'Concept Art',
    },
    {
      key: 'history',
      label: 'Historial',
      count: jobs.length > 0 ? jobs.length : null,
    },
  ]

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="flex items-center gap-3 text-amber-400">
          <svg className="animate-spin w-6 h-6" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
          <span className="text-sm">Cargando proyecto...</span>
        </div>
      </div>
    )
  }

  if (!project) {
    return (
      <div className="text-center py-20">
        <p className="text-gray-400">Proyecto no encontrado.</p>
        <Link to="/projects" className="text-amber-400 text-sm mt-2 inline-block">← Volver a proyectos</Link>
      </div>
    )
  }

  return (
    <div className="max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <Link
          to="/projects"
          className="p-2 rounded-lg hover:bg-white/5 text-gray-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div className="flex-1">
          <h1 className="text-2xl font-bold">{project.name}</h1>
          <p className="text-gray-400 text-sm mt-0.5">
            {project.description || 'Sin descripcion'}
            {project.script_text && (
              <span className="ml-2 text-green-400">· Guion cargado</span>
            )}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => handleExport('json')}
            disabled={!!exportingFormat || !planStatus?.export_json}
            className="px-4 py-2 text-sm border border-white/10 hover:border-white/20 rounded-xl transition-colors flex items-center gap-2 disabled:opacity-40"
          >
            <Download className="w-4 h-4" />
            {exportingFormat === 'json' ? 'Exportando JSON...' : 'Export JSON'}
          </button>
          <button
            onClick={() => handleExport('zip')}
            disabled={!!exportingFormat || !planStatus?.export_zip}
            className="px-4 py-2 text-sm border border-white/10 hover:border-white/20 rounded-xl transition-colors flex items-center gap-2 disabled:opacity-40"
          >
              <Download className="w-4 h-4" />
              {exportingFormat === 'zip' ? 'Empaquetando ZIP...' : 'Export ZIP'}
          </button>
          <Link
            to={`/projects/${projectId}/funding`}
            className="px-4 py-2 text-sm border border-white/10 hover:border-white/20 rounded-xl transition-colors flex items-center gap-2"
          >
            <FileText className="w-4 h-4" />
            Funding
          </Link>
          <Link
            to={`/projects/${projectId}/dashboard`}
            className="px-4 py-2 text-sm border border-white/10 hover:border-white/20 rounded-xl transition-colors flex items-center gap-2"
          >
            <FolderOpen className="w-4 h-4" />
            Dashboard
          </Link>
          <Link
            to={`/projects/${projectId}/storyboard-builder`}
            className="px-4 py-2 text-sm bg-amber-500 hover:bg-amber-400 text-black rounded-xl font-medium transition-colors flex items-center gap-2"
          >
            <Pencil className="w-4 h-4" />
            Editar Storyboard
          </Link>
          <Link
            to={`/projects/${projectId}/editorial`}
            className="px-4 py-2 text-sm border border-emerald-500/20 hover:border-emerald-400/30 text-emerald-300 rounded-xl transition-colors flex items-center gap-2"
          >
            <Film className="w-4 h-4" />
            Premontaje / Assembly
          </Link>
        </div>
      </div>

      {planStatus && (
        <div className="mb-6 rounded-2xl border border-white/10 bg-dark-200/80 p-4">
          <div className="flex items-center justify-between gap-6">
            <div>
              <div className="flex items-center gap-2 mb-2 text-sm text-slate-400">
                <Crown className="w-4 h-4 text-amber-400" />
                Plan y uso
              </div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                <div>
                  <p className="text-slate-500">Proyectos</p>
                  <p className="text-white font-semibold">{planStatus.projects_count}/{planStatus.max_projects === -1 ? '∞' : planStatus.max_projects}</p>
                </div>
                <div>
                  <p className="text-slate-500">Jobs</p>
                  <p className="text-white font-semibold">{planStatus.jobs_count}/{planStatus.max_total_jobs === -1 ? '∞' : planStatus.max_total_jobs}</p>
                </div>
                <div>
                  <p className="text-slate-500">Analisis</p>
                  <p className="text-white font-semibold">{planStatus.analyses_count}/{planStatus.max_analyses === -1 ? '∞' : planStatus.max_analyses}</p>
                </div>
                <div>
                  <p className="text-slate-500">Storyboards</p>
                  <p className="text-white font-semibold">{planStatus.storyboards_count}/{planStatus.max_storyboards === -1 ? '∞' : planStatus.max_storyboards}</p>
                </div>
              </div>
            </div>
            <div className="text-right">
              <p className={`text-sm font-medium ${planStatus.export_json ? 'text-green-400' : 'text-amber-400'}`}>
                {planStatus.export_json ? 'Export JSON incluido' : 'Upgrade para exportar'}
              </p>
              <p className={`mt-1 text-xs font-medium ${planStatus.export_zip ? 'text-green-400' : 'text-slate-500'}`}>
                {planStatus.export_zip ? 'ZIP comercial disponible' : 'ZIP disponible en planes con export completo'}
              </p>
              {(planStatus.recommended_upgrade || !planStatus.export_json) && (
                <Link to="/plans" className="mt-2 inline-flex items-center gap-1 text-sm text-amber-400 hover:text-amber-300">
                  Upgrade recomendado: {(planStatus.recommended_upgrade || 'creator')}
                  <ChevronRight className="w-4 h-4" />
                </Link>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Tab bar */}
      <div className="flex gap-1 mb-6 border-b border-white/10">
        {TABS.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`px-4 py-2.5 text-sm font-medium transition-all relative ${
              activeTab === tab.key
                ? 'text-amber-400'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            <span className="flex items-center gap-2">
              {tab.label}
              {tab.count != null && (
                <span className={`px-1.5 py-0.5 rounded text-xs ${
                  activeTab === tab.key ? 'bg-amber-500/20 text-amber-300' : 'bg-white/10 text-gray-400'
                }`}>
                  {tab.count}
                </span>
              )}
            </span>
            {activeTab === tab.key && (
              <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-amber-400 rounded-t" />
            )}
          </button>
        ))}
      </div>

      {(error || successMsg || analysisProgress || storyboardProgress) && (
        <div className="space-y-3 mb-6">
          {error && (
            <div className="rounded-2xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-300">
              {error}
            </div>
          )}
          {successMsg && (
            <div className="rounded-2xl border border-emerald-500/20 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-300">
              {successMsg}
            </div>
          )}
          <ActionProgressPanel progress={analysisProgress} onRetry={handleAnalyzeScript} retryLabel="Reintentar análisis" />
          <ActionProgressPanel progress={storyboardProgress} onRetry={handleGenerateStoryboard} retryLabel="Reintentar storyboard" />
        </div>
      )}

      {/* ── TAB: GUION ── */}
      {activeTab === 'script' && (
        <div className="space-y-4">
          {/* Editor card */}
          <div className="card bg-dark-200/80 border border-white/5 p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-amber-500/10 flex items-center justify-center">
                  <FileText className="w-5 h-5 text-amber-400" />
                </div>
                <div>
                  <h3 className="font-semibold">Editor de guion</h3>
                  <p className="text-gray-400 text-xs">Pega o edita el texto del guion</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".txt,.md,.pdf,.doc,.docx,.rtf"
                  onChange={handleScriptFileChange}
                  className="hidden"
                />
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  disabled={isUploadingScript || isSaving}
                  className="px-4 py-2 text-sm border border-white/10 hover:border-white/20 rounded-xl transition-colors flex items-center gap-2 disabled:opacity-40 disabled:cursor-not-allowed"
                >
                  <Upload className="w-4 h-4" />
                  {isUploadingScript ? 'Subiendo...' : 'Subir archivo de guion'}
                </button>
                {saveMsg && (
                  <span className="text-green-400 text-sm flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
                    {saveMsg}
                  </span>
                )}
                <button
                  type="button"
                  onClick={handleSaveScript}
                  disabled={isSaving}
                  className="px-4 py-2 text-sm border border-white/10 hover:border-white/20 rounded-xl transition-colors flex items-center gap-2 disabled:opacity-40 disabled:cursor-not-allowed"
                >
                  <Save className="w-4 h-4" />
                  {isSaving ? 'Guardando...' : 'Guardar guion'}
                </button>
              </div>
            </div>

            {selectedScriptFileName && (
              <div className="mb-4 rounded-xl border border-white/10 bg-white/[0.03] px-3 py-2 text-xs text-gray-400">
                Archivo seleccionado: <span className="text-white">{selectedScriptFileName}</span>
              </div>
            )}

            <textarea
              value={scriptText}
              onChange={(e) => setScriptText(e.target.value)}
              placeholder="Pega aqui el texto de tu guion...&#10;&#10;INT. CAFE - DIA&#10;MARIA esta sentada.&#10;MARIA: Buenos dias.&#10;EXT. CALLE - NOCHE&#10;JUAN camina bajo la lluvia."
              className="input w-full min-h-[320px] resize-y font-mono text-sm"
            />
            <div className="flex items-center justify-between mt-2">
              <p className="text-gray-500 text-xs">
                {scriptText.length.toLocaleString()} caracteres
              </p>
              {scriptText.trim() && (
                <span className="text-xs text-gray-500">
                  ~{Math.max(1, scriptText.trim().split(/\s+/).length)} palabras
                </span>
              )}
            </div>
          </div>

          {/* Action cards */}
          <div className="grid grid-cols-2 gap-4">
            <button
              type="button"
              onClick={handleAnalyzeScript}
              disabled={isAnalyzing || isUploadingScript}
              className="card p-5 flex items-start gap-4 hover:border-amber-500/30 transition-all disabled:opacity-40 disabled:cursor-not-allowed group"
            >
              <div className="w-11 h-11 rounded-xl bg-amber-500/10 flex items-center justify-center flex-shrink-0 group-hover:bg-amber-500/20 transition-colors">
                {isAnalyzing ? (
                  <svg className="animate-spin w-5 h-5 text-amber-400" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                ) : (
                  <Layers className="w-5 h-5 text-amber-400" />
                )}
              </div>
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-semibold text-sm">
                    {isAnalyzing ? 'Analizando...' : 'Analizar guion'}
                  </span>
                </div>
                <p className="text-gray-400 text-xs leading-relaxed">
                  Detecta tipo de documento, personajes, dialogos y estructura narrativa.
                </p>
              </div>
            </button>

            <button
              type="button"
              onClick={handleGenerateStoryboard}
              disabled={isStoryboarding || isAnalyzing || isUploadingScript}
              className="card p-5 flex items-start gap-4 hover:border-white/20 transition-all disabled:opacity-40 disabled:cursor-not-allowed group"
            >
              <div className="w-11 h-11 rounded-xl bg-white/5 flex items-center justify-center flex-shrink-0 group-hover:bg-white/10 transition-colors">
                {isStoryboarding ? (
                  <svg className="animate-spin w-5 h-5 text-gray-300" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                ) : (
                  <Eye className="w-5 h-5 text-gray-300" />
                )}
              </div>
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-semibold text-sm">
                    {isStoryboarding ? 'Generando...' : 'Generar storyboard'}
                  </span>
                </div>
                <p className="text-gray-400 text-xs leading-relaxed">
                  Detecta escenas, sugiere tipos de plano y genera la estructura visual.
                </p>
              </div>
            </button>
          </div>

          {error && (
            <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-sm">
              {error}
            </div>
          )}
        </div>
      )}

      {/* ── TAB: ANALISIS ── */}
      {activeTab === 'analysis' && (
        <div>
          {isAnalyzing ? (
            <div className="card p-12 flex flex-col items-center justify-center gap-4 text-center">
              <svg className="animate-spin w-8 h-8 text-amber-400" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              <div>
                <p className="text-amber-400 font-medium">Analizando guion...</p>
                <p className="text-gray-400 text-sm mt-1">Extrayendo escenas, personajes y estructura</p>
              </div>
            </div>
          ) : analysisData ? (
            <div className="space-y-4">
              <div className="card bg-dark-200/80 border border-white/5 p-6">
                <div className="flex items-center gap-2 mb-5">
                  <div className="w-8 h-8 rounded-lg bg-amber-500/10 flex items-center justify-center">
                    <Sparkles className="w-4 h-4 text-amber-400" />
                  </div>
                  <h3 className="font-semibold">Resumen del analisis</h3>
                </div>
                <div className="grid grid-cols-3 gap-4">
                  <div className="p-4 bg-white/5 rounded-xl">
                    <p className="text-gray-400 text-xs mb-1 uppercase tracking-wider">Fuente</p>
                    <p className="text-white font-semibold capitalize">
                      {analysisData.source === 'breakdown' ? 'Scene breakdown' : (analysisData.doc_type || 'document').replace(/_/g, ' ')}
                    </p>
                  </div>
                  <div className="p-4 bg-white/5 rounded-xl">
                    <p className="text-gray-400 text-xs mb-2 uppercase tracking-wider">Escenas</p>
                    <p className="text-white font-semibold">{analysisData.scenes_count ?? analysisData.scenes?.length ?? 0}</p>
                  </div>
                  <div className="p-4 bg-white/5 rounded-xl">
                    <p className="text-gray-400 text-xs mb-1 uppercase tracking-wider">Personajes</p>
                    <p className="text-white font-semibold">
                      {analysisData.characters_count ?? '—'}
                    </p>
                  </div>
                </div>
              </div>

              {analysisData.source === 'breakdown' ? (
                <>
                  <div className="card bg-dark-200/80 border border-white/5 p-6">
                    <h4 className="text-sm font-semibold mb-4 text-gray-300">Desglose</h4>
                    <div className="grid gap-3 md:grid-cols-3 text-sm text-slate-300">
                      <p><span className="text-slate-500">Localizaciones:</span> {analysisData.locations_count ?? '—'}</p>
                      <p><span className="text-slate-500">Secuencias:</span> {analysisData.sequences_count ?? '—'}</p>
                      <p><span className="text-slate-500">Estado:</span> {analysisData.status || 'completed'}</p>
                    </div>
                  </div>
                  <div className="card bg-dark-200/80 border border-white/5 p-6">
                    <h4 className="text-sm font-semibold mb-4 text-gray-300">Escenas detectadas</h4>
                    <div className="space-y-3">
                      {(analysisData.scenes || []).slice(0, 8).map((scene, index) => (
                        <div key={`${scene.scene_id || index}`} className="rounded-xl border border-white/5 bg-white/[0.03] p-4">
                          <p className="font-medium text-white">{String(scene.heading || scene.scene_id || `Escena ${index + 1}`)}</p>
                          <p className="mt-1 text-xs text-slate-400">
                            {String(scene.location || 'sin localizacion')} · {String(scene.time_of_day || 'DAY')}
                          </p>
                          <p className="mt-2 text-sm text-slate-300">
                            Personajes: {Array.isArray(scene.characters) ? scene.characters.join(', ') || '—' : '—'}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                </>
              ) : (
                <div className="card bg-dark-200/80 border border-white/5 p-6">
                  <h4 className="text-sm font-semibold mb-4 text-gray-300">Analisis documental</h4>
                  <div className="grid gap-3 md:grid-cols-2 text-sm text-slate-300">
                    <p><span className="text-slate-500">Documento:</span> {analysisData.document_id || '—'}</p>
                    <p><span className="text-slate-500">Tipo:</span> {(analysisData.doc_type || 'unknown').replace(/_/g, ' ')}</p>
                    <div className="md:col-span-2"><ConfidenceBar score={analysisData.confidence_score ?? null} /></div>
                  </div>
                </div>
              )}

              <button
                onClick={() => setActiveTab('script')}
                className="text-sm text-gray-400 hover:text-white transition-colors flex items-center gap-1"
              >
                <ChevronRight className="w-4 h-4" />
                Volver al guion
              </button>
            </div>
          ) : (
            <div className="card p-12 flex flex-col items-center justify-center gap-3 text-center">
              <Layers className="w-10 h-10 text-gray-600" />
              <div>
                <p className="text-gray-300 font-medium">Sin analisis aun</p>
                <p className="text-gray-500 text-sm mt-1">
                  Ve a la pestana Guion y pulsa "Analizar guion" para comenzar.
                </p>
              </div>
              <button
                onClick={() => setActiveTab('script')}
                className="mt-2 px-4 py-2 text-sm border border-amber-500/20 text-amber-400 rounded-xl hover:bg-amber-500/10 transition-colors"
              >
                Ir al guion
              </button>
            </div>
          )}
        </div>
      )}

      {/* ── TAB: STORYBOARD ── */}
      {activeTab === 'storyboard' && (
        <div>
          {isStoryboarding ? (
            <div className="card p-12 flex flex-col items-center justify-center gap-4 text-center">
              <svg className="animate-spin w-8 h-8 text-gray-300" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              <div>
                <p className="text-gray-300 font-medium">Generando storyboard...</p>
                <p className="text-gray-400 text-sm mt-1">Parseando escenas y sugiriendo planos</p>
              </div>
            </div>
          ) : storyboardData ? (
            <div className="space-y-3">
              {/* Stats bar */}
              <div className="flex items-center gap-4 mb-2">
                <div className="flex items-center gap-2 text-sm">
                  <Film className="w-4 h-4 text-gray-400" />
                  <span className="text-gray-300">
                    <span className="font-semibold text-white">{storyboardData.total_scenes}</span>{' '}
                    escena{storyboardData.total_scenes !== 1 ? 's' : ''} detectada{storyboardData.total_scenes !== 1 ? 's' : ''}
                  </span>
                </div>
                <div className="flex-1 h-px bg-white/10" />
              </div>

              {/* Scene cards */}
              {storyboardData.scenes.map((scene) => (
                <div key={scene.scene_number} className="card bg-dark-200/80 border border-white/5 overflow-hidden">
                  {/* Scene header */}
                  <div className="px-5 py-4 border-b border-white/5 bg-white/[0.02]">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 text-xs font-bold">
                            ESC {String(scene.scene_number).padStart(2, '0')}
                          </span>
                          {scene.time_of_day && (
                            <span className="px-2 py-0.5 rounded bg-white/5 text-gray-400 text-xs flex items-center gap-1">
                              <Clock className="w-3 h-3" />
                              {scene.time_of_day}
                            </span>
                          )}
                        </div>
                        <h4 className="text-white font-mono text-sm font-semibold">
                          {scene.heading}
                        </h4>
                        {scene.location && (
                          <div className="flex items-center gap-1 mt-1 text-gray-400 text-xs">
                            <MapPin className="w-3 h-3" />
                            {scene.location}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Shots */}
                  {scene.shots.length > 0 ? (
                    <div className="p-4 grid grid-cols-1 sm:grid-cols-2 gap-3">
                      {scene.shots.map((shot) => (
                        <div
                          key={shot.shot_number}
                          className="flex gap-3 p-3 bg-white/[0.03] rounded-xl border border-white/5 hover:border-white/10 transition-colors"
                        >
                          {/* Shot visual placeholder */}
                          <div className="w-16 h-16 rounded-lg bg-gradient-to-br from-gray-800 to-gray-900 border border-white/10 flex flex-col items-center justify-center flex-shrink-0 overflow-hidden relative">
                            {shot.thumbnail_url || shot.preview_url ? (
                              <img
                                src={shot.thumbnail_url || shot.preview_url || undefined}
                                alt={shot.asset_file_name || `Storyboard ${shot.shot_number}`}
                                className="absolute inset-0 w-full h-full object-cover"
                              />
                            ) : null}
                            <div className="relative z-10 bg-black/45 px-1.5 py-1 rounded-md text-center">
                              <span className="text-[10px] font-bold text-gray-200 leading-none block">
                                {shot.shot_type}
                              </span>
                              <span className="text-[9px] text-gray-300 mt-0.5 block">
                                #{shot.shot_number}
                              </span>
                            </div>
                          </div>
                          {/* Shot details */}
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-1.5">
                              <ShotTypeBadge type={shot.shot_type} />
                              <span className="text-gray-500 text-xs">#{shot.shot_number}</span>
                            </div>
                            <p className="text-gray-300 text-xs leading-relaxed line-clamp-2">
                              {shot.description}
                            </p>
                            {(shot.preview_url || shot.thumbnail_url) && (
                              <a
                                href={shot.preview_url || shot.thumbnail_url || undefined}
                                target="_blank"
                                rel="noreferrer"
                                className="mt-2 inline-flex text-[11px] text-amber-300 hover:text-amber-200"
                              >
                                Ver imagen
                              </a>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="p-6 text-center">
                      <p className="text-gray-500 text-sm">Sin planos detectados en esta escena.</p>
                    </div>
                  )}
                </div>
              ))}

              <button
                onClick={() => setActiveTab('script')}
                className="text-sm text-gray-400 hover:text-white transition-colors flex items-center gap-1"
              >
                <ChevronRight className="w-4 h-4" />
                Volver al guion
              </button>
            </div>
          ) : (
            <div className="card p-12 flex flex-col items-center justify-center gap-3 text-center">
              <Eye className="w-10 h-10 text-gray-600" />
              <div>
                <p className="text-gray-300 font-medium">Sin storyboard aun</p>
                <p className="text-gray-500 text-sm mt-1">
                  Ve a la pestana Guion y pulsa "Generar storyboard" para comenzar.
                </p>
              </div>
              <button
                onClick={() => setActiveTab('script')}
                className="mt-2 px-4 py-2 text-sm border border-white/10 text-gray-300 rounded-xl hover:bg-white/5 transition-colors"
              >
                Ir al guion
              </button>
            </div>
          )}
        </div>
      )}

      {/* ── TAB: CONCEPT ART ── */}
      {activeTab === 'concept-art' && (
        <ConceptArtDryRunPanel projectId={projectId!} />
      )}

      {/* ── TAB: HISTORIAL ── */}
      {activeTab === 'history' && (
        <div>
          {(jobsLoading || jobs.length === 0) && !jobsLoading ? (
            <div className="card p-12 flex flex-col items-center justify-center gap-4 text-center">
              <History className="w-10 h-10 text-gray-600" />
              <div>
                <p className="text-gray-300 font-medium">
                  {jobsLoading ? 'Cargando historial...' : 'Sin historial de operaciones'}
                </p>
                <p className="text-gray-500 text-sm mt-1">
                  Las operaciones de analisis y storyboard apareceran aqui.
                </p>
              </div>
              {!jobsLoading && (
                <button
                  onClick={loadJobs}
                  className="mt-2 px-4 py-2 text-sm border border-white/10 text-gray-300 rounded-xl hover:bg-white/5 transition-colors"
                >
                  Actualizar
                </button>
              )}
            </div>
          ) : (
            <div className="space-y-3">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <History className="w-4 h-4 text-gray-400" />
                  <span className="text-gray-300 text-sm font-medium">
                    {jobs.length} operacion{jobs.length !== 1 ? 'es' : ''}
                  </span>
                </div>
                <button
                  onClick={loadJobs}
                  className="text-xs text-gray-500 hover:text-gray-300 transition-colors"
                >
                  Actualizar
                </button>
              </div>

              {jobs.map((job) => {
                const isRetrying = retryingJobId === job.id
                const isFailed = job.status === 'failed'
                const isPending = job.status === 'pending'
                const isProcessing = job.status === 'processing'
                const isCompleted = job.status === 'completed'
                const isDone = isCompleted || isFailed

                const jobLabel = job.job_type === 'analyze' ? 'Analisis' : 'Storyboard'
                const jobIcon = job.job_type === 'analyze' ? (
                  <Sparkles className="w-4 h-4 text-amber-400" />
                ) : (
                  <Eye className="w-4 h-4 text-gray-400" />
                )

                const statusColor = isCompleted
                  ? 'bg-green-500/10 text-green-400 border-green-500/20'
                  : isFailed
                  ? 'bg-red-500/10 text-red-400 border-red-500/20'
                  : isProcessing
                  ? 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                  : 'bg-white/5 text-gray-400 border-white/10'

                const statusIcon = isCompleted ? (
                  <CheckCircle2 className="w-3.5 h-3.5" />
                ) : isFailed ? (
                  <AlertCircle className="w-3.5 h-3.5" />
                ) : isProcessing ? (
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                ) : (
                  <History className="w-3.5 h-3.5" />
                )

                const statusLabel = isCompleted ? 'Completado'
                  : isFailed ? 'Fallido'
                  : isProcessing ? 'Procesando'
                  : isPending ? 'Pendiente'
                  : job.status

                const when = job.completed_at || job.created_at
                const dateStr = when
                  ? new Date(when).toLocaleString('es-ES', {
                      day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit',
                    })
                  : '—'

                return (
                  <div key={job.id} className="card bg-dark-200/80 border border-white/5 p-4">
                    <div className="flex items-start gap-3">
                      <div className="w-9 h-9 rounded-xl bg-white/5 flex items-center justify-center flex-shrink-0 mt-0.5">
                        {jobIcon}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between gap-3">
                          <div>
                            <div className="flex items-center gap-2 mb-1">
                              <span className="text-white text-sm font-medium">{jobLabel}</span>
                              <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-lg text-xs border ${statusColor}`}>
                                {statusIcon}
                                {statusLabel}
                              </span>
                            </div>
                            <p className="text-gray-500 text-xs">
                              {dateStr}
                              {isDone && job.completed_at && job.created_at && (
                                <> · {(new Date(job.completed_at).getTime() - new Date(job.created_at).getTime()) / 1000 < 60
                                  ? `${Math.round((new Date(job.completed_at).getTime() - new Date(job.created_at).getTime()) / 1000)}s`
                                  : `${Math.round((new Date(job.completed_at).getTime() - new Date(job.created_at).getTime()) / 60000)}m`}
                                </>
                              )}
                            </p>
                          </div>
                          {(isProcessing || isPending) && (
                            <JobProgress
                              progress_percent={job.progress_percent}
                              progress_stage={job.progress_stage}
                              status={job.status}
                              job_type={job.job_type}
                            />
                          )}
                          {job.error_message && (
                            <p className="mt-2 text-xs text-red-400 bg-red-500/10 p-2 rounded">
                              {job.error_message}
                            </p>
                          )}
                          <div className="flex items-center gap-2 flex-shrink-0">
                            {isDone && (
                              <button
                                onClick={() => {
                                  setRetryingJobId(job.id)
                                  projectsApi.retryJob(projectId!, job.id)
                                    .then((updated) => {
                                      setJobs(prev => prev.map(j => j.id === updated.id ? updated as unknown as ProjectJob : j))
                                      if (updated.job_type === 'analyze') {
                                        setActiveTab('analysis')
                                        setAnalysisData({
                                          source: 'document',
                                          document_id: String((updated.result_data as unknown as { document_id?: string })?.document_id || ''),
                                          doc_type: String((updated.result_data as unknown as { doc_type?: string })?.doc_type || ''),
                                          confidence_score: (updated.result_data as unknown as { confidence_score?: number })?.confidence_score ?? null,
                                          structured_payload: (updated.result_data as unknown as { structured_payload?: Record<string, unknown> })?.structured_payload ?? {},
                                        })
                                      } else {
                                        setActiveTab('storyboard')
                                        const sbData = updated.result_data as unknown as {
                                          total_scenes?: number; scenes?: Scene[]
                                        }
                                        setStoryboardData({
                                          project_id: projectId!,
                                          total_scenes: sbData?.total_scenes ?? 0,
                                          scenes: sbData?.scenes ?? [],
                                        })
                                      }
                                    })
                                    .catch(() => setError('Error al reintentar'))
                                    .finally(() => setRetryingJobId(null))
                                }}
                                disabled={isRetrying || isProcessing}
                                className="px-3 py-1.5 text-xs border border-amber-500/20 text-amber-400 rounded-lg hover:bg-amber-500/10 transition-colors disabled:opacity-40 flex items-center gap-1.5"
                              >
                                {isRetrying ? (
                                  <Loader2 className="w-3 h-3 animate-spin" />
                                ) : (
                                  <RefreshCw className="w-3 h-3" />
                                )}
                                Reintentar
                              </button>
                            )}
                          </div>
                        </div>
                        {isFailed && job.error_message && (
                          <p className="text-red-400/70 text-xs mt-2 bg-red-500/5 border border-red-500/10 rounded-lg px-3 py-2">
                            {job.error_message}
                          </p>
                        )}
                        {isCompleted && job.result_data && (() => {
                          const rd = job.result_data as unknown as {
                            doc_type?: string; confidence_score?: number; total_scenes?: number
                          }
                          return (
                            <div className="flex items-center gap-4 mt-2">
                              {rd.doc_type && (
                                <span className="text-xs text-gray-400">
                                  Tipo: <span className="text-gray-300 capitalize">{rd.doc_type.replace(/_/g, ' ')}</span>
                                </span>
                              )}
                              {rd.confidence_score != null && (
                                <span className="text-xs text-gray-400">
                                  Confianza: <span className="text-gray-300">{Math.round(rd.confidence_score * 100)}%</span>
                                </span>
                              )}
                              {rd.total_scenes != null && (
                                <span className="text-xs text-gray-400">
                                  Escenas: <span className="text-gray-300">{rd.total_scenes}</span>
                                </span>
                              )}
                            </div>
                          )
                        })()}
                        {job.history && job.history.length > 0 && (
                          <div className="mt-3 pt-3 border-t border-white/5">
                            <p className="text-xs text-gray-500 mb-2 flex items-center gap-1.5">
                              <Clock className="w-3 h-3" />
                              Linea de tiempo
                            </p>
                            <div className="flex flex-wrap gap-2">
                              {job.history.map((entry, idx) => {
                                const time = entry.created_at
                                  ? new Date(entry.created_at).toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })
                                  : '—'
                                const eventIcon = entry.event_type === 'job_created'
                                  ? <Sparkles className="w-3 h-3" />
                                  : entry.event_type === 'job_running'
                                  ? <Loader2 className="w-3 h-3 animate-spin" />
                                  : entry.event_type === 'job_succeeded'
                                  ? <CheckCircle2 className="w-3 h-3" />
                                  : entry.event_type === 'job_failed'
                                  ? <AlertCircle className="w-3 h-3" />
                                  : entry.event_type === 'job_retry_requested'
                                  ? <RefreshCw className="w-3 h-3" />
                                  : <History className="w-3 h-3" />
                                const eventLabel = entry.event_type.replace(/_/g, ' ')
                                return (
                                  <div key={entry.id || idx} className="flex items-center gap-1.5 px-2 py-1 bg-white/5 rounded-lg border border-white/5">
                                    <span className="text-gray-500">{eventIcon}</span>
                                    <span className="text-xs text-gray-400 capitalize">{eventLabel}</span>
                                    <span className="text-gray-600 text-xs">·</span>
                                    <span className="text-xs text-gray-500">{time}</span>
                                  </div>
                                )
                              })}
                            </div>
                          </div>
                        )}
                        {job.assets && job.assets.length > 0 && (
                          <div className="mt-3 pt-3 border-t border-white/5">
                            <p className="text-xs text-gray-500 mb-2 flex items-center gap-1.5">
                              <FileJson className="w-3 h-3" />
                              Assets del job
                            </p>
                            <div className="flex flex-wrap gap-2">
                              {job.assets.map((asset, idx) => (
                                <div key={asset.id || idx} className="flex items-center gap-1.5 px-2 py-1 bg-amber-500/5 rounded-lg border border-amber-500/10">
                                  <FileJson className="w-3 h-3 text-amber-400" />
                                  <span className="text-xs text-gray-300">{asset.file_name}</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                )
              })}

            {/* ── ASSETS ── */}
            <div className="mt-6 pt-6 border-t border-white/10">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <FolderOpen className="w-4 h-4 text-gray-400" />
                  <span className="text-gray-300 text-sm font-medium">
                    Assets generados
                  </span>
                  {assetsLoading && (
                    <Loader2 className="w-3 h-3 animate-spin text-gray-500" />
                  )}
                </div>
                {assets.length > 0 && (
                  <div className="flex items-center gap-1">
                    <button
                      onClick={() => setViewMode('list')}
                      className={`px-2 py-1 rounded text-xs ${viewMode === 'list' ? 'bg-amber-500/20 text-amber-400' : 'text-gray-500 hover:text-gray-400'}`}
                    >
                      Lista
                    </button>
                    <button
                      onClick={() => setViewMode('grid')}
                      className={`px-2 py-1 rounded text-xs ${viewMode === 'grid' ? 'bg-amber-500/20 text-amber-400' : 'text-gray-500 hover:text-gray-400'}`}
                    >
                      Grid
                    </button>
                    <button
                      onClick={() => setViewMode('presentation')}
                      className={`px-2 py-1 rounded text-xs ${viewMode === 'presentation' ? 'bg-amber-500/20 text-amber-400' : 'text-gray-500 hover:text-gray-400'}`}
                    >
                      Presentacion
                    </button>
                  </div>
                )}
              </div>

              {assets.length === 0 && !assetsLoading ? (
                <p className="text-gray-600 text-xs text-center py-4">
                  No hay assets generados aun.
                </p>
              ) : viewMode === 'grid' ? (
                /* GRID VIEW BY SEQUENCE */
                <div className="space-y-4">
                  {Object.keys(assetsBySequence).sort().map(seqId => {
                    const seqAssets = assetsBySequence[seqId]
                    return (
                      <div key={seqId} className="card bg-dark-200/80 border border-white/5 overflow-hidden">
                        <div className="px-4 py-2 bg-white/[0.02] border-b border-white/5">
                          <div className="flex items-center gap-2">
                            <Film className="w-4 h-4 text-amber-400" />
                            <span className="text-amber-300 font-semibold text-sm">
                              Secuencia {seqId.toUpperCase()}
                            </span>
                            <span className="text-gray-500 text-xs">
                              ({seqAssets.length} shot{seqAssets.length !== 1 ? 's' : ''})
                            </span>
                          </div>
                        </div>
                        <div className="p-3 grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
                          {seqAssets.map((asset) => {
                            const meta = asset.metadata_json as Record<string, unknown> | null
                            const visualMode = (meta?.visual_mode as string) || 'unknown'
                            const shotOrder = (meta?.shot_order as number) || '?'
                            const shotType = (meta?.shot_type as string) || 'unknown'
                            const isPremium = visualMode === 'flux'
                            // Use centralized thumbnail resolution
                            const thumbnailUrl = isComfyAsset(asset.asset_source) && asset.file_name
                              ? getThumbnailUrl(asset.file_name)
                              : null
                            return (
                              <div
                                key={asset.id}
                                className="relative aspect-video bg-white/5 rounded-lg border border-white/5 overflow-hidden group"
                              >
                                {thumbnailUrl ? (
                                  <img
                                    src={thumbnailUrl}
                                    alt={`Shot ${shotOrder}`}
                                    className="absolute inset-0 w-full h-full object-cover"
                                    onError={(e) => {
                                      // Fallback on error
                                      e.currentTarget.style.display = 'none'
                                    }}
                                  />
                                ) : (
                                  <div className="absolute inset-0 flex items-center justify-center">
                                    <FileJson className="w-8 h-8 text-gray-600" />
                                  </div>
                                )}
                                <div className="absolute bottom-0 left-0 right-0 p-2 bg-gradient-to-t from-black/80 to-transparent">
                                  <p className="text-white text-xs font-medium truncate">
                                    Shot {shotOrder}
                                  </p>
                                  <div className="flex items-center gap-1 mt-0.5">
                                    <span className={`px-1.5 py-0.5 rounded text-[10px] ${isPremium ? 'bg-purple-500/20 text-purple-400' : 'bg-amber-500/20 text-amber-400'}`}>
                                      {isPremium ? 'Premium' : 'Realistic'}
                                    </span>
                                    <span className="text-gray-500 text-[10px] capitalize">
                                      {shotType}
                                    </span>
                                  </div>
                                </div>
                              </div>
                            )
                          })}
                        </div>
                      </div>
                    )
                  })}
                </div>
              ) : viewMode === 'presentation' ? (
                /* PRESENTATION VIEW - One sequence per page/grid */
                <div className="space-y-6">
                  {Object.keys(assetsBySequence).sort().map(seqId => {
                    const seqAssets = assetsBySequence[seqId]
                    const seqModes = [...new Set(seqAssets.map(a => {
                      const meta = a.metadata_json as Record<string, unknown> | null
                      return (meta?.visual_mode as string) || 'unknown'
                    }))]
                    return (
                      <div key={seqId} className="bg-dark-100 rounded-xl border border-white/10 overflow-hidden">
                        <div className="px-6 py-4 bg-gradient-to-r from-amber-500/10 to-transparent border-b border-white/10">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                              <Film className="w-5 h-5 text-amber-400" />
                              <div>
                                <h3 className="text-lg font-semibold text-white">
                                  Secuencia {seqId.toUpperCase()}
                                </h3>
                                <p className="text-sm text-gray-400">
                                  {seqAssets.length} shot{seqAssets.length !== 1 ? 's' : ''} · {seqModes.includes('flux') ? 'Premium' : 'Realistic'}
                                </p>
                              </div>
                            </div>
<div className="flex items-center gap-2">
          <Link
            to={`/projects/${projectId}/dashboard`}
            className="btn-secondary"
          >
            Dashboard
          </Link>
                              {seqModes.includes('flux') && (
                                <span className="px-2 py-1 rounded bg-purple-500/20 text-purple-400 text-xs">
                                  Premium
                                </span>
                              )}
                              {seqModes.includes('realistic') && (
                                <span className="px-2 py-1 rounded bg-amber-500/20 text-amber-400 text-xs">
                                  Realistic
                                </span>
                              )}
                            </div>
                          </div>
                        </div>
                        <div className="p-6">
                          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
                            {seqAssets.map((asset) => {
                              const meta = asset.metadata_json as Record<string, unknown> | null
                              const shotOrder = (meta?.shot_order as number) || '?'
                              const shotType = (meta?.shot_type as string) || 'unknown'
                              const promptSummary = (meta?.prompt_summary as string) || ''
                              const isPremium = (meta?.visual_mode as string) === 'flux'
                              // Use centralized thumbnail resolution
                              const thumbnailUrl = isComfyAsset(asset.asset_source) && asset.file_name
                                ? getThumbnailUrl(asset.file_name)
                                : null
                              return (
                                <div
                                  key={asset.id}
                                  className="group"
                                >
                                  <div className="relative aspect-[16/9] bg-dark-200 rounded-lg border border-white/10 overflow-hidden mb-2">
                                    {thumbnailUrl ? (
                                      <img
                                        src={thumbnailUrl}
                                        alt={`Shot ${shotOrder}`}
                                        className="absolute inset-0 w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                                        onError={(e) => {
                                          e.currentTarget.style.display = 'none'
                                        }}
                                      />
                                    ) : (
                                      <div className="absolute inset-0 flex items-center justify-center">
                                        <FileJson className="w-8 h-8 text-gray-600" />
                                      </div>
                                    )}
                                    <div className="absolute top-2 left-2 px-2 py-1 rounded bg-black/60 text-white text-xs font-medium">
                                      {shotOrder}
                                    </div>
                                    {isPremium && (
                                      <div className="absolute top-2 right-2 px-2 py-1 rounded bg-purple-500/80 text-white text-[10px]">
                                        PREM
                                      </div>
                                    )}
                                  </div>
                                  <div className="space-y-1">
                                    <p className="text-sm font-medium text-white capitalize">
                                      {shotType}
                                    </p>
                                    {promptSummary && (
                                      <p className="text-xs text-gray-500 line-clamp-2" title={promptSummary}>
                                        {promptSummary}
                                      </p>
                                    )}
                                  </div>
                                </div>
                              )
                            })}
                          </div>
                        </div>
                      </div>
                    )
                  })}
                </div>
              ) : (
                /* LIST VIEW */
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {assets.map((asset) => {
                    const meta = asset.metadata_json as Record<string, unknown> | null
                    const visualMode = (meta?.visual_mode as string) || 'unknown'
                    const seqId = (meta?.sequence_id as string) || 'sin-seq'
                    const isAnalysis = asset.asset_source === 'script_analysis'
                    const isStoryboard = asset.asset_source === 'script_storyboard'
                    const sourceLabel = isAnalysis ? 'Analisis' : isStoryboard ? 'Storyboard' : asset.asset_source || 'Asset'
                    const sourceColor = isAnalysis ? 'text-amber-400' : isStoryboard ? 'text-blue-400' : 'text-gray-400'
                    const isPremium = visualMode === 'flux'
                    const dateStr = asset.created_at
                      ? new Date(asset.created_at).toLocaleString('es-ES', {
                          day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit',
                        })
                      : '—'
                    return (
                      <div
                        key={asset.id}
                        className="flex items-center gap-3 p-3 bg-white/[0.03] rounded-xl border border-white/5 hover:border-white/10 transition-colors"
                      >
                        <div className="w-9 h-9 rounded-lg bg-white/5 flex items-center justify-center flex-shrink-0">
                          <FileJson className="w-4 h-4 text-gray-400" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-white text-xs font-medium truncate">{asset.file_name}</p>
                          <div className="flex items-center gap-2 mt-0.5">
                            <span className="text-gray-600 text-xs">{seqId}</span>
                            <span className="text-gray-600 text-xs">·</span>
                            <span className={`text-xs ${isPremium ? 'text-purple-400' : sourceColor}`}>
                              {isPremium ? 'Premium' : sourceLabel}
                            </span>
                            <span className="text-gray-600 text-xs">·</span>
                            <span className="text-gray-500 text-xs">{dateStr}</span>
                          </div>
                        </div>
                        <span className="px-2 py-0.5 rounded bg-white/5 text-gray-500 text-xs flex-shrink-0">
                          {asset.file_extension}
                        </span>
                      </div>
                    )
                  })}
                </div>
              )}
            </div>
            </div>
          )}
        </div>
      )}

      <StoryboardSequenceSelectorModal
        open={storyboardModalOpen}
        isLoading={isLoadingStoryboardCandidates}
        error={storyboardCandidateError}
        scenes={storyboardCandidates}
        sequences={storyboardSequences}
        onClose={() => setStoryboardModalOpen(false)}
        onConfirm={confirmGenerateStoryboardSelection}
      />
    </div>
  )
}
