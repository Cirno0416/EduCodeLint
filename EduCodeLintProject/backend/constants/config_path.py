import os


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
