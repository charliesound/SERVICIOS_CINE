import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { DollarSign, Download, RefreshCw, AlertTriangle } from 'lucide-react'
import { budgetsApi } from '@/api/budget'
import type { BudgetEstimate, BudgetLine } from '@/api/budget'

const LEVEL_LABELS: Record<string, string> = {
  low: 'Conservador',
  medium: 'Medio',
  high: 'Alto',
}

const CONFIDENCE_LABELS: Record<string, string> = {
  low: 'Baja',
  medium: 'Media',
  high: 'Alta',
}

function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('es-ES', {
    style: 'currency',
    currency: 'EUR',
    maximumFractionDigits: 0,
  }).format(amount)
}

export default function BudgetEstimatorPage() {
  const { projectId = '' } = useParams()
  const [budget, setBudget] = useState<BudgetEstimate | null>(null)
  const [lines, setLines] = useState<BudgetLine[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    loadBudget()
  }, [projectId])

  async function loadBudget() {
    try {
      setIsLoading(true)
      const { budget: activeBudget } = await budgetsApi.getActive(projectId)
      if (activeBudget) {
        setBudget(activeBudget)
        const { lines: budgetLines } = await budgetsApi.get(projectId, activeBudget.id)
        setLines(budgetLines)
      }
    } catch (_e) {
      } finally {
      setIsLoading(false)
    }
  }

  async function generateBudget() {
    try {
      setIsLoading(true)
      const { budget: newBudget } = await budgetsApi.generate(projectId, { level: 'medium' })
      setBudget(newBudget)
      const { lines: budgetLines } = await budgetsApi.get(projectId, newBudget.id)
      setLines(budgetLines)
    } catch (_e) {
      } finally {
      setIsLoading(false)
    }
  }

  async function recalculateBudget(level: string) {
    if (!budget) return
    try {
      setIsLoading(true)
      const { budget: recalculated } = await budgetsApi.recalculate(projectId, budget.id, { level })
      setBudget(recalculated)
      const { lines: budgetLines } = await budgetsApi.get(projectId, recalculated.id)
      setLines(budgetLines)
    } catch (_e) {
      } finally {
      setIsLoading(false)
    }
  }

  async function activateBudget() {
    if (!budget) return
    try {
      await budgetsApi.activate(projectId, budget.id)
      loadBudget()
    } catch (_e) {
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-12">
        <div className="animate-spin w-8 h-8 border-2 border-amber-500 border-t-transparent rounded-full" />
      </div>
    )
  }

  if (!budget) {
    return (
      <div className="space-y-6">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <h1 className="heading-lg">Presupuesto Estimado</h1>
            <p className="mt-1 text-slate-400">
              Genera un presupuesto orientativo desde el guion
            </p>
          </div>
          <Link to={`/projects/${projectId}/dashboard`} className="btn-secondary">
            Volver al dashboard
          </Link>
        </div>

        <div className="card">
          <div className="text-center p-12">
            <DollarSign className="w-16 h-16 mx-auto mb-4 text-slate-500" />
            <h2 className="heading-md mb-2">Sin presupuesto</h2>
            <p className="text-slate-400 mb-6">
              Genera una estimación orientativa basada en tu guion
            </p>
            <button onClick={generateBudget} className="btn-primary">
              Generar presupuesto desde guion
            </button>
          </div>
        </div>

        <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30">
          <div className="flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-medium text-amber-400">Aviso legal</p>
              <p className="text-sm text-slate-400 mt-1">
                Esta es una estimación orientativa generada automáticamente. 
                Las tarifas son reglas internas-heurísticas, NO tarifas oficiales. 
                Validar con producción real antes de usar.
              </p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center LG:justify-between">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="heading-lg">Presupuesto Estimado</h1>
            <span className={`badge ${
              budget.status === 'active' ? 'badge-green' : 'badge-amber'
            }`}>
              {budget.status === 'active' ? 'Activo' : 'Borrador'}
            </span>
          </div>
          <p className="mt-1 text-slate-400">
            Nivel: {LEVEL_LABELS[budget.budget_level] || budget.budget_level}
          </p>
        </div>

        <div className="flex gap-3">
          <Link to={`/projects/${projectId}/dashboard`} className="btn-secondary">
            Volver al dashboard
          </Link>
          {budget.status !== 'active' && (
            <button onClick={activateBudget} className="btn-primary">
              Activar
            </button>
          )}
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <div className="card">
          <p className="text-sm text-slate-400">Presupuesto mínimo</p>
          <p className="text-2xl font-bold text-red-400">{formatCurrency(budget.total_min)}</p>
        </div>
        <div className="card">
          <p className="text-sm text-slate-400">Presupuesto estimado</p>
          <p className="text-2xl font-bold text-amber-400">{formatCurrency(budget.total_estimated)}</p>
        </div>
        <div className="card">
          <p className="text-sm text-slate-400">Presupuesto máximo</p>
          <p className="text-2xl font-bold text-green-400">{formatCurrency(budget.total_max)}</p>
        </div>
      </div>

      <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30">
        <div className="flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-medium text-amber-400">Aviso legal</p>
            <p className="text-sm text-slate-400 mt-1">
              Estimación orientativa. Tarifas no oficiales - validar con producción.
            </p>
          </div>
        </div>
      </div>

      <div className="flex gap-2 mb-4">
        <button onClick={() => recalculateBudget('low')} className="btn-secondary text-sm">
          <RefreshCw className="w-4 h-4 mr-1" /> Bajo
        </button>
        <button onClick={() => recalculateBudget('medium')} className="btn-secondary text-sm">
          <RefreshCw className="w-4 h-4 mr-1" /> Medio
        </button>
        <button onClick={() => recalculateBudget('high')} className="btn-secondary text-sm">
          <RefreshCw className="w-4 h-4 mr-1" /> Alto
        </button>
        <button className="btn-secondary text-sm">
          <Download className="w-4 h-4 mr-1" /> JSON
        </button>
        <button className="btn-secondary text-sm">
          <Download className="w-4 h-4 mr-1" /> CSV
        </button>
      </div>

      <div className="card overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-white/10">
              <th className="text-left py-3 px-4 text-sm font-medium text-slate-400">Categoría</th>
              <th className="text-left py-3 px-4 text-sm font-medium text-slate-400">Descripción</th>
              <th className="text-right py-3 px-4 text-sm font-medium text-slate-400">Cantidad</th>
              <th className="text-right py-3 px-4 text-sm font-medium text-slate-400">Unidad</th>
              <th className="text-right py-3 px-4 text-sm font-medium text-slate-400">Coste</th>
              <th className="text-right py-3 px-4 text-sm font-medium text-slate-400">Total</th>
              <th className="text-center py-3 px-4 text-sm font-medium text-slate-400">Confianza</th>
            </tr>
          </thead>
          <tbody>
            {lines.map((line) => (
              <tr key={line.id} className="border-b border-white/5 hover:bg-white/5">
                <td className="py-3 px-4 capitalize">{line.category}</td>
                <td className="py-3 px-4 text-slate-400">{line.description}</td>
                <td className="py-3 px-4 text-right">{line.quantity}</td>
                <td className="py-3 px-4 text-right text-slate-400">{line.unit}</td>
                <td className="py-3 px-4 text-right">{formatCurrency(line.unit_cost_estimated)}</td>
                <td className="py-3 px-4 text-right font-medium">{formatCurrency(line.total_estimated)}</td>
                <td className="py-3 px-4 text-center">
                  <span className={`text-xs px-2 py-0.5 rounded ${
                    line.confidence === 'high' ? 'bg-green-500/20 text-green-400' :
                    line.confidence === 'medium' ? 'bg-blue-500/20 text-blue-400' :
                    'bg-amber-500/20 text-amber-400'
                  }`}>
                    {CONFIDENCE_LABELS[line.confidence] || line.confidence}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}