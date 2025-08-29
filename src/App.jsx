import React, { useState, useEffect } from 'react'
import UploadForm from './components/UploadForm'
import FileHistory from './components/FileHistory'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState('upload')
  const [uploadHistory, setUploadHistory] = useState([])

  useEffect(() => {
    // Fetch upload history on component mount
    fetchHistory()
  }, [])

  const fetchHistory = async () => {
    try {
      const response = await fetch('/api/history')
      if (response.ok) {
        const data = await response.json()
        setUploadHistory(data.files || [])
      }
    } catch (error) {
      console.error('Error fetching history:', error)
    }
  }

  const handleUploadSuccess = (fileInfo) => {
    // Add new file to history
    setUploadHistory(prev => [fileInfo, ...prev])
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>🔧 A15 Framework Patcher</h1>
        <p>Modern Web Interface for Android Framework Patching</p>
      </header>

      <nav className="app-nav">
        <button 
          className={`nav-button ${activeTab === 'upload' ? 'active' : ''}`}
          onClick={() => setActiveTab('upload')}
        >
          📤 Upload & Patch
        </button>
        <button 
          className={`nav-button ${activeTab === 'history' ? 'active' : ''}`}
          onClick={() => setActiveTab('history')}
        >
          📜 History
        </button>
      </nav>

      <main className="app-main">
        {activeTab === 'upload' && (
          <UploadForm onUploadSuccess={handleUploadSuccess} />
        )}
        {activeTab === 'history' && (
          <FileHistory 
            files={uploadHistory} 
            onRefresh={fetchHistory}
          />
        )}
      </main>

      <footer className="app-footer">
        <p>A15 Framework Patcher Web UI - Powered by React & Flask</p>
      </footer>
    </div>
  )
}

export default App