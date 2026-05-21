import { useMemo, useState } from 'react'
import { AlertTriangle, CheckCircle2, Download, ExternalLink, FileImage, LayoutGrid, Loader2 } from 'lucide-react'
import { storyboardApi } from '@/api/storyboard'
import type {
  StoryboardSheetLayoutConfig,
  StoryboardSheetLayoutName,
  StoryboardSheetOutputFormat,
  StoryboardSheetPreset,
  StoryboardSheetResponse,
} from '@/types/storyboard'

type StoryboardSheetErrorItem = {
  msg?: string
  loc?: Array<string | number>
}

type StoryboardSheetApiError = {
  code?: string
  message?: string
  response?: {
    status?: number
    data?: {
      detail?: string | StoryboardSheetErrorItem[] | { message?: string }
      message?: string
    } | string
  }
}

const layoutOptions: Array<{ value: StoryboardSheetLayoutName; label: string; description: string }> = [
  { value: 'grid_2x2', label: 'Grid 2x2', description: '4 frames por página' },
  { value: 'grid_2x3', label: 'Grid 2x3', description: '6 frames por página' },
  { value: 'grid_2x4', label: 'Grid 2x4', description: '8 frames por página' },
  { value: 'grid_3x3', label: 'Grid 3x3', description: '9 frames por página' },
]

const presetOptions: Array<{ value: StoryboardSheetPreset; label: string; description: string }> = [
  { value: 'realistic_client_review', label: 'Realistic Client Review', description: 'Presentación recomendada para revisión de cliente' },
  { value: 'cinematic_pitch', label: 'Cinematic Pitch', description: 'Look editorial para presentación narrativa' },
  { value: 'production_sheet', label: 'Production Sheet', description: 'Formato operativo orientado a producción' },
  { value: 'clean_corporate', label: 'Clean Corporate', description: 'Acabado sobrio y limpio para entregables' },
]

const outputFormatOptions: Array<{ value: StoryboardSheetOutputFormat; label: string }> = [
  { value: 'png', label: 'PNG' },
  { value: 'pdf', label: 'PDF' },
]

function getStoryboardSheetErrorMessage(error: unknown): string {
  const apiError = error as StoryboardSheetApiError
  const status = apiError.response?.status
  const payload = apiError.response?.data

  const detailFromArray = (items: StoryboardSheetErrorItem[]): string => {
    const messages = items
      .map((item) => {
        const location = Array.isArray(item.loc) ? item.loc.join(' > ') : ''
        if (typeof item.msg !== 'string' || !item.msg.trim()) return null
        return location ? `${location}: ${item.msg}` : item.msg
      })
      .filter((item): item is string => Boolean(item))
    return messages.join(' | ')
  }

  const detail = typeof payload === 'string'
    ? payload
    : payload?.detail

  if (status === 401) {
    return 'Sesión caducada. Vuelve a iniciar sesión.'
  }

  if (status === 400) {
    if (typeof detail === 'string' && detail.trim()) return detail
    if (detail && typeof detail === 'object' && !Array.isArray(detail) && typeof detail.message === 'string') {
      return detail.message
    }
    return 'La solicitud del storyboard sheet no es válida.'
  }

  if (status === 422) {
    if (Array.isArray(detail)) {
      const message = detailFromArray(detail)
      if (message) return message
    }
    if (typeof detail === 'string' && detail.trim()) return detail
    return 'El backend rechazó la solicitud por un error de validación.'
  }

  if (status === 500) {
    if (typeof detail === 'string' && detail.trim() && detail !== 'Internal Server Error') return detail
    return 'No se pudo generar el storyboard sheet por un error interno del backend.'
  }

  if (!apiError.response) {
    return 'El backend no está disponible en este momento. Revisa la conexión e inténtalo otra vez.'
  }

  if (typeof detail === 'string' && detail.trim()) {
    return detail
  }

  if (payload && typeof payload === 'object' && typeof payload.message === 'string' && payload.message.trim()) {
    return payload.message
  }

  if (typeof apiError.message === 'string' && apiError.message.trim()) {
    return apiError.message
  }

  return 'No se pudo generar el storyboard sheet.'
}

interface StoryboardSheetExportPanelProps {
  projectId: string
}

export function StoryboardSheetExportPanel({ projectId }: StoryboardSheetExportPanelProps) {
  const [outputFormat, setOutputFormat] = useState<StoryboardSheetOutputFormat>('png')
  const [layout, setLayout] = useState<StoryboardSheetLayoutName>('grid_2x2')
  const [preset, setPreset] = useState<StoryboardSheetPreset>('realistic_client_review')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<StoryboardSheetResponse | null>(null)

  const pagePaths = useMemo(() => {
    const paths = result?.metadata?.page_paths
    if (!Array.isArray(paths)) return []
    return paths.filter((item): item is string => typeof item === 'string' && item.trim().length > 0)
  }, [result])

  const pageCount = useMemo(() => {
    const rawPageCount = result?.metadata?.page_count
    if (typeof rawPageCount === 'number' && Number.isFinite(rawPageCount)) {
      return rawPageCount
    }
    return pagePaths.length
  }, [pagePaths.length, result])

  const handleGenerate = async () => {
    const payload: { project_id: string; layout: StoryboardSheetLayoutConfig; output_format: StoryboardSheetOutputFormat } = {
      project_id: projectId,
      layout: {
        layout,
        preset,
      },
      output_format: outputFormat,
    }

    setIsSubmitting(true)
    setError(null)
    setResult(null)

    try {
      const response = await storyboardApi.exportStoryboardSheet(projectId, payload)
      setResult(response)
    } catch (err) {
      setError(getStoryboardSheetErrorMessage(err))
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <section className="card bg-dark-200/80 border border-amber-500/20 p-6 space-y-5">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-amber-300">
            <LayoutGrid className="h-5 w-5" />
            <h3 className="text-lg font-semibold text-white">Storyboard Sheet Export</h3>
          </div>
          <p className="max-w-3xl text-sm text-slate-400">
            Genera una hoja editorial del storyboard usando los frames disponibles del proyecto. El backend devuelve la ruta del artefacto y, si existe, una URL pública para abrirlo o descargarlo.
          </p>
        </div>
        <div className="rounded-xl border border-white/10 bg-black/20 px-3 py-2 text-xs text-slate-400">
          Endpoint: <span className="font-mono text-slate-200">POST /api/projects/{projectId}/storyboard/sheet</span>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <label className="space-y-2">
          <span className="text-xs font-medium uppercase tracking-[0.2em] text-slate-400">Formato</span>
          <select
            value={outputFormat}
            onChange={(event) => setOutputFormat(event.target.value as StoryboardSheetOutputFormat)}
            className="w-full rounded-xl border border-white/10 bg-dark-300/70 px-4 py-3 text-sm text-white outline-none transition-colors focus:border-amber-500/50"
          >
            {outputFormatOptions.map((option) => (
              <option key={option.value} value={option.value}>{option.label}</option>
            ))}
          </select>
        </label>

        <label className="space-y-2">
          <span className="text-xs font-medium uppercase tracking-[0.2em] text-slate-400">Layout</span>
          <select
            value={layout}
            onChange={(event) => setLayout(event.target.value as StoryboardSheetLayoutName)}
            className="w-full rounded-xl border border-white/10 bg-dark-300/70 px-4 py-3 text-sm text-white outline-none transition-colors focus:border-amber-500/50"
          >
            {layoutOptions.map((option) => (
              <option key={option.value} value={option.value}>{option.label}</option>
            ))}
          </select>
          <p className="text-xs text-slate-500">
            {layoutOptions.find((option) => option.value === layout)?.description}
          </p>
        </label>

        <label className="space-y-2">
          <span className="text-xs font-medium uppercase tracking-[0.2em] text-slate-400">Preset</span>
          <select
            value={preset}
            onChange={(event) => setPreset(event.target.value as StoryboardSheetPreset)}
            className="w-full rounded-xl border border-white/10 bg-dark-300/70 px-4 py-3 text-sm text-white outline-none transition-colors focus:border-amber-500/50"
          >
            {presetOptions.map((option) => (
              <option key={option.value} value={option.value}>{option.label}</option>
            ))}
          </select>
          <p className="text-xs text-slate-500">
            {presetOptions.find((option) => option.value === preset)?.description}
          </p>
        </label>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <button
          type="button"
          onClick={handleGenerate}
          disabled={isSubmitting}
          className="inline-flex items-center gap-2 rounded-xl bg-amber-500 px-5 py-3 text-sm font-semibold text-black transition-colors hover:bg-amber-400 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {isSubmitting ? <Loader2 className="h-4 w-4 animate-spin" /> : <FileImage className="h-4 w-4" />}
          {isSubmitting ? 'Generando storyboard sheet...' : 'Generar Storyboard Sheet'}
        </button>
        <div className="text-xs text-slate-500">
          Configuración actual: <span className="text-slate-300">{layout}</span> · <span className="text-slate-300">{preset}</span> · <span className="text-slate-300">{outputFormat.toUpperCase()}</span>
        </div>
      </div>

      {error && (
        <div className="rounded-xl border border-red-500/20 bg-red-500/10 p-4 text-sm text-red-300">
          <div className="flex items-start gap-2">
            <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
            <span>{error}</span>
          </div>
        </div>
      )}

      {result && (
        <div className="space-y-4 rounded-2xl border border-emerald-500/20 bg-emerald-500/5 p-5">
          <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
            <div className="space-y-1">
              <div className="flex items-center gap-2 text-emerald-300">
                <CheckCircle2 className="h-5 w-5" />
                <p className="text-sm font-semibold text-white">Export generado correctamente</p>
              </div>
              <p className="text-xs text-slate-400">
                Resultado backend: {result.output_format.toUpperCase()} · layout {result.layout} · preset {result.preset}
              </p>
            </div>

            {result.artifact_url && (
              <div className="flex flex-wrap gap-2">
                <a
                  href={result.artifact_url}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-white/10"
                >
                  <ExternalLink className="h-4 w-4" />
                  Abrir export
                </a>
                <a
                  href={result.artifact_url}
                  download
                  className="inline-flex items-center gap-2 rounded-xl border border-amber-500/30 bg-amber-500/10 px-4 py-2 text-sm font-medium text-amber-300 transition-colors hover:bg-amber-500/20"
                >
                  <Download className="h-4 w-4" />
                  Descargar
                </a>
              </div>
            )}
          </div>

          <div className="grid gap-3 md:grid-cols-4">
            <div className="rounded-xl border border-white/10 bg-black/20 p-3">
              <p className="text-[11px] uppercase tracking-[0.18em] text-slate-500">Frames</p>
              <p className="mt-2 text-2xl font-semibold text-white">{result.frame_count}</p>
            </div>
            <div className="rounded-xl border border-white/10 bg-black/20 p-3">
              <p className="text-[11px] uppercase tracking-[0.18em] text-slate-500">Páginas</p>
              <p className="mt-2 text-2xl font-semibold text-white">{pageCount}</p>
            </div>
            <div className="rounded-xl border border-white/10 bg-black/20 p-3">
              <p className="text-[11px] uppercase tracking-[0.18em] text-slate-500">Formato</p>
              <p className="mt-2 text-lg font-semibold text-white">{result.output_format.toUpperCase()}</p>
            </div>
            <div className="rounded-xl border border-white/10 bg-black/20 p-3">
              <p className="text-[11px] uppercase tracking-[0.18em] text-slate-500">Layout</p>
              <p className="mt-2 text-lg font-semibold text-white">{result.layout}</p>
            </div>
          </div>

          {!result.artifact_url && (
            <div className="rounded-xl border border-amber-500/20 bg-amber-500/5 p-4 text-sm text-amber-200">
              Export generado. La URL pública de descarga todavía no está disponible.
            </div>
          )}

          <div className="space-y-2">
            <p className="text-xs font-medium uppercase tracking-[0.18em] text-slate-500">Artifact Path</p>
            <div className="overflow-x-auto rounded-xl border border-white/10 bg-black/30 px-4 py-3 font-mono text-xs text-slate-200">
              {result.artifact_path}
            </div>
          </div>

          <div className="space-y-2">
            <p className="text-xs font-medium uppercase tracking-[0.18em] text-slate-500">Page Paths</p>
            {pagePaths.length > 0 ? (
              <ul className="space-y-2">
                {pagePaths.map((path, index) => (
                  <li key={`${path}-${index}`} className="overflow-x-auto rounded-xl border border-white/10 bg-black/20 px-4 py-3 font-mono text-xs text-slate-200">
                    {path}
                  </li>
                ))}
              </ul>
            ) : (
              <div className="rounded-xl border border-dashed border-white/10 bg-black/10 px-4 py-3 text-sm text-slate-500">
                El backend no devolvió rutas de páginas adicionales para este export.
              </div>
            )}
          </div>

          {result.artifact_url && result.output_format === 'png' && (
            <div className="space-y-3">
              <p className="text-xs font-medium uppercase tracking-[0.18em] text-slate-500">Preview</p>
              <div className="overflow-hidden rounded-2xl border border-white/10 bg-black/40 p-2">
                <img
                  src={result.artifact_url}
                  alt="Storyboard sheet export preview"
                  className="h-auto w-full rounded-xl object-cover"
                />
              </div>
            </div>
          )}
        </div>
      )}
    </section>
  )
}
