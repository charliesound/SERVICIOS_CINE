import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore, getPrimaryCIDTarget } from '@/store'
import { Clapperboard, ArrowRight, Check } from 'lucide-react'

const steps = [
  {
    title: 'Configura tu perfil',
    description: 'Completa tu información de perfil y preferencias.',
  },
  {
    title: 'Conecta tus fuentes de almacenamiento',
    description: 'Vincula Dropbox, Google Drive o un servidor local para acceder a tus guiones.',
  },
  {
    title: 'Sube tu primer guion',
    description: 'Comienza con el análisis automático de escenas y personajes.',
  },
]

export default function OnboardingPage() {
  const navigate = useNavigate()
  const { user, completeOnboarding, updateUser } = useAuthStore()
  const [currentStep, setCurrentStep] = useState(0)
  const [fullName, setFullName] = useState(user?.full_name || '')
  const [company, setCompany] = useState(user?.company || '')

  const handleFinish = async () => {
    if (fullName || company) {
      updateUser({ full_name: fullName, company })
    }
    completeOnboarding()
    navigate(getPrimaryCIDTarget(user))
  }

  return (
    <div className="min-h-screen bg-dark-300 flex items-center justify-center px-6">
      <div className="w-full max-w-lg">
        <div className="text-center mb-10">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-amber-400 to-amber-600 flex items-center justify-center mx-auto mb-4 shadow-lg shadow-amber-500/20">
            <Clapperboard className="w-8 h-8 text-black" />
          </div>
          <h1 className="text-2xl font-bold mb-2">Bienvenido a AILinkCinema</h1>
          <p className="text-gray-400">
            Completa estos pasos para sacar el máximo partido a CID.
          </p>
        </div>

        <div className="space-y-4 mb-8">
          {steps.map((step, i) => (
            <div
              key={i}
              className={`p-5 rounded-xl border transition-all cursor-pointer ${
                i === currentStep
                  ? 'bg-amber-500/10 border-amber-500/30'
                  : i < currentStep
                  ? 'bg-green-500/5 border-green-500/20'
                  : 'bg-white/5 border-white/10'
              }`}
              onClick={() => setCurrentStep(i)}
            >
              <div className="flex items-center gap-4">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                  i < currentStep
                    ? 'bg-green-500 text-black'
                    : i === currentStep
                    ? 'bg-amber-500 text-black'
                    : 'bg-white/10 text-gray-400'
                }`}>
                  {i < currentStep ? <Check className="w-4 h-4" /> : i + 1}
                </div>
                <div>
                  <h3 className={`font-medium ${i === currentStep ? 'text-white' : 'text-gray-400'}`}>
                    {step.title}
                  </h3>
                  <p className="text-sm text-gray-500">{step.description}</p>
                </div>
              </div>
            </div>
          ))}
        </div>

        {currentStep === 0 && (
          <div className="p-6 bg-white/5 rounded-xl border border-white/10 mb-6 space-y-4">
            <div>
              <label className="label">Nombre completo</label>
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="Tu nombre"
                className="input"
              />
            </div>
            <div>
              <label className="label">Empresa / Productora</label>
              <input
                type="text"
                value={company}
                onChange={(e) => setCompany(e.target.value)}
                placeholder="Nombre de tu empresa"
                className="input"
              />
            </div>
          </div>
        )}

        <div className="flex gap-3">
          {currentStep > 0 && (
            <button
              onClick={() => setCurrentStep(currentStep - 1)}
              className="flex-1 py-3 border border-white/10 hover:border-white/20 text-white rounded-xl transition-colors"
            >
              Atrás
            </button>
          )}
          {currentStep < steps.length - 1 ? (
            <button
              onClick={() => setCurrentStep(currentStep + 1)}
              className="flex-1 py-3 bg-amber-500 hover:bg-amber-400 text-black font-medium rounded-xl transition-colors flex items-center justify-center gap-2"
            >
              Siguiente <ArrowRight className="w-4 h-4" />
            </button>
          ) : (
            <button
              onClick={handleFinish}
              className="flex-1 py-3 bg-amber-500 hover:bg-amber-400 text-black font-medium rounded-xl transition-colors flex items-center justify-center gap-2"
            >
              Empezar con CID <ArrowRight className="w-4 h-4" />
            </button>
          )}
        </div>

        <p className="text-center text-gray-500 text-sm mt-6">
          Puedes saltarte este paso.{' '}
          <button
            onClick={handleFinish}
            className="text-amber-400 hover:text-amber-300 transition-colors"
          >
            Ir directamente a CID
          </button>
        </p>
      </div>
    </div>
  )
}
