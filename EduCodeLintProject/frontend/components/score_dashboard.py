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
        self.file_table.setColumnCount(4)
        self.file_table.setHorizontalHeaderLabels(
            ["文件路径", "得分", "状态", "操作"]
        )
        self.file_table.setSortingEnabled(True)

        self.file_table.setStyleSheet("""
            QListWidget#fileTable {
                border: 1px solid #ccc;
                border-radius: 3px;
            }
        """)

        # 禁止编辑
        self.file_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        header = self.file_table.horizontalHeader()
        # 文件路径列占据剩余空间
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        # 得分列自适应内容宽度
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        # 状态列自适应内容宽度
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
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

        self.file_table.setRowCount(len(files))

        for row, f in enumerate(files):
            # 文件名
            self.file_table.setItem(
                row, 0, QTableWidgetItem(f.get("file_path", ""))
            )
            # 得分
            self.file_table.setItem(
                row, 1, QTableWidgetItem(str(f.get("score", "--")))
            )
            # 状态
            self.file_table.setItem(
                row, 2, QTableWidgetItem(f.get("status", ""))
            )

            # ===== 操作按钮 =====
            btn = QPushButton("查看分析报告")
            btn.clicked.connect(
                lambda _, file_data=f: self.open_report(file_data)
            )
            self.file_table.setCellWidget(row, 3, btn)

        if data.get("status") == "success":
            self.btn_statistics.setEnabled(True)

    # =============================
    # 打开单文件详细报告
    # =============================
    def open_report(self, file_data):
        dialog = AnalyzeReportWindow(file_data)
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
