# %% [markdown]
# # 枢纽和谁相连？酵母蛋白质网络的度相关、富人俱乐部与聚集谱
#
# 度分布只告诉我们“有多少枢纽”，不告诉我们“枢纽和谁相连”。本案例在一张酵母蛋白质物理相互作用网络上计算[度相关性](degree-correlations.html)的几种刻画——邻居平均度函数 $k_{nn}(k)$、度相关系数 $r$、富人俱乐部系数 $\phi(k)$、聚集谱 $C(k)$——并始终与**保持度序列的随机化网络**比较（[度保持随机化检验](degree-correlations.randomization-tests.html)），因为度序列本身就会造成一部分度相关。
#
# 经典结果是 Maslov 与 Sneppen（2002）发现酵母 PPI 网络中枢纽之间的连接被系统性压低（异配），Newman（2002）给出的酵母 PPI 网络 $r=-0.156$。那些网络来自早期的酵母双杂交数据；这里用的是整合了多种证据的 STRING 高置信物理网络，结论未必相同——这正是需要重新检验的地方。
#
# **1. 数据来源**
#
# - 数据：STRING v12.0 酿酒酵母（taxon 4932）物理相互作用子网络，`https://stringdb-downloads.org/`（2026-11-20 下载）。许可证 **CC BY 4.0**（`https://string-db.org/cgi/access`）。引用：Szklarczyk D 等, *Nucleic Acids Research* 2023, DOI [10.1093/nar/gkac1000](https://doi.org/10.1093/nar/gkac1000)。
# - 裁剪：综合分数 ≥ 700，每对一行：`data/yeast_string_physical_v12_hc.csv`；节点名与注释：`data/yeast_string_physical_v12_nodes.csv`。

# %% [markdown]
# ## 2. 读入与清洗

# %%
import time
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

t0 = time.time()
E = pd.read_csv("data/yeast_string_physical_v12_hc.csv")
info = pd.read_csv("data/yeast_string_physical_v12_nodes.csv").set_index("id")
names = info["preferred_name"].to_dict()
G = nx.Graph()
G.add_edges_from(zip(E.protein1, E.protein2))
G.remove_edges_from(nx.selfloop_edges(G))
N, M = G.number_of_nodes(), G.number_of_edges()
deg = dict(G.degree())
k = np.array(list(deg.values()))
print("N = %d，M = %d，<k> = %.2f，最大度 %d" % (N, M, k.mean(), k.max()))

# %% [markdown]
# ## 3. 构网：保持度序列的随机化网络
#
# 对真实网络做双边交换（每个样本 $5M$ 次交换，不产生自环和重边），得到 10 个零模型样本。它们与真实网络的每个节点度完全相同，其余连接方式随机。

# %%
n_null = 10
nulls = []
for s in range(n_null):
    H = G.copy()
    nx.double_edge_swap(H, nswap=5 * M, max_tries=100 * M, seed=100 + s)
    nulls.append(H)
print("零模型样本数:", len(nulls), "；度序列保持:", all(dict(H.degree()) == deg for H in nulls))

# %% [markdown]
# ## 4. 核心指标
#
# ### 4.1 邻居平均度函数 $k_{nn}(k)$ 与相关指数 $\mu$
#
# $k_{nn}(k)$ 是度为 $k$ 的节点的邻居平均度。不相关网络中 $k_{nn}(k)=\langle k^2\rangle/\langle k\rangle$，与 $k$ 无关；同配网络随 $k$ 上升，异配网络随 $k$ 下降。在双对数坐标上拟合 $k_{nn}(k)\sim k^{\mu}$。

# %%
def knn_curve(H):
    knn = nx.average_degree_connectivity(H)
    ks = np.array(sorted(knn))
    return ks, np.array([knn[x] for x in ks])

def mu_fit(ks, kv):
    ok = ks >= 2
    return np.polyfit(np.log(ks[ok]), np.log(kv[ok]), 1)[0]

ks, kv = knn_curve(G)
mu_real = mu_fit(ks, kv)
mu_null = [mu_fit(*knn_curve(H)) for H in nulls]
print("不相关网络的预期 <k²>/<k> = %.1f" % ((k ** 2).mean() / k.mean()))
print("μ：真实 %.3f，零模型 %.3f ± %.3f" % (mu_real, np.mean(mu_null), np.std(mu_null)))

# %% [markdown]
# ### 4.2 度相关系数 $r$ 与结构截断
#
# $r$ 是边两端度的皮尔逊相关系数。度保持随机化给出“仅由度序列造成”的 $r$ 的分布，用 $z$ 分数比较。
#
# 结构截断 $k_s=\sqrt{\langle k\rangle N}$：度超过 $k_s$ 的节点之间，在简单图中期望边数会超过 1，于是即使随机连接也会表现出异配（结构性异配，[结构截断](degree-correlations.structural-cutoff.html)）。

# %%
r_real = nx.degree_assortativity_coefficient(G)
r_null = np.array([nx.degree_assortativity_coefficient(H) for H in nulls])
z_r = (r_real - r_null.mean()) / r_null.std()
print("r：真实 %.3f，零模型 %.3f ± %.3f，z = %.1f" % (r_real, r_null.mean(), r_null.std(), z_r))
k_s = np.sqrt(k.mean() * N)
print("结构截断 k_s = %.0f；度超过 k_s 的节点 %d 个；最大度 %d" % (k_s, (k > k_s).sum(), k.max()))

# %% [markdown]
# ### 4.3 富人俱乐部
#
# $\phi(k)$ 是度大于 $k$ 的节点之间实际边数占最大可能边数的比例。$\phi(k)$ 随 $k$ 上升是任何网络的普遍趋势，必须除以零模型的 $\phi_{\text{rand}}(k)$，得到归一化系数 $\rho(k)=\phi(k)/\phi_{\text{rand}}(k)$；$\rho>1$ 才说明高度节点之间的连接多于度序列的预期（[富人俱乐部系数及其归一化](degree-correlations.rich-club.html)）。

# %%
phi = nx.rich_club_coefficient(G, normalized=False)
phi_null = [nx.rich_club_coefficient(H, normalized=False) for H in nulls]
k_grid = [x for x in [5, 10, 20, 30, 40, 60, 80, 100, 120, 150] if x in phi and (k > x).sum() >= 10]
print("  k   >k的节点数   φ(k)   φ_rand(k)   ρ(k)")
rho = {}
for x in k_grid:
    pr = np.mean([p[x] for p in phi_null])
    rho[x] = phi[x] / pr
    print("%4d %10d %8.3f %10.3f %7.2f" % (x, (k > x).sum(), phi[x], pr, rho[x]))

# %% [markdown]
# ### 4.4 聚集谱 $C(k)$
#
# 层次模块网络中常见 $C(k)\sim k^{-1}$：低度节点处在稠密的小模块里，高度节点连接不同模块。比较真实网络与零模型的 $C(k)$。

# %%
clu = nx.clustering(G)
dfc = pd.DataFrame({"k": [deg[n] for n in G], "C": [clu[n] for n in G]})
Ck = dfc.groupby("k")["C"].mean()
ok = Ck.index >= 2
slope = np.polyfit(np.log(Ck.index[ok]), np.log(Ck.values[ok] + 1e-9), 1)[0]
clu0 = nx.clustering(nulls[0])
Ck0 = pd.Series({kk: np.mean([clu0[n] for n in nulls[0] if deg[n] == kk]) for kk in Ck.index})
print("C(k) 的双对数斜率：%.2f" % slope)
print("平均聚集系数：真实 %.3f，零模型 %.3f" % (np.mean(list(clu.values())), np.mean(list(clu0.values()))))

# %% [markdown]
# ## 5. 与零模型比较：枢纽之间到底是“多连”还是“少连”？
#
# 直接数度最高的 50 个蛋白之间的边数，与零模型比较；再看这些枢纽是谁。

# %%
hubs = sorted(deg, key=deg.get, reverse=True)[:50]
e_hub = G.subgraph(hubs).number_of_edges()
e_hub_null = np.array([H.subgraph(hubs).number_of_edges() for H in nulls])
print("度前 50 的蛋白之间：真实 %d 条边，零模型 %.1f ± %.1f 条，z = %.1f" %
      (e_hub, e_hub_null.mean(), e_hub_null.std(), (e_hub - e_hub_null.mean()) / e_hub_null.std()))
print("度前 12 的蛋白:", [(names.get(n, n), deg[n]) for n in hubs[:12]])
print("用时 %.0f 秒" % (time.time() - t0))

# %% [markdown]
# ## 6. 作图
#
# 左：$k_{nn}(k)$，真实网络与零模型（灰色为 10 个样本）。中：归一化富人俱乐部系数 $\rho(k)$，虚线为 1。右：聚集谱 $C(k)$。

# %%
fig, ax = plt.subplots(1, 3, figsize=(14, 4))
for H in nulls:
    a, b = knn_curve(H)
    ax[0].loglog(a, b, ".", ms=2, color="#cbd5e0")
ax[0].loglog(ks, kv, "o", ms=3, color="#c53030", label="yeast")
ax[0].axhline((k ** 2).mean() / k.mean(), ls="--", color="k", lw=1, label="<k²>/<k>")
ax[0].set_xlabel("k")
ax[0].set_ylabel("k_nn(k)")
ax[0].legend()
ax[1].plot(list(rho), list(rho.values()), "o-", color="#3182ce")
ax[1].axhline(1, ls="--", color="k", lw=1)
ax[1].set_xlabel("k")
ax[1].set_ylabel("ρ(k) = φ / φ_rand")
ax[2].loglog(Ck.index[ok], Ck.values[ok] + 1e-3, "o", ms=3, color="#c53030", label="yeast")
ax[2].loglog(Ck0.index[ok], Ck0.values[ok] + 1e-3, ".", ms=3, color="#a0aec0", label="degree-preserving null")
ax[2].set_xlabel("k")
ax[2].set_ylabel("C(k)")
ax[2].legend()
fig.tight_layout()

# %% [markdown]
# ## 7. 解读与局限
#
**结果。** 这张网络是**强烈同配**的，与早期双杂交网络的异配结论相反：
#
# - $k_{nn}(k)$ 随 $k$ 明显上升，$\mu=0.64$，而度保持零模型的 $\mu=-0.057\pm0.002$（零模型略呈异配，这是度序列本身带来的结构性效应）；
# - 度相关系数 $r=0.586$，零模型 $r=-0.086\pm0.003$，$z\approx233$；
# - 结构截断 $k_s=\sqrt{\langle k\rangle N}\approx293$，最大度 282 没有超过它，所以零模型中的轻微异配不能归因于“枢纽太多、简单图放不下”；
# - 归一化富人俱乐部系数 $\rho(k)$ 随 $k$ 单调上升，$k>150$ 的 121 个蛋白之间 $\rho\approx2.0$：高度蛋白之间的连接是度序列预期的两倍；
# - 度前 50 的蛋白之间有 1 225 条边，恰好是 $50\times49/2$——它们**两两相连**，而零模型只有约 660 条。前 12 名全是核糖体小亚基蛋白（RPS13、RPS7A、RPS5……），成对的旁系同源拷贝（如 RPS4A 与 RPS4B）作为两个节点各自出现；
# - 平均聚集系数 0.581，零模型只有 0.122；$C(k)$ 几乎不随 $k$ 变化（双对数斜率 $-0.07$），没有层次模块网络常见的 $C(k)\sim k^{-1}$。
#
# 这些现象有一个共同的来源：大型复合物（核糖体、蛋白酶体、RNA 聚合酶等）的成员在 STRING 物理网络中两两成边，形成团；团内成员的度相近，彼此相连，于是度高者连度高者。同配、富人俱乐部和度无关的高聚集，在这里都是“复合物成团”的不同侧面，而不是三个独立的发现。
#
# **局限。**
#
# - **数据来源决定结论**：早期双杂交网络（Maslov 与 Sneppen 2002；Newman 2002 的 $r=-0.156$）是异配的；STRING 物理网络整合了亲和纯化–质谱和数据库中的复合物信息，复合物成员两两成边，把一批高度节点连成团，使网络变成同配。同一个物种，不同的测量方式可以得到符号相反的 $r$；报告度相关时必须说明数据来源与构网规则。
# - **$r$ 是一个数**：它受最大度节点的强烈影响，大网络中 $r$ 会被压向 0（见[度相关系数 r](degree-correlations.assortativity-coefficient.html)）；$k_{nn}(k)$ 和 $\rho(k)$ 给出的信息更完整。
# - **零模型的选择**：这里只保持度序列。保持度序列的同时还保持聚集系数或社团结构的零模型，会给出不同的基线。
# - **研究偏倚**：被研究得多的蛋白既度高、又更可能与其他被研究得多的蛋白一起被检测到，这会制造同配的假象。
