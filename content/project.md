---
title: 课程论文选题
checked: 2026-11-27
---

## 作业说明 {#guide}

课程论文是本课程唯一的考核。可以个人完成，也可以 2–3 人一组。

**选题方式。** 从下面 17 个题目中任选一个，也可以自拟题目。每个题目都写明了研究问题、公开数据、必做分析和进阶方向。“必做分析”是一篇合格论文的基本工作量；“进阶分析”供希望深入的同学选择，不要求全做。同一题目可以由多组选择，各组在计划书中写清自己的具体问题，例如选择不同的疾病、不同的数据子集，或比较不同的方法。自拟题目同样要回答下面的“五个问题”，并在计划书中写明数据来源。

**流程。** 选题与计划书（1–2 页：背景、问题、数据来源、拟用方法）→ 中期交流（数据已获取、网络已建好、有初步结果）→ 终期提交论文并课堂汇报。

**提交材料。**

1. 论文 PDF，正文 5–10 页（不含参考文献与附录）；
2. 代码（脚本或 Notebook）和简短的运行说明，按说明应能重现论文中的主要图表；
3. 数据来源清单：数据库名称、版本号、下载链接、下载日期、所用文件、许可；
4. 汇报幻灯片（10–15 分钟）。

**起步数据。** 课程手册已经把其中一部分数据整理成小表格，说明见[数据说明页](data-sources.html)，文件名可直接点击下载。这些文件适合熟悉数据、调试代码；论文的主体分析建议从原始来源下载完整数据，并记录版本。

## 每篇论文都要回答的五个问题 {#five}

1. **节点和边是什么？** 写清边的定义（相关系数类型、阈值、证据来源、是否有方向和权重），以及这样选的理由。
2. **和什么比？** 至少使用一种零模型或随机化对照，例如保度重连、按度匹配的随机基因集、置换组别标签、相位随机化代用数据、保留空间自相关的旋转检验。报告效应量，以及 z 分数、经验 p 值或置信区间。
3. **结论稳不稳？** 至少做一项敏感性分析：更换阈值、数据库版本、相互作用组、算法或参数，或者用自助法重抽样。
4. **有没有混杂？** 例如基因的研究热度（被研究得多的基因，被测到的相互作用也多）、头动、采集站点、年龄与性别、两组样本量不同。
5. **结论能说到哪一步？** 区分相关与因果。网络上找到的“关键节点”“候选药物”是待检验的假设，不是已经证实的结论。

## 论文结构建议 {#structure}

摘要（300 字以内）→ 引言（问题与已有工作，提出 1–3 个可检验的问题或假设）→ 数据与方法（数据来源与预处理、网络构建、指标、零模型、统计检验、敏感性分析）→ 结果（每张图回答一个问题）→ 讨论（与文献比较，说明局限）→ 参考文献（带 DOI）→ 附录（补充图表、数据来源清单、代码说明）。

## 评分 {#grading}

评分综合考虑四个方面：

| 方面 | 看什么 |
|:--------|:-------------------------|
| 选题创新性 | 问题明确、可检验，有自己的角度；数据与问题匹配 |
| 分析方法正确性 | 网络构建有依据；零模型与统计检验恰当；做了多重比较校正；代码能运行，数据来源和版本可追溯 |
| 结果与分析深度 | 结论与证据相称；做了敏感性分析；与文献比较；说明局限 |
| 报告和展示质量 | 结构清楚，图表规范；汇报控制时间，回答问题清楚 |

## 题目一览 {#list}

难度：★ 数据现成，方法常规；★★ 需要整合多个数据源或较多预处理；★★★ 原始数据量大、分析流程长。

| 编号 | 题目 | 主要数据 | 核心方法 | 难度 |
|:--:|:--------------|:-----------|:-----------|:---:|
| [A1](#a1) | 中心性–致死性规则的再检验 | BioGRID、STRING、SGD（酵母） | 中心性、ROC、保度重连、回归 | ★ |
| [A2](#a2) | 转录调控网络中的网络模体与零模型 | CollecTRI、TRRUST | 三元组普查、多种零模型 | ★ |
| [A3](#a3) | 基因调控网络推断方法的金标准评测 | BEELINE、DREAM5 | 相关、互信息、GENIE3、AUPR | ★★ |
| [A4](#a4) | 阿尔茨海默病脑组织共表达模块 | GEO GSE33000、GSE132903 | WGCNA、模块保守性、富集 | ★★ |
| [A5](#a5) | 乳腺癌 ER 亚型间的共表达网络重连 | TCGA（UCSC Xena）、GEO | 差异相关、置换检验 | ★★ |
| [B1](#b1) | 疾病模块与疾病间的网络分离度 | Open Targets、STRING、BioGRID | LCC 显著性、分离度 | ★★ |
| [B2](#b2) | 网络邻近度与药物重定位的回顾性验证 | Open Targets（ChEMBL）、STRING | 邻近度 z 分数、ROC | ★★ |
| [B3](#b3) | 人类症状–疾病网络 | HPO、STRING | 二部网络投影、Mantel 检验、社团 | ★★ |
| [B4](#b4) | 慢性病共病网络 | NHANES | 相对风险、φ 系数、分层网络 | ★ |
| [C1](#c1) | 抑郁症状网络的性别差异与跨时期稳定性 | NHANES PHQ-9（2005–2023） | 正则化偏相关网络、稳定性、NCT | ★ |
| [D1](#d1) | 结构–功能耦合 | Lausanne 连接组（70 人） | 通讯模型、回归、空间零模型 | ★★ |
| [D2](#d2) | 疾病皮层改变是否沿连接组分布 | ENIGMA Toolbox | 邻域模型、旋转检验、震中 | ★★ |
| [D3](#d3) | 孤独症功能连接组差异的稳健性 | ABIDE Preprocessed | 多元宇宙分析、NBS、ComBat | ★★★ |
| [D4](#d4) | 动态功能连接与代用数据检验 | nilearn 发育 fMRI（OpenNeuro ds000228） | 滑动窗口、k-means、相位随机化 | ★★★ |
| [D5](#d5) | 头皮脑电的同步网络 | PhysioNet eegmmidb、CHB-MIT | PLV、wPLI、Kuramoto 序参量 | ★ / ★★★ |
| [E1](#e1) | 医院病房接触网络上的传播与免疫 | SocioPatterns | 时间网络 SIR、免疫策略 | ★ |
| [E2](#e2) | 人类信号网络的结构可控性 | OmniPath、DepMap、Open Targets | 最大匹配、驱动节点、富集 | ★★ |

## A　分子网络与网络基础 {#group-a}

### A1　中心性–致死性规则还成立吗？研究热度、数据来源与蛋白复合物的影响 {#a1 toc="A1　中心性–致死性规则的再检验"}

**难度** ★　**对应手册专题**：[生物分子网络与拓扑特征](molecular-networks.html)、[网络结构指标与随机图](network-metrics.html)、[网络鲁棒性](robustness.html)

**背景与问题。** Jeong 等（2001）在酵母蛋白质相互作用网络中发现，连接多的蛋白（枢纽）更可能是必需基因，这被称为“中心性–致死性规则”。后来的研究给出了不同的解释：枢纽更可能参与“必需的相互作用”（He 与 Zhang 2006），或更可能属于必需的蛋白复合物（Zotenko 等 2008）。还有一个常被忽略的混杂：被研究得多的蛋白，被测到的相互作用也多。本题用当前的高质量数据重新检验这一规则：

1. 各种中心性与必需性的关联有多强？
2. 控制研究热度之后还剩多少？
3. 换用不同来源、不同通量的相互作用数据，结论是否一致？

**数据**

| 数据 | 内容 | 获取 | 许可 |
|:-------|:----------------|:-----------|:-----|
| BioGRID 5.0（酿酒酵母 S288c） | 物理与遗传相互作用记录，含实验方法、通量（高/低）、文献编号 | [downloads.thebiogrid.org/BioGRID](https://downloads.thebiogrid.org/BioGRID) | MIT |
| STRING v12.0（物种 4932） | 按证据通道打分的蛋白关联 | [string-db.org/cgi/download](https://string-db.org/cgi/download) | CC BY 4.0 |
| SGD 表型注释 | 系统缺失突变的“致死/存活”表型 | [downloads.yeastgenome.org/…/phenotype_data.tab](https://downloads.yeastgenome.org/curation/literature/phenotype_data.tab) | CC BY 4.0 |
| NCBI gene2pubmed | 每个基因关联的 PubMed 文献，用来衡量研究热度 | [ftp.ncbi.nlm.nih.gov/…/gene2pubmed.gz](https://ftp.ncbi.nlm.nih.gov/gene/DATA/gene2pubmed.gz) | NCBI 公开数据 |
| Complex Portal（进阶用） | 人工整理的酵母蛋白复合物 | [ftp.ebi.ac.uk/…/559292.tsv](https://ftp.ebi.ac.uk/pub/databases/intact/complex/current/complextab/559292.tsv) | 见 Complex Portal 网站 |
| 手册起步数据 | [`yeast_ppi_biogrid.csv`](data/yeast_ppi_biogrid.csv)（至少 2 篇文献支持，25,006 条边、3,968 个蛋白）与 [`yeast_genes_essential.csv`](data/yeast_genes_essential.csv)；[`yeast_string_v12_experimental.csv`](data/yeast_string_v12_experimental.csv) 与 [`yeast_genes_essentiality.csv`](data/yeast_genes_essentiality.csv) | [数据说明页](data-sources.html) | 同上 |

**必做分析**

1. 构建网络，报告节点数、边数和巨连通分支大小；拟合度分布（按 Clauset 等的方法，比较幂律、对数正态和截断幂律）。
2. 计算至少四种中心性（度、介数、特征向量或 PageRank、k-core 或聚类系数），用 ROC 曲线下面积（AUC）评价它们区分必需与非必需基因的能力；画“按度分箱的必需基因比例”曲线。
3. 零模型：保度重连不改变节点的度，所以度的 AUC 不变。比较介数、k-core、聚类系数在真实网络和至少 100 个重连网络中的 AUC，判断这些指标是否提供了度以外的信息。置换必需性标签，得到 AUC 的随机基线。
4. 控制混杂：逻辑回归“必需性 ~ log(度+1) + log(文献数+1)”，报告度的调整后比值比及其置信区间。
5. 数据来源敏感性：分别用 BioGRID 的低通量记录、高通量记录和 STRING 的 experiments 通道建网，比较结论。

**进阶方向**

- 复合物解释：标出属于“必需复合物”（复合物中必需成员比例高）的蛋白，检验控制复合物成员身份后，度与必需性的关联是否消失。
- 鲁棒性：按度、介数和随机顺序删除节点，比较巨连通分支的下降；删除必需基因是否比删除按度匹配的非必需基因更破坏连通性。
- 推广到人类：用 DepMap 的 CRISPR 必需性数据（或 Open Targets 的 `target_essentiality`）与 STRING 人类网络重复主要分析。

**注意。** 一个蛋白在 BioGRID 中出现的文献数与它的度高度相关，用它衡量研究热度会造成循环论证，应取 gene2pubmed 等独立来源。SGD 中不同实验的必需性注释可能互相矛盾，要写清判定规则。

**参考文献**

- Jeong H, et al. Lethality and centrality in protein networks. *Nature*, 2001. [doi:10.1038/35075138](https://doi.org/10.1038/35075138)
- He X, Zhang J. Why Do Hubs Tend to Be Essential in Protein Networks? *PLoS Genetics*, 2006. [doi:10.1371/journal.pgen.0020088](https://doi.org/10.1371/journal.pgen.0020088)
- Zotenko E, et al. Why Do Hubs in the Yeast Protein Interaction Network Tend To Be Essential: Reexamining the Connection between the Network Topology and Essentiality. *PLoS Computational Biology*, 2008. [doi:10.1371/journal.pcbi.1000140](https://doi.org/10.1371/journal.pcbi.1000140)
- Albert R, et al. Error and attack tolerance of complex networks. *Nature*, 2000. [doi:10.1038/35019019](https://doi.org/10.1038/35019019)
- Clauset A, et al. Power-Law Distributions in Empirical Data. *SIAM Review*, 2009. [doi:10.1137/070710111](https://doi.org/10.1137/070710111)

### A2　转录调控网络中的网络模体：富集结论有多依赖零模型？ {#a2 toc="A2　转录调控网络中的网络模体与零模型"}

**难度** ★　**对应手册专题**：[生物分子网络与拓扑特征](molecular-networks.html)、[度相关性与网络结构的高阶统计](degree-correlations.html)、[网络构建与统计验证](network-construction.html)

**背景与问题。** Milo 等（2002）和 Shen-Orr 等（2002）发现，大肠杆菌和酵母转录调控网络中前馈环（FFL）等三节点结构出现得远比随机网络多，称为网络模体，并认为它们是执行特定信息处理功能的基本单元。Artzy-Randrup 等（2004）随即指出，一个结构是否“显著富集”取决于拿什么样的随机网络来比较。本题在人类转录调控网络中检验：

1. 哪些三节点子图显著富集？
2. 换用不同的零模型，z 分数和排序怎样变化？
3. 带符号的前馈环中，一致型与非一致型各占多少？

**数据**

| 数据 | 内容 | 获取 | 许可 |
|:-------|:----------------|:-----------|:-----|
| CollecTRI（经 OmniPath 下载） | 人类转录因子（TF）→ 靶基因调控关系，部分带激活/抑制标注 | [omnipathdb.org/interactions](https://omnipathdb.org/interactions?datasets=collectri&genesymbols=yes) | 每条关系沿用来源数据库的许可 |
| TRRUST v2 | 文献整理的人类与小鼠 TF–靶基因关系，带激活/抑制；人类 8,444 条、800 个 TF | [www.grnpedia.org/trrust](https://www.grnpedia.org/trrust/) | CC BY-SA 4.0 |
| 手册起步数据 | [`collectri_human_tf_target_ccby_curated.csv`](data/collectri_human_tf_target_ccby_curated.csv)（16,164 条、918 个 TF，只保留有 CC BY 4.0 来源支持的关系，无符号） | [数据说明页](data-sources.html) | CC BY 4.0 |

**必做分析**

1. 构建有向网络，描述入度和出度分布、自调控与相互调控的数量。
2. 三元组普查（如 `networkx.triadic_census`），统计 13 类连通三节点子图的出现次数。
3. 至少用三种零模型，各生成不少于 200 个随机网络：(a) 节点数、边数相同的有向随机图；(b) 保持每个节点入度和出度的边交换；(c) 在 (b) 的基础上同时保持相互调控边的数目。计算每类子图的 z 分数和经验 p 值，比较三种零模型下的结果。
4. 讨论：FFL 富集在哪些零模型下成立？z 分数的大小怎样随零模型变化？“显著富集”应该怎样报告？

**进阶方向**

- 用 TRRUST 的激活/抑制标注统计 8 种带符号 FFL，比较一致型与非一致型的比例（Mangan 与 Alon 2003）。
- 研究偏倚：只保留有多个独立来源支持的边，或者去掉靶基因最多的若干 TF，重复分析。
- 节点的模体参与度（参与 FFL 的次数）与疾病基因（Open Targets）是否有关，与按度匹配的随机基因比较。
- 比较人类与小鼠 TRRUST 网络的“模体谱”。

**注意。** 已知的调控关系集中在少数研究充分的 TF 上，网络很不完整。随机网络的数量要在计算量和精度之间权衡，并在文中说明。

**参考文献**

- Milo R, et al. Network Motifs: Simple Building Blocks of Complex Networks. *Science*, 2002. [doi:10.1126/science.298.5594.824](https://doi.org/10.1126/science.298.5594.824)
- Shen-Orr SS, et al. Network motifs in the transcriptional regulation network of Escherichia coli. *Nature Genetics*, 2002. [doi:10.1038/ng881](https://doi.org/10.1038/ng881)
- Artzy-Randrup Y, et al. Comment on "Network Motifs: Simple Building Blocks of Complex Networks" and "Superfamilies of Evolved and Designed Networks". *Science*, 2004. [doi:10.1126/science.1099334](https://doi.org/10.1126/science.1099334)
- Alon U. Network motifs: theory and experimental approaches. *Nature Reviews Genetics*, 2007. [doi:10.1038/nrg2102](https://doi.org/10.1038/nrg2102)
- Mangan S, Alon U. Structure and function of the feed-forward loop network motif. *Proceedings of the National Academy of Sciences*, 2003. [doi:10.1073/pnas.2133841100](https://doi.org/10.1073/pnas.2133841100)
- Müller-Dott S, et al. Expanding the coverage of regulons from high-confidence prior knowledge for accurate estimation of transcription factor activities. *Nucleic Acids Research*, 2023. [doi:10.1093/nar/gkad841](https://doi.org/10.1093/nar/gkad841)
- Han H, et al. TRRUST v2: an expanded reference database of human and mouse transcriptional regulatory interactions. *Nucleic Acids Research*, 2018. [doi:10.1093/nar/gkx1013](https://doi.org/10.1093/nar/gkx1013)

### A3　基因调控网络推断方法的金标准评测 {#a3 toc="A3　基因调控网络推断方法的金标准评测"}

**难度** ★★　**对应手册专题**：[基因调控网络推断与共表达分析](gene-network-inference.html)

**背景与问题。** 从表达数据推断调控关系的方法很多：相关、偏相关、互信息（ARACNe、CLR）、基于树模型的 GENIE3 等。DREAM5 评测发现，没有一种方法在所有数据上都最好，把多种方法的排名集成起来最稳健（Marbach 等 2012）；BEELINE 对单细胞数据的评测发现，许多方法只比随机略好（Pratapa 等 2020）。本题在带金标准的数据上比较几类方法：

1. 各方法的 AUPR 比随机高多少？
2. 性能怎样随样本量变化？
3. 方法在哪些网络结构上系统性地出错？

**数据**

| 数据 | 内容 | 获取 | 许可 |
|:-------|:----------------|:-----------|:-----|
| BEELINE | 不同拓扑的合成网络（BoolODE 模拟）、人工整理的布尔模型、真实单细胞数据及其参考网络 | Zenodo，doi:10.5281/zenodo.3701939（`BEELINE-data.zip` 262 MB，`BEELINE-Networks.zip` 17 MB），无需注册 | CC BY-NC 4.0 |
| DREAM5 网络推断挑战 | 计算机模拟网络与大肠杆菌、酿酒酵母等的表达汇编及金标准 | Synapse，编号 syn2787209（需免费注册账号） | 见 Synapse 页面 |

**必做分析**

1. 选至少两套带金标准的数据（如 BEELINE 中两种合成网络，加上 DREAM5 的模拟网络或大肠杆菌数据）。
2. 至少比较三类方法：Pearson 或 Spearman 相关；偏相关（graphical lasso）；互信息类（CLR 或 ARACNe）；树模型（GENIE3 或 GRNBoost2，可用 Python 包 arboreto）。
3. 评估：AUROC、AUPR，以及 AUPR 相对随机预测的倍数；打乱基因标签得到随机基线。说明无向方法的结果怎样与有向金标准比较（例如只评估 TF → 靶基因的边）。
4. 样本量：对样本随机子抽样（如 10%、25%、50%、100%），每一档重复多次，画“性能–样本量”曲线。
5. 错误分析：把排名前 k 的预测中的假阳性按结构分类，例如两个靶基因共享同一调控者造成的“兄弟边”、级联中跳过中间节点的边，解释各方法的系统性偏差（Marbach 等 2010）。

**进阶方向**

- 集成：对多种方法的边排名取平均，检验是否优于单一方法。
- 先验约束：在大肠杆菌数据中只允许已知 TF 作为调控者，比较性能变化。
- 真实单细胞数据：在 BEELINE 的真实数据上比较各方法与随机基线的差距。

**注意。** 金标准本身不完整，一部分“假阳性”可能是未被记录的真实调控。在稀疏网络中 AUROC 很容易显得高，应以 AUPR 为主要指标。

**参考文献**

- Marbach D, et al. Wisdom of crowds for robust gene network inference. *Nature Methods*, 2012. [doi:10.1038/nmeth.2016](https://doi.org/10.1038/nmeth.2016)
- Marbach D, et al. Revealing strengths and weaknesses of methods for gene network inference. *Proceedings of the National Academy of Sciences*, 2010. [doi:10.1073/pnas.0913357107](https://doi.org/10.1073/pnas.0913357107)
- Pratapa A, et al. Benchmarking algorithms for gene regulatory network inference from single-cell transcriptomic data. *Nature Methods*, 2020. [doi:10.1038/s41592-019-0690-6](https://doi.org/10.1038/s41592-019-0690-6)
- Huynh-Thu VA, et al. Inferring Regulatory Networks from Expression Data Using Tree-Based Methods. *PLoS ONE*, 2010. [doi:10.1371/journal.pone.0012776](https://doi.org/10.1371/journal.pone.0012776)
- Margolin AA, et al. ARACNE: An Algorithm for the Reconstruction of Gene Regulatory Networks in a Mammalian Cellular Context. *BMC Bioinformatics*, 2006. [doi:10.1186/1471-2105-7-S1-S7](https://doi.org/10.1186/1471-2105-7-S1-S7)
- Faith JJ, et al. Large-Scale Mapping and Validation of Escherichia coli Transcriptional Regulation from a Compendium of Expression Profiles. *PLoS Biology*, 2007. [doi:10.1371/journal.pbio.0050008](https://doi.org/10.1371/journal.pbio.0050008)

### A4　阿尔茨海默病前额叶皮层的共表达模块：识别、跨队列保守性与疾病关联 {#a4 toc="A4　阿尔茨海默病脑组织共表达模块"}

**难度** ★★　**对应手册专题**：[基因调控网络推断与共表达分析](gene-network-inference.html)

**背景与问题。** Zhang 等（2013）用数百例尸检脑组织构建共表达与调控网络，发现以 TYROBP 为核心的免疫/小胶质细胞模块与晚发型阿尔茨海默病（AD）相关。此后加权基因共表达网络分析（WGCNA）被广泛使用，但模块能否在独立队列中重现、是否只是细胞组成变化的反映，常常没有检验。本题：

1. 识别与 AD 诊断相关的共表达模块；
2. 检验这些模块在另一队列、另一脑区中是否保守；
3. 判断模块与 AD 遗传风险基因、细胞类型标记的关系。

**数据**

| 数据 | 内容 | 获取 | 许可 |
|:-------|:----------------|:-----------|:-----|
| GEO GSE33000（发现队列） | 624 例背外侧前额叶（BA9）：AD 310、亨廷顿病 157、非痴呆对照 157；Agilent 44K 定制芯片（GPL4372），双通道，每个样本与混合参照池对比（数值是相对参照池的比值） | [www.ncbi.nlm.nih.gov/geo/query/acc.cgi](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE33000) | GEO 公开 |
| GEO GSE132903（验证队列） | 195 例颞中回：AD 97、对照 98；Illumina HT-12 v4 | [www.ncbi.nlm.nih.gov/geo/query/acc.cgi](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE132903) | GEO 公开 |
| GEO GSE48350（备选验证） | 253 个样本，取自海马、内嗅皮层、额上回、中央后回四个脑区；Affymetrix GPL570 | [www.ncbi.nlm.nih.gov/geo/query/acc.cgi](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE48350) | GEO 公开 |
| AD 遗传关联基因 | Open Targets 遗传关联分数（数据版本 26.09）；手册起步数据 [`opentargets_disease_genes_ga.csv`](data/opentargets_disease_genes_ga.csv) 已含 AD | [platform.opentargets.org/downloads](https://platform.opentargets.org/downloads) | CC0 1.0 |
| 脑细胞类型标记 | McKenzie 等（2018）整理的神经元、星形胶质细胞、小胶质细胞、少突胶质细胞、内皮细胞标记基因 | 论文补充材料 | 见原文 |

GSE33000 的说明中写明，其中 227 个样本在 GSE44770 中重复使用，因此 GSE44770 不能当作独立的验证队列。

**必做分析**

1. 预处理：探针合并到基因；样本聚类，剔除离群样本；在模型中控制年龄、性别等 GEO 提供的协变量。
2. WGCNA：选择软阈值（同时报告无标度拟合 R² 和平均连通度，并讨论“无标度”标准本身的局限），识别模块，计算模块特征基因与诊断的关联。
3. 模块保守性：在验证队列中计算 Zsummary 和 medianRank（WGCNA 的 `modulePreservation`），区分保守、中等保守和不保守的模块。
4. 功能与细胞类型：对与诊断相关的模块做 AD 遗传关联基因、细胞类型标记和 Reactome 通路的超几何检验，背景基因集用芯片上检测到的全部基因。
5. 稳健性：对样本做至少 50 次 80% 子抽样，重新识别模块，用调整兰德指数衡量模块划分的一致性；比较不同软阈值和最小模块大小下的结果。

**进阶方向**

- 比较 AD 与亨廷顿病的模块（Narayanan 等 2014 报告了两种疾病共有的失调网络）。
- 模块内“枢纽基因”与按连通度匹配的随机基因相比，是否更多是 AD 遗传关联基因？
- 差异连通性：分别在 AD 和对照中计算基因的模块内连通度，找连接变化最大的基因。
- 用 STRING 检验模块内的蛋白相互作用是否多于随机。

**注意。** AD 脑组织中神经元减少、胶质增生，与诊断相关的模块可能主要反映细胞比例的变化，而不是调控关系的改变，应以细胞类型标记的特征基因为协变量做敏感性分析。枢纽基因不等于驱动基因。

**参考文献**

- Langfelder P, Horvath S. WGCNA: an R package for weighted correlation network analysis. *BMC Bioinformatics*, 2008. [doi:10.1186/1471-2105-9-559](https://doi.org/10.1186/1471-2105-9-559)
- Langfelder P, et al. Is My Network Module Preserved and Reproducible? *PLoS Computational Biology*, 2011. [doi:10.1371/journal.pcbi.1001057](https://doi.org/10.1371/journal.pcbi.1001057)
- Zhang B, et al. Integrated Systems Approach Identifies Genetic Nodes and Networks in Late-Onset Alzheimer’s Disease. *Cell*, 2013. [doi:10.1016/j.cell.2013.03.030](https://doi.org/10.1016/j.cell.2013.03.030)
- Narayanan M, et al. Common dysregulation network in the human prefrontal cortex underlies two neurodegenerative diseases. *Molecular Systems Biology*, 2014. [doi:10.15252/msb.20145304](https://doi.org/10.15252/msb.20145304)
- McKenzie AT, et al. Brain Cell Type Specific Gene Expression and Co-expression Network Architectures. *Scientific Reports*, 2018. [doi:10.1038/s41598-018-27293-5](https://doi.org/10.1038/s41598-018-27293-5)
- Broido AD, Clauset A. Scale-free networks are rare. *Nature Communications*, 2019. [doi:10.1038/s41467-019-08746-5](https://doi.org/10.1038/s41467-019-08746-5)

### A5　乳腺癌雌激素受体亚型之间的共表达网络“重连” {#a5 toc="A5　乳腺癌 ER 亚型间的共表达网络重连"}

**难度** ★★　**对应手册专题**：[基因调控网络推断与共表达分析](gene-network-inference.html)、[网络构建与统计验证](network-construction.html)

**背景与问题。** 差异表达分析只比较均值。疾病或亚型之间，基因与基因之间的关系也可能改变：一些基因对在一组中高度相关，在另一组中却不相关，这称为差异共表达或网络重连（de la Fuente 2010）。雌激素受体（ER）阳性和阴性乳腺癌在生物学和治疗上差别很大。本题：

1. 两种亚型之间有多少基因对的相关显著不同，是否超过置换标签后的期望？
2. 相关关系变化最多的“重连枢纽”基因，是不是差异表达基因？
3. 差异相关中有多少可以由方差差异或肿瘤纯度解释？
4. 结果能否在另一个队列中重复？

**数据**

| 数据 | 内容 | 获取 | 许可 |
|:-------|:----------------|:-----------|:-----|
| TCGA 乳腺癌（UCSC Xena） | RNA-seq 表达矩阵 `HiSeqV2`（log2(RSEM+1)，1,218 个样本，其中 114 个为癌旁正常组织）；临床表 `BRCA_clinicalMatrix`（ER 状态字段为 `breast_carcinoma_estrogen_receptor_status`，另有 PAM50 分型） | [xenabrowser.net/datapages](https://xenabrowser.net/datapages/?cohort=TCGA%20Breast%20Cancer%20(BRCA)) | TCGA 开放获取数据 |
| GEO GDS4057（验证或起步） | 103 例化疗前 HER2 阴性乳腺癌活检：ER 阳性 42、阴性 56、缺失 5；Affymetrix GPL96。手册起步数据 [`breast_gds4057_expr_top1000.csv`](data/breast_gds4057_expr_top1000.csv)（方差最大的 1,000 个基因）与 [`breast_gds4057_samples.csv`](data/breast_gds4057_samples.csv)；完整数据见 GSE22093 | [数据说明页](data-sources.html)；[www.ncbi.nlm.nih.gov/geo/query/acc.cgi](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE22093) | NCBI 不设限制 |
| 肿瘤纯度（可选） | 用 ESTIMATE 方法由表达谱估计基质和免疫评分，或使用 TCGA 已发表的纯度估计 | R 包 `estimate`；Aran 等（2015）的补充数据 | 见原文 |

**必做分析**

1. 选择基因集（如两组都表达、方差最大的 1,000–2,000 个基因），在 ER 阳性和阴性组中分别计算 Spearman 相关。两组样本量不同，把 ER 阳性组多次随机下采样到与阴性组相同的人数。
2. 差异相关：对每对基因做 Fisher z 检验并做 FDR 校正；置换 ER 标签（不少于 1,000 次），得到“差异边总数”和“每个基因的差异度”的零分布。
3. 差异网络的拓扑：差异度最高的“重连枢纽”有哪些？它们与差异表达基因（t 检验或 limma）的重叠是否超过随机期望？
4. 混杂：比较两组的基因方差，检验差异相关是否集中在方差变化大的基因上；以肿瘤纯度为协变量计算偏相关后重做。
5. 重复：在第二个队列中检验差异边的方向一致率，并与随机基因对比较。

**进阶方向**

- 模块层面：在 ER 阳性组中定义共表达模块，检验它们在 ER 阴性组中是否保守。
- 比较几种差异共表达方法（参考 Bhuva 等 2019 的评测）。
- 按 PAM50 分子亚型分层分析。

**注意。** 两组样本量不同会改变相关系数的抽样方差；上百万对基因的检验必须做多重校正；批次和测序平台的差异会影响跨队列比较。

**参考文献**

- de la Fuente A. From ‘differential expression’ to ‘differential networking’ – identification of dysfunctional regulatory networks in diseases. *Trends in Genetics*, 2010. [doi:10.1016/j.tig.2010.05.001](https://doi.org/10.1016/j.tig.2010.05.001)
- Bhuva DD, et al. Differential co-expression-based detection of conditional relationships in transcriptional data: comparative analysis and application to breast cancer. *Genome Biology*, 2019. [doi:10.1186/s13059-019-1851-8](https://doi.org/10.1186/s13059-019-1851-8)
- Cancer Genome Atlas Network. Comprehensive molecular portraits of human breast tumours. *Nature*, 2012. [doi:10.1038/nature11412](https://doi.org/10.1038/nature11412)
- Iwamoto T, et al. Gene Pathways Associated With Prognosis and Chemotherapy Sensitivity in Molecular Subtypes of Breast Cancer. *JNCI: Journal of the National Cancer Institute*, 2011. [doi:10.1093/jnci/djq524](https://doi.org/10.1093/jnci/djq524)
- Yoshihara K, et al. Inferring tumour purity and stromal and immune cell admixture from expression data. *Nature Communications*, 2013. [doi:10.1038/ncomms3612](https://doi.org/10.1038/ncomms3612)
- Aran D, et al. Systematic pan-cancer analysis of tumour purity. *Nature Communications*, 2015. [doi:10.1038/ncomms9971](https://doi.org/10.1038/ncomms9971)

## B　网络医学 {#group-b}

### B1　疾病模块与疾病间的网络分离度：在不完整的相互作用组中能看到什么？ {#b1 toc="B1　疾病模块与疾病间的网络分离度"}

**难度** ★★　**对应手册专题**：[疾病模块、网络邻近度与药物重定位](network-medicine.html)

**背景与问题。** 网络医学认为，同一疾病的相关基因在人类相互作用组中聚集成“疾病模块”。Menche 等（2015）发现，尽管相互作用组很不完整，许多疾病的基因仍然形成显著大于随机的连通子网；两种疾病的模块在网络上的分离度 s~AB~ 还能预测它们在共表达、症状和共病上的相似性。本题用当前数据检验：

1. 哪些疾病有显著的疾病模块？
2. 结论怎样随相互作用组和基因集阈值变化？
3. 分离度能否预测独立测量的疾病相似性？

**数据**

| 数据 | 内容 | 获取 | 许可 |
|:-------|:----------------|:-----------|:-----|
| Open Targets Platform 26.09 | `association_by_datatype_direct`（列为 diseaseId、targetId、aggregationValue、associationScore 等），取 aggregationValue 为 `genetic_association` 的记录作为疾病基因 | [platform.opentargets.org/downloads](https://platform.opentargets.org/downloads)；FTP 目录 [ftp.ebi.ac.uk/…/output](https://ftp.ebi.ac.uk/pub/databases/opentargets/platform/26.09/output/) | CC0 1.0 |
| STRING v12.0（人类） | `protein.physical.links`（物理相互作用）与 `protein.links.full`（分证据通道） | [string-db.org/cgi/download](https://string-db.org/cgi/download) | CC BY 4.0 |
| BioGRID 5.0（人类） | 实验测定的相互作用记录 | [downloads.thebiogrid.org/BioGRID](https://downloads.thebiogrid.org/BioGRID) | MIT |
| 疾病相似性（任选一种） | HPO 表型注释（见 B3）、共享药物（见 B2）、共病强度（见 B4） | 见相应题目 | 见相应题目 |
| 手册起步数据 | [`opentargets_disease_genes_ga.csv`](data/opentargets_disease_genes_ga.csv)（11 种疾病）；[`string_human_physical_v12_s700.csv`](data/string_human_physical_v12_s700.csv)（86,519 条边、10,746 个蛋白）；[`string_multichannel_disease_genes_v12_5.csv`](data/string_multichannel_disease_genes_v12_5.csv)（分通道打分） | [数据说明页](data-sources.html) | CC0 / CC BY 4.0 |

**必做分析**

1. 选至少 10 种疾病（可以从起步数据的 11 种开始扩展），按遗传关联分数取疾病基因（主分析如 ≥ 0.5，敏感性分析用 0.3 和 0.7）。
2. 模块显著性：计算疾病基因在网络中的最大连通分支（LCC）大小，与按度分箱匹配的随机基因集（不少于 1,000 次）比较，报告 z 分数；同时计算模块内的平均最短距离 d~s~。
3. 疾病对的分离度 s~AB~ = ⟨d~AB~⟩ − (⟨d~AA~⟩ + ⟨d~BB~⟩)/2，与独立的疾病相似性做 Spearman 相关。疾病对之间不独立，用置换检验（如 Mantel 检验）。
4. 相互作用组敏感性：比较 STRING 物理相互作用 ≥ 700、≥ 400，BioGRID 低通量记录，STRING 全通道（含文本挖掘）。讨论文本挖掘边可能与疾病基因注释出自同一批文献而造成的循环。
5. 共享基因会直接使 s~AB~ 变小，去掉两种疾病的共享基因后重做第 3 步。

**进阶方向**

- 不完整性模拟：随机删除一定比例的边，观察 LCC z 分数随网络完整度的变化（Menche 等 2015 的核心论证）。
- 用 DIAMOnD 或基于随机游走的网络传播扩展疾病模块，用留一交叉验证评估能否找回被隐藏的疾病基因。

**注意。** 不同疾病的基因数相差很大，要比较 z 分数，而不是 LCC 的原始大小。疾病基因往往研究得多、度高，按度匹配的随机抽样必不可少。

**参考文献**

- Menche J, et al. Uncovering disease-disease relationships through the incomplete interactome. *Science*, 2015. [doi:10.1126/science.1257601](https://doi.org/10.1126/science.1257601)
- Barabási AL, et al. Network medicine: a network-based approach to human disease. *Nature Reviews Genetics*, 2011. [doi:10.1038/nrg2918](https://doi.org/10.1038/nrg2918)
- Ghiassian SD, et al. A DIseAse MOdule Detection (DIAMOnD) Algorithm Derived from a Systematic Analysis of Connectivity Patterns of Disease Proteins in the Human Interactome. *PLOS Computational Biology*, 2015. [doi:10.1371/journal.pcbi.1004120](https://doi.org/10.1371/journal.pcbi.1004120)
- Cowen L, et al. Network propagation: a universal amplifier of genetic associations. *Nature Reviews Genetics*, 2017. [doi:10.1038/nrg.2017.38](https://doi.org/10.1038/nrg.2017.38)
- Buniello A, et al. Open Targets Platform: facilitating therapeutic hypotheses building in drug discovery. *Nucleic Acids Research*, 2025. [doi:10.1093/nar/gkae1128](https://doi.org/10.1093/nar/gkae1128)
- Szklarczyk D, et al. The STRING database in 2023: protein–protein association networks and functional enrichment analyses for any sequenced genome of interest. *Nucleic Acids Research*, 2023. [doi:10.1093/nar/gkac1000](https://doi.org/10.1093/nar/gkac1000)

### B2　网络邻近度能找回已知适应症吗？药物重定位方法的回顾性验证 {#b2 toc="B2　网络邻近度与药物重定位的回顾性验证"}

**难度** ★★　**对应手册专题**：[疾病模块、网络邻近度与药物重定位](network-medicine.html)

**背景与问题。** Guney 等（2016）提出用“网络邻近度”衡量药物与疾病的关系：计算药物靶点到疾病基因的最近距离，再与按度匹配的随机靶点集比较，得到 z 分数；z 越负，药物越可能对该疾病有效。这一思路后来被用于老药新用（Cheng 等 2018）和新冠药物筛选（Morselli Gysi 等 2021）。本题：

1. 用当前的 Open Targets 数据，邻近度区分已批准适应症的能力有多强？
2. 是否优于更简单的基线？
3. 结论对距离定义和相互作用组有多敏感？

**数据**

| 数据 | 内容 | 获取 | 许可 |
|:-------|:----------------|:-----------|:-----|
| Open Targets Platform 26.09 | `drug_molecule`（药物）、`drug_mechanism_of_action`（作用机制与靶点，源自 ChEMBL）、`clinical_indication`（药物–疾病对及其最高临床阶段，其中 APPROVAL 为已批准）、`association_by_datatype_direct`（疾病基因） | FTP 目录 [ftp.ebi.ac.uk/…/output](https://ftp.ebi.ac.uk/pub/databases/opentargets/platform/26.09/output/) | Open Targets 为 CC0 1.0；源自 ChEMBL 的部分为 CC BY-SA 3.0 |
| STRING v12.0（人类） | 物理相互作用 | [string-db.org/cgi/download](https://string-db.org/cgi/download) | CC BY 4.0 |
| 手册起步数据 | [`opentargets_drug_targets.csv`](data/opentargets_drug_targets.csv)（17 种药物的作用机制靶点与已批准适应症） | [数据说明页](data-sources.html) | CC BY-SA 3.0 |

**必做分析**

1. 选 5–10 种疾病和至少 100 种有明确作用机制靶点的药物，建立药物–靶点和疾病–基因对应表。
2. 对每个药物–疾病对计算最近距离 d~c~，以及与按度匹配的随机靶点集、随机疾病基因集（不少于 1,000 次）比较得到的 z 分数。
3. 回顾性验证：以已批准适应症为正例，报告 AUROC、AUPR 及置换基线；与三种简单基线比较：药物的靶点数、靶点的平均度、靶点与疾病基因的直接重叠数。
4. 敏感性：比较最近、最短、核心、中心、分离等几种距离定义，不同的相互作用组，不同的遗传关联阈值。
5. 病例：选一种疾病，列出邻近度最高但尚未获批的药物，检索 ClinicalTrials.gov 和文献，说明哪些已有临床试验，哪些只是网络层面的假设。

**进阶方向**

- 药物组合：两种药物靶点模块之间的分离度与已知联合用药的关系（Cheng 等 2019）。
- 按治疗领域分层，看邻近度在哪些疾病领域最有用。

**注意。** 疾病基因只能用遗传关联证据（`genetic_association`），不能用 Open Targets 的综合分数——综合分数包含“已知药物”类证据（`known_drug`），会把药物靶点直接算成疾病基因，造成循环论证。未获批不等于无效，未标记的药物–疾病对不能当作阴性。网络上接近不能证明疗效。

**参考文献**

- Guney E, et al. Network-based in silico drug efficacy screening. *Nature Communications*, 2016. [doi:10.1038/ncomms10331](https://doi.org/10.1038/ncomms10331)
- Cheng F, et al. Network-based approach to prediction and population-based validation of in silico drug repurposing. *Nature Communications*, 2018. [doi:10.1038/s41467-018-05116-5](https://doi.org/10.1038/s41467-018-05116-5)
- Cheng F, et al. Network-based prediction of drug combinations. *Nature Communications*, 2019. [doi:10.1038/s41467-019-09186-x](https://doi.org/10.1038/s41467-019-09186-x)
- Morselli Gysi D, et al. Network medicine framework for identifying drug-repurposing opportunities for COVID-19. *Proceedings of the National Academy of Sciences*, 2021. [doi:10.1073/pnas.2025581118](https://doi.org/10.1073/pnas.2025581118)
- Barabási AL, et al. Network medicine: a network-based approach to human disease. *Nature Reviews Genetics*, 2011. [doi:10.1038/nrg2918](https://doi.org/10.1038/nrg2918)

### B3　人类症状–疾病网络：表型相似的疾病在分子网络上更接近吗？ {#b3 toc="B3　人类症状–疾病网络"}

**难度** ★★　**对应手册专题**：[疾病模块、网络邻近度与药物重定位](network-medicine.html)、[复杂系统与网络的数学表示](network-basics.html)

**背景与问题。** Goh 等（2007）把疾病与致病基因连成二部网络，投影后得到“人类疾病网络”。Zhou 等（2014）用文献中症状与疾病的共现构建症状–疾病网络，发现症状相似的疾病共享更多致病基因和蛋白相互作用。本题用人类表型本体（HPO）的疾病注释重复并扩展这一分析：

1. 疾病–表型二部网络有什么结构？
2. 表型相似度与共享基因、在相互作用组上的距离是否相关？
3. 按表型聚出的疾病社团与器官系统分类是否一致？

**数据**

| 数据 | 内容 | 获取 | 许可 |
|:-------|:----------------|:-----------|:-----|
| HPO 注释（v2026-09-01 版） | `phenotype.hpoa`（疾病–表型注释，疾病来自 OMIM、Orphanet 等）、`genes_to_disease.txt`、`hp.obo`（本体结构） | [github.com/…/releases](https://github.com/obophenotype/human-phenotype-ontology/releases) | 免费使用，须按 HPO 许可注明来源与版本（[hpo.jax.org/license](https://hpo.jax.org/license)） |
| STRING v12.0（人类） | 物理相互作用 | [string-db.org/cgi/download](https://string-db.org/cgi/download) | CC BY 4.0 |

**必做分析**

1. 解析 `phenotype.hpoa`：选一种疾病来源（如 OMIM），排除带 NOT 限定的注释；比较“只用直接注释”与“把注释沿本体向上传播到祖先术语”两种处理。
2. 二部网络：描述“每种疾病的表型数”和“每个表型涉及的疾病数”的分布；投影成疾病–疾病网络，比较两种边权：共享表型数，以及 TF-IDF 加权的余弦相似度（后者降低常见表型的影响）。
3. 疾病–基因：用 `genes_to_disease.txt` 计算疾病对的共享基因（Jaccard 系数）；对不共享基因的疾病对，计算它们的基因在 STRING 网络上的分离度或平均最短距离。
4. 以疾病对为单位检验表型相似度与共享基因、网络距离的关系（用 Mantel 置换检验），并按表型相似度分组作图。
5. 社团发现（Louvain 或 Leiden，多次运行检查一致性），用归一化互信息比较社团与 HPO 顶层器官系统分类，并与打乱标签的基线比较。

**进阶方向**

- 单基因病与复杂病分开分析。
- 找出“表型高度相似却没有共享基因”的疾病对，在网络上寻找连接它们的通路，作为候选的共同机制。
- 表型–表型共现网络：哪些表型连接了不同的器官系统？

**注意。** 研究得多的疾病注释的表型也多，相似度会偏高。沿本体传播后，几乎所有疾病都共享最顶层的宽泛术语，要剔除这类术语。疾病对之间不独立，不能直接用普通相关检验的 p 值。

**参考文献**

- Goh KI, et al. The human disease network. *Proceedings of the National Academy of Sciences*, 2007. [doi:10.1073/pnas.0701361104](https://doi.org/10.1073/pnas.0701361104)
- Zhou X, et al. Human symptoms–disease network. *Nature Communications*, 2014. [doi:10.1038/ncomms5212](https://doi.org/10.1038/ncomms5212)
- Gargano MA, et al. The Human Phenotype Ontology in 2024: phenotypes around the world. *Nucleic Acids Research*, 2024. [doi:10.1093/nar/gkad1005](https://doi.org/10.1093/nar/gkad1005)
- Menche J, et al. Uncovering disease-disease relationships through the incomplete interactome. *Science*, 2015. [doi:10.1126/science.1257601](https://doi.org/10.1126/science.1257601)

### B4　慢性病共病网络：基于 NHANES 的多病共存结构 {#b4 toc="B4　慢性病共病网络"}

**难度** ★　**对应手册专题**：[疾病模块、网络邻近度与药物重定位](network-medicine.html)、[网络构建与统计验证](network-construction.html)

**背景与问题。** 多种慢性病共存在中老年人中很普遍。Hidalgo 等（2009）用美国医保数据构建表型疾病网络，用相对风险（RR）和 φ 系数衡量两种疾病的共现，发现患者倾向于沿网络“移动”到与已有疾病相连的疾病。本题用美国全国健康与营养调查（NHANES）的公开数据：

1. 15–20 种常见慢性病构成怎样的共病网络？
2. 哪些疾病是枢纽或桥接节点？
3. 控制年龄之后，哪些边仍然存在？
4. 不同年龄段、不同性别的共病网络有何不同？

**数据**

| 数据 | 内容 | 获取 | 许可 |
|:-------|:----------------|:-----------|:-----|
| NHANES 2017 至 2020 年 3 月疫情前合并数据（P_ 系列文件） | `P_DEMO`（人口学）；`P_MCQ`（医生告知的哮喘、关节炎、心衰、冠心病、卒中、慢阻肺、甲状腺疾病、肝病、癌症等）；`P_DIQ`（糖尿病）；`P_BPQ`（高血压、高胆固醇）；`P_KIQ_U`（肾脏疾病）；`P_BMX`（BMI，用于定义肥胖）；`P_DPQ`（PHQ-9，≥ 10 分定义抑郁）；`P_SLQ`（睡眠） | 数据首页 [wwwn.cdc.gov/nchs/nhanes](https://wwwn.cdc.gov/nchs/nhanes/)；文件地址形如 [wwwn.cdc.gov/…/P_MCQ.xpt](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/P_MCQ.xpt) | 美国联邦政府公开数据（公有领域），需注明来源 |
| 其他周期（重复分析用） | 2011–2012、2013–2014、2015–2016 等周期的同名文件 | 同上 | 同上 |

文件为 SAS XPT 格式，Python 可用 `pandas.read_sas`，R 可用 `haven::read_xpt` 读取。

**必做分析**

1. 定义疾病：以“医生曾告知患有”为主，必要时结合测量值（如 BMI ≥ 30 为肥胖、PHQ-9 ≥ 10 为抑郁）；写清每个定义和缺失值的处理，限定 20 岁及以上成人。
2. 边权：两两计算 RR = C~ij~N / (P~i~P~j~) 和 φ 系数；用 Fisher 精确检验并做 FDR 校正，保留显著且 RR > 1 的边。
3. 年龄调整：对每对疾病做逻辑回归（疾病 i ~ 疾病 j + 年龄 + 性别），比较调整前后的网络——不少共病边可能只是因为两种病都随年龄增加。
4. 网络分析：度、强度、介数；社团结构（是否出现心血管代谢、呼吸、精神–疼痛等簇）；按年龄组（20–44、45–64、≥ 65 岁）和性别分层比较。
5. 稳健性：自助法重抽样（不少于 500 次），得到每条边的出现频率；比较加权（使用 NHANES 抽样权重）与不加权的估计。

**进阶方向**

- 与 B1 联动：比较共病强度与两种疾病的疾病模块在相互作用组上的分离度。
- 按家庭收入与贫困线之比（PIR）等社会经济因素分层。
- 用多个周期比较共病结构随时间的变化。

**注意。** 自报诊断有回忆偏倚，也受就医机会影响；横断面数据不能判断疾病发生的先后；患病率很低的疾病 RR 不稳定；φ 系数受患病率影响，RR 和 φ 各有偏差，要同时报告。

**参考文献**

- Hidalgo CA, et al. A Dynamic Network Approach for the Study of Human Phenotypes. *PLoS Computational Biology*, 2009. [doi:10.1371/journal.pcbi.1000353](https://doi.org/10.1371/journal.pcbi.1000353)
- Jensen AB, et al. Temporal disease trajectories condensed from population-wide registry data covering 6.2 million patients. *Nature Communications*, 2014. [doi:10.1038/ncomms5022](https://doi.org/10.1038/ncomms5022)
- Barabási AL, et al. Network medicine: a network-based approach to human disease. *Nature Reviews Genetics*, 2011. [doi:10.1038/nrg2918](https://doi.org/10.1038/nrg2918)
- Kroenke K, et al. The PHQ-9: Validity of a brief depression severity measure. *Journal of General Internal Medicine*, 2001. [doi:10.1046/j.1525-1497.2001.016009606.x](https://doi.org/10.1046/j.1525-1497.2001.016009606.x)

## C　症状网络 {#group-c}

### C1　抑郁症状网络的性别差异与跨时期稳定性 {#c1 toc="C1　抑郁症状网络的性别差异与跨时期稳定性"}

**难度** ★　**对应手册专题**：[症状网络与网络精神病学](symptom-networks.html)

**背景与问题。** 网络理论认为，精神障碍不是由一个潜在病因引起的一组症状，而是症状之间相互作用形成的系统（Borsboom 2017）。在横断面数据上估计的症状网络常被用来寻找“中心症状”，但中心性能否解释为干预靶点存在争议（Bringmann 等 2019），网络估计的稳定性也需要检验（Epskamp 等 2018）。NHANES 从 2005 年起每个周期都用 PHQ-9 筛查抑郁，样本量大且公开。本题：

1. 男性和女性的 PHQ-9 症状网络是否不同？
2. 网络结构在 2005–2023 年间（包括新冠疫情前后）是否稳定？
3. 中心性估计是否可靠？

**数据**

| 数据 | 内容 | 获取 | 许可 |
|:-------|:----------------|:-----------|:-----|
| NHANES 抑郁筛查问卷（DPQ） | 9 个条目（各 0–3 分）；周期从 2005–2006（`DPQ_D`）到 2017–2018（`DPQ_J`），以及 2017 至 2020 年 3 月（`P_DPQ`）、2021–2023（`DPQ_L`）；按受访者编号 SEQN 合并人口学文件 DEMO | 文件地址形如 [wwwn.cdc.gov/…/DPQ_L.xpt](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/DPQ_L.xpt) | 公有领域 |
| 手册起步数据 | [`nhanes_phq9_2017_2018.csv`](data/nhanes_phq9_2017_2018.csv)（九个条目都有效的 5,068 名受访者，含性别、年龄） | [数据说明页](data-sources.html) | 公有领域 |

`P_DPQ` 已包含 2017–2018 周期的受访者，不要与 `DPQ_J` 重复使用。

**必做分析**

1. 合并多个周期，描述各条目的均值、方差和偏度（一般人群中多数人得 0 分）。
2. 网络估计：用多分类相关（polychoric）加 EBICglasso 估计正则化偏相关网络（R 包 bootnet、qgraph）；再把条目二值化，用 Ising 模型估计，比较两种方法得到的结构。
3. 稳定性：非参数自助法给出边权的置信区间；逐步删除样本，得到中心性稳定性系数 CS（≥ 0.5 才适合解释）。
4. 组间比较：用网络比较检验（NCT）比较男女的整体连接强度、网络结构和单条边；再比较两个时期（如 2017–2018 与 2021–2023）。
5. 讨论：两组条目方差不同可能造成边权差异（Terluin 等 2016）；中心性高能否说明该症状“驱动”了其他症状。

**进阶方向**

- 可预测性：每个症状能被其余症状解释的方差比例（R 包 mgm）。
- 桥接中心性：躯体症状（睡眠、疲乏、食欲）与认知–情感症状之间的桥接节点。
- 演示 Berkson 偏倚：只在 PHQ-9 ≥ 10 的子样本中建网，观察负边的出现（de Ron 等 2021）。
- 抽样权重对网络估计的影响。

**注意。** 横断面的组水平网络不能说明个体内部症状之间的因果；第 9 条（自杀意念）阳性率很低，相关的边不稳定；多次组间比较要做校正。

**参考文献**

- Borsboom D. A network theory of mental disorders. *World Psychiatry*, 2017. [doi:10.1002/wps.20375](https://doi.org/10.1002/wps.20375)
- Epskamp S, et al. Estimating psychological networks and their accuracy: A tutorial paper. *Behavior Research Methods*, 2018. [doi:10.3758/s13428-017-0862-1](https://doi.org/10.3758/s13428-017-0862-1)
- Epskamp S, Fried EI. A tutorial on regularized partial correlation networks. *Psychological Methods*, 2018. [doi:10.1037/met0000167](https://doi.org/10.1037/met0000167)
- van Borkulo CD, et al. Comparing network structures on three aspects: A permutation test. *Psychological Methods*, 2023. [doi:10.1037/met0000476](https://doi.org/10.1037/met0000476)
- Bringmann LF, et al. What do centrality measures measure in psychological networks? *Journal of Abnormal Psychology*, 2019. [doi:10.1037/abn0000446](https://doi.org/10.1037/abn0000446)
- Fried EI, Nesse RM. Depression sum-scores don’t add up: why analyzing specific depression symptoms is essential. *BMC Medicine*, 2015. [doi:10.1186/s12916-015-0325-4](https://doi.org/10.1186/s12916-015-0325-4)
- Terluin B, et al. Differences in Connection Strength between Mental Symptoms Might Be Explained by Differences in Variance: Reanalysis of Network Data Did Not Confirm Staging. *PLOS ONE*, 2016. [doi:10.1371/journal.pone.0155205](https://doi.org/10.1371/journal.pone.0155205)
- Haslbeck JMB, Waldorp LJ. How well do network models predict observations? On the importance of predictability in network models. *Behavior Research Methods*, 2018. [doi:10.3758/s13428-017-0910-x](https://doi.org/10.3758/s13428-017-0910-x)
- Jones PJ, et al. Bridge Centrality: A Network Approach to Understanding Comorbidity. *Multivariate Behavioral Research*, 2021. [doi:10.1080/00273171.2019.1614898](https://doi.org/10.1080/00273171.2019.1614898)
- de Ron J, et al. Psychological networks in clinical populations: investigating the consequences of Berkson's bias. *Psychological Medicine*, 2021. [doi:10.1017/S0033291719003209](https://doi.org/10.1017/S0033291719003209)

## D　脑网络 {#group-d}

### D1　结构连接能在多大程度上解释功能连接？结构–功能耦合的个体与区域差异 {#d1 toc="D1　结构–功能耦合"}

**难度** ★★　**对应手册专题**：[脑连接组：结构与功能连接](brain-connectome.html)、[网络结构指标与随机图](network-metrics.html)

**背景与问题。** 静息态功能连接（FC）受白质结构连接（SC）约束，但不由它决定：直接的结构连接只能解释一部分 FC（Honey 等 2009），用最短路径、搜索信息、可通信性等“通讯模型”作为预测因子能解释更多（Goñi 等 2014）。耦合强度在皮层上呈梯度分布：初级感觉运动区强，跨模态联合皮层弱（Vázquez-Rodríguez 等 2019；Baum 等 2020）。本题用 70 名健康青年的公开连接组：

1. SC 及其通讯指标能解释多少 FC？是否超出空间距离本身的解释？
2. 区域耦合是否按功能系统分层？
3. 一个人自己的 SC 是否比别人的 SC 更能预测他自己的 FC？

**数据**

| 数据 | 内容 | 获取 | 许可 |
|:-------|:----------------|:-----------|:-----|
| Lausanne 个体连接组 | 70 名健康青年的 DSI 结构连接（纤维密度、纤维长度）与静息态 FC，Lausanne 图谱多个尺度（最粗为 68 个皮层区） | Zenodo，doi:10.5281/zenodo.2872624（`Individual_Connectomes.mat`，701 MB） | CC BY 4.0 |
| Lausanne 组水平一致性连接组 | 组水平 SC、FC、脑区坐标与静息态网络标签 | Zenodo，doi:10.5281/zenodo.3067849（10.7 MB） | CC BY 4.0 |
| 手册起步数据 | [`lausanne68_sc_fc.csv`](data/lausanne68_sc_fc.csv)（69 名被试的 SC 和 FC，68 区，上三角向量）与 [`lausanne68_nodes.csv`](data/lausanne68_nodes.csv)；`lausanne114_*`（114 区组水平连接） | [数据说明页](data-sources.html) | CC BY 4.0 |

**必做分析**

1. SC 网络描述：密度、度分布、聚类系数与特征路径长度，与保度随机网络以及保留边长分布的空间零模型比较；富人俱乐部系数（相对随机网络归一化）。
2. 全局耦合：每名被试计算 SC 非零边上 SC 与 FC 的相关；以脑区间欧氏距离为基线，逐步加入最短路径长度、搜索信息、可通信性等预测因子，报告多元回归 R² 的增量。
3. 区域耦合：对每个脑区，用它与其余脑区的 SC 衍生指标回归它的 FC 行，得到 68 个脑区的耦合 R²，按静息态网络比较。
4. 零模型：用 SC 的保度重连检验预测能力是否依赖真实拓扑；区域耦合图与其他脑图的相关，要用保留空间自相关的零模型（旋转检验或 BrainSMASH）。
5. 个体特异性：用被试 i 的 SC 预测被试 j 的 FC，得到 69 × 69 的预测矩阵，检验对角线（自己预测自己）是否高于非对角线。

**进阶方向**

- 在 114 区或更细的尺度上重复，检验结论对分区尺度的依赖。
- 在结构网络上运行扩散或 Kuramoto 模型模拟 FC，与观测 FC 比较。
- 比较二值与加权网络、不同纤维密度归一化方式的结果。

**注意。** 空间上相邻的脑区 FC 高、SC 也多，必须把欧氏距离作为基线预测因子；SC 很稀疏，直接连接只覆盖一部分脑区对；数据只有 69 人、来自单一中心，推广结论要谨慎。

**参考文献**

- Honey CJ, et al. Predicting human resting-state functional connectivity from structural connectivity. *Proceedings of the National Academy of Sciences*, 2009. [doi:10.1073/pnas.0811168106](https://doi.org/10.1073/pnas.0811168106)
- Goñi J, et al. Resting-brain functional connectivity predicted by analytic measures of network communication. *Proceedings of the National Academy of Sciences*, 2014. [doi:10.1073/pnas.1315529111](https://doi.org/10.1073/pnas.1315529111)
- Vázquez-Rodríguez B, et al. Gradients of structure–function tethering across neocortex. *Proceedings of the National Academy of Sciences*, 2019. [doi:10.1073/pnas.1903403116](https://doi.org/10.1073/pnas.1903403116)
- Baum GL, et al. Development of structure–function coupling in human brain networks during youth. *Proceedings of the National Academy of Sciences*, 2020. [doi:10.1073/pnas.1912034117](https://doi.org/10.1073/pnas.1912034117)
- van den Heuvel MP, Sporns O. Rich-Club Organization of the Human Connectome. *The Journal of Neuroscience*, 2011. [doi:10.1523/JNEUROSCI.3539-11.2011](https://doi.org/10.1523/JNEUROSCI.3539-11.2011)
- Colizza V, et al. Detecting rich-club ordering in complex networks. *Nature Physics*, 2006. [doi:10.1038/nphys209](https://doi.org/10.1038/nphys209)
- Roberts JA, et al. The contribution of geometry to the human connectome. *NeuroImage*, 2016. [doi:10.1016/j.neuroimage.2015.09.009](https://doi.org/10.1016/j.neuroimage.2015.09.009)
- Markello RD, Misic B. Comparing spatial null models for brain maps. *NeuroImage*, 2021. [doi:10.1016/j.neuroimage.2021.118052](https://doi.org/10.1016/j.neuroimage.2021.118052)

### D2　疾病相关的皮层厚度改变是否沿结构连接组分布？跨疾病比较 {#d2 toc="D2　疾病皮层改变是否沿连接组分布"}

**难度** ★★　**对应手册专题**：[脑连接组：结构与功能连接](brain-connectome.html)、[网络上的传播与免疫](spreading.html)、[网络鲁棒性、渗流与级联失效](robustness.html)

**背景与问题。** 许多神经和精神疾病的灰质改变并不是随机分布的：枢纽脑区更容易受累（Crossley 等 2014）；一个脑区的萎缩程度与它的结构连接邻居的萎缩程度相关，提示病理可能沿连接传播，或者网络位置决定了易损性（Zhou 等 2012；Shafiei 等 2020）。ENIGMA 联盟公开了多种疾病大样本病例–对照研究的皮层厚度效应量，ENIGMA Toolbox 还提供健康成人的结构和功能连接矩阵（Larivière 等 2021）。本题：

1. 各种疾病的皮层厚度改变是否在枢纽脑区更大？
2. 是否与结构连接邻居的改变相关？
3. 这些关系能否超出空间自相关的解释？
4. 哪些疾病有相似的网络模式？

**数据**

| 数据 | 内容 | 获取 | 许可 |
|:-------|:----------------|:-----------|:-----|
| ENIGMA Toolbox | 多种疾病的病例–对照汇总统计（Desikan–Killiany 图谱 68 个皮层区的 Cohen's d），包括 22q11.2 缺失综合征、ADHD、孤独症、双相障碍、癫痫、重性抑郁、强迫症、精神分裂症等；HCP 健康成人的组水平 SC 与 FC 矩阵；内置旋转检验、枢纽易损性和震中分析函数 | `pip install enigmatoolbox`；文档 [enigma-toolbox.readthedocs.io](https://enigma-toolbox.readthedocs.io) | 工具箱 BSD-3-Clause；汇总统计须引用对应的 ENIGMA 原始论文（文档中逐表列出） |
| Lausanne 连接组（重复验证用） | 68 区 Desikan–Killiany 皮层分区的独立 DSI 结构连接（见 D1） | 见 D1 | CC BY 4.0 |

**必做分析**

1. 读取至少三种疾病的皮层厚度 Cohen's d，以及 HCP 的 SC 和 FC。
2. 枢纽易损性：脑区加权度（强度）与 d 的相关，用 1,000 次旋转检验得到 p~spin~。
3. 邻域模型：每个脑区“按结构连接加权的邻居平均改变”与该脑区自身改变的相关；用 FC 重复；再以欧氏距离加权的邻居作为对照，区分网络效应和空间邻近效应。
4. 震中：计算每个脑区的连接谱与疾病改变图的相关，找出可能的震中。
5. 跨疾病：计算疾病之间改变图的相关矩阵（同样用旋转检验），做层次聚类，讨论共享的网络模式。

**进阶方向**

- 网络扩散模型：从震中出发在 SC 上模拟扩散，与观测改变图比较，并与随机起点比较（Raj 等 2012）。
- 用 Lausanne 的 SC 重复主要结果，检验对连接组来源的依赖（注意核对两套数据的脑区顺序）。
- 比较成人与儿童/青少年的汇总统计。

**注意。** 汇总统计已由原研究做了年龄、性别、颅内体积等校正，各疾病的校正方式不同，要查阅原文；任意两张平滑的脑图都容易显得“相关”，所以必须用空间零模型；横断面效应量不能证明病理在“传播”。

**参考文献**

- Larivière S, et al. The ENIGMA Toolbox: multiscale neural contextualization of multisite neuroimaging datasets. *Nature Methods*, 2021. [doi:10.1038/s41592-021-01186-4](https://doi.org/10.1038/s41592-021-01186-4)
- Hettwer MD, et al. Coordinated cortical thickness alterations across six neurodevelopmental and psychiatric disorders. *Nature Communications*, 2022. [doi:10.1038/s41467-022-34367-6](https://doi.org/10.1038/s41467-022-34367-6)
- Crossley NA, et al. The hubs of the human connectome are generally implicated in the anatomy of brain disorders. *Brain*, 2014. [doi:10.1093/brain/awu132](https://doi.org/10.1093/brain/awu132)
- Zhou J, et al. Predicting Regional Neurodegeneration from the Healthy Brain Functional Connectome. *Neuron*, 2012. [doi:10.1016/j.neuron.2012.03.004](https://doi.org/10.1016/j.neuron.2012.03.004)
- Raj A, et al. A Network Diffusion Model of Disease Progression in Dementia. *Neuron*, 2012. [doi:10.1016/j.neuron.2011.12.040](https://doi.org/10.1016/j.neuron.2011.12.040)
- Shafiei G, et al. Spatial Patterning of Tissue Volume Loss in Schizophrenia Reflects Brain Network Architecture. *Biological Psychiatry*, 2020. [doi:10.1016/j.biopsych.2019.09.031](https://doi.org/10.1016/j.biopsych.2019.09.031)
- Alexander-Bloch AF, et al. On testing for spatial correspondence between maps of human brain structure and function. *NeuroImage*, 2018. [doi:10.1016/j.neuroimage.2018.05.070](https://doi.org/10.1016/j.neuroimage.2018.05.070)

### D3　孤独症功能连接组的组间差异有多稳健？多站点数据中的分析选择 {#d3 toc="D3　孤独症功能连接组差异的稳健性"}

**难度** ★★★　**对应手册专题**：[脑连接组：结构与功能连接](brain-connectome.html)、[网络构建与统计验证](network-construction.html)、[研究问题、可复现分析与敏感性分析](reproducible-research.html)

**背景与问题。** 孤独症谱系障碍（ASD）的功能连接研究既有“连接不足”也有“连接过度”的报告，结果不一致。图论指标对分析选择很敏感：脑图谱、是否回归全局信号、阈值方法（比例阈值、绝对阈值或保留全部加权边）、头动处理（van den Heuvel 等 2017；Hallquist 与 Hillary 2019）。同一份数据由不同团队分析，结论也会不同（Botvinik-Nezer 等 2020）。本题用 ABIDE I 的预处理数据做“多元宇宙分析”：

1. ASD 与典型发育对照在全局图论指标上的差异，在多种合理的分析流程中方向和大小是否一致？
2. 差异有多少可以由头动和站点解释？

**数据**

| 数据 | 内容 | 获取 | 许可 |
|:-------|:----------------|:-----------|:-----|
| ABIDE Preprocessed（Preprocessed Connectomes Project） | ABIDE I 共 1,112 人（ASD 539、对照 573），来自多个国际站点；提供 CCS、CPAC、DPARSF、NIAK 等预处理流程，每种流程又分是否滤波、是否回归全局信号；有 AAL、CC200、CC400、Harvard–Oxford 等图谱的脑区时间序列，以及表型表（诊断、年龄、性别、站点、平均帧位移 FD、质控评分） | [preprocessed-connectomes-project.org/…/abide](http://preprocessed-connectomes-project.org/abide/)；可用 `nilearn.datasets.fetch_abide_pcp` 下载，或从 Amazon S3 按文件下载（时间序列是小文本文件） | 遵守 ABIDE 数据使用条款（非商业用途），引用 Di Martino 等（2014）与 Craddock 等（2013） |

**必做分析**

1. 纳入标准：通过质控、平均 FD < 0.2 mm（或其他有依据的阈值）、限定年龄范围；报告最终各站点的 ASD 与对照人数。
2. 多元宇宙：至少 2 种图谱 × 是否回归全局信号 × 3 种阈值方法（比例阈值取多个密度、绝对阈值、加权全连接），计算全局效率、平均聚类系数、模块度等指标。
3. 组间比较：线性模型“指标 ~ 诊断 + 年龄 + 性别 + 平均 FD + 站点”，或者先用 ComBat 校正站点效应；报告每条流程的效应量（Cohen's d）及置信区间，画“多元宇宙图”展示方向和大小是否一致。
4. 边层面：在 1–2 条流程中用网络统计方法（NBS，置换不少于 5,000 次）找出组间差异子网络，比较不同流程得到的子网络的重叠程度。
5. 头动：各指标与平均 FD 的相关；按头动匹配两组后，结果怎样变化。

**进阶方向**

- 分类：以 FC 为特征，比较随机交叉验证与留站点交叉验证的准确率，讨论“站点泄漏”。
- 年龄交互：儿童、青少年和成人分开分析。

**注意。** 在比例阈值下，平均 FC 较弱的一组会被迫纳入更多弱边（噪声），使拓扑指标出现虚假差异；负相关边的处理要说明；各站点的诊断比例不平衡，会与诊断混杂。

**参考文献**

- Di Martino A, et al. The autism brain imaging data exchange: towards a large-scale evaluation of the intrinsic brain architecture in autism. *Molecular Psychiatry*, 2014. [doi:10.1038/mp.2013.78](https://doi.org/10.1038/mp.2013.78)
- Craddock C, et al. The Neuro Bureau Preprocessing Initiative: open sharing of preprocessed neuroimaging data and derivatives. *Frontiers in Neuroinformatics*（会议摘要）, 2013. [doi:10.3389/conf.fninf.2013.09.00041](https://doi.org/10.3389/conf.fninf.2013.09.00041)
- Zalesky A, et al. Network-based statistic: Identifying differences in brain networks. *NeuroImage*, 2010. [doi:10.1016/j.neuroimage.2010.06.041](https://doi.org/10.1016/j.neuroimage.2010.06.041)
- van Wijk BCM, et al. Comparing Brain Networks of Different Size and Connectivity Density Using Graph Theory. *PLoS ONE*, 2010. [doi:10.1371/journal.pone.0013701](https://doi.org/10.1371/journal.pone.0013701)
- van den Heuvel MP, et al. Proportional thresholding in resting-state fMRI functional connectivity networks and consequences for patient-control connectome studies: Issues and recommendations. *NeuroImage*, 2017. [doi:10.1016/j.neuroimage.2017.02.005](https://doi.org/10.1016/j.neuroimage.2017.02.005)
- Yu M, et al. Statistical harmonization corrects site effects in functional connectivity measurements from multi‐site fMRI data. *Human Brain Mapping*, 2018. [doi:10.1002/hbm.24241](https://doi.org/10.1002/hbm.24241)
- Botvinik-Nezer R, et al. Variability in the analysis of a single neuroimaging dataset by many teams. *Nature*, 2020. [doi:10.1038/s41586-020-2314-9](https://doi.org/10.1038/s41586-020-2314-9)
- Hallquist MN, Hillary FG. Graph theory approaches to functional network organization in brain disorders: A critique for a brave new small-world. *Network Neuroscience*, 2019. [doi:10.1162/netn_a_00054](https://doi.org/10.1162/netn_a_00054)
- Van Dijk KRA, et al. The influence of head motion on intrinsic functional connectivity MRI. *NeuroImage*, 2012. [doi:10.1016/j.neuroimage.2011.07.044](https://doi.org/10.1016/j.neuroimage.2011.07.044)

### D4　动态功能连接是真实的吗？用代用数据检验儿童与成人的“连接状态” {#d4 toc="D4　动态功能连接与代用数据检验"}

**难度** ★★★　**对应手册专题**：[动态功能连接与多层脑网络](dynamic-brain-networks.html)

**背景与问题。** 滑动窗口功能连接显示，脑网络在若干反复出现的“连接状态”之间转换（Allen 等 2014）。但即使信号本身是平稳的，有限长窗口内的相关系数也会因抽样误差而波动（Hindriks 等 2016；Liégeois 等 2017），所以需要用保留静态特性的代用数据来检验，观察到的动态是否超出随机波动。本题用儿童和成人观看动画短片时的 fMRI：

1. 滑动窗口 FC 的波动是否显著大于平稳代用数据？
2. 儿童与成人的连接状态（占比、驻留时间、转换概率）有何差异？差异能否由头动解释？

**数据**

| 数据 | 内容 | 获取 | 许可 |
|:-------|:----------------|:-----------|:-----|
| nilearn 发育 fMRI 数据（OpenNeuro ds000228） | 155 名被试（3–12 岁儿童 122 名、成人 33 名）观看一部动画短片时的 fMRI，已用 fMRIPrep 预处理并降采样到 4 mm；附混杂变量表和表型信息 | `nilearn.datasets.fetch_development_fmri`（可指定被试数，分批下载）；原始数据 [openneuro.org/datasets/ds000228](https://openneuro.org/datasets/ds000228) | CC0 |
| 脑图谱 | MSDL 概率图谱（39 区）或 Schaefer 2018 图谱（100 或 200 区） | `nilearn.datasets.fetch_atlas_msdl`、`fetch_atlas_schaefer_2018` | 见各图谱说明 |

**必做分析**

1. 提取脑区时间序列（回归头动等混杂变量，带通滤波），计算每名被试的静态 FC。
2. 滑动窗口 FC（窗长 30–60 s，至少比较两种窗长），把所有窗口的连接矩阵做 k-means 聚类得到连接状态（说明 k 的选择依据），计算每名被试的状态占比、平均驻留时间和状态转换概率矩阵。
3. 代用数据：为每名被试生成保留各脑区功率谱和脑区间互谱的多变量相位随机化代用数据（也可以拟合多元自回归模型生成），重复整个流程；比较真实数据与代用数据的 FC 时间变异度和聚类质量。
4. 儿童与成人比较：状态指标的组间差异，以平均 FD 为协变量，或按头动匹配样本。
5. 每个窗口计算模块度和全局效率，得到拓扑指标的时间序列，比较两组的变异程度。

**进阶方向**

- 被试间功能连接（ISFC）：提取由影片驱动的共同信号，比较儿童与成人的刺激驱动连接。
- 时间多层网络的社团检测，计算各脑区的“灵活性”（Bassett 等 2011）。

**注意。** 儿童头动明显大于成人，必须控制；k-means 的结果对初始化敏感，要多次运行；观影任务中的连接波动有一部分由刺激驱动，解释时与静息态不同。

**参考文献**

- Allen EA, et al. Tracking Whole-Brain Connectivity Dynamics in the Resting State. *Cerebral Cortex*, 2014. [doi:10.1093/cercor/bhs352](https://doi.org/10.1093/cercor/bhs352)
- Hindriks R, et al. Can sliding-window correlations reveal dynamic functional connectivity in resting-state fMRI? *NeuroImage*, 2016. [doi:10.1016/j.neuroimage.2015.11.055](https://doi.org/10.1016/j.neuroimage.2015.11.055)
- Liégeois R, et al. Interpreting temporal fluctuations in resting-state functional connectivity MRI. *NeuroImage*, 2017. [doi:10.1016/j.neuroimage.2017.09.012](https://doi.org/10.1016/j.neuroimage.2017.09.012)
- Richardson H, et al. Development of the social brain from age three to twelve years. *Nature Communications*, 2018. [doi:10.1038/s41467-018-03399-2](https://doi.org/10.1038/s41467-018-03399-2)
- Van Dijk KRA, et al. The influence of head motion on intrinsic functional connectivity MRI. *NeuroImage*, 2012. [doi:10.1016/j.neuroimage.2011.07.044](https://doi.org/10.1016/j.neuroimage.2011.07.044)
- Bassett DS, et al. Dynamic reconfiguration of human brain networks during learning. *Proceedings of the National Academy of Sciences*, 2011. [doi:10.1073/pnas.1018985108](https://doi.org/10.1073/pnas.1018985108)
- Schaefer A, et al. Local-Global Parcellation of the Human Cerebral Cortex from Intrinsic Functional Connectivity MRI. *Cerebral Cortex*, 2018. [doi:10.1093/cercor/bhx179](https://doi.org/10.1093/cercor/bhx179)

### D5　头皮脑电的同步网络：从睁眼–闭眼到癫痫发作 {#d5 toc="D5　头皮脑电的同步网络"}

**难度** A 部分 ★，B 部分 ★★★　**对应手册专题**：[同步与协同动力学](synchronization.html)、[脑连接组：结构与功能连接](brain-connectome.html)

**背景与问题。** 闭眼时枕区 alpha 节律增强，是最经典的脑电现象之一（Barry 等 2007）。用头皮脑电构建功能网络时，容积传导会让相邻电极出现零相位滞后的虚假同步，相位滞后指数（PLI）及其加权形式（wPLI）可以减轻这一问题（Stam 等 2007；Vinck 等 2011）。癫痫发作中，脑网络的同步程度随时间演化，发作开始时下降，接近结束时升高（Schindler 等 2007；Kramer 等 2010）。本题二选一：

- **A.** 睁眼和闭眼静息态的 alpha 同步网络有何差异？结论是否依赖同步指标（PLV 还是 wPLI）？是否超过相位随机化代用数据？
- **B.** 癫痫发作前、发作中、发作后，同步程度和网络拓扑怎样演化？不同患者、不同发作之间是否一致？

**数据**

| 数据 | 内容 | 获取 | 许可 |
|:-------|:----------------|:-----------|:-----|
| PhysioNet EEG Motor Movement/Imagery（A 用） | 109 名被试，64 导，160 Hz；每人 1 分钟睁眼基线（R01）和 1 分钟闭眼基线（R02），EDF 格式；全库 3.4 GB，只需下载 R01、R02 | [physionet.org/content/eegmmidb/1.0.0](https://physionet.org/content/eegmmidb/1.0.0/) | ODC-By 1.0 |
| CHB-MIT 头皮脑电数据库（B 用） | 22 名药物难治性癫痫儿童的 23 例记录，256 Hz，多数为 23 导（10-20 系统双极导联），标注发作起止时间；全库 42.6 GB，按各患者的 summary 文件只下载含发作的记录 | [physionet.org/content/chbmit/1.0.0](https://physionet.org/content/chbmit/1.0.0/) | ODC-By 1.0 |
| 手册起步数据 | [`eeg_eyes_open_closed.csv`](data/eeg_eyes_open_closed.csv)（6 名被试、19 导，睁眼和闭眼各 1 分钟，降采样到 80 Hz） | [数据说明页](data-sources.html) | ODC-By 1.0 |

**必做分析（A）**

1. 预处理：选定参考方式（平均参考或表面拉普拉斯），带通滤波到 delta、theta、alpha、beta 频段，切成 2–4 s 的段。
2. 每个频段计算 PLV 和 wPLI（或相干的虚部），得到睁眼、闭眼的连接矩阵。
3. 零模型：用相位随机化代用数据确定每条边的显著性阈值；全局指标（平均同步强度、聚类系数、路径长度）与同密度随机网络比较。
4. 109 人配对比较睁眼与闭眼，边层面用 NBS 或 FDR 校正。
5. 用 alpha 频段的 Hilbert 相位计算 Kuramoto 序参量 R(t)，比较两种条件下的分布；讨论 PLV 与 wPLI 结论不同的原因。

**必做分析（B）**

1. 选至少 5 名患者、10 次发作，每次发作取发作前、发作中、发作后各一段，并匹配一段远离发作的发作间期对照。
2. 用 1–2 s 的滑动窗口计算相关或 wPLI 网络，按发作时长把时间轴归一化。
3. 计算同步程度（平均连接强度、相关矩阵最大特征值）和拓扑指标（聚类系数、全局效率、模块度）的时间曲线。
4. 统计：用以患者为随机效应的混合模型比较各阶段；用代用数据检验发作期的同步是否超过随机。
5. 讨论患者之间的异质性，以及双极导联对空间解释的限制。

**进阶方向**

- 用 MNE-Python 做源空间重建后再建网络，与头皮层面的结果比较。
- 在估计出的网络上运行 Kuramoto 模型，改变耦合强度，与观测到的同步比较。

**注意。** 容积传导和参考电极会显著影响结果；肌电和眼电伪迹（发作期尤其严重）要处理或说明；窗长要与所分析的频段匹配。

**参考文献**

- Barry RJ, et al. EEG differences between eyes-closed and eyes-open resting conditions. *Clinical Neurophysiology*, 2007. [doi:10.1016/j.clinph.2007.07.028](https://doi.org/10.1016/j.clinph.2007.07.028)
- Stam CJ, et al. Phase lag index: Assessment of functional connectivity from multi channel EEG and MEG with diminished bias from common sources. *Human Brain Mapping*, 2007. [doi:10.1002/hbm.20346](https://doi.org/10.1002/hbm.20346)
- Vinck M, et al. An improved index of phase-synchronization for electrophysiological data in the presence of volume-conduction, noise and sample-size bias. *NeuroImage*, 2011. [doi:10.1016/j.neuroimage.2011.01.055](https://doi.org/10.1016/j.neuroimage.2011.01.055)
- Theiler J, et al. Testing for nonlinearity in time series: the method of surrogate data. *Physica D: Nonlinear Phenomena*, 1992. [doi:10.1016/0167-2789(92)90102-S](https://doi.org/10.1016/0167-2789(92)90102-S)
- Acebrón JA, et al. The Kuramoto model: A simple paradigm for synchronization phenomena. *Reviews of Modern Physics*, 2005. [doi:10.1103/RevModPhys.77.137](https://doi.org/10.1103/RevModPhys.77.137)
- Schindler K, et al. Assessing seizure dynamics by analysing the correlation structure of multichannel intracranial EEG. *Brain*, 2007. [doi:10.1093/brain/awl304](https://doi.org/10.1093/brain/awl304)
- Kramer MA, et al. Coalescence and Fragmentation of Cortical Networks during Focal Seizures. *The Journal of Neuroscience*, 2010. [doi:10.1523/JNEUROSCI.6309-09.2010](https://doi.org/10.1523/JNEUROSCI.6309-09.2010)
- Schalk G, et al. BCI2000: A General-Purpose Brain-Computer Interface (BCI) System. *IEEE Transactions on Biomedical Engineering*, 2004. [doi:10.1109/TBME.2004.827072](https://doi.org/10.1109/TBME.2004.827072)
- Goldberger AL, et al. PhysioBank, PhysioToolkit, and PhysioNet: Components of a New Research Resource for Complex Physiologic Signals. *Circulation*, 2000. [doi:10.1161/01.CIR.101.23.e215](https://doi.org/10.1161/01.CIR.101.23.e215)

## E　网络动力学与控制 {#group-e}

### E1　医院病房接触网络上的院内传播与免疫策略 {#e1 toc="E1　医院病房接触网络上的传播与免疫"}

**难度** ★　**对应手册专题**：[网络上的传播与免疫](spreading.html)

**背景与问题。** Vanhems 等（2013）用可穿戴近距离传感器，记录了法国里昂一家医院病房 4 天内人员之间的面对面接触。真实的接触网络随时间变化：接触成簇出现，有日内节律，这些时间结构会改变传播的速度和规模（Holme 与 Saramäki 2012）。本题：

1. 不同角色（医生、护士、行政人员、患者）在传播中的作用有何不同？
2. 用时间网络模拟，与用聚合静态网络、时间打乱网络模拟，结果相差多少？
3. 疫苗数量有限时，哪种免疫策略最有效？

**数据**

| 数据 | 内容 | 获取 | 许可 |
|:-------|:----------------|:-----------|:-----|
| SocioPatterns 医院病房动态接触网络 | 75 人（患者 29、护士 27、医生 11、行政人员 8），约 4 天，20 秒分辨率，32,424 条接触记录 | [www.sociopatterns.org/…/hospital-ward-dynamic-contact-network](http://www.sociopatterns.org/datasets/hospital-ward-dynamic-contact-network/) | CC BY-NC-SA 3.0 |
| SocioPatterns 其他数据（重复验证用） | 小学、办公室等场所的接触数据 | [www.sociopatterns.org/datasets](http://www.sociopatterns.org/datasets/) | 见各数据页（多为 CC BY-NC-SA） |
| 手册起步数据 | [`hospital_lyon_contacts.tsv`](data/hospital_lyon_contacts.tsv)（原始数据，未删减） | [数据说明页](data-sources.html) | CC BY-NC-SA 3.0 |

**必做分析**

1. 描述：按角色的接触矩阵（次数和总时长）、日内节律、接触持续时间与接触间隔的分布（是否重尾、爆发性有多强）。
2. 聚合静态网络：度、强度、介数，按角色比较；社团结构与角色的对应关系。
3. 时间网络上的 SIR（或 SEIR）模拟：以 20 秒为步长，每次接触以概率 β 传播，恢复期以天计；数据只有 4 天，要说明循环使用数据的假设；以每个人为首发者各模拟至少 500 次，比较不同角色作为首发者时的平均爆发规模。
4. 零模型：时间打乱（保留每对人的接触次数，随机分配接触时间）、全部时间戳随机化、加权聚合静态网络，比较爆发规模和速度，判断时间结构的作用。
5. 免疫策略：固定免疫人数 k（如 5、10、15），比较随机免疫、按角色免疫、按度免疫、按接触总时长免疫、熟人免疫（Cohen 等 2003），以及“只用第 1 天的数据选人、在之后几天评估效果”这种更现实的策略。

**进阶方向**

- 在小学或办公室数据上重复，比较不同场所的最优策略。
- 分析患者之间经医护人员的间接传播路径（时间可达性）。
- 参数扫描：画出爆发规模随 β 和恢复期变化的相图。

**注意。** 数据只覆盖病房内，且只有 4 天；参数要参考具体病原体（如流感）并做敏感性分析；75 人的小网络随机波动大，需要大量重复模拟并报告区间。

**参考文献**

- Vanhems P, et al. Estimating Potential Infection Transmission Routes in Hospital Wards Using Wearable Proximity Sensors. *PLoS ONE*, 2013. [doi:10.1371/journal.pone.0073970](https://doi.org/10.1371/journal.pone.0073970)
- Holme P, Saramäki J. Temporal networks. *Physics Reports*, 2012. [doi:10.1016/j.physrep.2012.03.001](https://doi.org/10.1016/j.physrep.2012.03.001)
- Pastor-Satorras R, et al. Epidemic processes in complex networks. *Reviews of Modern Physics*, 2015. [doi:10.1103/RevModPhys.87.925](https://doi.org/10.1103/RevModPhys.87.925)
- Pastor-Satorras R, Vespignani A. Immunization of complex networks. *Physical Review E*, 2002. [doi:10.1103/PhysRevE.65.036104](https://doi.org/10.1103/PhysRevE.65.036104)
- Cohen R, et al. Efficient Immunization Strategies for Computer Networks and Populations. *Physical Review Letters*, 2003. [doi:10.1103/PhysRevLett.91.247901](https://doi.org/10.1103/PhysRevLett.91.247901)
- Stehlé J, et al. High-Resolution Measurements of Face-to-Face Contact Patterns in a Primary School. *PLoS ONE*, 2011. [doi:10.1371/journal.pone.0023176](https://doi.org/10.1371/journal.pone.0023176)
- Génois M, et al. Data on face-to-face contacts in an office building suggest a low-cost vaccination strategy based on community linkers. *Network Science*, 2015. [doi:10.1017/nws.2015.10](https://doi.org/10.1017/nws.2015.10)

### E2　人类信号网络的结构可控性：驱动节点与疾病基因、药物靶点、必需基因 {#e2 toc="E2　人类信号网络的结构可控性"}

**难度** ★★　**对应手册专题**：[网络可控性与稳定性](controllability.html)

**背景与问题。** Liu 等（2011）把结构可控性问题转化为最大匹配问题：未被匹配的节点就是驱动节点，驱动节点的比例主要由度分布决定。Vinayagam 等（2016）在有向人类蛋白网络中逐个删除节点，按驱动节点数的变化把节点分为“不可或缺”“中性”“可有可无”三类，发现不可或缺的节点富集疾病基因和药物靶点。本题用当前的 OmniPath 信号网络重新检验：

1. 网络需要多少驱动节点？与随机网络相比如何？
2. 三类节点中必需基因、疾病基因、药物靶点的比例是否不同？
3. 控制节点的度之后，这种差异是否仍然存在？

**数据**

| 数据 | 内容 | 获取 | 许可 |
|:-------|:----------------|:-----------|:-----|
| OmniPath（omnipath 数据集） | 文献整理的人类信号相互作用约 8.6 万条，带方向和激活/抑制标注 | [omnipathdb.org/interactions](https://omnipathdb.org/interactions?datasets=omnipath&genesymbols=yes)（加 `&license=academic` 只取允许学术使用的记录） | 每条沿用来源数据库的许可 |
| DepMap CRISPR 依赖性数据 | 上千个癌细胞系的基因敲除效应（`CRISPRGeneEffect`）和共同必需基因列表 | [depmap.org/portal/data_page](https://depmap.org/portal/data_page/) | Broad 生成的数据一般为 CC BY 4.0，以下载页说明为准；引用所用版本的 figshare 记录 |
| Open Targets Platform 26.09 | 疾病基因（遗传关联）、药物靶点（`drug_mechanism_of_action`） | FTP 目录 [ftp.ebi.ac.uk/…/output](https://ftp.ebi.ac.uk/pub/databases/opentargets/platform/26.09/output/) | CC0 1.0（源自 ChEMBL 的部分为 CC BY-SA 3.0） |

**必做分析**

1. 构建有向网络（只保留方向一致的边，去掉自环），描述入度和出度分布。
2. 用最大匹配求最少驱动节点（把有向图拆成二部图，用 Hopcroft–Karp 算法，networkx 可以实现），计算驱动节点比例 n~D~，与保持入度和出度的随机网络、同规模的 ER 随机网络比较。
3. 节点分类：逐个删除节点并重新计算驱动节点数，分为不可或缺（驱动节点数增加）、可有可无（减少）、中性（不变）三类。
4. 富集：比较三类节点中必需基因、疾病基因、药物靶点的比例；用逻辑回归控制入度和出度；做按度匹配的置换检验。
5. 控制概况：计算源节点、外部扩张、内部扩张三类驱动节点的比例（Ruths 与 Ruths 2014），并与其他网络（如 A2 的转录调控网络）比较。

**进阶方向**

- 最大匹配不唯一：多次随机化匹配，计算每个节点成为驱动节点的频率，区分“关键”与“冗余”节点（Jia 等 2013）。
- 秀丽隐杆线虫神经连接组：在 Yan 等（2017）研究的连接组上重复分析，与其神经元消融实验的结果对照（连接组数据见 <https://wormwiring.org/>）。

**注意。** 结构可控性只看拓扑，隐含线性时不变动力学、每条边都可调节等假设，对生物系统的解释有限（Gates 与 Rocha 2016）。药物靶点和疾病基因研究得多、连边多，必须控制度。网络不完整，结论依赖数据版本。

**参考文献**

- Liu YY, et al. Controllability of complex networks. *Nature*, 2011. [doi:10.1038/nature10011](https://doi.org/10.1038/nature10011)
- Liu YY, Barabási AL. Control principles of complex systems. *Reviews of Modern Physics*, 2016. [doi:10.1103/RevModPhys.88.035006](https://doi.org/10.1103/RevModPhys.88.035006)
- Vinayagam A, et al. Controllability analysis of the directed human protein interaction network identifies disease genes and drug targets. *Proceedings of the National Academy of Sciences*, 2016. [doi:10.1073/pnas.1603992113](https://doi.org/10.1073/pnas.1603992113)
- Ruths J, Ruths D. Control Profiles of Complex Networks. *Science*, 2014. [doi:10.1126/science.1242063](https://doi.org/10.1126/science.1242063)
- Jia T, et al. Emergence of bimodality in controlling complex networks. *Nature Communications*, 2013. [doi:10.1038/ncomms3002](https://doi.org/10.1038/ncomms3002)
- Gates AJ, Rocha LM. Control of complex networks requires both structure and dynamics. *Scientific Reports*, 2016. [doi:10.1038/srep24456](https://doi.org/10.1038/srep24456)
- Yan G, et al. Network control principles predict neuron function in the Caenorhabditis elegans connectome. *Nature*, 2017. [doi:10.1038/nature24056](https://doi.org/10.1038/nature24056)
- Türei D, et al. OmniPath: guidelines and gateway for literature-curated signaling pathway resources. *Nature Methods*, 2016. [doi:10.1038/nmeth.4077](https://doi.org/10.1038/nmeth.4077)
- Tsherniak A, et al. Defining a Cancer Dependency Map. *Cell*, 2017. [doi:10.1016/j.cell.2017.06.010](https://doi.org/10.1016/j.cell.2017.06.010)

## 自拟题目 {#own}

可以结合自己的研究方向自拟题目。自拟题目要回答上面的“五个问题”，计划书中写清楚：网络的节点和边、公开数据来源（链接、版本、许可）、至少一种零模型或随机化对照、至少一项敏感性分析。可以参考的方向：

- 肠道菌群共现网络：组成型数据直接算相关会产生虚假的负相关，比较 Pearson 相关与 SparCC 等组成型数据方法得到的网络（Friedman 与 Alm 2012）。
- 单细胞转录调控网络：在 A3 的基础上，用 SCENIC 等方法比较不同细胞类型的调控子活性。
- 药物不良反应共现网络：基于公开的药物不良事件报告数据，分析药物–不良反应二部网络的结构。
- 其他题目中提到的“进阶方向”，也可以扩展成独立的论文。

参考文献：Friedman J, Alm EJ. Inferring Correlation Networks from Genomic Survey Data. *PLoS Computational Biology*, 2012. [doi:10.1371/journal.pcbi.1002687](https://doi.org/10.1371/journal.pcbi.1002687)

## 常用工具 {#tools}

| 用途 | Python | R |
|:-------|:-------------------|:--------------|
| 网络构建与指标 | networkx、python-igraph | igraph |
| 社团发现 | networkx、leidenalg | igraph |
| 脑网络 | nilearn、bctpy、netneurotools、enigmatoolbox | — |
| 脑电 | MNE-Python | — |
| 基因网络推断 | arboreto（GENIE3、GRNBoost2）、scikit-learn（graphical lasso） | WGCNA、minet |
| 症状网络 | — | bootnet、qgraph、NetworkComparisonTest、IsingFit、mgm |
| 调查数据 | pandas（读 XPT） | haven、survey |

课程手册的[代码库](code.html)有两百多个可直接运行的 Python 示例，分析流程可参考[网络分析流程与 NetworkX 实践](analysis-workflow.html)和[研究问题、可复现分析与敏感性分析](reproducible-research.html)两个专题。
