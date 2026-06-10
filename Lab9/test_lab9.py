import pytest
import datetime
import statistics

from Station import Station
from TimeSeries import TimeSeries
from SeriesValidator import OutlierDetector, ZeroSpikeDetector, ThresholdDetector
from Measurements import Measurements
from SimpleReporter import SimpleReporter


@pytest.fixture
def sample_dates():
    base = datetime.datetime(2023, 1, 1, 12, 0)
    return [base + datetime.timedelta(hours=i) for i in range(5)]

@pytest.fixture
def sample_ts(sample_dates):
    values = [10.0, 20.0, 30.0, 40.0, 50.0]
    return TimeSeries("PM10", "ST1", "1g", sample_dates, values, "ug/m3")

@pytest.fixture
def sample_ts_with_none(sample_dates):
    values = [10.0, None, 30.0, None, 50.0]
    return TimeSeries("PM10", "ST1", "1g", sample_dates, values, "ug/m3")


def test_station_eq_same_code():
    s1 = Station(station_code="WRO1", station_name="Wrocław A")
    s2 = Station(station_code="WRO1", station_name="Wrocław B")
    assert s1 == s2

def test_station_eq_different_code():
    s1 = Station(station_code="WRO1")
    s2 = Station(station_code="WRO2")
    assert s1 != s2

def test_station_eq_different_type():
    s1 = Station(station_code="WRO1")
    assert s1 != "WRO1"

def test_timeseries_getitem_int(sample_ts, sample_dates):
    assert sample_ts[2] == (sample_dates[2], 30.0)

def test_timeseries_getitem_slice(sample_ts, sample_dates):
    assert sample_ts[1:3] == [(sample_dates[1], 20.0), (sample_dates[2], 30.0)]

def test_timeseries_getitem_date_exists(sample_ts):
    search_date = datetime.date(2023, 1, 1)
    result = sample_ts[search_date]
    assert result == [10.0, 20.0, 30.0, 40.0, 50.0]

def test_timeseries_getitem_date_missing(sample_ts):
    search_date = datetime.date(2025, 5, 5)
    with pytest.raises(KeyError):
        result = sample_ts[search_date]
    #assert result == []

def test_timeseries_mean_stddev_complete(sample_ts):
    assert sample_ts.mean == 30.0
    expected_stddev = statistics.stdev([10.0, 20.0, 30.0, 40.0, 50.0])
    assert sample_ts.stddev == pytest.approx(expected_stddev)

def test_timeseries_mean_stddev_with_none(sample_ts_with_none):
    assert sample_ts_with_none.mean == 30.0
    expected_stddev = statistics.stdev([10.0, 30.0, 50.0])
    assert sample_ts_with_none.stddev == pytest.approx(expected_stddev)

def test_outlier_detector():
    base = datetime.datetime(2023, 1, 1, 12, 0)
    dates = [base + datetime.timedelta(hours=i) for i in range(6)]
    values = [10.0, 10.0, 10.0, 10.0, 10.0, 1000.0]

    ts = TimeSeries("PM10", "ST1", "1g", dates, values, "ug/m3")
    detector = OutlierDetector(k=2.0)
    anomalies = detector.analyze(ts)

    assert len(anomalies) == 1
    assert "Outlier: 1000.0" in anomalies[0]


def test_zero_spike_detector():
    base = datetime.datetime(2023, 1, 1, 12, 0)
    dates = [base + datetime.timedelta(hours=i) for i in range(10)]
    values = [10.0, 0.0, 0.0, 0.0, 15.0, None, None, None, None, 20.0]

    ts = TimeSeries("PM10", "ST1", "1g", dates, values, "ug/m3")
    detector = ZeroSpikeDetector()
    anomalies = detector.analyze(ts)

    assert len(anomalies) == 2
    assert "3 zeros/missing values" in anomalies[0]
    assert "4 zeros/missing values" in anomalies[1]



def test_threshold_detector():
    base = datetime.datetime(2023, 1, 1, 12, 0)
    dates = [base + datetime.timedelta(hours=i) for i in range(3)]
    values = [10.0, 55.0, 100.0]

    ts = TimeSeries("PM10", "ST1", "1g", dates, values, "ug/m3")
    detector = ThresholdDetector(threshold=50.0)
    anomalies = detector.analyze(ts)

    assert len(anomalies) == 2
    assert "Threshold exceeded: 55.0" in anomalies[0]
    assert "Threshold exceeded: 100.0" in anomalies[1]

@pytest.fixture
def mock_measurements(sample_ts):
    m = Measurements(".")
    m.loaded[("ST1", "PM10", "1g")] = sample_ts
    return m


@pytest.mark.parametrize("validator_object, expected_key, expected_substrings", [
    (ThresholdDetector(threshold=35.0),"ThresholdDetector/ST1/PM10",["Threshold exceeded: 40.0", "Threshold exceeded: 50.0"]),
    (ZeroSpikeDetector(),None,[]),
    (OutlierDetector(k=5.0),None,[]),
    (SimpleReporter(),"SimpleReporter/ST1/PM10",["Info: PM10 at ST1 has mean = 30.0000"])
])
def test_detect_all_anomalies(mock_measurements, validator_object, expected_key, expected_substrings):
    validators = [validator_object]
    results = mock_measurements.detect_all_anomalies(validators, preload=False)
    if expected_key is None:
        assert len(results) == 0
    else:
        assert expected_key in results
        messages = results[expected_key]
        assert len(messages) == len(expected_substrings)
        for expected_str in expected_substrings:
            assert any(expected_str in msg for msg in messages)
