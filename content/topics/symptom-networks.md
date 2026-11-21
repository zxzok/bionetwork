---
id: symptom-networks
title: 症状网络与网络精神病学
en: Symptom networks and network psychiatry
domain: symptom
legacy: L11
summary: 把症状视为相互作用的网络节点，估计偏相关、Ising 与时间序列网络，并检验中心性、稳定性与组间差异。
keywords: [网络精神病学, 症状网络, 高斯图模型, 偏相关, EBICglasso, Ising 模型, 混合图模型, 可预测性, 强度中心性, 预期影响, 桥中心性, 共病, bootstrap, CS 系数, 网络比较检验, 经验取样, mlVAR, GVAR, 横截滞后面板网络, 网络干预分析, 模块控制]
synonyms: [network psychiatry, network psychometrics, 网络心理测量学, symptom network, 共同原因模型, common cause model, 潜变量模型, latent variable model, reflective model, 局部独立性, local independence, Gaussian graphical model, GGM, 高斯图模型, partial correlation, 偏相关, 精度矩阵, precision matrix, 条件独立, conditional independence, graphical LASSO, glasso, 图形 LASSO, EBIC, extended BIC, 扩展贝叶斯信息准则, EBICglasso, ggmModSelect, 收缩偏倚, shrinkage, Ising model, Ising 模型, 二值数据, binary data, eLasso, IsingFit, 逐节点回归, nodewise regression, neighborhood selection, 邻域选择, AND 规则, OR 规则, mixed graphical model, MGM, mgm, 混合图模型, predictability, 可预测性, 多分格相关, polychoric correlation, strength, 强度中心性, expected influence, EI, 预期影响, bridge centrality, bridge strength, bridge expected influence, 桥中心性, 桥梁中心性, 桥强度, 桥症状, comorbidity, 共病, bootnet, qgraph, networktools, goldbricker, psychonetrics, CS 系数, correlation stability coefficient, case-dropping bootstrap, 病例删除, netSimulator, 样本量, network comparison test, NCT, NetworkComparisonTest, 网络比较检验, 网络结构不变性, 全局强度不变性, global strength, moderated network model, 调节网络模型, ESM, EMA, 经验取样, 生态瞬时评估, experience sampling, VAR, 向量自回归, mlVAR, 多层 VAR, GVAR, graphical VAR, 时间网络, temporal network, 同期网络, contemporaneous network, 个体间网络, between-subjects network, 个体内, within-person, 个体中心化, ergodicity, 遍历性, idiographic, 个体化网络, cross-lagged panel network, CLPN, 横截滞后面板网络, panel-GVAR, RI-CLPM, network intervention analysis, NIA, 网络干预分析, CBT-I, 替代稳定态, 滞后, hysteresis, 临界慢化, critical slowing down, 对撞偏倚, collider bias, 可重复性, replicability, 中心性假说, centrality hypothesis, 模块控制, module control, 最小支配集, MDSet, AMCS, PHQ-9, GAD-7, ISI, PSS-14]
demos: [symptom]
reviewed: 2026-11-15
---

## 概述 {#overview}

[脑连接组](brain-connectome.html)与[动态脑网络](dynamic-brain-networks.html)中的节点是脑区，边来自影像信号。症状网络的节点换成了**症状**：失眠、情绪低落、疲乏、注意力差……边是症状之间的统计关联。这个看似简单的转换背后，是对“精神疾病是什么”的一种不同理解，被称为**网络精神病学**（network psychiatry）或网络心理测量学（network psychometrics）。Borsboom 等（2021, *Nature Reviews Methods Primers*）对这一方法体系做了系统综述：从多元数据中估计变量之间的条件依赖网络，再对网络结构做描述、比较和推断。

本专题按“理论—估计—推断—动态与干预—争议”组织：

- **理论**：[共同原因模型与网络理论](symptom-networks.network-theory.html)，说明为什么要把症状看成网络，以及“替代稳定态”“滞后”等复杂系统概念如何进入精神病理学；
- **估计**：连续/有序数据的[偏相关与高斯图模型](symptom-networks.gaussian-graphical-model.html)与[正则化估计](symptom-networks.regularization.html)；二值数据的 [Ising 模型](symptom-networks.ising-model.html)；混合类型数据的[混合图模型与可预测性](symptom-networks.mixed-graphical-models.html)；
- **解读与推断**：贯穿全专题的[横断面统计依赖与因果作用](symptom-networks.dependence-vs-causation.html)之分；[症状中心性](symptom-networks.centrality.html)、[桥中心性与共病](symptom-networks.bridge-centrality.html)；[抽样不确定性与稳定性](symptom-networks.stability.html)、[样本量与估计方法的选择](symptom-networks.sample-size.html)、[网络比较](symptom-networks.network-comparison.html)；
- **动态与干预**：[个体动态网络（ESM、mlVAR、GVAR）](symptom-networks.temporal-networks.html)、[面板数据网络（CLPN 与 panel-GVAR）](symptom-networks.panel-networks.html)、[网络干预分析](symptom-networks.network-intervention.html)；
- **应用与争议**：[临床应用、可重复性与中心性假说之争](symptom-networks.clinical-controversies.html)，以及[症状网络模块控制](symptom-networks.module-control.html)方面的研究。

方法部分用到[脑连接组](brain-connectome.functional-connectivity.html)中介绍过的偏相关与精度矩阵、[社团结构与社区发现](community-structure.html)中的社团划分、[网络构建与统计验证](network-construction.html)中的 bootstrap 与置换检验，以及[网络可控性与稳定性](controllability.html)中的网络控制理论。真实研究中，症状网络通常用 R 语言的 qgraph、bootnet、IsingFit、mgm、mlVAR、psychonetrics、NetworkComparisonTest 等包或图形界面软件 JASP 估计；本专题的[代码示例](symptom-networks.html#code)用 numpy 从零实现其中的核心算法（EBICglasso、Ising 逐节点回归、桥中心性、NCT 置换、多被试 VAR、网络干预分析、可预测性），以便看清原理。

## 共同原因模型与网络理论 {#network-theory}

### 共同原因模型

传统的精神病学和心理测量学大多隐含一个**共同原因模型**（common cause model）：存在一个潜在的疾病实体（如“抑郁症”），它导致了失眠、情绪低落、疲乏等症状。症状是疾病的“指标”，就像体温是感染的指标。统计上，这对应**反映性潜变量模型**（reflective latent variable model）：在给定潜变量的条件下，各症状彼此独立（**局部独立性**），症状之间的相关完全来自它们共同的原因。

这一模型对于“肺炎导致发热和咳嗽”很合适，但对精神障碍有几处不太对劲：

- 症状之间似乎存在**直接**的因果联系：失眠会导致疲乏，疲乏导致注意力差，注意力差又可能加重自我评价低；
- 很难找到独立于症状本身的“潜在病因实体”；
- 同一诊断下的症状组合差异极大。Fried & Nesse（2015, *Journal of Affective Disorders*）分析 STAR\*D 研究中 3703 名抑郁症门诊患者，发现了 1030 种不同的症状组合，最常见的一种也只占很小比例。

### 网络模型

::: {.callout-def}
**症状网络**（symptom network）：以症状（通常是量表条目）为节点，以症状之间的统计关联（通常是偏相关或条件对数优势比）为边的网络。

**网络理论的核心主张**（Borsboom, 2017, *World Psychiatry*）：精神障碍不是某个潜在实体的外在表现，而是**症状之间相互因果作用**形成的自我维持状态。当症状网络连接足够强时，一个外部诱因（如重大生活事件）激活的症状会通过网络扩散，并在诱因消失后继续维持，系统“卡”在疾病状态中。
:::

这个理论借用了复杂系统中的几个概念：

- **替代稳定态**（alternative stable states）：健康和疾病是同一系统的两个稳定状态；
- **滞后**（hysteresis）：从健康进入疾病所需的外部压力，与从疾病恢复所需的压力减少量并不对称；
- **共病**（comorbidity）：不同障碍通过**桥症状**相连。Cramer 等（2010, *Behavioral and Brain Sciences*）指出，抑郁与广泛性焦虑共享睡眠问题、疲乏、注意困难等症状，这些共享症状可以解释二者高共病率，而不需要假设一个共同的潜在原因（量化方法见[桥中心性与共病](symptom-networks.bridge-centrality.html)）。

### 从口头理论到形式模型

“症状相互激活”是一个口头理论，要检验它，需要把它写成可以模拟的动力学模型。Cramer 等（2016, *PLOS ONE*）用 DSM 抑郁症状构成的网络做模拟：每个症状以一定概率被激活，激活概率随其邻居的激活状态升高。模拟显示，**连接越强**的网络越容易在外部压力下整体进入“多数症状激活”的状态，并且在压力撤除后不易恢复——即出现类似替代稳定态与滞后的行为；连接弱的网络则随压力平滑变化。这与[同步与协同动力学](synchronization.html)、[网络上的传播](spreading.html)中“耦合强度跨过阈值后出现集体行为”的逻辑相通。

Haslbeck 等（2021, *Psychological Methods*）进一步区分了**数据模型**（如 GGM，是对观测数据统计结构的描述）与**形式理论**（关于产生这些数据的机制的数学模型）。他们指出：从一个统计网络中，通常不能直接读出产生它的动力学机制；更有效的路径是先写出形式理论，再推导它在不同数据设计下会产生什么样的统计网络，与实测比对。

::: {.callout-bio}
网络观点改变了临床问题的提法：不再只问“这个人是否患有抑郁症”，而是问“这个人的哪些症状在相互维持，打断哪条链条最有效”。例如，如果失眠在网络中连接疲乏、注意力和情绪等多个症状，那么针对失眠的认知行为治疗（CBT-I）是否会产生“连锁改善”，就成为一个可检验的假说——[网络干预分析](symptom-networks.network-intervention.html)正是用随机对照试验数据检验这类假说的方法之一。
:::

需要注意，网络理论的主张是关于**因果作用**的，而从数据中估计出来的症状网络描述的是**统计依赖**。二者之间的距离见[横断面统计依赖与因果作用](symptom-networks.dependence-vs-causation.html)。理论文献的入门可读[Borsboom 2013 的精读](paper-borsboom2013_psychopathology.html)。

## 偏相关与高斯图模型 {#gaussian-graphical-model}

### 为什么不用相关网络

如果直接用相关系数构网，“失眠–注意力差”可能很强，但这可能完全来自它们共同与“疲乏”相关。相关网络会把间接关联也画成边，因而又密又难以解释。我们需要的是**控制其他所有症状后**仍然存在的关联。

### 偏相关与精度矩阵

在多元正态假设下，这正是**高斯图模型**（Gaussian graphical model, GGM）：设症状向量协方差为 $\Sigma$，其逆矩阵（精度矩阵）为 $K=\Sigma^{-1}$，则

$$
\rho_{ij\cdot\text{rest}} = -\frac{K_{ij}}{\sqrt{K_{ii}K_{jj}}}
$$

$\rho_{ij\cdot\text{rest}}=0$ 当且仅当在给定其余全部症状时，$i$ 与 $j$ **条件独立**。GGM 中的边就是非零偏相关。该等价关系的推导见[数学推导与算法](symptom-networks.derivations.html)。

::: {.callout-def}
**条件独立与边**：GGM 中两个症状之间没有边，表示控制其他所有症状后二者不再相关。“失眠–疲乏–注意力差”这条链中，如果失眠与注意力差之间只通过疲乏相关，那么偏相关网络中失眠和注意力差之间就没有边。

**成对马尔可夫性质**：GGM 是一种**无向图模型**（马尔可夫随机场）。图中两点不相邻 ⇔ 给定其余变量后条件独立；多元正态下还进一步有全局马尔可夫性质：若节点集 $C$ 把 $A$ 与 $B$ 在图中分隔开，则 $A\perp B\mid C$。
:::

### 算例：三个症状的链

设失眠（A）、疲乏（B）、注意力差（C）的相关为 $r_{AB}=0.5$，$r_{BC}=0.5$，$r_{AC}=0.25$。三变量时，一阶偏相关可以手算：

$$
\rho_{AC\cdot B}=\frac{r_{AC}-r_{AB}r_{BC}}{\sqrt{(1-r_{AB}^2)(1-r_{BC}^2)}}=\frac{0.25-0.25}{0.75}=0,
$$

$$
\rho_{AB\cdot C}=\frac{0.5-0.5\times0.25}{\sqrt{(1-0.25^2)(1-0.5^2)}}=\frac{0.375}{\sqrt{0.9375\times0.75}}\approx0.447 .
$$

相关网络里 A–C 有一条 0.25 的边；偏相关网络里这条边消失，A–B、B–C 两条边保留（同理 $\rho_{BC\cdot A}\approx0.447$）。这正是“A 与 C 只经由 B 相关”的情形。$p$ 个变量时不必逐个用递推公式，直接对相关矩阵求逆即可，[代码示例](symptom-networks.html#code)中的第一个单元就是这样做的。

### 数据类型与输入矩阵

GGM 假设变量连续且近似多元正态。症状量表条目通常是 0–3 或 1–5 分的**有序变量**，常用做法是以**多分格相关**（polychoric correlation，假设每个有序条目背后有一个被切分的连续正态变量）代替皮尔逊相关作为输入；条目严重偏态（如一般人群中的自杀意念条目大多为 0）时，多分格相关估计本身也不稳定，需要检查。真正的二值变量（有/无）应使用 [Ising 模型](symptom-networks.ising-model.html)，类型混合的数据使用[混合图模型](symptom-networks.mixed-graphical-models.html)。

## 正则化估计：EBICglasso {#regularization}

9 个症状（如 PHQ-9 抑郁量表）需要估计 $9\times8/2=36$ 个偏相关；37 个条目的组合量表需要 666 个。样本量有限时，样本偏相关会产生大量**小而非零的虚假边**。标准做法是**图形 LASSO**（graphical LASSO, glasso）：在最大化似然的同时对精度矩阵的非对角元素施加 $\ell_1$ 惩罚

$$
\hat K = \arg\max_{K \succ 0}\; \log\det K - \operatorname{tr}(SK) - \lambda \sum_{i\neq j}|K_{ij}|
$$

$\lambda$ 越大，被压缩为 0 的边越多。$\lambda$ 通常由**扩展贝叶斯信息准则**（EBIC）选择，超参数 $\gamma$ 常取 0.5，$\gamma$ 越大网络越稀疏、越保守。这一整套流程（EBICglasso）是 R 包 qgraph 和 bootnet 的默认方法之一，详见 Epskamp & Fried（2018, *Psychological Methods*）的教程；完整算法见[数学推导与算法](symptom-networks.derivations.html)，numpy 实现见[代码示例](symptom-networks.html#code)中的“EBICglasso”单元。

### 正则化带来的三个后果

1. **稀疏化**：许多边被精确地压为 0，网络图更易读，假阳性边减少；
2. **收缩偏倚**（shrinkage bias）：保留下来的边权也被系统地向 0 压小，因此正则化网络的边权大小不能直接当作效应量的无偏估计；
3. **选择不确定性**：$\lambda$ 由数据选出，“哪些边被保留”本身随样本波动，这正是[稳定性分析](symptom-networks.stability.html)要量化的东西。

### 替代估计方法

- **非正则化模型选择**：在 $n$ 相对 $p$ 较大时，可先用 glasso 产生候选结构，再在每个候选结构下做**无惩罚**的最大似然估计，以 EBIC 在候选中选择（qgraph 的 `ggmModSelect`）；或逐步删边/加边。这样避免收缩偏倚。
- **逐节点回归**（neighborhood selection）：对每个节点做 LASSO 回归，再用 AND/OR 规则合成无向图；这也是 Ising 模型和混合图模型的标准估计思路。
- **显著性检验法**：对每个偏相关做检验（如 Fisher $z$）并做多重比较校正，适合低维情形。

各方法在“发现真实边的能力”（敏感性）与“少报假边”（特异性）之间各有取舍，选择依据见[样本量与估计方法的选择](symptom-networks.sample-size.html)。

::: {.callout-warn}
**几个实际细节**：（1）量表条目通常是有序变量，常用多分格相关代替皮尔逊相关作为输入；（2）二分类症状（有/无）应改用 [Ising 模型](symptom-networks.ising-model.html)；（3）LASSO 的稀疏化假设“真实网络是稀疏的”，如果真实网络是由许多小边构成的稠密网络（例如数据其实由一个潜变量产生），LASSO 会系统性地漏掉它们（Epskamp, Kruis & Marsman, 2017, *PLOS ONE*）；（4）正则化后边权被压缩，**边不存在不代表真实的条件独立**，可能只是功效不足。
:::

## Ising 模型与二值症状数据 {#ising-model}

很多症状数据本来就是二值的：诊断访谈中的症状“有/无”、DSM 条目是否达到临床阈值。此时 GGM 的正态假设明显不成立。二值数据的对应模型是来自统计物理的 **Ising 模型**。

::: {.callout-def}
**Ising 模型**：设 $x_i\in\{0,1\}$（也可编码为 $\{-1,1\}$），$p$ 个症状的联合分布为

$$
P(\mathbf x)=\frac1Z\exp\Big(\sum_i\tau_ix_i+\sum_{i<j}\omega_{ij}x_ix_j\Big),
$$

$\tau_i$ 是**阈值**（threshold，节点在其余症状都为 0 时出现的倾向），$\omega_{ij}=\omega_{ji}$ 是**边权**（成对交互），$Z$ 是对全部 $2^p$ 种状态求和的归一化常数。$\omega_{ij}=0$ ⇔ 给定其余症状时 $x_i\perp x_j$，所以 Ising 模型与 GGM 一样是一个无向图模型（成对马尔可夫随机场）。
:::

### 条件分布与边权的含义

固定其余全部症状，单个症状服从逻辑回归：

$$
P(x_i=1\mid \mathbf x_{-i})=\sigma\Big(\tau_i+\sum_{j\ne i}\omega_{ij}x_j\Big),\qquad \sigma(u)=\frac1{1+e^{-u}} .
$$

因此 $\omega_{ij}$ 是**条件对数优势比**：其余症状固定时，$x_j$ 从 0 变为 1 使 $x_i$ 出现的对数优势增加 $\omega_{ij}$。

**算例**：设 $\tau_i=-1.5$，$i$ 只与 $j$ 相连且 $\omega_{ij}=1.2$。$x_j=0$ 时 $P(x_i=1)=\sigma(-1.5)\approx0.18$；$x_j=1$ 时 $P(x_i=1)=\sigma(-0.3)\approx0.43$；条件优势比 $e^{1.2}\approx3.3$。对两个节点的网络还可以直接验证 $\dfrac{P(1,1)P(0,0)}{P(1,0)P(0,1)}=e^{\omega_{12}}$：$Z$ 与 $\tau$ 在比值中全部约去。

### 估计：逐节点 L1 逻辑回归（eLasso）

$Z$ 含 $2^p$ 项，$p$ 稍大时无法直接最大化似然。van Borkulo 等（2014, *Scientific Reports*）提出的 **eLasso**（R 包 IsingFit）利用上面的条件分布：

1. 对每个节点 $i$，以其余节点为自变量做 $\ell_1$ 正则化逻辑回归，得到 $\hat\beta_{ij}$ 与截距 $\hat\tau_i$；
2. 每个节点的 $\lambda$ 用 EBIC 选择（原文默认 $\gamma=0.25$）；
3. 合并两次估计：**AND 规则**要求 $\hat\beta_{ij}$ 与 $\hat\beta_{ji}$ 都非零才保留边，**OR 规则**只要求其一非零；边权取二者平均。

这一“伪似然”思路的计算量只是 $p$ 次逻辑回归。[代码示例](symptom-networks.html#code)中先用 Gibbs 抽样从已知 Ising 模型生成数据，再用近端梯度法实现 L1 逻辑回归与 AND 规则，可以看到边的有无大体恢复，而边权被收缩。

### 与潜变量模型的等价

Ising 模型与心理测量学中的项目反应理论（IRT）模型有深刻联系：Marsman 等（2018, *Multivariate Behavioral Research*）系统说明了 Ising 网络模型与多维 IRT 模型在一定条件下给出相同的观测数据分布；Kruis & Maris（2016）给出了 Ising 模型与特定潜变量模型的统计等价结果。这意味着，仅凭数据拟合好坏，往往无法在“网络”与“潜变量”两种解释之间作出选择（见[横断面统计依赖与因果作用](symptom-networks.dependence-vs-causation.html)）。

::: {.callout-warn}
**二值化的代价**：把有序量表条目二分（如“≥2 分算有”）会丢失信息、降低功效，并使结果依赖切分点。若原始数据是有序的，通常优先用多分格相关加 GGM，或把它们作为类别变量放入混合图模型。另一方面，症状出现率极低或极高的条目方差很小，在 Ising 模型中同样难以估计边权。
:::

## 混合图模型与可预测性 {#mixed-graphical-models}

### 混合图模型（MGM）

临床数据常同时包含连续变量（如量表总分、生理指标）、类别变量（性别、诊断、治疗分组）和计数变量（发作次数）。Haslbeck & Waldorp（2020, *Journal of Statistical Software*）的 R 包 **mgm** 把 GGM 与 Ising 模型推广到这种情形：

- 每个变量的条件分布取自指数族（高斯、类别/多项、泊松），整个联合分布是一个成对马尔可夫随机场；
- 估计沿用逐节点思路：对每个变量做相应的 $\ell_1$ 正则化广义线性回归（连续变量用线性回归，类别变量用多项逻辑回归，计数用泊松回归），$\lambda$ 用 EBIC 或交叉验证选择，再用 AND/OR 规则合并；
- 类别变量与其他变量之间的“边”由多个参数组成（例如三类变量对一个连续变量有两个参数），绘图时通常汇总为一个非负的边权，符号不再有统一含义；
- mgm 还支持高阶交互（调节效应）与**时变**网络（用核平滑估计随时间变化的参数）。在此基础上，Haslbeck, Borsboom & Waldorp（2021, *Multivariate Behavioral Research*）提出**调节网络模型**（moderated network model）：让一个变量（如年龄、治疗分组）调节其余边的强度，可以看作连续版本的组间网络比较。

[网络干预分析](symptom-networks.network-intervention.html)就是混合图模型的一个直接应用：把二值的治疗分组变量与连续的症状变量放进同一个网络。

### 节点可预测性

中心性只描述一个节点在网络中的“位置”，不说明这个节点有多少变异能被网络解释。Haslbeck & Waldorp（2018, *Behavior Research Methods*）提出报告**节点可预测性**（predictability）：用其邻居预测该节点时的解释方差 $R^2$（连续变量）或校正后的分类准确率（类别变量）。

::: {.callout-def}
**可预测性**：节点 $i$ 被网络中其余节点解释的程度。对标准化的连续变量，把 $x_i$ 对其余全部变量做线性回归，残差方差等于 $1/K_{ii}$（$K$ 为相关矩阵的逆），因此

$$
R^2_i = 1-\frac{1}{K_{ii}} .
$$

可预测性是一个**绝对**量（0 到 1），可以在不同节点、不同网络之间比较；中心性则只是相对排序。
:::

可预测性的意义在于给“干预”设定上限：一个可预测性很低的症状主要由网络外的因素决定，即使干预它的全部邻居，它也不会改变多少；反之，一个可预测性很高的症状，至少在统计上“处在网络的控制之下”。这一推理依然以网络边具有因果含义为前提。样本内 $R^2$ 会高估样本外表现，严格的做法是用交叉验证估计样本外可预测性。[代码示例](symptom-networks.html#code)中验证了 $R^2_i=1-1/K_{ii}$ 与逐个回归的结果完全一致。

## 横断面统计依赖与因果作用 {#dependence-vs-causation}

症状网络研究中最常见的混淆，是把估计出来的**统计依赖**读成症状之间的**因果作用**。网络理论的主张是因果性的（症状相互引起、相互维持），但常用的数据和方法只能提供以下几层不同强度的证据，应分别看待。

### 截面偏相关描述的是人与人之间的条件依赖

用一大群人的单次测量估计的网络，描述的是**人与人之间**的条件相关结构，不一定对应任何一个人体内症状随时间的相互作用。截面偏相关网络的边是无向的，表示条件关联；方向和因果需要纵向、实验或干预证据。群体网络能否推广到个体，是一个仍在研究的问题：个体间结构与个体内结构可以相差很大，甚至符号相反（见[个体动态网络](symptom-networks.temporal-networks.html)与[研究前沿与开放问题](symptom-networks.frontiers.html)）。

### 网络模型与潜变量模型并不总能区分

网络模型和潜变量模型在统计上并不总能区分——在某些条件下，二者可以产生完全相同的观测数据分布（Kruis & Maris, 2016 给出了 Ising 网络模型与特定潜变量模型的等价结果；见 [Ising 模型](symptom-networks.ising-model.html)）。所以“数据支持网络模型”往往只能说明网络是一种**有用的描述**，而不能直接证明因果作用存在于症状之间。Epskamp 等（2017, *Psychometrika*）的“广义网络心理测量学”把二者合并：潜变量之间、或潜变量残差之间可以有网络结构，从而在同一框架中比较不同模型。

### 偏相关可能“制造”关联

::: {.callout-warn}
**偏相关不是因果，甚至可能“制造”关联。** 设 $A\to C\leftarrow B$，$A$ 与 $B$ 本来独立。控制共同结果 $C$ 后，$A$ 与 $B$ 会出现非零偏相关（对撞偏倚，collider bias）。例如“失眠”和“工作压力”若都导致“疲乏”，控制疲乏后二者可能呈负偏相关。GGM 无法区分这种边与真实的直接作用。中心性同理：强度高说明条件关联多，**不说明干预该节点能改变其他节点**——干预效应取决于因果方向，而无向网络中没有方向。
:::

Dablander & Hinne（2019, *Scientific Reports*）用模拟的有向无环因果图系统检验了这一点：在由已知因果结构生成的数据上，从无向网络计算出的中心性与节点真实的因果影响只有有限的对应关系，作者的结论是中心性不能替代因果推断。

### 更接近因果的证据

- **个体内时间序列网络**：时间网络满足“原因在前”，比截面网络更接近因果，但仍可能受未测量的共同原因和测量频率的影响（见[个体动态网络](symptom-networks.temporal-networks.html)）；
- **面板数据的滞后效应**：少数几个测量时点的纵向数据可估计横截滞后网络，但需要处理个体间稳定差异的混杂（见[面板数据网络](symptom-networks.panel-networks.html)）；
- **随机化干预**：随机分组切断了混杂，治疗分组对症状的条件关联可以给出“治疗先作用于哪些症状”的证据（见[网络干预分析](symptom-networks.network-intervention.html)）；
- **纵向与干预研究检验中心性**：中心症状是否为好靶点，需要纵向和干预研究检验（见[症状中心性](symptom-networks.centrality.html)）。

::: {.callout-warn}
**正确的表述**是：“在本样本的截面偏相关网络中，失眠的强度中心性最高，提示它与其他症状的条件关联最强；它是否在症状维持中起因果作用，需要纵向或干预研究检验。”而不是“失眠是抑郁症的核心症状，应优先治疗”。
:::

## 症状中心性及其解释 {#centrality}

### 常用指标

在加权症状网络中，[网络结构指标](network-metrics.html)中的中心性有对应的加权版本：

- **强度**（strength）：$s_i=\sum_j |w_{ij}|$，即与节点相连的边权绝对值之和；
- **预期影响**（expected influence, EI; Robinaugh 等, 2016, *J Abnorm Psychol*）：$\text{EI}_i=\sum_j w_{ij}$，保留边的正负号。当网络中有负边时（例如“睡眠增多”与“睡眠减少”），强度会高估节点的激活能力，EI 更合适；
- **接近中心性**、**介数中心性**：基于加权最短路径（通常把 $1/|w_{ij}|$ 作为距离）；
- **桥中心性**（bridge centrality）：只计算一个节点与其他症状群之间的连接，用于共病研究，详见[桥中心性与共病](symptom-networks.bridge-centrality.html)；
- **可预测性**：严格说不是中心性，但常与强度并列报告，表示节点被网络解释的绝对程度（见[混合图模型与可预测性](symptom-networks.mixed-graphical-models.html)）。

**算例**：节点“疲乏”与三个邻居的偏相关为 $0.30$、$0.20$、$-0.10$，则强度 $s=0.60$，EI $=0.40$。若把负边看成“疲乏升高时该邻居倾向降低”，EI 更贴近“激活疲乏会对网络产生多少净正向推动”这一问题。

### 中心性的解释局限

早期研究常把**最中心的症状**解释为“最重要的症状”和“最佳干预靶点”（这一推论被称为**中心性假说**）。这一推论有几处薄弱环节，需要特别谨慎：

1. **接近与介数不适合症状网络**。Bringmann 等（2019, *J Abnorm Psychol*）指出，这两个指标假设某种沿最短路径流动的“信息”，而偏相关网络中并不存在这样的流动；它们在实证数据中也很不稳定。多数研究现在主要报告强度或 EI。
2. **截面网络不是个体内的因果网络**。用一大群人的单次测量估计的网络，描述的是**人与人之间**的条件相关结构，不一定对应任何一个人体内症状随时间的相互作用（见[横断面统计依赖与因果作用](symptom-networks.dependence-vs-causation.html)）。
3. **中心性可能反映条目重叠**。如果两个条目问的几乎是同一件事（如“入睡困难”和“早醒”），它们之间会有很强的边，抬高双方的强度。分析前应检查内容重叠的条目（例如 R 包 networktools 中的 goldbricker 函数，它比较两个条目与其余条目的相关模式是否几乎相同）。
4. **中心性受方差影响**。一个在样本中几乎人人都有或几乎没人有的症状，方差很小，与其他症状的相关被压低，看起来就“不中心”。临床样本常因入组标准而对严重程度做了截断（全部患者都“情绪低落”），这同样会压低相关。
5. **干预证据有限**。Spiller 等（2020, *BMC Medicine*）综述了用截面中心性预测治疗中症状变化的研究，并在 710 名寻求治疗的 PTSD 患者中检验：治疗前的强度、EI 与可预测性能否预测某症状的变化与其余症状变化之间的关联。结果对中心性假说的支持有限。中心症状是否为好靶点，需要纵向和干预研究检验。
6. **稳定性**。中心性排序在小样本中很不稳定，报告前必须做[病例删除 bootstrap](symptom-networks.stability.html)。

## 桥中心性与共病 {#bridge-centrality}

### 共病的网络解释

精神障碍之间共病率很高，抑郁与焦虑尤甚。共同原因模型的解释是两个潜在疾病相关；网络模型的解释是两组症状通过若干**桥症状**直接相连：一组症状被激活后，经由桥症状扩散到另一组（Cramer 等, 2010）。要把这一想法量化，需要一个只计算“跨症状群连接”的中心性。

::: {.callout-def}
**桥中心性**（Jones, Ma & McNally, 2021, *Multivariate Behavioral Research*；R 包 networktools 的 `bridge` 函数）：给定节点的社团（症状群）划分 $c(\cdot)$，记 $\mathcal B_i=\{j: c(j)\ne c(i)\}$ 为节点 $i$ 所在社团之外的节点。

- **桥强度**：$\text{BS}_i=\sum_{j\in\mathcal B_i}|w_{ij}|$；
- **一步桥预期影响**：$\text{BEI}^{(1)}_i=\sum_{j\in\mathcal B_i}w_{ij}$；
- **两步桥预期影响**：在一步的基础上，还计入经由一个中间邻居到达其他社团的间接影响（以两段边权的乘积加权）；
- **桥介数**：节点出现在“起点与终点属于不同社团”的最短路径上的次数；
- **桥接近度**：节点到所有其他社团节点平均最短路径长度的倒数。
:::

**算例**：抑郁社团中的“睡眠问题”与同社团的“疲乏”相连（0.30），与焦虑社团的“紧张不安”（0.20）、“注意力差”（0.15）相连。它的普通强度为 $0.65$，桥强度为 $0.35$。而同社团中与情绪类条目连接很强的“情绪低落”可能普通强度更高，桥强度却接近 0。[代码示例](symptom-networks.html#code)中构造了一个 10 节点的抑郁–焦虑网络，可以看到普通强度最高的节点与桥强度最高的节点并不相同。

### 实践要点

- **社团划分从哪里来**：可以按量表（PHQ-9 条目为一群、GAD-7 条目为一群），也可以由数据驱动（如 Louvain、walktrap 或探索性图分析，见[社团结构与社区发现](community-structure.html)）。桥症状的识别完全依赖划分：同一网络换一种划分，桥症状就可能不同，应报告划分方法并做敏感性分析。
- **“桥症状”的界定**：应用研究中常把桥强度位于前 20%（第 80 百分位以上）的节点称为桥症状。这是经验界限，不是统计检验；也应像普通中心性一样用病例删除 bootstrap 检验桥中心性的稳定性（bootnet 支持对桥指标做稳定性分析）。
- **共享条目与条目重叠**：不同量表中内容相近的条目（如 PHQ-9 与 GAD-7 中的睡眠、疲乏、注意力相关条目）天然会形成强的跨量表边，它们成为桥症状部分是测量内容重叠的结果，而非两种障碍的机制性联系。
- **负的桥边**：桥强度把负边也计为“桥”，若研究问题是“激活一组症状是否会促进另一组”，应看桥 EI。

::: {.callout-bio}
网络模型对共病的研究影响了**症状维度**与**诊断边界**的讨论：如果抑郁和焦虑之间存在少数强的桥症状，那么针对这些桥症状的干预（例如针对睡眠或注意力问题），在网络理论下被预期能够同时减轻两类症状。[模块控制研究](symptom-networks.module-control.html)从另一个角度处理同一问题：不是看单个桥节点，而是看一个症状模块对另一个症状模块的控制强度。
:::

## 抽样不确定性：边权准确性与中心性稳定性 {#stability}

症状网络通常基于几百人的样本，估计不确定性很大。Epskamp, Borsboom & Fried（2018, *Behavior Research Methods*）提出了一套检验流程，实现于 R 包 **bootnet**（详见[Epskamp 2018 的精读](paper-epskamp2018_accuracy.html)）：

1. **边权准确性**：非参数 bootstrap（有放回重抽样被试，重复估计网络）得到每条边的置信区间。如果大部分边的区间重叠很多，就不应对边的大小排序做强结论。
2. **中心性稳定性**：**病例删除 bootstrap**（case-dropping），逐步删去 10%、20%……的被试，看中心性排序与全样本的相关是否仍然很高。**相关稳定性系数**（CS 系数）定义为：在 95% 的重抽样中，中心性与原始排序相关仍 ≥ 0.7 时，最多可删去的样本比例。建议 CS 不低于 0.25，最好高于 0.5。
3. **差异检验**：bootstrap 差异检验比较两条边或两个节点的中心性是否显著不同。

[代码示例](symptom-networks.html#code)中的简化版病例删除 bootstrap 显示：同一个真实网络，$n=300$ 时强度的 CS 约为 0.5，$n=100$ 时约为 0.1——后者的中心性排序不宜解读。

### 边的“出现频率”

除了区间，bootnet 还报告每条边在 bootstrap 样本中**非零的比例**。对正则化网络，这比置信区间更好解释：一条边在 95% 的 bootstrap 网络中都被选中，说明它的存在相当稳健；只在 40% 中出现的边，网络图上画出来也只能算“可能存在”。

### 报告规范

Burger 等（2023, *Psychological Methods*）整理了截面心理网络分析的报告标准，要求说明的内容包括：变量的选择理由与条目内容重叠检查、数据类型与输入相关矩阵、缺失数据处理、估计方法与全部调参（如 $\gamma$）、边权准确性与中心性稳定性结果、所用软件版本，以及公开数据或代码的方式。这与[可复现分析](reproducible-research.html)的一般要求一致。

算法细节，以及为什么 LASSO 边权的 bootstrap 区间不是严格意义上的置信区间，见[数学推导与算法](symptom-networks.derivations.html)。

## 样本量与估计方法的选择 {#sample-size}

“需要多少人才能估计一个症状网络”没有统一答案：它取决于节点数 $p$、真实网络的稀疏程度与边权大小、数据类型（连续、有序、二值）以及研究目标。这里只总结有文献支持的原则。

### 参数数量与功效

GGM 有 $p(p-1)/2$ 个偏相关，Ising 模型另有 $p$ 个阈值；参数数随 $p^2$ 增长。偏相关的抽样误差大致按 $1/\sqrt{n-p}$ 量级变化（控制的变量越多，有效自由度越少），所以同样的 $n$，节点越多，每条边越难估准。小的真实边（如 0.1）需要的样本量远大于大的真实边。

### 已有模拟研究的结论

- **Epskamp & Fried（2018）**：用模拟展示了 EBICglasso 的典型行为——小样本时网络偏稀疏（漏检多），但选出的边多为真实边；样本量增大，敏感性上升；他们也强调，在研究前应根据预期的网络结构做模拟以评估功效。
- **Epskamp, Kruis & Marsman（2017）**：当真实结构并不稀疏（例如数据来自潜变量模型，所有变量两两之间都有小的条件关联）时，glasso 会给出“看起来稀疏”的错误网络，并可能产生虚假的中心性差异。
- **Williams 等（2019）**：在 $n\gg p$ 的低维情形下，非正则化估计配合合适的边选择可以有更好的假阳性控制，正则化并非总是更好。
- **Isvoranu & Epskamp（2023, *Psychological Methods*）**：一项覆盖连续与偏态有序数据的大规模模拟研究，比较了多种 GGM 估计方法。核心结论是：发现能力（敏感性）与谨慎（特异性、精确度）之间总存在取舍，没有在所有条件下都最优的方法；应根据研究目标（探索还是确认、更怕漏报还是误报）和样本量选择方法，并用模拟评估所选方法在预期条件下的表现。

### 实际做法

1. **事先模拟**：bootnet 的 `netSimulator` 可以给定一个假设的真实网络（例如来自既往研究或文献）、估计方法和一系列样本量，模拟敏感性、特异性与边权相关，从而为样本量规划提供依据；
2. **控制节点数**：只纳入与研究问题直接相关、内容不重叠的条目，而不是把能拿到的所有量表条目都放进网络；
3. **事后检查**：无论样本多大，都要报告[边权准确性与中心性稳定性](symptom-networks.stability.html)；
4. **预先说明**：估计方法、$\gamma$、阈值规则等应在分析前确定（必要时预注册），并把替代选择作为敏感性分析报告（见[研究问题、可复现分析与敏感性分析](reproducible-research.html)）。

::: {.callout-warn}
不要把某篇模拟研究在某一组条件下得出的样本量当作普适门槛。没有提供模拟依据时，与其引用一个固定的“最少多少人”，不如直接报告 CS 系数和边权区间，让读者看到估计的实际精度。
:::

## 网络比较与跨样本复现 {#network-comparison}

### 网络比较检验（NCT）

比较两组（如男性与女性、不同诊断组、两个国家的样本）时，可用**网络比较检验**（network comparison test, NCT；van Borkulo 等, 2023, *Psychological Methods*；R 包 NetworkComparisonTest）。它是一个**置换检验**，在三个层面上检验两组网络是否相同：

::: {.callout-def}
设两组估计出的边权为 $w^{(1)}_{ij}$、$w^{(2)}_{ij}$。

- **网络结构不变性**：$H_0$：所有边都相同。检验统计量 $M=\max_{i<j}\big|w^{(1)}_{ij}-w^{(2)}_{ij}\big|$；
- **全局强度不变性**：$H_0$：两组网络的总连接度相同。统计量 $S=\Big|\sum_{i<j}|w^{(1)}_{ij}|-\sum_{i<j}|w^{(2)}_{ij}|\Big|$；
- **边不变性**：对每条边单独检验 $\big|w^{(1)}_{ij}-w^{(2)}_{ij}\big|$，需要多重比较校正（如 Holm）。
- （软件还支持对指定节点的中心性做不变性检验。）

**零分布**：把两组被试合并，随机重新分成同样大小的两组，在每次置换中重新估计两个网络并计算统计量，重复（如 1000 次以上）；$p$ 值是置换统计量不小于观测统计量的比例。
:::

**算例**：只有三条边的网络，A 组边权为 $(0.30, 0.20, 0.10)$，B 组为 $(0.30, 0.40, 0.00)$。则 $M=\max(0, 0.20, 0.10)=0.20$；全局强度分别为 $0.60$ 与 $0.70$，$S=0.10$。即使某条边相差很大，全局强度也可能几乎不变——三种检验回答的是不同问题。[代码示例](symptom-networks.html#code)中，只让一条边在 B 组变强：$M$ 的检验显著、Holm 校正后的边检验定位到这条边，而全局强度检验并不显著。

### 解读要点

- 由于每组网络本身都带有[抽样不确定性](symptom-networks.stability.html)，两组网络图“看起来不同”并不等于存在显著差异；反之，NCT 不显著也不等于网络相同，可能只是功效不足（样本量小、真实差异小）。
- NCT 中的网络通常用 EBICglasso 估计，两组样本量不同会导致正则化强度不同，样本量小的一组网络更稀疏；比较时要留意这种由估计方法带来的差异。
- **全局强度差异的混杂**：组间严重程度分布不同（例如临床样本症状范围被入组标准截断）会改变相关的大小，从而改变全局强度，而不一定反映症状间作用强度的改变。
- 基本形式的 NCT 假设两组是**独立样本**；同一批人治疗前后比较属于配对设计，需要专门的方法。多组或连续的分组变量可用[调节网络模型](symptom-networks.mixed-graphical-models.html)处理。

### 跨样本复现

单个样本中观察到的网络能否在其他样本中重现，是网络精神病学的一个核心问题，详见[临床应用与争议](symptom-networks.clinical-controversies.html)。

::: {.callout-bio}
**可重复性的争论**：Forbes 等（2017）认为症状网络在不同样本间复现性差，Borsboom 等随即撰文回应，认为差异部分来自样本特征和方法差异。随后的多样本研究（如 Fried 等 2018 年对四个创伤后应激障碍临床样本的跨文化比较）显示，网络结构存在相当程度的共性，但具体边和中心性排序存在样本差异。结论是：网络的整体结构比单条边和中心性排序更可靠，后者需要更大样本和稳定性检验支持。
:::

## 个体动态网络：经验取样与时间序列 {#temporal-networks}

为了接近“个体体内的症状相互作用”，研究者使用**经验取样法**（experience sampling method, ESM；也称生态瞬时评估，EMA）：让被试在数周内每天多次用手机报告情绪和症状。Bringmann 等（2013, *PLOS ONE*）较早把多层向量自回归用于这类临床纵向数据，估计情绪变量之间的时间网络；Epskamp 等（2018, *Multivariate Behavioral Research*）把它系统化为**图形向量自回归**（graphical VAR, GVAR）框架，区分了三种网络。

### 一个人的时间序列：时间网络与同期网络

设某人第 $t$ 次测量的症状向量为 $\mathbf y_t$（已减去此人的均值），一阶向量自回归 VAR(1) 为

$$
\mathbf y_t = B\,\mathbf y_{t-1} + \boldsymbol\varepsilon_t,\qquad \boldsymbol\varepsilon_t\sim\mathcal N(\mathbf 0,\Sigma_\varepsilon).
$$

::: {.callout-def}
- **时间网络**（temporal network）：由 $B$ 给出的**有向**网络，$B_{ji}\neq0$ 表示上一时刻的症状 $i$ 在控制所有上一时刻症状后预测这一时刻的症状 $j$（格兰杰意义上的“预测”）。$B_{ii}$ 是自回归效应（症状的惯性）。
- **同期网络**（contemporaneous network）：控制时间效应后，同一时刻残差（新息）$\boldsymbol\varepsilon_t$ 之间的偏相关，由 $\Sigma_\varepsilon^{-1}$ 标准化后取负得到，是**无向**的 GGM。它捕捉在测量间隔以内发生的相互作用（如果失眠在几分钟内就引起烦躁，而测量间隔是 3 小时，这一效应只会出现在同期网络中）。
:::

单被试估计（R 包 graphicalVAR）对 $B$ 与 $\Sigma_\varepsilon^{-1}$ 同时施加 LASSO 惩罚，用 EBIC 选择两个惩罚参数。Epskamp, van Borkulo 等（2018, *Clinical Psychological Science*）用单个患者的 ESM 数据演示了**个体化网络**的估计，并强调同期网络与时间网络都需要报告。

### 多个人：个体内与个体间网络

多被试 ESM 数据中，变异有两个来源：同一个人随时间的波动（个体内），以及不同人平均水平的差异（个体间）。GVAR 框架给出第三种网络：

- **个体间网络**（between-subjects network）：各人症状均值之间的偏相关网络，回答“平均压力高的人，平均情绪是否也低”。

多层 VAR（R 包 **mlVAR**）的标准做法分两步：先对每个人的滞后预测变量做**个体中心化**（within-person centering），在多层模型中估计固定效应（群体平均时间网络）与随机效应（个体差异）；再从残差估计同期网络、从个人均值估计个体间网络。

::: {.callout-warn}
**个体内与个体间可以相反**。[代码示例](symptom-networks.html#code)中模拟了一个情形：在每个人身上，压力上升会使下一时刻情绪变差（个体内正效应），但平均压力高的人平均情绪反而更好（个体间负相关）。把所有观测直接合并计算的相关接近 0——两种来源相互抵消。截面网络只看到个体间那一层；把它当作个体内机制，就可能得到符号错误的结论。这是**遍历性**（ergodicity）问题：只有当个体间结构与个体内结构相同时，群体结论才能直接推广到个体。
:::

### 前提与局限

- **平稳性**：VAR 假设均值、方差与 $B$ 在观察期内不变；病情改善或治疗中的数据往往不满足，可用时变 VAR（如 mgm 的核平滑方法）；
- **测量间隔**：一阶滞后效应的大小依赖测量间隔，间隔为 2 小时与 1 天得到的时间网络不能直接比较；
- **等间隔与夜间间隔**：ESM 通常白天多次、夜间不测，需要处理隔夜的滞后（常见做法是不把前一晚最后一次与次日第一次配对）；
- **条目数与时间点数**：单被试 VAR 的参数为 $p^2$ 个，ESM 每人常只有几十到一百多个时间点，因此 ESM 通常只纳入少数条目，且个体网络估计不确定性很大；
- **测量误差**：单条目的 ESM 测量误差会削弱并扭曲滞后效应；Epskamp（2020, *Psychometrika*）提出在 GVAR 中引入潜变量（ts-lvgvar），以处理测量误差。

::: {.callout-bio}
Fisher 等（2017, *J Abnorm Psychol*）对心境与焦虑障碍患者做了密集的个体化 ESM 测量，为每名患者分别估计同期与时间网络，发现患者之间的网络结构差异很大；Fisher, Medaglia & Jeronimus（2018, *PNAS*）进一步显示个体间变异与个体内变异的结构可以相差很大。这类结果推动了“为每名患者建立个体网络，以选择个体化治疗靶点”的设想，但个体网络的估计精度与临床价值仍在检验中。
:::

## 面板数据网络：CLPN 与 panel-GVAR {#panel-networks}

ESM 需要密集测量，成本高、条目少。很多队列研究只有 2–5 次随访（如间隔数月或一年），但每次测量了完整量表。这类**面板数据**也可以估计有向的滞后网络。

### 横截滞后面板网络（CLPN）

**横截滞后面板网络**（cross-lagged panel network, CLPN；Wysocki、McCarthy、van Bork 与 Cramer 提出，预印本 2022，正式发表于 2025）：对两次相邻测量，把每个 $t_2$ 时刻的条目对全部 $t_1$ 时刻条目做正则化回归：

$$
y_{j,t_2}=\alpha_j+\beta_{jj}\,y_{j,t_1}+\sum_{i\ne j}\beta_{ji}\,y_{i,t_1}+e_j ,
$$

$\beta_{jj}$ 为**自回归**边（症状的稳定性），$\beta_{ji}$ 为**横截滞后**边（$i$ 在 $t_1$ 预测 $j$ 在 $t_2$ 的变化）。所有横截滞后边构成一个有向网络，可以计算出度（cross-lagged out-prediction，该症状预测其他症状后续变化的总量）与入度。原文用 LASSO 回归选边，再在结构方程模型框架中重新估计。

### 个体间稳定差异的混杂

CLPN 继承了传统**横截滞后面板模型**（CLPM）的问题。Hamaker, Kuiper & Grasman（2015, *Psychological Methods*）指出，CLPM 没有把稳定的个体间差异（特质水平）与个体内的时间变化分开：如果“长期压力高的人”同时“长期情绪低”，这种个体间相关会被误读为压力对后续情绪的滞后效应。他们提出的**随机截距 CLPM**（RI-CLPM）为每个人加一个随机截距，把特质差异分离出去。

在网络框架中，Epskamp（2020, *Psychometrika*）的 **panel-GVAR**（R 包 psychonetrics）做了同样的分离：在**至少三次测量**的面板数据上，同时估计个体内的时间网络与同期网络、以及个体间网络，与 ESM 数据的 GVAR 对应。

::: {.callout-warn}
**两次测量的 CLPN 无法分离个体内与个体间效应**，其横截滞后边混合了特质水平的个体间关联。若只有两波数据，结论应表述为“$t_1$ 的 $i$ 预测 $t_2$ 的 $j$（控制 $t_1$ 的其他条目）”，而不是“$i$ 导致 $j$ 增加”；有三波以上数据时，应考虑 panel-GVAR 或 RI-CLPM 类模型。此外，滞后效应的大小依赖随访间隔，间隔为 3 个月与 1 年的结果不可直接比较。
:::

## 网络干预分析 {#network-intervention}

“中心症状是否为好的干预靶点”最终需要干预数据来回答。**网络干预分析**（network intervention analysis, NIA）由 Blanken 等（2019, *Psychotherapy and Psychosomatics*）提出，思路很直接：在随机对照试验数据中，把**治疗分组**（治疗 = 1，对照 = 0）作为一个节点，与症状一起放进[混合图模型](symptom-networks.mixed-graphical-models.html)中估计网络，并在每个测量时点重复。

::: {.callout-def}
**NIA 中“分组–症状”边的含义**：由于分组是随机的，分组与症状的简单相关是治疗对该症状的**总效应**；网络中的边则是控制其余症状后的条件关联。若治疗只直接作用于症状 $A$，再经 $A$ 影响 $B$，则在网络中分组与 $A$ 相连、与 $B$ 不相连（条件于 $A$ 后关联消失）。因此，与分组直接相连的症状被解释为治疗的**直接作用点**（条件于网络中的其他症状），其他症状的改善则可能是经由网络传递的间接效应。
:::

::: {.callout-bio}
Blanken 等（2019）分析了一项随机对照试验：104 名同时有失眠与抑郁症状的参与者，52 人接受 5 周 CBT-I，52 人为对照；连续 10 周每周测量失眠严重度指数（ISI）与 PHQ-9 条目，每周估计一个包含分组节点的 LASSO 正则化混合网络。治疗节点主要与失眠条目直接相连——其中“早醒”和“睡眠维持困难”最为突出，第一周之后即出现；抑郁条目中只有个别条目在个别时点与治疗直接相连。作者据此认为，CBT-I 对抑郁的改善最可能是经由这两项睡眠症状间接实现的。这些结论建立在单个试验、每周一次测量的基础上，需要在更大样本中重复。
:::

[代码示例](symptom-networks.html#code)中模拟了“治疗 → 睡眠 → 疲乏 → 情绪”的链：分组与疲乏、情绪的简单相关都不为零，但在偏相关网络中只有“分组–睡眠问题”一条边。

::: {.callout-warn}
**NIA 的解释边界**：（1）“没有边”可能只是功效不足，尤其在样本量为一百人左右的试验中；（2）条件于其他症状后，若某症状既受治疗直接影响又受其他症状影响，正则化可能只保留其中一条路径；（3）在同一时点估计的网络无法确定症状之间的先后，NIA 依靠跨时点的重复估计看“效应如何在网络中展开”，但症状之间的边仍是条件关联，不是已证实的因果路径；（4）存在对撞偏倚的可能：若治疗和某个未测量因素都影响症状 $A$，以 $A$ 为条件可能在治疗与其他症状之间制造虚假的条件关联。
:::

## 临床应用与争议 {#clinical-controversies}

网络方法在十余年间迅速扩散，Robinaugh 等（2020, *Psychological Medicine*）对 2008–2018 年的文献做了系统回顾，并提出未来议程；Fried & Cramer（2017, *Perspectives on Psychological Science*）集中讨论了理论与方法上的挑战。以下几条争论最为集中。

### 可重复性之争

- **Forbes 等（2017, *J Abnorm Psychol*）**用两个大型流行病学样本中的抑郁与焦虑症状（二值条目），比较两个样本的网络，认为边、中心性等特征的复现性有限；
- **Borsboom 等（2017, *J Abnorm Psychol*，“False alarm?”）**对同一数据做了全面重分析，认为在考虑抽样误差和方法选择后，两个样本的网络实际上高度相似，原文的结论来自方法问题；
- **Forbes 等（2017, *J Abnorm Psychol*，答复）**坚持认为网络特征（尤其是单个节点和边的特征）的复现性与实用性有限；之后 Forbes 等（2021, *Multivariate Behavioral Research*）进一步量化了心理病理网络特征的信度与复现性；
- **Fried 等（2018, *Clinical Psychological Science*）**比较了四个跨文化、多中心的 PTSD 临床样本，发现网络整体结构有相当程度的共性，同时具体边和中心性存在差异。

这场争论的共识大致是：（1）网络的**整体结构**（例如哪些条目形成症状群、强边的大致位置）比单条边的有无和中心性的精确排序可靠得多；（2）单样本研究必须报告稳定性分析，跨样本比较需要正式检验（[NCT](symptom-networks.network-comparison.html)），而不是并排看图；（3）复现失败可能有多种来源：抽样误差、样本特征（社区样本与临床样本）、条目的翻译与测量差异、估计方法的选择。

### 中心性假说之争

中心性假说认为高中心性症状是有效的干预靶点。支持与反对的证据：

- 理论层面：截面无向网络中的中心性不等于因果影响（Bringmann 等 2019；Dablander & Hinne 2019，见[横断面统计依赖与因果作用](symptom-networks.dependence-vs-causation.html)）；
- 实证层面：Spiller 等（2020）在 710 名 PTSD 患者中检验治疗前中心性对症状变化的预测，支持有限；
- 干预层面：[网络干预分析](symptom-networks.network-intervention.html)和针对特定症状的随机试验，才是检验“干预某症状是否带动其余症状”的直接方式。

### 网络与潜变量之争

数据层面的等价性（[Ising 模型与 IRT](symptom-networks.ising-model.html)、Kruis & Maris 2016）意味着拟合优度不能裁决两种模型。目前更常见的立场是把二者看作互补：潜变量模型描述“症状共同变化的维度”，网络模型描述“控制其余症状后仍存在的特异关联”；区分它们需要干预、纵向和[形式理论](symptom-networks.network-theory.html)层面的证据。

### 临床应用的现状

- **个体化网络**：基于 ESM 的个体网络被设想用于个体化治疗规划，目前仍以可行性研究为主，个体网络的估计精度与对治疗结局的增益尚需前瞻性试验检验；
- **治疗机制研究**：NIA、治疗前后网络比较、调节网络模型被用于研究“治疗先改变什么”；
- **预警信号**：情绪时间序列的自相关和方差升高（临界慢化）被研究为症状转变的预警信号（见[研究前沿与开放问题](symptom-networks.frontiers.html)）；
- **诊断与分类**：网络观点支持把精神障碍看作症状维度与相互作用，而非离散类别，这与精神病理分类学中的维度化方向有共通之处，但网络模型本身并不提供诊断标准。

::: {.callout-warn}
在临床报告中，应避免把群体截面网络中的“中心症状”直接写成治疗建议。较稳妥的写法是：说明网络的数据来源（截面/纵向、群体/个体），报告稳定性，指出结论属于假说生成，并提出可以检验它的纵向或干预设计。
:::

## 症状网络的模块控制 {#module-control}

Pan 等（2024）把[网络可控性](controllability.html)理论用于症状网络（[Pan 2024](paper-pan2024_modulecontrol.html)）。思路是：症状网络中多个量表条目往往形成**症状模块**，以往研究多关注单个节点之间的关系（中心性、[桥中心性](symptom-networks.bridge-centrality.html)），而较少从全局出发研究**模块之间的控制关系**。

- **方法**：针对无向网络，采用基于**最小支配集**（minimum dominating set, MDSet）的控制框架，支配集中的节点作为驱动节点。由于最小支配集往往不唯一，在多个最小支配集上计算模块之间的**平均模块控制强度**（AMCS），以模块为节点、AMCS 为边权构成有向的**模块控制网络**（MCN）。每个模块有对外控制力、被控制力和对内控制力三个指标。
- **数据**：某高校 2773 名大一新生（经伦理委员会批准），使用 PHQ-9（抑郁）、GAD-7（焦虑）、ISI（失眠严重度）和 PSS-14（感知压力）共 37 个条目。用图形 LASSO 估计得到 37 个节点、254 条边的症状网络，Louvain 算法划分出 6 个症状模块，并把模块区分为直接描述情绪感受的“情绪模块”和不直接描述情绪的“非情绪模块”。
- **发现**：非情绪模块的对外控制强度高于情绪模块，情绪模块更容易受其他模块控制；从非情绪模块到情绪模块的平均控制强度最高。失眠量表第 4 条目和压力量表第 2、7 条目在非情绪模块中控制作用最强，被视为主要控制症状。以 80% 子样本重复 1000 次的 bootstrap 显示，边权、驱动节点集和模块数都较稳定。

### 与其他方法的关系

- 与[桥中心性](symptom-networks.bridge-centrality.html)相比：桥中心性按节点统计跨社团连接的强度，是“局部、对称”的量；模块控制网络是在全网驱动节点集合上统计的“有向”模块间关系，回答“哪个模块更能影响哪个模块”。
- 与[网络干预分析](symptom-networks.network-intervention.html)相比：模块控制从网络结构推导潜在的控制关系，NIA 用随机化干预数据检验实际的直接作用点。前者提出假说，后者可以检验假说，例如“以失眠和压力模块为靶点的干预，是否比以情绪模块为靶点的干预带来更大的整体改善”。
- 与[时间网络](symptom-networks.temporal-networks.html)、[面板网络](symptom-networks.panel-networks.html)相比：在有向的滞后网络上，也可以用结构可控性的方法（如[最大匹配](controllability.structural-controllability.html)）分析驱动节点，这时“控制”的方向来自时间顺序，而不是从无向网络中推断。

这一工作提供了一个“从模块尺度看症状网络”的视角。阅读时要注意它与[症状中心性](symptom-networks.centrality.html)相同的前提：网络来自截面数据和无向偏相关，“控制”是网络结构意义上的可控性，不等于已证实的临床因果效应，需要纵向或干预研究进一步检验。

## 数学推导与算法 {#derivations}

本节从多元正态分布出发推导“偏相关为 0 ⇔ 条件独立”，写出图形 LASSO 与 EBIC 的完整形式，给出 Ising 伪似然估计、病例删除 bootstrap 与 CS 系数、NCT 置换检验和 GVAR 三种网络的算法。符号：$p$ 个症状（节点），$n$ 名被试，$X\in\mathbb R^{n\times p}$，样本协方差（或相关）矩阵 $S$，总体协方差 $\Sigma$，精度矩阵 $K=\Sigma^{-1}$。偏相关等于精度矩阵归一化负值的回归推导（不需要正态假设）见[脑连接组的数学推导](brain-connectome.derivations.html)。

### A. 高斯图模型：为什么 $K_{ij}=0$ 意味着条件独立

设 $x\sim\mathcal N(0,\Sigma)$，密度为

$$
f(x)\propto\exp\Big(-\tfrac12 x^\top Kx\Big)=\exp\Big(-\tfrac12\sum_{a}K_{aa}x_a^2-\sum_{a<b}K_{ab}x_ax_b\Big).
$$

指数中含 $x_i$ 与 $x_j$ 的**交叉项**只有 $-K_{ij}x_ix_j$。若 $K_{ij}=0$，密度可以分解成“不含 $x_i$ 的因子”乘“不含 $x_j$ 的因子”（其余变量固定），由因子分解定理即得 $x_i\perp x_j\mid x_{\text{rest}}$。反之亦然。这就是 GGM 中“无边 = 条件独立”的来源，它**依赖多元正态假设**；对非正态数据，$K_{ij}=0$ 只保证“偏相关为 0”，不保证条件独立。

再看回归形式：把 $x_i$ 对其余变量回归，$x_i=\sum_{j\ne i}\beta_{ij}x_j+\varepsilon_i$，可以证明

$$
\beta_{ij}=-\frac{K_{ij}}{K_{ii}},\qquad \operatorname{Var}(\varepsilon_i)=\frac{1}{K_{ii}},\qquad \rho_{ij\cdot\text{rest}}=\operatorname{sign}(\beta_{ij})\sqrt{\beta_{ij}\beta_{ji}}.
$$

所以 GGM 也可以看成 $p$ 个相互约束的回归；“邻域选择”（逐节点 LASSO 回归）正是利用这一点的另一种估计方法。由第二式，对标准化变量（$\operatorname{Var}(x_i)=1$）有可预测性 $R^2_i=1-\operatorname{Var}(\varepsilon_i)=1-1/K_{ii}$。

### B. 图形 LASSO 与 EBIC

高斯似然（忽略常数）为 $\ell(K)=\tfrac n2\big[\log\det K-\operatorname{tr}(SK)\big]$。图形 LASSO 求解

$$
\hat K_\lambda=\arg\max_{K\succ0}\ \log\det K-\operatorname{tr}(SK)-\lambda\sum_{i\ne j}|K_{ij}|.
$$

两个有用的事实：（1）当 $\lambda\ge\max_{i\ne j}|S_{ij}|$ 时解是对角阵，即空网络，这给出 $\lambda$ 路径的上端 $\lambda_{\max}$；（2）问题是凸的，常用块坐标下降求解（Friedman 等, 2008），每次更新一行/列相当于解一个 LASSO 回归。

**块坐标下降的一步**：记 $W=\hat K^{-1}$ 为当前协方差估计。把第 $j$ 行/列分出来，$W_{11}$ 为去掉 $j$ 后的子矩阵，$s_{12}$ 为 $S$ 的第 $j$ 列（去掉第 $j$ 个元素）。求解 LASSO 问题

$$
\hat\beta=\arg\min_\beta\ \tfrac12\beta^\top W_{11}\beta-s_{12}^\top\beta+\lambda\|\beta\|_1 ,
$$

用坐标下降：$\beta_k\leftarrow \operatorname{soft}\big(s_{12,k}-\sum_{l\ne k}(W_{11})_{kl}\beta_l,\ \lambda\big)/(W_{11})_{kk}$，其中 $\operatorname{soft}(u,\lambda)=\operatorname{sign}(u)\max(|u|-\lambda,0)$。更新 $w_{12}=W_{11}\hat\beta$。所有列收敛后，由分块求逆公式恢复精度矩阵：$\hat K_{jj}=1/(W_{jj}-w_{12}^\top\hat\beta)$，$\hat K_{-j,j}=-\hat\beta\,\hat K_{jj}$。收敛解满足 KKT 条件：$\hat K_{ij}\ne0$ 时 $W_{ij}-S_{ij}=\lambda\operatorname{sign}(\hat K_{ij})$，$\hat K_{ij}=0$ 时 $|W_{ij}-S_{ij}|\le\lambda$——可以用来检验实现是否正确。

EBIC（Foygel & Drton, 2010）在 BIC 上加了对“候选模型数量”的惩罚：

$$
\text{EBIC}_\gamma(\lambda)=-2\,\ell(\hat K_\lambda)+E_\lambda\log n+4\gamma\,E_\lambda\log p,
$$

$E_\lambda$ 是 $\hat K_\lambda$ 中非零边数。$\gamma=0$ 时退化为普通 BIC；$\gamma$ 越大越偏向稀疏网络。$\gamma=0.5$ 是常用默认，研究目标偏向“少报假边”时取大，偏向探索（如样本量较小但希望保留弱边）时可取 0.25 甚至 0，但必须事先说明。

```text
算法 1  EBICglasso
输入：相关矩阵 S（p×p，可为多分格相关）；样本量 n；γ；路径长度 L（如 100）；比例 r（如 0.01）
输出：选定的偏相关网络 W
1. λ_max ← max_{i≠j} |S_ij|；λ_min ← r·λ_max
2. 在 [λ_min, λ_max] 上取 L 个对数等距的 λ
3. 对每个 λ：用 glasso 解出 K_λ（可用上一个 λ 的解作热启动）
4.     E_λ ← K_λ 非对角非零元素对数
5.     EBIC(λ) ← −n[log det K_λ − tr(S K_λ)] + E_λ log n + 4γ E_λ log p
6. λ* ← argmin EBIC(λ)
7. W_ij ← −K*_ij / sqrt(K*_ii K*_jj)，i ≠ j
复杂度：每个 λ 的 glasso 约 O(p³)（每轮块坐标下降），总计约 O(L·p³)；p≈40 时几乎瞬时完成
```

### C. Ising 模型的伪似然估计

Ising 模型的对数似然含 $\log Z(\tau,\omega)$，$Z$ 是 $2^p$ 项之和。**伪似然**用全部条件分布的乘积代替联合分布：

$$
\text{PL}(\tau,\omega)=\sum_{k=1}^n\sum_{i=1}^p\log P\big(x_{ki}\mid \mathbf x_{k,-i}\big),\qquad P(x_i=1\mid\mathbf x_{-i})=\sigma\Big(\tau_i+\sum_{j\ne i}\omega_{ij}x_j\Big).
$$

$\omega_{ij}$ 同时出现在节点 $i$ 和 $j$ 的条件分布中；若放松 $\omega_{ij}=\omega_{ji}$ 的约束，最大化伪似然就可以分解为 $p$ 个独立的逻辑回归（各自估计 $\beta_{ij}$），再用 AND/OR 规则把 $\beta_{ij}$ 与 $\beta_{ji}$ 合并。每个回归加 $\ell_1$ 惩罚，以节点级 EBIC 选 $\lambda$：

$$
\text{EBIC}_i(\lambda)=-2\,\ell_i(\hat\beta_\lambda)+k_\lambda\log n+2\gamma\,k_\lambda\log(p-1),
$$

$k_\lambda$ 为节点 $i$ 回归中的非零系数个数。Gibbs 抽样可以从给定参数的 Ising 模型生成数据：依次对每个节点按上面的条件概率重新抽取 0/1，多轮后收敛到联合分布。

### D. 强度、预期影响与桥中心性

由 $W$ 定义：强度 $s_i=\sum_j|W_{ij}|$；一步预期影响 $\text{EI}^{(1)}_i=\sum_jW_{ij}$；Robinaugh 等（2016）还定义了两步预期影响 $\text{EI}^{(2)}_i=\text{EI}^{(1)}_i+\sum_jW_{ij}\,\text{EI}^{(1)}_j$，把邻居的影响也计入。若网络全为正边，$s_i=\text{EI}^{(1)}_i$；负边越多，两者差别越大。给定社团划分，把求和限制在其他社团的节点上即得桥强度与桥 EI（见[桥中心性与共病](symptom-networks.bridge-centrality.html)）。偏相关边与因果作用的区别（包括对撞偏倚）见[横断面统计依赖与因果作用](symptom-networks.dependence-vs-causation.html)。

### E. 病例删除 bootstrap 与 CS 系数

```text
算法 2  中心性稳定性（case-dropping）与 CS 系数
输入：数据 X（n×p）；中心性函数 c(·)（如强度）；删除比例集合 P = {0.05, 0.1, …, 0.75}；
      每个比例的重抽样次数 B（如 1000）；相关阈值 r0 = 0.7；置信水平 q = 0.95
输出：CS 系数
1. c0 ← c(EBICglasso(X))                       // 全样本中心性向量，长度 p
2. 对每个 π ∈ P：
3.     对 b = 1..B：
4.         无放回抽取 ⌊(1−π)n⌋ 名被试，得子样本 X_b
5.         c_b ← c(EBICglasso(X_b))
6.         ρ_b ← cor(c_b, c0)
7.     prop(π) ← #{ρ_b ≥ r0} / B
8. CS ← max{ π ∈ P : prop(π) ≥ q }（若无满足者则 CS = 0）
9. 报告：CS ≥ 0.25 为最低可接受，≥ 0.5 较好
复杂度：|P|·B 次 glasso 估计，每次约 O(L·p³)；可完全并行
```

注意三点：（1）这里用**无放回子抽样**，不是常规 bootstrap；（2）子样本中每次都要重新选 $\lambda$，否则低估不稳定性；（3）CS 只衡量“排序稳不稳”，不衡量“排序对不对”，有偏样本中排序也可以很稳。边权准确性的非参数 bootstrap 则是**有放回**抽取 $n$ 人，对每条边取 2.5% 和 97.5% 分位数；由于 LASSO 会把边压向 0，这些区间并不是严格意义上的置信区间，只宜用来判断边的大小是否可区分。

### F. 网络比较检验的置换算法

```text
算法 3  NCT（独立两组）
输入：X1（n1×p），X2（n2×p）；网络估计函数 est(·)；置换次数 R（如 1000–5000）
输出：M、S 与各边的置换 p 值
1. W1 ← est(X1)，W2 ← est(X2)
2. M0 ← max_{i<j} |W1_ij − W2_ij|；S0 ← | Σ_{i<j}|W1_ij| − Σ_{i<j}|W2_ij| |；D0_ij ← |W1_ij − W2_ij|
3. 合并 X ← [X1; X2]
4. 对 r = 1..R：
5.     随机打乱 X 的行，前 n1 行为 X1*，其余为 X2*
6.     W1* ← est(X1*)，W2* ← est(X2*)；计算 M_r、S_r、D_r
7. p_M ← (1 + #{M_r ≥ M0}) / (R + 1)；p_S 同理；p_ij ← (1 + #{D_r,ij ≥ D0_ij}) / (R + 1)
8. 对 {p_ij} 做多重比较校正（如 Holm）
复杂度：2R 次网络估计
```

置换检验的有效性依赖“零假设下组标签可交换”：两组除网络结构外，变量的边际分布（均值以外的方差等）若明显不同，也可能导致显著结果，解读时需要同时检查。

### G. GVAR：三种网络的估计

对第 $k$ 个人、第 $t$ 次测量的 $\mathbf y_{kt}$：

$$
\mathbf y_{kt}=\boldsymbol\mu_k+B(\mathbf y_{k,t-1}-\boldsymbol\mu_k)+\boldsymbol\varepsilon_{kt},\qquad \boldsymbol\varepsilon_{kt}\sim\mathcal N(\mathbf 0,\Sigma_\varepsilon),\qquad \boldsymbol\mu_k\sim\mathcal N(\boldsymbol\mu,\Sigma_\mu).
$$

- 时间网络：$B$（有向；也可标准化为偏有向相关）；
- 同期网络：$\Theta=\Sigma_\varepsilon^{-1}$ 标准化取负，$\rho^{\text{contemp}}_{ij}=-\Theta_{ij}/\sqrt{\Theta_{ii}\Theta_{jj}}$；
- 个体间网络：$\Sigma_\mu^{-1}$ 标准化取负。

mlVAR 的两步近似：（1）用每人的样本均值 $\bar{\mathbf y}_k$ 代替 $\boldsymbol\mu_k$，对滞后预测变量做个体中心化，逐变量拟合多层回归，得到 $B$ 的固定效应与随机效应；（2）由残差估计 $\Sigma_\varepsilon$（同期网络），由各人均值之间的回归估计 $\Sigma_\mu^{-1}$ 的结构（个体间网络）。直接把全部观测合并计算协方差，得到的是 $\Sigma_\mu$ 与个体内协方差的混合，这就是[代码示例](symptom-networks.html#code)中合并相关接近 0 的原因。

## 研究前沿与开放问题 {#frontiers}

1. **群体网络能否推广到个体？** Fisher, Medaglia & Jeronimus（2018, *PNAS*，DOI: [10.1073/pnas.1711978115](https://doi.org/10.1073/pnas.1711978115)）显示个体间变异与个体内变异的结构可以相差很大。截面网络中的边在多少个体身上成立，如何用 ESM 数据检验，仍是核心问题。
2. **网络模型与潜变量模型能否区分？** Kruis & Maris（2016, *Scientific Reports*，DOI: [10.1038/srep34175](https://doi.org/10.1038/srep34175)）给出了 Ising 网络模型与特定潜变量模型统计等价的结果。要区分二者，需要哪类数据（干预、纵向、实验操纵），尚无定论。
3. **低维时还要正则化吗？** Williams 等（2019, *Multivariate Behavioral Research*，DOI: [10.1080/00273171.2019.1575716](https://doi.org/10.1080/00273171.2019.1575716)）认为当 $n\gg p$ 时，非正则化估计可能比 glasso 有更好的假阳性控制；Isvoranu & Epskamp（2023）的模拟显示不存在在所有条件下都最优的方法。估计方法的选择如何影响已发表的中心性结论，仍有争议。
4. **网络能否预警症状转变？** van de Leemput 等（2014, *PNAS*，DOI: [10.1073/pnas.1312114110](https://doi.org/10.1073/pnas.1312114110)）报告情绪的自相关与方差升高（临界慢化）与抑郁发作或缓解有关。这类早期预警信号在个体层面的预测效能和假警报率，仍需前瞻性研究检验。
5. **从数据模型到形式理论**：如何写出可模拟的症状动力学模型，并用其预测不同数据设计下应出现的统计网络（Haslbeck 等, 2021）？形式理论能否给出网络中心性无法给出的干预预测？
6. **面板数据中的个体内效应**：只有少数几波测量时，如何可靠地分离个体内滞后效应与特质差异？panel-GVAR 在常见队列样本量下的估计精度如何？
7. **干预网络与控制理论的结合**：能否用随机化干预数据（NIA）检验由[模块控制](symptom-networks.module-control.html)或其他控制理论方法预测的“关键症状”？

## 生物医学应用 {#biomedical}

症状网络方法已扩展到精神医学之外。慢性疼痛研究中，疼痛强度、睡眠、疲乏、抑郁情绪、灾难化思维之间的网络被用于理解“疼痛–失眠–情绪”的恶性循环；在癌症患者的症状群研究中，护理学领域用网络分析识别化疗期间相互关联的症状簇；在新冠后综合征等新兴疾病中，症状网络被用来描述疲乏、认知障碍和情绪症状的关系。这些应用同样需要满足本专题讨论的数据类型、稳定性与因果解释要求。

在临床试验中，网络方法也被用来提出更细的问题：治疗是整体降低所有症状，还是先作用于某几个症状，再通过网络扩散？[网络干预分析](symptom-networks.network-intervention.html)把治疗分组作为节点，直接检验治疗的直接作用点；比较治疗前后或不同治疗组网络的连接强度（全局强度，见[网络比较](symptom-networks.network-comparison.html)）则回答网络整体连接是否改变。

::: {.callout-bio}
**共病研究**：抑郁–焦虑、PTSD–抑郁、物质使用–情绪障碍等共病组合常用[桥中心性](symptom-networks.bridge-centrality.html)识别连接两组症状的条目。由于不同量表之间存在内容重叠的条目，可靠的桥症状结论需要同时报告社团划分方法、条目重叠检查与桥中心性的稳定性。
:::

公开数据中常含 PHQ-9、GAD-7 等量表条目，例如美国 NHANES 调查公开了数千名成人的 PHQ-9 逐条目数据（见延伸资源），可以构建症状网络；分析流程通常在 R（qgraph + bootnet + NetworkComparisonTest）或 JASP 的 Network 模块中完成，并按 Epskamp 等（2018）与 Burger 等（2023）的建议完整报告稳定性分析和估计细节。

## 适用范围与常见误用 {#limitations}

1. **误区**：症状网络的边表示一个症状导致另一个症状。→ **正解**：截面偏相关网络的边表示条件关联，方向和因果需要纵向、实验或干预证据；还可能是对撞偏倚造成的。
2. **误区**：网络里没有边的两个症状一定条件独立。→ **正解**：正则化会把弱边压缩为 0，样本量小时功效不足，“没有边”可能只是没检测到。
3. **误区**：强度最高的症状就是最佳治疗靶点。→ **正解**：中心性受条目重叠、方差、样本特征影响，截面网络不等于个体内因果网络；靶点需要干预研究验证。
4. **误区**：只要报告了网络图，结果就可以解读。→ **正解**：必须报告边权置信区间和中心性 CS 系数；CS < 0.25 时中心性排序不宜解读。
5. **误区**：数据符合网络模型就证明潜变量模型是错的。→ **正解**：二者在一定条件下可产生相同的数据分布，网络模型首先是一种有用的描述和假说生成工具。
6. **误区**：二值症状数据也直接用皮尔逊相关加 glasso。→ **正解**：二值数据应使用 Ising 模型，混合类型数据使用混合图模型；有序数据用多分格相关时要检查严重偏态条目。
7. **误区**：两组网络图看起来不同，说明网络结构有差异。→ **正解**：需要 NCT 等正式检验；NCT 不显著也可能只是功效不足；组间严重程度分布不同会改变相关大小。
8. **误区**：群体 ESM 网络或截面网络描述了每一个患者体内的症状机制。→ **正解**：个体间、个体内同期与个体内时间网络回答不同问题，可以方向相反；推广到个体需要个体层面的证据。
9. **误区**：两次随访的横截滞后网络给出了症状之间的因果方向。→ **正解**：两波数据无法分离稳定的个体间差异，滞后边可能来自特质水平的关联，且大小依赖随访间隔。
10. **误区**：桥症状是两种障碍之间的机制联系。→ **正解**：桥症状依赖社团划分，并可能来自量表间内容重叠的条目。

## 关联知识 {#related}

- [网络结构指标与随机图](network-metrics.html)：度、介数、接近中心性的原始定义及其“流动”假设，是理解症状中心性局限的起点。
- [社团结构与社区发现](community-structure.html)：Louvain 等社团划分方法，用于识别症状模块，是桥中心性与模块控制的前提。
- [网络可控性与稳定性](controllability.html)：最小支配集与结构可控性，症状网络模块控制的理论基础。
- [脑连接组：结构与功能连接](brain-connectome.html)：偏相关、精度矩阵与正则化在功能连接估计中的同一用法。
- [网络构建与统计验证](network-construction.html)：从原始测量构建网络、bootstrap 与置换检验的一般原则。
- [动态功能连接与多层脑网络](dynamic-brain-networks.html)：时间序列上的网络估计、零模型与可重复性问题，与个体动态症状网络方法相通。
- [同步与协同动力学](synchronization.html)、[网络上的传播与免疫](spreading.html)：耦合强度与集体状态转变，为症状网络的替代稳定态与滞后提供动力学类比。
- [研究问题、可复现分析与敏感性分析](reproducible-research.html)：估计方法与超参数选择的敏感性分析和预注册。

## 核心文献 {#references}

### Borsboom 2017：A network theory of mental disorders

- **背景**：网络方法在精神病理学中迅速流行，但缺少一个系统的理论表述。
- **核心发现**：该文（*World Psychiatry*，DOI: [10.1002/wps.20375](https://doi.org/10.1002/wps.20375)）系统阐述了网络理论：症状之间存在直接因果关系；强连接的症状网络可能具有替代稳定态和滞后效应；外部因素通过“外场”作用于特定症状。文后附有多位学者的评论，代表了支持与批评的不同立场。
- **阅读提示**：一定要读评论部分，体会该理论在概念上的争议（例如症状是否能被清楚地界定为独立的“节点”）。早期的综述可读 Borsboom & Cramer 2013（[精读](paper-borsboom2013_psychopathology.html)）。
- **思考题**：如果网络理论正确，治疗应该怎样设计？如果共同原因模型正确，治疗又应怎样设计？二者的预测在什么实验中会出现分歧？

### Borsboom 等 2021：Network analysis of multivariate data in psychological science

- **背景**：网络方法从精神病理学扩展到人格、态度、认知等领域，需要一份系统的方法学综述。
- **核心内容**：该文（*Nature Reviews Methods Primers*，DOI: [10.1038/s43586-021-00055-w](https://doi.org/10.1038/s43586-021-00055-w)）覆盖数据类型与研究设计、截面网络（GGM、Ising、混合图模型）与时间序列网络的估计、中心性与可预测性、稳定性与可重复性、报告与数据共享、方法局限与发展方向。
- **阅读提示**：可作为本专题估计方法部分的总纲；对照本专题各知识页面，看每一种估计方法对应的数据假设。

### Epskamp & Fried 2018：A tutorial on regularized partial correlation networks

- **背景**：EBICglasso 被广泛使用，但许多使用者不清楚正则化的假设和后果。
- **核心内容**：该文（*Psychological Methods*，DOI: [10.1037/met0000167](https://doi.org/10.1037/met0000167)）系统讲解偏相关网络、glasso 与 EBIC 选择、有序数据的处理，并用模拟说明不同样本量下的估计表现与常见误读。
- **阅读提示**：对照[正则化估计](symptom-networks.regularization.html)与[样本量与估计方法的选择](symptom-networks.sample-size.html)阅读。

### Epskamp, Borsboom & Fried 2018：Estimating psychological networks and their accuracy: A tutorial paper

- **背景**：大量症状网络研究只报告一个网络图和中心性排序，缺少对估计不确定性的检验。
- **核心发现**：该文（*Behavior Research Methods*，DOI: [10.3758/s13428-017-0862-1](https://doi.org/10.3758/s13428-017-0862-1)）提出了边权 bootstrap 置信区间、病例删除 bootstrap 与 CS 系数、差异检验等一整套方法，实现于 R 包 bootnet，并用一个 PTSD 数据集完整演示。
- **阅读提示**：对照[抽样不确定性：边权准确性与中心性稳定性](symptom-networks.stability.html)，把文中每一张图与它要回答的问题对应起来；注意作者对 CS 系数阈值的表述是经验性的建议。
- **思考题**：如果一项研究的强度中心性 CS 系数为 0.13，作者却在讨论部分大篇幅解释“最中心症状”的临床意义，你作为审稿人会提出什么意见？
- **精读**：[Epskamp 2018](paper-epskamp2018_accuracy.html)

### Bringmann 等 2019：What do centrality measures measure in psychological networks?

- **背景**：中心性指标来自社会网络和信息流动研究，被直接搬到症状网络中。
- **核心发现**：该文（*Journal of Abnormal Psychology*，DOI: [10.1037/abn0000446](https://doi.org/10.1037/abn0000446)）分析了中心性指标背后的假设，指出接近中心性和介数中心性的假设在症状网络中难以满足，强度的解释也需谨慎，并用实证数据展示了这些指标的不稳定性。
- **阅读提示**：结合[网络结构指标与随机图](network-metrics.html)中中心性的定义，思考“流动”的假设在社交网络、脑网络和症状网络中各自是否成立。
- **思考题**：你能否设计一个中心性指标，使其假设与症状网络的生成机制相匹配？它需要什么样的数据？

### Epskamp, Waldorp, Mõttus & Borsboom 2018：The Gaussian graphical model in cross-sectional and time-series data

- **背景**：ESM 数据同时含有个体内与个体间变异，单一网络无法区分。
- **核心内容**：该文（*Multivariate Behavioral Research*，DOI: [10.1080/00273171.2018.1454823](https://doi.org/10.1080/00273171.2018.1454823)）把 GGM 推广到时间序列，提出时间网络、同期网络与个体间网络三者的区分，并给出多被试的估计方法（mlVAR）。
- **阅读提示**：对照[个体动态网络](symptom-networks.temporal-networks.html)与代码中的模拟，理解三种网络为什么可能符号不同。

### 其他方法文献

| 主题 | 文献 |
|---|---|
| Ising 模型估计 | van Borkulo 等 2014，*Scientific Reports*，[10.1038/srep05918](https://doi.org/10.1038/srep05918) |
| Ising 与 IRT | Marsman 等 2018，*Multivariate Behavioral Research*，[10.1080/00273171.2017.1379379](https://doi.org/10.1080/00273171.2017.1379379) |
| 混合图模型 | Haslbeck & Waldorp 2020，*Journal of Statistical Software*，[10.18637/jss.v093.i08](https://doi.org/10.18637/jss.v093.i08) |
| 可预测性 | Haslbeck & Waldorp 2018，*Behavior Research Methods*，[10.3758/s13428-017-0910-x](https://doi.org/10.3758/s13428-017-0910-x) |
| 调节网络模型 | Haslbeck, Borsboom & Waldorp 2021，*Multivariate Behavioral Research*，[10.1080/00273171.2019.1677207](https://doi.org/10.1080/00273171.2019.1677207) |
| 桥中心性 | Jones, Ma & McNally 2021，*Multivariate Behavioral Research*，[10.1080/00273171.2019.1614898](https://doi.org/10.1080/00273171.2019.1614898) |
| 预期影响 | Robinaugh, Millner & McNally 2016，*J Abnorm Psychol*，[10.1037/abn0000181](https://doi.org/10.1037/abn0000181) |
| 网络比较检验 | van Borkulo 等 2023，*Psychological Methods*，[10.1037/met0000476](https://doi.org/10.1037/met0000476) |
| 稀疏假设的风险 | Epskamp, Kruis & Marsman 2017，*PLOS ONE*，[10.1371/journal.pone.0179891](https://doi.org/10.1371/journal.pone.0179891) |
| 估计方法选择 | Isvoranu & Epskamp 2023，*Psychological Methods*，[10.1037/met0000439](https://doi.org/10.1037/met0000439) |
| 报告规范 | Burger 等 2023，*Psychological Methods*，[10.1037/met0000471](https://doi.org/10.1037/met0000471) |
| 广义网络心理测量 | Epskamp, Rhemtulla & Borsboom 2017，*Psychometrika*，[10.1007/s11336-017-9557-x](https://doi.org/10.1007/s11336-017-9557-x) |
| 多层 VAR | Bringmann 等 2013，*PLOS ONE*，[10.1371/journal.pone.0060188](https://doi.org/10.1371/journal.pone.0060188) |
| 个体化网络 | Epskamp, van Borkulo 等 2018，*Clinical Psychological Science*，[10.1177/2167702617744325](https://doi.org/10.1177/2167702617744325)；Fisher 等 2017，*J Abnorm Psychol*，[10.1037/abn0000311](https://doi.org/10.1037/abn0000311) |
| 面板数据网络 | Epskamp 2020，*Psychometrika*，[10.1007/s11336-020-09697-3](https://doi.org/10.1007/s11336-020-09697-3)；Wysocki 等 2025，*advances.in/psychology*，[10.56296/aip00037](https://doi.org/10.56296/aip00037)；Hamaker, Kuiper & Grasman 2015，*Psychological Methods*，[10.1037/a0038889](https://doi.org/10.1037/a0038889) |
| 网络干预分析 | Blanken 等 2019，*Psychotherapy and Psychosomatics*，[10.1159/000495045](https://doi.org/10.1159/000495045) |
| 中心性与因果 | Dablander & Hinne 2019，*Scientific Reports*，[10.1038/s41598-019-43033-9](https://doi.org/10.1038/s41598-019-43033-9)；Spiller 等 2020，*BMC Medicine*，[10.1186/s12916-020-01740-5](https://doi.org/10.1186/s12916-020-01740-5) |
| 可重复性争论 | Forbes 等 2017，[10.1037/abn0000276](https://doi.org/10.1037/abn0000276)；Borsboom 等 2017，[10.1037/abn0000306](https://doi.org/10.1037/abn0000306)；Forbes 等 2017 答复，[10.1037/abn0000313](https://doi.org/10.1037/abn0000313)（均为 *J Abnorm Psychol*）；Forbes 等 2021，*Multivariate Behavioral Research*，[10.1080/00273171.2019.1616526](https://doi.org/10.1080/00273171.2019.1616526)；Fried 等 2018，*Clinical Psychological Science*，[10.1177/2167702617745092](https://doi.org/10.1177/2167702617745092) |
| 理论与综述 | Cramer 等 2010，*Behav Brain Sci*，[10.1017/S0140525X09991567](https://doi.org/10.1017/S0140525X09991567)；Cramer 等 2016，*PLOS ONE*，[10.1371/journal.pone.0167490](https://doi.org/10.1371/journal.pone.0167490)；Fried & Nesse 2015，*J Affect Disord*，[10.1016/j.jad.2014.10.010](https://doi.org/10.1016/j.jad.2014.10.010)；Fried & Cramer 2017，*Perspect Psychol Sci*，[10.1177/1745691617705892](https://doi.org/10.1177/1745691617705892)；Robinaugh 等 2020，*Psychol Med*，[10.1017/S0033291719003404](https://doi.org/10.1017/S0033291719003404)；Haslbeck 等 2021，*Psychological Methods*，[10.1037/met0000303](https://doi.org/10.1037/met0000303) |

## 延伸资源 {#resources}

| 类型 | 资源 | 说明 |
|---|---|---|
| 视频 | [朱政：症状网络的概述和应用](https://www.bilibili.com/video/BV1cvWpeQEa1/)（B 站） | 中文讲座，70 分钟，理论与临床应用概述；上传者非讲者本人 |
| 视频 | [R 语言 bootnet 心理学网络分析](https://www.bilibili.com/video/BV1KA4m1N7jw/)（B 站） | 中文，16 分钟，照着 Epskamp 2018 教程逐步操作 |
| 综述 | Borsboom 等 2021，[doi.org/10.1038/s43586-021-00055-w](https://doi.org/10.1038/s43586-021-00055-w) | 心理科学中多元数据网络分析的方法学总览 |
| 理论 | Borsboom 2017，[doi.org/10.1002/wps.20375](https://doi.org/10.1002/wps.20375) | 网络理论的纲领性文章，附多篇评论 |
| 方法 | Epskamp, Borsboom & Fried 2018，[doi.org/10.3758/s13428-017-0862-1](https://doi.org/10.3758/s13428-017-0862-1) | 稳定性分析教程（CC BY 4.0），撰写方法部分时的主要参考 |
| 方法 | Epskamp & Fried 2018，[doi.org/10.1037/met0000167](https://doi.org/10.1037/met0000167) | 正则化偏相关网络（EBICglasso）教程 |
| 方法 | Burger 等 2023，[doi.org/10.1037/met0000471](https://doi.org/10.1037/met0000471) | 截面心理网络分析的报告标准 |
| 批评 | Bringmann 等 2019，[doi.org/10.1037/abn0000446](https://doi.org/10.1037/abn0000446) | 中心性指标适用性的代表性批评 |
| 网站 | [psych-networks.com](https://psych-networks.com/) | Eiko Fried 维护的博客，含心理网络方法的教程、争论与新文献介绍（中心性解读、正则化后的 bootstrap、个体化方法等） |
| 软件 | [JASP](https://jasp-stats.org/)；R 包 [bootnet](https://cran.r-project.org/package=bootnet)、[qgraph](https://cran.r-project.org/package=qgraph)、[networktools](https://cran.r-project.org/package=networktools) | JASP 的 Network 模块无需写代码；R 包分别负责估计与稳定性、绘图、桥中心性与条目重叠检查 |
| 软件 | R 包 [IsingFit](https://cran.r-project.org/package=IsingFit)、[mgm](https://cran.r-project.org/package=mgm)、[mlVAR](https://cran.r-project.org/package=mlVAR)、[graphicalVAR](https://cran.r-project.org/package=graphicalVAR)、[psychonetrics](https://cran.r-project.org/package=psychonetrics)、[NetworkComparisonTest](https://cran.r-project.org/package=NetworkComparisonTest) | 分别对应 Ising 模型、混合图模型与可预测性、多层 VAR、单被试 GVAR、panel-GVAR 与潜变量网络、网络比较检验 |
| 数据 | [NHANES 2021–2023 PHQ-9（DPQ_L）](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/DPQ_L.htm) | 6337 名成人的 PHQ-9 九个条目，公开下载，可用于构建抑郁症状网络 |

## 开放问题 {#questions}

1. 选择一种你熟悉的疾病（可以是精神疾病，也可以是慢性病，如糖尿病、慢性疼痛、帕金森病的非运动症状），列出 8–12 个可测量的症状或指标。用网络视角提出一个可检验的假说，并说明你需要什么样的数据（截面、ESM、面板还是干预）来检验它，以及应选择 GGM、Ising 还是混合图模型。
2. Pan 等（2024）的模块控制研究发现非情绪模块（如睡眠、压力相关条目）对情绪模块有更强的控制作用。如果要把这一发现推进到临床应用，你认为下一步应做什么研究？请说明研究设计（例如能否用网络干预分析检验）、主要结局指标以及可能的混杂因素。
3. 一项研究用两次随访的横截滞后网络发现“失眠预测后续情绪低落，而不是相反”。在接受这一结论之前，你还需要看到哪些证据或敏感性分析？
4. 两组样本的 NCT 结果是全局强度显著不同，但网络结构不变性检验不显著。这种组合可能在什么情况下出现？应如何解读？
