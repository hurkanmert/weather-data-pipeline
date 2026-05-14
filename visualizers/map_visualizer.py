import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
import matplotlib.lines as mlines
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as shpreader
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from pathlib import Path
from datetime import datetime
from utils.logger import get_logger

logger = get_logger("map_visualizer")

plt.rcParams["axes.labelweight"] = "bold"
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = "Arial"


class TurkeyMapVisualizer:
    """
    Cartopy-based meteorological map visualizer for Turkey.
    Generates publication-quality maps for weather parameters.
    
    Original: DAG Observatory monitoring system, Erzurum
    Public version: Works with any lat/lon point data over Turkey.
    """

    TURKEY_EXTENT = [26, 45, 36, 42]  # [lon_min, lon_max, lat_min, lat_max]

    # Observatory locations
    STATIONS = {
        "DAG": {"lon": 41.226446, "lat": 39.780950, "marker": "o"},
        "TUG": {"lon": 30.335311, "lat": 36.824305, "marker": "v"},
    }

    def __init__(self, output_dir: str = "output", dpi: int = 300):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.dpi = dpi

    def _setup_map(self, figsize: tuple = (16, 13)) -> tuple:
        """Initialize figure and axes with Turkey extent."""
        fig = plt.figure(figsize=figsize)
        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.set_extent(self.TURKEY_EXTENT, crs=ccrs.PlateCarree())

        # Ocean mask
        ocean = cfeature.NaturalEarthFeature("physical", "ocean", "10m")
        ax.add_feature(ocean, edgecolor="gray", facecolor="lightblue", alpha=0.4)

        # Country borders
        shpfile = shpreader.natural_earth(
            resolution="10m", category="cultural", name="admin_0_countries"
        )
        reader = shpreader.Reader(shpfile)
        for country in reader.records():
            code = country.attributes["ADM0_A3"]
            if code not in ("TUR", "CYN", "CYP"):
                try:
                    geoms = list(country.geometry)
                except TypeError:
                    geoms = [country.geometry]
                ax.add_geometries(
                    geoms, ccrs.PlateCarree(),
                    facecolor="white", edgecolor="gray", linewidth=0.5
                )

        # Gridlines
        gl = ax.gridlines(
            crs=ccrs.PlateCarree(), draw_labels=True,
            linewidth=0.8, color="gray", alpha=0.4, linestyle="--"
        )
        gl.xlines = False
        gl.ylines = False
        gl.xlocator = mticker.FixedLocator([26, 30, 35, 40, 45])
        gl.ylocator = mticker.FixedLocator([36, 38, 40, 42])
        gl.xformatter = LONGITUDE_FORMATTER
        gl.yformatter = LATITUDE_FORMATTER

        # North arrow
        ax.annotate(
            "N", xy=(0.05, 0.20), xytext=(0.05, 0.11),
            color="gray",
            arrowprops=dict(facecolor="gray", width=3, headwidth=8, alpha=0.5),
            ha="center", va="center", fontsize=13,
            xycoords=ax.transAxes
        )

        return fig, ax

    def _add_stations(self, ax, station_values: dict = None):
        """Plot observatory stations with optional value labels."""
        handles = []
        for name, info in self.STATIONS.items():
            value = station_values.get(name, "") if station_values else ""
            label = f"{name}: {value}" if value != "" else name

            ax.plot(
                info["lon"], info["lat"],
                info["marker"],
                markersize=7,
                color="red",
                transform=ccrs.PlateCarree(),
                zorder=5
            )
            handle = mlines.Line2D(
                [], [], color="red",
                marker=info["marker"],
                linestyle="None",
                markersize=7,
                label=label
            )
            handles.append(handle)

        return handles

    def plot_pwv(self, dag_pwv: float, tug_pwv: float,
                 date_str: str = None) -> str:
        """
        Plot Precipitable Water Vapor (PWV) values for observatory stations.
        
        Args:
            dag_pwv: PWV value at DAG Observatory (mm)
            tug_pwv: PWV value at TUG Observatory (mm)
            date_str: Optional date string for title
        """
        fig, ax = self._setup_map()

        station_values = {"DAG": f"{dag_pwv} mm", "TUG": f"{tug_pwv} mm"}
        handles = self._add_stations(ax, station_values)

        title_date = date_str or datetime.utcnow().strftime("%Y-%m-%d %H:00 UTC")
        ax.set_title(
            f"Precipitable Water Vapor (PWV)\n{title_date}",
            fontsize=14, pad=20
        )

        ax.legend(
            handles=handles,
            prop={"size": 12},
            fancybox=True,
            framealpha=0.7,
            loc="lower right"
        )

        filename = f"PWV_{datetime.utcnow().strftime('%Y%m%d_%H%M')}.png"
        output_path = self.output_dir / filename
        plt.savefig(output_path, dpi=self.dpi, bbox_inches="tight")
        plt.clf()
        plt.close()

        logger.info(f"PWV map saved: {output_path}")
        return str(output_path)

    def plot_sounding_profile(self, df, station_id: int,
                               date_str: str = None) -> str:
        """
        Plot vertical atmospheric sounding profile (Skew-T style simplified).
        Temperature and dew point vs pressure level.
        """
        if df.empty:
            logger.warning("Empty dataframe, skipping profile plot.")
            return ""

        fig, axes = plt.subplots(1, 2, figsize=(14, 8))
        fig.suptitle(
            f"Atmospheric Sounding Profile — Station {station_id}\n"
            f"{date_str or datetime.utcnow().strftime('%Y-%m-%d %H:00 UTC')}",
            fontsize=14
        )

        # Temperature profile
        axes[0].plot(df["temperature"], df["pressure"], "r-o",
                     markersize=4, linewidth=1.5, label="Temperature")
        axes[0].plot(df["dew_point"], df["pressure"], "b--o",
                     markersize=4, linewidth=1.5, label="Dew Point")
        axes[0].set_xlabel("Temperature (°C)")
        axes[0].set_ylabel("Pressure (hPa)")
        axes[0].invert_yaxis()
        axes[0].grid(True, alpha=0.3)
        axes[0].legend()
        axes[0].set_title("Temperature & Dew Point")

        # Wind & humidity profile
        axes[1].barh(df["pressure"], df["wind_speed"],
                     color="steelblue", alpha=0.7, label="Wind Speed (kt)")
        ax2 = axes[1].twiny()
        ax2.plot(df["rel_humidity"], df["pressure"], "g-o",
                 markersize=4, linewidth=1.5, label="Rel. Humidity (%)")
        ax2.set_xlabel("Relative Humidity (%)", color="green")
        axes[1].set_xlabel("Wind Speed (kt)")
        axes[1].set_ylabel("Pressure (hPa)")
        axes[1].invert_yaxis()
        axes[1].grid(True, alpha=0.3)
        axes[1].set_title("Wind Speed & Humidity")

        plt.tight_layout()

        filename = f"SOUNDING_{station_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M')}.png"
        output_path = self.output_dir / filename
        plt.savefig(output_path, dpi=self.dpi, bbox_inches="tight")
        plt.clf()
        plt.close()

        logger.info(f"Sounding profile saved: {output_path}")
        return str(output_path)

    
    def plot_temperature_series(self, df, title: str = None) -> str:
        if df.empty:
            logger.warning("Empty dataframe, skipping time series plot.")
            return ""

        import pandas as pd
        df = df.copy()
        df["date"] = pd.to_datetime(df["date"])
        df["air_temp_ave"] = pd.to_numeric(df["air_temp_ave"], errors="coerce")
        df["rel_hum_ave"] = pd.to_numeric(df["rel_hum_ave"], errors="coerce")
        df = df.replace(-999999, float("nan"))

        fig, axes = plt.subplots(2, 1, figsize=(14, 8), sharex=True)
        fig.suptitle(title or "Weather Station — Temperature & Humidity", fontsize=14)

        axes[0].plot(df["date"], df["air_temp_ave"],
                    "r-", linewidth=1.5, label="Temperature")
        axes[0].set_ylabel("Temperature (°C)")
        axes[0].grid(True, alpha=0.3)
        axes[0].legend()

        axes[1].plot(df["date"], df["rel_hum_ave"],
                    "b-", linewidth=1.5, label="Relative Humidity")
        axes[1].set_ylabel("Relative Humidity (%)")
        axes[1].set_xlabel("Date (UTC)")
        axes[1].grid(True, alpha=0.3)
        axes[1].legend()

        plt.tight_layout()

        filename = f"SERIES_{datetime.utcnow().strftime('%Y%m%d_%H%M')}.png"
        output_path = self.output_dir / filename
        plt.savefig(output_path, dpi=self.dpi, bbox_inches="tight")
        plt.clf()
        plt.close()

        logger.info(f"Time series plot saved: {output_path}")
        return str(output_path)

if __name__ == "__main__":
    viz = TurkeyMapVisualizer(output_dir="output", dpi=150)

    # Test PWV map
    output = viz.plot_pwv(dag_pwv=15.3, tug_pwv=12.8,
                          date_str="2024-10-25 12:00 UTC")
    print(f"PWV map: {output}")