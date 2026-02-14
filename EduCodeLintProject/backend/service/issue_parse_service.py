import logging

from backend.constant.metric_severity import METRIC_SEVERITY_MAP
from backend.entity.dto.issue_dto import IssueDTO
from backend.constant.metric_category import MetricCategory
from backend.constant.tool_name import ToolName
from backend.constant.metric_name import MetricName
from backend.constant.severity_level import SeverityLevel


def parse_issues_to_dtos(raw: dict[str, any], exclude_tools: list = None) -> list[IssueDTO]:

    issue_dtos: list[IssueDTO] = []
    exclude_tools = exclude_tools or []

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

        issue_dtos.extend(tool_func(raw))

    return issue_dtos


def _parse_bandit(results: dict[str, any]) -> list[IssueDTO]:
    dtos: list[IssueDTO] = []
    for item in results.get(ToolName.BANDIT, []):
        rule_id = item.get("test_id")
        metric_name = _get_metric_name_bandit(rule_id)
        sererity = METRIC_SEVERITY_MAP.get(metric_name, SeverityLevel.LOW)

        dtos.append(IssueDTO(
            metric_summary_id=-1,
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


def _parse_flake8(results: dict[str, any]) -> list[IssueDTO]:
    dtos: list[IssueDTO] = []

    for _, issues in results.get(ToolName.FLAKE8, {}).items():
        for item in issues:
            rule_id = item.get("code")
            metric_category = _get_metric_category_flake8(rule_id)
            metric_name = _get_metric_name_flake8(rule_id)
            severity = METRIC_SEVERITY_MAP.get(metric_name, SeverityLevel.LOW)

            dtos.append(IssueDTO(
                metric_summary_id=-1,
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


def _parse_pylint(results: dict[str, any]) -> list[IssueDTO]:
    dtos: list[IssueDTO] = []
    for item in results.get(ToolName.PYLINT, []):
        rule_id = item.get("message-id")
        metric_category = _get_metric_category_pylint(rule_id)
        metric_name = _get_metric_name_pylint(rule_id)
        severity = METRIC_SEVERITY_MAP.get(metric_name, SeverityLevel.LOW)

        dtos.append(IssueDTO(
            metric_summary_id=-1,
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
        "R0915": MetricCategory.CODE_SMELL,
        # 大类
        "R0902": MetricCategory.CODE_SMELL,
        "R0904": MetricCategory.CODE_SMELL,
        # 参数过多
        "R0913": MetricCategory.CODE_SMELL,
        # 过多分支
        "R0912": MetricCategory.CODE_SMELL,
        # 深层嵌套
        "R1702": MetricCategory.CODE_SMELL,

        # 未使用赋值（参数） W0613
        "W0613": MetricCategory.POTENTIAL_ERROR
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

        "W0613": MetricName.UNUSED_ASSIGNMENT
    }

    return PYLINT_METRIC_NAME_MAPPING.get(rule_id, MetricName.UNKNOWN_METRIC_NAME)


def _parse_pydocstyle(results: dict[str, any]) -> list[IssueDTO]:
    dtos: list[IssueDTO] = []
    for item in results.get(ToolName.PYDOCSTYLE, []):
        rule_id = item.get("code")
        metric_name = _get_metric_name_pydocstyle(rule_id)
        severity = METRIC_SEVERITY_MAP.get(metric_name, SeverityLevel.LOW)

        dtos.append(IssueDTO(
            metric_summary_id=-1,
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


def _parse_radon(results: dict[str, any]) -> list[IssueDTO]:
    dtos: list[IssueDTO] = []
    for item in results.get(ToolName.RADON, []):
        dtos.append(IssueDTO(
            metric_summary_id=-1,
            tool=ToolName.RADON,
            metric_category=MetricCategory.COMPLEXITY,
            metric_name=MetricName.CYCLOMATIC_COMPLEXITY,
            rule_id=item.get("complexity"),
            line=item.get("line"),
            severity=SeverityLevel.HIGH,
            message=item.get("message")
        ))
    return dtos


def _parse_pyright(results: dict[str, any]) -> list[IssueDTO]:
    dtos: list[IssueDTO] = []
    for item in results.get(ToolName.PYRIGHT, {}).get("generalDiagnostics", []):
        rule_id = item.get("rule")
        metric_name = _get_metric_name_pyright(rule_id)
        severity = METRIC_SEVERITY_MAP.get(metric_name, SeverityLevel.LOW)

        dtos.append(IssueDTO(
            metric_summary_id=-1,
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
