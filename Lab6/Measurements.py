import csv
import datetime
import os
import sys
import re
from typing import Optional

from TimeSeries import TimeSeries
from SimpleReporter import SimpleReporter
from SeriesValidator import ThresholdDetector, OutlierDetector, ZeroSpikeDetector

ROW_STATION_CODE    = 1
ROW_PARAMETER       = 2
ROW_AVERAGING_TIME  = 3
ROW_UNIT            = 4
HEADER_ROWS         = 6


class SeriesKey:
    __slots__ = ('station_code', 'parameter', 'averaging_time')

    def __init__(self, station_code: str, parameter: str, averaging_time: str):
        self.station_code = station_code
        self.parameter = parameter
        self.averaging_time = averaging_time

    def __eq__(self, other):
        return (self.station_code, self.parameter, self.averaging_time) == \
               (other.station_code, other.parameter, other.averaging_time)

    def __hash__(self):
        return hash((self.station_code, self.parameter, self.averaging_time))

    def __repr__(self):
        return f"SeriesKey(station_code={self.station_code!r}, parameter={self.parameter!r}, avg_time={self.averaging_time!r})"


class ColumnMeta:
    __slots__ = ('file_path', 'col_index', 'key', 'unit')

    def __init__(self, file_path: str, col_index: int, key: SeriesKey, unit: str):
        self.file_path = file_path
        self.col_index = col_index
        self.key = key
        self.unit = unit


def parse_datetime(raw: str) -> Optional[datetime.datetime]:
    raw = raw.strip()
    if not raw:
        return None
    try:
        return datetime.datetime.strptime(raw, '%d/%m/%y %H:%M')
    except ValueError:
        return None


def parse_value(raw: str) -> Optional[float]:
    raw = raw.strip()
    if not raw:
        return None
    try:
        return float(raw)
    except ValueError:
        return None


class Measurements:
    def __init__(self, directory: str):
        if not os.path.isdir(directory):
            raise NotADirectoryError(f"Path is not a directory: {directory!r}")

        self.directory = directory
        self.registry: dict[SeriesKey, ColumnMeta] = {}
        self.loaded: dict[SeriesKey, TimeSeries] = {}
        self.loaded_files: set[str] = set()
        self.scan_headers()

    def scan_headers(self) -> None:
        # if file's name matches the regex, register the file
        for filename in sorted(os.listdir(self.directory)):
            if not re.match(r'^(\d{4})_(.+?)_(.+?)\.csv$', filename):
                continue
            file_path = os.path.join(self.directory, filename)
            self.register_file(file_path)

    def register_file(self, file_path: str) -> None:
        #Load only the first 6 header rows
        with open(file_path, encoding='utf-8', newline='') as f:
            reader = csv.reader(f)
            header_rows = [next(reader) for _ in range(HEADER_ROWS)]

        station_codes   = header_rows[ROW_STATION_CODE]
        parameters      = header_rows[ROW_PARAMETER]
        averaging_times = header_rows[ROW_AVERAGING_TIME]
        units           = header_rows[ROW_UNIT]

        # Get each column's info
        for col_index in range(1, len(station_codes)):
            station_code   = station_codes[col_index].strip()
            parameter      = parameters[col_index].strip()
            averaging_time = averaging_times[col_index].strip()
            unit           = units[col_index].strip()

            if not station_code:
                continue

            key = SeriesKey(station_code, parameter, averaging_time)
            # Ignore duplicates
            if key not in self.registry:
                self.registry[key] = ColumnMeta(file_path, col_index, key, unit)

    def load_file(self, file_path: str) -> None:
        if file_path in self.loaded_files:
            return

        # Make dictionary (dates[], values[]) for each station in file
        cols: list[ColumnMeta] = [meta for meta in self.registry.values() if meta.file_path == file_path]
        if not cols:
            self.loaded_files.add(file_path)
            return
        col_data: dict[int, tuple[list, list]] = {
            meta.col_index: ([], []) for meta in cols
        }

        with open(file_path, encoding='utf-8', newline='') as f:
            reader = csv.reader(f)
            for _ in range(HEADER_ROWS):
                next(reader)

            for row in reader:
                if not row:
                    continue
                dt = parse_datetime(row[0])
                if dt is None:
                    continue
                # Fill the dictionary
                for col_index, (dates, values) in col_data.items():
                    raw = row[col_index] if col_index < len(row) else ''
                    dates.append(dt)
                    values.append(parse_value(raw))

        # Create TimeSeries objects
        for meta in cols:
            dates, values = col_data[meta.col_index]
            ts = TimeSeries(
                parameter_name=meta.key.parameter,
                station_code=meta.key.station_code,
                averaging_time=meta.key.averaging_time,
                dates=dates,
                values=values,
                unit=meta.unit,
            )
            self.loaded[meta.key] = ts
        # Mark file as loaded
        self.loaded_files.add(file_path)

    def ensureloaded(self, key: SeriesKey) -> None:
        if key not in self.loaded and key in self.registry:
            self.load_file(self.registry[key].file_path)

    def preload_all(self) -> None:
        for meta in self.registry.values():
            if meta.file_path not in self.loaded_files:
                self.load_file(meta.file_path)

    def __len__(self) -> int:
        return len(self.registry)

    def __contains__(self, parameter_name: str) -> bool:
        return any(key.parameter == parameter_name for key in self.registry)

    def get_by_parameter(self, param_name: str) -> list[TimeSeries]:
        matching_keys = [key for key in self.registry if key.parameter == param_name]
        for key in matching_keys:
            self.ensureloaded(key)
        return [self.loaded[key] for key in matching_keys if key in self.loaded]

    def get_by_station(self, station_code: str) -> list[TimeSeries]:
        matching_keys = [key for key in self.registry if key.station_code == station_code]
        for key in matching_keys:
            self.ensureloaded(key)
        return [self.loaded[key] for key in matching_keys if key in self.loaded]

    def __repr__(self) -> str:
        return (f"Measurements(directory={self.directory!r}, "
                f"registered={len(self.registry)}, "
                f"loaded={len(self.loaded)})")

    def detect_all_anomalies(self, validators: list, preload: bool = False) -> dict[str, list[str]]:
        if preload:
            self.preload_all()

        results: dict[str, list[str]] = {}

        for ts in self.loaded.values():
            for validator in validators:
                messages = validator.analyze(ts)
                if messages:
                    validator_name = validator.__class__.__name__
                    key = f"{validator_name}/{ts.station_code}/{ts.parameter_name}"
                    results[key] = messages
        return results

if __name__ == "__main__":
    default = os.path.join(os.path.dirname(os.path.abspath(__file__)), "measurements")
    data_dir = sys.argv[1] if len(sys.argv) > 1 else default

    m = Measurements(data_dir)
    print(m)
    print(f"(__len__): {len(m)}")
    print()

    for param in ("PM10", "O3", "SO2", "benzen"):
        print(f"{param!r} in m: {param in m}")
    print()

    print("=== get_by_parameter('PM10') ===")
    pm10_series = m.get_by_parameter("PM10")
    for ts in pm10_series[:3]:
        mean_str = f"{ts.mean:.2f}" if ts.mean is not None else "N/A"
        print(f"  {ts.station_code} | {ts.parameter_name} | mean={mean_str}")
    print(f"{len(pm10_series)} PM10 series")

    print("=== get_by_station('DsWrocWybCon') ===")
    station_series = m.get_by_station("DsWrocWybCon") # Loads ~1300 TimeSeries
    for ts in station_series:
        print(f"  {ts.parameter_name} | {ts.averaging_time} | {len(ts.values)} measurements")

    print("=== detect_all_anomalies ===")
    validators = [
            ThresholdDetector(threshold=100.0),
            OutlierDetector(k=3.0),
            ZeroSpikeDetector(),
            SimpleReporter()]

    anomalies = m.detect_all_anomalies(validators, preload=False)
    print(f"Anomalies found: {len(anomalies)}")
    for key, msgs in list(anomalies.items())[:5]:
        print(f"  [{key}] → {len(msgs)} messages, first: {msgs[0][:80]}")

    print("=== detect_all_anomalies, preload=True ===")
    print(f"Before: {m}")
    anomalies_full = m.detect_all_anomalies(validators, preload=True) # Jednocześnie zad 7
    print(f"After: {m}")
    print(f"Anomalies found: {len(anomalies_full)}")
