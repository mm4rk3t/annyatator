# ui_app.py
import sys
import subprocess
import threading
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QPushButton, QTextEdit, QLabel, QFileDialog
)
from PyQt6.QtCore import QTimer, Qt

LOG_FILE = Path("results/last_run.log")

class AnnotatorUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Amazing Annotator")
        self.resize(800, 600)

        layout = QVBoxLayout()        

        self.status_label = QLabel("Idle")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        self.run_button = QPushButton("Run Sweep")
        self.run_button.clicked.connect(self.run_sweep)
        layout.addWidget(self.run_button)

        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        layout.addWidget(self.log_view)

        self.setLayout(layout)

        # Timer to refresh logs
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_logs)

    def run_sweep(self):
        self.status_label.setText("Running sweep...")
        self.run_button.setEnabled(False)
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

        def task():
            with open(LOG_FILE, "w") as f:
                subprocess.run(
                    ["python", "orchestrator.py"],
                    stdout=f, stderr=subprocess.STDOUT, text=True
                )
            self.status_label.setText("Finished")
            self.run_button.setEnabled(True)

        threading.Thread(target=task, daemon=True).start()
        self.timer.start(1000)  # refresh logs every 1s

    def update_logs(self):
        if LOG_FILE.exists():
            with open(LOG_FILE) as f:
                self.log_view.setPlainText(f.read())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AnnotatorUI()
    window.show()
    sys.exit(app.exec())