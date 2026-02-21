from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout

from frontend.components.loading_overlay import LoadingOverlay
from frontend.components.sidebar import Sidebar
from frontend.pages.analyze_page import AnalyzePage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EduCodeLint - 教学代码质量分析系统")
        self.resize(1200, 750)

        container = QWidget()
        layout = QHBoxLayout()

        self.sidebar = Sidebar()
        self.analysis_page = AnalyzePage()

        layout.addWidget(self.sidebar)
        layout.addWidget(self.analysis_page)

        container.setLayout(layout)
        self.setCentralWidget(container)

        # 进度条浮层
        self.loading = LoadingOverlay(self.centralWidget())
