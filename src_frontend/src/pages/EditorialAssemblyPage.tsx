import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { Clapperboard, Download, Layers, RefreshCw, Scissors } from 'lucide-react'
import { editorialApi, projectsApi } from '@/api'
import type { AssemblyCut, EditorialFCPXMLStatus, EditorialRecommendedTake, EditorialTake, DavinciPlatformExportRequest } from '@/api/editorial'

export default function EditorialAssemblyPage() {
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
      setError('No se pudo cargar el estado editorial.')
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
      setError(`No se pudo ejecutar: ${label}`)
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
      setMessage(`Paquete DaVinci (${davinciPlatform}) exportado`)
    } catch (err) {
      setError(`Error exportando paquete DaVinci: ${err}`)
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
    return <div className="text-sm text-slate-400">Cargando estado editorial...</div>
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between gap-4">
        <div>
          <Link to={`/projects/${projectId}`} className="text-sm text-amber-400 hover:text-amber-300">
            ← Volver al proyecto
          </Link>
          <h1 className="mt-2 text-2xl font-semibold text-white flex items-center gap-3">
            <Clapperboard className="h-6 w-6 text-amber-400" />
            Premontaje / Assembly
          </h1>
          <p className="mt-1 text-sm text-slate-400">{projectName || 'Proyecto'} · flujo editorial MVP</p>
        </div>
        <div className="flex flex-wrap gap-3">
          <button className="btn-secondary" onClick={loadState}>
            <RefreshCw className="h-4 w-4" />
            Refresh
          </button>
          <button
            className="btn-secondary"
            disabled={!!action}
            onClick={() => runAction('Reconciliar material', async () => {
              await editorialApi.reconcile(projectId)
              setMessage('Reconciliación completada')
            })}
          >
            <Layers className="h-4 w-4" />
            Reconciliar material
          </button>
          <button
            className="btn-secondary"
            disabled={!!action}
            onClick={() => runAction('Calcular tomas recomendadas', async () => {
              await editorialApi.score(projectId)
              setMessage('Scoring completado')
            })}
          >
            <Scissors className="h-4 w-4" />
            Calcular tomas recomendadas
          </button>
          <button
            className="btn-primary"
            disabled={!!action}
            onClick={() => runAction('Generar AssemblyCut', async () => {
              const result = await editorialApi.generateAssembly(projectId)
              setAssembly(result.assembly_cut)
              setMessage(`AssemblyCut generado con ${result.items_created} items`)
            })}
          >
            Generar AssemblyCut
          </button>
          <button
            className="btn-secondary"
            disabled={!!action || !assembly}
            onClick={() => runAction('Validar FCPXML', async () => {
              const validation = await editorialApi.validateFCPXML(projectId)
              setFcpxmlStatus((current) => current ? { ...current, validation } : current)
              setMessage(validation.valid ? 'FCPXML validado' : `FCPXML con errores: ${validation.errors.length}`)
            })}
          >
            Validar FCPXML
          </button>
          <button
            className="btn-primary"
            disabled={!!action || !assembly}
            onClick={() => runAction('Exportar FCPXML', async () => {
              const blob = await editorialApi.exportFCPXML(projectId)
              downloadBlob(blob, `${projectName || 'project'}_assembly.fcpxml`)
              setMessage('FCPXML exportado')
            })}
          >
            <Download className="h-4 w-4" />
            Exportar FCPXML
          </button>
          <button
            className="btn-primary"
            disabled={!!action || !assembly}
            onClick={() => runAction('Exportar paquete editorial ZIP', async () => {
              const blob = await editorialApi.exportEditorialPackage(projectId)
              downloadBlob(blob, `${projectName || 'project'}_editorial_package.zip`)
              setMessage('Paquete editorial exportado')
            })}
          >
            <Download className="h-4 w-4" />
            Exportar paquete editorial ZIP
          </button>
        </div>
      </div>

      {action && <div className="rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-slate-300">Ejecutando: {action}</div>}
      {message && <div className="rounded-xl border border-green-500/20 bg-green-500/10 px-4 py-3 text-sm text-green-200">{message}</div>}
      {error && <div className="rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-200">{error}</div>}

      <section className="card card-hover space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="heading-md">Exportacion DaVinci</h2>
          <span className="text-sm text-slate-400">{fcpxmlStatus?.clip_count ?? assembly?.items.length ?? 0} clips</span>
        </div>
        {!assembly || !fcpxmlStatus ? (
          <p className="text-sm text-slate-400">Genera un AssemblyCut para habilitar validacion, export y relink report.</p>
        ) : (
          <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-5">
            <div className="rounded-xl border border-white/10 bg-dark-300/40 p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Estado FCPXML</p>
              <p className="mt-2 text-lg font-semibold text-white">{fcpxmlStatus.validation.valid ? 'Valido' : 'Con errores'}</p>
            </div>
            <div className="rounded-xl border border-white/10 bg-dark-300/40 p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Media resuelta</p>
              <p className="mt-2 text-lg font-semibold text-white">{fcpxmlStatus.media_relink_report.resolved_media_count}</p>
            </div>
            <div className="rounded-xl border border-white/10 bg-dark-300/40 p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Media offline</p>
              <p className="mt-2 text-lg font-semibold text-white">{fcpxmlStatus.media_relink_report.offline_media_count}</p>
            </div>
            <div className="rounded-xl border border-white/10 bg-dark-300/40 p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Warnings</p>
              <p className="mt-2 text-lg font-semibold text-white">{fcpxmlStatus.warnings.length}</p>
            </div>
            <div className="rounded-xl border border-white/10 bg-dark-300/40 p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Archivo</p>
              <p className="mt-2 text-sm font-medium text-slate-200 break-all">{fcpxmlStatus.file_name}</p>
            </div>
          </div>
        )}
        {fcpxmlStatus && (fcpxmlStatus.validation.errors.length > 0 || fcpxmlStatus.warnings.length > 0) && (
          <div className="rounded-xl border border-amber-500/20 bg-amber-500/10 p-4 text-sm text-amber-100 space-y-2">
            {fcpxmlStatus.validation.errors.length > 0 && <p>Errores: {fcpxmlStatus.validation.errors.join(' · ')}</p>}
            {fcpxmlStatus.warnings.length > 0 && <p>Warnings: {fcpxmlStatus.warnings.join(' · ')}</p>}
          </div>
        )}
      </section>

      <section className="card card-hover space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="heading-md">Exportacion DaVinci multiplataforma</h2>
        </div>
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <div>
            <label className="block text-xs uppercase tracking-[0.2em] text-slate-500 mb-2">Plataforma</label>
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
            <label className="block text-xs uppercase tracking-[0.2em] text-slate-500 mb-2">Ruta raiz</label>
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
            <label className="block text-xs uppercase tracking-[0.2em] text-slate-500 mb-2">Audio</label>
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
              Incluir media
            </label>
          </div>
        </div>
        <div className="rounded-xl border border-amber-500/20 bg-amber-500/10 px-4 py-2 text-xs text-amber-100">
          El modo conservative es el export seguro validado. El modo experimental intenta linked audio, pero todavia requiere validacion manual en DaVinci.
        </div>
        <button
          className="btn-primary"
          disabled={davinciExporting || !assembly}
          onClick={handleDavinciExport}
        >
          {davinciExporting ? 'Exportando...' : 'Generar paquete DaVinci'}
        </button>
      </section>

      <section className="card card-hover space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="heading-md">Takes</h2>
          <span className="text-sm text-slate-400">{takes.length}</span>
        </div>
        <div className="overflow-auto">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="text-left text-slate-500">
                <th className="py-2 pr-4">Escena</th>
                <th className="py-2 pr-4">Plano</th>
                <th className="py-2 pr-4">Toma</th>
                <th className="py-2 pr-4">Estado</th>
                <th className="py-2 pr-4">Camara</th>
                <th className="py-2 pr-4">Sonido</th>
                <th className="py-2 pr-4">Audio metadata</th>
                <th className="py-2 pr-4">Dual-system</th>
                <th className="py-2 pr-4">Sync</th>
                <th className="py-2 pr-4">Score</th>
              </tr>
            </thead>
            <tbody>
              {takes.map((take) => (
                <tr key={take.id} className="border-t border-white/5 text-slate-200">
                  <td className="py-2 pr-4">{take.scene_number ?? '—'}</td>
                  <td className="py-2 pr-4">{take.shot_number ?? '—'}</td>
                  <td className="py-2 pr-4">{take.take_number ?? '—'}</td>
                  <td className="py-2 pr-4">{take.reconciliation_status || 'partial'}</td>
                  <td className="py-2 pr-4">{take.video_filename || 'missing camera'}</td>
                  <td className="py-2 pr-4">{take.audio_filename || 'missing audio'}</td>
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
          <h2 className="heading-md">Tomas recomendadas</h2>
          <span className="text-sm text-slate-400">{recommended.length}</span>
        </div>
        <div className="space-y-3">
          {recommended.map((item) => (
            <div key={item.take.id} className="rounded-xl border border-white/10 bg-dark-300/40 p-4">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <p className="font-medium text-white">
                    Escena {item.scene_number ?? '—'} · Plano {item.shot_number ?? '—'} · Toma {item.take.take_number ?? '—'}
                  </p>
                  <p className="mt-1 text-sm text-slate-400">{item.take.recommended_reason || 'Sin razón editorial'}</p>
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
          <h2 className="heading-md">Orden de montaje</h2>
          <span className="text-sm text-slate-400">{assembly?.items.length ?? 0}</span>
        </div>
        {!assembly ? (
          <p className="text-sm text-slate-400">Todavía no existe un AssemblyCut para este proyecto.</p>
        ) : (
          <div className="space-y-3">
            {assembly.items.map((item) => (
              <div key={item.id} className="rounded-xl border border-white/10 bg-dark-300/40 p-4">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <p className="font-medium text-white">
                      #{item.order_index + 1} · Escena {item.scene_number ?? '—'} · Plano {item.shot_number ?? '—'} · Toma {item.take_number ?? '—'}
                    </p>
                    <p className="mt-1 text-sm text-slate-400">{item.recommended_reason || 'Sin motivo editorial'}</p>
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
