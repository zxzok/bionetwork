# 依赖：networkx>=3, numpy, scipy, matplotlib
# 数据：全部为 numpy 生成的模拟数据，仅用于演示方法，不代表真实人脑、真实量表或真实蛋白质网络。
#   - 模拟“脑区时间序列”：N 个脑区 × T 个时间点的矩阵，每行一个脑区；
#     信号 = 所属功能系统的共同波动 + 全脑共同波动 + 独立噪声。
#   - 模拟“量表数据”：n 名被试 × p 个条目，由已知的稀疏精度矩阵（真实网络）生成。
#   - 若换成自己的数据：时间序列用 N×T 的 numpy 数组；量表用 n×p 数组；网络用 networkx.Graph。
# 每个“# %% 示例”单元可以单独运行，单元之间不共享变量。

# %% 示例：阈值敏感性——同一个相关矩阵，不同绝对阈值下的拓扑指标
# 用一个 60 脑区的模拟相关矩阵，在一串绝对阈值上计算密度、平均聚集系数、全局效率，
# 并用 Spearman 秩相关检查“度排序”（枢纽排序）与参考阈值下是否一致。
# 解读：聚集系数和效率随阈值（也就是随密度）系统变化；枢纽排序在不同阈值下并不完全一致。
# 报告时应给出整条曲线或曲线下面积，而不是挑一个阈值。
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from scipy.stats import spearmanr

plt.rcParams["font.sans-serif"] = ["PingFang SC", "Microsoft YaHei", "SimHei", "Noto Sans CJK SC", "DejaVu Sans"]
rng = np.random.default_rng(1)
n_mod, per, T = 4, 15, 200
N = n_mod * per
labels = np.repeat(np.arange(n_mod), per)
load = rng.uniform(0.3, 1.0, size=N)                     # 各脑区对本系统的载荷不同
sys_sig = rng.standard_normal((n_mod, T))
glob = rng.standard_normal(T)
X = load[:, None] * sys_sig[labels] + 0.3 * glob + rng.standard_normal((N, T))
R = np.corrcoef(X)
np.fill_diagonal(R, 0)

taus = np.round(np.arange(0.10, 0.46, 0.05), 2)
ref_tau = 0.25
deg_ref = (np.abs(R) > ref_tau).sum(axis=1)
rows = []
for tau in taus:
    A = (np.abs(R) > tau).astype(int)
    G = nx.from_numpy_array(A)
    dens = nx.density(G)
    C = nx.average_clustering(G)
    E = nx.global_efficiency(G)
    gcc = max(len(c) for c in nx.connected_components(G)) / N
    rho = spearmanr(A.sum(axis=1), deg_ref)[0]
    rows.append((tau, dens, C, E, gcc, rho))
    print(f"阈值 {tau:.2f}: 密度={dens:.3f}  聚集系数={C:.3f}  全局效率={E:.3f}  "
          f"最大连通分支占比={gcc:.2f}  度排序与阈值{ref_tau}的秩相关={rho:.2f}")

rows = np.array(rows)
fig, ax = plt.subplots(1, 2, figsize=(9, 3.5))
ax[0].plot(rows[:, 0], rows[:, 1], "o-", label="密度")
ax[0].plot(rows[:, 0], rows[:, 2], "s-", label="平均聚集系数")
ax[0].plot(rows[:, 0], rows[:, 3], "^-", label="全局效率")
ax[0].set_xlabel("绝对阈值 |r| >")
ax[0].legend(fontsize=8)
ax[1].plot(rows[:, 1], rows[:, 2], "s-", label="聚集系数")
ax[1].plot(rows[:, 1], rows[:, 3], "^-", label="全局效率")
ax[1].set_xlabel("网络密度")
ax[1].legend(fontsize=8)
fig.suptitle("模拟数据：拓扑指标随阈值与密度变化")
fig.tight_layout()
plt.show()

# %% 示例：保度随机化（双边交换）零模型、z 分数与经验 p 值
# 自己实现 Maslov–Sneppen 双边交换，检查度序列严格不变；再生成 M 个保度随机网络和 M 个 ER 网络，
# 对平均聚集系数和度同配系数计算 z 分数与经验 p 值 p = (1 + #{零模型 >= 观测}) / (M + 1)。
# 解读：ER 只保留节点数和边数，保度零模型还保留度序列；同一观测值对两种零模型的 z 分数可能相差很大，
# 结论只能说“超出了该零模型所保留的性质能解释的范围”。本例中负的度同配相对 ER 显著，
# 相对保度零模型则不显著：它大部分可由度序列本身（简单图中枢纽之间可连的边有限）解释。
import numpy as np
import networkx as nx

def degree_preserving_rewire(G, n_swap_per_edge=10, seed=0):
    """Maslov–Sneppen 双边交换：(a,b),(c,d) -> (a,d),(c,b)。拒绝产生自环或重边的交换。"""
    rng = np.random.default_rng(seed)
    edges = [tuple(e) for e in G.edges()]
    eset = set(frozenset(e) for e in edges)
    m = len(edges)
    n_try, n_ok = n_swap_per_edge * m, 0
    for _ in range(n_try):
        i, j = rng.integers(m, size=2)
        if i == j:
            continue
        a, b = edges[i]
        c, d = edges[j]
        if rng.random() < 0.5:                 # 两种重连方式各占一半
            c, d = d, c
        if len({a, b, c, d}) < 4:
            continue
        e1, e2 = frozenset((a, d)), frozenset((c, b))
        if e1 in eset or e2 in eset:
            continue
        eset -= {frozenset((a, b)), frozenset((c, d))}
        eset |= {e1, e2}
        edges[i], edges[j] = (a, d), (c, b)
        n_ok += 1
    H = nx.Graph()
    H.add_nodes_from(G.nodes())
    H.add_edges_from(edges)
    return H, n_ok / n_try

# 观测网络：一个带三角形闭合倾向的重尾网络（模拟的“相互作用网络”）
G = nx.powerlaw_cluster_graph(300, 3, 0.4, seed=2)
n, m = G.number_of_nodes(), G.number_of_edges()
obs = {"平均聚集系数": nx.average_clustering(G),
       "度同配系数": nx.degree_assortativity_coefficient(G)}

H, acc = degree_preserving_rewire(G, seed=0)
same_deg = sorted(d for _, d in G.degree()) == sorted(d for _, d in H.degree())
same_node_deg = all(G.degree(v) == H.degree(v) for v in G)
print(f"交换接受率={acc:.2f}；度序列保持={same_deg}；每个节点的度保持={same_node_deg}")

M = 50
null = {"ER": {k: [] for k in obs}, "保度": {k: [] for k in obs}}
for s in range(M):
    ER = nx.gnm_random_graph(n, m, seed=100 + s)
    DP, _ = degree_preserving_rewire(G, seed=200 + s)
    for name, Hs in (("ER", ER), ("保度", DP)):
        null[name]["平均聚集系数"].append(nx.average_clustering(Hs))
        null[name]["度同配系数"].append(nx.degree_assortativity_coefficient(Hs))

for k, x in obs.items():
    for name in ("ER", "保度"):
        v = np.array(null[name][k])
        z = (x - v.mean()) / v.std(ddof=1)
        # 双侧经验 p 值：以零分布均值为中心比较偏离幅度
        p = (1 + np.sum(np.abs(v - v.mean()) >= abs(x - v.mean()))) / (M + 1)
        print(f"{k}: 观测={x:.3f}  {name}零模型 均值={v.mean():.3f} 标准差={v.std(ddof=1):.3f}  "
              f"z={z:.1f}  经验p={p:.3f}（M={M} 时最小可能值为 {1/(M+1):.3f}）")

# 作图：两种零模型下的零分布与观测值
import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 2, figsize=(10, 4))
for a, k, xl in zip(ax, ["平均聚集系数", "度同配系数"], ["average clustering", "degree assortativity"]):
    a.hist(null["ER"][k], bins=12, color="0.75", edgecolor="white", label="ER null")
    a.hist(null["保度"][k], bins=12, color="C0", alpha=0.6, edgecolor="white", label="degree-preserving null")
    a.axvline(obs[k], color="C3", lw=2, label="observed")
    a.set_xlabel(xl); a.set_ylabel("count"); a.legend(fontsize=8)
ax[0].set_title("Clustering exceeds both nulls", fontsize=10)
ax[1].set_title("Negative r is explained by the degree sequence", fontsize=10)
plt.tight_layout(); plt.show()

# %% 示例：置换检验比较两组网络——逐边 FDR 与基于网络的统计（NBS）
# 模拟两组被试（各 20 人）、30 个脑区的功能连接；B 组在脑区 0–5 组成的子网络内连接减弱。
# 每名被试得到一个 Fisher z 矩阵，逐边做两样本 t 检验，然后：
#   (1) Benjamini–Hochberg FDR 校正；(2) NBS：主阈值 |t|>3 下超阈值边构成的最大连通分量大小，
#   置换组标签 1000 次得到最大分量大小的零分布，给出族错误率（FWE）校正的 p 值。
# 解读：NBS 的结论在“子网络”层面（这一组相连的边整体显著），不能据此说其中某一条边显著。
import numpy as np
import networkx as nx
from scipy import stats

rng = np.random.default_rng(3)
N, T, n_per = 30, 150, 20
iu = np.triu_indices(N, 1)
sub = np.arange(6)

def subject_fc(effect):
    """模拟一名被试的 Fisher z 连接向量。effect 为子网络内共同信号的载荷。"""
    common = rng.standard_normal(T)
    X = 0.4 * common + rng.standard_normal((N, T))
    X[sub] += effect * rng.standard_normal(T)            # 子网络共享的额外信号
    R = np.corrcoef(X)
    return np.arctanh(R[iu])

ZA = np.array([subject_fc(0.9) for _ in range(n_per)])
ZB = np.array([subject_fc(0.5) for _ in range(n_per)])
Zall = np.vstack([ZA, ZB])
grp = np.r_[np.zeros(n_per), np.ones(n_per)].astype(bool)
truth = np.isin(iu[0], sub) & np.isin(iu[1], sub)

def tstats(Z, g):
    return stats.ttest_ind(Z[~g], Z[g], axis=0).statistic

t_obs = tstats(Zall, grp)
p_edge = 2 * stats.t.sf(np.abs(t_obs), df=2 * n_per - 2)

def bh(p, q=0.05):
    m = len(p)
    order = np.argsort(p)
    passed = p[order] <= q * np.arange(1, m + 1) / m
    k = np.max(np.nonzero(passed)[0]) + 1 if passed.any() else 0
    sig = np.zeros(m, bool)
    sig[order[:k]] = True
    return sig

sig_fdr = bh(p_edge)
print(f"边数={len(p_edge)}，真实差异边={truth.sum()}")
print(f"未校正 p<0.05：{(p_edge < 0.05).sum()} 条，其中真实差异边 {(p_edge < 0.05)[truth].sum()} 条")
print(f"FDR q<0.05：{sig_fdr.sum()} 条，其中真实差异边 {sig_fdr[truth].sum()} 条")

def max_component(t, thr=3.0):
    keep = np.abs(t) > thr
    G = nx.Graph()
    G.add_edges_from(zip(iu[0][keep], iu[1][keep]))
    comps = list(nx.connected_components(G))
    if not comps:
        return 0, set()
    best = max(comps, key=lambda c: G.subgraph(c).number_of_edges())
    return G.subgraph(best).number_of_edges(), best

size_obs, nodes_obs = max_component(t_obs)
n_perm = 1000
null_max = np.empty(n_perm)
for b in range(n_perm):
    null_max[b] = max_component(tstats(Zall, rng.permutation(grp)))[0]
p_fwe = (1 + np.sum(null_max >= size_obs)) / (n_perm + 1)
print(f"NBS：最大超阈值分量含 {size_obs} 条边，节点={sorted(int(v) for v in nodes_obs)}，FWE 校正 p={p_fwe:.4f}")
print(f"置换零分布中最大分量边数的 95% 分位数={np.quantile(null_max, 0.95):.0f}")

# 全局指标的置换检验：平均连接强度（Fisher z 均值）
g_stat = Zall.mean(axis=1)
d_obs = g_stat[~grp].mean() - g_stat[grp].mean()
d_null = np.array([g_stat[~g].mean() - g_stat[g].mean()
                   for g in (rng.permutation(grp) for _ in range(5000))])
p_glob = (1 + np.sum(np.abs(d_null) >= abs(d_obs))) / (5000 + 1)
print(f"平均连接强度组差={d_obs:.4f}，置换 p={p_glob:.4f}")

# 作图：逐边 t 统计量矩阵（子网络 0–5 在左上角），以及 NBS 最大分量的置换零分布
import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 2, figsize=(10, 4))
Tm = np.zeros((N, N)); Tm[iu] = t_obs; Tm += Tm.T
im = ax[0].imshow(Tm, cmap="RdBu_r", vmin=-6, vmax=6)
fig.colorbar(im, ax=ax[0], label="t (group A - B)")
ax[0].set_title("Edge-wise t; true effect in regions 0-5", fontsize=10); ax[0].set_xlabel("region"); ax[0].set_ylabel("region")
ax[1].hist(null_max, bins=range(int(max(null_max.max(), size_obs)) + 2), color="0.7", edgecolor="white",
           label="permutation null (max component)")
ax[1].axvline(size_obs, color="C3", lw=2, label=f"observed = {size_obs} edges")
ax[1].set_xlabel("edges in largest suprathreshold component (|t|>3)"); ax[1].set_ylabel("count")
ax[1].set_title(f"NBS: FWE-corrected p = {p_fwe:.4f}", fontsize=10); ax[1].legend(fontsize=8)
plt.tight_layout(); plt.show()

# %% 示例：bootstrap 边稳定性与病例删除稳定性（偏相关网络）
# 由一个已知的稀疏精度矩阵生成 n=300 名被试、p=8 个条目的模拟量表数据，估计偏相关网络。
# (1) 非参数 bootstrap：有放回重抽样被试 1000 次，得到每条边的 95% 分位数区间和“|偏相关|>0.1 的比例”；
# (2) 病例删除：无放回地删去 10%–70% 的被试，看强度中心性与全样本的相关，计算类似 CS 系数的指标。
# 解读：真实的强边区间远离 0；多数不存在的边区间包含 0，但同时考察几十条边时，总会有个别假边的
# 区间不含 0，弱的真实边也可能与假边难以区分——逐边区间不是多重比较校正。这里为了自包含用了未正则化的偏相关，
# 实际症状网络常用 EBICglasso，此时 bootstrap 区间会因收缩而偏向 0，只宜用于判断边的可区分性。
import numpy as np

rng = np.random.default_rng(4)
p, n = 8, 300
K = np.eye(p)
true_edges = [(0, 1, 0.35), (1, 2, 0.3), (2, 3, 0.3), (3, 4, 0.25), (4, 5, 0.3), (5, 6, 0.25), (6, 7, 0.3), (0, 4, 0.2)]
for i, j, w in true_edges:
    K[i, j] = K[j, i] = -w                       # 精度矩阵负元素对应正偏相关
Sigma = np.linalg.inv(K)
X = rng.multivariate_normal(np.zeros(p), Sigma, size=n)

def pcor(X):
    P = np.linalg.inv(np.corrcoef(X, rowvar=False))
    d = np.sqrt(np.diag(P))
    W = -P / np.outer(d, d)
    np.fill_diagonal(W, 0)
    return W

iu = np.triu_indices(p, 1)
W0 = pcor(X)
B = 1000
boot = np.empty((B, len(iu[0])))
for b in range(B):
    boot[b] = pcor(X[rng.integers(n, size=n)])[iu]
lo, hi = np.percentile(boot, [2.5, 97.5], axis=0)
inc = (np.abs(boot) > 0.1).mean(axis=0)
is_true = np.zeros((p, p), bool)
for i, j, _ in true_edges:
    is_true[i, j] = is_true[j, i] = True
print("边      估计     95%区间            |w|>0.1比例  真实存在")
for k in np.argsort(-np.abs(W0[iu]))[:12]:
    i, j = iu[0][k], iu[1][k]
    print(f"{i}-{j}   {W0[i, j]:+.3f}  [{lo[k]:+.3f}, {hi[k]:+.3f}]   {inc[k]:.2f}        {is_true[i, j]}")
excl0 = (lo > 0) | (hi < 0)
t_vec = is_true[iu]
print(f"区间不含 0：真实边 {excl0[t_vec].sum()}/{t_vec.sum()} 条，不存在的边 {excl0[~t_vec].sum()}/{(~t_vec).sum()} 条")

# 病例删除稳定性：强度中心性
s0 = np.abs(W0).sum(axis=1)
props = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]
cs = 0.0
r_drop = []                                   # 保存每个删除比例下的相关，用于作图
for prop in props:
    keep = int(round((1 - prop) * n))
    r = np.array([np.corrcoef(np.abs(pcor(X[rng.choice(n, keep, replace=False)])).sum(axis=1), s0)[0, 1]
                  for _ in range(300)])
    r_drop.append(r)
    frac = (r >= 0.7).mean()
    print(f"删去 {prop:.0%} 被试：强度与全样本相关的中位数={np.median(r):.2f}，r>=0.7 的比例={frac:.2f}")
    if frac >= 0.95:
        cs = prop
print(f"类 CS 系数（95% 的子样本中 r>=0.7 时可删去的最大比例）= {cs:.1f}")

# 作图：全部边的 bootstrap 95% 区间（按估计值排序，真实边与不存在的边分色）；病例删除稳定性曲线
import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 2, figsize=(10, 4.2))
o = np.argsort(W0[iu])
for j, k in enumerate(o):
    c = "C3" if t_vec[k] else "0.5"
    ax[0].plot([lo[k], hi[k]], [j, j], color=c, lw=1.5); ax[0].plot(W0[iu][k], j, "o", color=c, ms=3)
ax[0].axvline(0, color="k", lw=0.8)
ax[0].plot([], [], color="C3", label="true edge"); ax[0].plot([], [], color="0.5", label="absent edge")
ax[0].set_xlabel("partial correlation (bootstrap 95% interval)"); ax[0].set_yticks([]); ax[0].legend(fontsize=8)
ax[0].set_title("Strong true edges are far from 0", fontsize=10)
ax[1].boxplot(r_drop, showfliers=False); ax[1].set_xticklabels([f"{p_:.0%}" for p_ in props])
ax[1].axhline(0.7, color="C3", ls="--", label="r = 0.7")
ax[1].set_xlabel("proportion of cases dropped"); ax[1].set_ylabel("corr. with full-sample strength")
ax[1].set_title(f"Case-dropping stability (CS-like = {cs:.1f})", fontsize=10); ax[1].legend(fontsize=8)
plt.tight_layout(); plt.show()

# %% 示例：比例阈值与密度匹配——整体连接强度差异如何“制造”拓扑差异
# 两组模拟被试拥有完全相同的模块结构，只是 B 组的系统内信号整体更弱（例如头动更大或信噪比更低）。
# 比较三种做法下的组间差异：(1) 绝对阈值；(2) 比例阈值（各被试保留最强的前 10% 边）；
# (3) 在 10%–30% 密度范围上积分（曲线下面积），并把聚集系数除以同度序列随机网络的值做归一化。
# 依次模拟两种情形：B 组信号略弱、B 组信噪比明显更低。
# 解读：绝对阈值下的“差异”主要来自密度不同；比例阈值消除了密度差。信号略弱时比例阈值下差异基本消失；
# 信噪比明显更低时，B 组最强的 10% 边中混入更多接近噪声的边，网络向随机网络靠拢，差异重新出现
# （本例中在归一化聚集系数的 AUC 上最明显）——
# 这时的差异来源是信噪比，而不是“拓扑组织”本身不同。最后演示 MST 骨架 + 比例补边保证连通。
import numpy as np
import networkx as nx
from scipy import stats

rng = np.random.default_rng(5)
n_mod, per, T, n_sub = 4, 10, 200, 15
N = n_mod * per
labels = np.repeat(np.arange(n_mod), per)
iu = np.triu_indices(N, 1)

def subject_R(strength):
    sys_sig = rng.standard_normal((n_mod, T))
    X = strength * sys_sig[labels] + rng.standard_normal((N, T))
    R = np.corrcoef(X)
    np.fill_diagonal(R, 0)
    return R

def threshold_abs(R, tau):
    return nx.from_numpy_array((R > tau).astype(int))

def threshold_prop(R, density):
    k = int(round(density * len(iu[0])))
    w = R[iu]
    keep = np.argsort(-w)[:k]
    G = nx.Graph()
    G.add_nodes_from(range(R.shape[0]))
    G.add_edges_from(zip(iu[0][keep], iu[1][keep]))
    return G

def report(name, fA, fB):
    a, b = np.array(fA), np.array(fB)
    t, pv = stats.ttest_ind(a, b)
    print(f"  {name:<26} A={a.mean():.3f}  B={b.mean():.3f}  t={t:+.2f}  p={pv:.3g}")

def norm_clustering(G, n_null=3, seed=0):
    """聚集系数除以同度序列随机网络（networkx 内置双边交换）的平均聚集系数。"""
    m = G.number_of_edges()
    c_rand = []
    for s in range(n_null):
        H = G.copy()
        nx.double_edge_swap(H, nswap=5 * m, max_tries=100 * m, seed=seed + s)
        c_rand.append(nx.average_clustering(H))
    return nx.average_clustering(G) / np.mean(c_rand)

grid = np.arange(0.10, 0.31, 0.05)
def auc_norm_c(R, seed):
    vals = np.array([norm_clustering(threshold_prop(R, d), seed=seed) for d in grid])
    return float(np.sum((vals[1:] + vals[:-1]) / 2 * np.diff(grid)))   # 梯形法积分

partition = [set(np.where(labels == k)[0]) for k in range(n_mod)]
for strength_B in (0.6, 0.45):            # 情形一：B 组信号略弱；情形二：B 组信噪比明显更低
    groups = {"A": [subject_R(0.8) for _ in range(n_sub)],
              "B": [subject_R(strength_B) for _ in range(n_sub)]}
    mean_fc = {g: round(float(np.mean([R[iu].mean() for R in Rs])), 3) for g, Rs in groups.items()}
    print(f"B 组系统内信号载荷={strength_B}；组平均连接强度 {mean_fc}")
    report("绝对阈值 r>0.2：密度", [nx.density(threshold_abs(R, 0.2)) for R in groups["A"]],
           [nx.density(threshold_abs(R, 0.2)) for R in groups["B"]])
    report("绝对阈值 r>0.2：聚集系数", [nx.average_clustering(threshold_abs(R, 0.2)) for R in groups["A"]],
           [nx.average_clustering(threshold_abs(R, 0.2)) for R in groups["B"]])
    report("比例阈值 10%：聚集系数", [nx.average_clustering(threshold_prop(R, 0.10)) for R in groups["A"]],
           [nx.average_clustering(threshold_prop(R, 0.10)) for R in groups["B"]])
    report("比例阈值 10%：已知划分模块度",
           [nx.community.modularity(threshold_prop(R, 0.10), partition) for R in groups["A"]],
           [nx.community.modularity(threshold_prop(R, 0.10), partition) for R in groups["B"]])
    report("密度10%–30% 归一化C的AUC", [auc_norm_c(R, 10 * s) for s, R in enumerate(groups["A"])],
           [auc_norm_c(R, 500 + 10 * s) for s, R in enumerate(groups["B"])])

# 最小生成树（MST）骨架 + 比例补边：保证每个被试的网络连通
R = groups["B"][0]
T_mst = nx.maximum_spanning_tree(nx.from_numpy_array(np.clip(R, 0, None)))
G_prop = threshold_prop(R, 0.10)
G_union = nx.compose(T_mst, G_prop)
print(f"B 组被试 1：比例阈值 10% 连通={nx.is_connected(G_prop)}，"
      f"MST+比例阈值 连通={nx.is_connected(G_union)}，边数 {G_prop.number_of_edges()} -> {G_union.number_of_edges()}")

# 作图（情形二的被试）：绝对阈值下聚集系数几乎完全跟着密度走；比例阈值消除了密度差
import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 2, figsize=(10, 4))
for g, mk in (("A", "o"), ("B", "s")):
    Gs = [threshold_abs(R, 0.2) for R in groups[g]]
    ax[0].plot([nx.density(H) for H in Gs], [nx.average_clustering(H) for H in Gs], mk, label=f"group {g}")
ax[0].set_xlabel("density (absolute threshold r > 0.2)"); ax[0].set_ylabel("average clustering")
ax[0].set_title("Absolute threshold: clustering tracks density", fontsize=10); ax[0].legend()
cA = [nx.average_clustering(threshold_prop(R, 0.10)) for R in groups["A"]]
cB = [nx.average_clustering(threshold_prop(R, 0.10)) for R in groups["B"]]
ax[1].boxplot([cA, cB]); ax[1].set_xticklabels(["group A", "group B (low SNR)"])
ax[1].set_ylabel("average clustering (top 10% edges)")
ax[1].set_title("Proportional threshold: equal density, residual SNR effect", fontsize=10)
plt.tight_layout(); plt.show()

# %% 示例：样本量、Fisher z 置信区间，以及相关与偏相关的差别
# (1) 用 Fisher z 计算 r 的 95% 置信区间，展示样本量对区间宽度的影响；
# (2) 模拟链式结构 A -> B -> C，A 与 C 之间没有直接作用：相关网络会连出 A–C 边，偏相关网络不会；
# (3) 模拟对撞结构 A -> C <- B：A 与 B 本无关联，控制 C 后反而出现偏相关（对撞偏倚）。
import numpy as np

def fisher_ci(r, n, level=0.95):
    from scipy.stats import norm
    z, se = np.arctanh(r), 1 / np.sqrt(n - 3)
    q = norm.ppf(0.5 + level / 2)
    return np.tanh(z - q * se), np.tanh(z + q * se)

for n in (30, 100, 300, 1000):
    lo, hi = fisher_ci(0.3, n)
    print(f"r=0.30, n={n:4d}: 95% CI = [{lo:.2f}, {hi:.2f}]，宽度 {hi - lo:.2f}")

def pcor(X):
    P = np.linalg.inv(np.cov(X, rowvar=False))
    d = np.sqrt(np.diag(P))
    W = -P / np.outer(d, d)
    np.fill_diagonal(W, 1)
    return W

rng = np.random.default_rng(6)
n = 2000
a = rng.standard_normal(n)
b = 0.7 * a + rng.standard_normal(n)
c = 0.7 * b + rng.standard_normal(n)
X = np.c_[a, b, c]
print("链式 A->B->C   相关 r(A,C) = %.2f，偏相关 = %.2f" % (np.corrcoef(X, rowvar=False)[0, 2], pcor(X)[0, 2]))
chain = (np.corrcoef(X, rowvar=False)[0, 2], pcor(X)[0, 2])

a = rng.standard_normal(n)
b = rng.standard_normal(n)
c = 0.7 * a + 0.7 * b + rng.standard_normal(n)
X = np.c_[a, b, c]
print("对撞 A->C<-B   相关 r(A,B) = %.2f，偏相关 = %.2f" % (np.corrcoef(X, rowvar=False)[0, 1], pcor(X)[0, 1]))
collider = (np.corrcoef(X, rowvar=False)[0, 1], pcor(X)[0, 1])

# 作图：r=0.3 的 95% CI 随样本量变化；链式与对撞结构中相关与偏相关的差别
import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 2, figsize=(10, 4))
ns = np.arange(10, 1001, 10)
lo_, hi_ = fisher_ci(0.3, ns)
ax[0].fill_between(ns, lo_, hi_, color="C0", alpha=0.3, label="95% CI (Fisher z)")
ax[0].axhline(0.3, color="C0", lw=1.5, label="r = 0.30"); ax[0].axhline(0, color="k", lw=0.8)
ax[0].set_xscale("log"); ax[0].set_xlabel("sample size n"); ax[0].set_ylabel("correlation")
ax[0].set_title("CI excludes 0 only for n > ~40", fontsize=10); ax[0].legend(fontsize=8)
x = np.arange(2)
ax[1].bar(x - 0.2, [chain[0], collider[0]], 0.4, label="correlation")
ax[1].bar(x + 0.2, [chain[1], collider[1]], 0.4, label="partial correlation")
ax[1].set_xticks(x); ax[1].set_xticklabels(["chain A->B->C\n(A, C)", "collider A->C<-B\n(A, B)"])
ax[1].axhline(0, color="k", lw=0.8); ax[1].legend(fontsize=8)
ax[1].set_title("Partial correlation removes the chain edge\nbut creates a collider edge", fontsize=10)
plt.tight_layout(); plt.show()

# %% 示例：从时间序列推断有向边——Granger 因果、条件 GC 与转移熵（高斯情形）
# 模拟 3 变量一阶向量自回归 VAR(1)：Z 同时驱动 X 与 Y（Z 先于 X 一步、先于 Y 两步），X 与 Y 之间没有直接作用。
# 用最小二乘拟合受限/完整自回归模型，计算 GC = ln(受限残差方差 / 完整残差方差) 与 F 检验。
# (1) 两两 GC 会给出虚假的 X→Y（来自共同驱动 Z 的时滞差）；条件 GC（把 Z 的过去也放入两个模型）消除它；
# (2) 对高斯变量，转移熵 TE = GC / 2（Barnett 等, 2009），这里用高斯熵公式直接计算 TE 来核对；
# (3) 时间降采样（每 k 步取一个点）削弱真实方向的 GC；只给“源”Z 加测量噪声，还会产生高度显著的反向 X→Z。
#     这正是 fMRI 中 GC 的主要难点（Seth 等, 2013）。p 值显示为 0 表示小于浮点下限。
import numpy as np
from scipy import stats

rng = np.random.default_rng(11)

def simulate(T, rng):
    Z = np.zeros(T); X = np.zeros(T); Y = np.zeros(T)
    for t in range(2, T):
        Z[t] = 0.6 * Z[t - 1] + rng.standard_normal()
        X[t] = 0.4 * X[t - 1] + 0.8 * Z[t - 1] + rng.standard_normal()
        Y[t] = 0.4 * Y[t - 1] + 0.8 * Z[t - 2] + rng.standard_normal()
    return np.c_[X, Y, Z]

def lagmat(D, p):
    """把 T×k 序列展开为滞后 1..p 的设计矩阵（加截距）。"""
    T = D.shape[0]
    cols = [D[p - l:T - l] for l in range(1, p + 1)]
    return np.column_stack([np.ones(T - p)] + cols)

def gc(data, src, tgt, cond=(), p=2):
    """src→tgt 的 Granger 因果（可条件于 cond 中的变量）；返回 GC 值、F 统计量与 p 值。"""
    y = data[p:, tgt]
    restricted = [tgt] + list(cond)
    full = restricted + [src]
    Xr, Xf = lagmat(data[:, restricted], p), lagmat(data[:, full], p)
    rss_r = np.sum((y - Xr @ np.linalg.lstsq(Xr, y, rcond=None)[0]) ** 2)
    rss_f = np.sum((y - Xf @ np.linalg.lstsq(Xf, y, rcond=None)[0]) ** 2)
    df1, df2 = p, len(y) - Xf.shape[1]
    F = ((rss_r - rss_f) / df1) / (rss_f / df2)
    return np.log(rss_r / rss_f), F, stats.f.sf(F, df1, df2)

def gaussian_te(data, src, tgt, cond=(), p=2):
    """高斯转移熵：TE = H(Y_t | Y_past, Z_past) - H(Y_t | Y_past, Z_past, X_past)，用条件方差计算。"""
    def cond_var(target_cols):
        y = data[p:, tgt]
        Xd = lagmat(data[:, target_cols], p)
        r = y - Xd @ np.linalg.lstsq(Xd, y, rcond=None)[0]
        return r.var()
    v_r = cond_var([tgt] + list(cond))
    v_f = cond_var([tgt] + list(cond) + [src])
    return 0.5 * np.log(v_r / v_f)        # 高斯熵 H = 0.5 ln(2πe σ²)，常数项相消

D = simulate(3000, rng)
names = ["X", "Y", "Z"]
print("两两 GC（不条件于第三个变量）：")
gc_pair, gc_cond, ds_res = [], [], []          # 保存结果用于作图
for s, t in [(0, 1), (1, 0), (2, 0), (2, 1)]:
    g, F, pv = gc(D, s, t)
    gc_pair.append(g)
    print(f"  {names[s]}→{names[t]}: GC={g:.4f}  F={F:7.1f}  p={pv:.1e}")
print("条件 GC（条件于另一变量的过去）：")
for s, t, c in [(0, 1, (2,)), (1, 0, (2,)), (2, 0, (1,)), (2, 1, (0,))]:
    g, F, pv = gc(D, s, t, cond=c)
    gc_cond.append(g)
    print(f"  {names[s]}→{names[t]} | {names[c[0]]}: GC={g:.4f}  F={F:7.1f}  p={pv:.2g}")

g = gc(D, 2, 1, cond=(0,))[0]
te = gaussian_te(D, 2, 1, cond=(0,))
print(f"Z→Y|X：GC={g:.4f}，高斯 TE={te:.4f}，GC/2={g / 2:.4f}（二者相等）")

# 降采样与测量噪声：真实方向 Z→X（X 不影响 Z），比较 GC(Z→X|Y) 与 GC(X→Z|Y) 及其 F 检验 p 值
print("真实方向 Z→X；比较条件 GC(Z→X|Y) 与 GC(X→Z|Y)：")
Dlong = simulate(20000, rng)
for k, noise_z in ((1, 0.0), (4, 0.0), (1, 3.0), (4, 3.0)):
    Dk = Dlong[::k].copy()
    Dk[:, 2] += noise_z * rng.standard_normal(len(Dk))      # 只给“源”Z 加测量噪声
    f, _, pf = gc(Dk, 2, 0, cond=(1,))
    b, _, pb = gc(Dk, 0, 2, cond=(1,))
    ds_res.append((k, noise_z, f, b))
    print(f"  每 {k} 步取样、Z 的测量噪声 sd={noise_z}: Z→X GC={f:.4f} (p={pf:.1g})   "
          f"X→Z GC={b:.4f} (p={pb:.1g})")

# 作图：两两 GC 与条件 GC；降采样与测量噪声下真实方向与反向 GC
import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 2, figsize=(10, 4))
x = np.arange(4)
ax[0].bar(x - 0.2, gc_pair, 0.4, label="pairwise GC")
ax[0].bar(x + 0.2, gc_cond, 0.4, label="conditional GC")
ax[0].set_xticks(x); ax[0].set_xticklabels(["X->Y", "Y->X", "Z->X", "Z->Y"])
ax[0].set_ylabel("Granger causality (log variance ratio)"); ax[0].legend(fontsize=8)
ax[0].set_title("Conditioning on Z removes the spurious X->Y", fontsize=10)
ax[1].bar(x - 0.2, [r[2] for r in ds_res], 0.4, label="Z->X | Y (true)")
ax[1].bar(x + 0.2, [r[3] for r in ds_res], 0.4, label="X->Z | Y (reverse)")
ax[1].set_xticks(x); ax[1].set_xticklabels([f"step {k}\nnoise sd {nz:g}" for k, nz, _, _ in ds_res])
ax[1].set_yscale("log"); ax[1].set_ylabel("conditional GC"); ax[1].legend(fontsize=8)
ax[1].set_title("Downsampling and source noise distort direction", fontsize=10)
plt.tight_layout(); plt.show()

# %% 示例：采样网络——随机节点采样、随机边采样与滚雪球采样如何改变度分布与其他指标
# “真实”网络：N=5000、带三角形闭合倾向的重尾网络（Holme–Kim 模型）。三种不完整观测：
#   (1) 随机节点采样：保留比例 p 的节点及其之间的边（诱导子图），对应“只研究了部分蛋白”；
#   (2) 随机边采样：每条边以概率 q 被检测到，对应实验灵敏度有限；
#   (3) 滚雪球采样：从少数种子出发沿边扩展，对应“从已知疾病基因出发找相互作用”。
# 解读：节点采样下，原度为 k 的节点观测度服从 Binomial(k, p)，平均度按 p 缩小，分布形状也随之改变；
# 理论上观测度分布的生成函数为 G0(1 - p + p x)。全局传递性（3×三角形数/连通三元组数）在节点采样下期望近似不变
# （三角形与三元组都需要 3 个节点同时被保留），在边采样下约按 q 缩小（三角形需 3 条边，三元组只需 2 条）。
# 滚雪球采样偏向枢纽：样本节点的真实平均度被高估，局部结构也被放大。
import numpy as np
import networkx as nx
from scipy import stats

rng = np.random.default_rng(21)
G = nx.powerlaw_cluster_graph(5000, 3, 0.3, seed=21)
k_true = np.array([d for _, d in G.degree()])

def summary(H, name):
    k = np.array([d for _, d in H.degree()])
    k = k[k > 0]
    gcc = max((len(c) for c in nx.connected_components(H)), default=0) / max(H.number_of_nodes(), 1)
    print(f"{name:<22} 节点={H.number_of_nodes():5d}  非孤立节点平均度={k.mean():5.2f}  最大度={k.max():4d}  "
          f"k的变异系数={k.std() / k.mean():.2f}  孤立点占比={np.mean([d == 0 for _, d in H.degree()]):.2f}  "
          f"最大连通分支占比={gcc:.2f}  全局传递性={nx.transitivity(H):.3f}")
    return k

summary(G, "完整网络")
for p in (0.5, 0.2):
    keep = rng.random(G.number_of_nodes()) < p
    H = G.subgraph(np.flatnonzero(keep)).copy()
    k_obs = np.array([H.degree(v) for v in H])
    summary(H, f"节点采样 p={p}")
    # 理论预测：对被保留的节点，E[k_obs] = p * k_true
    print(f"    观测平均度={k_obs.mean():.2f}，理论 p·<k>={p * k_true.mean():.2f}；"
          f"同一节点观测度与 p·真实度的相关={np.corrcoef(k_obs, p * k_true[keep])[0, 1]:.2f}")

for q in (0.5,):
    H = nx.Graph()
    H.add_nodes_from(G)
    H.add_edges_from(e for e in G.edges() if rng.random() < q)
    summary(H, f"边采样 q={q}")

def snowball(G, n_seeds, n_target, rng):
    """从种子出发做广度优先扩展，按发现顺序取前 n_target 个节点。"""
    seeds = rng.choice(G.number_of_nodes(), n_seeds, replace=False).tolist()
    order, seen, frontier = list(seeds), set(seeds), list(seeds)
    while frontier and len(order) < n_target:
        nxt = []
        for v in frontier:
            for u in G.neighbors(v):
                if u not in seen:
                    seen.add(u); order.append(u); nxt.append(u)
        frontier = nxt
    return G.subgraph(order[:n_target]).copy()

S = snowball(G, 5, 1000, rng)
summary(S, "滚雪球 5 种子→1000 点")
k_in_true = k_true[list(S.nodes())]
print(f"    滚雪球样本中节点在完整网络中的平均度={k_in_true.mean():.2f}（全网平均 {k_true.mean():.2f}）")

# 生成函数核对：节点采样 p=0.2 后，观测度分布 P'(k') = sum_k P(k) C(k,k') p^k' (1-p)^(k-k')
p = 0.2
kmax = k_true.max()
Pk = np.bincount(k_true, minlength=kmax + 1) / len(k_true)
kk = np.arange(kmax + 1)
P_pred = np.array([np.sum(Pk * stats.binom.pmf(j, kk, p)) for j in range(15)])
keep = rng.random(G.number_of_nodes()) < p
H = G.subgraph(np.flatnonzero(keep))
k_obs = np.array([d for _, d in H.degree()])
P_emp = np.bincount(k_obs, minlength=15)[:15] / len(k_obs)
print("k'   理论 P'(k')  经验 P'(k')")
for j in range(0, 8):
    print(f"{j:2d}    {P_pred[j]:.3f}       {P_emp[j]:.3f}")

# 作图：完整网络、节点采样与滚雪球样本的度分布；节点采样后观测度分布的理论与经验对照
import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 2, figsize=(10, 4))
for kv, lab, mk in [(k_true, "full network", "o"), (k_obs, "node sample p=0.2", "s"),
                    (np.array([d for _, d in S.degree()]), "snowball (1000 nodes)", "^")]:
    kv = np.sort(kv[kv > 0])
    ax[0].loglog(kv, 1 - np.arange(len(kv)) / len(kv), mk, ms=3, alpha=0.6, label=lab)
ax[0].set_xlabel("observed degree k"); ax[0].set_ylabel("P(K >= k)"); ax[0].legend(fontsize=8)
ax[0].set_title("Sampling reshapes the degree distribution", fontsize=10)
j = np.arange(15)
ax[1].bar(j, P_emp, color="0.7", label="empirical (node sample p=0.2)")
ax[1].plot(j, P_pred, "o-", color="C3", label="theory: binomial thinning")
ax[1].set_xlabel("observed degree k'"); ax[1].set_ylabel("P'(k')"); ax[1].legend(fontsize=8)
ax[1].set_title("Generating-function prediction matches", fontsize=10)
plt.tight_layout(); plt.show()

# %% 示例：边权不确定性向网络指标的传播——块 bootstrap、边入选概率与“指标的均值 ≠ 均值网络的指标”
# 模拟单名被试 30 个脑区、T=300 个时间点的自相关时间序列（AR(1)，系数 0.7），按 3 个系统共享信号。
# 流程：相关矩阵 → 比例阈值（保留最强 15% 的边）→ 全局效率、传递性、度最高的 5 个“枢纽”。
# (1) “真值”参照：从同一生成模型独立重复模拟 200 次，得到指标的真实抽样标准差；
# (2) 朴素 bootstrap：逐时间点有放回重抽样（破坏自相关）；(3) 循环块 bootstrap：按长度 L 的连续块重抽样。
# 解读：朴素 bootstrap 低估不确定性；块 bootstrap 更接近真实抽样变异。阈值附近的边入选概率接近 0.5，
# 是指标不稳定的主要来源；把整个流程（含阈值化）放进重抽样循环，才能把边权误差传播到网络指标上。
import numpy as np
import networkx as nx

rng = np.random.default_rng(31)
N, T, phi, n_sys = 30, 300, 0.7, 3
labels = np.repeat(np.arange(n_sys), N // n_sys)
load = rng.uniform(0.2, 0.7, size=N)

def ar1(shape, rng):
    e = rng.standard_normal(shape)
    x = np.zeros(shape)
    for t in range(1, shape[-1]):
        x[..., t] = phi * x[..., t - 1] + e[..., t]
    return x

def simulate(rng):
    sys_sig = ar1((n_sys, T), rng)
    return load[:, None] * sys_sig[labels] + ar1((N, T), rng)

iu = np.triu_indices(N, 1)
n_keep = int(round(0.15 * len(iu[0])))

def pipeline(X):
    R = np.corrcoef(X)[iu]
    keep = np.argsort(-R)[:n_keep]
    A = np.zeros((N, N), bool)
    A[iu[0][keep], iu[1][keep]] = True
    A |= A.T
    G = nx.from_numpy_array(A.astype(int))
    deg = A.sum(axis=1)
    return nx.global_efficiency(G), nx.transitivity(G), A[iu], set(np.argsort(-deg)[:5])

# (1) 真实抽样变异（实际研究中拿不到，这里用来检验 bootstrap）
truth = np.array([pipeline(simulate(rng))[:2] for _ in range(200)])
X = simulate(rng)
E0, C0, edges0, hubs0 = pipeline(X)

def boot(X, B, L, rng):
    out, inc, hub_overlap = [], np.zeros(len(iu[0])), []
    for _ in range(B):
        if L == 1:
            idx = rng.integers(T, size=T)
        else:                                     # 循环块 bootstrap
            starts = rng.integers(T, size=int(np.ceil(T / L)))
            idx = (starts[:, None] + np.arange(L)).ravel()[:T] % T
        e, c, a, h = pipeline(X[:, idx])
        out.append((e, c)); inc += a; hub_overlap.append(len(h & hubs0) / 5)
    return np.array(out), inc / B, np.mean(hub_overlap)

print(f"观测：全局效率={E0:.3f}  传递性={C0:.3f}")
print(f"真实抽样标准差（200 次独立重复）：效率 {truth[:, 0].std():.4f}  传递性 {truth[:, 1].std():.4f}")
sd_boot = []                                   # 保存各方法的标准差用于作图
for L in (1, 10, 25):
    res, inc, hov = boot(X, 300, L, rng)
    sd_boot.append(res[:, 0].std())
    unstable = np.mean((inc > 0.2) & (inc < 0.8))
    name = "朴素 bootstrap（逐点）" if L == 1 else f"循环块 bootstrap L={L}"
    print(f"{name:<22} 标准差：效率 {res[:, 0].std():.4f}  传递性 {res[:, 1].std():.4f}  "
          f"入选概率在 0.2–0.8 之间的边占比={unstable:.2f}  前 5 枢纽平均重合={hov:.2f}")
    if L == 25:
        inc25 = inc

# 指标的均值 vs 均值网络（按入选概率取前 15% 的“共识网络”）的指标
cons = np.zeros((N, N), int)
top = np.argsort(-inc25)[:n_keep]
cons[iu[0][top], iu[1][top]] = 1
Gc = nx.from_numpy_array(cons + cons.T)
print(f"bootstrap 指标均值：效率={res[:, 0].mean():.3f} 传递性={res[:, 1].mean():.3f}；"
      f"共识网络的指标：效率={nx.global_efficiency(Gc):.3f} 传递性={nx.transitivity(Gc):.3f}")

# 作图：全局效率的标准差（真值 vs 三种 bootstrap）；块 bootstrap（L=25）下的边入选概率分布
import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 2, figsize=(10, 4))
ax[0].bar(["true sampling\n(200 sims)", "naive\nbootstrap", "block\nL=10", "block\nL=25"],
          [truth[:, 0].std()] + sd_boot, color=["C3", "0.6", "C0", "C0"])
ax[0].set_ylabel("SD of global efficiency")
ax[0].set_title("Naive bootstrap underestimates uncertainty", fontsize=10)
ax[1].hist(inc25, bins=20, color="C0", edgecolor="white")
ax[1].set_xlabel("edge inclusion probability (block bootstrap, L=25)"); ax[1].set_ylabel("number of edges")
ax[1].set_yscale("log")
ax[1].set_title("Edges near the threshold flip in and out", fontsize=10)
plt.tight_layout(); plt.show()

# %% 示例：样本量与功效——单条边的解析计算、整网边恢复的模拟，以及测量信度造成的衰减
# (1) Fisher z 近似：检测真实相关 ρ（双侧 α）达到功效 1-β 所需 n ≈ ((z_{1-α/2}+z_{1-β}) / artanh ρ)² + 3；
#     同时给出对 m 条边做 Bonferroni 校正时的 n，并用模拟核对 m=1 时的功效。
# (2) 由已知稀疏精度矩阵（p=15 个变量）生成数据，对每个偏相关做 Fisher z 检验（标准误 1/sqrt(n-(p-2)-3)），
#     BH 校正后统计边的灵敏度、错误发现比例，以及强度中心性与真值的秩相关，观察它们随 n 的变化。
# (3) 信度衰减：观测相关 ≈ 真实相关 × sqrt(信度_x × 信度_y)（Spearman, 1904），低信度会让所需样本量成倍增加。
# 解读：这些都是在模型假设成立时的乐观估计；真实研究应按自己的网络结构与估计方法做模拟功效分析。
import numpy as np
from scipy import stats

def n_required(rho, alpha=0.05, power=0.8, m=1):
    za = stats.norm.ppf(1 - alpha / (2 * m))
    zb = stats.norm.ppf(power)
    return int(np.ceil(((za + zb) / np.arctanh(rho)) ** 2 + 3))

print("单条边：检测 ρ 所需样本量（α=0.05 双侧，功效 0.8）")
for rho in (0.1, 0.2, 0.3, 0.5):
    print(f"  ρ={rho}: 单次检验 n={n_required(rho):5d}；"
          f"对 4005 条边 Bonferroni 校正 n={n_required(rho, m=4005):5d}")

rng = np.random.default_rng(41)
rho, n = 0.3, n_required(0.3)
cov = [[1, rho], [rho, 1]]
hits = 0
for _ in range(4000):
    xy = rng.multivariate_normal([0, 0], cov, size=n)
    hits += stats.pearsonr(xy[:, 0], xy[:, 1]).pvalue < 0.05
print(f"模拟核对：ρ=0.3, n={n} 时实际功效={hits / 4000:.3f}")

# (2) 整网边恢复
p = 15
K = np.eye(p)
edges = [(i, i + 1) for i in range(p - 1)] + [(0, 7), (3, 11), (5, 13)]
for i, j in edges:
    K[i, j] = K[j, i] = -0.25
assert np.all(np.linalg.eigvalsh(K) > 0)
Sigma = np.linalg.inv(K)
d = np.sqrt(np.diag(K)); true_pc = -K / np.outer(d, d); np.fill_diagonal(true_pc, 0)
iu = np.triu_indices(p, 1)
truth = true_pc[iu] != 0
true_strength = np.abs(true_pc).sum(axis=1)
print(f"\n整网：p={p} 个变量，{truth.sum()} 条真实边，真实偏相关约 {np.abs(true_pc[iu][truth]).mean():.2f}")
curve = []                                     # 保存整网恢复结果用于作图
for n in (50, 100, 200, 500, 1000):
    sens, fdp, rs = [], [], []
    for _ in range(200):
        X = rng.multivariate_normal(np.zeros(p), Sigma, size=n)
        P = np.linalg.inv(np.cov(X, rowvar=False))
        dd = np.sqrt(np.diag(P)); W = -P / np.outer(dd, dd); np.fill_diagonal(W, 0)
        z = np.arctanh(W[iu]) * np.sqrt(n - (p - 2) - 3)
        pv = 2 * stats.norm.sf(np.abs(z))
        # BH
        o = np.argsort(pv); ok = pv[o] <= 0.05 * np.arange(1, len(pv) + 1) / len(pv)
        k = ok.nonzero()[0].max() + 1 if ok.any() else 0
        sig = np.zeros(len(pv), bool); sig[o[:k]] = True
        sens.append(sig[truth].mean())
        fdp.append((sig & ~truth).sum() / max(sig.sum(), 1))
        rs.append(stats.spearmanr(np.abs(W).sum(axis=1), true_strength)[0])
    print(f"  n={n:5d}: 边灵敏度={np.mean(sens):.2f}  错误发现比例={np.mean(fdp):.3f}  "
          f"强度中心性与真值的秩相关 中位数={np.median(rs):.2f}")
    curve.append((n, np.mean(sens), np.mean(fdp), np.median(rs)))

# (3) 信度衰减
print("\n信度衰减：真实相关 0.3")
for rel in (1.0, 0.8, 0.6, 0.4):
    r_obs = 0.3 * np.sqrt(rel * rel)
    print(f"  两端信度均为 {rel}: 期望观测相关={r_obs:.3f}，所需 n={n_required(r_obs)}")

# 作图：所需样本量随真实相关变化（单次检验 vs Bonferroni）；整网边恢复随 n 的变化
import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 2, figsize=(10, 4))
rhos = np.linspace(0.05, 0.6, 50)
ax[0].plot(rhos, [n_required(r_) for r_ in rhos], "-", label="single test")
ax[0].plot(rhos, [n_required(r_, m=4005) for r_ in rhos], "--", label="Bonferroni, 4005 edges")
ax[0].set_yscale("log"); ax[0].set_xlabel("true correlation rho"); ax[0].set_ylabel("n for 80% power")
ax[0].set_title("Weak edges need very large samples", fontsize=10); ax[0].legend(fontsize=8)
cv = np.array(curve)
ax[1].plot(cv[:, 0], cv[:, 1], "o-", label="edge sensitivity")
ax[1].plot(cv[:, 0], cv[:, 2], "s--", label="false discovery proportion")
ax[1].plot(cv[:, 0], cv[:, 3], "^:", label="strength rank corr. (median)")
ax[1].set_xscale("log"); ax[1].set_xlabel("sample size n"); ax[1].set_ylim(-0.05, 1.05)
ax[1].set_title("Network recovery, p = 15, partial corr. 0.25", fontsize=10); ax[1].legend(fontsize=8)
plt.tight_layout(); plt.show()

# %% 示例：比较两张网络——已知节点对应的距离、谱距离、WL 图核，以及基于距离的置换检验
# 生成 4 类网络（N=100、边数相同）：ER、Watts–Strogatz、Barabási–Albert、随机块模型（SBM），每类 6 个实例。
# 距离：(a) Jaccard 边距离（需要节点对应）；(b) 归一化拉普拉斯谱距离（不需要对应）；
#       (c) 度分布的 Jensen–Shannon 散度；(d) Weisfeiler–Lehman（WL）子树特征的余弦距离（一种图核）。
# 用“类内平均距离 / 类间平均距离”衡量每种距离区分网络类型的能力（越小越好）。
# 最后对两组“被试网络”做基于距离的置换检验：统计量 = 组间平均距离 − 组内平均距离。
# 解读：节点无对应时，Jaccard 距离只在 WS 这类“共享格点骨架”的网络之间较小，对同类随机网络接近 1，不适用；谱距离、度分布与 WL 核关注的结构层次不同，
# 应按研究问题选择，并像任何检验统计量一样配合置换或零模型使用。
import numpy as np
import networkx as nx
from collections import Counter
from scipy.spatial.distance import jensenshannon

N, k = 100, 6
m = N * k // 2

def make(kind, s):
    if kind == "ER":
        return nx.gnm_random_graph(N, m, seed=s)
    if kind == "WS":
        return nx.watts_strogatz_graph(N, k, 0.1, seed=s)
    if kind == "BA":
        return nx.barabasi_albert_graph(N, k // 2, seed=s)
    sizes = [25] * 4                                    # SBM：4 个模块，块内连接更密
    pin = 0.17; pout = (2 * m / N - 24 * pin) / 75
    return nx.stochastic_block_model(sizes, [[pin if i == j else pout for j in range(4)] for i in range(4)], seed=s)

def jaccard(G, H):
    a, b = set(map(frozenset, G.edges())), set(map(frozenset, H.edges()))
    return 1 - len(a & b) / len(a | b)

def lap_spec(G):
    return np.sort(np.linalg.eigvalsh(nx.normalized_laplacian_matrix(G).toarray()))

def degree_js(G, H, kmax=60):
    def pk(G):
        c = np.bincount([d for _, d in G.degree()], minlength=kmax + 1)[:kmax + 1]
        return c / c.sum()
    return jensenshannon(pk(G), pk(H))

def wl_features(G, it=2):
    """WL 子树特征：所有节点初始标签相同，第 1 轮标签等价于度，第 2 轮编码“邻居度的多重集”。
    迭代轮数越多特征越细，随机网络之间几乎不再共享特征，距离趋近 1。"""
    G = G.copy()
    nx.set_node_attributes(G, {v: "0" for v in G}, "lab")
    h = nx.weisfeiler_lehman_subgraph_hashes(G, node_attr="lab", iterations=it)
    return Counter(x for hs in h.values() for x in hs)

def wl_dist(fa, fb):
    keys = set(fa) | set(fb)
    a = np.array([fa.get(x, 0) for x in keys], float); b = np.array([fb.get(x, 0) for x in keys], float)
    return 1 - a @ b / np.linalg.norm(a) / np.linalg.norm(b)

kinds = ["ER", "WS", "BA", "SBM"]
graphs = [(kd, make(kd, 10 * i + j)) for i, kd in enumerate(kinds) for j in range(6)]
specs = [lap_spec(G) for _, G in graphs]
wls = [wl_features(G) for _, G in graphs]
n = len(graphs)
D = {name: np.zeros((n, n)) for name in ("Jaccard", "拉普拉斯谱", "度分布JS", "WL核")}
for a in range(n):
    for b in range(a + 1, n):
        Ga, Gb = graphs[a][1], graphs[b][1]
        vals = {"Jaccard": jaccard(Ga, Gb), "拉普拉斯谱": np.linalg.norm(specs[a] - specs[b]),
                "度分布JS": degree_js(Ga, Gb), "WL核": wl_dist(wls[a], wls[b])}
        for name, v in vals.items():
            D[name][a, b] = D[name][b, a] = v

lab = np.array([kd for kd, _ in graphs])
same = (lab[:, None] == lab[None, :]) & ~np.eye(n, dtype=bool)
diff = lab[:, None] != lab[None, :]
print("距离        类内均值  类间均值  类内/类间")
for name, M in D.items():
    print(f"{name:<10} {M[same].mean():8.3f}  {M[diff].mean():8.3f}  {M[same].mean() / M[diff].mean():8.2f}")
print("拉普拉斯谱距离的类间矩阵（行、列为 ER/WS/BA/SBM）：")
blk = np.array([[D['拉普拉斯谱'][np.ix_(lab == x, lab == y)].mean() for y in kinds] for x in kinds])
print(np.round(blk, 2))

# 基于距离的置换检验：两组各 12 个“被试网络”，节点对应已知；B 组模块内连接略强
rng = np.random.default_rng(51)
def subject(pin):
    pout = (2 * m / N - 24 * pin) / 75
    return nx.stochastic_block_model([25] * 4, [[pin if i == j else pout for j in range(4)] for i in range(4)],
                                     seed=int(rng.integers(1e9)))
subs = [subject(0.15) for _ in range(12)] + [subject(0.18) for _ in range(12)]
g = np.r_[np.zeros(12), np.ones(12)].astype(int)
A = np.array([nx.to_numpy_array(G, nodelist=range(N))[np.triu_indices(N, 1)] for G in subs])
Dm = np.array([[np.abs(x - y).sum() for y in A] for x in A])          # 汉明距离（边集合的对称差大小）
def stat(g):
    w = g[:, None] == g[None, :]
    off = ~np.eye(len(g), dtype=bool)
    return Dm[~w].mean() - Dm[w & off].mean()
s0 = stat(g)
null = np.array([stat(rng.permutation(g)) for _ in range(2000)])
print(f"组间−组内平均汉明距离={s0:.1f}，置换 p={(1 + np.sum(null >= s0)) / 2001:.4f}")

# 作图：24 个网络两两之间的拉普拉斯谱距离矩阵；基于距离的置换检验零分布
import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 2, figsize=(10, 4))
im = ax[0].imshow(D["拉普拉斯谱"], cmap="viridis")
ax[0].set_xticks(np.arange(3, n, 6)); ax[0].set_xticklabels(kinds)
ax[0].set_yticks(np.arange(3, n, 6)); ax[0].set_yticklabels(kinds)
fig.colorbar(im, ax=ax[0], label="Laplacian spectral distance")
ax[0].set_title("Spectral distance separates network classes", fontsize=10)
ax[1].hist(null, bins=30, color="0.7", edgecolor="white", label="permutation null")
ax[1].axvline(s0, color="C3", lw=2, label="observed")
ax[1].set_xlabel("between - within mean Hamming distance"); ax[1].set_ylabel("count"); ax[1].legend(fontsize=8)
ax[1].set_title("Distance-based permutation test (SBM groups)", fontsize=10)
plt.tight_layout(); plt.show()
