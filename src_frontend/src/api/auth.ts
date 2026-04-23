import api from './client'
import type {
  TokenResponse,
  User,
  UserProfile,
  RegisterCIDPayload,
  RegisterDemoPayload,
  RegisterPartnerPayload,
} from '@/types'

export const authApi = {
  login: async (email: string, password: string): Promise<TokenResponse> => {
    const { data } = await api.post<TokenResponse>('/auth/login', { email, password })
    return data
  },

  register: async (username: string, email: string, password: string): Promise<User> => {
    const { data } = await api.post<User>('/auth/register', { username, email, password })
    return data
  },

  registerCID: async (payload: RegisterCIDPayload): Promise<UserProfile> => {
    const { data } = await api.post<UserProfile>('/auth/register/cid', payload)
    return data
  },

  registerDemo: async (payload: RegisterDemoPayload): Promise<UserProfile> => {
    const { data } = await api.post<UserProfile>('/auth/register/demo', payload)
    return data
  },

  registerDemoWithPassword: async (payload: RegisterDemoPayload): Promise<UserProfile> => {
    const { data } = await api.post<UserProfile>('/auth/register/demo', payload)
    return data
  },

  registerPartner: async (payload: RegisterPartnerPayload): Promise<UserProfile> => {
    const { data } = await api.post<UserProfile>('/auth/register/partner', payload)
    return data
  },

  registerPartnerWithPassword: async (payload: RegisterPartnerPayload): Promise<UserProfile> => {
    const { data } = await api.post<UserProfile>('/auth/register/partner', payload)
    return data
  },

  getMe: async (): Promise<UserProfile> => {
    const { data } = await api.get<UserProfile>('/auth/me')
    return data
  },
}

export const userApi = {
  getUser: async (userId: string): Promise<User> => {
    const { data } = await api.get<User>(`/users/${userId}`)
    return data
  },

  updatePlan: async (_userId: string, plan: string): Promise<{
    message: string
    previous_plan: string
    current_plan: string
    activation_mode: string
    effective_immediately: boolean
  }> => {
    void _userId
    const { data } = await api.post('/plans/change', { target_plan: plan })
    return data
  },
}
