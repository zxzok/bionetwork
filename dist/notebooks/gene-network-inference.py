# 依赖：numpy, scipy, matplotlib
# 数据：全部为程序生成的模拟表达数据，仅用于演示方法，不代表任何真实基因或疾病。
#   表达矩阵 X 为“样本 × 基因”（行 = 样本，列 = 基因），与 WGCNA 的输入格式一致。
#   模拟设定：60 个样本、120 个“基因”；其中 4 个共表达模块（30/25/20/15 个基因）分别由 4 个潜在因子驱动，
#   另有 30 个纯噪声基因（标签 0）。模块 1 的潜在因子与一个“临床性状”相关。
#   每个基因的“载荷”越大，它越接近所在模块的潜在因子（噪声越小）。
#   真实数据应先完成质控、标准化、批次与离群样本检查，再按同样步骤分析。
#   前三个单元共用上述模拟设定；其后的单元（互信息与 CLR/ARACNe、收缩偏相关、回归与先验整合、差异共表达、
#   模块保守性、评估指标）各自在单元内生成带已知真实网络的模拟数据，便于计算 AUROC/AUPR。

# %% 示例：软阈值幂次 β 的无标度拟合准则
# 对 β = 1..12 构建无符号软阈值邻接矩阵 A = |r|^β，计算连接度 k_i = Σ_j a_ij（不含自身），
# 把 k 分 10 个箱，拟合 log10 p(k) ~ log10 k，拟合指数 = −sign(斜率)·R²；选拟合指数首次 ≥ 0.85 的最小 β。
# 输出解读：β 增大时拟合指数先快速上升、随后在高位波动，平均连接度单调下降。
# 拟合指数只是选 β 的经验准则，不是对网络无标度性的检验。
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

def simulate(seed=13):
    """模拟表达矩阵 X（样本 x 基因）、真实模块标签、真实载荷、临床性状。"""
    rng = np.random.default_rng(seed)
    n, sizes = 60, [30, 25, 20, 15]
    trait = rng.normal(size=n)
    factors = [0.8 * trait + 0.6 * rng.normal(size=n)] + [rng.normal(size=n) for _ in sizes[1:]]
    X, labels, load = [], [], []
    for m, (s, f) in enumerate(zip(sizes, factors)):
        for l in rng.uniform(0.5, 0.95, size=s):          # 载荷越大，越像模块“核心”
            X.append(l * f + np.sqrt(1 - l**2) * rng.normal(size=n))
            labels.append(m + 1); load.append(l)
    for _ in range(30):                                     # 噪声基因，标签 0
        X.append(rng.normal(size=n)); labels.append(0); load.append(0.0)
    return np.array(X).T, np.array(labels), np.array(load), trait

def scale_free_fit(A, nbins=10):
    """返回 (无标度拟合指数, 平均连接度)。A 的对角线为 1，计算连接度时减去。"""
    k = A.sum(axis=1) - 1.0
    cnt, edges = np.histogram(k, bins=nbins)
    mid = (edges[:-1] + edges[1:]) / 2
    ok = cnt > 0
    res = stats.linregress(np.log10(mid[ok]), np.log10(cnt[ok] / cnt.sum()))
    return -np.sign(res.slope) * res.rvalue**2, k.mean()

X, true_lab, true_load, trait = simulate()
R = np.corrcoef(X.T)                                        # 基因 x 基因相关矩阵

betas = list(range(1, 13))
res = [scale_free_fit(np.abs(R) ** b) for b in betas]
fits = [r[0] for r in res]; mean_k = [r[1] for r in res]
for b, f, mk in zip(betas, fits, mean_k):
    print(f"beta = {b:2d}：拟合指数 = {f:5.2f}，平均连接度 = {mk:6.2f}")
beta_star = next(b for b, f in zip(betas, fits) if f >= 0.85)
print("选定 beta =", beta_star)

fig, ax = plt.subplots(1, 2, figsize=(9, 3.5))
ax[0].plot(betas, fits, "o-"); ax[0].axhline(0.85, color="r", ls="--")
ax[0].set_xlabel("beta"); ax[0].set_ylabel("scale-free fit index")
ax[1].plot(betas, mean_k, "o-"); ax[1].set_xlabel("beta"); ax[1].set_ylabel("mean connectivity")
plt.tight_layout(); plt.show()

# %% 示例：拓扑重叠矩阵（TOM）与层次聚类划分模块
# 用无标度拟合准则选出的 β 构建邻接矩阵，计算 TOM_ij = (l_ij + a_ij) / (min(k_i, k_j) + 1 − a_ij)，l = A·A；
# 以 1 − TOM 为距离做平均连锁层次聚类，在高度 0.93 处切树，少于 10 个基因的小簇记为 0
# （相当于 WGCNA 中未归类的灰色基因），再与真实模块标签做列联表。
# 输出解读：4 个真实模块基本被完整找回，噪声基因大多落在 0 类；热图中模块沿对角线呈块状。
# 切树高度与最小模块大小会改变结果（例如改成 0.98 与 5），真实分析中应报告这些参数并检验稳定性。
import numpy as np
from scipy import stats
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import squareform
import matplotlib.pyplot as plt

def simulate(seed=13):
    rng = np.random.default_rng(seed)
    n, sizes = 60, [30, 25, 20, 15]
    trait = rng.normal(size=n)
    factors = [0.8 * trait + 0.6 * rng.normal(size=n)] + [rng.normal(size=n) for _ in sizes[1:]]
    X, labels, load = [], [], []
    for m, (s, f) in enumerate(zip(sizes, factors)):
        for l in rng.uniform(0.5, 0.95, size=s):
            X.append(l * f + np.sqrt(1 - l**2) * rng.normal(size=n))
            labels.append(m + 1); load.append(l)
    for _ in range(30):
        X.append(rng.normal(size=n)); labels.append(0); load.append(0.0)
    return np.array(X).T, np.array(labels), np.array(load), trait

def scale_free_fit(A, nbins=10):
    k = A.sum(axis=1) - 1.0
    cnt, edges = np.histogram(k, bins=nbins)
    mid = (edges[:-1] + edges[1:]) / 2
    ok = cnt > 0
    res = stats.linregress(np.log10(mid[ok]), np.log10(cnt[ok] / cnt.sum()))
    return -np.sign(res.slope) * res.rvalue**2

def tom(A):
    """TOM_ij = (l_ij + a_ij) / (min(k_i, k_j) + 1 − a_ij)，l = A @ A；A 的对角线须为 0。"""
    k = A.sum(axis=1)
    T = (A @ A + A) / (np.minimum.outer(k, k) + 1 - A)
    np.fill_diagonal(T, 1.0)
    return T

def cut_modules(Z, height=0.93, min_size=10):
    """按高度切树；小于 min_size 的簇记为 0；其余按大小从大到小编号 1, 2, ..."""
    c = fcluster(Z, t=height, criterion="distance")
    ids, counts = np.unique(c, return_counts=True)
    big = [i for i, n in sorted(zip(ids, counts), key=lambda x: -x[1]) if n >= min_size]
    return np.array([big.index(x) + 1 if x in big else 0 for x in c])

X, true_lab, true_load, trait = simulate()
R = np.corrcoef(X.T)
beta = next(b for b in range(1, 13) if scale_free_fit(np.abs(R) ** b) >= 0.85)
A = np.abs(R) ** beta
np.fill_diagonal(A, 0.0)

T = tom(A)
dist = 1.0 - T
np.fill_diagonal(dist, 0.0)
Z = linkage(squareform(dist, checks=False), method="average")
clusters = cut_modules(Z)
K = clusters.max()
print(f"beta = {beta}；找到 {K} 个模块；列联表（行 = 真实标签 0..4，列 = 聚类 0..{K}，0 为未归类）：")
for t in range(5):
    print(t, [int(np.sum((true_lab == t) & (clusters == c))) for c in range(K + 1)])

order = np.argsort(clusters, kind="stable")
plt.figure(figsize=(4.5, 4))
plt.imshow(T[np.ix_(order, order)], cmap="magma", vmax=np.percentile(T, 99))
plt.title("TOM ordered by module"); plt.colorbar(); plt.show()

# %% 示例：模块特征基因、模块–性状关联与 hub 基因
# 对每个模块计算特征基因 ME（标准化表达的第一主成分，符号与模块平均表达一致）及其解释的方差比例，
# 计算 ME 与临床性状的相关；再计算模块成员度 kME = cor(基因表达, ME)，取 kME 最高的 3 个基因作为 hub。
# 为突出这一步，这里直接使用真实模块标签；实际分析中用 TOM 聚类得到的模块。
# 输出解读：模块 1 的 ME 与性状显著相关；hub 基因的真实载荷明显高于模块平均。
# 在本模拟中，模块 1 的所有基因都只是同一个潜在因子的“读数”，hub 只是噪声最小的读数——
# 这正是“hub 适合作标志物、不等于驱动者”的含义。
import numpy as np
from scipy import stats

def simulate(seed=13):
    rng = np.random.default_rng(seed)
    n, sizes = 60, [30, 25, 20, 15]
    trait = rng.normal(size=n)
    factors = [0.8 * trait + 0.6 * rng.normal(size=n)] + [rng.normal(size=n) for _ in sizes[1:]]
    X, labels, load = [], [], []
    for m, (s, f) in enumerate(zip(sizes, factors)):
        for l in rng.uniform(0.5, 0.95, size=s):
            X.append(l * f + np.sqrt(1 - l**2) * rng.normal(size=n))
            labels.append(m + 1); load.append(l)
    for _ in range(30):
        X.append(rng.normal(size=n)); labels.append(0); load.append(0.0)
    return np.array(X).T, np.array(labels), np.array(load), trait

def eigengene(Xm):
    """Xm：样本 x 模块基因（已标准化）。返回 (第一主成分得分, 解释的方差比例)，得分符号与模块平均表达一致。"""
    U, S, Vt = np.linalg.svd(Xm, full_matrices=False)
    me = U[:, 0] * S[0]
    if np.corrcoef(me, Xm.mean(axis=1))[0, 1] < 0:
        me = -me
    return me, S[0]**2 / np.sum(S**2)

X, true_lab, true_load, trait = simulate()
Xz = (X - X.mean(0)) / X.std(0)                              # 每个基因标准化

r_trait, kme_by_mod = [], {}
for m in range(1, 5):
    idx = np.where(true_lab == m)[0]
    me, ve = eigengene(Xz[:, idx])
    r, p = stats.pearsonr(me, trait)
    kme = np.array([np.corrcoef(Xz[:, g], me)[0, 1] for g in idx])
    top = idx[np.argsort(-kme)[:3]]
    print(f"模块{m}: ME 解释方差 = {ve:.2f}，ME–性状 r = {r:.2f}, p = {p:.1e}; hub = {top.tolist()}, "
          f"hub 真实载荷 = {np.round(true_load[top], 2).tolist()}, 模块平均载荷 = {true_load[idx].mean():.2f}")
    r_trait.append(r); kme_by_mod[m] = (idx, kme, top)

import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 2, figsize=(10, 4))
ax[0].bar([f"M{m}" for m in range(1, 5)], r_trait, color=["C3"] + ["0.6"] * 3)
ax[0].axhline(0, color="k", lw=0.8); ax[0].set_ylabel("cor(module eigengene, trait)")
ax[0].set_title("Module–trait association")
idx, kme, top = kme_by_mod[1]
ax[1].scatter(true_load[idx], kme, s=40, color="0.5", label="module 1 genes")
ax[1].scatter(true_load[top], kme[np.isin(idx, top)], s=90, color="C3", label="top-3 hubs (kME)")
ax[1].set_xlabel("true loading on latent factor"); ax[1].set_ylabel("module membership kME")
ax[1].set_title("Hubs = least noisy read-outs of the factor"); ax[1].legend()
plt.tight_layout(); plt.show()

# %% 示例：互信息网络、CLR 背景校正与 ARACNe 的数据处理不等式
# 在一个已知的有向无环调控网络（30 个基因，含线性、饱和与非单调 U 形调控）上生成 400 个稳态样本，
# 分别用 |皮尔逊相关|、互信息（等频分箱的插入估计）、CLR 与 ARACNe（DPI，容差 0）给所有基因对打分，
# 以真实的“父–子”对为金标准（无向），计算 AUROC、AUPR、早期精度比 EPR 与随机基线。
# 输出解读：U 形调控使相关几乎为 0，互信息仍能发现；CLR 与 DPI 去除部分间接边，早期精度通常提高。
# 结果依赖模拟设定、分箱数与样本量；不要把这里的排名推广到真实数据。
import numpy as np

def simulate_dag(p=30, n=400, seed=1):
    rng = np.random.default_rng(seed)
    X = np.zeros((n, p)); edges = set(); kinds = {}
    X[:, :4] = rng.normal(size=(n, 4))                      # 4 个根节点（上游调控因子）
    for j in range(4, p):
        parents = rng.choice(j, size=rng.integers(1, 3), replace=False)
        signal = np.zeros(n)
        for k in parents:
            kind = rng.choice(["linear", "saturating", "u-shape"], p=[0.4, 0.4, 0.2])
            z = (X[:, k] - X[:, k].mean()) / X[:, k].std()
            signal += {"linear": z, "saturating": 2 * np.tanh(1.5 * z), "u-shape": z**2 - 1}[kind]
            edges.add((min(j, k), max(j, k))); kinds[(min(j, k), max(j, k))] = kind
        X[:, j] = signal + 0.7 * signal.std() * rng.normal(size=n)
    return X, edges, kinds

def mutual_information(X, bins=8):
    """等频分箱后的插入（plug-in）互信息估计，单位 nat。"""
    n, p = X.shape
    D = np.argsort(np.argsort(X, axis=0), axis=0) * bins // n   # 每列按秩切成 bins 个等频箱
    M = np.zeros((p, p))
    for i in range(p):
        for j in range(i + 1, p):
            joint = np.zeros((bins, bins)); np.add.at(joint, (D[:, i], D[:, j]), 1); joint /= n
            pi, pj = joint.sum(1), joint.sum(0); nz = joint > 0
            M[i, j] = M[j, i] = np.sum(joint[nz] * np.log(joint[nz] / np.outer(pi, pj)[nz]))
    return M

def clr(M):
    """CLR：每个 MI 相对于两个基因各自 MI 背景分布的 z 分数，负值截为 0，合并为 sqrt(zi^2 + zj^2)。"""
    p = M.shape[0]; off = ~np.eye(p, dtype=bool)
    mu = np.array([M[i, off[i]].mean() for i in range(p)]); sd = np.array([M[i, off[i]].std() for i in range(p)])
    Z = np.maximum(0, (M - mu[:, None]) / sd[:, None])
    S = np.sqrt(Z**2 + Z.T**2); np.fill_diagonal(S, 0); return S

def aracne_dpi(M, eps=0.0):
    """对每个三角形，若某边 MI 小于另两边的最小值（乘 1−eps），标记删除；最后一次性删除。"""
    p = M.shape[0]; keep = M.copy(); drop = np.zeros_like(M, dtype=bool)
    for i in range(p):
        for j in range(i + 1, p):
            for k in range(p):
                if k != i and k != j and M[i, j] < (1 - eps) * min(M[i, k], M[j, k]):
                    drop[i, j] = drop[j, i] = True; break
    keep[drop] = 0; return keep

def evaluate(S, gold, p):
    """S：对称打分矩阵；gold：真边集合 (i<j)。返回 AUROC、AUPR、随机 AUPR、早期精度比 EPR。"""
    iu = np.triu_indices(p, 1); score = S[iu]
    y = np.array([(i, j) in gold for i, j in zip(*iu)])
    order = np.argsort(-score, kind="stable"); ys = y[order]
    tp = np.cumsum(ys); prec = tp / np.arange(1, len(ys) + 1)
    aupr = np.sum(prec[ys]) / ys.sum()                      # 平均精确率：不做线性插值
    ranks = np.argsort(np.argsort(score)) + 1               # 秩和法计算 AUROC（并列忽略）
    auroc = (ranks[y].sum() - y.sum() * (y.sum() + 1) / 2) / (y.sum() * (~y).sum())
    k = y.sum(); base = y.mean()
    return auroc, aupr, base, (tp[k - 1] / k) / base

X, gold, kinds = simulate_dag()
p = X.shape[1]
R = np.abs(np.corrcoef(X.T)); np.fill_diagonal(R, 0)
MI = mutual_information(X)
print(f"真边 {len(gold)} 条 / 候选 {p*(p-1)//2} 条；其中 U 形调控 {sum(v=='u-shape' for v in kinds.values())} 条")
methods = [("|Pearson r|", R), ("互信息 MI", MI), ("CLR", clr(MI)), ("ARACNe(DPI)", aracne_dpi(MI))]
for name, S in methods:
    auroc, aupr, base, epr = evaluate(S, gold, p)
    print(f"{name:12s} AUROC = {auroc:.3f}  AUPR = {aupr:.3f}（随机 {base:.3f}，比值 {aupr/base:4.1f}）  EPR = {epr:4.1f}")
u = [e for e, v in kinds.items() if v == "u-shape"]
print("U 形调控边上的平均 |r| =", np.round(np.mean([R[e] for e in u]), 3), "；平均 MI =", np.round(np.mean([MI[e] for e in u]), 3),
      "；全部候选对的平均 MI =", np.round(MI[np.triu_indices(p, 1)].mean(), 3))

import matplotlib.pyplot as plt
iu = np.triu_indices(p, 1); y = np.array([(i, j) in gold for i, j in zip(*iu)])
fig, ax = plt.subplots(figsize=(6.4, 4.2))
for (name, S), lab, ls in zip(methods, ["|Pearson r|", "MI", "CLR", "ARACNe (DPI)"], ["-", "--", "-.", ":"]):
    ys = y[np.argsort(-S[iu], kind="stable")]; tp = np.cumsum(ys)
    ax.plot(tp / ys.sum(), tp / np.arange(1, len(ys) + 1), ls, lw=2,
            label=f"{lab} (AUPR = {evaluate(S, gold, p)[1]:.2f})")
ax.axhline(y.mean(), color="0.6", lw=0.8, label="random")
ax.set_xlabel("recall"); ax.set_ylabel("precision"); ax.set_ylim(0, 1.02)
ax.set_title("Precision–recall against the true regulatory edges"); ax.legend()
plt.tight_layout(); plt.show()

# %% 示例：Schäfer–Strimmer 收缩估计偏相关（p > n）
# 从一个已知的稀疏高斯图模型（80 个基因：8 个枢纽各连 6 个邻居，另加少量随机边）抽取 n 个样本。
# n ≤ p 时样本协方差不可逆，普通偏相关无法计算。按 Schäfer & Strimmer（2005）的解析公式估计收缩强度 λ*，
# 把相关矩阵向单位阵收缩 R* = λ*·I + (1−λ*)·R，再求逆得到偏相关；与 |相关| 比较恢复真实边的 AUPR。
# 输出解读：λ* 随样本量增大而减小。同一枢纽的两个邻居之间没有直接边，却有明显相关；偏相关把这类间接对压到接近 0。
# 但 n 很小时偏相关估计噪声大、且收缩很强，AUPR 不一定高于相关排序；n 增大后偏相关继续改进，相关排序则停在间接边造成的上限附近。
# 本示例只演示点估计；GeneNet 还用局部 fdr 判断哪些偏相关显著，这里未实现。
import numpy as np

def sparse_ggm(p=80, seed=7):
    rng = np.random.default_rng(seed)
    K = np.eye(p)
    for h in range(0, p, 10):                               # 枢纽 0, 10, 20, ...，各连 6 个邻居
        for j in range(h + 1, h + 7):
            K[h, j] = K[j, h] = -0.4
    for _ in range(15):
        i, j = rng.choice(p, 2, replace=False); K[i, j] = K[j, i] = 0.2
    K += (abs(np.linalg.eigvalsh(K).min()) + 0.2) * np.eye(p)   # 保证正定
    gold = {(i, j) for i in range(p) for j in range(i + 1, p) if K[i, j] != 0}
    return np.linalg.inv(K), gold

def shrinkage_lambda(X):
    """Schäfer–Strimmer “目标 D”：相关矩阵向单位阵收缩的最优强度 λ*。返回 (λ*, 样本相关矩阵)。"""
    n = X.shape[0]
    Z = (X - X.mean(0)) / X.std(0, ddof=1)
    W = Z[:, :, None] * Z[:, None, :]                       # w_kij = z_ki z_kj
    R = W.sum(0) / (n - 1)
    var_r = n / (n - 1) ** 3 * ((W - W.mean(0)) ** 2).sum(0)
    off = ~np.eye(X.shape[1], dtype=bool)
    return float(np.clip(var_r[off].sum() / (R[off] ** 2).sum(), 0, 1)), R

def pcor_from_corr(R):
    O = np.linalg.inv(R); d = np.sqrt(np.diag(O))
    P = -O / np.outer(d, d); np.fill_diagonal(P, 0); return P

def aupr(S, gold, p):
    iu = np.triu_indices(p, 1); y = np.array([(i, j) in gold for i, j in zip(*iu)])
    ys = y[np.argsort(-np.abs(S[iu]), kind="stable")]
    return np.sum((np.cumsum(ys) / np.arange(1, len(ys) + 1))[ys]) / ys.sum(), y.mean()

Sigma, gold = sparse_ggm()
p = Sigma.shape[0]
rng = np.random.default_rng(3)
ns, curve = [40, 100, 400, 1600], []
for n in ns:
    X = rng.multivariate_normal(np.zeros(p), Sigma, size=n)
    lam, R = shrinkage_lambda(X)
    P = pcor_from_corr(lam * np.eye(p) + (1 - lam) * R)
    Rc = R.copy(); np.fill_diagonal(Rc, 0)
    a_r, base = aupr(Rc, gold, p); a_p, _ = aupr(P, gold, p)
    note = "样本协方差奇异" if n <= p else "样本协方差可逆"
    print(f"n = {n:4d}（{note}）：λ* = {lam:.2f}；AUPR |相关| = {a_r:.3f}，AUPR 收缩偏相关 = {a_p:.3f}（随机 {base:.3f}）")
    curve.append((lam, a_r, a_p))
# 间接对：同一枢纽的两个邻居（且不是真边）
X = rng.multivariate_normal(np.zeros(p), Sigma, size=400); lam, R = shrinkage_lambda(X)
P = pcor_from_corr(lam * np.eye(p) + (1 - lam) * R)
ind = [(a, b) for h in range(0, p, 10) for a in range(h + 1, h + 7) for b in range(a + 1, h + 7) if (a, b) not in gold]
dirs = sorted(gold)
print(f"n = 400：间接对平均 |r| = {np.mean([abs(R[e]) for e in ind]):.3f}，平均 |偏相关| = {np.mean([abs(P[e]) for e in ind]):.3f}；"
      f"真边平均 |r| = {np.mean([abs(R[e]) for e in dirs]):.3f}，平均 |偏相关| = {np.mean([abs(P[e]) for e in dirs]):.3f}")

import matplotlib.pyplot as plt
lam_, a_r_, a_p_ = np.array(curve).T
fig, ax = plt.subplots(1, 2, figsize=(10, 4))
ax[0].plot(ns, a_r_, "s--", label="|correlation|"); ax[0].plot(ns, a_p_, "o-", label="shrinkage partial correlation")
ax[0].plot(ns, lam_, "^:", color="0.4", label="shrinkage intensity λ*")
ax[0].axvline(p, color="0.7", lw=0.8); ax[0].set_xscale("log")
ax[0].set_xlabel("sample size n (vertical line: n = p)"); ax[0].set_ylabel("AUPR  /  λ*")
ax[0].set_title("Edge recovery vs sample size"); ax[0].legend(fontsize=8)
for pairs, lab, mk in [(ind, "indirect pairs (shared hub)", "o"), (dirs, "true edges", "s")]:
    ax[1].scatter([abs(R[e]) for e in pairs], [abs(P[e]) for e in pairs], s=30, marker=mk, alpha=0.7, label=lab)
ax[1].set_xlabel("|correlation|  (n = 400)"); ax[1].set_ylabel("|partial correlation|")
ax[1].set_title("Partial correlation removes indirect pairs"); ax[1].legend()
plt.tight_layout(); plt.show()

# %% 示例：基于回归的有向推断与先验知识整合（LASSO 路径 + 惩罚因子）
# 已知 10 个转录因子（TF）与 50 个靶基因，靶基因表达是 1–3 个 TF 的线性组合加噪声（TF 之间彼此相关）。
# 对每个靶基因用坐标下降求 LASSO 正则化路径，边 TF→靶 的得分 = 该系数首次进入模型时的 λ/λmax（越早进入越可信）。
# 先验网络含一半真边和同样多的假边（模拟“不完整且有错”的数据库）；整合方式是把先验边的惩罚乘以 0.5
# （Inferelator 等方法的思路）。在同一真实网络下比较样本少（n = 30）与样本多（n = 120）两种情形。
# 输出解读：数据弱时，先验明显提高 AUPR；数据强时，先验几乎不再增益，甚至略有拖累。先验中的错误边也会被抬高，
# 所以整合后的预测仍需独立验证，且评估时不能再用同一个数据库当金标准。
import numpy as np

def lasso_cd(X, y, lam, w, beta0=None, iters=200):
    """min 1/(2n)||y − Xb||² + lam·Σ w_k|b_k|，X 列已标准化；坐标下降，可用上一个 λ 的解热启动。"""
    n, q = X.shape; b = np.zeros(q) if beta0 is None else beta0.copy(); r = y - X @ b
    for _ in range(iters):
        b_old = b.copy()
        for k in range(q):
            r += X[:, k] * b[k]
            rho = X[:, k] @ r / n
            b[k] = np.sign(rho) * max(abs(rho) - lam * w[k], 0.0)
            r -= X[:, k] * b[k]
        if np.max(np.abs(b - b_old)) < 1e-6:
            break
    return b

def entry_scores(T, y, w, n_lam=40):
    """每个 TF 首次进入 LASSO 路径时的 λ/λmax（从未进入为 0）。"""
    n = len(y); lam_max = np.max(np.abs(T.T @ y) / n / w)
    score = np.zeros(T.shape[1]); b = None
    for lam in lam_max * np.logspace(0, -2, n_lam):
        b = lasso_cd(T, y, lam, w, b)
        score[(b != 0) & (score == 0)] = lam / lam_max
    return score

def aupr(score, gold):
    pairs = [(k, j) for k in range(score.shape[0]) for j in range(score.shape[1])]
    s = np.array([score[e] for e in pairs]); y = np.array([e in gold for e in pairs])
    ys = y[np.argsort(-s, kind="stable")]
    return np.sum((np.cumsum(ys) / np.arange(1, len(ys) + 1))[ys]) / ys.sum(), y.mean()

rng = np.random.default_rng(11)
n_tf, n_tg = 10, 50
L = np.linalg.cholesky(0.5 * np.ones((n_tf, n_tf)) + 0.5 * np.eye(n_tf))   # TF 两两相关约 0.5
B = np.zeros((n_tf, n_tg))                                                  # 真实调控系数
for j in range(n_tg):
    for k in rng.choice(n_tf, size=rng.integers(1, 4), replace=False):
        B[k, j] = rng.choice([-1, 1]) * rng.uniform(0.5, 1.0)
gold = {(k, j) for k in range(n_tf) for j in range(n_tg) if B[k, j] != 0}
true_list = sorted(gold); false_pool = [(k, j) for k in range(n_tf) for j in range(n_tg) if B[k, j] == 0]
half = rng.choice(len(true_list), len(true_list) // 2, replace=False)
prior = {true_list[i] for i in half} | {false_pool[i] for i in rng.choice(len(false_pool), len(half), replace=False)}
S_prior = np.array([[1.0 if (k, j) in prior else 0.0 for j in range(n_tg)] for k in range(n_tf)])
S_prior += 1e-3 * rng.random(S_prior.shape)                 # 仅先验：先验边内部随机排序
print(f"真边 {len(gold)} 条；先验 {len(prior)} 条（其中正确 {len(prior & gold)} 条）；仅先验 AUPR = {aupr(S_prior, gold)[0]:.3f}")

res = {}
for n in [30, 120]:
    T = rng.normal(size=(n, n_tf)) @ L.T; T = (T - T.mean(0)) / T.std(0)
    Y = T @ B + 1.5 * rng.normal(size=(n, n_tg)); Y = (Y - Y.mean(0)) / Y.std(0)
    S_data = np.zeros((n_tf, n_tg)); S_both = np.zeros((n_tf, n_tg))
    for j in range(n_tg):
        S_data[:, j] = entry_scores(T, Y[:, j], np.ones(n_tf))
        S_both[:, j] = entry_scores(T, Y[:, j], np.array([0.5 if (k, j) in prior else 1.0 for k in range(n_tf)]))
    (a_d, base), (a_b, _) = aupr(S_data, gold), aupr(S_both, gold)
    wrong = [e for e in prior if e not in gold]
    print(f"n = {n:3d}：仅数据 AUPR = {a_d:.3f}，数据 + 先验 AUPR = {a_b:.3f}（随机 {base:.3f}）；"
          f"先验错误边的平均得分 {np.mean([S_data[e] for e in wrong]):.3f} → {np.mean([S_both[e] for e in wrong]):.3f}")
    res[n] = (a_d, a_b, base)

import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(6.4, 4.2))
x = np.arange(len(res))
ax.bar(x - 0.18, [v[0] for v in res.values()], 0.36, color="0.6", label="data only")
ax.bar(x + 0.18, [v[1] for v in res.values()], 0.36, color="C0", hatch="//", label="data + prior (penalty × 0.5)")
ax.axhline(aupr(S_prior, gold)[0], color="C3", ls="--", lw=1, label="prior only")
ax.axhline(list(res.values())[0][2], color="k", ls=":", lw=1, label="random")
ax.set_xticks(x); ax.set_xticklabels([f"n = {n}" for n in res]); ax.set_ylabel("AUPR")
ax.set_title("Prior knowledge helps most when data are scarce"); ax.legend(fontsize=8)
plt.tight_layout(); plt.show()

# %% 示例：差异共表达——Fisher z 检验与模块水平的置换检验
# 两种条件各 50 个样本、40 个基因：基因 0–9 在条件 A 中共表达（共享一个潜在因子），在条件 B 中失去协同（“重布线”）；
# 基因 10–19 在两种条件中都共表达，但条件 B 中平均表达整体上调（差异表达而非差异共表达）；其余为噪声基因。
# 逐对用 Fisher z 检验 H0: ρ_A = ρ_B，BH 法控制 FDR；再对“模块平均相关之差”做样本标签置换检验。
# 输出解读：差异共表达对集中在基因 0–9 内部；t 检验找到的差异表达基因是 10–19，两类信号互不重叠。
import numpy as np
from scipy import stats

rng = np.random.default_rng(5)
n, p = 50, 40
def condition(rewired, shift):
    X = rng.normal(size=(n, p))
    f = rng.normal(size=n); g = rng.normal(size=n)
    if not rewired:
        X[:, :10] = 0.8 * f[:, None] + 0.6 * rng.normal(size=(n, 10))
    X[:, 10:20] = 0.8 * g[:, None] + 0.6 * rng.normal(size=(n, 10)) + shift
    return X
XA, XB = condition(False, 0.0), condition(True, 1.0)

RA, RB = np.corrcoef(XA.T), np.corrcoef(XB.T)
iu = np.triu_indices(p, 1)
z = (np.arctanh(RA[iu]) - np.arctanh(RB[iu])) / np.sqrt(1 / (n - 3) + 1 / (n - 3))
pv = 2 * stats.norm.sf(np.abs(z))
m = len(pv); o = np.argsort(pv); q = np.empty(m)
q[o] = np.minimum.accumulate((pv[o] * m / np.arange(1, m + 1))[::-1])[::-1]   # BH 校正
sig = q < 0.05
in_mod = (iu[0] < 10) & (iu[1] < 10)
print(f"FDR<0.05 的差异共表达基因对：{sig.sum()} 个，其中位于基因 0–9 内部的 {np.sum(sig & in_mod)} 个（该区域共 {in_mod.sum()} 对）")
t, pt = stats.ttest_ind(XA, XB)
print("差异表达（t 检验 p<0.001）的基因：", np.where(pt < 1e-3)[0].tolist())

def mean_r(X, idx):
    R = np.corrcoef(X[:, idx].T); return R[np.triu_indices(len(idx), 1)].mean()
for name, idx in [("基因 0–9", np.arange(10)), ("基因 10–19", np.arange(10, 20))]:
    obs = mean_r(XA, idx) - mean_r(XB, idx)
    pooled = np.vstack([XA, XB]); null = []
    for _ in range(2000):
        perm = rng.permutation(2 * n)
        null.append(mean_r(pooled[perm[:n]], idx) - mean_r(pooled[perm[n:]], idx))
    p_perm = (1 + np.sum(np.abs(null) >= abs(obs))) / (1 + len(null))
    print(f"{name}：平均相关 A = {mean_r(XA, idx):.2f}，B = {mean_r(XB, idx):.2f}，差 = {obs:.2f}，置换 p = {p_perm:.4f}")

import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 2, figsize=(10, 4.2), constrained_layout=True)
for a, Rm, title in zip(ax, [RA, RB], ["condition A", "condition B"]):
    im = a.imshow(Rm, cmap="RdBu_r", vmin=-1, vmax=1, interpolation="nearest")
    a.set_title(title); a.set_xlabel("gene"); a.set_ylabel("gene")
    for b in (9.5, 19.5):
        a.axhline(b, color="k", lw=0.6); a.axvline(b, color="k", lw=0.6)
fig.colorbar(im, ax=ax, shrink=0.85, label="Pearson r")
fig.suptitle("Genes 0–9 lose co-expression in B (rewired); genes 10–19 keep it")
plt.show()

# %% 示例：模块保守性检验（简化版 modulePreservation 的 Z 统计量）
# 在参考数据中定义两个模块；检验数据中模块 1 保留了共表达结构，模块 2 的基因彼此独立（未保留）。
# 对每个模块计算密度类统计量（模块内平均相关 meanCor、第一主成分解释方差 propVE）与
# 连接模式类统计量（模块内连接度的跨数据相关 cor.kIM、相关矩阵上三角的跨数据相关 cor.cor），
# 再在检验数据（300 个基因）中随机抽取同样大小的基因集合 200 次得到零分布，换算为 Z 分数：
# Zdensity、Zconnectivity 分别取中位数，Zsummary = 二者的平均（与 WGCNA 实现的汇总方式一致）。
# 输出解读：模块 1 的 Zsummary 高（按 Langfelder 等 2011 的经验阈值属于“强证据”），模块 2 在 0 附近。完整实现还包括更多统计量，并以模块标签置换生成零分布。
import numpy as np

rng = np.random.default_rng(21)
def dataset(preserve2, n=50):
    p = 300; X = rng.normal(size=(n, p))
    f1, f2 = rng.normal(size=n), rng.normal(size=n)
    load1 = np.linspace(0.5, 0.9, 25)
    X[:, :25] = f1[:, None] * load1 + rng.normal(size=(n, 25)) * np.sqrt(1 - load1**2)
    if preserve2:
        X[:, 25:45] = 0.75 * f2[:, None] + 0.66 * rng.normal(size=(n, 20))
    return X
ref, test = dataset(True), dataset(False)
modules = {"模块 1": np.arange(25), "模块 2": np.arange(25, 45)}

def stats_for(idx, Rref_full, Xtest):
    Rr = Rref_full[np.ix_(idx, idx)]; Rt = np.corrcoef(Xtest[:, idx].T)
    sgn = np.sign(Rr); iu = np.triu_indices(len(idx), 1)
    Z = (Xtest[:, idx] - Xtest[:, idx].mean(0)) / Xtest[:, idx].std(0)
    s = np.linalg.svd(Z, compute_uv=False)
    density = [np.mean((sgn * Rt)[iu]), s[0]**2 / np.sum(s**2)]
    kref = np.abs(Rr).sum(0) - 1; ktest = np.abs(Rt).sum(0) - 1
    connectivity = [np.corrcoef(kref, ktest)[0, 1], np.corrcoef(Rr[iu], Rt[iu])[0, 1]]
    return np.array(density), np.array(connectivity)

Rref = np.corrcoef(ref.T)
zsum = {}
for name, idx in modules.items():
    d_obs, c_obs = stats_for(idx, Rref, test)
    d_null, c_null = [], []
    for _ in range(200):
        rnd = rng.choice(test.shape[1], len(idx), replace=False)
        d, c = stats_for(rnd, Rref, test); d_null.append(d); c_null.append(c)
    d_null, c_null = np.array(d_null), np.array(c_null)
    Zd = np.median((d_obs - d_null.mean(0)) / d_null.std(0))
    Zc = np.median((c_obs - c_null.mean(0)) / c_null.std(0))
    print(f"{name}（{len(idx)} 基因）：meanCor = {d_obs[0]:.2f}，cor.kIM = {c_obs[0]:.2f}，cor.cor = {c_obs[1]:.2f}；"
          f"Zdensity = {Zd:.1f}，Zconnectivity = {Zc:.1f}，Zsummary = {(Zd + Zc) / 2:.1f}")
    zsum[name] = (Zd, Zc, (Zd + Zc) / 2)

import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(6.4, 4.2))
x = np.arange(len(zsum)); vals = np.array(list(zsum.values()))
for k, (lab, h) in enumerate([("Zdensity", ""), ("Zconnectivity", "//"), ("Zsummary", "")]):
    ax.bar(x + (k - 1) * 0.26, vals[:, k], 0.26, hatch=h, color=["0.75", "0.55", "C0"][k], label=lab)
ax.axhline(2, color="C1", ls="--", lw=1, label="Z = 2 (weak evidence)")
ax.axhline(10, color="C3", ls=":", lw=1, label="Z = 10 (strong evidence)")
ax.set_xticks(x); ax.set_xticklabels([f"module {i + 1}" for i in x]); ax.set_ylabel("preservation Z")
ax.set_title("Module 1 is preserved in the test data, module 2 is not"); ax.legend(fontsize=8)
plt.tight_layout(); plt.show()

# %% 示例：评估指标——AUROC、AUPR、早期精度与不完整金标准
# 1000 个候选基因对中只有 20 条真边（π = 2%）。打分器 A 把 8 条真边排在最前、其余真边与随机无异；
# 打分器 B 把全部真边整体前移，但有 30 个假阳性得分最高（例如批次效应造成的强共表达）。
# 输出解读：B 的 AUROC 更高，但 AUPR 与早期精度显示 A 对“挑出少量可验证的边”更有用。
# 再把金标准随机删去一半真边（模拟数据库不完整）：被漏标的真边被算作假阳性，表观精确率系统性偏低。
import numpy as np

def metrics(score, y):
    order = np.argsort(-score, kind="stable"); ys = y[order]
    tp = np.cumsum(ys); prec = tp / np.arange(1, len(ys) + 1)
    aupr = np.sum(prec[ys]) / ys.sum()                     # 平均精确率，不做线性插值
    ranks = np.argsort(np.argsort(score)) + 1
    auroc = (ranks[y].sum() - y.sum() * (y.sum() + 1) / 2) / (y.sum() * (~y).sum())
    k = y.sum(); ep = tp[k - 1] / k                         # 早期精度：前 k 条（k = 真边数）中的精确率
    return auroc, aupr, ep

rng = np.random.default_rng(2)
m, k = 1000, 20
y = np.zeros(m, dtype=bool); y[rng.choice(m, k, replace=False)] = True
A = rng.random(m); A[np.where(y)[0][:8]] = 2 + rng.random(8)
B = rng.random(m) + 0.6 * y
B[rng.choice(np.where(~y)[0], 30, replace=False)] += 2
print(f"真边比例 π = {y.mean():.3f}：随机预测的 AUROC ≈ 0.5，AUPR ≈ π，早期精度 ≈ π")
for name, s in [("打分器 A", A), ("打分器 B", B)]:
    auroc, aupr, ep = metrics(s, y)
    print(f"{name}：AUROC = {auroc:.3f}；AUPR = {aupr:.3f}（AUPR 比 {aupr / y.mean():4.1f}）；早期精度 = {ep:.2f}（EPR {ep / y.mean():4.1f}）")

y_obs = y.copy(); y_obs[rng.choice(np.where(y)[0], k // 2, replace=False)] = False
top = np.argsort(-A)[:k]
print(f"打分器 A 前 {k} 条：按完整金标准精确率 = {y[top].mean():.2f}，按只含一半真边的金标准 = {y_obs[top].mean():.2f}；"
      f"AUPR（对不完整金标准）= {metrics(A, y_obs)[1]:.3f}")

import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 2, figsize=(10, 4))
for s, yy, lab, ls in [(A, y, "scorer A", "-"), (B, y, "scorer B", "--"), (A, y_obs, "scorer A, half gold standard", ":")]:
    ys = yy[np.argsort(-s, kind="stable")]; tp = np.cumsum(ys); fp = np.cumsum(~ys)
    au, ap, _ = metrics(s, yy)
    ax[0].plot(fp / fp[-1], tp / tp[-1], ls, lw=2, label=f"{lab} (AUROC {au:.2f})")
    ax[1].plot(tp / tp[-1], tp / np.arange(1, len(ys) + 1), ls, lw=2, label=f"{lab} (AUPR {ap:.2f})")
ax[0].plot([0, 1], [0, 1], color="0.6", lw=0.8); ax[1].axhline(y.mean(), color="0.6", lw=0.8)
ax[0].set_xlabel("false positive rate"); ax[0].set_ylabel("true positive rate"); ax[0].set_title("ROC: B looks better")
ax[1].set_xlabel("recall"); ax[1].set_ylabel("precision"); ax[1].set_title("PR: A finds the top edges")
ax[0].legend(fontsize=8, loc="lower right"); ax[1].legend(fontsize=8, loc="upper right")
plt.tight_layout(); plt.show()
