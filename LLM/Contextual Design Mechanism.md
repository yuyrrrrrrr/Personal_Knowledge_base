> 前置阅读：[[AI Concept]]

## 上下文是根本问题

![[Pasted image 20260927105444.png]]

harness框架和agent智能体的问题，本质都是在有限的上下文窗口里，做信息的取舍与编排。

我们以claude code为例，来介绍这些设计。

## 常见的上下文构成
![[Pasted image 20260927095247.png]]
可以用/context指令查看上下文构成。

> [!IMPORTANT] 为什么MCP是上下文隐形杀手？ 比如github mcp，包含20-30个工具定义，约4k-6k tokens，5个mcp就是25k tokens。 [!IMPORTANT] /context指令，会经常用

## 上下文分层

![](https://i0.hdslb.com/bfs/new_dyn/32b2ada7650e7e0a5cbf6255e0d6126c88926070.png@976w_506h.webp)

## 自动压缩

token总量快到上下文窗口的时候，会触发auto-compact。

### 压缩机制

1. 清除工具输出：比如grep、bash、glob、websearch、fileread、fileedit，输出替换成占位符

2. 记忆文件：平时后台持续fork子代理提取关键信息，写到.claude/projects/*/MEMORY.md，压缩时直接复用

3. 摘要：让大模型对对话作摘要，清空最早的对话，重新注入上下文


上述过程：

- 可以自动触发

- 可以用/compact 保留XXX手动触发

- 可以把压缩规则添加到CLAUDE.md文件中


### compact不够好

这套压缩机制，容易丢信息，两种解决方案：

- 压缩规则：把压缩规则写进CLAUDE.md中

- 笨办法：/config关闭auto-compact，plan模式手动总结前面的上下文，人审核后保存到本地，/clear清空会话，读取保存的文件


## memory

memory由这些构成：

![](https://i0.hdslb.com/bfs/new_dyn/451518378229ce81e57972eb388f537788926070.png@1134w_376h.webp)

可以用/memory指令查看memory构成。

# agent.md
## CLAUDE.md

CLAUDE.md是常驻上下文的。

### 优先级

CLAUDE.local.md > ./CLAUDE.md > ~/.claude/CLAUDE.md

CLAUDE.local.md

- 项目根目录（需用 .gitignore 忽略）

- 个人使用


./CLAUDE.md

- 项目根目录

- 团队共享


~/.claude/CLAUDE.md

- 用户主目录

- 用户全局


> [!IMPORTANT] settings.json同理，如果hooks、plugin、permissions配置，仅限这个项目使用，可以写入项目目录的 **.claude/settings.local.json** [!IMPORTANT] 可以用#前缀，添加信息到CLAUDE.md

### 内容取舍

正确的

- build、test、run的命令

- 关键目录结构、模块边界、常量

- 命名约定

- 不明显的环境配置问题、已知bug

- 禁止做的事，同时提供替代方案

- /compact时必须保留的信息（不用压缩可以不写）

- 什么情况应该参考什么路径的文档


错误的

- 低频任务知识 → 放到Skills

- 大量背景资料和完整 API 文档 → 改为”详见 path/to/doc”

- 空泛原则，如”写高质量代码”

- Claude 通过读仓库即可推断的显然信息

- 只有“禁止”而没有替代方案

- 用 @src/api/client.ts 引用文件 → 改为纯文本路径：


详见 src/api/client.ts，避免加载整个文件到上下文

### 维护

可以让Claude 维护自己的 CLAUDE.md

/insight指令提炼信息

人工定期剪枝，控制在200行以内

## rules

可以把项目规范细分成独立的markdown文件，比如API、类型定义、组件。

放在.claude/rules/目录下，路径匹配加载。

### 路径加载

Claude Code 读取.claude/rules/*.md，根据文件头元数据决定加载方式，加载到memory。

.claude/rules/*.md示例

代码块

PlainText

自动换行

复制代码

```plaintext
---
paths:
  - "src/api/**/*.ts"
  - "src/xxx/**/*.ts"
---
# API Design Rules

- xxxx
- xxxxx
```

复制成功

- 不带 paths 元数据：视为**全局规则**，加载到memory，整个会话持续生效。

- 带 paths 元数据：视为**条件规则**，**仅当操作的文件路径匹配到**paths**中的路径才会加载**，用来节省上下文窗口。


## SKILL

SKILL的加载层级更多，也叫“渐进式披露”。

可以看作加强版rules。

### 渐进式披露

标准的skill目录：

代码块

PlainText

自动换行

复制代码

```plaintext
.claude/skills/
└── example-skill/
    ├── SKILL.md		← description 始终在上下文，匹配后整个加载
    ├── runbook.md
    ├── examples.md
    ├── scripts/
    │   └── helper.py
    └── references/
        └── spec.md
```

复制成功

SKILL.md示例：

代码块

PlainText

自动换行

复制代码

```plaintext
---
name: example-skill
description: 当用户想要执行 [操作 X] 时使用此技能。它会处理 [上下文 Y] 并确保实现 [结果 Z]。
disable-model-invocation: true
---

# 技能名称示例

在此处为 Claude 编写详细指令……

## 使用示例
- "对文件 Y 执行 X"
- "帮我完成 Z"

## 脚本与资源
- 参见 `scripts/helper.py` 获取确定性处理逻辑。
- 参见 `references/spec.md` 获取技术标准。
```

复制成功

加载顺序：

1. 文件头元数据name、description、disable-model-invocation始终放上下文里

2. 任务匹配时，再把整个SKILL.md放上下文里

3. 模型根据需要读取其他文件

4. 模型根据需要执行scripts/里面的脚本


### 内容取舍

- description一句话概括，写”何时该用我“，而不是“我是干什么的”


比如help with backend，任何后端都能触发

- SKILL.md要写完整步骤、输入输出、停止条件

- 一个skill只做一件事


比如review、debug、docs都写进去

- SKILL.md只写骨架，文档放其他文件，方便按需加载

- 不想让claude自己决定运行，要加显式调用disable-model-invocation: true（只能用命令手动触发）


### 自定义命令调用

命令文件：.claude/commands/fix-issue.md

代码块

PlainText

自动换行

复制代码

```plaintext
请修复 Issue #$ARGUMENTS[1]。
1. 分析问题原因。
2. 实现修复。
3. 调用 `/code-review-skill` 对修改进行审查。
```

复制成功

调用方式：/fix-issue 5678，$ARGUMENTS[1]会被替换为5678

## MCP

> [!IMPORTANT] 建议少用MCP，MCP多了占用上下文窗口，多用CLI

### 理念

- 强调外部交互 → 用 CLI


强调工作流程 → 写 Skill

- 不重复造轮子，不做 Shell 可以做的事

- 静态知识，模型参数库里有的不外部获取，能直接发文件就不动态获取


### 搜索模式

超过上下文窗口的10%，自动启用搜索模式，MCP多的话可以节约上下文。

在~/.claude/settings.json修改

代码块

PlainText

自动换行

复制代码

```plaintext
{
  "env": {
+    "ENABLE_TOOL_SEARCH": "true"
  }
}
```

复制成功

也可以设置为"ENABLE_TOOL_SEARCH": "auto:0"

阈值为0，也就是始终搜索模式，MCP只有1-2个就没必要。

## subagents

subagent好处是隔离上下文，坏处也是隔离上下文

- Subagent有独立的上下文窗口，不污染主会话。

- 任务完成后，主会话只读取结果，不关心过程。


### 调用

- 可以用@的方式创建

- 可以/agents创建

- 可以自然语言让claude创建

- /branch从当前会话创建 fork subagent。


### 理念

- 适合探索性任务和并行任务。

- 子任务强依赖、频繁共享中间状态时，不要用 subagent。


### 内置 Subagent

![](https://i0.hdslb.com/bfs/new_dyn/1136c78fefe566790dd427f713c5075b88926070.png@656w.webp)

### 自定义subagent

自定义subagent文件头的元数据，会放进上下文

可以用/agents查看。

.claude/agents/xxx.md

代码块

PlainText

自动换行

复制代码

```plaintext
---
name: xxx
description: 实现xxx
model: haiku
color: orange
---

实现指定 xxx
1. xxx
2. xxx
```

复制成功

## Hooks

hooks好处是强制执行，不进上下文。

写强制执行的某些逻辑（比如保护文件不能改、任务完成要通知），模型理解容易出错。

/hooks指令可以查看当前 hooks。

可以自然语言让claude添加。

### 理念

- 确定性检查、单步判断：写hook

- 复杂语义、多步推理：交给模型


### 示例

.claude/hooks/lint-check.sh

代码块

PlainText

自动换行

复制代码

```plaintext
#!/bin/bash
cd "$CLAUDE_PROJECT_DIR" || exit 1

# Check if any ts/vue/scss files were modified
if git diff --name-only | grep -E '.(ts|tsx|vue|scss)$' > /dev/null 2>&1; then
  pnpm lint:fix
else
  exit 0
fi
```

复制成功

.claude/settings.json

代码块

PlainText

自动换行

复制代码

```plaintext
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": ""$CLAUDE_PROJECT_DIR"/.claude/hooks/lint-check.sh",
            "timeout": 120,
            "statusMessage": "Running lint & stylelint checks..."
          }
        ]
      }
    ]
  }
}
```

复制成功

### hook点

![](https://i0.hdslb.com/bfs/new_dyn/37d197a9cf1758d2661ecb63a010551088926070.png@1040w_2310h.webp)

![](https://i0.hdslb.com/bfs/new_dyn/3ea9d0cbe059c932a73330c773d2472188926070.png@1074w_708h.webp)
