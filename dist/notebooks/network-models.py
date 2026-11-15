# 依赖：networkx>=3, numpy, scipy, matplotlib
# 数据：WS、BA、ER、配置模型、随机几何图等网络均由 NetworkX 生成器或本文件中的简短模拟函数生成（固定随机种子以便复现）；
#       真实网络示例为《悲惨世界》人物共现网络（NetworkX 内置 les_miserables_graph()，此处按无权网络处理）。

# %% 示例：复现 Watts–Strogatz 的经典曲线
# 对一组重连概率 β（0.001 到 1，对数间隔），生成 WS 网络（N=300，K=10），
# 计算平均聚集系数 C(β) 与平均最短路径 L(β)，除以 β=0 时的值后画在对数横轴上。
# connected_watts_strogatz_graph 保证网络连通，才能计算平均最短路径。
# 输出：L(β)/L(0) 在 β≈0.01 附近已大幅下降，而 C(β)/C(0) 要到 β≈0.1 以后才明显下降，两者之间即小世界区间。
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

N, K = 300, 10
betas = np.logspace(-3, 0, 10)          # 0.001 ... 1

G0 = nx.watts_strogatz_graph(N, K, 0)
C0 = nx.average_clustering(G0)
L0 = nx.average_shortest_path_length(G0)
print("β=0（规则网格）: C(0)=%.3f（理论 3(K-2)/(4(K-1))=%.3f），L(0)=%.2f" % (C0, 3 * (K - 2) / (4 * (K - 1)), L0))

C_ratio, L_ratio = [], []
for b in betas:
    G = nx.connected_watts_strogatz_graph(N, K, b, seed=42)
    C_ratio.append(nx.average_clustering(G) / C0)
    L_ratio.append(nx.average_shortest_path_length(G) / L0)
    print("β=%.4f: C/C0=%.3f, L/L0=%.3f" % (b, C_ratio[-1], L_ratio[-1]))

plt.figure(figsize=(6, 4))
plt.semilogx(betas, C_ratio, "o-", label="C(β)/C(0)")
plt.semilogx(betas, L_ratio, "s-", label="L(β)/L(0)")
plt.xlabel("rewiring probability β")
plt.ylabel("normalized value")
plt.legend()
plt.title("Watts–Strogatz: N=%d, K=%d" % (N, K))
plt.show()


# %% 示例：BA 网络与 ER 网络的度分布（CCDF）
# 生成节点数和平均度相同的 BA 网络（n=3000，m=2）与 ER 网络，画两者度分布的互补累积分布 P(K ≥ k)。
# CCDF 不需要分箱，尾部比直方图平滑；幂律 P(k)~k^-γ 的 CCDF 斜率为 -(γ-1)。
# 输出：两者平均度相同，BA 的最大度远大于 ER；双对数坐标下 BA 的 CCDF 尾部近似直线（斜率约 -2），ER 很快“掉崖”。
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

n, m = 3000, 2
G_ba = nx.barabasi_albert_graph(n, m, seed=1)
avg_k = 2 * G_ba.number_of_edges() / n
G_er = nx.gnp_random_graph(n, avg_k / (n - 1), seed=1)


def ccdf(degrees):
    """返回 (k 值, P(K >= k))。"""
    degrees = np.asarray(degrees)
    ks = np.unique(degrees)
    p = np.array([(degrees >= k).mean() for k in ks])
    return ks, p


deg_ba = [d for _, d in G_ba.degree()]
deg_er = [d for _, d in G_er.degree()]
print("BA: 平均度 %.2f, 最大度 %d" % (np.mean(deg_ba), max(deg_ba)))
print("ER: 平均度 %.2f, 最大度 %d" % (np.mean(deg_er), max(deg_er)))

plt.figure(figsize=(6, 4))
for degs, lab, mk in [(deg_ba, "BA", "o"), (deg_er, "ER", "s")]:
    ks, p = ccdf(degs)
    plt.loglog(ks, p, mk, ms=3, label=lab)
plt.xlabel("k")
plt.ylabel("P(K ≥ k)")
plt.legend()
plt.title("CCDF of degree")
plt.show()


# %% 示例：用最大似然估计度指数，并与最小二乘比较
# 对 BA 网络（理论 γ=3）的度序列，用离散数据常用的最大似然近似
#     γ = 1 + n / Σ ln(k_i / (k_min - 0.5))      （只用 k_i >= k_min 的 n 个节点）
# 依次取 k_min = 2, 4, 6, 8；再与“直方图 + 双对数最小二乘”（不推荐的做法）比较。
# 输出：k_min 增大时 MLE 逐渐接近 3（BA 的度分布只在大 k 处才趋于 k^-3），但所用节点变少、方差变大；
#       最小二乘结果明显偏离 3，因为它被尾部大量“只出现一次”的大度值拉偏。
# Clauset 等（2009）选择使 KS 距离最小的 k_min 来权衡这种偏差与方差。
import networkx as nx
import numpy as np

G = nx.barabasi_albert_graph(3000, 2, seed=1)
k = np.array([d for _, d in G.degree()], dtype=float)


def gamma_mle(k, k_min):
    kk = k[k >= k_min]
    return 1 + len(kk) / np.sum(np.log(kk / (k_min - 0.5)))


for k_min in [2, 4, 6, 8]:
    print("k_min=%d: 使用 %4d 个节点, MLE γ = %.2f" % (k_min, (k >= k_min).sum(), gamma_mle(k, k_min)))

vals, counts = np.unique(k, return_counts=True)
pk = counts / counts.sum()
slope, intercept = np.polyfit(np.log(vals), np.log(pk), 1)
print("直方图最小二乘估计 γ = %.2f" % (-slope))

# 作图：左为直方图 + 最小二乘直线；右为 CCDF 与不同 k_min 的 MLE 拟合
import matplotlib.pyplot as plt

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
ax1.loglog(vals, pk, "o", ms=4, color="#4393c3", label="histogram P(k)")
ax1.loglog(vals, np.exp(intercept) * vals ** slope, "-", color="#d6604d", label="least squares: gamma = %.2f" % -slope)
ax1.set_xlabel("k"); ax1.set_ylabel("P(k)"); ax1.legend(fontsize=8)
ax1.set_title("Tail of single counts biases least squares", fontsize=10)
ks = np.sort(np.unique(k))
ccdf = np.array([(k >= x).mean() for x in ks])
ax2.loglog(ks, ccdf, "o", ms=4, color="0.4", label="CCDF P(K >= k)")
for k_min, ls in [(2, "--"), (8, "-")]:
    g = gamma_mle(k, k_min)
    xx = ks[ks >= k_min]
    ax2.loglog(xx, (k >= k_min).mean() * (xx / k_min) ** (1 - g), ls, lw=2, label="MLE k_min=%d: gamma = %.2f" % (k_min, g))
ax2.set_xlabel("k"); ax2.set_ylabel("P(K >= k)"); ax2.legend(fontsize=8)
ax2.set_title("BA network (theory gamma = 3)", fontsize=10)
plt.tight_layout(); plt.show()


# %% 示例：判断一个真实网络是否“小世界”
# 以《悲惨世界》人物共现网络为例，计算 C 和 L，再与两种零模型比较，求小世界系数 σ = (C/C_rand)/(L/L_rand)：
#   (a) 同节点数、同边数的 ER 网络；(b) 用双边交换（约 10×E 次）保持度序列的随机化网络。
# 每种零模型取 5 个随机种子平均，并只在最大连通分支上计算 L。
# 输出：两种参照下 σ 都明显大于 1；保度随机化网络的 C_rand 比 ER 更高，因此 σ 更小、判断更严格。
import networkx as nx
import numpy as np

G = nx.Graph(nx.les_miserables_graph())      # 按无权图处理
n, e = G.number_of_nodes(), G.number_of_edges()
C = nx.average_clustering(G)
L = nx.average_shortest_path_length(G)
print("原网络: N=%d, E=%d, C=%.3f, L=%.3f" % (n, e, C, L))


def er_reference(seed):
    R = nx.gnm_random_graph(n, e, seed=seed)
    R = R.subgraph(max(nx.connected_components(R), key=len)).copy()
    return nx.average_clustering(R), nx.average_shortest_path_length(R)


def degree_preserving_reference(seed):
    R = G.copy()
    nx.double_edge_swap(R, nswap=10 * e, max_tries=100 * e, seed=seed)
    R = R.subgraph(max(nx.connected_components(R), key=len)).copy()
    return nx.average_clustering(R), nx.average_shortest_path_length(R)


Cr, Lr = np.mean([er_reference(s) for s in range(5)], axis=0)
print("ER 参照:   C_rand=%.3f, L_rand=%.3f, σ=%.2f" % (Cr, Lr, (C / Cr) / (L / Lr)))
Cd, Ld = np.mean([degree_preserving_reference(s) for s in range(5)], axis=0)
print("保度参照:  C_rand=%.3f, L_rand=%.3f, σ=%.2f" % (Cd, Ld, (C / Cd) / (L / Ld)))

# 作图：原网络与两种零模型的 C、L 对比，标题给出 σ
import matplotlib.pyplot as plt

labels = ["Les Miserables", "ER reference", "degree-preserving"]
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
for ax, v, lab in [(ax1, [C, Cr, Cd], "average clustering C"), (ax2, [L, Lr, Ld], "average path length L")]:
    ax.bar(labels, v, color=["#d6604d", "#92c5de", "#4393c3"], width=0.6)
    for i, x in enumerate(v):
        ax.text(i, x * 1.02, "%.3f" % x, ha="center", fontsize=9)
    ax.set_ylabel(lab)
ax1.set_title("sigma = %.2f (ER), %.2f (degree-preserving)" % ((C / Cr) / (L / Lr), (C / Cd) / (L / Ld)), fontsize=10)
ax2.set_title("Path lengths are comparable", fontsize=10)
plt.tight_layout(); plt.show()


# %% 示例：配置模型——从给定度序列生成随机网络
# 先从离散幂律（γ=2.5，k_min=2）抽取 N=5000 个节点的度序列，再用 nx.configuration_model 随机配对“半边”。
# 检查三件事：(1) 配对产生的自环与重边数目（集中在枢纽上）；(2) 化为简单图后度序列的改变；
# (3) Molloy–Reed 判据 <k^2> - 2<k> > 0 与巨连通分支的大小；并验证“朋友悖论”：随机一条边末端的平均度 <k^2>/<k> 远大于 <k>。
# 输出：自环与重边共有数百条且集中在枢纽，删除后最大度明显下降；判据为正，巨分支覆盖几乎全部节点；
#       由于 k_max 超过结构截断，C 的近似公式只给出数量级。
import networkx as nx
import numpy as np

rng = np.random.default_rng(0)
N, gamma, kmin = 5000, 2.5, 2
# 用连续幂律的逆变换抽样后向下取整，得到近似离散幂律的度序列
u = rng.random(N)
deg = np.floor(kmin * (1 - u) ** (-1 / (gamma - 1))).astype(int)
if deg.sum() % 2 == 1:          # 半边总数必须为偶数
    deg[0] += 1
print("度序列: N=%d, <k>=%.2f, k_max=%d, 自然截断估计 k_min*N^(1/(γ-1))=%.0f"
      % (N, deg.mean(), deg.max(), kmin * N ** (1 / (gamma - 1))))

M = nx.configuration_model(deg.tolist(), seed=1)          # MultiGraph，允许自环与重边
n_self = nx.number_of_selfloops(M)
n_multi = M.number_of_edges() - nx.Graph(M).number_of_edges()
print("配对后: 自环 %d 条, 重边（多余的平行边）%d 条" % (n_self, n_multi))

G = nx.Graph(M)                                           # 合并重边
G.remove_edges_from(nx.selfloop_edges(G))                 # 删除自环
deg_simple = np.array([d for _, d in G.degree()])
print("化为简单图后: <k>=%.2f, k_max=%d（原为 %d）" % (deg_simple.mean(), deg_simple.max(), deg.max()))

k1, k2 = deg.mean(), (deg.astype(float) ** 2).mean()
print("Molloy–Reed: <k^2>-2<k> = %.1f  (>0 则存在巨连通分支)" % (k2 - 2 * k1))
giant = max(nx.connected_components(G), key=len)
print("巨连通分支占比 = %.3f" % (len(giant) / N))
print("朋友悖论: 节点平均度 <k>=%.2f, 边末端平均度 <k^2>/<k>=%.2f" % (k1, k2 / k1))
C_theory = (k2 - k1) ** 2 / (k1 ** 3 * N)
print("聚集系数: 模拟 C=%.4f, 配置模型近似 (<k^2>-<k>)^2/(<k>^3 N)=%.4f" % (nx.transitivity(G), C_theory))
print("结构截断 sqrt(<k>N)=%.0f：k_max 超过它时，枢纽之间会被迫出现重边，删重边后近似公式高估 C" % np.sqrt(k1 * N))

# 作图：配对前后度分布的 CCDF，竖线为结构截断与自然截断
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(6.4, 4.2))
for d, mk, lab in [(deg, "o", "target sequence (multigraph)"), (deg_simple, "s", "after removing loops/multi-edges")]:
    xs = np.sort(np.unique(d))
    ax.loglog(xs, [(d >= x).mean() for x in xs], mk, ms=3.5, alpha=0.8, label=lab)
xs = np.logspace(np.log10(kmin), np.log10(deg.max()), 50)
ax.loglog(xs, (xs / kmin) ** (1 - gamma), "--", color="0.4", label="slope -(gamma-1) = %.1f" % (1 - gamma))
ax.axvline(np.sqrt(k1 * N), color="#d6604d", ls=":", label="structural cutoff sqrt(<k>N)")
ax.axvline(kmin * N ** (1 / (gamma - 1)), color="0.6", ls="-.", label="natural cutoff")
ax.set_xlabel("degree k"); ax.set_ylabel("P(K >= k)"); ax.legend(fontsize=7)
ax.set_title("Simplifying the graph trims the hubs (%d self-loops, %d multi-edges)" % (n_self, n_multi), fontsize=10)
plt.tight_layout(); plt.show()


# %% 示例：非线性优先连接 Π(k) ∝ k^α 与“测量”优先连接
# 用同一个生长过程（每步加入 1 个节点、带 m=2 条边）分别取 α=0.5、1、1.5，比较最大度与 CCDF 尾部：
# 亚线性时枢纽受限（拉伸指数），超线性时出现“赢家通吃”的超级枢纽。
# 然后按 Jeong、Néda、Barabási（2003）的思路测量 Π(k)：记录 t0 时各节点的度，统计此后 Δt 内各度类获得新边的数目，
# 得到累积函数 π(k)=Σ_{k'<k}Π(k')，在双对数下拟合斜率 ≈ α+1。
# 输出：k_max 依次约为 40、170、近 5000（α=1.5 时一个节点连到了绝大多数新节点）；
#       由 π(k) 估计的 α 依次接近 0.5、1、1.5，超线性时因度类稀疏而低估。
import numpy as np


def grow(n, m, alpha, seed=0, record_at=None):
    """非线性优先连接生长；返回最终度数组，以及（可选）在 record_at 时刻之后各节点按初始度统计的新增边数。"""
    rng = np.random.default_rng(seed)
    deg = np.zeros(n)
    deg[: m + 1] = m                       # 初始：m+1 个节点的完全图
    k_at_t0, gained = None, None
    for t in range(m + 1, n):
        if record_at is not None and t == record_at:
            k_at_t0 = deg[:t].copy()
            gained = np.zeros(t)
        w = deg[:t] ** alpha
        targets = rng.choice(t, size=m, replace=False, p=w / w.sum())
        deg[targets] += 1
        deg[t] = m
        if gained is not None:
            gained[targets[targets < len(gained)]] += 1
    return deg, k_at_t0, gained


n, m = 6000, 2
results = []                                # 存下结果用于作图
for alpha in [0.5, 1.0, 1.5]:
    deg, k0, g = grow(n, m, alpha, seed=1, record_at=4000)
    # 测量：度为 k 的节点在 Δt 内平均获得的新边数 ∝ Π(k)
    ks = np.unique(k0)
    Pi = np.array([g[k0 == k].mean() for k in ks])
    cum = np.cumsum(Pi)                     # π(k) 的离散近似
    sel = (ks >= 3) & (ks <= np.percentile(k0, 99))
    slope = np.polyfit(np.log(ks[sel]), np.log(cum[sel]), 1)[0]
    print("α=%.1f: k_max=%5d, 最大节点占全部边端点的比例=%.3f, 由 π(k) 斜率估计 α≈%.2f"
          % (alpha, deg.max(), deg.max() / deg.sum(), slope - 1))
    results.append((alpha, deg, ks[sel], cum[sel], slope))

# 作图：左为三种 α 的度分布 CCDF；右为测得的累积优先连接函数 π(k) 及其斜率
import matplotlib.pyplot as plt

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
for (alpha, deg, kk, cc, sl), mk in zip(results, ["o", "s", "^"]):
    xs = np.sort(np.unique(deg))
    ax1.loglog(xs, [(deg >= x).mean() for x in xs], mk + "-", ms=3, lw=0.8, label="alpha = %.1f (k_max = %d)" % (alpha, deg.max()))
    ax2.loglog(kk, cc, mk, ms=4, label="alpha = %.1f: slope - 1 = %.2f" % (alpha, sl - 1))
ax1.set_xlabel("degree k"); ax1.set_ylabel("P(K >= k)"); ax1.legend(fontsize=8)
ax1.set_title("Superlinear attachment creates a super-hub", fontsize=10)
ax2.set_xlabel("degree at t0, k"); ax2.set_ylabel("cumulative pi(k)"); ax2.legend(fontsize=8)
ax2.set_title("Measured pi(k) ~ k^(alpha+1)", fontsize=10)
plt.tight_layout(); plt.show()


# %% 示例：Bianconi–Barabási 适应度模型——后来者居上
# 每个节点带适应度 η（均匀分布于 [0,1]），新节点连向 i 的概率 ∝ η_i k_i。
# 模拟 N=20000、m=2 的网络；在 t=1000 时人为插入一个 η=1 的“后来者”，追踪它与最早一批节点的度。
# 再按适应度分组，用 ln k_i 对 ln(t/t_i) 回归估计动态指数 β(η)，与理论 β(η)=η/C*（均匀分布 C*≈1.255）比较。
# 输出：t=1000 才加入的高适应度节点，度数很快超过最早的节点；β(η) 随 η 近似线性增长，
#       数值比理论 η/1.255 低约 5–10%（有限时间与初始度的影响），但线性关系清楚。
import numpy as np

rng = np.random.default_rng(3)
N, m, t_late = 20000, 2, 1000
eta = rng.random(N)
eta[t_late] = 1.0
deg = np.zeros(N)
deg[: m + 1] = m
track = {0: [], 1: [], t_late: []}
for t in range(m + 1, N):
    w = eta[:t] * deg[:t]
    targets = rng.choice(t, size=m, replace=False, p=w / w.sum())
    deg[targets] += 1
    deg[t] = m
    if t % 200 == 0:                                # 记录轨迹用于作图
        for i in track:
            track[i].append((t, deg[i]))
    if t % 4000 == 0 or t == N - 1:
        print("t=%5d: 节点0(η=%.2f) k=%4d, 节点1(η=%.2f) k=%4d, 后来者(η=1, t_i=%d) k=%4d"
              % (t, eta[0], deg[0], eta[1], deg[1], t_late, deg[t_late]))

# 估计 β(η)：对每个适应度区间，回归 ln(k_i/m) ~ β ln(N/t_i)，只用 t_i 足够早的节点
ti = np.arange(N)
ok = (ti > 10) & (ti < N // 5)
betas = []
for lo in np.arange(0.2, 1.0, 0.2):
    sel = ok & (eta >= lo) & (eta < lo + 0.2)
    x, y = np.log(N / ti[sel]), np.log(deg[sel] / m)
    beta = (x * y).sum() / (x * x).sum()            # 过原点回归
    print("η∈[%.1f,%.1f): β 估计=%.3f, 理论 η_mid/1.255=%.3f" % (lo, lo + 0.2, beta, (lo + 0.1) / 1.255))
    betas.append((lo + 0.1, beta))

# 作图：左为度随时间的增长轨迹（双对数）；右为 β(η) 与理论直线
import matplotlib.pyplot as plt

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
for i, ls, lab in [(0, "-", "node 0 (eta = %.2f)" % eta[0]), (1, "--", "node 1 (eta = %.2f)" % eta[1]),
                   (t_late, "-", "latecomer t_i = %d (eta = 1)" % t_late)]:
    tt, kk = zip(*[(t, k) for t, k in track[i] if t > i])
    ax1.loglog(tt, kk, ls, lw=2, label=lab)
ax1.set_xlabel("time t"); ax1.set_ylabel("degree k_i(t)"); ax1.legend(fontsize=8)
ax1.set_title("The fittest latecomer overtakes early nodes", fontsize=10)
em, bt = zip(*betas)
ax2.plot(em, bt, "o", ms=8, label="estimated beta")
ax2.plot([0, 1], [0, 1 / 1.255], "--", color="0.4", label="theory eta / 1.255")
ax2.set_xlabel("fitness eta (bin centre)"); ax2.set_ylabel("dynamic exponent beta"); ax2.legend(fontsize=8)
ax2.set_title("beta grows linearly with fitness", fontsize=10)
plt.tight_layout(); plt.show()


# %% 示例：复制–分化（duplication–divergence）模型与蛋白质网络的长尾
# 每一步随机选一个已有“基因” i 复制出 i'：i' 以概率 q 保留 i 的每条相互作用（分化 = 以 1-q 丢失），
# 并以概率 p 与 i 直接相连（同源二聚体）。为避免产生孤立节点，若 i' 一条边都没保留就重新抽样（与多数文献的做法一致）。
# 比较 q=0.3、0.5、0.7：平均度随网络规模的变化（均场预期 q>1/2 时持续增长）、最大度与聚集系数，
# 并用 MLE（k_min=5）给出尾部指数的粗略估计。
# 输出：q=0.3 时平均度几乎不随 N 变化；q≥0.5 时平均度随 N 增长（q=0.7 时网络迅速变稠密、尾部变平）；
#       三种 q 下都出现度为数百的枢纽，聚集系数比同规模 ER 网络高一到两个数量级。
import networkx as nx
import numpy as np


def duplication_divergence(n, q, p, seed=0):
    rng = np.random.default_rng(seed)
    G = nx.Graph([(0, 1)])
    while G.number_of_nodes() < n:
        new = G.number_of_nodes()
        while True:
            i = int(rng.integers(new))
            kept = [j for j in G.neighbors(i) if rng.random() < q]
            if kept:
                break
        G.add_edges_from((new, j) for j in kept)
        if rng.random() < p:
            G.add_edge(new, i)
    return G


kbar, degs = {}, {}                                 # 存下结果用于作图
for q in [0.3, 0.5, 0.7]:
    out = []
    for n in [1000, 4000]:
        G = duplication_divergence(n, q, p=0.1, seed=7)
        out.append(2 * G.number_of_edges() / n)
    k = np.array([d for _, d in G.degree()], float)
    kmin = 5
    tail = k[k >= kmin]
    gam = 1 + len(tail) / np.sum(np.log(tail / (kmin - 0.5))) if len(tail) > 20 else float("nan")
    er = nx.gnm_random_graph(G.number_of_nodes(), G.number_of_edges(), seed=1)
    print("q=%.1f: <k>(N=1000)=%.2f, <k>(N=4000)=%.2f, k_max=%d, C=%.3f（ER: %.4f）, 尾部 γ≈%.2f"
          % (q, out[0], out[1], k.max(), nx.average_clustering(G), nx.average_clustering(er), gam))
    kbar[q], degs[q] = out, k

# 作图：左为平均度随规模的变化；右为 N=4000 时的度分布 CCDF
import matplotlib.pyplot as plt

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
for (q, kb), mk in zip(kbar.items(), ["o", "s", "^"]):
    ax1.plot([1000, 4000], kb, mk + "-", label="q = %.1f" % q)
    xs = np.sort(np.unique(degs[q]))
    ax2.loglog(xs, [(degs[q] >= x).mean() for x in xs], mk, ms=3, label="q = %.1f" % q)
ax1.set_xlabel("network size N"); ax1.set_ylabel("average degree <k>"); ax1.legend(fontsize=8)
ax1.set_title("<k> grows with N when q >= 1/2", fontsize=10)
ax2.set_xlabel("degree k"); ax2.set_ylabel("P(K >= k)"); ax2.legend(fontsize=8)
ax2.set_title("Long-tailed degree distributions (N = 4000)", fontsize=10)
plt.tight_layout(); plt.show()


# %% 示例：随机几何图——空间嵌入带来的高聚类与“大世界”
# 在单位正方形中随机撒 N 个点，距离小于 r 的点对相连；r 取使期望平均度约为 10 的值（忽略边界效应 <k>≈Nπr²）。
# 与同节点数、同边数的 ER 网络比较聚集系数与平均路径；二维随机几何图的聚集系数理论值为 1-3√3/(4π)≈0.587（Dall 与 Christensen 2002）。
# 再加入少量随机“长程连接”（每节点平均 0.05 条），观察路径长度骤降而聚集几乎不变——空间版的小世界机制。
# 输出：RGG 的 C≈0.60–0.62，略高于理论值（边界附近节点的邻域被截断）；N 增大 4 倍时 L 约增大 2 倍（按 √N 增长），
#       ER 的 C 很小、L 按 ln N 缓慢增长；加入约 100 条长程边后 L 降到原来的一半以下，C 几乎不变。
import networkx as nx
import numpy as np

for N in [500, 2000]:
    r = np.sqrt(10 / (np.pi * N))
    G = nx.random_geometric_graph(N, r, seed=2)
    G = G.subgraph(max(nx.connected_components(G), key=len)).copy()
    E = nx.gnm_random_graph(G.number_of_nodes(), G.number_of_edges(), seed=2)
    E = E.subgraph(max(nx.connected_components(E), key=len)).copy()
    print("N=%4d: RGG <k>=%.1f, C=%.3f, L=%.1f | ER C=%.4f, L=%.2f"
          % (N, 2 * G.number_of_edges() / G.number_of_nodes(), nx.average_clustering(G),
             nx.average_shortest_path_length(G), nx.average_clustering(E), nx.average_shortest_path_length(E)))

print("理论值 1-3√3/(4π) = %.3f" % (1 - 3 * np.sqrt(3) / (4 * np.pi)))

rng = np.random.default_rng(5)
nodes = list(G.nodes())
H = G.copy()
for _ in range(int(0.05 * len(nodes))):
    a, b = rng.choice(nodes, 2, replace=False)
    H.add_edge(a, b)
print("加入 %d 条长程边后: C=%.3f, L=%.2f" % (int(0.05 * len(nodes)), nx.average_clustering(H),
                                          nx.average_shortest_path_length(H)))

# 作图：左为空间嵌入的网络（红线 = 新加的长程边）；右为加边前后的 C 与 L
import matplotlib.pyplot as plt

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.2), gridspec_kw={"width_ratios": [1.1, 1]})
pos = nx.get_node_attributes(G, "pos")
nx.draw_networkx_edges(G, pos, ax=ax1, edge_color="0.7", alpha=0.4, width=0.4)
nx.draw_networkx_edges(H, pos, ax=ax1, edgelist=[e for e in H.edges() if not G.has_edge(*e)], edge_color="#d6604d", width=1)
nx.draw_networkx_nodes(G, pos, ax=ax1, node_size=4, node_color="#4393c3")
ax1.set_title("RGG (N = %d) + %d shortcuts" % (N, H.number_of_edges() - G.number_of_edges()), fontsize=10)
ax1.set_aspect("equal"); ax1.axis("off")
vals = [(nx.average_clustering(G), nx.average_shortest_path_length(G)), (nx.average_clustering(H), nx.average_shortest_path_length(H))]
for j, (lab, col) in enumerate([("clustering C", "#92c5de"), ("path length L", "#d6604d")]):
    bars = ax2.bar(np.arange(2) + (j - 0.5) * 0.36, [v[j] / vals[0][j] for v in vals], 0.36, color=col, label=lab)
    for bar, v in zip(bars, vals):
        ax2.text(bar.get_x() + 0.18, bar.get_height() + 0.02, "%.3g" % v[j], ha="center", fontsize=9)
ax2.set_xticks([0, 1]); ax2.set_xticklabels(["RGG", "RGG + shortcuts"])
ax2.set_ylabel("value relative to RGG"); ax2.set_ylim(0, 1.2); ax2.legend(fontsize=8)
ax2.set_title("Shortcuts halve L, C barely changes", fontsize=10)
plt.tight_layout(); plt.show()


# %% 示例：初始吸引力与内部连边如何改变度指数
# 用平均场结论检验三种 BA 变体（每步新节点带 m=2 条边，最终 N=30000）：
#   (a) 初始吸引力 Π ∝ k + A，A=2：  理论 γ = 3 + A/m = 4
#   (b) 每步另加 n=2 条“双优先”内部边（两端都按度选择）：理论 γ = 2 + m/(m+2n) ≈ 2.33
#   (c) 每步另加 n=2 条两端随机的内部边：理论 γ = 3 + 2n/m = 5
# 用 MLE（离散近似，k_min=20）估计 γ。平均场解的度分布其实是“平移幂律” P(k) ∝ (k+s)^-γ，
# 直接对 k 拟合会低估 γ，对 k+s 拟合则接近理论值——这也说明有限数据上“读出的指数”依赖于拟合形式。为了高效，用“边端点列表”抽样实现按度成比例的选择。
# 输出：直接 MLE 的排序与理论一致（b < BA < a < c）但 a、c 明显偏低；平移后的估计更接近理论值。
import numpy as np


def simulate(N, m, A=0.0, n_int=0, internal="none", seed=0):
    rng = np.random.default_rng(seed)
    deg = np.zeros(N, dtype=np.int64)
    ends = []                                  # 每条边的两个端点都记一次：均匀抽一个元素 = 按度抽节点
    for i in range(m + 1):
        for j in range(i + 1, m + 1):
            ends += [i, j]
            deg[i] += 1; deg[j] += 1
    for t in range(m + 1, N):
        for _ in range(m):
            # 以概率 (Σk)/(Σk + A t) 按度选，否则均匀选：合起来即 Π ∝ k + A
            if A > 0 and rng.random() < A * t / (len(ends) + A * t):
                v = int(rng.integers(t))
            else:
                v = ends[rng.integers(len(ends))]
            deg[v] += 1; ends.append(v)
        deg[t] += m; ends += [t] * m
        for _ in range(n_int):
            if internal == "pref":
                a, b = ends[rng.integers(len(ends))], ends[rng.integers(len(ends))]
            else:
                a, b = rng.integers(t + 1), rng.integers(t + 1)
            deg[a] += 1; deg[b] += 1; ends += [int(a), int(b)]
    return deg


def gamma_mle(k, kmin, shift=0.0):
    """离散近似 MLE；shift>0 时对平移变量 k+shift 拟合，对应 P(k) ∝ (k+shift)^-γ。"""
    kk = k[k >= kmin].astype(float) + shift
    return 1 + len(kk) / np.sum(np.log(kk / (kmin + shift - 0.5)))


N, m = 30000, 2
n = 2
# 平均场给出的平移量：Π∝k+A 时 k_i+A ∝ t^β；随机内部边时 k_i + 4n(m+n)/m ∝ t^β
cases = [("BA", dict(), 3.0, 0.0),
         ("初始吸引力 A=2", dict(A=2.0), 3 + 2 / m, 2.0),
         ("双优先内部边 n=2", dict(n_int=n, internal="pref"), 2 + m / (m + 2 * n), 0.0),
         ("随机内部边 n=2", dict(n_int=n, internal="rand"), 3 + 2 * n / m, 4 * n * (m + n) / m)]
kmin = 20
sims = []                                      # 存下结果用于作图
for name, kw, theory, s in cases:
    k = simulate(N, m, seed=11, **kw)
    sims.append((k, theory, gamma_mle(k, kmin), gamma_mle(k, kmin, s)))
    print("%-12s 理论 γ=%.2f | 直接 MLE γ=%.2f | 平移 s=%g 后 MLE γ=%.2f | k_max=%d"
          % (name, theory, gamma_mle(k, kmin), s, gamma_mle(k, kmin, s), k.max()))

# 作图：左为四种变体的度分布 CCDF；右为理论 γ 与两种 MLE 估计的对比
import matplotlib.pyplot as plt

names_en = ["BA", "initial attractiveness A=2", "preferential internal n=2", "random internal n=2"]
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
for (k, th, g0, g1), lab, mk in zip(sims, names_en, ["o", "s", "^", "D"]):
    xs = np.sort(np.unique(k))
    ax1.loglog(xs, [(k >= x).mean() for x in xs], mk, ms=2.5, label=lab)
ax1.axvline(kmin, color="0.6", ls=":")
ax1.set_xlabel("degree k"); ax1.set_ylabel("P(K >= k)"); ax1.legend(fontsize=7)
ax1.set_title("Degree distributions (N = %d)" % N, fontsize=10)
x = np.arange(len(sims))
for j, (lab, col) in enumerate([("theory", "0.3"), ("MLE on k", "#92c5de"), ("MLE on k + s", "#4393c3")]):
    ax2.bar(x + (j - 1) * 0.26, [r[j + 1] for r in sims], 0.26, color=col, label=lab)
ax2.set_xticks(x); ax2.set_xticklabels(["BA", "A=2", "pref.", "random"])
ax2.set_ylabel("degree exponent gamma"); ax2.legend(fontsize=8)
ax2.set_title("Shifted fit recovers mean-field exponents", fontsize=10)
plt.tight_layout(); plt.show()
