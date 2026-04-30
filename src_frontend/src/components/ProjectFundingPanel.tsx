import { useState, useEffect } from 'react'
import { projectFundingApi, type ProjectFundingSource, type ProjectFundingSummary, type CreateFundingSourcePayload } from '@/api'
import {
  DollarSign, Plus, Pencil, Trash2, Save, X, Loader2, AlertCircle, CheckCircle2
} from 'lucide-react'

const SOURCE_TYPES = [
  { value: 'equity', label: 'Equity' },
  { value: 'private_investor', label: 'Inverse Privado' },
  { value: 'pre_sale', label: 'Pre-venta' },
  { value: 'minimum_guarantee', label: 'Garantía Mínima' },
  { value: 'in_kind', label: 'Especie (In-kind)' },
  { value: 'brand_partnership', label: 'Partner de Marca' },
  { value: 'loan', label: 'Préstamo' },
  { value: 'other', label: 'Otro' },
]

const STATUS_OPTIONS = [
  { value: 'secured', label: 'Secured', color: 'bg-green-500/10 text-green-400 border-green-500/20' },
  { value: 'negotiating', label: 'En negociación', color: 'bg-amber-500/10 text-amber-400 border-amber-500/20' },
  { value: 'projected', label: 'Proyectado', color: 'bg-blue-500/10 text-blue-400 border-blue-500/20' },
]

interface Props {
  projectId: string
}

export default function ProjectFundingPanel({ projectId }: Props) {
  const [sources, setSources] = useState<ProjectFundingSource[]>([])
  const [summary, setSummary] = useState<ProjectFundingSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [successMsg, setSuccessMsg] = useState('')
  const [editingId, setEditingId] = useState<string | null>(null)
  const [isCreating, setIsCreating] = useState(false)

  const [formData, setFormData] = useState<CreateFundingSourcePayload>({
    source_name: '',
    source_type: 'equity',
    amount: 0,
    currency: 'EUR',
    status: 'projected',
    notes: '',
  })

  const loadData = async () => {
    try {
      const [srcs, sum] = await Promise.all([
        projectFundingApi.listSources(projectId),
        projectFundingApi.getSummary(projectId),
      ])
      setSources(srcs)
      setSummary(sum)
    } catch (err) {
      console.error('Error loading funding data:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [projectId])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setError('')
    setSuccessMsg('')

    try {
      await projectFundingApi.createSource(projectId, formData)
      setSuccessMsg('Fuente creada correctamente')
      setIsCreating(false)
      setFormData({
        source_name: '',
        source_type: 'equity',
        amount: 0,
        currency: 'EUR',
        status: 'projected',
        notes: '',
      })
      await loadData()
      setTimeout(() => setSuccessMsg(''), 2000)
    } catch (err) {
      setError('Error al crear fuente')
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (sourceId: string) => {
    if (!confirm('¿Eliminar esta fuente?')) return

    try {
      await projectFundingApi.deleteSource(projectId, sourceId)
      setSuccessMsg('Fuente eliminada')
      await loadData()
      setTimeout(() => setSuccessMsg(''), 2000)
    } catch (err) {
      setError('Error al eliminar')
    }
  }

  const handleEdit = async (source: ProjectFundingSource) => {
    if (editingId === source.id) {
      setEditingId(null)
      return
    }
    setEditingId(source.id)
    setFormData({
      source_name: source.source_name,
      source_type: source.source_type,
      amount: source.amount,
      currency: source.currency,
      status: source.status,
      notes: source.notes || '',
    })
  }

  const handleSaveEdit = async (sourceId: string) => {
    setSaving(true)
    try {
      await projectFundingApi.updateSource(projectId, sourceId, formData)
      setSuccessMsg('Fuente actualizada')
      setEditingId(null)
      await loadData()
      setTimeout(() => setSuccessMsg(''), 2000)
    } catch (err) {
      setError('Error al actualizar')
    } finally {
      setSaving(false)
    }
  }

  const formatCurrency = (amount: number, currency: string = 'EUR') => {
    return new Intl.NumberFormat('es-ES', {
      style: 'currency',
      currency,
    }).format(amount)
  }

  const getStatusColor = (status: string) => {
    const opt = STATUS_OPTIONS.find(s => s.value === status)
    return opt?.color || 'bg-gray-500/10 text-gray-400 border-gray-500/20'
  }

  const getStatusLabel = (status: string) => {
    const opt = STATUS_OPTIONS.find(s => s.value === status)
    return opt?.label || status
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="w-6 h-6 animate-spin text-gray-400" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {error && (
        <div className="flex items-center gap-2 p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400">
          <AlertCircle className="w-4 h-4" />
          {error}
        </div>
      )}

      {successMsg && (
        <div className="flex items-center gap-2 p-3 bg-green-500/10 border border-green-500/20 rounded-lg text-green-400">
          <CheckCircle2 className="w-4 h-4" />
          {successMsg}
        </div>
      )}

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="p-4 bg-white/5 rounded-lg border border-white/10">
          <div className="text-sm text-gray-400 mb-1">Total Budget</div>
          <div className="text-xl font-semibold text-white">
            {summary ? formatCurrency(summary.total_budget, summary.currency) : '-'}
          </div>
        </div>
        <div className="p-4 bg-green-500/5 rounded-lg border border-green-500/20">
          <div className="text-sm text-green-400 mb-1">Secured</div>
          <div className="text-xl font-semibold text-green-400">
            {summary ? formatCurrency(summary.total_secured_private_funds, summary.currency) : '-'}
          </div>
        </div>
        <div className="p-4 bg-amber-500/5 rounded-lg border border-amber-500/20">
          <div className="text-sm text-amber-400 mb-1">Negotiating</div>
          <div className="text-xl font-semibold text-amber-400">
            {summary ? formatCurrency(summary.total_negotiating_private_funds, summary.currency) : '-'}
          </div>
        </div>
        <div className="p-4 bg-blue-500/5 rounded-lg border border-blue-500/20">
          <div className="text-sm text-blue-400 mb-1">Projected</div>
          <div className="text-xl font-semibold text-blue-400">
            {summary ? formatCurrency(summary.total_projected_private_funds, summary.currency) : '-'}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 p-4 bg-red-500/10 rounded-lg border border-red-500/20">
        <div>
          <div className="text-sm text-red-300 mb-1">Funding Gap (Actual)</div>
          <div className="text-2xl font-bold text-red-400">
            {summary ? formatCurrency(summary.current_funding_gap, summary.currency) : '-'}
          </div>
        </div>
        <div>
          <div className="text-sm text-gray-400 mb-1">Funding Gap (Optimista)</div>
          <div className="text-2xl font-semibold text-gray-300">
            {summary ? formatCurrency(summary.optimistic_funding_gap, summary.currency) : '-'}
          </div>
        </div>
      </div>

      <div className="border-t border-white/10 pt-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white">Fuentes Privadas</h3>
          <button
            onClick={() => setIsCreating(true)}
            className="flex items-center gap-2 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 rounded-lg text-white text-sm transition-colors"
          >
            <Plus className="w-4 h-4" />
            Nueva Fuente
          </button>
        </div>

        {isCreating && (
          <form onSubmit={handleSubmit} className="mb-4 p-4 bg-white/5 rounded-lg border border-white/10 space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-sm text-gray-400 mb-1">Nombre</label>
                <input
                  type="text"
                  value={formData.source_name}
                  onChange={e => setFormData({ ...formData, source_name: e.target.value })}
                  className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white"
                  required
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Tipo</label>
                <select
                  value={formData.source_type}
                  onChange={e => setFormData({ ...formData, source_type: e.target.value })}
                  className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white"
                >
                  {SOURCE_TYPES.map(st => (
                    <option key={st.value} value={st.value}>{st.label}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Monto</label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.amount}
                  onChange={e => setFormData({ ...formData, amount: parseFloat(e.target.value) || 0 })}
                  className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white"
                  required
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Estado</label>
                <select
                  value={formData.status}
                  onChange={e => setFormData({ ...formData, status: e.target.value })}
                  className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white"
                >
                  {STATUS_OPTIONS.map(s => (
                    <option key={s.value} value={s.value}>{s.label}</option>
                  ))}
                </select>
              </div>
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Notas</label>
              <textarea
                value={formData.notes}
                onChange={e => setFormData({ ...formData, notes: e.target.value })}
                className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white"
                rows={2}
              />
            </div>
            <div className="flex gap-2">
              <button
                type="submit"
                disabled={saving}
                className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg text-white text-sm transition-colors disabled:opacity-50"
              >
                {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
                Guardar
              </button>
              <button
                type="button"
                onClick={() => {
                  setIsCreating(false)
                  setFormData({
                    source_name: '',
                    source_type: 'equity',
                    amount: 0,
                    currency: 'EUR',
                    status: 'projected',
                    notes: '',
                  })
                }}
                className="flex items-center gap-2 px-4 py-2 bg-gray-600 hover:bg-gray-700 rounded-lg text-white text-sm transition-colors"
              >
                <X className="w-4 h-4" />
                Cancelar
              </button>
            </div>
          </form>
        )}

        {sources.length === 0 ? (
          <div className="text-center py-8 text-gray-400">
            <DollarSign className="w-12 h-12 mx-auto mb-2 opacity-50" />
            <p>No hay fuentes privadas registradas</p>
            <p className="text-sm">Añade fuentes para calcular la brecha de financiación</p>
          </div>
        ) : (
          <div className="space-y-2">
            {sources.map(source => (
              <div
                key={source.id}
                className="flex items-center gap-4 p-3 bg-white/5 rounded-lg border border-white/10"
              >
                {editingId === source.id ? (
                  <div className="flex-1 space-y-2">
                    <div className="grid grid-cols-2 gap-2">
                      <input
                        type="text"
                        value={formData.source_name}
                        onChange={e => setFormData({ ...formData, source_name: e.target.value })}
                        className="px-2 py-1 bg-white/10 border border-white/20 rounded text-white text-sm"
                      />
                      <input
                        type="number"
                        step="0.01"
                        value={formData.amount}
                        onChange={e => setFormData({ ...formData, amount: parseFloat(e.target.value) || 0 })}
                        className="px-2 py-1 bg-white/10 border border-white/20 rounded text-white text-sm"
                      />
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleSaveEdit(source.id)}
                        disabled={saving}
                        className="flex items-center gap-1 px-2 py-1 bg-green-600 rounded text-white text-xs"
                      >
                        <Save className="w-3 h-3" />
                      </button>
                      <button
                        onClick={() => handleEdit(source)}
                        className="flex items-center gap-1 px-2 py-1 bg-gray-600 rounded text-white text-xs"
                      >
                        <X className="w-3 h-3" />
                      </button>
                    </div>
                  </div>
                ) : (
                  <>
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-white">{source.source_name}</span>
                        <span className={`px-2 py-0.5 rounded text-xs border ${getStatusColor(source.status)}`}>
                          {getStatusLabel(source.status)}
                        </span>
                        <span className="text-xs text-gray-400">
                          {SOURCE_TYPES.find(st => st.value === source.source_type)?.label || source.source_type}
                        </span>
                      </div>
                      <div className="text-sm text-gray-400">
                        {formatCurrency(source.amount, source.currency)}
                      </div>
                      {source.notes && (
                        <div className="text-xs text-gray-500 mt-1">{source.notes}</div>
                      )}
                    </div>
                    <div className="flex gap-1">
                      <button
                        onClick={() => handleEdit(source)}
                        className="p-2 hover:bg-white/10 rounded text-gray-400 hover:text-white transition-colors"
                      >
                        <Pencil className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDelete(source.id)}
                        className="p-2 hover:bg-white/10 rounded text-gray-400 hover:text-red-400 transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}