from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel,
    QPushButton, QHBoxLayout
)
from PyQt6.QtCore import Qt


class BaseDialog(QDialog):
    def __init__(self, parent, title, text):
        super().__init__(parent)

        self.setWindowTitle(title)

        # 自定义窗口
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.CustomizeWindowHint |
            Qt.WindowType.WindowTitleHint |
            Qt.WindowType.WindowCloseButtonHint
        )

        self.setModal(True)
        self.setFixedSize(200, 120)

        layout = QVBoxLayout(self)

        self.label = QLabel(text)
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_close = QPushButton("关闭")
        self.btn_close.setFixedWidth(80)
        self.btn_close.clicked.connect(self.accept)

        btn_layout.addWidget(self.btn_close)
        btn_layout.addStretch()

        layout.addStretch()
        layout.addWidget(self.label)
        layout.addStretch()
        layout.addLayout(btn_layout)


class DialogUtil:

    @staticmethod
    def warning(parent, text, title="提示"):
        dialog = BaseDialog(parent, title, text)
        dialog.exec()

    @staticmethod
    def error(parent, text, title="错误"):
        dialog = BaseDialog(parent, title, text)
        dialog.exec()

    @staticmethod
    def info(parent, text, title="信息"):
        dialog = BaseDialog(parent, title, text)
        dialog.exec()
