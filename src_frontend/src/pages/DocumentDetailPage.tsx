import { useEffect, useMemo, useState } from 'react'
import axios from 'axios'
import { Link, useParams } from 'react-router-dom'
import { ArrowLeft, CheckCircle2, FileText, Layers3, Sparkles, Wand2, FileOutput, AlertCircle, Check } from 'lucide-react'
import StorageStatusBadge from '@/components/StorageStatusBadge'
import {
  useApproveDocument,
  useClassifyDocument,
  useDeriveDocumentPreview,
  useDeriveDocumentReport,
  useDocument,
  useDocumentEvents,
  useExtractDocument,
  useStructureDocument,
  useUpdateDocument,
} from '@/hooks'
import { DerivePreviewResponse } from '@/types'
import { useLanguage } from '@/i18n'

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

export default function DocumentDetailPage() {
  const { t } = useLanguage()
  const { documentId = '' } = useParams()
  const [actionError, setActionError] = useState<string | null>(null)
  const [actionSuccess, setActionSuccess] = useState<string | null>(null)
  const [structuredText, setStructuredText] = useState('{}')
  const [derivePreview, setDerivePreview] = useState<DerivePreviewResponse | null>(null)
  const [showDeriveModal, setShowDeriveModal] = useState(false)
  const [reportPayloadText, setReportPayloadText] = useState('{}')

  const documentQuery = useDocument(documentId)
  const eventsQuery = useDocumentEvents(documentId)
  const updateDocument = useUpdateDocument(documentId)
  const extractDocument = useExtractDocument(documentId)
  const classifyDocument = useClassifyDocument(documentId)
  const structureDocument = useStructureDocument(documentId)
  const approveDocument = useApproveDocument(documentId)
  const derivePreviewMutation = useDeriveDocumentPreview(documentId)
  const deriveReportMutation = useDeriveDocumentReport(documentId)

  const document = documentQuery.data
  
  const isDerivable = document?.status === 'approved' && 
    document?.classification?.doc_type !== 'unknown_document' &&
    document?.classification?.doc_type !== 'operator_note' &&
    document?.structured_data?.review_status === 'approved'

  const reportTypeLabel = derivePreview?.target_report_type === 'camera' ? t('internal.documentDetail.reportTypeCamera')
    : derivePreview?.target_report_type === 'sound' ? t('internal.documentDetail.reportTypeSound')
    : derivePreview?.target_report_type === 'script' ? t('internal.documentDetail.reportTypeScript')
    : derivePreview?.target_report_type === 'director' ? t('internal.documentDetail.reportTypeDirector')
    : t('internal.documentDetail.reportTypeLabel')

  useEffect(() => {
    if (document?.structured_data?.structured_payload_json) {
      setStructuredText(JSON.stringify(document.structured_data.structured_payload_json, null, 2))
    } else {
      setStructuredText('{}')
    }
  }, [document?.structured_data?.structured_payload_json])

  const extractedTable = useMemo(() => {
    return document?.extraction?.extracted_table_json
      ? JSON.stringify(document.extraction.extracted_table_json, null, 2)
      : null
  }, [document?.extraction?.extracted_table_json])

  const clearFeedback = () => {
    setActionError(null)
    setActionSuccess(null)
  }

  const handleSaveStructuredPayload = async () => {
    clearFeedback()
    try {
      const parsed = JSON.parse(structuredText)
      await updateDocument.mutateAsync({ structured_payload_json: parsed, review_status: 'draft' })
      setActionSuccess(t('internal.documentDetail.savePayloadSuccess'))
    } catch (error) {
      if (error instanceof SyntaxError) {
        setActionError(`Invalid JSON: ${error.message}`)
        return
      }
      setActionError(getErrorMessage(error, t('internal.documentDetail.savePayloadError')))
    }
  }

  const handleApprove = async () => {
    clearFeedback()
    try {
      const parsed = JSON.parse(structuredText)
      await updateDocument.mutateAsync({ structured_payload_json: parsed, review_status: 'draft' })
      await approveDocument.mutateAsync({})
      setActionSuccess(t('internal.documentDetail.approveSuccess'))
    } catch (error) {
      if (error instanceof SyntaxError) {
        setActionError(`Invalid JSON: ${error.message}`)
        return
      }
      setActionError(getErrorMessage(error, t('internal.documentDetail.approveError')))
    }
  }

  const runAction = async (
    action: () => Promise<unknown>,
    successMessage: string,
    fallbackMessage: string,
  ) => {
    clearFeedback()
    try {
      await action()
      setActionSuccess(successMessage)
    } catch (error) {
      setActionError(getErrorMessage(error, fallbackMessage))
    }
  }

  const handleGenerateReport = async () => {
    clearFeedback()
    try {
      const preview = await derivePreviewMutation.mutateAsync()
      setDerivePreview(preview)
      setReportPayloadText(JSON.stringify(preview.initial_report_payload, null, 2))
      setShowDeriveModal(true)
    } catch (error) {
      setActionError(getErrorMessage(error, t('internal.documentDetail.reportPreviewError')))
    }
  }

  const handleCreateReport = async () => {
    clearFeedback()
    if (!derivePreview) return
    try {
      const parsed = JSON.parse(reportPayloadText)
      await deriveReportMutation.mutateAsync({
        report_payload: parsed,
        report_type: derivePreview.target_report_type,
      })
      setShowDeriveModal(false)
      setActionSuccess(t('internal.documentDetail.reportCreated').replace('{reportType}', reportTypeLabel))
    } catch (error) {
      if (error instanceof SyntaxError) {
        setActionError(`Invalid JSON: ${error.message}`)
        return
      }
      setActionError(getErrorMessage(error, t('internal.documentDetail.reportCreateError')))
    }
  }

  if (!documentId) {
    return <div className="card text-sm text-red-200">{t('internal.documentDetail.missingId')}</div>
  }

  if (documentQuery.isLoading) {
    return <div className="text-sm text-slate-400">{t('internal.documentDetail.loading')}</div>
  }

  if (documentQuery.error || !document) {
    return (
      <div className="card space-y-4">
        <Link to="/documents" className="btn-ghost inline-flex items-center gap-2 px-0">
          <ArrowLeft className="h-4 w-4" />
          {t('internal.documentDetail.backToDocuments')}
        </Link>
        <div className="rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-200">
          {getErrorMessage(documentQuery.error, t('internal.documentDetail.notFound'))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <Link to="/documents" className="btn-ghost inline-flex items-center gap-2 px-0">
            <ArrowLeft className="h-4 w-4" />
            {t('internal.documentDetail.backToDocuments')}
          </Link>
          <h1 className="heading-lg mt-2 flex items-center gap-3">
            <FileText className="h-6 w-6 text-amber-400" />
            {document.file_name}
          </h1>
          <p className="mt-1 text-slate-400">{t('internal.documentDetail.description')}</p>
        </div>

        <div className="flex flex-wrap gap-3">
          <button className="btn-secondary flex items-center gap-2" onClick={() => runAction(() => extractDocument.mutateAsync({}), t('internal.documentDetail.extractSuccess'), t('internal.documentDetail.extractError'))}>
            <Wand2 className="h-4 w-4" />
            {t('internal.documentDetail.extract')}
          </button>
          <button className="btn-secondary flex items-center gap-2" onClick={() => runAction(() => classifyDocument.mutateAsync({}), t('internal.documentDetail.classifySuccess'), t('internal.documentDetail.classifyError'))}>
            <Sparkles className="h-4 w-4" />
            {t('internal.documentDetail.classify')}
          </button>
          <button className="btn-secondary flex items-center gap-2" onClick={() => runAction(() => structureDocument.mutateAsync({}), t('internal.documentDetail.structureSuccess'), t('internal.documentDetail.structureError'))}>
            <Layers3 className="h-4 w-4" />
            {t('internal.documentDetail.structure')}
          </button>
          <button className="btn-primary flex items-center gap-2" onClick={handleApprove}>
            <CheckCircle2 className="h-4 w-4" />
            {t('internal.documentDetail.approve')}
          </button>
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

      <div className="grid gap-6 xl:grid-cols-[1.05fr,1.35fr]">
        <div className="space-y-6">
          <section className="card card-hover space-y-4">
            <div className="flex flex-wrap items-center gap-3">
              <h2 className="heading-md">{t('internal.documentDetail.overview')}</h2>
              <StorageStatusBadge status={document.status} />
            </div>
            <div className="grid gap-3 text-sm text-slate-300">
              <p><span className="text-slate-500">{t('internal.documentsPage.id')}</span> {document.id}</p>
              <p><span className="text-slate-500">{t('internal.documentDetail.extension')}</span> {document.file_extension}</p>
              <p><span className="text-slate-500">{t('internal.documentDetail.mimeType')}</span> {document.mime_type || 'n/a'}</p>
              <p><span className="text-slate-500">{t('internal.documentDetail.sourceKind')}</span> {document.source_kind}</p>
              <p><span className="text-slate-500">{t('internal.documentDetail.originalPath')}</span> {document.original_path || 'n/a'}</p>
              <p><span className="text-slate-500">{t('internal.documentDetail.mediaAssetId')}</span> {document.media_asset_id || 'n/a'}</p>
              <p><span className="text-slate-500">{t('internal.documentDetail.createdAt')}</span> {new Date(document.created_at).toLocaleString()}</p>
            </div>
            {document.media_asset_id && (
              <Link to={`/ingest/assets/${document.media_asset_id}`} className="btn-secondary inline-flex">
                {t('internal.documentDetail.openMediaAsset')}
              </Link>
            )}
            {isDerivable && (
              <button className="btn-primary flex items-center gap-2" onClick={handleGenerateReport}>
                <FileOutput className="h-4 w-4" />
                {t('internal.documentDetail.generateReport')}
              </button>
            )}
            {!isDerivable && document?.status === 'approved' && (
              <div className="flex items-center gap-2 text-sm text-amber-400">
                <AlertCircle className="h-4 w-4" />
                {t('internal.documentDetail.notDerivable')}
              </div>
            )}
          </section>

          <section className="card card-hover space-y-4">
            <h2 className="heading-md">{t('internal.documentDetail.extraction')}</h2>
            <div className="grid gap-3 text-sm text-slate-300">
              <p><span className="text-slate-500">{t('internal.documentDetail.extractionStatus')}</span> {document.extraction?.extraction_status || t('internal.documentDetail.notStarted')}</p>
              <p><span className="text-slate-500">{t('internal.documentDetail.engine')}</span> {document.extraction?.extraction_engine || 'n/a'}</p>
              <p><span className="text-slate-500">{t('internal.documentDetail.error')}</span> {document.extraction?.error_message || t('internal.documentDetail.none')}</p>
            </div>
            <div>
              <p className="mb-2 text-xs uppercase tracking-wide text-slate-500">{t('internal.documentDetail.rawText')}</p>
              <pre className="max-h-72 overflow-auto rounded-xl border border-white/10 bg-dark-300/40 p-4 text-xs text-slate-200 whitespace-pre-wrap">
                {document.extraction?.raw_text || t('internal.documentDetail.noRawText')}
              </pre>
            </div>
            <div>
              <p className="mb-2 text-xs uppercase tracking-wide text-slate-500">{t('internal.documentDetail.extractedTable')}</p>
              <pre className="max-h-72 overflow-auto rounded-xl border border-white/10 bg-dark-300/40 p-4 text-xs text-slate-200 whitespace-pre-wrap">
                {extractedTable || t('internal.documentDetail.noExtractedTable')}
              </pre>
            </div>
          </section>
        </div>

        <div className="space-y-6">
          <section className="card card-hover space-y-4">
            <h2 className="heading-md">{t('internal.documentDetail.classification')}</h2>
            <div className="grid gap-3 text-sm text-slate-300 md:grid-cols-2">
              <p><span className="text-slate-500">{t('internal.documentDetail.docType')}</span> {document.classification?.doc_type || t('internal.documentDetail.notClassified')}</p>
              <p><span className="text-slate-500">{t('internal.documentDetail.status')}</span> {document.classification?.classification_status || 'n/a'}</p>
              <p><span className="text-slate-500">{t('internal.documentDetail.confidence')}</span> {document.classification?.confidence_score ?? 'n/a'}</p>
            </div>
          </section>

          <section className="card card-hover space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <h2 className="heading-md">{t('internal.documentDetail.structuredPayload')}</h2>
              <button className="btn-secondary" onClick={handleSaveStructuredPayload}>
                {t('internal.documentDetail.savePayload')}
              </button>
            </div>
            <div className="grid gap-3 text-sm text-slate-300 md:grid-cols-2">
              <p><span className="text-slate-500">{t('internal.documentDetail.reviewStatus')}</span> {document.structured_data?.review_status || 'n/a'}</p>
              <p><span className="text-slate-500">{t('internal.documentDetail.schemaType')}</span> {document.structured_data?.schema_type || 'n/a'}</p>
              <p><span className="text-slate-500">{t('internal.documentDetail.approvedBy')}</span> {document.structured_data?.approved_by || 'n/a'}</p>
              <p><span className="text-slate-500">{t('internal.documentDetail.approvedAt')}</span> {document.structured_data?.approved_at ? new Date(document.structured_data.approved_at).toLocaleString() : 'n/a'}</p>
            </div>
            <textarea
              className="input min-h-[320px] font-mono text-xs"
              value={structuredText}
              onChange={(event) => setStructuredText(event.target.value)}
              spellCheck={false}
            />
          </section>

          <section className="card card-hover space-y-4">
            <h2 className="heading-md">{t('internal.documentDetail.events')}</h2>
            {eventsQuery.error && (
              <div className="rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-200">
                {getErrorMessage(eventsQuery.error, t('internal.documentDetail.eventsError'))}
              </div>
            )}
            {eventsQuery.isLoading && <div className="text-sm text-slate-400">{t('internal.documentDetail.eventsLoading')}</div>}
            {!eventsQuery.isLoading && !eventsQuery.error && (!eventsQuery.data || eventsQuery.data.length === 0) && (
              <div className="text-sm text-slate-400">{t('internal.documentDetail.eventsEmpty')}</div>
            )}
            <div className="space-y-3">
              {eventsQuery.data?.map((event) => (
                <div key={event.id} className="rounded-xl border border-white/10 bg-dark-300/40 p-4">
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <p className="font-medium text-white">{event.event_type}</p>
                    <p className="text-xs text-slate-500">{new Date(event.created_at).toLocaleString()}</p>
                  </div>
                  <p className="mt-2 text-sm text-slate-400">Created by: {event.created_by || 'system'}</p>
                  <pre className="mt-3 overflow-auto rounded-lg bg-black/20 p-3 text-xs text-slate-300 whitespace-pre-wrap">
                    {event.event_payload_json ? JSON.stringify(event.event_payload_json, null, 2) : '{}'}
                  </pre>
                </div>
              ))}
            </div>
          </section>
        </div>
      </div>

      {showDeriveModal && derivePreview && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
          <div className="card w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">
            <div className="flex items-center justify-between border-b border-white/10 p-6">
              <h2 className="heading-md flex items-center gap-3">
                <FileOutput className="h-5 w-5 text-amber-400" />
                {t('internal.documentDetail.generateModalTitle').replace('{reportType}', reportTypeLabel)}
              </h2>
              <button
                className="btn-ghost"
                onClick={() => setShowDeriveModal(false)}
              >
                {t('internal.documentDetail.close')}
              </button>
            </div>

            <div className="flex-1 overflow-auto p-6 space-y-4">
              {!derivePreview.allowed ? (
                <div className="rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-200">
                  <div className="flex items-center gap-2">
                    <AlertCircle className="h-4 w-4" />
                    {t('internal.documentDetail.derivationNotAllowed')}
                  </div>
                  <p className="mt-2">{derivePreview.reason}</p>
                </div>
              ) : (
                <>
                  <div className="rounded-xl border border-green-500/20 bg-green-500/10 px-4 py-3 text-sm text-green-200">
                    <div className="flex items-center gap-2">
                      <Check className="h-4 w-4" />
                      {t('internal.documentDetail.readyToGenerate').replace('{reportType}', reportTypeLabel)}
                    </div>
                    <p className="mt-1 text-slate-300">
                      {t('internal.documentDetail.editPayloadHelp')}
                    </p>
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-300">
                      {t('internal.documentDetail.reportPayloadLabel')}
                    </label>
                    <textarea
                      className="input min-h-[300px] font-mono text-xs"
                      value={reportPayloadText}
                      onChange={(e) => setReportPayloadText(e.target.value)}
                      spellCheck={false}
                    />
                  </div>
                </>
              )}
            </div>

            <div className="flex items-center justify-end gap-3 border-t border-white/10 p-6">
              <button
                className="btn-secondary"
                onClick={() => setShowDeriveModal(false)}
              >
                {t('internal.documentDetail.cancel')}
              </button>
              {derivePreview.allowed && (
                <button
                  className="btn-primary flex items-center gap-2"
                  onClick={handleCreateReport}
                  disabled={deriveReportMutation.isPending}
                >
                  <FileOutput className="h-4 w-4" />
                  {deriveReportMutation.isPending ? t('internal.documentDetail.creatingReport') : t('internal.documentDetail.createReport')}
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
