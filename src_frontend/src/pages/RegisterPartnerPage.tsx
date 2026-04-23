import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Clapperboard, Mail, ArrowRight, Check } from 'lucide-react'
import { authApi } from '@/api'
import { useAuthStore, getPrimaryCIDTarget } from '@/store'
import type { RegisterPartnerPayload } from '@/types'

export default function RegisterPartnerPage() {
  const navigate = useNavigate()
  const { login, user } = useAuthStore()
  const [form, setForm] = useState<RegisterPartnerPayload>({
    full_name: '',
    email: '',
    company: '',
    collaboration_type: '',
    message: '',
  })
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [step, setStep] = useState<'form' | 'success'>('form')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    const tempPassword = `partner_${Math.random().toString(36).slice(2, 18)}`

    try {
      await authApi.registerPartnerWithPassword({
        ...form,
        password: tempPassword,
      })
      await login(form.email, tempPassword)
      setStep('success')
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        'Error en la solicitud'
      setError(message)
    } finally {
      setIsLoading(false)
    }
  }

  if (step === 'success') {
    return (
      <div className="min-h-screen bg-dark-300 flex items-center justify-center px-6">
        <div className="text-center max-w-md">
          <div className="w-16 h-16 rounded-full bg-purple-500/20 flex items-center justify-center mx-auto mb-6">
            <Check className="w-8 h-8 text-purple-400" />
          </div>
          <h1 className="text-2xl font-bold mb-4">¡Solicitud enviada!</h1>
          <p className="text-gray-400 mb-8">
            Hemos recibido tu interés como partner. El equipo de AILinkCinema se pondrá en contacto contigo.
          </p>
          <button
            onClick={() => navigate(getPrimaryCIDTarget(user))}
            className="px-8 py-3 bg-purple-500 hover:bg-purple-400 text-black font-medium rounded-xl transition-colors flex items-center gap-2 mx-auto"
          >
            Ir al dashboard <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-dark-300 text-white flex flex-col">
      <nav className="border-b border-white/5">
        <div className="max-w-lg mx-auto px-6 py-4 flex items-center justify-between">
          <Link to="/register/select" className="text-sm text-gray-400 hover:text-white transition-colors">
            ← Volver
          </Link>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-400 to-purple-600 flex items-center justify-center">
              <Clapperboard className="w-4 h-4 text-black" />
            </div>
            <span className="text-sm font-medium">Programa Partner</span>
          </div>
          <div className="w-16" />
        </div>
      </nav>

      <div className="flex-1 flex items-center justify-center px-6 py-12">
        <div className="w-full max-w-md">
          <div className="text-center mb-8">
            <h1 className="text-2xl font-bold mb-2">Ser partner de AILinkCinema</h1>
            <p className="text-gray-400 text-sm">Únete como partner estratégico. Te contactaremos para explorar la colaboración.</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="label">Nombre completo *</label>
              <input
                type="text"
                value={form.full_name}
                onChange={(e) => setForm({ ...form, full_name: e.target.value })}
                placeholder="Tu nombre"
                className="input"
                required
              />
            </div>

            <div>
              <label className="label">Email *</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                <input
                  type="email"
                  value={form.email}
                  onChange={(e) => setForm({ ...form, email: e.target.value })}
                  placeholder="tu@empresa.com"
                  className="input pl-10"
                  required
                />
              </div>
            </div>

            <div>
              <label className="label">Empresa *</label>
              <input
                type="text"
                value={form.company}
                onChange={(e) => setForm({ ...form, company: e.target.value })}
                placeholder="Nombre de tu empresa"
                className="input"
                required
              />
            </div>

            <div>
              <label className="label">Tipo de colaboración *</label>
              <select
                value={form.collaboration_type}
                onChange={(e) => setForm({ ...form, collaboration_type: e.target.value })}
                className="input"
                required
              >
                <option value="">Selecciona una opción</option>
                <option value="integrador">Integrador tecnológico</option>
                <option value="distribuidor">Distribuidor regional</option>
                <option value="whitelabel">White-label</option>
                <option value="agencia">Agencia de producción</option>
                <option value="otro">Otro</option>
              </select>
            </div>

            <div>
              <label className="label">Mensaje (opcional)</label>
              <textarea
                value={form.message}
                onChange={(e) => setForm({ ...form, message: e.target.value })}
                placeholder="Cuéntanos sobre tu propuesta de colaboración..."
                className="input min-h-[80px] resize-none"
              />
            </div>

            {error && (
              <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-sm">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-3 bg-purple-500 hover:bg-purple-400 text-black font-medium rounded-xl transition-colors flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <span className="flex items-center gap-2">
                  <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Enviando...
                </span>
              ) : (
                <>Enviar solicitud <ArrowRight className="w-4 h-4" /></>
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}
