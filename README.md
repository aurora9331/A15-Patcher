# A15 Patcher Modern Web UI

## Kurulum

### Backend (Flask)
```
bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

### Frontend (Vite + React)
```
bash
cd frontend
npm install
npm run dev
```

### Kullanım
- Flask backend çalışıyorken `npm run dev` ile frontend başlatılır.
- localhost:5173 üzerinden modern yükleyici arayüzü açılır.
- Dosya yükleyince backend/uploads klasörüne kaydedilir.

---

Bu temel yapıdır; ek geliştirme veya tasarım/işlev isteğin olursa belirtmen yeterli!