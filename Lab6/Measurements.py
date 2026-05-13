import csv
import datetime
import os
import re
import sys
from collections import defaultdict
from typing import Optional

from TimeSeries import TimeSeries
from SeriesValidator import ThresholdDetector, OutlierDetector, ZeroSpikeDetector
from SimpleReporter import SimpleReporter


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
        self.registry: dict[tuple, tuple] = {}
        self.loaded: dict[tuple, TimeSeries] = {}
        self.loaded_files: set[str] = set()

        for filename in sorted(os.listdir(directory)):
            if re.match(r'^(\d{4})_(.+?)_(.+?)\.csv$', filename):
                self.register_file(os.path.join(directory, filename))

    def register_file(self, file_path: str):
        with open(file_path, encoding='utf-8-sig') as f:
            rows = [next(csv.reader(f)) for _ in range(6)]

        # Register each station in the file
        for i in range(1, len(rows[1])):
            station = rows[1][i].strip()
            if station:
                key = (station, rows[2][i].strip(), rows[3][i].strip())
                if key not in self.registry:
                    self.registry[key] = (file_path, rows[4][i].strip())

    def load_file(self, file_path: str):
        if file_path in self.loaded_files:
            return

        with open(file_path, encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            next(reader)
            stations = [s.strip() for s in next(reader)]
            params   = [p.strip() for p in next(reader)]
            avgs     = [a.strip() for a in next(reader)]
            next(reader)
            next(reader)
            data = defaultdict(lambda: ([], []))

            for row in reader:
                if not row or not row[0].strip():
                    continue
                try:
                    dt = datetime.datetime.strptime(row[0].strip(), '%d/%m/%y %H:%M')
                except ValueError:
                    continue
                for i in range(1, len(row)):
                    if stations[i].strip():
                        key = (stations[i].strip(), params[i].strip(), avgs[i].strip())
                        data[key][0].append(dt)
                        data[key][1].append(parse_value(row[i]))

        for (station, param, avg), (dates, values) in data.items():
            unit = self.registry.get((station, param, avg), (None, ''))[1]
            self.loaded[(station, param, avg)] = TimeSeries(param, station, avg, dates, values, unit)

        self.loaded_files.add(file_path)

    def _ensure_loaded(self, key: tuple):
        if key not in self.loaded and key in self.registry:
            self.load_file(self.registry[key][0])

    def preload_all(self):
        for file_path, _ in self.registry.values():
            self.load_file(file_path)

    def __len__(self) -> int:
        return len(self.registry)

    def __contains__(self, parameter_name: str) -> bool:
        return any(key[1] == parameter_name for key in self.registry)

    def get_by_parameter(self, param_name: str) -> list[TimeSeries]:
        keys = [k for k in self.registry if k[1] == param_name]
        for k in keys:
            self._ensure_loaded(k)
        return [self.loaded[k] for k in keys if k in self.loaded]

    def get_by_station(self, station_code: str) -> list[TimeSeries]:
        keys = [k for k in self.registry if k[0] == station_code]
        for k in keys:
            self._ensure_loaded(k)
        return [self.loaded[k] for k in keys if k in self.loaded]

    def __repr__(self) -> str:
        return f"Measurements(directory={self.directory!r}, registered={len(self.registry)}, loaded={len(self.loaded)})"

    def detect_all_anomalies(self, validators: list, preload: bool = False) -> dict[str, list[str]]:
        if preload:
            self.preload_all()
        results = {}
        for ts in self.loaded.values():
            for validator in validators:
                messages = validator.analyze(ts)
                if messages:
                    results[f"{validator.__class__.__name__}/{ts.station_code}/{ts.parameter_name}"] = messages
        return results

if __name__ == "__main__":
    data_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "measurements")

    m = Measurements(data_dir)
    print(m)
    print(f"(__len__): {len(m)}\n")

    for param in ("PM10", "O3", "SO2", "benzen", "chomik"):
        print(f"{param!r} in m: {param in m}")

    print("\n=== get_by_parameter('PM10') ===")
    pm10 = m.get_by_parameter("PM10")
    for ts in pm10[:3]:
        mean_str = f"{ts.mean:.2f}" if ts.mean is not None else "N/A"
        print(f"  {ts.station_code} | {ts.parameter_name} | mean={mean_str}")
    print(f"{len(pm10)} PM10 series")

    print("\n=== get_by_station('DsWrocWybCon') ===")
    for ts in m.get_by_station("DsWrocWybCon"):
        print(f"  {ts.parameter_name} | {ts.averaging_time} | {len(ts.values)} measurements")

    validators = [
        ThresholdDetector(threshold=100.0),
        OutlierDetector(k=3.0),
        ZeroSpikeDetector(),
        SimpleReporter()]

    print("\n=== detect_all_anomalies ===")
    anomalies = m.detect_all_anomalies(validators, preload=False)
    print(f"Anomalies found: {len(anomalies)}")
    for key, msgs in list(anomalies.items())[:5]:
        print(f"  [{key}] -> {len(msgs)} messages, first: {msgs[0][:80]}")

    print("\n=== detect_all_anomalies, preload=True ===")
    print(f"Before: {m}")
    anomalies_full = m.detect_all_anomalies(validators, preload=True) # Jednoczesnie zad 7
    print(f"After:  {m}")
    print(f"Anomalies found: {len(anomalies_full)}")