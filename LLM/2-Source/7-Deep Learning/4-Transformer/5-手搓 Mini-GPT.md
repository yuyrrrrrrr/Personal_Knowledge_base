![](Pasted%20image%2020261108155255.png)
## GPT: Decoder-Only 架构
GPT 只堆叠 Decoder Block，每个位置通过**因果自注意力**读取前文，不接 Encoder，也不使用交叉注意力。
**向量 $\to$ 词表分数**
每个位置输出全部候选 Token 的 logits。
**GPT Block $\times$ 4**
注意力汇集前文信息，前馈层加工每个位置的特征。
**Token $\to$ 向量**
字符映射为 ID，再由 Embedding 查出向量。

## 现代大模型优化
![](Pasted%20image%2020261108155456.png)
现代大模型对 Transformer 的多个模块做了大量工程优化，涉及**位置编码、归一化、前馈网络和线性投影**等环节。这些改动改善位置感知、深层训练与特征表达，也有助于控制参数量。下面是本课采用的五项。
*   **RoPE**：更好地感知 Token 之间的相对距离。
*   **Pre-Norm**：让梯度更顺畅地穿过多个层 Block，稳定深层训练。
*   **RMSNorm**：以更少的归一化计算维持特征尺度稳定。
*   **SwiGLU**：增强前馈层的表达能力，更灵活地筛选特征。
*   **无偏置**：减少冗余参数，让投影层更简洁。
## 我们的训练目标：首字续写四句五言诗

我们选择四句五言诗作为 Mini-GPT 的训练任务。每首诗都有统一的长度和标点位置，便于构造定长序列，也能直观检查续写效果。模型从唐宋诗中学习字符的衔接；给定首字，目标是续成一首含**20 个汉字和 4 个标点**的诗。

**训练时**
输入真实诗句的前缀，让每个位置学习预测紧邻的下一个 Token。

**生成时**
从 `<BOS>` 和首字出发，每次取最后位置的预测并追加新字符。

先看一次实际生成：训练完成后，给 Mini-GPT 首字“春”，它逐字写出了下面这首诗。下一页再看模型怎样学会预测下一字。

> **春风吹白鹭，日暮望孤山。谁家千里泪，相送一行愁。**

## 训练方式：每个位置预测下一个 Token
以《春晓》为例，模型从 `<BOS>` 预测“春”，从 `<BOS>春` 预测“眠”，后续位置也遵循同一规则。把输入和标签错位一格，再用因果掩码保证各位置只能读取前缀，一次前向计算就能得到整首诗各位置的预测。
```text
输入  <BOS> 春 眠 不 觉 晓 ， ... 花 落 知 多 少 。
标签      春 眠 不 觉 晓 ， ... 花 落 知 多 少 。 <EOS>
```
**自监督**：答案直接来自原诗，无需逐字人工标注。  
**Teacher Forcing**：训练时始终喂入真实前缀。

2424 个正文字符加上 `<BOS>`、`<EOS>`，共 2626 个 Token；错位后得到 2525 个预测位置。
## Mini-GPT 模块总览：从字符到词表分数

一首诗送入 Mini-GPT 前，先拆成字符并编码为 Token ID；Embedding 再把 ID 变成向量。接着，四层 GPT Block 让各位置结合自身位置和已见前文，最后得到对词表中所有 Token 的打分。训练时用这些分数与真实下一字计算损失；生成时取末位分数选择新字。下面先看模块如何衔接，再逐个实现。

```
# 输入处理
def encode(text): ...          # 字符 -> Token ID
def decode(ids): ...           # Token ID -> 字符
class TokenEmbedding:
    def forward(self, token_ids): ... # 查字符向量
class RotaryPositionalEmbedding:
    def forward(self, q_or_k): ... # 在 Q、K 中注入位置信息
# 注意力与前馈计算
def attention(q, k, v): ...    # 因果掩码下计算注意力

class MultiHeadAttention:
    def forward(self, x): ...          # QKV 投影 -> RoPE -> 多头注意力
class RMSNorm:
    def forward(self, x): ...          # 按特征均方根缩放
class SwiGLU:
    def forward(self, x): ...          # 门控前馈变换
# 解码器与完整模型
class GPTBlock:
    def forward(self, x): ...          # Pre-Norm 注意力 -> Pre-Norm 前馈，各带残差
class GPTDecoder:
    def forward(self, x): ...          # 依次运行四个 Block，最后做 RMSNorm
class MiniGPT:
    def forward(self, token_ids): ...  # Embedding -> Decoder -> 共享权重的词表投影
```

## 准备运行环境
项目使用 Python 3.12、PyTorch 和 Matplotlib，依赖由 uv 管理。先运行 `uv sync --locked`，再打开 `notebook/mini_gpt_modern.ipynb`。
```toml
[project]
name = "deep-learning"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "matplotlib>=3.10.9",
    "torch>=2.12.0",
]
```
## 导入依赖与定义模型规模
运行环境就绪后，先固定随机种子、选择可用设备，再统一设置模型规模。\(96\) 维向量分给 \(6\) 个注意力头，每头 \(16\) 维，可成对施加 RoPE；最大上下文长度设为 \(32\)，足以容纳本例 \(26\) 个 Token 的诗歌序列。
```python
import math
import random
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import torch
from torch import nn

# 固定 Python 与 PyTorch 的随机种子，使数据顺序、参数初始化和演示可复现
random.seed(42)
torch.manual_seed(42)

# 小模型的单次矩阵运算很短，限制 CPU 线程可避免线程调度开销反而拖慢运行
torch.set_num_threads(1)

# 后续模型参数和训练 Batch 必须移动到同一个 DEVICE，否则张量运算会报设备不一致
DEVICE = torch.device(
    'cuda' if torch.cuda.is_available()
    else 'mps' if torch.backends.mps.is_available()
    else 'cpu'
)
print("训练设备: ", DEVICE)

# 模型参数
D_MODEL = 96         # 每个 Token 的向量维度
HEADS = 6            # 注意力头数，每个头有 16 维
D_FF = 256           # SwiGLU 前馈网络的中间层维度
NUM_LAYERS = 4       # GPT Block 的层数
MAX_LENGTH = 32      # 最大上下文长度，需大于本例完整序列长度 26
ROPE_BASE = 10000.0  # RoPE 的频率基数
```

## 数据集来源与筛选

训练目标是四句五言，语料也需要一致的句数和句长。原始唐宋诗格式各异，直接混用会让小模型同时学习多种诗形，也不便于整理成固定长度的训练序列。

我们把古诗词开源数据集 `chinese-poetry` 的唐诗和宋诗中按标点拆句，只保留**恰好四句、每句五个汉字**的作品，再转成简体并按正文去重。文件保留朝代、题目、作者和正文，模型只使用 `text` 列。

`notebook/data/five_char_quatrains.tsv` (真实数据节选)

| 朝代 | 题目 | 作者 | text (诗歌正文) |
| :--- | :--- | :--- | :--- |
| 唐 | 春晓 | 孟浩然 | 春眠不觉晓，处处闻啼鸟。夜来风雨声，花落知多少。 |
| 宋 | 梅花 | 王安石 | 墙角数枝梅，凌寒独自开。遥知不是雪，为有暗香来。 |
| 宋 | 夏日绝句 | 李清照 | 生当作人杰，死亦为鬼雄。至今思项羽，不肯过江东。 |

最终得到 $16,640$ 首，每首正文统一为 $20$ 个汉字 + $4$ 个标点。筛选只检查文本结构，不校验平仄和押韵。

## 保留高频汉字，罕见字交给 UNK
为了训练方便，本例使用字符级 Token，并且只保留**至少出现 \(5\) 次**的汉字，罕见字统一映射为 `<UNK>`，逗号和句号始终保留。
```python
MIN_TOKEN_FREQ = 5
character_counts = Counter("".join(all_poems))
kept_characters = {
    char
    for char, count in character_counts.items()
    if char in "，。" or count >= MIN_TOKEN_FREQ
}
```
例如，一个字在整份诗集中只出现 22 次，却仍需要自己的词表编号和向量，模型很难学到它的用法。把出现少于 55 次的字统一记作 `<UNK>`，词表和参数量都会变小；代价是模型无法再区分这些罕见字。
## 构造 Token 与 ID 的双向映射
Embedding 需要整数 ID，不能直接接收汉字。我们给每个保留的字符分配编号：token_ids 用字查 ID，tokens 用 ID 找回字。`<UNK>` 表示罕见字；`<BOS>` 和 `<EOS>` 标记序列的开始与结束，下一页再看它们如何参与训练。
```python
tokens = ["<BOS>", "<EOS>", "<UNK>"] + sorted(kept_characters)
token_ids = {token: index for index, token in enumerate(tokens)}
BOS = token_ids["<BOS>"]
EOS = token_ids["<EOS>"]
UNK = token_ids["<UNK>"]
```
**输入：字 -> ID**  
`token_ids["春"] -> 1346`，模型用这个编号查 Embedding 向量。

**输出：ID -> 字**  
`tokens[1346] -> "春"`，把模型预测的编号还原为文字。
## BOS、EOS 与 Teacher Forcing

`<BOS>` 告诉模型一首诗从哪里开始，`<EOS>` 则是模型要学会预测的结束标记。以刚才数据表中的《春晓》为例，\(24\) 个正文字符加上两个边界 Token，形成长度为 \(26\) 的完整序列。

> 《春晓》的完整序列（以 Token 展示，代码中存储的是 ID）
> `<BOS>`春眠不觉晓，处处闻啼鸟。夜来风雨声，花落知多少。`<EOS>`

**模型输入：去掉最后的 `<EOS>`**
`full_sequence[:-1]` 对应 `<BOS> 春 眠 ... 少 。`

**监督标签：去掉开头的 `<BOS>`**
`full_sequence[1:]` 对应 `春 眠 ... 少 。 <EOS>`

答案直接从原诗错位得到，属于**自监督训练**。训练时始终喂入原诗的**真实前缀**，这叫 Teacher Forcing；因果掩码遮住未来，模型在 \(25\) 个位置同时预测下一个 Token，最后一个位置学习预测 `<EOS>`。

| 全部 \(16,640\) 首 | 训练 \(14,976\) 首 | 验证 \(1,664\) 首 | 词表 \(3,502\) | 序列 \(26\) Token |
| :--- | :--- | :--- | :--- | :--- |
## Embedding：给每个 Token 配一个可训练向量

上一页把《春晓》转换成 Token ID 序列，但编号本身没有字义。进入 GPT Block 前，Embedding 根据每个 ID 从可训练的**参数表**中取出一个 96 维向量，作为这个 Token 的初始表示。

**1 · 输入编号**
“春” $\to$ 1346

**2 · 按 ID 查表**
取参数表的第 1346 行

**3 · 得到向量**
$[96]$ 维特征，送入 GPT Block

参数表形状是 $[3502, 96]$：每个 Token 占一行。同一个“春”总会查到同一行；训练会更新这张表，后续 GPT Block 再根据上下文改变它的表示。

$$
X = \text{Dropout}(\text{Embedding}(\text{token\_ids}))
$$

一个 Batch 从 $[B, 25]$ 个 ID 变成 $[B, 25, 96]$ 的向量序列。Dropout 只在训练时随机屏蔽部分特征；本版不在这里叠加位置向量，也不乘以 $\sqrt{96}$。位置处理留给后面的注意力模块。
## 实现 TokenEmbedding

把查表过程封装成 TokenEmbedding：输入 `[B,25]` 个 ID，输出 `[B,25,96]` 的向量。这张参数表稍后还会用于输出预测，因此先用 `std=0.02` 小幅初始化，避免初始预测分数过大；`Dropout(0.1)` 只在训练时生效。

```python
# 训练时随机屏蔽 10% 的 Embedding 输出特征
DROPOUT = 0.1

class TokenEmbedding(nn.Module):
    def __init__(self, vocab_size):
        super().__init__()
        # 每个 Token 对应参数表中的一行，向量维度由 D_MODEL 决定
        self.embedding = nn.Embedding(vocab_size, D_MODEL)

        # 后续输出投影复用这张表；小幅初始化可避免初始 logits 过大
        nn.init.normal_(self.embedding.weight, mean=0.0, std=0.02)

        # train() 模式启用；调用 eval() 后关闭，用于评估和生成
        self.dropout = nn.Dropout(DROPOUT)

    def forward(self, token_ids):
        # 查表后施加 Dropout；这里不叠加位置向量，也不乘 sqrt(D_MODEL)
        # 位置信息留给后续注意力层处理
        return self.dropout(self.embedding(token_ids))
```
        
## RoPE：旋转 Q、K，感知相对位置
![](Pasted%20image%2020261108161536.png)
Embedding 本身没有写入位置。本例每头 \(16\) 维，RoPE 将 Q、K 的相邻两维分成 \(8\) 对；第 \(i\) 对在位置 \(pos\) 的转角为 \(\alpha = pos\theta_i\)。
**为什么只旋转 Q、K？** 注意力权重由 Q、K 点积决定，旋转后点积包含两位置的角度差。V 在权重确定后才提供内容；旋转 V 不会改变注意力看哪里。
---
**频率（base=10000）：低维快，高维慢**
$$
\theta_i = \text{base}^{-2i/D_h}
$$
**\(x, y\) 是 Q/K 中相邻的两个数；\(x', y'\) 是旋转后的值**
$$
R(\alpha) = \begin{pmatrix} \cos\alpha & -\sin\alpha \\ \sin\alpha & \cos\alpha \end{pmatrix}, \quad \begin{pmatrix} x' \\ y' \end{pmatrix} = R(\alpha)\begin{pmatrix} x \\ y \end{pmatrix}
$$
---
**例：**《春晓》中的“不”位于位置 \(3\)。只看其 Q 中编号 \(i=2\) 的一对，假设原值为 \((x, y) = (1, 0)\)。
**先算频率**
$$
\theta_2 = 10000^{-2\cdot2/16} = 10000^{-1/4} = (10^4)^{-1/4} = 10^{-1} = 0.1
$$
**再算转角**
$$
\alpha = pos\theta_2 = 3 \times 0.1 = 0.3 \text{ 弧度}
$$
**$旋转矩阵 \times 原值 = 新值$**
$$
R(0.3)\begin{pmatrix} 1 \\ 0 \end{pmatrix} = \begin{pmatrix} \cos 0.3 \\ \sin 0.3 \end{pmatrix} \approx \begin{pmatrix} 0.96 \\ 0.30 \end{pmatrix}
$$## 实现 RoPE：预计算角度并旋转 Q、K

初始化时，为 \(8\) 对维度 \(\times\) 最多 \(32\) 个位置预存 \(\cos/\sin\)。前向函数里的 `x` 是整批 Q/K 张量；`even`、`odd` 才分别对应上一页每对的 \(x\)、\(y\)。代码把矩阵乘法展开成两式，再交错还原，形状仍为 \([B, H, L, 16]\)。

```python
class RotaryPositionalEmbedding(nn.Module):
    def __init__(self, head_dim, max_length, base=ROPE_BASE):
        super().__init__()
        assert head_dim % 2 == 0, "RoPE 要求每个注意力头的维度为偶数。"

        # 每一对维度共享一个频率 theta_i = base^(-2i/head_dim)。
        # head_dim 个特征按 (0,1)、(2,3)... 两两组成二维平面，因此只需 head_dim/2 个频率
        pair_index = torch.arange(0, head_dim // 2, dtype=torch.float32)

        # 低维频率高、旋转快；高维频率低、旋转慢，从而覆盖不同尺度的位置关系
        theta = base ** (-2.0 * pair_index / head_dim)           # [head_dim/2]
        position = torch.arange(max_length, dtype=torch.float32) # [L]
        angles = torch.outer(position, theta)                    # [L, head_dim/2]

        # 预存每个位置、每对维度对应旋转角的余弦与正弦
        # cos/sin 不参与训练；register_buffer 让它们随模型迁移到 CPU、CUDA 或 MPS
        self.register_buffer("cos", torch.cos(angles))
        self.register_buffer("sin", torch.sin(angles))

    def forward(self, x):
        # x: [B, H, L, head_dim], 按相邻维度两两配对旋转
        sequence_length = x.shape[-2]

        # cos/sin 的 [L, head_dim/2] 会自动广播到 Batch 维与 Head 维
        cos = self.cos[:sequence_length]    # [L, head_dim/2]
        sin = self.sin[:sequence_length]
        even = x[..., 0::2]  # 偶数维 x_2j
        odd = x[..., 1::2]   # 奇数维 x_2j+1
        rotated_even = even * cos - odd * sin
        rotated_odd = even * sin + odd * cos

        # 交错合并回原来的维度顺序
        # stack 后为 [..., head_dim/2, 2], flatten 将每对维度交错还原为 [..., head_dim]
        rotated = torch.stack((rotated_even, rotated_odd), dim=-1)
        return rotated.flatten(-2)
```
## 单头注意力：用 Q、K、V 汇集信息

**自注意力的核心作用**是让每个位置从同一序列中挑选相关信息，把当前 Token 的向量更新为带上下文的表示。例如处理《春晓》里的“声”时，它可以参考前面的“风”“雨”。具体计算时，同一组 Token 向量投影成 Q、K、V，依次完成打分、求权重和汇总。

**1 · 打分**
\(QK^\top/\sqrt{D_h}\) 比较 Q 与 K；缩放避免分数过大。

**2 · 得到权重**
对每个 Query 的一行分数做 Softmax，权重之和为 \(1\)。

**3 · 汇总**
按权重对各位置的 V 加权求和，得到当前位置的新向量。

$$
\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^\top}{\sqrt{D_h}}\right)V
$$

**单头的张量形状**
Q、K、V $[B, L, D_h]$ $\to$ 权重 $[B, L, L]$ $\to$ 输出 $[B, L, D_h]$

**下一步**
目前还能读取未来位置；下一页用因果掩码限制可见范围。
## 单头因果注意力：掩码遮住未来
训练时一次处理整首诗，但每个位置只看已有前缀。例如“春”要预测“眠”，若能读到后面的“眠”，就等于偷看答案。
![](Pasted%20image%2020261108163538.png)
每行是 Query，每列是 Key；从左到右依次是打分、加右上三角掩码、Softmax 求权重、加权 V。未来位置在汇总前就被排除。
$$
\text{CausalAttention}(Q, K, V) = \text{softmax}\left(\frac{QK^\top}{\sqrt{D_h}} + M\right)V
$$
**掩码规则**
$j \le i$: $M_{ij} = 0$; $j > i$: $M_{ij} = -\infty$。Softmax 后，未来权重为 $0$。
**《春晓》中的可见范围**
在“春”处，可读取 `<BOS>` 和“春”；“眠”及后文都被遮住。
## 实现因果注意力：掩码与广播

代码按“打分 $\to$ 遮住未来 $\to$ Softmax $\to$ 加权 V”执行。$[L,L]$ 的掩码可广播到每个 Batch 和 Head 的分数矩阵，因此同一函数既能算单头，也能并行处理 $[B,H,L,D_h]$。

```python
def attention(q, k, v):
    # 单头 [L, Dh] 与批量多头 [B, H, L, Dh] 共用同一计算，@ 作用于最后两维
    # 转置 K 的最后两维后，Q @ K^T 得到 [..., L, L] 的注意力分数
    # 除以 sqrt(Dh) 可控制点积数值范围，避免 softmax 过早进入接近 one-hot 的饱和区
    scores = q @ k.transpose(-2, -1) / math.sqrt(q.shape[-1])

    sequence_length = q.shape[-2]
    # diagonal=1 只遮住严格位于主对角线右上方的位置：第 i 个 Token 可看见自己和全部前文
    # mask 与 q 放在同一设备，避免在 GPU/MPS 训练时发生设备不一致
    mask = torch.triu(
        torch.ones(sequence_length, sequence_length, dtype=torch.bool, device=q.device),
        diagonal=1,
    )
    
    # [L, L] 掩码自动广播到每个 Batch、每个 Head 的分数矩阵
    scores = scores.masked_fill(mask, float("-inf"))

    # softmax 在 Key 维度归一化，使每个 Query 对所有可见位置的权重之和为 1
    weights = torch.softmax(scores, dim=-1)
    # [B, H, L, L] @ [B, H, L, Dh] -> [B, H, L, Dh]
    return weights @ v
```
## 多头注意力：拆头、旋转与输出投影
单头只有一组 Q、K、V；多头用不同的投影参数，并行学习“该关注哪些位置”。本例把 96 维分给 6 个头，每头处理 16 维，再把各头读到的信息汇总。
![](Pasted%20image%2020261108163909.png)
**1 · 投影并拆头**
一次投影生成 Q、K、V；各自从 $[B,L,96]$ 拆成 $[B,6,L,16]$，让每个头独立打分。
**2 · 旋转后计算注意力*
拆头后先对 Q、K 调用 RoPE，V 不旋转；各头分别计算因果注意力。
**3 · 合并并输出投影**
6 个头的结果拼回 $[B,L,96]$；输出投影混合这些信息，供下一层继续处理。

## 实现多头注意力：沿着形状读代码

输入 $[B,L,96]$ 经过一次投影，得到打包的 Q/K/V $[B,L,288]$；拆头后，Q、K、V 各为 $[B,6,L,16]$。此时只给 Q/K 加 RoPE，再计算因果注意力，最后合并回 $[B,L,96]$。输入若只有 $[L,96]$，代码会临时补上 Batch 维，返回前再去掉。

```python
class MultiHeadAttention(nn.Module):
    def __init__(self):
        super().__init__()
        assert D_MODEL % HEADS == 0, "D_MODEL 必须能被 HEADS 整除。"
        self.head_dim = D_MODEL // HEADS

        # 类 LLaMA 结构中的线性层不使用偏置
        # 一次生成 Q、K、V；bias=False 与 LLaMA 的无偏置线性层保持一致
        self.qkv_proj = nn.Linear(D_MODEL, 3 * D_MODEL, bias=False)

        # 多头结果拼接后，通过输出投影重新混合各个 Head 的信息
        self.out_proj = nn.Linear(D_MODEL, D_MODEL, bias=False)

        # 旋转位置编码引入
        self.rope = RotaryPositionalEmbedding(self.head_dim, MAX_LENGTH)

    def forward(self, x):
        # 生成时可能传入 [L, D_MODEL]，统一转为 [1, L, D_MODEL] 进行多头计算
        unbatched = x.dim() == 2
        if unbatched:
            x = x.unsqueeze(0)

        batch_size, sequence_length, _ = x.shape
        qkv = self.qkv_proj(x)

        # 在最后一维平均切成三份；此时 Q、K、V 的形状均为 [B, L, D_MODEL]
        q, k, v = qkv.chunk(3, dim=-1)

        def split_heads(tensor):
            # [B, L, D_MODEL] -> [B, L, H, Dh] -> [B, H, L, Dh]
            return tensor.reshape(
                batch_size, sequence_length, HEADS, self.head_dim
            ).transpose(1, 2)

        q = split_heads(q)
        k = split_heads(k)
        v = split_heads(v)

        # RoPE 只旋转 Q 和 K，让注意力分数依赖相对位置，V 保持不变
        # Q、K 在相同位置使用相同旋转角，二者点积后，绝对角度相消，只保留相对位置
        q = self.rope(q)
        k = self.rope(k)

        # 一次矩阵运算并行处理所有 Batch 和所有 Head
        context = attention(q, k, v)  # [B, H, L, Dh]

        # [B, H, L, Dh] -> [B, L, H, Dh] -> [B, L, D_MODEL]，把多个 Head 重新拼回特征维
        # transpose 后内存通常不连续，先调用 contiguous 再 reshape 可避免潜在的步长问题
        joined = context.transpose(1, 2).contiguous().reshape(
            batch_size, sequence_length, D_MODEL
        )

        output = self.out_proj(joined)
        return output.squeeze(0) if unbatched else output
```
## SwiGLU: 按输入调节前馈层特征
注意力汇入前文后，前馈层分别处理各位置的向量。普通 ReLU FFN 把负的中间值直接置零，只用一条路径产生特征。**SwiGLU** 的关键不只是换用更平滑的 SiLU：up 生成候选特征，独立的 gate 路径为每项特征计算乘数；逐项相乘后，down 投回原维度。内容与调节分开学习，特征贡献就能随输入改变。
![](Pasted%20image%2020261108164455.png)
**up: 生成内容**
把当前 Token 的 96 维表示投到 256 维，形成候选特征；这一路不经过激活。
**gate: 分别调节各项特征**
另一路也生成 256 个数并经过 SiLU；每个数只乘 up 对应位置的特征，可分别放大或抑制。
**down: 投回模型空间**
将调节后的 256 维压回 96 维，让输出能与 Block 的残差分支相加。
## 实现 SwiGLU：两路投影与逐元素门控

对照上一页公式读 `forward`：**只有 `gate` 经过 SiLU**，再与未激活的 `up` 逐元素相乘，最后交给 `down`。`gate`、`up` 都把 \(96\) 维升到 \(256\) 维，`down` 降回 \(96\) 维；三个线性层都不加偏置，Batch 与序列长度保持不变。

```python
class SwiGLU(nn.Module):
    def __init__(self):
        super().__init__()
        # 门控与升维两条并行投影，逐元素相乘后再降维；均不使用偏置
        # gate_proj 决定哪些特征通过，up_proj 提供被筛选的内容，两条路径形状均为 [..., D_FF]
        self.gate_proj = nn.Linear(D_MODEL, D_FF, bias=False)
        self.up_proj = nn.Linear(D_MODEL, D_FF, bias=False)

        # 逐元素门控后再投影回 D_MODEL，保证结果能与残差分支直接相加
        self.down_proj = nn.Linear(D_FF, D_MODEL, bias=False)

        self.activation = nn.SiLU()

    def forward(self, x):
        # SiLU(gate) 与 up 逐元素相乘，相当于为每个 Token、每个中间特征学习一个连续门控值
        return self.down_proj(self.activation(self.gate_proj(x)) * self.up_proj(x))
```
## Pre-Norm: 让残差保留直接通路
**Post-Norm: 残差相加后再归一化**
$$
y = \text{Norm}(x + F(x))
$$
先算 $F(x)$，与原输入 $x$ 相加，再对总和做 Norm。残差分支到达下一层前仍要经过 Norm；堆叠很多层时，梯度也要反复穿过它，训练可能更难稳定。
**Pre-Norm: 先归一化再进入子层**
$$
y = x + F(\text{Norm}(x))
$$
先对 $x$ 做 Norm，再送进 $F$；$F$ 的结果与未经变换的 $x$ 相加。信息和梯度都能沿残差分支直接传递，深层模型通常更易优化。
## RMSNorm：只按均方根缩放

**为什么可以不减均值？**
LayerNorm 同时把均值移到 \(0\)、控制尺度。
均方根已能衡量整体幅度；即使均值不为 \(0\)，除以均方根也能控制数值大小，因此本例省去减均值。

**RMSNorm 怎样计算？**

$$
\text{RMSNorm}(x) = \gamma \odot \frac{x}{\sqrt{\text{mean}(x^2) + \epsilon}}
$$

沿每个 Token 的特征维求均方根；$\gamma$ 调节各维，$\epsilon$ 防止除零，形状不变。

```python
class RMSNorm(nn.Module):
    # eps 避免分母归零
    def __init__(self, dim, eps=1e-6):
        super().__init__()
        self.eps = eps
        self.weight = nn.Parameter(torch.ones(dim))

    def forward(self, x):
        # 在最后的特征维计算均方根，keepdim=True 便于广播回原形状
        rms = torch.sqrt(x.pow(2).mean(dim=-1, keepdim=True) + self.eps)
        return self.weight * (x / rms)
```
## GPT Block: 先读前文，再变换特征

一个 Block 连做两次残差更新，输入和输出都保持 $[B,L,96]$：先用多头注意力汇入可见前文，再用 SwiGLU 变换当前位置的特征。两次都是先归一化子层输入，原向量沿残差分支直接保留。

**① 注意力：从前文取信息**

$$
u = \text{RMSNorm}_1(x)
$$

$$
h = x + \text{Dropout}(\text{MultiHeadAttention}(u))
$$

归一化后的 $u$ 进入因果多头注意力；未经归一化的 \(x\) 直接加回，得到带上下文的 $h$。

**② 前馈层：加工当前位置**

$$
v = \text{RMSNorm}_2(h)
$$

$$
y = h + \text{Dropout}(\text{SwiGLU}(v))
$$

第二次使用已更新的 $h$；SwiGLU 逐位置变换特征，再与 $h$ 相加得到 Block 输出 $y$。

Dropout 只作用于子层输出，不打断残差直通路径。四个 Block 各有独立参数；全部堆叠后，Decoder 再做一次 RMSNorm。
## 实现 GPTBlock

读 `forward` 的两行更新：第一行把 \(\text{norm1}(x)\) 送入注意力；第二行用更新后的 \(x\) 计算 \(\text{norm2}(x)\) 与 SwiGLU。每行加号旁的 \(x\) 都是残差直通，Dropout 只作用于子层输出。

```python
class GPTBlock(nn.Module):
    def __init__(self):
        super().__init__()
        self.self_attn = MultiHeadAttention()
        self.ffn = SwiGLU()
        self.norm1 = RMSNorm(D_MODEL)
        self.norm2 = RMSNorm(D_MODEL)
        # 残差 Dropout：子层输出在加回残差前先随机置零一部分，抑制记忆式过拟合
        self.dropout = nn.Dropout(DROPOUT)

    def forward(self, x):
        # Pre-Norm：先归一化再进子层，残差分支保持不被归一化
        # 注意调用顺序：RMSNorm(x) 进入子层，子层输出再与原始 x 相加，这就是 Pre-Norm
        x = x + self.dropout(self.self_attn(self.norm1(x)))
        x = x + self.dropout(self.ffn(self.norm2(x)))
        return x
```
## 堆叠 Decoder 并做最终归一化

本例用 ModuleList 创建四个参数各自独立的 GPT Block。每层都保持 $[B, L, 96]$，因此上一层输出能直接送入下一层；因果掩码与 RoPE 在各层的注意力内部生效。循环结束后只做一次 RMSNorm，整理最终表示，再交给输出层预测 Token。

```python
class GPTDecoder(nn.Module):
    def __init__(self, num_layers):
        super().__init__()
        self.layers = nn.ModuleList([GPTBlock() for _ in range(num_layers)])
        self.norm = RMSNorm(D_MODEL)  # Pre-Norm 结构需在最后补一次归一化

    def forward(self, x):
        for layer in self.layers:
            x = layer(x)
        # 各 Block 的残差分支末尾没有归一化，因此堆叠结束后统一补一次 RMSNorm
        return self.norm(x)
```
## 从 Decoder 向量到词表 logits

经过四个 Block 和最终 RMSNorm 后，每个位置得到一个 $96$ 维向量：它已汇入该位置可见的前文，却还不是下一个字的预测。接下来输出层把这个向量映射到 $3,502$ 维词表空间，让每个候选 Token 都得到一个分数——logit。

向量 $h_t$ 与词表向量表 $E$ 逐行点积 $\to$ $3,502$ 个 logits

$$
z_t = h_t E^\top, \quad z_t \in \mathbb{R}^{3502}
$$

**例如：预测“晓”**
输入 `<BOS>`春眠不觉，取“觉”的向量为“晓”等候选 Token 打分。logit 是相对分数，还不是概率。

**训练与生成**
训练：所有位置的 logits 与下一 Token 算交叉熵。
生成：取最后位置的 logits，转成概率后采样。

**权重共享**：输入查表与输出打分共用 $E \in \mathbb{R}^{3502 \times 96}$，省去 $336,192$ 个参数；模型约 $77.9$ 万个参数。

## 拼装 MiniGPT：从 Token ID 到词表分数

MiniGPT 依次经过 Embedding、四层 Decoder 和词表投影，输出 \([B, L, 3502]\) 的 logits。留意两点：**输出投影复用 Embedding 权重**，`forward` 不做 Softmax。

```python
class MiniGPT(nn.Module):
    def __init__(self, vocab_size):
        super().__init__()
        self.embedding = TokenEmbedding(vocab_size)
        self.decoder = GPTDecoder(NUM_LAYERS)
        self.output_projection = nn.Linear(D_MODEL, vocab_size, bias=False)

        # 输出投影复用输入 Embedding 的 [vocab_size, D_MODEL] 参数表
        # 本例省去 3502 x 96 个参数，约占未共享模型参数量的 30%
        self.output_projection.weight = self.embedding.embedding.weight

    def forward(self, token_ids):
        x = self.embedding(token_ids)
        x = self.decoder(x)

        # 对每个位置独立地产生 vocab_size 个 logits；softmax 留给损失函数或采样阶段处理
        return self.output_projection(x)
```

## 训练 Mini-GPT：错位一格预测下一字

训练分两步：错位得到下一字标签，再按批计算损失、更新参数。下方先设置超参数。

**① 把序列错位一格**

$26$ 个 Token 中，前 $25$ 个作输入，后 $25$ 个作目标；每列对应一次下一字预测。

| 输入 | `<BOS>` | 春 | 眠 | 不 | 觉 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 目标 | 春 | 眠 | 不 | 觉 | 晓 |

**② 按批次更新模型**

因果掩码限制可读前缀；每首诗一次前向得到 $25$ 个预测。交叉熵汇总误差，AdamW 更新参数。

验证损失用于早停；Dropout、权重衰减和标签平滑缓解过拟合。

```python
BATCH_SIZE = 64                  # 每次参数更新使用的诗歌数
MAX_EPOCHS = 1000                # 最多遍历训练集的轮数，通常由早停提前结束
MIN_EPOCHS = 10                  # 至少训练到这一轮，才累计早停等待轮数
LEARNING_RATE = 0.002            # AdamW 的初始学习率
EARLY_STOPPING_PATIENCE = 10     # 验证损失连续多少轮未改善后停止
EARLY_STOPPING_MIN_DELTA = 0.0001 # 早停判定所需的最小下降量
WEIGHT_DECAY = 0.1               # AdamW 权重衰减的强度
LABEL_SMOOTHING = 0.1            # 将 10% 的目标权重均匀分给整个词表
```
## 用验证损失检查训练效果

每轮结束后，用 `mean_loss` 计算训练子集和验证集的普通交叉熵。评估时关闭 Dropout、不用标签平滑；**验证损失越低，模型对未见诗句的下一字预测越准**。

```python
train_criterion = nn.CrossEntropyLoss(label_smoothing=LABEL_SMOOTHING)
eval_criterion = nn.CrossEntropyLoss()

def mean_loss(model, sequences):
    """计算一组诗的平均损失，不记录梯度。"""
    model.eval()
    total_loss = 0.0
    total_poems = 0

    with torch.no_grad():
        for start in range(0, len(sequences), BATCH_SIZE):
            # 所有诗长度相同，可以直接 stack 为 [B, 26]，无需 Padding 与 Padding Mask
            batch = torch.stack(sequences[start:start + BATCH_SIZE]).to(DEVICE)
            # 自回归训练把同一序列错开一位：inputs 与 labels 的形状都是 [B, 25]
            inputs = batch[:, :-1]
            labels = batch[:, 1:]
            logits = model(inputs)
            # CrossEntropyLoss 期望 [样本数, 类别数]，因此把 Batch 维与序列维合并
            # 每首诗的 25 个预测位置都会贡献一个监督信号
            # 用不含标签平滑的纯交叉熵评估，保证验证/绘图损失与未正则化的基线可比
            loss = eval_criterion(logits.reshape(-1, len(tokens)), labels.reshape(-1))

            # 最后一个 Batch 可能不足 BATCH_SIZE，按实际样本数加权才能得到正确的整体验证损失
            batch_size = len(batch)
            total_loss += loss.item() * batch_size
            total_poems += batch_size

    return total_loss / total_poems
```
## 保存最佳参数并提前停止

验证损失下降超过 0.0001 时，保存当前参数；至少训练 10 轮后，连续 10 轮无明显改善便早停。结束时恢复验证效果最好的一轮。

```python
class EarlyStopping:
    def __init__(self, patience, min_delta, min_epochs):
        self.patience = patience
        self.min_delta = min_delta
        self.min_epochs = min_epochs
        self.best_loss = float("inf")
        self.best_epoch = 0
        self.best_state = None
        self.epochs_without_improvement = 0

    def step(self, validation_loss, model, epoch):
        """记录最佳参数；达到耐心上限时返回 True。"""
        # 只有下降幅度超过 min_delta 才视为真正改善，避免把浮点抖动当成新最佳值
        improved = validation_loss < self.best_loss - self.min_delta
        if improved:
            self.best_loss = validation_loss
            self.best_epoch = epoch
            # detach 切断计算图，cpu 避免长期占用加速设备显存，clone 防止后续训练原地改写
            self.best_state = {
                name: value.detach().cpu().clone()
                for name, value in model.state_dict().items()
            }
            self.epochs_without_improvement = 0
        elif epoch >= self.min_epochs:
            # 最少训练轮数结束后，才开始累计没有改善的轮数
            self.epochs_without_improvement += 1
        else:
            self.epochs_without_improvement = 0

        return self.epochs_without_improvement >= self.patience

    def restore_best(self, model):
        model.load_state_dict(self.best_state)
```
## 初始化模型、优化器与训练状态

固定种子初始化模型，再创建 AdamW 和早停器。`train_eval_examples` 固定一组训练诗，供每轮与验证集按同一规则评估。

```python
# 固定模型初始化，便于复现训练结果
torch.manual_seed(42)
model = MiniGPT(len(tokens)).to(DEVICE)

# AdamW 用解耦的权重衰减替代普通 Adam，配合权重共享与 Dropout 一起抑制过拟合
optimizer = torch.optim.AdamW(
    model.parameters(), lr=LEARNING_RATE, weight_decay=WEIGHT_DECAY
)
early_stopping = EarlyStopping(
    patience=EARLY_STOPPING_PATIENCE,
    min_delta=EARLY_STOPPING_MIN_DELTA,
    min_epochs=MIN_EPOCHS,
)
train_losses = []
validation_losses = []
```
## 单轮训练：前向、反向与更新

每轮打乱训练集并分批处理。读代码时抓住一次参数更新的顺序：错位取标签 $\to$ 计算交叉熵 $\to$ 清梯度 $\to$ 反传 $\to$ 更新。

```python
def train_one_epoch(model, examples):
    model.train()
    random.shuffle(examples)
    running_objective = 0.0
    seen_poems = 0

    for start in range(0, len(examples), BATCH_SIZE):
        batch = torch.stack(examples[start:start + BATCH_SIZE]).to(DEVICE)
        inputs = batch[:, :-1]
        labels = batch[:, 1:]

        logits = model(inputs)
        # 将 [B, 25, vocab_size] 展平为 [Bx25, vocab_size]，与展平后的标签逐位置计算交叉熵。
        loss = train_criterion(logits.reshape(-1, len(tokens)), labels.reshape(-1))

        # PyTorch 默认累加梯度，因此每个 Batch 反向传播前必须先清零。
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        running_objective += loss.item() * len(batch)
        seen_poems += len(batch)

    return running_objective / seen_poems
```
## 逐轮验证并决定何时停止

每轮先更新参数，再计算训练子集与验证集的普通交叉熵。`train_obj` 含标签平滑；`train_ce` 和 `val_ce` 可直接对照，早停只看 `val_ce`。

```python
for epoch in range(1, MAX_EPOCHS + 1):
    train_objective = train_one_epoch(model, train_examples)
    # 曲线统一用纯交叉熵、在 eval 模式 (Dropout 关闭) 下评估，训练/验证彼此可比。
    train_loss = mean_loss(model, train_eval_examples)
    validation_loss = mean_loss(model, validation_examples)
    train_losses.append(train_loss)
    validation_losses.append(validation_loss)
    current_lr = optimizer.param_groups[0]["lr"]

    print(
        f"Epoch {epoch:4d} | train_obj={train_objective:.4f} "
        f"| train_ce={train_loss:.4f} | val_ce={validation_loss:.4f} | lr={current_lr:.6f}"
    )

    if early_stopping.step(validation_loss, model, epoch):
        print(
            f"Early Stopping: 达到最少 {MIN_EPOCHS} 轮后，验证损失连续 "
            f"{EARLY_STOPPING_PATIENCE} 轮未改善，"
            f"停止于第 {epoch} 轮。"
        )
        break
```
## 训练日志：第 18 轮最佳，第 28 轮早停
对比第 1、18、28 轮的 `train_ce` 与 `val_ce`：训练集继续变好，验证集却在第 18 轮后不再改善。`train_obj` 含标签平滑，不与两者直接比较。
```text
Epoch    1 | train_obj=6.1134 | train_ce=5.3684 | val_ce=5.3902 | lr=0.002000
...
Epoch   18 | train_obj=4.7902 | train_ce=3.9147 | val_ce=4.6267 | lr=0.002000
...
Epoch   28 | train_obj=4.6807 | train_ce=3.7434 | val_ce=4.6285 | lr=0.002000
```
Early Stopping: 达到最少 10 轮后，验证损失连续 10 轮未改善，停止于第 28 轮。
已恢复第 18 轮参数，最佳验证损失为 4.6267。

**第 1 →→ 18 轮：验证集也进步**  
验证交叉熵从 5.39025.3902 降到 4.62674.6267，第 18 轮是记录中的最低点。

**第 18 →→ 28 轮：验证无改善**  
训练交叉熵仍下降，验证值却略升；连续 1010 轮无改善后早停，并恢复第 18 轮参数。
## 恢复最佳参数并绘制曲线

先用 `restore_best` 恢复第 18 轮参数，再绘制训练、验证曲线；若旧版记录存在，就叠加 64 维模型的验证曲线。

```python
# 后续生成与保存都使用验证损失最低时的模型参数。
early_stopping.restore_best(model)
print(
    f"已恢复第 {early_stopping.best_epoch} 轮参数，"
    f"最佳验证损失为 {early_stopping.best_loss:.4f}。"
)

# 载入上一版 (d_model=64、同为 reg+trim、词表同为约 3500) 的验证曲线用于对照。
# 词表一致，因此这次验证损失可直接比较。
previous_path = DATA_PATH.with_name("mini_gpt_five_char_modern_reg_trim.pt")
previous_validation_losses = None
if previous_path.exists():
    previous_ckpt = torch.load(previous_path, map_location="cpu", weights_only=False)
    previous_validation_losses = previous_ckpt.get("validation_losses")

trained_epochs = range(1, len(train_losses) + 1)
plt.plot(trained_epochs, train_losses, label="Train (d_model=96)")
plt.plot(trained_epochs, validation_losses, label="Validation (d_model=96)")
if previous_validation_losses:
    previous_epochs = range(1, len(previous_validation_losses) + 1)
    plt.plot(
        previous_epochs,
        previous_validation_losses,
        "--",
        color="gray",
        label="Validation (prev d_model=64)",
    )
plt.xlabel("Epoch")
plt.ylabel("Mean poem loss")
plt.legend()
plt.show()
```
## 保存模型与训练记录

新检查点保存**第 18 轮最佳参数**、词表、模型配置和损失记录。生成时用同一词表与结构加载；64 维旧版文件保留供对照。

```python
# 保存到新文件，保留 d_model=64 版 (reg+trim) 作为对照
checkpoint_path = DATA_PATH.with_name("mini_gpt_five_char_modern_reg_trim_d96.pt")
torch.save(
    {
        "model_state_dict": early_stopping.best_state,
        "tokens": tokens,
        "config": {
            "d_model": D_MODEL,
            "heads": HEADS,
            "d_ff": D_FF,
            "num_layers": NUM_LAYERS,
            "max_length": MAX_LENGTH,
            "rope_base": ROPE_BASE,
            "architecture": "llama-like + reg + trim: RoPE + Pre-Norm + RMSNorm + SwiGLU + WeightTying + ",
            "weight_decay": WEIGHT_DECAY,
            "dropout": DROPOUT,
            "label_smoothing": LABEL_SMOOTHING,
            "weight_tying": True,
            "min_token_freq": MIN_TOKEN_FREQ,
        },
        "train_losses": train_losses,
        "validation_losses": validation_losses,
        "best_epoch": early_stopping.best_epoch,
        "best_validation_loss": early_stopping.best_loss,
        "final_learning_rate": optimizer.param_groups[0]["lr"],
    },
    checkpoint_path,
)
print("最佳模型已保存：", checkpoint_path)
```
## 推理：用前缀一步步生成字符

训练时能同时监督多个位置；生成时后文尚不存在，只能从 `<BOS>` 和可选提示字起步。模型反复执行下面的循环，**每次只生成一个字符**。

当前前缀 $\to$ 最后位置 logits $\to$ 调整并筛选候选 $\to$ 采样新字 $\to$ 追加到前缀

**Top-k 采样**
只在最高分的 $k$ 个候选中按概率抽取，兼顾合理性与变化。

**温度与重复惩罚**
温度调节随机性；重复惩罚压低已用字分数，减少连续重复。

**自由生成**
标点与停止时机也由模型决定；训练语料的诗形不会被代码强制执行。

**实现取舍：** 本例没有 KV Cache，每追加一个字都重算完整前缀。短诗的开销较小，也更容易看清逐字生成的计算流程。
## 采样一个字：重复惩罚、温度与 Top-k

采样前依次降低重复 Token 的分数、用温度调节分布、从 Top-k 候选中抽取。本例的参数分别是重复惩罚 \(1.3\)、温度 \(0.8\)、候选数 \(20\)。

```python
def sample_top_k(logits, temperature=0.8, top_k=20):
    """从分数最高的 k 个候选中按概率采样。"""
    # temperature < 1 会放大高分候选间的差异，使采样更保守；> 1 则增加随机性
    logits = logits / temperature

    # 防止 top_k 大于词表大小，只在最高分的 k 个 Token 中重新归一化并采样。
    k = min(top_k, len(logits))

    top_logits, top_ids = torch.topk(logits, k)
    probabilities = torch.softmax(top_logits, dim=-1)
    sampled_index = torch.multinomial(probabilities, num_samples=1).item()
    return top_ids[sampled_index].item()

def penalize_repeats(logits, used_ids, penalty):
    """CTRL 式重复惩罚：对已出现过的 Token，正 logit 除以惩罚、负 logit 乘以惩罚，
    压低它们再次被采样的概率，缓解“花花花”“寒寒寒”这类字符重复。"""
    if penalty == 1.0 or not used_ids:
        return logits
    unique_ids = torch.tensor(sorted(set(used_ids)), device=logits.device)
    scores = logits[unique_ids]
    logits[unique_ids] = torch.where(scores > 0, scores / penalty, scores * penalty)
    return logits
```
## 自由生成：模型决定何时停

从 `<BOS>` 和可选提示字起步，每次取末位 logits 采样并追加一个字符。标点由模型决定；采到 `<EOS>` 或达到长度上限就停止。

```python
@torch.no_grad()
def generate_text(prompt="", max_new_tokens=31, temperature=0.8, top_k=20, repetition_penalty=1.3):
    """自由生成：标点位置与停止时机都由模型预测。"""
    model.eval()
    generated = list(prompt)
    ids = [BOS] + encode(prompt)

    for _ in range(min(max_new_tokens, MAX_LENGTH - len(ids))):
        # 当前实现没有 KV Cache：每一步都重新计算完整前缀，只取最后位置的 logits
        logits = model(torch.tensor(ids, dtype=torch.long, device=DEVICE))[-1].clone()

        # 屏蔽 <BOS> 与 <UNK>：前者不应出现在正文，后者只是罕见字占位符
        logits[BOS] = float("-inf")
        logits[UNK] = float("-inf")

        # 对已生成的 Token 施加重复惩罚，再做 Top-k 采样
        logits = penalize_repeats(logits, ids, repetition_penalty)
        next_id = sample_top_k(logits, temperature, top_k)

        if next_id == EOS:
            break
        ids.append(next_id)
        generated.append(tokens[next_id])

    return "".join(generated)
```

## 从下一字预测，到诗句生成

Mini-GPT 的目标始终是：根据前缀预测下一个 Token。

| 字符 ID | $\to$ | Embedding | $\to$ | GPT Block x 4 | $\to$ | 词表 logits | $\to$ | 下一个字 |
| :---- | :---- | :-------- | :---- | :------------ | :---- | :-------- | :---- | :--- |

*   **训练：** 因果遮罩只读前缀，同时监督各位置。
*   **生成：** 只取末位预测，采样后逐字追加。

---

**现代组件带来了什么**
*   **RoPE：** 让 Q/K 的匹配感知相对位置。
*   **Pre-Norm + RMSNorm：** 让残差堆叠更易优化。
*   **SwiGLU：** 按输入调节中间特征。
*   **无偏置 + 权重共享：** 减少模型参数。

**自由生成的成果与边界**
*   **格式无硬约束：** 语料统一，自由生成仍可能偏离。
*   **模型选择字句：** 能写出局部有诗意的搭配。
*   **质量仍有限：** 连贯、押韵和平仄尚不稳定。
*   **推理仍可优化：** 未用 KV Cache，每步重算前缀。

---

从字符到诗句，Mini-GPT 跑通了完整链路；能生成一首诗，不等于已稳定掌握五言与格律。