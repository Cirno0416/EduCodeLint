from PyQt6.QtCore import QThread
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QFileDialog, QListWidget
)

from frontend.core.analyze_worker import AnalyzeWorker
from frontend.components.tool_selector import ToolSelector
from frontend.components.score_dashboard import ScoreDashboard
from frontend.controllers.analyze_controller import AnalyzeController
from frontend.utils.dialog_util import DialogUtil


class AnalyzePage(QWidget):
    def __init__(self):
        super().__init__()

        self.controller = AnalyzeController()
        self.selected_files = []

        layout = QVBoxLayout()

        title = QLabel("代码分析模块")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        self.btn_select = QPushButton("选择文件")
        self.btn_select.clicked.connect(self.select_files)
        layout.addWidget(self.btn_select)

        self.file_list = QListWidget()
        layout.addWidget(self.file_list)

        self.tool_selector = ToolSelector()
        layout.addWidget(self.tool_selector)

        self.btn_analyze = QPushButton("开始分析")
        self.btn_analyze.clicked.connect(self.run_analysis)
        layout.addWidget(self.btn_analyze)

        self.dashboard = ScoreDashboard()
        layout.addWidget(self.dashboard)

        self.setLayout(layout)

    def select_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "选择Python文件", "", "Python Files (*.py)")
        if files:
            self.selected_files = files
            self.file_list.clear()
            self.file_list.addItems(files)

    def run_analysis(self):
        if not self.selected_files:
            DialogUtil.warning(self, "请先选择文件")
            return

        exclude_tools = self.tool_selector.get_selected()

        # 禁用按钮
        self.btn_analyze.setEnabled(False)

        # 显示主窗口级别的 Loading
        main_window = self.window()
        if hasattr(main_window, "loading"):
            main_window.loading.show()

        # 创建线程
        self.thread = QThread()
        self.worker = AnalyzeWorker(
            self.controller,
            self.selected_files,
            exclude_tools
        )

        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_analysis_finished)
        self.worker.error.connect(self.on_analysis_error)

        # 清理线程
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def on_analysis_finished(self, result):
        main_window = self.window()
        if hasattr(main_window, "loading"):
            main_window.loading.hide()

        self.btn_analyze.setEnabled(True)

        if result.get("code") != 0:
            DialogUtil.error(self, result.get("msg", "未知错误"))
            return

        self.dashboard.update_score(result["data"])

    def on_analysis_error(self, message):
        main_window = self.window()
        if hasattr(main_window, "loading"):
            main_window.loading.hide()

        self.btn_analyze.setEnabled(True)
        DialogUtil.error(self, message)
