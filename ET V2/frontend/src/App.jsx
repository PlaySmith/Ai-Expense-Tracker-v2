import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sun, Moon, UploadCloud, BarChart3, Menu, X } from 'lucide-react';
import UploadPage from './pages/UploadPage';
import Dashboard from './pages/Dashboard';
import './index.css';

function App() {
  const [darkMode, setDarkMode] = useState(true);
  const [currentPage, setCurrentPage] = useState('upload');
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  // Sync theme with data-theme attribute for CSS variables
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', darkMode ? 'dark' : 'light');
  }, [darkMode]);

  // Prevent scroll when mobile menu is open
  useEffect(() => {
    document.body.style.overflow = isMenuOpen ? 'hidden' : 'unset';
  }, [isMenuOpen]);

  return (
    <div className="app-layout">
      <header className="main-header glass">
        <div className="container header-inner">
          {/* Logo Section */}
          <div className="logo-section">
            <div className="logo-icon">
              <BarChart3 size={22} />
            </div>
            <div className="logo-text">
              <h1>SmartSpend</h1>
              <span>AI V2.1</span>
            </div>
          </div>

          {/* Desktop Navigation */}
          <nav className="desktop-nav">
            <button 
              className={`nav-link ${currentPage === 'upload' ? 'active' : ''}`}
              onClick={() => setCurrentPage('upload')}
            >
              <UploadCloud size={18} /> <span>Scan</span>
            </button>
            <button 
              className={`nav-link ${currentPage === 'dashboard' ? 'active' : ''}`}
              onClick={() => setCurrentPage('dashboard')}
            >
              <BarChart3 size={18} /> <span>Analytics</span>
            </button>
          </nav>

          {/* Action Group */}
          <div className="action-group">
            <button className="icon-btn" onClick={() => setDarkMode(!darkMode)} aria-label="Toggle Theme">
              {darkMode ? <Sun size={20} /> : <Moon size={20} />}
            </button>
            <button className="icon-btn mobile-toggle" onClick={() => setIsMenuOpen(!isMenuOpen)}>
              {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>

        {/* Mobile Navigation Overlay */}
        <AnimatePresence>
          {isMenuOpen && (
            <motion.div 
              className="mobile-overlay"
              initial={{ opacity: 0, x: '100%' }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: '100%' }}
              transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            >
              <div className="mobile-menu-content">
                <button onClick={() => {setCurrentPage('upload'); setIsMenuOpen(false)}}>
                  <UploadCloud size={24} /> Scan Receipts
                </button>
                <button onClick={() => {setCurrentPage('dashboard'); setIsMenuOpen(false)}}>
                  <BarChart3 size={24} /> View Analytics
                </button>
                <div className="menu-footer">
                  <p>SmartSpend AI V2.1</p>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </header>

      {/* Main Content Area */}
      <main className="content-wrapper container">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentPage}
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -15 }}
            transition={{ duration: 0.25 }}
          >
            {currentPage === 'upload' ? <UploadPage /> : <Dashboard />}
          </motion.div>
        </AnimatePresence>
      </main>

      <footer className="main-footer">
        <p>© 2026 SmartSpend AI • Nagpur, India • Pure CSS</p>
      </footer>
    </div>
  );
}

export default App;