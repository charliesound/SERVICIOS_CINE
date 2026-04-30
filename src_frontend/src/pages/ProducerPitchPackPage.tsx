import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { producerPitchApi, ProducerPitchPack } from '../api/producerPitch'

export default function ProducerPitchPackPage() {
  const { projectId } = useParams<{ projectId: string }>()
  const [pack, setPack] = useState<ProducerPitchPack | null>(null)
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [exportFormat, setExportFormat] = useState<string | null>(null)

  useEffect(() => {
    loadPack()
  }, [projectId])

  const loadPack = async () => {
    if (!projectId) return
    try {
      const result = await producerPitchApi.getActive(projectId)
      setPack(result.pack)
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
      const result = await producerPitchApi.generate(projectId)
      if (result.pack_id) {
        const packResult = await producerPitchApi.get(projectId, result.pack_id)
        setPack(packResult.pack)
      }
    } catch (e: any) {
      setError(e.message || 'Error generating pitch pack')
    } finally {
      setGenerating(false)
    }
  }

  const handleExport = async (format: string) => {
    if (!projectId || !pack) return
    setExportFormat(format)
    try {
      if (format === 'json') {
        const data = await producerPitchApi.exportJson(projectId, pack.id)
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
        downloadBlob(blob, `pitch_pack_${pack.id}.json`)
      } else if (format === 'markdown') {
        const data = await producerPitchApi.exportMarkdown(projectId, pack.id)
        const blob = new Blob([data], { type: 'text/markdown' })
        downloadBlob(blob, `pitch_pack_${pack.id}.md`)
      } else if (format === 'zip') {
        const blob = await producerPitchApi.exportZip(projectId, pack.id)
        downloadBlob(blob, `pitch_pack_${pack.id}.zip`)
      }
    } catch (e: any) {
      setError(e.message || 'Error exporting')
    } finally {
      setExportFormat(null)
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
        <h1 className="text-2xl font-bold text-gray-900">Dossier para Productores</h1>
        <p className="text-gray-600">Documento de trabajo para pitching</p>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 text-red-700 rounded">{error}</div>
      )}

      {!pack ? (
        <div className="text-center py-12">
          <p className="text-gray-600 mb-4">No hay dossier generado para este proyecto.</p>
          <button
            onClick={handleGenerate}
            disabled={generating}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {generating ? 'Generando...' : 'Generar Dossier'}
          </button>
        </div>
      ) : (
        <>
          <div className="mb-4 flex items-center justify-between">
            <span className="text-sm text-gray-500">
              Estado: <span className="font-medium capitalize">{pack.status}</span>
            </span>
            <div className="space-x-2">
              <button
                onClick={() => handleExport('json')}
                disabled={exportFormat === 'json'}
                className="px-3 py-1 text-sm border rounded hover:bg-gray-50 disabled:opacity-50"
              >
                Export JSON
              </button>
              <button
                onClick={() => handleExport('markdown')}
                disabled={exportFormat === 'markdown'}
                className="px-3 py-1 text-sm border rounded hover:bg-gray-50 disabled:opacity-50"
              >
                Export Markdown
              </button>
              <button
                onClick={() => handleExport('zip')}
                disabled={exportFormat === 'zip'}
                className="px-3 py-1 text-sm border rounded hover:bg-gray-50 disabled:opacity-50"
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
                <h2 className="text-lg font-semibold text-gray-900 mb-2">Sinopsis Corta</h2>
                <p className="text-gray-700">{pack.short_synopsis}</p>
              </section>
            )}

            {pack.long_synopsis && (
              <section>
                <h2 className="text-lg font-semibold text-gray-900 mb-2">Sinopsis Larga</h2>
                <p className="text-gray-700 whitespace-pre-wrap">{pack.long_synopsis}</p>
              </section>
            )}

            {pack.intention_note && (
              <section>
                <h2 className="text-lg font-semibold text-gray-900 mb-2">Nota de Intención</h2>
                <p className="text-gray-700">{pack.intention_note}</p>
              </section>
            )}

            {(pack.genre || pack.format || pack.tone) && (
              <section>
                <h2 className="text-lg font-semibold text-gray-900 mb-2">Género / Formato</h2>
                <p className="text-gray-700">
                  {pack.genre && <span className="mr-4">Género: {pack.genre}</span>}
                  {pack.format && <span className="mr-4">Formato: {pack.format}</span>}
                  {pack.tone && <span>Tono: {pack.tone}</span>}
                </p>
              </section>
            )}

            {pack.target_audience && (
              <section>
                <h2 className="text-lg font-semibold text-gray-900 mb-2">Público Objetivo</h2>
                <p className="text-gray-700">{pack.target_audience}</p>
              </section>
            )}

            {pack.budget_summary && Object.keys(pack.budget_summary).length > 0 && (
              <section>
                <h2 className="text-lg font-semibold text-gray-900 mb-2">Resumen de Presupuesto</h2>
                <p className="text-gray-700">
                  Total: €{((pack.budget_summary as any).total_estimated || 0).toLocaleString()}
                </p>
              </section>
            )}

            {pack.funding_summary && Object.keys(pack.funding_summary).length > 0 && (
              <section>
                <h2 className="text-lg font-semibold text-gray-900 mb-2">Ayudas/Funding</h2>
                <p className="text-gray-700">{(pack.funding_summary as any).message}</p>
              </section>
            )}

            {pack.commercial_strengths && pack.commercial_strengths.length > 0 && (
              <section>
                <h2 className="text-lg font-semibold text-gray-900 mb-2">Fortalezas Comerciales</h2>
                <ul className="list-disc pl-5 text-gray-700">
                  {pack.commercial_strengths.map((s, i) => (
                    <li key={i}>{s}</li>
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

          <div className="mt-8 p-4 bg-gray-50 rounded text-sm text-gray-600">
            <em>Documento de trabajo para pitching. Revisar antes de enviar.</em>
          </div>
        </>
      )}
    </div>
  )
}