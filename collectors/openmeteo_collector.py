import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
from pathlib import Path
from datetime import datetime, timedelta
from utils.logger import get_logger

logger = get_logger("openmeteo_collector")

# Observatory coordinates
STATIONS = {
    "DAG": {"lat": 39.780950, "lon": 41.226446, "altitude": 3170, "name": "DAG Observatory, Erzurum"},
    "TUG": {"lat": 36.824305, "lon": 30.335311, "altitude": 2547, "name": "TUG Observatory, Antalya"},
    "ISTANBUL": {"lat": 41.0082, "lon": 28.9784, "altitude": 100, "name": "Istanbul"},
    "ANKARA": {"lat": 39.9334, "lon": 32.8597, "altitude": 938, "name": "Ankara"},
    "ERZURUM": {"lat": 39.9000, "lon": 41.2700, "altitude": 1869, "name": "Erzurum"},
}

HOURLY_VARIABLES = [
    "temperature_2m",
    "relative_humidity_2m",
    "dew_point_2m",
    "precipitation",
    "pressure_msl",
    "surface_pressure",
    "wind_speed_10m",
    "wind_direction_10m",
    "cloud_cover",
    "visibility",
]

DAILY_VARIABLES = [
    "temperature_2m_max",
    "temperature_2m_min",
    "temperature_2m_mean",
    "precipitation_sum",
    "wind_speed_10m_max",
    "sunrise",
    "sunset",
]


class OpenMeteoCollector:
    """
    Open-Meteo API collector for meteorological data.
    No API key required. Supports historical and forecast data.
    
    Stations include DAG and TUG observatories used in
    original atmospheric monitoring system.
    """

    BASE_URL = "https://api.open-meteo.com/v1/forecast"
    ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"

    def __init__(self, data_dir: str = "data", cache_expire: int = 3600):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Setup cached session with retry
        cache_session = requests_cache.CachedSession(
            str(self.data_dir / ".weather_cache"),
            expire_after=cache_expire
        )
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        self.client = openmeteo_requests.Client(session=retry_session)

    def fetch_current(self, station_key: str = "DAG") -> dict:
        """
        Fetch current + 7-day forecast for a station.
        Returns hourly data as DataFrame.
        """
        station = STATIONS.get(station_key)
        if not station:
            raise ValueError(f"Unknown station: {station_key}. "
                             f"Available: {list(STATIONS.keys())}")

        logger.info(f"Fetching current data for {station['name']}...")

        params = {
            "latitude": station["lat"],
            "longitude": station["lon"],
            "hourly": HOURLY_VARIABLES,
            "daily": DAILY_VARIABLES,
            "timezone": "UTC",
            "forecast_days": 7,
        }

        try:
            responses = self.client.weather_api(self.BASE_URL, params=params)
            response = responses[0]
            logger.info(f"Data fetched for {station['name']} "
                        f"({response.Latitude():.2f}N, {response.Longitude():.2f}E)")
        except Exception as e:
            logger.error(f"Fetch failed: {e}")
            raise

        hourly = self._parse_hourly(response)
        daily = self._parse_daily(response)

        self._save(hourly, f"current_hourly_{station_key}_{datetime.utcnow().strftime('%Y%m%d')}.csv")
        self._save(daily, f"current_daily_{station_key}_{datetime.utcnow().strftime('%Y%m%d')}.csv")

        return {
            "station": station,
            "station_key": station_key,
            "hourly": hourly,
            "daily": daily,
            "fetched_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        }

    def fetch_historical(self, station_key: str = "DAG",
                          start_date: str = None,
                          end_date: str = None) -> dict:
        """
        Fetch historical data for a station.
        Default: last 30 days.
        
        Args:
            station_key: Station identifier (DAG, TUG, ISTANBUL, etc.)
            start_date: Format YYYY-MM-DD (default: 30 days ago)
            end_date: Format YYYY-MM-DD (default: today)
        """
        station = STATIONS.get(station_key)
        if not station:
            raise ValueError(f"Unknown station: {station_key}")

        if not start_date:
            start_date = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d")
        if not end_date:
            end_date = datetime.utcnow().strftime("%Y-%m-%d")

        logger.info(f"Fetching historical data for {station['name']} "
                    f"({start_date} → {end_date})...")

        params = {
            "latitude": station["lat"],
            "longitude": station["lon"],
            "start_date": start_date,
            "end_date": end_date,
            "hourly": HOURLY_VARIABLES,
            "daily": DAILY_VARIABLES,
            "timezone": "UTC",
        }

        try:
            responses = self.client.weather_api(self.ARCHIVE_URL, params=params)
            response = responses[0]
            logger.info(f"Historical data fetched: {start_date} → {end_date}")
        except Exception as e:
            logger.error(f"Historical fetch failed: {e}")
            raise

        hourly = self._parse_hourly(response)
        daily = self._parse_daily(response)

        filename_base = f"historical_{station_key}_{start_date}_{end_date}"
        self._save(hourly, f"{filename_base}_hourly.csv")
        self._save(daily, f"{filename_base}_daily.csv")

        return {
            "station": station,
            "station_key": station_key,
            "start_date": start_date,
            "end_date": end_date,
            "hourly": hourly,
            "daily": daily,
        }

    def fetch_all_stations(self, mode: str = "current") -> dict:
        """Fetch data for all defined stations."""
        results = {}
        for key in STATIONS:
            try:
                if mode == "historical":
                    results[key] = self.fetch_historical(key)
                else:
                    results[key] = self.fetch_current(key)
                logger.info(f"✓ {key} done.")
            except Exception as e:
                logger.error(f"✗ {key} failed: {e}")
        return results

    def _parse_hourly(self, response) -> pd.DataFrame:
        """Parse hourly response into DataFrame."""
        hourly = response.Hourly()
        hourly_data = {
            "date": pd.date_range(
                start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=hourly.Interval()),
                inclusive="left"
            )
        }
        for i, var in enumerate(HOURLY_VARIABLES):
            hourly_data[var] = hourly.Variables(i).ValuesAsNumpy()

        return pd.DataFrame(hourly_data)

    def _parse_daily(self, response) -> pd.DataFrame:
        """Parse daily response into DataFrame."""
        daily = response.Daily()
        daily_data = {
            "date": pd.date_range(
                start=pd.to_datetime(daily.Time(), unit="s", utc=True),
                end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=daily.Interval()),
                inclusive="left"
            )
        }
        for i, var in enumerate(DAILY_VARIABLES):
            try:
                daily_data[var] = daily.Variables(i).ValuesAsNumpy()
            except Exception:
                daily_data[var] = None

        return pd.DataFrame(daily_data)

    def _save(self, df: pd.DataFrame, filename: str):
        """Save DataFrame to CSV."""
        path = self.data_dir / filename
        df.to_csv(path, index=False)
        logger.info(f"Saved: {path}")

    def get_summary(self, data: dict) -> dict:
        """Return current conditions summary."""
        hourly = data["hourly"]
        now_idx = 0

        summary = {
            "station": data["station"]["name"],
            "fetched_at": data.get("fetched_at", ""),
            "temperature": f"{hourly['temperature_2m'].iloc[now_idx]:.1f} °C",
            "humidity": f"{hourly['relative_humidity_2m'].iloc[now_idx]:.0f} %",
            "pressure": f"{hourly['pressure_msl'].iloc[now_idx]:.1f} hPa",
            "wind_speed": f"{hourly['wind_speed_10m'].iloc[now_idx]:.1f} km/h",
            "wind_dir": f"{hourly['wind_direction_10m'].iloc[now_idx]:.0f} °",
            "cloud_cover": f"{hourly['cloud_cover'].iloc[now_idx]:.0f} %",
            "visibility": f"{hourly['visibility'].iloc[now_idx]:.0f} m",
        }
        return summary


if __name__ == "__main__":
    collector = OpenMeteoCollector()

    print("\n--- Current Conditions: DAG Observatory ---")
    data = collector.fetch_current("DAG")
    summary = collector.get_summary(data)
    for k, v in summary.items():
        print(f"  {k:12}: {v}")

    print("\n--- Historical 30 days: Erzurum ---")
    hist = collector.fetch_historical("ERZURUM")
    print(f"  Rows: {len(hist['hourly'])}")
    print(f"  Columns: {list(hist['hourly'].columns)}")