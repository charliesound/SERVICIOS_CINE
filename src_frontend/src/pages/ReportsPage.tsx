import type { FormEvent } from 'react'
import { useEffect, useState } from 'react'
import axios from 'axios'
import { Link, Navigate, useNavigate, useParams, useSearchParams } from 'react-router-dom'
import { ClipboardList, RefreshCw } from 'lucide-react'
import { useCreateReport, useReports } from '@/hooks'
import { StructuredReportPayload } from '@/types'
import {
  REPORT_TYPE_OPTIONS,
  buildInitialReportPayload,
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

export default function ReportsPage() {
  const { reportType } = useParams()
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const [submitError, setSubmitError] = useState<string | null>(null)
  const [formValues, setFormValues] = useState<StructuredReportPayload>(buildInitialReportPayload(searchParams))

  if (!isStructuredReportType(reportType)) {
    return <Navigate to="/reports/camera" replace />
  }

  const meta = getReportTypeMeta(reportType)
  const { common, specific } = getReportFields(reportType)
  const reportsQuery = useReports(reportType)
  const createReport = useCreateReport(reportType)

  useEffect(() => {
    setFormValues(buildInitialReportPayload(searchParams))
    setSubmitError(null)
  }, [reportType, searchParams])

  const handleChange = (field: keyof StructuredReportPayload, value: string) => {
    setFormValues((current) => ({ ...current, [field]: value }))
  }

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setSubmitError(null)

    try {
      const report = await createReport.mutateAsync(sanitizeReportPayload(formValues))
      navigate(`/reports/${reportType}/${report.id}`)
    } catch (error) {
      setSubmitError(getErrorMessage(error, 'Unable to create report'))
    }
  }

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h1 className="heading-lg flex items-center gap-3">
            <ClipboardList className="h-6 w-6 text-amber-400" />
            Structured Reports
          </h1>
          <p className="mt-1 text-slate-400">Create and maintain manual shooting reports with optional document-based prefills.</p>
        </div>
        <button className="btn-secondary flex items-center gap-2" onClick={() => reportsQuery.refetch()}>
          <RefreshCw className={`h-4 w-4 ${reportsQuery.isFetching ? 'animate-spin' : ''}`} />
          Refresh
        </button>
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

      <div className="grid gap-6 xl:grid-cols-[1.15fr,1.45fr]">
        <section className="card card-hover">
          <div className="mb-5">
            <h2 className="heading-md">Create {meta.label.slice(0, -1)}</h2>
            <p className="mt-1 text-sm text-slate-400">
              Add a manual report or pass `document_asset_id` to reuse approved structured data when compatible.
            </p>
          </div>

          {submitError && (
            <div className="mb-4 rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-200">
              {submitError}
            </div>
          )}

          <form className="space-y-6" onSubmit={handleSubmit}>
            <div className="grid gap-4 md:grid-cols-2">
              {common.map((field) => (
                <div key={field.name} className={field.type === 'date' ? '' : ''}>
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
                      className="input min-h-[120px]"
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

            <button className="btn-primary" type="submit" disabled={createReport.isPending}>
              {createReport.isPending ? 'Creating...' : `Create ${meta.label.slice(0, -1)}`}
            </button>
          </form>
        </section>

        <section className="card card-hover space-y-4">
          <div className="flex items-center justify-between gap-3">
            <div>
              <h2 className="heading-md">{meta.label}</h2>
              <p className="mt-1 text-sm text-slate-400">Manual records with optional document and media references.</p>
            </div>
            <span className="rounded-full bg-white/5 px-3 py-1 text-xs font-medium text-slate-300">
              {reportsQuery.data?.length ?? 0}
            </span>
          </div>

          {reportsQuery.error && (
            <div className="rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-200">
              {getErrorMessage(reportsQuery.error, `Unable to load ${meta.label.toLowerCase()}`)}
            </div>
          )}

          {reportsQuery.isLoading && <div className="text-sm text-slate-400">Loading reports...</div>}

          {!reportsQuery.isLoading && !reportsQuery.error && (!reportsQuery.data || reportsQuery.data.length === 0) && (
            <div className="rounded-xl border border-dashed border-white/10 px-6 py-10 text-center text-sm text-slate-400">
              No reports created yet for this type.
            </div>
          )}

          {reportsQuery.data?.map((report) => {
            const summary = getReportSummary(reportType, report)
            return (
              <article key={report.id} className="rounded-2xl border border-white/10 bg-dark-300/40 p-5">
                <div className="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
                  <div className="space-y-3 min-w-0">
                    <div className="flex flex-wrap items-center gap-3">
                      <h3 className="text-lg font-semibold text-white break-all">{summary.primary}</h3>
                    </div>
                    <div className="grid gap-2 text-sm text-slate-300 md:grid-cols-2">
                      <p><span className="text-slate-500">ID:</span> {report.id}</p>
                      <p><span className="text-slate-500">Project:</span> {report.project_id}</p>
                      <p><span className="text-slate-500">Document Asset:</span> {report.document_asset_id || 'n/a'}</p>
                      <p><span className="text-slate-500">Media Asset:</span> {report.media_asset_id || 'n/a'}</p>
                      <p><span className="text-slate-500">Report Date:</span> {report.report_date}</p>
                      <p><span className="text-slate-500">Summary:</span> {summary.secondary}</p>
                    </div>
                  </div>

                  <Link to={`/reports/${reportType}/${report.id}`} className="btn-secondary">
                    Open Detail
                  </Link>
                </div>
              </article>
            )
          })}
        </section>
      </div>
    </div>
  )
}
