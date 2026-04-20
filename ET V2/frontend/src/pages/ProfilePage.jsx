import React, { useEffect, useState } from 'react'
import { Edit2, Save, X } from 'lucide-react'
import { useAuth } from '../context/AuthContext.jsx'
import { authAPI } from '../api/API.js'
import './UploadPage.css'
import './ProfilePage.css'

export default function ProfilePage({ onBack }) {
  const { user, refreshUser } = useAuth()
  const [isEditing, setIsEditing] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const [formData, setFormData] = useState({
    full_name: '',
    phone: ''
  })

  useEffect(() => {
    refreshUser?.()
  }, [refreshUser])

  // Initialize form data when user data is available
  useEffect(() => {
    if (user) {
      setFormData({
        full_name: user.full_name?.trim() || '',
        phone: user.phone?.trim() || ''
      })
    }
  }, [user])

  const name = user?.full_name?.trim() || '—'
  const email = user?.email || '—'
  const phone = user?.phone && String(user.phone).trim() ? user.phone.trim() : '—'

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSave = async () => {
    setIsSaving(true)
    setError('')
    setSuccess('')

    try {
      await authAPI.updateProfile({
        full_name: formData.full_name.trim() || null,
        phone: formData.phone.trim() || null
      })
      await refreshUser?.()
      setIsEditing(false)
      setSuccess('Profile updated successfully!')
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
      setError(err.message || 'Failed to update profile')
    } finally {
      setIsSaving(false)
    }
  }

  const handleCancel = () => {
    setFormData({
      full_name: user?.full_name?.trim() || '',
      phone: user?.phone?.trim() || ''
    })
    setIsEditing(false)
    setError('')
  }

  return (
    <div className="upload-page">
      <div className="upload-container profile-container">
        <div className="upload-header">
          <h1>Profile</h1>
        </div>

        {error && (
          <div className="alert alert-error">
            {error}
          </div>
        )}

        {success && (
          <div className="alert alert-success">
            {success}
          </div>
        )}

        {/* Profile Fields */}
        <div className="profile-fields">
          {!isEditing ? (
            <>
              <div className="form-group profile-field">
                <label>Name</label>
                <p className="profile-value">{name}</p>
              </div>
              <div className="form-group profile-field">
                <label>Email</label>
                <p className="profile-value">{email}</p>
              </div>
              <div className="form-group profile-field">
                <label>Phone</label>
                <p className="profile-value">{phone}</p>
              </div>

              <div className="profile-actions">
                <button
                  type="button"
                  className="profile-edit-btn"
                  onClick={() => setIsEditing(true)}
                >
                  <Edit2 size={18} />
                  Edit Profile
                </button>
              </div>
            </>
          ) : (
            <>
              <div className="form-group">
                <label htmlFor="full_name">Name</label>
                <input
                  id="full_name"
                  type="text"
                  name="full_name"
                  value={formData.full_name}
                  onChange={handleInputChange}
                  className="form-input"
                  placeholder="Enter your full name"
                />
              </div>

              <div className="form-group">
                <label htmlFor="phone">Phone</label>
                <input
                  id="phone"
                  type="tel"
                  name="phone"
                  value={formData.phone}
                  onChange={handleInputChange}
                  className="form-input"
                  placeholder="Enter your phone number"
                />
              </div>

              <div className="form-group profile-field">
                <label>Email</label>
                <p className="profile-value" style={{ color: '#999' }}>
                  {email} <span style={{ fontSize: '12px' }}>(Cannot change)</span>
                </p>
              </div>

              <div className="profile-edit-actions">
                <button
                  type="button"
                  className="profile-save-btn"
                  onClick={handleSave}
                  disabled={isSaving}
                >
                  <Save size={18} />
                  {isSaving ? 'Saving...' : 'Save Changes'}
                </button>
                <button
                  type="button"
                  className="profile-cancel-btn"
                  onClick={handleCancel}
                  disabled={isSaving}
                >
                  <X size={18} />
                  Cancel
                </button>
              </div>
            </>
          )}
        </div>

        {onBack && (
          <button type="button" className="upload-btn profile-back" onClick={onBack}>
            Back to app
          </button>
        )}
      </div>
    </div>
  )
}
