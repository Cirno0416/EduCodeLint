from PyQt6.QtWidgets import QWidget, QHBoxLayout, QCheckBox


class ToolSelector(QWidget):
    def __init__(self):
        super().__init__()

        layout = QHBoxLayout()

        self.tools = {
            "flake8": QCheckBox("flake8"),
            "pylint": QCheckBox("pylint"),
            "radon": QCheckBox("radon"),
            "bandit": QCheckBox("bandit"),
            "pyright": QCheckBox("pyright"),
            "pydocstyle": QCheckBox("pydocstyle"),
        }

        for cb in self.tools.values():
            layout.addWidget(cb)

        self.setLayout(layout)

    def get_selected(self):
        return [name for name, cb in self.tools.items() if cb.isChecked()]
