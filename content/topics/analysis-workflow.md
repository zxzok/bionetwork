---
id: analysis-workflow
title: 网络分析流程与 NetworkX 实践
en: Network analysis workflow with NetworkX
domain: methods
legacy: L08
summary: 从提出问题、读入与清洗数据、选择工具，到指标计算、零模型比较、可视化与报告，用 NetworkX 完成一次完整的网络分析
keywords: [NetworkX, 网络分析流程, 工具选择, igraph, graph-tool, BCT, Cytoscape, Gephi, 数据格式, 稀疏矩阵, 大规模网络, 近似算法, 布局算法, 力导向布局, 可视化, 计算陷阱, 零模型, 保度随机化, 小世界系数, 公开数据集]
synonyms: [NetworkX, Python 网络分析, network analysis pipeline, 分析流程, workflow, igraph, python-igraph, graph-tool, NetworKit, Brain Connectivity Toolbox, BCT, bctpy, Cytoscape, stringApp, py4cytoscape, Gephi, ForceAtlas2, GEXF, GraphML, GML, node-link JSON, 边表, 边列表, edge list, 邻接表, adjacency list, 邻接矩阵, adjacency matrix, scipy.sparse, CSR, 压缩稀疏行, sparse matrix, 稀疏矩阵, pandas, from_pandas_edgelist, 格式转换, file format, 大规模网络, large-scale network, 近似介数, approximate betweenness, Brandes 算法, 抽样, sampling, 诱导子图, induced subgraph, 后端, backend, nx-cugraph, nx-parallel, 布局, layout, 力导向, force-directed, Fruchterman-Reingold, spring layout, Kamada-Kawai, 谱布局, spectral layout, 层次布局, hierarchical layout, Sugiyama, hive plot, 毛线团, hairball, 自环, self-loop, 重边, multi-edge, MultiGraph, 孤立点, isolated node, 有向图, DiGraph, 权重, 距离, 相似度, distance vs similarity, null model, 零模型, 参照网络, degree-preserving randomization, 保度随机化, 双边交换, double edge swap, configuration model, 配置模型, small-world coefficient, sigma, z-score, 共表达网络, 疾病模块, LCC, 最大连通分支, 度匹配, degree-matched]
demos: [graph_matrix, modularity]
reviewed: 2026-11-15
---

## 概述 {#overview}

网络科学的概念（度、聚集系数、路径长度、社团、中心性）只有落到具体数据上才能检验其价值。本专题处理的是从理论到数据的“最后一公里”：怎样把一个生物医学问题转化为节点与边的定义，怎样选择计算工具，怎样把各种来源的数据正确读入并在不同格式之间转换，怎样计算指标、发现社团、与模型网络和零模型比较，网络大到普通方法算不动时怎么办，怎样画出能回答问题的网络图，以及有哪些看似细小却会悄悄改变结果的计算陷阱。

这里的方法是其他专题的共同基础。指标的定义见[网络结构指标与随机图](network-metrics.html)，小世界与无标度的判别见[小世界与无标度网络模型](network-models.html)，模块度与社团检测算法见[社团结构与社区发现](community-structure.html)；从原始测量构建网络、阈值选择、零模型与统计验证的系统讨论见[网络构建与统计验证](network-construction.html)。把分析做得可复算、并检验结论对分析选择是否稳健，见[研究问题、可复现分析与敏感性分析](reproducible-research.html)；结果的图表呈现与报告结构见[结果呈现与研究前沿](reporting-frontiers.html)。

本专题以 Python 的 NetworkX 为主要工具，同时比较 igraph、graph-tool、Brain Connectivity Toolbox（BCT）、Cytoscape 与 Gephi 的定位，并给出一个从模拟表达矩阵出发、经过质控、建网、模块识别、枢纽筛选、零模型检验到敏感性分析的完整案例。最后整理了生物医学研究中常见的公开网络数据来源与分析方向。所有计算都有对应的可运行[代码示例](analysis-workflow.html#code)。

## 网络分析的一般流程 {#workflow}

无论分析什么生物医学数据，一个网络研究大致都包括以下六步：

1. **提出问题**：想用网络回答什么？（例如“阿尔茨海默病相关蛋白在 PPI 网络中是否聚成模块？哪些蛋白处于关键位置？”）
2. **数据获取与预处理**：选择合适的公开数据集，清洗、过滤、统一标识符（如基因名与 UniProt ID 的映射）。
3. **构建网络**：明确规定**节点是什么、边是什么**、边是否有方向和权重、阈值怎么定。这一步的选择往往比后面的算法更影响结论。
4. **网络特性分析**：度分布、聚集系数、路径长度、密度、中心性，并**从生物学角度解读**。
5. **算法分析**：社团划分或节点分类，分析不同类别节点之间的关系，探讨结构与功能的联系；与零模型比较，判断观察到的性质是否“非随机”。
6. **解释与报告**：结合文献给出生物学解释，讨论局限，撰写论文。

每一步都有应当留下的“记录”，它们既是质量控制，也是写方法部分的素材：

| 步骤 | 应记录或检查的内容 | 常见遗漏 |
|---|---|---|
| 数据获取 | 数据库名称、版本号或下载日期、物种、证据类型、许可 | 只写“来自 STRING”，不写版本与置信度阈值 |
| 预处理 | 标识符映射规则与映射失败的数目、重复记录的合并方式 | 一对多映射被静默丢弃或重复计数 |
| 构建网络 | 有向或无向、加权或无权、阈值与理由、是否去除自环与重边 | 权重究竟是“强度”还是“距离”没有说明 |
| 网络概况 | 节点数、边数、密度、连通分支数、最大连通分支占比、孤立点数 | 只报告最大连通分支上的结果，不说明丢了多少节点 |
| 指标与算法 | 软件与版本、函数与关键参数（权重、归一化、随机种子） | Louvain 只跑一次；默认参数未写明 |
| 统计比较 | 零模型类型、随机网络个数、$z$ 分数或经验 $p$ 值、多重比较校正 | 只与 ER 比较；零模型次数太少 |
| 稳健性 | 换阈值、换数据源、换算法后主要结论是否成立 | 只报告“效果最好”的那个设置 |

::: {.callout-def}
**零模型**（null model）：保留真实网络的某些性质（如节点数、边数，或者每个节点的度）而其余部分随机化得到的参照网络。只有与合适的零模型比较，“聚集系数高”“模块度高”“某些基因彼此靠近”这类结论才有意义。常用两种：（1）**ER 随机图**，只保留节点数和边数；（2）**保度随机化**（配置模型或双边交换），保留每个节点的度。后者更严格，因为许多性质（如枢纽的存在）由度序列本身决定。更多零模型（加权、空间约束、相关矩阵、节点标签置换）见[零模型与空模型](network-construction.null-models.html)。
:::

::: {.callout-warn}
网络构建的选择要在报告中**明确写出并做敏感性分析**：PPI 网络用 STRING 置信度 0.4 还是 0.7？共表达网络用相关系数 0.6 还是 0.8 作为阈值？换一个合理的参数，主要结论是否仍然成立？脑网络中的阈值问题见[脑连接组：结构与功能连接](brain-connectome.html)，系统的敏感性分析方法见[敏感性分析与替代解释](reproducible-research.sensitivity-analysis.html)。
:::

设计一项网络分析时，有几条通用原则：

- **从问题出发，而不是从数据库出发**：“用 STRING 做一个网络”不是研究问题；“阿尔茨海默病风险基因在 PPI 网络中是否比随机基因集更聚集？”是。
- **规模要可控**：先用小样本跑通全流程，再扩大；网络规模要与可用的计算资源和分析方法匹配（见[大规模网络的计算策略](analysis-workflow.large-scale.html)）。
- **至少包含一个对照**：零模型、随机基因集、健康与疾病两组网络、不同阈值的结果，都可以作为对照。
- **先看数据，再算指标**：在计算任何指标之前，先打印节点数、边数、自环数、连通分支、度的最大值与最小值，并检查几条具体的边是否符合预期。很多错误（标识符错位、权重方向弄反）在这一步就能发现。

## 工具选择 {#tool-selection}

网络分析的软件大致分两类：**编程库**（NetworkX、igraph、graph-tool、NetworKit、BCT）适合可复算的计算与统计；**交互式桌面软件**（Cytoscape、Gephi）适合探索、注释与作图。实际研究通常两类并用：在脚本中完成构建、计算与统计，再把带属性的网络导出到桌面软件作图。

| 工具 | 形式与核心实现 | 规模与速度（定性） | 算法与功能侧重 | 许可 |
|---|---|---|---|---|
| NetworkX | Python 库，纯 Python，图存为“字典的字典” | 适合 $10^4$–$10^5$ 节点的交互分析与方法原型；全局算法在更大网络上很慢 | 覆盖面最广：经典图算法、生成模型、读写格式、与 NumPy/SciPy/pandas 互转；可通过“后端”调用 GPU 或并行实现 | BSD-3-Clause |
| igraph | C 核心库，提供 R、Python（python-igraph）、Mathematica 接口 | 常见算法比纯 Python 实现快得多，百万级边可用 | 社团检测（Leiden、Infomap、walktrap 等）、布局、图同构；R 生态中最常用 | GPL-2.0 或更高 |
| graph-tool | Python 接口，C++ 模板实现，基于 Boost Graph Library，部分算法 OpenMP 并行 | 官方称速度与内存接近纯 C/C++ 库 | 随机块模型（SBM）的贝叶斯推断、网络重建、高质量绘图 | LGPL-3.0 |
| NetworKit | C++ 核心、Python 接口，多线程 | 面向大规模网络的并行算法 | 近似中心性、社团检测、大图生成 | MIT |
| BCT / bctpy | MATLAB 工具箱，bctpy 为 Python 移植；以邻接矩阵为输入 | 面向脑网络规模（数十到数千个节点） | 加权、有向、带符号网络的脑网络指标：参与系数、模块内度 $z$ 分数、富人俱乐部、零模型 | bctpy 为 GPL-3.0；MATLAB 原版以下载包内说明为准 |
| Cytoscape | Java 桌面软件，App 扩展（stringApp、clusterMaker2 等）；可用 py4cytoscape / RCy3 脚本控制 | 交互操作适合数千到数万节点 | 生物分子网络标准平台：数据库导入、属性映射样式、功能富集、聚类 | LGPL-2.1 |
| Gephi | Java 桌面软件，OpenGL 渲染 | 官方说明可视化可达百万元素级 | ForceAtlas2 等布局、模块度与中心性统计、动态网络、导出出版级图 | CDDL-1.0 与 GPL-3.0 双许可 |

选择时可按以下顺序考虑：

1. **规模**：几千个节点以内，NetworkX 足够；数十万节点以上需要全局路径类计算时，改用 igraph、graph-tool 或 NetworKit，或者先过滤。
2. **所需算法是否已实现、实现是否可信**：例如 Leiden 算法在 igraph 中有成熟实现；基于随机块模型的社团推断以 graph-tool 最完整；脑网络中参与系数、带符号网络的模块度等指标以 BCT 的定义最常被引用。同一个指标在不同软件中的定义细节（归一化、对非连通图的处理、加权推广）可能不同，换软件时要核对文档。
3. **数据形态**：脑网络常以 $N\times N$ 连接矩阵存储，用 BCT 或 NumPy 直接处理矩阵更自然；PPI、调控网络常以边表存储，NetworkX、igraph、Cytoscape 更方便。
4. **许可**：GPL 类许可对“在自己的软件中再分发”有要求，一般科研使用不受影响，但开发并发布软件包时需要留意。
5. **可复现性**：脚本化工具（库）优先于手工点击；桌面软件中的操作要记录步骤、参数与版本，必要时用 py4cytoscape 等自动化接口重放。

::: {.callout-warn}
**不同软件的“同名指标”未必相同**。例如对非连通图，接近中心性有的软件只在节点所在分支内计算，有的做了修正（NetworkX 默认使用 Wasserman–Faust 修正）；加权聚集系数至少有几种不同推广；介数是否归一化、是否计入端点也各不相同。报告中应写出软件名、版本与函数名；对比文献数值时先确认定义一致。
:::

## NetworkX 上手 {#networkx-basics}

NetworkX 是 Python 中最常用的网络分析库，接口友好，适合中小规模网络（数万节点以内）。在本地使用时，建议用 Anaconda 或 `pip install networkx numpy scipy matplotlib pandas` 安装。

### 数据结构与图类型

NetworkX 把图存成嵌套字典：`G.adj[u][v]` 是边 $(u,v)$ 的属性字典，`G.nodes[u]` 是节点属性字典。节点可以是任何可哈希的 Python 对象（字符串、整数、元组），边可以携带任意属性。这种设计非常灵活，也解释了它在大规模网络上较慢、占内存较多的原因：每条边都是若干个 Python 字典条目，而不是数组中的一个整数。

| 类 | 有向 | 允许重边 | 典型用途 |
|---|---|---|---|
| `nx.Graph` | 否 | 否（允许自环） | PPI、共表达、功能连接 |
| `nx.DiGraph` | 是 | 否 | 转录调控、信号通路、代谢反应方向、有效连接 |
| `nx.MultiGraph` | 否 | 是 | 同一对蛋白被多项实验分别报告、多种证据类型并存 |
| `nx.MultiDiGraph` | 是 | 是 | 知识图谱中同一对实体之间的多种关系 |

大多数指标（聚集系数、社团检测、许多中心性）只为 `Graph` 或 `DiGraph` 设计，对多重图要么不支持，要么含义不清。通常的做法是先把重边按明确规则聚合（计数、求和、取最大）为简单图，见[常见计算陷阱](analysis-workflow.computational-pitfalls.html)。

### 构建与读入

```python
import networkx as nx

G = nx.Graph()                    # 无向图；有向图用 nx.DiGraph()
G.add_edge("TP53", "MDM2")        # 加边时自动加节点
G.add_edge("TP53", "EP300", weight=0.9)
G.add_edges_from([("MDM2", "MDM4"), ("EP300", "CREBBP")])

# 从边列表文件读入（每行 "a b" 或 "a b 0.9"）
# G = nx.read_edgelist("ppi.txt", data=(("weight", float),))
# 从 pandas 表读入
# G = nx.from_pandas_edgelist(df, "protein1", "protein2", edge_attr="score")

print(G.number_of_nodes(), G.number_of_edges())
```

### 一个最小的完整分析

```python
G = nx.karate_club_graph()
G = G.subgraph(max(nx.connected_components(G), key=len)).copy()   # 取最大连通分支
deg = dict(G.degree())
print("平均度", sum(deg.values()) / G.number_of_nodes())
print("平均聚集系数", nx.average_clustering(G))
print("平均最短路径", nx.average_shortest_path_length(G))
comms = nx.community.louvain_communities(G, seed=1)
print("社团数", len(comms), "模块度 Q =", nx.community.modularity(G, comms))
```

注意 `G.subgraph(...)` 返回的是原图的“视图”，原图改变时它随之改变，并且不能增删节点；需要独立对象时加 `.copy()`。

本专题的代码示例把这几行扩展为九个完整示例：读入与清洗边表、指标与中心性计算、社团发现与稳定性、与模型网络和零模型比较、格式互转、计算陷阱、大规模计算策略、布局比较，以及一个从原始数据到结论的完整案例。

## 数据读写与格式转换 {#data-io}

生物医学网络数据以多种形式出现：数据库导出的边表（STRING、BioGRID、TRRUST）、实验或影像处理流程输出的连接矩阵（脑网络）、桌面软件保存的 GraphML/GEXF 文件、网页可视化使用的 JSON。正确地在这些表示之间转换，是保证后续计算正确的前提。

### 常见格式

| 格式 | 内容 | 能否保存孤立点 | 能否保存节点/边属性 | NetworkX 读 / 写 | 适用场合 |
|---|---|---|---|---|---|
| 边表（edge list，CSV/TSV） | 每行一条边，可带权重列 | 否（需另附节点表） | 边属性可作为列；节点属性需另表 | `read_edgelist` / `write_edgelist`；`from_pandas_edgelist` / `to_pandas_edgelist` | 数据库导出、最通用的交换格式 |
| 邻接表（adjacency list） | 每行一个节点及其全部邻居 | 是 | 否 | `read_adjlist` / `write_adjlist` | 简单无权图 |
| 邻接矩阵 | $N\times N$ 数组 | 是 | 只有一个边权；节点身份靠行列顺序 | `from_numpy_array` / `to_numpy_array` | 脑连接矩阵、相关矩阵、线性代数计算 |
| 稀疏矩阵（SciPy CSR/COO） | 只存非零元 | 是 | 同上 | `from_scipy_sparse_array` / `to_scipy_sparse_array` | 大规模网络的矩阵运算 |
| GraphML | XML，带类型声明 | 是 | 是（标量属性） | `read_graphml` / `write_graphml` | 与 Cytoscape、Gephi、igraph、graph-tool 交换 |
| GEXF | XML，Gephi 原生格式，可含动态信息 | 是 | 是 | `read_gexf` / `write_gexf` | 导入 Gephi 作图 |
| GML | 文本，层级键值 | 是 | 是 | `read_gml` / `write_gml` | 一些经典数据集的发布格式 |
| node-link JSON | 节点列表 + 边列表 | 是 | 是（可 JSON 化的任意属性） | `node_link_data` / `node_link_graph` | 网页可视化（D3.js 等）、Web API |
| Cytoscape JSON | Cytoscape.js 使用的结构 | 是 | 是 | `cytoscape_data` / `cytoscape_graph` | 与 Cytoscape.js / Cytoscape 交换 |

### 与 pandas、NumPy、SciPy 互转

- **pandas 边表**：`nx.from_pandas_edgelist(df, source="protein1", target="protein2", edge_attr=["score"], create_using=nx.Graph)`；反向用 `nx.to_pandas_edgelist(G)`。节点属性可另建一张表，用 `nx.set_node_attributes(G, df_nodes.set_index("id")["type"].to_dict(), "type")` 写入。
- **NumPy 矩阵**：`A = nx.to_numpy_array(G, nodelist=nodes, weight="weight")`。务必**显式给出并保存 `nodelist`**：矩阵只靠行列顺序记录节点身份，顺序丢了，矩阵就无法再与基因名或脑区名对应。从矩阵建图用 `nx.from_numpy_array(A)`，再用 `nx.relabel_nodes` 把整数编号换回名称。
- **SciPy 稀疏矩阵**：`S = nx.to_scipy_sparse_array(G, nodelist=nodes, format="csr")` 返回 SciPy 稀疏数组；无向图的每条边在矩阵中存两次（$(i,j)$ 与 $(j,i)$），所以非零元个数是边数的两倍（自环只存一次）。
- **其他库**：igraph 可以用 `ig.Graph.from_networkx(G)` 与 `g.to_networkx()` 互转；graph-tool 与 Cytoscape、Gephi 之间最稳妥的交换格式是 GraphML。

### 读写中的细节

1. **标识符**：STRING 的蛋白标识形如“物种编号.Ensembl 蛋白 ID”（人类为 `9606.ENSP…`），需要映射为基因名才能与其他数据对接；映射常是一对多或多对一，要写明规则并报告映射失败的数目。
2. **数据类型**：从 GraphML 读回时节点 id 一律是字符串，原来的整数节点 `1` 会变成 `"1"`；与其他数据合并前要统一类型。GraphML 只支持标量属性，列表类属性（例如一个基因所属的多个通路）需要先转成分隔符字符串或改用 JSON。
3. **方向与重复**：同一条无向边在边表中可能出现两次（A–B 与 B–A），读入 `nx.Graph` 会自动合并，读入 `nx.DiGraph` 则成为两条有向边；STRING 的完整下载文件中每对蛋白就是双向各列一次。
4. **孤立点**：边表天然不含孤立点。若研究问题涉及“某些基因在网络中没有任何连接”（例如疾病基因的网络覆盖率），需要另外维护节点全集。

::: {.callout-warn}
格式转换后要做**往返检查**：节点数、边数、权重总和、若干条具体边的属性是否与原始数据一致。代码示例“格式互转”把同一个小网络依次转为边表、稠密矩阵、CSR 稀疏矩阵、GraphML 与 node-link JSON，结果显示：边表往返后孤立点丢失（6 个节点变成 5 个），其余表示保留了全部节点和边；含列表的节点属性写 GraphML 时报错，转为字符串后才能写入。
:::

## NetworkX 速查表 {#networkx-cheatsheet}

| 任务 | 函数 | 相关专题 / 说明 |
|---|---|---|
| 建图 | `nx.Graph()`、`nx.DiGraph()`、`G.add_edge(u, v, weight=w)` | [网络结构指标与随机图](network-metrics.html)；有向图区分入度、出度 |
| 读入 | `nx.read_edgelist()`、`nx.from_pandas_edgelist()`、`nx.read_gexf()`、`nx.read_graphml()` | GEXF/GraphML 可与 Gephi、Cytoscape 互通，见[数据读写与格式转换](analysis-workflow.data-io.html) |
| 导出 | `nx.write_gexf(G, "g.gexf")`、`nx.write_graphml()`、`nx.to_pandas_edgelist(G)`、`nx.node_link_data(G)` | 导出到 Gephi/Cytoscape 作图，或导出 JSON 供网页使用 |
| 矩阵 | `nx.to_numpy_array(G, nodelist=)`、`nx.from_numpy_array(A)`、`nx.to_scipy_sparse_array(G)`、`nx.laplacian_matrix(G)` | [网络结构指标与随机图](network-metrics.html)、[同步与协同动力学](synchronization.html)；固定 `nodelist` |
| 基本信息 | `G.number_of_nodes()`、`G.number_of_edges()`、`nx.density(G)`、`nx.number_of_selfloops(G)`、`list(nx.isolates(G))` | 先检查自环与孤立点 |
| 连通性 | `nx.is_connected(G)`、`nx.connected_components(G)`、`nx.strongly_connected_components(D)`、`nx.weakly_connected_components(D)` | 很多指标要求连通，先取最大连通分支 |
| 子图 | `G.subgraph(nodes).copy()`、`nx.k_core(G, k)`、`nx.core_number(G)` | [网络上的传播与免疫](spreading.html)中的 k-壳 |
| 度 | `G.degree()`、`D.in_degree()`、`D.out_degree()`、`nx.degree_histogram(G)` | [网络结构指标与随机图](network-metrics.html)；加权时 `G.degree(weight="weight")` 为强度 |
| 路径 | `nx.shortest_path(G, s, t, weight=)`、`nx.average_shortest_path_length(G)`、`nx.diameter(G)` | [网络结构指标与随机图](network-metrics.html)；只对连通图有定义；`weight` 被当作距离 |
| 聚集 | `nx.clustering(G)`、`nx.average_clustering(G)`、`nx.transitivity(G)` | [网络结构指标与随机图](network-metrics.html)；注意平均聚集系数与传递性的区别 |
| 同配性 | `nx.degree_assortativity_coefficient(G)` | 高度节点是否倾向于相连，见[度相关性与网络结构的高阶统计](degree-correlations.html) |
| 中心性 | `nx.degree_centrality`、`nx.betweenness_centrality`、`nx.closeness_centrality`、`nx.eigenvector_centrality`、`nx.pagerank` | [网络结构指标与随机图](network-metrics.html)、[网络上的传播与免疫](spreading.html)；大网络的介数可用参数 `k` 抽样近似 |
| 社团 | `nx.community.louvain_communities(G, seed=)`、`nx.community.greedy_modularity_communities(G)`、`nx.community.girvan_newman(G)`、`nx.community.label_propagation_communities(G)` | [社团结构与社区发现](community-structure.html)；Louvain 有随机性，固定 `seed` 并多次运行 |
| 模块度 | `nx.community.modularity(G, communities)` | [社团结构与社区发现](community-structure.html) |
| 模型网络 | `nx.gnm_random_graph(n, m)`、`nx.watts_strogatz_graph(n, k, p)`、`nx.barabasi_albert_graph(n, m)`、`nx.random_partition_graph(sizes, p_in, p_out)`、`nx.stochastic_block_model(sizes, P)` | [网络结构指标与随机图](network-metrics.html)、[小世界与无标度网络模型](network-models.html)、[社团结构与社区发现](community-structure.html) |
| 零模型 | `nx.double_edge_swap(G, nswap, max_tries)`、`nx.configuration_model(deg_seq)` | 保度随机化；配置模型会产生重边和自环，需要清理 |
| 匹配 | `nx.bipartite.hopcroft_karp_matching(B, top_nodes)` | [网络可控性与稳定性](controllability.html)中的驱动节点 |
| 布局 | `nx.spring_layout(G, seed=)`、`nx.kamada_kawai_layout`、`nx.spectral_layout`、`nx.forceatlas2_layout`、`nx.multipartite_layout` | 见[布局算法](analysis-workflow.layouts.html)；`forceatlas2_layout` 需 NetworkX 3.4 及以上 |
| 可视化 | `nx.draw_networkx(G, pos, node_color=, node_size=)` | 快速查看；论文图建议用 Gephi/Cytoscape |
| 后端 | `nx.betweenness_centrality(G, backend="cugraph")`、`nx.config.backend_priority` | 安装 nx-cugraph、nx-parallel 等后端后，同一函数可调用 GPU 或并行实现 |
| 自带数据 | `nx.karate_club_graph()`、`nx.les_miserables_graph()`、`nx.florentine_families_graph()` | 演示用的小网络 |

::: {.callout-warn}
三个常见坑：（1）`average_shortest_path_length` 在非连通图上会报错，先取最大连通分支，并在报告中说明丢掉了多少节点；（2）`louvain_communities` 每次结果可能不同，要固定随机种子、多次运行并报告结果的稳定性；（3）NetworkX 是纯 Python 实现，对几十万节点以上的网络（如完整的 STRING 人类网络）计算介数会很慢，可以先按置信度过滤，或改用 igraph、graph-tool。更多陷阱见下一节。
:::

## 常见计算陷阱 {#computational-pitfalls}

很多错误不会让程序报错，只会悄悄改变数值。下面五类问题在生物医学网络中最常见，代码示例“五个常见计算陷阱”给出了每一类的可手算演示。

### 自环

蛋白质同源二聚化、基因的自调控会在数据中表现为自环。在无向简单图中，一个自环使该节点的度加 2（NetworkX 的约定），并可能影响聚集系数、模块度等的计算。示例中三角形加一条悬挂边的小图里，节点 3 的度从 3 变为 5。自环有生物学意义（如[网络基序：自调控与前馈环](molecular-networks.network-motifs.html)中的负自调控），但大多数拓扑指标的定义假设没有自环。做法是：用 `nx.number_of_selfloops` 检查，把自环作为节点属性另行记录，然后 `G.remove_edges_from(nx.selfloop_edges(G))`。

### 重边

同一对蛋白可能被多项实验、多种证据分别报告。用 `nx.Graph(M)` 把多重图直接转为简单图时，重边被合并，只保留**其中一条边的属性**，而不是自动求和。示例中 A–B 被报告两次（权重 1 与 2），直接转换得到权重 2，显式求和得到 3。应当根据问题选定聚合规则（证据条数、权重求和、取最大、组合置信度），并在方法中写明。STRING 的综合得分（combined score）就是按其自身规则整合多个证据通道的结果，不应再与单个通道的分数混用。

### 孤立点

孤立点改变平均度、密度，并使所有基于路径的全局指标报错或失去意义。示例中 5 节点的路径图加上 3 个孤立点后，平均度从 1.6 降到 1.0，密度从 0.40 降到 0.14，平均最短路径直接报错。孤立点从哪里来本身就是信息：可能是阈值过高、标识符映射失败，也可能是该基因确实缺乏已知相互作用（研究偏倚）。应当报告孤立点数目及其可能来源，再决定是否去除。

### 有向性

调控、信号与代谢网络的方向有明确的生物学含义。把有向图无向化会改变几乎所有中心性：示例中调控链 TF1 → TF2 → TF3 → TF4 的 PageRank 在有向图中沿方向递增（末端 TF4 最高），无向化后变成首尾对称。有向图的连通性分“弱连通”（忽略方向连通）与“强连通”（双向可达），该示例弱连通而不强连通。特征向量中心性在无环有向图上没有有意义的非零解，PageRank 通过随机跳转避免了这一问题；有向图的聚集系数、同配性也都有专门的定义。

### 权重是相似度还是距离

这是最隐蔽也最常见的错误。最短路径、接近中心性和介数中心性把 `weight` 当作**距离**（越大越远），而共表达相关、STRING 置信度、纤维束数目都是**相似度或强度**（越大越近）。示例中 A–B、B–C 为强相关（$r=0.9$），A–C 为弱相关（$r=0.2$）：若直接把 $r$ 作为 `weight`，算法认为 A→C 的直接弱边“最短”，B 的介数为 0；把 $r$ 转换为距离后，最短路径改走 A–B–C，B 的介数为 1。

两种常用的转换（见 Opsahl 等 2010 与 [Rubinov 2010](paper-rubinov2010_measures.html)）：

$$
d_{ij}=\frac{1}{w_{ij}}\qquad\text{或}\qquad d_{ij}=-\log w_{ij}\quad(0<w_{ij}\le 1).
$$

倒数变换常用于脑网络的连接长度；负对数变换把路径长度对应为沿途相似度（或概率）的乘积，在 $w$ 可解释为置信概率时更自然。相反，模块度、加权度（强度）、加权聚集系数把权重当作**强度**，不需要转换。同一份分析中往往两种用法并存，最好在图中分别存储两个属性（如 `weight` 与 `distance`），并在每次调用时显式指定。

::: {.callout-warn}
其他需要留意的默认行为：`betweenness_centrality` 默认归一化（`normalized=True`），不同论文的数值因此不能直接比较；权重为 0 或负数时 Dijkstra 类算法不适用，带负权（负相关）的网络需要先决定是取绝对值、只保留正边，还是使用带符号网络的专门方法；对浮点权重，NetworkX 文档提示介数的结果可能受舍入影响，必要时可将权重放大取整。模块度对负权边也没有标准定义，带符号的相关网络应使用专门推广（如 BCT 中的带符号模块度）。
:::

## 大规模网络的计算策略 {#large-scale}

“大规模”是相对于算法复杂度而言的。在一个 2 万节点、6 万条边的稀疏网络上，度、连通分支、PageRank 都很快完成；但所有节点对的最短路径与精确介数的计算量与 $NM$ 成正比，规模再大一两个数量级就会变得不可行。应对策略可以归为五类。

### 1. 先缩小问题

- **按研究问题过滤**：只保留高置信度边、特定组织表达的基因、研究关心的子网络。
- **结构化约简**：最大连通分支、$k$-核（`nx.k_core`）、去除度为 1 的“悬挂”节点（若研究问题允许）。
- 每一步都要报告保留与丢弃的节点和边。过滤本身是一个需要做敏感性分析的分析选择。

### 2. 用稀疏矩阵和专门的数值库

生物网络几乎都是稀疏的（$M\ll N^2$）。稠密邻接矩阵的内存与 $N^2$ 成正比，稀疏格式（CSR、COO）只与非零元个数成正比。代码示例中 2 万节点的 BA 网络：稠密 `float64` 矩阵约需 3200 MB，CSR 格式约 2 MB。很多计算可以完全在稀疏矩阵上完成：

| 任务 | SciPy 函数 |
|---|---|
| 度、强度 | `A.sum(axis=1)` |
| 连通分支 | `scipy.sparse.csgraph.connected_components` |
| 最短路径（BFS / Dijkstra） | `scipy.sparse.csgraph.shortest_path`、`breadth_first_order` |
| 最大或最小几个特征值与特征向量（谱聚类、特征向量中心性、谱布局） | `scipy.sparse.linalg.eigsh`（对称）、`eigs`（非对称） |
| 拉普拉斯矩阵 | `scipy.sparse.csgraph.laplacian` |
| 随机游走、扩散、PageRank 的幂迭代 | 稀疏矩阵–向量乘法 `A @ x` |

### 3. 近似算法

- **抽样介数**：Brandes 算法对每个源点做一次单源最短路径并“回传”依赖值。只取 $k$ 个随机源点，再按 $N/k$ 放大，得到介数的无偏估计（Brandes 与 Pich 2007）；NetworkX 中即 `betweenness_centrality(G, k=k, seed=s)`。Riondato 与 Kornaropoulos（2016）给出了基于最短路径抽样、具有误差上界保证的近似算法。代码示例中，在 2000 节点的 BA 网络上，$k=200$ 个源点的估计耗时约为精确计算的十分之一，与精确值的 Spearman 秩相关约 0.91，前 20 名中有 19 个重合；$k=50$ 时秩相关约 0.86、前 20 名重合 14 个。也就是说，抽样介数适合找“排名靠前的节点”，对中低介数节点的精确排序不可靠。
- **平均路径长度**：从随机抽取的若干源点做 BFS，用样本均值估计全网平均距离。
- **社团检测**：Louvain、Leiden、标签传播在稀疏网络上的运行时间大致随边数近线性增长，适合大网络；Girvan–Newman 需要反复计算边介数，只适合小网络。

### 4. 换工具或换后端

NetworkX 3 起支持“后端分派”：安装 nx-parallel（基于 joblib 的并行实现）或 nx-cugraph（基于 NVIDIA GPU 的 RAPIDS cuGraph）等后端后，可以用函数的 `backend=` 参数、环境变量 `NETWORKX_BACKEND_PRIORITY` 或 `nx.config.backend_priority` 切换实现，代码其余部分不变。也可以直接改用 igraph、graph-tool、NetworKit 等 C/C++ 实现的库。

### 5. 谨慎使用网络抽样

当完整网络无法获得或无法处理时，人们会抽取子网络。需要牢记：**子网络的统计性质一般不等于全网络的性质**。均匀抽取节点后取诱导子图，每条边被保留的概率约为抽样比例的平方，度分布整体左移并改变形状；Stumpf、Wiuf 与 May（2005）证明，无标度网络的随机子网一般不再是无标度的——这对“相互作用组不完整”的生物网络尤其重要，因为现有 PPI 数据本身就可以看作真实相互作用组的一个非随机样本。Leskovec 与 Faloutsos（2006）比较了多种大图抽样方法，基于随机游走或“森林火灾”式扩展的方法比均匀节点抽样更能保留原网络的多种性质。代码示例中，从 2 万节点 BA 网络随机抽取 20% 节点，诱导子图的平均度从 6.0 降到约 1.2，最大度从 323 降到 45，并出现约 1500 个孤立点。

::: {.callout-def}
**计算复杂度速记**（$N$ 节点，$M$ 边，稀疏网络）：BFS 单源最短路径 $O(N+M)$；全部节点对最短路径（无权）$O(N(N+M))$；精确介数（Brandes）无权 $O(NM)$、加权 $O(NM+N^2\log N)$；局部聚集系数 $O\!\left(\sum_i k_i^2\right)$，枢纽节点主导计算量；幂迭代每步 $O(M)$；Kamada–Kawai 布局需要全部节点对距离，内存 $O(N^2)$。推导见[数学推导与算法](analysis-workflow.derivations.html)。
:::

## 布局算法 {#layouts}

网络图的节点坐标不是数据，而是**布局算法**为了满足某种美学或几何目标计算出来的。理解各类布局优化的是什么，才能判断图中看到的“簇”“中心”有多少来自数据、多少来自算法。

### 力导向布局

把边看作弹簧、节点之间存在斥力，求系统的低能量状态。

- **Fruchterman–Reingold**（1991，NetworkX 的 `spring_layout`）：相连节点之间的吸引力随距离平方增长，所有节点对之间的斥力与距离成反比，并用逐渐降低的“温度”限制每步位移，逐步冷却到稳定状态。结果通常比较均匀，社团往往呈现为团块。
- **Kamada–Kawai**（1989）：让图上两点的欧氏距离尽量接近它们的最短路径距离，能量是所有节点对“距离误差”的加权平方和。对中小网络，它对图距离的保真度通常较好，但需要全部节点对最短路径，难以用于大网络。
- **ForceAtlas2**（Jacomy 等 2014，Gephi 的主力布局，NetworkX 3.4 起提供 `forceatlas2_layout`）：斥力与两端节点的“度加 1”之积成正比，枢纽之间被推开，低度节点贴近其枢纽；可选 LinLog 模式加强社团分离，并可用 Barnes–Hut 近似把每步斥力计算从 $O(N^2)$ 降到约 $O(N\log N)$，适合较大网络的交互探索。

力导向布局有随机初值，结果依赖种子与迭代次数；节点之间的距离只在局部上有意义，**不同簇之间的远近与相对位置往往没有可解释的含义**。

### 谱布局

用拉普拉斯矩阵 $L=D-A$ 的第二、第三小特征值对应的特征向量作为二维坐标（Hall 1970 的二次布局思想；NetworkX 的 `spectral_layout`）。它最小化相连节点之间的距离平方和，结果不依赖随机种子，对社团结构敏感，在代码示例中“同模块与异模块平均距离之比”最小。缺点是节点容易大量重叠、分布很不均匀，常作为力导向布局的初值。

### 层次与分层布局

- **Sugiyama 型层次布局**（1981）：先把节点分配到若干层，再最小化相邻层之间的边交叉，最后确定坐标。适合有向无环或近似无环的网络，如转录调控级联、信号通路、细胞分化谱系。Graphviz 的 `dot` 程序实现了这一类布局。
- **按属性分层**（NetworkX 的 `multipartite_layout`、`bipartite_layout`）：按节点类型（药物 / 靶点 / 疾病）或属性分列排列，结构上的距离不再体现，但类型之间的连接模式一目了然。代码示例中，按模块分列的布局对图距离几乎没有保真度（秩相关约 0.03），这是它的设计目的使然。
- **Hive plot**（Krzywinski 等 2012）：按规则把节点放在几条径向轴上，位置由节点属性决定而不是由优化决定，因此不同网络之间可以直接比较。

### 布局质量可以定量检查

代码示例“布局算法比较”在一个含 4 个植入模块的随机分块网络上比较五种布局，用“节点对的图距离与欧氏距离的 Spearman 秩相关”衡量对距离的保真程度，用“同模块与异模块节点对的平均欧氏距离之比”衡量模块的视觉分离程度。在该网络上，Kamada–Kawai 的距离保真度最高（$\rho\approx0.76$），谱布局与 ForceAtlas2 的模块分离最明显（距离比约 0.17 与 0.25）。没有一种布局在所有目标上都最好；选择布局应服务于图要传达的那个结论。

## 可视化工具与原则 {#visualization}

| 工具 | 适合做什么 | 提示 |
|---|---|---|
| NetworkX + Matplotlib | 分析过程中快速看图、画度分布等统计图 | 布局用 `spring_layout` 并固定 `seed`；NetworkX 官方文档说明其绘图功能只是基础性的，建议用专门工具作图 |
| Gephi（[gephi.org](https://gephi.org)） | 中大型网络的交互式布局（ForceAtlas2）、按社团着色、导出高分辨率图 | 用 `nx.write_gexf` 导出，节点属性（社团、中心性）会一起带过去 |
| Cytoscape（[cytoscape.org](https://cytoscape.org)） | 生物分子网络的标准工具：可直接导入 STRING 网络（stringApp），做功能富集、聚类等 | 官方教程见 [tutorials.cytoscape.org](https://tutorials.cytoscape.org/)；属性到颜色、大小的“样式映射”可保存复用 |
| Graphviz | 层次布局（`dot`）、小型有向网络与流程图 | 适合调控级联、通路示意 |
| 邻接矩阵热图（Matplotlib） | 稠密网络（如脑功能连接）；按模块排序后块结构清晰 | 行列顺序决定能否看出结构，排序方式要写明 |

::: {.callout-def}
**好的网络图要回答一个问题**。“毛线团”式的全网图信息量很小。更好的做法是：按社团着色、节点大小映射某个中心性、只标注关键节点；或者干脆用统计图（度分布、中心性排名条形图、与零模型比较的箱线图）来呈现结论。更多图表原则见[研究结果的图表呈现](reporting-frontiers.figures.html)。
:::

网络图的视觉编码原则：

1. **一个视觉通道只编码一个变量**：节点颜色表示类别（社团、节点类型），节点大小表示一个连续量（度、中心性），边的粗细表示权重。类别颜色一般不超过 8 种左右，再多就难以分辨；连续量用单色渐变而非彩虹色。
2. **面积而非半径与数值成正比**：若半径与数值成正比，大节点会被视觉放大。
3. **标签要少**：只标注文中讨论的节点。
4. **稠密网络考虑矩阵视图**：边数远多于节点数时，按模块排序的邻接矩阵热图通常比节点–边图更清楚。
5. **展示用的阈值不等于分析用的阈值**：为了画图只显示最强的边是可以的，但要在图注中写明，且不能用这张图去“说明”分析结果。
6. **可复现**：固定布局随机种子、保存坐标；桌面软件中保存会话文件与样式文件。
7. **可读性**：考虑色觉障碍读者（避免只靠红绿区分）、黑白打印与缩印后的清晰度。

## 用模型网络与零模型解读真实网络 {#null-model-comparison}

判断小世界和无标度的方法见[小世界与无标度网络模型](network-models.html)，零模型的系统讨论见[零模型与空模型](network-construction.null-models.html)。实际研究中常见的做法是把真实网络的指标与几种模型网络（及零模型）放在一张表里比较：

| 指标 | 真实网络 | ER（同 $N$、$M$） | 保度随机化 | 解读 |
|---|---|---|---|---|
| 平均聚集系数 $C$ | | | | $C\gg C_{\text{rand}}$ 提示局部成团 |
| 平均最短路径 $L$ | | | | $L\approx L_{\text{rand}}$ 且 $C\gg C_{\text{rand}}$ 提示小世界 |
| 度同配系数 $r$ | | | | 生物网络常为负（枢纽连向低度节点） |
| 模块度 $Q$ | | | | 应与零模型的 $Q$ 比较，随机网络也能得到不小的 $Q$ |

小世界系数 $\sigma=\dfrac{C/C_{\text{rand}}}{L/L_{\text{rand}}}$，$\sigma>1$ 提示小世界性。零模型应多次生成（如 20–100 次），报告均值与标准差，必要时计算 $z$ 分数 $z=(X_{\text{real}}-\bar X_{\text{rand}})/s_{\text{rand}}$ 或经验 $p$ 值。

代码示例对《悲惨世界》人物共现网络（77 个节点，按无权图处理）做了这样的比较：真实网络 $C=0.573$，ER 零模型均值约 0.091，保度零模型均值约 0.199；平均最短路径与两种零模型接近（2.64 对约 2.5）；以 ER 为参照的小世界系数 $\sigma\approx5.9$。保度零模型的 $C$ 更接近真实值，说明一部分聚集来自度序列（几个高度人物）本身，这正是保度零模型“更严格”的含义。

::: {.callout-warn}
“度分布在双对数坐标下近似直线，所以是无标度网络”是研究报告中最常见的过度推断。幂律拟合需要专门的统计方法（最大似然估计、拟合优度检验、与对数正态等分布比较），而且很多生物网络的度分布更接近截断幂律或其他重尾分布。报告中写“度分布呈重尾”往往比写“无标度”更稳妥（参见[小世界与无标度网络模型](network-models.html)中关于“无标度是否普遍”的讨论，以及 [Clauset 2009](paper-clauset2009_powerlaw.html)、[Broido 2019](paper-broido2019_rare.html) 的论文精读）。
:::

## 完整案例：从表达矩阵到可检验的结论 {#case-study}

本节用一个**模拟**的共表达数据集，把前面各节串成一次完整分析。数据由代码生成，含已知答案（植入的模块与疾病基因），因此可以检查每一步是否把答案找回来了；真实分析的步骤相同，只是没有答案可对。完整代码见示例“完整案例”。

**研究问题**：一组候选疾病基因在共表达网络中是否比度相近的随机基因更聚集？若是，它们集中在哪个模块，模块的枢纽基因是哪些？

**数据**：200 个基因 × 60 个样本。160 个基因分属 4 个各含 40 个基因的模块，每个模块由一个潜在因子驱动（因子载荷 0.5–0.9）；另有 40 个噪声基因，其中 5 个几乎不随样本变化。各基因的表达尺度不同。疾病基因集含 12 个基因：8 个来自模块 0，4 个随机取自其他基因。

**第 1 步，质控**：去除方差极低的基因（表达几乎不变的基因，其相关系数主要由噪声决定）。去除 5 个，保留 195 个。

**第 2 步，估计边并控制假阳性**：计算 Spearman 相关（对异常值和非线性单调关系稳健，且不受表达尺度影响）。用 Fisher $z$ 变换求每个相关系数的 $p$ 值——对 Spearman 相关，$\operatorname{arctanh}(r_s)$ 的方差约为 $1.06/(n-3)$（Fieller 等 1957）——再用 Benjamini–Hochberg 方法在全部约 1.9 万个基因对上把错误发现率（FDR）控制在 0.01，只保留正相关。得到 2031 条边，密度约 0.11；34 个基因没有任何边，其中 33 个是噪声基因。这一步把“阈值取多少”转化为“容忍多大比例的假边”，阈值的含义更清楚（另见[阈值、加权与稀疏化](network-construction.thresholding.html)）。

**第 3 步，模块识别**：在去除孤立点后的加权网络上运行 Louvain（固定种子），得到 4 个模块，$Q\approx0.75$；与植入模块对照，调整兰德指数（ARI）约 0.98。真实数据没有“植入模块”，此时应当报告多次运行的稳定性，并用独立数据或功能注释检验模块（见[社团结果的验证与解读](community-structure.validation.html)）。

**第 4 步，枢纽基因**：在每个模块内部计算加权度（模块内连接度，与 WGCNA 中 intramodular connectivity 的思想一致，见 [WGCNA](gene-network-inference.wgcna.html)），列出每个模块中最高者作为候选枢纽。

**第 5 步，零模型检验**：疾病基因集中有 11 个在网络中（1 个随机选入的噪声基因成为孤立点而被去除）。用两种统计量衡量“聚集”：诱导子图最大连通分支（LCC）的大小，以及集合内部的边数。零模型是**度匹配的随机基因集**：把网络节点按度分为 10 个分位区间，每个疾病基因替换为同区间内的随机基因，重复 1000 次。结果：LCC 观测值 9，随机期望 4.5 ± 1.0，$z\approx4.7$；内部边数观测值 24，随机期望 10.1 ± 2.7，$z\approx5.1$；两者的经验 $p$ 值均约为 0.003。

**第 6 步，敏感性分析**：把 FDR 换成 0.001、0.05、0.1 重建网络并重复检验。内部边数在三种设置下都显著（$p$ 约 0.002–0.018）；LCC 在 FDR 0.001 与 0.05 下显著，在 FDR 0.1 时不再显著（观测 9，随机期望 7.0，$p\approx0.21$）。原因是网络变稠密后，随机基因集也很容易连成大分支，LCC 这个统计量趋于饱和。这提示：**统计量的选择与网络密度会相互作用**，应当预先指定主要统计量，并报告全部敏感性结果，而不是挑选显著的那个。

**结论的写法**：“在以 Spearman 相关、FDR 0.01 构建的共表达网络中，候选疾病基因的内部连接显著多于度匹配的随机基因集（$z\approx5.1$，经验 $p\approx0.003$），且对 FDR 水平稳健；以 LCC 衡量时，结论在较稠密的网络中不再成立。”这句话限定了网络构建方式、零模型和统计量，比“这些基因构成致病模块”更准确，也更容易被他人检验。

::: {.callout-bio}
**真实研究中的同一逻辑**。Menche 等（2015, *Science*）检验疾病基因在人类相互作用组中是否形成可观测的疾病模块：对每种疾病，计算其基因诱导子图的最大连通分支，并与度保持的随机基因集比较；他们同时讨论了相互作用组不完整对模块可观测性的影响（见 [Menche 2015](paper-menche2015_interactome.html) 与[疾病模块：定义与检测](network-medicine.disease-modules.html)）。共表达网络中的模块与模块内枢纽基因分析，则以 WGCNA（Zhang 与 Horvath 2005；Langfelder 与 Horvath 2008）的框架最为常用（见 [Zhang 2005](paper-zhang2005_wgcna.html)）。本案例的模拟数据只用于演示流程，其中的数值不代表任何真实疾病。
:::

## 常见生物医学网络数据与分析方向 {#biomedical-datasets}

下表整理了十类常见的生物医学网络、对应的公开数据来源与典型分析问题。

| # | 方向 | 数据来源 | 典型分析问题 |
|---|---|---|---|
| 1 | 脑网络分析 | Human Connectome Project（HCP）[humanconnectome.org](https://www.humanconnectome.org/) | 用 fMRI 构建功能脑网络，研究脑区连接强度；识别功能模块，比较其在视觉、记忆或运动等任务下的网络特性变化 |
| 2 | 蛋白质相互作用网络 | STRING [string-db.org](https://string-db.org/) | 针对一种疾病（如阿尔茨海默病）构建 PPI 网络，用度、介数等中心性找出关键蛋白，结合文献讨论其在疾病中的作用与成药潜力 |
| 3 | 基因调控网络 | GEO [ncbi.nlm.nih.gov/geo](https://www.ncbi.nlm.nih.gov/geo/) | 用某种癌症的表达数据构建基因调控（或共表达）网络，识别关键基因，解释其潜在机制与治疗意义 |
| 4 | 疾病关联网络 | DisGeNET [disgenet.com](https://disgenet.com/) | 构建多种疾病的基因关联网络，分析疾病间共享基因及其在共病机制中的作用 |
| 5 | 代谢网络 | KEGG [genome.jp/kegg](https://www.genome.jp/kegg/) | 构建代谢网络，分析度分布、聚类系数，识别高中心性代谢物，讨论网络的稳健性与脆弱性 |
| 6 | 微生物生态网络 | Earth Microbiome Project [earthmicrobiome.org](https://earthmicrobiome.org/) | 构建微生物共现网络（正、负相关），识别关键物种，分析温度、湿度等环境因素对网络结构的影响 |
| 7 | miRNA–基因调控网络 | miRTarBase（官网暂不可用，见 [2025 年 NAR 论文](https://doi.org/10.1093/nar/gkae1072)） | 构建 miRNA–靶基因调控网络，用中心性找出关键 miRNA，探讨其在某种疾病中的调控机制 |
| 8 | 药物–靶点网络 | DrugBank [go.drugbank.com](https://go.drugbank.com/) | 构建药物–靶点网络，分析药物间靶点重叠，寻找药物重定位线索，识别关键药物与关键靶点 |
| 9 | 癌症突变网络 | TCGA [cancer.gov/tcga](https://www.cancer.gov/tcga) | 用突变数据构建突变基因相互作用网络，识别高频突变基因，分析其网络地位、模块化与连通性 |
| 10 | 细胞信号传导网络 | Reactome [reactome.org](https://reactome.org/) | 构建信号传导网络，用中心性识别信号传递关键节点，分析或模拟信号传递路径 |

无论哪个方向，一个完整的分析通常包括：详细描述网络构建过程；解释所用网络指标及其生物学意义；列出关键节点并结合文献讨论；尽可能用独立数据集或文献支持结果的可靠性；讨论研究的应用前景与局限。各方向的专门方法见[脑连接组：结构与功能连接](brain-connectome.html)、[生物分子网络与拓扑特征](molecular-networks.html)、[基因调控网络推断与共表达分析](gene-network-inference.html)与[疾病模块、网络邻近度与药物重定位](network-medicine.html)。

不同方向的数据在读入时各有需要注意的地方：

| 方向 | 读入时的要点 |
|---|---|
| 脑网络 | 连接矩阵的行列顺序对应脑图谱的分区编号，必须同时保存图谱标签文件；对角线通常置零；功能连接含负值，需决定处理方式 |
| PPI | 标识符映射；无向边在完整文件中双向重复；按置信度或证据通道过滤；剔除预测来源或同源迁移来源时要写明 |
| 调控网络 | 方向（调控者 → 靶标）与符号（激活 / 抑制）是边属性，应读入 `DiGraph` 并保存符号 |
| 二部网络（药物–靶点、miRNA–靶基因） | 用节点属性 `bipartite=0/1` 区分两类节点；投影到单类网络会丢失信息并产生大量团，投影方式要说明 |
| 微生物共现 | 组成数据（相对丰度）直接求相关会产生虚假相关，应使用针对组成数据的方法 |

::: {.callout-warn}
**数据获取与合规**：HCP 数据需注册 ConnectomeDB 并同意其数据使用条款，个体数据不得再分发；DisGeNET 的免费学术许可只含人工审编数据，需申请；DrugBank 的学术下载需注册，目前暂停（截至 2026 年 11 月），可考虑 DGIdb 等替代来源（见[疾病模块、网络邻近度与药物重定位](network-medicine.html)的延伸资源）。初次分析可以先从下载即得的数据入手，例如 STRING 的人类 PPI 文件、TRRUST v2 转录调控关系、ENIGMA Toolbox 内置的 HCP 组平均连接组矩阵。不要把含个人信息的数据上传到任何公共平台或 AI 工具。
:::

## 数学推导与算法 {#derivations}

### Brandes 介数算法

节点 $v$ 的介数 $B(v)=\sum_{s\ne v\ne t}\sigma_{st}(v)/\sigma_{st}$，其中 $\sigma_{st}$ 是 $s$ 到 $t$ 的最短路径条数，$\sigma_{st}(v)$ 是其中经过 $v$ 的条数。按定义计算需要先求所有节点对的最短路径并逐对累加，代价为 $O(N^3)$。Brandes（2001）引入单源“依赖值”

$$
\delta_s(v)=\sum_{t}\frac{\sigma_{st}(v)}{\sigma_{st}},\qquad B(v)=\sum_{s\ne v}\delta_s(v),
$$

并证明它满足递推关系

$$
\delta_s(v)=\sum_{w:\,v\in P_s(w)}\frac{\sigma_{sv}}{\sigma_{sw}}\bigl(1+\delta_s(w)\bigr),
$$

其中 $P_s(w)$ 是从 $s$ 出发的最短路径上 $w$ 的前驱节点集合。于是对每个源点 $s$：先用 BFS（无权）或 Dijkstra（加权）求出到各点的距离、最短路径条数 $\sigma_{sv}$ 与前驱集合，再按距离从远到近回传依赖值。每个源点的代价为 $O(M)$（无权）或 $O(M+N\log N)$（加权），对全部源点求和即得上文的复杂度。

**抽样估计**：随机均匀抽取 $k$ 个源点组成集合 $S$，令 $\hat B(v)=\frac{N}{k}\sum_{s\in S}\delta_s(v)$。由于每个源点被抽中的概率为 $k/N$，$\mathbb E[\hat B(v)]=\sum_s\delta_s(v)=B(v)$，即估计无偏；其方差随 $k$ 增大大致按 $1/k$ 减小。高介数节点的依赖值来自很多源点，相对误差较小，这解释了为什么抽样介数对“前几名”的排序更可靠。

### 力导向布局的力与能量

Fruchterman–Reingold 设理想边长 $\ell=C\sqrt{\text{面积}/N}$，相距 $d$ 的节点之间：

$$
f_{\text{attr}}(d)=\frac{d^2}{\ell}\ (\text{仅相连节点}),\qquad f_{\text{rep}}(d)=-\frac{\ell^2}{d}\ (\text{所有节点对}).
$$

两力在 $d=\ell$ 时平衡。每次迭代按合力方向移动节点，位移不超过当前“温度”，温度逐步降低。朴素实现每步需计算全部节点对的斥力，代价 $O(N^2)$。

Kamada–Kawai 的能量函数为

$$
E=\sum_{i<j}\frac{1}{2}\,\frac{K}{d_{ij}^2}\bigl(\lVert \mathbf x_i-\mathbf x_j\rVert-\ell\, d_{ij}\bigr)^2,
$$

其中 $d_{ij}$ 是图上最短路径距离，$\ell$ 是单位边长。权重 $1/d_{ij}^2$ 使近邻之间的距离误差受到更大惩罚。最小化 $E$ 相当于一种加权的多维尺度分析。

ForceAtlas2 的斥力为 $F_r=k_r\,(\deg(i)+1)(\deg(j)+1)/d$，吸引力为 $F_a=d$（LinLog 模式下为 $\log(1+d)$），另加一个把节点拉向中心的“重力”项。斥力中的度因子让枢纽彼此远离，而只连接一个枢纽的低度节点留在其附近。

### 谱布局的推导

设一维坐标 $\mathbf x\in\mathbb R^N$，希望相连节点尽量靠近：

$$
\min_{\mathbf x}\ \frac{1}{2}\sum_{i,j}A_{ij}(x_i-x_j)^2=\mathbf x^{\top}L\mathbf x,\qquad L=D-A .
$$

不加约束时 $\mathbf x$ 全部相同即可取到 0，所以加上约束 $\mathbf x^{\top}\mathbf x=1$ 且 $\mathbf x\perp\mathbf 1$（排除平凡解）。由瑞利商的性质，最优解是 $L$ 的第二小特征值对应的特征向量（Fiedler 向量）；二维布局的第二个坐标取与之正交的下一个特征向量，即第三小特征值的特征向量（Hall 1970）。由于 $\mathbf x^{\top}L\mathbf x$ 正是图分割中“割边数”的连续松弛，谱布局与谱聚类有相同的数学基础，这解释了它为何能把社团分得很开（见[谱方法与层次聚类](community-structure.spectral-hierarchical.html)）。

### 稀疏存储的内存

CSR（compressed sparse row）格式用三个数组存储矩阵：非零值 `data`（长度 nnz）、列索引 `indices`（长度 nnz）、行指针 `indptr`（长度 $N+1$）。无向图 nnz $=2M$。以 64 位浮点值和 64 位整数索引计（代码示例中 SciPy 返回的即为 64 位索引；若为 32 位索引，则约为 1.52 MB），内存约为 $2M\times(8+8)+8(N+1)$ 字节。代码示例中 $N=20000$、$M=59991$，得到约 2.08 MB；同样大小的稠密矩阵为 $N^2\times8\approx3.2\times10^9$ 字节。对稀疏网络，稀疏存储的优势随 $N$ 线性扩大。

### 度匹配随机基因集的经验 $p$ 值

设观测统计量为 $T_{\text{obs}}$，$R$ 个度匹配随机集合的统计量为 $T_1,\dots,T_R$。经验 $p$ 值

$$
\hat p=\frac{1+\#\{r: T_r\ge T_{\text{obs}}\}}{R+1}.
$$

分子分母加 1 保证 $\hat p>0$，可达到的最小 $p$ 值为 $1/(R+1)$（详见[零模型与空模型](network-construction.null-models.html)）。度匹配的理由是：度高的基因在几乎任何网络统计量上都占优势，若疾病基因恰好偏向高度（常见于研究较多的基因），不做度匹配会把“度偏倚”误当成“聚集”。

## 研究前沿与开放问题 {#frontiers}

- **软件实现之间的一致性**：同一指标在不同软件中的定义与默认参数存在差异，跨研究比较时可能造成系统偏差。如何在报告中规范地写出“计算定义”（而不仅是指标名称），仍缺乏统一做法；[可复算的分析](reproducible-research.reproducible-analysis.html)中的版本记录与环境锁定是目前最实际的手段。
- **后端分派与硬件加速**：NetworkX 的后端机制让同一份代码可以在 CPU 并行或 GPU 上运行，降低了从原型到大规模计算的迁移成本；不同后端在随机算法、浮点运算顺序上的差异是否影响结论，需要在使用时核对。
- **大规模网络的统计推断**：精确零模型（大量保度随机化）在百万级网络上代价很高，解析的最大熵零模型、抽样估计与近似算法的误差控制是活跃的方法问题。
- **从网络图到可交互的可视分析**：网页端可交互网络（如 Cytoscape.js）、多尺度与层次化的展示、带不确定性的网络可视化（例如把边的自举支持率编码为透明度），都还在发展中。
- **图机器学习的工程化**：节点嵌入与图神经网络在药物重定位、疾病基因预测中被广泛使用（见[异质网络、知识图谱与图机器学习](network-medicine.knowledge-graphs.html)），其数据划分（防止信息泄漏）、负样本选择与基线比较需要比传统网络分析更严格的流程设计。

## 生物医学应用 {#biomedical}

网络分析在生物医学研究中最常见的“套路”是：从数据库或实验数据构建网络 → 计算中心性找“关键节点” → 做功能富集 → 用文献“验证”。这个流程上手快，但也最容易得出不可靠的结论。几个值得在研究设计中主动避免的问题：

- **研究偏倚**：研究得越多的蛋白，记录的相互作用越多，度就越高。PPI 网络中“疾病基因度高”部分反映的是研究热度，而非生物学重要性。可以用只含高通量实验的数据（如 HuRI）或控制文献数量来检验；在零模型中做度匹配（见[完整案例](analysis-workflow.case-study.html)）也是常用的控制办法。
- **循环论证**：用已知疾病基因作种子构建网络，再发现网络中心是已知疾病基因，并不能证明方法有效。
- **相关不等于调控**：共表达网络的边是统计相关，不是调控关系（详见[基因调控网络推断与共表达分析](gene-network-inference.html)）。
- **“验证”要独立**：用于发现的数据和用于验证的数据应当不同；富集分析要选择合适的背景基因集（例如以网络中的全部基因而非全基因组为背景）。
- **网络不完整**：现有相互作用组只覆盖真实相互作用的一部分，且覆盖并不均匀。子网络的性质不等于全网络的性质（Stumpf 等 2005），“某基因没有连接”可能只是数据缺失。

::: {.callout-bio}
**工具与生物医学研究的结合**。Cytoscape 最初就是为整合生物分子相互作用网络与表达谱等高通量数据而设计的（Shannon 等 2003, *Genome Research*），至今仍是 PPI 与通路分析的常用平台。脑网络研究中，Rubinov 与 Sporns（2010, *NeuroImage*）系统整理了脑连接指标的定义与解释，并以 Brain Connectivity Toolbox 提供实现，成为该领域最常引用的指标参考之一（见 [Rubinov 2010](paper-rubinov2010_measures.html)）。两者都说明：工具的选择不仅关乎速度，还决定了研究者默认使用哪一套指标定义。
:::

[网络可控性与稳定性](controllability.html)专题中介绍的控制核心点研究、症状网络模块控制研究，都在方法中包含了富集分析、方法对比或自举稳定性检验，可以作为研究设计的参照。

## 适用范围与常见误用 {#limitations}

1. **误区**：先下载数据，再想研究问题。→ **正解**：先写出具体问题和假设，再选择能回答它的数据和网络构建方式。
2. **误区**：网络构建只是预处理，不重要。→ **正解**：节点、边、阈值的定义决定了后面的所有结果，需要说明理由并做敏感性分析。
3. **误区**：模块度 $Q$ 很高就说明网络有显著的社团结构。→ **正解**：随机网络也能得到不小的 $Q$，需要与零模型比较；Louvain 结果有随机性，要报告稳定性。
4. **误区**：度分布在双对数图上像直线，就是无标度网络。→ **正解**：需要严格的统计检验；多数情况下写“重尾分布”更稳妥。
5. **误区**：中心性最高的节点就是“致病基因”或“药物靶点”。→ **正解**：中心性只是候选筛选依据，要结合研究偏倚、功能富集和独立证据讨论。
6. **误区**：把相关系数或置信度直接作为 `weight` 传给最短路径、介数、接近中心性。→ **正解**：这些函数把权重当距离，需先转换为 $1/w$ 或 $-\log w$；模块度、强度等则直接使用强度。
7. **误区**：网络图上两个簇离得远，说明它们在生物学上关系疏远。→ **正解**：力导向布局中簇间距离与相对位置一般没有可解释的含义；需要用图距离或统计量说明。
8. **误区**：网络太大，就随机抽一部分节点分析，结论推广到全网络。→ **正解**：诱导子图的度分布、聚集系数等都会系统性改变；应过滤或改用近似算法与更快的工具，并说明抽样方式。
9. **误区**：换了软件，指标数值不同，说明有一个算错了。→ **正解**：先核对定义与默认参数（归一化、非连通处理、加权推广）。

NetworkX 本身的适用范围：适合中小规模网络与方法原型；对几十万节点以上的网络，介数、最短路径等全局计算会很慢，应先过滤、使用抽样近似、启用后端，或改用 igraph、graph-tool、NetworKit。

## 关联知识 {#related}

- [网络结构指标与随机图](network-metrics.html)：度、聚集系数、路径长度、中心性与 ER 随机图的定义，是本专题所有计算的理论来源。
- [复杂系统与网络的数学表示](network-basics.html)：邻接矩阵、边列表与稀疏性，是数据格式与稀疏计算的数学基础。
- [小世界与无标度网络模型](network-models.html)：小世界系数与幂律检验的理论背景。
- [社团结构与社区发现](community-structure.html)：模块度、Louvain 与谱方法的原理与局限，与谱布局共享数学基础。
- [网络构建与统计验证](network-construction.html)：从原始测量到网络的构建选择、零模型与统计检验。
- [研究问题、可复现分析与敏感性分析](reproducible-research.html)：把本专题的流程做成可复算、可检验的研究；[结果呈现与研究前沿](reporting-frontiers.html)：网络分析结果的图表呈现与科学报告。
- [生物分子网络与拓扑特征](molecular-networks.html)、[疾病模块、网络邻近度与药物重定位](network-medicine.html)：同一流程在 PPI 与网络医学中的应用。
- [网络上的传播与免疫](spreading.html)：社会网络中传播效应的推断及其方法学争议。

## 核心文献 {#references}

### Hagberg、Schult 与 Swart 2008：Exploring network structure, dynamics, and function using NetworkX

- **背景**：NetworkX 的原始介绍论文，发表于 SciPy 2008 会议论文集，说明了库的设计理念：用 Python 字典表示图，节点可以是任意可哈希对象，边可以携带任意属性。
- **核心内容**：数据结构、算法覆盖、与 NumPy/SciPy 的衔接，以及在流行病学等领域的使用示例。
- **阅读提示**：论文很短，重点理解“图就是字典的字典”这一数据结构，它解释了为什么 NetworkX 灵活但在大规模网络上较慢。在研究中使用 NetworkX 时，应引用这篇论文。
- **思考题**：你所分析的网络有多少节点和边？NetworkX 在哪一步可能成为瓶颈？有什么替代方案？

### Barabási、Gulbahce 与 Loscalzo 2011：Network medicine: a network-based approach to human disease（Nature Reviews Genetics）

- **背景**：疾病很少由单一基因决定，网络医学试图在分子相互作用网络中理解疾病。
- **核心内容**：人类相互作用组的构成与不完整性；疾病模块假说；网络中的疾病基因发现、疾病之间的关系与药物作用；网络方法的局限。
- **阅读提示**：可以把这篇综述当作确定研究方向的“地图”——[常见生物医学网络数据与分析方向](analysis-workflow.biomedical-datasets.html)中的方向 2、3、4、8、9 都可以在其中找到对应的问题框架。注意文中关于数据不完整和研究偏倚的讨论。论文精读见 [Barabási 2011](paper-barabasi2011_networkmedicine.html)。
- **思考题**：在你关注的方向中，“疾病模块”可以如何定义和检验？需要什么样的零模型？

DOI：[10.1038/nrg2918](https://doi.org/10.1038/nrg2918)

### Christakis 与 Fowler 2007 及其批评（另见[网络上的传播与免疫](spreading.html)）

- **为什么放在这里**：这是“网络分析得出强结论、随后受到方法学批评”的典型案例，对设计自己的网络分析很有启发。
- **阅读提示**：对照阅读原文的方法部分与批评文章，列出自己的分析可能面临的同类问题（混杂、同质性、选择偏倚），并在研究设计阶段写出应对办法。
- **思考题**：如果一项分析的结论是“A 与 B 在网络中相邻，因此 A 可能调控 B”，审稿人最可能提出哪些质疑？

DOI：[10.1056/NEJMsa066082](https://doi.org/10.1056/NEJMsa066082)

### Brandes 2001：A faster algorithm for betweenness centrality（Journal of Mathematical Sociology）

- **核心内容**：通过单源依赖值的递推，把介数计算从 $O(N^3)$ 降到无权图 $O(NM)$，是 NetworkX、igraph 等软件中介数实现的基础。Brandes 与 Pich（2007, *International Journal of Bifurcation and Chaos*）进一步研究了只取部分源点的抽样估计及源点的选取策略。
- **阅读提示**：对照[数学推导与算法](analysis-workflow.derivations.html)中的递推式，理解为什么要按距离从远到近回传。

DOI：[10.1080/0022250X.2001.9990249](https://doi.org/10.1080/0022250X.2001.9990249)；Brandes 与 Pich 2007：[10.1142/S0218127407018403](https://doi.org/10.1142/S0218127407018403)

### Rubinov 与 Sporns 2010：Complex network measures of brain connectivity: uses and interpretations（NeuroImage）

- **核心内容**：系统整理脑网络常用指标在二值、加权、有向网络中的定义与解释，配套 Brain Connectivity Toolbox；讨论了权重与“连接长度”之间的转换。
- **阅读提示**：与本专题“权重是相似度还是距离”一节对照阅读。论文精读见 [Rubinov 2010](paper-rubinov2010_measures.html)。

DOI：[10.1016/j.neuroimage.2009.10.003](https://doi.org/10.1016/j.neuroimage.2009.10.003)

### 软件与方法文献

| 文献 | 内容 | DOI |
|---|---|---|
| Shannon 等 2003, *Genome Research* | Cytoscape：整合生物分子相互作用网络的软件环境 | [10.1101/gr.1239303](https://doi.org/10.1101/gr.1239303) |
| Bastian、Heymann 与 Jacomy 2009, *Proceedings of ICWSM* | Gephi：网络探索与操作的开源软件 | [10.1609/icwsm.v3i1.13937](https://doi.org/10.1609/icwsm.v3i1.13937) |
| Csárdi 与 Nepusz 2006, *InterJournal Complex Systems* 1695 | igraph 软件包的介绍 | — |
| Peixoto 2014, The graph-tool python library（figshare） | graph-tool 的引用文献 | — |
| Staudt、Sazonovs 与 Meyerhenke 2016, *Network Science* | NetworKit：大规模网络分析工具集 | [10.1017/nws.2016.20](https://doi.org/10.1017/nws.2016.20) |
| Virtanen 等 2020, *Nature Methods* | SciPy 1.0，含稀疏矩阵与 csgraph 模块 | [10.1038/s41592-019-0686-2](https://doi.org/10.1038/s41592-019-0686-2) |
| Fruchterman 与 Reingold 1991, *Software: Practice and Experience* | 力导向布局 | [10.1002/spe.4380211102](https://doi.org/10.1002/spe.4380211102) |
| Kamada 与 Kawai 1989, *Information Processing Letters* | 基于图距离的弹簧能量布局 | [10.1016/0020-0190(89)90102-6](https://doi.org/10.1016/0020-0190(89)90102-6) |
| Jacomy 等 2014, *PLoS ONE* | ForceAtlas2 布局 | [10.1371/journal.pone.0098679](https://doi.org/10.1371/journal.pone.0098679) |
| Hall 1970, *Management Science* | 二次布局与拉普拉斯特征向量（谱布局的思想来源） | [10.1287/mnsc.17.3.219](https://doi.org/10.1287/mnsc.17.3.219) |
| Sugiyama、Tagawa 与 Toda 1981, *IEEE Transactions on Systems, Man, and Cybernetics* | 层次结构的分层布局 | [10.1109/TSMC.1981.4308636](https://doi.org/10.1109/TSMC.1981.4308636) |
| Krzywinski 等 2012, *Briefings in Bioinformatics* | Hive plot：基于规则的网络可视化 | [10.1093/bib/bbr069](https://doi.org/10.1093/bib/bbr069) |
| Opsahl、Agneessens 与 Skvoretz 2010, *Social Networks* | 加权网络中度与最短路径类中心性的推广 | [10.1016/j.socnet.2010.03.006](https://doi.org/10.1016/j.socnet.2010.03.006) |
| Riondato 与 Kornaropoulos 2016, *Data Mining and Knowledge Discovery* | 带误差保证的介数抽样近似 | [10.1007/s10618-015-0423-0](https://doi.org/10.1007/s10618-015-0423-0) |
| Stumpf、Wiuf 与 May 2005, *PNAS* | 无标度网络的子网一般不是无标度的 | [10.1073/pnas.0501179102](https://doi.org/10.1073/pnas.0501179102) |
| Leskovec 与 Faloutsos 2006, *Proceedings of KDD* | 大图抽样方法的比较 | [10.1145/1150402.1150479](https://doi.org/10.1145/1150402.1150479) |
| Menche 等 2015, *Science* | 不完整相互作用组中的疾病模块与 LCC 检验 | [10.1126/science.1257601](https://doi.org/10.1126/science.1257601) |
| Langfelder 与 Horvath 2008, *BMC Bioinformatics* | WGCNA 软件包：加权共表达网络、模块与模块内连接度 | [10.1186/1471-2105-9-559](https://doi.org/10.1186/1471-2105-9-559) |
| Benjamini 与 Hochberg 1995, *Journal of the Royal Statistical Society B* | 错误发现率（FDR）控制 | [10.1111/j.2517-6161.1995.tb02031.x](https://doi.org/10.1111/j.2517-6161.1995.tb02031.x) |
| Fieller、Hartley 与 Pearson 1957, *Biometrika* | 秩相关系数的检验，含 Fisher $z$ 变换后的方差近似 | [10.1093/biomet/44.3-4.470](https://doi.org/10.1093/biomet/44.3-4.470) |

## 延伸资源 {#resources}

| 类型 | 资源 | 说明 |
|---|---|---|
| 官方教程 | NetworkX Tutorial（[链接](https://networkx.org/documentation/stable/tutorial.html)） | 建图、属性、读写、绘图的官方入门，约 1 小时 |
| 官方文档 | NetworkX 后端说明（[链接](https://networkx.org/documentation/stable/backends.html)） | nx-parallel、nx-cugraph 等后端的启用方式 |
| 官方文档 | NetworkX 绘图与布局（[链接](https://networkx.org/documentation/stable/reference/drawing.html)） | 全部布局函数；文档建议用专门工具作网络图 |
| 官方教程 | nx-guides：Facebook 网络探索分析（[链接](https://networkx.org/nx-guides/content/exploratory_notebooks/facebook_notebook.html)） | 加载真实网络→度分布→聚类→社团→可视化的完整流程，可照着改成生物网络；CC0 |
| 教材 | Menczer、Fortunato 与 Davis，*A First Course in Network Science*（Cambridge University Press, 2020；DOI [10.1017/9781108653947](https://doi.org/10.1017/9781108653947)）；配套 NetworkX 教程（[GitHub](https://github.com/CambridgeUniversityPress/FirstCourseNetworkScience)） | 基本元素、小世界、枢纽、方向与权重、模型、社团、动力学七章均配有 Jupyter 实践 |
| 教材 | Barabási，*Network Science*（[在线版](http://networksciencebook.com/)） | 网络科学概念的系统参考，可与本专题的计算对照 |
| 官方文档 | igraph（[igraph.org](https://igraph.org/)）、graph-tool（[graph-tool.skewed.de](https://graph-tool.skewed.de/)）、NetworKit（[networkit.github.io](https://networkit.github.io/)） | 需要更快实现或特定算法（Leiden、SBM 推断）时查阅 |
| 官方文档 | Brain Connectivity Toolbox（[网站](https://sites.google.com/site/bctnet/)）、bctpy（[GitHub](https://github.com/aestrivex/bctpy)） | 脑网络指标的 MATLAB 与 Python 实现 |
| 官方文档 | SciPy sparse 与 csgraph（[链接](https://docs.scipy.org/doc/scipy/reference/sparse.html)） | 稀疏矩阵格式、稀疏线性代数与图算法 |
| 中文视频 | 同济子豪兄：图机器学习 NetworkX 代码实战——创建图和可视化（[B 站](https://www.bilibili.com/video/BV1kM41147zV/)） | 29 分钟中文 NetworkX 上手 |
| 中文视频 | 四十分钟掌握 Gephi（[B 站](https://www.bilibili.com/video/BV1Cx4y1r7K3/)） | Gephi 导入、布局、统计、导出的中文教程 |
| 中文视频 | PPI 网络：蛋白互作网络的构建与核心基因的筛选（STRING + Cytoscape + CytoNCA）（[B 站](https://www.bilibili.com/video/BV1n34y1b7by/)） | PPI 方向最常用的操作流程；注意本专题“生物医学应用”中关于研究偏倚的提醒 |
| 官方教程 | Cytoscape Tutorials（[链接](https://cytoscape.org/cytoscape-tutorials/)） | 生物网络可视化、STRING 导入、聚类与富集分析 |
| 数据 | STRING 下载页（[链接](https://string-db.org/cgi/download)） | 人类 PPI 文件约 83 MB（压缩），CC BY 4.0，下载即可用 |
| 数据 | ENIGMA Toolbox 内置 HCP 组平均连接组（[文档](https://enigma-toolbox.readthedocs.io/en/latest/pages/05.HCP/index.html)） | 一行代码读取结构与功能连接矩阵，免去处理原始影像，适合脑网络分析入门 |

## 开放问题 {#questions}

1. 用 3 句话写出一个你感兴趣的网络研究问题：（1）生物医学问题是什么；（2）网络的节点和边是什么；（3）希望用哪一个网络指标或算法回答它。其中哪一环最薄弱？
2. 在[常见生物医学网络数据与分析方向](analysis-workflow.biomedical-datasets.html)中任选一个，列出构建网络时至少 3 个会显著影响结果的选择（如阈值、数据来源、是否加权），并说明怎样做敏感性分析来证明结论稳健。
3. 你的网络中的边权表示的是相似度、强度还是距离？在你打算使用的每一个指标中，权重分别被当作哪一种？是否需要同时保存两种属性？
4. 在[完整案例](analysis-workflow.case-study.html)中，LCC 与内部边数两种统计量在较稠密的网络中给出不同结论。对你的研究问题，应当预先指定哪一种作为主要统计量？理由是什么？
5. 如果你的网络有 50 万个节点，需要找出介数最高的 100 个节点，你会依次尝试哪些策略？怎样检验近似结果足够可靠？
