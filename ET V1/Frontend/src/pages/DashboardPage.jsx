import React, { useState, useEffect } from 'react'
import { 
  Trash2, 
  Edit2, 
  TrendingUp, 
  DollarSign, 
  Receipt, 
  AlertCircle,
  Loader2,
  RefreshCw,
  Plus
} from 'lucide-react'
import { expenseAPI } from '../api/API'
import ExpenseModal from './ExpenseModal'
import './DashboardPage.css'


function DashboardPage() {
  const [expenses, setExpenses] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [deletingId, setDeletingId] = useState(null)
  const [editModal, setEditModal] = useState({ open: false, expense: null })
  const [addModal, setAddModal] = useState(false)


  const fetchData = async () => {
    try {
      setLoading(true)
      setError(null)
      
      // Fetch expenses and stats in parallel
      const [expensesRes, statsRes] = await Promise.all([
        expenseAPI.getExpenses({ limit: 100 }),
        expenseAPI.getStats()
      ])
      
      setExpenses(expensesRes.expenses || [])
      setStats(statsRes.data)
    } catch (err) {
      console.error('Failed to fetch data:', err)
      setError(err.message || 'Failed to load expenses')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to delete this expense?')) {
      return
    }

    setDeletingId(id)
    try {
      await expenseAPI.deleteExpense(id)
      setExpenses(expenses.filter(e => e.id !== id))
    } catch (err) {
      alert('Failed to delete expense: ' + err.message)
    } finally {
      setDeletingId(null)
    }
  }

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'INR'
    }).format(amount || 0)
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  if (loading) {
    return (
      <div className="dashboard-page">
        <div className="loading-container">
          <Loader2 className="spinner-large" size={48} />
          <p>Loading your expenses...</p>
        {/* Modals */}
        <ExpenseModal
          isOpen={editModal.open}
          expense={editModal.expense}
          mode="edit"
          onClose={() => setEditModal({ open: false, expense: null })}
          onSave={async (id, data) => {
            try {
              await expenseAPI.updateExpense(id, data)
              fetchData() // Refresh list
            } catch (error) {
              alert('Update failed: ' + error.message)
            }
          }}
        />
        
        <ExpenseModal
          isOpen={addModal}
          mode="add"
          onClose={() => setAddModal(false)}
          onSave={async (data) => {
            try {
              await expenseAPI.createManualExpense(data)
              fetchData() // Refresh list
            } catch (error) {
              alert('Add failed: ' + error.message)
            }
          }}
        />
      </div>
    </div>
  )
}


  return (
    <div className="dashboard-page">
      <div className="page-header">
        <h2>Expense Dashboard</h2>
        <button 
          className="btn btn-secondary refresh-btn"
          onClick={fetchData}
          disabled={loading}
        >
          <RefreshCw size={18} className={loading ? 'spin' : ''} />
          Refresh
        </button>
      </div>

      {error && (
        <div className="alert alert-error">
          <AlertCircle size={20} />
          <span>{error}</span>
        </div>
      )}

      {/* Stats Cards */}
      {stats && (
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon total">
              <DollarSign size={24} />
            </div>
            <div className="stat-info">
              <span className="stat-label">Total Spent</span>
              <span className="stat-value">{formatCurrency(stats.total_amount)}</span>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon count">
              <Receipt size={24} />
            </div>
            <div className="stat-info">
              <span className="stat-label">Total Expenses</span>
              <span className="stat-value">{stats.total_count}</span>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon average">
              <TrendingUp size={24} />
            </div>
            <div className="stat-info">
              <span className="stat-label">Average</span>
              <span className="stat-value">{formatCurrency(stats.average_amount)}</span>
            </div>
          </div>
        </div>
      )}

      {/* Category Breakdown */}
      {stats?.categories?.length > 0 && (
        <div className="card category-card">
          <h4>Spending by Category</h4>
          <div className="category-list">
            {stats.categories.map((cat, idx) => (
              <div key={idx} className="category-item">
                <div className="category-info">
                  <span className="category-name">{cat.category}</span>
                  <span className="category-count">{cat.count} expenses</span>
                </div>
                <div className="category-bar-container">
                  <div 
                    className="category-bar" 
                    style={{ 
                      width: `${(cat.amount / stats.total_amount * 100) || 0}%` 
                    }}
                  />
                </div>
                <span className="category-amount">{formatCurrency(cat.amount)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Expenses Table */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Recent Expenses</h3>
          <div className="card-header-actions">
            <button 
              className="btn btn-primary btn-sm"
              onClick={() => setAddModal(true)}
            >
              <Plus size={16} className="mr-1" />
              Add Manual
            </button>
            <span className="expense-count">{expenses.length} total</span>
          </div>
        </div>


        {expenses.length === 0 ? (
          <div className="empty-state">
            <Receipt size={48} className="empty-icon" />
            <h4>No expenses yet</h4>
            <p>Upload your first receipt to get started</p>
          </div>
        ) : (
          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  <th>Merchant</th>
                  <th>Category</th>
                  <th>Date</th>
                  <th>Amount</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {expenses.map((expense) => (
                  <tr key={expense.id}>
                    <td>
                      <div className="merchant-cell">
                        <span className="merchant-name">
                          {expense.merchant || 'Unknown'}
                        </span>
                        {expense.ocr_confidence && expense.ocr_confidence < 70 && (
                          <span className="low-confidence-badge" title="Low OCR confidence">
                            !
                          </span>
                        )}
                      </div>
                    </td>
                    <td>
                      <span className="badge badge-success">
                        {expense.category || 'Uncategorized'}
                      </span>
                    </td>
                    <td>{formatDate(expense.date)}</td>
                    <td className="amount-cell">
                      {formatCurrency(expense.amount)}
                    </td>
                    <td>
                      <div className="action-buttons">
                        <button 
                          className="action-btn edit"
                          title="Edit expense"
                          onClick={() => setEditModal({ open: true, expense })}
                        >
                          <Edit2 size={16} />
                        </button>

                        <button 
                          className="action-btn delete"
                          title="Delete expense"
                          onClick={() => handleDelete(expense.id)}
                          disabled={deletingId === expense.id}
                        >
                          {deletingId === expense.id ? (
                            <Loader2 size={16} className="spin" />
                          ) : (
                            <Trash2 size={16} />
                          )}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}

export default DashboardPage
