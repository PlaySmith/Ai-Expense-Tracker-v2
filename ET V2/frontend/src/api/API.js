import axios from 'axios'

// Create axios instance with base configuration
const api = axios.create({
  baseURL: '/api',  // V2 vite proxy → backend
  timeout: 60000,  // OCR needs time
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`)
    return config
  },
  (error) => {
    console.error('API Request Error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor - Safe error handling
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`)
    return response
  },
  (error) => {
    if (error.response) {
      const { status, data } = error.response
      console.error(`API Error ${status}:`, data)
      
      const errorMessage = data?.message || data?.detail || data?.error || `Server error: ${status}`
      const errorDetails = data?.details || data?.warnings || {}
      
      const enhancedError = new Error(errorMessage)
      enhancedError.status = status
      enhancedError.code = data?.error_code || 'UNKNOWN_ERROR'
      enhancedError.details = errorDetails
      enhancedError.response = error.response || null
      
      return Promise.reject(enhancedError)
    } else if (error.request) {
      console.error('Network Error:', error.request)
      const networkError = new Error('Network error. Please check your connection.')
      networkError.code = 'NETWORK_ERROR'
      return Promise.reject(networkError)
    } else {
      console.error('Error:', error.message)
      return Promise.reject(error)
    }
  }
)

// V1-compatible API (V2 backend)
export const expenseAPI = {
  // Upload receipt (V1 signature)
  uploadReceipt: async (file, onProgress) => {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await api.post('/expenses/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          onProgress(progress)
        }
      }
    })
    
    return response.data
  },

  // Get expenses
  getExpenses: async (params = {}) => {
    const response = await api.get('/expenses', { params })
    return response.data
  },

  // Get stats
  getStats: async () => {
    const response = await api.get('/expenses/stats')
    return response.data
  },

  // Health check
  checkHealth: async () => {
    const response = await api.get('/expenses/health')
    return response.data
  }
}

export default api
