from backend.constant.metric_category import MetricCategory


DEFAULT_WEIGHTS = {
    MetricCategory.CODE_STYLE: 0.15,
    MetricCategory.CODE_SMELL: 0.20,
    MetricCategory.COMPLEXITY: 0.20,
    MetricCategory.SECURITY_VULNERABILITY: 0.15,
    MetricCategory.POTENTIAL_ERROR: 0.30
}

# 权重上下限配置
WEIGHT_LOWER_BOUNDS = {
    MetricCategory.CODE_STYLE: 0.10,              # 代码规范性
    MetricCategory.CODE_SMELL: 0.05,              # 代码异味
    MetricCategory.COMPLEXITY: 0.05,              # 圈复杂度
    MetricCategory.SECURITY_VULNERABILITY: 0.10,  # 安全漏洞（下限保护）
    MetricCategory.POTENTIAL_ERROR: 0.05          # 潜在错误
}

WEIGHT_UPPER_BOUNDS = {
    MetricCategory.CODE_STYLE: 0.50,              # 代码规范性
    MetricCategory.CODE_SMELL: 0.40,              # 代码异味
    MetricCategory.COMPLEXITY: 0.40,              # 圈复杂度
    MetricCategory.SECURITY_VULNERABILITY: 0.45,  # 安全漏洞
    MetricCategory.POTENTIAL_ERROR: 0.35          # 潜在错误
}
