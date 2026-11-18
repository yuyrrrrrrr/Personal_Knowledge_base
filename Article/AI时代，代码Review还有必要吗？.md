上海QEcon中，有一个热门的话题：AI时代，还有必要CR吗？这里谈谈一个一线开发思考，供参考。
# 01

一线同学 真实的CR现状
一个需求，AI 一分钟 写了几百行代码，告诉我写完了。
OK，我瞅瞅，我盯着他写的代码，陷入了沉思，心想：**这什么玩意？**   
![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/ZRhjO8xAWr7HMhYHhXXzRxvN2CMLicySp0uLjibdHW6wHqjneddq4FcODnNGGAev4goPfec7bCD3Reysv3ficshGzwBBWeUZNjzwNSg6EUoctI/640?wx_fmt=png&from=appmsg&tp=wxpic&wxfrom=5&wx_lazy=1#imgIndex=3)
看了**半个小时**后，貌似看懂了AI写的什么了。于是乎，我在群里at了大伙，一起帮忙看看…
这种场景已成了日常。每天我要CR别人的代码 ，别人也要CR我的代码。
![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/ZRhjO8xAWr6bSBClCx5a5PqjRib3NHse96q9AvvxGQh21ycymS6bXe0mYM8iaaPgE5ZIpXSnbrHGmkWekiaqGuIA1DIa0IicpXHt7p0GgBCZJ7M/640?wx_fmt=png&from=appmsg&tp=wxpic&wxfrom=5&wx_lazy=1#imgIndex=4)
大家都在猜AI写了什么？一个字：**累**。
AI在写代码上**速度优势**，在CR的环节统统**还了回去**！
体感就是：**AI来了后，更累了 更慢了！**
   ****1.1 信任危机 与 旧的生产关系****
”猜“代码的背后，有一个更加本质的问题：**信任感在慢慢瓦解**。
传统的CR建立在人与人的**协同信任**上，有时CR可以闭眼通过，为什么？因为我信任**这个人**！
但AI入场后，这个信息链断裂了，**人与人之间夹了一个AI（一个概率模型）**。
在信任上叠加一个概率，这听起来也太扯淡了。

CR困难也揭露出了一个更深层次的矛盾：

> 旧的生产关系，已经容纳不下新时代下AI的生产力

旧的分工模式、各种SOP、信任机制、考核机制…，这些**非技术的元素**如何适配AI是一个更加需要思考的问题。

   **1.2 CR稀释了我的注意力**

卡尔・纽波特在《深度工作》中提出的观点：

> 知识经济时代，**深度专注的认知能力是最稀缺、最不可替代的核心生产资料**

从这个角度看，CR AI的代码 实际上就是在抢夺我们的**宝贵注意力**。

当**注意力资源**已经cover不了AI产生信息的速度时，大脑就宕机了。

针对这个问题《代码整洁之道》的作者比较极端，他在2026年7月23上公开表示：

> **他不再看AI写的任何代码，唯有如此，我才能发挥它的生产力。**

这句话后面还跟着另一句话：

> **取而代之的做法，是用严苛的约束把这些智能体包裹起来：单元测试、Gherkin 验收测试、QA 流程、质量指标、变异测试、测试覆盖率，以及许许多多其他手段。**

他给CR指明了一条路：**用测试手段 确保代码的正确**。
# 02

100%的测试，存在吗？

按这个思路走，有一个绕不开的问题，即：

> **如何构建100%的测试用例？**

但遗憾的是，这个问题早有了结论（可参考 图灵停机问题、Rice定理）：

**对于任意图灵完备的程序，不存在一组测试用例，能够完备地证明该程序不存在任何缺陷。**

那，工程上可以达到多少呢？

精耕细作的话，可以做到**80%-90%** 的覆盖。

剩余的10%-20%，用其他方式补偿，如下图：
![图片](https://mmbiz.qpic.cn/mmbiz_png/ZRhjO8xAWr5zK468LBJFNFHtc8icKfblW9G6vdRDMLLyFlaoMovUdqg4icRVZCCwBzklnwtqYlkkNjP6PqQeRX3wK0dNRAIP3Kba1SxAdHNlQ/640?wx_fmt=png&from=appmsg&tp=wxpic&wxfrom=5&wx_lazy=1#imgIndex=5)


对于测试，我们也需要用更加立体的角度去看：

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/ZRhjO8xAWr4hcX04WQGy6IZjwuFF9ibPUibON1hfCZVTj0nqqcrxqh7MkniaM8shVdCdSN1HEWIibjyT9DKCyEBGSZrnRwnuQpOOA919PPu5mts/640?wx_fmt=png&from=appmsg&tp=wxpic&wxfrom=5&wx_lazy=1#imgIndex=6)

  
   **2.1 方法10年前就有了，AI时代要怎么用？**

以上的方法，并不是AI时代特有的产物，之前就已经很成熟了。AI时代这些理念 并没有改变。

这里我们需要思考的是：AI和这些方法如何结合起来？

而不是下面的场景：
![图片](https://mmbiz.qpic.cn/mmbiz_png/ZRhjO8xAWr5wQHXT0anmO1kn5ooyaiclZKftOroQKDic5FN0RH6N5KNjCJYH7pSjjWmyO0bZVNugiavLXE8VxK56OGW4rqJjFaJnVibHXpLVjVQ/640?wx_fmt=png&from=appmsg&tp=wxpic&wxfrom=5&wx_lazy=1#imgIndex=7)

简单的一句话，给我生成测试用例，这样的测试基本是自己骗自己。

结果就是AI通过一个错误的代码产生错误的测试用例，出现问题后，再次让AI反复写代码，无限循环这个过程。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/ZRhjO8xAWr7hEtfibq0xL47hIfThleApne7E1iaAAIC1WIyNs7WVew4QKNAgrxudISRtSMbicJ7rHS1FkibcG4Teh0zibgdvXqQMbsqButeP7WxY/640?wx_fmt=png&from=appmsg&tp=wxpic&wxfrom=5&wx_lazy=1#imgIndex=8)

这里很容易想到了，把多余的测试合并并提前，这不就是TDD的核心理念。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/ZRhjO8xAWr5G2yWcyw03q2HM6u2zWgiaPlJZcVicSv3FiaickXq0oibBUsNy6Lx9z9dLbwM6XxkIUXwAPFiaEn8I9Zs1OTTSDIKOLmVMB9YOJZ4jM/640?wx_fmt=png&from=appmsg&tp=wxpic&wxfrom=5&wx_lazy=1#imgIndex=9)


好，现在我们推导出了，测试要左移，但是要具体怎么去写测试用例呢？有没有一个相对可操作的方法。

   **2.2 从 信息论 的视角看测试**

从信息论的视角看软件测试，软件测试可以被定义为**信息捕获的过程**：

一个没有测试的代码，实际上是一个高度不确定的状态（高熵），每增加一次测试，实际上是一次熵减。

但是在实践过程中，我们在写测试用例的时候，往往还是直接通过理解需求去写，这个中间貌似少了一些结构化的方法能体系的输出测试用例，这是什么呢？

我想是：**建模**。

建模把模糊的需求结构化，让我们可以通过结构化的方法写测试用例。

![图片](https://mmbiz.qpic.cn/mmbiz_png/ZRhjO8xAWr5tvVy2mh7zACFsauT7DrhMTSczebeOMOWlglGoo57BLm0Kqic4UdTpZibooCX6NKTVCia119bEyrxkFMHLg3DQKC0U3HhGV1ibVLI/640?wx_fmt=png&from=appmsg&tp=wxpic&wxfrom=5&wx_lazy=1#imgIndex=10)


在自然语言描述的需求当中 ，只说清楚了 系统要做什么？大量的结构信息、协助、时序、数据、状态信息实际上都是空的，实际上从信息论的角度看，建模的本质就是在可控的补全这个过程。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/ZRhjO8xAWr4t01jnhwZuM45cOAUA7AEUrIloQVMZiaYlhicDjCictV1ibCAmCNKWkvSibLghjtJzicN7gsT3tDdbIuDicOPWGtianRz4VIB1vibGf2yc/640?wx_fmt=png&from=appmsg&tp=wxpic&wxfrom=5&wx_lazy=1#imgIndex=11)


通过类图和序列图，去构建对应的测试用例：


![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/ZRhjO8xAWr4KN4ue1hz14ZUfWyZxr6p3laRnaebicEw0xuUdkiamKicu8SCMAlpx9Zv6cIzlasMmILgb75skWg2zS2xwhvd3jia0TY7lBTfcQoQ/640?wx_fmt=png&from=appmsg&tp=wxpic&wxfrom=5&wx_lazy=1#imgIndex=12)


当我们构建完了测试用例，实际上也为AI验证代码补全了反馈信号，写代码的Loop自然而然构建成功，真正做到了，AI自己跑、自己验证。
![图片](https://mmbiz.qpic.cn/mmbiz_png/ZRhjO8xAWr4hhuB8ZFfoepj5D5kUHHJ1gibSVD7mibL6JjDeRYXiaYCvUHndXsKHqicjSQicrpNMkU7tIzgNjLZ1XhuOC2pRGkyZy7NvjI73lTrw/640?wx_fmt=png&from=appmsg&tp=wxpic&wxfrom=5&wx_lazy=1#imgIndex=13)

以上的方法，一句话概括就是：**我们通过建模的手段去构建测试用例，尽一切可能把测试左移动，去构建AI从写代码到自我验证的Loop。**

# 03

向内看：关注设计

但，光有测试就够了吗？远远不够！

即使一段代码功能上完全**符合预期**，测试也都可以通过。

但人可能完全**读不懂**，AI产生的负债让代码越来越难维护，这次可以，但是到那一天，线上就炸了。

![图片](https://mmbiz.qpic.cn/mmbiz_png/ZRhjO8xAWr5TicJrykV87BpLjrSk3FgvJsEiaPfIN5V4ibMh5nsZqxdDmcFooUDlj4Bp4qsU8HKns7reQFyqEHm3vGCjeXHMWYbFTicbXVQmLkw/640?wx_fmt=png&from=appmsg&tp=wxpic&wxfrom=5&wx_lazy=1#imgIndex=14)

所以长远考虑还是要 **向内看**。
   **3.1 为什么CR别人的代码很难？**

首先我们要问自己，为什么CR别人的代码很难？
本质上因为我不知道这段代码**做了什么事？因为什么？背景是什么？**

所以实际上，真实的CR代码的过程就是在不管的问人问题，你为啥这样写…

而这个过程，就是就是在**理解需求。**

我们会发现，实际的思考链路如下：

![图片](https://mmbiz.qpic.cn/mmbiz_png/ZRhjO8xAWr7eibsNMNvq0msP5gDKrhTsFQFATsUBNL5k9TQacYHiaG0ONLvS6Q9ZcNUgT4dMNn004Kxaal8DNlFMZuniaqjTolc5GzBozic1ZAE/640?wx_fmt=png&from=appmsg&tp=wxpic&wxfrom=5&wx_lazy=1#imgIndex=15)

到最后，会CR实际上是一个需求推导的游戏，这个游戏的逻辑，和写代码的逻辑正好相反。

写代码：实际上是正向推导，从需求出发，一步一步地向**后**推演。

CR代码：实际是回答这个代码是从什么地方来的，一步一步地向**前**推演。

所以，CR的过程，就是在构建这个思维链。

最后，我们会发现业务的逻辑，都需要从需求中得到印证。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/ZRhjO8xAWr5habORNXjZ7dAQ8xsccERxrhQChoricI8kVbqUO4icCcf7RfdYopD58rRev6KfUv15rUba4Y1KN7K98ZFFHKB86Kxj13icJNCg88/640?wx_fmt=png&from=appmsg&tp=wxpic&wxfrom=5&wx_lazy=1#imgIndex=16)

另一个角度，为什么CR很难？

**因为代码是线性的，缺失了架构信息。**

这就意味这，一段代码的diff，人想要理解，一定要从一个起点开始看，并且要知道改动局部和全局的关系？从这个层面讲，理解代码最好的方式，就是理解代码背后的那个图，以及**验证代码和建模**的一致性。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/ZRhjO8xAWr4WiaOv83t2JDWj2hpdfMgKB95aDEEOL77G3egNd9Ca8w4h2ZJGjonlq0UjD6PG07iaKyic1WWQGOibSk3TIeyE7GXQuUehHFxA5G0/640?wx_fmt=png&from=appmsg&tp=wxpic&wxfrom=5&wx_lazy=1#imgIndex=17)

所以核心的问题又回到了**建模**上。

   **3.2 AI与人的分工**

讲到这里，我们会发现：
![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/ZRhjO8xAWr7gfOoFE9qndBHEwTXOvE4aR2SE9X7Hnc7FUicibvyxSnurUob8icQFkyNqo2KKicLFw5AtYhsCItdWJYicZJ1ibkWfLGI0U45T2zAok/640?wx_fmt=png&from=appmsg&tp=wxpic&wxfrom=5&wx_lazy=1#imgIndex=18)

结合AICR，我们就有了明确的倾向性，如下图：
![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/ZRhjO8xAWr4jNvdhRWLQ1TPoKRgZomhvyiaHicNhcKUPw4QJLTHvSN9cPuFlB7hQ4alRFF5UF13cnD6k83qbvZ0CltsKlkMs4zNm8NjJsQld8/640?wx_fmt=png&from=appmsg&tp=wxpic&wxfrom=5&wx_lazy=1#imgIndex=19)



   **3.3 设计产物（上下文）要如何管理？**

结合上面的上面我们分析CR的方式，即CR设计与测试集，但是这些产物要如何管理，其一致性如何。

要真实的需求开发中，我们实际在各个环节在拷贝上下文，人工在处理各个流程的环节，真实的场景可能是下图：

![图片](https://mmbiz.qpic.cn/mmbiz_png/ZRhjO8xAWr5s8j58UBLLqz6LeOKq51WmktgsTzpNZ3QibP1PakRVyQbQqSyDKcMvaxg99sWYTzI5t2BOvrBvL075froYPFxJB2Kue4Liasdj0/640?wx_fmt=png&from=appmsg&tp=wxpic&wxfrom=5&wx_lazy=1#imgIndex=20)

所以这里有一个更大的工程问题：**上下文要如何管理？**

我们需要一个**工程化的方案**，从需求的源头出发，全局管理中间的所有产物。

于是，我们做了一个产品（体验阶段），提供了如下能力：

1、每月**3000的opus5.5**额度。

2、把整个**建模**融入到了AI的交互中。

3、提供记忆的管理服务。

   **上海QEcon相关材料分享**

链接: https://pan.baidu.com/s/1UE8oP0Q0E8E2SOdvO-bj9g?pwd=QESH 提取码: QESH

图文总结：https://live.photoplus.cn/live/pc/26832171/#/live

AI 逆向产物：https://sherlock.devcloud.woa.com/qecon/