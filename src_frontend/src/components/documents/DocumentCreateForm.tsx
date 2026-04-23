import { FormEvent, useState } from 'react'
import { DocumentAssetCreate } from '@/types'

interface DocumentCreateFormProps {
  isSubmitting?: boolean
  onSubmit: (payload: DocumentAssetCreate) => Promise<void> | void
}

export default function DocumentCreateForm({ isSubmitting = false, onSubmit }: DocumentCreateFormProps) {
  const [form, setForm] = useState<DocumentAssetCreate>({
    organization_id: '',
    project_id: '',
    source_kind: 'mounted_path',
    original_path: '',
    media_asset_id: '',
    file_name: '',
    storage_source_id: '',
  })

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    await onSubmit({
      organization_id: form.organization_id || undefined,
      project_id: form.project_id,
      source_kind: form.source_kind,
      original_path: form.original_path || undefined,
      media_asset_id: form.media_asset_id || undefined,
      file_name: form.file_name || undefined,
      storage_source_id: form.storage_source_id || undefined,
    })
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <div>
          <label className="label">Organization ID</label>
          <input
            className="input"
            value={form.organization_id || ''}
            onChange={(event) => setForm((current) => ({ ...current, organization_id: event.target.value }))}
            placeholder="org_doc"
          />
        </div>
        <div>
          <label className="label">Project ID</label>
          <input
            className="input"
            value={form.project_id}
            onChange={(event) => setForm((current) => ({ ...current, project_id: event.target.value }))}
            placeholder="proj_doc"
            required
          />
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <div>
          <label className="label">Source kind</label>
          <select
            className="input"
            value={form.source_kind}
            onChange={(event) => setForm((current) => ({ ...current, source_kind: event.target.value }))}
          >
            <option value="mounted_path">mounted_path</option>
            <option value="media_asset">media_asset</option>
          </select>
        </div>
        <div>
          <label className="label">File name (opcional)</label>
          <input
            className="input"
            value={form.file_name || ''}
            onChange={(event) => setForm((current) => ({ ...current, file_name: event.target.value }))}
            placeholder="camera_notes.txt"
          />
        </div>
      </div>

      <div>
        <label className="label">Original path</label>
        <input
          className="input"
          value={form.original_path || ''}
          onChange={(event) => setForm((current) => ({ ...current, original_path: event.target.value }))}
          placeholder="C:/WINDOWS/Temp/camera_notes.txt"
        />
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <div>
          <label className="label">Media asset ID (opcional)</label>
          <input
            className="input"
            value={form.media_asset_id || ''}
            onChange={(event) => setForm((current) => ({ ...current, media_asset_id: event.target.value }))}
            placeholder="asset-id"
          />
        </div>
        <div>
          <label className="label">Storage source ID (opcional)</label>
          <input
            className="input"
            value={form.storage_source_id || ''}
            onChange={(event) => setForm((current) => ({ ...current, storage_source_id: event.target.value }))}
            placeholder="source-id"
          />
        </div>
      </div>

      <button type="submit" className="btn-primary" disabled={isSubmitting}>
        {isSubmitting ? 'Registrando...' : 'Registrar documento'}
      </button>
    </form>
  )
}
