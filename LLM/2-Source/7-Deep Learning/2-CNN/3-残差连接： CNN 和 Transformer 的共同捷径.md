# 残差连接： CNN 和 Transformer 的共同捷径

## CNN 的演进先沿着深度推进

| LeNet-5 | AlexNet | VGGNet | GoogLeNet |
| :--- | :--- | :--- | :--- |
| 1998 · 约 5 层 | 2012 · 约 8 层 | 2014 · 16 / 19 层 | 2014 · 约 22 层 |
| 奠定 **卷积 + 池化 + 全连接** 的基础范式，在支票手写邮编识别上进入实际应用。 | 引入 ReLU、Dropout、数据增强与 GPU 训练，ImageNet top-5 错误率降到 15.3%。 | 用连续堆叠的 $3 \times 3$ 小卷积证明：更深的简单结构也可以非常有效。 | 通过多尺度并行分支和 $1 \times 1$ 卷积继续加深，top-5 错误率降到 6.67%。 |

> [!important] 核心规律
> 早期 CNN 语义层层组合出来，**网络越深，能表达的视觉概念通常越复杂**。

## 但继续加深之后，反常现象出现了
如果网络越深越好，那么把层数从几十层堆到上百层，训练误差至少不应该变差。
ResNet 论文在 CIFAR-10 上比较了 20 层和 56 层普通网络。结果显示：更深的网络不只是测试集效果下降，连**训练集误差**也更高。
![](../../../../image/Pasted%20image%2020261026143058.png)
> [!important] 核心结论
> 问题不出在泛化，而出在优化本身。

## 退化不是过拟合，而是优化问题
过拟合的典型症状是训练误差很低、测试误差很高，模型把训练集背得很熟，泛化却差。
深度网络的退化不同：网络连训练集误差都降不下去。
![](../../../../image/Pasted%20image%2020261026143214.png)
> [!important] 核心概念
> 深层网络更难被训练到一个好的解，这个现象叫做**退化（degradation）**。
---

## 为什么“什么都不做”反而很难学

| 普通堆叠                                                                                                 | 残差思路                                                                               |
| :--------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------- |
| 多层 Conv $\rightarrow$ BN $\rightarrow$ ReLU 叠在一起，要让复合变换精确等于输入，需要权重落在非常特殊的位置。<br><br>$H(x) \approx x$ | 让主路径只学需要补充的变化；如果没有必要改变输入，只要把残差压到 0。<br><br>$H(x) = F(x) + x, \quad F(x) \approx 0$ |

> [!important] 核心结论
> 把一组卷积层的权重学到接近 0，通常比让它们精确学出恒等映射容易得多。

## ResNet 的突破：让深层网络重新可训练

> [!abstract] 核心数据
> - **152 层**：2015 年，ResNet 把网络深度推进到 152 层。
> - **3.57%**：ImageNet top-5 错误率进一步降到低于人类标注者错误率的水平。

> [!info] 关键结构
> 这个突破依赖的关键结构，就是**残差连接（residual connection）**。
> 
> 它并没有推翻 CNN 从局部纹理到高级语义的路线，而是改变了每一段特征变换的**学习方式**。

> [!quote] 延伸意义
> 理解残差连接，也是在提前理解 **Transformer** 里的 **Add & Norm**。

## 残差：还没有解释掉的那一部分

在回归问题里，残差的含义非常明确：**真实值里还没有被当前模型解释掉的部分。**

$$
r = y - \hat{y}
$$

> [!important] 核心思想
> **Boosting 方法**也体现了这种思想：新加入的模型不必一次解决全部问题，而是**一级一级地补当前还没解释好的部分**。

### 🏌️ 直观比喻：高尔夫球与 Boosting

| 挥杆阶段            | 动作与目标                        | 剩余距离（残差）                 |
| :-------------- | :--------------------------- | :----------------------- |
| **目标**          | 距离球洞 350 米                   | -                        |
| **第一杆（第 1 棵树）** | 大力开球，打了 300 米                | 离球洞还差：$350 - 300 = 50$ 米 |
| **第二杆（第 2 棵树）** | 目标不是重打 350 米，而是**“补上”**剩下的距离 | 继续逼近，填补剩余的残差             |

> [!tip] 总结
> Boosting 的思想：**每一棵树（每一杆）都专注于纠正前一棵树的残差（剩余误差），一步步逼近目标。**

## 加性建模：不要一步到位，而是逐步修正

> [!note] 模型由多个增量相加
> $$
> F = f_0 + f_1 + f_2 + \cdots
> $$
> 最终模型由多个增量相加而来，不要求某一步独立完成全部任务。

> [!note] 逐步逼近目标
> $$
> \hat{y}_{t+1} = \hat{y}_t + \eta h_t(x)
> $$
> 其中 $h_t(x)$ 是新加入的弱学习器，$\eta$ 控制每次修正幅度。

> [!important] 核心迁移
> **残差连接**把这种“在已有结果上做修正”的思想搬进了深层 CNN。

## CNN 里的残差：对特征图的修正量
与其让一组层直接学习目标映射 $H(x)$，不如让它只学习输入基础上还需要补多少。
![](../../../../image/Pasted%20image%2020261026144546.png)
> [!math] 核心公式
> $$
> H(x) = F(x) + x
> $$
> 
> $$
> F(x) = H(x) - x
> $$


> [!important] 结构解析
> - **主路径**：学习残差映射 $F(x)$（即对特征图的修正量）。
> - **跳跃连接（Skip Connection）**：把输入 $x$ 原样送到输出处相加。

## 这里的 $x$ 不是一个数，而是一整张特征图

| 输入特征                                               | 残差修正                          | 相加输出                     |
| :------------------------------------------------- | :---------------------------- | :----------------------- |
| $x$ 的形状是 $C \times H \times W$，代表已经提取出来的一组特征图。 | $F(x)$ 不是一个数字，而是一组同样形状的修正量。 | 已有特征原样传下去，卷积层只负责补充或修正细节。 |

> [!important] 核心结论
> 当这层不需要做任何事情时，只要让 $F(x)$ 接近 0，输出就自动等于输入 $x$。

## 带残差连接的 CNN：ResNet 主干
输入图像先经过 **stem** 转成初始特征图，随后进入多个 **stage**。
![](../../../../image/Pasted%20image%2020261026145312.png)
> [!info] 宏观结构
> 每个 stage 内堆叠残差块；stage 之间空间尺寸逐步变小，通道数逐步变多。
> 

> [!important] 核心结论
> ResNet 不是等宽长链，而是带有尺度变化节奏的 CNN 主干。

## Stage 决定尺度，残差块负责修正

| 模块       | 输出形状           | 作用                      |
| :------- | :------------- | :---------------------- |
| 输入       | `[3, 32, 32]`  | RGB 图像                  |
| stem     | `[16, 32, 32]` | 用 $3\times3$ 卷积提取初始特征 |
| stage 1  | `[16, 32, 32]` | 保持分辨率，提取局部纹理            |
| stage 2  | `[32, 16, 16]` | 下采样一次，增加通道数             |
| stage 3  | `[64, 8, 8]`   | 再次下采样，形成更抽象的语义特征        |
| GAP + FC | `[10]`         | 输出 10 类 logits          |

> [!important] 核心规律
> 浅层保留边缘、颜色和纹理；越往后，空间尺寸降低，感受野变大，通道表达更多语义模式。

## Stem: 把像素转换成初始特征图

针对不同尺寸的图像输入，ResNet 的 Stem（主干入口）设计有显著差异：

| 对比维度     | ImageNet 版 ResNet             | CIFAR-10 版 ResNet             |
| :------- | :---------------------------- | :---------------------------- |
| **输入图像** | $(3 \times 224 \times 224)$   | $(3 \times 32 \times 32)$     |
| **卷积操作** | Conv $(7 \times 7)$, stride=2 | Conv $(3 \times 3)$, stride=1 |
| **池化操作** | MaxPool, stride=2             | 无                             |
| **输出形状** | $(64 \times 56 \times 56)$    | $(16 \times 32 \times 32)$    |
| **设计考量** | 大图像先快速降低分辨率，减少后续计算量。          | 小图像不能一开始缩得太快，否则细节会过早丢失。       |

> [!important] 核心设计思想
> **Stem 的设计取决于输入分辨率**：大图需要快速降维来节约算力，小图则需要平缓降维以保留空间细节。

## BasicBlock：最容易理解的残差块
![](../../../../image/Pasted%20image%2020261026150454.png)
**结构组成**：
- **主路径**：Conv $3\times3$ $\rightarrow$ BatchNorm $\rightarrow$ ReLU $\rightarrow$ Conv $3\times3$ $\rightarrow$ BatchNorm，得到残差 $F(x)$。
- **捷径连接 (Shortcut / Identity)**：输入 $x$ 原样跳过主路径。
- **融合输出**：$y = F(x) + x$，最后通常再经过一次 ReLU 激活。

**张量形状变化**：

| 操作步骤 | 输出形状 (以 $C \times H \times W$ 为例) |
| :--- | :--- |
| 输入 $x$ | $C \times H \times W$ |
| Conv $3\times3$, BN, ReLU | $C \times H \times W$ |
| Conv $3\times3$, BN | $C \times H \times W$ |
| $\oplus \ x$  (skip 相加) | $C \times H \times W$ |
| ReLU | $C \times H \times W$ |

> [!important] 核心结论
> 同一个 stage 内部，输入输出形状通常相同，所以 shortcut 可以直接做**恒等相加**（即 $F(x)$ 和 $x$ 的形状完全一致，无需额外调整）。

## 进入新 stage 时，需要投影 shortcut
新 stage 的第一个残差块通常让**空间尺寸减半、通道数增加**。此时输入 $x$ 和主路径输出 $F(x)$ 的形状不一致，无法直接相加。
![](../../../../image/Pasted%20image%2020261026151013.png)
> [!info] 结构设计：如何对齐形状？
> - **主路径**：第一个 $3\times3$ 卷积使用 `stride = 2` 进行下采样。
> - **Shortcut 分支**：不再直接做恒等映射，而是使用 **$1\times1$ 卷积** 且 `stride = 2` 进行投影，以匹配通道数和步长。
**对应的计算公式**：
$$
H(x) = F(x) + W_s x
$$
*(其中 $W_s$ 代表用于对齐形状的 $1\times1$ 卷积操作)*
## BasicBlock 的 PyTorch 实现
```python
import torch
import torch.nn as nn
class BasicBlock(nn.Module):
    def __init__(self, in_channels, out_channels, stride=1):
        super().__init__()
        # 主路径：两层 3x3 卷积。第一层用 stride 控制是否下采样，bias=False 是因为后面紧跟 BN。
        self.conv1 = nn.Conv2d(in_channels, out_channels, 3, stride=stride, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.conv2 = nn.Conv2d(out_channels, out_channels, 3, stride=1, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(out_channels)
        # 跳跃连接：形状不变时就是恒等映射（什么都不做）；
        # 一旦下采样或通道数改变，就用 1x1 卷积把 x 投影到和主路径对齐的形状。
        self.shortcut = nn.Sequential()
        if stride != 1 or in_channels != out_channels:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_channels, out_channels, 1, stride=stride, bias=False),
                nn.BatchNorm2d(out_channels)
            )
    def forward(self, x):
        out = torch.relu(self.bn1(self.conv1(x)))  # 主路径第一层：卷积 -> BN -> ReLU
        out = self.bn2(self.conv2(out))            # 主路径第二层：卷积 -> BN (先不激活)
        out = out + self.shortcut(x)               # 残差相加：F(x) + x 或 F(x) + W_s x
        out = torch.relu(out)                      # 相加之后再激活
        return out
```
## Bottleneck：更深 ResNet 的计算控制
ResNet-50、101、152 网络越来越深，如果每个残差块仍使用两个完整 $3\times3$ 卷积，计算量会非常大。为了解决这个问题，引入了 **Bottleneck（瓶颈）结构**。
![](../../../../image/Pasted%20image%2020261026151509.png)
> [!info] 核心思路：$1\times1 \rightarrow 3\times3 \rightarrow 1\times1$
> 通过“两头细、中间粗”的设计，大幅减少参数量和计算量：
> - **$1\times1$ 卷积**：降通道（压缩特征维度）
> - **$3\times3$ 卷积**：处理空间邻域（在低维空间提取特征）
> - **$1\times1$ 卷积**：升通道（恢复特征维度）

## Bottleneck 降的是中间通道，不是默认降分辨率

Bottleneck 结构的设计核心是**压缩中间通道数**以减少 $3\times3$ 卷积的计算量，而不是在默认情况下降低空间分辨率（分辨率只在特定阶段改变）。

### 形状不变的 Bottleneck 示例

当输入输出空间尺寸不变时，通道数经历“降维 $\rightarrow$ 卷积 $\rightarrow$ 升维”的过程：

| 操作 | 张量形状（通道数 $\times$ 高 $\times$ 宽） |
| :--- | :--- |
| 输入 $x$ | $256 \times 56 \times 56$ |
| Conv $1\times1$ | $64 \times 56 \times 56$ （降通道） |
| Conv $3\times3$ | $64 \times 56 \times 56$ （空间处理） |
| Conv $1\times1$ | $256 \times 56 \times 56$ （升通道） |
| $\oplus \ x$ | $256 \times 56 \times 56$ |

### 两类残差块对比

| 残差块 | 主路径结构 | 常见网络 |
| :--- | :--- | :--- |
| **BasicBlock** | $3\times3 \rightarrow 3\times3$ | ResNet-18 / 34 |
| **Bottleneck** | $1\times1 \rightarrow 3\times3 \rightarrow 1\times1$ | ResNet-50 / 101 / 152 |

> [!important] 核心结论
> **只有进入新 stage 的第一个 Bottleneck**，才会通过 `stride = 2` 改变空间尺寸（下采样）；同一 stage 内的其他 Bottleneck 只改变中间通道数，保持空间分辨率不变。

## Global Average Pooling (GAP)
经过多个 stage 后，ResNet 最后一个 stage 会输出一组高层特征图。GAP 层把这组特征图逐通道压缩。
![](../../../../image/Pasted%20image%2020261026152104.png)
> [!math] 维度变化与公式
> 维度变化：$[C, H, W] \rightarrow [C, 1, 1] \rightarrow [C]$
> 
> 逐通道求平均公式：
> $$
> z_c = \frac{1}{HW} \sum_{i,j} x_{c,i,j}
> $$
### GAP 的两个核心动作
> [!info] 1. 逐通道求平均
> 第 $c$ 个通道的 $H \times W$ 个位置，被平均成 1 个数。
> [!info] 2. 特征图变成向量
> $C$ 张特征图最终变成长度为 $C$ 的分类向量。

>[!important] 核心作用  
**GAP 的核心作用**：把最后一个 stage 输出的 CC 张特征图，逐通道从 H×WH×W 压缩成 1×11×1（即 1 个数），从而无缝衔接后续的全连接层（FC），大幅减少了传统全连接层带来的海量参数。
## 把残差块放进 CIFAR-10 训练流程

> [!note] 为什么是 CIFAR ResNet
> CIFAR-10 图像只有 $32 \times 32$，开头不适合使用 ImageNet ResNet 那种大卷积和最大池化，否则空间信息会过早丢失。

> [!info] 核心改动
> 开头只用一层 $3\times3$ 卷积，随后依次堆叠 $16 \rightarrow 32 \rightarrow 64$ 三个通道阶段。

### 网络结构流向

`输入 (3 x 32 x 32)` $\rightarrow$ `Stem (3x3 Conv)` $\rightarrow$ `Stage 1 (16 通道)` $\rightarrow$ `Stage 2 (32 通道)` $\rightarrow$ `Stage 3 (64 通道)`

> [!important] 空间与形状对齐规则
> - 每次进入新阶段时，用 **`stride = 2`** 进行下采样；
> - 形状发生变化时，用 **$1\times1$ shortcut 投影**对齐维度。

### 训练设置

| 数据增强        | 优化器策略            |
| :---------- | :--------------- |
| 随机裁剪 + 水平翻转 | SGD + momentum   |
| -           | weight decay 正则化 |
| -           | MultiStep 学习率衰减  |
## CIFAR-10 ResNet 完整代码实现
## 这段代码和架构分析——对应

将前面代码中的网络模块与张量形状的流动轨迹一一对应：

| 模块 | 张量形状（通道数 × 高 × 宽） | 对应代码中的变量/操作 |
| :--- | :--- | :--- |
| **输入 (Input)** | `[3, 32, 32]` | CIFAR-10 RGB 图像 |
| **stem** | `[16, 32, 32]` | `self.stem` (一层 $3\times3$ 卷积，不降采样) |
| **layer1** (Stage 1) | `[16, 32, 32]` | `self.stage1` (保持空间尺寸) |
| **layer2** (Stage 2) | `[32, 16, 16]` | `self.stage2` (首次用 stride=2 减半空间，通道翻倍) |
| **layer3** (Stage 3) | `[64, 8, 8]` | `self.stage3` (再次用 stride=2 减半空间，通道翻倍) |

> [!important] 核心结论
> **主路径负责学习修正量，跳跃连接负责保留已有信息。网络因此可以放心继续加深。**
```python
import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
from torch.utils.data import DataLoader

# ==========================================
# 1. 定义基础残差块 (BasicBlock)
# ==========================================
class BasicBlock(nn.Module):
    # BasicBlock 的输出通道数不会被放大; Bottleneck 才会用 expansion=4。
    expansion = 1

    def __init__(self, in_channels, out_channels, stride=1):
        super().__init__()

        # 主路径第一层: 3x3 卷积负责提取局部特征。
        # stride=2 时同时完成下采样, 把 H、W 减半; padding=1 保持 3x3 卷积前后尺寸对齐。
        self.conv1 = nn.Conv2d(in_channels, out_channels, 3, stride=stride, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(out_channels)

        # 主路径第二层: 继续做一次 3x3 特征变换。
        # 这里固定 stride=1, 因为是否下采样只由第一层控制。
        self.conv2 = nn.Conv2d(out_channels, out_channels, 3, stride=1, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(out_channels)

        # 跳跃连接 (Shortcut)
        # 形状不变时就是恒等映射（什么都不做）
        self.shortcut = nn.Sequential()
        # 一旦下采样或通道数改变，就用 1x1 卷积把 x 投影到和主路径对齐的形状
        if stride != 1 or in_channels != out_channels:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_channels, out_channels, 1, stride=stride, bias=False),
                nn.BatchNorm2d(out_channels)
            )

    def forward(self, x):
        out = torch.relu(self.bn1(self.conv1(x)))  # 主路径第一层: 卷积 -> BN -> ReLU
        out = self.bn2(self.conv2(out))            # 主路径第二层: 卷积 -> BN (先不激活)
        out = out + self.shortcut(x)               # 残差相加: F(x) + x 或 F(x) + W_s x
        out = torch.relu(out)                      # 相加之后再统一激活
        return out


# ==========================================
# 2. 定义 CifarResNet 主体
# ==========================================
class CifarResNet(nn.Module):
    def __init__(self, block=BasicBlock, num_blocks=(3, 3, 3), num_classes=10):
        super().__init__()

        # self.in_channels 记录当前特征图的通道数, 构建每个阶段时会不断更新。
        self.in_channels = 16

        # CIFAR-10 图片只有 32x32, 所以不用 ImageNet ResNet 的 7x7 卷积和最大池化。
        # 这里用 3x3 卷积保留空间分辨率, 把输入从 [3, 32, 32] 变成 [16, 32, 32]。
        self.stem = nn.Sequential(
            nn.Conv2d(3, 16, 3, stride=1, padding=1, bias=False),
            nn.BatchNorm2d(16),
            nn.ReLU(inplace=True),
        )

        # 三个阶段分别使用 16、32、64 个通道。
        # stage1 不下采样; stage2 和 stage3 的第一个 block 用 stride=2, 把空间尺寸减半。
        self.stage1 = self._make_layer(block, 16, num_blocks[0], stride=1)  # [16, 32, 32]
        self.stage2 = self._make_layer(block, 32, num_blocks[1], stride=2)  # [32, 16, 16]
        self.stage3 = self._make_layer(block, 64, num_blocks[2], stride=2)  # [64, 8, 8]

        # 全局平均池化把每个通道的 8x8 特征压成 1 个数, 得到长度为 64 的向量。
        self.pool = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Linear(64 * block.expansion, num_classes)

    def _make_layer(self, block, out_channels, num_blocks, stride):
        # 每个阶段的第一个 block 可能负责下采样, 后面的 block 都保持尺寸不变。
        # 例如 stride=2、num_blocks=3 时, strides = [2, 1, 1]。
        strides = [stride] + [1] * (num_blocks - 1)
        layers = []

        for s in strides:
            layers.append(block(self.in_channels, out_channels, s))
            # 当前 block 结束后, 下一层看到的输入通道数就是 out_channels。
            self.in_channels = out_channels * block.expansion

        return nn.Sequential(*layers)

    def forward(self, x):
        # x: [batch_size, 3, 32, 32]
        out = self.stem(x)           # [batch_size, 16, 32, 32]
        out = self.stage1(out)       # [batch_size, 16, 32, 32]
        out = self.stage2(out)       # [batch_size, 32, 16, 16]
        out = self.stage3(out)       # [batch_size, 64, 8, 8]
        out = self.pool(out)         # [batch_size, 64, 1, 1]
        out = torch.flatten(out, 1)  # [batch_size, 64]
        return self.fc(out)          # [batch_size, 10]


# ==========================================
# 3. 训练与评估函数
# ==========================================
def train_one_epoch(model, loader, criterion, optimizer, device):
    # 进入训练模式: BN 会更新均值方差, Dropout (如果有) 会随机失活。
    model.train()
    total_loss, correct, total = 0.0, 0, 0

    for images, labels in loader:
        images, labels = images.to(device), labels.to(device)

        # 标准训练四步: 清梯度 -> 前向传播 -> 反向传播 -> 参数更新。
        optimizer.zero_grad()
        logits = model(images)
        loss = criterion(logits, labels)
        loss.backward()
        optimizer.step()

        # loss.item() 是当前 batch 的平均 loss, 乘以 batch 大小后才能累加成全数据集平均值。
        total_loss += loss.item() * labels.size(0)
        correct += (logits.argmax(dim=1) == labels).sum().item()
        total += labels.size(0)

    return total_loss / total, correct / total


@torch.no_grad()
def evaluate(model, loader, criterion, device):
    # 进入评估模式: BN 使用训练时累计的统计量, 不再根据当前 batch 更新。
    model.eval()
    total_loss, correct, total = 0.0, 0, 0

    for images, labels in loader:
        images, labels = images.to(device), labels.to(device)
        logits = model(images)
        loss = criterion(logits, labels)

        total_loss += loss.item() * labels.size(0)
        correct += (logits.argmax(dim=1) == labels).sum().item()
        total += labels.size(0)

    return total_loss / total, correct / total


# ==========================================
# 4. 主程序入口
# ==========================================
def main():
    # 优先使用 NVIDIA GPU; Apple 芯片可用 mps; 都没有时退回 CPU。
    device = torch.device(
        "cuda" if torch.cuda.is_available()
        else "mps" if torch.backends.mps.is_available()
        else "cpu"
    )

    # CIFAR-10 训练集的 RGB 均值和标准差, 用于把输入归一化到更稳定的尺度。
    mean = (0.4914, 0.4822, 0.4465)
    std = (0.2470, 0.2435, 0.2616)

    # 训练集使用数据增强: 先在四周补 4 个像素, 再随机截回 32x32, 相当于轻微平移图像。
    # 随机水平翻转可以让模型不要把物体朝向记得过死。
    train_transform = transforms.Compose([
        transforms.RandomCrop(32, padding=4),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize(mean, std),
    ])

    # 测试集不能使用随机增强, 否则每次评估的输入都不同; 这里只做张量转换和归一化。
    test_transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(mean, std),
    ])

    # 加载 CIFAR-10 数据集
    train_set = torchvision.datasets.CIFAR10(
        root="./data",
        train=True,
        download=True,
        transform=train_transform,
    )
    test_set = torchvision.datasets.CIFAR10(
        root="./data",
        train=False,
        download=True,
        transform=test_transform,
    )

    # shuffle=True 只用于训练集, 让每个 epoch 的 batch 组合不同。
    train_loader = DataLoader(train_set, batch_size=128, shuffle=True, num_workers=2)
    test_loader = DataLoader(test_set, batch_size=256, shuffle=False, num_workers=2)

    # 实例化模型
    model = CifarResNet().to(device)
    criterion = nn.CrossEntropyLoss()

    # SGD + momentum 是 ResNet 训练中的经典组合; weight_decay 对卷积权重做 L2 正则化。
    optimizer = optim.SGD(model.parameters(), lr=0.1, momentum=0.9, weight_decay=5e-4)

    # 第 100 和 150 个 epoch 后把学习率乘以 0.1: 前期快速学习, 后期小步精修。
    scheduler = optim.lr_scheduler.MultiStepLR(optimizer, milestones=[100, 150], gamma=0.1)

    # 开始训练循环
    epochs = 200
    for epoch in range(1, epochs + 1):
        train_loss, train_acc = train_one_epoch(model, train_loader, criterion, optimizer, device)
        test_loss, test_acc = evaluate(model, test_loader, criterion, device)
        scheduler.step()

        print(
            f"epoch {epoch:03d} | "
            f"train loss {train_loss:.4f}, train acc {train_acc:.2%} | "
            f"test loss {test_loss:.4f}, test acc {test_acc:.2%}"
        )

if __name__ == "__main__":
    main()
```
## 残差连接已经超越 CNN

> [!info] CNN 架构继续演进
> - **ResNeXt**：残差块里加入分组卷积
> - **DenseNet**：用拼接让浅层特征反复复用
> - **SENet**：在残差块中加入通道注意力
> - **ConvNeXt**：保留卷积主干，吸收 Transformer 时代设计

> [!success] 深层网络的通用组件
> **Transformer** 在每一个子层外面都套了一圈残差连接，并配合归一化一起使用。
>
> ```text
> Add & Norm
> ```

> [!important] 核心意义
> 残差连接让训练**数百甚至上千层**的网络成为可能。

## 一条捷径，改变了深度学习的默认结构

> [!abstract] 20 万+
> ResNet 论文《Deep Residual Learning for Image Recognition》
> 引用量已突破 **20 万次**。
> [ResNet残差神经网络](ResNet残差神经网络.pdf)

它的影响越出了图像分类，被迁移到目标检测、语义分割、NLP、语音、强化学习等几乎所有深度学习子领域。

> [!important] 核心结论
> 残差连接不再只是一个 CNN 技巧，而是**深层网络的标准组件**。

## 总结：残差连接到底解决了什么

| 核心维度 | 具体作用 |
| :--- | :--- |
| **解决退化问题** | 一味加深层数会触发网络退化，网络连训练误差都更高。残差连接打破了这一限制。 |
| **学习增量** | 把目标从学习完整映射 $H(x)$ 改成学习增量 $F(x) = H(x) - x$。 |
| **特征修正** | 在 CNN 里，$x$ 是特征图，$F(x)$ 是对输入特征图的修正量。 |
| **架构节奏** | ResNet 用 stem、stage、残差块和全局平均池化，组成可训练的深层 CNN 主干。 |

> [!important] 一句话总结
> 把残差连接压缩成一句话：**让网络去学在已有基础上的增量，而不是从零开始的全部。**
