# 依赖：networkx>=3, numpy, scipy, matplotlib
# 数据：所有示例网络都用代码生成（ER 随机图、BA 网络、配置模型、随机模块网络、玩具代谢网络），
#       节点编号 0..N-1；无向网络用 networkx.Graph 表示。示例只用于演示方法，数值随随机种子略有变化。
# 记号：f 为删除比例，p = 1 - f 为保留比例；P_inf 为巨连通分支占原网络节点数的比例；
#       G0(x) = sum_k P(k) x^k，G1(x) = G0'(x) / G0'(1)。

# %% 示例：生成函数求解点渗流与边渗流，并与 Newman–Ziff 模拟比较
# 对给定度分布，点渗流（每个节点以概率 phi 保留）：u = 1 - phi + phi*G1(u)，S = phi*(1 - G0(u))；
# 边渗流（每条边以概率 phi 保留）：u = 1 - phi + phi*G1(u)，S = 1 - G0(u)。两者阈值相同：phi_c = <k>/(<k^2>-<k>)。
# 模拟用 Newman–Ziff 算法：按随机顺序逐个"加回"节点（或边），用并查集维护最大分支，一次得到整条曲线。
# 解读：理论曲线与模拟吻合；点渗流曲线始终低于边渗流曲线（删一个点等于删掉它的全部边），但两者在同一 phi_c 处消失。
import numpy as np
import networkx as nx

def moments_G(degs):
    k = np.arange(degs.max() + 1)
    P = np.bincount(degs, minlength=len(k)) / len(degs)
    G0 = lambda x: np.sum(P * x ** k)
    mk = np.sum(k * P)
    G1 = lambda x: np.sum(k[1:] * P[1:] * x ** (k[1:] - 1)) / mk
    return P, k, G0, G1

def solve_u(G1, phi, iters=2000):
    u = 0.0                                   # 从 0 开始迭代，收敛到最小非平凡解
    for _ in range(iters):
        u = 1 - phi + phi * G1(u)
    return u

def newman_ziff(G, mode="site", reps=20, seed=0):
    rng = np.random.default_rng(seed)
    nodes = list(G.nodes()); N = len(nodes); edges = list(G.edges())
    out = np.zeros(N + 1 if mode == "site" else len(edges) + 1)
    for _ in range(reps):
        parent = {v: v for v in nodes}; size = {v: 1 for v in nodes}
        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]; x = parent[x]
            return x
        def union(a, b, smax):
            ra, rb = find(a), find(b)
            if ra != rb:
                if size[ra] < size[rb]: ra, rb = rb, ra
                parent[rb] = ra; size[ra] += size[rb]; smax = max(smax, size[ra])
            return smax
        curve = [0]; smax = 0
        if mode == "site":
            present = set()
            for v in rng.permutation(N):
                v = nodes[v]; present.add(v); smax = max(smax, 1)
                for w in G[v]:
                    if w in present: smax = union(v, w, smax)
                curve.append(smax)
        else:
            smax = 1
            for e in rng.permutation(len(edges)):
                a, b = edges[e]; smax = union(a, b, smax); curve.append(smax)
        out += np.array(curve) / N
    return out / reps

G = nx.gnp_random_graph(5000, 4 / 4999, seed=1)
degs = np.array([d for _, d in G.degree()])
P, k, G0, G1 = moments_G(degs)
phi_c = degs.mean() / (np.mean(degs ** 2) - degs.mean())
print("ER <k>=%.2f  理论 phi_c = %.3f (即随机删除临界比例 f_c = %.3f)" % (degs.mean(), phi_c, 1 - phi_c))
site = newman_ziff(G, "site"); bond = newman_ziff(G, "bond")
for phi in [0.2, 0.3, 0.5, 0.8]:
    u = solve_u(G1, phi)
    S_site, S_bond = phi * (1 - G0(u)), 1 - G0(u)
    s_sim = site[int(phi * G.number_of_nodes())]; b_sim = bond[int(phi * G.number_of_edges())]
    print("phi=%.1f  点渗流 理论 %.3f 模拟 %.3f | 边渗流 理论 %.3f 模拟 %.3f" % (phi, S_site, s_sim, S_bond, b_sim))

import matplotlib.pyplot as plt
phis = np.linspace(0.01, 1, 60)
S_th = np.array([1 - G0(solve_u(G1, ph, iters=500)) for ph in phis])
fig, ax = plt.subplots(figsize=(6.4, 4.2))
ax.plot(np.arange(len(site)) / G.number_of_nodes(), site, c="tab:blue", lw=3, alpha=0.4, label="site (Newman-Ziff)")
ax.plot(np.arange(len(bond)) / G.number_of_edges(), bond, c="tab:orange", lw=3, alpha=0.4, label="bond (Newman-Ziff)")
ax.plot(phis, phis * S_th, "--", c="tab:blue", label="site (theory)")
ax.plot(phis, S_th, ":", c="tab:orange", lw=2, label="bond (theory)")
ax.axvline(phi_c, c="0.5", lw=0.8)
ax.set_xlabel("occupation probability phi"); ax.set_ylabel("giant component / N"); ax.legend()
ax.set_title("Site and bond percolation vanish at the same phi_c = %.2f" % phi_c)
plt.tight_layout(); plt.show()

# %% 示例：随机失效与四种攻击策略的比较，并计算 R 指标
# 策略：random（随机删点）；ID（按初始度）；RD（每删一个节点重新计算度，自适应）；RB（每次重算介数，自适应）。
# R = (1/N) * sum_{Q=1}^{N} s(Q)，s(Q) 为删去 Q 个节点后最大连通分支的节点比例（Schneider 等 2011）。
# 为节省时间，RB 每删 1% 的节点才重算一次介数，并用 k=200 个源点近似介数。
# 解读：BA 网络对随机失效的 R 明显高于攻击；自适应攻击（RD、RB）比按初始度攻击更具破坏性；ER 网络各策略差距较小。
import numpy as np
import networkx as nx

def attack_curve(G, strategy, seed=0, step_frac=0.01):
    H = G.copy(); N = G.number_of_nodes(); rng = np.random.default_rng(seed)
    lcc = lambda H: max((len(c) for c in nx.connected_components(H)), default=0) / N
    if strategy == "random":
        order = list(rng.permutation(list(G.nodes())))
    elif strategy == "ID":
        order = sorted(G.nodes(), key=lambda v: -G.degree(v))
    s = [lcc(H)]
    while H.number_of_nodes() > 0:
        if strategy in ("random", "ID"):
            batch = [order[len(s) - 1]]
        elif strategy == "RD":
            batch = [max(H.degree, key=lambda x: x[1])[0]]
        else:                                          # RB：分批重算近似介数
            m = max(1, int(step_frac * N))
            bc = nx.betweenness_centrality(H, k=min(200, H.number_of_nodes()), seed=seed)
            batch = sorted(bc, key=bc.get, reverse=True)[:m]
        for v in batch:
            H.remove_node(v)
            s.append(lcc(H))
    return np.array(s)

def R_index(s):
    return s[1:].sum() / (len(s) - 1)

def fc_one_percent(s):
    idx = np.argmax(s < 0.01 * s[0])
    return idx / (len(s) - 1)

N = 1000
nets = {"BA(m=2)": nx.barabasi_albert_graph(N, 2, seed=3),
        "ER(<k>=4)": nx.gnm_random_graph(N, 2 * N, seed=3)}
curves = {}
for name, G in nets.items():
    print(name)
    for st in ["random", "ID", "RD", "RB"]:
        s = attack_curve(G, st)
        curves[name, st] = s
        print("  %-6s R = %.3f   f_c(1%%规则) = %.3f" % (st, R_index(s), fc_one_percent(s)))

import matplotlib.pyplot as plt
fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
for ax, name in zip(axes, nets):
    for st, ls in zip(["random", "ID", "RD", "RB"], ["-", "--", "-.", ":"]):
        s = curves[name, st]
        ax.plot(np.arange(len(s)) / (len(s) - 1), s, ls=ls, lw=2, label="%s (R = %.3f)" % (st, R_index(s)))
    ax.set_xlim(0, 0.6); ax.set_xlabel("fraction removed f"); ax.set_title(name); ax.legend(fontsize=8)
axes[0].set_ylabel("largest component s(f)")
fig.suptitle("Adaptive attacks are most damaging, especially on BA")
plt.tight_layout(); plt.show()

# 手算小例子：星形与路径（N = 5）
star = nx.star_graph(4); path = nx.path_graph(5)
print("星形 RD 攻击 R =", round(R_index(attack_curve(star, "RD")), 3), "(手算 4/25 = 0.16)")

# %% 示例：无标度网络的随机失效阈值与攻击阈值（连续度近似）
# 随机失效：f_c = 1 - 1/(kappa - 1)，kappa = <k^2>/<k> 用截断幂律 [k_min, k_max] 的连续近似计算，k_max = k_min N^{1/(gamma-1)}。
# 攻击（Cohen 等 2001）：f_c 满足 f^{(2-g)/(1-g)} = 2 + (2-g)/(3-g) * k_min * (f^{(3-g)/(1-g)} - 1)，用 brentq 求根。
# 解读：gamma<3 时随机失效阈值随 N 增大逼近 1；攻击阈值只有百分之几到二十几，且随 gamma 非单调变化
# （k_min=1 时约在 gamma≈2.3 处取极大值 0.06 左右）。连续度近似对小 k_min 只是粗略估计，应以模拟核对。
import numpy as np
from scipy.optimize import brentq

def kappa(g, kmin, kmax):
    m1 = (kmax ** (2 - g) - kmin ** (2 - g)) / (2 - g)
    m2 = (kmax ** (3 - g) - kmin ** (3 - g)) / (3 - g)
    return m2 / m1

def fc_random(g, kmin, N):
    kmax = kmin * N ** (1 / (g - 1))
    return 1 - 1 / (kappa(g, kmin, kmax) - 1)

def fc_attack(g, kmin):
    F = lambda f: f ** ((2 - g) / (1 - g)) - 2 - (2 - g) / (3 - g) * kmin * (f ** ((3 - g) / (1 - g)) - 1)
    grid = np.logspace(-6, -0.001, 4000)
    vals = [F(f) for f in grid]
    for a, b, va, vb in zip(grid[:-1], grid[1:], vals[:-1], vals[1:]):
        if va * vb < 0:
            return brentq(F, a, b)
    return np.nan

print("gamma   f_c随机(N=1e4)  f_c随机(N=1e6)  f_c攻击(k_min=1)  f_c攻击(k_min=2)")
for g in [2.1, 2.3, 2.5, 2.7, 2.9, 3.5]:
    print("%.1f     %.3f           %.3f           %.4f            %.4f" % (
        g, fc_random(g, 2, 1e4), fc_random(g, 2, 1e6), fc_attack(g, 1), fc_attack(g, 2)))

import matplotlib.pyplot as plt
gs = np.linspace(2.05, 3.5, 20)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
ax1.plot(gs, [fc_random(g, 2, 1e4) for g in gs], "o-", ms=4, label="N = 1e4")
ax1.plot(gs, [fc_random(g, 2, 1e6) for g in gs], "s--", ms=4, label="N = 1e6")
ax1.set_xlabel("degree exponent gamma"); ax1.set_ylabel("critical fraction f_c"); ax1.legend()
ax1.set_title("Random failure (k_min = 2)")
ax2.plot(gs, [fc_attack(g, 1) for g in gs], "o-", ms=4, label="k_min = 1")
ax2.plot(gs, [fc_attack(g, 2) for g in gs], "s--", ms=4, label="k_min = 2")
ax2.set_xlabel("degree exponent gamma"); ax2.set_ylabel("critical fraction f_c"); ax2.legend()
ax2.set_title("Targeted attack: only a few percent")
plt.tight_layout(); plt.show()

# %% 示例：Motter–Lai 负载重分配级联
# 负载 L_i 取节点介数（最短路径条数意义），容量 C_i = (1+alpha) L_i。移除一个初始节点后，重新计算介数，
# 负载超过容量的节点全部失效，循环直至没有新的失效。用 G = N'/N 度量级联后最大连通分支的相对规模。
# 比较三种触发方式：移除负载最高的节点、移除度最高的节点、随机移除一个节点。
# 解读：容忍参数 alpha 较小时，移除一个高负载节点即可引发大面积崩溃，而随机触发几乎无影响；
# 负载更不均匀的 BA 网络需要更大的 alpha（更多冗余容量）才能避免崩溃。
import numpy as np
import networkx as nx

def load(G):
    return nx.betweenness_centrality(G, normalized=False, endpoints=True)

def motter_lai(G, alpha, trigger):
    L0 = load(G); C = {v: (1 + alpha) * L0[v] for v in G}
    H = G.copy(); H.remove_node(trigger)
    while True:
        L = load(H)
        failed = [v for v in H if L[v] > C[v] + 1e-9]
        if not failed:
            break
        H.remove_nodes_from(failed)
    lcc = max((len(c) for c in nx.connected_components(H)), default=0)
    return lcc / G.number_of_nodes()

rng = np.random.default_rng(0)
alphas, res = [0.1, 0.3, 0.6, 1.0], {}
for name, G in [("BA", nx.barabasi_albert_graph(400, 2, seed=1)), ("ER", nx.gnm_random_graph(400, 800, seed=1))]:
    G = G.subgraph(max(nx.connected_components(G), key=len)).copy()
    L0 = load(G)
    top_load = max(L0, key=L0.get); top_deg = max(G.degree, key=lambda x: x[1])[0]
    rand = [int(v) for v in rng.choice(list(G.nodes()), 5, replace=False)]
    for alpha in alphas:
        g_load = motter_lai(G, alpha, top_load); g_deg = motter_lai(G, alpha, top_deg)
        g_rand = np.mean([motter_lai(G, alpha, v) for v in rand])
        res.setdefault(name, []).append((g_load, g_deg, g_rand))
        print("%s alpha=%.1f  最高负载触发 G=%.2f  最高度触发 G=%.2f  随机触发 G=%.2f" % (name, alpha, g_load, g_deg, g_rand))

import matplotlib.pyplot as plt
fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
for ax, (name, vals) in zip(axes, res.items()):
    vals = np.array(vals)
    for j, (lab, mk, ls) in enumerate([("highest load", "o", "-"), ("highest degree", "s", "--"), ("random", "^", ":")]):
        ax.plot(alphas, vals[:, j], marker=mk, ls=ls, label=lab)
    ax.set_xlabel("tolerance alpha"); ax.set_title(name + " network"); ax.legend(fontsize=8)
axes[0].set_ylabel("G = N' / N after cascade")
fig.suptitle("One overloaded hub can collapse the network when alpha is small")
plt.tight_layout(); plt.show()

# %% 示例：Watts 阈值级联的"级联窗口"与分支过程
# Watts 模型：节点在失效邻居比例 >= phi 时失效。度 k <= 1/phi 的节点是"易损节点"（一个失效邻居即可触发）。
# 全局级联条件：sum_k k(k-1) rho_k P(k) > <k>，rho_k = 1 若 k <= floor(1/phi)。对 ER 网络扫描 <k> 得到级联窗口，并与模拟比较。
# 分支过程部分：后代分布 p0, p1, p2 的灭绝概率 q 满足 q = g(q)；临界分支过程的雪崩规模分布 P(s) ~ s^{-3/2}。
# 解读：<k> 太小（网络不连通）或太大（易损节点太少）都不会出现全局级联；窗口边界附近有限规模效应明显，
# 解析判据略小于 1 时模拟仍可能出现少量全局级联。临界分支过程的对数斜率接近 -1.5。
import numpy as np
import networkx as nx
from scipy.stats import poisson

def watts_condition(kmean, phi, kmax=60):
    k = np.arange(kmax); P = poisson.pmf(k, kmean)
    rho = (k <= np.floor(1 / phi)).astype(float); rho[0] = 0
    return np.sum(k * (k - 1) * rho * P) / kmean

def watts_sim(n, kmean, phi, trials=30, seed=0):
    G = nx.fast_gnp_random_graph(n, kmean / (n - 1), seed=seed)
    rng = np.random.default_rng(seed); big = 0
    deg = dict(G.degree())
    for _ in range(trials):
        failed = {int(rng.integers(n))}; frontier = list(failed)
        while frontier:
            new = []
            for v in frontier:
                for w in G[v]:
                    if w not in failed and deg[w] > 0 and sum(x in failed for x in G[w]) / deg[w] >= phi:
                        failed.add(w); new.append(w)
            frontier = new
        big += len(failed) > 0.1 * n
    return big / trials

phi = 0.18
kms, sims = [0.8, 1.5, 3, 5, 6, 7, 9], []
for km in kms:
    sims.append(watts_sim(3000, km, phi))
    print("<k>=%.1f  解析判据 %.2f (>1 才可能全局级联)  模拟全局级联比例 %.2f" % (km, watts_condition(km, phi), sims[-1]))

# 分支过程：p0=0.25, p1=0.25, p2=0.5 -> 平均后代 1.25，灭绝概率 q = 0.5（手算见正文）
g = lambda q: 0.25 + 0.25 * q + 0.5 * q ** 2
q = 0.0
for _ in range(200):
    q = g(q)
print("超临界分支过程的灭绝概率 q =", round(q, 4))

rng = np.random.default_rng(1); sizes = []
for _ in range(20000):                       # 临界：p0 = p2 = 1/2
    active, s = 1, 1
    while active > 0 and s < 10 ** 5:
        kids = 2 * rng.integers(0, 2, size=active).sum()
        active = kids; s += kids
    sizes.append(s)
sizes = np.array(sizes)
bins = np.logspace(0, 4, 13); h, e = np.histogram(sizes, bins=bins, density=True)
c = np.sqrt(e[1:] * e[:-1]); ok = h > 0
print("临界分支过程雪崩规模分布的拟合指数 alpha ≈ %.2f（理论 1.5）" % -np.polyfit(np.log(c[ok][2:]), np.log(h[ok][2:]), 1)[0])

import matplotlib.pyplot as plt
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
kg = np.linspace(0.5, 10, 120)
ax1.plot(kg, [watts_condition(x, phi) for x in kg], c="0.4", label="analytic condition")
ax1.axhline(1, ls="--", c="tab:red", lw=1)
ax1.set_xlabel("mean degree <k>"); ax1.set_ylabel("cascade condition (>1 = global)")
ax1b = ax1.twinx(); ax1b.plot(kms, sims, "o", c="tab:blue", label="simulated P(global)")
ax1b.set_ylabel("fraction of global cascades", color="tab:blue"); ax1b.set_ylim(0, 1.05)
ax1.set_title("Cascade window (phi = %.2f)" % phi)
h1, l1 = ax1.get_legend_handles_labels(); h2, l2 = ax1b.get_legend_handles_labels(); ax1.legend(h1 + h2, l1 + l2, fontsize=8)
ax2.loglog(c[ok], h[ok], "o", label="critical branching")
ax2.loglog(c[ok], h[ok][0] * (c[ok] / c[ok][0]) ** -1.5, "k--", label="slope -3/2")
ax2.set_xlabel("avalanche size s"); ax2.set_ylabel("P(s)"); ax2.legend(); ax2.set_title("Avalanche sizes ~ s^(-3/2)")
plt.tight_layout(); plt.show()

# %% 示例：相互依存 ER 网络的级联（Buldyrev 等 2010）
# 两个 ER 网络 A、B 平均度均为 k，节点一一依赖。初始随机保留比例 p 的 A 节点，然后交替执行：
# A 中只保留巨分支 -> B 中依赖已失效 A 节点的节点失效 -> B 中只保留巨分支 -> A 中对应节点失效 …… 直到稳定。
# 理论：相互巨分支比例 mu 满足 mu = p (1 - exp(-k mu))^2，p_c = 2.4554/k，且 mu 在 p_c 处不连续地跳到 0。
# 解读：模拟的 mu(p) 与理论一致，阈值远高于单个 ER 网络的 p_c = 1/k，并呈现突变式（一级）崩溃。
import numpy as np
import networkx as nx
from scipy.optimize import minimize_scalar

def mu_theory(p, k):
    mu = 1.0
    for _ in range(5000):
        mu = p * (1 - np.exp(-k * mu)) ** 2
    return mu

res = minimize_scalar(lambda z: z / (1 - np.exp(-z)) ** 2, bounds=(0.1, 10), method="bounded")
print("理论：k*p_c = %.4f，跳变处 k*mu_c = %.4f" % (res.fun, res.x))

def lcc_nodes(G, alive):
    H = G.subgraph(alive)
    if H.number_of_nodes() == 0:
        return set()
    return set(max(nx.connected_components(H), key=len))

def interdependent(GA, GB, p, rng):
    n = GA.number_of_nodes()
    alive = set(int(v) for v in rng.choice(n, int(p * n), replace=False))
    while True:
        a = lcc_nodes(GA, alive)                # 依赖关系为 i <-> i
        b = lcc_nodes(GB, a)
        if b == alive:
            break
        alive = b
    return len(alive) / n

k, n = 4.0, 20000
rng = np.random.default_rng(0)
GA = nx.fast_gnp_random_graph(n, k / (n - 1), seed=1); GB = nx.fast_gnp_random_graph(n, k / (n - 1), seed=2)
ps, mus = [0.9, 0.75, 0.66, 0.62, 0.60, 0.55], []
for p in ps:
    mus.append(interdependent(GA, GB, p, rng))
    print("p=%.2f  理论 mu=%.3f  模拟 mu=%.3f" % (p, mu_theory(p, k), mus[-1]))

import matplotlib.pyplot as plt
pg = np.linspace(0.3, 1, 200)
fig, ax = plt.subplots(figsize=(6.4, 4.2))
ax.plot(pg, [mu_theory(x, k) for x in pg], "k-", label="interdependent (theory)")
ax.plot(ps, mus, "o", c="tab:red", label="interdependent (simulation)")
ax.axvline(res.fun / k, ls="--", c="tab:red", lw=1, label="p_c = %.3f" % (res.fun / k))
ax.axvline(1 / k, ls=":", c="0.5", label="single ER p_c = 1/k")
ax.set_xlabel("initially retained fraction p"); ax.set_ylabel("mutual giant component mu"); ax.legend()
ax.set_title("Interdependence causes an abrupt collapse (k = 4)")
plt.tight_layout(); plt.show()

# %% 示例：保度换边优化 R 指标，得到"洋葱"结构（Schneider 等 2011）
# 随机选两条边 (i,j),(k,l) 改为 (i,k),(j,l)（或 (i,l),(j,k)），保持每个节点的度不变；只有当自适应度攻击下的 R 增大时才接受。
# 这里用小网络（N=200）和有限次尝试，仅演示思想；度同配系数 r 用来观察"洋葱化"往往伴随同配性升高。
# 解读：R 明显增大而度分布不变；优化后网络的度同配系数通常上升，高度节点彼此相连形成核心。
import numpy as np
import networkx as nx

def R_adaptive_degree(G):
    H = G.copy(); N = G.number_of_nodes(); total = 0.0
    for _ in range(N):
        v = max(H.degree, key=lambda x: x[1])[0]; H.remove_node(v)
        total += max((len(c) for c in nx.connected_components(H)), default=0) / N
    return total / N

G = nx.barabasi_albert_graph(200, 2, seed=5)
G_init = G
rng = np.random.default_rng(0)
R = R_adaptive_degree(G)
print("初始 R = %.3f，同配系数 r = %.3f" % (R, nx.degree_assortativity_coefficient(G)))
edges = list(G.edges()); accepted = 0
for t in range(1500):
    (i, j), (a, b) = [edges[x] for x in rng.choice(len(edges), 2, replace=False)]
    if len({i, j, a, b}) < 4:
        continue
    new = [(i, a), (j, b)] if rng.random() < 0.5 else [(i, b), (j, a)]
    if any(G.has_edge(*e) for e in new):
        continue
    H = G.copy(); H.remove_edges_from([(i, j), (a, b)]); H.add_edges_from(new)
    if not nx.is_connected(H):
        continue
    Rn = R_adaptive_degree(H)
    if Rn > R:
        G, R = H, Rn; edges = list(G.edges()); accepted += 1
print("接受换边 %d 次，优化后 R = %.3f，同配系数 r = %.3f" % (accepted, R, nx.degree_assortativity_coefficient(G)))

import matplotlib.pyplot as plt
def attack_s(G):
    H = G.copy(); N = G.number_of_nodes(); s = [1.0]
    for _ in range(N):
        H.remove_node(max(H.degree, key=lambda x: x[1])[0])
        s.append(max((len(c) for c in nx.connected_components(H)), default=0) / N)
    return np.array(s)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
for H, lab, ls in [(G_init, "original BA", "--"), (G, "optimized", "-")]:
    s = attack_s(H)
    ax1.plot(np.linspace(0, 1, len(s)), s, ls=ls, lw=2, label="%s (R = %.3f)" % (lab, s[1:].mean()))
ax1.set_xlim(0, 0.5); ax1.set_xlabel("fraction removed (adaptive degree attack)"); ax1.set_ylabel("largest component / N")
ax1.legend(); ax1.set_title("Degree-preserving swaps raise R")
dg = dict(G.degree()); pos = nx.kamada_kawai_layout(G)
nx.draw_networkx_edges(G, pos, ax=ax2, edge_color="0.6", alpha=0.4)
nx.draw_networkx_nodes(G, pos, ax=ax2, node_size=[min(120, 40 + 4 * dg[v]) for v in G], node_color=[dg[v] for v in G], cmap="viridis")
ax2.set_title("Optimized network (size/color = degree)"); ax2.axis("off")
plt.tight_layout(); plt.show()

# %% 示例：玩具代谢网络的单基因与双基因敲除——必需基因与合成致死对
# 用"网络扩张"（scope）判断可行性：从培养基中的底物出发，反应的全部底物都可得时反应可进行并产生产物；
# 能合成全部"生物量前体"即视为可存活。每个反应由一个或多个同工酶基因催化（任一基因存在即可）。
# 单基因敲除不能存活 -> 必需基因；两个单独敲除都存活、同时敲除不能存活 -> 合成致死对。
# 解读：同工酶（G3/G4）与平行通路（G5 与 G6–G7 两条旁路）提供冗余，因此产生合成致死对，这正是"冗余造就鲁棒、也造就弱点"。
from itertools import combinations

reactions = {                       # 反应: (底物, 产物, 催化基因)
    "R1": ({"glc"}, {"g6p"}, {"G1"}),
    "R2": ({"g6p"}, {"pyr"}, {"G2"}),
    "R3": ({"pyr"}, {"accoa"}, {"G3", "G4"}),      # 同工酶
    "R4": ({"g6p"}, {"r5p"}, {"G5"}),              # 通路 1
    "R5": ({"pyr"}, {"x"}, {"G6"}),                # 通路 2 的两步旁路
    "R6": ({"x"}, {"r5p"}, {"G7"}),
    "R7": ({"accoa"}, {"lipid"}, {"G8"}),
}
medium = {"glc"}; biomass = {"r5p", "lipid", "pyr"}
genes = sorted(set().union(*[r[2] for r in reactions.values()]))

def viable(knockout):
    avail = set(medium); changed = True
    active = {r for r, (_, _, gs) in reactions.items() if gs - set(knockout)}
    while changed:
        changed = False
        for r in active:
            sub, prod, _ = reactions[r]
            if sub <= avail and not prod <= avail:
                avail |= prod; changed = True
    return biomass <= avail

essential = [g for g in genes if not viable([g])]
sl_pairs = [(a, b) for a, b in combinations([g for g in genes if g not in essential], 2) if not viable([a, b])]
print("必需基因:", essential)
print("合成致死对:", sl_pairs)

import numpy as np
import matplotlib.pyplot as plt
V = np.array([[viable([a] if a == b else [a, b]) for b in genes] for a in genes], float)
fig, ax = plt.subplots(figsize=(6.4, 4.6))
ax.imshow(V, cmap="RdYlGn", vmin=-0.3, vmax=1.3)
ax.set_xticks(range(len(genes)), genes); ax.set_yticks(range(len(genes)), genes)
for i in range(len(genes)):
    for j in range(len(genes)):
        ax.text(j, i, "ok" if V[i, j] else "x", ha="center", va="center", fontsize=8)
ax.set_xlabel("knockout gene"); ax.set_ylabel("knockout gene")
ax.set_title("Knockout viability (diagonal = single; x = lethal)", fontsize=10)
plt.tight_layout(); plt.show()

# %% 示例：模块化"脑网络"的虚拟损伤——枢纽 vs 连接者
# 生成一个 6 模块的随机加权网络（模块内连接密、模块间稀疏），按度（模块内枢纽）与参与系数（连接者）选损伤节点，
# 删除节点后比较全局效率与模块度（用已知的模块划分计算）的下降，并与随机删除比较。
# 这只是 Alstott 等（2009）、Gratton 等（2012）思路的拓扑简化：真实研究用结构连接组和动力学模型或病人数据。
# 解读：删除连接者对模块间整合（效率）的损害通常大于同等数量的随机节点；模块度可能反而升高（模块更"孤立"）。
import numpy as np
import networkx as nx

rng = np.random.default_rng(2)
sizes = [20] * 6
P = np.full((6, 6), 0.01); np.fill_diagonal(P, 0.35)
G = nx.stochastic_block_model(sizes, P.tolist(), seed=3)
comm = {v: G.nodes[v]["block"] for v in G}
# 指定少数"连接者"：给 6 个节点添加跨模块连接
connectors = [i * 20 for i in range(6)]
for c in connectors:
    for b in range(6):
        if b != comm[c]:
            for w in rng.choice(range(b * 20, b * 20 + 20), 2, replace=False):
                G.add_edge(c, int(w))

def participation(G, comm):
    pc = {}
    for v in G:
        k = G.degree(v)
        if k == 0:
            pc[v] = 0; continue
        counts = np.bincount([comm[w] for w in G[v]], minlength=6)
        pc[v] = 1 - np.sum((counts / k) ** 2)
    return pc

def lesion_effect(G, targets):
    H = G.copy(); H.remove_nodes_from(targets)
    parts = [{v for v in H if comm[v] == b} for b in range(6)]
    parts = [p for p in parts if p]
    return nx.global_efficiency(H), nx.community.modularity(H, parts)

pc = participation(G, comm); deg = dict(G.degree())
within = [v for v in G if v not in connectors]
hubs = sorted(within, key=lambda v: -deg[v])[:6]
conn = sorted(G, key=lambda v: -pc[v])[:6]
E0, Q0 = lesion_effect(G, [])
print("完整网络: 全局效率 %.3f  模块度 %.3f" % (E0, Q0))
eff = [(E0, Q0)]
for name, t in [("模块内枢纽(高度、低参与系数)", hubs), ("连接者(高参与系数)", conn)]:
    E, Q = lesion_effect(G, t); eff.append((E, Q)); print("%s: 效率 %.3f  模块度 %.3f" % (name, E, Q))
rand = [lesion_effect(G, list(rng.choice(G.number_of_nodes(), 6, replace=False))) for _ in range(30)]
print("随机 6 个节点: 效率 %.3f  模块度 %.3f" % tuple(np.mean(rand, axis=0)))

import matplotlib.pyplot as plt
eff = np.vstack([eff, np.mean(rand, axis=0)]); err = [0, 0, 0, np.std([r[0] for r in rand])]
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
pos = nx.spring_layout(G, seed=1)
col = ["tab:red" if v in conn else ("tab:orange" if v in hubs else "0.75") for v in G]
nx.draw_networkx_edges(G, pos, ax=ax1, edge_color="0.6", alpha=0.3, width=0.5)
nx.draw_networkx_nodes(G, pos, ax=ax1, node_size=[110 if v in conn or v in hubs else 40 for v in G], node_color=col)
ax1.set_title("Connectors (red) vs within-module hubs (orange)"); ax1.axis("off")
ax2.bar(["intact", "hubs", "connectors", "random"], eff[:, 0], color=["0.4", "tab:orange", "tab:red", "0.75"], width=0.6)
ax2.errorbar(3, eff[3, 0], yerr=err[3], c="k", capsize=4, label="random: mean +/- SD (30 draws)")
ax2.set_ylim(0, E0 * 1.3); ax2.set_ylabel("global efficiency"); ax2.legend(fontsize=8, loc="upper right")
ax2.set_title("Removing 6 connectors hurts integration most")
plt.tight_layout(); plt.show()
