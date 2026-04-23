import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Clapperboard, Mail, ArrowRight, Check } from 'lucide-react'
import { authApi } from '@/api'
import { useAuthStore, getPrimaryCIDTarget } from '@/store'
import type { RegisterDemoPayload } from '@/types'

export default function RegisterDemoPage() {
  const navigate = useNavigate()
  const { login, user } = useAuthStore()
  const [form, setForm] = useState<RegisterDemoPayload>({
    full_name: '',
    email: '',
    company: '',
    position: '',
    need: '',
    project_size: '',
    message: '',
  })
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [step, setStep] = useState<'form' | 'success'>('form')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    const tempPassword = `demo_${Math.random().toString(36).slice(2, 18)}`

    try {
      await authApi.registerDemoWithPassword({
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
          <div className="w-16 h-16 rounded-full bg-blue-500/20 flex items-center justify-center mx-auto mb-6">
            <Check className="w-8 h-8 text-blue-400" />
          </div>
          <h1 className="text-2xl font-bold mb-4">¡Solicitud enviada!</h1>
          <p className="text-gray-400 mb-8">
            Hemos recibido tu solicitud de demo. El equipo de AILinkCinema te contactará en las próximas 24 horas.
          </p>
          <button
            onClick={() => navigate(getPrimaryCIDTarget(user))}
            className="px-8 py-3 bg-blue-500 hover:bg-blue-400 text-black font-medium rounded-xl transition-colors flex items-center gap-2 mx-auto"
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
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center">
              <Clapperboard className="w-4 h-4 text-black" />
            </div>
            <span className="text-sm font-medium">Solicitar Demo</span>
          </div>
          <div className="w-16" />
        </div>
      </nav>

      <div className="flex-1 flex items-center justify-center px-6 py-12">
        <div className="w-full max-w-md">
          <div className="text-center mb-8">
            <h1 className="text-2xl font-bold mb-2">Solicitar una demo personalizada</h1>
            <p className="text-gray-400 text-sm">Te contactamos en 24h con una sesión adaptada a tu equipo.</p>
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
                  placeholder="tu@productora.com"
                  className="input pl-10"
                  required
                />
              </div>
            </div>

            <div>
              <label className="label">Empresa / Productora *</label>
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
              <label className="label">Cargo</label>
              <input
                type="text"
                value={form.position}
                onChange={(e) => setForm({ ...form, position: e.target.value })}
                placeholder="Tu posición en la empresa"
                className="input"
              />
            </div>

            <div>
              <label className="label">¿Qué necesitas? *</label>
              <select
                value={form.need}
                onChange={(e) => setForm({ ...form, need: e.target.value })}
                className="input"
                required
              >
                <option value="">Selecciona una opción</option>
                <option value="desglose">Desglose de guion</option>
                <option value="storyboard">Storyboard con IA</option>
                <option value="planificacion">Planificación visual</option>
                <option value="completo">Flujo completo CID</option>
                <option value="otro">Otro</option>
              </select>
            </div>

            <div>
              <label className="label">Tamaño del proyecto</label>
              <select
                value={form.project_size}
                onChange={(e) => setForm({ ...form, project_size: e.target.value })}
                className="input"
              >
                <option value="">Selecciona</option>
                <option value="pequeño">Pequeño (&lt; 90 min)</option>
                <option value="medio">Medio (90-120 min)</option>
                <option value="grande">Grande (&gt; 120 min)</option>
                <option value="serie">Serie / Episódico</option>
              </select>
            </div>

            <div>
              <label className="label">Mensaje (opcional)</label>
              <textarea
                value={form.message}
                onChange={(e) => setForm({ ...form, message: e.target.value })}
                placeholder="Cuéntanos más sobre tu proyecto..."
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
              className="w-full py-3 bg-blue-500 hover:bg-blue-400 text-black font-medium rounded-xl transition-colors flex items-center justify-center gap-2"
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
                <>Solicitar demo <ArrowRight className="w-4 h-4" /></>
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}
