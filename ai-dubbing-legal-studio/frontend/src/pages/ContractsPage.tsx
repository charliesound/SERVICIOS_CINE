import { useEffect, useState } from 'react'
import api from '../api/client'
import { Plus, Shield, ShieldCheck } from 'lucide-react'
import type { VoiceContract } from '../types'

export default function ContractsPage() {
  const [contracts, setContracts] = useState<VoiceContract[]>([])
  const [showForm, setShowForm] = useState(false)
  const [contractRef, setContractRef] = useState('')
  const [actorId, setActorId] = useState(0)
  const [iaConsent, setIaConsent] = useState(false)
  const [validationResult, setValidationResult] = useState<any>(null)
  const [validatingId, setValidatingId] = useState<number | null>(null)

  useEffect(() => {
    api.get('/contracts').then((r) => setContracts(r.data))
  }, [])

  const createContract = async (e: React.FormEvent) => {
    e.preventDefault()
    await api.post('/contracts', {
      actor_id: actorId || 1,
      contract_ref: contractRef,
      signed_date: new Date().toISOString(),
      expiry_date: new Date(Date.now() + 365 * 86400000).toISOString(),
      ia_consent: iaConsent,
      allowed_languages: ['es', 'en'],
      allowed_territories: ['ES', 'MX', 'US'],
      allowed_usage_types: ['dubbing', 'trailer'],
    })
    setShowForm(false)
    setContractRef('')
    api.get('/contracts').then((r) => setContracts(r.data))
  }

  const validateContract = async (contractId: number) => {
    setValidatingId(contractId)
    try {
      const res = await api.post(`/contracts/${contractId}/validate`, {
        mode: 'voz_original_ia_autorizada',
        language: 'es',
        territory: 'ES',
        usage_type: 'dubbing',
      })
      setValidationResult(res.data)
    } finally {
      setValidatingId(null)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Contratos de voz</h1>
          <p className="text-cine-400 mt-1">Gestiona contratos y permisos de actores/voces</p>
        </div>
        <button onClick={() => setShowForm(!showForm)} className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" /> Nuevo contrato
        </button>
      </div>

      {showForm && (
        <form onSubmit={createContract} className="card space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">Referencia del contrato</label>
              <input className="input" value={contractRef} onChange={(e) => setContractRef(e.target.value)} placeholder="REF-001" required />
            </div>
            <div>
              <label className="label">ID del actor</label>
              <input type="number" className="input" value={actorId} onChange={(e) => setActorId(Number(e.target.value))} placeholder="1" />
            </div>
          </div>
          <label className="flex items-center gap-3">
            <input type="checkbox" checked={iaConsent} onChange={(e) => setIaConsent(e.target.checked)} className="w-4 h-4 rounded border-cine-500 bg-cine-900 text-amber-500 focus:ring-amber-500" />
            <span className="text-sm text-cine-200">Consentimiento IA explícito</span>
          </label>
          <div className="flex gap-2">
            <button type="submit" className="btn-primary">Crear</button>
            <button type="button" onClick={() => setShowForm(false)} className="btn-secondary">Cancelar</button>
          </div>
        </form>
      )}

      {validationResult && (
        <div className={`card border ${validationResult.blocked ? 'border-legal-red/50' : 'border-green-500/30'}`}>
          <div className="flex items-center gap-2 mb-3">
            {validationResult.blocked ? (
              <Shield className="w-5 h-5 text-legal-red" />
            ) : (
              <ShieldCheck className="w-5 h-5 text-green-400" />
            )}
            <h3 className="font-semibold text-white">Validación de contrato #{validationResult.contract_id}</h3>
          </div>
          {validationResult.blocked ? (
            <p className="text-legal-red text-sm">{validationResult.reason}</p>
          ) : (
            <p className="text-green-400 text-sm">Contrato válido - todos los checks pasaron</p>
          )}
          <pre className="mt-2 text-xs text-cine-400 bg-cine-900 rounded p-2 overflow-x-auto">
            {JSON.stringify(validationResult.checks, null, 2)}
          </pre>
        </div>
      )}

      <div className="space-y-3">
        {contracts.map((c) => (
          <div key={c.id} className={`card ${!c.is_active ? 'opacity-60' : ''}`}>
            <div className="flex items-start justify-between">
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-medium text-white">{c.contract_ref}</span>
                  <span className={c.is_active ? 'badge-green' : 'badge-red'}>
                    {c.is_active ? 'Activo' : 'Inactivo'}
                  </span>
                  {c.ia_consent && <span className="badge-blue">Consentimiento IA</span>}
                </div>
                <p className="text-sm text-cine-400 mt-1">Actor ID: {c.actor_id}</p>
                <p className="text-sm text-cine-400">Expira: {new Date(c.expiry_date).toLocaleDateString()}</p>
              </div>
              <button
                onClick={() => validateContract(c.id)}
                disabled={validatingId === c.id}
                className="btn-secondary text-sm flex items-center gap-1"
              >
                <Shield className="w-3 h-3" />
                {validatingId === c.id ? 'Validando...' : 'Validar'}
              </button>
            </div>
          </div>
        ))}
        {contracts.length === 0 && (
          <div className="card text-center py-12">
            <p className="text-cine-400">No hay contratos registrados</p>
          </div>
        )}
      </div>
    </div>
  )
}
