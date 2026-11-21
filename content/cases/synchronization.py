# %% [markdown]
# # 人脑结构连接组上的 Kuramoto 同步：拉普拉斯谱、同步阈值与功能连接
#
# 本案例把 Kuramoto 振荡器放到真实的人脑结构连接组（70 名健康成人的组水平一致性网络，114 个皮层区）上，完整做一次网络同步分析：计算拉普拉斯谱、代数连通度与特征值比，用异质平均场和最大特征值两种近似估计同步阈值，扫描耦合强度得到 $r(K)$ 曲线与亚稳态，考察两半球之间的同步，并把模拟的相位一致性与同一批被试的静息态功能连接（FC）比较；所有结构指标都与保度随机化网络对照。所用定义与[Kuramoto 模型与序参量](synchronization.kuramoto-model.html)、[网络拓扑与同步阈值](synchronization.network-kuramoto.html)、[拉普拉斯谱与代数连通度](synchronization.laplacian-spectrum.html)、[神经质量模型与全脑模型](synchronization.whole-brain-models.html)一致。
#
# ## 1. 数据来源
#
# - 数据集：Shafiei G, Markello R, Talpalaru T, et al.（2019）Consensus structural and functional connectome from 70 young healthy adults. Zenodo，DOI [10.5281/zenodo.3067849](https://doi.org/10.5281/zenodo.3067849)（文件 `Consensus_Connectomes.mat`，2026-11-20 下载）。它由 Griffa、Alemán-Gómez 与 Hagmann（2019）发布的个体数据（Zenodo，DOI [10.5281/zenodo.2872624](https://doi.org/10.5281/zenodo.2872624)）构建，相关论文为 Shafiei 等（2020）*Biological Psychiatry* 87(8):727–735。
# - 许可证：CC BY 4.0（Zenodo 记录所标），可自由再分发，须署名。
# - 采集与处理（据个体数据集说明）：70 名健康成人（年龄 28.8 ± 9.1 岁，女性 27 名），3T 扫描，扩散谱成像（DSI）确定性纤维追踪；结构连接强度为**纤维密度**（两区之间的流线数，按流线平均长度和两区平均表面积归一化）；静息态 fMRI 在所有被试的时间序列拼接后计算一个组水平相关矩阵，只保留自助法检验中符号一致的相关。
# - 本案例只取 Lausanne 图谱的 114 区尺度，整理为三个文件：`data/lausanne114_sc_edges.csv`（结构连接的边、纤维密度和纤维长度）、`data/lausanne114_nodes.csv`（脑区名、半球、静息态子网络标签、坐标）、`data/lausanne114_fc.csv`（组水平 FC 矩阵）。

# %% [markdown]
# ## 2. 读入与清洗
#
# 检查四件事：结构连接是否对称、有无自环、网络是否连通、FC 是否对称且对角为 1。纤维密度的绝对数值没有物理单位，耦合强度 $K$ 的大小只有在固定了权重尺度后才有意义，所以把权重整体除以平均强度，使 $\langle s\rangle=1$。这样 $K$ 就是“一个平均脑区受到的总耦合”的量级。

# %%
import time
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

t0 = time.time()
edges = pd.read_csv("data/lausanne114_sc_edges.csv")
nodes = pd.read_csv("data/lausanne114_nodes.csv")
FC = np.loadtxt("data/lausanne114_fc.csv", delimiter=",")
N = len(nodes)
print("脑区 %d 个，结构连接边 %d 条；FC 矩阵 %s" % (N, len(edges), FC.shape))
print("自环 %d 条，重复边 %d 条" % ((edges.i == edges.j).sum(), edges.duplicated(["i", "j"]).sum()))
print("FC 对称: %s，对角全为 1: %s，FC 中为 0（未通过检验）的比例 %.1f%%"
      % (np.allclose(FC, FC.T), np.allclose(np.diag(FC), 1), 100 * (FC[np.triu_indices(N, 1)] == 0).mean()))

W = np.zeros((N, N))
W[edges.i, edges.j] = edges.fiber_density
W = W + W.T
W = W / W.sum(axis=1).mean()          # 归一化：平均强度 <s> = 1
A = (W > 0).astype(float)
G = nx.from_numpy_array(W)
print("连通: %s" % nx.is_connected(G))
hemi = nodes.hemi.to_numpy()
print("半球:", nodes.hemi.value_counts().to_dict(), "；静息态子网络:", nodes.rsn.value_counts().to_dict())

# %% [markdown]
# ## 3. 构网
#
# 节点是 114 个皮层区，无向加权边的权重是归一化后的纤维密度 $W_{ij}$。同时保留无权邻接矩阵 $A_{ij}=\mathbb 1[W_{ij}>0]$，用来计算度。结构连接的一个已知特点是半球间连接少（经胼胝体的长纤维更难追踪），这里先统计一下。

# %%
k = A.sum(axis=1)
s = W.sum(axis=1)
iu = np.triu_indices(N, 1)
same_hemi = (hemi[:, None] == hemi[None, :])[iu]
has_edge = A[iu] > 0
print("密度 %.3f，<k> = %.1f，k 范围 %d–%d" % (has_edge.mean(), k.mean(), k.min(), k.max()))
print("强度 s（<s>=1）：范围 %.2f–%.2f，变异系数 %.2f" % (s.min(), s.max(), s.std() / s.mean()))
print("半球内的边 %d 条，半球间的边 %d 条；半球间边的权重之和占 %.1f%%"
      % ((has_edge & same_hemi).sum(), (has_edge & ~same_hemi).sum(), 100 * W[iu][~same_hemi].sum() / W[iu].sum()))
print("平均聚集系数（无权）%.3f" % nx.average_clustering(nx.from_numpy_array(A)))

# %% [markdown]
# ## 4. 核心指标
#
# **（1）拉普拉斯谱。** $L=D-W$ 的特征值 $0=\mu_1\le\mu_2\le\cdots\le\mu_N$。$\mu_2$（代数连通度）决定共识动力学中最慢模式的衰减 $e^{-K\mu_2t}$；特征值比 $\mu_N/\mu_2$ 越小，相同振荡器的完全同步越容易稳定（[主稳定函数](synchronization.master-stability.html)第 3 类）。Fiedler 向量的符号给出“最便宜的二分”。
#
# **（2）同步阈值。** 网络 Kuramoto 模型 $\dot\theta_i=\omega_i+K\sum_jW_{ij}\sin(\theta_j-\theta_i)$（总输入随强度增长的写法），固有频率取标准高斯分布，$K_0=2/(\pi g(0))=2\sqrt{2\pi}/\pi\approx1.60$。异质平均场 $K_c\approx K_0\langle k\rangle/\langle k^2\rangle$（加权网络用强度 $s$ 代替度，是同一思路的推广），最大特征值近似 $K_c\approx K_0/\Lambda_{\max}$。
#
# **（3）模拟。** 欧拉法积分（$dt=0.02$，总时长 200，丢弃前一半），对每个 $K$ 记录时间平均的 $r$、亚稳态（$r(t)$ 的标准差）、两半球各自的序参量，以及两两相位一致性 $C_{ij}=\langle\cos(\theta_i-\theta_j)\rangle_t$，后者作为“模拟功能连接”与实测 FC 比较。每个 $K$ 用 3 组不同的固有频率取平均。

# %%
K0 = 2 * np.sqrt(2 * np.pi) / np.pi

def spectrum(W):
    L = np.diag(W.sum(axis=1)) - W
    mu, vec = np.linalg.eigh(L)
    return mu, vec[:, 1]

mu, fiedler = spectrum(W)
lam_max = np.linalg.eigvalsh(W).max()
print("加权拉普拉斯：mu_2 = %.4f，mu_N = %.3f，特征值比 mu_N/mu_2 = %.1f" % (mu[1], mu[-1], mu[-1] / mu[1]))
muA, _ = spectrum(A)
print("无权拉普拉斯：mu_2 = %.3f，mu_N = %.2f，特征值比 = %.1f" % (muA[1], muA[-1], muA[-1] / muA[1]))
side = np.sign(fiedler)
agree = max(np.mean((side > 0) == (hemi == "lh")), np.mean((side > 0) == (hemi == "rh")))
print("Fiedler 向量的符号与半球划分一致的比例: %.1f%%" % (100 * agree))
Kc_hmf = K0 * s.mean() / (s**2).mean()
Kc_lam = K0 / lam_max
print("同步阈值估计：HMF K0<s>/<s^2> = %.3f；最大特征值 K0/Lambda_max = %.3f（Lambda_max = %.3f）" % (Kc_hmf, Kc_lam, lam_max))

lh, rh = hemi == "lh", hemi == "rh"

def kuramoto(W, K, omega, T=200.0, dt=0.02, seed=0):
    rng = np.random.default_rng(seed)
    theta = rng.uniform(0, 2 * np.pi, len(omega))
    n = int(T / dt)
    rs, rl, rr = [], [], []
    C = np.zeros((len(omega), len(omega))); cnt = 0
    for t in range(n):
        sn, cs = np.sin(theta), np.cos(theta)
        theta = theta + dt * (omega + K * (cs * (W @ sn) - sn * (W @ cs)))
        if t >= n // 2:
            z = np.exp(1j * theta)
            rs.append(abs(z.mean())); rl.append(abs(z[lh].mean())); rr.append(abs(z[rh].mean()))
            if t % 10 == 0:
                C += np.cos(theta[:, None] - theta[None, :]); cnt += 1
    return np.mean(rs), np.std(rs), 0.5 * (np.mean(rl) + np.mean(rr)), C / cnt

omegas = [np.random.default_rng(10 + d).standard_normal(N) for d in range(3)]
Ks = np.array([0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 4.0, 6.0])

def sweep(W, tag):
    out = {"r": [], "meta": [], "r_hemi": [], "fc_corr": [], "C": []}
    for K in Ks:
        res = [kuramoto(W, K, om, seed=d) for d, om in enumerate(omegas)]
        C = np.mean([x[3] for x in res], axis=0)
        out["r"].append(np.mean([x[0] for x in res]))
        out["meta"].append(np.mean([x[1] for x in res]))
        out["r_hemi"].append(np.mean([x[2] for x in res]))
        out["fc_corr"].append(np.corrcoef(C[iu], FC[iu])[0, 1])
        out["C"].append(C)
    out = {key: np.array(v) for key, v in out.items()}
    print("[%s]" % tag)
    print("  K       :", np.round(Ks, 2).tolist())
    print("  r       :", np.round(out["r"], 2).tolist())
    print("  r 半球内:", np.round(out["r_hemi"], 2).tolist())
    print("  std r(t):", np.round(out["meta"], 3).tolist())
    print("  corr(C, FC):", np.round(out["fc_corr"], 3).tolist())
    return out

real = sweep(W, "real connectome")
print("随机相位的基线 1/sqrt(N) = %.3f" % (1 / np.sqrt(N)))
best = int(np.argmax(real["fc_corr"]))
print("与实测 FC 最相似的 K = %.2f（相关 %.3f），亚稳态最高的 K = %.2f"
      % (Ks[best], real["fc_corr"][best], Ks[int(np.argmax(real["meta"]))]))
print("对照：结构连接权重本身与 FC 的相关 = %.3f" % np.corrcoef(W[iu], FC[iu])[0, 1])

# 半球内 vs 半球间的模拟一致性与实测 FC
Cb = real["C"][best]
print("K = %.2f 时模拟一致性：半球内平均 %.3f，半球间平均 %.3f；实测 FC：半球内 %.3f，半球间 %.3f"
      % (Ks[best], Cb[iu][same_hemi].mean(), Cb[iu][~same_hemi].mean(), FC[iu][same_hemi].mean(), FC[iu][~same_hemi].mean()))

# %% [markdown]
# ## 5. 与零模型比较
#
# 零模型是**保度随机化**：对无权拓扑做双边交换（每个脑区的连接数不变），再把原有的纤维密度随机分配给新边。它保留了度序列和边权分布，破坏了空间嵌入（近处脑区更容易相连）、半球结构和模块结构。比较的量：聚集系数、无权与加权拉普拉斯的 $\mu_2$ 和特征值比、$\Lambda_{\max}$ 与阈值估计（10 个随机网络，报告中位数和范围，因为特征值比在个别随机网络中会因极小的 $\mu_2$ 变得很大），以及 $r(K)$ 曲线和与 FC 的相似度（其中 3 个随机网络）。

# %%
def rewire(A, W, seed):
    H = nx.from_numpy_array(A)
    nx.double_edge_swap(H, nswap=10 * H.number_of_edges(), max_tries=10**6, seed=seed)
    w = np.random.default_rng(seed).permutation(W[iu][A[iu] > 0])
    Wr = np.zeros_like(W)
    for (u, v), x in zip(H.edges(), w):
        Wr[u, v] = Wr[v, u] = x
    return Wr

nulls = [rewire(A, W, sd) for sd in range(10)]
stats = []
for Wr in nulls:
    m, _ = spectrum(Wr)
    Ab = (Wr > 0).astype(float)
    mb, _ = spectrum(Ab)
    stats.append((nx.average_clustering(nx.from_numpy_array(Ab)), mb[1], mb[-1] / mb[1], m[1], m[-1] / m[1],
                  np.linalg.eigvalsh(Wr).max()))
stats = np.array(stats)
cols = ("clustering", "mu_2(bin)", "ratio(bin)", "mu_2(w)", "ratio(w)", "Lambda_max")
print("%-18s" % "" + "".join("%12s" % c for c in cols))
print("%-18s" % "real" + "".join("%12.3f" % x for x in
      (nx.average_clustering(nx.from_numpy_array(A)), muA[1], muA[-1] / muA[1], mu[1], mu[-1] / mu[1], lam_max)))
print("%-18s" % "null median" + "".join("%12.3f" % x for x in np.median(stats, axis=0)))
print("%-18s" % "null min" + "".join("%12.3f" % x for x in stats.min(axis=0)))
print("%-18s" % "null max" + "".join("%12.3f" % x for x in stats.max(axis=0)))
print("零模型的阈值估计 K0/Lambda_max = %.3f ± %.3f" % ((K0 / stats[:, 5]).mean(), (K0 / stats[:, 5]).std()))
s_null = [Wr.sum(axis=1).min() for Wr in nulls]
print("最小节点强度：真实 %.3f，零模型 %.3f–%.3f（加权 mu_2 <= N/(N-1) * s_min）" % (s.min(), min(s_null), max(s_null)))

null_sweeps = [sweep(Wr, "null %d" % i) for i, Wr in enumerate(nulls[:3])]
null_r = np.mean([x["r"] for x in null_sweeps], axis=0)
null_meta = np.mean([x["meta"] for x in null_sweeps], axis=0)
null_fc = np.mean([x["fc_corr"] for x in null_sweeps], axis=0)
print("零模型平均：r =", np.round(null_r, 2).tolist())
print("零模型平均：corr(C, FC) =", np.round(null_fc, 3).tolist(), "；最大值 %.3f" % null_fc.max())

# %% [markdown]
# ## 6. 作图
#
# 左上：结构连接矩阵（按半球排序，对数色标）；右上：拉普拉斯谱，真实网络与一个保度随机化网络对比；左下：$r(K)$ 与亚稳态曲线，竖线为两种阈值估计；右下：在与 FC 最相似的 $K$ 下，模拟相位一致性与实测 FC 的散点（按半球内/半球间着色）。

# %%
fig, axes = plt.subplots(2, 2, figsize=(11, 9))
order = np.argsort(hemi, kind="stable")
ax = axes[0, 0]
Wl = np.where(W > 0, np.log10(W + 1e-12), np.nan)
im = ax.imshow(Wl[np.ix_(order, order)], cmap="magma")
nl = int((hemi == "lh").sum())
ax.axhline(nl - 0.5, c="c", lw=1); ax.axvline(nl - 0.5, c="c", lw=1)
ax.set_title("Structural connectivity (log10 weight), lh | rh"); fig.colorbar(im, ax=ax, shrink=0.8)

ax = axes[0, 1]
mr, _ = spectrum(nulls[0])
ax.plot(mu, "o", ms=3, label="real: mu_N/mu_2 = %.0f" % (mu[-1] / mu[1]))
ax.plot(mr, "s", ms=3, label="null: mu_N/mu_2 = %.0f" % (mr[-1] / mr[1]))
ax.set_xlabel("index"); ax.set_ylabel("Laplacian eigenvalue mu"); ax.set_yscale("symlog", linthresh=0.05)
ax.legend(); ax.set_title("Laplacian spectrum")

ax = axes[1, 0]
ax.plot(Ks, real["r"], "o-", label="r, real")
ax.plot(Ks, real["r_hemi"], "^-", label="r within hemisphere, real")
ax.plot(Ks, null_r, "s--", label="r, degree-preserving null")
ax2 = ax.twinx()
ax2.plot(Ks, real["meta"], "k:", label="std r(t), real")
ax2.plot(Ks, null_meta, ":", c="0.6", label="std r(t), null")
ax2.set_ylabel("metastability std r(t)")
ax.axvline(Kc_lam, c="C3", ls="--", lw=1); ax.axvline(Kc_hmf, c="C4", ls="--", lw=1)
ax.text(Kc_lam, 0.95, " K0/Lambda", color="C3", fontsize=8); ax.text(Kc_hmf, 0.85, " HMF", color="C4", fontsize=8)
ax.set_xlabel("coupling K"); ax.set_ylabel("order parameter r"); ax.set_ylim(0, 1)
h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, fontsize=7, loc="center right"); ax.set_title("Kuramoto on the connectome")

ax = axes[1, 1]
ax.scatter(Cb[iu][same_hemi], FC[iu][same_hemi], s=3, alpha=0.3, label="within hemisphere")
ax.scatter(Cb[iu][~same_hemi], FC[iu][~same_hemi], s=3, alpha=0.3, label="between hemispheres")
ax.set_xlabel("simulated phase coherence C_ij (K = %.2f)" % Ks[best]); ax.set_ylabel("empirical FC")
ax.set_title("corr = %.2f" % real["fc_corr"][best]); ax.legend(markerscale=4)
plt.tight_layout()
print("运行时间 %.1f 秒" % (time.time() - t0))

# %% [markdown]
# ## 7. 解读与局限
#
# **结果。**
#
# 1. **结构特征**。真实连接组的聚集系数约 0.57，是保度随机化网络（约 0.25）的两倍多；半球间的边只占约 22%（权重之和约 20%）。无权拉普拉斯的 $\mu_2$（约 2.53）低于随机网络（约 2.78–2.92），Fiedler 向量的符号与左右半球的划分有 86% 一致——最“便宜”的二分基本就是两个半球，这正是专题页所说“瓶颈压低 $\mu_2$”。
# 2. **加权谱要小心解读**。加权 $\mu_2$ 受最弱节点控制（$\mu_2\le\frac{N}{N-1}s_{\min}$）：零模型随机分配边权时，会让某些低度脑区只分到很弱的边，加权 $\mu_2$ 和特征值比因此在随机网络之间相差几个数量级。比较“哪个网络更易同步”时，结论会随用无权还是加权谱而变化，这与专题页“使用 $L$ 还是 $\mathcal L$、加权与否会改变排序，报告时须说明”的提醒一致。
# 3. **同步起点**。最大特征值近似给出 $K_c\approx0.70$，异质平均场给出约 1.10；模拟中 $r$ 在 $K\approx0.75$–1 开始明显高于随机相位基线 $1/\sqrt N\approx0.094$，更接近最大特征值近似。真实网络的 $\Lambda_{\max}$ 高于零模型（2.29 vs 约 1.68），预测的阈值更低，但模拟的 $r(K)$ 在 $K\le1.25$ 时两者几乎重合：阈值近似只描述线性化后的起点，有限网络上的差别被涨落掩盖。
# 4. **同步的路径**。越过起点后两类网络分道扬镳：$K=2$ 时零模型的 $r$ 约 0.54，真实网络只有约 0.39；$K=4$ 时分别约 0.86 和 0.65。高聚集、空间嵌入和半球瓶颈让真实连接组需要强得多的耦合才能全局锁定；同时它的亚稳态（$r(t)$ 的标准差）在 $K\approx1.25$–3 的宽范围内保持在 0.08–0.09，而零模型在 $K>1.5$ 后迅速下降。这与专题页“模块化维持分离与整合的平衡”的说法一致。
# 5. **与实测 FC 的比较**。模拟相位一致性与实测 FC 的相关在 $K=1$ 附近最高（约 0.21），即刚越过同步起点的中等耦合处；保度随机化网络上的模拟与 FC 几乎无关（约 0）。这说明 FC 的格局依赖具体的连接方式，而不只是度序列。但结构连接权重本身与 FC 的相关（约 0.29）比这个模型还高：一个无时滞、频率随机的 Kuramoto 模型并不比“直接看结构连接”解释得更多。专题页强调，“模型能重现 FC 不等于模型机制正确”，线性扩散一类更简单的模型往往也能解释相当一部分 FC。亚稳态最高的 $K$（约 2.5，但 1.25–3 之间几乎是平台）与 FC 拟合最好的 $K$ 并不重合，也说明“最佳工作点”取决于选哪个统计量。
#
# **局限。**
#
# - 结构连接由 DSI 确定性纤维追踪估计，无方向，并已知会低估长程（尤其是半球间）连接；组水平一致性网络掩盖了个体差异。
# - 模型没有传导时滞（数据中有纤维长度，可以按 $\tau_{ij}=\ell_{ij}/v$ 加入，是本案例的自然延伸）、没有噪声，也没有把相位转换为 BOLD 信号；$C_{ij}$ 与 fMRI 的相关系数不是同一个量，只能比较空间格局。
# - 固有频率取标准高斯分布只是演示假设；$K$ 的数值依赖“平均强度归一化为 1”这一约定，不能与其他文献的 $K$ 直接比较。
# - 实测 FC 来自拼接后的组水平时间序列，并经过显著性筛选；它本身的测量与预处理不确定性（专题页“全脑模型的局限”）没有在这里传播到结论中。
# - 每个 $K$ 只平均了 3 组频率、零模型只模拟了 3 个随机网络，曲线上相邻点的小幅起伏不应过度解读。
