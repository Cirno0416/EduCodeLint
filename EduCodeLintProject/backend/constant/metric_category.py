from backend.constant.metric_name import MetricName


class MetricCategory:
    CODE_STYLE = "代码规范性"
    CODE_SMELL = "代码异味"
    COMPLEXITY = "复杂度"
    SECURITY_VULNERABILITY = "安全漏洞"
    POTENTIAL_ERROR = "潜在错误"
    DOCSTRING = "注释"

    UNKNOWN_METRIC_CATEGORY = "未知指标类型"


METRIC_CATEGORIES = {
    MetricCategory.CODE_STYLE: "代码规范性",
    MetricCategory.CODE_SMELL: "代码异味",
    MetricCategory.COMPLEXITY: "复杂度",
    MetricCategory.SECURITY_VULNERABILITY: "安全漏洞",
    MetricCategory.POTENTIAL_ERROR: "潜在错误",
    MetricCategory.DOCSTRING: "注释"
}


CATEGORY_MAPPING = {
    MetricCategory.CODE_STYLE: [
        MetricName.VARIABLE_FUNCTION_NAMING,
        MetricName.CLASS_NAMING,
        MetricName.LINE_LENGTH,
        MetricName.BRACKET_WHITESPACE,
        MetricName.BLANK_LINES,
    ],
    MetricCategory.CODE_SMELL: [
        MetricName.LONG_FUNCTION_OR_METHOD,
        MetricName.LARGE_CLASS,
        MetricName.TOO_MANY_PARAMETERS,
        MetricName.TOO_MANY_BRANCHES,
        MetricName.DEEP_NESTING,
    ],
    MetricCategory.POTENTIAL_ERROR: [
        MetricName.UNDEFINED_NAME,
        MetricName.UNUSED_ASSIGNMENT,
        MetricName.USE_BEFORE_ASSIGNMENT,
        MetricName.INCONSISTENT_RETURN,
    ],
    MetricCategory.SECURITY_VULNERABILITY: [
        MetricName.DANGEROUS_FUNCTION_CALL,
        MetricName.IGNORED_EXCEPTION,
        MetricName.HARDCODED_SENSITIVE_INFO,
    ],
    MetricCategory.COMPLEXITY: [
        MetricName.CYCLOMATIC_COMPLEXITY,
    ],
    MetricCategory.DOCSTRING: [
        MetricName.STANDARD_DOCSTRING,
        MetricName.NONSTANDARD_DOCSTRING,
        MetricName.MISSING_MODULE_DOCSTRING,
    ]
}
