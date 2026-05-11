import datetime
import statistics
from typing import Union, List


class TimeSeries:
    def __init__(self, parameter_name: str, station_code: str, averaging_time: str,
                 dates: List[datetime.datetime], values: List[Union[float, None]], unit: str):
        self.parameter_name = parameter_name
        self.station_code = station_code
        self.averaging_time = averaging_time
        self.dates = dates
        self.values = values
        self.unit = unit

    def __getitem__(self, key: Union[slice, int, datetime.datetime, datetime.date]):
        if isinstance(key, slice):
            return list(zip(self.dates[key], self.values[key]))

        elif isinstance(key, int):
            return self.dates[key], self.values[key]


        elif isinstance(key, datetime.datetime):
            try:
                idx = self.dates.index(key)
                return self.values[idx]
            except ValueError:
                raise KeyError(f"Brak pomiaru dla dokładnego czasu: {key}")

        elif isinstance(key, datetime.date):
            matched_values = [
                val for dt, val in zip(self.dates, self.values)
                if dt.date() == key
            ]
            if not matched_values:
                raise KeyError(f"Brak pomiarów dla dnia: {key}")
            return matched_values
        else:
            raise TypeError("Zly typ indeksu")

    @property
    def mean(self) -> Union[float, None]:
        valid_values = [v for v in self.values if v is not None]
        if not valid_values:
            return None
        return sum(valid_values) / len(valid_values)

    @property
    def stddev(self) -> Union[float, None]:
        valid_values = [v for v in self.values if v is not None]
        if len(valid_values) < 2:
            return None

        return statistics.stdev(valid_values)

if __name__ == "__main__":
    base_time = datetime.datetime(2023, 1, 1, 12, 0)
    dates = [base_time + datetime.timedelta(hours=i) for i in range(5)]
    values = [10.5, 12.0, None, 15.5, 11.0]

    ts = TimeSeries(
        parameter_name="PM10",
        station_code="DzWroBarto",
        averaging_time="1g",
        dates=dates,
        values=values,
        unit="ug/m3"
    )

    print("Indeks 1:", ts[1])
    print("Wycinek 0:3:", ts[0:3])
    print("Dokładny czas:", ts[dates[0]])
    print("Cały dzień:", ts[datetime.date(2023, 1, 1)])

    print("Średnia (mean):", ts.mean)
    print("Odchylenie (stddev):", ts.stddev)