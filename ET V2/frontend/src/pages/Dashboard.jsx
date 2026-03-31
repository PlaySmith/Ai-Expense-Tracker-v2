import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { BarChart3, TrendingUp, AlertTriangle, DollarSign, CreditCard, Receipt, PieChart as PieIcon } from 'lucide-react';
import axios from 'axios';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

const COLORS = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

const Dashboard = () => {
  const [stats, setStats] = useState({ total: 0, amount: 0, avg: 0, review: 0 });
  const [expenses, setExpenses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [categoryData, setCategoryData] = useState([]);

  useEffect(() => { fetchData(); }, []);

  const fetchData = async () => {
    try {
      const [statsRes, expensesRes] = await Promise.all([
        axios.get('/api/expenses/stats'),
        axios.get('/api/expenses')
      ]);
      setStats({
        total: statsRes.data.total_count || 0,
        amount: statsRes.data.total_amount || 0,
        avg: statsRes.data.average_amount || 0,
        review: statsRes.data.review_count || 0
      });
      const data = expensesRes.data.expenses || [];
      setExpenses(data.slice(0, 5));
      
      const cats = data.reduce((acc, exp) => {
        const cat = exp.category || 'Other';
        acc[cat] = (acc[cat] || 0) + (exp.amount || 0);
        return acc;
      }, {});
      setCategoryData(Object.entries(cats).map(([name, value]) => ({ name, value })));
    } finally { setLoading(false); }
  };

  if (loading) return <div className="text-center" style={{ padding: '100px' }}>Loading Analytics...</div>;

  return (
    <div className="dashboard-page">
      {/* Stats Section */}
      <section className="grid-stats">
        <div className="glass card-stat" style={{ padding: '2rem' }}>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>TOTAL RECEIPTS</p>
          <h2 style={{ fontSize: '2.5rem', fontWeight: 900 }}>{stats.total}</h2>
        </div>
        <div className="glass card-stat" style={{ padding: '2rem', background: 'var(--accent-glow)' }}>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>TOTAL SPENT</p>
          <h2 style={{ fontSize: '2.5rem', fontWeight: 900, color: 'var(--accent)' }}>₹{stats.amount.toLocaleString()}</h2>
        </div>
        <div className="glass card-stat" style={{ padding: '2rem' }}>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>NEEDS REVIEW</p>
          <h2 style={{ fontSize: '2.5rem', fontWeight: 900, color: '#f59e0b' }}>{stats.review}</h2>
        </div>
      </section>

      <div className="dashboard-layout">
        {/* Category Breakdown */}
        <div className="glass" style={{ padding: '2rem' }}>
          <h3 style={{ marginBottom: '1.5rem' }}>Categories</h3>
          <div style={{ height: '300px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={categoryData} dataKey="value" nameKey="name" outerRadius={80} cornerRadius={10} paddingAngle={5}>
                  {categoryData.map((entry, index) => <Cell key={index} fill={COLORS[index % COLORS.length]} />)}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="glass" style={{ padding: '2rem' }}>
          <h3 style={{ marginBottom: '1.5rem' }}>Recent Activity</h3>
          {expenses.map((exp, idx) => (
            <div key={idx} style={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              padding: '1rem', 
              borderBottom: '1px solid var(--border)',
              alignItems: 'center'
            }}>
              <div>
                <p style={{ fontWeight: 700 }}>{exp.merchant || 'Unknown'}</p>
                <span className={`badge ${exp.requires_review ? 'badge-warning' : 'badge-success'}`}>
                  {exp.category || 'Other'}
                </span>
              </div>
              <p style={{ fontSize: '1.2rem', fontWeight: 800 }}>₹{exp.amount}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;