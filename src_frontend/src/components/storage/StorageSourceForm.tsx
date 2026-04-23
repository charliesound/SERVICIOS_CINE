import { FormEvent, useEffect, useState } from 'react'
import { StorageSource, StorageSourceCreate, StorageSourceUpdate } from '@/types'

type StorageSourceFormProps = {
  mode: 'create'
  initialValue?: StorageSource
  isSubmitting?: boolean
  onSubmit: (payload: StorageSourceCreate) => Promise<void> | void
} | {
  mode: 'edit'
  initialValue?: StorageSource
  isSubmitting?: boolean
  onSubmit: (payload: StorageSourceUpdate) => Promise<void> | void
}

interface FormState {
  organization_id: string
  project_id: string
  name: string
  source_type: string
  mount_path: string
}

function mapSourceToState(source?: StorageSource): FormState {
  return {
    organization_id: source?.organization_id || '',
    project_id: source?.project_id || '',
    name: source?.name || '',
    source_type: source?.source_type || 'local_mounted_path',
    mount_path: source?.mount_path || '',
  }
}

export default function StorageSourceForm({
  mode,
  initialValue,
  isSubmitting = false,
  onSubmit,
}: StorageSourceFormProps) {
  const [form, setForm] = useState<FormState>(mapSourceToState(initialValue))

  useEffect(() => {
    setForm(mapSourceToState(initialValue))
  }, [initialValue])

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    if (mode === 'create') {
      await onSubmit({
        organization_id: form.organization_id || undefined,
        project_id: form.project_id,
        name: form.name,
        source_type: form.source_type,
        mount_path: form.mount_path,
      })
      return
    }

    await onSubmit({
      name: form.name,
      source_type: form.source_type,
      mount_path: form.mount_path,
    })
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {mode === 'create' && (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div>
            <label className="label">Organization ID</label>
            <input
              className="input"
              value={form.organization_id}
              onChange={(event) => setForm((current) => ({ ...current, organization_id: event.target.value }))}
              placeholder="org_demo"
            />
          </div>
          <div>
            <label className="label">Project ID</label>
            <input
              className="input"
              value={form.project_id}
              onChange={(event) => setForm((current) => ({ ...current, project_id: event.target.value }))}
              placeholder="proj_demo"
              required
            />
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <div>
          <label className="label">Nombre</label>
          <input
            className="input"
            value={form.name}
            onChange={(event) => setForm((current) => ({ ...current, name: event.target.value }))}
            placeholder="NAS Cliente"
            required
          />
        </div>
        <div>
          <label className="label">Tipo</label>
          <select
            className="input"
            value={form.source_type}
            onChange={(event) => setForm((current) => ({ ...current, source_type: event.target.value }))}
          >
            <option value="local_mounted_path">local_mounted_path</option>
            <option value="smb_mounted_path">smb_mounted_path</option>
            <option value="nfs_mounted_path">nfs_mounted_path</option>
          </select>
        </div>
      </div>

      <div>
        <label className="label">Mount Path</label>
        <input
          className="input"
          value={form.mount_path}
          onChange={(event) => setForm((current) => ({ ...current, mount_path: event.target.value }))}
          placeholder="C:/WINDOWS"
          required
        />
      </div>

      <button type="submit" className="btn-primary" disabled={isSubmitting}>
        {isSubmitting ? 'Guardando...' : mode === 'create' ? 'Crear source' : 'Guardar cambios'}
      </button>
    </form>
  )
}
