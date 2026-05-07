import argparse
import csv
import logging
import math
import random
import statistics
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from parseFiles import parse_metadata
from anomalyDetection import detect_anomalies


def _setup_logging():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        fmt='%(asctime)s  %(levelname)-8s  %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.addFilter(lambda record: record.levelno <= logging.WARNING)
    stdout_handler.setFormatter(formatter)

    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.ERROR)
    stderr_handler.setFormatter(formatter)

    logger.addHandler(stdout_handler)
    logger.addHandler(stderr_handler)

    return logger


logger = _setup_logging()


VALID_MEASURES = [
    "As(PM10)", "BaA(PM10)", "BaP(PM10)", "BbF(PM10)", "BjF(PM10)", "BkF(PM10)",
    "C6H6", "Cd(PM10)", "CO", "DBahA(PM10)",
    "As(cdepoz)", "BaA(cdepoz)", "BaP(cdepoz)", "BbF(cdepoz)", "BjF(cdepoz)",
    "BkF(cdepoz)", "Cd(cdepoz)", "DBahA(cdepoz)", "Hg(cdepoz)", "IP(cdepoz)", "Ni(cdepoz)",
    "formaldehyd", "Hg(TGM)", "IP(PM10)",
    "Ca2+(PM2.5)", "Cl_(PM2.5)", "EC(PM2.5)", "K+(PM2.5)", "Mg2+(PM2.5)", "Na+(PM2.5)",
    "NH4+(PM2.5)", "NO3_(PM2.5)", "OC(PM2.5)", "SO42_(PM2.5)",
    "Ni(PM10)", "NO2", "NO", "NOx", "O3", "Pb(PM10)", "PM10", "PM25",
    "SO2", "Depozycja", "Jony_PM25", "PrekursoryZielonka",
]

VALID_FREQUENCIES = ["1g", "24g", "1m"]


def validate_date(date_string):
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return date_string
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid date format: {date_string}")


def validate_measure(measure_string):
    if measure_string not in VALID_MEASURES:
        raise argparse.ArgumentTypeError(
            f"Invalid measure: '{measure_string}'.\n"
            f"Valid measures are: {', '.join(VALID_MEASURES)}"
        )
    return measure_string


def validate_freq(freq_string):
    if freq_string not in VALID_FREQUENCIES:
        raise argparse.ArgumentTypeError(
            f"Invalid frequency: '{freq_string}'. "
            f"Valid frequencies are: {', '.join(VALID_FREQUENCIES)}"
        )
    return freq_string


def load_measurements(file_path, start_date, end_date, measure, station_code=None):
    measurements = []

    logger.info("Opening file: %s", file_path)

    with open(file_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.reader(f, delimiter=',')

        next(reader)
        header_kody_stacji = next(reader)
        header_wskazniki = next(reader)
        next(reader)
        next(reader)
        next(reader)

        if measure not in header_wskazniki:
            logger.warning(
                "Measure '%s' does not appear in any column of file '%s'.",
                measure, file_path,
            )

        if station_code is not None and station_code not in header_kody_stacji:
            logger.warning(
                "Station '%s' not found in data for measure='%s', freq='%s'.",
                station_code, measure, file_path,
            )
            logger.info("Closed file: %s  (0 data rows processed)", file_path)
            return measurements

        station_indices = [
            i for i in range(1, len(header_kody_stacji))
            if station_code is None or header_kody_stacji[i] == station_code
        ]

        rows_read = 0
        for row in reader:
            if not row or len(row) < 2:
                continue

            row_bytes = len(','.join(row).encode('utf-8'))
            logger.debug("Row %d read: %d bytes", rows_read + 1, row_bytes)
            rows_read += 1

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

    logger.info("Closed file: %s  (%d data rows processed)", file_path, rows_read)

    return measurements


def execute_random(stations, measurements, measure, freq):
    valid_stations = list(set(m[2] for m in measurements))

    if not valid_stations:
        logger.warning(
            "No measurements found for measure='%s', freq='%s'. Result list is empty.",
            measure, freq,
        )
        print("No measurements available for the given criteria.")
        return

    chosen_station = random.choice(valid_stations)
    station_info = stations.get(chosen_station, {})

    if not station_info:
        logger.warning(
            "Station '%s' appears in measurements but has no metadata entry.",
            chosen_station,
        )

    print(f"Station Code: {chosen_station}")
    print(f"Name: {station_info.get('name', 'Unknown')}")
    print(f"Address: {station_info.get('address', 'Unknown')}")


def execute_stats(station_code, measurements, measure, freq):
    station_vals = [m[1] for m in measurements if m[2] == station_code]

    if not station_vals:
        logger.warning(
            "No measurements found for station='%s' in the given date range.",
            station_code,
        )
        return

    mean_val = statistics.mean(station_vals)
    stdev_val = statistics.stdev(station_vals) if len(station_vals) > 1 else 0.0

    print(f"Station: {station_code}")
    print(f"Mean: {mean_val:.4f}")
    print(f"Standard Deviation: {stdev_val:.4f}")

def execute_anomaly(measurements, threshold_delta, alarm_limit, inv_val_limit, delta_limit):
    if not measurements:
        logger.warning("No measurements available for anomaly detection.")
        return

    anomalies = detect_anomalies(measurements, threshold_delta=threshold_delta, alarm_limit=alarm_limit, inv_val_limit=inv_val_limit, delta_limit=delta_limit)

    if not anomalies:
        logger.debug("No anomalies detected.")
        return

    for anomaly in anomalies:
        logger.warning(anomaly)

def execute_best_station(measurements):
    stations = defaultdict(list)
    for m in measurements:
        stations[m[2]].append(m[1])

    minmean = math.inf
    minstation = ""
    for key, m in stations.items():
        mean = statistics.mean(m)
        if minmean > mean:
            minmean = mean
            minstation = key

    print(minmean)
    print(minstation)

def main():
    parser = argparse.ArgumentParser(description="Air Quality Data CLI")

    parser.add_argument('--measure', type=validate_measure, required=True)
    parser.add_argument('--freq', type=validate_freq, required=True)
    parser.add_argument('--start', type=validate_date, required=True)
    parser.add_argument('--end', type=validate_date, required=True)

    subparsers = parser.add_subparsers(dest='command', required=True)

    subparsers.add_parser("best-station")

    subparsers.add_parser('random')

    stats_parser = subparsers.add_parser('stats')
    stats_parser.add_argument('--station', required=True)

    anomaly_parser = subparsers.add_parser('anomaly')
    anomaly_parser.add_argument('--station', default=None)
    anomaly_parser.add_argument('--threshold-delta', type=float, default=100.0)
    anomaly_parser.add_argument('--alarm-limit', type=float, default=500.0)
    anomaly_parser.add_argument('--inv-val-limit', type=int, default=1000)
    anomaly_parser.add_argument('--delta-limit', type=int, default=1000)
    args = parser.parse_args()

    year = args.start.split('-')[0]
    file_name = f"{year}_{args.measure}_{args.freq}.csv"
    file_path = Path('measurements') / file_name

    if not file_path.exists():
        logger.error(
            "Measurement file '%s' does not exist. Cannot continue without data.",
            file_name,
        )
        return

    logger.info("Opening metadata file: stacje.csv")
    raw_meta = parse_metadata('stacje.csv')
    logger.info("Closed metadata file: stacje.csv  (%d stations loaded)", len(raw_meta))

    stations_meta = {
        s.get('kodStacji'): {
            'name': s.get('miasto', ''),
            'address': s.get('adres', '')
        }
        for s in raw_meta if s.get('kodStacji')
    }
    if args.command == 'best-station':
        measurements = load_measurements(file_path, args.start, args.end, args.measure)
        execute_best_station(measurements)
    elif args.command == 'random':
        measurements = load_measurements(file_path, args.start, args.end, args.measure)
        execute_random(stations_meta, measurements, args.measure, args.freq)
    elif args.command == 'stats':
        measurements = load_measurements(file_path, args.start, args.end, args.measure, args.station)
        execute_stats(args.station, measurements, args.measure, args.freq)
    elif args.command == 'anomaly':
        measurements = load_measurements(file_path, args.start, args.end, args.measure, args.station)
        execute_anomaly(measurements, args.threshold_delta, args.alarm_limit, args.inv_val_limit, args.delta_limit)

if __name__ == "__main__":
    main()