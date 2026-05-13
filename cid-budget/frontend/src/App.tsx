import { useState } from 'react'
import BudgetEstimator from './pages/BudgetEstimator'

export default function App() {
  const [projectId, setProjectId] = useState(localStorage.getItem('cid_budget_project') || '')

  return (
    <div className="min-h-screen bg-dark-300">
      <header className="border-b border-white/5 bg-dark-400/50 backdrop-blur-xl">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-amber-400 to-amber-600 flex items-center justify-center">
              <span className="text-black font-bold text-sm">€</span>
            </div>
            <h1 className="text-lg font-bold text-white">CID Budget Estimator</h1>
          </div>
          <div className="flex items-center gap-3">
            <input
              className="bg-dark-600 border border-white/10 rounded-lg px-3 py-2 text-sm text-white w-48"
              placeholder="Project ID"
              value={projectId}
              onChange={(e) => {
                setProjectId(e.target.value)
                localStorage.setItem('cid_budget_project', e.target.value)
              }}
            />
            <span className="badge-blue text-xs">Standalone</span>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-8">
        {projectId ? (
          <BudgetEstimator key={projectId} projectId={projectId} />
        ) : (
          <div className="card text-center py-20">
            <p className="text-6xl mb-4">💰</p>
            <h2 className="text-xl font-semibold text-white mb-2">CID Budget Estimator</h2>
            <p className="text-cine-400">Introduce un Project ID arriba para empezar</p>
          </div>
        )}
      </main>
    </div>
  )
}
