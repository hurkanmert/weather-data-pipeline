import argparse
from collectors.wyoming_collector import WyomingCollector
from collectors.openmeteo_collector import OpenMeteoCollector
from visualizers.map_visualizer import TurkeyMapVisualizer
from utils.logger import get_logger, cleanup_old_logs

logger = get_logger("main")


def run_wyoming(args):
    logger.info("Starting Wyoming sounding data collection...")
    collector = WyomingCollector(
        station_id=args.station or 17095,
        region="mideast",
        altitude_target=3170
    )
    data = collector.fetch()

    print(f"\n{'='*40}")
    print(f"  Date     : {data['date']}")
    print(f"  PWV      : {data['pwv']} mm")
    print(f"  Station  : {data['station_id']}")
    if data['target_altitude']:
        print(f"  Altitude : {data['target_altitude'].get('height')} m")
        print(f"  Temp     : {data['target_altitude'].get('temperature')} °C")
        print(f"  Humidity : {data['target_altitude'].get('rel_humidity')} %")
    print(f"{'='*40}\n")

    if args.plot:
        viz = TurkeyMapVisualizer(output_dir="output")
        profile_path = viz.plot_sounding_profile(
            data["full_profile"],
            station_id=data["station_id"],
            date_str=data["date"]
        )
        print(f"Profile plot: {profile_path}")

        pwv_path = viz.plot_pwv(
            dag_pwv=data["pwv"],
            tug_pwv=0.0,
            date_str=data["date"]
        )
        print(f"PWV map: {pwv_path}")


def run_openmeteo(args):
    logger.info(f"Fetching Open-Meteo data for station: {args.station}")
    collector = OpenMeteoCollector()

    if args.historical:
        data = collector.fetch_historical(
            station_key=args.station,
            start_date=args.start,
            end_date=args.end
        )
        print(f"\n--- Historical Data: {data['station']['name']} ---")
        print(f"  Period : {data['start_date']} → {data['end_date']}")
        print(f"  Hourly rows : {len(data['hourly'])}")
        print(f"  Daily rows  : {len(data['daily'])}")
    else:
        data = collector.fetch_current(args.station)
        summary = collector.get_summary(data)
        print(f"\n--- Current Conditions: {summary['station']} ---")
        for k, v in summary.items():
            print(f"  {k:12}: {v}")

    if args.plot:
        viz = TurkeyMapVisualizer(output_dir="output")
        hourly = data["hourly"]
        path = viz.plot_temperature_series(
            hourly.rename(columns={
                "temperature_2m": "air_temp_ave",
                "relative_humidity_2m": "rel_hum_ave",
            }),
            title=f"{data['station']['name']} — Temperature & Humidity"
        )
        print(f"Plot saved: {path}")


def run_visualize(args):
    viz = TurkeyMapVisualizer(output_dir="output", dpi=150)
    output = viz.plot_pwv(dag_pwv=15.3, tug_pwv=12.8)
    print(f"Map saved: {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Weather Data Pipeline — Meteorological data collection & visualization"
    )
    subparsers = parser.add_subparsers(dest="command")

    # Wyoming command
    wy = subparsers.add_parser("wyoming", help="Fetch atmospheric sounding data")
    wy.add_argument("--station", type=int, default=17095)
    wy.add_argument("--plot", action="store_true")

    # Open-Meteo command
    om = subparsers.add_parser("openmeteo", help="Fetch weather data from Open-Meteo")
    om.add_argument("--station", type=str, default="DAG",
                    choices=["DAG", "TUG", "ISTANBUL", "ANKARA", "ERZURUM"])
    om.add_argument("--historical", action="store_true")
    om.add_argument("--start", type=str, default=None)
    om.add_argument("--end", type=str, default=None)
    om.add_argument("--plot", action="store_true")

    # Visualize command
    vis = subparsers.add_parser("visualize", help="Generate test visualizations")

    args = parser.parse_args()
    cleanup_old_logs()

    if args.command == "wyoming":
        run_wyoming(args)
    elif args.command == "openmeteo":
        run_openmeteo(args)
    elif args.command == "visualize":
        run_visualize(args)
    else:
        parser.print_help()