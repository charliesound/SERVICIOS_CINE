import { useState } from 'react'
import { conceptArtApi } from '@/api/conceptArt'
import type { ConceptArtDryRunResponse } from '@/types/conceptArt'
import {
  Sparkles, Loader2, CheckCircle2, AlertCircle, Eye,
  Monitor, Hash, Layers, Cpu,
} from 'lucide-react'

type Mode = 'concept_art' | 'key_visual'
type Phase = 'idle' | 'validating' | 'resolving' | 'compiling' | 'validating_ph' | 'done' | 'error'

interface Props {
  projectId: string
}

const PHASE_LABELS: Record<Phase, string> = {
  idle: '',
  validating: 'Validando proyecto',
  resolving: 'Resolviendo modelos Flux',
  compiling: 'Compilando workflow',
  validating_ph: 'Validando placeholders',
  done: 'Listo para ComfyUI',
  error: 'Error',
}

export default function ConceptArtDryRunPanel({ projectId }: Props) {
  const [mode, setMode] = useState<Mode>('concept_art')
  const [prompt, setPrompt] = useState('')
  const [negativePrompt, setNegativePrompt] = useState('')
  const [width, setWidth] = useState(1344)
  const [height, setHeight] = useState(768)
  const [steps, setSteps] = useState(28)
  const [cfg, setCfg] = useState(3.5)
  const [seed, setSeed] = useState(0)
  const [phase, setPhase] = useState<Phase>('idle')
  const [phasePercent, setPhasePercent] = useState(0)
  const [result, setResult] = useState<ConceptArtDryRunResponse | null>(null)
  const [errorMsg, setErrorMsg] = useState('')

  const reset = () => {
    setPhase('idle')
    setPhasePercent(0)
    setResult(null)
    setErrorMsg('')
  }

  const runPhases = async () => {
    reset()
    const payload = {
      prompt: prompt.trim(),
      negative_prompt: negativePrompt.trim() || undefined,
      width,
      height,
      steps,
      cfg,
      seed,
    }

    setPhase('validating')
    setPhasePercent(10)
    await sleep(400)

    setPhase('resolving')
    setPhasePercent(30)
    await sleep(400)

    setPhase('compiling')
    setPhasePercent(55)
    await sleep(400)

    setPhase('validating_ph')
    setPhasePercent(80)
    await sleep(400)

    try {
      const fn = mode === 'concept_art'
        ? conceptArtApi.compileProjectConceptArtWorkflowDryRun
        : conceptArtApi.compileProjectKeyVisualWorkflowDryRun
      const response = await fn(projectId, payload)
      setResult(response)
      setPhase('done')
      setPhasePercent(100)
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail
      setErrorMsg(typeof detail === 'string' ? detail : 'Error al preparar el workflow')
      setPhase('error')
      setPhasePercent(0)
    }
  }

  const PhaseIcon = () => {
    if (phase === 'done') return <CheckCircle2 className="w-4 h-4 text-emerald-400" />
    if (phase === 'error') return <AlertCircle className="w-4 h-4 text-red-400" />
    return <Loader2 className="w-4 h-4 animate-spin text-amber-400" />
  }

  return (
    <div className="space-y-4">
      {/* Mode selector */}
      <div className="card bg-dark-200/80 border border-white/5 p-6">
        <div className="flex items-center gap-3 mb-5">
          <div className="w-10 h-10 rounded-xl bg-purple-500/10 flex items-center justify-center">
            <Sparkles className="w-5 h-5 text-purple-400" />
          </div>
          <div>
            <h3 className="font-semibold">Concept Art / Key Visual</h3>
            <p className="text-gray-400 text-xs">Dry-run con Flux. No se ejecuta render real.</p>
          </div>
        </div>

        <div className="flex gap-2 mb-5">
          <button
            type="button"
            onClick={() => { setMode('concept_art'); reset() }}
            className={`px-4 py-2 text-sm rounded-xl transition-colors ${
              mode === 'concept_art'
                ? 'bg-purple-500/20 text-purple-300 border border-purple-500/30'
                : 'bg-white/5 text-gray-400 border border-white/10 hover:border-white/20'
            }`}
          >
            <Sparkles className="w-4 h-4 inline mr-1.5" />
            Concept Art
          </button>
          <button
            type="button"
            onClick={() => { setMode('key_visual'); reset() }}
            className={`px-4 py-2 text-sm rounded-xl transition-colors ${
              mode === 'key_visual'
                ? 'bg-purple-500/20 text-purple-300 border border-purple-500/30'
                : 'bg-white/5 text-gray-400 border border-white/10 hover:border-white/20'
            }`}
          >
            <Eye className="w-4 h-4 inline mr-1.5" />
            Key Visual
          </button>
        </div>

        {/* Prompts */}
        <div className="space-y-3 mb-4">
          <div>
            <label className="text-xs text-gray-400 mb-1 block">Prompt positivo</label>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="cinematic key visual, detective in neon alley, anamorphic lighting"
              rows={3}
              className="input w-full resize-y text-sm"
              disabled={phase !== 'idle' && phase !== 'error'}
            />
          </div>
          <div>
            <label className="text-xs text-gray-400 mb-1 block">Prompt negativo</label>
            <textarea
              value={negativePrompt}
              onChange={(e) => setNegativePrompt(e.target.value)}
              placeholder="low quality, blurry, watermark"
              rows={2}
              className="input w-full resize-y text-sm"
              disabled={phase !== 'idle' && phase !== 'error'}
            />
          </div>
        </div>

        {/* Parameters */}
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mb-5">
          <div>
            <label className="text-xs text-gray-400 mb-1 block flex items-center gap-1">
              <Monitor className="w-3 h-3" /> Width
            </label>
            <input
              type="number"
              value={width}
              onChange={(e) => setWidth(Number(e.target.value))}
              className="input w-full text-sm"
              disabled={phase !== 'idle' && phase !== 'error'}
            />
          </div>
          <div>
            <label className="text-xs text-gray-400 mb-1 block flex items-center gap-1">
              <Monitor className="w-3 h-3" /> Height
            </label>
            <input
              type="number"
              value={height}
              onChange={(e) => setHeight(Number(e.target.value))}
              className="input w-full text-sm"
              disabled={phase !== 'idle' && phase !== 'error'}
            />
          </div>
          <div>
            <label className="text-xs text-gray-400 mb-1 block flex items-center gap-1">
              <Hash className="w-3 h-3" /> Steps
            </label>
            <input
              type="number"
              value={steps}
              onChange={(e) => setSteps(Number(e.target.value))}
              className="input w-full text-sm"
              disabled={phase !== 'idle' && phase !== 'error'}
            />
          </div>
          <div>
            <label className="text-xs text-gray-400 mb-1 block flex items-center gap-1">
              <Cpu className="w-3 h-3" /> CFG
            </label>
            <input
              type="number"
              step={0.5}
              value={cfg}
              onChange={(e) => setCfg(Number(e.target.value))}
              className="input w-full text-sm"
              disabled={phase !== 'idle' && phase !== 'error'}
            />
          </div>
          <div>
            <label className="text-xs text-gray-400 mb-1 block flex items-center gap-1">
              <Layers className="w-3 h-3" /> Seed
            </label>
            <input
              type="number"
              value={seed}
              onChange={(e) => setSeed(Number(e.target.value))}
              className="input w-full text-sm"
              disabled={phase !== 'idle' && phase !== 'error'}
            />
          </div>
        </div>

        {/* Action button */}
        <button
          type="button"
          onClick={runPhases}
          disabled={!prompt.trim() || (phase !== 'idle' && phase !== 'error')}
          className="w-full px-4 py-2.5 bg-purple-500/20 hover:bg-purple-500/30 text-purple-300 border border-purple-500/30 rounded-xl font-medium transition-colors text-sm flex items-center justify-center gap-2 disabled:opacity-40 disabled:cursor-not-allowed"
        >
          {phase !== 'idle' && phase !== 'error' ? (
            <><Loader2 className="w-4 h-4 animate-spin" /> Preparando...</>
          ) : (
            <><Sparkles className="w-4 h-4" /> {mode === 'concept_art' ? 'Preparar Concept Art' : 'Preparar Key Visual'}</>
          )}
        </button>
      </div>

      {/* Progress phases */}
      {phase !== 'idle' && (
        <div className="card bg-dark-200/80 border border-white/5 p-4 space-y-3">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-300 font-medium">{PHASE_LABELS[phase]}</span>
            <div className="flex items-center gap-2">
              <PhaseIcon />
              <span className="text-xs text-gray-500">{phasePercent}%</span>
            </div>
          </div>
          <div className="w-full h-2 rounded-full bg-white/10 overflow-hidden">
            <div
              className={`h-full transition-all duration-500 ${
                phase === 'error' ? 'bg-red-400' : phase === 'done' ? 'bg-emerald-400' : 'bg-purple-400'
              }`}
              style={{ width: `${phasePercent}%` }}
            />
          </div>
          <div className="grid grid-cols-5 gap-1 text-[10px] text-gray-500">
            {(['validating', 'resolving', 'compiling', 'validating_ph', 'done'] as Phase[]).map((p) => {
              const order = ['validating', 'resolving', 'compiling', 'validating_ph', 'done']
              const idx = order.indexOf(p)
              const currentIdx = order.indexOf(phase === 'error' ? 'validating' : phase)
              return (
                <div key={p} className={`text-center py-1 rounded ${
                  idx < currentIdx ? 'text-emerald-400' : idx === currentIdx ? 'text-purple-300' : 'text-gray-600'
                }`}>
                  {p === 'done' ? <CheckCircle2 className="w-3 h-3 inline" /> : <div className="w-1.5 h-1.5 rounded-full mx-auto bg-current" />}
                  <span className="block mt-0.5">{PHASE_LABELS[p]}</span>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Error */}
      {phase === 'error' && errorMsg && (
        <div className="rounded-2xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-300">
          {errorMsg}
        </div>
      )}

      {/* Result */}
      {phase === 'done' && result && (
        <div className="card bg-dark-200/80 border border-white/5 p-5 space-y-4">
          <div className="flex items-center gap-2 text-emerald-400 text-sm font-medium">
            <CheckCircle2 className="w-4 h-4" />
            Workflow compilado correctamente
          </div>

          {/* Summary */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="p-3 bg-white/5 rounded-xl">
              <p className="text-gray-500 text-xs uppercase tracking-wider">Workflow ID</p>
              <p className="text-white font-mono text-sm mt-1 break-all">{result.workflow_id}</p>
            </div>
            <div className="p-3 bg-white/5 rounded-xl">
              <p className="text-gray-500 text-xs uppercase tracking-wider">Familia</p>
              <p className="text-purple-300 font-semibold text-sm mt-1 uppercase">{result.pipeline.model_family}</p>
            </div>
            <div className="p-3 bg-white/5 rounded-xl">
              <p className="text-gray-500 text-xs uppercase tracking-wider">Safe to render</p>
              <p className={`font-semibold text-sm mt-1 ${result.pipeline.safe_to_render ? 'text-emerald-400' : 'text-red-400'}`}>
                {result.pipeline.safe_to_render ? 'Sí' : 'No'}
              </p>
            </div>
            <div className="p-3 bg-white/5 rounded-xl">
              <p className="text-gray-500 text-xs uppercase tracking-wider">Nodos</p>
              <p className="text-white font-semibold text-sm mt-1">{result.compiled_workflow_preview.validation.node_count}</p>
            </div>
          </div>

          {/* Resolved models */}
          <div>
            <p className="text-gray-400 text-xs uppercase tracking-wider mb-2 flex items-center gap-1">
              <Cpu className="w-3 h-3" /> Modelos resueltos
            </p>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
              {(['unet', 'clip_l', 't5xxl', 'vae'] as const).map((key) => {
                const value = result.pipeline[key]
                return (
                  <div key={key} className={`p-2 rounded-lg border text-xs ${value ? 'border-emerald-500/20 bg-emerald-500/5' : 'border-red-500/20 bg-red-500/5'}`}>
                    <span className="text-gray-500">{key}</span>
                    <p className={`font-mono mt-0.5 truncate ${value ? 'text-emerald-300' : 'text-red-300'}`}>
                      {value || '—'}
                    </p>
                  </div>
                )
              })}
            </div>
          </div>

          {/* Validation details */}
          <div className="flex items-center gap-2 text-xs text-gray-400">
            <span className={`px-2 py-0.5 rounded ${result.compiled_workflow_preview.validation.valid ? 'bg-emerald-500/10 text-emerald-400' : 'bg-red-500/10 text-red-400'}`}>
              Validation: {result.compiled_workflow_preview.validation.valid ? 'OK' : 'FAIL'}
            </span>
            {result.compiled_workflow_preview.validation.missing_placeholders.length > 0 && (
              <span className="text-red-400">
                Placeholders missing: {result.compiled_workflow_preview.validation.missing_placeholders.join(', ')}
              </span>
            )}
            {result.pipeline.missing_models.length > 0 && (
              <span className="text-red-400">
                Missing models: {result.pipeline.missing_models.join(', ')}
              </span>
            )}
          </div>

          {/* Warning */}
          <div className="rounded-xl border border-amber-500/20 bg-amber-500/5 px-3 py-2 text-xs text-amber-300 flex items-start gap-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
            <span>Dry-run: no se ha ejecutado render real ni se ha llamado a /prompt de ComfyUI.</span>
          </div>
        </div>
      )}
    </div>
  )
}

function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}
