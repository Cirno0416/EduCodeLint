from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem,
    QHeaderView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class ScoreDashboard(QWidget):
    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)

        # ===== 标题 =====
        title = QLabel("分析结果")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        font = QFont()
        font.setPointSize(20)
        font.setBold(True)
        title.setFont(font)

        main_layout.addWidget(title)

        # ===== 文件结果表 =====
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["文件名", "评分", "问题数"])

        # 列宽自动拉伸
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)

        main_layout.addWidget(self.table)

        self.setLayout(main_layout)

    def update_score(self, data: dict):
        """
        这里接收 result["data"]
        """

        if not data:
            return

        results = data.get("results", [])

        self.table.setRowCount(len(results))

        for row, r in enumerate(results):
            file_name = r.get("file_name", f"文件{row+1}")
            score = r.get("score", "--")
            issues = len(r.get("issues", []))

            self.table.setItem(row, 0, QTableWidgetItem(str(file_name)))
            self.table.setItem(row, 1, QTableWidgetItem(str(score)))
            self.table.setItem(row, 2, QTableWidgetItem(str(issues)))
