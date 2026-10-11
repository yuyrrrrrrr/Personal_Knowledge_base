---
order: 4
tags: [Python, 数据结构]
prerequisites: ["[[3-String Details]]"]
next: "[[5-Process Control]]"
---

## 本章大纲

- [[#1. 容器概述]]
- [[#2. 列表与元组（Lists and Tuples）]]
- [[#3. 列表与元组操作]]
- [[#4. 字典与集合（Dictionary and Set）]]
- [[#5. 通用操作、遍历与解包]]
- [[#6. 推导式]]

## 1. 容器概述

- 容器用于把多个元素组织为一个整体。
- 常见容器包括字符串、列表、元组、字典和集合。
- 序列类型有字符串、列表和元组，支持索引、切片和顺序遍历。
- 映射类型以键值对保存数据，代表是字典。
- 集合类型用于保存不重复元素，适合去重和集合运算。

### 可变与不可变

- 列表和字典是可变对象，可以在原对象上增删改。
- 元组、字符串和数值是不可变对象，修改时会生成新对象。
- 可变对象作为函数参数传入后，原地修改会影响函数外部看到的对象。

## 2. 列表与元组（Lists and Tuples）

列表是Python 中最灵活的数据结构之一, 它能够存储任意类型的数据, 并且可以动态地添加, 删除和修改元素. 创建列表最直接的方法是使用方括号将元素包围起来.
### 列表创建

```python
empty = []
numbers = [1, 2, 3]
mixed = [1, "Python", True, None]
nested = [[1, 2], [3, 4]]
from_range = list(range(5))
```

- 列表使用方括号，元素可以重复，顺序固定。
- 列表元素可以是不同类型，也可以嵌套其他容器。
- 列表可变，适合需要频繁增删改的数据集合。

列表的一个重要特性是元素的有序性和可重复性. 这一维者列表中的每个元素都有一个固定的位置, 并且可以存储重复的值:
```python
# 支持的视频格式
video_formats = ["mp4", "avi", "mov", "mp4", "mkv"]  # mp4 重复出现
print(f"支持的格式: {video_formats}")
print(f"总共支持: {len(video_formats)} 种格式")

# 面试鸭小程序的版本历史
resume_versions = ["v1.0", "v1.1", "v1.2", "v1.3", "v1.4"]
print(f"最新版本: {resume_versions[-1]}")
print(f"初始版本: {resume_versions[0]}")

```
输出结果:
```
支持的格式: ['mp4', 'avi', 'mov', 'mp4', 'mkv']
总共支持: 5 种格式
最新版本: v1.4
初始版本: v1.0
```
### 元组创建

```python
empty = ()
point = (10, 20)
single = (1,)
from_list = tuple([1, 2, 3])
```

- 元组使用圆括号，单个元素后必须保留逗号。
- 元组有序、可重复，但创建后不能修改元素引用。
- 元组常用于表示不可变记录，例如坐标、配置项和固定结构。
- 元组中可以包含可变对象，此时该对象本身仍可被修改。

## 3. 列表与元组操作

### 查询与访问

- `len(container)`：获取元素数量。
- `container[index]`：按索引访问。
- `container[start:end:step]`：切片并返回新的序列。
- `element in container`：判断元素是否存在。
- `container.count(value)`：统计出现次数。
- `container.index(value)`：返回首次出现位置，找不到会报错。

### 列表新增

- `append(value)`：在末尾追加一个元素。
- `insert(index, value)`：在指定位置插入元素。
- `extend(iterable)`：把可迭代对象中的元素逐个追加。

### 列表删除

- `del items[index]`：按下标删除。
- `pop(index)`：按下标删除并返回元素，省略下标时删除最后一个。
- `remove(value)`：删除第一个匹配值，找不到会报错。
- `clear()`：清空列表。

### 列表修改与排序

```python
items = [3, 1, 2]
items[0] = 10
items.sort()
items.reverse()
```

- 通过索引可以替换已有元素。
- `sort()` 原地排序，`sorted()` 返回新列表。
- `reverse()` 原地反转元素顺序。
- `copy()` 返回浅拷贝，嵌套对象仍可能共享引用。

### 元组操作

- 元组支持索引、切片、遍历、`count()` 和 `index()`。
- `+` 可以拼接元组，`*` 可以重复元组。
- 元组不可变，因此没有 `append()`、`remove()` 等原地修改方法。

## 4. 字典与集合（Dictionary and Set）

### 字典创建与访问

```python
user = {"name": "Alice", "age": 18}
print(user["name"])
print(user.get("email"))
```

- 字典使用 `{key: value}` 保存键值对。
- 键必须唯一并且可哈希，常用字符串、数字和元组作为键。
- `dict[key]` 在键不存在时触发 `KeyError`。
- `get(key, default)` 在键不存在时返回默认值。

### 字典新增、修改与删除

```python
user["email"] = "alice@example.com"
user["age"] = 19
del user["email"]
```

- `dict[key] = value` 在键不存在时新增，存在时修改。
- `update(other)` 批量更新键值对。
- `setdefault(key, default)` 在键不存在时设置默认值。
- `pop(key, default)` 删除并返回对应值。
- `clear()` 清空字典。

### 字典常用查询

- `keys()`：返回所有键的视图。
- `values()`：返回所有值的视图。
- `items()`：返回键值对视图，适合循环解包。
- `key in dict`：判断键是否存在。
- `len(dict)`：返回键值对数量。
- Python 3.7 起字典保证按插入顺序遍历。

### 集合创建与修改

```python
empty = set()
numbers = {1, 2, 3}
unique = set([1, 2, 2, 3])
```

- 集合使用 `{}` 创建，但空集合必须写为 `set()`，因为 `{}` 是空字典。
- 集合元素不重复、无序且必须可哈希。
- `add(value)` 添加单个元素。
- `update(iterable)` 批量添加元素。
- `remove(value)` 删除元素，不存在会报错。
- `discard(value)` 删除元素，不存在不会报错。
- `pop()` 删除并返回任意元素，`clear()` 清空集合。

### 集合运算

- `a | b` 或 `union()`：并集。
- `a & b` 或 `intersection()`：交集。
- `a - b` 或 `difference()`：差集。
- `a ^ b` 或 `symmetric_difference()`：对称差集。
- 集合适合去重、成员判断和集合关系计算。

## 5. 通用操作、遍历与解包

- `len()`、`in`、`max()`、`min()`、`sum()` 等内置函数可处理多种容器。
- `for item in container` 直接遍历元素。
- `enumerate(container)` 同时获得索引和值。
- `zip(a, b)` 并行遍历多个可迭代对象。
- `a, b = pair` 可以解包列表或元组。
- `first, *rest = items` 可以收集剩余元素。
- 嵌套容器操作时要关注浅拷贝和共享引用问题。

```python
for index, value in enumerate(["a", "b"]):
    print(index, value)
```

## 6. 推导式

```python
squares = [x * x for x in range(5)]
evens = [x for x in range(10) if x % 2 == 0]
lengths = {word: len(word) for word in ["a", "bb"]}
unique_lengths = {len(word) for word in ["a", "bb", "cc"]}
```

- 列表推导式：`[表达式 for 元素 in 可迭代对象 if 条件]`。
- 字典推导式：`{键表达式: 值表达式 for ...}`。
- 集合推导式：`{表达式 for ...}`。
- 推导式适合简单转换和过滤，复杂逻辑应改写为普通循环。
- 圆括号中的推导式创建的是生成器表达式，不是元组推导式。

