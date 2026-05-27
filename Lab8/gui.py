import sys
from PySide6.QtCore import QDate
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton,
                               QVBoxLayout, QHBoxLayout, QWidget, QFileDialog,
                               QListWidget, QMessageBox, QLabel, QLineEdit,
                               QFormLayout, QDateEdit)
from readLog import read_log_file


class LogBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Log Browser")
        self.resize(950, 600)
        self.logs = []
        self.filtered_logs = []

        main_layout = QHBoxLayout()

        left_layout = QVBoxLayout()
        self.open_button = QPushButton("Load logs file")

        filter_layout = QHBoxLayout()
        self.from_date_edit = QDateEdit()
        self.from_date_edit.setCalendarPopup(True)
        self.to_date_edit = QDateEdit()
        self.to_date_edit.setCalendarPopup(True)

        filter_layout.addWidget(QLabel("From:"))
        filter_layout.addWidget(self.from_date_edit)
        filter_layout.addWidget(QLabel("To:"))
        filter_layout.addWidget(self.to_date_edit)

        self.log_list = QListWidget()

        left_layout.addWidget(self.open_button)
        left_layout.addLayout(filter_layout)
        left_layout.addWidget(self.log_list)

        main_layout.addLayout(left_layout, stretch=2)

        right_widget = QWidget()
        right_main_layout = QVBoxLayout(right_widget)
        detail_layout = QFormLayout()

        self.host_input = QLineEdit()
        self.host_input.setReadOnly(True)

        self.date_input = QLineEdit()
        self.date_input.setReadOnly(True)

        self.time_input = QLineEdit()
        self.time_input.setReadOnly(True)

        self.method_input = QLineEdit()
        self.method_input.setReadOnly(True)

        self.resource_input = QLineEdit()
        self.resource_input.setReadOnly(True)

        self.status_input = QLineEdit()
        self.status_input.setReadOnly(True)

        detail_layout.addRow(QLabel("<h3>Log Details</h3>"))
        detail_layout.addRow("Remote host:", self.host_input)
        detail_layout.addRow("Date:", self.date_input)
        detail_layout.addRow("Time:", self.time_input)
        detail_layout.addRow("Method:", self.method_input)
        detail_layout.addRow("Resource:", self.resource_input)
        detail_layout.addRow("Status code:", self.status_input)

        nav_layout = QHBoxLayout()
        self.prev_button = QPushButton("Previous")
        self.next_button = QPushButton("Next")

        self.prev_button.setEnabled(False)
        self.next_button.setEnabled(False)

        nav_layout.addWidget(self.prev_button)
        nav_layout.addWidget(self.next_button)

        right_main_layout.addLayout(detail_layout)
        right_main_layout.addStretch()
        right_main_layout.addLayout(nav_layout)

        main_layout.addWidget(right_widget, stretch=1)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.open_button.clicked.connect(self.load_file)

        self.log_list.currentRowChanged.connect(self.display_details)
        self.from_date_edit.dateChanged.connect(self.filter_logs)
        self.to_date_edit.dateChanged.connect(self.filter_logs)

        self.prev_button.clicked.connect(self.go_previous)
        self.next_button.clicked.connect(self.go_next)

    def load_file(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Select the logs file", "", "All Files (*);;Log Files (*.log)")

        if filepath:
            self.log_list.clear()
            self.clear_details()
            self.logs = []

            logs, error = read_log_file(filepath)

            if error:
                QMessageBox.critical(self, "Error", f"Couldn't load file:\n{error}")
            elif logs:
                self.logs = logs
                if self.logs:
                    all_dates = [log["datetime"].date() for log in self.logs]
                    min_date = min(all_dates)
                    max_date = max(all_dates)

                    self.from_date_edit.blockSignals(True)
                    self.to_date_edit.blockSignals(True)

                    self.from_date_edit.setDate(QDate(min_date.year, min_date.month, min_date.day))
                    self.to_date_edit.setDate(QDate(max_date.year, max_date.month, max_date.day))

                    self.from_date_edit.blockSignals(False)
                    self.to_date_edit.blockSignals(False)

                self.filter_logs()
            else:
                QMessageBox.warning(self, "No data", "File is empty or unsupported.")

    def filter_logs(self):
        self.log_list.clear()
        self.clear_details()
        self.filtered_logs = []

        start_date = self.from_date_edit.date().toPython()
        end_date = self.to_date_edit.date().toPython()

        for log in self.logs:
            log_date = log["datetime"].date()

            if start_date <= log_date <= end_date:
                self.filtered_logs.append(log)
                self.log_list.addItem(log["master_text"])
        if self.log_list.count() > 0:
            self.log_list.setCurrentRow(0)
        else:
            self.update_nav_buttons()

    def display_details(self, row):
        if 0 <= row < len(self.filtered_logs):
            log = self.filtered_logs[row]
            self.host_input.setText(log["remote_host"])
            self.date_input.setText(log["date"])
            self.time_input.setText(log["time"])
            self.method_input.setText(log["method"])
            self.resource_input.setText(log["resource"])
            self.status_input.setText(log["status"])
        else:
            self.clear_details()
        self.update_nav_buttons()

    def clear_details(self):
        self.host_input.clear()
        self.date_input.clear()
        self.time_input.clear()
        self.method_input.clear()
        self.resource_input.clear()
        self.status_input.clear()

    def go_previous(self):
        current_row = self.log_list.currentRow()
        if current_row > 0:
            self.log_list.setCurrentRow(current_row - 1)

    def go_next(self):
        current_row = self.log_list.currentRow()
        if current_row < self.log_list.count() - 1:
            self.log_list.setCurrentRow(current_row + 1)

    def update_nav_buttons(self):
        current_row = self.log_list.currentRow()
        total_items = self.log_list.count()

        if total_items == 0:
            self.prev_button.setEnabled(False)
            self.next_button.setEnabled(False)
        else:
            self.prev_button.setEnabled(current_row > 0)
            self.next_button.setEnabled(current_row < total_items - 1)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LogBrowser()
    window.show()
    sys.exit(app.exec())