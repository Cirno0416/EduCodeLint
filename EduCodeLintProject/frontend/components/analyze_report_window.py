import hashlib

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout,
    QLabel, QTabWidget,
    QTableWidget, QTableWidgetItem,
    QHeaderView, QHBoxLayout, QWidget, QPlainTextEdit
)
from PyQt6.QtGui import QFont, QColor, QTextCursor, QTextCharFormat

from backend.constant.severity_level import SeverityLevel
from backend.constant.metric_category import MetricCategory


class AnalyzeReportWindow(QDialog):
    def __init__(self, file_data):
        super().__init__()

        self.file_path = file_data.get('file_path', '')
        self.original_hash = file_data.get("file_hash", '')
        self.setWindowTitle(f"分析报告 - {self.file_path}")
        self.resize(900, 600)

        layout = QVBoxLayout(self)

        # =============================
        # 顶部统计信息
        # =============================
        summaries = file_data.get("summaries", [])

        total_issues = sum(
            s.get("issue_count", 0)
            for s in summaries
        )

        # =============================
        # 顶部卡片区域
        # =============================
        header_card = QWidget()
        header_layout = QVBoxLayout(header_card)
        header_layout.setContentsMargins(20, 15, 20, 15)

        header_card.setStyleSheet("""
            QWidget {
                background-color: #f5f7fa;
                border-radius: 8px;
            }
        """)

        # 文件名
        file_label = QLabel(file_data['file_path'])
        file_font = QFont()
        file_font.setPointSize(16)
        file_font.setBold(True)
        file_label.setFont(file_font)

        # 数据区域
        info_layout = QHBoxLayout()

        score_label = QLabel("总分")
        score_value = QLabel(f"{file_data['score']:.2f}")
        score_value.setFont(file_font)

        issue_label = QLabel("问题数")
        issue_value = QLabel(str(total_issues))
        issue_value.setFont(file_font)

        info_layout.addStretch()
        info_layout.addWidget(score_label)
        info_layout.addSpacing(10)
        info_layout.addWidget(score_value)
        info_layout.addSpacing(40)
        info_layout.addWidget(issue_label)
        info_layout.addSpacing(10)
        info_layout.addWidget(issue_value)
        info_layout.addStretch()

        header_layout.addWidget(file_label)
        header_layout.addSpacing(10)
        header_layout.addLayout(info_layout)

        layout.addWidget(header_card)

        # =============================
        # 分类 Tabs
        # =============================
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # 从 summaries 里提取 issues
        category_map = _collect_issues_by_category(summaries)

        all_categories = [
            MetricCategory.CODE_STYLE,
            MetricCategory.CODE_SMELL,
            MetricCategory.COMPLEXITY,
            MetricCategory.SECURITY_VULNERABILITY,
            MetricCategory.POTENTIAL_ERROR,
            MetricCategory.DOCSTRING
        ]

        for category in all_categories:
            issues = category_map.get(category, [])
            self.add_category_tab(category, issues, len(issues) == 0)

        # =============================
        # 全局代码查看区域
        # =============================
        self.code_viewer = QPlainTextEdit()
        self.code_viewer.setReadOnly(True)
        self.code_viewer.setFont(QFont("Consolas", 14))
        self.code_viewer.setPlaceholderText("点击上方问题查看代码上下文...")
        self.code_viewer.setMinimumHeight(220)
        self.code_viewer.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.code_viewer.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        layout.addWidget(self.code_viewer)

    # ==================================================
    # 每个类别一个Tab
    # ==================================================
    def add_category_tab(self, category, issues, is_empty=False):
        if is_empty:
            # 创建容器widget
            container = QWidget()
            container_layout = QVBoxLayout(container)

            # 添加提示标签
            empty_label = QLabel("未检测到此类问题")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_label.setStyleSheet("""
                QLabel {
                    color: #666;
                    font-size: 18px;
                    padding: 50px;
                }
            """)

            container_layout.addWidget(empty_label)
            container_layout.addStretch()

            self.tabs.addTab(container, category)
            return

        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(
            ["行号", "严重程度", "检测工具", "问题描述"]
        )

        header = table.horizontalHeader()

        # 行号：固定宽度
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        table.setColumnWidth(0, 60)

        # 严重程度：固定宽度
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        table.setColumnWidth(1, 100)

        # 检测工具
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        table.setColumnWidth(2, 100)

        # 问题描述：自动填满剩余空间
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)

        # 禁止编辑
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # 启用自动换行
        table.setWordWrap(True)

        # 行高自动调整
        table.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )

        table.setRowCount(len(issues))

        for row, issue in enumerate(issues):
            # 行号
            line_item = QTableWidgetItem(str(issue.get("line", "")))
            line_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(row, 0, line_item)

            # 严重程度
            severity = issue.get("severity", "")
            severity_item = QTableWidgetItem(severity)
            severity_item.setForeground(getSeverityColor(severity))
            severity_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(row, 1, severity_item)

            # 检测工具
            tool_item = QTableWidgetItem(issue.get("tool", ""))
            tool_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(row, 2, tool_item)

            # 问题描述
            desc_item = QTableWidgetItem(issue.get("message", ""))
            desc_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            table.setItem(row, 3, desc_item)

        table.cellClicked.connect(
            lambda row, col: self.show_code_context(issues[row])
        )
        self.tabs.addTab(table, category)

    def show_code_context(self, issue):
        line_no = issue.get("line")
        category = issue.get("metric_category")

        if not line_no:
            self.code_viewer.setPlainText("无法定位行号")
            return

        try:
            current_hash = calculate_file_hash(self.file_path)
            with open(self.file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except Exception:
            self.code_viewer.setPlainText("文件读取失败")
            return

        if self.original_hash and current_hash != self.original_hash:
            self.code_viewer.setPlainText(
                "⚠文件已被修改，当前定位可能不准确，请重新分析"
            )
            return

        # =============================
        # 复杂度tab显示整个函数
        # =============================
        if category == MetricCategory.COMPLEXITY:
            start, end = find_function_block(lines, line_no)

            if start is None:
                # fallback
                start = max(0, line_no - 3 - 1)
                end = min(len(lines), line_no + 3)
        else:
            # 普通问题
            start = max(0, line_no - 3 - 1)
            end = min(len(lines), line_no + 3)

        # =============================
        # 构建显示内容
        # =============================
        text_lines = []
        for i in range(start, end):
            line_text = lines[i].rstrip("\n")
            prefix = f"{i + 1:>4} | "
            text_lines.append(prefix + line_text)

        self.code_viewer.setPlainText("\n".join(text_lines))

        # =============================
        # 高亮问题行
        # =============================
        cursor = self.code_viewer.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)

        target_line = line_no - start - 1

        for _ in range(target_line):
            cursor.movePosition(QTextCursor.MoveOperation.Down)

        cursor.select(QTextCursor.SelectionType.LineUnderCursor)

        fmt = QTextCharFormat()
        fmt.setBackground(QColor("#ffe6e6"))

        cursor.setCharFormat(fmt)


def _collect_issues_by_category(summaries):
    category_map = {}

    for s in summaries:
        category = s.get("metric_category")
        issues = s.get("issues", [])

        if not category or not issues:
            continue

        category_map.setdefault(category, []).extend(issues)

    return category_map


def getSeverityColor(severity):
    color = Qt.GlobalColor.black  # 默认颜色

    if severity == SeverityLevel.HIGH:
        color = Qt.GlobalColor.red
    elif severity == SeverityLevel.MEDIUM:
        color = QColor("#FFA500")
    elif severity == SeverityLevel.LOW:
        color = Qt.GlobalColor.blue

    return color


def find_function_block(lines, line_no):
    """
    根据行号找到函数的开始和结束行
    """
    index = line_no - 1

    # =============================
    # 向上找 def
    # =============================
    start = index
    while start >= 0:
        line = lines[start].lstrip()

        if line.startswith("def ") or line.startswith("async def "):
            break

        start -= 1

    # 没找到函数定义
    if start < 0:
        return None, None

    # =============================
    # 获取函数缩进
    # =============================
    def_line = lines[start]
    base_indent = len(def_line) - len(def_line.lstrip())

    # =============================
    # 向下找函数结束
    # =============================
    end = start + 1
    while end < len(lines):
        line = lines[end]

        # 跳过空行
        if line.strip() == "":
            end += 1
            continue

        current_indent = len(line) - len(line.lstrip())

        # 缩进 <= 函数定义 → 结束
        if current_indent <= base_indent:
            break

        end += 1

    return start, end


def calculate_file_hash(file_path):
    with open(file_path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()
