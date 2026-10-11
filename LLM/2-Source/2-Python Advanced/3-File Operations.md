---
order: 3
tags: [Python, 文件操作]
prerequisites: ["[[2-Modules and Packages]]"]
next: "[[4-Exception Handing]]"
---

## 本章大纲

- [[#1. 文件打开与关闭]]
- [[#2. 文本文件读写]]
- [[#3. 文件指针与缓冲]]
- [[#4. with 上下文管理]]
- [[#5. 路径处理]]
- [[#6. CSV 操作]]
- [[#7. JSON 操作]]
- [[#8. 文件与目录管理]]

## 1. 文件打开与关闭

```python
file = open("data.txt", mode="r", encoding="utf-8")
try:
    content = file.read()
finally:
    file.close()
```

- `open(path, mode, encoding)` 用于打开文件并返回文件对象。
- 文本模式应明确指定 `encoding="utf-8"`，减少跨平台乱码。
- 常用模式：`r` 只读、`w` 清空写入、`a` 追加、`x` 独占创建。
- `t` 表示文本模式，`b` 表示二进制模式，`+` 表示读写扩展。
- 文件使用完成后必须关闭，释放操作系统资源并刷新缓冲区。

## 2. 文本文件读写

### 读取

```python
with open("data.txt", encoding="utf-8") as file:
    all_text = file.read()
    file.seek(0)
    first_line = file.readline()
    file.seek(0)
    lines = file.readlines()
```

- `read(size)` 读取指定字符数，省略参数时读取全部内容。
- `readline()` 读取一行，`readlines()` 返回所有行组成的列表。
- 直接遍历文件对象可以逐行处理，适合大文件。

### 写入

```python
with open("output.txt", "w", encoding="utf-8") as file:
    file.write("第一行\n")
    file.writelines(["第二行\n", "第三行\n"])
```

- `write(text)` 写入字符串，不自动添加换行符。
- `writelines(lines)` 依次写入多个字符串，不自动添加分隔符。
- 使用 `w` 会清空原文件，需要追加时使用 `a`。

## 3. 文件指针与缓冲

- `tell()` 返回当前文件指针位置。
- `seek(offset, whence)` 移动文件指针。
- `seek(0)` 常用来回到文件开头。
- 文本文件的指针位置适合进行有限控制，二进制文件更适合精确随机访问。
- 写入内容可能暂存在缓冲区，`flush()` 可立即写入底层设备。
- `close()` 通常会刷新缓冲区；使用 `with` 可自动完成关闭。

## 4. with 上下文管理

```python
with open("data.txt", encoding="utf-8") as file:
    for line in file:
        print(line.rstrip())
```

- `with` 进入上下文时获取资源，退出时自动调用清理逻辑。
- 即使代码块中发生异常，文件也会被关闭。
- 优先使用 `with`，避免依赖手写 `close()`。
- 自定义类可实现 `__enter__()` 和 `__exit__()` 支持上下文管理。

## 5. 路径处理

```python
from pathlib import Path

path = Path("data") / "users.csv"
print(path.resolve())
print(path.exists())
```

- `pathlib.Path` 提供跨平台、面向对象的路径操作。
- `/` 运算符可以安全拼接路径。
- `exists()`、`is_file()`、`is_dir()` 用于检查路径。
- `name`、`stem`、`suffix`、`parent` 可读取路径组成部分。
- `mkdir()`、`rename()`、`unlink()` 分别用于创建目录、重命名文件和删除文件。
- `glob()`、`rglob()` 用于按模式查找文件。

## 6. CSV 操作

### 读取 CSV

```python
import csv

with open("users.csv", newline="", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    for row in reader:
        print(row["name"])
```

### 写入 CSV

```python
import csv

with open("users.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=["name", "age"])
    writer.writeheader()
    writer.writerow({"name": "Alice", "age": 18})
```

- `csv.reader` 和 `csv.writer` 按行处理列表数据。
- `csv.DictReader` 和 `csv.DictWriter` 按字典处理带表头数据。
- 文本模式打开 CSV 时常使用 `newline=""`，避免多余空行。
- CSV 是纯文本格式，不保存复杂嵌套结构和类型信息。

## 7. JSON 操作

```python
import json

data = {"name": "Alice", "age": 18}

with open("data.json", "w", encoding="utf-8") as file:
    json.dump(data, file, ensure_ascii=False, indent=2)

with open("data.json", encoding="utf-8") as file:
    loaded = json.load(file)
```

- JSON 支持对象、数组、字符串、数字、布尔值和 `null`。
- `json.dumps()` 把 Python 对象转换为 JSON 字符串。
- `json.loads()` 把 JSON 字符串解析为 Python 对象。
- `json.dump()` 和 `json.load()` 直接读写文件对象。
- `ensure_ascii=False` 可以保留中文，`indent` 用于美化输出。
- 日期时间、集合和自定义对象通常需要先转换为可序列化数据。

## 8. 文件与目录管理

- `os` 模块提供路径、环境和文件系统相关函数。
- `os.rename()` 重命名，`os.remove()` 删除文件，`os.mkdir()` 创建单个目录。
- `os.makedirs()` 可递归创建目录，`os.getcwd()` 获取当前目录，`os.chdir()` 切换目录。
- `shutil.copy()`、`shutil.move()`、`shutil.rmtree()` 处理常见复制、移动和删除任务。
- 删除和覆盖操作可能不可逆，应先检查路径并保留必要备份。
- 跨平台代码优先使用 `pathlib`，减少手动拼接路径字符串。
