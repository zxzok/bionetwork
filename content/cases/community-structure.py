# %% [markdown]
# # 社团能找回通路吗？人类蛋白质网络中 8 条 Reactome 通路的社团发现
#
# 社团发现最常被问的问题是：算法找到的社团有没有生物学意义？本案例先**事先**选定 8 条功能差别明显的 Reactome 通路，取它们的成员蛋白在 STRING 高置信物理网络中的诱导子网络；然后**不看通路标签**做社团发现，最后再把社团与通路比较（NMI、ARI、列联表），并用保持度序列的随机网络检验模块度是否显著（[社团结果的验证与解读](community-structure.validation.html)）。
#
# **1. 数据来源**
#
# - 网络：STRING v12.0 人类物理相互作用子网络（综合分数 ≥ 700），`data/string_human_physical_v12_s700.csv`，来自 `https://stringdb-downloads.org/`（2026-11-20 下载）。许可证 **CC BY 4.0**。引用：Szklarczyk D 等, *Nucleic Acids Research* 2023, DOI [10.1093/nar/gkac1000](https://doi.org/10.1093/nar/gkac1000)。
# - 通路：Reactome 第 98 版 `ReactomePathways.gmt`，`https://reactome.org/download/current/ReactomePathways.gmt.zip`（2026-11-20 下载），许可证 **CC0**。引用：Milacic M 等, The Reactome Pathway Knowledgebase 2024, *Nucleic Acids Research* 2024, DOI [10.1093/nar/gkad1025](https://doi.org/10.1093/nar/gkad1025)。裁剪为 8 条通路的“通路–基因”表 `data/reactome_selected_pathways.csv`。
# - 8 条通路：线粒体复合物 I 组装、胞质 tRNA 氨酰化、蛋白酶体组装、胆固醇合成、前复制复合物激活、线粒体翻译延伸、三羧酸循环、胶原形成。它们分属能量代谢、翻译、蛋白降解、脂质合成、DNA 复制和细胞外基质，选择时只看功能，不看网络。

# %% [markdown]
# ## 2. 读入与清洗
#
# 属于两条以上所选通路的基因无法给出唯一标签，先去掉；再只保留在 STRING 网络中出现的基因。

# %%
import time
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

t0 = time.time()
pw = pd.read_csv("data/reactome_selected_pathways.csv")
short = {"Complex I biogenesis": "Complex I", "Cytosolic tRNA aminoacylation": "tRNA aa",
         "Proteasome assembly": "Proteasome", "Cholesterol biosynthesis": "Cholesterol",
         "Activation of the pre-replicative complex": "Pre-RC", "Mitochondrial translation elongation": "Mito transl",
         "Citric acid cycle (TCA cycle)": "TCA", "Collagen formation": "Collagen"}
pw["label"] = pw.pathway.map(short)
n_path = pw.groupby("gene").label.nunique()
multi = set(n_path[n_path > 1].index)
print("通路–基因行数 %d，基因 %d 个，属于多条通路的 %d 个: %s" % (len(pw), pw.gene.nunique(), len(multi), sorted(multi)))
pw = pw[~pw.gene.isin(multi)]
label = dict(zip(pw.gene, pw.label))

E = pd.read_csv("data/string_human_physical_v12_s700.csv")
in_net = set(E.protein1) | set(E.protein2)
genes = sorted(g for g in label if g in in_net)
print("在 STRING 网络中的基因: %d / %d" % (len(genes), len(label)))

# %% [markdown]
# ## 3. 构网：诱导子网络
#
# 只保留两端都在这些基因中的边（诱导子网络），以 STRING 分数/1000 作为边权（备用）。去掉在子网络中没有任何边的基因。

# %%
gs = set(genes)
sub = E[E.protein1.isin(gs) & E.protein2.isin(gs)]
G = nx.Graph()
for a, b, s in zip(sub.protein1, sub.protein2, sub.score):
    G.add_edge(a, b, weight=s / 1000)
nodes = sorted(G.nodes())
truth = np.array([label[n] for n in nodes])
print("子网络：N = %d，M = %d，连通分支 %d 个，未进入子网络的基因 %d 个" %
      (G.number_of_nodes(), G.number_of_edges(), nx.number_connected_components(G), len(gs) - G.number_of_nodes()))
summary = pd.DataFrame({"基因数": pd.Series(truth).value_counts()})
inside = {}
for lab in summary.index:
    members = [n for n in nodes if label[n] == lab]
    tot = sum(d for _, d in G.degree(members))
    internal = G.subgraph(members).number_of_edges()
    inside[lab] = 2 * internal / tot if tot else np.nan
summary["边落在通路内的比例"] = pd.Series(inside).round(2)
print(summary.to_string())

# %% [markdown]
# ## 4. 核心指标：模块度、社团与通路的一致性
#
# - 社团发现用 Louvain（不用边权，10 个随机种子）和贪婪模块度算法（Clauset–Newman–Moore）。
# - 一致性用两个指标：**NMI**（归一化互信息，算术平均归一化，1 为完全一致）与 **ARI**（调整兰德指数，随机划分期望为 0）。
# - 同时计算“以通路为划分”时的模块度 $Q$，作为参照。

# %%
def as_labels(parts, nodes):
    lab = {}
    for i, c in enumerate(parts):
        for n in c:
            lab[n] = i
    return np.array([lab[n] for n in nodes])

def contingency(a, b):
    ua, ia = np.unique(a, return_inverse=True)
    ub, ib = np.unique(b, return_inverse=True)
    T = np.zeros((len(ua), len(ub)))
    np.add.at(T, (ia, ib), 1)
    return T

def nmi(a, b):
    T = contingency(a, b)
    n = T.sum()
    pa, pb, pab = T.sum(1) / n, T.sum(0) / n, T / n
    nz = pab > 0
    I = (pab[nz] * np.log(pab[nz] / np.outer(pa, pb)[nz])).sum()
    Ha, Hb = -(pa * np.log(pa)).sum(), -(pb * np.log(pb)).sum()
    return 2 * I / (Ha + Hb)

def ari(a, b):
    T = contingency(a, b)
    c2 = lambda x: x * (x - 1) / 2
    s, sa, sb, n = c2(T).sum(), c2(T.sum(1)).sum(), c2(T.sum(0)).sum(), c2(T.sum())
    exp = sa * sb / n
    return (s - exp) / ((sa + sb) / 2 - exp)

truth_parts = [set(n for n in nodes if label[n] == lab) for lab in summary.index]
Q_truth = nx.community.modularity(G, truth_parts, weight=None)
print("以 8 条通路为划分：Q = %.3f" % Q_truth)

runs = []
for seed in range(10):
    parts = nx.community.louvain_communities(G, weight=None, seed=seed)
    lab = as_labels(parts, nodes)
    runs.append((nx.community.modularity(G, parts, weight=None), len(parts), nmi(truth, lab), ari(truth, lab), lab))
R = pd.DataFrame([r[:4] for r in runs], columns=["Q", "社团数", "NMI", "ARI"])
print("Louvain 10 个种子：\n", R.describe().loc[["mean", "min", "max"]].round(3).to_string())
best = max(runs, key=lambda r: r[0])
louv = best[4]
pair_nmi = [nmi(runs[i][4], runs[j][4]) for i in range(10) for j in range(i + 1, 10)]
print("不同种子划分之间的 NMI：平均 %.3f，最低 %.3f" % (np.mean(pair_nmi), np.min(pair_nmi)))

cnm = nx.community.greedy_modularity_communities(G)
lab_cnm = as_labels(cnm, nodes)
print("贪婪模块度：Q = %.3f，社团 %d 个，NMI = %.3f，ARI = %.3f" %
      (nx.community.modularity(G, cnm, weight=None), len(cnm), nmi(truth, lab_cnm), ari(truth, lab_cnm)))

# %% [markdown]
# **分辨率参数。** 广义模块度 $Q_\gamma=\frac1{2m}\sum_{ij}\left(A_{ij}-\gamma\frac{k_ik_j}{2m}\right)\delta(c_i,c_j)$ 中，$\gamma$ 越大社团越小越多（[多分辨率与共识聚类](community-structure.multiresolution-consensus.html)）。扫描 $\gamma$，看哪个尺度与通路最一致。

# %%
scan = []
for gam in [0.25, 0.5, 1.0, 1.5, 2.0, 3.0]:
    parts = nx.community.louvain_communities(G, weight=None, resolution=gam, seed=0)
    lab = as_labels(parts, nodes)
    scan.append((gam, len(parts), nmi(truth, lab), ari(truth, lab)))
scan = pd.DataFrame(scan, columns=["γ", "社团数", "NMI", "ARI"])
print(scan.round(3).to_string(index=False))

# %% [markdown]
# ## 5. 与零模型比较
#
# 对子网络做保持度序列的双边交换，生成 20 个随机网络，在每个上面同样运行 Louvain，得到“只由度序列造成”的模块度分布。

# %%
Q_null = []
for s in range(20):
    H = nx.Graph(G.edges())
    nx.double_edge_swap(H, nswap=10 * H.number_of_edges(), max_tries=1000 * H.number_of_edges(), seed=500 + s)
    Q_null.append(nx.community.modularity(H, nx.community.louvain_communities(H, seed=0)))
Q_null = np.array(Q_null)
Q_best = best[0]
print("真实子网络 Louvain Q = %.3f；随机网络 Q = %.3f ± %.3f；z = %.1f" %
      (Q_best, Q_null.mean(), Q_null.std(), (Q_best - Q_null.mean()) / Q_null.std()))
print("用时 %.0f 秒" % (time.time() - t0))

# %% [markdown]
# ## 6. 作图
#
# 左：通路（行）× Louvain 社团（列）的列联表，每格为基因数；一行集中在一列，说明该通路被完整找回；一行分散在多列，说明它被拆开；一列包含多行，说明几条通路被合并。中：真实网络的 $Q$ 与随机网络 $Q$ 的分布。右：按 Louvain 社团着色的网络图。

# %%
T = contingency(truth, louv)
row_names = np.unique(truth)
order = np.argsort(-T.sum(0))
fig, ax = plt.subplots(1, 3, figsize=(16, 4.8))
im = ax[0].imshow(T[:, order], cmap="Blues", aspect="auto")
ax[0].set_yticks(range(len(row_names)))
ax[0].set_yticklabels(row_names)
ax[0].set_xlabel("Louvain community")
for i in range(T.shape[0]):
    for j in range(T.shape[1]):
        v = T[i, order[j]]
        if v > 0:
            ax[0].text(j, i, int(v), ha="center", va="center", fontsize=7)
ax[1].hist(Q_null, bins=10, color="#a0aec0", label="degree-preserving null")
ax[1].axvline(Q_best, color="#c53030", lw=2, label="observed")
ax[1].set_xlabel("modularity Q")
ax[1].legend()
pos = nx.spring_layout(G, seed=1)
nx.draw_networkx_edges(G, pos, ax=ax[2], alpha=0.15, width=0.5)
nx.draw_networkx_nodes(G, pos, nodelist=nodes, node_color=louv, cmap="tab20", node_size=12, ax=ax[2])
ax[2].set_axis_off()
fig.tight_layout()

# %% [markdown]
# ## 7. 解读与局限
#
**结果。** 去掉 8 个跨通路基因（多为线粒体编码的复合物 I 亚基）后，416 个基因中有 374 个在 STRING 高置信网络里，诱导子网络有 350 个蛋白、5 916 条边，分成 18 个连通分支。各通路的边几乎都落在通路内部（胶原、蛋白酶体、前复制复合物为 100%，最低的复合物 I 也有 89%），所以以通路为划分时 $Q=0.540$ 已经很高。
#
# Louvain 在 10 个种子下给出完全相同的划分（种子之间 NMI = 1），$Q=0.578$，比通路划分还略高；22 个社团与通路的 NMI 为 0.873、ARI 为 0.86，贪婪模块度算法结果几乎一样（21 个社团，NMI 0.873，ARI 0.854）。社团数多于 8，是因为 18 个连通分支中的小碎片各自成为社团，大通路也有被拆成几块的（见列联表）。在保持度序列的随机网络上，Louvain 只能得到 $Q=0.102\pm0.003$，真实值远高于零模型（$z\approx168$）。分辨率 $\gamma$ 在 0.25–1.5 之间结果基本不变；$\gamma\ge2$ 时社团数骤增到一百多个，大通路被切碎，NMI 和 ARI 明显下降——在这张网络里，最接近通路的尺度正好是常规的 $\gamma=1$，但在其他网络中未必如此，应当扫描。
#
# 结论：对功能差别明显、内部高度连接的通路，纯粹由网络结构得到的社团可以很好地找回它们；但这个高一致性在很大程度上来自设定本身（见局限）。
#
# **局限。**
#
# - **这是一个“容易”的设定**：8 条通路是按功能差异挑出来的，诱导子网络又去掉了它们与网络其他部分的连接。在全蛋白质组网络上，社团会受分辨率极限和枢纽的影响，与通路的一致性会差得多（见[模块度](community-structure.modularity.html)中的分辨率极限）。
# - **通路不是“真值”**：Reactome 通路是人为整理的功能单元，一条通路可以包含多个物理复合物（如胶原形成既有胶原链，也有修饰酶），一个复合物也可以参与多条通路。社团与通路不一致不一定是算法错了。
# - **循环论证的风险**：STRING 的“数据库”证据通道部分来自通路与复合物数据库，社团与通路的一致性有一部分是数据来源相同造成的；更严格的检验可以只用实验证据通道构网。
# - **随机性与稳定性**：Louvain 结果随种子变化，应报告多次运行的一致性；这里只用了 20 个零模型样本，$z$ 分数只是粗略的参照。
