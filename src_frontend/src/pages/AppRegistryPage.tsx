import { useEffect, useState, useCallback } from 'react'
import api from '../api/client'
import {
  ExternalLink, Cpu, Wifi, WifiOff, Mic, Search, Calculator,
  Film, Music, Palette, DollarSign, RefreshCw, Puzzle, FolderOpen,
  Maximize2, X,
} from 'lucide-react'

const iconMap: Record<string, any> = {
  search: Search, mic: Mic, calculator: Calculator, film: Film,
  music: Music, palette: Palette, dollar: DollarSign, cpu: Cpu,
  puzzle: Puzzle, folder: FolderOpen,
}

interface AppManifest {
  app_id: string
  name: string
  version: string
  description: string
  category: string
  icon?: string
  pricing?: { standalone_monthly_eur?: number; included_in_cid?: boolean }
  entrypoints?: {
    api?: { url: string; health_endpoint?: string }
    frontend?: { url: string; type?: string; route?: string }
    cid_integration?: { api_prefix?: string; frontend_route?: string }
  }
  capabilities?: string[]
  _health?: { status: string; latency_ms?: number; status_code?: number }
}

interface HealthInfo {
  status?: string
  type?: string
  latency_ms?: number
  url?: string
}

export default function AppRegistryPage() {
  const [apps, setApps] = useState<AppManifest[]>([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [filter, setFilter] = useState<string>('all')
  const [embedApp, setEmbedApp] = useState<AppManifest | null>(null)

  const fetchApps = useCallback(async () => {
    try {
      const r = await api.get('/apps')
      setApps(r.data.apps || [])
    } catch {
      // silent
    }
    setLoading(false)
  }, [])

  useEffect(() => { fetchApps() }, [fetchApps])

  const handleRefresh = async () => {
    setRefreshing(true)
    try {
      await api.post('/apps/refresh')
      await fetchApps()
    } catch {
      // silent
    }
    setRefreshing(false)
  }

  const categories = Array.from(new Set(apps.map((a) => a.category).filter(Boolean)))
  const filtered = filter === 'all' ? apps : apps.filter((a) => a.category === filter)
  const onlineCount = apps.filter((a) => a._health?.status === 'online').length

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Ecosistema CID</h1>
          <p className="text-cine-400 mt-1">
            {apps.length} apps · {onlineCount} online
          </p>
        </div>
        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className="btn-secondary text-sm flex items-center gap-1"
        >
          <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
          {refreshing ? 'Actualizando...' : 'Actualizar'}
        </button>
      </div>

      <div className="flex gap-2 flex-wrap">
        <button
          onClick={() => setFilter('all')}
          className={`px-3 py-1.5 rounded-lg text-xs border transition-colors ${
            filter === 'all' ? 'bg-amber-500/20 border-amber-500/30 text-amber-400' : 'bg-dark-600 border-white/10 text-cine-300 hover:border-white/20'
          }`}
        >Todas</button>
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setFilter(cat)}
            className={`px-3 py-1.5 rounded-lg text-xs border transition-colors ${
              filter === cat ? 'bg-amber-500/20 border-amber-500/30 text-amber-400' : 'bg-dark-600 border-white/10 text-cine-300 hover:border-white/20'
            }`}
          >{cat}</button>
        ))}
      </div>

      {loading ? (
        <div className="text-cine-400 text-center py-12">Cargando...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((app) => {
            const Icon = iconMap[app.icon || 'cpu'] || Cpu
            const health = app._health ?? {} as HealthInfo
            const isOnline = health.status === 'online'
            const cid = app.entrypoints?.cid_integration ?? {} as { api_prefix?: string; frontend_route?: string }
            const frontend = app.entrypoints?.frontend ?? {} as { url?: string; type?: string; route?: string }
            const isEmbed = frontend.type === 'embed'

            return (
              <div key={app.app_id} className={`card ${isOnline ? '' : 'opacity-70'}`}>
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                      isOnline ? 'bg-amber-500/10' : 'bg-cine-700'
                    }`}>
                      <Icon className={`w-5 h-5 ${isOnline ? 'text-amber-400' : 'text-cine-400'}`} />
                    </div>
                    <div>
                      <h3 className="text-white font-semibold">{app.name}</h3>
                      <p className="text-xs text-cine-400">{app.app_id} v{app.version}</p>
                    </div>
                  </div>
                  {isOnline ? (
                    <Wifi className="w-4 h-4 text-green-400" />
                  ) : (
                    <WifiOff className="w-4 h-4 text-red-400" />
                  )}
                </div>

                <p className="text-sm text-cine-300 mb-4 line-clamp-2">{app.description}</p>

                <div className="flex items-center gap-2 mb-3">
                  <span className="badge-blue text-xs">{app.category}</span>
                  <span className={`badge text-xs ${isOnline ? 'badge-green' : 'badge-red'}`}>
                    {isOnline ? `${health.latency_ms ?? ''}ms` : 'offline'}
                  </span>
                  {app.pricing?.included_in_cid && (
                    <span className="badge text-xs border-amber-500/30 text-amber-400">Incluida en CID</span>
                  )}
                </div>

                {app.capabilities && (
                  <div className="flex flex-wrap gap-1 mb-4">
                    {app.capabilities.slice(0, 4).map((cap: string) => (
                      <span key={cap} className="text-xs text-cine-400 bg-cine-700/50 px-2 py-0.5 rounded">
                        {cap}
                      </span>
                    ))}
                  </div>
                )}

                <div className="flex items-center gap-2 mt-auto">
                  {cid.frontend_route ? (
                    <a href={cid.frontend_route} className="btn-primary text-xs flex items-center gap-1">
                      Abrir en CID <ExternalLink className="w-3 h-3" />
                    </a>
                  ) : frontend.url ? (
                    isEmbed ? (
                      <button onClick={() => setEmbedApp(app)} className="btn-primary text-xs flex items-center gap-1">
                        Abrir <Maximize2 className="w-3 h-3" />
                      </button>
                    ) : (
                      <a href={frontend.url} target="_blank" rel="noopener noreferrer" className="btn-secondary text-xs flex items-center gap-1">
                        Abrir standalone <ExternalLink className="w-3 h-3" />
                      </a>
                    )
                  ) : (
                    <span className="text-xs text-cine-500">Sin interfaz</span>
                  )}

                  {app.pricing?.standalone_monthly_eur && (
                    <span className="text-xs text-cine-400 ml-auto">
                      {app.pricing.standalone_monthly_eur}€/mes
                    </span>
                  )}
                </div>
              </div>
            )
          })}

          {filtered.length === 0 && (
            <div className="card col-span-full text-center py-12">
              <Cpu className="w-12 h-12 text-cine-600 mx-auto mb-4" />
              <p className="text-cine-400">No se encontraron apps en esta categoría.</p>
            </div>
          )}
        </div>
      )}

      {embedApp && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-dark-400 rounded-2xl border border-white/10 w-full max-w-6xl max-h-[90vh] flex flex-col">
            <div className="flex items-center justify-between p-4 border-b border-white/5">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-amber-500/10 flex items-center justify-center">
                  <Maximize2 className="w-4 h-4 text-amber-400" />
                </div>
                <h3 className="text-white font-semibold">{embedApp.name}</h3>
                <span className="badge-blue text-xs">{embedApp.app_id}</span>
              </div>
              <button onClick={() => setEmbedApp(null)} className="p-2 text-cine-400 hover:text-white transition-colors">
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="flex-1 p-0">
              <iframe
                src={embedApp.entrypoints?.frontend?.url || ''}
                className="w-full h-[80vh] rounded-b-2xl"
                style={{ border: 'none' }}
                title={embedApp.name}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
