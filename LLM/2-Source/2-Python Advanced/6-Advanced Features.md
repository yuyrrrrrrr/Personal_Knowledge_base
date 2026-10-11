---
order: 6
tags: [Python, 高级特性]
prerequisites: ["[[5-OOP (object-oriented programming)]]"]
next: "[[7-Code Quality And Testing]]"
---

## 本章大纲

- [[#1. 迭代器]]
- [[#2. 生成器]]
- [[#3. 上下文管理器]]
- [[#4. 并发编程基础]]
- [[#5. 线程与进程]]
- [[#6. 异步编程]]
- [[#7. 其他高级特性]]

## 1. 迭代器(iterator)

```python
numbers = iter([1, 2, 3])
print(next(numbers))
```

- 可迭代对象实现 `__iter__()`，可以被 `for` 遍历。
- 迭代器同时实现 `__iter__()` 和 `__next__()`，记录当前迭代状态。
- `next(iterator)` 获取下一个元素，耗尽后抛出 `StopIteration`。
- 迭代器具有一次性特点，耗尽后不能直接重新遍历。
- 自定义迭代器适合按规则逐个产生数据。

```python
class Countdown:
    def __init__(self, start):
        self.current = start

    def __iter__(self):
        return self

    def __next__(self):
        if self.current <= 0:
            raise StopIteration
        self.current -= 1
        return self.current + 1
```
```
```

```python
class ResumeTemplateIterator:
    """老鱼简历模板迭代器"""
    
    def __init__(self, templates):
        self.templates = templates
        self.index = 0
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.index >= len(self.templates):
            raise StopIteration
        
        template = self.templates[self.index]
        self.index += 1
        return template

class ResumeTemplateCollection:
    """简历模板集合"""
    
    def __init__(self):
        self.templates = [
            {"name": "经典模板", "category": "通用", "price": 0},
            {"name": "创意模板", "category": "设计", "price": 19.9},
            {"name": "技术模板", "category": "IT", "price": 29.9},
            {"name": "商务模板", "category": "商业", "price": 39.9}
        ]
    
    def __iter__(self):
        return ResumeTemplateIterator(self.templates)

# 使用自定义迭代器
templates = ResumeTemplateCollection()

print("=== 老鱼简历模板迭代器 ===")
for template in templates:
    print(f"模板: {template['name']}, 类别: {template['category']}, 价格: {template['price']}")

```
## 2. 生成器(generator)

```python
def number_stream(limit):
    for number in range(limit):
        yield number * number

squares = number_stream(5)
```

```python
def coding_progress_tracker():
    """编程导航学习进度生成器"""
    courses = ["Python基础", "数据结构", "算法进阶", "Web开发", "项目实战"]
    
    for i, course in enumerate(courses, 1):
        progress = (i / len(courses)) * 100
        yield {
            "course": course,
            "progress": progress,
            "status": "已完成" if progress == 100 else "学习中"
        }

# 使用生成器
print("=== 程序员鱼皮的学习进度 ===")
for progress in coding_progress_tracker():
    print(f"{progress['course']}: {progress['progress']:.1f}% - {progress['status']}")

```

生成器表达式提供了更简洁的创建方式, 它的语法类似于列表推导式, 但使用圆括号而不是方括号
```Python
def interview_question_generator():
    """面试鸭题目生成器"""
    subjects = ["Python", "算法", "数据库", "前端", "后端"]
    difficulties = ["简单", "中等", "困难"]
    
    # 生成器表达式
    questions = (
        f"{subject}_{difficulty}_{i}"
        for subject in subjects
        for difficulty in difficulties
        for i in range(1, 4)
    )
    
    return questions

# 使用生成器表达式
question_gen = interview_question_generator()
print("\n=== 面试鸭题目生成器 ===")
for i, question in enumerate(question_gen, 1):
    print(f"题目 {i}: {question}")
    if i >= 10:  # 只显示前10个
        break

```
- 包含 `yield` 的函数会返回生成器对象。
- 生成器按需产生值，适合处理大数据流和无限序列。
- 调用生成器函数时不会立即执行函数体，首次迭代才开始执行。
- `yield from` 可以把另一个可迭代对象的值依次委托出来。
- 生成器表达式使用圆括号，例如 `(x * x for x in range(5))`。
- 生成器同样是一次性对象，不适合反复遍历。

## 3. 上下文管理器

```python
from contextlib import contextmanager

@contextmanager
def managed_resource():
    print("获取资源")
    try:
        yield "resource"
    finally:
        print("释放资源")
```

- 上下文管理器保证资源在进入和退出时执行固定逻辑。
- 类可以通过 `__enter__()` 和 `__exit__()` 实现协议。
- `contextlib.contextmanager` 可以把生成器快速转换为上下文管理器。
- 常见用途包括文件、连接、锁、事务和临时状态恢复。
- 清理逻辑应放在 `finally` 中，保证异常时也能执行。

## 4. 并发编程基础

- 并发描述多个任务在重叠时间段内推进，并行强调多个任务同时执行。
- I/O 密集型任务通常适合线程或异步 I/O。
- CPU 密集型任务通常适合多进程或原生扩展。
- Python 的全局解释器锁 `GIL` 会限制同一解释器内多个线程同时执行 Python 字节码。
- 共享可变状态可能产生竞态条件，应使用锁、队列或消息传递保护。
- 并发不是自动提升性能，应先测量瓶颈再选择模型。

## 5. 线程与进程

### 线程

```python
from threading import Thread

thread = Thread(target=worker, args=(data,))
thread.start()
thread.join()
```

- 线程适合等待网络、文件和其他 I/O 操作。
- 线程共享进程内存，通信方便但需要同步机制。
- `Lock`、`RLock`、`Event`、`Queue` 常用于线程协调。

### 进程

```python
from multiprocessing import Process

process = Process(target=worker, args=(data,))
process.start()
process.join()
```

- 进程拥有独立内存空间，适合 CPU 密集型任务。
- 进程间通信成本通常高于线程，可使用队列、管道或共享内存。
- `concurrent.futures` 提供线程池和进程池的统一接口。

```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=4) as executor:
    results = executor.map(worker, items)
```

## 6. 异步编程

```python
import asyncio

async def fetch_data():
    await asyncio.sleep(1)
    return "data"

result = asyncio.run(fetch_data())
```

- `async def` 定义协程函数，调用后得到协程对象。
- `await` 暂停当前协程，把控制权交还事件循环。
- `asyncio.run()` 创建事件循环并运行主协程。
- 异步适合大量网络请求和 I/O 等待，不自动让 CPU 任务并行。
- 阻塞函数会卡住事件循环，应使用异步库或线程执行器。
- `asyncio.gather()` 可以并发等待多个可等待对象。

## 7. 其他高级特性

- 解包和星号表达式简化参数与容器处理。
- 推导式适合简单的数据转换和过滤。
- `dataclasses` 可以减少数据类样板代码。
- `functools.lru_cache` 可以缓存纯函数结果，但要关注内存和参数可哈希性。
- `__slots__` 可以减少实例字典开销，但会限制动态属性。
- 高级特性应服务于可读性和性能目标，不应为了炫技增加复杂度。
