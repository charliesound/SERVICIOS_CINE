import { Navigate, useLocation } from 'react-router-dom'
import { useAuthStore, canAccessCID, canAccessProgram } from '@/store'
import type { CIDProgram } from '@/types'

interface PlanRouteProps {
  program: CIDProgram
  children: React.ReactNode
}

export default function PlanRoute({ program, children }: PlanRouteProps) {
  const { user, isAuthenticated, sessionReady } = useAuthStore()
  const location = useLocation()

  if (!sessionReady) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-dark-300">
        <div className="flex items-center gap-3 text-amber-400">
          <svg className="animate-spin w-6 h-6" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
          <span className="text-sm">Verificando acceso...</span>
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  if (!canAccessCID(user)) {
    return <Navigate to="/pending-access" state={{ from: location }} replace />
  }

  if (!canAccessProgram(user, program)) {
    return <Navigate to={`/cid/${user?.program || 'demo'}`} state={{ from: location }} replace />
  }

  return <>{children}</>
}
