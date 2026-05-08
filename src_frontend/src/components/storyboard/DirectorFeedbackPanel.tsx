import { useState } from 'react'
import { Loader2, Send, History, AlertTriangle, CheckCircle2, Shield, FileText, ChevronDown, ChevronUp } from 'lucide-react'
import { storyboardApi } from '@/api/storyboard'
import type {
  StoryboardShot,
  FeedbackCategory,
  FeedbackSeverity,
  DirectorFeedbackInterpretation,
  PromptRevisionPatch,
  StoryboardRevisionPlan,
} from '@/types/storyboard'

const CATEGORY_LABELS: { value: FeedbackCategory; label: string }[] = [
  { value: 'composition', label: 'Composición' },
  { value: 'lighting', label: 'Iluminación' },
  { value: 'character', label: 'Personaje' },
  { value: 'camera', label: 'Cámara' },
  { value: 'continuity', label: 'Continuidad' },
  { value: 'tone', label: 'Tono' },
  { value: 'production', label: 'Producción' },
  { value: 'other', label: 'Otro' },
]

const SEVERITY_LABELS: { value: FeedbackSeverity; label: string; color: string }[] = [
  { value: 'minor', label: 'Leve', color: 'text-green-400 border-green-500/30 bg-green-500/10' },
  { value: 'medium', label: 'Media', color: 'text-amber-400 border-amber-500/30 bg-amber-500/10' },
  { value: 'major', label: 'Grave', color: 'text-red-400 border-red-500/30 bg-red-500/10' },
]

interface DirectorFeedbackPanelProps {
  shot: StoryboardShot
  projectId: string
}

type FeedbackResult = {
  status: string
  revision_id: string
  interpretation: DirectorFeedbackInterpretation
  prompt_revision: PromptRevisionPatch
  revision_plan: StoryboardRevisionPlan
}

type RevisionHistoryEntry = Record<string, unknown>

export default function DirectorFeedbackPanel({ shot, projectId }: DirectorFeedbackPanelProps) {
  const [noteText, setNoteText] = useState('')
  const [category, setCategory] = useState<FeedbackCategory>('composition')
  const [severity, setSeverity] = useState<FeedbackSeverity>('minor')
  const [preserveLogic, setPreserveLogic] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitError, setSubmitError] = useState<string | null>(null)
  const [result, setResult] = useState<FeedbackResult | null>(null)

  const [showHistory, setShowHistory] = useState(false)
  const [historyEntries, setHistoryEntries] = useState<RevisionHistoryEntry[] | null>(null)
  const [isLoadingHistory, setIsLoadingHistory] = useState(false)
  const [historyError, setHistoryError] = useState<string | null>(null)

  const handleSubmit = async () => {
    if (!noteText.trim()) return
    setIsSubmitting(true)
    setSubmitError(null)
    setResult(null)
    try {
      const res = await storyboardApi.submitShotDirectorFeedback(projectId, shot.id, {
        note_text: noteText.trim(),
        category,
        severity,
        created_by_role: 'director',
        preserve_original_logic: preserveLogic,
      })
      setResult({
        status: res.status,
        revision_id: res.revision_id,
        interpretation: res.revision_plan.interpretation ?? {
          requested_changes: [],
          protected_story_elements: [],
          protected_visual_elements: [],
          conflict_with_script: false,
          conflict_with_script_details: '',
          conflict_with_reference: false,
          conflict_with_reference_details: '',
          conflict_with_initial_prompt: false,
          conflict_with_initial_prompt_details: '',
          recommended_action: '',
          risk_level: '',
          explanation: '',
        },
        prompt_revision: res.revision_plan.prompt_revision ?? {
          original_prompt: '',
          revised_prompt: '',
          original_negative_prompt: '',
          revised_negative_prompt: '',
          preserved_elements: [],
          changed_elements: [],
          rejected_changes: [],
          revision_reason: '',
          director_note_applied: '',
          version_number: 0,
        },
        revision_plan: res.revision_plan,
      })
    } catch (err: any) {
      setSubmitError(err?.response?.data?.detail || err?.message || 'Error al enviar la nota del director')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleToggleHistory = async () => {
    if (showHistory) {
      setShowHistory(false)
      return
    }
    setShowHistory(true)
    if (historyEntries !== null) return
    setIsLoadingHistory(true)
    setHistoryError(null)
    try {
      const entries = await storyboardApi.getShotRevisionHistory(projectId, shot.id)
      setHistoryEntries(entries)
    } catch (err: any) {
      setHistoryError(err?.response?.data?.detail || err?.message || 'Error al cargar historial')
    } finally {
      setIsLoadingHistory(false)
    }
  }

  const isNoteEmpty = !noteText.trim()

  return (
    <div className="rounded-xl border border-amber-500/20 bg-dark-300/60 p-4 mt-2 space-y-4">
      {/* Header */}
      <div className="flex items-center gap-2">
        <Shield className="w-4 h-4 text-amber-400" />
        <h4 className="text-sm font-semibold text-amber-300">Notas del director</h4>
      </div>

      {/* Functional note */}
      <p className="text-[11px] text-slate-500 leading-relaxed">
        CID revisa el prompt respetando la lógica narrativa original: guion, secuencia, intención cinematográfica, continuidad y referencia visual si existe.
      </p>

      {/* Note textarea */}
      <div>
        <textarea
          value={noteText}
          onChange={(e) => setNoteText(e.target.value)}
          placeholder="Escribe tu nota aquí... Ej: 'La iluminación es demasiado oscura, necesito más luz natural'"
          rows={3}
          className="w-full rounded-xl border border-white/10 bg-[#0a1016] px-4 py-2.5 text-sm text-white placeholder-slate-500 focus:border-amber-500/50 focus:outline-none resize-none"
        />
      </div>

      {/* Category + Severity row */}
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-xs font-medium text-slate-400 mb-1">Categoría</label>
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value as FeedbackCategory)}
            className="w-full rounded-xl border border-white/10 bg-[#0a1016] px-3 py-2 text-sm text-white focus:border-amber-500/50 focus:outline-none"
          >
            {CATEGORY_LABELS.map((opt) => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-xs font-medium text-slate-400 mb-1">Severidad</label>
          <div className="flex gap-1.5">
            {SEVERITY_LABELS.map((s) => (
              <button
                key={s.value}
                onClick={() => setSeverity(s.value)}
                className={`flex-1 rounded-lg border px-2 py-1.5 text-[11px] font-medium transition-all ${
                  severity === s.value
                    ? s.color
                    : 'border-white/10 bg-[#0a1016] text-slate-500 hover:border-white/20'
                }`}
              >
                {s.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Preserve logic checkbox */}
      <label className="flex items-center gap-2 cursor-pointer">
        <input
          type="checkbox"
          checked={preserveLogic}
          onChange={(e) => setPreserveLogic(e.target.checked)}
          className="rounded border-white/20 bg-[#0a1016] text-amber-500 focus:ring-amber-500/30"
        />
        <span className="text-xs text-slate-400">Preservar lógica original del guion</span>
      </label>

      {/* Submit button */}
      <button
        onClick={handleSubmit}
        disabled={isSubmitting || isNoteEmpty}
        className="w-full flex items-center justify-center gap-2 rounded-xl bg-amber-500/20 border border-amber-500/30 px-4 py-2.5 text-sm font-medium text-amber-300 hover:bg-amber-500/30 transition-all disabled:opacity-40 disabled:cursor-not-allowed"
      >
        {isSubmitting ? (
          <Loader2 className="w-4 h-4 animate-spin" />
        ) : (
          <Send className="w-4 h-4" />
        )}
        {isSubmitting ? 'Revisando prompt con CID...' : 'Revisar prompt con CID'}
      </button>

      {/* Error */}
      {submitError && (
        <div className="flex items-start gap-2 rounded-lg border border-red-500/20 bg-red-500/10 p-3 text-xs text-red-300">
          <AlertTriangle className="w-3.5 h-3.5 shrink-0 mt-0.5" />
          <span>{submitError}</span>
        </div>
      )}

      {/* Result */}
      {result && (
        <div className="space-y-3 rounded-xl border border-white/10 bg-[#0a1016] p-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-green-400 flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5" />
              Revisión completada
            </span>
            {result.prompt_revision.version_number > 0 && (
              <span className="text-[10px] text-slate-500">v{result.prompt_revision.version_number}</span>
            )}
          </div>

          {/* Status & Risk */}
          <div className="grid grid-cols-2 gap-2 text-[11px]">
            <div className="rounded-lg border border-white/5 bg-dark-300/40 p-2">
              <span className="text-slate-500">Estado</span>
              <p className="text-white font-medium">{result.status}</p>
            </div>
            <div className="rounded-lg border border-white/5 bg-dark-300/40 p-2">
              <span className="text-slate-500">Riesgo</span>
              <p className={`font-medium ${
                result.interpretation.risk_level === 'high' ? 'text-red-400' :
                result.interpretation.risk_level === 'medium' ? 'text-amber-400' :
                'text-green-400'
              }`}>
                {result.interpretation.risk_level === 'high' ? 'Alto' :
                 result.interpretation.risk_level === 'medium' ? 'Medio' : 'Bajo'}
              </p>
            </div>
          </div>

          {/* Conflicts */}
          <div className="space-y-1 text-[11px]">
            <div className="flex items-center gap-2">
              <span className="text-slate-500">Conflicto con guion:</span>
              {result.interpretation.conflict_with_script ? (
                <span className="text-red-400 font-medium flex items-center gap-1"><AlertTriangle className="w-3 h-3" /> Sí</span>
              ) : (
                <span className="text-green-400 font-medium flex items-center gap-1"><CheckCircle2 className="w-3 h-3" /> No</span>
              )}
            </div>
            <div className="flex items-center gap-2">
              <span className="text-slate-500">Conflicto con referencia visual:</span>
              {result.interpretation.conflict_with_reference ? (
                <span className="text-red-400 font-medium flex items-center gap-1"><AlertTriangle className="w-3 h-3" /> Sí</span>
              ) : (
                <span className="text-green-400 font-medium flex items-center gap-1"><CheckCircle2 className="w-3 h-3" /> No</span>
              )}
            </div>
            <div className="flex items-center gap-2">
              <span className="text-slate-500">Conflicto con prompt inicial:</span>
              {result.interpretation.conflict_with_initial_prompt ? (
                <span className="text-amber-400 font-medium flex items-center gap-1"><AlertTriangle className="w-3 h-3" /> Sí</span>
              ) : (
                <span className="text-green-400 font-medium flex items-center gap-1"><CheckCircle2 className="w-3 h-3" /> No</span>
              )}
            </div>
          </div>

          {/* Explanation */}
          {result.interpretation.explanation && (
            <div className="text-[11px] text-slate-300 leading-relaxed">
              <span className="text-slate-500">Explicación:</span> {result.interpretation.explanation}
            </div>
          )}

          {/* Recommended action */}
          {result.interpretation.recommended_action && (
            <div className="rounded-lg border border-amber-500/10 bg-amber-500/5 p-2 text-[11px] text-slate-300">
              <span className="text-amber-400 font-medium">Acción recomendada:</span> {result.interpretation.recommended_action}
            </div>
          )}

          {/* Requested changes */}
          {result.interpretation.requested_changes.length > 0 && (
            <div>
              <p className="text-[11px] font-medium text-slate-400 mb-1">Cambios solicitados</p>
              <ul className="list-inside list-disc text-[11px] text-slate-300 space-y-0.5">
                {result.interpretation.requested_changes.map((c, i) => (
                  <li key={i}>{c}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Protected story elements */}
          {result.interpretation.protected_story_elements.length > 0 && (
            <div>
              <p className="text-[11px] font-medium text-green-400/80 mb-1 flex items-center gap-1">
                <Shield className="w-3 h-3" /> Elementos protegidos del guion
              </p>
              <ul className="list-inside list-disc text-[11px] text-slate-300 space-y-0.5">
                {result.interpretation.protected_story_elements.map((e, i) => (
                  <li key={i}>{e}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Prompt comparison */}
          {result.prompt_revision.original_prompt && (
            <div className="border-t border-white/10 pt-3 space-y-3">
              <h5 className="text-xs font-medium text-amber-400 flex items-center gap-1.5">
                <FileText className="w-3.5 h-3.5" /> Prompt
              </h5>

              <div>
                <p className="text-[10px] font-medium text-slate-500 mb-1">Original</p>
                <pre className="whitespace-pre-wrap text-[11px] text-slate-400 bg-dark-300/40 rounded-lg p-2 border border-white/5 max-h-24 overflow-y-auto">
                  {result.prompt_revision.original_prompt || '(sin prompt original)'}
                </pre>
              </div>

              <div>
                <p className="text-[10px] font-medium text-green-400/70 mb-1">Revisado</p>
                <pre className="whitespace-pre-wrap text-[11px] text-green-300/80 bg-dark-300/40 rounded-lg p-2 border border-green-500/10 max-h-24 overflow-y-auto">
                  {result.prompt_revision.revised_prompt || '(sin cambios)'}
                </pre>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <p className="text-[10px] font-medium text-slate-500 mb-1">Negative prompt original</p>
                  <pre className="whitespace-pre-wrap text-[11px] text-slate-400 bg-dark-300/40 rounded-lg p-2 border border-white/5 max-h-20 overflow-y-auto">
                    {result.prompt_revision.original_negative_prompt || '(vacío)'}
                  </pre>
                </div>
                <div>
                  <p className="text-[10px] font-medium text-green-400/70 mb-1">Negative prompt revisado</p>
                  <pre className="whitespace-pre-wrap text-[11px] text-green-300/80 bg-dark-300/40 rounded-lg p-2 border border-green-500/10 max-h-20 overflow-y-auto">
                    {result.prompt_revision.revised_negative_prompt || '(vacío)'}
                  </pre>
                </div>
              </div>
            </div>
          )}

          {/* Preserved / Changed / Rejected */}
          <div className="grid grid-cols-3 gap-2 text-[11px]">
            {result.prompt_revision.preserved_elements.length > 0 && (
              <div className="rounded-lg border border-green-500/10 bg-green-500/5 p-2">
                <p className="font-medium text-green-400/80 mb-0.5">Preservado</p>
                <ul className="list-inside list-disc text-green-300/60 space-y-0.5">
                  {result.prompt_revision.preserved_elements.map((e, i) => (
                    <li key={i} className="text-[10px]">{e}</li>
                  ))}
                </ul>
              </div>
            )}
            {result.prompt_revision.changed_elements.length > 0 && (
              <div className="rounded-lg border border-amber-500/10 bg-amber-500/5 p-2">
                <p className="font-medium text-amber-400/80 mb-0.5">Cambiado</p>
                <ul className="list-inside list-disc text-amber-300/60 space-y-0.5">
                  {result.prompt_revision.changed_elements.map((e, i) => (
                    <li key={i} className="text-[10px]">{e}</li>
                  ))}
                </ul>
              </div>
            )}
            {result.prompt_revision.rejected_changes.length > 0 && (
              <div className="rounded-lg border border-red-500/10 bg-red-500/5 p-2">
                <p className="font-medium text-red-400/80 mb-0.5">Rechazado</p>
                <ul className="list-inside list-disc text-red-300/60 space-y-0.5">
                  {result.prompt_revision.rejected_changes.map((e, i) => (
                    <li key={i} className="text-[10px]">{e}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Revision reason */}
          {result.prompt_revision.revision_reason && (
            <div className="text-[11px] text-slate-400">
              <span className="text-slate-500">Motivo de revisión:</span> {result.prompt_revision.revision_reason}
            </div>
          )}

          {/* QA Checklist */}
          {result.revision_plan.qa_checklist.length > 0 && (
            <div className="border-t border-white/10 pt-2">
              <p className="text-[11px] font-medium text-slate-400 mb-1">Checklist QA</p>
              <ul className="space-y-0.5">
                {result.revision_plan.qa_checklist.map((item, i) => (
                  <li key={i} className="text-[10px] text-slate-500 flex items-start gap-1.5">
                    <span className="text-amber-400/60 mt-0.5">•</span>
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Revision history toggle */}
      <div className="border-t border-white/5 pt-2">
        <button
          onClick={handleToggleHistory}
          className="flex items-center gap-1.5 text-xs text-slate-500 hover:text-amber-400 transition-colors"
        >
          <History className="w-3.5 h-3.5" />
          Ver historial de revisiones
          {showHistory ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
        </button>

        {showHistory && (
          <div className="mt-2">
            {isLoadingHistory ? (
              <div className="flex items-center gap-2 text-xs text-slate-400 py-2">
                <Loader2 className="w-3 h-3 animate-spin" />
                Cargando historial...
              </div>
            ) : historyError ? (
              <div className="text-xs text-red-400 py-1">{historyError}</div>
            ) : historyEntries && historyEntries.length > 0 ? (
              <div className="space-y-1.5 max-h-48 overflow-y-auto">
                {historyEntries.map((raw, i) => {
                  const entry = raw as Record<string, string | number | undefined>
                  return (
                    <div key={i} className="rounded-lg border border-white/5 bg-dark-300/30 p-2 text-[11px] space-y-0.5">
                      {entry.revision_id && (
                        <p className="text-[10px] text-slate-500">ID: {String(entry.revision_id).substring(0, 12)}...</p>
                      )}
                      {entry.version_number !== undefined && (
                        <p className="text-[10px] text-slate-500">Versión: {String(entry.version_number)}</p>
                      )}
                      {entry.note_text && (
                        <p className="text-slate-300">{String(entry.note_text)}</p>
                      )}
                      {entry.category && (
                        <span className="inline-block px-1.5 py-0.5 text-[9px] bg-amber-400/10 text-amber-300 rounded">{String(entry.category)}</span>
                      )}
                      {entry.created_at && (
                        <p className="text-[9px] text-slate-600">{String(entry.created_at)}</p>
                      )}
                    </div>
                  )
                })}
              </div>
            ) : (
              <p className="text-xs text-slate-500 py-1">Todavía no hay revisiones para este plano.</p>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
