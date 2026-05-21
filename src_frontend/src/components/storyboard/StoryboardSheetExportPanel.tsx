import { useMemo, useState } from 'react'
import { AlertTriangle, CheckCircle2, Download, ExternalLink, FileImage, LayoutGrid, Loader2 } from 'lucide-react'
import { storyboardApi } from '@/api/storyboard'
import type {
  StoryboardSheetRequest,
  StoryboardSheetTemplate,
  StoryboardSheetTemplateMetadata,
  StoryboardSheetLayoutName,
  StoryboardSheetOutputFormat,
  StoryboardSheetPreset,
  StoryboardSheetCreditEstimate,
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

const frameCountOptions = [
  { value: 'all', label: 'Todas' },
  { value: '4', label: '4 imágenes' },
  { value: '8', label: '8 imágenes' },
  { value: '12', label: '12 imágenes' },
  { value: '16', label: '16 imágenes' },
  { value: '24', label: '24 imágenes' },
  { value: 'custom', label: 'Personalizado' },
] as const

const sheetTemplateOptions: Array<{
  value: 'current' | StoryboardSheetTemplate
  label: string
  description: string
  defaultFrames: number | null
}> = [
  {
    value: 'current',
    label: 'Automático / Actual',
    description: 'Usa el layout y preset actuales sin aplicar plantilla comercial.',
    defaultFrames: null,
  },
  {
    value: 'clean_4_panel_pitch',
    label: 'Pitch limpio — 4 imágenes',
    description: 'Pitch compacto para presentar 4 frames clave.',
    defaultFrames: 4,
  },
  {
    value: 'clean_6_panel_review',
    label: 'Review — 6 imágenes',
    description: 'Formato de revisión editorial con 6 frames.',
    defaultFrames: 6,
  },
  {
    value: 'grid_8_panel_vertical',
    label: '8 imágenes vertical',
    description: 'Plantilla vertical de 8 panels para revisión densa.',
    defaultFrames: 8,
  },
  {
    value: 'grid_8_panel_landscape',
    label: '8 imágenes landscape',
    description: 'Versión horizontal de 8 panels.',
    defaultFrames: 8,
  },
  {
    value: 'production_12_panel_vertical',
    label: 'Producción — 12 vertical',
    description: 'Hoja de producción vertical para secuencias extensas.',
    defaultFrames: 12,
  },
  {
    value: 'production_12_panel_landscape',
    label: 'Producción — 12 landscape',
    description: 'Hoja de producción horizontal de alta densidad.',
    defaultFrames: 12,
  },
  {
    value: 'client_review_with_notes',
    label: 'Cliente con notas',
    description: 'Template con más espacio para revisión y notas.',
    defaultFrames: 4,
  },
  {
    value: 'technical_storyboard_sheet',
    label: 'Técnico',
    description: 'Formato técnico inspirado en hojas de shot list y notas.',
    defaultFrames: null,
  },
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
  const [sheetTemplate, setSheetTemplate] = useState<'current' | StoryboardSheetTemplate>('current')
  const [frameCountMode, setFrameCountMode] = useState<(typeof frameCountOptions)[number]['value']>('all')
  const [customFrameCount, setCustomFrameCount] = useState('20')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<StoryboardSheetResponse | null>(null)

  const selectedTemplateOption = useMemo(
    () => sheetTemplateOptions.find((option) => option.value === sheetTemplate) || sheetTemplateOptions[0],
    [sheetTemplate]
  )

  const requestedFrameCount = useMemo(() => {
    if (frameCountMode === 'all') return null
    if (frameCountMode === 'custom') {
      const parsed = Number(customFrameCount)
      return Number.isInteger(parsed) ? parsed : null
    }
    return Number(frameCountMode)
  }, [customFrameCount, frameCountMode])

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

  const creditEstimate = useMemo(() => {
    const estimate = result?.metadata?.credit_estimate
    if (!estimate || typeof estimate !== 'object') return null
    return estimate as StoryboardSheetCreditEstimate
  }, [result])

  const pageUrls = useMemo(() => {
    const urls = result?.metadata?.page_urls
    if (!Array.isArray(urls)) return []
    return urls.filter((item): item is string => typeof item === 'string' && item.trim().length > 0)
  }, [result])

  const templateMetadata = useMemo(() => {
    const metadata = result?.metadata?.template
    if (!metadata || typeof metadata !== 'object') return null
    return metadata as StoryboardSheetTemplateMetadata
  }, [result])

  const singleImagePreviewUrl = useMemo(() => {
    if (result?.output_format !== 'png') return null
    if (pageUrls.length > 1) return null
    return result?.artifact_url || pageUrls[0] || null
  }, [pageUrls, result])

  const estimatedCreditsLabel = useMemo(() => {
    if (requestedFrameCount != null) {
      return `Créditos estimados: ${requestedFrameCount}`
    }
    if (selectedTemplateOption.defaultFrames != null) {
      return `Créditos estimados: ${selectedTemplateOption.defaultFrames}`
    }
    if (requestedFrameCount == null) {
      return 'Créditos estimados: Se calculará al generar el sheet.'
    }
    return 'Créditos estimados: Se calculará al generar el sheet.'
  }, [requestedFrameCount, selectedTemplateOption.defaultFrames])

  const handleGenerate = async () => {
    if (frameCountMode === 'custom') {
      const parsed = Number(customFrameCount)
      if (!Number.isInteger(parsed) || parsed < 1 || parsed > 100) {
        setError('El valor personalizado debe ser un número entero entre 1 y 100.')
        setResult(null)
        return
      }
    }

    const payload: StoryboardSheetRequest = {
      project_id: projectId,
      layout: {
        layout,
        preset,
      },
      output_format: outputFormat,
      sheet_template: sheetTemplate === 'current' ? null : sheetTemplate,
      max_frames: requestedFrameCount,
      frame_selection_mode: 'first',
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

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
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

        <label className="space-y-2 xl:col-span-2">
          <span className="text-xs font-medium uppercase tracking-[0.2em] text-slate-400">Template</span>
          <select
            value={sheetTemplate}
            onChange={(event) => setSheetTemplate(event.target.value as 'current' | StoryboardSheetTemplate)}
            className="w-full rounded-xl border border-white/10 bg-dark-300/70 px-4 py-3 text-sm text-white outline-none transition-colors focus:border-amber-500/50"
          >
            {sheetTemplateOptions.map((option) => (
              <option key={option.value} value={option.value}>{option.label}</option>
            ))}
          </select>
          <p className="text-xs text-slate-500">
            {selectedTemplateOption.description}
          </p>
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
            {sheetTemplate === 'current'
              ? layoutOptions.find((option) => option.value === layout)?.description
              : 'La plantilla seleccionada resolverá automáticamente el layout efectivo.'}
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
            {sheetTemplate === 'current'
              ? presetOptions.find((option) => option.value === preset)?.description
              : 'La plantilla seleccionada resolverá automáticamente el preset efectivo.'}
          </p>
        </label>

        <label className="space-y-2">
          <span className="text-xs font-medium uppercase tracking-[0.2em] text-slate-400">Imágenes a incluir</span>
          <select
            value={frameCountMode}
            onChange={(event) => setFrameCountMode(event.target.value as (typeof frameCountOptions)[number]['value'])}
            className="w-full rounded-xl border border-white/10 bg-dark-300/70 px-4 py-3 text-sm text-white outline-none transition-colors focus:border-amber-500/50"
          >
            {frameCountOptions.map((option) => (
              <option key={option.value} value={option.value}>{option.label}</option>
            ))}
          </select>
          <p className="text-xs text-slate-500">
            Selecciona cuántos frames incluir para controlar el coste estimado del export.
          </p>
        </label>
      </div>

      {frameCountMode === 'custom' && (
        <div className="grid gap-4 md:grid-cols-[minmax(0,280px)_1fr] md:items-end">
          <label className="space-y-2">
            <span className="text-xs font-medium uppercase tracking-[0.2em] text-slate-400">Cantidad personalizada</span>
            <input
              type="number"
              min={1}
              max={100}
              step={1}
              value={customFrameCount}
              onChange={(event) => setCustomFrameCount(event.target.value)}
              className="w-full rounded-xl border border-white/10 bg-dark-300/70 px-4 py-3 text-sm text-white outline-none transition-colors focus:border-amber-500/50"
            />
          </label>
          <div className="rounded-xl border border-white/10 bg-black/20 px-4 py-3 text-sm text-slate-400">
            Valor permitido: entre 1 y 100 imágenes.
          </div>
        </div>
      )}

      <div className="rounded-xl border border-cyan-500/20 bg-cyan-500/5 px-4 py-3 text-sm text-cyan-100">
        {estimatedCreditsLabel}
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
          Configuración actual: <span className="text-slate-300">{sheetTemplate === 'current' ? 'modo actual' : selectedTemplateOption.label}</span> · <span className="text-slate-300">{outputFormat.toUpperCase()}</span> · <span className="text-slate-300">{requestedFrameCount == null ? 'frames por defecto/todos' : `${requestedFrameCount} imágenes`}</span>
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
              {templateMetadata && (
                <p className="text-xs text-slate-500">
                  Template efectivo: {templateMetadata.sheet_template || 'current'} · orientación {templateMetadata.orientation}
                </p>
              )}
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

          <div className="grid gap-3 md:grid-cols-5">
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
            <div className="rounded-xl border border-white/10 bg-black/20 p-3">
              <p className="text-[11px] uppercase tracking-[0.18em] text-slate-500">Créditos</p>
              <p className="mt-2 text-lg font-semibold text-white">{creditEstimate?.estimated_credits ?? 'n/a'}</p>
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

          {pageUrls.length > 0 && (
            <div className="space-y-2">
              <p className="text-xs font-medium uppercase tracking-[0.18em] text-slate-500">Page URLs</p>
              <ul className="space-y-2">
                {pageUrls.map((url, index) => (
                  <li key={`${url}-${index}`} className="flex flex-col gap-2 rounded-xl border border-white/10 bg-black/20 px-4 py-3 text-xs text-slate-200 md:flex-row md:items-center md:justify-between">
                    <span className="overflow-x-auto font-mono">{url}</span>
                    <span className="flex shrink-0 gap-2">
                      <a
                        href={url}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-1 rounded-lg border border-white/10 bg-white/5 px-3 py-1.5 text-xs font-medium text-white hover:bg-white/10"
                      >
                        <ExternalLink className="h-3.5 w-3.5" />
                        Abrir
                      </a>
                      <a
                        href={url}
                        download
                        className="inline-flex items-center gap-1 rounded-lg border border-amber-500/30 bg-amber-500/10 px-3 py-1.5 text-xs font-medium text-amber-300 hover:bg-amber-500/20"
                      >
                        <Download className="h-3.5 w-3.5" />
                        Descargar
                      </a>
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {creditEstimate && (
            <div className="space-y-2">
              <p className="text-xs font-medium uppercase tracking-[0.18em] text-slate-500">Credit Estimate</p>
              <div className="rounded-xl border border-white/10 bg-black/20 px-4 py-3 text-sm text-slate-200">
                <p><span className="text-slate-500">Billable frames:</span> {creditEstimate.billable_frames}</p>
                <p><span className="text-slate-500">Pricing unit:</span> {creditEstimate.pricing_unit}</p>
                <p><span className="text-slate-500">Estimated credits:</span> {creditEstimate.estimated_credits}</p>
                <p><span className="text-slate-500">Policy:</span> {creditEstimate.credit_policy}</p>
              </div>
            </div>
          )}

          {singleImagePreviewUrl && (
            <div className="space-y-3">
              <p className="text-xs font-medium uppercase tracking-[0.18em] text-slate-500">Preview</p>
              <div className="overflow-hidden rounded-2xl border border-white/10 bg-black/40 p-2">
                <img
                  src={singleImagePreviewUrl}
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
