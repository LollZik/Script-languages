from SeriesValidator import *


class SimpleReporter:
    def analyze(self, series: 'TimeSeries') -> list[str]:
        result = []
        mean = series.mean
        mean_str = f"{mean:.4f}" if mean is not None else "N/A"
        result.append(f"Info: {series.parameter_name} at {series.station_code} has mean = {mean_str}")
        return result

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

    analyzers = [
        SimpleReporter(),
        ThresholdDetector(threshold=20.0),
        ZeroSpikeDetector(),
        OutlierDetector(k=1.0)
    ]

    for analyzer in analyzers:
        results = analyzer.analyze(ts)
        if results:
            for msg in results:
                print(msg)
