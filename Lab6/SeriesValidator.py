import abc
import datetime
from TimeSeries import TimeSeries


class SeriesValidator(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def analyze(self, series: 'TimeSeries') -> list[str]:
        pass


class OutlierDetector(SeriesValidator):
    def __init__(self, k: float):
        self.k = k

    def analyze(self, series: 'TimeSeries') -> list[str]:
        mean = series.mean
        std = series.stddev

        if mean is None or std is None:
            return []

        anomalies = []
        for dt, val in series[:]:
            if val is not None:
                if abs(val - mean) > self.k * std:
                    anomalies.append(f"Outlier: {val} at {dt}")
        return anomalies


class ZeroSpikeDetector(SeriesValidator):
    def analyze(self, series: 'TimeSeries') -> list[str]:
        anomalies = []
        count = 0

        for i, val in enumerate(series.values):
            if val == 0 or val is None:
                count += 1
            else:
                if count >= 3:
                    anomalies.append(f"{count} zeros/missing values starting at {series.dates[i - count]}")
                count = 0
        return anomalies


class ThresholdDetector(SeriesValidator):
    def __init__(self, threshold: float):
        self.threshold = threshold

    def analyze(self, series: 'TimeSeries') -> list[str]:
        anomalies = []
        for dt, val in series[:]:
            if val is not None and val > self.threshold:
                anomalies.append(f"Threshold exceeded: {val} at {dt}")
        return anomalies

if __name__ == "__main__":
    base_time = datetime.datetime(2023, 1, 1, 12, 0)
    dates = [base_time + datetime.timedelta(hours=i) for i in range(8)]
    values = [10.5, 12.0, None, 0.0, None, 0.0, 15.5, 21.0]

    ts = TimeSeries(
        parameter_name="PM10",
        station_code="DzWroBarto",
        averaging_time="1g",
        dates=dates,
        values=values,
        unit="ug/m3"
    )
    detectors = [
        ThresholdDetector(threshold=20.0),
        ZeroSpikeDetector(),
        OutlierDetector(k=1.0)
    ]


    for d in detectors:
        results = d.analyze(ts)
        name = d.__class__.__name__
        if results:
            print(f"[{name}] Wykryto anomalie:")
            for msg in results:
                print(f"  - {msg}")
        else:
            print(f"[{name}] Brak anomali.")