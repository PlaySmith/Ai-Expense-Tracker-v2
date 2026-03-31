import React, { useState, useEffect } from 'react'
import { X, Save, Upload, DollarSign, Calendar, Tag, FileText } from 'lucide-react'
import { expenseAPI } from '../api/API'

function ExpenseModal({ isOpen, onClose, expense = null, onSave, mode = 'edit' }) {
  const [formData, setFormData] = useState({
    amount: '',
    merchant: '',
    category: '',
    date: '',
    description: ''
  })
  const [loading, setLoading] = useState(false)
  const [file, setFile] = useState(null)

  useEffect(() => {
    if (expense && isOpen) {
      setFormData({
        amount: expense.amount || '',
        merchant: expense.merchant || '',
        category: expense.category || '',
        date: expense.date ? new Date(expense.date).toISOString().slice(0, 16) : '',
        description: expense.description || ''
      })
      setFile(null)
    } else if (isOpen) {
      setFormData({ amount: '', merchant: '', category: '', date: '', description: '' })
      setFile(null)
    }
  }, [expense, isOpen])

  const categories = ['Groceries', 'Dining', 'Transportation', 'Entertainment', 'Utilities', 'Healthcare', 'Other']

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!formData.amount || parseFloat(formData.amount) <= 0) {
      alert('Amount is required and must be greater than 0')
      return
    }

    setLoading(true)
    try {
      const data = {
        amount: parseFloat(formData.amount),
        merchant: formData.merchant.trim() || null,
        category: formData.category.trim() || null,
        date: formData.date ? new Date(formData.date) : null,
        description: formData.description.trim()
      }

      if (mode === 'edit') {
        await onSave(expense.id, data)
      } else {
        await onSave(data)
      }
      onClose()
    } catch (error) {
      console.error('Save failed:', error)
      alert(`Failed to save expense: ${error.message}`)
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>{mode === 'edit' ? 'Edit Expense' : 'Add Manual Expense'}</h3>
          <button className="modal-close" onClick={onClose} aria-label="Close">
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="expense-form">
          <div className="form-group">
            <label>
              <DollarSign size={18} />
              Amount *
            </label>
            <input
              type="number"
              step="0.01"
              min="0.01"
              required
              value={formData.amount}
              onChange={(e) => setFormData({...formData, amount: e.target.value})}
              placeholder="0.00"
              className="form-input"
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>
                <FileText size={18} />
                Merchant
              </label>
              <input
                type="text"
                value={formData.merchant}
                onChange={(e) => setFormData({...formData, merchant: e.target.value})}
                placeholder="Merchant name"
                className="form-input"
              />
            </div>

            <div className="form-group">
              <label>
                <Tag size={18} />
                Category
              </label>
              <select
                value={formData.category}
                onChange={(e) => setFormData({...formData, category: e.target.value})}
                className="form-input"
              >
                <option value="">Select category</option>
                {categories.map(cat => (
                  <option key={cat} value={cat}>{cat}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>
                <Calendar size={18} />
                Date
              </label>
              <input
                type="datetime-local"
                value={formData.date}
                onChange={(e) => setFormData({...formData, date: e.target.value})}
                className="form-input"
              />
            </div>
            <div className="form-group file-upload">
              <label>
                <Upload size={18} />
                Receipt (optional)
              </label>
              <input
                type="file"
                accept="image/*"
                onChange={(e) => setFile(e.target.files[0])}
                className="form-file"
              />
              {file && <span className="file-name">{file.name}</span>}
            </div>
          </div>

          <div className="form-group">
            <label>
              <FileText size={18} />
              Description
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({...formData, description: e.target.value})}
              placeholder="Additional notes..."
              rows="3"
              className="form-textarea"
            />
          </div>

          <div className="modal-actions">
            <button 
              type="button" 
              className="btn btn-secondary"
              onClick={onClose}
              disabled={loading}
            >
              Cancel
            </button>
            <button 
              type="submit" 
              className="btn btn-primary"
              disabled={loading}
            >
              {loading ? (
                <>
                  <Loader2 className="spin mr-2" size={18} />
                  Saving...
                </>
              ) : (
                <>
                  <Save size={18} className="mr-2" />
                  Save Expense
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default ExpenseModal

