---
order: 3
tags: [Python, 字符串]
prerequisites: ["[[2-Data Types And Operators]]"]
next: "[[4-Data Container]]"
---

## 本章大纲

- [[#1. 字符串创建与转义]]
- [[#2. 索引、切片与遍历]]
- [[#3. 常用字符串操作]]
- [[#4. 字符串格式化]]
- [[#5. 正则表达式基础]]

## 1. 字符串创建与转义

```python
single = 'Python'
double = "Python"
multi_line = """第一行
多行字符串
第二行key包含换行"""
raw = r"C:\Users\name"
```

- 单引号和双引号创建的字符串等价。
- 三引号可以创建跨行字符串，也常用于文档字符串。
- 原始字符串以 `r` 开头，反斜杠不再作为普通转义符处理。
- 相邻字符串字面量会隐式拼接，但变量之间必须使用 `+` 或 f-string。

### 常见转义字符

| 写法 | 含义 |
|---|---|
| `\n` | 换行 |
| `\t` | 制表符 |
| `\\` | 反斜杠 |
| `\'` | 单引号 |
| `\"` | 双引号 |

## 2. 索引、切片与遍历

### 索引

```python
text = "Python"
print(text[0])
print(text[-1])
```

- Python 索引从 `0` 开始。
- 负索引从字符串末尾向前计数，`-1` 表示最后一个字符。
- 索引越界会触发 `IndexError`。

### 切片

```python
text = "Python"
print(text[1:4])
print(text[:3])
print(text[::2])
print(text[::-1])
```

- 切片格式为 `字符串[起始:结束:步长]`。
- 起始位置包含，结束位置不包含。
- 省略起始值表示从开头开始，省略结束值表示到末尾结束。
- 步长为负数时可以从右向左取字符。

### 遍历

```python
for char in "Python":
    print(char)
```

- 字符串是可迭代对象，可以直接使用 `for` 循环。
- 字符串不可变，不能通过索引直接修改其中的字符。
- 如需修改，通常生成新字符串，例如使用 `replace()` 或切片拼接。

## 3. 常用字符串操作

### 查询与判断

- `len(text)`：返回字符数量。
- `substring in text`：判断子串是否存在。
- `text.count(sub)`：统计子串出现次数。
- `text.find(sub)`、`text.rfind(sub)`：查找首次或最后一次出现位置，找不到返回 `-1`。
- `text.index(sub)`：查找位置，找不到触发 `ValueError`。
- `text.startswith(prefix)`、`text.endswith(suffix)`：判断前缀或后缀。

### 修改与切分

- `text.replace(old, new, count)`：生成替换后的新字符串。
- `text.split(sep)`、`text.rsplit(sep, maxsplit)`：按分隔符切分为列表。
- `text.splitlines()`：按行切分。
- `separator.join(iterable)`：用分隔符连接多个字符串。
- `text.strip()`、`lstrip()`、`rstrip()`：去除两端、左侧或右侧空白。

### 大小写与排版

- `upper()`、`lower()`、`title()`、`capitalize()`、`swapcase()`。
- `center(width)`、`ljust(width)`、`rjust(width)`、`zfill(width)`。

### 字符判断

- `isdigit()`、`isalpha()`、`isalnum()`、`isspace()`。
- `islower()`、`isupper()`、`istitle()`。
- 判断方法返回布尔值，不等同于完整的输入校验。

### 编码与解码

- `text.encode("utf-8")` 把字符串转换为字节串。
- `data.decode("utf-8")` 把字节串转换为字符串。
- 读写文件时应明确使用一致的字符编码。

### 代码示例:
```python
# 字符串的常用操作
text = "  Python Programming  "

print(f"原始字符串：'{text}'")
print(f"去掉空格：'{text.strip()}'")
print(f"转大写：'{text.upper()}'")
print(f"转小写：'{text.lower()}'")
print(f"替换内容：'{text.replace('Python', 'Java')}'")
print(f"字符串长度：{len(text)}")
print(f"是否包含Python：{'Python' in text}")
```
字符串的索引和切片操作让我们能够精确地提取需要的部分
```python
# 字符串索引和切片
greeting = "Hello, Python!"

print(f"第一个字符：{greeting[0]}")
print(f"最后一个字符：{greeting[-1]}")
print(f"前5个字符：{greeting[:5]}")
print(f"后7个字符：{greeting[-7:]}")
print(f"中间部分：{greeting[7:13]}")
print(f"反转字符串：{greeting[::-1]}")
```

## 4. 字符串格式化

### 百分号格式化

```python
text = "姓名：%s，年龄：%d" % ("Alice", 18)
```

- 使用 `%s`、`%d`、`%f` 等占位符。
- 属于较早的格式化方式，新代码中通常优先使用 f-string。

### `str.format()`

```python
text = "姓名：{}，年龄：{}".format("Alice", 18)
text = "姓名：{name}，年龄：{age}".format(name="Alice", age=18)
```

- 支持位置参数、关键字参数和重复引用。

### f-string

```python
name = "Alice"
score = 95.5
print(f"{name} 的分数是 {score:.1f}")
```

- 在字符串前加 `f`，把表达式直接写入 `{}`。
- 支持调用函数、访问属性和执行简单表达式。
- 格式说明符写在冒号后，例如 `:.2f`、`:>10`、`:04d`、`:,`。

## 5. 正则表达式基础

正则表达式是处理文本模式匹配的强大工具, 语法相对复杂, 但在文本处理中及其有用.
### 基本使用

```python
import re

# 图书馆系统的用户数据清洗
def clean_user_data():
    # 邮箱验证
    emails = ["yuyirrr@yuyirrr.com", "invalid-email", "user@domain.cn"]
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    print("=== 邮箱验证 ===")
    for email in emails:
        if re.match(email_pattern, email):
            print(f"✓ {email} 格式正确")
        else:
            print(f"✗ {email} 格式错误")
    
    # 手机号提取
    text = "联系管理员老蒋：手机 13800138000，微信同号。备用联系方式：15900159000"
    phone_pattern = r'1[3-9]\d{9}'
    phones = re.findall(phone_pattern, text)
    print(f"\n提取到的手机号：{phones}")
    
    # 密码强度检查
    passwords = ["123456", "abc123", "MyPassword123!", "weakpwd"]
    # 至少8位，包含大小写字母、数字和特殊字符
    strong_pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
    
    print("\n=== 密码强度检查 ===")
    for pwd in passwords:
        if re.match(strong_pattern, pwd):
            print(f"✓ {pwd} 强度足够")
        else:
            print(f"✗ {pwd} 强度不足")

clean_user_data()
```
这段程序输出结果:
```
=== 邮箱验证 ===
✓ yupi@yuyuanweb.com 格式正确
✗ invalid-email 格式错误
✓ user@domain.cn 格式正确

提取到的手机号：['13800138000', '15900159000']

=== 密码强度检查 ===
✗ 123456 强度不足
✗ abc123 强度不足
✓ MyPassword123! 强度足够
✗ weakpwd 强度不足
```
- 正则表达式用于匹配、查找、提取和替换文本模式。
- 正则表达式通常使用原始字符串 `r"..."`，避免反斜杠被提前转义。
- `re.match()` 从字符串开头匹配，`re.search()` 在任意位置查找，`re.fullmatch()` 要求整个字符串匹配。
```python
import re
# 简历处理
def process_resume():
    resume_text = """
    管理员老蒋
    邮箱：yuyirrr@yuyirrr.com
    手机：138-0013-8000
    GitHub: https://github.com/yuyrrrrrrr
    技能：Python、Java、JavaScript
    """
    
    # 替换手机号格式
    phone_pattern = r'(\d{3})-(\d{4})-(\d{4})'
    resume_text = re.sub(phone_pattern, r'\1\2\3', resume_text)
    
    # 提取所有链接
    url_pattern = r'https?://[^\s]+'
    urls = re.findall(url_pattern, resume_text)
    
    print("处理后的简历:")
    print(resume_text)
    print(f"\n提取到的链接: {urls}")

process_resume()

```
程序输出结果
```
处理后的简历:

    管理员老蒋
    邮箱：yuyirrr@yuyirrr.com
    手机：13800138000
    GitHub: https://github.com/yuyrrrrrrr
    技能：Python、Java、JavaScript
    
提取到的链接: ['https://github.com/yuyrrrrrrr']

```
### 常用函数

- `re.findall(pattern, text)`：返回全部匹配结果。
- `re.finditer(pattern, text)`：返回匹配对象迭代器。
- `re.sub(pattern, replacement, text)`：替换匹配内容。
- `re.split(pattern, text)`：按模式切分字符串。
- `re.compile(pattern)`：预编译并复用正则表达式。

### 常用语法

| 语法 | 含义 |
|---|---|
| `.` | 匹配除换行外的任意字符 |
| `\d` | 数字字符 |
| `\w` | 字母、数字或下划线 |
| `\s` | 空白字符 |
| `^`、`$` | 字符串开头、结尾 |
| `*`、`+`、`?` | 重复 0 次以上、1 次以上、0 或 1 次 |
| `{m,n}` | 重复 m 到 n 次 |
| `[]` | 字符集合 |
| `|` | 或 |
| `()` | 分组 |

- 量词默认采用贪婪匹配，追加 `?` 可使用非贪婪匹配。
- 分组可通过 `group(1)` 等方式提取。
- 复杂文本解析通常不应只依赖正则表达式。

