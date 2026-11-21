# %% [markdown]
# # 人类蛋白质相互作用网络的“体检”：度、距离、聚集、中心性与 k 核
#
# 本案例对一张真实的人类蛋白质物理相互作用网络逐项计算[网络结构指标](network-metrics.html)：度与密度、连通分支、最短路径与效率、聚集系数、几种中心性和 k 核，并把每一项与同样大小的 ER 随机网络比较（[真实网络与随机网络的比较](network-metrics.real-vs-random.html)）。
#
# **1. 数据来源**
#
# - 数据：STRING v12.0 人类（taxon 9606）**物理**相互作用子网络 `9606.protein.physical.links.v12.0.txt.gz`，蛋白名映射自 `9606.protein.info.v12.0.txt.gz`，下载自 `https://stringdb-downloads.org/`（2026-11-20）。
# - 许可证：**CC BY 4.0**（`https://string-db.org/cgi/access`）。引用：Szklarczyk D 等, The STRING database in 2023, *Nucleic Acids Research* 2023, DOI [10.1093/nar/gkac1000](https://doi.org/10.1093/nar/gkac1000)。
# - 裁剪：只保留综合分数（combined score）≥ 700 的“高置信”边，蛋白 ID 换成 STRING 首选基因名，每对只留一行，存为 `data/string_human_physical_v12_s700.csv`（列：`protein1, protein2, score`）。
#
# STRING 的“物理”子网络表示两个蛋白属于同一个物理复合物的证据（实验、数据库、文本挖掘等通道综合），分数是置信度而不是结合强度。阈值 700 是 STRING 推荐的“高置信”档，换阈值会改变网络，这一点放在最后讨论。

# %% [markdown]
# ## 2. 读入与清洗
#
# 读入边表，确认没有自环和重复边，查看分数分布，再找出连通分支。

# %%
import time
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from scipy import stats

t0 = time.time()
E = pd.read_csv("data/string_human_physical_v12_s700.csv")
print("边表行数:", len(E), "；自环:", int((E.protein1 == E.protein2).sum()))
pairs = {tuple(sorted(p)) for p in zip(E.protein1, E.protein2)}
print("不同的无序蛋白对:", len(pairs))
print("分数分位数（25%, 50%, 75%）:", E.score.quantile([0.25, 0.5, 0.75]).tolist(), "；分数 ≥ 900 的边占 %.0f%%" % (100 * (E.score >= 900).mean()))

G = nx.Graph()
G.add_edges_from(zip(E.protein1, E.protein2))
N, M = G.number_of_nodes(), G.number_of_edges()
comps = sorted(nx.connected_components(G), key=len, reverse=True)
print("N = %d，M = %d，连通分支 %d 个" % (N, M, len(comps)))
print("最大的 5 个分支的大小:", [len(c) for c in comps[:5]])
print("最大连通分支（LCC）占 %.1f%% 的节点" % (100 * len(comps[0]) / N))
size_counts = pd.Series([len(c) for c in comps[1:]]).value_counts().sort_index()
print("其余分支的大小分布:", dict(size_counts.head(6)))

# %% [markdown]
# ## 3. 构网
#
# 后面的距离类指标只在最大连通分支上计算（[连通分支与巨连通分支](network-metrics.components.html)）；度、聚集系数、k 核在整张网络上计算。对照组是同样 $N$、$M$ 的 ER 随机网络 $G(N,M)$，固定随机种子。

# %%
LCC = G.subgraph(comps[0]).copy()
ER = nx.gnm_random_graph(N, M, seed=2026)
ER_lcc = ER.subgraph(max(nx.connected_components(ER), key=len)).copy()
print("LCC: N = %d，M = %d" % (LCC.number_of_nodes(), LCC.number_of_edges()))
print("ER:  最大连通分支占 %.1f%% 的节点，孤立节点 %d 个" % (100 * ER_lcc.number_of_nodes() / N, nx.number_of_isolates(ER)))

# %% [markdown]
# ## 4. 核心指标
#
# ### 4.1 度、密度与度分布
#
# 平均度 $\langle k\rangle = 2M/N$，密度 $\rho = \langle k\rangle/(N-1)$。度的不均匀性用 $\langle k^2\rangle/\langle k\rangle$ 和最大度来看。

# %%
k = np.array([d for _, d in G.degree()])
k_er = np.array([d for _, d in ER.degree()])
print("平均度 %.2f，中位数 %d，最大度 %d，密度 %.5f" % (k.mean(), np.median(k), k.max(), nx.density(G)))
print("度为 1 的蛋白占 %.1f%%" % (100 * (k == 1).mean()))
print("<k²>/<k>：真实 %.1f，ER %.1f" % ((k ** 2).mean() / k.mean(), (k_er ** 2).mean() / k_er.mean()))
print("最大度：真实 %d，ER %d" % (k.max(), k_er.max()))
deg = dict(G.degree())
print("度最高的 10 个蛋白:", sorted(deg.items(), key=lambda x: -x[1])[:10])

# %% [markdown]
# ### 4.2 最短路径、直径与全局效率
#
# LCC 有上万个节点，逐对求最短路径代价较大。这里随机抽 300 个源节点做广度优先搜索（BFS），用到其他所有节点的距离估计平均路径长度 $L$、距离分布和全局效率；直径的下界取抽样中出现的最大距离。抽样估计的误差可以用不同种子重复检验。

# %%
def sample_distances(H, n_src=300, seed=0):
    rng = np.random.default_rng(seed)
    nodes = list(H.nodes())
    src = rng.choice(len(nodes), size=min(n_src, len(nodes)), replace=False)
    dist = []
    for s in src:
        dist.extend(d for d in nx.single_source_shortest_path_length(H, nodes[s]).values() if d > 0)
    return np.array(dist)

d_real = sample_distances(LCC, seed=1)
d_er = sample_distances(ER_lcc, seed=1)
print("平均路径长度 L：真实 %.2f，ER %.2f；理论估计 ln N / ln<k> = %.2f" %
      (d_real.mean(), d_er.mean(), np.log(N) / np.log(k.mean())))
print("抽样中最大距离（直径下界）：真实 %d，ER %d" % (d_real.max(), d_er.max()))
print("全局效率（LCC 内）：真实 %.3f，ER %.3f" % ((1 / d_real).mean(), (1 / d_er).mean()))
print("另一组种子下的 L：%.2f" % sample_distances(LCC, seed=7).mean())

# %% [markdown]
# ### 4.3 聚集系数
#
# 平均聚集系数 $C=\frac1N\sum_i C_i$ 对每个节点等权，传递性 $T$ 相当于按“连通三元组”加权，二者在高度节点很多的网络中可能差别很大（[聚集系数](network-metrics.clustering.html)）。ER 网络的期望聚集系数约为 $p=\rho$。

# %%
C_real, T_real = nx.average_clustering(G), nx.transitivity(G)
C_er, T_er = nx.average_clustering(ER), nx.transitivity(ER)
print("平均聚集系数 C：真实 %.3f，ER %.4f（理论 p = %.4f）" % (C_real, C_er, nx.density(G)))
print("传递性 T：真实 %.3f，ER %.4f" % (T_real, T_er))
print("C / C_ER = %.0f" % (C_real / C_er))
clust = nx.clustering(G)

# %% [markdown]
# ### 4.4 中心性与 k 核
#
# - 度中心性、介数中心性（抽 300 个源节点近似，固定种子）、PageRank（阻尼因子 0.85）；
# - k 核分解给出每个节点的核数，最内层的核是网络最稠密的部分（[k 核分解](network-metrics.k-core.html)）。
#
# 再看几种排序之间的斯皮尔曼相关：若高度相关，说明它们在这张网络里提供的信息相近。

# %%
bc = nx.betweenness_centrality(LCC, k=300, seed=3)
pr = nx.pagerank(LCC, alpha=0.85)
core = nx.core_number(G)
lcc_nodes = list(LCC.nodes())
kv = np.array([deg[n] for n in lcc_nodes])
bv = np.array([bc[n] for n in lcc_nodes])
pv = np.array([pr[n] for n in lcc_nodes])
cv = np.array([core[n] for n in lcc_nodes])
print("斯皮尔曼相关：度–介数 %.2f，度–PageRank %.2f，度–核数 %.2f" %
      (stats.spearmanr(kv, bv)[0], stats.spearmanr(kv, pv)[0], stats.spearmanr(kv, cv)[0]))
print("介数最高的 10 个蛋白:", [n for n, _ in sorted(bc.items(), key=lambda x: -x[1])[:10]])
kmax_core = max(core.values())
inner = sorted(n for n, c in core.items() if c == kmax_core)
print("最大核数 = %d，最内层核有 %d 个蛋白，例如 %s" % (kmax_core, len(inner), inner[:12]))
top_b = sorted(bc, key=bc.get, reverse=True)[:100]
top_k = set(sorted(deg, key=deg.get, reverse=True)[:100])
print("介数前 100 与度前 100 的重叠: %d 个" % len(set(top_b) & top_k))
# 介数排名前 100、但度相对最低的蛋白：可能起“桥”的作用
bridges = sorted(top_b, key=deg.get)[:8]
print("介数前 100 中度最低的 8 个蛋白:", [(n, deg[n]) for n in bridges])

# %% [markdown]
# ## 5. 与零模型比较
#
# 把主要指标放进一张表，用多个 ER 样本给出随机网络的取值范围（这里用 5 个样本，聚集系数在 ER 样本间几乎不变）。

# %%
rows = []
for s in range(5):
    R = nx.gnm_random_graph(N, M, seed=100 + s)
    rows.append((nx.transitivity(R), max(d for _, d in R.degree()),
                 max(len(c) for c in nx.connected_components(R)) / N))
rows = np.array(rows)
table = pd.DataFrame({
    "真实网络": [k.mean(), k.max(), len(comps[0]) / N, C_real, T_real, d_real.mean()],
    "ER（5 个样本均值）": [k_er.mean(), rows[:, 1].mean(), rows[:, 2].mean(), C_er, rows[:, 0].mean(), d_er.mean()],
}, index=["平均度", "最大度", "LCC 比例", "平均聚集系数", "传递性", "平均路径长度"])
print(table.round(3).to_string())
print("用时 %.0f 秒" % (time.time() - t0))

# %% [markdown]
# ## 6. 作图
#
# 左：度分布的互补累积分布 $P(K\ge k)$（双对数坐标），真实网络与 ER 对照。中：最短路径长度的分布。右：度与介数的关系，右下方偏离主趋势的点是“度不高但处在许多最短路径上”的蛋白。

# %%
def ccdf(x):
    xs = np.sort(np.unique(x))
    return xs, np.array([(x >= v).mean() for v in xs])

fig, ax = plt.subplots(1, 3, figsize=(14, 4))
for arr, lab, col in [(k, "STRING human (score ≥ 700)", "#2b6cb0"), (k_er, "ER G(N, M)", "#a0aec0")]:
    xs, ys = ccdf(arr[arr > 0])
    ax[0].loglog(xs, ys, "o", ms=3, label=lab, color=col)
ax[0].set_xlabel("degree k")
ax[0].set_ylabel("P(K ≥ k)")
ax[0].legend()
bins = np.arange(0.5, max(d_real.max(), d_er.max()) + 1.5)
ax[1].hist(d_real, bins=bins, density=True, alpha=0.7, label="real", color="#2b6cb0")
ax[1].hist(d_er, bins=bins, density=True, alpha=0.5, label="ER", color="#a0aec0")
ax[1].set_xlabel("shortest-path length")
ax[1].legend()
ax[2].loglog(kv, bv + 1e-7, ".", ms=2, color="#dd6b20")
ax[2].set_xlabel("degree k")
ax[2].set_ylabel("betweenness (approx.)")
fig.tight_layout()

# %% [markdown]
# ## 7. 解读与局限
#
**结果。** 高置信物理网络有 10 746 个蛋白、86 519 条边，分成 344 个连通分支；最大连通分支包含 9 830 个蛋白（91.5%），其余几乎都是 2–3 个蛋白的小碎片。平均度 16.1，但中位数只有 6，17.8% 的蛋白只有 1 个伙伴，最大度达 434（RPS27A）；$\langle k^2\rangle/\langle k\rangle$ 为 66.1，而同规模 ER 网络只有 17.1、最大度 33——度分布高度不均匀。度最高的是泛素前体（RPS27A、UBA52、UBC）和组蛋白，它们的高度很大程度上反映了“被共价修饰的蛋白很多”和“组蛋白基因多拷贝”，并不都是信号枢纽。
#
# 聚集系数 0.466（传递性 0.516），是 ER 网络（≈ $p$ = 0.0015）的约 300 倍，这是真实网络与随机网络最显著的差别。平均路径长度约 4.8（两组抽样 4.78 与 4.72），比同等规模的 ER 网络（3.65）长约 1 步，抽样中最远的距离为 14，而 ER 只有 5；全局效率也略低（0.226 对 0.283）。也就是说，这张网络仍然是“小世界”的量级（$L$ 与 $\ln N$ 同阶），但并不比随机网络更短。一个可能的原因是：边集中在稠密的复合物内部，而大量度为 1–2 的边缘蛋白只通过细长的链与核心相连，这会拉长平均路径。
#
# 几种中心性中，度与核数几乎一致（斯皮尔曼 0.98），与 PageRank 也高度相关（0.89），与介数的相关较弱（0.65）：介数前 100 与度前 100 只重叠 17 个。介数最高的是 TP53、EGFR、RPS27A、CTNNB1、ACTB、HSP90AA1 等，它们连接着不同的功能区域，而度最高的组蛋白介数并不高。最内层的 87 核由 88 个蛋白组成，按字母排在前面的有 CDK7、CCNH、ERCC2、ERCC3 和 GTF2 家族等转录起始与核苷酸切除修复（TFIIH）相关蛋白：k 核挑出的是稠密的复合物核心，而不是“最重要”的蛋白。
#
# **局限。**
#
# - **阈值依赖**：分数 ≥ 700 是一个约定。阈值降低，边和节点都会增多，平均度上升、路径变短；比较不同网络时要用相同的构网规则，并报告结果对阈值的敏感性（见[研究问题、可复现分析与敏感性分析](reproducible-research.html)）。
# - **STRING 的“物理”边不全是直接结合**：它表示“同属一个复合物”的综合证据，包括文本挖掘和数据库转移来的证据；大复合物（核糖体、蛋白酶体等）会以团的形式出现，抬高聚集系数。
# - **研究偏倚与数据不完整**：被研究得多的蛋白证据多、度高；约三分之一的人类蛋白在这一阈值下没有任何边，不在网络中。
# - **抽样估计**：平均路径长度、效率和介数都用 300 个源节点近似，换种子会有小幅波动；直径只给出下界。
# - **ER 是最弱的对照**：它连度分布都不保留。要问“聚集系数高是不是仅由度分布造成”，应改用保持度序列的随机化（见[配置模型](network-models.configuration-model.html)与[度保持随机化检验](degree-correlations.randomization-tests.html)）。
