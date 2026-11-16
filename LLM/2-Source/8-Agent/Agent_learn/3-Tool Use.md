# 一、从 Chatbot 到 Agent
大语言模型最初主要以 Chatbot 的形式与用户交互，用户输入问题，模型根据已有知识和对话上下文生成回答。但模型本身无法直接获取实时信息，也无法操作外部系统。当用户希望查询 GitHub 上最新的 Issue、获取实时天气，甚至发送邮件、修改订单时，仅依靠文本生成已经无法完成这些任务。
![](Pasted%20image%2020261116100505.png)
Tool Use为大模型打开了与外部世界交互的通道，开发者可以向模型提供一组外部工具，让模型根据用户需求决定是否需要使用工具，并通过 Agent 执行相应操作。2023 年，OpenAI 推出 Function Calling 能力，随后 Anthropic、Google 等主流模型厂商也陆续支持类似机制。如今，Tool Use 已经成为构建 Agent 的基础能力，也是大模型从 Chatbot 走向 Agent 的重要一步。
# 二、Tool Use 是如何工作的？
模型为什么能够知道什么时候应该调用工具？又是如何生成正确的工具名称和参数的？这背后主要涉及模型训练和 API 调用两个环节。

## 1. 模型如何学会使用工具？
![](Pasted%20image%2020261116100532.png)
在模型训练阶段，通常会通过 SFT（监督微调）等后训练方式，让模型学习工具调用相关的行为，包括识别需要使用工具的场景、根据工具描述选择合适的工具，以及按照约定格式生成调用参数。

例如，在训练数据中，可能包含这样的交互：

用户：北京今天的天气怎么样？

模型：
```python
{
  "name": "get_weather",
  "arguments": {
    "city": "北京"
  }
}
```
模型通过大量类似的训练样本，逐渐学会在合适的场景下生成工具调用请求，并在获得工具执行结果后继续生成回答。

经过训练，模型就具备了通用的工具调用能力，Function Calling 这个名字容易让人误以为大模型能够直接调用和执行函数，实际上模型本身并没有直接执行外部函数的能力。它所做的事情是在判断需要使用工具时，生成一条结构化的调用请求，告诉 Agent 应该调用什么工具，以及需要传入哪些参数。真正找到函数、执行代码、调用外部 API 的，始终是 Agent 所在的应用程序。

换句话说，模型负责决定调用什么，Agent 负责真正执行。 Function Calling 描述的是模型生成函数调用请求的能力，而不是模型直接执行函数的能力。
## 2. Tool Use 的完整调用流程

理解了模型和 Agent 各自承担的职责，再来看一次完整的 Tool Use 是如何发生的。整个过程可以分为五个步骤：

1. **提供工具描述**：Agent 调用模型 API 时，将当前可用的工具名称、描述和参数 Schema 一起传给模型，让模型了解自己可以使用哪些能力。
2. **生成工具调用请求**：模型根据用户需求判断是否需要使用工具，如果需要，就返回包含工具名称和调用参数的结构化 Tool Call。
3. **执行工具**：Agent 接收到 Tool Call 后，根据工具名称找到对应的实现，解析参数并执行真正的函数或外部 API。
4. **反馈执行结果**：工具执行完成后，Agent 将结果按照模型 API 约定的格式重新组织，再次提交给模型。
5. **继续决策**：模型读取工具执行结果后，可以继续调用其他工具，也可以直接生成最终回答，结束本次任务。

整个过程可以用下面的时序图表示：
![](Pasted%20image%2020261116100609.png)
可以看到，模型和工具之间并不存在直接的调用关系，Agent 始终处于中间位置，负责接收模型的调用请求、执行工具以及反馈结果。理解这一点，就掌握了 Tool Use 最核心的工作机制。

# 三、动手实现一个 Tool Use Demo

理解了整体流程，我们直接使用模型 API 实现一个简单的天气查询 Agent，看看上面的过程在代码中是如何发生的。这里使用 OpenAI Python SDK，以 Chat Completions API 的 Function Calling 结构为例。

首先，定义一个天气查询工具，需要注意我们传给模型的并不是 Python 函数本身，而是一个描述工具能力的结构化 Schema：
```python
from openai import AsyncOpenAI
import asyncio
import json

client = AsyncOpenAI()

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询指定城市当前的天气信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "需要查询天气的城市名称"
                    }
                },
                "required": ["city"],
                "additionalProperties": False
            }
        }
    }
]
```
接下来，在 Agent 所在的应用程序中实现真正的天气查询函数：
```python
async def get_weather(city: str):
    # 实际项目中可以调用天气 API
    return {
        "city": city,
        "temperature": 22,
        "condition": "晴"
    }
```
然后编写 Agent 的执行逻辑：
```python
async def run_agent(user_input: str):
    messages = [
        {"role": "user", "content": user_input}
    ]

    while True:
        # 1. 请求模型
        response = await client.chat.completions.create(
            model="gpt-4.1",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        assistant_message = response.choices[0].message

        # 保存模型响应
        messages.append(
            assistant_message.model_dump(exclude_none=True)
        )

        tool_calls = assistant_message.tool_calls or []

        # 2. 没有工具调用，返回最终回答
        if not tool_calls:
            return assistant_message.content

        # 3. Agent 执行模型返回的工具调用
        async def execute_tool(call):
            try:
                args = json.loads(call.function.arguments)

                if call.function.name == "get_weather":
                    result = await get_weather(args["city"])
                else:
                    raise ValueError(
                        f"未知工具：{call.function.name}"
                    )

            except Exception as error:
                result = {"error": str(error)}

            return {
                "role": "tool",
                "tool_call_id": call.id,
                "content": json.dumps(
                    result,
                    ensure_ascii=False
                )
            }

        # 并行执行所有工具调用
        tool_results = await asyncio.gather(
            *(execute_tool(call) for call in tool_calls)
        )

        # 4. 将工具结果返回模型，进入下一轮
        messages.extend(tool_results)


async def main():
    result = await run_agent("北京今天的天气怎么样？")
    print(result)


asyncio.run(main())
```
这段代码已经实现了一个最小的 Tool Use Agent：应用程序首先将工具描述传给模型，模型根据用户问题生成调用请求，Agent 解析请求并执行对应函数，再将结果反馈给模型，直到模型生成最终回答。

其中，`while True` 实际上就是 Agent Loop 的最简单实现，模型可以根据每次工具执行的结果决定下一步行动，而应用程序则负责不断执行和反馈。

从代码中还可以看到，工具定义和工具实现是完全分离的。模型只需要知道工具的名称、描述和参数结构，并不需要了解具体的函数实现。这也是 Tool Use 能够将模型决策能力与外部系统解耦的关键。
# 四、模型一次返回多个工具调用，怎么办？

前面的 Demo 中有这样一行代码：
```python
tool_calls = assistant_message.tool_calls or []
```
为什么模型返回的是一个数组，而不是单个工具调用？

因为当用户提出一个比较复杂的需求时，模型可能判断需要同时使用多个工具。例如，用户要求分别查询北京和上海今天的天气，由于这两个查询相互独立，模型就可以在一次响应中同时返回两个 Tool Call：
```python
{
  "tool_calls": [
    {
      "id": "call_001",
      "type": "function",
      "function": {
        "name": "get_weather",
        "arguments": "{\"city\":\"北京\"}"
      }
    },
    {
      "id": "call_002",
      "type": "function",
      "function": {
        "name": "get_weather",
        "arguments": "{\"city\":\"上海\"}"
      }
    }
  ]
}
```
这两个请求调用的是同一个函数，只是参数不同。对于彼此独立的调用，Agent 没有必要等待第一个工具执行完成后再执行第二个，可以使用 Python 的 `asyncio` 实现并行处理。

我们先定义一个工具执行函数：
```python
async def execute_tool(call):
    args = json.loads(call.function.arguments)

    if call.function.name == "get_weather":
        result = await get_weather(args["city"])
    else:
        raise ValueError(f"未知工具：{call.function.name}")

    return {
        "role": "tool",
        "tool_call_id": call.id,
        "content": json.dumps(result, ensure_ascii=False)
    }
```
接下来，使用 `asyncio.create_task` 创建多个异步任务，再通过 `asyncio.as_completed` 获取执行结果：
```python
# 创建多个并行执行任务
tasks = [
    asyncio.create_task(execute_tool(call))
    for call in tool_calls
]

tool_results = []

# 按照实际完成顺序获取结果
for task in asyncio.as_completed(tasks):
    result = await task
    tool_results.append(result)

# 将所有工具结果返回模型
messages.extend(tool_results)
```
这里还有一个值得关注的细节，模型一次返回多个 Tool Call 时，Agent 如何知道每一份执行结果对应哪个调用请求？

假设北京的天气查询需要 2 秒，上海的天气查询只需要 1 秒，那么上海的查询结果就会先返回。如果我们简单地按照执行完成的顺序，将结果与原始调用顺序对应起来，就可能出现结果错配。

为了解决这个问题，每个 Tool Call 都会带有一个唯一的 ID，例如上面的 `call_001` 和 `call_002`。Agent 在执行工具时需要保留这个 ID，并在返回执行结果时通过 `tool_call_id` 将它带回去。

例如，最终得到的结果可能是：
```python
[
  {
    "role": "tool",
    "tool_call_id": "call_002",
    "content": "{\"city\":\"上海\",\"temperature\":25}"
  },
  {
    "role": "tool",
    "tool_call_id": "call_001",
    "content": "{\"city\":\"北京\",\"temperature\":22}"
  }
]
```
即使结果返回顺序发生变化，也可以通过 ID 准确关联原始请求与执行结果，不需要依赖数组下标或者执行顺序。

当然，并不是所有工具调用都可以并行执行。例如，查询订单之后才能根据订单 ID 查询物流信息，再根据物流信息决定是否申请退款。这些操作之间存在依赖关系，需要 Agent 先执行前一步，再将结果交给模型决定下一步行动。

因此，模型既可以在一次响应中提出多个独立的工具调用，也可以通过多轮交互逐步完成具有依赖关系的任务。
# 五、不同模型厂商的 Tool Use 使用方式并不相同

到这里，我们已经掌握了 Tool Use 的基本原理，也实现了一个简单的 Agent。但如果希望自己的 Agent 同时支持 OpenAI、Claude 和 Gemini 等不同模型，就会遇到一个实际的工程问题：虽然各家模型都支持 Tool Use，但它们在 API 中定义工具、返回调用请求以及反馈执行结果的方式并不相同。

## 1. OpenAI：Function Calling

OpenAI 使用 `tools` 定义可用工具。模型返回工具调用时，会在响应中包含 `tool_calls` 数组，其中包含工具名称、参数和调用 ID：
```python
{
  "tool_calls": [
    {
      "id": "call_001",
      "type": "function",
      "function": {
        "name": "get_weather",
        "arguments": "{\"city\":\"北京\"}"
      }
    }
  ]
}
```
Agent 执行完成后，通过 `role: "tool"` 和 `tool_call_id` 将结果反馈给模型。

### 2. Anthropic：Tool Use

Claude 使用自己的工具定义结构，参数 Schema 使用 `input_schema`。模型返回的工具调用是 Assistant 消息中的 `tool_use` 内容块：
```python
{
  "type": "tool_use",
  "id": "toolu_001",
  "name": "get_weather",
  "input": {
    "city": "北京"
  }
}
```
执行完成后，通过 `tool_result` 内容块返回结果，并使用 `tool_use_id` 关联原始调用：
```python
{
  "type": "tool_result",
  "tool_use_id": "toolu_001",
  "content": "{\"temperature\":22}"
}
```
## 3. Google Gemini：Function Calling

Gemini 使用 `functionDeclarations` 定义可用函数，模型返回的内容中包含 `functionCall`：
```python
{
  "functionCall": {
    "id": "call_001",
    "name": "get_weather",
    "args": {
      "city": "北京"
    }
  }
}
```
执行完成后，通过 `functionResponse` 返回结果，并关联对应的调用 ID：
```python
{
  "functionResponse": {
    "id": "call_001",
    "name": "get_weather",
    "response": {
      "temperature": 22
    }
  }
}
```
因为不同模型在工具定义、参数结构、调用请求和返回结果等方面都有自己的规范。Agent 开发者需要编写适配层，才能让同一套 Agent 逻辑运行在不同模型之上。
# 六、兼容之殇

模型兼容只是 Agent 兼容的一部分，工具接入也有类似的问题。GitHub、数据库、搜索引擎、邮件系统等外部服务，各自的工具描述方式、参数结构、返回值、通信协议和鉴权方式都不一样。Agent 开发者需要逐个适配这些工具；而站在工具开发者的角度，如果希望自己的工具能够被不同的 Agent、Host 或框架使用，也需要针对不同平台提供适配。

这样一来，Agent 开发者既要兼容不同模型，又要接入各种异构工具；工具开发者也要适配不同的 Agent。双方都需要投入大量重复的适配工作，随着模型和工具越来越多，兼容成本也会不断增加，形成典型的 **M × N 问题**。
![](Pasted%20image%2020261116101033.png)
有没有一种统一的协议，让 Agent 能够以标准化的方式发现和调用不同来源的工具，而不需要为每个工具单独实现一套接入逻辑？这就是下一节我们要介绍的 MCP。
# 总结

Tool Use 让大模型具备了使用外部工具的能力，是 Agent 能够与外部世界交互的基础。

模型通过训练学习工具调用行为，在推理时根据开发者提供的工具描述生成结构化调用请求；Agent 接收请求并执行工具，再将执行结果反馈给模型，让模型根据真实结果继续决策。

**模型负责决策，Agent 负责执行，工具负责提供外部能力。**

理解这套机制之后，我们就能够进一步思考如何设计工具、如何组织多工具调用，以及如何解决不同模型和外部工具之间的接入差异。