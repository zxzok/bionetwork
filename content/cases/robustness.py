# %% [markdown]
# # 酵母蛋白相互作用网络的鲁棒性：随机失效、蓄意攻击与必需基因
#
# 本案例用 BioGRID 中实验测定的酿酒酵母蛋白物理相互作用，完整做一次网络鲁棒性分析：由度分布算出 Molloy–Reed 判据与理论随机失效阈值，模拟随机删点、按初始度攻击、按自适应度攻击和按初始介数攻击，计算最大连通分支曲线、$f_c$ 与 R 指标，并与保度随机化网络和同规模 ER 网络比较；最后用 SGD 的基因敲除表型，检验“结构碎裂”与“功能丧失（致死）”是不是同一回事。所用定义与[渗流理论与网络碎裂](robustness.percolation.html)、[生成函数方法与 Molloy–Reed 判据](robustness.generating-functions.html)、[蓄意攻击](robustness.targeted-attack.html)、[鲁棒性度量](robustness.robustness-measures.html)、[生物系统的鲁棒性](robustness.biological-robustness.html)一致。
#
# ## 1. 数据来源
#
# - 相互作用：BioGRID 5.0.263（文件 `BIOGRID-ORGANISM-Saccharomyces_cerevisiae_S288c-5.0.263.tab3.txt`，<https://downloads.thebiogrid.org/BioGRID/Release-Archive/BIOGRID-5.0.263/>，2026-11-20 下载）。许可证：MIT（<https://wiki.thebiogrid.org/doku.php/terms_and_conditions>）。引用：Oughtred R, et al.（2019）The BioGRID interaction database: 2019 update. *Nucleic Acids Research* 47(D1):D529–D541。
# - 整理：只保留物理相互作用（去掉遗传相互作用以及 Affinity Capture-RNA、Protein-RNA 两类蛋白–RNA 记录），按无序蛋白对合并，**只保留至少 2 篇独立文献报告过的蛋白对**，得到 `data/yeast_ppi_biogrid.csv`（25 006 对，`n_pub` 为支持文献数）。这一筛选去掉了大量只被单次高通量实验报告的相互作用，代价是网络更小、更偏向被研究得多的蛋白。
# - 必需性：酵母基因组数据库（SGD）表型注释 `phenotype_data.tab`（<https://downloads.yeastgenome.org/curation/literature/phenotype_data.tab>，2026-11-20 下载），许可证 CC BY 4.0。在实验类型为 “systematic mutation set”（全基因组缺失株集合）、突变类型为 null 的注释中，只有 “inviable” 的基因记为必需（1），只有 “viable” 的记为非必需（0），其余为空，见 `data/yeast_genes_essential.csv`。引用：Engel SR, et al.（2022）*Genetics* 220: iyab224。

# %% [markdown]
# ## 2. 读入与清洗
#
# 检查自环与重复对，统计支持文献数的分布；必需性表中空值（注释冲突或缺失）的基因在分析必需性时排除，但仍保留在网络里。

# %%
import time
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

t0 = time.time()
ppi = pd.read_csv("data/yeast_ppi_biogrid.csv")
genes = pd.read_csv("data/yeast_genes_essential.csv")
print("蛋白对 %d 条；自环 %d；重复对 %d" % (len(ppi), (ppi.a == ppi.b).sum(), ppi.duplicated(["a", "b"]).sum()))
print("支持文献数 n_pub：中位数 %d，≥5 篇的占 %.1f%%" % (ppi.n_pub.median(), 100 * (ppi.n_pub >= 5).mean()))
print("基因表 %d 个：必需 %d，非必需 %d，未定 %d"
      % (len(genes), (genes.essential == 1).sum(), (genes.essential == 0).sum(), genes.essential.isna().sum()))

# %% [markdown]
# ## 3. 构网
#
# 节点是蛋白（以 ORF 系统名标识），无向边表示至少两篇文献报告的物理相互作用。鲁棒性分析在**最大连通分支**上进行（$N$ 取最大分支的节点数），这是渗流文献的通常做法。

# %%
G0 = nx.from_pandas_edgelist(ppi, "a", "b")
comps = sorted(nx.connected_components(G0), key=len, reverse=True)
G = G0.subgraph(comps[0]).copy()
print("全网 %d 个蛋白、%d 条边、%d 个连通分支；最大分支 %d 个蛋白（%.1f%%）、%d 条边"
      % (G0.number_of_nodes(), G0.number_of_edges(), len(comps), G.number_of_nodes(),
         100 * G.number_of_nodes() / G0.number_of_nodes(), G.number_of_edges()))
nodes = list(G.nodes())
idx = {v: i for i, v in enumerate(nodes)}
N = len(nodes)
eu = np.array([(idx[u], idx[v]) for u, v in G.edges()])
k = np.bincount(eu.ravel(), minlength=N).astype(float)
sym = dict(zip(genes.orf, genes.symbol))
print("<k> = %.2f，<k^2> = %.1f，最大度 %d（%s）" % (k.mean(), (k**2).mean(), k.max(), sym.get(nodes[int(k.argmax())])))
print("度最高的 10 个蛋白:", [sym.get(nodes[i]) for i in np.argsort(-k)[:10]])
print("平均聚集系数 %.3f，度同配系数 %.3f" % (nx.average_clustering(G), nx.degree_assortativity_coefficient(G)))

# %% [markdown]
# ## 4. 核心指标
#
# **（1）理论阈值。** $\kappa_0=\langle k^2\rangle/\langle k\rangle$；Molloy–Reed 判据 $\kappa_0>2$ 时存在巨分支；配置模型的随机失效阈值 $f_c=1-1/(\kappa_0-1)$。对同样 $\langle k\rangle$ 的 ER 网络 $f_c^{ER}=1-1/\langle k\rangle$。
#
# **（2）模拟。** 四种删点策略：随机（random，20 次平均）、按初始度（ID）、按自适应度（RD，每删一个节点后重新计算度）、按初始介数（IB，用 500 个源点近似）。对每种删除顺序，倒序“加回”节点并用并查集维护连通分支（Newman–Ziff 思路），一次得到删去 $Q=0,1,\dots,N$ 个节点后的最大分支比例 $s(Q)$ 与第二大分支。由此计算
#
# - R 指标 $R=\frac1N\sum_{Q=1}^{N}s(Q)$（Schneider 等 2011）；
# - $f_c$ 的两种判定：**1% 规则**（最大分支首次低于原规模 1%）和**第二大分支峰值**。专题页提醒，不同规则可以相差不少，报告时要写明。

# %%
rng = np.random.default_rng(7)

def neighbors_of(eu, N):
    nb = [[] for _ in range(N)]
    for u, v in eu:
        nb[u].append(v); nb[v].append(u)
    return nb

def curve_from_order(order, nb, N, n_check=400):
    """order：删除顺序（长度 N）。返回 s1[Q]：删去前 Q 个节点后最大分支的节点比例（每个 Q 都算），
    以及 s2[Q]：第二大分支比例（只在约 n_check 个等间隔的 Q 上计算，其余为 nan）。"""
    parent = np.arange(N); size = np.ones(N, int); present = np.zeros(N, bool)
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    s1 = np.zeros(N + 1); s2 = np.full(N + 1, np.nan); s2[N] = 0.0
    big = 0
    roots = set()                               # 当前所有分支的根
    every = max(1, N // n_check)
    for step, v in enumerate(order[::-1]):      # 倒序加回
        present[v] = True; roots.add(v); big = max(big, 1)
        for w in nb[v]:
            if present[w]:
                a, b = find(v), find(w)
                if a != b:
                    if size[a] < size[b]:
                        a, b = b, a
                    parent[b] = a; size[a] += size[b]; roots.discard(b)
                    big = max(big, size[a])
        Q = N - step - 1
        s1[Q] = big / N
        if Q % every == 0:
            top = sorted((size[r] for r in roots), reverse=True)[:2]
            s2[Q] = (top[1] / N) if len(top) > 1 else 0.0
    return s1, s2

def adaptive_degree_order(eu, N):
    nb = [set(x) for x in neighbors_of(eu, N)]
    deg = np.array([len(x) for x in nb]); alive = np.ones(N, bool); order = []
    import heapq
    heap = [(-d, v) for v, d in enumerate(deg)]; heapq.heapify(heap)
    while heap:
        d, v = heapq.heappop(heap)
        if not alive[v] or -d != deg[v]:
            continue
        alive[v] = False; order.append(v)
        for w in nb[v]:
            if alive[w]:
                deg[w] -= 1; heapq.heappush(heap, (-deg[w], w))
    return np.array(order)

def all_curves(eu, N, n_random=20, betweenness=True, seed=0):
    r = np.random.default_rng(seed)
    nb = neighbors_of(eu, N)
    deg = np.array([len(x) for x in nb])
    out = {}
    rs = [curve_from_order(r.permutation(N), nb, N) for _ in range(n_random)]
    out["random"] = (np.mean([x[0] for x in rs], axis=0), np.mean([x[1] for x in rs], axis=0))  # s2 的 nan 位置相同
    out["ID"] = curve_from_order(np.argsort(-deg, kind="stable"), nb, N)
    out["RD"] = curve_from_order(adaptive_degree_order(eu, N), nb, N)
    if betweenness:
        H = nx.Graph(); H.add_nodes_from(range(N)); H.add_edges_from(eu)
        bc = nx.betweenness_centrality(H, k=min(500, N), seed=seed)
        out["IB"] = curve_from_order(np.array(sorted(range(N), key=lambda v: -bc[v])), nb, N)
    return out

def R_index(s1):
    return s1[1:].sum() / (len(s1) - 1)

def fc_rules(s1, s2):
    f = np.arange(len(s1)) / (len(s1) - 1)
    one = f[np.argmax(s1 < 0.01 * s1[0])]
    peak = f[np.nanargmax(s2)]
    return one, peak

kappa = (k**2).mean() / k.mean()
print("kappa_0 = <k^2>/<k> = %.2f（Molloy–Reed：> 2 存在巨分支）" % kappa)
print("配置模型理论随机失效阈值 f_c = 1 - 1/(kappa_0 - 1) = %.3f；同 <k> 的 ER 理论值 1 - 1/<k> = %.3f"
      % (1 - 1 / (kappa - 1), 1 - 1 / k.mean()))

real = all_curves(eu, N, seed=1)
print("\n%-8s %8s %14s %18s" % ("策略", "R", "f_c(1%规则)", "f_c(第二大分支峰)"))
for st, (s1, s2) in real.items():
    print("%-8s %8.3f %14.3f %18.3f" % (st, R_index(s1), *fc_rules(s1, s2)))
f = np.arange(N + 1) / N
for st in ["random", "ID", "RD"]:
    s1 = real[st][0]
    print("删去 5%% 的节点后（%s），最大分支剩 %.1f%%" % (st, 100 * s1[int(0.05 * N)]))

# %% [markdown]
# **必需基因。** 先看度与必需性的关系（[Jeong 等 2001](paper-jeong2001_lethality.html) 的经典观察），再做一个“功能 vs 结构”的对照：一次删去全部必需蛋白（细胞层面必然致死），看网络碎裂到什么程度，并与删去同样数目的随机蛋白、按度最高的蛋白比较。

# %%
ess = np.array([genes.set_index("orf").essential.get(v, np.nan) for v in nodes])
known = ~np.isnan(ess)
print("最大分支中必需性已知的蛋白 %d 个，其中必需 %d 个（%.1f%%）"
      % (known.sum(), (ess == 1).sum(), 100 * np.nanmean(ess)))
bins = [1, 2, 4, 8, 16, 32, 64, 1000]
lab = pd.cut(k[known], bins, right=False)
tab = pd.DataFrame({"deg": lab, "ess": ess[known]}).groupby("deg", observed=True).ess.agg(["size", "mean"])
tab.columns = ["蛋白数", "必需比例"]
print(tab.round(3).to_string())
from scipy.stats import mannwhitneyu
print("必需蛋白度的中位数 %.0f，非必需 %.0f；Mann–Whitney 单侧 p = %.1e"
      % (np.median(k[ess == 1]), np.median(k[ess == 0]),
         mannwhitneyu(k[ess == 1], k[ess == 0], alternative="greater").pvalue))

def lcc_after_removal(removed):
    keep = np.ones(N, bool); keep[removed] = False
    H = nx.Graph(); H.add_nodes_from(np.where(keep)[0])
    H.add_edges_from(eu[keep[eu[:, 0]] & keep[eu[:, 1]]])
    return max(len(c) for c in nx.connected_components(H)) / N

E_set = np.where(ess == 1)[0]
m = len(E_set)
lcc_ess = lcc_after_removal(E_set)
lcc_rand = [lcc_after_removal(rng.choice(N, m, replace=False)) for _ in range(20)]
lcc_top = lcc_after_removal(np.argsort(-k)[:m])
print("\n删去 %d 个蛋白（%.1f%% 的节点）后的最大分支比例：" % (m, 100 * m / N))
print("  全部必需蛋白：%.3f" % lcc_ess)
print("  随机蛋白：    %.3f ± %.3f" % (np.mean(lcc_rand), np.std(lcc_rand)))
print("  度最高的蛋白：%.3f" % lcc_top)

# %% [markdown]
# ## 5. 与零模型比较
#
# 两个零模型：（a）**保度随机化**（双边交换，每个蛋白的度不变），检验“鲁棒性是否只由度序列决定”；（b）**ER 网络**（同样 $N$、$L$），代表“没有度异质性”的情形。随机网络取其最大连通分支后再分析。专题页把“比随机化网络更鲁棒”（增强鲁棒性）作为可检验的命题，这里直接比较。

# %%
def as_index_edges(H):
    H = H.subgraph(max(nx.connected_components(H), key=len)).copy()
    mp = {v: i for i, v in enumerate(H.nodes())}
    return np.array([(mp[u], mp[v]) for u, v in H.edges()]), H.number_of_nodes(), H

null_curves = {}
Hc = G.copy()
nx.double_edge_swap(Hc, nswap=5 * Hc.number_of_edges(), max_tries=10**7, seed=11)
e_c, N_c, Hc = as_index_edges(Hc)
null_curves["degree-preserving"] = (all_curves(e_c, N_c, n_random=10, seed=2), N_c, Hc)
He = nx.gnm_random_graph(N, G.number_of_edges(), seed=12)
e_e, N_e, He = as_index_edges(He)
null_curves["ER"] = (all_curves(e_e, N_e, n_random=10, seed=3), N_e, He)

print("%-20s %6s %8s %8s %8s %8s %12s %12s" % ("network", "N", "C", "R_rand", "R_ID", "R_RD", "fc_rand(1%)", "fc_RD(1%)"))
rows = [("real", real, N, G)] + [(name, c, n, H) for name, (c, n, H) in null_curves.items()]
for name, c, n, H in rows:
    print("%-20s %6d %8.3f %8.3f %8.3f %8.3f %12.3f %12.3f"
          % (name, n, nx.average_clustering(H), R_index(c["random"][0]), R_index(c["ID"][0]), R_index(c["RD"][0]),
             fc_rules(*c["random"])[0], fc_rules(*c["RD"])[0]))
kd = np.array([d for _, d in He.degree()], float)
print("ER 网络 <k> = %.2f，kappa = %.2f；理论 f_c = %.3f" % (kd.mean(), (kd**2).mean() / kd.mean(), 1 - 1 / ((kd**2).mean() / kd.mean() - 1)))

# %% [markdown]
# ## 6. 作图
#
# 左上：度分布的互补累积分布（对数坐标），真实网络与 ER 网络；右上：真实网络在四种策略下的最大分支曲线 $s(f)$，虚线为第二大分支（放大 10 倍）；左下：随机失效与自适应攻击下，真实网络与两个零模型的对比；右下：按度分组的必需蛋白比例。

# %%
fig, axes = plt.subplots(2, 2, figsize=(11, 8.5))
ax = axes[0, 0]
for name, deg in [("yeast PPI", k), ("ER (same N, L)", kd)]:
    x = np.sort(deg)
    ax.loglog(x, 1 - np.arange(len(x)) / len(x), ".", ms=3, label=name)
ax.set_xlabel("degree k"); ax.set_ylabel("P(K >= k)"); ax.legend(); ax.set_title("Degree distribution (CCDF)")

ax = axes[0, 1]
for st, ls in zip(["random", "ID", "RD", "IB"], ["-", "--", "-.", ":"]):
    s1, s2 = real[st]
    ax.plot(f, s1, ls=ls, lw=2, label="%s (R = %.3f)" % (st, R_index(s1)))
for st, col in [("random", "C0"), ("RD", "C2")]:
    s2 = real[st][1]; ok = ~np.isnan(s2)
    ax.plot(f[ok], 10 * s2[ok], c=col, lw=1, alpha=0.6, label="2nd component x10 (%s)" % st)
ax.set_xlabel("fraction removed f"); ax.set_ylabel("largest component s(f)"); ax.legend(fontsize=7)
ax.set_title("Yeast PPI: failure vs attack")

ax = axes[1, 0]
for (name, c, n, _), col in zip(rows, ["k", "C1", "C4"]):
    fx = np.arange(n + 1) / n
    ax.plot(fx, c["random"][0], c=col, lw=2, label="%s, random" % name)
    ax.plot(fx, c["RD"][0], c=col, lw=2, ls="--", label="%s, adaptive degree" % name)
ax.set_xlabel("fraction removed f"); ax.set_ylabel("s(f)"); ax.legend(fontsize=7); ax.set_title("Real vs null models")

ax = axes[1, 1]
ax.bar(range(len(tab)), tab["必需比例"], color="C3")
ax.set_xticks(range(len(tab))); ax.set_xticklabels(["%d-%d" % (iv.left, iv.right - 1) for iv in tab.index], rotation=30)
ax.axhline(np.nanmean(ess), c="k", ls="--", lw=1, label="overall")
ax.set_xlabel("degree bin"); ax.set_ylabel("fraction essential"); ax.legend(); ax.set_title("Essentiality vs degree")
plt.tight_layout()
print("运行时间 %.1f 秒" % (time.time() - t0))

# %% [markdown]
# ## 7. 解读与局限
#
# **结果。**
#
# 1. **度异质与理论阈值**。最大分支含 3 860 个蛋白，$\langle k\rangle\approx12.9$，$\kappa_0\approx49$，远大于同 $\langle k\rangle$ 的 ER 网络（约 14）。配置模型理论给出随机失效阈值 $f_c\approx0.98$；模拟中按 1% 规则 $f_c\approx0.94$，按第二大分支峰值约 0.86。两种判定规则相差约 0.08，理论值又高于两者：理论假设无度相关、局部树状、无限大，而这里的网络有限且高度聚集（聚集系数约 0.38）。这正是专题页“不同规则可以相差不少”“理论值只是参照”的具体例子。
# 2. **耐随机失效、怕攻击**。随机删点的 R 约 0.44，按初始度攻击约 0.21，自适应度攻击约 0.17；删去 5% 的节点，随机失效后最大分支仍有约 94%，按度攻击后只剩约 84%。自适应攻击比按初始度攻击更具破坏性（Holme 等 2002 的结论），按初始介数攻击（R 约 0.19）介于两者之间。与 ER 网络相比，酵母网络的随机失效阈值更高（0.94 vs 0.93，满足专题页“增强鲁棒性”的定义，但差距不大），而对自适应攻击远更脆弱（$f_c$ 约 0.29 vs 0.63，R 约 0.17 vs 0.41）——同一个大的 $\langle k^2\rangle$ 带来两面。
# 3. **度序列解释了大部分**。保度随机化网络的各条曲线与真实网络很接近（R 相差约 0.01–0.02）：随机失效和自适应攻击下真实网络略差，按初始度攻击下略好。真实网络的聚集系数是随机化网络的约 10 倍，高聚集让部分边落在三角形里，对维持全局连通是“冗余”的，但这一效应在这里很小。所以在这个网络上，“耐随机、怕攻击”主要是度分布的性质，而不是更细的拓扑结构。
# 4. **度与必需性**。必需蛋白的比例随度单调上升：度为 1 的蛋白中约 9% 必需，度 ≥ 64 的蛋白中约 57% 必需；必需蛋白的度中位数（14）远高于非必需蛋白（4）。这复现了 Jeong 等（2001）的经典观察。
# 5. **结构碎裂 ≠ 功能丧失**。一次删去全部 939 个必需蛋白（约 24% 的节点），在细胞层面每一个都足以致死，网络却仍保留约 68% 的节点在最大分支中，只比删去同样数目的随机蛋白（约 71%）略低，远不如删去同样数目的最高度蛋白（约 47%）。也就是说，必需性并不主要通过“让网络碎裂”体现。这与专题页的论点一致：渗流意义上的结构鲁棒与细胞的功能鲁棒是两个层次；高度蛋白更可能必需，也可能是因为它们参与必需的复合物或相互作用（He 与 Zhang 2006；Zotenko 等 2008），而不是因为它们维持连通（详见[致死性与中心性](molecular-networks.centrality-lethality.html)）。
#
# **局限。**
#
# - BioGRID 汇集的是文献报告，被研究得多的蛋白度更高（研究偏倚），而“至少 2 篇文献”的筛选会放大这一偏倚；度与必需性的相关有一部分可能来自必需基因更受关注。专题页建议做敏感性分析，例如改用 `n_pub ≥ 1` 或 `n_pub ≥ 3`，或随机删去一部分边后重复。
# - 亲和纯化–质谱（Affinity Capture-MS）把复合物中的共纯化蛋白记为两两相互作用，会制造团块结构；不同实验系统的含义不同，这里没有区分。
# - 必需性来自缺失株集合在标准培养条件下的生长表型；许多“非必需”基因在其他条件下才显示表型，注释冲突的 222 个基因被排除在必需性分析之外。
# - 介数攻击只用了 500 个源点的近似，并且只按初始介数排序；自适应介数攻击通常更具破坏性，但计算量大得多。
# - 最大分支比例只是结构指标；它不说明剩余网络能否完成任何具体的细胞功能。
