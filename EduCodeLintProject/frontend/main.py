import sys
from PyQt6.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)

    with open("frontend/resources/styles.qss", "r", encoding="utf-8") as f:
        app.setStyleSheet(f.read())

    from frontend.core.app import MainWindow

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
