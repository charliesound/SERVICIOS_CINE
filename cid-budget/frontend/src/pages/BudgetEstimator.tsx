import { useEffect, useState, useCallback } from 'react'
import { budgetsApi, BudgetEstimate, BudgetLine } from '../api'
import { DollarSign, Download, RefreshCw, AlertTriangle, Check, Archive, Plus, FileText } from 'lucide-react'

interface Props {
  projectId: string
}

const LEVEL_LABELS: Record<string, string> = { low: 'Bajo', medium: 'Medio', high: 'Alto' }
const LEVEL_COLORS: Record<string, string> = { low: 'badge-amber', medium: 'badge-blue', high: 'badge-green' }

export default function BudgetEstimator({ projectId }: Props) {
  const [budget, setBudget] = useState<BudgetEstimate | null>(null)
  const [lines, setLines] = useState<BudgetLine[]>([])
  const [budgets, setBudgets] = useState<BudgetEstimate[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showNewForm, setShowNewForm] = useState(false)
  const [newLevel, setNewLevel] = useState('medium')
  const [scriptText, setScriptText] = useState('')

  const load = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const { budgets: all } = await budgetsApi.list(projectId)
      setBudgets(all)
      const active = all.find((b) => b.status === 'active')
      if (active) {
        const detail = await budgetsApi.get(active.id)
        setBudget(detail.budget)
        setLines(detail.lines)
      } else {
        setBudget(null)
        setLines([])
      }
    } catch (e: any) {
      setError(e.message || 'Error loading budgets')
    }
    setLoading(false)
  }, [projectId])

  useEffect(() => { load() }, [load])

  const selectBudget = async (id: string) => {
    setLoading(true)
    try {
      const detail = await budgetsApi.get(id)
      setBudget(detail.budget)
      setLines(detail.lines)
    } catch (e: any) {
      setError(e.message)
    }
    setLoading(false)
  }

  const handleGenerate = async () => {
    setLoading(true)
    try {
      await budgetsApi.generate(projectId, newLevel, scriptText)
      setShowNewForm(false)
      setScriptText('')
      await load()
    } catch (e: any) {
      setError(e.message)
    }
    setLoading(false)
  }

  const handleActivate = async (id: string) => {
    await budgetsApi.activate(id)
    await load()
  }

  const handleRecalculate = async (level: string) => {
    if (!budget) return
    setLoading(true)
    try {
      const { budget: updated } = await budgetsApi.recalculate(budget.id, level)
      const detail = await budgetsApi.get(updated.id)
      setBudget(detail.budget)
      setLines(detail.lines)
    } catch (e: any) {
      setError(e.message)
    }
    setLoading(false)
  }

  const handleArchive = async (id: string) => {
    await budgetsApi.archive(id)
    if (budget?.id === id) { setBudget(null); setLines([]) }
    await load()
  }

  const fmt = (n: number) => `€${n.toLocaleString('es-ES', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`

  if (loading && !budget && budgets.length === 0) {
    return <div className="text-cine-400 text-center py-12">Cargando...</div>
  }

  return (
    <div className="space-y-6">
      {error && (
        <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4 text-red-400 text-sm flex items-center gap-2">
          <AlertTriangle className="w-4 h-4" /> {error}
        </div>
      )}

      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white">Presupuestos</h2>
          <p className="text-sm text-cine-400">{budgets.length} presupuesto(s)</p>
        </div>
        <div className="flex gap-2">
          <button onClick={load} className="btn-secondary text-sm flex items-center gap-1">
            <RefreshCw className="w-4 h-4" /> Recargar
          </button>
          <button onClick={() => setShowNewForm(true)} className="btn-primary text-sm flex items-center gap-1">
            <Plus className="w-4 h-4" /> Nuevo
          </button>
        </div>
      </div>

      {showNewForm && (
        <div className="card space-y-4">
          <h3 className="font-semibold text-white">Generar nuevo presupuesto</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-cine-400 mb-1">Nivel</label>
              <select className="bg-dark-600 border border-white/10 rounded-lg px-3 py-2 text-sm w-full" value={newLevel} onChange={(e) => setNewLevel(e.target.value)}>
                <option value="low">Bajo</option>
                <option value="medium">Medio</option>
                <option value="high">Alto</option>
              </select>
            </div>
            <div className="flex items-end">
              <button onClick={handleGenerate} className="btn-primary text-sm w-full">Generar</button>
            </div>
          </div>
          <div>
            <label className="block text-sm text-cine-400 mb-1">Texto del guion (opcional)</label>
            <textarea className="bg-dark-600 border border-white/10 rounded-lg px-3 py-2 text-sm w-full h-20" value={scriptText} onChange={(e) => setScriptText(e.target.value)} placeholder="Pega el texto del guion para una estimación más precisa..." />
          </div>
        </div>
      )}

      {budgets.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {budgets.map((b) => (
            <button
              key={b.id}
              onClick={() => selectBudget(b.id)}
              className={`px-3 py-1.5 rounded-lg text-xs border transition-colors ${
                budget?.id === b.id
                  ? 'bg-amber-500/20 border-amber-500/30 text-amber-400'
                  : 'bg-dark-600 border-white/10 text-cine-300 hover:border-white/20'
              }`}
            >
              {b.title} <span className={`ml-1 badge ${LEVEL_COLORS[b.budget_level] || 'badge-blue'}`}>{LEVEL_LABELS[b.budget_level] || b.budget_level}</span>
            </button>
          ))}
        </div>
      )}

      {budget && (
        <>
          <div className="card">
            <div className="flex items-start justify-between mb-4">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <h3 className="text-lg font-bold text-white">{budget.title}</h3>
                  <span className={`badge ${budget.status === 'active' ? 'badge-green' : 'badge-amber'}`}>
                    {budget.status === 'active' ? 'Activo' : 'Draft'}
                  </span>
                  <span className={`badge ${LEVEL_COLORS[budget.budget_level]}`}>{LEVEL_LABELS[budget.budget_level]}</span>
                </div>
                <p className="text-xs text-cine-400">Contingencia: {budget.contingency_percent}%</p>
              </div>
              <div className="flex gap-2">
                {budget.status === 'draft' && (
                  <button onClick={() => handleActivate(budget.id)} className="btn-primary text-xs flex items-center gap-1">
                    <Check className="w-3 h-3" /> Activar
                  </button>
                )}
                <button onClick={() => handleArchive(budget.id)} className="btn-secondary text-xs flex items-center gap-1">
                  <Archive className="w-3 h-3" /> Archivar
                </button>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4 mb-4">
              <div className="bg-red-500/5 border border-red-500/20 rounded-xl p-4 text-center">
                <p className="text-xs text-red-400 mb-1">Mínimo</p>
                <p className="text-xl font-bold text-red-400">{fmt(budget.total_min)}</p>
              </div>
              <div className="bg-amber-500/5 border border-amber-500/20 rounded-xl p-4 text-center">
                <p className="text-xs text-amber-400 mb-1">Estimado</p>
                <p className="text-xl font-bold text-amber-400">{fmt(budget.total_estimated)}</p>
              </div>
              <div className="bg-green-500/5 border border-green-500/20 rounded-xl p-4 text-center">
                <p className="text-xs text-green-400 mb-1">Máximo</p>
                <p className="text-xl font-bold text-green-400">{fmt(budget.total_max)}</p>
              </div>
            </div>

            <div className="flex gap-2">
              {['low', 'medium', 'high'].map((level) => (
                <button
                  key={level}
                  onClick={() => handleRecalculate(level)}
                  className={`text-xs px-3 py-1.5 rounded-lg border transition-colors ${
                    budget.budget_level === level
                      ? 'bg-amber-500/20 border-amber-500/30 text-amber-400'
                      : 'bg-dark-600 border-white/10 text-cine-300 hover:border-white/20'
                  }`}
                >
                  Recalcular {LEVEL_LABELS[level]}
                </button>
              ))}
            </div>

            {budget.assumptions && budget.assumptions.length > 0 && (
              <div className="mt-4 bg-blue-500/5 border border-blue-500/20 rounded-xl p-3">
                <p className="text-xs text-blue-400 font-medium mb-1">Supuestos</p>
                <ul className="text-xs text-cine-300 space-y-0.5">
                  {budget.assumptions.map((a, i) => <li key={i}>• {a}</li>)}
                </ul>
              </div>
            )}
          </div>

          <div className="card">
            <h4 className="font-semibold text-white mb-4">Partidas ({lines.length})</h4>
            <div className="space-y-1">
              {lines.map((line) => (
                <div key={line.id} className="flex items-center justify-between py-2 px-3 rounded-lg hover:bg-dark-600/50 text-sm">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="badge-blue text-xs">{line.category}</span>
                      <span className="text-white truncate">{line.description}</span>
                    </div>
                    <p className="text-xs text-cine-400 mt-0.5">
                      {line.quantity} × {line.unit} · unit: {fmt(line.unit_cost_estimated)}
                    </p>
                  </div>
                  <div className="text-right ml-4">
                    <p className="text-white font-medium">{fmt(line.total_estimated)}</p>
                    <span className={`badge text-xs ${
                      line.confidence === 'high' ? 'badge-green' :
                      line.confidence === 'medium' ? 'badge-blue' : 'badge-amber'
                    }`}>{line.confidence}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}

      {!loading && budgets.length === 0 && !showNewForm && (
        <div className="card text-center py-12">
          <DollarSign className="w-12 h-12 text-cine-600 mx-auto mb-4" />
          <p className="text-cine-400">No hay presupuestos. Crea uno nuevo para empezar.</p>
        </div>
      )}
    </div>
  )
}
