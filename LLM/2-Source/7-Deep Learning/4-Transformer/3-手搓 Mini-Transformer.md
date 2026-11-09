# 用 Mini-Transformer 完成英译中

- **核心任务**：将 Encoder 和 Decoder 的数据流写成代码。
    
- **运行机制**：模型根据英文和已有中文前缀，预测下一个中文 Token。
## 示例

- **英文输入**：`there is a cat under the table`
    
- **中文译文**：`桌子 下面 有 一只 猫`
## 代码实现设定

- **单样本处理**：每次处理一对句子。
    
- **无 Padding**：无需补齐长度，张量中无批次维度。
    
- **核心关注点**：理解每个位置上的注意力、特征变换和输出计算。
## 变量与实现

- **变量定义**：
    
    - $S$：英文长度
        
    - $T$：中文前缀长度
        
    - $D$：每个 Token 的向量维度
- **实现细节**：
    
    - 注意力：按矩阵公式实现。
        
    - 多头计算和层堆叠：用循环展开。

# Transformer 的整体数据流

## 输入处理
英文和中文前缀分别查出词向量，再加入位置编码。
## 编码器 (Encoder)
处理英文，生成包含上下文信息的表示，供 Decoder 读取。
## 解码器 (Decoder)
先用因果自注意力处理中文前缀，再通过交叉注意力读取英文表示。
## 输出概率
将中文表示投影到词表，得到候选 Token 的分数，再用 Softmax 转成概率。

# 各个模块在代码中的对应位置

最终的代码结构大概是这样的，稍后我们逐模块实现
```python
# 输入处理
class PositionalEncoding: ...  # 为每个位置生成固定向量
class TokenEmbedding: ...      # 查词向量，再加入位置编码
# 注意力计算
def attention(): ...           # 用矩阵计算注意力，并按需应用因果掩码
class AttentionHead: ...       # 学习一个头的 Q、K、V 投影
class MultiHeadAttention: ...  # 逐个运行各头，再拼接结果
# 编码器与解码器
class FeedForward: ...         # 单独加工每个位置的特征
class EncoderLayer: ...        # 一层：自注意力 -> FFN，配合 Add & Norm
class Encoder: ...             # 依次运行多个编码器层
class DecoderLayer: ...        # 一层：掩码自注意力 -> 交叉注意力 -> FFN
class Decoder: ...             # 依次运行多个解码器层
# 串联完整模型
class MiniTransformer:
    def encode(): ...          # 编码英文
    def decode(): ...          # 根据中文前缀和英文表示计算词表分数
    def forward(): ...         # 串联编码与解码
```
# 准备运行环境

本例使用 Python 3.12 和 PyTorch，模型与数据规模较小，在 CPU 上即可完成训练。

项目使用 `uv` 管理环境，`pyproject.toml` 声明依赖，`uv.lock` 锁定版本。在项目根目录执行以下命令，创建环境、安装依赖并启动 Notebook。

```python
# 安装项目锁定的依赖，创建 .venv 环境
uv sync --locked
# 从项目环境启动 Notebook
uv run jupyter lab notebook/transformer_loop.ipynb
```

如果使用 VS Code，打开 Notebook 后，在右上角的内核选择器中选择项目的`.venv/bin/python`。

# 导入依赖与模型参数

导入模型实现所需的依赖，固定随机种子，再定义后续模块共用的参数。

```python
import math
import random
import torch
from torch import nn
# 固定随机种子，便于重复运行
random.seed(42)
torch.manual_seed(42)
torch.set_num_threads(1)
# 模型参数
D = 32          # 每个 Token 的向量维度；本例要求为正偶数
HEADS = 2       # 注意力头数；D 必须能被 HEADS 整除
D_FF = 64       # FFN 中间层的维度
NUM_LAYERS = 2  # Encoder 和 Decoder 各自堆叠的层数
MAX_LENGTH = 32 # 位置编码表支持的最大 TOKEN 数
```
# 准备英中句对

先准备 8 对英中句子。en_cn_pairs 中的每一项都是一个二元组，前面是英文，后面是对应的中文译文；中文已经用空格分好词。

```python
en_cn_pairs = [
    ("there is a cat under the table", "桌子 下面 有 一只 猫"),
    ("there is a dog on the chair", "椅子 上面 有 一只 狗"),
    ("there is a cat on the chair", "椅子 上面 有 一只 猫"),
    ("there is a dog under the table", "桌子 下面 有 一只 狗"),
    ("there is a small cat on the table", "桌子 上面 有 一只 小 猫"),
    ("there is a small dog under the chair", "椅子 下面 有 一只 小 狗"),
    ("there is a black cat under the chair", "椅子 下面 有 一只 黑色 猫"),
    ("there is a black dog on the table", "桌子 上面 有 一只 黑色 狗"),
]
```
# Token、词表与 Token ID

模型需要数值输入，因此先把句子拆成 Token。本例按空格拆分，每个词就是一个 Token。

把同一种语言中的 Token 去重、排序，就得到词表；再从 0 开始为每一项编号，得到 Token ID。英文和中文分别建立自己的词表。
![](Pasted%20image%2020261108100143.png)
编号只是查表的索引，相邻编号不代表词义相近。模型还会训练一张超大的“字典表”，也就是 Embedding 表。当模型拿到一个 Token ID 时，用这个 ID 去 Embedding 表里查询就知道语义了。
# 建立词表与特殊 Token

中文词表额外加入 `<BOS>` 和 `<EOS>`：前者给 Decoder 一个开始生成的输入，后者让模型学会何时停止。它们也有自己的 Token ID。

```python
# 1. 分别收集英文和中文 Token，去重、排序，建立词表。
source_words = sorted({word for english, chinese in en_cn_pairs for word in english.split()})
target_words = ["<BOS>", "<EOS>"] + sorted(
    {word for english, chinese in en_cn_pairs for word in chinese.split()}
)
# 列表用于“ID -> Token”，字典用于“Token -> ID”。
source_ids = {word: i for i, word in enumerate(source_words)}
target_ids = {word: i for i, word in enumerate(target_words)}
BOS = target_ids["<BOS>"]
EOS = target_ids["<EOS>"]
```

# 输入与标签为什么错开一位

训练时，每个位置都要预测下一个 Token。给中文译文两端加入 `<BOS>` 和 `<EOS>`，得到完整目标 target；去掉末尾作为输入，去掉开头作为监督标签。

| 训练位置           | 0       | 1   | 2   | 3   | 4   | 5       |
| -------------- | ------- | --- | --- | --- | --- | ------- |
| **Decoder 输入** | `<BOS>` | 桌子  | 下面  | 有   | 一只  | 猫       |
| **监督标签**       | 桌子      | 下面  | 有   | 一只  | 猫   | `<EOS>` |
(teacher forcing)
```python
decoder_input = target[:-1]  # 去掉末尾 EOS
labels = target[1:]          # 去掉开头 BOS
```

训练时，Decoder 读取真实译文前缀，这称为教师强制 (Teacher Forcing)；因果掩码保证当前位置只能读取自己及之前的输入。推理时则从 `<BOS>` 开始，逐次追加模型自己的预测，直到生成 `<EOS>` 或达到长度上限。

# 将句子转换为 Token ID 张量

将句对转换成 Token ID 张量，存入 `examples`。每项保留英文输入 `[S]` 和完整中文目标 `[T + 1]`，`S` 是英文长度，`T` 是错位切分后的中文输入长度；训练时再取出形状均为 `[T]` 的输入与标签。


```python
# 2. 将每对句子转换为一维整数张量，中文目标两端加入 BOS 和 EOS。
examples = []
for english, chinese in en_cn_pairs:
    source = [source_ids[word] for word in english.split()]
    target = [BOS] + [target_ids[word] for word in chinese.split()] + [EOS]
    examples.append((
        torch.tensor(source, dtype=torch.long),
        torch.tensor(target, dtype=torch.long),
    ))

**`examples[0]`: 第一对句子的处理结果**
```

| **英文输入**   | `tensor([10, 5, 0, 2, 11, 9, 8])` | `[S] = [7]`     |
| ---------- | --------------------------------- | --------------- |
| **完整中文目标** | `tensor([0, 7, 4, 6, 2, 10, 11])` | `[T + 1] = [7]` |
# 词向量与位置编码

Embedding 根据 Token ID 查出一个 DD 维词向量，使它能够参与后续计算；同一个 Token 会查出相同的向量，因此还需要加入位置信息，区分它出现在句子的哪里。
![](Pasted%20image%2020261108101510.png)
# 利用正弦、余弦对位置编码

位置编码要和词向量逐元素相加，所以它也是一个 DD 维向量。把这 DD 维相邻两维分成一组，共 D/2D/2 组；每组代入同一个角度，一维取正弦，一维取余弦，因此本例要求 DD 为正偶数。
$$PE_{pos, 2i} = sin(pos / 10000^{2i/D})$$
$$PE_{pos, 2i+1} = cos(pos / 10000^{2i/D})$$

$pos$ 是位置编号，$i$ 是组号。$i$ 越大，分母 $10000^{2i/D}$ 越大，角度随位置增长得越慢，也就是**每组各有自己的频率**：靠前的组转得快，靠后的组转得慢。
![](Pasted%20image%2020261108102408.png)
**时钟比喻：**

- **秒针**：最快，区分相邻位置
    
- **分针**：较慢，标记中等跨度
    
- **时针**：最慢，刻画整体位置
    

这就像看时钟：只盯着秒针，转满一圈就会重复；秒针、分针、时针快慢不同，合起来才能唯一读出时刻。

$D/2$ 组编码同理，快的组区分相邻位置，慢的组刻画大范围，组合起来让每个位置都拿到一份独特的编码。

# 实现 PositionalEncoding

先生成固定位置表，再逐行相加。这里 LL 表示当前句子的长度，输入和输出均为 [L,D][L,D]，且 LL 不能超过位置表的最大长度。

```python
class PositionalEncoding(nn.Module):
    def __init__(self, d_model, max_length):
        super().__init__()
        pe = torch.zeros(max_length, d_model)
        for pos in range(max_length):
            for i in range(d_model // 2):
                angle = pos / (10000.0 ** (2 * i / d_model))
                pe[pos, 2 * i] = math.sin(angle)
                pe[pos, 2 * i + 1] = math.cos(angle)
        # 固定位置表，不参与梯度更新。
        self.register_buffer("pe", pe)
    def forward(self, x):
        rows = []
        for pos in range(len(x)):
            rows.append(x[pos] + self.pe[pos])  # 两个 [D] 向量逐元素相加。
        return torch.stack(rows)  # 把多行 [D] 叠成 [句长, D]。
```
# 实现 TokenEmbedding

把词向量查表、缩放和位置编码放在同一个模块中，输入一维 ID 序列 $[L]$，输出可送入 Encoder 或 Decoder 的 $[L,D]$ 表示。

```python
class TokenEmbedding(nn.Module):
    def __init__(self, vocab_size):
        super().__init__()
        # 创建形状为 [vocab_size, D] 的词向量表，每个 Token ID 对应一行。
        self.embedding = nn.Embedding(vocab_size, D)
        self.position = PositionalEncoding(D, MAX_LENGTH)

    def forward(self, token_ids):
        # 输入为一维 Token ID 张量，形状为 [L]。
        # 按 ID 查出每个 Token 的词向量，得到 [L, D]，再按论文乘以 sqrt(D)。
        x = self.embedding(token_ids) * math.sqrt(D)
        return self.position(x)  # 加入位置编码，输出形状仍为 [L, D]。
```

## 注意力如何汇总其他位置的信息

每个 Query 与可以读取的 Key 计算相关性分数，再按归一化后的权重对 Value 加权求和，得到融合其他位置信息的新表示。

$$
\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^\top}{\sqrt{D_h}}\right)V
$$

$Q$ 的形状为 $[L_q, D_h]$，$K$、$V$ 的形状为 $[L_k, D_h]$。$L_q$ 是 Query 数，$L_k$ 是 Key/Value 数，$D_h$ 是单个头的维度。

点积得到 $[L_q, L_k]$ 的分数表，除以 $\sqrt{D_h}$ 控制数值尺度。Softmax 沿每一行的 Key 方向归一化，再与 $V$ 相乘，输出 $[L_q, D_h]$。
## 一个 Query 的注意力计算
![](Pasted%20image%2020261108110219.png)
以 cat 所在位置为例，用它的 Query 与各个 Key 打分，沿 Key 方向做 Softmax，再汇总对应的 Value。本例图中的 dkdk​、dvdv​ 都对应单头维度 Dh=16Dh​=16。
## 因果掩码限制中文位置的可见范围

训练输入包含真实中文前缀。位置 ii 预测下一个词时，只能读取位置 00 到 ii，避免提前读取后面的答案。
![](Pasted%20image%2020261108110504.png)
$$
\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^\top}{\sqrt{D_h}} + M\right)V
$$
图中展示加到分数表上的掩码 MM：加 00 保留原分数，加 −∞−∞ 使未来位置在 Softmax 后的权重为 00。
## 掩码注意力的完整计算流程
![](Pasted%20image%2020261108110903.png)
图中的分数与权重用于说明流程，不作为逐项计算结果。按本例记号，中文分数表和掩码均为 $[T, T]$，单头输出为 $[T, D_h]$；Softmax 沿每一行的 Key 方向计算。
## 用矩阵运算实现注意力
一次计算所有 Query 对所有 Key 的分数，得到 $[L_q, L_k]$ 矩阵。按需屏蔽未来位置，再沿 Key 方向归一化并汇总 Value，输出 $[L_q, D_h]$；因果掩码仅用于 Decoder 自注意力。
```python
def attention(q, k, v, causal=False):
    # [Lq, Dh] @ [Dh, Lk] -> [Lq, Lk], 每行是一个 Query 的分数。
    scores = q @ k.T / math.sqrt(q.shape[-1])
    if causal:
        # 右上三角为 True，表示未来位置 (j > i) 需要屏蔽。
        mask = torch.triu(torch.ones_like(scores, dtype=torch.bool), diagonal=1)
        scores = scores.masked_fill(mask, float("-inf"))
    # 沿 Key 方向归一化；被屏蔽位置的权重为 0。
    weights = torch.softmax(scores, dim=-1)  # [Lq, Lk]
    return weights @ v  # [Lq, Lk] @ [Lk, Dh] -> [Lq, Dh]
```
## 单个注意力头的 Q、K、V 投影
![](Pasted%20image%2020261108111245.png)
以自注意力为例，三套投影读取同一份输入。本例将完整的 $D=32$ 维输入分别投影到 $D_h=16$维；图中省略偏置，实际线性层包含可学习的偏置。交叉注意力的 Q 来自 Decoder，K、V 来自 Encoder。
## 单个注意力头的投影与计算
一个头有独立的 Q、K、V 投影，将完整的 $D$ 维输入映射到 $D_h = D/\text{HEADS}$ 维。本例 $D=32$、头数为 2，所以每个头的维度为 16；$Query$ 和 $Key/Value$ 的位置数可以不同。
```python
class AttentionHead(nn.Module):
	def __init__(self):
		super().__init__()
		head_dim = D // HEADS  # 单个头的维度 Dh，本例为 32 / 2 = 16。
		# 分别学习 Q、K、V 的投影，将每个位置从 D 维映射到 Dh 维。
		self.q_proj = nn.Linear(D, head_dim) 
		self.k_proj = nn.Linear(D, head_dim)
		self.v_proj = nn.Linear(D, head_dim)
	def forward(self, query, key, value, causal=False):
	    q = self.q_proj(query)  # [Lq, D] -> [Lq, Dh]
	    k = self.k_proj(key)    # [Lk, D] -> [Lk, Dh]
	    v = self.v_proj(value)  # [Lk, D] -> [Lk, Dh]
	    # 用 Q、K 计算权重，再汇总 V；本例仅 Decoder 自注意力启用因果掩码。
	    return attention(q, k, v, causal)  # 输出 [Lq, Dh]。
```
## 多头独立计算、拼接与输出投影
![](Pasted%20image%2020261108111819.png)
各个头读取相同的输入，使用各自独立的参数，分别计算注意力。
本例使用 2 个头，每个头输出 \([L_q, 16]\)，沿特征维拼接后为 \([L_q, 32]\)；输出投影保持这一形状。

## 合并多个注意力头
各个头读取相同的输入，使用各自的投影参数分别计算。将多份 $[L_q, D_h]$ 沿特征维度拼接为 $[L_q, D]$，再通过输出投影组合各个头的信息。
```python
class MultiHeadAttention(nn.Module):
    def __init__(self):
        super().__init__()
        # 每个头分别学习自己的 Q、K、V 投影，参数相互独立。
        self.heads = nn.ModuleList([AttentionHead() for _ in range(HEADS)])
        # 对拼接后的特征做输出投影，融合各个头的信息，维度保持 D。
        self.out_proj = nn.Linear(D, D)
    def forward(self, query, key, value, causal=False):
        outputs = []
        # 所有头读取相同输入，各自得到一个 [Lq, Dh] 的结果。
        for head in self.heads:
            outputs.append(head(query, key, value, causal))
        # 沿特征维拼接: HEADS 个 [Lq, Dh] -> [Lq, HEADS * Dh] = [Lq, D]
        joined = torch.cat(outputs, dim=-1)
        return self.out_proj(joined)  # 输出仍为 [Lq, D]。
```
## FFN 对各个位置分别计算
![](Pasted%20image%2020261108112301.png)
每个位置分别经过两次线性变换与 ReLU，特征维度依次为 $32 \to 64 \to 32$，序列长度保持不变。
所有位置共用同一套参数。FFN 加工每个位置自身的特征，不在这一步交换位置信息。
## FFN 加上每个位置的特征
注意力完成位置间的信息交换后，FFN 对每个位置分别做非线性变换。特征先从 $D$ 维扩展到 $D_{FF}$ 维，再映射回 $D$ 维；所有位置共用参数。
$$
\text{FFN}(x) = \text{ReLU}(xW_1 + b_1)W_2 + b_2
$$
```python
class FeedForward(nn.Module):
    def __init__(self):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(D, D_FF),  # 升维: [L, D] -> [L, D_FF], 本例 32 -> 64。
            nn.ReLU(),           # 引入非线性, 形状保持 [L, D_FF]。
            nn.Linear(D_FF, D),  # 降维: [L, D_FF] -> [L, D], 本例 64 -> 32。
        )
    def forward(self, x):
	    # 各位置使用相同的参数, 句子 L 保持不变.
	    return self.network(x)  # 输入和输出均为 [L, D].
```
## Encoder 层与层间堆叠
![](Pasted%20image%2020261108113018.png)
*   每层接收上一层的输出，各层参数独立。本例输入为英文，不添加图中示意的 CLS 或 SEP。
*   图中 Q、K、V 是多头的合并表示，单个头的特征维度为 $D_h = 16$。各层输出均为 $[S, D]$，最后得到供 Decoder 读取的 encoder_output。
## Encoder 层中的残差连接与归一化

英文表示先经过多头自注意力，再经过 FFN；每个子层之后都进行残差相加和层归一化，也就是 Add & Norm。

$$
y = \text{LayerNorm}(x + \text{Sublayer}(x))
$$

$x$ 是进入当前子层的表示，Sublayer 对应自注意力或 FFN。残差保留输入信息并提供更直接的梯度路径，层归一化在每个位置的 $D$ 个特征上计算，帮助稳定训练。

自注意力的 Q、K、V 都来自当前英文表示，所有英文位置可以相互读取。各步都保持 $[S, D]$，因此能够残差相加，并送入下一层。
## 实现 EncoderLayer

按自注意力、FFN 的顺序处理英文表示，每次相加都使用进入当前子层前的 $x$。输入和输出均为 $[S, D]$。

```python
class EncoderLayer(nn.Module):
    def __init__(self):
        super().__init__()
        self.self_mha = MultiHeadAttention()  # 多头自注意力：在英文位置之间交换信息。
        self.ffn = FeedForward()              # FFN：逐位置加工特征。
        self.norm1 = nn.LayerNorm(D)          # 自注意力残差相加后的归一化。
        self.norm2 = nn.LayerNorm(D)          # FFN 残差相加后的归一化。

    def forward(self, x):
        # 输入 x 已经过 Embedding 和位置编码，形状为 [S, D]。
        # 1-2. 多头自注意力 -> Add & Norm。
        # Q、K、V 都来自 x；所有英文位置可以相互读取。
        x = self.norm1(x + self.self_mha(x, x, x))
        
        # 3-4. FFN -> Add & Norm；残差使用进入 FFN 前的 x。
        x = self.norm2(x + self.ffn(x))
        return x  # [S, D]，作为下一层的输入。
```

## 堆叠 Encoder 层

每层接收上一层的输出，各层参数独立，形状始终为 $[S, D]$。本例堆叠 2 层，最后的输出就是供 Decoder 读取的 encoder_output。

```python
class Encoder(nn.Module):
    def __init__(self, num_layers):
        super().__init__()
        # 各层结构相同，参数独立。
        self.layers = nn.ModuleList([EncoderLayer() for _ in range(num_layers)])

    def forward(self, x):
        # 英文输入表示 -> 第 1 层 -> 第 2 层 -> ... -> 最后一层。
        for layer in self.layers:
            x = layer(x)  # 每层均执行: 自注意力 -> Add & Norm -> FFN -> Add & Norm。
        return x  # [S, D], 作为 Decoder 读取的 encoder_output。
```
## Decoder 的三类子层与英文信息读取
![](Pasted%20image%2020261108114319.png)
*   中文前缀 ID 的形状是 $[T]$，词嵌入后才是 $[T, D]$。图右侧 Q、K、V 标注的是投影前的来源表示。
*   交叉注意力单头投影后，Q 为 $[T, D_h]$，K、V 为 $[S, D_h]$。每层更新中文表示，并读取同一份英文 encoder_output。
## Decoder 层如何结合中文与英文

Decoder 接收中文前缀表示 \([T, D]\) 和英文编码结果 \([S, D]\)，依次执行下面的计算，每个子层之后都进行 Add & Norm。

| 子层 | 处理的信息 |
| :--- | :--- |
| 因果自注意力 | Q、K、V 都来自中文表示，每个位置只读取自己及之前的中文位置。 |
| 交叉注意力 | Q 来自更新后的中文表示，K、V 来自英文编码结果，读取相关英文信息。 |
| FFN | 分别加工每个中文位置的特征。 |

交叉注意力每个头的分数表为 $[T, S]$，合并各头后仍输出 $[T, D]$。因此残差相加使用中文表示，英文编码结果在这里保持不变。
## 实现 DecoderLayer

用 `causal=True` 限制中文自注意力，再让中文 Query 读取英文 Key、Value。三个子层的输出都保持 $[T, D]$。

```python
class DecoderLayer(nn.Module):
    def __init__(self):
        super().__init__()
        self.self_attn = MultiHeadAttention()  # 因果自注意力：读取允许看到的中文前缀。
        self.cross_attn = MultiHeadAttention() # 交叉注意力：根据中文表示读取英文 encoder_output。
        self.ffn = FeedForward()               # FFN：逐位置加工中文特征。
        self.norm1 = nn.LayerNorm(D)           # 自注意力残差相加后的归一化。
        self.norm2 = nn.LayerNorm(D)           # 交叉注意力残差相加后的归一化。
        self.norm3 = nn.LayerNorm(D)           # FFN 残差相加后的归一化。

    def forward(self, x, encoder_output):
        # x: [T, D], 中文前缀表示; encoder_output: [S, D], 英文编码结果。
        # 1-2. 因果多头自注意力 -> Add & Norm; 位置 i 只能读取 0 到 i。
        x = self.norm1(x + self.self_attn(x, x, x, causal=True))

        # 3-4. 多头交叉注意力 -> Add & Norm。
        # Q 来自中文 x, K、V 来自英文 encoder_output; 输出与 x 都是 [T, D]。
        x = self.norm2(x + self.cross_attn(x, encoder_output, encoder_output))

        # 5-6. FFN -> Add & Norm; 残差使用进入 FFN 前的 x。
        x = self.norm3(x + self.ffn(x))
        return x  # [T, D], 作为下一层的中文输入。
```

## 堆叠 Decoder 层

各层依次更新中文表示，但始终读取 Encoder 最后一层输出的同一份英文编码结果。每层有自己独立的注意力、FFN 和归一化参数。

```python
class Decoder(nn.Module):
    def __init__(self, num_layers):
        super().__init__()
        # 堆叠多个独立的 DecoderLayer，各层拥有自己的注意力、FFN 和归一化参数。
        self.layers = nn.ModuleList([DecoderLayer() for _ in range(num_layers)])

    def forward(self, x, encoder_output):
        # 中文输入表示 -> 第 1 层 -> 第 2 层 -> ... -> 最后一层。
        for layer in self.layers:
            # 每层更新中文 x，并读取同一份英文 encoder_output；encoder_output 不在此处更新。
            x = layer(x, encoder_output)
        return x  # [T, D], 后续再投影到中文词表，计算各 Token 的分数。
```

## 实现 MiniTransformer
串联两种语言的输入处理、Encoder、Decoder 和输出投影。训练调用完整前向过程，生成时分别调用编码与解码入口。
```python
class MiniTransformer(nn.Module):
    def __init__(self):
        super().__init__()
        # 两种语言分别使用自己的词向量表。
        # TokenEmbedding 内部已完成：查词向量 -> 乘以 sqrt(D) -> 加位置编码。
        self.source_embedding = TokenEmbedding(len(source_words))
        self.target_embedding = TokenEmbedding(len(target_words))
        # Encoder 编码英文；Decoder 根据中文前缀读取英文编码结果。
        self.encoder = Encoder(NUM_LAYERS)
        self.decoder = Decoder(NUM_LAYERS)
        # 将每个中文位置的 D 维表示，映射为中文词表中各 Token 的分数。
        self.output_projection = nn.Linear(D, len(target_words))
    def encode(self, source):
        # source 是英文 Token ID，形状为 [S]。
        # TokenEmbedding 加入词向量与位置信息：[S] -> [S, D]。
        # Encoder 输出仍为 [S, D]；推理时只需计算一次，供各生成步骤复用。
        return self.encoder(self.source_embedding(source))
    def decode(self, target, encoder_output):
        # target 是中文前缀的 Token ID：[T]；encoder_output 是英文表示：[S, D]。
        x = self.target_embedding(target)  # 查词向量、缩放并加位置编码：[T] -> [T, D]。
        x = self.decoder(x, encoder_output)  # 因果自注意力与交叉注意力处理后，仍为 [T, D]。
        # 输出 logits：[T, 中文词表大小]，每行用于预测对应位置的下一个 Token。
        # 训练时直接交给 CrossEntropyLoss，无需在这里先做 Softmax。
        return self.output_projection(x)
    def forward(self, source, target):
        # 完整前向过程：先编码英文，再结合中文前缀计算词表分数。
        # 训练时 target 传入完整中文目标去掉末尾 EOS 后的序列。
        encoder_output = self.encode(source)
        return self.decode(target, encoder_output)
```
## 实现训练循环

中文输入去掉末尾 EOS，标签去掉开头 BOS。因果掩码在 Decoder 内部生效，使每个位置只能读取它可以看到的真实前缀。

```python
# 1. 创建模型实例，并固定初始化，方便重复运行时比较结果。
torch.manual_seed(42)
model = MiniTransformer()

# 2. 配置损失函数和优化器。
# CrossEntropyLoss 接收原始 logits，不需要提前做 Softmax。
criterion = nn.CrossEntropyLoss()
# model.parameters() 收集整个模型的可训练参数；Adam 用学习率 0.003 更新它们。
optimizer = torch.optim.Adam(model.parameters(), lr=0.003)
losses = []  # 记录每轮训练的平均句子损失，用于画图。

model.train()  # 切换到训练模式；真正的计算和参数更新在下面的循环中进行。
for epoch in range(100):  # 一轮 (Epoch) 会遍历全部 8 对句子，共训练 100 轮。
    random.shuffle(examples)  # 每轮打乱句对顺序，避免总按固定顺序学习。
    total_loss = 0.0
    for source, target in examples:  # 一次处理一对句子，并更新一次参数。
        # 3. 前向计算：英文作为 Encoder 输入，真实中文前缀作为 Decoder 输入。
        # target[:-1] 去掉末尾 EOS；输出 logits 的形状为 [T, 中文词表大小]。
        logits = model(source, target[:-1])
        # target[1:] 去掉开头 BOS，作为各位置要预测的下一个 Token，形状为 [T]。
        # 默认对当前句子中所有预测位置的损失取平均。
        loss = criterion(logits, target[1:])

        # 4. 更新参数：先清除上一次的梯度，再计算本次梯度，最后由 Adam 更新参数。
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        total_loss += loss.item()  # 只累计损失数值，不保留计算图。

    # 5. 对本轮 8 个句子的损失取平均，记录并定期打印训练进度。
    losses.append(total_loss / len(examples))
    if epoch == 0 or (epoch + 1) % 20 == 0:
        print(f"Epoch {epoch + 1:3d} | loss={losses[-1]:.4f}")

# 6. 绘制损失曲线，观察模型学习这些句子时的损失是否逐渐下降。
plt.plot(range(1, 101), losses)
plt.xlabel("Epoch")
plt.ylabel("Mean sentence loss")
plt.show()
```

## 从 BOS 开始逐个生成中文

英文只编码一次，每一步根据当前前缀重新计算 Decoder 输出，选择最后一个位置的预测。预测到 EOS 时立即停止。

```python
@torch.no_grad()
def translate(english):
    model.eval()

    # 1. 将英文按空格分词，再查词表得到一维 Token ID 张量，形状为 $[S]$。
    source = torch.tensor([source_ids[word] for word in english.split()])
    # 英文只需编码一次，得到 $[S, D]$ 的表示，后续每一步生成都复用它。
    encoder_output = model.encode(source)
    prefix = [BOS]  # 中文前缀从 BOS 开始，后续逐步追加模型自己生成的 Token。

    # 2. 逐个生成中文 Token，最多生成 16 步，同时保证输入不超出位置表容量。
    for step in range(min(16, MAX_LENGTH)):
        target = torch.tensor(prefix)  # 将当前完整前缀转为 ID 张量，形状为 $[T]$。
        # Decoder 读取中文前缀和英文表示，输出 $[T, 中文词表大小]$ 的分数。
        logits = model.decode(target, encoder_output)
        # 只取最后一个位置的分数，用来预测前缀之后的下一个 Token。
        # 选择分数最高的 Token ID。
        next_id = logits[-1].argmax().item()
        if next_id == EOS:
            break  # 预测到结束标记就停止，不将 EOS 加入译文。
        prefix.append(next_id)  # 将预测结果追加到前缀，作为下一步的输入。

    # 3. 去掉开头的 BOS，将其余 ID 转回中文 Token，再拼成译文。
    return "".join(target_words[i] for i in prefix[1:])
```
## 逐 Token 观察生成过程

```python
# 1. 取第一对句子，参考译文只用于最后对照，不作为模型输入。
trace_english, trace_reference = en_cn_pairs[0]
trace_reference = trace_reference.replace(" ", "")
# 将英文转换为 Token ID 张量，形状为 \([S]\)。
trace_source = torch.tensor([source_ids[word] for word in trace_english.split()])

# trace_prefix: 送入 Decoder 的中文前缀，从 BOS 开始。
# trace_rows: 每步的展示记录，保存步数、输入前缀、预测 Token 及其概率。
# trace_ids: 每步预测出的 Token ID，包括模型可能生成的 EOS。
trace_prefix, trace_rows, trace_ids = [BOS], [], []
model.eval()  # 切换到评估模式。
with torch.no_grad():  # 只观察生成过程，无需记录梯度。
    # 2. 英文只编码一次，得到 \([S, D]\) 的表示，供所有生成步骤复用。
    trace_encoder_output = model.encode(trace_source)
    for step in range(min(16, MAX_LENGTH)):  # 与 translate 使用相同的生成上限。
        # 当前前缀长度为 T, Decoder 输出形状为 [T, 中文词表大小].
        logits = model.decode(torch.tensor(trace_prefix), trace_encoder_output)
        # 最后一个位置用于预测下一个 Token; Softmax 将词表分数转换为概率, 供展示使用.
        probabilities = logits[-1].softmax(dim=-1)
        next_id = logits[-1].argmax().item()  # 贪心选择分数最高的 Token ID。

        # 3. 先记录本步输入的前缀，再追加预测结果，保证表格每行能对应本次计算。
        prefix_text = " ".join(target_words[i] for i in trace_prefix)
        trace_rows.append((step + 1, prefix_text, target_words[next_id], probabilities[next_id].item()))
        trace_ids.append(next_id)
        if next_id == EOS:
            break  # EOS 已记录在展示数据中，但不加入下一步前缀或最终译文。
        trace_prefix.append(next_id)  # 下一步以前缀加上本步预测结果作为输入。

# 4. 判断是否因生成 EOS 而结束；否则说明达到了生成长度上限。
trace_finished = trace_ids[-1] == EOS
# 去掉开头的 BOS，将中文 Token 拼成完整译文。
trace_text = "".join(target_words[i] for i in trace_prefix[1:])
assert trace_text == translate(trace_english)  # 展开的演示与正式翻译函数应一致。
```
## 每一步的前缀与所选 Token

输入 there is a cat under the table，模型用 6 步生成桌子下面有一只猫，预测出 `<EOS>` 后停止输入。

| 步 | 当前中文前缀 | 预测 Token | 所选 Token 概率 |
| :--- | :--- | :--- | :--- |
| 1 | `<BOS>` | 桌子 | 99.90% |
| 2 | `<BOS>` 桌子 | 下面 | 99.87% |
| 3 | `<BOS>` 桌子 下面 | 有 | 99.96% |
| 4 | `<BOS>` 桌子 下面 有 | 一只 | 99.97% |
| 5 | `<BOS>` 桌子 下面 有 一只 | 猫 | 99.87% |
| 6 | `<BOS>` 桌子 下面 有 一只 猫 | `<EOS>` | 99.94% |

每一步的前缀都比上一步多出一个 Token，说明模型确实在用自己的输出继续生成；第 6 步预测出 `<EOS>` 生成停止。各步概率都接近 100%，这与训练损失降到 0.001 是一致的，模型已经把这 8 条句子记得很牢。
## 总结

| 阶段 | Decoder 输入 | 输出的用途 |
| :--- | :--- | :--- |
| 训练 | 从 BOS 开始的真实中文前缀 | 各位置与错位标签计算损失，更新模型参数。 |
| 生成 | 从 BOS 开始、由模型逐次补充的前缀 | 选取最后一个位置的预测，直到 EOS 或长度上限。 |

词向量与位置编码、三种注意力、FFN、残差连接和归一化，已经组合成一个可以训练与生成的 Mini-Transformer。为了理解简单，本例做了不少简化：

*   数据量很小，只有 8 对短句，模型足以把它们完整记住。
*   每次只训练一个句子，而不是批量训练一个 Batch，也就没有用到 Padding Mask。
*   主要靠 CPU 上的循环运算，而不是 GPU / MPS 的张量批运算。
*   解码阶段每步都重新计算整段前缀，没有做 KV Cache 处理。
