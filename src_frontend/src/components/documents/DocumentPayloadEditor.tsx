import { useEffect, useState } from 'react'

interface DocumentPayloadEditorProps {
  initialValue?: Record<string, unknown>
  isSubmitting?: boolean
  onApprove: (payload?: Record<string, unknown>) => Promise<void> | void
}

export default function DocumentPayloadEditor({
  initialValue,
  isSubmitting = false,
  onApprove,
}: DocumentPayloadEditorProps) {
  const [payloadText, setPayloadText] = useState('{}')
  const [parseError, setParseError] = useState<string | null>(null)

  useEffect(() => {
    setPayloadText(JSON.stringify(initialValue || {}, null, 2))
  }, [initialValue])

  const handleApprove = async () => {
    try {
      setParseError(null)
      const parsed = JSON.parse(payloadText) as Record<string, unknown>
      await onApprove(parsed)
    } catch {
      setParseError('El payload debe ser JSON valido antes de aprobar.')
    }
  }

  return (
    <div className="space-y-4">
      <textarea
        className="input min-h-[320px] font-mono text-xs"
        value={payloadText}
        onChange={(event) => setPayloadText(event.target.value)}
      />
      {parseError && <p className="text-sm text-red-300">{parseError}</p>}
      <button type="button" className="btn-primary" disabled={isSubmitting} onClick={() => void handleApprove()}>
        {isSubmitting ? 'Aprobando...' : 'Aprobar estructura'}
      </button>
    </div>
  )
}
