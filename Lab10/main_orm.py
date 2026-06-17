import sys
import zipfile
import csv
import io
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

from database_orm import Base, Stop, Route, Calendar, Trip, StopTime


def create_db_and_session(db_name):
    engine = create_engine(f'sqlite:///{db_name}')

    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


def load_table(zip_file, filename, model_class, columns, session, batch_size=10000):
    with zip_file.open(filename) as f:
        text_file = io.TextIOWrapper(f, encoding='utf-8-sig')
        reader = csv.DictReader(text_file)

        batch = []
        for row in reader:
            clean_row = {col: (row.get(col) if row.get(col) != '' else None) for col in columns}

            orm_object = model_class(**clean_row)
            batch.append(orm_object)

            if len(batch) >= batch_size:
                session.add_all(batch)
                session.commit()
                batch.clear()

        if batch:
            session.add_all(batch)
            session.commit()

def run_aggregation_query(session):
    '''
    SELECT r.route_short_name, COUNT(t.trip_id) AS trip_count
    FROM routes r
    JOIN trips t ON r.route_id = t.route_id
    GROUP BY r.route_short_name
    ORDER BY trip_count DESC
    LIMIT 10;

    '''
    results = session.query(
        Route.route_short_name,
        func.count(Trip.trip_id).label('trip_count')
    ) \
        .join(Trip) \
        .group_by(Route.route_short_name) \
        .order_by(func.count(Trip.trip_id).desc()) \
        .limit(10) \
        .all()

    for route_name, count in results:
        print(f"Linia {route_name}: {count} kursow")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(1)

    zip_path = sys.argv[1]
    db_name = sys.argv[2]
    if not db_name.endswith('.sqlite3'):
        db_name += '.sqlite3'

    session = create_db_and_session(db_name)

    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            load_table(zf, "stops.txt", Stop,
                       ['stop_id', 'stop_code', 'stop_name', 'stop_lat', 'stop_lon'], session)

            load_table(zf, "routes.txt", Route,
                       ['route_id', 'agency_id', 'route_short_name', 'route_long_name',
                        'route_desc', 'route_type', 'route_type2_id', 'valid_from', 'valid_until'], session)

            load_table(zf, "calendar.txt", Calendar,
                       ['service_id', 'monday', 'tuesday', 'wednesday', 'thursday',
                        'friday', 'saturday', 'sunday', 'start_date', 'end_date'], session)

            load_table(zf, "trips.txt", Trip,
                       ['trip_id', 'route_id', 'service_id', 'trip_headsign',
                        'direction_id', 'shape_id', 'brigade_id'], session)

            load_table(zf, "stop_times.txt", StopTime,
                       ['trip_id', 'arrival_time', 'departure_time', 'stop_id', 'stop_sequence'], session)

        run_aggregation_query(session)

    except Exception as e:
        print(f"Error occured: {e}")
        session.rollback()
    finally:
        session.close()