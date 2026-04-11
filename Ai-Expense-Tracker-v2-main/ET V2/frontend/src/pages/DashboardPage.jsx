import React, { useState, useEffect, useCallback } from 'react'
import { RefreshCw, Receipt, DollarSign, TrendingUp, BarChart3, AlertTriangle, AlertCircle } from 'lucide-react'
import { expenseAPI } from '../api/API'
import SummaryCard from '../components/SummaryCard'
import ExpenseCard from '../components/ExpenseCard'
import CategoryPie from '../components/CategoryPie'
import './DashboardPage.css'

function DashboardPage({ refreshKey = 0 }) {
  const [stats, setStats] = useState(null)
  const [expenses, setExpenses] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [refreshing, setRefreshing] = useState(false)

  const computePieData = (expenses) => {
    const categoryTotals = {}
    expenses.forEach(exp => {
      const cat = exp.category || 'Uncategorized'
      categoryTotals[cat] = (categoryTotals[cat] || 0) + exp.amount
    })
    return Object.entries(categoryTotals).map(([name, value]) => ({ name, value }))
  }

  const computeSummary = (expenses, stats) => {
    if (!expenses.length) return {}
    const totalTxns = expenses.length
    const highest = Math.max(...expenses.map(e => e.amount))
    const categoryCounts = {}
    expenses.forEach(exp => {
      const cat = exp.category || 'Uncategorized'
      categoryCounts[cat] = (categoryCounts[cat] || 0) + 1
    })
    const mostUsed = Object.entries(categoryCounts).reduce((a, b) => (b[1] > a[1] ? b : a), ['', 0])[0]
    return { totalTxns, highestExpense: highest.toFixed(0), mostUsedCategory: mostUsed }
  }

  useEffect(() => {
    loadData()
  }, [refreshKey])

  const loadData = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const [statsRes, expensesRes] = await Promise.all([
        expenseAPI.getStats(),
        expenseAPI.getExpenses({ limit: 50 }),
      ])
      const sortedExpenses = (expensesRes.expenses || []).sort((a, b) => {
        const ta = a.date ? new Date(a.date).getTime() : 0
        const tb = b.date ? new Date(b.date).getTime() : 0
        return tb - ta
      })
      setStats(statsRes)
      setExpenses(sortedExpenses)
    } catch (err) {
      console.error('Dashboard load error:', err)
      setError(err.message || 'Failed to load data')
    } finally {
      setLoading(false)
    }
  }, [])

  const handleRefresh = async () => {
    setRefreshing(true)
    await loadData()
    setRefreshing(false)
  }

  if (error) {
    return (
      <div className="dashboard-page">
        <div className="page-header">
          <h2>Dashboard</h2>
          <button onClick={handleRefresh} className="btn btn-secondary refresh-btn">
            <RefreshCw size={18} />
            Try Again
          </button>
        </div>
        <div className="alert alert-error" style={{maxWidth: '500px', margin: '0 auto'}}>
          <AlertCircle size={24} />
          <span>{error}</span>
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="dashboard-page">
        <div className="page-header">
          <h2>Dashboard</h2>
          <div>Loading...</div>
        </div>
        <div className="skeleton-stats">
          <div className="skeleton skeleton-card"></div>
          <div className="skeleton skeleton-card"></div>
          <div className="skeleton skeleton-card"></div>
          <div className="skeleton skeleton-card"></div>
        </div>
        <div className="skeleton-expenses">
          <div className="skeleton skeleton-expense"></div>
          <div className="skeleton skeleton-expense"></div>
          <div className="skeleton skeleton-expense"></div>
        </div>
      </div>
    )
  }

  const pieData = computePieData(expenses)
  const summary = computeSummary(expenses, stats)

  return (
    <div className="dashboard-container">
      <div className="page-header">
        <h2>Dashboard</h2>
      </div>

      {/* Summary Cards */}
      <div className="stats-grid">
        <SummaryCard 
          icon={Receipt} 
          label="Total Transactions" 
          value={summary.totalTxns || stats?.total_count || 0} 
          color="blue" 
        />
        <SummaryCard 
          icon={DollarSign} 
          label="Total Spent" 
          value={`₹${(stats?.total_amount || 0).toLocaleString()}`} 
          color="green" 
        />
        <SummaryCard 
          icon={TrendingUp} 
          label="Highest Expense" 
          value={`₹${summary.highestExpense || 0}`} 
          color="orange" 
        />
        <SummaryCard 
          icon={BarChart3} 
          label="Top Category" 
          value={summary.mostUsedCategory || 'N/A'} 
          color="purple" 
        />
      </div>

      {/* Main Grid: Pie + Expenses */}
      <div className="main-grid">
        {/* Category Pie Chart */}
        <CategoryPie data={pieData} />

        {/* Recent Expenses */}
        <div className="expenses-section">
          <h4>Recent Expenses ({expenses.length})</h4>
          {expenses.length === 0 ? (
            <div className="empty-state">
              <Receipt className="empty-icon" size={64} />
              <h4>No expenses yet</h4>
              <p>Upload your first receipt using the Upload tab to get started</p>
            </div>
          ) : (
            <div className="expenses-grid">
              {expenses.slice(0, 10).map((expense) => (
                <ExpenseCard key={expense.id} expense={expense} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )

}

export default DashboardPage

