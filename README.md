# 🔧 A15 Framework Patcher - Web UI

Modern web arayüzü ile Android framework yamalama aracı. Bu proje, HyperOS cihazlarında APK korumasını kaldırmak ve sistem uygulamalarını özgürce yükleyebilmek için geliştirilmiştir.

## ✨ Özellikler

- **Modern Web Arayüzü**: React + Vite ile geliştirilmiş kullanıcı dostu arayüz
- **Sürükle-Bırak Upload**: Framework dosyalarını kolayca yükleyin
- **Otomatik Yamalama**: Framework, Services ve MIUI Services dosyalarını otomatik olarak yamalama
- **Dosya Geçmişi**: Yüklenen dosyaları takip etme ve yönetme
- **İndirme Yönetimi**: Yamalanan dosyaları kolayca indirme
- **Cihaz Bilgileri**: Cihaz adı ve sürüm bilgilerini saklama

## 🎯 Desteklenen Cihazlar

- ✅ HyperOS 2.0 (Global)
- ✅ HyperOS 2.1 (Global)
- ❌ Çin ROM'ları (test edilmemiştir)

## 🚀 Kurulum ve Çalıştırma

### Gereksinimler

- **Node.js** (v18 veya üstü)
- **Python** (3.8 veya üstü)
- **npm** veya **yarn**

### Frontend Kurulumu

```bash
# Bağımlılıkları yükle
npm install

# Geliştirme sunucusunu başlat
npm run dev

# Production build
npm run build
```

### Backend Kurulumu

```bash
# Python bağımlılıklarını yükle
pip install -r requirements.txt

# Flask sunucusunu başlat
cd backend
python app.py
```

### Docker ile Çalıştırma (Opsiyonel)

```bash
# TODO: Docker yapılandırması eklenecek
```

## 📁 Proje Yapısı

```
A15-Patcher/
├── src/                          # React frontend kaynakları
│   ├── components/               # React bileşenleri
│   │   ├── UploadForm.jsx       # Dosya yükleme formu
│   │   └── FileHistory.jsx     # Dosya geçmişi bileşeni
│   ├── App.jsx                  # Ana uygulama bileşeni
│   ├── App.css                  # Stil dosyaları
│   └── main.jsx                 # Giriş noktası
├── backend/                     # Flask backend
│   └── app.py                   # Flask API sunucusu
├── tools/                       # Yamalama araçları
│   ├── baksmali.jar
│   ├── smali.jar
│   └── *.sh scripts
├── framework_patch.py           # Framework yamalama modülü
├── services_patch.py            # Services yamalama modülü
├── miui-service_Patch.py       # MIUI services yamalama modülü
├── package.json                 # Frontend bağımlılıkları
├── vite.config.js              # Vite yapılandırması
├── requirements.txt             # Python bağımlılıkları
├── index.html                   # Ana HTML dosyası
└── README.md                    # Bu dosya
```

## 🔧 API Endpoints

### Upload Endpoint
```http
POST /api/upload
Content-Type: multipart/form-data

Parameters:
- file: Framework dosyası (.jar/.zip)
- deviceName: Cihaz adı
- deviceVersion: Cihaz sürümü
- patchType: Yama türü (framework/services/miui-services)
```

### History Endpoint
```http
GET /api/history
Response: JSON array of uploaded files
```

### Download Endpoint
```http
GET /api/download/<file_id>
Response: Yamalanan dosya
```

### Health Check
```http
GET /api/health
Response: Server durumu ve kullanılabilir yamalar
```

## 💻 Geliştirme

### Frontend Geliştirme

```bash
# Geliştirme sunucusunu başlat (port 3000)
npm run dev

# Kodları lint'le
npm run lint

# Production build'i test et
npm run preview
```

### Backend Geliştirme

```bash
# Debug modunda başlat
FLASK_DEBUG=true python backend/app.py

# Logs'ları takip et
tail -f *.log
```

### Proxy Yapılandırması

Frontend geliştirme sunucusu, `/api` isteklerini otomatik olarak `http://localhost:5000` adresindeki Flask sunucusuna yönlendirir.

## 🛠️ Yamalama Süreci

1. **Dosya Yükleme**: Kullanıcı framework/services dosyasını yükler
2. **Validasyon**: Dosya türü ve boyutu kontrol edilir
3. **Yamalama**: Seçilen modül ile dosya yamalanır
4. **Kayıt**: İşlem geçmişe kaydedilir
5. **İndirme**: Yamalanan dosya indirilmeye hazır hale gelir

## 🎨 UI/UX Özellikleri

- **Responsive Tasarım**: Tüm cihazlarda uyumlu
- **Drag & Drop**: Dosya yükleme için sürükle-bırak desteği
- **Real-time Status**: Yükleme ve işlem durumu gösterimi
- **Dark Theme**: Modern koyu tema
- **Progress Indicators**: İşlem ilerleme göstergeleri
- **Error Handling**: Kullanıcı dostu hata mesajları

## 🔒 Güvenlik

- **Dosya Türü Kontrolü**: Sadece .jar ve .zip dosyaları kabul edilir
- **Boyut Limiti**: Maksimum 100MB dosya boyutu
- **Secure Filename**: Güvenli dosya adı oluşturma
- **Path Sanitization**: Dizin geçişi saldırılarından korunma

## 🤝 Katkıda Bulunma

1. Projeyi fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## 📝 Lisans

Bu proje GNU General Public License v3.0 altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 🙏 Emeği Geçenler

- **[Xiaomi](https://xiaomi.com)** - HyperOS framework
- **[Google](https://google.com)** - Android framework
- **[CorePatch](https://github.com/LSPosed/CorePatch)** - Yamalama teknikleri
- **React Team** - Frontend framework
- **Flask Team** - Backend framework
- **Vite Team** - Modern build tools

## 📞 Destek

Sorunlar için [GitHub Issues](https://github.com/aurora9331/A15-Patcher/issues) kullanın.

## 🔄 Güncelleme Geçmişi

### v2.0.0 (Web UI)
- ✅ Modern React + Vite frontend
- ✅ Flask REST API backend
- ✅ Dosya yükleme ve geçmiş yönetimi
- ✅ Responsive web arayüzü
- ✅ Otomatik yamalama işlemi

### v1.x (CLI Version)
- ✅ Command line yamalama aracı
- ✅ Framework ve services desteği
- ✅ GitHub Actions entegrasyonu
