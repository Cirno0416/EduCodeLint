from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton


class Sidebar(QWidget):
    def __init__(self):
        super().__init__()

        self.setFixedWidth(220)

        self.btn_home = QPushButton("EduCodeLint")
        self.btn_home.setObjectName("navTitle")

        self.btn_analysis = QPushButton("代码分析")
        self.btn_compare = QPushButton("批次对比")
        self.btn_record = QPushButton("历史记录")
        self.btn_theory = QPushButton("指标与权重说明")

        # 设置鼠标悬停时的手型
        self.btn_home.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_analysis.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_compare.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_record.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_theory.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout()
        layout.addWidget(self.btn_home)
        layout.addSpacing(30)
        layout.addWidget(self.btn_analysis)
        layout.addSpacing(10)
        layout.addWidget(self.btn_compare)
        layout.addSpacing(10)
        layout.addWidget(self.btn_record)
        layout.addStretch()
        layout.addWidget(self.btn_theory)
        layout.addSpacing(10)

        self.setStyleSheet("""
            QPushButton {
                color: #ecf0f1;
                background-color: #2c3e50;
                font-size: 18px;
                font-weight: bold;
                border: none;
                text-align: center;
                padding: 10px 15px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
            
            QPushButton#navTitle {
                color: #2c3e50;
                font-size: 26px;
                font-weight: bold;
                background: transparent;
            }
            QPushButton#navTitle:hover {
                color: #34495e;
            }
        """)

        self.setLayout(layout)

    def set_active(self, btn):
        """设置当前激活的按钮样式"""
        btn_list = [self.btn_analysis, self.btn_compare, self.btn_record, self.btn_theory]
        for b in btn_list:
            b.setStyleSheet("""
                QPushButton {
                    color: #ecf0f1;
                    padding: 10px 15px;
                    border-radius: 6px;
                }
            """)

        # home 按钮特殊处理
        if btn in btn_list:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #4A90E2;
                    color: white;
                    padding: 10px 15px;
                    border-radius: 6px;
                }
            """)
