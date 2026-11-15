# 依赖：networkx>=3, numpy, scipy, matplotlib
# 数据：全部示例网络由 networkx 生成（BA 无标度网络、同边数的 ER 随机网络、配置模型、小世界网络、
#       随机块模型）或取自 networkx 内置的空手道俱乐部网络（nx.karate_club_graph()）；
#       输入为无向简单图，节点编号为 0..N-1。发病曲线、集合种群与活动驱动网络均为代码内模拟数据。

# %% 示例：网络上的离散时间 SIR 模拟（ER 与 BA 网络对比）
# 每一步：每个感染者以概率 beta 感染每个易感邻居，然后以概率 gamma 恢复（移除）。
# 在节点数、平均度都相同的 ER 与 BA 网络上各做 30 次模拟（每次随机选 1 个种子），
# 比较平均最终感染规模（最终 R 的比例），并画出 BA 网络上的一条 S/I/R 曲线。
# 解读：同样的 beta、gamma 下，度异质的 BA 网络更容易暴发，平均最终规模更大。
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

def sir(G, beta, gamma, seeds, rng, max_steps=500):
    """返回 (每一步的 S, I, R 比例数组, 最终移除比例)。"""
    n = G.number_of_nodes()
    nbrs = [list(G.neighbors(v)) for v in range(n)]
    state = np.zeros(n, dtype=int)          # 0=S, 1=I, 2=R
    state[list(seeds)] = 1
    hist = []
    for _ in range(max_steps):
        infected = np.flatnonzero(state == 1)
        hist.append([(state == 0).mean(), (state == 1).mean(), (state == 2).mean()])
        if infected.size == 0:
            break
        new_inf = set()
        for u in infected:
            for v in nbrs[u]:
                if state[v] == 0 and rng.random() < beta:
                    new_inf.add(v)
        recover = infected[rng.random(infected.size) < gamma]
        state[recover] = 2
        state[list(new_inf)] = 1
    return np.array(hist), (state == 2).mean()

N, m = 1000, 3
G_ba = nx.barabasi_albert_graph(N, m, seed=1)
G_er = nx.gnm_random_graph(N, G_ba.number_of_edges(), seed=1)
beta, gamma = 0.05, 0.3
rng = np.random.default_rng(0)

sizes_er = [sir(G_er, beta, gamma, [rng.integers(N)], rng)[1] for _ in range(30)]
sizes_ba = [sir(G_ba, beta, gamma, [rng.integers(N)], rng)[1] for _ in range(30)]
print("ER 平均最终规模 = %.3f" % np.mean(sizes_er))
print("BA 平均最终规模 = %.3f" % np.mean(sizes_ba))

hist, _ = sir(G_ba, beta, gamma, [0], np.random.default_rng(3))
plt.plot(hist[:, 0], label="S"); plt.plot(hist[:, 1], label="I"); plt.plot(hist[:, 2], label="R")
plt.xlabel("time step"); plt.ylabel("fraction"); plt.title("SIR on BA network"); plt.legend()
plt.show()

# %% 示例：用度分布估计 SIR 流行病阈值
# 异质平均场给出 SIR 的阈值：传播性 T 需大于 T_c = <k> / (<k^2> - <k>)。
# 在上一示例的离散时间模型中，一个感染者在整个感染期内把病传给某个邻居的概率（传播性）为
#   T = 1 - gamma*(1-beta) / (1 - (1-beta)*(1-gamma))
# 代码计算 ER 与 BA 网络的 T_c，并与当前参数的 T 比较。
# 解读：BA 网络的 <k^2> 更大，T_c 更低；同一 T 可能高于 BA 的阈值而低于 ER 的阈值。
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

N, m = 1000, 3
G_ba = nx.barabasi_albert_graph(N, m, seed=1)
G_er = nx.gnm_random_graph(N, G_ba.number_of_edges(), seed=1)
beta, gamma = 0.05, 0.3
T = 1 - gamma * (1 - beta) / (1 - (1 - beta) * (1 - gamma))
print("当前参数的传播性 T = %.3f" % T)

def threshold(G):
    k = np.array([d for _, d in G.degree()], dtype=float)
    return k.mean() / ((k**2).mean() - k.mean())

for name, G in [("ER", G_er), ("BA", G_ba)]:
    Tc = threshold(G)
    print("%s: T_c = %.3f  -> %s" % (name, Tc, "高于阈值，可能暴发" if T > Tc else "低于阈值"))

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
for name, G, mk in [("ER", G_er, "o"), ("BA", G_ba, "s")]:
    k, cnt = np.unique([d for _, d in G.degree()], return_counts=True)
    ax1.loglog(k, cnt / N, mk, ms=4, label=name)
ax1.set_xlabel("degree k"); ax1.set_ylabel("P(k)"); ax1.legend(); ax1.set_title("Degree distributions")
ax2.bar(["ER", "BA"], [threshold(G_er), threshold(G_ba)], color=["0.6", "tab:blue"], width=0.5)
ax2.axhline(T, ls="--", c="tab:red", label="T = %.3f (current)" % T)
ax2.set_ylabel("epidemic threshold T_c"); ax2.legend()
ax2.set_title("Heterogeneity lowers T_c: BA outbreak, ER not")
plt.tight_layout(); plt.show()

# %% 示例：三种免疫策略的比较
# 在 BA 网络上接种 10% 的节点（接种者从网络中删除），比较三种策略后的流行风险：
#   随机免疫、目标免疫（度最高者）、熟人免疫（随机选人，再接种其随机邻居）。
# 用剩余网络的阈值 T_c 和巨连通分支比例来衡量，并与上一示例中的传播性 T≈0.149 比较。
# 解读：随机免疫后 T_c 仍低于 T；目标免疫和熟人免疫都把 T_c 提到 T 以上（目标免疫提升最多）。
#       接种 10% 时巨分支比例下降有限，三种策略的差别主要体现在剩余网络的阈值上。
import numpy as np
import networkx as nx

N, m = 1000, 3
G = nx.barabasi_albert_graph(N, m, seed=1)
rng = np.random.default_rng(1)
n_vac = int(0.1 * N)

def evaluate(G, removed):
    H = G.copy()
    H.remove_nodes_from(removed)
    k = np.array([d for _, d in H.degree()], dtype=float)
    Tc = k.mean() / ((k**2).mean() - k.mean())
    giant = max(len(c) for c in nx.connected_components(H)) / G.number_of_nodes()
    return Tc, giant

random_set = list(rng.choice(N, n_vac, replace=False))
target_set = [v for v, _ in sorted(G.degree(), key=lambda x: -x[1])[:n_vac]]

# 熟人免疫：反复随机选节点 u，再从其邻居中随机选一个加入接种集合，直到凑满 n_vac 个
acq = set()
while len(acq) < n_vac:
    u = int(rng.integers(N))
    nb = list(G.neighbors(u))
    acq.add(nb[rng.integers(len(nb))])
acq_set = list(acq)

res = {}
for name, S in [("随机", random_set), ("目标", target_set), ("熟人", acq_set)]:
    Tc, giant = evaluate(G, S)
    res[name] = (Tc, giant)
    print("%s免疫: 剩余网络 T_c = %.3f, 巨分支比例 = %.3f" % (name, Tc, giant))

import matplotlib.pyplot as plt
labels = ["random", "targeted", "acquaintance"]
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
ax1.bar(labels, [v[0] for v in res.values()], color=["0.6", "tab:blue", "tab:green"], width=0.55)
ax1.axhline(0.149, ls="--", c="tab:red", label="transmissibility T = 0.149")
ax1.set_ylabel("T_c of remaining network"); ax1.legend(); ax1.set_title("Threshold after 10% vaccinated")
ax2.bar(labels, [v[1] for v in res.values()], color=["0.6", "tab:blue", "tab:green"], width=0.55)
ax2.set_ylim(0, 1); ax2.set_ylabel("giant component / N"); ax2.set_title("Giant component barely changes")
plt.tight_layout(); plt.show()

# %% 示例：扩散中心性与独立级联
# 扩散中心性 DC = sum_{t=1..T} (q A)^t · 1。在空手道俱乐部网络上取 q=0.15, T=3，
# 与度中心性比较排名前 5 的节点；再用独立级联模型（每条边一次机会，概率 q）
# 模拟每个节点作为单种子的平均传播规模（200 次平均），用 Spearman 相关比较两种中心性与它的一致程度。
# 解读：两个相关系数越接近 1，说明该中心性越能预测单种子的传播能力。
import numpy as np
import networkx as nx
from scipy.stats import spearmanr

G = nx.karate_club_graph()
A = nx.to_numpy_array(G, weight=None)
n = A.shape[0]
q, Tmax = 0.15, 3

M = q * A
P = np.eye(n); S = np.zeros((n, n))
for _ in range(Tmax):          # 累加 M + M^2 + M^3
    P = P @ M
    S += P
DC = S @ np.ones(n)

def ic_spread(G, seed, q, rng):
    active, frontier = {seed}, [seed]
    while frontier:
        nxt = []
        for u in frontier:
            for v in G.neighbors(u):
                if v not in active and rng.random() < q:
                    active.add(v); nxt.append(v)
        frontier = nxt
    return len(active)

rng = np.random.default_rng(0)
spread = np.array([np.mean([ic_spread(G, s, q, rng) for _ in range(200)]) for s in range(n)])
deg = A.sum(1)
print("度 前5:", np.argsort(-deg)[:5].tolist())
print("DC 前5:", np.argsort(-DC)[:5].tolist())
print("IC 规模 前5:", np.argsort(-spread)[:5].tolist())
print("Spearman(度, IC) = %.3f" % spearmanr(deg, spread)[0])
print("Spearman(DC, IC) = %.3f" % spearmanr(DC, spread)[0])

import matplotlib.pyplot as plt
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
for ax, x, name in [(ax1, deg, "degree"), (ax2, DC, "diffusion centrality")]:
    ax.scatter(x, spread, s=30, c="tab:blue", alpha=0.7)
    for v in np.argsort(-spread)[:3]:
        ax.annotate(str(v), (x[v], spread[v]), fontsize=8, xytext=(3, 3), textcoords="offset points")
    ax.set_xlabel(name); ax.set_ylabel("mean IC spread (single seed)")
    ax.set_title("Spearman rho = %.2f" % spearmanr(x, spread)[0])
plt.tight_layout(); plt.show()

# %% 示例：三种阈值近似的比较——异质平均场、淬火平均场与非回溯矩阵
# 同一张网络可以给出三个不同的 SIR 阈值估计：
#   HMF：T_c = <k>/(<k^2>-<k>)；QMF：T_c ≈ 1/Λ_max(A)；消息传递：T_c = 1/ρ(B)，B 为非回溯矩阵。
# ρ(B) 用 Ihara–Bass 公式化成 2N×2N 矩阵 [[A, I-D], [I, 0]] 的最大特征值来算，避免构造 2m×2m 的 B。
# 再用“键渗流”精确地模拟 SIR 最终规模（每条边以概率 T 保留，取种子所在分支），看哪一个估计最接近实际转变点。
# 解读：三者的大小关系一般为 QMF ≤ 非回溯，且 1/Λ_max 常偏低（Λ_max ≥ sqrt(k_max)，被单个枢纽拉高）；
#       有限网络中转变是平滑的，最大分支在非回溯估计附近开始明显离开 0。
import numpy as np
import networkx as nx
import scipy.sparse as sp
import scipy.sparse.linalg as spla

rng = np.random.default_rng(2)
deg_seq = np.clip(np.round(rng.pareto(1.6, 3000) * 2 + 2), 2, 300).astype(int)
if deg_seq.sum() % 2:
    deg_seq[0] += 1
G = nx.Graph(nx.configuration_model(deg_seq, seed=2))
G.remove_edges_from(nx.selfloop_edges(G))
G = G.subgraph(max(nx.connected_components(G), key=len)).copy()
G = nx.convert_node_labels_to_integers(G)
N = G.number_of_nodes()

k = np.array([d for _, d in G.degree()], dtype=float)
Tc_hmf = k.mean() / ((k**2).mean() - k.mean())
A = nx.to_scipy_sparse_array(G, format="csr", dtype=float)
lam_max = spla.eigsh(A, k=1, which="LA")[0][0]
I = sp.identity(N, format="csr")
D = sp.diags(k)
M = sp.bmat([[A, I - D], [I, None]], format="csr")
rho_B = np.max(np.abs(spla.eigs(M, k=1, which="LM")[0]))
print("N = %d, <k> = %.2f, k_max = %d" % (N, k.mean(), k.max()))
print("HMF  T_c = %.4f" % Tc_hmf)
print("QMF  T_c = 1/Λ_max = %.4f" % (1 / lam_max))
print("非回溯 T_c = 1/ρ(B) = %.4f" % (1 / rho_B))

def giant_after_percolation(G, T, rng, runs=30):
    """键渗流：每条边以概率 T 保留，返回最大连通分支的平均相对大小（即大暴发的最终规模）。"""
    edges = np.array(G.edges())
    out = []
    for _ in range(runs):
        H = nx.Graph(); H.add_nodes_from(G); H.add_edges_from(edges[rng.random(len(edges)) < T])
        out.append(max(len(c) for c in nx.connected_components(H)) / N)
    return np.mean(out)

Ts, giants = [0.03, 0.05, 0.07, 0.09, 0.12, 0.15, 0.20], []
for T in Ts:
    giants.append(giant_after_percolation(G, T, rng))
    print("T = %.2f  最大分支（大暴发规模）= %.4f" % (T, giants[-1]))

import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(6.4, 4.2))
ax.plot(Ts, giants, "ko-", label="bond percolation (simulated)")
for x, name, ls in [(Tc_hmf, "HMF", ":"), (1 / lam_max, "QMF 1/Lambda_max", "--"), (1 / rho_B, "non-backtracking 1/rho(B)", "-.")]:
    ax.axvline(x, ls=ls, c="tab:red" if ls == "-." else "0.4", label="%s = %.3f" % (name, x))
ax.set_xlabel("transmissibility T"); ax.set_ylabel("largest outbreak size / N"); ax.legend(fontsize=8)
ax.set_title("Outbreak size departs from 0 near the NB threshold")
plt.tight_layout(); plt.show()

# %% 示例：边基仓室模型（EBCM）与精确随机模拟的比较
# Miller–Volz 边基模型把配置模型上的 SIR 化为一个关于 θ 的常微分方程：
#   dθ/dt = -β θ + β ψ'(θ)/<k> + γ (1-θ),  S = ψ(θ),  dR/dt = γ I,  I = 1 - S - R
# 其中 ψ(x)=Σ P(k) x^k 是度分布的生成函数，θ 为“一条随机边尚未传来感染”的概率。
# 精确模拟用事件驱动法：每个感染者的恢复时间 ~ Exp(γ)，沿每条边的传播时间 ~ Exp(β)，
# 只有传播时间早于恢复时间才发生传播（与连续时间马尔可夫 SIR 同分布）。
# 解读：对大规模配置模型，EBCM 曲线与随机模拟的平均曲线（按暴发时刻对齐后）几乎重合；
#       同一参数下，均匀混合 ODE（R0 = β<k>/γ）会高估峰值与最终规模。
import heapq
import numpy as np
import networkx as nx
from scipy.integrate import solve_ivp

rng = np.random.default_rng(0)
N = 5000
deg_seq = rng.choice([2, 3, 4, 10], size=N, p=[0.35, 0.3, 0.25, 0.1])
if deg_seq.sum() % 2:
    deg_seq[0] += 1
G = nx.Graph(nx.configuration_model(deg_seq, seed=0))
G.remove_edges_from(nx.selfloop_edges(G))
beta, gamma = 0.8, 1.0

def fast_sir(G, beta, gamma, seed, rng, tmax=40):
    status = {}
    rec_time = {}
    pq = [(0.0, "inf", seed)]
    times, counts = [], []
    S, I, R = G.number_of_nodes(), 0, 0
    while pq:
        t, ev, v = heapq.heappop(pq)
        if t > tmax:
            break
        if ev == "inf":
            if status.get(v, "S") != "S":
                continue
            status[v] = "I"; S -= 1; I += 1
            rec_time[v] = t + rng.exponential(1 / gamma)
            heapq.heappush(pq, (rec_time[v], "rec", v))
            for u in G.neighbors(v):
                if status.get(u, "S") == "S":
                    tt = t + rng.exponential(1 / beta)
                    if tt < rec_time[v]:
                        heapq.heappush(pq, (tt, "inf", u))
        else:
            status[v] = "R"; I -= 1; R += 1
        times.append(t); counts.append((S, I, R))
    return np.array(times), np.array(counts) / G.number_of_nodes()

k = np.array([d for _, d in G.degree()]); vals, cnt = np.unique(k, return_counts=True); P = cnt / cnt.sum()
kmean = (vals * P).sum()
psi = lambda x: (P * x**vals).sum()
dpsi = lambda x: (P * vals * x**(vals - 1)).sum()
eps = 1e-3
def rhs(t, y):
    th, R = y
    S = psi(th); I = 1 - S - R
    return [-beta * th + beta * dpsi(th) / kmean + gamma * (1 - th), gamma * I]
tgrid = np.linspace(0, 40, 401)
sol = solve_ivp(rhs, (0, 40), [1 - eps, 0.0], t_eval=tgrid, rtol=1e-8)
I_ebcm = 1 - np.array([psi(t) for t in sol.y[0]]) - sol.y[1]

# 随机模拟：只保留发生大暴发的轨迹，并按 I 达到 1% 的时刻与 EBCM 对齐
t_ebcm_1 = tgrid[np.argmax(I_ebcm > 0.01)]
curves = []
for r in range(30):
    t, c = fast_sir(G, beta, gamma, int(rng.integers(N)), rng)
    if c[-1, 2] > 0.1:
        t0 = t[np.argmax(c[:, 1] > 0.01)]
        curves.append(np.interp(tgrid, t - t0 + t_ebcm_1, c[:, 1], left=0, right=0))
I_sim = np.mean(curves, axis=0)
R0_hom = beta * kmean / gamma
r_hom = 1 - np.exp(-R0_hom)  # 迭代求均匀混合最终规模
for _ in range(200):
    r_hom = 1 - np.exp(-R0_hom * r_hom)
print("大暴发次数：%d / 30" % len(curves))
print("峰值 I：EBCM = %.3f，模拟 = %.3f" % (I_ebcm.max(), I_sim.max()))
print("最终规模：EBCM = %.3f，均匀混合 ODE = %.3f" % (1 - psi(sol.y[0][-1]), r_hom))

import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(6.4, 4.2))
for c in curves:
    ax.plot(tgrid, c, c="0.8", lw=0.6)
ax.plot(tgrid, I_sim, "k-", lw=2, label="stochastic mean (aligned)")
ax.plot(tgrid, I_ebcm, "--", c="tab:red", lw=2, label="EBCM")
ax.set_xlabel("time"); ax.set_ylabel("infected fraction I(t)"); ax.legend()
ax.set_title("EBCM matches exact simulation on configuration model")
plt.tight_layout(); plt.show()

# %% 示例：活动驱动时间网络上的 SIS 阈值
# 活动驱动模型（Perra 等 2012）：每个时间步，节点 i 以概率 a_i 被激活，向 m 个随机节点发出接触，
# 接触只持续一个时间步。感染者每步以概率 μ 恢复，每次 S–I 接触以概率 λ 传播。
# 线性化平均场（推导见“数学推导与算法”D 节）给出阈值 λ_c = μ / [m(<a> + sqrt(<a^2>))]；
# 若忽略活动性的异质性（人人活动性都取 <a>），阈值为 μ / (2m<a>)，更高。
# 解读：模拟的稳态流行率在异质理论阈值附近开始离开 0，低于“同质”估计——活跃个体既常感染别人也常被感染。
import numpy as np

rng = np.random.default_rng(1)
N, m, mu, steps = 5000, 1, 0.1, 1500
a = np.where(rng.random(N) < 0.2, 0.5, 0.05)          # 20% 高活跃个体
lam_c = mu / (m * (a.mean() + np.sqrt((a**2).mean())))
lam_hom = mu / (2 * m * a.mean())
print("<a> = %.3f, sqrt(<a^2>) = %.3f" % (a.mean(), np.sqrt((a**2).mean())))
print("异质平均场 λ_c = %.3f；忽略活动异质性的估计 = %.3f" % (lam_c, lam_hom))

def simulate(lam, rng):
    inf = np.zeros(N, bool); inf[rng.choice(N, 250, replace=False)] = True
    prev = []
    for t in range(steps):
        src = np.repeat(np.flatnonzero(rng.random(N) < a), m)
        dst = rng.integers(N, size=src.size)
        new = np.zeros(N, bool)
        for u, v in ((src, dst), (dst, src)):          # 接触是双向的
            hit = inf[u] & ~inf[v] & (rng.random(u.size) < lam)
            new[v[hit]] = True
        inf = (inf & ~(rng.random(N) < mu)) | new
        if t >= steps - 500:
            prev.append(inf.mean())
        if not inf.any():
            return 0.0
    return float(np.mean(prev))

lams, prevs = [0.6 * lam_c, 0.9 * lam_c, 1.2 * lam_c, 1.6 * lam_c, lam_hom, 2.5 * lam_c], []
for lam in lams:
    prevs.append(simulate(lam, rng))
    print("λ = %.3f (= %.1f λ_c)  稳态流行率 = %.4f" % (lam, lam / lam_c, prevs[-1]))

import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(6.4, 4.2))
order = np.argsort(lams)
ax.plot(np.array(lams)[order], np.array(prevs)[order], "ko-", label="simulation")
ax.axvline(lam_c, ls="--", c="tab:red", label="heterogeneous MF lambda_c")
ax.axvline(lam_hom, ls=":", c="0.4", label="homogeneous estimate")
ax.set_xlabel("infection probability lambda"); ax.set_ylabel("stationary prevalence"); ax.legend()
ax.set_title("Prevalence rises at the heterogeneous threshold")
plt.tight_layout(); plt.show()

# %% 示例：集合种群模型与有效距离
# 在 M 个城市组成的随机流动网络上运行随机集合种群 SIR（城市内均匀混合，城市间按旅行概率移动感染者）。
# 用 Brockmann–Helbing 有效距离 d_mn = 1 - ln P_mn（P_mn 为离开 n 的旅客去往 m 的比例）求从源城市出发的最短有效路径，
# 比较“到达时间”与有效距离、跳数距离的相关性。
# 解读：流量高度不均时，跳数距离几乎相同的城市到达时间可以差很多；到达时间与有效距离的相关明显高于
#       与跳数距离的相关，这就是 Brockmann 与 Helbing（2013）所说的“隐藏几何”。
import numpy as np
import networkx as nx
from scipy.stats import pearsonr, spearmanr

rng = np.random.default_rng(4)
M = 150
G = nx.barabasi_albert_graph(M, 6, seed=4)
pop = (rng.pareto(1.5, M) + 1) * 5e4
W = np.zeros((M, M))
for u, v in G.edges():                       # 流量 ∝ (P_u P_v)^0.5（重力模型的简化）
    W[u, v] = W[v, u] = np.sqrt(pop[u] * pop[v]) * rng.lognormal(0, 2.0)
travel_rate = 0.002 * W.sum(1) / W.sum(1).mean()   # 每天离开城市的人口比例
Pmat = W / W.sum(1, keepdims=True)                  # P[n, m]：离开 n 去 m 的比例

H = nx.DiGraph()
for n in range(M):
    for mm in np.flatnonzero(Pmat[n]):
        H.add_edge(n, mm, d=1 - np.log(Pmat[n, mm]))
src = int(np.argmax(pop))
d_eff = nx.single_source_dijkstra_path_length(H, src, weight="d")
d_hop = nx.single_source_shortest_path_length(G, src)

beta, gamma = 0.5, 0.25
S = pop.copy(); I = np.zeros(M); I[src] = 10; S[src] -= 10
arrival = np.full(M, np.nan); arrival[src] = 0
for day in range(1, 400):
    newinf = rng.binomial(S.astype(int), 1 - np.exp(-beta * I / pop))
    rec = rng.binomial(I.astype(int), gamma)
    S -= newinf; I += newinf - rec
    travelers = rng.binomial(I.astype(int), np.minimum(travel_rate, 1))
    for n in np.flatnonzero(travelers):
        dest = rng.multinomial(travelers[n], Pmat[n])
        I[n] -= travelers[n]; I += dest
    hit = np.isnan(arrival) & (I >= 1)
    arrival[hit] = day
ok = ~np.isnan(arrival) & (np.arange(M) != src)
nodes = np.flatnonzero(ok)
print("被感染城市 %d / %d" % (ok.sum(), M - 1))
print("到达时间 vs 有效距离 r = %.2f" % pearsonr([d_eff[n] for n in nodes], arrival[nodes])[0])
print("到达时间 vs 跳数距离 r = %.2f" % pearsonr([d_hop[n] for n in nodes], arrival[nodes])[0])

import matplotlib.pyplot as plt
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
for ax, d, name in [(ax1, d_eff, "effective distance"), (ax2, d_hop, "hop distance")]:
    x = np.array([d[n] for n in nodes], float)
    if ax is ax2:
        x = x + rng.uniform(-0.12, 0.12, x.size)      # 横向抖动，便于看清重叠的点
    ax.scatter(x, arrival[nodes], s=20, alpha=0.6)
    ax.set_xlabel(name); ax.set_title("r = %.2f" % pearsonr([d[n] for n in nodes], arrival[nodes])[0])
ax1.set_ylabel("arrival time (days)")
fig.suptitle("Arrival time follows effective distance, not hops")
plt.tight_layout(); plt.show()

# %% 示例：超级传播——负二项后代分布、早期灭绝与“20/80”
# 用分支过程模拟疾病早期：每个感染者的继发病例数 ~ 负二项(R0, k)，离散度 k 越小个体差异越大。
# 计算 (1) 疫情自行灭绝的概率（解 q = g(q)，g 为负二项生成函数）；
#      (2) 造成 80% 传播的感染者比例。
# 解读：R0 相同时，k 越小越容易早期灭绝，但一旦暴发更“爆炸”；少数感染者贡献大部分传播，
#       这与 Lloyd-Smith 等 2005 的结论一致，也说明针对个体的干预比全员均匀干预更有效。
import numpy as np
import matplotlib.pyplot as plt

R0 = 2.5
rng = np.random.default_rng(0)
fig, ax = plt.subplots(figsize=(6.4, 4.2))
for kdisp, ls in zip([0.1, 0.5, 1.0, 10.0], ["-", "--", "-.", ":"]):
    g = lambda s: (1 + R0 / kdisp * (1 - s)) ** (-kdisp)   # 负二项生成函数
    q = 0.0
    for _ in range(5000):
        q = g(q)
    p = kdisp / (kdisp + R0)
    off = rng.negative_binomial(kdisp, p, size=200000)
    srt = np.sort(off)[::-1]
    frac = np.searchsorted(np.cumsum(srt), 0.8 * srt.sum()) / len(srt)
    print("k = %5.1f  灭绝概率 = %.3f  零继发病例比例 = %.3f  造成 80%% 传播的感染者比例 = %.3f"
          % (kdisp, q, (off == 0).mean(), frac))
    cum = np.cumsum(srt) / srt.sum()
    idx = np.linspace(0, len(srt) - 1, 400).astype(int)
    ax.plot(idx / len(srt), cum[idx], ls=ls, lw=2, label="k = %g (extinction %.2f)" % (kdisp, q))
ax.axhline(0.8, c="0.7", lw=0.8)
ax.set_xlabel("fraction of cases (most infectious first)"); ax.set_ylabel("fraction of transmission")
ax.legend(); ax.set_title("Small k: few cases cause most transmission (R0 = 2.5)")
plt.tight_layout(); plt.show()

# %% 示例：从发病曲线估计时变再生数 R_t（Cori 方法）
# 先用已知的 R_t（第 40 天因干预从 2.0 降到 0.7）和代际间隔分布 w_s 生成一条发病曲线（更新方程 + 泊松噪声），
# 再用 Cori 等 2013 的贝叶斯估计：在长度为 τ 的滑动窗口内，R_t 的后验为 Gamma 分布，
#   形状 = a + Σ I_s，  速率 = 1/b + Σ Λ_s，  Λ_s = Σ_{u≥1} w_u I_{s-u}（总感染力）。
# 解读：估计值在约一个窗口长度的滞后后跟上真实 R_t 的下降；早期病例少时可信区间很宽。
import numpy as np
from scipy.stats import gamma as gamma_dist

rng = np.random.default_rng(3)
T = 90
s = np.arange(1, 21)
w = gamma_dist.pdf(s, a=2.5, scale=2.0); w /= w.sum()      # 代际间隔：均值约 5 天
R_true = np.where(np.arange(T) < 40, 2.0, 0.7)
I = np.zeros(T); I[0] = 10
for t in range(1, T):
    lam = sum(w[u - 1] * I[t - u] for u in range(1, min(t, 20) + 1))
    I[t] = rng.poisson(R_true[t] * lam)

tau, a_prior, b_prior = 7, 1.0, 5.0
Lam = np.array([sum(w[u - 1] * I[t - u] for u in range(1, min(t, 20) + 1)) for t in range(T)])
for t in range(10, T, 8):
    shape = a_prior + I[t - tau + 1:t + 1].sum()
    rate = 1 / b_prior + Lam[t - tau + 1:t + 1].sum()
    lo, hi = gamma_dist.ppf([0.025, 0.975], shape, scale=1 / rate)
    print("第 %2d 天  真实 R = %.1f  估计 R_t = %.2f  95%%CrI [%.2f, %.2f]  当日病例 %d"
          % (t, R_true[t], shape / rate, lo, hi, I[t]))

import matplotlib.pyplot as plt
ts = np.arange(tau, T)
sh = np.array([a_prior + I[t - tau + 1:t + 1].sum() for t in ts])
rt = np.array([1 / b_prior + Lam[t - tau + 1:t + 1].sum() for t in ts])
lo, hi = gamma_dist.ppf(0.025, sh, scale=1 / rt), gamma_dist.ppf(0.975, sh, scale=1 / rt)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
ax1.bar(np.arange(T), I, color="0.6", width=1.0); ax1.axvline(40, ls="--", c="tab:red")
ax1.set_xlabel("day"); ax1.set_ylabel("daily cases"); ax1.set_title("Simulated epidemic curve")
ax2.fill_between(ts, lo, hi, color="tab:blue", alpha=0.25, label="95% CrI")
ax2.plot(ts, sh / rt, c="tab:blue", label="Cori estimate"); ax2.plot(np.arange(T), R_true, "k--", label="true R_t")
ax2.axhline(1, c="0.7", lw=0.8); ax2.set_ylim(0, 4)
ax2.set_xlabel("day"); ax2.set_ylabel("R_t"); ax2.legend(); ax2.set_title("Estimate lags the drop by ~one window")
plt.tight_layout(); plt.show()

# %% 示例：向前追踪与向后追踪——传播树中的朋友悖论
# 在度异质网络上做 SIR 模拟并记录“谁传染了谁”（传播树）。
# 比较：随机挑一个感染者，(a) 它自己的继发病例数（向前追踪能发现的人数），
#       (b) 它的“传染源”的继发病例数（向后追踪找到的源头还能牵出多少人）。
# 解读：整个暴发中“每个病例平均只传给约 1 人”（除种子外每个病例恰有一个传染源），
#       但随机病例的传染源平均传给了多得多的人——被感染者更可能来自“多产”的传染源，
#       这正是 Kojaku 等 2021 指出向后追踪更有效的原因。
import numpy as np
import networkx as nx

rng = np.random.default_rng(5)
G = nx.barabasi_albert_graph(5000, 2, seed=5)
beta, gamma = 0.15, 0.3

def sir_tree(G, seed, rng):
    parent = {seed: None}; state = {seed: 1}; frontier = [seed]
    while frontier:
        nxt = []
        for u in frontier:
            for v in G.neighbors(u):
                if v not in state and rng.random() < beta:
                    state[v] = 1; parent[v] = u; nxt.append(v)
            if rng.random() < gamma:
                state[u] = 2
            else:
                nxt.append(u)
        frontier = [v for v in nxt if state[v] == 1]
    return parent

own, src_off = [], []
for _ in range(20):
    parent = sir_tree(G, int(rng.integers(5000)), rng)
    if len(parent) < 200:
        continue
    off = {}
    for v, p in parent.items():
        if p is not None:
            off[p] = off.get(p, 0) + 1
    for v, p in parent.items():
        own.append(off.get(v, 0))
        if p is not None:
            src_off.append(off[p])
print("随机感染者的平均继发病例数（≈R）= %.2f" % np.mean(own))
print("其传染源的平均继发病例数       = %.2f" % np.mean(src_off))
print("继发病例数的方差/均值 = %.2f（>1 表示过度离散）" % (np.var(own) / np.mean(own)))

import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(6.4, 4.2))
bins = np.arange(0, max(max(own), max(src_off)) + 2) - 0.5
ax.hist(own, bins=bins, density=True, histtype="step", lw=2, label="random case (forward)")
ax.hist(src_off, bins=bins, density=True, histtype="step", lw=2, ls="--", label="its infector (backward)")
ax.axvline(np.mean(own), c="tab:blue", lw=0.8); ax.axvline(np.mean(src_off), c="tab:orange", lw=0.8)
ax.set_yscale("log"); ax.set_xlabel("number of secondary cases"); ax.set_ylabel("probability"); ax.legend()
ax.set_title("Infectors have more offspring (means %.1f vs %.1f)" % (np.mean(own), np.mean(src_off)))
plt.tight_layout(); plt.show()

# %% 示例：影响力最大化——贪心算法与启发式中心性
# 传播模型：每条边以概率 p 处于“通”状态（键渗流；等价于固定感染期的 SIR，也是独立级联在无向图上的常用简化）。
# 种子集合 S 的传播范围 = 含有至少一个种子的“通边分支”的节点总数，用 R 个随机样本平均（共同随机数）。
# 在同一组样本上做贪心选种：每一步加入边际增益最大的节点；期望传播范围是子模函数，贪心有 (1-1/e) 保证。
# 与度最高、k-核最高、集体影响 CI_2 = (k_i-1) Σ_{d(i,j)=2} (k_j-1)（Morone 与 Makse 2015）比较，
# 最后在另一组新样本上评估，避免“在训练样本上挑出幸运节点”的乐观偏差。
# 网络：一个稠密大社团（枢纽都在这里）+ 7 个小社团，社团间只有极少的桥。
# 解读：度、k-核、CI 的前 K 名全部挤在大社团里，彼此重叠，甚至不如随机选种；贪心会把种子分散到各社团。
import numpy as np
import networkx as nx
import scipy.sparse as sp
from scipy.sparse.csgraph import connected_components

sizes = [600] + [200] * 7                 # 一个稠密大社团 + 7 个较稀疏的小社团
P = [[(0.02 if i == 0 else 0.03) if i == j else 0.00002 for j in range(8)] for i in range(8)]
G = nx.stochastic_block_model(sizes, P, seed=7)
N, K = G.number_of_nodes(), 10
edges = np.array(G.edges())
k = np.array([d for _, d in G.degree()], float)
p = 0.2                                  # 每条边“通”的概率

def samples(R, rng):
    labs, sizes = [], []
    for _ in range(R):
        e = edges[rng.random(len(edges)) < p]
        A = sp.coo_matrix((np.ones(len(e)), (e[:, 0], e[:, 1])), shape=(N, N))
        _, lab = connected_components(A, directed=False)
        labs.append(lab); sizes.append(np.bincount(lab))
    return labs, sizes

def spread(S, labs, sizes):
    return np.mean([sz[np.unique(lab[list(S)])].sum() for lab, sz in zip(labs, sizes)])

train = samples(200, np.random.default_rng(0))
seeds = []
covered = [np.zeros(len(sz), bool) for sz in train[1]]
for _ in range(K):
    gain = np.zeros(N)
    for lab, sz, cov in zip(*train, covered):
        gain += np.where(cov[lab], 0, sz[lab])
    gain[seeds] = -1
    v = int(np.argmax(gain)); seeds.append(v)
    for lab, cov in zip(train[0], covered):
        cov[lab[v]] = True

deg = dict(G.degree()); core = nx.core_number(G)
ci = {}
for i in G:
    ring = [j for j, d in nx.single_source_shortest_path_length(G, i, cutoff=2).items() if d == 2]
    ci[i] = (deg[i] - 1) * sum(deg[j] - 1 for j in ring)
top = lambda score: sorted(G, key=lambda v: (-score[v], -deg[v]))[:K]
test = samples(500, np.random.default_rng(1))
rng = np.random.default_rng(2)
vals = []
for name, S in [("贪心", seeds), ("度", top(deg)), ("k-核", top(core)), ("CI_2", top(ci)),
                ("随机", list(rng.choice(N, K, replace=False)))]:
    vals.append(spread(S, *test))
    print("%-6s 期望传播范围 = %.1f" % (name, vals[-1]))

import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(6.4, 4.2))
ax.bar(["greedy", "degree", "k-core", "CI_2", "random"], vals,
       color=["tab:blue", "0.6", "0.6", "0.6", "0.85"], width=0.6)
ax.set_ylabel("expected spread (held-out samples)")
ax.set_title("Greedy spreads seeds across communities (K = %d)" % K)
plt.tight_layout(); plt.show()

# %% 示例：复杂传染——阈值模型在聚集网络与随机网络上的级联
# 线性阈值模型：节点在已激活邻居比例 ≥ θ 时被激活（θ=0.25）。
# 比较三种平均度相同（k=6）的网络：环形格子（高聚集）、少量重连的小世界网络、完全随机重连。
# 种子为格子上相邻的一小段节点。对比：独立级联（简单传染，p=0.3）在同样网络上的覆盖率。
# 解读：复杂传染在聚集的格子上能传遍网络，在随机网络上卡在种子附近；
#       简单传染恰好相反——随机捷径让它传得更快更远（Centola 与 Macy 2007）。
import numpy as np
import networkx as nx

N, kdeg, theta = 1000, 6, 0.25
seeds = list(range(6))

def threshold_cascade(G):
    active = set(seeds); changed = True
    while changed:
        changed = False
        for v in G:
            if v not in active:
                nb = list(G.neighbors(v))
                if nb and sum(u in active for u in nb) / len(nb) >= theta:
                    active.add(v); changed = True
    return len(active) / G.number_of_nodes()

def ic_cover(G, p, rng, runs=50):
    out = []
    for _ in range(runs):
        active, frontier = set(seeds), list(seeds)
        while frontier:
            nxt = []
            for u in frontier:
                for v in G.neighbors(u):
                    if v not in active and rng.random() < p:
                        active.add(v); nxt.append(v)
            frontier = nxt
        out.append(len(active) / G.number_of_nodes())
    return np.mean(out)

rng = np.random.default_rng(0)
qs, cov_thr, cov_ic = [0.0, 0.05, 1.0], [], []
for q in qs:
    G = nx.watts_strogatz_graph(N, kdeg, q, seed=1)
    cov_thr.append(threshold_cascade(G)); cov_ic.append(ic_cover(G, 0.3, rng))
    print("重连概率 %.2f  聚集系数 %.2f  阈值模型覆盖 %.3f  独立级联覆盖 %.3f"
          % (q, nx.average_clustering(G), cov_thr[-1], cov_ic[-1]))

import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(6.4, 4.2))
x = np.arange(len(qs))
ax.bar(x - 0.18, cov_thr, 0.36, color="tab:blue", label="complex contagion (threshold 0.25)")
ax.bar(x + 0.18, cov_ic, 0.36, color="0.6", hatch="//", label="simple contagion (IC, p = 0.3)")
ax.set_xticks(x, ["lattice (q=0)", "small world (q=0.05)", "random (q=1)"])
ax.set_ylabel("final coverage"); ax.set_ylim(0, 1.05); ax.legend(fontsize=8)
ax.set_title("Clustering helps complex contagion, shortcuts help simple")
plt.tight_layout(); plt.show()

# %% 示例：传播溯源——Jordan 中心与基于观测点的估计
# SI 传播从未知源头出发，只观测到 (a) 某一时刻的感染快照，或 (b) 少数观测点被感染的时刻。
# (a) Jordan 中心：在感染子图中，到其他感染节点最大距离最小的节点；
# (b) 观测点法：对每个候选源 s，若它是源头，则 t_o - d(s,o) 对所有观测点应近似相等，取方差最小者。
# 观测点的选择影响很大：这里比较随机选取与按介数最高选取的观测点（各占 5%）。
# 解读：报告估计源与真实源的平均跳数误差与命中率。介数最高的节点集中在网络中部、彼此信息冗余，
#       反而不如随机分布的观测点；“选谁当观测点”本身是一个需要优化的问题。
import numpy as np
import networkx as nx

G = nx.connected_watts_strogatz_graph(400, 6, 0.1, seed=3)
dist = dict(nx.all_pairs_shortest_path_length(G))
nodes = list(G)
bet = nx.betweenness_centrality(G)

def si_times(src, rng, beta=0.5):
    t_inf = {src: 0}; t = 0; frontier = {src}
    while len(t_inf) < len(G):
        t += 1; new = set()
        for u in list(t_inf):
            for v in G.neighbors(u):
                if v not in t_inf and rng.random() < beta:
                    new.add(v)
        for v in new:
            t_inf[v] = t
    return t_inf

def jordan(t_inf, T):
    inf = [v for v, t in t_inf.items() if t <= T]
    return min(inf, key=lambda s: max(dist[s][v] for v in inf))

def observer_est(t_inf, obs):
    return min(nodes, key=lambda s: np.var([t_inf[o] - dist[s][o] for o in obs]))

rng = np.random.default_rng(0)
n_obs = 20
obs_rand = list(rng.choice(nodes, n_obs, replace=False))
obs_bet = sorted(nodes, key=lambda v: -bet[v])[:n_obs]
err = {"Jordan 中心(快照)": [], "观测点-随机": [], "观测点-介数": []}
for _ in range(100):
    src = int(rng.integers(400)); t_inf = si_times(src, rng)
    err["Jordan 中心(快照)"].append(dist[src][jordan(t_inf, 6)])
    err["观测点-随机"].append(dist[src][observer_est(t_inf, obs_rand)])
    err["观测点-介数"].append(dist[src][observer_est(t_inf, obs_bet)])
for k_, v in err.items():
    print("%-14s 平均误差 = %.2f 跳，命中率 = %.2f" % (k_, np.mean(v), np.mean(np.array(v) == 0)))

import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(6.4, 4.2))
names = ["Jordan center (snapshot)", "observers: random", "observers: top betweenness"]
mx = max(max(v) for v in err.values())
for (k_, v), name, ls in zip(err.items(), names, ["-", "--", ":"]):
    h = np.bincount(v, minlength=mx + 1) / len(v)
    ax.plot(np.arange(mx + 1), h, ls=ls, marker="o", ms=4, label="%s (mean %.2f)" % (name, np.mean(v)))
ax.set_xlabel("hop distance from true source"); ax.set_ylabel("fraction of trials"); ax.legend(fontsize=8)
ax.set_title("Source localization error (100 SI outbreaks)")
plt.tight_layout(); plt.show()
