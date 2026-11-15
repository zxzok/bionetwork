# 依赖：networkx>=3, numpy, scipy, matplotlib
# 数据：全部为 numpy / networkx 生成的模拟数据，仅用于演示方法。模拟的“节点”可以理解为脑区、基因或症状。
# 输入格式：示例 1、3 的输入是 N×N 相关矩阵（由“样本×节点”数据矩阵按列计算）；示例 2、6 的输入是一个无向图；
# 示例 4、5、7 的输入是“样本×节点”数据矩阵；示例 8 的输入是边列表文件（在临时目录中生成）。
# 真实分析中，可用自己的相关矩阵或网络替换各示例开头的模拟函数输出。

# %% 示例：阈值敏感性——枢纽排名随网络密度如何变化
# 用三因子模型模拟 80 个样本、50 个节点的数据，按比例阈值（保留绝对相关最强的前 d 比例的边）建网，
# 在密度 5%–40% 范围内取度最高的 5 个节点为“枢纽”，计算其与 10% 密度下枢纽集合的 Jaccard 相似度
# （交集大小 / 并集大小）。
# 解读：密度离参考值越远，枢纽集合通常变化越大；报告时应说明结论在哪个密度区间内成立。
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

def simulate_corr(n_samples=80, n_nodes=50, seed=15):
    """三因子模型生成的相关矩阵（模拟数据）。"""
    rng = np.random.default_rng(seed)
    F = rng.normal(size=(n_samples, 3))
    L = rng.uniform(0, 0.8, size=(n_nodes, 3)) * (rng.random((n_nodes, 3)) < 0.5)
    X = F @ L.T + rng.normal(size=(n_samples, n_nodes))
    return np.corrcoef(X.T)

def network_at_density(C, density):
    """保留绝对相关最强的前 density 比例的边（比例阈值法）。"""
    n = C.shape[0]
    iu = np.triu_indices(n, 1)
    keep = np.argsort(-np.abs(C[iu]))[:int(round(density * len(iu[0])))]
    G = nx.Graph(); G.add_nodes_from(range(n))
    G.add_edges_from(zip(iu[0][keep], iu[1][keep]))
    return G

def top_hubs(G, k=5):
    return set(sorted(G.nodes, key=lambda v: (-G.degree(v), v))[:k])

C = simulate_corr()
ref = top_hubs(network_at_density(C, 0.10))
print("10% 密度下的枢纽：", sorted(ref))
densities = np.arange(0.05, 0.41, 0.05)
jac = []
for d in densities:
    h = top_hubs(network_at_density(C, d))
    jac.append(len(h & ref) / len(h | ref))
    print(f"密度 {d:.2f}: 枢纽 {sorted(h)}，Jaccard = {jac[-1]:.2f}")

plt.figure(figsize=(5, 3))
plt.plot(densities, jac, "o-"); plt.axvline(0.10, color="gray", ls="--")
plt.xlabel("network density"); plt.ylabel("Jaccard vs. hubs at 10%"); plt.ylim(0, 1.05)
plt.tight_layout(); plt.show()

# %% 示例：随机种子敏感性——社团划分的可重复程度
# 在 4 个大小不等、边界较模糊的模拟社团网络上，用 20 个随机种子运行 Louvain，记录社团数和模块度 Q，
# 并计算每个划分与种子 0 划分的调整兰德指数（ARI；1 表示完全一致，约 0 表示与随机划分相当）。
# 解读：Q 的波动通常很小，但社团数和具体划分可能变化；报告时应给出多次运行的范围或共识划分。
import numpy as np
import networkx as nx

def ari(a, b):
    """调整兰德指数：两个标签数组的一致性。"""
    a = np.unique(a, return_inverse=True)[1]; b = np.unique(b, return_inverse=True)[1]
    M = np.zeros((a.max() + 1, b.max() + 1))
    np.add.at(M, (a, b), 1)
    c2 = lambda x: x * (x - 1) / 2
    s_ij, s_a, s_b, n2 = c2(M).sum(), c2(M.sum(1)).sum(), c2(M.sum(0)).sum(), c2(len(a))
    exp = s_a * s_b / n2
    return (s_ij - exp) / (0.5 * (s_a + s_b) - exp)

def labels_from(comms, n):
    lab = np.zeros(n, dtype=int)
    for i, c in enumerate(comms):
        lab[list(c)] = i
    return lab

G = nx.random_partition_graph([30, 25, 25, 20], 0.25, 0.04, seed=15)   # 模拟数据
n = G.number_of_nodes()
base = labels_from(nx.community.louvain_communities(G, seed=0), n)

res = []
for s in range(20):
    comms = nx.community.louvain_communities(G, seed=s)
    res.append((len(comms), nx.community.modularity(G, comms), ari(base, labels_from(comms, n))))
print(f"社团数范围 {min(r[0] for r in res)}–{max(r[0] for r in res)}；"
      f"Q 范围 {min(r[1] for r in res):.3f}–{max(r[1] for r in res):.3f}；"
      f"与种子 0 的 ARI 范围 {min(r[2] for r in res):.2f}–{max(r[2] for r in res):.2f}")

# 作图：种子 0 的划分（网络布局着色）；20 个种子的社团数与 ARI
import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 2, figsize=(10, 4))
pos = nx.spring_layout(G, seed=1)
nx.draw_networkx_edges(G, pos, ax=ax[0], edge_color="0.7", alpha=0.4, width=0.5)
nx.draw_networkx_nodes(G, pos, ax=ax[0], node_size=40, node_color=base, cmap="tab10", vmin=0, vmax=9)
ax[0].set_title("Louvain partition, seed 0", fontsize=10); ax[0].axis("off")
seeds = np.arange(20)
ax[1].plot(seeds, [r[2] for r in res], "o-", label="ARI vs seed 0")
ax[1].set_xlabel("random seed"); ax[1].set_ylabel("ARI"); ax[1].set_ylim(0, 1.05)
ax2 = ax[1].twinx()
ax2.plot(seeds, [r[0] for r in res], "s--", color="C1", label="number of communities")
ax2.set_ylabel("number of communities (orange)")
ax[1].set_title("Partitions vary across seeds while Q barely changes", fontsize=10)
plt.tight_layout(); plt.show()

# %% 示例：替代解释——组间差异来自“结构不同”还是“连接整体变弱”
# 模拟两组数据：潜在结构完全相同，只是 B 组测量噪声更大（类似头动或批次差异）。
# 先用固定阈值 |r| > 0.3 比较两组的密度和平均聚集系数，再改为两组都取相同密度（15%）比较。
# 解读：固定阈值下的大差异主要来自 B 组相关整体变弱、网络更稀疏；密度匹配消除了这一部分，
# 但噪声还会让“哪些边最强”的估计变得不准，使聚集系数仍然偏低。因此“B 组网络聚集性更低”
# 至少有两个替代解释（密度差异、测量质量差异），需要分别排查：例如扫描多个密度并报告曲线、
# 把测量质量指标（如头动）作为协变量，或在质量匹配的子样本中重复分析。
import numpy as np
import networkx as nx

def group_corr(noise, n_samples=80, n_nodes=50, seed=0):
    """两组共享同一潜在结构，只有噪声水平不同（模拟数据）。"""
    rng = np.random.default_rng(1000 + seed)
    struct = np.random.default_rng(15)                  # 两组共享同一潜在结构
    L = struct.uniform(0, 0.8, size=(n_nodes, 3)) * (struct.random((n_nodes, 3)) < 0.5)
    F = rng.normal(size=(n_samples, 3))
    X = F @ L.T + noise * rng.normal(size=(n_samples, n_nodes))
    return np.corrcoef(X.T)

def net_threshold(C, r):
    A = (np.abs(C) > r).astype(int); np.fill_diagonal(A, 0)
    return nx.from_numpy_array(A)

def net_density(C, density):
    n = C.shape[0]; iu = np.triu_indices(n, 1)
    keep = np.argsort(-np.abs(C[iu]))[:int(round(density * len(iu[0])))]
    G = nx.Graph(); G.add_nodes_from(range(n)); G.add_edges_from(zip(iu[0][keep], iu[1][keep]))
    return G

CA, CB = group_corr(noise=1.0, seed=1), group_corr(noise=1.6, seed=2)
for name, C in [("A 组（噪声小）", CA), ("B 组（噪声大）", CB)]:
    G1, G2 = net_threshold(C, 0.3), net_density(C, 0.15)
    print(f"{name}: 固定阈值 |r|>0.3 → 密度 {nx.density(G1):.3f}, 平均聚集系数 {nx.average_clustering(G1):.3f} | "
          f"密度匹配 15% → 密度 {nx.density(G2):.3f}, 平均聚集系数 {nx.average_clustering(G2):.3f}")

# 作图：两组 |r| 的分布与固定阈值；在一串密度上比较平均聚集系数
import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 2, figsize=(10, 4))
iu = np.triu_indices(CA.shape[0], 1)
ax[0].hist(np.abs(CA[iu]), bins=40, alpha=0.6, label="group A (low noise)")
ax[0].hist(np.abs(CB[iu]), bins=40, alpha=0.6, label="group B (high noise)")
ax[0].axvline(0.3, color="k", ls="--", label="fixed threshold |r| = 0.3")
ax[0].set_xlabel("|r|"); ax[0].set_ylabel("number of edges"); ax[0].legend(fontsize=8)
ax[0].set_title("A fixed threshold keeps far fewer edges in B", fontsize=10)
dens = np.arange(0.05, 0.41, 0.05)
for C, lab, mk in [(CA, "group A", "o"), (CB, "group B", "s")]:
    ax[1].plot(dens, [nx.average_clustering(net_density(C, d)) for d in dens], marker=mk, label=lab)
ax[1].axvline(0.15, color="gray", ls=":")
ax[1].set_xlabel("matched density"); ax[1].set_ylabel("average clustering"); ax[1].legend(fontsize=8)
ax[1].set_title("At matched density a smaller gap remains (noisier edges)", fontsize=10)
plt.tight_layout(); plt.show()

# %% 示例：多元宇宙分析——把所有合理的网络构建选择组合起来同时报告
# 模拟两组被试（各 60 人、30 个节点），B 组只在一个 6 节点子模块内的连接略强（真实差异很小）。
# 分析选择的组合（共 3×4×2 = 24 个“宇宙”）：边的统计量（Pearson、Spearman、偏相关）×
# 网络密度（10%、15%、20%、30%）× 指标（平均聚集系数、全局效率）。
# 每个宇宙用 200 次组标签置换计算 p 值，最后按效应量排序，打印“设定曲线”（specification curve）
# 并统计显著宇宙所占比例。
# 解读：结论在不同宇宙中的一致程度本身就是结果。在这组模拟数据中，效应的方向和显著性都随边的统计量、
# 密度和指标而变；若只挑其中显著的一个宇宙报告，就是挑选性报告。
# 置换检验要在“整条流水线”外层做：每次置换都重新计算相关、阈值化和指标。
import itertools
import numpy as np
import networkx as nx
from scipy.stats import rankdata

rng = np.random.default_rng(2026)
n_nodes, n_per_group = 30, 60

def simulate_group(n, boost, rng):
    """单因子背景 + 子模块 0–5 共享额外因子（强度 boost）。模拟数据。"""
    g = rng.normal(size=(n, 1)); m = rng.normal(size=(n, 1))
    X = 0.5 * g + rng.normal(size=(n, n_nodes))
    X[:, :6] += boost * m
    return X

XA = simulate_group(n_per_group, 0.5, rng)
XB = simulate_group(n_per_group, 0.8, rng)

def edge_matrix(X, kind):
    if kind == "pearson":
        return np.corrcoef(X.T)
    if kind == "spearman":
        return np.corrcoef(np.apply_along_axis(rankdata, 0, X).T)
    P = np.linalg.inv(np.cov(X.T))                       # 偏相关：由精度矩阵标准化得到
    d = np.sqrt(np.diag(P)); R = -P / np.outer(d, d); np.fill_diagonal(R, 1)
    return R

def graph_at_density(C, density):
    iu = np.triu_indices(C.shape[0], 1)
    keep = np.argsort(-np.abs(C[iu]))[:int(round(density * len(iu[0])))]
    G = nx.Graph(); G.add_nodes_from(range(C.shape[0])); G.add_edges_from(zip(iu[0][keep], iu[1][keep]))
    return G

metrics = {"clustering": nx.average_clustering, "efficiency": nx.global_efficiency}

def group_diff(XA, XB, kind, density, metric):
    f = metrics[metric]
    return f(graph_at_density(edge_matrix(XB, kind), density)) - f(graph_at_density(edge_matrix(XA, kind), density))

X_all = np.vstack([XA, XB]); n_perm = 200
results = []
for kind, dens, met in itertools.product(["pearson", "spearman", "partial"], [0.10, 0.15, 0.20, 0.30], metrics):
    obs = group_diff(XA, XB, kind, dens, met)
    null = []
    for _ in range(n_perm):
        idx = rng.permutation(len(X_all))
        null.append(group_diff(X_all[idx[:n_per_group]], X_all[idx[n_per_group:]], kind, dens, met))
    p = (1 + np.sum(np.abs(null) >= abs(obs))) / (n_perm + 1)
    results.append((obs, p, kind, dens, met))

results.sort(key=lambda r: r[0])
print("设定曲线（按效应量排序）：")
for obs, p, kind, dens, met in results:
    print(f"  {kind:8s} 密度 {dens:.2f} {met:10s} 差值 {obs:+.4f}  p = {p:.3f} {'*' if p < 0.05 else ''}")
sig = sum(r[1] < 0.05 for r in results)
print(f"显著宇宙：{sig}/{len(results)}；效应量中位数 {np.median([r[0] for r in results]):+.4f}；"
      f"效应为正的宇宙比例 {np.mean([r[0] > 0 for r in results]):.2f}")

# 作图：设定曲线（上：按效应量排序，实心 = p < 0.05；下：每个宇宙的分析选择）
import matplotlib.pyplot as plt
fig, ax = plt.subplots(2, 1, figsize=(10, 5), sharex=True, gridspec_kw={"height_ratios": [2, 1.4]})
x = np.arange(len(results))
for i, (obs, p, kind, dens, met) in enumerate(results):
    ax[0].plot(i, obs, "o", color="C3" if p < 0.05 else "0.5", mfc="C3" if p < 0.05 else "white")
ax[0].axhline(0, color="k", lw=0.8); ax[0].set_ylabel("group difference (B - A)")
ax[0].set_title(f"Specification curve: {sig}/{len(results)} universes significant (filled = p < 0.05)", fontsize=10)
rows = ["pearson", "spearman", "partial", "0.1", "0.15", "0.2", "0.3", "clustering", "efficiency"]
for i, (obs, p, kind, dens, met) in enumerate(results):
    for lab in (kind, f"{dens:g}", met):
        ax[1].plot(i, rows.index(lab), "s", color="0.2", ms=4)
ax[1].set_yticks(range(len(rows))); ax[1].set_yticklabels(["Pearson", "Spearman", "partial corr.", "density 0.10",
                                                           "density 0.15", "density 0.20", "density 0.30",
                                                           "clustering", "efficiency"], fontsize=7)
ax[1].invert_yaxis(); ax[1].set_xlabel("universe (sorted by effect size)")
plt.tight_layout(); plt.show()

# %% 示例：网络边检测的统计功效——Fisher z 近似与蒙特卡洛模拟
# 第一部分：用 Fisher z 变换近似计算“检出一条真实（偏）相关边”所需样本量，
#   n ≈ ((z_{1-α/2} + z_{1-β}) / artanh(ρ))² + 3 + k，k 为偏相关中被控制的变量数。
# 第二部分：模拟一个 15 节点、稀疏的真实偏相关网络，对不同样本量重复抽样，用偏相关的 Fisher z 检验
#   （Bonferroni 校正）判定边，统计灵敏度（检出真实边的比例）和假阳性边数。
# 解读：边越弱、节点越多（多重比较越严、控制变量越多），所需样本量越大；把功效分析写进分析计划。
import numpy as np
from scipy.stats import norm

def n_required(rho, alpha=0.05, power=0.80, k=0):
    za, zb = norm.ppf(1 - alpha / 2), norm.ppf(power)
    return int(np.ceil(((za + zb) / np.arctanh(rho)) ** 2 + 3 + k))

p = 15; m = p * (p - 1) // 2
for rho in [0.1, 0.2, 0.3]:
    print(f"ρ = {rho}: 单条边 α=0.05 需 n ≈ {n_required(rho)}；"
          f"{m} 条边 Bonferroni 且控制 {p-2} 个变量需 n ≈ {n_required(rho, alpha=0.05/m, k=p-2)}")

rng = np.random.default_rng(7)
# 构造稀疏精度矩阵：环状结构，偏相关约 0.2–0.3
K = np.eye(p)
for i in range(p):
    j = (i + 1) % p; K[i, j] = K[j, i] = -0.25
for i, j in [(0, 7), (3, 11)]:
    K[i, j] = K[j, i] = -0.2
Sigma = np.linalg.inv(K)
d = np.sqrt(np.diag(K)); true_pcor = -K / np.outer(d, d)
iu = np.triu_indices(p, 1); truth = np.abs(true_pcor[iu]) > 1e-8
print(f"真实边数 {truth.sum()}，真实偏相关范围 {np.abs(true_pcor[iu][truth]).min():.2f}–{np.abs(true_pcor[iu][truth]).max():.2f}")

crit = norm.ppf(1 - 0.05 / m / 2)
power_curve = []                                         # 保存模拟结果用于作图
for n in [100, 200, 400, 800, 1600]:
    sens, fp = [], []
    for _ in range(50):
        X = rng.multivariate_normal(np.zeros(p), Sigma, size=n)
        P = np.linalg.inv(np.cov(X.T)); dd = np.sqrt(np.diag(P))
        r = (-P / np.outer(dd, dd))[iu]
        z = np.arctanh(r) * np.sqrt(n - 3 - (p - 2))
        detected = np.abs(z) > crit
        sens.append(detected[truth].mean()); fp.append(detected[~truth].sum())
    print(f"n = {n:5d}: 灵敏度 {np.mean(sens):.2f}，平均假阳性边 {np.mean(fp):.2f}")
    power_curve.append((n, np.mean(sens), np.mean(fp)))

# 作图：解析的所需样本量曲线；模拟得到的灵敏度与假阳性边数随 n 的变化
import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 2, figsize=(10, 4))
rhos = np.linspace(0.08, 0.5, 40)
ax[0].plot(rhos, [n_required(r_) for r_ in rhos], "-", label="single edge, alpha = 0.05")
ax[0].plot(rhos, [n_required(r_, alpha=0.05 / m, k=p - 2) for r_ in rhos], "--",
           label=f"Bonferroni over {m} edges, partial corr.")
ax[0].set_yscale("log"); ax[0].set_xlabel("true (partial) correlation rho"); ax[0].set_ylabel("n for 80% power")
ax[0].set_title("Required sample size (Fisher z)", fontsize=10); ax[0].legend(fontsize=8)
pc = np.array(power_curve)
ax[1].plot(pc[:, 0], pc[:, 1], "o-", label="sensitivity")
ax[1].set_xscale("log"); ax[1].set_xlabel("sample size n"); ax[1].set_ylabel("sensitivity"); ax[1].set_ylim(0, 1.05)
ax2 = ax[1].twinx(); ax2.plot(pc[:, 0], pc[:, 2], "s--", color="C1"); ax2.set_ylabel("false-positive edges (orange)")
ax[1].set_title("Simulated edge detection, 15-node network", fontsize=10)
plt.tight_layout(); plt.show()

# %% 示例：随机种子与蒙特卡洛误差——零模型 z 分数和置换 p 值本身也是估计量
# 对一个模拟网络，用度保持随机化（双边交换）估计平均聚集系数的 z 分数与单侧经验 p 值；
# 比较随机网络数 B = 19 与 B = 199 时，8 个不同种子给出的结果离散程度。
# 经验 p 值用 (1 + #{null ≥ obs}) / (B + 1)（Phipson & Smyth 2010），因此最小可达 1/(B+1)：
# B = 19 时 p 不可能小于 0.05。p 的蒙特卡洛标准误约为 sqrt(p(1-p)/B)。
# 解读：B 太小时，z 分数随种子明显波动，p 值受分辨率限制；应预先确定足够大的 B，
# 报告 B 和种子，并检查结论在多个种子下是否一致，而不是换种子直到显著。
import numpy as np
import networkx as nx

G = nx.powerlaw_cluster_graph(150, 3, 0.15, seed=42)          # 模拟网络
obs = nx.average_clustering(G)
print(f"观测平均聚集系数 C = {obs:.4f}")

def null_stats(G, B, seed):
    rng = np.random.default_rng(seed); vals = []
    for _ in range(B):
        H = G.copy()
        nx.double_edge_swap(H, nswap=2 * H.number_of_edges(), max_tries=10**6,
                            seed=int(rng.integers(2**31)))
        vals.append(nx.average_clustering(H))
    return np.array(vals)

mc = {}                                                  # 保存各 B 下的 z 与 p 用于作图
for B in [19, 199]:
    zs, ps = [], []
    for seed in range(8):
        null = null_stats(G, B, seed)
        zs.append((obs - null.mean()) / null.std(ddof=1))
        ps.append((1 + np.sum(null >= obs)) / (B + 1))
    print(f"B = {B:3d}: 8 个种子的 z 分数范围 {min(zs):.1f}–{max(zs):.1f}；"
          f"经验 p 值范围 {min(ps):.3f}–{max(ps):.3f}（最小可达 {1/(B+1):.3f}）")
    mc[B] = (zs, ps)
p_hat = 0.04
for B in [20, 100, 1000, 10000]:
    print(f"若真实 p ≈ {p_hat}，B = {B:5d} 时蒙特卡洛标准误 ≈ {np.sqrt(p_hat * (1 - p_hat) / B):.4f}")

# 作图：8 个种子下的 z 分数与经验 p 值（B = 19 vs 199）
import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 2, figsize=(10, 4))
for j, (B, mk) in enumerate([(19, "o"), (199, "s")]):
    zs, ps = mc[B]
    ax[0].plot(np.full(8, j) + np.linspace(-0.12, 0.12, 8), zs, mk, label=f"B = {B}")
    ax[1].plot(np.full(8, j) + np.linspace(-0.12, 0.12, 8), ps, mk)
    ax[1].hlines(1 / (B + 1), j - 0.3, j + 0.3, color="C3", ls="--")
for a, yl in zip(ax, ["z-score of clustering", "empirical p-value"]):
    a.set_xticks([0, 1]); a.set_xticklabels(["B = 19", "B = 199"]); a.set_xlim(-0.6, 1.6); a.set_ylabel(yl)
ax[0].set_title("z-score varies with the seed (8 seeds per B)", fontsize=10)
ax[1].set_yscale("log"); ax[1].set_title("p cannot go below 1/(B+1) (dashed)", fontsize=10)
plt.tight_layout(); plt.show()

# %% 示例：循环论证（double dipping）——用同一份数据选边又检验边
# 两组被试的数据来自同一分布（不存在任何真实组间差异）。
# 错误做法：在全部数据上找出组间差异最大的 10 条边，再在同一数据上检验这 10 条边的组间差异。
# 正确做法：在一半被试上选边，在另一半独立被试上检验。重复 200 次，统计“检出差异”的比例。
# 解读：循环分析在纯噪声中也几乎总是“显著”；选择和检验必须用独立数据（或把选择步骤放进置换检验）。
import numpy as np
from scipy.stats import ttest_ind

rng = np.random.default_rng(11)
n_per, p = 40, 20
iu = np.triu_indices(p, 1)

def subject_edges(n):
    """每个被试 60 个时间点的相关矩阵上三角，作为该被试的“连接向量”（模拟数据）。"""
    out = []
    for _ in range(n):
        X = rng.normal(size=(60, p))
        out.append(np.arctanh(np.corrcoef(X.T)[iu]))
    return np.array(out)

circ, split = 0, 0
for _ in range(200):
    A, B = subject_edges(n_per), subject_edges(n_per)
    t_all = ttest_ind(A, B).statistic
    top = np.argsort(-np.abs(t_all))[:10]; s = np.sign(t_all[top])          # 按差异方向对齐后取平均
    circ += ttest_ind((A[:, top] * s).mean(1), (B[:, top] * s).mean(1)).pvalue < 0.05
    h = n_per // 2
    t_half = ttest_ind(A[:h], B[:h]).statistic
    top = np.argsort(-np.abs(t_half))[:10]; s = np.sign(t_half[top])
    split += ttest_ind((A[h:, top] * s).mean(1), (B[h:, top] * s).mean(1)).pvalue < 0.05
print(f"纯噪声数据中“显著”比例：循环分析 {circ / 200:.2f}；独立分半 {split / 200:.2f}（名义水平 0.05）")

# 作图：纯噪声下两种做法的假阳性率（200 次重复，误差线为二项标准误）
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(6.4, 4.2))
rates = np.array([circ, split]) / 200
ax.bar(["circular (select & test\non same data)", "independent split"], rates,
       yerr=np.sqrt(rates * (1 - rates) / 200), color=["C3", "C0"], capsize=4)
ax.axhline(0.05, color="k", ls="--", label="nominal alpha = 0.05")
ax.set_ylabel("false-positive rate"); ax.set_ylim(0, 1.05); ax.legend()
ax.set_title("Double dipping finds 'effects' in pure noise", fontsize=10)
plt.tight_layout(); plt.show()

# %% 示例：运行清单（provenance manifest）——记录环境、参数、种子与输入输出的哈希
# 把一次网络分析需要复算的信息写进 JSON：Python 与关键包版本、平台、参数、随机种子、
# 输入文件与输出结果的 SHA-256。然后用同样的设置重跑一次，比较输出哈希是否一致。
# 解读：哈希一致说明在同一环境下可复算；换机器或升级包后若哈希改变，可据清单逐项排查。
# 浮点运算在不同平台或并行设置下可能有末位差异，此时应比较数值容差而非字节哈希。
import hashlib, json, platform, sys, tempfile
from pathlib import Path
import numpy as np
import networkx as nx
import scipy

def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def run_analysis(edge_file, out_file, seed, resolution):
    G = nx.read_edgelist(edge_file, nodetype=int)
    comms = nx.community.louvain_communities(G, seed=seed, resolution=resolution)
    Q = nx.community.modularity(G, comms)
    labels = {v: i for i, c in enumerate(sorted(comms, key=min)) for v in c}
    Path(out_file).write_text(json.dumps({"Q": round(Q, 10), "labels": [labels[v] for v in sorted(G)]}))
    return Q

workdir = Path(tempfile.mkdtemp())
edge_file = workdir / "network.edgelist"                      # 模拟的“原始数据”
nx.write_edgelist(nx.random_partition_graph([20, 20, 20], 0.3, 0.03, seed=5), edge_file, data=False)

params = {"algorithm": "louvain", "resolution": 1.0, "seed": 20261115}
hashes = []
for run in range(2):
    out = workdir / f"result_run{run}.json"
    Q = run_analysis(edge_file, out, params["seed"], params["resolution"])
    hashes.append(sha256(out))

manifest = {
    "python": sys.version.split()[0], "platform": platform.platform(),
    "packages": {"networkx": nx.__version__, "numpy": np.__version__, "scipy": scipy.__version__},
    "parameters": params,
    "inputs": {edge_file.name: sha256(edge_file)},
    "outputs": {"result_run0.json": hashes[0]},
    "modularity_Q": round(Q, 4),
}
(workdir / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
print(json.dumps(manifest, indent=2, ensure_ascii=False))
print("两次运行输出哈希一致：", hashes[0] == hashes[1])
