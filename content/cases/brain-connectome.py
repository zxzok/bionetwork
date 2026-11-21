# %% [markdown]
# # 69 名健康成人的结构与功能连接组：组一致性阈值、小世界、富人俱乐部与结构–功能耦合
#
# 本案例用真实的弥散谱成像（DSI）结构连接和静息态 fMRI 功能连接，把[脑连接组](brain-connectome.html)专题的主要分析走一遍：构建组水平结构网络，计算聚集、效率和模块，与度保持随机网络比较，检验富人俱乐部，再看结构连接能在多大程度上解释功能连接，最后检查功能网络指标对阈值的依赖。
#
# **1. 数据来源**
#
# - 数据集：Griffa、Alemán-Gómez 与 Hagmann（2019）在 Zenodo 公开的 “Structural and functional connectome from 70 young healthy adults”，doi:[10.5281/zenodo.2872624](https://doi.org/10.5281/zenodo.2872624)，许可证 CC BY 4.0。下载日期 2026-11-20。
# - 被试与采集（据数据说明）：70 名健康成人（年龄 28.8 ± 9.1 岁，27 名女性），3T 扫描；DSI 序列重建纤维方向，确定性流线追踪；静息态 fMRI 共 280 个时间点，TR 1.92 s。
# - 结构连接的边权是**纤维密度**：两区之间的流线数，按流线平均长度和两区平均表面积归一化（Hagmann 等, 2008 的做法），用来部分校正追踪对长纤维的偏倚和脑区大小差异。功能连接是去除头动、白质和脑脊液信号并做 scrubbing 后的皮尔逊相关。
# - 本案例只用最粗的尺度：68 个皮层区（Desikan–Killiany 分区）。文件 `data/lausanne68_sc_fc.csv` 由原始 `.mat` 文件整理而来，处理步骤见 `data/SOURCES.md`。
# - 原文件不含脑区名称。脑区名称、半球、静息态子网络标签和坐标取自同一批数据的共识连接组记录（Shafiei 等, 2019, doi:[10.5281/zenodo.3067849](https://doi.org/10.5281/zenodo.3067849)，CC BY 4.0），整理为 `data/lausanne68_nodes.csv`；两份文件的节点顺序经组水平 SC、FC 的相关核对一致。节点 0–33 为右半球，34–67 为左半球，$i$ 与 $i+34$ 是同名脑区。
#
# %% [markdown]
# ## 2. 读入与清洗
#
# 每行是一名被试的一种模态，列是上三角的 2278 条边（列名 `i-j`）。先还原成 $69\times68\times68$ 的对称矩阵，再做三项检查：矩阵对称、无缺失值；SC 非负、FC 在 $[-1,1]$ 内；每名被试结构网络的密度。
#
# %%
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from scipy.stats import spearmanr

df = pd.read_csv("data/lausanne68_sc_fc.csv")
N = 68
iu = np.triu_indices(N, 1)
assert list(df.columns[2:]) == [f"{i}-{j}" for i, j in zip(*iu)], "列顺序与 triu_indices 不一致"


def to_matrices(mod):
    V = df[df.modality == mod].iloc[:, 2:].to_numpy(float)
    M = np.zeros((len(V), N, N))
    M[:, iu[0], iu[1]] = V
    return M + M.transpose(0, 2, 1)


SC = to_matrices("SC")
FC = to_matrices("FC")
n_sub = SC.shape[0]
print("被试数:", n_sub, "；每人边数:", len(iu[0]))
print("SC 缺失值:", np.isnan(SC).sum(), " FC 缺失值:", np.isnan(FC).sum())
print("SC 最小值 %.3g，FC 范围 [%.2f, %.2f]" % (SC.min(), FC[:, iu[0], iu[1]].min(), FC[:, iu[0], iu[1]].max()))
dens = (SC[:, iu[0], iu[1]] > 0).mean(1)
print("个体结构网络密度：均值 %.3f，范围 %.3f–%.3f" % (dens.mean(), dens.min(), dens.max()))
nz = SC[:, iu[0], iu[1]][SC[:, iu[0], iu[1]] > 0]
print("非零纤维密度跨越 %.1f 个数量级（第 1 到第 99 百分位）" % np.log10(np.percentile(nz, 99) / np.percentile(nz, 1)))

nodes = pd.read_csv("data/lausanne68_nodes.csv")
assert (nodes.hemi[:34] == "rh").all() and (nodes.hemi[34:] == "lh").all()
assert (nodes.region[:34].to_numpy() == nodes.region[34:].to_numpy()).all(), "i 与 i+34 应为同名脑区"
hemi = np.where(nodes.hemi == "rh", "A", "B")       # A = 右半球，B = 左半球
lab_name = (nodes.short + "-" + nodes.hemi.str[0].str.upper()).to_numpy()   # 例如 PCUN-R
same_hemi = hemi[:, None] == hemi[None, :]
print("个体平均：半球内 SC 连接存在比例 %.2f，半球间 %.2f"
      % ((SC > 0)[:, same_hemi & ~np.eye(N, dtype=bool)].mean(), (SC > 0)[:, ~same_hemi].mean()))

# %% [markdown]
# 纤维密度的分布极度偏斜、跨越几个数量级，这是专题页[边权的定义与归一化](brain-connectome.structural-connectivity.html)中提到的典型特征，所以后面比较边权时取对数或用秩相关。半球间的结构连接比半球内稀疏得多：胼胝体纤维集中在少数通路上，而且长程、穿过交叉区域的纤维本来就更难追踪到。
#
# %% [markdown]
# ## 3. 构网
#
# **结构网络**：用[组一致性阈值](brain-connectome.structural-connectivity.html)，只保留至少 50% 被试中都出现的连接，边权取所有被试纤维密度的平均。阈值从 30% 到 75% 时边数的变化也一并列出。
#
# **功能网络**：每名被试的 $r$ 做 Fisher $z$ 变换，平均后再反变换，得到组平均 FC。它几乎是全连接的，图论指标要么用加权形式，要么先阈值化（第 5 节）。
#
# %%
presence = (SC > 0).mean(0)
for p in (0.3, 0.5, 0.75):
    A_p = presence >= p
    np.fill_diagonal(A_p, False)
    print("组一致性阈值 %.0f%%：%d 条边，密度 %.3f" % (100 * p, A_p.sum() // 2, A_p.sum() / (N * (N - 1))))

A = (presence >= 0.5).astype(float)
np.fill_diagonal(A, 0)
W = np.where(A > 0, SC.mean(0), 0.0)
G = nx.from_numpy_array(A)
print("组水平结构网络：%d 个节点，%d 条边，连通：%s" % (G.number_of_nodes(), G.number_of_edges(), nx.is_connected(G)))

Z = np.arctanh(np.clip(FC, -0.999, 0.999))
FCg = np.tanh(Z.mean(0))
np.fill_diagonal(FCg, 0)
homo = np.array([FCg[i, i + 34] for i in range(34)])
print("组平均 FC：全部边均值 %.3f；同源脑区对均值 %.3f；其余半球间边均值 %.3f"
      % (FCg[iu].mean(), homo.mean(), FCg[:34, 34:][~np.eye(34, dtype=bool)].mean()))

fig, ax = plt.subplots(1, 2, figsize=(10, 4.2))
im = ax[0].imshow(np.log10(W + 1e-5), cmap="viridis")
ax[0].set_title("Group SC (log10 fibre density)")
plt.colorbar(im, ax=ax[0], fraction=0.046)
im = ax[1].imshow(FCg, cmap="RdBu_r", vmin=-0.8, vmax=0.8)
ax[1].set_title("Group FC (Pearson r)")
plt.colorbar(im, ax=ax[1], fraction=0.046)
for a in ax:
    a.axhline(33.5, color="k", lw=0.6)
    a.axvline(33.5, color="k", lw=0.6)
plt.tight_layout()

# %% [markdown]
# SC 矩阵的两个对角块（半球内）远比非对角块（半球间）稠密；FC 矩阵的非对角块里有一条清楚的“副对角线”，就是同源脑区对之间的强功能连接。
#
# %% [markdown]
# ## 4. 核心指标：分离、整合、模块与枢纽
#
# 在二值结构网络上计算平均聚集系数 $C$、特征路径长度 $L$、全局效率 $E$；在加权网络上用 Louvain 做模块划分（固定随机种子，并重复 20 次检查稳定性），看模块与半球的对应关系；用度和参与系数区分“省内枢纽”和“连接枢纽”（见[拓扑指标](brain-connectome.topology.html)）。
#
# %%
C = nx.average_clustering(G)
L = nx.average_shortest_path_length(G)
E = nx.global_efficiency(G)
print("C = %.3f，L = %.3f，E = %.3f" % (C, L, E))

Gw = nx.from_numpy_array(W / W.max())
parts = [nx.community.louvain_communities(Gw, weight="weight", seed=s) for s in range(20)]
Qs = [nx.community.modularity(Gw, p, weight="weight") for p in parts]
best = parts[int(np.argmax(Qs))]
print("Louvain 20 次：Q = %.3f–%.3f，模块数 %s" % (min(Qs), max(Qs), sorted({len(p) for p in parts})))
lab = np.zeros(N, int)
for k, c in enumerate(sorted(best, key=min)):
    lab[list(c)] = k
for k in range(lab.max() + 1):
    members = np.where(lab == k)[0]
    in_a = set(members[members < 34])
    in_b = set(members[members >= 34] - 34)
    note = "，全部由成对的同源脑区组成" if in_a and in_a == in_b else ""
    print("  模块 %d：%2d 个节点，其中右半球 %2d 个、左半球 %2d 个%s"
          % (k, len(members), len(in_a), len(in_b), note))
    if note:
        print("     脑区：", ", ".join(sorted(nodes.region[sorted(in_a)])))

deg = A.sum(1)
kis = np.array([[A[i, lab == s].sum() for s in range(lab.max() + 1)] for i in range(N)])
P = 1 - ((kis / deg[:, None]) ** 2).sum(1)
order = np.argsort(deg)[::-1][:8]
print("度最高的 8 个节点：", [lab_name[i] for i in order])
print("  它们的度：", deg[order].astype(int).tolist())
print("  参与系数：", np.round(P[order], 2).tolist())
print("全部节点参与系数的中位数 %.2f" % np.median(P))

# %% [markdown]
# Louvain 多次运行给出的模块数（5 或 6 个）和 $Q$ 有小幅波动，这是模块度存在许多近似最优解的表现，正式分析应构建共识划分。两个最大的模块各自基本只占一个半球，说明结构模块首先反映了“半球”这一解剖事实；另外三个较小的模块横跨两半球，而且恰好由成对的同名脑区组成：内侧额叶与前扣带回、楔前叶与后扣带回一带、内侧枕叶视觉皮层。它们都位于大脑中线附近，两侧之间有胼胝体纤维直接相连，所以在模块划分中被“绑”在一起。
#
# 度最高的节点是双侧顶上小叶、额上回、楔前叶和左侧岛叶——与专题页列举的结构枢纽（楔前叶/后扣带回、额上回、顶上小叶、岛叶）一致。它们中多数参与系数高于全部节点的中位数，连接分布在多个模块之间，更像“连接枢纽”；左侧岛叶的参与系数明显偏低，连接集中在本模块内。度与参与系数回答的是不同问题。
#
# %% [markdown]
# ## 5. 与零模型比较
#
# **(a) 小世界**：用 Maslov–Sneppen 度保持边交换（`nx.double_edge_swap`，每条边平均交换约 10 次）生成 20 个随机网络，计算 $C/C_{\text{rand}}$、$L/L_{\text{rand}}$ 和 $\sigma$。
#
# **(b) 富人俱乐部**：$\phi(k)$ 与度保持随机网络的 $\phi_{\text{rand}}(k)$ 之比 $\phi_{\text{norm}}(k)$。
#
# **(c) 结构–功能耦合**：有直接结构连接的脑区对，FC 是否更强？在这些脑区对中，纤维密度与 FC 的秩相关有多大？作为零模型，把 SC 边权在已有的边之间随机置换 1000 次。最后用脑区坐标检查空间距离的作用：近处的脑区既更容易有结构连接、FC 也更强，耦合中有多少只是二者共同依赖距离？这里用“对距离回归后的秩残差”之间的相关作为偏秩相关。
#
# %%
rng = np.random.default_rng(0)
Cr, Lr = [], []
for s in range(20):
    H = G.copy()
    nx.double_edge_swap(H, nswap=10 * H.number_of_edges(), max_tries=10 ** 6, seed=int(rng.integers(1e9)))
    if not nx.is_connected(H):
        continue
    Cr.append(nx.average_clustering(H))
    Lr.append(nx.average_shortest_path_length(H))
n_null = len(Cr)
Cr, Lr = np.mean(Cr), np.mean(Lr)
sigma = (C / Cr) / (L / Lr)
print("度保持随机网络（%d 个连通样本）：C_rand = %.3f，L_rand = %.3f" % (n_null, Cr, Lr))
print("C/C_rand = %.2f，L/L_rand = %.2f，σ = %.2f" % (C / Cr, L / Lr, sigma))

ks = np.arange(5, 31)
rc = nx.rich_club_coefficient(G, normalized=False)
phi = np.array([rc.get(k, np.nan) for k in ks])
phi_r = []
for s in range(10):
    H = G.copy()
    nx.double_edge_swap(H, nswap=10 * H.number_of_edges(), max_tries=10 ** 6, seed=100 + s)
    r = nx.rich_club_coefficient(H, normalized=False)
    phi_r.append([r.get(k, np.nan) for k in ks])
phi_r = np.nanmean(phi_r, 0)
phi_norm = phi / phi_r
n_rich = np.array([(deg > k).sum() for k in ks])
for k, f, fr, fn, nr in zip(ks, phi, phi_r, phi_norm, n_rich):
    if k % 5 == 0:
        print("k > %2d：%2d 个节点，φ = %.2f，φ_rand = %.2f，φ_norm = %.2f" % (k, nr, f, fr, fn))

m = A[iu] > 0
fc_e = FCg[iu]
print("有直接结构连接的脑区对：FC 均值 %.3f（%d 对）；没有的：%.3f（%d 对）"
      % (fc_e[m].mean(), m.sum(), fc_e[~m].mean(), (~m).sum()))
rho_obs = spearmanr(W[iu][m], fc_e[m])[0]
w_e = W[iu][m]
null = [spearmanr(rng.permutation(w_e), fc_e[m])[0] for _ in range(1000)]
print("有连接的脑区对中，纤维密度与 FC 的 Spearman ρ = %.3f；置换零分布 95%% 上界 %.3f"
      % (rho_obs, np.percentile(null, 95)))

# 空间距离：连接概率与 FC 都随距离衰减，结构–功能耦合有多少只是“共同依赖距离”？
xyz = nodes[["x", "y", "z"]].to_numpy(float)
dist = np.linalg.norm(xyz[:, None, :] - xyz[None, :, :], axis=2)
d_e = dist[iu]
same_e = same_hemi[iu]
tert = np.quantile(d_e[same_e], [1 / 3, 2 / 3])
for name_, lo, hi in (("近", 0, tert[0]), ("中", tert[0], tert[1]), ("远", tert[1], np.inf)):
    mm = same_e & (d_e >= lo) & (d_e < hi)
    print("半球内%s距离三分位：组网络连接概率 %.2f，平均 FC %.3f" % (name_, m[mm].mean(), fc_e[mm].mean()))
print("全部脑区对：FC 与距离的 Spearman ρ = %.3f" % spearmanr(fc_e, d_e)[0])


def rank_resid(y, x):
    ry, rx = np.argsort(np.argsort(y)), np.argsort(np.argsort(x))
    beta = np.polyfit(rx, ry, 1)
    return ry - np.polyval(beta, rx)


rho_partial = np.corrcoef(rank_resid(W[iu][m], d_e[m]), rank_resid(fc_e[m], d_e[m]))[0, 1]
print("有连接的脑区对中，控制距离后纤维密度与 FC 的偏秩相关 = %.3f（未控制时 %.3f）" % (rho_partial, rho_obs))

# 同源脑区对的结构连接
homo_sc = np.array([A[i, i + 34] for i in range(34)])
print("34 对同源脑区中，组网络里有直接结构连接的有 %d 对；它们的 FC 均值 %.3f，无直接连接的 %.3f"
      % (homo_sc.sum(), homo[homo_sc > 0].mean(), homo[homo_sc == 0].mean()))

# %% [markdown]
# ## 6. 阈值如何改变功能网络的“拓扑”
#
# 对组平均 FC 做[比例阈值](brain-connectome.thresholding.html)（保留最强的正相关），在密度 5%–40% 上计算 $C$ 和 $E$，并与同边数 ER 随机图比较。
#
# %%
def proportional(Fm, d):
    w = Fm[iu]
    k = int(round(d * len(w)))
    keep = np.argsort(w)[::-1][:k]
    H = nx.Graph()
    H.add_nodes_from(range(N))
    H.add_edges_from(zip(iu[0][keep], iu[1][keep]))
    return H


rows = []
for d in (0.05, 0.10, 0.15, 0.20, 0.30, 0.40):
    H = proportional(FCg, d)
    R = nx.gnm_random_graph(N, H.number_of_edges(), seed=1)
    rows.append((d, nx.average_clustering(H), nx.global_efficiency(H), nx.number_connected_components(H),
                 nx.average_clustering(R)))
print("密度   C      E      分量数  C/C_ER")
for d, c, e, nc, cr in rows:
    print("%.2f  %.3f  %.3f  %4d   %.2f" % (d, c, e, nc, c / cr))

# %% [markdown]
# ## 7. 作图
#
# %%
fig, ax = plt.subplots(1, 3, figsize=(14, 4))
ax[0].scatter(np.log10(W[iu][m]), fc_e[m], s=8, alpha=0.5, label="direct SC")
ax[0].set_xlabel("log10 fibre density")
ax[0].set_ylabel("group FC")
ax[0].set_title("SC-FC coupling, Spearman rho = %.2f" % rho_obs)
ax[1].plot(ks, phi_norm, "o-", ms=3)
ax[1].axhline(1, color="gray", ls="--")
ax[1].set_xlabel("degree k")
ax[1].set_ylabel("phi_norm(k)")
ax[1].set_title("Rich club (degree-preserving null)")
ax[2].plot([r[0] for r in rows], [r[1] for r in rows], "o-", label="C")
ax[2].plot([r[0] for r in rows], [r[2] for r in rows], "s-", label="E")
ax[2].set_xlabel("density")
ax[2].legend()
ax[2].set_title("FC metrics vs threshold")
plt.tight_layout()

# %% [markdown]
# ## 8. 解读与局限
#
# **结果**
#
# 1. 组水平结构网络的聚集系数约为度保持随机网络的两倍，路径长度只长约 8%，$\sigma>1$，与 Hagmann 等（2008）等结构网络研究报告的“高聚集、短路径”一致。
# 2. 两个最大的结构模块各占一个半球，较小的模块由中线附近成对的同名脑区组成；度最高的是顶上小叶、额上回、楔前叶和岛叶，多数参与系数较高，但并非全部，仅凭度不能确定枢纽的角色。
# 3. 未归一化的 $\phi(k)$ 随 $k$ 从约 0.27 升到 0.7，看起来像“富人俱乐部”；但度保持随机网络的 $\phi_{\text{rand}}(k)$ 几乎同样上升，$\phi_{\text{norm}}(k)$ 始终接近 1。也就是说，在这个 68 区、密度约 25% 的二值组网络中，高度节点之间的连接没有明显超出“度高所以更容易相连”的预期。这正是需要归一化的原因。它与 van den Heuvel & Sporns（2011）在更高分辨率网络中报告的富人俱乐部并不矛盾：节点粗、网络稠密时，度最高的少数节点之间在随机网络里也几乎全连，留给“超出随机”的空间很小；改用更细的分区、加权富人俱乐部，或者更严格的一致性阈值，结论可能不同，应作为敏感性分析报告。
# 4. 有直接结构连接的脑区对，FC 明显更强；在这些脑区对中，纤维密度与 FC 呈中等程度的正秩相关，远超置换零分布。同时，同源脑区之间即使在组网络中没有直接连接，FC 也很强——功能连接可以经由间接通路产生（Honey 等, 2009）。但空间距离是一个重要的共同因素：近处的脑区更容易有结构连接，FC 也更强；控制距离后，纤维密度与 FC 的偏秩相关从约 0.39 降到约 0.16，下降了一半以上——相当一部分“耦合”来自二者共同依赖距离。
# 5. 功能网络的 $C$、$E$ 随密度单调变化，且低密度时网络会断开；只报告一个密度，结论就绑定在这个选择上。
#
# **局限**
#
# - 结构连接来自确定性流线追踪，存在系统性的假阳性和假阴性，长程连接尤其不可靠（见[重建偏倚](brain-connectome.structural-connectivity.html)）；组一致性阈值减少了假阳性，但也会删掉个体特异的真实连接。阈值从 30% 改到 75%，边数会改变近一倍。
# - 度保持随机网络破坏了空间嵌入：真实脑网络中相邻脑区更容易相连，单凭这一点就能抬高聚集。更严格的零模型应同时保持连接长度分布（见[空间嵌入与布线代价](brain-connectome.spatial-embedding.html)）。这里只用脑区坐标的欧氏距离做了一个粗略检查；坐标来自共识连接组文件，坐标空间未另行核实，只用于比较相对距离。
# - 只有 68 个皮层区，没有皮层下结构；节点数改变后所有指标的绝对值都会变（Zalesky 等, 2010），不宜与其他图谱的研究直接比较数值。
# - 组平均矩阵掩盖了个体差异；功能连接只有一次约 9 分钟的扫描，单条边的个体估计噪声较大。
# - 枢纽的解剖学解释依赖节点标签与分区：68 区的 Desikan–Killiany 分区中，顶上小叶、额上回等脑区面积很大，度高的一部分原因可能只是“节点大”。
#