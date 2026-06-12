import sqlite3


class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = (
            sqlite3.Row
        )
        return conn

    def create_tables(self):
        query_stops = """
        CREATE TABLE IF NOT EXISTS stops (
            stop_id INTEGER PRIMARY KEY,
            stop_code INTEGER NOT NULL,
            stop_name TEXT NOT NULL,
            stop_lat REAL NOT NULL,
            stop_lon REAL NOT NULL
        );
        """

        query_routes = """
        CREATE TABLE IF NOT EXISTS routes (
            route_id TEXT PRIMARY KEY,
            agency_id INTEGER NOT NULL,
            route_short_name TEXT NOT NULL,
            route_long_name TEXT,
            route_desc TEXT NOT NULL,
            route_type INTEGER NOT NULL,
            route_type2_id INTEGER NOT NULL,
            valid_from TEXT NOT NULL,
            valid_until TEXT NOT NULL
        );
        """

        query_trips = """
        CREATE TABLE IF NOT EXISTS trips (
            trip_id TEXT PRIMARY KEY,
            route_id TEXT NOT NULL,
            service_id TEXT NOT NULL,
            trip_headsign TEXT,
            direction_id INTEGER,
            shape_id TEXT,
            brigade_id TEXT,
            FOREIGN KEY (route_id) REFERENCES routes(route_id),
            FOREIGN KEY (service_id) REFERENCES calendar(service_id)
        );
        """

        query_stop_times = """
        CREATE TABLE IF NOT EXISTS stop_times (
            trip_id TEXT NOT NULL,
            arrival_time TEXT NOT NULL,
            departure_time TEXT NOT NULL,
            stop_id INTEGER NOT NULL,
            stop_sequence INTEGER NOT NULL,
            FOREIGN KEY (trip_id) REFERENCES trips(trip_id),
            FOREIGN KEY (stop_id) REFERENCES stops(stop_id),
            PRIMARY KEY (trip_id, stop_sequence)
        );
        """

        query_calendar = """
        CREATE TABLE IF NOT EXISTS calendar (
            service_id TEXT PRIMARY KEY,
            monday INTEGER NOT NULL,
            tuesday INTEGER NOT NULL,
            wednesday INTEGER NOT NULL,
            thursday INTEGER NOT NULL,
            friday INTEGER NOT NULL,
            saturday INTEGER NOT NULL,
            sunday INTEGER NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL
        );
        """

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query_stops)
            cursor.execute(query_routes)
            cursor.execute(query_calendar)
            cursor.execute(query_trips)
            cursor.execute(query_stop_times)
            conn.commit()
        conn.close()


    def _execute_insert(self, query, data):
        conn = self.get_connection()
        try:
            with conn:
                conn.cursor().executemany(query, data)
        finally:
            conn.close()


    def insert_data(self, table_name, columns, data):
        if not data:
            return
        columns_str = ', '.join(columns)
        questionmarks = ', '.join(['?'] * len(columns))
        query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({questionmarks})"

        self._execute_insert(query, data)
