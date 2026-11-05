### 手搓 Mini Transformer 前要知道的编码器工作流程
![](Pasted%20image%2020261101143107.png)
### 整体视角: Encoder 发生了什么
架构图自下向上看，Token 先经 **Embedding** 变成向量、再加上**位置编码**，组成一份序列表示矩阵；随后它依次穿过 Multi-Head Attention、Add & Norm、Feed Forward。在这些模块之间传递的，始终是**由序列中所有 Token 向量组成的这份矩阵**。

> [!note] Self-Attention 的作用
> 让不同 Token **互相读取**，每个位置拿到与上下文相关的新表示。

> [!note] FFN 的作用
> 对每个 Token **各自变换**，把刚获得的信息进一步加工。

> [!important] 核心总结
> 经过多个 Encoder 层，原本主要描述 Token 自身的向量，逐渐转化为**融合上下文信息的表示**。
### Encoder 里流动的数据是什么

> [!example] 输入序列
> `The animal didn't cross the street because it was too tired.`


![](Pasted%20image%2020261102155347.png)

$$
X^{(0)} = \text{Embedding}(X) + \text{PositionalEncoding}
$$

$$
X^{(0)} \in \mathbb{R}^{N \times d_{\text{model}}}
$$

矩阵的**每一行对应一个 Token**，每一列对应向量中的一个特征维度。

> [!info] 初始状态
> 此时每个 Token 只知道**自己是什么、位于第几个位置**，还没有读取任何其他 Token 的信息。

> [!note] 图示数据流说明
> - 每个 Token 经过 `Embedding` 后，与对应的 `Position` 向量相加。
> - 组合得到初始序列表示矩阵 $X^{(0)}$，其形状为 $N \times d_{\text{model}}$。

### Self-Attention：让 Token 之间交换信息

Query、Key 和 Value 都来自**同一份序列表示**，因此称为自注意力。每个 Token 用自己的 Query 与全序列的 Key 匹配，再按权重汇总 Value。

$$
A = \text{MultiHeadAttention}(X^{(0)}) \in \mathbb{R}^{N \times d_{\text{model}}}
$$
![](Pasted%20image%2020261102155734.png)
> [!note] 形状没变，内容变了
> 进去之前，`it` 的向量主要表示它自身和所在位置；出来之后，它可以读取 `animal` 提供的指代信息和 `tired` 提供的语义信息。

> [!important] 核心总结
> Self-Attention 在 Encoder 里承担的，就是让不同 Token **交换信息**。

### Add & Norm：先相加，再归一化

经过 Multi-Head Attention 之后，Encoder 不会直接把结果传入下一个模块，而是先将 Attention 的输出与进入这个子层之前的输入相加，这就是**残差连接（Residual Connection）**。相加之后，结果还会经过**层归一化（Layer Normalization, LayerNorm）**，保持数值稳定。
![](Pasted%20image%2020261102160627.png)
> [!info] ① ADD · 与子层输入相加
> 
> $$
> X^{(0)} + A
> $$

> [!abstract] ② NORM · 对相加结果归一化
> 
> $$
> Z = \text{LayerNorm}(X^{(0)} + A)
> $$

### 残差连接让深层训练更稳定

Attention 让每个 Token 的表示发生变化，而残差连接与 LayerNorm 决定了这些变化能否**稳定地逐层积累**。

> [!info] ① 残差连接的作用
> 子层交出的不是一份新表示，而是**在原表示上要补的修正量**，相加之后进子层之前的信息不会被覆盖。这一层没什么要补时，子层把输出压到接近 0 就行，表示原样通过；反向传播时，梯度也能顺着这个加号**直接跳回上一层**，不必每次穿过 Attention 与 FFN，深层网络因此更容易训练。

> [!abstract] ② 层归一化的作用
> LayerNorm 分别对每个 Token 的向量做归一化，**使不同层之间的数值分布更加稳定**。它处理的是**一个 Token 内部**的特征维度，不会让不同 Token 之间再次交换信息。

> [!important] 架构演进说明
> 原始 Transformer 先相加再归一化，称为 **Post-Norm**；后来的实现更多把 LayerNorm 前置到子层之前，先归一化再送进子层，称为 **Pre-Norm**，这样深层模型更容易训练。

### Feed Forward：两次线性变换加一次非线性

注意力主要解决的是**应该关注哪些位置、从这些位置读取多少信息**，上下文表示还需要进一步加工，才能形成更有表达能力的特征。
![](Pasted%20image%2020261102161306.png)
$$
\text{FFN}(x) = \text{ReLU}(xW_1 + b_1)W_2 + b_2
$$

$$
f_i = \text{FFN}(z_i)
$$

> [!important] 核心处理逻辑
> $z_i$ 是第 $i$ 个位置经过 Self-Attention 之后的向量，**已经融合了其他位置的信息**，序列里的每个位置都**各自走一遍**这套变换。

> [!note] 激活函数演进
> 激活函数在原始论文中使用 ReLU，后来的实现多改用 **GELU** 或 **SwiGLU**。
### 先升维再降回，每个位置互不干扰

> [!info] ① 先升维
> $W_1$、$b_1$ 把向量从 $d_{\text{model}}$ 升到更大的中间维度 $d_{\text{ff}}$，原始论文中是 $512 \rightarrow 2048$。

> [!abstract] ② 再降回
> 经过非线性激活后，$W_2$、$b_2$ 把它映射回 $d_{\text{model}}$，序列表示的**形状不变**。

> [!warning] ③ 参数大头在这里
> 中间维度是输入的 4 倍，单看参数数量，FFN **比同一层的注意力部分更大**。

#### Self-Attention 与 Feed Forward 的对比

| SELF-ATTENTION | FEED FORWARD |
| :--- | :--- |
| 处理**不同 Token 之间**的关系，完成序列维度上的信息交换。 | 不在 Token 之间传递信息，完成**特征维度**上的非线性变换；所有位置共用**同一套参数**，输入不同，结果也不同。 |

> [!important] 核心总结
> 两者组合起来，才构成一次**完整的序列表示更新**。
### 一层 Encoder 的完整计算

FFN 的输出也不会直接覆盖它的输入，而是**再次经过残差连接与 LayerNorm**。一层 Encoder 内的全部计算可以用四行公式表示：

$$
\begin{aligned}
A &= \text{MultiHeadAttention}(X^{(0)}) \\
Z &= \text{LayerNorm}(X^{(0)} + A) \\
F &= \text{FFN}(Z) \\
X^{(1)} &= \text{LayerNorm}(Z + F)
\end{aligned}
$$

$X^{(1)}$ 就是第一个 Encoder 层的最终输出。
![](Pasted%20image%2020261102170456.png)
> [!important] 核心流程总结
> 经过 Self-Attention，每个 Token 融合了其他位置的信息；经过 FFN，这些信息又被进一步转换；两个 Add & Norm 分别**保留了子层的输入**，并让更新过程保持稳定。

### 多层 Encoder 堆叠：同一份表示反复更新

前一层输出的序列表示直接成为后一层的输入。每一层都拥有**自己独立的 Attention 与 FFN 参数**，因此可以基于上一层的结果重新计算 Token 之间的关系。
![](Pasted%20image%2020261102171640.png)
$$
X^{(l)} = \text{EncoderLayer}_l \left( X^{(l-1)} \right)
$$

> [!example] 以 `it` 为例
> 进第一层前，`it` 的向量只有 Embedding 和位置编码；出第一层后，它已经融合了 `animal`、`tired` 等位置的信息。下一层拿到的，已经不是彼此独立的 Token 表示。

> [!info] 核心特征
> 在多层堆叠的过程中，序列表示的**形状始终为 $N \times d_{\text{model}}$**，但其中的内容在不断更新与重组。

### 输出的不是一个向量，而是一整排表示

$$
H \in \mathbb{R}^{N \times d_{\text{model}}}
$$

矩阵的第 $i$ 行 $h_i$ 对应输入序列中的第 $i$ 个位置。这些表示已经**不再只描述单个 Token**，而是融合了整个输入序列的上下文信息。

> [!note] 核心理解
> 整句话并没有被压缩进一个向量，而是保留着**每个 Token 各自的上下文表示**。
> 
> 对于前面那句话，$h_{\text{it}}$ 仍然对应 `it` 这个位置，但它已经包含了与 `animal`、`tired` 相关的信息。

---
![](Pasted%20image%2020261102171842.png)
$H$ 也就是 Decoder 交叉注意力的 **Key 与 Value 来源**：$K = HW_K, \quad V = HW_V$ *注：Query 由 Decoder 产生。*
### 总结：Encoder 在不断更新同一份序列表示

从进入第一层到最终输出，流动的一直是同一份 $N \times d_{\text{model}}$ 的表示矩阵，变的是矩阵里每一行的内容。

| ① 交换 | ② 加工 | ③ 稳定 |
| :--- | :--- | :--- |
| Self-Attention 让不同 Token 之间**交换信息**。 | FFN **分别加工**每个 Token 刚获得的新表示。 | 残差连接和 LayerNorm 让这些变化能**稳定地逐层积累**。 |

> [!important] 核心总结
> Encoder 的核心不是把输入压缩成一个固定长度的向量，而是**不断更新同一份序列表示**。

### Decoder
### 根据 Encoder 的表示 H，Decoder 开始预测

Encoder 把输入序列转换成了 Decoder 可以反复读取的信息 \(H\)。

$$
H \in \mathbb{R}^{S \times d_{\text{model}}}
$$

后面统一用 $S$ 表示 Encoder 输入序列长度（Source Length），$T$表示 Decoder 目标序列长度（Target Length）。

> [!important] 核心区别
> Encoder 一次接收完整的输入序列，而 Decoder 要**从一个起始 Token 开始，不断预测下一个 Token**。

### Decoder 从一个起始 Token 开始
![](Pasted%20image%2020261103083655.png)
> [!info] 第 1 步 · 只有起始标记
> 序列中只有一个位置，表示矩阵是 $1 \times d_{\text{model}}$。

> [!info] 第 2 步 · 追加「那只」
> 序列变成两个位置，矩阵长高一行，成为 $2 \times d_{\text{model}}$。

> [!info] 第 T 步 · 已生成 $T-1$ 个 Token
> 输入由起始标记和前 $T-1$ 个目标 Token 组成，矩阵是 $T \times d_{\text{model}}$。

每生成一个 Token，矩阵就**多出一行**，而列数 $d_{\text{model}}$ 始终不变。Decoder 每次都会处理当前的整个输出序列，但推理时**只用最新一行**预测下一个 Token。

> [!important] 核心机制
> 预测出的 Token 会被**追加回** Decoder 的输入，参与下一个 Token 的预测。

### Masked Self-Attention 理解已经生成的内容

目标序列表示首先进入 Masked Multi-Head Attention。这里的 Query、Key 和 Value **都来自 Decoder 当前已经生成的序列**，因此它本质上仍然是 Self-Attention。
![](Pasted%20image%2020261103085227.png)
> [!info] 为什么叫 MASKED
> 每个位置**只能看自己和它之前的位置**，读不到未来内容。

> [!abstract] 多头注意力
> 512 维拆给 8 个 Head 各看 64 维，拼回后经 $W_O$ 映射。**形状不变**。

### Add & Norm 让深层网络训练更加稳定

Decoder 每个模块后面都跟着 Add & Norm，让模型训练稳定，作用与 Encoder 中完全相同。
![](Pasted%20image%2020261103090809.png)
$$
Y = \text{LayerNorm}(X + \text{Sublayer}(X))
$$

> [!info] ① 残差连接
> 子层输出与**进入子层之前的表示相加**，原有信息不会被覆盖。相加要求两边形状一致，输出仍是 $T \times d_{\text{model}}$。

> [!abstract] ② 层归一化
> LayerNorm 对**每个 Token** 的向量各自归一化，让不同层之间的数值分布更稳定，也不会让 Token 之间再次交换信息。

### Cross-Attention 融合 Encoder 的输入信息

Masked Self-Attention 只能整理**已经生成的目标序列**，但完成翻译还需要参考原始英文句子表达了什么。因此 Decoder 接下来通过 Cross-Attention **读取 Encoder 的最终输出做融合**。
![](Pasted%20image%2020261103091051.png)
$$
Q = Z_T W_Q, \quad K = H W_K, \quad V = H W_V
$$

> [!important] 核心区别
> $Z_T$ 是 Masked Self-Attention 经过 Add & Norm 后的 Decoder 表示。
> **Query 来自 Decoder，Key 和 Value 来自 Encoder**，这正是它与 Self-Attention 的区别，计算逻辑完全一致。

### FFN 先升维再降维，提取融合后的特征

FFN 的作用与 Encoder 中完全一致：把融合后的 Token 内的特征**再提取一遍**。

> [!info] ① 先升维，再降维
> 先从 $d_{\text{model}}$ 升到 $d_{\text{ff}}$，经非线性激活后再降回 $d_{\text{model}}$。

> [!abstract] ② 最终维度不变
> 中间的特征维度变宽了，但输出**与输入维度一致**。

**计算说明**：各位置独立处理，共享同一组参数。

$$
\text{FFN}(x) = W_2 \cdot \text{GELU}(W_1x + b_1) + b_2
$$
### 多个 Decoder 层不断更新目标序列表示

一个 Decoder 层只完成**一轮**生成历史理解、Encoder 信息融合和特征加工。完整的 Transformer Decoder 通常会堆叠多个结构相同的 Decoder 层。
![](Pasted%20image%2020261103091739.png)
$$
Y_T^{(l)} = \text{DecoderLayer}_l \left( Y_T^{(l-1)}, H \right)
$$

> [!info] 核心机制
> 每层都有**自己独立的 Attention 与 FFN 参数**，因此可以基于上一层的结果重新整理目标序列，并重新读取输入序列中的信息。

> [!important] 最终输出状态
> 最终得到的 $Y_T^{(L)}$ 已经融合了生成历史和 Encoder 输入信息，但它们仍然只是 $d_{\text{model}}$ 维向量，**还不能直接表示下一个 Token 是什么**。

### Linear 将 Decoder 表示映射到词表空间

每个位置仍然是一个 $d_{\text{model}}$ 维向量，而向量的**每一维并不直接对应某个 Token**。为了预测下一个 Token，Linear 把它映射到**词表空间**：每一行都变成对词表全部 Token 的一组打分。
![](Pasted%20image%2020261103091958.png)

映射矩阵 $W_{\text{vocab}} \in \mathbb{R}^{d_{\text{model}} \times |\mathcal{V}|}$ 把**模型内部的特征维度换成了词表维度**。

### Softmax 得到下一个 Token 的概率

Linear 只给出了词表中每个 Token 的预测分数。接下来，Softmax 把**最新位置**的 Logits 转换成概率分布：

$$
p_i = \frac{\exp(l_i)}{\sum_{j=1}^{|\mathcal{V}|} \exp(l_j)}
$$

分母把所有 Token 的分数加在一起做归一化，因此每个概率都位于 0 到 1 之间，并且**总和为 1**。向量长度不变，变的只是数值的意义：从一组打分变成一份概率分布。

> [!important] 核心结论
> **Softmax 只负责生成概率分布，不会直接决定最终选择哪个 Token**——那是解码策略的工作。
### 解码策略：从概率分布中选出 Token

拿到概率分布之后，**并不是简单地取概率最大的那个 Token**。
![](Pasted%20image%2020261103092511.png)
> [!info] TEMPERATURE
> 在 Softmax 之前缩放 Logits，可以调整概率分布：
> - **调高**后分布更平缓，低概率 Token 也有机会被选中，生成更发散；
> - **调低**后分布更尖锐，生成更保守。

> [!abstract] GREEDY SEARCH (贪心搜索)
> 从分布中选 Token 的做法有多种，最常用的是每一步都取**概率最大**的那个。

---

> [!important] 核心逻辑与演进
> 但每步最优不等于整句最优，直接采样又可能选到概率很低的异常 Token，于是有了 **Top-K 与 Top-P**。
> 
> *注：结合左侧图示补充，Top-K 是固定候选数量（如 K=3），Top-P 是动态累积概率阈值（如 P=0.85），两者都会重新归一化后再进行采样。*

### Top-K 与 Top-P：把候选范围收紧

> [!info] TOP-K SAMPLING
> 只保留概率最高的 \(K\) 个 Token。候选数量固定，**不随分布变化**：分布很集中时可能放进来不该选的 Token。

> [!abstract] TOP-P SAMPLING (NUCLEUS)
> 只保留累计概率达到 \(P\) 的最小集合。候选数量**随分布动态伸缩**：模型很确定时候选更少，犹豫时候选更多。

三者可以组合使用：先用 Temperature 调整 Logits，再用 Top-K 或 Top-P 缩小候选范围，最后从剩余 Token 中采样。它们都**不会改变 Decoder 内部的表示矩阵**，只作用于最新位置产生的词表预测结果。

> [!important] 结束条件
> 当模型生成 `<EOS>` 时，表示目标序列已经结束，Decoder **停止继续生成**。

### 训练时不需要真的一个 Token 一个 Token 计算

推理时下一个 Token 尚未产生，不同步骤必须依次进行。但训练时**正确的目标序列已经存在**，把它右移一位当作输入，$T$ 个位置就能**通过一次矩阵运算全部算完**。
![](Pasted%20image%2020261103094947.png)
### 训练 VS 推理

|         | 训练 (Teacher Forcing)                     | 推理 (自回归 + KV Cache)                   |
| :------ | :--------------------------------------- | :------------------------------------ |
| **输入**  | 整句 $x_1 \dots x_T$ **全部已知**              | 第 $i$ 步只有 $x_1 \dots x_i$             |
| **QKV** | 一次算出**全部 $T$ 组 $Q, K, V$**               | 每步只算**最新一个 $q_i$**，K/V 从缓存取           |
| **分数**  | $T \times T$ 大矩阵 $QK^T$，再加 Causal Mask   | $1 \times i$ 的向量与矩阵相乘 $q_i K_{1:i}^T$ |
| **输出**  | 一次得到 $o_1 \dots o_T$                     | 每步只得到 $o_i$                           |
| **预测**  | $o_i \rightarrow x_{i+1}$，$T$ 个预测**同时做** | 第 $i$ 步由 $o_i$ 采样出 $x_{i+1}$          |
| **步数**  | 1 次前向                                    | $T$ 次前向                               |
### 批量处理多个样本

前面为了方便理解都省略了批次维度，实际实现时模型通常会同时处理 $B$ 个样本，因此所有矩阵都要在**最前面增加一个批次维度 $B$**。

![](Pasted%20image%2020261103095826.png)
> [!info] PADDING MASK
> 同一批样本长度不同，短的要用 PAD 补齐。Padding Mask 用 1 标记有效 Token、0 标记 PAD，让注意力**跳过这些补齐位置**。

> [!note] 补充说明
> $B$ 只表示**同时处理的样本数量**，不同样本之间不会互相读取。
> *（注：处理时补齐到相同长度 $S$，1 代表有效 Token，0 代表忽略 `<PAD>`，同一份有效位置标记，同时计算，样本之间互不读取。）*

### 总结：Decoder 预测下一个 Token

| 步骤             | 核心操作                  | 具体说明                                        |
| :------------- | :-------------------- | :------------------------------------------ |
| **① 理解已生成内容**  | Masked Self-Attention | 只让每个位置读自己和之前的 Token。                        |
| **② 融合输入信息**   | Cross-Attention       | 用 Decoder 的 Query 查询 Encoder 输出。            |
| **③ 变换位置表示**   | FFN                   | 逐位置先升维再降维，把特征再提取一遍。                         |
| **④ 重复多个层**    | 逐层更新                  | 表示逐层更新，形状始终保持在 $T \times d_{\text{model}}$。 |
| **⑤ 选出 Token** | Linear & Softmax      | Linear 得到 Logits，Softmax 转成概率，解码策略选出 Token。 |

其中 Embedding、位置编码、Add & Norm 和 FFN 的作用，与 Encoder 中**完全一样**。

> [!important] 核心结论
> 训练时目标序列已知，右移一位后**一次前向算完**；推理时逐个生成，K/V 走缓存，需要 **$T$ 次前向**。


