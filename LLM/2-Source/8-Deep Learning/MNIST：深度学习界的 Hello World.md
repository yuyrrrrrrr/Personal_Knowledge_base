
MNIST 是 $28 \times 28$ 的灰度手写数字图，0-9 共 10 类。

| 60 000 | 10 000 |
| :---: | :---: |
| **训练集** | **测试集** |
| **$28 \times 28$** | **10 类** |
| 每张图（灰度） | 数字 0-9 |

> [!tip] 核心优势
> 小到能在 CPU 上几十秒跑完，又足够真实——是**验证想法的标准沙盘**。

## 网络结构：$784 \to 128 \to 10$

最朴素的 2 层 MLP——三句话讲完它的所有秘密：

| 输入 (784) | 隐层 (128) | 输出 (10) |
| :--- | :--- | :--- |
| 把 $28 \times 28$ 灰度图**拍平成 784 维向量**<br>——每一个像素是一个特征。 | $\text{ReLU}(W_1 x + b_1)$——仿射变换 + 非线性。<br>是网络真正"学东西"的地方。 | $W_2 h + b_2$——10 维 logits，<br>对应 10 个数字类别。 |

| 参数量                                                                                                                      | 为什么是 128，不是 256 或 64？                               |
| :----------------------------------------------------------------------------------------------------------------------- | :-------------------------------------------------- |
| $W_1$: $784 \times 128$, $b_1$: $128 \to 100\ 480$<br>$W_2$: $128 \times 10$, $b_2$: $10 \to 1\ 290$<br>共 $101\ 770$ 个参数 | 没什么特别理由——2 的幂次顺手，跑得动就行。今天我们关心的是"训练循环长什么样"，不是"调到极致"。 |
# 手写版 ①：初始化 4 个参数张量

## 💻 代码实现
```python
torch.manual_seed(42)
# requires_grad=True: 告诉 autograd“这个张量是参数，需要记录梯度”
# (2.0 / n_in) ** 0.5 是 He 初始化的标准差，专门给 ReLU 网络用
W1 = (torch.randn(784, 128) * (2.0 / 784) ** 0.5).requires_grad_()
b1 = torch.zeros(128, requires_grad=True)
W2 = (torch.randn(128, 10) * (2.0 / 128) ** 0.5).requires_grad_()
b2 = torch.zeros(10, requires_grad=True)
params = [W1, b1, W2, b2]
lr = 0.1  # 学习率：每次梯度下降迈多大一步
```

---

## 📝 核心知识点说明

> [!info] `requires_grad`
> 
> - 没这个标记，`loss.backward()` 算不出 `p.grad`。
>     
> - 这是张量“**是不是参数**”的标识。
>     

> [!tip] He 初始化
> 
> - `sqrt(2/n_in)` 是 ReLU 网络的经验值。
>     
> - 为什么是这个数字？后面“参数初始化”那节再讲。
>     

> [!warning] ⚠️ 写法陷阱  
> `randn(..., requires_grad=True) * scale` 会让 `* scale` 产生**新的非叶子张量**，导致训练时 `W1.grad` 始终是 `None`。  
> _(注：因此代码中采用先相乘，后调用 `.requires_grad_()` 的方式规避此陷阱)_。

# PyTorch 基础与细节梳理

## 一、 手写版 ①：初始化 4 个参数张量

```python
torch.manual_seed(42)

# requires_grad=True: 告诉 autograd“这个张量是参数，需要记录梯度”
# (2.0 / n_in) ** 0.5 是 He 初始化的标准差，专门给 ReLU 网络用
W1 = (torch.randn(784, 128) * (2.0 / 784) ** 0.5).requires_grad_()
b1 = torch.zeros(128, requires_grad=True)
W2 = (torch.randn(128, 10) * (2.0 / 128) ** 0.5).requires_grad_()
b2 = torch.zeros(10, requires_grad=True)

params = [W1, b1, W2, b2]
lr = 0.1  # 学习率：每次梯度下降迈多大一步
```
## 一、 手写版 ②：4 步循环就是训练的全部
```python
for epoch in range(5):
    for xb, yb in train_loader:
        x = xb.view(-1, 784)               # 拍平 (128, 1, 28, 28) -> (128, 784)
        # —— ① forward ——
        h = F.relu(x @ W1 + b1)            # 隐层：仿射 + ReLU
        logits = h @ W2 + b2               # 输出层：只做仿射，不加 softmax
        # —— ② loss ——
        loss = F.cross_entropy(logits, yb) # 内部自带 log_softmax + NLL
        # —— ③ backward ——
        loss.backward()                    # autograd 顺着前向图链式求导
        # —— ④ step ——
        with torch.no_grad():              # 参数更新不需要建图
            for p in params:
                p -= lr * p.grad           # 沿梯度反方向迈 lr 这么大一步
                p.grad.zero_()             # 清零，防止下个 batch 累加
```
## 二、 用 nn.Module 重写：同样的 4 步，更简洁
```python
class SimpleMLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(784, 128)     # ← 等价于手写版 W1, b1
        self.fc2 = nn.Linear(128, 10)      # ← 等价于手写版 W2, b2

    def forward(self, x):
        x = x.view(-1, 784)                # 拍平成(batch, 784)
        x = F.relu(self.fc1(x))            # 隐层 + ReLU
        return self.fc2(x)                 # 输出 logits (不如softmax, 原因同上)

model = SimpleMLP()
optimizer = optim.SGD(model.parameters(), lr=0.1)  # ← 内部就是手写版的 `p -= lr * p.grad`
loss_fn = nn.CrossEntropyLoss()                    # ← 等价于 F.cross_entropy

for epoch in range(5):
	model.train()                      # 进入"训练模式" (Dropout/BN) 行为切换; 这里没用到,但养成习惯 
	running_loss = 0.0
	n_samples = 0
    for xb, yb in train_loader:
        optimizer.zero_grad()          # ← 替代 `p.grad.zero_()`，一行清掉所有梯度
        logits = model(xb)             # ← ① forward ——
        loss = loss_fn(logits, yb)     # ← ② loss ——
        loss.backward()                # ← ③ backward ——（图底被截断补全）
        optimizer.step()               # ← ④ step ——（图底被截断补全）
        running_loss += loss.item() * yb.size(0)
        n_samples += yb.size(0)
        
    model.eval()                       # 进入"评估模式"
    correct = 0
    with torch.no_grad():
	    for xb, yb in test_loader:
		    correct += (model(xb).argmax(1) == yb).sum().item())
		    
	train_losses_v2.append(running_loss / n_samples)
	test_accs_v2.append(correct / len(test_set))
	print(f"epoch {epoch+1}/5  train_loss={train_losses_v2[-1]:.4f} train_acc={test_accs_v2[-1]:.4f}")
```
# PyTorch 进阶：API 封装与超参数解析
## 一、 对照表：PyTorch 替你打包了哪些东西
| 功能模块     | 手写版                                                                             | `nn.Module` 版                                    |
| :------- | :------------------------------------------------------------------------------ | :----------------------------------------------- |
| **参数声明** | `W1, b1, W2, b2 = ...`<br>手动写 4 个张量 + `requires_grad`                           | `self.fc1 = nn.Linear(784, 128)`<br>两行搞定 + 自动初始化 |
| **参数收集** | `params = [W1, b1, W2, b2]`                                                     | `model.parameters()`<br>自动扫描所有子模块                |
| **梯度清零** | `for p in params:`<br>`    p.grad.zero_()`                                      | `optimizer.zero_grad()`                          |
| **参数更新** | `with torch.no_grad():`<br>`    for p in params:`<br>`        p -= lr * p.grad` | `optimizer.step()`                               |
| **设备搬运** | 自己写 `.to(device)`<br>（每个张量都搬...）                                                | `model.to(device)`<br>一行搬完所有参数                   |
> [!important] 核心思想
> `nn.Module` 不是新东西——它只是把上面那段手写代码**打包成更顺手的 API**。背后的 4 步循环（前向、计算损失、反向传播、参数更新）**没变**。
