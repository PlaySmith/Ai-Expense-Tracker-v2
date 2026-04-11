import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom'
import { Receipt, LayoutDashboard, Upload, Menu, X, LogIn, User } from 'lucide-react'
import { useAuth } from './context/AuthContext.jsx'
import UploadPage from './pages/UploadPage'
import DashboardPage from './pages/DashboardPage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import './App.css'


function App() {
  const { isAuthenticated, logout, user } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  return (
    <Router>
      <div className="app">
        {/* Header */}

      <header className="header">
        <div className="container header-content">
          <div className="logo">
            <Receipt className="logo-icon" />
            <h1>SmartSpend AI</h1>
          </div>
          
          {/* Desktop Navigation */}
          <nav className="nav-desktop">
            <Link to="/" className="nav-link">
              <Upload size={18} />
              Upload
            </Link>
            <Link to="/dashboard" className="nav-link">
              <LayoutDashboard size={18} />
              Dashboard
            </Link>
            {isAuthenticated ? (
              <div className="nav-user">
                <span>{user?.email}</span>
                <button onClick={logout} className="logout-btn">
                  Logout
                </button>
              </div>
            ) : (
              <Link to="/login" className="nav-link">
                <LogIn size={18} />
                Login
              </Link>
            )}
          </nav>

          {/* Mobile Menu Button */}
          <button 
            className="mobile-menu-btn"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <nav className="nav-mobile">
            <Link to="/" className="nav-link" onClick={() => setMobileMenuOpen(false)}>
              <Upload size={18} />
              Upload
            </Link>
            <Link to="/dashboard" className="nav-link" onClick={() => setMobileMenuOpen(false)}>
              <LayoutDashboard size={18} />
              Dashboard
            </Link>
            {isAuthenticated ? (
              <>
                <Link to="/profile" className="nav-link" onClick={() => setMobileMenuOpen(false)}>
                  <User size={18} />
                  Profile
                </Link>
                <button onClick={() => { logout(); setMobileMenuOpen(false); }} className="nav-logout">
                  Logout
                </button>
              </>
            ) : (
              <Link to="/login" className="nav-link" onClick={() => setMobileMenuOpen(false)}>
                <LogIn size={18} />
                Login
              </Link>
            )}
          </nav>
        )}
      </header>

      {/* Main Content */}
      <main className="main">
        <div className="container">
          <Routes>
            <Route path="/" element={<UploadPage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
          </Routes>

        </div>
      </main>

      {/* Footer */}
      <footer className="footer">
        <div className="container">
          <p>&copy; 2024 SmartSpend AI. Built with FastAPI + React + Tesseract OCR.</p>
        </div>
      </footer>
    </div>
  </Router>
)
}


export default App
