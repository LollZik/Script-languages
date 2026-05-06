from parseFiles import parse_measurements

def detect_anomalies(measurements, threshold_delta=100.0, alarm_limit=500.0, inv_val_limit = 1000, delta_limit = 1000):
    anomalies = []
    prev_val = None
    inv_val_count = 0
    delta_count = 0

    for m in measurements:
        val = m[1]

        if val is None or val <= 0:
            inv_val_count += 1

        if val is not None and val > alarm_limit:
            anomalies.append(f"Przekroczenie progu alarmowego - {m[1]}")

        if prev_val is not None and val is not None:
            if abs(val - prev_val) > threshold_delta:
                delta_count += 1

        prev_val = val

    if delta_count > 0:
        anomalies.append(f"Zbyt częste skoki wartości - {delta_count}")
    if inv_val_count > 0:
        anomalies.append(f"Zbyt wiele błędnych wartości - {inv_val_count}")
    return anomalies

def main():
    measurements = parse_measurements('measurements/2023_PM10_1g.csv')
    anomalies = detect_anomalies(measurements)
    for a in anomalies:
        print(a)

if __name__ == "__main__":
    main()