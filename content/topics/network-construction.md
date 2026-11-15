---
id: network-construction
title: 网络构建与统计验证
en: Network construction and statistical validation
domain: theory
legacy: ""
summary: 从影像、量表、表达谱和相互作用数据库到网络，再到可信结论：节点与边的定义、连接估计、阈值、零模型、统计推断与稳定性检验。
keywords: [网络构建, 功能连接, 偏相关, 阈值化, 零模型, 置换检验, 多重比较, 稳定性, 研究偏倚, Granger 因果, 转移熵, 采样网络, 不确定性传播, 统计功效, 网络距离]
synonyms: [network construction, network inference, 网络推断, 网络重建, network reconstruction, 边估计, edge estimation, 连接估计, connectivity estimation, 相关网络, correlation network, 偏相关, partial correlation, 精度矩阵, precision matrix, 高斯图模型, Gaussian graphical model, GGM, 图形 LASSO, graphical lasso, glasso, EBICglasso, 正则化偏相关, regularized partial correlation, 收缩估计, shrinkage, Ledoit-Wolf, 互信息, mutual information, MI, Fisher z, Fisher z 变换, artanh, 阈值, 阈值化, thresholding, 绝对阈值, absolute threshold, 比例阈值, proportional threshold, 密度阈值, 网络密度, density, cost, 密度匹配, density matching, 成本积分, cost integration, AUC, 最小生成树, minimum spanning tree, MST, 加权网络, weighted network, 稀疏化, sparsification, 零模型, null model, 空模型, 参照模型, 随机化, randomization, ER 随机图, Erdős–Rényi, 保度随机化, degree-preserving randomization, 度保持随机化, 边交换, 双边交换, double edge swap, edge swap, rewiring, 重连, Maslov–Sneppen, 配置模型, configuration model, 空间零模型, spatial null model, spin test, 旋转检验, BrainSMASH, 权重保持零模型, z 分数, z-score, 经验 p 值, empirical p-value, 置换检验, permutation test, 随机化检验, 非参数检验, 网络统计量, 基于网络的统计, NBS, network-based statistic, 族错误率, FWE, family-wise error, 错误发现率, FDR, false discovery rate, Benjamini–Hochberg, BH, 多重比较, multiple comparisons, 网络比较检验, NCT, network comparison test, 组间网络比较, 研究偏倚, study bias, 注释偏倚, annotation bias, 度偏倚, degree bias, 不完整相互作用组, incomplete interactome, 头动, head motion, framewise displacement, FD, 伪迹, artifact, 全局信号回归, GSR, bootstrap, 自助法, 重抽样, resampling, 病例删除, case-dropping, CS 系数, correlation stability coefficient, 留一法, leave-one-out, jackknife, 刀切法, 重测信度, test-retest reliability, 组内相关系数, ICC, 可重复性, reproducibility, replicability, 稳定性选择, stability selection, 敏感性分析, sensitivity analysis, 有向边, 有向功能连接, directed functional connectivity, 有效连接, effective connectivity, Granger 因果, Granger causality, GC, 条件 Granger 因果, conditional Granger causality, 谱 Granger 因果, 向量自回归, vector autoregression, VAR, 转移熵, transfer entropy, TE, 动态因果模型, dynamic causal modelling, DCM, 容积传导, volume conduction, 降采样, downsampling, 采样网络, sampled network, 子网采样, subnet sampling, 节点采样, node sampling, 边采样, edge sampling, 滚雪球采样, snowball sampling, 快照偏倚, 不完整观测, incomplete observation, 假阳性边, 假阴性边, false positive edge, false negative edge, 相互作用组大小, interactome size, 贝叶斯网络重建, Bayesian network reconstruction, 期望最大化, EM, 不确定性传播, uncertainty propagation, delta 方法, delta method, 块 bootstrap, block bootstrap, 概率网络, probabilistic network, 共识网络, consensus network, 边入选概率, 样本量, sample size, 统计功效, statistical power, 功效分析, power analysis, 信度衰减, attenuation, 扫描时长, scan length, 网络比较, network comparison, 网络距离, graph distance, 汉明距离, Hamming distance, Jaccard 距离, 谱距离, spectral distance, 拉普拉斯谱, Laplacian spectrum, 同谱图, cospectral graphs, 图核, graph kernel, Weisfeiler–Lehman, WL 核, 小图, graphlet, GDD, 网络肖像散度, portrait divergence, DeltaCon, 节点对应, node correspondence, KNC, UNC, 集合内图距离, within-ensemble graph distance]
demos: [brain_threshold, symptom]
reviewed: 2026-11-15
---

## 概述 {#overview}

网络分析中最容易被低估的一步，是“网络从哪里来”。一个脑网络、症状网络、共表达网络或蛋白质相互作用网络，都不是直接测量得到的对象，而是一连串建模决定的产物：什么算一个节点，什么算一条边，边权用什么统计量估计，保留哪些边，和什么样的参照对象比较，用什么方法控制假阳性。每一步都可能改变后面所有的拓扑指标，因此“网络构建”本身就是一个需要报告、检验和论证的统计推断问题。

这一专题按数据流程组织：先讨论不同数据类型中节点与边的含义（[节点与边的定义](network-construction.nodes-and-edges.html)），再讨论边权的估计与估计误差（[连接强度的估计](network-construction.edge-estimation.html)）、从时间序列推断方向（[从时间序列推断有向边](network-construction.directed-edges.html)）、从稠密矩阵到网络的稀疏化（[阈值、加权与稀疏化](network-construction.thresholding.html)）、边权误差如何传到指标上（[边权不确定性向网络指标的传播](network-construction.uncertainty-propagation.html)），然后是三类验证：与零模型比较（[零模型与空模型](network-construction.null-models.html)）、组间比较与多重比较控制（[统计推断与多重比较](network-construction.statistical-inference.html)、[网络之间的距离与相似性](network-construction.network-distances.html)）、对数据缺陷与结果稳定性的检查（[测量误差、缺失与偏倚](network-construction.bias-and-missingness.html)、[采样网络与不完整观测](network-construction.sampling-incomplete.html)、[稳定性与可重复性](network-construction.stability-reproducibility.html)），以及研究设计阶段的 [样本量与统计功效](network-construction.sample-size-power.html)。

它与 [网络结构指标与随机图](network-metrics.html) 互为前后：后者定义指标，这里讨论指标在什么条件下可以被解释。各应用领域的具体流程分别见 [脑连接组](brain-connectome.html)、[症状网络](symptom-networks.html)、[基因调控网络推断](gene-network-inference.html) 与 [网络医学](network-medicine.html)；分析报告的规范见 [可复现分析与敏感性分析](reproducible-research.html)。

## 节点与边的定义 {#nodes-and-edges}

### 节点：分析单元的选择

节点（node）是研究者选定的分析单元。它要求单元内部足够同质、单元之间可以区分，并且在不同个体或样本之间可以对应。

| 数据类型 | 常见节点 | 典型的节点定义问题 |
|---|---|---|
| 结构/功能 MRI | 脑图谱中的脑区（ROI）、体素、皮层顶点 | 图谱分辨率；群体图谱与个体功能边界不一致 |
| 电生理（EEG/MEG） | 电极、源空间脑区 | 容积传导使相邻电极信号混合 |
| 量表与症状评估 | 条目或症状 | 条目内容重叠；条目与潜变量的关系 |
| 转录组 | 基因、转录本、模块特征基因 | 低表达基因噪声大；细胞组成混杂 |
| 相互作用数据库 | 蛋白质、基因、代谢物、药物、疾病 | 同一基因的多个蛋白异构体被合并；命名映射丢失 |

节点定义会直接改变网络指标。Zalesky 等（2010, *NeuroImage*）用同一批弥散数据、不同分辨率的脑区划分构建结构网络，发现小世界性、度分布等指标随节点尺度系统变化。因此跨研究比较指标的绝对值意义有限，同一流程下的相对比较更可靠。

### 边：四种不同性质的关系

“边”这个词在不同数据中指代性质完全不同的关系，混用会导致解释错误。

::: {.callout-def}
**物理连接**（physical connection）：两个对象之间存在可直接观察的实体联系，如蛋白质之间的结合、神经元之间的突触、两脑区之间的白质纤维束。

**统计关联**（statistical association）：两个变量的测量值共同变化，如功能连接中 BOLD 时间序列的相关、共表达网络中的表达相关、症状网络中的偏相关。

**功能关联**（functional association）：两个对象参与同一生物学过程的证据，可能整合多种来源，例如 STRING 数据库的综合得分同时纳入实验、共表达、基因组邻近和文本挖掘证据（Szklarczyk 等, 2019, *Nucleic Acids Research*）。

**因果或有向关系**（causal/directed relation）：一个变量的变化导致另一个变量变化，如转录因子对靶基因的调控、有效连接（effective connectivity）。
:::

这四类边回答不同问题。物理连接网络中的路径可以对应实际的信号或物质传递；统计关联网络中的“最短路径”没有明确的物理含义（Rubinov & Sporns, 2010, *NeuroImage*）；功能关联网络的边权是证据强度，不是作用强度；有向边需要时间顺序、干预或强结构假设才能识别。

::: {.callout-warn}
**同一个“网络”可能混合了多种边。** 很多数据库把酵母双杂交得到的二元结合、亲和纯化–质谱得到的复合物共沉淀、遗传相互作用放在同一张表里。复合物共沉淀并不说明两个蛋白直接接触，常见的做法是把复合物展开为“星形”或“全连接”，两种展开方式给出的度分布差别很大。构建前应按实验类型筛选，并写明展开方式。
:::

### 有向关系的证据来源

从观测数据推断方向需要额外信息。时间顺序是最常用的线索：Granger（1969, *Econometrica*）因果检验问“加入 $X$ 的过去值能否改进对 $Y$ 的预测”；动态因果模型（dynamic causal modelling, DCM; Friston 等, 2003, *NeuroImage*）则用生成模型显式描述神经活动如何产生观测信号。Smith 等（2011, *NeuroImage*）在模拟 fMRI 数据上比较了多种连接估计方法，偏相关、正则化逆协方差等方法在检测“是否有直接连接”上表现较好，而基于滞后的方向推断在 fMRI 的时间分辨率与血流动力学延迟下表现很差。基因调控方面，扰动实验（敲除、敲低、CRISPR 筛选）提供的方向证据通常强于纯观测数据，详见 [基因调控网络推断](gene-network-inference.html)。Granger 因果、转移熵与动态因果模型的定义、算法与限制见 [从时间序列推断有向边](network-construction.directed-edges.html)。

## 连接强度的估计 {#edge-estimation}

### 相关与偏相关

对 $N$ 个变量各有 $T$ 个观测（时间点、被试或样本），最常用的边权是皮尔逊相关 $r_{ij}$。相关网络的问题是间接关联也会成边：若 $A\to B\to C$，$A$ 与 $C$ 之间没有直接作用，相关仍可能很高。

偏相关（partial correlation）在控制其余所有变量后度量两变量的关联。记协方差矩阵 $\Sigma$，精度矩阵 $\Theta=\Sigma^{-1}$，则

$$
\rho_{ij\cdot\text{rest}}=-\frac{\Theta_{ij}}{\sqrt{\Theta_{ii}\Theta_{jj}}}.
$$

在多元正态假设下，$\rho_{ij\cdot\text{rest}}=0$ 等价于给定其余变量时 $i$ 与 $j$ 条件独立，这样的网络称为高斯图模型（Gaussian graphical model, GGM）。偏相关能去掉链式结构中的间接边，但它也会在对撞结构 $A\to C\leftarrow B$ 中制造原本不存在的 $A$–$B$ 关联（代码示例最后一个单元演示了这两种情况）。偏相关因此更接近“直接关联”，但仍然不是因果。

::: {.callout-def}
**相关网络的传递性**：若 $r_{ij}$ 与 $r_{jk}$ 都较大，$r_{ik}$ 在数学上不可能任意小。相关矩阵必须半正定，这个约束本身就会让相关网络的聚集系数高于随机图（Zalesky 等, 2012, *NeuroImage*）。这一点在选择零模型时很关键。
:::

### 高维情形：收缩与正则化

当 $T$ 与 $N$ 同量级，样本协方差矩阵 $S$ 接近奇异，直接求逆得到的偏相关噪声极大；$T<N$ 时 $S$ 根本不可逆。两类常用对策：

1. **收缩估计**（shrinkage）：把 $S$ 向一个结构简单的目标矩阵（如对角阵）收缩，$\hat\Sigma=(1-\delta)S+\delta F$，收缩强度 $\delta$ 可解析地估计（Ledoit & Wolf, 2004, *Journal of Multivariate Analysis*）。Schäfer 与 Strimmer（2005, *Statistical Applications in Genetics and Molecular Biology*）把这一思路用于基因表达数据的偏相关网络。
2. **稀疏正则化**：图形 LASSO（graphical lasso; Friedman 等, 2008, *Biostatistics*）在高斯似然上对精度矩阵的非对角元素加 $\ell_1$ 惩罚，直接得到稀疏的 $\hat\Theta$；邻域选择法（Meinshausen & Bühlmann, 2006, *Annals of Statistics*）对每个变量做 LASSO 回归，再合并邻居集合。心理网络中最常用的 EBICglasso 流程用扩展 BIC 选择惩罚参数，详见 Epskamp 与 Fried（2018, *Psychological Methods*）的教程和 [症状网络](symptom-networks.html)。

::: {.callout-warn}
正则化有代价：LASSO 假设真实网络稀疏，并会把所有非零边向 0 压缩。估计出来“没有边”可能只是功效不足，而不是条件独立；边权的大小也系统偏小，不宜直接与未正则化的估计比较。
:::

### 互信息与非线性依赖

互信息（mutual information, MI）$I(X;Y)=\iint p(x,y)\log\frac{p(x,y)}{p(x)p(y)}\,dx\,dy$ 能捕捉非线性、非单调的依赖。对二元正态变量，$I=-\tfrac12\ln(1-\rho^2)$，与相关一一对应，此时 MI 不提供额外信息。MI 的估计比相关困难：分箱估计对箱宽敏感，k 近邻估计（Kraskov 等, 2004, *Physical Review E*）在连续数据中更常用。在基因网络中，ARACNe（Margolin 等, 2006, *BMC Bioinformatics*）先用 MI 构建网络，再用数据处理不等式删去三角形中最弱的一条边，以减少间接关联。

### 样本量与估计误差

边权估计的不确定性常被忽略。样本相关的标准误近似为 $(1-\rho^2)/\sqrt{T}$，依赖未知的真值；Fisher（1915, *Biometrika*）研究了样本相关系数的抽样分布，其后提出的 $z$ 变换

$$
z=\operatorname{artanh}(r)=\tfrac12\ln\frac{1+r}{1-r},\qquad \operatorname{Var}(z)\approx\frac{1}{T-3}
$$

使方差近似不依赖 $\rho$（推导见 [数学推导与算法](network-construction.derivations.html)）。由此可以算出：要把 $r$ 的 95% 置信区间宽度缩小一半，需要的样本量大约是原来的 4 倍。代码示例中，$r=0.3$ 时 $n=30$ 的区间跨过 0，而 $n=1000$ 的区间宽度约为 0.1。

两个实际要点：

- **有效样本量**：fMRI 的 BOLD 信号有很强的自相关，独立观测数远少于时间点数。直接用 $T$ 计算单被试层面的标准误会高估精度。被试水平的组分析（每名被试一个 $z$ 值，误差来自被试间变异）对此更稳健。
- **组分析的单位**：比较两组时，应把每名被试的 Fisher $z$ 作为观测，而不是先平均相关矩阵再比较。

## 从时间序列推断有向边 {#directed-edges}

相关、偏相关和互信息都是对称的，得到的是无向网络。当每个节点有一段足够长、采样足够快的时间序列（神经元放电、EEG/MEG、颅内脑电、经验取样的症状自评、时间序列转录组）时，可以尝试利用“时间先后”估计有向边。这类边在脑网络中常称为有向功能连接（directed functional connectivity），与基于生物物理生成模型的有效连接（effective connectivity）相区别（Friston, 2011, *Brain Connectivity*）。三类方法最常用：Granger 因果、转移熵和动态因果模型。

### Granger 因果

::: {.callout-def}
**Granger 因果**（Granger causality, GC）：若在已经利用 $Y$ 自身过去（以及其他条件变量 $Z$ 的过去）的基础上，再加入 $X$ 的过去能显著改进对 $Y$ 当前值的预测，就称 $X$ Granger 引起 $Y$，记为 $X\to Y$（Granger, 1969, *Econometrica*）。
:::

线性情形用向量自回归（VAR）实现。拟合两个模型：

$$
\begin{aligned}
\text{受限模型：}\; y_t&=\sum_{l=1}^{p}a_l y_{t-l}+\sum_{l=1}^{p}\mathbf c_l^{\top}\mathbf z_{t-l}+\varepsilon_t,\\
\text{完整模型：}\; y_t&=\sum_{l=1}^{p}a'_l y_{t-l}+\sum_{l=1}^{p}\mathbf c'^{\top}_l\mathbf z_{t-l}+\sum_{l=1}^{p}b_l x_{t-l}+\varepsilon'_t ,
\end{aligned}
$$

Geweke（1982, *Journal of the American Statistical Association*）把 GC 定义为两个残差方差之比的对数

$$
\mathcal F_{X\to Y\mid Z}=\ln\frac{\operatorname{Var}(\varepsilon_t)}{\operatorname{Var}(\varepsilon'_t)}\ \ge 0 ,
$$

并给出了按频率分解的谱 GC。检验 $b_1=\dots=b_p=0$ 可用 $F$ 检验，或在大样本下用 $(T-p)\,\hat{\mathcal F}$ 的近似 $\chi^2_p$ 分布。模型阶数 $p$ 通常用 AIC/BIC 选择。

**两两 GC 与条件 GC**。若只拟合 $X$、$Y$ 两个变量，一个同时驱动二者、且对 $X$ 的作用早于对 $Y$ 的作用的第三变量 $Z$，会产生虚假的 $X\to Y$。条件 GC 把 $Z$ 的过去放进两个模型，能消除这种由**已观测**共同驱动引起的假边；对未观测的共同驱动无能为力。代码示例中，两两 GC 给出极显著的 $X\to Y$（$F\approx 400$），条件于 $Z$ 后降为 $F\approx 0.1$。

### 转移熵

转移熵（transfer entropy, TE; Schreiber, 2000, *Physical Review Letters*）是 GC 的信息论版本：

$$
\mathrm{TE}_{X\to Y}=I\big(Y_t;\,X_{t-1}^{(l)}\,\big|\,Y_{t-1}^{(k)}\big)
=H\big(Y_t\mid Y^{(k)}_{t-1}\big)-H\big(Y_t\mid Y^{(k)}_{t-1},X^{(l)}_{t-1}\big),
$$

其中 $X^{(l)}_{t-1}$ 表示 $X$ 的过去 $l$ 个值。它不假设线性（神经科学中的使用见 Vicente 等, 2011, *Journal of Computational Neuroscience*），代价是条件熵难以估计：数据有限时分箱或 k 近邻估计的偏差与方差都大，嵌入维数 $k,l$ 也会改变结果。

对联合高斯变量，TE 与 GC 等价，$\mathrm{TE}=\tfrac12\mathcal F$（Barnett, Barrett & Seth, 2009, *Physical Review Letters*；推导见 [数学推导与算法](network-construction.derivations.html)），TE 的价值在非高斯、非线性数据中。

### 动态因果模型

动态因果模型（DCM; Friston, Harrison & Penny, 2003, *NeuroImage*）走的是另一条路：先写出一个**生成模型**，描述少数几个脑区的神经状态 $\mathbf z$ 如何在实验输入 $\mathbf u$ 的作用下演化，

$$
\dot{\mathbf z}=\Big(A+\sum_j u_j B^{(j)}\Big)\mathbf z+C\mathbf u ,
$$

再用血流动力学正向模型把 $\mathbf z$ 映射为可观测的 BOLD 信号，用贝叶斯方法估计耦合矩阵 $A$（固有连接）、$B^{(j)}$（输入对连接的调制）和 $C$（输入的作用点），并用模型证据比较不同的连接假设。DCM 显式处理了“神经活动 → 观测信号”的变换，但只能比较预先设定的少数候选模型、脑区数量有限，结论依赖生成模型的正确性，不是在全脑“发现”网络的工具。

### 限制：什么时候时间先后不等于因果

1. **测量噪声与降采样**。Seth、Chorley 与 Barnett（2013, *NeuroImage*）在模拟中显示，GC 在原理上对血流动力学卷积不敏感，但在严重降采样或测量噪声过大时（正是 fMRI 的典型情形）会得出错误的方向。Smith 等（2011）的 fMRI 模拟中，基于滞后的方向推断表现也很差。代码示例给出一个反直觉的现象：只给“源”变量加测量噪声，就能产生高度显著的反向 GC。
2. **未观测的共同驱动**。条件 GC 只能条件于测量到的变量；在全脑只取部分脑区、或只测部分基因时，遗漏的变量会制造有向假边。
3. **瞬时混合与非平稳**。EEG/MEG 的容积传导使通道在同一时刻混合，可能被误读为定向作用；VAR 假设平稳和线性，状态切换会破坏这些假设，滑动窗口又带来有限样本波动（见 [动态功能连接](dynamic-brain-networks.html)）。
4. **时间尺度**。采样间隔长于真实作用的时间尺度时，作用表现为“同期相关”，方向信息丢失；经验取样症状网络区分时间网络与同期网络正是为此（见 [个体动态网络](symptom-networks.temporal-networks.html)）。

Seth、Barrett 与 Barnett（2015, *Journal of Neuroscience*）总结了 GC 在神经科学中的使用条件。总体原则是：有向边是“给定模型、变量集合与采样下的预测性优先关系”，解释为机制上的因果需要干预或结构证据；基因调控中的扰动数据在这一点上更有力（见 [基因调控网络推断](gene-network-inference.html)）。代码示例：[有向边推断](network-construction.html#code)。

## 阈值、加权与稀疏化 {#thresholding}

相关、偏相关或互信息给出的是一个稠密的加权矩阵。多数经典图论指标定义在二值网络上，于是需要决定保留哪些边。

### 几种做法

::: {.callout-def}
**绝对阈值**（absolute threshold）：保留 $|w_{ij}|>\tau$ 的边，$\tau$ 对所有个体相同，网络密度随个体变化。

**比例阈值**（proportional threshold）：每个个体保留最强的前 $p$ 比例的边，所有个体密度相同，也称密度阈值或成本（cost）阈值。

**显著性阈值**：对每条边做检验，保留校正后显著的边。边数取决于样本量和效应量。

**最小生成树**（minimum spanning tree, MST）：在连通的加权图中，连接全部 $N$ 个节点、总权重最小的 $N-1$ 条边（相关网络中取“最大生成树”，即保留最强连接）。可用 Kruskal（1956, *Proceedings of the American Mathematical Society*）算法求得。
:::

**密度为什么重要**：几乎所有拓扑指标都随密度变化。密度越高，聚集系数和全局效率越高，路径越短。van Wijk 等（2010, *PLoS ONE*）系统说明了在节点数或密度不同的网络之间比较图论指标的困难：简单地除以随机网络的值也不能完全消除这种依赖。因此组间比较的第一条原则是**不让密度差异冒充拓扑差异**。

**绝对阈值的偏差**：如果患者组整体连接偏弱（例如头动更大、信噪比更低），同一 $\tau$ 下患者网络更稀疏，聚集系数和效率随之下降，这种“差异”完全来自密度。

**比例阈值的偏差**：比例阈值强制密度相同，但当一组整体连接偏弱时，为了凑够同样的边数，会纳入更多接近噪声的弱边。这些边的位置近似随机，使该组网络看起来更“随机”。van den Heuvel 等（2017, *NeuroImage*）在静息态 fMRI 数据中展示了这一效应，并建议把整体连接强度作为协变量报告。代码示例中的“比例阈值与密度匹配”单元用模拟数据重现了两种偏差。

**MST 的取舍**：MST 的边数固定为 $N-1$，不需要选阈值，也保证连通，因此可以避免密度差异（Tewarie 等, 2015, *NeuroImage*）。代价是丢掉了所有环路，聚集系数恒为 0，只能计算树结构上的指标。另一种常见做法是“MST 骨架 + 按强度补边”，用于保证比例阈值后的网络连通。

### 在一段密度范围上分析

单一阈值几乎总是任意的。常见的稳妥做法有三种：

1. **密度扫描**：在一段预先确定的密度范围（例如 5% 到 30%）内逐点计算指标，报告曲线，或用曲线下面积（AUC）作为综合指标。Achard 与 Bullmore（2007, *PLoS Computational Biology*）在“成本”范围上比较效率；Ginestet 等（2011, *PLoS ONE*）提出对成本积分以把拓扑与成本分开。
2. **多阈值的统计校正**：在每个阈值上都做组间检验再挑最显著的，会膨胀假阳性。Drakesmith 等（2015, *NeuroImage*）提出多阈值置换校正（multi-threshold permutation correction），把阈值也纳入置换框架。
3. **直接分析加权网络**：使用加权聚集系数、加权效率、强度等，避免二值化。需要注意负权的处理（取绝对值、只看正边或分开分析），并在报告中说明；路径类指标要先把“相似度”转为“距离”。

Garrison 等（2015, *NeuroImage*）发现，许多功能网络指标在不同阈值下的个体排序并不稳定。这意味着阈值敏感性分析不是可选项：结论至少应在一段合理的阈值或密度范围内方向一致。

::: {.callout-warn}
**阈值方案要在看结果之前确定。** 尝试多个阈值、只报告显著的那一个，是典型的研究者自由度问题。可接受的做法是预先注册方案，或者报告全部阈值下的结果并做相应校正。
:::

## 边权不确定性向网络指标的传播 {#uncertainty-propagation}

[连接强度的估计](network-construction.edge-estimation.html) 讨论了单条边的误差；但研究者报告的通常不是边，而是聚集系数、效率、模块度、中心性这些**由所有边共同决定的指标**。边权的误差如何传到指标上，是网络分析中最容易被跳过的一步。

### 三种传播方式

**1. 解析近似（delta 方法）**。若指标 $f(\mathbf w)$ 是边权向量 $\mathbf w$ 的光滑函数，边权估计的协方差为 $\Sigma_w$，则

$$
\operatorname{Var}\big(f(\hat{\mathbf w})\big)\approx\nabla f(\mathbf w)^{\top}\,\Sigma_w\,\nabla f(\mathbf w).
$$

节点强度是边权的线性函数，可直接套用（共享节点的边误差相关，忽略协方差会低估方差）；路径长度、模块度和阈值化后的指标不光滑，这一近似基本不可用。

**2. 重抽样（bootstrap）**。把“原始数据 → 边权 → 稀疏化 → 指标”的**整个流程**放进重抽样循环，每次重新计算指标，用其分布描述不确定性（Epskamp, Borsboom & Fried, 2018）。重抽样单位必须是独立单位：被试、样本，或单被试时间序列中的连续块。

**3. 概率网络与网络集合**。若能得到每条边存在的概率 $\pi_{ij}$（来自 bootstrap 入选频率、贝叶斯后验或数据库的置信度得分），可以把网络看作随机图。在边相互独立的近似下，节点度的期望与方差为

$$
\mathbb E[k_i]=\sum_{j}\pi_{ij},\qquad \operatorname{Var}(k_i)=\sum_j\pi_{ij}(1-\pi_{ij}).
$$

更复杂的指标可以从这一随机图中抽取大量网络，逐一计算后汇总。Newman（2018, *Nature Physics*）和 Peixoto（2018, *Physical Review X*）的网络重建方法直接给出网络的后验分布，指标的不确定性随之得到。

### 阈值附近的边是主要来源

阈值化把连续误差变成离散的“有/无”。远离阈值的边几乎每次都入选或落选；真实强度接近阈值的边，入选与否近似抛硬币。这些边的位置大体随机，于是噪声越大，阈值化网络越像随机图：聚集系数与模块度被低估，全局效率被高估。van den Heuvel 等（2017）描述的比例阈值偏差，本质上就是这一机制在组间比较中的表现。

::: {.callout-def}
**指标的均值不等于均值网络的指标**。对非线性指标 $f$，一般 $\mathbb E[f(A)]\ne f(\mathbb E[A])$（Jensen 不等式的推论）。“先把 bootstrap 网络平均成一张共识网络再算指标”和“对每个 bootstrap 网络算指标再平均”回答的是不同问题，报告时要写明用的是哪一种。
:::

代码示例（一名模拟被试，30 个脑区、300 个自相关时间点）中，全局效率的真实抽样标准差约为 0.046；逐时间点的朴素 bootstrap 只给出约 0.021，循环块 bootstrap 给出约 0.026–0.029，更接近但仍偏乐观。约五分之一的边入选概率介于 0.2 与 0.8 之间，度最高的 5 个“枢纽”在重抽样中平均不到一半保持不变；bootstrap 网络的平均传递性（约 0.39）也明显低于共识网络的传递性（约 0.48）。

对下游分析而言：两组的边权估计精度不同（头动、扫描时长、样本量不同）时，噪声差异会经阈值化转化为拓扑差异；指标的测量误差还会衰减它与表型的相关（见 [样本量与统计功效](network-construction.sample-size-power.html)）。因此指标应带区间报告，中心性排序应报告其稳定性。

## 零模型与空模型 {#null-models}

一个指标的数值本身很少有意义。“聚集系数 0.25”是高还是低，取决于与什么比较。零模型（null model）是一组保留了真实网络某些性质、其余部分随机化的参照网络，用来回答“观察到的结构能否被这些被保留的性质解释”。中文文献中也称空模型或参照模型。Váša 与 Mišić（2022, *Nature Reviews Neuroscience*）对网络神经科学中的零模型做了系统综述。

::: {.callout-def}
**零模型的逻辑**：设观测网络的指标为 $X_{\text{obs}}$，零模型生成 $M$ 个随机网络，指标为 $X_1,\dots,X_M$。若 $X_{\text{obs}}$ 落在零分布的极端位置，结论是：该结构**超出了零模型所保留性质能解释的范围**。零模型保留的性质越多，检验越严格，结论也越具体。
:::

### 常见零模型

| 零模型 | 保留的性质 | 随机化的部分 | 典型用途 |
|---|---|---|---|
| ER 随机图 $G(N,M)$ | 节点数、边数 | 边的位置 | 最粗的基线；小世界的 $C_{\text{rand}}$、$L_{\text{rand}}$ |
| 配置模型（configuration model） | 度序列 | 在度约束下随机配对“半边” | 模块度的期望项、度相关结构 |
| 保度随机化（边交换） | 每个节点的度（可加连通性） | 边的位置 | 基序、富人俱乐部、聚集系数 |
| 保度保强度的加权零模型 | 度和强度（近似） | 权重的位置 | 加权网络、带符号的相关网络 |
| 空间约束零模型 | 度序列加连接长度分布，或节点的空间位置 | 不依赖距离的部分 | 脑网络、空间嵌入网络 |
| 相关矩阵零模型 | 相关矩阵元素的均值与方差 | 相关结构 | 功能连接网络的聚集系数基线 |
| 节点标签置换 / 空间自相关保持置换 | 网络本身不变 | 节点属性在节点间的分配 | 脑图与脑图、基因集与网络的对应关系 |

**配置模型**：给定度序列 $\{k_i\}$，把每个节点 $i$ 看作带 $k_i$ 个“半边”，随机两两配对。稀疏情形下 $i$ 与 $j$ 之间期望边数约为 $k_ik_j/2M$，这正是模块度定义中的期望项。随机配对会产生自环和重边，删除它们又会改变度序列。Molloy 与 Reed（1995, *Random Structures & Algorithms*）给出了给定度序列随机图出现巨连通分支的条件；Fosdick 等（2018, *SIAM Review*）指出，“配置模型”实际上是一族模型，是否允许自环与重边、以“半边”还是以“图”为抽样单位，都会改变零分布，在度分布重尾时差别尤其明显。Squartini 与 Garlaschelli（2011, *New Journal of Physics*）给出了一种只在期望意义上保持度序列的最大熵版本，可以解析计算期望值。

**保度随机化**：Maslov 与 Sneppen（2002, *Science*）用反复交换边端点的方法生成保度随机网络，比较酵母蛋白质相互作用网络与转录调控网络中高度节点之间的连接，发现高度节点之间的直接连接少于随机预期。双边交换算法见 [数学推导与算法](network-construction.derivations.html)。Milo 等（2002, *Science*）在网络基序研究中也用保度随机网络作为参照。

**空间约束**：脑区之间的连接概率随距离下降，猕猴示踪数据中这一关系可以用指数距离规则描述（Ercsey-Ravasz 等, 2013, *Neuron*）。Roberts 等（2016, *NeuroImage*）显示，仅由空间几何就能产生人脑连接组的许多拓扑特征。Vértes 等（2012, *PNAS*）用带距离惩罚的简单生成模型再现了功能网络的多项拓扑性质。因此对脑网络，“比保度随机网络更模块化”可能只是空间嵌入的结果；需要再与保持连接长度分布的零模型比较。

**加权与相关网络**：Rubinov 与 Sporns（2011, *NeuroImage*）给出了在带符号加权网络中近似保持度和强度分布的零模型。对相关网络，Zalesky 等（2012, *NeuroImage*）建议用与真实相关矩阵统计特征相匹配的随机相关矩阵作为参照，因为保度随机化仍会破坏相关矩阵固有的传递性，使 $C_{\text{rand}}$ 偏低、“小世界性”被高估。

**节点属性置换**：当问题是“两张脑图（例如基因表达图与皮层厚度变化图）是否空间对应”时，简单打乱脑区标签会忽略空间自相关，使假阳性率膨胀。旋转检验（spin test）在球面上旋转一张图以保持其空间自相关（Alexander-Bloch 等, 2018, *NeuroImage*）；BrainSMASH 生成具有相同空间自相关的替代图（Burt 等, 2020, *NeuroImage*）。

### z 分数与经验 p 值

由 $M$ 个零模型网络得到均值 $\bar X$ 与标准差 $s$，

$$
z=\frac{X_{\text{obs}}-\bar X}{s},\qquad
\hat p=\frac{1+\#\{X_m\ge X_{\text{obs}}\}}{M+1}.
$$

$z$ 分数便于比较不同指标的偏离程度，但只有在零分布近似正态时才能换算成 $p$ 值；零分布偏斜或离散时应直接报告经验 $p$ 值。经验 $p$ 值分子分母加 1，是因为观测本身也是零假设下的一个可能结果，这保证了 $\hat p$ 永远不为 0，并且检验在有限次置换下仍然有效（Phipson & Smyth, 2010, *Statistical Applications in Genetics and Molecular Biology*）。$M$ 决定了能达到的最小 $p$ 值 $1/(M+1)$，需要多重比较校正时，$M$ 要相应加大。

代码示例中，一个模拟网络的负度同配相对 ER 零模型显著，相对保度零模型则不显著：负同配的大部分可由度序列本身解释，因为在简单图中高度节点之间可连接的边数有限。这说明零模型的选择决定了结论的含义。

## 统计推断与多重比较 {#statistical-inference}

### 比较什么：三个层面

组间网络比较（如患者与对照）可以在三个层面进行，层面越细，比较次数越多，多重比较的负担越重：

1. **全局指标**：每名被试计算全局效率、模块度等，组间做 $t$ 检验或一般线性模型。比较次数少，但解释依赖密度控制。
2. **节点指标**：每个节点一次检验，$N$ 次。
3. **边**：每条边一次检验，$N(N-1)/2$ 次，90 个脑区就有 4005 条边。

### 置换检验

置换检验（permutation test）在零假设下认为组标签可交换：随机打乱组标签，重新计算统计量，重复多次得到零分布。它不需要统计量服从已知分布，适用于网络指标这类分布难以推导的统计量（Nichols & Holmes, 2002, *Human Brain Mapping*）。需要注意：

- **可交换性**是前提。存在家系、重复测量或扫描站点时，应只在可交换的块内置换（Winkler 等, 2014, *NeuroImage*）。
- 有协变量（年龄、头动、整体连接强度）时，应置换残差或采用专门的置换方案，而不是直接打乱原始数据。
- **最大统计量法**：每次置换只记录所有检验中的最大统计量，用其分布确定阈值，可以控制族错误率（family-wise error rate, FWE）（Nichols & Hayasaka, 2003, *Statistical Methods in Medical Research*）。

### 错误发现率

当检验数量很大、目标是筛选候选而不是确证每一个时，控制错误发现率（false discovery rate, FDR）比控制 FWE 更有功效。Benjamini 与 Hochberg（1995, *Journal of the Royal Statistical Society: Series B*）提出的 BH 程序：把 $m$ 个 $p$ 值从小到大排序为 $p_{(1)}\le\dots\le p_{(m)}$，找最大的 $k$ 使 $p_{(k)}\le kq/m$，拒绝前 $k$ 个假设。在检验独立或正相关依赖时，它把 FDR 控制在 $q$ 以下；任意依赖结构下可用 Benjamini 与 Yekutieli（2001, *Annals of Statistics*）的更保守版本。Storey 与 Tibshirani（2003, *PNAS*）提出的 $q$ 值在基因组学中常用。

### 基于网络的统计（NBS）

逐边 FDR 把每条边当作独立单元，忽略了“异常连接往往连成一片”的可能。基于网络的统计（network-based statistic, NBS; Zalesky, Fornito & Bullmore, 2010, *NeuroImage*）借鉴影像中的团块推断：

1. 对每条边做组间检验，得到统计量 $t_{ij}$；
2. 用一个**主阈值**保留 $|t_{ij}|$ 超过阈值的边，找出它们构成的连通分量，记录每个分量的大小（边数）；
3. 置换组标签，重复第 1–2 步，每次只记录**最大分量**的大小，得到零分布；
4. 观测分量的 FWE 校正 $p$ 值为零分布中不小于其大小的比例。

::: {.callout-warn}
**NBS 的推断单位是子网络，不是边。** 显著的结论是“这个相连的边集合作为整体在组间不同”，不能据此说其中任意一条边显著。主阈值是一个需要预先确定的参数：较高的主阈值利于检出强而局限的效应，较低的主阈值利于检出弱而广泛的效应。改变主阈值寻找显著结果同样属于研究者自由度。
:::

代码示例中的模拟显示：真实差异集中在 6 个脑区构成的子网络内，FDR 与 NBS 都能找到它；NBS 的最大分量还纳入了少量子网络外的边，这正说明不能把 NBS 的结论下放到单条边。

### 网络比较检验

对估计出来的整张网络（如两个人群的症状网络）进行比较时，网络比较检验（network comparison test, NCT; van Borkulo 等, 2023, *Psychological Methods*）通过置换组标签、在每次置换中重新估计两个网络，检验三类不变性：整体网络结构（最大边差异）、全局强度、指定边。重新估计这一步不可省略，因为正则化估计本身对样本量和数据特征敏感。

## 网络之间的距离与相似性 {#network-distances}

[统计推断与多重比较](network-construction.statistical-inference.html) 讨论的是在边、节点或全局指标层面比较两组网络。另一类问题是直接问“两张网络有多不同”：同一被试两次扫描的网络是否相似，疾病组与对照组的网络整体是否不同，一个模型生成的网络与真实网络是否相像，一个物种的相互作用组与另一个物种的有多大差异。这需要定义网络之间的**距离**或**相似度**。

### 两类问题：节点是否对应

Tantardini 等（2019, *Scientific Reports*）把网络比较方法分为两类：

::: {.callout-def}
**已知节点对应**（known node-correspondence, KNC）：两张网络的节点集合相同且一一对应，例如同一脑图谱下不同被试的网络、同一批基因在两种条件下的共表达网络。

**未知节点对应**（unknown node-correspondence, UNC）：节点集合不同或无法对应，例如不同物种的相互作用组、不同大小的模型网络。只能比较与节点标签无关的结构特征。
:::

### 已知节点对应时

- **边集合距离**：汉明距离 $\sum_{i<j}|A_{ij}-B_{ij}|$（两网络边集合对称差的大小）；Jaccard 距离 $1-|E_A\cap E_B|/|E_A\cup E_B|$ 消除了边数的影响。
- **加权矩阵距离**：Frobenius 范数 $\|W_A-W_B\|_F$，或边权向量之间的相关。对功能连接矩阵，也可以把相关矩阵看作正定矩阵流形上的点，在切空间中计算距离；这类做法在个体识别与表型预测中常见。
- **考虑传播的距离**：DeltaCon（Koutra 等, 2016, *ACM Transactions on Knowledge Discovery from Data*）比较节点间“亲和度”矩阵，删去连接两个模块的桥边比删去模块内的冗余边带来更大的距离。

### 节点无对应时

- **指标向量**：把度分布、聚集系数、同配系数等拼成特征向量再比较；简单，但只比较了少数相关的统计量。
- **谱距离**：比较邻接矩阵或（归一化）拉普拉斯矩阵的特征值序列，如 $d(G,H)=\|\boldsymbol\lambda(G)-\boldsymbol\lambda(H)\|_2$（Wilson & Zhu, 2008, *Pattern Recognition*）。特征值与标签无关、计算方便；但存在**同谱异构图**（不同的图有相同的谱），谱距离为 0 并不说明两图相同。
- **小图（graphlet）方法**：统计每个节点参与的各种小连通子图“轨道”的分布。Pržulj（2007, *Bioinformatics*）提出了基于小图度分布的一致性度量并用于比较蛋白质相互作用网络；Yaveroğlu 等（2014, *Scientific Reports*）提出小图相关距离。
- **图核**（graph kernel）：两图之间的内积 $K(G,H)=\langle\phi(G),\phi(H)\rangle$，$\phi$ 为子结构计数特征。Weisfeiler–Lehman（WL）子树核反复把节点标签与其邻居标签的多重集合并重新编码，再统计各轮标签频数（综述见 Kriege, Johansson & Morris, 2020, *Applied Network Science*）。网络肖像散度（Bagrow & Bollt, 2019, *Applied Network Science*）则比较全尺度的最短路径距离分布。

### 选择距离的原则

不同距离关注不同的结构层次，没有普遍最优的选择。Hartle 等（2020, *Proceedings of the Royal Society A*）提出用“同一生成模型独立抽取的两个网络之间的期望距离”（集合内图距离）来刻画距离度量本身：如果同类随机网络之间的距离已经很大，那么观测到的大距离不说明什么。代码示例比较了 ER、WS、BA 与随机块模型四类网络：拉普拉斯谱距离与 WL 核的“类内/类间”比约为 0.25，度分布 Jensen–Shannon 散度约为 0.45；节点无对应时 Jaccard 距离对同类随机网络也接近 1；谱距离几乎区分不开 ER 与弱模块的随机块模型。

::: {.callout-warn}
**距离本身不是检验**。“两组网络距离为 0.3”没有意义，除非知道在零假设下（例如同一总体的两组网络之间）会是多少。常用做法是把距离当作检验统计量：比较组间平均距离与组内平均距离，置换组标签得到零分布（代码示例中的最后一部分），或与 [零模型](network-construction.null-models.html) 生成网络之间的距离比较。
:::

## 测量误差、缺失与偏倚 {#bias-and-missingness}

前面各节默认数据是“干净”的。实际数据中，系统性误差往往比随机误差更危险，因为增加样本量不会消除它。

### 数据库研究偏倚

文献整理型的相互作用数据库（如 BioGRID; Stark 等, 2006, *Nucleic Acids Research*）记录的是“被研究过的”相互作用。研究得越多的蛋白，记录的相互作用越多，度就越高。Edwards 等（2011, *Nature*）指出蛋白质研究长期集中在少数早已熟知的家族；Haynes 等（2018, *Scientific Reports*）报告基因注释偏向已被大量研究的基因；Stoeger 等（2018, *PLOS Biology*）分析了一些可能重要的基因长期被忽视的原因。由此产生两个后果：

- **度与“疾病相关性”混杂**：疾病基因研究多，度也高。“疾病基因在网络中是枢纽”的结论可能部分来自研究热度。
- **度偏倚与功能预测**：Gillis 与 Pavlidis（2011, *PLoS ONE*）发现，“关联推定”（guilt by association）的功能预测性能中有相当部分可由基因的多功能性（注释数量）和节点度解释；Gillis 与 Pavlidis（2012, *PLoS Computational Biology*）进一步显示，网络中与功能预测相关的信息集中在少数边上。评估网络方法时应加入“只按度排序”这一基线。

系统性的二元相互作用筛选受研究偏倚影响较小。Rolland 等（2014, *Cell*）和 Luck 等（2020, *Nature*，HuRI）报告了蛋白质组规模的人类二元相互作用图谱，其中相互作用在蛋白质组中的分布比文献整理数据更均匀。比较两类数据库的结果，是检验研究偏倚的直接办法。

### 不完整的相互作用组

即使不考虑偏倚，现有人类相互作用组也远不完整。Venkatesan 等（2009, *Nature Methods*）提出了评估二元相互作用图谱完整性、精确度和灵敏度的实证框架。Menche 等（2015, *Science*）讨论了在不完整网络中识别疾病模块的条件：疾病基因之间的连接必须达到一定覆盖率，模块才可能被检测到。实际后果是：

- 网络中“两个节点不相连”不等于“二者不相互作用”；
- 基于最短路径的指标（如网络邻近度）对缺失边敏感，应在不同数据库版本或随机删边后检验结论；
- 零模型应在同一个不完整网络上构建，并保持度分布，以抵消度偏倚的一部分影响。

不完整观测对度分布、传递性和枢纽识别的定量影响见 [采样网络与不完整观测](network-construction.sampling-incomplete.html)。

### 测量伪迹：以头动为例

在静息态 fMRI 中，即使毫米级的头动也会系统性地增强近距离脑区的相关、削弱远距离相关（Power 等, 2012, *NeuroImage*；Van Dijk 等, 2012, *NeuroImage*；Satterthwaite 等, 2012, *NeuroImage*）。若患者组头动更大，就可能“制造”出组间连接差异，而且这种差异具有距离依赖的空间模式，看起来像生物学结果。Ciric 等（2017, *NeuroImage*）与 Parkes 等（2018, *NeuroImage*）比较了多种去混杂策略，发现没有一种方法在所有评价指标上都最好，选择取决于研究目标。常规做法包括：头动参数回归、按帧位移剔除坏帧、组间匹配头动、把头动作为协变量，并检查结果与头动的相关。

全局信号回归是否应当进行仍有争论（Murphy & Fox, 2017, *NeuroImage*），稳妥的做法是两种都分析并报告。弥散成像的纤维追踪同样存在系统性的假阳性（Maier-Hein 等, 2017, *Nature Communications*）；共表达网络中，批次效应和细胞组成会制造大量虚假共表达（Parsana 等, 2019, *Genome Biology*）。

### 缺失数据与条目问题

量表数据中的缺失若与症状严重度有关（非随机缺失），直接删除病例会改变网络结构；成对删除计算相关可能使相关矩阵失去正定性，导致偏相关估计失败。条目内容高度重叠时，它们之间会出现很强的边，并抬高双方的中心性，应在估计前检查。

## 采样网络与不完整观测 {#sampling-incomplete}

[测量误差、缺失与偏倚](network-construction.bias-and-missingness.html) 讨论的是缺失“偏向哪里”；这里讨论缺失“如何改变网络指标”。几乎所有生物医学网络都是真实网络的一个样本：相互作用组只测了部分蛋白与蛋白对，连接组只纳入了部分脑区或神经元，症状网络只纳入了量表中的条目。Newman《Networks》（第 2 版）专门讨论了网络数据中测量误差的类型、来源以及估计与校正方法，其中最基本的两类是漏检的边（假阴性）与多出的边（假阳性）。

### 三种采样方式

::: {.callout-def}
**随机节点采样**：每个节点以概率 $p$ 被纳入，网络为被纳入节点的诱导子图。对应“只研究了一部分基因或蛋白”。

**随机边采样**：每条边以概率 $q$ 被检测到，节点全部保留。对应实验灵敏度有限、每次筛选只能捕获部分相互作用。

**滚雪球采样**（snowball sampling）：从少数种子节点出发，沿边逐层纳入邻居。对应“从已知疾病基因或药物靶点出发，查找其相互作用伙伴”。
:::

**度分布**。在随机节点采样下，原来度为 $k$ 的节点被保留后，其邻居各自以概率 $p$ 被保留，观测度 $k'\sim\mathrm{Binomial}(k,p)$。于是平均度按 $p$ 缩小，而观测度分布是原分布的二项“稀释”；用生成函数写为 $G'_0(x)=G_0(1-p+px)$（推导见 [数学推导与算法](network-construction.derivations.html)）。随机边采样下每个节点的度同样按 $\mathrm{Binomial}(k,q)$ 稀释。泊松分布经过二项稀释仍是泊松分布，因此 ER 随机图的子网仍是 ER 图；幂律分布则不具有这种封闭性。Stumpf、Wiuf 与 May（2005, *PNAS*）由此指出，只有当全网与随机子网的度分布属于同一个分布族时，才能从子网外推全网的性质，而无标度分布不满足这一条件。

**反方向的问题同样存在**。Han 等（2005, *Nature Biotechnology*）对随机、指数、幂律和截断正态四种度分布的理论网络按当时酵母双杂交的覆盖率部分采样，得到的子网与已有的部分相互作用组图谱几乎无法区分；因此部分图谱的无标度外观不能可靠地外推到完整相互作用组（参见 [无标度的统计判别](network-models.identification.html)）。

**其他指标**。Lee、Kim 与 Jeong（2006, *Physical Review E*）系统比较了节点、边和滚雪球三种采样对度分布、介数分布、平均路径长度、同配性和聚集系数的影响，发现同一性质在不同采样方式下的偏差方向不同。几条可以手算验证的规律：

- 全局传递性（三角形数 × 3 / 连通三元组数）在随机节点采样下期望近似不变，因为三角形与三元组都需要 3 个节点同时被保留；在随机边采样下约按 $q$ 缩小，因为三角形需要 3 条边，三元组只需要 2 条。
- 采样比例低时，节点采样会把网络打碎：代码示例中，在一个平均度为 6 的重尾网络上保留 20% 的节点，约三分之一的被保留节点成为孤立点，最大连通分支只含约一半的节点，基于最短路径的指标随之失去意义。
- 节点在子网中的度与其真实度的相关随采样比例下降而迅速减弱（示例中 $p=0.5$ 时约 0.95，$p=0.2$ 时约 0.3），按观测度识别“枢纽”变得不可靠。
- 滚雪球采样偏向高度节点：被纳入的节点平均真实度明显高于全网平均（示例中约 9.9 对 6.0）。以疾病基因为种子扩展得到的局部网络，会系统性地高估枢纽的比例。

::: {.callout-bio}
**估计人类相互作用组的大小。** Stumpf 等（2008, *PNAS*）利用子网采样理论，从多个真核生物的部分相互作用数据外推完整网络的边数，估计人类蛋白质相互作用约有 65 万对，比果蝇的大一个数量级。这一估计依赖随机节点采样模型与数据质量的假设，但它说明现有数据库只覆盖了真实相互作用组的一部分。
:::

### 修正与稳健化

1. **按采样过程建模**。若采样机制已知（例如每个蛋白对被检测的概率），可以把它写进似然。Newman（2018, *Nature Physics*）提出用期望最大化（EM）算法，从对同一网络的多次含噪测量中同时估计真实网络和测量的真/假阳性率；Peixoto（2018, *Physical Review X*）用贝叶斯方法在误差率未知且因边而异时重建网络。
2. **敏感性分析**。在已观测网络上进一步随机删除节点或边，观察结论随采样比例的变化趋势；若结论在删除 10%–20% 的边后即消失，它很可能也对尚未观测的边敏感。
3. **边界设定**。Kossinets（2006, *Social Networks*）讨论了边界设定、无应答等缺失机制对社会网络统计量的影响；生物医学中纳入哪些基因、脑区或条目同样是采样决定，应写明理由。比率型指标（传递性、同配系数）通常比平均度这类广延量受采样影响小，但仍需检验。

## 稳定性与可重复性 {#stability-reproducibility}

一个网络结论至少要经受四层检验：同一数据的重抽样（稳定性）、同一被试的重复测量（信度）、独立数据集（复现）、不同合理分析流程（稳健性）。

### 重抽样：bootstrap 与留一法

非参数 bootstrap（Efron, 1979, *Annals of Statistics*）有放回地重抽样观测单位（被试、样本），每次重新估计网络，得到每条边或每个指标的经验分布。几个要点：

- **重抽样的单位**必须与数据的独立单位一致。时间序列不能逐时间点重抽样，否则破坏自相关结构；应重抽样被试，或对单被试数据使用块 bootstrap。
- **整个估计流程都要放进循环**，包括正则化参数的选择和阈值化，否则低估不确定性。
- 对正则化估计，bootstrap 分位数区间会因收缩而偏向 0，它适合判断边之间是否可区分，而不是严格的置信区间（Epskamp, Borsboom & Fried, 2018, *Behavior Research Methods*）。

留一法（leave-one-out，或刀切法 jackknife）每次删去一个观测，检查单个被试或样本对结果的影响；病例删除 bootstrap（case-dropping）每次删去一定比例的被试，看中心性排序与全样本的相关能保持到什么程度。Epskamp 等（2018）据此定义了相关稳定性系数（CS 系数），并建议不低于 0.25、最好高于 0.5，这一阈值是经验建议。

稳定性选择（stability selection; Meinshausen & Bühlmann, 2010, *Journal of the Royal Statistical Society: Series B*）把这一思想用于变量选择：在大量子样本上重复稀疏估计，只保留被选中频率高的边，并给出错误选择数量的上界。

### 重测信度

对同一被试重复测量（如两次扫描），用组内相关系数（intraclass correlation coefficient, ICC; Shrout & Fleiss, 1979, *Psychological Bulletin*）衡量网络指标的个体差异是否稳定。Noble 等（2019, *NeuroImage*）对静息态功能连接重测信度的系统综述与元分析显示，单条边的信度总体偏低，延长扫描时间、使用更多数据可以提高信度；Andellini 等（2015, *Journal of Neuroscience Methods*）综述了图论指标的重测信度，不同指标和流程之间差异很大。信度低的指标即使组间显著，也难以作为个体标志物。

### 跨数据集复现与样本量

Button 等（2013, *Nature Reviews Neuroscience*）说明了小样本研究功效低、效应量被高估的问题。Marek 等（2022, *Nature*）用大样本数据显示，脑影像特征与个体表型的全脑关联效应通常很小，需要数千人才能稳定复现。在症状网络领域，Forbes 等（2017, *Journal of Abnormal Psychology*）质疑网络结构的可复现性，Borsboom 等（2017, 同刊）的再分析认为问题部分来自方法差异；后续研究的共识是网络的整体结构比单条边和中心性排序更可靠。

::: {.callout-bio}
**一个可操作的稳定性报告清单**：（1）边权的 bootstrap 区间；（2）主要指标的病例删除稳定性或留一法影响；（3）阈值或密度范围上的敏感性曲线；（4）关键预处理选择（如是否做全局信号回归、不同图谱或不同数据库版本）下的结果；（5）若有条件，独立样本或重测数据中的复现。
:::

## 样本量与统计功效 {#sample-size-power}

网络研究的功效问题有两层：估计网络本身需要多少数据（每个边权、每个指标的精度），以及检验组间差异或个体差异需要多少被试。这里只给出有公认推导或实证文献支持的经验规则；具体研究应按自己的网络结构和估计方法做模拟功效分析。

### 单条边：Fisher z 的解析计算

检测真实相关 $\rho\ne0$ 的双侧检验（水平 $\alpha$，功效 $1-\beta$）所需样本量近似为

$$
n\approx\left(\frac{z_{1-\alpha/2}+z_{1-\beta}}{\operatorname{artanh}\rho}\right)^{2}+3 .
$$

$\alpha=0.05$、功效 0.8 时，$\rho=0.3$ 约需 85，$\rho=0.2$ 约需 194，$\rho=0.1$ 约需 783（代码示例用模拟核对了 $\rho=0.3,n=85$ 时的实际功效约为 0.80）。对 90 个脑区的 4005 条边做 Bonferroni 校正，相应样本量变为约 287、664 和 2700。偏相关控制了 $p-2$ 个其余变量，Fisher $z$ 的标准误变为 $1/\sqrt{n-(p-2)-3}$，自由度随网络规模减少。两组相关的比较需要更大的样本：标准误是两组之和。

### 信度衰减

若两个变量的测量信度分别为 $r_{xx}$、$r_{yy}$，观测相关的期望约为真实相关乘以 $\sqrt{r_{xx}r_{yy}}$（Spearman, 1904, *American Journal of Psychology*）。这对网络研究有两重含义：边权本身被衰减（量表条目、单次扫描的 BOLD 信号信度有限）；网络指标与表型的相关又被指标的信度衰减一次。两端信度均为 0.6 时，真实相关 0.3 的期望观测值降为 0.18，所需样本量从约 85 增加到约 240。提高信度（更长的扫描、更多的条目或重复测量）与增加样本量同样重要。

### 整网估计：模拟功效分析

整张网络的“功效”没有单一定义：可以是边的灵敏度、特异度、边权与真值的相关，或中心性排序与真值的相关。这些量依赖网络规模、稀疏度、真实边权的大小与估计方法，没有通用的解析式。代码示例中，一个 15 变量、17 条真实边（偏相关约 0.25）的网络，用逐边 Fisher $z$ 检验加 BH 校正时，边灵敏度在 $n=100$ 时约为 0.25，$n=200$ 时约为 0.8，$n=500$ 时接近 1；而强度中心性排序与真值的秩相关到 $n=1000$ 仍未超过 0.9。即使边能被可靠检出，**中心性排序需要的样本量往往更大**。

心理网络中，Epskamp 与 Fried（2018, *Psychological Methods*）建议按假设的网络结构做模拟功效分析；Constantin 等（2026, *Psychological Methods*）把它形式化为通用的蒙特卡罗算法：给定假设网络、性能指标的目标值（如灵敏度 0.6）及达到目标的概率，自动搜索样本量。

### 脑网络：被试数与扫描时长

- **被试数**：Marek 等（2022）显示，全脑范围的脑–表型关联效应通常很小，稳定复现需要数千名被试（见 [稳定性与可重复性](network-construction.stability-reproducibility.html)）。组间比较的功效还取决于效应在网络中的分布：NBS 对弱而广泛的效应有优势，逐边方法对强而局限的效应有优势（Zalesky, Fornito & Bullmore, 2010）。
- **扫描时长**：Birn 等（2013, *NeuroImage*）比较了 3 到 27 分钟的静息态扫描，把扫描从 5 分钟延长到 13 分钟能显著提高功能连接的重测信度，跨次扫描的信度增益在 9–12 分钟后开始减小。

::: {.callout-warn}
**不要用经验规则代替模拟。** “每个参数需要 $k$ 个被试”之类的规则在网络模型中没有可靠依据，因为参数数量（$p(p-1)/2$ 条边）与有效信息量（取决于稀疏度和正则化）并不对应。解析公式只适用于单条边；整网的功效应按预期结构做模拟，并把多重比较、正则化和阈值化都纳入模拟流程。
:::

## 数学推导与算法 {#derivations}

### A. Fisher z 变换与样本量

设 $(x,y)$ 二元正态，$n$ 个独立样本，样本相关 $r$ 的渐近方差为 $\operatorname{Var}(r)\approx(1-\rho^2)^2/n$。寻找变换 $g$ 使方差不依赖 $\rho$：由 delta 方法 $\operatorname{Var}(g(r))\approx g'(\rho)^2(1-\rho^2)^2/n$，令 $g'(\rho)=1/(1-\rho^2)$，积分得 $g(\rho)=\operatorname{artanh}\rho$，方差约为 $1/n$，小样本修正为 $1/(n-3)$。

**置信区间**：$\operatorname{artanh}r\pm z_{1-\alpha/2}/\sqrt{n-3}$，再用 $\tanh$ 变回相关尺度。区间在 $z$ 尺度上的宽度为 $2z_{1-\alpha/2}/\sqrt{n-3}$，因此宽度减半需要 $n-3$ 增加到 4 倍。

**两个独立相关的比较**：$Z=(z_1-z_2)/\sqrt{1/(n_1-3)+1/(n_2-3)}$，与标准正态比较。

**自相关时间序列**：若两序列各自有自相关 $\rho_x(k)$、$\rho_y(k)$，在真实相关为 0 时，$r$ 的方差近似为 $\frac1n\big[1+2\sum_{k\ge1}\rho_x(k)\rho_y(k)\big]$，相当于有效样本量 $n_{\text{eff}}=n/\big[1+2\sum_k\rho_x(k)\rho_y(k)\big]$。对强自相关的 BOLD 信号，$n_{\text{eff}}$ 可远小于时间点数。

### B. 置换检验的有效性与 z 分数

**可交换性论证**：若零假设成立且观测在置换下可交换，则观测统计量 $X_0$ 与 $M$ 个置换统计量 $X_1,\dots,X_M$ 构成可交换序列，$X_0$ 在这 $M+1$ 个值中的秩在 $\{1,\dots,M+1\}$ 上均匀分布（忽略并列）。于是

$$
\Pr\!\Big(\hat p\le\alpha\Big)\le\alpha,\qquad \hat p=\frac{1+\#\{m:X_m\ge X_0\}}{M+1},
$$

即这个 $\hat p$ 在有限 $M$ 下也是精确有效的。若写成 $\#\{X_m\ge X_0\}/M$，$\hat p$ 可以为 0，检验会偏松。

**蒙特卡罗误差**：$\hat p$ 的标准误约为 $\sqrt{p(1-p)/M}$。$p=0.05$、$M=1000$ 时约为 0.007；若需要在多重比较后判断 $p$ 是否小于 $0.05/100$，$M$ 至少要达到数万。

**z 分数的局限**：$z=(X_0-\bar X)/s$ 只是标准化距离。零分布偏斜（例如稀疏网络的聚集系数）时，相同的 $z$ 对应的尾部概率可能相差很大；$s$ 很小时（零模型约束很强），微小的绝对差异也会给出很大的 $z$。报告时应同时给出 $X_0$、$\bar X$、$s$ 与经验 $p$ 值。

**最大统计量控制 FWE**：在每次置换中取所有检验统计量的最大值 $\max_j T_j^{(m)}$，以其 $1-\alpha$ 分位数 $c$ 作为共同阈值。零假设全真时，$\Pr(\exists j:T_j>c)=\Pr(\max_jT_j>c)\le\alpha$。NBS 用“最大分量大小”代替“最大统计量”，逻辑相同。

### C. BH 程序为什么控制 FDR

设 $m$ 个检验中 $m_0$ 个为真零假设，其 $p$ 值独立且服从 $U(0,1)$，并与假零假设的 $p$ 值独立。BH 拒绝集合为 $\{(1),\dots,(k)\}$，$k=\max\{i:p_{(i)}\le iq/m\}$。对每个真零假设 $j$，利用独立性可证明 $\mathbb E\big[\mathbf 1\{j\text{ 被拒绝}\}/\max(R,1)\big]=q/m$，其中 $R$ 为拒绝总数，对 $m_0$ 个真零假设求和得

$$
\mathrm{FDR}=\mathbb E\!\left[\frac{V}{\max(R,1)}\right]=\frac{m_0}{m}\,q\le q .
$$

网络中的边检验通常相关（共享节点的边相关更强），BH 在正相关依赖下仍然成立；依赖结构未知时可用 Benjamini–Yekutieli 版本，把 $q$ 替换为 $q/\sum_{i=1}^m i^{-1}$。

### D. 保度随机化：双边交换算法

```text
算法 1  双边交换（无向、无权、简单图）
输入：边列表 E（m 条边），每边平均交换次数 Q
输出：每个节点度与原图相同的随机图
1. 用哈希集合 H 存储 E，以 O(1) 判断边是否存在
2. 重复 Q·m 次：
3.     均匀随机抽两条不同的边 (a,b)、(c,d)
4.     以 1/2 概率把第二条边写作 (d,c)
5.     若 a,b,c,d 有重复节点，或 (a,d)、(c,b) 已在 H 中：拒绝本次交换，当前图保持不变
6.     否则删去 (a,b)、(c,d)，加入 (a,d)、(c,b)，同步更新 H
7. 返回 E
```

**度保持**：交换前后 $a,b,c,d$ 各失去一条边、得到一条边，所有节点的度不变。

**作为马尔可夫链**：每一步要么得到一个新图，要么留在原图。对给定度序列的全部简单图，这样的交换可以连通所有状态，因此链是不可约的；交换是对称的（从 $G$ 到 $G'$ 与从 $G'$ 到 $G$ 的提议概率相同），被拒绝的提议计为“停留”，于是均匀分布是平稳分布。实践中常见的错误是“拒绝后重新抽样直到成功”，这会改变平稳分布；有关不同实现与抽样空间的讨论见 Fosdick 等（2018）。

**混合与复杂度**：时间复杂度为 $O(Qm)$。$Q$ 太小时随机图保留原图结构的残余，可以监测聚集系数等指标随交换次数的变化，直到趋于平稳。若要求结果连通，交换后检查连通性并撤销导致断开的交换，代价是每步增加 $O(N+m)$。有向图用同样的方法交换“出端—入端”，可同时保持入度和出度。

### E. NBS 的置换算法

```text
算法 2  基于网络的统计（两组比较）
输入：每名被试的连接矩阵（Fisher z），组标签 g，主阈值 u，置换次数 B
输出：每个超阈值连通分量的 FWE 校正 p 值
1. 对每条边做两样本 t 检验，得到 t_ij
2. 保留 |t_ij| > u 的边，求连通分量 C_1, C_2, …，记录各分量边数 |C_k|
3. 对 b = 1..B：
4.     随机置换 g；重新计算全部 t_ij^(b)
5.     保留 |t_ij^(b)| > u 的边，求最大分量的边数 S_b
6. 对每个观测分量：p_k = (1 + #{b : S_b ≥ |C_k|}) / (B + 1)
复杂度：每次置换 O(n·N²) 计算检验统计量，加 O(N²) 求连通分量
```

有协变量时第 1 步改为一般线性模型，第 4 步改为置换残差。分量大小也可以用分量内统计量之和（“强度”）代替边数。

### F. 高斯情形下 GC 与转移熵的等价

设 $(X,Y,Z)$ 联合高斯平稳。记 $\mathcal P^-=\{Y^{(k)}_{t-1},Z^{(k)}_{t-1}\}$ 为不含 $X$ 的过去，$\mathcal P^+=\mathcal P^-\cup\{X^{(l)}_{t-1}\}$。高斯变量的条件分布仍是高斯的，其条件方差等于对条件变量做线性回归的残差方差，记为 $\sigma^2_-$、$\sigma^2_+$。一维高斯分布的熵为 $H=\tfrac12\ln(2\pi e\sigma^2)$，于是

$$
\mathrm{TE}_{X\to Y\mid Z}=H(Y_t\mid\mathcal P^-)-H(Y_t\mid\mathcal P^+)=\tfrac12\ln\frac{\sigma_-^2}{\sigma_+^2}=\tfrac12\,\mathcal F_{X\to Y\mid Z}.
$$

$2\pi e$ 在相减时消去。等价性只依赖联合高斯假设，不要求 VAR 是“真实”的生成机制（Barnett, Barrett & Seth, 2009）。代码示例中两种算法的数值完全一致。

**检验统计量**：完整模型比受限模型多 $p$ 个参数。零假设 $b_1=\dots=b_p=0$ 下，$F=\frac{(\mathrm{RSS}_r-\mathrm{RSS}_f)/p}{\mathrm{RSS}_f/(T'-q_f)}\sim F_{p,T'-q_f}$（$T'=T-p$，$q_f$ 为完整模型参数个数）；由于 $\hat{\mathcal F}$ 较小时 $\hat{\mathcal F}\approx(\mathrm{RSS}_r-\mathrm{RSS}_f)/\mathrm{RSS}_f$，$T'\hat{\mathcal F}$ 近似服从 $\chi^2_p$。残差自相关或非平稳时，应改用基于替代数据（surrogate）的置换检验。

### G. 随机节点采样下的度分布

设全网度分布 $P(k)$，生成函数 $G_0(x)=\sum_k P(k)x^k$。每个节点独立以概率 $p$ 被保留。对一个被保留、真实度为 $k$ 的节点，它的 $k$ 个邻居各自独立以概率 $p$ 被保留，因此观测度 $k'\mid k\sim\mathrm{Binomial}(k,p)$，

$$
P'(k')=\sum_{k\ge k'}P(k)\binom{k}{k'}p^{k'}(1-p)^{k-k'} .
$$

二项分布的生成函数为 $(1-p+px)^k$，对 $k$ 取期望得

$$
G'_0(x)=\sum_k P(k)(1-p+px)^k=G_0(1-p+px).
$$

对 $x$ 求导并令 $x=1$，得 $\langle k'\rangle=p\,G_0'(1)=p\langle k\rangle$；令 $x=0$，得被保留节点中孤立点的比例 $P'(0)=G_0(1-p)$。

**封闭性**：若 $P(k)$ 为泊松分布，$G_0(x)=e^{\langle k\rangle(x-1)}$，则 $G'_0(x)=e^{p\langle k\rangle(x-1)}$，仍是泊松分布，只是均值变为 $p\langle k\rangle$。若 $P(k)\propto k^{-\gamma}$，$G_0(1-p+px)$ 一般不再对应幂律：小 $k'$ 处的分布由二项稀释主导而明显弯曲，严格的幂律形式只在大 $k'$ 的尾部近似保留。这就是 Stumpf 等（2005）“无标度网络的子网不是无标度的”这一结论的来源。随机边采样在度分布上给出同样的稀释公式（以 $q$ 代替 $p$），但不产生节点缺失。代码示例中，用上式预测的 $P'(k')$ 与一次采样的经验分布基本一致。

### H. 样本量公式与信度衰减

**单条相关**：备择 $\rho$ 下 $\sqrt{n-3}\,\operatorname{artanh}r\approx N\big(\sqrt{n-3}\operatorname{artanh}\rho,1\big)$。要以概率 $1-\beta$ 超过临界值 $z_{1-\alpha/2}$，需 $\sqrt{n-3}\operatorname{artanh}\rho\ge z_{1-\alpha/2}+z_{1-\beta}$，即正文公式（忽略另一侧尾部）。多元正态下，控制 $c$ 个变量的样本偏相关与样本量为 $n-c$ 的普通样本相关同分布，故其 Fisher $z$ 方差约为 $1/(n-c-3)$。

**信度衰减**：设 $x=x^*+e_x$、$y=y^*+e_y$，误差独立且与真分数无关，信度 $r_{xx}=\operatorname{Var}(x^*)/\operatorname{Var}(x)$。协方差不变而标准差分别放大 $1/\sqrt{r_{xx}}$、$1/\sqrt{r_{yy}}$，故 $\rho_{xy}=\rho_{x^*y^*}\sqrt{r_{xx}r_{yy}}$。

## 研究前沿与开放问题 {#frontiers}

1. **把网络当作待估计的未知量**。贝叶斯网络重建把观测、测量误差与网络结构放进同一生成模型（Newman, 2018；Peixoto, 2018；Peixoto, 2019, *Physical Review Letters* 从动力学同时重建网络与社团），网络后验使后续指标自带不确定性；如何扩展到上万节点的脑与组学数据仍待解决。
2. **从观测到干预**。GC、TE 受采样、噪声与未观测变量限制；单细胞大规模扰动筛选（如 Perturb-seq; Dixit 等, 2016, *Cell*）为调控网络提供干预数据。如何在有限扰动预算下结合干预与观测数据识别方向，是活跃问题。
3. **个体网络与精密测量**。组水平的脑–表型效应很小；对少数个体长时间反复采集可得到高信度的个体网络。两种设计各能回答什么、个体网络的结论如何推广，尚无共识。
4. **超越成对关系**。许多生物过程涉及多个分子或脑区同时参与（Battiston 等, 2020, *Physics Reports*）；从数据推断高阶相互作用需要多得多的数据，相应的零模型与检验刚刚起步。
5. **网络比较的统计理论**。图距离与图核大多是描述性的，缺少在生成模型下的分布理论；Hartle 等（2020）的集合内图距离提供了基准，但“距离显著”对应何种结构差异仍难解释。
6. **零模型的组合**。同时保持度、强度、空间与相关结构等多种约束的抽样往往困难，不同零模型还可能给出矛盾结论；如何预先规定零模型层级，仍未标准化（Váša & Mišić, 2022）。

## 生物医学应用 {#biomedical}

::: {.callout-bio}
**脑网络的组间比较。** 静息态功能连接研究中，常见的流程是：每名被试按图谱提取时间序列，计算 Fisher $z$ 相关矩阵，再在边层面用 NBS 或 FDR 做组间比较，在全局层面在一段密度范围内比较效率、模块度等。Fornito、Zalesky 与 Breakspear（2013, *NeuroImage*）系统讨论了这一流程中节点定义、阈值、零模型与组间比较的陷阱。可信的结论通常同时满足：密度或整体连接强度被控制，头动被匹配或作为协变量，结果在阈值范围内方向一致。详见 [脑连接组](brain-connectome.html)。
:::

**症状网络的稳定性检验。** 心理网络研究普遍采用 EBICglasso 估计正则化偏相关网络，再用 bootstrap 报告边权区间、用病例删除计算中心性的 CS 系数、用 NCT 比较不同人群的网络（Epskamp, Borsboom & Fried, 2018；[论文精读](paper-epskamp2018_accuracy.html)）。中心性指标本身的解释局限见 Bringmann 等（2019, *Journal of Abnormal Psychology*）与 [症状网络](symptom-networks.html)。

**共表达网络。** WGCNA（Langfelder & Horvath, 2008, *BMC Bioinformatics*）用软阈值把相关转为连续的邻接权重，避免硬阈值；模块与性状的关联需要在独立数据集中复现。去除批次和细胞组成等混杂会显著改变网络结构（Parsana 等, 2019）。推断方法的整体评估见 Marbach 等（2012, *Nature Methods*；[论文精读](paper-marbach2012_wisdom.html)）。

**定向脑网络。** 在时间分辨率高的电生理数据（EEG/MEG、颅内脑电）中，Granger 因果与转移熵被用来估计脑区之间的定向交互；在 fMRI 中，方向推断受血流动力学延迟、降采样与噪声限制，基于生成模型的 DCM 更常用于少数脑区的假设检验（Seth, Barrett & Barnett, 2015；Friston, Harrison & Penny, 2003）。无论哪种方法，有向边都应与“对称连接 + 零模型”的结果并列报告，并说明方向结论依赖的假设。见 [从时间序列推断有向边](network-construction.directed-edges.html)。

**部分相互作用组的拓扑。** Han 等（2005）与 Stumpf 等（2005）的采样分析说明，部分采样既可能掩盖、也可能“制造”幂律外观，对覆盖率有限的图谱做拓扑外推需要按采样过程建模（见 [采样网络与不完整观测](network-construction.sampling-incomplete.html)）。

**相互作用网络与疾病模块。** 网络医学研究把疾病基因映射到相互作用组上，检验它们是否形成连通的模块，常用的零模型是随机抽取同样数量、度分布相近的基因（Barabási, Gulbahce & Loscalzo, 2011, *Nature Reviews Genetics*）。由于研究偏倚，度匹配的抽样是必需的；用系统筛选的二元相互作用数据复核结论，可以检验结论是否依赖文献热度（Menche 等, 2015；[论文精读](paper-menche2015_interactome.html)）。

## 适用范围与常见误用 {#limitations}

1. **误用**：把相关网络的边解释为直接作用或信息通路。→ **正解**：相关包含间接关联；偏相关去掉了一部分间接关联，但可能引入对撞偏倚；直接作用需要物理连接证据，方向需要时间顺序或干预证据。
2. **误用**：选一个“常用阈值”构网，然后比较组间拓扑。→ **正解**：先说明密度是否匹配；在一段预先确定的密度范围内报告结果，或使用加权指标，并把整体连接强度作为协变量。
3. **误用**：只与 ER 随机图比较就宣称“非随机组织”。→ **正解**：ER 只保留边数。度分布、空间嵌入、相关矩阵的传递性都可能解释观察到的结构，应与保留这些性质的零模型比较，并写明零模型保留了什么。
4. **误用**：报告 $z$ 分数很大，就认为差异在生物学上很重要。→ **正解**：$z$ 分数依赖零分布的离散程度，约束越强的零模型方差越小，$z$ 越容易很大；要同时报告效应量和经验 $p$ 值。
5. **误用**：NBS 显著后，逐条列出“显著的边”并解释其功能。→ **正解**：NBS 只支持子网络层面的结论；若需要边层面的结论，应使用控制边层面错误率的方法。
6. **误用**：在 PPI 网络中发现“疾病基因的度更高”，据此认为疾病基因是网络枢纽。→ **正解**：先控制研究热度（文献数量）或改用系统筛选数据；功能预测要与“只按度排序”的基线比较。
7. **误用**：bootstrap 时只重抽样数据，沿用全样本选定的正则化参数或阈值。→ **正解**：整个估计流程都应放入重抽样循环，否则会低估不稳定性。
8. **误用**：把时间点当作独立样本计算单被试的显著性。→ **正解**：时间序列存在自相关，应使用有效样本量，或在被试层面做组分析。
9. **误用**：两两 Granger 因果显著，就画出有向箭头并解释为“信息流”。→ **正解**：先用条件 GC 排除已观测的共同驱动；说明采样率、测量噪声与未观测变量可能造成的假方向；在 fMRI 中尤其谨慎。
10. **误用**：在部分相互作用图谱上拟合出幂律，就宣称完整相互作用组是无标度的。→ **正解**：随机子网的度分布一般与全网不同族；外推需要按采样过程建模，并报告覆盖率。
11. **误用**：只报告网络指标的点估计，或 bootstrap 时逐时间点重抽样。→ **正解**：把整个构网流程放进重抽样循环，时间序列用块 bootstrap；区分“指标的均值”与“均值网络的指标”。
12. **误用**：用“每个参数需要若干被试”的经验规则确定网络研究的样本量。→ **正解**：单条边可用 Fisher $z$ 公式计算；整网的边恢复与中心性稳定性应按预期网络结构做模拟功效分析，并考虑测量信度。
13. **误用**：报告“两组网络的谱距离为某值”就认为网络不同。→ **正解**：距离需要参照：与零模型或组内距离比较，用置换检验评估；并说明所选距离对哪种结构差异敏感。

适用范围方面，本专题的方法主要针对由变量间关联构建的网络（功能连接、症状网络、共表达）和由数据库整合构建的网络（相互作用组）。对直接测量的网络（如电镜重建的突触连接组），误差主要来自分割与重建，验证手段不同，但零模型与多重比较的原则同样适用。

## 关联知识 {#related}

- [网络结构指标与随机图](network-metrics.html)：本专题检验的各种指标的定义，以及作为最基本零模型的 ER 随机图。
- [小世界与无标度网络模型](network-models.html)：小世界系数 $\sigma$、$\omega$ 的归一化都依赖零模型；度分布的统计检验。
- [社团结构与社区发现](community-structure.html)：模块度的期望项来自配置模型，模块划分的显著性需要零模型比较。
- [脑连接组：结构与功能连接](brain-connectome.html)：脑图谱、功能连接估计、阈值与头动控制在脑影像中的具体实施。
- [症状网络与网络精神病学](symptom-networks.html)：EBICglasso、中心性、CS 系数与网络比较检验。
- [基因调控网络推断与共表达分析](gene-network-inference.html)：互信息、WGCNA 软阈值与推断网络的金标准评估。
- [疾病模块、网络邻近度与药物重定位](network-medicine.html)：不完整相互作用组、度匹配的零模型与网络邻近度的显著性。
- [动态功能连接与多层脑网络](dynamic-brain-networks.html)：滑动窗口连接的有限样本波动与平稳零模型，与本专题的有向边推断、不确定性传播相衔接。
- [研究问题、可复现分析与敏感性分析](reproducible-research.html)：把本专题的检验写进预先确定的分析计划与报告。

## 核心文献 {#references}

**零模型**

- Maslov S, Sneppen K. Specificity and stability in topology of protein networks. *Science*, 2002, 296: 910–913. DOI: [10.1126/science.1065103](https://doi.org/10.1126/science.1065103)
- Molloy M, Reed B. A critical point for random graphs with a given degree sequence. *Random Structures & Algorithms*, 1995, 6: 161–180. DOI: [10.1002/rsa.3240060204](https://doi.org/10.1002/rsa.3240060204)
- Fosdick BK, Larremore DB, Nishimura J, Ugander J. Configuring random graph models with fixed degree sequences. *SIAM Review*, 2018, 60: 315–355. DOI: [10.1137/16M1087175](https://doi.org/10.1137/16M1087175)
- Rubinov M, Sporns O. Weight-conserving characterization of complex functional brain networks. *NeuroImage*, 2011, 56: 2068–2079. DOI: [10.1016/j.neuroimage.2011.03.069](https://doi.org/10.1016/j.neuroimage.2011.03.069)
- Zalesky A, Fornito A, Bullmore E. On the use of correlation as a measure of network connectivity. *NeuroImage*, 2012, 60: 2096–2106. DOI: [10.1016/j.neuroimage.2012.02.001](https://doi.org/10.1016/j.neuroimage.2012.02.001)
- Alexander-Bloch AF, Shou H, Liu S, et al. On testing for spatial correspondence between maps of human brain structure and function. *NeuroImage*, 2018, 178: 540–551. DOI: [10.1016/j.neuroimage.2018.05.070](https://doi.org/10.1016/j.neuroimage.2018.05.070)
- Váša F, Mišić B. Null models in network neuroscience. *Nature Reviews Neuroscience*, 2022, 23: 493–504. DOI: [10.1038/s41583-022-00601-9](https://doi.org/10.1038/s41583-022-00601-9)

**连接估计与阈值**

- Fisher RA. Frequency distribution of the values of the correlation coefficient in samples from an indefinitely large population. *Biometrika*, 1915, 10: 507–521. DOI: [10.2307/2331838](https://doi.org/10.2307/2331838)
- Ledoit O, Wolf M. A well-conditioned estimator for large-dimensional covariance matrices. *Journal of Multivariate Analysis*, 2004, 88: 365–411. DOI: [10.1016/S0047-259X(03)00096-4](https://doi.org/10.1016/S0047-259X(03)00096-4)
- Friedman J, Hastie T, Tibshirani R. Sparse inverse covariance estimation with the graphical lasso. *Biostatistics*, 2008, 9: 432–441. DOI: [10.1093/biostatistics/kxm045](https://doi.org/10.1093/biostatistics/kxm045)
- Smith SM, Miller KL, Salimi-Khorshidi G, et al. Network modelling methods for FMRI. *NeuroImage*, 2011, 54: 875–891. DOI: [10.1016/j.neuroimage.2010.08.063](https://doi.org/10.1016/j.neuroimage.2010.08.063)
- van Wijk BCM, Stam CJ, Daffertshofer A. Comparing brain networks of different size and connectivity density using graph theory. *PLoS ONE*, 2010, 5: e13701. DOI: [10.1371/journal.pone.0013701](https://doi.org/10.1371/journal.pone.0013701)
- van den Heuvel MP, de Lange SC, Zalesky A, et al. Proportional thresholding in resting-state fMRI functional connectivity networks and consequences for patient-control connectome studies: issues and recommendations. *NeuroImage*, 2017, 152: 437–449. DOI: [10.1016/j.neuroimage.2017.02.005](https://doi.org/10.1016/j.neuroimage.2017.02.005)
- Tewarie P, van Dellen E, Hillebrand A, Stam CJ. The minimum spanning tree: an unbiased method for brain network analysis. *NeuroImage*, 2015, 104: 177–188. DOI: [10.1016/j.neuroimage.2014.10.015](https://doi.org/10.1016/j.neuroimage.2014.10.015)

**统计推断**

- Benjamini Y, Hochberg Y. Controlling the false discovery rate: a practical and powerful approach to multiple testing. *Journal of the Royal Statistical Society: Series B*, 1995, 57: 289–300. DOI: [10.1111/j.2517-6161.1995.tb02031.x](https://doi.org/10.1111/j.2517-6161.1995.tb02031.x)
- Nichols TE, Holmes AP. Nonparametric permutation tests for functional neuroimaging: a primer with examples. *Human Brain Mapping*, 2002, 15: 1–25. DOI: [10.1002/hbm.1058](https://doi.org/10.1002/hbm.1058)
- Zalesky A, Fornito A, Bullmore ET. Network-based statistic: identifying differences in brain networks. *NeuroImage*, 2010, 53: 1197–1207. DOI: [10.1016/j.neuroimage.2010.06.041](https://doi.org/10.1016/j.neuroimage.2010.06.041)
- Phipson B, Smyth GK. Permutation p-values should never be zero: calculating exact p-values when permutations are randomly drawn. *Statistical Applications in Genetics and Molecular Biology*, 2010, 9. DOI: [10.2202/1544-6115.1585](https://doi.org/10.2202/1544-6115.1585)
- Winkler AM, Ridgway GR, Webster MA, et al. Permutation inference for the general linear model. *NeuroImage*, 2014, 92: 381–397. DOI: [10.1016/j.neuroimage.2014.01.060](https://doi.org/10.1016/j.neuroimage.2014.01.060)
- van Borkulo CD, van Bork R, Boschloo L, et al. Comparing network structures on three aspects: a permutation test. *Psychological Methods*, 2023, 28: 1273–1285. DOI: [10.1037/met0000476](https://doi.org/10.1037/met0000476)

**有向边推断**

- Granger CWJ. Investigating causal relations by econometric models and cross-spectral methods. *Econometrica*, 1969, 37: 424–438. DOI: [10.2307/1912791](https://doi.org/10.2307/1912791)
- Geweke J. Measurement of linear dependence and feedback between multiple time series. *Journal of the American Statistical Association*, 1982, 77: 304–313. DOI: [10.1080/01621459.1982.10477803](https://doi.org/10.1080/01621459.1982.10477803)
- Schreiber T. Measuring information transfer. *Physical Review Letters*, 2000, 85: 461–464. DOI: [10.1103/PhysRevLett.85.461](https://doi.org/10.1103/PhysRevLett.85.461)
- Barnett L, Barrett AB, Seth AK. Granger causality and transfer entropy are equivalent for Gaussian variables. *Physical Review Letters*, 2009, 103: 238701. DOI: [10.1103/PhysRevLett.103.238701](https://doi.org/10.1103/PhysRevLett.103.238701)
- Friston KJ, Harrison L, Penny W. Dynamic causal modelling. *NeuroImage*, 2003, 19: 1273–1302. DOI: [10.1016/S1053-8119(03)00202-7](https://doi.org/10.1016/S1053-8119(03)00202-7)
- Friston KJ. Functional and effective connectivity: a review. *Brain Connectivity*, 2011, 1: 13–36. DOI: [10.1089/brain.2011.0008](https://doi.org/10.1089/brain.2011.0008)
- Vicente R, Wibral M, Lindner M, Pipa G. Transfer entropy—a model-free measure of effective connectivity for the neurosciences. *Journal of Computational Neuroscience*, 2011, 30: 45–67. DOI: [10.1007/s10827-010-0262-3](https://doi.org/10.1007/s10827-010-0262-3)
- Seth AK, Chorley P, Barnett LC. Granger causality analysis of fMRI BOLD signals is invariant to hemodynamic convolution but not downsampling. *NeuroImage*, 2013, 65: 540–555. DOI: [10.1016/j.neuroimage.2012.09.049](https://doi.org/10.1016/j.neuroimage.2012.09.049)
- Seth AK, Barrett AB, Barnett L. Granger causality analysis in neuroscience and neuroimaging. *Journal of Neuroscience*, 2015, 35: 3293–3297. DOI: [10.1523/JNEUROSCI.4399-14.2015](https://doi.org/10.1523/JNEUROSCI.4399-14.2015)

**采样、测量误差与网络重建**

- Stumpf MPH, Wiuf C, May RM. Subnets of scale-free networks are not scale-free: sampling properties of networks. *PNAS*, 2005, 102: 4221–4224. DOI: [10.1073/pnas.0501179102](https://doi.org/10.1073/pnas.0501179102)
- Han JDJ, Dupuy D, Bertin N, et al. Effect of sampling on topology predictions of protein-protein interaction networks. *Nature Biotechnology*, 2005, 23: 839–844. DOI: [10.1038/nbt1116](https://doi.org/10.1038/nbt1116)
- Lee SH, Kim PJ, Jeong H. Statistical properties of sampled networks. *Physical Review E*, 2006, 73: 016102. DOI: [10.1103/PhysRevE.73.016102](https://doi.org/10.1103/PhysRevE.73.016102)
- Kossinets G. Effects of missing data in social networks. *Social Networks*, 2006, 28: 247–268. DOI: [10.1016/j.socnet.2005.07.002](https://doi.org/10.1016/j.socnet.2005.07.002)
- Stumpf MPH, Thorne T, de Silva E, et al. Estimating the size of the human interactome. *PNAS*, 2008, 105: 6959–6964. DOI: [10.1073/pnas.0708078105](https://doi.org/10.1073/pnas.0708078105)
- Newman MEJ. Network structure from rich but noisy data. *Nature Physics*, 2018, 14: 542–545. DOI: [10.1038/s41567-018-0076-1](https://doi.org/10.1038/s41567-018-0076-1)
- Peixoto TP. Reconstructing networks with unknown and heterogeneous errors. *Physical Review X*, 2018, 8: 041011. DOI: [10.1103/PhysRevX.8.041011](https://doi.org/10.1103/PhysRevX.8.041011)
- Peixoto TP. Network reconstruction and community detection from dynamics. *Physical Review Letters*, 2019, 123: 128301. DOI: [10.1103/PhysRevLett.123.128301](https://doi.org/10.1103/PhysRevLett.123.128301)

**网络比较**

- Tantardini M, Ieva F, Tajoli L, Piccardi C. Comparing methods for comparing networks. *Scientific Reports*, 2019, 9: 17557. DOI: [10.1038/s41598-019-53708-y](https://doi.org/10.1038/s41598-019-53708-y)
- Wilson RC, Zhu P. A study of graph spectra for comparing graphs and trees. *Pattern Recognition*, 2008, 41: 2833–2841. DOI: [10.1016/j.patcog.2008.03.011](https://doi.org/10.1016/j.patcog.2008.03.011)
- Pržulj N. Biological network comparison using graphlet degree distribution. *Bioinformatics*, 2007, 23: e177–e183. DOI: [10.1093/bioinformatics/btl301](https://doi.org/10.1093/bioinformatics/btl301)
- Yaveroğlu ÖN, Malod-Dognin N, Davis D, et al. Revealing the hidden language of complex networks. *Scientific Reports*, 2014, 4: 4547. DOI: [10.1038/srep04547](https://doi.org/10.1038/srep04547)
- Koutra D, Shah N, Vogelstein JT, Gallagher B, Faloutsos C. DeltaCon: principled massive-graph similarity function with attribution. *ACM Transactions on Knowledge Discovery from Data*, 2016, 10: 1–43. DOI: [10.1145/2824443](https://doi.org/10.1145/2824443)
- Kriege NM, Johansson FD, Morris C. A survey on graph kernels. *Applied Network Science*, 2020, 5: 6. DOI: [10.1007/s41109-019-0195-3](https://doi.org/10.1007/s41109-019-0195-3)
- Bagrow JP, Bollt EM. An information-theoretic, all-scales approach to comparing networks. *Applied Network Science*, 2019, 4: 45. DOI: [10.1007/s41109-019-0156-x](https://doi.org/10.1007/s41109-019-0156-x)
- Hartle H, Klein B, McCabe S, et al. Network comparison and the within-ensemble graph distance. *Proceedings of the Royal Society A*, 2020, 476: 20190744. DOI: [10.1098/rspa.2019.0744](https://doi.org/10.1098/rspa.2019.0744)

**样本量、信度与前沿**

- Spearman C. The proof and measurement of association between two things. *American Journal of Psychology*, 1904, 15: 72–101. DOI: [10.2307/1412159](https://doi.org/10.2307/1412159)
- Epskamp S, Fried EI. A tutorial on regularized partial correlation networks. *Psychological Methods*, 2018, 23: 617–634. DOI: [10.1037/met0000167](https://doi.org/10.1037/met0000167)
- Constantin MA, Schuurman NK, Vermunt JK. A general Monte Carlo method for sample size analysis in the context of network models. *Psychological Methods*, 2026, 31: 385–405. DOI: [10.1037/met0000555](https://doi.org/10.1037/met0000555)
- Birn RM, Molloy EK, Patriat R, et al. The effect of scan length on the reliability of resting-state fMRI connectivity estimates. *NeuroImage*, 2013, 83: 550–558. DOI: [10.1016/j.neuroimage.2013.05.099](https://doi.org/10.1016/j.neuroimage.2013.05.099)
- Battiston F, Cencetti G, Iacopini I, et al. Networks beyond pairwise interactions: structure and dynamics. *Physics Reports*, 2020, 874: 1–92. DOI: [10.1016/j.physrep.2020.05.004](https://doi.org/10.1016/j.physrep.2020.05.004)
- Dixit A, Parnas O, Li B, et al. Perturb-Seq: dissecting molecular circuits with scalable single-cell RNA profiling of pooled genetic screens. *Cell*, 2016, 167: 1853–1866. DOI: [10.1016/j.cell.2016.11.038](https://doi.org/10.1016/j.cell.2016.11.038)

**偏倚、稳定性与综述**

- Gillis J, Pavlidis P. The impact of multifunctional genes on “guilt by association” analysis. *PLoS ONE*, 2011, 6: e17258. DOI: [10.1371/journal.pone.0017258](https://doi.org/10.1371/journal.pone.0017258)
- Gillis J, Pavlidis P. “Guilt by association” is the exception rather than the rule in gene networks. *PLoS Computational Biology*, 2012, 8: e1002444. DOI: [10.1371/journal.pcbi.1002444](https://doi.org/10.1371/journal.pcbi.1002444)
- Luck K, Kim DK, Lambourne L, et al. A reference map of the human binary protein interactome. *Nature*, 2020, 580: 402–408. DOI: [10.1038/s41586-020-2188-x](https://doi.org/10.1038/s41586-020-2188-x)
- Power JD, Barnes KA, Snyder AZ, et al. Spurious but systematic correlations in functional connectivity MRI networks arise from subject motion. *NeuroImage*, 2012, 59: 2142–2154. DOI: [10.1016/j.neuroimage.2011.10.018](https://doi.org/10.1016/j.neuroimage.2011.10.018)
- Efron B. Bootstrap methods: another look at the jackknife. *Annals of Statistics*, 1979, 7: 1–26. DOI: [10.1214/aos/1176344552](https://doi.org/10.1214/aos/1176344552)
- Epskamp S, Borsboom D, Fried EI. Estimating psychological networks and their accuracy: a tutorial paper. *Behavior Research Methods*, 2018, 50: 195–212. DOI: [10.3758/s13428-017-0862-1](https://doi.org/10.3758/s13428-017-0862-1)
- Noble S, Scheinost D, Constable RT. A decade of test-retest reliability of functional connectivity: a systematic review and meta-analysis. *NeuroImage*, 2019, 203: 116157. DOI: [10.1016/j.neuroimage.2019.116157](https://doi.org/10.1016/j.neuroimage.2019.116157)
- Fornito A, Zalesky A, Breakspear M. Graph analysis of the human connectome: promise, progress, and pitfalls. *NeuroImage*, 2013, 80: 426–444. DOI: [10.1016/j.neuroimage.2013.04.087](https://doi.org/10.1016/j.neuroimage.2013.04.087)

## 延伸资源 {#resources}

| 类型 | 资源 | 说明 |
|---|---|---|
| 综述 | Váša & Mišić 2022，[doi.org/10.1038/s41583-022-00601-9](https://doi.org/10.1038/s41583-022-00601-9) | 网络神经科学中零模型的分类与选择，适合作为零模型部分的总纲 |
| 综述 | Fornito, Zalesky & Breakspear 2013，[doi.org/10.1016/j.neuroimage.2013.04.087](https://doi.org/10.1016/j.neuroimage.2013.04.087) | 脑网络构建全流程的陷阱，节点、边、阈值、组间比较逐一讨论 |
| 方法 | Fosdick 等 2018，[doi.org/10.1137/16M1087175](https://doi.org/10.1137/16M1087175) | 配置模型与双边交换抽样的严格讨论，适合需要自己实现零模型时阅读 |
| 教程 | Epskamp, Borsboom & Fried 2018，[doi.org/10.3758/s13428-017-0862-1](https://doi.org/10.3758/s13428-017-0862-1) | 边权 bootstrap、病例删除与 CS 系数的完整示范（开放获取） |
| 工具 | [Brain Connectivity Toolbox](https://sites.google.com/site/bctnet/)（MATLAB）/ [bctpy](https://github.com/aestrivex/bctpy)（Python） | 网络指标与多种零模型（含加权、带符号版本）的实现 |
| 工具 | [netneurotools](https://netneurotools.readthedocs.io/) | Python 工具包，包含空间置换检验等零模型 |
| 工具 | R 包 [bootnet](https://cran.r-project.org/package=bootnet) | 心理网络的估计、bootstrap 与稳定性分析 |
| 教材 | Barabási, *Network Science*, Ch. 4 The Scale-Free Property（4.8 节：生成任意度分布的网络，含配置模型与保度随机化），[networksciencebook.com/chapter/4](http://networksciencebook.com/chapter/4) | 配置模型、完全随机化与保度随机化的图示讲解（CC BY-NC-SA 2.0）；Ch. 3 Random Networks 给出 ER 零模型的基本性质 |
| 教材 | Fornito A, Zalesky A, Bullmore ET. *Fundamentals of Brain Network Analysis*. Academic Press, 2016 | 脑网络中节点与边的定义、连接矩阵、零模型与统计连接组学的系统讲解 |
| 教材 | Newman MEJ. *Networks*（第 2 版）. Oxford University Press, 2018 | 网络统计量与测量误差的章节讨论误差类型、来源、估计与校正 |
| 综述 | Seth, Barrett & Barnett 2015，[doi.org/10.1523/JNEUROSCI.4399-14.2015](https://doi.org/10.1523/JNEUROSCI.4399-14.2015) | Granger 因果在神经科学中的使用条件与常见误解，篇幅短，适合入门 |
| 方法 | Tantardini 等 2019，[doi.org/10.1038/s41598-019-53708-y](https://doi.org/10.1038/s41598-019-53708-y) | 网络比较方法的分类（节点是否对应）与在合成网络上的系统比较 |
| 工具 | [netrd](https://netrd.readthedocs.io/)（Python） | 实现了数十种图距离与从时间序列重建网络的方法，可用于比较不同距离的行为 |
| 工具 | [graph-tool](https://graph-tool.skewed.de/)（Python） | 包含 Peixoto 的贝叶斯网络重建与随机块模型推断 |
| 数据 | [BioGRID](https://thebiogrid.org/) / [STRING](https://string-db.org/) | 两类不同性质的相互作用数据库：前者为整理的实验证据，后者为整合的功能关联得分；可用来比较构网选择对结论的影响 |

## 开放问题 {#questions}

1. 在你的数据中，“边”属于物理连接、统计关联、功能关联还是有向关系？如果要把它换成另一类边（例如从功能连接换成结构连接，或从文献整理的相互作用换成系统筛选数据），你预期哪些结论会改变？
2. 对同一个网络指标，ER、保度随机化和空间约束零模型可能给出相互矛盾的结论。你会怎样预先规定零模型，并在结果不一致时如何解读？
3. 当样本量只够估计一个稀疏的正则化网络时，“这条边不存在”的证据强度有多大？有没有办法区分“条件独立”与“功效不足”？
4. 研究偏倚、头动和批次效应都是与生物学变量相关的系统误差。在你熟悉的数据类型中，哪一种系统误差最可能被误读为生物学发现？可以设计什么样的阴性对照来检验？
5. 你的网络只观测了真实系统的一部分（部分基因、部分脑区、部分条目）。若采样比例减半，你的主要结论会如何变化？能否用进一步删除节点或边的模拟来回答？
6. 若要声称“A 脑区驱动 B 脑区”，你的数据的采样间隔、测量噪声与可能遗漏的脑区是否允许这一结论？有哪些干预或对照分析可以加强它？
