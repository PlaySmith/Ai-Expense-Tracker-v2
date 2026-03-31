import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Sun, Moon, UploadCloud, BarChart3 } from 'lucide-react';
import UploadPage from './pages/UploadPage';
import DashboardPage from './pages/DashboardPage';
import './App.css';

function App() {
  const [darkMode, setDarkMode] = useState(true);
  const [currentPage, setCurrentPage] = useState('upload');

  useEffect(() => {
    if (darkMode) {
      document.documentElement.setAttribute('data-theme', 'dark');
    } else {
      document.documentElement.removeAttribute('data-theme');
    }
  }, [darkMode]);

  return (
    <div className="app-container">
      {/* Doc-style Minimal Header */}
      <header className="header-doc">
        <div className="container">
          {/* Logo */}
          <div className="logo">
            <h1>SmartSpend AI</h1>
            <span>Receipt Tracker</span>
          </div>

          {/* Nav */}
          <nav className="nav-desktop">
            <motion.button
              className={`nav-btn ${currentPage === 'upload' ? 'active' : ''}`}
              onClick={() => setCurrentPage('upload')}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.98 }}
            >
              <UploadCloud className="icon" />
              Receipts
            </motion.button>
            <motion.button
              className={`nav-btn ${currentPage === 'dashboard' ? 'active' : ''}`}
              onClick={() => setCurrentPage('dashboard')}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.98 }}
            >
              <BarChart3 className="icon" />
              Dashboard
            </motion.button>
          </nav>

          {/* Theme Toggle */}
          <motion.button
            className="theme-btn"
            onClick={() => setDarkMode(!darkMode)}
            whileHover={{ rotate: 180 }}
            whileTap={{ scale: 0.95 }}
            title="Toggle theme"
          >
            {darkMode ? <Sun className="icon" /> : <Moon className="icon" />}
          </motion.button>
        </div>
      </header>

      {/* Spacer */}
      <div className="header-spacer"></div>

      {/* Main Content */}
      <main className="main-content">
        <div className="container">
          {currentPage === 'upload' ? <UploadPage /> : <DashboardPage />}
        </div>
      </main>

      {/* Footer */}
      <footer className="footer">
        <div className="container">
          <p>© 2026 SmartSpend AI • Pure CSS • FastAPI + React</p>
        </div>
      </footer>
    </div>
  );
}

export default App;

