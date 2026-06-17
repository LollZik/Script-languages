import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget,
                               QComboBox, QPushButton, QTextEdit, QLabel)
from database import DatabaseManager


class TimetableWindow(QMainWindow):
    def __init__(self, db_name):
        super().__init__()
        self.manager = DatabaseManager(db_name)
        self.setWindowTitle("Przystanki rozkładu Jazdy")
        self.resize(500, 450)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        layout.addWidget(QLabel("Wybierz przystanek:"))
        self.stop_combobox = QComboBox()
        self.load_stops()
        layout.addWidget(self.stop_combobox)

        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        layout.addWidget(self.result_display)

        self.stop_combobox.currentTextChanged.connect(self.analyze_stop)
        self.analyze_stop()

    def load_stops(self):
        conn = self.manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT stop_id, stop_name FROM stops ORDER BY stop_name")
        self.stops = cursor.fetchall()
        for stop in self.stops:
            self.stop_combobox.addItem(f"{stop['stop_name']} (ID: {stop['stop_id']})", stop['stop_id'])
        conn.close()

    def analyze_stop(self):
        stop_id = self.stop_combobox.currentData()

        basic_query = """
        SELECT 
            COUNT(DISTINCT r.route_id) as route_count,
            COUNT(st.arrival_time) as departure_count,
            MIN(st.departure_time) as earliest,
            MAX(st.departure_time) as latest,
            (SELECT trip_headsign FROM trips t2 
             JOIN stop_times st2 ON t2.trip_id = st2.trip_id 
             WHERE st2.stop_id = stops.stop_id GROUP BY trip_headsign ORDER BY COUNT(*) DESC LIMIT 1) as common_dest
        FROM stops
        LEFT JOIN stop_times st ON stops.stop_id = st.stop_id
        LEFT JOIN trips t ON st.trip_id = t.trip_id
        LEFT JOIN routes r ON t.route_id = r.route_id
        WHERE stops.stop_id = ?
        """

        avg_time_query = """
        SELECT 
            r.route_short_name,
            AVG((strftime('%s', next_departure) - strftime('%s', current_departure))/60.0) as srednia_przerwa
        FROM (
            SELECT 
                route_id,
                current_departure,
                LEAD(current_departure) OVER (PARTITION BY route_id, direction_id ORDER BY current_departure) as next_departure
            FROM (
                SELECT DISTINCT t.route_id, t.direction_id, st.departure_time as current_departure
                FROM stop_times st
                JOIN trips t ON st.trip_id = t.trip_id
                WHERE st.stop_id = ?
            )
        ) as sub
        JOIN routes r ON sub.route_id = r.route_id
        WHERE next_departure IS NOT NULL AND next_departure > current_departure
        GROUP BY r.route_short_name;
        """
        conn = self.manager.get_connection()
        cursor = conn.cursor()
        cursor.execute(basic_query, (stop_id,))
        res = cursor.fetchone()
        cursor.execute(avg_time_query, (stop_id,))
        res2 = cursor.fetchall()
        conn.close()

        avg_times = ""
        if res2:
            for row in res2:
                if row['srednia_przerwa'] is not None:
                    czas_min = round(row['srednia_przerwa'], 1)
                    avg_times += f"  Linia {row['route_short_name']}: {czas_min} min\n"
        else:
            avg_times = "Nie wystarcząjąco danych o kursach\n"

        output = (
            f"Przystanek: {self.stop_combobox.currentText()}\n"
            f"\n"
            f"a. Liczba różnych linii: {res['route_count']}\n"
            f"b. Liczba odjazdów: {res['departure_count']}\n"
            f"c. Najwcześniejszy odjazd: {res['earliest']}\n"
            f"c. Najpóźniejszy odjazd: {res['latest']}\n"
            f"d. Najczęstszy kierunek odjazdu: {res['common_dest']}\n"
            f"\n"
            f"e. Średni czas między kursami:"
            f"\n{avg_times}"
        )
        self.result_display.setPlainText(output)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TimetableWindow("abc.sqlite3")
    window.show()
    sys.exit(app.exec())