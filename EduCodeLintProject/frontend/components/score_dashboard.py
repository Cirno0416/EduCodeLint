from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout,
    QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView,
    QPushButton,
)
from PyQt6.QtGui import QFont

from frontend.components.report_window import ReportWindow
from frontend.components.statistics_window import StatisticsWindow
from frontend.utils.dialog_util import DialogUtil


class ScoreDashboard(QWidget):
    def __init__(self):
        super().__init__()

        self.analysis_data = None

        main_layout = QVBoxLayout(self)

        # =============================
        # 标题区域
        # =============================
        title = QLabel("分析结果")
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        title.setFont(font)

        main_layout.addWidget(title)

        # =============================
        # 统计按钮
        # =============================
        self.btn_statistics = QPushButton("查看批量统计报告")
        self.btn_statistics.setEnabled(False)
        self.btn_statistics.clicked.connect(self.show_statistics)

        main_layout.addWidget(self.btn_statistics)

        # ===== 文件列表表格 =====
        self.file_table = QTableWidget()
        self.file_table.setColumnCount(4)
        self.file_table.setHorizontalHeaderLabels(
            ["文件名", "得分", "状态", "操作"]
        )
        self.file_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.file_table.setSortingEnabled(True)

        # 禁止编辑
        self.file_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

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
                row, 0, QTableWidgetItem(f.get("file_name", ""))
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
        dialog = ReportWindow(file_data)
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
