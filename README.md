# 🌤️ Weather Data Pipeline

Meteorolojik veri toplama, işleme ve görselleştirme pipeline'ı.
Wyoming Üniversitesi radiosonde verileri ve Open-Meteo API'si kullanılarak
Türkiye genelinde atmosferik analiz ve harita görselleştirmesi yapılmaktadır.

---

## 🚀 Özellikler

- 🔭 **Wyoming Radiosonde** — Erzurum (İstasyon 17095) atmosferik sondaj verisi
- 🌡️ **Open-Meteo** — Türkiye geneli gerçek zamanlı ve tarihsel hava verisi
- 🗺️ **Türkiye Haritası** — Cartopy ile meteorolojik parametre görselleştirmesi
- 📊 **Zaman Serisi** — Sıcaklık, nem, rüzgar trend grafikleri
- 📁 **Otomatik kayıt** — CSV çıktıları ve log yönetimi

---

## 🏔️ İstasyonlar

| Kod | İstasyon | Enlem | Boylam | İrtifa |
|-----|----------|-------|--------|--------|
| DAG | DAG Gözlemevi, Erzurum | 39.78°N | 41.23°E | 3170 m |
| TUG | TUG Gözlemevi, Antalya | 36.82°N | 30.34°E | 2547 m |
| ISTANBUL | İstanbul | 41.01°N | 28.98°E | 100 m |
| ANKARA | Ankara | 39.93°N | 32.86°E | 938 m |
| ERZURUM | Erzurum | 39.90°N | 41.27°E | 1869 m |

---

## ⚙️ Kurulum

```bash
git clone https://github.com/hurkanmert/weather-data-pipeline.git
cd weather-data-pipeline
pip install -r requirements.txt
```

---

## 💻 Kullanım

### Wyoming Radiosonde Verisi
```bash
# Veri çek
python main.py wyoming

# Veri çek + grafik oluştur
python main.py wyoming --plot
```

### Open-Meteo Hava Verisi
```bash
# Güncel veri
python main.py openmeteo --station DAG

# Güncel veri + grafik
python main.py openmeteo --station DAG --plot

# Tarihsel veri (son 30 gün)
python main.py openmeteo --station ERZURUM --historical

# Tarih aralığı belirle
python main.py openmeteo --station ISTANBUL --historical --start 2026-01-01 --end 2026-03-01

# Tüm istasyonlar
python main.py openmeteo --station ANKARA --plot
```

---

## 📊 Örnek Çıktılar

### Atmosferik Sondaj Profili
Sıcaklık, çiy noktası, rüzgar hızı ve nem değerlerinin basınç seviyesine göre dikey dağılımı.

### PWV Haritası
Türkiye haritası üzerinde DAG ve TUG gözlemevlerinde ölçülen
Precipitable Water Vapor (PWV) değerleri.

### Sıcaklık & Nem Serisi
Seçilen istasyon için saatlik sıcaklık ve bağıl nem zaman serisi grafikleri.

---

## 🏗️ Proje Yapısı
weather-data-pipeline/
├── collectors/
│   ├── wyoming_collector.py    # Wyoming Üniversitesi radiosonde API
│   └── openmeteo_collector.py  # Open-Meteo hava verisi API
├── visualizers/
│   └── map_visualizer.py       # Cartopy harita + grafik görselleştirme
├── utils/
│   ├── logger.py               # Log yönetimi
│   └── db_handler.py           # Veritabanı bağlantısı (MySQL)
├── config/
│   ├── config.yaml             # Yapılandırma dosyası
│   └── .env.example            # Ortam değişkenleri örneği
├── data/                       # Ham veri (CSV)
├── output/                     # Üretilen görseller
├── logs/                       # Log dosyaları
└── main.py                     # Ana giriş noktası

---

## 🛠️ Teknolojiler

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)
![Cartopy](https://img.shields.io/badge/Cartopy-0.22-green)
![Pandas](https://img.shields.io/badge/Pandas-2.x-blue)
![Matplotlib](https://img.shields.io/badge/Matplotlib-3.9-orange)
![OpenMeteo](https://img.shields.io/badge/Open--Meteo-API-brightgreen)

---

## 📄 Lisans

MIT License