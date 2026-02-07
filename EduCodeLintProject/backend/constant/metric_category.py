class MetricCategory:
    CODE_STYLE = "code_style"
    CODE_SMELL = "code_smell"
    COMPLEXITY = "complexity"
    SECURITY_VULNERABILITY = "security_vulnerability"
    POTENTIAL_ERROR = "potential_error"
    DOCUMENTATION = "documentation"

    UNKNOWN_METRIC_CATEGORY = "unknown_metric_category"


METRIC_CATEGORIES = {
    MetricCategory.CODE_STYLE: "code_style",
    MetricCategory.CODE_SMELL: "code_smell",
    MetricCategory.COMPLEXITY: "complexity",
    MetricCategory.POTENTIAL_ERROR: "security_vulnerability",
    MetricCategory.SECURITY_VULNERABILITY: "potential_error",
    MetricCategory.DOCUMENTATION: "documentation"
}
