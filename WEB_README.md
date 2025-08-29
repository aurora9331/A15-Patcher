# A15 Framework Patcher - Web Interface

Bu web arayüzü, A15 Framework Patcher aracının modern ve kullanıcı dostu bir sürümüdür. Flask tabanlı bu arayüz sayesinde Android framework dosyalarını kolayca yamalayabilirsiniz.

## Özellikler

- 🚀 **Modern Web Arayüzü**: Bootstrap ile tasarlanmış responsive ve kullanıcı dostu arayüz
- 📁 **Dosya Yükleme**: Sürükle-bırak desteği ile kolay JAR dosyası yükleme
- 🔧 **Otomatik Yamalama**: Framework, Services ve MIUI Services dosyalarını otomatik olarak yamalama
- 📊 **Geçmiş Takibi**: Yüklenen dosyaların geçmişini görüntüleme
- 💾 **Güvenli Depolama**: Yüklenen dosyalar ve meta veriler güvenli bir şekilde saklanır
- 📱 **Responsive Tasarım**: Mobil ve masaüstü cihazlarda mükemmel görünüm

## Kurulum

### Gereksinimler

- Python 3.7+
- Java 11+
- 7z
- Flask ve bağımlılıkları

### Kurulum Adımları

1. **Bağımlılıkları yükleyin:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Uygulamayı başlatın:**
   ```bash
   python app.py
   ```

3. **Web arayüzüne erişin:**
   Tarayıcınızda `http://localhost:5000` adresine gidin.

## Kullanım

### JAR Dosyası Yükleme

1. Ana sayfada "JAR Dosyası" alanına tıklayın veya dosyayı sürükleyin
2. Proje adı ve açıklama bilgilerini girin
3. "Dosyayı Yükle ve İşle" butonuna tıklayın
4. İşlem tamamlandığında yamalı dosyayı indirin

### Desteklenen Dosya Türleri

- **framework.jar**: Android framework yamaları
- **services.jar**: Android services yamaları  
- **miui-services.jar**: MIUI services yamaları

### Dosya Boyutu Limiti

- Maksimum dosya boyutu: 500MB
- Desteklenen format: .jar

## API Endpoints

- `GET /` - Ana sayfa
- `POST /upload` - Dosya yükleme
- `GET /history` - Yükleme geçmişi
- `GET /download/<filename>` - Dosya indirme
- `GET /api/status` - API durum kontrolü

## Güvenlik

- Dosya türü kontrolü (sadece .jar dosyaları)
- Dosya boyutu limiti
- Güvenli dosya adı oluşturma
- Temporary directory kullanımı

## Klasör Yapısı

```
├── app.py                 # Ana Flask uygulaması
├── requirements.txt       # Python bağımlılıkları
├── uploads/              # Yüklenen dosyalar
├── data.json            # Meta veri depolama
├── templates/           # HTML şablonları
│   ├── index.html       # Ana sayfa
│   ├── result.html      # Sonuç sayfası
│   └── history.html     # Geçmiş sayfası
├── static/              # Statik dosyalar
│   ├── css/
│   │   └── style.css    # Özel CSS stilleri
│   └── js/
│       └── script.js    # JavaScript fonksiyonları
└── tools/               # Patch araçları
    ├── baksmali.jar
    └── smali.jar
```

## Yamalama İşlemi

Uygulama aşağıdaki adımları otomatik olarak gerçekleştirir:

1. **Dosya Doğrulama**: Yüklenen dosyanın geçerli bir JAR olduğunu kontrol eder
2. **Tür Tespiti**: Framework, Services veya MIUI Services türünü belirler
3. **Çıkarma**: JAR dosyasını geçici dizine çıkarır
4. **DEX Decompile**: Gerekirse DEX dosyalarını Smali koduna çevirir
5. **Yamalama**: İlgili patch scriptini çalıştırır
6. **Yeniden Paketleme**: Yamalı dosyaları yeni JAR olarak paketler
7. **Temizlik**: Geçici dosyaları temizler

## Sorun Giderme

### Yaygın Hatalar

- **"Geçersiz JAR dosyası"**: Dosyanın geçerli bir Android JAR dosyası olduğundan emin olun
- **"DEX dosyası bulunamadı"**: Dosya Android framework dosyası olmayabilir
- **"İşlem başarısız"**: Java araçlarının doğru yüklendiğini kontrol edin

### Log Kontrolü

Uygulama çalışırken terminal çıktısını kontrol ederek detaylı hata bilgilerini görebilirsiniz.

## Katkıda Bulunma

Bu proje açık kaynaklıdır. Katkılarınızı bekliyoruz!

## Lisans

Bu proje GPL-3.0 lisansı altında lisanslanmıştır.