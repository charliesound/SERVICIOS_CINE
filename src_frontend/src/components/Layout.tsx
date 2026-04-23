import { Outlet, Link, useLocation } from 'react-router-dom'
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
  ExternalLink,
  Folder,
  Briefcase,
  HardDrive
} from 'lucide-react'
import clsx from 'clsx'

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/create', icon: PlusCircle, label: 'Crear' },
  { to: '/projects', icon: Folder, label: 'Proyectos' },
  { to: '/producer', icon: Briefcase, label: 'Productor' },
  { to: '/queue', icon: ListOrdered, label: 'Cola' },
  { to: '/workflows', icon: GitBranch, label: 'Workflows' },
  { to: '/plans', icon: CreditCard, label: 'Planes' },
  { to: '/storage-sources', icon: HardDrive, label: 'Storage' },
  { to: '/ingest/scans', icon: Search, label: 'Ingesta' },
  { to: '/documents', icon: FileText, label: 'Documentos' },
  { to: '/reports/camera', icon: ClipboardList, label: 'Reportes' },
  { to: '/history', icon: History, label: 'Historial' },
  { to: '/admin', icon: Settings, label: 'Admin' },
]

const externalLinks = [
  { to: '/portal', icon: ExternalLink, label: 'Portal Cliente' },
]

export default function Layout() {
  const location = useLocation()
  const { user, logout } = useAuthStore()

  const handleLogout = () => {
    logout()
    window.location.href = '/login'
  }

  return (
    <div className="min-h-screen flex bg-dark-300">
      {/* Sidebar estilo MITO */}
      <aside className="w-64 bg-dark-400/50 backdrop-blur-xl border-r border-white/5 flex flex-col">
        {/* Logo */}
        <div className="p-6 border-b border-white/5">
          <Link to="/" className="flex items-center gap-3 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-400 to-amber-600 flex items-center justify-center shadow-lg group-hover:shadow-amber-500/30 transition-shadow">
              <Clapperboard className="w-5 h-5 text-black" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-white tracking-tight">AILink</h1>
              <p className="text-xs text-amber-400/80 font-medium">CINEMA</p>
            </div>
          </Link>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-1">
          {navItems.map(({ to, icon: Icon, label }) => {
            const isActive = to === '/'
              ? location.pathname === '/'
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
          
          {/* External Links - Separator */}
          <div className="pt-4 mt-4 border-t border-white/5">
            <p className="px-4 pb-2 text-xs font-medium text-gray-500 uppercase tracking-wider">Externo</p>
            {externalLinks.map(({ to, icon: Icon, label }) => {
              const isActive = location.pathname === to
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
          </div>
        </nav>

        {/* User section */}
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

      {/* Main content */}
      <main className="flex-1 overflow-auto bg-dark-300">
        <div className="p-8 max-w-7xl mx-auto">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
