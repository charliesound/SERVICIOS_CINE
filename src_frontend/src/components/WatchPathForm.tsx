import { FormEvent, useState } from 'react'
import { StorageWatchPathCreatePayload } from '@/types'

interface WatchPathFormProps {
  isSubmitting?: boolean
  onSubmit: (payload: StorageWatchPathCreatePayload) => void | Promise<void>
}

export default function WatchPathForm({ isSubmitting = false, onSubmit }: WatchPathFormProps) {
  const [watchPath, setWatchPath] = useState('')

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    await onSubmit({ watch_path: watchPath.trim() })
    setWatchPath('')
  }

  return (
    <form className="space-y-4" onSubmit={handleSubmit}>
      <div>
        <label className="label" htmlFor="watch_path">Watch Path</label>
        <input
          id="watch_path"
          className="input"
          value={watchPath}
          onChange={(event) => setWatchPath(event.target.value)}
          placeholder="/mnt/storage/project-a/incoming"
          required
        />
      </div>

      <button className="btn-secondary" type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Saving...' : 'Add Watch Path'}
      </button>
    </form>
  )
}
