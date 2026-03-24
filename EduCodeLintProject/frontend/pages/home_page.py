import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QFrame, QHBoxLayout
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from backend.constant.metric_category import MetricCategory


class HomePage(QWidget):

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(60, 60, 60, 60)
        main_layout.setSpacing(30)

        # ===== 标题 =====
        title = QLabel("EduCodeLint")
        title.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("教学代码质量分析系统")
        subtitle.setFont(QFont("Arial", 16))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: gray;")

        # ===== 分割线 =====
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: #dddddd;")

        # ===== 样图 =====
        chart_layout = QHBoxLayout()
        chart_layout.setSpacing(30)
        radar = self.create_demo_radar_chart()
        bar = self.create_demo_bar_chart()
        chart_layout.addWidget(self.wrap_card(radar))
        chart_layout.addWidget(self.wrap_card(bar))

        # ===== 底部说明 =====
        footer = QLabel("用于教学场景的代码质量评估与反馈系统")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet("color: #999999;")

        main_layout.addStretch()
        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)
        main_layout.addWidget(line)
        main_layout.addStretch()
        main_layout.addLayout(chart_layout)
        main_layout.addWidget(footer)

        self.setLayout(main_layout)

    def wrap_card(self, widget):
        """卡片包裹"""
        frame = QFrame()
        layout = QVBoxLayout()
        layout.addWidget(widget)
        frame.setLayout(layout)

        frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 10px;
                border: 1px solid #e5e5e5;
            }
        """)
        return frame

    def create_demo_radar_chart(self):
        categories = [
            MetricCategory.DOCSTRING,
            MetricCategory.CODE_SMELL,
            MetricCategory.COMPLEXITY,
            MetricCategory.POTENTIAL_ERROR,
            MetricCategory.SECURITY_VULNERABILITY,
            MetricCategory.CODE_STYLE,
        ]
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False)

        fig = Figure(figsize=(2, 2))
        ax = fig.add_subplot(111, polar=True)

        # 三批次假数据
        batch_data = [
            [82, 68, 75, 70, 65, 90],
            [88, 72, 80, 76, 70, 100],
            [92, 78, 85, 82, 75, 95],
        ]
        colors = ["#2196F3", "#FF9800", "#9C27B0"]

        for i, data in enumerate(batch_data):
            data = data + [data[0]]  # 闭合
            angle_loop = np.append(angles, angles[0])
            ax.plot(angle_loop, data, color=colors[i], linewidth=2)
            ax.fill(angle_loop, data, color=colors[i], alpha=0.15)

        # 坐标轴标签和网格
        ax.set_xticks(angles)
        ax.set_xticklabels([c for c in categories], fontsize=7)
        ax.set_yticks([20, 40, 60, 80, 100])
        ax.set_yticklabels(["20", "40", "60", "80", "100"], fontsize=7)
        ax.grid(True, color="#CCCCCC", linestyle="--", linewidth=0.5)
        ax.set_ylim(0, 100)

        # 图例
        ax.legend(["批次1", "批次2", "批次3"], fontsize=7, loc="upper right", bbox_to_anchor=(1.5, 1.1))

        # 留白，防止裁剪
        fig.subplots_adjust(left=0.15, right=0.85, top=0.90, bottom=0.10)

        return FigureCanvas(fig)

    def create_demo_bar_chart(self):
        categories = [
            MetricCategory.CODE_STYLE,
            MetricCategory.CODE_SMELL,
            MetricCategory.COMPLEXITY,
            MetricCategory.POTENTIAL_ERROR,
            MetricCategory.SECURITY_VULNERABILITY,
            MetricCategory.DOCSTRING
        ]

        batch1 = [11.5, 12.5, 1.0, 7.8, 4.6, 3.2]
        batch2 = [10.8, 12.0, 0.7, 8.4, 9.1, 6.9]
        batch3 = [6.5, 11.6, 0.5, 10.1, 7.8, 5.5]

        x = np.arange(len(categories))
        width = 0.25

        fig = Figure(figsize=(4, 2))
        ax = fig.add_subplot(111)

        ax.bar(x - width, batch1, width, label="批次1")
        ax.bar(x, batch2, width, label="批次2")
        ax.bar(x + width, batch3, width, label="批次3")

        # 坐标轴文字
        ax.set_xticks(x)
        ax.set_xticklabels([c for c in categories], fontsize=7)
        ax.set_yticks([0, 5, 10, 15])
        ax.set_yticklabels(["0", "5", "10", "15"], fontsize=7)

        # 网格
        ax.grid(True, axis='y', color="#CCCCCC", linestyle="--", linewidth=0.5)

        # 图例
        ax.legend(fontsize=7, loc="upper right", bbox_to_anchor=(1.0, 1.0))

        # 留白
        fig.subplots_adjust(left=0.15, right=0.85, top=0.9, bottom=0.15)

        return FigureCanvas(fig)
