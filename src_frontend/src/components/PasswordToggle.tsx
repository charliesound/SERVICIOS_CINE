import { Eye, EyeOff } from 'lucide-react'

interface PasswordToggleProps {
  visible: boolean
  onToggle: () => void
}

export const PasswordToggle = ({ visible, onToggle }: PasswordToggleProps) => {
  return (
    <button
      type="button"
      onClick={onToggle}
      className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 transition-colors"
      aria-label={visible ? 'Ocultar contraseña' : 'Mostrar contraseña'}
    >
      {visible ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
    </button>
  )
}
