import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { AlertCircle, FileText, RefreshCw } from 'lucide-react'
import { producerPitchApi, ProducerPitchPack } from '../api/producerPitch'
import { t } from '@/i18n'

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
      setError(e.message || t('internal.producerPitchPackPage.errors.generate'))
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
      setError(e.message || t('internal.producerPitchPackPage.errors.export'))
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
        <div className="animate-spin w-8 h-8 border-2 border-amber-500 border-t-transparent rounded-full" />
      </div>
    )
  }

  if (error && !pack) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <h1 className="text-2xl font-bold text-white mb-4">{t('internal.producerPitchPackPage.title')}</h1>
        <div className="rounded-xl border border-red-500/20 bg-red-500/10 p-8 text-center">
          <AlertCircle className="w-12 h-12 mx-auto mb-3 text-red-400" />
          <h2 className="text-lg font-semibold text-white mb-2">{t('internal.producerPitchPackPage.errorTitle')}</h2>
          <p className="text-slate-400 mb-6">{error}</p>
          <button onClick={loadPack} className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
            <RefreshCw className="w-4 h-4 inline mr-1" /> {t('internal.common.retry')}
          </button>
          <Link to={`/projects/${projectId}/dashboard`} className="px-4 py-2 ml-3 border border-white/10 rounded text-white hover:bg-white/5">
            {t('internal.producerPitchPackPage.backToProject')}
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-white">{t('internal.producerPitchPackPage.title')}</h1>
        <p className="text-slate-400">{t('internal.producerPitchPackPage.subtitle')}</p>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-500/10 border border-red-500/20 text-red-400 rounded flex items-center gap-2">
          <AlertCircle className="w-4 h-4" /> {error}
          <button onClick={loadPack} className="ml-auto text-sm underline hover:no-underline">{t('internal.common.retry')}</button>
        </div>
      )}

      {!pack ? (
        <div className="text-center py-12">
          <FileText className="w-16 h-16 mx-auto mb-4 text-slate-500" />
          <p className="text-slate-400 mb-4">{t('internal.producerPitchPackPage.empty')}</p>
          <button
            onClick={handleGenerate}
            disabled={generating}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {generating ? t('internal.producerPitchPackPage.generating') : t('internal.producerPitchPackPage.generate')}
          </button>
        </div>
      ) : (
        <>
          <div className="mb-4 flex items-center justify-between">
            <span className="text-sm text-gray-500">
              {t('internal.producerPitchPackPage.status')}: <span className="font-medium capitalize">{pack.status}</span>
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
                <h2 className="text-lg font-semibold text-gray-900 mb-2">{t('internal.producerPitchPackPage.sections.logline')}</h2>
                <p className="text-gray-700">{pack.logline}</p>
              </section>
            )}

            {pack.short_synopsis && (
              <section>
                <h2 className="text-lg font-semibold text-gray-900 mb-2">{t('internal.producerPitchPackPage.sections.shortSynopsis')}</h2>
                <p className="text-gray-700">{pack.short_synopsis}</p>
              </section>
            )}

            {pack.long_synopsis && (
              <section>
                <h2 className="text-lg font-semibold text-gray-900 mb-2">{t('internal.producerPitchPackPage.sections.longSynopsis')}</h2>
                <p className="text-gray-700 whitespace-pre-wrap">{pack.long_synopsis}</p>
              </section>
            )}

            {pack.intention_note && (
              <section>
                <h2 className="text-lg font-semibold text-gray-900 mb-2">{t('internal.producerPitchPackPage.sections.intentionNote')}</h2>
                <p className="text-gray-700">{pack.intention_note}</p>
              </section>
            )}

            {(pack.genre || pack.format || pack.tone) && (
              <section>
                <h2 className="text-lg font-semibold text-gray-900 mb-2">{t('internal.producerPitchPackPage.sections.genreFormat')}</h2>
                <p className="text-gray-700">
                  {pack.genre && <span className="mr-4">{t('internal.producerPitchPackPage.fields.genre')}: {pack.genre}</span>}
                  {pack.format && <span className="mr-4">{t('internal.producerPitchPackPage.fields.format')}: {pack.format}</span>}
                  {pack.tone && <span>{t('internal.producerPitchPackPage.fields.tone')}: {pack.tone}</span>}
                </p>
              </section>
            )}

            {pack.target_audience && (
              <section>
                <h2 className="text-lg font-semibold text-gray-900 mb-2">{t('internal.producerPitchPackPage.sections.targetAudience')}</h2>
                <p className="text-gray-700">{pack.target_audience}</p>
              </section>
            )}

            {pack.budget_summary && Object.keys(pack.budget_summary).length > 0 && (
              <section>
                <h2 className="text-lg font-semibold text-gray-900 mb-2">{t('internal.producerPitchPackPage.sections.budgetSummary')}</h2>
                <p className="text-gray-700">
                  {t('internal.producerPitchPackPage.fields.total')}: €{((pack.budget_summary as any).total_estimated || 0).toLocaleString()}
                </p>
              </section>
            )}

            {pack.funding_summary && Object.keys(pack.funding_summary).length > 0 && (
              <section>
                <h2 className="text-lg font-semibold text-gray-900 mb-2">{t('internal.producerPitchPackPage.sections.funding')}</h2>
                <p className="text-gray-700">{(pack.funding_summary as any).message}</p>
              </section>
            )}

            {pack.commercial_strengths && pack.commercial_strengths.length > 0 && (
              <section>
                <h2 className="text-lg font-semibold text-gray-900 mb-2">{t('internal.producerPitchPackPage.sections.commercialStrengths')}</h2>
                <ul className="list-disc pl-5 text-gray-700">
                  {pack.commercial_strengths.map((s, i) => (
                    <li key={i}>{s}</li>
                  ))}
                </ul>
              </section>
            )}

            {pack.risks && pack.risks.length > 0 && (
              <section>
                <h2 className="text-lg font-semibold text-gray-900 mb-2">{t('internal.producerPitchPackPage.sections.risks')}</h2>
                <ul className="list-disc pl-5 text-gray-700">
                  {pack.risks.map((r, i) => (
                    <li key={i}>{r}</li>
                  ))}
                </ul>
              </section>
            )}
          </div>

          <div className="mt-8 p-4 bg-gray-50 rounded text-sm text-gray-600">
            <em>{t('internal.producerPitchPackPage.disclaimer')}</em>
          </div>
        </>
      )}
    </div>
  )
}