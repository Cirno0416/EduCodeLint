from datetime import datetime
import pytz
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QScrollArea, QWidget,
    QSizePolicy, QHBoxLayout, QTableWidgetItem, QTableWidget, QHeaderView
)
from matplotlib.figure import Figure
import numpy as np
from backend.constant.severity_level import SeverityLevel
from frontend.components.scrollable_canvas import ScrollableCanvas


class CompareReportWindow(QDialog):

    def __init__(self, compare_data, parent=None):
        super().__init__(parent)

        self.compare_data = compare_data
        # 批次列表
        self.batches = compare_data["batches"]

        self.setWindowTitle("代码质量批次对比报告")
        self.resize(1000, 800)

        layout = QVBoxLayout(self)

        # 批次信息
        batch_label = self.create_batch_label()
        layout.addWidget(batch_label)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        container = QWidget()
        scroll_layout = QVBoxLayout(container)

        label_font = QFont()
        label_font.setPointSize(16)
        label_font.setBold(True)

        # ================= 雷达图 =================
        label = QLabel("指标评分对比")
        label.setFont(label_font)
        scroll_layout.addWidget(label)

        radar_layout = QVBoxLayout()
        radar_values = self.create_radar_values()
        radar_canvas = self.create_radar_chart()
        radar_layout.addWidget(radar_values)
        radar_layout.addWidget(radar_canvas)
        scroll_layout.addLayout(radar_layout)

        # ================= 平均问题数 =================
        label = QLabel("平均每文件问题数")
        label.setFont(label_font)
        scroll_layout.addWidget(label)
        issues_canvas = self.create_issue_chart()
        scroll_layout.addWidget(issues_canvas)

        # ================= 严重度分布 =================
        label = QLabel("问题严重度分布")
        label.setFont(label_font)
        scroll_layout.addWidget(label)
        severity_canvas = self.create_severity_chart()
        scroll_layout.addWidget(severity_canvas)

        # ================= 二级指标共性问题 =================
        secondary_canvas = self.create_secondary_chart()
        if secondary_canvas:
            label = QLabel("前十共性问题")
            label.setFont(label_font)
            scroll_layout.addWidget(label)

            desc_font = QFont()
            desc_font.setPointSize(10)
            desc = QLabel("共性问题强度 = 出现频率 × 严重程度 ÷ 波动程度 \n"
                          "值越高，说明该问题在多个批次中普遍存在、数量多且稳定，是最值得优先优化的问题。\n"
                          "只取至少在50%的批次中出现的指标。")
            desc.setFont(desc_font)

            scroll_layout.addWidget(desc)
            scroll_layout.addWidget(secondary_canvas)

        scroll.setWidget(container)
        layout.addWidget(scroll, stretch=1)

    # ===== 批次信息 =====
    def create_batch_label(self):
        text = ""
        for i, batch in enumerate(self.batches):
            text += f"批次{i+1}: {self.time_format(batch['created_at'])} ({batch['file_count']}个文件)  {batch['id']}\n"
        batch_label = QLabel(text)
        batch_label.setStyleSheet("""
            font-family: Consolas, Courier, monospace;
            font-size: 16px;
        """)
        return batch_label

    # ===== 雷达图表格 =====
    def create_radar_values(self):
        """使用 QTableWidget 创建雷达值表格，横向排列"""
        categories = list(self.batches[0]["metrics"].keys())
        batch_count = len(self.batches)
        color_list = ["#2196F3", "#FF9800", "#9C27B0", "#009688", "#FF5722", "#607D8B"]

        table = QTableWidget()
        table.setColumnCount(len(categories) + 1)  # +1 是批次列
        table.setRowCount(batch_count)
        table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # 固定高度，让所有行显示
        row_height = 30
        table.setFixedHeight(batch_count * row_height + 50)  # +50 表头高度
        table.verticalHeader().setVisible(False)  # 隐藏行号

        # 固定列宽
        col_width = 100
        for col in range(len(categories) + 1):
            table.setColumnWidth(col, col_width)
        table.setFixedWidth(7 * col_width + 10)

        # 设置表头
        table.setHorizontalHeaderLabels(["批次"] + categories)
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)  # 固定宽度，不自适应

        # 填充数据
        for i, batch in enumerate(self.batches):
            # 第一列：批次
            item = QTableWidgetItem(f"批次{i + 1}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setFont(QFont("Consolas", 11, QFont.Weight.Bold))
            table.setItem(i, 0, item)

            # 每个指标的得分
            for j, cat in enumerate(categories):
                score = self.normalize_score(batch["metrics"][cat]["avg_score"])
                item = QTableWidgetItem(f"{score:.2f}")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setFont(QFont("Consolas", 11, QFont.Weight.Bold))
                # 设置字体颜色
                item.setForeground(QColor(color_list[i % len(color_list)]))
                table.setItem(i, j + 1, item)

        # 禁止编辑和选择
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        table.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # 表格样式
        table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 6px;
                gridline-color: #ccc;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                font-weight: bold;
                font-family: Consolas;
                font-size: 12pt;
                padding: 4px;
            }
        """)

        # 居中显示表格
        container = QWidget()
        container_layout = QHBoxLayout(container)
        container_layout.addWidget(table)
        container_layout.setContentsMargins(0, 0, 0, 0)

        return container

    # ===== 雷达图 =====
    def create_radar_chart(self):
        categories = list(self.batches[0]["metrics"].keys())
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False)

        fig = Figure(figsize=(5, 5))
        ax = fig.add_subplot(111, polar=True)
        ax.set_yticks([20, 40, 60, 80, 100])
        ax.set_yticklabels(["20", "40", "60", "80", "100"])

        color_list = ["#2196F3", "#FF9800", "#9C27B0", "#009688", "#FF5722", "#607D8B"]

        for i, batch in enumerate(self.batches):
            scores = [self.normalize_score(batch["metrics"][c]["avg_score"]) for c in categories]
            scores += scores[:1]
            angle_loop = np.append(angles, angles[0])
            ax.plot(angle_loop, scores, label=f"批次{i+1}", linewidth=2, color=color_list[i % len(color_list)])
            ax.fill(angle_loop, scores, alpha=0.2, color=color_list[i % len(color_list)])

        ax.set_thetagrids(angles * 180 / np.pi, categories)
        ax.tick_params(pad=15)
        ax.set_ylim(0, 100)
        ax.legend(loc="upper left", bbox_to_anchor=(1.05, 1))
        return self.create_canvas(fig)

    # ===== 平均问题数 =====
    def create_issue_chart(self):
        categories = list(self.batches[0]["metrics"].keys())
        values_list = []
        for batch in self.batches:
            values = [batch["metrics"][c]["avg_issues_per_file"] for c in categories]
            values_list.append(values)
        return self.create_multi_bar_chart(categories, values_list, "平均每文件问题数")

    # ===== 严重度分布 =====
    def create_severity_chart(self):
        severity_all = []
        for batch in self.batches:
            severity_map = {}
            for c in batch["metrics"].values():
                for k, v in c.get("avg_severity_count", {}).items():
                    severity_map[k] = severity_map.get(k, 0) + v
            severity_all.append(severity_map)

        severity_order = [SeverityLevel.HIGH, SeverityLevel.MEDIUM, SeverityLevel.LOW]
        labels = [s for s in severity_order if any(s in sev for sev in severity_all)]
        values_list = [[sev.get(i, 0) for i in labels] for sev in severity_all]

        return self.create_multi_bar_chart(labels, values_list, "平均问题数量")

    # ===== 二级指标共性问题横向柱状图 =====
    def create_secondary_chart(self):
        common_issues = self.compare_data.get("common_issues", [])

        if not common_issues:
            return None

        # 构建 metric -> category 映射
        metric_category_map = {}

        for batch in self.batches:
            for category, data in batch["metrics"].items():
                for metric_name in data.get("avg_issues_by_name", {}).keys():
                    metric_category_map[metric_name] = category

        # 组装数据
        labels = []
        scores = []

        for item in common_issues:
            name = item["metric_name"]
            category = metric_category_map.get(name, "未知")

            # 拼接展示名
            display_name = f"{name}（{category}）"

            labels.append(display_name)
            scores.append(item["common_score"])

        # 绘图
        fig = Figure(figsize=(6, 4))
        ax = fig.add_subplot(111)

        bars = ax.barh(labels, scores)

        # 数值标签
        ax.bar_label(bars, padding=3, fmt="%.2f", fontsize=9)

        ax.set_xlabel("共性问题强度")

        ax.axvline(0, linestyle="--", linewidth=1)
        ax.grid(axis="x", linestyle="--", alpha=0.6)

        ax.margins(x=0.15)

        ax.invert_yaxis()

        return self.create_canvas(fig)

    # ===== 多柱状图 =====
    def create_multi_bar_chart(self, labels, values_list, ylabel):
        """
        创建多批次柱状图，自动调整柱宽，避免重叠
        labels: X轴标签
        values_list: [[批次1值], [批次2值], ...]
        ylabel: Y轴标签
        """
        x = np.arange(len(labels))
        batch_count = len(values_list)

        # 总宽度固定，每个柱子宽度自适应
        total_width = 0.8
        width = total_width / batch_count

        # 偏移起点，让柱子围绕中心对齐
        start = - total_width / 2 + width / 2

        fig = Figure(figsize=(6, 4))
        ax = fig.add_subplot(111)

        color_list = ["#2196F3", "#FF9800", "#9C27B0", "#009688", "#FF5722", "#607D8B"]

        for i, values in enumerate(values_list):
            pos = x + start + i * width
            bars = ax.bar(pos, values, width, label=f"批次{i + 1}", color=color_list[i % len(color_list)])
            ax.bar_label(bars, padding=3, fmt="%.1f", fontsize=9)  # 保留柱子上的数据

        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.set_ylabel(ylabel)
        ax.grid(axis="y", linestyle="--", linewidth=0.8, alpha=0.6)
        ax.margins(y=0.15)
        ax.legend()

        return self.create_canvas(fig)

    # ===== 画布封装 =====
    def create_canvas(self, fig):
        fig.tight_layout()
        fig.patch.set_facecolor("#f4f6f8")
        for ax in fig.axes:
            ax.set_facecolor("#f4f6f8")
        canvas = ScrollableCanvas(fig)
        canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        return canvas

    # ===== 工具函数 =====
    def normalize_score(self, v):
        return v * 100 if v <= 1 else v

    def time_format(self, created_at):
        local_tz = pytz.timezone('Asia/Shanghai')
        try:
            dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            if dt.tzinfo is not None:
                dt = dt.astimezone(local_tz)
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return created_at
