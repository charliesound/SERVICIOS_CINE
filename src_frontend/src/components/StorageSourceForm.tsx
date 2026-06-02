import { FormEvent, useState } from 'react'
import { useLanguage } from '@/i18n'
import { StorageSource, StorageSourceCreatePayload, StorageSourceUpdatePayload } from '@/types'

interface StorageSourceCreateFormProps {
  mode: 'create'
  initialValues?: Partial<StorageSource>
  submitLabel: string
  isSubmitting?: boolean
  onSubmit: (payload: StorageSourceCreatePayload) => void | Promise<void>
}

interface StorageSourceEditFormProps {
  mode: 'edit'
  initialValues?: Partial<StorageSource>
  submitLabel: string
  isSubmitting?: boolean
  onSubmit: (payload: StorageSourceUpdatePayload) => void | Promise<void>
}

type StorageSourceFormProps = StorageSourceCreateFormProps | StorageSourceEditFormProps

export default function StorageSourceForm({
  mode,
  initialValues,
  submitLabel,
  isSubmitting = false,
  onSubmit,
}: StorageSourceFormProps) {
  const { t } = useLanguage()
  const [organizationId, setOrganizationId] = useState(initialValues?.organization_id ?? '')
  const [projectId, setProjectId] = useState(initialValues?.project_id ?? '')
  const [name, setName] = useState(initialValues?.name ?? '')
  const [sourceType, setSourceType] = useState(initialValues?.source_type ?? 'local')
  const [mountPath, setMountPath] = useState(initialValues?.mount_path ?? '')
  const [status, setStatus] = useState(initialValues?.status ?? 'active')

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    if (mode === 'create') {
      await onSubmit({
        organization_id: organizationId.trim(),
        project_id: projectId.trim(),
        name: name.trim(),
        source_type: sourceType.trim(),
        mount_path: mountPath.trim(),
      })
      return
    }

    await onSubmit({
      name: name.trim(),
      status,
    })
  }

  return (
    <form className="space-y-4" onSubmit={handleSubmit}>
      {mode === 'create' && (
        <>
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <label className="label" htmlFor="organization_id">{t('internal.storageSourceForm.organizationId')}</label>
              <input
                id="organization_id"
                className="input"
                value={organizationId}
                onChange={(event) => setOrganizationId(event.target.value)}
                placeholder={t('internal.storageSourceForm.organizationIdPlaceholder')}
                required
              />
            </div>
            <div>
              <label className="label" htmlFor="project_id">{t('internal.storageSourceForm.projectId')}</label>
              <input
                id="project_id"
                className="input"
                value={projectId}
                onChange={(event) => setProjectId(event.target.value)}
                placeholder={t('internal.storageSourceForm.projectIdPlaceholder')}
                required
              />
            </div>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <label className="label" htmlFor="source_name">{t('internal.storageSourceForm.name')}</label>
              <input
                id="source_name"
                className="input"
                value={name}
                onChange={(event) => setName(event.target.value)}
                placeholder={t('internal.storageSourceForm.namePlaceholder')}
                required
              />
            </div>
            <div>
              <label className="label" htmlFor="source_type">{t('internal.storageSourceForm.sourceType')}</label>
              <input
                id="source_type"
                className="input"
                value={sourceType}
                onChange={(event) => setSourceType(event.target.value)}
                placeholder={t('internal.storageSourceForm.sourceTypePlaceholder')}
                required
              />
            </div>
          </div>

          <div>
            <label className="label" htmlFor="mount_path">{t('internal.storageSourceForm.mountPath')}</label>
            <input
              id="mount_path"
              className="input"
              value={mountPath}
              onChange={(event) => setMountPath(event.target.value)}
              placeholder={t('internal.storageSourceForm.mountPathPlaceholder')}
              required
            />
          </div>
        </>
      )}

      {mode === 'edit' && (
        <div className="grid gap-4 md:grid-cols-2">
          <div>
            <label className="label" htmlFor="edit_name">{t('internal.storageSourceForm.name')}</label>
            <input
              id="edit_name"
              className="input"
              value={name}
              onChange={(event) => setName(event.target.value)}
              required
            />
          </div>
          <div>
            <label className="label" htmlFor="edit_status">{t('internal.storageSourceForm.status')}</label>
            <select
              id="edit_status"
              className="input"
              value={status}
              onChange={(event) => setStatus(event.target.value)}
            >
              <option value="active">active</option>
              <option value="inactive">inactive</option>
              <option value="error">error</option>
            </select>
          </div>
        </div>
      )}

      <button className="btn-primary" type="submit" disabled={isSubmitting}>
        {isSubmitting ? t('internal.storageSourceForm.saving') : submitLabel}
      </button>
    </form>
  )
}
