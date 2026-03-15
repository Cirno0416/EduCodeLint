from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QScrollArea, QWidget
)

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np


class CompareReportWindow(QDialog):

    def __init__(self, compare_data, parent=None):
        super().__init__(parent)

        self.compare_data = compare_data

        self.setWindowTitle("批次对比报告")
        self.resize(1000, 800)

        layout = QVBoxLayout(self)

        title = QLabel("代码质量批次对比报告")
        layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        container = QWidget()
        scroll_layout = QVBoxLayout(container)

        metrics = compare_data.get("metrics_comparison", {})

        # ================= 雷达图 =================
        radar_canvas = self.create_radar_chart(metrics)
        scroll_layout.addWidget(QLabel("指标评分对比"))
        scroll_layout.addWidget(radar_canvas)

        # ================= 平均问题数 =================
        issues_canvas = self.create_issue_chart(metrics)
        scroll_layout.addWidget(QLabel("平均每文件问题数"))
        scroll_layout.addWidget(issues_canvas)

        # ================= 严重度分布 =================
        severity_canvas = self.create_severity_chart(metrics)
        scroll_layout.addWidget(QLabel("问题严重度分布"))
        scroll_layout.addWidget(severity_canvas)

        # ================= 二级指标 =================
        secondary_canvas = self.create_secondary_chart(metrics)
        if secondary_canvas:
            scroll_layout.addWidget(QLabel("主要问题变化"))
            scroll_layout.addWidget(secondary_canvas)

        scroll.setWidget(container)
        layout.addWidget(scroll)

    # ================= 雷达图 =================
    def create_radar_chart(self, metrics):
        categories = list(metrics.keys())

        score_a = [metrics[c]["avg_score"]["batch1"] for c in categories]
        score_b = [metrics[c]["avg_score"]["batch2"] for c in categories]

        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False)

        score_a += score_a[:1]
        score_b += score_b[:1]
        angles = np.append(angles, angles[0])

        fig = Figure(figsize=(6, 5))
        ax = fig.add_subplot(111, polar=True)

        ax.plot(angles, score_a, label="批次A", linewidth=2)
        ax.fill(angles, score_a, alpha=0.2)

        ax.plot(angles, score_b, label="批次B", linewidth=2)
        ax.fill(angles, score_b, alpha=0.2)

        ax.set_thetagrids(angles[:-1] * 180 / np.pi, categories)

        ax.set_ylim(0, 100)

        ax.legend(loc="upper right")

        return FigureCanvas(fig)

    # ================= 平均问题数柱状图 =================
    def create_issue_chart(self, metrics):
        categories = list(metrics.keys())

        issue_a = [metrics[c]["avg_issues_per_file"]["batch1"] for c in categories]
        issue_b = [metrics[c]["avg_issues_per_file"]["batch2"] for c in categories]

        x = np.arange(len(categories))
        width = 0.35

        fig = Figure(figsize=(7, 4))
        ax = fig.add_subplot(111)

        ax.bar(x - width / 2, issue_a, width, label="批次A")
        ax.bar(x + width / 2, issue_b, width, label="批次B")

        ax.set_xticks(x)
        ax.set_xticklabels(categories, rotation=30)

        ax.set_ylabel("问题数")

        ax.legend()

        return FigureCanvas(fig)

    # ================= 严重度分布 =================
    def create_severity_chart(self, metrics):
        severity_a = {}
        severity_b = {}

        for data in metrics.values():

            s = data.get("severity_distribution", {})

            for k, v in s.get("batch1", {}).items():
                severity_a[k] = severity_a.get(k, 0) + v

            for k, v in s.get("batch2", {}).items():
                severity_b[k] = severity_b.get(k, 0) + v

        labels = list(set(severity_a.keys()) | set(severity_b.keys()))

        val_a = [severity_a.get(i, 0) for i in labels]
        val_b = [severity_b.get(i, 0) for i in labels]

        x = np.arange(len(labels))
        width = 0.35

        fig = Figure(figsize=(7, 4))
        ax = fig.add_subplot(111)

        ax.bar(x - width / 2, val_a, width, label="批次A")
        ax.bar(x + width / 2, val_b, width, label="批次B")

        ax.set_xticks(x)
        ax.set_xticklabels(labels)

        ax.set_ylabel("数量")

        ax.legend()

        return FigureCanvas(fig)

    # ================= 二级指标变化 =================
    def create_secondary_chart(self, metrics):
        changes = {}

        for data in metrics.values():

            sec = data.get("secondary_metric_comparison", {})

            for name, val in sec.items():
                changes[name] = val["difference"]

        if not changes:
            return None

        # 只展示变化最大的10个
        changes = dict(
            sorted(changes.items(), key=lambda x: abs(x[1]), reverse=True)[:10]
        )

        labels = list(changes.keys())
        values = list(changes.values())

        fig = Figure(figsize=(7, 4))
        ax = fig.add_subplot(111)

        ax.barh(labels, values)

        ax.set_xlabel("问题变化数量")

        return FigureCanvas(fig)
