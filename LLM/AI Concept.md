## 从模型调用开始

```python
# Please install OpenAI SDK first: `pip3 install openai`
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com")

response = client.chat.completions.create(
    model="deepseek-v4-pro",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"},
    ],
    stream=False,
    reasoning_effort="high",
    extra_body={"thinking": {"type": "enabled"}}
)

print(response.choices[0].message.content)
```

这是一个简单的deepseek api调用。你可以看到：

- base_url：模型厂商的接口地址

- api_key：用于认证的API KEY，一般格式是sk-xxxxxxxxxxx

- model：指定使用的模型，deepseek-v4-flash还是deepseek-v4-pro

- system prompt：系统提示词，全局设定。

- user prompt：用户提示词。

- stream：流式输出，大模型是按token一个一个预测的，流式输出可以让大模型按token一个一个输出

- reasoning_effort：思维链CoT的详细程度，详细程度越高，耗的算力越多

- "thinking": {"type": "enabled"}：用来开关模型的思维链

command: 将提示词结构化为md文件,可以用命令调出
metadata: 元数据, 不同场景下提示词md文件被调用时使用的描述信息,方便
AI区分和使用
References: 参考资料,当需求高,单个文件上下文长度过长就进行拆分,AI可以针对细分领域进行读取md文件
Scripts: 实现文件写入和导出
## system prompt和user prompt的区别

```python
messages = [
    {
        "role": "system",
        "content": "你是一位经验丰富的旅行规划师。请用简洁、有条理的列表形式回复，每次推荐不超过3个选项。"
    },
    {
        "role": "user",
        "content": "我计划10月去日本，想去看红叶，有什么目的地推荐吗？"
    },
    {
        "role": "assistant",
        "content": "当然！以下是10月日本赏枫的3个推荐地：\n1. **京都** – 岚山、清水寺，10月下旬开始变色。\n2. **日光** – 中禅寺湖周边，10月中旬最佳。\n3. **北海道层云峡** – 10月上旬即可观赏，适合早出行。"
    },
    {
        "role": "user",
        "content": "如果从东京出发，哪个地方交通最方便？"
    },
    {
        "role": "assistant",
        "content": "从东京出发，日光最方便：\n- 搭乘东武铁道或JR，约2小时直达。\n- 可当天往返，无需住宿。\n其余两地：京都需新干线+当地交通；北海道需飞机或长途JR。"
    },
    {
        "role": "user",
        "content": "那就日光吧，帮我规划一个2天1晚的行程，预算控制在3000人民币以内。"
    }
]
```

这是一个常见的对话messages

- system prompt（系统提示词） 全程生效。就像上面的例子，即便聊到最后的“日光”，模型也始终记得自己是一名旅行规划师，而不是别的身份。在一些 AI 产品中，它也可能被称为 rule（规则）——概念虽多，但只需记住它是在整个会话中持续起作用的设定。

- user prompt（用户提示词） 会累积成历史上下文（context），通常就是用户直接输入的内容。


另外，system prompt也不是严格的全程遵守，上下文长了之后，开头的 System Prompt会被稀释，也就是容易被遗忘。

比如你中途问了很多无关的东西，上午吃的什么，下午吃的什么，它可能会忘了最开始system prompt中的“简洁、有条理的列表形式”。

这是注意力机制导致的，这里不展开。

## context

context上下文是模型能看到的信息总和，也叫上下文窗口。也就是前面messages里面存的信息。

可以理解为“工作记忆”，模型每次生成回复的时候，会基于窗口内的全部内容进行计算，决定接下来该说什么。

上下文窗口大小以token为单位计算。比如deepseekv4pro上下文窗口是1M，约等于几十万汉字。

- 超过token上限，内容会被截断。

- 即使信息还在窗口内，过于久远的内容也可能被注意力机制稀释。


这两点给用户带来的体验就是，模型“遗忘”了信息。

关于上下文的组织、压缩与取舍，详见 [[Contextual Design Mechanism]]。

## harness

harness原意是马鞍缰绳，也就是把ai比做马，harness是用来驾驭ai的。
![[Pasted image 20260927103818.png]]

为了更好地使用ai，harness工程一般会提供：

- 工具

- 文件系统

- 权限

- 提示词

- 记忆

- 任务系统


harness并不是一个模型，而是一套为ai准备的工作流。

## tool

过去的大模型产品，一般是对话形式的，把你要问的东西，塞进他的上下文。

模型没法联网，不能运行代码，不能操作第三方软件。

工具的提出，就是为了解决这些问题。

常见的工具：

- API调用工具：可以让模型连接外部服务，比如高德API查位置。

- 代码执行工具：可以用python代码来做可视化。

- 搜索工具：可以接入搜索引擎或者本地知识库，获取实时信息，弥补模型知识限制。

- 浏览器工具：做网页上的点击、输入等操作，流程自动化。


## tool schema

怎样让模型知道如何使用工具？把工具代码直接塞进上下文吗？

通过tool schema工具说明书来解决，用结构化的 JSON，向模型说明以下信息：

- 工具名称

- 功能描述

- 需要的参数和类型

- 参数的约束


模型本身并不认识外部工具，也从不直接执行工具。流程是：

1. 将 tool schema 传入模型上下文。

2. 模型根据上下文和 schema 约束，生成一个包含工具名和参数的结构化调用指令。

3. harness 系统接收到调用指令后，真正去执行工具。

4. 工具执行的结果返回给模型。


## 文件系统

传统网页端的大模型对话，聊天内容往往“阅后即焚”，管理起来很不方便。有了文件系统后，情况就不同了。

现在可以告诉大模型，读取目录里的markdown，把处理结果写入csv，保存到其他文目录，再把这个csv作为下一个任务的输入。

复杂的多步骤的问题，处理起来更方便了。

## permission

当大模型可以执行代码后，意味着他可以通过代码修改、删除你的文件，所以要加入权限系统。

比如sudo rm -rf，你也不想让它随便执行吧。

## memory

memory是跨会话保存的信息，比如：

- 用户长期偏好，更喜欢用折线图而不是柱状图

- 别的会话依然有价值的信息，python遵循pep8规范


memory一般拼装到system prompt里去，也会放进上下文，所以宜精不宜多，应当只保留最有价值的长期信息。

## task

一个复杂任务，比如说“分析这个报表，找出下滑原因，写成报告”。直接对大模型说这个，效果往往不好。

有了任务系统后，会拆解成“读取文件 → 清洗数据 → 统计分析 → 生成图表 → 写报告”的步骤。

如果其中“生成图表”，因为某个python库没装卡住了，任务系统根据预设的策略，判断重试还是向用户求助，不至于因为小问题让整个流程瘫痪。

## agent

agent概念很广，现在大多说的是harness设计。

可以这样理解，agent=model+harness。

model提供智力，harness提供工具、记忆、权限、任务，所以agent能判断输入、调用工具、完成任务。

## agent loop

agent运行机制是反复执行的主循环，在重复以下过程：

1. 组装上下文发给模型

2. 模型决定直接回答，还是调用工具

3. 调用工具的话，也要执行工具

4. 把工具结果写回上下文

5. 继续下一轮循环


agent loop让模型不断循环，直到给出最终答案。

## compact

上下文窗口有限，compact上下文压缩就是为了解决这个问题。

压缩并不是简单的删掉旧的信息，compact要做的事是保留关键信息，减少冗余，不扭曲原意。

## subagent

“创建agent”本身也可以注册为一个工具。

一个agent可以调用工具，创建另一个agent，把新创建的这个叫做subagent子代理。子代理执行完后，结果传回父代理。

这样的好处是，子代理有独立上下文，防止污染原本的上下文。

## fork

这里说的fork是子代理的创建模式，不是git中的fork。

- 普通子代理：从空白上下文开始运行。

- Fork 子代理：会继承父代理当前的上下文，在该上下文的“快照”基础上继续工作。


## hook

hook是agent主循环中，预留的插入点。

打个比方，预留hook后，主循环变成了这样：

用户输入 → 模型决策 → [hook] → 执行工具 → [hook] → 返回结果

如果你想加权限校验，可以不动主循环本身，在执行工具前的[hook]加权限校验就行了。

hook可以方便插件做扩展。

## MCP

我的工具都在本地，能不能用统一的方式，接入外部的工具？MCP就是解决这个问题的。

MCP全称Model Context Protocol，是让agent和外部工具联系起来的统一协议。
![[Pasted image 20260927102340.png]]

MCP遵循客户端-服务端架构，

- 客户端：通常是AI应用，比如claude code、vscode插件、cursor，负责发起请求。

- 服务端：是暴露特定数据或工具的轻量程序，比如github mcp server（通过github API管理仓库、issue、PR）、postgres SQL MCP server（执行SQL查询）。


harness会根据工具类型做路由，本地工具，就给本地handler，MCP工具，就给MCP client。MCP client发请求到MCP server，server返回结果。

MCP server暴露的工具是通过schema描述的，schema由server提供，省去了手动编写。

大家说添加MCP，一般是说添加MCP server。

## skill

skill是针对特定任务的技能包，封装好了提示词、工具、知识、工作流。

skill包括以下内容，

触发条件：会提供一份简短描述，告诉模型“什么时候该用我”，让模型去判断。

提示词：做角色设定的。

知识：这个任务需要的专业知识，比如标准文档。

工具集：可以是本地工具，可以是MCP的工具，可以是另一个skill。会配置好schema和权限。

工作流：针对具体任务的执行步骤。


大模型比作大脑,MCP协议比作手,MCP插件比作工具,skill(可以是MCP插件和本地script脚本)比作操作经验
skills可以简单理解为大模型驱动的Workflow
## plugin

plugin可以封装skill/mcp/hook，方便分发。
