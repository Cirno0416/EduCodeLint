import os
import sys


def resource_path(relative_path):
    """获取配置文件的绝对路径（兼容打包）"""
    if hasattr(sys, '_MEIPASS'):
        # 打包后，配置文件在临时目录
        base_path = sys._MEIPASS
    else:
        # 开发模式：使用 backend 目录的上级目录作为基准
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    return os.path.join(base_path, relative_path)


class ConfigPath:
    BASE_DIR = os.path.dirname(__file__)

    _PYLINT_CONFIG_PATH = '../config/.pylintrc'
    _BANDIT_CONFIG_PATH = '../config/bandit.yml'
    _FLAKE8_CONFIG_PATH = '../config/.flake8'
    # pyright 只能识别指定目录下的 pyrightconfig.json 配置文件，不能直接指定文件路径
    _PYRIGHT_CONFIG_PATH = '../config'
    _PYDOCSTYLE_CONFIG_PATH = '../config/.pydocstyle'

    PYLINT_CONFIG = os.path.abspath(os.path.join(BASE_DIR, _PYLINT_CONFIG_PATH))
    BANDIT_CONFIG = os.path.abspath(os.path.join(BASE_DIR, _BANDIT_CONFIG_PATH))
    FLAKE8_CONFIG = os.path.abspath(os.path.join(BASE_DIR, _FLAKE8_CONFIG_PATH))
    PYRIGHT_CONFIG = os.path.abspath(os.path.join(BASE_DIR, _PYRIGHT_CONFIG_PATH))
    PYDOCSTYLE_CONFIG = os.path.abspath(os.path.join(BASE_DIR, _PYDOCSTYLE_CONFIG_PATH))
