# 依赖：networkx>=3, numpy, scipy, matplotlib
# 数据：全部为程序生成的模拟数据，仅用于演示方法，不对应任何真实物种。
#   “蛋白相互作用网络”用 BA 无标度网络模拟（无向图，节点 = 蛋白，边 = 相互作用）；
#   “转录调控网络”是嵌入了前馈环的随机有向图（有向边 TF → 靶基因）；
#   表达动力学由简化的阶跃型调控模型生成；
#   AP-MS 拉下、互补界面 PPI、玩具代谢网络、含复合物的 PPI、两条件表达矩阵与两类组学的患者数据
#   也都在各单元内用固定随机种子生成。
#   真实数据可从 STRING（建议限定实验证据渠道）、BioGRID、TRRUST 等数据库下载为边列表，
#   用 nx.read_edgelist 读入后套用同样代码。

# %% 示例：重尾度分布与 Jeong 式统计
# 比较 1500 节点的 BA 网络（模拟 PPI）与同节点数、同边数的 ER 随机网络：
# (a) 画度的互补累积分布（CCDF）双对数图；(b) 仿照 Jeong 等（2001）统计度 ≤ 5 与度 > 15 的节点比例。
# 输出解读：BA 网络的 CCDF 呈长尾，存在度很大的枢纽；ER 网络几乎没有度 > 15 的节点。
# 注意：CCDF 近似直线不等于证明了幂律，严格判断需最大似然拟合与替代分布比较。
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

G_ba = nx.barabasi_albert_graph(1500, 2, seed=1)   # 模拟数据，仅用于演示方法
G_er = nx.gnm_random_graph(1500, G_ba.number_of_edges(), seed=1)

def ccdf(G):
    """返回 (ks, P)：ks 为排序后的不同度值，P[i] = 度 >= ks[i] 的节点比例。"""
    deg = np.array([d for _, d in G.degree()])
    ks = np.unique(deg)
    P = np.array([np.mean(deg >= k) for k in ks])
    return ks, P

for name, G in [("BA", G_ba), ("ER", G_er)]:
    deg = np.array([d for _, d in G.degree()])
    print(f"{name}：度 ≤ 5 的比例 = {np.mean(deg <= 5):.3f}，度 > 15 的比例 = {np.mean(deg > 15):.3f}，最大度 = {deg.max()}")
    ks, P = ccdf(G)
    plt.loglog(ks, P, "o", ms=3, label=name)
plt.xlabel("k"); plt.ylabel("P(K ≥ k)"); plt.legend(); plt.title("CCDF of degree (simulated)")
plt.show()

# %% 示例：删除枢纽与随机删除对巨连通分支的影响
# 分别按度从高到低、以及随机顺序删除 0–20% 的节点，记录最大连通分支占原网络节点数的比例。
# 输出解读：随机删除时巨分支缓慢缩小；优先删除枢纽时巨分支迅速崩塌。
# 这种“网络碎裂”是中心性–致死性规则最初的解释之一，但它并不能单独证明枢纽必需性的机制
# （竞争解释还有必需相互作用、必需复合物与研究偏倚）。
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

G = nx.barabasi_albert_graph(1500, 2, seed=1)   # 模拟数据，仅用于演示方法
N = G.number_of_nodes()
fracs = np.linspace(0, 0.2, 11)

def giant_fraction_after_removal(G, order, f):
    """删除 order 中前 int(f*N) 个节点，返回最大连通分支节点数 / 原网络节点数。"""
    N = G.number_of_nodes()
    H = G.copy()
    H.remove_nodes_from(order[:int(f * N)])
    if H.number_of_nodes() == 0:
        return 0.0
    return len(max(nx.connected_components(H), key=len)) / N

rng = np.random.default_rng(0)
order_hub = [n for n, _ in sorted(G.degree(), key=lambda x: -x[1])]
order_rand = list(rng.permutation(list(G.nodes())))
res = {"hubs first": [giant_fraction_after_removal(G, order_hub, f) for f in fracs],
       "random": [giant_fraction_after_removal(G, order_rand, f) for f in fracs]}
for k, v in res.items():
    print(k, [round(x, 2) for x in v])
plt.plot(fracs, res["random"], "o-", label="random")
plt.plot(fracs, res["hubs first"], "s-", label="hubs first")
plt.xlabel("fraction removed"); plt.ylabel("giant component fraction"); plt.legend()
plt.show()

# %% 示例：前馈环计数与保持入度/出度的随机化零模型（网络基序 Z 分数）
# 构造 200 个节点的有向“调控网络”：随机有向边 + 人为嵌入的 30 个前馈环（X→Y、Y→Z、X→Z）。
# count_ffl 统计满足 X→Y、Y→Z、X→Z 的三元组数；用有向边交换生成 30 个保持每个节点入度和出度的
# 随机化网络作为对照，计算 Z = (N_real − mean N_rand) / sd N_rand 与计数比。
# 输出解读：真实网络的 FFL 数远多于随机化网络，Z 很大，说明 FFL 在此网络中是“基序”。
# 正式分析应使用更多随机网络（如 1000 个），并同时报告经验 p 值。
import numpy as np
import networkx as nx

def make_trn(seed=0):
    """模拟数据，仅用于演示方法：随机有向网络 + 嵌入的前馈环。"""
    rng = np.random.default_rng(seed)
    D = nx.gnm_random_graph(200, 300, directed=True, seed=seed)
    for _ in range(30):
        x, y, z = rng.choice(200, 3, replace=False)
        D.add_edges_from([(x, y), (y, z), (x, z)])
    D.remove_edges_from(list(nx.selfloop_edges(D)))
    return D

def count_ffl(D):
    """对每条边 (x, y)，统计同时满足 y→z 且 x→z 的 z（z 不等于 x、y），累加返回。"""
    total = 0
    for x, y in D.edges():
        common = set(D.successors(x)) & set(D.successors(y))
        common.discard(x); common.discard(y)
        total += len(common)
    return total

def degree_preserving_shuffle(D, n_swap, rng):
    """有向边交换：(a→b, c→d) 换成 (a→d, c→b)，保持所有节点的入度和出度。"""
    D = D.copy()
    edges = list(D.edges())
    done = 0
    while done < n_swap:
        i, j = rng.integers(len(edges), size=2)
        (a, b), (c, d) = edges[i], edges[j]
        if len({a, b, c, d}) < 4 or D.has_edge(a, d) or D.has_edge(c, b):
            continue
        D.remove_edges_from([(a, b), (c, d)]); D.add_edges_from([(a, d), (c, b)])
        edges[i], edges[j] = (a, d), (c, b)
        done += 1
    return D

D = make_trn()
n_real = count_ffl(D)
rng = np.random.default_rng(1)
null = [count_ffl(degree_preserving_shuffle(D, 3 * D.number_of_edges(), rng)) for _ in range(30)]
z = (n_real - np.mean(null)) / (np.std(null) + 1e-9)
print(f"真实网络 FFL 数 = {n_real}，随机化均值 = {np.mean(null):.1f} ± {np.std(null):.1f}，Z = {z:.1f}，"
      f"计数比 = {n_real / max(np.mean(null), 1e-9):.1f}")

import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(6.4, 4.2))
ax.hist(null, bins=10, color="0.65", edgecolor="white", label="degree-preserving null (30 networks)")
ax.axvline(n_real, color="C3", lw=2, label=f"real network ({n_real})")
ax.set_xlabel("number of feed-forward loops"); ax.set_ylabel("count")
ax.set_title(f"FFL is a network motif (Z = {z:.1f})"); ax.legend(loc="upper center")
plt.tight_layout(); plt.show()

# %% 示例：一致型 1 型前馈环（与门）的持续性检测
# 用欧拉法（步长 0.01，总时长 15）模拟两种线路对输入 X 脉冲的响应：
#   简单调控：dZ/dt = beta·X − alpha·Z；
#   一致型 1 型 FFL（与门）：dY/dt = beta·X − alpha·Y，dZ/dt = beta·X·θ(Y > K_yz) − alpha·Z。
# 输入为短脉冲（持续 0.5）与长脉冲（持续 4）。
# 输出解读：简单调控对两种脉冲都响应；FFL 对短脉冲不响应、对长脉冲延迟响应。
# 理论延迟 T_on = (1/alpha)·ln(1/(1 − K_yz/Y_st))，此处 Y_st = beta/alpha = 1、K_yz = 0.5，T_on = ln2 ≈ 0.69，
# 短于 T_on 的脉冲被过滤。改变 K_yz 或 alpha，延迟随之改变：结构相同、参数不同，功能也会不同。
import numpy as np
import matplotlib.pyplot as plt

def simulate(pulse_len, ffl=True, beta=1.0, alpha=1.0, K_yz=0.5, dt=0.01, T=15.0, t_on=1.0):
    """模拟数据，仅用于演示方法：阶跃型调控函数的简化模型。"""
    t = np.arange(0, T, dt)
    X = ((t >= t_on) & (t < t_on + pulse_len)).astype(float)
    Y = np.zeros_like(t); Z = np.zeros_like(t)
    for i in range(1, len(t)):
        Y[i] = Y[i - 1] + dt * (beta * X[i - 1] - alpha * Y[i - 1])
        gate = (Y[i - 1] > K_yz) if ffl else 1.0
        Z[i] = Z[i - 1] + dt * (beta * X[i - 1] * gate - alpha * Z[i - 1])
    return t, X, Y, Z

print(f"理论延迟 T_on = ln2 ≈ {np.log(2):.2f}")
fig, axes = plt.subplots(1, 2, figsize=(10, 3.5))
for ax, L in zip(axes, [0.5, 4.0]):
    t, X, Y, Z_ffl = simulate(L, ffl=True)
    _, _, _, Z_simple = simulate(L, ffl=False)
    ax.plot(t, X, "k--", label="X input")
    ax.plot(t, Z_simple, label="Z (simple)")
    ax.plot(t, Z_ffl, label="Z (C1-FFL, AND)")
    ax.set_title(f"pulse length = {L}"); ax.set_xlabel("time")
    print(f"脉冲 {L}：简单调控 Z 峰值 = {Z_simple.max():.2f}，FFL 的 Z 峰值 = {Z_ffl.max():.2f}")
axes[0].legend()
plt.tight_layout(); plt.show()

# %% 示例：AP-MS 拉下数据的 spoke 模型与 matrix 模型
# 模拟 40 个蛋白复合物（每个 3–8 个亚基，复合物内部的“真实二元接触”是一棵随机生成树加少量额外边），
# 对随机选取的 30% 蛋白做“诱饵”拉下实验：拉下的是诱饵所在复合物的全部成员（检出率 0.8）。
# spoke 模型只连 诱饵–猎物；matrix 模型把同一次拉下的所有蛋白两两相连。
# 输出解读：matrix 模型的边数约为 spoke 的两倍，覆盖的直接接触更多，但“非直接接触”的边也成倍增加；
# 在这个模拟中两种模型对直接接触的精确率都只有约 4 成。两者都把“共复合物”当成边，
# 因此都不等于二元相互作用图（Y2H 测的那一类）；复合物越大，matrix 模型引入的间接边越多（约按 s² 增长）。
import itertools
import numpy as np
import networkx as nx

rng = np.random.default_rng(3)
complexes, binary = [], set()
next_id = 0
for _ in range(40):                                  # 模拟数据，仅用于演示方法
    s = int(rng.integers(3, 9))
    members = list(range(next_id, next_id + s)); next_id += s
    complexes.append(members)
    T = nx.random_labeled_tree(s, seed=int(rng.integers(1e9))) if hasattr(nx, "random_labeled_tree") \
        else nx.random_tree(s, seed=int(rng.integers(1e9)))
    for a, b in T.edges():
        binary.add(frozenset((members[a], members[b])))
    for a, b in itertools.combinations(members, 2):  # 少量额外的直接接触
        if rng.random() < 0.15:
            binary.add(frozenset((a, b)))
member_of = {p: c for c in complexes for p in c}
proteins = np.arange(next_id)
baits = rng.choice(proteins, size=int(0.3 * len(proteins)), replace=False)

spoke, matrix = set(), set()
for b in baits:
    preys = [p for p in member_of[b] if p != b and rng.random() < 0.8]
    spoke |= {frozenset((b, p)) for p in preys}
    matrix |= {frozenset(e) for e in itertools.combinations([b] + preys, 2)}

for name, E in [("spoke", spoke), ("matrix", matrix)]:
    tp = len(E & binary)
    print(f"{name:6s}：边数 = {len(E):4d}，直接接触 = {tp:4d}，非直接 = {len(E) - tp:4d}"
          f"（精确率 {tp / len(E):.2f}），覆盖全部直接接触的比例 = {tp / len(binary):.2f}")
print(f"真实直接接触总数 = {len(binary)}；蛋白数 = {len(proteins)}；诱饵数 = {len(baits)}")

import matplotlib.pyplot as plt
tps = [len(E & binary) for E in (spoke, matrix)]
fps = [len(E) - t for E, t in zip((spoke, matrix), tps)]
fig, ax = plt.subplots(figsize=(6.4, 4.2))
ax.bar(["spoke", "matrix"], tps, width=0.5, color="C0", label="direct (binary) contact")
ax.bar(["spoke", "matrix"], fps, width=0.5, bottom=tps, color="0.75", label="indirect (co-complex only)")
ax.axhline(len(binary), color="k", ls="--", lw=1, label="all true binary contacts")
ax.set_ylabel("number of inferred edges")
ax.set_title("Matrix model adds many indirect edges"); ax.legend()
plt.tight_layout(); plt.show()

# %% 示例：互作组补全——共同邻居（L2）与长度为 3 的路径（L3）链路预测
# Kovács 等（2019）指出：蛋白往往通过互补界面结合，A 与 B 相互作用，并不意味着 A 与 B 的伙伴相似；
# 但若 A 与 B 的某个伙伴相似（共享伙伴），则 A 更可能与 B 结合，因此应数长度为 3 的路径（L3）。
# 这里用“界面类型互补”生成模拟网络：每个蛋白有一个类型，类型 t 只与互补类型 partner[t] 结合。
# 隐藏 10% 的边，比较 L2（共同邻居数）与度归一化 L3 打分对隐藏边的排序 AUC。
# 输出解读：在互补结合主导的网络中，L3 的 AUC 明显高于 L2；在社交网络式的“相似者相连”网络中结论可能相反。
import numpy as np
import networkx as nx

rng = np.random.default_rng(0)
n, n_types = 600, 30                                  # 模拟数据，仅用于演示方法
types = rng.integers(n_types, size=n)
partner = {t: (t + n_types // 2) % n_types for t in range(n_types)}   # 互补类型配对
G = nx.Graph(); G.add_nodes_from(range(n))
for i in range(n):
    for j in range(i + 1, n):
        p = 0.25 if partner[types[i]] == types[j] else 0.002
        if rng.random() < p:
            G.add_edge(i, j)

edges = list(G.edges())
idx = rng.permutation(len(edges))
hidden = [edges[k] for k in idx[: len(edges) // 10]]
G_obs = G.copy(); G_obs.remove_edges_from(hidden)
A = nx.to_numpy_array(G_obs, nodelist=range(n))
k = A.sum(1); k[k == 0] = 1
L2 = A @ A
Dm = np.diag(1 / np.sqrt(k))
L3 = A @ Dm @ A @ Dm @ A                               # p_XY = Σ a_XU a_UV a_VY / sqrt(k_U k_V)

def auc(score, pos, neg):
    s_pos = np.array([score[i, j] for i, j in pos]); s_neg = np.array([score[i, j] for i, j in neg])
    # AUC = P(正例得分 > 负例得分)，平局记 0.5
    gt = (s_pos[:, None] > s_neg[None, :]).mean(); eq = (s_pos[:, None] == s_neg[None, :]).mean()
    return gt + 0.5 * eq

neg = []
while len(neg) < 3000:
    i, j = rng.integers(n, size=2)
    if i != j and not G.has_edge(i, j):
        neg.append((i, j))
print(f"节点 {n}，边 {G.number_of_edges()}，隐藏 {len(hidden)} 条")
print(f"AUC：L2（共同邻居）= {auc(L2, hidden, neg):.3f}，L3（度归一化）= {auc(L3, hidden, neg):.3f}")

import matplotlib.pyplot as plt
def roc(score, pos, neg):
    """在每个不同的得分阈值处计算 (FPR, TPR)；并列得分之间线性连接，与平局记 0.5 的 AUC 一致。"""
    sp_ = np.sort([score[i, j] for i, j in pos]); sn_ = np.sort([score[i, j] for i, j in neg])
    thr = np.r_[np.inf, np.unique(np.r_[sp_, sn_])[::-1]]
    return 1 - np.searchsorted(sn_, thr) / len(sn_), 1 - np.searchsorted(sp_, thr) / len(sp_)
fig, ax = plt.subplots(figsize=(5.2, 4.6))
for S, lab, ls in [(L2, "L2 (common neighbours)", "--"), (L3, "L3 (degree-normalised)", "-")]:
    fpr, tpr = roc(S, hidden, neg)
    ax.plot(fpr, tpr, ls, lw=2, label=f"{lab}, AUC = {auc(S, hidden, neg):.2f}")
ax.plot([0, 1], [0, 1], color="0.6", lw=0.8)
ax.set_xlabel("false positive rate"); ax.set_ylabel("true positive rate (hidden edges)")
ax.set_title("Complementary binding: L3 beats L2"); ax.legend(loc="lower right")
plt.tight_layout(); plt.show()

# %% 示例：通量平衡分析（FBA）与反应敲除
# 玩具代谢网络：R1 摄取 → A（上限 10）；R2 A → B；R3 A → C；R4 B + C → 生物量；R5 B → C（旁路）。
# 稳态约束 S v = 0，下界 0，目标为最大化生物量通量 v4，用 scipy.optimize.linprog 求解。
# 依次把每个反应的上界设为 0（模拟基因敲除），看最优生物量是否降为 0。
# 输出解读：完整网络最优 v4 = 5；敲除 R3 后因为存在旁路 R5，v4 仍为 5（R3 非必需）；
# 敲除 R1、R2 或 R4 则生物量为 0（必需反应）。去掉旁路 R5 后，R3 也变成必需。
import numpy as np
from scipy.optimize import linprog

mets = ["A", "B", "C"]
rxns = ["R1_uptake", "R2_A→B", "R3_A→C", "R4_biomass", "R5_B→C"]
S = np.array([[1, -1, -1,  0,  0],    # A
              [0,  1,  0, -1, -1],    # B
              [0,  0,  1, -1,  1]])   # C
ub = np.array([10, 1000, 1000, 1000, 1000], float)

def fba(S, ub, obj=3):
    c = np.zeros(S.shape[1]); c[obj] = -1             # linprog 求最小，取负号即最大化
    res = linprog(c, A_eq=S, b_eq=np.zeros(S.shape[0]),
                  bounds=list(zip(np.zeros(S.shape[1]), ub)), method="highs")
    return -res.fun, res.x

opt, v = fba(S, ub)
print("完整网络：最优生物量 =", round(opt, 3), "，通量 =", dict(zip(rxns, np.round(v, 2))))
for r in range(S.shape[1]):
    ub_ko = ub.copy(); ub_ko[r] = 0
    print(f"  敲除 {rxns[r]:12s} → 生物量 = {fba(S, ub_ko)[0]:.2f}")
S_noby = S[:, :4]
ub_ko = ub[:4].copy(); ub_ko[2] = 0
print("去掉旁路 R5 后再敲除 R3 → 生物量 =", round(fba(S_noby, ub_ko)[0], 2))

import matplotlib.pyplot as plt
labels = ["wild type", "ΔR1", "ΔR2", "ΔR3", "ΔR4", "ΔR5", "ΔR3\n(no R5)"]
vals = [opt] + [fba(S, np.where(np.arange(len(ub)) == r, 0, ub))[0] for r in range(len(ub))] \
       + [fba(S_noby, ub_ko)[0]]
fig, ax = plt.subplots(figsize=(6.4, 4.2))
ax.bar(labels, vals, color=["C0" if v > 1e-6 else "C3" for v in vals])
for i, v in enumerate(vals):
    ax.text(i, v + 0.1, f"{abs(v):.0f}", ha="center", color="C0" if v > 1e-6 else "C3", fontweight="bold")
ax.set_ylim(0, 5.8)
ax.set_ylabel("optimal biomass flux v4")
ax.set_title("Knockouts: red = essential (biomass drops to 0)")
plt.tight_layout(); plt.show()

# %% 示例：负自调控加快响应；不一致型 1 型前馈环产生脉冲并加速
# (a) 简单调控 dX/dt = β − αX 与负自调控 dX/dt = β·K^n/(K^n + X^n) − αX（K = 0.5，n = 2）的上升时间比较。
#     两者稳态相同（调节 β 使负自调控的稳态也等于 1），比较达到稳态一半所需的时间 T_1/2。
# (b) I1-FFL：X 激活 Z，同时激活 Z 的抑制物 Y；dZ/dt = β·[θ(Y < K) + (1 − θ(Y < K))/F] − αZ，F 为抑制倍数。
#     与“稳态相同的简单调控”比较。
# 输出解读：负自调控的 T_1/2 明显小于 ln2/α ≈ 0.69（K 越小、n 越大越快）；I1-FFL 的 Z 先冲高后回落（脉冲），到达稳态一半的时间更短。
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import brentq

alpha, dt, T = 1.0, 0.001, 6.0
t = np.arange(0, T, dt)

def half_time(x):
    return t[np.argmax(x >= 0.5 * x[-1])]

# (a) 简单调控与负自调控
X_s = 1 - np.exp(-alpha * t)                          # β = α = 1，稳态 1
K, n = 0.5, 2
beta_nar = brentq(lambda b: b * K**n / (K**n + 1.0) - alpha * 1.0, 0.1, 1e6)  # 使稳态 = 1
X_n = np.zeros_like(t)
for i in range(1, len(t)):
    x = X_n[i - 1]
    X_n[i] = x + dt * (beta_nar * K**n / (K**n + x**n) - alpha * x)
print(f"简单调控 T1/2 = {half_time(X_s):.3f}（理论 ln2 = {np.log(2):.3f}）；负自调控 T1/2 = {half_time(X_n):.3f}")

# (b) I1-FFL 与稳态相同的简单调控
F, K_y, beta = 5.0, 0.5, 1.0
Y = 1 - np.exp(-alpha * t)                            # Y 由 X 激活
Z = np.zeros_like(t)
for i in range(1, len(t)):
    prod = beta if Y[i - 1] < K_y else beta / F
    Z[i] = Z[i - 1] + dt * (prod - alpha * Z[i - 1])
Z_simple = (beta / F) * (1 - np.exp(-alpha * t))      # 同稳态的简单调控
print(f"I1-FFL：Z 峰值 = {Z.max():.3f}，稳态 ≈ {Z[-1]:.3f}，T1/2 = {half_time(Z):.3f}；"
      f"同稳态简单调控 T1/2 = {half_time(Z_simple):.3f}")

fig, ax = plt.subplots(1, 2, figsize=(10, 3.5))
ax[0].plot(t, X_s, label="simple"); ax[0].plot(t, X_n, label="NAR"); ax[0].set_title("rise time")
ax[1].plot(t, Z, label="I1-FFL"); ax[1].plot(t, Z_simple, label="simple (same steady state)")
ax[1].set_title("pulse & acceleration")
for a in ax: a.set_xlabel("time"); a.legend()
plt.tight_layout(); plt.show()

# %% 示例：三节点子图普查（triad census）与显著性谱
# networkx 的 triadic_census 按 MAN 编码统计 16 类三元组（含不连通的 003、012、102）；
# 其中 030T 即前馈环，021D 为“一个调控者调两个靶”，021U 为“两个调控者共调一个靶”。
# 模拟一个嵌入了前馈环与单输入模块的调控网络，用保持入度/出度的边交换生成 50 个随机网络，
# 对 13 类连通三元组计算 Z 分数与显著性谱 SP = Z / ||Z||。
# 输出解读：030T（FFL）的 Z 显著为正；正式分析应使用更多随机网络并报告经验 p 值。
import numpy as np
import networkx as nx

rng = np.random.default_rng(7)
D = nx.gnm_random_graph(150, 260, directed=True, seed=7)   # 模拟数据，仅用于演示方法
for _ in range(25):
    x, y, z = rng.choice(150, 3, replace=False); D.add_edges_from([(x, y), (y, z), (x, z)])
for _ in range(5):                                           # 单输入模块：一个 TF 调 6 个靶
    tf = int(rng.integers(150)); D.add_edges_from((tf, int(g)) for g in rng.choice(150, 6, replace=False) if g != tf)
D.remove_edges_from(list(nx.selfloop_edges(D)))

def shuffle(D, n_swap, rng):
    D = D.copy(); edges = list(D.edges()); done = 0; tries = 0
    while done < n_swap and tries < 50 * n_swap:
        tries += 1
        i, j = rng.integers(len(edges), size=2)
        (a, b), (c, d) = edges[i], edges[j]
        if len({a, b, c, d}) < 4 or D.has_edge(a, d) or D.has_edge(c, b):
            continue
        D.remove_edges_from([(a, b), (c, d)]); D.add_edges_from([(a, d), (c, b)])
        edges[i], edges[j] = (a, d), (c, b); done += 1
    return D

connected = ["021D", "021U", "021C", "111D", "111U", "030T", "030C",
             "201", "120D", "120U", "120C", "210", "300"]
real = nx.triadic_census(D)
null = np.array([[nx.triadic_census(shuffle(D, 5 * D.number_of_edges(), rng))[c] for c in connected]
                 for _ in range(50)])
Z = (np.array([real[c] for c in connected]) - null.mean(0)) / (null.std(0) + 1e-9)
SP = Z / np.linalg.norm(Z)
for c, r, m, z, sp in zip(connected, [real[c] for c in connected], null.mean(0), Z, SP):
    if r > 0 or m > 0.5:
        print(f"{c:5s} 真实 {r:5d}  随机均值 {m:7.1f}  Z = {z:6.1f}  SP = {sp:5.2f}")

import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(6.4, 4.2))
ax.bar(connected, SP, color=["C3" if c == "030T" else "0.6" for c in connected])
ax.axhline(0, color="k", lw=0.8)
ax.set_xlabel("connected triad type (MAN code)"); ax.set_ylabel("significance profile SP = Z / ||Z||")
ax.tick_params(axis="x", rotation=45)
ax.set_title("Triad significance profile (red: 030T = feed-forward loop)")
plt.tight_layout(); plt.show()

# %% 示例：马尔可夫聚类（MCL）检测蛋白复合物并与参考复合物匹配
# 生成含 12 个“复合物”（每个 5–9 个蛋白，内部连边概率 0.7）的模拟 PPI 网络，并加入随机背景边。
# MCL：对列随机化的邻接矩阵（加自环）反复做“扩张”（矩阵平方）与“膨胀”（逐元素 r 次幂后列归一化）。
# 用重叠分数 ω(P, R) = |P∩R|² / (|P|·|R|) 把预测簇与参考复合物匹配（阈值 0.2），报告精确率与召回率。
# 输出解读：膨胀参数 r 越大，簇越小越多；r 适中时预测簇与参考复合物匹配最好。
import numpy as np
import networkx as nx

rng = np.random.default_rng(11)
ref, nodes = [], 0                                   # 模拟数据，仅用于演示方法
G = nx.Graph()
for _ in range(12):
    s = int(rng.integers(5, 10)); members = list(range(nodes, nodes + s)); nodes += s
    ref.append(set(members))
    G.add_nodes_from(members)
    G.add_edges_from((a, b) for i, a in enumerate(members) for b in members[i + 1:] if rng.random() < 0.7)
for _ in range(60):
    a, b = rng.integers(nodes, size=2)
    if a != b: G.add_edge(int(a), int(b))

def mcl(G, inflation=2.0, n_iter=60):
    nl = list(G.nodes()); M = nx.to_numpy_array(G, nodelist=nl) + np.eye(len(nl))
    M /= M.sum(0)
    for _ in range(n_iter):
        M = M @ M                                    # 扩张
        M = M ** inflation; M /= M.sum(0)            # 膨胀
    clusters = {}
    for j in range(len(nl)):                         # 每列归到其吸引子（最大值所在行）
        clusters.setdefault(int(np.argmax(M[:, j])), set()).add(nl[j])
    return [c for c in clusters.values() if len(c) >= 3]

def omega(P, R):
    return len(P & R) ** 2 / (len(P) * len(R))

rs, n_pred, precs, recs = [1.4, 2.0, 3.0, 5.0], [], [], []
for r in rs:
    pred = mcl(G, r)
    prec = np.mean([max(omega(P, R) for R in ref) >= 0.2 for P in pred]) if pred else 0
    rec = np.mean([max((omega(P, R) for P in pred), default=0) >= 0.2 for R in ref])
    print(f"膨胀 r = {r}: 预测簇 {len(pred):2d} 个，精确率 = {prec:.2f}，召回率 = {rec:.2f}")
    n_pred.append(len(pred)); precs.append(prec); recs.append(rec)

import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 2, figsize=(10, 4))
ax[0].plot(rs, precs, "o-", label="precision (predicted clusters)")
ax[0].plot(rs, recs, "s--", label="recall (reference complexes)")
ax[0].set_ylim(0, 1.05); ax[0].set_xlabel("inflation r"); ax[0].set_ylabel("fraction matched (ω ≥ 0.2)")
ax[0].set_title("MCL vs reference complexes"); ax[0].legend()
ax[1].plot(rs, n_pred, "o-", color="0.3"); ax[1].axhline(len(ref), color="C3", ls=":", label="12 reference complexes")
ax[1].set_xlabel("inflation r"); ax[1].set_ylabel("number of clusters (size ≥ 3)")
ax[1].set_title("Too high r fragments complexes into clusters < 3"); ax[1].legend()
plt.tight_layout(); plt.show()

# %% 示例：度与必需性的混杂——控制复合物成员身份后度还有预测力吗？
# 模拟：蛋白分为“必需复合物成员”“非必需复合物成员”“不在复合物中”三类；必需性只由所在复合物决定
# （必需复合物成员 70% 必需，其余 10%），而复合物成员因复合物内部稠密而度更高。
# 用逻辑回归（scipy 最小化负对数似然）比较：只用 log(度) 的模型 vs 同时纳入复合物类别的模型。
# 输出解读：单独看度，与必需性显著正相关（“中心性–致死性”）；控制所在复合物后，度的系数接近 0。
# 这与 Zotenko 等（2008）的“必需复合物”解释同一逻辑；真实数据还需考虑研究偏倚与检测方法差异。
import numpy as np
from scipy.optimize import minimize

rng = np.random.default_rng(5)
n = 3000                                             # 模拟数据，仅用于演示方法
group = rng.choice(3, size=n, p=[0.1, 0.2, 0.7])     # 0 必需复合物，1 非必需复合物，2 不在复合物
lam = np.where(group == 2, 3.0, 9.0)                 # 复合物成员度更高
deg = rng.poisson(lam) + 1
p_ess = np.where(group == 0, 0.7, 0.1)
ess = rng.random(n) < p_ess

def logit_fit(X, y):
    X = np.column_stack([np.ones(len(y)), X])
    nll = lambda b: np.sum(np.logaddexp(0, X @ b)) - y @ (X @ b)
    res = minimize(nll, np.zeros(X.shape[1]), method="BFGS")
    se = np.sqrt(np.diag(res.hess_inv))
    return res.x, se

x = np.log(deg)
b1, se1 = logit_fit(x[:, None], ess.astype(float))
b2, se2 = logit_fit(np.column_stack([x, group == 0, group == 1]).astype(float), ess.astype(float))
print(f"只含 log(度)：系数 = {b1[1]:.2f} ± {se1[1]:.2f}")
print(f"加入复合物类别：log(度) 系数 = {b2[1]:.2f} ± {se2[1]:.2f}；必需复合物系数 = {b2[2]:.2f}")
for lo, hi in [(1, 3), (4, 8), (9, 100)]:
    m = (deg >= lo) & (deg <= hi)
    print(f"度 {lo}–{hi}：必需比例 = {ess[m].mean():.2f}（n = {m.sum()}）")

import matplotlib.pyplot as plt
edges_k = [1, 3, 5, 7, 9, 11, 14, 100]                 # 度分箱
mids = [f"{lo}-{hi - 1}" if hi < 100 else f"{lo}+" for lo, hi in zip(edges_k[:-1], edges_k[1:])]
def frac(mask):
    return [ess[mask & (deg >= lo) & (deg < hi)].mean() if np.sum(mask & (deg >= lo) & (deg < hi)) >= 20 else np.nan
            for lo, hi in zip(edges_k[:-1], edges_k[1:])]
fig, ax = plt.subplots(figsize=(6.4, 4.2))
ax.plot(mids, frac(np.ones(n, bool)), "k-o", lw=2.5, label="all proteins")
for g, lab, st in [(0, "essential complexes", "s--"), (1, "non-essential complexes", "^--"), (2, "not in a complex", "v:")]:
    ax.plot(mids, frac(group == g), st, label=lab)
ax.set_xlabel("degree"); ax.set_ylabel("fraction essential"); ax.set_ylim(0, 0.9)
ax.set_title("Degree–essentiality trend vanishes within groups"); ax.legend()
plt.tight_layout(); plt.show()

# %% 示例：差异共表达——Fisher z 检验与置换检验
# 两种条件（如正常 vs 肿瘤）各 n 个样本，模拟 30 个基因：基因 0 与基因 1 在条件 A 中强相关（ρ = 0.8），
# 在条件 B 中几乎不相关（ρ = 0.1），即一条“重连”的边；其余基因对在两条件下相关结构相同。
# 对每个基因对计算 z = (atanh r_A − atanh r_B) / sqrt(1/(n_A − 3) + 1/(n_B − 3))，并用 BH 法控制 FDR。
# 再对基因 0–1 这一对做置换检验（打乱条件标签）。
# 输出解读：被重连的边排名第一；其余 434 对中约 5% 达到名义 p < 0.05（多重比较下的预期假阳性），
# BH 校正后只剩真正重连的那一对。
import numpy as np
from scipy import stats

rng = np.random.default_rng(2)
p, nA, nB = 30, 60, 60                               # 模拟数据，仅用于演示方法
base = 0.3 * np.ones((p, p)) + 0.7 * np.eye(p)       # 背景：所有基因对相关 0.3
CA, CB = base.copy(), base.copy()
CA[0, 1] = CA[1, 0] = 0.8; CB[0, 1] = CB[1, 0] = 0.1
XA = rng.multivariate_normal(np.zeros(p), CA, nA); XB = rng.multivariate_normal(np.zeros(p), CB, nB)

def fisher_z(XA, XB):
    rA, rB = np.corrcoef(XA.T), np.corrcoef(XB.T)
    z = (np.arctanh(np.clip(rA, -0.999, 0.999)) - np.arctanh(np.clip(rB, -0.999, 0.999))) \
        / np.sqrt(1 / (len(XA) - 3) + 1 / (len(XB) - 3))
    return z, rA, rB

z, rA, rB = fisher_z(XA, XB)
iu = np.triu_indices(p, 1)
pv = 2 * stats.norm.sf(np.abs(z[iu]))
order = np.argsort(pv); m = len(pv)
bh = np.minimum.accumulate((pv[order] * m / np.arange(1, m + 1))[::-1])[::-1]
q = np.empty(m); q[order] = np.minimum(bh, 1)
top = order[0]
print(f"排名第一的基因对：({iu[0][top]}, {iu[1][top]})，r_A = {rA[iu][top]:.2f}，r_B = {rB[iu][top]:.2f}，"
      f"z = {z[iu][top]:.2f}，q = {q[top]:.2g}")
print(f"名义 p < 0.05 的基因对数 = {(pv < 0.05).sum()} / {m}；BH q < 0.05 的基因对数 = {(q < 0.05).sum()}")

X = np.vstack([XA, XB]); obs = z[0, 1]; cnt = 0; B = 2000
for _ in range(B):
    perm = rng.permutation(len(X))
    zp, _, _ = fisher_z(X[perm[:nA]][:, :2], X[perm[nA:]][:, :2])
    cnt += abs(zp[0, 1]) >= abs(obs)
print(f"基因 0–1 置换检验 p ≈ {(cnt + 1) / (B + 1):.4f}")

import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(5.4, 4.6))
sig = q < 0.05
ax.scatter(rA[iu][~sig], rB[iu][~sig], s=14, color="0.6", alpha=0.6, label="gene pairs (BH q ≥ 0.05)")
ax.scatter(rA[iu][sig], rB[iu][sig], s=60, color="C3", label="BH q < 0.05")
ax.plot([-0.2, 1], [-0.2, 1], color="k", lw=0.8, ls="--")
ax.set_xlabel("correlation in condition A"); ax.set_ylabel("correlation in condition B")
ax.set_title("Only the rewired pair (0, 1) is differentially co-expressed", fontsize=10); ax.legend(loc="upper left")
plt.tight_layout(); plt.show()

# %% 示例：相似性网络融合（SNF）整合两类组学数据
# 模拟 90 名患者分属 3 个亚型；“表达”数据只能区分亚型 1 与 {2,3}，“甲基化”数据只能区分亚型 3 与 {1,2}。
# 对每类数据建患者相似性矩阵（缩放指数核），再按 Wang 等（2014）的思路迭代：
#   P_v ← S_v · (其他数据类型的 P 的平均) · S_vᵀ，其中 S_v 只保留每个患者的 K 个近邻。
# 最后对融合矩阵做谱聚类（拉普拉斯特征向量 + k-means），与真实亚型比较调整兰德指数（ARI）。
# 输出解读：单一数据类型只能分出 2 组，融合后可分出 3 个亚型（ARI 明显更高）。
import numpy as np
from scipy.cluster.vq import kmeans2
from scipy.spatial.distance import cdist
from scipy.special import comb

rng = np.random.default_rng(4)
labels = np.repeat([0, 1, 2], 30)                   # 模拟数据，仅用于演示方法
expr = rng.normal(size=(90, 50)); expr[labels == 0, :10] += 1.5
meth = rng.normal(size=(90, 40)); meth[labels == 2, :10] += 1.5

def affinity(X, K=15, mu=0.5):
    D = cdist(X, X); Ds = np.sort(D, 1)[:, 1:K + 1].mean(1)
    eps = (Ds[:, None] + Ds[None, :] + D) / 3
    return np.exp(-D**2 / (mu * eps**2))

def full_kernel(W):
    P = W / (2 * (W.sum(1, keepdims=True) - np.diag(W)[:, None])); np.fill_diagonal(P, 0.5); return P

def knn_kernel(W, K=15):
    S = np.zeros_like(W)
    for i in range(len(W)):
        nb = np.argsort(-W[i])[:K]; S[i, nb] = W[i, nb] / W[i, nb].sum()
    return S

def snf(Ws, K=15, t=20):
    Ps = [full_kernel(W) for W in Ws]; Ss = [knn_kernel(W, K) for W in Ws]
    for _ in range(t):
        Ps = [Ss[v] @ np.mean([Ps[u] for u in range(len(Ws)) if u != v], 0) @ Ss[v].T for v in range(len(Ws))]
        Ps = [(P + P.T) / 2 for P in Ps]
    return np.mean(Ps, 0)

def spectral(W, k, seed=0):
    d = W.sum(1); L = np.eye(len(W)) - W / np.sqrt(np.outer(d, d))
    _, vec = np.linalg.eigh(L); U = vec[:, :k]; U /= np.linalg.norm(U, axis=1, keepdims=True)
    return kmeans2(U, k, seed=seed, minit="++")[1]

def ari(a, b):
    ct = np.array([[np.sum((a == i) & (b == j)) for j in np.unique(b)] for i in np.unique(a)])
    s = comb(ct, 2).sum(); sa = comb(ct.sum(1), 2).sum(); sb = comb(ct.sum(0), 2).sum(); tot = comb(len(a), 2)
    exp = sa * sb / tot
    return (s - exp) / (0.5 * (sa + sb) - exp)

W_e, W_m = affinity(expr), affinity(meth)
W_f = snf([W_e, W_m])
for name, W in [("只用表达", W_e), ("只用甲基化", W_m), ("SNF 融合", W_f)]:
    print(f"{name}：ARI = {ari(labels, spectral(W, 3)):.2f}")

import matplotlib.pyplot as plt
fig, axes = plt.subplots(1, 3, figsize=(11, 3.8))
for ax, W, title in zip(axes, [W_e, W_m, W_f], ["expression only", "methylation only", "SNF fused"]):
    M = W.copy(); np.fill_diagonal(M, np.nan)              # 患者按真实亚型排序，去掉对角线以便配色
    ax.imshow(M, cmap="viridis", vmax=np.nanpercentile(M, 98), interpolation="nearest")
    for b in (29.5, 59.5):
        ax.axhline(b, color="w", lw=0.8); ax.axvline(b, color="w", lw=0.8)
    ax.set_title(title); ax.set_xticks([15, 45, 75]); ax.set_xticklabels(["S1", "S2", "S3"])
    ax.set_yticks([15, 45, 75]); ax.set_yticklabels(["S1", "S2", "S3"])
fig.suptitle("Patient similarity ordered by true subtype: fusion reveals 3 blocks")
plt.tight_layout(); plt.show()
