import { useEffect, useMemo, useState } from 'react'
import { AlertCircle, CheckCircle2, Play, RefreshCw, Shield } from 'lucide-react'
import PipelinePromptBox from '@/components/pipeline/PipelinePromptBox'
import PipelineStageView from '@/components/pipeline/PipelineStageView'
import PipelineValidationPanel from '@/components/pipeline/PipelineValidationPanel'
import PipelineJobHistory from '@/components/pipeline/PipelineJobHistory'
import LegalGatePanel from '@/components/pipeline/LegalGatePanel'
import {
  pipelineApi,
  pipelineModeToPreset,
  type PipelineDefinition,
  type PipelineJob,
  type PipelineLegalContext,
  type PipelineMode,
  type PipelinePreset,
  type PipelineValidationResponse,
} from '@/services/pipelineApi'
import { getApiErrorMessage } from '@/utils/apiErrors'

const initialLegalState: PipelineLegalContext = {
  voice_cloning: false,
  consent: false,
  rights_declared: false,
  rights_notes: '',
}

function buildContext(mode: PipelineMode, prompt: string, legal: PipelineLegalContext): Record<string, unknown> {
  const shared: Record<string, unknown> = {
    requested_mode: mode,
    rights_declared: legal.rights_declared,
    rights_notes: legal.rights_notes || undefined,
  }

  switch (mode) {
    case 'storyboard':
    case 'image':
      return {
        ...shared,
        script_text: prompt,
        visual_style: mode === 'image' ? 'concept image development' : 'storyboard frame sequence',
      }
    case 'video':
      return {
        ...shared,
        script_text: prompt,
        target_duration_seconds: 45,
        output_goal: 'teaser_preview',
      }
    case 'dubbing':
      return {
        ...shared,
        dialogue_script: prompt,
        translated_lines: prompt,
        voice_cloning: legal.voice_cloning,
        consent: legal.consent,
      }
    case 'sound':
      return {
        ...shared,
        source_audio: 'simulated_audio_source',
        cleanup_brief: prompt,
      }
    case 'editorial':
      return {
        ...shared,
        script_text: prompt,
        output_goal: 'editorial_assembly_preview',
      }
    case 'pitch':
      return {
        ...shared,
        project_brief: prompt,
        references: ['moodboard', 'sales_hooks'],
      }
  }
}

function buildSuggestions(mode: PipelineMode, validation: PipelineValidationResponse | null): string[] {
  const suggestions: string[] = []

  if (mode === 'dubbing') {
    suggestions.push('Si activas voice cloning, marca tambien consentimiento explicito antes de ejecutar la simulacion.')
  }

  if (!validation) {
    suggestions.push('Genera el pipeline para inspeccionar fases, outputs y preset base.')
    return suggestions
  }

  if (validation.warnings.some((warning) => warning.code === 'legal.rights_missing')) {
    suggestions.push('Declara ownership o licencias para reducir warnings del Legal Gate.')
  }

  if (validation.warnings.some((warning) => warning.code === 'legal.rights_notes_missing')) {
    suggestions.push('Anade notas de derechos para dejar trazabilidad del material fuente.')
  }

  if (!validation.valid) {
    suggestions.push('Corrige bloqueos y vuelve a validar antes de ejecutar la simulacion.')
  }

  if (validation.valid && suggestions.length === 0) {
    suggestions.push('El pipeline esta listo para una ejecucion simulated y revision del historial de jobs.')
  }

  return suggestions
}

function getPipelineErrorDetail(error: unknown): PipelineValidationResponse | null {
  const response = error as {
    response?: {
      data?: {
        detail?: unknown
      }
    }
  }
  const detail = response?.response?.data?.detail
  if (!detail || typeof detail !== 'object' || !('validation' in detail)) {
    return null
  }
  const validation = (detail as { validation?: unknown }).validation
  if (!validation || typeof validation !== 'object') {
    return null
  }
  return validation as PipelineValidationResponse
}

function getPipelineErrorMessage(error: unknown, fallback: string): string {
  const response = error as {
    response?: {
      data?: {
        detail?: unknown
      }
    }
  }
  const detail = response?.response?.data?.detail
  if (detail && typeof detail === 'object' && 'message' in detail) {
    const message = (detail as { message?: unknown }).message
    if (typeof message === 'string' && message.trim()) {
      return message
    }
  }
  return getApiErrorMessage(error, fallback)
}

export default function CIDPipelineBuilderPage() {
  const [prompt, setPrompt] = useState('')
  const [mode, setMode] = useState<PipelineMode>('storyboard')
  const [projectId, setProjectId] = useState('')
  const [legal, setLegal] = useState<PipelineLegalContext>(initialLegalState)
  const [presets, setPresets] = useState<PipelinePreset[]>([])
  const [pipeline, setPipeline] = useState<PipelineDefinition | null>(null)
  const [validation, setValidation] = useState<PipelineValidationResponse | null>(null)
  const [jobs, setJobs] = useState<PipelineJob[]>([])
  const [isGenerating, setIsGenerating] = useState(false)
  const [isValidating, setIsValidating] = useState(false)
  const [isExecuting, setIsExecuting] = useState(false)
  const [isJobsLoading, setIsJobsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  const normalizedProjectId = projectId.trim() || undefined
  const selectedPreset = useMemo(
    () => presets.find((preset) => preset.key === pipelineModeToPreset[mode]) || null,
    [mode, presets]
  )
  const suggestions = useMemo(() => buildSuggestions(mode, validation), [mode, validation])

  const loadJobs = async () => {
    setIsJobsLoading(true)
    try {
      const response = await pipelineApi.listJobs(normalizedProjectId)
      setJobs(response.jobs)
    } catch (loadError) {
      setError(getPipelineErrorMessage(loadError, 'No se pudo cargar el historial de jobs simulated.'))
    } finally {
      setIsJobsLoading(false)
    }
  }

  useEffect(() => {
    let mounted = true

    const loadInitialState = async () => {
      try {
        const [presetResponse, jobsResponse] = await Promise.all([
          pipelineApi.listPresets(),
          pipelineApi.listJobs(),
        ])
        if (!mounted) return
        setPresets(presetResponse.presets)
        setJobs(jobsResponse.jobs)
      } catch (loadError) {
        if (!mounted) return
        setError(getPipelineErrorMessage(loadError, 'No se pudo inicializar CID Pipeline Builder.'))
      }
    }

    void loadInitialState()
    return () => {
      mounted = false
    }
  }, [])

  const handleModeChange = (nextMode: PipelineMode) => {
    setMode(nextMode)
    setSuccess(null)
    if (nextMode !== 'dubbing') {
      setLegal((current) => ({
        ...current,
        voice_cloning: false,
        consent: false,
      }))
    }
  }

  const handleGenerate = async () => {
    setIsGenerating(true)
    setError(null)
    setSuccess(null)

    try {
      const response = await pipelineApi.generate({
        intent: prompt,
        preset_key: pipelineModeToPreset[mode],
        title: undefined,
        project_id: normalizedProjectId,
        context: buildContext(mode, prompt, legal),
        legal,
      })
      setPipeline(response.pipeline)
      setValidation(response.validation)
      setSuccess('Pipeline generated in simulated mode.')
    } catch (generateError) {
      setError(getPipelineErrorMessage(generateError, 'No se pudo generar el pipeline simulated.'))
    } finally {
      setIsGenerating(false)
    }
  }

  const handleValidate = async () => {
    if (!pipeline) {
      setError('Genera un pipeline antes de validar.')
      return
    }

    setIsValidating(true)
    setError(null)
    setSuccess(null)
    try {
      const response = await pipelineApi.validate({
        pipeline: {
          ...pipeline,
          project_id: normalizedProjectId || pipeline.project_id || undefined,
          legal,
        },
        project_id: normalizedProjectId,
      })
      setValidation(response)
      setSuccess(response.valid ? 'Pipeline validated successfully.' : 'La validacion detecto ajustes pendientes.')
    } catch (validateError) {
      setError(getPipelineErrorMessage(validateError, 'No se pudo validar el pipeline.'))
    } finally {
      setIsValidating(false)
    }
  }

  const handleExecute = async () => {
    if (!pipeline) {
      setError('Genera un pipeline antes de ejecutar la simulacion.')
      return
    }

    setIsExecuting(true)
    setError(null)
    setSuccess(null)
    try {
      const response = await pipelineApi.execute({
        pipeline: {
          ...pipeline,
          project_id: normalizedProjectId || pipeline.project_id || undefined,
          legal,
        },
        project_id: normalizedProjectId,
      })
      setJobs((current) => [response.job, ...current.filter((job) => job.job_id !== response.job.job_id)])
      setValidation(response.job.validation)
      setSuccess('Simulacion ejecutada. El job se ha encolado en memoria.')
    } catch (executeError) {
      const validationDetail = getPipelineErrorDetail(executeError)
      if (validationDetail) {
        setValidation(validationDetail)
      }
      setError(getPipelineErrorMessage(executeError, 'No se pudo ejecutar la simulacion del pipeline.'))
    } finally {
      setIsExecuting(false)
    }
  }

  return (
    <div className="space-y-8">
      <PipelinePromptBox
        prompt={prompt}
        mode={mode}
        projectId={projectId}
        selectedPresetName={selectedPreset?.name || 'Preset simulated'}
        isGenerating={isGenerating}
        onPromptChange={setPrompt}
        onModeChange={handleModeChange}
        onProjectIdChange={setProjectId}
        onGenerate={handleGenerate}
      />

      <LegalGatePanel mode={mode} legal={legal} onChange={setLegal} />

      {(error || success) ? (
        <section className="grid gap-4 lg:grid-cols-2">
          {error ? (
            <div className="rounded-2xl border border-red-500/20 bg-red-500/10 p-4 text-sm text-red-100">
              <div className="flex items-start gap-3">
                <AlertCircle className="mt-0.5 h-4 w-4" />
                <p>{error}</p>
              </div>
            </div>
          ) : null}
          {success ? (
            <div className="rounded-2xl border border-green-500/20 bg-green-500/10 p-4 text-sm text-green-100">
              <div className="flex items-start gap-3">
                <CheckCircle2 className="mt-0.5 h-4 w-4" />
                <p>{success}</p>
              </div>
            </div>
          ) : null}
        </section>
      ) : null}

      <section className="grid gap-8 xl:grid-cols-[1.3fr_0.7fr]">
        <PipelineStageView pipeline={pipeline} />

        <div className="card card-hover flex flex-col justify-between gap-6 bg-[linear-gradient(180deg,rgba(14,23,39,0.96),rgba(8,15,28,0.98))]">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full border border-amber-400/15 bg-amber-400/10 px-3 py-1 text-xs font-medium uppercase tracking-[0.2em] text-amber-100">
              <Shield className="h-3.5 w-3.5" />
              Review Gate
            </div>
            <h2 className="mt-4 heading-md">Valida y ejecuta</h2>
            <p className="mt-2 text-sm leading-6 text-slate-400">
              Revisa la estructura del pipeline, confirma el Legal Gate y lanza una ejecucion simulated aislada del motor real.
            </p>

            <div className="mt-6 rounded-[1.5rem] border border-white/8 bg-white/[0.03] p-4 text-sm text-slate-300">
              <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Estado actual</p>
              <div className="mt-3 space-y-2">
                <p>Pipeline: <span className="font-medium text-white">{pipeline?.pipeline_id || 'pendiente'}</span></p>
                <p>Validacion: <span className="font-medium text-white">{validation ? (validation.valid ? 'valida' : validation.blocked ? 'bloqueada' : 'con warnings') : 'sin ejecutar'}</span></p>
                <p>Proyecto: <span className="font-medium text-white">{normalizedProjectId || pipeline?.project_id || 'scope general'}</span></p>
              </div>
            </div>
          </div>

          <div className="grid gap-3">
            <button type="button" onClick={handleValidate} disabled={!pipeline || isValidating} className="btn-secondary flex items-center justify-center gap-2">
              <RefreshCw className={`h-4 w-4 ${isValidating ? 'animate-spin' : ''}`} />
              {isValidating ? 'Validando...' : 'Validar'}
            </button>
            <button type="button" onClick={handleExecute} disabled={!pipeline || isExecuting} className="btn-primary flex items-center justify-center gap-2">
              <Play className="h-4 w-4" />
              {isExecuting ? 'Ejecutando simulacion...' : 'Ejecutar simulacion'}
            </button>
          </div>
        </div>
      </section>

      <PipelineValidationPanel validation={validation} suggestions={suggestions} />

      <PipelineJobHistory jobs={jobs} isLoading={isJobsLoading} onRefresh={() => { void loadJobs() }} />
    </div>
  )
}
