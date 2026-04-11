import React, { useEffect } from 'react'
import { User } from 'lucide-react'
import { useAuth } from '../context/AuthContext.jsx'
import './UploadPage.css'

export default function ProfilePage({ onBack }) {
  const { user, refreshUser } = useAuth()

  useEffect(() => {
    refreshUser?.()
  }, [refreshUser])

  const name = user?.full_name?.trim() || '—'
  const email = user?.email || '—'
  const phone =
    user?.phone && String(user.phone).trim() ? user.phone.trim() : '—'

  return (
    <div className="upload-page">
      <div className="upload-container profile-container">
        <div className="upload-header">
          <User className="upload-icon" size={48} />
          <h1>Profile</h1>
        </div>

        <div className="profile-fields">
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
