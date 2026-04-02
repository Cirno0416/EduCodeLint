from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea, QGridLayout, QGroupBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame
)
from PyQt6.QtGui import QFont


class TheoryPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: #f5f7fa; border: none; }")

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(24)
        container_layout.setContentsMargins(40, 40, 40, 40)

        # 标题
        title = QLabel("代码质量指标体系与评分规则")
        title_font = QFont()
        title_font.setPointSize(22)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #1e2a3a; margin-bottom: 15px;")
        container_layout.addWidget(title)

        # 副标题
        subtitle = QLabel("面向教育场景的 Python 代码质量自动化分析工具")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #4a627a; font-size: 15px; margin-bottom: 25px;")
        container_layout.addWidget(subtitle)

        # ========== 指标选取说明 ==========
        indicator_box = self._create_card("核心代码质量指标")
        indicator_grid = QGridLayout()
        indicators = [
            ("代码规范性", "PEP8 风格：命名、缩进、行长度、空行等"),
            ("代码异味", "过长函数、大类、参数过多、深层嵌套、过多分支"),
            ("复杂度", "圈复杂度（阈值 ≤10，超出即扣分）"),
            ("潜在错误", "未定义变量、赋值前使用、不一致返回等"),
            ("安全漏洞", "危险函数调用、硬编码敏感信息、异常忽略"),
            ("注释", "模块级 Docstring 完整性与规范性（约束项）")
        ]
        for i, (name, desc) in enumerate(indicators):
            title_lbl = QLabel(name)
            title_lbl.setStyleSheet("font-weight: bold; font-size: 16px; color: #0f3b5c;")
            desc_lbl = QLabel(desc)
            desc_lbl.setStyleSheet("color: #2c3e50; font-size: 14px;")
            desc_lbl.setWordWrap(True)
            indicator_grid.addWidget(title_lbl, i, 0)
            indicator_grid.addWidget(desc_lbl, i, 1)
        indicator_grid.setColumnStretch(1, 1)
        indicator_box.layout().addLayout(indicator_grid)
        container_layout.addWidget(indicator_box)

        # ========== 评分规则简述 ==========
        rule_box = self._create_card("各维度评分规则")
        rule_text = QLabel(
            "• 代码规范性 / 代码异味 / 潜在错误 / 安全漏洞：基于问题数量及其严重度扣分<br>"
            "• 复杂度：圈复杂度 ≤ 10 得满分，超出后按超出程度扣分<br>"
            "• 注释：作为约束项，根据 Docstring 规范性确定修正系数<br>"
            "• 最终得分 = 注释修正系数 × 五维度加权基础分"
        )
        rule_text.setWordWrap(True)
        rule_text.setStyleSheet("color: #2c3e50; font-size: 14px; line-height: 1.6;")
        rule_text.setTextFormat(Qt.TextFormat.RichText)
        rule_box.layout().addWidget(rule_text)
        container_layout.addWidget(rule_box)

        # ========== 权重预设表 ==========
        weight_box = self._create_card("五类可量化指标权重预设")
        weight_table = QTableWidget()
        weight_table.setRowCount(5)
        weight_table.setColumnCount(2)
        weight_table.setHorizontalHeaderLabels(["指标", "默认权重"])
        weight_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        weight_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        weight_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)  # 禁止表格获得焦点
        weight_table.setStyleSheet(self._table_style())

        weight_data = [
            ("潜在错误", "0.30"),
            ("复杂度", "0.20"),
            ("代码异味", "0.20"),
            ("代码规范性", "0.15"),
            ("安全漏洞", "0.15")
        ]
        for row, (indicator, w) in enumerate(weight_data):
            weight_table.setItem(row, 0, QTableWidgetItem(indicator))
            weight_table.setItem(row, 1, QTableWidgetItem(w))
        weight_table.setFixedHeight(197)
        weight_box.layout().addWidget(weight_table)
        container_layout.addWidget(weight_box)

        # ========== 权重自适应机制说明 ==========
        adaptive_box = self._create_card("权重自适应机制")
        adaptive_text = QLabel(
            "系统根据学生代码的历史表现动态调整权重，使评分更贴合当前教学阶段的重点问题。<br><br>"
            "<b>自适应原理：</b><br>"
            "• 统计每类指标在最近作业中的加权错误强度变化量 ΔE<br>"
            "• 权重更新公式：w_new = w_old + η × ΔE（学习率η = 0.01）<br>"
            "• 错误强度 E = (1/N) × Σ(惩罚系数 × 问题数量)<br>"
            "• 当某类指标错误率显著上升时，其权重自动提高，反之降低<br><br>"
            "<b>设计目的：</b><br>"
            "避免权重长期固定，使评分能够反映学生在不同学习阶段的实际薄弱环节，"
            "提升评价与教学干预的适应性。"
        )
        adaptive_text.setWordWrap(True)
        adaptive_text.setStyleSheet("color: #2c3e50; font-size: 14px; line-height: 1.6;")
        adaptive_text.setTextFormat(Qt.TextFormat.RichText)
        adaptive_box.layout().addWidget(adaptive_text)
        container_layout.addWidget(adaptive_box)

        # ========== 惩罚系数与严重度表 ==========
        penalty_box = self._create_card("二级指标严重度与惩罚系数")
        penalty_table = QTableWidget()
        penalty_table.setColumnCount(4)
        penalty_table.setHorizontalHeaderLabels(["一级指标", "二级指标", "严重度", "惩罚系数"])
        penalty_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        penalty_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        penalty_table.setStyleSheet(self._table_style())

        # 详细数据：每个二级指标单独一行
        penalty_details = [
            ("潜在错误", "未定义名称引用", "高", "5.0"),
            ("潜在错误", "变量赋值前使用", "高", "5.0"),
            ("潜在错误", "不一致返回", "高", "5.0"),
            ("潜在错误", "未使用的赋值", "中", "3.0"),
            ("复杂度", "圈复杂度", "高", "5.0"),
            ("代码异味", "过长函数/方法", "高", "5.0"),
            ("代码异味", "过多分支", "高", "5.0"),
            ("代码异味", "深层嵌套", "中", "3.0"),
            ("代码异味", "参数过多", "中", "3.0"),
            ("代码异味", "大类", "中", "3.0"),
            ("安全漏洞", "危险函数调用", "高", "5.0"),
            ("安全漏洞", "硬编码敏感信息", "高", "5.0"),
            ("安全漏洞", "异常忽略", "中", "3.0"),
            ("代码规范性", "变量和函数命名风格", "中", "3.0"),
            ("代码规范性", "类命名风格", "中", "3.0"),
            ("代码规范性", "行长度限制", "低", "1.0"),
            ("代码规范性", "括号和空白使用", "低", "1.0"),
            ("代码规范性", "空行使用", "低", "1.0")
        ]

        penalty_table.setRowCount(len(penalty_details))
        for row, (cat, sub, severity, penalty) in enumerate(penalty_details):
            penalty_table.setItem(row, 0, QTableWidgetItem(cat))
            penalty_table.setItem(row, 1, QTableWidgetItem(sub))
            penalty_table.setItem(row, 2, QTableWidgetItem(severity))
            penalty_table.setItem(row, 3, QTableWidgetItem(penalty))

        penalty_table.setFixedHeight(587)
        penalty_box.layout().addWidget(penalty_table)
        container_layout.addWidget(penalty_box)

        # ========== 注释修正系数表 ==========
        comment_box = self._create_card("注释约束项修正系数")
        comment_table = QTableWidget()
        comment_table.setRowCount(3)
        comment_table.setColumnCount(2)
        comment_table.setHorizontalHeaderLabels(["Docstring 情况", "修正系数 r"])
        comment_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        comment_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        comment_table.setStyleSheet(self._table_style())

        comment_data = [
            ("有模块 Docstring 且符合 PEP257 格式", "1.0"),
            ("有模块 Docstring 但格式不规范", "0.95"),
            ("无模块 Docstring", "0.9")
        ]
        for row, (desc, coef) in enumerate(comment_data):
            comment_table.setItem(row, 0, QTableWidgetItem(desc))
            comment_table.setItem(row, 1, QTableWidgetItem(coef))
        comment_table.setFixedHeight(137)
        comment_box.layout().addWidget(comment_table)
        container_layout.addWidget(comment_box)

        scroll.setWidget(container)
        main_layout.addWidget(scroll)

    def _create_card(self, title_text):
        card = QGroupBox()
        card.setTitle(title_text)
        card.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 16px;
                color: #1e466e;
                background-color: #ffffff;
                border: 1px solid #dce5f0;
                border-radius: 12px;
                margin-top: 12px;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                background-color: #ffffff;
            }
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        return card

    def _table_style(self):
        return """
            QTableWidget {
                color: #2c3e50;
                background-color: #ffffff;
                alternate-background-color: #f9fafc;
                gridline-color: #e2e8f0;
                font-size: 14px;
                outline: none;          /* 移除整体焦点框 */
            }
            QTableWidget::item {
                padding: 8px;
                border: none;                 /* 移除每个格子前的蓝线 */
            }
            QTableWidget::item:hover {
                background-color: transparent;
                color: #2c3e50;
            }
            QTableWidget::item:selected {
                background-color: transparent;   /* 选中时背景透明 */
                color: #2c3e50;                 /* 文字颜色不变 */
            }
            QTableWidget::item:focus {
                outline: none;          /* 移除单元格焦点虚线框 */
                border: none;
            }
            QHeaderView::section {
                background-color: #eef2f7;
                padding: 8px;
                font-weight: bold;
                font-size: 14px;
                border: none;
                border-bottom: 1px solid #cbd5e1;
            }
        """
