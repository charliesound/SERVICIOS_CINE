type ApiErrorResponse = {
  status?: number
  data?: {
    detail?: string
    message?: string
  } | string
}

type ApiError = {
  response?: ApiErrorResponse
  message?: string
}

export function getApiErrorMessage(error: unknown, fallback: string): string {
  const apiError = error as ApiError
  const response = apiError?.response

  if (typeof response?.data === 'string') {
    const detail = response.data.trim()
    if (detail && detail !== 'Internal Server Error') {
      return detail
    }
  }

  if (response?.data && typeof response.data === 'object') {
    if (typeof response.data.detail === 'string' && response.data.detail.trim()) {
      return response.data.detail
    }
    if (typeof response.data.message === 'string' && response.data.message.trim()) {
      return response.data.message
    }
  }

  if (response?.status === 503) {
    return 'El backend no puede acceder a la base de datos en este momento.'
  }

  if (response?.status === 500) {
    return 'Error interno del backend. Revisa la configuracion del servidor y vuelve a intentarlo.'
  }

  if (typeof apiError?.message === 'string' && apiError.message.trim()) {
    return apiError.message
  }

  return fallback
}
