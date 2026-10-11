---
order: 5
tags: [Python, 面向对象]
prerequisites: ["[[4-Exception Handing]]"]
next: "[[6-Advanced Features]]"
---

## 本章大纲

- [[#1. 类与对象]]
- [[#2. 属性与方法]]
- [[#3. 封装]]
- [[#4. 继承]]
- [[#5. 多态与鸭子类型]]
- [[#6. 特殊方法]]
- [[#7. 类方法、静态方法与属性]]

## 1. 类与对象

```python
class User:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def introduce(self):
        return f"我是 {self.name}"

user = User("Alice", 18)
```

- 类定义一类对象的属性结构和行为，对象是类的具体实例。
- `__init__()` 在创建对象时初始化实例属性。
- `self` 表示当前实例，必须是实例方法的第一个参数。
- 同类对象共享方法定义，但各自拥有独立的实例属性。
- 面向对象适合表达具有状态和行为的领域对象。

## 2. 属性与方法

- 实例属性通过 `self.attribute` 定义和访问。
- 类属性由所有实例共享，适合保存公共配置或计数器。
- 实例方法可以读取和修改实例状态。
- 属性名和对象内部变量应保持清晰，避免把无关数据堆进同一个类。
- 组合是在类中持有其他对象；当“拥有关系”更自然时，优先使用组合而不是继承。

## 3. 封装

```python
class BankAccount:
    def __init__(self, balance=0):
        self._balance = balance

    @property
    def balance(self):
        return self._balance

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("金额必须为正数")
        self._balance += amount
```

- 封装用于隐藏内部实现，只暴露稳定的操作接口。
- 单下划线 `_name` 表示内部使用约定，仍然可以被访问。
- 双下划线 `__name` 会触发名称改写，用于减少子类意外覆盖。
- `@property` 把方法包装为可读属性，可以在不改变调用形式的情况下增加校验。
- `@setter` 可以控制属性赋值逻辑。
- 不应为了“绝对私有”滥用双下划线，Python 更依赖约定和清晰边界。

## 4. 继承

```python
class Animal:
    def speak(self):
        raise NotImplementedError


class Dog(Animal):
    def speak(self):
        return "汪汪"
```

- 子类继承父类的属性和方法，可以扩展或重写行为。
- `super()` 用于调用父类实现，常见于 `__init__()` 初始化。
- 子类应满足父类的接口约定，避免破坏可替换性。
- 多重继承按 `MRO` 查找方法，可用 `Class.mro()` 查看顺序。
- 继承表达“是一个”的关系；共享代码但无类型关系时，组合通常更合适。
- 过深的继承层级会增加理解成本，应保持层次简单。

## 5. 多态与鸭子类型

- 多态允许不同对象对同一操作作出不同响应。
- 子类可以重写父类方法，让调用方无须判断具体类型。
- Python 鸭子类型强调对象是否具备所需行为，而不是严格继承自某个类。
- 只要对象支持相同方法，就可能用于同一调用位置。
- `isinstance()` 适合必要的类型判断，但不应把所有多态都改写成条件分支。
- 抽象基类 `abc.ABC` 可以定义统一接口，但简单项目可优先使用约定。

```python
def make_sound(animal):
    return animal.speak()
```

## 6. 特殊方法

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Point({self.x}, {self.y})"

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)
```

- `__repr__()` 面向开发者，尽可能返回可重建对象的字符串。
- `__str__()` 面向用户展示，缺失时通常回退到 `__repr__()`。
- `__len__()`、`__getitem__()`、`__iter__()` 让对象支持容器协议。
- `__eq__()`、`__hash__()` 控制相等性和哈希行为。
- `__enter__()`、`__exit__()` 支持 `with` 上下文管理。
- 特殊方法应遵循 Python 数据模型语义，不要随意创造不一致行为。

## 7. 类方法、静态方法与属性

```python
class User:
    species = "human"

    def __init__(self, name):
        self.name = name

    @classmethod
    def from_dict(cls, data):
        return cls(data["name"])

    @staticmethod
    def is_valid_name(name):
        return bool(name.strip())
```

- 实例方法接收 `self`，用于操作具体对象。
- `@classmethod` 接收 `cls`，常用于替代构造器和操作类状态。
- `@staticmethod` 不接收 `self` 或 `cls`，适合与类概念相关但不依赖实例状态的工具函数。
- `@property` 可以把计算逻辑封装为属性访问。
- 方法选择应取决于是否需要实例或类上下文，而不是随意添加装饰器。
