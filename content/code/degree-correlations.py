# 依赖：networkx>=3, numpy, scipy, matplotlib
# 数据：全部为 networkx/numpy 生成的模型网络或模拟数据，仅用于演示方法，
#   不代表真实蛋白质相互作用网络、真实连接组或真实调控网络。
#   - 换成自己的数据时：无向网络读成 networkx.Graph（例如 nx.read_edgelist("ppi.tsv")），
#     先去掉自环、合并重边，并说明是否只保留最大连通分支。
#   - 有向网络（如转录调控网络）读成 networkx.DiGraph，度相关要分 in/out 组合计算。
# 每个“# %% 示例”单元可以单独运行，单元之间不共享变量。

# %% 示例：按定义手算度相关系数 r 与 k_nn(k)，并与 NetworkX 对照
# 用三个小网络（星形图、完全二部图之外加一条边、两个大小不同的完全图）演示：
#   r 是“同一条边两端度”的 Pearson 相关；每条无向边要按两个方向各计一次。
#   k_nn(k) 是度为 k 的节点的邻居平均度。
# 解读：星形图是最极端的异配（r = -1）；由两个不同大小团组成的网络中，每个节点只连同度节点，r = 1。
import numpy as np
import networkx as nx


def r_by_definition(G):
    """对每条边取 (k_u, k_v) 与 (k_v, k_u) 两个有序对，计算 Pearson 相关。"""
    deg = dict(G.degree())
    x, y = [], []
    for u, v in G.edges():
        x += [deg[u], deg[v]]
        y += [deg[v], deg[u]]
    x, y = np.array(x, float), np.array(y, float)
    if x.std() == 0:
        return float("nan")          # 正则图：所有边两端度相同，相关系数无定义
    return float(np.corrcoef(x, y)[0, 1])


def knn_by_definition(G):
    deg = dict(G.degree())
    knn_i = {i: np.mean([deg[j] for j in G[i]]) for i in G if deg[i] > 0}
    out = {}
    for k in sorted(set(deg.values()) - {0}):
        out[k] = np.mean([knn_i[i] for i in knn_i if deg[i] == k])
    return out


cases = {
    "星形图 (1 个中心 + 6 个叶子)": nx.star_graph(6),
    "两个团 K3 与 K5（不相连）": nx.disjoint_union(nx.complete_graph(3), nx.complete_graph(5)),
    "Zachary 空手道俱乐部": nx.karate_club_graph(),
}
for name, G in cases.items():
    r_def = r_by_definition(G)
    r_nx = nx.degree_assortativity_coefficient(G)
    knn = knn_by_definition(G)
    knn_nx = nx.average_degree_connectivity(G)       # NetworkX 中 k_nn(k) 的函数名
    same = all(abs(knn[k] - knn_nx[k]) < 1e-12 for k in knn)
    print(f"{name}: r(定义) = {r_def:.4f}, r(NetworkX) = {r_nx:.4f}, k_nn(k) 与 NetworkX 一致: {same}")
    print("   k_nn(k):", {k: round(float(v), 2) for k, v in knn.items()})

# 中性网络的预测：k_nn = <k^2>/<k>，与 k 无关（也就是“朋友比你朋友多”的来源）
G = nx.gnm_random_graph(3000, 15000, seed=1)
k = np.array([d for _, d in G.degree()], float)
print(f"\nER 随机图：<k> = {k.mean():.2f}, <k^2>/<k> = {(k**2).mean()/k.mean():.2f}, "
      f"所有节点的邻居平均度的均值 = {np.mean(list(nx.average_neighbor_degree(G).values())):.2f}")

# 作图：空手道网络按度着色，以及它的 k_nn(k) 与中性预测 <k^2>/<k>
import matplotlib.pyplot as plt
K = nx.karate_club_graph()
kk = np.array([d for _, d in K.degree()], float)
knn_k = knn_by_definition(K)
fig, ax = plt.subplots(1, 2, figsize=(10, 4))
pos = nx.spring_layout(K, seed=2)
nx.draw_networkx_edges(K, pos, ax=ax[0], edge_color="0.6", alpha=0.4)
sc = nx.draw_networkx_nodes(K, pos, ax=ax[0], node_size=[30 + 8 * d for d in kk], node_color=kk, cmap="viridis")
fig.colorbar(sc, ax=ax[0], label="degree k"); ax[0].axis("off")
ax[0].set_title(f"Karate club, r = {nx.degree_assortativity_coefficient(K):+.2f}")
ax[1].plot(list(knn_k), list(knn_k.values()), "o-", label="k_nn(k)")
ax[1].axhline((kk**2).mean() / kk.mean(), color="gray", ls="--", label="neutral <k^2>/<k>")
ax[1].set_xlabel("degree k"); ax[1].set_ylabel("mean neighbor degree k_nn(k)")
ax[1].set_title("Hubs attach to low-degree nodes (disassortative)"); ax[1].legend()
plt.tight_layout(); plt.show()

# %% 示例：k_nn(k)、相关指数 mu、r 与 Spearman rho——三类网络对照
# 从同一个度序列（BA 模型，N=3000, m=2）出发，用 Xulvi-Brunet–Sokolov 重连得到同配版与异配版。
# 重连只交换边的端点，所以三张网络的度序列完全相同，差别只在“谁连谁”。
# 对每张网络：对数分箱计算 k_nn(k)，在双对数坐标下拟合 k_nn ~ k^mu；同时报告 r 与边两端度的 Spearman rho。
# 解读：mu、r、rho 的符号一致；同配版在高 k 处 k_nn 走平甚至下降，这是结构截断的痕迹。
import numpy as np
import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import spearmanr

plt.rcParams["font.sans-serif"] = ["PingFang SC", "Microsoft YaHei", "SimHei", "Noto Sans CJK SC", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


def xbs_rewire(G, n_swaps, mode, p=1.0, seed=0):
    """Xulvi-Brunet & Sokolov 重连：随机取两条边，把四个端点按度排序后，
    以概率 p 按 mode 确定性配对（assortative: 大配大、小配小；disassortative: 大配小），
    以概率 1-p 随机配对。拒绝产生自环或重边的交换，因此保持简单图与度序列。"""
    rng = np.random.default_rng(seed)
    G = G.copy()
    deg = dict(G.degree())
    edges = list(G.edges())
    done = 0
    while done < n_swaps:
        i, j = rng.choice(len(edges), 2, replace=False)
        (a, b), (c, d) = edges[i], edges[j]
        nodes = [a, b, c, d]
        if len(set(nodes)) < 4:
            continue
        if rng.random() < p:
            s = sorted(nodes, key=lambda x: deg[x], reverse=True)
            new = [(s[0], s[1]), (s[2], s[3])] if mode == "assortative" else [(s[0], s[3]), (s[1], s[2])]
        else:
            rng.shuffle(nodes)
            new = [(nodes[0], nodes[1]), (nodes[2], nodes[3])]
        if any(G.has_edge(*e) for e in new):
            continue
        G.remove_edges_from([(a, b), (c, d)])
        G.add_edges_from(new)
        edges[i], edges[j] = new
        done += 1
    return G


def knn_logbinned(G, n_bins=12):
    deg = dict(G.degree())
    knn_i = nx.average_neighbor_degree(G)
    k = np.array([deg[i] for i in G], float)
    kn = np.array([knn_i[i] for i in G], float)
    bins = np.unique(np.round(np.logspace(0, np.log10(k.max() + 1), n_bins)))
    kc, kv = [], []
    for lo, hi in zip(bins[:-1], bins[1:]):
        sel = (k >= lo) & (k < hi)
        if sel.sum() >= 3:
            kc.append(k[sel].mean())
            kv.append(kn[sel].mean())
    return np.array(kc), np.array(kv)


def edge_spearman(G):
    deg = dict(G.degree())
    x = [deg[u] for u, v in G.edges()] + [deg[v] for u, v in G.edges()]
    y = [deg[v] for u, v in G.edges()] + [deg[u] for u, v in G.edges()]
    return spearmanr(x, y)[0]


G0 = nx.barabasi_albert_graph(3000, 2, seed=3)
M = G0.number_of_edges()
nets = {
    "BA 原始": G0,
    "同配重连": xbs_rewire(G0, 3 * M, "assortative", p=1.0, seed=1),
    "异配重连": xbs_rewire(G0, 3 * M, "disassortative", p=1.0, seed=2),
}
fig, ax = plt.subplots(figsize=(5, 4))
for name, G in nets.items():
    assert sorted(d for _, d in G.degree()) == sorted(d for _, d in G0.degree())
    kc, kv = knn_logbinned(G)
    mu = np.polyfit(np.log(kc), np.log(kv), 1)[0]
    r = nx.degree_assortativity_coefficient(G)
    rho = edge_spearman(G)
    print(f"{name}: r = {r:+.3f}   Spearman rho = {rho:+.3f}   拟合 mu = {mu:+.2f}")
    ax.loglog(kc, kv, "o-", label=f"{name} (r={r:+.2f})")
k = np.array([d for _, d in G0.degree()], float)
ax.axhline((k**2).mean() / k.mean(), color="gray", ls="--", label="中性预测 <k²>/<k>")
ax.set_xlabel("度 k")
ax.set_ylabel("k_nn(k)")
ax.legend(fontsize=8)
fig.tight_layout()
fig.savefig("knn_three_networks.png", dpi=120)
print("图已保存为 knn_three_networks.png")

# %% 示例：结构截断与“伪异配”——简单图约束本身就会产生负的 r
# 用配置模型生成幂律度序列（gamma=2.2，N=5000）。允许重边与自环时（多重图），网络在期望上是中性的；
# 把重边合并、自环删除得到简单图后，r 变为负值。
# 同时比较结构截断 k_s ~ sqrt(<k> N) 与最大度 k_max：k_max 远大于 k_s 时，枢纽之间“应有”的多条边
# 只能保留一条，枢纽被迫连向低度节点。
# 解读：重尾度分布的简单图出现负 r，不能直接当作“生物学上的枢纽回避”。
import numpy as np
import networkx as nx

rng = np.random.default_rng(7)
N, gamma, kmin = 5000, 2.2, 2
# 从离散幂律 p_k ~ k^(-gamma)（k >= kmin）抽样，用连续分布逆变换后取整
u = rng.random(N)
deg = np.floor(kmin * (1 - u) ** (-1 / (gamma - 1))).astype(int)
deg = np.minimum(deg, N - 1)
if deg.sum() % 2:
    deg[0] += 1

Gm = nx.configuration_model(deg.tolist(), seed=11)          # MultiGraph，含重边与自环
r_multi = nx.degree_assortativity_coefficient(Gm)
n_multi = Gm.number_of_edges() - nx.Graph(Gm).number_of_edges()
n_loops = nx.number_of_selfloops(Gm)

Gs = nx.Graph(Gm)                                           # 合并重边
Gs.remove_edges_from(nx.selfloop_edges(Gs))                 # 删除自环
r_simple = nx.degree_assortativity_coefficient(Gs)

k_mean = deg.mean()
k_s = np.sqrt(k_mean * N)
print(f"N = {N}, <k> = {k_mean:.2f}, 最大度 k_max = {deg.max()}, 结构截断 k_s = sqrt(<k>N) ≈ {k_s:.0f}")
print(f"度超过 k_s 的节点数: {(deg > k_s).sum()}")
print(f"多重图（保留重边/自环）: r = {r_multi:+.3f}；重边 {n_multi} 条，自环 {n_loops} 个")
print(f"简单图（合并重边、删自环）: r = {r_simple:+.3f}")

# 对照：把度截断在 k_s 以下再生成，伪异配基本消失
deg_cut = np.minimum(deg, int(k_s))
if deg_cut.sum() % 2:
    deg_cut[0] += 1
Gc = nx.Graph(nx.configuration_model(deg_cut.tolist(), seed=12))
Gc.remove_edges_from(nx.selfloop_edges(Gc))
print(f"度序列截断在 k_s 以下后的简单图: r = {nx.degree_assortativity_coefficient(Gc):+.3f}")

# 对照：泊松度分布（ER 图）没有结构截断问题
Ge = nx.gnm_random_graph(N, int(k_mean * N / 2), seed=13)
print(f"同样平均度的 ER 随机图: r = {nx.degree_assortativity_coefficient(Ge):+.3f}, 最大度 = {max(d for _, d in Ge.degree())}")

# 作图：度分布的互补累积分布与结构截断 k_s；四种构造下的 r
import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 2, figsize=(10, 4))
ks = np.sort(deg)
ax[0].loglog(ks, 1 - np.arange(len(ks)) / len(ks), ".", ms=3, color="C0")
ax[0].axvline(k_s, color="C3", ls="--", label=f"structural cutoff k_s = {k_s:.0f}")
ax[0].set_xlabel("degree k"); ax[0].set_ylabel("P(K >= k)"); ax[0].legend()
ax[0].set_title(f"Power-law degrees (gamma = {gamma}), k_max = {deg.max()}")
r_vals = [r_multi, r_simple, nx.degree_assortativity_coefficient(Gc), nx.degree_assortativity_coefficient(Ge)]
ax[1].bar(["multigraph", "simple graph", "simple, k<=k_s", "ER"], r_vals, color=["0.6", "C3", "C0", "0.6"])
ax[1].axhline(0, color="k", lw=0.8); ax[1].set_ylabel("degree assortativity r")
ax[1].set_title("Removing multi-edges alone makes r negative")
plt.tight_layout(); plt.show()

# %% 示例：度保持随机化检验——观测到的 r 是否超出度序列本身能解释的范围
# 两个“观测网络”有相同的幂律度序列：
#   网络 A：对简单配置模型再做充分的双边交换，相当于从“给定度序列的均匀随机简单图”中抽一张
#           （只含结构性异配）；
#   网络 B：在 A 的基础上做部分异配重连（p=0.5，模拟真实的“枢纽回避”机制）。
# 对每个网络生成 100 个保度、保持简单图的随机网络（双边交换，Maslov–Sneppen），比较 r。
# 解读：A 的 r 虽为负，却落在零分布之内（结构性）；B 的 r 显著低于零分布（超出度序列的额外异配）。
# 注意：直接“合并重边、删自环”得到的简单图（erased configuration model）与均匀随机简单图不是同一个
# 分布，拿它当零模型会给出有偏的 r，所以这里先用双边交换把 A 混合充分。
import numpy as np
import networkx as nx

rng = np.random.default_rng(5)
N, gamma = 1500, 2.3
deg = np.floor(2 * (1 - rng.random(N)) ** (-1 / (gamma - 1))).astype(int)
deg = np.minimum(deg, 120)
if deg.sum() % 2:
    deg[0] += 1
A = nx.Graph(nx.configuration_model(deg.tolist(), seed=1))
A.remove_edges_from(nx.selfloop_edges(A))
nx.double_edge_swap(A, nswap=20 * A.number_of_edges(), max_tries=10**7, seed=3)


def xbs_rewire(G, n_swaps, p, seed):
    rng = np.random.default_rng(seed)
    G = G.copy()
    dg = dict(G.degree())
    edges = list(G.edges())
    done = 0
    while done < n_swaps:
        i, j = rng.choice(len(edges), 2, replace=False)
        (a, b), (c, d) = edges[i], edges[j]
        nodes = [a, b, c, d]
        if len(set(nodes)) < 4:
            continue
        if rng.random() < p:
            s = sorted(nodes, key=lambda x: dg[x], reverse=True)
            new = [(s[0], s[3]), (s[1], s[2])]
        else:
            rng.shuffle(nodes)
            new = [(nodes[0], nodes[1]), (nodes[2], nodes[3])]
        if any(G.has_edge(*e) for e in new):
            continue
        G.remove_edges_from([(a, b), (c, d)])
        G.add_edges_from(new)
        edges[i], edges[j] = new
        done += 1
    return G


B = xbs_rewire(A, A.number_of_edges(), p=0.5, seed=2)


def null_r(G, n_null=100, swaps_per_edge=5, seed=0):
    vals = []
    for s in range(n_null):
        H = G.copy()
        m = H.number_of_edges()
        nx.double_edge_swap(H, nswap=swaps_per_edge * m, max_tries=100 * swaps_per_edge * m, seed=seed + s)
        vals.append(nx.degree_assortativity_coefficient(H))
    return np.array(vals)


tests = []                                                  # 保存结果用于作图
for name, G in [("网络 A（仅结构性异配）", A), ("网络 B（额外异配重连）", B)]:
    r_obs = nx.degree_assortativity_coefficient(G)
    r0 = null_r(G, n_null=100, swaps_per_edge=5, seed=100)
    tests.append((r_obs, r0))
    z = (r_obs - r0.mean()) / r0.std(ddof=1)
    p_low = (1 + np.sum(r0 <= r_obs)) / (len(r0) + 1)       # 单侧：是否比零模型更异配
    print(f"{name}: r_obs = {r_obs:+.3f}; 零模型 r = {r0.mean():+.3f} ± {r0.std(ddof=1):.3f}; "
          f"z = {z:+.1f}; 单侧经验 p = {p_low:.3f}")

# 对照：erased configuration model（不再交换）与均匀随机简单图的 r 不同
E = nx.Graph(nx.configuration_model(deg.tolist(), seed=1))
E.remove_edges_from(nx.selfloop_edges(E))
print(f"erased 配置模型 r = {nx.degree_assortativity_coefficient(E):+.3f}，"
      f"同一度序列的保度随机网络 r = {null_r(E, n_null=20, seed=500).mean():+.3f}")

# 作图：两个网络的保度零分布与观测 r
import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
for a, (r_obs, r0), ttl in zip(ax, tests, ["A: structural disassortativity only", "B: extra disassortative rewiring"]):
    a.hist(r0, bins=20, color="0.7", edgecolor="white", label="degree-preserving null (n=100)")
    a.axvline(r_obs, color="C3", lw=2, label=f"observed r = {r_obs:+.3f}")
    a.set_xlabel("degree assortativity r"); a.set_title(ttl, fontsize=10); a.legend(fontsize=8)
ax[0].set_ylabel("count")
fig.suptitle("Only network B is more disassortative than its degree sequence implies")
plt.tight_layout(); plt.show()

# %% 示例：富人俱乐部系数 phi(k) 及其保度归一化 rho(k)
# 构造两张度序列相近的网络：BA 网络，以及在 BA 网络上把前 2% 高度节点之间“补齐”连接后
# 再用保度交换恢复原度序列的网络（植入的富人俱乐部）。
# 计算未归一化 phi(k) 与归一化 rho(k) = phi(k)/phi_rand(k)，phi_rand 取 20 个保度随机网络的平均。
# 解读：即使是 BA 网络，phi(k) 也随 k 上升，单看 phi(k) 会误判；rho(k) > 1 才是富人俱乐部的证据。
import numpy as np
import networkx as nx

G0 = nx.barabasi_albert_graph(2000, 3, seed=4)
deg0 = dict(G0.degree())

# 植入富人俱乐部：把度最高的 40 个节点两两相连，再为每条新边删去一条“枢纽-低度节点”边并
# 把被拆开的低度端点两两接上，近似保持度序列（剩余偏差很小）。
rng = np.random.default_rng(0)
G1 = G0.copy()
hubs = sorted(G1, key=lambda x: deg0[x], reverse=True)[:40]
hubset = set(hubs)
for i in range(len(hubs)):
    for j in range(i + 1, len(hubs)):
        a, b = hubs[i], hubs[j]
        if G1.has_edge(a, b):
            continue
        na = [x for x in G1[a] if x not in hubset]
        nb = [x for x in G1[b] if x not in hubset]
        if not na or not nb:
            continue
        x, y = rng.choice(na), rng.choice(nb)
        if x == y or G1.has_edge(x, y):
            continue
        G1.remove_edges_from([(a, x), (b, y)])
        G1.add_edges_from([(a, b), (x, y)])
assert dict(G1.degree()) == deg0                     # 度序列严格不变


def rich_club(G):
    return nx.rich_club_coefficient(G, normalized=False)


def rich_club_rand(G, n_null=20, seed=0):
    acc = {}
    for s in range(n_null):
        H = G.copy()
        m = H.number_of_edges()
        nx.double_edge_swap(H, nswap=10 * m, max_tries=1000 * m, seed=seed + s)
        for k, v in rich_club(H).items():
            acc.setdefault(k, []).append(v)
    return {k: np.mean(v) for k, v in acc.items()}


curves = []                                         # 保存 phi 与 phi_rand 用于作图
for name, G in [("BA 网络", G0), ("植入富人俱乐部", G1)]:
    phi = rich_club(G)
    phi_r = rich_club_rand(G, n_null=20, seed=10)
    curves.append((phi, phi_r))
    print(name)
    for k in [5, 10, 20, 30, 40, 60]:
        if k in phi and phi_r.get(k, 0) > 0:
            n_rich = sum(1 for _, d in G.degree() if d > k)
            print(f"   k > {k:3d}: N_>k = {n_rich:4d}, phi = {phi[k]:.3f}, phi_rand = {phi_r[k]:.3f}, "
                  f"rho = {phi[k] / phi_r[k]:.2f}")

# 作图：未归一化 phi(k) 与归一化 rho(k) = phi / phi_rand
import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 2, figsize=(10, 4))
for (phi, phi_r), lab, mk in zip(curves, ["BA network", "planted rich club"], ["o", "s"]):
    ks = [k for k in sorted(phi) if phi_r.get(k, 0) > 0 and sum(1 for _, d in G0.degree() if d > k) >= 5]
    ax[0].plot(ks, [phi[k] for k in ks], marker=mk, ms=3, label=lab)
    ax[1].plot(ks, [phi[k] / phi_r[k] for k in ks], marker=mk, ms=3, label=lab)
ax[0].set_ylabel("phi(k), unnormalized"); ax[0].set_title("phi(k) rises with k even in BA")
ax[1].axhline(1, color="gray", ls="--"); ax[1].set_ylabel("rho(k) = phi / phi_rand")
ax[1].set_title("Planted club: rho(k) >> 1; BA stays near 1")
for a in ax:
    a.set_xscale("log"); a.set_xlabel("degree threshold k"); a.legend()
plt.tight_layout(); plt.show()

# %% 示例：聚集谱 C(k) 与层次模块网络（Ravasz–Barabási 型确定性模型）
# 递归构造层次网络：基本单元是 5 个节点的完全图（1 个中心 + 4 个外围）；每一层把当前网络复制 4 份，
# 并把各副本中“最底层外围节点”全部连到原网络的中心节点。
# 对比 BA 网络：层次网络的 C(k) 随 k 近似按 k^(-1) 下降，BA 网络的 C(k) 基本与 k 无关。
# 解读：C(k) 的负斜率是层次模块性的一个必要而非充分的信号；度相关与 C(k) 的估计也相互影响。
import numpy as np
import networkx as nx


def hierarchical_network(levels=3):
    G = nx.complete_graph(5)
    center = 0
    periphery = [1, 2, 3, 4]                 # 当前网络中“最外围”的节点
    for _ in range(levels):
        n = G.number_of_nodes()
        H = G.copy()
        new_periph = []
        for c in range(1, 5):
            offset = c * n
            H = nx.union(H, nx.relabel_nodes(G, {v: v + offset for v in G}))
            for p in periphery:
                H.add_edge(center, p + offset)
                new_periph.append(p + offset)
        G, periphery = H, new_periph
    return G


def ck_curve(G):
    cl = nx.clustering(G)
    deg = dict(G.degree())
    out = {}
    for k in sorted(set(deg.values())):
        if k >= 2:
            out[k] = np.mean([cl[i] for i in G if deg[i] == k])
    return out


H = hierarchical_network(levels=3)
B = nx.barabasi_albert_graph(H.number_of_nodes(), 3, seed=1)
for name, G in [("层次网络", H), ("BA 网络", B)]:
    ck = ck_curve(G)
    ks = np.array([k for k in ck if ck[k] > 0], float)
    cs = np.array([ck[k] for k in ck if ck[k] > 0])
    slope = np.polyfit(np.log(ks), np.log(cs), 1)[0]
    print(f"{name}: N = {G.number_of_nodes()}, 平均聚集系数 = {nx.average_clustering(G):.3f}, "
          f"log C(k) ~ log k 斜率 = {slope:.2f}, 度相关 r = {nx.degree_assortativity_coefficient(G):+.3f}")
    show = list(ck.items())[:: max(1, len(ck) // 6)]
    print("   部分 C(k):", {k: round(float(v), 3) for k, v in show})

# 作图：双对数坐标下的聚集谱 C(k)，并画出 k^-1 参考线
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(6.4, 4.2))
for G, lab, mk in [(H, "hierarchical network", "o"), (B, "BA network", "s")]:
    ck = {k: c for k, c in ck_curve(G).items() if c > 0}
    ax.loglog(list(ck), list(ck.values()), mk, ms=5, alpha=0.8, label=lab)
kref = np.array([4, 100])
ax.loglog(kref, 2.0 / kref, "k--", lw=1, label="~ k^-1")
ax.set_xlabel("degree k"); ax.set_ylabel("clustering spectrum C(k)")
ax.set_title("Hierarchical modularity: C(k) falls as k^-1, BA stays flat")
ax.legend(); plt.tight_layout(); plt.show()

# %% 示例：k-核分解——手写剥离算法并与 NetworkX 对照，比较核数与度
# 实现 Batagelj–Zaversnik 的“按当前度从小到大剥离”思想（这里用简单的最小堆，复杂度 O(M log N)），
# 与 nx.core_number 对照；再在一个幂律随机网络与一个“度相同但枢纽之间互连更多”的网络上比较：
# （不用 BA 网络：BA 网络每个新节点恰好带 m 条边，整张图就是一个 m-核，壳层结构是平凡的。）
# 最内核大小、最内核内部密度，以及核数与度的 Spearman 相关。
# 解读：核数度量的是“嵌在多稠密的子图里”，与度高度相关但不等同；度相同的节点可以处在很不同的壳层。
import heapq
import numpy as np
import networkx as nx
from scipy.stats import spearmanr


def core_numbers(G):
    deg = dict(G.degree())
    heap = [(d, v) for v, d in deg.items()]
    heapq.heapify(heap)
    removed, core, k = set(), {}, 0
    while heap:
        d, v = heapq.heappop(heap)
        if v in removed or d != deg[v]:
            continue                      # 过期的堆元素
        k = max(k, d)                     # 当前壳层编号只增不减
        core[v] = k
        removed.add(v)
        for u in G[v]:
            if u not in removed:
                deg[u] -= 1
                heapq.heappush(heap, (deg[u], u))
    return core


rng = np.random.default_rng(2)
deg_seq = np.minimum(np.floor((1 - rng.random(3000)) ** (-1 / 1.3)).astype(int), 200)   # 幂律，gamma≈2.3，k_min=1
if deg_seq.sum() % 2:
    deg_seq[0] += 1
G = nx.Graph(nx.configuration_model(deg_seq.tolist(), seed=2))
G.remove_edges_from(nx.selfloop_edges(G))
core = core_numbers(G)
print("手写剥离算法与 nx.core_number 一致:", core == nx.core_number(G))

# 一个度序列相同、但用同配重连让高度节点彼此相连的网络
def assort_rewire(G, n_swaps, seed):
    rng = np.random.default_rng(seed)
    G = G.copy(); dg = dict(G.degree()); edges = list(G.edges()); done = 0
    while done < n_swaps:
        i, j = rng.choice(len(edges), 2, replace=False)
        (a, b), (c, d) = edges[i], edges[j]
        if len({a, b, c, d}) < 4:
            continue
        s = sorted([a, b, c, d], key=lambda x: dg[x], reverse=True)
        new = [(s[0], s[1]), (s[2], s[3])]
        if any(G.has_edge(*e) for e in new):
            continue
        G.remove_edges_from([(a, b), (c, d)]); G.add_edges_from(new)
        edges[i], edges[j] = new; done += 1
    return G


Ga = assort_rewire(G, G.number_of_edges(), seed=3)
for name, H in [("幂律随机网络", G), ("同配重连（度序列相同）", Ga)]:
    cn = nx.core_number(H)
    kmax = max(cn.values())
    inner = [v for v in H if cn[v] == kmax]
    sub = H.subgraph(inner)
    deg = dict(H.degree())
    rho = spearmanr([deg[v] for v in H], [cn[v] for v in H])[0]
    print(f"{name}: r = {nx.degree_assortativity_coefficient(H):+.2f}, 最大核数 k_s^max = {kmax}, "
          f"最内核节点数 = {len(inner)}, 最内核内部密度 = {nx.density(sub):.2f}, 核数与度的 Spearman = {rho:.2f}")

# 同一度的节点可以位于不同壳层
deg = dict(G.degree())
k_ex = 6
shells = sorted({core[v] for v in G if deg[v] == k_ex})
print(f"幂律随机网络中度为 {k_ex} 的节点分布在这些壳层: {shells}")

# 作图：度 vs 核数（加少量抖动以显示重叠点）
import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
jit = np.random.default_rng(0)
for a, H, ttl in [(ax[0], G, "power-law random network"), (ax[1], Ga, "assortative rewiring (same degrees)")]:
    cn = nx.core_number(H)
    x = np.array([H.degree(v) for v in H]); y = np.array([cn[v] for v in H], float)
    a.scatter(x, y + jit.uniform(-0.2, 0.2, len(y)), s=6, alpha=0.4)
    a.set_xscale("log"); a.set_xlabel("degree k"); a.set_title(f"{ttl}\nmax core = {int(y.max())}", fontsize=10)
ax[0].set_ylabel("core number")
plt.tight_layout(); plt.show()

# %% 示例：度相关如何改变巨连通分支、传播阈值与可同步性
# 从同一张 ER 随机图（N=2000, <k>=4）出发，用 Xulvi-Brunet–Sokolov 重连（p=0.5）得到同配与异配版本。
# 比较：(1) 随机删边（键渗流）后巨连通分支占比；(2) 邻接矩阵最大特征值 lambda_1，
#   SIS 模型的淬火平均场阈值约为 1/lambda_1；(3) 拉普拉斯特征值比 lambda_N/lambda_2（越小越易同步）。
# 解读：同配使 lambda_1 增大（高度节点聚在一起形成“储库”，阈值降低）、低保留率下巨分支更易存活，
# 但高保留率下巨分支更小；同配同时使 lambda_N/lambda_2 增大，可同步性变差。
import numpy as np
import networkx as nx
from scipy.sparse.linalg import eigsh
from scipy.sparse.csgraph import laplacian


def xbs_rewire(G, n_swaps, mode, p, seed):
    rng = np.random.default_rng(seed)
    G = G.copy(); dg = dict(G.degree()); edges = list(G.edges()); done = 0
    while done < n_swaps:
        i, j = rng.choice(len(edges), 2, replace=False)
        (a, b), (c, d) = edges[i], edges[j]
        nodes = [a, b, c, d]
        if len(set(nodes)) < 4:
            continue
        if rng.random() < p:
            s = sorted(nodes, key=lambda x: dg[x], reverse=True)
            new = [(s[0], s[1]), (s[2], s[3])] if mode == "assortative" else [(s[0], s[3]), (s[1], s[2])]
        else:
            rng.shuffle(nodes)
            new = [(nodes[0], nodes[1]), (nodes[2], nodes[3])]
        if any(G.has_edge(*e) for e in new):
            continue
        G.remove_edges_from([(a, b), (c, d)]); G.add_edges_from(new)
        edges[i], edges[j] = new; done += 1
    return G


def giant_after_bond_percolation(G, keep, n_rep=10, seed=0):
    rng = np.random.default_rng(seed)
    edges = list(G.edges())
    out = []
    for _ in range(n_rep):
        H = nx.Graph()
        H.add_nodes_from(G)
        H.add_edges_from([e for e in edges if rng.random() < keep])
        out.append(max(len(c) for c in nx.connected_components(H)) / G.number_of_nodes())
    return np.mean(out)


G0 = nx.gnm_random_graph(2000, 4000, seed=1)
M = G0.number_of_edges()
nets = {
    "同配 (p=0.5)": xbs_rewire(G0, 3 * M, "assortative", 0.5, 1),
    "ER 原始": G0,
    "异配 (p=0.5)": xbs_rewire(G0, 3 * M, "disassortative", 0.5, 2),
}
print("保留边比例:            0.30    0.50    0.90")
summ = []                                    # 保存结果用于作图
for name, G in nets.items():
    A = nx.to_scipy_sparse_array(G, dtype=float, format="csr")
    lam1 = eigsh(A, k=1, which="LA")[0][0]
    S = [giant_after_bond_percolation(G, q, seed=3) for q in (0.3, 0.5, 0.9)]
    Gc = G.subgraph(max(nx.connected_components(G), key=len))
    L = laplacian(nx.to_numpy_array(Gc))
    ev = np.sort(np.linalg.eigvalsh(L))
    print(f"{name:12s} r={nx.degree_assortativity_coefficient(G):+.2f}  巨分支占比 "
          f"{S[0]:.3f}  {S[1]:.3f}  {S[2]:.3f} | lambda_1={lam1:.2f} (SIS 阈值≈{1/lam1:.3f}) "
          f"| lambda_N/lambda_2={ev[-1]/ev[1]:.1f}")
    summ.append((nx.degree_assortativity_coefficient(G), S, lam1, ev[-1] / ev[1]))

# 作图：键渗流后的巨分支占比，以及 SIS 阈值与同步性指标
import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 2, figsize=(10, 4))
labs = ["assortative", "ER original", "disassortative"]
for (r, S, lam1, ratio), lab, mk in zip(summ, labs, ["o", "s", "^"]):
    ax[0].plot([0.3, 0.5, 0.9], S, marker=mk, label=f"{lab} (r={r:+.2f})")
ax[0].set_xlabel("fraction of edges kept"); ax[0].set_ylabel("giant component fraction"); ax[0].legend()
ax[0].set_title("Assortative nets survive sparse sampling, lose at high retention", fontsize=10)
x = np.arange(3)
ax[1].bar(x - 0.2, [1 / s[2] for s in summ], 0.4, label="SIS threshold 1/lambda_1")
ax2 = ax[1].twinx()
ax2.bar(x + 0.2, [s[3] for s in summ], 0.4, color="C1", label="lambda_N/lambda_2")
ax[1].set_xticks(x); ax[1].set_xticklabels(labs); ax[1].set_ylabel("1/lambda_1 (blue)")
ax2.set_ylabel("lambda_N/lambda_2 (orange, lower = easier sync)")
ax[1].set_title("Assortativity lowers epidemic threshold, hurts sync", fontsize=10)
plt.tight_layout(); plt.show()

# %% 示例：阈值化相关网络中的同配性——模块大小如何制造正的 r
# 模拟 60 个“脑区”的时间序列：4 个功能系统，大小分别为 30、15、10、5 个脑区，系统内共享一个波动。
# 用比例阈值保留最强的若干比例相关，得到二值网络，计算度同配 r，并与保度零模型比较；
# 再用 Newman (2003) 的类别同配系数检查边是否偏向连接同一系统的脑区。
# 解读：大系统里的脑区仅因“同伴多”而度高，且主要连向同系统（同样度高）的脑区，于是 r > 0；
# 这种同配来自模块大小与相关的传递性，并随阈值（密度）明显变化，不对应解剖上的“枢纽互连”。
import numpy as np
import networkx as nx

rng = np.random.default_rng(1)
sizes = [30, 15, 10, 5]
labels = np.repeat(np.arange(len(sizes)), sizes)
N, T = len(labels), 300
X = 0.6 * rng.standard_normal((len(sizes), T))[labels] + rng.standard_normal((N, T))
R = np.corrcoef(X)
np.fill_diagonal(R, 0)
iu = np.triu_indices(N, 1)


def threshold(R, density):
    thr = np.quantile(R[iu], 1 - density)
    return nx.from_numpy_array((R > thr).astype(int))


for dens in [0.05, 0.10, 0.20]:
    G = threshold(R, dens)
    print(f"密度 {dens:.2f}: 度同配 r = {nx.degree_assortativity_coefficient(G):+.3f}")

G = threshold(R, 0.10)
nx.set_node_attributes(G, {i: int(labels[i]) for i in range(N)}, "system")
r_obs = nx.degree_assortativity_coefficient(G)
null = []
for s in range(200):
    H = G.copy()
    nx.double_edge_swap(H, nswap=10 * H.number_of_edges(), max_tries=10**6, seed=s)
    null.append(nx.degree_assortativity_coefficient(H))
null = np.array(null)
p = (1 + np.sum(null >= r_obs)) / (len(null) + 1)
print(f"密度 0.10: r = {r_obs:+.3f}; 保度零模型 r = {null.mean():+.3f} ± {null.std(ddof=1):.3f}; 单侧经验 p = {p:.3f}")
deg = dict(G.degree())
for s_id, sz in enumerate(sizes):
    print(f"   系统 {s_id}（{sz} 个脑区）的平均度 = {np.mean([deg[i] for i in G if labels[i] == s_id]):.1f}")

# 类别同配系数 r = (sum_i e_ii - sum_i a_i^2) / (1 - sum_i a_i^2)（无向网络 a_i = b_i）
e = np.zeros((len(sizes), len(sizes)))
for u, v in G.edges():
    e[labels[u], labels[v]] += 1
    e[labels[v], labels[u]] += 1
e /= e.sum()
a = e.sum(axis=1)
r_cat = (np.trace(e) - a @ a) / (1 - a @ a)
print(f"按功能系统的类别同配系数（手算）= {r_cat:.3f}；NetworkX = {nx.attribute_assortativity_coefficient(G, 'system'):.3f}")

# 作图：按系统排序的二值邻接矩阵（密度 0.10），以及度同配 r 的保度零分布
import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 2, figsize=(10, 4))
ax[0].imshow(nx.to_numpy_array(G, nodelist=range(N)), cmap="Greys", interpolation="none")
for b in np.cumsum(sizes)[:-1]:
    ax[0].axhline(b - 0.5, color="C3", lw=0.8); ax[0].axvline(b - 0.5, color="C3", lw=0.8)
ax[0].set_title("Thresholded network (density 0.10),\nsystems of size 30/15/10/5", fontsize=10)
ax[0].set_xlabel("region"); ax[0].set_ylabel("region")
ax[1].hist(null, bins=25, color="0.7", edgecolor="white", label="degree-preserving null")
ax[1].axvline(r_obs, color="C3", lw=2, label=f"observed r = {r_obs:+.3f}")
ax[1].set_xlabel("degree assortativity r"); ax[1].set_ylabel("count"); ax[1].legend(fontsize=8)
ax[1].set_title("Module size alone produces positive r", fontsize=10)
plt.tight_layout(); plt.show()
