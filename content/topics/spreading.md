---
id: spreading
title: 网络上的传播与免疫
en: Spreading processes and immunization
domain: dynamics
legacy: L05
summary: 研究病原体、信息与行为如何沿网络传播，网络结构怎样决定流行阈值，以及如何选择免疫、追踪与干预对象。
keywords: [SIR, SIS, 基本再生数, 流行病阈值, 度异质性, 消息传递, 时间网络, 集合种群, 接触追踪, 免疫策略, 复杂传染, 影响力最大化, 超级传播, 传播溯源]
synonyms: [spreading, epidemic spreading, 流行病传播, 传染病模型, compartmental model, 仓室模型, SI, SIS, SIR, SEIR, basic reproduction number, R0, 基本再生数, effective reproduction number, Rt, 有效再生数, 时变再生数, next-generation matrix, NGM, 下一代矩阵, generation interval, 代际间隔, serial interval, 序列间隔, epidemic threshold, 传播阈值, 流行阈值, transmissibility, 传播性, heterogeneous mean-field, HMF, 异质平均场, quenched mean-field, QMF, 淬火平均场, individual-based mean-field, IBMF, NIMFA, 个体平均场, pair approximation, 配对近似, moment closure, 矩封闭, edge-based compartmental model, EBCM, 边基仓室模型, message passing, 消息传递, belief propagation, 置信传播, non-backtracking matrix, 非回溯矩阵, Hashimoto matrix, Ihara–Bass, approximate master equation, AME, 近似主方程, excess degree, 剩余度, friendship paradox, 朋友悖论, bond percolation, 键渗流, Gillespie algorithm, 随机模拟, contact network, 接触网络, contact matrix, 接触矩阵, POLYMOD, wearable proximity sensor, 可穿戴近距离传感器, temporal network, 时间网络, 时序网络, time-respecting path, 时间相容路径, burstiness, 阵发性, 爆发性, inter-event time, 事件间隔, activity-driven model, 活动驱动模型, metapopulation, 集合种群, 复合种群, mobility network, 流动网络, 航空网络, invasion threshold, 入侵阈值, effective distance, 有效距离, GLEaM, epidemic forecasting, 流行病预测, superspreading, 超级传播, superspreader, 超级传播者, dispersion parameter, 离散参数, negative binomial, 负二项分布, contact tracing, 接触追踪, backward tracing, 向后追踪, forward tracing, 向前追踪, digital contact tracing, 数字接触追踪, sentinel surveillance, 哨点监测, social network sensor, 社交网络传感器, immunization, 免疫, vaccination, 疫苗接种, targeted immunization, 目标免疫, acquaintance immunization, 熟人免疫, community bridge finder, 社团桥接免疫, herd immunity, 群体免疫, independent cascade, IC, 独立级联, linear threshold model, 线性阈值模型, simple contagion, 简单传染, complex contagion, 复杂传染, social reinforcement, 社会强化, global cascade, 全局级联, simplicial contagion, 单纯复形传染, higher-order interaction, 高阶相互作用, influence maximization, 影响力最大化, submodularity, 子模性, greedy algorithm, 贪心算法, CELF, k-shell, k-壳, k-core, k-核, collective influence, CI, 集体影响, optimal percolation, 最优渗流, diffusion centrality, 扩散中心性, network targeting, 网络靶向干预, source localization, 传播溯源, 源定位, patient zero, 零号病人, rumor centrality, 谣言中心性, Jordan center, Jordan 中心, observer, 观测点, homophily, 同质性, social contagion, 社会传染, hospital-acquired infection, 院内感染, 医院感染网络, MRSA, network diffusion model, 网络扩散模型]
demos: [sir, attack]
reviewed: 2026-11-15
---

## 概述 {#overview}

网络结构指标与网络模型描述的是网络“长什么样”：度分布、路径、聚集、社团。网络动力学进一步让网络“动起来”：节点带有状态，状态沿着边变化。传播（spreading）是最直观的一类网络动力学：病原体沿接触网络传播，谣言和健康行为沿社交网络扩散，药物与诊疗新知沿医生网络流动，错误折叠蛋白甚至可能沿脑连接组扩散。

这一专题按“模型—结构—干预—推断”组织，围绕以下科学问题展开：

1. **经典模型**：没有网络时，SI、SIS、SIR、SEIR 模型说了什么，基本再生数 $R_0$ 从何而来（[均匀混合下的经典传播模型](spreading.compartmental-models.html)）。
2. **结构如何决定阈值**：度分布的异质性怎样改变流行病阈值，为什么无标度网络的阈值会趋近于 0（[度异质性与流行病阈值](spreading.epidemic-threshold.html)）；真实接触网络从哪里来、有什么结构（[接触网络](spreading.contact-networks.html)）。
3. **更精确的理论**：平均场之外，配对近似、边基模型与消息传递如何把聚集、度相关与具体拓扑纳入计算（[配对近似、边基模型与消息传递](spreading.message-passing.html)）。
4. **超越静态度分布**：接触随时间变化、成簇出现（阵发性），人群在城市间流动，这些怎样改变传播的速度与可预测性（[时间网络与阵发性](spreading.temporal-networks.html)、[集合种群与全球传播](spreading.metapopulation.html)）。
5. **从数据估计传播**：如何从发病曲线和传播链估计 $R_0$、时变再生数 $R_t$ 与超级传播程度（[再生数与超级传播](spreading.reproduction-number.html)）。
6. **干预**：给谁接种、追踪谁、监测谁（[免疫策略](spreading.immunization.html)、[接触追踪与监测](spreading.contact-tracing.html)）。
7. **信息与行为**：社会传染与疾病传播有何不同，怎样选种子使影响最大，怎样从观测反推源头（[信息与行为的传播](spreading.social-contagion.html)、[影响力最大化与关键传播者](spreading.influential-spreaders.html)、[传播溯源](spreading.source-localization.html)）。

这些问题直接建立在[网络结构指标与随机图](network-metrics.html)中的度分布和二阶矩 $\langle k^2\rangle$，以及[小世界与无标度网络模型](network-models.html)中的无标度网络之上。SIR 的最终规模与键渗流等价，因此传播理论与[网络鲁棒性、渗流与级联失效](robustness.html)共用同一套数学；“删去枢纽”既是蓄意攻击，也是目标免疫。流行阈值 $\langle k\rangle/\langle k^2\rangle$ 的形式还会在[同步与协同动力学](synchronization.html)的同步阈值中重现。

## 网络传播过程 {#spreading-on-networks}

“流行病”（epidemic）一词源自希腊语 epi（在……之上）与 demos（人群）。传播现象远不止传染病：

| 现象 | 网络 | 传播的“东西” |
|---|---|---|
| 性传播疾病 | 性接触网络 | 病原体 |
| 呼吸道传染病 | 近距离接触网络、交通网络 | 病原体 |
| 院内感染 | 医护–患者接触网络、医院间转诊网络 | 耐药菌等病原体 |
| 谣言与健康信息 | 通信网络、社交媒体 | 信息 |
| 创新与行为扩散 | 社会网络、医生咨询网络 | 观念、行为、处方习惯 |
| 疟疾 | 蚊媒–人二分网络 | 疟原虫 |
| 神经退行性病变 | 脑结构连接网络 | 错误折叠蛋白（假说） |

14 世纪的黑死病从法国传到瑞典用了约 4 年，速度受限于人步行和航运；2003 年 SARS 借助航空网络在数周内到达多个大洲。Hufnagel、Brockmann 和 Geisel（2004，PNAS）用全球航空网络模拟 SARS 的扩散，说明传播的空间格局主要由交通网络的拓扑决定，而不是由地理距离决定（见[集合种群与全球传播](spreading.metapopulation.html)）。

::: {.callout-def}
**网络传播过程**：每个节点处于有限个状态之一（如易感 S、潜伏 E、感染 I、移除 R），状态转移只能沿边发生（感染）或自发发生（潜伏结束、恢复）。网络决定“谁能感染谁”，动力学参数决定“感染得多快、持续多久”。
:::

一个核心结论贯穿本专题：**传播只能沿连接发生，所以网络结构本身就是传播的“燃料管道”。** 规模小、彼此隔绝的狩猎采集群体难以长期维持麻疹这类“人群病”（crowd diseases），而人口稠密、相互连通的城市可以。

### 微观模型：精确描述及其代价

最精确的描述是**个体层面的随机过程**（Barabási 第 10 章 Advanced Topics 10.A 称为微观模型）。以 SIS 为例，记 $x_i(t)\in\{0,1\}$ 表示节点 $i$ 是否感染，$A_{ij}$ 为邻接矩阵，则在一个很短的时间 $dt$ 内：

- 感染者 $i$ 以概率 $\mu\,dt$ 恢复；
- 易感者 $i$ 以概率 $\beta\,dt\sum_j A_{ij}x_j$ 被感染。

这是一个有 $2^N$ 个状态的连续时间马尔可夫链。它在有限网络上**一定**最终到达全体易感的吸收态（SIS 的“流行”只是一个寿命随 $N$ 指数增长的亚稳态），而且主方程维数随 $N$ 指数增长，无法直接求解。于是理论研究发展出一系列近似，从粗到细大致是：

| 近似层次 | 跟踪的变量 | 保留的结构信息 | 典型阈值 | 进一步阅读 |
|---|---|---|---|---|
| 均匀混合 | $s,i,r$ | 只有平均度 | $\lambda_c=1/\langle k\rangle$ | [经典模型](spreading.compartmental-models.html) |
| 异质平均场（HMF） | 每个度类的 $i_k$ | 度分布 | $\langle k\rangle/\langle k^2\rangle$ | [流行病阈值](spreading.epidemic-threshold.html) |
| 个体平均场（QMF/NIMFA） | 每个节点的 $\rho_i$ | 完整邻接矩阵 | $1/\Lambda_{\max}(A)$ | [消息传递](spreading.message-passing.html) |
| 配对近似 / 边基模型 | 成对状态 $[SI]$、边变量 $\theta$ | 度分布、聚集（部分） | 依闭合方式而定 | [消息传递](spreading.message-passing.html) |
| 消息传递（SIR） | 每条有向边的消息 | 完整拓扑（树状近似下精确） | $1/\rho(B)$ | [消息传递](spreading.message-passing.html) |
| 随机模拟 | 每个节点的状态轨迹 | 一切 | 数值估计 | [数学推导与算法](spreading.derivations.html) C 节 |

越往下越精确，代价是需要的数据和计算更多。应用中常见的做法是：先用 HMF 得到量级与直觉，再用消息传递或随机模拟在真实网络上校准。

## 均匀混合下的经典传播模型 {#compartmental-models}

先假设**均匀混合**（homogeneous mixing）：每个人单位时间与 $\langle k\rangle$ 个随机选出的人接触，每次“感染者–易感者”接触以速率 $\beta$ 传播。记 $s, i, r$ 为三类人群所占比例。

**SI 模型**（只感染不恢复）：

$$\frac{di}{dt}=\beta\langle k\rangle\, i\,(1-i)$$

解为 logistic 曲线 $i(t)=\dfrac{i_0e^{t/\tau}}{1-i_0+i_0e^{t/\tau}}$，特征时间 $\tau=1/(\beta\langle k\rangle)$。早期 $i$ 很小，$i(t)\approx i_0e^{t/\tau}$，呈指数增长；后期饱和到 1。早期行为最重要：疫苗和药物需要数月以上研发，早期隔离和接种是控制疫情的主要手段。

**SIS 模型**（如普通感冒，痊愈后可再感染），恢复率 $\mu$：

$$\frac{di}{dt}=\beta\langle k\rangle\, i\,(1-i)-\mu i$$

稳态 $i_\infty=1-\dfrac{\mu}{\beta\langle k\rangle}$。只有当 $\beta\langle k\rangle>\mu$ 时 $i_\infty>0$，否则疾病消亡。

**SIR 模型**（如流感、麻疹，痊愈后获得免疫）：

$$\frac{ds}{dt}=-\beta\langle k\rangle si,\qquad \frac{di}{dt}=\beta\langle k\rangle si-\mu i,\qquad \frac{dr}{dt}=\mu i$$

感染比例先升后降，最终 $r_\infty$ 饱和。这一框架可追溯到 Kermack 与 McKendrick（1927）。

**SEIR 模型**在 S 与 I 之间加入潜伏态 E（已感染、尚无传染性），潜伏期结束速率 $\sigma$：$\dot s=-\beta\langle k\rangle si$，$\dot e=\beta\langle k\rangle si-\sigma e$，$\dot i=\sigma e-\mu i$。潜伏期不改变 $R_0$，但拉长每一“代”的时间，使早期增长变慢；COVID-19 等疾病的建模通常用 SEIR 或其扩展（例如区分症状前、无症状感染）。

::: {.callout-def}
**基本再生数** $R_0$：在完全易感人群中，一个典型感染者在整个感染期内平均直接感染的人数。均匀混合时 $R_0=\beta\langle k\rangle/\mu$。$R_0>1$ 疾病可以流行，$R_0<1$ 疾病消亡。定义**传播强度** $\lambda=\beta/\mu$，则流行病阈值为 $\lambda_c=1/\langle k\rangle$。人群分为多类（年龄、度、地区）时，$R_0$ 推广为**下一代矩阵**的谱半径（Diekmann、Heesterbeek 与 Metz 1990；见[再生数与超级传播](spreading.reproduction-number.html)）。
:::

直观例子：若 $R_0=2$，初始 1 人，理想情况下每“代”感染人数为 1、2、4、8……；若 $R_0=0.8$，则 1、0.8、0.64……，期望的总感染人数为 $1/(1-0.8)=5$，疫情自行熄灭。

**最终规模方程**。SIR 中把 $ds/dt$ 除以 $dr/dt$ 得 $ds/dr=-R_0 s$，故 $s=s_0e^{-R_0r}$。疫情结束时 $i=0$，$s_\infty=1-r_\infty$，于是（$s_0\approx1$）

$$r_\infty=1-e^{-R_0r_\infty}.$$

算例：$R_0=2$ 时迭代 $r\leftarrow1-e^{-2r}$ 得 $r_\infty\approx0.797$，即约 80% 的人最终被感染——高于“群体免疫阈值” $1-1/R_0=50\%$，多出的部分是疫情越过峰值后的“惯性”感染（overshoot）。网络上的对应结果见[数学推导与算法](spreading.derivations.html) B 节。

::: {.callout-warn}
$R_0$ 不是病原体的固有常数。它等于“传播概率 × 接触数 × 感染持续时间”，接触结构一变（封校、居家），$R_0$ 就变。[度异质性与流行病阈值](spreading.epidemic-threshold.html)会说明，在网络上起作用的“接触数”甚至不是平均度。
:::

## 度异质性与流行病阈值 {#epidemic-threshold}

均匀混合假设每个人能感染任何人。真实传播只能沿边进行，而且节点的度差别巨大。**异质平均场**（heterogeneous mean-field, HMF）方法把度相同的节点归为一类，记 $i_k(t)$ 为度为 $k$ 的节点中感染者比例。以 SIS 为例：

$$\frac{di_k}{dt}=\beta k\,[1-i_k]\,\Theta(t)-\mu i_k,\qquad \Theta=\frac{\sum_{k'}k'P(k')\,i_{k'}}{\langle k\rangle}$$

$\Theta$ 是“随机沿一条边走到的邻居是感染者”的概率。注意权重是 $k'P(k')/\langle k\rangle$ 而不是 $P(k')$：沿边走更容易走到高度节点（这就是“朋友悖论”）。线性化后可得 Pastor-Satorras 与 Vespignani（2001，PRL）的经典结果：

$$\lambda_c^{\text{SIS}}=\frac{\langle k\rangle}{\langle k^2\rangle},\qquad \lambda_c^{\text{SIR}}=\frac{\langle k\rangle}{\langle k^2\rangle-\langle k\rangle}$$

::: {.callout-def}
**流行病阈值消失**：对度指数 $2<\gamma\le 3$ 的无标度网络，网络规模 $N\to\infty$ 时 $\langle k^2\rangle\to\infty$，于是 $\lambda_c\to 0$——任意小的传播强度都可能导致大范围流行。原因是枢纽节点既容易被感染（邻居多），又能把病原体传给大量邻居。
:::

**估算示例**：ER 随机网络 $\langle k\rangle=6$，泊松分布有 $\langle k^2\rangle=\langle k\rangle^2+\langle k\rangle=42$，$\lambda_c^{\text{SIR}}=6/36\approx0.17$，正好等于 $1/\langle k\rangle$，与均匀混合一致。若一个同样平均度的无标度网络 $\langle k^2\rangle=90$，则 $\lambda_c^{\text{SIR}}=6/84\approx0.07$，阈值降到约 40%。

阈值公式也给出了网络上的再生数：$R_0=\lambda\,\dfrac{\langle k^2\rangle-\langle k\rangle}{\langle k\rangle}$。被感染者是“沿边走到的人”，其平均剩余度（excess degree）$\frac{\langle k^2\rangle-\langle k\rangle}{\langle k\rangle}$ 比 $\langle k\rangle$ 大，度越异质差得越多。减去的 $\langle k\rangle$（即剩余度中的“−1”）来自“传染给自己的那条边不能再用来传播”；SIS 中这条边上的感染者会恢复，之后还可以被回传，所以 SIS 的阈值没有这一项。

### 三种模型的网络解：一张对照表

Barabási《Network Science》10.B 节把 HMF 下三种模型的早期行为放在一起比较。记 $\tau$ 为早期指数增长 $i\propto e^{t/\tau}$ 的特征时间：

| 模型 | 早期特征时间 $\tau$ | 阈值 $\lambda_c$ | 无标度网络（$\gamma\le3$）中 $N\to\infty$ |
|---|---|---|---|
| SI | $\dfrac{\langle k\rangle}{\beta(\langle k^2\rangle-\langle k\rangle)}$ | 无（必然传遍） | $\tau\to0$：瞬时传遍 |
| SIS | $\dfrac{\langle k\rangle}{\beta\langle k^2\rangle-\mu\langle k\rangle}$ | $\dfrac{\langle k\rangle}{\langle k^2\rangle}$ | $\lambda_c\to0$ |
| SIR | $\dfrac{\langle k\rangle}{\beta\langle k^2\rangle-(\beta+\mu)\langle k\rangle}$ | $\dfrac{\langle k\rangle}{\langle k^2\rangle-\langle k\rangle}$ | $\lambda_c\to0$ |

传播的**早期速度**也受异质性影响。Barthélemy 等（2004，PRL）证明网络上 SI 模型的特征时间如表所示；无标度网络中 $\tau\to0$，而且感染呈现层级顺序：先感染枢纽，再扩散到中等度节点，最后到达低度节点。这一“先枢纽后外围”的顺序正是[接触追踪与监测](spreading.contact-tracing.html)中“社交网络传感器”的理论基础。

### 淬火平均场与度相关

HMF 只用度分布。若把每个节点单独作为变量（**个体平均场**，也叫淬火平均场 QMF 或 NIMFA），记 $\rho_i$ 为节点 $i$ 被感染的概率：

$$\frac{d\rho_i}{dt}=-\mu\rho_i+\beta(1-\rho_i)\sum_jA_{ij}\rho_j .$$

在 $\rho=0$ 处线性化，增长矩阵为 $\beta A-\mu I$，于是阈值为 $\lambda_c=1/\Lambda_{\max}$，$\Lambda_{\max}$ 是邻接矩阵的最大特征值（Wang、Chakrabarti 等的工作，正式发表见 Chakrabarti 等 2008；Van Mieghem、Omic 与 Kooij 2009）。对无度相关的网络，$\Lambda_{\max}$ 大致取 $\sqrt{k_{\max}}$ 与 $\langle k^2\rangle/\langle k\rangle$ 中较大者：当最大度足够大时，$\Lambda_{\max}$ 由单个枢纽的“星形”结构决定，对应的特征向量**局域化**在枢纽周围。这时 QMF 预测的是“枢纽周围的局部活跃”，未必是全网流行，HMF 与 QMF 的分歧由此而来（Castellano 与 Pastor-Satorras 2010）。

**度相关**。HMF 假设邻居的度与自身的度无关。若存在度相关，条件概率 $P(k'|k)$（度为 $k$ 的节点的邻居度为 $k'$ 的概率）取代 $k'P(k')/\langle k\rangle$，SIS 阈值变为矩阵 $C_{kk'}=kP(k'|k)$ 最大特征值的倒数（SIR 中用 $(k'-1)P(k'|k)$ 一类的剩余度形式）。同配网络（高度节点彼此相连）中枢纽形成一个相互支撑的“核心”，通常更容易维持流行；异配网络则相反。详细讨论见 Pastor-Satorras 等（2015）综述第 4 节；度相关的度量见[度相关性与网络结构的高阶统计](degree-correlations.html)。

::: {.callout-warn}
“阈值为 0”是 $N\to\infty$ 的渐近结论。有限网络的 $\langle k^2\rangle$ 有限，阈值是小而非零；而且度相关性、聚集、社团结构都会改变实际阈值。HMF（$\langle k\rangle/\langle k^2\rangle$）、QMF（$1/\Lambda_{\max}$）与消息传递（$1/\rho(B)$）在同一张网络上可以给出明显不同的数值，代码示例“三种阈值近似的比较”演示了这一点（[代码](spreading.html#code)）；综述见 Pastor-Satorras 等（2015，Rev Mod Phys）。
:::

::: {.callout-bio}
性接触网络的度分布具有重尾特征（Liljeros 等，2001，Nature，基于瑞典的性行为调查），这为“少数高接触人群对性传播疾病流行贡献大”提供了网络解释，也解释了为什么针对高风险人群的干预效率高。
:::

阈值公式的完整推导（HMF 自洽方程、自然截断下 $\lambda_c$ 随 $N$ 的标度）见[数学推导与算法](spreading.derivations.html)。

## 接触网络：数据与结构 {#contact-networks}

理论结果都以“接触网络”为输入。对传染病而言，什么算一条边取决于传播途径：性传播疾病是性伴侣关系，呼吸道疾病是近距离（约 1–3 米内）的面对面接触，院内感染还包括共用病房、器械与医护人员的手。构建接触网络的一般原则见[网络构建与统计验证](network-construction.html)，这里只讨论传播研究中的特殊之处。

### 数据来源

| 数据类型 | 例子 | 得到的结构 | 主要局限 |
|---|---|---|---|
| 问卷与接触日记 | POLYMOD 欧洲 8 国接触调查（Mossong 等 2008，PLoS Med） | 按年龄分组的**接触矩阵** | 回忆偏倚；只有群体平均，没有个体网络 |
| 性行为调查 | 瑞典性接触调查（Liljeros 等 2001） | 伴侣数的分布（重尾） | 只有度，没有谁与谁相连 |
| 交易或登记记录 | 巴西在线论坛记录的约 5 万次性交易（Rocha、Liljeros 与 Holme 2011） | 带时间戳的二分时间网络 | 特定人群，代表性有限 |
| 可穿戴近距离传感器 | 美国一所高中 788 人一天内的 762 868 次近距离接触（Salathé 等 2010，PNAS）；法国一家医院老年科病区（Vanhems 等 2013，PLoS ONE） | 带时间与持续时长的高分辨率接触网络 | 研究时间短；覆盖不全 |
| 手机与移动数据 | 人口流动、到访地点（Chang 等 2021，Nature） | 地点–人群二分网络、城市间流动网络 | 隐私；只反映共处而非真实接触 |
| 合成人口 | 基于普查、交通调查合成的城市人口网络（Eubank 等 2004，Nature） | 家庭、学校、工作场所的分层网络 | 依赖大量模型假设 |

### 接触网络的典型结构

真实接触网络与理论常用的配置模型有几处系统差别，每一处都会改变传播：

- **度异质性因传播途径而异**。性接触网络重尾，而 Salathé 等（2010）的高中近距离接触网络中，接触时长与接触对象数在个体间分布相对均匀。重尾度分布不是所有接触网络的普遍性质，不能不加检验地套用“阈值为零”。
- **高聚集与家庭结构**。同一家庭、同一病房的人彼此都接触，形成团（clique）。团内的重复接触“浪费”传播机会（感染者的邻居已经被同一团的其他人感染），通常降低增长率与最终规模；配对近似可部分纳入这一效应（见[配对近似、边基模型与消息传递](spreading.message-passing.html)）。
- **年龄同配**。POLYMOD 显示接触高度集中在同龄人之间，学龄儿童之间接触最密集。因此呼吸道疾病模型通常用年龄结构的下一代矩阵，而不是单一的 $R_0$。
- **时间性**。接触有先后、有持续时长、昼夜与工作日周期明显。把一段时间的接触累积成一张静态图会凭空制造出“不可能的传播路径”（见[时间网络与阵发性](spreading.temporal-networks.html)）。
- **加权**。接触时长与频率构成边权。累积暴露时间越长，传播概率越高，常用 $T_{ij}=1-e^{-\beta w_{ij}}$ 把边权（累积接触时长 $w_{ij}$）转换为传播性。

::: {.callout-bio}
**医院病区的接触网络**。Vanhems 等（2013）在法国一家大学医院的老年科病区让 46 名医护人员和 29 名患者佩戴近距离传感器 4 天 4 夜，空间分辨率约 1.5 米、时间分辨率 20 秒，共记录 14 037 次接触，其中 94.1% 发生在白天，38% 发生在护士之间（全部医护人员之间合计约 73%）；6 名医护人员占了所有涉及患者的接触的 42%，提示存在潜在的“超级传播者”岗位。不同日期的接触模式在统计上相当稳定，这意味着基于短期测量设计的感染控制方案（例如对少数高接触岗位重点培训手卫生）有可能长期适用。
:::

## 配对近似、边基模型与消息传递 {#message-passing}

HMF 有两个关键缺陷：（1）它把同一度类的节点看成可互换的，丢掉了具体拓扑；（2）它忽略了相邻节点状态之间的**动态相关**——例如在 SIR 中，感染我的那个邻居不可能再被我感染，HMF 只能用剩余度中的“−1”粗略修正。这一页介绍三类更精确的方法，它们是 Kiss、Miller 与 Simon（2017）《Mathematics of Epidemics on Networks》的主体内容。

### 配对近似

**思路**：除了单个节点的计数 $[S],[I]$，还跟踪成对计数 $[SI]$（S–I 边的数目）、$[SS]$ 等。以 SIR 为例，设每条 S–I 边上的传播速率为 $\tau$，恢复率为 $\gamma$：

$$\frac{d[S]}{dt}=-\tau[SI],\qquad \frac{d[I]}{dt}=\tau[SI]-\gamma[I],$$

$$\frac{d[SI]}{dt}=\tau\big([SSI]-[ISI]-[SI]\big)-\gamma[SI],\qquad \frac{d[SS]}{dt}=-2\tau[SSI].$$

这里 $[SSI]$ 是三元组（S–S–I 的路径）计数：中间的 S 被右边的 I 感染后，左边的 S–S 边变成 S–I 边；$[ISI]$ 是中间的 S 被另一侧 I 感染时，这条 S–I 边变成 I–I 边。方程不封闭（成对的方程需要三元组），必须**矩封闭**（moment closure）。在每个节点度都为 $n$ 的网络上，最常用的闭合是

$$[ABC]\approx\frac{n-1}{n}\,\frac{[AB][BC]}{[B]} .$$

含义：已知中间节点是 $B$，它两侧邻居的状态近似独立；因子 $(n-1)/n$ 修正“同一个节点的 $n$ 条边中已经用掉了一条”。Keeling（1999，Proc R Soc B）在闭合中再加入聚集系数 $\phi$ 的修正项，使三角形内的重复接触被计入，得到“聚集降低增长率”的定量结果。配对近似简单、可推广到聚集网络，但闭合是启发式的，对重尾度分布不够准确。

### 边基仓室模型（EBCM）

Volz（2008，J Math Biol）以及 Miller、Slim 与 Volz（2012，J R Soc Interface）提出了对配置模型上 SIR **精确**（在 $N\to\infty$ 极限下）而且只有一个方程的描述。关键变量是

$$\theta(t)=\text{一条随机选出的边，到时刻 } t \text{ 为止还没有把感染从邻居传到“我”这里的概率}.$$

一个度为 $k$ 的节点在时刻 $t$ 仍易感，当且仅当它的 $k$ 条边都还没传来感染，概率为 $\theta^k$；对度分布平均，$S(t)=\psi(\theta)$，$\psi(x)=\sum_kP(k)x^k$ 是度分布的生成函数。$\theta$ 满足

$$\frac{d\theta}{dt}=-\beta\theta+\beta\frac{\psi'(\theta)}{\psi'(1)}+\gamma(1-\theta),\qquad \frac{dR}{dt}=\gamma I,\qquad I=1-S-R .$$

推导要点：$1-\theta$ 可分解为“邻居尚未感染”“邻居已感染但还没传过来”“已经传过来”“邻居已恢复而没传过来”几部分，其中“邻居尚未感染”的概率是邻居的其余 $k'-1$ 条边都没传来感染，即 $\psi'(\theta)/\psi'(1)$。代码示例“边基仓室模型与精确随机模拟的比较”显示，在 5000 个节点的配置模型上，EBCM 的感染曲线与事件驱动随机模拟的平均曲线几乎重合，而同参数的均匀混合 ODE 把最终规模从约 0.61 高估到 0.93（[代码](spreading.html#code)）。

### 消息传递

**消息传递**（message passing，也称置信传播或腔方法）为每条**有向边**定义一个消息。对 SIR 的最终规模（Karrer 与 Newman 2010，PRE；更早的配置模型版本见 Newman 2002），记 $u_{i\leftarrow j}$ 为“去掉节点 $i$ 后，$j$ 不被大暴发感染”的概率，则

$$u_{i\leftarrow j}=1-T+T\prod_{l\in\partial j\setminus i}u_{j\leftarrow l},\qquad P(i\ \text{被感染})=1-\prod_{j\in\partial i}u_{i\leftarrow j}.$$

第一式的含义：边 $j\to i$ 要么不通（概率 $1-T$），要么通了但 $j$ 本身没有从**除 $i$ 以外**的邻居处被感染。“除 $i$ 以外”正是消除回声（echo chamber）的关键：在 HMF 和 QMF 中，$i$ 感染 $j$、$j$ 再“把感染算回给” $i$ 的虚假反馈被错误地计入了。

在 $u\equiv1$（无病态）附近线性化，得到 $\delta=T B\,\delta$，其中 $B$ 是**非回溯矩阵**（non-backtracking 或 Hashimoto 矩阵）：

$$B_{(k\to l),(i\to j)}=\delta_{jk}\,(1-\delta_{il}),$$

即从有向边 $i\to j$ 只能走到 $j\to l$ 且 $l\neq i$。于是 SIR 阈值为 $T_c=1/\rho(B)$。

- 在局部树状的网络上，消息传递对最终规模与阈值是**精确**的；有短环（三角形）时是近似，但通常仍优于 HMF 与 QMF。
- 对配置模型，$\rho(B)\approx(\langle k^2\rangle-\langle k\rangle)/\langle k\rangle$，回到 HMF 的 SIR 阈值。
- $B$ 有 $2m$ 行，直接构造代价高；Ihara–Bass 恒等式表明 $\rho(B)$ 等于 $2N\times2N$ 矩阵 $\begin{pmatrix}A & I-D\\ I & 0\end{pmatrix}$ 的最大特征值（$D$ 为度对角阵），代码示例正是这样计算的。
- 非回溯矩阵的特征向量不像 $A$ 那样在枢纽周围局域化，因此也被用于社团发现与关键节点识别（[影响力最大化与关键传播者](spreading.influential-spreaders.html)中的集体影响）。

**动态消息传递**进一步给出每个节点随时间的感染概率（Lokhov 等 2014 把它用于[传播溯源](spreading.source-localization.html)）。对一般的二元状态动力学（包括阈值模型），Gleeson（2011，PRL）的**近似主方程**（AME）按“度 $k$、已感染邻居数 $m$”跟踪节点比例，精度很高，代价是变量数约为 $k_{\max}^2/2$。

| 方法 | 适用 | 优点 | 局限 |
|---|---|---|---|
| HMF | 无度相关的大网络 | 解析、直观 | 忽略拓扑与动态相关 |
| QMF / NIMFA | 任意给定网络（SIS） | 只需最大特征值 | 局域化时高估流行，忽略动态相关 |
| 配对近似 | 规则或近规则、含聚集的网络 | 能纳入聚集 | 闭合是启发式的 |
| EBCM | 配置模型上的 SIR | 低维、在大 $N$ 极限精确 | 依赖配置模型假设 |
| 消息传递 | 给定稀疏网络上的 SIR / 渗流 | 树上精确，可算个体风险 | SIS 处理困难；短环多时有偏 |
| AME | 二元状态动力学（含阈值模型） | 精度高 | 变量多，需度分布与无相关假设 |

## 时间网络与阵发性 {#temporal-networks}

前面的理论都假设接触网络是**静态**的。Barabási 第 10.5 节“超越度分布”指出，真实接触还有三类结构会实质性地改变传播：时间顺序与阵发性、度相关、边权与社团。本页讨论时间与社团，度相关见[度异质性与流行病阈值](spreading.epidemic-threshold.html)。

### 时间相容路径

**时间网络**（temporal network）把接触记为带时间戳的事件 $(i,j,t)$ 或区间 $(i,j,t,\Delta t)$（Holme 与 Saramäki 2012，Phys Rep 综述）。传播只能沿**时间相容路径**（time-respecting path）进行：路径上的接触时间必须单调不减。

**算例**：A–B 在第 1 天接触，B–C 在第 3 天接触。若 A 第 0 天感染，它可以经 B 传到 C；若接触顺序颠倒（B–C 第 1 天，A–B 第 3 天），C 永远不会被 A 传染。累积成静态图后两种情形都是路径 A–B–C，无法区分。因此：

- 时间网络上的“可达”关系**不对称**、**不传递**：A 能到 B、B 能到 C，并不意味着 A 能到 C；
- 累积静态网络通常**高估**传播范围与速度。

### 阵发性与事件间隔

人类活动是**阵发**的（bursty）：两次接触之间的间隔 $\Delta t$ 服从重尾分布，短时间内连续多次接触之后是很长的静默期。常用阵发性系数 $B=(\sigma_{\Delta t}-m_{\Delta t})/(\sigma_{\Delta t}+m_{\Delta t})$ 度量，$m,\sigma$ 是间隔的均值与标准差：泊松过程 $B=0$，周期过程 $B=-1$，高度阵发 $B\to1$。

阵发性对传播速度的影响由**等待时间悖论**主导：病原体到达一个节点的时刻相当于在时间轴上随机落点，落入长间隔的概率正比于间隔长度，因此平均剩余等待时间为 $\langle\Delta t^2\rangle/(2\langle\Delta t\rangle)$，而不是 $\langle\Delta t\rangle/2$。重尾间隔使 $\langle\Delta t^2\rangle$ 很大，传播被拖慢。

- Vazquez 等（2007，PRL）在电子邮件病毒传播等数据上发现，重尾的事件间隔使流行病的早期衰减远慢于泊松假设的预测；
- Karsai 等（2011，PRE）在手机通话网络上做“打乱时间戳”的对照实验，发现阵发性与社团–边权相关共同使 SI 传播显著变慢（“小而慢的世界”）。

### 活动驱动模型

Perra 等（2012，Sci Rep）提出**活动驱动模型**：每个节点 $i$ 有活动潜能 $a_i$，每个时间步以概率 $a_i$ 激活并与 $m$ 个随机节点建立只持续一步的接触。它在任何瞬间都是稀疏的，累积起来却会形成枢纽（高活动个体）。线性化平均场给出 SIS 阈值（推导见[数学推导与算法](spreading.derivations.html) D 节）

$$\frac{\lambda}{\mu}>\frac{1}{m\big(\langle a\rangle+\sqrt{\langle a^2\rangle}\big)},$$

$\lambda$ 为每次 S–I 接触的传播概率。阈值由活动性的一阶与二阶矩决定，类似于静态网络中的 $\langle k\rangle$ 与 $\langle k^2\rangle$；而把接触累积成静态网络再套用静态公式，会因“同时存在的接触”被高估而得出错误的阈值与流行规模。对一般的离散时间网络序列 $A_1,\dots,A_T$，Valdano 等（2015，PRX）给出了基于“感染传播子” $\prod_t\big[(1-\mu)I+\lambda A_t\big]$ 谱半径的阈值计算方法。

### 边权与社团

- **弱关系**。按 Granovetter 的弱关系理论（见[社团结构与社区发现](community-structure.html)），社团内部的边强（接触频繁），连接社团的桥是弱的。对传染病而言，强边上的重复接触多“浪费”在已经感染的人身上，弱边虽然少却决定了能否跨社团传播。
- **社团减缓与截留传播**。Salathé 与 Jones（2010，PLoS Comput Biol）在模拟中发现，社团结构越强，暴发越小、越慢；而且此时优先免疫连接不同社团的“桥接节点”比按度免疫更有效（见[免疫策略](spreading.immunization.html)）。
- **层级结构**。家庭–学校–社区的多层嵌套使疾病先在家庭内饱和、再经学校或工作场所跳到其他家庭，这是“家庭模型”（household models）一类理论的出发点。

::: {.callout-warn}
从可穿戴传感器或手机数据得到的接触网络是**时间网络**。分析前要先决定时间聚合窗口：窗口太长会制造不存在的时间相容路径，太短则统计量不稳定。至少应报告结果对窗口长度的敏感性，或者直接在时间网络上模拟（打乱时间戳、保留边集的零模型可以检验“时间顺序本身”的贡献）。
:::

## 集合种群与全球传播 {#metapopulation}

在城市、国家尺度上追踪每个人的接触既不可能也无必要。**集合种群模型**（metapopulation model，又译复合种群模型）把人群分成若干“斑块”（城市、社区、医院），斑块内均匀混合，斑块之间通过人员流动耦合。网络的节点是斑块，边是流动通量 $w_{mn}$。

### 模型结构

以 SIR 为例，斑块 $n$ 中的感染人数满足

$$\frac{dI_n}{dt}=\beta\frac{S_nI_n}{N_n}-\mu I_n+\sum_m\big(p_{mn}I_m-p_{nm}I_n\big),$$

$p_{nm}$ 是 $n$ 中个体单位时间去往 $m$ 的概率。实际中，旅行者只占人口的很小比例，流动项对局部动力学影响很小，但决定了疾病**能否以及何时**到达新的斑块。

- **全球航空网络**。Hufnagel、Brockmann 与 Geisel（2004）在全球主要机场之间的航空网络上模拟 SARS 的扩散；Colizza 等（2006，PNAS）系统分析航空网络的度与流量异质性对全球流行可预测性的影响：流量的异质性使传播路径集中在少数主干航线上，反而提高了可预测性。
- **多尺度流动**。Balcan 等（2009，PNAS）在 GLEaM（全球流行与流动）模型中同时纳入航空与地面通勤，发现短程通勤流量虽然大，但全球扩散的时间格局主要由航空网络决定，通勤主要影响局部同步。
- **入侵阈值**。Colizza 与 Vespignani（2007，PRL）指出，即使每个斑块内部 $R_0>1$，若旅行率太低，感染者在恢复前离开斑块的期望人数不足，疾病也可能无法在斑块间扩散。这给出第二个阈值——斑块层面的**全局入侵阈值** $R_*>1$；$R_*$ 随旅行率与 $R_0-1$ 增大而增大，并且同样被斑块网络的度异质性降低。它对应的干预就是限制旅行。

### 有效距离

Brockmann 与 Helbing（2013，Science）发现，若把地理距离换成由流量定义的**有效距离**

$$d_{mn}=1-\ln P_{mn},\qquad P_{mn}=\frac{w_{mn}}{\sum_{m'}w_{m'n}},$$

（$w_{mn}$ 为从 $n$ 到 $m$ 的旅客流量，$P_{mn}$ 为离开 $n$ 的旅客中去往 $m$ 的比例），那么从源头出发、沿最短有效路径计算的距离与疾病到达时间近似成正比，复杂的全球扩散图案变成了从源头出发的“同心圆波”。两个直接应用：（1）即使不知道 $R_0$ 等参数，也能预测各地的**相对**到达顺序；（2）若源头未知，可以找一个使到达时间与有效距离最一致的节点作为候选源头（见[传播溯源](spreading.source-localization.html)）。他们用 2009 年 H1N1 流感与 2003 年 SARS 的数据验证了这一方法。代码示例在随机流动网络上重现了这一现象：到达时间与有效距离的相关系数约 0.88，与跳数距离只有约 0.61（[代码](spreading.html#code)）。

::: {.callout-bio}
**旅行限制的作用与局限**。Chinazzi 等（2020，Science）用全球集合种群模型评估 COVID-19 初期的旅行限制：2020 年 1 月 23 日武汉实施出行管控时，中国大陆多数城市已经输入了大量感染者，因此出行管控只把中国大陆的整体疫情进程推迟了 3–5 天，但在国际尺度上作用更明显——到 2 月中旬前，输出到其他国家的病例减少了近 80%；模型还显示，即使持续限制 90% 的进出旅行，若不同时把社区传播降低 50% 或以上，对疫情轨迹的影响也有限。结论与入侵阈值理论一致：旅行限制主要**推迟**到达，真正改变疫情规模要靠降低本地传播。
:::

**更细的流动网络**。Chang 等（2021，Nature）用手机定位数据构建美国 10 个大都市区的“社区—兴趣点”（餐馆、宗教场所等）二分流动网络，覆盖约 9800 万人，在其上运行集合种群 SEIR 模型。模型拟合了实际病例曲线，并预测少数“超级传播地点”贡献了大部分感染、限制每个地点的最大容纳人数比整体按比例减少出行更有效，还仅凭流动模式的差异就解释了弱势群体更高的感染率。

### 流行病预测

Barabási 第 10.7 节讨论的“实时预测”通常结合三部分：（1）集合种群或个体模型；（2）由早期病例数据校准的参数（$R_0$、代际间隔，见[再生数与超级传播](spreading.reproduction-number.html)）；（3）大量随机模拟给出的预测区间。预测的可靠性有天然上限：早期的随机性（谁先被感染、是否发生超级传播事件）、行为改变与干预措施都会使轨迹偏离模型。因此，**到达时间与传播顺序**通常比**病例数峰值**更容易预测。


## 再生数与超级传播 {#reproduction-number}

$R_0$ 是传播理论的中心量，但它既不能直接观测，在网络上还有多种含义。本页讨论如何定义、估计并解释再生数，以及个体传播能力的异质性（超级传播）。

### 下一代矩阵

人群分为 $n$ 类（年龄组、度类、地区）时，定义**下一代矩阵** $K$：$K_{ij}$ 是一个 $j$ 类感染者在完全易感人群中平均直接感染的 $i$ 类人数。每一代感染者的类别构成按 $x^{(g+1)}=Kx^{(g)}$ 演化，所以

$$R_0=\rho(K)\quad(\text{谱半径，即最大特征值的模}),$$

这一定义来自 Diekmann、Heesterbeek 与 Metz（1990，J Math Biol）。

**网络上的下一代矩阵**。按度分类，一个度为 $k'$ 的感染者（它是被某个邻居感染的，所以还剩 $k'-1$ 条可用的边）平均感染 $T(k'-1)$ 个邻居，这些邻居的度为 $k$ 的概率是 $kP(k)/\langle k\rangle$。于是 $K_{kk'}=T\,\dfrac{kP(k)}{\langle k\rangle}(k'-1)$，这是秩为 1 的矩阵，其谱半径为

$$R_0=T\sum_k\frac{kP(k)}{\langle k\rangle}(k-1)=T\,\frac{\langle k^2\rangle-\langle k\rangle}{\langle k\rangle},$$

正是[度异质性与流行病阈值](spreading.epidemic-threshold.html)中的网络再生数。

::: {.callout-warn}
**网络上的“第一代”与“稳定代”不同**。一个随机选出的首发病例平均感染 $T\langle k\rangle$ 人；但第二代及以后的感染者是“沿边走到的人”，平均感染 $T(\langle k^2\rangle-\langle k\rangle)/\langle k\rangle$ 人。在度异质网络中，后者可以远大于前者。用“首发病例的平均继发病例数”估计 $R_0$ 会低估流行潜力；在暴发早期，被感染者的度分布也会偏向高度，随后逐渐“回归”，所以早期估计的增长率可能高于之后。
:::

### 从增长率到再生数

暴发早期病例数近似指数增长 $I(t)\propto e^{rt}$，增长率 $r$ 可以从发病曲线拟合。把 $r$ 换算为 $R$ 需要**代际间隔**（generation interval）分布 $g(\tau)$：一个感染者从被感染到感染他人的时间间隔。Wallinga 与 Lipsitch（2007，Proc R Soc B）给出关系

$$R=\frac{1}{M(-r)},\qquad M(-r)=\int_0^\infty e^{-r\tau}g(\tau)\,d\tau .$$

**算例**：若代际间隔服从均值为 $T_g$ 的指数分布，$M(-r)=1/(1+rT_g)$，于是 $R=1+rT_g$。若 $r=0.2/\text{天}$、$T_g=5$ 天，$R=2$；若代际间隔固定为 5 天（零方差），$R=e^{rT_g}=e^{1}\approx2.72$。同一条增长曲线，代际间隔分布的形状不同，推出的 $R$ 相差可达 35%。SIR 模型的代际间隔是指数分布（均值 $1/\mu$），故 $R_0=1+r/\mu$；SEIR 模型为 $R_0=(1+r/\sigma)(1+r/\mu)$。

### 时变再生数 $R_t$

干预与人群免疫会使再生数随时间变化。**有效再生数** $R_t$ 指在时刻 $t$ 的条件下一个感染者平均造成的继发病例数。两种常用估计：

- **病例再生数**（Wallinga 与 Teunis 2004，Am J Epidemiol）：根据发病时间和序列间隔分布，计算每个病例 $j$ 被另一个病例 $i$ 感染的相对似然 $p_{ij}$，病例 $i$ 的再生数为 $\sum_jp_{ij}$，再按发病日期平均。它回答“在 $t$ 日发病的人后来平均感染了多少人”。他们用这一方法比较 2003 年香港、越南、新加坡与加拿大的 SARS 疫情，发现各地的传播潜力与控制措施效果相近，并估计控制措施推迟一周会使疫情规模增加到将近三倍。
- **瞬时再生数**（Cori 等 2013，Am J Epidemiol；软件 EpiEstim）：基于更新方程 $E[I_t]=R_t\sum_{s\ge1}w_sI_{t-s}$，$w_s$ 为代际（序列）间隔分布。在长度为 $\tau$ 的窗口内假设 $R_t$ 不变，并给 $R_t$ 一个 Gamma 先验，则后验仍是 Gamma 分布，形状参数为 $a+\sum I_s$，速率参数为 $1/b+\sum\Lambda_s$，其中 $\Lambda_s=\sum_uw_uI_{s-u}$ 是“总感染力”。

代码示例“从发病曲线估计时变再生数”中，真实 $R_t$ 在第 40 天从 2.0 降到 0.7，估计值在约一个窗口长度（7 天）的滞后后跟上了下降（[代码](spreading.html#code)）。

::: {.callout-warn}
$R_t$ 估计对代际间隔分布、报告延迟和检测强度的变化都很敏感：检测量突然增加会被误读为 $R_t$ 上升。在网络上，$R_t$ 的下降不仅来自易感者减少，还来自**高度节点先被感染**——网络中有效易感者的消耗比均匀混合假设的 $R_t=R_0s(t)$ 更快，因此群体免疫阈值也可能低于 $1-1/R_0$。
:::

### 个体异质性与超级传播

$R_0$ 是平均数，掩盖了个体差异。Lloyd-Smith 等（2005，Nature）分析 8 种直接传播疾病的接触追踪数据，发现个体再生数 $\nu$ 的分布通常高度偏斜。他们把继发病例数建模为**负二项分布**（相当于 $\nu$ 服从均值 $R_0$、形状参数 $k$ 的 Gamma 分布，再叠加泊松抽样），**离散参数** $k$ 越小，个体差异越大：$k\to\infty$ 时为泊松（无个体差异），$k=1$ 时为几何分布。

负二项后代分布的概率生成函数为 $g(s)=\big[1+\tfrac{R_0}{k}(1-s)\big]^{-k}$。由分支过程理论，从一个首发病例开始、疫情最终自行灭绝的概率 $q$ 是方程 $q=g(q)$ 在 $[0,1]$ 中的最小根。算例（$R_0=2.5$，代码示例“超级传播”）：

| 离散参数 $k$ | 灭绝概率 $q$ | 零继发病例的比例 | 造成 80% 传播的感染者比例 |
|---|---|---|---|
| 0.1 | 0.86 | 0.72 | 约 9% |
| 0.5 | 0.56 | 0.41 | 约 28% |
| 1.0 | 0.40 | 0.29 | 约 36% |
| 10 | 0.14 | 0.11 | 约 54% |

$R_0$ 相同时，$k$ 越小，疫情越容易在早期自行熄灭，但一旦暴发就更“爆炸”。Lloyd-Smith 等据此指出，针对个体的控制措施优于全人群均匀的措施，而识别高传播性个体的预测因素至关重要。

::: {.callout-bio}
**COVID-19 的超级传播**。Adam 等（2020，Nature Medicine）利用香港 2020 年 1 月 23 日至 4 月 28 日确诊的 1038 例 SARS-CoV-2 感染的接触追踪数据，识别出全部本地聚集性疫情，在 51 个聚集（309 例）中识别出 4–7 次超级传播事件，估计 19%（95% CI 15–24%）的病例造成了 80% 的本地传播。控制年龄后，社交场所的传播比家庭内产生更多继发病例；作为接触者被隔离的个体中断传播的比值比为 14.4（95% CI 1.9–107.2）。这些结果支持把资源集中在快速追踪与隔离接触者，以及限制社交聚集场所。
:::

超级传播有三类不同来源，干预含义也不同：**网络位置**（接触多的人，见[免疫策略](spreading.immunization.html)）、**生物学**（排毒量高、症状轻而继续活动）、**情境**（通风差的室内聚集，对应 Chang 等 2021 的“超级传播地点”）。网络模型通常只描述第一类，单凭度分布不能解释全部超级传播。

## 免疫策略 {#immunization}

控制疫情的三类手段在网络上的含义不同：

- **降低传播率**（口罩、手卫生、通风）：降低 $\beta$，即每条边的传播性 $T$；
- **减少接触**（隔离、停课、限制聚集规模）：删边，网络变稀疏；
- **接种疫苗**：删点，被接种者不再传播。

**随机免疫**：随机接种比例 $g$ 的人，等价于把传播强度变为 $\lambda(1-g)$。要阻断流行需 $\lambda(1-g)<\lambda_c$，即临界接种比例 $g_c=1-\lambda_c/\lambda$。均匀混合时 $\lambda_c/\lambda=1/R_0$，就是熟悉的群体免疫阈值 $g_c=1-1/R_0$（$R_0=3$ 时需 67%）。在无标度网络中 $\lambda_c\to0$，于是 $g_c\to1$：几乎要接种所有人。从渗流的角度看，随机免疫就是**随机删点**，而无标度网络对随机删点极其鲁棒（见[网络鲁棒性、渗流与级联失效](robustness.html)）。

**目标免疫**：优先接种度最高的节点。删除枢纽会迅速降低 $\langle k^2\rangle$，阈值显著升高（Pastor-Satorras 与 Vespignani 2002；Dezső 与 Barabási 2002，均发表于 PRE）。Barabási 10.C 节给出了这一效应的定量估计：对度指数为 $\gamma$ 的无标度网络，接种度最高的比例 $g$ 的节点后，剩余网络的最大度从 $\infty$ 降到 $k_c=k_{\min}g^{-1/(\gamma-1)}$，于是 $\langle k^2\rangle$ 变为有限值，阈值随 $g$ 以幂律上升；阻断流行所需的 $g_c$ 只是 $\lambda$ 的幂函数，远小于随机免疫的 $g_c\to1$（推导见[数学推导与算法](spreading.derivations.html) F 节）。问题是现实中往往不知道谁是枢纽。

**熟人免疫**（acquaintance immunization，Cohen、Havlin 与 ben-Avraham，2003，PRL）：随机选一个人，再让他随机提名一个熟人，给这个熟人接种。由于沿边到达高度节点的概率正比于 $k$，这个只用局部信息的策略接近目标免疫的效果。

::: {.callout-def}
**朋友悖论在免疫中的应用**：随机节点的平均度是 $\langle k\rangle$，随机节点的随机邻居的平均度是 $\langle k^2\rangle/\langle k\rangle\ge\langle k\rangle$。熟人免疫正是利用这一点“不看全局也能找到枢纽”。
:::

接种同样比例的人，不同策略下的最终感染规模可能相差数倍。本专题的代码示例在 BA 网络上比较这三种策略：各接种 10% 的节点后，计算剩余网络的阈值 $T_c$ 与巨连通分支比例。

### 利用社团与全局结构的策略

- **社团桥接免疫**。在社团结构明显的网络中，度最高的节点往往位于社团内部，免疫它们并不能阻止疾病在社团之间跳跃。Salathé 与 Jones（2010）提出“社团桥接寻找”（community bridge finder）策略：用只依赖局部信息的随机游走识别连接不同社团的桥接节点并优先接种。在社团结构强的网络中，它优于按度或熟人免疫。
- **基于渗流的最优免疫**。从渗流角度，最优免疫就是找到最小的节点集合，删除后网络的巨分支消失，这是“最优渗流”问题，NP 难。Morone 与 Makse（2015，Nature）用非回溯矩阵把它化为最小化一个能量函数，并提出集体影响（CI）启发式，见[影响力最大化与关键传播者](spreading.influential-spreaders.html)。
- **介数与桥**。按介数免疫能切断连接不同区域的“桥”，在空间或社团网络中常优于按度免疫，但需要全局拓扑信息，计算代价也高。

::: {.callout-bio}
**基于接触网络数据的校园免疫**。Salathé 等（2010，PNAS）用无线传感器记录美国一所高中典型一天内 788 人之间的近距离接触（覆盖率 94%，共 762 868 次、距离 3 米以内），在加权接触图上模拟流感样疾病的传播，模拟结果与该流感季的缺勤数据吻合良好。比较多种目标免疫策略后，他们发现需要真实接触网络数据才能设计出显著优于随机免疫的策略，而且基于接触网络的策略在高接种覆盖率时优势最明显。
:::

## 接触追踪与监测 {#contact-tracing}

疫苗出现之前，控制新发传染病主要依靠**发现—隔离—追踪**：发现病例并隔离，追踪其接触者并检疫。从网络角度，接触追踪就是沿着传播树的边去寻找尚未被发现的感染者。

### 什么决定追踪能否成功

Fraser、Riley、Anderson 与 Ferguson（2004，PNAS）指出，隔离有症状者和追踪检疫接触者这两项措施能否控制疫情，不仅取决于 $R_0$，同样取决于**症状出现前（或无症状）传播的比例** $\theta$：只有在出现症状之后才发生的传播才能被隔离阻断。他们根据已发表的参数估计，SARS 与天花（症状前传播少）比 HIV 与大流行性流感更容易用这些简单措施控制，并强调在新发传染病暴发中应优先通过接触追踪直接估计无症状与症状前感染的比例。

在网络框架中，Eames 与 Keeling（2003，Proc R Soc B）分析了接触追踪在网络传播中的控制效果，说明追踪的价值取决于接触网络的局部结构与追踪的及时性。对 COVID-19，Ferretti 等（2020，Science）估计了不同传播途径（症状前、有症状、无症状、环境）的贡献，结论是 SARS-CoV-2 传播太快，人工追踪难以控制，但若追踪更快、更高效、规模更大——例如一个记住近距离接触并在病例确诊后立即通知接触者的手机应用，在足够多的人使用时可以控制疫情，而无需全面封锁。Kucharski 等（2020，Lancet Infect Dis）比较了隔离、检测、追踪与保持社交距离在不同场所组合下降低传播的效果。

### 向后追踪与朋友悖论

追踪有两个方向：**向前追踪**找“病例传给了谁”，**向后追踪**找“病例是从谁那里感染的”。Kojaku 等（2021，Nature Physics）证明，在接触异质的网络中向后追踪远比向前追踪有效。原因是传播树上的“朋友悖论”：

- 记个体的继发病例数为 $Z$，一个随机病例的继发病例数平均为 $E[Z]=R$；
- 但一个随机病例的**传染源**是按其继发病例数加权抽到的（传了 $Z$ 个人的感染者有 $Z$ 次机会成为别人的传染源），其继发病例数的期望是 $E[Z^2]/E[Z]=R+\mathrm{Var}(Z)/R$——被感染者更可能来自“多产”的感染者。

**算例**：若 $Z$ 服从负二项分布，$\mathrm{Var}(Z)=R+R^2/k$。取 $R=1.5$、$k=0.2$，则随机病例的传染源平均有 $1.5+1+1.5/0.2=10$ 个继发病例。向后追踪一次，就可能找到一个超级传播者及其牵出的整个聚集。代码示例“向前追踪与向后追踪”在 BA 网络的 SIR 传播树上得到：随机病例平均只传给约 1 人（每个病例除种子外恰有一个传染源，所以整个暴发的平均值必然接近 1），而它们的传染源平均传给了约 8.7 人（[代码](spreading.html#code)）。

### 社交网络传感器：利用朋友悖论提前预警

既然传播先到达枢纽（[度异质性与流行病阈值](spreading.epidemic-threshold.html)中的层级传播），监测枢纽就能提前发现疫情。全网度未知时，可以再用一次朋友悖论：监测“随机个体所提名的朋友”。

::: {.callout-bio}
Christakis 与 Fowler（2010，PLoS ONE）在 2009 年美国一所大学的流感暴发中跟踪 744 名学生，一组随机抽取，另一组是被前者提名的朋友。按临床诊断，朋友组的流行进程比随机组（代表全人群）提前 13.9 天（95% CI 9.9–16.6）；在流行第 16 天朋友组已显著领先，比全人群每日发病高峰早了整整 46 天。这种“社交网络传感器”不需要绘制全网，适合作为哨点监测的补充。
:::

### 院内传播中的追踪与预防

医院是追踪与预防同时进行的典型场景。Lloyd-Smith、Galvani 与 Getz（2003，Proc R Soc B）建立了一个社区与其医院的 SARS 随机模型（重点分析香港和新加坡报告的 $R_0\approx3$ 的情形），发现医院内的接触防护是最有力的措施；当 $R_0=3$ 时，仅靠病例隔离要控制疫情，需要隔离把传播降低至少到四分之一、且从发病到隔离的平均时间少于 3 天；追踪与发现病例拖延几天，就会严重削弱检疫与隔离的作用。

::: {.callout-warn}
追踪的效果还受数据覆盖与隐私约束：数字追踪只记录使用应用的人之间的接触，若使用率为 $c$，一条接触被记录的概率约为 $c^2$。向后追踪需要回溯更长的时间窗口，对记忆或存储的要求更高；隐私保护设计（如去中心化存储）会限制能做的网络分析。评估追踪策略时应同时报告覆盖率、延迟与漏报的敏感性。
:::

## 信息与行为的传播 {#social-contagion}

信息和行为的传播与病原体有一个关键区别：**是否需要多次暴露**。

**独立级联模型**（independent cascade, IC）：节点被激活后，有一次机会以概率 $p_{uv}$ 激活每个未激活的邻居。它是“简单传染”（simple contagion），本质上与离散时间 SIR（感染一步即移除）相同。Kempe、Kleinberg 和 Tardos（2003，KDD）把“选 $k$ 个种子使期望传播范围最大”表述为**影响力最大化**问题，证明它是 NP 难的，但期望传播范围是子模函数，贪心算法至少能达到最优值的 $1-1/e\approx63\%$（详见[影响力最大化与关键传播者](spreading.influential-spreaders.html)）。

**线性阈值模型**（Granovetter 1978 的阈值思想）：节点 $v$ 有阈值 $\theta_v$，当已激活邻居的比例（或加权和）超过 $\theta_v$ 时才被激活。它刻画“复杂传染”（complex contagion）：采纳一种行为需要多个来源的社会强化。Watts（2002，PNAS）证明阈值模型上的全局级联只在中等平均度的窗口内出现：网络太稀疏则连不起来，太稠密则每个邻居的影响被稀释（级联条件的推导见[数学推导与算法](spreading.derivations.html) G 节）。

::: {.callout-def}
**简单传染与复杂传染**：简单传染只需一次有效接触（病原体、多数信息）；复杂传染需要来自多个邻居的强化（采纳新行为、改变健康习惯）。对简单传染，长程“捷径”（[小世界与无标度网络模型](network-models.html)中的小世界重连边）加速传播；对复杂传染，捷径只提供单一来源，作用有限，聚集的局部结构反而更利于传播（Centola 与 Macy 2007，Am J Sociol 称之为“长关系的弱点”）。Centola（2010，Science）的在线实验支持了这一点：健康行为在聚集度高的网络中扩散更多。
:::

**一个可手算的例子**。设阈值 $\theta=1/4$，网络是每个节点连接左右各 3 个最近邻的环（度为 6）。若连续 6 个节点被设为种子，紧挨种子块的节点有 3 个邻居在种子块中，$3/6\ge1/4$，被激活；激活像拉链一样沿环推进，最终覆盖全环。若把所有边随机重连（度仍约为 6），种子块外的节点通常只有 0–1 个种子邻居，$1/6<1/4$，级联在种子附近停住。代码示例“复杂传染”得到：在不重连与少量重连（5%）的格子上阈值模型覆盖全网，完全随机重连后只覆盖约 2%；而同样网络上的独立级联（$p=0.3$）恰好相反，在随机网络上覆盖约 74%，在格子上只有约 2%（[代码](spreading.html#code)）。

**高阶相互作用**。成对的边无法表达“三个朋友同时劝你”这种群体强化。Iacopini 等（2019，Nature Communications）把社会系统表示为单纯复形，允许传染通过不同规模的群体（三角形等）发生，发现高阶相互作用会导致不连续的（爆发式）转变，并出现健康态与流行态共存的双稳区——这为“社会变革需要临界数量”提供了一种机制解释。

**疾病与行为的耦合**。行为本身也在传播，并反过来改变疾病传播。Funk 等（2009，PNAS）建模了“对疾病的知晓”沿社交网络传播并降低易感性，发现知晓的扩散可以减小疫情规模，在一定条件下还能阻止大暴发。

::: {.callout-warn}
观察到网络中某种健康状态成簇，并不等于它在“传染”。同质性（相似的人结交）、共同环境与反向因果都能产生同样的聚集（Shalizi 与 Thomas 2011；见[生物医学应用](spreading.biomedical.html)）。区分简单与复杂传染也需要实验或准实验设计，单凭横断面网络数据通常无法判断。
:::

## 影响力最大化与关键传播者 {#influential-spreaders}

“谁最能促进传播”有两种不同问法：**单个**节点作为种子能传多远（关键传播者识别），以及选**一组** $K$ 个种子使总传播范围最大（影响力最大化）。前者是排序问题，后者是组合优化问题——一组最好的种子不等于单个最好的 $K$ 个节点。

### 单个节点：中心性指标

- **度**：最直观，但两个度相同的节点可能一个在核心、一个在边缘。
- **k-壳（k-核）分解**：反复删除度小于 $k$ 的节点，节点被删除时所处的层次为其核数 $k_s$。Kitsak 等（2010，Nature Physics）在多个真实网络上发现，单个种子的 SIR 传播范围更取决于它所在的 k-壳层，而不是度或介数：位于边缘的枢纽往往传播得并不远。
- **扩散中心性**（diffusion centrality，Banerjee 等 2013 在小额信贷扩散研究中提出）：$DC=\left[\sum_{t=1}^{T}(qA)^t\right]\mathbf 1$，统计在 $T$ 步内、每步以概率 $q$ 传递的信息从该节点出发的期望到达次数。$T=1$ 时退化为度（乘以 $q$）；$T\to\infty$ 且 $q$ 大于 $1/\Lambda_{\max}$ 时其排序趋近特征向量中心性；$q$ 小于 $1/\Lambda_{\max}$ 时与 Katz 中心性相关。它把“传播能走几步”显式放入中心性中。Banerjee 等发现，最初获知小额信贷信息的村民的扩散中心性能预测各村最终的参与率。
- **动力学敏感的指标**：最优的单节点排序依赖传播强度。远低于阈值时只有直接邻居重要（度最好）；接近阈值时传播能走很远，特征向量类指标（或非回溯中心性）更好；远高于阈值时几乎所有种子都能引发大暴发，排序意义下降。

::: {.callout-warn}
“高度节点就是最佳传播者”不总成立。对单种子的 SIR 传播，位于网络核心（高 k-壳）的节点通常优于边缘的高度节点；选**多个**种子时还要考虑种子之间的重叠，单纯取度最高的 $K$ 个节点常常浪费在同一个社团里。
:::

### 一组种子：子模性与贪心算法

记 $\sigma(S)$ 为种子集合 $S$ 的期望传播范围。Kempe、Kleinberg 与 Tardos（2003）证明，在独立级联与线性阈值模型下 $\sigma$ 满足：

- **单调性**：$S\subseteq S'\Rightarrow\sigma(S)\le\sigma(S')$；
- **子模性**（边际收益递减）：对 $S\subseteq S'$ 和任意 $v$，$\sigma(S\cup\{v\})-\sigma(S)\ge\sigma(S'\cup\{v\})-\sigma(S')$。

直观理由：把每条边“通/不通”的随机性预先抽好（活边图），$\sigma(S)$ 就是 $S$ 能到达的节点数的期望，而“集合覆盖”函数天然是子模的。由 Nemhauser–Wolsey–Fisher 定理，每步加入边际增益最大的节点的贪心算法满足 $\sigma(S_{\text{greedy}})\ge(1-1/e)\,\sigma(S^*)$。实际计算中 $\sigma$ 要用蒙特卡洛估计，代价很高；利用子模性的“懒惰评估”（只重算堆顶候选的边际增益，常称 CELF）可以大幅加速。

**集体影响**（collective influence，Morone 与 Makse 2015）从渗流角度处理同一问题：找最少的节点使其删除后巨分支消失（对应免疫），或使其激活后传遍全网（对应影响）。在局部树状近似下，问题化为非回溯矩阵谱半径的最小化，得到启发式指标

$$CI_\ell(i)=(k_i-1)\sum_{j\in\partial\mathrm{Ball}(i,\ell)}(k_j-1),$$

$\partial\mathrm{Ball}(i,\ell)$ 是与 $i$ 距离恰为 $\ell$ 的节点集合。算法每次删除 CI 最大的节点并更新。他们发现最优影响者集合比以往启发式中心性给出的小得多，其中包含许多被忽视的低度节点——它们本身度不高，但被层层枢纽包围。

代码示例“影响力最大化”构造了一个由稠密大社团（枢纽都在其中）和 7 个小社团组成、社团间只有极少桥的网络：按度、k-核或 CI 取前 10 名，种子全部挤在大社团中，期望传播范围（约 590）甚至不如随机选种（约 716）；贪心算法把种子分散到各社团，传播范围约 840（[代码](spreading.html#code)）。

::: {.callout-bio}
**网络靶向的健康干预**。Kim 等（2015，Lancet）在洪都拉斯伦皮拉省 32 个村庄（共 5773 人）开展整群随机对照试验，把净水用氯片或复合维生素先发放给每村 5% 的人，比较三种靶向方式：随机村民、社会联系最多（入度最高）的村民、随机村民所提名的朋友（利用朋友悖论）。复合维生素干预中，提名朋友组的兑换率为 74.3%，随机组 66.2%，入度最高组 61.0%；靶向提名朋友使营养干预的采纳比随机靶向提高 12.2%（95% CI 6.9–17.9），而靶向联系最多的人在两种干预中都没有比随机靶向产生更多采纳。这一方法不需要绘制全网，易于推广。
:::

## 传播溯源 {#source-localization}

前面的问题都是“正向”的：已知源头与网络，预测传播。**传播溯源**（source localization）是反问题：已知网络和部分传播观测，推断源头（零号病人、谣言发起者、污染源）。它在暴发调查、院内感染溯源、食源性疾病追查和虚假信息治理中都有需求。

### 问题设定

观测通常有两种：（1）某一时刻的**感染快照**（谁已感染）；（2）少数**观测点**（传感器节点）被感染的**时刻**。难点在于：同一个快照可以由许多不同源头以不同的传播路径产生，问题本质上是在指数多的传播历史上做推断。

### 主要方法

- **谣言中心性**（Shah 与 Zaman 2011，IEEE Trans Inf Theory）：对树状网络上的 SI 传播，源头的似然正比于“与快照一致的感染顺序”数目。对节点 $v$ 为根的感染子树，这一数目为 $R(v)=n!\prod_{u}\dfrac{1}{T_u^v}$，$T_u^v$ 是以 $v$ 为根时 $u$ 的子树大小；最大化 $R(v)$ 的节点称为谣言中心，对正则树是最大似然估计。一般网络上常用其 BFS 树近似。
- **Jordan 中心与距离中心**：在感染子图中，取到其他感染节点最大距离（或平均距离）最小的节点。简单、稳健，在快照较早时效果不错。
- **基于观测点**（Pinto、Thiran 与 Vetterli 2012，PRL）：若 $s$ 是源头，观测点 $o$ 的感染时刻约为 $t_o\approx t_0+d(s,o)\cdot\bar\tau$，加上沿路径累积的随机延迟；用高斯近似写出到达时刻的似然，选使之最大的候选源。它只需要少量观测点（稀疏观测）。简化版本是选择使 $t_o-d(s,o)$ 方差最小的 $s$。
- **动态消息传递**（Lokhov 等 2014，PRE）：对每个候选源用动态消息传递计算快照的近似概率，在稀疏网络上精度高。
- **有效距离**（Brockmann 与 Helbing 2013）：在流动网络上，以真实源头为中心时到达时间与有效距离的关系最接近线性，据此在候选城市中找源头（见[集合种群与全球传播](spreading.metapopulation.html)）。

### 观测点的选择

在基于观测点的方法中，**放在哪里**和**放多少**决定了能否定位。直觉上应选中心节点，但中心节点之间路径高度重叠、信息冗余。Zhang 等（2016，Physica A）研究了如何在复杂网络中识别高效的观测点以定位传播源；这一问题与[网络可控性与稳定性](controllability.html)中的“最少观测节点”有相似的组合结构，但目标不同：前者要区分传播源，后者要重构系统状态。代码示例“传播溯源”中，介数最高的 5% 节点作为观测点（平均误差约 1.3 跳）反而不如随机选取的观测点（约 1.1 跳），而早期快照上的 Jordan 中心命中率约 73%（[代码](spreading.html#code)）。

::: {.callout-warn}
溯源算法的评估通常假设网络完整已知、传播模型正确（多为 SI、离散时间）、观测无误差。现实中接触网络不完整、存在多个源头与多次输入、报告时间有延迟，准确率会显著下降。应用于暴发调查时，网络溯源只能缩小候选范围，最终需要与流行病学调查和病原体基因组测序（系统发育重建传播链）相互印证。
:::


## 数学推导与算法 {#derivations}

本页补全前面各页用到的结果：A. SIS 阈值 $\lambda_c=\langle k\rangle/\langle k^2\rangle$ 的推导；B. SIR 最终规模与键渗流的对应；C. 精确的随机模拟算法；D. 活动驱动时间网络上的阈值；E. 淬火平均场与非回溯矩阵阈值；F. 目标免疫所需的接种比例；G. 阈值模型的全局级联条件。记号：$P(k)$ 为度分布，$\langle k^n\rangle=\sum_k k^nP(k)$，$\beta$ 为每条 S–I 边上的传播速率，$\mu$ 为恢复速率，$\lambda=\beta/\mu$。

### A. SIS 的异质平均场阈值

**假设**（近似在这里进入）：（1）网络是无度相关的配置模型，$N\to\infty$；（2）同一度类的节点在统计上等价，只用 $i_k$ 描述（“退火”近似：相当于每一时刻重新随机连边）；（3）忽略邻居状态之间的相关性。

**第 1 步：$\Theta$ 的含义。** 从任一节点出发沿一条随机边走，到达度为 $k'$ 的节点的概率与它拥有的“边端”数成正比，为 $k'P(k')/\langle k\rangle$。因此该邻居处于感染态的概率为
$$
\Theta=\frac{1}{\langle k\rangle}\sum_{k'}k'P(k')\,i_{k'} .
$$

**第 2 步：稳态。** 令 HMF 方程 $\dfrac{di_k}{dt}=\beta k(1-i_k)\Theta-\mu i_k$ 等于零，两边除以 $\mu$：
$$
i_k=\frac{\lambda k\Theta}{1+\lambda k\Theta}.
$$

**第 3 步：自洽方程。** 把 $i_k$ 代回 $\Theta$ 的定义：
$$
\Theta=F(\Theta)\equiv\frac{1}{\langle k\rangle}\sum_k kP(k)\,\frac{\lambda k\Theta}{1+\lambda k\Theta}.
$$
$\Theta=0$ 总是解（无病态）。$F$ 满足 $F(0)=0$、$F(1)<1$，且 $F''(\Theta)<0$（每一项都是 $\Theta$ 的凹函数）。因此非零解存在，当且仅当 $F$ 在原点的斜率大于 1：
$$
F'(0)=\frac{\lambda}{\langle k\rangle}\sum_k k^2P(k)=\lambda\frac{\langle k^2\rangle}{\langle k\rangle}>1
\quad\Longleftrightarrow\quad
\lambda>\lambda_c=\frac{\langle k\rangle}{\langle k^2\rangle}.
$$

**第 4 步：为什么 $\gamma\le3$ 时阈值消失。** 取 $P(k)=Ck^{-\gamma}$，$k_{\min}\le k\le k_{\max}$，用连续近似：
$$
\langle k^2\rangle\approx C\int_{k_{\min}}^{k_{\max}}k^{2-\gamma}\,dk=
\begin{cases}
\dfrac{C\,(k_{\max}^{3-\gamma}-k_{\min}^{3-\gamma})}{3-\gamma}, & \gamma\ne3,\\[2mm]
C\ln(k_{\max}/k_{\min}), & \gamma=3 .
\end{cases}
$$
$2<\gamma<3$ 时指数 $3-\gamma>0$，$\langle k^2\rangle$ 随 $k_{\max}$ 发散；$\gamma=3$ 时对数发散；$\gamma>3$ 时收敛到有限值。配置模型中“自然截断”$k_{\max}\sim k_{\min}N^{1/(\gamma-1)}$，代入得 $2<\gamma<3$ 时 $\lambda_c\sim N^{-(3-\gamma)/(\gamma-1)}$，$\gamma=3$ 时 $\lambda_c\sim1/\ln N$。阈值随 $N$ 增大而趋于零，但下降很慢——这就是“有限网络阈值小而非零”的定量含义。

**第 5 步：早期增长（SI 的特征时间）。** 对 SI（$\mu=0$）在 $i_k\ll1$ 时线性化，并注意一个被感染节点已经用掉一条边（感染它的那条），定义 $\Theta=\sum_k(k-1)P(k)i_k/\langle k\rangle$，则 $d\Theta/dt=\beta\,\dfrac{\langle k^2\rangle-\langle k\rangle}{\langle k\rangle}\,\Theta$，得到[度异质性与流行病阈值](spreading.epidemic-threshold.html)表中的 $\tau=\langle k\rangle/[\beta(\langle k^2\rangle-\langle k\rangle)]$。SIS 与 SIR 的特征时间按同样方式加入恢复项得到。

::: {.callout-warn}
上面是退火（annealed）近似。在固定网络（淬火，quenched）上，SIS 的行为更微妙：Castellano 与 Pastor-Satorras（2010，*PRL*）指出，即使 $\gamma>3$，孤立的枢纽及其邻居也能自我维持感染，阈值同样随 $N$ 趋于零。因此“$\gamma>3$ 时有有限阈值”只对 HMF 成立；SIR 没有这种再感染机制，结论较稳健。
:::

### B. SIR 最终规模与键渗流

**第 1 步：传播性。** 设感染者 $i$ 的感染期为 $\tau$，在此期间沿每条边以速率 $\beta$ 传播。邻居 $j$ 最终被 $i$ 传染（假设 $j$ 尚未被别人传染）的概率为 $T=1-e^{-\beta\tau}$。若感染期服从速率为 $\mu$ 的指数分布，对 $\tau$ 求平均得 $T=\int_0^\infty\mu e^{-\mu\tau}(1-e^{-\beta\tau})d\tau=\dfrac{\beta}{\beta+\mu}$。

**第 2 步：映射。** 若 $\tau$ 对所有人相同，每条边是否“传得过去”是独立的伯努利事件，概率为 $T$。于是“最终被感染的集合”恰好等于“以概率 $T$ 保留每条边后、包含初始感染者的连通分支”——这就是**键渗流**（bond percolation）。若 $\tau$ 因人而异，同一感染者的各条出边不再独立（它们共享同一个 $\tau$），映射只是部分成立（Kenah 与 Robins 2007，*Physical Review E*）：在树状近似下，用平均传播性 $T$ 算出的大爆发规模仍然正确，但发生大爆发的概率不再等于这一规模，一般会更小。

**第 3 步：生成函数求解。** 记 $G_0(x)=\sum_kP(k)x^k$，$G_1(x)=G_0'(x)/G_0'(1)$（沿边到达节点的“剩余度”生成函数）。令 $v$ 为“沿一条边出发、不能通向大爆发”的概率：这条边要么没传过去（概率 $1-T$），要么传过去了但对方的其余边都不通向大爆发（概率 $T\,G_1(v)$）：
$$
v=1-T+T\,G_1(v),\qquad R_\infty=1-G_0(v).
$$
$R_\infty$ 是大爆发中最终被感染（移除）的比例，适用于初始感染者占比趋于零的极限。

**第 4 步：阈值。** $v=1$ 总是解。与 A 中同理，存在 $v<1$ 的解当且仅当 $T\,G_1'(1)>1$，而 $G_1'(1)=\dfrac{\langle k^2\rangle-\langle k\rangle}{\langle k\rangle}$，故
$$
T_c=\frac{\langle k\rangle}{\langle k^2\rangle-\langle k\rangle},
$$
这就是[度异质性与流行病阈值](spreading.epidemic-threshold.html)中的 $\lambda_c^{\text{SIR}}$（那里的 $\lambda$ 应理解为传播性 $T$）。

**检验**：泊松网络 $G_0(x)=G_1(x)=e^{\langle k\rangle(x-1)}$。由 $R_\infty=1-G_0(v)$ 得 $G_1(v)=1-R_\infty$，代入 $v$ 的方程得 $v=1-TR_\infty$，于是
$$
R_\infty=1-e^{-\langle k\rangle T R_\infty},
$$
正是均匀混合下的经典最终规模方程，其中 $R_0=\langle k\rangle T$。

**与消息传递、EBCM 的关系**：把第 3 步中“对所有边相同的 $v$”换成每条有向边各自的 $u_{i\leftarrow j}$，就得到[配对近似、边基模型与消息传递](spreading.message-passing.html)中的消息传递方程；EBCM 中 $\theta(t\to\infty)$ 满足的方程在指数感染期下与第 3 步等价。

### C. 精确随机模拟：Gillespie 算法

微分方程描述的是期望值；有限网络上的随机涨落（例如疫情早期灭绝）需要随机模拟。对指数分布的传播和恢复时间，Gillespie 算法给出与连续时间马尔可夫过程分布完全一致的轨迹。

```text
算法  网络 SIR 的 Gillespie 模拟
输入：网络 G、β、μ、初始感染集 I0
维护：状态 x_i∈{S,I,R}；对每个 i∈I 记 s_i = i 的易感邻居数；N_SI = Σ_{i∈I} s_i
1. t ← 0；按 I0 初始化 x、s、N_SI
2. while I 非空:
3.     Λ ← μ|I| + β·N_SI                     # 总事件速率
4.     抽 r1, r2 ~ U(0,1)；t ← t − ln(r1)/Λ    # 等待时间 ~ Exp(Λ)
5.     if r2·Λ < μ|I|:                          # 恢复事件
6.         从 I 中均匀抽 i；x_i ← R；N_SI ← N_SI − s_i；从 I 删除 i
7.     else:                                    # 感染事件
8.         以 s_i 为权重从 I 中抽 i；在 i 的易感邻居中均匀抽 j
9.         x_j ← I；s_j ← 0
10.        for j 的每个邻居 l:
11.            if x_l = I: s_l ← s_l − 1；N_SI ← N_SI − 1
12.            if x_l = S: s_j ← s_j + 1；N_SI ← N_SI + 1
13.        把 j 加入 I
14.    记录 (t, |S|, |I|, |R|)
```

复杂度：SIR 中每个节点至多被感染一次、恢复一次，事件总数 $\le 2N$；第 10–12 步对每个被感染节点只遍历一次邻居，合计 $O(m)$；第 8 步按权重抽样若用二叉求和树实现为 $O(\log N)$，总计 $O(m+N\log N)$。若改为 SIS（第 6 步令 $x_i\leftarrow S$ 并更新其邻居的 $s$），事件数不再有界，需设定最长模拟时间。离散时间近似（每步 $\Delta t$ 内以 $1-e^{-\beta\Delta t}$ 传播、$1-e^{-\mu\Delta t}$ 恢复）实现更简单，但有 $O(\Delta t)$ 的离散化误差。

**事件驱动的等价算法**。对 SIR 还有一种更简单的精确方法（Kiss、Miller 与 Simon 2017 书中称为快速 SIR 算法）：节点 $v$ 在时刻 $t$ 被感染时，抽取恢复时刻 $t+\mathrm{Exp}(\mu)$，并为每个邻居抽取传播时刻 $t+\mathrm{Exp}(\beta)$；只有早于恢复时刻的传播事件进入优先队列。按时间顺序处理队列，跳过已非易感的目标。代码示例“边基仓室模型与精确随机模拟的比较”使用的就是这一算法。把 $\mathrm{Exp}$ 换成其他分布，就能模拟非马尔可夫的感染期（例如固定感染期）。

### D. 活动驱动网络上的 SIS 阈值

设活动潜能密度为 $F(a)$，每步活跃节点向 $m$ 个随机节点发出接触，接触持续一步；每次 S–I 接触传播概率为 $\lambda$，感染者每步恢复概率为 $\mu$。记 $I_a$ 为活动性为 $a$ 的类中的感染人数，$N_a=NF(a)$。易感者有两种被感染方式：自己激活并连到感染者（概率 $\approx am\lambda I/N$），或被激活的感染者连到（概率 $\approx m\lambda\int a'I_{a'}da'/N$）。于是
$$
I_a^{t+1}-I_a^{t}=-\mu I_a+\lambda m(N_a-I_a)\,a\frac{I}{N}+\lambda m(N_a-I_a)\frac{\int a'I_{a'}\,da'}{N}.
$$
在无病态附近令 $N_a-I_a\approx N_a$，对 $a$ 积分得 $I=\int I_a\,da$ 与 $\Phi=\int aI_a\,da$ 的线性系统：
$$
\begin{pmatrix}\Delta I\\ \Delta\Phi\end{pmatrix}=
\begin{pmatrix}\lambda m\langle a\rangle-\mu & \lambda m\\ \lambda m\langle a^2\rangle & \lambda m\langle a\rangle-\mu\end{pmatrix}
\begin{pmatrix}I\\ \Phi\end{pmatrix}.
$$
矩阵的最大特征值为 $\lambda m(\langle a\rangle+\sqrt{\langle a^2\rangle})-\mu$，它大于 0 即为流行条件：
$$
\frac{\lambda}{\mu}>\frac{1}{m\big(\langle a\rangle+\sqrt{\langle a^2\rangle}\big)}.
$$
若所有人活动性相同（$\langle a^2\rangle=\langle a\rangle^2$），阈值为 $1/(2m\langle a\rangle)$；活动异质性越大，阈值越低。代码示例中，20% 高活跃个体（$a=0.5$）与 80% 低活跃个体（$a=0.05$）的混合使阈值从“同质”估计的 0.354 降到 0.270，模拟的稳态流行率在 0.9 倍理论阈值时为 0、1.2 倍时约为 0.11，转变位置与异质理论一致（[代码](spreading.html#code)）。

### E. 淬火平均场与非回溯矩阵阈值

**QMF**：在 $\rho_i=0$ 处线性化个体平均场方程 $\dot\rho_i=-\mu\rho_i+\beta(1-\rho_i)\sum_jA_{ij}\rho_j$，得 $\dot\rho=(\beta A-\mu I)\rho$。$A$ 是对称非负矩阵，最大特征值 $\Lambda_{\max}$ 对应非负特征向量（Perron–Frobenius），故 $\rho$ 沿该方向增长的条件是 $\beta\Lambda_{\max}>\mu$，即 $\lambda_c=1/\Lambda_{\max}$。由 Rayleigh 商，$\Lambda_{\max}\ge\sqrt{k_{\max}}$（取以最大度节点为中心的星形试探向量）且 $\Lambda_{\max}\ge\langle k\rangle$。

**非回溯矩阵**：消息传递方程在 $u\equiv1$ 附近线性化。令 $u_{i\leftarrow j}=1-\delta_{j\to i}$，保留一阶项得 $\delta_{j\to i}=T\sum_{l\in\partial j\setminus i}\delta_{l\to j}$，即 $\delta=TB\delta$。非零解出现的条件是 $T\rho(B)>1$。

**Ihara–Bass 化简**：设 $v$ 是 $B$ 的特征向量，特征值为 $\nu\ne0$。由 $B$ 的定义，$\nu v_{j\to i}=\sum_{l\in\partial j}v_{l\to j}-v_{i\to j}$。定义两个节点量：流入之和 $x_j=\sum_{l\in\partial j}v_{l\to j}$，流出之和 $y_j=\sum_{i\in\partial j}v_{j\to i}$。

- 对 $i\in\partial j$ 求和：$\nu y_j=k_jx_j-x_j$，即 $\nu y=(D-I)x$；
- 对固定的 $i$、$j\in\partial i$ 求和：$\nu x_i=\sum_{j\in\partial i}x_j-y_i$，即 $\nu x=Ax-y$。

消去 $y$ 得 $\big(\nu^2I-\nu A+(D-I)\big)x=0$，等价于
$$
\begin{pmatrix}A & I-D\\ I & 0\end{pmatrix}\begin{pmatrix}x\\ x/\nu\end{pmatrix}=\nu\begin{pmatrix}x\\ x/\nu\end{pmatrix}.
$$
因此 $\rho(B)$ 可以从这个 $2N\times2N$ 稀疏矩阵的最大特征值求得，计算量与 $A$ 同阶。

### F. 目标免疫所需的接种比例

取连续近似 $P(k)=(\gamma-1)k_{\min}^{\gamma-1}k^{-\gamma}$（$k\ge k_{\min}$，$2<\gamma<3$），接种度最高的比例 $g$ 的节点，等价于把度分布在 $k_c$ 处截断：
$$
g=\int_{k_c}^{\infty}P(k)\,dk=\Big(\frac{k_{\min}}{k_c}\Big)^{\gamma-1}\ \Longrightarrow\ k_c=k_{\min}\,g^{-1/(\gamma-1)}.
$$
忽略“删去枢纽也削减了其邻居的度”这一效应（它会使结果更有利），剩余网络中 $\langle k\rangle\approx k_{\min}\frac{\gamma-1}{\gamma-2}$，$\langle k^2\rangle\approx\frac{\gamma-1}{3-\gamma}k_{\min}^{\gamma-1}k_c^{3-\gamma}$，于是 HMF 阈值
$$
\lambda_c(g)=\frac{\langle k\rangle}{\langle k^2\rangle}=\frac{3-\gamma}{(\gamma-2)\,k_{\min}}\;g^{(3-\gamma)/(\gamma-1)} .
$$
令 $\lambda_c(g_c)=\lambda$ 解出
$$
g_c=\Big[\frac{(\gamma-2)\,k_{\min}\,\lambda}{3-\gamma}\Big]^{(\gamma-1)/(3-\gamma)} .
$$
**算例**：$\gamma=2.5$、$k_{\min}=2$，则 $\lambda_c(g)=0.5\,g^{1/3}$；若 $\lambda=0.1$，$g_c=0.2^3=0.008$，即只需接种度最高的约 0.8% 的人。随机免疫则要求 $\lambda(1-g)<\lambda_c(N)$，而 $\lambda_c(N)\to0$，需要几乎全员接种。这一对比与[网络鲁棒性、渗流与级联失效](robustness.html)中“随机失效鲁棒、蓄意攻击脆弱”是同一现象的两面。

### G. 阈值模型的全局级联条件

Watts（2002）考虑配置模型上的阈值模型：节点阈值 $\phi$ 服从分布 $f(\phi)$，节点在已激活邻居比例 $\ge\phi$ 时激活。关键概念是**易感节点**（vulnerable node）：只要一个邻居激活就会激活的节点，即 $\phi\le1/k$。度为 $k$ 的节点易感的概率为 $\rho_k=\Pr(\phi\le1/k)$。

一个小种子能触发全局级联，当且仅当易感节点构成的子网络存在“渗流”的巨分支。沿一条边到达一个度为 $k$ 的节点的概率为 $kP(k)/\langle k\rangle$，该节点易感的概率为 $\rho_k$，易感时它会把激活继续传给其余 $k-1$ 个邻居。分支过程的平均分支数大于 1，得到级联条件
$$
\sum_k k(k-1)\,\rho_k\,P(k)>\langle k\rangle .
$$
**算例**：所有节点阈值 $\phi=0.18$，则只有 $k\le5$ 的节点易感。对平均度为 $z$ 的泊松网络，条件化为 $z\cdot\Pr(\mathrm{Poisson}(z)\le3)>1$，数值求解得级联窗口约为 $1.02<z<5.76$。$z$ 太小，网络本身不连通；$z$ 太大，几乎没有节点易感（单个邻居的影响 $1/k$ 太小）。窗口上边界附近的级联罕见但一旦发生就覆盖几乎全网，这是“全局级联”难以预测的原因。

## 研究前沿与开放问题 {#frontiers}

1. **真实网络上的阈值到底由什么决定？** HMF 给出 $\langle k\rangle/\langle k^2\rangle$，淬火平均场给出 $1/\Lambda_{\max}$，消息传递给出 $1/\rho(B)$，三者在度分布相同的网络上可能相差很大。Castellano 与 Pastor-Satorras（2010，*PRL*）指出 SIS 在 $\gamma>3$ 时阈值同样会消失，引发了一系列关于“局域化”与真实阈值的讨论。对于含聚集、社团、度相关的接触网络，哪一种近似更可靠仍无统一答案。

2. **个体异质性与超级传播。** Lloyd-Smith 等（2005，*Nature*）用 SARS 等数据说明个体再生数高度离散，少数人造成大部分传播。超级传播来自接触网络中的枢纽、生物学上的高排毒量，还是环境与行为？这对靶向干预（见[免疫策略](spreading.immunization.html)、[接触追踪与监测](spreading.contact-tracing.html)）的设计至关重要，在 COVID-19 研究中仍有争论。

3. **高阶相互作用与复杂传染。** Iacopini 等（2019，*Nature Communications*）在单纯复形上构建传播模型，发现群体（三人及以上）相互作用可以导致不连续的爆发式转变和双稳态。健康行为（戒烟、疫苗接受度）是否需要用高阶网络而非成对网络描述，缺乏实证检验。

4. **疾病与行为的耦合。** Funk 等（2009，*PNAS*）建模了“对疾病的知晓”沿社交网络传播并降低易感性，发现知晓的扩散可以减小疫情规模，在一定条件下还能阻止大爆发。信息、恐慌、错误信息与病原体的共同演化如何量化、如何用于公共卫生沟通，仍是活跃方向。

5. **时间网络上的理论与数据。** 可穿戴传感器和手机数据提供了高分辨率时间网络，但时间网络上的阈值、最优免疫与追踪理论远不如静态网络成熟（Holme 与 Saramäki 2012；Valdano 等 2015）。如何从短期测量外推长期接触模式、如何在保护隐私的前提下使用流动数据，都是开放问题。

6. **网络推断与传播推断的结合。** 现实中接触网络本身是部分观测的，传播链又只能从病例与基因组数据间接推断。同时推断网络与传播（例如结合病原体系统发育与接触数据）、在网络不确定时给出溯源与 $R_t$ 的可信区间，是方法学前沿。

## 生物医学应用 {#biomedical}

**传染病控制**。网络流行病学的理论直接影响了公共卫生策略：针对高接触人群（如性传播疾病的核心人群）的干预、以接触追踪为基础的隔离，以及在疫苗短缺时优先接种高接触职业人群，都可以从 $\langle k^2\rangle$ 主导阈值的结果中找到依据。COVID-19 流行期间，“超级传播事件”（少数感染者造成大量继发感染）的观察也与个体传播能力高度异质这一网络观点相符。

**COVID-19：网络方法的集中检验**。这一次大流行几乎检验了本专题的每一部分：全球集合种群模型评估旅行限制（Chinazzi 等 2020，见[集合种群与全球传播](spreading.metapopulation.html)）；手机流动网络解释城市内的超级传播地点与感染不平等（Chang 等 2021）；接触追踪数据估计超级传播程度（Adam 等 2020，见[再生数与超级传播](spreading.reproduction-number.html)）；数字接触追踪的可行性分析（Ferretti 等 2020）与向后追踪理论（Kojaku 等 2021，见[接触追踪与监测](spreading.contact-tracing.html)）。也暴露了局限：行为随疫情快速变化，参数不可迁移，长期预测普遍失准。

**医院感染与医疗网络**。院内感染在两个尺度上是网络问题：

- **病区内**：医护–患者接触网络高度异质，少数岗位承担大部分接触（Vanhems 等 2013，见[接触网络](spreading.contact-networks.html)）；Lloyd-Smith 等（2003）的模型显示，医院内的接触防护是控制 SARS 最有力的措施。
- **医院之间**：患者转诊与再入院把医院连成网络。Donker、Wallinga 与 Grundmann（2010，PLoS Comput Biol）用 2004 年荷兰医疗登记数据重建全国医院网络，发现大学医院与其他医院共享的患者更多，因而更可能最早收到定植患者；由于网络的方向性指向大学医院，即使各医院感染控制同样有效，大学医院的 MRSA 流行率也更高。他们据此指出，用医院的 MRSA 率作为卫生质量指标进行比较时，必须考虑医院在网络中的位置。

**健康行为的社会传播**。Christakis 与 Fowler（2007，New England Journal of Medicine）分析弗雷明汉心脏研究中 12 067 人 1971–2003 年的社会关系与体重数据，报告肥胖在社会网络中聚集，关联可达三度分隔；在他们的模型中，朋友变得肥胖时个体肥胖风险升高约 57%，兄弟姐妹约 40%，配偶约 37%，邻居没有显著影响。作者认为传播机制是社会规范的改变而非共同环境。这项研究影响很大，但也受到方法学质疑：Cohen-Cole 与 Fletcher（2008，BMJ）用同样的方法在痤疮、身高、头痛上也“发现”了“传播”；Shalizi 与 Thomas（2011）从理论上证明，在观察性网络数据中，同质性（homophily，相似的人倾向于结交）与真正的传染效应一般无法区分。随机化的网络靶向试验（Kim 等 2015，见[影响力最大化与关键传播者](spreading.influential-spreaders.html)）提供了更强的证据。

::: {.callout-bio}
读“社会传染”类研究时，至少要问三个问题：关系是否可能因相似性而形成（同质性）？是否存在共同暴露（同一社区、同一食堂）？时间顺序和反向因果是否被排除？随机化实验（如 Centola 2010；Kim 等 2015）或自然实验能提供更强的证据。
:::

**医学信息与创新扩散**。医生之间的咨询与转诊网络会影响新药处方、新技术采纳的速度；这类研究通常用阈值或级联模型解释“早期采纳者 → 早期多数 → 晚期多数”的扩散曲线（Rogers 的创新扩散理论）。经典研究是 Coleman、Katz 与 Menzel（1957，Sociometry）对美国中西部城市医生采用一种新药的追踪：在同行网络中联系更紧密的医生更早采用。Iyengar、Van den Bulte 与 Valente（2011，Marketing Science）在新药处方数据上检验了医生之间的意见领袖效应与社会传染。药物安全信息（如不良反应警示、说明书更新）在医生与药师网络中的扩散可以用同样的级联与阈值模型分析，但直接以网络结构为自变量的实证研究仍然很少，是值得开展的方向；设计时同样要处理同质性与共同暴露（例如同一医院的统一培训）的混杂。

**脑网络上的“传播”**。神经退行性疾病中的错误折叠蛋白（如 tau、β-淀粉样蛋白）被认为可能以类朊蛋白方式沿神经通路扩散。Raj、Kuceyeski 与 Weiner（2012，Neuron）在由弥散 MRI 纤维追踪得到的结构连接网络上建立扩散模型 $dx/dt=-\beta Lx$（$L$ 为图拉普拉斯矩阵），其慢衰减的“持久模态”（小特征值对应的特征向量）重现了已知的痴呆萎缩模式，并与阿尔茨海默病和额颞叶痴呆患者的 MRI 体积测量相符。这是传播模型从流行病学走向[脑连接组](brain-connectome.html)的例子；它是线性扩散而非 SIR 型传染，二者的区别在于是否有“全或无”的状态转变与阈值。

## 适用范围与常见误用 {#limitations}

1. **误用**：把 $R_0$ 当作病原体的生物学常数。→ **正解**：$R_0$ 取决于传播概率、接触结构与感染持续时间；在网络上起作用的是邻居的平均剩余度 $(\langle k^2\rangle-\langle k\rangle)/\langle k\rangle$，而非平均度。
2. **误用**：认为无标度网络中任何疾病都必然大流行。→ **正解**：$\lambda_c\to0$ 是无穷大网络的渐近结论；有限网络阈值很小但非零，低于阈值附近的流行规模也可能非常小。而且并非所有接触网络都是重尾的（例如校园近距离接触网络）。
3. **误用**：认为随机接种足够多的人总能控制疫情，比例与网络结构无关。→ **正解**：$g_c=1-\lambda_c/\lambda$ 依赖于 $\lambda_c$；在高度异质的网络中随机接种效率极低，应利用结构信息（目标免疫或熟人免疫）。
4. **误用**：把度最高的节点直接当作最有影响力的传播者，或把单节点排名前 $K$ 的节点当作最好的 $K$ 个种子。→ **正解**：k-壳位置、扩散中心性、种子间重叠都会影响结果；复杂传染下，聚集的局部结构可能比枢纽更关键；选一组种子应使用贪心等考虑重叠的方法。
5. **误用**：观察到网络中某种健康状态聚集，就推断它在“传染”。→ **正解**：同质性和共同环境也能产生聚集，观察性数据难以区分，需要实验或更强的因果设计。
6. **误用**：把一段时间内的接触累积成静态网络后直接套用静态理论。→ **正解**：累积网络会制造不存在的时间相容路径并高估同时存在的接触，阈值与传播速度都会有偏；应在时间网络上模拟，或至少检验聚合窗口的敏感性。
7. **误用**：用首发病例的平均继发病例数或早期增长率直接作为 $R_0$，而不说明代际间隔假设。→ **正解**：网络上“第一代”与“稳定代”的再生数不同；从增长率换算 $R$ 依赖代际间隔分布的完整形状，应报告所用分布并做敏感性分析。
8. **误用**：只报告平均最终规模，不区分“小暴发”与“大暴发”。→ **正解**：在阈值附近，单次模拟的最终规模呈双峰分布（早期灭绝或大暴发），平均值没有代表性；应分别报告大暴发概率与条件规模。

此外，HMF 的阈值公式依赖无度相关、局部树状、$N\to\infty$ 等假设（见[数学推导与算法](spreading.derivations.html)）；在含聚集、社团、度相关的真实接触网络上使用时，应同时报告淬火平均场或消息传递估计，或直接做随机模拟。

::: {.callout-warn}
**报告网络传播模型时的最低清单**：网络的来源与构建方式（静态还是时间网络、边的定义、观测窗口）；传播模型与参数的来源（文献值还是拟合值）；初始条件（种子数目与选择方式）；模拟次数与随机种子；是否区分大暴发；关键结论对网络缺失、参数与模型选择（SIR/SEIR、马尔可夫/固定感染期）的敏感性。可复现计算的一般要求见[研究问题、可复现分析与敏感性分析](reproducible-research.html)。
:::


## 关联知识 {#related}

- [网络结构指标与随机图](network-metrics.html)：度分布、二阶矩 $\langle k^2\rangle$、巨连通分支与 ER 随机图，是流行阈值公式与最终规模方程的输入。
- [小世界与无标度网络模型](network-models.html)：无标度网络使 $\langle k^2\rangle$ 发散、阈值消失；小世界捷径加速简单传染、却未必帮助复杂传染。
- [网络鲁棒性、渗流与级联失效](robustness.html)：SIR 最终规模与键渗流等价，免疫与蓄意攻击同为删点渗流，Watts 阈值级联也是级联失效模型。
- [同步与协同动力学](synchronization.html)：网络 Kuramoto 模型的临界耦合 $K_c\propto\langle k\rangle/\langle k^2\rangle$，与传播阈值形式相同。
- [社团结构与社区发现](community-structure.html)：社团结构减缓并截留传播，影响免疫与种子选择；非回溯矩阵同样用于社团发现。
- [度相关性与网络结构的高阶统计](degree-correlations.html)：同配与异配改变阈值；单纯复形等高阶结构对应复杂传染。
- [网络构建与统计验证](network-construction.html)：从接触记录、传感器与流动数据构建静态或时间接触网络，是传播分析的前提。
- [网络可控性与稳定性](controllability.html)：传播溯源中的观测点选择与可观测性中的最少观测节点问题结构相似；[脑连接组](brain-connectome.html)上的网络扩散模型则是传播思想在神经退行性疾病中的应用。

## 核心文献 {#references}

### Pastor-Satorras 与 Vespignani 2001：Epidemic spreading in scale-free networks

- **背景**：经典流行病学基于均匀混合，存在有限的流行病阈值。20 世纪 90 年代末发现互联网等网络具有无标度度分布，而计算机病毒长期低水平流行的现象难以用经典理论解释。
- **核心发现**：用异质平均场方法分析 SIS 模型，得到 $\lambda_c=\langle k\rangle/\langle k^2\rangle$；对 $\gamma\le3$ 的无标度网络，$N\to\infty$ 时阈值消失，稳态流行率在 $\lambda$ 很小时以指数形式趋近于 0。
- **阅读要点**：区分“阈值为 0”和“流行规模大”——在阈值附近流行率可以极小。注意 HMF 忽略了度相关性与动态相关，后来的工作（淬火平均场、消息传递方法）修正了部分结论。
- **延伸思考**：如果网络存在强的度–度同配性（高度节点相互连接），你预计阈值会升高还是降低？为什么？

DOI：[10.1103/PhysRevLett.86.3200](https://doi.org/10.1103/PhysRevLett.86.3200)；精读：[Pastor-Satorras 2001](paper-pastorsatorras2001_epidemic.html)

### Christakis 与 Fowler 2007：The spread of obesity in a large social network over 32 years

- **背景**：慢性病一般被视为个体风险因素的结果。作者借助弗雷明汉心脏研究中记录的亲友关系，构建 12 067 人的纵向社会网络。
- **核心发现**：肥胖在网络中成簇出现，关联延伸到三度分隔；朋友、兄弟姐妹、配偶变胖与个体变胖风险升高相关，邻居无显著关联，同性关系的关联更强，地理距离不影响关联强度。
- **阅读要点**：这是观察性研究，识别“传染”依赖模型假设。对照阅读 Cohen-Cole 与 Fletcher（2008）及 Shalizi 与 Thomas（2011）的批评，思考同质性、共同环境与反向因果。可结合原文图 1 的网络可视化阅读。
- **延伸思考**：如果要在一所大学用随机化设计检验“运动习惯会在宿舍网络中传播”，应怎样设计干预和对照？

DOI：[10.1056/NEJMsa066082](https://doi.org/10.1056/NEJMsa066082)

### Cohen、Havlin 与 ben-Avraham 2003：Efficient immunization strategies for computer networks and populations

- **背景**：目标免疫需要知道每个人的度，现实中难以获得。
- **核心发现**：随机选人、再接种其随机熟人的策略，只需局部信息，接种比例远低于随机免疫就能使网络失去巨连通分支，效果接近目标免疫。
- **阅读要点**：分析基于渗流理论（删点后巨分支是否存在），与 SIR 的最终规模问题等价；理解为什么“沿边采样”天然偏向高度节点。
- **延伸思考**：在医院感染控制中，“熟人”可以对应什么？能否设计一个基于排班表的“熟人免疫”方案？

DOI：[10.1103/PhysRevLett.91.247901](https://doi.org/10.1103/PhysRevLett.91.247901)；精读：[Cohen 2003](paper-cohen2003_immunization.html)

### Lloyd-Smith 等 2005：Superspreading and the effect of individual variation on disease emergence

- **背景**：$R_0$ 是平均数。SARS 期间出现了多起“超级传播事件”，但对非性接触传播的疾病，个体传染性差异难以直接测量，其对暴发动力学的影响并不清楚。
- **核心发现**：利用 8 种直接传播疾病的接触追踪数据，发现个体再生数的分布常常高度偏斜；考虑这种异质性后，疾病更容易灭绝，暴发更罕见但更具爆炸性；针对个体的控制措施优于全人群均匀措施。作者还给出了超级传播事件的严格定义及其频率的预测方法。
- **阅读要点**：理解负二项后代分布与离散参数 $k$；把分支过程的灭绝概率 $q=g(q)$ 与[再生数与超级传播](spreading.reproduction-number.html)中的算例对照。
- **延伸思考**：度异质的接触网络会产生怎样的离散参数？网络之外还有哪些因素会使 $k$ 变小？

DOI：[10.1038/nature04153](https://doi.org/10.1038/nature04153)

### Brockmann 与 Helbing 2013：The hidden geometry of complex, network-driven contagion phenomena

- **背景**：全球流行的时空图案在地理地图上看起来杂乱无章，难以直观理解与预测。
- **核心发现**：用由航空流量定义的有效距离 $d_{mn}=1-\ln P_{mn}$ 替代地理距离，复杂图案化为从源头出发的近似匀速波；有效距离能可靠地预测到达时间，即使流行病学参数未知也能给出相对到达时间，并能识别传播的空间源头。方法在 2009 年 H1N1 与 2003 年 SARS 数据上得到验证。
- **阅读要点**：理解为什么 $-\ln P$ 是“概率意义上的距离”（多段路径的概率相乘，对数相加）；对照[集合种群与全球传播](spreading.metapopulation.html)的代码示例。
- **延伸思考**：在一个城市内部的医院转诊网络上，可以怎样定义有效距离，用于预测耐药菌在医院间的到达顺序？

DOI：[10.1126/science.1245200](https://doi.org/10.1126/science.1245200)

### Kempe、Kleinberg 与 Tardos 2003：Maximizing the spread of influence through a social network

- **背景**：病毒营销与公共卫生推广都要回答“先说服哪几个人”。此前多为启发式（选度最高者）。
- **核心发现**：在独立级联与线性阈值模型下，影响力最大化是 NP 难的；但期望传播范围是单调子模函数，贪心算法有 $1-1/e$ 的近似保证，且在实验中优于度与中心性启发式。
- **阅读要点**：掌握“活边图”论证子模性的技巧；理解为什么一组最好的种子不是单个排名前 $K$ 的节点。
- **延伸思考**：复杂传染（阈值较高）下传播范围是否仍为子模函数？如果不是，贪心算法会出什么问题？

DOI：[10.1145/956750.956769](https://doi.org/10.1145/956750.956769)

### 其他引用文献

正文中引用的其余文献：

- 经典模型与再生数：Kermack 与 McKendrick 1927，[10.1098/rspa.1927.0118](https://doi.org/10.1098/rspa.1927.0118)；Diekmann、Heesterbeek 与 Metz 1990，[10.1007/BF00178324](https://doi.org/10.1007/BF00178324)；Wallinga 与 Teunis 2004，[10.1093/aje/kwh255](https://doi.org/10.1093/aje/kwh255)；Wallinga 与 Lipsitch 2007，[10.1098/rspb.2006.3754](https://doi.org/10.1098/rspb.2006.3754)；Cori 等 2013，[10.1093/aje/kwt133](https://doi.org/10.1093/aje/kwt133)。
- 网络阈值与理论方法：Newman 2002，[10.1103/PhysRevE.66.016128](https://doi.org/10.1103/PhysRevE.66.016128)；Barthélemy 等 2004，[10.1103/PhysRevLett.92.178701](https://doi.org/10.1103/PhysRevLett.92.178701)；Kenah 与 Robins 2007，[10.1103/PhysRevE.76.036113](https://doi.org/10.1103/PhysRevE.76.036113)；Chakrabarti 等 2008，[10.1145/1284680.1284681](https://doi.org/10.1145/1284680.1284681)；Van Mieghem、Omic 与 Kooij 2009，[10.1109/TNET.2008.925623](https://doi.org/10.1109/TNET.2008.925623)；Castellano 与 Pastor-Satorras 2010，[10.1103/PhysRevLett.105.218701](https://doi.org/10.1103/PhysRevLett.105.218701)；Keeling 1999，[10.1098/rspb.1999.0716](https://doi.org/10.1098/rspb.1999.0716)；Volz 2008，[10.1007/s00285-007-0116-4](https://doi.org/10.1007/s00285-007-0116-4)；Miller、Slim 与 Volz 2012，[10.1098/rsif.2011.0403](https://doi.org/10.1098/rsif.2011.0403)；Karrer 与 Newman 2010，[10.1103/PhysRevE.82.016101](https://doi.org/10.1103/PhysRevE.82.016101)；Gleeson 2011，[10.1103/PhysRevLett.107.068701](https://doi.org/10.1103/PhysRevLett.107.068701)。
- 接触网络与时间网络：Liljeros 等 2001，[10.1038/35082140](https://doi.org/10.1038/35082140)；Eubank 等 2004，[10.1038/nature02541](https://doi.org/10.1038/nature02541)；Mossong 等 2008，[10.1371/journal.pmed.0050074](https://doi.org/10.1371/journal.pmed.0050074)；Salathé 等 2010，[10.1073/pnas.1009094108](https://doi.org/10.1073/pnas.1009094108)；Rocha、Liljeros 与 Holme 2011，[10.1371/journal.pcbi.1001109](https://doi.org/10.1371/journal.pcbi.1001109)；Vanhems 等 2013，[10.1371/journal.pone.0073970](https://doi.org/10.1371/journal.pone.0073970)；Holme 与 Saramäki 2012，[10.1016/j.physrep.2012.03.001](https://doi.org/10.1016/j.physrep.2012.03.001)；Vazquez 等 2007，[10.1103/PhysRevLett.98.158702](https://doi.org/10.1103/PhysRevLett.98.158702)；Karsai 等 2011，[10.1103/PhysRevE.83.025102](https://doi.org/10.1103/PhysRevE.83.025102)；Perra 等 2012，[10.1038/srep00469](https://doi.org/10.1038/srep00469)；Valdano 等 2015，[10.1103/PhysRevX.5.021005](https://doi.org/10.1103/PhysRevX.5.021005)；Salathé 与 Jones 2010，[10.1371/journal.pcbi.1000736](https://doi.org/10.1371/journal.pcbi.1000736)。
- 集合种群与全球传播：Hufnagel、Brockmann 与 Geisel 2004，[10.1073/pnas.0308344101](https://doi.org/10.1073/pnas.0308344101)；Colizza 等 2006，[10.1073/pnas.0510525103](https://doi.org/10.1073/pnas.0510525103)；Colizza 与 Vespignani 2007，[10.1103/PhysRevLett.99.148701](https://doi.org/10.1103/PhysRevLett.99.148701)；Balcan 等 2009，[10.1073/pnas.0906910106](https://doi.org/10.1073/pnas.0906910106)；Chinazzi 等 2020，[10.1126/science.aba9757](https://doi.org/10.1126/science.aba9757)；Chang 等 2021，[10.1038/s41586-020-2923-3](https://doi.org/10.1038/s41586-020-2923-3)。
- 免疫、追踪与监测：Pastor-Satorras 与 Vespignani 2002，[10.1103/PhysRevE.65.036104](https://doi.org/10.1103/PhysRevE.65.036104)；Dezső 与 Barabási 2002，[10.1103/PhysRevE.65.055103](https://doi.org/10.1103/PhysRevE.65.055103)；Lloyd-Smith、Galvani 与 Getz 2003，[10.1098/rspb.2003.2481](https://doi.org/10.1098/rspb.2003.2481)；Eames 与 Keeling 2003，[10.1098/rspb.2003.2554](https://doi.org/10.1098/rspb.2003.2554)；Fraser 等 2004，[10.1073/pnas.0307506101](https://doi.org/10.1073/pnas.0307506101)；Christakis 与 Fowler 2010，[10.1371/journal.pone.0012948](https://doi.org/10.1371/journal.pone.0012948)；Ferretti 等 2020，[10.1126/science.abb6936](https://doi.org/10.1126/science.abb6936)；Kucharski 等 2020，[10.1016/S1473-3099(20)30457-6](https://doi.org/10.1016/S1473-3099(20)30457-6)；Adam 等 2020，[10.1038/s41591-020-1092-0](https://doi.org/10.1038/s41591-020-1092-0)；Kojaku 等 2021，[10.1038/s41567-021-01187-2](https://doi.org/10.1038/s41567-021-01187-2)；Donker、Wallinga 与 Grundmann 2010，[10.1371/journal.pcbi.1000715](https://doi.org/10.1371/journal.pcbi.1000715)。
- 社会传染与影响力：Coleman、Katz 与 Menzel 1957，[10.2307/2785979](https://doi.org/10.2307/2785979)；Granovetter 1978，[10.1086/226707](https://doi.org/10.1086/226707)；Watts 2002，[10.1073/pnas.082090499](https://doi.org/10.1073/pnas.082090499)；Centola 与 Macy 2007，[10.1086/521848](https://doi.org/10.1086/521848)；Centola 2010，[10.1126/science.1185231](https://doi.org/10.1126/science.1185231)；Cohen-Cole 与 Fletcher 2008，[10.1136/bmj.a2533](https://doi.org/10.1136/bmj.a2533)；Funk 等 2009，[10.1073/pnas.0810762106](https://doi.org/10.1073/pnas.0810762106)；Kitsak 等 2010，[10.1038/nphys1746](https://doi.org/10.1038/nphys1746)；Iyengar、Van den Bulte 与 Valente 2011，[10.1287/mksc.1100.0566](https://doi.org/10.1287/mksc.1100.0566)；Shalizi 与 Thomas 2011，[10.1177/0049124111404820](https://doi.org/10.1177/0049124111404820)；Banerjee 等 2013，[10.1126/science.1236498](https://doi.org/10.1126/science.1236498)；Kim 等 2015，[10.1016/S0140-6736(15)60095-2](https://doi.org/10.1016/S0140-6736(15)60095-2)；Morone 与 Makse 2015，[10.1038/nature14604](https://doi.org/10.1038/nature14604)；Iacopini 等 2019，[10.1038/s41467-019-10431-6](https://doi.org/10.1038/s41467-019-10431-6)。
- 传播溯源：Shah 与 Zaman 2011，[10.1109/TIT.2011.2158885](https://doi.org/10.1109/TIT.2011.2158885)；Pinto、Thiran 与 Vetterli 2012，[10.1103/PhysRevLett.109.068702](https://doi.org/10.1103/PhysRevLett.109.068702)；Lokhov 等 2014，[10.1103/PhysRevE.90.012801](https://doi.org/10.1103/PhysRevE.90.012801)；Zhang、Zhang、Lv 与 Yin 2016，Identification of efficient observers for locating spreading source in complex networks，Physica A 442: 100–109，[10.1016/j.physa.2015.09.017](https://doi.org/10.1016/j.physa.2015.09.017)。
- 脑网络扩散：Raj、Kuceyeski 与 Weiner 2012，[10.1016/j.neuron.2011.12.040](https://doi.org/10.1016/j.neuron.2011.12.040)。

## 延伸资源 {#resources}

| 类型 | 资源 | 说明 |
|---|---|---|
| 教材 | Barabási《Network Science》第 10 章 Spreading Phenomena（[链接](http://networksciencebook.com/chapter/10)） | SI/SIS/SIR、异质平均场推导、接触网络、超越度分布、免疫策略与流行病预测的主要参考；Advanced Topics 10.A–10.E 对应本专题的微观模型、网络解析解、目标免疫、SIR 阈值与全球流行模型；CC BY-NC-SA 2.0 |
| 教材 | Kiss、Miller 与 Simon 2017，Mathematics of Epidemics on Networks，Springer（[DOI](https://doi.org/10.1007/978-3-319-50806-1)） | 配对近似、边基模型、消息传递与精确模拟的系统处理，对应[配对近似、边基模型与消息传递](spreading.message-passing.html) |
| 综述 | Pastor-Satorras 等 2015, Epidemic processes in complex networks, Rev Mod Phys（[DOI](https://doi.org/10.1103/RevModPhys.87.925)） | 网络流行病学最全面的综述，先读第 1–4 节；时间网络、集合种群与免疫见后续章节 |
| 综述 | Holme 与 Saramäki 2012, Temporal networks, Physics Reports（[DOI](https://doi.org/10.1016/j.physrep.2012.03.001)） | 时间网络的概念、度量与传播，对应[时间网络与阵发性](spreading.temporal-networks.html) |
| 中文视频 | 中国大学 MOOC《复杂网络分析》7.2 网络上的疾病传播（[链接](https://www.icourse163.org/course/BNU-1206632825)） | 13 分钟中文入门 |
| 交互演示 | Complexity Explorables：Facebooked Flu Shots（[链接](https://www.complexity-explorables.org/explorables/facebooked-flu-shots/)） | 在浏览器里比较随机免疫与熟人免疫，对应[免疫策略](spreading.immunization.html) |
| 交互演示 | Nicky Case：The Wisdom and/or Madness of Crowds（[链接](https://ncase.me/crowds/)） | 交互文章，直观区分简单传染与复杂传染、阈值与级联，约 30 分钟 |
| 英文视频 | Beveridge：NetSci 12-2 Epidemics on Networks（[YouTube](https://www.youtube.com/watch?v=B_64X8kqJ8k)） | 6 分钟说明剩余度与传播阈值；需境外网络 |
| 论文 | Kitsak 等 2010, Identification of influential spreaders in complex networks, Nature Physics（[DOI](https://doi.org/10.1038/nphys1746)） | k-壳与关键传播者，对应[影响力最大化与关键传播者](spreading.influential-spreaders.html)；精读：[Kitsak 2010](paper-kitsak2010_spreaders.html) |
| 代码 | EoN（Epidemics on Networks）Python 包（[文档](https://epidemicsonnetworks.readthedocs.io/en/latest/)） | 基于 NetworkX 的快速 SIS/SIR 模拟与配对近似、EBCM 等方程模型，由该书作者之一维护，可替代代码示例中的手写模拟 |
| 软件 | EpiEstim（R 包，Cori 等 2013） | 从发病曲线估计时变再生数 $R_t$，对应[再生数与超级传播](spreading.reproduction-number.html) |

> 提示：Barabási《Network Science》在线版需加载境外脚本，在中国大陆可能无法正常显示；标注“需境外网络”的为 YouTube 资源。

## 开放问题 {#questions}

1. 选择一种你熟悉的疾病或健康行为（如结核、HPV、吸烟、抑郁情绪），说明它更接近简单传染还是复杂传染，在网络上应采用哪种干预策略，为什么？需要哪些数据来检验这一判断？
2. 如果手中有一份医院病区的医护–患者接触记录（时间戳 + 两人编号），应如何构建网络（静态还是时序？加权还是不加权？），如何用本专题的方法评估院内感染风险并确定优先监测对象？
3. 同一张接触网络上，HMF、淬火平均场与消息传递给出的阈值相差一倍。你会如何设计模拟与敏感性分析，向公共卫生决策者说明“真实阈值”的不确定性？
4. 向后追踪在理论上更有效，但需要回溯更长时间、记录更多接触。在保护隐私的数字追踪框架下，你会如何权衡追踪深度、方向与数据保存期限？
5. 一次院内耐药菌暴发中，只知道若干患者的阳性检出日期和医院转诊记录。如何结合网络溯源方法与病原体基因组数据推断传入源头？哪些假设最可能不成立？
