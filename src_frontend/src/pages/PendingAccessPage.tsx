import { Link } from 'react-router-dom'
import { useAuthStore } from '@/store'
import { Mail, Clock, ArrowRight } from 'lucide-react'

export default function PendingAccessPage() {
  const { user } = useAuthStore()

  const programLabels: Record<string, string> = {
    cid_user: 'Programa CID',
    demo_request: 'Demo personalizada',
    partner_interest: 'Programa Partner',
  }

  return (
    <div className="min-h-screen bg-dark-300 flex items-center justify-center px-6">
      <div className="w-full max-w-md text-center">
        <div className="w-16 h-16 rounded-full bg-amber-500/10 flex items-center justify-center mx-auto mb-6">
          <Clock className="w-8 h-8 text-amber-400" />
        </div>

        <h1 className="text-2xl font-bold mb-4">Acceso pendiente</h1>
        <p className="text-gray-400 mb-8">
          Tu solicitud para el{' '}
          <span className="text-amber-400 font-medium">
            {programLabels[user?.signup_type || 'cid_user'] || 'programa'}
          </span>{' '}
          está siendo revisada por el equipo de AILinkCinema.
        </p>

        <div className="p-5 bg-white/5 rounded-xl border border-white/10 text-left mb-6 space-y-3">
          <div className="flex items-center gap-3 text-sm">
            <Clock className="w-4 h-4 text-amber-400" />
            <span className="text-gray-400">Recibirás un email en: <span className="text-white">{user?.email}</span></span>
          </div>
          <div className="flex items-center gap-3 text-sm">
            <Mail className="w-4 h-4 text-amber-400" />
            <span className="text-gray-400">Tiempo de respuesta habitual: 24-48h</span>
          </div>
        </div>

        <div className="space-y-3">
          <Link
            to="/dashboard"
            className="block w-full py-3 bg-amber-500 hover:bg-amber-400 text-black font-medium rounded-xl transition-colors flex items-center justify-center gap-2"
          >
            Ir al dashboard <ArrowRight className="w-4 h-4" />
          </Link>
          <Link
            to="/contacto"
            className="block w-full py-3 border border-white/10 hover:border-white/20 text-white rounded-xl transition-colors"
          >
            Contactar con el equipo
          </Link>
        </div>
      </div>
    </div>
  )
}
