---
order: 4
tags: [Python, 异常处理]
prerequisites: ["[[3-File Operations]]"]
next: "[[5-OOP (object-oriented programming)]]"
---

## 本章大纲

- [[#1. 异常基础]]
- [[#2. try-except]]
- [[#3. else 与 finally]]
- [[#4. 抛出与自定义异常]]
- [[#5. 异常链与传播]]
- [[#6. 常见内置异常]]
- [[#7. 调试与日志技巧]]

## 1. 异常基础

- 异常表示程序运行时出现的错误或异常状态。
- 未处理的异常会向上传播，最终可能导致程序终止。
- 异常对象通常包含类型、错误消息和堆栈信息。
- 异常处理的目标是恢复、转换提示或保证清理，不是隐藏所有错误。
- `Exception` 是大多数常规异常的基类，`BaseException` 还包含系统退出等特殊异常。

## 2. try-except

```python
try:
    number = int(input("请输入整数："))
except ValueError:
    print("输入格式不正确")
except (TypeError, OverflowError) as error:
    print(f"处理失败：{error}")
```

- `try` 放置可能抛出异常的代码。
- `except` 捕获匹配的异常类型并处理。
- `try` 和 `except` 必须同时出现，`else` 与 `finally` 可选；`else` 在实际开发中较少使用。
- 多个 `except` 按从上到下的顺序匹配，应把具体异常放在前面。
- `as error` 可以绑定异常对象。
- 应捕获预期的具体异常，避免直接使用过宽的 `except Exception`。
- 捕获后如果无法处理，应记录上下文并重新抛出，而不是静默忽略。

## 3. else 与 finally

```python
try:
    result = 10 / divisor
except ZeroDivisionError:
    print("除数不能为 0")
else:
    print(f"结果：{result}")
finally:
    print("处理结束")
```

- `else` 只在 `try` 没有发生异常时执行。
- `finally` 无论是否发生异常、是否执行 `return`，通常都会执行。
- `finally` 常用于释放文件、连接和锁等资源。
- 使用 `with` 管理资源通常比手写 `finally` 更清晰。

## 4. 抛出与自定义异常

```python
class ValidationError(ValueError):
    """输入校验失败。"""


def validate_age(age):
    if age < 0:
        raise ValidationError("年龄不能为负数")
```

- `raise` 用于主动抛出异常。
- 自定义异常通常继承 `Exception` 或更具体的异常类型。
- 异常类名应表达业务错误含义，并保持命名清晰。
- 应避免抛出过于泛化的异常，也不要用异常控制正常流程。
- 自定义异常可以携带结构化上下文，例如字段名、错误码和原始值。

## 5. 异常链与传播

```python
try:
    config = load_config(path)
except OSError as error:
    raise RuntimeError("配置加载失败") from error
```

- 当前函数不处理异常时，异常会继续向调用方传播。
- `raise ... from error` 明确保留原始异常原因。
- `raise ... from None` 可以隐藏原始上下文，但应谨慎使用。
- 追踪 `__cause__` 和 `__context__` 可以理解异常链。
- 业务边界可以把底层异常转换为更易理解的领域异常。

## 6. 常见内置异常

- `ValueError`：值类型正确但内容不合法。
- `TypeError`：对象类型或操作类型不匹配。
- `KeyError`：字典中不存在指定键。
- `IndexError`：序列索引越界。
- `FileNotFoundError`：文件或目录不存在。
- `PermissionError`：权限不足。
- `ZeroDivisionError`：除数为零。
- `AttributeError`：对象不存在指定属性。

## 7. 调试与日志技巧

- 优先阅读完整异常堆栈，从最底层错误和最后一行消息定位问题。
- `print()` 适合临时排查，但不应长期散落在业务代码中。
- `assert` 用于表达开发阶段的内部前提，不应替代完整输入校验。
- `breakpoint()` 或 `pdb` 可以进入交互式调试。
- `traceback` 模块可以格式化异常堆栈。
- `logging.exception()` 适合在记录错误时保留完整堆栈。
- 日志应包含时间、级别、模块、消息和关键上下文。
- `try-except` 不应吞掉异常；无法恢复时应重新抛出或转换为明确的业务异常。
