import sys
import zipfile
import csv
import io
from database import DatabaseManager


def load_table(zip_file, filename, table_name, columns, manager, batch_size=10000):
    with zip_file.open(filename) as f:
        text_file = io.TextIOWrapper(f, encoding='utf-8-sig')
        reader = csv.DictReader(text_file)

        batch = []
        for row in reader:
            clean_tuple = tuple((row.get(col) if row.get(col) != '' else None) for col in columns)
            batch.append(clean_tuple)

            if len(batch) >= batch_size:
                manager.insert_data(table_name, columns, batch)
                batch.clear()

        if batch:
            manager.insert_data(table_name, columns, batch)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(1)

    zip_path = sys.argv[1]
    db_name = sys.argv[2]
    manager = DatabaseManager(db_name)

    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            load_table(zf, "stops.txt", "stops",
                       ['stop_id', 'stop_code', 'stop_name', 'stop_lat', 'stop_lon'], manager)

            load_table(zf, "routes.txt","routes",
                       ['route_id', 'agency_id', 'route_short_name', 'route_long_name',
                        'route_desc', 'route_type', 'route_type2_id', 'valid_from', 'valid_until'], manager)

            load_table(zf, "calendar.txt","calendar",
                       ['service_id', 'monday', 'tuesday', 'wednesday', 'thursday',
                        'friday', 'saturday', 'sunday', 'start_date', 'end_date'], manager)

            load_table(zf, "trips.txt","trips",
                       ['trip_id', 'route_id', 'service_id', 'trip_headsign',
                        'direction_id', 'shape_id', 'brigade_id'], manager)

            load_table(zf, "stop_times.txt","stop_times",
                       ['trip_id', 'arrival_time', 'departure_time', 'stop_id', 'stop_sequence'], manager)
    except Exception as e:
        print(f"Error occured: {e}")