# CNN 3 池化、分类与代码示例

## 池化层：降低分辨率

池化层使用一个小窗口在(进行卷积,非线性激活后的)特征图上滑动，对空间维度做下采样，最常见的是**最大池化 (max pooling)**。

一个 $2 \times 2$ 的最大池化窗口，会在每个局部区域中保留响应最强的那个值，使特征图的高和宽减半。
![](../../../../image/Pasted%20image%2020261026111249.png)
## 池化更重要的作用：扩大有效视野

池化把相邻区域压缩之后，下一层卷积核在特征图上的尺寸可以保持不变，但对应回原图时覆盖的区域更大。

> [!important] 核心结论
> 池化通过降低分辨率，让网络在看完局部之后，逐渐有能力看向整体。

---
![](../../../../image/Pasted%20image%2020261026111854.png)

> [!note] 直观理解
> 虽然卷积核在特征图上的尺寸相同（都是 $3 \times 3$），但因为特征图分辨率降低，每个位置对应回原图时覆盖的区域更大，从而更快扩大感受野。

## Flatten 与全连接：从特征图到类别
卷积部分输出的是 $C \times H \times W$ 结构：有通道，有高度，也有宽度。但分类任务最终需要的是每个类别对应的判断结果。
![](../../../../image/Pasted%20image%2020261026112148.png)
> [!info] 核心步骤
> - **Flatten**：特征图拉成一维向量
> - **Linear**：映射到类别数维度
> - **Softmax**：推理时转成概率分布

## CNN 最后也用全连接，为什么没问题？
| MLP 直接处理图像                            | CNN 后面的全连接                         |
| :------------------------------------ | :--------------------------------- |
| 输入维度高，空间结构一开始就被展平，全连接层需要直接从原始像素中寻找模式。 | 处理的是多层卷积和池化之后的高层特征，尺寸更小、语义更强、冗余更少。 |
> [!important] 核心结论
> 全连接层在这里不再负责从原始像素中找模式，而是根据高层特征做最终判断。

## 最小 CNN 的形状流
```text
Input                   3 × 32 × 32
Conv(16, 3×3, pad=1)    16 × 32 × 32
ReLU                    16 × 32 × 32
MaxPool(2×2)            16 × 16 × 16
Conv(32, 3×3, pad=1)    32 × 16 × 16
ReLU                    32 × 16 × 16
MaxPool(2×2)            32 × 8 × 8
Flatten                 2048
Linear                  10
```

> [!info] 输入图像  
> 3×32×323×32×32，原始 RGB 像素。

> [!success] Conv + ReLU  
> 提取 16 类低级局部特征。

> [!warning] MaxPool  
> 空间分辨率减半。

> [!note] 第二组卷积  
> 组合更复杂的局部模式。

> [!important] Flatten + Linear  
> 从特征图走向 10 类得分。

## CNN 内部的三个变化

|空间尺寸变小|通道数变多|语义层级变高|
|---|---|---|
|从 32×3232×32 到 16×1616×16，再到 8×88×8。|从 33 到 1616，再到 3232。|从边缘纹理，逐渐接近部件和整体结构。|

> [!important] 核心规律  
> **空间越来越小，通道越来越多，语义越来越抽象。**
## PyTorch 实现最小CNN代码
下面的代码实现了刚才的形状流. 输入是3 * 32 * 32 的彩色图像, 输出是 10 个类别得分.

```python
import torch
import torch.nn as nn

class SmallCNN(nn.Module):
    def __init__(self, num_classes=10):
        super().__init__()

        self.features = nn.Sequential(
            # 第一组 Conv -> ReLU -> Pool:
            # 输入是 RGB 图像，所以 in_channels=3; 输出 16 张特征图，所以 out_channels=16。
            # kernel_size=3 表示 3 × 3 卷积核，padding=1 可以让输出高宽仍然保持 32 × 32。
            nn.Conv2d(3, 16, kernel_size=3, padding=1),    # [B, 3, 32, 32]  -> [B, 16, 32, 32]
            nn.ReLU(),                                     # 引入非线性，保留正响应，抑制负响应。
            nn.MaxPool2d(kernel_size=2),                   # 2 × 2 池化让高宽减半: [B, 16, 32, 32] -> [B, 16, 16, 16]

            # 第二组 Conv -> ReLU -> Pool:
            # 在上一层 16 张特征图的基础上，学习 32 种更复杂的局部模式。
            nn.Conv2d(16, 32, kernel_size=3, padding=1),   # [B, 16, 16, 16] -> [B, 32, 16, 16]
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2),                   # 再次下采样: [B, 32, 16, 16] -> [B, 32, 8, 8]
        )

        self.classifier = nn.Sequential(
            nn.Flatten(),                                  # 把 32 张 8 × 8 特征图拉平成向量: [B, 32, 8, 8] -> [B, 2048]
            nn.Linear(32 * 8 * 8, num_classes),            # 全连接分类器输出 10 个类别得分: [B, 2048] -> [B, 10]
        )

    def forward(self, x):
        # 先用卷积部分提取空间特征，再用分类器输出每个类别的 logits。
        x = self.features(x)
        x = self.classifier(x)
        return x

model = SmallCNN()
x = torch.randn(4, 3, 32, 32)  # 模拟一个 batch: 4 张 RGB 图片，每张大小 32 × 32。
y = model(x)                   # 前向传播后，每张图片得到 10 个类别得分。
print(y.shape)
```
## 最小 CNN 的输出与训练结果

> [!important] 核心提示  
> **输出结果是 `torch.Size([4, 10])`: 4 表示 batch size，10 表示每张图片对应 10 个类别得分。**

- `Conv2d(3, 16)` 表示输入通道数为 3，输出通道数为 16。
    
- `padding=1` 让 3 × 3 卷积保持空间尺寸不变。
    
- `MaxPool2d(2)` 会把高和宽都减半。
    
- 两轮池化后，最后全连接层输入维度是 32 × 8 × 8 = 2048。
    
---
**训练日志：**
Epoch 01 | loss=1.7014 | test_acc=47.56%
Epoch 02 | loss=1.3642 | test_acc=55.12%
Epoch 03 | loss=1.2312 | test_acc=57.91%
Epoch 04 | loss=1.1650 | test_acc=58.90%
Epoch 05 | loss=1.1029 | test_acc=61.42%
## 更接近实际训练的 CNN 写法

最小 CNN 适合理解形状变化。但在 CIFAR-10 这样的彩色图像任务上，如果希望训练表现更稳定，通常还会加入一些常见改进。

| 改进项           | 作用            | 改进项       | 作用               | 改进项           | 作用             |
| :------------ | :------------ | :-------- | :--------------- | :------------ | :------------- |
| **Normalize** | 让输入分布更稳定。     | **更多卷积层** | 提高特征组合能力。        | **BatchNorm** | 控制中间激活尺度。      |
| **Dropout**   | 降低对训练样本细节的依赖。 | **数据增强**  | 让模型看到同一类图像的不同扰动。 | **学习率调度**     | 让训练后期的参数更新更细致。 |
## BetterCNN: 更完整的特征提取器

下面直接在代码里标出相对 `SmallCNN` 新增的能力。重点看带有 `新增能力` 的注释块。

```python
class BetterCNN(nn.Module):
    def __init__(self, num_classes=10):
        super().__init__()

        self.features = nn.Sequential(
            # ===== 新增能力 1: 更多卷积层 =====
            # SmallCNN 每组只有一层卷积；这里每组连续堆叠 3 × 3 卷积，
            # 让模型在下采样前先组合出更丰富的局部模式。
            nn.Conv2d(3, 32, kernel_size=3, padding=1),  # [B, 3, 32, 32] -> [B, 32, 32, 32]

            # ===== 新增能力 2: BatchNorm =====
            # 对每个通道的激活做归一化，让中间特征的数值分布更稳定。
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.Conv2d(32, 32, kernel_size=3, padding=1), # [B, 32, 32, 32] -> [B, 32, 32, 32]
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2),                 # [B, 32, 32, 32] -> [B, 32, 16, 16]
            
            # ===== 新增能力 3: Dropout =====
            # 训练时随机丢弃一部分激活，减少模型对训练样本细节的依赖。
            nn.Dropout(0.20),
            
```
## 改进版 CNN 的训练表现
训练 5 轮后准确率可以到 74% 左右，训练 10 轮准确率可以提高到 79% 左右。
```
Epoch 01 | loss=1.5873 | test_acc=54.33%
Epoch 02 | loss=1.1680 | test_acc=62.02%
Epoch 03 | loss=1.0017 | test_acc=69.32%
Epoch 04 | loss=0.9130 | test_acc=69.66%
Epoch 05 | loss=0.8510 | test_acc=74.02%
Epoch 06 | loss=0.7680 | test_acc=77.28%
Epoch 07 | loss=0.7428 | test_acc=77.78%
Epoch 08 | loss=0.7203 | test_acc=76.48%
Epoch 09 | loss=0.7046 | test_acc=78.84%
Epoch 10 | loss=0.6891 | test_acc=79.10%
```
> [!important] 核心观点  
> CNN 架构设计不是只堆卷积层。卷积层决定如何提取视觉特征，归一化、正则化、数据增强和学习率调度共同决定这些特征能不能稳定学出来。

## 总结：CNN 如何看懂一张图像

> [!info] 卷积层
> 使用可学习的卷积核，在局部窗口中提取模式；卷积核数量决定输出通道数。

> [!success] ReLU
> 让卷积得到的特征响应具备非线性，使多层网络能组合复杂视觉模式。

> [!tip] 池化层
> 降低分辨率、减少计算量，同时扩大后续层的有效感受野。

> [!note] Flatten $\rightarrow$ Linear
> 把高度抽象、尺寸压缩后的特征图转换成类别得分。

> [!important] 核心流程
> 卷积核提取局部特征，特征图保留空间响应，池化扩大有效视野，多层堆叠完成抽象组合，最终由分类器输出图像类别。
