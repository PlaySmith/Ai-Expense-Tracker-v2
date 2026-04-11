import React, {
  createContext,
  useContext,
  useReducer,
  useEffect,
  useCallback,
} from 'react'
import api from '../api/API.js'

const AuthContext = createContext(null)

const initialState = {
  user: null,
  token: null,
  isAuthenticated: false,
  loading: true,
}

function authReducer(state, action) {
  switch (action.type) {
    case 'LOGIN':
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.token,
        isAuthenticated: true,
        loading: false,
      }
    case 'LOGOUT':
      return {
        ...initialState,
        loading: false,
      }
    case 'SET_READY':
      return { ...state, loading: false }
    case 'SET_USER':
      return { ...state, user: action.payload }
    default:
      return state
  }
}

export function AuthProvider({ children }) {
  const [state, dispatch] = useReducer(authReducer, initialState)

  useEffect(() => {
    let cancelled = false

    async function bootstrap() {
      const token = localStorage.getItem('token')
      if (!token) {
        dispatch({ type: 'SET_READY' })
        return
      }
      api.defaults.headers.common.Authorization = `Bearer ${token}`
      try {
        const { data } = await api.get('/auth/me')
        if (!cancelled) {
          dispatch({ type: 'LOGIN', payload: { user: data, token } })
        }
      } catch {
        localStorage.removeItem('token')
        delete api.defaults.headers.common.Authorization
        if (!cancelled) dispatch({ type: 'LOGOUT' })
      }
    }

    bootstrap()
    return () => {
      cancelled = true
    }
  }, [])

  const login = async (email, password) => {
    const response = await api.post('/auth/login', { email, password })
    const { access_token } = response.data
    localStorage.setItem('token', access_token)
    api.defaults.headers.common.Authorization = `Bearer ${access_token}`
    const { data: user } = await api.get('/auth/me')
    dispatch({ type: 'LOGIN', payload: { user, token: access_token } })
    return { success: true }
  }

  const register = async ({ full_name, email, password, phone }) => {
    const body = { full_name, email, password }
    if (phone && String(phone).trim()) {
      body.phone = String(phone).trim()
    }
    const { data } = await api.post('/auth/register', body)
    const { access_token } = data
    localStorage.setItem('token', access_token)
    api.defaults.headers.common.Authorization = `Bearer ${access_token}`
    const { data: user } = await api.get('/auth/me')
    dispatch({ type: 'LOGIN', payload: { user, token: access_token } })
    return { success: true }
  }

  const logout = () => {
    localStorage.removeItem('token')
    delete api.defaults.headers.common.Authorization
    dispatch({ type: 'LOGOUT' })
  }

  const refreshUser = useCallback(async () => {
    const token = localStorage.getItem('token')
    if (!token) return
    try {
      const { data } = await api.get('/auth/me')
      dispatch({ type: 'SET_USER', payload: data })
    } catch {
      /* keep existing user on transient errors */
    }
  }, [])

  const value = {
    ...state,
    login,
    register,
    logout,
    refreshUser,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
