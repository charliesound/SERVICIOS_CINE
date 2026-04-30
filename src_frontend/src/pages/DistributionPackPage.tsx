import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { distributionPackApi, DistributionPack } from '../api/distributionPack'

const PACK_TYPES = [
  { value: 'distributor', label: 'Distribuidora' },
  { value: 'sales_agent', label: 'Agente de ventas' },
  { value: 'festival', label: 'Festival' },
  { value: 'cinema', label: 'Cines' },
  { value: 'platform', label: 'Plataforma' },
  { value: 'general_sales', label: 'General' },
]

export default function DistributionPackPage() {
  const { projectId } = useParams<{ projectId: string }>()
  const [pack, setPack] = useState<DistributionPack | null>(null)
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [selectedType, setSelectedType] = useState('distributor')
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadPack()
  }, [projectId])

  const loadPack = async () => {
    if (!projectId) return
    try {
      const result = await distributionPackApi.list(projectId)
      if (result.packs && result.packs.length > 0) {
        const activePack = await distributionPackApi.get(projectId, result.packs[0].id)
        setPack(activePack.pack)
      }
    } catch (e) {
      setPack(null)
    } finally {
      setLoading(false)
    }
  }

  const handleGenerate = async () => {
    if (!projectId) return
    setGenerating(true)
    setError(null)
    try {
      const result = await distributionPackApi.generate(projectId, { pack_type: selectedType })
      if (result.pack_id) {
        const packResult = await distributionPackApi.get(projectId, result.pack_id)
        setPack(packResult.pack)
      }
    } catch (e: any) {
      setError(e.message || 'Error generating pack')
    } finally {
      setGenerating(false)
    }
  }

  const handleExport = async (format: string) => {
    if (!projectId || !pack) return
    try {
      if (format === 'json') {
        const data = await distributionPackApi.exportJson(projectId, pack.id)
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
        downloadBlob(blob, `distribution_${pack.pack_type}.json`)
      } else if (format === 'markdown') {
        const data = await distributionPackApi.exportMarkdown(projectId, pack.id)
        const blob = new Blob([data], { type: 'text/markdown' })
        downloadBlob(blob, `distribution_${pack.pack_type}.md`)
      } else if (format === 'zip') {
        const blob = await distributionPackApi.exportZip(projectId, pack.id)
        downloadBlob(blob, `distribution_${pack.pack_type}.zip`)
      }
    } catch (e: any) {
      setError(e.message || 'Error exporting')
    }
  }

  const downloadBlob = (blob: Blob, filename: string) => {
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.click()
    URL.revokeObjectURL(url)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Cargando...</div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Distribución / Cines / Plataformas</h1>
        <p className="text-gray-600">Herramienta de preparación comercial</p>
      </div>

      <div className="mb-4 p-3 bg-yellow-50 text-yellow-800 rounded text-sm">
         <em>Este documento es herramienta de preparación comercial. No asegura aceptación por distribuidores o plataformas.</em>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 text-red-700 rounded">{error}</div>
      )}

      {!pack ? (
        <div className="text-center py-12">
          <p className="text-gray-600 mb-4">No hay pack de distribución generado.</p>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">Tipo de pack</label>
            <select
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value)}
              className="border rounded px-3 py-2 w-64"
            >
              {PACK_TYPES.map((t) => (
                <option key={t.value} value={t.value}>{t.label}</option>
              ))}
            </select>
          </div>
          <button
            onClick={handleGenerate}
            disabled={generating}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {generating ? 'Generando...' : 'Generar Pack'}
          </button>
        </div>
      ) : (
        <>
          <div className="mb-4 flex items-center justify-between">
            <span className="text-sm text-gray-500">
              Tipo: <span className="font-medium">{pack.pack_type}</span> | 
              Estado: <span className="font-medium capitalize">{pack.status}</span>
            </span>
            <div className="space-x-2">
              <button
                onClick={() => handleExport('json')}
                className="px-3 py-1 text-sm border rounded hover:bg-gray-50"
              >
                Export JSON
              </button>
              <button
                onClick={() => handleExport('markdown')}
                className="px-3 py-1 text-sm border rounded hover:bg-gray-50"
              >
                Export Markdown
              </button>
              <button
                onClick={() => handleExport('zip')}
                className="px-3 py-1 text-sm border rounded hover:bg-gray-50"
              >
                Export ZIP
              </button>
            </div>
          </div>

          <div className="space-y-6">
            {pack.logline && (
              <section>
                <h2 className="text-lg font-semibold text-gray-900 mb-2">Logline</h2>
                <p className="text-gray-700">{pack.logline}</p>
              </section>
            )}

            {pack.short_synopsis && (
              <section>
                <h2 className="text-lg font-semibold text-gray-900 mb-2">Sinopsis</h2>
                <p className="text-gray-700">{pack.short_synopsis}</p>
              </section>
            )}

            {pack.commercial_positioning && (
              <section>
                <h2 className="text-lg font-semibold text-gray-900 mb-2">Posicionamiento Comercial</h2>
                <p className="text-gray-700">{pack.commercial_positioning}</p>
              </section>
            )}

            {pack.target_audience && (
              <section>
                <h2 className="text-lg font-semibold text-gray-900 mb-2">Público Objetivo</h2>
                <p className="text-gray-700">{pack.target_audience}</p>
              </section>
            )}

            {pack.comparables && pack.comparables.length > 0 && (
              <section>
                <h2 className="text-lg font-semibold text-gray-900 mb-2">Títulos Comparables</h2>
                <ul className="list-disc pl-5 text-gray-700">
                  {pack.comparables.map((c, i) => (
                    <li key={i}>{c.title} ({c.year}) - {c.box_office}</li>
                  ))}
                </ul>
              </section>
            )}

            {pack.territory_strategy && pack.territory_strategy.length > 0 && (
              <section>
                <h2 className="text-lg font-semibold text-gray-900 mb-2">Estrategia Territorial</h2>
                <ul className="list-disc pl-5 text-gray-700">
                  {(pack.territory_strategy as Array<{priority: string, territory: string}>).map((t, i) => (
                    <li key={i}>{t.priority.toUpperCase()}: {t.territory}</li>
                  ))}
                </ul>
              </section>
            )}

            {pack.available_materials && pack.available_materials.length > 0 && (
              <section>
                <h2 className="text-lg font-semibold text-gray-900 mb-2">Materiales Disponibles</h2>
                <ul className="list-disc pl-5 text-gray-700">
                  {(pack.available_materials as Array<{material: string, status: string}>).map((m, i) => (
                    <li key={i}>{m.material}: <span className="font-medium">{m.status}</span></li>
                  ))}
                </ul>
              </section>
            )}

            {pack.sales_arguments && pack.sales_arguments.length > 0 && (
              <section>
                <h2 className="text-lg font-semibold text-gray-900 mb-2">Argumentos de Venta</h2>
                <ul className="list-disc pl-5 text-gray-700">
                  {pack.sales_arguments.map((a, i) => (
                    <li key={i}>{a}</li>
                  ))}
                </ul>
              </section>
            )}

            {pack.risks && pack.risks.length > 0 && (
              <section>
                <h2 className="text-lg font-semibold text-gray-900 mb-2">Riesgos</h2>
                <ul className="list-disc pl-5 text-gray-700">
                  {pack.risks.map((r, i) => (
                    <li key={i}>{r}</li>
                  ))}
                </ul>
              </section>
            )}
          </div>
        </>
      )}
    </div>
  )
}