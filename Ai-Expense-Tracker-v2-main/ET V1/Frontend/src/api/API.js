import axios from 'axios'

// Create axios instance with base configuration
const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',  // Updated to match backend prefix
  timeout: 30000,
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

// Response interceptor
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`)
    return response
  },
  (error) => {
    // Handle different error types
    if (error.response) {
      // Server responded with error status
      const { status, data } = error.response
      
      console.error(`API Error ${status}:`, data)
      
      // Format error message
      const errorMessage = data?.message || data?.error || `Server error: ${status}`
      const errorDetails = data?.details || {}
      
      // Create enhanced error object
      const enhancedError = new Error(errorMessage)
      enhancedError.status = status
      enhancedError.code = data?.error_code || 'UNKNOWN_ERROR'
      enhancedError.details = errorDetails
      enhancedError.response = error.response || null
      
      return Promise.reject(enhancedError)
    } else if (error.request) {
      // Request made but no response
      console.error('Network Error:', error.request)
      const networkError = new Error('Network error. Please check your connection.')
      networkError.code = 'NETWORK_ERROR'
      networkError.response = null;
      return Promise.reject(networkError)
    } else {
      // Something else happened
      console.error('Error:', error.message)
      const otherError = new Error(error.message)
      otherError.response = null;
      return Promise.reject(otherError)
    }
  }
)

// API functions
export const expenseAPI = {
  // Manual expense
  createManualExpense: async (data) => {
    const response = await api.post('/expenses/manual', data)
    return response.data
  },

  // Upload receipt
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
  
  // Get all expenses
  getExpenses: async (params = {}) => {
    const response = await api.get('/expenses/', { params })
    return response.data
  },
  
  // Get single expense
  getExpense: async (id) => {
    const response = await api.get(`/expenses/${id}`)
    return response.data
  },
  
  // Update expense
  updateExpense: async (id, data) => {
    const response = await api.put(`/expenses/${id}`, data)
    return response.data
  },
  
  // Delete expense
  deleteExpense: async (id) => {
    const response = await api.delete(`/expenses/${id}`)
    return response.data
  },
  
  // Get statistics
  getStats: async () => {
    const response = await api.get('/expenses/stats')
    return response.data
  }
}

// Health check
export const checkHealth = async () => {
  const response = await api.get('/health')
  return response.data
}

export default api
