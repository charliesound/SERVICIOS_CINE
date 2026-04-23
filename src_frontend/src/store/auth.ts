import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type {
  UserProfile,
  SignupType,
  CIDProgram,
  AccessLevel,
  AccountStatus,
  TokenResponse,
} from '@/types'
import { authApi } from '@/api'

export type { SignupType, CIDProgram, AccessLevel, AccountStatus }
export type { UserProfile }

export type { CIDProgram as Program }

interface AuthState {
  user: UserProfile | null
  token: string | null
  isAuthenticated: boolean
  sessionReady: boolean
  sessionLoading: boolean
  loginError: string | null
  returnTo: string | null

  bootstrapSession: () => Promise<void>
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  register: (username: string, email: string, password: string) => Promise<void>
  refreshProfile: () => Promise<void>
  completeOnboarding: () => Promise<void>
  setReturnTo: (path: string | null) => void
  clearError: () => void
  updateUser: (updates: Partial<UserProfile>) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      sessionReady: false,
      sessionLoading: false,
      loginError: null,
      returnTo: null,

      clearError: () => set({ loginError: null }),

      setReturnTo: (path) => set({ returnTo: path }),

      updateUser: (updates) => {
        const current = get().user
        if (!current) return
        set({ user: { ...current, ...updates } })
      },

      bootstrapSession: async () => {
        const { token: storedToken } = get()
        if (!storedToken) {
          set({ sessionReady: true, sessionLoading: false })
          return
        }

        set({ sessionLoading: true })
        try {
          const user = await authApi.getMe()
          set({
            user: {
              ...user,
              signup_type: (user as UserProfile).signup_type || 'cid_user',
              account_status: (user as UserProfile).account_status || 'active',
              access_level: (user as UserProfile).access_level || 'standard',
              cid_enabled: (user as UserProfile).cid_enabled ?? true,
              onboarding_completed: (user as UserProfile).onboarding_completed ?? false,
              program: (user as UserProfile).program || _inferProgram((user as UserProfile).plan),
            },
            isAuthenticated: true,
            sessionLoading: false,
            sessionReady: true,
          })
        } catch {
          set({
            user: null,
            token: null,
            isAuthenticated: false,
            sessionLoading: false,
            sessionReady: true,
          })
        }
      },

      login: async (email, password) => {
        set({ sessionLoading: true, loginError: null })
        try {
          const response: TokenResponse = await authApi.login(email, password)
          localStorage.setItem('token', response.access_token)
          const user: UserProfile = await authApi.getMe() as UserProfile
          set({
            user: {
              ...user,
              signup_type: user.signup_type || 'cid_user',
              account_status: user.account_status || 'active',
              access_level: user.access_level || 'standard',
              cid_enabled: user.cid_enabled ?? true,
              onboarding_completed: user.onboarding_completed ?? false,
              program: user.program || _inferProgram(user.plan),
            },
            token: response.access_token,
            isAuthenticated: true,
            sessionLoading: false,
            sessionReady: true,
          })
        } catch (err: unknown) {
          const message =
            (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
            'Error de autenticación'
          set({ loginError: message, sessionLoading: false, sessionReady: true })
          throw err
        }
      },

      logout: async () => {
        set({ sessionLoading: true })
        localStorage.removeItem('token')
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          sessionLoading: false,
          sessionReady: true,
          loginError: null,
          returnTo: null,
        })
      },

      register: async (username, email, password) => {
        set({ sessionLoading: true, loginError: null })
        try {
          await authApi.register(username, email, password)
          await get().login(email, password)
        } catch (err: unknown) {
          const message =
            (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
            'Error en el registro'
          set({ loginError: message, sessionLoading: false, sessionReady: true })
          throw err
        }
      },

      refreshProfile: async () => {
        const { token } = get()
        if (!token) return
        try {
          const user: UserProfile = await authApi.getMe() as UserProfile
          set({
            user: {
              ...user,
              signup_type: user.signup_type || 'cid_user',
              account_status: user.account_status || 'active',
              access_level: user.access_level || 'standard',
              cid_enabled: user.cid_enabled ?? true,
              onboarding_completed: user.onboarding_completed ?? false,
              program: user.program || _inferProgram(user.plan),
            },
          })
        } catch {
          // ignore
        }
      },

      completeOnboarding: () => {
        const current = get().user
        if (!current) return Promise.resolve()
        set({
          user: { ...current, onboarding_completed: true },
        })
        return Promise.resolve()
      },
    }),
    {
      name: 'ailink-auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
        returnTo: state.returnTo,
      }),
    }
  )
)

function _inferProgram(plan: string | undefined): CIDProgram {
  const p = plan?.toLowerCase()
  if (p === 'studio') return 'studio'
  if (p === 'enterprise') return 'enterprise'
  if (p === 'producer') return 'producer'
  if (p === 'creator') return 'creator'
  return 'demo'
}

export function getPrimaryCIDTarget(user: UserProfile | null): string {
  if (!user) return '/'

  if (user.signup_type === 'demo_request' || user.signup_type === 'partner_interest') {
    return '/pending-access'
  }

  if (user.account_status === 'pending') {
    return '/pending-access'
  }

  if (!user.cid_enabled) {
    return '/pending-access'
  }

  if (!user.onboarding_completed) {
    return '/onboarding'
  }

  const program = user.program || _inferProgram(user.plan)
  return `/cid/${program}`
}

export function resolvePostLoginTarget(user: UserProfile | null): string {
  if (!user) return '/'

  if (user.signup_type === 'demo_request' || user.signup_type === 'partner_interest') {
    return '/pending-access'
  }

  if (user.account_status === 'pending') {
    return '/pending-access'
  }

  if (!user.cid_enabled) {
    return '/pending-access'
  }

  if (!user.onboarding_completed) {
    return '/onboarding'
  }

  const program = user.program || _inferProgram(user.plan)
  return `/cid/${program}`
}

export function canAccessCID(user: UserProfile | null): boolean {
  if (!user) return false
  return (
    (user.signup_type === 'cid_user' || !user.signup_type) &&
    (user.account_status === 'active' || user.account_status === undefined) &&
    user.cid_enabled === true
  )
}

export function canAccessProgram(user: UserProfile | null, targetProgram: CIDProgram): boolean {
  if (!user) return false
  if (!canAccessCID(user)) return false
  const userProgram = user.program || _inferProgram(user.plan)
  const hierarchy: CIDProgram[] = ['demo', 'creator', 'producer', 'studio', 'enterprise']
  const userIdx = hierarchy.indexOf(userProgram)
  const targetIdx = hierarchy.indexOf(targetProgram)
  return userIdx >= targetIdx
}

export function canAccessDemo(user: UserProfile | null): boolean {
  if (!user) return false
  return user.signup_type === 'demo_request'
}

export function canAccessPartner(user: UserProfile | null): boolean {
  if (!user) return false
  return user.signup_type === 'partner_interest'
}

export function needsOnboarding(user: UserProfile | null): boolean {
  if (!user) return false
  return user.onboarding_completed === false
}

export function getAccessLevel(user: UserProfile | null): AccessLevel {
  if (!user) return 'none'
  if (user.access_level) return user.access_level
  if (user.signup_type === 'cid_user') return 'full'
  if (user.signup_type === 'demo_request') return 'limited'
  if (user.signup_type === 'partner_interest') return 'limited'
  return 'none'
}
