import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/store'
import {
  LayoutDashboard,
  PlusCircle,
  ListOrdered,
  GitBranch,
  CreditCard,
  FileText,
  Search,
  ClipboardList,
  Settings,
  LogOut,
  Clapperboard,
  History,
  HardDrive,
  Film,
  FolderOpen,
  Sparkles,
  Grid2x2,
  BadgeEuro,
  Puzzle,
} from 'lucide-react'
import clsx from 'clsx'

const navItems = [
  { to: '/cid', icon: Film, label: 'CID' },
  { to: '/projects', icon: FolderOpen, label: 'Proyectos' },
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/create', icon: PlusCircle, label: 'Crear' },
  { to: '/queue', icon: ListOrdered, label: 'Cola' },
  { to: '/workflows', icon: GitBranch, label: 'Workflows' },
  { to: '/cid/pipeline-builder', icon: Sparkles, label: 'Pipeline Builder' },
  { to: '/solutions', icon: Grid2x2, label: 'Soluciones' },
  { to: '/apps', icon: Puzzle, label: 'Apps' },
  { to: '/pricing', icon: BadgeEuro, label: 'Precios' },
  { to: '/plans', icon: CreditCard, label: 'Planes' },
  { to: '/storage-sources', icon: HardDrive, label: 'Storage' },
  { to: '/ingest/scans', icon: Search, label: 'Escanear' },
  { to: '/documents', icon: FileText, label: 'Documentos' },
  { to: '/reports/camera', icon: ClipboardList, label: 'Reportes' },
  { to: '/history', icon: History, label: 'Historial' },
  { to: '/admin', icon: Settings, label: 'Admin' },
]

export default function AppShell() {
  const location = useLocation()
  const navigate = useNavigate()
  const { user, logout } = useAuthStore()
  const isCidHomePath =
    location.pathname === '/cid' ||
    /^\/cid\/(demo|creator|producer|studio|enterprise)$/.test(location.pathname)

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen flex bg-dark-300">
      <aside className="w-64 bg-dark-400/50 backdrop-blur-xl border-r border-white/5 flex flex-col">
          <div className="p-6 border-b border-white/5">
          <Link to="/cid" className="flex items-center gap-3 group">
            <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-amber-400 to-amber-600 flex items-center justify-center shadow-lg shadow-amber-500/20 group-hover:shadow-amber-500/30 transition-shadow">
              <Clapperboard className="w-6 h-6 text-black" />
            </div>
            <p className="text-lg font-bold text-white tracking-tight">AILinkCinema</p>
          </Link>
        </div>

        <nav className="flex-1 p-4 space-y-1">
          {navItems.map(({ to, icon: Icon, label }) => {
            const isActive = to === '/cid'
              ? isCidHomePath
              : location.pathname === to || location.pathname.startsWith(`${to}/`)
            return (
              <Link
                key={to}
                to={to}
                className={clsx(
                  'flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200',
                  isActive
                    ? 'bg-gradient-to-r from-amber-500/20 to-amber-600/10 text-amber-400 border border-amber-500/20'
                    : 'text-gray-400 hover:bg-white/5 hover:text-white'
                )}
              >
                <Icon className={clsx('w-5 h-5', isActive && 'text-amber-400')} />
                <span className="font-medium">{label}</span>
              </Link>
            )
          })}
        </nav>

        {user && (
          <div className="p-4 border-t border-white/5">
            <div className="flex items-center justify-between p-3 rounded-xl bg-white/5">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-amber-400 to-amber-600 flex items-center justify-center text-black text-sm font-bold">
                  {user.username.charAt(0).toUpperCase()}
                </div>
                <div>
                  <p className="text-sm font-medium text-white">{user.username}</p>
                  <span className={clsx('text-xs capitalize',
                    user.plan === 'studio' ? 'text-purple-400' :
                    user.plan === 'enterprise' ? 'text-amber-400' :
                    'text-gray-400'
                  )}>
                    {user.plan}
                  </span>
                </div>
              </div>
              <button
                onClick={handleLogout}
                className="p-2 text-gray-500 hover:text-amber-400 transition-colors"
                title="Cerrar sesión"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </aside>

      <main className="flex-1 overflow-auto bg-dark-300">
        <div className="p-8 max-w-7xl mx-auto">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
