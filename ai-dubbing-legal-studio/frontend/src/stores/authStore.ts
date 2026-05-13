import { create } from 'zustand'
import api from '../api/client'
import type { User } from '../types'

interface AuthState {
  token: string | null
  user: User | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  loadUser: () => Promise<void>
}

export const useAuthStore = create<AuthState>((set) => ({
  token: localStorage.getItem('token'),
  user: null,
  loading: false,

  login: async (email, password) => {
    const res = await api.post('/auth/login', { email, password })
    const { access_token } = res.data
    localStorage.setItem('token', access_token)
    set({ token: access_token })
    const userRes = await api.get('/auth/me')
    set({ user: userRes.data })
  },

  logout: () => {
    localStorage.removeItem('token')
    set({ token: null, user: null })
  },

  loadUser: async () => {
    try {
      const res = await api.get('/auth/me')
      set({ user: res.data })
    } catch {
      localStorage.removeItem('token')
      set({ token: null, user: null })
    }
  },
}))
