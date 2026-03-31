import React, { useState, useEffect } from 'react'
import { RefreshCw, Receipt, DollarSign, TrendingUp, AlertTriangle } from 'lucide-react'
import { expenseAPI } from '../api/API.js'
import axios from 'axios'

import './DashboardPage.css'

function DashboardPage() {
  const [stats, setStats] = useState(null)
  const [expenses, setExpenses] = useState([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      const [statsRes, expensesRes] = await Promise.all([
        expenseAPI.getStats(),
        expenseAPI.getExpenses({ limit: 50 })
      ])
      setStats(statsRes)
      setExpenses(expensesRes.expenses || [])
    } catch (error) {
      console.error('Dashboard load error:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleRefresh = async () => {
    setRefreshing(true)
    await loadData()
    setRefreshing(false)
  }

  if (loading) {
    return (
      <div className="loading-container">
        <RefreshCw className="spinner-large" size={48} />
        <p>Loading dashboard...</p>
      </div>
    )
  }

  return (
    <div className="dashboard-page">
      <div className="page-header">
        <h2>Dashboard</h2>
        <button onClick={handleRefresh} disabled={refreshing} className="btn btn-secondary refresh-btn">
          <RefreshCw size={18} className={refreshing ? 'spin' : ''} />
          Refresh
        </button>
      </div>

      {/* Stats Grid */}
      {stats && (
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon total">
              <Receipt size={24} />
            </div>
            <div className="stat-info">
              <div className="stat-label">Total Receipts</div>
              <div className="stat-value">{stats.total_count || 0}</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon count">
              <DollarSign size={24} />
            </div>
            <div className="stat-info">
              <div className="stat-label">Total Spent</div>
              <div className="stat-value">₹{(stats.total_amount || 0).toLocaleString()}</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon average">
              <TrendingUp size={24} />
            </div>
            <div className="stat-info">
              <div className="stat-label">Average Receipt</div>
              <div className="stat-value">₹{stats.average_amount ? stats.average_amount.toFixed(0) : '0'}</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon review">
              <AlertTriangle size={24} />
            </div>
            <div className="stat-info">
              <div className="stat-label">Needs Review</div>
              <div className="stat-value review">{stats.review_count || 0}</div>
            </div>
          </div>
        </div>
      )}

      {/* Recent Expenses */}
      <div className="category-card">
        <div className="card-header">
          <h4>Recent Receipts</h4>
        </div>
        {expenses.length === 0 ? (
          <div className="empty-state">
            <Receipt className="empty-icon" size={64} />
            <h4>No receipts yet</h4>
            <p>Upload your first receipt to get started</p>
          </div>
        ) : (
          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  <th>Merchant</th>
                  <th>Amount</th>
                  <th>Confidence</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {expenses.slice(0, 10).map((expense) => (
                  <tr key={expense.id}>
                    <td className="merchant-cell">
                      <span className="merchant-name">{expense.merchant}</span>
                      {expense.ocr_confidence < 0.8 && (
                        <span className="low-confidence-badge" title="Low confidence">
                          !
                        </span>
                      )}
                    </td>
                    <td className="amount-cell">
                      ₹{expense.amount.toFixed(2)}
                    </td>
                    <td>
                      <div className="confidence-bar small">
                        <div 
                          className="confidence-fill" 
                          style={{ width: `${expense.ocr_confidence * 100}%` }}
                        />
                        <span>{(expense.ocr_confidence * 100).toFixed(0)}%</span>
                      </div>
                    </td>
                    <td>
                      <span className={`badge ${expense.requires_review ? 'badge-warning' : 'badge-success'}`}>
                        {expense.requires_review ? 'Review' : 'OK'}
                      </span>
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

