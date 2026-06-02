import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { AlertCircle, Clapperboard, Download, Layers, RefreshCw, Scissors } from 'lucide-react'
import { editorialApi, projectsApi } from '@/api'
import type { AssemblyCut, EditorialFCPXMLStatus, EditorialRecommendedTake, EditorialTake, DavinciPlatformExportRequest } from '@/api/editorial'
import { useLanguage } from '@/i18n'

export default function EditorialAssemblyPage() {
  const { t } = useLanguage()
  const { projectId = '' } = useParams()
  const [projectName, setProjectName] = useState('')
  const [takes, setTakes] = useState<EditorialTake[]>([])
  const [recommended, setRecommended] = useState<EditorialRecommendedTake[]>([])
  const [assembly, setAssembly] = useState<AssemblyCut | null>(null)
  const [fcpxmlStatus, setFcpxmlStatus] = useState<EditorialFCPXMLStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [action, setAction] = useState<string | null>(null)
  const [message, setMessage] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  // DaVinci multiplatform export state
  const [davinciPlatform, setDavinciPlatform] = useState<DavinciPlatformExportRequest['platform']>('windows')
  const [davinciRootPath, setDavinciRootPath] = useState('C:/CID_DaVinci_Export')
  const [davinciIncludeMedia, setDavinciIncludeMedia] = useState(true)
  const [davinciAudioMode, setDavinciAudioMode] = useState<DavinciPlatformExportRequest['audio_mode']>('conservative')
  const [davinciExporting, setDavinciExporting] = useState(false)

  const loadState = async () => {
    if (!projectId) return
    setLoading(true)
    setError(null)
    try {
      const [project, takeItems, recommendedItems] = await Promise.all([
        projectsApi.get(projectId),
        editorialApi.listTakes(projectId),
        editorialApi.listRecommendedTakes(projectId),
      ])
      setProjectName(project.name)
      setTakes(takeItems)
      setRecommended(recommendedItems)
      try {
        const currentAssembly = await editorialApi.getAssembly(projectId)
        setAssembly(currentAssembly)
        try {
          const status = await editorialApi.getFCPXMLStatus(projectId)
          setFcpxmlStatus(status)
        } catch {
          setFcpxmlStatus(null)
        }
      } catch {
        setAssembly(null)
        setFcpxmlStatus(null)
      }
    } catch (err) {
      setError(t('internal.editorialAssembly.loadStateError'))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadState()
  }, [projectId])

  const downloadBlob = (blob: Blob, fileName: string) => {
    const url = URL.createObjectURL(blob)
    const anchor = document.createElement('a')
    anchor.href = url
    anchor.download = fileName
    document.body.appendChild(anchor)
    anchor.click()
    anchor.remove()
    URL.revokeObjectURL(url)
  }

  const runAction = async (label: string, callback: () => Promise<void>) => {
    setAction(label)
    setMessage(null)
    setError(null)
    try {
      await callback()
      await loadState()
    } catch {
      setError(t('internal.editorialAssembly.actionFailed').replace('{action}', label))
    } finally {
      setAction(null)
    }
  }

  const handleDavinciExport = async () => {
    setDavinciExporting(true)
    setMessage(null)
    setError(null)
    try {
      const payload: DavinciPlatformExportRequest = {
        platform: davinciPlatform,
        root_path: davinciRootPath,
        include_media: davinciIncludeMedia,
        audio_mode: davinciAudioMode,
      }
      const blob = await editorialApi.exportDavinciPackage(projectId, payload)
      downloadBlob(blob, `${projectName || 'project'}_davinci_${davinciPlatform}.fcpxml`)
      setMessage(t('internal.editorialAssembly.davinciExported').replace('{platform}', davinciPlatform))
    } catch (err) {
      setError(t('internal.editorialAssembly.davinciExportError').replace('{err}', String(err)))
    } finally {
      setDavinciExporting(false)
    }
  }

  const defaultRootPaths: Record<string, string> = {
    windows: 'C:/CID_DaVinci_Export',
    mac: '/Users/cliente/CID_DaVinci_Export',
    linux: '/home/cliente/CID_DaVinci_Export',
    offline: '(auto)',
    all: 'C:/CID_DaVinci_Export',
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center p-12">
        <div className="animate-spin w-8 h-8 border-2 border-amber-500 border-t-transparent rounded-full" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="space-y-6">
        <h1 className="heading-lg text-white flex items-center gap-3">
          <Clapperboard className="h-6 w-6 text-amber-400" />
          {t('internal.editorialAssembly.title')}
        </h1>
        <div className="card">
          <div className="text-center p-12">
            <AlertCircle className="w-16 h-16 mx-auto mb-4 text-red-400" />
            <h2 className="heading-md mb-2">{t('internal.editorialAssembly.loadErrorTitle')}</h2>
            <p className="text-slate-400 mb-6">{error}</p>
            <button onClick={loadState} className="btn-primary">
              {t('internal.common.retry')}
            </button>
            <Link to={`/projects/${projectId}/dashboard`} className="btn-secondary ml-3">
              {t('internal.editorialAssembly.backToProject')}
            </Link>
          </div>
        </div>
      </div>
    )
  }

  const isEmpty = !assembly && takes.length === 0 && recommended.length === 0

  if (isEmpty) {
    return (
      <div className="space-y-6">
        <h1 className="heading-lg text-white flex items-center gap-3">
          <Clapperboard className="h-6 w-6 text-amber-400" />
          {t('internal.editorialAssembly.title')}
        </h1>
        <div className="card">
          <div className="text-center p-12">
            <Scissors className="w-16 h-16 mx-auto mb-4 text-slate-500" />
            <h2 className="heading-md mb-2">{t('internal.editorialAssembly.emptyTitle')}</h2>
            <p className="text-slate-400 mb-6">
              {t('internal.editorialAssembly.emptyText')}
            </p>
            <Link to={`/projects/${projectId}/dashboard`} className="btn-primary">
              {t('internal.editorialAssembly.goToProject')}
            </Link>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between gap-4">
        <div>
          <Link to={`/projects/${projectId}`} className="text-sm text-amber-400 hover:text-amber-300">
            {t('internal.editorialAssembly.backToProjectArrow')}
          </Link>
          <h1 className="mt-2 text-2xl font-semibold text-white flex items-center gap-3">
            <Clapperboard className="h-6 w-6 text-amber-400" />
            {t('internal.editorialAssembly.title')}
          </h1>
          <p className="mt-1 text-sm text-slate-400">{projectName || t('internal.common.project')} · {t('internal.editorialAssembly.mvpFlow')}</p>
        </div>
        <div className="flex flex-wrap gap-3">
          <button className="btn-secondary" onClick={loadState}>
            <RefreshCw className="h-4 w-4" />
            {t('internal.editorialAssembly.refresh')}
          </button>
          <button
            className="btn-secondary"
            disabled={!!action}
            onClick={() => runAction(t('internal.editorialAssembly.reconcileMaterial'), async () => {
              await editorialApi.reconcile(projectId)
              setMessage(t('internal.editorialAssembly.reconciliationCompleted'))
            })}
          >
            <Layers className="h-4 w-4" />
            {t('internal.editorialAssembly.reconcileMaterial')}
          </button>
          <button
            className="btn-secondary"
            disabled={!!action}
            onClick={() => runAction(t('internal.editorialAssembly.calculateRecommendedTakes'), async () => {
              await editorialApi.score(projectId)
              setMessage(t('internal.editorialAssembly.scoringCompleted'))
            })}
          >
            <Scissors className="h-4 w-4" />
            {t('internal.editorialAssembly.calculateRecommendedTakes')}
          </button>
          <button
            className="btn-primary"
            disabled={!!action}
            onClick={() => runAction(t('internal.editorialAssembly.generateAssemblyCut'), async () => {
              const result = await editorialApi.generateAssembly(projectId)
              setAssembly(result.assembly_cut)
              setMessage(t('internal.editorialAssembly.assemblyGenerated').replace('{count}', String(result.items_created)))
            })}
          >
            {t('internal.editorialAssembly.generateAssemblyCut')}
          </button>
          <button
            className="btn-secondary"
            disabled={!!action || !assembly}
            onClick={() => runAction(t('internal.editorialAssembly.validateFCPXML'), async () => {
              const validation = await editorialApi.validateFCPXML(projectId)
              setFcpxmlStatus((current) => current ? { ...current, validation } : current)
              setMessage(validation.valid ? t('internal.editorialAssembly.fcpxmlValidated') : t('internal.editorialAssembly.fcpxmlErrors').replace('{count}', String(validation.errors.length)))
            })}
          >
            {t('internal.editorialAssembly.validateFCPXML')}
          </button>
          <button
            className="btn-primary"
            disabled={!!action || !assembly}
            onClick={() => runAction(t('internal.editorialAssembly.exportFCPXML'), async () => {
              const blob = await editorialApi.exportFCPXML(projectId)
              downloadBlob(blob, `${projectName || 'project'}_assembly.fcpxml`)
              setMessage(t('internal.editorialAssembly.fcpxmlExported'))
            })}
          >
            <Download className="h-4 w-4" />
            {t('internal.editorialAssembly.exportFCPXML')}
          </button>
          <button
            className="btn-primary"
            disabled={!!action || !assembly}
            onClick={() => runAction(t('internal.editorialAssembly.exportEditorialPackageZip'), async () => {
              const blob = await editorialApi.exportEditorialPackage(projectId)
              downloadBlob(blob, `${projectName || 'project'}_editorial_package.zip`)
              setMessage(t('internal.editorialAssembly.editorialPackageExported'))
            })}
          >
            <Download className="h-4 w-4" />
            {t('internal.editorialAssembly.exportEditorialPackageZip')}
          </button>
        </div>
      </div>

      {action && <div className="rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-slate-300">{t('internal.editorialAssembly.runningAction').replace('{action}', action)}</div>}
      {message && <div className="rounded-xl border border-green-500/20 bg-green-500/10 px-4 py-3 text-sm text-green-200">{message}</div>}
      {error && <div className="rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-200">{error}</div>}

      <section className="card card-hover space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="heading-md">{t('internal.editorialAssembly.davinciExportTitle')}</h2>
          <span className="text-sm text-slate-400">{fcpxmlStatus?.clip_count ?? assembly?.items.length ?? 0} {t('internal.editorialAssembly.clips')}</span>
        </div>
        {!assembly || !fcpxmlStatus ? (
          <p className="text-sm text-slate-400">{t('internal.editorialAssembly.generateAssemblyCutHint')}</p>
        ) : (
          <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-5">
            <div className="rounded-xl border border-white/10 bg-dark-300/40 p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-slate-500">{t('internal.editorialAssembly.fcpxmlStatus')}</p>
              <p className="mt-2 text-lg font-semibold text-white">{fcpxmlStatus.validation.valid ? t('internal.editorialAssembly.valid') : t('internal.editorialAssembly.withErrors')}</p>
            </div>
            <div className="rounded-xl border border-white/10 bg-dark-300/40 p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-slate-500">{t('internal.editorialAssembly.mediaResolved')}</p>
              <p className="mt-2 text-lg font-semibold text-white">{fcpxmlStatus.media_relink_report.resolved_media_count}</p>
            </div>
            <div className="rounded-xl border border-white/10 bg-dark-300/40 p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-slate-500">{t('internal.editorialAssembly.mediaOffline')}</p>
              <p className="mt-2 text-lg font-semibold text-white">{fcpxmlStatus.media_relink_report.offline_media_count}</p>
            </div>
            <div className="rounded-xl border border-white/10 bg-dark-300/40 p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-slate-500">{t('internal.editorialAssembly.warnings')}</p>
              <p className="mt-2 text-lg font-semibold text-white">{fcpxmlStatus.warnings.length}</p>
            </div>
            <div className="rounded-xl border border-white/10 bg-dark-300/40 p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-slate-500">{t('internal.editorialAssembly.file')}</p>
              <p className="mt-2 text-sm font-medium text-slate-200 break-all">{fcpxmlStatus.file_name}</p>
            </div>
          </div>
        )}
        {fcpxmlStatus && (fcpxmlStatus.validation.errors.length > 0 || fcpxmlStatus.warnings.length > 0) && (
          <div className="rounded-xl border border-amber-500/20 bg-amber-500/10 p-4 text-sm text-amber-100 space-y-2">
            {fcpxmlStatus.validation.errors.length > 0 && <p>{t('internal.editorialAssembly.errors')}: {fcpxmlStatus.validation.errors.join(' · ')}</p>}
            {fcpxmlStatus.warnings.length > 0 && <p>{t('internal.editorialAssembly.warnings')}: {fcpxmlStatus.warnings.join(' · ')}</p>}
          </div>
        )}
      </section>

      <section className="card card-hover space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="heading-md">{t('internal.editorialAssembly.davinciExportMultiplatform')}</h2>
        </div>
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <div>
            <label className="block text-xs uppercase tracking-[0.2em] text-slate-500 mb-2">{t('internal.editorialAssembly.platform')}</label>
            <select
              value={davinciPlatform}
              onChange={(e) => {
                const plat = e.target.value as DavinciPlatformExportRequest['platform']
                setDavinciPlatform(plat)
                setDavinciRootPath(defaultRootPaths[plat] || defaultRootPaths.windows)
              }}
              className="input w-full"
            >
              <option value="windows">Windows</option>
              <option value="mac">macOS</option>
              <option value="linux">Linux</option>
              <option value="offline">Offline / relink manual</option>
            </select>
          </div>
          <div>
            <label className="block text-xs uppercase tracking-[0.2em] text-slate-500 mb-2">{t('internal.editorialAssembly.rootPath')}</label>
            <input
              type="text"
              value={davinciRootPath}
              onChange={(e) => setDavinciRootPath(e.target.value)}
              placeholder={davinciPlatform === 'offline' ? '(auto)' : 'C:/CID_DaVinci_Export'}
              className="input w-full font-mono text-sm"
              disabled={davinciPlatform === 'offline'}
            />
          </div>
          <div>
            <label className="block text-xs uppercase tracking-[0.2em] text-slate-500 mb-2">{t('internal.editorialAssembly.audio')}</label>
            <select
              value={davinciAudioMode}
              onChange={(e) => setDavinciAudioMode(e.target.value as DavinciPlatformExportRequest['audio_mode'])}
              className="input w-full"
            >
              <option value="conservative">Conservative (SAFE)</option>
              <option value="experimental">Experimental (CANDIDATE)</option>
            </select>
          </div>
          <div className="flex items-end">
            <label className="flex items-center gap-2 text-sm text-slate-300">
              <input
                type="checkbox"
                checked={davinciIncludeMedia}
                onChange={(e) => setDavinciIncludeMedia(e.target.checked)}
                className="checkbox"
              />
              {t('internal.editorialAssembly.includeMedia')}
            </label>
          </div>
        </div>
        <div className="rounded-xl border border-amber-500/20 bg-amber-500/10 px-4 py-2 text-xs text-amber-100">
          {t('internal.editorialAssembly.audioModeHelp')}
        </div>
        <button
          className="btn-primary"
          disabled={davinciExporting || !assembly}
          onClick={handleDavinciExport}
        >
          {davinciExporting ? t('internal.editorialAssembly.exporting') : t('internal.editorialAssembly.generateDavinciPackage')}
        </button>
      </section>

      <section className="card card-hover space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="heading-md">{t('internal.editorialAssembly.takes')}</h2>
          <span className="text-sm text-slate-400">{takes.length}</span>
        </div>
        <div className="overflow-auto">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="text-left text-slate-500">
                <th className="py-2 pr-4">{t('internal.editorialAssembly.scene')}</th>
                <th className="py-2 pr-4">{t('internal.editorialAssembly.shot')}</th>
                <th className="py-2 pr-4">{t('internal.editorialAssembly.take')}</th>
                <th className="py-2 pr-4">{t('internal.editorialAssembly.status')}</th>
                <th className="py-2 pr-4">{t('internal.editorialAssembly.camera')}</th>
                <th className="py-2 pr-4">{t('internal.editorialAssembly.sound')}</th>
                <th className="py-2 pr-4">{t('internal.editorialAssembly.audioMetadata')}</th>
                <th className="py-2 pr-4">{t('internal.editorialAssembly.dualSystem')}</th>
                <th className="py-2 pr-4">{t('internal.editorialAssembly.sync')}</th>
                <th className="py-2 pr-4">{t('internal.editorialAssembly.score')}</th>
              </tr>
            </thead>
            <tbody>
              {takes.map((take) => (
                <tr key={take.id} className="border-t border-white/5 text-slate-200">
                  <td className="py-2 pr-4">{take.scene_number ?? '—'}</td>
                  <td className="py-2 pr-4">{take.shot_number ?? '—'}</td>
                  <td className="py-2 pr-4">{take.take_number ?? '—'}</td>
                  <td className="py-2 pr-4">{take.reconciliation_status || 'partial'}</td>
                  <td className="py-2 pr-4">{take.video_filename || t('internal.editorialAssembly.missingCamera')}</td>
                  <td className="py-2 pr-4">{take.audio_filename || t('internal.editorialAssembly.missingAudio')}</td>
                  <td className="py-2 pr-4">{take.audio_metadata_status || 'n/a'}</td>
                  <td className="py-2 pr-4">{take.dual_system_status || 'n/a'}</td>
                  <td className="py-2 pr-4">{take.sync_method ? `${take.sync_method}${take.sync_confidence ? ` (${take.sync_confidence.toFixed(2)})` : ''}` : 'n/a'}</td>
                  <td className="py-2 pr-4">{take.score.toFixed(1)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="card card-hover space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="heading-md">{t('internal.editorialAssembly.recommendedTakes')}</h2>
          <span className="text-sm text-slate-400">{recommended.length}</span>
        </div>
        <div className="space-y-3">
          {recommended.map((item) => (
            <div key={item.take.id} className="rounded-xl border border-white/10 bg-dark-300/40 p-4">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <p className="font-medium text-white">
                    {t('internal.editorialAssembly.scene')} {item.scene_number ?? '—'} · {t('internal.editorialAssembly.shot')} {item.shot_number ?? '—'} · {t('internal.editorialAssembly.take')} {item.take.take_number ?? '—'}
                  </p>
                  <p className="mt-1 text-sm text-slate-400">{item.take.recommended_reason || t('internal.editorialAssembly.noEditorialReason')}</p>
                  {(item.take.sync_warning || item.take.conflict_flags.length > 0) && (
                    <p className="mt-1 text-xs text-amber-300">{item.take.sync_warning || item.take.conflict_flags.join(' · ')}</p>
                  )}
                </div>
                <span className="text-amber-400 font-semibold">{item.take.score.toFixed(1)}</span>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="card card-hover space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="heading-md">{t('internal.editorialAssembly.assemblyOrder')}</h2>
          <span className="text-sm text-slate-400">{assembly?.items.length ?? 0}</span>
        </div>
        {!assembly ? (
          <p className="text-sm text-slate-400">{t('internal.editorialAssembly.noAssemblyYet')}</p>
        ) : (
          <div className="space-y-3">
            {assembly.items.map((item) => (
              <div key={item.id} className="rounded-xl border border-white/10 bg-dark-300/40 p-4">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <p className="font-medium text-white">
                      #{item.order_index + 1} · {t('internal.editorialAssembly.scene')} {item.scene_number ?? '—'} · {t('internal.editorialAssembly.shot')} {item.shot_number ?? '—'} · {t('internal.editorialAssembly.take')} {item.take_number ?? '—'}
                    </p>
                    <p className="mt-1 text-sm text-slate-400">{item.recommended_reason || t('internal.editorialAssembly.noEditorialMotive')}</p>
                  </div>
                  <div className="text-sm text-slate-400">
                    IN {item.timeline_in ?? 0} · OUT {item.timeline_out ?? 0}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  )
}
