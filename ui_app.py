import sys
import subprocess
import threading
import os
import re
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QPushButton, QTextEdit, QLabel,
    QCheckBox
)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QFont, QFontDatabase, QIcon, QTextCursor

LOG_FILE = Path("results/last_run.log")
os.environ["GTK_MODULES"] = ""

# Styles
STYLE_SHEET = """
    background-color: black;
    color: #00EE11;
    font-family: 'Liberation Mono';
"""

BUTTON_STYLE = """
    QPushButton {
        background-color: black;
        color: white;
        font-size: 12px;
        font-family: 'Liberation Mono';
        padding: 12px;
        text-align: center;
        border-radius: 0px;
    }
    QPushButton:hover {
        background-color: white;
        color: black;
    }
    QPushButton:pressed {
        background-color: #00EE11;
        color: black;
        border: 1.5px solid #00EE11;
    }
"""

TEXT_EDIT_STYLE = """
    background-color: black;
    color: #00EE11;
    font-family: 'Liberation Mono';
    font-size: 12px;
    border: 1.5px solid white;
    padding: 10px;
"""

LABEL_STYLE = """
    color: white;
    font-size: 20px;
    font-family: 'Liberation Mono';
"""

CHECKBOX_STYLE = """
    QCheckBox {
        color: white;
        font-size: 14px;
        margin: 5px;
        padding: 3px;
    }
    QCheckBox::indicator {
        border: 1px solid #00EE11;
        width: 16px;
        height: 16px;
        background-color: black;
    }
    QCheckBox::indicator:checked {
        background-color: #00EE11;
        border: 1px solid #00EE11;
    }
    QCheckBox::indicator:unchecked {
        background-color: black;
        border: 1px solid #00EE11;
    }
"""

FOOTER_STYLE = """
    color:white; 
    font-family: 'Liberation Mono'; 
    font-size: 12px; 
    text-align: center;
"""

class AnnotatorUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon("assets/img/icon.png"))
        self.setup_window()

        # UI Elements
        self.status_label = self.create_status_label()
        self.model_checkboxes = self.create_model_checkboxes()
        self.run_button = self.create_run_button()
        self.copy_button = self.create_copy_button()
        self.log_view = self.create_log_view()
        self.footer_label = self.create_footer_label()

        # Layout
        self.setup_layout()

        # Timer to allow auto-scrolling
        self.timer = QTimer()
        self.timer.timeout.connect(self.scroll_to_bottom)

        self.process_thread = None

    def setup_window(self):
        self.setWindowTitle("annyatator")
        self.resize(500, 600)
        self.setStyleSheet(STYLE_SHEET)
        self.load_custom_font("assets/fonts/LiberationMono-Regular.ttf")

    def load_custom_font(self, font_path):
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id != -1:
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            self.setFont(QFont(font_family, 12))
        else:
            print("Failed to load font!")

    def create_status_label(self):
        label = QLabel("Idle")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet(f"{LABEL_STYLE} font-size:12px; padding:5px;")
        return label

    def create_model_checkboxes(self):
        checkboxes = []
        for model in ["Ultralytics", "YoloNAS", "Darknet"]:
            cb = QCheckBox(model)
            cb.setStyleSheet(CHECKBOX_STYLE)
            checkboxes.append(cb)
        return checkboxes

    def create_run_button(self):
        button = QPushButton("Run Sweep")
        button.setStyleSheet(BUTTON_STYLE)
        button.clicked.connect(self.run_sweep)
        return button

    def create_copy_button(self):
        button = QPushButton("Copy Log")
        button.setStyleSheet(BUTTON_STYLE)
        button.clicked.connect(self.copy_log_to_clipboard)
        return button

    def copy_log_to_clipboard(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.log_view.toPlainText())
        self.status_label.setText("Log copied to clipboard")

    def create_log_view(self):
        log_view = QTextEdit()
        log_view.setReadOnly(True)
        log_view.setStyleSheet(TEXT_EDIT_STYLE)
        
        return log_view

    def create_footer_label(self):
        footer_label = QLabel(
            '''<p style="color:white; font-family: 'Liberation Mono'; font-size: 12px; text-align: center;">
            Made with <span style="color: black; background-color: white;">love</span> by 
            <a href="https://mm4rk3t.xyz" style="color:#00EE11;">/mm4rk3t/</a> - 
            <a href="https://github.com/mm4rk3t/annyatator" style="color:#00EE11;">GitHub Repo</a>
            </p>'''
        )
        footer_label.setOpenExternalLinks(True)
        return footer_label

    def setup_layout(self):
        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        for cb in self.model_checkboxes:
            layout.addWidget(cb)
        layout.addWidget(self.run_button)
        layout.addWidget(self.copy_button)
        layout.addWidget(self.log_view)
        layout.addWidget(self.footer_label)
        self.setLayout(layout)

    def run_sweep(self):
        """Run orchestrator.py and stream output live."""
        if self.process_thread and self.process_thread.is_alive():
            return

        self.status_label.setText("Running sweep...")
        self.run_button.setEnabled(False)
        self.log_view.clear()
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

        def task():
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

            with open(LOG_FILE, "w", encoding="utf-8") as log_file:
                process = subprocess.Popen(
                    ["python3", "orchestrator.py"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                )

                for line_bytes in iter(process.stdout.readline, b''):
                    try:
                        line = line_bytes.decode("utf-8", errors="replace")
                    except Exception:
                        line = str(line_bytes)
                    line_clean = ansi_escape.sub('', line)

                    # Append to QTextEdit
                    self.append_log(line_clean)

                    # Write raw line to log
                    log_file.write(line_clean)
                    log_file.flush()

                process.stdout.close()
                process.wait()

            self.status_label.setText("Finished")
            self.run_button.setEnabled(True)

        self.process_thread = threading.Thread(target=task, daemon=True)
        self.process_thread.start()
        self.timer.start(100)

    def append_log(self, text):
        scrollbar = self.log_view.verticalScrollBar()
        at_bottom = scrollbar.value() == scrollbar.maximum()

        self.log_view.moveCursor(QTextCursor.MoveOperation.End)
        self.log_view.insertPlainText(text)

    def scroll_to_bottom(self):
        scrollbar = self.log_view.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AnnotatorUI()
    window.show()
    sys.exit(app.exec())
