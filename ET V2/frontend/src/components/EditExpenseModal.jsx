import React, { useState, useEffect } from 'react'
import { X, Save, Trash2 } from 'lucide-react'
import { expenseAPI } from '../api/API'
import '../pages/UploadPage.css'

const EditExpenseModal = ({ expense, onClose, onUpdate, onDelete }) => {
  const [formData, setFormData] = useState({
    merchant: '',
    amount: '',
    category: '',
    date: '',
    description: ''
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)

  useEffect(() => {
    if (expense) {
      const dateStr = expense.date ? new Date(expense.date).toISOString().split('T')[0] : ''
      setFormData({
        merchant: expense.merchant || '',
        amount: expense.amount || '',
        category: expense.category || '',
        date: dateStr,
        description: expense.description || ''
      })
      setError('')
    }
  }, [expense])

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSave = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const response = await expenseAPI.updateExpense(expense.id, formData)
      if (onUpdate) onUpdate(response || { ...expense, ...formData })
      onClose()
    } catch (err) {
      console.error('Update failed:', err)
      setError(err.message || 'Failed to update expense')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async () => {
    setLoading(true)
    try {
      await expenseAPI.deleteExpense(expense.id)
      if (onDelete) onDelete(expense.id)
      onClose()
    } catch (err) {
      console.error('Delete failed:', err)
      setError(err.message || 'Failed to delete expense')
    } finally {
      setLoading(false)
    }
  }

  if (!expense) return null

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.5)',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      zIndex: 1000
    }}>
      <div style={{
        backgroundColor: '#1a1a1a',
        color: '#fff',
        borderRadius: '8px',
        padding: '24px',
        width: '90%',
        maxWidth: '500px',
        boxShadow: '0 10px 40px rgba(0,0,0,0.3)',
        border: '1px solid #333'
      }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '20px'
        }}>
          <h2 style={{ margin: 0, fontSize: '20px' }}>Edit Expense</h2>
          <button
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              color: '#fff',
              cursor: 'pointer',
              padding: '5px'
            }}
          >
            <X size={24} />
          </button>
        </div>

        {error && (
          <div style={{
            backgroundColor: '#dc2626',
            color: '#fff',
            padding: '12px',
            borderRadius: '4px',
            marginBottom: '16px'
          }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSave}>
          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'block', marginBottom: '6px', fontSize: '14px' }}>
              Merchant/Shop
            </label>
            <input
              type="text"
              name="merchant"
              value={formData.merchant}
              onChange={handleChange}
              placeholder="e.g., McDonald's"
              required
              style={{
                width: '100%',
                padding: '10px',
                borderRadius: '4px',
                border: '1px solid #444',
                backgroundColor: '#222',
                color: '#fff',
                fontSize: '14px',
                boxSizing: 'border-box'
              }}
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '16px' }}>
            <div>
              <label style={{ display: 'block', marginBottom: '6px', fontSize: '14px' }}>
                Amount (₹)
              </label>
              <input
                type="number"
                name="amount"
                value={formData.amount}
                onChange={handleChange}
                placeholder="0.00"
                step="0.01"
                min="0"
                required
                style={{
                  width: '100%',
                  padding: '10px',
                  borderRadius: '4px',
                  border: '1px solid #444',
                  backgroundColor: '#222',
                  color: '#fff',
                  fontSize: '14px',
                  boxSizing: 'border-box'
                }}
              />
            </div>

            <div>
              <label style={{ display: 'block', marginBottom: '6px', fontSize: '14px' }}>
                Date
              </label>
              <input
                type="date"
                name="date"
                value={formData.date}
                onChange={handleChange}
                style={{
                  width: '100%',
                  padding: '10px',
                  borderRadius: '4px',
                  border: '1px solid #444',
                  backgroundColor: '#222',
                  color: '#fff',
                  fontSize: '14px',
                  boxSizing: 'border-box'
                }}
              />
            </div>
          </div>

          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'block', marginBottom: '6px', fontSize: '14px' }}>
              Category
            </label>
            <select
              name="category"
              value={formData.category}
              onChange={handleChange}
              style={{
                width: '100%',
                padding: '10px',
                borderRadius: '4px',
                border: '1px solid #444',
                backgroundColor: '#222',
                color: '#fff',
                fontSize: '14px',
                boxSizing: 'border-box'
              }}
            >
              <option value="">Select Category</option>
              <option value="Food & Dining">Food & Dining</option>
              <option value="Groceries">Groceries</option>
              <option value="Fuel & Transport">Fuel & Transport</option>
              <option value="Transportation">Transportation</option>
              <option value="Shopping">Shopping</option>
              <option value="Utilities">Utilities</option>
              <option value="Health & Pharmacy">Health & Pharmacy</option>
              <option value="Education">Education</option>
              <option value="Entertainment">Entertainment</option>
              <option value="Services">Services</option>
              <option value="Household">Household</option>
              <option value="Rent">Rent</option>
              <option value="Other">Other</option>
            </select>
          </div>

          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '6px', fontSize: '14px' }}>
              Notes
            </label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleChange}
              placeholder="Add notes..."
              rows="3"
              style={{
                width: '100%',
                padding: '10px',
                borderRadius: '4px',
                border: '1px solid #444',
                backgroundColor: '#222',
                color: '#fff',
                fontSize: '14px',
                boxSizing: 'border-box',
                fontFamily: 'inherit'
              }}
            />
          </div>

          <div style={{
            display: 'flex',
            gap: '10px',
            justifyContent: 'space-between'
          }}>
            <button
              type="button"
              onClick={() => setShowDeleteConfirm(true)}
              style={{
                padding: '10px 16px',
                borderRadius: '4px',
                border: 'none',
                backgroundColor: '#dc2626',
                color: '#fff',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                fontSize: '14px'
              }}
              disabled={loading}
            >
              <Trash2 size={16} />
              Delete
            </button>

            <div style={{ display: 'flex', gap: '10px' }}>
              <button
                type="button"
                onClick={onClose}
                style={{
                  padding: '10px 16px',
                  borderRadius: '4px',
                  border: '1px solid #444',
                  backgroundColor: '#333',
                  color: '#fff',
                  cursor: 'pointer',
                  fontSize: '14px'
                }}
                disabled={loading}
              >
                Cancel
              </button>

              <button
                type="submit"
                style={{
                  padding: '10px 16px',
                  borderRadius: '4px',
                  border: 'none',
                  backgroundColor: '#22c55e',
                  color: '#000',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  fontSize: '14px',
                  fontWeight: 'bold'
                }}
                disabled={loading}
              >
                <Save size={16} />
                {loading ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          </div>
        </form>

        {showDeleteConfirm && (
          <div style={{
            marginTop: '20px',
            padding: '16px',
            backgroundColor: '#7f1d1d',
            borderRadius: '4px',
            border: '1px solid #dc2626'
          }}>
            <p style={{ margin: '0 0 12px 0' }}>
              Are you sure you want to delete this expense? This action cannot be undone.
            </p>
            <div style={{ display: 'flex', gap: '10px' }}>
              <button
                onClick={() => setShowDeleteConfirm(false)}
                style={{
                  padding: '8px 12px',
                  borderRadius: '4px',
                  border: 'none',
                  backgroundColor: '#444',
                  color: '#fff',
                  cursor: 'pointer',
                  fontSize: '14px'
                }}
                disabled={loading}
              >
                Cancel Delete
              </button>
              <button
                onClick={handleDelete}
                style={{
                  padding: '8px 12px',
                  borderRadius: '4px',
                  border: 'none',
                  backgroundColor: '#dc2626',
                  color: '#fff',
                  cursor: 'pointer',
                  fontSize: '14px',
                  fontWeight: 'bold'
                }}
                disabled={loading}
              >
                {loading ? 'Deleting...' : 'Yes, Delete'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default EditExpenseModal
