import { useEffect, useMemo, useState } from 'react'
import clsx from 'clsx'
import {
  AlertCircle,
  ArrowUpDown,
  Briefcase,
  ChevronLeft,
  ChevronRight,
  Clock3,
  ExternalLink,
  FileSearch,
  Filter,
  Loader2,
  RefreshCw,
  Search,
  ShieldAlert,
  Target,
  X,
  CheckCircle2,
} from 'lucide-react'
import type {
  FundingFitLevel,
  FundingMatch,
  FundingMatchListParams,
  FundingRequirementEvaluation,
} from '@/api/projectFunding'
import {
  useFundingChecklist,
  useFundingMatchEvidence,
  useFundingMatcherStatus,
  useFundingMatches,
  useFundingProfile,
  useRecomputeFundingMatches,
} from '@/hooks'

interface Props {
  projectId: string
}

const PAGE_SIZE = 10

const FIT_LEVEL_STYLES: Record<FundingFitLevel, string> = {
  high: 'border-emerald-500/30 bg-emerald-500/10 text-emerald-300',
  medium: 'border-amber-500/30 bg-amber-500/10 text-amber-300',
  low: 'border-rose-500/30 bg-rose-500/10 text-rose-300',
  blocked: 'border-rose-600/40 bg-rose-600/10 text-rose-200',
}

const FIT_LEVEL_LABELS: Record<FundingFitLevel, string> = {
  high: 'High fit',
  medium: 'Medium fit',
  low: 'Low fit',
  blocked: 'Blocked',
}

const REQUIREMENT_STATUS_STYLES: Record<FundingRequirementEvaluation['status'], string> = {
  met: 'border-emerald-500/25 bg-emerald-500/10 text-emerald-200',
  partially_met: 'border-amber-500/25 bg-amber-500/10 text-amber-200',
  unmet: 'border-rose-500/25 bg-rose-500/10 text-rose-200',
  unknown: 'border-white/10 bg-white/5 text-slate-300',
}

function formatCurrency(value: number | null | undefined) {
  return new Intl.NumberFormat('es-ES', {
    style: 'currency',
    currency: 'EUR',
    maximumFractionDigits: 0,
  }).format(Number(value || 0))
}

function formatDate(value: string | null) {
  if (!value) return 'Sin deadline'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return 'Sin deadline'
  return date.toLocaleDateString('es-ES', { day: '2-digit', month: 'short', year: 'numeric' })
}

function requirementIcon(status: FundingRequirementEvaluation['status']) {
  if (status === 'met') return <CheckCircle2 className="h-4 w-4" />
  if (status === 'partially_met') return <AlertCircle className="h-4 w-4" />
  if (status === 'unmet') return <ShieldAlert className="h-4 w-4" />
  return <FileSearch className="h-4 w-4" />
}

function SummaryCard({ label, value, tone = 'default' }: { label: string; value: string | number; tone?: 'default' | 'green' | 'amber' | 'rose' }) {
  const toneClass = {
    default: 'border-white/10 bg-white/5',
    green: 'border-emerald-500/20 bg-emerald-500/10',
    amber: 'border-amber-500/20 bg-amber-500/10',
    rose: 'border-rose-500/20 bg-rose-500/10',
  }[tone]

  return (
    <div className={clsx('rounded-2xl border p-4', toneClass)}>
      <p className="text-xs uppercase tracking-[0.18em] text-slate-400">{label}</p>
      <p className="mt-2 text-2xl font-semibold text-white">{value}</p>
    </div>
  )
}

function FitBadge({ fitLevel }: { fitLevel: FundingFitLevel }) {
  return (
    <span className={clsx('inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-medium', FIT_LEVEL_STYLES[fitLevel])}>
      {FIT_LEVEL_LABELS[fitLevel]}
    </span>
  )
}

export default function FundingOpportunitiesDashboard({ projectId }: Props) {
  const [searchText, setSearchText] = useState('')
  const [params, setParams] = useState<FundingMatchListParams>({
    page: 1,
    size: PAGE_SIZE,
    sort_by: 'match_score',
    sort_dir: 'desc',
    fit_level: '',
    region_scope: '',
    q: '',
  })
  const [selectedMatch, setSelectedMatch] = useState<FundingMatch | null>(null)
  const [trackingTarget, setTrackingTarget] = useState<FundingMatch | null>(null)

  useEffect(() => {
    const timeoutId = window.setTimeout(() => {
      setParams((current) => ({ ...current, page: 1, q: searchText.trim() }))
    }, 300)

    return () => window.clearTimeout(timeoutId)
  }, [searchText])

  const profileQuery = useFundingProfile(projectId)
  const checklistQuery = useFundingChecklist(projectId)
  const matcherStatusQuery = useFundingMatcherStatus(projectId)
  const matchesQuery = useFundingMatches(projectId, params)
  const recomputeMutation = useRecomputeFundingMatches(projectId)
  const evidenceQuery = useFundingMatchEvidence(projectId, selectedMatch?.match_id || '', !!selectedMatch)

  const matches = matchesQuery.data?.matches ?? []
  const totalMatches = matchesQuery.data?.total ?? checklistQuery.data?.total_opportunities ?? 0
  const topSummary = useMemo(() => ({
    high: checklistQuery.data?.high_matches ?? 0,
    medium: checklistQuery.data?.medium_matches ?? 0,
    low: checklistQuery.data?.low_matches ?? 0,
    blocked: checklistQuery.data?.blocked_matches ?? 0,
  }), [checklistQuery.data])

  const isInitialLoading = profileQuery.isLoading || checklistQuery.isLoading || matchesQuery.isLoading
  const hasError = profileQuery.isError || checklistQuery.isError || matchesQuery.isError
  const currentPage = matchesQuery.data?.page ?? params.page ?? 1
  const pageCount = matchesQuery.data?.pages ?? 0
  const requirementEvaluations = evidenceQuery.data?.evidence_chunks_json?.requirement_evaluations ?? []
  const evidenceChunks = evidenceQuery.data?.evidence_chunks_json?.retrieved_chunks ?? []

  useEffect(() => {
    if (matcherStatusQuery.data?.job?.status === 'completed') {
      matchesQuery.refetch()
      checklistQuery.refetch()
    }
  }, [matcherStatusQuery.data?.job?.status])

  const handleRefresh = async () => {
    await recomputeMutation.mutateAsync()
    await matcherStatusQuery.refetch()
    await matchesQuery.refetch()
    await checklistQuery.refetch()
  }

  return (
    <div className="space-y-6">
      <section className="rounded-[28px] border border-white/10 bg-[radial-gradient(circle_at_top_left,_rgba(245,158,11,0.14),_transparent_30%),linear-gradient(180deg,rgba(15,23,42,0.94),rgba(15,23,42,0.82))] p-6 shadow-2xl shadow-black/20">
        <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs uppercase tracking-[0.18em] text-slate-300">
              <Target className="h-3.5 w-3.5 text-amber-300" />
              Funding opportunities
            </div>
            <h1 className="mt-4 text-3xl font-semibold tracking-tight text-white">
              {profileQuery.data?.title || 'Proyecto'}
            </h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-300">
              Explora el matcher enriquecido por RAG con score, rationale, faltantes y evidencia documental privada por convocatoria.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <div className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-slate-300">
              <div className="text-xs uppercase tracking-[0.18em] text-slate-500">Funding gap</div>
              <div className="mt-1 text-lg font-semibold text-white">{formatCurrency(profileQuery.data?.funding_gap)}</div>
            </div>
            <button
              type="button"
              onClick={handleRefresh}
              disabled={recomputeMutation.isPending}
              className="inline-flex items-center gap-2 rounded-2xl border border-amber-400/30 bg-amber-400/10 px-4 py-3 text-sm font-medium text-amber-100 transition hover:bg-amber-400/20 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {recomputeMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
              Refrescar matcher
            </button>
          </div>
        </div>

        <div className="mt-6 grid gap-4 md:grid-cols-5">
          <SummaryCard label="Total matches" value={totalMatches} />
          <SummaryCard label="High" value={topSummary.high} tone="green" />
          <SummaryCard label="Medium" value={topSummary.medium} tone="amber" />
          <SummaryCard label="Low" value={topSummary.low} tone="rose" />
          <SummaryCard label="Blocked" value={topSummary.blocked} tone="rose" />
        </div>

        {matcherStatusQuery.data?.job && (
          <div className="mt-4 flex flex-wrap items-center gap-3 rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm text-slate-300">
            <Briefcase className="h-4 w-4 text-slate-400" />
            <span>Estado matcher: <strong className="text-white">{matcherStatusQuery.data.job.status}</strong></span>
            {matcherStatusQuery.data.job.completed_at && <span>Actualizado: {formatDate(matcherStatusQuery.data.job.completed_at)}</span>}
            {matcherStatusQuery.data.job.error_message && <span className="text-rose-300">{matcherStatusQuery.data.job.error_message}</span>}
          </div>
        )}
      </section>

      <section className="rounded-[28px] border border-white/10 bg-dark-200/80 p-5">
        <div className="grid gap-3 lg:grid-cols-[1.2fr_repeat(4,minmax(0,1fr))]">
          <label className="relative">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
            <input
              value={searchText}
              onChange={(event) => setSearchText(event.target.value)}
              placeholder="Buscar convocatoria o agencia"
              className="w-full rounded-2xl border border-white/10 bg-white/5 py-3 pl-10 pr-4 text-sm text-white outline-none transition focus:border-amber-400/40"
            />
          </label>

          <select
            value={params.fit_level}
            onChange={(event) => setParams((current) => ({ ...current, page: 1, fit_level: event.target.value as FundingFitLevel | '' }))}
            className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none transition focus:border-amber-400/40"
          >
            <option value="">Todos los niveles</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
            <option value="blocked">Blocked</option>
          </select>

          <select
            value={params.region_scope}
            onChange={(event) => setParams((current) => ({ ...current, page: 1, region_scope: event.target.value as FundingMatchListParams['region_scope'] }))}
            className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none transition focus:border-amber-400/40"
          >
            <option value="">Todas las regiones</option>
            <option value="spain">Spain</option>
            <option value="europe">Europe</option>
            <option value="iberoamerica_latam">Iberoamerica / LATAM</option>
          </select>

          <select
            value={params.sort_by}
            onChange={(event) => setParams((current) => ({ ...current, sort_by: event.target.value as FundingMatchListParams['sort_by'] }))}
            className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none transition focus:border-amber-400/40"
          >
            <option value="match_score">Ordenar por score</option>
            <option value="deadline">Ordenar por deadline</option>
            <option value="fit_level">Ordenar por fit level</option>
          </select>

          <button
            type="button"
            onClick={() => setParams((current) => ({ ...current, sort_dir: current.sort_dir === 'desc' ? 'asc' : 'desc' }))}
            className="inline-flex items-center justify-center gap-2 rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white transition hover:bg-white/10"
          >
            <ArrowUpDown className="h-4 w-4" />
            {params.sort_dir === 'desc' ? 'Descendente' : 'Ascendente'}
          </button>
        </div>

        <div className="mt-3 flex flex-wrap items-center gap-2 text-xs text-slate-400">
          <Filter className="h-3.5 w-3.5" />
          <span>{matchesQuery.data?.count ?? 0} resultados en pagina</span>
          <span className="text-slate-600">/</span>
          <span>{totalMatches} resultados totales</span>
          {checklistQuery.data?.priority_actions?.length ? (
            <>
              <span className="text-slate-600">/</span>
              <span>{checklistQuery.data.priority_actions.length} acciones prioritarias detectadas</span>
            </>
          ) : null}
        </div>
      </section>

      {isInitialLoading ? (
        <div className="flex items-center justify-center rounded-[28px] border border-white/10 bg-dark-200/80 px-6 py-16 text-slate-300">
          <Loader2 className="mr-3 h-5 w-5 animate-spin" />
          Cargando oportunidades enriquecidas...
        </div>
      ) : hasError ? (
        <div className="rounded-[28px] border border-rose-500/20 bg-rose-500/10 px-6 py-10 text-center text-rose-200">
          <AlertCircle className="mx-auto mb-3 h-8 w-8" />
          No se pudo cargar el dashboard de oportunidades.
        </div>
      ) : matches.length === 0 ? (
        <div className="rounded-[28px] border border-white/10 bg-dark-200/80 px-6 py-12 text-center">
          <FileSearch className="mx-auto mb-4 h-10 w-10 text-slate-500" />
          <h2 className="text-lg font-semibold text-white">Sin oportunidades enriquecidas disponibles</h2>
          <p className="mx-auto mt-2 max-w-2xl text-sm text-slate-400">
            El proyecto todavia no tiene resultados RAG visibles con los filtros actuales. Puedes limpiar filtros o lanzar un refresco explicito del matcher.
          </p>
          <div className="mt-5 flex justify-center gap-3">
            <button
              type="button"
              onClick={() => {
                setSearchText('')
                setParams({ page: 1, size: PAGE_SIZE, sort_by: 'match_score', sort_dir: 'desc', fit_level: '', region_scope: '', q: '' })
              }}
              className="rounded-2xl border border-white/10 bg-white/5 px-4 py-2 text-sm text-white transition hover:bg-white/10"
            >
              Limpiar filtros
            </button>
            <button
              type="button"
              onClick={handleRefresh}
              className="rounded-2xl border border-amber-400/30 bg-amber-400/10 px-4 py-2 text-sm font-medium text-amber-100 transition hover:bg-amber-400/20"
            >
              Recompute RAG
            </button>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          {matches.map((match) => (
            <article key={match.match_id} className="rounded-[26px] border border-white/10 bg-dark-200/80 p-5 transition hover:border-white/20">
              <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <FitBadge fitLevel={match.fit_level} />
                    <span className="rounded-full border border-white/10 bg-white/5 px-2.5 py-1 text-xs text-slate-300">{match.source_name}</span>
                    <span className="rounded-full border border-white/10 bg-white/5 px-2.5 py-1 text-xs text-slate-300">{match.region_scope}</span>
                    {match.opportunity_type && (
                      <span className="rounded-full border border-white/10 bg-white/5 px-2.5 py-1 text-xs text-slate-300">{match.opportunity_type}</span>
                    )}
                  </div>

                  <h2 className="mt-3 text-xl font-semibold text-white">{match.title}</h2>
                  <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-300">{match.fit_summary}</p>

                  <div className="mt-4 flex flex-wrap gap-4 text-sm text-slate-400">
                    <span className="inline-flex items-center gap-2"><Target className="h-4 w-4 text-amber-300" /> Score {Math.round(match.match_score)}</span>
                    <span className="inline-flex items-center gap-2"><Clock3 className="h-4 w-4 text-slate-400" /> {formatDate(match.deadline_at)}</span>
                    {match.rag_rationale && <span className="inline-flex items-center gap-2"><FileSearch className="h-4 w-4 text-slate-400" /> {match.rag_rationale}</span>}
                  </div>
                </div>

                <div className="flex min-w-[180px] flex-col gap-3 lg:items-end">
                  <div className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-right">
                    <p className="text-xs uppercase tracking-[0.16em] text-slate-500">Match score</p>
                    <p className="mt-1 text-3xl font-semibold text-white">{Math.round(match.match_score)}</p>
                  </div>
                  <div className="flex w-full gap-2 lg:w-auto">
                    <button
                      type="button"
                      onClick={() => setSelectedMatch(match)}
                      className="flex-1 rounded-2xl border border-white/10 bg-white/5 px-4 py-2.5 text-sm text-white transition hover:bg-white/10"
                    >
                      Ver detalle
                    </button>
                    <button
                      type="button"
                      onClick={() => setTrackingTarget(match)}
                      className="flex-1 rounded-2xl border border-amber-400/20 bg-amber-400/10 px-4 py-2.5 text-sm text-amber-100 transition hover:bg-amber-400/20"
                    >
                      Trackear
                    </button>
                  </div>
                </div>
              </div>

              {(match.recommended_actions_json.length > 0 || match.missing_documents_json.length > 0) && (
                <div className="mt-4 grid gap-4 border-t border-white/5 pt-4 lg:grid-cols-2">
                  <div>
                    <p className="text-xs uppercase tracking-[0.16em] text-slate-500">Recommended actions</p>
                    <div className="mt-2 flex flex-wrap gap-2">
                      {match.recommended_actions_json.slice(0, 3).map((item) => (
                        <span key={item} className="rounded-full border border-emerald-500/20 bg-emerald-500/10 px-2.5 py-1 text-xs text-emerald-100">{item}</span>
                      ))}
                    </div>
                  </div>
                  <div>
                    <p className="text-xs uppercase tracking-[0.16em] text-slate-500">Missing requirements</p>
                    <div className="mt-2 flex flex-wrap gap-2">
                      {match.rag_missing_requirements.slice(0, 3).map((item) => (
                        <span key={item} className="rounded-full border border-rose-500/20 bg-rose-500/10 px-2.5 py-1 text-xs text-rose-100">{item}</span>
                      ))}
                      {!match.rag_missing_requirements.length && match.missing_documents_json.slice(0, 3).map((item) => (
                        <span key={item} className="rounded-full border border-rose-500/20 bg-rose-500/10 px-2.5 py-1 text-xs text-rose-100">{item}</span>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </article>
          ))}

          <div className="flex flex-col gap-3 rounded-[24px] border border-white/10 bg-dark-200/70 px-5 py-4 sm:flex-row sm:items-center sm:justify-between">
            <p className="text-sm text-slate-400">
              Pagina <span className="font-medium text-white">{currentPage}</span> de <span className="font-medium text-white">{Math.max(pageCount, 1)}</span>
            </p>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => setParams((current) => ({ ...current, page: Math.max(1, (current.page || 1) - 1) }))}
                disabled={currentPage <= 1}
                className="inline-flex items-center gap-2 rounded-2xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white transition hover:bg-white/10 disabled:cursor-not-allowed disabled:opacity-50"
              >
                <ChevronLeft className="h-4 w-4" /> Anterior
              </button>
              <button
                type="button"
                onClick={() => setParams((current) => ({ ...current, page: (current.page || 1) + 1 }))}
                disabled={!pageCount || currentPage >= pageCount}
                className="inline-flex items-center gap-2 rounded-2xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white transition hover:bg-white/10 disabled:cursor-not-allowed disabled:opacity-50"
              >
                Siguiente <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      )}

      {selectedMatch && (
        <div className="fixed inset-0 z-40 flex justify-end bg-slate-950/60 backdrop-blur-sm">
          <div className="h-full w-full max-w-2xl overflow-y-auto border-l border-white/10 bg-[#0f172a] p-6 shadow-2xl shadow-black/40">
            <div className="flex items-start justify-between gap-4">
              <div>
                <div className="flex items-center gap-2">
                  <FitBadge fitLevel={selectedMatch.fit_level} />
                  <span className="text-sm text-slate-400">{selectedMatch.source_name}</span>
                </div>
                <h2 className="mt-3 text-2xl font-semibold text-white">{selectedMatch.title}</h2>
                <p className="mt-2 text-sm leading-6 text-slate-300">{selectedMatch.fit_summary}</p>
              </div>
              <button
                type="button"
                onClick={() => setSelectedMatch(null)}
                className="rounded-full border border-white/10 bg-white/5 p-2 text-slate-300 transition hover:bg-white/10"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <div className="mt-6 grid gap-4 md:grid-cols-2">
              <SummaryCard label="Score" value={Math.round(selectedMatch.match_score)} />
              <SummaryCard label="Deadline" value={formatDate(selectedMatch.deadline_at)} />
            </div>

            <div className="mt-6 space-y-6">
              <section className="rounded-2xl border border-white/10 bg-white/5 p-4">
                <p className="text-xs uppercase tracking-[0.16em] text-slate-500">Rationale</p>
                <p className="mt-2 text-sm leading-6 text-slate-200">{selectedMatch.rag_rationale || 'Sin rationale RAG adicional.'}</p>
              </section>

              <section className="grid gap-4 md:grid-cols-3">
                <div className="rounded-2xl border border-rose-500/20 bg-rose-500/10 p-4">
                  <p className="text-xs uppercase tracking-[0.16em] text-rose-200/70">Blocking reasons</p>
                  <ul className="mt-3 space-y-2 text-sm text-rose-100">
                    {(selectedMatch.blocking_reasons_json.length ? selectedMatch.blocking_reasons_json : ['Sin bloqueos duros detectados']).map((item) => (
                      <li key={item} className="flex gap-2"><ShieldAlert className="mt-0.5 h-4 w-4 flex-none" /> <span>{item}</span></li>
                    ))}
                  </ul>
                </div>
                <div className="rounded-2xl border border-amber-500/20 bg-amber-500/10 p-4">
                  <p className="text-xs uppercase tracking-[0.16em] text-amber-100/70">Missing requirements</p>
                  <ul className="mt-3 space-y-2 text-sm text-amber-50">
                    {((selectedMatch.rag_missing_requirements.length ? selectedMatch.rag_missing_requirements : selectedMatch.missing_documents_json).length
                      ? (selectedMatch.rag_missing_requirements.length ? selectedMatch.rag_missing_requirements : selectedMatch.missing_documents_json)
                      : ['Sin faltantes principales visibles']).map((item) => (
                      <li key={item} className="flex gap-2"><AlertCircle className="mt-0.5 h-4 w-4 flex-none" /> <span>{item}</span></li>
                    ))}
                  </ul>
                </div>
                <div className="rounded-2xl border border-emerald-500/20 bg-emerald-500/10 p-4">
                  <p className="text-xs uppercase tracking-[0.16em] text-emerald-100/70">Recommended actions</p>
                  <ul className="mt-3 space-y-2 text-sm text-emerald-50">
                    {(selectedMatch.recommended_actions_json.length ? selectedMatch.recommended_actions_json : ['Sin acciones recomendadas']).map((item) => (
                      <li key={item} className="flex gap-2"><CheckCircle2 className="mt-0.5 h-4 w-4 flex-none" /> <span>{item}</span></li>
                    ))}
                  </ul>
                </div>
              </section>

              <section className="rounded-2xl border border-white/10 bg-white/5 p-4">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <p className="text-xs uppercase tracking-[0.16em] text-slate-500">Requirement evaluation</p>
                    <p className="mt-1 text-sm text-slate-400">Cumplido, parcial o faltante segun evidencia recuperada.</p>
                  </div>
                  {evidenceQuery.isLoading && <Loader2 className="h-4 w-4 animate-spin text-slate-400" />}
                </div>

                <div className="mt-4 space-y-3">
                  {requirementEvaluations.length ? requirementEvaluations.map((item) => (
                    <div key={item.requirement} className={clsx('rounded-2xl border p-4', REQUIREMENT_STATUS_STYLES[item.status])}>
                      <div className="flex items-start gap-3">
                        <div className="mt-0.5">{requirementIcon(item.status)}</div>
                        <div className="min-w-0 flex-1">
                          <div className="flex flex-wrap items-center gap-2">
                            <h3 className="text-sm font-medium text-white">{item.requirement}</h3>
                            <span className="rounded-full border border-white/10 px-2 py-0.5 text-[11px] uppercase tracking-[0.16em] text-slate-200">{item.status.replace('_', ' ')}</span>
                            {item.is_mandatory && <span className="rounded-full border border-white/10 px-2 py-0.5 text-[11px] uppercase tracking-[0.16em] text-slate-200">Mandatory</span>}
                          </div>
                          <p className="mt-2 text-sm leading-6 text-slate-100/90">{item.reasoning}</p>
                          {item.evidence_excerpt && <p className="mt-2 rounded-xl border border-white/10 bg-black/20 p-3 text-sm text-slate-200">{item.evidence_excerpt}</p>}
                        </div>
                      </div>
                    </div>
                  )) : (
                    <div className="rounded-2xl border border-white/10 bg-black/20 px-4 py-6 text-center text-sm text-slate-400">
                      No hay evaluacion detallada disponible para esta oportunidad.
                    </div>
                  )}
                </div>
              </section>

              <section className="rounded-2xl border border-white/10 bg-white/5 p-4">
                <p className="text-xs uppercase tracking-[0.16em] text-slate-500">Evidence fragments</p>
                <div className="mt-4 space-y-3">
                  {evidenceChunks.length ? evidenceChunks.map((chunk) => (
                    <div key={chunk.chunk_id} className="rounded-2xl border border-white/10 bg-black/20 p-4">
                      <div className="flex flex-wrap items-center gap-2 text-xs text-slate-400">
                        <span className="rounded-full border border-white/10 px-2 py-0.5">{chunk.file_name}</span>
                        <span className="rounded-full border border-white/10 px-2 py-0.5">{chunk.document_type}</span>
                        <span className="rounded-full border border-white/10 px-2 py-0.5">Score {chunk.score.toFixed(2)}</span>
                      </div>
                      <p className="mt-3 text-sm leading-6 text-slate-200">{chunk.chunk_text}</p>
                    </div>
                  )) : (
                    <div className="rounded-2xl border border-white/10 bg-black/20 px-4 py-6 text-center text-sm text-slate-400">
                      Sin fragmentos de evidencia para esta oportunidad.
                    </div>
                  )}
                </div>
              </section>

              <section className="flex flex-wrap items-center gap-3 rounded-2xl border border-white/10 bg-white/5 p-4">
                <span className="text-sm text-slate-400">Convocatoria oficial:</span>
                {selectedMatch.official_url ? (
                  <a href={selectedMatch.official_url} target="_blank" rel="noreferrer" className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-2 text-sm text-white transition hover:bg-white/10">
                    Abrir fuente oficial
                    <ExternalLink className="h-4 w-4" />
                  </a>
                ) : (
                  <span className="text-sm text-slate-500">No disponible</span>
                )}
              </section>
            </div>
          </div>
        </div>
      )}

      {trackingTarget && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/60 px-4 backdrop-blur-sm">
          <div className="w-full max-w-lg rounded-[28px] border border-white/10 bg-[#0f172a] p-6 shadow-2xl shadow-black/40">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-xs uppercase tracking-[0.16em] text-amber-300">Tracking stub</p>
                <h3 className="mt-2 text-xl font-semibold text-white">{trackingTarget.title}</h3>
              </div>
              <button
                type="button"
                onClick={() => setTrackingTarget(null)}
                className="rounded-full border border-white/10 bg-white/5 p-2 text-slate-300 transition hover:bg-white/10"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            <p className="mt-4 text-sm leading-6 text-slate-300">
              El tracking operativo de convocatoria y aplicacion automatizada queda preparado para el siguiente bloque. En este MVP solo dejamos el punto de entrada visual sin activar workflow real.
            </p>
            <div className="mt-6 flex justify-end">
              <button
                type="button"
                onClick={() => setTrackingTarget(null)}
                className="rounded-2xl border border-amber-400/20 bg-amber-400/10 px-4 py-2 text-sm font-medium text-amber-100 transition hover:bg-amber-400/20"
              >
                Entendido
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
