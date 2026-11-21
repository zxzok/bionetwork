# %% [markdown]
# # 酵母蛋白质网络是小世界的吗？是无标度的吗？——与四种网络模型对照
#
# 本案例用一张真实的酿酒酵母蛋白质物理相互作用网络，检验[小世界与无标度网络模型](network-models.html)里的两个经典论断：真实网络“聚集高、路径短”（小世界），以及度分布“服从幂律”（无标度）。做法是把真实网络与四个模型——ER 随机网络、Watts–Strogatz（WS）小世界网络、Barabási–Albert（BA）优先连接网络、保持度序列的随机网络（配置模型）——放在同样的 $N$ 和边数下逐项比较，并用最大似然和似然比检验度分布（[小世界与无标度的统计判别](network-models.identification.html)）。
#
# **1. 数据来源**
#
# - 数据：STRING v12.0 酿酒酵母（taxon 4932）**物理**相互作用子网络 `4932.protein.physical.links.v12.0.txt.gz`，蛋白注释来自 `4932.protein.info.v12.0.txt.gz`，下载自 `https://stringdb-downloads.org/`（2026-11-20）。
# - 许可证：**CC BY 4.0**（`https://string-db.org/cgi/access`）。引用：Szklarczyk D 等, The STRING database in 2023, *Nucleic Acids Research* 2023, DOI [10.1093/nar/gkac1000](https://doi.org/10.1093/nar/gkac1000)。
# - 裁剪：只保留综合分数 ≥ 700 的边，每对一行，存为 `data/yeast_string_physical_v12_hc.csv`（列：`protein1, protein2, combined_score`，节点为酵母系统名，如 `YML030W`）；节点的常用名和注释在 `data/yeast_string_physical_v12_nodes.csv`。

# %% [markdown]
# ## 2. 读入与清洗

# %%
import time
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from scipy import optimize, stats, special

t0 = time.time()
E = pd.read_csv("data/yeast_string_physical_v12_hc.csv")
names = pd.read_csv("data/yeast_string_physical_v12_nodes.csv").set_index("id")["preferred_name"].to_dict()
print("边:", len(E), "；自环:", int((E.protein1 == E.protein2).sum()), "；最低分数:", E.combined_score.min())
G = nx.Graph()
G.add_edges_from(zip(E.protein1, E.protein2))
N, M = G.number_of_nodes(), G.number_of_edges()
comps = sorted(nx.connected_components(G), key=len, reverse=True)
print("N = %d，M = %d，<k> = %.2f，连通分支 %d 个，最大分支 %d 个节点（%.1f%%）" %
      (N, M, 2 * M / N, len(comps), len(comps[0]), 100 * len(comps[0]) / N))
k = np.array([d for _, d in G.degree()])
top = sorted(G.degree(), key=lambda x: -x[1])[:8]
print("度最高的 8 个蛋白:", [(names.get(n, n), d) for n, d in top])

# %% [markdown]
# ## 3. 构网：四个对照模型
#
# 所有模型都取与真实网络相同的节点数 $N$，边数尽量相同，并固定随机种子：
#
# - **ER**：$G(N,M)$；
# - **WS**：环形网格每个节点连 $K$ 个近邻（$K$ 取最接近平均度的偶数），重连概率 $p=0.1$；
# - **BA**：每个新节点带 $m=\mathrm{round}(M/N)$ 条边；
# - **配置模型**：对真实网络做 $10M$ 次双边交换，保持每个节点的度不变，其余全部随机化。

# %%
K = int(round(2 * M / N / 2) * 2)
m_ba = int(round(M / N))
models = {
    "yeast": G,
    "ER": nx.gnm_random_graph(N, M, seed=1),
    "WS (p=0.1)": nx.watts_strogatz_graph(N, K, 0.1, seed=1),
    "BA": nx.barabasi_albert_graph(N, m_ba, seed=1),
}
CM = G.copy()
nx.double_edge_swap(CM, nswap=10 * M, max_tries=100 * M, seed=1)
models["configuration"] = CM
for name, H in models.items():
    print("%-14s N = %d，M = %d" % (name, H.number_of_nodes(), H.number_of_edges()))
print("配置模型保持了每个节点的度:", dict(CM.degree()) == dict(G.degree()))

# %% [markdown]
# ## 4. 核心指标
#
# ### 4.1 每个网络的聚集、路径与度的不均匀性
#
# 平均路径长度在最大连通分支上计算，随机抽 300 个源节点做 BFS 估计。

# %%
def mean_path(H, n_src=300, seed=0):
    H = H.subgraph(max(nx.connected_components(H), key=len))
    nodes = list(H.nodes())
    rng = np.random.default_rng(seed)
    tot, cnt = 0, 0
    for i in rng.choice(len(nodes), size=min(n_src, len(nodes)), replace=False):
        d = nx.single_source_shortest_path_length(H, nodes[i])
        tot += sum(d.values())
        cnt += len(d) - 1
    return tot / cnt

rows = {}
for name, H in models.items():
    kk = np.array([d for _, d in H.degree()])
    rows[name] = {"C": nx.average_clustering(H), "L": mean_path(H), "k_max": kk.max(),
                  "<k²>/<k>": (kk ** 2).mean() / kk.mean()}
tab = pd.DataFrame(rows).T
print(tab.round(3).to_string())

# %% [markdown]
# ### 4.2 小世界指数
#
# - $\sigma=\dfrac{C/C_{\text{rand}}}{L/L_{\text{rand}}}$，以 ER 为随机参照，$\sigma\gg1$ 视为小世界；
# - $\omega=\dfrac{L_{\text{rand}}}{L}-\dfrac{C}{C_{\text{latt}}}$，以同平均度的环形网格为规则参照，$C_{\text{latt}}=\dfrac{3(K-2)}{4(K-1)}$，$\omega$ 接近 0 为小世界，接近 $-1$ 偏规则、接近 $+1$ 偏随机。
#
# 再用 ER 理论值核对：$C_{\text{ER}}\approx\langle k\rangle/N$，$L_{\text{ER}}\approx\ln N/\ln\langle k\rangle$。

# %%
C, L = tab.loc["yeast", "C"], tab.loc["yeast", "L"]
Cr, Lr = tab.loc["ER", "C"], tab.loc["ER", "L"]
C_latt = 3 * (K - 2) / (4 * (K - 1))
sigma = (C / Cr) / (L / Lr)
omega = Lr / L - C / C_latt
print("C = %.3f，C_ER = %.4f（理论 %.4f），C_latt = %.3f" % (C, Cr, 2 * M / N / N, C_latt))
print("L = %.2f，L_ER = %.2f（理论 %.2f）" % (L, Lr, np.log(N) / np.log(2 * M / N)))
print("σ = %.1f，ω = %.2f" % (sigma, omega))

# %% [markdown]
# ### 4.3 度分布：幂律、对数正态还是指数？
#
# 按 Clauset、Shalizi 与 Newman（2009）的思路，用连续近似做：
#
# 1. 对每个候选 $k_{\min}$，用最大似然估计 $\hat\gamma = 1 + n\left[\sum_{k_i\ge k_{\min}}\ln\dfrac{k_i}{k_{\min}-1/2}\right]^{-1}$，取使拟合分布与经验分布的 KS 距离最小的 $k_{\min}$；
# 2. 在 $k\ge k_{\min}$ 的尾部，再拟合截断于 $k_{\min}$ 的对数正态和指数分布，用对数似然比 $\mathcal R$ 与 Vuong 检验比较（$\mathcal R>0$ 偏向幂律，$\mathcal R<0$ 偏向备择分布）。

# %%
def fit_powerlaw(x, kmin):
    t = x[x >= kmin]
    g = 1 + len(t) / np.sum(np.log(t / (kmin - 0.5)))
    xs = np.sort(t)
    emp = np.arange(1, len(xs) + 1) / len(xs)
    model = 1 - (xs / (kmin - 0.5)) ** (1 - g)
    return g, np.max(np.abs(emp - model)), len(t)

cands = [km for km in np.unique(k) if (k >= km).sum() >= 50]
fits = [(km,) + fit_powerlaw(k.astype(float), km) for km in cands]
kmin, gamma, ks, n_tail = min(fits, key=lambda f: f[2])
print("k_min = %d，γ = %.2f，KS = %.3f，尾部节点 %d 个（占 %.0f%%）" % (kmin, gamma, ks, n_tail, 100 * n_tail / N))

x = k[k >= kmin].astype(float)
x0 = kmin - 0.5
ll_pl = np.log(gamma - 1) - np.log(x0) - gamma * np.log(x / x0)

def nll_logn(par):
    mu, s = par[0], abs(par[1]) + 1e-9
    logpdf = stats.norm.logpdf(np.log(x), mu, s) - np.log(x)
    tail = stats.norm.sf((np.log(x0) - mu) / s)
    return -(logpdf - np.log(tail)).sum()

res = optimize.minimize(nll_logn, [np.log(x).mean(), np.log(x).std()], method="Nelder-Mead")
mu, s = res.x[0], abs(res.x[1])
ll_ln = stats.norm.logpdf(np.log(x), mu, s) - np.log(x) - np.log(stats.norm.sf((np.log(x0) - mu) / s))
lam = 1 / (x - x0).mean()
ll_ex = np.log(lam) - lam * (x - x0)

def vuong(l1, l2):
    d = l1 - l2
    R = d.sum()
    z = R / (np.sqrt(len(d)) * d.std())
    return R, 2 * stats.norm.sf(abs(z))

for lab, ll in [("对数正态", ll_ln), ("指数", ll_ex)]:
    R, p = vuong(ll_pl, ll)
    print("幂律 vs %s：R = %.1f，p = %.2g" % (lab, R, p))

# %% [markdown]
# ## 5. 与零模型比较
#
# 配置模型保留了度序列，因此“真实网络与配置模型之差”只能来自度序列以外的结构。比较两者的聚集系数与平均路径；再看 BA 模型能否同时再现酵母网络的聚集与重尾。

# %%
print("聚集系数：酵母 %.3f，配置模型 %.3f，BA %.3f，WS %.3f" %
      (C, tab.loc["configuration", "C"], tab.loc["BA", "C"], tab.loc["WS (p=0.1)", "C"]))
print("平均路径：酵母 %.2f，配置模型 %.2f，BA %.2f，WS %.2f" %
      (L, tab.loc["configuration", "L"], tab.loc["BA", "L"], tab.loc["WS (p=0.1)", "L"]))
cm_C = []
for s in range(3):
    H = G.copy()
    nx.double_edge_swap(H, nswap=5 * M, max_tries=100 * M, seed=10 + s)
    cm_C.append(nx.average_clustering(H))
print("3 个配置模型样本的聚集系数:", np.round(cm_C, 3))
print("用时 %.0f 秒" % (time.time() - t0))

# %% [markdown]
# ## 6. 作图
#
# 左：五个网络度分布的互补累积分布（双对数），黑色虚线是从 $k_{\min}$ 起的幂律拟合。右：各网络在 $(L, C)$ 平面上的位置。

# %%
def ccdf(a):
    xs = np.sort(np.unique(a))
    return xs, np.array([(a >= v).mean() for v in xs])

fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
cols = {"yeast": "#c53030", "ER": "#a0aec0", "WS (p=0.1)": "#38a169", "BA": "#3182ce", "configuration": "#d69e2e"}
for name, H in models.items():
    kk = np.array([d for _, d in H.degree()])
    xs, ys = ccdf(kk[kk > 0])
    ax[0].loglog(xs, ys, ".", ms=4, color=cols[name], label=name)
xx = np.logspace(np.log10(kmin), np.log10(k.max()), 50)
ax[0].loglog(xx, (n_tail / N) * (xx / kmin) ** (1 - gamma), "k--", lw=1, label="power-law fit γ=%.2f" % gamma)
ax[0].set_xlabel("degree k")
ax[0].set_ylabel("P(K ≥ k)")
ax[0].legend(fontsize=8)
for name in tab.index:
    ax[1].plot(tab.loc[name, "L"], tab.loc[name, "C"], "o", ms=9, color=cols[name], label=name)
ax[1].set_xlabel("average path length L")
ax[1].set_ylabel("average clustering C")
ax[1].legend(fontsize=8)
fig.tight_layout()

# %% [markdown]
# ## 7. 解读与局限
#
**结果。** 酵母网络有 3 384 个蛋白、43 030 条边，平均度 25.4；最大连通分支含 2 780 个蛋白（82.2%）。度最高的全是核糖体小亚基蛋白（RPS13 度 282 等）。
#
# **小世界：是，但路径并不短于随机网络。** 聚集系数 $C=0.581$，是 ER 网络（0.0076，与理论值 $\langle k\rangle/N\approx0.0075$ 一致）的约 76 倍；平均路径长度（抽样估计）约 5.17，ER 为 2.83（理论 $\ln N/\ln\langle k\rangle\approx2.51$）。$\sigma=42$，远大于 1；但 $\omega=-0.26$，偏向“规则”一侧：聚集接近规则网格（$C_{\text{latt}}=0.72$），路径却比随机网络长将近一倍。所以“小世界”的判断取决于用哪个指数，应同时报告 $C$、$L$ 和参照值，而不只报告 $\sigma$。
#
# **四个模型各自缺什么。** WS 网络（$p=0.1$）的聚集（0.528）与酵母接近，但最大度只有 33，没有枢纽；BA 网络有枢纽（最大度 338），但聚集只有 0.029；ER 两者都没有。配置模型保留了度序列，因此 $\langle k^2\rangle/\langle k\rangle$ 与最大度完全相同，但聚集系数只有 0.12（3 个样本都是 0.12 左右），路径 2.97——真实网络远高出的聚集、明显更长的路径，都来自度序列以外的结构（复合物成团、模块化）。没有一个经典模型能同时再现高聚集、重尾和较长的路径。
#
# **无标度：证据不支持纯幂律。** 按 KS 距离选出的 $k_{\min}=65$，只覆盖 432 个蛋白（13%），$\hat\gamma=2.68$；在这段尾部，对数正态（$\mathcal R=-33.5$，$p\approx8\times10^{-8}$）和指数分布（$\mathcal R=-38.6$）都显著优于幂律。度分布是重尾的（$\langle k^2\rangle/\langle k\rangle=109$，ER 只有 26），但“重尾”不等于“幂律”。
#
# **局限。**
#
# - **度分布的检验结论依赖数据处理**：阈值 700、只用物理证据、STRING 综合打分本身都会改变度分布的尾部。Broido 与 Clauset（2019）在近千个网络上的检验显示，“强”无标度证据很少见，对数正态往往同样好或更好；本例的结论也只适用于这张网络和这些选择（见[无标度之争](network-models.identification.html)）。
# - **连续近似**：这里用连续分布近似离散的度（$k_{\min}-1/2$ 修正），没有做拟合优度的 bootstrap $p$ 值；严格分析应使用离散幂律与半参数 bootstrap。
# - **模型参数是按“同 $N$、同边数”粗略匹配的**：WS 的重连概率、BA 的 $m$ 都可以调；它们的作用是提供参照，而不是拟合这张网络的生成机制。
# - **STRING 的物理网络包含复合物成员关系**：大复合物以团的形式出现，抬高了聚集系数。复制–分化、空间（几何）模型等机制可能更接近蛋白质网络的形成过程（见[复制–分化模型](network-models.duplication-divergence.html)、[空间网络与随机几何图](network-models.spatial-networks.html)）。
