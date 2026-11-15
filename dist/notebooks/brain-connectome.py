# 依赖：networkx>=3, numpy, scipy, matplotlib
# 数据：numpy 生成的模拟“BOLD”时间序列（模拟数据，仅用于演示方法，不代表真实人脑）。
# 输入格式：N×T 数组，每行是一个脑区（ROI）的平均时间序列，另有长度为 N 的功能系统标签。
# 模拟设定：40 个脑区分属 4 个功能系统（每个 10 个脑区），200 个时间点；
# 每个脑区的信号 = 所属系统的共同波动 + 微弱的全脑共同波动 + 独立噪声；
# 脑区 9 额外接收系统 1 的信号，模拟一个跨系统的连接枢纽。
# 真实数据可用 Nilearn 等工具按图谱提取 ROI 时间序列后，替换 simulate_bold 的输出。
# 后续示例（格兰杰因果、加权指标、含负权模块度、连接组梯度、指纹识别、空间嵌入、病变网络映射）
# 各自在单元内生成模拟数据，设定写在单元开头的注释中；所有单元可独立运行。

# %% 示例：从 ROI 时间序列估计功能连接矩阵
# 用皮尔逊相关得到 40×40 的功能连接矩阵 R，再做 Fisher z 变换（对角线先置 0，避免 artanh(1)=∞）。
# 输出：系统内与系统间的平均相关；热图中应呈现 4 个对角块，对应 4 个模拟功能系统。
# 系统间平均相关略大于 0，来自模拟中的全脑共同波动（类比真实数据中的全局信号）。
import numpy as np
import matplotlib.pyplot as plt

def simulate_bold(n_mod=4, per=10, T=200, seed=0):
    """模拟数据，仅用于演示方法。返回 (时间序列 N×T, 系统标签)。"""
    rng = np.random.default_rng(seed)
    labels = np.repeat(np.arange(n_mod), per)
    sys_sig = rng.standard_normal((n_mod, T))
    glob = rng.standard_normal(T)
    load = rng.uniform(0.4, 1.0, size=n_mod * per)   # 各脑区对本系统的载荷不同
    X = load[:, None] * sys_sig[labels] + 0.3 * glob + rng.standard_normal((n_mod * per, T))
    X[9] += 0.8 * sys_sig[1]                          # 脑区 9：跨系统连接枢纽
    return X, labels

X, labels = simulate_bold()
N = X.shape[0]

R = np.corrcoef(X)                 # 按行计算：每行一个脑区
R0 = R.copy()
np.fill_diagonal(R0, 0)
Z = np.arctanh(R0)                 # Fisher z，组水平统计通常在 z 上进行

same = labels[:, None] == labels[None, :]
off = ~np.eye(N, dtype=bool)
print("系统内平均 r =", round(R[same & off].mean(), 3))
print("系统间平均 r =", round(R[~same].mean(), 3))
print("Fisher z 的取值范围：", round(Z[off].min(), 2), "~", round(Z[off].max(), 2))

plt.imshow(R, cmap="RdBu_r", vmin=-1, vmax=1)
plt.colorbar(label="Pearson r")
plt.title("Simulated functional connectivity matrix")
plt.show()

# %% 示例：比例阈值下网络指标随密度变化
# proportional_threshold 保留 |r| 最大的前 density 比例的边，得到二值无向图。
# 在密度 0.05–0.40 上计算平均聚集系数 C、全局效率 E、连通分量数，并与同边数的 ER 随机图比较。
# 输出解读：E 随密度单调上升；C 先升后降（系统内的强边用完后，新增的是跨系统的弱边）；
# 低密度时网络断成多个分量；C/C_rand 随密度下降。
# 同一个相关矩阵在不同密度下给出不同的“拓扑”，只报告单一密度会使结论依赖于该选择。
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

def simulate_bold(n_mod=4, per=10, T=200, seed=0):
    rng = np.random.default_rng(seed)   # 模拟数据，仅用于演示方法
    labels = np.repeat(np.arange(n_mod), per)
    sys_sig = rng.standard_normal((n_mod, T))
    glob = rng.standard_normal(T)
    load = rng.uniform(0.4, 1.0, size=n_mod * per)
    X = load[:, None] * sys_sig[labels] + 0.3 * glob + rng.standard_normal((n_mod * per, T))
    X[9] += 0.8 * sys_sig[1]
    return X, labels

def proportional_threshold(R, density):
    """保留 |r| 最大的前 density 比例的边，返回含全部 N 个节点的无向图。"""
    N = R.shape[0]
    iu = np.triu_indices(N, k=1)
    w = np.abs(R[iu])
    m = int(round(density * len(w)))
    keep = np.argsort(w)[::-1][:m]
    G = nx.Graph()
    G.add_nodes_from(range(N))
    G.add_edges_from(zip(iu[0][keep], iu[1][keep]))
    return G

X, labels = simulate_bold()
R = np.corrcoef(X)
N = R.shape[0]

rows = []
for d in [0.05, 0.10, 0.15, 0.20, 0.30, 0.40]:
    G = proportional_threshold(R, d)
    Gr = nx.gnm_random_graph(N, G.number_of_edges(), seed=1)
    C, E = nx.average_clustering(G), nx.global_efficiency(G)
    Cr = nx.average_clustering(Gr)
    rows.append((d, C, E, nx.number_connected_components(G), C / max(Cr, 1e-9)))

print("密度   C      E      分量数  C/C_rand")
for d, C, E, nc, ratio in rows:
    print(f"{d:.2f}  {C:.3f}  {E:.3f}  {nc:5d}   {ratio:.2f}")

ds = [r[0] for r in rows]
plt.plot(ds, [r[1] for r in rows], "o-", label="average clustering C")
plt.plot(ds, [r[2] for r in rows], "s-", label="global efficiency E")
plt.xlabel("network density")
plt.legend()
plt.title("Metrics depend on the threshold (simulated data)")
plt.show()

# %% 示例：枢纽排序对阈值的依赖——度与参与系数
# 已知系统标签时，参与系数 P_i = 1 - Σ_s (k_is / k_i)^2，k_is 为节点 i 连到系统 s 的边数。
# 分别在密度 0.10 与 0.30 下列出度最高的 5 个脑区，并查看脑区 9（跨系统枢纽）的参与系数排名。
# 输出解读：密度 0.10 时度最高的是系统内载荷大的“省内”脑区，所有边都在系统内，
# 脑区 9 的跨系统边尚未进入网络，P[9] = 0；密度 0.30 时它的度和参与系数都位居前列；
# 两种密度下度排序的 Spearman 相关很低。真实数据中模块标签本身也是估计出来的，
# 因此枢纽结论应在多个密度、多个图谱下检查稳定性。
import numpy as np
import networkx as nx
from scipy.stats import spearmanr

def simulate_bold(n_mod=4, per=10, T=200, seed=0):
    rng = np.random.default_rng(seed)   # 模拟数据，仅用于演示方法
    labels = np.repeat(np.arange(n_mod), per)
    sys_sig = rng.standard_normal((n_mod, T))
    glob = rng.standard_normal(T)
    load = rng.uniform(0.4, 1.0, size=n_mod * per)
    X = load[:, None] * sys_sig[labels] + 0.3 * glob + rng.standard_normal((n_mod * per, T))
    X[9] += 0.8 * sys_sig[1]
    return X, labels

def proportional_threshold(R, density):
    N = R.shape[0]
    iu = np.triu_indices(N, k=1)
    w = np.abs(R[iu])
    m = int(round(density * len(w)))
    keep = np.argsort(w)[::-1][:m]
    G = nx.Graph()
    G.add_nodes_from(range(N))
    G.add_edges_from(zip(iu[0][keep], iu[1][keep]))
    return G

def participation(G, labels):
    """参与系数；度为 0 的节点记为 0。"""
    n_mod = labels.max() + 1
    P = np.zeros(G.number_of_nodes())
    for i in G.nodes():
        k = G.degree(i)
        if k == 0:
            continue
        kis = np.bincount([labels[j] for j in G.neighbors(i)], minlength=n_mod)
        P[i] = 1 - np.sum((kis / k) ** 2)
    return P

X, labels = simulate_bold()
R = np.corrcoef(X)

for d in [0.10, 0.30]:
    G = proportional_threshold(R, d)
    deg = np.array([G.degree(i) for i in G.nodes()])
    top = np.argsort(deg)[::-1][:5]
    P = participation(G, labels)
    rank9 = int((P > P[9]).sum()) + 1
    print(f"密度 {d:.2f}：度最高的 5 个脑区 = {top.tolist()}，度 = {deg[top].tolist()}")
    print(f"  脑区 9 的参与系数 = {P[9]:.2f}，在 40 个脑区中排第 {rank9}（并列计同名次）；"
          f"参与系数 > 0 的脑区共 {int((P > 0).sum())} 个")

deg10 = [d for _, d in proportional_threshold(R, 0.10).degree()]
deg30 = [d for _, d in proportional_threshold(R, 0.30).degree()]
rho, _ = spearmanr(deg10, deg30)
print("两种密度下度排序的 Spearman 相关 =", round(rho, 3))

import matplotlib.pyplot as plt
dens = np.linspace(0.05, 0.40, 8)
P9, Poth = [], []
for d in dens:
    Pd = participation(proportional_threshold(R, d), labels)
    P9.append(Pd[9]); Poth.append(np.median(np.delete(Pd, 9)))
deg10, deg30 = np.array(deg10), np.array(deg30)
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
for m, mk in zip(range(4), "osD^"):
    idx = labels == m
    axes[0].scatter(deg10[idx], deg30[idx], marker=mk, s=50, alpha=0.8, label=f"system {m}")
axes[0].scatter(deg10[9], deg30[9], marker="*", s=300, facecolor="none", edgecolor="crimson", lw=1.5, label="node 9")
axes[0].set(xlabel="Degree at density 0.10", ylabel="Degree at density 0.30",
            title=f"Degree ranks across densities (rho = {rho:.2f})")
axes[0].legend(fontsize=8)
axes[1].plot(dens, P9, "o-", color="crimson", label="node 9 (cross-system)")
axes[1].plot(dens, Poth, "s--", color="gray", label="median of other nodes")
axes[1].set(xlabel="Edge density", ylabel="Participation coefficient", title="Connector role emerges at higher density")
axes[1].legend(fontsize=8)
plt.tight_layout(); plt.show()

# %% 示例：格兰杰因果——神经层面正确，经过区域不同的血流动力学延迟后可能反向
# 模拟两个脑区的“神经”信号：x 驱动 y（y_t 依赖 x_{t-1}），反向耦合为 0。
# granger_F 用最小二乘拟合 p 阶向量自回归，返回 Geweke 形式的 F_{x→y} = ln(受限残差方差 / 完整残差方差)。
# 然后把两路信号分别与峰值时间不同的伽马型血流动力学响应函数（HRF）卷积并降采样，模拟 BOLD：
# 情形 1：两区 HRF 相同；情形 2：被驱动的 y 区 HRF 峰值反而更早（区域间 HRF 差异约 1–2 秒在文献中常见）。
# 输出解读：神经信号上 F_{x→y} 远大于 F_{y→x}；HRF 相同时方向大体保留；
# y 区 HRF 更早时，BOLD 上的“因果方向”可能被削弱甚至反转。数值为模拟结果，仅说明机制。
import numpy as np
from scipy.stats import gamma

def granger_F(src, dst, p=2):
    """Geweke 形式的格兰杰因果量 F_{src→dst} = ln(var_restricted / var_full)。"""
    T = len(dst)
    Y = dst[p:]
    lags_dst = np.column_stack([dst[p - k:T - k] for k in range(1, p + 1)])
    lags_src = np.column_stack([src[p - k:T - k] for k in range(1, p + 1)])
    ones = np.ones((T - p, 1))
    Xr = np.hstack([ones, lags_dst])
    Xf = np.hstack([ones, lags_dst, lags_src])
    rr = Y - Xr @ np.linalg.lstsq(Xr, Y, rcond=None)[0]
    rf = Y - Xf @ np.linalg.lstsq(Xf, Y, rcond=None)[0]
    return np.log(rr.var() / rf.var())

def hrf(t, peak):
    """简化的单伽马 HRF，峰值约在 peak 秒（形状参数 a = peak + 1，尺度 1）。"""
    h = gamma.pdf(t, a=peak + 1, scale=1.0)
    return h / h.sum()

rng = np.random.default_rng(0)
dt, T = 0.1, 60000                       # 神经信号 10 Hz、共 6000 秒（模拟数据）
x = np.zeros(T); y = np.zeros(T)
for t in range(1, T):                    # 一阶自回归神经动力学，x → y，延迟 0.1 s
    x[t] = 0.9 * x[t - 1] + rng.standard_normal()
    y[t] = 0.9 * y[t - 1] + 0.5 * x[t - 1] + rng.standard_normal()

print(f"神经信号（10 Hz）：F_x→y = {granger_F(x, y):.3f}，F_y→x = {granger_F(y, x):.3f}")

th = np.arange(0, 30, dt)
step = int(2.0 / dt)                     # 降采样到 TR = 2 s
Fres = [(granger_F(x, y), granger_F(y, x))]   # 记录各情形的 F 值，供作图
for name, px, py in [("两区 HRF 峰值相同(5 s, 5 s)", 5.0, 5.0),
                     ("y 区 HRF 更早(x: 6 s, y: 4.5 s)", 6.0, 4.5)]:
    bx = np.convolve(x, hrf(th, px))[:T][::step]
    by = np.convolve(y, hrf(th, py))[:T][::step]
    bx = bx + 0.05 * bx.std() * rng.standard_normal(len(bx))   # 少量测量噪声
    by = by + 0.05 * by.std() * rng.standard_normal(len(by))
    fxy, fyx = granger_F(bx, by), granger_F(by, bx)
    verdict = "x→y" if fxy > fyx else "y→x"
    print(f"BOLD（TR=2 s），{name}：F_x→y = {fxy:.3f}，F_y→x = {fyx:.3f}，判定方向 {verdict}")
    Fres.append((fxy, fyx))

import matplotlib.pyplot as plt
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
for pk, ls, lab in [(5.0, "-", "peak 5 s (equal case)"), (6.0, "--", "x region, peak 6 s"), (4.5, ":", "y region, peak 4.5 s")]:
    axes[0].plot(th, hrf(th, pk) / dt, ls, lw=2, label=lab)
axes[0].set(xlabel="Time (s)", ylabel="HRF (a.u.)", title="Regional HRFs used in the simulation")
axes[0].legend(fontsize=8)
Fres = np.array(Fres)
pos = np.arange(3)
axes[1].bar(pos - 0.2, Fres[:, 0], 0.4, color="#4477AA", label="F x->y (true direction)")
axes[1].bar(pos + 0.2, Fres[:, 1], 0.4, color="#CC6677", label="F y->x")
axes[1].set_xticks(pos, ["Neural (10 Hz)", "BOLD, equal HRF", "BOLD, y HRF earlier"], fontsize=9)
axes[1].set(ylabel="Geweke Granger F", title="HRF differences can flip the inferred direction")
axes[1].legend(fontsize=8)
plt.tight_layout(); plt.show()

# %% 示例：加权脑网络指标与权重归一化
# 用模拟的 4 系统功能连接矩阵（只保留正相关）构建加权网络，比较：
# 强度 s_i、Onnela 加权聚集系数（networkx 的 clustering(weight=...) 即此定义，权重先除以最大权重）、
# 加权全局效率（边长取 1/w，Dijkstra 最短路径），以及“对所有权重乘同一常数”后各指标是否改变。
# 输出解读：加权聚集系数对整体缩放不变（已按最大权重归一化）；加权效率随整体缩放成比例变化，
# 因此组间比较加权效率前要决定是否归一化（如除以最大权重或与保持强度的零模型之比），否则“效率差异”可能只是整体 FC 强度差异。
import numpy as np
import networkx as nx

def simulate_fc(n_mod=4, per=10, T=300, seed=0):
    rng = np.random.default_rng(seed)        # 模拟数据，仅用于演示方法
    labels = np.repeat(np.arange(n_mod), per)
    sys_sig = rng.standard_normal((n_mod, T))
    load = rng.uniform(0.4, 1.0, size=n_mod * per)
    X = load[:, None] * sys_sig[labels] + 0.3 * rng.standard_normal(T) + rng.standard_normal((n_mod * per, T))
    return np.corrcoef(X), labels

def weighted_graph(W):
    G = nx.Graph()
    N = W.shape[0]
    G.add_nodes_from(range(N))
    for i in range(N):
        for j in range(i + 1, N):
            if W[i, j] > 0:
                G.add_edge(i, j, weight=W[i, j], length=1.0 / W[i, j])
    return G

def weighted_global_efficiency(G):
    N = G.number_of_nodes()
    tot = 0.0
    for i, dist in nx.all_pairs_dijkstra_path_length(G, weight="length"):
        tot += sum(1.0 / d for j, d in dist.items() if j != i)
    return tot / (N * (N - 1))

R, labels = simulate_fc()
W = np.clip(R, 0, None)                       # 只保留正权（负权需另行处理）
np.fill_diagonal(W, 0)

for scale in [1.0, 0.7]:                      # 0.7：模拟整体 FC 减弱 30% 的“另一组”
    G = weighted_graph(scale * W)
    s = np.array([d for _, d in G.degree(weight="weight")])
    Cw = nx.average_clustering(G, weight="weight")
    Ew = weighted_global_efficiency(G)
    print(f"整体缩放 ×{scale}: 平均强度 = {s.mean():.3f}，加权聚集 = {Cw:.4f}，加权全局效率 = {Ew:.4f}")

G = weighted_graph(W)
s = np.array([d for _, d in G.degree(weight="weight")])
print("强度最高的 5 个节点：", np.argsort(s)[::-1][:5].tolist())
print("提示：权重整体乘 0.7，效率也乘 0.7；聚集系数不变。")

import matplotlib.pyplot as plt
scales = np.linspace(0.4, 1.0, 7)
met = []
for sc in scales:
    Gs = weighted_graph(sc * W)
    met.append([np.mean([d for _, d in Gs.degree(weight="weight")]),
                nx.average_clustering(Gs, weight="weight"), weighted_global_efficiency(Gs)])
met = np.array(met) / np.array(met)[-1]
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
im = axes[0].imshow(W, cmap="Reds", vmin=0)
fig.colorbar(im, ax=axes[0], shrink=0.8, label="weight (positive r)")
axes[0].set(title="Positive-weight FC (sorted by system)", xlabel="Region", ylabel="Region")
for k, (mk, ls, lab) in enumerate([("o", "-", "mean strength"), ("s", "--", "weighted clustering"),
                                   ("^", ":", "weighted global efficiency")]):
    axes[1].plot(scales, met[:, k], marker=mk, ls=ls, label=lab)
axes[1].set(xlabel="Global weight scaling factor", ylabel="Metric / value at scale 1",
            title="Clustering is scale-invariant; efficiency is not")
axes[1].legend(fontsize=8)
plt.tight_layout(); plt.show()

# %% 示例：含负权的模块度与功能角色划分（Guimerà–Amaral 功能制图）
# 对含正负权的相关矩阵，用 Rubinov & Sporns (2011) 的非对称模块度
#   Q* = Q+ − [v−/(v+ + v−)] Q−
# 评价给定划分；再对正权网络计算模块内度 z 分数与参与系数 P，按 Guimerà & Amaral (2005) 的阈值
# （z ≥ 2.5 为枢纽；P 分界 0.30/0.75 用于枢纽）给节点分角色。
# 输出解读：真实系统划分的 Q* 明显高于随机打乱标签的 Q*；模拟中的跨系统节点 9 应有最高的 P。
# 小网络里很少有节点达到 z ≥ 2.5，这是该阈值源自大型网络的缘故，阈值不宜机械套用。
import numpy as np

def simulate_fc(n_mod=4, per=10, T=300, seed=1):
    rng = np.random.default_rng(seed)        # 模拟数据，仅用于演示方法
    labels = np.repeat(np.arange(n_mod), per)
    sys_sig = rng.standard_normal((n_mod, T))
    sys_sig[1] -= 0.6 * sys_sig[0]           # 系统 0 与 1 反相关，产生负权
    load = rng.uniform(0.4, 1.0, size=n_mod * per)
    X = load[:, None] * sys_sig[labels] + rng.standard_normal((n_mod * per, T))
    X[9] += 0.9 * sys_sig[2] + 0.9 * sys_sig[3]   # 节点 9：跨系统连接
    return np.corrcoef(X), labels

def modularity_signed(W, labels):
    """Rubinov & Sporns (2011) 非对称加权模块度 Q*。"""
    Wp, Wn = np.clip(W, 0, None), np.clip(-W, 0, None)
    same = labels[:, None] == labels[None, :]
    def q(A):
        v = A.sum()
        if v == 0:
            return 0.0, 0.0
        k = A.sum(1)
        return ((A - np.outer(k, k) / v) * same).sum() / v, v
    qp, vp = q(Wp)
    qn, vn = q(Wn)
    return qp - vn / (vp + vn) * qn

def roles(W, labels):
    """正权网络的模块内强度 z 分数与参与系数。"""
    A = np.clip(W, 0, None)
    k = A.sum(1)
    M = labels.max() + 1
    kis = np.column_stack([A[:, labels == m].sum(1) for m in range(M)])
    P = 1 - ((kis / k[:, None]) ** 2).sum(1)
    k_in = kis[np.arange(len(labels)), labels]
    z = np.zeros(len(labels))
    for m in range(M):
        idx = labels == m
        z[idx] = (k_in[idx] - k_in[idx].mean()) / (k_in[idx].std() + 1e-12)
    return z, P

R, labels = simulate_fc()
np.fill_diagonal(R, 0)
rng = np.random.default_rng(0)
q_true = modularity_signed(R, labels)
q_perm = [modularity_signed(R, rng.permutation(labels)) for _ in range(200)]
print(f"真实系统划分 Q* = {q_true:.3f}；随机标签 Q* 均值 = {np.mean(q_perm):.3f}，最大 = {np.max(q_perm):.3f}")
print("负权占全部权重绝对值的比例 =", round(np.clip(-R, 0, None).sum() / np.abs(R).sum(), 3))

z, P = roles(R, labels)
print("参与系数最高的 3 个节点：", np.argsort(P)[::-1][:3].tolist(), "P =", np.round(np.sort(P)[::-1][:3], 2).tolist())
print("模块内 z 最高的 3 个节点：", np.argsort(z)[::-1][:3].tolist(), "z =", np.round(np.sort(z)[::-1][:3], 2).tolist())
hub = z >= 2.5
print("z ≥ 2.5 的枢纽数 =", int(hub.sum()), "（40 个节点的小网络中通常为 0）")
for i in np.where(hub)[0]:
    role = "省内枢纽" if P[i] < 0.30 else ("连接枢纽" if P[i] < 0.75 else "交汇枢纽")
    print(f"  节点 {i}: z = {z[i]:.2f}, P = {P[i]:.2f} → {role}")

import matplotlib.pyplot as plt
fig, axes = plt.subplots(1, 2, figsize=(10, 4.2))
vmax = np.abs(R).max()
im = axes[0].imshow(R, cmap="RdBu_r", vmin=-vmax, vmax=vmax)
for b in np.where(np.diff(labels))[0] + 0.5:
    axes[0].axhline(b, color="k", lw=0.6); axes[0].axvline(b, color="k", lw=0.6)
fig.colorbar(im, ax=axes[0], shrink=0.8, label="r")
axes[0].set(title=f"Signed FC: Q* = {q_true:.2f} (null max {np.max(q_perm):.2f})", xlabel="Region", ylabel="Region")
for m, mk in zip(range(4), "osD^"):
    idx = labels == m
    axes[1].scatter(P[idx], z[idx], marker=mk, s=50, alpha=0.8, label=f"system {m}")
axes[1].annotate("node 9", (P[9], z[9]), xytext=(6, 4), textcoords="offset points", color="crimson")
axes[1].axhline(2.5, color="gray", ls="--", lw=1)
for x0 in (0.30, 0.75):
    axes[1].axvline(x0, color="gray", ls=":", lw=1)
axes[1].set(xlabel="Participation coefficient P", ylabel="Within-module z", title="Functional roles (Guimera-Amaral plane)")
axes[1].legend(fontsize=8)
plt.tight_layout(); plt.show()

# %% 示例：连接组梯度——扩散映射嵌入
# 模拟 60 个脑区沿一条隐藏的“感觉–联合”轴 h ∈ [0,1] 排列，FC 随 |h_i − h_j| 衰减，并加噪声。
# 按常见做法：每行只保留最强 10% 的连接，计算行向量的余弦相似度作为亲和矩阵 K，
# 做 α = 0.5 的扩散映射：先 K_α = D^{-α} K D^{-α}，再行归一化为马尔可夫矩阵，取非平凡特征向量。
# 输出解读：第一梯度与隐藏轴 h 的 Spearman 相关绝对值接近 1（梯度符号任意）；
# 第二梯度与隐藏轴的关系弱得多（它捕捉的是与第一梯度正交的次要变化）。梯度描述的是“连接模式的相似性”沿皮层的连续变化，而不是离散模块。
import numpy as np
from scipy.stats import spearmanr

rng = np.random.default_rng(3)                # 模拟数据，仅用于演示方法
N, T = 60, 400
h = np.sort(rng.uniform(0, 1, N))             # 隐藏的层级位置
C = np.exp(-np.abs(h[:, None] - h[None, :]) / 0.2)       # 真实协方差随层级距离衰减
L = np.linalg.cholesky(C + 1e-6 * np.eye(N))
X = L @ rng.standard_normal((N, T)) + 0.5 * rng.standard_normal((N, T))
R = np.corrcoef(X)
np.fill_diagonal(R, 0)

def diffusion_map(R, top=0.10, alpha=0.5, n_comp=3):
    A = R.copy()
    thr = np.quantile(A, 1 - top, axis=1, keepdims=True)
    A[A < thr] = 0                            # 每行保留最强 10%
    norms = np.linalg.norm(A, axis=1, keepdims=True)
    K = (A @ A.T) / (norms @ norms.T)         # 余弦相似度
    K = np.clip(K, 0, None)
    d = K.sum(1)
    Ka = K / np.outer(d ** alpha, d ** alpha)
    da = Ka.sum(1)
    S = Ka / np.sqrt(np.outer(da, da))        # 对称化，便于求特征分解
    vals, vecs = np.linalg.eigh(S)
    order = np.argsort(vals)[::-1]
    vals, vecs = vals[order], vecs[:, order]
    psi = vecs / vecs[:, [0]]                 # 还原为马尔可夫矩阵的右特征向量
    lam = vals[1:n_comp + 1]
    return psi[:, 1:n_comp + 1] * (lam / (1 - lam)), lam

grads, lam = diffusion_map(R)
rho1, _ = spearmanr(grads[:, 0], h)
rho2, _ = spearmanr(grads[:, 1], h)
print(f"梯度 1 与隐藏轴的 Spearman |ρ| = {abs(rho1):.3f}")
print(f"梯度 2 与隐藏轴的 Spearman |ρ| = {abs(rho2):.3f}")
print("前 3 个非平凡特征值：", np.round(lam, 3).tolist())

import matplotlib.pyplot as plt
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
axes[0].scatter(h, grads[:, 0], c=h, cmap="viridis", s=50, edgecolor="k", lw=0.3)
axes[0].set(xlabel="Hidden hierarchy position h", ylabel="Gradient 1",
            title=f"Gradient 1 recovers the hidden axis (|rho| = {abs(rho1):.2f})")
sc = axes[1].scatter(grads[:, 0], grads[:, 1], c=h, cmap="viridis", s=50, edgecolor="k", lw=0.3)
fig.colorbar(sc, ax=axes[1], label="h")
axes[1].set(xlabel="Gradient 1", ylabel="Gradient 2", title="Regions in gradient space")
plt.tight_layout(); plt.show()

# %% 示例：功能连接指纹识别与差异可识别性
# 模拟 50 名被试、各两次扫描（session 1/2）。每人的 FC = 群体共同模式 + 个体特异模式 + 扫描噪声。
# 识别：对 session 2 的每个人，在 session 1 的“数据库”中找边向量相关最高的人，命中即识别正确（Finn 等, 2015 的思路）。
# 差异可识别性 I_diff = 同一人跨扫描相关的均值 − 不同人之间相关的均值（Amico & Goñi, 2018）。
# 输出解读：个体特异成分越强、使用的边越多，识别率和 I_diff 越高；
# 只用少量边或扫描噪声大（扫描时间短）时识别率下降。识别率高说明个体差异稳定，不等于这些差异与行为有关。
import numpy as np

rng = np.random.default_rng(7)                # 模拟数据，仅用于演示方法
N_sub, n_edge = 50, 2000
group = rng.standard_normal(n_edge)

def simulate(indiv_sd, noise_sd):
    indiv = indiv_sd * rng.standard_normal((N_sub, n_edge))
    s1 = group + indiv + noise_sd * rng.standard_normal((N_sub, n_edge))
    s2 = group + indiv + noise_sd * rng.standard_normal((N_sub, n_edge))
    return s1, s2

def identify(s1, s2, edges):
    a = s1[:, edges]; b = s2[:, edges]
    a = (a - a.mean(1, keepdims=True)) / a.std(1, keepdims=True)
    b = (b - b.mean(1, keepdims=True)) / b.std(1, keepdims=True)
    Cm = b @ a.T / len(edges)                 # 行：目标被试；列：数据库被试
    acc = np.mean(Cm.argmax(1) == np.arange(N_sub))
    i_self = np.mean(np.diag(Cm))
    i_other = (Cm.sum() - np.trace(Cm)) / (N_sub * (N_sub - 1))
    return acc, i_self - i_other

print("个体成分SD  扫描噪声SD  使用边数  识别率  I_diff")
acc_list = []                                 # 记录识别率，供作图
for indiv_sd, noise_sd in [(0.3, 0.5), (0.3, 1.5), (0.1, 1.5)]:
    s1, s2 = simulate(indiv_sd, noise_sd)
    for m in [50, 2000]:
        edges = rng.choice(n_edge, m, replace=False)
        acc, idiff = identify(s1, s2, edges)
        acc_list.append(acc)
        print(f"   {indiv_sd:.1f}        {noise_sd:.1f}       {m:5d}    {acc:.2f}   {idiff:.3f}")

import matplotlib.pyplot as plt
s1, s2 = simulate(0.3, 0.5)                   # 另抽一组数据画识别矩阵（全部边）
a = (s1 - s1.mean(1, keepdims=True)) / s1.std(1, keepdims=True)
b = (s2 - s2.mean(1, keepdims=True)) / s2.std(1, keepdims=True)
Cm = b @ a.T / n_edge
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
im = axes[0].imshow(Cm, cmap="viridis")
fig.colorbar(im, ax=axes[0], shrink=0.8, label="r")
axes[0].set(xlabel="Subject, session 1 (database)", ylabel="Subject, session 2 (target)",
            title="Identification matrix (indiv SD 0.3, noise 0.5)")
acc_arr = np.array(acc_list).reshape(3, 2)
pos = np.arange(3)
axes[1].bar(pos - 0.2, acc_arr[:, 0], 0.4, color="#BBBBBB", label="50 edges")
axes[1].bar(pos + 0.2, acc_arr[:, 1], 0.4, color="#4477AA", label="2000 edges")
axes[1].set_xticks(pos, ["indiv 0.3\nnoise 0.5", "indiv 0.3\nnoise 1.5", "indiv 0.1\nnoise 1.5"])
axes[1].set(ylabel="Identification accuracy", ylim=(0, 1.05), title="More edges and less noise improve identification")
axes[1].legend(fontsize=8)
plt.tight_layout(); plt.show()

# %% 示例：空间嵌入与布线代价——距离惩罚生成模型 vs 度保持随机化
# 在单位立方体内随机放置 80 个“脑区”，按 P(i~j) ∝ exp(−d_ij/λ) 生成空间网络（布线倾向短程）。
# 比较三者的总布线长度 Σ d_ij 与平均聚集系数：空间网络、同度序列的随机重连网络、同边数 ER 网络。
# 输出解读：空间网络的布线长度远低于两种随机网络，聚集系数则更高——
# 仅凭“节省布线”就能产生高聚集与模块化，因此用不保留空间信息的零模型检验脑网络的“小世界”会高估其特殊性。
import numpy as np
import networkx as nx

rng = np.random.default_rng(11)               # 模拟数据，仅用于演示方法
N, m_target, lam = 80, 320, 0.15
pos = rng.uniform(0, 1, (N, 3))
D = np.linalg.norm(pos[:, None] - pos[None, :], axis=2)
iu = np.triu_indices(N, 1)
p = np.exp(-D[iu] / lam)
p /= p.sum()
chosen = rng.choice(len(p), m_target, replace=False, p=p)
G = nx.Graph()
G.add_nodes_from(range(N))
G.add_edges_from(zip(iu[0][chosen], iu[1][chosen]))

def wiring(G):
    return sum(D[u, v] for u, v in G.edges())

Gr = G.copy()
nx.double_edge_swap(Gr, nswap=10 * G.number_of_edges(), max_tries=10 ** 6, seed=1)
Ge = nx.gnm_random_graph(N, G.number_of_edges(), seed=2)
for name, H in [("空间网络", G), ("度保持重连", Gr), ("ER 随机网络", Ge)]:
    print(f"{name:8s}: 边数 = {H.number_of_edges()}, 总布线长度 = {wiring(H):7.1f}, "
          f"平均聚集系数 = {nx.average_clustering(H):.3f}")

lens = np.array([D[u, v] for u, v in G.edges()])
print("空间网络中边长的中位数 =", round(float(np.median(lens)), 3),
      "；全部节点对距离的中位数 =", round(float(np.median(D[iu])), 3))

import matplotlib.pyplot as plt
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
for u, v in G.edges():
    axes[0].plot(pos[[u, v], 0], pos[[u, v], 1], color="gray", lw=0.5, alpha=0.6)
axes[0].scatter(pos[:, 0], pos[:, 1], s=60, c=pos[:, 2], cmap="viridis", edgecolor="k", lw=0.3, zorder=3)
axes[0].set(xlabel="x", ylabel="y", title="Distance-penalised network (x-y projection)", aspect="equal")
bins = np.linspace(0, D.max(), 30)
for H, ls, lab in [(G, "-", "spatial model"), (Gr, "--", "degree-preserving rewired"), (Ge, ":", "ER random")]:
    axes[1].hist([D[u, v] for u, v in H.edges()], bins=bins, histtype="step", ls=ls, lw=2, label=lab)
axes[1].set(xlabel="Edge length (Euclidean)", ylabel="Number of edges", title="Spatial wiring favours short edges")
axes[1].legend(fontsize=8)
plt.tight_layout(); plt.show()

# %% 示例：病变网络映射（LNM）的原理与特异性检验
# 用模拟的“规范连接组”：100 个脑区，FC 由少数几个共享成分 + 噪声产生，其中第 0 个成分方差最大（全脑主轴）。
# 设 A 组 12 个“病灶”位置各不相同，但都与目标区 T 有较强 FC；B 组为 12 个随机位置的病灶。
# LNM：取每个病灶区与全脑的 FC 向量（病灶网络），二值化（|r| 大于阈值）后叠加，得到重叠图。
# 输出解读：A 组的重叠图在目标区 T 处排名第一，置换检验显著；但随机病灶也覆盖了目标区的大部分，
# 而且两组的平均病灶网络与 FC 第一主成分的相关同样高——叠加 FC 行向量会反复取样同一个连接组的主轴，
# 这正是 van den Heuvel 等（2026）对 LNM 特异性的质疑。
# 因此必须与对照病灶组比较（特异性检验），而不只报告重叠峰。
import numpy as np

rng = np.random.default_rng(5)                # 模拟数据，仅用于演示方法
N, T, K = 100, 600, 5
load = rng.standard_normal((N, K)) * np.array([1.0, 0.9, 0.9, 0.7, 0.7])
load[:, 0] = np.abs(load[:, 0]) + 0.3           # 第 0 个成分：全脑同号的主轴（类似全局信号/主梯度）
X = load @ rng.standard_normal((K, T)) + rng.standard_normal((N, T))
R = np.corrcoef(X)
np.fill_diagonal(R, 0)
target = 42

cand = np.argsort(R[target])[::-1]
lesions_A = cand[:12]                          # 与目标区 FC 最强的 12 个区域作为“症状组”病灶
lesions_B = rng.choice(np.setdiff1d(np.arange(N), [target]), 12, replace=False)

def overlap(lesions, thr=0.25):
    return (np.abs(R[lesions]) > thr).sum(0)

ovA, ovB = overlap(lesions_A), overlap(lesions_B)
rankA = int((ovA > ovA[target]).sum()) + 1
rankB = int((ovB > ovB[target]).sum()) + 1
print(f"症状组：目标区 {target} 被 {ovA[target]}/12 个病灶网络覆盖，在 {N} 个区域中排第 {rankA}")
print(f"随机组：目标区被 {ovB[target]}/12 个病灶网络覆盖，排第 {rankB}")
print("两组重叠图之间的相关 =", round(np.corrcoef(ovA, ovB)[0, 1], 3))

w, V = np.linalg.eigh(R)
pc1 = V[:, -1]
mapA = R[lesions_A].mean(0)
mapB = R[lesions_B].mean(0)
print("症状组平均病灶网络与 FC 第一主成分的 |相关| =", round(abs(np.corrcoef(mapA, pc1)[0, 1]), 3))
print("随机组平均病灶网络与 FC 第一主成分的 |相关| =", round(abs(np.corrcoef(mapB, pc1)[0, 1]), 3))
# 特异性检验：在目标区上，症状组覆盖数是否超过 1000 组随机病灶的分布
null = np.array([overlap(rng.choice(np.setdiff1d(np.arange(N), [target]), 12, replace=False))[target]
                 for _ in range(1000)])
print("目标区覆盖数的置换 p 值 =", round((np.sum(null >= ovA[target]) + 1) / 1001, 4))

import matplotlib.pyplot as plt
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
axes[0].scatter(ovB, ovA, s=40, color="gray", alpha=0.5, label="regions")
axes[0].scatter(ovB[target], ovA[target], s=200, marker="*", color="crimson", label=f"target region {target}")
axes[0].set(xlabel="Overlap count, random lesions", ylabel="Overlap count, symptom lesions",
            title=f"Symptom vs random overlap maps (r = {np.corrcoef(ovA, ovB)[0, 1]:.2f})")
axes[0].legend(fontsize=8)
axes[1].hist(null, bins=np.arange(-0.5, 13.5), color="#BBBBBB", edgecolor="k", lw=0.5, label="random lesion sets")
axes[1].axvline(ovA[target], color="crimson", lw=2, label="symptom lesion set")
axes[1].set(xlabel="Lesion networks covering the target", ylabel="Count (1000 permutations)",
            title="Specificity test at the target region")
axes[1].legend(fontsize=8)
plt.tight_layout(); plt.show()
