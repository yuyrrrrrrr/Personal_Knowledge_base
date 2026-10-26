编辑 | 姜篇

> 菲利克斯·里泽贝格：如果我们只让AI“帮我总结这封邮件”，那就没有真正用到新一代模型的智能。

> 菲利克斯·里泽贝格：我只是Claude的传送带。

> 菲利克斯·里泽贝格：把你最后想得到的结果，直接作为任务交给模型。

很多开发者已经把Claude Code放进日常工作，却仍然守在每一个步骤中间。

发现一条崩溃记录，复制给Claude；Claude修完代码，人再去找下一条；一个会话给出方案，再由人把结果搬到另一个会话里审查。模型确实干了活，开发者却忙着分发任务、转交上下文和收集结果。

菲利克斯·里泽贝格把这种状态称为“Claude的传送带”。

模型能够读取仓库、调用工具并持续处理一组问题，人却还沿用早期聊天机器人的方式，一次只发一条小指令。Agent能力提高以后，这套工作流反而把人留在了最机械的位置上。

备注：菲利克斯曾负责Claude.ai、Cowork和Claude Code Desktop的工程工作。他接受Silicon Valley Girl采访，谈了自己现在怎样使用Claude、如何检查模型那些听起来很有把握的错误，以及开发者怎样逐步把更完整的任务交出去。

这场访谈给出的建议很简单：少替Agent搬东西，多设计它可以独立完成的闭环；别用一句“你是专家”假装给足了上下文；权限可以逐步开放，验收证据必须留在人和外部工具手里。

**以下为访谈内容，我们进行了翻译与整理。**

![图片](https://mmbiz.qpic.cn/sz_mmbiz_gif/Zhxqo7xEfgLES5z1iblEB06Z21Ozax6cgYOYicIezBs73ibIuGTFkDKaHAeAINk3FgxgpTBHiboItkd94ez9DfCzhbGUbIz4ic0icIQqEfn78Dvlo/640?wx_fmt=gif&from=appmsg)

_菲利克斯表示，用户面前已经有能力很强的模型，实际使用方式却远远没有跟上_

## 给Claude的任务，可能早就小于它的能力

菲利克斯举了一个例子：如果手里有一个能力很强的模型，却只问“法国的首都是哪里”，那几乎没有碰到它的能力边界。

> 菲利克斯·里泽贝格：模型能力与用户实际用法之间，确实存在很大的落差。

> 菲利克斯·里泽贝格：我们对这些模型的使用，才刚刚触到表面。

这种落差在编程里很常见。

开发者让Agent补一个函数、解释一段报错、把JavaScript改成TypeScript。这些任务当然有用，但它们只占软件工作的一个小片段。

如果人把这条链拆成七条Prompt，再负责搬运每一步的输出，Claude只是写得更快的执行者。开发者没有减少多少协调工作。

菲利克斯建议开发者们先问自己为什么要做眼前这一步，下一步希望发生什么，再把那个结果交给模型。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_gif/Zhxqo7xEfgLXIuMbATvIBCvf4OowHxTWlsu1oWJRLkeJjDBQrrEsh32BALiawRP7ywuPia5nJsumLI7OHdydhz0qicz2MVAXfQGnkYjic2oI1pk/640?wx_fmt=gif&from=appmsg)

_菲利克斯建议继续追问眼前任务要达成什么结果，再把更高一层的目标交给Claude_

## 一条崩溃记录，把工程师变成了传送带

“人工传送带”，菲利克斯这样描述自己的工作。

一年半前，他处理软件崩溃时，会先去系统里找到一条记录，然后再把它交给Claude修复。做完以后，继续挑下一条，重复同样的动作。

> 菲利克斯·里泽贝格：我先去查看崩溃记录，挑出一条，搬过来放到Claude面前，再对它说：“请修复这个问题。”我很快意识到，自己只是Claude的传送带。

他后来改变了流程。Claude不再只收到某一条崩溃记录，而是能够访问完整的崩溃数据，自行判断哪些问题值得修、哪些不需要处理。

> 菲利克斯·里泽贝格：Claude应该访问全部崩溃数据，再由它自己判断哪些需要修复，哪些不需要。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_gif/Zhxqo7xEfgLFwBYBxezv1W0w6jCViaV4KZHDMCv30iaOWcddOPQguAQbJibp2YnJq0QBTaaibNlVD7wj1DUdoGswK5wKpc5kmZA0icosWSQJibjPE/640?wx_fmt=gif&from=appmsg)

_菲利克斯回忆，自己曾不断把单条崩溃记录搬给Claude，后来才发现人已经成了流程中的传送带_

![图片](https://mmbiz.qpic.cn/mmbiz_gif/Zhxqo7xEfgJElfXIA4FHNicfAPIWkRTvaibib9h6Uicp4eiaysteeQYRHscdFjgqYtvhQbodalBv8oCBsEjsnpsVrsKAicYdGvWGIWheWJ66iblfjg/640?wx_fmt=gif&from=appmsg)

_更高一层的任务，不是“修这一条”，而是让Claude读取完整崩溃数据，自行决定哪些问题值得修_

这里不能简单理解为“把生产系统全部交给Claude”。

要让Agent接住整段任务，团队需要先补齐数据入口、工具权限、测试环境、停止条件和结果记录。前期搭建会花时间，省掉的是此后反复出现的人工分发。

同样的变化也适用于常见维护工作。

![图片](https://mmbiz.qpic.cn/mmbiz_png/Zhxqo7xEfgLT1aCQBtKGhWhAD6Nbib9q61yQ3reoPjGMMTT0Duh2j37uZU4eMIJzMgpggtm75tpo2nibsicheHoM0NbJicjeJS6nxnY2icicfl70Y/640?wx_fmt=png&from=appmsg)

_逐步搬运让开发者卡在每次调用之间；目标、工具和验收条件齐全后，Agent才能形成可检查的任务闭环_

## “你是一位专家”，只给Claude换了一身衣服

早期Prompt教程很喜欢先分配角色：“你是一位世界级工程师”“你是一位资深数据科学家”。菲利克斯现在很少这么写。

> 菲利克斯·里泽贝格：我从来不会对Claude说：“你是一位优秀的某某专家。”

问题不在礼貌或措辞。只让模型“扮演专家”，很容易得到专业术语和相应口吻，未必得到专家处理问题的方法。

> 菲利克斯·里泽贝格：我们需要的是专业人士会使用的技术、工具和知识，不只是那套听起来专业的词汇。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_gif/Zhxqo7xEfgIZRN5so0HdvLLMiabMLFcpodm2Fic9JdS0E2KdDrFMJ3Q7vcGYGiaribxib5L1Pn993vIEMKhFt8NXOxDFsf76FUfwkbNtxSBaicLF8/640?wx_fmt=gif&from=appmsg)

_菲利克斯认为，角色提示容易让模型进入表面化的角色扮演；真正有用的是专业人士采用的工具和流程_

放到代码任务里，差别很明显。

当你给出指令：“你是一位资深后端工程师，请优化查询”以后，仍然缺少数据库规模、慢查询日志、延迟目标、索引约束和回滚要求。

换成“读取执行计划和监控数据，确认P95延迟来源；允许新增索引，不修改接口返回；给出压测结果和回滚SQL”，Claude才拿到了专业工作所需的材料。

## Claude可以干更多，同一个会话不能自己证明自己

把任务交得更完整，最容易引出另一个担心：Claude出错怎么办？

菲利克斯的答案没有停在“人工复核”。他会把生成、攻击、裁决拆开，让不同会话承担不同位置。

一份方案由一个Claude完成，再启动多个会话寻找事实错误、遗漏条件和反例；审查结果还可以交给另一个“裁判”会话判断是否成立。有效反馈再回到原会话修改。

> 菲利克斯·里泽贝格：这些会话的任务只有一个：攻击这份结果，证明它哪里错了。

> 菲利克斯·里泽贝格：我很少让当前会话自己评价自己做得怎么样。

![图片](https://mmbiz.qpic.cn/mmbiz_gif/Zhxqo7xEfgIicMW0575Y4azsQzCD0mJ5QaiaTJhOmJyQWcibwKOvQ6XScIOBn9Bhicdn0pMYkBokq7jLxwfwh7PTv50AgPQ98IGI2pYtR7MQYlg/640?wx_fmt=gif&from=appmsg)

_菲利克斯表示，当前会话往往不适合判断自己的产出是否合格，应加入外部信号或独立会话_

多开几个Claude并不等于验收完成。模型可能共享相似盲点，也可能被同一份错误上下文带偏。菲利克斯仍然优先寻找“硬的外部证据”。

> 菲利克斯·里泽贝格：我更希望找到硬性的外部证据，判断结果究竟有效还是无效。

不敢放手时，先让人和Claude并行工作

主持人提到，所有Agent输出都要经过团队，最后还会回到她手里。工具越多，她越像公司里最大的瓶颈。

菲利克斯没有建议她第二天就取消审批。他给了一条更稳妥的迁移路径：先并行运行。

> 菲利克斯·里泽贝格：先让人工流程和Claude并行跑一段时间。

开发者照常审一份文档、一次代码变更或一通客户电话，同时让Claude独立给出反馈。连续比较几轮，记录两边意见相同和不同的地方，再把反复出现的开发者判断整理成规则。

> 菲利克斯·里泽贝格：看看Claude会给出什么反馈，哪些地方与人不同，哪些地方一致。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_gif/Zhxqo7xEfgLbH7VU6bia4UYmZSdSgklnO7ibNNn4BHaaWHmFBO60qsBWgRS5xf4DJLrz9Id9QJQZFSugLuoraeUTGWiaLC5golLP2PxD9nDUyY/640?wx_fmt=gif&from=appmsg)

_菲利克斯建议在交出审批权之前，先让Claude与现有人工流程并行运行，通过差异逐步校准工作流_

这种方式更容易落地。团队可以给Agent准备一批历史Issue，让它在不影响生产的环境里独立处理；比较定位结果、修改范围和测试覆盖，再决定能否从建议模式进入自动提交模式。

权限也可以分级开放，这样Agent获得的是经过验证的行动范围，不是一张无限权限的通行证。

## 仅仅是记住React API，已经很难证明一名工程师的价值

当Claude能写代码、读工具和组合系统，软件工程师的评价标准也会变化。

菲利克斯说，工程师正在经历一场身份危机：价值是否还来自记住React的全部API？他的答案很明确，记忆某项接口的价值正在下降。

> 菲利克斯·里泽贝格：我一直用工程师产生的实际影响来评价他们。

> 菲利克斯·里泽贝格：仍然有价值的，是用有意思的方式把不同系统组合起来。

![图片](https://mmbiz.qpic.cn/mmbiz_gif/Zhxqo7xEfgLyGzaoxcecfOiblk94icZODOqBTwWx5jCK9hgXibUypXFGSVvOJoWW7CCqSQe84picRDOqvM12mHO5QBWtQVIMRQH8QZlvuiapfHaA/640?wx_fmt=gif&from=appmsg)

_漂亮的工程实现如果没有给用户带来收益，价值仍然有限；工程师应以最终影响衡量工作  
_

_许多人认为以后只要会写Prompt就可以，这种想法是错的。_

_把支付、库存、消息队列和风控系统接在一起，开发者仍要理解数据怎样流动、失败怎样扩散、权限在哪一层收口。AI降低了实现成本，也放大了组合错误可能造成的影响。_

对刚入行的开发者，菲利克斯给出的建议也很朴素：去做真实项目。

> 菲利克斯·里泽贝格：去做一些真实的东西，证明你能把它完成。

作品集不应只剩一个漂亮Demo。能否找到真实需求、和用户沟通、限定Agent权限、检查结果并把功能稳定交付，这些过程更能说明一个人是否会做软件。

视频发布后，一位开发者写下了把这两年的工作流变化。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/Zhxqo7xEfgKK9aicNVQ1yLXuINUjOPjJyDX9kEW12ibOyHaZWPy2yiazqVTSDtIuOeazxvlKoTfYEhVp2ZzqKWYBdf1iakm15Qdgr3cz9w3MsPw/640?wx_fmt=png&from=appmsg)

## 写在最后

菲利克斯没有要求开发者退出工作流。他想取代的是的是那部分没有判断、只有转交的工作。

工程师继续负责选择目标、划定权限、设计反馈回路和决定什么结果可以上线。Agent负责读取材料、调用工具、执行任务和处理大量重复检查。两者之间如果仍靠人逐条复制，AI再快，整条链路也快不起来。

团队可以从一项高频、可回滚的维护任务开始：把历史数据、工具入口和验收条件准备好；让Claude与人工流程并行运行；比较结果；补齐测试与日志；确认稳定以后，再取消中间那次机械转交。

开发者不必急着把键盘完全交出去。先把自己从传送带上拿下来。

参考链接：

https://www.youtube.com/watch?v=D-SVFneJ_Nk