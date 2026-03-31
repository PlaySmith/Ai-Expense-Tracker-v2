import { useState, useCallback, useRef } from 'react'
import axios from 'axios'
import './UploadPage.css'

const API_BASE = '/api/expenses'

function ProfessionalUpload() {
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState('')
  const [uploading, setUploading] = useState(false)
  const [result, setResult] = useState(null)
  const [expenses, setExpenses] = useState([])
  const [error, setError] = useState('')
  const fileInputRef = useRef(null)

  const resetState = () => {
    setFile(null)
    setPreview('')
    setResult(null)
    setError('')
  }

  const handleFileSelect = useCallback((selectedFile) => {
    if (selectedFile && selectedFile.type.startsWith('image/')) {
      setFile(selectedFile)
      const url = URL.createObjectURL(selectedFile)
      setPreview(url)
      setError('')
    } else {
      setError('Please select a valid image file (JPG, PNG)')
    }
  }, [])

  const handleFileDrop = useCallback((e) => {
    e.preventDefault()
    e.stopPropagation()
    handleFileSelect(e.dataTransfer.files[0])
  }, [handleFileSelect])

  const handleDragOver = useCallback((e) => {
    e.preventDefault()
    e.stopPropagation()
  }, [])

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file first')
      return
    }

    setUploading(true)
    setError('')
    const formData = new FormData()
    formData.append('file', file)

    try {
      const res = await axios.post(API_BASE + '/upload', formData, {
        timeout: 60000,
        headers: { 'Content-Type': 'multipart/form-data' }
      })

      if (res.data.success) {
        setResult(res.data)
        refreshList()
      } else {
        setError(res.data.message || 'Processing failed')
      }
    } catch (err) {
      console.error(err)
      const errData = err.response?.data
      if (typeof errData === 'object' && errData !== null) {
        setError(errData.message || errData.detail || JSON.stringify(errData.error || errData))
      } else {
        setError(err.response?.data?.detail || err.message || 'Upload failed - server error')
      }
    } finally {
      setUploading(false)
      URL.revokeObjectURL(preview)
    }
  }

  const refreshList = async () => {
    try {
      const res = await axios.get(API_BASE)
      setExpenses(res.data.expenses || [])
    } catch {
      // Silent fail
    }
  }

  const clearResult = () => {
    setResult(null)
  }

  return (
    <div className="pro-upload-container">
      <div className="upload-panel">
        <h2>📤 Receipt Upload</h2>
        <div className="drop-zone" 
             onDrop={handleFileDrop}
             onDragOver={handleDragOver}
             onClick={() => fileInputRef.current?.click()}>
          
          {preview ? (
            <div className="image-preview">
              <img src={preview} alt="Receipt preview" />
              <div className="preview-overlay">
                <p>{file.name}</p>
                <button onClick={resetState} className="change-btn">Change</button>
              </div>
            </div>
          ) : (
            <div className="drop-placeholder">
              <svg width="64" height="64" fill="currentColor" viewBox="0 0 24 24">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14,2 14,8 20,8"/>
                <line x1="12" y1="18" x2="12.01" y2="18"/>
                <path d="M16,16H8a1,1 0,0 1-1-1V11a1,1 0,0 1 1-1H16a1,1 0,0 1 1 1v4A1,1 0,0 1 16 16Z"/>
              </svg>
              <p>Drop receipt image here or click to browse</p>
              <small>JPG, PNG up to 10MB</small>
            </div>
          )}
          
          <input ref={fileInputRef} type="file" accept="image/*" 
                 onChange={(e) => handleFileSelect(e.target.files?.[0])}
                 style={{ display: 'none' }} />
        </div>

        <button className="upload-button" onClick={handleUpload} disabled={!file || uploading}>
          {uploading ? (
            <>
              <span className="spinner"></span>
              Analyzing with AI OCR...
            </>
          ) : (
            'Process Receipt'
          )}
        </button>
      </div>

      {error && (
        <div className="error-modal">
          <div className="error-content">
            <h3>Upload Error</h3>
            <p>{error}</p>
            <button onClick={() => setError('')} className="close-error">Try Again</button>
          </div>
        </div>
      )}

      {result && (
        <div className={`result-panel ${result.success ? 'success' : 'error'}`}>
          <div className="result-header">
            <h3>{result.success ? '✅ Receipt Processed!' : '❌ Processing Failed'}</h3>
            <button onClick={clearResult} className="close-result">×</button>
          </div>
          
          {result.success && result.expense && (
            <div className="result-details">
              <div className="extracted-item">
                <label>Merchant</label>
                <span>{result.expense.merchant || 'Unknown'}</span>
              </div>
              <div className="extracted-item amount">
                <label>Amount</label>
                <span>₹{result.expense.amount?.toFixed(2)}</span>
              </div>
              <div className="extracted-item">
                <label>Confidence</label>
                <span>{(result.expense.ocr_confidence * 100 || 0).toFixed(0)}%</span>
              </div>
              {result.expense.requires_review && (
                <div className="review-banner">
                  ⚠️ Low confidence - please verify before finalizing
                </div>
              )}
              {result.warnings?.length > 0 && (
                <div className="warnings">
                  {result.warnings.map((w, i) => (
                    <div key={i} className="warning">{w}</div>
                  ))}
                </div>
              )}
            </div>
          )}
          
          {!result.success && (
            <div className="result-message">
              {result.message || 'Unknown error - check image quality'}
            </div>
          )}
        </div>
      )}

      <div className="recent-list">
        <h3>Recent Expenses ({expenses.length})</h3>
        <div className="expenses-table">
          <div className="table-header">
            <span>Merchant</span>
            <span>Amount</span>
            <span>Status</span>
            <span>Date</span>
          </div>
          {expenses.map((exp) => (
            <div key={exp.id} className="table-row">
              <span>{exp.merchant}</span>
              <span>₹{exp.amount?.toFixed(2)}</span>
              <span className={`status ${exp.requires_review ? 'review' : 'ok'}`}>
                {exp.requires_review ? 'Review' : 'OK'}
              </span>
              <span>{new Date(exp.created_at).toLocaleDateString()}</span>
            </div>
          ))}
        </div>
        {expenses.length === 0 && (
          <div className="empty-state">
            <p>No expenses yet. Upload your first receipt!</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default ProfessionalUpload


