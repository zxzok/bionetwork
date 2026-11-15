# 依赖：networkx>=3, numpy, scipy, matplotlib（全部示例只用这些库，GCN 与嵌入均用 numpy 从零实现）
# 数据：示例 1、2、4、11、12 使用 networkx 自带的 Zachary 空手道俱乐部网络（Zachary 1977；34 个节点，
#       节点属性 'club' 记录俱乐部实际分裂为 'Mr. Hi' 与 'Officer' 两派）；其余示例使用代码生成的
#       合成网络或模拟数据（BA、WS、ER、种植分割模型、模拟接触序列），仅用于演示方法。
# 输入格式：网络为 networkx.Graph；超图用关联矩阵（节点 × 超边）；时间网络用接触序列 (u, v, t)。
# 前四个示例围绕同一个原则：任何网络指标都要写清“与什么比较”，并把对照和不确定性画进图里；
# 后面的示例对应可视化、高阶网络、时间网络、多层网络、网络表示学习与图神经网络等前沿方向。

# %% 示例：小世界性——与同规模 ER 随机图比较
# 计算空手道网络的平均聚集系数 C 和平均最短路径 L；生成 20 个节点数、边数相同的 ER 随机图
# （取最大连通分支）得到 C_rand、L_rand；求小世界系数 sigma = (C/C_rand) / (L/L_rand)。
# 解读：C 远大于 C_rand 而 L 与 L_rand 接近时 sigma 明显大于 1，提示小世界性。
import networkx as nx
import numpy as np

G = nx.karate_club_graph()
n, m = G.number_of_nodes(), G.number_of_edges()
C, L = nx.average_clustering(G), nx.average_shortest_path_length(G)

C_rand, L_rand = [], []
for s in range(20):
    R = nx.gnm_random_graph(n, m, seed=s)
    R = R.subgraph(max(nx.connected_components(R), key=len)).copy()
    C_rand.append(nx.average_clustering(R))
    L_rand.append(nx.average_shortest_path_length(R))

sigma = (C / np.mean(C_rand)) / (L / np.mean(L_rand))
print(f"C = {C:.3f}（ER 均值 {np.mean(C_rand):.3f}）；L = {L:.3f}（ER 均值 {np.mean(L_rand):.3f}）；sigma = {sigma:.2f}")

# 作图：C 与 L 的真实值和 20 个 ER 随机图的取值
import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 2, figsize=(10, 4))
for a, obs, null, nm in [(ax[0], C, C_rand, "average clustering C"), (ax[1], L, L_rand, "average shortest path L")]:
    a.plot(np.linspace(-0.15, 0.15, 20), null, "o", color="0.5", ms=4, label="ER (n=20)")
    a.plot(1, obs, "D", color="C3", ms=9, label="karate club")
    a.set_xticks([0, 1]); a.set_xticklabels(["ER", "observed"]); a.set_xlim(-0.6, 1.6); a.set_ylabel(nm)
ax[0].legend(fontsize=8); ax[0].set_title("C far above random", fontsize=10)
ax[1].set_title("L close to random", fontsize=10)
fig.suptitle(f"Small-world coefficient sigma = {sigma:.2f}", fontsize=11)
plt.tight_layout(); plt.show()

# %% 示例：社团检测与已知分组的一致性
# 用 Louvain（seed=0）划分空手道网络并计算模块度 Q，再统计每个社团中两派成员各有多少。
# 解读：若社团几乎不跨派混合，说明拓扑划分与已知的社会分裂一致；
# 社团数多于两派时，表示算法把某一派进一步细分，这本身不意味着划分错误。
import networkx as nx

G = nx.karate_club_graph()
comms = nx.community.louvain_communities(G, seed=0)
Q = nx.community.modularity(G, comms)
print(f"社团数 = {len(comms)}，Q = {Q:.3f}")
for i, c in enumerate(comms):
    hi = sum(1 for v in c if G.nodes[v]["club"] == "Mr. Hi")
    print(f"社团{i}: 大小 {len(c)}，Mr. Hi 派 {hi} 人，Officer 派 {len(c) - hi} 人")

# 作图：颜色 = Louvain 社团，形状 = 实际所属派别（圆 = Mr. Hi，方 = Officer）
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(6.4, 4.2))
pos = nx.spring_layout(G, seed=3)
lab = {v: i for i, c in enumerate(comms) for v in c}
nx.draw_networkx_edges(G, pos, ax=ax, edge_color="0.6", alpha=0.4)
for club, shape in [("Mr. Hi", "o"), ("Officer", "s")]:
    vs = [v for v in G if G.nodes[v]["club"] == club]
    nx.draw_networkx_nodes(G, pos, nodelist=vs, ax=ax, node_shape=shape, node_size=90,
                           node_color=[lab[v] for v in vs], cmap="tab10", vmin=0, vmax=9)
ax.set_title(f"Louvain communities (color) vs actual factions (shape), Q = {Q:.2f}", fontsize=10); ax.axis("off")
plt.tight_layout(); plt.show()

# %% 示例：鲁棒性——随机失效与蓄意攻击（双曲线对照图）
# 在 500 个节点的 BA 网络上依次删除 0%–50% 的节点，比较两种策略下最大连通分支占原网络的比例：
# 随机删除 vs 按初始度从高到低删除。图中把两条曲线画在同一坐标系，标题直接写结论。
# 解读：随机删除时巨分支缓慢缩小，攻击枢纽时迅速崩解——无标度网络“耐随机、怕攻击”。
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

G0 = nx.barabasi_albert_graph(500, 2, seed=16)
N = G0.number_of_nodes()
fracs = np.linspace(0, 0.5, 11)
rng = np.random.default_rng(0)
order_random = list(rng.permutation(N))
order_attack = [v for v, _ in sorted(G0.degree(), key=lambda x: -x[1])]

def giant_fraction(G0, order, f):
    G = G0.copy()
    G.remove_nodes_from(order[:int(f * N)])
    return max((len(c) for c in nx.connected_components(G)), default=0) / N

gr = [giant_fraction(G0, order_random, f) for f in fracs]
ga = [giant_fraction(G0, order_attack, f) for f in fracs]
print(f"删除 20% 节点后，巨分支比例：随机删除 = {gr[4]:.2f}，攻击枢纽 = {ga[4]:.2f}")

plt.figure(figsize=(5, 3))
plt.plot(fracs, gr, "o-", label="random failure")
plt.plot(fracs, ga, "s-", label="targeted attack (by degree)")
plt.xlabel("fraction of nodes removed"); plt.ylabel("giant component fraction")
plt.title("Hub removal fragments the BA network far faster")
plt.legend(); plt.tight_layout(); plt.show()

# %% 示例：度保持零模型与“真实值 vs 零分布”图
# ER 不保留度分布；更严格的基线是度保持重连（nx.double_edge_swap 反复交换两条边的端点）。
# 生成 30 个度保持随机网络，计算平均聚集系数的均值、标准差和空手道网络的 z 分数；
# 再把零分布画成直方图、真实值画成竖线——这是呈现“与什么比较”的常用图式。
# 解读：z 明显大于 2 说明高聚集不能仅由度分布解释；与 ER 基线相比，度保持基线下的偏离程度更小，
# 说明换不同零模型，“高聚集”的程度判断会不同，报告中必须写清所用零模型。
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

G = nx.karate_club_graph()
C = nx.average_clustering(G)
C_null = []
for s in range(30):
    R = G.copy()
    nx.double_edge_swap(R, nswap=10 * R.number_of_edges(), max_tries=10**5, seed=s)
    C_null.append(nx.average_clustering(R))
z = (C - np.mean(C_null)) / np.std(C_null)
print(f"C = {C:.3f}，度保持随机 = {np.mean(C_null):.3f} ± {np.std(C_null):.3f}，z = {z:.1f}")

plt.figure(figsize=(5, 3))
plt.hist(C_null, bins=10, color="0.7", edgecolor="white", label="degree-preserving null (n=30)")
plt.axvline(C, color="C3", lw=2, label="observed")
plt.xlabel("average clustering"); plt.ylabel("count")
plt.title(f"Observed clustering exceeds the null (z = {z:.1f})")
plt.legend(fontsize=8); plt.tight_layout(); plt.show()

# %% 示例：同一个网络的两种画法——节点–链接图与按社团排序的邻接矩阵
# 用种植分割模型（4 个社团、每个 30 个节点）生成网络，并排画出：
# (a) 弹簧布局的节点–链接图；(b) 节点随机排列的邻接矩阵；(c) 按 Louvain 社团排序的邻接矩阵。
# 配色用 matplotlib 的 "tab10" 前 4 色并辅以不同标记形状，避免只靠红绿区分。
# 解读：节点–链接图中的“团块”依赖布局算法的随机初值；排序后的矩阵中，社团表现为对角块，
# 块外的点就是社团间连边，块内密度可以直接读出——稠密网络中矩阵往往比节点–链接图更诚实。
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

G = nx.planted_partition_graph(4, 30, p_in=0.3, p_out=0.02, seed=3)
comms = sorted(nx.community.louvain_communities(G, seed=0), key=len, reverse=True)
label = {v: i for i, c in enumerate(comms) for v in c}
print(f"节点 {G.number_of_nodes()}，边 {G.number_of_edges()}，Louvain 社团数 {len(comms)}，"
      f"Q = {nx.community.modularity(G, comms):.3f}")

rng = np.random.default_rng(0)
order_rand = list(rng.permutation(list(G.nodes())))
order_comm = [v for c in comms for v in sorted(c)]
A_rand = nx.to_numpy_array(G, nodelist=order_rand)
A_comm = nx.to_numpy_array(G, nodelist=order_comm)
within = sum(1 for u, v in G.edges() if label[u] == label[v]) / G.number_of_edges()
print(f"社团内边占全部边的比例 = {within:.2f}")

fig, ax = plt.subplots(1, 3, figsize=(11, 3.6))
pos = nx.spring_layout(G, seed=1)
colors = plt.get_cmap("tab10").colors
markers = ["o", "s", "^", "D", "v", "P"]
nx.draw_networkx_edges(G, pos, ax=ax[0], alpha=0.15, width=0.5)
for i, c in enumerate(comms):
    nx.draw_networkx_nodes(G, pos, nodelist=list(c), ax=ax[0], node_size=18,
                           node_color=[colors[i % 10]], node_shape=markers[i % len(markers)])
ax[0].set_title("(a) node-link, spring layout"); ax[0].axis("off")
ax[1].imshow(A_rand, cmap="Greys", interpolation="none"); ax[1].set_title("(b) matrix, random order")
ax[2].imshow(A_comm, cmap="Greys", interpolation="none"); ax[2].set_title("(c) matrix, ordered by community")
for a in ax[1:]:
    a.set_xticks([]); a.set_yticks([])
plt.tight_layout(); plt.show()

# %% 示例：超图与它的两两投影——投影会丢失信息
# 用关联矩阵 H（节点 × 超边）表示超图。超图 H1 含一个三元超边 {a,b,c}（如三个亚基组成的复合物）；
# 超图 H2 含三条二元边 {a,b}、{b,c}、{a,c}（三对两两相互作用）。两者的两两投影 W = H H^T - D_v
# 完全相同，但超度（节点所在的超边数）与超边大小分布不同。
# 解读：投影图上无法区分“一个三元复合物”和“三个两两结合”，这正是需要高阶表示的原因。
import numpy as np

nodes = ["a", "b", "c", "d"]
H1 = np.array([[1, 0],   # 超边 e1={a,b,c}，e2={c,d}
               [1, 0],
               [1, 1],
               [0, 1]])
H2 = np.array([[1, 0, 1, 0],  # 超边 {a,b}、{b,c}、{a,c}、{c,d}
               [1, 1, 0, 0],
               [0, 1, 1, 1],
               [0, 0, 0, 1]])

def projection(H):
    W = H @ H.T
    np.fill_diagonal(W, 0)
    return (W > 0).astype(int)

for name, H in [("H1", H1), ("H2", H2)]:
    print(f"{name}: 超边大小 = {H.sum(0).tolist()}，超度 = {dict(zip(nodes, H.sum(1).tolist()))}")
    print(projection(H))
print("两个超图的两两投影是否相同：", np.array_equal(projection(H1), projection(H2)))

# 作图：两个超图的关联矩阵不同，两两投影却完全相同
import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 3, figsize=(10, 3.6), gridspec_kw={"width_ratios": [2, 4, 4]})
for a, M, ttl, xl in [(ax[0], H1, "H1: one triple {a,b,c}", ["{a,b,c}", "{c,d}"]),
                      (ax[1], H2, "H2: three pairs", ["{a,b}", "{b,c}", "{a,c}", "{c,d}"]),
                      (ax[2], projection(H1), "pairwise projection (H1 = H2)", nodes)]:
    a.imshow(M, cmap="Greys", vmin=0, vmax=1.5)
    a.set_xticks(range(M.shape[1])); a.set_xticklabels(xl, fontsize=8)
    a.set_yticks(range(4)); a.set_yticklabels(nodes); a.set_title(ttl, fontsize=10)
ax[0].set_xlabel("hyperedge"); ax[1].set_xlabel("hyperedge"); ax[2].set_xlabel("node")
plt.tight_layout(); plt.show()

# %% 示例：单纯复形的贝蒂数——空心三角形与实心三角形
# 构造边界矩阵 B1（节点 × 边）与 B2（边 × 三角形），用秩计算贝蒂数：
# beta_0 = n0 - rank B1，beta_1 = (n1 - rank B1) - rank B2。
# 同时构造霍奇拉普拉斯 L1 = B1^T B1 + B2 B2^T，其零空间维数等于 beta_1。
# 解读：只有三条边时有一个一维“洞”（beta_1 = 1）；把三角形 {0,1,2} 作为 2-单形填上后洞消失。
# 这正是“三人两两认识”与“三人同属一个群体”在拓扑上的区别。
import numpy as np
from itertools import combinations

def boundary_matrices(n_nodes, edges, triangles):
    edges = [tuple(sorted(e)) for e in edges]
    eidx = {e: i for i, e in enumerate(edges)}
    B1 = np.zeros((n_nodes, len(edges)))
    for j, (u, v) in enumerate(edges):
        B1[u, j], B1[v, j] = -1, 1
    B2 = np.zeros((len(edges), len(triangles)))
    for k, t in enumerate(triangles):
        a, b, c = sorted(t)
        # ∂[a,b,c] = [b,c] - [a,c] + [a,b]
        B2[eidx[(b, c)], k], B2[eidx[(a, c)], k], B2[eidx[(a, b)], k] = 1, -1, 1
    return B1, B2

def betti(n_nodes, edges, triangles):
    B1, B2 = boundary_matrices(n_nodes, edges, triangles)
    r1 = np.linalg.matrix_rank(B1) if B1.size else 0
    r2 = np.linalg.matrix_rank(B2) if B2.size else 0
    L1 = B1.T @ B1 + (B2 @ B2.T if B2.size else 0)
    null_L1 = int(np.sum(np.linalg.eigvalsh(L1) < 1e-9))
    assert np.allclose(B1 @ B2, 0) if B2.size else True  # 边界的边界为零
    return int(n_nodes - r1), int(len(edges) - r1 - r2), null_L1

edges = list(combinations(range(3), 2))
print("空心三角形：beta_0, beta_1, dim ker L1 =", betti(3, edges, []))
print("实心三角形：beta_0, beta_1, dim ker L1 =", betti(3, edges, [(0, 1, 2)]))
square = [(0, 1), (1, 2), (2, 3), (0, 3), (4, 5)]
print("四边形环 + 一条孤立边：beta_0, beta_1, dim ker L1 =", betti(6, square, []))

# 作图：三个单纯复形及其贝蒂数（填充 = 2-单形）
import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 3, figsize=(10, 3.4))
tri = np.array([[0, 0], [1, 0], [0.5, 0.87]])
sq = np.array([[0, 0], [1, 0], [1, 1], [0, 1], [1.6, 0.2], [1.6, 0.8]])
cases = [(tri, edges, [], "hollow triangle"), (tri, edges, [(0, 1, 2)], "filled triangle"),
         (sq, square, [], "square loop + isolated edge")]
for a, (P, E, T, ttl) in zip(ax, cases):
    for t in T:
        a.fill(*P[list(t)].T, color="C0", alpha=0.3)
    for u, v in E:
        a.plot(*P[[u, v]].T, color="0.3", lw=2)
    a.plot(*P[:max(max(e) for e in E) + 1].T, "o", color="C3", ms=8)
    b0, b1, _ = betti(len(P), E, T)
    a.set_title(f"{ttl}\nbeta_0 = {b0}, beta_1 = {b1}", fontsize=10); a.set_aspect("equal"); a.axis("off")
plt.tight_layout(); plt.show()

# %% 示例：持续同调入门——加权网络在阈值过滤下的贝蒂曲线
# 对一个加权网络，按边权从大到小逐步加入边（过滤），在每一步构造团复形（clique complex，
# 这里只取到三角形），计算 beta_0（连通分支数）与 beta_1（未被三角形填满的环的数目）。
# 两个模拟网络：环状几何网络（节点均匀排在圆周上，权重随距离衰减）与打乱权重的对照。
# 解读：环状网络在中间阈值段出现持续存在的 beta_1 = 1（一个大环），打乱后的网络 beta_1 的
# 峰更早、更“碎”。持续同调把“在哪些阈值下存在多少个洞”作为特征，而不是只看一个阈值。
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from itertools import combinations

def betti_curve(W, n_steps=40):
    n = W.shape[0]
    iu = np.triu_indices(n, 1)
    w_sorted = np.sort(W[iu])[::-1]
    thresholds = w_sorted[np.linspace(0, len(w_sorted) - 1, n_steps).astype(int)]
    b0, b1 = [], []
    for t in thresholds:
        G = nx.Graph(); G.add_nodes_from(range(n))
        G.add_edges_from((i, j) for i, j in zip(*iu) if W[i, j] >= t)
        E = [tuple(sorted(e)) for e in G.edges()]
        T = [tuple(sorted(c)) for c in nx.enumerate_all_cliques(G) if len(c) == 3]
        eidx = {e: k for k, e in enumerate(E)}
        B1 = np.zeros((n, len(E)))
        for k, (u, v) in enumerate(E):
            B1[u, k], B1[v, k] = -1, 1
        B2 = np.zeros((len(E), len(T)))
        for k, (a, b, c) in enumerate(T):
            B2[eidx[(b, c)], k], B2[eidx[(a, c)], k], B2[eidx[(a, b)], k] = 1, -1, 1
        r1 = np.linalg.matrix_rank(B1) if len(E) else 0
        r2 = np.linalg.matrix_rank(B2) if len(T) else 0
        b0.append(n - r1); b1.append(len(E) - r1 - r2)
    density = np.array([np.mean(W[iu] >= t) for t in thresholds])
    return density, np.array(b0), np.array(b1)

n = 16
theta = 2 * np.pi * np.arange(n) / n
D = np.abs(np.subtract.outer(theta, theta)); D = np.minimum(D, 2 * np.pi - D)
rng = np.random.default_rng(0)
W_ring = np.exp(-D / 0.4) + 0.01 * rng.random((n, n)); W_ring = (W_ring + W_ring.T) / 2
np.fill_diagonal(W_ring, 0)
iu = np.triu_indices(n, 1)
W_shuf = np.zeros_like(W_ring); W_shuf[iu] = rng.permutation(W_ring[iu]); W_shuf += W_shuf.T

d1, b0r, b1r = betti_curve(W_ring)
d2, b0s, b1s = betti_curve(W_shuf)
print(f"环状网络：beta_1 = 1 持续的密度区间长度 ≈ {np.sum(b1r == 1) / len(b1r):.2f}（占过滤步数比例），"
      f"beta_1 最大值 {b1r.max()}")
print(f"打乱权重：beta_1 最大值 {b1s.max()}，出现在密度 {d2[np.argmax(b1s)]:.2f}")

fig, ax = plt.subplots(1, 2, figsize=(8, 3), sharey=True)
for a, d, b0, b1, ttl in [(ax[0], d1, b0r, b1r, "ring geometry"), (ax[1], d2, b0s, b1s, "shuffled weights")]:
    a.step(d, b0, where="post", label=r"$\beta_0$"); a.step(d, b1, where="post", label=r"$\beta_1$")
    a.set_xlabel("edge density"); a.set_title(ttl); a.legend()
ax[0].set_ylabel("Betti number")
plt.tight_layout(); plt.show()

# %% 示例：时间网络——时间一致路径与聚合网络的可达性
# 用接触序列 (u, v, t) 表示时间网络。若信息只能沿时间递增的接触传播（时间一致路径），
# 那么聚合网络（忽略时间）上可达的节点对，在时间网络上未必可达。
# 本例生成 30 个节点的模拟接触数据，比较：(1) 聚合网络的可达节点对比例；
# (2) 时间网络的可达比例；(3) 随机打乱接触时间戳（保留谁和谁接触、改变顺序）后的可达比例。
# 同时计算节点间接触间隔的阵发性 B = (σ - μ)/(σ + μ)：泊松过程约为 0，阵发性越强越接近 1。
# 解读：聚合网络会高估传播可达性；打乱时间戳是常用的零模型，用来判断时间顺序本身是否重要——
# 这里原始数据的可达比例低于打乱后的比例，说明接触的先后顺序与阵发性限制了传播路径。
import numpy as np
import networkx as nx

def temporal_reach(contacts, n):
    """按时间顺序扫描接触，返回可达矩阵 R[i, j]：i 出发的信息能否沿时间一致路径到达 j。"""
    R = np.eye(n, dtype=bool)
    for u, v, t in sorted(contacts, key=lambda x: x[2]):
        # 同一时刻的接触按顺序处理（简化处理）；无向接触双向传递
        new_u, new_v = R[:, u] | R[:, v], R[:, u] | R[:, v]
        R[:, u], R[:, v] = new_u, new_v
    return R

rng = np.random.default_rng(42)
n, T = 30, 1000
# 接触对来自一个连通的稀疏网络；每对节点在 1–3 个随机“活跃期”内各接触数次（阵发性）
pairs = list(nx.connected_watts_strogatz_graph(n, 4, 0.2, seed=1).edges())
contacts = []
for u, v in pairs:
    for c in rng.uniform(0, T, rng.integers(1, 4)):
        contacts += [(u, v, float(t)) for t in np.clip(c + rng.normal(0, 5, rng.integers(1, 4)), 0, T)]
times = np.array([t for _, _, t in contacts])
print(f"{n} 个节点，{len(pairs)} 个接触对，{len(contacts)} 次接触")

G = nx.Graph([(u, v) for u, v, _ in contacts]); G.add_nodes_from(range(n))
agg = np.mean([[nx.has_path(G, i, j) for j in range(n)] for i in range(n)])
R = temporal_reach(contacts, n)
shuffled = [(u, v, t) for (u, v, _), t in zip(contacts, rng.permutation(times))]
Rs = temporal_reach(shuffled, n)
print(f"可达节点对比例：聚合网络 {agg:.2f}，时间网络 {R.mean():.2f}，打乱时间戳 {Rs.mean():.2f}")

def burstiness(ts):
    dt = np.diff(np.sort(ts))
    return (dt.std() - dt.mean()) / (dt.std() + dt.mean())

ts_all = np.sort(times)
pois = np.sort(rng.uniform(0, T, len(times)))
print(f"全体接触的阵发性 B = {burstiness(ts_all):.2f}；同样数量的泊松接触 B = {burstiness(pois):.2f}")

# 作图：三种可达比例；接触间隔分布（阵发 vs 泊松）
import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 2, figsize=(10, 4))
ax[0].bar(["aggregated\nnetwork", "temporal\n(time-respecting)", "shuffled\ntimestamps"],
          [agg, R.mean(), Rs.mean()], color=["0.6", "C3", "C0"])
ax[0].set_ylabel("fraction of reachable node pairs"); ax[0].set_ylim(0, 1.05)
ax[0].set_title("Aggregation overestimates reachability", fontsize=10)
bins = np.logspace(-3, 2, 30)
ax[1].hist(np.diff(ts_all), bins=bins, alpha=0.6, label=f"observed contacts (B = {burstiness(ts_all):.2f})")
ax[1].hist(np.diff(pois), bins=bins, alpha=0.6, label=f"Poisson (B = {burstiness(pois):.2f})")
ax[1].set_xscale("log"); ax[1].set_xlabel("inter-contact time"); ax[1].set_ylabel("count"); ax[1].legend(fontsize=8)
ax[1].set_title("Inter-contact times: observed vs Poisson", fontsize=10)
plt.tight_layout(); plt.show()

# %% 示例：多层网络的超拉普拉斯矩阵与层间耦合
# 两层多重网络（multiplex）共享 50 个节点：第 1 层是稀疏 ER 网络，第 2 层是 WS 小世界网络。
# 超拉普拉斯矩阵 L = [[L1 + Dx I, -Dx I], [-Dx I, L2 + Dx I]]，Dx 为层间扩散系数。
# 其第二小特征值 λ2 决定扩散趋于平衡的速度。Gómez 等（2013）指出：Dx 很小时 λ2 ≈ 2Dx，
# 受层间耦合限制；Dx 很大时 λ2 趋近于聚合拉普拉斯 (L1 + L2)/2 的 λ2，可以超过单独任一层的 λ2。
# 解读：观察 λ2 随 Dx 的变化，以及大 Dx 下是否出现比两层都快的“超扩散”。
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

n = 50
G1 = nx.gnm_random_graph(n, 70, seed=1)
comps = [min(c) for c in nx.connected_components(G1)]
G1.add_edges_from(zip(comps[:-1], comps[1:]))          # 把各连通分支串起来，保证连通
G2 = nx.connected_watts_strogatz_graph(n, 4, 0.05, seed=2)
L1 = nx.laplacian_matrix(G1, nodelist=range(n)).toarray().astype(float)
L2 = nx.laplacian_matrix(G2, nodelist=range(n)).toarray().astype(float)
lam2 = lambda L: np.sort(np.linalg.eigvalsh(L))[1]
I = np.eye(n)
Dxs = np.logspace(-2, 2, 30)
sup = [lam2(np.block([[L1 + d * I, -d * I], [-d * I, L2 + d * I]])) for d in Dxs]
print(f"λ2(层1) = {lam2(L1):.3f}，λ2(层2) = {lam2(L2):.3f}，λ2((L1+L2)/2) = {lam2((L1 + L2) / 2):.3f}")
print(f"Dx = 0.01 时 λ2(超拉普拉斯) = {sup[0]:.4f}（≈ 2Dx = 0.02）；Dx = 100 时 = {sup[-1]:.3f}")

plt.figure(figsize=(5, 3))
plt.loglog(Dxs, sup, "o-", ms=3, label="supra-Laplacian")
plt.axhline(lam2(L1), ls="--", c="C1", label="layer 1 alone")
plt.axhline(lam2(L2), ls="--", c="C2", label="layer 2 alone")
plt.axhline(lam2((L1 + L2) / 2), ls=":", c="k", label="(L1+L2)/2")
plt.xlabel("inter-layer coupling $D_x$"); plt.ylabel(r"$\lambda_2$")
plt.legend(fontsize=7); plt.tight_layout(); plt.show()

# %% 示例：节点嵌入——谱嵌入、node2vec 式随机游走嵌入与简单基线的链接预测比较
# 从空手道网络中随机隐藏 15% 的边作为测试正例，并抽同样数量的非边作为负例；只在剩余网络上学习。
# (1) 拉普拉斯特征映射：对称归一化拉普拉斯最小的非零特征向量作为 d 维坐标；
# (2) node2vec 式嵌入：二阶有偏随机游走（返回参数 p、进出参数 q），统计窗口内共现，
#     做正点互信息（PPMI）矩阵并截断 SVD——这与 DeepWalk/skip-gram 的矩阵分解解释相对应（Qiu 等 2018）；
# (3) 基线：共同邻居数、Adamic–Adar 指数。打分用嵌入向量的内积，评价用 AUC。
# 解读：比较的是 10 次随机划分的均值 ± 标准差；方法之间的差距要和划分间的波动对照着看。
# 任何嵌入方法都要和共同邻居这类无需训练的基线比较，且测试边不能参与嵌入的学习（否则就是泄漏）。
import numpy as np
import networkx as nx

def auc(pos, neg):
    pos, neg = np.asarray(pos), np.asarray(neg)
    return (np.sum(pos[:, None] > neg[None, :]) + 0.5 * np.sum(pos[:, None] == neg[None, :])) / (len(pos) * len(neg))

def node2vec_walks(G, num_walks, length, p, q, rng):
    nbrs = {v: list(G.neighbors(v)) for v in G}
    walks = []
    for _ in range(num_walks):
        for s in rng.permutation(list(G.nodes())):
            walk = [s]
            while len(walk) < length and nbrs[walk[-1]]:
                cur = walk[-1]
                if len(walk) == 1:
                    walk.append(rng.choice(nbrs[cur])); continue
                prev = walk[-2]
                w = np.array([1 / p if x == prev else (1.0 if G.has_edge(x, prev) else 1 / q) for x in nbrs[cur]])
                walk.append(nbrs[cur][rng.choice(len(w), p=w / w.sum())])
            walks.append(walk)
    return walks

def ppmi_svd_embedding(G, dim, rng, p=1.0, q=1.0, window=3):
    n = G.number_of_nodes()
    C = np.zeros((n, n))
    for walk in node2vec_walks(G, 20, 20, p, q, rng):
        for i, u in enumerate(walk):
            for v in walk[max(0, i - window): i] + walk[i + 1: i + 1 + window]:
                C[u, v] += 1
    total = C.sum(); row = C.sum(1, keepdims=True); col = C.sum(0, keepdims=True)
    with np.errstate(divide="ignore", invalid="ignore"):
        pmi = np.log(C * total / (row * col))
    M = np.where(np.isfinite(pmi) & (pmi > 0), pmi, 0.0)
    U, S, _ = np.linalg.svd(M)
    return U[:, :dim] * np.sqrt(S[:dim])

def spectral_embedding(G, dim):
    L = nx.normalized_laplacian_matrix(G, nodelist=range(G.number_of_nodes())).toarray()
    vals, vecs = np.linalg.eigh(L)
    return vecs[:, 1:dim + 1]

G = nx.karate_club_graph()
edges, non_edges = list(G.edges()), list(nx.non_edges(G))
results = {k: [] for k in ["谱嵌入（内积）", "node2vec 式 PPMI-SVD（内积）", "共同邻居", "Adamic–Adar"]}
for split in range(10):                                   # 10 次随机划分：单次划分的测试边太少，波动很大
    rng = np.random.default_rng(split)
    test_pos = [edges[i] for i in rng.choice(len(edges), int(0.15 * len(edges)), replace=False)]
    test_neg = [non_edges[i] for i in rng.choice(len(non_edges), len(test_pos), replace=False)]
    G_train = G.copy(); G_train.remove_edges_from(test_pos)
    Z_spec = spectral_embedding(G_train, 4)
    Z_n2v = ppmi_svd_embedding(G_train, 8, rng, p=1.0, q=0.5)
    scores = {
        "谱嵌入（内积）": lambda u, v: Z_spec[u] @ Z_spec[v],
        "node2vec 式 PPMI-SVD（内积）": lambda u, v: Z_n2v[u] @ Z_n2v[v],
        "共同邻居": lambda u, v: len(list(nx.common_neighbors(G_train, u, v))),
        "Adamic–Adar": lambda u, v: next(nx.adamic_adar_index(G_train, [(u, v)]))[2],
    }
    for name, f in scores.items():
        results[name].append(auc([f(u, v) for u, v in test_pos], [f(u, v) for u, v in test_neg]))
print(f"每次划分：测试正例 {len(test_pos)} 条、负例 {len(test_neg)} 条；共 10 次划分")
for name, r in results.items():
    print(f"{name:28s} AUC = {np.mean(r):.3f} ± {np.std(r):.3f}")

# 作图：10 次随机划分的 AUC（点）与均值（横线）
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(6.4, 4.2))
en = ["spectral\nembedding", "node2vec-style\nPPMI-SVD", "common\nneighbors", "Adamic-Adar"]
for j, r in enumerate(results.values()):
    ax.plot(np.full(10, j) + np.linspace(-0.15, 0.15, 10), r, "o", alpha=0.6, ms=5)
    ax.hlines(np.mean(r), j - 0.25, j + 0.25, color="k", lw=2)
ax.axhline(0.5, color="gray", ls="--", label="chance")
ax.set_xticks(range(4)); ax.set_xticklabels(en); ax.set_ylabel("link-prediction AUC"); ax.legend(fontsize=8)
ax.set_title("Split-to-split spread is as large as method differences", fontsize=10)
plt.tight_layout(); plt.show()

# %% 示例：从零实现两层图卷积网络（GCN）做半监督节点分类，并与标签传播比较
# 传播矩阵 Â = D̃^{-1/2}(A + I)D̃^{-1/2}；模型 softmax(Â ReLU(Â X W1) W2)，X 取单位矩阵（无节点特征）。
# 只给每个俱乐部各 2 个已标注节点，用全批量梯度下降（手写反向传播）训练 200 步，
# 在其余 30 个节点上计算准确率；再与简单的标签传播（无参数）比较，并重复 10 个随机种子。
# 解读：在这个只有拓扑信息的小例子里，GCN 并不比标签传播更准——GCN 的优势通常来自丰富的节点特征。
import numpy as np
import networkx as nx

G = nx.karate_club_graph()
n = G.number_of_nodes()
y = np.array([0 if G.nodes[v]["club"] == "Mr. Hi" else 1 for v in range(n)])
A = nx.to_numpy_array(G, nodelist=range(n)); A = (A > 0).astype(float)
At = A + np.eye(n); d = At.sum(1)
Ahat = At / np.sqrt(np.outer(d, d))

def train_gcn(labeled, seed, hidden=8, lr=0.2, epochs=200, wd=5e-4):
    rng = np.random.default_rng(seed)
    X = np.eye(n)
    W1 = rng.normal(0, np.sqrt(2 / n), (n, hidden)); W2 = rng.normal(0, np.sqrt(2 / hidden), (hidden, 2))
    Y = np.eye(2)[y]; mask = np.zeros(n); mask[labeled] = 1
    AX = Ahat @ X
    for _ in range(epochs):
        Z1 = AX @ W1; H1 = np.maximum(Z1, 0); Z2 = Ahat @ H1 @ W2
        P = np.exp(Z2 - Z2.max(1, keepdims=True)); P /= P.sum(1, keepdims=True)
        G2 = (P - Y) * mask[:, None] / mask.sum()            # dLoss/dZ2（只对已标注节点计损失）
        gW2 = (Ahat @ H1).T @ G2 + wd * W2
        G1 = (Ahat.T @ G2 @ W2.T) * (Z1 > 0)
        gW1 = AX.T @ G1 + wd * W1
        W1 -= lr * gW1; W2 -= lr * gW2
    return P.argmax(1)

def label_propagation(labeled, alpha=0.9, iters=100):
    F0 = np.zeros((n, 2)); F0[labeled, y[labeled]] = 1
    S = A / np.sqrt(np.outer(A.sum(1), A.sum(1)))
    F = F0.copy()
    for _ in range(iters):
        F = alpha * S @ F + (1 - alpha) * F0
    return F.argmax(1)

acc_gcn, acc_lp = [], []
for seed in range(10):
    rng = np.random.default_rng(seed)
    labeled = np.concatenate([rng.choice(np.where(y == c)[0], 2, replace=False) for c in (0, 1)])
    test = np.setdiff1d(np.arange(n), labeled)
    acc_gcn.append(np.mean(train_gcn(labeled, seed)[test] == y[test]))
    acc_lp.append(np.mean(label_propagation(labeled)[test] == y[test]))
print(f"GCN 准确率：{np.mean(acc_gcn):.2f} ± {np.std(acc_gcn):.2f}；"
      f"标签传播：{np.mean(acc_lp):.2f} ± {np.std(acc_lp):.2f}（10 个随机标注集）")

# 作图：同一标注集下两种方法的准确率（连线配对）
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(6.4, 4.2))
for a_, b_ in zip(acc_gcn, acc_lp):
    ax.plot([0, 1], [a_, b_], "-", color="0.7", lw=1)
ax.plot(np.zeros(10), acc_gcn, "o", color="C0", label="GCN")
ax.plot(np.ones(10), acc_lp, "s", color="C1", label="label propagation")
ax.set_xticks([0, 1]); ax.set_xticklabels(["GCN (2 layers)", "label propagation"]); ax.set_xlim(-0.5, 1.5)
ax.set_ylabel("test accuracy (30 unlabeled nodes)"); ax.set_ylim(0, 1.05)
ax.set_title("2 labels per class: no gain from GCN without features", fontsize=10)
plt.tight_layout(); plt.show()

# %% 示例：过平滑——反复做图卷积后节点表示趋于一致
# 对 BA 网络（200 个节点）的随机节点特征 X 反复左乘传播矩阵 Â（不加权重和非线性），
# 记录第 k 层表示的“节点间差异”：每列特征减去其按 sqrt(度) 加权的投影后剩余部分的相对大小。
# Â 的最大特征值为 1，对应特征向量与 sqrt(d̃) 成正比，其余特征值的绝对值小于 1，
# 所以 Â^k X 收敛到只由度决定的秩 1 结构，节点之间的可区分信息指数衰减（Li 等 2018）。
# 解读：这解释了为什么 GCN 一般只用 2–3 层，以及残差连接、跳跃连接等改进的动机。
import numpy as np
import networkx as nx

G = nx.barabasi_albert_graph(200, 3, seed=0)
A = nx.to_numpy_array(G); At = A + np.eye(len(A)); d = At.sum(1)
Ahat = At / np.sqrt(np.outer(d, d))
u = np.sqrt(d) / np.linalg.norm(np.sqrt(d))          # Â 的主特征向量
X = np.random.default_rng(0).normal(size=(len(A), 16))
H = X.copy()
for k in range(0, 33):
    if k in (0, 1, 2, 4, 8, 16, 32):
        resid = H - np.outer(u, u @ H)
        print(f"k = {k:2d}：去除主方向后的相对范数 = {np.linalg.norm(resid) / np.linalg.norm(H):.4f}")
    H = Ahat @ H
ev = np.sort(np.abs(np.linalg.eigvalsh(Ahat)))[::-1]
print(f"Â 的最大特征值 = {ev[0]:.3f}，次大绝对值 = {ev[1]:.3f}（决定衰减速度）")

# 作图：去除主方向后的相对范数随传播层数 k 衰减，并与 |lambda_2|^k 对照
import matplotlib.pyplot as plt
H = X.copy(); rel = []
for k in range(33):
    rel.append(np.linalg.norm(H - np.outer(u, u @ H)) / np.linalg.norm(H)); H = Ahat @ H
fig, ax = plt.subplots(figsize=(6.4, 4.2))
ks = np.arange(33)
ax.semilogy(ks, rel, "o-", ms=4, label="relative norm after removing sqrt(d) direction")
ax.semilogy(ks, rel[0] * ev[1] ** ks, "k--", label=f"|lambda_2|^k  (|lambda_2| = {ev[1]:.3f})")
ax.set_xlabel("number of propagation layers k"); ax.set_ylabel("distinguishable signal (relative)")
ax.set_title("Over-smoothing: node features collapse exponentially", fontsize=10); ax.legend(fontsize=8)
plt.tight_layout(); plt.show()
