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


# 测试pylint：类实例属性过多（默认阈值10）和方法过多（默认阈值20）
class OverloadedClass:
    def __init__(self):
        self.attr1 = 1
        self.attr2 = 2
        self.attr3 = 3
        self.attr4 = 4
        self.attr5 = 5
        self.attr6 = 6
        self.attr7 = 7
        self.attr8 = 8
        self.attr9 = 9
        self.attr10 = 10
        self.attr11 = 11  # 第11个属性，触发pylint检测

    def method1(self): pass
    def method2(self): pass
    def method3(self): pass
    def method4(self): pass
    def method5(self): pass
    def method6(self): pass
    def method7(self): pass
    def method8(self): pass
    def method9(self): pass
    def method10(self): pass
    def method11(self): pass
    def method12(self): pass
    def method13(self): pass
    def method14(self): pass
    def method15(self): pass
    def method16(self): pass
    def method17(self): pass
    def method18(self): pass
    def method19(self): pass
    def method20(self): pass
    def method21(self): pass  # 第21个方法，触发pylint检测

    def big_method(self, x: int):
        if x == 1:
            return "1"
        elif x == 2:
            return "2"
        elif x == 3:
            return "3"
        elif x == 4:
            return "4"
        elif x == 5:
            return "5"
        elif x == 6:
            return "6"
        elif x == 7:
            return "7"
        elif x == 8:
            return "8"
        elif x == 9:
            return "9"
        elif x == 10:
            return "10"
        else:
            return "other"  # 13个分支，圈复杂度>10，触发radon检测


# 测试pylint：嵌套深度过高（默认阈值4）
def deep_nesting():
    if True:
        if True:
            if True:
                if True:
                    if True:  # 第5层嵌套，触发检测
                        pass


# 测试pylint：分支过多（默认阈值12）+ radon：高圈复杂度
def high_complexity(x: int) -> str:
    if x == 1:
        return "1"
    elif x == 2:
        return "2"
    elif x == 3:
        return "3"
    elif x == 4:
        return "4"
    elif x == 5:
        return "5"
    elif x == 6:
        return "6"
    elif x == 7:
        return "7"
    elif x == 8:
        return "8"
    elif x == 9:
        return "9"
    elif x == 10:
        return "10"
    else:
        return "other"  # 13个分支，圈复杂度>10，触发radon检测


# 测试flake8：行过长（默认阈值79字符，此行故意超长）
long_line = "这是一行故意写得非常长的文本，用来测试flake8的line-too-long规则，确保长度超过默认的79个字符限制，触发检测触发检测触发检测触发检测触发检测触发检测"


# 测试bandit：危险函数exec（B307）
def dangerous_exec():
    code = "print('恶意代码')"
    exec(code)  # 触发bandit的B307


# 测试bandit：忽略异常未处理（B110）
def unhandled_exception():
    try:
        x = 1 / 0
    except:
        pass  # 仅捕获异常未处理，触发B110


def unhandled_exception2():
    try:
        x = 1 / 0
    except Exception:
        pass  # 仅捕获异常未处理，触发B110


# 测试bandit：硬编码敏感信息（B501）
def hardcoded_secret():
    password = "my_secret_password_123"  # 硬编码密码，触发B501
    return password


# 测试pyright：访问未定义变量
def undefined_variable():
    return undefined_var  # pyright检测到undefined_var未定义


# 测试pyright：函数返回值类型不匹配（注解返回int却返回str）
def wrong_return_type() -> int:
    return "should be int"  # 返回值类型错误

