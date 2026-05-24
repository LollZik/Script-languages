import sys
from datetime import datetime
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton,
                               QVBoxLayout, QWidget, QFileDialog, QListWidget, QMessageBox)


# From /lab3 but changed to open a file, not read from cmd
def read_log_file(filepath):
    log_data = []
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                fields = line.split('\t')
                try:
                    ts = datetime.fromtimestamp(float(fields[0]))
                    uid = fields[1]
                    orig_h = fields[2]
                    orig_p = int(fields[3])
                    resp_h = fields[4]
                    resp_p = int(fields[5])
                    method = fields[7]
                    host = fields[8]
                    uri = fields[9]
                    status = int(fields[14]) if fields[14] != '-' else 0

                    formatted_line = f"{orig_h} - [{ts}] \"{method} {uri}\" {status}"

                    if len(formatted_line) > 100:
                        formatted_line = formatted_line[:100] + "..."
                    log_data.append(formatted_line)
                except (ValueError, IndexError):
                    continue

    except Exception as e:
        return None, str(e)

    return log_data, None


class LogBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        # Main window
        self.setWindowTitle("Log Browser")
        self.resize(800, 600)

        # Widgets
        self.open_button = QPushButton("Load logs file")
        self.log_list = QListWidget()

        # Vertical layout
        layout = QVBoxLayout()
        layout.addWidget(self.open_button)
        layout.addWidget(self.log_list)

        # Central widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Connect mouse1 with loading slot
        self.open_button.clicked.connect(self.load_file)

    def load_file(self):
        # Select file dialog
        filepath, _ = QFileDialog.getOpenFileName(self, "Select the logs file", "", "All Files (*);;Log Files (*.log)")

        if filepath:
            self.log_list.clear()
            logs, error = read_log_file(filepath)

            if error:
                QMessageBox.critical(self, "Error", f"Couldn't load file:\n{error}")
            elif logs:
                self.log_list.addItems(logs)
            else:
                QMessageBox.warning(self, "No data", "File is empty or unsupported.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LogBrowser()
    window.show()
    sys.exit(app.exec())