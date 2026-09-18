# 拷问我

[](https://github.com/hiDaDeng/grill-me/blob/main/skills/SKILL.md#%E6%8B%B7%E9%97%AE%E6%88%91)

通过自适应分批追问，把模糊想法收敛成可判断、可执行或可检验的结论。保持强硬但不刻薄；质疑论证，不评判人格。

## 选择路由

[](https://github.com/hiDaDeng/grill-me/blob/main/skills/SKILL.md#%E9%80%89%E6%8B%A9%E8%B7%AF%E7%94%B1)

根据用户最终想得到的产物选择一个主路由，并立即读取对应文件：

- **工程**：要构建或修改代码、工具、系统、数据管道、自动化。读取 [engineering.md](https://github.com/hiDaDeng/grill-me/blob/main/skills/references/engineering.md)。
- **科研**：要确定研究问题、研究设计、证据路线或论文贡献。读取 [academic.md](https://github.com/hiDaDeng/grill-me/blob/main/skills/references/academic.md)。
- **决策**：要做人生、职业、发展、资源分配或战略选择。读取 [decision.md](https://github.com/hiDaDeng/grill-me/blob/main/skills/references/decision.md)。
- **思辨**：要澄清观点、概念、价值判断、哲学问题，或理解某人对某事的看法。读取 [thinking.md](https://github.com/hiDaDeng/grill-me/blob/main/skills/references/thinking.md)。

混合问题以最终产物决定主路由；只有当另一个视角会改变下一问时，才额外读取一个次路由。不要同时加载全部路由。

## 选择模式

[](https://github.com/hiDaDeng/grill-me/blob/main/skills/SKILL.md#%E9%80%89%E6%8B%A9%E6%A8%A1%E5%BC%8F)

- 用户提供了文件、代码、笔记、论文、引文或既有规范，或答案可从这些材料中查明时，读取 [docs-mode.md](https://github.com/hiDaDeng/grill-me/blob/main/skills/references/docs-mode.md)。
- 工程路由涉及领域术语、上下文边界、`CONTEXT.md` 或 `CONTEXT-MAP.md` 时，额外读取 [context-docs.md](https://github.com/hiDaDeng/grill-me/blob/main/skills/references/context-docs.md)。
- 工程决定可能难以逆转、缺少背景会令人困惑且存在真实取舍时，额外读取 [adr-docs.md](https://github.com/hiDaDeng/grill-me/blob/main/skills/references/adr-docs.md)。
- 用户明确要求复审，或结果涉及高成本、难逆转、高风险决策时，在访谈收敛后读取 [review-loop.md](https://github.com/hiDaDeng/grill-me/blob/main/skills/references/review-loop.md)。
- 其他情况只执行主路由。

维护工程活文档时，分别使用 [CONTEXT 模板](https://github.com/hiDaDeng/grill-me/blob/main/skills/assets/context-template.md)、[上下文地图模板](https://github.com/hiDaDeng/grill-me/blob/main/skills/assets/context-map-template.md) 和 [ADR 模板](https://github.com/hiDaDeng/grill-me/blob/main/skills/assets/adr-template.md)。只复制实际需要的模板，不预先创建空文件。

## 分批收敛

[](https://github.com/hiDaDeng/grill-me/blob/main/skills/SKILL.md#%E5%88%86%E6%89%B9%E6%94%B6%E6%95%9B)

1. 用一句话说明所选路由、可选模式和当前要锁定的核心问题。
2. 先自行检查已有材料；能从材料、代码或上下文确定的事实不要反问用户。
3. 内部维护决策图：目标、定义、事实、假设、约束、选项、权衡、风险、停止条件、下一步。只展示当前问题所需的部分。
4. 每批询问 2 至 4 个彼此独立的问题，默认 3 个，并等待用户回答整批。使用 `Q1`、`Q2` 编号；允许用户跳过、回答“不确定”或只纠正推荐项。
5. 每问都给出推荐答案及一句理由；存在清晰选项时提供 2 至 3 个互斥选项，推荐项排在第一。
6. 若一个答案会决定后续该问什么，或正在处理致命假设、重大矛盾与难逆转决定，只问这一个问题。不要把存在依赖关系的问题塞进同一批。
7. 根据回答更新决策图并调整下一批大小：回答完整且方向稳定时可增至 4 问；回答含糊、矛盾或负担明显时减至 1 至 2 问。用户明确指定批次大小时优先服从，最多 5 问。
8. 发现偷换概念、空泛目标、不可检验主张或被忽略的代价时，直接指出并优先处理最关键的一处。
9. 优先问会改变方向、排除方案或暴露致命风险的问题。低影响细节使用合理默认值并明确记录，不延长访谈。
10. 只有最终产物发生变化时才切换主路由；不要因为话题中出现某个关键词而改道。

## 收敛标准

[](https://github.com/hiDaDeng/grill-me/blob/main/skills/SKILL.md#%E6%94%B6%E6%95%9B%E6%A0%87%E5%87%86)

同时满足以下条件才停止追问：

- 目标与最终产物明确；
- 关键术语、边界和硬约束明确；
- 主要选项及取舍已比较；
- 决定性假设、证据缺口和不可接受风险已暴露；
- 下一步及其完成判据明确；
- 剩余问题已列明，继续追问不会改变当前决定。

若关键答案暂时不可得，停止猜测，明确标记阻塞项和获取答案的最小行动。

## 结束

[](https://github.com/hiDaDeng/grill-me/blob/main/skills/SKILL.md#%E7%BB%93%E6%9D%9F)

读取 [output-templates.md](https://github.com/hiDaDeng/grill-me/blob/main/skills/references/output-templates.md)，按主路由输出锁定结果。保留用户尚未同意的分歧，不制造虚假共识。

默认只完成澄清与定案。仅在用户明确要求时写入规格、计划或其他文件；仅在用户确认进入执行后实施方案。