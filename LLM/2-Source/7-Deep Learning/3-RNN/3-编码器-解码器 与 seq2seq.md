# 编码器-解码器 与 seq2seq

## RNN 擅长序列到单值任务

> **输入**: `I love this movie.`
> **输出**: `Positive`
$$
h_t = f(x_t, h_{t-1}), \quad \hat{y} = g(h_T)
$$
---

RNN 读到最后一个 Token 后，隐藏状态 $h_T$ 已经汇总了与分类任务有关的信息，交给全连接层 $g$ 就能预测整段文本的情感类别。

输入文本可以有不同长度，但模型只在读完整条序列后进行**一次预测**，情感分类、新闻分类、垃圾邮件识别都属于这一类。

> 一个输入序列对应一个任务输出，称为序列到单值 (Sequence-to-One)。

## 现实任务：输入和输出都是序列

现实中存在大量输入、输出都是序列的任务，Sequence-to-One 结构只能产生一个任务输出，无法直接完成它们。

| 任务 | 输入 | 输出 |
| :--- | :--- | :--- |
| **机器翻译** | 英文句子 | 中文句子 |
| **文本摘要** | 长文章 | 摘要 |
| **对话系统** | 用户输入 | 回复内容 |
| **语音识别** | 音频序列 | 文本序列 |

> 可能有同学会说：在 RNN 的每个隐藏状态上都接一个任务头，模型不就可以输出一个序列了吗？

## 序列标注：每个隐藏状态后接一个任务头
### 示例：词性标注
- **输入**：我 不 喜欢 电影
- **输出**：代词 副词 动词 名词
---
![](../../../../image/Pasted%20image%2020261027180705.png)
第 $t$ 个输出对应第 $t$ 个输入，输入有多少个 Token 就输出多少个标签——前面用 RNN 识别词性正是**序列标注** (Sequence Labeling) 的做法。
由于输入与输出有**相同的长度和位置关系**，把任务头放在每个隐藏状态后面就能完成这类任务。
## 机器翻译：语序变化打乱位置对应

### 示例对比
- **英文**：There is a cat **under the table**.
- **中文**：**桌子下面**有一只猫。

---

“**under the table**” 被译成「**桌子下面**」并移到句首；在每个输入位置接任务头，等于预设第 $t$ 个输入对应第 $t$ 个输出，无法完成这类任务。
![](../../../../image/Pasted%20image%2020261028094956.png)
> **核心结论**
> 模型需要让输入序列与输出序列拥有彼此独立的长度和时间轴。

## 2014: RNN Encoder-Decoder 登场

2014 年前后，统计机器翻译 (Statistical Machine Translation, SMT) 会从短语表中寻找并组合候选译文，其中一个关键环节，是判断一个源语言短语与一个目标语言短语有多匹配。本吉奥团队在研究如何改进 SMT 时，尝试把这种匹配关系交给神经网络学习。

| GRU ① · 编码 | ➔ | GRU ② · 解码 |
| :--- | :---: | :--- |
| 读完源语言短语，将其压缩成一个固定维度向量 | | 根据这个向量，逐步生成目标语言短语 |

前一个 GRU 负责编码，后一个 GRU 负责解码，这就是 RNN Encoder-Decoder。它给短语对计算一个分数，再把分数交给原有的 SMT 系统，帮它从候选结果中选出更合适的翻译。

> 此时完整译文仍由 SMT 系统生成，Encoder-Decoder 只是其中的一个辅助打分模块。

## 同年：Seq2Seq 把短语扩展成完整句子

同年，来自谷歌的 Ilya Sutskever 等人沿用「先编码、再解码」的思路，把处理对象从短语扩展到了**完整句子**：相比 RNN Encoder-Decoder 的单层 GRU，编码器和解码器都改用 4 层 LSTM，编码器先读完整个源句，解码器再逐词生成译文——这套架构被称为**序列到序列** (Sequence-to-Sequence, Seq2Seq)。

---
![](../../../../image/Pasted%20image%2020261028100349.png)
---

> **核心突破**
> Seq2Seq 直接从双语句对中学习生成译文，将原本服务于 SMT 的辅助打分模块，推进为可以独立完成整句翻译的神经网络系统，证明了纯神经网络可以不依赖传统 SMT 独立完成机器翻译任务。

## Seq2Seq 工作流程：一次完整的生成

### 核心步骤

1. **编码**：读取全部输入 Token，得到最终上下文 $c$
2. **初始化**：用 $c$ 初始化解码器状态 $s_0$
3. **起步**：接收 `<BOS>`，预测第一个目标 Token
4. **接力**：预测结果作为下一步输入
5. **自回归**：不断重复，持续向后生成
6. **停止**：输出 `<EOS>` 或达到长度上限

> *编码器与解码器通常独立用 LSTM 或 GRU 实现。*

---
![](../../../../image/Pasted%20image%2020261028100613.png)

---

> **核心特征**
> 输入在编码器内部加工，输出在解码器内部推进——两条时间轴不必等长，也不必逐位置对齐。

## 模型训练不能用自身预测

若训练始终使用模型自己的预测，第一个位置产生的错误会改变第二个位置的输入，后面的误差很快叠加，模型很难学到稳定的目标序列规律。
![](../../../../image/Pasted%20image%2020261028102035.png)

> [!example] 错误累积示例
> **目标译文**：我 喜欢 深度 学习
> **一路错下去**：我 想 深入 反思

而在监督学习中，训练时我们**已经知道正确的翻译结果**——没有理由不用它。
## Teacher Forcing：把目标序列错开一位
训练第 $t$ 步时，无论模型在第 $t-1$ 步预测了什么，都把**真实的 $y_{t-1}$** 作为当前输入。实现上只需把目标序列整体右移一位作为解码器输入，原始目标序列作为监督标签。
### 输入与目标错位示例
```text
解码器输入： <BOS>  我    喜欢   深度   学习
监督目标：     我    喜欢   深度   学习  <EOS>
```
---

### 每个时间步的输入与标签对应关系

|解码器输入|Label|
|---|---|
|`<BOS>`|我|
|`<BOS>` 我|喜欢|
|`<BOS>` 我 喜欢|深度|
|`<BOS>` 我 喜欢 深度|学习|
|`<BOS>` 我 喜欢 深度 学习|`<EOS>`|

---

> 每一个位置上，解码器实际学习的是**根据前面的真实 Token 预测下一个 Token**。

## Teacher Forcing 改变输入，不改变损失

![](../../../../image/Pasted%20image%2020261028103852.png)
---

解码器始终接收真实的历史 Token，避免错误不断累积；前向传播后，每个位置的预测与对应 Label 分别计算**交叉熵损失**，求和（或平均）后反向传播更新参数。

---

> Teacher Forcing 不会改变损失函数，它改变的是解码器每个时间步的输入内容。

**核心技巧：输入顺序反转**  
通过将源语言的输入序列进行反转，来缩短机器翻译中的依赖路径。
![](../../../../image/Pasted%20image%2020261101082524.png)
**1. 原理与机制**

- **普通顺序的问题**：源句开头的Token（如“I”）最早进入编码器，但解码器最先需要生成的对应Token（如“我”）是在编码器处理完整个序列后才开始的。这导致信息传递路径较长，存在长距离依赖。
    
- **反转后的优势**：将源句反转后，源句开头的Token（如“I”）会在编码末尾才进入模型。这样，它与解码器最先生成的Token（如“我”）在时间/空间上的距离就变得非常近。
    

**2. 示例**

- **原始源句**：I like deep learning
    
- **反转之后**：learning deep like I
    
- **目标句**：我 喜欢 深度 学习（保持不变）
    

**3. 作用与局限**

- **优势**：该技巧虽然没有消除RNN（循环神经网络）本身的循环依赖，但**缩短了许多源语言与目标语言Token之间的依赖路径**，从而让深层LSTM更容易学习两者之间的对应关系。
## 动手实验：从零训练迷你英中翻译模型

**实验目标**：使用 PyTorch 从零训练一个迷你英中翻译模型，使其学习两类句式，其中包含发生明显语序变化的句式。

## 一、 学习的句式示例

- **句式一（语序变化）**
    
    - **EN**: there is a quiet duck next to the door
        
    - **ZH**: 门 旁边 有 一只 安静 鸭子
        
- **句式二（顺序一致）**
    
    - **EN**: alice has two red apples
        
    - **ZH**: 爱丽丝 有 两 个 红色 苹果
        
## 二、 数据集构建与划分

- **数据来源**：用动物、颜色、位置、物体和数量组合出 **3,840 组**受控句对。
    
- **划分比例**：按 **8:1:1** 划分训练集 / 验证集 / 测试集。
    
- **数据特点**：每个完整句子只出现一次——测试句从未在训练集中原样出现，但组成它的**词**和**句式模板**都能从训练数据中学到。
    
## 三、 核心验证环节

1. **验证 1**：编码器读取变长英文，生成一个固定维度状态。
    
2. **验证 2**：解码器在这个状态的条件下学习中文序列。
    
3. **验证 3**：推理时不再提供正确中文，模型仍能从 `<BOS>` 逐词生成到 `<EOS>`。
### 实验配置：164,730 个参数

| 项目 | 配置 |
| :--- | :--- |
| **数据** | 3,840 组句对，训练 / 验证 / 测试为 3,072 / 384 / 384 |
| **词表** | 英文 71 个 Token，中文 58 个 Token |
| **编码器** | `Embedding(64)` + `GRU(128)` |
| **解码器** | `Embedding(64)` + `GRU(128)` + `Linear` |
| **训练方式** | Teacher Forcing，源句顺序反转 |
| **模型参数量** | 164,730 |

> **补充说明：**
> 出于复杂度考虑，编码器和解码器各用**一层 GRU**（`nn.GRU` 默认 `num_layers=1`）。Sutskever 的论文用 4 层 LSTM，那是面向大规模翻译的具体实现，并不是 Seq2Seq 架构的必要条件——受控任务上，单层 GRU 已足以展示编码、状态传递、Teacher Forcing 和自回归解码。

## 数据集: 反转源句, 加上BOS 与 EOS
```python
class TranslationDataset(Dataset):
    def __init__(
        self,
        pairs: list[tuple[list[str], list[str]]],
        source_vocab: Vocab,
        target_vocab: Vocab,
        reverse_source: bool = True,  # 是否反转源句 (英文)，默认开启
    ):
        self.pairs = pairs                 # (英文分词列表, 中文分词列表) 的句对
        self.source_vocab = source_vocab   # 英文词表: Token <-> ID 的映射
        self.target_vocab = target_vocab   # 中文词表
        self.reverse_source = reverse_source

    def __len__(self) -> int:
        return len(self.pairs)  # 数据集大小 = 句对数量

    def __getitem__(self, index: int) -> tuple[torch.Tensor, torch.Tensor]:
        source, target = self.pairs[index]

        # 反转源句：复现早期 Seq2Seq 缩短依赖路径的做法，
        # 让英文句首（对应中文句首）离解码器更近。
        if self.reverse_source:
            source = list(reversed(source))

        # 源句只需编码成 ID 序列，不加任何特殊 Token
        source_ids = self.source_vocab.encode(source)
        
        # 目标句首尾分别加 <BOS> 和 <EOS>:
        # <BOS> 给解码器提供第一步输入, <EOS> 教会模型「在哪里停」
        target_ids = [
            self.target_vocab.token_to_id[BOS],
            *self.target_vocab.encode(target),
            self.target_vocab.token_to_id[EOS] # 根据注释逻辑补全截断部分
        ]
        
        # 返回转为 Tensor 的 ID 序列
        return torch.tensor(source_ids), torch.tensor(target_ids)
```
## 一个 Batch 里的真实数据

DataLoader 把同一 Batch 的句子补齐到相同长度，并保留每个英文句子的真实长度。抽取一个 Batch，可以直接看到反转、特殊 Token 和 Teacher Forcing 如何共同改变模型接收的数据：

```text
source_batch: (128, 10)
target_batch: (128, 8)

原始英文:               henry has one black car
反转后的编码器输入:     car black one has henry
完整目标序列:           <BOS> 亨利 有 一个 黑色 汽车 <EOS>
Teacher Forcing 输入:   <BOS> 亨利 有 一个 黑色 汽车
对应监督目标:           亨利 有 一个 黑色 汽车 <EOS>
```
**英文序列和中文序列至此拥有各自独立的长度**：编码器不必为每个英文位置立即给出中文结果，解码器可以在读完英文后从自己的第一个时间步开始生成。

## Encoder、Decoder 与 Seq2Seq 三个类

```python
class Encoder(nn.Module):
    def __init__(self, vocab_size: int, embedding_dim: int, hidden_dim: int, pad_id: int):
        super().__init__()
        # padding_idx 让 <PAD> 的词向量恒为 0 且不参与梯度更新
        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=pad_id)
        # 单层 GRU; batch_first=True 表示输入形状为 [B, S, embedding_dim]
        self.gru = nn.GRU(embedding_dim, hidden_dim, batch_first=True)

    def forward(self, source: torch.Tensor, source_lengths: torch.Tensor) -> torch.Tensor:
        # Token ID -> 词向量 -> GRU 逐步读入, outputs: [B, S, hidden_dim]
        outputs, _ = self.gru(self.embedding(source))

        # Padding 后的最后一列不一定是真实句尾，因此按真实长度取最后一个有效状态。
        # 索引 = 长度 - 1，先扩展成 gather 需要的形状 [B, 1, hidden_dim]
        last_indices = (source_lengths - 1).view(-1, 1, 1)
        last_indices = last_indices.expand(-1, 1, outputs.size(-1))
        
        # 沿时间维取出每个句子的最后有效状态 -> [B, hidden_dim]
        final_hidden = outputs.gather(1, last_indices).squeeze(1)
        
        # 加回 num_layers 维 -> [1, B, hidden_dim], 可直接作为解码器 GRU 的初始隐藏状态
        return final_hidden.unsqueeze(0)
        
class Decoder(nn.Module):
    def __init__(self, vocab_size: int, embedding_dim: int, hidden_dim: int, pad_id: int):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=pad_id)
        self.gru = nn.GRU(embedding_dim, hidden_dim, batch_first=True)
        # 输出层：把每个时间步的隐藏状态映射为整个中文词表上的打分
        self.output = nn.Linear(hidden_dim, vocab_size)

    def forward(
        self, target_input: torch.Tensor, hidden: torch.Tensor
    ) -> tuple[torch.Tensor, torch.Tensor]:
        # hidden 是编码器传来的上下文向量 (或上一步的解码状态)
        # 训练时 target_input 是整段右移的真实序列，推理时是单个 Token
        outputs, hidden = self.gru(self.embedding(target_input), hidden)
        # 返回 logits [B, T, vocab_size] 和更新后的隐藏状态 (推理时继续传递)
        return self.output(outputs), hidden
        
class Seq2Seq(nn.Module):
    def __init__(self, encoder: Encoder, decoder: Decoder):
        super().__init__()
        self.encoder = encoder
        self.decoder = decoder

    def forward(
        self,
        source: torch.Tensor,
        source_lengths: torch.Tensor,
        target_input: torch.Tensor,
    ) -> torch.Tensor:
        # 编码：整句英文压缩为一个固定上下文向量 [1, B, hidden_dim]
        hidden = self.encoder(source, source_lengths)
        # 解码：Teacher Forcing 下所有时间步可一次并行计算
        logits, _ = self.decoder(target_input, hidden)
        return logits
        
model = Seq2Seq(
    Encoder(len(source_vocab), embedding_dim=64, hidden_dim=128, pad_id=source_pad_id),
    Decoder(len(target_vocab), embedding_dim=64, hidden_dim=128, pad_id=target_pad_id),
).to(device)
```
### 张量形状：数据在模型中的旅程

- **`B`**：Batch 大小（128）
    
- **`S`**：源句补齐后长度（如 10）
    
- **`T`**：目标输入长度（如 7）
    
- **`128`**：GRU 隐藏维度
    
- **`58`**：中文词表大小
    

| 张量                | 形状            | 含义                               |
| ----------------- | ------------- | -------------------------------- |
| `source`          | `[B, S]`      | B 个句子 × 每句 S 个英文 Token ID        |
| `Encoder.outputs` | `[B, S, 128]` | 每句每个时间步都留下一个 128 维隐藏状态           |
| `final_hidden`    | `[1, B, 128]` | 只保留每句最后一个有效状态，即固定上下文（1 为 GRU 层数） |
| `target_input`    | `[B, T]`      | 右移后的真实中文序列，每句 T 个位置              |
| `logits`          | `[B, T, 58]`  | 每个中文位置对词表 58 个 Token 各打一个分数      |

> **编码器的全部输出并没有交给解码器，`final_hidden` 是两者之间唯一的信息通道**——它既让 Seq2Seq 摆脱了逐位置对齐，也埋下了后面要解决的固定上下文瓶颈。

```python
# ignore_index: <PAD> 位置不计入损失，补齐部分不产生梯度
criterion = nn.CrossEntropyLoss(ignore_index=target_pad_id)
optimizer = torch.optim.Adam(model.parameters(), lr=3e-3)

def run_epoch(loader: DataLoader, training: bool) -> float:
    # 训练/验证共用一个函数，靠 training 开关区分
    model.train(training)
    total_loss = 0.0
    total_tokens = 0
    # 验证阶段用 no_grad 关闭梯度计算，省显存也更快
    gradient_context = torch.enable_grad() if training else torch.no_grad()

    with gradient_context:
        for source, lengths, target in loader:
            source = source.to(device)
            lengths = lengths.to(device)
            target = target.to(device)

            # Teacher Forcing 的核心：同一个 target 错开一位，
            # target[:, :-1] (去掉最后一个) 作为解码器输入，
            # target[:, 1:] (去掉 <BOS>) 作为监督目标。
            logits = model(source, lengths, target[:, :-1])
            labels = target[:, 1:]
            
            # CrossEntropyLoss 要求二维输入：把 [B, T, V] 展平成 [B*T, V]
            loss = criterion(
                logits.reshape(-1, logits.size(-1)),
                labels.reshape(-1),
            )

            if training:
                optimizer.zero_grad()       # 清空上一步的梯度
                loss.backward()             # 反向传播
                # 梯度裁剪：防止 RNN 训练中的梯度爆炸
                nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                optimizer.step()            # 更新参数

            # 按有效 Token 数 (排除 <PAD>) 加权累计损失
            token_count = int((labels != target_pad_id).sum().item())
            total_loss += loss.item() * token_count
            total_tokens += token_count

    # 返回整个 epoch 的平均每 Token 损失
    return total_loss / total_tokens
```
## 推理: 让模型接回自己的输出
```python
@torch.no_grad()  # 推理不需要梯度
def translate(
    source_tokens: list[str],
    max_length: int = 12,      # 生成长度上限，防止模型一直不输出 <EOS>
    return_trace: bool = False,
):
    model.eval()

    # 训练时反转了源句，推理时必须采用相同预处理。
    reversed_source = list(reversed(source_tokens))
    # 编码成 [1, S] 的张量 (Batch 大小为 1)
    source = torch.tensor([source_vocab.encode(reversed_source)], device=device)
    lengths = torch.tensor([len(reversed_source)], device=device)
    # 编码器输出固定上下文向量，作为解码器的初始隐藏状态
    hidden = model.encoder(source, lengths)

    # 解码器的第一个输入是 <BOS>
    current = torch.tensor([[target_vocab.token_to_id[BOS]]], device=device)
    generated_ids = []
    trace = [BOS]

    # 自回归循环：一次只生成一个 Token
    for _ in range(max_length):
        # 与训练不同：解码器输入是上一步「自己的输出」，而非真实答案
        logits, hidden = model.decoder(current, hidden)
        # 贪心解码：直接取词表上打分最高的 Token
        next_id = int(logits[:, -1].argmax(dim=-1).item())

        # 模型输出 <EOS>，说明它自己决定「翻译结束」
        if next_id == target_vocab.token_to_id[EOS]:
            trace.append(EOS)
            break

        generated_ids.append(next_id)
        trace.append(target_vocab.id_to_token[next_id])
        # 本步输出作为下一步输入，闭环接回自身
        current = torch.tensor([[next_id]], device=device)

    # 把 ID 序列还原成中文 Token
    prediction = target_vocab.decode(generated_ids)
    return (prediction, trace) if return_trace else prediction
```
### Teacher Forcing 与自回归，在代码里只差一行

**训练 · TEACHER FORCING**
```python
model(source, lengths, target[:, :-1])
```
一次读入完整的**真实目标前缀**；GRU 内部仍按 s1→s2→⋯s1​→s2​→⋯ 顺序更新，并没有位置级并行能力。

**推理 · 自回归**
```python
model.decoder(current, hidden)
```
循环调用，每次只输入一个 Token，只能读取**模型自己已经生成的结果**。

---

> **核心结论：**  
> 前者始终读取正确的历史 Token，后者把当前预测接回下一步——这正是训练与推理的本质区别。

### 训练结果：35 个 Epoch，完全匹配率 100%

#### TRAINING

**35 个 Epoch，CPU 耗时 6.9 秒**，训练与验证损失同步下降：
```text
Epoch 20 | train=0.0115 | valid=0.0101
Epoch 35 | train=0.0015 | valid=0.0015
```
![](../../../../image/Pasted%20image%2020261101085405.png)
#### TEST · EXACT MATCH

## 100.0%

> **384 / 384** 个测试句对：只有预测序列与正确序列逐 Token 完全相同才计为正确。
### 模型学会了组合，而不是背诵

模型没有在训练集中见过完整句子 `there is a quiet duck next to the door`，但已经学过其中的词和句式，因此能产生左边的生成轨迹——词汇组合、语序变化和停止条件都学会了。
![](../../../../image/Pasted%20image%2020261101085522.png)
这验证了经典 Seq2Seq 从数据构造、编码、Teacher Forcing 训练到自回归推理的**完整信息流**；但句子很短、词表很小、只有两种语法模板，并不意味着模型具备开放领域翻译能力。

> 进入真实翻译任务后，把全部输入压缩进一个 128 维状态的限制就会逐渐显现。

### 经典 Seq2Seq 的两个局限

#### 1. 串行计算

**训练无法完全并行**  
基于 RNN 的编码器与解码器仍需按时间顺序依次计算，序列越长，训练效率越低。

#### 2. 固定上下文

**整个输入压缩进一个向量**  
无论输入是一句 `Hello.`，还是数百词甚至数千词的长文章，编码器最终都输出一个固定长度的上下文向量（Context Vector）交给解码器。
### 固定上下文向量是一个信息瓶颈
![](../../../../image/Pasted%20image%2020261101085908.png)
#### 越长越挤

输入越长，越多的信息被压进同一个向量，模型难以完整保留语义，**长文本翻译和摘要的性能明显下降**。

#### 门控也无解

LSTM 与 GRU 改善了信息**穿过时间链**的能力，却没有消除这一**固定压缩**。

> **解决思路：**  
> 要进一步提升长序列转换效果，解码器需要能**直接查看编码器的各个位置**，并在每一步决定当前**最需要哪部分信息**。

### Attention：让解码器动态关注输入序列
![](../../../../image/Pasted%20image%2020261101090201.png)
编码器不再只输出最后一个隐藏状态，而是保留整个隐藏状态序列：
$$[h1​,h2​,h3​,…,hn​]$$
> [!abstract] 核心机制  
> 解码器在生成每个 Token 时，会执行以下三步：
> 
> 1. 先根据当前状态计算一组 **注意力权重**（Attention Weights）。
>     
> 2. 再对所有隐藏状态进行 **加权求和**，得到当前时间步的上下文向量（Context Vector）。
>     
> 3. 最后结合自身状态，预测下一个 Token。
>     

> [!example] 翻译示例  
> **输入**：`I love deep learning`
> 
> - 生成「**深度**」 →→ 自动关注 `deep`
>     
> - 生成「**学习**」 →→ 自动关注 `learning`

### 从固定向量到动态上下文
| 传统 Seq2Seq | ➡️ | + Attention |
| :--- | :---: | :--- |
| **一个向量说了算** | | **每一步各取所需** |
| 所有解码时间步共享同一个固定上下文 | | 每个输出 Token 动态获取最相关的源序列信息 |
> [!summary] 核心演进
> Attention 显著缓解了固定上下文的信息瓶颈，大幅提升长序列建模能力，并成为后续 **Transformer 架构**的核心组成部分。
