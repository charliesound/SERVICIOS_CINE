import { FormEvent, useEffect, useMemo, useState } from 'react'
import { ReportType, StructuredReport, StructuredReportCreate, StructuredReportUpdate } from '@/types'

type ReportEditorFormProps = {
  reportType: ReportType
  mode: 'create'
  initialValue?: StructuredReport | null
  isSubmitting?: boolean
  onSubmit: (payload: StructuredReportCreate) => Promise<void> | void
} | {
  reportType: ReportType
  mode: 'edit'
  initialValue?: StructuredReport | null
  isSubmitting?: boolean
  onSubmit: (payload: StructuredReportUpdate) => Promise<void> | void
}

interface ReportFormState {
  organization_id: string
  project_id: string
  shooting_day_id: string
  sequence_id: string
  scene_id: string
  shot_id: string
  report_date: string
  document_asset_id: string
  media_asset_id: string
  camera_label: string
  operator_name: string
  card_or_mag: string
  take_reference: string
  notes: string
  incidents: string
  sound_roll: string
  mixer_name: string
  boom_operator: string
  sample_rate: string
  bit_depth: string
  timecode_notes: string
  best_take: string
  continuity_notes: string
  editor_note: string
  preferred_take: string
  intention_note: string
  pacing_note: string
  coverage_note: string
}

function emptyState(): ReportFormState {
  return {
    organization_id: '',
    project_id: '',
    shooting_day_id: '',
    sequence_id: '',
    scene_id: '',
    shot_id: '',
    report_date: new Date().toISOString().slice(0, 10),
    document_asset_id: '',
    media_asset_id: '',
    camera_label: '',
    operator_name: '',
    card_or_mag: '',
    take_reference: '',
    notes: '',
    incidents: '',
    sound_roll: '',
    mixer_name: '',
    boom_operator: '',
    sample_rate: '',
    bit_depth: '',
    timecode_notes: '',
    best_take: '',
    continuity_notes: '',
    editor_note: '',
    preferred_take: '',
    intention_note: '',
    pacing_note: '',
    coverage_note: '',
  }
}

function mapReportToState(report?: StructuredReport | null): ReportFormState {
  const base = emptyState()
  if (!report) return base
  return {
    ...base,
    organization_id: report.organization_id,
    project_id: report.project_id,
    shooting_day_id: report.shooting_day_id || '',
    sequence_id: report.sequence_id || '',
    scene_id: report.scene_id || '',
    shot_id: report.shot_id || '',
    report_date: report.report_date,
    document_asset_id: report.document_asset_id || '',
    media_asset_id: report.media_asset_id || '',
    camera_label: 'camera_label' in report ? report.camera_label : '',
    operator_name: 'operator_name' in report ? report.operator_name || '' : '',
    card_or_mag: 'card_or_mag' in report ? report.card_or_mag : '',
    take_reference: 'take_reference' in report ? report.take_reference || '' : '',
    notes: 'notes' in report ? report.notes : '',
    incidents: 'incidents' in report ? report.incidents : '',
    sound_roll: 'sound_roll' in report ? report.sound_roll : '',
    mixer_name: 'mixer_name' in report ? report.mixer_name || '' : '',
    boom_operator: 'boom_operator' in report ? report.boom_operator || '' : '',
    sample_rate: 'sample_rate' in report ? report.sample_rate || '' : '',
    bit_depth: 'bit_depth' in report ? report.bit_depth || '' : '',
    timecode_notes: 'timecode_notes' in report ? report.timecode_notes || '' : '',
    best_take: 'best_take' in report ? report.best_take || '' : '',
    continuity_notes: 'continuity_notes' in report ? report.continuity_notes : '',
    editor_note: 'editor_note' in report ? report.editor_note || '' : '',
    preferred_take: 'preferred_take' in report ? report.preferred_take || '' : '',
    intention_note: 'intention_note' in report ? report.intention_note : '',
    pacing_note: 'pacing_note' in report ? report.pacing_note || '' : '',
    coverage_note: 'coverage_note' in report ? report.coverage_note || '' : '',
  }
}

function normalizeOptional(value: string): string | null | undefined {
  return value ? value : null
}

function buildPayload(reportType: ReportType, mode: 'create' | 'edit', form: ReportFormState): StructuredReportCreate | StructuredReportUpdate {
  const common = {
    shooting_day_id: normalizeOptional(form.shooting_day_id),
    sequence_id: normalizeOptional(form.sequence_id),
    scene_id: normalizeOptional(form.scene_id),
    shot_id: normalizeOptional(form.shot_id),
    report_date: form.report_date,
    document_asset_id: normalizeOptional(form.document_asset_id),
    media_asset_id: normalizeOptional(form.media_asset_id),
  }

  if (reportType === 'camera') {
    const payload = {
      ...common,
      camera_label: form.camera_label,
      operator_name: normalizeOptional(form.operator_name),
      card_or_mag: form.card_or_mag,
      take_reference: normalizeOptional(form.take_reference),
      notes: form.notes,
      incidents: form.incidents,
    }
    return mode === 'create'
      ? { organization_id: form.organization_id || undefined, project_id: form.project_id, ...payload }
      : payload
  }

  if (reportType === 'sound') {
    const payload = {
      ...common,
      sound_roll: form.sound_roll,
      mixer_name: normalizeOptional(form.mixer_name),
      boom_operator: normalizeOptional(form.boom_operator),
      sample_rate: normalizeOptional(form.sample_rate),
      bit_depth: normalizeOptional(form.bit_depth),
      timecode_notes: normalizeOptional(form.timecode_notes),
      notes: form.notes,
      incidents: form.incidents,
    }
    return mode === 'create'
      ? { organization_id: form.organization_id || undefined, project_id: form.project_id, ...payload }
      : payload
  }

  if (reportType === 'script') {
    const payload = {
      ...common,
      best_take: normalizeOptional(form.best_take),
      continuity_notes: form.continuity_notes,
      editor_note: normalizeOptional(form.editor_note),
    }
    return mode === 'create'
      ? { organization_id: form.organization_id || undefined, project_id: form.project_id, ...payload }
      : payload
  }

  const payload = {
    ...common,
    preferred_take: normalizeOptional(form.preferred_take),
    intention_note: form.intention_note,
    pacing_note: normalizeOptional(form.pacing_note),
    coverage_note: normalizeOptional(form.coverage_note),
  }
  return mode === 'create'
    ? { organization_id: form.organization_id || undefined, project_id: form.project_id, ...payload }
    : payload
}

export default function ReportEditorForm({ reportType, mode, initialValue, isSubmitting = false, onSubmit }: ReportEditorFormProps) {
  const [form, setForm] = useState<ReportFormState>(mapReportToState(initialValue))

  useEffect(() => {
    setForm(mapReportToState(initialValue))
  }, [initialValue])

  const title = useMemo(() => {
    if (reportType === 'camera') return 'Camera Report'
    if (reportType === 'sound') return 'Sound Report'
    if (reportType === 'script') return 'Script Note'
    return 'Director Note'
  }, [reportType])

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (mode === 'create') {
      await onSubmit(buildPayload(reportType, mode, form) as StructuredReportCreate)
      return
    }
    await onSubmit(buildPayload(reportType, mode, form) as StructuredReportUpdate)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <h2 className="heading-md">{title}</h2>
        <p className="text-sm text-slate-500">Captura manual y edición del reporte estructurado.</p>
      </div>

      {mode === 'create' && (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div>
            <label className="label">Organization ID</label>
            <input className="input" value={form.organization_id} onChange={(event) => setForm((current) => ({ ...current, organization_id: event.target.value }))} placeholder="org_reports" />
          </div>
          <div>
            <label className="label">Project ID</label>
            <input className="input" value={form.project_id} onChange={(event) => setForm((current) => ({ ...current, project_id: event.target.value }))} placeholder="proj_reports" required />
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
        <input className="input" value={form.shooting_day_id} onChange={(event) => setForm((current) => ({ ...current, shooting_day_id: event.target.value }))} placeholder="shooting_day_id" />
        <input className="input" value={form.sequence_id} onChange={(event) => setForm((current) => ({ ...current, sequence_id: event.target.value }))} placeholder="sequence_id" />
        <input className="input" value={form.scene_id} onChange={(event) => setForm((current) => ({ ...current, scene_id: event.target.value }))} placeholder="scene_id" />
        <input className="input" value={form.shot_id} onChange={(event) => setForm((current) => ({ ...current, shot_id: event.target.value }))} placeholder="shot_id" />
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <div>
          <label className="label">Report date</label>
          <input className="input" type="date" value={form.report_date} onChange={(event) => setForm((current) => ({ ...current, report_date: event.target.value }))} required />
        </div>
        <input className="input" value={form.document_asset_id} onChange={(event) => setForm((current) => ({ ...current, document_asset_id: event.target.value }))} placeholder="document_asset_id" />
        <input className="input" value={form.media_asset_id} onChange={(event) => setForm((current) => ({ ...current, media_asset_id: event.target.value }))} placeholder="media_asset_id" />
      </div>

      {reportType === 'camera' && (
        <>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <input className="input" value={form.camera_label} onChange={(event) => setForm((current) => ({ ...current, camera_label: event.target.value }))} placeholder="camera_label" required />
            <input className="input" value={form.operator_name} onChange={(event) => setForm((current) => ({ ...current, operator_name: event.target.value }))} placeholder="operator_name" />
            <input className="input" value={form.card_or_mag} onChange={(event) => setForm((current) => ({ ...current, card_or_mag: event.target.value }))} placeholder="card_or_mag" required />
            <input className="input" value={form.take_reference} onChange={(event) => setForm((current) => ({ ...current, take_reference: event.target.value }))} placeholder="take_reference" />
          </div>
          <textarea className="input min-h-[120px]" value={form.notes} onChange={(event) => setForm((current) => ({ ...current, notes: event.target.value }))} placeholder="notes" />
          <textarea className="input min-h-[120px]" value={form.incidents} onChange={(event) => setForm((current) => ({ ...current, incidents: event.target.value }))} placeholder="incidents" />
        </>
      )}

      {reportType === 'sound' && (
        <>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <input className="input" value={form.sound_roll} onChange={(event) => setForm((current) => ({ ...current, sound_roll: event.target.value }))} placeholder="sound_roll" required />
            <input className="input" value={form.mixer_name} onChange={(event) => setForm((current) => ({ ...current, mixer_name: event.target.value }))} placeholder="mixer_name" />
            <input className="input" value={form.boom_operator} onChange={(event) => setForm((current) => ({ ...current, boom_operator: event.target.value }))} placeholder="boom_operator" />
            <input className="input" value={form.sample_rate} onChange={(event) => setForm((current) => ({ ...current, sample_rate: event.target.value }))} placeholder="sample_rate" />
            <input className="input" value={form.bit_depth} onChange={(event) => setForm((current) => ({ ...current, bit_depth: event.target.value }))} placeholder="bit_depth" />
            <input className="input" value={form.timecode_notes} onChange={(event) => setForm((current) => ({ ...current, timecode_notes: event.target.value }))} placeholder="timecode_notes" />
          </div>
          <textarea className="input min-h-[120px]" value={form.notes} onChange={(event) => setForm((current) => ({ ...current, notes: event.target.value }))} placeholder="notes" />
          <textarea className="input min-h-[120px]" value={form.incidents} onChange={(event) => setForm((current) => ({ ...current, incidents: event.target.value }))} placeholder="incidents" />
        </>
      )}

      {reportType === 'script' && (
        <>
          <input className="input" value={form.best_take} onChange={(event) => setForm((current) => ({ ...current, best_take: event.target.value }))} placeholder="best_take" />
          <textarea className="input min-h-[140px]" value={form.continuity_notes} onChange={(event) => setForm((current) => ({ ...current, continuity_notes: event.target.value }))} placeholder="continuity_notes" required />
          <textarea className="input min-h-[120px]" value={form.editor_note} onChange={(event) => setForm((current) => ({ ...current, editor_note: event.target.value }))} placeholder="editor_note" />
        </>
      )}

      {reportType === 'director' && (
        <>
          <input className="input" value={form.preferred_take} onChange={(event) => setForm((current) => ({ ...current, preferred_take: event.target.value }))} placeholder="preferred_take" />
          <textarea className="input min-h-[140px]" value={form.intention_note} onChange={(event) => setForm((current) => ({ ...current, intention_note: event.target.value }))} placeholder="intention_note" required />
          <textarea className="input min-h-[120px]" value={form.pacing_note} onChange={(event) => setForm((current) => ({ ...current, pacing_note: event.target.value }))} placeholder="pacing_note" />
          <textarea className="input min-h-[120px]" value={form.coverage_note} onChange={(event) => setForm((current) => ({ ...current, coverage_note: event.target.value }))} placeholder="coverage_note" />
        </>
      )}

      <button type="submit" className="btn-primary" disabled={isSubmitting}>
        {isSubmitting ? 'Guardando...' : mode === 'create' ? 'Crear reporte' : 'Guardar cambios'}
      </button>
    </form>
  )
}
