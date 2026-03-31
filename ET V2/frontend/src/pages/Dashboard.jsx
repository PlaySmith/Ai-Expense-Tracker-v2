import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { BarChart3, TrendingUp, AlertTriangle, DollarSign, CreditCard, Receipt, PieChart as PieIcon } from 'lucide-react'
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts'
import axios from 'axios'

const COLORS = ['#3b82f6', '#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#ec4899']

const DashboardPage = () => {
  const [stats, setStats] = useState({ total: 0, amount: 0, avg: 0, review: 0 })
  const [expenses, setExpenses] = useState([])
  const [loading, setLoading] = useState(true)
  const [categoryData, setCategoryData] = useState([])

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    setLoading(true)
    try {
      const [statsRes, expensesRes] = await Promise.all([
        axios.get('/api/expenses/stats'),
        axios.get('/api/expenses')
      ])
      
      const statsData = statsRes.data || {}
      setStats({
        total: statsData.total_count || 0,
        amount: statsData.total_amount || 0,
        avg: statsData.average_amount || 0,
        review: statsData.review_count || 0
      })
      
      const data = expensesRes.data.expenses || []
      setExpenses(data.slice(0, 6))
      
      // Category pie data
      const cats = data.reduce((acc, exp) => {
        const cat = exp.category || 'Other'
        acc[cat] = (acc[cat] || 0) + (exp.amount || 0)
        return acc
      }, {})
      setCategoryData(Object.entries(cats).map(([name, value], i) => ({
        name,
        value,
        fill: COLORS[i % COLORS.length]
      })))
      
    } catch (error) {
      console.error('Dashboard error:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="dashboard min-h-[70vh]">
      {loading ? (
        <motion.div 
          className="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-slate-900/95 backdrop-blur-sm z-40"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <div className="glass p-12 rounded-3xl text-center max-w-md mx-6">
            <div className="w-20 h-20 border-4 border-slate-700/50 border-t-blue-500 rounded-full animate-spin mx-auto mb-6"></div>
            <h3 className="text-2xl font-bold text-white mb-2">Loading Analytics</h3>
            <p className="text-slate-400">Fetching your expense insights...</p>
          </div>
        </motion.div>
      ) : (
        <>
          {/* Stats Grid */}
          <motion.section 
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12"
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ staggerChildren: 0.1 }}
          >
            <motion.div 
              whileHover={{ scale: 1.05, y: -8 }}
              className="glass p-8 rounded-3xl group cursor-pointer hover:shadow-2xl transition-all duration-500"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="p-4 bg-blue-500/20 rounded-2xl group-hover:bg-blue-400/30 transition-all duration-300 backdrop-blur-sm">
                  <BarChart3 className="w-7 h-7 text-blue-400 drop-shadow-lg" />
                </div>
                <DollarSign className="w-10 h-10 text-slate-400 group-hover:text-slate-200 transition-all duration-300" />
              </div>
              <p className="text-slate-400 text-sm font-medium uppercase tracking-wide mb-2">Total Receipts</p>
              <p className="text-4xl font-black text-white">{stats.total.toLocaleString()}</p>
            </motion.div>

            <motion.div 
              whileHover={{ scale: 1.05, y: -8 }}
              className="glass p-8 rounded-3xl group cursor-pointer hover:shadow-2xl transition-all duration-500 bg-gradient-to-br from-emerald-500/5 backdrop-blur-sm"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="p-4 bg-emerald-500/20 rounded-2xl group-hover:bg-emerald-400/30 transition-all duration-300 backdrop-blur-sm">
                  <TrendingUp className="w-7 h-7 text-emerald-400 drop-shadow-lg" />
                </div>
                <DollarSign className="w-10 h-10 text-slate-400 group-hover:text-slate-200" />
              </div>
              <p className="text-slate-400 text-sm font-medium uppercase tracking-wide mb-2">Total Spent</p>
              <p className="text-4xl font-black bg-gradient-to-r from-emerald-400 to-emerald-200 bg-clip-text text-transparent">
                ₹{stats.amount.toLocaleString()}
              </p>
            </motion.div>

            <motion.div 
              whileHover={{ scale: 1.05, y: -8 }}
              className="glass p-8 rounded-3xl group cursor-pointer hover:shadow-2xl transition-all duration-500"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="p-4 bg-orange-500/20 rounded-2xl group-hover:bg-orange-400/30 transition-all duration-300 backdrop-blur-sm">
                  <CreditCard className="w-7 h-7 text-orange-400 drop-shadow-lg" />
                </div>
                <DollarSign className="w-10 h-10 text-slate-400 group-hover:text-slate-200" />
              </div>
              <p className="text-slate-400 text-sm font-medium uppercase tracking-wide mb-2">Avg Amount</p>
              <p className="text-4xl font-black text-white">₹{Math.round(stats.avg)}</p>
            </motion.div>

            <motion.div 
              whileHover={{ scale: 1.05, y: -8 }}
              className="glass p-8 rounded-3xl group cursor-pointer hover:shadow-2xl border border-yellow-500/30 bg-gradient-to-br from-yellow-500/5 to-orange-500/5"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="p-4 bg-yellow-500/20 rounded-2xl group-hover:bg-yellow-400/30 transition-all duration-300 backdrop-blur-sm">
                  <AlertTriangle className="w-7 h-7 text-yellow-400 drop-shadow-lg" />
                </div>
                <DollarSign className="w-10 h-10 text-slate-400 group-hover:text-slate-200" />
              </div>
              <p className="text-slate-400 text-sm font-medium uppercase tracking-wide mb-2">Needs Review</p>
              <p className="text-4xl font-black text-yellow-400">{stats.review}</p>
            </motion.div>
          </motion.section>

          <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
            {/* Category Chart */}
            <motion.section 
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="xl:col-span-1 glass p-8 rounded-3xl"
            >
              <div className="flex items-center space-x-3 mb-8">
                <PieIcon className="w-7 h-7 text-purple-400" />
                <h3 className="text-2xl font-bold text-white">Spending by Category</h3>
              </div>
              <div className="h-80 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={categoryData}
                      cx="50%"
                      cy="50%"
                      outerRadius={90}
                      dataKey="value"
                      nameKey="name"
                      cornerRadius={8}
                    >
                      {categoryData.map((entry, index) => (
                        <Cell 
                          key={`cell-${index}`} 
                          fill={entry.fill} 
                          strokeWidth={2}
                          stroke="rgba(255,255,255,0.1)"
                        />
                      ))}
                    </Pie>
                    <Tooltip contentStyle={{
                      background: 'rgba(15, 23, 42, 0.95)',
                      border: '1px solid rgba(255,255,255,0.1)',
                      borderRadius: '12px',
                      backdropFilter: 'blur(10px)'
                    }} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </motion.section>

            {/* Recent Expenses */}
            <motion.section 
              initial={{ opacity: 0, x: 30 }}
              animate={{ opacity: 1, x: 0 }}
              className="xl:col-span-2 glass p-8 rounded-3xl"
            >
              <div className="flex items-center justify-between mb-10">
                <div className="flex items-center space-x-3">
                  <Receipt className="w-7 h-7 text-blue-400" />
                  <div>
                    <h3 className="text-2xl font-bold text-white">Recent Receipts</h3>
                    <p className="text-slate-400 text-sm mt-1">Latest OCR processed</p>
                  </div>
                </div>
                <motion.button 
                  whileHover={{ scale: 1.05 }}
                  className="btn btn-secondary px-8 py-3 text-sm"
                >
                  View All
                </motion.button>
              </div>

              <div className="space-y-4">
                <AnimatePresence>
                  {expenses.map((expense, index) => (
                    <motion.article
                      key={expense.id || index}
                      initial={{ opacity: 0, y: 30 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -30 }}
                      transition={{ delay: index * 0.1 }}
                      whileHover={{ scale: 1.02, y: -5, boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.6)' }}
                      className={`group cursor-pointer p-8 rounded-3xl border transition-all duration-500 overflow-hidden relative ${
                        expense.requires_review 
                          ? 'border-yellow-500/40 bg-gradient-to-r from-yellow-500/5 to-orange-500/5' 
                          : 'border-slate-700/50 hover:border-slate-600/70 bg-gradient-to-r from-slate-800/20 hover:from-slate-700/30'
                      }`}
                    >
                      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/2 to-transparent -skew-x-12 -translate-x-40 group-hover:translate-x-40 transition-transform duration-1000" />
                      <div className="relative z-10 flex items-start justify-between gap-6">
                        <div className="flex-1 min-w-0">
                          <motion.h4 
                            className="font-black text-xl text-white truncate pr-8 mb-2 group-hover:text-blue-400 transition-all duration-300"
                            whileHover={{ scale: 1.02 }}
                          >
                            {expense.merchant || 'Unnamed Merchant'}
                          </motion.h4>
                          <div className="flex flex-wrap items-center gap-3 text-sm opacity-85 mb-3">
                            <span className={`badge badge-${expense.category === 'Food & Dining' ? 'success' : 'default'}`}>
                              {expense.category || 'Other'}
                            </span>
                            {expense.date && (
                              <span className="opacity-75 font-mono text-xs">
                                {new Date(expense.date).toLocaleDateString('en-IN')}
                              </span>
                            )}
                          </div>
                        </div>
                        <div className="text-right flex-shrink-0">
                          <motion.p 
                            className="text-3xl font-black text-white mb-2 drop-shadow-lg"
                            animate={{ scale: 1.05 }}
                            transition={{ yoyo: Infinity, duration: 2 }}
                          >
                            ₹{expense.amount ? expense.amount.toLocaleString('en-IN', {minimumFractionDigits: 0, maximumFractionDigits: 2}) : '0'}
                          </motion.p>
                          <div className="flex items-center gap-2">
                            <motion.span 
                              className={`px-3 py-1 rounded-full font-mono font-bold text-sm shadow-lg ${
                                expense.ocr_confidence > 0.8 ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30' :
                                expense.ocr_confidence > 0.6 ? 'bg-blue-500/20 text-blue-400 border-blue-500/30' :
                                'bg-yellow-500/20 text-yellow-400 border-yellow-500/30 animate-pulse'
                              }`}
                              style={{ border: '1px solid' }}
                            >
                              {(expense.ocr_confidence * 100).toFixed(0)}%
                            </motion.span>
                            {expense.requires_review && (
                              <motion.div 
                                className="flex items-center gap-1 px-3 py-1 rounded-full bg-gradient-to-r from-yellow-500/20 to-orange-500/20 border border-yellow-500/40 text-yellow-300 font-medium text-xs animate-pulse"
                                whileHover={{ scale: 1.1 }}
                              >
                                <AlertTriangle className="w-4 h-4" />
                                <span>Review</span>
                              </motion.div>
                            )}
                          </div>
                        </div>
                      </div>
                    </motion.article>
                  ))}
                </AnimatePresence>
                
                {expenses.length === 0 && (
                  <motion.div 
                    className="text-center py-24 text-slate-500 animate-fade-in-up"
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                  >
                    <Receipt className="w-24 h-24 mx-auto mb-8 opacity-40 animate-float" />
                    <h3 className="text-2xl font-bold text-slate-400 mb-4">No Receipts Yet</h3>
                    <p className="text-lg opacity-80 mb-8 max-w-md mx-auto">Upload your first receipt to unlock analytics and spending insights</p>
                    <div className="glass px-8 py-4 rounded-2xl inline-block cursor-pointer hover:shadow-xl transition-all">
                      <span className="font-semibold">🚀 Get Started</span>
                    </div>
                  </motion.div>
                )}
              </div>
            </motion.section>
          </div>
        </>
      )}
    </div>
  )
}

export default DashboardPage

