import { FormEvent, useState } from 'react'
import { StorageAuthorizationCreatePayload } from '@/types'

interface StorageAuthorizationFormProps {
  isSubmitting?: boolean
  onSubmit: (payload: StorageAuthorizationCreatePayload) => void | Promise<void>
}

export default function StorageAuthorizationForm({
  isSubmitting = false,
  onSubmit,
}: StorageAuthorizationFormProps) {
  const [authorizationMode, setAuthorizationMode] = useState('read')
  const [scopePath, setScopePath] = useState('')
  const [expiresAt, setExpiresAt] = useState('')

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    await onSubmit({
      authorization_mode: authorizationMode,
      scope_path: scopePath.trim(),
      expires_at: expiresAt ? new Date(expiresAt).toISOString() : null,
    })
    setScopePath('')
    setExpiresAt('')
    setAuthorizationMode('read')
  }

  return (
    <form className="space-y-4" onSubmit={handleSubmit}>
      <div className="grid gap-4 md:grid-cols-2">
        <div>
          <label className="label" htmlFor="authorization_mode">Authorization Mode</label>
          <select
            id="authorization_mode"
            className="input"
            value={authorizationMode}
            onChange={(event) => setAuthorizationMode(event.target.value)}
          >
            <option value="read">read</option>
            <option value="write">write</option>
            <option value="read_write">read_write</option>
          </select>
        </div>
        <div>
          <label className="label" htmlFor="expires_at">Expires At</label>
          <input
            id="expires_at"
            className="input"
            type="datetime-local"
            value={expiresAt}
            onChange={(event) => setExpiresAt(event.target.value)}
          />
        </div>
      </div>

      <div>
        <label className="label" htmlFor="scope_path">Scope Path</label>
        <input
          id="scope_path"
          className="input"
          value={scopePath}
          onChange={(event) => setScopePath(event.target.value)}
          placeholder="/mnt/storage/project-a/assets"
          required
        />
      </div>

      <button className="btn-secondary" type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Authorizing...' : 'Authorize Source'}
      </button>
    </form>
  )
}
