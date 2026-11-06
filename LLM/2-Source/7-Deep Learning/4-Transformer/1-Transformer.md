# Transformer

### 要解决的仍是序列到序列
2017 年，Google 在论文《Attention Is All You Need》中提出了 Transformer，最初要解决的仍然是自然语言处理中的一个经典问题：**如何把一个序列转换成另一个序列。**
```text
I love deep learning -> 我 喜欢 深度 学习
```
#### Transformer 带来的两大优势

| 摆脱 RNN 时序依赖                                             | 提升并行计算能力                                   |
| ------------------------------------------------------- | ------------------------------------------ |
| 通过一次 **Self-Attention**，序列所有 Token 直接建立联系，模型更容易建模长距离依赖。 | 序列训练的**并行计算能力**显著提升，模型更容易利用大规模数据和计算资源不断扩展。 |

> [!important] 深远影响  
> 此后 Transformer 逐渐成为自然语言处理的基础架构，**BERT、GPT、T5** 都建立在它之上，并进一步影响了计算机视觉、语音和多模态等领域。

### 完整的Transformer
[Attention Is All you Need](Attention%20Is%20All%20you%20Need.pdf)
![](../../../../image/Pasted%20image%2020261101143107.png)
Transformer 的原始架构由左侧的 **Encoder** 和右侧的 **Decoder** 组成，两者内部又堆叠了注意力、残差连接、归一化和前馈神经网络等模块。

所有结构同时出现在一张图中，很容易让人陷入局部细节，看不清整体的数据流向。

> [!tip] 学习路径
> 接下来先暂时忽略内部细节，从 Encoder-Decoder 框架出发，沿着数据流**逐步点亮各个模块**，观察 Transformer 如何读取输入、理解源序列并生成输出。

### 整体架构: Encoder-Decoder

Transformer 与 Seq2Seq 一样，仍然采用 Encoder-Decoder 架构。

1. **① 转换输入 · Embedding**
   源序列的 Token 经过 Input Embedding，转换成向量表示。
2. **② 理解源序列 · Encoder**
   为每个输入 Token 生成包含上下文信息的表示。
3. **③ 生成目标表示 · Decoder**
   读取 Encoder 输出，结合已生成的目标前缀，产生当前位置的隐藏表示。
4. **④ 映射到词表 · Linear**
   把隐藏表示映射到词表空间，为每个候选 Token 打分。
5. **⑤ 转换为概率 · Softmax**
   把分数转换成总和为 1 的概率分布。
6. **⑥ 预测下一个 Token · 自回归**
   选出的 Token 加入目标前缀，经 Output Embedding 再次输入 Decoder，重复直到生成 `<EOS>`。

> [!important] 核心结论
> 整体流程与 Seq2Seq 没有本质区别，真正发生变化的是 **Encoder** 和 **Decoder 内部生成上下文表示的方式**。

### Positional Encoding: 为 Token 加入位置信息
![](../../../../image/Pasted%20image%2020261101144029.png)
Token 先经过 Embedding 变成向量，这一步我们已经很熟悉。但 Transformer 不再像 RNN 那样沿序列逐步计算，Self-Attention 会**同时处理所有位置**——顺序计算的依赖消失了，模型也就无法再从计算顺序中知道谁先谁后。
```text
dog bites man

man bites dog
```
两句用的是同一组单词，只有顺序不同，单靠 Embedding 无法区分。因此 Transformer 单独对位置做编码，并**直接加到对应 Token 的 Embedding 上**，让进入第一层 Encoder 和 Decoder 的向量同时携带内容与位置。
$$X_i=Embedding(x_i)+PositionalEncoding(i)$$
### Self-Attention: 让输入位置直接交换信息
![](../../../../image/Pasted%20image%2020261101144155.png)
完成输入表示后，源序列首先进入 Encoder 的**自注意力（Self-Attention）**。

> [!info] RNN 的信息传递方式
> 句尾的词想拿到句首的信息，必须经过中间一连串隐藏状态**逐步传递**——序列越长路径越长，同一层的不同位置也无法同时计算。

Self-Attention 让每个 Token 用自己的 **Query** 去匹配全序列的 **Key**，再按得到的注意力权重汇总对应的 **Value**。于是每个位置都能**一步直接读取其他位置的信息**，生成融合上下文的新表示。
$$
\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V
$$

### 每个 Token 都以自己为 Query 查询全序列
`I love deep learning`，四个 Token 分别作为 Query，对全序列的 Key / Value 算出一组注意力权重：
![](../../../../image/Pasted%20image%2020261101144403.png)
同一层中，各个位置的计算不需要等待前一个位置的结果。只要整段输入已经存在，所有 Token 的注意力计算就可以组织成**矩阵并行完成**——这正是 Transformer 比 RNN 更适合并行训练的重要原因。
### Multi-Head Attention：从多个表示空间提取信息
Transformer 还使用了多头注意力（Multi-Head Attention）：用**多组不同的参数**对同一段输入进行映射，让多个 Attention Head 分别从不同的表示空间提取信息，最后再将各个 Head 的结果**拼接并融合**。

| CNN · 多个卷积核 | TRANSFORMER · 多个 HEAD |
| :--- | :--- |
| 同一卷积层内的多个卷积核关注**不同的局部模式**，分头提取特征后再汇总。 | 多个 Attention Head 则可以学习**不同位置之间的关系**，分头建立联系后再融合。 |
> [!important] 核心结论
> 多头注意力并不是一个新机制，而是 Self-Attention 的实现强化——从**多个角度**重复同一件事。
> Self-Attention + MHA 解决了RNN不能并行的问题

### Add & Norm: 让信息稳定地穿过深层网络

![](../../../../image/Pasted%20image%2020261101144943.png)
架构图中的 `Nx` 代表可以堆叠多层。Self-Attention 完成了不同 Token 之间的信息交换，但随着网络不断堆叠，原有信息可能在连续变换中逐渐丢失，各层输出的数值分布也可能发生较大变化。因此 Transformer 会在**每个子层之后**加入 Add & Norm。

> [!info] Add · 残差连接
> 把原始输入 $x$ 直接加回子层输出 $F(x)$。
> 
> 子层只需学习在原始表示上改什么，梯度也获得一条绕过子层的通路。

> [!info] Norm · 层归一化
> 对**每个 Token 隐藏表示内部**的各个维度做归一化。
> 
> 把数值拉回相对稳定的范围，减少层堆叠时数值分布的剧烈变化。

$$
y = \text{LayerNorm}(x + F(x))
$$

### 为什么是 LayerNorm，而不是 BatchNorm

关键在于：**哪些数据之间具有可比较的共性**。

> [!info] BATCHNORM 适用的场景
> 以房价预测为例，同一批次中的每个样本都拥有**对应特征**：
> 
> ```text
> 样本 1: 卧室数量   房屋面积   地铁距离
> 样本 2: 卧室数量   房屋面积   地铁距离
> ```
> 
> 可以分别统计**同一个特征**在一批样本中的数值分布，再对其归一化。

> [!warning] NLP 序列不具备这种关系
> 不同句子中**相同位置**的 Token 往往没有直接关系：
> 
> ```text
> 样本 1: There is a cat
> 样本 2: He came to the store
> ```
> 
> 而且不同序列的**长度也不相同**，没有稳定的对应位置可以统计。

> [!important] 核心结论
> Transformer 因此不在不同样本之间寻找对应位置，而是**分别处理每个 Token**：对它的多维向量内部做归一化，完全不依赖同一批次中的其他句子。

### FFN: 进一步加工每个位置的信息
![](../../../../image/Pasted%20image%2020261101145944.png)
Self-Attention 已经让每个 Token 从其他位置汇总了与自己相关的信息，但它解决的只是“**关注哪些位置、读多少信息**”。这些上下文表示还需要再加工一次，才能成为更有表达能力的特征。FFN 就是紧跟在它后面的两个线性层，中间夹一个 ReLU：

$$
\text{FFN}(x) = \text{ReLU}(xW_1 + b_1)W_2 + b_2
$$

| 步骤 | 核心操作 | 作用说明 |
| :--- | :--- | :--- |
| **STEP 1 · 升维** | 第一个线性层 | 映射到更高维度，提供更宽的特征空间 |
| **STEP 2 · 非线性** | ReLU 激活函数 | 引入非线性，能学习更复杂的特征转换 |
| **STEP 3 · 降维** | 第二个线性层 | 映射回原维度，便于与### 先升维、再降维
在 Transformer 论文中，FFN 会将每个 Token 的表示从 `512` 扩展到 `2048` 维，再压缩回 `512` 维：
```text
512 ➡️ 2048 ➡️ 512
```
> [!info] 分工明确  
> **Self-Attention** 负责在不同 Token 之间交换信息，  
> **FFN** 负责进一步加工每个 Token 已经获得的信息。

> [!info] Decoder 中同样包含 FFN  
> 作用没有变化：在掩码自注意力和交叉注意力完成信息交换后，继续加工每个**目标位置**融合得到的上下文表示。

> [!important] 核心流程与作用  
> FFN 处理完成后，数据会再次经过 Add & Norm，然后继续进入下一层 Encoder。
> 
> 经过多层 Encoder 的信息交换和加工，模型最终为源序列的每个 Token 生成一个上下文表示——这些表示经线性映射后，将作为 Decoder **Cross-Attention 使用的 Key 和 Value**。残差相加后传给下一层 |


### Masked Self-Attention: 训练时也不能看见未来
![](../../../../image/Pasted%20image%2020261101150446.png)
现在把视线移到 Decoder。Decoder 的输入是目标序列中已经出现的内容，也可以称为**目标前缀**。比如准备生成“深度”时，Decoder 已经拥有的内容可能是：
```text
<BOS> 我 喜欢
```
这些 Token 同样会先经过 Embedding 和位置编码，再进入掩码自注意力。它与 Encoder 中的 Self-Attention **基本形式相同**，区别在于增加了因果掩码：每个位置只能关注自己以及它前面的位置。

> [!important] 核心理解  
> 推理阶段未来的 Token 尚不存在，本来就无从读取。**掩码真正需要解决的是训练阶段的问题。**
### Teacher Forcing 带来的隐患
训练时，为了并行计算所有位置，模型不会像推理时一样逐个生成 Token，而是通过 **Teacher Forcing** 一次性把右移后的完整目标序列交给 Decoder：
```text
Decoder 输入:  <BOS>   我    喜欢   深度
预测目标:              我    喜欢   深度   学习   <EOS>
```
> [!success] 带来的好处  
> Decoder 可以**同时**学习从 `<BOS>` 预测“我”、从“我”预测“喜欢”、从“喜欢”预测“深度”，以及从“深度”预测“学习”。

> [!warning] 随之而来的问题  
> 完整的目标序列已经放进 Decoder，如果不加限制，用于预测“喜欢”的位置就可能直接读取后面的“喜欢”，相当于**提前看到了正确答案**。

> [!important] 核心解决方案  
> 模型可能由此找到一条训练时有效、推理时却无法使用的捷径。因此掩码自注意力会在 Self-Attention 基础上增加**因果掩码（Causal Mask）**。
### 因果掩码：只能连到自己和前面的位置
![](../../../../image/Pasted%20image%2020261101150739.png)

| 当前生成 (Query) | 可连线的位置 (Key/Value) | 被掩码的位置 (不能看) | 限制说明 |
| :--- | :--- | :--- | :--- |
| **① 生成第 1 个词：`I`** | ① `I` | ② `love`, ③ `deep`, ④ `learning` | 只能连到 **1** 个词 |
| **② 生成第 2 个词：`love`** | ① `I`, ② `love` | ③ `deep`, ④ `learning` | 只能连到 **2** 个词 |
| **③ 生成第 3 个词：`deep`** | ① `I`, ② `love`, ③ `deep` | ④ `learning` | 只能连到 **3** 个词 |
| **④ 生成第 4 个词：`learning`**| ① `I`, ② `love`, ③ `deep`, ④ `learning` | 无 | 能连到 **全部 4** 个词 |

> [!important] 核心意义
> 即使训练时一次输入完整的目标序列，每个位置也只能根据当时已经拥有的目标前缀预测下一个 Token。
> 
> Transformer 因而能够在**遵守自回归生成规则**的同时，并行完成目标序列中所有位置的训练。

### Cross-Attention：让 Decoder 查询 Encoder
![](../../../../image/Pasted%20image%2020261101150937.png)
掩码自注意力整理了已经生成的目标内容，但只看目标前缀还不足以完成翻译——Decoder 还需要知道**源序列表达了什么**。这一步与 Seq2Seq Attention 的思想如出一辙：**Decoder 先描述当前需要什么信息，再与 Encoder 保存的源序列信息匹配，最后取出相关内容。**

> [!abstract] Q、K、V 的来源
> - **Q**：来自 **Decoder** 掩码自注意力产生的目标序列上下文表示
> - **K**：来自 **Encoder** 输出的源序列上下文表示
> - **V**：同样来自 **Encoder** 输出的源序列上下文表示

$$
Q = SW_Q, \quad K = HW_K, \quad V = HW_V
$$

> [!important] 核心理解
> $S$ 表示 Decoder 根据目标前缀生成的上下文表示，$H$ 表示 Encoder 输出的源序列上下文表示，$W_Q$、$W_K$、$W_V$ 是三个不同的线性映射。
> **真正决定这一步性质的，是 Q 与 K、V 分别来自哪一侧。**

### 三种注意力：差别只在信息来源

> [!note] Encoder Self-Attention
> **Q、K、V 全部来自源序列**
> 
> 掩码：无

> [!warning] Masked Self-Attention
> **Q、K、V 全部来自目标前缀**
> 
> 掩码：因果掩码

> [!info] Cross-Attention
> **Q 来自 Decoder，K 和 V 来自 Encoder**
> 
> 掩码：无

> [!important] 核心结论
> 三种注意力的**核心计算形式相近**，真正不同的是信息来源，以及是否需要限制未来位置。

### Linear 和 Softmax：把隐藏表示变成 Token 概率
经过多层 Decoder 后，每个目标位置都会得到一个隐藏表示。但这个向量仍然位于模型内部的隐藏空间，**不能直接对应词表中的具体 Token**。
> [!note] Linear · 映射到词表空间
> 假设词表中有 $V$ 个 Token，Linear 就为每个位置输出 $V$ 个分数（logits），每个分数对应一个**候选 Token**。
> [!abstract] Softmax · 转成概率分布
> 将这些分数转换成**总和为 1** 的概率分布，表示下一个位置生成各个 Token 的概率。
```text
Decoder 隐藏表示 -> Linear -> 词表分数 -> Softmax -> Token 概率
```

> [!important] 推理机制：自回归生成  
> 推理时，模型根据这个概率分布选择下一个 Token，将它加入目标前缀，再次送入 Decoder——这个不断把已生成结果作为下一步输入的过程，就是**自回归生成**。
### 并行的是训练，不是生成

> [!success] ⚡ 训练阶段：可并行
> **已知的目标序列（输入给 Decoder）**：
> `<BOS>` `我` `喜欢` `深度` `学习`
> 
> ⬇️ 一次性输入给 **Decoder**
> 
> **并行输出**：
> `我` `喜欢` `深度` `学习` `<EOS>`
> 
> **说明**：目标序列已知，**可同时计算每个位置的输出与损失**。

> [!warning] 🔄 推理阶段：仍然串行
> 必须**先得到前一个 Token**，才能**继续生成下一个 Token**。
> 
> | 步骤 | 已知序列 (输入给 Decoder) | 模型操作 | 预测下一个 Token |
> | :---: | :--- | :---: | :--- |
> | **1** | `<BOS>` `我` | ➡️ Decoder | **喜欢** |
> | **2** | `<BOS>` `我` `喜欢` | ➡️ Decoder | **深度** |
> | **3** | `<BOS>` `我` `喜欢` `深度` | ➡️ Decoder | **学习** |
> | **4** | `<BOS>` `我` `喜欢` `深度` `学习` | ➡️ Decoder | `<EOS>` |

> [!important] 🎯 核心结论
> **Transformer 消除的是已知序列内部的循环依赖，而不是自回归生成的先后顺序。**

### Transformer 的变与不变

| 延续下来的部分 | 真正改变的部分 |
| :--- | :--- |
| Seq2Seq 的 Encoder-Decoder 数据流，以及 Attention 中**根据当前需求查询已有信息**的思想。 | **上下文表示的生成方式**：Self-Attention 让每个位置直接与整个序列建立联系，同一层中的多个位置可以组织成矩阵同时计算。 |

> [!success] 01
> 不同位置之间的**信息传递路径显著缩短**，模型处理长距离依赖的能力变强。

> [!success] 02
> 不再受 RNN **时序递推关系**的限制，更适合 GPU 等并行计算设备。

> [!important] 核心总结
> 理解 Transformer 的关键，就是理解序列中的信息如何通过 **Self-Attention 直接流动**。

## Transformer 注意力究竟在做什么
### Transformer 中的注意力机制

- **三类注意力**：
    
    - 编码器中的**自注意力**（Self-Attention）
    - 解码器中的**掩码自注意力**（Masked Self-Attention）
    - **交叉注意力**（Cross-Attention）

## 核心思考与待解决问题

1. 为什么同一个模型要连续使用这么多次 Attention？
2. 这些矩阵来回变换究竟在处理什么？
3. 为什么大模型推理时有 KV Cache，而没有 Q Cache？
## Attention 是什么
![](../../../../image/Pasted%20image%2020261102090629.png)
Attention 是一种计算序列中不同位置 Token 之间的**匹配关系**，再按照匹配程度**读取并汇总信息**，为每个 Token 生成新的上下文表示的方法。
## 案例说明

**示例句子：**

> The animal didn't cross the street because it was too tired.

**原理解释：**  
这句话里，代词 `it` 在更新自身表示时，与 `animal` 的连线明显更粗——这正是不同位置之间匹配程度的可视化。
## Attention 带来的变化

Attention 机制的核心作用在于**改变 Token 向量的信息构成**：
- **Attention 之前**：每个 Token 的向量主要表示**自身的语义和位置**。
- **Attention 之后**：每个 Token 的新向量已经**融合了序列中其他相关位置的信息**。
![](../../../../image/Pasted%20image%2020261102091014.png)
## 从 Seq2Seq 的任务重新理解 Attention

Seq2Seq 和 Transformer 都在完成**把输入序列 A 转换成输出序列 B** 的任务，计算的步骤也很相似：
## 计算步骤

1. **理解输入序列 A**；
2. **理解输出序列 B 中已经生成的内容**；
3. **使用最新 Token 的上下文表示，从输入序列 A 中查找、读取需要的信息**；
4. **综合信息，预测下一个 Token**。
![](../../../../image/Pasted%20image%2020261102091223.png)
## 核心结论

Seq2Seq Attention 和 Transformer 的主流程类似，**不同的是使用生成序列上下文表示的方法**。
## Seq2Seq Attention 在做什么
![](../../../../image/Pasted%20image%2020261102091852.png)
## 核心步骤

1. **理解输入序列**  
    Encoder 用 RNN 顺序读取，留下每个位置的隐藏状态 H=$[h1,...,hn]$。
2. **形成信息需求**  
    Decoder 状态 $s_t​$ 投影为 **Query**，Encoder 输出 H 投影为 **Key**、**Value**。
3. **读取并汇总**  
    按匹配程度对 Value 加权求和得 $c_t$​，结合 $s_t$​ 预测下一个 Token。
## 计算公式

$$Q=s_tW_Q,K=HW_K,V=HW_V$$
$$c_t=Attention(Q,K,V)$$
## 核心结论

Seq2Seq Attention 的作用可以概括为：根据 Decoder **当前的生成状态**，动态地从 Encoder 的**全部输出**中读取本次预测需要的信息。
### Transformer 改变了理解序列的方式

Transformer 完成的是相同的任务，只是不再使用 RNN 逐步生成隐藏状态，而是把**理解序列这件事本身**也交给了 Attention。整体流程可以概括为：

> [!note] 01
> Encoder 使用**自注意力**处理输入序列，生成输入序列的上下文表示。

> [!note] 02
> Decoder 使用**掩码自注意力**处理已经生成的输出序列。

> [!note] 03
> Decoder 使用**交叉注意力**，根据当前生成状态读取输入序列的信息。

> [!note] 04
> 经过 FFN、线性映射和 Softmax，预测下一个 Token。

> [!important] 核心总结
> 三类注意力内部使用的是**同一种计算机制**，主要区别在于 Query、Key 和 Value 来自哪里。

### 三类注意力：区别只在信息来源

| 注意力类型      | Q 来源    | K、V 来源  | 主要作用           |
| :--------- | :------ | :------ | :------------- |
| **自注意力**   | 输入序列    | 输入序列    | 生成输入序列的上下文表示   |
| **掩码自注意力** | 输出序列    | 输出序列    | 生成当前输出前缀的上下文表示 |
| **交叉注意力**  | Decoder | Encoder | 根据当前生成状态读取输入序列 |

### 输入序列预处理

进入 Encoder 之前输入序列会先经过 **Embedding** 和 **Positional Encoding** 处理，转换成一个序列表示矩阵。
![](../../../../image/Pasted%20image%2020261102093442.png)
**输入序列**：
`I love deep learning` （序列长度 = 4）

假设模型使用 512 维向量表示每个 Token，那么这个序列会形成一个 **4 × 512** 的矩阵，矩阵中的**每一行对应一个 Token**，包含这个 Token 的语义和位置信息：

$$
X = [x_I, x_{\text{love}}, x_{\text{deep}}, x_{\text{learning}}]
$$
### 一个 Token 的含义取决于它与其他 Token 的关系

此时，每一行主要描述的仍然是对应 Token 自身。例如，$x_{learning}$ 包含 learning 的语义和位置，却还没有直接融合 I、love 和 deep 的信息。

> [!note] DEEP 修饰了 LEARNING
> learning 前面的 deep 修饰了它，两者共同构成了 deep learning。

> [!note] LOVE 描述了关系
> love 则描述了 I 与 deep learning 之间的关系。

> [!important] 核心结论
> Self-Attention 要做的事情，就是让每个位置观察整个序列，根据它与其他位置的关系，重新生成一个包含上下文信息的向量。

### Q、K、V 是输入矩阵的三种投影

为了计算不同位置之间的关系，模型会学习三组参数矩阵 $W_Q$、$W_K$、$W_V$，输入矩阵 $X$ 分别与它们相乘：

$$
Q = XW_Q, \quad K = XW_K, \quad V = XW_V
$$
![](../../../../image/Pasted%20image%2020261102093923.png)

> [!abstract] Q：Query
> 描述当前位置在更新自身表示时，希望**寻找什么信息**。

> [!abstract] K：Key
> 描述当前位置提供了哪些可以**参与匹配的特征**。

> [!abstract] V：Value
> 描述匹配成功后，当前位置真正**提供给其他位置的内容**。

> [!info] 补充说明（来自左下角）
> - 矩阵乘法一次完成所有 Token 的线性投影。
> - Q、K、V 中每一行仍对应序列中的一个 Token。

### 一个Token 如何读取整个序列
![](../../../../image/Pasted%20image%2020261102094421.png)
### ① Query 与所有 Key 计算匹配分数

取出 `learning` 对应的 Query 向量 $q_{\text{learning}}$，分别与序列中所有 Token 的 Key 做点积：

$$
q_{\text{learning}}k_I^T, \quad q_{\text{learning}}k_{\text{love}}^T, \quad q_{\text{learning}}k_{\text{deep}}^T, \quad q_{\text{learning}}k_{\text{learning}}^T
$$

这些点积结果表示 `learning` 的 Query 与各个位置的 Key 有多匹配。这里得到的只是**匹配分数**，还不是最终的信息读取比例。
### ② 缩放：除以 $\sqrt{d_k}$

随着向量维度增加，点积结果的数值通常也会增大。如果直接输入 Softmax 计算，可能使输出分布**过于集中**，导致梯度变小，影响训练稳定性。

$$
\frac{q_{\text{learning}} K^T}{\sqrt{d_k}}
$$

因此，Transformer 会把点积结果除以 $\sqrt{d_k}$ 进行缩放，$d_k$ 表示当前注意力头中 Query 和 Key 的**向量维度**。
### ③ 使用 Softmax 得到注意力权重

缩放后的匹配分数经过 Softmax，被转换成一组**总和为 1** 的注意力权重：

$$
\alpha_{\text{learning}} = \text{softmax} \left( \frac{q_{\text{learning}}K^T}{\sqrt{d_k}} \right)
$$

这些权重表示：为了更新 `learning` 的表示，当前注意力头应该从各个位置**读取多少信息**。例如，模型可能为 `deep` 分配较高权重，因为它与 `learning` 共同构成了 `deep learning`。
### ④ 按照权重汇总 Value

得到注意力权重之后，模型会按照相应比例，对所有位置的 Value 进行加权求和：

$$
o_{\text{learning}} = \sum_{j=1}^N \alpha_{\text{learning},j} v_j
$$

最终得到的 $o_{\text{learning}}$，就是 `learning` 在这个注意力头中生成的**新表示**。它不再只包含自身的信息，还融合了 `I`、`love`、`deep` 和自身 Value 中与当前 Query 相关的内容。
### 使用矩阵从一个 Token 扩展到整个序列

序列中的每个 Token 都需要经历相同的过程，使用矩阵乘法可以一次完成整个序列的计算。

> [!note] ① 计算注意力权重矩阵
> 
> $$
> A = \text{softmax} \left( \frac{QK^T}{\sqrt{d_k}} \right), \quad A \in \mathbb{R}^{N \times N}
> $$
> 
> $A$ 的第 $i$ 行、第 $j$ 列，表示第 $i$ 个位置在更新自身表示时，对第 $j$ 个位置分配的**注意力权重**。

> [!abstract] ② 用 $A$ 加权汇总 VALUE
> 
> $$
> O = AV
> $$
> 
> 输出矩阵 $O$ 中的每一行，都是一个 Token **融合上下文信息之后的新表示**。

> [!important] 两步合并 · 缩放点积注意力
> $$
> \text{Attention}(Q, K, V) = \text{softmax} \left( \frac{QK^T}{\sqrt{d_k}} \right)V
> $$

### 掩码自注意力：先看它要解决的问题

Decoder 中的掩码自注意力与 Encoder 自注意力使用**相同的计算过程**，它的作用是生成目标序列的上下文表示。

> [!info] 推理时
> Token 是**一个一个生成**的，第 $t$ 个位置天然只能看到已经生成的内容。

> [!warning] 训练时
> Decoder 一次就接收到**完整的目标序列**。不做任何限制的话，前面的位置就可能直接读取后面的**正确答案**。

> [!important] 核心结论
> 掩码是为了防止训练时出现**目标信息泄露**，使模型训练时每个位置的可见范围与推理时自回归生成时**保持一致**。

### 因果掩码：遮挡未来位置
![](../../../../image/Pasted%20image%2020261102095710.png)
模型使用**因果掩码**遮挡未来位置，使第 $t$ 个位置只能关注自己以及它之前的 Token，不能读取后面的内容。

> [!info] 怎么遮
> 在匹配分数上加一个**掩码矩阵 $M$**：允许关注的位置取 `0`，需要遮挡的位置取**负无穷**。

> [!success] 为何有效
> 经过 Softmax 后，被遮挡位置的注意力权重会变成 `0`，相当于这些位置在本次计算中**不存在**。

左图中的每一行对应一个生成步骤，每个位置的可见范围只包含**自己和之前的 Token**，形成一个下三角形的关注区域。
> *注：图中绿色代表“可见（可以关注）”，红色代表“不可见（被掩码）”。*

> [!important] 因果掩码的作用
> 防止训练时看到未来的正确答案，保证训练与推理（自回归生成）时的可见范围一致。

$$
\text{Attention}(Q, K, V) = \text{softmax} \left( \frac{QK^T + M}{\sqrt{d_k}} \right) V
$$
### 再看一眼架构图：交叉注意力在哪里
![](../../../../image/Pasted%20image%2020261101143107.png)
> [!note] 刚讲完 · 掩码自注意力
> 发生在 Decoder **内部**：Q、K、V 都来自目标序列，每个位置只能看到当前前缀。

> [!info] 下一处 · 交叉注意力
> 位于掩码自注意力**之后**，是架构图中唯一**横跨 Encoder 与 Decoder** 的注意力模块。

> [!important] 核心提示
> 注意架构图中从 Encoder 顶部指向 Decoder 的那两条箭头：它们送进来的正是交叉注意力要用的 **K 和 V**。

### 交叉注意力：根据当前状态读取输入序列

经过掩码自注意力之后，Decoder 已经形成了当前输出序列的上下文表示，但它还需要回到输入序列中，读取预测下一个 Token 所需的信息——之所以称为交叉注意力，是因为 **Query 与 Key、Value 来自两个不同的序列**。
![](../../../../image/Pasted%20image%2020261102100242.png)
> [!abstract] 来源区分
> - **Query** 来自 Decoder 的当前序列表示；
> - **Key 和 Value** 来自 Encoder 的最终输出。

$$
Q = ZW_Q \quad K = HW_K \quad V = HW_V
$$

> [!important] 核心结论
> Decoder 根据当前已经生成的内容形成 **Query**，再用它查询 Encoder 对输入序列的表示，得到预测下一个 Token 所需的**源序列信息**。

### 一个序列是如何被生成的
![](../../../../image/Pasted%20image%2020261102100514.png)
### 生成一个 Token 的五个步骤

输入序列先经过 Encoder，生成上下文表示 $H$。在整个解码过程中输入序列不会改变，因此 Encoder 通常**只需要执行一次**。Decoder 从 `<BOS>` 开始：

> [!abstract] 生成步骤
> 1. 掩码自注意力生成当前输出前缀的上下文表示；
> 2. 交叉注意力根据当前状态读取 Encoder 的输出；
> 3. 当前表示继续经过残差连接、归一化和 FFN；
> 4. 最后一层 Decoder 的输出经线性映射，得到词表中每个 Token 的分数；
> 5. 通过 Softmax 转换成概率分布，预测出“我”。

随后把“我”加入 Decoder 的输入，Decoder 使用**最新位置**的表示查询**相同的 Encoder 输出**，预测出“喜欢”。这个过程不断重复，直到模型生成 `<EOS>`，或者达到设定的最大长度：

```text
<BOS>
<BOS> 我
<BOS> 我 喜欢
<BOS> 我 喜欢 深度
<BOS> 我 喜欢 深度 学习
```
### KV Cache 是什么

把历史 Token 在每一层注意力中已经生成的 Key 和 Value 保存下来，生成下一个 Token 时直接复用，这就是 KV Cache。
![](../../../../image/Pasted%20image%2020261102105352.png)
> [!info] ① 交叉注意力的 K、V
> 来自 Encoder 的最终输出。由于输入序列在整个解码过程中不会变化，因此可以**提前计算**，并在每一步解码时**重复使用**。

> [!abstract] ② 掩码自注意力的 K、V
> 每生成一个新 Token，Decoder 只需要计算新位置的 Q、K、V，再把新的 K 和 V **追加到缓存中**，过去位置不需要重新计算。
### 为什么不缓存 Q

在第 $t$ 个位置，模型会产生当前 Query $q_t$，并使用它查询当前所有可见位置的 Key，再按照注意力权重汇总对应的 Value。

当模型继续生成下一个 Token 时，会产生一个新的 Query $q_{t+1}$，过去的 Query 已经完成了自己的查询任务，后续计算通常不会再次使用它。

> [!important] 核心原因
> **Query 通常只服务于当前位置的一次查询**，而 **Key 和 Value 会持续作为历史信息被后续位置读取**。
### KV Cache 与 Prompt Cache

> [!info] KV CACHE · 一次生成内
> 主要发生在**一次自回归生成过程**中，复用已经处理过的 Token 在各层中产生的 Key 和 Value，避免生成每个新 Token 时重新计算全部历史内容。

> [!success] PROMPT CACHE · 跨请求
> 一些大模型服务还提供**跨请求的 Prompt Cache**，复用多个请求中**相同 Prompt 前缀**的计算结果，减少相同前缀被反复处理所需的时间和计算成本。

这也是为什么在 Agent 开发中，通常应该把稳定的系统提示词、工具定义和公共上下文放在 **Prompt 前部**，把经常变化的用户输入放在**后部**。

> [!important] 核心机制
> 模型中每个位置的中间状态都依赖它之前的内容。如果前缀较早的位置发生变化，后续大量计算结果就可能无法复用；**前缀越稳定，可以复用的范围通常越大**。

### 三类注意力，同一个过程

> [!info] 三类注意力共同的过程
> 根据 Query 与 Key 的匹配关系，**读取并汇总 Value**

> [!note] ① ENCODER 自注意力
> 输入序列内部相互读取，得到**输入序列的上下文表示**。

> [!note] ② 掩码自注意力
> 每个位置只读取当前可见的前缀，得到**目标序列的上下文表示**。

> [!note] ③ 交叉注意力
> Decoder 根据当前状态读取 Encoder 输出，**补充输入序列的信息**。

> [!important] 核心结论
> Attention 真正完成的是一次**序列表示的更新**：让每个 Token 从主要表示自身，变成一个融合了相关上下文信息的**新表示**。

### 自注意力回顾

每个 Token 用自己的 Query 与所有位置的 Key 算匹配度，再按匹配度汇总 Value——原本只表示自身的向量，被更新成融合了上下文的新表示。

$$
Q = XW_Q, \quad K = XW_K, \quad V = XW_V
$$
<div align="center">缩放点积注意力</div>
$$
\text{Attention}(Q, K, V) = \text{softmax} \left( \frac{QK^T}{\sqrt{d_k}} \right) V
$$

> [!info] 补充说明
> 不过重新看架构图，会发现其中写的并不是 Self-Attention，而是 **Multi-Head Attention**。

### Multi-Head Attention：多组投影再融合

同一输入走 **8 套独立的 Q、K、V 投影**——上一节讲的 Attention，只是其中的一个 Head。
![](../../../../image/Pasted%20image%2020261102110736.png)
$$
\text{head} = \text{Attention}(Q, K, V)
$$
<div align="center">每个 Head 独立投影</div>

$$
Q_i = XW_Q^{(i)}, \quad K_i = XW_K^{(i)}, \quad V_i = XW_V^{(i)}
$$
<div align="center">拼接 + 线性映射</div>

$$
O = \text{Concat}(\text{head}_1, \dots, \text{head}_h)W_O
$$
### 为什么需要多个 Head

一个 Head 只有一套投影，所有关系挤在同一空间。**多个 Head = 多套投影**，同一 `it` 在不同空间关注不同词。

> `The animal didn't cross the street because it was too tired.`

![](../../../../image/Pasted%20image%2020261102111101.png)

> [!note] 多头注意力的分工示例
> - **指代** | `animal` $\rightarrow$ `it`
> - **句法** | `was` $\rightarrow$ 句法结构
> - **语义** | `tired` $\rightarrow$ 主语状态

### 多个 Head，像 CNN 的多个卷积核

同一份输入，用**多套参数**提取多组特征再组合——这个思路并不新鲜。

| CNN · 多个卷积核                         | 🟰  | MULTI-HEAD · 多个 Head                             |
| :---------------------------------- | :-: | :----------------------------------------------- |
| 一个卷积核只能提取**一种**特征模式，所以同一层同时学习多个卷积核。 |     | 一个 Head 只有一套 $W_Q$、$W_K$、$W_V$，所以同一层同时学习多个 Head。 |

> [!warning] 但别想当然
> 每个 Head 学成什么样，由**训练过程自己决定**——不会有一个 Head 专门负责指代、另一个专门负责语法。
### 维度拆分：每个 Head 只看一个子空间

若 8 个 Head 都处理完整的 512 维，计算量直接翻 8 倍。Transformer 的做法是把表示空间切开分给各个 Head。

> [!info] 设定
> 
> $$
> d_{model} = 512, h = 8
> $$

⬇️

> [!abstract] 每个 HEAD 的维度
> 
> $$
> d_k = d_v = \frac{512}{8} = 64
> $$

⬇️

> [!example] 投影结果
> 
> $$
> Q_i, K_i, V_i \in \mathbb{R}^{N \times 64}
> $$

不是复制 8 份完整的 Attention，而是把一个 512 维的空间切成 8 个 64 维的子空间。
### 子空间变小了，注意力矩阵没变

无论子空间多小，每个 Head 得到的注意力权重矩阵**始终是 $N \times N$**——描述的仍是 $N$ 个位置彼此的关系，只是权重分布不同。
![](../../../../image/Pasted%20image%2020261102115030.png)
$$
Q_iK_i^T : (N, 64) \times (64, N) = (N, N)
$$

$$
(N, N) \times (N, 64) = (N, 64)
$$

<div align="center">8 个 Head 拼接</div>

$$
8 \times (N, 64) \rightarrow (N, 512)
$$

> [!important] 代码实现说明
> 代码实现时 Head 是张量的一个维度，矩阵运算**一次并行算完所有 Head**。
### 拼接之后，为什么还要一次线性映射

Concat 后维度已经回到 512，看上去和输入一致——但 8 段信息只是**排在不同的维度区间里**。

| head1 | head2 | head3 | head4 | head5 | head6 | head7 | head8 |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 64 维 | 64 维 | 64 维 | 64 维 | 64 维 | 64 维 | 64 维 | 64 维 |

$$
O = HW_O, \quad H = \text{Concat}(\text{head}_1, \dots, \text{head}_h)
$$

> [!info] CONCAT
> 把多个 Head 的结果**放进同一个向量**，各占一段。

> [!abstract] $W_O$
> 让每个输出维度都能**同时组合所有 Head**，信息真正混合。
### 总结：一套计算逻辑，多组表示空间

Attention 的计算逻辑一点没变，变的只是**投影参数从一套变成了多套**。

> [!note] ① 多组投影
> 同一序列被映射到**多个表示空间**，分别建立注意力关系。

> [!abstract] ② 维度拆分
> $d_{model}$ 切给多个 Head，避开计算量随 Head 数**线性膨胀**。

> [!success] ③ 重新融合
> Concat 恢复维度，$W_O$ **重新混合**各 Head 提取到的信息。

> [!important] 核心总结
> 让同一个序列在**多个不同的表示空间**中分别建立关系，再把这些关系产生的信息**重新融合**。
