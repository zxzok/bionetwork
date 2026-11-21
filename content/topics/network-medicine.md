---
id: network-medicine
title: 疾病模块、网络邻近度与药物重定位
en: Disease modules, network proximity and drug repurposing
domain: medicine
legacy: L14
summary: 在相互作用组上定义疾病模块，用度匹配零模型量化疾病分离度与药物邻近度，并经外部验证用于药物重定位
keywords: [网络医学, 相互作用组, 疾病模块, 疾病模块检测, DIAMOnD, 网络传播, 带重启随机游走, 热扩散, 网络分离度, 网络邻近度, 药物组合, 互补暴露, 药物重定位, 网络药理学, 链路预测, 知识图谱嵌入, 异质网络, Hetionet, 验证层次, 电子病历, 癌症维持基因]
synonyms: [网络医学, network medicine, 相互作用组, 互作组, interactome, 疾病模块, disease module, 疾病模块假说, disease module hypothesis, 局部假设, local hypothesis, 最大连通分支, largest connected component, LCC, 疾病模块检测, disease module detection, DIAMOnD, DIseAse MOdule Detection, 连接显著性, connectivity significance, 超几何检验, hypergeometric test, 种子扩展, seed expansion, 候选基因优先排序, gene prioritization, 网络传播, network propagation, 网络扩散, network diffusion, 带重启的随机游走, random walk with restart, RWR, 个性化 PageRank, personalized PageRank, 热扩散, heat diffusion, 扩散核, diffusion kernel, 热核, heat kernel, PRINCE, HotNet2, 绝热热扩散, insulated heat diffusion, GWAS 网络放大, network expansion, 网络分离度, network separation, s_AB, 网络邻近度, network proximity, 最近距离, closest distance, 度匹配, degree-preserving, degree-matched, 度分箱, degree binning, 药物重定位, 老药新用, drug repurposing, drug repositioning, 网络药理学, network pharmacology, 药物–靶点网络, drug–target network, 多靶点, polypharmacology, 药物组合, drug combination, 互补暴露, complementary exposure, 重叠暴露, overlapping exposure, 异质网络, heterogeneous network, 知识图谱, knowledge graph, Hetionet, Project Rephetio, 元路径, metapath, 链路预测, link prediction, 共同邻居, common neighbors, 资源分配指数, resource allocation, Adamic–Adar, Katz 指数, L3, 长度为 3 的路径, 知识图谱嵌入, knowledge graph embedding, TransE, DistMult, RotatE, 图神经网络, GNN, Decagon, TxGNN, 数据泄漏, data leakage, 冷启动, cold start, 药物流行病学, pharmacoepidemiology, 电子病历, electronic health records, EHR, 医保数据, claims data, 倾向评分匹配, propensity score matching, 目标试验模拟, target trial emulation, 适应证混杂, confounding by indication, 验证层次, 控制枢纽, control hub, 控制核心点, 癌症维持基因, cancer-keeper genes, CKG, 全网可控性, total controllability]
demos: [proximity]
reviewed: 2026-11-15
---

## 概述 {#overview}

[生物分子网络与拓扑特征](molecular-networks.html)提出了“疾病模块”的假说：同一疾病的相关基因倾向于在相互作用网络中聚在一起。[基因调控网络推断与共表达分析](gene-network-inference.html)讨论了怎样从表达数据推断网络。网络医学把这两条线汇合到一个更实际的问题上：**药物作用在网络的哪里？能不能用网络距离预测一个已有药物可以治疗什么新疾病？**

围绕这个问题，网络医学形成了三层相互依赖的方法。第一层是**定位疾病**：把已知疾病基因投到相互作用组上，检验它们是否聚集，并用种子扩展或网络传播把不完整的基因列表补全为疾病模块。第二层是**度量关系**：用网络分离度刻画两种疾病的分子重叠，用网络邻近度刻画药物靶点与疾病模块的相对位置，并推广到药物组合。第三层是**预测与验证**：在药物–靶点–疾病异质网络或知识图谱上做链路预测，给出重定位候选，再用电子病历、体外实验和临床试验逐级检验。

本专题依次介绍：网络医学的基本框架与相互作用组；疾病模块的定义、检测算法（DIAMOnD、随机游走与扩散、GWAS 信号的网络放大）；网络传播的数学与参数选择；疾病之间的网络分离度；药物–靶点网络与网络药理学；网络邻近度及其在药物组合中的推广；从网络预测到外部验证的药物重定位（包括 COVID-19 的案例）；异质网络、知识图谱与链路预测；证据层次与统计要点；最后介绍基于网络控制的靶点识别研究。计算核心是“与度匹配随机基线比较”，它与[网络构建与统计验证](network-construction.html)中的零模型、[社团结构与社区发现](community-structure.html)中模块度所用的配置模型一脉相承；网络传播的数学与[网络上的传播与免疫](spreading.html)中的随机游走和扩散过程同源。

## 网络医学：把疾病看作网络的扰动 {#framework}

### 相互作用组

::: {.callout-def}
**相互作用组（interactome）**：细胞内全部分子相互作用构成的网络，常见做法是把蛋白–蛋白物理相互作用、调控（蛋白–DNA）相互作用、代谢相互作用和激酶–底物关系整合成一张以基因/蛋白为节点的无向网络。
:::

以 Menche 等（2015）的整合版本为例，它包含约 1.35 万个蛋白、约 14.1 万条经实验验证的物理相互作用（Ghiassian 等 2015 使用的版本为 13,460 个蛋白、141,296 条相互作用）。这个规模远未覆盖真实的相互作用组：数据**不完整**，并且**有研究偏倚**——研究得多的基因（如 *TP53*）连边多，部分原因是被测得多。

### 网络医学的几条基本假设

Barabási、Gulbahce 与 Loscalzo（2011）在《Nature Reviews Genetics》的综述中，把网络医学的思路概括为几条相互关联的假设：

1. **局部假设（local hypothesis）**：与同一疾病相关的基因产物倾向于彼此相互作用、位于网络的同一邻域。
2. **疾病模块假说（disease module hypothesis）**：每种疾病对应相互作用组中的一个连通子图——疾病模块；模块内的扰动引起该疾病的表型。
3. **网络简约原则（network parsimony）**：已知疾病基因之间的致病通路往往与网络中的最短路径重合。
4. **共享组分假设（shared components hypothesis）**：共享网络组分（基因、通路）的疾病在表型和共病上更相似。

::: {.callout-bio}
网络医学的一个直接推论是：**疾病基因不一定是好靶点，好靶点也不一定是疾病基因**。只要药物作用于疾病模块内或紧邻模块的蛋白，就可能通过网络传播影响模块；反之，作用于远离模块的蛋白，即使该蛋白本身很“重要”，也未必有疗效。
:::

### 研究范围

Loscalzo、Barabási 与 Silverman 主编的《Network Medicine: Complex Systems in Human Disease and Therapeutics》（Harvard University Press，2017）给出了这一领域的大致版图：网络分析基础、人类相互作用组的测定、复杂疾病遗传学、转录组与表观组网络、代谢网络、癌症网络医学、系统药理学，以及社会网络与临床试验设计等。本专题聚焦其中与**分子网络上的疾病定位和药物作用**直接相关的部分；分子网络本身的类型和拓扑见[生物分子网络与拓扑特征](molecular-networks.html)，症状层面的网络见[症状网络与网络精神病学](symptom-networks.html)。

从数据流程看，一项网络医学研究通常包括四步：

1. **参考网络**：选择相互作用组（物理相互作用、功能关联或组织特异网络），写明版本和证据阈值；
2. **疾病与药物的节点集合**：疾病基因来自 OMIM、GWAS Catalog、DisGeNET 等，药物靶点来自 DrugBank、ChEMBL 等；
3. **网络量的计算**：模块聚集、分离度、邻近度、传播分数或链路预测分数，并与度匹配零模型比较；
4. **独立验证**：回顾性基准、人群数据、实验和临床证据（见[验证的层次](network-medicine.validation-hierarchy.html)）。

## 疾病模块：定义与检测 {#disease-modules}

::: {.callout-def}
**疾病模块（disease module）**：与同一疾病相关的基因产物在相互作用组中构成的连通子图；模块内的扰动引起该疾病的表型。实际操作中，把一种疾病的已知相关基因投到相互作用组上，用它们诱导子图的**最大连通分支**作为可观测的疾病模块。
:::

### 疾病基因真的聚集吗

把一种疾病的已知相关基因投到相互作用组上，取它们诱导的子图，计算**最大连通分支（largest connected component, LCC）**的大小 $S$。与随机选取同样数量基因得到的 $S^{\mathrm{rand}}$ 比较，得到 $z$ 分数：

$$z = \frac{S - \langle S^{\mathrm{rand}} \rangle}{\sigma(S^{\mathrm{rand}})}$$

::: {.callout-warn}
随机基因集必须**保持度分布**。疾病基因往往度数偏高（部分源于研究偏倚），若从全网均匀抽取随机基因，它们的度偏低、本来就难以相连，会把 $z$ 人为抬高。常用做法是按度分箱，从同一度箱中抽取替代基因。
:::

Menche 等（2015）分析了 299 种疾病，发现其中 226 种的疾病基因显著聚集，但可观测模块平均只包含约 20% 的已知疾病基因。例如多发性硬化的 69 个相关基因中，只有 11 个连成一个分支；不过这 11 个仍远多于随机期望（约 2 个）。作者用渗流理论说明：网络覆盖率不足时，模块会碎成片段；只有相关基因数超过约 25 个的疾病，才能期望观察到成形的模块。

### 疾病模块不等于拓扑社团

一个自然的想法是：既然疾病基因聚集，能否直接用[社团发现](community-structure.html)算法找到的密集子网络作为疾病模块？Ghiassian 等（2015）在 70 种疾病上系统检验了这一点，得到否定的答案：

- 疾病蛋白的 LCC 通常只包含 10%–30% 的疾病蛋白；
- 三种社团发现方法给出的拓扑社团中，只有 1%–5% 显著富集疾病蛋白；
- 疾病蛋白集合的局部模块度在 97% 的疾病中低于 0.01。

换言之，疾病蛋白并不形成“内部稠密、对外稀疏”的社团，而是**稀疏地**分布在一片网络邻域中。真正能把疾病蛋白与随机蛋白区分开的，是它们与其他疾病蛋白之间连接数的**统计显著性**——这是下一页 DIAMOnD 算法的出发点。

::: {.callout-bio}
疾病模块与拓扑社团的区分有实际后果：如果用社团发现结果代替疾病模块，会把大量与疾病无关的稠密复合物（如核糖体、剪接体）纳入分析，同时漏掉连接稀疏但功能相关的疾病蛋白。疾病模块应以已知疾病基因为锚点，从它们出发向外扩展，而不是先划分网络再找“哪个社团含疾病基因多”。
:::

## 疾病模块检测算法：从种子基因到完整模块 {#module-detection}

已知疾病基因只是真实疾病模块的一部分。**疾病模块检测**（disease module detection）以已知疾病基因为**种子**（seed），在相互作用组中找出最可能属于同一模块的其他基因，用于候选基因排序、补全模块，并为后续的分离度和邻近度计算提供更完整的疾病基因集合。方法可分为三类：

| 类别 | 代表方法 | 核心量 | 输出 |
|---|---|---|---|
| 种子扩展 | DIAMOnD（Ghiassian 等 2015） | 与种子连接数的超几何显著性 | 按加入顺序排列的基因，截断后成为模块 |
| 网络传播 | RWR（Köhler 等 2008）、PRINCE（Vanunu 等 2010） | 从种子出发的随机游走/扩散稳态分数 | 全网基因的连续分数 |
| 显著子网络 | HotNet2（Leiserson 等 2015） | 热扩散后节点间“交换热量”形成的强连通子网络 | 若干显著子网络及其置换检验 $p$ 值 |

### DIAMOnD：连接显著性

::: {.callout-def}
**连接显著性（connectivity significance）**：网络有 $N$ 个节点，其中 $s_0$ 个是种子。一个度为 $k$ 的节点恰有 $k_s$ 个种子邻居的概率，在“邻居从全网随机抽取”的零假设下服从超几何分布：
$$
p(k,k_s)=\frac{\binom{s_0}{k_s}\binom{N-s_0}{k-k_s}}{\binom{N}{k}} ,
$$
连接显著性 $p$ 值是观察到 $k_s$ 个**或更多**种子邻居的累积概率 $p\text{-value}(k,k_s)=\sum_{k_i=k_s}^{k}p(k,k_i)$。
:::

**DIAMOnD**（DIseAse MOdule Detection）的做法很简单：计算种子集合所有邻居的连接显著性 $p$ 值，把 $p$ 值最小的节点加入种子集合，然后重新计算，如此迭代。每加入一个节点，它的邻居的 $k_s$ 就可能增加，因此模块沿着“与已有模块连接最显著”的方向生长。

**为什么不直接数种子邻居？** 枢纽蛋白邻居多，碰巧连到几个种子是意料之中的事。超几何 $p$ 值把节点的度 $k$ 纳入考虑。

::: {.callout-def}
**手算例**：$N=20$，$s_0=4$。

- 节点 $x$：$k=3$，$k_s=2$。$P(X\ge2)=\dfrac{\binom42\binom{16}{1}+\binom43\binom{16}{0}}{\binom{20}{3}}=\dfrac{96+4}{1140}\approx0.088$。
- 节点 $y$：$k=10$，$k_s=3$。$P(X\ge3)=\dfrac{\binom43\binom{16}{7}+\binom44\binom{16}{6}}{\binom{20}{10}}=\dfrac{45760+8008}{184756}\approx0.291$。

$y$ 的种子邻居更多，但 $x$ 的连接更显著，DIAMOnD 先加入 $x$。
:::

**种子加权**：原文允许把每个种子计作 $\alpha$ 份（相当于虚拟复制种子及其连边），使种子比后加入的节点影响更大；$\alpha=1$ 即所有节点同等对待。原文报告不同验证方式下较优的 $\alpha$ 并不相同，因此 $\alpha$ 应视为需要报告和做敏感性分析的参数。

**在哪里停止？** DIAMOnD 只给出一个排序，模块边界需要另定。Ghiassian 等提出两种思路：(1) **拓扑标准**——隐藏部分种子，看迭代多少步后召回率不再上升；(2) **生物学标准**——用独立注释（GO、通路、表达）评估新加入节点，富集程度降到背景水平即停止。他们的结果中，独立证据支持的节点数在约 200 次迭代后趋于平台，70 个疾病模块中有 58 个得到 GO 或通路数据的支持。截断点依赖疾病和数据，没有通用值。

### 随机游走与扩散方法

另一类方法不做离散的“加入/不加入”决定，而是让信号从种子出发在网络上**传播**，给每个节点一个连续分数。Köhler 等（2008，*American Journal of Human Genetics*）用带重启的随机游走在相互作用组上为候选疾病基因排序，并显示它优于只看直接邻居或最短路径的方法——因为它综合了所有路径而不是一条最短路径，对缺失边更不敏感。Vanunu 等（2010）的 PRINCE 用对称归一化的传播，并把疾病相似性引入先验；数学细节、参数选择与度偏倚见下一页[网络传播](network-medicine.network-propagation.html)。

### GWAS 信号的网络放大

GWAS 位点往往落在非编码区、包含多个基因，单个基因的关联证据很弱。Cowen 等（2017，*Nature Reviews Genetics*）把网络传播称为遗传关联的“通用放大器”：把基因层面的关联分数作为初始“热量”，在网络上扩散后，彼此相连、各自证据中等的一组基因会相互加强，而孤立的弱信号被稀释。

- **体细胞突变**：HotNet2（Leiserson 等 2015，*Nature Genetics*）在泛癌突变数据上用扩散找出显著的突变子网络，从而发现单个基因突变频率很低、但合起来在通路或复合物层面频繁受累的组合。
- **常见变异**：Barrio-Hernandez 等（2023，*Nature Genetics*）对 1,002 种人类性状的 GWAS 相关基因做网络扩展，扩展分数能找回已知的疾病基因和药物靶点；按扩展分数相似性可以把性状分组，并识别出 73 个与多种性状相关的多效性基因模块。

::: {.callout-warn}
网络放大会**同时放大偏倚**：研究得多的基因连边多，扩散后分数偏高；GWAS 基因映射（最近基因、eQTL、染色质互作）的选择也会改变种子。放大后的候选基因需要与度匹配随机种子比较，并用独立数据（如罕见变异、功能实验）检验，而不能把“网络分数高”直接当作因果证据。
:::

本节方法的实现见[代码示例](network-medicine.html#code)：DIAMOnD 示例在埋入模块的合成网络中比较连接显著性、种子邻居数与度三种排序；网络传播示例比较 RWR 与热扩散的参数。

## 网络传播：带重启随机游走与热扩散 {#network-propagation}

::: {.callout-def}
**网络传播（network propagation）**：把一组节点上的初始信号 $p_0$（如疾病基因上的 1、GWAS 关联分数或突变频率）按网络连边重新分配，得到每个节点的平滑分数 $p^\ast$。最常用的两种形式是**带重启的随机游走**（RWR，等价于个性化 PageRank）和**热扩散**（扩散核）。
:::

### 两种传播的定义

记邻接矩阵 $A$，度矩阵 $D=\operatorname{diag}(k_v)$，列随机转移矩阵 $W=AD^{-1}$，随机游走拉普拉斯 $L=I-W$。

**带重启的随机游走**：游走者每步以概率 $1-r$ 走到随机邻居，以概率 $r$ 跳回种子分布 $p_0$：
$$p_{t+1}=(1-r)Wp_t+rp_0,\qquad p^\ast=r\big(I-(1-r)W\big)^{-1}p_0=r\sum_{\ell\ge0}(1-r)^\ell W^\ell p_0 .$$

**热扩散**：把 $p_0$ 看作初始热量，按 $\dfrac{dp}{dt}=-Lp$ 扩散时间 $t$：
$$p(t)=e^{-tL}p_0=e^{-t}\sum_{\ell\ge0}\frac{t^\ell}{\ell!}W^\ell p_0 .$$

两者都是**对所有长度 $\ell$ 的游走加权求和**，区别只在权重：RWR 用几何权重 $r(1-r)^\ell$，平均游走长度 $(1-r)/r$；热扩散用泊松权重 $e^{-t}t^\ell/\ell!$，平均长度 $t$。$r$ 越大或 $t$ 越小，传播越局部。热扩散在固定时间截断；HotNet2 所用的“绝热”热扩散（insulated heat diffusion）每一步都有一部分热量留在原处，形式上与 RWR 相同。

### 归一化方式

- **列随机 $W=AD^{-1}$**：保持概率守恒，$\sum_v p^\ast_v=1$；但 $r\to0$ 时 $p^\ast$ 趋于平稳分布 $\pi_v=k_v/2M$，分数正比于度。
- **行随机 $D^{-1}A$**：相当于对邻居分数求平均，偏向低度节点。
- **对称归一化 $D^{-1/2}AD^{-1/2}$**（PRINCE 采用）：介于两者之间，分数的度依赖较弱，但总量不再守恒。

归一化方式会改变排名，应在方法中写明。

### 手算例：三节点链

链 $1-2-3$，种子为节点 1，$r=0.5$。$W$ 的列为：节点 1 的全部概率转到 2；节点 2 的概率各一半转到 1 和 3；节点 3 的全部概率转到 2。稳态方程
$$p_1=0.25p_2+0.5,\quad p_2=0.5(p_1+p_3),\quad p_3=0.25p_2,$$
解得 $p^\ast=(7/12,\,4/12,\,1/12)$。节点 3 离种子两步，得分是节点 2 的四分之一。若把 $r$ 降到 0.1，分数会向平稳分布 $(1/4,1/2,1/4)$ 靠拢，度为 2 的节点 2 反而得分最高——这就是度偏倚的来源。

### 参数怎么选

- **用留出种子做交叉验证**：隐藏一部分已知疾病基因，按召回率（如前 $K$ 名中找回的比例）或 AUROC 选择 $r$ 或 $t$。
- **看稳定性而不只看最优值**：在合理范围内结果稳定，才说明结论不依赖参数；报告参数扫描结果。
- **检查分数与度的相关**：过度扩散时，排名会退化为按度排序。

[代码示例](network-medicine.html#code)在埋入 60 个模块节点（公开 30 个为种子）的 2000 节点合成网络中扫描参数：RWR 在 $r=0.2$–0.8、热扩散在 $t=0.5$–2 时，前 30 名可找回 14–15 个隐藏模块成员；$r=0.05$ 时只找回 6 个、分数与度的 Spearman 相关升到 0.86；$t=20$ 时一个也找不回，相关达 0.93。用 200 组度匹配随机种子把 $r=0.05$ 的分数转成 $z$ 分数后，与度的相关降到 0.10，命中数升到 10。这些数字只说明趋势，具体值依赖合成网络。

::: {.callout-warn}
传播分数高只说明“网络上接近种子”。它不区分激活与抑制，不考虑组织表达、可成药性和毒性；种子本身的偏倚（研究得多的疾病基因）也会被传播。比较不同疾病或不同数据集的传播结果时，要用相同的网络版本、归一化方式和参数。
:::

## 疾病之间的网络分离度 {#network-separation}

两种疾病 A、B 的**网络分离度（network separation）**定义为

$$s_{AB} = \langle d_{AB} \rangle - \frac{\langle d_{AA} \rangle + \langle d_{BB} \rangle}{2}$$

其中 $\langle d_{AA} \rangle$ 是 A 的每个基因到 A 中其他基因最短距离的平均，衡量模块自身的“直径”；$\langle d_{AB} \rangle$ 是两组基因之间最近距离的平均（共有基因的距离记为 0）。

- $s_{AB} < 0$：两个模块在网络上重叠；
- $s_{AB} > 0$：两个模块拓扑上分离。

Menche 等发现约 7% 的疾病对 $s_{AB} < 0$。这些疾病对的基因功能注释更相似、相关基因共表达更高、症状更相似，在美国医保老年人群（约 3000 万参保者，其中约 1300 万人有住院记录）中的共病风险也更高；$s_{AB} > 0$ 的疾病对则基本看不到这些关联。哮喘与乳糜泻是一个例子：两者临床表现迥异，但模块重叠，共享免疫相关基因，并呈现明显的共病。

分离度与 Goh 等（2007）的[人类疾病网络](molecular-networks.disease-modules.html)是互补的：后者只看两种疾病是否**共享**致病基因，而 $s_{AB}$ 还能捕捉“基因不同但在网络上相邻”的关系。计算细节见[数学推导与算法](network-medicine.derivations.html)。

## 药物–靶点网络与网络药理学 {#network-pharmacology}

### 网络的构成

药物–靶点–疾病网络是一个**异质网络（heterogeneous network）**：

| 节点类型 | 边类型 | 常用数据来源 |
|---|---|---|
| 药物 | 药物–靶点（结合、抑制、激活） | DrugBank、ChEMBL |
| 靶点（蛋白/基因） | 蛋白–蛋白相互作用 | STRING、BioGRID、整合相互作用组 |
| 疾病 | 疾病–基因（遗传关联、突变） | OMIM、GWAS Catalog、DisGeNET |
| 疾病 | 药物–疾病（适应症、临床试验） | DrugBank、ClinicalTrials.gov |

把“药物–靶点”二分网络投影到药物一侧，得到共享靶点的药物网络；投影到靶点一侧，得到被同一药物作用的靶点网络（[人类疾病网络](molecular-networks.disease-modules.html)用的是同样的二分投影方法）。

### 从“一药一靶”到网络药理学

Yildirim 等（2007，*Nature Biotechnology*）分析当时 FDA 批准药物的药物–靶点网络，发现新药大多作用于已被其他药物作用过的靶点，呈现明显的“跟进”趋势；许多药物的靶点并不是疾病基因本身，而是在网络上与疾病基因相隔一段距离，更多起缓解症状而非纠正病因的作用。

Hopkins（2008，*Nature Chemical Biology*）提出**网络药理学（network pharmacology）**：药物的疗效和副作用常来自同时作用多个靶点；对稳健的生物网络（见[网络可控性与稳定性](controllability.html)），单靶点抑制往往被冗余通路代偿，而合理设计的多靶点作用可能更有效。网络视角下：

- **疗效**：药物靶点与疾病模块的网络邻近程度；
- **副作用**：药物靶点与其他疾病模块或关键生理通路的邻近程度；
- **药物组合**：两种药物的靶点模块之间以及它们与疾病模块之间的相对位置（见[药物组合的网络构型](network-medicine.drug-combinations.html)）。

::: {.callout-warn}
“网络药理学”在中文文献中也常指“中药成分–预测靶点–PPI–富集分析”的流程。这类分析的靶点多来自结构预测、缺乏实验证据，且通常不与度匹配随机基线比较，得到的“核心靶点”往往就是 PPI 中的高连接度枢纽。引用或开展此类分析时，应至少报告靶点证据来源，并按本专题的方法做零模型比较。
:::

## 网络邻近度 {#network-proximity}

Guney 等（2016）比较了多种衡量药物靶点集合 $T$ 与疾病基因集合 $S$ 网络距离的方式，其中表现最好的是**最近距离（closest）**：

$$d_c(S,T) = \frac{1}{|T|} \sum_{t \in T} \min_{s \in S} d(s,t)$$

即每个靶点到最近疾病基因的最短路径长度的平均。同样需要与随机基线比较：

$$z = \frac{d_c - \mu_{\mathrm{rand}}}{\sigma_{\mathrm{rand}}}$$

随机基线由与 $S$、$T$ 度数匹配的随机节点集合给出。$z$ 显著为负（文中常用 $z < -0.15$ 作为“邻近”的界线，并辅以显著性检验）说明药物靶点比随机期望更靠近疾病模块。

::: {.callout-def}
**网络邻近度（network proximity）**：药物靶点与疾病模块在相互作用组中的距离，经度匹配随机基线标准化后的 $z$ 分数。它衡量“药物是否特异地落在疾病模块附近”，而不是“药物离疾病有多少步”。
:::

除最近距离外，Guney 等比较的距离还包括：所有靶点–疾病基因对的平均最短距离（shortest）、对远距离指数降权的核距离（kernel）、以疾病模块“中心”节点为参照的距离（center）以及分离度（separation）。最近距离表现最好的直观原因是：一个靶点只要接近模块的**某一处**就可能起作用，而平均所有对的距离会被模块中远离该靶点的部分稀释。

::: {.callout-warn}
为什么一定要用 $z$ 分数？枢纽蛋白离几乎所有节点都只有一两步。一个靶向枢纽的药物，原始距离 $d_c$ 可能很小，但与同样度数的随机靶点相比并不更近。不做度匹配标准化，就会系统性地高估靶向枢纽的药物。本专题的代码示例专门演示了这一点，“网络邻近度”交互演示也可以直观比较。
:::

Guney 等用已知的药物–疾病适应症对检验发现：有疗效的药物，其靶点往往**不在**疾病模块内部，而是在模块的网络邻域；邻近度可以区分已知有效和无效的药物–疾病对，但区分能力有限，因此更适合作为候选排序工具。

## 药物组合的网络构型 {#drug-combinations}

药物组合可以提高疗效、降低单药剂量和毒性，但候选组合的数量随药物数平方增长，再乘上剂量组合，实验无法穷举。Cheng、Kovács 与 Barabási（2019，*Nature Communications*）把邻近度和分离度推广到“药物 A–药物 B–疾病 D”三者的相对位置。

### 三个量与六种构型

对每个药物–药物–疾病三元组，考察：

- 两药靶点模块的分离度 $s_{AB}$：$<0$ 表示两药靶点在网络上重叠，$\ge0$ 表示分离；
- 每种药物与疾病模块的关系：靶点是否落在疾病模块内或其邻域（“暴露”于疾病模块）。

两药是否重叠 × 各自是否暴露，组合出六种拓扑上可区分的构型。按原文的思路，大意如下：

| 构型 | 两药靶点之间 | 与疾病模块的关系 |
|---|---|---|
| 重叠暴露（overlapping exposure） | 重叠 | 两药都暴露，且三者重叠 |
| **互补暴露（complementary exposure）** | **分离** | **两药都暴露，各自命中模块的不同邻域** |
| 间接暴露（indirect exposure） | 重叠 | 只有一药暴露，另一药通过与前者的重叠间接相关 |
| 单一暴露（single exposure） | 分离 | 只有一药暴露 |
| 非暴露（non-exposure） | 重叠 | 两药都不暴露 |
| 独立作用（independent action） | 分离 | 两药都不暴露 |

### 主要发现

以已批准的高血压和癌症药物组合为参照，作者发现六种构型中**只有互补暴露与治疗效果相关**：两药靶点都命中疾病模块，但分别作用于模块的不同邻域。直观地说，两药各自“覆盖”疾病模块的一部分，合起来覆盖更多；两药靶点重叠时，第二种药物带来的增量有限，还可能叠加毒性。作者据此筛选并检验了新的降压药组合。

::: {.callout-def}
**互补暴露（complementary exposure）**：两种药物的靶点模块在网络上彼此分离（$s_{AB}\ge0$），但都与疾病模块重叠或邻近。它是网络层面对“协同组合”的一个可检验的结构假设。
:::

::: {.callout-bio}
同样的构型思路也可用于推测**不良反应**：若两药靶点模块重叠、且共同邻近某个与目标疾病无关的生理模块，组合可能放大该模块受到的扰动（这是由框架引申出的假设，需要单独检验）。Zitnik 等（2018）的 Decagon 则直接在“蛋白–药物–副作用”多关系图上用图神经网络预测药物组合的副作用（见[链路预测与知识图谱嵌入](network-medicine.link-prediction.html)）。
:::

::: {.callout-warn}
构型分类依赖阈值（何为“重叠”“暴露”）、靶点数据的完整性和疾病模块的边界，原文结论是对已批准组合的统计关联，并不意味着每个互补暴露的组合都会协同。网络构型不含剂量、药代动力学和药物–药物相互作用的信息。[代码示例](network-medicine.html#code)构造了三种组合，演示如何计算 $s_{AB}$ 与两药的邻近度 $z$ 并据此归类，阈值仅作演示。
:::

## 药物重定位：从网络预测到外部验证 {#drug-repurposing}

**药物重定位**（drug repurposing / repositioning）为已上市或已完成安全性研究的药物寻找新适应症。它的优势是安全性、药代动力学和生产工艺已有数据，可以跳过部分早期研发；难点是新适应症的有效性证据、合适剂量与专利和商业激励（Pushpakom 等 2019，*Nature Reviews Drug Discovery*）。网络方法在其中的位置是**提出和排序假设**。

### 从网络预测到人群验证

Cheng 等（2018，*Nature Communications*）用网络邻近度为 900 多种 FDA 批准药物计算与多种疾病的关系，得到数百个新的药物–疾病关联。作者选取其中 4 个与冠心病相关的网络预测，在覆盖 2.2 亿以上患者的医疗保险数据库中用倾向评分匹配做药物流行病学检验，其中 2 个得到支持：卡马西平与冠心病风险升高相关（HR 1.56，95% CI 1.12–2.18），羟氯喹与冠心病风险降低相关（HR 0.76，95% CI 0.59–0.97）；体外实验显示羟氯喹可减弱人主动脉内皮细胞中促炎细胞因子介导的激活，为后者提供了机制支持。这项研究展示了一条完整链条：**网络预测 → 人群数据检验 → 机制实验**，每一环都不能替代另一环；4 个预测只有 2 个得到支持，也说明网络预测的阳性率需要独立评估。

Cheng、Kovács 与 Barabási（2019）把邻近度推广到**药物组合**，见[药物组合的网络构型](network-medicine.drug-combinations.html)。

### 案例：COVID-19 药物重定位

2020 年，Gordon 等（*Nature*）用亲和纯化质谱鉴定出 SARS-CoV-2 病毒蛋白与人类宿主蛋白之间的 332 个高置信相互作用。Gysi 等（2021，*PNAS*）以这些宿主蛋白为“疾病模块”的起点，组合三类网络算法为 6,340 种药物打分：

1. **基于人工智能**：在网络上学习节点表示，预测药物–疾病关联；
2. **基于扩散**：从宿主蛋白出发在网络上做扩散，看药物靶点接收到多少“信号”；
3. **基于邻近度**：计算药物靶点与宿主蛋白模块的网络邻近度。

各类算法分别形成多条预测流程，作者再用秩聚合把它们整合。随后在细胞实验中筛选了 918 种药物，用实验结果评估各流程：单一流程的表现在不同验证数据上不稳定，整合后的排序更稳健。实验中有效的药物大多并不直接结合病毒蛋白的宿主靶点，提示它们通过网络邻域间接起作用。作者最后在人细胞中检验排名靠前的药物，鉴定出 6 种可减少病毒感染的药物，认为其中 4 种具有重定位潜力。

::: {.callout-warn}
在细胞系中抑制病毒复制，离临床有效还很远。COVID-19 期间多项网络预测药物（包括羟氯喹）在大型随机对照试验中并未显示疗效：RECOVERY 试验（2020，*New England Journal of Medicine*）中，住院患者使用羟氯喹并未降低 28 天死亡率。网络重定位给出的是**优先排序的候选清单**，不是疗效证据。
:::

## 异质网络、知识图谱与图机器学习 {#knowledge-graphs}

把基因、化合物、疾病、解剖部位、副作用、通路等多种实体和关系放进同一张图，就得到**生物医学知识图谱**。Himmelstein 等（2017，*eLife*）构建的 **Hetionet** v1.0 整合了 29 个公开资源，含 11 类节点、24 类边，共 47,031 个节点和 2,250,197 条边。其 Project Rephetio 以 755 个已知治疗关系为训练标签，用**元路径（metapath）**作为特征，例如

> 化合物 –结合→ 基因 –关联→ 疾病

或“化合物 –相似→ 化合物 –治疗→ 疾病”，统计每类元路径连接某化合物与某疾病的路径数（并按路径上节点的度做降权），训练分类器预测新的治疗关系，为 209,168 个化合物–疾病对给出治疗概率，并在两个外部治疗关系集合上验证。

::: {.callout-def}
**元路径（metapath）**：知识图谱中由节点类型和边类型构成的模式序列，如“化合物–结合–基因–关联–疾病”。一条元路径对应一类可解释的生物学假设（“药物结合与疾病相关的基因”），以它连接两节点的路径数（经度降权）作为特征，模型的预测可以追溯到具体路径。
:::

图神经网络（graph neural network, GNN）进一步把多类关系的预测变成端到端学习，例如 Decagon（Zitnik 等，2018，*Bioinformatics*）在蛋白–药物多关系图上预测药物组合的副作用，每种副作用是一类药物–药物边。链路预测与知识图谱嵌入的一般方法见下一页；图机器学习的发展前景另见[结果呈现与研究前沿](reporting-frontiers.html)。

::: {.callout-warn}
知识图谱的边来自文献和数据库，“被研究得多”的药物和疾病连边多，模型容易学到“热门程度”而不是机制。评估时要警惕数据泄漏：例如用随机拆分的边做测试，测试药物的近亲药物已在训练集中出现。
:::

## 链路预测与知识图谱嵌入 {#link-prediction}

药物重定位可以表述为**链路预测**（link prediction）问题：在已知的药物–疾病、药物–靶点或蛋白–蛋白网络中，哪些尚未观察到的边最可能真实存在？Liben-Nowell 与 Kleinberg（2007）在社交网络中形式化了这一问题，Lü 与 Zhou（2011）对复杂网络中的方法做了系统综述。

### 基于局部结构的相似性指标

记 $\Gamma(u)$ 为 $u$ 的邻居集合，$k_w$ 为度。

| 指标 | 定义 | 思想 |
|---|---|---|
| 共同邻居（CN） | $\lvert\Gamma(u)\cap\Gamma(v)\rvert$ | 三角闭合：朋友的朋友是朋友 |
| Jaccard | $\lvert\Gamma(u)\cap\Gamma(v)\rvert/\lvert\Gamma(u)\cup\Gamma(v)\rvert$ | 对度做归一 |
| Adamic–Adar（AA） | $\sum_{w\in\Gamma(u)\cap\Gamma(v)}1/\log k_w$ | 低度的共同邻居更有信息量（Adamic & Adar 2003） |
| 资源分配（RA） | $\sum_{w\in\Gamma(u)\cap\Gamma(v)}1/k_w$ | 资源经共同邻居均分传递（Zhou、Lü & Zhang 2009） |
| Katz | $\sum_{\ell\ge1}\beta^\ell(A^\ell)_{uv}$ | 所有路径，按长度几何降权 |
| L3 | $\sum_{a,b}\dfrac{A_{ua}A_{ab}A_{bv}}{\sqrt{k_ak_b}}$ | 长度为 3 的路径（Kovács 等 2019） |

**蛋白网络为什么不同？** Kovács 等（2019，*Nature Communications*）指出：两个蛋白有许多共同伙伴，往往说明它们有**相似的结合界面**，因而与同一类蛋白结合，而不是彼此结合；真正可能结合的，是“与我的伙伴相似的蛋白的伙伴”，即长度为 3 的路径的终点。因此在 PPI 中，L3 明显优于基于三角闭合的 CN、RA，而在社交网络中则相反。这提醒我们：**相似性指标隐含了连接机制的假设**，应与网络的形成机制相符。

::: {.callout-def}
**手算例**：路径 $u-a-b-v$ 且 $u$ 与 $v$ 无共同邻居，则 $\mathrm{CN}(u,v)=0$，而 $\mathrm{L3}(u,v)=1/\sqrt{k_ak_b}$；若 $k_a=2,k_b=8$，$\mathrm{L3}=0.25$。
:::

[代码示例](network-medicine.html#code)隐藏 10% 的边后计算 AUROC：在三角闭合强的 Watts–Strogatz 网络中，CN、RA、L3 都在 0.95 左右；在同组节点共享伙伴但彼此不相连的分块二分网络中，CN 与 RA 只有 0.48，L3 为 0.86。

### 知识图谱嵌入

知识图谱由三元组 $(h,\rho,t)$（头实体、关系、尾实体）组成，例如（二甲双胍，治疗，2 型糖尿病）。**知识图谱嵌入**把每个实体和关系映射为向量，用打分函数 $f(h,\rho,t)$ 衡量三元组成立的可能性：

- **TransE**（Bordes 等 2013）：$f=-\lVert\mathbf h+\mathbf r-\mathbf t\rVert$，把关系看作嵌入空间中的平移；难以表示一对多关系。
- **DistMult**（Yang 等 2015）：$f=\sum_i h_ir_it_i$，对 $h$、$t$ 对称，无法区分“药物治疗疾病”与“疾病治疗药物”这类有方向的关系。
- **RotatE**（Sun 等 2019）：在复数空间中 $\mathbf t\approx\mathbf h\circ\mathbf r$，$\lvert r_i\rvert=1$，把关系看作旋转，可以表示对称、反对称、逆关系和组合关系。

训练时对每个真实三元组随机替换头或尾生成负样本，用间隔损失或对数损失优化。评估常用平均倒数排名（MRR）和 Hits@$k$，并采用“过滤”设置——排名时剔除其他已知为真的三元组。GNN 方法（如 Decagon、TxGNN）在嵌入中进一步聚合邻居信息。

### 评估设计：数据泄漏与冷启动

链路预测的评估结果高度依赖测试集如何划分：

- **随机拆边**：测试药物–疾病对的药物和疾病都在训练图中出现过，且常有化学结构相似的近亲药物，性能被高估；
- **按实体拆分（冷启动）**：把某些疾病（或药物）的全部边留作测试，更接近“为一个尚无治疗的疾病找药”的真实情境。TxGNN（Huang 等 2024，*Nature Medicine*）就针对这种零样本场景设计评估；
- **按时间拆分**：用某年之前的知识训练，预测之后才获批或发表的关系，最接近前瞻性检验。

::: {.callout-warn}
负样本通常是“未观察到的边”，其中混有尚未被发现的真边；把它们当作确定的阴性，会让在热门实体上打分高的模型显得更好。报告链路预测结果时，应写明拆分方式、负样本的构造方法和与度（热门程度）基线的比较。
:::

## 验证的层次：从回顾性基准到临床试验 {#validation-hierarchy}

网络医学给出的是假设和排序，可信度取决于它经受了哪一层次的检验。下表按证据由弱到强排列（各层并非互相替代，而是逐层递进）：

| 层次 | 做法 | 能说明什么 | 主要风险 |
|---|---|---|---|
| 回顾性基准 | 用已知适应症、已知疾病基因计算 AUROC、召回率 | 方法能否“找回”已知知识 | 已知知识本身有研究偏倚；数据泄漏 |
| 文献与数据库佐证 | 检索候选药物–疾病对的已有报道、临床试验登记 | 预测与既有知识一致 | 选择性引用；“佐证”与“验证”混淆 |
| 转录组与功能数据 | 药物是否逆转疾病表达特征（如 Connectivity Map）；GWAS、罕见变异的独立支持 | 提供方向性与独立数据支持 | 细胞系与组织差异 |
| 电子病历 / 医保数据 | 药物流行病学：比较使用与不使用候选药物人群的结局 | 真实人群中的关联 | 混杂、适应证偏倚、时间相关偏倚 |
| 体外与动物实验 | 细胞活性、病毒抑制、敲低实验、动物模型 | 机制与生物学可行性 | 剂量与人体暴露不一致；模型外推性 |
| 随机对照试验 | 前瞻、随机、预先登记终点 | 因果疗效与安全性 | 成本高、周期长 |

### 人群数据的药物流行病学检验

医保理赔数据和电子病历（EHR）样本量大、覆盖真实用药，是从网络预测走向临床的重要中间层。常用设计要点：

- **新用户设计与活性对照**：比较开始使用候选药物的患者与开始使用同一适应证另一药物的患者，减少“适应证混杂”（使用某药的人本来就与不用药的人不同）；
- **倾向评分匹配或加权**：平衡可观测的基线协变量，Cheng 等（2018）即采用倾向评分匹配；
- **目标试验模拟**（target trial emulation；Hernán 与 Robins 2016）：先写出一项理想随机试验的方案（入组、干预、随访起点、结局），再用观察数据逐项模拟，可避免不朽时间偏倚（immortal time bias）等常见错误；
- **阴性对照结局与敏感性分析**：检验未测混杂的可能大小。

::: {.callout-warn}
观察数据中的关联即使经过匹配，也不等于因果。Cheng 等（2018）中羟氯喹与冠心病风险降低的关联，与 COVID-19 期间羟氯喹在随机试验中无效，是两个不同的问题（适应证、人群、终点都不同），但同样说明：只有随机对照试验能确立疗效。
:::

### 前瞻性与预先登记

Gysi 等（2021）的设计值得借鉴：在看到实验结果之前固定各流程的预测，再用 918 种药物的筛选结果评估。这相当于在计算研究中做“预先登记”，避免根据实验结果回头调整方法、挑选有利的流程。

## 统计要点：参考网络、度偏倚、显著性与外部验证 {#statistical-validation}

疾病模块、分离度、邻近度和扩散打分虽然定义不同，但结论是否可信取决于同一组统计问题。本页把散见于各方法中的要点集中整理。

### 参考网络的选择

- **用哪一类边**：相互作用组通常整合经实验验证的物理相互作用（Menche 等，2015）；STRING 等库收录的是包含共表达、文本挖掘等渠道的功能关联，两者含义不同，使用时需写明证据渠道和置信度阈值（见[生物分子网络的类型与数据来源](molecular-networks.network-types.html)）。
- **不完整性**：可观测的疾病模块平均只包含约 20% 的已知疾病基因；网络覆盖率不足时模块会碎成片段，已知疾病基因数过少的疾病难以观察到成形的模块。$s_{AB} > 0$ 也只说明在当前不完整的相互作用组中两模块不重叠。
- **研究偏倚**：研究得多的基因连边多，部分原因是被测得多。
- **组织特异性**：相互作用组没有组织和细胞类型信息，同一蛋白在肝和脑中的邻居不同；组织特异网络能否稳定提升预测，仍是开放问题（见[研究前沿与开放问题](network-medicine.frontiers.html)）。

### 节点度偏倚与度匹配

疾病基因和药物靶点往往度偏高。高度节点彼此更容易相连，到任意节点的平均距离也更短；扩散方法中，枢纽也会获得偏高的分数。因此：

- 检验疾病模块的 LCC 时，随机基因集要从同一度箱中抽取；
- 计算邻近度时，随机靶点与随机疾病基因都要度匹配，否则靶向枢纽的药物会被系统性高估；
- RWR 等扩散打分要与度匹配随机种子集比较，或改用减弱度偏倚的归一化（见[网络传播](network-medicine.network-propagation.html)）；
- 链路预测要报告与“按度打分”基线的比较。

度分箱抽样的具体做法与箱宽的折中见[数学推导与算法](network-medicine.derivations.html)。

### 统计显著性

- $z$ 分数的含义依赖零分布近似正态；距离是小整数，$d_c$ 的零分布可能离散、偏斜，靶点只有 1–2 个时尤其如此，此时应以经验 $p$ 值为主；
- 对大量药物–疾病对同时检验时，需要做多重比较校正；
- 靶点本身就是疾病基因时贡献的距离为 0，$|T|$ 很小时 $d_c$ 对这类重叠极其敏感；
- 邻近度对已知有效与无效药物–疾病对的区分能力有限，适合作为候选排序，而不是逐对的判决。

### 外部验证

网络方法给出的是假设与排序，需要独立证据检验（证据的层次见[验证的层次](network-medicine.validation-hierarchy.html)）：

- **人群数据**：Cheng 等（2018）用医保数据库做药物流行病学检验，再做机制实验；
- **预先固定的预测与实验评估**：Gysi 等（2021）在看到实验结果之前固定各流程的预测，再用 918 种药物的细胞实验评估，并比较不同验证数据集上的表现；
- **临床证据**：细胞实验有效不等于临床有效，还需要药代动力学、安全性和随机对照试验证据；
- **避免信息泄漏**：在知识图谱与图学习模型中，随机拆分边做测试可能让近亲药物泄漏到训练集。

## 基于网络可控性的靶点识别 {#author-team-research}

邻近度、分离度和网络传播都把相互作用组当作**无向**网络，只问“药物靶点离疾病模块多近”。基于网络可控性的研究从另一个角度切入：在**有向**的调控或信号网络中，借助[结构可控性与最大匹配](controllability.structural-controllability.html)，问“哪些节点在维持网络当前状态的信号传递中不可绕开”。方法细节见[网络可控性与稳定性](controllability.author-team-research.html)中的“驱动节点的枚举、分类与自适应控制”一节，这里只说明它与网络医学的衔接。

### 控制枢纽与癌症维持基因

一个网络的最大匹配把它分解为若干条控制路径，节点在路径中可能是头（驱动节点）、尾或中间节点；控制方案不唯一，节点角色随方案变化。**控制枢纽**（control hub，即控制核心点）是在**所有**控制方案中都位于路径中间的节点，可在不枚举全部方案的情况下用多项式算法找出。

Zhang 等（2023，*iScience*；精读见 [Zhang 2023](paper-zhang2023_cancerkeeper.html)）把癌症基因调控网络中的控制枢纽定义为**癌症维持基因**（cancer-keeper genes, CKG）。在以膀胱癌驱动基因和高频突变基因为种子、从五个通路数据库构建的 7,030 个基因、103,360 条有向边的网络中，CKG 只有 660 个（9.4%），远少于驱动节点；CKG 在必需性、药物靶点等数据集中富集，并在细胞和小鼠实验中检验了部分候选，结果有正有负。

### 全网可控性与 COVID-19 药物重定位

Wei 等（2023，*Biology Direct*）在人类 PPI（HuRI-Union）、SARS-CoV-2–宿主相互作用（Gordon 等 2020）和 DrugBank 药物–靶点构成的三层网络中找出 1,256 个控制枢纽，再以“距病毒蛋白 $k$ 步以内”的社区筛选。$k=2$ 时控制枢纽最富集，其中 65 个是已知药物靶点，对应 185 种已有药物。

### 与邻近度方法的异同

| | 网络邻近度 | 控制枢纽 |
|---|---|---|
| 网络 | 无向相互作用组 | 有向调控/信号网络 |
| 问题 | 靶点是否特异地靠近疾病模块 | 节点是否在所有控制方案中都传递信号 |
| 零模型 | 度匹配随机靶点 | 随机节点集合、其他中心性方法 |
| 与疾病的联系 | 直接以疾病基因为参照 | 网络由疾病相关种子构建，或以病毒蛋白邻域筛选 |

两类方法可以互补：控制枢纽提供了不依赖距离的“结构必要性”标准，而邻近度提供了与特定疾病模块的定位关系。

::: {.callout-warn}
阅读这类结果时同样要区分证据层次。Wei 等（2023）的结论来自计算分析与已发表文献的支持，没有新的药效实验；在 2 步社区中，65 个可成药控制枢纽相对随机基线的药物靶点富集 $z=1.53$、$p=0.13$，未达到常用显著性水平，但优于驱动节点法。Zhang 等（2023）中的生存分析是相关性结果，实验检验也并非全部阳性。
:::

## 数学推导与算法 {#derivations}

本节把邻近度、分离度写成可执行的算法，说明度匹配抽样的细节与复杂度，并给出 DIAMOnD 的伪代码和基于扩散的替代方法——带重启的随机游走（RWR）与热核。符号：相互作用组 $G=(V,E)$，$|V|=N$，$|E|=M$；$d(u,v)$ 为最短路径长度；$S$ 为疾病基因集合，$T$ 为药物靶点集合；$k_v$ 为节点度。

### 最近距离 $d_c$ 与度匹配 $z$ 分数

$d_c(S,T)=\frac1{|T|}\sum_{t\in T}\min_{s\in S}d(s,t)$ 有一个计算上的便利：$\min_{s\in S}d(s,t)$ 对所有 $t$ 可以用**一次多源广度优先搜索**（把 $S$ 中所有节点同时作为起点、距离设为 0）得到，代价 $O(N+M)$，不需要计算全体节点对的距离。注意 $d_c$ 不对称：它对靶点求平均，衡量“每个靶点离疾病模块多远”。

```text
算法 1  网络邻近度 z 分数（Guney 等, 2016 思路）
输入：G；疾病基因 S；靶点 T；随机次数 B（如 1000）；分箱最小容量 b（例如约 100 个节点）
输出：d_c、z 分数、经验 p 值
1. S, T ← 只保留位于 G 最大连通分支中的节点（报告丢弃了多少）
2. 度分箱：把节点按度升序排列，依次装箱，每箱至少 b 个节点（高度端的箱会跨越较宽的度范围）
3. dist ← 以 S 为源的多源 BFS；d_obs ← mean_{t∈T} dist[t]
4. 对 i = 1..B：
5.     S' ← 对 S 中每个节点，从其所在度箱中无放回随机抽一个替身
6.     T' ← 对 T 同样处理
7.     dist' ← 以 S' 为源的多源 BFS；d_i ← mean_{t∈T'} dist'[t]
8. μ, σ ← d_1..d_B 的均值与标准差
9. z ← (d_obs − μ)/σ；p ← (1 + #{d_i ≤ d_obs}) / (B + 1)
复杂度：O(B·(N+M))；对 1.3 万节点、14 万边的互作组，B=1000 时在普通电脑上可接受
```

为什么必须分箱抽样？最短路径长度强烈依赖度：高度节点到任意节点的平均距离更短。如果 $T$ 中多为枢纽而随机替身均匀抽取，替身的度偏低、距离偏长，$z$ 就会系统性地偏负，产生“药物特异地靠近疾病”的假象。分箱是一种折中：箱太细则替身选择太少、随机性不足；箱太粗则度匹配不准。

::: {.callout-warn}
$z$ 分数的含义依赖零分布近似正态。距离是小整数，$d_c$ 的零分布可能离散、偏斜，尤其当 $|T|$ 只有 1–2 个靶点时。此时应以经验 $p$ 值为主，并对大量药物–疾病对做多重比较校正。还要注意，靶点本身就是疾病基因时贡献的距离为 0，$|T|$ 很小时 $d_c$ 对这类重叠极其敏感。
:::

### 分离度 $s_{AB}$ 的计算与含义

按 Menche 等（2015）的定义：

$$
\langle d_{AA}\rangle=\frac1{|A|}\sum_{a\in A}\min_{a'\in A,\,a'\ne a}d(a,a'),\qquad
\langle d_{AB}\rangle=\frac{1}{|A|+|B|}\Big[\sum_{a\in A}\min_{b\in B}d(a,b)+\sum_{b\in B}\min_{a\in A}d(a,b)\Big].
$$

$\langle d_{AB}\rangle$ 对 $A$、$B$ 对称，共有基因的距离为 0。可以这样理解 $s_{AB}=\langle d_{AB}\rangle-\frac12(\langle d_{AA}\rangle+\langle d_{BB}\rangle)$ 的符号：若 $A$、$B$ 是同一个模块被随机分成两半，那么从 $A$ 的基因找最近的 $B$ 基因，与找最近的另一个 $A$ 基因，距离分布相近，$s_{AB}\approx0$；若两模块有共享基因或彼此穿插，跨模块的最近距离比模块内更短，$s_{AB}<0$；若两模块在网络中各居一处，$s_{AB}>0$。$\langle d_{AB}\rangle$ 可用两次多源 BFS 得到；$\langle d_{AA}\rangle$ 需要排除自身，可从每个 $a$ 出发做 BFS，代价 $O(|A|(N+M))$。

### DIAMOnD 的伪代码

```text
算法 2  DIAMOnD 疾病模块扩展（Ghiassian 等, 2015）
输入：G（N 个节点）；种子集合 S0；迭代次数 n；种子权重 α（默认 1）
输出：按加入顺序排列的节点列表
1. S ← S0
2. 重复 n 次：
3.     C ← S 中节点的全部邻居 − S
4.     对每个 v ∈ C：
5.         k ← 节点 v 的度；ks ← v 在 S 中的邻居数（种子计 α 份时，相应调整 N、|S|、k、ks）
6.         p(v) ← Σ_{j=ks}^{k} C(|S|, j)·C(N−|S|, k−j) / C(N, k)      # 超几何上尾
7.     v* ← argmin p(v)；S ← S ∪ {v*}；记录 v*
8. 返回记录的顺序；模块边界由留出种子的召回率或独立注释的富集决定
复杂度：每次迭代需更新候选的 ks（只有 v* 的邻居会变），用对数阶乘计算 p 值；总计约 O(n·(|C| + k_max))
```

超几何 $p$ 值在 $k$ 和 $k_s$ 都较大时数值很小，应在对数空间计算（如 `scipy.stats.hypergeom.logsf`）以免下溢。

### 扩散方法：带重启的随机游走

最短路径只看“最近的一条路”，对缺失一条边非常敏感。扩散方法综合了所有路径。设 $A$ 为邻接矩阵，$D=\operatorname{diag}(k_v)$，列随机矩阵 $W=AD^{-1}$。游走者每一步以概率 $1-r$ 走到随机邻居，以概率 $r$ 跳回种子集合，种子分布 $p_0$（如 $S$ 上均匀，其余为 0）：

$$
p_{t+1}=(1-r)\,W p_t+r\,p_0 .
$$

因为 $W$ 的谱半径为 1，$(1-r)W$ 的谱半径小于 1，迭代收敛到唯一的不动点

$$
p^\ast=r\big(I-(1-r)W\big)^{-1}p_0=r\sum_{\ell=0}^{\infty}(1-r)^\ell W^\ell p_0 ,
$$

即所有长度 $\ell$ 的游走按几何权重 $(1-r)^\ell$ 加总：$r$ 越大越“局部”，$r$ 越小越“全局”。

```text
算法 3  RWR 候选基因 / 药物打分
输入：邻接矩阵 A（稀疏）；种子集合 S；重启概率 r；收敛阈值 tol（如 1e-6）
输出：每个节点的稳态分数 p*
1. W ← A D^{-1}（孤立节点需先移除）
2. p0 ← 1/|S| 于 S 上，其余为 0；p ← p0
3. 重复：p_new ← (1−r)·W·p + r·p0
4.     若 ||p_new − p||_1 < tol：停止；否则 p ← p_new
5. 返回 p*（排序时排除种子本身）
6. （去度偏倚）以度匹配随机种子集重复 1–5 共 B 次，
   把每个节点的分数转为 z 分数或经验百分位
复杂度：每次迭代 O(M)，迭代次数约 log(tol)/log(1−r)；总计 O(B·M·log(1/tol)/r)
```

::: {.callout-warn}
当 $r\to0$ 时，连通无向图上的 $p^\ast$ 趋于平稳分布 $\pi_v=k_v/2M$——**分数正比于度**。即使 $r$ 适中，枢纽也会获得偏高的分数。因此 RWR 排名靠前的基因必须与度匹配随机种子比较，或改用对称归一化 $D^{-1/2}AD^{-1/2}$ 等减弱度偏倚的变体。和邻近度一样，扩散分数高只说明“网络上接近”，不说明该蛋白是可行的干预靶点：方向（激活还是抑制）、可成药性、组织表达和毒性都不在模型之中。
:::

### 热核与 RWR 的统一

热扩散 $\dot p=-Lp$（$L=I-W$）的解是 $p(t)=e^{-tL}p_0$。由于 $I$ 与 $W$ 可交换，
$$
e^{-tL}=e^{-t}e^{tW}=\sum_{\ell\ge0}\frac{e^{-t}t^\ell}{\ell!}W^\ell .
$$
与 RWR 的 $r\sum_\ell(1-r)^\ell W^\ell$ 对比可见，两者都是 $\sum_\ell c_\ell W^\ell p_0$ 形式的**游走长度加权和**，权重分别为泊松分布与几何分布。几何分布的尾部更重，RWR 会给更长的游走留下更多权重；泊松分布集中在 $t$ 附近。对称归一化下的同类核还包括正则化拉普拉斯核 $(I+\beta L_{\mathrm{sym}})^{-1}$ 与扩散核 $e^{-\beta L_{\mathrm{sym}}}$（$L_{\mathrm{sym}}=I-D^{-1/2}AD^{-1/2}$）。大网络中无须显式计算矩阵指数，可用 Krylov 子空间方法直接求 $e^{-tL}p_0$（如 `scipy.sparse.linalg.expm_multiply`），RWR 则解一个稀疏线性方程组。

## 研究前沿与开放问题 {#frontiers}

1. **用哪张网络？** 互作组没有组织和细胞类型信息，而疾病发生在特定组织中。Greene 等（2015, *Nature Genetics*，DOI: [10.1038/ng.3259](https://doi.org/10.1038/ng.3259)）构建了组织特异的功能网络。组织特异网络能否稳定提升邻近度预测，尚缺乏大规模前瞻性检验。
2. **缺失的边如何影响距离？** Kovács 等（2019, *Nature Communications*，DOI: [10.1038/s41467-019-09177-y](https://doi.org/10.1038/s41467-019-09177-y)）指出 PPI 更符合“长度为 3 的路径”原则而非三角闭合，并据此预测缺失的相互作用。补全网络后，已报道的邻近度和分离度结论有多少会改变，是值得检验的问题。
3. **距离之外的“方向”**：网络邻近度不区分激活与抑制。Connectivity Map（Lamb 等, 2006, *Science*，DOI: [10.1126/science.1132939](https://doi.org/10.1126/science.1132939)）用“药物逆转疾病表达特征”提供方向信息。如何把有符号的转录响应与网络距离整合，仍是开放问题；基于有向网络的控制方法（见[基于网络可控性的靶点识别](network-medicine.author-team-research.html)）是另一种尝试。
4. **图学习模型的评估**：TxGNN（Huang 等, 2024, *Nature Medicine*，DOI: [10.1038/s41591-024-03233-x](https://doi.org/10.1038/s41591-024-03233-x)）在知识图谱上对缺乏治疗手段的疾病做零样本预测。怎样构建不泄漏信息、能反映真实临床前瞻性的评估方案，仍在讨论中。
5. **从 GWAS 到疾病模块**：网络扩展能放大弱遗传信号（Barrio-Hernandez 等 2023），但基因映射、网络版本和扩散参数都会改变结果；如何量化这些选择带来的不确定性，并与精细定位、罕见变异等独立证据结合，是正在发展的方向。
6. **疾病模块的边界**：DIAMOnD 等方法只给出排序，模块截断点依赖疾病和验证数据。是否存在不依赖外部注释的、统计上有依据的截断准则，仍不清楚。

## 生物医学应用 {#biomedical}

网络医学给药物研发带来的最大变化，是把“找一个关键靶点”改成“评估药物作用在疾病模块的哪个位置”。这对几类问题尤其有用。

**候选疾病基因排序**：对罕见病或复杂病的 GWAS、外显子测序结果，用 DIAMOnD 或网络传播在已知疾病基因周围为候选基因排序，帮助决定哪些基因优先做功能实验。

**药物重定位**：已上市药物的安全性和药代动力学已知，若能用网络为其找到新适应症，可大幅缩短研发周期。网络邻近度提供了一个与化学结构、副作用相似性互补的维度，并且能在大规模药物–疾病矩阵上快速计算。Cheng 等（2018）用医保数据验证网络预测，是“计算预测 + 真实世界数据”结合的范例。

**药物组合与多病共存**：老年患者常同时服用多种药物。药物靶点模块与非目标疾病模块的重叠可以帮助解释副作用；“互补暴露”构型为筛选协同组合提供了结构假设。

**新发传染病的快速响应**：COVID-19 期间，从病毒–宿主相互作用图谱到网络重定位候选、再到细胞筛选只用了数月（Gordon 等 2020；Gysi 等 2021），说明网络方法适合在信息有限时快速缩小候选范围。

同时应清醒看到局限：相互作用组不完整且有组织特异性（同一蛋白在肝和脑中的邻居不同）；药物–靶点数据偏向高亲和力结合，忽略激活/抑制方向；网络距离不区分“抑制”和“激活”。用 DrugBank、STRING、DisGeNET 等数据库构建网络时，应把“度匹配随机基线”和“对结果的独立验证”写进方法设计。

## 适用范围与常见误用 {#limitations}

1. **误用**：药物靶点离疾病基因越近（原始最短路径越短），药物越可能有效。→ **正解**：必须与度匹配的随机靶点比较；靶向枢纽的药物原始距离短，但未必特异。
2. **误用**：疾病基因就是最好的药物靶点。→ **正解**：Guney 等发现有效药物的靶点多在疾病模块的邻域而非模块内部；疾病基因可能难以成药或作用于发育阶段。
3. **误用**：$s_{AB} > 0$ 说明两种疾病毫无关系。→ **正解**：它只说明在当前（不完整的）相互作用组中两模块不重叠；数据缺失、组织特异性和非分子因素都可能造成关联。
4. **误用**：网络预测出的药物在细胞实验中有效，就可以用于患者。→ **正解**：还需要药代动力学、安全性和随机对照试验证据；COVID-19 期间多个候选药物在临床试验中失败。
5. **误用**：随机基线只需“随机选同样数量的基因”。→ **正解**：要保持度分布（按度分箱抽样），否则 $z$ 分数会被系统性偏倚。
6. **误用**：用社团发现算法找到的稠密社团当作疾病模块。→ **正解**：疾病蛋白很少形成稠密社团（Ghiassian 等 2015）；疾病模块应从已知疾病基因出发扩展，并用独立注释确定边界。
7. **误用**：网络传播排名靠前的基因就是新的疾病基因。→ **正解**：过度扩散时排名退化为按度排序；要扫描参数、与度匹配随机种子比较，并用独立数据检验。
8. **误用**：链路预测模型在随机拆边测试中 AUROC 很高，就能可靠地为新疾病找药。→ **正解**：随机拆边会泄漏近亲药物和热门实体的信息，应按疾病或时间拆分评估，并与按度打分的基线比较。
9. **误用**：医保或电子病历数据中候选药物与较好结局相关，即证明疗效。→ **正解**：观察数据有适应证混杂和时间相关偏倚，需要活性对照、目标试验模拟和敏感性分析，最终仍需随机对照试验。

## 关联知识 {#related}

- [生物分子网络与拓扑特征](molecular-networks.html)：互作组的数据来源、三类边的区别、研究偏倚与疾病模块假说的提出。
- [基因调控网络推断与共表达分析](gene-network-inference.html)：从表达数据推断的模块与关键基因，可作为疾病模块的另一种来源。
- [网络构建与统计验证](network-construction.html)：零模型、度保持随机化与统计验证的一般原则。
- [网络结构指标与随机图](network-metrics.html)：最短路径、连通分支与随机图基线，是 LCC、邻近度与分离度的基础。
- [社团结构与社区发现](community-structure.html)：拓扑社团与疾病模块的区别。
- [网络上的传播与免疫](spreading.html)：网络扩散与随机游走思想，对应 RWR、热扩散等网络传播方法。
- [网络可控性与稳定性](controllability.html)：生物网络的稳健性与冗余，解释单靶点抑制为何常被代偿；控制枢纽用于癌症维持基因与 COVID-19 药物重定位。
- [症状网络与网络精神病学](symptom-networks.html)：对分子机制尚不清楚的疾病，症状层面的网络提供了另一种网络化描述。
- [结果呈现与研究前沿](reporting-frontiers.html)：图机器学习与知识图谱方法的发展前景。

## 核心文献 {#references}

### Menche 等 2015：Uncovering disease-disease relationships through the incomplete interactome

- **背景**：疾病模块假说早已提出，但相互作用组与疾病基因列表都不完整，能否在现有数据中真正看到模块？*Science* 347:1257601，DOI [10.1126/science.1257601](https://doi.org/10.1126/science.1257601)。
- **核心发现**：299 种疾病中 226 种的基因显著聚集；渗流理论给出可观测模块所需的基因数阈值；提出网络分离度 $s_{AB}$，模块重叠的疾病对在功能注释、共表达、症状和共病上都更相似。
- **阅读提示**：重点读图 1（不完整性与渗流）和图 3（$s_{AB}$ 与四类独立验证）；注意作者如何用两种随机模型评估显著性。本站论文精读见 [Menche 2015](paper-menche2015_interactome.html)，可对照阅读。
- **思考题**：如果相互作用组的覆盖率再提高一倍，$s_{AB} < 0$ 的疾病对比例会上升还是下降？为什么？

### Ghiassian、Menche 与 Barabási 2015：A DIseAse MOdule Detection (DIAMOnD) algorithm

- **背景**：已知疾病基因只覆盖疾病模块的一部分，怎样从它们出发补全模块？*PLoS Computational Biology* 11:e1004120，DOI [10.1371/journal.pcbi.1004120](https://doi.org/10.1371/journal.pcbi.1004120)。
- **核心发现**：在 70 种疾病中，疾病蛋白不形成稠密的拓扑社团；与已知疾病蛋白连接数的超几何显著性比连接密度更能识别疾病蛋白；据此提出 DIAMOnD，并用 GO、通路和表达数据确定模块边界。
- **阅读提示**：先看疾病蛋白与拓扑社团的比较，再看算法；注意截断点如何由独立数据决定，以及种子权重 $\alpha$ 的作用。
- **思考题**：DIAMOnD 的超几何零模型假设邻居从全网均匀抽取，这与度异质的网络是否一致？它会偏爱高度还是低度节点？

### Cowen 等 2017：Network propagation: a universal amplifier of genetic associations

- **背景**：*Nature Reviews Genetics* 18:551–562，DOI [10.1038/nrg.2017.38](https://doi.org/10.1038/nrg.2017.38)。
- **核心内容**：系统综述网络传播（RWR、热扩散等）的数学形式、参数与归一化选择，以及在 GWAS、体细胞突变、表达数据中的应用。
- **阅读提示**：对照本专题“网络传播”一页的公式，留意综述对度偏倚和参数稳健性的讨论。

### Guney 等 2016：Network-based in silico drug efficacy screening

- **背景**：怎样用网络量化“药物作用于疾病”的程度？*Nature Communications* 7:10331，DOI [10.1038/ncomms10331](https://doi.org/10.1038/ncomms10331)。论文精读见 [Guney 2016](paper-guney2016_drugefficacy.html)。
- **核心发现**：比较多种距离度量后，“最近距离”加度匹配 $z$ 分数表现最好；有效药物靶点多位于疾病模块邻域；邻近度可用于药物–疾病对的初筛。
- **阅读提示**：注意随机基线的构造细节（度分箱）以及作者如何定义金标准（已知适应症）；思考已知适应症本身的偏倚。
- **思考题**：一个只有 1 个靶点的药物和一个有 30 个靶点的药物，邻近度 $z$ 分数可比吗？$z$ 的方差会怎样受靶点数影响？

### Cheng 等 2018：Network-based approach to prediction and population-based validation of in silico drug repurposing

- **背景**：*Nature Communications* 9:2691，DOI [10.1038/s41467-018-05116-5](https://doi.org/10.1038/s41467-018-05116-5)。
- **核心发现**：用邻近度为 900 多种 FDA 批准药物预测新的药物–疾病关联；在 2.2 亿以上患者的医保数据中，4 个冠心病相关预测有 2 个得到支持（卡马西平风险升高、羟氯喹风险降低），并用体外实验提供机制证据。
- **阅读提示**：重点看药物流行病学部分的设计（倾向评分匹配、对照组选择），以及为什么只选 4 个预测做检验。

### Cheng、Kovács 与 Barabási 2019：Network-based prediction of drug combinations

- **背景**：*Nature Communications* 10:1197，DOI [10.1038/s41467-019-09186-x](https://doi.org/10.1038/s41467-019-09186-x)。
- **核心发现**：药物–药物–疾病三元组有六种网络构型，只有“两药都命中疾病模块、但作用于不同邻域”的互补暴露与已批准高血压和癌症组合的疗效相关。
- **阅读提示**：留意构型分类所用的阈值，以及作者如何用已批准组合作为参照。

### Gysi 等 2021：Network medicine framework for identifying drug-repurposing opportunities for COVID-19

- **背景**：疫情初期急需在已上市药物中寻找候选。*PNAS* 118(19):e2025581118，DOI [10.1073/pnas.2025581118](https://doi.org/10.1073/pnas.2025581118)。
- **核心发现**：AI、扩散、邻近度三类网络算法各有短长，秩聚合后的整合预测更稳健；实验验证的有效药物多数不直接结合病毒宿主靶点。
- **阅读提示**：留意作者如何在“看到实验结果之前”固定预测并据此评估，以及不同验证数据集上性能的差异。
- **思考题**：本文的验证终点是细胞实验中的病毒抑制。若要把候选推进到临床，还缺哪些证据？网络方法能在其中哪一步继续发挥作用？

### Himmelstein 等 2017：Systematic integration of biomedical knowledge prioritizes drugs for repurposing

- **背景**：*eLife* 6:e26726，DOI [10.7554/eLife.26726](https://doi.org/10.7554/eLife.26726)。
- **核心发现**：构建 Hetionet（11 类节点、24 类边），以元路径特征训练模型，为 20 余万化合物–疾病对给出治疗概率，并在外部治疗关系集上验证；整个项目公开进行。
- **阅读提示**：看元路径特征如何做度降权，以及可解释性（哪些元路径贡献最大）。

### 其他引用文献

- Barabási AL, Gulbahce N, Loscalzo J (2011). Network medicine: a network-based approach to human disease. *Nature Reviews Genetics* 12:56–68. DOI [10.1038/nrg2918](https://doi.org/10.1038/nrg2918)。精读见 [Barabási 2011](paper-barabasi2011_networkmedicine.html)。
- Goh KI 等 (2007). The human disease network. *PNAS* 104:8685–8690. DOI [10.1073/pnas.0701361104](https://doi.org/10.1073/pnas.0701361104)。精读见 [Goh 2007](paper-goh2007_diseasenetwork.html)。
- Yıldırım MA 等 (2007). Drug–target network. *Nature Biotechnology* 25:1119–1126. DOI [10.1038/nbt1338](https://doi.org/10.1038/nbt1338)。
- Hopkins AL (2008). Network pharmacology: the next paradigm in drug discovery. *Nature Chemical Biology* 4:682–690. DOI [10.1038/nchembio.118](https://doi.org/10.1038/nchembio.118)。
- Köhler S 等 (2008). Walking the interactome for prioritization of candidate disease genes. *American Journal of Human Genetics* 82:949–958. DOI [10.1016/j.ajhg.2008.02.013](https://doi.org/10.1016/j.ajhg.2008.02.013)。
- Vanunu O 等 (2010). Associating genes and protein complexes with disease via network propagation. *PLoS Computational Biology* 6:e1000641. DOI [10.1371/journal.pcbi.1000641](https://doi.org/10.1371/journal.pcbi.1000641)。
- Leiserson MDM 等 (2015). Pan-cancer network analysis identifies combinations of rare somatic mutations across pathways and protein complexes. *Nature Genetics* 47:106–114. DOI [10.1038/ng.3168](https://doi.org/10.1038/ng.3168)。
- Barrio-Hernandez I 等 (2023). Network expansion of genetic associations defines a pleiotropy map of human cell biology. *Nature Genetics* 55:389–398. DOI [10.1038/s41588-023-01327-9](https://doi.org/10.1038/s41588-023-01327-9)。
- Gordon DE 等 (2020). A SARS-CoV-2 protein interaction map reveals targets for drug repurposing. *Nature* 583:459–468. DOI [10.1038/s41586-020-2286-9](https://doi.org/10.1038/s41586-020-2286-9)。
- RECOVERY Collaborative Group (2020). Effect of hydroxychloroquine in hospitalized patients with Covid-19. *New England Journal of Medicine* 383:2030–2040. DOI [10.1056/NEJMoa2022926](https://doi.org/10.1056/NEJMoa2022926)。
- Pushpakom S 等 (2019). Drug repurposing: progress, challenges and recommendations. *Nature Reviews Drug Discovery* 18:41–58. DOI [10.1038/nrd.2018.168](https://doi.org/10.1038/nrd.2018.168)。
- Zitnik M, Agrawal M, Leskovec J (2018). Modeling polypharmacy side effects with graph convolutional networks. *Bioinformatics* 34:i457–i466. DOI [10.1093/bioinformatics/bty294](https://doi.org/10.1093/bioinformatics/bty294)。
- Liben-Nowell D, Kleinberg J (2007). The link-prediction problem for social networks. *Journal of the American Society for Information Science and Technology* 58:1019–1031. DOI [10.1002/asi.20591](https://doi.org/10.1002/asi.20591)。
- Lü L, Zhou T (2011). Link prediction in complex networks: a survey. *Physica A* 390:1150–1170. DOI [10.1016/j.physa.2010.11.027](https://doi.org/10.1016/j.physa.2010.11.027)。
- Adamic LA, Adar E (2003). Friends and neighbors on the Web. *Social Networks* 25:211–230. DOI [10.1016/S0378-8733(03)00009-1](https://doi.org/10.1016/S0378-8733(03)00009-1)。
- Zhou T, Lü L, Zhang YC (2009). Predicting missing links via local information. *European Physical Journal B* 71:623–630. DOI [10.1140/epjb/e2009-00335-8](https://doi.org/10.1140/epjb/e2009-00335-8)。
- Kovács IA 等 (2019). Network-based prediction of protein interactions. *Nature Communications* 10:1240. DOI [10.1038/s41467-019-09177-y](https://doi.org/10.1038/s41467-019-09177-y)。
- Bordes A 等 (2013). Translating embeddings for modeling multi-relational data（TransE）. *Advances in Neural Information Processing Systems* 26。Yang B 等 (2015). Embedding entities and relations for learning and inference in knowledge bases（DistMult）. ICLR。Sun Z 等 (2019). RotatE: knowledge graph embedding by relational rotation in complex space. ICLR。（会议论文，未列 DOI）
- Hernán MA, Robins JM (2016). Using big data to emulate a target trial when a randomized trial is not available. *American Journal of Epidemiology* 183:758–764. DOI [10.1093/aje/kwv254](https://doi.org/10.1093/aje/kwv254)。
- Zhang X 等 (2023). Cancer-keeper genes as therapeutic targets. *iScience* 26:107296. DOI [10.1016/j.isci.2023.107296](https://doi.org/10.1016/j.isci.2023.107296)。精读见 [Zhang 2023](paper-zhang2023_cancerkeeper.html)。
- Wei X, Pan C, Zhang X, Zhang W (2023). Total network controllability analysis discovers explainable drugs for Covid-19 treatment. *Biology Direct* 18:55. DOI [10.1186/s13062-023-00410-9](https://doi.org/10.1186/s13062-023-00410-9)。

## 延伸资源 {#resources}

| 类型 | 资源 | 说明 |
|---|---|---|
| 综述 | Barabási, Gulbahce & Loscalzo 2011，[doi.org/10.1038/nrg2918](https://doi.org/10.1038/nrg2918) | 网络医学的纲领性综述，先读这篇；精读见 [Barabási 2011](paper-barabasi2011_networkmedicine.html) |
| 综述 | Cowen 等 2017，[doi.org/10.1038/nrg.2017.38](https://doi.org/10.1038/nrg.2017.38) | 网络传播的数学与应用综述，对应本专题“网络传播”与“疾病模块检测”两页 |
| 综述 | Pushpakom 等 2019，[doi.org/10.1038/nrd.2018.168](https://doi.org/10.1038/nrd.2018.168) | 药物重定位的整体图景，包括计算、实验与监管和商业层面的挑战 |
| 教材 | Loscalzo, Barabási & Silverman（主编），*Network Medicine: Complex Systems in Human Disease and Therapeutics*，Harvard University Press，2017 | 网络医学的专著，覆盖互作组、复杂疾病遗传学、组学网络、癌症与系统药理学；本专题对照其覆盖面组织 |
| 视频 | [Network Medicine: From Cellular Networks to Drug Repurposing for COVID-19（Barabási，2020）](https://www.youtube.com/watch?v=IkBZFnkxwpo) | 英文，约 54 分钟，方法提出者本人讲疾病模块、邻近度与 COVID-19 重定位；需境外网络 |
| 视频 | [6 分钟带你快速了解——什么是网络药理学？（B 站）](https://www.bilibili.com/video/BV19cZCB9ETE/) | 中文科普，概念入门；注意 B 站常见的“成分–靶点–PPI–富集”流程没有度匹配零模型，严谨性不及本专题介绍的邻近度方法 |
| 原始研究 | Cheng 等 2018，[doi.org/10.1038/s41467-018-05116-5](https://doi.org/10.1038/s41467-018-05116-5)；Zhou 等 2020，[doi.org/10.1038/s41421-020-0153-3](https://doi.org/10.1038/s41421-020-0153-3) | 网络预测 + 人群数据验证的重定位；疫情初期的 SARS-CoV-2 网络重定位，均开放获取 |
| 工具 | [NetMedPy（GitHub）](https://github.com/menicgiulia/NetMedPy) | Python 包，计算疾病模块 LCC、邻近度与分离度 z 分数，可直接用于实际分析 |
| 工具 | [Guney 2016 配套代码 toolbox](https://github.com/emreg00/toolbox) | 邻近度方法的原始实现，适合对照论文理解随机基线细节 |
| 交互工具 | [Hetionet Neo4j Browser](https://neo4j.het.io/browser/)；数据见 [hetio/hetionet](https://github.com/hetio/hetionet) | 不装软件，在浏览器里查询“药物–基因–疾病”路径；数据原创部分为 CC0 |
| 交互工具 | [Open Targets Platform](https://platform.opentargets.org/) | 查询靶点–疾病关联证据和已知药物，数据 CC0 |

## 开放问题 {#questions}

1. 针对一种具体疾病，设想用网络邻近度为它筛选重定位候选药物：应从哪些数据库取疾病基因和药物靶点？用哪种组织特异的网络？怎样设计度匹配随机基线和独立验证？
2. 网络医学假定“疾病是分子网络的扰动”。对于精神疾病、慢性疼痛等分子机制尚不清楚的疾病，这个框架有哪些适用之处和局限？能否与[症状网络](symptom-networks.html)结合？
3. DIAMOnD、RWR 与热扩散在同一组种子上给出的候选基因排序往往不同。如果没有独立的金标准，怎样判断哪一种更可信？哪些差异来自度偏倚，哪些来自对路径长度的不同加权？
4. “互补暴露”是对已批准组合的统计规律。怎样设计一项前瞻性研究，检验它对新组合的预测能力？剂量与药代动力学信息应如何纳入？
5. 一项链路预测模型在随机拆边下 AUROC 为 0.95，在按疾病拆分下降到 0.70。哪个数字更能代表它在药物重定位中的实际价值？还应补充哪些评估？
