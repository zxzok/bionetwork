# 依赖：networkx>=3, numpy, scipy, matplotlib
# 数据：全部示例网络由 networkx 生成（BA、ER、随机分块网络、WS 小世界网络、完全图）；
#       振荡器固有频率与初始相位用 numpy 随机数生成。相位以弧度表示。
#       相位同步指标示例使用合成的 10 Hz 振荡信号与线性混合（模拟 EEG 容积传导），不需要外部数据。
#       依赖 scipy.signal（滤波、希尔伯特变换、交叉谱）与 scipy.optimize（求根）。

# %% 示例：全连接 Kuramoto 模型的同步相变
# 固有频率取洛伦兹分布（半宽 gamma=0.5），理论临界耦合 K_c = 2*gamma = 1，
# 超过临界值后 r = sqrt(1 - K_c/K)。simulate 用平均场形式做欧拉积分，
# 扫描 K = 0, 0.25, ..., 3，记录每个 K 的稳态 r（后一半时间的平均），与理论曲线画在一张图上。
# 解读：K<1 时 r 很小（只剩约 1/sqrt(N) 的有限尺度基线），K>1 后 r 迅速上升并贴近理论值。
import numpy as np
import matplotlib.pyplot as plt

N, gamma = 500, 0.5
# 用分位数取样代替随机抽样，减少有限尺度涨落（洛伦兹分布的反函数为 gamma*tan）
omega = gamma * np.tan(np.pi * (np.arange(1, N + 1) / (N + 1) - 0.5))

def simulate(K, omega, T=60.0, dt=0.05, seed=0):
    rng = np.random.default_rng(seed)
    theta = rng.uniform(0, 2 * np.pi, omega.size)
    rs = []
    for _ in range(int(T / dt)):
        z = np.exp(1j * theta).mean()            # 序参量 r*e^{i psi}
        theta = theta + dt * (omega + K * np.imag(z * np.exp(-1j * theta)))
        rs.append(abs(z))
    rs = np.array(rs)
    return rs[len(rs) // 2:].mean()

Ks = np.arange(0, 3.01, 0.25)
r_sim = np.array([simulate(K, omega) for K in Ks])
print("K:", np.round(Ks, 2).tolist())
print("r:", np.round(r_sim, 2).tolist())

K_th = np.linspace(1.0001, 3, 200)
plt.plot(K_th, np.sqrt(1 - 2 * gamma / K_th), "k-", label="theory")
plt.plot(Ks, r_sim, "o", label="simulation")
plt.axvline(2 * gamma, ls="--", c="gray")
plt.xlabel("K"); plt.ylabel("r"); plt.legend(); plt.title("Kuramoto phase transition")
plt.show()

# %% 示例：网络结构如何影响同步起点
# 在 ER 与 BA 网络（N=300，平均度相同）上运行网络 Kuramoto 模型：
#   dtheta_i/dt = omega_i + K * sum_j A_ij sin(theta_j - theta_i)
# 固有频率取标准高斯分布，K_0 = 2/(pi*g(0)) = 2*sqrt(2*pi)/pi。
# 先用异质平均场 K_c = K_0 * <k>/<k^2> 估计两种网络的临界耦合，再画模拟的 r(K) 曲线。
# 解读：BA 网络的 <k^2> 更大，K_c 更小，r 更早开始上升。
import numpy as np
import networkx as nx
import scipy.sparse as sp
import matplotlib.pyplot as plt

N = 300
G_ba = nx.barabasi_albert_graph(N, 3, seed=2)
G_er = nx.gnm_random_graph(N, G_ba.number_of_edges(), seed=2)
omega = np.random.default_rng(5).standard_normal(N)
K0 = 2 * np.sqrt(2 * np.pi) / np.pi

def net_kuramoto(G, K, omega, T=40.0, dt=0.05, seed=0):
    A = sp.csr_matrix(nx.to_scipy_sparse_array(G, nodelist=range(G.number_of_nodes())))
    theta = np.random.default_rng(seed).uniform(0, 2 * np.pi, omega.size)
    rs = []
    for _ in range(int(T / dt)):
        s, c = np.sin(theta), np.cos(theta)
        coupling = c * (A @ s) - s * (A @ c)       # = sum_j A_ij sin(theta_j - theta_i)
        theta = theta + dt * (omega + K * coupling)
        rs.append(abs(np.exp(1j * theta).mean()))
    return np.mean(rs[len(rs) // 2:])

def Kc_hmf(G):
    k = np.array([d for _, d in G.degree()], dtype=float)
    return K0 * k.mean() / (k**2).mean()

for name, G in [("ER", G_er), ("BA", G_ba)]:
    print(name, "K_c 估计 =", round(Kc_hmf(G), 3))

Ks = np.linspace(0, 0.6, 9)
for name, G in [("ER", G_er), ("BA", G_ba)]:
    r = [net_kuramoto(G, K, omega) for K in Ks]
    print(name, "r(K):", np.round(r, 2).tolist())
    plt.plot(Ks, r, "o-", label=name)
plt.xlabel("K"); plt.ylabel("r"); plt.legend(); plt.title("Kuramoto on networks")
plt.show()

# %% 示例：模块化网络上的分层同步
# 4 个社团、每个 40 个节点，社团内连接概率 0.3，社团间 0.005。所有振荡器固有频率相同（=0），
# 初始相位随机。记录每个时刻的“社团内平均序参量”（4 个社团各自的 r 取平均）和“全局序参量”。
# 解读：社团内部先同步（r_local 很快接近 1），全局同步要慢得多。
import numpy as np
import networkx as nx
import scipy.sparse as sp
import matplotlib.pyplot as plt

sizes = [40, 40, 40, 40]
G = nx.random_partition_graph(sizes, 0.3, 0.005, seed=3)
A = sp.csr_matrix(nx.to_scipy_sparse_array(G, nodelist=range(G.number_of_nodes())))
labels = np.repeat(np.arange(len(sizes)), sizes)
theta = np.random.default_rng(1).uniform(0, 2 * np.pi, G.number_of_nodes())
K, dt, steps = 0.05, 0.1, 1500

r_local, r_global = [], []
for _ in range(steps):
    s, c = np.sin(theta), np.cos(theta)
    theta = theta + dt * K * (c * (A @ s) - s * (A @ c))
    z = np.exp(1j * theta)
    r_global.append(abs(z.mean()))
    r_local.append(np.mean([abs(z[labels == c_].mean()) for c_ in range(len(sizes))]))

t = np.arange(steps) * dt
print("t=20 时 r_local = %.2f, r_global = %.2f" % (r_local[200], r_global[200]))
print("t=%.0f 时 r_local = %.2f, r_global = %.2f" % (t[-1], r_local[-1], r_global[-1]))
plt.plot(t, r_local, label="within communities")
plt.plot(t, r_global, label="global")
plt.xlabel("time"); plt.ylabel("r"); plt.legend(); plt.title("Hierarchical synchronization")
plt.show()

# %% 示例：共识动力学与代数连通度
# 共识动力学 dx/dt = -L x。在 4 种网络（N=60，平均度 4 的环、两种 WS 小世界网络，以及完全图）上，
# 从相同的随机初值出发，记录偏离平均值的误差 ||x - mean(x0)|| 降到初始的 1% 所需的时间，
# 并与拉普拉斯矩阵的第二小特征值（代数连通度 mu_2）比较。
# 解读：mu_2 越大，收敛越快；收敛时间约 ∝ 1/mu_2，因此 mu_2*时间 在各网络间量级相近。
import numpy as np
import networkx as nx

N = 60
nets = {
    "ring": nx.watts_strogatz_graph(N, 4, 0.0, seed=1),
    "WS p=0.1": nx.connected_watts_strogatz_graph(N, 4, 0.1, seed=1),
    "WS p=0.5": nx.connected_watts_strogatz_graph(N, 4, 0.5, seed=1),
    "complete": nx.complete_graph(N),
}
x0 = np.random.default_rng(0).standard_normal(N)

def consensus_time(G, x0, dt=0.01, tol=0.01, tmax=2000):
    L = nx.laplacian_matrix(G, nodelist=range(N)).toarray().astype(float)
    x = x0.copy(); e0 = np.linalg.norm(x0 - x0.mean()); t = 0.0
    while np.linalg.norm(x - x0.mean()) > tol * e0 and t < tmax:
        x = x - dt * (L @ x); t += dt
    return t

for name, G in nets.items():
    L = nx.laplacian_matrix(G, nodelist=range(N)).toarray().astype(float)
    mu2 = np.sort(np.linalg.eigvalsh(L))[1]
    t = consensus_time(G, x0, dt=0.01 if name != "complete" else 0.001)
    print("%-10s mu2 = %.4f  收敛时间 = %.2f  mu2*时间 = %.2f" % (name, mu2, t, mu2 * t))

# 作图：用特征分解得到误差的解析衰减曲线 ||x(t) - mean|| = ||sum_k e^{-mu_k t} (v_k·x0) v_k||
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(6.4, 4.2))
tt = np.logspace(-2, 3, 300)
for (name, G), ls in zip(nets.items(), ["-", "--", "-.", ":"]):
    mu, V = np.linalg.eigh(nx.laplacian_matrix(G, nodelist=range(N)).toarray().astype(float))
    c = V.T @ (x0 - x0.mean())
    err = np.sqrt(((np.exp(-np.outer(tt, mu)) * c) ** 2).sum(1)) / np.linalg.norm(c)
    ax.loglog(tt, err, ls=ls, lw=2, label="%s (mu2 = %.3f)" % (name, mu[1]))
ax.axhline(0.01, c="0.6", lw=0.8)
ax.set_ylim(1e-3, 1.5); ax.set_xlabel("time t"); ax.set_ylabel("relative disagreement")
ax.legend(fontsize=8); ax.set_title("Consensus is faster with larger algebraic connectivity")
plt.tight_layout(); plt.show()

# %% 示例：常见图的拉普拉斯谱、特征值比与谱界
# 用数值方法验证几类图的拉普拉斯谱闭式解（完全图、星图、环、路径），并计算
# 代数连通度 mu_2、最大特征值 mu_N、特征值比 mu_N/mu_2，检查两条常用界：
#   Fiedler 上界 mu_2 <= N/(N-1) * k_min；  mu_N >= k_max + 1（至少有一条边时）。
# 最后演示：在环上加一条“捷径”后 mu_2 增大、特征值比下降（加边不会使任何拉普拉斯特征值变小）。
# 大型稀疏网络用 networkx.algebraic_connectivity（基于稀疏迭代求解）而不是稠密特征分解。
import numpy as np
import networkx as nx

N = 10
graphs = {
    "complete": nx.complete_graph(N),
    "star": nx.star_graph(N - 1),
    "ring": nx.cycle_graph(N),
    "path": nx.path_graph(N),
}
closed = {
    "complete": np.r_[0, [N] * (N - 1)],
    "star": np.r_[0, [1] * (N - 2), N],
    "ring": np.sort(2 - 2 * np.cos(2 * np.pi * np.arange(N) / N)),
    "path": np.sort(2 - 2 * np.cos(np.pi * np.arange(N) / N)),
}
for name, G in graphs.items():
    L = nx.laplacian_matrix(G).toarray().astype(float)
    mu = np.sort(np.linalg.eigvalsh(L))
    k = np.array([d for _, d in G.degree()])
    assert np.allclose(mu, closed[name]), name
    print("%-9s mu2=%.3f muN=%.3f 比值=%.2f | Fiedler 上界 %.3f | k_max+1=%d"
          % (name, mu[1], mu[-1], mu[-1] / mu[1], N / (N - 1) * k.min(), k.max() + 1))

def lap_spec(G):
    return np.sort(np.linalg.eigvalsh(nx.laplacian_matrix(G).toarray().astype(float)))
ring = nx.cycle_graph(N); mu_old = lap_spec(ring)
one = ring.copy(); one.add_edge(0, 5)                 # 一条对径捷径
two = one.copy(); two.add_edge(2, 7)                  # 再加一条
for name, H in [("环", ring), ("+1 条捷径", one), ("+2 条捷径", two)]:
    mu = lap_spec(H)
    print("%-8s mu2=%.3f  mu_N/mu_2=%.2f  特征值相对原环均不减: %s"
          % (name, mu[1], mu[-1] / mu[1], bool(np.all(mu >= mu_old - 1e-12))))
# 环的 mu2 是二重特征值：一条捷径只能抬高其中一个，mu2 不变；两条捷径才使 mu2 上升

big = nx.connected_watts_strogatz_graph(5000, 6, 0.1, seed=0)
print("N=5000 WS 网络的 mu2（稀疏求解）=", round(nx.algebraic_connectivity(big, method="lanczos", seed=0), 4))

import matplotlib.pyplot as plt
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
for (name, G), mk in zip(graphs.items(), ["o", "s", "^", "D"]):
    ax1.plot(np.arange(1, N + 1), lap_spec(G), marker=mk, ls="-", lw=0.8, ms=5, label=name)
ax1.set_xlabel("index i"); ax1.set_ylabel("Laplacian eigenvalue mu_i"); ax1.legend(loc="center left", bbox_to_anchor=(0.12, 0.6)); ax1.set_title("Laplacian spectra (N = 10)")
for (name, H), mk in zip([("ring", ring), ("+1 shortcut", one), ("+2 shortcuts", two)], ["o", "s", "^"]):
    ax2.plot(np.arange(1, N + 1), lap_spec(H), marker=mk, ls="-", lw=0.8, ms=5, label=name)
ax2.set_xlabel("index i"); ax2.set_ylabel("mu_i"); ax2.legend()
ax2.set_title("Adding edges never lowers any eigenvalue")
plt.tight_layout(); plt.show()

# %% 示例：数值计算 Rössler 振子的主稳定函数并判断网络可同步性
# 节点动力学为 Rössler 系统（a=b=0.2, c=7），耦合只通过 x 分量（H(x,y,z) = (x,0,0)）。
# 对每个 alpha 同时积分 Rössler 轨道和变分方程 d zeta/dt = [DF(s) - alpha*E11] zeta，
# 周期性重归一化求最大李雅普诺夫指数 Lambda(alpha)。读出 Lambda<0 的区间 (alpha1, alpha2)。
# 再用 alpha2/alpha1 判断几种 WS 网络（N=100）是否存在使同步稳定的耦合强度 sigma。
# 解读：这类 MSF 的稳定区是有限区间，特征值比 mu_N/mu_2 小于 alpha2/alpha1 的网络才可能同步。
import numpy as np
import networkx as nx

a, b, c = 0.2, 0.2, 7.0
def F(s):
    x, y, z = s
    return np.array([-y - z, x + a * y, b + z * (x - c)])
def DF(s):
    x, y, z = s
    return np.array([[0, -1, -1], [1, a, 0], [z, 0, x - c]])

def rk4(f, u, h):
    k1 = f(u); k2 = f(u + h / 2 * k1); k3 = f(u + h / 2 * k2); k4 = f(u + h * k3)
    return u + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)

h = 0.01
s0 = np.array([1.0, 1.0, 0.0])
for _ in range(20000):                                # 越过暂态
    s0 = rk4(F, s0, h)

E = np.zeros((3, 3)); E[0, 0] = 1.0                  # DH：只耦合 x
def msf(alpha, T=300.0, renorm=100):
    u = np.r_[s0, np.ones(3) / np.sqrt(3)]
    def f(u):
        s, z = u[:3], u[3:]
        return np.r_[F(s), (DF(s) - alpha * E) @ z]
    S = 0.0; steps = int(T / h)
    for n in range(1, steps + 1):
        u = rk4(f, u, h)
        if n % renorm == 0:
            nz = np.linalg.norm(u[3:]); S += np.log(nz); u[3:] /= nz
    return S / T

alphas = np.r_[0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.5, 1, 2, 3, 4, 4.5, 5, 6]
lam = np.array([msf(al) for al in alphas])
for al, l in zip(alphas, lam):
    print("alpha=%5.2f  Lambda=%+.3f" % (al, l))
def bisect(lo, hi, n=7):                             # Lambda 在 lo、hi 两端异号
    slo = np.sign(msf(lo))
    for _ in range(n):
        mid = (lo + hi) / 2
        if np.sign(msf(mid)) == slo: lo = mid
        else: hi = mid
    return (lo + hi) / 2
a1, a2 = bisect(0.10, 0.15), bisect(4.5, 5.0)
print("稳定区约为 (%.3f, %.3f)，alpha2/alpha1 约 %.1f（有限积分时长，末位不可靠）" % (a1, a2, a2 / a1))

ratios = []
for p in [0.0, 0.05, 0.2, 1.0]:
    G = nx.connected_watts_strogatz_graph(100, 6, p, seed=1)
    mu = np.sort(np.linalg.eigvalsh(nx.laplacian_matrix(G).toarray().astype(float)))
    R = mu[-1] / mu[1]
    ratios.append(R)
    print("WS p=%.2f  mu_N/mu_2 = %6.1f  可同步: %s" % (p, R, R < a2 / a1))

import matplotlib.pyplot as plt
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
ax1.axvspan(a1, a2, color="tab:green", alpha=0.15, label="stable region")
ax1.plot(alphas, lam, "ko-", ms=4); ax1.axhline(0, c="0.5", lw=0.8)
ax1.set_xlabel("alpha = sigma * mu"); ax1.set_ylabel("max Lyapunov exponent Lambda(alpha)")
ax1.legend(); ax1.set_title("Roessler MSF (x-coupling)")
ax2.bar(["p=0", "p=0.05", "p=0.2", "p=1"], ratios, color=["tab:blue" if R < a2 / a1 else "0.6" for R in ratios])
ax2.axhline(a2 / a1, ls="--", c="tab:red", label="alpha2/alpha1 = %.1f" % (a2 / a1))
ax2.set_yscale("log"); ax2.set_ylabel("eigenratio mu_N / mu_2"); ax2.legend()
ax2.set_title("WS networks below the line can synchronize")
plt.tight_layout(); plt.show()

# %% 示例：度–频率关联导致的爆发式同步与滞后
# 在 BA 网络（N=500，m=3）上令固有频率等于度 omega_i = k_i（Gómez-Gardeñes 等 2011 的设定），
# 先逐步增大 K（每步沿用上一 K 的终态），再逐步减小 K，记录有效序参量 r。
# 对照组：把同一组频率随机打乱，破坏度–频率关联。
# 解读：关联存在时，前向与后向曲线明显分开（滞后环），r 在前向扫描中突然跳升；打乱后滞后基本消失。
import numpy as np
import networkx as nx
import scipy.sparse as sp
import matplotlib.pyplot as plt

G = nx.barabasi_albert_graph(500, 3, seed=4)
A = sp.csr_matrix(nx.to_scipy_sparse_array(G, nodelist=range(500)))
k = np.asarray(A.sum(axis=1)).ravel()

def sweep(omega, Ks, T=30.0, dt=0.01, seed=0):
    theta = np.random.default_rng(seed).uniform(0, 2 * np.pi, omega.size)
    out = []
    for K in Ks:
        rs = []
        for n in range(int(T / dt)):
            s, c = np.sin(theta), np.cos(theta)
            theta = theta + dt * (omega + K * (c * (A @ s) - s * (A @ c)))
            if n > int(T / dt) // 2:
                rs.append(abs(np.exp(1j * theta).mean()))
        out.append(np.mean(rs))
    return np.array(out), theta

Ks = np.arange(0.5, 3.01, 0.25)
results = {}
for name, omega in [("omega=k", k.astype(float)),
                    ("shuffled", np.random.default_rng(1).permutation(k).astype(float))]:
    omega = omega - omega.mean()                     # 旋转参照系
    fwd, _ = sweep(omega, Ks)
    # 后向扫描从强同步态开始：先在最大 K 处跑一段，再逐步降低
    th = np.zeros(500); bwd = []
    for K in Ks[::-1]:
        rs = []
        for n in range(3000):
            s, c = np.sin(th), np.cos(th)
            th = th + 0.01 * (omega + K * (c * (A @ s) - s * (A @ c)))
            if n > 1500:
                rs.append(abs(np.exp(1j * th).mean()))
        bwd.append(np.mean(rs))
    bwd = np.array(bwd)[::-1]
    results[name] = (fwd, bwd)
    print(name, "前向 r:", np.round(fwd, 2).tolist())
    print(name, "后向 r:", np.round(bwd, 2).tolist())
    print(name, "滞后面积 sum|bwd-fwd|*dK = %.2f" % (np.abs(bwd - fwd).sum() * 0.25))

for name, (fwd, bwd) in results.items():
    plt.plot(Ks, fwd, "o-", label=name + " forward")
    plt.plot(Ks, bwd, "s--", label=name + " backward")
plt.xlabel("K"); plt.ylabel("r"); plt.legend(fontsize=8); plt.title("Explosive synchronization")
plt.show()

# %% 示例：对称性决定的簇同步（星图中的“远程同步”）
# 星图：中心节点与 6 个叶节点都是 Stuart–Landau 振子 dz/dt = (1 + i w - |z|^2) z + K sum_j A_ij (z_j - z)。
# 中心固有频率 w_h=3，叶节点 w=1，K=0.3。叶节点之间没有直接连接，但它们在图的自同构下
# 属于同一轨道（可以任意互换），因此“所有叶节点状态相同”是动力学的不变子空间。
# 先用 networkx 列出自同构轨道，再模拟，比较叶节点之间、叶节点与中心之间的状态差。
# 解读：叶节点彼此完全同步（状态差≈0），中心与它们频率锁定，但振幅和相位都不同，
#       不属于这个簇——互不相连的叶节点因对称位置而同步，这就是簇同步/远程同步。
import numpy as np
import networkx as nx
from networkx.algorithms.isomorphism import GraphMatcher

G = nx.star_graph(6)                                  # 节点 0 为中心
orbits = {}
for iso in GraphMatcher(G, G).isomorphisms_iter():
    for u, v in iso.items():
        orbits.setdefault(u, set()).add(v)
print("自同构轨道:", sorted({tuple(sorted(o)) for o in orbits.values()}))

A = nx.to_numpy_array(G, nodelist=range(7)); deg = A.sum(1)
w = np.r_[3.0, np.ones(6)]
rng = np.random.default_rng(2)
z = rng.standard_normal(7) + 1j * rng.standard_normal(7)
K, dt, steps = 0.3, 0.005, 60000
phases = []
for n in range(steps):
    z = z + dt * ((1 + 1j * w - np.abs(z) ** 2) * z + K * (A @ z - deg * z))
    if n >= steps // 2:
        phases.append(np.angle(z))
ph = np.unwrap(np.array(phases), axis=0)
freq = (ph[-1] - ph[0]) / ((len(ph) - 1) * dt)
print("叶节点之间最大状态差 max|z_i - z_j| = %.1e" % np.abs(z[1:, None] - z[None, 1:]).max())
print("振幅：中心 %.2f，叶节点 %.2f；中心与叶节点相位差 %.2f rad" % (abs(z[0]), abs(z[1]), np.angle(z[0] / z[1])))
print("平均角频率：中心 %.3f，叶节点" % freq[0], np.round(freq[1:], 3).tolist())

import matplotlib.pyplot as plt
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4), gridspec_kw={"width_ratios": [1, 1.6]})
pos = nx.spring_layout(G, seed=0)
nx.draw_networkx_edges(G, pos, ax=ax1, edge_color="0.6", alpha=0.4)
nx.draw_networkx_nodes(G, pos, ax=ax1, node_size=120, node_color=["tab:red"] + ["tab:blue"] * 6)
ax1.set_title("Orbits: hub (red) vs leaves (blue)"); ax1.axis("off")
tt = np.arange(len(ph))[-1500:] * dt
for i in range(7):
    ax2.plot(tt, np.cos(ph[-1500:, i]), c="tab:red" if i == 0 else "tab:blue",
             lw=2.5 if i == 0 else 1.2, ls="-" if i == 0 else "--", label=("hub" if i == 0 else ("leaves" if i == 1 else None)))
ax2.set_xlabel("time (last window)"); ax2.set_ylabel("cos(phase)"); ax2.legend(loc="upper right")
ax2.set_title("Unconnected leaves overlap exactly: cluster synchrony")
plt.tight_layout(); plt.show()

# %% 示例：噪声与时滞对 Kuramoto 同步的影响
# (1) 噪声：全连接 Kuramoto + 白噪声 d theta = [omega + K r sin(psi-theta)] dt + sqrt(2D) dW，
#     omega 取洛伦兹分布（gamma=0.5）。理论 K_c = 2(gamma + D)。用 Euler–Maruyama 积分，
#     比较 D=0 与 D=0.5 时 r(K) 的起点。
# (2) 时滞：两个相同振荡器 omega=1、耦合 K=1、时滞 tau，完全同步时集体频率满足
#     Omega = omega - K sin(Omega*tau)；同相态稳定需 K cos(Omega*tau) > 0。tau 较大时有多个解（多稳态），
#     模拟落在哪一个取决于初始历史。
import numpy as np
from scipy.optimize import brentq

N, gamma = 2000, 0.5
omega = gamma * np.tan(np.pi * (np.arange(1, N + 1) / (N + 1) - 0.5))
def r_noise(K, D, T=60.0, dt=0.02, seed=0):
    rng = np.random.default_rng(seed)
    th = rng.uniform(0, 2 * np.pi, N); rs = []
    for n in range(int(T / dt)):
        z = np.exp(1j * th).mean()
        th = th + dt * (omega + K * np.imag(z * np.exp(-1j * th))) + np.sqrt(2 * D * dt) * rng.standard_normal(N)
        if n > int(T / dt) // 2:
            rs.append(abs(z))
    return np.mean(rs)
r_by_D = {}
for D in [0.0, 0.5]:
    Ks = [1.0, 2.0, 3.0, 4.0]
    r_by_D[D] = [r_noise(K, D) for K in Ks]
    print("D=%.1f 理论 K_c=%.1f  r(K=1,2,3,4) =" % (D, 2 * (gamma + D)),
          np.round(r_by_D[D], 2).tolist())

w, K = 1.0, 1.0
delay_res = []
for tau in [0.0, 0.5, 1.5, 2.5]:
    g = lambda O: O - w + K * np.sin(O * tau)        # 所有解都落在 [w-K, w+K]
    grid = np.linspace(w - K, w + K, 2001)
    roots = [brentq(g, x0, x1) for x0, x1 in zip(grid[:-1], grid[1:]) if g(x0) * g(x1) < 0]
    roots = roots or [w]
    stable = [O for O in roots if K * np.cos(O * tau) > 0]
    print("tau=%.1f  同相解 Omega：" % tau, np.round(roots, 3).tolist(), " 其中稳定：", np.round(stable, 3).tolist())
    # 模拟：两个振荡器，初始相位接近，用历史缓冲实现时滞
    dt = 0.001; d = int(round(tau / dt)); steps = 60000
    th = np.zeros((steps + 1, 2)); th[0] = [0.0, 0.1]
    for n in range(steps):
        past = th[max(n - d, 0)]
        th[n + 1, 0] = th[n, 0] + dt * (w + K * np.sin(past[1] - th[n, 0]))
        th[n + 1, 1] = th[n, 1] + dt * (w + K * np.sin(past[0] - th[n, 1]))
    Om_sim = (th[-1, 0] - th[-20001, 0]) / (20000 * dt)
    print("         模拟（初值接近、历史取常数）得到 Omega=%.3f，末态相位差=%.2f"
          % (Om_sim, np.angle(np.exp(1j * (th[-1, 0] - th[-1, 1])))))
    delay_res.append((tau, roots, stable, Om_sim))

import matplotlib.pyplot as plt
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
for (D, rs), mk in zip(r_by_D.items(), ["o", "s"]):
    l, = ax1.plot(Ks, rs, marker=mk, ls="-", label="D = %.1f" % D)
    ax1.axvline(2 * (gamma + D), ls="--", c=l.get_color(), lw=1)
ax1.set_xlabel("K"); ax1.set_ylabel("r"); ax1.legend(); ax1.set_title("Noise shifts K_c = 2(gamma + D)")
for i, (tau, roots, stable, Om) in enumerate(delay_res):
    unst = [O for O in roots if O not in stable]
    ax2.plot([tau] * len(stable), stable, "o", c="tab:blue", label="stable root" if i == 0 else None)
    ax2.plot([tau] * len(unst), unst, "o", mfc="none", c="0.5", label="unstable root" if i == 0 else None)
    ax2.plot(tau, Om, "x", c="tab:red", ms=10, label="simulation" if i == 0 else None)
ax2.set_xlabel("delay tau"); ax2.set_ylabel("collective frequency Omega"); ax2.legend(fontsize=8)
ax2.set_title("Delay creates multiple in-phase solutions")
plt.tight_layout(); plt.show()

# %% 示例：模块化“连接组”上的 Hopf 全脑模型：模拟功能连接与亚稳态
# 每个脑区是一个 Stuart–Landau（Hopf 范式）振子 z_j = x_j + i y_j：
#   dz_j = [(a + i w_j) z_j - |z_j|^2 z_j + G sum_k C_jk (z_k - z_j)] dt + beta dW_j
# a=-0.02（略低于分岔点，噪声驱动的振荡），w_j 对应 0.04–0.07 Hz 的 fMRI 慢波频率。
# 结构连接 C 用加权随机分块网络代替真实连接组（4 个模块 x 10 个脑区）。
# 对不同全局耦合 G 计算：模拟 FC（x 的相关矩阵）与 C 的相关、以及亚稳态（r(t) 的标准差）。
# 解读：G 太小时 FC 与 SC 几乎无关；G 增大时 FC 逐渐反映结构；过大时全局同步、亚稳态下降。
import numpy as np
import networkx as nx
from scipy.signal import hilbert

rng = np.random.default_rng(0)
sizes = [10] * 4
G0 = nx.random_partition_graph(sizes, 0.6, 0.05, seed=1)
N = G0.number_of_nodes()
C = nx.to_numpy_array(G0, nodelist=range(N)) * rng.uniform(0.5, 1.0, (N, N))
C = np.triu(C, 1); C = C + C.T; C /= C.max()
w = 2 * np.pi * rng.uniform(0.04, 0.07, N)
a, beta, dt, T = -0.02, 0.02, 0.1, 3000.0
iu = np.triu_indices(N, 1)

def run(Gc, seed=0):
    r_ = np.random.default_rng(seed)
    z = 0.1 * (r_.standard_normal(N) + 1j * r_.standard_normal(N))
    xs = []
    deg = C.sum(1)
    for n in range(int(T / dt)):
        coup = Gc * (C @ z - deg * z)
        z = z + dt * ((a + 1j * w) * z - np.abs(z) ** 2 * z + coup) \
              + beta * np.sqrt(dt) * (r_.standard_normal(N) + 1j * r_.standard_normal(N))
        if n % 10 == 0 and n * dt > 500:
            xs.append(z.real.copy())
    X = np.array(xs)
    FC = np.corrcoef(X.T)
    ph = np.angle(hilbert(X - X.mean(0), axis=0))
    r_t = np.abs(np.exp(1j * ph).mean(1))
    return np.corrcoef(FC[iu], C[iu])[0, 1], r_t.mean(), r_t.std()

Gcs, out = [0.0, 0.05, 0.2, 0.5, 1.0], []
for Gc in Gcs:
    sfc, rbar, meta = run(Gc)
    out.append((sfc, rbar, meta))
    print("G=%.2f  corr(FC, SC)=%.2f  平均 r=%.2f  亚稳态 std(r)=%.3f" % (Gc, sfc, rbar, meta))

import matplotlib.pyplot as plt
out = np.array(out)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
ax1.imshow(C, cmap="Greys"); ax1.set_title("Structural connectivity C (4 modules)")
ax1.set_xlabel("region"); ax1.set_ylabel("region")
ax2.plot(Gcs, out[:, 0], "o-", label="corr(FC, SC)")
ax2.plot(Gcs, out[:, 1], "s--", label="mean r")
ax2b = ax2.twinx(); ax2b.plot(Gcs, out[:, 2], "^:", c="tab:red", label="metastability std(r)")
ax2b.set_ylabel("metastability std(r)", color="tab:red")
ax2.set_xlabel("global coupling G"); ax2.set_ylabel("corr / mean r")
h1, l1 = ax2.get_legend_handles_labels(); h2, l2 = ax2b.get_legend_handles_labels()
ax2.legend(h1 + h2, l1 + l2, fontsize=8, loc="center right"); ax2.set_title("FC reflects SC as coupling grows")
plt.tight_layout(); plt.show()

# %% 示例：PLV、PLI、wPLI、相干与虚部相干：容积传导的影响
# 构造两个真实源：s1 为 10 Hz 振荡（带相位噪声），s2 是 s1 延迟 20 ms 的版本加独立噪声，
# 即两源之间存在“滞后的真实耦合”。另有一个无关源 s3。电极信号是源的线性混合（容积传导）：
#   e1 = s1 + 0.5 s3,  e2 = s2 + 0.5 s3,  e3 = s3 + 噪声（e3 与 e1/e2 只通过 s3 的混合“相关”）。
# 对每对电极在 8–12 Hz 带通后计算：PLV、PLI、wPLI、幅度相干 |Coh| 与虚部相干 |ImCoh|，
# 并用时间平移替代数据（circular shift）得到 PLV 的 95% 零分布分位数。
# 解读：e1–e3 只有零滞后的混合，PLV 与 |Coh| 显著偏高，而 PLI、wPLI、ImCoh 接近 0；
#       e1–e2 存在滞后耦合，所有指标都高。
import numpy as np
from scipy.signal import butter, filtfilt, hilbert, csd, welch

fs, T = 250, 120
t = np.arange(int(fs * T)) / fs
rng = np.random.default_rng(0)
phase = 2 * np.pi * 10 * t + np.cumsum(rng.standard_normal(t.size)) * 0.05
s1 = np.cos(phase) + 0.5 * rng.standard_normal(t.size)
lag = int(0.020 * fs)
s2 = np.roll(np.cos(phase), lag) + 0.5 * rng.standard_normal(t.size)
s3 = np.cos(2 * np.pi * 10.5 * t + np.cumsum(rng.standard_normal(t.size)) * 0.05) + 0.5 * rng.standard_normal(t.size)
e = {"e1": s1 + 0.5 * s3, "e2": s2 + 0.5 * s3, "e3": s3 + 0.5 * rng.standard_normal(t.size)}

bb, aa = butter(4, [8, 12], btype="band", fs=fs)
an = {k: hilbert(filtfilt(bb, aa, v)) for k, v in e.items()}

def metrics(x, y):
    S = x * np.conj(y)                               # 瞬时交叉谱
    dphi = np.angle(S)
    plv = abs(np.mean(np.exp(1j * dphi)))
    pli = abs(np.mean(np.sign(np.sin(dphi))))
    wpli = abs(np.mean(S.imag)) / np.mean(np.abs(S.imag))
    return plv, pli, wpli

def coherence(x, y, band=(8, 12)):
    f, Sxy = csd(x, y, fs=fs, nperseg=fs * 2)
    _, Sxx = welch(x, fs=fs, nperseg=fs * 2); _, Syy = welch(y, fs=fs, nperseg=fs * 2)
    m = (f >= band[0]) & (f <= band[1])
    coh = Sxy[m] / np.sqrt(Sxx[m] * Syy[m])
    return abs(coh).mean(), abs(coh.imag).mean()

table = {}
for p, q in [("e1", "e2"), ("e1", "e3"), ("e2", "e3")]:
    plv, pli, wpli = metrics(an[p], an[q])
    ch, ich = coherence(e[p], e[q])
    null = [abs(np.mean(np.exp(1j * np.angle(an[p] * np.conj(np.roll(an[q], s))))))
            for s in rng.integers(fs * 5, t.size - fs * 5, 200)]
    table[p + "-" + q] = [plv, pli, wpli, ch, ich]
    print("%s-%s  PLV=%.2f (替代95%%=%.2f)  PLI=%.2f  wPLI=%.2f  |Coh|=%.2f  |ImCoh|=%.2f"
          % (p, q, plv, np.quantile(null, 0.95), pli, wpli, ch, ich))

import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(6.4, 4.2))
metric_names = ["PLV", "PLI", "wPLI", "|Coh|", "|ImCoh|"]
x = np.arange(len(metric_names))
for j, ((pair, v), hatch) in enumerate(zip(table.items(), ["", "//", ".."])):
    ax.bar(x + (j - 1) * 0.27, v, 0.27, hatch=hatch, label=pair, edgecolor="white")
ax.set_xticks(x, metric_names); ax.set_ylabel("value"); ax.set_ylim(0, 1.05); ax.legend()
ax.set_title("Zero-lag mixing (e1-e3) fools PLV/Coh, not PLI/wPLI/ImCoh", fontsize=10)
plt.tight_layout(); plt.show()
