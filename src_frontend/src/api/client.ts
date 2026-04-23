import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8010/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const { response, config } = error

    if (response?.status === 401 || response?.status === 403) {
      localStorage.removeItem('token')

      try {
        const { useAuthStore } = await import('@/store/auth')
        useAuthStore.getState().logout()
      } catch {
        window.location.href = '/login'
      }

      if (config?.url !== '/auth/me') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default api
