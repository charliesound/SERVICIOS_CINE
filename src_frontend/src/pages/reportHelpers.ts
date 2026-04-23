import {
  CameraReport,
  DirectorNoteReport,
  ScriptNoteReport,
  SoundReport,
  StructuredReport,
  StructuredReportPayload,
  StructuredReportType,
} from '@/types'

export interface ReportFieldDefinition {
  name: keyof StructuredReportPayload
  label: string
  type?: 'text' | 'textarea' | 'date'
}

export const REPORT_TYPE_OPTIONS: Array<{ type: StructuredReportType; label: string; path: string }> = [
  { type: 'camera', label: 'Camera Reports', path: '/reports/camera' },
  { type: 'sound', label: 'Sound Reports', path: '/reports/sound' },
  { type: 'script', label: 'Script Notes', path: '/reports/script' },
  { type: 'director', label: 'Director Notes', path: '/reports/director' },
]

const COMMON_FIELDS: ReportFieldDefinition[] = [
  { name: 'organization_id', label: 'Organization ID' },
  { name: 'project_id', label: 'Project ID' },
  { name: 'shooting_day_id', label: 'Shooting Day ID' },
  { name: 'sequence_id', label: 'Sequence ID' },
  { name: 'scene_id', label: 'Scene ID' },
  { name: 'shot_id', label: 'Shot ID' },
  { name: 'report_date', label: 'Report Date', type: 'date' },
  { name: 'document_asset_id', label: 'Document Asset ID' },
  { name: 'media_asset_id', label: 'Media Asset ID' },
]

const TYPE_FIELDS: Record<StructuredReportType, ReportFieldDefinition[]> = {
  camera: [
    { name: 'camera_label', label: 'Camera Label' },
    { name: 'operator_name', label: 'Operator Name' },
    { name: 'card_or_mag', label: 'Card or Mag' },
    { name: 'take_reference', label: 'Take Reference' },
    { name: 'notes', label: 'Notes', type: 'textarea' },
    { name: 'incidents', label: 'Incidents', type: 'textarea' },
  ],
  sound: [
    { name: 'sound_roll', label: 'Sound Roll' },
    { name: 'mixer_name', label: 'Mixer Name' },
    { name: 'boom_operator', label: 'Boom Operator' },
    { name: 'sample_rate', label: 'Sample Rate' },
    { name: 'bit_depth', label: 'Bit Depth' },
    { name: 'timecode_notes', label: 'Timecode Notes', type: 'textarea' },
    { name: 'notes', label: 'Notes', type: 'textarea' },
    { name: 'incidents', label: 'Incidents', type: 'textarea' },
  ],
  script: [
    { name: 'best_take', label: 'Best Take' },
    { name: 'continuity_notes', label: 'Continuity Notes', type: 'textarea' },
    { name: 'editor_note', label: 'Editor Note', type: 'textarea' },
  ],
  director: [
    { name: 'preferred_take', label: 'Preferred Take' },
    { name: 'intention_note', label: 'Intention Note', type: 'textarea' },
    { name: 'pacing_note', label: 'Pacing Note', type: 'textarea' },
    { name: 'coverage_note', label: 'Coverage Note', type: 'textarea' },
  ],
}

export function isStructuredReportType(value: string | undefined): value is StructuredReportType {
  return value === 'camera' || value === 'sound' || value === 'script' || value === 'director'
}

export function getReportTypeMeta(reportType: StructuredReportType) {
  return REPORT_TYPE_OPTIONS.find((item) => item.type === reportType) || REPORT_TYPE_OPTIONS[0]
}

export function getReportFields(reportType: StructuredReportType) {
  return {
    common: COMMON_FIELDS,
    specific: TYPE_FIELDS[reportType],
  }
}

export function getReportSummary(reportType: StructuredReportType, report: StructuredReport) {
  switch (reportType) {
    case 'camera': {
      const cameraReport = report as CameraReport
      return {
        primary: cameraReport.camera_label || 'Camera report',
        secondary: cameraReport.card_or_mag || 'No card or mag',
      }
    }
    case 'sound': {
      const soundReport = report as SoundReport
      return {
        primary: soundReport.sound_roll || 'Sound report',
        secondary: soundReport.mixer_name || 'No mixer name',
      }
    }
    case 'script': {
      const scriptReport = report as ScriptNoteReport
      return {
        primary: scriptReport.best_take || 'Script note',
        secondary: scriptReport.continuity_notes || 'No continuity notes',
      }
    }
    case 'director': {
      const directorReport = report as DirectorNoteReport
      return {
        primary: directorReport.preferred_take || 'Director note',
        secondary: directorReport.intention_note || 'No intention note',
      }
    }
  }
}

export function buildInitialReportPayload(searchParams: URLSearchParams): StructuredReportPayload {
  return {
    document_asset_id: searchParams.get('document_asset_id') || undefined,
    media_asset_id: searchParams.get('media_asset_id') || undefined,
    organization_id: searchParams.get('organization_id') || undefined,
    project_id: searchParams.get('project_id') || undefined,
    report_date: new Date().toISOString().slice(0, 10),
  }
}

export function sanitizeReportPayload(payload: StructuredReportPayload): StructuredReportPayload {
  const sanitized: StructuredReportPayload = {}
  for (const [key, value] of Object.entries(payload)) {
    if (typeof value !== 'string') continue
    const trimmed = value.trim()
    if (!trimmed) continue
    sanitized[key as keyof StructuredReportPayload] = trimmed as never
  }
  return sanitized
}
