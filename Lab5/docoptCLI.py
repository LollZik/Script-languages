"""Air Quality Data CLI

Usage:
  docoptCLI.py --measure=<measure> --freq=<freq> --start=<date> --end=<date> random
  docoptCLI.py --measure=<measure> --freq=<freq> --start=<date> --end=<date> stats --station=<station>
  docoptCLI.py (-h | --help)

Options:
  --measure=<measure>    Measured quantity (e.g. PM10, PM25, NO2).
  --freq=<freq>          Measurement frequency (1g, 24g, 1m).
  --start=<date>         Start date in YYYY-MM-DD format.
  --end=<date>           End date in YYYY-MM-DD format.
  --station=<station>    Station code (required for stats subcommand).
  -h --help              Show this help message.
"""

import csv
import random
import statistics
from datetime import datetime
from pathlib import Path

from docopt import docopt
from parseFiles import parse_metadata


VALID_MEASURES = [
    "As(PM10)", "BaA(PM10)", "BaP(PM10)", "BbF(PM10)", "BjF(PM10)", "BkF(PM10)",
    "C6H6", "Cd(PM10)", "CO", "DBahA(PM10)",
    "Hg(TGM)", "IP(PM10)", "Ni(PM10)", "NO2", "NO",
    "NOx", "O3", "Pb(PM10)", "PM10", "PM25", "SO2",
    "Depozycja","formaldehyd", "Jony_PM25", "PrekursoryZielonka",
]

VALID_FREQUENCIES = ["1g", "24g", "1m"]


def validate_date(date_string):
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
    except ValueError:
        raise SystemExit(f"Error: Invalid date format: '{date_string}'. Expected YYYY-MM-DD.")
    return date_string


def validate_measure(measure_string):
    if measure_string not in VALID_MEASURES:
        raise SystemExit(
            f"Error: Invalid measure: '{measure_string}'.\n"
            f"Valid measures are: {', '.join(VALID_MEASURES)}"
        )
    return measure_string


def validate_freq(freq_string):
    if freq_string not in VALID_FREQUENCIES:
        raise SystemExit(
            f"Error: Invalid frequency: '{freq_string}'. "
            f"Valid frequencies are: {', '.join(VALID_FREQUENCIES)}"
        )
    return freq_string


def load_measurements(file_path, start_date, end_date, station_code=None):
    measurements = []

    with open(file_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.reader(f, delimiter=',')

        next(reader)
        header_kody_stacji = next(reader)
        next(reader)
        next(reader)
        next(reader)
        next(reader)

        if station_code is not None and station_code not in header_kody_stacji:
            print(f"Error: Station '{station_code}' not found in data.")
            return measurements

        station_indices = [
            i for i in range(1, len(header_kody_stacji))
            if station_code is None or header_kody_stacji[i] == station_code
        ]

        for row in reader:
            if not row or len(row) < 2:
                continue

            date_time = row[0]
            date_only = date_time.split(' ')[0]

            if '/' in date_only:
                d, m, y = date_only.split('/')
                if len(y) == 2:
                    y = "20" + y
                date_only = f"{y}-{m}-{d}"

            if start_date <= date_only <= end_date:
                for i in station_indices:
                    val_str = row[i].strip()
                    if val_str:
                        measurements.append((date_time, float(val_str), header_kody_stacji[i]))

    return measurements


def execute_random(stations, measurements):
    valid_stations = list(set(m[2] for m in measurements))

    if not valid_stations:
        print("No measurements available for the given criteria.")
        return

    chosen_station = random.choice(valid_stations)
    station_info = stations.get(chosen_station, {})

    print(f"Station Code: {chosen_station}")
    print(f"Name: {station_info.get('name', 'Unknown')}")
    print(f"Address: {station_info.get('address', 'Unknown')}")


def execute_stats(station_code, measurements):
    station_vals = [m[1] for m in measurements if m[2] == station_code]

    if not station_vals:
        print("No measurements available for the given criteria.")
        return

    mean_val = statistics.mean(station_vals)
    stdev_val = statistics.stdev(station_vals) if len(station_vals) > 1 else 0.0

    print(f"Station: {station_code}")
    print(f"Mean: {mean_val:.4f}")
    print(f"Standard Deviation: {stdev_val:.4f}")


def main():
    args = docopt(__doc__)

    measure = validate_measure(args['--measure'])
    freq    = validate_freq(args['--freq'])
    start   = validate_date(args['--start'])
    end     = validate_date(args['--end'])

    year = start.split('-')[0]
    file_name = f"{year}_{measure}_{freq}.csv"
    file_path = Path('measurements') / file_name

    if not file_path.exists():
        raise SystemExit(f"Error: File '{file_name}' does not exist.")

    raw_meta = parse_metadata('stacje.csv')
    stations_meta = {
        s.get('kodStacji'): {
            'name': s.get('miasto', ''),
            'address': s.get('adres', '')
        }
        for s in raw_meta if s.get('kodStacji')
    }

    if args['random']:
        measurements = load_measurements(file_path, start, end)
        execute_random(stations_meta, measurements)
    elif args['stats']:
        measurements = load_measurements(file_path, start, end, args['--station'])
        execute_stats(args['--station'], measurements)


if __name__ == "__main__":
    main()
