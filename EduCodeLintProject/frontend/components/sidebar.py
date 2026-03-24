from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton


class Sidebar(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedWidth(180)

        layout = QVBoxLayout()

        btn_font = QFont()
        btn_font.setPointSize(12)
        btn_font.setBold(True)

        self.btn_analysis = QPushButton("代码分析")
        self.btn_compare = QPushButton("批次对比")
        self.btn_record = QPushButton("历史记录")
        self.btn_home = QPushButton("返回主页")

        self.btn_analysis.setFont(btn_font)
        self.btn_compare.setFont(btn_font)
        self.btn_record.setFont(btn_font)
        self.btn_home.setFont(btn_font)

        layout.addWidget(self.btn_analysis)
        layout.addSpacing(10)
        layout.addWidget(self.btn_compare)
        layout.addSpacing(10)
        layout.addWidget(self.btn_record)
        layout.addSpacing(10)
        layout.addWidget(self.btn_home)
        layout.addStretch()

        self.setLayout(layout)
