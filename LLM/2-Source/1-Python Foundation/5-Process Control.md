---
order: 5
tags: [Python, 流程控制]
prerequisites: ["[[4-Data Container]]"]
---

## 本章大纲

- [[#1. 条件语句]]
- [[#2. 条件表达式]]
- [[#3. while 循环]]
- [[#4. for 循环与 range]]
- [[#5. 循环控制语句]]
- [[#6. 循环嵌套与常见模式]]

## 1. 条件语句

### `if` 语句

```python
score = 85

if score >= 90:
    print("优秀")
elif score >= 60:
    print("及格")
else:
    print("不及格")
```

当需要处理多种情况时, elif和else语句就派上用场了. 它们让程序能够处理复杂的逻辑分支:
```python
# 老鱼简历系统的用户等级判断
def check_user_level(experience_years):
    if experience_years >= 5:
        return "高级开发者"
    elif experience_years >= 3:
        return "中级开发者"
    elif experience_years >= 1:
        return "初级开发者"
    else:
        return "实习生"

# 测试不同经验年限
candidates = [0.5, 2, 4, 6]
for years in candidates:
    level = check_user_level(years)
    print(f"工作经验 {years} 年，等级：{level}")
```
输出结果:
```
工作经验 0.5 年，等级：实习生
工作经验 2 年，等级：初级开发者
工作经验 4 年，等级：中级开发者
工作经验 6 年，等级：高级开发者
```

- `if` 根据条件表达式的结果决定是否执行代码块。
- 条件为真时执行 `if` 分支，否则继续检查 `elif`。
- `elif` 可以有多个，`else` 最多一个，并且必须放在最后。
- `if`、`elif`、`else` 是互斥分支，一次只会执行一个代码块。
- Python 使用缩进表示代码块，通常缩进 4 个空格。

### 条件与真值

- 比较运算符、逻辑运算符和成员运算符常用来构造条件。
- `and`、`or` 具有短路特性。
- 非布尔对象可以直接参与判断，例如空容器和 `0` 视为假。
- 条件复杂时应拆成命名清晰的中间变量。

### 嵌套条件

```python
if is_login:
    if is_admin:
        print("管理员")
    else:
        print("普通用户")
```

- 条件分支内部可以继续嵌套条件语句。
- 嵌套层次过深会降低可读性，可考虑使用提前返回或拆分函数。

## 2. 条件表达式(三元运算符)

```python
status = "成年" if age >= 18 else "未成年"
```

- 条件表达式格式为 `满足时的值 if 条件 else 不满足时的值`。
- 条件表达式可以让简单的条件判断更加简洁
- 条件表达式适合简单二选一赋值。
- 不应把复杂分支塞入单行表达式，以免降低可读性。

## 3. while 循环

```python
count = 1
while count <= 5:
    print(count)
    count += 1
```

- `while` 在条件为真时反复执行循环体。
- 循环体内必须修改能让条件最终变为假的变量，否则可能形成死循环。
- `while True:` 可用于主动控制退出时机的循环，但必须提供明确的 `break` 条件。

### `while ... else`

```python
index = 0
while index < 3:
    index += 1
else:
    print("循环正常结束")
```

- `while` 循环正常结束后会执行 `else`。
- 如果循环被 `break` 提前结束，则不会执行 `else`。

## 4. for 循环与 range

### `for` 循环

```python
for char in "Python":
    print(char)

for item in [10, 20, 30]:
    print(item)
```

- `for` 循环用于依次遍历可迭代对象。
- 字符串、列表、元组、字典、集合和 `range` 都可用于遍历。
- 遍历字典时默认得到键，也可遍历 `items()` 获取键值对。

### `range()`

```python
range(5)
range(2, 8)
range(10, 0, -2)
```

- `range(start, stop, step)` 生成整数序列。
- 起始值包含，结束值不包含。
- 步长可以为正数或负数，但不能为 `0`。
- `range` 具有惰性特点，适合表示大范围整数序列。

### `for ... else`

```python
for item in [1, 2, 3]:
    if item == 2:
        print("找到")
        break
else:
    print("未找到")
```

- `for` 循环正常结束后执行 `else`。
- 被 `break` 提前终止时不会执行 `else`。

## 5. 循环控制语句

### `break`

- 立即结束当前所在的整个循环。
- 常用于搜索到目标后提前退出。
- 只影响 `break` 所在的最近一层循环。

### `continue`

- 跳过本次循环剩余代码，直接进入下一次迭代。
- 常用于过滤不需要处理的数据。
- 只影响 `continue` 所在的最近一层循环。

### `pass`

```python
if condition:
    pass
```

- `pass` 是空语句，执行时什么也不做。
- 用于暂时占位，保证语法结构完整。
- 不要把 `pass` 当作隐藏错误的永久方案。

## 6. 循环嵌套与常见模式

### 循环嵌套

```python
for row in range(1, 4):
    for column in range(1, 4):
        print(row * column, end=" ")
    print()
```

- 外层循环每执行一次，内层循环会完整执行一轮。
- `break` 和 `continue` 默认只控制当前层循环。
- 需要一次退出多层循环时，可封装为函数并使用 `return`，或增加退出标志。

### 常见模式

- 累加模式：初始化结果变量，在循环中不断更新。
- 计数模式：满足条件时递增计数器。
- 最值模式：记录当前最大值或最小值并逐个比较。
- 搜索模式：找到目标后使用 `break` 提前结束。
- 菜单模式：使用 `while True` 持续接收操作，直到用户选择退出。

```python
total = 0
for number in range(1, 101):
    total += number

print(total)
```
