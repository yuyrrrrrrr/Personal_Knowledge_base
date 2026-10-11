2026-09-08 14:11

> 相关阅读：[[玩具 Demo 到稳定交付：个人开发者的 3 条 AI 编程工程铁律]]

## 本节重点

用 Cursor、Claude Code 或 Antigravity 写代码时，很多同学都有过类似的体会：让 Agent 写个独立的辅助脚本或单文件 demo，通常很顺手；但如果把它放进一个现有的多文件项目里做多轮迭代，往往很容易失控。比如顺手改掉没让它动的基础库、改错一个地方后进入反复修补的死循环，或者换个对话窗口就把之前的设计细节忘光。

这篇文章介绍我开发的开源 Agent Skill —— vibe-workflow，以及它在微信小程序 moneyRecord（清新记账）中的实际用法。

本文主要包含四部分内容：

- 分析 Coding Agent 在多文件项目中失控的常见原因；
- vibe-workflow 的状态机与四条核心约束；
- 以 moneyRecord 小程序 v0.2.0（月度预算与每日走势图）为例，看需求冻结、垂直切片到自动化验证的完整流程；
- 在自己的项目中接入 vibe-workflow 的配置方法。

前置条件：有基本的 Git 使用经验，日常用过至少一款 AI 编程工具。

## 一、为什么 Coding Agent 容易把项目改崩？

在多轮需求开发中，Agent 常见的问题主要有四类：

### 1. 范围膨胀（Scope Creep）

让 Agent 把某个保存按钮改成异步提交，打开 Git Diff 却发现它顺带重构了全局请求封装，甚至把原本做好的异常处理删掉了。给 Agent 编码权限，很容易被模型理解为可以随意调整业务和架构范围。

### 2. 反复修补

遇到报错或单测失败时，Agent 的第一反应往往是就地加补丁：第 10 行报空就加一层判断，第 25 行受影响又补一个容错。几轮交互下来，Token 耗费不少，底层设计越来越乱，最初的问题依然没解决。

### 3. 上下文随会话丢失

聊天窗口的上下文有限，一旦会话被压缩或者新开对话，模型就失去了之前的上下文。哪怕重新粘贴 Prompt，它也很难准确还原上一轮为什么这么设计、哪些模块已经测通。

### 4. 虚假完成

模型经常在回复里宣称“所有功能均已实现并通过测试”，但实际运行或者跑单测时往往直接报错。没有真实的命令输出做佐证，模型的口头确认并不能作为交付依据。

这些问题的根源，通常不在于模型单点写代码的能力，而在于开发过程缺少生命周期管理和工程约束。如果不能把确定性的流程规范和模型自身的生成能力结合起来，Agent 的多轮产出就很难稳定。

## 二、vibe-workflow 的机制与核心约束

vibe-workflow 是一个生命周期编排器（Orchestrator）。它用一套状态机把需求澄清、规格编写、架构设计、分步实现与测试验证串联起来，约束 Agent 在每一步的动作边界。

```text
REQUIREMENTS_FROZEN (需求冻结)
  ↓
SPECIFIED (行为规格)
  ↓
DESIGNED (架构设计)
  ↓
PLANNED (实施计划)
  ↓
BUILDING (垂直切片实现)
  ↓
VERIFYING (证据验收)
  ↓
READY_TO_SHIP (就绪发布)
  ↓
RELEASED (正式归档)
```

在这个流程中，有四条核心规则：

### 1. 需求必须先冻结，实现细节可委派

项目或版本在写代码前，必须满足：

```text
Requirement Status == FROZEN
Open Questions == None
Current Release ID exists
Acceptance Goals are testable
```

只要还有未确定的需求疑问，或者状态未标记为 FROZEN，Agent 就必须停下来，不能直接生成业务代码。产品的边界由人决定，具体实现细节才由 Agent 负责。

### 2. 仓库是唯一记忆，聊天只是临时通道

不把设计方案和任务进度留在聊天记录里，而是统一保存在代码仓库的 `docs/vibe/` 目录下。 新开会话或切换窗口时，Agent 只需要读取 `docs/vibe/PROJECT.md` 和 `docs/vibe/PROGRESS.md`，就能获取当前状态，不需要依赖人工手动同步聊天上下文。

### 3. 普通修改自主推进，关键事项走决策门禁

私有函数命名、小文件重构、本地单测等日常编码由 Agent 自行决定。但如果涉及产品范围调整、公共接口兼容性变动、数据库结构迁移、安全策略以及最终发布，Agent 必须停下来给出方案，等待人工明确确认。

### 4. 没有新鲜的验证证据，不得声称完成

任务完成的判断标准只有一条：终端实际执行的测试命令或检查输出。必须有当前轮次跑通的测试日志，且覆盖既定的验收目标，才能把状态流转到完成。

此外还有一项熔断规则：如果 Agent 就同一报错连续修补 3 次仍未解决，或者改好一处导致其他两处出现新错误，必须停止打补丁，记录当前断点，重新审视架构或方案后再继续。

## 三、实战：微信记账小程序 moneyRecord

以正在开发的微信原生记账小程序 `moneyRecord` 为例。在 v0.1.0 跑通基础记账与分类后，我们通过 vibe-workflow 推进 v0.2.0 的月度预算与收支趋势分析功能。

### 1. 需求冻结与目标定义 (`PROJECT_BRIEF.md`)

在 `docs/vibe/releases/v0.2.0/PROJECT_BRIEF.md` 中，我们把本期范围和排除项写清楚，并将状态置为 FROZEN：

```markdown
## Requirement Control
- Requirement Status: FROZEN
- Current Release: v0.2.0
- Approved By: User

## In Scope (v0.2.0)
- [x] 月度预算管理: 支持设置、修改或关闭月度预算限额；本地持久化。
- [x] 首页预算进度展示: 首页汇总卡片展示进度条、剩余预算、已用百分比。
- [x] 超支提醒机制: 预算超支时进度条呈现珊瑚红并标注“超支 ¥XXX”。
- [x] 每日收支趋势图表: 统计页新增基于 Canvas 2D 的每日收支趋势图。

## Out of Scope
- 分类独立子预算
- 年报与跨年度对比
- 多账户管理

## Acceptance Goals
| Goal ID  | 可观察目标 | 验证方式 |
|---|---|---|
| GOAL-201 | 用户可成功设置月度预算，首页即时展示剩余预算与已用进度条 | 查看首页卡片渲染与数据 |
| GOAL-202 | 当月支出未超预算时进度条为清新绿色；超支时变红并计算差额 | 录入超预算数据检查状态机 |
| GOAL-203 | 统计页准确绘制当月每日收支趋势图表，柱状高度与金额匹配 | 自动化单测计算趋势聚合数据 |
| GOAL-204 | 切换统计月份时，趋势图与每日数据自动同步更新 | 切换历史月份核对 |

## Open Questions
- None
```

明确了 Out of Scope 之后，Agent 就不会擅自去写多账户或分类子预算相关的逻辑。列出 GOAL-201 到 204，也让后续验收有了具体的比对标准。

### 2. 行为规格与设计先行 (`SPEC.md` 与 `TECH_DESIGN.md`)

编码前先定义关键状态和计算规则。比如针对预算监控，在规格中先写明状态机：

```javascript
const BUDGET_STATUS = {
  HEALTHY: 'HEALTHY',       // 已用 < 80% (绿色)
  WARNING: 'WARNING',       // 80% <= 已用 <= 100% (橙色)
  OVER_BUDGET: 'OVER_BUDGET'// 已用 > 100% (红色，计算超支差额)
};
```

同时在架构设计中规定：UI 层不直接处理聚合，按日汇总的数据逻辑全部收敛到 `utils/recordService.js`，图表渲染使用微信原生的 Canvas 2D 接口。

### 3. 垂直切片拆解 (`IMPLEMENTATION_PLAN.md`)

不一次性修改所有模块，而是把任务拆成 4 个垂直切片：

- Slice 2.1: 预算存储与每日数据聚合服务（`storage.js`, `recordService.js`, `date.js`）。
- Slice 2.2: 预算设置界面与首页卡片联动（`pages/settings/*`, `pages/index/*`）。
- Slice 2.3: 统计页趋势分析与 Canvas 2D 图表渲染（`pages/stats/*`）。
- Slice 2.4: 自动化单测编写与集成验证。

每做完一个切片，Agent 都在 `docs/vibe/PROGRESS.md` 中打钩更新，这样无论中途被打断还是换窗口，接手时都能看到当前进度：

```markdown
- [x] Slice 2.1: 预算底层服务与日趋势聚合 (storage.js, recordService.js, date.js)
- [x] Slice 2.2: 预算管理界面与超支监控 (settings/*, index/*, record/*)
- [x] Slice 2.3: 统计页收支趋势分析与 Canvas 2D 图表 (stats/*)
- [x] Slice 2.4: 自动化测试与 v0.2.0 验证 (tests/test_v2.js, VERIFICATION.md, TECH_DESIGN.md)
```

### 4. 验证与证据记录 (`VERIFICATION.md`)

写完功能后，在终端执行测试：

```bash
node tests/test_core.js && node tests/test_v2.js
```

输出真实的测试结果：

```text
--- 开始测试 Slice 1 核心模块 ---
✓ utils/calc.js 测试通过
✓ utils/date.js 测试通过
✓ utils/icons.js 测试通过
✓ utils/categoryService.js 测试通过
✓ utils/recordService.js 核心领域逻辑测试全部通过！
========================================
🎉 自动化测试 100% 通过！
--- 开始测试 v0.2.0 预算与趋势分析模块 ---
✓ dateUtil.getDaysInMonth 测试通过
✓ storage.js 预算存取测试通过
✓ recordService.getBudgetStatus 状态机与超支计算测试通过
✓ recordService.getMonthDailyTrend 每日趋势聚合测试通过
================================================
🎉 v0.2.0 自动化测试 100% 全部通过！
```

把这些输出记录到 `docs/vibe/releases/v0.2.0/VERIFICATION.md`，确认 4 个 Acceptance Goal 都通过后，状态才正式更新为 `READY_TO_SHIP`。

![image.png](https://pic.code-nav.cn/post_picture/1612112775822180354/InZLnNvxRSnxwWGS.webp)

## 四、在现有项目中接入 vibe-workflow

将这套流程加入现有项目通常只需要三个步骤：

### 1. 在根目录配置 `AGENTS.md`

在项目根目录创建 `AGENTS.md`，让 Agent 进入工作区时先阅读基础规则：

```markdown
# Agent Instructions

## Workflow & Governance
本项目遵循 `vibe-workflow` 软件生命周期管理规范。

### 核心规则
1. **Constitution**:
   - 工程开始前必须冻结需求（Requirement Status == FROZEN, Open Questions == None）。
   - What to build is frozen. How to build it is delegated.
   - 不得静默改变产品范围；产品变化必须经过明确的人类决策。
   - Repository is memory. Chat is conversation.
   - 没有 fresh verification evidence，不得声称完成。
2. **事实源**:
   - 项目总览与索引: `docs/vibe/PROJECT.md`
   - 当前执行进度: `docs/vibe/PROGRESS.md`
   - 当前 Release 需求基线: `docs/vibe/releases/<release-id>/PROJECT_BRIEF.md`
   - 当前架构事实: `docs/vibe/TECH_DESIGN.md`
```

### 2. 建立 `docs/vibe/` 目录与基础文档

在 `docs/vibe/` 目录下放置两个核心文件：

- `PROJECT.md`：记录项目定位、当前版本与测试命令：

```markdown
# Project
- Project Name: 你的项目名
- Current Release: v0.1.0
- Quality Profile: Standard
- Supported Commands: npm test / npm run dev
```

- `PROGRESS.md`：记录当前执行切片与任务状态：

```markdown
# Progress
- Current Release: v0.1.0
- Current Workflow State: REQUIREMENTS_FROZEN
- Operational Status: ACTIVE
- Current Slice: None
- Next Task: 编写 SPEC.md 行为规范
```

### 3. 日常开发指令

配置完成后，日常给 Agent 发指令时就可以按流程推进：

- 开新需求时：“按照 vibe-workflow 规范，为我们规划 v0.3.0 的需求基线 `PROJECT_BRIEF.md`，列出需要我确认的问题。”
- 新窗口继续工作时：“先读 `docs/vibe/PROJECT.md` 和 `docs/vibe/PROGRESS.md`，确认当前进度后继续执行下一个切片。”

这样可以让 Agent 始终围绕既定的切片和测试目标推进，减少无谓的来回试错。

## 五、总结与仓库地址

使用 AI 辅助编程，工具的生成速度很快，但如果缺少约束，规模稍大就会带来返工成本。vibe-workflow 的出发点，就是通过需求冻结、仓库持久化记录、垂直切片和测试证据链，把开发过程固定在可控的轨道里。

如果你在开发中也遇到过 Agent 随意改代码或遗忘上下文的问题，欢迎尝试这个工作流。

已在 GitHub 开源： 👉 **[https://github.com/sz-xiaohuolong/vibe-workflow](https://github.com/sz-xiaohuolong/vibe-workflow)**

觉得对你有帮助的话，欢迎去 GitHub 点个 Star 支持一下。也欢迎提交 issue 或 PR，一起交流 Agent 工程化落地的经验。
