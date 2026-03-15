from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout,
    QPushButton, QLabel,
    QSpinBox, QComboBox
)


class Pagination(QWidget):

    # 信号
    page_changed = pyqtSignal(int)
    page_size_changed = pyqtSignal(int)

    def __init__(self, page=1, page_size=10):
        super().__init__()

        self.page = page
        self.page_size = page_size
        self.total_pages = 1
        self.total_records = 0

        layout = QHBoxLayout()

        # 上一页
        self.prev_btn = QPushButton("上一页")
        self.prev_btn.clicked.connect(self.prev_page)

        # 页码
        self.page_label = QLabel()
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 下一页
        self.next_btn = QPushButton("下一页")
        self.next_btn.clicked.connect(self.next_page)

        # 跳转
        self.jump_label = QLabel("跳转到:")
        self.jump_spinbox = QSpinBox()
        self.jump_spinbox.setFixedWidth(60)
        self.jump_spinbox.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)

        self.jump_btn = QPushButton("Go")
        self.jump_btn.clicked.connect(self.jump_page)

        # 每页数量
        self.page_size_label = QLabel("每页显示:")
        self.page_size_combo = QComboBox()
        self.page_size_combo.addItems(["10", "20", "50"])
        self.page_size_combo.setCurrentText(str(self.page_size))
        self.page_size_combo.currentTextChanged.connect(self.on_page_size_change)

        # 总数
        self.total_label = QLabel()

        layout.addWidget(self.prev_btn)
        layout.addWidget(self.page_label)
        layout.addWidget(self.next_btn)

        layout.addStretch()

        layout.addWidget(self.jump_label)
        layout.addWidget(self.jump_spinbox)
        layout.addWidget(self.jump_btn)

        layout.addStretch()

        layout.addWidget(self.page_size_label)
        layout.addWidget(self.page_size_combo)
        layout.addWidget(self.total_label)

        self.setLayout(layout)

        self.update_ui()

    # =============================
    # 更新分页信息
    # =============================
    def update_pagination(self, page, total_pages, total_records):
        self.page = page
        self.total_pages = total_pages
        self.total_records = total_records

        self.update_ui()

    def update_ui(self):
        self.page_label.setText(f"第 {self.page} 页 / 共 {self.total_pages} 页")
        self.total_label.setText(f"共 {self.total_records} 条记录")

        self.jump_spinbox.setRange(1, self.total_pages)
        self.jump_spinbox.setValue(self.page)

        self.prev_btn.setEnabled(self.page > 1)
        self.next_btn.setEnabled(self.page < self.total_pages)

    # =============================
    # 按钮事件
    # =============================
    def prev_page(self):
        if self.page > 1:
            self.page -= 1
            self.page_changed.emit(self.page)

    def next_page(self):
        if self.page < self.total_pages:
            self.page += 1
            self.page_changed.emit(self.page)

    def jump_page(self):
        page = self.jump_spinbox.value()
        if page != self.page:
            self.page = page
            self.page_changed.emit(self.page)

    def on_page_size_change(self, text):
        self.page_size = int(text)
        self.page_size_changed.emit(self.page_size)
