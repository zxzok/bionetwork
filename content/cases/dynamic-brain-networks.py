# %% [markdown]
# # 睁眼与闭眼静息 EEG 的动态 α 频段网络：滑动窗口、容积传导、相位随机化零模型与连接状态
#
# 本案例用真实的 64 导静息态脑电中的 19 个标准电极，完成一次[动态功能连接与多层脑网络](dynamic-brain-networks.html)专题中的核心流程：带通滤波和希尔伯特相位 → 滑动窗口相位同步 → 检查容积传导 → 用相位随机化替代数据检验“波动是否超出平稳预期” → k-means 连接状态及其占时、停留时间。数据里自带一个已知的“状态”——睁眼还是闭眼——可以用来检验聚类得到的状态到底对应什么。
#
# **1. 数据来源**
#
# - 数据集：PhysioNet 的 EEG Motor Movement/Imagery Dataset v1.0.0（Schalk, 2009, doi:[10.13026/C28G6P](https://doi.org/10.13026/C28G6P)），由 BCI2000 系统采集（Schalk 等, 2004），许可证 Open Data Commons Attribution License v1.0（ODC-By），再分发需注明出处。下载日期 2026-11-20。
# - 每名被试先记录两段 1 分钟的静息基线：第 1 段睁眼（EO），第 2 段闭眼（EC）；原始数据 64 导、160 Hz、按国际 10-10 系统放置电极。
# - 文件 `data/eeg_eyes_open_closed.csv` 取前 6 名被试（S001–S006，按编号顺序，未做挑选），只保留 19 个 10-20 位置，每段前 60 秒，抗混叠滤波后降采样到 80 Hz、取整到 1 µV（处理见 `data/SOURCES.md`）。80 Hz 采样对本案例关心的 α 频段（8–12 Hz）足够。
# - 闭眼时枕区 α 节律增强（Berger 效应）是脑电最经典、最稳健的现象之一，这里把它当作一个“已知答案”：如果分析流程连它都看不出来，就要先怀疑流程。
#
# %% [markdown]
# ## 2. 读入与清洗
#
# 每行是一个采样点。按被试和条件切成 12 段 $19\times4800$ 的矩阵，做两步预处理：
#
# 1. **共同平均参考**：每个时刻减去 19 个电极的平均。原始记录的参考方式会影响所有电极对之间的相位关系，重参考后各通道更可比；但参考方式本身也会改变连接估计，这是一个需要报告的选择。
# 2. **质量检查**：每段的通道标准差，以及用 Welch 法估计的枕区（O1、O2）与额区（Fz）α 功率。
#
# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, hilbert, welch

df = pd.read_csv("data/eeg_eyes_open_closed.csv")
ch = list(df.columns[2:])
fs = 80
segments, raw = {}, {}
for (s, c), g in df.groupby(["subject", "condition"], sort=False):
    X = g[ch].to_numpy(float).T
    raw[(s, c)] = X                           # 原始记录参考
    segments[(s, c)] = X - X.mean(0)          # 共同平均参考
print("段数:", len(segments), "；每段形状:", segments[("S001", "EO")].shape, "；电极:", " ".join(ch))

io, iz = [ch.index("O1"), ch.index("O2")], ch.index("Fz")
rows = []
for (s, c), X in segments.items():
    f, P = welch(X, fs=fs, nperseg=4 * fs)
    alpha = P[:, (f >= 8) & (f <= 12)].mean(1)
    rows.append((s, c, X.std(1).min(), X.std(1).max(), alpha[io].mean(), alpha[iz]))
qc = pd.DataFrame(rows, columns=["subject", "cond", "sd_min", "sd_max", "alpha_occ", "alpha_Fz"])
print(qc.round(1).to_string(index=False))
ratio = (qc[qc.cond == "EC"].set_index("subject").alpha_occ / qc[qc.cond == "EO"].set_index("subject").alpha_occ)
print("闭眼/睁眼 枕区 α 功率比：", ratio.round(1).to_dict())

# %% [markdown]
# 没有通道是平直线或明显的大幅漂移（各段通道标准差在合理范围内）。6 名被试中有 4 名闭眼时枕区 α 功率升高数倍到十几倍；S005、S006 的升高很小。这不是数据错误，而是真实的个体差异：一部分人 α 节律本来就弱。后面会看到，这种个体差异会直接影响“连接状态”的结果。
#
# %% [markdown]
# ## 3. 构网：α 频段的瞬时相位与滑动窗口
#
# 4 阶 Butterworth 带通（8–12 Hz）零相位滤波，再用希尔伯特变换得到每个电极的瞬时相位（见[相位同步与瞬时相位方法](dynamic-brain-networks.phase-synchrony.html)）。去掉两端各 1 秒以避开滤波边缘效应后，用长 2 秒（160 点，约 20 个 α 周期）、步长 1 秒的窗口滑动，每个窗口计算 171 对电极的两种同步指标：
#
# - **相位锁定值** $\mathrm{PLV}=\big|\langle e^{i\Delta\phi_t}\rangle\big|$：对零滞后同步敏感；
# - **相位滞后指数** $\mathrm{PLI}=\big|\langle\operatorname{sign}(\sin\Delta\phi_t)\rangle\big|$：只看相位差是否稳定偏向一侧，对零滞后（容积传导）不敏感（见[EEG/MEG 网络](dynamic-brain-networks.electrophysiology.html)）。
#
# 每段得到一个“窗口 × 边”的矩阵，就是一条连接矩阵的时间序列。
#
# %%
b, a = butter(4, [8 / (fs / 2), 12 / (fs / 2)], btype="band")
n_ch = len(ch)
iu = np.triu_indices(n_ch, 1)
W_LEN, STEP, EDGE = 2 * fs, fs, fs


def alpha_phase(X):
    return np.angle(hilbert(filtfilt(b, a, X, axis=1), axis=1))[:, EDGE:-EDGE]


def windowed_sync(X):
    ph = alpha_phase(X)
    plv, pli = [], []
    for t in range(0, ph.shape[1] - W_LEN + 1, STEP):
        d = ph[iu[0], t:t + W_LEN] - ph[iu[1], t:t + W_LEN]
        plv.append(np.abs(np.exp(1j * d).mean(1)))
        pli.append(np.abs(np.sign(np.sin(d)).mean(1)))
    return np.array(plv), np.array(pli)


sync = {k: windowed_sync(X) for k, X in segments.items()}
n_win = sync[("S001", "EO")][0].shape[0]
print("每段窗口数:", n_win, "；每个窗口边数:", len(iu[0]))
print("subject cond  全网平均PLV  全网平均PLI")
for (s, c), (plv, pli) in sync.items():
    print("%s  %s    %.3f        %.3f" % (s, c, plv.mean(), pli.mean()))

# %% [markdown]
# ## 4. 核心指标
#
# ### 4.1 容积传导：PLV 与 PLI 随电极距离的变化
#
# 为区分“相邻”和“远距”电极对，下面给 19 个电极一个**示意性的平面坐标**：按 10-20 系统的行列排列（额极、额、中央/颞、顶/颞后、枕五行，左右对称），单位是“相邻位置的间隔”。它只用来排序距离，不是真实的头皮坐标。若信号间的同步主要来自同一个源在多个电极上的投影，PLV 会随距离快速下降，而 PLI 受影响小得多。
#
# 参考电极也会制造零滞后的共同成分，所以同一分析在**原始参考**和**共同平均参考**下各做一次，用边的“距离–同步”Spearman 相关 $\rho$ 概括距离依赖。
#
# %%
pos = {"Fp1": (-1, 2), "Fp2": (1, 2),
       "F7": (-2, 1), "F3": (-1, 1), "Fz": (0, 1), "F4": (1, 1), "F8": (2, 1),
       "T7": (-2, 0), "C3": (-1, 0), "Cz": (0, 0), "C4": (1, 0), "T8": (2, 0),
       "P7": (-2, -1), "P3": (-1, -1), "Pz": (0, -1), "P4": (1, -1), "P8": (2, -1),
       "O1": (-1, -2), "O2": (1, -2)}
xy = np.array([pos[c] for c in ch], float)
dist = np.linalg.norm(xy[iu[0]] - xy[iu[1]], axis=1)
near, far = dist <= 1.0, dist >= 3.0
print("相邻电极对 %d 对，远距（≥3 个间隔）%d 对" % (near.sum(), far.sum()))
from scipy.stats import spearmanr
sync_raw = {k: windowed_sync(X) for k, X in raw.items()}
for name, S in (("原始参考", sync_raw), ("平均参考", sync)):
    for c in ("EO", "EC"):
        plv_e = np.mean([S[k][0].mean(0) for k in S if k[1] == c], 0)
        pli_e = np.mean([S[k][1].mean(0) for k in S if k[1] == c], 0)
        print("%s %s：ρ(距离, PLV) = %.2f，ρ(距离, PLI) = %.2f；PLV 相邻/远距 = %.2f，PLI 相邻/远距 = %.2f"
              % (name, c, spearmanr(dist, plv_e)[0], spearmanr(dist, pli_e)[0],
                 plv_e[near].mean() / plv_e[far].mean(), pli_e[near].mean() / pli_e[far].mean()))
print("以下均使用平均参考：")
for c in ("EO", "EC"):
    plv_e = np.mean([sync[k][0].mean(0) for k in sync if k[1] == c], 0)
    pli_e = np.mean([sync[k][1].mean(0) for k in sync if k[1] == c], 0)
    print("%s：PLV 相邻 %.3f / 远距 %.3f（比 %.2f）；PLI 相邻 %.3f / 远距 %.3f（比 %.2f）"
          % (c, plv_e[near].mean(), plv_e[far].mean(), plv_e[near].mean() / plv_e[far].mean(),
             pli_e[near].mean(), pli_e[far].mean(), pli_e[near].mean() / pli_e[far].mean()))

# %% [markdown]
# ### 4.2 静态网络：闭眼比睁眼更同步吗？同步超出机会水平吗？
#
# 对每段把所有窗口平均，得到静态 PLI 网络，比较 EO 与 EC 的全网平均 PLI 和枕–顶区电极之间的平均 PLI，用逐被试配对的差值看方向是否一致。
#
# PLI 的取值总是 ≥ 0，有限窗口里两个**完全独立**的信号也会得到正的 PLI。为了知道“0 在哪里”，再做一个最弱的零模型：给每个通道**各自独立**的随机相位，彻底破坏通道间的耦合，但保留每个通道的功率谱；它给出的全网平均 PLI 就是这一窗长下的机会水平。
#
# %%
post = [ch.index(c) for c in ("P7", "P3", "Pz", "P4", "P8", "O1", "O2")]
pmask = np.isin(iu[0], post) & np.isin(iu[1], post)
print("subject  全网PLI(EO→EC)    枕顶PLI(EO→EC)")
d_all, d_post = [], []
for s in sorted({k[0] for k in sync}):
    eo, ec = sync[(s, "EO")][1].mean(0), sync[(s, "EC")][1].mean(0)
    d_all.append(ec.mean() - eo.mean())
    d_post.append(ec[pmask].mean() - eo[pmask].mean())
    print("%s    %.3f → %.3f      %.3f → %.3f" % (s, eo.mean(), ec.mean(), eo[pmask].mean(), ec[pmask].mean()))
print("闭眼升高的被试数：全网 %d/6，枕顶 %d/6" % (np.sum(np.array(d_all) > 0), np.sum(np.array(d_post) > 0)))

rng0 = np.random.default_rng(7)


def independent_randomize(X):
    F = np.fft.rfft(X, axis=1)
    ph = rng0.uniform(0, 2 * np.pi, F.shape)
    ph[:, 0] = 0
    ph[:, -1] = 0
    return np.fft.irfft(F * np.exp(1j * ph), n=X.shape[1], axis=1)


print("subject cond  观测PLI  机会水平(独立相位, 10次)")
chance = {}
for k, X in segments.items():
    chance[k] = np.mean([windowed_sync(independent_randomize(X))[1].mean() for _ in range(10)])
    print("%s  %s    %.3f    %.3f" % (k[0], k[1], sync[k][1].mean(), chance[k]))

# %% [markdown]
# ## 5. 与零模型比较：窗口间的波动超出平稳预期了吗？
#
# 统计量是**全网平均 PLI 在窗口之间的标准差**——它越大，看起来越“动态”。零模型是[相位随机化替代数据](dynamic-brain-networks.null-models.html)：对 19 个通道的傅里叶系数乘以**同一组**随机相位再逆变换，保留每个通道的功率谱和通道间的静态互谱，破坏一切随时间变化的耦合。每段生成 100 个替代数据，走完全相同的滤波、相位、窗口流程，单侧 $p$ = 替代数据统计量 ≥ 观测值的比例。
#
# %%
rng = np.random.default_rng(2026)


def phase_randomize(X):
    F = np.fft.rfft(X, axis=1)
    ph = rng.uniform(0, 2 * np.pi, F.shape[1])
    ph[0] = 0
    if X.shape[1] % 2 == 0:
        ph[-1] = 0
    return np.fft.irfft(F * np.exp(1j * ph), n=X.shape[1], axis=1)


N_SUR = 100
null_rows = []
for k, X in segments.items():
    obs = sync[k][1].mean(1).std()
    sur = np.array([windowed_sync(phase_randomize(X))[1].mean(1).std() for _ in range(N_SUR)])
    p = (np.sum(sur >= obs) + 1) / (N_SUR + 1)
    null_rows.append((k[0], k[1], obs, np.median(sur), np.percentile(sur, 95), p))
nulls = pd.DataFrame(null_rows, columns=["subject", "cond", "sd_obs", "sd_null_median", "sd_null_95", "p"])
print(nulls.round(3).to_string(index=False))
print("p < 0.05 的段数: %d / %d；Bonferroni 校正（0.05/12）后: %d"
      % ((nulls.p < 0.05).sum(), len(nulls), (nulls.p < 0.05 / len(nulls)).sum()))

# %% [markdown]
# ## 6. 连接状态：k-means 能找出“睁眼”与“闭眼”吗？
#
# 把 12 段、每段 57 个窗口的 PLV 向量（171 维）放在一起，用 k-means 聚类（多次随机初始化取组内平方和最小的解）。先看 $K=2$ 时两个状态与睁眼/闭眼、与被试的对应关系，再计算每段的占时比例和平均停留时间（见[连接状态](dynamic-brain-networks.connectivity-states.html)）。最后列出 $K=2\ldots6$ 的组内平方和，看“肘部”是否清楚。这里用 PLV 而不是 PLI 作为特征，是因为 2 秒窗口的 PLI 估计噪声更大；代价是特征里混有容积传导成分。
#
# %%
keys = list(sync)
F = np.vstack([sync[k][0] for k in keys])
cond = np.concatenate([[k[1]] * n_win for k in keys])
subj = np.concatenate([[k[0]] * n_win for k in keys])


def kmeans(X, k, n_init=20, seed=0, iters=200):
    r = np.random.default_rng(seed)
    best = None
    for _ in range(n_init):
        C = X[r.choice(len(X), k, replace=False)]
        for _ in range(iters):
            lab = ((X[:, None, :] - C[None]) ** 2).sum(2).argmin(1)
            newC = np.array([X[lab == j].mean(0) if np.any(lab == j) else C[j] for j in range(k)])
            if np.allclose(newC, C):
                break
            C = newC
        sse = ((X - C[lab]) ** 2).sum()
        if best is None or sse < best[0]:
            best = (sse, lab, C)
    return best


sse2, lab, cent = kmeans(F, 2)
hi = int(np.argmax(cent.mean(1)))          # 把平均同步更高的中心记为“状态 H”
state = np.where(lab == hi, "H", "L")
print(pd.crosstab(state, cond))
print(pd.crosstab(state, subj))


def dwell(seq, s):
    runs, n = [], 0
    for x in seq:
        if x == s:
            n += 1
        elif n:
            runs.append(n)
            n = 0
    if n:
        runs.append(n)
    return np.mean(runs) if runs else 0.0


print("subject cond  状态H占时  状态H平均停留(窗口)  切换次数")
for i, k in enumerate(keys):
    seq = state[i * n_win:(i + 1) * n_win]
    print("%s  %s    %.2f        %5.1f           %d"
          % (k[0], k[1], np.mean(seq == "H"), dwell(seq, "H"), int(np.sum(seq[1:] != seq[:-1]))))

sses = [kmeans(F, k, n_init=10)[0] for k in range(2, 7)]
print("K = 2…6 的组内平方和：", np.round(sses, 1).tolist())

# %% [markdown]
# ## 7. 作图
#
# %%
fig, ax = plt.subplots(1, 3, figsize=(15, 4))
for c, col in (("EO", "tab:blue"), ("EC", "tab:red")):
    plv_e = np.mean([sync_raw[k][0].mean(0) for k in sync_raw if k[1] == c], 0)
    pli_e = np.mean([sync_raw[k][1].mean(0) for k in sync_raw if k[1] == c], 0)
    ax[0].scatter(dist + (0.05 if c == "EC" else -0.05), plv_e, s=8, color=col, alpha=0.6, label="PLV " + c)
    ax[0].scatter(dist + (0.05 if c == "EC" else -0.05), pli_e, s=8, color=col, marker="x", alpha=0.6, label="PLI " + c)
ax[0].set_xlabel("schematic electrode distance")
ax[0].set_ylabel("alpha-band synchrony")
ax[0].legend(fontsize=7)
ax[0].set_title("Original reference: PLV vs PLI")
k0 = ("S001", "EC")
t = np.arange(n_win) + 2
ax[1].plot(t, sync[k0][1].mean(1), "k-", label="observed")
ax[1].plot(t, windowed_sync(phase_randomize(segments[k0]))[1].mean(1), color="gray", alpha=0.8, label="one surrogate")
ax[1].set_xlabel("window centre (s)")
ax[1].set_ylabel("mean PLI")
ax[1].set_title("S001 eyes closed: sliding-window PLI")
ax[1].legend()
ax[2].imshow(np.where(state == "H", 1, 0).reshape(len(keys), n_win), aspect="auto", cmap="Greys", interpolation="nearest")
ax[2].set_yticks(range(len(keys)))
ax[2].set_yticklabels(["%s %s" % k for k in keys], fontsize=7)
ax[2].set_xlabel("window")
ax[2].set_title("k-means state H (black) per segment")
plt.tight_layout()

# %% [markdown]
# ## 8. 解读与局限
#
# **结果**
#
# 1. **零滞后的共同成分很明显，而且和参考方式纠缠在一起。** 在原始参考下，PLV 随电极距离强烈下降（$\rho\approx-0.8$），PLI 的距离依赖弱得多；这正是容积传导（以及参考电极带来的共同信号）的特征。改用共同平均参考后，两种指标的距离依赖几乎消失。同一批数据，换一个参考，“谁和谁连得强”就变了——电极空间的连接结论必须说明参考方式。
# 2. **闭眼增强 α 同步，但先要问“0 在哪里”。** 6 名被试的全网 PLI 闭眼时都不低于睁眼，α 强的 4 人升高明显。但独立相位替代数据显示，2 秒窗口的 PLI 机会水平约 0.23–0.41，而且 α 功率越强、节律越规则，机会水平越高；多数睁眼段的观测 PLI 只比机会水平高 0.01 左右。闭眼时的“升高”有一部分来自谱的变化本身，真正超出机会水平的部分要小得多。功率改变会改变相位指标，这是比较条件或组别时首先要排除的混杂。
# 3. **多数窗口波动没有超出平稳零模型。** 保留功率谱和静态互谱的相位随机化替代数据，产生的窗口间波动与观测值相当：12 段中只有 2 段 $p<0.05$，Bonferroni 校正后为 0。这与专题页的结论一致：单个被试、单次 1 分钟记录中看起来起伏不定的窗口连接，大部分可以由有限样本的采样变异解释（Hindriks 等, 2016；Laumann 等, 2017）。
# 4. **“状态”首先抓住的是已知的大差异，并且混入了被试差异。** $K=2$ 时，高同步状态 H 几乎只包含闭眼窗口（197 个中只有 5 个来自睁眼），但全部来自 α 节律强的 4 名被试；S005、S006 的闭眼窗口全部落在低同步状态。所以聚类出的状态同时反映了“条件”和“被试”两种来源——这正是专题页提醒的、状态可能变成“被试标签”的问题。状态 H 的平均停留时间从约 1 个窗口到整段 57 个窗口不等，主要由这名被试的闭眼 α 强度决定。组内平方和随 $K$ 平滑下降，没有清楚的肘部，状态数是一个建模选择。
#
# **局限**
#
# - 只有 6 名被试、每段 1 分钟，统计功效很低；“未超出平稳零模型”不等于“没有动态”。
# - 电极空间分析无法摆脱容积传导和参考的影响；更严谨的做法是先做源重建，再用对泄漏稳健的指标，并注意 PLI 类指标重测信度较差（见[EEG/MEG 网络](dynamic-brain-networks.electrophysiology.html)）。只有 19 个电极时，共同平均参考本身也只是近似。
# - 示意坐标只能区分“近”和“远”，不是真实的电极位置。
# - 没有做眼动、肌电伪迹的剔除；睁眼段的额极电极（Fp1、Fp2）尤其可能含眨眼成分。
# - 窗长 2 秒、步长 1 秒、8–12 Hz 频带、k-means 的特征（PLV）与 $K$ 都是选择，应在其他取值下检查结论。睁眼和闭眼的记录顺序固定（先睁眼后闭眼），条件与时间顺序混在一起。
#