# 依赖：networkx>=3, numpy, scipy, matplotlib
# 数据：numpy 生成的模拟“BOLD”信号（模拟数据，仅用于演示方法，不代表真实 fMRI）。
# 输入格式：C×T 数组，每行是一个通道（脑区）的时间序列。
# 模拟信号经过一阶自回归（AR(1)，系数 0.8）平滑，以模仿真实 BOLD 低频、强自相关的特性。
# 真实数据可替换为按图谱提取、完成预处理的 ROI 时间序列。

# %% 示例：滑动窗口相关
# 生成两组两通道信号，各 600 个时间点：A（平稳）全程真实相关 0.3；
# B（切换）前 300 点真实相关 0.7、后 300 点真实相关 0。sliding_corr 返回每个窗口的相关系数。
# 输出解读：B 在中点附近明显下降；A 的真实相关恒定，窗口相关却同样明显起伏——
# 有限窗口的采样变异本身就会产生“波动”，起伏不能直接说明连接在变化。
import numpy as np
import matplotlib.pyplot as plt
from numpy.lib.stride_tricks import sliding_window_view

def ar1_smooth(e, phi=0.8):
    """一阶自回归平滑，模仿 BOLD 的自相关（模拟数据，仅用于演示方法）。"""
    out = np.zeros_like(e)
    for t in range(1, e.shape[-1]):
        out[..., t] = phi * out[..., t - 1] + e[..., t]
    return out

def correlated_pair(rho, T, rng):
    z = rng.standard_normal((2, T))
    return ar1_smooth(np.vstack([z[0], rho * z[0] + np.sqrt(1 - rho ** 2) * z[1]]))

def sliding_corr(x, y, w, step=1):
    """窗长 w、步长 step 的滑动窗口皮尔逊相关（矩形窗，向量化实现）。"""
    xw = sliding_window_view(x, w)[::step]
    yw = sliding_window_view(y, w)[::step]
    xc = xw - xw.mean(axis=1, keepdims=True)
    yc = yw - yw.mean(axis=1, keepdims=True)
    return (xc * yc).sum(1) / np.sqrt((xc ** 2).sum(1) * (yc ** 2).sum(1))

rng = np.random.default_rng(1)
A = correlated_pair(0.3, 600, rng)
B = np.hstack([correlated_pair(0.7, 300, rng), correlated_pair(0.0, 300, rng)])

w = 40
rA = sliding_corr(A[0], A[1], w)
rB = sliding_corr(B[0], B[1], w)
print(f"A（平稳 0.3）：窗口相关范围 {rA.min():.2f} ~ {rA.max():.2f}，标准差 {rA.std():.2f}")
print(f"B（切换）：前 200 个窗口均值 {rB[:200].mean():.2f}，后 200 个窗口均值 {rB[-200:].mean():.2f}")

plt.plot(rA, label="A: true r = 0.3 (stationary)")
plt.plot(rB, label="B: true r 0.7 -> 0")
plt.axhline(0.3, ls="--", c="gray")
plt.xlabel("window start")
plt.ylabel("windowed correlation")
plt.legend()
plt.title(f"Sliding-window correlation (w = {w}, simulated data)")
plt.show()

# %% 示例：窗长的权衡与相位随机化零模型
# (a) 对平稳信号 A，比较窗长 20、40、80、160 下窗口相关的标准差：窗越短，波动越大。
# (b) 多元相位随机化：两个通道乘以同一组随机相位，保留各自功率谱和静态相关、破坏非平稳结构；
#     以“窗口相关的标准差”为检验统计量，用 200 组替代数据构造零分布并给出经验 p 值。
# 输出解读：A 的观测值不超出零分布（没有超出平稳预期的“动态”）；B 明显超出。
# 拒绝零假设只说明偏离了“平稳、线性、高斯”，真实数据中还需排除头动和觉醒水平等来源。
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

def ar1_smooth(e, phi=0.8):
    out = np.zeros_like(e)
    for t in range(1, e.shape[-1]):
        out[..., t] = phi * out[..., t - 1] + e[..., t]
    return out

def correlated_pair(rho, T, rng):
    z = rng.standard_normal((2, T))
    return ar1_smooth(np.vstack([z[0], rho * z[0] + np.sqrt(1 - rho ** 2) * z[1]]))

def sliding_corr(x, y, w, step=1):
    xw = sliding_window_view(x, w)[::step]
    yw = sliding_window_view(y, w)[::step]
    xc = xw - xw.mean(axis=1, keepdims=True)
    yc = yw - yw.mean(axis=1, keepdims=True)
    return (xc * yc).sum(1) / np.sqrt((xc ** 2).sum(1) * (yc ** 2).sum(1))

def phase_randomize(X, rng):
    """多元相位随机化替代数据：所有通道共用同一组随机相位。"""
    T = X.shape[1]
    F = np.fft.rfft(X, axis=1)
    phi = rng.uniform(0, 2 * np.pi, F.shape[1])
    phi[0] = 0                     # 直流分量相位不变（保留均值）
    if T % 2 == 0:
        phi[-1] = 0                # 偶数长度时奈奎斯特频率相位不变，保证逆变换为实数
    return np.fft.irfft(F * np.exp(1j * phi), n=T, axis=1)

rng = np.random.default_rng(1)
A = correlated_pair(0.3, 600, rng)   # 模拟数据，仅用于演示方法
B = np.hstack([correlated_pair(0.7, 300, rng), correlated_pair(0.0, 300, rng)])

for w in [20, 40, 80, 160]:
    print(f"窗长 {w:3d}：A 的窗口相关标准差 = {sliding_corr(A[0], A[1], w).std():.3f}")

w, n_surr = 40, 200
null_res = []                        # 记录观测值与零分布，供作图
for name, X in [("A 平稳", A), ("B 切换", B)]:
    obs = sliding_corr(X[0], X[1], w).std()
    null = np.array([sliding_corr(*phase_randomize(X, rng), w).std() for _ in range(n_surr)])
    p = (np.sum(null >= obs) + 1) / (n_surr + 1)
    print(f"{name}：观测标准差 {obs:.3f}，零分布 95% 分位 {np.quantile(null, 0.95):.3f}，p ≈ {p:.3f}")
    null_res.append((obs, null))

import matplotlib.pyplot as plt
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
for ww, ls in [(20, "-"), (160, "--")]:
    r = sliding_corr(A[0], A[1], ww)
    axes[0].plot(np.arange(len(r)) + ww // 2, r, ls, lw=1.2, label=f"window {ww}")
axes[0].axhline(np.corrcoef(A)[0, 1], color="k", lw=0.8, ls=":", label="static r")
axes[0].set(xlabel="Time (window centre)", ylabel="Windowed r", title="Stationary pair: short windows fluctuate more")
axes[0].legend(fontsize=8)
for (obs, null), lab, col in zip(null_res, ["A stationary", "B switching"], ["#4477AA", "#CC6677"]):
    axes[1].hist(null, bins=25, alpha=0.5, color=col, label=f"{lab}: surrogates")
    axes[1].axvline(obs, color=col, lw=2, ls="--", label=f"{lab}: observed")
axes[1].set(xlabel="SD of windowed r (w = 40)", ylabel="Count", title="Phase-randomised null distributions")
axes[1].legend(fontsize=8)
plt.tight_layout(); plt.show()

# %% 示例：从窗口相关矩阵到“连接状态”（k-means）
# 模拟 6 个脑区、900 个时间点，隐藏状态按 S1 → S2 → S1 → S2 交替（段长 250/200/250/200）：
# S1 中脑区 0–2、3–5 各自共享潜在因子；S2 中脑区 0 与 3、1 与 4、2 与 5 两两共享因子。
# 每个窗口取相关矩阵上三角拉平成 15 维向量，用 k-means 聚类，计算与真实状态的一致率和平均停留时间。
# 输出解读：k = 2 能较好地恢复状态，交界处的窗口混合两种模式；改用 k = 4 时算法同样给出 4 个“状态”——
# 聚类数需要独立的依据（敏感性分析、替代数据比较）。
import numpy as np
from scipy.cluster.vq import kmeans2

def ar1_smooth(e, phi=0.8):
    out = np.zeros_like(e)
    for t in range(1, e.shape[-1]):
        out[..., t] = phi * out[..., t - 1] + e[..., t]
    return out

def segment(state, T, rng):
    """模拟数据，仅用于演示方法：用潜在因子生成指定连接模式。"""
    f = rng.standard_normal((3, T))
    X = rng.standard_normal((6, T))
    groups = [[0, 1, 2], [3, 4, 5]] if state == 0 else [[0, 3], [1, 4], [2, 5]]
    for g, members in enumerate(groups):
        for m in members:
            X[m] += 1.2 * f[g]
    return ar1_smooth(X)

def dwell(labels):
    """平均停留时间：连续处于同一状态的平均窗口数。"""
    runs, cur = [], 1
    for a, b in zip(labels[:-1], labels[1:]):
        if a == b:
            cur += 1
        else:
            runs.append(cur)
            cur = 1
    runs.append(cur)
    return np.mean(runs)

rng = np.random.default_rng(3)
lengths, states = [250, 200, 250, 200], [0, 1, 0, 1]
X = np.hstack([segment(s, L, rng) for s, L in zip(states, lengths)])
truth_t = np.concatenate([[s] * L for s, L in zip(states, lengths)])

w, step = 40, 5
iu = np.triu_indices(6, k=1)
starts = list(range(0, X.shape[1] - w + 1, step))
V = np.array([np.corrcoef(X[:, t:t + w])[iu] for t in starts])            # (窗口数, 15)
truth_w = np.array([np.round(truth_t[t:t + w].mean()) for t in starts])   # 以窗口内多数状态为真值
print("窗口数 =", V.shape[0], "；每个窗口的特征维数 =", V.shape[1])

for k in [2, 4]:
    _, lab = kmeans2(V, k, seed=0, minit="++")
    if k == 2:
        acc = max(np.mean(lab == truth_w), np.mean(lab != truth_w))   # 聚类标签与真值的对应关系任意
        print(f"k = 2：与真实状态一致率 = {acc:.2f}，平均停留 = {dwell(lab):.1f} 个窗口")
    else:
        print(f"k = 4：各“状态”窗口数 = {np.bincount(lab, minlength=4).tolist()}，"
              f"平均停留 = {dwell(lab):.1f} 个窗口")

import matplotlib.pyplot as plt
cen2, lab2 = kmeans2(V, 2, seed=0, minit="++")     # 与上面 k = 2 相同的设置，重新取出中心
if np.mean(lab2 == truth_w) < 0.5:
    lab2, cen2 = 1 - lab2, cen2[::-1]
fig, axes = plt.subplots(1, 3, figsize=(11, 3.6), gridspec_kw={"width_ratios": [2.2, 1, 1]})
tw = np.array(starts) + w / 2
axes[0].step(tw, truth_w + 0.04, where="mid", color="k", lw=2, label="true state")
axes[0].step(tw, lab2 - 0.04, where="mid", color="#CC6677", lw=1.2, ls="--", label="k-means (k = 2)")
axes[0].set(yticks=[0, 1], yticklabels=["S1", "S2"], ylim=(-0.3, 1.3), xlabel="Time (window centre)",
            title="Recovered state sequence")
axes[0].legend(fontsize=8, loc="center right")
for c in range(2):
    M = np.eye(6); M[iu] = cen2[c]; M = M + np.triu(M, 1).T
    im = axes[c + 1].imshow(M, cmap="RdBu_r", vmin=-1, vmax=1)
    axes[c + 1].set(title=f"Centroid S{c + 1}", xticks=range(6), yticks=range(6))
fig.colorbar(im, ax=axes[2], shrink=0.8, label="r")
plt.tight_layout(); plt.show()

# %% 示例：相位同步与主导特征向量（LEiDA 思路）
# 对窄带信号做希尔伯特变换得到瞬时相位 θ_i(t)，逐时间点构造相位一致性矩阵 P_ij(t) = cos(θ_i − θ_j)。
# P(t) 的秩不超过 2，取其主导特征向量 v1(t) 即可概括该时刻的相位结构，再对 v1(t) 做 k-means 得到状态。
# 模拟：8 个“脑区”，前半段 0–4 与 5–7 两组反相，后半段全部同相（模拟数据，仅用于演示方法）。
# 输出解读：主导特征向量的符号直接给出“谁和谁同相”；聚类标签在中点附近切换。
# 注意：瞬时相位只对窄带信号有意义，真实 BOLD 需先带通滤波（如 0.01–0.08 Hz 内再取较窄频带）。
import numpy as np
from scipy.signal import hilbert, butter, filtfilt
from scipy.cluster.vq import kmeans2

rng = np.random.default_rng(0)
N, T, fs = 8, 1200, 1.0                      # 1 个时间单位 = 1 个采样点
t = np.arange(T)
f0 = 0.05                                    # 共同振荡频率（每采样点 0.05 周期）
base = 2 * np.pi * f0 * t + 0.3 * np.cumsum(rng.standard_normal(T)) * 0.05
offset = np.zeros((N, T))
offset[5:, : T // 2] = np.pi                 # 前半段：5–7 号与 0–4 号反相
X = np.cos(base + offset) + 0.4 * rng.standard_normal((N, T))

b, a = butter(3, [0.03, 0.07], btype="band", fs=fs)
Xf = filtfilt(b, a, X, axis=1)
theta = np.angle(hilbert(Xf, axis=1))       # (N, T) 瞬时相位

def leading_eigvec(th):
    P = np.cos(th[:, None] - th[None, :])
    w, V = np.linalg.eigh(P)
    v = V[:, -1]
    return v if np.sum(v < 0) >= np.sum(v > 0) else -v   # 统一符号：使多数分量为负（v 与 −v 等价）

edge = 50                                    # 去掉两端受滤波边缘效应影响的点
V1 = np.array([leading_eigvec(theta[:, k]) for k in range(edge, T - edge)])
_, lab = kmeans2(V1, 2, seed=1, minit="++")
half = T // 2 - edge
print("前半段主导特征向量（取中位数）符号：", np.sign(np.median(V1[:half], axis=0)).astype(int))
print("后半段主导特征向量（取中位数）符号：", np.sign(np.median(V1[half:], axis=0)).astype(int))
acc = np.mean(lab[:half] == np.bincount(lab[:half]).argmax()) * 0.5 + \
      np.mean(lab[half:] == np.bincount(lab[half:]).argmax()) * 0.5
print(f"两段各自主导标签的占比（平均）= {acc:.2f}；前后两段主导标签是否不同：",
      np.bincount(lab[:half]).argmax() != np.bincount(lab[half:]).argmax())

import matplotlib.pyplot as plt
fig, axes = plt.subplots(2, 1, figsize=(10, 4.2), sharex=True, gridspec_kw={"height_ratios": [3, 1]},
                         layout="constrained")
tt = np.arange(edge, T - edge)
vm = np.abs(V1).max()
im = axes[0].imshow(V1.T, aspect="auto", cmap="RdBu_r", vmin=-vm, vmax=vm, interpolation="nearest",
                    extent=[tt[0], tt[-1], N - 0.5, -0.5])
axes[0].set(ylabel="Region", title="Leading eigenvector of phase coherence: two anti-phase groups, then one")
fig.colorbar(im, ax=axes, shrink=0.8, label="v1 component")
axes[1].plot(tt, lab, color="k", lw=1)
axes[1].set(xlabel="Time (samples)", ylabel="State", yticks=[0, 1])
plt.show()

# %% 示例：共激活模式（CAP）：种子阈值选帧 + k-means
# 思路来自 Liu & Duyn（2013, PNAS）：只取种子区信号超过阈值（此处取最高 15%）的时间帧，
# 对这些帧的全脑空间模式做 k-means，每类求平均得到 CAP。
# 模拟：20 个脑区；种子区（0 号）高活动时，伴随两种不同的空间模式之一（模式 A：1–6 号；模式 B：7–12 号）。
# 输出解读：全部帧平均（相当于种子相关图）把两种模式混在一起；k = 2 的 CAP 能把它们分开。
import numpy as np
from scipy.cluster.vq import kmeans2

rng = np.random.default_rng(4)
N, T = 20, 3000
X = rng.standard_normal((N, T))
events = rng.choice(T, 300, replace=False)
kind = rng.integers(0, 2, events.size)               # 每个事件随机属于模式 A 或 B
for e, k in zip(events, kind):
    X[0, e] += 3.0
    members = np.arange(1, 7) if k == 0 else np.arange(7, 13)
    X[members, e] += 2.5
X = (X - X.mean(1, keepdims=True)) / X.std(1, keepdims=True)

thr = np.quantile(X[0], 0.85)                         # 种子信号最高 15% 的帧
frames = np.where(X[0] > thr)[0]
F = X[:, frames].T                                    # (帧数, N)
_, lab = kmeans2(F, 2, seed=0, minit="++")
seed_map = F.mean(0)
print(f"选中帧数 = {frames.size}（占 {frames.size / T:.0%}）")
print("全部选中帧平均（类似种子相关图）：区 1–6 均值 %.2f，区 7–12 均值 %.2f"
      % (seed_map[1:7].mean(), seed_map[7:13].mean()))
for c in range(2):
    cap = F[lab == c].mean(0)
    print(f"CAP {c}：帧数 {np.sum(lab == c):3d}，区 1–6 均值 {cap[1:7].mean():.2f}，"
          f"区 7–12 均值 {cap[7:13].mean():.2f}")

import matplotlib.pyplot as plt
fig, axes = plt.subplots(1, 3, figsize=(10, 3.6), sharey=True)
maps = [("Mean of all selected frames", seed_map)] + \
       [(f"CAP {c} ({np.sum(lab == c)} frames)", F[lab == c].mean(0)) for c in range(2)]
for ax, (ttl, mp) in zip(axes, maps):
    ax.bar(np.arange(N), mp, color=np.where(mp >= 0, "#CC6677", "#4477AA"))
    ax.axvspan(0.5, 6.5, color="#DDCC77", alpha=0.25)
    ax.axvspan(6.5, 12.5, color="#88CCEE", alpha=0.25)
    ax.set(title=ttl, xlabel="Region (0 = seed)")
axes[0].set_ylabel("Mean z-score")
plt.tight_layout(); plt.show()

# %% 示例：边时间序列与高振幅共波动
# 把每个脑区 z 标准化后，边 (i,j) 的边时间序列为逐点乘积 e_ij(t) = z_i(t) z_j(t)；
# 它在时间上的平均恰好等于皮尔逊相关（用总体标准差标准化时严格相等）。
# 每帧的共波动幅度用所有边共波动的平方和的平方根（RSS）表示，取最高与最低 5% 的帧分别重建 FC，与整段 FC 比较。
# 模拟数据是一个“平稳”的多元高斯过程（真实 FC 恒定），用来说明：即使没有任何动态，
# 高 RSS 帧也会更像整体 FC（与 Ladwig 等 2022、Novelli & Razi 2022 的论证一致）。
import numpy as np

rng = np.random.default_rng(7)
N, T = 30, 1200
# 两个模块的平稳协方差（模拟数据，仅用于演示方法）
C = np.full((N, N), 0.1)
C[:15, :15] = C[15:, 15:] = 0.5
np.fill_diagonal(C, 1.0)
X = rng.multivariate_normal(np.zeros(N), C, size=T).T
Z = (X - X.mean(1, keepdims=True)) / X.std(1, keepdims=True)

iu = np.triu_indices(N, 1)
E = Z[iu[0]] * Z[iu[1]]                        # (边数, T) 边时间序列
r_static = np.corrcoef(X)[iu]
print("边时间序列的时间平均 与 皮尔逊 r 的最大差异 =", np.abs(E.mean(1) - r_static).max().round(12))

rss = np.sqrt((E ** 2).sum(0))
order = np.argsort(rss)
k = int(0.05 * T)
top, bottom = order[-k:], order[:k]
fc_top = E[:, top].mean(1)
fc_bot = E[:, bottom].mean(1)
print(f"最高 5% 帧重建的 FC 与整体 FC 的相关 = {np.corrcoef(fc_top, r_static)[0, 1]:.2f}")
print(f"最低 5% 帧重建的 FC 与整体 FC 的相关 = {np.corrcoef(fc_bot, r_static)[0, 1]:.2f}")
rand = rng.choice(T, k, replace=False)
print(f"随机 5% 帧重建的 FC 与整体 FC 的相关 = {np.corrcoef(E[:, rand].mean(1), r_static)[0, 1]:.2f}")

import matplotlib.pyplot as plt
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
axes[0].plot(rss, color="gray", lw=0.6)
axes[0].scatter(top, rss[top], s=10, color="crimson", label="top 5% RSS")
axes[0].scatter(bottom, rss[bottom], s=10, color="#4477AA", marker="s", label="bottom 5% RSS")
axes[0].set(xlabel="Frame", ylabel="RSS of edge co-fluctuation", title="Co-fluctuation amplitude (stationary data)")
axes[0].legend(fontsize=8)
axes[1].scatter(r_static, fc_top, s=8, alpha=0.5, color="crimson", marker="o", label="top 5% frames")
axes[1].scatter(r_static, fc_bot, s=8, alpha=0.5, color="#4477AA", marker="s", label="bottom 5% frames")
axes[1].set(xlabel="Static FC (Pearson r)", ylabel="FC from selected frames", title="High-RSS frames resemble static FC")
axes[1].legend(fontsize=8)
plt.tight_layout(); plt.show()

# %% 示例：高斯隐马尔可夫模型（HMM）：前向–后向与 EM
# 每个隐状态 k 有自己的协方差矩阵 Σ_k（均值设为 0，即“连接状态”），状态序列服从一阶马尔可夫链。
# 本例用 numpy 写出 Baum–Welch（EM）算法：E 步用缩放的前向–后向递推求后验 γ_t(k)，
# M 步更新初始概率、转移矩阵和各状态协方差。模拟数据按 S1(300)→S2(200)→S1(300)→S2(200) 切换。
# 输出解读：后验最大状态与真值的一致率；估计的转移矩阵对角线接近 1，对应较长的停留时间。
# 真实研究用 HMM-MAR、osl-dynamics 等工具，并需要多次随机初始化和状态数敏感性分析。
import numpy as np
from scipy.stats import multivariate_normal

rng = np.random.default_rng(11)
N = 5
S1 = np.eye(N); S1[0, 1] = S1[1, 0] = S1[2, 3] = S1[3, 2] = 0.8
S2 = np.eye(N); S2[0, 4] = S2[4, 0] = S2[1, 2] = S2[2, 1] = -0.7
segs = [(0, 300), (1, 200), (0, 300), (1, 200)]
X = np.vstack([rng.multivariate_normal(np.zeros(N), [S1, S2][s], size=L) for s, L in segs])
truth = np.concatenate([[s] * L for s, L in segs])
T, K = X.shape[0], 2

def fit_hmm(X, K, n_iter=50, seed=0):
    r = np.random.default_rng(seed)
    T, N = X.shape
    pi = np.full(K, 1 / K)
    A = np.full((K, K), 0.05 / (K - 1)); np.fill_diagonal(A, 0.95)
    blocks = np.array_split(r.permutation(T), K)        # 随机划分时间点作初始协方差
    Sig = [np.cov(X[b].T) + 1e-3 * np.eye(N) for b in blocks]
    for _ in range(n_iter):
        B = np.column_stack([multivariate_normal(np.zeros(N), S).pdf(X) for S in Sig])  # (T, K)
        alpha = np.zeros((T, K)); c = np.zeros(T)
        alpha[0] = pi * B[0]; c[0] = alpha[0].sum(); alpha[0] /= c[0]
        for t in range(1, T):
            alpha[t] = (alpha[t - 1] @ A) * B[t]; c[t] = alpha[t].sum(); alpha[t] /= c[t]
        beta = np.ones((T, K))
        for t in range(T - 2, -1, -1):
            beta[t] = (A @ (B[t + 1] * beta[t + 1])) / c[t + 1]
        gamma = alpha * beta
        xi = np.zeros((K, K))
        for t in range(T - 1):
            xi += (alpha[t][:, None] * A * (B[t + 1] * beta[t + 1])[None, :]) / c[t + 1]
        pi = gamma[0]
        A = xi / xi.sum(1, keepdims=True)
        Sig = [(gamma[:, k, None] * X).T @ X / gamma[:, k].sum() + 1e-6 * np.eye(N) for k in range(K)]
    return gamma, A, Sig, np.log(c).sum()

gamma, A, Sig, ll = fit_hmm(X, K)
path = gamma.argmax(1)
acc = max(np.mean(path == truth), np.mean(path != truth))
print(f"对数似然 = {ll:.1f}；后验最大状态与真值一致率 = {acc:.3f}")
print("估计的转移矩阵：\n", A.round(3))
print("平均停留时间（时间点）≈ 1/(1 − A_kk)：", (1 / (1 - np.diag(A))).round(1))

import matplotlib.pyplot as plt
k1 = int(np.argmax([np.mean(path[truth == 0] == k) for k in range(K)]))   # 与 S1 对应的估计状态
fig, axes = plt.subplots(1, 3, figsize=(11, 3.6), gridspec_kw={"width_ratios": [2.4, 1, 1]})
axes[0].fill_between(np.arange(T), 0, 1, where=truth == 0, color="#DDDDDD", step="mid", label="true S1 periods")
axes[0].plot(gamma[:, k1], color="#4477AA", lw=0.8, label="P(S1 | data)")
axes[0].set(xlabel="Time point", ylabel="Posterior probability", ylim=(-0.02, 1.02),
            title=f"HMM state posterior (agreement {acc:.2f})")
axes[0].legend(fontsize=8, loc="lower right")
for ax, k, nm in [(axes[1], k1, "S1"), (axes[2], 1 - k1, "S2")]:
    sd = np.sqrt(np.diag(Sig[k]))
    im = ax.imshow(Sig[k] / np.outer(sd, sd), cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set(title=f"{nm} (estimated r)", xticks=range(N), yticks=range(N))
fig.colorbar(im, ax=axes[2], shrink=0.8)
plt.tight_layout(); plt.show()

# %% 示例：状态数的选择与分半稳定性
# 对同一组“窗口连接向量”，比较 k = 2..6 的 k-means：(a) 组内平方和（肘部法则）；(b) 平均轮廓系数；
# (c) 分半稳定性：把窗口随机分成两半分别聚类，用匈牙利算法匹配两半的状态中心，报告匹配后最差一对中心的相关。
# 模拟数据有 3 个真实状态（模拟数据，仅用于演示方法）。
# 输出解读：轮廓系数在 k = 3 最高，组内平方和在 k = 3 之后下降明显变缓（肘部）；
# k 继续增大时多出的“状态”只是把真实状态切碎，k = 6 时分半中心已无法一一对应。
# 任何单一指标都只是参考，真实数据的“最佳 k”常常不明确，应报告多个 k 下结论是否一致。
import numpy as np
from scipy.cluster.vq import kmeans2
from scipy.spatial.distance import cdist
from scipy.optimize import linear_sum_assignment

rng = np.random.default_rng(5)
D, n_per = 45, 200                                    # 45 维 ≈ 10 个脑区的上三角
centers = rng.normal(0, 0.5, (3, D))
V = np.vstack([c + 0.45 * rng.standard_normal((n_per, D)) for c in centers])

def silhouette(V, lab):
    Dm = cdist(V, V)
    s = np.zeros(len(V))
    for i in range(len(V)):
        same = lab == lab[i]
        a = Dm[i, same].sum() / max(same.sum() - 1, 1)
        b = min(Dm[i, lab == c].mean() for c in np.unique(lab) if c != lab[i])
        s[i] = (b - a) / max(a, b)
    return s.mean()

def best_kmeans(V, k, n_init=10):
    best = None
    for s in range(n_init):
        cen, lab = kmeans2(V, k, seed=s, minit="++")
        sse = ((V - cen[lab]) ** 2).sum()
        if best is None or sse < best[0]:
            best = (sse, cen, lab)
    return best

curves = []                                           # 记录各 k 的指标，供作图
for k in range(2, 7):
    sse, cen, lab = best_kmeans(V, k)
    idx = rng.permutation(len(V)); h1, h2 = idx[: len(V) // 2], idx[len(V) // 2:]
    c1 = best_kmeans(V[h1], k)[1]; c2 = best_kmeans(V[h2], k)[1]
    R = np.corrcoef(c1, c2)[:k, k:]
    row, col = linear_sum_assignment(-R)              # 匈牙利算法：最大化匹配相关
    sil = silhouette(V, lab)
    curves.append((k, sse, sil, R[row, col].min()))
    print(f"k = {k}：组内平方和 {sse:8.1f}，平均轮廓系数 {sil:.3f}，"
          f"分半中心匹配相关（最差一对）{R[row, col].min():.2f}")

import matplotlib.pyplot as plt
cv = np.array(curves)
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
axes[0].plot(cv[:, 0], cv[:, 1], "o-", color="k")
axes[0].set(xlabel="Number of states k", ylabel="Within-cluster sum of squares", title="Elbow criterion")
axes[1].plot(cv[:, 0], cv[:, 2], "o-", color="#4477AA", label="mean silhouette")
axes[1].plot(cv[:, 0], cv[:, 3], "s--", color="#CC6677", label="split-half match r (worst pair)")
axes[1].axvline(3, color="gray", ls=":", lw=1)
axes[1].set(xlabel="Number of states k", ylabel="Score", title="Silhouette peaks at the true k = 3")
axes[1].legend(fontsize=8)
plt.tight_layout(); plt.show()

# %% 示例：多层模块度与网络灵活性
# 时间多层网络：12 个脑区、10 层（时间窗）。前 5 层模块为 {0–5}、{6–11}；后 5 层中脑区 4、5 换到第二个模块。
# 构造超模块度矩阵 B（层内 A − γ k kᵀ/2m，层间同一脑区相连、权重 ω），
# 用一个简化的“局部移动”启发式（Louvain 第一阶段）最大化 Q，再计算每个脑区的灵活性
# （相邻层间改变模块归属的次数 / (层数 − 1)）。
# 输出解读：在中小的 ω 下，只有换模块的脑区 4、5 灵活性非零（1 次变化 / 9 个相邻层对 ≈ 0.11）；
# ω 增大到 10 时只剩脑区 4 仍会切换，ω = 50 时层间耦合压倒层内结构，所有脑区被“冻结”，灵活性全为 0。
# 灵活性的数值依赖 ω 和 γ，研究中应在参数网格上报告。
# 不同随机种子得到的 Q 不同（模块度优化的简并性），所以要多次运行；实际研究用 GenLouvain 等实现，
# 并对多次运行取共识、与置换零模型比较。
import numpy as np

rng = np.random.default_rng(2)
N, L = 12, 10

def layer_adj(groups):
    A = rng.uniform(0, 0.2, (N, N))
    for g in groups:
        for i in g:
            for j in g:
                A[i, j] += rng.uniform(0.6, 1.0)
    A = (A + A.T) / 2
    np.fill_diagonal(A, 0)
    return A

layers = [layer_adj([range(0, 6), range(6, 12)]) for _ in range(5)] + \
         [layer_adj([range(0, 4), range(4, 12)]) for _ in range(5)]

def supra_B(layers, gamma, omega):
    B = np.zeros((N * L, N * L))
    for l, A in enumerate(layers):
        k = A.sum(1); m2 = k.sum()
        B[l * N:(l + 1) * N, l * N:(l + 1) * N] = A - gamma * np.outer(k, k) / m2
    for l in range(L - 1):                            # 有序耦合：只连相邻层
        for i in range(N):
            B[l * N + i, (l + 1) * N + i] = B[(l + 1) * N + i, l * N + i] = omega
    return B

def local_moving(B, seed=0, n_pass=50):
    """Louvain 第一阶段：逐个节点移到使 Q 增量最大的社团，直到不再移动。"""
    r = np.random.default_rng(seed)
    n = B.shape[0]
    g = np.arange(n)
    for _ in range(n_pass):
        moved = False
        for v in r.permutation(n):
            comms = np.unique(g)
            score = np.array([B[v, g == c].sum() - (B[v, v] if g[v] == c else 0) for c in comms])
            best = comms[score.argmax()]
            if best != g[v] and score.max() > score[comms == g[v]][0] + 1e-12:
                g[v] = best; moved = True
        if not moved:
            break
    return np.unique(g, return_inverse=True)[1]

def louvain_B(B, seed=0):
    """对任意模块度矩阵 B 做 Louvain：局部移动 + 聚合，重复至收敛。"""
    member = np.arange(B.shape[0])
    Bc = B.copy()
    while True:
        g = local_moving(Bc, seed)
        if g.max() + 1 == Bc.shape[0]:
            return member
        member = g[member]
        P = np.eye(g.max() + 1)[g]                    # (旧节点数, 新节点数) 指示矩阵
        Bc = P.T @ Bc @ P

def flexibility(g):
    G = g.reshape(L, N)
    return (G[1:] != G[:-1]).sum(0) / (L - 1)

def quality(B, g, two_mu):
    return B[g[:, None] == g[None, :]].sum() / two_mu

two_m = sum(A.sum() for A in layers)
best_g = []                                           # 记录各 ω 的最优划分，供作图
for omega in [0.1, 1.0, 10.0, 50.0]:
    B = supra_B(layers, gamma=1.0, omega=omega)
    two_mu = two_m + 2 * omega * N * (L - 1)
    runs = [louvain_B(B, seed=s) for s in range(10)]   # 启发式有随机性：多次运行
    Qs = [quality(B, g, two_mu) for g in runs]
    g = runs[int(np.argmax(Qs))]
    best_g.append(g)
    print(f"ω = {omega}：10 次运行 Q 范围 {min(Qs):.3f}–{max(Qs):.3f}，最优解社团数 = {g.max() + 1}，"
          f"灵活性 = {flexibility(g).round(2).tolist()}")

import matplotlib.pyplot as plt
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
axes[0].imshow(best_g[1].reshape(L, N).T, cmap="Set2", aspect="auto", interpolation="nearest")
axes[0].set(xlabel="Layer (time window)", ylabel="Region", xticks=range(L), yticks=range(N),
            title="Community labels across layers (omega = 1)")
for g, om, mk, ls in zip(best_g, [0.1, 1.0, 10.0, 50.0], "os^D", ["-", "--", "-.", ":"]):
    axes[1].plot(range(N), flexibility(g), marker=mk, ls=ls, lw=1, label=f"omega = {om}")
axes[1].set(xlabel="Region", ylabel="Flexibility", xticks=range(N), title="Only regions that switch are flexible")
axes[1].legend(fontsize=8)
plt.tight_layout(); plt.show()

# %% 示例：小波相干：连接强度随时间和频率变化
# 用 Morlet 小波对两条信号做连续小波变换 W_x(s,t)、W_y(s,t)，
# 小波相干 R²(s,t) = |S(W_x W_y*)|² / (S(|W_x|²) S(|W_y|²))，S 为时间方向的高斯平滑（尺度相关）。
# 模拟：两条信号共享一个周期 40 点的振荡，但只在前半段共享（模拟数据，仅用于演示方法）。
# 输出解读：周期 40 的相干在前半段接近 1、后半段明显下降；其他周期不随时间系统变化。
# 注意后半段及其他周期的相干仍有 0.4–0.7：平滑窗口有限时小波相干有正偏差，必须与替代数据比较而非与 0 比较。
# 实际分析还要剔除“影响锥”（cone of influence）内的边缘值，并用蒙特卡洛替代数据评估显著性。
import numpy as np

rng = np.random.default_rng(8)
T = 1000
t = np.arange(T)
common = np.sin(2 * np.pi * t / 40)
x = common + rng.standard_normal(T)
y = np.where(t < T // 2, common, 0.0) + rng.standard_normal(T)   # 后半段不再含共同振荡

def morlet_cwt(sig, periods, w0=6.0):
    """FFT 实现的 Morlet 连续小波变换；periods 以采样点为单位。"""
    n = len(sig)
    f = np.fft.fftfreq(n)
    F = np.fft.fft(sig - sig.mean())
    out = np.zeros((len(periods), n), dtype=complex)
    for i, P in enumerate(periods):
        s = P * w0 / (2 * np.pi)                     # Morlet：周期 ≈ 2π s / w0
        psi_hat = np.pi ** -0.25 * np.exp(-0.5 * (s * 2 * np.pi * f - w0) ** 2) * (f > 0)
        out[i] = np.fft.ifft(F * psi_hat * np.sqrt(2 * np.pi * s))
    return out

def smooth_time(M, periods, w0=6.0):
    out = np.empty_like(M)
    for i, P in enumerate(periods):
        s = P * w0 / (2 * np.pi)
        k = np.exp(-0.5 * (np.arange(-3 * int(s) - 1, 3 * int(s) + 2) / s) ** 2)
        k /= k.sum()
        out[i] = np.convolve(M[i], k, mode="same")
    return out

periods = np.array([10, 20, 40, 80])
Wx, Wy = morlet_cwt(x, periods), morlet_cwt(y, periods)
num = np.abs(smooth_time(Wx * np.conj(Wy), periods)) ** 2
den = smooth_time(np.abs(Wx) ** 2, periods).real * smooth_time(np.abs(Wy) ** 2, periods).real
R2 = num / den
first, second = slice(100, 400), slice(600, 900)    # 避开边缘
for P, r in zip(periods, R2):
    print(f"周期 {P:3d}：前半段平均相干 {r[first].mean():.2f}，后半段 {r[second].mean():.2f}")

import matplotlib.pyplot as plt
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
im = axes[0].imshow(R2, aspect="auto", cmap="viridis", vmin=0, vmax=1, origin="lower", interpolation="nearest",
                    extent=[0, T, -0.5, len(periods) - 0.5])
axes[0].set(yticks=range(len(periods)), yticklabels=periods, xlabel="Time (samples)", ylabel="Period (samples)",
            title="Wavelet coherence $R^2$(period, time)")
fig.colorbar(im, ax=axes[0], label="$R^2$")
axes[1].plot(t, R2[2], "-", color="crimson", label="period 40 (shared in first half)")
axes[1].plot(t, R2[0], "--", color="gray", label="period 10 (never shared)")
axes[1].axvline(T // 2, color="k", ls=":", lw=1)
axes[1].set(xlabel="Time (samples)", ylabel="$R^2$", ylim=(0, 1.05), title="Coherence drops when coupling stops")
axes[1].legend(fontsize=8, loc="lower left")
plt.tight_layout(); plt.show()

# %% 示例：动态指标的重测信度（ICC）
# 模拟 60 名被试、每人两次扫描。每人有一个稳定的“真实特质”：静态连接强度 ρ_s 与“动态性”（连接随时间变化的幅度）。
# 每次扫描计算：(a) 整段静态相关；(b) 滑动窗口相关的标准差（常用的动态指标）。
# 用 ICC(3,1)（一致性、双向混合效应）比较两类指标的重测信度。
# 输出解读：在同样的数据量下，静态相关的 ICC 明显高于窗口相关标准差——
# 后者受有限样本波动影响大（参见“有限样本波动”一节），需要更长扫描或模型化估计（如 DCC）。
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

rng = np.random.default_rng(21)
S, T, w = 60, 600, 40
rho_s = rng.uniform(0.1, 0.6, S)                      # 被试的静态连接
amp_s = rng.uniform(0.0, 0.35, S)                     # 被试的连接波动幅度

def ar1(e, phi=0.6):
    out = np.zeros_like(e)
    for t in range(1, e.shape[-1]):
        out[..., t] = phi * out[..., t - 1] + e[..., t]
    return out

def session(rho, amp):
    rt = np.clip(rho + amp * np.sin(2 * np.pi * np.arange(T) / 150 + rng.uniform(0, 6.3)), -0.95, 0.95)
    z = rng.standard_normal((2, T))
    x = z[0]; y = rt * z[0] + np.sqrt(1 - rt ** 2) * z[1]
    X = ar1(np.vstack([x, y]))
    xw = sliding_window_view(X[0], w); yw = sliding_window_view(X[1], w)
    xc = xw - xw.mean(1, keepdims=True); yc = yw - yw.mean(1, keepdims=True)
    r = (xc * yc).sum(1) / np.sqrt((xc ** 2).sum(1) * (yc ** 2).sum(1))
    return np.corrcoef(X)[0, 1], r.std()

def icc_3_1(Y):
    """Y: (被试数, 测量次数)。ICC(3,1) = (MS_R − MS_E) / (MS_R + (k−1) MS_E)。"""
    n, k = Y.shape
    gm = Y.mean()
    ms_r = k * ((Y.mean(1) - gm) ** 2).sum() / (n - 1)
    ms_c = n * ((Y.mean(0) - gm) ** 2).sum() / (k - 1)
    sse = ((Y - gm) ** 2).sum() - ms_r * (n - 1) - ms_c * (k - 1)
    ms_e = sse / ((n - 1) * (k - 1))
    return (ms_r - ms_e) / (ms_r + (k - 1) * ms_e)

res = np.array([[session(rho_s[s], amp_s[s]) for _ in range(2)] for s in range(S)])  # (S, 2, 2)
print(f"静态相关的 ICC(3,1)        = {icc_3_1(res[:, :, 0]):.2f}")
print(f"窗口相关标准差的 ICC(3,1)  = {icc_3_1(res[:, :, 1]):.2f}")
print(f"窗口相关标准差与真实波动幅度的相关 = {np.corrcoef(res[:, 0, 1], amp_s)[0, 1]:.2f}")

import matplotlib.pyplot as plt
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
for ax, j, lab in [(axes[0], 0, "Static correlation"), (axes[1], 1, "SD of windowed r")]:
    ax.scatter(res[:, 0, j], res[:, 1, j], s=40, color="#4477AA", edgecolor="k", lw=0.3)
    lo, hi = res[:, :, j].min(), res[:, :, j].max()
    ax.plot([lo, hi], [lo, hi], "k--", lw=0.8)
    ax.set(xlabel=f"{lab}, session 1", ylabel=f"{lab}, session 2", title=f"{lab}: ICC(3,1) = {icc_3_1(res[:, :, j]):.2f}")
plt.tight_layout(); plt.show()
