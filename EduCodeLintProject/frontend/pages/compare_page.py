from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox,
    QTableWidget, QTableWidgetItem,
    QHeaderView
)

from frontend.controllers.compare_controller import CompareController


class ComparePage(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.controller = CompareController()

        layout = QVBoxLayout(self)

        # ===== 选择批次 =====
        top_layout = QHBoxLayout()

        top_layout.addWidget(QLabel("Batch 1:"))
        self.combo_batch1 = QComboBox()
        top_layout.addWidget(self.combo_batch1)

        top_layout.addWidget(QLabel("Batch 2:"))
        self.combo_batch2 = QComboBox()
        top_layout.addWidget(self.combo_batch2)

        self.btn_compare = QPushButton("Compare")
        self.btn_compare.clicked.connect(self.compare_batches)

        top_layout.addWidget(self.btn_compare)
        top_layout.addStretch()

        layout.addLayout(top_layout)

        # ===== 总体趋势 =====
        self.lbl_overall = QLabel("Overall Trend: -")
        layout.addWidget(self.lbl_overall)

        # ===== 指标对比表格 =====
        self.table_metrics = QTableWidget()
        self.table_metrics.setColumnCount(6)

        self.table_metrics.setHorizontalHeaderLabels([
            "Metric",
            "Batch1 Score",
            "Batch2 Score",
            "Score Diff",
            "Batch1 Issues",
            "Batch2 Issues"
        ])

        self.table_metrics.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        layout.addWidget(self.table_metrics)

    def set_analysis_list(self, analysis_list):
        """
        外部调用：填充可选的 analysis id
        """
        self.combo_batch1.clear()
        self.combo_batch2.clear()

        for analysis in analysis_list:
            analysis_id = analysis["id"]
            self.combo_batch1.addItem(analysis_id)
            self.combo_batch2.addItem(analysis_id)

    def compare_batches(self):

        analysis_id_1 = self.combo_batch1.currentText()
        analysis_id_2 = self.combo_batch2.currentText()

        if not analysis_id_1 or not analysis_id_2:
            return

        result = self.controller.compare(analysis_id_1, analysis_id_2)

        if result.get("code") != 0:
            return

        data = result["data"]

        # ===== 显示总体趋势 =====
        trend = data.get("overall_trend", "-")
        weighted_diff = data.get("weighted_difference", 0)

        self.lbl_overall.setText(
            f"Overall Trend: {trend} (Weighted diff: {weighted_diff:.2f})"
        )

        # ===== 指标表格 =====
        metrics = data["metrics"]

        self.table_metrics.setRowCount(len(metrics))

        for row, (metric, info) in enumerate(metrics.items()):

            score_info = info["avg_score"]
            issue_info = info["avg_issues_per_file"]

            self.table_metrics.setItem(row, 0, QTableWidgetItem(metric))

            self.table_metrics.setItem(
                row, 1, QTableWidgetItem(str(score_info["batch1"]))
            )
            self.table_metrics.setItem(
                row, 2, QTableWidgetItem(str(score_info["batch2"]))
            )
            self.table_metrics.setItem(
                row, 3, QTableWidgetItem(str(score_info["difference"]))
            )

            self.table_metrics.setItem(
                row, 4, QTableWidgetItem(str(issue_info["batch1"]))
            )
            self.table_metrics.setItem(
                row, 5, QTableWidgetItem(str(issue_info["batch2"]))
            )
