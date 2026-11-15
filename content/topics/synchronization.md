---
id: synchronization
title: 同步与协同动力学
en: Synchronization and collective dynamics
domain: dynamics
legacy: L06
summary: 研究耦合振荡器如何在网络上达成同步，网络拓扑怎样决定同步阈值与稳定性，以及同步异常与疾病的关系。
keywords: [同步, Kuramoto 模型, 序参量, 相变, 拉普拉斯矩阵, 拉普拉斯谱, 代数连通度, 主稳定函数, 特征值比, 爆发式同步, 奇异态, 簇同步, 远程同步, 时滞, 噪声, 共识, 分层同步, 神经质量模型, Wilson–Cowan 模型, Hopf 模型, 全脑模型, 亚稳态, 锁相值, 相位滞后指数, 相干, 容积传导, 神经振荡, 起搏细胞, 昼夜节律, 癫痫]
synonyms: [synchronization, 同步化, coupled oscillators, 耦合振荡器, complete synchronization, 完全同步, phase synchronization, 相位同步, frequency locking, 频率锁定, generalized synchronization, 广义同步, lag synchronization, 滞后同步, Kuramoto model, Sakaguchi–Kuramoto, 相位滞后, order parameter, 序参量, critical coupling, 临界耦合, phase transition, 同步相变, incoherent state, 不相干态, Ott–Antonsen ansatz, Ott–Antonsen 约化, Laplacian, 拉普拉斯矩阵, Laplacian spectrum, 拉普拉斯谱, normalized Laplacian, 归一化拉普拉斯, algebraic connectivity, Fiedler value, Fiedler vector, 代数连通度, Fiedler 值, Fiedler 向量, Cheeger inequality, Cheeger 不等式, master stability function, MSF, 主稳定函数, eigenratio, 特征值比, synchronizability, 可同步性, Rössler oscillator, Rössler 振子, Lyapunov exponent, 李雅普诺夫指数, hierarchical synchronization, 分层同步, explosive synchronization, ES, 爆发式同步, 一级同步相变, hysteresis, 滞后环, chimera state, 奇异态, 嵌合态, cluster synchronization, 簇同步, 群同步, remote synchronization, 远程同步, network symmetry, 网络对称性, automorphism, 自同构, equitable partition, 等价划分, time delay, 时滞, 传导延迟, noise, 噪声, consensus, 共识动力学, DeGroot model, 意见动力学, neural mass model, 神经质量模型, Wilson–Cowan, Hopf model, Stuart–Landau oscillator, Stuart–Landau 振子, whole-brain model, 全脑模型, The Virtual Brain, TVB, metastability, 亚稳态, phase locking value, PLV, 锁相值, pairwise phase consistency, PPC, phase lag index, PLI, 相位滞后指数, weighted phase lag index, wPLI, 加权相位滞后指数, coherence, 相干, coherency, imaginary coherence, ImCoh, 虚部相干, volume conduction, 容积传导, source leakage, 源泄漏, Hilbert transform, 希尔伯特变换, surrogate data, 替代数据, neural oscillation, 神经振荡, sinoatrial node, 窦房结, pacemaker cells, 起搏细胞, suprachiasmatic nucleus, SCN, 视交叉上核, circadian rhythm, 昼夜节律, epilepsy, 癫痫, Epileptor, Parkinson's disease, 帕金森病, beta oscillation, β 振荡, deep brain stimulation, DBS, 深部脑刺激, coordinated reset, 协调复位]
demos: [kuramoto]
reviewed: 2026-11-15
---

## 概述 {#overview}

在[网络上的传播与免疫](spreading.html)中，节点状态是离散的（易感、感染、移除）。同步研究另一类网络动力学：每个节点本身是一个**振荡器**，有自己的节律，通过连接相互影响。当耦合足够强时，许多振荡器会“步调一致”，这就是**同步**（synchronization）。

心脏窦房结的起搏、视交叉上核产生的昼夜节律、大脑的 α/β/γ 节律都依赖同步；癫痫与帕金森病则与同步的异常有关。本专题围绕以下问题展开：

1. 怎样用数学描述“同步”，怎样度量同步程度（[同步现象与类型](synchronization.synchronization-types.html)、[Kuramoto 模型与序参量](synchronization.kuramoto-model.html)）；
2. 网络结构怎样决定同步何时开始、能否稳定：同步阈值中再次出现 $\langle k\rangle/\langle k^2\rangle$（[网络拓扑与同步阈值](synchronization.network-kuramoto.html)），而相同振荡器的同步稳定性归结为拉普拉斯矩阵的谱（[拉普拉斯谱与代数连通度](synchronization.laplacian-spectrum.html)、[主稳定函数与可同步性](synchronization.master-stability.html)）；
3. 同步的“非常规”形态：按模块分层出现（[分层同步](synchronization.hierarchical-sync.html)）、不连续地突然出现（[爆发式同步](synchronization.explosive-sync.html)）、只在部分节点出现（[簇同步与奇异态](synchronization.cluster-chimera.html)），以及时滞与噪声的作用（[时滞与噪声](synchronization.delay-noise.html)）；
4. 同步的线性简化——共识动力学——与代数连通度的关系（[共识动力学](synchronization.consensus.html)）；
5. 怎样把这些理论用于大脑：在结构连接组上搭建全脑动力学模型（[神经质量模型与全脑模型](synchronization.whole-brain-models.html)），以及怎样从 EEG/MEG 数据估计相位同步而不被容积传导误导（[从实测信号估计同步](synchronization.phase-synchrony-estimation.html)）。

本专题的谱方法与线性化思路是[网络可控性与稳定性](controllability.html)中动力学稳定性分析的基础；从实测信号估计同步的方法则直接通向[脑连接组：结构与功能连接](brain-connectome.html)和[动态功能连接与多层脑网络](dynamic-brain-networks.html)中的功能脑网络。全部示例代码见[计算实现](synchronization.html#code)。

## 同步现象与类型 {#synchronization-types}

1665 年，惠更斯（Huygens）发现挂在同一根横梁上的两只摆钟，过一段时间后摆动会变得严格反相——横梁的微小振动把两只钟“耦合”在了一起。类似现象随处可见：东南亚某些萤火虫成群同步闪光；放在同一块可滑动木板上的多个节拍器会逐渐同步；音乐厅里观众的掌声有时会自发变成整齐的节拍。生理学中的节律过程——心跳、呼吸、激素分泌、昼夜节律——同样可以从耦合振荡器的角度理解（Glass 2001，*Nature* 综述）。

::: {.callout-def}
**同步**：多个具有自身节律的动力学单元，通过相互作用使其节律（频率或相位）趋于一致的过程。常见类型包括：

- **完全同步**（complete / identical synchronization）：所有单元状态完全相同，$\mathbf x_1(t)=\mathbf x_2(t)=\cdots=\mathbf x_N(t)$，通常针对相同的单元，混沌振荡器也可以完全同步；
- **相位同步**：相位差保持有界或恒定，$|n\phi_1(t)-m\phi_2(t)|<\text{常数}$（$n{:}m$ 锁相），振幅可以不同甚至不相关；
- **频率锁定**（频率同步）：长时间平均频率相同，相位差可以不为零；
- **滞后同步**：$\mathbf x_2(t)\approx\mathbf x_1(t-\tau)$，一个单元重复另一个单元稍早的状态；
- **广义同步**：存在函数关系 $\mathbf x_2=\Phi(\mathbf x_1)$，两者状态不必相似，但可以互相预测；
- **簇同步**：网络分成若干组，组内同步而组间不同步（见[簇同步与奇异态](synchronization.cluster-chimera.html)）。
:::

这些类型大体从“强”到“弱”排列：完全同步意味着相位同步，相位同步意味着频率锁定，反之不成立。系统梳理见 Pikovsky、Rosenblum 与 Kurths 的专著《Synchronization: A Universal Concept in Nonlinear Sciences》（2001）以及 Boccaletti 等（2006，*Physics Reports*）的综述。

同步也不是“所有单元一样”那么简单。一群固有频率各不相同的振荡器，如果没有耦合，相位会在圆上各自转动；耦合弱时，它们只会彼此轻微扰动；耦合超过某个临界值后，一部分振荡器突然被“拉”到一起，形成同步簇。这种从无序到有序的转变是一种**相变**，Kuramoto 模型给出了它最简洁的描述。

::: {.callout-def}
**两条研究线**（Arenas 等 2008 的划分，见[精读](paper-arenas2008_sync.html)）：

| | 非相同振荡器的相位同步 | 相同振荡器的完全同步 |
|---|---|---|
| 代表模型 | Kuramoto 相振荡器 | 任意 $n$ 维系统（Rössler、神经元模型）经扩散耦合 |
| 核心问题 | 耦合多强时**开始**出现集体同步？ | 同步态是否**稳定**？ |
| 网络量 | $\langle k\rangle/\langle k^2\rangle$、邻接矩阵最大特征值 | 拉普拉斯谱：$\mu_2$、$\mu_N/\mu_2$ |
| 本专题 | Kuramoto 模型、网络阈值、爆发式同步 | 拉普拉斯谱、主稳定函数、簇同步 |

两条线回答不同问题，结论可以相反（例如度异质性使 Kuramoto 同步更早开始，却可能使完全同步更难稳定），阅读文献时要先分清是哪一条。
:::

## Kuramoto 模型与序参量 {#kuramoto-model}

### 模型

只用一个变量——相位 $\theta_i\in[0,2\pi)$——描述每个振荡器。Kuramoto（1975）提出：

$$\frac{d\theta_i}{dt}=\omega_i+\frac{K}{N}\sum_{j=1}^{N}\sin(\theta_j-\theta_i),\qquad i=1,\dots,N$$

$\omega_i$ 是固有频率，从分布 $g(\omega)$ 中抽取；$K$ 是耦合强度；正弦项使相位落后的振荡器加速、领先的减速。这是全连接（每个振荡器与所有其他振荡器耦合）的版本。

为什么只用相位就够？任何稳定的极限环振荡器在弱耦合下，振幅几乎不变，相互作用主要改变相位；对相位做平均（相位约化）后，耦合函数取决于相位差 $\Gamma(\theta_j-\theta_i)$。Kuramoto 模型就是取 $\Gamma$ 的第一个傅里叶分量。若保留一个相位偏移，得到 **Sakaguchi–Kuramoto 模型** $\sin(\theta_j-\theta_i-\alpha)$，它常用于模拟有传导延迟的系统，也是[奇异态](synchronization.cluster-chimera.html)出现的条件之一。

### 序参量

::: {.callout-def}
**Kuramoto 序参量**：
$$r\,e^{i\psi}=\frac{1}{N}\sum_{j=1}^{N}e^{i\theta_j}$$
把每个振荡器看作单位圆上的一点，$r e^{i\psi}$ 就是这些点的“质心”。$r\in[0,1]$ 度量相位同步程度：$r\approx0$ 表示相位均匀散开（不相干态），$r=1$ 表示完全相位同步；$\psi$ 是平均相位。
:::

直观例子：4 个振荡器相位分别为 $0,\pi/2,\pi,3\pi/2$，四个单位向量相加为零，$r=0$；若相位为 $0,0.1,-0.1,0$，则 $r\approx0.995$。

::: {.callout-warn}
有限个独立随机相位的 $r$ 并不为 0，而是约为 $1/\sqrt N$ 量级（$N=100$ 时约 0.09）。判断是否同步要看 $r$ 是否显著高于这个基线，并取时间平均。另一个陷阱：两个反相的大簇（各占一半）也会给出 $r\approx0$，所以 $r$ 小不等于“没有组织”。必要时计算二阶序参量 $r_2=|\langle e^{2i\theta}\rangle|$ 或看相位分布。
:::

### 平均场形式与临界耦合

利用序参量，方程可改写为

$$\frac{d\theta_i}{dt}=\omega_i+Kr\sin(\psi-\theta_i)$$

每个振荡器只与“平均场”$(r,\psi)$ 耦合，平均场又由所有振荡器决定——这是一个自洽问题。在以平均频率旋转的参照系中（取 $g$ 对称、中心为 0）：

- 若 $|\omega_i|\le Kr$，振荡器被**锁定**在 $\theta_i=\psi+\arcsin(\omega_i/Kr)$；
- 若 $|\omega_i|>Kr$，振荡器**漂移**，绕圆旋转，对 $r$ 的平均贡献为零。

自洽条件给出临界耦合强度：

$$K_c=\frac{2}{\pi g(0)}$$

$K<K_c$ 时只有不相干解 $r=0$；$K>K_c$ 时出现部分同步，$r$ 连续增长。对洛伦兹（柯西）分布 $g(\omega)=\dfrac{\gamma}{\pi(\omega^2+\gamma^2)}$，有精确解

$$K_c=2\gamma,\qquad r=\sqrt{1-\frac{K_c}{K}}\quad(K>K_c)$$

**计算例**：$\gamma=0.5$，则 $K_c=1$；$K=2$ 时 $r=\sqrt{0.5}\approx0.71$；$K=4$ 时 $r\approx0.87$。对标准差为 $\sigma$ 的高斯分布，$g(0)=1/(\sigma\sqrt{2\pi})$，$K_c=2\sigma\sqrt{2\pi}/\pi\approx1.60\,\sigma$。本站代码第一个示例（$N=500$）模拟得到 $K=2$ 时 $r\approx0.70$，$K=3$ 时 $r\approx0.81$，与理论值 0.71、0.82 相符。

::: {.callout-def}
**同步相变的直觉**：固有频率越分散（$g(0)$ 越小），越难同步，需要的耦合越强。临界点附近 $r\propto\sqrt{K-K_c}$，与铁磁体在居里温度附近磁化强度的行为类似——这正是物理学家对它感兴趣的原因。
:::

自洽方程与平方根标度的推导、以及对洛伦兹分布把无穷维系统严格约化为一个关于 $r$ 的常微分方程的 Ott–Antonsen 方法，见[数学推导与算法](synchronization.derivations.html)。

## 网络拓扑与同步阈值 {#network-kuramoto}

把全连接换成任意网络（邻接矩阵 $A$，可以带权）：

$$\frac{d\theta_i}{dt}=\omega_i+K\sum_{j}A_{ij}\sin(\theta_j-\theta_i)$$

### 两种阈值近似

**异质平均场**（Ichinomiya 2004，*PRE*）：假设度相同的节点统计上等价，节点 $i$ 感受到的平均场与其度 $k_i$ 成正比。与[传播阈值](spreading.epidemic-threshold.html)完全相同的推导给出

$$K_c=K_0\,\frac{\langle k\rangle}{\langle k^2\rangle},\qquad K_0=\frac{2}{\pi g(0)}$$

**最大特征值近似**（Restrepo、Ott 与 Hunt 2005，*PRE*）：对每个节点定义局部序参量 $r_i e^{i\psi_i}=\sum_jA_{ij}\langle e^{i\theta_j}\rangle$，在不相干态附近线性化，得到 $K_c\approx K_0/\Lambda_{\max}$，$\Lambda_{\max}$ 为 $A$ 的最大特征值。这一近似不需要“度相同即等价”的假设，适用于有度相关、有社团的网络；对无关联随机网络，$\Lambda_{\max}\approx\langle k^2\rangle/\langle k\rangle$，两者一致。

::: {.callout-def}
**与传播阈值的对照**：SIS 传播阈值 $\lambda_c=\langle k\rangle/\langle k^2\rangle$（或 $1/\Lambda_{\max}$），Kuramoto 同步阈值 $K_c=K_0\langle k\rangle/\langle k^2\rangle$（或 $K_0/\Lambda_{\max}$）。两者形式相同：度越异质，阈值越低。在无标度网络中，枢纽先与其邻居同步，再把同步“扩散”出去，所以**开始同步**所需的耦合很小；当 $\langle k^2\rangle$ 随 $N$ 发散（度指数 $\gamma\le3$），$K_c\to0$。
:::

**算例**：环（每个节点度为 2）上 $\langle k\rangle/\langle k^2\rangle=1/2$，$K_c=K_0/2$；星图（1 个中心、$N-1$ 个叶）上 $\langle k\rangle=2(N-1)/N$，$\langle k^2\rangle=(N-1)^2/N+(N-1)/N=(N-1)$，比值约为 $2/N$，$N=100$ 时异质平均场预测的 $K_c$ 只有环的约 1/25。（星图很小、度极端，平均场近似本身并不精确，这只说明趋势。）

### 同步的路径

阈值只描述起点。Arenas 等（2008）综述了数值结果：在 ER 网络中，许多小的同步团簇分散出现，再合并；在无标度网络中，包含枢纽的核心先同步，再逐步吸收周围节点。本站代码示例（$N=300$，平均度相同）中，异质平均场预测 BA 网络 $K_c\approx0.14$、ER 网络 $K_c\approx0.23$，模拟的 $r(K)$ 曲线中 BA 网络确实更早上升，但当 $K$ 较大时两者接近。

::: {.callout-warn}
网络 Kuramoto 模型中有两种常见的耦合写法：$K\sum_jA_{ij}\sin(\cdot)$（总输入随度增长）与 $\frac{K}{k_i}\sum_jA_{ij}\sin(\cdot)$（按度归一化）。后者中枢纽不再“更强”，$\langle k\rangle/\langle k^2\rangle$ 的结论不再成立。比较不同文献的 $K_c$ 时，先确认用的是哪一种写法，以及 $K$ 是否除以了 $N$ 或 $\langle k\rangle$。
:::

## 拉普拉斯谱与代数连通度 {#laplacian-spectrum}

从共识动力学、相同振荡器的同步稳定性，到谱聚类与随机游走，**图拉普拉斯矩阵**都是核心对象。本页集中整理它的定义、性质、典型图的谱与计算方法，供后面几个页面引用。

::: {.callout-def}
**拉普拉斯矩阵**：对无向（可加权）网络，$L=D-A$，$D=\mathrm{diag}(k_1,\dots,k_N)$ 为度（或强度）矩阵。即 $L_{ii}=k_i$，$L_{ij}=-A_{ij}$（$i\ne j$），每行和为零。其特征值记为
$$0=\mu_1\le\mu_2\le\cdots\le\mu_N .$$
$\mu_2$ 称为**代数连通度**（algebraic connectivity，Fiedler 1973），对应特征向量称为 **Fiedler 向量**；$\mu_N/\mu_2$ 称为**特征值比**（eigenratio）。
:::

### 基本性质

- **半正定**：$\mathbf x^\top L\mathbf x=\sum_{(i,j)\in E}w_{ij}(x_i-x_j)^2\ge0$，所以所有 $\mu_k\ge0$；$\mathbf 1$ 总是 0 特征值的特征向量。
- **连通分量**：0 特征值的重数等于连通分量个数；因此 $\mu_2>0\iff$ 网络连通。$\mu_2$ 越接近 0，网络越接近“断成两块”。
- **迹**：$\sum_k\mu_k=\mathrm{tr}\,L=\sum_ik_i=2m$（无权网络），所以平均特征值等于平均度。
- **加边单调**：加入一条边后，每个特征值都不减，且新旧谱交错：$\mu_k(G)\le\mu_k(G+e)\le\mu_{k+1}(G)$。注意这只保证“不减”，并不保证 $\mu_2$ 一定增加（见下面的环形图算例）。
- **常用界**（无权网络）：
  - $\mu_2\le\dfrac{N}{N-1}k_{\min}$（Fiedler 1973）：一个低度节点就能把 $\mu_2$ 压低；
  - $\mu_2\ge\dfrac{4}{N\cdot\mathrm{diam}(G)}$（Mohar 1991）：直径越大，$\mu_2$ 的下界越低；
  - $k_{\max}+1\le\mu_N\le\max_{(i,j)\in E}(k_i+k_j)\le2k_{\max}$（至少有一条边时）：枢纽决定 $\mu_N$。
- **Cheeger 不等式**：设 $h(G)=\min_{|S|\le N/2}\dfrac{|\partial S|}{|S|}$ 为“最窄瓶颈”（切掉的边数与较小一侧节点数之比），则 $\mu_2/2\le h(G)\le\sqrt{2k_{\max}\mu_2}$。$\mu_2$ 小意味着存在一个代价很低的二分——这是 Fiedler 向量可以用来做谱二分（见[谱方法与层次聚类](community-structure.spectral-hierarchical.html)）的理论依据。

上面三条界合在一起说明：**枢纽抬高 $\mu_N$，低度节点和瓶颈压低 $\mu_2$**，二者都会增大特征值比。这是后面“异质性悖论”的谱学根源。

### 典型图的拉普拉斯谱

| 图（$N$ 个节点） | 拉普拉斯特征值 | $\mu_2$ | $\mu_N/\mu_2$ |
|---|---|---|---|
| 完全图 $K_N$ | $0$，$N$（$N-1$ 重） | $N$ | $1$ |
| 星图 $S_N$ | $0$，$1$（$N-2$ 重），$N$ | $1$ | $N$ |
| 环 $C_N$ | $2-2\cos(2\pi k/N)$，$k=0,\dots,N-1$ | $2-2\cos(2\pi/N)$ | $N$ 大时约 $N^2/\pi^2$ |
| 路径 $P_N$ | $2-2\cos(\pi k/N)$，$k=0,\dots,N-1$ | $2-2\cos(\pi/N)$ | $N$ 大时约 $4N^2/\pi^2$ |

**手算例**：3 个节点的路径（也就是 3 节点星图）
$$L=\begin{pmatrix}1&-1&0\\-1&2&-1\\0&-1&1\end{pmatrix},$$
特征值为 $0,1,3$（迹 $=4=2m$），Fiedler 向量 $\propto(1,0,-1)$：两端取相反符号，中间为 0，自然地把两端分开。特征值比 $=3$；若再连上两端成为三角形 $K_3$，特征值变为 $0,3,3$，特征值比降为 1。

**环上加捷径**：$N=10$ 的环 $\mu_2\approx0.382$，且 $\mu_2$ 是**二重**特征值（对应 $\cos$ 与 $\sin$ 两个模式）。加一条对径捷径只能抬高其中一个，$\mu_2$ 不变，而 $\mu_N$ 增大，特征值比反而从 10.5 升到 12.7；再加一条与之“错开”的捷径，$\mu_2$ 升到约 0.70，特征值比降到 7.3（本站代码数值结果）。这个小例子说明谱的简并会让“加边改善同步”的直觉失效，优化网络时要直接计算谱。

### 归一化拉普拉斯

$\mathcal L=I-D^{-1/2}AD^{-1/2}$，特征值落在 $[0,2]$，且 2 是特征值当且仅当某个连通分量是二分图。它与随机游走转移矩阵 $P=D^{-1}A$ 的谱一一对应（$\lambda(P)=1-\lambda(\mathcal L)$），适用于按度归一化的耦合 $\frac{K}{k_i}\sum_j A_{ij}(\cdot)$，也决定随机游走的混合时间。度非常不均匀时，使用 $L$ 还是 $\mathcal L$ 会改变“哪个网络更易同步”的排序，报告结果时须说明。

### 计算

- 稠密特征分解（`numpy.linalg.eigvalsh`）复杂度 $O(N^3)$，$N$ 在数千以内可用；
- 大型稀疏网络只需要两端的少数特征值：用 Lanczos/LOBPCG 类迭代方法（`scipy.sparse.linalg.eigsh`、`networkx.algebraic_connectivity`、`networkx.fiedler_vector`），每次迭代成本 $O(m)$；求 $\mu_2$ 时要排除平凡的 $\mathbf 1$ 方向，迭代收敛速度取决于 $\mu_2$ 与 $\mu_3$ 的间隔，简并时（如上面的环）收敛慢；
- 有向网络的 $L$ 一般不对称，特征值可为复数，需要用一般特征值算法，并在[主稳定函数](synchronization.master-stability.html)中使用复平面上的稳定区。

## 主稳定函数与可同步性 {#master-stability}

对于**相同**的振荡器（如相同的神经元模型），完全同步态总是存在的，问题是：它稳定吗？Pecora 与 Carroll（1998，*PRL*）提出**主稳定函数**（master stability function, MSF）方法。设

$$\dot{\mathbf x}_i=\mathbf F(\mathbf x_i)-\sigma\sum_j L_{ij}\,\mathbf H(\mathbf x_j)$$

$\mathbf x_i\in\mathbb R^n$，$\mathbf F$ 是单个节点的动力学，$\mathbf H$ 是耦合函数（决定“通过哪些变量耦合”），$\sigma$ 是全局耦合强度，$L$ 为[拉普拉斯矩阵](synchronization.laplacian-spectrum.html)，特征值 $0=\mu_1<\mu_2\le\cdots\le\mu_N$（连通无向网络）。因为 $L$ 行和为零，同步流形 $\mathbf x_1=\cdots=\mathbf x_N=\mathbf s(t)$（$\dot{\mathbf s}=\mathbf F(\mathbf s)$）是不变集。

### 核心思想

在同步态附近线性化，扰动可以沿 $L$ 的特征向量分解成 $N-1$ 个互不耦合的横向模式，第 $k$ 个模式满足

$$\dot{\boldsymbol\eta}_k=\big[D\mathbf F(\mathbf s)-\sigma\mu_k\,D\mathbf H(\mathbf s)\big]\boldsymbol\eta_k .$$

所有模式都是同一个方程，只是参数 $\alpha=\sigma\mu_k$ 不同。于是定义**主稳定函数** $\Lambda(\alpha)$：主方程 $\dot{\boldsymbol\zeta}=[D\mathbf F(\mathbf s)-\alpha D\mathbf H(\mathbf s)]\boldsymbol\zeta$ 的最大李雅普诺夫指数。

::: {.callout-def}
**MSF 判据**：同步态局部稳定 $\iff$ $\Lambda(\sigma\mu_k)<0$ 对所有 $k=2,\dots,N$ 成立。$\Lambda(\alpha)$ 只取决于节点动力学 $\mathbf F$、耦合方式 $\mathbf H$；网络只通过 $\{\mu_k\}$ 进入。**节点动力学与网络结构因此被分离**：一个 $\Lambda(\alpha)$ 曲线可以用于任何网络。
:::

### MSF 的三种类型

按 $\Lambda(\alpha)<0$ 的区域形状（Boccaletti 等 2006 的归纳）：

1. **无稳定区**：$\Lambda(\alpha)>0$ 处处成立，任何网络、任何耦合强度都不能使同步稳定（耦合方式选错了变量）；
2. **无界稳定区** $(\alpha_1,\infty)$：只需 $\sigma\mu_2>\alpha_1$，**$\mu_2$ 越大越好**，所需最小耦合 $\sigma_{\min}=\alpha_1/\mu_2$；
3. **有界稳定区** $(\alpha_1,\alpha_2)$：需要 $\sigma\mu_2>\alpha_1$ 且 $\sigma\mu_N<\alpha_2$。存在这样的 $\sigma$ 当且仅当
$$\frac{\mu_N}{\mu_2}<\frac{\alpha_2}{\alpha_1}.$$
耦合太弱，慢模式不稳定；耦合太强，快模式（短波长模式）反而失稳。

::: {.callout-def}
**可同步性**：在第 3 类中，特征值比 $\mu_N/\mu_2$ 越小，网络越容易同步（能使同步稳定的耦合强度范围越宽）；在第 2 类中，代数连通度 $\mu_2$ 越大，所需耦合越弱。两个量都只依赖网络结构。
:::

### 例子

**例 1（可手算，第 2 类）**：标量节点 $\dot x=ax$（$a>0$，单独时不稳定），耦合 $H(x)=x$。主方程 $\dot\zeta=(a-\alpha)\zeta$，$\Lambda(\alpha)=a-\alpha$，稳定区为 $(a,\infty)$。取 $a=1$：3 节点路径 $\mu_2=1$，需要 $\sigma>1$；三角形 $\mu_2=3$，只需 $\sigma>1/3$；$N=5$ 的路径 $\mu_2\approx0.382$，需要 $\sigma>2.6$。

**例 2（数值，第 3 类）**：Rössler 振子（$a=b=0.2,\ c=7$，混沌），只通过 $x$ 分量耦合（$D\mathbf H=\mathrm{diag}(1,0,0)$）。本站代码对每个 $\alpha$ 积分变分方程并求最大李雅普诺夫指数，得到 $\Lambda(0)\approx+0.07$（即孤立 Rössler 振子的最大李雅普诺夫指数，混沌），稳定区约为 $(0.14,\,4.7)$，$\alpha_2/\alpha_1\approx35$（有限积分时长，数值仅作示意；参数不同时区间会变化）。于是 $N=100$、平均度 6 的规则环（$p=0$ 的 WS 网络）$\mu_N/\mu_2\approx156$，无论 $\sigma$ 取多少都无法同步；重连概率 $p=0.05$ 时降到约 34，处于边缘；$p=0.2$ 时约 19，可以同步。

### 由此得到的结论

- **小世界结构利于同步**：在环形规则网络中加入少量捷径，$\mu_N/\mu_2$ 急剧下降（Barahona 与 Pecora 2002，*PRL*）。长程连接让远处的节点能直接“对表”。
- **异质性悖论**：Nishikawa 等（2003，*PRL*）发现，度分布越异质的网络，尽管平均路径更短，按特征值比衡量却更难同步——枢纽抬高 $\mu_N$（$\mu_N\ge k_{\max}+1$），而大量低度节点压低 $\mu_2$。对耦合按度加权（如每个节点的输入除以其度）可以缓解这一问题（Arenas 等 2008 第 4 章）。
- 注意区分：度异质性使 Kuramoto 模型**更早开始**部分同步（$K_c$ 低），却可能使相同振荡器的**完全同步**更难稳定。两个结论回答的是不同问题。

::: {.callout-warn}
MSF 的适用条件：（1）振荡器**完全相同**，耦合函数 $\mathbf H$ 相同；（2）$L$ 行和为零（扩散型耦合）；（3）只给出**局部**（线性）稳定性：吸引域可能很小，噪声或参数失配可以使系统离开同步态（“气泡”与“间歇性失同步”）；（4）有向网络中 $\mu_k$ 为复数，需要在复平面上画 $\Lambda$；不可对角化时还需额外处理。参数略有差异的振荡器只能得到近似同步，误差大小可用 $\Lambda$ 与失配程度估计。
:::

完整推导见[数学推导与算法](synchronization.derivations.html) C 节，数值算法见算法 2。

## 模块结构与分层同步 {#hierarchical-sync}

Arenas、Díaz-Guilera 与 Pérez-Vicente（2006，*PRL*）在具有层次社团结构的网络上模拟相同振荡器的 Kuramoto 动力学，发现同步按层次出现：先在最小的社团内部同步，再到更大的社团，最后全局同步。各阶段的时间尺度与拉普拉斯谱中的“间隙”对应，因此同步过程本身可以用来**发现社团**——这把[社团结构与社区发现](community-structure.html)与同步动力学联系起来。

为什么是拉普拉斯谱？相同振荡器在同步态附近的线性化就是[共识动力学](synchronization.consensus.html) $\dot{\boldsymbol\theta}=-K L\boldsymbol\theta$，第 $k$ 个模式按 $e^{-K\mu_kt}$ 衰减。如果网络有 $c$ 个弱连接的社团，就会有 $c-1$ 个很小的特征值（社团之间的“慢模式”），与其余特征值之间存在明显间隙：快模式先衰减（社团内同步），慢模式后衰减（社团之间同步）。本站代码示例中，4 个社团的网络在 $t=20$ 时社团内平均 $r\approx0.98$，而全局 $r$ 只有约 0.46。

::: {.callout-warn}
“同步越强越好”是错误的直觉。在大脑中，功能分化要求不同模块保持相对独立，全局过度同步（如癫痫大发作）反而意味着信息处理能力的丧失。健康状态常处于“分离与整合”之间的平衡，模块化正是维持这种平衡的结构基础（另见[神经质量模型与全脑模型](synchronization.whole-brain-models.html)中的亚稳态）。
:::

另一类与模块结构有关的现象是**不连续的同步相变**，见[爆发式同步](synchronization.explosive-sync.html)。

## 爆发式同步 {#explosive-sync}

经典 Kuramoto 相变是连续的：$r$ 从 0 平滑增长。Gómez-Gardeñes、Gómez、Arenas 与 Moreno（2011，*PRL*）发现，若无标度网络中节点的固有频率与其度正相关（最简单地取 $\omega_i=k_i$），相变变成**不连续**的：前向增大 $K$ 时 $r$ 长时间停留在低值，然后在某个耦合强度突然跳到接近 1；反向减小 $K$ 时，$r$ 在更低的耦合强度才跌落。两条曲线之间形成**滞后环**（hysteresis），系统在一段耦合区间内**双稳**。

::: {.callout-def}
**爆发式同步**（explosive synchronization, ES）：网络同步相变表现为一级（不连续）相变，序参量跳变，并伴随滞后与双稳。其共同机制是**抑制大同步簇的逐步形成**：通常同步簇会从小到大逐步吸收节点（连续相变）；若某种结构或动力学约束阻止了小簇的形成，系统会积累到某一点后一次性整体同步。
:::

### 机制直觉

度–频率关联使枢纽的固有频率远离大多数低度节点。枢纽本应是同步的“种子”，但它的频率与邻居差异大，难以先与邻居锁定；低度节点之间又缺少直接耦合。于是部分同步簇难以形成，直到耦合足以同时克服枢纽与叶节点的频率差，整体在一瞬间锁定。星图上的解析处理可以得到前向与后向两个临界耦合（Gómez-Gardeñes 等 2011）。

其他可产生爆发式同步的机制包括：耦合强度按节点频率与其邻居频率之差加权、自适应耦合、高阶（三体）相互作用等。Boccaletti 等（2016，*Physics Reports*）把这类现象与“爆发式渗流”放在一起做了系统综述。

### 算例

本站代码在 BA 网络（$N=500$，$m=3$）上取 $\omega_i=k_i$（减去均值），前向扫描中 $r$ 在 $K=1.5$ 时约 0.15，到 $K=1.75$ 跳到约 0.94；后向扫描在 $K=1.5$ 仍保持约 0.91，形成一个耦合步长宽的滞后环。把同一组频率随机打乱（破坏度–频率关联）后，$r(K)$ 变为平滑上升，前向与后向曲线重合。（扫描步长较粗，滞后宽度仅作定性示意。）

::: {.callout-bio}
**麻醉与意识丧失**：Kim 等（2016，*Frontiers in Computational Neuroscience*）分析麻醉诱导意识丧失前后的人脑 EEG 功能网络，报告了与爆发式同步条件相符的网络特征（节点度与其振荡频率的关联等），并提出意识的突然恢复或丧失可能与这种不连续转变有关。这是一个用网络同步理论解释临床“突变”的尝试，但从 EEG 功能网络推断“度–频率关联”依赖于网络构建方式，结论仍需独立验证。
:::

::: {.callout-warn}
在有限、带噪声的系统中，“看起来很陡”的 $r(K)$ 曲线不足以判定一级相变。判别要点：（1）前向/后向扫描是否出现滞后；（2）滞后宽度是否随 $N$ 增大而保持（而不是消失）；（3）初值不同是否落到不同的稳态（双稳）。扫描时每一步必须沿用上一步的终态。
:::

## 簇同步与奇异态 {#cluster-chimera}

完全同步与完全不同步之间，还有许多“部分有序”的模式：一些节点同步、另一些不同步；或者网络分成几组，组内同步、组间相位不同。这些模式与网络的**对称性**密切相关。

### 簇同步与网络对称性

::: {.callout-def}
**簇同步**（cluster synchronization）：节点被划分为若干簇 $\mathcal C_1,\dots,\mathcal C_q$，同一簇内 $\mathbf x_i(t)=\mathbf x_j(t)$，不同簇的状态不同。
:::

哪些划分可能成为簇同步模式？关键是“同一簇的节点必须收到相同的输入”。

- **对称性（自同构）**：若置换 $\pi$ 把网络映成自身（$A_{\pi(i)\pi(j)}=A_{ij}$），节点又相同，则动力学方程在 $\pi$ 下不变。自同构群把节点分成**轨道**，轨道内节点“地位相同”，“每条轨道内状态相同”是动力学的一个不变子空间。Pecora 等（2014，*Nature Communications*）用群论（不可约表示）把同步态附近的扰动按对称性分块，从而计算每个簇模式的稳定性；他们还发现了**孤立失同步**（isolated desynchronization）：某一簇可以单独失去同步，而其他簇保持同步。Sorrentino 等（2016，*Science Advances*）进一步给出了簇同步稳定性的完整刻画。
- **等价划分**（equitable partition）：比对称性更弱的条件——每个簇 $\mathcal C_a$ 中的节点，连向簇 $\mathcal C_b$ 的边数都相同。等价划分同样保证簇同步子空间不变，可以出现在没有任何对称的网络中。

**算例**：星图的中心构成一条轨道，所有叶节点构成另一条轨道。叶节点之间**没有直接连接**，却可以通过中心彼此同步，而中心本身与它们状态不同——这称为**远程同步**（remote synchronization）。Nicosia 等（2013，*PRL*）指出远程同步揭示了网络的对称结构，可用于识别结构上等价的功能模块。本站代码中，用 Stuart–Landau 振子（中心固有频率 3，叶节点 1）模拟 1+6 节点星图，叶节点状态差收敛到数值零，中心的振幅（约 0.74）和相位与叶节点（约 0.92）不同。

::: {.callout-bio}
远程同步提示：两个脑区之间的高相位同步可以完全来自它们与同一个第三方区域的**对称**连接，而它们之间并无直接通路。这为“功能连接不等于结构连接”提供了一个动力学机制，与[结构–功能耦合](dynamic-brain-networks.sc-fc-coupling.html)中的通信模型讨论互补。
:::

### 奇异态（chimera）

::: {.callout-def}
**奇异态**（chimera state，也译作“嵌合态”）：在**相同**振荡器、**对称**耦合的网络中，同步区域与不同步区域稳定共存的状态。“奇异”在于：对称的系统自发打破了对称。
:::

Kuramoto 与 Battogtokh（2002）在非局域耦合的环形相振荡器中最早报告了这一现象；Abrams 与 Strogatz（2004，*PRL*）把它命名为 chimera，并对环形模型给出了解析描述。最简单的模型是两组相同振荡器，组内耦合 $\mu$ 强于组间耦合 $\nu$，采用 Sakaguchi–Kuramoto 耦合 $\sin(\theta_j-\theta_i-\alpha)$，$\alpha$ 略小于 $\pi/2$：在一定参数范围内，一组完全同步，另一组保持部分不相干。奇异态的出现需要非局域（不是最近邻、也不是全局均匀）的耦合结构和相位滞后；Panaggio 与 Abrams（2015，*Nonlinearity*）给出了系统综述。Shanahan（2010，*Chaos*）在社团结构的振荡器网络中观察到“亚稳态的奇异态”：哪个社团同步、哪个不同步随时间切换，并据此提出了度量亚稳态的指标（见[全脑模型](synchronization.whole-brain-models.html)）。

::: {.callout-warn}
奇异态常被拿来类比海豚、部分鸟类的**单半球睡眠**（一侧大脑半球呈慢波睡眠、另一侧保持清醒，Rattenborg 等 2000 综述），但这只是现象上的类比：真实大脑两半球并不相同，也不是对称耦合的相同振荡器。把某个脑电现象称为“奇异态”之前，需要说明模型假设在多大程度上成立。
:::

## 时滞与噪声 {#delay-noise}

真实系统中的耦合不是瞬时的，振荡器也不是确定性的。时滞和噪声都会改变同步阈值，有时还会产生新的现象。

### 时滞

大脑中，信号沿轴突传导需要时间：长程纤维长度可达十几厘米，传导速度从每秒数米到数十米，延迟可达数毫秒到数十毫秒，与 γ 振荡（约 25 ms 周期）同一量级。带时滞的 Kuramoto 模型为

$$\dot\theta_i(t)=\omega_i+\frac{K}{N}\sum_j\sin\big(\theta_j(t-\tau_{ij})-\theta_i(t)\big).$$

Yeung 与 Strogatz（1999，*PRL*）分析了均匀时滞 $\tau$ 的情形。对相同的振荡器（$\omega_i=\omega$），同相同步解 $\theta_i=\Omega t$ 的集体频率满足

$$\Omega=\omega-K\sin(\Omega\tau),$$

且该解稳定要求 $K\cos(\Omega\tau)>0$。由此得到几条结论：

- 时滞**降低**集体频率（$\Omega<\omega$ 当 $\sin(\Omega\tau)>0$）；
- $\tau$ 较大时方程有**多个解**，多个同步态共存（多稳态），系统落在哪个取决于初始历史；
- 某些 $\tau$ 下同相态不稳定，反相或行波态可能取而代之。

**算例**（本站代码）：$\omega=1,\ K=1$。$\tau=0.5$ 时唯一解 $\Omega\approx0.671$；$\tau=1.5$ 时 $\Omega\approx0.416$；$\tau=2.5$ 时有三个解 $\Omega\approx0.307,\ 1.438,\ 1.975$，其中 0.307 与 1.975 满足 $K\cos(\Omega\tau)>0$ 为稳定，从相近初值出发的模拟落在 0.307。

时滞在全脑模型中非常重要：Cabral 等（2011，*NeuroImage*）把以 γ 频段振荡的 Kuramoto 振荡器放在人脑结构连接组上，用纤维长度除以传导速度作为时滞，发现只有在适当的耦合强度与传导速度下，模型才能重现 fMRI 静息态功能连接中的慢波相关结构（见[神经质量模型与全脑模型](synchronization.whole-brain-models.html)）。

### 噪声

在每个振荡器上加独立白噪声：$d\theta_i=[\omega_i+Kr\sin(\psi-\theta_i)]dt+\sqrt{2D}\,dW_i$。噪声把相位“抖散”，与频率分散的作用类似。不相干态的线性稳定性分析（Sakaguchi 1988；Strogatz 与 Mirollo 1991）给出

$$K_c=\frac{2}{\displaystyle\int\frac{D\,g(\omega)}{D^2+\omega^2}d\omega}.$$

两种特例：相同振荡器（$g=\delta$）$K_c=2D$；洛伦兹分布 $K_c=2(\gamma+D)$——噪声强度直接加在频率分布的半宽上。本站代码（$N=2000,\ \gamma=0.5$）中，$D=0$ 时 $r(K{=}2)\approx0.71$，$D=0.5$ 时理论 $K_c=2$，$r(K{=}2)$ 降到约 0.14，到 $K=3$ 才回升到约 0.64。

::: {.callout-warn}
噪声并不总是破坏同步。共同噪声（所有振荡器收到同一个噪声输入）可以诱导**无耦合**的振荡器同步；适量噪声还可以使可兴奋系统产生更规则的振荡（相干共振）。因此，若两个脑区接受共同的皮层下输入，它们的高同步未必反映彼此之间的耦合——这是从数据推断“连接”时必须排除的混杂因素。
:::

## 神经质量模型与全脑模型 {#whole-brain-models}

前面的振荡器是抽象的。要用同步理论解释脑成像数据，需要一个层级：把每个脑区（数百万神经元）描述为一个低维的“群体”动力学单元（**神经质量模型**），再按结构连接组把它们耦合成**全脑模型**。Breakspear（2017，*Nature Neuroscience*）系统综述了这一类模型及其与 fMRI、EEG/MEG 数据的关系。

### Wilson–Cowan 模型

Wilson 与 Cowan（1972，*Biophysical Journal*）用兴奋性群体活动 $E(t)$ 与抑制性群体活动 $I(t)$ 描述一个局部神经回路：

$$\begin{aligned}
\tau_E\dot E&=-E+S_E\big(w_{EE}E-w_{EI}I+P\big),\\
\tau_I\dot I&=-I+S_I\big(w_{IE}E-w_{II}I+Q\big),
\end{aligned}$$

$S$ 是 S 形的激活函数（群体中“超过阈值”的神经元比例），$w$ 是群体间耦合，$P,Q$ 是外部输入。随着输入变化，这个二维系统可以有一个或多个稳定的不动点，或经过 Hopf 分岔产生**兴奋–抑制交替的极限环振荡**——这是神经振荡最基本的群体机制。把多个 Wilson–Cowan 单元按结构连接耦合，就得到网络模型。

### Hopf（Stuart–Landau）全脑模型

更进一步的简化只保留“振荡是否出现”这一关键特征。在 Hopf 分岔附近，任何振荡系统都可以约化为 Stuart–Landau 范式。Deco 等（2017，*Scientific Reports*）的全脑模型中，每个脑区 $j$ 用复变量 $z_j=x_j+iy_j$ 描述：

$$\dot z_j=(a_j+i\omega_j)z_j-|z_j|^2z_j+G\sum_kC_{jk}(z_k-z_j)+\beta\eta_j(t)$$

- $a_j$ 为分岔参数：$a<0$ 时孤立节点只有噪声驱动的阻尼振荡，$a>0$ 时为自持振荡（振幅 $\sqrt a$）；
- $\omega_j$ 取自该脑区 fMRI 信号的峰值频率（约 0.04–0.07 Hz）；
- $C$ 为结构连接（dMRI 纤维追踪），$G$ 为全局耦合强度，$x_j$ 作为模拟的 BOLD 信号。

拟合流程通常是：扫描 $G$（以及 $a$），对每组参数模拟信号、计算模拟的功能连接（FC），选择使模拟 FC 与实测 FC 最相似、或使亚稳态等动力学统计量最接近实测的参数。与之同类的模型还有带时滞的 Kuramoto 模型（Cabral 等 2011）以及更详细的平均场模型，开源仿真平台 The Virtual Brain 集成了多种神经质量模型与连接组（Sanz Leon 等 2013，*Frontiers in Neuroinformatics*）。

::: {.callout-def}
**亚稳态**（metastability）：系统在多个短暂的、部分同步的构型之间不断切换，既不完全同步，也不完全无序。常用指标是全局（或社团）序参量 $r(t)$ 随时间的**标准差**（或方差；Shanahan 2010）：$r(t)$ 恒定低（无序）或恒定高（锁定）时，标准差都小；在两者之间频繁起伏时，标准差最大。许多全脑模型在接近同步转变（或节点接近 Hopf 分岔）时亚稳态最高，模拟 FC 与实测 FC 也拟合得最好。
:::

**算例**（本站代码）：用 4 个模块 × 10 个脑区的加权随机网络代替连接组，Stuart–Landau 节点 $a=-0.02$。全局耦合 $G=0$ 时模拟 FC 与结构连接几乎无关（相关约 $-0.06$）；$G=0.05$ 时相关升到约 0.80；$G$ 继续增大，平均同步 $r$ 升高（0.31→0.81），FC 与结构的相关反而下降到约 0.6，亚稳态（$r(t)$ 标准差）在中间的 $G$ 处最高。这说明“结构–功能对应最好”的工作点出现在中等耦合，而非越强越好。

::: {.callout-warn}
全脑模型的局限：（1）参数（$G$、分岔参数、时滞、噪声）通常只拟合几个汇总统计量，**多组参数可以拟合得同样好**（可辨识性问题）；（2）拟合目标 FC 本身有很大的测量与预处理不确定性（见[预处理对功能连接的影响](brain-connectome.preprocessing.html)）；（3）结构连接由纤维追踪估计，含系统偏差且无方向；（4）“模型能重现 FC”不等于模型机制正确——一个线性扩散模型往往也能解释相当一部分 FC。把全脑模型用于“虚拟手术”或个体化治疗规划前，需要在独立数据上验证预测能力。
:::

## 从实测信号估计同步 {#phase-synchrony-estimation}

模型里的相位是现成的，实测信号（EEG、MEG、局部场电位、钙成像）则需要先提取相位，再选择合适的同步指标。

### 提取相位

1. **带通滤波**：只保留感兴趣的频段（如 8–12 Hz 的 α 波），因为相位只对窄带信号有明确含义；带宽太宽时希尔伯特相位难以解释，太窄时滤波器会人为引入长时间的相位相关；
2. **提取瞬时相位**：用希尔伯特变换得到解析信号 $s(t)+i\,\mathcal H[s](t)=A(t)e^{i\phi(t)}$，其辐角 $\phi(t)$ 即瞬时相位（也可用复小波卷积，两者在合适参数下等价）；
3. **计算同步指标**：群体同步用 Kuramoto 序参量 $r(t)$；两两同步用下面的指标，得到的 $N\times N$ 矩阵就是一种“功能连接”网络；
4. **与替代数据比较**：对一个信号做时间循环平移、相位随机化或打乱试次（surrogate data），重复计算，得到“无真实耦合时”的分布，判断观察到的同步是否显著。

### 常用指标

记两信号在某频率（或窄带）上的复数表示为 $X(t)=A_x e^{i\phi_x}$、$Y(t)=A_y e^{i\phi_y}$，交叉谱 $S_{xy}=X Y^*$，相位差 $\Delta\phi=\phi_x-\phi_y$。$\langle\cdot\rangle$ 表示对时间点或试次平均。

::: {.callout-def}
- **锁相值**（phase locking value, PLV；Lachaux 等 1999）：$\mathrm{PLV}=\big|\langle e^{i\Delta\phi}\rangle\big|$，本质上是相位差的 Kuramoto 序参量，只看相位、不看振幅。
- **成对相位一致性**（pairwise phase consistency, PPC；Vinck 等 2010）：$\mathrm{PPC}=\dfrac{T\cdot\mathrm{PLV}^2-1}{T-1}$（$T$ 为独立样本数），去除了 PLV 随样本量变化的偏倚。
- **相干**（coherence）：复数相干 $C_{xy}=\dfrac{\langle S_{xy}\rangle}{\sqrt{\langle|X|^2\rangle\langle|Y|^2\rangle}}$，其模 $|C_{xy}|$（或平方）同时反映相位一致与振幅协变。
- **虚部相干**（imaginary coherence；Nolte 等 2004）：$|\mathrm{Im}\,C_{xy}|$，只保留非零滞后的成分。
- **相位滞后指数**（phase lag index, PLI；Stam 等 2007）：$\mathrm{PLI}=\big|\langle\mathrm{sign}(\sin\Delta\phi)\rangle\big|$，度量相位差分布偏向一侧（一方持续领先）的程度。
- **加权相位滞后指数**（weighted PLI, wPLI；Vinck 等 2011）：$\mathrm{wPLI}=\dfrac{|\langle\mathrm{Im}\,S_{xy}\rangle|}{\langle|\mathrm{Im}\,S_{xy}|\rangle}$，按虚部大小加权，对接近 0 或 $\pi$ 的小相位差（最容易被噪声翻转符号）赋予小权重，因而比 PLI 更稳健。
:::

### 容积传导

EEG/MEG 的每个传感器都记录多个源的线性混合，同一个源同时出现在多个通道上，且**几乎没有时间滞后**（准静态电磁场传播是瞬时的）。因此，零滞后的成分既可能是真实的零滞后同步，也可能只是同一个源被两个通道“看到”。在源空间分析中，同样问题表现为**源泄漏**。

- PLV 与幅度相干对容积传导敏感：混合本身就能产生高 PLV；
- 虚部相干、PLI、wPLI 丢弃了相位差为 0（或 $\pi$）的成分，因此对纯粹的瞬时混合不敏感；
- 代价：它们同时丢掉了真实存在的零滞后同步，并且受相位差大小和信噪比影响，数值不能直接解释为“耦合强度”。

**算例**（本站代码）：构造源 $s_1$（10 Hz）与延迟 20 ms 的 $s_2$（真实的滞后耦合），以及无关源 $s_3$；电极 $e_1=s_1+0.5s_3$、$e_2=s_2+0.5s_3$、$e_3=s_3+$噪声。在 8–12 Hz：$e_1$–$e_2$ 的 PLV≈0.89、PLI≈wPLI≈1、|ImCoh|≈0.56，所有指标都高；$e_1$–$e_3$ 之间只有混合造成的零滞后相关，PLV≈0.29（高于循环平移替代数据的 95% 分位数 0.10，“显著”）、|Coh|≈0.47，而 PLI≈wPLI≈0.01、|ImCoh|≈0.04。也就是说，一个仅由容积传导产生的“连接”通过了替代数据检验——替代数据只能排除“完全独立”，不能排除共同源。

::: {.callout-def}
**从同步矩阵到网络**：对 $N$ 个通道两两计算同步指标，得到 $N\times N$ 的同步矩阵；对它取阈值或保留权重，就得到一个网络，可以用[网络结构指标与随机图](network-metrics.html)、[小世界与无标度网络模型](network-models.html)、[社团结构与社区发现](community-structure.html)中的全部指标分析。[脑连接组](brain-connectome.html)与[动态功能连接](dynamic-brain-networks.html)中的功能脑网络正是这一思路，只是 fMRI 中多用相关系数代替相位同步；电生理网络的其他方法学问题（源空间分析、微状态）见[EEG/MEG 网络与微状态](dynamic-brain-networks.electrophysiology.html)。
:::

::: {.callout-warn}
相位同步指标对信号长度、滤波带宽和信噪比都敏感：数据越短，偶然得到的锁相值越高（独立相位时 $\mathbb E[\mathrm{PLV}^2]\approx1/T$，与[序参量](synchronization.kuramoto-model.html)的 $r\sim1/\sqrt N$ 基线道理相同）。比较两组被试时，要保证数据长度、试次数和预处理一致，优先使用 PPC 等无偏指标；信噪比不同（如患者伪迹更多）也会造成组间差异。Bastos 与 Schoffelen（2016，*Frontiers in Systems Neuroscience*）对这些解释陷阱有系统的教学性综述。
:::

## 共识动力学 {#consensus}

如果每个节点只有一个标量状态 $x_i$（意见、估计值、温度），并向邻居靠拢：

$$\frac{dx_i}{dt}=\sum_j A_{ij}(x_j-x_i)\quad\Longleftrightarrow\quad\dot{\mathbf x}=-L\mathbf x$$

这就是**共识**（consensus）动力学。把 Kuramoto 模型在同步态附近线性化（$\sin(\theta_j-\theta_i)\approx\theta_j-\theta_i$，$\omega_i$ 相同），得到的正是这个方程；它也是[主稳定函数](synchronization.master-stability.html)中例 1 的特例。

::: {.callout-def}
**共识定理（无向连通网络）**：$\mathbf x(t)\to\bar x\,\mathbf 1$，其中 $\bar x=\frac1N\sum_i x_i(0)$ 为初值平均；收敛速度由代数连通度决定，偏离共识的误差约按 $e^{-\mu_2 t}$ 衰减。对强连通的有向网络，也会达成一致，但一致值是初值的加权平均，权重由 $L$ 的左零特征向量给出。
:::

**例子**：5 个节点的路径图 $\mu_2\approx0.38$，5 个节点的完全图 $\mu_2=5$，后者达成共识快约 13 倍。本站代码中，$N=60$、平均度 4 的环 $\mu_2\approx0.055$，误差降到 1% 用时约 65；重连概率 0.5 的 WS 网络 $\mu_2\approx0.57$，用时约 5，$\mu_2\times$时间在各网络间量级相近。离散时间版本 $\mathbf x(t+1)=W\mathbf x(t)$（$W$ 行随机）即社会学中的 DeGroot 意见模型；在多机器人编队、传感器网络中，共识算法用于分布式估计（Olfati-Saber、Fax 与 Murray 2007，*Proceedings of the IEEE*）。

共识动力学给出了一个统一视角：**$\mu_2$ 衡量网络“多快能变得一致”**。它同时出现在同步稳定性、共识速度、谱聚类（[社团结构与社区发现](community-structure.html)中的 Fiedler 向量）和随机游走混合时间中，其性质集中整理在[拉普拉斯谱与代数连通度](synchronization.laplacian-spectrum.html)。

## 数学推导与算法 {#derivations}

本页补全以下推导：A. Kuramoto 自洽方程与 $K_c=2/(\pi g(0))$；B. 共识方程的显式解与 $\mu_2$ 的作用；C. 主稳定函数如何导出特征值比判据；D. 洛伦兹分布下的 Ott–Antonsen 约化；E. 簇同步的商网络；以及三个数值算法。

### A. Kuramoto 自洽方程与临界耦合

**假设**：全连接、$N\to\infty$；$g(\omega)$ 关于 0 对称、单峰（在 $\omega=0$ 处取最大值）；只寻找 $r$ 与 $\psi$ 不随时间变化的稳态解，不讨论其稳定性。由对称性可取平均频率为 0，并选坐标使 $\psi=0$。

**第 1 步：两类振荡器。** 平均场方程变为 $\dot\theta_i=\omega_i-Kr\sin\theta_i$。

- 若 $|\omega_i|\le Kr$，存在不动点 $\sin\theta_i=\omega_i/(Kr)$；其中满足 $\cos\theta_i\ge0$ 的那个稳定，即 $\theta_i=\arcsin(\omega_i/Kr)\in[-\pi/2,\pi/2]$。这些是**锁定**振荡器。
- 若 $|\omega_i|>Kr$，$\dot\theta_i$ 不变号，振荡器绕圆**漂移**，在 $\theta$ 处停留的时间与 $1/|\dot\theta|$ 成正比，平稳密度 $\rho(\theta\,|\,\omega)\propto1/|\omega-Kr\sin\theta|$。由于 $\rho(\theta+\pi\,|\,-\omega)=\rho(\theta\,|\,\omega)$ 且 $g$ 对称，漂移振荡器对 $\langle\cos\theta\rangle$ 和 $\langle\sin\theta\rangle$ 的贡献两两抵消。

**第 2 步：自洽条件。** 序参量 $r=\langle e^{i\theta}\rangle$ 只剩锁定振荡器的贡献；虚部因 $g$ 对称而为零，实部为
$$
r=\int_{-Kr}^{Kr}\cos\theta(\omega)\,g(\omega)\,d\omega .
$$
换元 $\omega=Kr\sin\theta$，$d\omega=Kr\cos\theta\,d\theta$：
$$
r=Kr\int_{-\pi/2}^{\pi/2}\cos^2\theta\;g(Kr\sin\theta)\,d\theta .
$$
这就是**自洽方程**。$r=0$ 永远是解（不相干态）。

**第 3 步：分岔点。** 若 $r>0$，两边除以 $r$：
$$
1=K\int_{-\pi/2}^{\pi/2}\cos^2\theta\;g(Kr\sin\theta)\,d\theta .
$$
令 $r\to0^+$，$g(Kr\sin\theta)\to g(0)$，且 $\int_{-\pi/2}^{\pi/2}\cos^2\theta\,d\theta=\pi/2$，得 $1=K g(0)\pi/2$，即
$$
K_c=\frac{2}{\pi g(0)} .
$$

**第 4 步：临界点附近的 $r$。** 把 $g$ 在 0 处展开到二阶，$g(Kr\sin\theta)\approx g(0)+\tfrac12 g''(0)K^2r^2\sin^2\theta$，并用 $\int_{-\pi/2}^{\pi/2}\cos^2\theta\sin^2\theta\,d\theta=\pi/8$：
$$
1=\frac{K}{K_c}+\frac{\pi}{16}g''(0)K^3r^2
\;\Longrightarrow\;
r^2\approx\frac{16\,(K-K_c)}{\pi K_c^4\,[-g''(0)]}.
$$
单峰分布 $g''(0)<0$，所以只有 $K>K_c$ 时才有实解，且 $r\propto\sqrt{K-K_c}$——这就是[Kuramoto 模型与序参量](synchronization.kuramoto-model.html)中所说的连续相变及其平方根标度。对洛伦兹分布，自洽积分可以精确计算，得到 $r=\sqrt{1-2\gamma/K}$（另一种推导见 D 节）。

::: {.callout-warn}
上述推导只回答“部分同步的稳态解是否存在”，没有回答它是否稳定、有限 $N$ 时如何涨落；不相干态在 $K<K_c$ 时的稳定性涉及更细的分析（Strogatz 2000，*Physica D* 的综述有详细讨论）。若 $g$ 不是单峰（如双峰），相变可以是不连续的。
:::

### B. 共识方程的显式解与代数连通度

设网络无向、连通，边权 $w_{ij}=w_{ji}\ge0$，$L=D-A$。

**第 1 步：$L$ 半正定。** 对任意 $\mathbf x$，
$$
\mathbf x^\top L\mathbf x=\sum_{(i,j)\in E}w_{ij}(x_i-x_j)^2\ge0,
$$
等号成立当且仅当每条边两端相等；连通时即 $\mathbf x\propto\mathbf 1$。所以 0 是单重特征值，$\mu_2>0$。

**第 2 步：谱分解求解。** $L$ 对称，有正交归一特征向量 $\mathbf v_1=\mathbf 1/\sqrt N,\mathbf v_2,\dots,\mathbf v_N$。线性方程 $\dot{\mathbf x}=-L\mathbf x$ 的解为
$$
\mathbf x(t)=e^{-Lt}\mathbf x(0)=\sum_{k=1}^{N}e^{-\mu_kt}\,(\mathbf v_k^\top\mathbf x(0))\,\mathbf v_k
=\bar x\,\mathbf 1+\sum_{k=2}^{N}e^{-\mu_kt}c_k\mathbf v_k ,
$$
其中 $c_k=\mathbf v_k^\top\mathbf x(0)$，$\bar x=\frac1N\sum_ix_i(0)$。平均值守恒，因为 $\frac{d}{dt}\mathbf 1^\top\mathbf x=-\mathbf 1^\top L\mathbf x=0$。

**第 3 步：收敛速度。** 偏差 $\boldsymbol\delta(t)=\mathbf x(t)-\bar x\mathbf 1$ 满足
$$
\|\boldsymbol\delta(t)\|^2=\sum_{k\ge2}e^{-2\mu_kt}c_k^2\le e^{-2\mu_2t}\|\boldsymbol\delta(0)\|^2 ,
$$
所以 $\mu_2$ 给出最慢的衰减速率；当 $\boldsymbol\delta(0)$ 在 $\mathbf v_2$ 上有分量时，长时间行为就由 $e^{-\mu_2t}$ 主导，$1/\mu_2$ 是达成共识的特征时间。由 Courant–Fischer 定理，$\mu_2=\min_{\mathbf x\perp\mathbf 1,\,\mathbf x\ne0}\dfrac{\mathbf x^\top L\mathbf x}{\mathbf x^\top\mathbf x}$：使这个比值小的 $\mathbf x$ 在两个“几乎不相连”的部分上取相反符号，所以存在“瓶颈”的网络 $\mu_2$ 小——这正是 Fiedler 向量可用于二分（见[社团结构与社区发现](community-structure.html)）的原因。对无权网络，Fiedler（1973）还给出上界 $\mu_2\le\frac{N}{N-1}k_{\min}$（$k_{\min}$ 为最小度），即一个度很低的节点就足以让共识变慢。

**第 4 步：Fiedler 上界的一行证明。** 设 $v$ 为度最小的节点，取 $\mathbf x=\mathbf e_v-\frac1N\mathbf 1$（与 $\mathbf 1$ 正交）。$\mathbf x^\top L\mathbf x=\mathbf e_v^\top L\mathbf e_v=k_{\min}$（$L\mathbf 1=0$），$\mathbf x^\top\mathbf x=1-\frac1N$，代入 Rayleigh 商即得 $\mu_2\le\frac{N}{N-1}k_{\min}$。

### C. 主稳定函数与特征值比

**假设**：$N$ 个**相同**的 $n$ 维系统，耦合函数 $\mathbf H$ 相同，$L$ 行和为零（保证同步流形 $\mathbf x_1=\cdots=\mathbf x_N=\mathbf s(t)$ 是不变集）且可对角化（无向网络自动满足）；只讨论局部（线性）稳定性。

**第 1 步：线性化。** 令 $\mathbf x_i=\mathbf s+\boldsymbol\xi_i$，$\dot{\mathbf s}=\mathbf F(\mathbf s)$，保留一阶项：
$$
\dot{\boldsymbol\xi}_i=D\mathbf F(\mathbf s)\,\boldsymbol\xi_i-\sigma\sum_jL_{ij}\,D\mathbf H(\mathbf s)\,\boldsymbol\xi_j .
$$
堆叠成 $\dot{\boldsymbol\xi}=\big[I_N\otimes D\mathbf F-\sigma\,L\otimes D\mathbf H\big]\boldsymbol\xi$。

**第 2 步：解耦。** 令 $L=V\Lambda V^\top$，作变换 $\boldsymbol\eta=(V^\top\otimes I_n)\boldsymbol\xi$。利用 Kronecker 积的混合乘积性质 $(V^\top\otimes I_n)(L\otimes D\mathbf H)(V\otimes I_n)=\Lambda\otimes D\mathbf H$，方程分解为 $N$ 个互不耦合的 $n$ 维方程：
$$
\dot{\boldsymbol\eta}_k=\big[D\mathbf F(\mathbf s)-\sigma\mu_k\,D\mathbf H(\mathbf s)\big]\boldsymbol\eta_k,\qquad k=1,\dots,N .
$$
$k=1$（$\mu_1=0$）对应沿同步流形本身的扰动，不影响同步。

**第 3 步：主稳定函数。** 对实参数 $\alpha$ 定义“主方程”$\dot{\boldsymbol\zeta}=[D\mathbf F(\mathbf s)-\alpha D\mathbf H(\mathbf s)]\boldsymbol\zeta$，其最大李雅普诺夫指数记为 $\Lambda(\alpha)$——它只依赖节点动力学与耦合方式，与网络无关。同步局部稳定当且仅当 $\Lambda(\sigma\mu_k)<0$ 对所有 $k=2,\dots,N$ 成立。若 $\Lambda(\alpha)<0$ 的区域是有限区间 $(\alpha_1,\alpha_2)$，需要 $\sigma\mu_2>\alpha_1$ 且 $\sigma\mu_N<\alpha_2$，存在这样的 $\sigma$ 当且仅当 $\mu_N/\mu_2<\alpha_2/\alpha_1$。若稳定区域是无界的 $(\alpha_1,\infty)$，则只需 $\sigma\mu_2>\alpha_1$，此时只有 $\mu_2$ 起作用。

**第 4 步：推广。** 有向或非对称耦合时，$L$ 的特征值 $\mu_k$ 可能为复数；若 $L$ 可对角化（$L=V\Lambda V^{-1}$），同样的变换给出 $\dot{\boldsymbol\eta}_k=[D\mathbf F-\sigma\mu_kD\mathbf H]\boldsymbol\eta_k$，只是 $\alpha$ 取复数，主稳定函数成为复平面上的函数 $\Lambda(\alpha_r+i\alpha_i)$，稳定条件变为所有 $\sigma\mu_k$ 落在复平面上的稳定区内。

### D. 洛伦兹分布下的 Ott–Antonsen 约化

Ott 与 Antonsen（2008，*Chaos*）发现，对 $N\to\infty$ 的全连接 Kuramoto 模型，振荡器相位密度 $f(\theta,\omega,t)$ 存在一个不变流形，其上傅里叶系数满足 $f_n=\alpha(\omega,t)^n$（几何级数）。在这一流形上，连续性方程化为关于 $\alpha$ 的单个方程：
$$
\dot\alpha=-i\omega\alpha+\frac K2\big(z^*-z\,\alpha^2\big),\qquad z^*=\int g(\omega)\,\alpha(\omega,t)\,d\omega ,
$$
其中 $z=re^{i\psi}$ 为序参量。对洛伦兹分布，积分可以用留数定理计算：把 $\alpha$ 解析延拓到 $\omega$ 的下半平面，只需在极点 $\omega=-i\gamma$ 处取值，得到 $z^*=\alpha(-i\gamma,t)$。代入上式（取 $\omega=-i\gamma$）并分离模长，得到关于 $r$ 的**一维常微分方程**：
$$
\dot r=-\gamma r+\frac K2\,r\,(1-r^2).
$$
它的不动点为 $r=0$ 与 $r^*=\sqrt{1-2\gamma/K}$（$K>2\gamma$），后者稳定。这与 A 节的自洽结果完全一致，但额外给出了**动力学**：$r(t)$ 如何随时间趋近稳态，以及 $r=0$ 在 $K<2\gamma$ 时稳定、在 $K>2\gamma$ 时失稳。Ott–Antonsen 约化是分析爆发式同步、奇异态（两组振荡器各自一个 $\alpha$）以及带外部驱动的 Kuramoto 模型的标准工具；它对带噪声的系统不严格成立。

### E. 簇同步的商网络

设节点划分 $\{\mathcal C_1,\dots,\mathcal C_q\}$ 是**等价划分**：对任意 $a,b$，$\mathcal C_a$ 中每个节点连向 $\mathcal C_b$ 的边权之和都等于同一个数 $Q_{ab}$。令 $\mathbf x_i=\mathbf y_a$（$i\in\mathcal C_a$），代入 $\dot{\mathbf x}_i=\mathbf F(\mathbf x_i)+\sigma\sum_jA_{ij}\mathbf H(\mathbf x_j)$（这里用邻接形式，拉普拉斯形式同理）：
$$
\dot{\mathbf y}_a=\mathbf F(\mathbf y_a)+\sigma\sum_{b=1}^{q}Q_{ab}\,\mathbf H(\mathbf y_b).
$$
右端对 $\mathcal C_a$ 内所有节点相同，所以“簇内相同”的子空间是不变的；簇同步的动力学由 $q$ 个节点的**商网络** $Q$ 描述。自同构轨道一定构成等价划分，反之不然。簇同步是否**稳定**，还需要对横向扰动做类似 C 节的线性化，Pecora 等（2014）用对称群的不可约表示把横向扰动分块，从而降低计算量。

### 算法

```text
算法 1  网络 Kuramoto 模拟与 K 扫描（含前向/后向扫描）
输入：A、ω、K 网格、步长 h、预热步数 T0、统计步数 T1
1. θ ← 均匀随机初值
2. for K in K 网格（前向：递增；后向：递减，从强同步态开始）:
3.     （沿用上一 K 的终态 θ，以观察滞后；若只要无滞后的曲线，可每次重新随机初值）
4.     for t = 1 … T0+T1:
5.         f(θ)_i = ω_i + K Σ_j A_ij sin(θ_j − θ_i)   # 稀疏：cosθ_i (A sinθ)_i − sinθ_i (A cosθ)_i
6.         用 RK4（或小步长欧拉）以步长 h 推进 θ
7.         if t > T0: 记录 r(t) = |Σ_j e^{iθ_j}| / N
8.     输出 K 与时间平均 ⟨r⟩（以及标准差，作为亚稳态度量）
```

复杂度：每次求右端为 $O(m)$（全连接时利用 $\sum_j\sin(\theta_j-\theta_i)=N r\sin(\psi-\theta_i)$ 可降为 $O(N)$），每个 $K$ 为 $O\big((T_0+T_1)\,m\big)$。判断同步时与[序参量](synchronization.kuramoto-model.html)的 $1/\sqrt N$ 基线比较；判断一级相变时比较前向与后向曲线（见[爆发式同步](synchronization.explosive-sync.html)）。

```text
算法 2  数值计算主稳定函数 Λ(α)
输入：F、DF、DH、α 网格、步长 h、积分时长、重归一化间隔 τ
1. 积分 ds/dt = F(s) 越过暂态，得到同步轨道上的初值 s0
2. for α in α 网格:
3.     s ← s0；ζ ← 随机单位向量；S ← 0
4.     同时积分 ds/dt = F(s) 与 dζ/dt = [DF(s) − α DH(s)] ζ
5.     每隔 τ：S ← S + ln‖ζ‖；ζ ← ζ/‖ζ‖
6.     Λ(α) ← S / 总积分时间
7. 在 Λ 变号处用二分法细化 α1、α2；对给定网络计算 μ2、μN 并检验 μN/μ2 < α2/α1
```

复杂度：MSF 只需对每个 $\alpha$ 积分一次 $n$ 维系统（$n$ 通常很小），与网络规模无关；网络部分只需求 $L$ 的两个极端特征值，稀疏网络用 Lanczos 方法即可。李雅普诺夫指数的估计误差随积分时长约按 $1/\sqrt T$ 减小，$\Lambda$ 接近 0 处的边界 $\alpha_1,\alpha_2$ 最不确定。

```text
算法 3  从多通道信号估计相位同步网络
输入：N 通道信号、频段 [f1, f2]、指标（PLV / PPC / wPLI …）、替代数据次数 S
1. 零相位带通滤波（如双向 Butterworth），去掉边缘若干周期
2. 希尔伯特变换得到 X_i(t) = A_i(t) e^{iφ_i(t)}
3. for 每对 (i, j):
4.     S_ij(t) = X_i(t) X_j(t)*；按定义计算指标 W_ij
5.     for s = 1 … S: 对 X_j 做随机循环平移（或相位随机化），重算指标，得零分布
6.     p_ij = 零分布中 ≥ W_ij 的比例
7. 多重比较校正（FDR 等）后得到网络；报告频段、数据长度、指标与参考方式
```

复杂度：$O(N^2T\,S)$。替代数据只能检验“两信号独立”这一零假设，不能排除共同源或容积传导（见[从实测信号估计同步](synchronization.phase-synchrony-estimation.html)的算例）。

## 研究前沿与开放问题 {#frontiers}

1. **大脑运行在同步的临界点附近吗？** 神经质量模型与 Kuramoto 类模型显示，脑网络在接近同步转变时能产生最丰富的“亚稳态”动力学，模拟 FC 也最接近实测（Deco 等 2017；Breakspear 2017 综述）。“临界性”在多大程度上是解释性的而非拟合的结果，如何用数据检验，仍有争论。

2. **结构连接能在多大程度上预测功能连接？** Honey 等（2009，*PNAS*）在结构连接组上模拟神经动力学，能部分重现静息态功能连接，但远非完全。动力学模型、间接通路和时间变化各自贡献多少，是连接组学的核心问题，也决定了“在结构网络上做虚拟手术”的可信度（见[结构–功能耦合](dynamic-brain-networks.sc-fc-coupling.html)）。

3. **癫痫发作的动力学本质。** Jirsa 等（2014，*Brain*）提出发作的开始与终止可用少数几种分岔类型刻画（“Epileptor”模型），这一框架后来被用于个体化脑网络建模以辅助术前评估。发作是全局过度同步还是局部网络的分岔传播，不同患者是否不同，仍需更多颅内记录验证。

4. **用刺激“去同步”。** 帕金森病的 β 振荡与病理性同步相关。Tass（2003，*Biological Cybernetics*）提出协调复位刺激，利用相位动力学让神经元群去同步，而非持续高频刺激；Little 等（2013，*Annals of Neurology*）报告了以 β 振幅为反馈信号的自适应深部脑刺激的初步临床结果。闭环、基于模型的脑刺激能否在临床上稳定优于传统 DBS，仍在研究中，这也是[网络可控性与稳定性](controllability.html)中“控制非线性网络”的现实版本。

5. **高阶相互作用与自适应网络。** 当耦合不止发生在成对节点之间（三体及更高阶相互作用），或者耦合强度本身随同步状态改变（类似突触可塑性），同步相变可以变为爆发式，并出现新的多稳态。这些机制在真实神经组织中是否起作用、怎样从数据识别，是活跃的研究方向。

6. **从同步测量反推网络。** 由多通道时间序列推断耦合结构（“网络重建”）面临共同输入、隐藏节点、容积传导和观测噪声等困难；把动力学模型与统计推断结合（如基于模型的有效连接）是一个重要方向。

## 生物医学应用 {#biomedical}

### 心脏起搏细胞

窦房结中的起搏细胞各自具有略有差异的固有频率，通过缝隙连接耦合后以统一节律放电，决定心率。Peskin（1975）最早用耦合振荡器解释起搏细胞的同步；Mirollo 与 Strogatz（1990，*SIAM Journal on Applied Mathematics*）证明了全连接、相同的脉冲耦合“积分–发放”振荡器几乎从任何初值出发都会同步。Michaels、Matyas 与 Jalife（1987，*Circulation Research*）根据实验与模拟提出，窦房结的节律不是由单个“主导起搏点”决定的，而是众多起搏细胞**相互牵引**（mutual entrainment）后形成的“协商”结果——这正是耦合振荡器同步的图景。

::: {.callout-bio}
**窦房结的同步**：在耦合振荡器图景中，整体心率接近各细胞固有频率的某种加权平均，单个细胞的异常不会轻易改变整体节律；但若耦合减弱（如缝隙连接蛋白表达改变、纤维化），同步可能部分瓦解，出现节律不齐。Glass（2001，*Nature*）综述了生理节律中的同步与动力学疾病。
:::

### 昼夜节律

下丘脑视交叉上核（SCN）是哺乳动物的主生物钟，由约 2 万个神经元组成。Welsh 等（1995，*Neuron*）把大鼠 SCN 神经元分散培养在多电极阵列上，发现单个神经元各自保持近 24 小时的放电节律，但相位彼此独立；Liu 等（1997，*Cell*）进一步发现分散的单个 SCN 神经元周期分布很宽，而完整组织表现出精确一致的节律。也就是说，**精确的整体节律来自不精确振荡器的耦合**。Aton 与 Herzog（2005，*Neuron*）综述了这种同步的细胞机制，其中神经肽 VIP 等信号起关键作用。

::: {.callout-bio}
**生物钟的网络同步**：SCN 正好对应“固有频率有分布的 Kuramoto 群体”——频率分散度 $g(0)$ 与耦合强度 $K$ 共同决定整体节律是否稳健。耦合使群体节律对单细胞噪声不敏感，这是网络同步带来鲁棒性的生物学实例；倒班与时差导致的节律紊乱，则可以用“外部光照驱动与内部耦合之间的竞争”来理解。
:::

### 大脑中的同步与疾病

神经振荡（α、β、γ 节律）是神经元群体同步的宏观表现，被认为参与信息的选择性路由。Uhlhaas 与 Singer（2006，*Neuron*）综述了多种脑疾病中的同步异常：

- **癫痫**：传统上被看作“过度同步”，但颅内记录显示更复杂的图景。Schindler 等（2007，*Brain*）分析多通道颅内 EEG 的相关结构，发现发作前半段全局相关性反而降低，在接近发作结束时显著升高，提示同步增强可能参与发作终止（Jiruska 等 2013，*Journal of Physiology* 综述了这一争议）。Jirsa 等（2014）的 Epileptor 模型从分岔角度描述发作的开始与终止。
- **帕金森病**：基底节–皮层环路中 β 频段（约 13–30 Hz）振荡同步异常增强，与运动迟缓和僵直相关（Hammond、Bergman 与 Brown 2007，*Trends in Neurosciences*）；深部脑刺激被认为部分通过干扰这种病理同步起作用。
- **精神分裂症**：多项研究报告 γ 频段同步降低，与认知整合障碍有关。

::: {.callout-bio}
**帕金森病的病理性 β 同步与闭环刺激**：既然症状与 β 同步相关，就可以把 β 振幅作为“同步程度”的实时读数，只在同步增强时施加刺激。Little 等（2013）在少数患者中报告了这种自适应 DBS 的初步结果；Tass（2003）的协调复位则从相位动力学出发，主张用分时、分点的刺激把同步群体打散。二者都把同步动力学理论直接转化为治疗设计。
:::

### 从模型到数据

在 EEG/MEG/颅内记录分析中，常用锁相值、相位滞后指数等度量两个信号的相位同步（见[从实测信号估计同步](synchronization.phase-synchrony-estimation.html)）；PLV 本质上是相位差的 Kuramoto 序参量：$\text{PLV}=\left|\frac1T\sum_t e^{i(\phi_1(t)-\phi_2(t))}\right|$。将 Kuramoto 振荡器或 Hopf 振荡器放在人脑结构连接组上模拟，可以部分重现静息态功能连接的格局（Cabral 等 2011；Deco 等 2017），这是“结构–动力学–功能”研究路线的代表，详见[神经质量模型与全脑模型](synchronization.whole-brain-models.html)、[脑连接组：结构与功能连接](brain-connectome.html)与[动态功能连接与多层脑网络](dynamic-brain-networks.html)。

::: {.callout-bio}
模型只是工具：脑电中测得的高 PLV 可能来自共同参考电极或容积传导，而非真实的神经元同步。分析时应采用对零滞后不敏感的指标（如相位滞后指数、虚部相干）或源空间分析，相关方法学问题见[EEG/MEG 网络与微状态](dynamic-brain-networks.electrophysiology.html)。
:::

## 适用范围与常见误用 {#limitations}

1. **误用**：把同步理解为所有节点状态完全相同。→ **正解**：有完全同步、相位同步、频率锁定、广义同步、簇同步等多种类型；Kuramoto 模型中 $K>K_c$ 时通常是**部分**同步，固有频率极端的振荡器仍在漂移。
2. **误用**：序参量 $r$ 只要大于 0 就判定为同步。→ **正解**：有限系统的随机相位也有 $r\sim1/\sqrt N$；需要与基线比较并取时间平均。反过来，$r\approx0$ 也可能是两个反相簇。
3. **误用**：认为无标度网络既最容易开始同步，也最容易保持完全同步。→ **正解**：度异质性降低 Kuramoto 的 $K_c$，但会增大特征值比 $\mu_N/\mu_2$，使相同振荡器的完全同步更难稳定。
4. **误用**：加边（尤其是长程边）一定提高可同步性。→ **正解**：加边不会使拉普拉斯特征值减小，但可能只抬高 $\mu_N$ 而不改变 $\mu_2$（谱简并时），使特征值比变大；需要直接计算。
5. **误用**：把 MSF 结论直接套用到参数各异的真实振荡器或强非线性的大扰动情形。→ **正解**：MSF 只针对相同振荡器、只给出局部稳定性。
6. **误用**：$r(K)$ 曲线很陡就宣称“爆发式同步”。→ **正解**：要做前向/后向扫描检查滞后，并考察有限尺度效应。
7. **误用**：认为对大脑而言同步越强越好。→ **正解**：功能需要分离与整合的平衡；过度同步（癫痫）与同步不足（如精神分裂症中的 γ 同步降低）都与疾病相关；全脑模型中最符合数据的工作点通常在中等耦合。
8. **误用**：两个脑区信号同步，就推断它们之间有直接连接。→ **正解**：同步可以通过间接路径、远程同步（对称位置）、共同输入甚至测量伪迹（容积传导、共同参考）产生；功能同步不等于结构连接。
9. **误用**：替代数据检验显著，就认为排除了伪迹。→ **正解**：循环平移、相位随机化等替代数据只检验“相互独立”，容积传导产生的零滞后相关同样能通过检验。
10. **误用**：全脑模型拟合 FC 较好，就认为模型参数（如耦合强度、传导速度）得到了“测量”。→ **正解**：多组参数常常拟合得同样好，需要报告参数不确定性并在独立数据上检验预测。

适用范围方面：$K_c=2/(\pi g(0))$ 的推导假设全连接、$N\to\infty$、单峰对称的频率分布，只回答稳态解是否存在；网络阈值公式是平均场近似，在稀疏、有强社团或强度相关的网络上可能有较大偏差；主稳定函数只适用于**相同**振荡器、只给出局部（线性）稳定性（见[数学推导与算法](synchronization.derivations.html)）。

## 关联知识 {#related}

- [网络上的传播与免疫](spreading.html)：异质平均场方法与 $\langle k\rangle/\langle k^2\rangle$ 型阈值的来源，同步阈值与传播阈值形式相同。
- [网络结构指标与随机图](network-metrics.html)：度分布、邻接矩阵与拉普拉斯矩阵是同步分析的基本对象。
- [小世界与无标度网络模型](network-models.html)：小世界捷径降低特征值比、利于同步；度异质性带来“早开始、难稳定”的两面性。
- [社团结构与社区发现](community-structure.html)：分层同步可用于发现社团；Fiedler 向量与谱二分；簇同步与网络对称性。
- [网络可控性与稳定性](controllability.html)：主稳定函数是平衡态线性稳定性分析在同步态上的应用；去同步刺激与网络控制问题相关。
- [脑连接组：结构与功能连接](brain-connectome.html)：在结构连接组上模拟耦合振荡器与 Hopf 模型，重现静息态功能连接。
- [动态功能连接与多层脑网络](dynamic-brain-networks.html)：锁相值、相位滞后指数等同步指标构成的功能网络、容积传导与结构–功能耦合。

## 核心文献 {#references}

### Strogatz 2000：From Kuramoto to Crawford（Physica D）

- **背景**：Kuramoto 模型提出后 25 年，其稳定性分析一直存在难点。Strogatz 以讲故事的方式回顾了这一问题的来龙去脉。
- **核心内容**：平均场自洽推导 $K_c=2/(\pi g(0))$；锁定与漂移振荡器的划分；不相干态在 $K<K_c$ 时为何是“中性稳定”的；Crawford 等人的工作如何解释临界点附近的标度律。
- **阅读要点**：先读第 1–4 节，跟着推导一遍自洽方程。重点理解“漂移振荡器为何对序参量没有净贡献”。
- **延伸思考**：如果 $g(\omega)$ 是双峰分布（两群振荡器频率不同），预计会出现什么样的同步行为？

DOI：[10.1016/S0167-2789(00)00094-4](https://doi.org/10.1016/S0167-2789%2800%2900094-4)

### Arenas 等 2008：Synchronization in complex networks（Physics Reports）

- **背景**：2000 年后，网络科学与同步研究交汇，产生了大量结果。这篇综述是该领域的标准参考。
- **核心内容**：网络 Kuramoto 模型的平均场理论；主稳定函数与特征值比；小世界、无标度、加权与模块化网络上的同步；同步与社团发现；在生物、通信等系统中的应用。
- **阅读要点**：篇幅很长，建议先读引言和第 2–4 章的结构，按需深入。注意区分“相同振荡器的完全同步”和“非相同振荡器的相位同步”这两条研究线。
- **延伸思考**：如果想通过增加少量边来提高一个网络的可同步性，按 MSF 框架应该优化哪个量？这对脑网络的“长程连接”有何启示？

DOI：[10.1016/j.physrep.2008.09.002](https://doi.org/10.1016/j.physrep.2008.09.002)；精读：[Arenas 2008](paper-arenas2008_sync.html)

### Pecora 与 Carroll 1998：Master stability functions for synchronized coupled systems（PRL）

- **背景**：混沌系统可以同步（Pecora 与 Carroll 1990 年代初的工作），但不同网络、不同耦合方式下同步是否稳定，需要逐一计算。
- **核心内容**：在同步态附近按拉普拉斯特征向量把扰动解耦，提出只依赖节点动力学和耦合方式的主稳定函数，把网络结构的作用归结为 $\sigma\mu_k$ 是否落在稳定区。
- **阅读要点**：论文很短，重点看分块对角化那一步和对 Rössler 振子稳定区的讨论，对照[数学推导与算法](synchronization.derivations.html) C 节。
- **延伸思考**：如果耦合通过 $y$ 分量而不是 $x$ 分量，稳定区会怎样变化？对神经元模型，“通过哪个变量耦合”对应什么生理机制？

DOI：[10.1103/PhysRevLett.80.2109](https://doi.org/10.1103/PhysRevLett.80.2109)

### Rodrigues 等 2016：The Kuramoto model in complex networks（Physics Reports）

- **背景**：Arenas 等 2008 之后，网络 Kuramoto 模型的研究迅速扩展：爆发式同步、带惯性的模型（电网）、Ott–Antonsen 约化、多层网络等。
- **核心内容**：网络上同步起点的各种近似、同步路径、度–频率关联与爆发式同步、噪声与惯性的影响、在工程（电网）、神经科学与地球科学中的应用及开放问题。
- **阅读要点**：可作为工具书查阅，先读引言和网络阈值部分，再按需选读爆发式同步与神经科学应用章节。

DOI：[10.1016/j.physrep.2015.10.008](https://doi.org/10.1016/j.physrep.2015.10.008)

### Breakspear 2017：Dynamic models of large-scale brain activity（Nature Neuroscience）

- **背景**：脑成像产生了大量结构与功能连接数据，需要动力学模型把二者联系起来。
- **核心内容**：从神经质量模型、神经场模型到全脑网络模型的建模层级；多稳态、亚稳态、临界性等动力学概念；模型与 fMRI、EEG/MEG 数据的对接方式及其局限。
- **阅读要点**：重点理解模型层级的划分与每一层的假设，对照[神经质量模型与全脑模型](synchronization.whole-brain-models.html)。
- **延伸思考**：如果两个不同的全脑模型拟合同一份 FC 数据同样好，还能用什么数据或实验区分它们？

DOI：[10.1038/nn.4497](https://doi.org/10.1038/nn.4497)

### Uhlhaas 与 Singer 2006：Neural synchrony in brain disorders（Neuron）

- **背景**：神经振荡与同步被认为是大脑整合分布式信息的机制之一，那么疾病是否表现为同步异常？
- **核心内容**：综述精神分裂症、癫痫、孤独症、阿尔茨海默病、帕金森病等疾病中神经同步的改变，提出同步异常可能是多种疾病的共同病理生理基础。
- **阅读要点**：区分“同步增强”与“同步减弱”对应的疾病；关注各研究使用的同步指标和记录方式（EEG、MEG、颅内记录），想一想哪些结论可能受测量方法影响。
- **延伸思考**：如果用 Kuramoto 模型模拟“病理性过度同步”，应调整哪个参数？治疗（如深部脑刺激）在模型中可以对应什么操作？

DOI：[10.1016/j.neuron.2006.09.020](https://doi.org/10.1016/j.neuron.2006.09.020)

### 其他引用文献

**综述与专著**

- Boccaletti S, Latora V, Moreno Y, Chavez M, Hwang D-U. Complex networks: Structure and dynamics. *Physics Reports* 2006. [10.1016/j.physrep.2005.10.009](https://doi.org/10.1016/j.physrep.2005.10.009)
- Acebrón JA 等. The Kuramoto model: A simple paradigm for synchronization phenomena. *Rev Mod Phys* 2005. [10.1103/RevModPhys.77.137](https://doi.org/10.1103/RevModPhys.77.137)
- Pikovsky A, Rosenblum M, Kurths J. *Synchronization: A Universal Concept in Nonlinear Sciences*. Cambridge University Press 2001. [10.1017/CBO9780511755743](https://doi.org/10.1017/CBO9780511755743)
- Boccaletti S 等. Explosive transitions in complex networks' structure and dynamics: Percolation and synchronization. *Physics Reports* 2016. [10.1016/j.physrep.2016.10.004](https://doi.org/10.1016/j.physrep.2016.10.004)
- Panaggio MJ, Abrams DM. Chimera states: coexistence of coherence and incoherence in networks of coupled oscillators. *Nonlinearity* 2015. [10.1088/0951-7715/28/3/R67](https://doi.org/10.1088/0951-7715/28/3/R67)
- Glass L. Synchronization and rhythmic processes in physiology. *Nature* 2001. [10.1038/35065745](https://doi.org/10.1038/35065745)
- Olfati-Saber R, Fax JA, Murray RM. Consensus and cooperation in networked multi-agent systems. *Proc IEEE* 2007. [10.1109/JPROC.2006.887293](https://doi.org/10.1109/JPROC.2006.887293)

**理论**

- Fiedler M. Algebraic connectivity of graphs. *Czechoslovak Math J* 1973. [10.21136/CMJ.1973.101168](https://doi.org/10.21136/CMJ.1973.101168)
- Ichinomiya T. Frequency synchronization in a random oscillator network. *PRE* 2004. [10.1103/PhysRevE.70.026116](https://doi.org/10.1103/PhysRevE.70.026116)
- Restrepo JG, Ott E, Hunt BR. Onset of synchronization in large networks of coupled oscillators. *PRE* 2005. [10.1103/PhysRevE.71.036151](https://doi.org/10.1103/PhysRevE.71.036151)
- Barahona M, Pecora LM. Synchronization in small-world systems. *PRL* 2002. [10.1103/PhysRevLett.89.054101](https://doi.org/10.1103/PhysRevLett.89.054101)
- Nishikawa T 等. Heterogeneity in oscillator networks: Are smaller worlds easier to synchronize? *PRL* 2003. [10.1103/PhysRevLett.91.014101](https://doi.org/10.1103/PhysRevLett.91.014101)
- Arenas A, Díaz-Guilera A, Pérez-Vicente CJ. Synchronization reveals topological scales in complex networks. *PRL* 2006. [10.1103/PhysRevLett.96.114102](https://doi.org/10.1103/PhysRevLett.96.114102)
- Gómez-Gardeñes J, Gómez S, Arenas A, Moreno Y. Explosive synchronization transitions in scale-free networks. *PRL* 2011. [10.1103/PhysRevLett.106.128701](https://doi.org/10.1103/PhysRevLett.106.128701)
- Abrams DM, Strogatz SH. Chimera states for coupled oscillators. *PRL* 2004. [10.1103/PhysRevLett.93.174102](https://doi.org/10.1103/PhysRevLett.93.174102)
- Kuramoto Y, Battogtokh D. Coexistence of coherence and incoherence in nonlocally coupled phase oscillators. *Nonlinear Phenomena in Complex Systems* 2002.
- Pecora LM 等. Cluster synchronization and isolated desynchronization in complex networks with symmetries. *Nat Commun* 2014. [10.1038/ncomms5079](https://doi.org/10.1038/ncomms5079)
- Sorrentino F 等. Complete characterization of the stability of cluster synchronization in complex dynamical networks. *Sci Adv* 2016. [10.1126/sciadv.1501737](https://doi.org/10.1126/sciadv.1501737)
- Nicosia V 等. Remote synchronization reveals network symmetries and functional modules. *PRL* 2013. [10.1103/PhysRevLett.110.174102](https://doi.org/10.1103/PhysRevLett.110.174102)
- Yeung MKS, Strogatz SH. Time delay in the Kuramoto model of coupled oscillators. *PRL* 1999. [10.1103/PhysRevLett.82.648](https://doi.org/10.1103/PhysRevLett.82.648)
- Sakaguchi H. Cooperative phenomena in coupled oscillator systems under external fields. *Prog Theor Phys* 1988. [10.1143/PTP.79.39](https://doi.org/10.1143/PTP.79.39)
- Strogatz SH, Mirollo RE. Stability of incoherence in a population of coupled oscillators. *J Stat Phys* 1991. [10.1007/BF01029202](https://doi.org/10.1007/BF01029202)
- Ott E, Antonsen TM. Low dimensional behavior of large systems of globally coupled oscillators. *Chaos* 2008. [10.1063/1.2930766](https://doi.org/10.1063/1.2930766)
- Mirollo RE, Strogatz SH. Synchronization of pulse-coupled biological oscillators. *SIAM J Appl Math* 1990. [10.1137/0150098](https://doi.org/10.1137/0150098)

**脑动力学模型**

- Wilson HR, Cowan JD. Excitatory and inhibitory interactions in localized populations of model neurons. *Biophys J* 1972. [10.1016/S0006-3495(72)86068-5](https://doi.org/10.1016/S0006-3495%2872%2986068-5)
- Honey CJ 等. Predicting human resting-state functional connectivity from structural connectivity. *PNAS* 2009. [10.1073/pnas.0811168106](https://doi.org/10.1073/pnas.0811168106)
- Cabral J, Hugues E, Sporns O, Deco G. Role of local network oscillations in resting-state functional connectivity. *NeuroImage* 2011. [10.1016/j.neuroimage.2011.04.010](https://doi.org/10.1016/j.neuroimage.2011.04.010)
- Deco G 等. The dynamics of resting fluctuations in the brain: metastability and its dynamical cortical core. *Sci Rep* 2017. [10.1038/s41598-017-03073-5](https://doi.org/10.1038/s41598-017-03073-5)
- Sanz Leon P 等. The Virtual Brain: a simulator of primate brain network dynamics. *Front Neuroinform* 2013. [10.3389/fninf.2013.00010](https://doi.org/10.3389/fninf.2013.00010)
- Shanahan M. Metastable chimera states in community-structured oscillator networks. *Chaos* 2010. [10.1063/1.3305451](https://doi.org/10.1063/1.3305451)
- Kim M 等. Functional and topological conditions for explosive synchronization develop in human brain networks with the onset of anesthetic-induced unconsciousness. *Front Comput Neurosci* 2016. [10.3389/fncom.2016.00001](https://doi.org/10.3389/fncom.2016.00001)

**相位同步的估计**

- Lachaux J-P 等. Measuring phase synchrony in brain signals. *Hum Brain Mapp* 1999. [10.1002/(SICI)1097-0193(1999)8:4<194::AID-HBM4>3.0.CO;2-C](https://doi.org/10.1002/(SICI)1097-0193(1999)8:4%3C194::AID-HBM4%3E3.0.CO;2-C)
- Nolte G 等. Identifying true brain interaction from EEG data using the imaginary part of coherency. *Clin Neurophysiol* 2004. [10.1016/j.clinph.2004.04.029](https://doi.org/10.1016/j.clinph.2004.04.029)
- Stam CJ, Nolte G, Daffertshofer A. Phase lag index: assessment of functional connectivity from multi channel EEG and MEG with diminished bias from common sources. *Hum Brain Mapp* 2007. [10.1002/hbm.20346](https://doi.org/10.1002/hbm.20346)
- Vinck M 等. The pairwise phase consistency: a bias-free measure of rhythmic neuronal synchronization. *NeuroImage* 2010. [10.1016/j.neuroimage.2010.01.073](https://doi.org/10.1016/j.neuroimage.2010.01.073)
- Vinck M 等. An improved index of phase-synchronization for electrophysiological data in the presence of volume-conduction, noise and sample-size bias. *NeuroImage* 2011. [10.1016/j.neuroimage.2011.01.055](https://doi.org/10.1016/j.neuroimage.2011.01.055)
- Bastos AM, Schoffelen J-M. A tutorial review of functional connectivity analysis methods and their interpretational pitfalls. *Front Syst Neurosci* 2016. [10.3389/fnsys.2015.00175](https://doi.org/10.3389/fnsys.2015.00175)

**生物医学实例**

- Michaels DC, Matyas EP, Jalife J. Mechanisms of sinoatrial pacemaker synchronization: a new hypothesis. *Circ Res* 1987. [10.1161/01.RES.61.5.704](https://doi.org/10.1161/01.RES.61.5.704)
- Welsh DK 等. Individual neurons dissociated from rat suprachiasmatic nucleus express independently phased circadian firing rhythms. *Neuron* 1995. [10.1016/0896-6273(95)90214-7](https://doi.org/10.1016/0896-6273%2895%2990214-7)
- Liu C, Weaver DR, Strogatz SH, Reppert SM. Cellular construction of a circadian clock: period determination in the suprachiasmatic nuclei. *Cell* 1997. [10.1016/S0092-8674(00)80473-0](https://doi.org/10.1016/S0092-8674%2800%2980473-0)
- Aton SJ, Herzog ED. Come together, right…now: synchronization of rhythms in a mammalian circadian clock. *Neuron* 2005. [10.1016/j.neuron.2005.11.001](https://doi.org/10.1016/j.neuron.2005.11.001)
- Schindler K 等. Assessing seizure dynamics by analysing the correlation structure of multichannel intracranial EEG. *Brain* 2007. [10.1093/brain/awl304](https://doi.org/10.1093/brain/awl304)
- Jiruska P 等. Synchronization and desynchronization in epilepsy: controversies and hypotheses. *J Physiol* 2013. [10.1113/jphysiol.2012.239590](https://doi.org/10.1113/jphysiol.2012.239590)
- Jirsa VK 等. On the nature of seizure dynamics. *Brain* 2014. [10.1093/brain/awu133](https://doi.org/10.1093/brain/awu133)
- Hammond C, Bergman H, Brown P. Pathological synchronization in Parkinson's disease: networks, models and treatments. *Trends Neurosci* 2007. [10.1016/j.tins.2007.05.004](https://doi.org/10.1016/j.tins.2007.05.004)
- Tass PA. A model of desynchronizing deep brain stimulation with a demand-controlled coordinated reset of neural subpopulations. *Biol Cybern* 2003. [10.1007/s00422-003-0425-7](https://doi.org/10.1007/s00422-003-0425-7)
- Little S 等. Adaptive deep brain stimulation in advanced Parkinson disease. *Ann Neurol* 2013. [10.1002/ana.23951](https://doi.org/10.1002/ana.23951)
- Rattenborg NC, Amlaner CJ, Lima SL. Behavioral, neurophysiological and evolutionary perspectives on unihemispheric sleep. *Neurosci Biobehav Rev* 2000. [10.1016/S0149-7634(00)00039-7](https://doi.org/10.1016/S0149-7634%2800%2900039-7)

## 延伸资源 {#resources}

| 类型 | 资源 | 说明 |
|---|---|---|
| 中文视频 | Veritasium 真理元素：同步之秘【官方双语】（[B 站](https://www.bilibili.com/video/BV1zV411n7Nz/)） | 萤火虫、节拍器、千禧桥，引出 Kuramoto 模型；正片约 20 分钟 |
| 交互演示 | Complexity Explorables：Ride my Kuramotocycle!（[链接](https://www.complexity-explorables.org/explorables/ride-my-kuramotocycle/)） | 调节耦合强度与频率分布，实时观察序参量与同步相变 |
| 开放教材 | Sayama《Introduction to the Modeling and Analysis of Complex Systems》第 18 章（[LibreTexts](https://math.libretexts.org/Bookshelves/Scientific_Computing_Simulations_and_Modeling/Introduction_to_the_Modeling_and_Analysis_of_Complex_Systems_(Sayama)/18%3A_Dynamical_Networks_III__Analysis_of_Network_Dynamics)） | 拉普拉斯谱与可同步性（18.3 节），附 Python 代码；CC BY-NC-SA |
| 开放教材 | Barabási《Network Science》第 10 章 Spreading Phenomena（[链接](http://networksciencebook.com/chapter/10)） | 该书没有同步专章；第 10 章的异质平均场与 $\langle k\rangle/\langle k^2\rangle$ 阈值可与[网络拓扑与同步阈值](synchronization.network-kuramoto.html)对照 |
| 论文 | Strogatz 2000, From Kuramoto to Crawford, Physica D（[DOI](https://doi.org/10.1016/S0167-2789%2800%2900094-4)） | 见核心文献，Kuramoto 模型最好的教学性综述 |
| 综述 | Acebrón 等 2005, The Kuramoto model, Rev Mod Phys（[DOI](https://doi.org/10.1103/RevModPhys.77.137)） | 完整的数学综述，第 2 节平均场推导可对照[Kuramoto 模型与序参量](synchronization.kuramoto-model.html) |
| 综述 | Arenas 等 2008, Synchronization in complex networks, Physics Reports（[DOI](https://doi.org/10.1016/j.physrep.2008.09.002)） | 网络同步的标准参考，见核心文献 |
| 综述 | Rodrigues 等 2016, The Kuramoto model in complex networks, Physics Reports（[arXiv:1511.07139](https://arxiv.org/abs/1511.07139)） | 开放预印本，覆盖爆发式同步、噪声与惯性、Ott–Antonsen 约化 |
| 综述 | Boccaletti 等 2006, Complex networks: Structure and dynamics, Physics Reports（[DOI](https://doi.org/10.1016/j.physrep.2005.10.009)） | 结构与动力学的综合综述，同步部分对 MSF 类型有清晰归纳 |
| 科普书 | Strogatz《Sync: The Emerging Science of Spontaneous Order》（2003） | 从萤火虫、起搏细胞、生物钟到约瑟夫森结的非技术性介绍，适合建立整体图景 |
| 软件 | The Virtual Brain（[thevirtualbrain.org](https://www.thevirtualbrain.org/)） | 开源全脑建模平台，内置多种神经质量模型与连接组 |
| 软件 | MNE-Python Connectivity（[mne-connectivity](https://mne.tools/mne-connectivity/)） | EEG/MEG 的 PLV、PLI、wPLI、相干等指标的标准实现 |
| 论文（生物医学） | Jiruska 等 2013, Synchronization and desynchronization in epilepsy, J Physiol（[DOI](https://doi.org/10.1113/jphysiol.2012.239590)） | 癫痫中同步与去同步的争议与假说，对应[生物医学应用](synchronization.biomedical.html) |
| 英文视频 | LMU Physics of Life：The Kuramoto Model & Synchronization Transition（[YouTube](https://www.youtube.com/watch?v=ywd7jVIubOo)） | 约 50 分钟的大学讲座，完整推导同步相变，适合想跟一遍数学的读者；需境外网络 |

> 提示：Barabási《Network Science》在线版需加载境外脚本，在中国大陆可能无法正常显示；标注“需境外网络”的为 YouTube 资源。

## 开放问题 {#questions}

1. 在你的研究方向中（如脑电、心电、细胞钙振荡、生物钟、基因表达振荡），有没有可以看作“耦合振荡器”的系统？其中“耦合”由什么物理或生物机制实现？应该用什么指标度量同步？
2. 深部脑刺激的一种思路是“去同步化”。请用同步动力学的语言（耦合强度、序参量、网络结构）描述：若要用最少的刺激点打破一个病理性同步簇，应选择网络中的哪些节点？这个问题和[网络可控性与稳定性](controllability.html)中的网络控制问题有什么联系？
3. 某研究报告患者组的 EEG α 频段 PLV 网络“全局效率升高”。在接受这一结论之前，你会检查哪些方法学因素（数据长度、参考电极、容积传导、指标选择、信噪比差异）？换用 wPLI 后结论若消失，说明了什么？
4. 全脑模型中，若最符合数据的全局耦合强度在患者组更低，这能否解释为“患者的结构连接更弱”？还有哪些模型参数或数据差异可以产生同样的结果？
