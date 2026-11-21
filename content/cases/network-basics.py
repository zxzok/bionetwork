# %% [markdown]
# # 从原始相互作用记录到网络：人类 DNA 修复蛋白的 BioGRID 数据
#
# 数据库里下载下来的并不是一张“图”，而是一行一行的实验记录。同一对蛋白可能被几十篇文献、几种实验方法反复报道；有的记录是蛋白与自身结合；有的是物理结合，有的是遗传相互作用。本案例从这些原始记录出发，一步步做出[图的定义与基本类型](network-basics.graph-types.html)里的各种决定，并把结果写成[邻接矩阵](network-basics.adjacency-matrix.html)、[边列表与稀疏矩阵](network-basics.edge-list-sparsity.html)、[拉普拉斯矩阵](network-basics.laplacian-matrices.html)和[二分网络的投影](network-basics.bipartite-networks.html)。
#
# **1. 数据来源**
#
# - 相互作用记录：BioGRID 5.0.263 人类数据（`BIOGRID-ORGANISM-Homo_sapiens-5.0.263.tab3.txt`），下载自 `https://downloads.thebiogrid.org/BioGRID/Release-Archive/BIOGRID-5.0.263/`（2026-11-20）。许可证：**MIT**。引用：Oughtred R 等, The BioGRID interaction database: 2019 update, *Nucleic Acids Research* 2019, DOI [10.1093/nar/gky1079](https://doi.org/10.1093/nar/gky1079)。
# - 基因集：Reactome 第 98 版通路 R-HSA-73894“DNA Repair”（346 个基因），许可证 **CC0**。引用：Milacic M 等, The Reactome Pathway Knowledgebase 2024, *Nucleic Acids Research* 2024, DOI [10.1093/nar/gkad1025](https://doi.org/10.1093/nar/gkad1025)。
# - 裁剪：只保留两个相互作用者都在这 346 个基因中的人类记录，**不合并重复**，存为 `data/biogrid_human_dna_repair_records.csv`。每行一条记录：两个基因符号、实验方法、类型（physical / genetic）、通量（低通量 / 高通量）、文献编号。
#
# 选 DNA 修复通路，是因为它的成员（BRCA1、TP53、ATM、PCNA 等）被研究得很多，正好能看清“记录很多、网络不大”的现象，也能看出研究偏倚。

# %% [markdown]
# ## 2. 读入与清洗
#
# 先清点原始记录：一共有多少行、多少种实验方法、物理与遗传各占多少、有多少条是蛋白与自身的相互作用（自环）。

# %%
import collections
import numpy as np
import pandas as pd
import networkx as nx
import scipy.sparse as sp
import matplotlib.pyplot as plt
from networkx.algorithms import bipartite

rec = pd.read_csv("data/biogrid_human_dna_repair_records.csv")
print("记录数:", len(rec), "；列:", list(rec.columns))
print("\n物理 / 遗传:\n", rec["system_type"].value_counts().to_string())
print("\n记录最多的 5 种实验方法:\n", rec["experimental_system"].value_counts().head(5).to_string())
print("\n通量:\n", rec["throughput"].value_counts().to_string())
self_rec = rec[rec.interactor_a == rec.interactor_b]
print("\n自身相互作用记录:", len(self_rec), "条，涉及", self_rec.interactor_a.nunique(), "个蛋白")

# 无序基因对：A–B 与 B–A 是同一对
rec["pair"] = [tuple(sorted(p)) for p in zip(rec.interactor_a, rec.interactor_b)]
per_pair = rec.groupby("pair").size()
print("\n不同的无序基因对:", len(per_pair), "；平均每对", round(len(rec) / len(per_pair), 2), "条记录")
print("记录最多的 5 对:\n", per_pair.sort_values(ascending=False).head(5).to_string())

# %% [markdown]
# ## 3. 构网：多重图 → 简单图 → 加权图
#
# 同一份数据可以得到几种不同的图，选哪种取决于研究问题：
#
# - **多重图**：每条记录一条边，保留了全部重复与自环；
# - **简单无向图**：同一对只留一条边，去掉自环——这是多数网络指标默认的输入；
# - **加权图**：把“支持这对相互作用的独立文献数”作为边权 $w_{ij}$，权重粗略反映证据的多少（不是结合强度）；
# - 只保留物理相互作用、并要求至少 2 篇文献支持，是常见的“高可信”过滤。
#
# 物理结合是对称关系，所以这里都用无向图；表中 A、B 两列的先后只是记录格式，不代表方向。

# %%
phys = rec[rec.system_type == "physical"]
MG = nx.MultiGraph()
MG.add_edges_from(zip(phys.interactor_a, phys.interactor_b))
print("多重图：节点 %d，边 %d，自环 %d" % (MG.number_of_nodes(), MG.number_of_edges(), nx.number_of_selfloops(MG)))

no_self = phys[phys.interactor_a != phys.interactor_b]
w = no_self.groupby("pair")["publication"].nunique()       # 每对的独立文献数
G = nx.Graph()
for (a, b), k in w.items():
    G.add_edge(a, b, weight=int(k))
print("简单加权图：节点 %d，边 %d" % (G.number_of_nodes(), G.number_of_edges()))
G2 = nx.Graph([(a, b) for (a, b), k in w.items() if k >= 2])
print("至少 2 篇文献支持：节点 %d，边 %d（保留了 %.0f%% 的边）"
      % (G2.number_of_nodes(), G2.number_of_edges(), 100 * G2.number_of_edges() / G.number_of_edges()))

# %% [markdown]
# ## 4. 核心量：度、密度、矩阵表示
#
# 对简单图验证握手定理 $\sum_i k_i = 2M$，计算密度 $\rho = 2M/[N(N-1)]$。再把它写成三种矩阵：
#
# - 邻接矩阵 $A$：对称、对角线为 0；用稀疏格式存储时只记非零元素；
# - 拉普拉斯矩阵 $L = D - A$：每行和为 0；零特征值的个数等于连通分支数；
# - 关联矩阵 $B$（$N\times M$，每列两个 1）：满足 $BB^{\mathsf T} = D + A$。

# %%
nodes = sorted(G.nodes())
N, M = G.number_of_nodes(), G.number_of_edges()
deg = dict(G.degree())
print("度之和 = %d，2M = %d" % (sum(deg.values()), 2 * M))
print("平均度 = %.2f，密度 = %.4f" % (2 * M / N, nx.density(G)))
top = sorted(deg.items(), key=lambda x: -x[1])[:8]
print("度最高的 8 个蛋白:", top)

A = nx.to_scipy_sparse_array(G, nodelist=nodes, weight=None, format="csr")
print("\n邻接矩阵 %d×%d，非零元素 %d（= 2M），对称: %s" % (N, N, A.nnz, (A != A.T).nnz == 0))
dense_bytes = N * N * 8
sparse_bytes = A.data.nbytes + A.indices.nbytes + A.indptr.nbytes
print("稠密存储 %.0f KB，CSR 稀疏存储 %.0f KB" % (dense_bytes / 1024, sparse_bytes / 1024))

L = nx.laplacian_matrix(G, nodelist=nodes, weight=None).toarray().astype(float)
ev = np.linalg.eigvalsh(L)
print("L 的行和全为 0:", np.allclose(L.sum(axis=1), 0))
print("接近 0 的特征值个数 = %d，连通分支数 = %d" % ((ev < 1e-8).sum(), nx.number_connected_components(G)))
print("代数连通度 λ2 = %.3f" % ev[1])

B = nx.incidence_matrix(G, nodelist=nodes).toarray()
Ad = A.toarray()
print("B 的形状:", B.shape, "；B·Bᵀ = D + A:", np.allclose(B @ B.T, np.diag(Ad.sum(1)) + Ad))

# %% [markdown]
# **二分网络与投影。** 记录里的“文献编号”把数据变成了“蛋白–文献”二分网络：一篇文献连向它报道过的所有蛋白。投影到蛋白一侧，就得到“共同出现在同一篇文献中”的网络。投影会制造大量三角形：一篇报道了 $n$ 个蛋白的高通量文献，投影后就是一个 $n(n-1)/2$ 条边的完全子图。

# %%
Bp = nx.Graph()
Bp.add_nodes_from(nodes, bipartite=0)
papers = sorted(no_self.publication.unique())
Bp.add_nodes_from(papers, bipartite=1)
Bp.add_edges_from({(a, p) for a, b, p in zip(no_self.interactor_a, no_self.interactor_b, no_self.publication)} |
                  {(b, p) for a, b, p in zip(no_self.interactor_a, no_self.interactor_b, no_self.publication)})
pdeg = {p: Bp.degree(p) for p in papers}
print("文献数 %d；每篇文献涉及的蛋白数：中位数 %d，最多 %d" %
      (len(papers), np.median(list(pdeg.values())), max(pdeg.values())))
P = bipartite.projected_graph(Bp, nodes)
print("投影网络：边 %d，是相互作用网络边数的 %.1f 倍" % (P.number_of_edges(), P.number_of_edges() / M))
print("三角形数：相互作用网络 %d，投影网络 %d" %
      (sum(nx.triangles(G).values()) // 3, sum(nx.triangles(P).values()) // 3))
print("相互作用网络的每条边都在投影里:", all(P.has_edge(u, v) for u, v in G.edges()))

# %% [markdown]
# ## 5. 与零模型比较
#
# **度的不均匀性。** 用同样 $N$、$M$ 的 ER 随机图 $G(N,M)$ 作参照，看真实网络的最大度和度的方差是不是远超随机。
#
# **物理层与遗传层的重叠。** 把物理相互作用和遗传相互作用看成同一组节点上的两层（[多层网络](network-basics.multilayer-hypergraphs.html)）。如果两层互不相关，遗传层的边落在物理层边上的个数服从超几何分布；比较观测重叠与这个期望。

# %%
rng = np.random.default_rng(1)
kmax_null, var_null = [], []
for s in range(200):
    R = nx.gnm_random_graph(N, M, seed=int(rng.integers(1e9)))
    d = np.array([k for _, k in R.degree()])
    kmax_null.append(d.max())
    var_null.append(d.var())
d_obs = np.array(list(deg.values()))
print("最大度：观测 %d，ER 平均 %.1f（200 个样本中最大 %d）" % (d_obs.max(), np.mean(kmax_null), max(kmax_null)))
print("度方差：观测 %.1f，ER 平均 %.1f" % (d_obs.var(), np.mean(var_null)))

from scipy.stats import hypergeom
gen = rec[(rec.system_type == "genetic") & (rec.interactor_a != rec.interactor_b)]
gen_pairs = set(gen.pair)
phys_pairs = set(w.index)
layer_nodes = sorted({x for p in gen_pairs | phys_pairs for x in p})
n_all_pairs = len(layer_nodes) * (len(layer_nodes) - 1) // 2
overlap = len(gen_pairs & phys_pairs)
expected = len(gen_pairs) * len(phys_pairs) / n_all_pairs
p_val = hypergeom.sf(overlap - 1, n_all_pairs, len(phys_pairs), len(gen_pairs))
print("\n遗传层 %d 对，物理层 %d 对，可能的基因对 %d" % (len(gen_pairs), len(phys_pairs), n_all_pairs))
print("两层重叠：观测 %d 对，随机期望 %.1f 对，超几何检验 p = %.1e" % (overlap, expected, p_val))

# %% [markdown]
# ## 6. 作图
#
# 左：按度从高到低排列节点后的邻接矩阵（每个点是一条边），能看出少数高度节点占据了大量边。中：每对蛋白的记录数分布，长尾说明“同一对被反复报道”很常见。右：度分布的直方图（对数纵轴）。

# %%
order = [n for n, _ in sorted(deg.items(), key=lambda x: -x[1])]
Ao = nx.to_scipy_sparse_array(G, nodelist=order, weight=None)
fig, ax = plt.subplots(1, 3, figsize=(13, 4))
ax[0].spy(Ao, markersize=0.3, color="#2b6cb0")
ax[0].set_title("adjacency (nodes sorted by degree)")
cnt = per_pair.value_counts().sort_index()
ax[1].bar(cnt.index[:30], cnt.values[:30], color="#718096")
ax[1].set_xlabel("records per gene pair")
ax[1].set_ylabel("number of pairs")
ax[1].set_yscale("log")
ax[2].hist(d_obs, bins=40, color="#dd6b20")
ax[2].set_yscale("log")
ax[2].set_xlabel("degree k")
ax[2].set_ylabel("number of proteins")
fig.tight_layout()

# %% [markdown]
# ## 7. 解读与局限
#
# **结果。** 18 308 条原始记录只对应 5 052 个基因对，平均每对 3.62 条记录，BARD1–BRCA1 一对就有 118 条；713 条记录是蛋白与自身结合（涉及 183 个蛋白，多为同源二聚化等），在简单图里被去掉。物理相互作用占 98.7%，遗传相互作用只有 245 条。只用物理记录、去掉自环、合并重复后，简单图有 303 个蛋白、4 727 条边，平均度 31.2，密度约 0.10——对于一张通路内部的网络，这已相当稠密，全蛋白质组网络的密度要低得多。只保留“至少 2 篇文献支持”的边，只剩 2 010 条（43%），可见过滤条件对网络大小影响很大，必须写进方法。
#
# 邻接矩阵对称、非零元素数等于 $2M=9454$；拉普拉斯矩阵只有 1 个零特征值，说明这张网络是连通的；$BB^{\mathsf T}=D+A$ 在真实数据上同样成立。即使只有 303 个节点，CSR 稀疏格式也只占稠密存储的约五分之一，网络越大、越稀疏，这个差距越悬殊。蛋白–文献二分网络中，一半的文献只涉及 2 个蛋白，但最大的一篇涉及 228 个；投影后的边数是相互作用网络的 7.7 倍，三角形多了约 94 倍：“出现在同一篇文献里”不等于“相互作用”，投影网络的聚集程度主要是少数大文献造成的。
#
# 度最高的是单链 DNA 结合蛋白复合物 RPA 的三个亚基（RPA1 166、RPA2 163、RPA3 144）以及 BRCA1、TP53、TOPBP1、泛素 UBC。最大度 166 远高于同等规模 ER 图的最大度（200 个样本中最大 55），度方差约是 ER 的 26 倍。遗传层与物理层重叠 74 对，是随机期望（22 对）的 3 倍多，说明两类证据指向相关的生物学关系；但它们仍是两种不同含义的边，不宜不加说明地合并。
#
# **局限。**
#
# - **研究偏倚**：BRCA1、TP53、PCNA 等明星分子被研究得多，记录和边都多；高度部分反映的是“被关注的程度”，不全是生物学重要性（见[适用范围与常见误用](network-basics.limitations.html)）。
# - **节点集合是人为选定的**：只看 Reactome 中 DNA 修复通路的成员，通路外的伙伴全被截掉；这是一张诱导子图，度和密度都不能推广到全蛋白质组。
# - **记录数不等于证据强度**：一篇高通量文献可以贡献大量记录，同一实验室的重复报道也不独立；这里用“独立文献数”作边权只是粗略做法。
# - **物理结合不说明功能关系与方向**：亲和纯化可能捕获间接结合（同一复合物中的成员），双杂交可能有假阳性。泛素 UBC 成为枢纽，部分是因为许多蛋白被泛素共价修饰后一起被捕获，这与“两个蛋白稳定结合”不是一回事。
# - BioGRID 持续更新，换一个版本，记录数会变；分析时应记录版本号和下载日期（见[网络数据格式与数据来源](network-basics.data-formats.html)）。
