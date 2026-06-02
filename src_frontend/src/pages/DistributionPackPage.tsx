import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { AlertCircle, Film, RefreshCw } from 'lucide-react'
import { distributionPackApi, DistributionPack } from '../api/distributionPack'
import { t } from '@/i18n'

const PACK_TYPES = [
  { value: 'distributor', label: 'Distribuidora' },
  { value: 'sales_agent', label: 'Agente de ventas' },
  { value: 'festival', label: 'Festival' },
  { value: 'cinema', label: t('internal.distributionPackPage.packTypes.cinema') },
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
      setError(e.message || t('internal.distributionPackPage.errors.generate'))
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
      setError(e.message || t('internal.distributionPackPage.errors.export'))
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
        <div className="animate-spin w-8 h-8 border-2 border-amber-500 border-t-transparent rounded-full" />
      </div>
    )
  }

  if (error && !pack) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <h1 className="text-2xl font-bold text-white mb-4">{t('internal.distributionPackPage.title')}</h1>
        <div className="rounded-xl border border-red-500/20 bg-red-500/10 p-8 text-center">
          <AlertCircle className="w-12 h-12 mx-auto mb-3 text-red-400" />
          <h2 className="text-lg font-semibold text-white mb-2">{t('internal.distributionPackPage.errorTitle')}</h2>
          <p className="text-slate-400 mb-6">{error}</p>
          <button onClick={loadPack} className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
            <RefreshCw className="w-4 h-4 inline mr-1" /> {t('internal.common.retry')}
          </button>
          <Link to={`/projects/${projectId}/dashboard`} className="px-4 py-2 ml-3 border border-white/10 rounded text-white hover:bg-white/5">
            {t('internal.distributionPackPage.backToProject')}
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-white">{t('internal.distributionPackPage.title')}</h1>
        <p className="text-slate-400">{t('internal.distributionPackPage.subtitle')}</p>
      </div>

      <div className="mb-4 p-3 bg-amber-500/10 border border-amber-500/20 text-amber-200 rounded text-sm">
         <em>{t('internal.distributionPackPage.disclaimer')}</em>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-500/10 border border-red-500/20 text-red-400 rounded flex items-center gap-2">
          <AlertCircle className="w-4 h-4" /> {error}
          <button onClick={loadPack} className="ml-auto text-sm underline hover:no-underline">{t('internal.common.retry')}</button>
        </div>
      )}

      {!pack ? (
        <div className="text-center py-12">
          <Film className="w-16 h-16 mx-auto mb-4 text-slate-500" />
          <p className="text-slate-400 mb-4">{t('internal.distributionPackPage.empty')}</p>
          <div className="mb-4">
            <label className="block text-sm font-medium text-slate-300 mb-1">{t('internal.distributionPackPage.packType')}</label>
            <select
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value)}
              className="border border-white/10 rounded px-3 py-2 w-64 bg-white/5 text-white"
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
            {generating ? t('internal.distributionPackPage.generating') : t('internal.distributionPackPage.generate')}
          </button>
        </div>
      ) : (
        <>
          <div className="mb-4 flex items-center justify-between">
            <span className="text-sm text-gray-500">
              Tipo: <span className="font-medium">{pack.pack_type}</span> | 
              {t('internal.distributionPackPage.status')}: <span className="font-medium capitalize">{pack.status}</span>
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
                <h2 className="text-lg font-semibold text-gray-900 mb-2">{t('internal.distributionPackPage.sections.logline')}</h2>
                <p className="text-gray-700">{pack.logline}</p>
              </section>
            )}

            {pack.short_synopsis && (
              <section>
                <h2 className="text-lg font-semibold text-gray-900 mb-2">{t('internal.distributionPackPage.sections.synopsis')}</h2>
                <p className="text-gray-700">{pack.short_synopsis}</p>
              </section>
            )}

            {pack.commercial_positioning && (
              <section>
                <h2 className="text-lg font-semibold text-gray-900 mb-2">{t('internal.distributionPackPage.sections.commercialPositioning')}</h2>
                <p className="text-gray-700">{pack.commercial_positioning}</p>
              </section>
            )}

            {pack.target_audience && (
              <section>
                <h2 className="text-lg font-semibold text-gray-900 mb-2">{t('internal.distributionPackPage.sections.targetAudience')}</h2>
                <p className="text-gray-700">{pack.target_audience}</p>
              </section>
            )}

            {pack.comparables && pack.comparables.length > 0 && (
              <section>
                <h2 className="text-lg font-semibold text-gray-900 mb-2">{t('internal.distributionPackPage.sections.comparableTitles')}</h2>
                <ul className="list-disc pl-5 text-gray-700">
                  {pack.comparables.map((c, i) => (
                    <li key={i}>{c.title} ({c.year}) - {c.box_office}</li>
                  ))}
                </ul>
              </section>
            )}

            {pack.territory_strategy && pack.territory_strategy.length > 0 && (
              <section>
                <h2 className="text-lg font-semibold text-gray-900 mb-2">{t('internal.distributionPackPage.sections.territorialStrategy')}</h2>
                <ul className="list-disc pl-5 text-gray-700">
                  {(pack.territory_strategy as Array<{priority: string, territory: string}>).map((t, i) => (
                    <li key={i}>{t.priority.toUpperCase()}: {t.territory}</li>
                  ))}
                </ul>
              </section>
            )}

            {pack.available_materials && pack.available_materials.length > 0 && (
              <section>
                <h2 className="text-lg font-semibold text-gray-900 mb-2">{t('internal.distributionPackPage.sections.availableMaterials')}</h2>
                <ul className="list-disc pl-5 text-gray-700">
                  {(pack.available_materials as Array<{material: string, status: string}>).map((m, i) => (
                    <li key={i}>{m.material}: <span className="font-medium">{m.status}</span></li>
                  ))}
                </ul>
              </section>
            )}

            {pack.sales_arguments && pack.sales_arguments.length > 0 && (
              <section>
                <h2 className="text-lg font-semibold text-gray-900 mb-2">{t('internal.distributionPackPage.sections.salesArguments')}</h2>
                <ul className="list-disc pl-5 text-gray-700">
                  {pack.sales_arguments.map((a, i) => (
                    <li key={i}>{a}</li>
                  ))}
                </ul>
              </section>
            )}

            {pack.risks && pack.risks.length > 0 && (
              <section>
                <h2 className="text-lg font-semibold text-gray-900 mb-2">{t('internal.distributionPackPage.sections.risks')}</h2>
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
