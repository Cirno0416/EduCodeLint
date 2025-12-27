import json
import os
import re
import subprocess


PYLINT_CONFIG_PATH = '../config/.pylintrc_stu'
BANDIT_CONFIG_PATH = '../config/bandit_stu.yml'
FLAKE8_CONFIG_PATH = '../config/.flake8_stu'
PYRIGHT_CONFIG_PATH = '../config/pyrightconfig_stu.json'
PYDOCSTYLE_CONFIG_PATH = '../config/.pydocstyle_stu'

ANSI_ESCAPE_RE = re.compile(r'\x1b\[[0-9;]*m')


def run_linters(file_path: str, exclude_tools: list = None) -> dict:
    exclude_tools = exclude_tools or []
    tool_mapping = {
        "pylint": run_pylint,
        "flake8": run_flake8,
        "bandit": run_bandit,
        "radon": run_radon,
        "pyright": run_pyright,
        "pydocstyle": run_pydocstyle,
    }
    results = {}

    for tool_name, tool_func in tool_mapping.items():
        if tool_name in exclude_tools:
            results[tool_name] = []
            continue

        try:
            result = tool_func(file_path)
            results[tool_name] = result
        except Exception as e:
            # 单个工具执行失败不影响其他工具
            results[tool_name] = {"error": str(e)}

    return results


def run_pylint(file_path: str) -> list:
    pylint_config = os.path.abspath(
        os.path.join(os.path.dirname(__file__), PYLINT_CONFIG_PATH)
    )

    if not os.path.exists(pylint_config):
        print(f"Pylint 配置文件不存在: {pylint_config}")
        return []

    cmd = [
        'pylint',
        file_path,
        f'--rcfile={pylint_config}',
        '--output-format=json',
        '--score=no'
    ]

    process = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if process.stderr:
        print(f"Pylint 错误输出: {process.stderr}")
        return []

    if not process.stdout.strip():
        print("Pylint 无输出")
        return []

    try:
        return json.loads(process.stdout)
    except json.JSONDecodeError as e:
        print(f"Pylint JSON解析失败: {e}")
        return []


def run_flake8(file_path: str) -> list:
    flake8_config = os.path.abspath(
        os.path.join(os.path.dirname(__file__), FLAKE8_CONFIG_PATH)
    )

    if not os.path.exists(flake8_config):
        print(f"Flake8 配置文件不存在: {flake8_config}")
        return []

    cmd = [
        'flake8',
        file_path,
        f'--config={flake8_config}',
        '--format=json',
        '--exit-zero'
    ]

    process = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if process.stderr:
        print(f"Flake8 错误输出: {process.stderr}")

    if not process.stdout.strip():
        print("Flake8 无输出")
        return []

    try:
        return json.loads(process.stdout)
    except json.JSONDecodeError as e:
        print(f"Flake8 JSON解析失败: {e}")
        return []


def run_bandit(file_path: str) -> list:
    bandit_config = os.path.abspath(os.path.join(
        os.path.dirname(__file__), BANDIT_CONFIG_PATH)
    )

    if not os.path.exists(bandit_config):
        print(f"Bandit 配置文件不存在: {bandit_config}")
        return []

    cmd = [
        'bandit',
        file_path,
        '-c', bandit_config,
        '-f', 'json',
        '-o', '-',
        '--quiet'
    ]

    process = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if process.stderr:
        print(f"Bandit 错误输出: {process.stderr}")

    if not process.stdout.strip():
        print("Bandit 无输出")
        print(f"Bandit stdout 原始内容: {repr(process.stdout)}")
        return []

    try:
        # Bandit JSON 输出包含 results 字段，提取核心结果
        result = json.loads(process.stdout)
        return result.get('results', [])
    except json.JSONDecodeError as e:
        print(f"Bandit JSON解析失败: {e}")
        print(f"Bandit 原始输出: {process.stdout}")
        return []


def run_radon(file_path: str) -> list:
    cmd = [
        'radon',
        'cc',  # 分析圈复杂度
        file_path,
        '-j',  # 输出 JSON 格式
        '-s'  # 显示函数/方法的具体复杂度分数
    ]

    process = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if process.stderr:
        print(f"Radon 错误输出: {process.stderr}")

    if not process.stdout.strip():
        print("Radon 无输出")
        return []

    results = []

    try:
        # 清除 ANSI 颜色控制符
        clean_stdout = ANSI_ESCAPE_RE.sub('', process.stdout)

        for line in clean_stdout.splitlines():
            line = line.strip()
            if not line:
                continue

            data = json.loads(line)

            for file, items in data.items():
                for item in items:
                    # class / function
                    results.append({
                        "type": "radon",
                        "object_type": item.get("type"),
                        "name": item.get("name"),
                        "line": item.get("lineno"),
                        "complexity": item.get("complexity"),
                        "rank": item.get("rank"),
                        "message": f"圈复杂度 {item.get('complexity')}（等级 {item.get('rank')}）",
                        "severity": "warning" if item.get("complexity", 0) <= 10 else "error"
                    })

                    # class methods
                    if item.get("type") == "class":
                        for method in item.get("methods", []):
                            results.append({
                                "type": "radon",
                                "object_type": "method",
                                "class": item.get("name"),
                                "name": method.get("name"),
                                "line": method.get("lineno"),
                                "complexity": method.get("complexity"),
                                "rank": method.get("rank"),
                                "message": f"{item.get('name')}.{method.get('name')} 圈复杂度 {method.get('complexity')}",
                                "severity": "warning" if method.get("complexity", 0) <= 10 else "error"
                            })

        return results

    except json.JSONDecodeError as e:
        print(f"Radon JSON解析失败: {e}")
        print("Radon 原始输出（清洗前）:")
        print(repr(process.stdout))
        return []


def run_pyright(file_path: str) -> list:
    pyright_config_file = os.path.abspath(
        os.path.join(os.path.dirname(__file__), PYRIGHT_CONFIG_PATH)
    )
    pyright_config_dir = os.path.dirname(pyright_config_file)

    if not os.path.exists(pyright_config_file):
        print(f"Pyright 配置文件不存在: {pyright_config_file}")
        return []

    cmd = [
        'pyright',
        file_path,
        '--project', pyright_config_dir,
        '--outputjson'
    ]

    process = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    if process.stderr:
        print(f"Pyright 错误输出: {process.stderr}")

    if not process.stdout.strip():
        print("Pyright 无输出")
        return []

    try:
        return json.loads(process.stdout)
    except json.JSONDecodeError as e:
        print(f"Pyright JSON解析失败: {e}")
        print(f"Pyright 原始输出: {process.stdout}")
        return []


def run_pydocstyle(file_path: str) -> list:
    pydocstyle_config = os.path.abspath(
        os.path.join(os.path.dirname(__file__), PYDOCSTYLE_CONFIG_PATH)
    )

    if not os.path.exists(pydocstyle_config):
        print(f"Pydocstyle 配置文件不存在: {pydocstyle_config}")
        return []

    cmd = [
        'pydocstyle',
        file_path,
        '--config', pydocstyle_config
    ]

    process = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if process.stderr:
        print(f"Pydocstyle 错误输出: {process.stderr}")

    if not process.stdout.strip():
        print("Pydocstyle 无输出")
        return []

    results = []

    # 示例输出：
    # your_file.py:10 in public function `foo`:
    #     D103: Missing docstring in public function
    lines = process.stdout.splitlines()

    current_file = None
    current_line = None
    current_object = None

    for line in lines:
        line = line.strip()
        # 文件 + 行号

        match = re.match(r"(.+?):(\d+)", line)
        if match:
            current_file = match.group(1)
            current_line = int(match.group(2))
            current_object = None
            continue

        # 错误码 + 描述
        match = re.match(r"(D\d+):\s+(.*)", line)
        if match:
            code = match.group(1)
            message = match.group(2)

            results.append({
                "type": "pydocstyle",
                "code": code,
                "file": current_file,
                "line": current_line,
                "object": current_object,
                "message": message,
                "severity": "warning"
            })

    return results
