import sys
from PyQt6.QtWidgets import QApplication
from frontend.core.app import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    with open("frontend/resources/styles.qss", "r", encoding="utf-8") as f:
        app.setStyleSheet(f.read())

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
