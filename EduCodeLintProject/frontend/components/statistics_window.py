from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout,
    QLabel, QTabWidget, QWidget, QHBoxLayout
)
import matplotlib
from matplotlib.axes import Axes
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator

from backend.constant.metric_category import MetricCategory, CATEGORY_MAPPING
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
        layout.addWidget(create_summary_cards(analysis_data))

        # ========= Tabs =========
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        categories = [
            MetricCategory.CODE_STYLE,
            MetricCategory.CODE_SMELL,
            MetricCategory.POTENTIAL_ERROR,
            MetricCategory.SECURITY_VULNERABILITY,
            MetricCategory.DOCSTRING,
            MetricCategory.COMPLEXITY
        ]

        for cat in categories:
            if cat == MetricCategory.COMPLEXITY:
                self.tabs.addTab(create_complexity_tab(files), cat)
            elif cat == MetricCategory.DOCSTRING:
                self.tabs.addTab(create_docstring_tab(files), cat)
            else:
                self.tabs.addTab(create_general_tab(files, cat), cat)


# ==================================================
# 顶部统计卡片
# ==================================================
def create_summary_cards(analysis_data):
    files = analysis_data.get("results", [])
    weight_config = analysis_data.get("weight_config", {})

    container = QWidget()
    layout = QVBoxLayout(container)

    # ========================
    # 基础统计卡片
    # ========================
    stats_layout = QHBoxLayout()

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
                    font-size: 18px;
                    font-weight: bold;
                }
            """)
        stats_layout.addWidget(card)

    layout.addLayout(stats_layout)

    # ========================
    # 排除工具信息
    # ========================
    exclude_tools = analysis_data.get("exclude_tools", [])
    exclude_text = "、".join(exclude_tools) if exclude_tools else "无"
    exclude_label = QLabel(f"本次分析排除的工具：{exclude_text}")
    exclude_label.setStyleSheet("""
        QLabel {
            font-size: 13px;
            padding: 6px 2px;
        }
    """)

    layout.addWidget(exclude_label)

    # ========================
    # 权重 + 平均得分展示
    # ========================
    weight_layout = QHBoxLayout()

    # ===== 计算每个指标平均得分 =====
    category_scores = {k: [] for k in weight_config.keys()}

    for f in files:
        for s in f.get("summaries", []):
            cat = s.get("metric_category")
            score = s.get("score")

            if cat in category_scores and score is not None:
                category_scores[cat].append(score)

    # ===== 计算平均值 =====
    category_avg = {}
    for k, scores in category_scores.items():
        if scores:
            category_avg[k] = round(sum(scores) / len(scores), 2)
        else:
            category_avg[k] = 0

    # ===== 渲染卡片 =====
    for key, weight in weight_config.items():
        percent = round(weight * 100, 1)
        avg_score = category_avg.get(key, 0)

        card = QLabel(
            f"{key}\n"
            f"平均得分：{avg_score}\n"
            f"权重：{percent}%"
        )

        card.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card.setStyleSheet("""
            QLabel {
                background-color: #ffffff;
                border: 1px solid #dcdde1;
                border-radius: 8px;
                padding: 15px;
                font-size: 14px;
                font-weight: bold;
            }
        """)

        weight_layout.addWidget(card)

    layout.addLayout(weight_layout)

    return container


# ==================================================
# 风格规范 / 代码异味 / 潜在错误 / 安全漏洞
# ==================================================
def create_general_tab(files, category):
    figure = Figure(figsize=(10, 7), dpi=100)
    canvas = FigureCanvas(figure)

    # 预定义所有二级指标
    metric_list = CATEGORY_MAPPING.get(category, [])
    metric_count = {m: 0 for m in metric_list}
    metric_file_map = {m: 0 for m in metric_list}

    severity_count = {
        SeverityLevel.HIGH: 0,
        SeverityLevel.MEDIUM: 0,
        SeverityLevel.LOW: 0
    }

    for f in files:
        appeared_metrics = set()  # 每个文件去重

        for s in f.get("summaries", []):
            if s.get("metric_category") != category:
                continue

            for issue in s.get("issues", []):
                metric = issue.get("metric_name", MetricName.UNKNOWN_METRIC_NAME)
                sev = issue.get("severity", SeverityLevel.LOW)

                if metric in metric_count:
                    metric_count[metric] += 1
                    appeared_metrics.add(metric)

                if sev in severity_count:
                    severity_count[sev] += 1

        # ===== 每个文件只计一次 =====
        for metric in appeared_metrics:
            metric_file_map[metric] = metric_file_map.get(metric, 0) + 1

    # ===============================
    # 子图1：问题数量
    # ===============================
    ax1 = figure.add_subplot(221)

    sorted_metric_count = dict(
        sorted(metric_count.items(), key=lambda x: x[1], reverse=True)
    )

    draw_horizontal_bar_chart(
        ax=ax1,
        data_dict=sorted_metric_count,
        title="二级指标问题数量",
        xlabel="问题数量"
    )

    # ===============================
    # 子图2：严重度
    # ===============================
    ax2 = figure.add_subplot(222)

    total = sum(severity_count.values()) or 1

    severity_list = [SeverityLevel.LOW, SeverityLevel.MEDIUM, SeverityLevel.HIGH]
    color_map = {
        SeverityLevel.LOW: "#5CB85C",
        SeverityLevel.MEDIUM: "#F0AD4E",
        SeverityLevel.HIGH: "#D9534F"
    }

    severity_display = {}

    for k in severity_list:
        count = severity_count[k]
        percent = round(count / total * 100, 1)
        severity_display[f"{k} ({percent}%)"] = count

    draw_horizontal_bar_chart(
        ax=ax2,
        data_dict=severity_display,
        title="严重度分布",
        xlabel="问题数量",
        invert_y=False,
        colors=[color_map[k] for k in severity_list]
    )

    # ===============================
    # 子图3：文件数量
    # ===============================
    ax3 = figure.add_subplot(223)

    sorted_file_map = dict(
        sorted(metric_file_map.items(), key=lambda x: x[1], reverse=True)
    )

    draw_horizontal_bar_chart(
        ax=ax3,
        data_dict=sorted_file_map,
        title="涉及文件数量",
        xlabel="文件数量"
    )

    # ===============================
    # 布局
    # ===============================
    figure.subplots_adjust(
        left=0.15,
        right=0.95,
        top=0.9,
        bottom=0.1,
        hspace=0.5,
        wspace=0.3
    )

    return canvas


# ==================================================
# 复杂度
# ==================================================
def create_complexity_tab(files):
    figure = Figure(figsize=(6, 4), dpi=100)
    canvas = FigureCanvas(figure)

    complexity_values = []

    for f in files:
        found = False
        for s in f.get("summaries", []):
            if s.get("metric_category") != MetricCategory.COMPLEXITY:
                continue

            for issue in s.get("issues", []):
                try:
                    complexity_value = int(issue.get("rule_id", 0))
                    # 超过31的复杂度都归为31，避免极端值拉长图表
                    complexity_value = min(31, complexity_value)
                    complexity_values.append(complexity_value)
                    found = True
                except:
                    pass

        # 低复杂度的不会返回issue所以找不到，默认为10
        if not found:
            complexity_values.append(10)

    ax = figure.add_subplot(121)

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
    ax.set_xlabel("最大圈复杂度")
    ax.set_ylabel("文件数量")
    ax.grid(axis='y', linestyle='--', alpha=0.5)

    figure.subplots_adjust(
        left=0.1,
        right=0.95,
        top=0.9,
        bottom=0.15
    )

    return canvas


# ==================================================
# 注释与文档
# ==================================================
def create_docstring_tab(files):
    figure = Figure(figsize=(6, 6), dpi=100)
    canvas = FigureCanvas(figure)

    metric_list = CATEGORY_MAPPING.get(MetricCategory.DOCSTRING, [])
    # ===== 问题统计 =====
    metric_issue_count = {m: 0 for m in metric_list}

    # ===== 文件统计 =====
    metric_file_count = {m: 0 for m in metric_list}

    for f in files:
        appeared_metrics = set()
        has_doc_issue = False

        for s in f.get("summaries", []):
            if s.get("metric_category") != MetricCategory.DOCSTRING:
                continue

            for issue in s.get("issues", []):
                metric = issue.get("metric_name", MetricName.UNKNOWN_METRIC_NAME)

                # ===== 问题统计 =====
                if metric in metric_issue_count:
                    metric_issue_count[metric] += 1

                # ===== 文件统计 =====
                appeared_metrics.add(metric)
                has_doc_issue = True

        # ===== 文件级统计 =====
        if not has_doc_issue:
            # 没问题 → 标准docstring
            metric_file_count[MetricName.STANDARD_DOCSTRING] += 1
        else:
            for metric in appeared_metrics:
                if metric in metric_file_count:
                    metric_file_count[metric] += 1

    # ===============================
    # 图1：问题数量
    # ===============================
    ax1 = figure.add_subplot(211)

    draw_horizontal_bar_chart(
        ax=ax1,
        data_dict=metric_issue_count,
        title="Docstring问题数量",
        xlabel="问题数量",
    )

    # ===============================
    # 图2：文件数量
    # ===============================
    ax2 = figure.add_subplot(212)

    draw_horizontal_bar_chart(
        ax=ax2,
        data_dict=metric_file_count,
        title="Docstring涉及文件数量",
        xlabel="文件数量",
    )

    # 布局
    figure.subplots_adjust(
        left=0.15,
        right=0.7,
        top=0.9,
        bottom=0.1,
        hspace=0.5
    )

    return canvas


def draw_horizontal_bar_chart(
        ax: Axes,
        data_dict,
        title,
        xlabel,
        invert_y=True,
        colors=None
):
    """
    通用横向柱状图绘制函数
    """
    if not data_dict:
        ax.text(0.5, 0.5, "无相关问题或数据", ha="center")
        return

    items = list(data_dict.items())
    values = [v for k, v in items]
    labels = [k for k, v in items]
    y_pos = list(range(len(labels)))

    bars = ax.barh(
        y_pos,
        values,
        height=0.5,
        color=colors
    )

    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels)

    ax.set_xlim(left=0)

    # 处理单柱情况
    if len(labels) == 1:
        ax.set_ylim(-0.8, 0.8)
    else:
        ax.set_ylim(-0.5, len(labels) - 0.5)

    max_value = max(values)

    # 设置x轴范围，处理全零的情况
    if max_value == 0:
        # 所有值都是0，设置范围为[0, 1]避免警告
        ax.set_xlim(0, 1)
    else:
        # 有非零值，留15%的空白
        ax.set_xlim(0, max_value * 1.15)

    # 留白
    ax.set_ymargin(0.1)

    offset = ax.get_xlim()[1] * 0.01

    for bar in bars:
        width = bar.get_width()
        ax.text(
            width + offset,
            bar.get_y() + bar.get_height() / 2,
            str(int(width)),
            va='center',
            ha='left'
        )

    ax.xaxis.set_major_locator(MaxNLocator(integer=True))

    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.grid(axis='x', linestyle='--', alpha=0.5)

    if invert_y:
        ax.invert_yaxis()
