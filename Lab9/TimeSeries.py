import datetime
import statistics
from typing import Union, List

unitDict = {
        "ug/m3" : 1,
        "ng/m3" : 2
    }

class TimeSeries:
    def __init__(self, parameter_name: str, station_code: str, averaging_time: str,
                 dates: List[datetime.datetime], values: List[Union[float, None]], unit: str) -> None:
        self.parameter_name = parameter_name
        self.station_code = station_code
        self.averaging_time = averaging_time
        self.dates = dates
        self.values = values
        self.unit = unit

    def __getitem__(self, key: Union[slice, int, datetime.datetime, datetime.date]) -> Union[tuple, float, list, None]:
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


    @property
    def getUnit(self) -> str:
        return self.unit

    @getUnit.setter
    def setUnit(self, newUnit : str) -> None:
        if newUnit not in unitDict:
            raise ValueError("Wrong unit")
        else:
            multiplier : Union[int, float] = unitDict[newUnit] - unitDict[self.unit]
            self.unit = newUnit
            if multiplier != 0:
                if multiplier > 0:
                    multiplier = 1000 ** multiplier
                elif multiplier < 0:
                    multiplier = 0.001 ** multiplier
                for i in range(len(self.values)):
                    if self.values[i] != None:
                        self.values[i] = self.values[i] * multiplier

    def __add__(self, other : 'TimeSeries') -> 'TimeSeries':
        if isinstance(other, TimeSeries):
            if self.parameter_name == other.parameter_name and self.station_code == other.station_code and self.averaging_time == other.averaging_time:
                date : List[datetime.datetime] = self.dates + other.dates
                value : List[Union[float, None]] = self.values + other.values
                ts : 'TimeSeries' = TimeSeries(parameter_name=self.parameter_name, station_code=self.station_code,
                                averaging_time=self.averaging_time, dates=date, values=value, unit=self.unit)
                return ts
            else:
                raise ValueError
        else:
            raise TypeError

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

    print(ts.getUnit)
    print(ts.values)
    ts.setUnit("ng/m3")
    print("Zmiana")
    print(ts.values)

    # # print("Indeks 1:", ts[1])
    # # print("Wycinek 0:3:", ts[0:3])
    # # print("Dokładny czas:", ts[dates[0]])
    # # print("Cały dzień:", ts[datetime.date(2023, 1, 1)])
    # #
    # # print("Średnia (mean):", ts.mean)
    # # print("Odchylenie (stddev):", ts.stddev)
    #
    # base_time2 = datetime.datetime(2023, 2, 2, 12, 0)
    # dates2 = [base_time2 + datetime.timedelta(hours=i) for i in range(5)]
    # values2 = [7.0, 3.3, 2.0, 0.0, None]
    #
    # ts2 = TimeSeries(
    #     parameter_name="PM10",
    #     station_code="DzWroBarto",
    #     averaging_time="1g",
    #     dates=dates2,
    #     values=values2,
    #     unit="ug/m3"
    # )
    #
    # ts3 = TimeSeries(
    #     parameter_name="PM2",
    #     station_code="AAAAA",
    #     averaging_time="1g",
    #     dates=dates,
    #     values=values,
    #     unit="ug/m3"
    # )
    #
    # ts4 = ts + ts2
    # print(ts4.dates)
    # print(ts4.values)
    #
    # ts5 = ts + ts3