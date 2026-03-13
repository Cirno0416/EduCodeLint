from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton


class SelectedFileItem(QWidget):
    def __init__(self, filename, remove_callback):
        super().__init__()
        self.filename = filename
        self.remove_callback = remove_callback

        layout = QHBoxLayout()
        layout.setContentsMargins(5, 2, 5, 2)

        # 文件名标签
        self.label = QLabel(filename)
        font = QFont()
        font.setPointSize(10)
        self.label.setFont(font)
        layout.addWidget(self.label)

        # 占位，把按钮推到右侧
        layout.addStretch()

        # 删除按钮
        self.btn_remove = QPushButton("✕")
        self.btn_remove.setFixedSize(20, 20)
        self.btn_remove.clicked.connect(self.on_remove)
        layout.addWidget(self.btn_remove)

        self.setLayout(layout)

    def on_remove(self):
        # 调用外部回调
        self.remove_callback(self.filename)
