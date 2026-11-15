# 依赖：networkx>=3, numpy, scipy, matplotlib
# 数据：numpy 从一个已知的“真实”偏相关网络（多元正态）抽样得到的模拟症状得分
# （模拟数据，仅用于演示方法，不代表任何真实人群的抑郁症状结构）。
# 输入格式：n×p 数组，每行一名被试，每列一个症状条目。真实量表条目是 0–3 分的有序变量，这里简化为连续变量。
# 这里用 numpy 演示原理；真实研究通常用 R（qgraph、bootnet、NetworkComparisonTest）或 JASP 的 Network 模块，
# 并使用正则化估计（EBICglasso）和多分格相关。
#
# 9 个症状（仿 PHQ-9 条目顺序）：
# PHQ1 兴趣减退  PHQ2 情绪低落  PHQ3 睡眠问题  PHQ4 疲乏  PHQ5 食欲改变
# PHQ6 自我评价低  PHQ7 注意力差  PHQ8 精神运动改变  PHQ9 自杀意念

# %% 示例：相关网络与偏相关网络
# 由相关矩阵求精度矩阵 K，偏相关 pcor_ij = -K_ij / sqrt(K_ii K_jj)。
# 分别统计 |r| > 0.1 与 |pcor| > 0.1 的边数，与真实网络的 10 条边比较。
# 输出解读：相关网络把间接关联也画成了边，边数明显多于真实边；偏相关网络更接近真实结构。
# 例如“睡眠问题–注意力差”只经由“疲乏”相关，相关系数不为 0，偏相关接近 0。
import numpy as np

names = ["兴趣减退", "情绪低落", "睡眠问题", "疲乏", "食欲改变",
         "自我评价低", "注意力差", "精神运动改变", "自杀意念"]
TRUE_EDGES = {(0, 1): .40, (1, 5): .30, (1, 8): .25, (5, 8): .25, (2, 3): .40,
              (3, 6): .30, (3, 7): .20, (3, 4): .20, (0, 3): .20, (6, 7): .20}

def simulate_symptoms(n, seed=0):
    """模拟数据，仅用于演示方法：从已知偏相关结构的多元正态分布抽样。"""
    K = np.eye(9)
    for (i, j), w in TRUE_EDGES.items():
        K[i, j] = K[j, i] = -w          # 精度矩阵负的非对角元 → 正偏相关
    rng = np.random.default_rng(seed)
    return rng.multivariate_normal(np.zeros(9), np.linalg.inv(K), size=n)

def pcor_from_corr(R):
    K = np.linalg.inv(R)
    d = np.sqrt(np.diag(K))
    P = -K / np.outer(d, d)
    np.fill_diagonal(P, 0)
    return P

X = simulate_symptoms(500)
R = np.corrcoef(X, rowvar=False)
P = pcor_from_corr(R)

iu = np.triu_indices(9, k=1)
true_set = set(TRUE_EDGES)
est = {(i, j) for i, j in zip(*iu) if abs(P[i, j]) > 0.1}
print("真实边数：", len(true_set))
print("相关网络 |r| > 0.1 的边数：", int(np.sum(np.abs(R[iu]) > 0.1)))
print("偏相关网络 |pcor| > 0.1 的边数：", len(est),
      "；其中真实边", len(est & true_set), "条，虚假边", len(est - true_set), "条")
print(f"例：睡眠问题–注意力差  r = {R[2, 6]:.2f}，pcor = {P[2, 6]:.2f}（真实网络中无直接边）")

import networkx as nx
import matplotlib.pyplot as plt

def draw_signed(ax, M, labels, thr, title, node_color="#DDDDDD", node_size=180, pos=None):
    """边宽 ∝ |权重|，蓝色为正边、红色为负边。"""
    n = len(labels)
    pos = nx.circular_layout(range(n)) if pos is None else pos
    G = nx.Graph(); G.add_nodes_from(range(n))
    G.add_weighted_edges_from((i, j, M[i, j]) for i in range(n) for j in range(i + 1, n) if abs(M[i, j]) > thr)
    ws = [d["weight"] for _, _, d in G.edges(data=True)]
    nx.draw_networkx_edges(G, pos, ax=ax, width=[max(1.0, 8 * abs(w)) for w in ws],
                           edge_color=["#4477AA" if w > 0 else "#CC6677" for w in ws])
    nx.draw_networkx_nodes(G, pos, ax=ax, node_size=node_size, node_color=node_color, edgecolors="k")
    lab_pos = {k: (1.22 * np.asarray(v)) for k, v in pos.items()}
    nx.draw_networkx_labels(G, lab_pos, labels=dict(enumerate(labels)), ax=ax, font_size=9)
    ax.plot([], [], color="#4477AA", lw=2, label="positive")
    ax.plot([], [], color="#CC6677", lw=2, label="negative")
    ax.legend(loc="lower right", fontsize=7, frameon=False)
    ax.set_title(title, fontsize=10); ax.set_aspect("equal"); ax.axis("off")
    ax.set_xlim(-1.45, 1.45); ax.set_ylim(-1.45, 1.45)

abbr = ["Anh", "Sad", "Slp", "Fat", "App", "Gui", "Con", "Mot", "Sui"]   # PHQ-9 条目英文缩写
fig, axes = plt.subplots(1, 2, figsize=(10, 4.8))
draw_signed(axes[0], R - np.eye(9), abbr, 0.1, f"Correlation |r| > 0.1: {int(np.sum(np.abs(R[iu]) > 0.1))} edges")
draw_signed(axes[1], P, abbr, 0.1, f"Partial correlation |pcor| > 0.1: {len(est)} edges")
plt.tight_layout(); plt.show()

# %% 示例：强度中心性与预期影响
# 在偏相关网络上计算强度 s_i = Σ_j |pcor_ij| 与预期影响 EI_i = Σ_j pcor_ij，并与相关网络上的强度比较。
# 输出解读：偏相关网络中疲乏、情绪低落的强度最高，与生成数据的真实结构一致；
# 本例真实网络没有负边，但未正则化的样本偏相关含有一些小的负估计值（抽样噪声），使部分症状的 EI 低于强度；
# 相关网络的强度排序前几位相同，中后段与偏相关网络不同。
# 中心性描述的是条件关联的多少，不说明干预该症状能改变其他症状。
import numpy as np
import matplotlib.pyplot as plt

names = ["兴趣减退", "情绪低落", "睡眠问题", "疲乏", "食欲改变",
         "自我评价低", "注意力差", "精神运动改变", "自杀意念"]
TRUE_EDGES = {(0, 1): .40, (1, 5): .30, (1, 8): .25, (5, 8): .25, (2, 3): .40,
              (3, 6): .30, (3, 7): .20, (3, 4): .20, (0, 3): .20, (6, 7): .20}

def simulate_symptoms(n, seed=0):
    K = np.eye(9)                        # 模拟数据，仅用于演示方法
    for (i, j), w in TRUE_EDGES.items():
        K[i, j] = K[j, i] = -w
    rng = np.random.default_rng(seed)
    return rng.multivariate_normal(np.zeros(9), np.linalg.inv(K), size=n)

def pcor(X):
    K = np.linalg.inv(np.cov(X, rowvar=False))
    d = np.sqrt(np.diag(K))
    P = -K / np.outer(d, d)
    np.fill_diagonal(P, 0)
    return P

X = simulate_symptoms(500)
P = pcor(X)
R = np.corrcoef(X, rowvar=False)
np.fill_diagonal(R, 0)

strength = np.abs(P).sum(axis=1)
ei = P.sum(axis=1)
s_corr = np.abs(R).sum(axis=1)
print("偏相关强度排序：", [names[i] for i in np.argsort(strength)[::-1]])
print("相关网络强度排序：", [names[i] for i in np.argsort(s_corr)[::-1]])
print("强度与预期影响的最大差值 =", round(float(np.max(strength - ei)), 3))

x = np.arange(9)
plt.bar(x - 0.2, strength, 0.4, label="strength (pcor)")
plt.bar(x + 0.2, s_corr / s_corr.max() * strength.max(), 0.4, label="strength (corr, rescaled)")
plt.xticks(x, [f"PHQ{i + 1}" for i in range(9)], rotation=45)
plt.legend()
plt.title("Strength centrality (simulated data)")
plt.show()

# %% 示例：中心性稳定性——简化版病例删除 bootstrap
# 仿照 bootnet 的思路：从样本中无放回地保留 90%、70%、50%、30% 的被试，每个比例重复 100 次，
# 计算子样本强度与全样本强度的相关，取其 5% 分位数；CS 系数近似为该分位数仍 ≥ 0.7 时可删去的最大比例。
# 输出解读：保留比例越低，相关越低；n = 100 时 CS 明显低于 n = 300——小样本的中心性排序不可靠。
# bootnet 的正式 CS 系数使用更细的删除比例、1000 次以上重抽样，并在每个子样本中重新选择正则化参数。
import numpy as np

TRUE_EDGES = {(0, 1): .40, (1, 5): .30, (1, 8): .25, (5, 8): .25, (2, 3): .40,
              (3, 6): .30, (3, 7): .20, (3, 4): .20, (0, 3): .20, (6, 7): .20}

def simulate_symptoms(n, seed=0):
    K = np.eye(9)                        # 模拟数据，仅用于演示方法
    for (i, j), w in TRUE_EDGES.items():
        K[i, j] = K[j, i] = -w
    rng = np.random.default_rng(seed)
    return rng.multivariate_normal(np.zeros(9), np.linalg.inv(K), size=n)

def strength_of(X):
    K = np.linalg.inv(np.cov(X, rowvar=False))
    d = np.sqrt(np.diag(K))
    P = -K / np.outer(d, d)
    np.fill_diagonal(P, 0)
    return np.abs(P).sum(axis=1)

def case_drop(X, keep_props=(0.9, 0.7, 0.5, 0.3), n_boot=100, seed=1):
    """返回 {保留比例: 子样本与全样本强度相关的 5% 分位数}。"""
    rng = np.random.default_rng(seed)
    s_full = strength_of(X)
    n = X.shape[0]
    out = {}
    for p in keep_props:
        cors = []
        for _ in range(n_boot):
            idx = rng.choice(n, int(p * n), replace=False)   # 无放回子抽样
            cors.append(np.corrcoef(strength_of(X[idx]), s_full)[0, 1])
        out[p] = np.quantile(cors, 0.05)
    return out

curves = {}                              # 记录各样本量的结果，供作图
for n in [300, 100]:
    res = case_drop(simulate_symptoms(n, seed=2))
    curves[n] = res
    cs = max([1 - p for p, q in res.items() if q >= 0.7], default=0.0)
    print(f"n = {n}：", {f"保留{int(p * 100)}%": round(float(q), 2) for p, q in res.items()},
          f"→ CS ≈ {cs:.1f}")

import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(6.4, 4.2))
for (n, res), mk, ls in zip(curves.items(), "os", ["-", "--"]):
    ax.plot([1 - p for p in res], list(res.values()), marker=mk, ls=ls, label=f"n = {n}")
ax.axhline(0.7, color="gray", ls=":", lw=1, label="CS cut-off 0.7")
ax.set(xlabel="Proportion of cases dropped", ylabel="5% quantile of r(subsample, full)",
       title="Strength stability: smaller samples drop below 0.7 sooner")
ax.legend(fontsize=8)
plt.tight_layout(); plt.show()

# %% 示例：EBICglasso——图形 LASSO 加 EBIC 选择惩罚参数
# 用块坐标下降实现图形 LASSO（Friedman 等, 2008；对角元不惩罚，与 qgraph::EBICglasso 默认一致），
# 在 λ ∈ [0.01 λ_max, λ_max] 的对数网格上计算 EBIC（γ = 0.5），选取 EBIC 最小的网络。
# 输出解读：未正则化的样本偏相关 36 条边全部非零；EBICglasso 把大多数虚假小边压成 0，
# 真实边大多保留，但边权被系统地压小（收缩偏倚，真实边平均权重低于真值 0.27）。
# n 较小时，漏检的真实边和保留下来的虚假边都会增多——"有边/无边"本身带有抽样误差。
import numpy as np

TRUE_EDGES = {(0, 1): .40, (1, 5): .30, (1, 8): .25, (5, 8): .25, (2, 3): .40,
              (3, 6): .30, (3, 7): .20, (3, 4): .20, (0, 3): .20, (6, 7): .20}

def simulate_symptoms(n, seed=0):
    K = np.eye(9)                        # 模拟数据，仅用于演示方法
    for (i, j), w in TRUE_EDGES.items():
        K[i, j] = K[j, i] = -w
    rng = np.random.default_rng(seed)
    return rng.multivariate_normal(np.zeros(9), np.linalg.inv(K), size=n)

def glasso(S, lam, W0=None, max_iter=200, tol=1e-5):
    """图形 LASSO（块坐标下降）。返回精度矩阵估计 Θ 与协方差估计 W。对角元不惩罚。"""
    p = S.shape[0]
    W = S.copy() if W0 is None else W0.copy()
    B = np.zeros((p, p))                 # 每列的 LASSO 系数，用于热启动
    for _ in range(max_iter):
        W_old = W.copy()
        for j in range(p):
            idx = np.arange(p) != j
            W11, s12, beta = W[np.ix_(idx, idx)], S[idx, j], B[idx, j].copy()
            for _ in range(100):         # LASSO 坐标下降：min ½βᵀW11β − s12ᵀβ + λ|β|₁
                beta_old = beta.copy()
                for k in range(p - 1):
                    r = s12[k] - W11[k] @ beta + W11[k, k] * beta[k]
                    beta[k] = np.sign(r) * max(abs(r) - lam, 0) / W11[k, k]
                if np.max(np.abs(beta - beta_old)) < tol:
                    break
            B[idx, j] = beta
            w12 = W11 @ beta
            W[idx, j] = W[j, idx] = w12
        if np.mean(np.abs(W - W_old)) < tol:
            break
    Theta = np.zeros((p, p))
    for j in range(p):
        idx = np.arange(p) != j
        beta = B[idx, j]
        t22 = 1.0 / (W[j, j] - W[idx, j] @ beta)
        Theta[j, j] = t22
        Theta[idx, j] = -beta * t22
    Theta = (Theta + Theta.T) / 2
    return Theta, W

def ebic_glasso(X, gamma=0.5, n_lambda=40, ratio=0.01):
    n, p = X.shape
    S = np.corrcoef(X, rowvar=False)
    lam_max = np.max(np.abs(S - np.eye(p)))
    lams = np.exp(np.linspace(np.log(lam_max), np.log(ratio * lam_max), n_lambda))
    best, W = None, None
    for lam in lams:                     # 从稀疏到稠密，热启动
        K, W = glasso(S, lam, W0=W)
        E = int(np.sum(np.abs(K[np.triu_indices(p, 1)]) > 1e-8))
        loglik = np.linalg.slogdet(K)[1] - np.trace(S @ K)
        ebic = -n * loglik + E * np.log(n) + 4 * gamma * E * np.log(p)
        if best is None or ebic < best[0]:
            best = (ebic, lam, K)
    _, lam, K = best
    d = np.sqrt(np.diag(K))
    P = -K / np.outer(d, d)
    np.fill_diagonal(P, 0)
    P[np.abs(P) < 1e-8] = 0
    return P, lam

true_set = set(TRUE_EDGES)
iu = np.triu_indices(9, 1)
P_hat = {}                               # 记录各样本量的估计网络，供作图
for n in [500, 100]:
    X = simulate_symptoms(n, seed=3)
    P, lam = ebic_glasso(X)
    P_hat[n] = P
    est = {(i, j) for i, j in zip(*iu) if P[i, j] != 0}
    print(f"n = {n}: 选中 λ = {lam:.3f}，边数 {len(est)}，真实边命中 {len(est & true_set)}/10，虚假边 {len(est - true_set)}")
    print(f"        真实边平均权重（真值 0.27）: {np.mean([P[e] for e in true_set]):.3f}")

import networkx as nx
import matplotlib.pyplot as plt

def draw_signed(ax, M, labels, thr, title, node_color="#DDDDDD", node_size=180, pos=None):
    """边宽 ∝ |权重|，蓝色为正边、红色为负边。"""
    n = len(labels)
    pos = nx.circular_layout(range(n)) if pos is None else pos
    G = nx.Graph(); G.add_nodes_from(range(n))
    G.add_weighted_edges_from((i, j, M[i, j]) for i in range(n) for j in range(i + 1, n) if abs(M[i, j]) > thr)
    ws = [d["weight"] for _, _, d in G.edges(data=True)]
    nx.draw_networkx_edges(G, pos, ax=ax, width=[max(1.0, 8 * abs(w)) for w in ws],
                           edge_color=["#4477AA" if w > 0 else "#CC6677" for w in ws])
    nx.draw_networkx_nodes(G, pos, ax=ax, node_size=node_size, node_color=node_color, edgecolors="k")
    lab_pos = {k: (1.22 * np.asarray(v)) for k, v in pos.items()}
    nx.draw_networkx_labels(G, lab_pos, labels=dict(enumerate(labels)), ax=ax, font_size=9)
    ax.plot([], [], color="#4477AA", lw=2, label="positive")
    ax.plot([], [], color="#CC6677", lw=2, label="negative")
    ax.legend(loc="lower right", fontsize=7, frameon=False)
    ax.set_title(title, fontsize=10); ax.set_aspect("equal"); ax.axis("off")
    ax.set_xlim(-1.45, 1.45); ax.set_ylim(-1.45, 1.45)

abbr = ["Anh", "Sad", "Slp", "Fat", "App", "Gui", "Con", "Mot", "Sui"]
Ptrue = np.zeros((9, 9))
for (i, j), w in TRUE_EDGES.items():
    Ptrue[i, j] = Ptrue[j, i] = w
fig, axes = plt.subplots(1, 2, figsize=(10, 4.4))
draw_signed(axes[0], P_hat[500], abbr, 0, f"EBICglasso network, n = 500 ({int(np.sum(P_hat[500][iu] != 0))} edges)")
for n, mk, col in [(500, "o", "#4477AA"), (100, "s", "#CC6677")]:
    axes[1].scatter(Ptrue[iu], P_hat[n][iu], marker=mk, s=40, color=col, alpha=0.7, label=f"n = {n}")
axes[1].plot([0, 0.45], [0, 0.45], "k--", lw=0.8, label="identity")
axes[1].axhline(0, color="gray", lw=0.6)
axes[1].set(xlabel="True partial correlation", ylabel="EBICglasso estimate", title="Shrinkage: estimates fall below identity")
axes[1].legend(fontsize=8)
plt.tight_layout(); plt.show()

# %% 示例：二值症状的 Ising 模型——Gibbs 抽样与逐节点 L1 逻辑回归（eLasso 思路）
# 先用 Gibbs 抽样从已知 Ising 模型生成 0/1 症状数据（模拟数据，仅用于演示方法），
# 再对每个节点做 L1 正则化逻辑回归（近端梯度法），用 EBIC（γ = 0.25）选 λ，
# 最后用 AND 规则合并：β_ij 与 β_ji 都非零才保留边，边权取二者平均。
# 输出解读：n = 1000 时边的有无基本恢复正确，但部分边权被 L1 惩罚明显压小（收缩偏倚），
# 阈值估计也相应偏离真值。ω_ij 是"其余症状固定时，i 与 j 的条件对数优势比"，
# 例如 ω = 1.2 意味着条件优势比 e^1.2 ≈ 3.3。阈值 τ 为负表示其余症状都不出现时该症状倾向于不出现。
import numpy as np

p = 7
OMEGA = np.zeros((p, p))
for (i, j), w in {(0, 1): 1.2, (1, 2): 1.0, (2, 3): 0.8, (3, 4): 1.2, (4, 5): 1.0,
                  (5, 6): 0.8, (0, 6): 1.0}.items():
    OMEGA[i, j] = OMEGA[j, i] = w
TAU = np.full(p, -1.5)

def gibbs_ising(omega, tau, n, sweeps=200, seed=0):
    """对 n 条独立链并行 Gibbs 抽样，每条链取最后一个状态作为一名被试。"""
    rng = np.random.default_rng(seed)
    x = rng.integers(0, 2, size=(n, len(tau))).astype(float)
    for _ in range(sweeps):
        for i in range(len(tau)):
            eta = tau[i] + x @ omega[:, i]       # omega 对角为 0
            x[:, i] = rng.random(n) < 1 / (1 + np.exp(-eta))
    return x

def l1_logistic(Z, y, lam, beta0=None, iters=500):
    """近端梯度：min −(1/n)Σ loglik + λ|β|₁（截距不惩罚）。"""
    n, k = Z.shape
    A = np.column_stack([np.ones(n), Z])
    b = np.zeros(k + 1) if beta0 is None else beta0.copy()
    step = 4.0 / (np.linalg.norm(A, 2) ** 2 / n)
    for _ in range(iters):
        mu = 1 / (1 + np.exp(-A @ b))
        b = b - step * (A.T @ (mu - y) / n)
        b[1:] = np.sign(b[1:]) * np.maximum(np.abs(b[1:]) - step * lam, 0)
    return b

def ising_elasso(X, gamma=0.25, n_lambda=30):
    n, p = X.shape
    B = np.zeros((p, p))
    tau_hat = np.zeros(p)
    for i in range(p):
        Z, y = np.delete(X, i, axis=1), X[:, i]
        lam_max = np.max(np.abs(Z.T @ (y - y.mean()))) / n
        best, b = None, None
        for lam in np.exp(np.linspace(np.log(lam_max), np.log(0.01 * lam_max), n_lambda)):
            b = l1_logistic(Z, y, lam, b)
            eta = b[0] + Z @ b[1:]
            ll = np.sum(y * eta - np.log1p(np.exp(eta)))
            k = int(np.sum(np.abs(b[1:]) > 1e-6))
            ebic = -2 * ll + k * np.log(n) + 2 * gamma * k * np.log(p - 1)
            if best is None or ebic < best[0]:
                best = (ebic, b.copy())
        B[i, np.arange(p) != i] = best[1][1:]
        tau_hat[i] = best[1][0]
    nz = (np.abs(B) > 1e-6) & (np.abs(B.T) > 1e-6)  # AND 规则
    return np.where(nz, (B + B.T) / 2, 0.0), tau_hat

X = gibbs_ising(OMEGA, TAU, n=1000)
print("各症状出现率：", np.round(X.mean(axis=0), 2))
W, tau_hat = ising_elasso(X)
iu = np.triu_indices(p, 1)
true_e = {(i, j) for i, j in zip(*iu) if OMEGA[i, j] != 0}
est_e = {(i, j) for i, j in zip(*iu) if W[i, j] != 0}
print(f"真实边 {len(true_e)} 条；估计边 {len(est_e)} 条，命中 {len(est_e & true_e)}，虚假 {len(est_e - true_e)}")
for (i, j) in sorted(true_e):
    print(f"  边 {i}-{j}: 真值 ω = {OMEGA[i, j]:.1f}，估计 {W[i, j]:.2f}")
print("阈值估计 τ：", np.round(tau_hat, 2), "（真值均为 −1.5）")

import networkx as nx
import matplotlib.pyplot as plt
fig, axes = plt.subplots(1, 2, figsize=(10, 4.2))
pos = nx.circular_layout(range(p))
G = nx.Graph(); G.add_nodes_from(range(p))
G.add_weighted_edges_from((i, j, W[i, j]) for i, j in zip(*iu) if W[i, j] != 0)
for es, style, col in [([e for e in G.edges() if tuple(sorted(e)) in true_e], "solid", "#4477AA"),
                       ([e for e in G.edges() if tuple(sorted(e)) not in true_e], "dashed", "#CC6677")]:
    nx.draw_networkx_edges(G, pos, edgelist=es, ax=axes[0], style=style, edge_color=col,
                           width=[3 * abs(G[u][v]["weight"]) for u, v in es])
nx.draw_networkx_nodes(G, pos, ax=axes[0], node_size=180, node_color="#DDDDDD", edgecolors="k")
nx.draw_networkx_labels(G, {k: 1.2 * v for k, v in pos.items()}, labels={i: f"S{i + 1}" for i in range(p)}, ax=axes[0], font_size=9)
axes[0].set_title(f"Estimated Ising network (solid: true edge, dashed: false), n = {len(X)}", fontsize=9)
axes[0].set_aspect("equal"); axes[0].axis("off"); axes[0].set_xlim(-1.4, 1.4); axes[0].set_ylim(-1.4, 1.4)
te = sorted(true_e)
x = np.arange(len(te))
axes[1].bar(x - 0.2, [OMEGA[e] for e in te], 0.4, color="#BBBBBB", label="true omega")
axes[1].bar(x + 0.2, [W[e] for e in te], 0.4, color="#4477AA", label="eLasso estimate")
axes[1].set_xticks(x, [f"S{i + 1}-S{j + 1}" for i, j in te], fontsize=8)
axes[1].set(ylabel="Edge weight (log-odds)", title="L1 shrinks edge weights toward 0")
axes[1].legend(fontsize=8)
plt.tight_layout(); plt.show()

# %% 示例：桥中心性——抑郁与焦虑症状之间的"桥"
# 构造一个两社团网络（抑郁 5 个症状、焦虑 5 个症状，模拟边权，仅用于演示方法），
# 按 Jones, Ma & McNally (2021) 的定义计算桥强度（与其他社团节点的边权绝对值之和）
# 与一步桥预期影响（保留符号），并与普通强度对比。
# 输出解读：普通强度最高的是"紧张不安""情绪低落"，桥强度最高的却是"注意力差""睡眠问题"（"疲乏"次之）——
# 它们承担了两个症状群之间的大部分连接，这是共病网络解释中"桥症状"的含义。
# 有负的跨社团边时（如"自我评价低–易激惹"），桥 EI 与桥强度不同。
# 桥中心性依赖事先给定的社团划分；划分改变，桥症状也会改变。
import numpy as np
import networkx as nx

nodes = ["情绪低落", "兴趣减退", "自我评价低", "睡眠问题", "疲乏",       # 抑郁
         "过度担忧", "难以控制担忧", "紧张不安", "易激惹", "注意力差"]   # 焦虑
community = np.array([0] * 5 + [1] * 5)
edges = {(0, 1): .35, (0, 2): .25, (1, 2): .15, (0, 4): .15, (3, 4): .30, (1, 4): .10,
         (5, 6): .40, (5, 7): .20, (6, 7): .25, (7, 8): .20, (6, 9): .10, (8, 9): .10,
         (3, 7): .20, (3, 9): .15, (4, 9): .25, (0, 5): .08, (2, 8): -.05}
W = np.zeros((10, 10))
for (i, j), w in edges.items():
    W[i, j] = W[j, i] = w

strength = np.abs(W).sum(axis=1)
other = community[:, None] != community[None, :]
bridge_strength = (np.abs(W) * other).sum(axis=1)
bridge_ei1 = (W * other).sum(axis=1)

order = np.argsort(bridge_strength)[::-1]
print(f"{'症状':<8}{'社团':>4}{'强度':>8}{'桥强度':>8}{'桥EI(1)':>9}")
for i in order:
    print(f"{nodes[i]:<8}{'抑郁' if community[i] == 0 else '焦虑':>4}{strength[i]:>8.2f}"
          f"{bridge_strength[i]:>8.2f}{bridge_ei1[i]:>9.2f}")
cut = np.quantile(bridge_strength, 0.8)
print("桥强度位于前 20% 的症状（应用研究常用的经验界限，非统计检验）：",
      [nodes[i] for i in range(10) if bridge_strength[i] >= cut])

G = nx.from_numpy_array(np.abs(W))
comms = [set(np.where(community == c)[0]) for c in (0, 1)]
print(f"按给定划分的模块度 Q = {nx.community.modularity(G, comms, weight='weight'):.3f}")

import matplotlib.pyplot as plt

def draw_signed(ax, M, labels, thr, title, node_color="#DDDDDD", node_size=180, pos=None):
    """边宽 ∝ |权重|，蓝色为正边、红色为负边。"""
    n = len(labels)
    pos = nx.circular_layout(range(n)) if pos is None else pos
    G = nx.Graph(); G.add_nodes_from(range(n))
    G.add_weighted_edges_from((i, j, M[i, j]) for i in range(n) for j in range(i + 1, n) if abs(M[i, j]) > thr)
    ws = [d["weight"] for _, _, d in G.edges(data=True)]
    nx.draw_networkx_edges(G, pos, ax=ax, width=[max(1.0, 8 * abs(w)) for w in ws],
                           edge_color=["#4477AA" if w > 0 else "#CC6677" for w in ws])
    nx.draw_networkx_nodes(G, pos, ax=ax, node_size=node_size, node_color=node_color, edgecolors="k")
    lab_pos = {k: (1.22 * np.asarray(v)) for k, v in pos.items()}
    nx.draw_networkx_labels(G, lab_pos, labels=dict(enumerate(labels)), ax=ax, font_size=9)
    ax.plot([], [], color="#4477AA", lw=2, label="positive")
    ax.plot([], [], color="#CC6677", lw=2, label="negative")
    ax.legend(loc="lower right", fontsize=7, frameon=False)
    ax.set_title(title, fontsize=10); ax.set_aspect("equal"); ax.axis("off")
    ax.set_xlim(-1.45, 1.45); ax.set_ylim(-1.45, 1.45)

abbr = ["Sad", "Anh", "Wth", "Slp", "Fat", "Wry", "Ctl", "Nrv", "Irr", "Con"]   # 前 5 个抑郁，后 5 个焦虑
fig, axes = plt.subplots(1, 2, figsize=(10, 4.4))
draw_signed(axes[0], W, abbr, 0, "Depression (orange) and anxiety (blue) symptoms",
            node_color=np.where(community == 0, "#EE8866", "#77AADD"),
            node_size=60 + 140 * bridge_strength / bridge_strength.max())
axes[0].text(0, -1.42, "node size = bridge strength", ha="center", fontsize=8)
x = np.arange(10)
axes[1].bar(x - 0.2, strength, 0.4, color="#BBBBBB", label="strength")
axes[1].bar(x + 0.2, bridge_strength, 0.4, color="#4477AA", label="bridge strength")
axes[1].set_xticks(x, abbr)
axes[1].set(ylabel="Sum of |edge weights|", title="Bridge symptoms differ from the most central ones")
axes[1].legend(fontsize=8)
plt.tight_layout(); plt.show()

# %% 示例：网络比较检验（NCT）的置换逻辑
# 两组被试（模拟数据，仅用于演示方法）：B 组在"睡眠问题–疲乏"上的真实偏相关更强，其余相同。
# 统计量：M = 两组边权差的最大绝对值（网络结构不变性），S = 两组全局强度之差的绝对值（全局强度不变性）。
# 零分布：把两组被试合并后随机重分组（保持组大小），重复 1000 次重新计算 M 与 S。
# 输出解读：M 的置换 p 值小，说明至少一条边不同；再逐边检验并做多重比较校正才能定位是哪条边。
# S 的 p 值不显著：一条边变强并不一定使全局强度显著改变，三类检验回答的是不同问题。
# 简化：这里用未正则化偏相关以便快速演示；NetworkComparisonTest 默认在每次置换中重新运行 EBICglasso。
import numpy as np

def make_K(extra=0.0):
    K = np.eye(6)
    for (i, j), w in {(0, 1): .3, (1, 2): .25, (2, 3): .3, (3, 4): .2, (4, 5): .3, (0, 5): .2}.items():
        K[i, j] = K[j, i] = -w
    K[2, 3] = K[3, 2] = -(0.3 + extra)   # 节点 2 = 睡眠问题，节点 3 = 疲乏
    return K

def pcor(X):
    K = np.linalg.inv(np.cov(X, rowvar=False))
    d = np.sqrt(np.diag(K))
    P = -K / np.outer(d, d)
    np.fill_diagonal(P, 0)
    return P

rng = np.random.default_rng(7)
nA, nB = 400, 400
XA = rng.multivariate_normal(np.zeros(6), np.linalg.inv(make_K()), size=nA)
XB = rng.multivariate_normal(np.zeros(6), np.linalg.inv(make_K(0.25)), size=nB)
iu = np.triu_indices(6, 1)

def stats(XA, XB):
    D = pcor(XA)[iu] - pcor(XB)[iu]
    S = abs(np.abs(pcor(XA)[iu]).sum() - np.abs(pcor(XB)[iu]).sum())
    return np.max(np.abs(D)), S, np.abs(D)

M0, S0, D0 = stats(XA, XB)
Xall = np.vstack([XA, XB])
perm_M, perm_S, perm_D = [], [], []
for _ in range(1000):
    idx = rng.permutation(nA + nB)
    m, s, d = stats(Xall[idx[:nA]], Xall[idx[nA:]])
    perm_M.append(m); perm_S.append(s); perm_D.append(d)
perm_D = np.array(perm_D)
p_M = (1 + np.sum(np.array(perm_M) >= M0)) / 1001
p_S = (1 + np.sum(np.array(perm_S) >= S0)) / 1001
print(f"网络结构不变性：M = {M0:.3f}，置换 p = {p_M:.3f}")
print(f"全局强度不变性：S = {S0:.3f}，置换 p = {p_S:.3f}")
p_edge = (1 + (perm_D >= D0).sum(axis=0)) / 1001
m = len(p_edge)                          # Holm 校正
order = np.argsort(p_edge)
p_holm = np.empty(m)
p_holm[order] = np.minimum(1, np.maximum.accumulate((m - np.arange(m)) * p_edge[order]))
for k, (i, j) in enumerate(zip(*iu)):
    if p_holm[k] < 0.05:
        print(f"Holm 校正后显著不同的边：{i}-{j}，|Δw| = {D0[k]:.3f}，p_holm = {p_holm[k]:.3f}")

import matplotlib.pyplot as plt
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
axes[0].hist(perm_M, bins=30, color="#BBBBBB", edgecolor="k", lw=0.4, label="permutations")
axes[0].axvline(M0, color="crimson", lw=2, label=f"observed M (p = {p_M:.3f})")
axes[0].set(xlabel="Max |edge difference| M", ylabel="Count", title="Network structure invariance test")
axes[0].legend(fontsize=8)
x = np.arange(len(D0))
axes[1].bar(x, D0, color=np.where(p_holm < 0.05, "crimson", "#4477AA"))
axes[1].scatter(x, np.quantile(perm_D, 0.95, axis=0), marker="_", s=300, color="k", label="permutation 95th pct")
axes[1].set_xticks(x, [f"{i}-{j}" for i, j in zip(*iu)], fontsize=8)
axes[1].set(xlabel="Edge (node 2 = sleep, 3 = fatigue)", ylabel="|pcor_A - pcor_B|", title="Edge-wise tests (red: Holm p < 0.05)")
axes[1].legend(fontsize=8)
plt.tight_layout(); plt.show()

# %% 示例：个体内与个体间网络可以方向相反——多被试 VAR(1) 与 GVAR 的三种网络
# 模拟 100 名被试，每人 100 个时间点（模拟数据，仅用于演示方法）。个体内：上一时刻"压力"升高
# 使下一时刻"情绪低落"升高（时间效应 +0.3）；同一时刻两者残差正相关（同期效应）。
# 个体间：平均压力高的人平均情绪低落反而低（例如这些人有更多社会支持；人为设定的负相关）。
# 依次估计：时间网络（对个体中心化的滞后值做回归）、同期网络（残差相关）、个体间网络（个人均值相关），
# 再看把所有观测直接合并算出的相关。
# 输出解读：三种网络回答不同的问题；直接合并的相关混合了个体内（正）与个体间（负）两种来源，
# 可能接近 0 甚至符号错误。这是 mlVAR/GVAR 要把三者分开估计的原因。
import numpy as np

rng = np.random.default_rng(11)
N, T = 100, 100
A = np.array([[0.3, 0.0],        # 变量 0 = 压力，1 = 情绪低落；A[j, i] 为 i(t−1) → j(t)
              [0.3, 0.3]])
Sig_e = np.array([[1.0, 0.4], [0.4, 1.0]])
L = np.linalg.cholesky(Sig_e)
mu = rng.multivariate_normal([0, 0], [[1.0, -0.7], [-0.7, 1.0]], size=N)   # 个体均值：个体间负相关

data = []
for k in range(N):
    y = np.zeros((T + 50, 2))
    for t in range(1, T + 50):
        y[t] = A @ y[t - 1] + L @ rng.standard_normal(2)
    data.append(y[50:] + mu[k])
data = np.array(data)                       # N × T × 2

means = data.mean(axis=1)
Yc = data - means[:, None, :]               # 个体中心化（within-person centering）
Xlag = Yc[:, :-1, :].reshape(-1, 2)
Ynow = Yc[:, 1:, :].reshape(-1, 2)
coef, *_ = np.linalg.lstsq(Xlag, Ynow, rcond=None)
A_hat = coef.T
resid = Ynow - Xlag @ coef
r_contemp = np.corrcoef(resid, rowvar=False)[0, 1]
r_between = np.corrcoef(means, rowvar=False)[0, 1]
r_pooled = np.corrcoef(data.reshape(-1, 2), rowvar=False)[0, 1]

print("时间网络（个体内，有向）：")
print(f"  压力(t−1) → 情绪低落(t)：{A_hat[1, 0]:+.2f}（真值 +0.30）")
print(f"  情绪低落(t−1) → 压力(t)：{A_hat[0, 1]:+.2f}（真值 0）")
print(f"同期网络（残差相关，两个变量时等于偏相关）：{r_contemp:+.2f}（真值 +0.40）")
print(f"个体间网络（个人均值相关）：{r_between:+.2f}（设定 −0.70）")
print(f"所有观测直接合并的相关：{r_pooled:+.2f}")
print("注：真实 mlVAR 用多层模型给每人估计随机效应；此处共享同一时间效应，仅演示三种网络的区分。")

import matplotlib.pyplot as plt
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
x = np.arange(4)
axes[0].bar(x, [A_hat[1, 0], r_contemp, r_between, r_pooled], color=["#4477AA", "#4477AA", "#CC6677", "#BBBBBB"])
axes[0].scatter(x[:3], [0.3, 0.4, -0.7], marker="D", color="k", zorder=3, label="true / set value")
axes[0].axhline(0, color="k", lw=0.6)
axes[0].set_xticks(x, ["Temporal\nstress->mood", "Contemporaneous", "Between-\nperson", "Pooled r"], fontsize=8)
axes[0].set(ylabel="Estimate", title="Three networks answer different questions")
axes[0].legend(fontsize=8)
for k in range(0, N, 5):                    # 每 5 人取 1 人，画其个体内回归线（±1 SD 范围）
    xs, ys = data[k, :, 0], data[k, :, 1]
    xx = xs.mean() + np.array([-1, 1]) * xs.std()
    axes[1].plot(xx, ys.mean() + np.polyfit(xs, ys, 1)[0] * (xx - xs.mean()), color="#4477AA", lw=1.2)
axes[1].plot([], [], color="#4477AA", label="within-person fits (20 people)")
axes[1].scatter(means[:, 0], means[:, 1], s=20, color="k", marker="x", label="person means (all 100)")
xx = np.linspace(means[:, 0].min(), means[:, 0].max(), 2)
axes[1].plot(xx, np.polyval(np.polyfit(means[:, 0], means[:, 1], 1), xx), "--", color="#CC6677", lw=2,
             label="between-person fit")
axes[1].set(xlabel="Stress", ylabel="Low mood", title="Within-person slopes up; between-person slope down")
axes[1].legend(fontsize=8)
plt.tight_layout(); plt.show()

# %% 示例：网络干预分析（NIA）——把"治疗分组"作为网络中的一个节点
# 模拟一项随机对照试验（模拟数据，仅用于演示方法）：治疗只直接改善"睡眠问题"，
# 睡眠改善再通过"疲乏"间接改善"情绪低落"。治疗后把分组变量（0/1）与症状放在同一网络中估计偏相关。
# 输出解读：分组与三个症状的简单相关都不为 0（总效应），但在偏相关网络中，
# 只有"分组–睡眠问题"有明显的边——条件于其他症状后，治疗对疲乏与情绪的关联消失，
# 提示其效应可能经由睡眠传递。这是 Blanken 等 (2019) NIA 的基本逻辑；
# 横截面的单个时间点不能确定先后，原研究用逐周重复测量来看效应如何在网络中展开。
import numpy as np

rng = np.random.default_rng(5)
n = 600
treat = np.repeat([0, 1], n // 2)
sleep = 1.0 - 0.8 * treat + rng.standard_normal(n)
fatigue = 0.6 * sleep + rng.standard_normal(n)
mood = 0.5 * fatigue + 0.2 * sleep + rng.standard_normal(n)
worry = 0.4 * mood + rng.standard_normal(n)
names = ["分组(治疗=1)", "睡眠问题", "疲乏", "情绪低落", "担忧"]
X = np.column_stack([treat, sleep, fatigue, mood, worry])

R = np.corrcoef(X, rowvar=False)
K = np.linalg.inv(np.cov(X, rowvar=False))
d = np.sqrt(np.diag(K))
P = -K / np.outer(d, d)
print(f"{'症状':<8}{'与分组的相关':>10}{'与分组的偏相关':>12}")
for j in range(1, 5):
    print(f"{names[j]:<8}{R[0, j]:>12.2f}{P[0, j]:>14.2f}")

import networkx as nx
import matplotlib.pyplot as plt

def draw_signed(ax, M, labels, thr, title, node_color="#DDDDDD", node_size=180, pos=None):
    """边宽 ∝ |权重|，蓝色为正边、红色为负边。"""
    n = len(labels)
    pos = nx.circular_layout(range(n)) if pos is None else pos
    G = nx.Graph(); G.add_nodes_from(range(n))
    G.add_weighted_edges_from((i, j, M[i, j]) for i in range(n) for j in range(i + 1, n) if abs(M[i, j]) > thr)
    ws = [d["weight"] for _, _, d in G.edges(data=True)]
    nx.draw_networkx_edges(G, pos, ax=ax, width=[max(1.0, 8 * abs(w)) for w in ws],
                           edge_color=["#4477AA" if w > 0 else "#CC6677" for w in ws])
    nx.draw_networkx_nodes(G, pos, ax=ax, node_size=node_size, node_color=node_color, edgecolors="k")
    lab_pos = {k: (1.22 * np.asarray(v)) for k, v in pos.items()}
    nx.draw_networkx_labels(G, lab_pos, labels=dict(enumerate(labels)), ax=ax, font_size=9)
    ax.plot([], [], color="#4477AA", lw=2, label="positive")
    ax.plot([], [], color="#CC6677", lw=2, label="negative")
    ax.legend(loc="lower right", fontsize=7, frameon=False)
    ax.set_title(title, fontsize=10); ax.set_aspect("equal"); ax.axis("off")
    ax.set_xlim(-1.45, 1.45); ax.set_ylim(-1.45, 1.45)

abbr = ["Treat", "Slp", "Fat", "Sad", "Wry"]
fig, axes = plt.subplots(1, 2, figsize=(10, 4.2))
x = np.arange(1, 5)
axes[0].bar(x - 0.2, R[0, 1:], 0.4, color="#BBBBBB", label="correlation with treatment")
axes[0].bar(x + 0.2, P[0, 1:], 0.4, color="#4477AA", label="partial correlation")
axes[0].axhline(0, color="k", lw=0.6)
axes[0].set_xticks(x, abbr[1:])
axes[0].set(ylabel="Association with treatment", title="Total vs direct association")
axes[0].legend(fontsize=8)
P0 = P.copy(); np.fill_diagonal(P0, 0)
draw_signed(axes[1], P0, abbr, 0.1, "Partial correlation network (|pcor| > 0.1)",
            node_color=["#EE8866"] + ["#DDDDDD"] * 4)
plt.tight_layout(); plt.show()

# %% 示例：节点可预测性——由精度矩阵直接得到每个症状的 R²
# 对标准化变量，把症状 i 对其余全部症状做线性回归，残差方差为 1/K_ii，
# 因此可预测性 R²_i = 1 − 1/K_ii（Haslbeck & Waldorp, 2018 的连续变量版本，此处为样本内值）。
# 代码同时用逐个回归验证这一等式。
# 输出解读：高可预测性的症状（如疲乏、情绪低落）被其邻居解释得多；可预测性低的症状
# 主要由网络外的因素决定，从网络内部"干预邻居"去改变它，预期效果有限。
import numpy as np

TRUE_EDGES = {(0, 1): .40, (1, 5): .30, (1, 8): .25, (5, 8): .25, (2, 3): .40,
              (3, 6): .30, (3, 7): .20, (3, 4): .20, (0, 3): .20, (6, 7): .20}
names = ["兴趣减退", "情绪低落", "睡眠问题", "疲乏", "食欲改变",
         "自我评价低", "注意力差", "精神运动改变", "自杀意念"]
K0 = np.eye(9)
for (i, j), w in TRUE_EDGES.items():
    K0[i, j] = K0[j, i] = -w
rng = np.random.default_rng(0)
X = rng.multivariate_normal(np.zeros(9), np.linalg.inv(K0), size=500)   # 模拟数据，仅用于演示方法
Z = (X - X.mean(0)) / X.std(0)

R = np.corrcoef(Z, rowvar=False)
K = np.linalg.inv(R)
r2_formula = 1 - 1 / np.diag(K)
r2_reg = []
for i in range(9):
    A = np.delete(Z, i, axis=1)
    b, *_ = np.linalg.lstsq(A, Z[:, i], rcond=None)
    r2_reg.append(1 - np.var(Z[:, i] - A @ b) / np.var(Z[:, i]))
for i in np.argsort(r2_formula)[::-1]:
    print(f"{names[i]:<8} R² = {r2_formula[i]:.3f}（逐个回归：{r2_reg[i]:.3f}）")

import networkx as nx
import matplotlib.pyplot as plt
abbr = ["Anh", "Sad", "Slp", "Fat", "App", "Gui", "Con", "Mot", "Sui"]
dk = np.sqrt(np.diag(K)); Pc = -K / np.outer(dk, dk); np.fill_diagonal(Pc, 0)
fig, axes = plt.subplots(1, 2, figsize=(10, 4.2))
pos = nx.circular_layout(range(9))
G = nx.Graph(); G.add_nodes_from(range(9))
G.add_weighted_edges_from((i, j, Pc[i, j]) for i in range(9) for j in range(i + 1, 9) if abs(Pc[i, j]) > 0.1)
ws = [d["weight"] for _, _, d in G.edges(data=True)]
nx.draw_networkx_edges(G, pos, ax=axes[0], width=[max(1.0, 8 * abs(w)) for w in ws],
                       edge_color=["#4477AA" if w > 0 else "#CC6677" for w in ws])
nodes = nx.draw_networkx_nodes(G, pos, ax=axes[0], node_size=200, node_color=r2_formula, cmap="Oranges",
                               vmin=0, vmax=r2_formula.max(), edgecolors="k")
nx.draw_networkx_labels(G, {k: 1.22 * v for k, v in pos.items()}, labels=dict(enumerate(abbr)), ax=axes[0], font_size=9)
fig.colorbar(nodes, ax=axes[0], shrink=0.7, label="$R^2$")
axes[0].set_title("Node colour = predictability (|pcor| > 0.1 shown)", fontsize=10)
axes[0].set_aspect("equal"); axes[0].axis("off"); axes[0].set_xlim(-1.45, 1.45); axes[0].set_ylim(-1.45, 1.45)
order = np.argsort(r2_formula)
axes[1].barh(np.arange(9), r2_formula[order], color="#4477AA", label="$1 - 1/K_{ii}$")
axes[1].scatter(np.array(r2_reg)[order], np.arange(9), marker="|", color="k", s=200, zorder=3, label="per-node regression")
axes[1].set_yticks(range(9), [abbr[i] for i in order])
axes[1].set(xlabel="Node predictability $R^2$", title="Precision matrix gives $R^2$ directly")
axes[1].legend(fontsize=8, loc="lower right")
plt.tight_layout(); plt.show()
