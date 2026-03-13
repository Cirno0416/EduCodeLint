from PyQt6.QtCore import QThread
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QFileDialog, QListWidget, QHBoxLayout, QFrame, QListWidgetItem
)

from frontend.components.selected_file_item import SelectedFileItem
from frontend.core.analyze_worker import AnalyzeWorker
from frontend.components.exclude_tool_selector import ExcludeToolSelector
from frontend.components.score_dashboard import ScoreDashboard
from frontend.controllers.analyze_controller import AnalyzeController
from frontend.utils.dialog_util import DialogUtil


class AnalyzePage(QWidget):
    def __init__(self):
        super().__init__()

        self.controller = AnalyzeController()
        self.selected_files = []

        layout = QVBoxLayout()

        title = QLabel("代码分析")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        # ==============================
        # 分割线
        # ==============================
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(divider)

        # ==============================
        # 文件选择区域
        # ==============================
        file_section = QVBoxLayout()

        header_layout = QHBoxLayout()

        btn_font = QFont()
        btn_font.setPointSize(10)
        btn_font.setBold(True)

        label_font = QFont()
        label_font.setPointSize(12)
        label_font.setBold(True)

        # 标题
        label = QLabel("已选择文件")
        label.setFont(label_font)
        header_layout.addWidget(label)

        # 占位，把按钮推到右侧
        header_layout.addStretch()

        # 选择文件按钮
        self.btn_select = QPushButton("选择文件")
        self.btn_select.setFixedWidth(80)
        self.btn_select.setFixedHeight(30)
        self.btn_select.clicked.connect(self.select_files)
        self.btn_select.setFont(btn_font)
        header_layout.addWidget(self.btn_select)

        file_section.addLayout(header_layout)

        # 文件列表
        self.file_list = QListWidget()
        self.file_list.setObjectName("fileList")
        self.file_list.setStyleSheet("""
            QListWidget#fileList {
                border: 1px solid #ccc;
                border-radius: 3px;
            }
        """)
        file_section.addWidget(self.file_list)

        layout.addLayout(file_section)

        # ==============================
        # 底部区域
        # ==============================
        bottom_layout = QHBoxLayout()

        # 排除工具选择器
        self.exclude_tool_selector = ExcludeToolSelector()
        bottom_layout.addWidget(self.exclude_tool_selector)

        # 占位，把按钮推到右侧
        bottom_layout.addStretch()

        # 开始分析按钮
        self.btn_analyze = QPushButton("开始分析")
        self.btn_analyze.setFixedWidth(80)
        self.btn_analyze.setFixedHeight(30)
        self.btn_analyze.clicked.connect(self.run_analysis)
        self.btn_analyze.setFont(btn_font)
        bottom_layout.addWidget(self.btn_analyze)

        layout.addLayout(bottom_layout)

        # 这里是空隙
        layout.addSpacing(30)

        # ==============================
        # 分析结果展示区域
        # ==============================
        self.dashboard = ScoreDashboard()
        layout.addWidget(self.dashboard)

        self.setLayout(layout)

    def run_analysis(self):
        if not self.selected_files:
            DialogUtil.warning(self, "请先选择文件")
            return

        exclude_tools = self.exclude_tool_selector.get_selected()

        # 禁用按钮
        self.btn_analyze.setEnabled(False)

        # 显示主窗口级别的 Loading
        main_window = self.window()
        if hasattr(main_window, "loading"):
            main_window.loading.show()

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
        self.worker.error.connect(self.thread.quit)
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

    def select_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "选择Python文件", "", "Python Files (*.py)")
        if files:
            # 避免重复
            for f in files:
                if f not in self.selected_files:
                    self.selected_files.append(f)

            self.refresh_file_list()

    def refresh_file_list(self):
        self.file_list.clear()
        for f in self.selected_files:
            item_widget = SelectedFileItem(f, self.remove_file)
            item = QListWidgetItem(self.file_list)
            item.setSizeHint(item_widget.sizeHint())
            self.file_list.addItem(item)
            self.file_list.setItemWidget(item, item_widget)

    def remove_file(self, filename):
        if filename in self.selected_files:
            self.selected_files.remove(filename)
        self.refresh_file_list()
