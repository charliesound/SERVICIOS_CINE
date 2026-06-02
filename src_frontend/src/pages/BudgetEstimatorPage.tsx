import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { AlertCircle, DollarSign, Download, RefreshCw, AlertTriangle } from 'lucide-react'
import { budgetsApi } from '@/api/budget'
import type { BudgetEstimate, BudgetLine } from '@/api/budget'
import { t } from '@/i18n'

function getLevelLabel(level: string): string {
  const labels: Record<string, string> = {
    low: t('internal.budgetEstimatorPage.levels.low'),
    medium: t('internal.budgetEstimatorPage.levels.medium'),
    high: t('internal.budgetEstimatorPage.levels.high'),
  }
  return labels[level] || level
}

function getConfidenceLabel(confidence: string): string {
  const labels: Record<string, string> = {
    low: t('internal.budgetEstimatorPage.confidence.low'),
    medium: t('internal.budgetEstimatorPage.confidence.medium'),
    high: t('internal.budgetEstimatorPage.confidence.high'),
  }
  return labels[confidence] || confidence
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
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadBudget()
  }, [projectId])

  async function loadBudget() {
    try {
      setError(null)
      setIsLoading(true)
      const { budget: activeBudget } = await budgetsApi.getActive(projectId)
      if (activeBudget) {
        setBudget(activeBudget)
        const { lines: budgetLines } = await budgetsApi.get(projectId, activeBudget.id)
        setLines(budgetLines)
      }
    } catch (_e) {
      setError(t('internal.budgetEstimatorPage.errors.load'))
    } finally {
      setIsLoading(false)
    }
  }

  async function generateBudget() {
    try {
      setError(null)
      setIsLoading(true)
      const { budget: newBudget } = await budgetsApi.generate(projectId, { level: 'medium' })
      setBudget(newBudget)
      const { lines: budgetLines } = await budgetsApi.get(projectId, newBudget.id)
      setLines(budgetLines)
    } catch (_e) {
      setError(t('internal.budgetEstimatorPage.errors.generate'))
    } finally {
      setIsLoading(false)
    }
  }

  async function recalculateBudget(level: string) {
    if (!budget) return
    try {
      setError(null)
      setIsLoading(true)
      const { budget: recalculated } = await budgetsApi.recalculate(projectId, budget.id, { level })
      setBudget(recalculated)
      const { lines: budgetLines } = await budgetsApi.get(projectId, recalculated.id)
      setLines(budgetLines)
    } catch (_e) {
      setError(t('internal.budgetEstimatorPage.errors.recalculate'))
    } finally {
      setIsLoading(false)
    }
  }

  async function activateBudget() {
    if (!budget) return
    try {
      setError(null)
      await budgetsApi.activate(projectId, budget.id)
      loadBudget()
    } catch (_e) {
      setError(t('internal.budgetEstimatorPage.errors.activate'))
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-12">
        <div className="animate-spin w-8 h-8 border-2 border-amber-500 border-t-transparent rounded-full" />
      </div>
    )
  }

  if (error && !budget) {
    return (
      <div className="space-y-6">
        <h1 className="heading-lg">{t('internal.budgetEstimatorPage.title')}</h1>
        <div className="card">
          <div className="text-center p-12">
            <AlertCircle className="w-16 h-16 mx-auto mb-4 text-red-400" />
            <h2 className="heading-md mb-2">{t('internal.budgetEstimatorPage.loadErrorTitle')}</h2>
            <p className="text-slate-400 mb-6">{error}</p>
            <button onClick={() => { setError(null); loadBudget() }} className="btn-primary">
              {t('internal.common.retry')}
            </button>
            <Link to={`/projects/${projectId}/dashboard`} className="btn-secondary ml-3">
              {t('internal.budgetEstimatorPage.backToProject')}
            </Link>
          </div>
        </div>
      </div>
    )
  }

  if (!budget) {
    return (
      <div className="space-y-6">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <h1 className="heading-lg">{t('internal.budgetEstimatorPage.title')}</h1>
            <p className="mt-1 text-slate-400">
              {t('internal.budgetEstimatorPage.subtitle')}
            </p>
          </div>
          <Link to={`/projects/${projectId}/dashboard`} className="btn-secondary">
            {t('internal.budgetEstimatorPage.backToDashboard')}
          </Link>
        </div>

        <div className="card">
          <div className="text-center p-12">
            <DollarSign className="w-16 h-16 mx-auto mb-4 text-slate-500" />
            <h2 className="heading-md mb-2">{t('internal.budgetEstimatorPage.emptyTitle')}</h2>
            <p className="text-slate-400 mb-6">
              {t('internal.budgetEstimatorPage.emptyDescription')}
            </p>
            <button onClick={generateBudget} className="btn-primary">
              {t('internal.budgetEstimatorPage.generateFromScript')}
            </button>
          </div>
        </div>

        <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30">
          <div className="flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-medium text-amber-400">{t('internal.budgetEstimatorPage.legal.title')}</p>
              <p className="text-sm text-slate-400 mt-1">
                {t('internal.budgetEstimatorPage.legal.long')}
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
            <h1 className="heading-lg">{t('internal.budgetEstimatorPage.title')}</h1>
            <span className={`badge ${
              budget.status === 'active' ? 'badge-green' : 'badge-amber'
            }`}>
              {budget.status === 'active' ? t('internal.budgetEstimatorPage.status.active') : t('internal.budgetEstimatorPage.status.draft')}
            </span>
          </div>
          <p className="mt-1 text-slate-400">
            {t('internal.budgetEstimatorPage.levelLabel')}: {getLevelLabel(budget.budget_level)}
          </p>
        </div>

        <div className="flex gap-3">
          <Link to={`/projects/${projectId}/dashboard`} className="btn-secondary">
            {t('internal.budgetEstimatorPage.backToDashboard')}
          </Link>
          {budget.status !== 'active' && (
            <button onClick={activateBudget} className="btn-primary">
              {t('internal.budgetEstimatorPage.activate')}
            </button>
          )}
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <div className="card">
          <p className="text-sm text-slate-400">{t('internal.budgetEstimatorPage.totals.minimum')}</p>
          <p className="text-2xl font-bold text-red-400">{formatCurrency(budget.total_min)}</p>
        </div>
        <div className="card">
          <p className="text-sm text-slate-400">{t('internal.budgetEstimatorPage.totals.estimated')}</p>
          <p className="text-2xl font-bold text-amber-400">{formatCurrency(budget.total_estimated)}</p>
        </div>
        <div className="card">
          <p className="text-sm text-slate-400">{t('internal.budgetEstimatorPage.totals.maximum')}</p>
          <p className="text-2xl font-bold text-green-400">{formatCurrency(budget.total_max)}</p>
        </div>
      </div>

      <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30">
        <div className="flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-medium text-amber-400">{t('internal.budgetEstimatorPage.legal.title')}</p>
            <p className="text-sm text-slate-400 mt-1">
              {t('internal.budgetEstimatorPage.legal.short')}
            </p>
          </div>
        </div>
      </div>

      <div className="flex gap-2 mb-4">
        <button onClick={() => recalculateBudget('low')} className="btn-secondary text-sm">
          <RefreshCw className="w-4 h-4 mr-1" /> {t('internal.budgetEstimatorPage.actions.low')}
        </button>
        <button onClick={() => recalculateBudget('medium')} className="btn-secondary text-sm">
          <RefreshCw className="w-4 h-4 mr-1" /> {t('internal.budgetEstimatorPage.actions.medium')}
        </button>
        <button onClick={() => recalculateBudget('high')} className="btn-secondary text-sm">
          <RefreshCw className="w-4 h-4 mr-1" /> {t('internal.budgetEstimatorPage.actions.high')}
        </button>
        <button className="btn-secondary text-sm">
          <Download className="w-4 h-4 mr-1" /> {t('internal.budgetEstimatorPage.actions.exportJson')}
        </button>
        <button className="btn-secondary text-sm">
          <Download className="w-4 h-4 mr-1" /> {t('internal.budgetEstimatorPage.actions.exportCsv')}
        </button>
      </div>

      <div className="card overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-white/10">
              <th className="text-left py-3 px-4 text-sm font-medium text-slate-400">{t('internal.budgetEstimatorPage.table.category')}</th>
              <th className="text-left py-3 px-4 text-sm font-medium text-slate-400">{t('internal.budgetEstimatorPage.table.description')}</th>
              <th className="text-right py-3 px-4 text-sm font-medium text-slate-400">{t('internal.budgetEstimatorPage.table.quantity')}</th>
              <th className="text-right py-3 px-4 text-sm font-medium text-slate-400">{t('internal.budgetEstimatorPage.table.unit')}</th>
              <th className="text-right py-3 px-4 text-sm font-medium text-slate-400">{t('internal.budgetEstimatorPage.table.cost')}</th>
              <th className="text-right py-3 px-4 text-sm font-medium text-slate-400">{t('internal.budgetEstimatorPage.table.total')}</th>
              <th className="text-center py-3 px-4 text-sm font-medium text-slate-400">{t('internal.budgetEstimatorPage.table.confidence')}</th>
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
                    {getConfidenceLabel(line.confidence)}
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