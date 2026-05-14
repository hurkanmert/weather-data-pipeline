# 🌤️ Weather Data Pipeline

A meteorological data collection, processing and visualization pipeline.
Atmospheric analysis and map visualization across Turkey using
University of Wyoming radiosonde data and the Open-Meteo API.

---

## 🚀 Features

- 🔭 **Wyoming Radiosonde** — Atmospheric sounding data from Erzurum (Station 17095)
- 🌡️ **Open-Meteo** — Real-time and historical weather data across Turkey
- 🗺️ **Turkey Map** — Meteorological parameter visualization with Cartopy
- 📊 **Time Series** — Temperature, humidity and wind trend charts
- 📁 **Auto-save** — CSV outputs and log management

---

## 🏔️ Stations

| Code | Station | Latitude | Longitude | Altitude |
|------|---------|----------|-----------|----------|
| DAG | DAG Observatory, Erzurum | 39.78°N | 41.23°E | 3170 m |
| TUG | TUG Observatory, Antalya | 36.82°N | 30.34°E | 2547 m |
| ISTANBUL | Istanbul | 41.01°N | 28.98°E | 100 m |
| ANKARA | Ankara | 39.93°N | 32.86°E | 938 m |
| ERZURUM | Erzurum | 39.90°N | 41.27°E | 1869 m |

---

## ⚙️ Installation

```bash
git clone https://github.com/hurkanmert/weather-data-pipeline.git
cd weather-data-pipeline
pip install -r requirements.txt
```

---

## 💻 Usage

### Wyoming Radiosonde Data
```bash
# Fetch data
python main.py wyoming

# Fetch data + generate plots
python main.py wyoming --plot
```

### Open-Meteo Weather Data
```bash
# Current conditions
python main.py openmeteo --station DAG

# Current conditions + plot
python main.py openmeteo --station DAG --plot

# Historical data (last 30 days)
python main.py openmeteo --station ERZURUM --historical

# Custom date range
python main.py openmeteo --station ISTANBUL --historical --start 2026-01-01 --end 2026-03-01

# Any station with plot
python main.py openmeteo --station ANKARA --plot
```

---

## 📊 Sample Outputs

### Atmospheric Sounding Profile
Vertical distribution of temperature, dew point, wind speed and humidity by pressure level.

### PWV Map
Precipitable Water Vapor (PWV) values measured at DAG and TUG observatories
overlaid on a Turkey map.

### Temperature & Humidity Series
Hourly temperature and relative humidity time series charts for the selected station.

---

## 🏗️ Project Structure

    weather-data-pipeline/
    ├── collectors/
    │   ├── wyoming_collector.py    # University of Wyoming radiosonde API
    │   └── openmeteo_collector.py  # Open-Meteo weather data API
    ├── visualizers/
    │   └── map_visualizer.py       # Cartopy map + chart visualization
    ├── utils/
    │   ├── logger.py               # Log management
    │   └── db_handler.py           # Database connection (MySQL)
    ├── config/
    │   ├── config.yaml             # Configuration file
    │   └── .env.example            # Environment variables example
    ├── data/                       # Raw data (CSV)
    ├── output/                     # Generated visuals
    ├── logs/                       # Log files
    └── main.py                     # Entry point

---

## 🛠️ Tech Stack

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)
![Cartopy](https://img.shields.io/badge/Cartopy-0.22-green)
![Pandas](https://img.shields.io/badge/Pandas-2.x-blue)
![Matplotlib](https://img.shields.io/badge/Matplotlib-3.9-orange)
![OpenMeteo](https://img.shields.io/badge/Open--Meteo-API-brightgreen)

---

## 📄 License

MIT License
