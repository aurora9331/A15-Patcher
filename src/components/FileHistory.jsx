import React from 'react'

const FileHistory = ({ files, onRefresh }) => {
  const handleDownload = (downloadUrl, filename) => {
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  const handleDelete = async (fileId) => {
    if (!confirm('Are you sure you want to delete this file?')) return

    try {
      const response = await fetch(`/api/files/${fileId}`, {
        method: 'DELETE'
      })

      if (response.ok) {
        onRefresh()
      } else {
        alert('Failed to delete file')
      }
    } catch (error) {
      console.error('Delete error:', error)
      alert('Network error occurred')
    }
  }

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString()
  }

  return (
    <div className="history-container">
      <div className="history-header">
        <h2>📜 Upload History</h2>
        <button className="refresh-button" onClick={onRefresh}>
          🔄 Refresh
        </button>
      </div>

      {files.length === 0 ? (
        <div className="empty-state">
          <p>📂</p>
          <p>No files uploaded yet</p>
          <p>Upload your first framework file to get started!</p>
        </div>
      ) : (
        <ul className="file-list">
          {files.map((file, index) => (
            <li key={file.id || index} className="file-item">
              <div className="file-info">
                <div className="file-details">
                  <h3>{file.filename}</h3>
                  <p><strong>Device:</strong> {file.deviceName}</p>
                  <p><strong>Version:</strong> {file.deviceVersion}</p>
                  <p><strong>Patch Type:</strong> {file.patchType}</p>
                  <p><strong>Upload Time:</strong> {formatDate(file.uploadTime)}</p>
                  {file.fileSize && (
                    <p><strong>Size:</strong> {formatFileSize(file.fileSize)}</p>
                  )}
                </div>
                <div className="file-actions">
                  {file.downloadUrl && (
                    <button
                      className="action-button"
                      onClick={() => handleDownload(file.downloadUrl, file.filename)}
                    >
                      📥 Download
                    </button>
                  )}
                  <button
                    className="action-button danger"
                    onClick={() => handleDelete(file.id)}
                  >
                    🗑️ Delete
                  </button>
                </div>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

export default FileHistory