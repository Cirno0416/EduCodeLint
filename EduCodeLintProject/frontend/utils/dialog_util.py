from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel,
    QPushButton, QHBoxLayout
)
from PyQt6.QtCore import Qt


class BaseDialog(QDialog):
    def __init__(self, parent, title, text, question_type=False):
        super().__init__(parent)

        self.setWindowTitle(title)
        self.result = False  # 用于存储用户选择结果

        # 自定义窗口
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.CustomizeWindowHint |
            Qt.WindowType.WindowTitleHint |
            Qt.WindowType.WindowCloseButtonHint
        )

        self.setModal(True)
        self.setFixedSize(300, 150)

        layout = QVBoxLayout(self)

        label_font = QFont()
        label_font.setPointSize(12)

        self.label = QLabel(text)
        self.label.setFont(label_font)
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        if question_type:
            # 判断性窗口：确定 + 取消
            self.btn_ok = QPushButton("确定")
            self.btn_ok.setFixedWidth(80)
            self.btn_ok.clicked.connect(self._on_ok)

            self.btn_cancel = QPushButton("取消")
            self.btn_cancel.setFixedWidth(80)
            self.btn_cancel.clicked.connect(self._on_cancel)

            btn_layout.addWidget(self.btn_ok)
            btn_layout.addSpacing(20)
            btn_layout.addWidget(self.btn_cancel)
        else:
            # 提示性窗口：只有一个关闭按钮
            self.btn_close = QPushButton("关闭")
            self.btn_close.setFixedWidth(80)
            self.btn_close.clicked.connect(self.accept)
            btn_layout.addWidget(self.btn_close)

        btn_layout.addStretch()

        layout.addStretch()
        layout.addWidget(self.label)
        layout.addStretch()
        layout.addLayout(btn_layout)

    def _on_ok(self):
        """确定按钮点击处理"""
        self.result = True
        self.accept()

    def _on_cancel(self):
        """取消按钮点击处理"""
        self.result = False
        self.reject()

    def get_result(self):
        """获取用户选择结果"""
        return self.result


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

    @staticmethod
    def question(parent, text, title="确认"):
        """询问对话框（确定 + 取消按钮）"""
        dialog = BaseDialog(parent, title, text, question_type=True)
        dialog.exec()
        return dialog.get_result()
