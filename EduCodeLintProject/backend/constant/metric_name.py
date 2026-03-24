class MetricName:

    # ===== 代码规范性 =====

    # 变量和函数命名风格
    VARIABLE_FUNCTION_NAMING = "变量和函数命名风格"

    # 类命名风格
    CLASS_NAMING = "类命名风格"

    # 行长度限制
    LINE_LENGTH = "行长度限制"

    # 括号和空白使用
    BRACKET_WHITESPACE = "括号和空白使用"

    # 空行使用
    BLANK_LINES = "空行使用"

    # ===== 代码异味 =====

    # 过长函数/方法
    LONG_FUNCTION_OR_METHOD = "过长函数/方法"

    # 大类
    LARGE_CLASS = "大类"

    # 参数过多
    TOO_MANY_PARAMETERS = "参数过多"

    # 过多分支
    TOO_MANY_BRANCHES = "过多分支"

    # 深层嵌套
    DEEP_NESTING = "深层嵌套"

    # ===== 代码复杂度 =====

    # 圈复杂度
    CYCLOMATIC_COMPLEXITY = "圈复杂度"

    # ===== 潜在错误 =====

    # 未定义名称引用
    UNDEFINED_NAME = "未定义名称引用"

    # 未使用的赋值
    UNUSED_ASSIGNMENT = "未使用的赋值"

    # 变量赋值前使用
    USE_BEFORE_ASSIGNMENT = "变量赋值前使用"

    # 不一致返回
    INCONSISTENT_RETURN = "不一致返回"

    # ===== 安全漏洞 =====

    # 危险函数调用
    DANGEROUS_FUNCTION_CALL = "危险函数调用"

    # 异常忽略
    IGNORED_EXCEPTION = "异常忽略"

    # 硬编码敏感信息
    HARDCODED_SENSITIVE_INFO = "硬编码敏感信息"

    # ===== 注释与文档 =====

    # 缺少模块Docstring
    MISSING_MODULE_DOCSTRING = "缺少模块Docstring"

    # 不规范的Docstring
    NONSTANDARD_DOCSTRING = "不规范的Docstring"

    # 规范的Docstring（这个不算问题，仅用来统计数据）
    STANDARD_DOCSTRING = "规范的Docstring"

    # ===== 异常情况 =====

    # 未知指标名称
    UNKNOWN_METRIC_NAME = "未知指标名称"
