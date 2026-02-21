from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt


class LoadingOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("loadingOverlay")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.setStyleSheet("""
                    QWidget#loadingOverlay {
                        background-color: rgba(0, 0, 0, 120);
                    }
                """)

        # 主布局，铺满父窗口
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 中间容器，控制整体宽度
        center_container = QWidget()
        center_container.setFixedWidth(320)

        center_layout = QVBoxLayout(center_container)
        center_layout.setSpacing(15)
        center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 文本
        self.label = QLabel("正在分析，请稍候...")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("""
                    color: white;
                    font-size: 18px;
                    font-weight: bold;
                    background: transparent;
                """)

        # 进度条
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # 无限滚动
        self.progress.setFixedHeight(20)
        self.progress.setTextVisible(False)

        # 让进度条撑满容器宽度
        self.progress.setMinimumWidth(300)

        center_layout.addWidget(self.label)
        center_layout.addWidget(self.progress)

        main_layout.addWidget(center_container)

        self.hide()

    def showEvent(self, event):
        """每次显示时铺满父窗口"""
        if self.parent():
            self.setGeometry(self.parent().rect())
        super().showEvent(event)

    # def resizeEvent(self, event):
    #     """窗口变化时自动适配"""
    #     if self.parent():
    #         self.setGeometry(self.parent().rect())
    #     super().resizeEvent(event)
