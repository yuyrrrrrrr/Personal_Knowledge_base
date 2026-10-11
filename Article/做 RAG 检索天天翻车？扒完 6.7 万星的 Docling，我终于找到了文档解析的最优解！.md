2026-09-22 15:39
阅读 867
大家好，我是不会喷火的小火龙。

最近在自研知识库和 Agent 的过程中，我遇到了一个让我抓狂的问题：同样的 PDF 文档，同样的大模型，为什么用传统方式抽取后做 RAG 问答，大模型的回答经常是一本正经的胡说八道？

我反反复复换了好几个向量库，调了无数 Prompt，甚至升级了更贵的大模型。最后才发现，问题根本不在模型和检索算法上，而在最不起眼的第一步：文档解析。

如图 1 所示，这就是绝大多数 RAG 检索翻车的真实现场。

![image.png](https://pic.code-nav.cn/post_picture/1612112775822180354/eqCyjbvq1GHvhy46.webp)

Garbage In, Garbage Out。搞不定文档解析的"第一公里"，无论换什么顶级大模型，你的 RAG 永远在吃垃圾。

今天这篇文章，来深度拆解 GitHub 上 6.7 万 Star、IBM Research 开源的文档解析神器 Docling，讲清楚三件事：传统 PDF 抽取为什么必然翻车、Docling 的轻量小模型如何在 CPU 上破局、以及你的项目到底该选哪个方案。

---

## 一、传统 PDF 抽取做 RAG，为什么是一场灾难？

先说一个很多人没意识到的事实：PDF 是一种"打印渲染格式"，它存储的是"这个字符画在屏幕 (x, y) 坐标的什么位置"，而不是"这段话属于哪个章节、这个表格有几行几列"。

PDF 天然丢弃了逻辑结构。传统的纯文本抽取工具（如 PyPDF、pdfplumber），本质上是在用物理坐标硬猜语义。

这会导致三个致命的翻车硬伤。

第一，双栏混排串行。学术论文、研究报告大量使用左右两栏排版。传统工具按物理 Y 轴从上到下读取，会把左栏第 3 行和右栏第 3 行拼成一句话，语义完全颠倒。大模型拿到的上下文从头到尾就是错的。

第二，复杂表格粉碎性骨折。这是公认的重灾区。多行合并单元格、无框线表格被传统工具拍扁成一行字符串，行列对齐关系彻底丢失。你问"2026 年 Q3 营收是多少"，模型把 Q2 的数字回答给你，因为它根本分不清哪行对应哪列。

如下表所示，在面对合并单元格和复杂表格时，两种方式的差距触目惊心：

**传统文本抽取 vs 结构化提取在复杂表格下的表现对比**

|对比维度|传统纯文本抽取（PyPDF 等）|Docling 结构化提取|
|:--|:--|:--|
|双栏论文|左右栏串行拼接，语义错乱|按真实阅读顺序重组，段落完整|
|合并单元格表格|单元格边界丢失，行列全部错位|准确重建行列拓扑关系，输出干净 Markdown 表格|
|无框线表格|完全无法识别表格结构，输出纯散文|通过 TableFormer 模型识别隐含表格边界|
|跨页表格|表格在页面断裂处截断为两段无关文本|智能拼接跨页内容，保持表格完整|
|公式与代码|公式变为乱码符号串|识别公式区域并保留原始格式|

第三，机械切片破坏 AST。即便你用了稍好的工具提取出了还算干净的文本，后面的分块环节同样致命。主流 RAG 框架默认按 500 或 1000 个字符盲切，完全不管你切在了一个段落中间、还是一个表格的第三行。检索回来的片段残缺不全，大模型只能基于半截话去回答。

---

## 二、扒开 Docling 源码：它是如何用轻量小模型破局的？

Docling 是 IBM Research 开源的文档解析框架，采用宽松的 MIT 协议，GitHub Star 已突破 6.7 万。

它的工程哲学和很多人预期的不一样：IBM 没有盲目依赖几十亿参数的重型视觉大模型（那意味着动辄 16G 以上显存和极慢的推理速度），而是选择了一条更克制的路线，用专门优化的轻量小模型，各自解决一个特定的工程难题。

如图 2 所示，Docling 的核心在于其分层解耦的轻量多模型流水线：

**图 2：传统文本提取流水线 vs Docling 结构化多模态解析流水线**

![image.png](https://pic.code-nav.cn/post_picture/1612112775822180354/OWud1YLSMMXhDovU.webp)

三大底层支柱：

DocLayNet 版面语义识别。IBM Research 基于大规模人工标注文档数据集训练的版面分析模型，精准区分正文、标题、双栏排版、图片注释和页眉页脚，并还原正确的人类阅读顺序。双栏论文不再串行拼接，因为模型知道应该先读完左栏再读右栏。

TableFormer 表格结构识别。专门针对表格场景的 [Transformer](https://www.mianshiya.com/bank/1821834692534505473) 小模型，输入是表格区域的图像，输出是每个单元格的行列拓扑坐标。合并单元格、无框线表格、跨页表格都能准确还原为干净的 Markdown 或 HTML 表格。

DoclingDocument 统一中间抽象。Docling 把 PDF、DOCX、PPTX、HTML 等多源异构文档统一解析为一棵结构化的文档 AST 语法树（DoclingDocument），向下游导出时可以无损转换为 Markdown、JSON、DocTags 等多种格式。

IBM 技术报告（[arXiv:2408.09869](https://arxiv.org/abs/2408.09869)）中的原话：

> "powered by state-of-the-art specialized AI models for layout analysis (DocLayNet) and table structure recognition (TableFormer), and runs efficiently on commodity hardware in a small resource budget."

在普通硬件上、以极小的资源开销高效运行。

![image.png](https://pic.code-nav.cn/post_picture/1612112775822180354/itwhiZdOpSDRo7xI.webp)

---

## 三、RAG 进阶利器：丢掉机械字符切片，拥抱 HybridChunker

搞定了文档结构化转换，还有一道关卡：切片。

传统 RAG 框架的 RecursiveCharacterTextSplitter 按固定字符数（500/1000）盲切文本，完全不管你切在了一个段落中间还是一个表格的第三行。前面辛辛苦苦还原出的排版结构，在切片环节又被摧毁了。

如图 4 所示，传统固定字符切片和 HybridChunker 语法树智能分块的差距一目了然：

**图 4：传统固定字符切片 vs HybridChunker 语法树智能分块**

![image.png](https://pic.code-nav.cn/post_picture/1612112775822180354/H7yQgURC7UOa9ofe.webp)

Docling 原生内置的 HybridChunker 基于前一步生成的 DoclingDocument AST 语法树切分，感知 Markdown 的标题层级、段落边界和完整表格，绝不在表格单元格中间截断，小段落自动合并到上一个分块，超长段落按句子边界自然截断。

核心代码只需要几行：

```python
from docling.document_converter import DocumentConverter
from docling.chunking import HybridChunker

# 第 1 步：解析 PDF 为结构化文档
converter = DocumentConverter()
result = converter.convert("financial_report.pdf")

# 第 2 步：基于 AST 智能分块
chunker = HybridChunker(tokenizer="BAAI/bge-small-en-v1.5")
chunks = list(chunker.chunk(result.document))

for i, chunk in enumerate(chunks[:3]):
    print(f"--- Chunk {i} ---")
    print(chunk.text[:200])
```

---

## 四、本地轻量闭环实测：Docling + Ollama + SQLite

一套高精度的文档问答系统，完全不需要依赖昂贵的云端 API 或重型 GPU。

技术栈非常简单：

1）文档解析：Docling 本地 CPU 运行，解析 PDF/DOCX/PPTX 输出结构化 Markdown； 2）向量嵌入：本地 Ollama 驱动轻量 `nomic-embed-text` 模型（仅 274MB），无需调用任何外部 API； 3）向量存储：单文件、零依赖的 SQLite 存储，无需部署任何数据库服务。

整个技术栈在一台普通笔记本上即可跑通，不依赖网络、不发送数据到第三方。

我选取了 IBM 官方发布的《Docling Technical Report》学术论文（共 9 页，含双栏混排、多级标题和跨页合并表格），以同一个检索问题进行对决： _Query: "What are the specialized AI models used in Docling for layout analysis and table recognition?"_（Docling 用于版面分析和表格识别的专用模型分别是什么？）

控制台输出的真实对比数据如下：

![image.png](https://pic.code-nav.cn/post_picture/1612112775822180354/Vdycn9CoqgRa4A5n.webp)

不仅是指标差距，翻开两边召回的具体内容，差距更明显：

**传统 PyPDF 召回的 Top 1 切片：**

```text
psearch-experience, our cloud-native service for knowledge
exploration tasks.
Layout Analysis Model
Our layout analysis model is an object-detector which predicts the bounding-boxes and classes of
various elements on the image of a given page. Its ar...
```

前两行直接把上一栏截断的半句话 `psearch-experience...` 拼了进来，缺少章节归属，典型的上下文污染。

**Docling + HybridChunker 召回的 Top 1 切片：**

```text
[标题路径: 3.2 AI models]
As part of Docling, we initially release two highly capable AI models to the open-source community, which have been developed and published recently by our team. The first model is a layout analysis model, an accurate object-detector for page element...
```

不仅自带 `[标题路径: 3.2 AI models]` 层级标签，而且首句完整交代了两个核心模型的出处，相似度直接飙到 0.8595。

在纯 CPU 环境下，9 页复杂双栏论文用时 38.921 秒，切片数量从 109 个压缩到 49 个（降噪 55%），彻底消除了表格截断和句子跨栏错乱。

---

## 五、横评与选型指南：Docling、MinerU、MarkItDown 怎么选？

开源文档解析赛道目前三大主流方案各有所长。选错了，要么精度不够，要么成本爆炸，要么商用受限。

我把市面上主流工具的选型逻辑整理成了一张清晰的决策树，如图 6 所示：

**图 6：文档解析与 RAG 预处理技术选型决策树**

![image.png](https://pic.code-nav.cn/post_picture/1612112775822180354/JKfZAXtkXt3DW3vi.webp)

三个方案的核心取舍：

Docling（IBM Research）：MIT 协议，企业商用零法律风险。纯 CPU 可跑，TableFormer 专攻复杂表格，HybridChunker 原生支持 AST 智能分块，自带 MCP Server 可直接让 Cursor、Claude Code 等 Agent 调用。适合 90% 的个人开发者和企业 RAG 场景。

MinerU（上海 AI Lab）：在学术论文和数学公式 LaTeX 还原上精度极高，对中文复杂排版的支持也很强。但动辄需要 16G+ 显存的 GPU 支持，且采用 AGPL-3.0 协议，商业使用限制较多。适合科研机构和不差 GPU 算力的团队。

MarkItDown（微软）：超轻量的多格式转 Markdown 工具，安装简单、速度快。但缺乏深度的视觉版面分析能力，对双栏排版和复杂表格基本无能为力。适合文档格式极简单、只需文本级转换的场景。

---

## 结语

AI 应用的上限，往往不取决于你换了多大、多贵的模型，而取决于你在最前面喂给模型的数据有多干净、多结构化。

Docling 用两个轻量小模型解决了困扰无数开发者的文档解析难题：它没有花哨的概念，只有对工程问题的诚实面对和克制回答。希望这篇文章能帮你在自研 RAG 和 Agent 的路上少走一段弯路。