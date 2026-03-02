from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout,
    QLabel, QTabWidget,
    QTableWidget, QTableWidgetItem,
    QHeaderView, QHBoxLayout, QWidget
)
from PyQt6.QtGui import QFont, QColor

from backend.constant.severity_level import SeverityLevel


class ReportWindow(QDialog):
    def __init__(self, file_data):
        super().__init__()

        self.setWindowTitle(f"分析报告 - {file_data.get('file_name', '')}")
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
        file_label = QLabel(file_data['file_name'])
        file_font = QFont()
        file_font.setPointSize(16)
        file_font.setBold(True)
        file_label.setFont(file_font)

        # 数据区域
        info_layout = QHBoxLayout()

        score_label = QLabel("总分")
        score_value = QLabel(str(file_data['score']))
        score_value.setFont(QFont("", 16, QFont.Weight.Bold))

        issue_label = QLabel("问题数")
        issue_value = QLabel(str(total_issues))
        issue_value.setFont(QFont("", 16, QFont.Weight.Bold))

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

        if not category_map:
            empty_label = QLabel("无问题数据")
            layout.addWidget(empty_label)
            return

        for category, issue_list in category_map.items():
            self.add_category_tab(category, issue_list)

    # ==================================================
    # 每个类别一个Tab
    # ==================================================
    def add_category_tab(self, category, issues):
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(
            ["行号", "严重程度", "问题描述"]
        )

        header = table.horizontalHeader()

        # 行号：固定宽度
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        table.setColumnWidth(0, 80)

        # 严重程度：固定宽度
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        table.setColumnWidth(1, 110)

        # 问题描述：自动填满剩余空间
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

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

            # 问题描述
            desc_item = QTableWidgetItem(issue.get("message", ""))
            desc_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            table.setItem(row, 2, desc_item)

        self.tabs.addTab(table, category)


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
