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

    @staticmethod
    def to_lower(text):
        """从未被调用"""

        def helper_function(x):
            """这个嵌套函数从未被调用"""
            return x * 2

        return text.lower()

    def method1(self):
        pass

    def method2(self):
        pass

    def method3(self):
        pass

    def method4(self):
        pass

    def method5(self):
        pass

    def method6(self):
        pass

    def method7(self):
        pass

    def method8(self):
        pass

    def method9(self):
        pass

    def method10(self):
        pass

    def method11(self):
        pass

    def method12(self):
        pass

    def method13(self):
        pass

    def method14(self):
        pass

    def method15(self):
        pass

    def method16(self):
        pass

    def method17(self):
        pass

    def method18(self):
        pass

    def method19(self):
        pass

    def method20(self):
        pass

    def method21(self):
        pass  # 第21个方法，触发pylint检测

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
    def test():
        pass
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

    def test():
        pass


# 测试bandit：危险函数exec（B307）
def dangerous_exec():
    code = "print('恶意代码')"
    exec(code)  # 触发bandit的B102
    eval(code)


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
    password = "my_secret'_password_123"  # 硬编码密码，触发B501
    return password


# 测试pyright：访问未定义变量
def undefined_variable():
    return undefined_var  # pyright检测到undefined_var未定义


# 测试pyright：函数返回值类型不匹配（注解返回int却返回str）
def wrong_return_type() -> int:
    return "should be int"  # 返回值类型错误


def add(a, b):
    return a + b


def sum_values(x, y):
    return x + y


def long_func():
    print("1")
    print("1")
    print("1")
    print("1")
    print("1")
    print("1")
    print("1")
    print("1")
    print("1")
    print("1")
    print("1")
    print("1")
    print("1")
    print("1")
    print("1")
    print("1")
    print("1")
    print("1")
    print("1")
    print("1")
    print("1")
    print("1")
    print("1")
    print("1")
    print("1")
    print("1")
    print("1")
    print("1")
    print("1")
    print("1")
    print("1")
    print("1")
    print("1")
    print("1")
    print("1")
    print("1")
    print("1")
    print("1")
    print("1")
    print("1")
    print("1")
    print("1")
    print("1")
    print("1")
    print("1")
    print("1")
    print("1")
    print("1")
    print("1")
    print("1")
    print("1")
    print("1")
    print("1")
    print("1")
    print("1")
    print("1")
    print("1")
    print("1")
    print("1")
    print("1")


def inconsistent_return_statements_func(x):
    if x == 1:
        return 1
    else:
        a = x
        print(a)


def used_before_assignment_func():
    print(a)  # 使用了 a，但还没赋值
    a = 10


# ==================== E201: 左括号后多余空格 ====================
def test_e201(  ):
    pass


result = (  1 + 2)


# ==================== E202: 右括号前多余空格 ====================
def test_e202() :
    # 正确写法: def test_e202():
    dict = { }
    pass


numbers = [ 1, 2, 3 ]
# 正确写法: numbers = [1, 2, 3]


# ==================== E225: 运算符缺少空格 ====================
a = 1+2
# 正确写法: a = 1 + 2

b = 3-4
# 正确写法: b = 3 - 4

c = 5*6
# 正确写法: c = 5 * 6

d = 10/2
# 正确写法: d = 10 / 2

e = 2**3
# 正确写法: e = 2 ** 3

f = 10%3
# 正确写法: f = 10 % 3

g = 5==5
# 正确写法: g = 5 == 5


# ==================== E231: 缺少逗号后空格 ====================
items = [1,2,3]
# 正确写法: items = [1, 2, 3]

def test(a,b,c):
    # 正确写法: def test(a, b, c):
    pass

person = {"name":"Alice","age":30}
# 正确写法: person = {"name": "Alice", "age": 30}


# ==================== E301: 缺少空行 ====================
def function1():
    pass
def function2():
    # 两个函数之间缺少空行
    pass
# 正确写法: 在 function1 和 function2 之间加一个空行


# ==================== E302: 函数/类前空行不足 ====================
def function_a():
    pass


class MyClass:
    # 类前面缺少两个空行（模块级类需要2个空行）
    pass


# 正确写法: class 前面加两个空行


# ==================== E303: 空行过多 ====================
def function_b():
    pass



def function_c():
    # function_b 和 function_c 之间空行过多
    pass

# 正确写法: 两个函数之间只留一个空行


# ==================== E305: 定义后缺少空行 ====================
class MyClass2:
    pass
# 类定义后面没有空行
def function_d():
    pass

# 正确写法: 类定义后面加一个空行


# ==================== E501: 行长度超过 79 字符 ====================
def test_e501():
    # 这一行太长了，超过了 79 个字符的限制，应该拆分成多行或者调整代码结构，使每行不超过规定的最大长度
    long_variable_name = "这行非常长这行非常长这行非常长这行非常长这行非常长这行非常长这行非常长这行非常长这行非常长这行非常长这行非常长这行非常长这行非常长这行非常长这行非常长这行非常长这行非常长这行非常长这行非常长这行非常长"
    return long_variable_name


# ==================== N801: 类名不是 CamelCase ====================
class my_class:  # 错误：类名应该是 CamelCase
    pass


class myclass:  # 错误：类名应该是 CamelCase
    pass


class My_Class:  # 错误：类名应该使用 CamelCase，不要用下划线
    pass


# ==================== N802: 函数名不是 snake_case ====================
def MyFunction():  # 错误：函数名应该是 snake_case
    pass


def myFunction():  # 错误：函数名应该是 snake_case
    pass


# ==================== N803: 参数名不是 snake_case ====================
def test_function(ParamName):  # 错误：参数名应该是 snake_case
    pass


def test_function(myParam):  # 错误：参数名应该是 snake_case
    pass


def test_function(my_param):  # 正确：参数名是 snake_case
    pass


# ==================== N806: 变量名不是 snake_case ====================
def test():
    MyVariable = 10  # 错误：变量名应该是 snake_case
    myVariable = 20  # 错误：变量名应该是 snake_case
    my_variable = 30  # 正确：变量名是 snake_case
    return my_variable


# ==================== N812: 常量名非全大写 ====================
MAX_SIZE = 100  # 正确：常量名全大写

max_size = 100  # 错误：常量名应该是全大写
MaxSize = 100  # 错误：常量名应该是全大写


def test():
    MY_CONSTANT = 100  # 正确：函数内的常量也要全大写
    my_constant = 100  # 错误：常量名应该是全大写


# ==================== W391: 文件末尾存在多余空行 ====================
# 文件末尾不应该有多余的空行，这里模拟了在文件末尾添加一个空行的情况
def test_function():
    pass









