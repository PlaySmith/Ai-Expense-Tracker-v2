import React, { useState, useEffect, useCallback, useMemo } from 'react'
import { RefreshCw, Receipt, DollarSign, TrendingUp, BarChart3, AlertTriangle, AlertCircle, Download, X } from 'lucide-react'
import { expenseAPI } from '../api/API'
import SummaryCard from '../components/SummaryCard'
import ExpenseCard from '../components/ExpenseCard'
import CategoryPie from '../components/CategoryPie'
import EditExpenseModal from '../components/EditExpenseModal'
import './DashboardPage.css'

function DashboardPage({ refreshKey = 0 }) {
  const [stats, setStats] = useState(null)
  const [expenses, setExpenses] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [refreshing, setRefreshing] = useState(false)
  const [selectedExpense, setSelectedExpense] = useState(null)
  const [showEditModal, setShowEditModal] = useState(false)
  
  // Filter states
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('')
  const [searchMerchant, setSearchMerchant] = useState('')

  // Get all unique categories from expenses
  const categories = useMemo(() => {
    const cats = new Set(expenses.map(e => e.category).filter(c => c))
    return Array.from(cats).sort()
  }, [expenses])

  // Apply filters to expenses
  const filteredExpenses = useMemo(() => {
    return expenses.filter(exp => {
      // Date filter
      if (dateFrom) {
        const expDate = new Date(exp.date)
        const fromDate = new Date(dateFrom)
        if (expDate < fromDate) return false
      }
      if (dateTo) {
        const expDate = new Date(exp.date)
        const toDate = new Date(dateTo)
        toDate.setHours(23, 59, 59, 999) // Include entire day
        if (expDate > toDate) return false
      }

      // Category filter
      if (selectedCategory && exp.category !== selectedCategory) return false

      // Merchant search (case-insensitive)
      if (searchMerchant) {
        if (!exp.merchant.toLowerCase().includes(searchMerchant.toLowerCase())) {
          return false
        }
      }

      return true
    })
  }, [expenses, dateFrom, dateTo, selectedCategory, searchMerchant])

  // Export to CSV
  const exportToCSV = () => {
    if (filteredExpenses.length === 0) {
      alert('No expenses to export')
      return
    }

    const headers = ['ID', 'Date', 'Merchant', 'Amount', 'Category', 'Description']
    const rows = filteredExpenses.map(exp => [
      exp.id,
      exp.date ? new Date(exp.date).toLocaleDateString() : '',
      exp.merchant,
      exp.amount,
      exp.category || 'Uncategorized',
      exp.description || ''
    ])

    const csv = [
      headers.join(','),
      ...rows.map(row => 
        row.map(cell => 
          // Escape quotes and wrap in quotes if contains comma
          typeof cell === 'string' && cell.includes(',') 
            ? `"${cell.replace(/"/g, '""')}"` 
            : cell
        ).join(',')
      )
    ].join('\n')

    const blob = new Blob([csv], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `expenses_${new Date().toISOString().split('T')[0]}.csv`
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
  }

  // Export to PDF
  const exportToPDF = () => {
    if (filteredExpenses.length === 0) {
      alert('No expenses to export')
      return
    }

    // Generate HTML table
    const totalAmount = filteredExpenses.reduce((sum, exp) => sum + exp.amount, 0)
    const today = new Date().toLocaleDateString()
    
    const html = `
      <!DOCTYPE html>
      <html>
      <head>
        <style>
          body { font-family: Arial, sans-serif; margin: 20px; color: #333; }
          h1 { text-align: center; color: #22c55e; margin-bottom: 10px; }
          .info { text-align: center; color: #666; margin-bottom: 20px; font-size: 12px; }
          table { width: 100%; border-collapse: collapse; margin-top: 20px; }
          th { background-color: #22c55e; color: white; padding: 12px; text-align: left; font-weight: bold; }
          td { padding: 10px; border-bottom: 1px solid #ddd; }
          tr:nth-child(even) { background-color: #f9f9f9; }
          .amount { text-align: right; font-weight: bold; }
          .total-row { background-color: #f0f0f0; font-weight: bold; }
          .total-row td { padding: 12px 10px; border-top: 2px solid #22c55e; }
          .confidence { text-align: center; }
          .review { text-align: center; }
        </style>
      </head>
      <body>
        <h1>Expense Report</h1>
        <div class="info">
          Generated on ${today} • Total Expenses: ${filteredExpenses.length} • Total Amount: ₹${totalAmount.toLocaleString('en-IN', { maximumFractionDigits: 2 })}
        </div>
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Date</th>
              <th>Merchant</th>
              <th class="amount">Amount</th>
              <th>Category</th>
              <th>Description</th>
            </tr>
          </thead>
          <tbody>
            ${filteredExpenses.map(exp => `
              <tr>
                <td>${exp.id}</td>
                <td>${exp.date ? new Date(exp.date).toLocaleDateString() : '-'}</td>
                <td>${exp.merchant}</td>
                <td class="amount">₹${exp.amount.toLocaleString('en-IN', { maximumFractionDigits: 2 })}</td>
                <td>${exp.category || 'Uncategorized'}</td>
                <td>${exp.description || '-'}</td>
              </tr>
            `).join('')}
            <tr class="total-row">
              <td colspan="3">TOTAL</td>
              <td class="amount">₹${totalAmount.toLocaleString('en-IN', { maximumFractionDigits: 2 })}</td>
              <td colspan="2"></td>
            </tr>
          </tbody>
        </table>
      </body>
      </html>
    `

    // Open print dialog
    const printWindow = window.open('', '', 'width=900,height=600')
    printWindow.document.write(html)
    printWindow.document.close()
    
    // Trigger print dialog
    setTimeout(() => {
      printWindow.print()
      printWindow.close()
    }, 250)
  }

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

  const handleEditClick = (expense) => {
    setSelectedExpense(expense)
    setShowEditModal(true)
  }

  const handleDeleteClick = async (expenseId) => {
    if (confirm('Are you sure you want to delete this expense?')) {
      try {
        await expenseAPI.deleteExpense(expenseId)
        setExpenses(expenses.filter(e => e.id !== expenseId))
        setShowEditModal(false)
      } catch (err) {
        alert('Failed to delete expense: ' + err.message)
      }
    }
  }

  const handleExpenseUpdated = (updatedExpense) => {
    setExpenses(expenses.map(e => e.id === updatedExpense.id ? updatedExpense : e))
    setShowEditModal(false)
    setSelectedExpense(null)
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

  const pieData = computePieData(filteredExpenses)
  const summary = computeSummary(filteredExpenses, stats)

  return (
    <div className="dashboard-container">
      <div className="page-header">
        <h2>Dashboard</h2>
      </div>

      {/* Filters Section */}
      <div style={{
        backgroundColor: '#1a1a1a',
        border: '1px solid #333',
        borderRadius: '8px',
        padding: '16px',
        marginBottom: '24px'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: '16px'
        }}>
          <h3 style={{ margin: 0, fontSize: '16px', fontWeight: '600' }}>Filters & Export</h3>
          {(dateFrom || dateTo || selectedCategory || searchMerchant) && (
            <button
              onClick={() => {
                setDateFrom('')
                setDateTo('')
                setSelectedCategory('')
                setSearchMerchant('')
              }}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                padding: '6px 12px',
                backgroundColor: '#444',
                border: 'none',
                color: '#fff',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '13px'
              }}
            >
              <X size={14} />
              Clear Filters
            </button>
          )}
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '12px',
          marginBottom: '12px'
        }}>
          {/* Date From */}
          <div>
            <label style={{ display: 'block', marginBottom: '6px', fontSize: '13px', color: '#aaa' }}>From Date</label>
            <input
              type="date"
              value={dateFrom}
              onChange={(e) => setDateFrom(e.target.value)}
              style={{
                width: '100%',
                padding: '8px',
                borderRadius: '4px',
                border: '1px solid #444',
                backgroundColor: '#222',
                color: '#fff',
                fontSize: '13px',
                boxSizing: 'border-box'
              }}
            />
          </div>

          {/* Date To */}
          <div>
            <label style={{ display: 'block', marginBottom: '6px', fontSize: '13px', color: '#aaa' }}>To Date</label>
            <input
              type="date"
              value={dateTo}
              onChange={(e) => setDateTo(e.target.value)}
              style={{
                width: '100%',
                padding: '8px',
                borderRadius: '4px',
                border: '1px solid #444',
                backgroundColor: '#222',
                color: '#fff',
                fontSize: '13px',
                boxSizing: 'border-box'
              }}
            />
          </div>

          {/* Category Filter */}
          <div>
            <label style={{ display: 'block', marginBottom: '6px', fontSize: '13px', color: '#aaa' }}>Category</label>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              style={{
                width: '100%',
                padding: '8px',
                borderRadius: '4px',
                border: '1px solid #444',
                backgroundColor: '#222',
                color: '#fff',
                fontSize: '13px',
                boxSizing: 'border-box'
              }}
            >
              <option value="">All Categories</option>
              {categories.map(cat => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
          </div>

          {/* Merchant Search */}
          <div>
            <label style={{ display: 'block', marginBottom: '6px', fontSize: '13px', color: '#aaa' }}>Search Merchant</label>
            <input
              type="text"
              placeholder="e.g., McDonald's, Amazon"
              value={searchMerchant}
              onChange={(e) => setSearchMerchant(e.target.value)}
              style={{
                width: '100%',
                padding: '8px',
                borderRadius: '4px',
                border: '1px solid #444',
                backgroundColor: '#222',
                color: '#fff',
                fontSize: '13px',
                boxSizing: 'border-box'
              }}
            />
          </div>
        </div>

        {/* Export Buttons */}
        <div style={{
          display: 'flex',
          gap: '8px',
          flexWrap: 'wrap',
          alignItems: 'center'
        }}>
          <button
            onClick={exportToCSV}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '8px 16px',
              backgroundColor: '#22c55e',
              color: '#000',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '13px',
              fontWeight: '600'
            }}
          >
            <Download size={16} />
            Export CSV
          </button>
          
          <button
            onClick={exportToPDF}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '8px 16px',
              backgroundColor: '#3b82f6',
              color: '#fff',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '13px',
              fontWeight: '600'
            }}
          >
            <Download size={16} />
            Export PDF
          </button>
          
          <span style={{ fontSize: '12px', color: '#666' }}>
            ({filteredExpenses.length} {filteredExpenses.length === 1 ? 'expense' : 'expenses'} to export)
          </span>
        </div>
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
          <h4>Recent Expenses ({filteredExpenses.length})</h4>
          {filteredExpenses.length === 0 ? (
            <div className="empty-state">
              <Receipt className="empty-icon" size={64} />
              <h4>{expenses.length === 0 ? 'No expenses yet' : 'No expenses match filters'}</h4>
              <p>{expenses.length === 0 ? 'Upload your first receipt using the Upload tab to get started' : 'Try adjusting your filters'}</p>
            </div>
          ) : (
            <div className="expenses-grid">
              {filteredExpenses.slice(0, 10).map((expense) => (
                <ExpenseCard 
                  key={expense.id} 
                  expense={expense}
                  onEdit={handleEditClick}
                  onDelete={handleDeleteClick}
                />
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Edit Modal */}
      {showEditModal && selectedExpense && (
        <EditExpenseModal
          expense={selectedExpense}
          onClose={() => {
            setShowEditModal(false)
            setSelectedExpense(null)
          }}
          onUpdate={handleExpenseUpdated}
          onDelete={handleDeleteClick}
        />
      )}
    </div>
  )

}

export default DashboardPage

