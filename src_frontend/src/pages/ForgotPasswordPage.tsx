import { useState } from 'react'
import { Link } from 'react-router-dom'
import { KeyRound, ArrowLeft, Mail } from 'lucide-react'
import { authApi } from '@/api/auth'

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('')
  const [sent, setSent] = useState(false)
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)
    try {
      await authApi.forgotPassword({ email })
      setSent(true)
    } catch {
      setError('Error al enviar la solicitud. Intenta de nuevo.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-indigo-600/20 border border-indigo-500/30 mb-4">
            <KeyRound className="w-8 h-8 text-indigo-400" />
          </div>
          <h1 className="text-2xl font-bold text-white">
            {sent ? 'Revisa tu email' : '¿Has olvidado tu contraseña?'}
          </h1>
          <p className="text-slate-400 mt-2 text-sm">
            {sent
              ? 'Si el email está registrado, recibirás instrucciones para restablecer tu contraseña.'
              : 'Introduce tu email y te enviaremos un enlace para restablecerla.'}
          </p>
        </div>

        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-6">
          {sent ? (
            <div className="text-center">
              <Mail className="w-12 h-12 text-indigo-400 mx-auto mb-3" />
              <p className="text-slate-300 text-sm mb-4">
                Si el email está registrado, recibirás instrucciones para restablecer tu contraseña.
              </p>
              <Link
                to="/login"
                className="inline-flex items-center gap-2 text-indigo-400 hover:text-indigo-300 text-sm transition-colors"
              >
                <ArrowLeft className="w-4 h-4" />
                Volver al inicio de sesión
              </Link>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="label">Email</label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="tu@email.com"
                    className="input pl-10"
                    required
                  />
                </div>
              </div>

              {error && (
                <p className="text-red-400 text-sm">{error}</p>
              )}

              <button
                type="submit"
                disabled={isLoading}
                className="btn btn-primary w-full"
              >
                {isLoading ? 'Enviando...' : 'Enviar enlace de restablecimiento'}
              </button>

              <div className="text-center">
                <Link
                  to="/login"
                  className="inline-flex items-center gap-2 text-slate-400 hover:text-slate-300 text-sm transition-colors"
                >
                  <ArrowLeft className="w-4 h-4" />
                  Volver al inicio de sesión
                </Link>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  )
}
