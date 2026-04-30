import { Link, useNavigate } from 'react-router-dom'
import { Clapperboard, ArrowRight, Film, Users, Star } from 'lucide-react'
import { useAuthStore, getPrimaryCIDTarget } from '@/store'
import { useEffect } from 'react'

const programs = [
  {
    id: 'cid',
    icon: Film,
    title: 'Acceso CID',
    description: 'Acceso directo a la plataforma. Puedes empezar con el plan Demo gratis y entrar hoy mismo a CID.',
    features: ['Plan Demo gratis', 'Acceso inmediato', 'Storyboard con IA', 'Reportes de producción'],
    cta: 'Crear cuenta demo CID',
    color: 'amber',
  },
  {
    id: 'demo',
    icon: Users,
    title: 'Demo guiada',
    description: 'Solicita una sesion personalizada con el equipo. Esta opcion no crea acceso inmediato a CID.',
    features: ['Demo personalizada de 30 min', 'Casos de uso de tu productora', 'Propuesta adaptada a tu flujo'],
    cta: 'Solicitar demo guiada',
    color: 'blue',
  },
  {
    id: 'partner',
    icon: Star,
    title: 'Programa Partner',
    description: 'Colabora con AILinkCinema como partner estratégico. Integraciones, white-label o distribución.',
    features: ['API de integración', 'Modelo de ingresos compartido', 'Soporte técnico dedicado'],
    cta: 'Ser partner',
    color: 'purple',
  },
]

export default function RegisterSelectPage() {
  const navigate = useNavigate()
  const { isAuthenticated, user } = useAuthStore()

  useEffect(() => {
    if (isAuthenticated) {
      navigate(getPrimaryCIDTarget(user), { replace: true })
    }
  }, [isAuthenticated, user, navigate])

  const colorClasses: Record<string, { border: string; bg: string; text: string; hover: string }> = {
    amber: {
      border: 'border-amber-500/30 hover:border-amber-500/60',
      bg: 'bg-amber-500/10',
      text: 'text-amber-400',
      hover: 'hover:bg-amber-500',
    },
    blue: {
      border: 'border-blue-500/30 hover:border-blue-500/60',
      bg: 'bg-blue-500/10',
      text: 'text-blue-400',
      hover: 'hover:bg-blue-500',
    },
    purple: {
      border: 'border-purple-500/30 hover:border-purple-500/60',
      bg: 'bg-purple-500/10',
      text: 'text-purple-400',
      hover: 'hover:bg-purple-500',
    },
  }

  return (
    <div className="min-h-screen bg-dark-300 text-white flex flex-col">
      {/* Nav */}
      <nav className="border-b border-white/5">
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-400 to-amber-600 flex items-center justify-center shadow-lg">
              <Clapperboard className="w-5 h-5 text-black" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-white tracking-tight">AILink</h1>
              <p className="text-xs text-amber-400/80 font-medium">CINEMA</p>
            </div>
          </div>
          <Link
            to="/login"
            className="text-sm text-gray-400 hover:text-white transition-colors"
          >
            Ya tengo cuenta
          </Link>
        </div>
      </nav>

      {/* Content */}
      <div className="flex-1 flex items-center justify-center px-6 py-16">
        <div className="w-full max-w-5xl">
          <div className="text-center mb-12">
              <h1 className="text-3xl md:text-4xl font-bold mb-4">
                Elige cómo quieres empezar
              </h1>
              <p className="text-gray-400 text-lg max-w-xl mx-auto">
                Si quieres entrar ahora a CID, usa Acceso CID. La demo guiada es una solicitud comercial.
              </p>
            </div>

          <div className="grid md:grid-cols-3 gap-6">
            {programs.map((program) => {
              const Icon = program.icon
              const colors = colorClasses[program.color]
              return (
                <div
                  key={program.id}
                  className={`relative p-8 bg-white/5 rounded-2xl border ${colors.border} transition-all duration-200 flex flex-col`}
                >
                  <div className={`w-14 h-14 rounded-xl ${colors.bg} flex items-center justify-center mb-6`}>
                    <Icon className={`w-7 h-7 ${colors.text}`} />
                  </div>

                  <h2 className="text-xl font-bold mb-3">{program.title}</h2>
                  <p className="text-gray-400 text-sm mb-6 leading-relaxed">
                    {program.description}
                  </p>

                  <ul className="space-y-2 mb-8 flex-1">
                    {program.features.map((feature) => (
                      <li key={feature} className="flex items-start gap-2 text-sm text-gray-400">
                        <span className={`mt-0.5 w-1.5 h-1.5 rounded-full ${colors.text.replace('text-', 'bg-')}`} />
                        {feature}
                      </li>
                    ))}
                  </ul>

                  <Link
                    to={`/register/${program.id}`}
                    className={`flex items-center justify-center gap-2 px-6 py-3 font-medium bg-white/5 border ${colors.border} rounded-xl transition-all duration-200 ${colors.hover} ${colors.hover === 'hover:bg-amber-500' ? 'hover:text-black' : 'hover:text-white'}`}
                  >
                    {program.cta} <ArrowRight className="w-4 h-4" />
                  </Link>
                </div>
              )
            })}
          </div>

          <p className="text-center text-gray-500 text-sm mt-8">
            ¿Ya tienes cuenta?{' '}
            <Link to="/login" className="text-amber-400 hover:text-amber-300 transition-colors">
              Inicia sesión
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
