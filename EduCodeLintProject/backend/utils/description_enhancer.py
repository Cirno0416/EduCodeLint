import re

from backend.constant.tool_name import ToolName


class DescriptionEnhancer:
    """增强问题描述"""

    @classmethod
    def enhance(cls, tool_name, original_message):
        """radon 只有一种圈复杂度，固定格式，直接在 `linter_service` 中完成问题描述增强"""

        if tool_name == ToolName.BANDIT:
            # 硬编码密码检测
            if "Possible hardcoded password:" in original_message:
                match = re.search(r"Possible hardcoded password: '(.+)'$", original_message)
                if match:
                    password = match.group(1)
                    return f"可能的硬编码密码：'{password}'。密码泄露风险高，建议使用环境变量或配置文件存储。"
                return "可能的硬编码密码。密码泄露风险高，建议使用环境变量或配置文件存储。"

            # exec 函数检测
            if original_message == "Use of exec detected.":
                return "使用 exec() 函数，存在代码注入风险。建议避免使用 exec()。"

            # eval 函数检测
            if original_message == "Use of possibly insecure function - consider using safer ast.literal_eval.":
                return "使用 eval() 函数，存在代码注入风险。建议使用 ast.literal_eval() 替代。"

            # try-except-pass 检测
            if "Try, Except, Pass detected." in original_message:
                return "空的异常处理（try-except-pass）。错误会被静默隐藏，难以调试。建议捕获具体异常并添加日志。"

        if tool_name == ToolName.PYLINT:
            # 过多参数检测
            match = re.search(r"Too many arguments \((\d+)/(\d+)\)", original_message)
            if match:
                current = match.group(1)
                threshold = match.group(2)
                return f"函数参数过多（当前 {current}，阈值 {threshold}）。建议减少参数数量，或将相关参数封装为对象。"

            # 实例属性过多
            match = re.search(r"Too many instance attributes \((\d+)/(\d+)\)", original_message)
            if match:
                current = match.group(1)
                threshold = match.group(2)
                return f"类实例属性过多（当前 {current}，阈值 {threshold}）。建议拆分类，遵循单一职责原则。"

            # 公共方法过多
            match = re.search(r"Too many public methods \((\d+)/(\d+)\)", original_message)
            if match:
                current = match.group(1)
                threshold = match.group(2)
                return f"类公共方法过多（当前 {current}，阈值 {threshold}）。建议拆分类或使用策略模式简化接口。"

            # 分支过多
            match = re.search(r"Too many branches \((\d+)/(\d+)\)", original_message)
            if match:
                current = match.group(1)
                threshold = match.group(2)
                return f"分支过多（当前 {current}，阈值 {threshold}）。建议使用字典映射或策略模式替代。"

            # 嵌套过深
            match = re.search(r"Too many nested blocks \((\d+)/(\d+)\)", original_message)
            if match:
                current = match.group(1)
                threshold = match.group(2)
                return f"代码嵌套过深（当前 {current}，阈值 {threshold}）。建议使用卫语句提前返回，或提取内部逻辑为独立函数。"

            # 语句过多
            match = re.search(r"Too many statements \((\d+)/(\d+)\)", original_message)
            if match:
                current = match.group(1)
                threshold = match.group(2)
                return f"函数/方法过长（当前 {current}，阈值 {threshold}）。建议拆分为多个小函数。"

            # 未使用的参数
            match = re.search(r"Unused argument '([^']+)'", original_message)
            if match:
                arg_name = match.group(1)
                return f"未使用的参数 '{arg_name}'。建议删除或用下划线前缀（_arg_name）表示忽略。"

        if tool_name == ToolName.PYRIGHT:
            # 未使用的导入
            match = re.search(r'Import "([^"]+)" is not accessed', original_message)
            if match:
                import_name = match.group(1)
                return f"未使用的导入 '{import_name}'。建议删除未使用的导入，保持代码简洁。"

            # 未使用的变量
            match = re.search(r'Variable "([^"]+)" is not accessed', original_message)
            if match:
                var_name = match.group(1)
                return f"未使用的变量 '{var_name}'。建议删除或用下划线（_{var_name}）表示忽略。"

            # 未使用的函数
            match = re.search(r'Function "([^"]+)" is not accessed', original_message)
            if match:
                func_name = match.group(1)
                return f"未使用的函数 '{func_name}'。建议删除或检查是否遗漏调用。"

            # 未定义的变量
            match = re.search(r'"([^"]+)" is not defined', original_message)
            if match:
                var_name = match.group(1)
                return f"未定义的变量 '{var_name}'。请确保变量已定义或正确导入。"

            # 返回类型不一致
            if "is not assignable to return type" in original_message:
                match = re.search(r'Type "([^"]+)" is not assignable to return type "([^"]+)"', original_message)
                if match:
                    actual_type = match.group(1)
                    expected_type = match.group(2)
                    return f"返回类型不匹配。实际返回 '{actual_type}'，但函数声明返回 '{expected_type}'。建议统一返回类型。"

            # 变量未绑定（使用前未赋值）
            match = re.search(r'"([^"]+)" is unbound', original_message)
            if match:
                var_name = match.group(1)
                return f"变量 '{var_name}' 在使用前未赋值。请确保在使用前已初始化。"

        if tool_name == ToolName.FLAKE8:
            # 左括号后多余空格
            match = re.search(r"whitespace after '([(\[{])'", original_message)
            if match:
                punct = match.group(1)
                return f"标点 '{punct}' 后存在多余空格，建议删除。"

            # 右括号前多余空格
            match = re.search(r"whitespace before '([)\]}])'", original_message)
            if match:
                punct = match.group(1)
                return f"标点 '{punct}' 前存在多余空格，建议删除。"

            # 运算符缺少空格
            if "missing whitespace around operator" in original_message:
                return "运算符前后缺少空格。建议在运算符两侧各添加一个空格。"

            # 逗号/冒号/分号后缺少空格
            match = re.search(r"missing whitespace after '([,;:])'", original_message)
            if match:
                punct = match.group(1)
                return f"标点 '{punct}' 后缺少空格，建议添加。"

            # 函数/类前空行不足
            match = re.search(r"expected (\d+) blank lines, found (\d+)", original_message)
            if match:
                return f"空行不足（期望 {match.group(1)} 个，实际 {match.group(2)} 个）。建议添加空行。"

            # 定义后缺少空行
            match = re.search(r"expected (\d+) blank lines after class or function definition, found (\d+)",
                              original_message)
            if match:
                return f"类/函数定义后缺少空行（期望 {match.group(1)} 个，实际 {match.group(2)} 个）。建议添加空行。"

            # 空行过多
            match = re.search(r"too many blank lines \((\d+)\)", original_message)
            if match:
                return f"空行过多（{match.group(1)} 个）。建议只保留 1 个空行。"

            # 文件末尾多余空行
            if "blank line at end of file" in original_message:
                return "文件末尾存在多余空行。建议删除末尾空行。"

            # 行长度超限
            match = re.search(r"line too long \((\d+) > (\d+) characters\)", original_message)
            if match:
                return f"行长度超限（{match.group(1)} > {match.group(2)} 字符），建议拆分。"

            # 类名命名规范
            match = re.search(r"class name '([^']+)' should use CapWords convention", original_message)
            if match:
                class_name = match.group(1)
                return f"类名 '{class_name}' 应使用 CapWords 命名规范（如 MyClass）。"

            # 函数名命名规范
            match = re.search(r"function name '([^']+)' should be lowercase", original_message)
            if match:
                func_name = match.group(1)
                return f"函数名 '{func_name}' 应使用 snake_case 命名规范（如 my_function）。"

            # 参数名命名规范
            match = re.search(r"argument name '([^']+)' should be lowercase", original_message)
            if match:
                arg_name = match.group(1)
                return f"参数名 '{arg_name}' 应使用 snake_case 命名规范（如 my_param）。"

            # 变量名命名规范
            match = re.search(r"variable '([^']+)' in function should be lowercase", original_message)
            if match:
                var_name = match.group(1)
                return f"变量名 '{var_name}' 应使用 snake_case 命名规范（如 my_variable）。"

        if tool_name == ToolName.PYDOCSTYLE:
            # 公共模块缺少文档字符串
            if "Missing docstring in public module" in original_message:
                return "公共模块缺少文档字符串。建议在文件开头添加模块级文档字符串，说明模块的功能和用途。"

            # 摘要行和描述之间缺少空行
            match = re.search(r"(\d+) blank line required between summary line and description \(found (\d+)\)",
                              original_message)
            if match:
                expected = match.group(1)
                found = match.group(2)
                return f"文档字符串中摘要行和详细描述之间需要 {expected} 个空行（实际 {found} 个）。建议在摘要行后添加空行。"

            # 第一行应以句号/问号/感叹号结尾
            if "First line should end with a period, question mark, or exclamation point" in original_message:
                return "文档字符串第一行应以句号、问号或感叹号结尾。建议在第一行末尾添加合适的标点符号。"

        return original_message
