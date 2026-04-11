import React, { useState } from 'react'
import { useAuth } from '../context/AuthContext.jsx'
import { Link, useNavigate } from 'react-router-dom'
import { UserPlus, Mail, Lock } from 'lucide-react'
import '../pages/UploadPage.css' // Reuse styling

function RegisterPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const { register } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    const result = await register(email, password)
    
    if (result.success) {
      navigate('/')
    } else {
      setError(result.error || 'Registration failed')
    }
    
    setLoading(false)
  }

  return (
    <div className="upload-page">
      <div className="upload-container">
        <div className="upload-header">
          <UserPlus className="upload-icon" size={48} />
          <h1>Create Account</h1>
          <p>Join SmartSpend AI for automatic expense tracking</p>
        </div>

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="upload-form">
          <div className="form-group">
            <label htmlFor="email">
              <Mail size={20} />
              Email
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="your@email.com"
              required
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">
              <Lock size={20} />
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              minLength={8}
              maxLength={72}
              required
              className="form-input"
              disabled={loading}
            />
            <small className={`form-hint ${password.length > 0 ? (password.length < 8 || password.length > 72 ? 'invalid' : 'valid') : ''}`}>
              {password.length === 0 ? '8-72 characters required' : 
               password.length < 8 ? `Too short (${password.length}/8)` :
               password.length > 72 ? `Too long (${password.length}/72)` :
               `Valid (${password.length} chars)`}
            </small>
          </div>

          <button type="submit" className="upload-btn" disabled={loading}>
            {loading ? 'Creating account...' : 'Sign Up'}
          </button>
        </form>

        <div className="auth-links">
          <p>Already have an account? <Link to="/login">Login</Link></p>
        </div>
      </div>
    </div>
  )
}

export default RegisterPage
