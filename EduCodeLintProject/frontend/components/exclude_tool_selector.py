from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QCheckBox, QLabel


class ExcludeToolSelector(QWidget):
    def __init__(self):
        super().__init__()

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        title = QLabel("点击勾选要排除的工具：")
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)

        self.tools = {
            "flake8": QCheckBox("flake8"),
            "pylint": QCheckBox("pylint"),
            "radon": QCheckBox("radon"),
            "bandit": QCheckBox("bandit"),
            "pyright": QCheckBox("pyright"),
            "pydocstyle": QCheckBox("pydocstyle"),
        }

        tooltips = {
            "flake8": "用于检测代码风格问题",
            "pylint": "用于检测代码异味问题",
            "radon": "用于计算代码圈复杂度",
            "bandit": "用于检测代码安全漏洞",
            "pyright": "用于检测代码潜在错误",
            "pydocstyle": "用于检测代码注释规范",
        }

        for name, cb in self.tools.items():
            cb.setToolTip(tooltips.get(name, ""))
            layout.addWidget(cb)

        layout.addStretch()
        self.setLayout(layout)

    def get_selected(self):
        return [name for name, cb in self.tools.items() if cb.isChecked()]
