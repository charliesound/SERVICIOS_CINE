import api from './client'
import {
  CameraReport,
  CameraReportListResponse,
  DirectorNoteListResponse,
  DirectorNoteReport,
  ScriptNoteListResponse,
  ScriptNoteReport,
  SoundReport,
  SoundReportListResponse,
  StructuredReport,
  StructuredReportPayload,
  StructuredReportType,
} from '@/types'

function getReportEndpoint(reportType: StructuredReportType) {
  switch (reportType) {
    case 'camera':
      return '/ingest/camera-reports'
    case 'sound':
      return '/ingest/sound-reports'
    case 'script':
      return '/ingest/script-notes'
    case 'director':
      return '/ingest/director-notes'
  }
}

export const reportsApi = {
  listCameraReports: async (): Promise<CameraReport[]> => {
    const { data } = await api.get<CameraReportListResponse>('/ingest/camera-reports')
    return data.reports
  },

  createCameraReport: async (payload: StructuredReportPayload): Promise<CameraReport> => {
    const { data } = await api.post<CameraReport>('/ingest/camera-reports', payload)
    return data
  },

  getCameraReport: async (reportId: string): Promise<CameraReport> => {
    const { data } = await api.get<CameraReport>(`/ingest/camera-reports/${reportId}`)
    return data
  },

  updateCameraReport: async (reportId: string, payload: StructuredReportPayload): Promise<CameraReport> => {
    const { data } = await api.patch<CameraReport>(`/ingest/camera-reports/${reportId}`, payload)
    return data
  },

  listSoundReports: async (): Promise<SoundReport[]> => {
    const { data } = await api.get<SoundReportListResponse>('/ingest/sound-reports')
    return data.reports
  },

  createSoundReport: async (payload: StructuredReportPayload): Promise<SoundReport> => {
    const { data } = await api.post<SoundReport>('/ingest/sound-reports', payload)
    return data
  },

  getSoundReport: async (reportId: string): Promise<SoundReport> => {
    const { data } = await api.get<SoundReport>(`/ingest/sound-reports/${reportId}`)
    return data
  },

  updateSoundReport: async (reportId: string, payload: StructuredReportPayload): Promise<SoundReport> => {
    const { data } = await api.patch<SoundReport>(`/ingest/sound-reports/${reportId}`, payload)
    return data
  },

  listScriptNotes: async (): Promise<ScriptNoteReport[]> => {
    const { data } = await api.get<ScriptNoteListResponse>('/ingest/script-notes')
    return data.reports
  },

  createScriptNote: async (payload: StructuredReportPayload): Promise<ScriptNoteReport> => {
    const { data } = await api.post<ScriptNoteReport>('/ingest/script-notes', payload)
    return data
  },

  getScriptNote: async (reportId: string): Promise<ScriptNoteReport> => {
    const { data } = await api.get<ScriptNoteReport>(`/ingest/script-notes/${reportId}`)
    return data
  },

  updateScriptNote: async (reportId: string, payload: StructuredReportPayload): Promise<ScriptNoteReport> => {
    const { data } = await api.patch<ScriptNoteReport>(`/ingest/script-notes/${reportId}`, payload)
    return data
  },

  listDirectorNotes: async (): Promise<DirectorNoteReport[]> => {
    const { data } = await api.get<DirectorNoteListResponse>('/ingest/director-notes')
    return data.reports
  },

  createDirectorNote: async (payload: StructuredReportPayload): Promise<DirectorNoteReport> => {
    const { data } = await api.post<DirectorNoteReport>('/ingest/director-notes', payload)
    return data
  },

  getDirectorNote: async (reportId: string): Promise<DirectorNoteReport> => {
    const { data } = await api.get<DirectorNoteReport>(`/ingest/director-notes/${reportId}`)
    return data
  },

  updateDirectorNote: async (reportId: string, payload: StructuredReportPayload): Promise<DirectorNoteReport> => {
    const { data } = await api.patch<DirectorNoteReport>(`/ingest/director-notes/${reportId}`, payload)
    return data
  },

  listReports: async (reportType: StructuredReportType): Promise<StructuredReport[]> => {
    switch (reportType) {
      case 'camera':
        return reportsApi.listCameraReports()
      case 'sound':
        return reportsApi.listSoundReports()
      case 'script':
        return reportsApi.listScriptNotes()
      case 'director':
        return reportsApi.listDirectorNotes()
    }
  },

  createReport: async (
    reportType: StructuredReportType,
    payload: StructuredReportPayload,
  ): Promise<StructuredReport> => {
    const endpoint = getReportEndpoint(reportType)
    const { data } = await api.post<StructuredReport>(endpoint, payload)
    return data
  },

  getReport: async (reportType: StructuredReportType, reportId: string): Promise<StructuredReport> => {
    const endpoint = getReportEndpoint(reportType)
    const { data } = await api.get<StructuredReport>(`${endpoint}/${reportId}`)
    return data
  },

  updateReport: async (
    reportType: StructuredReportType,
    reportId: string,
    payload: StructuredReportPayload,
  ): Promise<StructuredReport> => {
    const endpoint = getReportEndpoint(reportType)
    const { data } = await api.patch<StructuredReport>(`${endpoint}/${reportId}`, payload)
    return data
  },
}
