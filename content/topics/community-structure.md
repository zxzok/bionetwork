---
id: community-structure
title: 社团结构与社区发现
en: Community structure and detection
domain: theory
legacy: L04
summary: 研究网络中内部紧密、彼此稀疏的节点群：模块度与随机块模型、主要算法、可检测性、结果评价与生物学验证。
keywords: [社团结构, 弱关系, 模块度, 边介数, Girvan–Newman 算法, Louvain 算法, Leiden 算法, 谱聚类, 分辨率极限, 随机块模型, 度修正随机块模型, Infomap, 映射方程, 可检测性阈值, 重叠社团, 共识聚类, 多层模块度, NMI, ARI, LFR 基准]
synonyms: [社团, community, 社区, 模块, module, 簇, cluster, 社团结构, community structure, 社区发现, 社团发现, 社团检测, community detection, 图划分, graph partitioning, 图二分, graph bisection, 割, cut size, 模块化, modularity, 模块度, Q, 模块度最大化, modularity maximization, 模块度平台, modularity plateau, 简并性, degeneracy, 分辨率参数, resolution parameter, 分辨率极限, resolution limit, 弱关系, weak ties, 强关系, strong ties, 三元闭合, triadic closure, 桥, bridge, 局部桥, local bridge, 空手道俱乐部, Zachary karate club, 配置模型, configuration model, 基本假设, fundamental hypothesis, 强社团, strong community, 弱社团, weak community, 团, clique, Bell 数, Bell number, NP 难, NP-hard, 边介数, edge betweenness, Girvan–Newman, GN 算法, 树状图, dendrogram, 贪心算法, greedy modularity, CNM, Louvain, Leiden, 细化, refinement, 常数 Potts 模型, constant Potts model, CPM, Reichardt–Bornholdt, 谱方法, spectral method, 模块度矩阵, modularity matrix, 谱二分, spectral bisection, 拉普拉斯矩阵, Laplacian, Fiedler 向量, 谱聚类, spectral clustering, Bethe Hessian, 非回溯矩阵, non-backtracking matrix, 层次聚类, hierarchical clustering, Ravasz 算法, 拓扑重叠, topological overlap, 层次模块化, hierarchical modularity, 随机块模型, stochastic block model, SBM, 度修正随机块模型, degree-corrected SBM, DC-SBM, 种植划分模型, planted partition model, 嵌套随机块模型, nested SBM, 最小描述长度, minimum description length, MDL, 贝叶斯推断, Bayesian inference, 混合成员随机块模型, mixed membership SBM, 核心–边缘结构, core-periphery, 异配结构, disassortative structure, Infomap, 映射方程, map equation, 随机游走, random walk, 马尔可夫稳定性, Markov stability, 标签传播, label propagation, 可检测性, detectability, 可检测性阈值, detectability threshold, Kesten–Stigum 阈值, 重叠社团, overlapping communities, 团渗流, clique percolation, CFinder, 连边社团, link communities, 连边聚类, link clustering, 划分密度, partition density, 共识矩阵, consensus matrix, 共识聚类, consensus clustering, 多分辨率, multiresolution, 稳定性, stability, 归一化互信息, normalized mutual information, NMI, 调整兰德指数, adjusted Rand index, ARI, 信息变差, variation of information, VI, GN 基准, LFR 基准, LFR benchmark, 混合参数, mixing parameter, 元数据, metadata, 金标准, ground truth, 参与系数, participation coefficient, 模块内度 z 分数, within-module degree z-score, 节点角色, node roles, 功能制图, functional cartography, 多层模块度, multilayer modularity, 层间耦合, interlayer coupling, 灵活性, flexibility, 时变网络, temporal network, 社团演化, community evolution, 功能模块, functional module, 疾病模块, disease module, 脑功能系统, brain systems, WGCNA]
demos: [modularity]
reviewed: 2026-11-15
---

## 概述 {#overview}

[网络结构指标与随机图](network-metrics.html)和[小世界与无标度网络模型](network-models.html)研究的是网络的**全局**性质（度分布、平均路径）和**局部**性质（聚集系数）。介于两者之间还有一个尺度：网络常常由若干“内部连接紧密、彼此连接稀疏”的节点群组成，称为社团（community）或模块（module）。在蛋白质网络中，它们可能对应蛋白复合物和信号通路；在代谢网络中，对应相对独立的代谢子系统；在脑网络中，对应视觉、运动、默认模式等功能系统；在疾病网络中，对应疾病模块。

社团发现（community detection）看似只是“把节点分组”，但它同时牵涉三个不同层次的问题：**什么算一个社团**（定义与基本假设）、**怎样找到它**（质量函数与优化算法，或生成模型与统计推断），以及**找到的东西可信吗**（显著性、稳定性、可检测性与外部验证）。本专题按这个顺序组织：

1. 从社会学的[弱关系理论](community-structure.weak-ties.html)出发，理解社团为何存在，再给出社团的[基本假设与形式化定义](community-structure.hypotheses-definitions.html)，说明可能的划分数目为何天文数字般巨大；
2. 以[模块度](community-structure.modularity.html)为中心介绍描述性方法：[Girvan–Newman 删边法](community-structure.girvan-newman.html)、[Louvain 与 Leiden 算法](community-structure.louvain-leiden.html)、[谱方法与层次聚类](community-structure.spectral-hierarchical.html)；
3. 介绍两类“换一个视角”的方法：把社团看作生成模型参数的[随机块模型与统计推断](community-structure.stochastic-block-model.html)，以及把社团看作随机游走描述压缩的[映射方程与 Infomap](community-structure.infomap.html)；
4. 讨论社团发现的理论极限——[可检测性阈值](community-structure.detectability.html)；
5. 放宽“每个节点只属于一个社团、网络不随时间变化”的假设：[重叠社团](community-structure.overlapping-communities.html)、[多分辨率与共识聚类](community-structure.multiresolution-consensus.html)、[多层与时变网络的社团](community-structure.multilayer-temporal.html)；
6. 最后是方法选择与结果评价：[方法比较](community-structure.method-comparison.html)、[划分比较与基准检验](community-structure.partition-comparison.html)、[社团结果的验证与解读](community-structure.validation.html)。

各知识页面中的算法都在[代码示例](community-structure.html#code)中有可运行的实现。

## 弱关系理论与社团的定义 {#weak-ties}

### Granovetter 的弱关系理论

1973 年，社会学家 Mark Granovetter 研究人们如何找到工作，发现一个反直觉的现象：帮人找到工作的，多是**熟人**（weak ties）而不是亲密朋友（strong ties）。他的解释把关系强度与网络结构联系了起来：

- **三元闭合**（triadic closure）：如果 B、C 都是 A 的好朋友，那么 B 和 C 很可能也认识。强关系倾向于“嵌在”三角形中；
- 因此强关系所连接的人，往往处在同一个紧密的圈子里，彼此掌握的信息高度重叠；
- 弱关系更可能是连接不同圈子的**桥**（bridge）或**局部桥**（local bridge，删去后两端点的距离大于 2 的边），能带来圈子外的新信息。

### 来自数据的检验

Granovetter 的理论在提出后几十年里难以大规模检验。Onnela 等（2007，*PNAS*）分析了一个国家约 20% 人口的手机通话网络，以通话时长衡量关系强度，发现：

1. 两个人共同好友越多（邻居重叠度越高），他们之间的通话越频繁——**强关系嵌在紧密的局部结构中**；
2. 按强度**从弱到强**删边，网络很快碎裂；按强度从强到弱删边，网络则能维持较长时间——**弱关系承担着连接不同社团的作用**。

这就给出了一幅网络的概念图：许多内部由强关系紧密相连的社团，通过少量弱关系相互连接。需要注意，“强关系在社团内部、弱关系在社团之间”是社会网络中的经验规律，并非所有网络都如此。在某些生物与技术网络中，社团之间的连接也可能是高权重的；连边权重与社团结构之间的关系需要在具体系统中检验（Barabási《Network Science》第 9 章“Communities and Link Weights”一节对此有讨论）。

::: {.callout-def}
**社团**（community，也称社区、模块、簇）：网络中的一个节点子集，子集内部的连边相对密集，与子集外部的连边相对稀疏。社团没有唯一的数学定义，不同算法实质上采用了不同的形式化方式（见[基本假设与形式化定义](community-structure.hypotheses-definitions.html)）。
:::

### 经典例子：Zachary 空手道俱乐部

人类学家 Zachary（1977）观察了一所美国大学空手道俱乐部 34 名成员之间的交往，记录了 78 条友谊关系。观察期间，教练（节点 0）与俱乐部管理者（节点 33）发生冲突，俱乐部最终分裂为两派。由于事后知道每个成员去了哪一派，这个网络成为检验社团发现算法的“标准考题”。本专题的模块度演示和代码示例都使用它。不过要记住：两派分裂是一种**节点元数据**，网络中的社团结构不必与它完全一致（见[划分比较与基准检验](community-structure.partition-comparison.html)）。

## 社团的基本假设与形式化定义 {#hypotheses-definitions}

Barabási《Network Science》第 9 章用四条“假设”串起社团发现的逻辑。它们不是定理，而是各类方法赖以成立的前提，理解它们有助于看清每种方法“默认了什么”。

### 四条基本假设

::: {.callout-def}
- **H1 基本假设**（fundamental hypothesis）：网络的社团结构唯一地蕴含在其连边图中，原则上只用邻接矩阵 $A$ 就能把它找出来。
- **H2 连通与密度假设**（connectedness and density hypothesis）：社团是局部稠密的**连通**子图——社团内任意两个节点之间应能只经由社团内部节点到达。
- **H3 随机假设**（random hypothesis）：随机网络没有内在的社团结构；判断一个划分“好”，要与同样度序列的随机网络比较。
- **H4 最大模块度假设**（maximal modularity hypothesis）：对给定网络，模块度最大的划分对应最优的社团结构。
:::

H1 让社团发现成为纯粹的图论问题；但在生物医学数据中，节点注释（基因功能、脑区位置）与网络之外的信息常常被用来“检验”社团，这实际上偏离了 H1——网络结构与外部注释可以不一致（Peel 等 2017）。H2 是 Leiden 算法相对 Louvain 的改进动机。H3 是模块度零模型的出发点，也是[可检测性阈值](community-structure.detectability.html)讨论的起点。H4 则被[分辨率极限](community-structure.derivations.html)和[模块度平台](community-structure.modularity.html)所质疑，这也是随机块模型和 Infomap 等方法出现的原因之一。

### 由严到宽的几种社团定义

记子图 $C$ 中节点 $i$ 的**内度** $k_i^{\text{int}}$（连向 $C$ 内部的边数）和**外度** $k_i^{\text{ext}}$（连向 $C$ 外部的边数）。

| 定义 | 条件 | 说明 |
|---|---|---|
| 团（clique） | $C$ 是完全子图 | 最严格；在真实网络中很少有大团，且团内节点地位完全对称 |
| 强社团（strong community） | 对每个 $i\in C$，$k_i^{\text{int}}>k_i^{\text{ext}}$ | 每个成员“更忠于”本社团（Radicchi 等 2004） |
| 弱社团（weak community） | $\sum_{i\in C}k_i^{\text{int}}>\sum_{i\in C}k_i^{\text{ext}}$ | 只要求社团整体的内部连接多于外部连接 |

每个团都是强社团，每个强社团都是弱社团，反之不成立。以上是**局部**定义：只看子图自身和它的边界。模块度、随机块模型等则是**全局**定义：社团是整个划分的一部分，好坏由全网的质量函数或似然决定。

### 社团不一定“内部稠密”

“内部稠密、外部稀疏”的**同配**（assortative）结构只是众多分块结构中的一种。二分网络（如药物–靶点网络）中，同类节点之间没有边，组之间才有边，是典型的**异配**（disassortative）结构；**核心–边缘**结构中，核心节点彼此相连并连接边缘节点，而边缘节点之间很少相连。模块度只奖励同配结构，而[随机块模型](community-structure.stochastic-block-model.html)可以同时描述这几类结构。在把“社团”一词用于某个生物网络之前，先想清楚要找的是哪一种结构。

### 划分数目：为什么不能穷举

最简单的社团问题是**图二分**（graph bisection）：把 $N$ 个节点分成两个等大的组，使两组之间的边数（**割**，cut size）最小。等大二分的方式有
$$
\binom{N}{N/2}=\frac{N!}{[(N/2)!]^2}\approx \frac{2^{N+1}}{\sqrt{2\pi N}}
$$
种（由 Stirling 公式得到）。若不限定组数和组的大小，$N$ 个节点的全部划分数是 **Bell 数** $B_N$，满足递推 $B_{N+1}=\sum_{j=0}^{N}\binom{N}{j}B_j$，并有 Dobinski 公式 $B_N=\frac1e\sum_{j\ge0} j^N/j!$。Bell 数增长得比任何指数函数都快：$B_{10}=115\,975$，$B_{20}\approx5.2\times10^{13}$，$B_{50}\approx1.9\times10^{47}$（[代码示例](community-structure.html#code)）。

::: {.callout-def}
**计算复杂性**：模块度最大化是 NP 难问题（Brandes 等 2008）。因此所有实用的模块度算法都是启发式的，只能保证得到“好的”而非“最优的”划分。只有在十几个节点以内的网络上，才能穷举全部 $B_N$ 种划分求得精确最优。
:::

**手算例**：4 个节点的路径 1–2–3–4（$m=3$，度为 1,2,2,1）。$B_4=15$ 种划分中，$\{1,2\}\{3,4\}$ 的模块度为 $2\times\left[\frac13-\left(\frac36\right)^2\right]=\frac16\approx0.167$；$\{1\}\{2,3,4\}$ 为 $\left[0-\left(\frac16\right)^2\right]+\left[\frac23-\left(\frac56\right)^2\right]=-\frac1{36}+\frac{-1}{36}=-\frac{1}{18}$。可以逐一验证，$\{1,2\}\{3,4\}$ 是 15 种划分中模块度最大的。

### 描述性方法与推断性方法

Peixoto（2023）把社团发现方法区分为两类：**描述性**方法（如模块度最大化）给出一个满足某种准则的划分，回答“这个网络可以怎样被概括”；**推断性**方法（如贝叶斯随机块模型）假设网络由某个含分组的生成过程产生，回答“哪种分组最可能产生了这个网络、证据有多强”。两者问的是不同问题：描述性方法在随机网络中也会“找到”社团（见下页），推断性方法则会在证据不足时报告“没有结构”。选择方法前应先明确研究问题属于哪一类。

## 模块度 {#modularity}

### 思路：与随机期望比较

一个好的划分，社团内部的边应当“多于随机情况下的预期”。问题是：随机预期应该怎么算？如果只按边数平均分配，枢纽节点因为连接多，会被误认为与谁都“紧密”。Newman 和 Girvan 选用的零模型是**配置模型**（configuration model）：保持每个节点的度不变，随机重新配对所有“半边”。在这个零模型下，度为 $k_i$ 和 $k_j$ 的两个节点之间期望的边数为 $\dfrac{k_i k_j}{2m}$（$m$ 为总边数）。

::: {.callout-def}
**模块度**（modularity）：
$$
Q = \frac{1}{2m}\sum_{i,j}\left[A_{ij} - \frac{k_i k_j}{2m}\right]\delta(c_i, c_j),
$$
其中 $c_i$ 是节点 $i$ 所属的社团，$\delta(c_i,c_j)=1$ 当且仅当 $i,j$ 属于同一社团。等价地按社团求和：
$$
Q = \sum_{c}\left[\frac{l_c}{m} - \left(\frac{d_c}{2m}\right)^2\right],
$$
$l_c$ 为社团 $c$ 内部的边数，$d_c$ 为社团 $c$ 内所有节点的度之和。
:::

第二种写法的含义很直观：$l_c/m$ 是“实际落在社团内部的边的比例”，$(d_c/2m)^2$ 是“随机配对时预期落在社团内部的比例”。本专题页面的模块度演示可以点击节点改变分组，实时观察 $Q$ 的变化。

### 一个手算例子

两个三角形 {1,2,3} 与 {4,5,6}，再用一条边 3–4 相连。共 $m = 7$ 条边。

- 划分为两个三角形：每个社团 $l_c = 3$；度为 2、2、3，$d_c = 7$。
  $Q = 2 \times \left[\dfrac{3}{7} - \left(\dfrac{7}{14}\right)^2\right] = 2 \times (0.429 - 0.25) \approx 0.357$。
- 所有节点放在一个社团：$Q = \dfrac{7}{7} - 1^2 = 0$。
- 每个节点单独一个社团：没有内部边，$Q = -\sum_i (k_i/2m)^2 < 0$。

### 加权与有向网络的推广

- **加权网络**：把 $A_{ij}$ 换成边权 $w_{ij}$，$k_i$ 换成节点强度 $s_i=\sum_j w_{ij}$，$m$ 换成总权重的一半。
- **有向网络**（Leicht 与 Newman 2008）：零模型改为“$j$ 的出度与 $i$ 的入度相乘”，$Q=\frac{1}{m}\sum_{ij}\left[A_{ij}-\frac{k_i^{\text{in}}k_j^{\text{out}}}{m}\right]\delta(c_i,c_j)$，$m$ 为有向边数。它只看边的密度，不看流动方向形成的循环；若社团的意义在于“信息在其中循环停留”，[映射方程](community-structure.infomap.html)更合适。
- **带符号网络**（如含负相关的功能连接）：正、负边的零模型需要分别构造，不能直接把负权代入上式（见[脑连接组](brain-connectome.html)中关于负相关的讨论）。

### 模块度的性质与局限

- **取值范围**：$Q<1$；整个网络作为一个社团时 $Q=0$。若划分含 $n_c$ 个社团，则 $Q\le1-1/n_c$。实际网络中，“有明显社团结构”的划分通常 $Q$ 在 0.3–0.7 之间。
- **随机网络也能得到不低的 $Q$**。在一个没有任何真实社团的 ER 网络上做模块度最大化，往往也能找到 $Q$ 达 0.3 以上的划分（Guimerà 等，2004），对稀疏的小网络尤其如此。因此 $Q$ 的绝对值不能直接说明“社团结构显著”，应与同样度序列的随机网络比较。这违背了 H3 的精神：模块度最大化本身无法区分“结构”与“涨落”。
- **分辨率极限**（resolution limit，Fortunato 与 Barthélemy，2007）：模块度的零模型依赖网络总边数 $m$。在大网络中，度之和小于约 $\sqrt{2m}$ 量级的社团，即使本身是完全连接的小团，也可能被合并到更大的社团中（推导见[数学推导与算法](community-structure.derivations.html)）。
- **简并性与模块度平台**：Good、de Montjoye 与 Clauset（2010）发现，模块度函数在高值区不是一个尖峰，而是一片“高原”：存在数量随网络规模指数增长的划分，它们的 $Q$ 与最大值相差无几，但彼此结构差别很大。这解释了为什么各种启发式算法都能很快找到“高 $Q$”划分，也意味着最大 $Q$ 的那个划分并没有特殊的可信度。

::: {.callout-warn}
很多软件提供**分辨率参数** $\gamma$（Reichardt 与 Bornholdt 2006）：$Q_\gamma = \frac{1}{2m}\sum_{ij}[A_{ij} - \gamma\frac{k_ik_j}{2m}]\delta(c_i,c_j)$。$\gamma>1$ 得到更多、更小的社团，$\gamma<1$ 得到更少、更大的社团。它不能消除分辨率问题，只是让你选择观察的尺度。报告结果时要写明 $\gamma$ 的取值，最好展示结论在一系列 $\gamma$ 下是否稳健（见[多分辨率与共识聚类](community-structure.multiresolution-consensus.html)）。
:::

### 贪心模块度算法

最早的快速模块度算法是 Newman（2004）的**贪心凝聚法**：开始时每个节点自成一个社团，每一步合并能使 $Q$ 增加最多（或减少最少）的一对相连社团，直到只剩一个社团，再选 $Q$ 最大的那一层。Clauset、Newman 与 Moore（2004）用堆结构把它加速到稀疏层次网络上约 $O(n\log^2 n)$，常称 CNM 算法（NetworkX 中的 `greedy_modularity_communities`）。贪心合并倾向于先形成少数大社团、再吞并小社团，在基准测试中通常不如 Louvain 准确（见[划分比较与基准检验](community-structure.partition-comparison.html)）。

## Girvan–Newman 算法与边介数 {#girvan-newman}

### 边介数

社团之间的连边少，所以社团之间的最短路径必须挤过这些少数“桥”。这启发了**边介数**（edge betweenness）的定义：

::: {.callout-def}
**边介数**：网络中所有节点对之间的最短路径中，经过某条边的数量（若一对节点之间有多条等长最短路径，按比例分摊）。
:::

社团之间的边介数高，社团内部的边介数低。这与 Granovetter 的“弱关系是桥”一脉相承。

### 算法步骤

1. 计算所有边的边介数；
2. 删除边介数最大的边；
3. **重新计算**剩余所有边的边介数（删边会改变最短路径，这一步不能省略）；
4. 重复第 2–3 步，直到所有边都被删除。

在删边过程中，网络逐渐分裂为越来越多的连通分支，这一过程形成一棵**树状图**（dendrogram）。在哪一层“切”下去？常用做法是选择**模块度最大**的那一层。

在空手道俱乐部网络上，Girvan–Newman 算法的第一次分裂与真实的两派分裂几乎一致，只有个别节点被分到另一侧；继续分裂，模块度在 5 个社团时达到最大（约 0.40）。

### 分裂式与凝聚式

Girvan–Newman 是**分裂式**（divisive）层次方法：从整个网络出发，逐步删去“最不像社团内部”的边。与之相对的**凝聚式**（agglomerative）方法从单个节点出发逐步合并最相似者，见[层次聚类](community-structure.spectral-hierarchical.html)。删边的依据也不限于边介数：Radicchi 等（2004）用**边聚集系数**（一条边参与的三角形数相对于可能的最大数）作为局部替代量——社团之间的边很少处在三角形中——计算量远小于边介数。

### 优缺点

优点：思路直观，输出完整的层次结构。缺点：每删一条边都要重新计算所有边介数，单次计算需要 $O(mn)$，总计算量约为 $O(m^2 n)$，只适用于几百到几千个节点的网络。

## Louvain 与 Leiden 算法 {#louvain-leiden}

### Louvain 算法

**Louvain 算法**（Blondel 等，2008）是目前最常用的社团发现算法之一，它反复执行两个阶段：

1. **局部移动**：开始时每个节点自成一个社团。依次考察每个节点，把它移到能使 $Q$ 增加最多的邻居社团中（若都不能增加则不动），直到没有节点再移动；
2. **聚合**：把每个社团压缩成一个“超节点”，社团内部的边变成超节点的自环，社团之间的边合并为加权边。在新网络上回到第 1 步。

每一轮聚合得到一层更粗的划分，自然形成层次结构。Louvain 速度很快，可处理数百万节点的网络。局部移动中 $\Delta Q$ 的计算公式与伪代码见[数学推导与算法](community-structure.derivations.html)。

### Louvain 的缺陷：连接不良的社团

Traag、Waltman 与 van Eck（2019）指出 Louvain 有一个长期被忽视的问题：它可能产生**连接不良**（badly connected）甚至**内部不连通**的社团。原因在于局部移动阶段：设节点 $v$ 是社团 $C$ 内部连接其他几部分的“桥”，当 $v$ 被移到另一个社团后，$C$ 剩下的部分可能已经断开，但它们之后作为一个整体被聚合成超节点，以后的层次中再也不会被拆开。作者在若干真实网络上的实验中观察到，Louvain 的结果中最多约 25% 的社团连接不良、最多约 16% 的社团不连通，而且迭代运行 Louvain 会让问题更严重。这直接违背了 H2（社团应当连通）。

### Leiden 算法的改进

**Leiden 算法**在“局部移动”和“聚合”之间加入**细化**（refinement）阶段：

1. **快速局部移动**：与 Louvain 相似，但只把“邻居发生变化”的节点放回待访问队列，而不是每轮遍历全部节点，因此更快；
2. **细化**：在第 1 步得到的每个社团 $C$ **内部**，从单点出发重新合并，只允许把节点并入与它连接足够好的子社团，并且合并时带有一定随机性（由参数 $\theta$ 控制）；这样得到的细化划分中，每个子社团都是 $C$ 的连通子集；
3. **聚合**：以**细化后**的子社团为超节点构造聚合网络，但用第 1 步的划分作为聚合网络的初始划分。

由于聚合基于细化划分，一个原来连接不良的社团在下一层会以多个超节点的形式出现，仍然可以被拆开。作者证明：Leiden 每次迭代后的社团都是连通的（进一步满足 $\gamma$-连接性）；反复迭代直到划分不再改变时，所有社团的所有子集都处于局部最优位置。实践中 Leiden 通常更快，且得到的 $Q$ 与 Louvain 相当或更高。

::: {.callout-warn}
- 两者都含有随机性（节点访问顺序、细化中的随机合并），不同运行可能给出不同结果；应固定随机种子以便复现，并用多次运行评估稳定性。
- Leiden 保证的是**连通性**，不是**正确性**：它同样继承模块度的分辨率极限和简并性。
- NetworkX 从 3.7 起提供纯 Python 实现的 `leiden_communities`（3.5、3.6 中只有接口，须安装后端才能运行；本站环境为 3.7），但其默认质量函数是 CPM 而非模块度（`metric="cpm"`, `resolution=1`），对无权网络几乎只会返回单点社团；用模块度时应显式设置 `metric="modularity"`。官方实现见 `leidenalg`（基于 igraph）。
:::

### 质量函数的选择：模块度与常数 Potts 模型

Louvain/Leiden 只是优化框架，可以优化不同的质量函数。Traag、Van Dooren 与 Nesterov（2011）提出**常数 Potts 模型**（constant Potts model, CPM）：
$$
H_{\text{CPM}}=\sum_c\left[e_c-\gamma\binom{n_c}{2}\right],
$$
$e_c$ 为社团内部的边数（或边权之和），$n_c$ 为社团节点数。其含义是：社团内部的边密度应高于 $\gamma$，社团之间的边密度应低于 $\gamma$。由于 CPM 中没有全网边数 $m$，它是**无分辨率极限**的：一个子图是否被识别为社团只取决于其自身与相邻部分，而不取决于网络其余部分有多大。代价是 $\gamma$ 的取值有了“密度”的绝对含义，需要按网络的边密度量级来选。在由 $K_5$ 团组成的环上，模块度在团数超过 22 时开始合并相邻团，而 CPM（取 $0<\gamma<$ 团内密度）不论团数多少都把每个团单独识别出来（[代码示例](community-structure.html#code)）。

## 谱方法与层次聚类 {#spectral-hierarchical}

### 模块度谱方法

把模块度写成矩阵形式。定义**模块度矩阵** $B_{ij} = A_{ij} - \dfrac{k_ik_j}{2m}$。若把网络一分为二，用 $s_i = \pm 1$ 表示节点 $i$ 属于哪一侧，则

$$
Q = \frac{1}{4m}\, \mathbf{s}^\top B\, \mathbf{s}.
$$

在 $s_i$ 只能取 $\pm1$ 的约束下精确最大化很困难；放松为实数后，最优解就是 $B$ 的**最大特征值对应的特征向量**。按其分量的正负号把节点分为两组，就得到谱二分（Newman，2006）。对每一组可以继续二分，直到 $Q$ 不再增加。特征向量分量的绝对值还给出了一种“归属强度”：$|u_i|$ 接近 0 的节点处于两组之间，归属最不确定。

### 拉普拉斯谱聚类

另一类谱方法基于图拉普拉斯矩阵 $L = D - A$。最小割问题 $\min \frac14\mathbf s^\top L\mathbf s$ 放松后的解是 $L$ 的第二小特征值（代数连通度）对应的特征向量，即 **Fiedler 向量**。为避免切下孤立的小块，常改用比率割（对应 $L$ 本身）或归一化割（对应 $D^{-1}L$ 或对称归一化拉普拉斯 $D^{-1/2}LD^{-1/2}$）的特征向量。分成 $K$ 组时，取前 $K$ 个特征向量作为节点坐标，再用 k 均值聚类，这就是机器学习中常用的**谱聚类**。它需要预先给定 $K$，可用“特征值间隙”（eigengap）粗略估计。

### 稀疏网络中的谱方法

在平均度很低的稀疏网络中，邻接矩阵和拉普拉斯矩阵的主特征向量容易**局域化**在少数高度节点或悬挂树上，不再携带社团信息。Krzakala 等（2013）提出基于**非回溯矩阵**（non-backtracking matrix，描述“不立即原路返回”的游走）的谱方法；Saade、Krzakala 与 Zdeborová（2014）给出等价但更易计算的 **Bethe Hessian** $H(r)=(r^2-1)I-rA+D$（$r$ 取平均超额度的平方根，近似为 $\sqrt{\langle k\rangle}$），其负特征值的个数可估计社团数，对应特征向量用于划分。这类方法在稀疏随机块模型上一直有效到理论可检测阈值（见[可检测性阈值](community-structure.detectability.html)）。

### 层次聚类与 Ravasz 算法

层次聚类（hierarchical clustering）先定义节点之间的相似度，再自底向上逐步合并最相似的节点或簇，形成树状图。Ravasz 等（2002）为识别代谢网络中的功能模块提出的算法是一个典型例子：

1. **拓扑重叠相似度**：
$$
x_{ij}=\frac{J(i,j)}{\min(k_i,k_j)+1-\Theta(A_{ij})},
$$
其中 $J(i,j)$ 是 $i,j$ 的共同邻居数，若 $i,j$ 直接相连则 $J$ 再加 1；$\Theta(A_{ij})$ 在 $i,j$ 相连时为 1、否则为 0。$x_{ij}=1$ 表示两点的邻居完全重叠，$x_{ij}=0$ 表示没有共同邻居且不相连。
2. **簇间相似度**：合并时如何衡量两个簇之间的相似度有三种常见选择——单连接（取簇间最相似的一对）、全连接（取最不相似的一对）、平均连接（取所有跨簇节点对的平均）。Ravasz 算法采用平均连接。
3. **逐步合并**：每次合并相似度最高的两个簇，更新簇间相似度，直到所有节点合为一个簇；得到的树状图可在不同高度切割，或用模块度选择切割高度。

计算量的主要部分是相似度矩阵（$O(n^2)$）与合并过程（朴素实现 $O(n^2\log n)$ 级），适用于数千到数万节点的网络。基因共表达网络分析中的 WGCNA 方法就是“拓扑重叠相似度 + 平均连接层次聚类 + 动态剪枝”的一个变体（见[基因调控网络推断与共表达分析](gene-network-inference.html)）。

### 层次模块性

在许多真实网络中，小而紧密的模块组合成较大、较松散的模块，再逐级组合，形成**层次模块化**结构。Ravasz 与 Barabási 的确定性层次模型给出了一个可解析的例子：从一个 5 节点完全图开始，每一步复制 4 份并把复制品的外围节点连到原来的中心节点。这一构造产生度指数 $\gamma=1+\ln5/\ln4\approx2.16$ 的无标度网络，而且聚集系数随度按 $C(k)\sim k^{-1}$ 递减——高度节点连接不同模块，邻居之间很少相连。$C(k)$ 随 $k$ 递减常被当作层次模块性的一个经验特征（但并非充分条件）。

## 随机块模型与统计推断 {#stochastic-block-model}

### 从“找划分”到“拟合模型”

模块度最大化问的是“哪个划分使某个分数最高”；**随机块模型**（stochastic block model, SBM）问的是“什么样的分组最可能生成了观测到的网络”。SBM 最早由 Holland、Laskey 与 Leinhardt（1983）在社会网络分析中提出，后来成为社团发现中统计推断方法的基础（Peixoto 2019 的综述）。

::: {.callout-def}
**随机块模型**：$n$ 个节点各属于 $B$ 个组之一，组标签 $b_i\in\{1,\dots,B\}$；任意两个节点 $i,j$ 之间是否有边（或有多少条边）相互独立，概率只取决于它们所属的组：
$$
P(A_{ij}=1)=p_{b_ib_j}.
$$
$B\times B$ 矩阵 $p_{rs}$ 描述了组内、组间的连接倾向。$p_{rr}>p_{rs}$ 时为同配的社团结构；$p_{rr}<p_{rs}$ 时为异配结构；还可以描述核心–边缘等其他混合模式。
:::

最简单的特例是**种植划分模型**（planted partition model）：$B$ 个等大的组，组内连边概率 $p_{\text{in}}$，组间 $p_{\text{out}}$。它是检验算法和研究[可检测性](community-structure.detectability.html)的标准模型。

### 度修正随机块模型

标准 SBM 中同组节点的期望度相同，而真实网络的度分布高度异质。Karrer 与 Newman（2011）发现，用标准 SBM 拟合空手道网络时，最大似然的二分并不是两派，而是把少数高度节点和其余低度节点分开——模型只能用“组”来解释度的差异。他们提出**度修正 SBM**（degree-corrected SBM, DC-SBM）：
$$
A_{ij}\sim \text{Poisson}\left(\theta_i\theta_j\,\omega_{b_ib_j}\right),
$$
节点参数 $\theta_i$ 刻画节点自身的“活跃度”，$\omega_{rs}$ 刻画组间的连接倾向。用最大似然消去 $\theta$ 与 $\omega$ 后，只剩下依赖划分的目标函数（推导见[数学推导与算法](community-structure.derivations.html)）：
$$
\mathcal L_{\text{SBM}}=\sum_{rs}m_{rs}\ln\frac{m_{rs}}{n_rn_s},\qquad
\mathcal L_{\text{DC}}=\sum_{rs}m_{rs}\ln\frac{m_{rs}}{\kappa_r\kappa_s},
$$
$m_{rs}$ 为组 $r$、$s$ 之间的边数（$r=s$ 时计两次），$n_r$ 为组的节点数，$\kappa_r$ 为组内节点度之和。在空手道网络上，DC-SBM 的最大似然二分与两派分裂基本一致（[代码示例](community-structure.html#code)中只与真实两派差 2 个节点）。

**与模块度的关系**：Newman（2016）证明，带分辨率参数 $\gamma$ 的模块度最大化，等价于一个特殊的“种植划分 DC-SBM”的最大似然估计——所有组内连接倾向都等于 $\omega_{\text{in}}$、组间都等于 $\omega_{\text{out}}$，且
$$
\gamma=\frac{\omega_{\text{in}}-\omega_{\text{out}}}{\ln\omega_{\text{in}}-\ln\omega_{\text{out}}}.
$$
这给 $\gamma$ 提供了统计解释，也说明模块度隐含了“所有社团同样紧密”的强假设。

### 模型选择：组数 $B$ 怎么定

最大似然有一个根本问题：组数越多，似然越大（每个节点自成一组时最大），所以不能直接用似然选择 $B$。常见解决办法：

- **贝叶斯推断与最小描述长度**（Peixoto 2017, 2019）：给参数加上无信息先验，计算划分的后验概率 $P(\mathbf b\mid A)\propto P(A\mid\mathbf b)P(\mathbf b)$。$-\ln P(A,\mathbf b)$ 可以解释为用模型“压缩”网络所需的**描述长度**：数据部分 $-\ln P(A\mid\mathbf b)$ 随组数增加而减小，模型部分 $-\ln P(\mathbf b)$ 随组数增加而增大，二者之和自动权衡复杂度与拟合度。在没有结构的随机网络上，后验最可能的结果是 $B=1$——这与模块度在随机网络上也能找到高 $Q$ 的行为形成对照。
- **嵌套 SBM**（Peixoto 2014）：把组本身再看作一个网络的节点，用更高一层的 SBM 描述组间连接矩阵，逐层向上，形成层次结构。Peixoto（2013）指出，非层次 SBM 用描述长度做模型选择时，可检测的组数上限约随 $\sqrt N$ 增长——这也是一种分辨率极限；嵌套的先验大大放宽了这一上限，使大网络中的小组仍可被识别。
- **后验不确定性**：贝叶斯方法不只给一个“最优”划分，还可以对后验分布抽样，得到每个节点属于各组的边际概率，以及划分的整体不确定性。

::: {.callout-warn}
SBM 同样有前提：连边条件独立、组内节点（在度修正后）统计上可交换。真实生物网络中三角形很多（三元闭合），而 SBM 对三角形的刻画能力有限，可能用许多小组来“解释”局部聚集。此外，DC-SBM 的推断在大网络上需要 MCMC 等较重的计算（`graph-tool` 软件是主要实现），对于百万节点以上的网络仍有挑战。
:::

### SBM 的扩展

- **混合成员 SBM**（Airoldi 等 2008）：每个节点有一个在各组上的隶属概率向量，可用于[重叠社团](community-structure.overlapping-communities.html)；
- **加权、多层与时变 SBM**：边权、多种关系或多个时间层由相应的分布描述，适用于共表达、多组学和纵向脑网络数据；
- **带元数据的 SBM**：把节点注释作为额外信息纳入模型，可以检验“元数据与网络结构是否相关”，而不是默认二者一致。

## 映射方程与 Infomap {#infomap}

### 社团是“流”停留的地方

模块度和 SBM 都从**连边的分布**出发定义社团。Rosvall 与 Bergstrom（2008）换了一个角度：许多网络承载着“流”——信号在通路中传递、信息在脑区间流动、引文从一篇论文流向另一篇。若一个随机游走者进入某组节点后往往要停留很久才离开，这组节点就是一个社团。他们把“找社团”变成一个**数据压缩**问题：要把随机游走者的轨迹编码成尽量短的比特串，最好的编码方式就会揭示社团结构。

### 两层编码与映射方程

用类似地图的方式编码轨迹：每个模块内部有一本**模块码本**，给模块内的节点分配短码，同一个短码可以在不同模块中重复使用（就像不同城市可以有同名的街道）；另有一本**索引码本**，只在游走者进入一个新模块时使用，记录进入了哪个模块；每本模块码本中再有一个**退出码**，表示离开当前模块。若社团划分得好，游走者大部分时间在模块内部，只用短的模块码本；跨模块的“索引 + 退出”开销很少出现。

::: {.callout-def}
**映射方程**（map equation）：对划分 $M$，描述随机游走每一步所需的平均码长下界为
$$
L(M)=q\,H(\mathcal Q)+\sum_{i=1}^{n_c}p_i\,H(\mathcal P_i),
$$
其中 $q=\sum_i q_i$ 为每一步“进入某个模块”的概率（使用索引码本的频率），$H(\mathcal Q)$ 为索引码本的熵；$p_i=q_i+\sum_{\alpha\in i}p_\alpha$ 为使用模块 $i$ 码本的频率（模块内节点的访问概率加上退出概率），$H(\mathcal P_i)$ 为模块码本的熵。熵以 2 为底，单位为比特。
:::

对无向无权网络，随机游走的稳态访问概率 $p_\alpha=k_\alpha/2m$，模块 $i$ 的退出概率 $q_i$ 等于它的外连边数除以 $2m$。把熵展开后，$L(M)$ 只依赖于 $q_i$、$p_\alpha$ 两类量（[数学推导与算法](community-structure.derivations.html)）。**Infomap** 就是最小化 $L(M)$ 的算法：先用与 Louvain 相似的局部移动和聚合，再加入子模块移动、单节点移动等细化步骤，复杂度与 Louvain 同量级。

**小例子**：空手道网络中，所有节点放在一个模块时 $L=4.70$ 比特（即节点访问分布的熵）；按真实两派划分时 $L=4.46$ 比特；用 Louvain 的 4 社团划分时 $L=4.34$ 比特（[代码示例](community-structure.html#code)）。划分越能“困住”游走者，描述越短。

### 与模块度的区别

- **有向与加权网络**：映射方程天然使用有向网络上的流（对有向网络需加入“传送”以保证游走遍历，类似 PageRank），而有向模块度只看边的密度。在引文网络、信号转导网络、有效连接网络中，二者可能给出明显不同的结果。
- **分辨率**：映射方程不使用配置模型零模型，在“团组成的环”这一构造中，即使团数很多也偏好把每个团分开，而模块度会合并相邻团（[代码示例](community-structure.html#code)）。但它并非完全没有分辨率限制：模块很多、跨模块流很大时，索引码本的开销也会促使合并。
- **随机网络**：在没有结构的网络上，最优 $L$ 往往对应单一模块，Infomap 倾向于不报告虚假社团；但这只是经验行为，不是统计检验。
- **层次与重叠的推广**：多层映射方程（Rosvall 与 Bergstrom 2011）用嵌套的码本描述层次模块；带“记忆”的高阶版本可以让同一个节点在不同流动路径中属于不同模块，从而得到重叠社团。

基准测试中，Infomap 与 Louvain 都属于表现最好的一类方法（Lancichinetti 与 Fortunato 2009）。Power 等（2011）对静息态功能脑网络划分功能系统时，使用的正是 Infomap。

### 其他基于动力学的方法

- **马尔可夫稳定性**（Markov stability，Delvenne、Yaliraki 与 Barahona 2010）：用“随机游走在时间 $t$ 后仍留在起始社团的概率超出随机期望的程度”作为质量函数，马尔可夫时间 $t$ 起分辨率参数的作用，在特定的线性化极限下与模块度对应；扫描 $t$ 可以得到多尺度划分。
- **标签传播**（label propagation，Raghavan 等 2007）：每个节点反复采用邻居中最常见的标签，直到收敛。几乎线性时间，但结果高度依赖随机顺序，且在社团不清晰时可能整体塌缩为一个社团。

## 可检测性阈值 {#detectability}

### 问题：结构存在，但能找到吗

H3 说随机网络没有社团。反过来问：如果网络确实由含社团的模型生成，但社团之间的差别很弱，算法能不能把它找出来？答案是：存在一个**相变式的阈值**，低于它时，**任何**算法都无法以优于随机猜测的准确率恢复真实分组——不是算法不够好，而是信息本身已不足。

### 稀疏 SBM 的阈值

考虑 $q$ 个等大组的种植划分模型，组内连边概率 $c_{\text{in}}/n$、组间 $c_{\text{out}}/n$，平均度 $c=[c_{\text{in}}+(q-1)c_{\text{out}}]/q$ 为常数（稀疏极限）。Decelle、Krzakala、Moore 与 Zdeborová（2011）用统计物理的方法证明：

::: {.callout-def}
**可检测性阈值**：当
$$
|c_{\text{in}}-c_{\text{out}}|\le q\sqrt{c}
$$
时，在 $n\to\infty$ 的极限下，没有任何算法能得到与真实分组相关性大于零的划分；当 $|c_{\text{in}}-c_{\text{out}}|>q\sqrt c$ 时，置信传播（belief propagation）等算法可以得到正相关的划分。这一条件也称为 Kesten–Stigum 阈值。
:::

几点含义：

- **阈值低于“社团看起来存在”的直觉标准**：即使 $c_{\text{in}}>c_{\text{out}}$，组内连边多于组间连边，只要差距不足 $q\sqrt c$，社团结构就无法从网络中恢复。例如 $q=2$、$c=5$ 时，阈值为 $\Delta c=2\sqrt5\approx4.47$，即 $c_{\text{in}}\approx7.2$、$c_{\text{out}}\approx2.8$——组内连边比组间多一倍以上，仍然处在不可检测的边缘。
- **平均度越大，越容易检测**：阈值与 $\sqrt c$ 成正比，而 $c_{\text{in}}-c_{\text{out}}$ 可以与 $c$ 同量级增长，所以稠密网络中的社团更容易被检测到。这对稀疏的生物网络（如实验测得的 PPI 网络）是一个提醒：观测到的边越少，能可靠识别的社团结构就越粗。
- **$q\ge5$ 时存在“困难区”**：在阈值之上的一段参数范围内，信息论上可以检测，但目前已知的多项式时间算法做不到；$q\le4$ 时阈值处是连续相变，不存在这一困难区。

### 哪些算法能达到阈值

置信传播、基于非回溯矩阵或 Bethe Hessian 的谱方法可以一直工作到阈值（Krzakala 等 2013）；基于邻接矩阵、拉普拉斯矩阵或模块度矩阵的普通谱方法，在稀疏网络中会因为特征向量局域化在高度节点上而提前失效。Nadakuditi 与 Newman（2012）用随机矩阵理论分析了谱方法的可检测转变。在[代码示例](community-structure.html#code)中，$q=2$、$c=5$、$n=4000$ 的种植划分网络上，Bethe Hessian 恢复的重叠度（0 为随机猜测、1 为完全恢复）在 $\Delta c/2\sqrt c=0.9$ 时约为 0.05，1.1 时约为 0.27，1.5 时约为 0.79，与理论阈值 $\Delta c/2\sqrt c=1$ 吻合；有限规模下阈值附近的转变会被抹平。

::: {.callout-warn}
可检测性阈值是在理想化模型（等大组、稀疏、$n\to\infty$）下得到的。它的实际意义在于：**算法没有找到社团，不等于网络中没有社团结构**；**算法找到的社团与已知分组不一致，也可能只是信号太弱**。对稀疏、含测量缺失的生物网络，应先估计信号强度（例如与同样度序列的随机网络比较），再解释社团结果。
:::

## 重叠社团 {#overlapping-communities}

上面的方法都把每个节点只分到一个社团。但一个人可以同时属于家庭、同事、球友几个圈子；一个蛋白也可以同时参与多个复合物；一个脑区可以参与多个功能系统。

### 团渗流（CFinder）

**团渗流方法**（clique percolation，Palla 等，2005）允许社团重叠：把 $k$ 个节点两两相连的子图称为 $k$-团，共享 $k-1$ 个节点的两个 $k$-团视为“相邻”，相互可达的 $k$-团的并集构成一个 $k$-团社团。一个节点可以属于多个这样的社团。直观上，可以想象一个 $k$-团“模板”在网络上滚动：每次移动一个节点到新位置，只要新位置仍构成 $k$-团，模板就能继续滚动；模板能到达的所有位置构成一个社团。

**随机网络中的渗流阈值**：团渗流社团会不会在随机网络中偶然出现？Derényi、Palla 与 Vicsek（2005）推导出 ER 网络中 $k$-团渗流的阈值
$$
p_c(k)=\frac{1}{[(k-1)N]^{1/(k-1)}}.
$$
$k=2$ 时 $p_c=1/N$，即巨连通分支出现的条件；$k=3$ 时 $p_c=1/\sqrt{2N}$。连接概率低于 $p_c(k)$ 时，随机网络中只有零散的 $k$-团，不会形成大的 $k$-团社团。因此，若真实网络中存在大的 $k$-团社团，而它的边密度低于对应的阈值，就说明这些社团不是密度带来的偶然产物（推导见[数学推导与算法](community-structure.derivations.html)）。

团渗流的局限：$k$ 需要人为选择；网络中没有三角形的部分（如树状边缘）不属于任何社团；在稠密网络中可能形成一个巨大的社团。在空手道网络上，$k=3$ 得到一个 25 节点的大社团，$k=4$ 时则有 22 个节点不属于任何社团（[代码示例](community-structure.html#code)）。

### 连边社团（link communities）

Ahn、Bagrow 与 Lehmann（2010）提出把**边**而不是节点分组：每条边只属于一个社团，而节点通过它的不同边自然地属于多个社团。具体做法：

1. 对共享一个端点 $k$ 的两条边 $e_{ik}$、$e_{jk}$，定义相似度 $S(e_{ik},e_{jk})=\dfrac{|n_+(i)\cap n_+(j)|}{|n_+(i)\cup n_+(j)|}$，$n_+(i)$ 为包含 $i$ 自身的邻居集；
2. 对边做单连接层次聚类，得到边的树状图；
3. 在使**划分密度** $D=\frac{2}{M}\sum_c m_c\frac{m_c-(n_c-1)}{(n_c-2)(n_c-1)}$ 最大的高度切割（$M$ 为总边数，$m_c$、$n_c$ 为连边社团 $c$ 的边数与节点数）。

$D$ 衡量每个连边社团比同样节点数的树多出多少边。连边聚类同时给出层次与重叠，适合“每个节点参与很多不同情境”的网络；Ahn 等在包括蛋白质相互作用在内的多个网络上展示了它。一个与之相关的思路是在**线图**（以边为节点）上做普通的社团划分（Evans 与 Lambiotte 2009）。

### 其他途径

- **混合成员 SBM**、OSLOM 等统计方法给出节点在各社团中的隶属程度；
- 对 Louvain 等不重叠算法多次运行，节点在不同运行中所属社团的变化本身就提示其“跨社团”的地位（见[共识聚类](community-structure.multiresolution-consensus.html)）；
- 参与系数（[验证与解读](community-structure.validation.html)）是在不重叠划分上刻画“节点连接多个社团”的简单指标。

## 多分辨率与共识聚类 {#multiresolution-consensus}

### 为什么需要多分辨率

真实网络的社团结构往往是多尺度的：蛋白复合物嵌在通路中，通路又嵌在更大的功能系统中；脑网络中的子系统组合成更大的系统。一个固定的 $\gamma$（或 CPM 的密度阈值、马尔可夫时间 $t$）只选取了其中一个尺度。**多分辨率分析**系统地扫描分辨率参数，观察社团结构随尺度的变化，并寻找“稳健”的尺度。

常用的判断依据：

- **平台**：社团数在一段较宽的 $\gamma$ 区间内保持不变，提示该尺度上存在清晰结构；
- **稳定性**：同一 $\gamma$ 下多次运行（不同随机种子）得到的划分两两之间的相似度（ARI 或 NMI 的平均值）较高；
- **与零模型的差距**：同一 $\gamma$ 下，真实网络的 $Q_\gamma$ 明显高于保度随机网络。

在空手道网络上，$\gamma=0.5$ 时 50 次运行几乎都得到同一个两社团划分（平均两两 ARI 约 0.98）；随 $\gamma$ 增大，社团增多、稳定性下降（[代码示例](community-structure.html#code)）。

### 共识聚类

由于模块度平台的存在，同一个算法多次运行会得到许多“差不多好”的不同划分。**共识聚类**（consensus clustering）把它们整合成一个更稳定的划分（Lancichinetti 与 Fortunato 2012）：

1. 用同一算法（同一参数、不同随机种子）运行 $n_P$ 次；
2. 计算**共识矩阵** $D_{ij}$：节点 $i,j$ 被分到同一社团的次数比例；
3. 把 $D_{ij}$ 低于阈值 $\tau$ 的元素置零（去掉偶然的同组），以 $D$ 为加权网络再运行 $n_P$ 次算法；
4. 重复第 2–3 步，直到共识矩阵只含 0 和 1（所有运行一致），即得到共识划分。

共识矩阵本身也很有信息量：$D_{ij}$ 接近 0.5 的节点对说明归属不确定；一个节点与本社团其他成员的平均 $D_{ij}$ 可以作为其“归属一致度”。在功能脑网络分析中，常用共识划分来定义群组水平的功能系统（Bassett 等 2013 也讨论了共识方法在多层网络中的用法）。

**多分辨率共识**：Jeub 等（2018）进一步在一系列分辨率上采样划分，构造跨尺度的共识矩阵，再从中提取一组层次化、彼此嵌套的共识划分，避免“选一个 $\gamma$”的主观性。

::: {.callout-warn}
共识聚类提高的是**稳定性**，不是**正确性**：若算法系统性地偏向某种错误划分（例如因分辨率极限合并了小社团），共识只会让错误更“稳定”。共识矩阵的阈值 $\tau$ 与运行次数 $n_P$ 也需要报告，并检查结果对它们是否敏感。
:::

## 多层与时变网络的社团 {#multilayer-temporal}

### 多层模块度

当同一组节点之间有多种关系（多组学网络、多频段脑网络），或网络随时间变化（逐个时间窗估计的功能连接），可以把它们组织为**多层网络**：每层是一个网络，同一节点在不同层的副本之间用**层间边**相连。Mucha 等（2010）把模块度推广到多层网络：
$$
Q_{\text{ML}}=\frac{1}{2\mu}\sum_{ijsr}\left[\left(A_{ijs}-\gamma_s\frac{k_{is}k_{js}}{2m_s}\right)\delta_{sr}+\delta_{ij}\,C_{jsr}\right]\delta(g_{is},g_{jr}),
$$
其中 $A_{ijs}$ 是第 $s$ 层的邻接矩阵，$g_{is}$ 是节点 $i$ 在第 $s$ 层的社团标签，$C_{jsr}$ 是节点 $j$ 在层 $s$ 与 $r$ 之间的耦合强度（时变网络中通常只连相邻时间层，取常数 $\omega$），$2\mu$ 为所有层内边权与层间耦合的总和。$\gamma$ 控制每层内的分辨率，$\omega$ 控制层与层之间划分的一致程度：$\omega=0$ 时各层独立划分；$\omega\to\infty$ 时所有层被迫取相同划分。

实现上，可以把整个多层网络写成一个 $nT\times nT$ 的超模块度矩阵，用 Louvain 式的局部移动与聚合直接优化（如 GenLouvain）。动态脑网络中更多的实现细节与应用见[动态功能连接与多层脑网络](dynamic-brain-networks.multilayer.html)。

### 由时变划分派生的指标

- **灵活性**（flexibility，Bassett 等 2011）：节点在相邻时间层之间改变社团归属的比例；
- **招募与整合系数**：节点与同一先验系统（或不同系统）的节点被分到同一社团的频率；
- **社团的生存与演化**：追踪社团在时间上的分裂、合并、生长、收缩、出现与消失。

在[代码示例](community-structure.html#code)的人工时变网络中，8 个节点在第 4 个时间层“换队”。$\omega=1$ 时，它们的灵活性恰为 $1/5$（6 层中只换了一次），其余节点为 0；$\omega=0.05$ 时各层的社团标签在层间“乱跳”，灵活性被夸大；$\omega=20$ 时所有层被迫取同一划分，换队完全被掩盖。

::: {.callout-warn}
$\omega$ 与 $\gamma$ 的取值没有公认标准，灵活性等指标对它们很敏感。Bassett 等（2013）建议同时与三类零模型比较：打乱层内连边（连接零模型）、打乱节点的层间对应（节点零模型）、打乱层的时间顺序（时间零模型），只有显著偏离零模型的动态结构才值得解释。
:::

### 社团演化的经验规律

Palla、Barabási 与 Vicsek（2007）在合作网络和通话网络中追踪团渗流社团的演化，识别出生长、收缩、合并、分裂、诞生和消亡六种基本事件。他们发现社团的年龄与规模正相关；大社团若能不断更新成员则存续更久，而小社团的存续依赖成员的稳定。Barabási《Network Science》第 9 章还总结了其他社会网络研究的规律：节点加入某社团的概率随它与该社团成员的连边数增加；与社团联系少的成员更容易离开。这些结论来自社会系统，在生物系统中社团如何演化（如发育、疾病进展中的模块重组）仍了解有限。

## 社团发现方法的比较 {#method-comparison}

| 方法 | 核心思想 | 速度 | 需要预设社团数？ | 适用情形 |
|---|---|---|---|---|
| Girvan–Newman | 反复删除边介数最大的边 | 慢，$O(m^2n)$ | 否（按 $Q$ 选层） | 小网络、概念演示、需要完整层次 |
| 贪心模块度（CNM） | 逐步合并使 $Q$ 增加最多的社团对 | 快 | 否 | 历史方法；倾向于形成大社团 |
| Louvain | 局部移动 + 聚合，贪心优化 $Q$ | 很快，近线性 | 否（可调分辨率） | 大网络；注意可能出现连接不良的社团 |
| Leiden | Louvain + 细化，保证社团连通 | 很快 | 否（可选模块度或 CPM） | 大网络的默认选择 |
| 模块度谱方法 | 模块度矩阵的主特征向量 | 中等 | 否（递归二分） | 中等规模，结果确定 |
| 拉普拉斯谱聚类 | 拉普拉斯矩阵特征向量 + k 均值 | 中等 | 是 | 已知社团数的情形 |
| Bethe Hessian / 非回溯谱 | 稀疏网络中不局域化的谱 | 中等 | 可由负特征值个数估计 | 稀疏网络、接近可检测阈值 |
| 层次聚类（Ravasz、WGCNA） | 相似度 + 逐步合并 | 中等 | 剪枝高度需选择 | 加权网络、共表达网络 |
| 标签传播 | 节点采用邻居中最多的标签 | 极快 | 否 | 超大网络的粗略划分；不稳定 |
| 随机块模型（DC-SBM，贝叶斯） | 生成模型 + 后验推断 | 较慢（MCMC） | 否（模型选择） | 需要统计证据、非同配结构或不确定性估计 |
| Infomap | 最小化随机游走描述长度 | 快 | 否 | 有向、加权、以“流”为意义的网络 |
| 团渗流（CFinder） | 相邻 $k$-团的并 | 视网络而定 | 需选 $k$ | 重叠社团、富含三角形的网络 |
| 连边聚类 | 对边做层次聚类 | 中等 | 由划分密度确定 | 重叠且层次化的社团 |
| 多层模块度 | 层内模块度 + 层间耦合 | 中等 | 否（需选 $\gamma,\omega$） | 时变或多关系网络 |

选择方法的几条经验：

1. **先明确问题**：要描述网络（描述性）还是要检验“是否存在分组、有多少组”（推断性）？要找同配社团还是一般的分块结构？节点能否属于多个社团？
2. **网络的类型**：有向且以流动为意义时考虑 Infomap；稀疏且信号弱时注意可检测性；加权的相关网络（共表达、功能连接）中，先想清楚负权与阈值的处理。
3. **至少用两类方法**：例如 Leiden（模块度或 CPM）与 DC-SBM 或 Infomap 对照。若结论只在一种方法下成立，应谨慎解释。

## 划分比较与基准检验 {#partition-comparison}

### 怎样比较两个划分

评价算法、检查稳定性、与已知分组对照，都需要量化两个划分 $X$、$Y$ 的相似程度。设 $n$ 个节点，$n_{xy}$ 为同时属于 $X$ 中社团 $x$ 与 $Y$ 中社团 $y$ 的节点数（列联表），$n_x$、$n_y$ 为边际和。

::: {.callout-def}
- **归一化互信息**（NMI，Danon 等 2005）：$I(X;Y)=\sum_{xy}\frac{n_{xy}}{n}\log\frac{n_{xy}\,n}{n_xn_y}$，
$$
\text{NMI}(X,Y)=\frac{2I(X;Y)}{H(X)+H(Y)},
$$
$H$ 为划分的熵。两划分相同时为 1，独立时为 0。
- **调整兰德指数**（ARI，Hubert 与 Arabie 1985）：统计“节点对”的一致性——两个划分是否都把这对节点放在同组（或都分开），再减去随机期望并归一化：
$$
\text{ARI}=\frac{\sum_{xy}\binom{n_{xy}}{2}-\left[\sum_x\binom{n_x}{2}\sum_y\binom{n_y}{2}\right]\big/\binom n2}{\frac12\left[\sum_x\binom{n_x}{2}+\sum_y\binom{n_y}{2}\right]-\left[\sum_x\binom{n_x}{2}\sum_y\binom{n_y}{2}\right]\big/\binom n2}.
$$
完全一致为 1，随机划分的期望为 0，可以为负。
- **信息变差**（VI，Meilă 2007）：$\text{VI}=H(X)+H(Y)-2I(X;Y)$，是划分空间中的一个真正的距离（满足三角不等式），完全一致时为 0。
:::

**手算例**：6 个节点，真实划分 $\{0,1,2\}\{3,4,5\}$，检测划分 $\{0,1\}\{2,3,4,5\}$（节点 2 被放错）。列联表为 $\begin{pmatrix}2&1\\0&3\end{pmatrix}$。$H(X)=1$ 比特，$H(Y)=-\frac13\log_2\frac13-\frac23\log_2\frac23\approx0.918$，联合熵 $\approx1.459$，故 $I\approx0.459$，$\text{NMI}\approx0.479$，$\text{VI}=1$ 比特。ARI：$\sum\binom{n_{xy}}2=1+3=4$，$\sum\binom{n_x}2=6$，$\sum\binom{n_y}2=7$，$\binom62=15$，期望 $=42/15=2.8$，$\text{ARI}=(4-2.8)/(6.5-2.8)\approx0.324$。一个节点放错就让 ARI 降到 0.32，说明它在小网络上相当严格。

::: {.callout-warn}
NMI 对社团数敏感：把 200 个节点**随机**分成 50 组，与真实的 4 组划分之间的 NMI 平均约为 0.17，而 ARI 约为 0（[代码示例](community-structure.html#code)）。比较社团数相差很大的划分时，应使用 ARI、经过机会校正的调整互信息（AMI），或同时报告社团数。此外，NMI 有多种归一化方式（算术平均、几何平均、最大值），报告时要写明。
:::

### 基准网络

要判断算法能否找到“正确”的社团，需要事先知道答案的人工网络：

- **GN 基准**（Girvan 与 Newman 2002）：128 个节点分成 4 组、每组 32 个，平均度 16；改变组外连边的比例，观察算法何时失效。缺点是所有节点度相近、所有社团等大，与真实网络差距大。
- **LFR 基准**（Lancichinetti、Fortunato 与 Radicchi 2008）：节点度和社团大小都服从幂律分布，更接近真实网络。**混合参数** $\mu$ 是每个节点连向社团外的边所占的比例；$\mu$ 越大，社团越难识别。NetworkX 提供 `LFR_benchmark_graph`。
- **种植划分 SBM**：便于与可检测性理论对照。

Lancichinetti 与 Fortunato（2009）在 GN 与 LFR 基准上比较了十余种算法，Infomap 与 Louvain 等方法表现最好；贪心模块度在 LFR 上表现较差。[代码示例](community-structure.html#code)在 1000 个节点、平均度 20 的 LFR 网络上复现了类似规律：$\mu\le0.3$ 时 Louvain、Leiden 与标签传播的 NMI 接近 1，贪心模块度已明显下降；$\mu=0.4$ 时标签传播塌缩为单一社团；$\mu\ge0.6$ 时所有算法都接近失效。

### 元数据不是金标准

在真实网络上，人们常把节点元数据（已知复合物、GO 注释、脑区的解剖分区、空手道俱乐部的两派）当作“真实划分”。Peel、Larremore 与 Clauset（2017）指出这样做有三个问题：元数据可能与网络结构无关；可能与网络中的**另一种**结构相关；网络中也可能同时存在多个合理的划分。他们证明了一个“没有免费午餐”定理：不存在对所有网络都最优的社团发现算法。算法结果与元数据不一致时，不能直接断定算法错了；反之，一致也不能证明算法“正确”。更好的做法是把元数据作为待检验的假设，例如用带元数据的 SBM 检验它是否解释了网络结构。

## 社团结果的验证与解读 {#validation}

找到社团只是第一步，更重要的是判断它是否可靠、有什么含义。

1. **显著性**：把实际网络的 $Q$ 与大量保度随机网络上得到的 $Q$ 比较。若随机网络的 $Q$ 也差不多，说明“社团”可能只是随机涨落。推断性方法（贝叶斯 SBM）则直接比较“有结构”与“无结构”模型的后验证据。
2. **稳定性**：用不同随机种子、不同算法、不同分辨率参数重复运行，看节点的归属是否一致。可以统计任意两个节点被分到同一社团的频率（[共识矩阵](community-structure.multiresolution-consensus.html)）。还可以对数据做扰动（删去一部分边、对样本做自助抽样后重建网络），检查社团对测量误差是否稳健。
3. **与已知分组比较**：若有参考分组（例如已知的蛋白复合物或脑功能系统划分），可以用 NMI 或 ARI 量化一致程度，但要注意[元数据不是金标准](community-structure.partition-comparison.html)。
4. **生物学验证**：对每个社团中的基因做功能富集分析（如 GO、KEGG 通路），检验社团是否对应特定的生物学过程；在脑网络中，检验社团是否对应已知的功能系统。富集检验的背景基因集应是网络中的全部节点，而不是全基因组，否则网络本身的选择偏倚会制造虚假富集。
5. **社团之间的关系与节点角色**：见下文。

### 节点角色：模块内度与参与系数

Guimerà 与 Amaral（2005）用两个量刻画节点在社团结构中的角色：

::: {.callout-def}
- **模块内度 $z$ 分数**：$z_i=\dfrac{\kappa_i-\bar\kappa_{s_i}}{\sigma_{\kappa_{s_i}}}$，$\kappa_i$ 为节点 $i$ 连向本社团 $s_i$ 的边数，$\bar\kappa_{s_i}$、$\sigma_{\kappa_{s_i}}$ 为本社团所有节点 $\kappa$ 的均值与标准差。
- **参与系数**：$P_i=1-\sum_s\left(\dfrac{k_{is}}{k_i}\right)^2$，$k_{is}$ 为 $i$ 连向社团 $s$ 的边数。所有边都在本社团内时 $P_i=0$；边均匀分布在各社团时 $P_i$ 接近 1。
:::

他们把 $z\ge2.5$ 的节点称为**枢纽**，再按 $P$ 把节点分为 7 种角色：非枢纽中的极端外围（R1，$P\le0.05$）、外围（R2）、非枢纽连接者（R3）、非枢纽无归属节点（R4，$P>0.80$）；枢纽中的局部枢纽（R5，$P\le0.30$）、连接枢纽（R6）、无归属枢纽（R7，$P>0.75$）。这一“功能制图”在脑网络中被广泛用来区分“社团内枢纽”和“连接枢纽”（见[脑连接组：结构与功能连接](brain-connectome.html)）。

::: {.callout-warn}
$z$ 与 $P$ 都依赖于所用的划分；划分不稳定时，节点角色也不稳定。阈值 2.5、0.30、0.62 等是在较大的代谢网络上经验确定的，在小网络中可能没有节点能达到枢纽门槛（如空手道网络中 $z$ 最高的节点 33 只有约 2.3），直接套用会得出“没有枢纽”的误导性结论。
:::

### 社团的统计刻画

- **社团大小分布**：许多真实网络的社团大小分布呈长尾，少数大社团与大量小社团共存。但不同算法给出的大小分布可能截然不同：Barabási《Network Science》第 9 章以电网为例，基于模块度的算法给出大小相近的社团，而 Ravasz 算法与 Infomap 给出大量小社团加少数大社团。这部分源于模块度的分辨率极限，说明社团大小分布本身也是算法依赖的。
- **社团与边权**：在社会网络中，强关系多在社团内部（Onnela 等 2007）；在其他系统中需要具体检验。

::: {.callout-bio}
**层次模块化**：Ravasz 等（2002，*Science*）分析 43 种生物的代谢网络，发现它们同时具有高聚集系数、长尾度分布，以及“度越高的节点聚集系数越低”（$C(k) \sim k^{-1}$）的特征。他们用层次模块化的结构解释这一现象：小而紧密的模块组合成更大、更松散的模块，再逐级组合。用层次聚类得到的模块与已知的代谢功能类别（如碳水化合物代谢、核苷酸代谢）有明显的对应关系。
:::

## 数学推导与算法 {#derivations}

本节把[模块度](community-structure.modularity.html)、[Louvain 与 Leiden 算法](community-structure.louvain-leiden.html)、[谱方法](community-structure.spectral-hierarchical.html)、[随机块模型](community-structure.stochastic-block-model.html)、[映射方程](community-structure.infomap.html)、[可检测性](community-structure.detectability.html)和[团渗流](community-structure.overlapping-communities.html)中只陈述的结果完整推一遍。记号：$A$ 为无向无权网络的邻接矩阵（加权网络把 $A_{ij}$ 换成边权、$k_i$ 换成强度即可），$k_i=\sum_j A_{ij}$ 为节点 $i$ 的度，$m=\frac12\sum_i k_i$ 为边数，$n$ 为节点数。

### A. 从模块度到谱二分（Newman 2006）

**第 1 步：把 $\delta$ 函数写成 $\pm1$ 变量。** 二分时令 $s_i\in\{+1,-1\}$ 表示节点 $i$ 在哪一侧。两点同侧时 $s_is_j=1$，异侧时 $s_is_j=-1$，所以
$$
\delta(c_i,c_j)=\tfrac12(1+s_is_j).
$$

**第 2 步：代入模块度。** 记模块度矩阵 $B_{ij}=A_{ij}-\dfrac{k_ik_j}{2m}$，则
$$
Q=\frac{1}{2m}\sum_{ij}B_{ij}\cdot\frac{1+s_is_j}{2}
=\frac{1}{4m}\sum_{ij}B_{ij}+\frac{1}{4m}\sum_{ij}B_{ij}s_is_j .
$$
$B$ 的每一行之和为零：$\sum_j B_{ij}=k_i-\dfrac{k_i\cdot 2m}{2m}=0$。所以第一项消失，得到 $Q=\dfrac{1}{4m}\mathbf s^\top B\mathbf s$。这一步是精确的。

**第 3 步：特征分解。** $B$ 是实对称矩阵，有正交归一的特征向量 $\mathbf u_1,\dots,\mathbf u_n$，对应特征值 $\beta_1\ge\beta_2\ge\cdots\ge\beta_n$。把 $\mathbf s$ 展开为 $\mathbf s=\sum_l a_l\mathbf u_l$，$a_l=\mathbf u_l^\top\mathbf s$，则
$$
Q=\frac{1}{4m}\sum_{l=1}^{n}a_l^2\,\beta_l,\qquad \sum_l a_l^2=\mathbf s^\top\mathbf s=n .
$$

**第 4 步：放松与取整（近似在这里进入）。** 若 $\mathbf s$ 可以是任意实向量（只保留 $\mathbf s^\top\mathbf s=n$），把全部“权重”$n$ 放到最大特征值上即可使 $Q$ 最大，即 $\mathbf s\propto\mathbf u_1$。但 $s_i$ 只能取 $\pm1$，退而求其次：让 $a_1=\mathbf u_1^\top\mathbf s=\sum_i u_{1i}s_i$ 尽量大，显然取 $s_i=\operatorname{sign}(u_{1i})$。这是启发式，不保证全局最优；Newman 建议之后再做一轮“逐个翻转节点、保留使 $Q$ 增加的翻转”的局部微调。

**第 5 步：何时停止。** 因为 $B\mathbf 1=\mathbf 0$，全 1 向量总是特征值为 0 的特征向量。若 $\beta_1\le 0$（没有正特征值），任何二分都不能让 $Q$ 超过“不分”的 0，网络被判为**不可再分**。

**第 6 步：递归细分。** 对已有社团 $g$ 再二分时，$Q$ 的增量为 $\Delta Q=\frac{1}{4m}\mathbf s^\top B^{(g)}\mathbf s$，其中
$$
B^{(g)}_{ij}=B_{ij}-\delta_{ij}\sum_{l\in g}B_{il},\qquad i,j\in g ,
$$
对角修正项保证 $B^{(g)}$ 的行和也为零。用 $B^{(g)}$ 的主特征向量重复第 4、5 步，直到所有社团都不可再分。

```text
算法 1  模块度谱二分（递归版）
输入：网络 G；输出：社团划分 P
1. P ← {V}；待处理队列 S ← {V}
2. while S 非空:
3.     取出 g；构造 B^(g)（不显式存储，见下）
4.     用 Lanczos/幂迭代求 B^(g) 的最大特征值 β1 与特征向量 u1
5.     if β1 ≤ 0（数值容差内）: g 不可再分，continue
6.     s_i ← sign(u1_i)；可选：逐点翻转微调 s
7.     ΔQ ← sᵀ B^(g) s / (4m)
8.     if ΔQ ≤ 0: continue
9.     按 s 把 g 分成 g+、g−，在 P 中替换 g；把 g+、g− 加入 S
10. return P
```

复杂度：$B$ 是稠密矩阵，但不必存储。$B\mathbf x=A\mathbf x-\mathbf k\,(\mathbf k^\top\mathbf x)/2m$，一次乘法只需 $O(m+n)$。每次二分需要若干次乘法（次数取决于特征值间隙）；Newman（2006）估计稀疏网络上整个递归过程约为 $O(n^2\log n)$。

### B. Louvain 局部移动的 $\Delta Q$

用按社团求和的形式 $Q=\sum_c\left[\frac{l_c}{m}-\left(\frac{d_c}{2m}\right)^2\right]$（$l_c$：社团内部边数；$d_c$：社团度之和）。设节点 $i$ 当前独自成一个社团（贡献 $-(k_i/2m)^2$），记 $k_{i,C}$ 为 $i$ 连向社团 $C$ 的边数。把 $i$ 并入 $C$ 后，$l_C\to l_C+k_{i,C}$，$d_C\to d_C+k_i$，$i$ 自身的那一项消失：
$$
\Delta Q_{i\to C}=\frac{k_{i,C}}{m}-\frac{(d_C+k_i)^2-d_C^2-k_i^2}{4m^2}
=\frac{k_{i,C}}{m}-\frac{k_i\,d_C}{2m^2}.
$$
一般情形：节点 $i$ 从社团 $D$ 移到 $C$，可看作“先移出成为孤点、再并入”，记 $D'=D\setminus\{i\}$，
$$
\Delta Q_{D\to C}=\frac{k_{i,C}-k_{i,D'}}{m}-\frac{k_i\,(d_C-d_{D'})}{2m^2}.
$$
含义：第一项是“连向 $C$ 比连向原社团多出的边”，第二项是零模型下的期望惩罚。带分辨率参数 $\gamma$ 时第二项乘以 $\gamma$。这个公式只需要 $i$ 的邻居信息和每个社团的 $d_c$，所以一次扫描全部节点的代价为 $O(m)$。（聚合后的超节点带自环，自环随节点一起移动，公式形式不变。）

```text
算法 2  Louvain（一轮"局部移动 + 聚合"）
1. 每个节点自成社团；记录每个社团的 d_c
2. repeat
3.     improved ← false
4.     for 节点 i（随机顺序）:
5.         统计 i 连向各邻居社团的边数 k_{i,C}
6.         对每个邻居社团 C 计算 ΔQ_{D→C}；取最大者 C*
7.         if ΔQ_{D→C*} > 0: 移动 i，更新 d_D、d_{C*}；improved ← true
8. until not improved
9. 每个社团压缩为超节点，社团间边权相加，社团内边变为自环
10. 若第 9 步后社团数未减少则停止，否则在新网络上回到第 1 步
```

复杂度：每次扫描 $O(m)$；扫描次数和层数没有严格的理论上界，经验上整体接近线性。第 7 步只接受严格增益，保证 $Q$ 单调上升、算法终止；但只能到达局部最优，结果依赖访问顺序。

**推广到任意质量矩阵**：若质量函数可写成 $\sum_{ij}M_{ij}\delta(g_i,g_j)$（$M$ 对称，如多层模块度的超模块度矩阵），则把节点 $i$ 从 $D$ 移到 $C$ 的增量为 $2\left(\sum_{j\in C}M_{ij}-\sum_{j\in D'}M_{ij}\right)$，聚合时 $M\to Z^\top MZ$（$Z$ 为节点–社团指示矩阵）。这就是 GenLouvain 一类实现的核心，[代码示例](community-structure.html#code)的多层模块度即用此法。

### C. Leiden 算法的流程

```text
算法 3  Leiden（一层）
输入：网络 G，初始划分 P；输出：新划分
1. 快速局部移动：队列 Q ← 全部节点（随机顺序）
2.     while Q 非空: 取出 v，移到增益最大的社团（含空社团）；
3.         若 v 移动了，把 v 的不在 Q 中、且不属于 v 新社团的邻居加入 Q
4. 细化：对 P 中每个社团 C，令 P_ref 在 C 内从单点开始；
5.     对 C 中仍为单点、且与 C 其余部分连接足够好的节点 v（随机顺序）：
6.         在 C 内与 v 相连、且自身与 C 连接足够好的子社团中，
7.         以概率 ∝ exp(ΔH/θ)（只考虑 ΔH ≥ 0）选择一个并入
8. 聚合：以 P_ref 的子社团为超节点建聚合网络；初始划分取 P（每个超节点归入其母社团）
9. 若 P 中每个社团都只含一个 P_ref 子社团（不再变化），停止；否则在聚合网络上回到第 1 步
```

“连接足够好”的判据与质量函数有关：以 CPM 为例，要求子集 $S$ 与 $C\setminus S$ 之间的边数不少于 $\gamma\,\|S\|\cdot(\|C\|-\|S\|)$。第 7 步的随机性让细化可以探索更多可能的子社团；$\theta\to0$ 时退化为贪心选择。

### D. 分辨率极限的推导要点

把局部移动的方法用于“合并两个社团 1、2”：设它们之间有 $l_{12}$ 条边，度之和为 $d_1,d_2$，则
$$
\Delta Q_{\text{merge}}=\frac{l_{12}}{m}-\frac{d_1d_2}{2m^2}.
$$
只要 $l_{12}\ge1$ 且 $d_1d_2<2m\,l_{12}$，合并就会提高 $Q$。取 $l_{12}=1$、$d_1=d_2=d$：当 $d<\sqrt{2m}$ 时，模块度最大化**倾向于**把两个哪怕内部完全连通的小团合并。

经典例子（Fortunato 与 Barthélemy 2007）：$n_c$ 个 $K_k$ 完全子图连成环，相邻两团之间只有 1 条边。每团 $d=k(k-1)+2$，$m=n_c\left[\frac{k(k-1)}{2}+1\right]$。代入 $d^2<2m$ 得：当 $n_c>k(k-1)+2$ 时，把相邻两团合并的 $Q$ 更高。例如 $k=5$ 时，只要环上超过 22 个团，最大模块度划分就不再把每个团单独作为社团。[代码示例](community-structure.html#code)中，10 个 $K_5$ 时“每团一社团”的 $Q=0.809$ 高于两两合并的 0.755；30 个 $K_5$ 时则反过来（0.876 对 0.888）。

**CPM 为何没有分辨率极限**：对 CPM，合并社团 1、2 的增量为 $\Delta H=l_{12}-\gamma n_1n_2$，只依赖两个社团自身，与网络其余部分无关。两个 $K_5$ 之间 $l_{12}=1$、$n_1n_2=25$，只要 $\gamma>1/25$ 就不会合并，与团数无关。

::: {.callout-warn}
上述推导只说明“合并能提高 $Q$”，并没有证明全局最优解一定合并；它也假设两社团之间的连接数和度之和已知。要点是：判据 $d<\sqrt{2m}$ 中出现的是**全网**边数 $m$，因此“小”是相对于整个网络而言的——同一个蛋白复合物，放在更大的相互作用组里就可能被吞并。
:::

### E. 划分数目的估计

等大二分数用 Stirling 公式 $N!\approx\sqrt{2\pi N}(N/e)^N$：
$$
\binom{N}{N/2}=\frac{N!}{[(N/2)!]^2}\approx\frac{\sqrt{2\pi N}\,(N/e)^N}{\pi N\,(N/2e)^N}=\frac{2^N\sqrt{2}}{\sqrt{\pi N}}=\frac{2^{N+1}}{\sqrt{2\pi N}}.
$$
Bell 数的递推来自“考察包含节点 $N+1$ 的那个组”：若该组另含 $N-j$ 个其他节点（$\binom{N}{N-j}=\binom Nj$ 种选法），其余 $j$ 个节点任意划分（$B_j$ 种），故 $B_{N+1}=\sum_j\binom NjB_j$。$B_N$ 的增长快于任何 $c^N$：粗略地，$\ln B_N\sim N\ln N$。

### F. SBM 与 DC-SBM 的轮廓似然（Karrer 与 Newman 2011）

**DC-SBM**：$A_{ij}\sim\text{Poisson}(\theta_i\theta_j\omega_{b_ib_j})$（$i<j$；自环另计，此处略），对数似然（略去与参数无关的项）
$$
\ln P(A\mid\theta,\omega,\mathbf b)=\sum_i k_i\ln\theta_i+\frac12\sum_{rs}\left(m_{rs}\ln\omega_{rs}-\omega_{rs}\sum_{i\in r}\theta_i\sum_{j\in s}\theta_j\right),
$$
$m_{rs}=\sum_{ij}A_{ij}\delta_{b_i,r}\delta_{b_j,s}$（$r=s$ 时为组内边数的 2 倍）。$\theta$ 有尺度不确定性，加约束 $\sum_{i\in r}\theta_i=1$（对每个组）。在此约束下对 $\theta_i$ 求极大得 $\hat\theta_i=k_i/\kappa_r$（$\kappa_r=\sum_{i\in r}k_i$），对 $\omega_{rs}$ 求极大得 $\hat\omega_{rs}=m_{rs}$。代回并去掉常数，得到只依赖划分的轮廓对数似然
$$
\mathcal L_{\text{DC}}(\mathbf b)=\sum_{rs}m_{rs}\ln\frac{m_{rs}}{\kappa_r\kappa_s}.
$$
**标准 SBM** 相当于所有 $\theta_i$ 相同，同理得到 $\mathcal L_{\text{SBM}}=\sum_{rs}m_{rs}\ln\frac{m_{rs}}{n_rn_s}$。

二者的差别一目了然：DC-SBM 用组的**度之和** $\kappa_r$ 做归一化，标准 SBM 用组的**节点数** $n_r$。前者把“度高”归因于节点参数 $\theta_i$，后者只能把度的差异归因于分组，因此在度异质的网络中会按度分组。

**与模块度的对应**（Newman 2016 的要点）：若限定 $\omega_{rr}=\omega_{\text{in}}$、$\omega_{rs}=\omega_{\text{out}}$（$r\ne s$），并取 $\theta_i=k_i$（期望度等于观测度），对数似然中依赖划分的部分为
$$
\frac12\sum_{ij}\left[A_{ij}\ln\frac{\omega_{\text{in}}}{\omega_{\text{out}}}-\frac{k_ik_j}{2m}\cdot 2m(\omega_{\text{in}}-\omega_{\text{out}})\right]\delta(b_i,b_j)
\;\propto\;\sum_{ij}\left[A_{ij}-\gamma\frac{k_ik_j}{2m}\right]\delta(b_i,b_j),
$$
其中 $\gamma=\dfrac{\omega_{\text{in}}-\omega_{\text{out}}}{\ln\omega_{\text{in}}-\ln\omega_{\text{out}}}$（$\omega$ 已按 $2m$ 归一化）。也就是说，最大化 $Q_\gamma$ 就是在这个受限模型下做最大似然；交替地“固定划分估计 $\omega_{\text{in}},\omega_{\text{out}}$、再更新 $\gamma$ 与划分”，就得到一个由数据决定 $\gamma$ 的迭代方案。

```text
算法 4  DC-SBM 的贪心最大似然（固定组数 B，多次随机重启）
1. for restart = 1..R:
2.     随机初始化 b
3.     repeat
4.         for 节点 i（随机顺序）: 把 i 移到使 L_DC 最大的组（只增益时移动）
5.     until 无移动
6.     记录 L_DC(b)
7. 返回 L_DC 最大的 b
```
Karrer 与 Newman 使用类似 Kernighan–Lin 的启发式（允许暂时降低似然的强制移动）以跳出局部最优；贝叶斯版本则用 MCMC 在划分空间中抽样。

### G. 映射方程的展开

对两层编码，索引码本中各模块码字的使用频率正比于进入概率 $q_i$，模块 $i$ 的码本中各码字（模块内节点与退出码）的使用频率正比于 $p_\alpha$（$\alpha\in i$）与 $q_i$。由 Shannon 信源编码定理，
$$
H(\mathcal Q)=-\sum_i\frac{q_i}{q}\log_2\frac{q_i}{q},\qquad
H(\mathcal P_i)=-\frac{q_i}{p_i}\log_2\frac{q_i}{p_i}-\sum_{\alpha\in i}\frac{p_\alpha}{p_i}\log_2\frac{p_\alpha}{p_i},
$$
其中 $q=\sum_iq_i$，$p_i=q_i+\sum_{\alpha\in i}p_\alpha$。代入 $L=qH(\mathcal Q)+\sum_ip_iH(\mathcal P_i)$ 并记 $\eta(x)=x\log_2x$，整理得
$$
L(M)=\eta(q)-2\sum_i\eta(q_i)-\sum_\alpha\eta(p_\alpha)+\sum_i\eta(p_i).
$$
第三项与划分无关（节点访问分布的熵），只有含 $q_i$ 与 $p_i$ 的三项随划分变化，而它们都只依赖于每个模块的退出流和总访问量，因此移动一个节点后的 $\Delta L$ 可以像 $\Delta Q$ 一样局部计算。单一模块时 $q_i=0$，$L=-\sum_\alpha\eta(p_\alpha)$，即节点访问分布的熵。

对无向网络，$p_\alpha=k_\alpha/2m$；模块 $i$ 的退出概率 $q_i$ 等于随机游走者某一步从 $i$ 内部走到外部的概率，即 $\sum_{\alpha\in i}p_\alpha\cdot\frac{k_\alpha^{\text{ext}}}{k_\alpha}=\frac{1}{2m}\sum_{\alpha\in i}k_\alpha^{\text{ext}}$。有向网络需先用带传送的随机游走（传送概率常取 0.15）求稳态分布。

### H. 可检测性阈值的直观推导

以 $q=2$ 为例给出一个启发式论证（严格结果见 Decelle 等 2011）。设每个节点有 $c$ 个邻居（稀疏极限下邻域是树状的）。把节点的组标签 $\sigma_i=\pm1$ 看作沿树传播的“信号”：沿一条边走一步，标签保持不变的概率为 $c_{\text{in}}/(c_{\text{in}}+c_{\text{out}})$，因此相关性每步乘以
$$
\lambda=\frac{c_{\text{in}}-c_{\text{out}}}{c_{\text{in}}+c_{\text{out}}}=\frac{c_{\text{in}}-c_{\text{out}}}{2c}.
$$
距离根节点 $d$ 步处约有 $c^d$ 个节点，每个携带的关于根标签的相关性为 $\lambda^d$。把它们“投票”汇总，信号量级为 $c^d\lambda^d$，而随机涨落的量级为 $\sqrt{c^d}$。信号压过噪声的条件是 $c^d\lambda^d\gg c^{d/2}$，即
$$
c\lambda^2>1\iff |c_{\text{in}}-c_{\text{out}}|>2\sqrt c ,
$$
与 $q=2$ 时的阈值一致（一般 $q$ 时 $\lambda=\frac{c_{\text{in}}-c_{\text{out}}}{qc}$，得 $|c_{\text{in}}-c_{\text{out}}|>q\sqrt c$）。这一条件也正是非回溯矩阵中携带社团信息的特征值 $\frac{c_{\text{in}}-c_{\text{out}}}{q}$ 从噪声谱的半径 $\sqrt c$ 中分离出来的条件，所以非回溯谱方法恰好在阈值处开始有效。

### I. 团渗流阈值

在 ER 网络 $G(N,p)$ 中滚动一个 $k$-团模板：每次保留 $k-1$ 个节点、把第 $k$ 个节点换到别处。可选择留下的 $k-1$ 个节点中哪一个作为下次移动的“支点”，约有 $k-1$ 种；新节点约有 $N-k-1\approx N$ 个候选位置；新节点必须与留下的 $k-1$ 个节点全部相连，概率为 $p^{k-1}$。渗流阈值处，每次滚动产生的“下一个相邻 $k$-团”的期望数应恰好为 1（类似分支过程的临界条件）：
$$
(k-1)\,N\,p_c^{\,k-1}=1\quad\Longrightarrow\quad p_c(k)=\frac{1}{[(k-1)N]^{1/(k-1)}} .
$$
期望小于 1 时，滚动很快停止，$k$-团社团的规模呈指数衰减；大于 1 时，出现横跨网络的巨大 $k$-团社团。

### J. 划分比较指标的性质

- **NMI 的上界与偏差**：$I(X;Y)\le\min\{H(X),H(Y)\}$，故 NMI $\le1$。当 $Y$ 的组数很多时，即使 $Y$ 随机，有限样本下的互信息估计也偏正（每组节点很少，列联表稀疏），这是随机多组划分 NMI 虚高的来源；调整互信息（AMI）减去了随机划分下互信息的期望。
- **ARI 的机会校正**：在两个划分的组大小（边际）固定、节点标签随机排列的超几何模型下，$\sum\binom{n_{xy}}2$ 的期望为 $\left[\sum\binom{n_x}2\sum\binom{n_y}2\right]/\binom n2$，ARI 正是减去这一期望后的归一化值，因此随机划分的 ARI 期望为 0。
- **VI 是度量**：$\text{VI}(X,Y)=H(X\mid Y)+H(Y\mid X)$，满足非负性、对称性与三角不等式，上界为 $\log_2 n$。

## 研究前沿与开放问题 {#frontiers}

1. **社团发现有没有“正确答案”？** 用节点元数据（如 GO 注释、已知复合物）当作“金标准”来评价算法，隐含了“元数据 = 网络结构真实分组”的假设。Peel、Larremore 与 Clauset（2017，*Science Advances*）证明不存在对所有网络都最优的社团发现算法，元数据与算法结果不一致时，不能直接断定算法错了。在功能注释本身不完整的生物网络中，怎样评价模块是开放问题。

2. **模块度优化还是统计推断？** 随机块模型（Karrer 与 Newman 2011，*Physical Review E*）把社团发现变为模型拟合，可以做模型选择、给出不确定性；配合贝叶斯模型选择时，可以避免在没有结构的随机网络中“找到”社团；嵌套随机块模型（Peixoto 2014，*Physical Review X*）进一步缓解了分辨率极限。Peixoto（2023）系统论证了描述性与推断性方法的区别；而 Newman（2016）的等价性结果表明二者并非截然对立。两类方法在大规模生物网络上的取舍仍有争论，例如 SBM 对三角形丰富的网络可能“过度分组”，而模块度在稀疏网络中容易报告虚假结构。

3. **哪种模块方法真正找到疾病相关模块？** DREAM 挑战（Choobdar 等 2019，*Nature Methods*）比较了 75 种模块识别方法在多个人类分子网络上的表现，用 GWAS 信号评价模块的疾病相关性。表现较好的方法分属不同类别，各自找到的性状相关模块彼此互补。怎样整合多种网络与方法、怎样评价模块的生物学意义，仍未解决。

4. **随时间变化的模块。** Mucha 等（2010，*Science*）提出多层模块度，可以在时间序列网络中追踪社团的分合；Bassett 等（2011，*PNAS*）用它发现运动学习过程中脑网络模块会动态重组，且重组程度可预测后续学习表现。多层模块度的层间耦合参数如何选取、结果如何做统计检验，目前没有公认标准（见[动态功能连接与多层脑网络](dynamic-brain-networks.html)）；时变与多层 SBM 提供了一种基于模型选择的替代方案。

5. **可检测性与数据质量。** 可检测性理论建立在理想化模型上。真实的分子网络存在大量假阴性（未测到的相互作用）和研究偏倚（研究多的蛋白被测到的相互作用多），这些如何改变“可检测”的边界，以及如何在社团分析中显式建模测量误差（例如把观测网络看作对真实网络的含噪测量），是仍在发展的方向。

6. **高阶结构与社团。** 社团结构可以定义在三角形、基序或超边之上（高阶聚类、超图社团），也可以由带记忆的流动定义（高阶映射方程）。生物系统中大量相互作用是多元的（蛋白复合物、多药联合），这些方法何时比成对网络上的社团更有解释力，尚无定论。

## 生物医学应用 {#biomedical}

**蛋白复合物与功能模块。** Hartwell、Hopfield、Leibler 与 Murray（1999，*Nature*）提出“功能模块”是细胞生物学的基本组织单位：一组相互作用的分子共同完成一项相对独立的功能。在蛋白质相互作用网络中，蛋白复合物和信号通路通常表现为密集连接的子网络。Spirin 与 Mirny（2003，*PNAS*）在酵母蛋白质网络中系统搜索高密度子图，找到的模块大多对应已知的蛋白复合物或功能通路。这类分析的意义在于：一个功能未知的蛋白如果落在某个功能明确的模块中，就可以推测它参与相同的过程（“近朱者赤”的功能预测）。由于一个蛋白常参与多个复合物，[重叠社团](community-structure.overlapping-communities.html)方法（团渗流、连边社团）在 PPI 网络中尤为常用。

**代谢网络的功能制图。** Guimerà 与 Amaral（2005，*Nature*）用模拟退火最大化模块度，划分了三个生物界共 12 种生物的代谢网络，再用模块内度 $z$ 与参与系数 $P$ 把代谢物分为 7 种角色（见[验证与解读](community-structure.validation.html)）。他们发现，连接不同模块的低度代谢物（非枢纽连接者）在物种间比主要连接本模块内部的枢纽更保守——提示“连接者”的角色可能比“度高”更能反映结构上的重要性。

::: {.callout-bio}
**脑网络的功能系统。** Power 等（2011，*Neuron*）在静息态 fMRI 功能网络上，用 Infomap 在一系列连边密度阈值下划分社团，得到的模块与视觉、躯体运动、听觉、默认模式、额顶控制、背侧注意等已知功能系统高度对应，而且这种划分在不同密度阈值下相当稳定。这一划分此后被大量研究用作脑区的“系统标签”，Power 等（2013）又在此基础上用参与系数识别跨系统的连接枢纽。脑网络的模块化程度在发育、衰老和多种精神疾病中会发生改变，但这些结论对网络构建方式和算法参数相当敏感，跨研究比较时要特别留意方法是否一致（Sporns 与 Betzel 2016 的综述）。
:::

**学习与认知中的动态模块。** Bassett 等（2011，*PNAS*）把被试在数天运动学习过程中的功能网络按时间窗组织成多层网络，用多层模块度追踪模块的变化，发现模块组成随学习发生动态重组，且某一阶段脑区的灵活性可以预测之后的学习表现。这类研究的统计检验依赖于与连接、节点、时间三类零模型的比较（见[多层与时变网络的社团](community-structure.multilayer-temporal.html)）。

**疾病模块。** 网络医学的核心假设是：同一种疾病的相关基因在相互作用组中聚集成一个连通的局部区域。需要区分两个概念：**拓扑模块**（社团发现算法找到的密集子网络）与**疾病模块**（疾病基因所在的网络区域），两者有重叠但并不相同——疾病模块不一定恰好对应某一个算法输出的社团（见[疾病模块、网络邻近度与药物重定位](network-medicine.html)）。DREAM 模块识别挑战（Choobdar 等 2019）提示，不同类别的模块方法找到的疾病相关模块彼此互补，单一方法的结果不宜作为唯一依据。

**共表达模块与细胞类型。** WGCNA 用拓扑重叠和层次聚类识别共表达模块（见[基因调控网络推断与共表达分析](gene-network-inference.html)）。单细胞转录组分析中，常见流程是在细胞的 $k$ 近邻图上运行 Louvain 或 Leiden 来定义细胞簇，这里分辨率参数直接决定“细胞类型”划分的粗细，同样需要多分辨率与稳定性分析的支持。

## 适用范围与常见误用 {#limitations}

1. **误区**：模块度越高，社团结构就越“真实”。→ **正解**：随机网络也能得到不低的 $Q$，且 $Q$ 存在分辨率极限和简并性。应把 $Q$ 与保度随机网络的结果比较，并检查划分的稳定性和生物学意义。
2. **误区**：Girvan–Newman 算法只需计算一次边介数，然后按从大到小依次删边。→ **正解**：每删一条边，最短路径都会改变，必须重新计算所有边的边介数。
3. **误区**：Louvain 算法每次运行的结果都相同。→ **正解**：Louvain 和 Leiden 依赖节点访问顺序等随机因素，应固定随机种子以便复现，并通过多次运行评估稳定性。
4. **误区**：社团发现算法找到的社团就是生物学功能模块。→ **正解**：社团是拓扑上的结构，是否对应功能需要通过富集分析、已知复合物或独立数据验证。算法、参数和网络构建方式不同，社团也会不同。
5. **误区**：分辨率参数可以随意调，选一个“看起来最好”的就行。→ **正解**：分辨率决定观察尺度。若根据结果挑参数，结论就带有主观性；应事先确定选择标准，或展示结论在一系列参数下的稳健性。
6. **误区**：Louvain 的社团一定是连通的。→ **正解**：Louvain 可能产生连接不良甚至不连通的社团；应检查每个社团的连通性，或改用 Leiden。
7. **误区**：没找到社团（或与已知分组不一致）说明网络没有模块结构。→ **正解**：在稀疏网络中，信号低于可检测性阈值时任何算法都会失败；同时元数据也不一定对应网络结构。
8. **误区**：用 NMI 比较社团数差别很大的两个划分。→ **正解**：NMI 在组数多时对随机划分也会给出正值，应同时报告 ARI 或 AMI 与社团数。
9. **误区**：在加权相关网络上直接运行为无权图设计的算法。→ **正解**：先决定阈值与负权的处理方式；正负边需要分别建模，不同阈值下的社团结果应一并报告（见[网络构建与统计验证](network-construction.html)）。
10. **误区**：把标准 SBM 用在度高度异质的网络上。→ **正解**：标准 SBM 会按度分组；应使用度修正 SBM，并用模型选择而不是似然大小决定组数。

## 关联知识 {#related}

- [网络结构指标与随机图](network-metrics.html)：聚集系数、最短路径与零模型是模块度和边介数的基础。
- [小世界与无标度网络模型](network-models.html)：保度随机化零模型同样用于检验模块度的显著性；层次模型联系了无标度与模块性。
- [网络构建与统计验证](network-construction.html)：阈值、加权、零模型与稳定性分析决定社团结果是否可信。
- [基因调控网络推断与共表达分析](gene-network-inference.html)：WGCNA 用拓扑重叠与层次聚类识别共表达模块。
- [生物分子网络与拓扑特征](molecular-networks.html)：蛋白复合物、信号通路与功能模块在 PPI 网络中的识别。
- [脑连接组：结构与功能连接](brain-connectome.html)：脑功能系统的社团划分、模块内连接度与参与系数。
- [动态功能连接与多层脑网络](dynamic-brain-networks.html)：多层模块度追踪脑网络模块随时间的重组。
- [疾病模块、网络邻近度与药物重定位](network-medicine.html)：疾病模块与拓扑模块的区别及其在药物重定位中的应用。
- [研究问题、可复现分析与敏感性分析](reproducible-research.html)：随机种子、分辨率参数与算法选择的稳健性报告。

## 核心文献 {#references}

### Girvan & Newman 2002：Community structure in social and biological networks

- **出处**：*PNAS* 99: 7821–7826。DOI：[10.1073/pnas.122653799](https://doi.org/10.1073/pnas.122653799)。论文精读：[Girvan 2002](paper-girvan2002_community.html)
- **背景**：传统的层次聚类从“最相似的节点”开始合并，容易把边缘节点孤立出来；作者转而从“最不像社团内部的边”入手。
- **核心发现**：提出基于边介数的分裂式算法，在计算机生成的有社团网络上验证了效果；在空手道俱乐部网络上基本复现了真实的分裂；在科学家合作网络和海洋食物网中找到了有意义的社团。
- **阅读提示**：本文尚未提出模块度（模块度在 Newman 与 Girvan 2004 年的论文中正式提出，*Phys. Rev. E* 69: 026113，[DOI](https://doi.org/10.1103/PhysRevE.69.026113)），注意作者当时如何判断“分到第几层”。对照阅读 2004 年的论文，理解模块度为何成为后来的标准。
- **思考题**：边介数的计算依赖最短路径。如果网络是加权的（例如脑功能网络），应该怎样定义边介数？

### Blondel, Guillaume, Lambiotte & Lefebvre 2008：Fast unfolding of communities in large networks

- **出处**：*Journal of Statistical Mechanics* P10008。DOI：[10.1088/1742-5468/2008/10/P10008](https://doi.org/10.1088/1742-5468/2008/10/P10008)。论文精读：[Blondel 2008](paper-blondel2008_louvain.html)
- **背景**：模块度最大化是 NP 难问题，已有的贪心算法在百万节点规模上太慢。
- **核心发现**：提出“局部移动 + 聚合”的两阶段算法（即 Louvain 算法），在数百万节点的网络上几分钟内得到高模块度划分，并自然产生多层次结构。
- **阅读提示**：注意作者对“中间层次划分也有意义”的讨论，这与分辨率极限有关；之后阅读下面的 Traag 等 2019，理解 Louvain 可能产生内部不连通社团的原因。
- **思考题**：Louvain 算法中节点的访问顺序会影响结果。在你自己的研究中，你会怎样设计分析来报告这种不确定性？

### Traag, Waltman & van Eck 2019：From Louvain to Leiden: guaranteeing well-connected communities

- **出处**：*Scientific Reports* 9: 5233。DOI：[10.1038/s41598-019-41695-z](https://doi.org/10.1038/s41598-019-41695-z)
- **背景**：Louvain 被广泛使用，但它得到的社团是否满足“社团应当连通”这一最基本的要求，此前很少被检查。
- **核心发现**：证明 Louvain 可能产生任意差的连接甚至不连通的社团，并在实验中观察到较高比例的连接不良社团；提出 Leiden 算法，通过细化阶段保证社团连通，迭代收敛后所有社团的所有子集都处于局部最优，且速度更快。
- **阅读提示**：重点理解细化阶段为何能让“已经聚合的社团”在下一层被拆开；文中对模块度与 CPM 两种质量函数都做了实验。
- **思考题**：如果一个算法保证社团连通，是否就意味着它找到的社团更“真实”？连通性与分辨率极限是两个独立的问题吗？

### Fortunato & Barthélemy 2007：Resolution limit in community detection

- **出处**：*PNAS* 104: 36–41。DOI：[10.1073/pnas.0605965104](https://doi.org/10.1073/pnas.0605965104)
- **背景**：模块度最大化被广泛使用，但它能识别多小的社团，一直没有系统分析。
- **核心发现**：证明模块度存在一个与网络总边数相关的固有尺度，小于这一尺度的社团可能无法被识别，即使它们是完全连接的团；用“团组成的环”等例子说明了这一问题。
- **阅读提示**：理解“团环”例子的构造和计算，这是理解分辨率极限最直接的途径。
- **思考题**：一个包含 2 万个蛋白、30 万条相互作用的网络中，一个由 5 个蛋白组成的复合物有可能被模块度最大化单独识别出来吗？你会如何验证？

### Karrer & Newman 2011：Stochastic blockmodels and community structure in networks

- **出处**：*Physical Review E* 83: 016107。DOI：[10.1103/PhysRevE.83.016107](https://doi.org/10.1103/PhysRevE.83.016107)
- **背景**：标准随机块模型假设同组节点度相同，用于度异质的真实网络时会按度而不是按社团分组。
- **核心发现**：提出度修正随机块模型，给出只依赖划分的轮廓似然 $\sum_{rs}m_{rs}\ln[m_{rs}/(\kappa_r\kappa_s)]$；在空手道俱乐部与政治博客网络上，度修正模型恢复了真实分组，而标准模型没有。
- **阅读提示**：对照本专题[推导 F](community-structure.derivations.html)，自己从泊松似然推出两种目标函数。
- **思考题**：DC-SBM 的最大似然仍需预先给定组数。你会如何决定一个 PPI 网络应分成多少组？

### Rosvall & Bergstrom 2008：Maps of random walks on complex networks reveal community structure

- **出处**：*PNAS* 105: 1118–1123。DOI：[10.1073/pnas.0706851105](https://doi.org/10.1073/pnas.0706851105)
- **背景**：模块度只看连边密度，对于以“流动”为意义的有向、加权网络（如引文网络）未必合适。
- **核心发现**：把社团发现表述为随机游走轨迹的最优压缩问题，提出映射方程及其优化算法（Infomap）；在大型期刊引文网络上得到了与学科划分相符的“科学地图”。
- **阅读提示**：先在纸上为一个小网络的两种划分各设计一套码本，体会“短码可以在不同模块中重复使用”为何能降低描述长度。
- **思考题**：信号转导网络是有向的。对它分别使用有向模块度和映射方程，你预计结果在哪些地方会不同？

### Decelle, Krzakala, Moore & Zdeborová 2011：Inference and phase transitions in the detection of modules in sparse networks

- **出处**：*Physical Review Letters* 107: 065701。DOI：[10.1103/PhysRevLett.107.065701](https://doi.org/10.1103/PhysRevLett.107.065701)
- **背景**：社团发现算法在什么条件下必然失败？这是一个与算法无关的信息论问题。
- **核心发现**：用统计物理的空腔方法与置信传播分析稀疏随机块模型，给出可检测性阈值 $|c_{\text{in}}-c_{\text{out}}|=q\sqrt c$，并指出 $q$ 较大时存在“可检测但计算困难”的区域。
- **阅读提示**：对照本专题[推导 H](community-structure.derivations.html)的启发式论证，理解阈值中 $\sqrt c$ 的来源。
- **思考题**：一个实验测得的 PPI 网络平均度只有约 5。若其中的功能模块之间连接较多，你应如何解读社团发现“失败”的结果？

### Peixoto 2019：Bayesian stochastic blockmodeling

- **出处**：收于 Doreian、Batagelj 与 Ferligoj 编 *Advances in Network Clustering and Blockmodeling*（Wiley），pp. 289–332。DOI：[10.1002/9781119483298.ch11](https://doi.org/10.1002/9781119483298.ch11)
- **背景**：随机块模型的最大似然无法自行确定组数，且只给出点估计。
- **核心发现**：系统介绍以非参数贝叶斯方法推断 SBM 的框架：微正则模型、最小描述长度、嵌套 SBM、度修正、重叠与加权扩展、MCMC 抽样与模型比较。
- **阅读提示**：这是一篇教程式的综述，配合 `graph-tool` 文档中的示例阅读最有效；Peixoto 2023 的短书进一步讨论了描述性与推断性方法的区别。
- **思考题**：在一个完全随机的 ER 网络上，模块度最大化与贝叶斯 SBM 分别会报告什么？为什么？

## 延伸资源 {#resources}

| 类型 | 资源 | 说明 |
|---|---|---|
| 教材 | Barabási, *Network Science*, Ch. 9 Communities（[networksciencebook.com/chapter/9](http://networksciencebook.com/chapter/9)，CC BY-NC-SA 2.0） | 免费在线教材：基本假设、层次聚类、模块度、重叠社团、社团检验、社团的刻画；Advanced Topics 含层次模型、模块度推导、Louvain 与 Infomap、团渗流阈值 |
| 公开课 | Stanford CS224W（[主页](https://web.stanford.edu/class/cs224w/)） | 英文公开课，偏图机器学习；“强弱关系”与社团检测部分可与本专题对照，视频在 YouTube（需境外网络） |
| 综述 | Fortunato 2010, “Community detection in graphs”, *Physics Reports* 486: 75–174（[DOI](https://doi.org/10.1016/j.physrep.2009.11.002)） | 社团发现领域最全面的综述，篇幅很长，建议按需查阅相关章节 |
| 综述 | Fortunato & Hric 2016, “Community detection in networks: A user guide”, *Physics Reports* 659: 1–44（[DOI](https://doi.org/10.1016/j.physrep.2016.09.002)） | 面向使用者的指南：社团的定义、方法类别、验证与常见陷阱，比 2010 年的综述更易读 |
| 综述 | Peixoto 2023, *Descriptive vs. Inferential Community Detection in Networks*（Cambridge Elements，[DOI](https://doi.org/10.1017/9781009118897)） | 系统论述两类方法的区别及模块度的统计问题 |
| 综述 | Sporns & Betzel 2016, “Modular brain networks”, *Annu. Rev. Psychol.* 67: 613–640（[DOI](https://doi.org/10.1146/annurev-psych-122414-033634)） | 脑网络中社团发现的方法与应用 |
| 方法论文 | Newman 2006, “Modularity and community structure in networks”, *PNAS*（[DOI](https://doi.org/10.1073/pnas.0601602103)） | 模块度矩阵与谱方法，推导简洁；论文精读见 [Newman 2006](paper-newman2006_modularity.html) |
| 方法论文 | Lancichinetti, Fortunato & Radicchi 2008, *Phys. Rev. E* 78: 046110（[DOI](https://doi.org/10.1103/PhysRevE.78.046110)）；Lancichinetti & Fortunato 2009, *Phys. Rev. E* 80: 056117（[DOI](https://doi.org/10.1103/PhysRevE.80.056117)） | LFR 基准网络的构造，以及在其上对多种算法的系统比较 |
| 方法论文 | Lancichinetti & Fortunato 2012, “Consensus clustering in complex networks”, *Sci. Rep.* 2: 336（[DOI](https://doi.org/10.1038/srep00336)） | 共识聚类的算法与实验 |
| 方法论文 | Mucha et al. 2010, *Science* 328: 876–878（[DOI](https://doi.org/10.1126/science.1184819)） | 多层与时变网络的模块度 |
| 软件 | NetworkX 社团模块文档（[networkx.org](https://networkx.org/documentation/stable/reference/algorithms/community.html)） | `girvan_newman`、`louvain_communities`、`leiden_communities`、`k_clique_communities`、`modularity`、`LFR_benchmark_graph` 等，配合本专题代码示例使用 |
| 软件 | leidenalg（[文档](https://leidenalg.readthedocs.io/)） | Leiden 算法的官方实现，支持模块度、CPM、多层网络等多种质量函数 |
| 软件 | graph-tool（[graph-tool.skewed.de](https://graph-tool.skewed.de/)） | 贝叶斯随机块模型（嵌套、度修正、加权、多层）推断的主要实现 |
| 软件 | Infomap（[mapequation.org](https://www.mapequation.org/)） | 映射方程与 Infomap 的官方实现、在线演示与教程 |
| 软件 | Brain Connectivity Toolbox（[网站](https://sites.google.com/site/bctnet/)） | 脑网络常用的模块度、共识、参与系数与模块内 $z$ 分数函数 |
| 经典数据 | Zachary 1977, 空手道俱乐部原始论文（[DOI](https://doi.org/10.1086/jar.33.4.3629752)） | 了解这个“标准考题”的来历和实际的分裂过程 |

## 开放问题 {#questions}

1. 在你的研究方向中，“社团”可能对应什么生物学实体（蛋白复合物、通路、细胞类型、脑功能系统、症状簇……）？如果你用社团发现算法得到了一个划分，你会用什么独立证据来验证它的生物学意义？
2. 有人说“模块度最大化找到的社团，很大程度上取决于你选择的分辨率参数，所以社团发现是主观的”。你同意吗？请结合分辨率极限、稳定性分析和生物学验证，讨论怎样让社团分析的结论更可信。
3. 你的网络更适合描述性方法还是推断性方法？如果用贝叶斯 SBM 得到“只有一个组”，而 Leiden 得到了 12 个模块，你会如何解读和报告？
4. 对一个稀疏、存在大量未测相互作用的分子网络，怎样估计其中的社团结构是否处于可检测范围之内？可以设计什么样的模拟来回答这个问题？
