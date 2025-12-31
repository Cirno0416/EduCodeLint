import logging
from typing import List, Dict, Any

from backend.db.dto.issue_dto import IssueDTO
from backend.constants.metric_category import MetricCategory
from backend.constants.tool_name import ToolName


# TODO: 统一metric_name和severity标准
def parse_issues_to_dtos(results: Dict[str, Any], analysis_id: str) -> List[IssueDTO]:
    issue_dtos: List[IssueDTO] = []

    issue_dtos.extend(_parse_bandit(results, analysis_id))
    issue_dtos.extend(_parse_flake8(results, analysis_id))
    issue_dtos.extend(_parse_pylint(results, analysis_id))
    issue_dtos.extend(_parse_pydocstyle(results, analysis_id))
    issue_dtos.extend(_parse_radon(results, analysis_id))
    issue_dtos.extend(_parse_pyright(results, analysis_id))

    return issue_dtos


def _parse_bandit(results: Dict[str, Any], analysis_id: str) -> List[IssueDTO]:
    dtos: List[IssueDTO] = []
    for item in results.get(ToolName.BANDIT, []):
        dtos.append(IssueDTO(
            analysis_id=analysis_id,
            file_path=item.get("filename"),
            tool=ToolName.BANDIT,
            metric_category=MetricCategory.SECURITY_VULNERABILITY,
            metric_name=item.get("test_name"),
            rule_id=item.get("test_id"),
            line=item.get("line_number"),
            severity=item.get("issue_severity"),
            message=item.get("issue_text")
        ))
    return dtos


def _parse_flake8(results: Dict[str, Any], analysis_id: str) -> List[IssueDTO]:
    dtos: List[IssueDTO] = []

    def get_metric_category(code_val: str) -> str:
        if code_val.startswith("C"):
            return MetricCategory.COMPLEXITY
        elif code_val.startswith("D"):
            return MetricCategory.DOCUMENTATION
        elif code_val.startswith(("E", "W", "N")):
            return MetricCategory.STYLE
        elif code_val.startswith("F"):
            return MetricCategory.POTENTIAL_ERROR
        else:
            logging.warning(f"Flake8 返回了未知规则: {code_val}")
            return "invalid"

    for _, issues in results.get(ToolName.FLAKE8, {}).items():
        for item in issues:
            code = item.get("code", "")

            dtos.append(IssueDTO(
                analysis_id=analysis_id,
                file_path=item.get("filename"),
                tool=ToolName.FLAKE8,
                metric_category=get_metric_category(code),
                metric_name=code,
                rule_id=code,
                line=item.get("line_number"),
                severity="warning",
                message=item.get("text")
            ))
    return dtos


def _parse_pylint(results: Dict[str, Any], analysis_id: str) -> List[IssueDTO]:
    dtos: List[IssueDTO] = []
    for item in results.get(ToolName.PYLINT, []):
        dtos.append(IssueDTO(
            analysis_id=analysis_id,
            file_path=item.get("path"),
            tool=ToolName.PYLINT,
            metric_category=MetricCategory.CODE_SMELL,
            metric_name=item.get("symbol"),
            rule_id=item.get("message-id"),
            line=item.get("line"),
            severity=item.get("type"),
            message=item.get("message")
        ))
    return dtos


def _parse_pydocstyle(results: Dict[str, Any], analysis_id: str) -> List[IssueDTO]:
    dtos: List[IssueDTO] = []
    for item in results.get(ToolName.PYDOCSTYLE, []):
        dtos.append(IssueDTO(
            analysis_id=analysis_id,
            file_path=item.get("file"),
            tool=ToolName.PYDOCSTYLE,
            metric_category=MetricCategory.DOCUMENTATION,
            metric_name=item.get("code"),
            rule_id=item.get("code"),
            line=item.get("line"),
            severity=item.get("severity"),
            message=item.get("message")
        ))
    return dtos


def _parse_radon(results: Dict[str, Any], analysis_id: str) -> List[IssueDTO]:
    dtos: List[IssueDTO] = []
    for item in results.get(ToolName.RADON, []):
        dtos.append(IssueDTO(
            analysis_id=analysis_id,
            file_path=item.get("file"),
            tool=ToolName.RADON,
            metric_category=MetricCategory.COMPLEXITY,
            metric_name=item.get("name"),
            rule_id="",
            line=item.get("line"),
            severity=item.get("severity"),
            message=item.get("message")
        ))
    return dtos


def _parse_pyright(results: Dict[str, Any], analysis_id: str) -> List[IssueDTO]:
    dtos: List[IssueDTO] = []
    for item in results.get(ToolName.PYRIGHT, {}).get("generalDiagnostics", []):
        dtos.append(IssueDTO(
            analysis_id=analysis_id,
            file_path=item.get("file"),
            tool=ToolName.PYRIGHT,
            metric_category=MetricCategory.POTENTIAL_ERROR,
            metric_name=item.get("rule"),
            rule_id=item.get("rule"),
            line=item.get("range", {}).get("start", {}).get("line"),
            severity=item.get("severity"),
            message=item.get("message")
        ))
    return dtos
