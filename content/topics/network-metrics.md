---
id: network-metrics
title: 网络结构指标与随机图
en: Network metrics and random graphs
domain: theory
legacy: L02
summary: 用度、路径、聚集、效率与中心性刻画网络结构，并以 Erdős–Rényi 随机图为零模型判断真实网络的特殊之处。
keywords: [度分布, 密度, 最短路径, 直径, 广度优先搜索, 聚集系数, 全局效率, 局部效率, 加权网络, 中心性, 介数中心性, 特征向量中心性, PageRank, k 核, 连通分支, ER 随机网络, 巨连通分支, 相变, 小世界性]
synonyms: [度, degree, 入度, in-degree, 出度, out-degree, 强度, strength, 节点强度, node strength, 平均度, average degree, 密度, density, 度分布, degree distribution, 重尾分布, heavy-tailed distribution, 枢纽, hub, 互补累积分布, CCDF, 自然截断, natural cutoff, 最短路径, shortest path, 测地距离, geodesic distance, 途径, walk, 离心率, eccentricity, 半径, radius, 直径, diameter, 平均路径长度, average path length, 特征路径长度, characteristic path length, 全局效率, global efficiency, 局部效率, local efficiency, 节点效率, nodal efficiency, 广度优先搜索, breadth-first search, BFS, Dijkstra, Floyd–Warshall, 连通分支, connected component, 巨连通分支, giant component, GCC, LCC, 强连通分支, strongly connected component, 弱连通分支, weakly connected component, 聚集系数, clustering coefficient, 传递性, transitivity, 全局聚集系数, 三元组, triplet, 三角形, triangle, 加权聚集系数, weighted clustering, Onnela, Barrat, 权重–长度转换, weight-to-length, 中心性, centrality, 度中心性, degree centrality, 接近中心性, closeness centrality, 调和中心性, harmonic centrality, 介数中心性, betweenness centrality, 瓶颈, bottleneck, Brandes 算法, 边介数, edge betweenness, 特征向量中心性, eigenvector centrality, Katz 中心性, Katz centrality, PageRank, 阻尼因子, damping factor, 随机游走, random walk, HITS, 权威值, authority, 枢纽值, hub score, 子图中心性, subgraph centrality, k 核, k-core, k 壳, k-shell, 核数, coreness, 核分解, core decomposition, s 核, s-core, 中心化, centralization, ER 随机图, Erdős–Rényi, G(N,p), G(N,M), 随机网络, random graph, 泊松分布, Poisson distribution, 相变, phase transition, 临界点, critical point, 亚临界, subcritical, 超临界, supercritical, 连通区, connected regime, 分支大小分布, component size distribution, 临界指数, critical exponent, 渗流, percolation, 小世界性, small-world property, 超小世界, ultra-small world, 零模型, null model]
demos: [graph_matrix, er]
reviewed: 2026-11-15
---

## 概述 {#overview}

把一个系统写成图和邻接矩阵（见[复杂系统与网络的数学表示](network-basics.html)）之后，下一步是描述它的结构。一张有上万个节点的网络画出来只是一团“毛线球”，肉眼看不出任何规律，需要定量的结构指标。本专题按“从局部到全局、从无权到加权、从描述到比较”的顺序整理这些指标：

- **三把基本尺子**：度分布（每个节点有多少连接、这些连接如何分配）、路径长度（信息或影响要走多远）、聚集系数（邻居之间是否彼此相连），以及与之相关的连通分支；
- **效率**：用距离的倒数刻画整合与局部容错，适用于不连通网络；
- **加权网络**：强度、加权聚集系数与加权路径，以及“权重如何转换为长度”这一常被忽视的步骤；
- **中心性家族**：度、接近、介数、特征向量、Katz、PageRank、HITS 与 k 核，各自隐含不同的“流动”假设；
- **随机网络**：Erdős–Rényi（ER）模型的度分布、最大与最小度、四个演化区间与临界现象、平均距离的对数律。

有了尺子还需要一个参照物，否则无法判断一个数值是“大”还是“小”。ER 随机网络就是最基本的参照物，即零模型。把真实网络与 ER 网络比较，会得到两个“反常”：聚集系数远高于随机预期，度分布的尾巴远比泊松分布长。这两个反常正是[小世界与无标度网络模型](network-models.html)要解释的对象；介于全局与局部之间的社团尺度在[社团结构与社区发现](community-structure.html)中讨论；度–度相关（同配性）与富人俱乐部等高阶统计在[度相关性与网络结构的高阶统计](degree-correlations.html)中讨论。

本专题的定义与 Barabási《Network Science》第 2–3 章、Newman《Networks》“Measures and metrics”一章以及 Brain Connectivity Toolbox（BCT）的指标文档保持一致；符号约定：$N$ 为节点数，$M$ 为边数，$A$ 为邻接矩阵。有向网络中 $A_{ij}=1$ 表示存在边 $i\to j$。

## 度、平均度与密度 {#degree-density}

::: {.callout-def}
**度**（degree）：节点 $i$ 连接的边数，$k_i = \sum_j A_{ij}$。有向网络区分**入度** $k_i^{\text{in}} = \sum_j A_{ji}$ 和**出度** $k_i^{\text{out}} = \sum_j A_{ij}$；加权网络中把边权相加得到**强度**（strength）$s_i = \sum_j w_{ij}$（见[加权网络的指标](network-metrics.weighted-networks.html)）。
:::

由“每条边贡献两个度”（握手定理 $\sum_i k_i = 2M$）可得**平均度**：

$$
\langle k \rangle = \frac{1}{N}\sum_i k_i = \frac{2M}{N}.
$$

有向网络中每条边贡献一个入度和一个出度，故 $\langle k^{\text{in}}\rangle=\langle k^{\text{out}}\rangle=M/N$。

**密度**（density）是实际边数与最大可能边数之比：

$$
\rho = \frac{M}{N(N-1)/2} = \frac{\langle k \rangle}{N-1}.
$$

有向简单图最多有 $N(N-1)$ 条边，密度为 $M/[N(N-1)]$。

真实网络几乎都很稀疏（$\langle k \rangle \ll N$）。比如 Zachary 空手道俱乐部网络 $N=34$、$M=78$，$\langle k \rangle \approx 4.6$，$\rho \approx 0.14$；而一个 2 万节点、平均度 20 的蛋白质网络，密度只有 0.001。稀疏性决定了计算策略：用边列表或稀疏矩阵存储，算法复杂度以 $N+M$ 而非 $N^2$ 衡量。

::: {.callout-warn}
密度与网络规模紧密相关：节点越多，即便平均度不变，密度也越低。比较两个规模不同的网络时，“密度高低”本身的意义有限；在脑网络研究中，常把不同被试的网络**固定在同一密度**下再比较其他指标（见[脑连接组：结构与功能连接](brain-connectome.html)）。
:::

## 度分布 {#degree-distribution}

::: {.callout-def}
**度分布**（degree distribution）$P(k)$：随机选一个节点，其度恰为 $k$ 的概率。若 $N_k$ 个节点的度为 $k$，则 $P(k) = N_k / N$。
:::

度分布刻画了“连接是如何在节点之间分配的”。两类典型形状：

- **均匀型**：大多数节点的度集中在平均值附近，分布有一个峰，远离峰值的概率迅速衰减。规则网格（所有节点度相同）和 ER 随机网络（泊松分布）属于这一类。
- **重尾型**（heavy-tailed）：大多数节点度很小，但存在少数度极大的节点（枢纽，hub），分布的“尾巴”拖得很长。社交网络、万维网、许多生物分子网络属于这一类。

### 矩与异质性

度分布的 $n$ 阶矩 $\langle k^n\rangle=\sum_k k^nP(k)$ 在后续理论中反复出现：一阶矩是平均度；二阶矩 $\langle k^2\rangle$ 决定“沿一条边走到的邻居平均有多少个其他邻居”，即**剩余度**（excess degree）均值 $\langle k^2\rangle/\langle k\rangle-1$，它控制巨连通分支的出现、传播阈值和平均距离。常用**异质性指数** $\kappa=\langle k^2\rangle/\langle k\rangle$ 或变异系数 $\sigma_k/\langle k\rangle$ 概括度分布的宽窄：泊松分布 $\sigma_k/\langle k\rangle=1/\sqrt{\langle k\rangle}$，平均度越大越“均匀”；重尾分布的 $\langle k^2\rangle$ 随网络规模增大而增大（见[无标度网络](network-models.scale-free.html)）。

### 判断重尾的实用做法

1. 看**最大度与平均度之比**。均匀型网络中二者相差几倍；重尾型网络可达几十到上百倍。对 ER 网络可以算出“期望最大度”（**自然截断**，见[ER 随机网络](network-metrics.er-random-graph.html)），它只比平均度高出若干个标准差；
2. 在**双对数坐标**下画分布。重尾分布在双对数图上衰减缓慢，接近一条下倾的直线；均匀型分布则会急剧“掉崖”；
3. 画**互补累积分布**（CCDF）$P(K \ge k)$，它比直方图更平滑，尾部不需要分箱（详见[幂律判断](network-models.identification.html)）。

::: {.callout-bio}
**同一个平均度，完全不同的意义。**设两个蛋白质网络平均度都是 8。一个网络中所有蛋白都有 5–12 个伙伴；另一个网络中多数蛋白只有 1–3 个伙伴，少数蛋白有几百个伙伴。后者中，敲除一个枢纽蛋白可能影响上百个相互作用，前者则不会出现这种情况。**只报告平均度会掩盖这种差异，应该报告并展示完整的度分布。**
:::

## 路径、距离与最短路径算法 {#paths-distance}

### 路径与最短路径

**路径**（path）是一串节点，相邻节点之间都有边相连；路径包含的边数称为**路径长度**。两个节点之间的**距离**（distance）$d_{ij}$ 是它们之间最短路径的长度，也叫测地距离（geodesic distance）。若两点之间不存在路径，约定 $d_{ij} = \infty$。有向网络中一般 $d_{ij}\ne d_{ji}$，甚至可能一个有限、一个无穷。

邻接矩阵的幂有一个漂亮的性质：$(A^h)_{ij}$ 等于从 $i$ 到 $j$ 长度恰为 $h$ 的**途径**（walk，允许重复经过节点和边）条数。因此 $d_{ij}$ 就是使 $(A^h)_{ij} > 0$ 的最小 $h$。途径计数也是[谱类中心性](network-metrics.spectral-centrality.html)的出发点。

### 离心率、直径与平均路径长度

::: {.callout-def}
**离心率**（eccentricity）：$\varepsilon_i=\max_j d_{ij}$，节点 $i$ 到最远节点的距离。**半径**为 $\min_i\varepsilon_i$，**直径**（diameter）为 $D = \max_i\varepsilon_i=\max_{i,j} d_{ij}$。
**平均路径长度**（average path length；脑网络文献中常称特征路径长度，characteristic path length）：所有节点对之间距离的平均值，
$$
L = \frac{1}{N(N-1)}\sum_{i \ne j} d_{ij}.
$$
:::

直径对单个“偏远”节点很敏感，平均路径长度更能反映典型情况。网络不连通时 $L$ 为无穷大，常见处理有两种：只在**最大连通分支**上计算 $L$；或改用**全局效率**（见[全局效率与局部效率](network-metrics.efficiency.html)），不连通的节点对贡献 0。后者在脑网络研究中很常用。

### 广度优先搜索

怎样计算距离？**广度优先搜索**（breadth-first search，BFS）是最基本的算法：

1. 把源点 $s$ 标记为距离 0，放入队列；
2. 从队列取出一个节点 $v$，把它尚未标记的邻居标记为 $d(v)+1$，放入队列尾部；
3. 重复第 2 步直到队列为空。

BFS 像水波一样从源点“一层一层”向外扩散，每一层的节点距离相同。它的计算量与 $N+M$ 成正比，在稀疏网络上非常快。对每个节点各做一次 BFS，就得到所有节点对之间的距离。加权网络的最短路径要用 Dijkstra 算法（单源，要求长度非负）或 Floyd–Warshall 算法（全点对，$O(N^3)$，适合几百个节点的稠密脑网络），并且要先想清楚“距离”与“权重”的关系：相关系数越大表示连接越强，转换成长度时通常取倒数或 $-\log w$（见[加权网络的指标](network-metrics.weighted-networks.html)）。

::: {.callout-def}
**算例**：路径图 1–2–3–4 共有 6 个节点对，距离为 1、1、1、2、2、3，故 $L=10/6\approx1.67$，直径 $D=3$，端点的离心率为 3，中间两点的离心率为 2，半径为 2。
:::

## 连通分支与巨连通分支 {#components}

无向网络中，彼此可达的节点构成一个**连通分支**（connected component）。真实网络往往包含一个规模远大于其他分支的**巨连通分支**（giant component）以及许多小碎片。有向网络中要区分**强连通分支**（任意两点双向可达）与**弱连通分支**（忽略方向后连通）。在有向网络中，最大强连通分支、能到达它的“入集”和能从它到达的“出集”组成常说的“领结”（bow-tie）结构，代谢网络和万维网都呈现这种组织。

“巨”的严格含义是**规模与 $N$ 成正比**：$N\to\infty$ 时 $N_G/N$ 趋于一个正数。对一个具体的有限网络，只能说最大分支远大于第二大分支。分支可用 BFS 或并查集在 $O(N+M)$ 时间内求出；强连通分支用 Tarjan 算法同样是线性时间。ER 网络中巨分支何时出现、小分支的大小如何分布，见[ER 网络的演化与相变](network-metrics.er-evolution.html)。

::: {.callout-warn}
从数据库下载的 PPI 网络，常常有一部分蛋白与主体不连通。报告平均路径长度时要写明：是在整个网络上用全局效率计算，还是只在最大连通分支上计算；最大连通分支包含了多少比例的节点。
:::

## 聚集系数 {#clustering}

### 局部聚集系数

“我的两个朋友之间是否也是朋友？”这个问题用**聚集系数**（clustering coefficient）来量化。

::: {.callout-def}
**局部聚集系数**：节点 $i$ 的 $k_i$ 个邻居之间实际存在的边数 $e_i$，与最大可能边数 $k_i(k_i-1)/2$ 之比：
$$
C_i = \frac{2e_i}{k_i(k_i-1)}.
$$
$C_i \in [0,1]$。$C_i=1$ 表示邻居两两相连，$C_i=0$ 表示邻居之间没有任何边。度小于 2 的节点 $C_i$ 无定义，NetworkX 中约定为 0。
:::

例：节点 $i$ 有 4 个邻居，邻居之间有 3 条边，则 $C_i = 2\times 3/(4\times 3) = 0.5$。等价地说，$e_i$ 就是包含节点 $i$ 的三角形个数，矩阵写法为 $e_i=(A^3)_{ii}/2$（从 $i$ 出发走 3 步回到 $i$ 的途径，每个三角形按两个方向各计一次）。全网三角形个数为 $\operatorname{tr}(A^3)/6$。

### 网络层面的两种定义

- **平均聚集系数**：$C = \frac{1}{N}\sum_i C_i$（Watts–Strogatz 的定义）；
- **传递性**（transitivity，也称全局聚集系数）：$T = \dfrac{3 \times \text{三角形个数}}{\text{连通三元组个数}}$，其中“连通三元组”指以某节点为中心、两条边构成的“开口路径”，个数为 $\sum_i k_i(k_i-1)/2$。

两者通常数值接近但并不相等：平均聚集系数中每个节点权重相同，低度节点（$C_i$ 容易很高）影响较大；传递性相当于按 $k_i(k_i-1)$ 加权，高度节点影响较大。空手道网络的 $C\approx0.57$，而 $T\approx0.26$，相差一倍以上。**写论文时要说明用的是哪一种。**（Barabási《Network Science》第 2 章进阶专题 2.A 专门讨论了两者的差别。）

### 聚集系数与度的关系

在许多真实网络中，$C(k)$（度为 $k$ 的节点的平均聚集系数）随 $k$ 增大而下降，近似 $C(k)\sim k^{-1}$：低度节点处于紧密的小团体中，枢纽则连接着许多彼此不相连的团体。这种模式被认为是**层次模块化**结构的信号（见[社团结构与社区发现](community-structure.validation.html)）。ER 网络中 $C(k)=p$ 与 $k$ 无关，可作对照。

## 全局效率与局部效率 {#efficiency}

### 定义

Latora 与 Marchiori（2001）把“效率”定义为距离的倒数：两点越近，交换信息越“高效”；不可达时效率为 0。

::: {.callout-def}
**全局效率**（global efficiency）：
$$
E_{\text{glob}}=\frac{1}{N(N-1)}\sum_{i\ne j}\frac{1}{d_{ij}}.
$$
**节点效率**（nodal efficiency）$E_i=\frac{1}{N-1}\sum_{j\ne i}1/d_{ij}$，即下文的调和中心性，$E_{\text{glob}}$ 是它的平均。
**局部效率**（local efficiency）：设 $G_i$ 为节点 $i$ 的邻居（不含 $i$）诱导的子图，
$$
E_{\text{loc}}(i)=E_{\text{glob}}(G_i)=\frac{1}{k_i(k_i-1)}\sum_{j\ne h\in G_i}\frac{1}{d_{jh}^{(G_i)}},\qquad E_{\text{loc}}=\frac1N\sum_iE_{\text{loc}}(i),
$$
其中 $d_{jh}^{(G_i)}$ 是只经过 $i$ 的邻居的最短路径长度。
:::

### 与 $L$ 和 $C$ 的关系

- $E_{\text{glob}}$ 是距离的**调和平均**的倒数，$L$ 是距离的**算术平均**。由于调和平均不大于算术平均，连通网络中 $E_{\text{glob}}\ge 1/L$，二者只在所有距离相等时相同。算例：路径图 1–2–3–4 的 $L=1.67$，$1/L=0.60$，而 $E_{\text{glob}}=(3\cdot1+2\cdot\tfrac12+\tfrac13)/6\approx0.72$。
- $E_{\text{loc}}(i)$ 回答“去掉 $i$ 之后，它的邻居之间还能多容易地互相到达”，可看作局部容错能力。若邻居子图中只有直接相连和不可达两种情况，$E_{\text{loc}}(i)=C_i$；邻居之间存在 2 步、3 步路径时，$E_{\text{loc}}(i)>C_i$。空手道网络中 $E_{\text{loc}}\approx0.65$，略高于 $C\approx0.57$。
- Latora 与 Marchiori 据此把小世界性重新表述为“全局效率与局部效率都高”，这一表述不依赖网络连通，也可直接用于加权网络。

### 加权与适用条件

加权网络中把 $d_{ij}$ 换成加权最短路径长度即可（BCT 的 `efficiency_wei`）。加权局部效率有多种推广方式（例如三角形各边权重如何组合），不同软件、甚至同一软件的不同版本给出的数值可能不同，报告时应注明所用定义、软件与版本。

::: {.callout-warn}
效率指标隐含“信息沿最短路径传递”的假设。在神经系统中，信号是否真正沿全局最短路径路由并无定论；BCT 因此还提供了基于随机游走的扩散效率（平均首达时间的倒数）等替代指标。把 $E_{\text{glob}}$ 称为“整合能力”时，应把它理解为对拓扑的描述，而不是对信息传递过程的测量。
:::

## 加权网络的指标 {#weighted-networks}

生物医学网络大多带权：功能连接的相关系数、纤维束的条数或各向异性分数、共表达强度、STRING 的置信分数。二值化会丢失信息，并引入阈值选择问题；直接在加权网络上定义指标是另一条路线。

### 强度与强度–度关系

::: {.callout-def}
**强度**（strength）：$s_i=\sum_jw_{ij}$。有向网络区分入强度与出强度。
:::

若边权与端点度无关，则 $\langle s\,|\,k\rangle\approx\langle w\rangle k$。Barrat 等（2004）在若干真实网络中观察到 $s(k)\sim k^{\beta}$，$\beta>1$ 表示高度节点的边也更“重”。空手道网络中度与强度的相关系数约 0.98，强度排序与度排序的前五名完全相同；但在功能连接这类几乎全连通的加权网络中，度失去意义，强度成为主要的“度”类指标。

### 加权聚集系数

把三角形的“强弱”计入聚集系数有多种方式，常用两种：

$$
C_i^{\text{O}}=\frac{1}{k_i(k_i-1)}\sum_{j\ne h}\left(\hat w_{ij}\hat w_{ih}\hat w_{jh}\right)^{1/3},\qquad
C_i^{\text{B}}=\frac{1}{s_i(k_i-1)}\sum_{j\ne h}\frac{w_{ij}+w_{ih}}{2}\,a_{ij}a_{ih}a_{jh},
$$

求和遍历 $i$ 的有序邻居对。$C^{\text{O}}$ 由 Onnela 等（2005）提出，$\hat w=w/\max w$，用三角形三条边权重的几何平均衡量“三角形强度”，是 NetworkX 与 BCT（`clustering_coef_wu`）的默认加权定义；$C^{\text{B}}$ 由 Barrat 等（2004）提出，只看 $i$ 自己的两条边，衡量“$i$ 的强连接是否落在三角形里”。所有权重相等时，两者都退化为无权 $C_i$。

::: {.callout-def}
**算例**：节点 $i$ 连向 $j$、$h$、$l$，权重分别为 4、2、2；$j$–$h$ 之间有一条权重为 1 的边，最大权重为 4。无权 $C_i=2\cdot1/(3\cdot2)=0.33$。Onnela：唯一三角形的强度 $(1\times0.5\times0.25)^{1/3}=0.5$，有序对计两次，$C_i^{\text{O}}=2\times0.5/6\approx0.17$，因为第三条边很弱而低于无权值。Barrat：$s_i=8$，$C_i^{\text{B}}=2\times\frac{4+2}{2}/(8\times2)=0.375$，因为 $i$ 的最强连接参与了三角形而高于无权值。
:::

两者回答不同的问题，数值可能朝相反方向偏离无权值。Onnela 定义对最大权重敏感：加入一条极端大的边会压低所有节点的 $C^{\text{O}}$。

### 加权路径：先把权重变成长度

最短路径算法把边属性当作**长度**（越大越远），而多数生物医学网络的权重是**强度**（越大越近）。必须先转换：$\ell_{ij}=1/w_{ij}$、$\ell_{ij}=-\log w_{ij}$（$w\in(0,1]$，如概率或置信度，路径长度对应概率乘积的负对数）或 $\ell_{ij}=1-w_{ij}$。转换方式没有唯一正确答案，结果会随之变化，应作为敏感性分析的一部分。代码示例中，空手道网络节点 0 到 33 的正确最短路径（$\ell=1/w$）经过强度为 5、5、4 的三条边；若误把强度当长度，算法会选择强度为 2、1 的两条最弱的边。

Opsahl 等（2010）用一个参数 $\alpha$ 在“只看边数”和“只看权重”之间插值：广义度 $k_i^{1-\alpha}s_i^{\alpha}$，广义长度 $\ell_{ij}=w_{ij}^{-\alpha}$。$\alpha=0$ 回到无权指标，$\alpha=1$ 为纯加权指标。

::: {.callout-warn}
**负权重**（如偏相关网络中的负边）不能直接用于最短路径（Dijkstra 要求非负长度），也会让强度正负抵消。常见做法是分别分析正、负子网络，或使用符号专用的定义（BCT 的 `clustering_coef_wu_sign`；症状网络中的预期影响，见[症状中心性及其解释](symptom-networks.centrality.html)）。直接取绝对值会把“抑制”与“促进”混为一谈。
:::

## 中心性：度、接近与介数 {#centrality}

“哪个节点最重要？”没有唯一答案。**中心性**（centrality）是一族把节点按某种“重要性”排序的指标，每一种都对应一个关于网络上“流动什么、怎样流动”的隐含模型。本页介绍基于局部连接与最短路径的三种，[谱类中心性](network-metrics.spectral-centrality.html)介绍基于途径与随机游走的几种，[k 核](network-metrics.k-core.html)介绍基于“嵌入深度”的指标，[中心性的选择与解释](network-metrics.centrality-choice.html)讨论如何选择。

### 度中心性

$$
C_D(i)=\frac{k_i}{N-1}.
$$

最简单、最稳健、计算最快（$O(M)$），只反映直接邻居。它假设影响只通过一步接触产生，例如直接的物理相互作用或直接接触传播的初期。

### 接近中心性与调和中心性

::: {.callout-def}
**接近中心性**（closeness centrality）：到其他所有节点平均距离的倒数，
$$
C_C(i)=\frac{N-1}{\sum_{j\ne i}d_{ij}}.
$$
**调和中心性**（harmonic centrality）：距离倒数的平均，
$$
C_H(i)=\frac{1}{N-1}\sum_{j\ne i}\frac{1}{d_{ij}}.
$$
:::

接近中心性在不连通网络中失效（只要有一个 $d_{ij}=\infty$，$C_C(i)=0$）。NetworkX 对不连通网络采用 Wasserman–Faust 修正：只对可达节点求平均，再乘以可达比例。调和中心性天然处理不可达节点，Boldi 与 Vigna（2014）从公理化角度论证它比接近中心性更合理。网络平均的调和中心性就是全局效率。

接近类指标的数值范围通常很窄：小世界网络中所有节点的平均距离都在 $\ln N$ 附近，节点之间差别不大，排序容易被微小的结构变动打乱。

### 介数中心性

::: {.callout-def}
**介数中心性**（betweenness centrality；Freeman 1977）：
$$
C_B(i)=\sum_{s\ne i\ne t}\frac{\sigma_{st}(i)}{\sigma_{st}},
$$
$\sigma_{st}$ 是 $s$ 到 $t$ 的最短路径条数，$\sigma_{st}(i)$ 是其中经过 $i$ 的条数。无向网络中对无序对 $\{s,t\}$ 求和；归一化时除以 $(N-1)(N-2)/2$。
:::

介数大的节点是**瓶颈**（bottleneck）或“桥”：大量最短路径依赖它。它与度相关但不等价，一个度很低的节点只要连接两个大社团，介数就可能很高。把求和对象从节点换成边，就得到用于 Girvan–Newman 社团发现的**边介数**（见[Girvan–Newman 算法与边介数](community-structure.girvan-newman.html)）。

::: {.callout-def}
**算例**：(1) 星形图（1 个中心、4 个叶子）：任意两片叶子之间唯一的最短路径都经过中心，中心的介数为 $\binom42=6$，归一化后为 $6/6=1$；叶子到中心距离 1、到其他叶子距离 2，接近中心性为 $4/(1+3\times2)=4/7\approx0.57$。(2) 路径图 1–2–3–4–5：节点 3 位于 $\{1,4\},\{1,5\},\{2,4\},\{2,5\}$ 四对之间，介数为 4；节点 2 位于 $\{1,3\},\{1,4\},\{1,5\}$ 之间，介数为 3；端点为 0。
:::

**计算**：逐对枚举最短路径的代价过高。Brandes（2001）算法对每个源点做一次 BFS，同时记录最短路径条数，再按距离由远及近回溯累加“依赖度”，总代价在无权网络中为 $O(NM)$，加权网络中为 $O(NM+N^2\log N)$（推导见[数学推导与算法](network-metrics.derivations.html)）。对几十万节点的网络，可随机抽取部分源点近似（NetworkX 的参数 `k`）。

## 谱类中心性：特征向量、Katz、PageRank 与 HITS {#spectral-centrality}

度中心性只数一步邻居。一个自然的推广是：**被重要节点连接的节点更重要**。这一递归思想把中心性写成邻接矩阵的特征向量或线性方程的解，统称谱类中心性。它们的共同数学基础是：$(A^t)_{ij}$ 计数长度为 $t$ 的途径，各种谱类中心性就是对不同长度的途径按不同方式加权求和。

### 特征向量中心性

::: {.callout-def}
**特征向量中心性**（eigenvector centrality；Bonacich 1987 系统化）：节点得分正比于邻居得分之和，
$$
x_i=\frac{1}{\lambda_1}\sum_jA_{ij}x_j,\qquad A\mathbf x=\lambda_1\mathbf x,
$$
取最大特征值 $\lambda_1$ 对应的特征向量。
:::

对连通无向网络，Perron–Frobenius 定理保证 $\lambda_1$ 是单重的、对应特征向量所有分量为正，因此排名唯一。从任意正初值出发做**幂迭代** $\mathbf x\leftarrow A\mathbf x/\|A\mathbf x\|$，结果收敛到 $\mathbf x$，这说明特征向量中心性就是“很长的途径从哪里出发最多”。收敛速度由 $|\lambda_2/\lambda_1|$ 决定。

**算例**：星形图（中心 + 4 叶）的 $\lambda_1=\sqrt4=2$；设叶子得分为 $x$、中心为 $y$，则 $2y=4x$、$2x=y$，中心与叶子之比为 $\sqrt{N-1}=2$。

两个局限：(1) **有向网络**中，只有能被强连通核心“到达”的节点得分为正，没有入边或只位于无环部分的节点得分为 0（代码示例中，不在环上的 3 个节点得分全为 0）；(2) 在含有极大枢纽的网络中，特征向量可能**局域化**在枢纽及其邻居上，其他节点得分几乎为 0、无法区分（Martin、Zhang 与 Newman 2014）。

### Katz 中心性

Katz（1953）给每个节点一个“免费”的基础得分 $\beta$，并让长途径的贡献按 $\alpha$ 衰减：

$$
x_i=\alpha\sum_jA_{ji}x_j+\beta
\quad\Longrightarrow\quad
\mathbf x=\beta\,(I-\alpha A^{\top})^{-1}\mathbf 1=\beta\sum_{t=0}^{\infty}\alpha^t(A^{\top})^t\mathbf 1 .
$$

级数收敛要求 $0<\alpha<1/\lambda_1$。$\alpha\to0$ 时排序趋于（入）度，$\alpha\to1/\lambda_1$ 时趋于特征向量中心性，因此 Katz 中心性是二者之间的连续插值，并解决了有向无环部分得分为 0 的问题。$\alpha$ 的选择会改变排序，常取 $1/\lambda_1$ 的某个比例并报告敏感性。

### PageRank

Katz 中心性中，一个出度很大的节点会把它的“全部”得分传给每个邻居。PageRank（Brin 与 Page 1998）让每个节点把得分**按出度平分**给邻居，并以概率 $1-d$ 随机跳转到任意节点：

$$
x_i=d\sum_j\frac{A_{ji}}{k_j^{\text{out}}}x_j+\frac{1-d}{N}.
$$

它就是“随机冲浪者”马尔可夫链的平稳分布：以概率 $d$（阻尼因子，常取 0.85）沿随机一条出边走，以概率 $1-d$ 随机跳到任意节点。随机跳转保证了链的不可约与非周期，平稳分布唯一。出度为 0 的“悬挂节点”需要特殊处理，通常让它以均匀概率跳转。

::: {.callout-warn}
在**无向连通网络**上，若 $d=1$（无随机跳转），随机游走的平稳分布恰好是 $k_i/2M$，PageRank 退化为度；$d<1$ 时二者也高度相关（空手道网络中 Spearman 秩相关约 0.98）。因此在无向 PPI 或共表达网络上“用 PageRank 找关键基因”，所得排名与度相差不大，额外信息主要来自所加的先验（个性化跳转向量）。PageRank 的真正优势在有向网络，或跳转向量携带外部信息（种子基因、表达变化）的场合，例如 GeneRank（Morrison 等 2005）和网络传播类的疾病基因优先排序。
:::

### HITS：枢纽值与权威值

在有向网络中，“指向很多重要节点”和“被很多重要节点指向”是两种不同的重要性。Kleinberg（1999）的 HITS 算法为每个节点定义两个得分：**权威值**（authority）$a_i$ 是指向它的枢纽值之和，**枢纽值**（hub score）$h_i$ 是它指向的权威值之和：

$$
\mathbf a=A^{\top}\mathbf h,\quad \mathbf h=A\mathbf a
\quad\Longrightarrow\quad
A^{\top}A\,\mathbf a=\lambda\mathbf a,\quad AA^{\top}\mathbf h=\lambda\mathbf h .
$$

$A^{\top}A$ 的元素是两个节点共同的“上游”数（共引），$AA^{\top}$ 是共同的“下游”数（共被引）。在转录调控网络中，调控大量重要靶基因的转录因子枢纽值高，被多个关键转录因子共同调控的基因权威值高。

### 子图中心性

Estrada 与 Rodríguez-Velázquez（2005）的**子图中心性** $SC_i=(e^{A})_{ii}=\sum_t (A^t)_{ii}/t!$ 计数从 $i$ 出发又回到 $i$ 的闭合途径，长度为 $t$ 的途径以 $1/t!$ 加权。它衡量节点参与局部稠密子结构（三角形、小团）的程度，BCT 中为 `subgraph_centrality`。

## k 核分解与核数 {#k-core}

::: {.callout-def}
**k 核**（k-core；Seidman 1983）：图中所有节点度都不小于 $k$ 的极大子图。节点的**核数**（coreness，或 k-shell 指数）$k_s(i)$ 是包含它的最大 k 核的 $k$ 值；核数恰为 $k$ 的节点组成第 $k$ **壳**（k-shell）。
:::

**算法（剥洋葱）**：反复删除当前度小于 $k$ 的节点（删除后邻居的度会减小，可能引发连锁删除），剩下的就是 k 核；令 $k=1,2,\dots$ 依次剥离，得到每个节点的核数。按当前度排序的桶实现（Batagelj 与 Zaversnik 2003）总代价 $O(M)$，适合百万级网络。

**算例**：一个三角形 $\{a,b,c\}$ 加一个只连在 $a$ 上的节点 $d$：$d$ 的度为 1，先被剥离，核数为 1；剩下的三角形每个节点度为 2，核数为 2。注意 $a$ 的度为 3，但核数只有 2，核数衡量的是节点所处“核心”的稠密程度，而不只是自己的度。空手道网络的最大核数为 4，最内层的 4 核包含 10 个节点（含两位核心人物 0 与 33）。

**性质与用途**：

- 核数是**粗粒度**的排序，大量节点并列，适合分层而不是精细排名；
- 核数对“位于边缘的枢纽”有区分力：一个连接着许多叶子的高度节点，核数可能很低。Kitsak 等（2010）在几个社会网络上做 SIR 模拟，发现单个传播源最终感染范围更好地由核数预测，而不是度或介数（论文精读：[Kitsak 2010](paper-kitsak2010_spreaders.html)；传播背景见[网络上的传播与免疫](spreading.html)）；
- 加权推广为 **s 核**（所有节点强度 $\ge s$ 的极大子图，BCT 的 `score_wu`）；
- ER 网络中 $k\ge3$ 的 k 核以**不连续**方式突然出现（Pittel、Spencer 与 Wormald 1996），这与巨分支的连续相变形成对照；不同度分布下 k 核的组织见 Dorogovtsev 等（2006）。

::: {.callout-bio}
Wuchty 与 Almaas（2005, *Proteomics*）对酵母 PPI 网络做 k 核分解，发现从外层到最内层的核，蛋白为必需基因和进化保守的概率依次升高，并且这一结论对相互作用数据中的假阳性、假阴性较为稳健。它为[致死性与中心性](molecular-networks.centrality-lethality.html)的争论提供了另一个视角：起作用的可能不是“度大”，而是“处在网络稠密核心”。
:::

## 中心性的选择与解释 {#centrality-choice}

### 一张对照表

| 指标 | 衡量什么 | 隐含的流动假设 | 计算代价 | 适用场景 |
|---|---|---|---|---|
| 度 / 强度 | 直接连接数 / 强度 | 一步接触 | $O(M)$ | 几乎所有场合的基线；稠密加权网络用强度 |
| 接近 / 调和 | 到全网的平均远近 | 沿最短路径、逐一传递 | $O(NM)$ | 需要快速到达全网的过程；不连通时用调和 |
| 介数 | 对最短路径的“控制” | 沿最短路径转运，不复制 | $O(NM)$ | 瓶颈、桥、连接社团的节点 |
| 特征向量 | 被重要节点连接 | 沿途径复制扩散 | $O(M)$/迭代 | 无向连通网络；影响力的长期累积 |
| Katz | 衰减加权的全部途径 | 沿途径扩散并衰减 | 解线性方程 | 有向网络，需要介于度与特征向量之间 |
| PageRank | 随机游走停留概率 | 沿出边随机游走 + 跳转 | $O(M)$/迭代 | 有向网络；带先验的个性化排序 |
| HITS | 枢纽 / 权威两种角色 | 共引与共被引 | $O(M)$/迭代 | 调控网络、引用网络等有向网络 |
| 核数 | 所处核心的深度 | 无显式流动，衡量嵌入 | $O(M)$ | 分层、识别稠密核心与边缘枢纽 |

Borgatti（2005）把这种对应关系系统化：网络上的“流”可按**路线**（最短路径、不重复节点的路径、可重复的途径）与**传递方式**（转运、串行复制、并行复制）分类，每种中心性只对与其假设匹配的流有清晰解释。例如介数假设东西沿最短路径整体搬运，对包裹递送合适，对并行扩散的信息或感染就不太合适。

### 选择与解释的要点

1. **先问研究问题，再选指标。**“哪个蛋白的缺失最可能破坏复合物”与“哪个脑区最可能传递信号”对应不同的流动模型；不要把所有中心性都算一遍再挑结果最好看的。
2. **指标之间高度相关。**空手道网络中各指标与度的 Spearman 秩相关在 0.78–0.98 之间。若一个复杂指标与度的相关接近 1，它提供的额外信息有限；报告复杂指标时最好同时报告度，或报告“控制度之后”的效应（如回归残差、保度零模型下的 z 分数）。
3. **网络层面的中心化。**Freeman（1978）定义中心化 $\sum_i[C(i^*)-C(i)]$ 除以同规模星形图的对应值，衡量“权力”是否集中在少数节点上；星形图为 1，规则图为 0。
4. **方向与权重要与定义一致。**有向网络用入度类还是出度类、加权网络如何把权重转为长度（见[加权网络的指标](network-metrics.weighted-networks.html)），都会改变排序。
5. **排序的稳定性。**数据的抽样误差、缺失边和阈值都会扰动排序。可用自助法或删节点子抽样估计排名的稳定性（症状网络中的 CS 系数见[抽样不确定性](symptom-networks.stability.html)）。
6. **高中心性不等于因果重要。**中心性是描述性统计。把中心节点解释为“驱动者”或“干预靶点”需要额外证据（扰动实验、纵向数据或可控性分析，见[网络可控性与稳定性](controllability.html)）。

::: {.callout-warn}
在偏相关或相关网络（如症状网络、功能连接网络）中，边表示统计依赖，不表示有东西在“流动”。Bringmann 等（2019）指出，接近与介数在这类网络中缺乏清晰含义且估计不稳定，多数研究现在主要报告强度或预期影响（见[症状中心性及其解释](symptom-networks.centrality.html)）。
:::

## ER 随机网络 {#er-random-graph}

### 模型定义

::: {.callout-def}
**Erdős–Rényi 随机网络**：$G(N,p)$ 模型中，$N$ 个节点的每一对以概率 $p$ 独立连边；$G(N,M)$ 模型中，从所有可能的边中均匀随机地选出 $M$ 条。$N$ 很大时两者性质相同。（$G(N,p)$ 也常归于 Gilbert 1959。）
:::

注意 $N$ 和 $p$ 并不唯一决定一张图：同样的参数，每次生成的网络都不同。我们研究的是这一类网络的**统计性质**，以及当 $N\to\infty$ 时“几乎必然”成立的性质。

**边数**：$\binom N2$ 个节点对各以概率 $p$ 连边，故边数服从二项分布，期望 $\langle M\rangle=p\,N(N-1)/2$，平均度 $\langle k\rangle=2\langle M\rangle/N=p(N-1)$。

### 度分布

每个节点与其余 $N-1$ 个节点各以概率 $p$ 相连，因此度服从二项分布，在 $N\to\infty$、$\langle k\rangle$ 固定时趋于泊松分布

$$
P(k) = \binom{N-1}{k} p^k (1-p)^{N-1-k} \;\xrightarrow{N\to\infty,\ \langle k\rangle \text{固定}}\; e^{-\langle k\rangle}\frac{\langle k\rangle^k}{k!},
$$

其中 $\langle k\rangle = p(N-1)$。泊松分布的方差等于均值，标准差为 $\sqrt{\langle k\rangle}$，相对宽度 $\sigma_k/\langle k\rangle=1/\sqrt{\langle k\rangle}$：平均度越大，节点的度越集中在平均值附近，几乎不存在枢纽。

### 最大度与最小度

要求“度不小于 $k_{\max}$ 的节点期望只有一个”：$N\,P(K\ge k_{\max})\approx1$；同理 $N\,P(K\le k_{\min})\approx1$。Barabási 书中以 $N=10^9$、$\langle k\rangle=1000$（粗略对应全球熟人网络）为例：数值求解得 $k_{\max}$ 约 $1.2\times10^3$（书中用级数近似得 1185）、$k_{\min}\approx816$。也就是说，即使在十亿规模的随机社会中，“最受欢迎的人”的朋友也只比平均多约 20%。真实社交网络中存在朋友数比平均多几个数量级的人，这本身就否定了随机网络模型。

### 聚集系数

节点 $i$ 的任意两个邻居之间是否连边，与其他边无关，概率仍为 $p$，所以 $C_{\text{rand}} \approx p = \langle k\rangle/(N-1)$。在平均度固定时，$C_{\text{rand}}$ 随 $N$ 增大按 $1/N$ 趋于 0，并且 $C(k)$ 与 $k$ 无关。真实网络的平均聚集系数则大体与规模无关（Barabási 书图 3.13）。

### 平均路径长度

$L_{\text{rand}} \approx \ln N/\ln \langle k\rangle$，只随 $N$ 对数增长：即便有几十亿个节点，平均路径也只有几步到十几步。推导与修正见[小世界性与平均距离](network-metrics.small-world-distance.html)。

### 巨连通分支

逐渐增大 $p$，ER 网络会经历一个**相变**（phase transition）：$\langle k\rangle<1$ 时只有小碎片，$\langle k\rangle=1$ 时巨连通分支出现，$\langle k\rangle>\ln N$ 时整个网络几乎必然连通。巨分支所占比例 $S$ 满足 $S = 1 - e^{-\langle k\rangle S}$。四个区间的细节见[ER 网络的演化与相变](network-metrics.er-evolution.html)，各结果的推导见[数学推导与算法](network-metrics.derivations.html)。本专题页面的 ER 演示可以拖动 $p$ 观察这一过程。

## ER 网络的演化与相变 {#er-evolution}

设想从 $N$ 个孤立节点出发，不断随机加边（$p$ 从 0 增大）。直觉上最大分支应该平滑长大；实际上它在 $\langle k\rangle=1$ 处突然“出现”。这是 Erdős 与 Rényi（1960）最著名的发现。

### 四个区间

| 区间 | 条件 | 最大分支规模 $N_G$ | 结构特征 |
|---|---|---|---|
| 亚临界 | $0<\langle k\rangle<1$（$p<1/N$） | $\sim\ln N$，$N_G/N\to0$ | 许多小分支，几乎都是树；平均分支大小 $1/(1-\langle k\rangle)$ |
| 临界点 | $\langle k\rangle=1$（$p=1/N$） | $\sim N^{2/3}$，$N_G/N\to0$ | 分支大小分布为幂律 $p_s\sim s^{-3/2}$，大小悬殊的分支共存 |
| 超临界 | $1<\langle k\rangle<\ln N$ | $\approx SN$，$S=1-e^{-\langle k\rangle S}$ | 一个含环的巨分支 + 许多树状小分支和孤立节点 |
| 连通区 | $\langle k\rangle>\ln N$（$p>\ln N/N$） | $=N$ | 巨分支吸收所有节点，网络连通 |

几点说明：

- 临界点 $p_c=1/N$ 随规模增大而趋于 0：网络越大，越少的“边比例”就足以产生巨分支；但以平均度计，临界值总是 1，与 $N$ 无关。
- 超临界区与连通区的分界 $\ln N$ 随规模缓慢增长。以 $N=7\times10^9$ 的世界人口为例，$\ln N\approx22.7$：只要每人平均认识二十几个人，一个随机社会就应该完全连通。
- 连通的精确判据：令 $p=(\ln N+c)/N$，则网络连通的概率趋于 $e^{-e^{-c}}$（Erdős 与 Rényi 1959）。原因是阻碍连通的最后障碍是孤立节点，其个数近似服从均值 $Ne^{-\langle k\rangle}$ 的泊松分布。代码示例在 $N=2000$ 时验证了这一点：$\langle k\rangle=\ln N\approx7.6$ 时连通概率约 0.37，$\langle k\rangle=11$ 时约 0.97。

### 临界现象

巨分支的出现与水结冰、铁磁体在居里温度下出现磁化同属**相变**：一个**序参量**（这里是 $S$）从 0 变为正值。在临界点附近，许多量呈幂律：

- **序参量**：$\langle k\rangle$ 略大于 1 时，把 $1-e^{-\langle k\rangle S}$ 展开到 $S^2$ 项得 $S\approx2(\langle k\rangle-1)$，即 $S\sim(\langle k\rangle-1)^{\beta}$，$\beta=1$；
- **平均分支大小**（随机选一个节点，它所在小分支的大小）：$\langle s\rangle=1/[1-\langle k\rangle+\langle k\rangle S]$，亚临界时为 $1/(1-\langle k\rangle)$，在 $\langle k\rangle\to1$ 时发散，$\langle s\rangle\sim|\langle k\rangle-1|^{-\gamma}$，$\gamma=1$；
- **分支大小分布**：随机选一个节点，它属于大小为 $s$ 的（非巨）分支的概率为
$$
p_s=\frac{e^{-\langle k\rangle s}(\langle k\rangle s)^{s-1}}{s!}\;\approx\;\frac{1}{\sqrt{2\pi}}\,s^{-3/2}\,e^{-(\langle k\rangle-1)s+(s-1)\ln\langle k\rangle}.
$$
偏离临界点时指数项使大分支被指数压制；在 $\langle k\rangle=1$ 处指数项消失，$p_s\sim s^{-3/2}$。

这些指数与 Bethe 晶格（无限维）上的渗流相同，称为**平均场**指数。巨分支相变与渗流理论是同一回事：随机删除节点或边相当于把平均度调低，网络在某个临界删除比例处碎裂（见[网络鲁棒性、渗流与级联失效](robustness.html)）。同样的阈值思想也出现在[网络上的传播与免疫](spreading.html)（传播阈值）中。

::: {.callout-def}
**为什么是 1？**沿一条边走到一个新节点，它平均还有多少条“向外”的边？对泊松度分布，剩余度均值为 $\langle k^2\rangle/\langle k\rangle-1=\langle k\rangle$。若每一步平均找到的新节点少于 1 个，探索会像亚临界的分支过程一样很快灭绝；多于 1 个时有正概率无限延续，形成巨分支。一般度分布下的条件 $\langle k^2\rangle/\langle k\rangle>2$ 称为 Molloy–Reed 判据。
:::

### 真实网络处在哪个区间？

Barabási 书表 3.1 列出了几个无向网络的 $\langle k\rangle$ 与 $\ln N$：所有网络都有 $\langle k\rangle>1$，即都在超临界区之上；但多数网络的 $\langle k\rangle<\ln N$，例如书中所用的酵母蛋白相互作用网络 $N=2018$、$\langle k\rangle=2.90$、$\ln N=7.61$，只有演员合作网络（$\langle k\rangle=83.7$，$\ln N=13.5$）处在连通区。按随机网络理论，这些网络应当碎裂成许多分支，并有不少孤立节点。互联网、电网事实上是连通的，这说明真实网络的连通性并非由随机连边决定。蛋白网络确实含有许多小分支，但这部分反映的是数据不完整，而不只是拓扑规律。

## 小世界性与平均距离 {#small-world-distance}

### 推导：$\langle d\rangle\approx\ln N/\ln\langle k\rangle$

从一个节点出发，在稀疏、局部近似为树的网络中：1 步可达约 $\langle k\rangle$ 个节点，2 步约 $\langle k\rangle^2$ 个，$d$ 步以内总共

$$
N(d)\approx1+\langle k\rangle+\langle k\rangle^2+\cdots+\langle k\rangle^d=\frac{\langle k\rangle^{d+1}-1}{\langle k\rangle-1}\approx\langle k\rangle^d .
$$

可达节点数不能超过 $N$。令 $\langle k\rangle^{d_{\max}}\approx N$，得

$$
d_{\max}\approx\frac{\ln N}{\ln\langle k\rangle}.
$$

这个估计严格说是“搜索覆盖全网所需的步数”，更接近直径；但直径受少数极端路径支配，实际数据中它对**平均距离** $\langle d\rangle$ 的近似反而更好，因此小世界性通常写作 $\langle d\rangle\approx\ln N/\ln\langle k\rangle$。关键在于 $\langle d\rangle$ 与 $N$ 呈**对数关系**：$N$ 增大 10 倍，平均距离只增加 $\ln10/\ln\langle k\rangle$ 步。

### 推导中隐含的假设

1. **局部树状**：第 $d$ 层发现的节点都是“新”的。高聚类会让朋友的朋友大量重复，扩张变慢（见[小世界现象](network-models.small-world-phenomenon.html)）；
2. **分支因子等于 $\langle k\rangle$**：严格地说，第二层以后的扩张因子是剩余度均值 $\langle k^2\rangle/\langle k\rangle-1$，ER 网络中它恰好等于 $\langle k\rangle$。对任意度分布的随机网络，Newman、Strogatz 与 Watts（2001）给出 $\ell\approx\ln(N/z_1)/\ln(z_2/z_1)+1$，$z_1=\langle k\rangle$、$z_2=\langle k^2\rangle-\langle k\rangle$ 分别为一阶、二阶邻居的平均数。度分布越重尾，$z_2$ 越大，距离越短，无标度网络因此可以是“超小世界”（见[无标度网络](network-models.scale-free.html)）；
3. **有限规模**：当 $\langle k\rangle^d$ 接近 $N$ 时扩张必然放慢，粗略公式低估距离。Fronczak 等（2004）对 ER 网络得到更精确的平均距离 $\langle d\rangle\approx(\ln N-\gamma_E)/\ln\langle k\rangle+1/2$，$\gamma_E\approx0.5772$ 为欧拉常数。代码示例中 $\langle k\rangle=6$、$N=16000$ 时，模拟值 5.61，粗略公式 5.40，修正公式 5.58。Barabási 书进阶专题 3.G 还讨论了直径的修正：在临界点附近网络呈长链状的树结构，直径远大于 $\ln N/\ln\langle k\rangle$ 的预测。

### 与真实网络的对照

Barabási 书表 3.2 比较了 10 个真实网络的 $\langle d\rangle$ 与 $\ln N/\ln\langle k\rangle$，摘录几例：

| 网络 | $N$ | $\langle k\rangle$ | $\langle d\rangle$ | $d_{\max}$ | $\ln N/\ln\langle k\rangle$ |
|---|---|---|---|---|---|
| 互联网（路由器） | 192,244 | 6.34 | 6.98 | 26 | 6.58 |
| 科学合作 | 23,133 | 8.08 | 5.35 | 15 | 4.81 |
| 演员合作 | 702,388 | 83.71 | 3.91 | 14 | 3.04 |
| 大肠杆菌代谢 | 1,039 | 5.58 | 2.98 | 8 | 4.04 |
| 酵母蛋白相互作用 | 2,018 | 2.90 | 5.61 | 14 | 7.14 |
| 电网 | 4,941 | 2.67 | 18.99 | 46 | 8.66 |

对多数网络，公式给出了正确的量级，且 $\langle d\rangle$ 明显比 $d_{\max}$ 更接近公式；电网是明显的例外，空间嵌入使它的距离远长于随机预期。

## 真实网络与随机网络的比较 {#real-vs-random}

以 2006 年微软即时通信网络为例（Leskovec 与 Horvitz 2008 的分析，约 1.8 亿用户、13 亿条边，两人有过对话即连边）：

| 指标 | 真实网络 | 同规模 ER 网络 |
|---|---|---|
| 平均度 | 14.4 | 14.4（按定义相同） |
| 度分布 | 高度右偏、重尾 | 泊松，集中在 14 附近 |
| 平均路径长度 | 6.6 | $\ln N/\ln\langle k\rangle \approx 7$ |
| 聚集系数 | 0.11 | $\langle k\rangle/N \approx 8\times10^{-8}$ |

比较结果有一致也有反常：

1. **路径长度**：二者同样短。随机网络能解释“小世界”中“路径短”的那一半；
2. **聚集系数**：真实网络比随机网络高出约 6 个数量级。随机网络完全无法解释；
3. **度分布**：真实网络是重尾分布，有枢纽；随机网络没有。随机网络同样无法解释。

把本专题各页的结论汇总为逐项对照（参照 Barabási 书第 3 章小结的思路）：

| 性质 | ER 模型的预测 | 真实网络的典型情况 | 结论 |
|---|---|---|---|
| 度分布 | 泊松，$k_{\max}$ 只比 $\langle k\rangle$ 高若干个 $\sqrt{\langle k\rangle}$ | 常为重尾，存在度高出平均几十倍以上的枢纽 | 不符，需要[无标度模型](network-models.scale-free.html)等机制 |
| 连通性 | $\langle k\rangle>1$ 有巨分支；$\langle k\rangle<\ln N$ 时碎裂 | 都有巨分支；许多 $\langle k\rangle<\ln N$ 的网络仍连通 | 部分符合 |
| 平均距离 | $\ln N/\ln\langle k\rangle$ | 多数量级一致；空间网络偏长，重尾网络可更短 | 大体符合 |
| 聚集系数 | $\langle k\rangle/N$，随 $N$ 趋于 0；$C(k)$ 与 $k$ 无关 | 高出几个数量级，与 $N$ 大体无关；$C(k)$ 常随 $k$ 下降 | 不符，需要[小世界模型](network-models.watts-strogatz.html)与层次模块 |
| 度–度相关 | 无相关 | 社会网络常同配，生物与技术网络常异配 | 不符，见[度相关性](degree-correlations.html) |
| 中心性分布 | 各节点中心性相近，集中于平均值 | 少数节点占据大部分介数与 PageRank | 不符 |

::: {.callout-def}
**小世界性**（small-world property）：网络的平均路径长度与同规模随机网络相近（$L \approx L_{\text{rand}}$），而聚集系数远高于随机网络（$C \gg C_{\text{rand}}$）。小世界系数 $\sigma$、$\omega$ 等量化方法见[小世界与无标度的统计判别](network-models.identification.html)。
:::

那么，既然 ER 模型“错”了，为什么还要研究它？因为它是**零模型**（null model）：它告诉我们“如果连接完全随机，某个指标应该是多少”。真实网络与零模型的偏离，才是需要解释的、可能有生物学意义的结构。ER 模型只保留 $N$ 与 $M$，因而无法区分“由度分布引起”的性质与“超出度分布”的性质；保持度序列的随机化网络（配置模型、双边交换）是更严格的零模型，见[小世界与无标度的统计判别](network-models.identification.html)与[零模型与空模型](network-construction.null-models.html)。

## 数学推导与算法 {#derivations}

### 平均度与密度

由握手定理 $\sum_i k_i = 2M$ 立即得到 $\langle k\rangle = 2M/N$。无向简单图最多有 $N(N-1)/2$ 条边，故 $\rho = 2M/[N(N-1)] = \langle k\rangle/(N-1)$。

### ER 网络度分布的泊松极限

节点 $i$ 的度是 $N-1$ 次独立伯努利试验（成功概率 $p$）的成功次数，故 $P(k)=\binom{N-1}{k}p^k(1-p)^{N-1-k}$。令 $\lambda=\langle k\rangle=p(N-1)$ 固定、$N\to\infty$，对固定的 $k$：
$$
\binom{N-1}{k}p^k=\frac{(N-1)(N-2)\cdots(N-k)}{k!}\cdot\frac{\lambda^k}{(N-1)^k}\to\frac{\lambda^k}{k!},
$$
$$
\ln(1-p)^{N-1-k}=(N-1-k)\ln\!\left(1-\frac{\lambda}{N-1}\right)\to-\lambda ,
$$
其中用到 $\ln(1+x)\approx x$（$|x|\ll1$）。合起来得到泊松分布 $P(k)=e^{-\lambda}\lambda^k/k!$，其均值与方差都等于 $\lambda$。这一近似要求 $k\ll N$，对稀疏网络总是成立。

### 最大度与最小度

令 $k_{\max}$ 满足 $N\sum_{k\ge k_{\max}}P(k)\approx1$。泊松分布在 $k>\lambda$ 时随 $k$ 快速下降，和式由首项主导：$N e^{-\lambda}\lambda^{k_{\max}}/k_{\max}!\approx1$，可用对数与 Stirling 公式数值求解。同理 $N\sum_{k\le k_{\min}}P(k)\approx1$ 给出 $k_{\min}$。由于泊松分布在均值附近近似正态，$k_{\max}-\langle k\rangle$ 与 $\sqrt{\langle k\rangle\ln N}$ 同阶，相对偏离 $(k_{\max}-\langle k\rangle)/\langle k\rangle$ 随 $\langle k\rangle$ 增大而减小。

### ER 网络的聚集系数

节点 $i$ 有 $k_i$ 个邻居，邻居对共 $k_i(k_i-1)/2$ 个。在 $G(N,p)$ 中，每一对邻居之间是否有边与 $i$ 的连边独立，概率均为 $p$，于是 $\mathbb E[e_i \mid k_i]=p\,k_i(k_i-1)/2$，$\mathbb E[C_i]=p$。

### ER 网络的平均路径长度

见[小世界性与平均距离](network-metrics.small-world-distance.html)：由 $\langle k\rangle^{d}\approx N$ 得 $L_{\text{rand}}\approx\ln N/\ln\langle k\rangle$；有限规模修正为 $(\ln N-\gamma_E)/\ln\langle k\rangle+1/2$（Fronczak 等 2004）。

### 巨连通分支的自洽方程

**写法一（Barabási 书进阶专题 3.C）。**记 $u=1-S$ 为不在巨分支中的节点比例。节点 $i$ 经由某个特定节点 $j$ 连到巨分支失败，有两种情况：$i$、$j$ 无边（概率 $1-p$），或有边但 $j$ 不在巨分支中（概率 $pu$）。$i$ 不在巨分支中，当且仅当经由其余 $N-1$ 个节点都失败：
$$
u=(1-p+pu)^{N-1}.
$$
取对数并用 $p=\langle k\rangle/(N-1)$、$\ln(1+x)\approx x$：$\ln u\approx-(N-1)p(1-u)=-\langle k\rangle(1-u)$，即 $u=e^{-\langle k\rangle(1-u)}$，也就是
$$
S=1-e^{-\langle k\rangle S}.
$$

**写法二（生成函数）。**记 $u$ 为“沿一条边到达的节点不通向巨分支”的概率。节点不在巨分支中，当且仅当它的所有邻居都不把它连到巨分支：$1-S=\sum_k P(k)\,u^k=G_0(u)$。对泊松分布，沿边到达的邻居剩余度仍服从均值 $\langle k\rangle$ 的泊松分布，$u$ 满足同样的方程，于是 $\sum_k e^{-\langle k\rangle}\frac{\langle k\rangle^k}{k!}u^k=e^{-\langle k\rangle(1-u)}$，结果相同。这种写法可直接推广到任意度分布（配置模型）。

**临界点。**$S=0$ 总是一个解。非零解存在的条件是右端函数在 $S=0$ 处的斜率大于 1：$\frac{d}{dS}\big(1-e^{-\langle k\rangle S}\big)\big|_{S=0}=\langle k\rangle>1$。临界点附近展开 $1-e^{-cS}\approx cS-c^2S^2/2$，代入得 $S\approx2(c-1)/c^2\approx2(c-1)$。数值上可用不动点迭代 $S \leftarrow 1-e^{-\langle k\rangle S}$ 求解（见代码示例）。

### 分支大小分布

亚临界与临界状态下，从一个节点出发的探索近似为后代数服从泊松($\langle k\rangle$)的 Galton–Watson 分支过程。用 Lagrange 反演（或 Borel 分布）可得总后代数为 $s$ 的概率 $p_s=e^{-\langle k\rangle s}(\langle k\rangle s)^{s-1}/s!$。代入 Stirling 公式 $s!\approx\sqrt{2\pi s}\,(s/e)^s$：
$$
p_s\approx\frac{1}{\sqrt{2\pi}}\,s^{-3/2}\exp\!\big[-(\langle k\rangle-1)s+(s-1)\ln\langle k\rangle\big].
$$
$\langle k\rangle=1$ 时指数部分为 $e^0$，$p_s\approx s^{-3/2}/\sqrt{2\pi}$。代码示例在 $N=2\times10^5$ 的临界网络上验证：$p_1$、$p_2$、$p_3$ 的模拟值 0.368、0.137、0.074 与理论值 0.368、0.135、0.075 吻合。

### 完全连通区的阈值

在 $\langle k\rangle$ 较大时，巨分支已包含几乎所有节点，网络是否连通取决于是否还有孤立节点。一个节点孤立的概率 $(1-p)^{N-1}\approx e^{-pN}$，孤立节点的期望数 $I_N\approx Ne^{-pN}$。令 $I_N=1$ 得 $p=\ln N/N$，即 $\langle k\rangle\approx\ln N$。

### 广度优先搜索的伪代码与复杂度

```text
算法 1  BFS 求单源距离（无权图）
输入：图 G，源点 s；输出：dist（s 到各可达节点的距离）
1. dist ← {s: 0}；队列 Q ← [s]
2. while Q 非空:
3.     v ← Q.popleft()
4.     for u in 邻居(v):
5.         if u 不在 dist 中:
6.             dist[u] ← dist[v] + 1；Q.append(u)
7. return dist
```

每个节点入队、出队各一次，每条边在两端各被检查一次，总代价 $O(N+M)$。对全部节点各做一次得到所有点对距离，代价 $O(N(N+M))$。加权网络中改用以优先队列实现的 Dijkstra 算法，单源代价 $O(M+N\log N)$，要求边上的“长度”非负，因此相关系数等“强度型”权重需先转换为长度（如 $1/w$ 或 $-\log w$）。

### Brandes 介数算法

关键观察：定义源点 $s$ 对节点 $v$ 的**依赖度** $\delta_s(v)=\sum_{t}\sigma_{st}(v)/\sigma_{st}$，则 $C_B(v)=\sum_{s\ne v}\delta_s(v)$，且依赖度满足递推
$$
\delta_s(v)=\sum_{w:\,v\in\text{pred}_s(w)}\frac{\sigma_{sv}}{\sigma_{sw}}\big(1+\delta_s(w)\big),
$$
其中 $\text{pred}_s(w)$ 是 $s$ 到 $w$ 的最短路径上 $w$ 的前驱节点。

```text
算法 2  Brandes 介数（无权图）
对每个源点 s：
1. BFS：dist[s]=0，σ[s]=1；访问 v 的邻居 w 时，
   若 w 首次被发现则 dist[w]=dist[v]+1 并入队；
   若 dist[w]=dist[v]+1，则 σ[w] += σ[v]，把 v 加入 pred[w]。
   把出队顺序记入栈 S。
2. 回溯：δ ≡ 0；当 S 非空，弹出 w，
   对每个 v ∈ pred[w]：δ[v] += σ[v]/σ[w]·(1+δ[w])；
   若 w ≠ s：C_B[w] += δ[w]。
无向图最后把 C_B 除以 2。
```

每个源点的两个阶段都是 $O(N+M)$，总代价 $O(NM)$（稀疏图），远优于朴素方法的 $O(N^3)$。代码示例中的手写实现与 NetworkX 结果之差在 $10^{-14}$ 量级。

### 谱类中心性的幂迭代与收敛条件

- **特征向量**：$\mathbf x^{(t+1)}=A\mathbf x^{(t)}/\|A\mathbf x^{(t)}\|$。把初值按特征向量展开 $\mathbf x^{(0)}=\sum_i c_i\mathbf v_i$，则 $A^t\mathbf x^{(0)}=\sum_ic_i\lambda_i^t\mathbf v_i$，归一化后其他分量以 $|\lambda_i/\lambda_1|^t$ 衰减。二部图中 $-\lambda_1$ 也是特征值，简单幂迭代会振荡，可改用 $A+I$。
- **Katz**：$(I-\alpha A^{\top})\mathbf x=\beta\mathbf 1$。Neumann 级数 $\sum_t(\alpha A^{\top})^t$ 收敛当且仅当 $\alpha\lambda_1<1$。
- **PageRank**：$\mathbf x=dP\mathbf x+\frac{1-d}{N}\mathbf 1$，$P=A^{\top}D_{\text{out}}^{-1}$ 为列随机矩阵。迭代映射是压缩映射，误差每步至少乘以 $d$，收敛到 $10^{-6}$ 只需约 $\log(10^{-6})/\log0.85\approx85$ 步，与网络规模无关。
- **HITS**：交替执行 $\mathbf a\leftarrow A^{\top}\mathbf h$、$\mathbf h\leftarrow A\mathbf a$ 并归一化，等价于对 $A^{\top}A$ 与 $AA^{\top}$ 做幂迭代。若主特征值不唯一（网络由多个互不相连的部分组成），结果依赖初值。

每次迭代只需一次稀疏矩阵–向量乘法，代价 $O(M)$。

### k 核分解

```text
算法 3  核数（Batagelj–Zaversnik 思想）
1. 计算所有节点的度，按度放入桶中；k ← 0
2. 重复直到所有节点被删除：
3.     取当前度最小的节点 v；k ← max(k, deg(v))；core[v] ← k
4.     删除 v，把每个未删除邻居的度减 1 并移到相应桶中
```

每个节点删除一次，每条边导致一次度减少，用桶结构维护最小度，总代价 $O(N+M)$。“$k\leftarrow\max(k,\deg v)$”保证核数单调不减：当剩余图的最小度为 $k$ 时，剩余图本身就是 k 核。

## 研究前沿与开放问题 {#frontiers}

- **零模型的选择。**ER 网络只保持节点数与边数。保持度序列、空间嵌入、模块结构等性质的零模型更严格，但不同零模型可能得出不同结论。对于一个具体的生物网络，什么才是“公平”的比较对象，没有统一答案（见[小世界与无标度的统计判别](network-models.identification.html)与[网络构建与统计验证](network-construction.html)）。
- **路径类指标的生理含义。**在功能连接网络中，两个脑区之间的“最短路径”是否对应真实的信息传递路线并不清楚；Rubinov 与 Sporns（2010）对用路径长度解释“功能整合”持谨慎态度。基于随机游走、扩散或通信模型的替代指标（如扩散效率、导航效率）是活跃方向，怎样为整合类指标建立可检验的生理解释仍是开放问题。
- **中心性的公理化与可比性。**不同中心性满足的数学性质不同（Boldi 与 Vigna 2014 的公理），同一网络上不同指标的排名可能大相径庭。哪些性质对生物学问题是必要的、如何把中心性与动力学过程（传播、控制、同步）的真实影响相联系，仍在研究中。
- **测量误差下的稳健性。**分子网络的假阳性与假阴性、功能网络的估计误差都会扰动距离与中心性，介数和接近中心性对缺失边尤其敏感。如何为中心性排名给出置信区间、并在缺失数据下做校正，仍缺乏通用方法。
- **阈值与密度依赖。**功能网络的度、密度、聚集系数和路径长度都随阈值改变。固定密度、跨阈值积分、保留权重等策略各有利弊（见[脑连接组：结构与功能连接](brain-connectome.html)）。
- **研究偏倚。**分子网络中热门基因的度被系统性高估，如何在比较疾病基因与非疾病基因的拓扑指标时校正这种偏倚，仍需要谨慎的统计设计（见[疾病模块、网络邻近度与药物重定位](network-medicine.html)）。
- **超越成对连接。**聚集系数只看三角形；高阶相互作用（超图、单纯复形）和多层网络上的路径、效率与中心性定义尚未统一（见[动态功能连接与多层脑网络](dynamic-brain-networks.html)）。

## 生物医学应用 {#biomedical}

**脑网络中的三把尺子。** 在脑网络研究中，节点通常是按脑图谱划分的几十到几百个脑区。度高的脑区被称为枢纽脑区，常位于楔前叶、后扣带回、额顶联合皮层等；聚集系数和局部效率刻画局部“功能分离”（segregation），平均路径长度或全局效率刻画全脑“功能整合”（integration）。Achard 等（2006，*Journal of Neuroscience*）在静息态 fMRI 功能网络中报告了小世界性和位于联合皮层的枢纽。Rubinov 与 Sporns（2010，*NeuroImage*）系统整理了脑网络常用指标及其神经科学解释，是本专题指标在脑科学中的“使用手册”。需要注意的是，功能网络的边来自相关系数，必须先阈值化或保留权重，而阈值的选择会直接改变度、密度、聚集系数和路径长度（见[脑连接组：结构与功能连接](brain-connectome.html)中的阈值分析）。

::: {.callout-bio}
**脑网络枢纽的多指标识别。**van den Heuvel 与 Sporns（2013, *Trends in Cognitive Sciences*）综述了人脑枢纽的识别方法与功能角色：单一中心性给出的枢纽集合并不一致，因此常把度、介数、接近等多种中心性与节点的模块角色结合起来判定枢纽；文献中常被报告的结构枢纽包括楔前叶、后扣带回、额上回和岛叶等区域。该综述也讨论了枢纽在多种脑疾病中更易受累的证据。功能网络中“度被模块大小绑架”的问题与参与系数的用法见[拓扑指标：小世界、模块、枢纽与富人俱乐部](brain-connectome.topology.html)。
:::

**分子网络中的度与连通性。** 在蛋白质相互作用网络中，研究者常比较疾病基因与非疾病基因的度：疾病相关蛋白的度是否更高？这类分析要警惕“研究偏倚”——热门基因被研究得多，测到的相互作用也多，度自然偏高。另一个常见做法是检验一组疾病基因在网络中是否形成一个连通的子网络，并用随机抽取同样数量（最好度分布相近）的基因作为零模型，判断这种连通性是否超出随机预期——这正是“与零模型比较”思想的直接应用（见[疾病模块、网络邻近度与药物重定位](network-medicine.html)）。

**分子网络中的中心性：度、介数与核数各有所长。** Jeong 等（2001, *Nature*）在酵母 PPI 网络中发现高度蛋白更可能是必需基因（论文精读：[Jeong 2001](paper-jeong2001_lethality.html)；争论见[致死性与中心性](molecular-networks.centrality-lethality.html)）。Yu 等（2007, *PLoS Computational Biology*）进一步比较了度与介数：在无向的蛋白相互作用网络中，度对必需性的预测更强；而在有向的转录调控网络中，高介数的“瓶颈”比高度的枢纽更能预测必需性。Wuchty 与 Almaas（2005）则显示，处在 k 核分解最内层的蛋白更可能必需且进化保守。这些结果说明，同一个“重要性”问题，在不同类型的网络上最有信息量的中心性不同。

**PageRank 与基因排序。** GeneRank（Morrison 等 2005, *BMC Bioinformatics*）把 PageRank 的随机跳转向量换成基因的表达变化，让一个基因的得分同时取决于自身的差异表达和网络邻居的得分，在模拟与真实芯片数据中得到比单纯按倍数变化更好的排序。这类“网络传播”方法如今广泛用于疾病基因优先排序与药物靶点筛选（见[疾病模块、网络邻近度与药物重定位](network-medicine.html)）。

**随机网络作为零模型。** 在流行病学的接触网络、症状网络和分子网络中，ER 网络都常作为“没有结构”的基线：观测到的聚集系数、最大分支比例或中心性集中程度，只有在明显偏离同规模随机网络（更好的做法是偏离保度随机网络）时，才值得给出生物学解释。

## 适用范围与常见误用 {#limitations}

1. **误区**：平均度相同的两个网络结构相似。→ **正解**：平均度只是度分布的一阶矩，均匀分布与重尾分布可以有同样的平均度，但结构和功能（如鲁棒性、传播阈值）截然不同。
2. **误区**：平均聚集系数和传递性是同一个指标。→ **正解**：前者对节点等权平均，后者按连通三元组数加权，数值可能差别很大（空手道网络 0.57 对 0.26），报告时要写明定义。
3. **误区**：网络不连通时，直接调用函数算平均路径长度就行。→ **正解**：不连通网络的平均路径长度为无穷大（NetworkX 会报错）；应在最大连通分支上计算并报告其规模，或改用全局效率。
4. **误区**：全局效率就是平均路径长度的倒数。→ **正解**：$E_{\text{glob}}$ 是距离调和平均的倒数，连通网络中 $E_{\text{glob}}\ge1/L$，二者只在所有距离相等时相同。
5. **误区**：ER 网络与真实网络不符，所以 ER 模型没有用。→ **正解**：ER 网络是最基本的零模型，正是通过与它比较，才发现了真实网络的高聚类和重尾度分布。
6. **误区**：加权网络的最短路径可以直接把相关系数当作“距离”。→ **正解**：相关越强表示连接越近，应先把权重转换成长度（如取倒数），否则最短路径会走“最弱”的连接。
7. **误区**：加权聚集系数只有一种。→ **正解**：Onnela 与 Barrat 等定义回答不同问题，可能朝相反方向偏离无权值；应注明定义与软件实现。
8. **误区**：中心性最高的节点就是最重要的节点。→ **正解**：每种中心性对应一种流动假设，排名随指标、方向、权重和数据误差改变；“重要”需要按研究问题定义，并用独立证据检验。
9. **误区**：PageRank 比度“更高级”，在无向网络上也能给出新信息。→ **正解**：无向网络上 PageRank 与度高度相关（无随机跳转时正比于度），额外信息主要来自有向结构或个性化跳转向量。
10. **误区**：特征向量中心性可以直接用于任何有向网络。→ **正解**：不在强连通核心下游的节点得分为 0；有向网络应使用 Katz、PageRank 或 HITS。
11. **误区**：ER 网络 $\langle k\rangle>1$ 就是连通的。→ **正解**：$\langle k\rangle>1$ 只保证存在巨分支；整个网络连通需要 $\langle k\rangle>\ln N$。

## 关联知识 {#related}

- [复杂系统与网络的数学表示](network-basics.html)：邻接矩阵、边列表与握手定理是本专题所有指标的出发点。
- [小世界与无标度网络模型](network-models.html)：解释真实网络相对 ER 网络的两个反常——高聚类与重尾度分布，并给出小世界系数与幂律检验。
- [度相关性与网络结构的高阶统计](degree-correlations.html)：同配性、富人俱乐部等超出度分布的二阶结构，是 ER 模型无法解释的又一类性质。
- [社团结构与社区发现](community-structure.html)：在局部聚集与全局路径之间的中间尺度上描述网络结构；边介数用于 Girvan–Newman 算法。
- [网络鲁棒性、渗流与级联失效](robustness.html)：巨分支相变即渗流相变，用于分析随机失效与蓄意攻击。
- [网络上的传播与免疫](spreading.html)：度分布的二阶矩决定传播阈值，k 核与中心性用于识别关键传播者与免疫目标。
- [脑连接组：结构与功能连接](brain-connectome.html)：聚集系数、效率、枢纽与参与系数在脑网络中的使用与阈值问题。
- [疾病模块、网络邻近度与药物重定位](network-medicine.html)：用保度随机抽样作为零模型检验疾病基因的网络聚集，用网络传播对基因排序。

## 核心文献 {#references}

### Erdős & Rényi 1960：On the evolution of random graphs

- **出处**：*Publications of the Mathematical Institute of the Hungarian Academy of Sciences* 5: 17–61。（原刊无 DOI，可在网上找到公开的重排版）论文精读：[Erdős 1960](paper-erdos1960_randomgraphs.html)
- **背景**：图论此前主要研究具体的、确定的图。Erdős 与 Rényi 系统研究了“随机地加边，图会如何演化”。
- **核心发现**：随着边数增加，图的许多性质（是否含有某种子图、是否存在大连通分支、是否连通）会在某个临界边数附近**突然**出现，即阈值现象；巨连通分支在平均度为 1 时出现。
- **阅读提示**：这是一篇纯数学论文，不必逐条读证明。重点读引言和关于“巨分支”出现的部分，体会“相变”这一思想，[网络上的传播与免疫](spreading.html)（传播阈值）和[网络鲁棒性、渗流与级联失效](robustness.html)都会再次用到它。
- **思考题**：为什么巨连通分支恰好在平均度等于 1 时出现？试用“沿着边向外探索，每一步平均能找到几个新节点”的思路解释。

### Freeman 1977：A set of measures of centrality based on betweenness

- **出处**：*Sociometry* 40: 35–41。DOI：[10.2307/3033543](https://doi.org/10.2307/3033543)。论文精读：[Freeman 1977](paper-freeman1977_betweenness.html)
- **背景**：社会网络分析中，“中心”的直觉含义有多种，此前的指标多基于度或距离。
- **核心内容**：提出以“处在多少对节点的最短路径之间”度量节点对交流的控制力，即介数中心性，并给出网络层面的中心化指标。次年的 Freeman（1978, *Social Networks*）进一步把度、接近、介数三类中心性放在统一框架下比较。
- **阅读提示**：注意介数隐含的假设——交流沿最短路径进行、各条最短路径等可能。思考它在 PPI、调控网络和功能连接网络中是否成立。

### Rubinov & Sporns 2010：Complex network measures of brain connectivity: uses and interpretations

- **出处**：*NeuroImage* 52: 1059–1069。DOI：[10.1016/j.neuroimage.2009.10.003](https://doi.org/10.1016/j.neuroimage.2009.10.003)。论文精读：[Rubinov 2010](paper-rubinov2010_measures.html)
- **背景**：图论指标在脑影像研究中快速普及，但不同研究使用的定义、计算方法和解释各不相同。
- **核心内容**：把脑网络指标分为功能分离（聚集系数、局部效率、模块度）、功能整合（路径长度、全局效率）、中心性与枢纽、网络韧性等几类，给出二值/加权、有向/无向情形下的统一定义，并讨论各指标的神经生物学解释与局限。
- **阅读提示**：文末附有各指标数学定义的汇总，可作为“速查表”；特别留意作者对“路径长度是否真正反映信息传递”的谨慎态度。Rubinov 与 Sporns 提供的 Brain Connectivity Toolbox 是脑网络分析的常用工具。
- **思考题**：在功能连接网络中，两个脑区之间的“最短路径”有没有明确的生理含义？如果没有，平均路径长度还能解释为“整合能力”吗？

### 其他引用文献

- Achard S, Salvador R, Whitcher B, Suckling J, Bullmore E (2006). A resilient, low-frequency, small-world human brain functional network with highly connected association cortical hubs. *Journal of Neuroscience* 26: 63–72. DOI：[10.1523/JNEUROSCI.3874-05.2006](https://doi.org/10.1523/JNEUROSCI.3874-05.2006)
- Barrat A, Barthélemy M, Pastor-Satorras R, Vespignani A (2004). The architecture of complex weighted networks. *PNAS* 101: 3747–3752. DOI：[10.1073/pnas.0400087101](https://doi.org/10.1073/pnas.0400087101)
- Batagelj V, Zaversnik M (2003). An O(m) algorithm for cores decomposition of networks. arXiv:cs/0310049
- Boldi P, Vigna S (2014). Axioms for centrality. *Internet Mathematics* 10: 222–262. DOI：[10.1080/15427951.2013.865686](https://doi.org/10.1080/15427951.2013.865686)
- Bonacich P (1987). Power and centrality: a family of measures. *American Journal of Sociology* 92: 1170–1182. DOI：[10.1086/228631](https://doi.org/10.1086/228631)
- Borgatti SP (2005). Centrality and network flow. *Social Networks* 27: 55–71. DOI：[10.1016/j.socnet.2004.11.008](https://doi.org/10.1016/j.socnet.2004.11.008)
- Brandes U (2001). A faster algorithm for betweenness centrality. *Journal of Mathematical Sociology* 25: 163–177. DOI：[10.1080/0022250X.2001.9990249](https://doi.org/10.1080/0022250X.2001.9990249)
- Bringmann LF, Elmer T, Epskamp S, et al. (2019). What do centrality measures measure in psychological networks? *Journal of Abnormal Psychology* 128: 892–903. DOI：[10.1037/abn0000446](https://doi.org/10.1037/abn0000446)
- Brin S, Page L (1998). The anatomy of a large-scale hypertextual Web search engine. *Computer Networks and ISDN Systems* 30: 107–117. DOI：[10.1016/S0169-7552(98)00110-X](https://doi.org/10.1016/S0169-7552(98)00110-X)
- Dorogovtsev SN, Goltsev AV, Mendes JFF (2006). k-core organization of complex networks. *Physical Review Letters* 96: 040601. DOI：[10.1103/PhysRevLett.96.040601](https://doi.org/10.1103/PhysRevLett.96.040601)
- Estrada E, Rodríguez-Velázquez JA (2005). Subgraph centrality in complex networks. *Physical Review E* 71: 056103. DOI：[10.1103/PhysRevE.71.056103](https://doi.org/10.1103/PhysRevE.71.056103)
- Freeman LC (1978). Centrality in social networks: conceptual clarification. *Social Networks* 1: 215–239. DOI：[10.1016/0378-8733(78)90021-7](https://doi.org/10.1016/0378-8733(78)90021-7)
- Fronczak A, Fronczak P, Hołyst JA (2004). Average path length in random networks. *Physical Review E* 70: 056110. DOI：[10.1103/PhysRevE.70.056110](https://doi.org/10.1103/PhysRevE.70.056110)
- Katz L (1953). A new status index derived from sociometric analysis. *Psychometrika* 18: 39–43. DOI：[10.1007/BF02289026](https://doi.org/10.1007/BF02289026)
- Kitsak M, Gallos LK, Havlin S, et al. (2010). Identification of influential spreaders in complex networks. *Nature Physics* 6: 888–893. DOI：[10.1038/nphys1746](https://doi.org/10.1038/nphys1746)
- Kleinberg JM (1999). Authoritative sources in a hyperlinked environment. *Journal of the ACM* 46: 604–632. DOI：[10.1145/324133.324140](https://doi.org/10.1145/324133.324140)
- Latora V, Marchiori M (2001). Efficient behavior of small-world networks. *Physical Review Letters* 87: 198701. DOI：[10.1103/PhysRevLett.87.198701](https://doi.org/10.1103/PhysRevLett.87.198701)
- Martin T, Zhang X, Newman MEJ (2014). Localization and centrality in networks. *Physical Review E* 90: 052808. DOI：[10.1103/PhysRevE.90.052808](https://doi.org/10.1103/PhysRevE.90.052808)
- Morrison JL, Breitling R, Higham DJ, Gilbert DR (2005). GeneRank: using search engine technology for the analysis of microarray experiments. *BMC Bioinformatics* 6: 233. DOI：[10.1186/1471-2105-6-233](https://doi.org/10.1186/1471-2105-6-233)
- Newman MEJ, Strogatz SH, Watts DJ (2001). Random graphs with arbitrary degree distributions and their applications. *Physical Review E* 64: 026118. DOI：[10.1103/PhysRevE.64.026118](https://doi.org/10.1103/PhysRevE.64.026118)
- Onnela JP, Saramäki J, Kertész J, Kaski K (2005). Intensity and coherence of motifs in weighted complex networks. *Physical Review E* 71: 065103. DOI：[10.1103/PhysRevE.71.065103](https://doi.org/10.1103/PhysRevE.71.065103)
- Opsahl T, Agneessens F, Skvoretz J (2010). Node centrality in weighted networks: generalizing degree and shortest paths. *Social Networks* 32: 245–251. DOI：[10.1016/j.socnet.2010.03.006](https://doi.org/10.1016/j.socnet.2010.03.006)
- Pittel B, Spencer J, Wormald N (1996). Sudden emergence of a giant k-core in a random graph. *Journal of Combinatorial Theory, Series B* 67: 111–151. DOI：[10.1006/jctb.1996.0036](https://doi.org/10.1006/jctb.1996.0036)
- Seidman SB (1983). Network structure and minimum degree. *Social Networks* 5: 269–287. DOI：[10.1016/0378-8733(83)90028-X](https://doi.org/10.1016/0378-8733(83)90028-X)
- van den Heuvel MP, Sporns O (2013). Network hubs in the human brain. *Trends in Cognitive Sciences* 17: 683–696. DOI：[10.1016/j.tics.2013.09.012](https://doi.org/10.1016/j.tics.2013.09.012)
- Wuchty S, Almaas E (2005). Peeling the yeast protein network. *Proteomics* 5: 444–449. DOI：[10.1002/pmic.200400962](https://doi.org/10.1002/pmic.200400962)
- Yu H, Kim PM, Sprecher E, Trifonov V, Gerstein M (2007). The importance of bottlenecks in protein networks: correlation with gene essentiality and expression dynamics. *PLoS Computational Biology* 3: e59. DOI：[10.1371/journal.pcbi.0030059](https://doi.org/10.1371/journal.pcbi.0030059)

## 延伸资源 {#resources}

| 类型 | 资源 | 说明 |
|---|---|---|
| 教材 | Barabási, *Network Science*, Ch. 2 Graph Theory（[networksciencebook.com/chapter/2](http://networksciencebook.com/chapter/2)） | 度、邻接矩阵、加权与二分网络、路径与距离、BFS、连通性、聚集系数；进阶专题 2.A 讨论全局聚集系数 |
| 教材 | Barabási, *Network Science*, Ch. 3 Random Networks（[networksciencebook.com/chapter/3](http://networksciencebook.com/chapter/3)） | 随机网络模型、泊松度分布、演化的四个区间、小世界、聚集系数；进阶专题 3.A–3.G 给出泊松推导、最大最小度、巨分支、分支大小、完全连通区、相变与小世界修正 |
| 教材 | Newman, *Networks*（第 2 版, Oxford University Press, 2018），Ch. 7 Measures and metrics；随机图各章 | 中心性家族（度、特征向量、Katz、PageRank、枢纽与权威、接近、介数）、群组与 k 核、传递性与相似性的系统处理 |
| 工具 | Brain Connectivity Toolbox（[sites.google.com/site/bctnet](https://sites.google.com/site/bctnet/)） | 二值/加权、有向/无向的聚集、效率、路径、中心性、核结构函数清单，含权重–长度转换的说明；Python 版为 bctpy |
| 软件 | NetworkX 算法文档（[networkx.org](https://networkx.org/documentation/stable/reference/algorithms/index.html)） | 查阅 `clustering`、`transitivity`、`global_efficiency`、`betweenness_centrality`、`pagerank`、`core_number` 等函数的精确定义与约定 |
| 公开课 | Stanford CS224W（[主页](https://web.stanford.edu/class/cs224w/)） | 英文公开课；“网络性质与随机图模型”部分与本专题对应，视频在 YouTube（需境外网络） |
| 综述 | Newman 2003, “The structure and function of complex networks”, *SIAM Review*（[DOI](https://doi.org/10.1137/S003614450342480)） | 网络指标与模型的经典长综述，第 III 节（真实网络的性质）与本专题对应；论文精读见 [Newman 2003](paper-newman2003_review.html) |
| 脑网络 | Rubinov & Sporns 2010, *NeuroImage*（[DOI](https://doi.org/10.1016/j.neuroimage.2009.10.003)） | 脑网络指标的定义与解释，可作为脑网络分析的工具书 |
| 经典数据 | Zachary 1977, 空手道俱乐部网络（[DOI](https://doi.org/10.1086/jar.33.4.3629752)） | 本专题代码示例所用数据的原始论文；NetworkX 内置为 `karate_club_graph()` |

## 开放问题 {#questions}

1. 你的研究数据如果构建成网络（例如基因共表达网络或脑功能网络），你认为它的度分布更可能是均匀型还是重尾型？如果是重尾型，度最高的那些节点在生物学上可能是什么？你会如何排除“研究偏倚”等技术性原因？
2. 本专题把 ER 随机网络作为零模型。对于你的数据，ER 网络是否是一个“公平”的比较对象？你认为还应该保持哪些性质不变（例如度序列、空间距离、模块结构），比较才有意义？
3. 在你的网络里，“重要节点”应该按哪种流动模型来定义？如果度、介数和 PageRank 给出的前十名不一致，你会怎样决定报告哪一个，又如何检验它的生物学意义？
4. 一个功能连接网络的平均度为 10、节点数为 300。按 ER 理论它处于哪个演化区间？如果实际网络有若干孤立脑区，这更可能反映拓扑规律，还是阈值选择与测量噪声？
