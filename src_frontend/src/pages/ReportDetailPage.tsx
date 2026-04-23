import type { FormEvent } from 'react'
import { useEffect, useState } from 'react'
import axios from 'axios'
import { Link, Navigate, useParams } from 'react-router-dom'
import { ArrowLeft, ClipboardList, Save } from 'lucide-react'
import { useReport, useUpdateReport } from '@/hooks'
import { StructuredReportPayload } from '@/types'
import {
  REPORT_TYPE_OPTIONS,
  getReportFields,
  getReportSummary,
  getReportTypeMeta,
  isStructuredReportType,
  sanitizeReportPayload,
} from './reportHelpers'

function getErrorMessage(error: unknown, fallback: string) {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail
    if (typeof detail === 'string') return detail
    if (Array.isArray(detail)) {
      return detail.map((item) => (typeof item?.msg === 'string' ? item.msg : JSON.stringify(item))).join(', ')
    }
  }
  return fallback
}

export default function ReportDetailPage() {
  const { reportType, reportId = '' } = useParams()
  const [actionError, setActionError] = useState<string | null>(null)
  const [actionSuccess, setActionSuccess] = useState<string | null>(null)
  const [formValues, setFormValues] = useState<StructuredReportPayload>({})

  if (!isStructuredReportType(reportType)) {
    return <Navigate to="/reports/camera" replace />
  }

  const meta = getReportTypeMeta(reportType)
  const { common, specific } = getReportFields(reportType)
  const reportQuery = useReport(reportType, reportId)
  const updateReport = useUpdateReport(reportType, reportId)

  useEffect(() => {
    const report = reportQuery.data
    if (!report) return

    const nextValues: StructuredReportPayload = {
      organization_id: report.organization_id,
      project_id: report.project_id,
      report_date: report.report_date,
    }

    for (const [key, value] of Object.entries(report)) {
      if (value == null) continue
      if (typeof value === 'string') {
        nextValues[key as keyof StructuredReportPayload] = value as never
      }
    }

    setFormValues(nextValues)
  }, [reportQuery.data])

  const handleChange = (field: keyof StructuredReportPayload, value: string) => {
    setFormValues((current) => ({ ...current, [field]: value }))
  }

  const handleSave = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setActionError(null)
    setActionSuccess(null)

    try {
      await updateReport.mutateAsync(sanitizeReportPayload(formValues))
      setActionSuccess('Report saved')
    } catch (error) {
      setActionError(getErrorMessage(error, 'Unable to save report'))
    }
  }

  if (!reportId) {
    return <div className="card text-sm text-red-200">Missing report id.</div>
  }

  if (reportQuery.isLoading) {
    return <div className="text-sm text-slate-400">Loading report...</div>
  }

  if (reportQuery.error || !reportQuery.data) {
    return (
      <div className="card space-y-4">
        <Link to={meta.path} className="btn-ghost inline-flex items-center gap-2 px-0">
          <ArrowLeft className="h-4 w-4" />
          Back to {meta.label}
        </Link>
        <div className="rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-200">
          {getErrorMessage(reportQuery.error, 'Report not found')}
        </div>
      </div>
    )
  }

  const report = reportQuery.data
  const summary = getReportSummary(reportType, report)

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <Link to={meta.path} className="btn-ghost inline-flex items-center gap-2 px-0">
            <ArrowLeft className="h-4 w-4" />
            Back to {meta.label}
          </Link>
          <h1 className="heading-lg mt-2 flex items-center gap-3">
            <ClipboardList className="h-6 w-6 text-amber-400" />
            {summary.primary}
          </h1>
          <p className="mt-1 text-slate-400">Edit the manual report and keep document/media links in sync.</p>
        </div>

        <div className="flex flex-wrap gap-3">
          {REPORT_TYPE_OPTIONS.map((option) => (
            <Link
              key={option.type}
              to={option.path}
              className={option.type === reportType ? 'btn-primary' : 'btn-secondary'}
            >
              {option.label}
            </Link>
          ))}
        </div>
      </div>

      {actionError && (
        <div className="rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-200">
          {actionError}
        </div>
      )}

      {actionSuccess && (
        <div className="rounded-xl border border-green-500/20 bg-green-500/10 px-4 py-3 text-sm text-green-200">
          {actionSuccess}
        </div>
      )}

      <div className="grid gap-6 xl:grid-cols-[1fr,1.25fr]">
        <section className="card card-hover space-y-4">
          <h2 className="heading-md">Report Overview</h2>
          <div className="grid gap-3 text-sm text-slate-300">
            <p><span className="text-slate-500">ID:</span> {report.id}</p>
            <p><span className="text-slate-500">Type:</span> {meta.label}</p>
            <p><span className="text-slate-500">Project:</span> {report.project_id}</p>
            <p><span className="text-slate-500">Document Asset:</span> {report.document_asset_id || 'n/a'}</p>
            <p><span className="text-slate-500">Media Asset:</span> {report.media_asset_id || 'n/a'}</p>
            <p><span className="text-slate-500">Created At:</span> {new Date(report.created_at).toLocaleString()}</p>
            <p><span className="text-slate-500">Updated At:</span> {new Date(report.updated_at).toLocaleString()}</p>
          </div>
          <div className="flex flex-wrap gap-3">
            {report.document_asset_id && (
              <Link to={`/documents/${report.document_asset_id}`} className="btn-secondary">
                Open Document
              </Link>
            )}
            {report.media_asset_id && (
              <Link to={`/ingest/assets/${report.media_asset_id}`} className="btn-secondary">
                Open Media Asset
              </Link>
            )}
          </div>
        </section>

        <section className="card card-hover">
          <form className="space-y-6" onSubmit={handleSave}>
            <div className="grid gap-4 md:grid-cols-2">
              {common.map((field) => (
                <div key={field.name}>
                  <label className="label" htmlFor={String(field.name)}>{field.label}</label>
                  <input
                    id={String(field.name)}
                    type={field.type === 'date' ? 'date' : 'text'}
                    className="input"
                    value={String(formValues[field.name] ?? '')}
                    onChange={(event) => handleChange(field.name, event.target.value)}
                  />
                </div>
              ))}
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              {specific.map((field) => (
                <div key={field.name} className={field.type === 'textarea' ? 'md:col-span-2' : ''}>
                  <label className="label" htmlFor={String(field.name)}>{field.label}</label>
                  {field.type === 'textarea' ? (
                    <textarea
                      id={String(field.name)}
                      className="input min-h-[140px]"
                      value={String(formValues[field.name] ?? '')}
                      onChange={(event) => handleChange(field.name, event.target.value)}
                    />
                  ) : (
                    <input
                      id={String(field.name)}
                      type="text"
                      className="input"
                      value={String(formValues[field.name] ?? '')}
                      onChange={(event) => handleChange(field.name, event.target.value)}
                    />
                  )}
                </div>
              ))}
            </div>

            <button className="btn-primary flex items-center gap-2" type="submit" disabled={updateReport.isPending}>
              <Save className="h-4 w-4" />
              {updateReport.isPending ? 'Saving...' : 'Save Report'}
            </button>
          </form>
        </section>
      </div>
    </div>
  )
}
