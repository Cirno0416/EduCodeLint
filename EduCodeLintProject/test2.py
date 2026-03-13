"""
and calculates the final quality score
and calculates the final quality score
"""
# 测试flake8：未使用的导入（unused-import）
import math  # 未使用此导入

# 测试pyright：变量类型不匹配（声明int却赋值str）
def type_mismatch():
    num: int = "not a number"  # pyright会检测类型错误
    return num


# 测试pylint：函数参数过多（too-many-arguments，默认阈值5）
def too_many_args(a: int, b: int, c: int, d: int, e: int, f: int) -> int:
    x = f  # 测试pylint：未使用的变量（unused-variable，x未被使用）
    return a + b
