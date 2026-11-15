---
id: robustness
title: 网络鲁棒性、渗流与级联失效
en: Robustness, percolation and cascading failures
domain: dynamics
legacy: ""
summary: 研究网络在节点或连边失效、蓄意攻击与级联传播下能否保持整体连通与功能，以及如何量化、预测和提高鲁棒性。
keywords: [鲁棒性, 渗流, 巨连通分支, 临界阈值, 随机失效, 蓄意攻击, 级联失效, 相互依存网络, R 指标, 合成致死, 脑损伤]
synonyms: [robustness, network robustness, 网络鲁棒性, 稳健性, resilience, 韧性, percolation, 渗流, site percolation, 点渗流, 节点渗流, bond percolation, 边渗流, 键渗流, giant component, 巨连通分支, 巨分支, GCC, LCC, largest connected component, 最大连通分支, order parameter, 序参量, critical threshold, 临界阈值, percolation threshold, 渗流阈值, f_c, Molloy-Reed criterion, Molloy–Reed 判据, generating function, 生成函数, random failure, 随机失效, error tolerance, 容错性, targeted attack, 蓄意攻击, 目标攻击, intentional attack, attack tolerance, 攻击容忍, adaptive attack, 自适应攻击, betweenness attack, 介数攻击, network dismantling, 网络瓦解, collective influence, 集体影响力, optimal percolation, 最优渗流, Newman-Ziff algorithm, Newman–Ziff 算法, cascading failure, 级联失效, 连锁失效, load redistribution, 负载重分配, Motter-Lai model, Motter–Lai 模型, threshold model, 阈值模型, Watts model, cascade window, 级联窗口, branching process, 分支过程, avalanche, 雪崩, sandpile, 沙堆模型, interdependent networks, 相互依存网络, 相互依赖网络, network of networks, 网络的网络, multilayer percolation, 多层网络渗流, multiplex, 多路网络, first-order transition, 一级相变, robustness measure R, R 指标, Schneider R, onion-like structure, 洋葱结构, bimodal degree distribution, 双峰度分布, essential gene, 必需基因, lethality, 致死性, gene knockout, 基因敲除, flux balance analysis, FBA, 通量平衡分析, synthetic lethality, 合成致死, synthetic rescue, 合成拯救, Lazarus effect, PARP inhibitor, PARP 抑制剂, BRCA, redundancy, 冗余, degeneracy, 简并性, virtual lesion, 虚拟损伤, brain lesion, 脑损伤, diaschisis, 远隔效应, connector hub, 连接者枢纽, participation coefficient, 参与系数]
demos: [attack]
reviewed: 2026-11-15
---

## 概述 {#overview}

鲁棒性（robustness）指系统在部分组件失效后仍能维持基本功能的能力。细胞中蛋白错误折叠、反应缺失时时发生，大多数单基因敲除并不致死；脑卒中可以毁掉一片皮层，病人却可能只出现局限的缺损；而另一些时候，一个小小的初始故障会沿着网络放大，演变为大面积停电、多器官衰竭或细胞死亡。系统能承受什么样的损伤、在哪里会突然崩溃，在很大程度上由连接结构决定。

本专题从统计物理的**渗流理论**出发，回答四组问题：（1）随机删除节点或连边时，网络何时碎裂，临界阈值怎样由度分布决定，为什么无标度网络“耐随机失效、怕蓄意攻击”；（2）攻击者掌握的信息越多（度、介数、每一步重新计算），网络瓦解得有多快；（3）当失效会传递——负载重分配、阈值触发、相互依存——级联何时出现，规模服从什么分布；（4）怎样量化和提高鲁棒性，以及这些思想在蛋白必需性、代谢网络基因敲除、脑损伤和癌症合成致死中的用法与限度。

基础概念见[连通分支与巨连通分支](network-metrics.components.html)和[ER 随机网络](network-metrics.er-random-graph.html)；[网络可控性与稳定性](controllability.html)中的[结构鲁棒性](controllability.structural-robustness.html)给出了随机失效阈值 $f_c$ 的最短推导，本专题在此基础上系统展开。渗流也是[网络上的传播与免疫](spreading.html)的数学核心：SIR 最终规模等价于边渗流，目标免疫就是对传播网络的“攻击”。结构鲁棒性与动力学稳定性、韧性的区别见[动力学稳定性](controllability.dynamical-stability.html)。

## 渗流理论与网络碎裂 {#percolation}

### 从格点渗流到网络

渗流（percolation）研究随机占据的元素何时连成贯穿整个系统的团簇。经典问题是：在二维正方格点上以概率 $p$ 放置“石子”，相邻石子相连，最大团簇有多大？渗流理论的核心结论是：团簇规模并不随 $p$ 平滑变化，而是在临界值 $p_c$ 处发生**相变**——低于 $p_c$ 只有许多小团簇，高于 $p_c$ 出现一个占有限比例的“渗流团簇”。二维正方格点的点渗流 $p_c\approx0.593$，三角格点为 $1/2$，简单立方格点约为 $0.3116$。

::: {.callout-def}
**点渗流与边渗流**。给定网络，**点渗流**（site percolation）中每个节点以概率 $\phi$ 被保留（以概率 $1-\phi$ 连同其边一起删除）；**边渗流**（bond percolation，又称键渗流）中每条边以概率 $\phi$ 被保留，节点全部保留。**序参量** $P_\infty$（也记作 $S$）是一个随机节点属于巨连通分支的概率；临界占据概率 $\phi_c$ 是 $P_\infty$ 由零变为正值的点。研究失效时常用删除比例 $f=1-\phi$，临界删除比例 $f_c=1-\phi_c$。
:::

网络在随机失效下的碎裂正是“反向”的渗流：从完整网络开始，逐步随机删除比例 $f$ 的节点。$f<f_c$ 时巨分支仍在，$f>f_c$ 时网络碎成许多小块。

### 临界行为与普适性

在临界点附近，三个量服从幂律：

$$
\langle s\rangle\sim|\phi-\phi_c|^{-\gamma_p},\qquad P_\infty\sim(\phi-\phi_c)^{\beta_p},\qquad \xi\sim|\phi-\phi_c|^{-\nu},
$$

其中 $\langle s\rangle$ 是有限团簇（不含巨分支）的平均大小，$\xi$ 是关联长度。$\phi_c$ 依赖于格点类型，**临界指数却只依赖于维数**，这称为普适性：二维时 $\gamma_p=43/18$、$\beta_p=5/36$、$\nu=4/3$；维数 $d>6$ 时取平均场值 $\gamma_p=1$、$\beta_p=1$、$\nu=1/2$。没有空间嵌入、局部呈树状的随机网络相当于“无穷维”，因此 ER 网络的随机失效属于平均场普适类。度分布很宽的网络会偏离平均场：对 $P(k)\sim k^{-\gamma}$，Cohen 等（2002，*Physical Review E*）得到

$$
\beta_p=\begin{cases}1/(3-\gamma),&2<\gamma<3\\ 1/(\gamma-3),&3<\gamma<4\\ 1,&\gamma>4\end{cases}
$$

即只有 $\gamma>4$ 时才回到 ER 网络的行为。

### 有限网络中如何判定 $f_c$

真实网络是有限的，“$P_\infty$ 恰好为零”的点并不存在。常用的经验做法有三种：（1）**1% 规则**：最大分支首次降到原规模 1% 以下的 $f$（Barabási《Network Science》第 8 章对真实网络就采用此法）；（2）**第二大分支峰值**：第二大连通分支的规模（或有限团簇平均大小 $\langle s\rangle$）在临界点附近达到峰值，这是最符合渗流理论的定义；（3）对多个规模 $N$ 做有限尺度标度分析。不同规则给出的 $f_c$ 可以相差不少，报告时要写明。

::: {.callout-warn}
“最大连通分支比例”是结构指标，不是功能指标。网络仍然连通并不说明信号还能有效传递（路径可能大大变长），而巨分支消失也不等于每个节点都“失效”。在生物网络中，应同时报告平均路径长度、全局效率或与功能直接相关的指标（如代谢网络能否合成生物量前体）。
:::

## 生成函数方法与 Molloy–Reed 判据 {#generating-functions}

对“度分布给定、其余完全随机”的配置模型网络，渗流问题可以用生成函数精确求解（Callaway、Newman、Strogatz 与 Watts 2000，*PRL*；Newman、Strogatz 与 Watts 2001，*PRE*）。

### 两个生成函数

::: {.callout-def}
**度分布生成函数**：$G_0(x)=\sum_k P(k)x^k$；**剩余度生成函数**：$G_1(x)=\dfrac{G_0'(x)}{G_0'(1)}=\dfrac{1}{\langle k\rangle}\sum_k kP(k)x^{k-1}$。沿一条随机边到达的节点，其度为 $k$ 的概率正比于 $kP(k)$（高度节点更容易被边“碰到”），去掉来时的那条边后剩下的 $k-1$ 条边称为**剩余度**，其分布由 $G_1$ 生成。$G_1'(1)=\dfrac{\langle k^2\rangle-\langle k\rangle}{\langle k\rangle}$ 是平均剩余度。
:::

### 自洽方程

设 $u$ 为“沿一条随机边出发，**不能**通向巨分支”的概率。在点渗流中，这条边的另一端要么被删除（概率 $1-\phi$），要么保留且它的所有剩余边都不通向巨分支（概率 $\phi\,G_1(u)$）：

$$
u=1-\phi+\phi\,G_1(u),\qquad P_\infty=\phi\,[1-G_0(u)].
$$

边渗流只需把“节点被保留”换成“边被保留”：$u=1-\phi+\phi\,G_1(u)$，$P_\infty=1-G_0(u)$。两种渗流的 $u$ 方程相同，所以**临界点相同**，只是巨分支大小不同：点渗流多乘一个 $\phi$，因为删一个节点等于同时删掉它的全部边。$u=1$ 总是方程的解；非平凡解 $u<1$ 出现的条件是曲线 $1-\phi+\phi G_1(u)$ 在 $u=1$ 处的斜率大于 1，即

$$
\phi\,G_1'(1)>1\iff\phi_c=\frac{1}{G_1'(1)}=\frac{\langle k\rangle}{\langle k^2\rangle-\langle k\rangle}.
$$

完整网络（$\phi=1$）存在巨分支的条件 $G_1'(1)>1$ 等价于 $\langle k^2\rangle-2\langle k\rangle>0$，这就是 **Molloy–Reed 判据**（Molloy 与 Reed 1995）：$\kappa=\langle k^2\rangle/\langle k\rangle>2$。由 $\phi_c$ 立即得到随机失效阈值

$$
f_c=1-\frac{1}{\kappa_0-1},\qquad\kappa_0=\frac{\langle k^2\rangle}{\langle k\rangle}.
$$

这与[结构鲁棒性](controllability.structural-robustness.html)中用“删点后度分布二项稀释”得到的结果一致，生成函数的好处是还能给出整条 $P_\infty(\phi)$ 曲线与团簇大小分布。临界点以下，含随机节点的团簇平均大小为

$$
\langle s\rangle=\phi\left[1+\frac{\phi\,G_0'(1)}{1-\phi\,G_1'(1)}\right],
$$

在 $\phi\to\phi_c$ 时发散。边渗流情形的推导与 SIR 最终规模的对应见[网络上的传播与免疫的数学推导](spreading.derivations.html)。

### 算例

**算例 1（泊松网络）**：ER 网络 $G_0(x)=G_1(x)=e^{\langle k\rangle(x-1)}$。由 $P_\infty=\phi[1-G_0(u)]$ 得 $G_0(u)=1-P_\infty/\phi$，代回 $u$ 的方程得 $u=1-P_\infty$，于是点渗流满足 $P_\infty=\phi\,(1-e^{-\langle k\rangle P_\infty})$，边渗流满足 $P_\infty=1-e^{-\phi\langle k\rangle P_\infty}$。取 $\langle k\rangle=4$：$\phi_c=1/4$，即要随机删掉 75% 的节点网络才碎裂；$\phi=0.5$ 时迭代得点渗流 $P_\infty\approx0.398$、边渗流 $P_\infty\approx0.797$。

**算例 2（可手算的双值度分布）**：一半节点度为 1、一半度为 3。$\langle k\rangle=2$，$\langle k^2\rangle=5$，$\kappa_0=2.5>2$，存在巨分支；$f_c=1-1/1.5=1/3$。完整网络中 $G_1(u)=(1\cdot\tfrac12+3\cdot\tfrac12u^2)/2=\tfrac14+\tfrac34u^2$，解 $u=\tfrac14+\tfrac34u^2$ 得 $u=1/3$，于是 $P_\infty=1-G_0(1/3)=1-(\tfrac12\cdot\tfrac13+\tfrac12\cdot\tfrac1{27})=44/54\approx0.81$。

::: {.callout-warn}
生成函数方法的假设是：网络无度相关、局部树状（短环很少）、$N\to\infty$。真实生物网络常有高聚集、模块和度相关，此时理论值只是参照。实践中应该把观测网络与**保度随机化网络**的模拟曲线放在一起比较，而不是直接拿理论 $f_c$ 下结论。度相关的影响：Newman（2002，*PRL*）指出同配网络更容易形成巨分支，对删除高度节点也更鲁棒（见[度相关性](degree-correlations.html)）。
:::

## 随机失效与无标度网络 {#random-failure}

### 二阶矩决定一切

$f_c=1-1/(\kappa_0-1)$ 表明随机失效阈值只依赖 $\langle k\rangle$ 和 $\langle k^2\rangle$。对 ER 网络，$\langle k^2\rangle=\langle k\rangle(\langle k\rangle+1)$，故 $f_c^{ER}=1-1/\langle k\rangle$：总是有限，越稠密越耐删。对幂律分布 $P(k)\sim k^{-\gamma}$（$k_{\min}\le k\le k_{\max}$），用连续度近似

$$
\kappa=\frac{\langle k^2\rangle}{\langle k\rangle}\approx\left|\frac{2-\gamma}{3-\gamma}\right|\times
\begin{cases}k_{\min}, &\gamma>3\\ k_{\max}^{3-\gamma}k_{\min}^{\gamma-2}, &2<\gamma<3\\ k_{\max}, &1<\gamma<2\end{cases}
$$

- $\gamma>3$：$\kappa$ 有限，$f_c$ 只由 $\gamma$ 和 $k_{\min}$ 决定，网络的行为与随机网络类似；
- $2<\gamma<3$：$k_{\max}\sim k_{\min}N^{1/(\gamma-1)}$ 随规模增大，$\kappa\to\infty$，$f_c\to1$，即无限大的无标度网络必须删掉几乎全部节点才会碎裂（Cohen、Erez、ben-Avraham 与 Havlin 2000，*PRL*）。

有限网络中 $f_c\approx1-C\,N^{-(3-\gamma)/(\gamma-1)}$，网络越大越接近 1。直观原因：随机删除对度“视而不见”，而无标度网络中绝大多数节点是低度节点，删到枢纽的概率很小；只要枢纽还在，它们就把剩余节点连在一起。

::: {.callout-def}
**增强鲁棒性**：若一个网络的随机失效阈值高于同样 $N$、$L$ 的随机网络，$f_c>f_c^{ER}$，称其具有增强鲁棒性。它不要求严格的幂律，只要求 $\langle k^2\rangle$ 明显大于 $\langle k\rangle(\langle k\rangle+1)$。
:::

Barabási《Network Science》第 8 章表 8.1 对十个参考网络比较了真实网络与随机化网络的 $f_c$：多数网络满足增强鲁棒性，例如蛋白相互作用网络随机失效 $f_c\approx0.88$，对应随机化网络约 0.66，而按度攻击时只有约 0.06；度分布近似指数的电网（0.61 vs 0.63）则没有增强鲁棒性。

### 点失效与边失效

随机删边与随机删点的阈值相同（上一节已证明），但同样比例下删点造成的损伤更大：删去比例 $f$ 的节点平均相当于删去约 $1-(1-f)^2$ 比例的边（一条边只要任一端点被删就消失）。比较生物网络中的“蛋白缺失”（删点，如基因敲除）与“相互作用缺失”（删边，如破坏某个结合界面的点突变）时要注意这一差别。Zhong 等（2009，*Molecular Systems Biology*）分析约 5 万个已知的孟德尔病致病突变，把它们区分为“节点去除”与“边特异”（edgetic）扰动，并发现二者的功能后果不同。

::: {.callout-warn}
“无标度网络 $f_c\to1$”是 $N\to\infty$ 且无度相关的极限结论。生物网络节点数有限（数千到两万），度分布是否为幂律本身存疑（见[小世界与无标度的统计判别](network-models.identification.html)），而且观测网络有大量缺失边。应当直接对观测网络做模拟，把“比随机化网络更鲁棒”作为可检验的命题，而不是从“无标度”推断“极鲁棒”。
:::

## 蓄意攻击：按度、介数与自适应攻击 {#targeted-attack}

### 攻击阈值

**蓄意攻击**按某种重要性从高到低删除节点。按度攻击同时改变两件事（Cohen、Erez、ben-Avraham 与 Havlin 2001，*PRL*）：最大度从 $k_{\max}$ 降到 $k'_{\max}$；剩余节点因失去连向枢纽的边而度数下降。对无度相关网络，删去比例 $f$ 的枢纽后，被删掉的边占全部边的比例 $\tilde f=f^{(2-\gamma)/(1-\gamma)}$，剩余网络相当于“截断到 $k'_{\max}=k_{\min}f^{1/(1-\gamma)}$ 的幂律网络再随机删去比例 $\tilde f$ 的边”。代入 Molloy–Reed 判据，得到攻击阈值满足

$$
f_c^{\frac{2-\gamma}{1-\gamma}}=2+\frac{2-\gamma}{3-\gamma}\,k_{\min}\left(f_c^{\frac{3-\gamma}{1-\gamma}}-1\right).
$$

数值解表明：攻击阈值只有百分之几到二十几；攻击阈值总小于随机失效阈值；它随 $\gamma$ 非单调变化。按本页代码中的连续度近似，$k_{\min}=1$ 时攻击阈值约在 $\gamma\approx2.3$ 取极大值 0.06 左右。$\gamma\to2$ 时 $\tilde f\to1$：删掉极少数枢纽就带走几乎全部边。$\gamma\to\infty$ 时所有节点度相同，攻击与随机失效不再有区别，$f_c\to1-1/(k_{\min}-1)$。

Albert、Jeong 与 Barabási（2000，*Nature*）首先用模拟展示了这一“阿喀琉斯之踵”：无标度网络在随机失效下直径几乎不变，在攻击下迅速增大并碎裂（[论文精读](paper-albert2000_attack.html)）。同一个 $\langle k^2\rangle$ 既带来对随机失效的鲁棒，也带来对攻击的脆弱。

### 攻击者知道得越多，网络瓦解得越快

Holme、Kim、Yoon 与 Han（2002，*Physical Review E*）比较了四种删点策略：按**初始**度（ID）、按**初始**介数（IB）、每删一个节点后**重新计算**度（RD）、重新计算介数（RB）。结论是：自适应策略（RD、RB）通常比按初始排序更具破坏性，因为删掉枢纽后网络结构变了，原来的“第二重要”节点不一定仍然重要。直观上，介数攻击针对的是承担大量最短路径的“桥”，在社团之间只靠少数节点连接的网络中，它可能比按度攻击更快地切断网络。

更进一步，**网络瓦解**（dismantling）问题要求找到最小的节点集合，使删除后最大分支不超过给定规模。这是 NP 难问题，近年的近似方法包括：Morone 与 Makse（2015，*Nature*）的**集体影响力**（collective influence），把它表述为“最优渗流”，节点 $i$ 的得分为 $\mathrm{CI}_\ell(i)=(k_i-1)\sum_{j\in\partial B(i,\ell)}(k_j-1)$，即自身剩余度乘以距离恰为 $\ell$ 的节点的剩余度之和；Braunstein 等（2016，*PNAS*）的“先拆环（decycling）再拆树”的消息传递算法。它们都比按度攻击更高效，其核心洞见是：瓦解网络的关键不只是枢纽，而是那些破坏环结构、切断社团之间联系的节点。

::: {.callout-bio}
攻击与免疫是同一个数学问题：[免疫策略](spreading.immunization.html)中，给度高的人接种相当于对接触网络做按度攻击，熟人免疫（[Cohen 2003](paper-cohen2003_immunization.html)）是在只知道局部信息时近似实现攻击。在药物研发中，“攻击”对应用药物抑制病原体或肿瘤细胞网络的关键蛋白；Barabási 第 8 章指出，细菌对枢纽蛋白删除的脆弱性可以为抗菌药物设计提供思路。但细胞功能不等于网络连通，见[致死性与中心性](molecular-networks.centrality-lethality.html)的争论。
:::

## 鲁棒性度量：R 指标与功能性指标 {#robustness-measures}

单个阈值 $f_c$ 只描述“网络何时完全碎裂”，忽略了崩溃之前的损伤程度。两个网络可能有相同的 $f_c$，但其中一个在删去 5% 的节点后就失去一半节点的连通。

::: {.callout-def}
**R 指标**（Schneider 等 2011，*PNAS*）：按自适应度攻击逐个删除节点，记 $s(Q)$ 为删去 $Q$ 个节点后最大连通分支的节点比例，
$$
R=\frac{1}{N}\sum_{Q=1}^{N}s(Q).
$$
$R$ 即攻击曲线下的面积，取值约在 $1/N$（星形网络）到 $1/2$（完全图）之间，可以比较不同规模的网络。对随机失效或其他攻击策略同样可以定义类似的曲线下面积。
:::

**手算例**：$N=5$ 的星形网络，第一步删掉中心，此后每个剩余节点都孤立：$s(1)=\dots=s(4)=1/5$，$s(5)=0$，$R=4/25=0.16$。$N=5$ 的路径 0–1–2–3–4，按介数先删中点 2，剩下两段长度为 2 的路径：$s(1)=2/5$；再删 1 得 $s(2)=2/5$；随后 $s(3)=s(4)=1/5$，$s(5)=0$，$R=6/25=0.24$。路径比星形“更鲁棒”，因为它没有单点故障。

其他常用指标：

| 指标 | 定义 | 适用场景 |
|---|---|---|
| $P_\infty(f)$ 曲线与 $f_c$ | 最大分支比例随删除比例的变化 | 渗流意义上的整体连通 |
| 全局效率 $E=\frac{1}{N(N-1)}\sum_{i\ne j}1/d_{ij}$ | 删除后效率下降比例 | 不连通网络也有定义；脑网络常用 |
| 平均路径长度、直径 | Albert 等（2000）使用 | 只在连通分支内定义 |
| 第二大分支、团簇大小分布 | 临界点附近达到峰值 | 判定 $f_c$ |
| 功能指标 | 代谢网络的生物量合成、信号网络的输入–输出可达性 | 生物医学问题首选 |

## 级联失效：负载重分配 {#load-cascades}

前面假定节点独立失效。真实系统中，一个组件失效会把它承担的“流”转移给其他组件，使后者超载失效，形成**级联失效**（cascading failure）。2003 年 8 月 14 日北美大停电就是例子：一条超载输电线触树、报警系统软件故障使操作员未能及时重新分配负荷，局部故障最终使安大略省和美国八个州约 5500 万人断电。级联有三个共同要素：网络上存在某种流；每个组件有局部失效规则；失效后有流的重分配机制。

::: {.callout-def}
**Motter–Lai 负载模型**（Motter 与 Lai 2002，*Physical Review E*）：假设每对节点之间沿最短路径交换一个单位的流，节点 $i$ 的负载 $L_i$ 即经过它的最短路径数（介数）。容量与初始负载成正比：$C_i=(1+\alpha)L_i$，$\alpha\ge0$ 为容忍参数。移除一个节点后重新计算所有负载，$L_i>C_i$ 的节点失效；重复直到不再有新的失效。用 $G=N'/N$（级联结束后最大分支的相对规模）度量损害。
:::

主要结论：负载分布高度异质的网络（如无标度网络），**移除单个高负载节点**就可能触发覆盖大部分网络的级联，而随机移除一个节点几乎不造成影响；负载均匀的网络则不易出现这种不对称。$\alpha$ 越小（冗余容量越少），越容易崩溃。

**算例**：考虑一个由两个三角形 {A,B,C} 和 {D,E,F} 加一条桥 C–D 组成的网络。桥端点 C、D 的负载最高（所有跨三角形的流都经过它们）。若删除 B，A 与 C 之间只剩直连边，其他节点的最短路径不受影响，负载不增，级联不发生；若删除 C，A、B 与另一侧完全断开，虽然没有超载，但网络已经分裂。若在 A–E 之间再加一条“备用”长程边，删除 C 后跨侧流全部改走 A–E，A、E 的负载骤增，$\alpha$ 小时它们会相继超载——**冗余路径同时也是级联通道**，这正是电网中“N−1 安全准则”需要考虑负载转移的原因。

模型的发展：Crucitti、Latora 与 Marchiori（2004，*Physical Review E*）把节点“效率”而不是二元失效作为动态变量，使过载节点降低效率、引导流绕行；Motter（2004，*PRL*）提出**级联防御**：在初始故障后、级联扩散前，有选择地主动移除低负载节点和超负荷边，可以显著缩小最终损失——这与森林火灾中“以火攻火”开辟隔离带的思路相同。

::: {.callout-bio}
生物学类比：在代谢网络中，一个酶失活后底物积累、通量被迫改道，可能使其他通路过载或使有毒中间产物堆积；Smart、Amaral 与 Ottino（2008，*PNAS*）用基于拓扑通量平衡的级联模型分析大肠杆菌、甲烷八叠球菌、金黄色葡萄球菌和酿酒酵母的代谢网络，发现它们比合适的零模型更鲁棒，级联过程可以描述为渗流过程。Motter 的“主动移除以止损”在代谢网络中也有对应——见[代谢网络的基因敲除](robustness.metabolic-knockouts.html)中的合成拯救。
:::

## 阈值级联与分支过程 {#threshold-branching}

### Watts 阈值模型

在负载模型之外，另一类级联由**局部阈值规则**驱动（Watts 2002，*PNAS*）：每个节点有阈值 $\varphi$，当失效（或被“激活”）邻居的比例 $\ge\varphi$ 时它也失效。这与[信息与行为的传播](spreading.social-contagion.html)中的复杂传染是同一模型，在这里把“采纳”理解为“失效”。

度 $k\le1/\varphi$ 的节点只需一个失效邻居就会失效，称为**易损节点**。全局级联可以发生，当且仅当易损节点在网络中形成渗流团簇。用生成函数可得到条件

$$
\sum_k k(k-1)\,\rho_k\,P(k)>\langle k\rangle,
$$

其中 $\rho_k$ 是度为 $k$ 的节点是易损节点的概率（阈值相同时 $\rho_k=1$ 当 $k\le\lfloor1/\varphi\rfloor$）。这给出了在 $(\langle k\rangle,\varphi)$ 平面上的**级联窗口**：$\langle k\rangle$ 太小时网络本身不连通，级联无法扩散；$\langle k\rangle$ 太大时每个节点的邻居太多，一个失效邻居不足以越过阈值，易损节点稀少。在窗口的上边界附近，级联很少发生，一旦发生却往往是全局性的——“稳定的”系统反而可能突然整体崩溃。

### 分支过程

更抽象的描述把级联看作**分支过程**：初始失效节点是树根，它引起的每一次失效是一个“后代”，每个后代再独立地产生后代，后代数服从分布 $\{p_k\}$，生成函数 $g(x)=\sum_kp_kx^k$，平均后代数 $m=g'(1)$。

- $m<1$（亚临界）：级联必然熄灭，规模分布呈指数衰减；
- $m>1$（超临界）：级联以正概率无限增长，熄灭概率 $q$ 是 $q=g(q)$ 在 $[0,1)$ 内的解；
- $m=1$（临界）：规模分布为幂律 $P(s)\sim s^{-\alpha}$。

**算例**：$p_0=1/4,p_1=1/4,p_2=1/2$，$m=1.25$。解 $q=\tfrac14+\tfrac14q+\tfrac12q^2$，即 $2q^2-3q+1=0$，得 $q=1/2$（另一根 $q=1$ 舍去）：一半的初始故障会自行熄灭，另一半会发展为全局级联。

临界分支过程可以映射为一维随机游走的首次返回问题：当前“活跃”节点数 $x$ 每步加一或减一，雪崩规模就是从 $x=1$ 首次到达 $x=0$ 的时间，其分布指数为 $3/2$。若后代分布本身是幂律 $p_k\sim k^{-\gamma}$，则

$$
\alpha=\begin{cases}\gamma/(\gamma-1),&2<\gamma<3\\ 3/2,&\gamma\ge3\end{cases}
$$

（Goh 等 2003，*PRL* 关于无标度网络上沙堆模型的结果与此一致）。Barabási 第 8 章汇总的经验雪崩指数（各国电网停电规模、转发级联、地震）多在 1.6–2.0 之间，落在这一预测范围内。

::: {.callout-warn}
经验数据呈“厚尾”并不等于系统处在临界态，也不等于存在网络级联。幂律拟合需要严格的统计检验（见[小世界与无标度的统计判别](network-models.identification.html)），雪崩的定义（时间窗、阈值）也会改变指数。神经元“雪崩”与大脑临界性的研究中，这一问题尤为突出。
:::

## 相互依存网络与多层网络的渗流 {#interdependent-networks}

现代系统往往由多个相互依赖的网络组成：电站依赖通信网络控制，通信节点依赖电站供电。Buldyrev、Parshani、Paul、Stanley 与 Havlin（2010，*Nature*）提出了**相互依存网络**模型（[论文精读](paper-buldyrev2010_cascade.html)）。

::: {.callout-def}
**相互依存网络与相互连通巨分支**：网络 A、B 各有 $N$ 个节点，内部各自随机连接；A 的节点 $i$ 与 B 的节点 $i$ 通过**依赖边**一一对应，任一方失效，另一方随之失效。一个节点“存活”要求它在本网络中属于巨分支，且它的依赖伙伴也存活。迭代执行“A 中只保留巨分支 → 删除 B 中失去依赖的节点 → B 中只保留巨分支 → 删除 A 中失去依赖的节点……”直至稳定，剩下的就是**相互连通巨分支**（mutually connected giant component）。
:::

设初始随机保留比例 $p$ 的 A 节点，$g_A(\cdot)$、$g_B(\cdot)$ 为单网络中“随机保留某比例时巨分支占保留节点的比例”。级联稳态满足 $x=p\,g_A(y)$，$y=p\,g_B(x)$。对两个平均度均为 $\langle k\rangle$ 的 ER 网络，相互连通巨分支比例 $\mu$ 满足

$$
\mu=p\,\big(1-e^{-\langle k\rangle\mu}\big)^2 .
$$

令 $z=\langle k\rangle\mu$，则 $\langle k\rangle p=z/(1-e^{-z})^2$；非零解存在的最小 $p$ 由右边的极小值给出：$p_c=2.4554/\langle k\rangle$，此时 $\mu$ 不是从零连续增长，而是从 $1.2564/\langle k\rangle$ 直接跳到零。

由此得到三条与单一网络相反的结论：

1. **一级（不连续）相变**：崩溃是突发的，接近阈值时几乎没有“渐进损伤”的预警；
2. **阈值大幅提高**：$\langle k\rangle=4$ 时单个 ER 网络的 $p_c=0.25$，相互依存后变为约 0.61；
3. **宽度分布反而更脆弱**：平均度相同时，度分布越宽，相互依存系统越容易崩溃——单一网络中耐随机失效的无标度结构，在相互依存时不再有优势。

后续工作给出了更一般的图景：Parshani、Buldyrev 与 Havlin（2010，*PRL*）表明只有一部分节点相互依赖时，降低耦合强度可使相变从一级变为二级；Gao 等（2012，*Nature Physics*）把理论推广到“网络的网络”；Bashan 等（2013，*Nature Physics*）发现空间嵌入的相互依存网络极端脆弱，任意小比例的依赖都可能导致突变式崩溃。多路网络（同一组节点上多种关系）的渗流还区分“任一层连通”与“各层同时连通”两种定义，结论差别很大（多层网络的一般框架见 Kivelä 等 2014，以及[动态功能连接与多层脑网络](dynamic-brain-networks.html)）。

::: {.callout-bio}
生物系统中的“依赖”比基础设施更难界定。细胞内信号网络、转录调控网络和代谢网络相互耦合（酶的表达依赖转录因子，转录因子的活性又依赖代谢物），脑的结构连接与神经血管耦合、胶质–神经元网络也相互依存。把这些系统建模为相互依存网络时，必须说明依赖边的生物学含义（“A 失效必然导致 B 失效”的证据是什么），否则一级相变等结论只是模型的产物。
:::

## 鲁棒性优化与网络设计 {#robustness-optimization}

### 理论最优：双峰度分布

若只要求对随机失效最鲁棒且固定成本 $\langle k\rangle$，应让 $\langle k^2\rangle$ 尽可能大；若要求随机失效阈值与攻击阈值之和 $f_c^{tot}=f_c^{rand}+f_c^{targ}$ 最大，解析与数值结果表明最优度分布是**双峰**的（Paul 等 2004，*European Physical Journal B*；Valente、Sarkar 与 Stone 2004，*PRL*；Tanizawa 等 2005，*Physical Review E*）：

$$
P(k)=(1-r)\,\delta(k-k_{\min})+r\,\delta(k-k_{\max}),
$$

且最优情形是 $r=1/N$——只有一个枢纽，其度 $k_{\max}\sim A N^{2/3}$，其余节点度均为 $k_{\min}$。这样的网络耐随机失效（删中枢纽的概率只有 $1/N$），删掉唯一的枢纽造成一次性损失，剩下的 $k_{\min}\ge2$ 的规则部分仍自成巨分支。Barabási 据此指出：鲁棒性优化得到的是“中心辐射 + 规则网”，而不是幂律，所以鲁棒性不太可能是真实网络呈无标度的原因。

### 实际改造：保度换边与“洋葱”结构

改造已建成的网络时，节点度往往难以改变。Schneider 等（2011，*PNAS*）提出在**保持每个节点度不变**的前提下随机交换两条边的端点，只有当 $R$ 增大时才接受。对欧洲电网和互联网服务提供商网络，只改动约 5.5% 的边就使 $R$ 提高约 45% 和 55%，而按渗流阈值 $q_c$ 衡量几乎没有变化（这正说明 $R$ 比单一阈值更敏感），传输性能也基本不变。优化后的网络呈现**洋葱结构**：高度节点构成相互连接的核心，外面一层层包裹着度递减的节点，同度节点之间存在不经过更高度节点的路径。洋葱结构往往伴随较高的度同配，但高同配网络不一定是洋葱结构，也不一定更鲁棒。

### 其他提高鲁棒性的途径

- **加边**：最直接，但代价高；对攻击，连接低度节点、增加环和社团间冗余路径比给枢纽加边更有效；
- **保护关键节点**：资源有限时优先保护集体影响力高、介数高的节点，而不只是度高的节点；
- **抑制级联**：容量冗余（提高 $\alpha$）、隔离（切断社团间联系，阻止故障跨社团扩散）、主动卸载（Motter 2004）；
- **降低依赖**：减少相互依存比例，或让依赖边连接度相近的节点。

::: {.callout-warn}
“提高鲁棒性”与“提高可攻击性”是同一枚硬币的两面。对病原体或肿瘤细胞网络，我们希望找到其最脆弱之处；对宿主细胞或脑网络，我们希望理解其冗余来自何处。同一个算法（如网络瓦解）在两类问题中的含义正好相反，解读时要明确站在哪一方。
:::

## 生物系统的鲁棒性：冗余、缓冲与必需性 {#biological-robustness}

### 生物鲁棒性的来源

Kitano（2004，*Nature Reviews Genetics*）把生物鲁棒性归结为几类机制：**系统控制**（负反馈、前馈）、**冗余与多样性**（同工酶、重复基因、可替代通路）、**模块化**（把扰动限制在局部）以及**解耦**（把低层噪声与高层功能隔开）。他特别强调“鲁棒而脆弱”（robust yet fragile）：为抵抗常见扰动而演化出的结构，会对罕见扰动格外脆弱——这与无标度网络“耐随机、怕攻击”是同一类现象。

网络结构对基因敲除鲁棒性的贡献有直接证据。酿酒酵母中约五分之一的基因单独敲除即致死（Giaever 等 2002，*Nature* 构建了覆盖约 96% 开放阅读框的缺失株集合），其余大多数敲除表型很弱。缓冲来自两类机制：**重复基因**——Gu 等（2003，*Nature*）估计酵母中无表型的基因敲除至少有四分之一是由重复基因补偿的；**无关基因之间的相互作用**（替代通路、网络重路由）——Wagner（2000，*Nature Genetics*）的全基因组分析认为后者是更主要的原因。两者并不矛盾：它们在不同数据与定义下估计了不同的补偿形式。

### 必需性与拓扑：要区分“结构碎裂”与“功能丧失”

Jeong 等（2001，*Nature*）发现酵母蛋白相互作用网络中高度蛋白更可能是必需的（[论文精读](paper-jeong2001_lethality.html)），这常被解读为“删除枢纽使网络碎裂而致死”。但 He 与 Zhang（2006，*PLoS Genetics*）和 Zotenko 等（2008，*PLoS Computational Biology*）给出了不依赖连通性的解释：必需性来自少数必需相互作用或必需复合物，度高只是因为参与其中。详见[致死性与中心性：枢纽蛋白假说及其争议](molecular-networks.centrality-lethality.html)，这里不再重复数据。

对鲁棒性研究的启示是：**渗流意义上的结构鲁棒与细胞的功能鲁棒是两个层次**。PPI 网络删除一个蛋白后最大分支几乎不变，细胞仍可能死亡（该蛋白是核糖体的组成部分）；反之，网络被切成两块，细胞也可能存活（断开的部分对当前环境不重要）。把拓扑分析与功能模型（如代谢通量模型）或实验表型结合，才能回答“哪些扰动是致命的”。

::: {.callout-bio}
**结构扰动的两种类型**。Zhong 等（2009，*Molecular Systems Biology*）提出“边特异”（edgetic）扰动的概念：许多致病突变并不消除蛋白，而只破坏它的部分相互作用。一个基因关联多种疾病的情形，有相当一部分可以用同一基因的不同突变破坏不同的边来解释。这使“点渗流 vs 边渗流”的区分在疾病遗传学中有了具体意义。
:::

## 代谢网络的基因敲除与级联 {#metabolic-knockouts}

代谢网络为鲁棒性研究提供了少有的“可以计算功能”的系统：给定反应化学计量和培养基，可以预测细胞能否合成生长所需的全部前体。

### 三种预测必需性的方法

1. **拓扑损伤**：删除一个酶后，有多少代谢物无法再从营养物出发生成。Lemke 等（2004，*Bioinformatics*）对大肠杆菌的分析预测约 91% 的酶删除后只造成很小损伤，约 9% 造成严重损伤，而这一小部分包含了多数实验证实的必需酶——损伤分布高度不均，与“耐随机、怕攻击”的模式一致。
2. **通量平衡分析**（flux balance analysis, FBA）：在稳态 $S\mathbf v=\mathbf 0$ 与通量上下界约束下最大化生物量通量；敲除基因即令其催化反应的通量为零，最优生物量为零（或远低于野生型）即预测为必需（Orth、Thiele 与 Palsson 2010 的入门介绍）。Edwards 与 Palsson（2000，*PNAS*）用大肠杆菌基因组尺度模型对中心代谢基因缺失做预测，在 86% 的检验案例中定性正确。
3. **最小代谢调整**（MOMA）：Segrè、Vitkup 与 Church（2002，*PNAS*）认为突变株不会立刻达到新的最优，而是使通量分布尽量接近野生型，这对刚敲除的突变株预测更准确。

### 级联与合成拯救

代谢网络中的级联并非负载过载，而是**上游缺失导致下游无法合成**的“饿死”式级联：一个反应失去底物，它的产物又是其他反应的底物……Smart 等（2008，*PNAS*）发现真实代谢网络对这类级联比零模型更鲁棒，关键在于分支代谢物（可由多条途径生成的代谢物）的组织方式。

反直觉的是，**额外的损伤可以挽救细胞**。Motter、Gulbahce、Almaas 与 Barabási（2008，*Molecular Systems Biology*）用 FBA 研究缺失必需酶而无法生长的突变株，发现一些突变株可以通过再敲除其他基因恢复生长（**合成拯救**，synthetic rescue），机制是迫使通量绕过受损功能或补偿失去的功能。Barabási 第 8 章称之为“拉撒路效应”，并把它与级联防御中的主动移除类比。

**算例（代码中的玩具网络）**：葡萄糖 → G6P（基因 G1）→ 丙酮酸（G2）→ 乙酰辅酶 A（同工酶 G3 或 G4）→ 脂质（G8）；核糖-5-磷酸可由 G6P 经一步（G5）或由丙酮酸经两步旁路（G6、G7）生成。生物量需要核糖-5-磷酸、脂质和丙酮酸。单独敲除 G1、G2 或 G8 致死（无替代）；G3 与 G4 互为冗余，G5 与旁路互为冗余，所以 (G3,G4)、(G5,G6)、(G5,G7) 是合成致死对。冗余让单基因敲除变得无害，同时也制造了成对的弱点——这正是下一页合成致死疗法的逻辑。

::: {.callout-warn}
FBA 的必需性预测依赖培养基设定、生物量方程和基因–蛋白–反应规则（GPR），在不同条件下可以改变；拓扑方法忽略化学计量与热力学，常把辅因子（ATP、NADH 等）当作普通代谢物，导致虚假连通。比较网络方法时，要在相同条件与相同实验金标准上评估。
:::

## 脑损伤与病变的网络后果 {#brain-lesions}

### 从“局部损伤”到“网络损伤”

传统神经心理学按损伤部位推断功能缺损，但临床上常见远离损伤部位的功能改变（远隔效应，diaschisis）。网络观点把局灶损伤看作对连接组的“删点”，其后果取决于被删节点在网络中的位置。脑网络的构建与枢纽、富人俱乐部见[拓扑指标：小世界、模块、枢纽与富人俱乐部](brain-connectome.topology.html)。

### 虚拟损伤与模拟攻击

- Achard 等（2006，*Journal of Neuroscience*）在静息态 fMRI 构建的 90 区功能网络上做模拟攻击：网络对针对枢纽的攻击比同等的无标度网络更有韧性，对随机失效的韧性与之相当。
- Honey 与 Sporns（2008，*Human Brain Mapping*）以及 Alstott、Breakspear、Hagmann、Cammoun 与 Sporns（2009，*PLoS Computational Biology*）把损伤放进**动力学模型**：在人脑结构连接组上模拟静息态活动，比较损伤前后的功能连接。Alstott 等发现损伤会改变远处脑区之间的功能连接，常常波及两侧半球；沿皮层中线和颞顶联合区附近的损伤引起大范围改变，初级感觉或运动区的损伤影响则较局限；影响大小部分可由损伤部位的结构网络指标预测。
- Crossley 等（2014，*Brain*）在 56 名健康人的弥散张量成像网络上表明，靶向枢纽的计算攻击比随机攻击更大幅度降低网络效率；再对涵盖 26 种脑疾病、超过 2 万名受试者的 MRI 荟萃分析病灶图进行比较，发现跨疾病共有的灰质病变更可能位于正常连接组的枢纽，其中 9 种疾病（包括精神分裂症和阿尔茨海默病）单独达到显著。

### 病人数据：不是所有“枢纽”都一样

- Gratton、Nomura、Pérez 与 D'Esposito（2012，*Journal of Cognitive Neuroscience*）用局灶损伤病人的静息态 fMRI 发现：只有损伤负责**子网络之间**通信的“连接者”区域（高参与系数）才会降低全脑模块度，模块内“枢纽”的损伤则不会；而且这种网络紊乱延伸到结构上完好的对侧半球。
- Warren 等（2014，*PNAS*）追踪 30 名局灶损伤病人的长期认知结局：19 人损伤位于按系统密度和参与系数定义的“目标枢纽”，11 人损伤位于按度中心性定义的“对照枢纽”。前者出现严重而广泛的认知缺损，后者的缺损较局限。

这些研究共同提示：在脑网络中，**高度**（尤其是功能相关网络中的度，受子网络大小影响）不一定是损伤后果的最佳预测指标，**跨模块整合**的位置（连接者、参与系数）可能更关键。本页代码用一个模块化随机网络演示了这一点：删除 6 个连接者使全局效率下降明显多于删除 6 个模块内枢纽或随机节点，同时模块度反而升高（模块变得更孤立）。

::: {.callout-warn}
虚拟损伤研究的局限：（1）结构连接组来自健康人，忽略了损伤后的可塑性和代偿重组；（2）功能网络的“度”受网络构建方法（阈值、全局信号回归）影响很大；（3）模拟删点不等于真实病灶——卒中会损伤白质纤维（更像删边），神经退行性病变是渐进的、选择性的“攻击”；（4）病人研究样本小、病灶位置不随机。综述见 Fornito、Zalesky 与 Breakspear（2015，*Nature Reviews Neuroscience*）。
:::

## 合成致死与癌症治疗 {#synthetic-lethality}

::: {.callout-def}
**合成致死**（synthetic lethality）：两个基因各自失活时细胞存活，同时失活时细胞死亡。若肿瘤细胞已经失去基因 A（如抑癌基因突变），抑制 A 的合成致死伙伴 B 就能选择性杀死肿瘤细胞，而保留 A 正常的正常细胞（Kaelin 2005，*Nature Reviews Cancer*）。**遗传相互作用网络**以基因为节点，以合成致死或更广义的“双突变表型偏离单突变预期”为边。
:::

### 网络视角

合成致死是冗余的直接后果：两条平行通路、一对同工酶或重复基因，任何一个都能完成功能，两个都失去才致死。在酵母中，Tong 等（2004，*Science*）把 132 个查询基因的突变与约 4700 个存活缺失株杂交，得到约 1000 个基因、约 4000 个相互作用的遗传相互作用网络；Costanzo 等（2010，*Science*）把规模扩大到检测约 540 万个基因对、覆盖约 75% 的基因。Kelley 与 Ideker（2005，*Nature Biotechnology*）把遗传相互作用与物理相互作用网络结合，发现约 40% 的已知遗传相互作用可以用“通路内”或“通路间”模型解释，而且“通路间”模型（两条并行通路各中一刀）解释力更强——这与本专题“平行路径提供冗余”的图景一致。

### 从概念到临床：PARP 抑制剂

BRCA1/BRCA2 参与同源重组修复 DNA 双链断裂，PARP 参与单链断裂的修复。Farmer 等（2005，*Nature*）与 Bryant 等（2005，*Nature*）同期报道：BRCA 功能缺陷的细胞对 PARP 抑制极为敏感——PARP 被抑制后，未修复的单链损伤在复制时变成双链断裂，而 BRCA 缺陷细胞无法修复。PARP 抑制剂是首批按合成致死原理设计并获临床批准的药物（Lord 与 Ashworth 2017，*Science*），这一综述也讨论了耐药与联合用药的挑战。

### 计算预测

人类细胞中系统检测所有基因对不现实，计算方法因此重要。Jerby-Arnon 等（2014，*Cell*）提出数据驱动的流程（DAISY），从大规模癌症基因组数据中推断合成致死对（如果两个基因很少同时失活、且一个失活时另一个的必需性上升，就可能构成合成致死对），并实验验证了抑癌基因 VHL 的部分预测伙伴。网络方法（通路冗余、模块间关系）、代谢模型（成对反应敲除）与 CRISPR 组合筛选正在互相补充。

::: {.callout-bio}
把合成致死放回鲁棒性框架：单个肿瘤驱动突变相当于对细胞网络的一次“攻击”，肿瘤依赖剩余的冗余通路维持存活；合成致死疗法则是“第二次精准攻击”，利用的正是肿瘤已经失去冗余这一点。Barabási 第 8 章、Kitano（2004）关于“鲁棒而脆弱”的论述为这一思路提供了系统层面的解释。多靶点药物与[网络药理学](network-medicine.network-pharmacology.html)中的药物组合也可以从同一角度理解。
:::

## 数学推导与算法 {#derivations}

本页补充正文中略去的推导与算法。随机失效阈值的“二项稀释”推导与 Newman–Ziff 基本算法见[网络可控性与稳定性的数学推导](controllability.derivations.html)；SIR 与边渗流的映射见[网络上的传播与免疫的数学推导](spreading.derivations.html)。

### A. 生成函数解的阈值与临界指数（ER 网络）

由 $P_\infty=\phi(1-e^{-\langle k\rangle P_\infty})$，在 $P_\infty$ 小时展开 $1-e^{-x}\approx x-x^2/2$：
$$
P_\infty\approx\phi\langle k\rangle P_\infty-\tfrac12\phi\langle k\rangle^2P_\infty^2
\;\Rightarrow\;P_\infty\approx\frac{2(\phi\langle k\rangle-1)}{\phi\langle k\rangle^2}\propto(\phi-\phi_c)^1,
$$
即 $\beta_p=1$，$\phi_c=1/\langle k\rangle$。对 $\langle k^2\rangle$ 发散的分布，$G_1(u)$ 在 $u=1$ 附近的展开含非整数次幂项，导致 $\beta_p$ 依赖于 $\gamma$（Cohen 等 2002）。

### B. 攻击阈值的推导要点

1. 删除比例 $f$ 的最高度节点后，新的最大度由 $f=\int_{k'_{\max}}^{k_{\max}}P(k)\,dk$ 决定，忽略 $k_{\max}$ 项得 $k'_{\max}=k_{\min}f^{1/(1-\gamma)}$。
2. 被删枢纽带走的边占全部边端的比例 $\tilde f=\frac{1}{\langle k\rangle}\int_{k'_{\max}}^{k_{\max}}kP(k)\,dk=f^{(2-\gamma)/(1-\gamma)}$（用 $\langle k\rangle\approx\frac{\gamma-1}{\gamma-2}k_{\min}$）。
3. 无度相关时，这些边的另一端是随机的，剩余网络等价于“度分布截断于 $k'_{\max}$、再随机删去比例 $\tilde f$ 的边”的网络。随机删边后 $\kappa'=(1-\tilde f)\kappa+\tilde f$，代入 Molloy–Reed 条件 $\kappa'=2$ 得 $(1-\tilde f)(\kappa-1)=1$，即 $\tilde f=1-1/(\kappa-1)$。
4. 用截断幂律的 $\kappa=\frac{2-\gamma}{3-\gamma}\,\frac{k'^{\,3-\gamma}_{\max}-k_{\min}^{3-\gamma}}{k'^{\,2-\gamma}_{\max}-k_{\min}^{2-\gamma}}$，代入 $k'_{\max}$ 与 $\tilde f$，整理即得正文中的攻击阈值方程。

### C. 自适应攻击的计算

```text
算法 1  自适应度攻击（RD）与 R 指标
输入：图 G(V,E)，|V| = N
1. 用桶（按度分组的链表）存储节点；s ← [ ]
2. for Q = 1 … N:
3.     取出当前度最大的节点 v，删除 v
4.     对 v 的每个邻居 w：把 w 从度为 d 的桶移到度为 d−1 的桶
5.     计算最大连通分支 s(Q)/N
6. R ← (1/N) Σ s(Q)
```

第 3–4 步每次 $O(k_v)$，总计 $O(L)$。第 5 步若每步重新做 BFS 是 $O(N(N+L))$；更快的做法是记录完整的删除顺序，然后**逆序加回**节点，用并查集维护最大分支（与 Newman–Ziff 相同），总复杂度近似 $O(L\,\alpha(N))$。介数攻击（RB）每步都需重算介数（Brandes 算法 $O(NL)$），代价高，常用分批重算或抽样近似介数。

### D. Motter–Lai 级联

```text
算法 2  负载重分配级联
输入：G，容忍参数 α，触发节点 t
1. L ← 介数(G)；对每个 i：C_i ← (1+α) L_i
2. 删除 t
3. repeat
4.     L ← 介数(当前图)
5.     F ← { i : L_i > C_i }
6.     删除 F
7. until F 为空
8. return G = 最大分支节点数 / N
```

每轮重算介数 $O(NL)$，轮数通常很少；大网络可用抽样介数近似。注意结论对“负载”的定义（最短路径、加权流、电力潮流）敏感。

### E. Watts 级联条件

令 $v$ 为“沿一条随机边到达的节点属于易损团簇”的生成函数意义下的量。在局部树状网络中，从一个易损节点出发沿边扩散，到达节点的剩余度分布为 $kP(k)/\langle k\rangle$，它是易损节点的概率为 $\rho_k$。易损团簇的平均后代数为
$$
m=\sum_k\frac{kP(k)}{\langle k\rangle}\rho_k(k-1),
$$
全局级联要求 $m>1$，即 $\sum_kk(k-1)\rho_kP(k)>\langle k\rangle$。这与 Molloy–Reed 判据形式相同，只是把度为 $k$ 的节点以概率 $\rho_k$“占据”——级联问题被化归为以度相关占据概率的点渗流（Callaway 等 2000 处理过这类“依赖度的占据概率”）。

### F. 相互依存网络的切点条件

记 $h(\mu)=p(1-e^{-\langle k\rangle\mu})^2$，稳态 $\mu=h(\mu)$。$p$ 减小时，曲线 $h$ 下移；临界点是 $h$ 与对角线**相切**之时：$\mu=h(\mu)$ 且 $h'(\mu)=1$。令 $z=\langle k\rangle\mu$，第一式给出 $\langle k\rangle p=z/(1-e^{-z})^2$，第二式等价于对 $z$ 求该表达式的极小值，数值上 $z_c\approx1.2564$，$\langle k\rangle p_c\approx2.4554$。因为切点处 $\mu_c=z_c/\langle k\rangle>0$，序参量在临界点不连续——这就是一级相变的来源。单一网络中 $h(\mu)=p(1-e^{-\langle k\rangle\mu})$ 在 $\mu=0$ 处斜率为 $p\langle k\rangle$，相切发生在原点，相变连续。

## 研究前沿与开放问题 {#frontiers}

1. **从结构鲁棒到动力学韧性**。连通性只是功能的前提。Gao、Barzel 与 Barabási（2016，*Nature*）把多维网络动力学约化为一维有效方程，预测系统何时从健康态跃迁到崩溃态；Artime 等（2024，*Nature Reviews Physics*）的综述系统比较了结构鲁棒性、动力学韧性与恢复能力的各种定义。如何把二者结合到生物网络（如基因调控网络的多稳态）上，仍缺乏实验检验。
2. **高阶与时序结构中的渗流**。超图、单纯复形、时序网络中的渗流可能出现不连续转变与多重转变；在蛋白复合物（天然是高阶相互作用）和时变脑网络上，传统点/边渗流是否足够，尚无定论。
3. **不完整网络上的鲁棒性推断**。生物网络观测有大量缺失边和研究偏倚，鲁棒性指标对缺失边高度敏感。如何在“网络本身不确定”的条件下给出带置信区间的 $f_c$ 或 $R$，是方法学空白。
4. **合成致死的网络预测**。人类细胞的遗传相互作用远未测全，计算预测（网络、代谢模型、基因组数据、深度学习）与 CRISPR 组合筛选结果的一致性有限，且合成致死关系高度依赖细胞背景。
5. **脑损伤后果的个体化预测**。病灶网络映射（lesion network mapping）、个体结构连接组与动力学模型相结合，能否在卒中或手术前预测个体的认知结局，需要大样本、前瞻性研究验证。

## 生物医学应用 {#biomedical}

| 问题 | 网络操作 | 代表研究 | 本站相关页面 |
|---|---|---|---|
| 哪些基因或蛋白是必需的 | 删点后的结构损伤 / 功能模型 | Jeong 2001；Lemke 2004；Edwards 与 Palsson 2000 | [生物系统的鲁棒性](robustness.biological-robustness.html)，[致死性与中心性](molecular-networks.centrality-lethality.html) |
| 代谢缺陷能否被补偿 | 敲除、合成拯救 | Segrè 2002；Motter 2008；Smart 2008 | [代谢网络的基因敲除](robustness.metabolic-knockouts.html) |
| 局灶脑损伤的远隔后果 | 虚拟损伤、病人网络 | Alstott 2009；Gratton 2012；Warren 2014 | [脑损伤与病变的网络后果](robustness.brain-lesions.html) |
| 脑疾病病灶为何集中于枢纽 | 枢纽攻击与病灶定位 | Crossley 2014 | [脑连接组](brain-connectome.html) |
| 癌症的选择性弱点 | 成对删除（合成致死） | Farmer 2005；Bryant 2005；Jerby-Arnon 2014 | [合成致死与癌症治疗](robustness.synthetic-lethality.html) |
| 接种与隔离对象的选择 | 对接触网络的攻击 / 渗流 | Cohen 2003 | [免疫策略](spreading.immunization.html) |
| 病原体关键蛋白与药物靶点 | 攻击病原体网络 | Barabási 第 8 章的讨论 | [网络药理学](network-medicine.network-pharmacology.html) |

把这些应用放在一起看，鲁棒性分析在生物医学中回答的是同一个问题的不同版本：**系统的冗余在哪里，冗余耗尽之处在哪里**。对宿主，我们希望保护冗余；对病原体和肿瘤，我们希望找到冗余已经耗尽的位置。

## 适用范围与常见误用 {#limitations}

1. **误用**：笼统地说“无标度网络很鲁棒”。→ **正解**：要说明扰动类型。对随机失效鲁棒、对攻击脆弱是同一性质（$\langle k^2\rangle$ 大）的两面；相互依存时连“耐随机失效”也不再成立。
2. **误用**：把理论 $f_c$ 直接套用到真实网络。→ **正解**：理论假设无度相关、局部树状、无限大；应对观测网络和保度随机化网络做模拟比较，并说明 $f_c$ 的判定规则。
3. **误用**：把“最大连通分支变小”等同于“功能丧失”。→ **正解**：结构连通是功能的必要条件之一，不是充分条件；生物问题应尽量使用功能性指标（生物量合成、信号可达性、认知表现）。
4. **误用**：只按初始度排序做攻击，就宣称“网络对攻击的脆弱程度为……”。→ **正解**：初始度、自适应度、介数、集体影响力给出的结果可能相差很大；报告时写明策略，必要时比较多种。
5. **误用**：在不完整的蛋白相互作用网络上解读鲁棒性差异。→ **正解**：研究偏倚使被研究得多的蛋白度更高，缺失边会系统性地低估鲁棒性；做敏感性分析（随机删除或补充一定比例的边）后再下结论。
6. **误用**：把经验数据中的厚尾分布当作级联或临界性的证据。→ **正解**：需要严格的幂律检验，并排除其他生成机制。
7. **误用**：把“相互依存”随意套用到任何两个相关的网络。→ **正解**：依赖边必须有“一方失效则另一方失效”的证据；仅有相关或调节关系时，一级相变等结论不适用。
8. **误用**：用功能网络中的“度”定义脑枢纽，并预测损伤后果。→ **正解**：功能网络的度受子网络大小与构建方法影响；参与系数、系统密度等指标在病人数据中预测性更好（Warren 2014），且结论需要独立样本验证。

## 关联知识 {#related}

- [结构鲁棒性](controllability.structural-robustness.html)：$f_c$ 的二项稀释推导与 Newman–Ziff 算法，本专题的起点。
- [连通分支与巨连通分支](network-metrics.components.html)、[ER 随机网络](network-metrics.er-random-graph.html)：巨分支与渗流相变的基础。
- [幂律度分布与无标度网络](network-models.scale-free.html)：决定 $\langle k^2\rangle$ 与“耐随机、怕攻击”的度分布。
- [网络上的传播与免疫](spreading.html)：SIR 最终规模等价于边渗流，目标免疫就是攻击；阈值模型与本专题的级联模型相同。
- [度相关性与网络结构的高阶统计](degree-correlations.html)：同配性改变渗流阈值，洋葱结构与同配性相关但不等同。
- [致死性与中心性](molecular-networks.centrality-lethality.html)：蛋白必需性与度的关系及其竞争性解释。
- [拓扑指标：小世界、模块、枢纽与富人俱乐部](brain-connectome.topology.html)：脑网络枢纽、富人俱乐部与虚拟损伤分析的背景。
- [动力学稳定性](controllability.dynamical-stability.html)：结构鲁棒性之外，平衡态稳定性与韧性的分析框架。

## 核心文献 {#references}

### Albert、Jeong 与 Barabási 2000：Error and attack tolerance of complex networks（Nature）

- **背景**：互联网、万维网等系统在大量组件随机故障下仍能工作，其结构原因是什么？
- **核心发现**：无标度网络对随机删点高度鲁棒，对按度攻击极其脆弱；ER 网络对两种删除的反应相近。
- **阅读要点**：区分直径与最大分支两种鲁棒性指标；注意攻击使用的是初始度还是重新计算的度。
- **延伸思考**：在蛋白相互作用网络中，“随机失效”和“蓄意攻击”分别对应什么生物学过程（自发突变、药物、病原体效应蛋白）？

DOI：[10.1038/35019019](https://doi.org/10.1038/35019019)；精读：[Albert 2000](paper-albert2000_attack.html)

### Callaway、Newman、Strogatz 与 Watts 2000：Network robustness and fragility: percolation on random graphs（PRL）

- **背景**：此前的随机图渗流结果多限于泊松度分布，与真实网络的偏态度分布相去甚远。
- **核心发现**：用生成函数给出任意度分布网络上点渗流、边渗流以及“占据概率依赖于度”的渗流的精确解，统一处理随机失效与按度删除。
- **阅读要点**：掌握 $u=1-\phi+\phi G_1(u)$ 一类自洽方程的推导和图解；对照同期 Cohen 等（2000）的 Molloy–Reed 路线。
- **延伸思考**：如果占据概率依赖于节点的某个生物学属性（如表达量）而不是度，方程应怎样修改？

DOI：[10.1103/PhysRevLett.85.5468](https://doi.org/10.1103/PhysRevLett.85.5468)

### Cohen、Erez、ben-Avraham 与 Havlin 2000/2001：Resilience of the Internet to random breakdowns；Breakdown of the Internet under intentional attack（PRL）

- **背景**：Albert 等（2000）的模拟结论需要解析理论支撑。
- **核心发现**：2000 年的论文由 Molloy–Reed 判据得到随机删除阈值，证明 $\gamma\le3$ 时无限网络不会因随机删除而碎裂；2001 年的论文推导按度攻击的阈值方程，表明攻击阈值很小。
- **阅读要点**：注意有限规模下 $f_c$ 随 $N$ 的变化，以及攻击推导中“把删枢纽转化为随机删边”的技巧。
- **延伸思考**：若网络存在度相关（枢纽彼此相连），攻击推导的哪一步不再成立？

DOI：[10.1103/PhysRevLett.85.4626](https://doi.org/10.1103/PhysRevLett.85.4626)；[10.1103/PhysRevLett.86.3682](https://doi.org/10.1103/PhysRevLett.86.3682)

### Motter 与 Lai 2002：Cascade-based attacks on complex networks（Physical Review E）

- **背景**：静态删点忽略了失效后负载的重新分配。
- **核心发现**：在负载可重分配的网络中，负载高度异质使网络特别脆弱：移除单个关键节点就可能引发覆盖大部分网络的过载级联。
- **阅读要点**：理解容量 $(1+\alpha)L_i$ 的设定和 $G$ 随 $\alpha$ 的变化；比较按负载、按度和随机触发。
- **延伸思考**：代谢网络或血管网络中，“负载”与“容量”分别可以对应什么物理量？

DOI：[10.1103/PhysRevE.66.065102](https://doi.org/10.1103/PhysRevE.66.065102)

### Buldyrev 等 2010：Catastrophic cascade of failures in interdependent networks（Nature）

- **背景**：基础设施相互依存，单一网络的鲁棒性理论不足以描述其失效。
- **核心发现**：相互依存使渗流转变成为一级相变，阈值大幅提高；度分布越宽，系统越脆弱。
- **阅读要点**：重点理解 $x=p\,g_A(p\,g_B(x))$ 的图解与切点条件。
- **延伸思考**：在细胞中，哪些网络对之间存在严格意义上的“依赖”？

DOI：[10.1038/nature08932](https://doi.org/10.1038/nature08932)；精读：[Buldyrev 2010](paper-buldyrev2010_cascade.html)

### Schneider 等 2011：Mitigation of malicious attacks on networks（PNAS）

- **背景**：单一渗流阈值无法反映网络在崩溃之前承受的损伤。
- **核心发现**：提出 R 指标；保度换边可以在几乎不改变功能的前提下显著提高 R；最鲁棒的网络呈洋葱结构。
- **阅读要点**：注意 R 用的是自适应度攻击；比较 R 与渗流阈值 $q_c$ 对同一改造的反应。
- **延伸思考**：如果把“换边”的成本设为生物学约束（如脑网络中的连线长度），优化结果会怎样？

DOI：[10.1073/pnas.1009440108](https://doi.org/10.1073/pnas.1009440108)

### Alstott 等 2009：Modeling the impact of lesions in the human brain（PLoS Computational Biology）

- **背景**：局灶脑损伤的功能后果高度依赖部位，且常难以预测。
- **核心发现**：在人脑结构连接组上用动力学模型模拟损伤，损伤会改变远处脑区的功能连接；中线和颞顶联合区附近的损伤影响广泛，初级感觉运动区损伤影响局限。
- **阅读要点**：区分“结构删点后的拓扑变化”与“动力学模型中的功能连接变化”两类评估。
- **延伸思考**：如何用卒中病人的纵向数据检验模型预测？

DOI：[10.1371/journal.pcbi.1000408](https://doi.org/10.1371/journal.pcbi.1000408)

### Lord 与 Ashworth 2017：PARP inhibitors: synthetic lethality in the clinic（Science）

- **背景**：合成致死在酵母遗传学中早已熟知，如何变成癌症疗法？
- **核心发现**：综述 PARP 抑制剂从 BRCA 缺陷细胞的合成致死（Farmer 2005；Bryant 2005）到临床获批的过程，以及耐药与联合用药的挑战。
- **阅读要点**：把“肿瘤失去一条修复通路”理解为网络冗余的丧失。
- **延伸思考**：网络方法能否预测哪些肿瘤会对 PARP 抑制剂产生耐药？

DOI：[10.1126/science.aam7344](https://doi.org/10.1126/science.aam7344)

### 其他引用文献

- Molloy M, Reed B (1995) A critical point for random graphs with a given degree sequence. *Random Structures & Algorithms*. [10.1002/rsa.3240060204](https://doi.org/10.1002/rsa.3240060204)
- Newman MEJ, Ziff RM (2000) Efficient Monte Carlo algorithm and high-precision results for percolation. *PRL*. [10.1103/PhysRevLett.85.4104](https://doi.org/10.1103/PhysRevLett.85.4104)
- Newman MEJ, Strogatz SH, Watts DJ (2001) Random graphs with arbitrary degree distributions and their applications. *PRE*. [10.1103/PhysRevE.64.026118](https://doi.org/10.1103/PhysRevE.64.026118)
- Cohen R, ben-Avraham D, Havlin S (2002) Percolation critical exponents in scale-free networks. *PRE*. [10.1103/PhysRevE.66.036113](https://doi.org/10.1103/PhysRevE.66.036113)
- Holme P, Kim BJ, Yoon CN, Han SK (2002) Attack vulnerability of complex networks. *PRE*. [10.1103/PhysRevE.65.056109](https://doi.org/10.1103/PhysRevE.65.056109)
- Newman MEJ (2002) Assortative mixing in networks. *PRL*. [10.1103/PhysRevLett.89.208701](https://doi.org/10.1103/PhysRevLett.89.208701)
- Watts DJ (2002) A simple model of global cascades on random networks. *PNAS*. [10.1073/pnas.082090499](https://doi.org/10.1073/pnas.082090499)
- Goh K-I, Lee D-S, Kahng B, Kim D (2003) Sandpile on scale-free networks. *PRL*. [10.1103/PhysRevLett.91.148701](https://doi.org/10.1103/PhysRevLett.91.148701)
- Crucitti P, Latora V, Marchiori M (2004) Model for cascading failures in complex networks. *PRE*. [10.1103/PhysRevE.69.045104](https://doi.org/10.1103/PhysRevE.69.045104)
- Motter AE (2004) Cascade control and defense in complex networks. *PRL*. [10.1103/PhysRevLett.93.098701](https://doi.org/10.1103/PhysRevLett.93.098701)
- Paul G, Tanizawa T, Havlin S, Stanley HE (2004) Optimization of robustness of complex networks. *European Physical Journal B*. [10.1140/epjb/e2004-00112-3](https://doi.org/10.1140/epjb/e2004-00112-3)
- Valente AXCN, Sarkar A, Stone HA (2004) Two-peak and three-peak optimal complex networks. *PRL*. [10.1103/PhysRevLett.92.118702](https://doi.org/10.1103/PhysRevLett.92.118702)
- Tanizawa T, Paul G, Cohen R, Havlin S, Stanley HE (2005) Optimization of network robustness to waves of targeted and random attacks. *PRE*. [10.1103/PhysRevE.71.047101](https://doi.org/10.1103/PhysRevE.71.047101)
- Parshani R, Buldyrev SV, Havlin S (2010) Interdependent networks: reducing the coupling strength leads to a change from a first to second order percolation transition. *PRL*. [10.1103/PhysRevLett.105.048701](https://doi.org/10.1103/PhysRevLett.105.048701)
- Gao J, Buldyrev SV, Stanley HE, Havlin S (2012) Networks formed from interdependent networks. *Nature Physics*. [10.1038/nphys2180](https://doi.org/10.1038/nphys2180)
- Bashan A, Berezin Y, Buldyrev SV, Havlin S (2013) The extreme vulnerability of interdependent spatially embedded networks. *Nature Physics*. [10.1038/nphys2727](https://doi.org/10.1038/nphys2727)
- Morone F, Makse HA (2015) Influence maximization in complex networks through optimal percolation. *Nature*. [10.1038/nature14604](https://doi.org/10.1038/nature14604)
- Braunstein A, Dall'Asta L, Semerjian G, Zdeborová L (2016) Network dismantling. *PNAS*. [10.1073/pnas.1605083113](https://doi.org/10.1073/pnas.1605083113)
- Zhong Q 等 (2009) Edgetic perturbation models of human inherited disorders. *Molecular Systems Biology*. [10.1038/msb.2009.80](https://doi.org/10.1038/msb.2009.80)
- Kitano H (2004) Biological robustness. *Nature Reviews Genetics*. [10.1038/nrg1471](https://doi.org/10.1038/nrg1471)
- Wagner A (2000) Robustness against mutations in genetic networks of yeast. *Nature Genetics*. [10.1038/74174](https://doi.org/10.1038/74174)
- Giaever G 等 (2002) Functional profiling of the *Saccharomyces cerevisiae* genome. *Nature*. [10.1038/nature00935](https://doi.org/10.1038/nature00935)
- Gu Z 等 (2003) Role of duplicate genes in genetic robustness against null mutations. *Nature*. [10.1038/nature01198](https://doi.org/10.1038/nature01198)
- Jeong H, Mason SP, Barabási A-L, Oltvai ZN (2001) Lethality and centrality in protein networks. *Nature*. [10.1038/35075138](https://doi.org/10.1038/35075138)
- He X, Zhang J (2006) Why do hubs tend to be essential in protein networks? *PLoS Genetics*. [10.1371/journal.pgen.0020088](https://doi.org/10.1371/journal.pgen.0020088)
- Zotenko E 等 (2008) Why do hubs in the yeast protein interaction network tend to be essential. *PLoS Computational Biology*. [10.1371/journal.pcbi.1000140](https://doi.org/10.1371/journal.pcbi.1000140)
- Edwards JS, Palsson BO (2000) The *Escherichia coli* MG1655 in silico metabolic genotype. *PNAS*. [10.1073/pnas.97.10.5528](https://doi.org/10.1073/pnas.97.10.5528)
- Segrè D, Vitkup D, Church GM (2002) Analysis of optimality in natural and perturbed metabolic networks. *PNAS*. [10.1073/pnas.232349399](https://doi.org/10.1073/pnas.232349399)
- Lemke N 等 (2004) Essentiality and damage in metabolic networks. *Bioinformatics*. [10.1093/bioinformatics/btg386](https://doi.org/10.1093/bioinformatics/btg386)
- Smart AG, Amaral LAN, Ottino JM (2008) Cascading failure and robustness in metabolic networks. *PNAS*. [10.1073/pnas.0803571105](https://doi.org/10.1073/pnas.0803571105)
- Motter AE, Gulbahce N, Almaas E, Barabási A-L (2008) Predicting synthetic rescues in metabolic networks. *Molecular Systems Biology*. [10.1038/msb.2008.1](https://doi.org/10.1038/msb.2008.1)
- Orth JD, Thiele I, Palsson BØ (2010) What is flux balance analysis? *Nature Biotechnology*. [10.1038/nbt.1614](https://doi.org/10.1038/nbt.1614)
- Achard S 等 (2006) A resilient, low-frequency, small-world human brain functional network with highly connected association cortical hubs. *Journal of Neuroscience*. [10.1523/JNEUROSCI.3874-05.2006](https://doi.org/10.1523/JNEUROSCI.3874-05.2006)
- Honey CJ, Sporns O (2008) Dynamical consequences of lesions in cortical networks. *Human Brain Mapping*. [10.1002/hbm.20579](https://doi.org/10.1002/hbm.20579)
- Gratton C, Nomura EM, Pérez F, D'Esposito M (2012) Focal brain lesions to critical locations cause widespread disruption of the modular organization of the brain. *Journal of Cognitive Neuroscience*. [10.1162/jocn_a_00222](https://doi.org/10.1162/jocn_a_00222)
- Warren DE 等 (2014) Network measures predict neuropsychological outcome after brain injury. *PNAS*. [10.1073/pnas.1322173111](https://doi.org/10.1073/pnas.1322173111)
- Crossley NA 等 (2014) The hubs of the human connectome are generally implicated in the anatomy of brain disorders. *Brain*. [10.1093/brain/awu132](https://doi.org/10.1093/brain/awu132)
- Fornito A, Zalesky A, Breakspear M (2015) The connectomics of brain disorders. *Nature Reviews Neuroscience*. [10.1038/nrn3901](https://doi.org/10.1038/nrn3901)
- Kaelin WG (2005) The concept of synthetic lethality in the context of anticancer therapy. *Nature Reviews Cancer*. [10.1038/nrc1691](https://doi.org/10.1038/nrc1691)
- Farmer H 等 (2005) Targeting the DNA repair defect in BRCA mutant cells as a therapeutic strategy. *Nature*. [10.1038/nature03445](https://doi.org/10.1038/nature03445)
- Bryant HE 等 (2005) Specific killing of BRCA2-deficient tumours with inhibitors of poly(ADP-ribose) polymerase. *Nature*. [10.1038/nature03443](https://doi.org/10.1038/nature03443)
- Tong AHY 等 (2004) Global mapping of the yeast genetic interaction network. *Science*. [10.1126/science.1091317](https://doi.org/10.1126/science.1091317)
- Costanzo M 等 (2010) The genetic landscape of a cell. *Science*. [10.1126/science.1180823](https://doi.org/10.1126/science.1180823)
- Kelley R, Ideker T (2005) Systematic interpretation of genetic interactions using protein networks. *Nature Biotechnology*. [10.1038/nbt1096](https://doi.org/10.1038/nbt1096)
- Jerby-Arnon L 等 (2014) Predicting cancer-specific vulnerability via data-driven detection of synthetic lethality. *Cell*. [10.1016/j.cell.2014.07.027](https://doi.org/10.1016/j.cell.2014.07.027)
- Kivelä M 等 (2014) Multilayer networks. *Journal of Complex Networks*. [10.1093/comnet/cnu016](https://doi.org/10.1093/comnet/cnu016)
- Gao J, Barzel B, Barabási A-L (2016) Universal resilience patterns in complex networks. *Nature*. [10.1038/nature16948](https://doi.org/10.1038/nature16948)
- Artime O 等 (2024) Robustness and resilience of complex networks. *Nature Reviews Physics*. [10.1038/s42254-023-00676-y](https://doi.org/10.1038/s42254-023-00676-y)

## 延伸资源 {#resources}

| 类型 | 资源 | 说明 |
|---|---|---|
| 教材 | Barabási《Network Science》第 8 章 Network Robustness（[链接](http://networksciencebook.com/chapter/8)） | 渗流、无标度网络的鲁棒性、攻击容忍、级联失效与建模、构建鲁棒网络；Advanced Topics 含 Molloy–Reed 判据、攻击阈值、最优度分布的推导；CC BY-NC-SA 2.0 |
| 教材 | Newman《Networks》（第 2 版，Oxford University Press 2018）“Percolation and network resilience”一章 | 生成函数方法处理点渗流、边渗流与非均匀删除的标准参考 |
| 教材 | Cohen 与 Havlin《Complex Networks: Structure, Robustness and Function》（Cambridge University Press 2010） | 渗流方法研究网络鲁棒性的专著，作者即 $f_c$ 与攻击阈值解析结果的提出者 |
| 综述 | Dorogovtsev、Goltsev 与 Mendes 2008, Critical phenomena in complex networks, *Rev Mod Phys*（[DOI](https://doi.org/10.1103/RevModPhys.80.1275)） | 网络上渗流与临界现象的全面综述 |
| 综述 | Artime 等 2024, Robustness and resilience of complex networks, *Nat Rev Phys*（[DOI](https://doi.org/10.1038/s42254-023-00676-y)） | 结构鲁棒性、动力学韧性与恢复的最新统一综述 |
| 综述（生物医学） | Fornito、Zalesky 与 Breakspear 2015, The connectomics of brain disorders, *Nat Rev Neurosci*（[DOI](https://doi.org/10.1038/nrn3901)） | 枢纽脆弱性、网络扩散与脑疾病 |
| 中文视频 | 单哥：复杂网络建模·网络鲁棒性（[B 站](https://www.bilibili.com/video/BV1WR4y1G7kH/)，P54–P60） | 约 45 分钟，从渗流理论到随机与度攻击，含 Python 代码 |
| 交互演示 | NetLogo Web：Giant Component（[链接](https://www.netlogoweb.org/launch#https://www.netlogoweb.org/assets/modelslib/Sample%20Models/Networks/Giant%20Component.nlogo)） | 观察巨分支随连边增加而出现的相变 |
| 软件 | NetworkX：`connected_components`、`betweenness_centrality`、`global_efficiency`（[文档](https://networkx.org/documentation/stable/)） | 本专题代码示例使用的函数 |
| 本站代码 | [本专题代码示例](robustness.html#code) | 生成函数与 Newman–Ziff、四种攻击与 R 指标、攻击阈值方程、Motter–Lai 级联、Watts 级联窗口与分支过程、相互依存网络、保度换边优化、玩具代谢网络的合成致死、模块网络的虚拟损伤 |

> 提示：Barabási《Network Science》在线版需加载境外脚本，在中国大陆可能无法正常显示。

## 开放问题 {#questions}

1. 选择一个你熟悉的生物医学网络（如某病原体的蛋白相互作用网络、某代谢通路、某个体的结构连接组）。“随机失效”和“蓄意攻击”在这个系统中分别对应什么真实过程？你会用哪种鲁棒性指标（$f_c$、$R$、全局效率还是功能指标），为什么？
2. 合成致死揭示了冗余的“背面”：冗余使单个扰动无害，也制造了成对的弱点。设计一个分析流程：从人类蛋白相互作用网络或代谢模型出发，预测某种抑癌基因缺失肿瘤的合成致死候选靶点，并说明需要哪些独立数据（如 CRISPR 筛选、患者生存数据）来验证。
3. 两个网络之间何时可以被视为“相互依存”？以脑的结构连接与功能连接、或细胞的信号网络与代谢网络为例，讨论依赖边的生物学含义，以及一级相变的预测在该系统中是否可信。
