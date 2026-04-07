from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout,
    QLabel, QTabWidget, QWidget, QHBoxLayout, QScrollArea
)
import matplotlib
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator

from backend.constant.metric_category import MetricCategory, CATEGORY_MAPPING
from backend.constant.metric_name import MetricName
from backend.constant.severity_level import SeverityLevel
from frontend.components.file_list_panel import FileListPanel
from frontend.components.scrollable_canvas import ScrollableCanvas

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

        self.metric_to_files = self._build_metric_file_map(analysis_data)

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
                tab_content = create_complexity_tab(files)
            else:
                # 注释不区分严重度，其他Tab才显示
                show_severity = cat != MetricCategory.DOCSTRING
                tab_content = create_general_tab(files, cat, self.metric_to_files, show_severity)

            self.tabs.addTab(tab_content, cat)

    def _build_metric_file_map(self, analysis_data):
        """构建全局映射：metric_name -> list of file_path"""
        metric_files = {}
        files = analysis_data.get("results", [])
        for file_info in files:
            file_path = file_info.get("file_path", "未知路径")
            for summary in file_info.get("summaries", []):
                for issue in summary.get("issues", []):
                    metric_name = issue.get("metric_name")
                    if not metric_name:
                        continue
                    metric_files.setdefault(metric_name, set()).add(file_path)
        # 将 set 转为 list 以便显示
        return {
            metric: list(paths) for metric, paths in metric_files.items()
        }

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
# 风格规范 / 代码异味 / 潜在错误 / 安全漏洞 / 注释
# ==================================================
def create_general_tab(files, category, metric_to_files, show_severity=True):
    """
    通用统计报告 Tab 创建函数
    :param files: 文件列表
    :param category: 指标类别
    :param metric_to_files: 问题到文件路径的映射
    :param show_severity: 是否显示严重度图（DOCSTRING 类别不显示）
    """
    widget = QWidget()
    main_layout = QHBoxLayout(widget)

    # ========== 左侧区域 ==========
    left_scroll = QScrollArea()
    # 允许内容调整，但滚动条按需出现
    left_scroll.setWidgetResizable(True)
    left_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
    left_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

    left_widget = QWidget()
    left_layout = QVBoxLayout(left_widget)
    left_layout.setContentsMargins(0, 0, 0, 0)  # 清除外边距
    left_layout.setSpacing(0)  # 清除控件间距

    # 预定义所有二级指标
    metric_list = CATEGORY_MAPPING.get(category, [])
    metric_count = {m: 0 for m in metric_list}
    metric_file_map = {m: 0 for m in metric_list}

    # 严重度统计（仅在 show_severity=True 时使用）
    severity_count = None
    if show_severity:
        severity_count = {SeverityLevel.HIGH: 0, SeverityLevel.MEDIUM: 0, SeverityLevel.LOW: 0}

    for f in files:
        appeared_metrics = set()
        for s in f.get("summaries", []):
            if s.get("metric_category") != category:
                continue
            for issue in s.get("issues", []):
                metric = issue.get("metric_name", MetricName.UNKNOWN_METRIC_NAME)
                if metric in metric_count:
                    metric_count[metric] += 1
                    appeared_metrics.add(metric)

                # 统计严重度
                if show_severity:
                    sev = issue.get("severity", SeverityLevel.LOW)
                    if sev in severity_count:
                        severity_count[sev] += 1
        for metric in appeared_metrics:
            metric_file_map[metric] = metric_file_map.get(metric, 0) + 1

    # 创建图表
    if show_severity:
        figure = Figure(figsize=(9, 12), dpi=100)
        canvas = ScrollableCanvas(figure)
        create_charts(figure, metric_count, metric_file_map, severity_count, show_severity=True)
        canvas.setMinimumHeight(780)
    else:
        figure = Figure(figsize=(9, 7), dpi=100)
        canvas = ScrollableCanvas(figure)
        create_charts(figure, metric_count, metric_file_map, show_severity=False)
        canvas.setMinimumHeight(520)

    left_layout.addWidget(canvas)
    left_scroll.setWidget(left_widget)

    # ========== 右侧区域 ==========
    metric_list = CATEGORY_MAPPING.get(category, [])
    right_panel = FileListPanel()
    right_panel.set_data(
        metric_list=metric_list,
        metric_to_files=metric_to_files,
        title="点击问题查看涉及的文件"
    )

    main_layout.addWidget(left_scroll, 6)
    main_layout.addWidget(right_panel, 4)

    return widget


def create_charts(figure, metric_count, metric_file_map, severity_count=None, show_severity=True):
    """
    在给定的 Figure 上绘制图表
    :param figure: matplotlib Figure 对象
    :param metric_count: 问题数量字典
    :param metric_file_map: 文件数量字典
    :param severity_count: 严重度统计字典（仅当 show_severity=True 时需要）
    :param show_severity: 是否显示严重度图
    """
    if show_severity:
        # 3个子图：问题数量、文件数量、严重度分布
        ax1 = figure.add_subplot(311)
        sorted_metric_count = dict(sorted(metric_count.items(), key=lambda x: x[1], reverse=True))
        draw_horizontal_bar_chart(
            ax1,
            sorted_metric_count,
            "二级指标问题数量",
            "问题数量"
        )

        ax2 = figure.add_subplot(312)
        sorted_file_map = dict(sorted(metric_file_map.items(), key=lambda x: x[1], reverse=True))
        draw_horizontal_bar_chart(
            ax2,
            sorted_file_map,
            "每个问题涉及的文件数量",
            "文件数量"
        )

        ax3 = figure.add_subplot(313)
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
            ax3,
            severity_display,
            "严重度分布",
            "问题数量",
            invert_y=False,
            colors=[color_map[k] for k in severity_list]
        )

        figure.subplots_adjust(left=0.22, right=0.9, top=0.95, bottom=0.07, hspace=0.5)

    else:
        # 2个子图：问题数量、文件数量
        ax1 = figure.add_subplot(211)
        sorted_metric_count = dict(sorted(metric_count.items(), key=lambda x: x[1], reverse=True))
        draw_horizontal_bar_chart(
            ax1,
            sorted_metric_count,
            "二级指标问题数量",
            "问题数量"
        )

        ax2 = figure.add_subplot(212)
        sorted_file_map = dict(sorted(metric_file_map.items(), key=lambda x: x[1], reverse=True))
        draw_horizontal_bar_chart(
            ax2,
            sorted_file_map,
            "每个问题涉及的文件数量",
            "文件数量"
        )

        figure.subplots_adjust(left=0.22, right=0.9, top=0.9, bottom=0.1, hspace=0.5)


# ==================================================
# 复杂度
# ==================================================
def create_complexity_tab(files):
    """
    复杂度统计报告 Tab
    :param files: 文件列表
    """
    widget = QWidget()
    main_layout = QHBoxLayout(widget)
    main_layout.setContentsMargins(0, 0, 0, 0)

    # ========== 左侧区域（可滚动图表） ==========
    left_scroll = QScrollArea()
    left_scroll.setWidgetResizable(True)
    left_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
    left_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
    left_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

    left_widget = QWidget()
    left_layout = QVBoxLayout(left_widget)
    left_layout.setContentsMargins(0, 0, 0, 0)
    left_layout.setSpacing(0)

    # 统计每个文件的复杂度值
    file_complexity_map = {}  # 文件路径 -> 最大圈复杂度
    complexity_values = []

    for f in files:
        file_path = f.get("file_path", "未知路径")
        found = False
        max_complexity = 10  # 默认值

        for s in f.get("summaries", []):
            if s.get("metric_category") != MetricCategory.COMPLEXITY:
                continue

            for issue in s.get("issues", []):
                try:
                    complexity_value = int(issue.get("rule_id", 0))
                    # 超过31的复杂度都归为31，避免极端值拉长图表
                    complexity_value = min(31, complexity_value)
                    if complexity_value > max_complexity:
                        max_complexity = complexity_value
                    found = True
                except:
                    pass

        # 低复杂度的不会返回issue所以找不到，默认为10
        if not found:
            max_complexity = 10

        complexity_values.append(max_complexity)
        file_complexity_map[file_path] = max_complexity

    # ===============================
    # 绘制图表
    # ===============================
    figure = Figure(figsize=(6, 6), dpi=100)
    canvas = ScrollableCanvas(figure)

    ax = figure.add_subplot(111)

    # 基础分箱
    bins = [0, 11, 16, 21, 26, 31, 36]

    n, bins, patches = ax.hist(
        complexity_values,
        bins=bins,
        edgecolor='black'
    )

    # 为每个柱子设置颜色（绿->黄->红）
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

    figure.subplots_adjust(left=0.15, right=0.95, top=0.9, bottom=0.1)
    canvas.setMinimumHeight(500)

    left_layout.addWidget(canvas)
    left_scroll.setWidget(left_widget)

    # ========== 右侧区域 ==========
    # 定义复杂度范围和对应的标签
    range_labels = ["0–10", "11–15", "16–20", "21–25", "26–30", "≥31"]
    range_bounds = [(0, 10), (11, 15), (16, 20), (21, 25), (26, 30), (31, 999)]

    # 构建适配 FileListPanel 的数据结构
    metric_list = range_labels
    metric_count = {}
    complexity_to_files = {}

    for i, (label, (low, high)) in enumerate(zip(range_labels, range_bounds)):
        count = 0
        file_paths = []
        for file_path, complexity in file_complexity_map.items():
            if low <= complexity <= high:
                count += 1
                file_paths.append(file_path)
        metric_count[label] = count
        complexity_to_files[label] = file_paths

    # 创建右侧面板
    right_panel = FileListPanel()
    right_panel.set_data(
        metric_list=metric_list,
        metric_to_files=complexity_to_files,
        title="点击复杂度范围查看涉及的文件"
    )

    # 左右分栏布局
    main_layout.addWidget(left_scroll, 6)
    main_layout.addWidget(right_panel, 4)

    return widget


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
