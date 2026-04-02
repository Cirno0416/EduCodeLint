from PyQt6.QtWidgets import QFrame, QGraphicsDropShadowEffect
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt, QPropertyAnimation


class HoverCard(QFrame):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 10px;
                border: 1px solid #e5e5e5;
            }
        """)

        # 开启 hover
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
        self.setMouseTracking(True)

        # 阴影
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(10)
        self.shadow.setOffset(0, 2)
        self.shadow.setColor(QColor(0, 0, 0, 60))
        self.setGraphicsEffect(self.shadow)

        # 动画
        self.anim = QPropertyAnimation(self.shadow, b"blurRadius")
        self.anim.setDuration(200)  # 动画时长（毫秒）

    def enterEvent(self, event):
        """鼠标进入"""
        self.anim.stop()
        self.anim.setStartValue(self.shadow.blurRadius())
        self.anim.setEndValue(30)
        self.anim.start()

        self.shadow.setOffset(0, 6)
        self.shadow.setColor(QColor(0, 0, 0, 120))

        super().enterEvent(event)

    def leaveEvent(self, event):
        """鼠标离开"""
        self.anim.stop()
        self.anim.setStartValue(self.shadow.blurRadius())
        self.anim.setEndValue(10)
        self.anim.start()

        self.shadow.setOffset(0, 2)
        self.shadow.setColor(QColor(0, 0, 0, 60))

        super().leaveEvent(event)
