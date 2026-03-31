import React, { useState } from 'react'
import UploadPage from './pages/UploadPage'
import DashboardPage from './pages/DashboardPage'
import './App.css'

function App() {
  const [currentPage, setCurrentPage] = useState('upload') // 'upload' | 'dashboard'

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="container header-content">
          <div className="logo">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="currentColor">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14,2 14,8 20,8"/>
              <line x1="12" y1="18" x2="12.01" y2="18"/>
              <path d="M16,16H8a1,1 0 0 1-1-1V11a1,1 0 0 1 1-1H16a1,1 0 0 1 1 1v4A1,1 0 0 1 16 16Z"/>
            </svg>
            <h1>SmartSpend AI V2</h1>
          </div>

          {/* Navigation */}
          <nav className="nav-desktop">
            <button 
              className={`nav-link ${currentPage === 'upload' ? 'active' : ''}`} 
              onClick={() => setCurrentPage('upload')}
            >
              📤 Upload
            </button>
            <button 
              className={`nav-link ${currentPage === 'dashboard' ? 'active' : ''}`}
              onClick={() => setCurrentPage('dashboard')}
            >
              📊
              Dashboard
            </button>
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main className="main">
        <div className="container">
          {currentPage === 'upload' ? <UploadPage /> : <DashboardPage />}
        </div>
      </main>

      {/* Footer */}
      <footer className="footer">
        <div className="container">
          <p>&copy; 2026 SmartSpend AI V2. FastAPI + React + EasyOCR.</p>
        </div>
      </footer>
    </div>
  )
}

export default App
