import { Layers3, Sparkles } from 'lucide-react'
import type { PipelineMode } from '@/services/pipelineApi'

interface PipelinePromptBoxProps {
  prompt: string
  mode: PipelineMode
  projectId: string
  selectedPresetName: string
  isGenerating: boolean
  onPromptChange: (value: string) => void
  onModeChange: (value: PipelineMode) => void
  onProjectIdChange: (value: string) => void
  onGenerate: () => void
}

const options: Array<{ value: PipelineMode; label: string; hint: string }> = [
  { value: 'storyboard', label: 'Storyboard', hint: 'Desde guion' },
  { value: 'image', label: 'Image', hint: 'Concept frames' },
  { value: 'video', label: 'Video', hint: 'Teaser simulado' },
  { value: 'dubbing', label: 'Dubbing', hint: 'Con Legal Gate' },
  { value: 'sound', label: 'Sound', hint: 'Limpieza audio' },
  { value: 'editorial', label: 'Editorial', hint: 'Assembly preview' },
  { value: 'pitch', label: 'Pitch', hint: 'Deck audiovisual' },
]

export default function PipelinePromptBox({
  prompt,
  mode,
  projectId,
  selectedPresetName,
  isGenerating,
  onPromptChange,
  onModeChange,
  onProjectIdChange,
  onGenerate,
}: PipelinePromptBoxProps) {
  return (
    <section className="card card-hover overflow-hidden border-amber-500/10 bg-[radial-gradient(circle_at_top_right,rgba(245,158,11,0.12),transparent_28%),linear-gradient(180deg,rgba(15,23,42,0.96),rgba(2,6,23,0.96))]">
      <div className="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
        <div className="max-w-2xl">
          <div className="inline-flex items-center gap-2 rounded-full border border-amber-400/15 bg-amber-400/10 px-3 py-1 text-xs font-medium uppercase tracking-[0.24em] text-amber-300">
            <Layers3 className="h-3.5 w-3.5" />
            CID Pipeline Builder
          </div>
          <h1 className="mt-4 font-['Cormorant_Garamond'] text-4xl font-semibold text-white md:text-5xl">
            Diseña un pipeline audiovisual antes de ejecutarlo
          </h1>
          <p className="mt-3 max-w-xl text-sm leading-6 text-slate-300">
            Describe el resultado que quieres producir, selecciona el modo de trabajo y genera una propuesta simulated con fases, validacion y control legal.
          </p>
        </div>

        <div className="rounded-2xl border border-cyan-400/10 bg-cyan-400/5 px-4 py-3 text-sm text-slate-300 lg:max-w-xs">
          <p className="text-xs uppercase tracking-[0.2em] text-cyan-300">Preset activo</p>
          <p className="mt-2 text-base font-semibold text-white">{selectedPresetName}</p>
          <p className="mt-1 text-xs text-slate-400">El backend simulated elegira este preset como base para construir el pipeline.</p>
        </div>
      </div>

      <div className="mt-8 grid gap-6 xl:grid-cols-[1.35fr_0.65fr]">
        <div>
          <label className="label" htmlFor="pipeline-prompt">
            Describe que quieres producir
          </label>
          <textarea
            id="pipeline-prompt"
            value={prompt}
            onChange={(event) => onPromptChange(event.target.value)}
            placeholder="Ejemplo: Quiero un teaser tenso de 45 segundos para presentar un thriller rural con tono nocturno y energia festivalera."
            className="input min-h-[180px] resize-y leading-6"
          />
        </div>

        <div className="space-y-5">
          <div>
            <label className="label" htmlFor="pipeline-mode">
              Selector de pipeline
            </label>
            <select
              id="pipeline-mode"
              value={mode}
              onChange={(event) => onModeChange(event.target.value as PipelineMode)}
              className="input"
            >
              {options.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label} - {option.hint}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="label" htmlFor="pipeline-project-id">
              Project ID opcional
            </label>
            <input
              id="pipeline-project-id"
              type="text"
              value={projectId}
              onChange={(event) => onProjectIdChange(event.target.value)}
              placeholder="Si quieres scope por proyecto, pegalo aqui"
              className="input"
            />
          </div>

          <div className="rounded-2xl border border-white/8 bg-white/[0.03] p-4 text-sm text-slate-300">
            <p className="text-xs uppercase tracking-[0.22em] text-slate-400">Que obtienes</p>
            <ul className="mt-3 space-y-2 text-sm leading-6">
              <li>- Fases del pipeline con inputs y outputs</li>
              <li>- Validacion estructural y Legal Gate</li>
              <li>- Ejecucion simulated con historial de jobs</li>
            </ul>
          </div>

          <button
            type="button"
            onClick={onGenerate}
            disabled={isGenerating || !prompt.trim()}
            className="btn-primary flex w-full items-center justify-center gap-2"
          >
            <Sparkles className="h-4 w-4" />
            {isGenerating ? 'Generando pipeline...' : 'Generar pipeline'}
          </button>
        </div>
      </div>
    </section>
  )
}
