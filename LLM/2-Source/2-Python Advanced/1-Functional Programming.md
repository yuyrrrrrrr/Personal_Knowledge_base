---
order: 1
tags: [Python, 函数编程]
next: "[[2-Modules and Packages]]"
---

## 本章大纲

- [[#1. 函数定义与调用]]
- [[#2. 参数传递]]
- [[#3. 作用域与闭包]]
- [[#4. 返回值与函数对象]]
- [[#5. lambda 表达式]]
- [[#6. 装饰器]]
- [[#7. 常用函数式工具]]

## 1. 函数定义与调用

```python
def greet(name):
    """返回问候语。"""
    return f"Hello, {name}!"

message = greet("Alice")
```

- `def` 用于定义函数，函数体通过缩进划分。
- 调用函数时传入实参，函数执行完成后可以通过 `return` 返回结果。
- 没有显式 `return` 时，函数默认返回 `None`。
- 文档字符串应说明函数用途、参数、返回值和可能抛出的异常。
- 函数应尽量保持职责单一，便于测试和复用。

### 函数类型

| 类型 | 说明 |
|---|---|
| 无参无返 | 基本不用 |
| 无参有返 | 返回由函数内部计算或获取的结果 |
| 有参无返 | 仅执行操作，默认返回 `None` |
| 有参有返 | 最常见，接收输入并返回结果 |

## 2. 参数传递

### 常见参数形式

```python
def create_user(name, age=18, *hobbies, city="上海", **extra):
    return name, age, hobbies, city, extra
```

- 位置参数按调用顺序绑定。
- 关键字参数通过 `参数名=值` 绑定，提高可读性。
- 默认参数必须在非默认参数之后。
- `*args` 把多余的位置参数收集为元组。
- `**kwargs` 把多余的关键字参数收集为字典。
- `*` 后的参数只能使用关键字传递，`/` 前的参数只能使用位置传递。

### 参数规则与陷阱

- 位置参数必须写在关键字参数之前。
- 可变对象不适合作为默认参数，因为默认值只在函数定义时创建一次。
- 需要可变默认值时，通常使用 `None` 并在函数体内部创建新对象。
- 传入可变对象后，函数内部的原地修改会影响调用方。

```python
def append_item(item, target=None):
    if target is None:
        target = []
    target.append(item)
    return target
```

## 3. 作用域与闭包

- Python 变量查找遵循 `LEGB` 顺序：局部、外层函数、全局、内置。
- 函数内部读取全局变量通常不需要声明，重新绑定全局变量需要 `global`。
- 修改外层函数变量需要 `nonlocal`。
- 闭包是内部函数引用外层函数变量的结构。
- 闭包可以保存状态，但复杂状态通常更适合使用类。

```python
def counter():
    count = 0

    def increase():
        nonlocal count
        count += 1
        return count

    return increase
```

## 4. 返回值与函数对象

- `return` 可以返回单个值、多个值、容器或函数。
- 多个返回值实际会打包成元组。
- 函数是一等对象，可以赋值给变量、作为参数传递或作为返回值。
- 高阶函数可以接收函数作为参数，或者返回一个函数。
- 纯函数只依赖输入并返回结果，副作用更少，更容易测试。

```python
def apply_twice(func, value):
    return func(func(value))
```

### 嵌套与递归

- 函数嵌套是指在一个函数内部定义或调用另一个函数。
- 递归是函数直接或间接调用自身。
- 递归必须提供终止条件，并逐步接近终止条件，否则会触发 `RecursionError`。
- 递归适合树结构、分治等天然递归问题；简单循环问题优先使用迭代。

## 5. lambda 表达式

```python
square = lambda x: x * x
sorted_users = sorted(users, key=lambda user: user["age"])
```

- `lambda` 用于创建简单的匿名函数。
- 语法为 `lambda 参数: 表达式`，表达式结果就是返回值。
- 不支持多条语句、复杂分支和文档字符串。
- 适合短小的回调或排序键，复杂逻辑应使用 `def`。

## 6. 装饰器

### 基本装饰器

```python
from functools import wraps

def log_calls(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"调用 {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@log_calls
def add(a, b):
    return a + b
```

- 装饰器本质上是接收函数并返回新函数的高阶函数。
- `@decorator` 等价于把原函数传给装饰器并重新绑定名称。
- `*args` 和 `**kwargs` 让装饰器适配不同参数形式。
- `functools.wraps` 保留原函数的名称、文档字符串和元数据。
- 多个装饰器按从下到上的顺序应用。

### 带参数的装饰器

```python
def repeat(times):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = None
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator
```

- 带参数的装饰器需要多一层函数：接收配置、接收原函数、包装调用。
- 装饰器适合日志、计时、缓存、权限校验和重试。
- 不建议用装饰器隐藏过多核心业务逻辑。

## 7. 常用函数式工具

- `map(func, iterable)`：对每个元素应用函数。
- `filter(func, iterable)`：保留条件为真的元素。
- `functools.reduce(func, iterable)`：把序列逐步归约为一个结果。
- `functools.partial(func, ...)`：预先绑定部分参数。
- 推导式通常比 `map` 和 `filter` 更直观。
- 函数式写法应服务于可读性，不应为了风格刻意使用。
