---
order: 2
tags: [Python, 模块, 包]
prerequisites: ["[[1-Functional Programming]]"]
next: "[[3-File Operations]]"
---

## 本章大纲

- [[#1. 模块基础]]
- [[#2. 导入方式]]
- [[#3. 自定义模块与执行入口]]
- [[#4. 包与相对导入]]
- [[#5. 模块搜索路径]]
- [[#6. 标准库]]
- [[#7. 第三方库与依赖管理]]

## 1. 模块基础

- 模块通常是一个 `.py` 文件，用于组织函数、类、变量和可执行代码。
- 每个模块拥有独立的命名空间，避免不同文件中的同名对象直接冲突。
- 模块名应遵循文件命名规范，优先使用小写字母和下划线。
- 导入模块时，模块顶层代码会在第一次导入时执行。
- 模块应减少导入阶段的副作用，把主要逻辑放入函数或类中。

## 2. 导入方式

```python
import math
import math as m
from math import sqrt
from math import sqrt as square_root
from math import *
```

- `import 模块名`：导入模块并保留模块命名空间，最推荐。
- `import 模块名 as 别名`：适合模块名较长或避免命名冲突。
- `from 模块名 import 对象`：只导入需要使用的对象。
- `from 模块名 import *`：会污染命名空间，通常不推荐。
- 导入语句应放在文件顶部，并按标准库、第三方库、本地模块分组。

## 3. 自定义模块与执行入口

```python
# tools.py
def add(a, b):
    return a + b

if __name__ == "__main__":
    print(add(1, 2))
```

```python
import tools

result = tools.add(1, 2)
```

- 自定义模块可与调用代码放在同一目录，或放入包中。
- `__name__` 在直接运行文件时为 `"__main__"`，被导入时为模块名。
- `if __name__ == "__main__":` 用于区分直接运行和模块导入。
- `__all__` 可以控制 `from module import *` 导出的名称。
- 避免在模块顶层执行耗时任务、打印调试信息或修改外部状态。

## 4. 包与相对导入

```text
project/
├── app/
│   ├── __init__.py
│   ├── models.py
│   └── services/
│       ├── __init__.py
│       └── user.py
└── main.py
```

```python
from app.models import User
from .models import User
from ..utils import clean_text
```

- 包是包含多个模块的目录，传统包通常包含 `__init__.py`。
- `__init__.py` 可用于初始化包、控制导出和设置包级变量。
- 绝对导入从项目根包开始，可读性更好。
- 相对导入使用 `.` 表示当前包，`..` 表示上一级包。
- `from 包名 import *` 需要在包的 `__init__.py` 中通过 `__all__` 明确导出内容。
- 直接运行包含相对导入的模块时可能报错，应从项目入口运行。

## 5. 模块搜索路径

```python
import sys

print(sys.path)
```

- Python 导入模块时会依次搜索内置模块、`sys.path` 中的目录和已安装包。
- 当前运行脚本所在目录通常会加入搜索路径。
- `sys.path` 可以临时调整，但不建议在业务代码中随意修改。
- 模块首次导入后会缓存到 `sys.modules`，再次导入不会重新执行。
- 循环导入通常需要调整依赖方向、延迟导入或拆分公共模块。

## 6. 标准库

- `os`、`sys`：操作系统和解释器相关功能。
- `pathlib`：面向对象的路径处理。
- `json`、`csv`：常用数据格式读写。
- `datetime`、`time`：日期时间处理。
- `math`、`random`、`statistics`：数学、随机数和统计计算。
- `collections`、`itertools`、`functools`：常用数据结构和函数工具。
- `re`：正则表达式；`logging`：日志记录。
- 标准库应优先于自行重复实现，使用前先确认其适用范围。

## 7. 第三方库与依赖管理

- 第三方库应用通常通过 `pip install 包名` 安装。
- 虚拟环境可以隔离不同项目的依赖，避免全局环境冲突。
- `python -m venv .venv` 创建虚拟环境，激活后再安装依赖。
- `requirements.txt` 适合记录简单依赖，`pyproject.toml` 更适合现代项目配置。
- 应固定或约束关键依赖版本，保证环境可复现。
- 升级依赖前应检查兼容性并运行测试，避免间接依赖冲突。
