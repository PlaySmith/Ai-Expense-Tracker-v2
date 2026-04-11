import React, { useState, useCallback, useEffect } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, FileText, CheckCircle, AlertCircle, Loader2, Camera } from 'lucide-react'
import { expenseAPI } from '../api/API'
import './UploadPage.css'

function UploadPage({ onUploadSuccess }) {
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

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
      
      // Clear file after successful upload + notify parent
      if (data.success) {
        if (onUploadSuccess) {
          onUploadSuccess()
        }
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
    if (preview) URL.revokeObjectURL(preview)
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
                ×
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
            Process Receipt with AI
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
              <span>Processing with OCR... {uploadProgress}%</span>
            </div>
            <p className="progress-hint">
              AI analysis in progress (2-5 seconds)
            </p>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="alert alert-error">
            <AlertCircle size={20} />
            <div className="alert-content">
              <strong>{error.message}</strong>
              {error.code && <code className="error-code">({error.code})</code>}
              {error.details?.suggested_action && (
                <p className="suggestion">💡 {error.details.suggested_action}</p>
              )}
            </div>
          </div>
        )}

        {/* Success Result */}
        {result?.success && result.expense && (
          <div className="result-container">
            <div className="alert alert-success">
              <CheckCircle size={20} />
              <span>Receipt processed successfully!</span>
            </div>

            <div className="extracted-data">
              <h4>Extracted Information</h4>
              <div className="data-grid">
                <div className="data-item">
                  <label>Merchant</label>
                  <span>{result.expense.merchant}</span>
                </div>
                <div className="data-item">
                  <label>Amount</label>
                  <span className="amount">₹{result.expense.amount.toFixed(2)}</span>
                </div>
                <div className="data-item">
                  <label>Confidence</label>
                  <span className="confidence">{(result.expense.ocr_confidence * 100).toFixed(0)}%</span>
                </div>
                <div className="data-item">
                  <label>Category</label>
                  <span className="badge">{result.expense.category || 'Other'}</span>
                </div>
              </div>
              {result.expense.requires_review && (
                <div className="alert alert-warning">
                  <AlertCircle size={18} />
                  <span>Review recommended - low confidence</span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Processing Failed */}
        {result && !result.success && (
          <div className="result-container">
            <div className="alert alert-error">
              <AlertCircle size={20} />
              <span>{result.message || 'Processing failed'}</span>
            </div>
            <p className="progress-hint">Try a clearer image or manual entry.</p>
          </div>
        )}

        {/* Tips Card */}
        <div className="card tips-card">
          <h4>💡 Tips for Best Results</h4>
          <ul>
            <li>Good lighting, flat receipt</li>
            <li>No glare or shadows</li>
            <li>Entire receipt visible</li>
            <li>High resolution image</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

export default UploadPage

