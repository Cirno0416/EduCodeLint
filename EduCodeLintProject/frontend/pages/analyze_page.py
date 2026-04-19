import os

from PyQt6.QtCore import QThread, Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QFileDialog, QListWidget, QHBoxLayout, QFrame, QListWidgetItem, QGridLayout, QMessageBox
)

from backend.constant.metric_category import MetricCategory
from frontend.components.selected_file_item import SelectedFileItem
from frontend.core.analyze_worker import AnalyzeWorker
from frontend.components.exclude_tool_selector import ExcludeToolSelector
from frontend.components.score_dashboard import ScoreDashboard
from frontend.controllers.analyze_controller import AnalyzeController
from frontend.core.reset_weights_worker import ResetWeightsWorker
from frontend.core.weights_worker import WeightsWorker
from frontend.utils.dialog_util import DialogUtil


class AnalyzePage(QWidget):
    def __init__(self):
        super().__init__()

        self.controller = AnalyzeController()
        self.selected_files = []

        layout = QVBoxLayout()

        title = QLabel("代码分析")
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)

        # ==============================
        # 分割线
        # ==============================
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(divider)

        btn_font = QFont()
        btn_font.setPointSize(10)
        btn_font.setBold(True)

        label_font = QFont()
        label_font.setPointSize(12)
        label_font.setBold(True)

        top_section_layout = QHBoxLayout()

        # 左侧：文件选择区域（占70%宽度）
        file_section = QVBoxLayout()
        file_section.setObjectName("fileSection")

        file_header_layout = QHBoxLayout()

        # 标题
        label = QLabel("已选择文件")
        label.setFont(label_font)
        file_header_layout.addWidget(label)

        # 占位，把按钮推到右侧
        file_header_layout.addStretch()

        # 选择文件按钮
        self.btn_select = QPushButton("选择文件")
        self.btn_select.setFixedWidth(80)
        self.btn_select.setFixedHeight(30)
        self.btn_select.clicked.connect(self.select_files)
        self.btn_select.setFont(btn_font)
        file_header_layout.addWidget(self.btn_select)

        file_section.addLayout(file_header_layout)

        # 文件列表
        self.file_list = QListWidget()
        self.file_list.setObjectName("fileList")
        self.file_list.setStyleSheet("""
            QListWidget#fileList {
                border: 1px solid #ccc;
                border-radius: 3px;
                background-color: white;
                border-radius: 6px;
            }
        """)
        file_section.addWidget(self.file_list)

        # 右侧：权重展示区域（占30%宽度）
        weight_section = QVBoxLayout()

        weights_header_layout = QHBoxLayout()

        # 标题
        label = QLabel("当前权重配置")
        label.setFont(label_font)
        weights_header_layout.addWidget(label)

        # 问号提示
        help_label = QLabel("?")
        help_label.setFont(btn_font)
        help_label.setFixedSize(18, 18)
        help_label.setStyleSheet("""
            QLabel {
                color: #555;
                border: 1px solid #ccc;
                border-radius: 9px;
                background-color: #f5f5f5;
                font-size: 12px;
                font-family: Arial;
                padding-left: 1px;
            }
        """)

        help_label.setToolTip(
            "注释指标不参与权重计算。\n\n"
            "原因：\n"
            "1. 注释不影响程序运行\n"
            "2. 更适合作为教学辅助指标\n"
            "3. 采用“约束项扣分”机制：\n"
            "   · 无Docstring：扣分\n"
            "   · 不规范Docstring：轻微扣分\n"
            "   · 规范Docstring：不扣分"
        )

        weights_header_layout.addWidget(help_label)

        # 占位，把按钮推到右侧
        weights_header_layout.addStretch()

        # 重置权重按钮
        self.btn_reset_weights = QPushButton("重置权重")
        self.btn_reset_weights.setFixedWidth(80)
        self.btn_reset_weights.setFixedHeight(30)
        self.btn_reset_weights.clicked.connect(self.reset_weights)
        self.btn_reset_weights.setFont(btn_font)
        weights_header_layout.addWidget(self.btn_reset_weights)

        weight_section.addLayout(weights_header_layout)

        # 添加分隔线
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setFrameShadow(QFrame.Shadow.Sunken)
        weight_section.addWidget(divider)

        # 创建权重列表容器
        weights_container = QWidget()
        weights_layout = QGridLayout(weights_container)
        weights_layout.setVerticalSpacing(10)
        weights_layout.setHorizontalSpacing(20)

        # 创建权重标签字典
        self.weight_labels = {}

        # 定义初始指标列表
        indicators = [
            MetricCategory.CODE_STYLE,
            MetricCategory.CODE_SMELL,
            MetricCategory.COMPLEXITY,
            MetricCategory.POTENTIAL_ERROR,
            MetricCategory.SECURITY_VULNERABILITY
        ]

        # 创建权重显示行
        for i, indicator in enumerate(indicators):
            # 指标名称
            name_label = QLabel(indicator)
            name_label.setFont(btn_font)
            weights_layout.addWidget(name_label, i, 0)

            # 权重值（初始显示0%）
            weight_label = QLabel("0.00%")
            weight_label.setFont(btn_font)
            weight_label.setAlignment(Qt.AlignmentFlag.AlignRight)
            weights_layout.addWidget(weight_label, i, 1)

            # 存储到字典中
            self.weight_labels[indicator] = weight_label

        # 将权重容器添加到weight_section
        weight_section.addWidget(weights_container)

        # 添加弹性空间，使内容靠上对齐
        weight_section.addStretch()

        top_section_layout.addLayout(file_section, 8)
        top_section_layout.addSpacing(20)
        top_section_layout.addLayout(weight_section, 2)

        # 将整个水平布局添加到主布局
        layout.addLayout(top_section_layout)

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

        # 初始加载权重
        self.get_weights()

    def get_weights(self):
        self.weight_thread = QThread()
        self.worker = WeightsWorker(self.controller)
        self.worker.moveToThread(self.weight_thread)

        self.weight_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_get_weights_finished)
        self.worker.error.connect(self.on_error)

        # 清理线程
        self.worker.finished.connect(self.weight_thread.quit)
        self.worker.error.connect(self.weight_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.weight_thread.finished.connect(self.weight_thread.deleteLater)

        self.weight_thread.start()

    def on_get_weights_finished(self, result):
        if result.get("code") != 0:
            DialogUtil.error(self, result.get("msg", "未知错误"))
            return

        weights_data = result.get("data", {})

        for indicator, weight_value in weights_data.items():
            if indicator in self.weight_labels:
                percentage = weight_value * 100
                self.weight_labels[indicator].setText(f"{percentage:.2f}%")

    def reset_weights(self):
        """重置权重为默认配置"""
        reset = DialogUtil.question(self, "确定要重置权重为默认值吗？", "重置权重确认")
        if not reset:
            return

        # 创建并启动重置线程
        self.reset_thread = QThread()
        self.reset_worker = ResetWeightsWorker(self.controller)
        self.reset_worker.moveToThread(self.reset_thread)

        self.reset_thread.started.connect(self.reset_worker.run)
        self.reset_worker.finished.connect(self.on_reset_weights_finished)
        self.reset_worker.error.connect(self.on_error)

        # 清理线程
        self.reset_worker.finished.connect(self.reset_thread.quit)
        self.reset_worker.error.connect(self.reset_thread.quit)
        self.reset_worker.finished.connect(self.reset_worker.deleteLater)
        self.reset_thread.finished.connect(self.reset_thread.deleteLater)

        self.reset_thread.start()

    def on_reset_weights_finished(self, result):
        if result.get("code") != 0:
            DialogUtil.error(self, result.get("msg", "重置权重失败"))
            return

        # 重置成功后，重新获取最新的权重配置
        DialogUtil.info(self, "权重已重置为默认值")

        # 重新获取权重更新界面
        self.get_weights()

    def run_analysis(self):
        if not self.selected_files:
            DialogUtil.warning(self, "请先选择文件")
            return

        self.invalid_check()
        # 如果检查后没有有效文件了，停止分析
        if not self.selected_files:
            DialogUtil.warning(self, "没有有效的文件可分析")
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

    def invalid_check(self):
        invalid_files = []
        for file_path in self.selected_files:
            if not os.path.isfile(file_path):
                invalid_files.append(file_path)

        if invalid_files:
            # 从已选列表中移除不存在的文件
            for file_path in invalid_files:
                self.selected_files.remove(file_path)

            # 刷新文件列表
            self.refresh_file_list()

            # 构建提示信息
            if len(invalid_files) == 1:
                message = f"文件 '{os.path.basename(invalid_files[0])}' 已不存在，已从列表中移除。"
            else:
                file_names = [os.path.basename(f) for f in invalid_files]
                message = f"以下 {len(invalid_files)} 个文件已不存在，已从列表中移除：\n" + "\n".join(file_names)

            DialogUtil.warning(self, message)

    def on_analysis_finished(self, result):
        main_window = self.window()
        if hasattr(main_window, "loading"):
            main_window.loading.hide()

        self.btn_analyze.setEnabled(True)

        if result.get("code") != 0:
            DialogUtil.error(self, result.get("msg", "未知错误"))
            return

        self.dashboard.update_score(result["data"])
        self.get_weights()

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

    def on_error(self, message):
        DialogUtil.error(self, f"获取记录失败: {message}")
