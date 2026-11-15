---
id: degree-correlations
title: 度相关性与网络结构的高阶统计
en: Degree correlations and higher-order structure
domain: theory
legacy: ""
summary: 度分布之外，谁和谁相连：联合度分布、同配与异配、结构截断、富人俱乐部、聚集谱与 k-核，以及它们对传播、渗流、同步与控制的影响。
keywords: [度相关, 同配性, 异配性, 联合度分布, 邻居平均度, 度相关系数, 结构截断, 富人俱乐部, 聚集谱, 层次模块性, k-核分解, 度保持随机化]
synonyms: [degree correlations, degree-degree correlation, 度-度相关, 度度相关, assortativity, assortative mixing, 同配混合, 同配, disassortativity, disassortative mixing, 异配混合, 异配, 中性网络, neutral network, 联合度分布, joint degree distribution, 度相关矩阵, degree correlation matrix, e_jk, mixing matrix, 混合矩阵, 条件度分布, conditional degree distribution, P(k'|k), 细致平衡, detailed balance, 邻居平均度, average nearest-neighbor degree, ANND, k_nn, knn, 度相关函数, degree correlation function, 相关指数, correlation exponent, mu, 度相关系数, degree correlation coefficient, assortativity coefficient, Newman r, 同配系数, Spearman 同配, rank assortativity, 类别同配系数, attribute assortativity, 有向同配, directed assortativity, 友谊悖论, friendship paradox, 结构截断, structural cutoff, 自然截断, natural cutoff, 结构性异配, structural disassortativity, 伪异配, 配置模型, configuration model, erased configuration model, 隐变量模型, hidden variable model, 度保持随机化, degree-preserving randomization, 双边交换, double edge swap, Maslov–Sneppen, Xulvi-Brunet–Sokolov, 重连算法, rewiring, dK 序列, dK-series, 富人俱乐部, rich club, rich-club coefficient, 富人俱乐部系数, 归一化富人俱乐部系数, normalized rich-club coefficient, 加权富人俱乐部, weighted rich club, 聚集谱, clustering spectrum, C(k), 三点相关, three-point correlation, 层次模块性, hierarchical modularity, 层次网络模型, hierarchical network model, k-核, k-core, k 核, k-壳, k-shell, 核数, coreness, core number, k-核分解, k-core decomposition, 剥离算法, pruning, 结构核心, structural core, 枢纽回避, hub avoidance, 枢纽, hub]
demos: [ba, er, attack, sir, kuramoto, brain_threshold]
reviewed: 2026-11-15
---

## 概述 {#overview}

度分布 $p_k$ 只告诉我们“每个节点有多少条边”，没有说明“这些边连向谁”。两张度序列完全相同的网络，可以一张让枢纽彼此相连，另一张让枢纽各自统领一群低度节点。区分这两种连接方式的统计量就是**度相关性**（degree correlations）：一条边两端节点的度是否相互依赖。枢纽倾向于连接枢纽的网络称为**同配**（assortative），枢纽倾向于连接低度节点的称为**异配**（disassortative），两者都不明显的称为**中性**（neutral）。

度相关是“度分布之后的下一层结构”。它最早由 Pastor-Satorras、Vázquez 与 Vespignani（2001, *PRL*）在互联网拓扑中通过邻居平均度函数 $k_{nn}(k)$ 提出；Maslov 与 Sneppen（2002, *Science*）用保度随机化比较了酵母蛋白质相互作用网络与转录调控网络中枢纽之间的连接；Newman（2002, *PRL*；2003, *PRE*）引入了度相关系数 $r$，并系统比较了社会、技术和生物网络。一个反复出现的经验规律是：社会网络多为同配，蛋白质相互作用、代谢、神经元等生物网络多为异配。但后续工作也表明，生物网络的异配有相当一部分可以由重尾度分布和“简单图不允许重边”这一约束解释，这就是[结构截断](degree-correlations.structural-cutoff.html)问题。

本专题从两点相关推进到更高阶的结构统计：

1. [联合度分布与条件度分布](degree-correlations.joint-degree-distribution.html)：度相关的完整描述；
2. [邻居平均度函数 $k_{nn}(k)$](degree-correlations.knn-function.html) 与 [度相关系数 $r$](degree-correlations.assortativity-coefficient.html)：两种压缩描述及其局限；
3. [结构截断与结构性异配](degree-correlations.structural-cutoff.html)、[度保持随机化检验](degree-correlations.randomization-tests.html)：怎样判断观测到的相关是否超出了度序列本身的约束；
4. [生成具有度相关的网络](degree-correlations.generating-correlated-networks.html)：模型与重连算法；
5. 更高阶的统计：[富人俱乐部](degree-correlations.rich-club.html)、[聚集谱与层次模块性](degree-correlations.clustering-spectrum.html)、[k-核分解](degree-correlations.k-core.html)；
6. [度相关对网络过程的影响](degree-correlations.impact-on-dynamics.html)：渗流、鲁棒性、传播、同步与可控性。

它建立在[网络结构指标与随机图](network-metrics.html)（度、度分布、聚集系数）和[小世界与无标度网络模型](network-models.html)（配置模型、BA 模型）之上；零模型的一般原理见[网络构建与统计验证](network-construction.null-models.html)。本专题的全部代码示例见[代码示例](degree-correlations.html#code)。

## 联合度分布与条件度分布 {#joint-degree-distribution}

### 从“随机抽一个节点”到“随机抽一条边”

度相关的所有定义都以**边**为抽样单位。在无向网络中随机选一条边，再随机选它的一端，到达度为 $k$ 的节点的概率不是 $p_k$，而是

$$
q_k=\frac{k\,p_k}{\langle k\rangle},
$$

因为度为 $k$ 的节点有 $k$ 条边可以“被抽中”。$q_k$ 称为**边端度分布**。在 Newman 的原始定义中使用的是“剩余度”（excess degree，即除去来时那条边后剩下的边数 $k-1$），这只是把度平移 1，不影响后面的相关系数。

::: {.callout-def}
**联合度分布**（joint degree distribution，也称度相关矩阵）$e_{jk}$：随机选一条边，其两端节点的度分别为 $j$ 与 $k$ 的概率。无向网络中 $e_{jk}=e_{kj}$，且

$$
\sum_{j,k}e_{jk}=1,\qquad \sum_{j}e_{jk}=q_k .
$$

**条件度分布** $P(k'\mid k)$：从一个度为 $k$ 的节点出发沿一条边，到达度为 $k'$ 的节点的概率，$P(k'\mid k)=e_{kk'}/q_k$。

**中性（无相关）网络**：$e_{jk}=q_j\,q_k$，等价地 $P(k'\mid k)=q_{k'}$ 与 $k$ 无关。
:::

$e_{jk}$ 与 $P(k'\mid k)$ 满足**细致平衡**（detailed balance）条件

$$
k\,p_k\,P(k'\mid k)=k'\,p_{k'}\,P(k\mid k'),
$$

两边都等于 $\langle k\rangle e_{kk'}$。它说明联合分布不能随意指定：一旦给定度分布，条件分布必须与之相容。这一约束在后面推导[传播阈值](degree-correlations.impact-on-dynamics.html)时起关键作用。

### 从计数到概率：一个可手算的例子

设 $N_k$ 为度为 $k$ 的节点数，$E_{kk'}$ 为连接度 $k$ 与度 $k'$ 节点的边数（$k=k'$ 时计两次），$L$ 为总边数。则

$$
e_{kk'}=\frac{E_{kk'}}{2L},\qquad q_k=\frac{kN_k}{2L},\qquad P(k'\mid k)=\frac{E_{kk'}}{kN_k}.
$$

以 4 个节点的路径图 $1-2-3-4$ 为例：度序列为 $(1,2,2,1)$，$L=3$。两条端边连接度 1 与度 2，中间一条边连接度 2 与度 2。于是 $E_{12}=E_{21}=2$，$E_{22}=2$（一条边计两次），$e_{12}=e_{21}=e_{22}=1/3$，$e_{11}=0$。边端度分布 $q_1=1/3$、$q_2=2/3$。如果网络是中性的，应有 $e_{11}=q_1^2=1/9$，$e_{22}=4/9$；实际上度 1 节点之间没有边，而度 1 与度 2 节点之间的边比中性预期多（$2/3$ 对 $4/9$），这是一个轻度异配的小网络。

### 为什么需要压缩描述

$e_{jk}$ 是完整的两点度相关描述，但它有约 $k_{\max}^2/2$ 个自由参数，真实网络中大部分格子只有零星几条边，直接比较两张网络的 $e_{jk}$ 噪声很大。因此实践中常用两类压缩：一个函数 $k_{nn}(k)$，或一个数 $r$。另一条路线是 **dK 序列**（dK-series; Mahadevan 等, 2006）：0K 保留平均度，1K 保留度分布，2K 保留联合度分布 $e_{jk}$，3K 再保留三节点子图的度组合。Orsini 等（2015, *Nature Communications*）用 dK 随机网络逐级比较真实网络，发现不少网络的许多常用指标在 2K 或 2.5K（再加上聚集谱）层面就已基本被再现，从而可以判断某个指标是否“超出了低阶统计的解释”。

### 友谊悖论

中性网络中，沿一条边到达的节点平均度为 $\sum_k k\,q_k=\langle k^2\rangle/\langle k\rangle\ge\langle k\rangle$，等号只在所有节点度相同时成立。这就是 Feld（1991, *American Journal of Sociology*）描述的**友谊悖论**：平均而言，你的朋友的朋友比你多。它不是度相关造成的，而是“按边抽样偏向高度节点”的直接结果。在度分布重尾的网络中，$\langle k^2\rangle/\langle k\rangle$ 可以远大于 $\langle k\rangle$。下一节的 $k_{nn}(k)$ 正是在这一基线上判断相关。

## 邻居平均度函数与相关指数 {#knn-function}

### 定义

::: {.callout-def}
节点 $i$ 的**邻居平均度**（average nearest-neighbor degree）$k_{nn,i}=\frac{1}{k_i}\sum_j A_{ij}k_j$。

**度相关函数** $k_{nn}(k)$：所有度为 $k$ 的节点的 $k_{nn,i}$ 的平均，

$$
k_{nn}(k)=\sum_{k'}k'\,P(k'\mid k).
$$

- 中性网络：$k_{nn}(k)=\langle k^2\rangle/\langle k\rangle$，与 $k$ 无关（水平线）；
- 同配网络：$k_{nn}(k)$ 随 $k$ 增加；
- 异配网络：$k_{nn}(k)$ 随 $k$ 减小。
:::

中性情形的推导只需一行：$P(k'\mid k)=q_{k'}=k'p_{k'}/\langle k\rangle$，代入得 $\sum_{k'}k'^2p_{k'}/\langle k\rangle$。路径图的例子中，$k_{nn}(1)=2$，$k_{nn}(2)=(1+2)/2=1.5$，中性预期为 $\langle k^2\rangle/\langle k\rangle=2.5/1.5\approx1.67$：度 1 节点的邻居度高于基线，度 2 节点的邻居度低于基线，$k_{nn}(k)$ 下降，与上节结论一致。

### 相关指数 $\mu$

Pastor-Satorras 等（2001）观察到互联网的 $k_{nn}(k)$ 在双对数坐标下近似为直线，于是常用幂律近似

$$
k_{nn}(k)\approx a\,k^{\mu},
$$

$\mu>0$ 同配，$\mu=0$ 中性，$\mu<0$ 异配。Barabási《Network Science》第 7 章对十个参考网络做了拟合：科学合作网络 $\mu>0$，电网与零几乎无差别，大肠杆菌代谢网络 $\mu$ 明显为负。若干模型给出幂律形式的理论支持：隐变量模型在禁止重边时得到 $k_{nn}(k)\sim k^{-1}$；初始吸引力增长模型在度指数 $\gamma<3$ 时得到幂律衰减的 $k_{nn}(k)$，在 BA 极限（$\gamma=3$）为中性，在 $\gamma>3$ 时 $k_{nn}$ 随 $\ln k$ 缓慢上升（Barrat & Pastor-Satorras, 2005, *PRE*）。

### 估计时的实际问题

- **对数分箱**：高 $k$ 处每个度值只有一两个节点，线性分箱的 $k_{nn}(k)$ 噪声极大，应在对数间隔的度区间内平均。
- **拟合区间**：$\mu$ 依赖拟合区间，高 $k$ 端常因[结构截断](degree-correlations.structural-cutoff.html)而弯曲，应报告拟合区间并画出整条曲线。
- **加权网络**：Barrat 等（2004, *PNAS*）定义加权邻居平均度 $k^w_{nn,i}=\frac{1}{s_i}\sum_j w_{ij}k_j$（$s_i$ 为节点强度）。若 $k^w_{nn,i}>k_{nn,i}$，说明权重大的边偏向连接高度节点。
- **有向网络**：每个节点有入度与出度，需要分别计算四种组合 $k_{nn}^{\alpha\beta}(k)$，$\alpha,\beta\in\{\text{in},\text{out}\}$（Foster 等, 2010, *PNAS*）。转录调控网络中“转录因子的出度”与“靶基因的入度”的组合，与无向化后的结果可能完全不同。

代码示例“三类网络对照”从同一个 BA 度序列出发，重连出同配版和异配版，分别拟合 $\mu$，并与 $r$、Spearman 秩相关对照。

## 度相关系数 r {#assortativity-coefficient}

### 定义

::: {.callout-def}
**度相关系数**（degree assortativity coefficient，Newman, 2002）：一条边两端节点度的 Pearson 相关系数，

$$
r=\frac{\sum_{jk}jk\,(e_{jk}-q_jq_k)}{\sigma_q^2},\qquad
\sigma_q^2=\sum_k k^2q_k-\Big(\sum_k k\,q_k\Big)^2 .
$$

$-1\le r\le1$；$r>0$ 同配，$r=0$ 中性，$r<0$ 异配。
:::

在边列表上直接计算更方便。设第 $i$ 条边两端的度为 $j_i,k_i$，共 $L$ 条边，

$$
r=\frac{L^{-1}\sum_i j_ik_i-\big[L^{-1}\sum_i\tfrac12(j_i+k_i)\big]^2}
{L^{-1}\sum_i\tfrac12(j_i^2+k_i^2)-\big[L^{-1}\sum_i\tfrac12(j_i+k_i)\big]^2}.
$$

这等价于把每条无向边按两个方向各记一次，再算普通 Pearson 相关。用剩余度 $k-1$ 或度 $k$ 计算结果相同。

**算例一（星形图）**：中心度为 $N-1$，叶子度为 1。每条边的有序对只有 $(1,N-1)$ 与 $(N-1,1)$ 两种，两者完全反向，$r=-1$。星形图是最极端的异配结构。

**算例二（路径图 $1-2-3-4$）**：三条边的六个有序对为 $(1,2),(2,1),(2,2),(2,2),(2,1),(1,2)$。$x$ 的均值 $5/3$，方差 $3-25/9=2/9$；$xy$ 的均值 $16/6$，协方差 $8/3-25/9=-1/9$；$r=-0.5$。

### 真实网络中的数值

Newman（2003, *PRE*）表 II 给出的部分数值：物理学合作网络 $r=0.363$，电影演员合作网络 $0.208$，公司董事网络 $0.276$；酵母蛋白质相互作用网络 $-0.156$，大肠杆菌代谢网络 $-0.240$，线虫神经网络（有向）$-0.226$，互联网自治系统网络 $-0.189$。这一对照是“社会网络同配、生物与技术网络异配”这一说法的主要依据。Newman 与 Park（2003, *PRE*）提出，社会网络的同配性可以部分来自社团结构：人们分属大小不同的群体，大群体中的成员度高且彼此相连。代码示例“阈值化相关网络中的同配性”在模拟脑网络中重现了这一机制。

### 不确定性

$r$ 是从 $L$ 条边估计的统计量。Newman（2003）建议用刀切法（jackknife）估计标准误：依次删除每条边重算 $r_i$，$\sigma_r^2=\sum_i(r_i-r)^2$。但这一误差只反映“边的抽样波动”，不反映网络构建本身的误差（假阳性相互作用、阈值选择等），也不能代替与零模型的比较。

### 局限

::: {.callout-warn}
**$r$ 不是一个与网络规模无关的“相关强度”。**

1. **线性假设**：$r$ 相当于用直线拟合 $k_{nn}(k)$，而理论与实证常给出幂律或对数形式。Barabási 书中第 7 章进阶专题 7.A 显示，在多个网络上线性拟合都很差；$r$ 与 $\mu$ 的符号通常一致，大小却不能直接换算。
2. **规模依赖**：对重尾度分布的大网络，即使把网络重连到“最大异配”，$r$ 的绝对值也随 $N$ 增大而趋近 0。Litvak 与 van der Hofstad（2013, *PRE*）从数学上解释了这一现象，并建议改用 Spearman 秩相关等秩统计量，它们在不同规模的同类网络之间更可比。
3. **被极少数枢纽主导**：$r$ 的分母与分子都含 $\sum k^2q_k$ 这类高阶矩，删去一两个枢纽可能显著改变 $r$。
4. **可达范围受度序列约束**：给定度序列下 $r$ 的最小值与最大值通常不是 $-1$ 与 $1$。比较两个网络的 $r$ 时，应同时报告各自度序列下的可达范围或零模型分布。
:::

### 类别同配与有向同配

Newman（2003）把同一思想推广到离散属性：若 $e_{ij}$ 为一条边连接类型 $i$ 与类型 $j$ 节点的比例，$a_i=\sum_j e_{ij}$、$b_j=\sum_i e_{ij}$，则

$$
r=\frac{\sum_i e_{ii}-\sum_i a_ib_i}{1-\sum_i a_ib_i}.
$$

这可以用于检验“同一功能模块的蛋白是否更倾向于相互作用”“同一功能系统的脑区是否更倾向于相连”，与模块度的期望项形式相同（见[社团结构与社区发现](community-structure.modularity.html)）。有向网络中可以定义四个系数 $r_{\text{out,in}}$、$r_{\text{in,out}}$、$r_{\text{out,out}}$、$r_{\text{in,in}}$（Foster 等, 2010）；Piraveenan 等（2012, *IEEE/ACM TCBB*）讨论了有向生物网络中这些系数的计算与解读。

## 结构截断与结构性异配 {#structural-cutoff}

### 简单图与度分布的冲突

在配置模型中，度为 $k$ 与 $k'$ 的两个节点之间的期望边数约为

$$
E_{kk'}^{(\text{pair})}\approx\frac{k\,k'}{2L}=\frac{k\,k'}{\langle k\rangle N}.
$$

当两个节点的度都很大时，这个期望值可以超过 1。例如 $N=300$、$L=450$ 的网络中，两个度为 55 与 46 的枢纽之间“应有”约 2.8 条边。多重图允许这样，网络保持中性；但大多数生物网络被表示为**简单图**（两节点之间最多一条边），多出的边只能连到别处，主要连到低度节点，网络因此表现出异配。这种完全由约束产生的相关称为**结构性异配**（structural disassortativity）。

### 结构截断

::: {.callout-def}
**结构截断**（structural cutoff）$k_s$：度超过 $k_s$ 的两个节点在中性网络中的期望边数超过 1，因而在简单图中无法保持中性。对中性网络，

$$
k_s\sim(\langle k\rangle N)^{1/2}.
$$

**自然截断**（natural cutoff）$k_{\max}$：网络中期望的最大度。对 $p_k\sim k^{-\gamma}$ 的无标度网络，$k_{\max}\sim k_{\min}N^{1/(\gamma-1)}$。
:::

比较两个指数即可判断冲突是否存在（Boguñá, Pastor-Satorras & Vespignani, 2004, *EPJ B*）：

- $\gamma\ge3$ 或泊松度分布：$1/(\gamma-1)\le1/2$，$k_{\max}$ 增长不快于 $k_s$，没有冲突；
- $2<\gamma<3$：$k_{\max}\gg k_s$，度介于两者之间的枢纽必然“缺边”，简单图会表现出异配。

而许多生物网络报告的度指数正落在 $2<\gamma<3$。严格推导见[数学推导与算法](degree-correlations.derivations.html)。

### 消除结构性相关的办法

1. 允许重边（多重图），网络回到中性；
2. 删除度大于 $k_s$ 的节点，或在生成模型中把度上限设为 $k_s$；
3. 最常用：不去“消除”它，而是在相同度序列、同为简单图的随机网络中重新计算度相关，把这部分当作基线（见下一节）。

代码示例“结构截断与伪异配”中，$\gamma=2.2$、$N=5000$ 的配置模型保留重边时 $r\approx-0.01$，合并重边与自环成为简单图后 $r\approx-0.14$；把度上限截在 $k_s$ 附近后 $r$ 回升到约 $-0.05$；同平均度的 ER 图 $r\approx0$。

### 熵的视角

Johnson 等（2010, *PRL*）计算了给定度序列下不同相关程度的网络构型数（熵），发现对高度异质的度序列，熵最大的构型通常是异配的而不是中性的。也就是说，在没有任何特殊机制时，“随机”得到的无标度简单图本来就偏异配；只有偏离这一最大熵预期的相关才提示存在特殊的形成机制。这与下面的保度随机化检验是同一个逻辑。

## 度保持随机化检验 {#randomization-tests}

### 两种随机化

度相关的检验问题是：观测到的 $k_{nn}(k)$ 或 $r$ 是否超出了“同一度序列的随机网络”能产生的范围。Barabási 书第 7 章区分两种保度随机化：

- **R-S（保持简单图）**：双边交换时拒绝产生重边或自环的交换。若观测的 $k_{nn}(k)$ 与 R-S 随机网络的 $k_{nn}^{R\text{-}S}(k)$ 无法区分，观测到的相关完全是结构性的；
- **R-M（允许重边）**：接受所有交换。它总是给出中性网络（水平的 $k_{nn}$），主要用作自洽检查。

真正有信息的是观测值与 R-S 的比较。按这一方法，第 7 章的十个参考网络中：社会网络（合作网络、演员网络、手机通话网络）的同配性不能被度分布解释；蛋白质相互作用网络与代谢网络的 $k_{nn}(k)$ 与 R-S 版本几乎重合，即它们的异配主要是结构性的；万维网的异配只能被度分布部分解释。需要注意，这些结论依赖于具体的数据版本（书中使用的是早期酵母相互作用图谱）。

### Maslov–Sneppen 的相关剖面

Maslov 与 Sneppen（2002）不压缩为单个数，而是对每一对度 $(k_0,k_1)$ 比较观测的联合分布 $P(k_0,k_1)$ 与保度随机网络的均值 $P_r(k_0,k_1)$，画出比值 $P/P_r$ 及其 $z$ 分数的二维图（相关剖面，correlation profile）。他们在酵母蛋白质相互作用网络和转录调控网络中都发现：高度节点之间的连接被系统性压低，高度与低度节点之间的连接被增强。这种二维剖面比 $r$ 保留了更多信息，可以看出相关集中在哪个度区间。

### 实施要点

1. **随机化次数与混合**：每个随机网络的交换次数通常取边数的 10–100 倍；可以检查 $r$ 随交换次数的变化是否已平稳。
2. **“合并重边”不是均匀抽样**：先用配置模型生成多重图、再合并重边与删自环（erased configuration model），得到的网络与“给定度序列的均匀随机简单图”不是同一分布，重尾时差别明显（Fosdick 等, 2018, *SIAM Review*）。代码示例中同一度序列的 erased 配置模型 $r\approx-0.07$，充分交换后的保度随机网络 $r\approx-0.11$。
3. **报告方式**：给出观测值、零分布均值与标准差、$z$ 分数和经验 $p$ 值 $\hat p=(1+\#\{r_m\le r_{\text{obs}}\})/(M+1)$。
4. **零模型保留什么**：保度随机化保留度序列但打乱了模块、空间位置与聚集。若网络有强模块或空间嵌入，相关性的差异可能来自这些被打乱的结构，而不是“度对度的偏好”（见[零模型与空模型](network-construction.null-models.html)）。

::: {.callout-bio}
代码示例“度保持随机化检验”构造了两张度序列相同的幂律网络：网络 A 是给定度序列的随机简单图，$r\approx-0.12$，与 100 个保度随机网络（$-0.110\pm0.009$）无显著差异；网络 B 额外做了异配重连，$r\approx-0.24$，$z\approx-14$。两者的 $r$ 都为负，但只有 B 的异配需要额外的生物学解释。把这一检验用于真实相互作用组时，还要考虑数据中的研究偏倚：被研究得多的蛋白既度高又更可能与其他被研究得多的蛋白有记录的相互作用，这会以难以预测的方向改变度相关（见[测量误差、缺失与偏倚](network-construction.bias-and-missingness.html)）。
:::

## 生成具有度相关的网络 {#generating-correlated-networks}

### 常见模型的度相关

| 模型 | 度相关 | 说明 |
|---|---|---|
| ER 随机图 | 中性 | 没有枢纽，也没有结构截断问题 |
| 配置模型（允许重边与自环） | 中性 | 枢纽之间的“多余”边以重边形式存在 |
| 配置模型（简单图） | 结构性异配 | $2<\gamma<3$ 时尤其明显 |
| 隐变量模型（禁止重边） | 异配，$k_{nn}(k)\sim k^{-1}$ | Boguñá & Pastor-Satorras（2003, *PRE*） |
| BA 模型 | 渐近中性 | Newman（2002）给出 $r\to0$；有限规模下仍可测到负的 $r$，代码示例中 $N=3000$ 时 $r\approx-0.08$ |
| 初始吸引力模型 | $\gamma<3$ 异配、$\gamma=3$ 中性、$\gamma>3$ 弱同配 | Barrat & Pastor-Satorras（2005） |

### Xulvi-Brunet–Sokolov 重连

Xulvi-Brunet 与 Sokolov（2004, *PRE*）提出一种在保持度序列的同时调节相关的重连算法：

1. 随机选两条边，把四个端点按度从大到小记为 $a,b,c,d$；
2. 以概率 $p$ 做确定性配对：同配方向连 $a\!-\!b$ 与 $c\!-\!d$，异配方向连 $a\!-\!d$ 与 $b\!-\!c$；以概率 $1-p$ 随机配对；
3. 若产生重边或自环则拒绝；重复直至平稳。

$p=1$ 时得到给定度序列下近似最大（或最小）的相关；$p$ 越小相关越弱。对重尾度序列，即使 $p=1$ 的“最大同配”网络，在高 $k$ 端也会因结构截断而出现下降的 $k_{nn}(k)$：低度部分同配、高度部分异配。这种混合形态与某些真实网络（Barabási 书中的引文网络）相似。

### 按目标联合分布生成

Newman（2003）给出一种 Metropolis 型蒙特卡洛方法，从指定的 $e_{jk}$ 生成网络；dK 序列方法（Mahadevan 等, 2006；Orsini 等, 2015）则在保持 2K 统计量（联合度分布）的条件下随机化其余结构，可以作为比保度随机化更严格的零模型：若一个现象在 2K 随机网络中依然存在，它就可以用度相关来解释。生成任意 $e_{jk}$ 且同时满足简单图约束的网络，至今仍没有通用而高效的方法。

## 富人俱乐部系数及其归一化 {#rich-club}

### 定义

::: {.callout-def}
**富人俱乐部系数**（rich-club coefficient; Zhou & Mondragón, 2004, *IEEE Communications Letters*）：度大于 $k$ 的 $N_{>k}$ 个节点之间实际边数 $E_{>k}$ 占可能边数的比例，

$$
\phi(k)=\frac{2E_{>k}}{N_{>k}(N_{>k}-1)}.
$$

**归一化富人俱乐部系数**（Colizza 等, 2006, *Nature Physics*）：$\rho_{\text{ran}}(k)=\phi(k)/\phi_{\text{ran}}(k)$，$\phi_{\text{ran}}(k)$ 是同一度序列的保度随机网络的富人俱乐部系数。$\rho_{\text{ran}}(k)>1$（且统计上显著）才是富人俱乐部的证据。
:::

### 为什么必须归一化

度高的节点“天然”更可能彼此相连。Colizza 等推导出无相关网络在大 $k$ 处 $\phi_{\text{unc}}(k)\sim k^2/(\langle k\rangle N)$，即使完全随机，$\phi(k)$ 也随 $k$ 单调上升。早期一些研究据此认为互联网存在富人俱乐部；Colizza 等用 $\rho_{\text{ran}}$ 重新分析，发现科学合作网络有明显的富人俱乐部，而蛋白质相互作用网络和自治系统层面的互联网 $\rho_{\text{ran}}(k)$ 随 $k$ 下降、低于 1，即高度蛋白之间的连接反而少于随机预期。他们的解释是，高度蛋白各自主导不同的功能模块，而不是组成一个互连的核心。

代码示例“富人俱乐部系数”显示：BA 网络的 $\phi(k)$ 从 $k>5$ 时的 0.010 上升到 $k>40$ 时的 0.26，但 $\rho\approx0.8$–$1.0$；植入富人俱乐部的网络在 $k>20$ 后 $\rho\approx4$。当 $N_{>k}$ 只剩个位数时（BA 网络 $k>60$ 只有 7 个节点），$\rho$ 的波动很大，不应据此下结论。

### 富人俱乐部与同配性的关系

两者都与“枢纽连不连枢纽”有关，但不是同一件事。$r$ 衡量所有边两端度的整体相关，由大量低度节点之间的边主导；$\phi(k)$ 只看度大于 $k$ 的子图密度。一个网络可以 $r<0$（大量枢纽-叶子边）而仍有富人俱乐部（少数最高度节点互相全连），人脑结构网络就常是这种情况。反过来，同配网络也不一定在最高度端形成稠密核心。

### 统计检验与变体

- **检验**：对每个 $k$ 生成 $M$ 个保度随机网络，得到 $\phi_{\text{ran}}(k)$ 的零分布，计算经验 $p$ 值；不同 $k$ 的检验高度相关，可用置换得到的最大统计量控制族错误率，或预先规定 $k$ 的区间。
- **加权富人俱乐部**：Opsahl 等（2008, *PRL*）把“富”定义为高强度等节点属性，计算富节点之间的权重占比，并以保持拓扑、打乱权重的零模型归一化。
- **按其他属性定义“富”**：可用中心性、模块参与系数等替代度，但零模型应相应调整。
- **与空间零模型的关系**：脑网络中高度脑区之间往往距离远、连接代价高，保度随机网络不保留空间结构；富人俱乐部的强度在空间约束零模型下可能减弱（见[脑连接组](brain-connectome.topology.html)）。

::: {.callout-bio}
van den Heuvel 与 Sporns（2011, *J Neurosci*）在 21 名健康被试的弥散成像结构网络中，用 $\rho_{\text{ran}}(k)$ 发现了由楔前叶、额上回、顶上皮层以及海马、壳核、丘脑等组成的富人俱乐部（精读见 [van den Heuvel & Sporns 2011](paper-vandenheuvel2011_richclub.html)）。van den Heuvel 等（2012, *PNAS*）进一步指出富人俱乐部连接长、代价高，却承载大量脑区间的最短路径。在细胞分辨率上，Towlson 等（2013, *J Neurosci*）在 279 个神经元、2287 条突触连接的秀丽隐杆线虫连接组中识别出由 11 个神经元组成的富人俱乐部，几乎全部是运动回路的中间神经元；Harriger 等（2012, *PLoS ONE*）在猕猴皮层网络中也报告了富人俱乐部。
:::

## 聚集谱 C(k) 与层次模块性 {#clustering-spectrum}

### 三点相关

$k_{nn}(k)$ 是两点相关。更高一阶的统计是：度为 $k$ 的节点的两个邻居之间是否相连。**聚集谱**（clustering spectrum）$C(k)$ 是度为 $k$ 的节点局部聚集系数的平均。它对应条件概率 $P(k^{(1)},k^{(2)}\mid k)$ 与“两个邻居相连”的概率，是三点相关的一个压缩。对无相关的稀疏随机网络，$C(k)$ 与 $k$ 无关，近似为 $(\langle k^2\rangle-\langle k\rangle)^2/(\langle k\rangle^3N)$。

### 层次模块网络

Ravasz 等（2002, *Science*）分析了 43 种生物的代谢网络，发现它们由许多小而紧密的模块逐级组合成更大、更松散的单元，聚集系数随度按幂律下降；在大肠杆菌中，这种层次模块与已知代谢功能有较好的对应。Ravasz 与 Barabási（2003, *PRE*）用一个确定性的层次模型说明这一结构：从 5 个节点的完全图出发，每一步复制 4 份，把副本的最外围节点连到原始中心节点。这样生成的网络同时具有：

- 无标度度分布；
- 与网络规模无关的高平均聚集系数；
- $C(k)\sim k^{-1}$：低度节点处在小而紧密的模块内，邻居彼此相连；枢纽连接许多彼此不相连的模块。

BA 模型与 ER 模型的 $C(k)$ 都近似与 $k$ 无关，因此 $C(k)$ 的负斜率被用作层次模块性的一个信号。代码示例“聚集谱”中，3 层迭代的层次网络（625 个节点）平均聚集系数 0.82，$\log C(k)$ 对 $\log k$ 的斜率约 $-1.1$；同规模 BA 网络斜率约 $-0.1$。

### 解读时的注意点

::: {.callout-warn}
1. **度相关会影响 $C(k)$**：高度节点的可能三角形数量受其邻居度的限制。Soffer 与 Vázquez（2005, *PRE*）指出，在异配网络中高度节点的邻居多为低度节点，$C(k)$ 会因度相关而系统性下降；他们提出用“邻居之间实际可能的最大边数”而非 $k(k-1)/2$ 作分母的修正聚集系数。
2. **$C(k)$ 下降是必要而非充分条件**：许多没有层次模块的机制（例如空间嵌入、几何随机图、某些复制-分化模型）也能产生下降的 $C(k)$。要支持“层次模块”，还应直接检验模块的嵌套结构（见[社团结构与社区发现](community-structure.spectral-hierarchical.html)）。
3. **相关网络**：基于相关阈值化的网络因相关的传递性本身就有高聚集（Zalesky 等, 2012），$C(k)$ 的形状受阈值强烈影响。
:::

## k-核分解 {#k-core}

### 定义

::: {.callout-def}
**$k$-核**（$k$-core; Seidman, 1983, *Social Networks*）：反复删除度小于 $k$ 的节点后剩下的最大子图；其中每个节点在子图内的度都至少为 $k$。

**核数**（coreness，core number）$c_i$：节点 $i$ 所属的最大 $k$-核的 $k$。核数为 $k$ 的节点构成 **$k$-壳**（$k$-shell）。

**$k$-核分解**：依次求出所有 $k$-核，得到一组嵌套的子图 $\text{core}_1\supseteq\text{core}_2\supseteq\cdots$。
:::

### 剥离算法

从 $k=1$ 开始，反复删去当前度小于 $k$ 的节点（删除会降低邻居的度，可能引发连锁删除），直到没有可删的节点，剩下的就是 $k$-核；然后 $k\leftarrow k+1$。Batagelj 与 Zaversnik（2011, *Advances in Data Analysis and Classification*）用“按当前度分桶”的方法使整个分解的时间复杂度为 $O(L)$。伪代码见[数学推导与算法](degree-correlations.derivations.html)，代码示例用最小堆实现，复杂度 $O(L\log N)$，并与 `nx.core_number` 逐节点对照。

**算例**：一个三角形 $\{a,b,c\}$ 加上一条挂在 $c$ 上的路径 $c-d-e$。删去度为 1 的 $e$，$d$ 的度降为 1，也被删去；剩下三角形中每个节点度为 2，于是 $a,b,c$ 的核数为 2，$d,e$ 的核数为 1。注意 $c$ 的度为 3，但核数只有 2：核数衡量的是“嵌在多稠密的子图里”，而不是边数。

### 核数、度与度相关

核数与度高度相关但不等同。度相同的节点可以处在不同的壳层（代码示例中，幂律随机网络里度为 6 的节点分布在 2、3、4 三个壳层）；一个连着很多叶子的枢纽可能核数很低。度相关直接影响核结构：同配网络中高度节点彼此相连，形成深而稠密的内核；异配网络的内核浅。代码示例中，同一度序列的网络经同配重连后，最大核数从 9 升到 20。还要注意，BA 网络中每个新节点恰好带 $m$ 条边加入，整张图就是一个 $m$-核，壳层结构是平凡的，不适合作为 k-核分析的模型示例。

### 应用

- **影响力传播者**：Kitsak 等（2010, *Nature Physics*）在多个真实网络的 SIR/SIS 模拟中发现，单个起始节点的传播范围由其核数比由度或介数中心性预测得更好（精读见 [Kitsak 2010](paper-kitsak2010_spreaders.html)，与[网络上的传播与免疫](spreading.html)相联系）。
- **相互作用组的“骨架”**：Wuchty 与 Almaas（2005, *Proteomics*）对酵母蛋白质相互作用网络做核分解，发现越靠内层的核中，必需蛋白和进化保守蛋白的比例越高，而且这一结果对相互作用数据的误差较稳健。
- **脑结构核心**：Hagmann 等（2008, *PLoS Biology*）用 $k$-核与强度版本的 $s$-核分解弥散谱成像结构网络，识别出位于后内侧与顶叶皮层的结构核心（精读见 [Hagmann 2008](paper-hagmann2008_structuralcore.html)）。
- **理论**：Dorogovtsev、Goltsev 与 Mendes（2006, *PRL*）研究了随机网络中 $k$-核的出现条件（$k$-核渗流），对 $k\ge3$ 它与普通巨分支出现的连续相变性质不同。

## 度相关对网络过程的影响 {#impact-on-dynamics}

度相关改变的不只是一个描述性数字，它会改变发生在网络上的过程。下面的结论多来自模型网络，在真实生物网络中往往与模块、空间约束等因素同时存在。

### 巨连通分支与鲁棒性

Newman（2002）求解了具有给定 $e_{jk}$ 的随机网络的渗流问题：巨分支在矩阵 $m_{jk}=k\,e_{jk}/q_j$（以剩余度为下标）的最大特征值达到 1 时出现。无相关时 $m$ 是秩 1 矩阵，条件退化为熟悉的 Molloy–Reed 判据 $\langle k^2\rangle/\langle k\rangle=2$。结论是：

- **同配网络**更早形成巨分支（高度节点相互连接，在稀疏时就能连成一片），对删除高度节点也更稳健（枢纽彼此冗余）；
- 但在边较多时，同配网络的巨分支反而更小，因为大量低度节点只与低度节点相连，未被枢纽“收编”；
- **异配网络**在删除枢纽时更脆弱：每个枢纽带走一批只连向它的低度节点。Vázquez 与 Moreno（2003, *PRE*）给出了相关网络上点渗流与键渗流阈值的一般表达式。

代码示例“度相关如何改变……”中，同一张 ER 图（$N=2000$，$\langle k\rangle=4$）重连后，保留 30% 的边时同配版巨分支占 0.34、异配版 0.26；保留 90% 时顺序反过来（0.964 对 0.973）。网络在蓄意攻击下的崩解见[网络鲁棒性、渗流与级联失效](robustness.html)。

### 流行病传播

异质平均场 SIS 模型中，度为 $k$ 的节点感染比例 $\rho_k$ 满足

$$
\frac{d\rho_k}{dt}=-\rho_k+\lambda k(1-\rho_k)\sum_{k'}P(k'\mid k)\rho_{k'} .
$$

在无病态附近线性化，传播阈值由矩阵 $C_{kk'}=k\,P(k'\mid k)$ 的最大特征值 $\Lambda_m$ 决定：$\lambda_c=1/\Lambda_m$（Boguñá & Pastor-Satorras, 2002, *PRE*）。无相关时 $\Lambda_m=\langle k^2\rangle/\langle k\rangle$，回到[度异质性与流行病阈值](spreading.epidemic-threshold.html)中的结果。几个要点：

- 同配性使高度节点形成相互感染的“储库”，通常降低阈值、使疾病在整体稀疏时也能持续；但由于传播主要局限在这个高度节点核心内，最终波及的范围可能更小（Newman, 2002）；
- Boguñá、Pastor-Satorras 与 Vespignani（2003, *PRL*）证明：只要度分布的二阶矩发散，无论同配还是异配，无标度网络的传播阈值都趋于 0；其原因是细致平衡强制 $\sum_k k\,p_k\,k_{nn}(k)=\langle k^2\rangle$（推导见[数学推导与算法](degree-correlations.derivations.html)）；
- 在有限网络上，淬火平均场阈值约为 $1/\lambda_1$（$\lambda_1$ 为邻接矩阵最大特征值）。代码示例中，同配重连使 $\lambda_1$ 从 5.23 升到 5.93，异配重连降到 4.92。

### 同步

可同步性常用拉普拉斯矩阵特征值比 $\lambda_N/\lambda_2$ 衡量（越小越容易同步，见[拉普拉斯谱与可同步性](synchronization.master-stability.html)）。同配使高度节点聚成核心、低度节点形成长链，$\lambda_2$ 变小，可同步性变差；di Bernardo、Garofalo 与 Sorrentino（2007, *IJBC*）系统研究了度相关对振子网络同步的影响。代码示例中三张度序列相同的网络，$\lambda_N/\lambda_2$ 依次为 173（同配）、94（原始）、59（异配）。同配网络的平均路径长度略短而直径更长，也与这一图景一致（Barabási 书第 7.7 节）。

### 可控性

结构可控性中驱动节点数由最大匹配决定（见[结构可控性与最大匹配](controllability.structural-controllability.html)）。Pósfai 等（2013, *Scientific Reports*）发现，聚集与模块性对驱动节点数没有明显影响，而度相关的作用取决于是哪一种有向相关（入-入、出-出、出-入等）：驱动节点数可以随相关系数线性变化、二次变化或不变。因此在比较两张调控网络的驱动节点比例时，应检查它们的有向度相关是否不同。

## 数学推导与算法 {#derivations}

### A. 细致平衡与中性网络的 $k_{nn}$

由 $e_{kk'}$ 的两种写法 $e_{kk'}=q_kP(k'\mid k)=q_{k'}P(k\mid k')$ 及 $q_k=kp_k/\langle k\rangle$，得细致平衡 $kp_kP(k'\mid k)=k'p_{k'}P(k\mid k')$。

把 $k_{nn}(k)$ 按 $kp_k$ 加权求和：

$$
\sum_k k\,p_k\,k_{nn}(k)=\sum_k\sum_{k'}k'\,k\,p_k\,P(k'\mid k)
=\langle k\rangle\sum_{k'}k'\sum_k e_{kk'}=\langle k\rangle\sum_{k'}k'q_{k'}=\langle k^2\rangle .
$$

这一恒等式对任何相关结构都成立。若 $\langle k^2\rangle$ 随 $N$ 发散，则必有某些 $k$ 的 $k_{nn}(k)$ 发散，矩阵 $C_{kk'}=kP(k'\mid k)$ 的最大特征值也无界，SIS 阈值趋于 0。中性网络中 $P(k'\mid k)=q_{k'}$，直接得到 $k_{nn}(k)=\langle k^2\rangle/\langle k\rangle$。

### B. 度相关系数的边列表形式

把每条无向边记为两个有序对 $(j_i,k_i)$ 与 $(k_i,j_i)$，共 $2L$ 个。$x$ 与 $y$ 的边际分布相同（都是 $q_k$），均值 $\bar k_e=\frac{1}{2L}\sum_i(j_i+k_i)$，方差 $\frac{1}{2L}\sum_i(j_i^2+k_i^2)-\bar k_e^2$，协方差 $\frac{1}{L}\sum_i j_ik_i-\bar k_e^2$。二者之比就是上文的 $r$。把求和改写为对度对 $(j,k)$ 计数，即得 $r=\sum_{jk}jk(e_{jk}-q_jq_k)/\sigma_q^2$。由于 Pearson 相关对平移不变，用度或剩余度结果相同。

### C. 结构截断

设 $E_{kk'}$ 为连接度 $k$ 与 $k'$ 节点的边数（$k=k'$ 时计两次），$E_{kk'}=\langle k\rangle N e_{kk'}$。简单图中它不能超过

$$
m_{kk'}=\min\{kN_k,\;k'N_{k'},\;N_kN_{k'}\},
$$

分别对应“度 $k$ 一侧的边端总数”“度 $k'$ 一侧的边端总数”“两组节点之间的节点对数”。定义 $r_{kk'}=E_{kk'}/m_{kk'}\le1$。当 $k,k'$ 足够大（$k>Np_{k'}$ 且 $k'>Np_k$）时，最小值是 $N_kN_{k'}=N^2p_kp_{k'}$。中性网络中 $e_{kk'}=kk'p_kp_{k'}/\langle k\rangle^2$，于是

$$
r_{kk'}=\frac{\langle k\rangle N\,kk'p_kp_{k'}/\langle k\rangle^2}{N^2p_kp_{k'}}=\frac{kk'}{\langle k\rangle N}.
$$

令 $r_{k_sk_s}=1$，得 $k_s=(\langle k\rangle N)^{1/2}$。它与度分布形式无关。与 $k_{\max}\sim N^{1/(\gamma-1)}$ 比较，$\gamma<3$ 时 $k_{\max}\gg k_s$，中性的简单无标度网络不存在。

### D. 无相关网络的富人俱乐部系数

在无相关网络中，度为 $k_i$ 与 $k_j$ 的两节点相连的概率约为 $k_ik_j/(\langle k\rangle N)$（不超过 1 时）。富节点集合 $R=\{i:k_i>k\}$ 内的期望边数为

$$
\mathbb E[E_{>k}]\approx\frac12\sum_{i\ne j\in R}\frac{k_ik_j}{\langle k\rangle N}\approx\frac{\big(\sum_{i\in R}k_i\big)^2}{2\langle k\rangle N},
\qquad
\phi_{\text{unc}}(k)\approx\frac{\bar k_R^{\,2}}{\langle k\rangle N},
$$

其中 $\bar k_R$ 为富节点的平均度，它随阈值 $k$ 增大，所以 $\phi_{\text{unc}}(k)$ 随 $k$ 单调上升，大致按 $k^2$ 增长（直到结构截断使概率饱和）。这就是必须用 $\phi_{\text{ran}}$ 归一化的原因。

### E. 算法

```text
算法 1  邻居平均度函数 k_nn(k)（对数分箱）
输入：无向简单图 G
1. 对每个节点 i：k_nn,i ← (Σ_{j∈N(i)} k_j) / k_i          # O(L)
2. 取对数间隔的度区间 [b_0,b_1), [b_1,b_2), …
3. 对每个区间：k̄ ← 区间内节点度的均值；k_nn ← 区间内 k_nn,i 的均值（节点数 < 3 时跳过）
4. 输出 (k̄, k_nn) 序列；在选定区间内对 log k_nn ~ log k 做线性拟合，斜率为 μ
复杂度：O(L + N)
```

```text
算法 2  Xulvi-Brunet–Sokolov 重连（保度、保持简单图）
输入：简单图 G，交换次数 S，方向 mode ∈ {同配, 异配}，概率 p
1. 重复直到成功交换 S 次：
2.     随机取两条边 (a,b)、(c,d)；若四个端点有重复，跳过
3.     以概率 p：按度从大到小排序为 v1 ≥ v2 ≥ v3 ≥ v4
4.         同配：新边 (v1,v2)、(v3,v4)；异配：新边 (v1,v4)、(v2,v3)
5.     否则：随机打乱四个端点，两两配对
6.     若新边已存在（会产生重边）：拒绝
7.     删除旧边，加入新边
复杂度：每次尝试 O(1)（用哈希集合判断边是否存在）
```

```text
算法 3  k-核分解（按当前度剥离）
输入：无向图 G
1. d[v] ← deg(v)；把所有节点放入以 d 为键的桶（或最小堆）
2. k ← 0
3. 当还有未删除节点：
4.     取出当前 d 最小的节点 v；k ← max(k, d[v])；core[v] ← k；删除 v
5.     对 v 的每个未删除邻居 u：d[u] ← d[u] − 1，更新其在桶中的位置
6. 返回 core
复杂度：桶实现 O(L)（Batagelj & Zaversnik）；堆实现 O(L log N)
```

```text
算法 4  富人俱乐部检验
输入：图 G，度阈值集合 K，随机网络数 M
1. 对每个 k ∈ K：计算 φ_obs(k)
2. 对 m = 1..M：用双边交换生成保度随机网络 G_m（交换次数 ≥ 10L），计算 φ_m(k)
3. φ_ran(k) ← mean_m φ_m(k)；ρ(k) ← φ_obs(k) / φ_ran(k)
4. p(k) ← (1 + #{m: φ_m(k) ≥ φ_obs(k)}) / (M + 1)
5. 多个 k 的检验：用每次置换中 max_k [φ_m(k)/φ_ran(k)] 构造零分布，或预先规定 k 区间
6. 报告 ρ(k) 曲线、N_{>k} 与 p(k)；N_{>k} 很小的区间只作描述
```

## 生物医学应用 {#biomedical}

### 蛋白质相互作用网络：枢纽回避及其解释

酵母蛋白质相互作用网络是异配网络的典型例子：Newman（2003）报告 $r=-0.156$；Maslov 与 Sneppen（2002）发现高度蛋白之间的连接被系统性压低，并提出这种结构减少了不同功能模块之间的串扰，把有害扰动的影响局限在局部。Colizza 等（2006）进一步显示该网络没有富人俱乐部。

但这一现象至少有三种解释需要区分：

1. **结构性**：重尾度分布加简单图约束本身就产生异配。Barabási 书第 7 章用 R-S 随机化发现，早期酵母图谱的 $k_{nn}(k)$ 与保度随机版本几乎重合；
2. **实验方法**：酵母双杂交以“诱饵-猎物”方式筛选，少数“粘性”诱饵产生大量与低度蛋白的相互作用；亲和纯化-质谱数据把复合物展开成星形或团时，度相关的方向截然不同（见[节点与边的定义](network-construction.nodes-and-edges.html)）；
3. **生物学**：枢纽蛋白功能上分化。Han 等（2004, *Nature*）根据与相互作用伙伴的共表达程度区分“派对枢纽”（与伙伴同时表达）与“约会枢纽”（在不同时间、地点与不同伙伴结合），后者连接不同模块，与枢纽回避的图景相容（精读见 [Han 2004](paper-han2004_datehubs.html)）。

报告 PPI 网络度相关时，应写明数据版本与实验类型，并给出保度随机化下的比较。

### 基因调控网络：有向的度相关

转录调控网络是有向网络，出度高的节点是调控很多靶基因的转录因子，入度高的节点是受多个因子调控的基因。Maslov 与 Sneppen（2002）在酵母调控网络中同样发现枢纽之间的连接被压低。分析调控网络时应分别计算四种有向相关（Foster 等, 2010；Piraveenan 等, 2012），因为“转录因子调控转录因子”的连接（出-出组合）与级联结构、前馈环等基序密切相关（见[网络基序](molecular-networks.network-motifs.html)）。度相关还会改变驱动节点数（Pósfai 等, 2013），这在[网络可控性](controllability.html)分析中需要考虑。

### 代谢网络：层次模块性

Ravasz 等（2002）在 43 种生物的代谢网络中发现聚集系数随度按幂律下降，提出代谢网络由小而紧密的模块层次组合而成；在大肠杆菌中，这些模块与已知代谢通路有较好的对应。代谢网络同时是强异配网络（Newman, 2003 报告大肠杆菌代谢网络 $r=-0.240$），而按 Barabási 书的 R-S 分析，这种异配主要是结构性的。代谢网络的构建（是否去除 ATP、水等“货币代谢物”）会显著改变枢纽与度相关，解读前应确认构网规则。

### 脑网络：富人俱乐部与结构核心

结构脑网络中的富人俱乐部（van den Heuvel & Sporns, 2011）、结构核心（Hagmann 等, 2008）和线虫神经元富人俱乐部（Towlson 等, 2013）是本专题“高阶统计”在神经科学中最有影响的应用。在疾病研究中，van den Heuvel 等（2013, *JAMA Psychiatry*）报告了精神分裂症患者富人俱乐部节点之间的结构连接密度降低，并与功能动力学的改变相联系（见[脑连接组](brain-connectome.biomedical.html)）。

::: {.callout-bio}
对阈值化的功能连接网络，度同配性很大程度上由构网方式决定。代码示例“阈值化相关网络中的同配性”模拟了大小为 30、15、10、5 个脑区的四个功能系统：大系统里的脑区仅因同系统成员多而度高，又主要连向同系统的脑区，于是 $r>0$；密度从 0.05 增加到 0.20 时，$r$ 从约 0.06 升到 0.49，而保度零模型下 $r\approx-0.11$。这与 Power 等（2013）指出的“功能网络中度被模块大小绑架”是同一现象，也对应 Newman 与 Park（2003）的社团导致同配机制。因此，在功能连接网络中报告的“同配性异常”需要排除模块大小和密度的影响。
:::

### 网络医学中的度偏倚

疾病基因、药物靶点往往是被研究得多的高度蛋白。网络邻近度、疾病模块检验中常用的“度匹配随机基因集”零模型，正是为了控制度与度相关带来的偏倚：高度节点彼此之间的距离本来就短。若相互作用组是异配的，高度节点之间直接相连的概率较低，但通过一两步就能相互到达，这影响邻近度零分布的形状（见[统计要点：参考网络、度偏倚、显著性与外部验证](network-medicine.statistical-validation.html)）。

## 适用范围与常见误用 {#limitations}

::: {.callout-warn}
1. **把负的 $r$ 直接解释为“枢纽回避”的生物学机制。** 重尾度分布的简单图本身就偏异配；必须与同一度序列的保度随机网络（R-S）比较，并报告零分布。
2. **跨网络比较 $r$ 的绝对值。** $r$ 依赖网络规模和度序列，大网络中的 $r$ 被压向 0；比较不同规模的网络时应同时报告 Spearman 秩相关、$k_{nn}(k)$ 曲线和零模型 $z$ 分数。
3. **只看未归一化的 $\phi(k)$。** 随机网络的 $\phi(k)$ 也随 $k$ 上升；富人俱乐部的证据是 $\rho_{\text{ran}}(k)>1$ 且显著，并且 $N_{>k}$ 不能太小。
4. **零模型选错或混合不足。** “合并重边”的配置模型不是均匀随机简单图；交换次数不足时随机网络保留原图结构。对空间嵌入的脑网络，还应比较空间约束零模型。
5. **忽视构网方式。** 阈值、密度、加权与二值化、复合物展开方式、货币代谢物处理都会改变度相关；功能连接网络的同配性可以完全由模块大小和阈值产生。
6. **有向网络无向化。** 调控网络、神经元网络无向化后的 $r$ 混合了四种不同的有向相关，可能互相抵消。
7. **把 $C(k)\sim k^{-1}$ 当作层次模块的证明。** 它只是相容的证据，度相关、空间约束等都能产生下降的 $C(k)$。
8. **把 $k$-核当作“重要性”的通用度量。** 核数对少量边的增删敏感（尤其在稀疏、含假阳性的相互作用数据中），且只在特定动力学（如单点起始的传播）下有预测意义。
9. **用模型网络的结论推断真实系统。** 度相关对渗流、传播、同步的影响多在保持度序列的重连模型中得出；真实网络中度相关与模块、聚集、空间结构同时变化，很难单独归因。
:::

## 关联知识 {#related}

- [网络结构指标与随机图](network-metrics.html)：度、度分布与聚集系数的定义；ER 随机图是中性网络的基准。
- [小世界与无标度网络模型](network-models.html)：配置模型、BA 模型与无标度度分布；结构截断只在 $2<\gamma<3$ 时出现。
- [网络构建与统计验证](network-construction.null-models.html)：保度随机化、配置模型与经验 $p$ 值的一般原理。
- [社团结构与社区发现](community-structure.html)：社团结构可以产生同配；类别同配系数与模块度同形。
- [网络上的传播与免疫](spreading.html)：相关网络中的传播阈值、$k$-核与影响力传播者。
- [网络鲁棒性、渗流与级联失效](robustness.html)：同配与异配网络在随机失效与蓄意攻击下的差异。
- [同步与协同动力学](synchronization.html)与[网络可控性与稳定性](controllability.html)：度相关改变可同步性与驱动节点数。
- [脑连接组：结构与功能连接](brain-connectome.html)与[生物分子网络与拓扑特征](molecular-networks.html)：富人俱乐部、结构核心与 PPI 的度异配。

## 核心文献 {#references}

**度相关的定义与测量**

- Pastor-Satorras R, Vázquez A, Vespignani A. Dynamical and correlation properties of the Internet. *Physical Review Letters*, 2001, 87: 258701. DOI: [10.1103/PhysRevLett.87.258701](https://doi.org/10.1103/PhysRevLett.87.258701)
- Vázquez A, Pastor-Satorras R, Vespignani A. Large-scale topological and dynamical properties of the Internet. *Physical Review E*, 2002, 65: 066130. DOI: [10.1103/PhysRevE.65.066130](https://doi.org/10.1103/PhysRevE.65.066130)
- Newman MEJ. Assortative mixing in networks. *Physical Review Letters*, 2002, 89: 208701. DOI: [10.1103/PhysRevLett.89.208701](https://doi.org/10.1103/PhysRevLett.89.208701)
- Newman MEJ. Mixing patterns in networks. *Physical Review E*, 2003, 67: 026126. DOI: [10.1103/PhysRevE.67.026126](https://doi.org/10.1103/PhysRevE.67.026126)
- Newman MEJ, Park J. Why social networks are different from other types of networks. *Physical Review E*, 2003, 68: 036122. DOI: [10.1103/PhysRevE.68.036122](https://doi.org/10.1103/PhysRevE.68.036122)
- Foster JG, Foster DV, Grassberger P, Paczuski M. Edge direction and the structure of networks. *PNAS*, 2010, 107: 10815–10820. DOI: [10.1073/pnas.0912671107](https://doi.org/10.1073/pnas.0912671107)
- Litvak N, van der Hofstad R. Uncovering disassortativity in large scale-free networks. *Physical Review E*, 2013, 87: 022801. DOI: [10.1103/PhysRevE.87.022801](https://doi.org/10.1103/PhysRevE.87.022801)
- Barrat A, Barthélemy M, Pastor-Satorras R, Vespignani A. The architecture of complex weighted networks. *PNAS*, 2004, 101: 3747–3752. DOI: [10.1073/pnas.0400087101](https://doi.org/10.1073/pnas.0400087101)
- Feld SL. Why your friends have more friends than you do. *American Journal of Sociology*, 1991, 96: 1464–1477. DOI: [10.1086/229693](https://doi.org/10.1086/229693)

**结构截断、零模型与生成模型**

- Maslov S, Sneppen K. Specificity and stability in topology of protein networks. *Science*, 2002, 296: 910–913. DOI: [10.1126/science.1065103](https://doi.org/10.1126/science.1065103)
- Boguñá M, Pastor-Satorras R, Vespignani A. Cut-offs and finite size effects in scale-free networks. *European Physical Journal B*, 2004, 38: 205–209. DOI: [10.1140/epjb/e2004-00038-8](https://doi.org/10.1140/epjb/e2004-00038-8)
- Park J, Newman MEJ. Origin of degree correlations in the Internet and other networks. *Physical Review E*, 2003, 68: 026112. DOI: [10.1103/PhysRevE.68.026112](https://doi.org/10.1103/PhysRevE.68.026112)
- Johnson S, Torres JJ, Marro J, Muñoz MA. Entropic origin of disassortativity in complex networks. *Physical Review Letters*, 2010, 104: 108702. DOI: [10.1103/PhysRevLett.104.108702](https://doi.org/10.1103/PhysRevLett.104.108702)
- Boguñá M, Pastor-Satorras R. Class of correlated random networks with hidden variables. *Physical Review E*, 2003, 68: 036112. DOI: [10.1103/PhysRevE.68.036112](https://doi.org/10.1103/PhysRevE.68.036112)
- Barrat A, Pastor-Satorras R. Rate equation approach for correlations in growing network models. *Physical Review E*, 2005, 71: 036127. DOI: [10.1103/PhysRevE.71.036127](https://doi.org/10.1103/PhysRevE.71.036127)
- Xulvi-Brunet R, Sokolov IM. Reshuffling scale-free networks: from random to assortative. *Physical Review E*, 2004, 70: 066102. DOI: [10.1103/PhysRevE.70.066102](https://doi.org/10.1103/PhysRevE.70.066102)
- Mahadevan P, Krioukov D, Fall K, Vahdat A. Systematic topology analysis and generation using degree correlations. *Proceedings of ACM SIGCOMM*, 2006: 135–146. DOI: [10.1145/1159913.1159930](https://doi.org/10.1145/1159913.1159930)
- Orsini C, Dankulov MM, Colomer-de-Simón P, et al. Quantifying randomness in real networks. *Nature Communications*, 2015, 6: 8627. DOI: [10.1038/ncomms9627](https://doi.org/10.1038/ncomms9627)
- Fosdick BK, Larremore DB, Nishimura J, Ugander J. Configuring random graph models with fixed degree sequences. *SIAM Review*, 2018, 60: 315–355. DOI: [10.1137/16M1087175](https://doi.org/10.1137/16M1087175)

**富人俱乐部、聚集谱与 k-核**

- Zhou S, Mondragón RJ. The rich-club phenomenon in the Internet topology. *IEEE Communications Letters*, 2004, 8: 180–182. DOI: [10.1109/LCOMM.2004.823426](https://doi.org/10.1109/LCOMM.2004.823426)
- Colizza V, Flammini A, Serrano MA, Vespignani A. Detecting rich-club ordering in complex networks. *Nature Physics*, 2006, 2: 110–115. DOI: [10.1038/nphys209](https://doi.org/10.1038/nphys209)
- Opsahl T, Colizza V, Panzarasa P, Ramasco JJ. Prominence and control: the weighted rich-club effect. *Physical Review Letters*, 2008, 101: 168702. DOI: [10.1103/PhysRevLett.101.168702](https://doi.org/10.1103/PhysRevLett.101.168702)
- Ravasz E, Somera AL, Mongru DA, Oltvai ZN, Barabási AL. Hierarchical organization of modularity in metabolic networks. *Science*, 2002, 297: 1551–1555. DOI: [10.1126/science.1073374](https://doi.org/10.1126/science.1073374)
- Ravasz E, Barabási AL. Hierarchical organization in complex networks. *Physical Review E*, 2003, 67: 026112. DOI: [10.1103/PhysRevE.67.026112](https://doi.org/10.1103/PhysRevE.67.026112)
- Soffer SN, Vázquez A. Network clustering coefficient without degree-correlation biases. *Physical Review E*, 2005, 71: 057101. DOI: [10.1103/PhysRevE.71.057101](https://doi.org/10.1103/PhysRevE.71.057101)
- Seidman SB. Network structure and minimum degree. *Social Networks*, 1983, 5: 269–287. DOI: [10.1016/0378-8733(83)90028-X](https://doi.org/10.1016/0378-8733(83)90028-X)
- Batagelj V, Zaveršnik M. Fast algorithms for determining (generalized) core groups in social networks. *Advances in Data Analysis and Classification*, 2011, 5: 129–145. DOI: [10.1007/s11634-010-0079-y](https://doi.org/10.1007/s11634-010-0079-y)
- Dorogovtsev SN, Goltsev AV, Mendes JFF. k-core organization of complex networks. *Physical Review Letters*, 2006, 96: 040601. DOI: [10.1103/PhysRevLett.96.040601](https://doi.org/10.1103/PhysRevLett.96.040601)
- Kitsak M, Gallos LK, Havlin S, et al. Identification of influential spreaders in complex networks. *Nature Physics*, 2010, 6: 888–893. DOI: [10.1038/nphys1746](https://doi.org/10.1038/nphys1746)

**对网络过程的影响**

- Boguñá M, Pastor-Satorras R. Epidemic spreading in correlated complex networks. *Physical Review E*, 2002, 66: 047104. DOI: [10.1103/PhysRevE.66.047104](https://doi.org/10.1103/PhysRevE.66.047104)
- Boguñá M, Pastor-Satorras R, Vespignani A. Absence of epidemic threshold in scale-free networks with degree correlations. *Physical Review Letters*, 2003, 90: 028701. DOI: [10.1103/PhysRevLett.90.028701](https://doi.org/10.1103/PhysRevLett.90.028701)
- Vázquez A, Moreno Y. Resilience to damage of graphs with degree correlations. *Physical Review E*, 2003, 67: 015101. DOI: [10.1103/PhysRevE.67.015101](https://doi.org/10.1103/PhysRevE.67.015101)
- di Bernardo M, Garofalo F, Sorrentino F. Effects of degree correlation on the synchronization of networks of oscillators. *International Journal of Bifurcation and Chaos*, 2007, 17: 3499–3506. DOI: [10.1142/S0218127407019263](https://doi.org/10.1142/S0218127407019263)
- Pósfai M, Liu YY, Slotine JJ, Barabási AL. Effect of correlations on network controllability. *Scientific Reports*, 2013, 3: 1067. DOI: [10.1038/srep01067](https://doi.org/10.1038/srep01067)

**生物医学应用**

- Jeong H, Mason SP, Barabási AL, Oltvai ZN. Lethality and centrality in protein networks. *Nature*, 2001, 411: 41–42. DOI: [10.1038/35075138](https://doi.org/10.1038/35075138)
- Han JDJ, Bertin N, Hao T, et al. Evidence for dynamically organized modularity in the yeast protein–protein interaction network. *Nature*, 2004, 430: 88–93. DOI: [10.1038/nature02555](https://doi.org/10.1038/nature02555)
- Wuchty S, Almaas E. Peeling the yeast protein network. *Proteomics*, 2005, 5: 444–449. DOI: [10.1002/pmic.200400962](https://doi.org/10.1002/pmic.200400962)
- Piraveenan M, Prokopenko M, Zomaya A. Assortative mixing in directed biological networks. *IEEE/ACM Transactions on Computational Biology and Bioinformatics*, 2012, 9: 66–78. DOI: [10.1109/TCBB.2010.80](https://doi.org/10.1109/TCBB.2010.80)
- Hagmann P, Cammoun L, Gigandet X, et al. Mapping the structural core of human cerebral cortex. *PLoS Biology*, 2008, 6: e159. DOI: [10.1371/journal.pbio.0060159](https://doi.org/10.1371/journal.pbio.0060159)
- van den Heuvel MP, Sporns O. Rich-club organization of the human connectome. *Journal of Neuroscience*, 2011, 31: 15775–15786. DOI: [10.1523/JNEUROSCI.3539-11.2011](https://doi.org/10.1523/JNEUROSCI.3539-11.2011)
- van den Heuvel MP, Kahn RS, Goñi J, Sporns O. High-cost, high-capacity backbone for global brain communication. *PNAS*, 2012, 109: 11372–11377. DOI: [10.1073/pnas.1203593109](https://doi.org/10.1073/pnas.1203593109)
- Harriger L, van den Heuvel MP, Sporns O. Rich club organization of macaque cerebral cortex and its role in network communication. *PLoS ONE*, 2012, 7: e46497. DOI: [10.1371/journal.pone.0046497](https://doi.org/10.1371/journal.pone.0046497)
- Towlson EK, Vértes PE, Ahnert SE, Schafer WR, Bullmore ET. The rich club of the *C. elegans* neuronal connectome. *Journal of Neuroscience*, 2013, 33: 6380–6387. DOI: [10.1523/JNEUROSCI.3784-12.2013](https://doi.org/10.1523/JNEUROSCI.3784-12.2013)
- van den Heuvel MP, Sporns O, Collin G, et al. Abnormal rich club organization and functional brain dynamics in schizophrenia. *JAMA Psychiatry*, 2013, 70: 783. DOI: [10.1001/jamapsychiatry.2013.1328](https://doi.org/10.1001/jamapsychiatry.2013.1328)

## 延伸资源 {#resources}

| 类型 | 资源 | 说明 |
|---|---|---|
| 教材 | Barabási, *Network Science*, Ch. 7 Degree Correlations，[networksciencebook.com/chapter/7](http://networksciencebook.com/chapter/7)（CC BY-NC-SA 2.0） | $e_{ij}$、$k_{nn}(k)$、相关指数、结构截断、R-S/R-M 随机化、Xulvi-Brunet–Sokolov 算法；进阶专题 7.A（$r$ 与 $\mu$ 的关系）与 7.B（结构截断推导） |
| 教材 | Newman, *Networks*（第 2 版, Oxford University Press, 2018），同配混合与度相关相关章节 | 类别与标量同配系数、相关网络上的渗流与传播的生成函数处理 |
| 综述 | Newman 2003, *SIAM Review*（精读见 [Newman 2003](paper-newman2003_review.html)） | 同配混合在复杂网络结构统计中的位置 |
| 工具 | NetworkX：`degree_assortativity_coefficient`、`average_degree_connectivity`、`rich_club_coefficient`、`core_number`、`double_edge_swap`、`attribute_assortativity_coefficient` | 本专题代码示例全部基于这些函数，并给出与定义的手算对照 |
| 工具 | [Brain Connectivity Toolbox](https://sites.google.com/site/bctnet/) / [bctpy](https://github.com/aestrivex/bctpy) | 加权与有向的同配系数、富人俱乐部系数（`rich_club_bu`、`rich_club_wu` 等）、核分解与多种零模型；指标说明见 Rubinov & Sporns（2010, *NeuroImage*，DOI: [10.1016/j.neuroimage.2009.10.003](https://doi.org/10.1016/j.neuroimage.2009.10.003)） |
| 工具 | [igraph](https://igraph.org/)（R / Python） | `assortativity_degree`、`knn`、`coreness`，适合大规模网络 |
| 数据 | [BioGRID](https://thebiogrid.org/) | 可按实验类型（双杂交、亲和纯化）筛选相互作用，比较不同证据类型对度相关的影响 |

## 开放问题 {#questions}

1. 对你熟悉的一个生物网络，度相关有多少可以由度序列和简单图约束解释（R-S 随机化），多少需要额外的机制？如果再控制模块结构或空间距离，剩余的相关还存在吗？
2. 相互作用组的研究偏倚使被研究得多的蛋白既度高又更可能互相有记录。你预期这种偏倚使观测的度相关偏向同配还是异配？可以用系统性筛选数据（如人类二元相互作用参考图谱）做什么样的对照？
3. 富人俱乐部的归一化依赖零模型：保度、保持空间距离、保持权重分布的零模型可能给出不同结论。对一个具体的脑网络问题，你会预先规定哪一种，为什么？
4. 两点相关（$k_{nn}$）、三点相关（$C(k)$）和更高阶统计（$k$-核、dK 序列）之间是什么关系？在什么条件下，掌握到 2K 或 2.5K 就足以预测传播阈值或可控性，什么时候还需要更高阶的结构？
5. 在患者与对照的网络比较中，如果患者组 $r$ 或 $\rho_{\text{ran}}(k)$ 不同，怎样区分“度相关结构改变”与“度分布、网络密度或模块大小改变”的间接效应？
