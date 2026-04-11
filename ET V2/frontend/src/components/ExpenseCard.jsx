import React from 'react'
import { Calendar, Tag, AlertTriangle } from 'lucide-react'

const ExpenseCard = ({ expense }) => {
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
    <div className="expense-card">
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
    </div>
  )
}

export default ExpenseCard

