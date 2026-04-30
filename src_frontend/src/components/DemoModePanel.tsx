import { useState } from 'react'
import { DEMO_GUIDE } from '../data/demoProjectGuide'

interface DemoModePanelProps {
  projectId?: string
  onClose?: () => void
}

export default function DemoModePanel({ projectId, onClose }: DemoModePanelProps) {
  const [currentStep, setCurrentStep] = useState(0)

  const step = DEMO_GUIDE[currentStep]
  const isLastStep = currentStep === DEMO_GUIDE.length - 1

  const handleNext = () => {
    if (!isLastStep) {
      setCurrentStep(currentStep + 1)
    }
  }

  const handlePrev = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1)
    }
  }

  const handleGoToModule = () => {
    if (projectId) {
      const route = step.targetRoute.replace(':projectId', projectId)
      window.location.href = route
    }
  }

  return (
    <div className="fixed bottom-4 right-4 w-96 bg-white rounded-lg shadow-xl border border-gray-200 z-50">
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-bold text-blue-900">Demo Guiada</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            ✕
          </button>
        </div>
        <p className="text-sm text-gray-500 mt-1">
          Paso {step.step} de {DEMO_GUIDE.length}
        </p>
      </div>

      <div className="p-4">
        <h4 className="text-xl font-semibold text-gray-900">{step.title}</h4>
        <p className="text-gray-600 mt-2">{step.description}</p>

        {step.talkingPoints.length > 0 && (
          <div className="mt-4">
            <h5 className="text-sm font-medium text-gray-700">Puntos clave:</h5>
            <ul className="mt-2 space-y-1">
              {step.talkingPoints.map((point, i) => (
                <li key={i} className="text-sm text-gray-600 flex items-start">
                  <span className="text-blue-500 mr-2">•</span>
                  {point}
                </li>
              ))}
            </ul>
          </div>
        )}

        <div className="mt-4 p-3 bg-yellow-50 text-yellow-800 text-sm rounded">
          <strong>Resultado esperado:</strong> {step.expectedOutcome}
        </div>
      </div>

      <div className="p-4 border-t border-gray-200 flex gap-2">
        <button
          onClick={handlePrev}
          disabled={currentStep === 0}
          className="flex-1 px-4 py-2 border border-gray-300 rounded text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Anterior
        </button>
        
        {projectId && (
          <button
            onClick={handleGoToModule}
            className="flex-1 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Ir al módulo
          </button>
        )}
        
        <button
          onClick={handleNext}
          disabled={isLastStep}
          className="flex-1 px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLastStep ? 'Finalizar' : 'Siguiente'}
        </button>
      </div>

      <div className="px-4 pb-4">
        <div className="flex gap-1">
          {DEMO_GUIDE.map((_, i) => (
            <div
              key={i}
              className={`h-1 flex-1 rounded ${
                i <= currentStep ? 'bg-blue-600' : 'bg-gray-200'
              }`}
            />
          ))}
        </div>
      </div>
    </div>
  )
}