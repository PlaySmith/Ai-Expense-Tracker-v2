import { useState, useEffect } from 'react'
import axios from 'axios'
import './Dashboard.css'

const API_BASE = '/api/expenses'

function Dashboard() {
  const [stats, setStats] = useState({ total: 0, amount: 0 })
  const [expenses, setExpenses] = useState([])
  const [reviewItems, setReviewItems] = useState([])

  useEffect(() => {
    fetchStats()
    fetchExpenses()
  }, [])

  const fetchStats = async () => {
    try {
      const res = await axios.get(API_BASE + '/stats')
      setStats(res.data || { total_count: 0, total_amount: 0, average_amount: 0, review_count: 0 })
    } catch (err) {
      console.warn('Stats unavailable:', err)
      setStats({ total_count: 0, total_amount: 0, average_amount: 0, review_count: 0 })
    }
  }

  const fetchExpenses = async () => {
    try {
      const res = await axios.get(API_BASE)
      const data = res.data.expenses || []
      setExpenses(data.slice(0, 10))
      setReviewItems(data.filter(e => e.requires_review).slice(0, 5))
    } catch {}
  }

  return (
    <div className="dashboard">
      <div className="stats-grid">
        <div className="stat-card total">
          <h3>Total Expenses</h3>
          <div className="stat-number">{stats.total_count || 0}</div>
        </div>
        <div className="stat-card amount">
          <h3>Total Spent</h3>
          <div className="stat-number">₹{stats.total_amount?.toFixed(0) || 0}</div>
        </div>
        <div className="stat-card avg">
          <h3>Avg Amount</h3>
          <div className="stat-number">₹{(stats.average_amount || 0)?.toFixed(0)}</div>
        </div>
        <div className="stat-card review">
          <h3>Needs Review</h3>
          <div className="stat-number review">{reviewItems.length}</div>
        </div>
      </div>

      <div className="dashboard-content">
        <div className="recent-section">
          <h3>Recent Receipts</h3>
          <div className="expenses-grid">
            {expenses.map(exp => (
              <div key={exp.id} className="expense-card">
                <div className="expense-header">
                  <h4>{exp.merchant}</h4>
                  <span className={`conf-badge conf-${exp.ocr_confidence > 0.8 ? 'high' : 'low'}`}>
                    {exp.ocr_confidence ? (exp.ocr_confidence * 100).toFixed(0) + '%' : 'N/A'}
                  </span>
                </div>
                <div className="expense-amount">₹{exp.amount.toFixed(2)}</div>
                <div className="expense-meta">
                  <span>{exp.category || 'Other'}</span>
                  {exp.requires_review && <span className="review-dot">Review</span>}
                </div>
              </div>
            ))}
          </div>
        </div>

        {reviewItems.length > 0 && (
          <div className="review-section">
            <h3>⚠️ Needs Review</h3>
            <div className="review-list">
              {reviewItems.map(exp => (
                <div key={exp.id} className="review-item">
                  <span>{exp.merchant} - ₹{exp.amount}</span>
                  <button>Edit</button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default Dashboard

