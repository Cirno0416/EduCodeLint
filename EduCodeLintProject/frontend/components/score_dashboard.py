from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout,
    QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView,
    QPushButton, QHBoxLayout,
)
from PyQt6.QtGui import QFont

from frontend.components.analyze_report_window import AnalyzeReportWindow
from frontend.components.statistics_window import StatisticsWindow
from frontend.utils.dialog_util import DialogUtil


class ScoreDashboard(QWidget):
    def __init__(self):
        super().__init__()

        self.analysis_data = None

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # =============================
        # 标题区域
        # =============================
        header_layout = QHBoxLayout()

        title = QLabel("分析结果")
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        title.setFont(font)
        header_layout.addWidget(title)

        header_layout.addStretch()

        # 统计按钮
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)

        self.btn_statistics = QPushButton("查看批量统计报告")
        self.btn_statistics.setEnabled(False)
        self.btn_statistics.clicked.connect(self.show_statistics)
        self.btn_statistics.setFont(font)
        header_layout.addWidget(self.btn_statistics)

        main_layout.addLayout(header_layout)

        # ===== 文件列表表格 =====
        self.file_table = QTableWidget()
        self.file_table.setObjectName("fileTable")
        self.file_table.setColumnCount(3)
        self.file_table.setHorizontalHeaderLabels(
            ["文件路径", "得分", "操作"]
        )
        self.file_table.setSortingEnabled(True)

        self.file_table.setStyleSheet("""
            QTableWidget::item:selected {
                background-color: #f0f0f0;    /* 背景色 */
                color: #000000; 
            }
            QTableWidget::item {
                border: none;                 /* 移除每个格子前的蓝线 */
            }
        """)

        # 禁止编辑
        self.file_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        # 去掉焦点
        self.file_table.setFocusPolicy(
            Qt.FocusPolicy.NoFocus
        )

        # 整行选中
        self.file_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        header = self.file_table.horizontalHeader()
        # 文件路径列占据剩余空间
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        # 得分列自适应内容宽度
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        # 操作列固定宽度
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)

        font = QFont()
        font.setBold(True)
        header.setFont(font)

        main_layout.addWidget(self.file_table)

    # =============================
    # 更新数据
    # =============================
    def update_score(self, data):
        self.analysis_data = data
        files = data.get("results", [])
        exclude_tools = data.get("exclude_tools", [])

        self.file_table.setRowCount(len(files))

        for row, f in enumerate(files):
            # 文件名
            self.file_table.setItem(
                row, 0, QTableWidgetItem(f.get("file_path", ""))
            )
            # 得分
            score_value = f.get("score", "--")
            display_score = f"{score_value:.2f}" if isinstance(score_value, (int, float)) else str(score_value)
            self.file_table.setItem(row, 1, QTableWidgetItem(display_score))

            # ===== 操作按钮 =====
            btn = QPushButton("查看分析报告")
            btn.clicked.connect(
                lambda _, file_data=f: self.open_report(file_data, exclude_tools)
            )
            self.file_table.setCellWidget(row, 2, btn)

        if data.get("status") == "success":
            self.btn_statistics.setEnabled(True)

    # =============================
    # 打开单文件详细报告
    # =============================
    def open_report(self, file_data, exclude_tools):
        dialog = AnalyzeReportWindow(file_data, exclude_tools)
        dialog.exec()

    # =============================
    # 批量统计报告
    # =============================
    def show_statistics(self):
        files = self.analysis_data.get("results", [])

        if len(files) <= 1:
            DialogUtil.warning(self, "单文件分析不支持批量统计")
            return

        dialog = StatisticsWindow(self.analysis_data)
        dialog.exec()

    # =============================
    # 重置面板
    # =============================
    def reset(self):
        """清空当前展示的数据"""
        self.analysis_data = None

        # 关闭排序避免清空时触发排序问题
        self.file_table.setSortingEnabled(False)

        # 清空表格
        self.file_table.setRowCount(0)
        self.file_table.clearContents()

        # 关闭统计按钮
        self.btn_statistics.setEnabled(False)

        # 重新开启排序
        self.file_table.setSortingEnabled(True)
