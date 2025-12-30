import axios, { AxiosError, AxiosInstance, AxiosResponse } from 'axios'

/**
 * Standard API response format from Flourisha backend
 */
export interface APIResponse<T> {
  success: boolean
  data: T | null
  error: string | null
  meta: {
    request_id: string
    duration_ms: number
    timestamp: string
  }
}

/**
 * Create configured axios instance for API calls
 */
function createApiClient(): AxiosInstance {
  const instance = axios.create({
    baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://100.66.28.67:8001/api',
    timeout: 30000,
    headers: {
      'Content-Type': 'application/json',
    },
  })

  // Request interceptor for auth
  instance.interceptors.request.use(
    (config) => {
      // Get token from localStorage if available
      if (typeof window !== 'undefined') {
        const token = localStorage.getItem('auth_token')
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
      }
      return config
    },
    (error) => Promise.reject(error)
  )

  // Response interceptor for error handling
  instance.interceptors.response.use(
    (response: AxiosResponse) => response,
    (error: AxiosError<APIResponse<unknown>>) => {
      // Handle specific error codes
      if (error.response?.status === 401) {
        // Clear auth and redirect to login
        if (typeof window !== 'undefined') {
          localStorage.removeItem('auth_token')
          window.location.href = '/login'
        }
      }

      // Extract error message from response
      const message =
        error.response?.data?.error ||
        error.message ||
        'An unexpected error occurred'

      return Promise.reject(new Error(message))
    }
  )

  return instance
}

export const api = createApiClient()

/**
 * Type-safe API request helper
 */
export async function apiRequest<T>(
  method: 'GET' | 'POST' | 'PUT' | 'DELETE',
  url: string,
  data?: unknown
): Promise<T> {
  const response = await api.request<APIResponse<T>>({
    method,
    url,
    data,
  })

  if (!response.data.success) {
    throw new Error(response.data.error || 'Request failed')
  }

  return response.data.data as T
}

/**
 * Common API endpoints
 */
export const endpoints = {
  // Auth
  auth: {
    login: '/auth/login',
    logout: '/auth/logout',
    me: '/auth/me',
  },
  // Search
  search: '/search',
  // Knowledge
  graph: {
    query: '/graph/query',
  },
  para: {
    browse: '/para/browse',
  },
  // Productivity
  okrs: {
    list: '/okrs',
    measure: '/okrs/measure',
  },
  energy: {
    log: '/energy',
    history: '/energy/history',
  },
  reports: {
    morning: '/reports/morning',
  },
  // Content
  youtube: {
    playlists: '/youtube/playlists',
  },
  documents: {
    upload: '/documents/upload',
  },
  skills: {
    list: '/skills',
  },
  // System
  health: {
    dashboard: '/health/dashboard',
  },
  integrations: '/integrations',
}
