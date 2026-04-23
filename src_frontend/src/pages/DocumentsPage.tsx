import type { FormEvent } from 'react'
import { useMemo, useState } from 'react'
import axios from 'axios'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { FileText, RefreshCw } from 'lucide-react'
import StorageStatusBadge from '@/components/StorageStatusBadge'
import { useCreateDocument, useDocuments } from '@/hooks'
import { DocumentAssetCreatePayload } from '@/types'

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

export default function DocumentsPage() {
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()
  const [submitError, setSubmitError] = useState<string | null>(null)
  const [mediaAssetId, setMediaAssetId] = useState(searchParams.get('media_asset_id') ?? '')
  const [organizationId, setOrganizationId] = useState('')
  const [projectId, setProjectId] = useState('')
  const [storageSourceId, setStorageSourceId] = useState('')
  const [fileName, setFileName] = useState('')
  const [mimeType, setMimeType] = useState('')
  const [originalPath, setOriginalPath] = useState('')

  const filters = useMemo(() => {
    const status = searchParams.get('status')?.trim() || undefined
    const docType = searchParams.get('doc_type')?.trim() || undefined
    return { status, doc_type: docType }
  }, [searchParams])

  const documentsQuery = useDocuments(filters)
  const createDocument = useCreateDocument()

  const applyFilter = (key: string, value: string) => {
    const next = new URLSearchParams(searchParams)
    if (value.trim()) next.set(key, value.trim())
    else next.delete(key)
    setSearchParams(next)
  }

  const handleCreateDocument = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setSubmitError(null)

    const payload: DocumentAssetCreatePayload = {
      media_asset_id: mediaAssetId.trim() || undefined,
      organization_id: organizationId.trim() || undefined,
      project_id: projectId.trim() || undefined,
      storage_source_id: storageSourceId.trim() || undefined,
      file_name: fileName.trim() || undefined,
      mime_type: mimeType.trim() || undefined,
      original_path: originalPath.trim() || undefined,
    }

    try {
      const document = await createDocument.mutateAsync(payload)
      navigate(`/documents/${document.id}`)
    } catch (error) {
      setSubmitError(getErrorMessage(error, 'Unable to create document'))
    }
  }

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h1 className="heading-lg flex items-center gap-3">
            <FileText className="h-6 w-6 text-amber-400" />
            Documents
          </h1>
          <p className="mt-1 text-slate-400">Register indexed files as documents and prepare them for human review.</p>
        </div>
        <button className="btn-secondary flex items-center gap-2" onClick={() => documentsQuery.refetch()}>
          <RefreshCw className={`h-4 w-4 ${documentsQuery.isFetching ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.15fr,1.45fr]">
        <section className="card card-hover">
          <div className="mb-5">
            <h2 className="heading-md">Register Document</h2>
            <p className="mt-1 text-sm text-slate-400">
              Prefer `media_asset_id` when the file already exists in indexed ingest assets.
            </p>
          </div>

          {submitError && (
            <div className="mb-4 rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-200">
              {submitError}
            </div>
          )}

          <form className="space-y-4" onSubmit={handleCreateDocument}>
            <div>
              <label className="label" htmlFor="document_media_asset_id">Media Asset ID</label>
              <input
                id="document_media_asset_id"
                className="input"
                value={mediaAssetId}
                onChange={(event) => setMediaAssetId(event.target.value)}
                placeholder="Preferred when document comes from ingest assets"
              />
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <label className="label" htmlFor="document_org_id">Organization ID</label>
                <input id="document_org_id" className="input" value={organizationId} onChange={(event) => setOrganizationId(event.target.value)} />
              </div>
              <div>
                <label className="label" htmlFor="document_project_id">Project ID</label>
                <input id="document_project_id" className="input" value={projectId} onChange={(event) => setProjectId(event.target.value)} />
              </div>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <label className="label" htmlFor="document_storage_source_id">Storage Source ID</label>
                <input id="document_storage_source_id" className="input" value={storageSourceId} onChange={(event) => setStorageSourceId(event.target.value)} />
              </div>
              <div>
                <label className="label" htmlFor="document_file_name">File Name</label>
                <input id="document_file_name" className="input" value={fileName} onChange={(event) => setFileName(event.target.value)} />
              </div>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <label className="label" htmlFor="document_mime_type">MIME Type</label>
                <input id="document_mime_type" className="input" value={mimeType} onChange={(event) => setMimeType(event.target.value)} />
              </div>
              <div>
                <label className="label" htmlFor="document_original_path">Original Path</label>
                <input id="document_original_path" className="input" value={originalPath} onChange={(event) => setOriginalPath(event.target.value)} />
              </div>
            </div>

            <button className="btn-primary" type="submit" disabled={createDocument.isPending}>
              {createDocument.isPending ? 'Creating...' : 'Create Document'}
            </button>
          </form>
        </section>

        <section className="space-y-6">
          <div className="card card-hover">
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <label className="label" htmlFor="document_status_filter">Status</label>
                <select
                  id="document_status_filter"
                  className="input"
                  value={filters.status ?? ''}
                  onChange={(event) => applyFilter('status', event.target.value)}
                >
                  <option value="">All statuses</option>
                  <option value="registered">registered</option>
                  <option value="extracted">extracted</option>
                  <option value="classified">classified</option>
                  <option value="structured">structured</option>
                  <option value="approved">approved</option>
                  <option value="pending_ocr">pending_ocr</option>
                  <option value="unsupported">unsupported</option>
                  <option value="error">error</option>
                </select>
              </div>
              <div>
                <label className="label" htmlFor="document_doc_type_filter">Doc Type</label>
                <select
                  id="document_doc_type_filter"
                  className="input"
                  value={filters.doc_type ?? ''}
                  onChange={(event) => applyFilter('doc_type', event.target.value)}
                >
                  <option value="">All document types</option>
                  <option value="camera_report">camera_report</option>
                  <option value="sound_report">sound_report</option>
                  <option value="script_note">script_note</option>
                  <option value="director_note">director_note</option>
                  <option value="operator_note">operator_note</option>
                  <option value="unknown_document">unknown_document</option>
                </select>
              </div>
            </div>
          </div>

          <section className="card card-hover space-y-4">
            {documentsQuery.error && (
              <div className="rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-200">
                {getErrorMessage(documentsQuery.error, 'Unable to load documents')}
              </div>
            )}

            {documentsQuery.isLoading && <div className="text-sm text-slate-400">Loading documents...</div>}

            {!documentsQuery.isLoading && !documentsQuery.error && (!documentsQuery.data || documentsQuery.data.length === 0) && (
              <div className="rounded-xl border border-dashed border-white/10 px-6 py-10 text-center text-sm text-slate-400">
                No documents found for the current filters.
              </div>
            )}

            {documentsQuery.data?.map((document) => (
              <article key={document.id} className="rounded-2xl border border-white/10 bg-dark-300/40 p-5">
                <div className="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
                  <div className="space-y-3 min-w-0">
                    <div className="flex flex-wrap items-center gap-3">
                      <h2 className="text-lg font-semibold text-white break-all">{document.file_name}</h2>
                      <StorageStatusBadge status={document.status} />
                    </div>
                    <div className="grid gap-2 text-sm text-slate-300 md:grid-cols-2">
                      <p><span className="text-slate-500">ID:</span> {document.id}</p>
                      <p><span className="text-slate-500">Extension:</span> {document.file_extension}</p>
                      <p><span className="text-slate-500">Source Kind:</span> {document.source_kind}</p>
                      <p><span className="text-slate-500">Media Asset:</span> {document.media_asset_id || 'n/a'}</p>
                      <p><span className="text-slate-500">Doc Type:</span> {document.classification?.doc_type || 'Pending classification'}</p>
                    </div>
                  </div>

                  <Link to={`/documents/${document.id}`} className="btn-secondary">
                    Open Detail
                  </Link>
                </div>
              </article>
            ))}
          </section>
        </section>
      </div>
    </div>
  )
}
