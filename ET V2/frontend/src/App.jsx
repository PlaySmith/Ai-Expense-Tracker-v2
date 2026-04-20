import React, { useState } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import UploadPage from './pages/UploadPage'
import DashboardPage from './pages/DashboardPage'
import BudgetPage from './pages/BudgetPage'
import ProfilePage from './pages/ProfilePage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import ProtectedRoute from './components/ProtectedRoute.jsx'
import { useAuth } from './context/AuthContext.jsx'
import './App.css'

function MainShell() {
  const [currentPage, setCurrentPage] = useState('upload')
  const [refreshKey, setRefreshKey] = useState(0)
  const { user, logout } = useAuth()

  const handleUploadSuccess = () => {
    setRefreshKey((prev) => prev + 1)
  }

  return (
    <div className="app">
      <header className="navbar">
        <div className="nav-left">
          <h1 className="logo">SmartSpend AI V2</h1>
        </div>
        <div className="nav-center">
          <button
            type="button"
            className="nav-btn"
            onClick={() => setCurrentPage('upload')}
          >
            Upload
          </button>
          <button
            type="button"
            className="nav-btn"
            onClick={() => setCurrentPage('dashboard')}
          >
            Dashboard
          </button>
          <button
            type="button"
            className="nav-btn"
            onClick={() => setCurrentPage('budget')}
          >
            Budget
          </button>
        </div>
        <div className="nav-right nav-user-actions">
          <button
            type="button"
            className="nav-profile-name"
            title="Open profile"
            onClick={() => setCurrentPage('profile')}
          >
            {user?.full_name?.trim() || user?.email || 'Account'}
          </button>
          <button
            type="button"
            className="refresh-btn"
            onClick={() => setRefreshKey((prev) => prev + 1)}
          >
            Refresh
          </button>
          <button type="button" className="logout-btn" onClick={logout}>
            Log out
          </button>
        </div>
      </header>

      <main className="main">
        <div className="container">
          {currentPage === 'upload' ? (
            <UploadPage onUploadSuccess={handleUploadSuccess} />
          ) : currentPage === 'profile' ? (
            <ProfilePage
              onBack={() => setCurrentPage('upload')}
            />
          ) : currentPage === 'budget' ? (
            <BudgetPage />
          ) : (
            <DashboardPage refreshKey={refreshKey} />
          )}
        </div>
      </main>

      <footer className="footer">
        <div className="container">
          <p>&copy; 2026 SmartSpend AI V2. FastAPI + React + EasyOCR.</p>
        </div>
      </footer>
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter
      future={{ v7_startTransition: true, v7_relativeSplatPath: true }}
    >
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route
          path="/*"
          element={
            <ProtectedRoute>
              <MainShell />
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  )
}
