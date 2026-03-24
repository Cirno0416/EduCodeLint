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
