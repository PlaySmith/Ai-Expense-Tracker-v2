import React, { useState, useCallback, useEffect } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, FileText, CheckCircle, AlertCircle, Loader2, Camera, LogIn } from 'lucide-react'
import { expenseAPI } from '../api/API'
import { useAuth } from '../context/AuthContext.jsx'
import { Link } from 'react-router-dom'
import './UploadPage.css'

function UploadPage() {
  const { isAuthenticated } = useAuth()
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  // Redirect if not authenticated
  useEffect(() => {
    if (!isAuthenticated) {
      window.location.href = '/login?redirect=upload'
      return
    }
  }, [isAuthenticated])

  const onDrop = useCallback((acceptedFiles) => {
    const selectedFile = acceptedFiles[0]
    if (selectedFile) {
      setFile(selectedFile)
      setPreview(URL.createObjectURL(selectedFile))
      setResult(null)
      setError(null)
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.bmp', '.tiff']
    },
    maxSize: 10 * 1024 * 1024, // 10MB
    multiple: false
  })

  const handleUpload = async () => {
    if (!file) return

    setUploading(true)
    setUploadProgress(0)
    setError(null)
    setResult(null)

    try {
      const data = await expenseAPI.uploadReceipt(file, (progress) => {
        setUploadProgress(progress)
      })
      
      setResult(data)
      
      // Clear file after successful upload
      if (data.success) {
        setTimeout(() => {
          setFile(null)
          setPreview(null)
        }, 3000)
      }
    } catch (err) {
      console.error('Upload error:', err)
      setError({
        message: err.message || 'Failed to upload receipt',
        code: err.code || 'UNKNOWN_ERROR',
        details: err.details || {}
      })
    } finally {
      setUploading(false)
    }
  }

  const clearFile = () => {
    setFile(null)
    setPreview(null)
    setResult(null)
    setError(null)
  }

  if (!isAuthenticated) {
    return (
      <div className="upload-page">
        <div className="auth-required">
          <LogIn size={64} className="auth-icon" />
          <h2>Please log in to upload receipts</h2>
          <p>Your account is required to process and store expenses securely.</p>
          <Link to="/login" className="btn btn-primary login-btn">
            Go to Login
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="upload-page">
      <div className="page-header">
        <h2>Upload Receipt</h2>
        <p>Take a photo or upload an image of your receipt</p>
      </div>

      {/* Dropzone */}
      <div className="card">
        <div
          {...getRootProps()}
          className={`dropzone ${isDragActive ? 'active' : ''} ${isDragReject ? 'reject' : ''}`}
        >
          <input {...getInputProps()} />
          
          {preview ? (
            <div className="preview-container">
              <img src={preview} alt="Receipt preview" className="preview-image" />
              <button className="clear-btn" onClick={(e) => { e.stopPropagation(); clearFile(); }}>
                Remove
              </button>
            </div>
          ) : (
            <div className="dropzone-content">
              <div className="dropzone-icon">
                {isDragActive ? <Camera size={48} /> : <Upload size={48} />}
              </div>
              <p className="dropzone-text">
                {isDragActive
                  ? 'Drop the receipt here...'
                  : 'Drag & drop a receipt image here, or click to select'}
              </p>
              <p className="dropzone-hint">
                Supports: JPG, PNG, BMP, TIFF (Max 10MB)
              </p>
            </div>
          )}
        </div>

        {/* Upload Button */}
        {file && !uploading && !result && (
          <button 
            className="btn btn-primary upload-btn"
            onClick={handleUpload}
            disabled={uploading}
          >
            <FileText size={18} />
            Process Receipt
          </button>
        )}

        {/* Progress */}
        {uploading && (
          <div className="upload-progress">
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${uploadProgress}%` }}
              />
            </div>
            <div className="progress-info">
              <Loader2 className="spinner-icon" size={20} />
              <span>Processing... {uploadProgress}%</span>
            </div>
            <p className="progress-hint">
              OCR processing may take a few seconds
            </p>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="alert alert-error">
            <AlertCircle size={20} />
            <div className="alert-content">
              <strong>{error.message}</strong>
              {error.code && <span className="error-code">Code: {error.code}</span>}
              {error.details?.suggested_action && (
                <span className="suggestion">💡 {error.details.suggested_action}</span>
              )}
            </div>
          </div>
        )}

        {/* Processing Failed - But no crash */}
        {result && !result.success && (
          <div className="result-container">
            <div className="alert alert-warning">
              <AlertCircle size={20} />
              <span>{result.message}</span>
            </div>

            {result.extracted_data && (
              <div className="extracted-data">
                <h4>Extracted Information (Incomplete)</h4>
                <div className="data-grid">
                  <div className="data-item">
                    <label>Merchant</label>
                    <span>{result.extracted_data.parsed_data?.merchant || 'Not detected'}</span>
                  </div>
                  <div className="data-item">
                    <label>Amount</label>
                    <span className="amount" style={{color: '#e74c3c'}}>
                      Not detected
                    </span>
                  </div>
                  <div className="data-item">
                    <label>Date</label>
                    <span>{result.extracted_data.parsed_data?.date ? new Date(result.extracted_data.parsed_data.date).toLocaleDateString() : 'Not detected'}</span>
                  </div>
                  <div className="data-item">
                    <label>Category</label>
                    <span className="badge">{result.extracted_data.parsed_data?.category || 'Uncategorized'}</span>
                  </div>
                </div>
                
                {result.extracted_data?.ocr_confidence > 0 && (
                  <div className="confidence-score">
                    <label>OCR Confidence</label>
                    <div className={`confidence-bar ${result.extracted_data.ocr_confidence > 80 ? 'high' : result.extracted_data.ocr_confidence > 60 ? 'medium' : 'low'}`}>
                      <div 
                        className="confidence-fill" 
                        style={{ width: `${result.extracted_data.ocr_confidence}%` }}
                      />
                      <span>{result.extracted_data.ocr_confidence.toFixed(1)}%</span>
                    </div>
                  </div>
                )}
              </div>
            )}

            {result.warnings?.length > 0 && (
              <div className="alert alert-warning">
                <AlertCircle size={18} />
                <div>
                  <strong>Suggestions:</strong>
                  <ul>
                    {result.warnings.map((warning, idx) => (
                      <li key={idx}>{warning}</li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
            
            <div className="retry-hint">
              <p>💡 <strong>Tip:</strong> Try uploading a clearer image with better lighting, or enter the expense manually on the Dashboard.</p>
            </div>
          </div>
        )}

        {/* Success Result */}
        {result?.success && (

          <div className="result-container">
            <div className="alert alert-success">
              <CheckCircle size={20} />
              <span>{result.message}</span>
            </div>

            {result.expense && (
              <div className="extracted-data">
                <h4>Extracted Information</h4>
                <div className="data-grid">
                  <div className="data-item">
                    <label>Merchant</label>
                    <span>{result.expense.merchant || 'Not detected'}</span>
                  </div>
                  <div className="data-item">
                    <label>Amount</label>
                    <span className="amount">
                      ${result.expense.amount?.toFixed(2) || '0.00'}
                    </span>
                  </div>
                  <div className="data-item">
                    <label>Date</label>
                    <span>{result.expense.date ? new Date(result.expense.date).toLocaleDateString() : 'Not detected'}</span>
                  </div>
                  <div className="data-item">
                    <label>Category</label>
                    <span className="badge badge-success">{result.expense.category || 'Uncategorized'}</span>
                  </div>
                </div>
                
                {result.extracted_data?.ocr_confidence && (
                  <div className="confidence-score">
                    <label>OCR Confidence</label>
                    <div className={`confidence-bar ${result.extracted_data.ocr_confidence > 80 ? 'high' : result.extracted_data.ocr_confidence > 60 ? 'medium' : 'low'}`}>
                      <div 
                        className="confidence-fill" 
                        style={{ width: `${result.extracted_data.ocr_confidence}%` }}
                      />
                      <span>{result.extracted_data.ocr_confidence.toFixed(1)}%</span>
                    </div>
                  </div>
                )}
              </div>
            )}

            {result.warnings?.length > 0 && (
              <div className="alert alert-warning">
                <AlertCircle size={18} />
                <div>
                  <strong>Warnings:</strong>
                  <ul>
                    {result.warnings.map((warning, idx) => (
                      <li key={idx}>{warning}</li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Tips Card */}
      <div className="card tips-card">
        <h4>💡 Tips for Best Results</h4>
        <ul>
          <li>Ensure good lighting when taking photos</li>
          <li>Keep the receipt flat and avoid shadows</li>
          <li>Make sure all text is clearly visible</li>
          <li>Capture the entire receipt in the frame</li>
          <li>Avoid blurry or low-resolution images</li>
        </ul>
      </div>
    </div>
  )
}

export default UploadPage
