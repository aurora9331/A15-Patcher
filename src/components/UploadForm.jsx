import React, { useState } from 'react'

const UploadForm = ({ onUploadSuccess }) => {
  const [formData, setFormData] = useState({
    file: null,
    deviceName: '',
    deviceVersion: '',
    patchType: 'framework'
  })
  const [uploading, setUploading] = useState(false)
  const [status, setStatus] = useState({ message: '', type: '' })

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleFileChange = (e) => {
    const file = e.target.files[0]
    setFormData(prev => ({
      ...prev,
      file
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!formData.file) {
      setStatus({ message: 'Please select a file to upload', type: 'error' })
      return
    }

    if (!formData.deviceName || !formData.deviceVersion) {
      setStatus({ message: 'Please fill in device name and version', type: 'error' })
      return
    }

    setUploading(true)
    setStatus({ message: 'Uploading and processing file...', type: 'info' })

    const formDataToSend = new FormData()
    formDataToSend.append('file', formData.file)
    formDataToSend.append('deviceName', formData.deviceName)
    formDataToSend.append('deviceVersion', formData.deviceVersion)
    formDataToSend.append('patchType', formData.patchType)

    try {
      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formDataToSend
      })

      const result = await response.json()

      if (response.ok) {
        setStatus({ message: 'File uploaded and patched successfully!', type: 'success' })
        if (onUploadSuccess) {
          onUploadSuccess({
            filename: formData.file.name,
            deviceName: formData.deviceName,
            deviceVersion: formData.deviceVersion,
            patchType: formData.patchType,
            uploadTime: new Date().toISOString(),
            downloadUrl: result.downloadUrl
          })
        }
        // Reset form
        setFormData({
          file: null,
          deviceName: '',
          deviceVersion: '',
          patchType: 'framework'
        })
        // Reset file input
        e.target.reset()
      } else {
        setStatus({ message: result.error || 'Upload failed', type: 'error' })
      }
    } catch (error) {
      console.error('Upload error:', error)
      setStatus({ message: 'Network error occurred', type: 'error' })
    } finally {
      setUploading(false)
    }
  }

  return (
    <form className="upload-form" onSubmit={handleSubmit}>
      <h2>📤 Upload Framework Files</h2>
      
      <div className="form-group">
        <label htmlFor="file">Select Framework File (.jar)</label>
        <input
          type="file"
          id="file"
          name="file"
          accept=".jar,.zip"
          onChange={handleFileChange}
          className="file-input"
          required
        />
        {formData.file && (
          <p style={{ marginTop: '0.5rem', opacity: 0.8 }}>
            Selected: {formData.file.name} ({(formData.file.size / 1024 / 1024).toFixed(2)} MB)
          </p>
        )}
      </div>

      <div className="form-group">
        <label htmlFor="deviceName">Device Name</label>
        <input
          type="text"
          id="deviceName"
          name="deviceName"
          value={formData.deviceName}
          onChange={handleInputChange}
          placeholder="e.g., Xiaomi 14 Pro"
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="deviceVersion">Device Version</label>
        <input
          type="text"
          id="deviceVersion"
          name="deviceVersion"
          value={formData.deviceVersion}
          onChange={handleInputChange}
          placeholder="e.g., HyperOS 2.0, HyperOS 2.1"
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="patchType">Patch Type</label>
        <select
          id="patchType"
          name="patchType"
          value={formData.patchType}
          onChange={handleInputChange}
        >
          <option value="framework">Framework</option>
          <option value="services">Services</option>
          <option value="miui-services">MIUI Services</option>
        </select>
      </div>

      <button 
        type="submit" 
        className="upload-button"
        disabled={uploading}
      >
        {uploading ? '🔄 Processing...' : '🚀 Upload & Patch'}
      </button>

      {status.message && (
        <div className={`status-message status-${status.type}`}>
          {status.message}
        </div>
      )}
    </form>
  )
}

export default UploadForm