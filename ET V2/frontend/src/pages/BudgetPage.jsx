import React, { useState, useEffect, useCallback } from 'react'
import { Plus, Trash2, Edit2, AlertTriangle, TrendingUp } from 'lucide-react'
import { budgetAPI } from '../api/API'
import './BudgetPage.css'

const BudgetPage = () => {
  const [budgets, setBudgets] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [showForm, setShowForm] = useState(false)
  const [editingId, setEditingId] = useState(null)

  const [formData, setFormData] = useState({
    category: '',
    budget_amount: '',
    period: 'monthly'
  })

  const categories = [
    'Food & Dining',
    'Groceries',
    'Fuel & Transport',
    'Transportation',
    'Shopping',
    'Utilities',
    'Health & Pharmacy',
    'Education',
    'Entertainment',
    'Services',
    'Household',
    'Rent',
    'Other'
  ]

  useEffect(() => {
    loadBudgets()
  }, [])

  const loadBudgets = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await budgetAPI.getBudgets()
      setBudgets(response.budgets || [])
    } catch (err) {
      console.error('Load budgets error:', err)
      setError(err.message || 'Failed to load budgets')
    } finally {
      setLoading(false)
    }
  }, [])

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!formData.category || !formData.budget_amount) {
      alert('Please fill all fields')
      return
    }

    try {
      if (editingId) {
        await budgetAPI.updateBudget(editingId, {
          budget_amount: parseFloat(formData.budget_amount),
          period: formData.period
        })
      } else {
        await budgetAPI.createBudget({
          category: formData.category,
          budget_amount: parseFloat(formData.budget_amount),
          period: formData.period
        })
      }
      
      resetForm()
      await loadBudgets()
    } catch (err) {
      alert('Error: ' + err.message)
    }
  }

  const handleEdit = (budget) => {
    setFormData({
      category: budget.category,
      budget_amount: budget.budget_amount,
      period: budget.period
    })
    setEditingId(budget.id)
    setShowForm(true)
  }

  const handleDelete = async (budgetId) => {
    if (confirm('Delete this budget?')) {
      try {
        await budgetAPI.deleteBudget(budgetId)
        await loadBudgets()
      } catch (err) {
        alert('Error: ' + err.message)
      }
    }
  }

  const resetForm = () => {
    setFormData({ category: '', budget_amount: '', period: 'monthly' })
    setEditingId(null)
    setShowForm(false)
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'safe':
        return '#10b981' // Green
      case 'warning':
        return '#f59e0b' // Orange
      case 'critical':
        return '#ef4444' // Red
      case 'exceeded':
        return '#dc2626' // Dark Red
      default:
        return '#6b7280'
    }
  }

  const getStatusLabel = (status) => {
    switch (status) {
      case 'safe':
        return 'Safe'
      case 'warning':
        return 'Warning'
      case 'critical':
        return 'Critical'
      case 'exceeded':
        return 'Exceeded'
      default:
        return 'Unknown'
    }
  }

  if (loading) {
    return <div className="budget-page"><div style={{ padding: '40px', textAlign: 'center' }}>Loading budgets...</div></div>
  }

  return (
    <div className="budget-page">
      <div className="page-header">
        <h2>Budget Management</h2>
        <button
          onClick={() => setShowForm(!showForm)}
          className="btn btn-primary"
          style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
        >
          <Plus size={18} />
          Add Budget
        </button>
      </div>

      {error && (
        <div className="alert alert-error" style={{ margin: '20px 0' }}>
          {error}
        </div>
      )}

      {/* Add/Edit Form */}
      {showForm && (
        <div style={{
          backgroundColor: '#1a1a1a',
          border: '1px solid #333',
          borderRadius: '8px',
          padding: '20px',
          marginBottom: '24px'
        }}>
          <h3 style={{ marginTop: 0, marginBottom: '16px' }}>
            {editingId ? 'Edit Budget' : 'Create New Budget'}
          </h3>

          <form onSubmit={handleSubmit} style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '16px'
          }}>
            {/* Category */}
            <div>
              <label style={{ display: 'block', marginBottom: '6px', fontSize: '14px' }}>
                Category
              </label>
              <select
                name="category"
                value={formData.category}
                onChange={handleChange}
                disabled={editingId !== null}
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
                {categories.map(cat => (
                  <option key={cat} value={cat}>{cat}</option>
                ))}
              </select>
            </div>

            {/* Budget Amount */}
            <div>
              <label style={{ display: 'block', marginBottom: '6px', fontSize: '14px' }}>
                Budget Amount (₹)
              </label>
              <input
                type="number"
                name="budget_amount"
                value={formData.budget_amount}
                onChange={handleChange}
                placeholder="5000.00"
                step="100"
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

            {/* Period */}
            <div>
              <label style={{ display: 'block', marginBottom: '6px', fontSize: '14px' }}>
                Period
              </label>
              <select
                name="period"
                value={formData.period}
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
                <option value="monthly">Monthly</option>
                <option value="yearly">Yearly</option>
              </select>
            </div>

            {/* Buttons */}
            <div style={{ display: 'flex', gap: '8px', alignItems: 'flex-end' }}>
              <button
                type="submit"
                style={{
                  flex: 1,
                  padding: '10px',
                  backgroundColor: '#22c55e',
                  color: '#000',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  fontWeight: '600'
                }}
              >
                {editingId ? 'Update' : 'Create'}
              </button>
              <button
                type="button"
                onClick={resetForm}
                style={{
                  flex: 1,
                  padding: '10px',
                  backgroundColor: '#444',
                  color: '#fff',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer'
                }}
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Summary Stats */}
      {budgets.length > 0 && (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '16px',
          marginBottom: '24px'
        }}>
          <div style={{
            backgroundColor: '#1a1a1a',
            border: '1px solid #333',
            borderRadius: '8px',
            padding: '16px'
          }}>
            <p style={{ margin: '0 0 8px 0', color: '#aaa', fontSize: '12px' }}>Total Budget</p>
            <p style={{ margin: 0, fontSize: '24px', fontWeight: 'bold', color: '#22c55e' }}>
              ₹{budgets.reduce((sum, b) => sum + b.budget_amount, 0).toLocaleString()}
            </p>
          </div>

          <div style={{
            backgroundColor: '#1a1a1a',
            border: '1px solid #333',
            borderRadius: '8px',
            padding: '16px'
          }}>
            <p style={{ margin: '0 0 8px 0', color: '#aaa', fontSize: '12px' }}>Total Spent</p>
            <p style={{ margin: 0, fontSize: '24px', fontWeight: 'bold', color: '#f59e0b' }}>
              ₹{budgets.reduce((sum, b) => sum + b.spent_amount, 0).toLocaleString()}
            </p>
          </div>

          <div style={{
            backgroundColor: '#1a1a1a',
            border: '1px solid #333',
            borderRadius: '8px',
            padding: '16px'
          }}>
            <p style={{ margin: '0 0 8px 0', color: '#aaa', fontSize: '12px' }}>Remaining</p>
            {(() => {
              const totalBudget = budgets.reduce((sum, b) => sum + b.budget_amount, 0)
              const totalSpent = budgets.reduce((sum, b) => sum + b.spent_amount, 0)
              const totalRemaining = totalBudget - totalSpent
              const textColor = totalRemaining < 0 ? '#ef4444' : '#10b981'
              return (
                <p style={{ margin: 0, fontSize: '24px', fontWeight: 'bold', color: textColor }}>
                  {totalRemaining < 0 ? '- ' : ''}₹{Math.abs(totalRemaining).toLocaleString()}
                </p>
              )
            })()}
          </div>
        </div>
      )}

      {/* Budgets List */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))',
        gap: '16px'
      }}>
        {budgets.length === 0 ? (
          <div style={{
            gridColumn: '1 / -1',
            textAlign: 'center',
            padding: '40px',
            color: '#666'
          }}>
            <TrendingUp size={48} style={{ opacity: 0.3, marginBottom: '16px' }} />
            <p>No budgets yet. Create your first budget!</p>
          </div>
        ) : (
          budgets.map(budget => (
            <div
              key={budget.id}
              style={{
                backgroundColor: '#1a1a1a',
                border: '1px solid #333',
                borderRadius: '8px',
                padding: '16px'
              }}
            >
              {/* Header */}
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'start',
                marginBottom: '12px'
              }}>
                <div>
                  <h3 style={{ margin: '0 0 4px 0', fontSize: '16px' }}>
                    {budget.category}
                  </h3>
                  <p style={{ margin: 0, fontSize: '12px', color: '#aaa' }}>
                    {budget.period === 'monthly' ? 'Monthly' : 'Yearly'}
                  </p>
                </div>
                <div style={{
                  display: 'flex',
                  gap: '8px'
                }}>
                  <button
                    onClick={() => handleEdit(budget)}
                    style={{
                      background: 'none',
                      border: 'none',
                      color: '#22c55e',
                      cursor: 'pointer',
                      padding: '4px'
                    }}
                  >
                    <Edit2 size={16} />
                  </button>
                  <button
                    onClick={() => handleDelete(budget.id)}
                    style={{
                      background: 'none',
                      border: 'none',
                      color: '#ef4444',
                      cursor: 'pointer',
                      padding: '4px'
                    }}
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>

              {/* Amount Info */}
              <div style={{ marginBottom: '12px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                  <span style={{ fontSize: '14px', color: '#aaa' }}>Spent</span>
                  <span style={{ fontSize: '14px', fontWeight: '600' }}>
                    ₹{budget.spent_amount.toLocaleString()}
                  </span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                  <span style={{ fontSize: '14px', color: '#aaa' }}>Budget</span>
                  <span style={{ fontSize: '14px', fontWeight: '600' }}>
                    ₹{budget.budget_amount.toLocaleString()}
                  </span>
                </div>
              </div>

              {/* Progress Bar */}
              <div style={{
                backgroundColor: '#222',
                borderRadius: '4px',
                height: '24px',
                overflow: 'hidden',
                marginBottom: '12px'
              }}>
                <div
                  style={{
                    height: '100%',
                    width: `${Math.min(budget.percentage, 100)}%`,
                    backgroundColor: getStatusColor(budget.status),
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: '#000',
                    fontSize: '12px',
                    fontWeight: 'bold',
                    transition: 'width 0.3s'
                  }}
                >
                  {budget.percentage > 10 ? `${budget.percentage.toFixed(0)}%` : ''}
                </div>
              </div>

              {/* Status */}
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                padding: '8px',
                backgroundColor: getStatusColor(budget.status) + '20',
                borderLeft: `3px solid ${getStatusColor(budget.status)}`,
                borderRadius: '4px'
              }}>
                {budget.status === 'exceeded' ? (
                  <AlertTriangle size={16} style={{ color: getStatusColor(budget.status) }} />
                ) : budget.status === 'critical' ? (
                  <AlertTriangle size={16} style={{ color: getStatusColor(budget.status) }} />
                ) : null}
                <span style={{ fontSize: '13px', color: getStatusColor(budget.status) }}>
                  {getStatusLabel(budget.status)}
                  {budget.remaining_amount < 0
                    ? ` - ₹${Math.abs(budget.remaining_amount).toLocaleString()} over`
                    : ` - ₹${budget.remaining_amount.toLocaleString()} remaining`}
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default BudgetPage
