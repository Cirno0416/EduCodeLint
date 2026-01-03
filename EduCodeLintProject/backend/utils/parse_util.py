import logging
import uuid
from typing import List, Dict, Any

from backend.entity.dto.issue_dto import IssueDTO
from backend.constant.metric_category import MetricCategory
from backend.constant.tool_name import ToolName
from backend.constant.metric_name import MetricName
from backend.constant.severity_level import SeverityLevel


def parse_issues_to_dtos(results: Dict[str, Any], exclude_tools: list = None) -> List[IssueDTO]:
    issue_dtos: List[IssueDTO] = []
    exclude_tools = exclude_tools or []

    analysis_id = _generate_analysis_id()

    tool_mapping = {
        ToolName.PYLINT: _parse_pylint,
        ToolName.FLAKE8: _parse_flake8,
        ToolName.BANDIT: _parse_bandit,
        ToolName.RADON: _parse_radon,
        ToolName.PYRIGHT: _parse_pyright,
        ToolName.PYDOCSTYLE: _parse_pydocstyle
    }

    for tool_name, tool_func in tool_mapping.items():
        if tool_name in exclude_tools:
            continue

        issue_dtos.extend(tool_func(results, analysis_id))

    return issue_dtos


def _generate_analysis_id() -> str:
    return str(uuid.uuid4())


def _parse_bandit(results: Dict[str, Any], analysis_id: str) -> List[IssueDTO]:
    dtos: List[IssueDTO] = []
    for item in results.get(ToolName.BANDIT, []):
        rule_id = item.get("test_id")
        metric_name = _get_metric_name_bandit(rule_id)
        sererity = _get_severity_bandit(rule_id)

        dtos.append(IssueDTO(
            analysis_id=analysis_id,
            file_path=item.get("filename"),
            tool=ToolName.BANDIT,
            metric_category=MetricCategory.SECURITY_VULNERABILITY,
            metric_name=metric_name,
            rule_id=rule_id,
            line=item.get("line_number"),
            severity=sererity,
            message=item.get("issue_text")
        ))
    return dtos


def _get_metric_name_bandit(rule_id: str) -> str:
    BANDIT_METRIC_NAME_MAPPING = {
        # 危险函数调用
        "B102": MetricName.DANGEROUS_FUNCTION_CALL,
        # 捕获异常未处理
        "B110": MetricName.IGNORED_EXCEPTION,
        # 硬编码敏感信息
        "B105": MetricName.HARDCODED_SENSITIVE_INFO
    }

    return BANDIT_METRIC_NAME_MAPPING.get(rule_id, MetricName.UNKNOWN_METRIC_NAME)


def _get_severity_bandit(rule_id: str) -> str:
    BANDIT_SEVERITY_MAPPING = {
        "B102": SeverityLevel.MEDIUM,
        "B110": SeverityLevel.LOW,
        "B105": SeverityLevel.MEDIUM
    }
    return BANDIT_SEVERITY_MAPPING.get(rule_id, SeverityLevel.LOW)


def _parse_flake8(results: Dict[str, Any], analysis_id: str) -> List[IssueDTO]:
    dtos: List[IssueDTO] = []

    for _, issues in results.get(ToolName.FLAKE8, {}).items():
        for item in issues:
            rule_id = item.get("code")
            metric_category = _get_metric_category_flake8(rule_id)
            metric_name = _get_metric_name_flake8(rule_id)
            severity = _get_severity_flake8(rule_id)

            dtos.append(IssueDTO(
                analysis_id=analysis_id,
                file_path=item.get("filename"),
                tool=ToolName.FLAKE8,
                metric_category=metric_category,
                metric_name=metric_name,
                rule_id=rule_id,
                line=item.get("line_number"),
                severity=severity,
                message=item.get("text")
            ))
    return dtos


def _get_metric_category_flake8(code_val: str) -> str:
    if code_val.startswith("C"):
        return MetricCategory.COMPLEXITY
    elif code_val.startswith("D"):
        return MetricCategory.DOCUMENTATION
    elif code_val.startswith(("E", "W", "N")):
        return MetricCategory.CODE_STYLE
    elif code_val.startswith("F"):
        return MetricCategory.POTENTIAL_ERROR
    else:
        logging.warning(f"Flake8 返回了未知规则: {code_val}")
        return MetricCategory.UNKNOWN_METRIC_CATEGORY


def _get_metric_name_flake8(rule_id: str) -> str:
    FLAKE8_METRIC_NAME_MAPPING = {
        # 圈复杂度 > 10
        "C901": MetricName.CYCLOMATIC_COMPLEXITY,

        # 缺少模块/类/函数 Docstring
        "D100": MetricName.MISSING_MODULE_DOCSTRING,
        "D205": MetricName.NONSTANDARD_DOCSTRING,

        # 行长度限制
        "E501": MetricName.LINE_LENGTH,
        # 括号和空白使用
        "E201": MetricName.BRACKET_WHITESPACE,
        "E202": MetricName.BRACKET_WHITESPACE,
        "E225": MetricName.BRACKET_WHITESPACE,
        "E231": MetricName.BRACKET_WHITESPACE,
        # 空行使用
        "E301": MetricName.BLANK_LINES,
        "E302": MetricName.BLANK_LINES,
        "E303": MetricName.BLANK_LINES,
        "E305": MetricName.BLANK_LINES,
        "W391": MetricName.BLANK_LINES,

        # 使用未定义名称
        "F821": MetricName.UNDEFINED_NAME,
        # 局部变量赋值但未使用
        "F841": MetricName.UNUSED_ASSIGNMENT,

        # 变量和函数命名风格
        "N806": MetricName.VARIABLE_FUNCTION_NAMING,
        "N802": MetricName.VARIABLE_FUNCTION_NAMING,
        # 类命名风格
        "N801": MetricName.CLASS_NAMING,
        # 参数名不是 snake_case
        "N803": MetricName.VARIABLE_FUNCTION_NAMING,
        # 常量名非全大写
        "N812": MetricName.VARIABLE_FUNCTION_NAMING
    }

    return FLAKE8_METRIC_NAME_MAPPING.get(rule_id, MetricName.UNKNOWN_METRIC_NAME)


def _get_severity_flake8(rule_id: str) -> str:
    FLAKE8_SEVERITY_MAPPING = {
        "C901": SeverityLevel.HIGH,

        "D100": SeverityLevel.MEDIUM,
        "D205": SeverityLevel.LOW,

        "E201": SeverityLevel.LOW,
        "E202": SeverityLevel.LOW,
        "E225": SeverityLevel.LOW,
        "E231": SeverityLevel.LOW,
        "E301": SeverityLevel.LOW,
        "E302": SeverityLevel.LOW,
        "E303": SeverityLevel.LOW,
        "E305": SeverityLevel.LOW,
        "E501": SeverityLevel.MEDIUM,
        "W391": SeverityLevel.LOW,

        "F821": SeverityLevel.HIGH,
        "F841": SeverityLevel.LOW,

        "N801": SeverityLevel.LOW,
        "N802": SeverityLevel.LOW,
        "N803": SeverityLevel.LOW,
        "N806": SeverityLevel.LOW,
        "N812": SeverityLevel.LOW
    }

    return FLAKE8_SEVERITY_MAPPING.get(rule_id, SeverityLevel.LOW)


def _parse_pylint(results: Dict[str, Any], analysis_id: str) -> List[IssueDTO]:
    dtos: List[IssueDTO] = []
    for item in results.get(ToolName.PYLINT, []):
        rule_id = item.get("message-id")
        metric_category = _get_metric_category_pylint(rule_id)
        metric_name = _get_metric_name_pylint(rule_id)
        severity = _get_severity_pylint(rule_id)

        dtos.append(IssueDTO(
            analysis_id=analysis_id,
            file_path=item.get("path"),
            tool=ToolName.PYLINT,
            metric_category=metric_category,
            metric_name=metric_name,
            rule_id=rule_id,
            line=item.get("line"),
            severity=severity,
            message=item.get("message")
        ))
    return dtos


def _get_metric_category_pylint(rule_id: str) -> str:
    PYLINT_CATEGORY_MAPPING = {
        # 过长函数/方法
        "R0915": MetricCategory.CODE_STYLE,
        # 大类
        "R0902": MetricCategory.CODE_STYLE,
        "R0904": MetricCategory.CODE_STYLE,
        # 参数过多
        "R0913": MetricCategory.CODE_STYLE,
        # 过多分支
        "R0912": MetricCategory.CODE_STYLE,
        # 深层嵌套
        "R1702": MetricCategory.CODE_STYLE,

        # 未定义名称
        "E0602": MetricCategory.POTENTIAL_ERROR,
        # 赋值前使用
        "E0601": MetricCategory.POTENTIAL_ERROR,
        # 未使用的赋值
        "W0612": MetricCategory.POTENTIAL_ERROR,
        "W0613": MetricCategory.POTENTIAL_ERROR,
        "W0611": MetricCategory.POTENTIAL_ERROR,
        # 不一致返回
        "R1710": MetricCategory.POTENTIAL_ERROR,
    }

    return PYLINT_CATEGORY_MAPPING.get(rule_id, MetricCategory.UNKNOWN_METRIC_CATEGORY)


def _get_metric_name_pylint(rule_id: str) -> str:
    PYLINT_METRIC_NAME_MAPPING = {
        "R0915": MetricName.LONG_FUNCTION_OR_METHOD,
        "R0902": MetricName.LARGE_CLASS,
        "R0904": MetricName.LARGE_CLASS,
        "R0913": MetricName.TOO_MANY_PARAMETERS,
        "R0912": MetricName.TOO_MANY_BRANCHES,
        "R1702": MetricName.DEEP_NESTING,

        "E0602": MetricName.UNDEFINED_NAME,
        "E0601": MetricName.USE_BEFORE_ASSIGNMENT,
        "W0612": MetricName.UNUSED_ASSIGNMENT,
        "W0613": MetricName.UNUSED_ASSIGNMENT,
        "W0611": MetricName.UNUSED_ASSIGNMENT,
        "R1710": MetricName.INCONSISTENT_RETURN,
    }

    return PYLINT_METRIC_NAME_MAPPING.get(rule_id, MetricName.UNKNOWN_METRIC_NAME)


def _get_severity_pylint(rule_id: str) -> str:
    PYLINT_SEVERITY_MAPPING = {
        "E0602": SeverityLevel.HIGH,
        "E0601": SeverityLevel.HIGH,
        "R1710": SeverityLevel.HIGH,

        "R0915": SeverityLevel.MEDIUM,
        "R0902": SeverityLevel.MEDIUM,
        "R0904": SeverityLevel.MEDIUM,
        "R0913": SeverityLevel.MEDIUM,
        "R0912": SeverityLevel.MEDIUM,
        "R1702": SeverityLevel.MEDIUM,

        "W0612": SeverityLevel.LOW,
        "W0613": SeverityLevel.LOW,
        "W0611": SeverityLevel.LOW,
    }

    return PYLINT_SEVERITY_MAPPING.get(rule_id, SeverityLevel.LOW)


def _parse_pydocstyle(results: Dict[str, Any], analysis_id: str) -> List[IssueDTO]:
    dtos: List[IssueDTO] = []
    for item in results.get(ToolName.PYDOCSTYLE, []):
        rule_id = item.get("code")
        metric_name = _get_metric_name_pydocstyle(rule_id)
        severity = _get_severity_pydocstyle(rule_id)

        dtos.append(IssueDTO(
            analysis_id=analysis_id,
            file_path=item.get("file"),
            tool=ToolName.PYDOCSTYLE,
            metric_category=MetricCategory.DOCUMENTATION,
            metric_name=metric_name,
            rule_id=rule_id,
            line=item.get("line"),
            severity=severity,
            message=item.get("message")
        ))
    return dtos


def _get_metric_name_pydocstyle(rule_id: str) -> str:
    PYDOCSTYLE_METRIC_MAPPING = {
        "D100": MetricName.MISSING_MODULE_DOCSTRING,
        "D205": MetricName.NONSTANDARD_DOCSTRING,
        "D400": MetricName.NONSTANDARD_DOCSTRING,
        "D415": MetricName.NONSTANDARD_DOCSTRING
    }

    return PYDOCSTYLE_METRIC_MAPPING.get(rule_id, MetricName.UNKNOWN_METRIC_NAME)


def _get_severity_pydocstyle(rule_id: str) -> str:
    PYDOCSTYLE_SEVERITY_MAPPING = {
        "D100": SeverityLevel.MEDIUM,
        "D205": SeverityLevel.LOW,
        "D400": SeverityLevel.LOW,
        "D415": SeverityLevel.LOW
    }

    return PYDOCSTYLE_SEVERITY_MAPPING.get(rule_id, SeverityLevel.LOW)


def _parse_radon(results: Dict[str, Any], analysis_id: str) -> List[IssueDTO]:
    dtos: List[IssueDTO] = []
    for item in results.get(ToolName.RADON, []):
        dtos.append(IssueDTO(
            analysis_id=analysis_id,
            file_path=item.get("file"),
            tool=ToolName.RADON,
            metric_category=MetricCategory.COMPLEXITY,
            metric_name=MetricName.CYCLOMATIC_COMPLEXITY,
            rule_id=item.get("name"),
            line=item.get("line"),
            severity=SeverityLevel.HIGH,
            message=item.get("message")
        ))
    return dtos


def _parse_pyright(results: Dict[str, Any], analysis_id: str) -> List[IssueDTO]:
    dtos: List[IssueDTO] = []
    for item in results.get(ToolName.PYRIGHT, {}).get("generalDiagnostics", []):
        rule_id = item.get("rule")
        metric_name = _get_metric_name_pyright(rule_id)
        severity = _get_severity_pyright(item.get("severity"))

        dtos.append(IssueDTO(
            analysis_id=analysis_id,
            file_path=item.get("file"),
            tool=ToolName.PYRIGHT,
            metric_category=MetricCategory.POTENTIAL_ERROR,
            metric_name=metric_name,
            rule_id=rule_id,
            line=item.get("range", {}).get("start", {}).get("line"),
            severity=severity,
            message=item.get("message")
        ))
    return dtos


def _get_metric_name_pyright(rule_id: str) -> str:
    PYRIGHT_METRIC_NAME_MAPPING = {
        # 使用未定义变量
        "reportUndefinedVariable": MetricName.UNDEFINED_NAME,

        # 变量赋值前使用
        "reportUnboundVariable": MetricName.USE_BEFORE_ASSIGNMENT,

        # 未使用变量/导入/函数
        "reportUnusedVariable": MetricName.UNUSED_ASSIGNMENT,
        "reportUnusedImport": MetricName.UNUSED_ASSIGNMENT,
        "reportUnusedFunction": MetricName.UNUSED_ASSIGNMENT,

        # 不一致返回
        "reportReturnType": MetricName.INCONSISTENT_RETURN
    }

    return PYRIGHT_METRIC_NAME_MAPPING.get(rule_id, MetricName.UNKNOWN_METRIC_NAME)


def _get_severity_pyright(rule_id: str) -> str:
    PYRIGHT_SEVERITY_MAPPING = {
        "reportUndefinedVariable": SeverityLevel.HIGH,
        "reportUnboundVariable": SeverityLevel.HIGH,
        "reportReturnType": SeverityLevel.HIGH,

        "reportUnusedVariable": SeverityLevel.LOW,
        "reportUnusedImport": SeverityLevel.LOW,
        "reportUnusedFunction": SeverityLevel.LOW
    }

    return PYRIGHT_SEVERITY_MAPPING.get(rule_id, SeverityLevel.LOW)
