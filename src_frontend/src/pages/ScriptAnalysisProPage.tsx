import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Sparkles, FileJson, FileText, Layers, AlertCircle, CheckCircle2, Loader2, Lock, BookOpen, Film, Briefcase, WalletCards, Lightbulb } from 'lucide-react'
import { scriptAnalysisApi } from '@/api/scriptAnalysis'
import { projectsApi, type Project } from '@/api'
import { getApiErrorMessage } from '@/utils/apiErrors'
import type { ScriptAnalysisSummary, ScriptAnalysisExportFormat } from '@/types/scriptAnalysis'
import { t } from '@/i18n'

type PageState = 'loading' | 'ready' | 'error' | 'blocked'

const DOWNSTREAM_MODULES = [
  { key: 'breakdown', label: 'Breakdown', icon: Layers, description: t('internal.scriptAnalysisPro.connected.breakdown'), href: '#' },
  { key: 'pitch_deck', label: 'Pitch Deck', icon: Briefcase, description: t('internal.scriptAnalysisPro.connected.pitchDeck'), href: '#' },
  { key: 'storyboard_ai', label: 'Storyboard', icon: Film, description: t('internal.scriptAnalysisPro.connected.storyboard'), href: '#' },
  { key: 'budget_lite', label: 'Budget Lite', icon: WalletCards, description: t('internal.scriptAnalysisPro.connected.budgetLite'), href: '#' },
]

const WHAT_YOU_GET = [
  t('internal.scriptAnalysisPro.deliverables.logline'),
  t('internal.scriptAnalysisPro.deliverables.synopsis'),
  t('internal.scriptAnalysisPro.deliverables.premiseTheme'),
  t('internal.scriptAnalysisPro.deliverables.genreTone'),
  t('internal.scriptAnalysisPro.deliverables.characters'),
  t('internal.scriptAnalysisPro.deliverables.locations'),
  t('internal.scriptAnalysisPro.deliverables.structure'),
  t('internal.scriptAnalysisPro.deliverables.scenes'),
  t('internal.scriptAnalysisPro.deliverables.departments'),
  t('internal.scriptAnalysisPro.deliverables.exportableReport'),
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
        setPageError(getApiErrorMessage(err, t('internal.scriptAnalysisPro.errors.loadProject')))
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
        <p className="text-gray-400">{t('internal.common.projectNotFound')}</p>
        <Link to="/projects" className="mt-4 text-amber-400 hover:underline">{t('internal.common.backToProjects')}</Link>
      </div>
    )
  }

  if (pageState === 'loading') {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="flex items-center gap-3 text-amber-400">
          <Loader2 className="w-6 h-6 animate-spin" />
          <span className="text-sm">{t('internal.scriptAnalysisPro.loading')}</span>
        </div>
      </div>
    )
  }

  if (pageState === 'blocked') {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="mb-6">
          <Link to={`/projects/${projectId}`} className="inline-flex items-center gap-2 text-gray-400 hover:text-white transition-colors">
            <ArrowLeft className="w-4 h-4" /> {t('internal.scriptAnalysisPro.backToProject')}
          </Link>
        </div>
        <div className="card p-12 flex flex-col items-center justify-center gap-4 text-center border border-amber-500/20">
          <div className="w-16 h-16 rounded-2xl bg-amber-500/10 flex items-center justify-center">
            <Lock className="w-8 h-8 text-amber-400" />
          </div>
          <h2 className="text-xl font-semibold">{t('internal.scriptAnalysisPro.lockedTitle')}</h2>
          <p className="text-gray-400 max-w-md">{t('internal.scriptAnalysisPro.lockedDescription')}</p>
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
            <ArrowLeft className="w-4 h-4" /> {t('internal.scriptAnalysisPro.backToProject')}
          </Link>
        </div>
        <div className="card p-12 flex flex-col items-center justify-center gap-4 text-center border border-red-500/20">
          <AlertCircle className="w-10 h-10 text-red-400" />
          <h2 className="text-xl font-semibold">{t('internal.scriptAnalysisPro.loadErrorTitle')}</h2>
          <p className="text-gray-400 max-w-md">{pageError}</p>
          <button onClick={loadData} className="btn-primary mt-2">{t('internal.common.retry')}</button>
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
          <ArrowLeft className="w-4 h-4" /> {t('internal.scriptAnalysisPro.backToProject')}
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
            {hasAnalysis ? t('internal.scriptAnalysisPro.status.completed') : t('internal.scriptAnalysisPro.status.empty')}
          </span>
        </div>
      </div>

      {/* Header */}
      <div className="relative overflow-hidden rounded-[2rem] border border-white/8 bg-dark-200/70 px-8 py-8 mb-8 shadow-[0_28px_80px_rgba(2,6,23,0.32)]">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(245,158,11,0.16),transparent_28%),radial-gradient(circle_at_82%_16%,rgba(56,189,248,0.1),transparent_24%)]" />
        <div className="relative">
          <div className="inline-flex items-center gap-2 rounded-full border border-amber-400/20 bg-amber-400/10 px-4 py-2 text-[11px] font-semibold uppercase tracking-[0.24em] text-amber-100 mb-4">
            <Sparkles className="h-3.5 w-3.5" />
            {t('internal.scriptAnalysisPro.moduleLabel')}
          </div>
          <h1 className="text-3xl font-bold tracking-tight">{t('internal.scriptAnalysisPro.title')}</h1>
          <p className="mt-2 text-gray-400 max-w-2xl">
            {t('internal.scriptAnalysisPro.subtitle')}
          </p>
          {project && (
            <p className="mt-3 text-sm text-gray-500">
              {t('internal.scriptAnalysisPro.projectLabel')}: <span className="text-gray-300">{project.name}</span>
              {hasScript && <span className="ml-2 text-emerald-400">· {t('internal.scriptAnalysisPro.scriptLoaded')} ({project.script_text?.length.toLocaleString()} {t('internal.scriptAnalysisPro.characters')})</span>}
              {!hasScript && <span className="ml-2 text-amber-400">· {t('internal.scriptAnalysisPro.noScript')}</span>}
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
            <p className="font-semibold text-sm">{isAnalyzing ? t('internal.scriptAnalysisPro.analyzing') : t('internal.scriptAnalysisPro.analyzeScript')}</p>
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
            <p className="font-semibold text-sm">{exportingFormat === 'json' ? t('internal.scriptAnalysisPro.exporting') : t('internal.scriptAnalysisPro.exportJson')}</p>
            <p className="text-gray-400 text-xs mt-0.5">{t('internal.scriptAnalysisPro.exportJsonHelp')}</p>
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
            <p className="font-semibold text-sm">{exportingFormat === 'md' ? t('internal.scriptAnalysisPro.exporting') : t('internal.scriptAnalysisPro.exportMarkdown')}</p>
            <p className="text-gray-400 text-xs mt-0.5">{t('internal.scriptAnalysisPro.exportMarkdownHelp')}</p>
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
              <h3 className="font-semibold">{t('internal.scriptAnalysisPro.summaryTitle')}</h3>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="p-4 bg-white/5 rounded-xl">
                <p className="text-gray-400 text-xs mb-1 uppercase tracking-wider">{t('internal.scriptAnalysisPro.metrics.scenes')}</p>
                <p className="text-white font-semibold text-lg">{analysis.scenes_count ?? analysis.scenes?.length ?? 0}</p>
              </div>
              <div className="p-4 bg-white/5 rounded-xl">
                <p className="text-gray-400 text-xs mb-1 uppercase tracking-wider">{t('internal.scriptAnalysisPro.metrics.characters')}</p>
                <p className="text-white font-semibold text-lg">{analysis.characters_count ?? '—'}</p>
              </div>
              <div className="p-4 bg-white/5 rounded-xl">
                <p className="text-gray-400 text-xs mb-1 uppercase tracking-wider">{t('internal.scriptAnalysisPro.metrics.locations')}</p>
                <p className="text-white font-semibold text-lg">{analysis.locations_count ?? '—'}</p>
              </div>
              <div className="p-4 bg-white/5 rounded-xl">
                <p className="text-gray-400 text-xs mb-1 uppercase tracking-wider">{t('internal.scriptAnalysisPro.metrics.sequences')}</p>
                <p className="text-white font-semibold text-lg">{analysis.sequences_count ?? '—'}</p>
              </div>
            </div>
          </div>

          {analysis.summary && (
            <div className="card bg-dark-200/80 border border-white/5 p-6">
              <h4 className="text-sm font-semibold mb-3 text-gray-300">{t('internal.scriptAnalysisPro.detailsTitle')}</h4>
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
            <h3 className="text-lg font-semibold text-gray-300">{t('internal.scriptAnalysisPro.emptyTitle')}</h3>
            <p className="text-gray-500 text-sm mt-1 max-w-md">
              {!hasScript
                ? t('internal.scriptAnalysisPro.emptyNeedsScript')
                : t('internal.scriptAnalysisPro.emptyReady')}
            </p>
          </div>
          {!hasScript && (
            <Link to={`/projects/${projectId}`} className="btn-primary mt-2 inline-flex items-center gap-2">
              <ArrowLeft className="w-4 h-4" /> Ir al proyecto
            </Link>
          )}
        </div>
      )}

      {/* Demo helper */}
      <div className="card bg-gradient-to-r from-amber-500/5 to-transparent border border-amber-500/10 p-5 mb-8">
        <div className="flex items-start gap-4">
          <div className="w-10 h-10 rounded-xl bg-amber-500/10 flex items-center justify-center flex-shrink-0">
            <Lightbulb className="w-5 h-5 text-amber-400" />
          </div>
          <div>
            <p className="font-medium text-sm text-amber-200">{t('internal.scriptAnalysisPro.howToTitle')}</p>
            <p className="text-gray-400 text-sm mt-1 leading-relaxed">
              Selecciona un proyecto con guion cargado desde <span className="text-gray-300">Proyectos</span>,
              pulsa <span className="text-gray-300">Script Analysis Pro</span> en el encabezado del proyecto y luego
              {t('internal.scriptAnalysisPro.howToClickAnalyze')}
              Una vez completado, podrás exportar el análisis en JSON o Markdown.
            </p>
          </div>
        </div>
      </div>

      {/* What you get */}
      <div className="card bg-dark-200/80 border border-white/5 p-6 mb-8">
        <div className="flex items-center gap-2 mb-5">
          <div className="w-8 h-8 rounded-lg bg-amber-500/10 flex items-center justify-center">
            <Sparkles className="w-4 h-4 text-amber-400" />
          </div>
          <h3 className="font-semibold">{t('internal.scriptAnalysisPro.whatItDeliversTitle')}</h3>
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
          <h3 className="font-semibold">{t('internal.scriptAnalysisPro.connectTitle')}</h3>
        </div>
        <p className="text-gray-400 text-sm mb-4">
          {t('internal.scriptAnalysisPro.connectDescription')}
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {DOWNSTREAM_MODULES.map((mod) => {
            const path = mod.key === 'breakdown' ? `/projects/${projectId}/breakdown` : '#'
            const isLink = path !== '#'
            const inner = (
              <div className="flex items-start gap-3 p-4 bg-white/[0.03] rounded-xl border border-white/5 h-full hover:border-white/20 transition-colors">
                <div className="w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center flex-shrink-0">
                  <mod.icon className="w-5 h-5 text-gray-300" />
                </div>
                <div>
                  <p className="font-medium text-sm text-white">{mod.label}</p>
                  <p className="text-gray-400 text-xs mt-0.5">{mod.description}</p>
                </div>
              </div>
            )
            return isLink ? (
              <Link key={mod.key} to={path} className="block">
                {inner}
              </Link>
            ) : (
              <div key={mod.key}>
                {inner}
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
