class MetricCategory:
    CODE_STYLE = "code_style"
    CODE_SMELL = "code_smell"
    COMPLEXITY = "complexity"
    SECURITY_VULNERABILITY = "security_vulnerability"
    POTENTIAL_ERROR = "potential_error"
    DOCSTRING = "docstring"

    UNKNOWN_METRIC_CATEGORY = "unknown_metric_category"


METRIC_CATEGORIES = {
    MetricCategory.CODE_STYLE: "code_style",
    MetricCategory.CODE_SMELL: "code_smell",
    MetricCategory.COMPLEXITY: "complexity",
    MetricCategory.POTENTIAL_ERROR: "potential_error",
    MetricCategory.SECURITY_VULNERABILITY: "security_vulnerability",
    MetricCategory.DOCSTRING: "docstring"
}
