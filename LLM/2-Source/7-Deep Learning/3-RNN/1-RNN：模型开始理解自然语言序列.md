# RNN：模型开始理解自然语言序列

## 词向量有了，句子仍然没有被理解

> [!abstract] 核心观点
> **Embedding** 已经把每个 token 转换成可计算的词向量，但它解决的只是**单个 token 如何表示**。
> 把一串词向量摆在一起，并不等于模型已经理解句子。

## 为什么仅靠词向量不够？
文本模型不仅要知“有哪些词”，还要利用**词序**和**上下文**。以下三个例子说明了这一点：

### 1. 否定词改变情感方向
- 句子 A：`我 喜欢 这部 电影`
- 句子 B：`我 不 喜欢 这部 电影`
- **结论**：只多一个“不”，情感方向就反转。

### 2. 语序改变主客体关系
- 句子 A：`孙悟空 打 白骨精`
- 句子 B：`白骨精 打 孙悟空`
- **结论**：词没有变，主客体关系完全不同。

### 3. 上下文消除歧义
- 句子 A：`苹果 发布 新产品`
- 句子 B：`我 吃了 一个 苹果`
- **结论**：同一个词（如“苹果”），需要上下文消除歧义。

---
> [!important] 总结
> 文本模型不仅要知“有哪些词”，还要利用**词序**和**上下文**。

## 先回顾：什么是前馈神经网络
> [!info] 定义
> **前馈神经网络** (Feedforward Neural Network, **FNN**) 是一类信息单向传播的网络。
> 数据从输入层出发，依次经过隐藏层到达输出层，网络内部**没有循环连接**。此前学过的多层感知机（MLP）就是典型的 FNN。
## 网络结构
- **输入层**（接收特征） ➔ **隐藏层**（逐层变换） ➔ **隐藏层**（提取特征） ➔ **输出层**（给出预测）
---
> [!warning] 核心痛点
> 这种结构**并不适合直接处理自然语言序列**。
主要有以下两个原因：
### 原因一：前后依赖
- 一次性处理整段输入，**没有沿时间建模上下文的机制**。
### 原因二：变长序列
- 输入维度必须预先固定，**长短不一的句子难以对齐**。
## 原因一：FNN 无法建模前后依赖

## ① 难以建模序列的前后依赖

**例句：我 去 银行 存钱**

> 💡 **关键点**：“银行” 的含义需要结合前文 “去” 才能确定。

---

### FNN (MLP) 一次性接收整个输入

![](../../../../image/Pasted%20image%2020261027095554.png)

> [!danger] ❌ 核心缺陷
> **没有机制捕捉前后顺序和依赖关系**
> **把序列当作一个固定向量处理**

## 📝 总结与说明

序列中的内容存在**前后依赖** —— 一个词的含义，往往要结合前文才能确定。

但 FNN 会把整段输入当作一个**固定向量一次性处理**，结构中没有专门处理时序关系的机制，因此不擅长建模这种前后关联。

## 原因二：变长序列难以对齐固定输入
## ② 难以处理不固定长度的序列
**问题现象：句子长度不固定**
- 句子1: `我 喜欢 吃 苹果` （长度 = 4）
- 句子2: `今天天气 很 好 呀` （长度 = 5）
- 句子3: `我 昨天 看了 一部 很好 的 电影` （长度 = 8）
![](../../../../image/Pasted%20image%2020261027095802.png)
---
**FNN 的解决方案：** FNN 需要固定维度输入，只能通过**截断**或**填充**对齐。
### 方法一：截断 (Truncation)
- **规则**：设定最大长度为 5
- **示例**：`我 | 昨天 | 看 | 了 | 一部 | ✂️(很) | ✂️(好) | ✂️(的) | ✂️(电影)`
- **缺陷**：❌ 丢失后续信息
### 方法二：填充 (Padding)
- **规则**：设定固定长度为 8
- **示例**：`我 | 喜欢 | 吃 | 苹果 | PAD | PAD | PAD | PAD | PAD`
- **缺陷**：❌ 引入大量无意义的填充信息
> [!danger] 综合后果
> ❌ 会造成信息丢失，或引入噪声，影响模型学习效果。
---
## 📝 核心总结
| 痛点          | 说明                 |
| :---------- | :----------------- |
| **句子长短不一**  | 文本、语音和时间序列都没有统一长度。 |
| **截断会丢信息**  | 超过最大长度的内容只能被舍弃。    |
| **补齐会引入空位** | 短句需要大量没有实际语义的填充。   |
## RNN 改变的不是词向量，而是读取方式
> **核心思想**：RNN 不会先把整个句子拼成固定向量，而是**从左到右逐个读取 token**。
---
![](../../../../image/Pasted%20image%2020261027100945.png)
## 📌 RNN 的读取机制
1. 读第一个词，只能根据当前输入形成初始状态。
2. 读第二个词，把新词与上一步留下的状态结合。
3. 读第三个词时，前两步积累的信息继续参与计算。
4. 重复这一过程，直到整个序列处理完毕。
## 隐藏状态：前文的压缩摘要
隐藏状态其实就是一个**向量**——模型算出的一组浮点数，信息由多个维度共同表达，而非一维对应一个语法概念。
```text
h1 = [ 0.20, -0.10, 0.05, 0.81]
h2 = [ 0.44, -0.35, 0.62, 0.12]
h3 = [ 0.10, -0.70, 0.88, -0.20]

```
$$
h_t=f(x_t,h_{t−1})
$$
$x_t$​ 是当前位置输入，$h_{t−1}​$ 是此前形成的状态，$h_t$​ 是读完当前位置后的新状态。

| 状态        | 前文理解           | 当前读入  | 计算过程           |
| --------- | -------------- | ----- | -------------- |
| h₀ = 初始状态 |                |       |                |
| t=1       | 尚无前文           | 读“我”  | h₁ = f(x₁, h₀) |
| t=2       | 已理解“我”         | 读“不”  | h₂ = f(x₂, h₁) |
| t=3       | 已理解“我 不”       | 读“喜欢” | h₃ = f(x₃, h₂) |
| t=4       | 已理解“我 不 喜欢”    | 读“这部” | h₄ = f(x₄, h₃) |
| t=5       | 已理解“我 不 喜欢 这部” | 读“电影” | h₅ = f(x₅, h₄) |

> 读到“我 不 喜欢”时，h3h3​ 可能已经综合了主语、否定与评价词之间的关系。

## RNN Layer: 同一个 Cell 沿序列循环调用

![](../../../../image/Pasted%20image%2020261027101911.png)

图中看似有多个 Cell，其实是**同一个 RNN Cell** 在不同时间步上的重复使用。

任务头放在循环内，就会每步输出；放在循环外，就只读取最后状态。

> 序列有多长，循环就执行多少次。

```python
h = [0] # 初始化隐藏态

# 循环调用 RNNCell，处理序列中的每个 token，暂存到隐藏...
while x[t] != eos:
    # 利用上一步计算的隐藏态，计算当前时间步的隐藏态
    h.append(RNNCell(x[t], h[t - 1]))
    t += 1

# 如果只需要最后做预测，就在循环外调用任务头
output = task(h[-1])
```
## 局部视角：一个 Cell 只完成一次状态更新

$$
\text{RNNCell}(x_t, h_{t-1}) \rightarrow h_t
$$

- $x_t$ 当前 token 的词向量，是当前时间步的新信息
- $h_{t-1}$ 此前已经积累的上下文。

Cell 把两者合并成新状态 $h_t$，完成**一次**状态更新；下一位置再调用同一个 Cell。
一个 Cell 是局部计算单元；沿整段序列循环调用，才构成 RNN Layer。

---
![](../../../../image/Pasted%20image%2020261027102330.png)
## 参数共享：每一步复用同一组权重

RNN 沿序列多次更新状态，但每一步用的都是同一个 RNN Cell——也就是同一组权重参数。

---

 RNN: 每步复用同一个 $f$
$$
f \rightarrow f \rightarrow f \rightarrow \cdots
$$
所有时间步共用一组权重 $W_{xh}, W_{hh}, b$，反复计算 $h_t = f(x_t, h_{t-1})$，就像循环里调用同一个函数。
---

### 若每步各用一套参数
$$
f_1 \rightarrow f_2 \rightarrow f_3 \rightarrow \cdots
$$

序列每多一个位置就多一套参数，模型也只能处理预先规定好的长度。

---

### 参数共享带来两个关键好处：
#### ① 参数量与句长解耦
句子变长只是多循环几次同一个 Cell，**参数规模保持不变**。
> 5 / 10 / 100 次调用 $\rightarrow$ 同一组 
#### ② 一套规则通吃任意长度
无论 5 个、10 个还是上百个 token，都用**相同的更新规则**逐步处理，无需改变结构。

---
> **正是因为参数共享，RNN 才真正获得了处理不定长序列的能力。**

## RNN 更新状态，任务头决定在哪里输出

RNN 每一步都会产生隐藏状态，但**输出几次、在哪里输出**，取决于具体任务，常见的输出方式大致有三类：
![](../../../../image/Pasted%20image%2020261027103228.png)
---
### 1. 整体分类
$$
 \hat{y} = g(h_T) 
$$
读完整段序列，只在最后输出一次；损失来自整体标签。

---
### 2. 序列标注
$$
 \hat{y}_i = g(h_i) 
$$
每个 token 都输出标签；补齐位置通过 mask 排除。

---
### 3. 序列生成
$$
 P(w_{t+1} | h_t) 
$$
每个位置预测下一个 token；汇总所有有效位置的损失。

---

任务头 $g$ 可以是线性层、MLP、softmax 分类器，也可以是更复杂的结构。

## 整体分类：只在最后输出一次

输入是一整段序列，输出是一个整体标签。比如情感分类，读入一句影评，只需判断整句的情感倾向。

> **核心思路**：读完整段序列，只取最后状态 `h_n[-1]` 交给分类器，输出一个整体标签。

---

### 示例
- **输入**：我 不喜欢 这部 电影
- **输出**：负面

情感分类、垃圾邮件识别、新闻分类都只需一个整体标签，读完整个序列后只输出一次，任务头接在最后一个隐藏状态 $h_T$ 上。

> 中间状态仍参与信息传递，只是任务头最终只读取 $h_T$。

---

### 代码实现示例

```python
class RNNClassifier(nn.Module):
    def __init__(self, vocab_size, embed_dim, hidden_dim, num_classes):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.rnn = nn.RNN(embed_dim, hidden_dim, batch_first=True)
        self.classifier = nn.Linear(hidden_dim, num_classes)

    def forward(self, token_ids):
        x = self.embedding(token_ids)        # [batch, seq_len, embed_dim]
        states, h_n = self.rnn(x)            # states: 每步状态; h_n: 最后一步状态 [batch, hidden_dim]
        h_last = h_n[-1]                     # 只取最后状态 [batch, hidden_dim]
        logits = self.classifier(h_last)     # 整段 -> 一个标签 [batch, num_classes]
        return logits
```
## 序列标注：每个位置都输出标签

输入是一串 token，输出也是一串标签，且**位置一一对应**。比如词性标注，每个词都要得到自己的词性标签。

> **核心思路**：每个时间步的状态都过同一个分类器，逐位置输出标签，形状 `[batch, seq_len, tags]`。
---
### 示例：词性标注
- **输入**：我 不 喜欢 电影
- **输出**：代词 副词 动词 名词

词性标注、命名实体识别每个位置都需要预测，同一个任务头作用在每个时间步的 $h_t$ 上；补齐产生的 `[PAD]` 通过 mask 排除。

> 多个位置的损失，共同更新同一个 RNN Cell 和分类器。
---
### 代码实现示例

```python
class RNNTagger(nn.Module):
    def __init__(self, vocab_size, embed_dim, hidden_dim, num_tags):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.rnn = nn.RNN(embed_dim, hidden_dim, batch_first=True)
        self.classifier = nn.Linear(hidden_dim, num_tags)

    def forward(self, token_ids):
        x = self.embedding(token_ids)        # [batch, seq_len, embed_dim]
        states, h_n = self.rnn(x)            # 保留“每个时间步”的状态
        logits = self.classifier(states)     # 逐位置输出 [batch, seq_len, num_tags]
        return logits
```
## 序列生成：每个位置预测下一个 token

语言模型的输入是一段已出现的文本，输出是下一个 token 的概率分布。训练时把同一句话错开一位，让每个位置学习预测后面的词。

> **核心思路**：与序列标注同构，但输出维度换成词表大小，每个位置都预测下一个 token。

---

### 示例：训练数据错位

| 类型 | 序列 |
| :--- | :--- |
| **输入** | 我 不 喜欢 这部 |
| **目标** | 不 喜欢 这部 电影 |

任务头作用在每个时间步，但输出维度变成**词表大小**，每个位置的隐藏状态用来预测下一个 token。

> 所有有效位置的交叉熵会合并，再沿时间链反向传播。

---

### 代码实现示例

```python
class RNNLanguageModel(nn.Module):
    def __init__(self, vocab_size, embed_dim, hidden_dim):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.rnn = nn.RNN(embed_dim, hidden_dim, batch_first=True)
        self.lm_head = nn.Linear(hidden_dim, vocab_size)

    def forward(self, token_ids):
        x = self.embedding(token_ids)        # [batch, seq_len, embed_dim]
        states, h_n = self.rnn(x)            # 保留每个时间步的状态
        logits = self.lm_head(states)        # 每个位置预测下一词 [..., vocab_size]
        return logits
```
## 三类任务，共用同一条训练链

三类任务的输出方式不同，但训练流程是一致的：先沿时间步前向，再由损失沿原路反向传回。

**训练流程**：
`1 沿序列前向` ➔ `2 任务头输出` ➔ `3 计算有效位置损失` ➔ `4 沿状态链反向传播`

---

### 梯度的回传路径
损失从输出出发，沿着 **任务头** ➔ **隐藏状态链** ➔ **Embedding** 一路传回，每个时间步都会收到梯度。

### 梯度的累加与更新
同一个 Cell 在多个时间步共享参数，不同位置的梯度会**累加**到同一组参数，最后由优化器统一更新。

---

> **无论哪类任务，最终都归结为同一件事：把梯度沿时间链传回共享的参数。**

## Demo: 把句子变成一道道“下一词预测题”

给定已经出现的词，预测下一个词。对序列 $w_1, \dots, w_t$，模型在**每个位置**都要估计下一个 token 的概率分布：

### 概率公式
$$
 P(w_{t+1} \mid w_1, w_2, \dots, w_t) 
$$
每个有效位置都是一次**词表分类**：读到的上下文越具体，下一词的分布越集中。

---

### 训练数据构造示例

| 分类 | 序列内容 |
| :--- | :--- |
| **原句** | 我 \| 喜欢 \| 吃 \| 苹果 \| `<EOS>` |
| **输入** | 我 \| 喜欢 \| 吃 \| 苹果 |
| **目标** | 喜欢 \| 吃 \| 苹果 \| `<EOS>` |

目标就是原句**整体左移一位**：一句话内部天然形成多道训练题。

---

### 整体流程

- **01** 读语料
- **02** 建词表
- **03** 做训练对
- **04** 定义模型
- **05** 训练
- **06** 预测/生成

## ① 准备语料与训练对

**核心思路**：读取准备好的语料、建立词表，再把每个 batch 的输入与目标错开一位，用 `<PAD>` 补齐对齐成同一形状。
### 特殊 Token 说明
- `<PAD>`  
    补齐 batch 里的短句，算损失时被忽略
- `<UNK>`  
    代表词表里没有的词
- `<EOS>`  
    标记句子结束，让模型学会何时停下

> 输入与目标同源，只差一位，一句话就拆成多道预测题。
### 代码实现

```python
import random
from pathlib import Path
import torch
from torch import nn
from torch.nn.utils.rnn import pad_sequence  # 把变长序列补齐成同一长度

# ---------- 1) 读取语料 ----------
# 语料每行一句话，词与词之间已用空格分好
lines = corpus_path.read_text(encoding="utf-8").splitlines()
# 丢掉空行，再按空格切成 token 列表：["我", "喜欢", ...]
sentences = [s.split() for s in lines if s.strip()]

# ---------- 2) 建立词表 ----------
# 三个特殊 token 固定放在最前，保证它们的 id 稳定
PAD, UNK, EOS = "<PAD>", "<UNK>", "<EOS>"   # 补齐 / 未知词 / 句子结束
# 其余词去重后排序，接在特殊 token 之后组成词表
vocab = [PAD, UNK, EOS] + sorted(
    {w for s in sentences for w in s})
word_to_id = {w: i for i, w in enumerate(vocab)}         # 词 -> 整数 id
id_to_word = {i: w for w, i in word_to_id.items()}       # id -> 词（预测时反查）
pad_id = word_to_id[PAD]                                 # 记下 <PAD> 的 id
# ---------- 3) 制作训练对 ----------
# 每句话末尾补一个 <EOS>，让模型学会“何时停下”
encoded = [torch.tensor(
    [word_to_id[w] for w in s] + [word_to_id[EOS]])
    for s in sentences]
# 输入去掉最后一个词、目标去掉第一个词 -> 两者天然错开一位
# 例: 输入「我 喜欢 吃 苹果」/ 目标「喜欢 吃 苹果 <EOS>」
inputs = pad_sequence([e[:-1] for e in encoded],
    batch_first=True, padding_value=pad_id)            # 同一 batch 内短句用 <PAD>
targets = pad_sequence([e[1:] for e in encoded],
    batch_first=True, padding_value=pad_id)
```

## ② 定义模型：Embedding + RNN + Linear

> **核心思路**：把 Embedding、RNN、Linear 三层串起来：token 序列 $\rightarrow$ 词向量 $\rightarrow$ 每步隐藏状态 $\rightarrow$ 每步的词表分数。
### 模块解析

- **Embedding**  
    把离散 token ID 变成稠密词向量；`padding_idx` 让 `<PAD>` 向量恒为零。
- **RNN**  
    沿序列逐步更新隐藏状态，输出每个时间步的 htht​。
- **Linear**  
    把每个 htht​ 映射到词表大小的分数，即下一词的 logits。
---
### 代码实现

```python
class NextWordRNN(nn.Module):
    def __init__(self, vocab_size,
                 embed_dim=48, hidden_dim=96):
        super().__init__()
        # 词嵌入层：token id -> embed_dim 维词向量
        # padding_idx=pad_id 让 <PAD> 的向量恒为零，且不参与更新
        self.embedding = nn.Embedding(
            vocab_size, embed_dim, padding_idx=pad_id)
        # RNN 层：沿序列逐步更新隐藏状态
        # batch_first=True -> 输入形状为 [batch, seq_len, embed_dim]
        self.rnn = nn.RNN(
            embed_dim, hidden_dim, batch_first=True)
        # 输出层：把每一步的隐藏状态映射成词表上的分数 logits
        self.output = nn.Linear(hidden_dim, vocab_size)

    def forward(self, token_ids):
	    # token_ids: [batch, seq_len]
	    embeddings = self.embedding(token_ids)    # [batch, seq_len, embed_dim]
states, _ = self.rnn(embeddings)          # [batch, seq_len, hidden_dim]
return self.output(states)                # [batch, seq_len, vocab_size]
```

## ③ 训练 & 预测与生成

---

### 训练：每个位置一道分类题

**核心思路**：把每个有效位置当成一道分类题，用交叉熵（忽略 `<PAD>`）反复前向、反向，更新同一组参数。

```python
# 交叉熵损失；ignore_index=pad_id 让补齐位置不计入损失
criterion = nn.CrossEntropyLoss(ignore_index=pad_id)
# Adam 优化器，学习率 0.01
optimizer = torch.optim.Adam(
    model.parameters(), lr=0.01)

for epoch in range(1, 10001):
    logits = model(inputs)                   # 前向: [B, T, V]=[批...
    # 把 logits 摊平成 [B*T, V]、目标摊平成 [B*T]
    # 于是每个时间步都成为一道独立的“下一词分类题”
    loss = criterion(
        logits.reshape(-1, len(vocab)),
        targets.reshape(-1))
    optimizer.zero_grad()                    # 清空上一轮累积的梯度
    loss.backward()                          # 反向传播：梯度沿时间链...
    optimizer.step()                         # 按梯度更新参数
```
### 预测：取最后一步、softmax、Top-k

**核心思路**：只看最后一步的分布，softmax 后取 Top-k；反复取 Top-1 追加回序列，就是贪心生成。
```python
@torch.no_grad()                             # 预测阶段不需要...
def predict_next(prefix, top_k=5):
    # 把前缀里的词转成 id，不在词表里的词用 <UNK> 兜底
    ids = [word_to_id.get(w, word_to_id[UNK])
           for w in prefix.split()]
    # 前向后只取“最后一个时间步”的输出 -> 紧接前缀的下一词分布
    logits = model(torch.tensor([ids]))[0, -1].clone()
    logits[pad_id] = -torch.inf              # 不允许生成 <PAD>
    logits[word_to_id[UNK]] = -torch.inf     # 不允许生成 <UNK>
    probs = torch.softmax(logits, dim=-1)    # 分数 logits...
    v, i = torch.topk(probs, top_k)          # 取概率最高的...
    return [(id_to_word[j].item(), p.item())
            for p, j in zip(v, i)]

def generate(prefix, max_new_words=8):       # 贪心生成：每...
    words = prefix.split()
    for _ in range(max_new_words):
```
## 固定维度的隐藏状态，也是一条信息瓶颈

不管序列多长，RNN 每一步都要把**当前输入**和**全部过去**重新压缩进同一个固定维度的隐藏状态里。

---
### 序列越长，压缩比越高

- $5 个 token \rightarrow h \in \mathbb{R}^{128}$
- $50 个 token \rightarrow h \in \mathbb{R}^{128}$
- $500 个 token \rightarrow h \in \mathbb{R}^{128}$
> 右侧容器始终一样大——这就是瓶颈所在。

---

短句中，这份摘要**可能足够**；序列变长后，早期信息更容易被后续输入**覆盖**。

> **RNN 保存的是任务相关摘要，不是对历史内容的无损备份。**

## 序列变长后，RNN 会遇到三类困难

### 1. 表示容量

当前输入不断写入固定维度状态
$\downarrow$
早期内容逐渐弱化或被覆盖
$\downarrow$
**长距离信息难以保留**

### 2. 优化路径

末端损失沿时间链反向传播
$\downarrow$
反复经过矩阵乘法和非线性
$\downarrow$
**梯度消失或爆炸**

### 3. 计算效率

$h_{t+1}$ 必须等待 $h_t$
$\downarrow$
同一序列只能逐步递推
$\downarrow$
**难以并行、训练速度受限**

---
> RNN 解决了“如何沿序列传递上下文”，却没有彻底解决长序列中的记忆、优化与效率问题。

## RNN 之后，序列建模继续解决这些问题

| 结构                  | 针对的问题          | 核心改动                    |
| :------------------ | :------------- | :---------------------- |
| **LSTM / GRU**      | 长期依赖难保留，梯度容易消失 | 引入门控，选择性地保留、遗忘和写入信息     |
| **Encoder-Decoder** | 输入序列与输出序列长度不同  | 把“读入”与“生成”组织成完整的序列到序列映射 |
| **Attention**       | 全部信息被压进固定长度状态  | 预测时直接访问输入中的相关位置，缓解信息瓶颈  |
| **Transformer**     | 递推依赖导致序列内部难以并行 | 以自注意力替代循环递推，统一建模全局关系    |
## RNN 的能力与局限

### RNN 建立了什么
- [x] 用同一套参数处理不定长序列
- [x] 沿时间步传递和更新上下文
- [x] 统一整体分类、序列标注和生成
- [x] 让序列建模进入可端到端训练的框架

### RNN 仍未解决什么
- [-] 固定状态带来的信息瓶颈
- [-] 长距离信息容易被覆盖
- [-] 梯度消失与梯度爆炸
- [-] 逐步递推造成的并行瓶颈

---

> RNN 定义了序列建模的基本问题；LSTM 与 GRU 将先从“怎样让状态记得更久”开始改进。
