import { FormEvent, useState } from 'react'

interface WatchPathFormProps {
  isSubmitting?: boolean
  onSubmit: (watchPath: string) => Promise<void> | void
}

export default function WatchPathForm({ isSubmitting = false, onSubmit }: WatchPathFormProps) {
  const [watchPath, setWatchPath] = useState('')

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    await onSubmit(watchPath)
    setWatchPath('')
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <div>
        <label className="label">Watch path</label>
        <input
          className="input"
          value={watchPath}
          onChange={(event) => setWatchPath(event.target.value)}
          placeholder="C:/WINDOWS/Temp"
          required
        />
      </div>
      <button type="submit" className="btn-secondary" disabled={isSubmitting}>
        {isSubmitting ? 'Creando...' : 'Crear watch path'}
      </button>
    </form>
  )
}
