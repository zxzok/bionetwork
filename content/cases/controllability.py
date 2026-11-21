# %% [markdown]
# # 人类转录调控网络的结构可控性：最大匹配、驱动节点与保度随机化
#
# 本案例用真实的人类转录因子（TF）→靶基因调控关系，完整做一次 Liu、Slotine 与 Barabási（2011）式的结构可控性分析：求最大匹配，得到最少驱动节点数 $N_D=\max(N-|M^*|,1)$ 和驱动节点比例 $n_D=N_D/N$，再与保持入度、出度序列的随机网络和同规模的 ER 随机网络比较，最后用控制轮廓（Ruths 与 Ruths 2014）解释结果。所用定义与[结构可控性与最大匹配](controllability.structural-controllability.html)、[驱动节点与网络结构](controllability.driver-nodes.html)一致。
#
# **1. 数据来源**
#
# - 数据库：CollecTRI（Müller-Dott 等 2023，*Nucleic Acids Research* 51:10934–10949，DOI [10.1093/nar/gkad841](https://doi.org/10.1093/nar/gkad841)），经 OmniPath 网络服务下载（`https://omnipathdb.org/interactions?datasets=collectri`，2026-11-20）。
# - 许可证：CollecTRI 是“组合资源”，各条关系沿用其来源数据库的许可证。为保证可再分发，本案例**只保留至少有一个 CC BY 4.0 许可的人工整理来源支持的关系**（OmniPath 资源表中的 NTNU.Curated、TFactS、SIGNOR、CytReg、Pavlidis2021、GOA、IntAct），并去掉以蛋白复合物（如 AP-1、NF-κB 二聚体）为调控方的行。文件为 `data/collectri_human_tf_target_ccby_curated.csv`，按 CC BY 4.0 再分发，`cc_by_curated` 列记录每条关系的支持来源。
# - 这样做的代价是网络比完整的 CollecTRI 小（完整版约 6.4 万条，这里约 1.6 万条），结论只针对这个子集。

# %% [markdown]
# ## 2. 读入与清洗
#
# 每一行是一条有向边 TF → 靶基因。清洗只做三件事：去掉重复边、去掉自环（自调控）、统计节点。自环要单独说明：在结构可控性里，自环让节点可以“匹配自己”，若给**每个**节点都加上独立的自环参数，$N_D$ 会变成 1（见专题页“节点自身动力学的影响”）。这里只有极少数自调控记录，按 Liu 等（2011）的做法把网络当作纯拓扑处理，去掉自环。

# %%
import time
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import maximum_bipartite_matching

t0 = time.time()
raw = pd.read_csv("data/collectri_human_tf_target_ccby_curated.csv")
print("原始行数:", len(raw))
df = raw.drop_duplicates(["tf", "target"])
n_self = int((df.tf == df.target).sum())
df = df[df.tf != df.target].reset_index(drop=True)
print("去重后去掉自环 %d 条，剩余有向边 %d 条" % (n_self, len(df)))
print("支持来源个数的分布：")
print(df.cc_by_curated.str.count(";").add(1).value_counts().sort_index().to_string())

# %% [markdown]
# ## 3. 构网
#
# 节点是基因（以 HGNC 基因符号表示），边 $u\to v$ 表示 $u$ 编码的转录因子调控 $v$。按专题代码的约定，系统矩阵中 $A_{vu}\neq0$ 表示 $u$ 影响 $v$。为了在零模型里重复几十次最大匹配，另外把网络存成整数编号的边数组 `u, v`。

# %%
nodes = sorted(set(df.tf) | set(df.target))
idx = {g: i for i, g in enumerate(nodes)}
N = len(nodes)
u = df.tf.map(idx).to_numpy()
v = df.target.map(idx).to_numpy()
L = len(u)
G = nx.DiGraph()
G.add_nodes_from(range(N))
G.add_edges_from(zip(u, v))
kin = np.bincount(v, minlength=N)
kout = np.bincount(u, minlength=N)
print("N = %d 个基因，L = %d 条调控边，平均度 <k> = L/N = %.2f" % (N, L, L / N))
print("有出边的节点（TF）: %d；没有入边的源节点: %d；没有出边的汇节点: %d"
      % ((kout > 0).sum(), (kin == 0).sum(), (kout == 0).sum()))
print("最大出度 %d（%s），最大入度 %d（%s）"
      % (kout.max(), nodes[kout.argmax()], kin.max(), nodes[kin.argmax()]))
print("弱连通分支数 %d，最大弱连通分支占 %.1f%% 节点"
      % (nx.number_weakly_connected_components(G), 100 * len(max(nx.weakly_connected_components(G), key=len)) / N))

# %% [markdown]
# ## 4. 核心指标：最大匹配与驱动节点
#
# 把每个节点拆成出端 $u^+$ 和入端 $v^-$，有向边 $u\to v$ 变成二分图的边 $u^+$–$v^-$，用 Hopcroft–Karp 算法求最大匹配，入端未被匹配的节点就是驱动节点。这里先用 NetworkX（与专题代码相同的写法）求一次，再用 SciPy 的稀疏实现求一次，两者的 $|M^*|$ 必须相同；后面重复计算时用更快的 SciPy 版本。
#
# 注意：驱动节点**集合**不唯一，但**数目** $N_D$ 唯一。

# %%
top = [("o", x) for x in range(N)]
Bg = nx.Graph()
Bg.add_nodes_from(top)
Bg.add_nodes_from(("i", x) for x in range(N))
Bg.add_edges_from((("o", a), ("i", b)) for a, b in zip(u, v))
M_nx = nx.bipartite.hopcroft_karp_matching(Bg, top_nodes=top)
size_nx = sum(1 for key in M_nx if key[0] == "o")

def match(u, v, N):
    """返回 m：m[r] 为出端 r 匹配到的入端编号，-1 表示未匹配。"""
    A = csr_matrix((np.ones(len(u)), (u, v)), shape=(N, N))
    return maximum_bipartite_matching(A, perm_type="column")

def n_drivers(u, v, N):
    return max(N - int((match(u, v, N) >= 0).sum()), 1)

m = match(u, v, N)
assert size_nx == (m >= 0).sum(), "两种实现的最大匹配大小应相同"
matched_in = np.zeros(N, bool)
matched_in[m[m >= 0]] = True
drivers = np.where(~matched_in)[0]
ND = max(N - size_nx, 1)
print("|M*| = %d，N_D = %d，n_D = N_D/N = %.3f" % (size_nx, ND, ND / N))

# %% [markdown]
# **驱动节点从哪里来？** 驱动节点数主要来自“下游太多、上游太少”：一个 TF 的众多靶基因里，只有一个能与它匹配。下面按 Ruths 与 Ruths（2014）把 $N_D$ 分解为源节点 $N_s$、外部扩张 $N_e=\max(0,N_t-N_s)$（$N_t$ 为汇节点数）和内部扩张 $N_i=N_D-N_s-N_e$，并比较驱动节点和非驱动节点的度。
#
# 再进一步：哪些节点**可能**在某个最小驱动节点集里？从当前未匹配的入端出发，沿“非匹配边到某个出端、再沿匹配边到它的入端”的交替路径能到达的入端，都可以通过交换匹配变成未匹配。还可以论证：未匹配节点只要有一条入边，就能被换成匹配节点，因此出现在**所有**最小驱动节点集中的节点恰好是没有入边的源节点（与专题页“关键节点”的例子一致）。

# %%
Ns = int((kin == 0).sum())
Nt = int((kout == 0).sum())
Ne = max(0, Nt - Ns)
Ni = ND - Ns - Ne
print("控制轮廓: N_s = %d, N_e = %d, N_i = %d  ->  (eta_s, eta_e, eta_i) = (%.3f, %.3f, %.3f)"
      % (Ns, Ne, Ni, Ns / N, Ne / N, Ni / N))

ktot = kin + kout
isdrv = ~matched_in
print("驱动节点平均总度 %.2f，非驱动节点平均总度 %.2f" % (ktot[isdrv].mean(), ktot[~isdrv].mean()))
hubs = np.argsort(-kout)[:50]
print("出度最高的 50 个 TF 中，在本次匹配下是驱动节点的有 %d 个" % isdrv[hubs].sum())
print("TF（有出边）中驱动节点比例 %.3f；非 TF 基因中驱动节点比例 %.3f"
      % (isdrv[kout > 0].mean(), isdrv[kout == 0].mean()))

# 交替路径搜索：哪些节点可能成为驱动节点
Acsc = csr_matrix((np.ones(L), (u, v)), shape=(N, N)).tocsc()
possible = isdrv.copy()
queue = list(np.where(isdrv)[0])
while queue:
    c = queue.pop()
    for r in Acsc.indices[Acsc.indptr[c]:Acsc.indptr[c + 1]]:   # r -> c 的所有上游 r
        c2 = m[r]
        if c2 >= 0 and not possible[c2]:
            possible[c2] = True
            queue.append(c2)
print("关键节点（出现在所有最小驱动节点集中，即源节点）: %d" % Ns)
print("可能成为驱动节点的节点: %d；永不成为驱动节点的冗余节点: %d" % (possible.sum(), N - possible.sum()))

# %% [markdown]
# **控制的鲁棒性：关键边。** 删除一条边后若 $N_D$ 增加，这条边就是关键边。不在当前最大匹配里的边被删掉后，原匹配仍在，$N_D$ 不会增加，所以只需逐条检查当前匹配里的 $|M^*|$ 条边。

# %%
eid = {(a, b): k for k, (a, b) in enumerate(zip(u, v))}
crit = 0
for r in np.where(m >= 0)[0]:
    keep = np.ones(L, bool)
    keep[eid[(r, m[r])]] = False
    if n_drivers(u[keep], v[keep], N) > ND:
        crit += 1
print("匹配边 %d 条，其中关键边 %d 条（占全部边的 %.1f%%）" % ((m >= 0).sum(), crit, 100 * crit / L))

# %% [markdown]
# ## 5. 与零模型比较
#
# 两个零模型，各 30 次（固定种子）：
#
# - **保度随机化**：保持每个节点的入度和出度不变，打乱“谁调控谁”。做法是随机打乱边表的靶基因列（这一步已经精确保持两个度序列），再把产生的自环和重边与随机挑选的其他边交换靶基因，直到没有自环和重边。这对应 Liu 等（2011）用来说明“$n_D$ 主要由度分布决定”的比较。
# - **有向 ER 网络**：同样的 $N$ 和 $L$，边在所有有序节点对中均匀随机放置（无自环、无重边）。
#
# 用 $z=(x_{\rm real}-\bar x_{\rm null})/s_{\rm null}$ 概括差异。

# %%
rng = np.random.default_rng(2026)

def degree_preserving(u, v, rng, n, max_iter=1000):
    v = v.copy()
    rng.shuffle(v)
    for _ in range(max_iter):
        key = u.astype(np.int64) * n + v
        order = np.argsort(key, kind="stable")
        dup = np.zeros(len(u), bool)
        ks = key[order]
        dup[order[1:][ks[1:] == ks[:-1]]] = True
        bad = np.where((u == v) | dup)[0]
        if len(bad) == 0:
            return v
        for i, j in zip(bad, rng.integers(0, len(u), len(bad))):
            v[i], v[j] = v[j], v[i]          # 逐对交换靶基因，度序列不变
    raise RuntimeError("未能消除重边")

def er_directed(N, L, rng):
    pairs = set()
    while len(pairs) < L:
        a = rng.integers(0, N, L)
        b = rng.integers(0, N, L)
        for x, y in zip(a, b):
            if x != y:
                pairs.add((x, y))
            if len(pairs) == L:
                break
    e = np.array(sorted(pairs))
    return e[:, 0], e[:, 1]

R = 30
nd_deg, nd_er, prof_deg, prof_er = [], [], [], []
for _ in range(R):
    vv = degree_preserving(u, v, rng, N)
    assert (np.bincount(vv, minlength=N) == kin).all()
    nd_deg.append(n_drivers(u, vv, N))
    uu, ve = er_directed(N, L, rng)
    nd_er.append(n_drivers(uu, ve, N))
    for (a, b, store, nd) in [(u, vv, prof_deg, nd_deg[-1]), (uu, ve, prof_er, nd_er[-1])]:
        ki, ko = np.bincount(b, minlength=N), np.bincount(a, minlength=N)
        s, t_ = int((ki == 0).sum()), int((ko == 0).sum())
        e = max(0, t_ - s)
        store.append((s / N, e / N, (nd - s - e) / N))
nd_deg, nd_er = np.array(nd_deg) / N, np.array(nd_er) / N
nD = ND / N
for name, x in [("保度随机化", nd_deg), ("有向 ER", nd_er)]:
    print("%-6s n_D = %.4f ± %.4f；真实网络 n_D = %.4f，z = %.1f"
          % (name, x.mean(), x.std(ddof=1), nD, (nD - x.mean()) / x.std(ddof=1)))
print("控制轮廓均值 (eta_s, eta_e, eta_i)：保度 %s，ER %s"
      % (np.round(np.mean(prof_deg, 0), 3), np.round(np.mean(prof_er, 0), 3)))

# %% [markdown]
# **只看 TF 之间的调控核心。** 大多数驱动节点是只被调控、不调控别人的靶基因。把网络限制在“调控方和被调控方都是 TF”的子网络上，再做同样的比较，可以看出这一结论对“汇节点很多”这一特点依赖有多大。

# %%
is_tf = kout > 0
core = is_tf[u] & is_tf[v]
cu, cv = u[core], v[core]
core_nodes = np.unique(np.r_[cu, cv])
remap = -np.ones(N, int)
remap[core_nodes] = np.arange(len(core_nodes))
cu, cv = remap[cu], remap[cv]
Nc, Lc = len(core_nodes), len(cu)
ND_core = n_drivers(cu, cv, Nc)
core_deg = np.array([n_drivers(cu, degree_preserving(cu, cv, rng, Nc), Nc) for _ in range(R)]) / Nc
core_er = np.array([n_drivers(*er_directed(Nc, Lc, rng), Nc) for _ in range(R)]) / Nc
print("TF 核心: N = %d, L = %d, <k> = %.2f, n_D = %.3f" % (Nc, Lc, Lc / Nc, ND_core / Nc))
print("  保度随机化 n_D = %.3f ± %.3f；有向 ER n_D = %.3f ± %.3f"
      % (core_deg.mean(), core_deg.std(ddof=1), core_er.mean(), core_er.std(ddof=1)))

# %% [markdown]
# ## 6. 作图
#
# 左：入度与出度的互补累积分布（出度极不均匀，少数 TF 调控上百个基因；入度较均匀）。中：真实网络与两个零模型的 $n_D$。右：控制轮廓的三个分量。

# %%
fig, axes = plt.subplots(1, 3, figsize=(13, 3.8))
ax = axes[0]
for k, lab in [(kout[kout > 0], "out-degree (TFs)"), (kin[kin > 0], "in-degree")]:
    ks = np.sort(k)
    ax.loglog(ks, 1 - np.arange(len(ks)) / len(ks), ".", ms=3, label=lab)
ax.set_xlabel("k"); ax.set_ylabel("P(K >= k)"); ax.legend(); ax.set_title("Degree distributions")

ax = axes[1]
ax.boxplot([nd_deg, nd_er], positions=[1, 2], widths=0.5)
ax.scatter([0], [nD], color="tab:red", zorder=3, s=40)
ax.set_xticks([0, 1, 2]); ax.set_xticklabels(["real", "degree-\npreserving", "directed ER"])
ax.set_ylabel("n_D = N_D / N"); ax.set_title("Driver-node fraction (%d nulls each)" % R)

ax = axes[2]
labels = ["real", "degree-pres.", "ER"]
profs = [(Ns / N, Ne / N, Ni / N), tuple(np.mean(prof_deg, 0)), tuple(np.mean(prof_er, 0))]
bottom = np.zeros(3)
for j, (name, col) in enumerate([("source", "tab:blue"), ("external dilation", "tab:orange"), ("internal dilation", "tab:green")]):
    h = np.array([p[j] for p in profs])
    ax.bar(labels, h, bottom=bottom, color=col, label=name)
    bottom += h
ax.set_ylabel("fraction of N"); ax.set_title("Control profile"); ax.legend(fontsize=8)
plt.tight_layout()

fig, ax = plt.subplots(figsize=(5, 3.6))
bins = np.logspace(0, np.log10(ktot.max() + 1), 25)
ax.hist(ktot[isdrv], bins=bins, alpha=0.6, label="driver nodes")
ax.hist(ktot[~isdrv], bins=bins, alpha=0.6, label="matched nodes")
ax.set_xscale("log"); ax.set_xlabel("total degree k_in + k_out"); ax.set_ylabel("count")
ax.set_title("Degree of driver vs matched nodes"); ax.legend()
plt.tight_layout()
print("总运行时间 %.1f 秒" % (time.time() - t0))

# %% [markdown]
# ## 7. 解读与局限
#
# **结果怎么读**（数字以上面的运行输出为准）：
#
# - 这个人类 TF–靶基因网络的驱动节点比例很高，约 0.8：要在结构意义上控制全部基因的线性动力学，大约每 5 个基因里就有 4 个需要独立输入。这与 Liu 等（2011）“基因调控网络的 $n_D$ 相对较高”的结论一致。
# - 控制轮廓几乎全部来自**外部扩张**：汇节点（只被调控的靶基因）远多于源节点，每条控制路径只能“带走”一个汇节点。这正是专题页所述的转录调控网络类型（Ruths 与 Ruths 2014）。
# - **保度随机化**后 $n_D$ 只略有下降、控制轮廓几乎不变，而同规模 ER 网络的 $n_D$ 低一个数量级以上：决定 $n_D$ 的主要是入度、出度序列（尤其是“少数 TF、大量靶基因”的出度异质性），而不是具体谁连谁。真实网络与保度网络之间的小差异在 30 次随机化下仍然显著（$|z|$ 大），说明度序列之外的连接方式也有一点影响，但幅度很小。
# - 驱动节点的平均总度远低于匹配节点；出度最高的 50 个 TF 枢纽中只有约三分之一在这次匹配下是驱动节点，而全网的比例约为 0.8：与“驱动节点倾向于避开枢纽”一致。不过就“是不是 TF”而言，TF 与非 TF 基因成为驱动节点的比例几乎相同——避开的是枢纽，而不是 TF 这一类基因。出现在所有最小驱动节点集中的只有源节点；其余驱动节点可以在许多候选中互换，所以“某个基因是驱动节点”这句话必须指明是哪一个最大匹配。
# - 限制在 TF 核心子网络后，$n_D$ 明显下降，说明整体的高 $n_D$ 主要来自大量汇节点。
#
# **局限**：
#
# - 结构可控性假设线性时不变动力学和相互独立的非零权重；真实的转录调控是非线性的，有饱和、协同结合和反馈（见[非线性网络的控制](controllability.nonlinear-control.html)）。$N_D$ 回答的是“最少需要几个独立输入”这一理论问题，不等于实验上需要扰动几个基因。
# - 结果对建模选择敏感：去掉自环是一种选择；若给每个基因加上独立的自身衰减参数，$N_D$ 会变成 1；若衰减参数全部相同，又与无自环时相同（见专题页“节点自身动力学的影响”）。
# - 数据是“文献中已知的调控关系”，不是某一种细胞里同时活跃的调控：不同组织、不同条件下的网络不同；研究多的 TF 记录更多（研究偏倚，见[网络构建](network-construction.bias-and-missingness.html)）。为了许可证干净，又去掉了只来自其他许可证来源的关系和复合物调控方，边数只有完整 CollecTRI 的约四分之一，$n_D$ 的具体数值不能直接与 Liu 等（2011）表中的网络比较。
# - 控制全部节点通常不是生物学问题本身。更有意义的往往是**目标控制**（只控制与某个表型相关的基因，见[目标控制与部分可控](controllability.target-control.html)），Yan 等（2017）在线虫连接组上也是这样做的。
