import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Sparkles, FileJson, FileText, Layers, AlertCircle, CheckCircle2, Loader2, Lock, BookOpen, Film, Briefcase, WalletCards } from 'lucide-react'
import { scriptAnalysisApi } from '@/api/scriptAnalysis'
import { projectsApi, type Project } from '@/api'
import { getApiErrorMessage } from '@/utils/apiErrors'
import type { ScriptAnalysisSummary, ScriptAnalysisExportFormat } from '@/types/scriptAnalysis'

type PageState = 'loading' | 'ready' | 'error' | 'blocked'

const DOWNSTREAM_MODULES = [
  { key: 'breakdown', label: 'Breakdown', icon: Layers, description: 'Desglose técnico por escenas y departamentos.', href: '#' },
  { key: 'pitch_deck', label: 'Pitch Deck', icon: Briefcase, description: 'Presentación ejecutable del proyecto para inversores.', href: '#' },
  { key: 'storyboard_ai', label: 'Storyboard', icon: Film, description: 'Guion gráfico con planos sugeridos por IA.', href: '#' },
  { key: 'budget_lite', label: 'Budget Lite', icon: WalletCards, description: 'Estimación rápida de presupuesto desde el análisis.', href: '#' },
]

const WHAT_YOU_GET = [
  'Logline — una línea que captura la esencia de la historia',
  'Sinopsis extendida — resumen narrativo completo',
  'Premisa y tema — el "de qué trata realmente"',
  'Género(s) y tono — clasificación y atmósfera emocional',
  'Personajes detectados — lista con roles y arcos',
  'Localizaciones — lugares donde transcurre la acción',
  'Estructura dramática — actos, puntos de giro, ritmo',
  'Escenas detalladas — desglose técnico por escena',
  'Departamentos — necesidades técnicas por área',
  'Informe exportable — JSON y Markdown para compartir',
]

function downloadBlob(blob: Blob, filename: string) {
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
  window.URL.revokeObjectURL(url)
}

export default function ScriptAnalysisProPage() {
  const { projectId } = useParams<{ projectId: string }>()
  const [project, setProject] = useState<Project | null>(null)
  const [analysis, setAnalysis] = useState<ScriptAnalysisSummary | null>(null)
  const [pageState, setPageState] = useState<PageState>('loading')
  const [pageError, setPageError] = useState('')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [exportingFormat, setExportingFormat] = useState<ScriptAnalysisExportFormat | null>(null)

  const loadData = async () => {
    if (!projectId) return
    try {
      const p = await projectsApi.get(projectId)
      setProject(p)
      let summary: ScriptAnalysisSummary | null = null
      try {
        summary = await scriptAnalysisApi.getSummary(projectId)
      } catch {
        summary = null
      }
      setAnalysis(summary)
      setPageState('ready')
    } catch (err) {
      const status = (err as { response?: { status?: number } })?.response?.status
      const data = (err as { response?: { data?: unknown } })?.response?.data as Record<string, unknown> | undefined
      const details = data?.details as Record<string, unknown> | undefined
      if (status === 403 && details?.code === 'MODULE_ACCESS_BLOCKED') {
        setPageState('blocked')
      } else {
        setPageError(getApiErrorMessage(err, 'No se pudo cargar el proyecto.'))
        setPageState('error')
      }
    }
  }

  useEffect(() => {
    loadData()
  }, [projectId])

  const handleAnalyze = async () => {
    if (!projectId) return
    setIsAnalyzing(true)
    try {
      await scriptAnalysisApi.runAnalysis(projectId)
      const checkResult = async () => {
        try {
          const summary = await scriptAnalysisApi.getSummary(projectId)
          if (summary?.status === 'completed' || summary?.source === 'breakdown') {
            setAnalysis(summary)
            setIsAnalyzing(false)
            return
          }
          setTimeout(checkResult, 2000)
        } catch {
          setTimeout(checkResult, 2000)
        }
      }
      setTimeout(checkResult, 2000)
    } catch (err) {
      setIsAnalyzing(false)
      const status = (err as { response?: { status?: number } })?.response?.status
      if (status === 403) {
        setPageState('blocked')
      }
    }
  }

  const handleExport = async (format: ScriptAnalysisExportFormat) => {
    if (!projectId) return
    setExportingFormat(format)
    try {
      const blob = await scriptAnalysisApi.exportAnalysis(projectId, format)
      const ext = format === 'json' ? 'json' : 'md'
      downloadBlob(blob, `CID_script_analysis_${projectId}.${ext}`)
    } catch (err) {
      const status = (err as { response?: { status?: number } })?.response?.status
      if (status === 403) {
        setPageState('blocked')
      }
    } finally {
      setExportingFormat(null)
    }
  }

  const hasAnalysis = analysis?.status === 'completed' || analysis?.source === 'breakdown'
  const hasScript = !!project?.script_text

  if (!projectId) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen">
        <p className="text-gray-400">Proyecto no encontrado</p>
        <Link to="/projects" className="mt-4 text-amber-400 hover:underline">Volver a proyectos</Link>
      </div>
    )
  }

  if (pageState === 'loading') {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="flex items-center gap-3 text-amber-400">
          <Loader2 className="w-6 h-6 animate-spin" />
          <span className="text-sm">Cargando análisis de guion...</span>
        </div>
      </div>
    )
  }

  if (pageState === 'blocked') {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="mb-6">
          <Link to={`/projects/${projectId}`} className="inline-flex items-center gap-2 text-gray-400 hover:text-white transition-colors">
            <ArrowLeft className="w-4 h-4" /> Volver al proyecto
          </Link>
        </div>
        <div className="card p-12 flex flex-col items-center justify-center gap-4 text-center border border-amber-500/20">
          <div className="w-16 h-16 rounded-2xl bg-amber-500/10 flex items-center justify-center">
            <Lock className="w-8 h-8 text-amber-400" />
          </div>
          <h2 className="text-xl font-semibold">Módulo bloqueado</h2>
          <p className="text-gray-400 max-w-md">El módulo CID Script Analysis Pro no está disponible en tu plan actual. Actualiza tu plan para acceder al análisis completo de guion.</p>
          <Link to="/plans" className="btn-primary mt-2 inline-flex items-center gap-2">
            <WalletCards className="w-4 h-4" /> Ver planes
          </Link>
        </div>
      </div>
    )
  }

  if (pageState === 'error') {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="mb-6">
          <Link to={`/projects/${projectId}`} className="inline-flex items-center gap-2 text-gray-400 hover:text-white transition-colors">
            <ArrowLeft className="w-4 h-4" /> Volver al proyecto
          </Link>
        </div>
        <div className="card p-12 flex flex-col items-center justify-center gap-4 text-center border border-red-500/20">
          <AlertCircle className="w-10 h-10 text-red-400" />
          <h2 className="text-xl font-semibold">Error al cargar</h2>
          <p className="text-gray-400 max-w-md">{pageError}</p>
          <button onClick={loadData} className="btn-primary mt-2">Reintentar</button>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-5xl mx-auto">
      {/* Back navigation */}
      <div className="mb-6 flex items-center justify-between">
        <Link
          to={`/projects/${projectId}`}
          className="inline-flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-4 h-4" /> Volver al proyecto
        </Link>
        <div className="flex items-center gap-2">
          <span className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium border ${
            hasAnalysis
              ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
              : 'bg-gray-500/10 text-gray-400 border-gray-500/20'
          }`}>
            {hasAnalysis ? (
              <CheckCircle2 className="w-3.5 h-3.5" />
            ) : (
              <AlertCircle className="w-3.5 h-3.5" />
            )}
            {hasAnalysis ? 'Análisis completado' : 'Sin análisis'}
          </span>
        </div>
      </div>

      {/* Header */}
      <div className="relative overflow-hidden rounded-[2rem] border border-white/8 bg-dark-200/70 px-8 py-8 mb-8 shadow-[0_28px_80px_rgba(2,6,23,0.32)]">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(245,158,11,0.16),transparent_28%),radial-gradient(circle_at_82%_16%,rgba(56,189,248,0.1),transparent_24%)]" />
        <div className="relative">
          <div className="inline-flex items-center gap-2 rounded-full border border-amber-400/20 bg-amber-400/10 px-4 py-2 text-[11px] font-semibold uppercase tracking-[0.24em] text-amber-100 mb-4">
            <Sparkles className="h-3.5 w-3.5" />
            Módulo
          </div>
          <h1 className="text-3xl font-bold tracking-tight">CID Script Analysis Pro</h1>
          <p className="mt-2 text-gray-400 max-w-2xl">
            Analiza tu guion cinematográfico con IA: extrae escenas, personajes, localizaciones, estructura narrativa, género, tono y genera informes exportables. Diseñado para productores, guionistas y equipos de desarrollo.
          </p>
          {project && (
            <p className="mt-3 text-sm text-gray-500">
              Proyecto: <span className="text-gray-300">{project.name}</span>
              {hasScript && <span className="ml-2 text-emerald-400">· Guion cargado ({project.script_text?.length.toLocaleString()} caracteres)</span>}
              {!hasScript && <span className="ml-2 text-amber-400">· Sin guion</span>}
            </p>
          )}
        </div>
      </div>

      {/* Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <button
          onClick={handleAnalyze}
          disabled={isAnalyzing || !hasScript}
          className="card p-5 flex items-start gap-4 hover:border-amber-500/30 transition-all disabled:opacity-40 disabled:cursor-not-allowed group"
        >
          <div className="w-11 h-11 rounded-xl bg-amber-500/10 flex items-center justify-center flex-shrink-0 group-hover:bg-amber-500/20 transition-colors">
            {isAnalyzing ? (
              <Loader2 className="w-5 h-5 text-amber-400 animate-spin" />
            ) : (
              <Sparkles className="w-5 h-5 text-amber-400" />
            )}
          </div>
          <div>
            <p className="font-semibold text-sm">{isAnalyzing ? 'Analizando...' : 'Analizar guion'}</p>
            <p className="text-gray-400 text-xs mt-0.5">{isAnalyzing ? 'Procesando el guion...' : 'Extrae escenas, personajes y estructura'}</p>
          </div>
        </button>

        <button
          onClick={() => handleExport('json')}
          disabled={!hasAnalysis || exportingFormat !== null}
          className="card p-5 flex items-start gap-4 hover:border-white/20 transition-all disabled:opacity-40 disabled:cursor-not-allowed group"
        >
          <div className="w-11 h-11 rounded-xl bg-white/5 flex items-center justify-center flex-shrink-0 group-hover:bg-white/10 transition-colors">
            {exportingFormat === 'json' ? (
              <Loader2 className="w-5 h-5 text-gray-300 animate-spin" />
            ) : (
              <FileJson className="w-5 h-5 text-gray-300" />
            )}
          </div>
          <div>
            <p className="font-semibold text-sm">{exportingFormat === 'json' ? 'Exportando...' : 'Exportar JSON'}</p>
            <p className="text-gray-400 text-xs mt-0.5">Descarga el análisis completo en formato JSON</p>
          </div>
        </button>

        <button
          onClick={() => handleExport('md')}
          disabled={!hasAnalysis || exportingFormat !== null}
          className="card p-5 flex items-start gap-4 hover:border-white/20 transition-all disabled:opacity-40 disabled:cursor-not-allowed group"
        >
          <div className="w-11 h-11 rounded-xl bg-white/5 flex items-center justify-center flex-shrink-0 group-hover:bg-white/10 transition-colors">
            {exportingFormat === 'md' ? (
              <Loader2 className="w-5 h-5 text-gray-300 animate-spin" />
            ) : (
              <FileText className="w-5 h-5 text-gray-300" />
            )}
          </div>
          <div>
            <p className="font-semibold text-sm">{exportingFormat === 'md' ? 'Exportando...' : 'Exportar Markdown'}</p>
            <p className="text-gray-400 text-xs mt-0.5">Descarga el informe legible en Markdown</p>
          </div>
        </button>
      </div>

      {/* Analysis results or empty state */}
      {hasAnalysis && analysis ? (
        <div className="space-y-4 mb-8">
          <div className="card bg-dark-200/80 border border-white/5 p-6">
            <div className="flex items-center gap-2 mb-5">
              <div className="w-8 h-8 rounded-lg bg-amber-500/10 flex items-center justify-center">
                <Sparkles className="w-4 h-4 text-amber-400" />
              </div>
              <h3 className="font-semibold">Resumen del análisis</h3>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="p-4 bg-white/5 rounded-xl">
                <p className="text-gray-400 text-xs mb-1 uppercase tracking-wider">Escenas</p>
                <p className="text-white font-semibold text-lg">{analysis.scenes_count ?? analysis.scenes?.length ?? 0}</p>
              </div>
              <div className="p-4 bg-white/5 rounded-xl">
                <p className="text-gray-400 text-xs mb-1 uppercase tracking-wider">Personajes</p>
                <p className="text-white font-semibold text-lg">{analysis.characters_count ?? '—'}</p>
              </div>
              <div className="p-4 bg-white/5 rounded-xl">
                <p className="text-gray-400 text-xs mb-1 uppercase tracking-wider">Localizaciones</p>
                <p className="text-white font-semibold text-lg">{analysis.locations_count ?? '—'}</p>
              </div>
              <div className="p-4 bg-white/5 rounded-xl">
                <p className="text-gray-400 text-xs mb-1 uppercase tracking-wider">Secuencias</p>
                <p className="text-white font-semibold text-lg">{analysis.sequences_count ?? '—'}</p>
              </div>
            </div>
          </div>

          {analysis.summary && (
            <div className="card bg-dark-200/80 border border-white/5 p-6">
              <h4 className="text-sm font-semibold mb-3 text-gray-300">Detalles del análisis</h4>
              <pre className="text-sm text-gray-400 overflow-auto max-h-60 whitespace-pre-wrap font-sans">
                {JSON.stringify(analysis.summary, null, 2)}
              </pre>
            </div>
          )}
        </div>
      ) : (
        <div className="card p-12 flex flex-col items-center justify-center gap-4 text-center mb-8 border border-white/5">
          <div className="w-14 h-14 rounded-2xl bg-gray-500/10 flex items-center justify-center">
            <BookOpen className="w-7 h-7 text-gray-500" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-300">Sin análisis todavía</h3>
            <p className="text-gray-500 text-sm mt-1 max-w-md">
              {!hasScript
                ? 'Carga un guion en el proyecto para poder analizarlo. Ve a la vista de proyecto y añade el texto del guion.'
                : 'Pulsa "Analizar guion" para extraer escenas, personajes, localizaciones y estructura narrativa.'}
            </p>
          </div>
          {!hasScript && (
            <Link to={`/projects/${projectId}`} className="btn-primary mt-2 inline-flex items-center gap-2">
              <ArrowLeft className="w-4 h-4" /> Ir al proyecto
            </Link>
          )}
        </div>
      )}

      {/* What you get */}
      <div className="card bg-dark-200/80 border border-white/5 p-6 mb-8">
        <div className="flex items-center gap-2 mb-5">
          <div className="w-8 h-8 rounded-lg bg-amber-500/10 flex items-center justify-center">
            <Sparkles className="w-4 h-4 text-amber-400" />
          </div>
          <h3 className="font-semibold">Qué entrega este análisis</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
          {WHAT_YOU_GET.map((item) => (
            <div key={item} className="flex items-start gap-3 p-3 bg-white/[0.03] rounded-xl">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 mt-0.5 flex-shrink-0" />
              <span className="text-sm text-gray-300">{item}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Downstream modules */}
      <div className="card bg-dark-200/80 border border-white/5 p-6 mb-8">
        <div className="flex items-center gap-2 mb-5">
          <div className="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center">
            <Layers className="w-4 h-4 text-blue-400" />
          </div>
          <h3 className="font-semibold">Conecta con otros módulos</h3>
        </div>
        <p className="text-gray-400 text-sm mb-4">
          El análisis de guion es la base de estos módulos. Actívalos para ampliar el flujo de producción.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {DOWNSTREAM_MODULES.map((mod) => (
            <div key={mod.key} className="flex items-start gap-3 p-4 bg-white/[0.03] rounded-xl border border-white/5">
              <div className="w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center flex-shrink-0">
                <mod.icon className="w-5 h-5 text-gray-300" />
              </div>
              <div>
                <p className="font-medium text-sm text-white">{mod.label}</p>
                <p className="text-gray-400 text-xs mt-0.5">{mod.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
