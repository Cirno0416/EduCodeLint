class MetricName:

    # ===== 代码规范性 =====

    # 变量和函数命名风格
    VARIABLE_FUNCTION_NAMING = "variable_function_naming"

    # 类命名风格
    CLASS_NAMING = "class_naming"

    # 行长度限制
    LINE_LENGTH = "line_length"

    # 括号和空白使用
    BRACKET_WHITESPACE = "bracket_whitespace"

    # 空行使用
    BLANK_LINES = "blank_lines"

    # ===== 代码异味 =====

    # 过长函数/方法
    LONG_FUNCTION_OR_METHOD = "long_function_or_method"

    # 大类
    LARGE_CLASS = "large_class"

    # 参数过多
    TOO_MANY_PARAMETERS = "too_many_parameters"

    # 过多分支
    TOO_MANY_BRANCHES = "too_many_branches"

    # 深层嵌套
    DEEP_NESTING = "deep_nesting"

    # ===== 代码复杂度 =====

    # 圈复杂度
    CYCLOMATIC_COMPLEXITY = "cyclomatic_complexity"

    # ===== 潜在错误 =====

    # 未定义名称引用
    UNDEFINED_NAME = "undefined_name"

    # 未使用的赋值
    UNUSED_ASSIGNMENT = "unused_assignment"

    # 变量赋值前使用
    USE_BEFORE_ASSIGNMENT = "use_before_assignment"

    # 不一致返回
    INCONSISTENT_RETURN = "inconsistent_return"

    # ===== 安全漏洞 =====

    # 危险函数调用
    DANGEROUS_FUNCTION_CALL = "dangerous_function_call"

    # 异常忽略
    IGNORED_EXCEPTION = "ignored_exception"

    # 硬编码敏感信息
    HARDCODED_SENSITIVE_INFO = "hardcoded_sensitive_info"

    # ===== 注释与文档 =====

    # 缺少模块Docstring
    MISSING_MODULE_DOCSTRING = "missing_module_docstring"

    # 不规范的Docstring
    NONSTANDARD_DOCSTRING = "nonstandard_docstring"

    # ===== 异常情况 =====

    # 未知指标名称
    UNKNOWN_METRIC_NAME = "unknown_metric_name"
