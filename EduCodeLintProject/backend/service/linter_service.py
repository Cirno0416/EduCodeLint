import json
import re
import subprocess
import logging

from backend.constant.config_path import ConfigPath
from backend.constant.tool_name import ToolName


def run_linters(file_path: str, exclude_tools: list = None) -> dict:
    exclude_tools = exclude_tools or []
    tool_mapping = {
        ToolName.PYLINT: _run_pylint,
        ToolName.FLAKE8: _run_flake8,
        ToolName.BANDIT: _run_bandit,
        ToolName.RADON: _run_radon,
        ToolName.PYRIGHT: _run_pyright,
        ToolName.PYDOCSTYLE: _run_pydocstyle
    }
    results = {}

    for tool_name, tool_func in tool_mapping.items():
        if tool_name in exclude_tools:
            results[tool_name] = []
            continue

        try:
            results[tool_name] = tool_func(file_path)
        except Exception as e:
            logging.error(f"运行 {tool_name} 失败: {e}")
            results[tool_name] = {"error": str(e)}

    return results


def _run_pylint(file_path: str) -> list:
    cmd = [
        ToolName.PYLINT,
        file_path,
        f'--rcfile={ConfigPath.PYLINT_CONFIG}',
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
        logging.error(f"Pylint 错误输出: {process.stderr}")
        return []

    if not process.stdout.strip():
        logging.info("Pylint 无输出")
        return []

    try:
        return json.loads(process.stdout)
    except json.JSONDecodeError as e:
        logging.error(f"Pylint JSON解析失败: {e}")
        return []


def _run_flake8(file_path: str) -> list:
    cmd = [
        ToolName.FLAKE8,
        file_path,
        f'--config={ConfigPath.FLAKE8_CONFIG}',
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
        logging.error(f"Flake8 错误输出: {process.stderr}")

    if not process.stdout.strip():
        logging.info("Flake8 无输出")
        return []

    try:
        return json.loads(process.stdout)
    except json.JSONDecodeError as e:
        logging.error(f"Flake8 JSON解析失败: {e}")
        return []


def _run_bandit(file_path: str) -> list:
    cmd = [
        ToolName.BANDIT,
        file_path,
        '-c', ConfigPath.BANDIT_CONFIG,
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
        logging.error(f"Bandit 错误输出: {process.stderr}")

    if not process.stdout.strip():
        logging.info("Bandit 无输出")
        return []

    try:
        # Bandit JSON 输出包含 results 字段，提取核心结果
        result = json.loads(process.stdout)
        return result.get('results', [])
    except json.JSONDecodeError as e:
        logging.error(f"Bandit JSON解析失败: {e}")
        return []


def _run_radon(file_path: str) -> list:
    cmd = [
        ToolName.RADON,
        'cc',
        file_path,
        '-j',
        '-s'
    ]

    process = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if process.stderr:
        logging.error(f"Radon 错误输出: {process.stderr}")

    if not process.stdout.strip():
        logging.info("Radon 无输出")
        return []

    try:
        return _parse_radon_output(process.stdout)
    except json.JSONDecodeError as e:
        logging.error(f"Radon JSON 解析失败: {e}")
        return []


def _parse_radon_output(stdout: str) -> list:
    results = []
    # 去除 ANSI stdout
    clean_stdout = re.sub(r'\x1b\[[0-9;]*m', '', stdout)
    # 圈复杂度阈值
    THRESHOLD = 10

    for line in clean_stdout.splitlines():
        if not line.strip():
            continue

        data = json.loads(line)
        for items in data.values():
            for item in items:
                results.extend(
                    _collect_item_issues(item, THRESHOLD)
                )

    return results


def _collect_item_issues(item: dict, threshold: int) -> list:
    issues = []

    complexity = item.get("complexity", 0)
    if complexity > threshold:
        object_type = item.get("type")
        name = item.get("name")
        line = item.get("lineno")

        issues.append({
                "object_type": object_type,
                "name": name,
                "line": line,
                "complexity": complexity,
                "message": f"{object_type} `{name}` 圈复杂度 {complexity}",
            }
        )

    return issues


def _run_pyright(file_path: str) -> list:
    cmd = [
        ToolName.PYRIGHT,
        file_path,
        '--project', ConfigPath.PYRIGHT_CONFIG,
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
        logging.error(f"Pyright 错误输出: {process.stderr}")

    if not process.stdout.strip():
        logging.info("Pyright 无输出")
        return []

    try:
        return json.loads(process.stdout)
    except json.JSONDecodeError as e:
        logging.error(f"Pyright JSON解析失败: {e}")
        return []


def _run_pydocstyle(file_path: str) -> list:
    cmd = [
        ToolName.PYDOCSTYLE,
        file_path,
        '--config', ConfigPath.PYDOCSTYLE_CONFIG
    ]

    process = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if process.stderr:
        logging.error(f"Pydocstyle 错误输出: {process.stderr}")

    if not process.stdout.strip():
        logging.info("Pydocstyle 无输出")
        return []

    results = []

    lines = process.stdout.splitlines()
    current_line = None

    for line in lines:
        line = line.strip()

        # 文件 + 行号
        match = re.match(r"(.+?):(\d+)", line)
        if match:
            current_line = int(match.group(2))
            continue

        # 错误码 + 描述
        match = re.match(r"(D\d+):\s+(.*)", line)
        if match:
            code = match.group(1)
            message = match.group(2)
            results.append({
                "code": code,
                "line": current_line,
                "message": message,
            })

    return results
