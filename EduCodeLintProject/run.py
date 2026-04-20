import logging
import sys
import threading
import time
import os
from logging.handlers import TimedRotatingFileHandler

import requests
from PyQt6.QtWidgets import QApplication

from backend.app import create_app
from frontend.core.app import MainWindow
from frontend.utils.env_checker import check_environment

# 获取项目根目录
root_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, root_dir)
sys.path.insert(0, os.path.join(root_dir, 'backend'))


def setup_logging():
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    log_dir = os.path.join(base_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, "app.log")

    handler = TimedRotatingFileHandler(
        log_file,
        when="midnight",
        interval=1,
        backupCount=7,
        encoding="utf-8"
    )

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] [%(threadName)s] "
        "%(filename)s:%(lineno)d - %(message)s"
    )
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)


setup_logging()


def wait_for_flask(url="http://127.0.0.1:5000", timeout=5):
    """等待 Flask 服务启动"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            requests.get(url, timeout=0.5)
            print("Flask 服务已就绪")
            return True
        except:
            time.sleep(0.1)
    return False


def start_flask():
    """启动Flask后端"""
    app = create_app()
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)


def start_pyqt():
    """启动PyQt前端"""
    qt_app = QApplication(sys.argv)

    style_path = "frontend/resources/styles.qss"
    if os.path.exists(style_path):
        with open(style_path, "r", encoding="utf-8") as f:
            qt_app.setStyleSheet(f.read())

    window = MainWindow()
    window.show()
    sys.exit(qt_app.exec())


if __name__ == "__main__":
    # 1. 环境检测
    if not check_environment():
        sys.exit(1)

    # 2. 启动Flask线程
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()

    # 3. 等Flask启动
    wait_for_flask(timeout=10)

    # 4. 启动PyQt界面
    start_pyqt()
