import React from 'react'
import { Calendar, Tag, AlertTriangle, Edit2, Trash2 } from 'lucide-react'

const ExpenseCard = ({ expense, onEdit, onDelete }) => {
  const getConfidenceColor = (confidence) => {
    if (!confidence) return 'gray'
    if (confidence >= 0.8) return 'green'
    if (confidence >= 0.6) return 'yellow'
    return 'red'
  }

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0
    }).format(amount)
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleDateString('en-IN', {
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    })
  }

  const colorClass = getConfidenceColor(expense.ocr_confidence)

  return (
    <div className="expense-card" style={{ position: 'relative' }}>
      <div className="expense-header">
        <h4 className="merchant">{expense.merchant || 'Unknown Merchant'}</h4>
        {expense.ocr_confidence !== undefined && (
          <span className={`conf-badge conf-${colorClass}`}>
            {(expense.ocr_confidence * 100).toFixed(0)}%
          </span>
        )}
      </div>
      <div className="expense-amount">
        {formatCurrency(expense.amount)}
      </div>
      <div className="expense-meta">
        <div className="meta-item">
          <Calendar size={16} />
          <span>{formatDate(expense.date)}</span>
        </div>
        {expense.category && (
          <div className="meta-item">
            <Tag size={16} />
            <span className="category-badge">{expense.category}</span>
          </div>
        )}
        {expense.requires_review && (
          <div className="meta-item review">
            <AlertTriangle size={16} />
            <span>Review</span>
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div style={{
        display: 'flex',
        gap: '8px',
        marginTop: '12px',
        paddingTop: '12px',
        borderTop: '1px solid #333'
      }}>
        {onEdit && (
          <button
            onClick={() => onEdit(expense)}
            style={{
              flex: 1,
              padding: '8px 12px',
              borderRadius: '4px',
              border: '1px solid #444',
              backgroundColor: 'transparent',
              color: '#22c55e',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '6px',
              fontSize: '13px',
              transition: '0.2s',
            }}
            onMouseOver={(e) => e.target.style.backgroundColor = '#1f2937'}
            onMouseOut={(e) => e.target.style.backgroundColor = 'transparent'}
          >
            <Edit2 size={14} />
            Edit
          </button>
        )}
        {onDelete && (
          <button
            onClick={() => onDelete(expense.id)}
            style={{
              flex: 1,
              padding: '8px 12px',
              borderRadius: '4px',
              border: '1px solid #dc2626',
              backgroundColor: 'transparent',
              color: '#ef4444',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '6px',
              fontSize: '13px',
              transition: '0.2s',
            }}
            onMouseOver={(e) => e.target.style.backgroundColor = '#7f1d1d'}
            onMouseOut={(e) => e.target.style.backgroundColor = 'transparent'}
          >
            <Trash2 size={14} />
            Delete
          </button>
        )}
      </div>
    </div>
  )
}

export default ExpenseCard