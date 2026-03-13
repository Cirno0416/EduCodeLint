from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStackedWidget

from frontend.components.loading_overlay import LoadingOverlay
from frontend.components.sidebar import Sidebar
from frontend.pages.analyze_page import AnalyzePage
from frontend.pages.compare_page import ComparePage
from frontend.pages.record_page import RecordPage


class MainWindow(QMainWindow):
    PAGE_ANALYZE = 0
    PAGE_COMPARE = 1
    PAGE_RECORD = 2

    def __init__(self):
        super().__init__()
        self.setWindowTitle("EduCodeLint - 教学代码质量分析系统")
        self.resize(1200, 770)

        container = QWidget()
        layout = QHBoxLayout()

        self.sidebar = Sidebar()
        self.analyze_page = AnalyzePage()
        self.compare_page = ComparePage()
        self.record_page = RecordPage()

        # 页面容器
        self.stack = QStackedWidget()
        self.stack.addWidget(self.analyze_page)
        self.stack.addWidget(self.compare_page)
        self.stack.addWidget(self.record_page)

        # 绑定按钮事件
        self.sidebar.btn_analysis.clicked.connect(
            lambda: self.show_page(self.PAGE_ANALYZE)
        )
        self.sidebar.btn_compare.clicked.connect(
            lambda: self.show_page(self.PAGE_COMPARE)
        )
        self.sidebar.btn_record.clicked.connect(
            lambda: self.show_page(self.PAGE_RECORD)
        )

        layout.addWidget(self.sidebar)
        layout.addWidget(self.stack)

        container.setLayout(layout)
        self.setCentralWidget(container)

        # 进度条浮层
        self.loading = LoadingOverlay(self.centralWidget())

    def show_page(self, index: int):
        """
        切换页面，同时处理特殊逻辑：
        - 历史记录页面切换时自动刷新
        """
        self.stack.setCurrentIndex(index)

        # 如果切换到历史记录页面，自动刷新
        if index == self.PAGE_RECORD:
            self.record_page.load_records()
