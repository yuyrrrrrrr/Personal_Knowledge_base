2026-09-17 17:53
大家好，我是不会喷火的小火龙。

> 相关阅读：[[告别 Agent 研发失控：vibe-workflow 实战指南]]

今天聊一个让我笑出声，但笑完立刻打开项目开始配置的 GitHub 项目。

---

## 一、你的钱包，正在被 AI 的"客套礼貌"掏空

用 Claude Code 或 Cursor 写代码的同学，对下面这种场景一定不陌生：

你："帮我看下这个 [React](https://www.mianshiya.com/bank/1817900465338241026) 组件为什么重复渲染。"

AI：_"好的！非常理解您的需求！为了帮您深入排查这个 React 组件的重复渲染问题，我将首先详细分析您当前的代码结构。从您提供的代码来看，这个问题很可能与组件的 props 引用变化有关。让我来一步步为您解释这个现象的根本原因……"_

69 个 Token。说了一大堆。核心信息只有一句话。

这些 Token 全是要花钱的。更麻烦的是，这些废话会迅速填满你的上下文窗口。上下文被垃圾信息塞满以后，AI 后续回复的质量直线下降，改 Bug 越改越慢，越改越容易忘掉之前的讨论内容。

你每个月的 API 账单里，可能有一半以上都是在给 AI 的"社交礼貌"买单。

下面这张图基本就是大部分开发者的日常：

![image.png](https://pic.code-nav.cn/post_picture/1612112775822180354/pyt9tQ6J3RsUiezN.webp)

---

## 二、十万星的 Caveman 到底干了啥？

2026 年 4 月的一个周五，一个叫 Julius Brussee 的开发者在 GitHub 上传了一个项目，名字叫 [Caveman](https://github.com/juliusbrussee/caveman)（原始人）。

口号只有一句：

> **"why use many token when few token do trick"**

模仿的是美剧《办公室》里 Kevin 的经典名言（为什么要用很多词，少几个词也能成事）。

一开始大家当他在玩梗。一周之后，4000 星。再后来，GitHub 趋势榜第一，Hacker News 第一（904 分、366 条评论），JetBrains 实验室拿 86 个真实编码任务做了严格测试，Adobe Research 专门写了一篇学术论文来验证它。

截至今天，超过 10 万星。

### 同一个 Bug，两种回答

看看同一个 React 重复渲染问题，两种 Agent 的输出：

||普通 Agent（69 Tokens）|野人 Agent（19 Tokens）|
|---|---|---|
|**回复内容**|"The reason your React component is re-rendering is likely because you're creating a new object reference on each render cycle. When you pass an inline object as a prop, React's shallow comparison sees it as a different object every time, which triggers a re-render. I'd recommend using useMemo to memoize the object."|"New object ref each render. Inline object prop = new ref = re-render. Wrap in `useMemo`."|
|**诊断**|正确|正确|
|**解法**|`useMemo`|`useMemo`|
|**Token 数**|69|19|

诊断一样。解法一样。代码一样。唯一死掉的就是废话。

项目 README 里有一句话我觉得说得好：

> **"Caveman no make brain smaller. Caveman make _mouth_ smaller."**
>
> 野人不把脑子变小，野人只把嘴变小。

### 什么不会被"野人化"？

作者 Julius Brussee 在 Hacker News 上澄清过：

> "This skill is not intended to reduce hidden reasoning / thinking tokens... What it targets is the visible completion: less preamble, less filler, less polished-but-nonessential text. Therefore, since post-completion output is 'cavemanned' the code hasn't been affected by the skill at all."

翻译一下：

1. AI 内部的思考过程（Thinking Tokens）完全不碰，该怎么想还怎么想。
2. 代码块、命令行、文件路径、错误信息原样输出，一个字都不改。
3. 安全警告和"你确定要执行这个危险操作吗"这类提示，自动恢复完整句式。
4. 被压缩的只有套话、客套、铺垫、重复解释。

Caveman 关键代码与安全警告完整保留展示：

![image.png](https://pic.code-nav.cn/post_picture/1612112775822180354/2RAbnHPxaJdf8JkH.webp)

---

## 三、为什么我们不能学习 AI 当野人？

看到这里你可能会想："既然让 AI 少说话能省钱，那我是不是也少跟 AI 说话？用更短的 Prompt 双向省钱？"

Adobe Research 替你做了这个实验。2026 年 6 月，他们发表了一篇论文叫《CAVEWOMAN》（名字从 Caveman 来的），在 8 个模型、5 组数据集上严格测试了两个方向的语言压缩效果。

结论和直觉相反。

如图 3 所示，双通道压缩的实验结果：

![image.png](https://pic.code-nav.cn/post_picture/1612112775822180354/GyuzLJtQkO0jfVmv.webp)

具体数据：

- 让 AI 简短回复（输出压缩）：净成本削减 1.4 到 2.4 倍，最高达 3 倍。任务完成率不受影响。
- 人类给 AI 发模糊短语（输入压缩）：净成本反而暴涨 1.15 到 2.7 倍。因为输入信息不够，AI 会耗费大量 Token 去脑补、猜测、过度解释，而且准确率严重下滑。

你跟 AI 说话不能偷懒，需求描述越详尽越好。但你可以要求 AI 回复你的时候像野人一样简短。

一句话总结：人说人话，AI 说野人话。

口说无凭，我直接在本地拿真实模型跑了一组对比评测。

面对同一个典型的 React 重复渲染 Bug，分别交给"标准模式"和"野人模式"去解，本地真实终端评测对比截图如图 4 所示：

![image.png](https://pic.code-nav.cn/post_picture/1612112775822180354/9inB8KCPmVnNprQm.webp)

跑出来的数字非常直观：

- **标准 Agent（无约束）**：吐了整整 4,515 个 Token，洋洋洒洒写了一大篇分析小作文，耗时 **57.3 秒**；
- **野人 Agent（极简约束）**：只用了 **1,033 个 Token**，点明原因直奔核心代码，耗时压缩到 **22.97 秒**。

**输出 Token 削减了整整 77.1%，响应速度快了 2.5 倍。** 代码修复逻辑完全一致，没有任何质量折损。

---

## 四、零成本上手"白嫖指南"

### 方案 A：官方一行命令

如果你用 Claude Code、Cursor、Codex、Gemini CLI 等 30 多种主流 Agent 工具中的任何一个，直接在终端跑：

```bash
npx skills add JuliusBrussee/caveman -g
```

装完以后，Agent 会自动开始用极简风格回复你。如果没有自动生效，输入 `/caveman` 触发即可。

### 方案 B：复制 Rules 模板，零安装

如果你不想装额外依赖，直接把下面这段规则复制到项目根目录的 `.cursorrules`、`CLAUDE.md` 或 `AGENTS.md` 文件里。

```markdown
# Agent 输出精简规范

## 回复风格
- 禁止任何形式的寒暄、客套、感叹词开场（如"好的！""当然！""非常理解！"）。
- 禁止重复用户的问题或需求描述。用户已经知道自己问了什么。
- 先给结论或修复代码，再用 1~2 句话说原因。不要反过来。
- 不解释对方已知的基础概念。对方是有经验的开发者。

## 代码输出
- 修改已有代码时，只输出 diff 或变更部分，不要输出完整文件。
- 新建文件时才输出完整代码。
- 禁止在代码注释中写"这里我们做了XX"这类叙述性注释。

## 格式
- 不使用 emoji 装饰。
- 列表不超过 5 项，超过的合并或省略次要项。
- 段落最多 3 句话。能用一句说清楚就不写两句。
```

这份规则不需要安装 Node.js，不需要跑命令，不需要代理。放进去就生效。

根据我自己的使用经验，光这一份规则就能砍掉 30% 到 50% 的输出 Token。如果再搭配 Caveman 的官方 Proxy（负责压缩 AI 读取的日志、JSON 和搜索结果），还能在输入端再省一截。

![image.png](https://pic.code-nav.cn/post_picture/1612112775822180354/Wv6BikBBqbb8jbJI.webp)

---

## 五、降本是独立开发者的第一生命线

回到最开始的问题。一个按词收费的 AI 编程工具，写东西像在写求职信，这合理吗？

站在模型厂商的角度，当然合理。Agent 越啰嗦，它们收的钱越多。

站在你的角度，用工程手段给 AI 的输出做一次"脱水"，是最直接的降本方式。你不需要换更便宜的模型（那会损失代码质量），只需要让同一个模型闭上它的"客套嘴"。

省下来的每一分 Token 费，对独立开发者来说都是纯利润。
