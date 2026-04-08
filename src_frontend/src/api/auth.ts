import api from './client'
import { TokenResponse, User } from '@/types'

export const authApi = {
  login: async (email: string, password: string): Promise<TokenResponse> => {
    const { data } = await api.post<TokenResponse>('/auth/login', { email, password })
    return data
  },

  register: async (username: string, email: string, password: string): Promise<User> => {
    const { data } = await api.post<User>('/auth/register', { username, email, password })
    return data
  },

  getMe: async (): Promise<User> => {
    const { data } = await api.get<User>('/auth/me')
    return data
  },
}

export const userApi = {
  getUser: async (userId: string): Promise<User> => {
    const { data } = await api.get<User>(`/users/${userId}`)
    return data
  },

  updatePlan: async (userId: string, plan: string): Promise<void> => {
    await api.patch(`/users/${userId}/plan`, null, { params: { new_plan: plan } })
  },
}
