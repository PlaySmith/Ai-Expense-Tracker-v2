import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { UserPlus, Mail, Lock, User, Phone } from 'lucide-react'
import { useAuth } from '../context/AuthContext.jsx'
import './UploadPage.css'

function formatError(err) {
  const d = err?.response?.data?.detail
  if (typeof d === 'string') return d
  if (Array.isArray(d)) {
    return d.map((x) => x.msg || JSON.stringify(x)).join(' ')
  }
  return err?.message || 'Registration failed'
}

export default function RegisterPage() {
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
    try {
      await register({
        full_name: fullName.trim(),
        email,
        password,
        phone: phone.trim() || undefined,
      })
      navigate('/', { replace: true })
    } catch (err) {
      setError(formatError(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="upload-page">
      <div className="upload-container">
        <div className="upload-header">
          <UserPlus className="upload-icon" size={48} />
          <h1>Create account</h1>
        </div>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit} className="upload-form">
          <div className="form-group">
            <label htmlFor="reg-email">
              <Mail size={20} />
              Email
            </label>
            <input
              id="reg-email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="your@email.com"
              required
              className="form-input"
              autoComplete="username"
            />
          </div>

          <div className="form-group">
            <label htmlFor="reg-phone">
              <Phone size={20} />
              Phone <span className="optional-label">(optional)</span>
            </label>
            <input
              id="reg-phone"
              type="tel"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              placeholder="e.g. +91 98765 43210"
              className="form-input"
              autoComplete="tel"
            />
          </div>

          <div className="form-group">
            <label htmlFor="reg-password">
              <Lock size={20} />
              Password
            </label>
            <input
              id="reg-password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              minLength={8}
              maxLength={72}
              required
              className="form-input"
              autoComplete="new-password"
              disabled={loading}
            />
            <small
              className={`form-hint ${
                password.length > 0
                  ? password.length < 8 || password.length > 72
                    ? 'invalid'
                    : 'valid'
                  : ''
              }`}
            >
              {password.length === 0
                ? '8–72 characters'
                : password.length < 8
                  ? `${password.length}/8 min`
                  : password.length > 72
                    ? 'Too long'
                    : 'OK'}
            </small>
          </div>

          <button type="submit" className="upload-btn" disabled={loading}>
            {loading ? 'Creating account…' : 'Register'}
          </button>
        </form>

        <div className="auth-links">
          <p>
            Already registered? <Link to="/login">Login</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
