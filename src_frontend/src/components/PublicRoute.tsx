import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuthStore, getPrimaryCIDTarget } from '@/store'

interface PublicRouteProps {
  children?: React.ReactNode
}

export default function PublicRoute({ children }: PublicRouteProps) {
  const { isAuthenticated, sessionReady, user } = useAuthStore()
  const location = useLocation()

  if (!sessionReady) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-dark-300">
        <div className="flex items-center gap-3 text-amber-400">
          <svg className="animate-spin w-6 h-6" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
          <span className="text-sm">Cargando...</span>
        </div>
      </div>
    )
  }

  if (isAuthenticated) {
    const from = (location.state as { from?: Location })?.from?.pathname
    if (from) {
      return <Navigate to={from} replace />
    }
    return <Navigate to={getPrimaryCIDTarget(user)} replace />
  }

  return <>{children ?? <Outlet />}</>
}
