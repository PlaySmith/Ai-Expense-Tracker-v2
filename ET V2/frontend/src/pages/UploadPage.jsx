import React, { useState } from 'react';
import { Upload, Camera, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import { expenseAPI } from '../api/API';
import '../index.css';

function UploadPage() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);

  const handleFile = (e) => {
    const selected = e.target.files[0];
    setFile(selected);
    setPreview(URL.createObjectURL(selected));
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    try {
      const data = await expenseAPI.uploadReceipt(file);
      setResult(data);
    } finally { setUploading(false); }
  };

  return (
    <div className="glass" style={{ maxWidth: '600px', margin: '0 auto', padding: '3rem', textAlign: 'center' }}>
      <h2 style={{ marginBottom: '1rem' }}>Scan Receipt</h2>
      
      {!preview ? (
        <label style={{ border: '2px dashed var(--border)', padding: '4rem', borderRadius: '24px', display: 'block', cursor: 'pointer' }}>
          <input type="file" onChange={handleFile} style={{ display: 'none' }} />
          <Upload size={48} style={{ color: 'var(--accent)', marginBottom: '1rem' }} />
          <p>Drop receipt here or click to browse</p>
        </label>
      ) : (
        <div style={{ position: 'relative' }}>
          <img src={preview} alt="Preview" style={{ width: '100%', borderRadius: '20px', marginBottom: '2rem' }} />
          {!result && (
            <button className="btn btn-primary" onClick={handleUpload} disabled={uploading} style={{ width: '100%' }}>
              {uploading ? <Loader2 className="spin" /> : <Camera />} Analyze Receipt
            </button>
          )}
        </div>
      )}

      {result && result.success && (
        <div className="glass" style={{ marginTop: '2rem', background: 'rgba(34, 197, 94, 0.1)', padding: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
            <span style={{ color: 'var(--text-muted)' }}>Merchant</span>
            <span style={{ fontWeight: 700 }}>{result.expense.merchant}</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: 'var(--text-muted)' }}>Amount</span>
            <span style={{ fontSize: '1.5rem', fontWeight: 900, color: 'var(--accent)' }}>₹{result.expense.amount}</span>
          </div>
        </div>
      )}
    </div>
  );
}

export default UploadPage;