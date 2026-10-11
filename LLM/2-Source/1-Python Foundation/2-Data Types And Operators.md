---
order: 2
tags: [Python, 数据类型, 运算符]
prerequisites: ["[[1-Python Basic Grammer]]"]
next: "[[3-String Details]]"
---

## 本章大纲

- [[#1. 数字类型]]
- [[#2. 布尔类型]]
- [[#3. 算术与赋值运算符]]
- [[#4. 比较与逻辑运算符]]
- [[#5. 成员、身份与位运算符]]
- [[#6. 类型转换]]
- [[#7. 运算符优先级]]

## 1. 数字类型

### 整数（`int`）
整数类型可以表示任意大小的整数,这是Pyhon的一个优势

```python
# 整数类型示例
age = 25
population = 1400000000  # 14亿
small_number = -100
big_number = 999999999999999999999999999999

print(f"年龄：{age}")
print(f"人口：{population}")
print(f"大数字：{big_number}")
print(f"大数字的类型：{type(big_number)}")

```

- Python 整数精度只受可用内存限制，适合处理大整数。
- 支持十进制、二进制、八进制和十六进制字面量。
- 可使用 `_` 提升可读性，例如 `1_000_000`。

### 浮点数（`float`）
浮点数用于表示带小数点的数字, 在科学计算中经常用到

```python
# 浮点数类型示例
temperature = 36.5
pi = 3.14159
scientific_notation = 1.23e-4  # 科学计数法，等于0.000123

print(f"体温：{temperature}℃")
print(f"圆周率：{pi}")
print(f"科学计数法：{scientific_notation}")

# 浮点数的精度问题
result = 0.1 + 0.2
print(f"0.1 + 0.2 = {result}")  # 可能不是你期望的0.3
print(f"结果是否等于0.3：{result == 0.3}")

```

- 浮点数使用二进制浮点表示，部分十进制小数无法精确存储。
- 金额等精度敏感场景可使用 `decimal.Decimal`。
- `math.isclose()` 常用于浮点数近似比较。

### 复数（`complex`）
复数在数学计算中有特殊用途, 虽然日常编程中用得不多, 但了解一下也有好处

```python
# 复数类型示例
complex_num1 = 3 + 4j
complex_num2 = complex(5, 6)  # 另一种创建方式

print(f"复数1：{complex_num1}")
print(f"复数2：{complex_num2}")
print(f"复数1的实部：{complex_num1.real}")
print(f"复数1的虚部：{complex_num1.imag}")

```

- 复数包含实部和虚部，虚部以 `j` 结尾。
- 可使用 `number.real` 和 `number.imag` 读取实部和虚部。

## 2. 布尔类型

- 布尔类型只有两个值：`True` 和 `False`，首字母必须大写。
- `bool` 是 `int` 的子类，`True` 等价于 `1`，`False` 等价于 `0`。
- `bool()` 可以把其他对象转换为布尔值。
- 以下值通常视为假：`False`、`None`、`0`、`0.0`、`""`、`[]`、`()`、`{}`、`set()`。
- 非空字符串、非零数值和非空容器通常视为真。

```python
# 布尔类型的基本使用
is_student = True
is_working = False
has_license = True

print(f"是学生：{is_student}")
print(f"在工作：{is_working}")
print(f"有驾照：{has_license}")

# 布尔值的产生
age = 20
print(f"是否成年：{age >= 18}")
print(f"是否未成年：{age < 18}")

# 空值的布尔转换
empty_string = ""
empty_list = []
zero = 0

print(f"空字符串的布尔值：{bool(empty_string)}")
print(f"空列表的布尔值：{bool(empty_list)}")
print(f"零的布尔值：{bool(zero)}")

```

## 3. 算术与赋值运算符

### 算术运算符

| 运算符 | 说明 | 示例 |
|---|---|---|
| `+` | 加法 | `3 + 2` |
| `-` | 减法 | `3 - 2` |
| `*` | 乘法 | `3 * 2` |
| `/` | 真除法，结果通常为浮点数 | `5 / 2` |
| `//` | 向下取整除法 | `5 // 2` |
| `%` | 取余 | `5 % 2` |
| `**` | 幂运算 | `2 ** 3` |
```python
# 基本算术运算
a = 10
b = 3

print(f"加法：{a} + {b} = {a + b}")
print(f"减法：{a} - {b} = {a - b}")
print(f"乘法：{a} * {b} = {a * b}")
print(f"除法：{a} / {b} = {a / b}")
print(f"整除：{a} // {b} = {a // b}")
print(f"取模：{a} % {b} = {a % b}")
print(f"幂运算：{a} ** {b} = {a ** b}")

# 实际应用：计算复利
principal = 1000  # 本金
rate = 0.05      # 年利率5%
time = 3         # 3年

compound_interest = principal * (1 + rate) ** time
profit = compound_interest - principal

print(f"本金：{principal}元")
print(f"年利率：{rate * 100}%")
print(f"时间：{time}年")
print(f"复利后金额：{compound_interest:.2f}元")
print(f"利润：{profit:.2f}元")

```

- `/` 的结果是浮点数，即使能够整除。
- `//` 对负数会向下取整，例如 `-5 // 2` 的结果是 `-3`。
- `%` 可用于判断奇偶、周期性索引和限制数值范围。

### 赋值运算符

```python
# 基本赋值和复合赋值
count = 10
print(f"初始值：{count}")

count += 5  # 等同于 count = count + 5
print(f"加5后：{count}")

count -= 3  # 等同于 count = count - 3
print(f"减3后：{count}")

count *= 2  # 等同于 count = count * 2
print(f"乘2后：{count}")

count //= 4  # 等同于 count = count // 4
print(f"整除4后：{count}")

# 实际应用：累加计算
total = 0
numbers = [1, 2, 3, 4, 5]

for num in numbers:
    total += num
    print(f"加入{num}后，总和为：{total}")

print(f"最终总和：{total}")

```

- 常见复合赋值包括 `+=`、`-=`、`*=`、`/=`、`//=`、`%=`、`**=`。
- 链式赋值可以把同一个对象绑定到多个变量。
- 海象运算符 `:=` 可以在表达式内部为变量赋值。

## 4. 比较与逻辑运算符

### 比较运算符

- `==` 判断值是否相等，`!=` 判断是否不相等。
- `>`、`<`、`>=`、`<=` 用于比较大小。
- 比较运算返回布尔值。
- Python 支持链式比较，例如 `0 <= score <= 100`。

```python
# 比较运算符示例
x = 10
y = 5

print(f"{x} > {y}: {x > y}")
print(f"{x} < {y}: {x < y}")
print(f"{x} >= {y}: {x >= y}")
print(f"{x} <= {y}: {x <= y}")
print(f"{x} == {y}: {x == y}")
print(f"{x} != {y}: {x != y}")

# 字符串比较
name1 = "Alice"
name2 = "Bob"
print(f"字符串比较：{name1} < {name2} = {name1 < name2}")  # 按字典序比较

# 实际应用：成绩评级
score = 85
if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
elif score >= 60:
    grade = "D"
else:
    grade = "F"

print(f"成绩：{score}分，等级：{grade}")

```
### 逻辑运算符

- `and`：两个条件都为真时结果才为真。
- `or`：至少一个条件为真时结果就为真。
- `not`：对布尔结果取反。
- `and` 和 `or` 具有短路特性，可能返回参与运算的原对象，而不一定是 `True` 或 `False`。

```python
# 逻辑运算符示例
age = 25
has_job = True
has_car = False

# and运算符：所有条件都为True时结果才为True
can_rent_car = age >= 21 and has_job
print(f"可以租车：{can_rent_car}")

# or运算符：任意一个条件为True时结果就为True
can_travel = has_car or age >= 18
print(f"可以旅行：{can_travel}")

# not运算符：取反
is_minor = not (age >= 18)
print(f"是未成年人：{is_minor}")

# 复杂逻辑判断
username = "admin"
password = "123456"
is_admin = username == "admin" and password == "123456"
print(f"是管理员：{is_admin}")

```

## 5. 成员、身份与位运算符

### 成员运算符

- `in` 判断元素是否存在于字符串、列表、元组、集合或字典键中。
- `not in` 判断元素是否不存在。

### 身份运算符

- `is` 判断两个变量是否引用同一个对象。
- `is not` 判断两个变量是否引用不同对象。
- 判断值相等使用 `==`，判断是否为 `None` 通常使用 `is None`。

```python
# 成员运算符
fruits = ["apple", "banana", "orange"]
print(f"apple在列表中：{'apple' in fruits}")
print(f"grape不在列表中：{'grape' not in fruits}")

# 字符串中的成员运算
text = "Hello, Python!"
print(f"Python在字符串中：{'Python' in text}")

# 身份运算符
list1 = [1, 2, 3]
list2 = [1, 2, 3]
list3 = list1

print(f"list1 is list2: {list1 is list2}")  # False，不同对象
print(f"list1 is list3: {list1 is list3}")  # True，同一对象
print(f"list1 == list2: {list1 == list2}")  # True，内容相同

# 小整数对象的特殊情况
x = 100
y = 100
print(f"x is y: {x is y}")  # True，小整数有缓存

```
### 位运算符

| 运算符 | 说明 |
|---|---|
| `&` | 按位与 |
| `|` | 按位或 |
| `^` | 按位异或 |
| `~` | 按位取反 |
| `<<` | 左移 |
| `>>` | 右移 |

- 位运算直接操作整数的二进制位，常用于权限标记和底层数据操作。

## 6. 类型转换

```python
int("10")
float("3.14")
str(100)
bool(0)
```

- `int()` 把可解析的字符串或数值转换为整数。
- `float()` 把整数或可解析字符串转换为浮点数。
- `str()` 把对象转换为字符串。
- `bool()` 根据对象的真值规则进行转换。
- 不合法格式会触发 `ValueError`，例如 `int("abc")`。
- `int(3.9)` 直接截断小数部分，不会四舍五入。

## 7. 运算符优先级

- 常见优先级从高到低大致为：括号、幂、正负号、乘除、加减、移位、位运算、比较、身份与成员、逻辑运算、赋值。
- 使用括号可以明确计算顺序，并减少阅读歧义。
- 复杂表达式应拆成多个中间变量，不要只依赖优先级记忆。

```python
result = (base + bonus) * rate
```
