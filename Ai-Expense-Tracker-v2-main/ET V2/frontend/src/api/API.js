import axios from 'axios'

// Create axios instance with base configuration
const api = axios.create({
  baseURL: '/api',  // V2 vite proxy → backend
  timeout: 60000,  // OCR needs time
  headers: {
    'Content-Type': 'application/json'
  }
})

// Attach JWT on every request (avoids losing Authorization after multipart / header merges)
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  // Default instance sets Content-Type: application/json — breaks FormData (no boundary) if left on
  if (typeof FormData !== 'undefined' && config.data instanceof FormData) {
    if (config.headers?.delete) {
      config.headers.delete('Content-Type')
    } else {
      delete config.headers['Content-Type']
    }
  }
  return config
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

      let detailMsg = data?.detail
      if (Array.isArray(detailMsg)) {
        detailMsg = detailMsg.map((x) => x.msg || JSON.stringify(x)).join(' ')
      }
      const errorMessage =
        data?.message || detailMsg || data?.error || `Server error: ${status}`
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
    
    // Do not set Content-Type — browser/axios adds multipart boundary; manual type can break auth + parsing
    const response = await api.post('/expenses/upload', formData, {
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          onProgress(progress)
        }
      }
    })
    
    return response.data
  },

  // Trailing slash required: GET /expenses 307→/expenses/ drops Authorization on redirect (401)
  getExpenses: async (params = {}) => {
    const response = await api.get('/expenses/', { params })
    return response.data
  },

  // Get single expense
  getExpense: async (expenseId) => {
    const response = await api.get(`/expenses/${expenseId}`)
    return response.data
  },

  // Update expense
  updateExpense: async (expenseId, data) => {
    const response = await api.put(`/expenses/${expenseId}`, data)
    return response.data
  },

  // Delete expense
  deleteExpense: async (expenseId) => {
    const response = await api.delete(`/expenses/${expenseId}`)
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
