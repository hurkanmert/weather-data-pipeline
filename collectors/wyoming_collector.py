import requests
import pandas as pd
from datetime import datetime
from pathlib import Path
from utils.logger import get_logger

logger = get_logger("wyoming_collector")

BASE_URL = "https://weather.uwyo.edu/cgi-bin/sounding.py"


class WyomingCollector:
    """
    University of Wyoming Atmospheric Sounding Data Collector.
    Fetches radiosonde (balloon) data from public API.
    Station 17095 = Erzurum, Turkey (DAG Observatory region)
    """

    def __init__(self, station_id: int = 17095, region: str = "mideast",
                 altitude_target: int = 3170, data_dir: str = "data"):
        self.station_id = station_id
        self.region = region
        self.altitude_target = altitude_target
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def _build_url(self, year: str, month: str, day_hour: str) -> str:
        return (
            f"https://weather.uwyo.edu/cgi-bin/sounding?region={self.region}"
            f"&TYPE=TEXT%3ALIST&YEAR={year}&MONTH={month}"
            f"&FROM={day_hour}&TO={day_hour}&STNM={self.station_id}"
        )

    def _get_day_hour(self) -> tuple:
        now = datetime.utcnow()
        hour = "12" if now.hour >= 14 else "00"
        day_hour = now.strftime("%d") + hour
        return now.strftime("%Y"), now.strftime("%m"), day_hour, hour

    def _parse_sounding_data(self, lines: list) -> pd.DataFrame:
        """Parse raw sounding text into DataFrame."""
        columns = [
            "pressure", "height", "temperature", "dew_point",
            "rel_humidity", "mixing_ratio", "wind_dir", "wind_speed",
            "potential_temp", "equ_pot_temp", "virtual_pot_temp"
        ]

        data_start = False
        rows = []

        for line in lines:
            stripped = line.strip()

            if "---" in stripped and data_start is False:
                data_start = True
                continue

            if data_start:
                if stripped.startswith("<") or stripped == "" or "Station" in stripped:
                    break
                parts = stripped.split()
                if len(parts) >= 11:
                    try:
                        rows.append([float(x) for x in parts[:11]])
                    except ValueError:
                        continue

        if not rows:
            logger.warning("No data rows parsed from sounding.")
            return pd.DataFrame()

        df = pd.DataFrame(rows, columns=columns)
        logger.info(f"Parsed {len(df)} pressure levels.")
        return df

    def _extract_pwv(self, lines: list) -> float:
        """Extract Precipitable Water Vapor value."""
        for line in lines:
            if "Precipitable" in line:
                try:
                    return float(line.split(":")[1].strip().split()[0])
                except (IndexError, ValueError):
                    pass
        return -999.0

    def _find_target_altitude(self, df: pd.DataFrame) -> dict:
        """Find data row closest to target altitude (DAG Observatory = 3170m)."""
        if df.empty:
            return {}
        idx = (df["height"] - self.altitude_target).abs().idxmin()
        row = df.iloc[idx]
        logger.info(f"Closest altitude to {self.altitude_target}m: {row['height']}m")
        return row.to_dict()

    def fetch(self) -> dict:
        """Main method: fetch, parse and return sounding data."""
        year, month, day_hour, hour = self._get_day_hour()
        url = self._build_url(year, month, day_hour)

        logger.info(f"Fetching sounding data from: {url}")

        # Retry logic (same as original wyoming.py)
        for attempt in range(3):
            try:
                response = requests.get(url, verify=False, timeout=30)
                lines = response.text.splitlines()

                if any(line.startswith("Can't") or line.startswith("Sorry") 
                       for line in lines):
                    logger.warning(f"Data not available yet. Attempt {attempt+1}/3")
                    continue

                logger.info("Data fetched successfully.")
                break
            except Exception as e:
                logger.error(f"Fetch error (attempt {attempt+1}): {e}")
                if attempt == 2:
                    raise

        pwv = self._extract_pwv(lines)
        df = self._parse_sounding_data(lines)
        target = self._find_target_altitude(df)

        date_str = (f"{year}-{month}-{datetime.utcnow().strftime('%d')} "
                    f"{hour}:00:00")

        result = {
            "date": date_str,
            "pwv": pwv,
            "full_profile": df,
            "target_altitude": target,
            "station_id": self.station_id
        }

        # Save raw data
        output_file = self.data_dir / f"sounding_{year}{month}{day_hour}.csv"
        df.to_csv(output_file, index=False)
        logger.info(f"Data saved to {output_file}")

        return result


if __name__ == "__main__":
    collector = WyomingCollector(
        station_id=17095,
        region="mideast",
        altitude_target=3170
    )
    data = collector.fetch()
    print(f"\nDate: {data['date']}")
    print(f"PWV: {data['pwv']} mm")
    print(f"\nTarget altitude data:")
    for k, v in data['target_altitude'].items():
        print(f"  {k}: {v}")
    print(f"\nFull profile shape: {data['full_profile'].shape}")