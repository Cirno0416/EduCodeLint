from backend.constant.metric_category import MetricCategory

DEFAULT_WEIGHTS = {
    MetricCategory.CODE_STYLE: 0.15,
    MetricCategory.CODE_SMELL: 0.20,
    MetricCategory.COMPLEXITY: 0.20,
    MetricCategory.SECURITY_VULNERABILITY: 0.15,
    MetricCategory.POTENTIAL_ERROR: 0.30
}

WEIGHTS = {
    MetricCategory: 0.15,
    MetricCategory.CODE_SMELL: 0.20,
    MetricCategory.COMPLEXITY: 0.20,
    MetricCategory.SECURITY_VULNERABILITY: 0.15,
    MetricCategory.POTENTIAL_ERROR: 0.30
}
