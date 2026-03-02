from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout,
    QLabel, QTabWidget, QWidget, QHBoxLayout
)
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator

from backend.constant.metric_category import MetricCategory
from backend.constant.metric_name import MetricName
from backend.constant.severity_level import SeverityLevel

# 中文支持
matplotlib.rcParams["font.sans-serif"] = ["SimHei"]
matplotlib.rcParams["axes.unicode_minus"] = False


class StatisticsWindow(QDialog):

    def __init__(self, analysis_data):
        super().__init__()

        self.setWindowTitle("批量统计报告")
        self.resize(1200, 800)

        layout = QVBoxLayout(self)

        files = analysis_data.get("results", [])
        if len(files) <= 1:
            layout.addWidget(QLabel("单文件分析不展示总体统计"))
            return

        # ========= 顶部统计卡片 =========
        layout.addWidget(create_summary_cards(files))

        # ========= Tabs =========
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        categories = [
            MetricCategory.CODE_STYLE,
            MetricCategory.CODE_SMELL,
            MetricCategory.POTENTIAL_ERROR,
            MetricCategory.SECURITY_VULNERABILITY,
            MetricCategory.DOCUMENTATION,
            MetricCategory.COMPLEXITY
        ]

        for cat in categories:
            if cat == MetricCategory.COMPLEXITY:
                self.tabs.addTab(create_complexity_tab(files), cat)
            else:
                self.tabs.addTab(create_general_tab(files, cat), cat)


# ==================================================
# 顶部统计卡片
# ==================================================
def create_summary_cards(files):
    container = QWidget()
    layout = QHBoxLayout(container)

    total_files = len(files)
    total_issues = sum(
        sum(s.get("issue_count", 0) for s in f.get("summaries", []))
        for f in files
    )
    avg_score = round(
        sum(f.get("score", 0) for f in files) / total_files,
        2
    )

    cards = [
        ("文件数量", total_files),
        ("总问题数", total_issues),
        ("平均得分", avg_score)
    ]

    for title, value in cards:
        card = QLabel(f"{title}\n{value}")
        card.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card.setStyleSheet("""
            QLabel {
                background-color: #f5f6fa;
                border-radius: 10px;
                padding: 20px;
                font-size: 18px;
                font-weight: bold;
            }
        """)
        layout.addWidget(card)

    return container


# ==================================================
# 风格规范 / 代码异味 / 潜在错误 / 安全漏洞
# ==================================================
def create_general_tab(files, category):
    figure = Figure(figsize=(6, 5), dpi=100)
    canvas = FigureCanvas(figure)
    canvas.setFixedSize(650, 500)

    metric_count = {}
    severity_count = {
        SeverityLevel.HIGH: 0,
        SeverityLevel.MEDIUM: 0,
        SeverityLevel.LOW: 0
    }

    for f in files:
        for s in f.get("summaries", []):
            if s.get("metric_category") != category:
                continue

            for issue in s.get("issues", []):
                metric = issue.get("metric_name", MetricName.UNKNOWN_METRIC_NAME)
                sev = issue.get("severity", SeverityLevel.LOW)

                metric_count[metric] = metric_count.get(metric, 0) + 1
                if sev in severity_count:
                    severity_count[sev] += 1

    # ===============================
    # 子图1：二级指标
    # ===============================
    ax1 = figure.add_subplot(211)

    if metric_count:
        sorted_items = sorted(
            metric_count.items(),
            key=lambda x: x[1],
            reverse=True
        )

        values = [i[1] for i in sorted_items]
        labels = [i[0] for i in sorted_items]

        y_pos = list(range(len(labels)))

        bars = ax1.barh(y_pos, values, height=0.5)

        ax1.set_yticks(y_pos)
        ax1.set_yticklabels(labels)

        if len(labels) == 1:
            ax1.set_ylim(-0.8, 0.8)
        else:
            ax1.set_ylim(-0.5, len(labels) - 0.5)

        max_value = max(values)

        # 留白
        ax1.set_xlim(0, max_value * 1.15)
        ax1.set_ymargin(0.1)

        # 1% 的横轴长度
        offset = ax1.get_xlim()[1] * 0.01

        # 使用 bars 精准贴柱
        for bar in bars:
            width = bar.get_width()
            ax1.text(
                width + offset,
                bar.get_y() + bar.get_height() / 2,
                str(int(width)),
                va='center',
                ha='left'
            )

        # 横坐标为整数
        ax1.xaxis.set_major_locator(MaxNLocator(integer=True))

        ax1.set_title("二级指标数量")
        ax1.set_xlabel("问题数量")
        ax1.grid(axis='x', linestyle='--', alpha=0.5)
        ax1.invert_yaxis()

    else:
        ax1.text(0.5, 0.5, "无数据", ha="center")

    # ===============================
    # 子图2：严重度比例
    # ===============================
    ax2 = figure.add_subplot(212)

    total = sum(severity_count.values())

    if total > 0:
        labels = []
        values = []

        for k in [SeverityLevel.LOW, SeverityLevel.MEDIUM, SeverityLevel.HIGH]:
            count = severity_count[k]
            percent = round(count / total * 100, 1)
            labels.append(f"{k} ({percent}%)")
            values.append(count)

        y_pos = range(len(labels))
        bars = ax2.barh(y_pos, values, height=0.5)

        ax2.set_yticks(y_pos)
        ax2.set_yticklabels(labels)

        max_value = max(values)
        ax2.set_xlim(0, max_value * 1.15)
        ax2.set_ymargin(0.1)

        offset = ax1.get_xlim()[1] * 0.01

        for bar in bars:
            width = bar.get_width()
            ax2.text(
                width + offset,
                bar.get_y() + bar.get_height() / 2,
                str(int(width)),
                va='center',
                ha='left'
            )

        # 横坐标为整数
        ax2.xaxis.set_major_locator(MaxNLocator(integer=True))

        ax2.set_title("严重度比例")
        ax2.set_xlabel("问题数量")
        ax2.grid(axis='x', linestyle='--', alpha=0.5)

    else:
        ax2.text(0.5, 0.5, "无严重度数据", ha="center")

    # 固定布局，不自动缩放
    figure.subplots_adjust(
        left=0.30,
        right=0.95,
        top=0.92,
        bottom=0.08,
        hspace=0.4
    )

    return canvas


# ==================================================
# 复杂度
# ==================================================
def create_complexity_tab(files):
    figure = Figure(figsize=(6, 4), dpi=100)
    canvas = FigureCanvas(figure)
    canvas.setFixedSize(650, 450)

    complexity_values = []

    for f in files:
        found = False
        for s in f.get("summaries", []):
            if s.get("metric_category") != MetricCategory.COMPLEXITY:
                continue

            for issue in s.get("issues", []):
                try:
                    complexity_value = int(issue.get("rule_id", 0))
                    complexity_value = min(31, complexity_value)
                    complexity_values.append(complexity_value)
                    found = True
                except:
                    pass

        # 低复杂度默认为10
        if not found:
            complexity_values.append(10)

    ax = figure.add_subplot(111)

    # 基础分箱
    bins = [0, 11, 16, 21, 26, 31, 36]

    n, bins, patches = ax.hist(
        complexity_values,
        bins=bins,
        edgecolor='black'
    )

    # 为每个柱子设置颜色
    # 绿->黄->红
    colors = ["#2ca02c", "#7fc97f", "#ffff99", "#ff7f0e", "#d62728", "#8b0000"]
    for patch, color in zip(patches, colors):
        patch.set_facecolor(color)

    # 顶部留白防止数字贴顶
    max_height = max(n) if len(n) > 0 else 0
    ax.set_ylim(0, max_height * 1.15)

    # 数字标注与柱子间的偏移
    offset = ax.get_ylim()[1] * 0.01

    for count, patch in zip(n, patches):
        if count > 0:
            ax.text(
                patch.get_x() + patch.get_width() / 2,
                count + offset,
                str(int(count)),
                ha='center',
                va='bottom'
            )

    centers = [(bins[i] + bins[i + 1]) / 2 for i in range(len(bins) - 1)]
    labels = ["0–10", "11–15", "16–20", "21–25", "26–30", "≥31"]

    ax.set_xticks(centers)
    ax.set_xticklabels(labels)

    # 纵坐标为整数
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))

    ax.set_title("各文件最大圈复杂度分布")
    ax.set_xlabel("最大复杂度")
    ax.set_ylabel("文件数量")
    ax.grid(axis='y', linestyle='--', alpha=0.5)

    figure.subplots_adjust(
        left=0.30,
        right=0.95,
        top=0.9,
        bottom=0.12
    )

    return canvas
