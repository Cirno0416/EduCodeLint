from backend.constant.metric_name import MetricName
from backend.constant.severity_level import SeverityLevel


METRIC_SEVERITY_MAP = {
    MetricName.UNDEFINED_NAME: SeverityLevel.HIGH,
    MetricName.USE_BEFORE_ASSIGNMENT: SeverityLevel.HIGH,
    MetricName.INCONSISTENT_RETURN: SeverityLevel.HIGH,
    MetricName.UNUSED_ASSIGNMENT: SeverityLevel.MEDIUM,

    MetricName.CYCLOMATIC_COMPLEXITY: SeverityLevel.HIGH,

    MetricName.LONG_FUNCTION_OR_METHOD: SeverityLevel.HIGH,
    MetricName.TOO_MANY_BRANCHES: SeverityLevel.HIGH,
    MetricName.DEEP_NESTING: SeverityLevel.MEDIUM,
    MetricName.TOO_MANY_PARAMETERS: SeverityLevel.MEDIUM,
    MetricName.LARGE_CLASS: SeverityLevel.MEDIUM,

    MetricName.DANGEROUS_FUNCTION_CALL: SeverityLevel.HIGH,
    MetricName.HARDCODED_SENSITIVE_INFO: SeverityLevel.HIGH,
    MetricName.IGNORED_EXCEPTION: SeverityLevel.MEDIUM,

    MetricName.VARIABLE_FUNCTION_NAMING: SeverityLevel.MEDIUM,
    MetricName.CLASS_NAMING: SeverityLevel.MEDIUM,
    MetricName.LINE_LENGTH: SeverityLevel.LOW,
    MetricName.BRACKET_WHITESPACE: SeverityLevel.LOW,
    MetricName.BLANK_LINES: SeverityLevel.LOW,

    MetricName.MISSING_MODULE_DOCSTRING: SeverityLevel.LOW,
    MetricName.NONSTANDARD_DOCSTRING: SeverityLevel.LOW
}
