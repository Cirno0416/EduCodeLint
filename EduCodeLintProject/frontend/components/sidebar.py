from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton


class Sidebar(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedWidth(180)

        layout = QVBoxLayout()

        self.btn_analysis = QPushButton("代码分析")
        self.btn_compare = QPushButton("批次对比")
        self.btn_history = QPushButton("历史记录")

        layout.addWidget(self.btn_analysis)
        layout.addWidget(self.btn_compare)
        layout.addWidget(self.btn_history)
        layout.addStretch()

        self.setLayout(layout)
