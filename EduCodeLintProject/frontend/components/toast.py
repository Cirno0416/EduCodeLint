from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation
from PyQt6.QtWidgets import QGraphicsOpacityEffect


class Toast(QLabel):
    def __init__(self, parent, message, duration=2000):
        super().__init__(parent)

        self.duration = duration

        self.setText(message)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 样式
        self.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 0, 0, 200);
                color: white;
                padding: 15px 30px;
                border-radius: 10px;
                font-size: 15px;
                font-weight: bold;
            }
        """)

        self.adjustSize()

        # ===== 设置透明效果 =====
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0)

        # ===== 居中显示 =====
        self.center_in_parent()

        self.show()

        # ===== 淡入动画 =====
        self.fade_in()

    # ==========================
    # 居中
    # ==========================
    def center_in_parent(self):
        if not self.parent():
            return

        parent_rect = self.parent().rect()

        x = (parent_rect.width() - self.width()) // 2
        y = (parent_rect.height() - self.height()) // 2

        self.move(x, y)

    # ==========================
    # 淡入
    # ==========================
    def fade_in(self):
        self.anim_in = QPropertyAnimation(
            self.opacity_effect, b"opacity"
        )
        self.anim_in.setDuration(300)
        self.anim_in.setStartValue(0)
        self.anim_in.setEndValue(1)
        self.anim_in.finished.connect(self.start_fade_out_timer)
        self.anim_in.start()

    # ==========================
    # 等待后淡出
    # ==========================
    def start_fade_out_timer(self):
        QTimer.singleShot(self.duration, self.fade_out)

    def fade_out(self):
        self.anim_out = QPropertyAnimation(
            self.opacity_effect, b"opacity"
        )
        self.anim_out.setDuration(400)
        self.anim_out.setStartValue(1)
        self.anim_out.setEndValue(0)
        self.anim_out.finished.connect(self.close)
        self.anim_out.start()

    # ==========================
    # 父窗口大小改变时重新居中
    # ==========================
    def resizeEvent(self, event):
        self.center_in_parent()
        super().resizeEvent(event)
