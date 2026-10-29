# AI 全栈与大模型个人知识库

这是一个以 **Obsidian** 为主组织方式的个人 AI 学习仓库。内容围绕 AI 全栈、大模型原理与应用开发持续整理，覆盖学习路线、基础编程、机器学习、深度学习、Agent、RAG、模型训练、经典论文、技术文章与电子书等方向。

仓库中的资料来自日常阅读与收集，包含微信公众号、X、技术社区、个人博客、网站及开源项目等渠道。部分文章保留了原文链接或作者信息；所有内容的版权归原作者所有，本仓库仅用于个人学习与知识整理。

> 本仓库本身就是一个 Obsidian Vault。下载或克隆后，请在 Obsidian 中打开**仓库根目录**，而不是只打开其中的 `LLM`、`Article` 等子目录。

## 内容概览

| 目录 | 内容 |
| --- | --- |
| `Article/` | 从公众号、技术社区、博客、X 等渠道整理的文章，主题包括 AI 编程、Agent 工程、RAG、代码阅读、开源项目学习和 AI 学习方法。 |
| `Full_Stack/` | 全栈学习入口，包含零到全栈路线及 Spring AI 相关 Canvas 内容。 |
| `LLM/1-Plan and Outline/` | AI 大模型学习路径、课程大纲、研发流程及数据结构与算法等规划资料。 |
| `LLM/2-Source/` | AI 全栈核心知识体系，覆盖 Git、Python、Linux、MySQL、机器学习、深度学习、Prompt Engineering、Agent、RAG、Multi-Agent、LangChain、LangGraph、模型训练、多模态和 Spring AI 等主题。 |
| `LLM/3-Thesis/` | AI 经典与新近论文，包括 Transformer、BERT、GPT、T5、ResNet、ViT、CLIP、LoRA、Qwen、GLM、DeepSeek 等。 |
| `LLM/4-Book/` | AI、机器学习、深度学习、数学、Python 及 Agent 相关电子书和学习手册。 |
| `LLM/Data analysis/` | 数据科学与业务分析资料。 |
| `image/` | Obsidian 统一图片附件目录。部分 Markdown 笔记依赖这里的图片，请勿随意移动或删除。 |
| `.obsidian/` | Obsidian 仓库配置，包括 Canvas、图谱、附件路径和阅读界面设置。 |

## 推荐阅读入口

初次进入仓库时，可以从以下内容开始：

1. `LLM/从零开始的AI学习之路.canvas`：AI 学习总览与知识地图。
2. `LLM/1-Plan and Outline/AI 大模型学习路径.canvas`：大模型学习路线。
3. `LLM/Karpathy_LLM_训练管线知识图谱.canvas`：大模型训练流程知识图谱。
4. `LLM/AI Concept.md`：AI 核心概念笔记。
5. `LLM/2-Source/`：按主题进入基础编程、机器学习、深度学习、Agent、RAG 与应用开发笔记。
6. `LLM/3-Thesis/Basic/`：从经典基础论文开始阅读，再进入 `LLM/3-Thesis/Advanced/`。
7. `Article/`：阅读 AI 工程实践、行业观察和技术方法类文章。

一个比较稳妥的学习顺序是：

```text
学习路线与知识地图
        ↓
编程基础：Git / Python / Linux / MySQL
        ↓
机器学习与深度学习基础
        ↓
Transformer 与大模型核心论文
        ↓
Prompt Engineering / RAG / Agent / Multi-Agent
        ↓
LangChain / LangGraph / Spring AI 等应用开发
        ↓
模型训练、微调、多模态与前沿论文
        ↓
项目实践、技术文章复盘与电子书查漏补缺
```

## 如何使用这个仓库

### 方式一：使用 Git 克隆（推荐）

先安装 [Git](https://git-scm.com/) 和 [Obsidian](https://obsidian.md/)，然后在终端中执行：

```bash
git clone https://github.com/yuyrrrrrrr/Personal_Knowledge_base.git
cd Personal_Knowledge_base
```

后续需要同步最新内容时，在仓库目录执行：

```bash
git pull --rebase
```

### 方式二：从 GitHub 下载 ZIP

1. 打开仓库主页：<https://github.com/yuyrrrrrrr/Personal_Knowledge_base>。
2. 点击绿色的 **Code** 按钮。
3. 选择 **Download ZIP**。
4. 下载完成后解压压缩包。
5. 记住解压后的仓库根目录位置。

不建议直接在 ZIP 压缩包内阅读，也不需要把仓库放在固定盘符；只要 Obsidian 能访问该文件夹即可。

### 使用 Obsidian 打开

1. 启动 Obsidian。
2. 点击欢迎页中的 **Open folder as vault**。
   - 如果已经打开其他仓库，也可以点击左下角仓库切换按钮，选择 **Open another vault**，再选择 **Open folder as vault**。
3. 选择克隆或解压后的 `Personal_Knowledge_base` **根目录**。
4. 如果 Obsidian 询问是否信任该仓库的作者，确认这是你从本仓库下载的内容后再允许打开。
5. 进入仓库后，按 `Ctrl + O` 打开快速切换面板，搜索 `从零开始的AI学习之路` 或 `AI 大模型学习路径`，即可打开知识地图。

目录选择示意：

```text
正确：Personal_Knowledge_base/
      ├── Article/
      ├── Full_Stack/
      ├── LLM/
      ├── image/
      └── .obsidian/

错误：Personal_Knowledge_base/LLM/
错误：Personal_Knowledge_base/Full_Stack/
```

只打开子目录会导致部分相对链接、附件和 Obsidian Canvas 无法正常显示，因此务必选择仓库根目录。

### Obsidian 使用技巧

- `Ctrl + O`：按文件名快速打开笔记。
- `Ctrl + Shift + F`：在整个仓库中搜索内容。
- 左侧文件列表：按目录浏览 Markdown、Canvas、PDF 等资料。
- 关系图谱和反向链接：查看笔记之间的关联。
- 双击 `.canvas` 文件：打开可视化知识地图。
- PDF 文件通常可在 Obsidian 内直接阅读；EPUB 等格式可根据需要安装插件或使用外部阅读器。
- 仓库配置将图片附件统一放在 `image/` 目录。新增笔记时建议继续使用该目录，以免图片链接失效。
- `.obsidian/community-plugins.json` 中记录了 `advanced-canvas` 插件。若 Obsidian 提示插件缺失，不影响普通 Markdown 和 Canvas 阅读，可按需在社区插件市场安装或忽略提示。

## 仓库结构

```text
Personal_Knowledge_base/
├── Article/                     # 收集与整理的文章
├── Full_Stack/                  # 全栈学习入口
├── LLM/
│   ├── 1-Plan and Outline/      # 学习路线、课程大纲与规划
│   ├── 2-Source/                # AI 全栈与算法知识笔记
│   ├── 3-Thesis/                # 基础与进阶论文
│   ├── 4-Book/                  # AI、数学与编程电子书
│   └── Data analysis/           # 数据分析资料
├── image/                       # 图片附件
├── .obsidian/                   # Obsidian 配置
├── Data_Base.base               # Obsidian Base 文件
├── MD语法.md                    # Markdown 语法笔记
└── README.md                    # 仓库说明
```

## 适合谁使用

- 希望系统学习 AI 全栈与大模型开发的学习者。
- 正在准备 AI 应用开发、Agent、RAG 或大模型相关项目的人。
- 想按主题查阅经典论文、技术文章和电子书的开发者。
- 希望使用 Obsidian 建立个人 AI 知识库的人。

## 维护与分享

- 新增 Markdown、Canvas、PDF 等资料时，建议放入对应主题目录。
- 文章中引用的图片建议统一保存到 `image/`。
- 引用外部文章时，尽量保留原标题、作者和原文链接。
- 本仓库是个人学习资料集合，不保证所有外部链接长期有效，也不构成商业使用授权。
- 若内容涉及版权问题，请优先联系原作者或仓库维护者处理。

## 致谢

感谢所有文章、论文、书籍、开源项目及其作者的公开分享。这个仓库的价值来自持续阅读、整理、实践与复盘，而不只是资料本身。
