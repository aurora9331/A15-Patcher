import React, { useState } from 'react'

function UploadForm() {
  const [file, setFile] = useState(null)
  const [name, setName] = useState('')
  const [desc, setDesc] = useState('')
  const [status, setStatus] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setStatus("Yükleniyor...")
    const formData = new FormData()
    formData.append('file', file)
    formData.append('name', name)
    formData.append('desc', desc)
    try {
      const res = await fetch('/api/upload', {
        method: 'POST',
        body: formData
      })
      if (res.ok) {
        setStatus("Başarıyla yüklendi!")
      } else {
        setStatus("Yükleme hatası!")
      }
    } catch {
      setStatus("Sunucuya ulaşılamadı!")
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label>Dosya: </label>
        <input type="file" accept=".jar" onChange={e => setFile(e.target.files[0])} required />
      </div>
      <div>
        <label>İsim: </label>
        <input type="text" value={name} onChange={e => setName(e.target.value)} required />
      </div>
      <div>
        <label>Açıklama: </label>
        <input type="text" value={desc} onChange={e => setDesc(e.target.value)} />
      </div>
      <button type="submit">Yükle</button>
      <div style={{ marginTop: 10 }}>{status}</div>
    </form>
  )
}

export default UploadForm
