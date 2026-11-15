# 依赖：networkx>=3, numpy, scipy, matplotlib
# 数据：Zachary 空手道俱乐部网络（NetworkX 内置 karate_club_graph()，34 个节点、78 条边；
#       边属性 weight 为两人共同参与的活动情境数，除加权示例外按无权网络处理）；
#       有向小图、ER 随机网络均由代码生成，固定随机种子以便复现。
# 说明：各单元相互独立，可单独运行；规模较大的 ER 模拟（N 达 2×10^5）在普通笔记本上需数秒。

# %% 示例：度、平均度、密度与度分布
# 用公式 <k> = 2M/N 与 ρ = 2M/(N(N-1)) 计算平均度和密度，并用 nx.density 核对；
# 再计算最大度与平均度之比，画出度分布直方图 P(k)。
# 输出：平均度约 4.6，密度约 0.14；度分布右偏，度最大的是节点 33 与节点 0（俱乐部的两位核心人物）。
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

G = nx.karate_club_graph()
N, M = G.number_of_nodes(), G.number_of_edges()
deg = np.array([d for _, d in G.degree()])

k_mean = 2 * M / N
rho = 2 * M / (N * (N - 1))
print("N=%d, M=%d, 平均度=%.2f, 密度=%.3f, nx.density=%.3f" % (N, M, k_mean, rho, nx.density(G)))
print("最大度 = %d（节点 %d），最大度/平均度 = %.1f" % (deg.max(), deg.argmax(), deg.max() / k_mean))
print("度最大的 3 个节点:", sorted(G.degree(), key=lambda x: -x[1])[:3])

ks, counts = np.unique(deg, return_counts=True)
plt.bar(ks, counts / N)
plt.xlabel("degree k")
plt.ylabel("P(k)")
plt.title("Karate club degree distribution")
plt.show()


# %% 示例：用广度优先搜索（BFS）求最短路径距离
# 用队列实现 BFS，求从源点 0 到所有节点的距离，并与 NetworkX 的结果对比；
# 按距离把节点分层输出，可以看到 BFS “一层一层”向外扩散。
# 最后计算整个网络的直径与平均路径长度（空手道网络是连通的，可直接计算）。
# 输出：自己的结果与 NetworkX 完全一致；直径为 5，平均路径长度约 2.41。
import networkx as nx
from collections import deque

G = nx.karate_club_graph()


def bfs_distances(G, source):
    dist = {source: 0}
    queue = deque([source])
    while queue:
        v = queue.popleft()
        for u in G.neighbors(v):
            if u not in dist:
                dist[u] = dist[v] + 1
                queue.append(u)
    return dist


my = bfs_distances(G, 0)
ref = nx.single_source_shortest_path_length(G, 0)
print("与 NetworkX 一致吗？", my == dict(ref))
layers = {}
for node, d in my.items():
    layers.setdefault(d, []).append(node)
for d in sorted(layers):
    print("距离 %d 的节点: %s" % (d, sorted(layers[d])))
print("直径 =", nx.diameter(G), "，平均路径长度 = %.3f" % nx.average_shortest_path_length(G))

# 作图：节点按到源点 0 的 BFS 距离着色，可见“一层一层”向外扩散
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(6.4, 4.2))
pos = nx.spring_layout(G, seed=4)
nx.draw_networkx_edges(G, pos, ax=ax, edge_color="0.7", alpha=0.4)
nc = nx.draw_networkx_nodes(G, pos, ax=ax, node_color=[my[v] for v in G], cmap=plt.get_cmap("viridis_r", max(my.values()) + 1), vmin=-0.5, vmax=max(my.values()) + 0.5,
                            node_size=[200 if v == 0 else 90 for v in G], edgecolors="0.3", linewidths=0.5)
fig.colorbar(nc, ax=ax, ticks=range(max(my.values()) + 1), label="BFS distance from node 0")
ax.set_title("BFS layers from node 0 (diameter = %d)" % nx.diameter(G))
ax.axis("off"); plt.tight_layout(); plt.show()


# %% 示例：局部聚集系数、平均聚集系数与传递性
# 手工计算节点 0 的局部聚集系数 C_i = 2 e_i / (k_i (k_i - 1))（e_i 为邻居之间的边数），与 nx.clustering 对比；
# 再比较平均聚集系数（节点等权）与传递性（按连通三元组加权）——两者数值不同。
# 最后画出各节点的度与 C_i 的散点图：高度节点的 C_i 普遍较低，与 C(k) 随 k 下降的规律一致。
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations

G = nx.karate_club_graph()
i = 0
nbrs = list(G.neighbors(i))
k = len(nbrs)
e_i = sum(1 for u, v in combinations(nbrs, 2) if G.has_edge(u, v))
C_i = 2 * e_i / (k * (k - 1))
print("节点 %d: 度=%d, 邻居间边数=%d, C_i=%.3f, NetworkX=%.3f" % (i, k, e_i, C_i, nx.clustering(G, i)))
print("平均聚集系数 = %.3f" % nx.average_clustering(G))
print("传递性       = %.3f" % nx.transitivity(G))

deg = dict(G.degree())
clu = nx.clustering(G)
x = np.array([deg[n] for n in G])
y = np.array([clu[n] for n in G])
print("度 <= 4 的节点平均 C_i = %.3f；度 >= 10 的节点平均 C_i = %.3f" % (y[x <= 4].mean(), y[x >= 10].mean()))
plt.scatter(x, y)
plt.xlabel("degree k")
plt.ylabel("local clustering C_i")
plt.title("Clustering vs degree (karate club)")
plt.show()


# %% 示例：全局效率与局部效率
# 全局效率 E_glob = 平均 1/d_ij（不连通点对贡献 0），局部效率 E_loc(i) = 节点 i 的邻居子图（去掉 i）的全局效率。
# 先在空手道网络上手工实现两者并与 nx.global_efficiency / nx.local_efficiency 核对；
# 再把网络拆成不连通的两半，说明此时平均路径长度无定义而全局效率仍可计算。
# 输出：手工值与 NetworkX 一致；E_glob 约 0.49（与 1/L≈0.42 同量级但不相等），E_loc 约 0.65，
#       平均聚集系数约 0.57；
#       删掉若干边使网络断开后，nx.average_shortest_path_length 报错，而全局效率下降但仍有限。
import networkx as nx
import numpy as np

G = nx.karate_club_graph()


def global_eff(H):
    n = H.number_of_nodes()
    if n < 2:
        return 0.0
    tot = 0.0
    for s, dist in nx.all_pairs_shortest_path_length(H):
        tot += sum(1.0 / d for t, d in dist.items() if t != s)
    return tot / (n * (n - 1))


def local_eff(H):
    return np.mean([global_eff(H.subgraph(list(H.neighbors(i)))) for i in H])


print("E_glob: 手工 %.4f, NetworkX %.4f" % (global_eff(G), nx.global_efficiency(G)))
print("E_loc : 手工 %.4f, NetworkX %.4f" % (local_eff(G), nx.local_efficiency(G)))
print("平均聚集系数 C = %.4f；1/L = %.4f" % (nx.average_clustering(G), 1 / nx.average_shortest_path_length(G)))

H = G.copy()
H.remove_edges_from(nx.minimum_edge_cut(H, 0, 33))      # 切断两位核心人物之间的所有路径
print("切边后连通分支数 =", nx.number_connected_components(H))
try:
    nx.average_shortest_path_length(H)
except nx.NetworkXError as e:
    print("平均路径长度：报错 ->", e)
print("切边后全局效率 = %.4f" % nx.global_efficiency(H))

# 作图：左为各指标对比，右为切边后的网络（红色虚线 = 被删除的边，节点按连通分支着色）
import matplotlib.pyplot as plt

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
vals = {"E_glob": nx.global_efficiency(G), "1/L": 1 / nx.average_shortest_path_length(G),
        "E_loc": nx.local_efficiency(G), "C": nx.average_clustering(G), "E_glob\n(after cut)": nx.global_efficiency(H)}
ax1.bar(list(vals), list(vals.values()), color=["#4393c3"] * 4 + ["#d6604d"])
for i, v in enumerate(vals.values()):
    ax1.text(i, v + 0.01, "%.3f" % v, ha="center", fontsize=9)
ax1.set_ylabel("value"); ax1.set_title("Efficiency stays finite after disconnection", fontsize=10)
pos = nx.spring_layout(G, seed=4)
comp = {v: i for i, cc in enumerate(nx.connected_components(H)) for v in cc}
cut = [e for e in G.edges() if not H.has_edge(*e)]
nx.draw_networkx_edges(H, pos, ax=ax2, edge_color="0.7", alpha=0.4)
nx.draw_networkx_edges(G, pos, ax=ax2, edgelist=cut, edge_color="#d6604d", style="--", width=1.5)
nx.draw_networkx_nodes(H, pos, ax=ax2, node_size=70, node_color=[comp[v] for v in H], cmap="coolwarm")
ax2.set_title("%d edges cut between nodes 0 and 33" % len(cut), fontsize=10); ax2.axis("off")
plt.tight_layout(); plt.show()


# %% 示例：加权网络的强度、加权聚集系数与加权最短路径
# 空手道网络的边属性 weight 记录两人共同参与活动的情境数（Zachary 1977），视为“连接强度”。
# (1) 强度 s_i = Σ_j w_ij；(2) Onnela 加权聚集系数（几何平均，NetworkX 的默认加权定义）与
#     Barrat 加权聚集系数（手工实现）；(3) 把强度转换为长度 l = 1/w 后用 Dijkstra 求加权距离，
#     并演示“直接把强度当长度”会得到错误的最短路径。
# 输出：强度与度高度相关但排序不完全相同；两种加权聚集系数与无权值不同；
#       两种长度定义下 0→33 的最短路径不同。
import networkx as nx
import numpy as np
from itertools import permutations

G = nx.karate_club_graph()
deg = dict(G.degree())
s = dict(G.degree(weight="weight"))
print("强度最大的 5 个节点:", sorted(s, key=s.get, reverse=True)[:5])
print("度最大的 5 个节点:  ", sorted(deg, key=deg.get, reverse=True)[:5])
print("度与强度的相关系数 r = %.3f" % np.corrcoef([deg[i] for i in G], [s[i] for i in G])[0, 1])


def barrat_clustering(G, i, weight="weight"):
    k = G.degree(i)
    if k < 2:
        return 0.0
    si = G.degree(i, weight=weight)
    tot = 0.0
    for j, h in permutations(G.neighbors(i), 2):   # 有序邻居对
        if G.has_edge(j, h):
            tot += (G[i][j][weight] + G[i][h][weight]) / 2
    return tot / (si * (k - 1))


for i in [0, 33, 2]:
    print("节点 %2d: 无权 C=%.3f, Onnela C_w=%.3f, Barrat C_w=%.3f"
          % (i, nx.clustering(G, i), nx.clustering(G, i, weight="weight"), barrat_clustering(G, i)))

for u, v, d in G.edges(data=True):
    d["length"] = 1.0 / d["weight"]              # 强度 -> 长度
p_right = nx.dijkstra_path(G, 0, 33, weight="length")
p_wrong = nx.dijkstra_path(G, 0, 33, weight="weight")   # 错误：把强度当长度
print("正确（l=1/w）最短路径:", p_right, "边强度", [G[a][b]["weight"] for a, b in zip(p_right, p_right[1:])])
print("错误（l=w）  最短路径:", p_wrong, "边强度", [G[a][b]["weight"] for a, b in zip(p_wrong, p_wrong[1:])])

# 作图：左为度–强度散点；右为边宽 ∝ 权重的网络，绿色为正确最短路径，红色虚线为错误路径
import matplotlib.pyplot as plt

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
ax1.scatter([deg[i] for i in G], [s[i] for i in G], s=40, color="#4393c3", alpha=0.8)
for i in [0, 33, 2]:
    ax1.annotate(str(i), (deg[i], s[i]), textcoords="offset points", xytext=(4, 4), fontsize=9)
ax1.set_xlabel("degree k"); ax1.set_ylabel("strength s")
ax1.set_title("Strength vs degree (r = %.2f)" % np.corrcoef([deg[i] for i in G], [s[i] for i in G])[0, 1], fontsize=10)
pos = nx.spring_layout(G, seed=4)
nx.draw_networkx_edges(G, pos, ax=ax2, edge_color="0.6", alpha=0.4, width=[0.5 * d["weight"] for _, _, d in G.edges(data=True)])
for pth, col, ls, lab in [(p_right, "#1b7837", "-", "l = 1/w (correct)"), (p_wrong, "#b2182b", "--", "l = w (wrong)")]:
    nx.draw_networkx_edges(G, pos, ax=ax2, edgelist=list(zip(pth, pth[1:])), edge_color=col, style=ls, width=2.5)
    ax2.plot([], [], color=col, ls=ls, lw=2.5, label=lab)
nx.draw_networkx_nodes(G, pos, ax=ax2, node_size=60, node_color="#bdbdbd")
nx.draw_networkx_labels(G, pos, ax=ax2, labels={0: "0", 33: "33"}, font_size=9)
ax2.legend(fontsize=8, loc="lower left"); ax2.set_title("Shortest path 0 -> 33", fontsize=10); ax2.axis("off")
plt.tight_layout(); plt.show()


# %% 示例：中心性家族在同一网络上的比较
# 在空手道网络（无权）上计算 8 种中心性：度、接近、调和接近、介数、特征向量、Katz、PageRank、k 核数，
# 列出各指标排名前 5 的节点，并计算它们两两之间的 Spearman 秩相关。
# 先用两个可手算的小图核对定义：星形图中心的归一化介数为 1；路径图 1-2-3-4-5 中节点 3 的介数为 4。
# 输出：多数指标都把节点 0、33 排在前列，但第 3–5 名各不相同（k 核数有大量并列，前 5 名只是并列者之一）；
#       与度的秩相关在 0.78–0.98 之间，说明各指标高度相关却不可互换，选哪一个取决于研究问题。
import networkx as nx
import numpy as np
from scipy.stats import spearmanr

star = nx.star_graph(4)                     # 中心 0 + 4 个叶子
path = nx.path_graph([1, 2, 3, 4, 5])
print("星形图中心介数（归一化）=", nx.betweenness_centrality(star)[0],
      "；叶子接近中心性 = %.3f（手算 4/7=%.3f）" % (nx.closeness_centrality(star)[1], 4 / 7))
print("路径图未归一化介数:", nx.betweenness_centrality(path, normalized=False))

G = nx.karate_club_graph()
lam1 = max(np.linalg.eigvalsh(nx.to_numpy_array(G, weight=None)))
C = {
    "degree": nx.degree_centrality(G),
    "closeness": nx.closeness_centrality(G),
    "harmonic": nx.harmonic_centrality(G),
    "betweenness": nx.betweenness_centrality(G),
    "eigenvector": nx.eigenvector_centrality_numpy(G, weight=None),
    "katz": nx.katz_centrality_numpy(G, alpha=0.5 / lam1, beta=1.0, weight=None),
    "pagerank": nx.pagerank(G, alpha=0.85, weight=None),
    "k-core": nx.core_number(G),
}
print("最大特征值 λ1 = %.3f，Katz 取 α = 0.5/λ1 = %.4f" % (lam1, 0.5 / lam1))
for name, c in C.items():
    print("%-12s 前 5: %s" % (name, sorted(c, key=c.get, reverse=True)[:5]))

names = list(C)
X = np.array([[C[m][i] for i in G] for m in names])
rho = spearmanr(X.T).correlation
print("\n与度中心性的 Spearman 秩相关：")
for m, r in zip(names, rho[0]):
    print("  %-12s %.2f" % (m, r))

# 作图：8 种中心性两两之间的 Spearman 秩相关热图
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(6.4, 5.2))
im = ax.imshow(rho, cmap="RdBu_r", vmin=-1, vmax=1)
for i in range(len(names)):
    for j in range(len(names)):
        ax.text(j, i, "%.2f" % rho[i, j], ha="center", va="center", fontsize=8,
                color="white" if rho[i, j] > 0.8 else "black")
ax.set_xticks(range(len(names))); ax.set_xticklabels(names, rotation=45, ha="right")
ax.set_yticks(range(len(names))); ax.set_yticklabels(names)
fig.colorbar(im, ax=ax, label="Spearman rho")
ax.set_title("Centralities correlate but are not interchangeable", fontsize=10)
plt.tight_layout(); plt.show()


# %% 示例：用 Brandes 算法手工计算介数中心性
# Brandes（2001）：对每个源点 s 做一次 BFS，记录最短路径条数 σ_sv 与前驱；再按距离从远到近回溯，
# 累加依赖度 δ_s(v) = Σ_{w: v 是 w 的前驱} σ_sv/σ_sw · (1 + δ_s(w))。总代价 O(NM)。
# 无向图中每对节点被两个源点各计一次，最后除以 2。输出：与 nx.betweenness_centrality 完全一致。
import networkx as nx
from collections import deque


def brandes_betweenness(G):
    bc = dict.fromkeys(G, 0.0)
    for s in G:
        stack, pred = [], {v: [] for v in G}
        sigma = dict.fromkeys(G, 0); sigma[s] = 1
        dist = dict.fromkeys(G, -1); dist[s] = 0
        Q = deque([s])
        while Q:                                   # 阶段 1：BFS 计数最短路径
            v = Q.popleft(); stack.append(v)
            for w in G.neighbors(v):
                if dist[w] < 0:
                    dist[w] = dist[v] + 1; Q.append(w)
                if dist[w] == dist[v] + 1:
                    sigma[w] += sigma[v]; pred[w].append(v)
        delta = dict.fromkeys(G, 0.0)
        while stack:                               # 阶段 2：反向累加依赖度
            w = stack.pop()
            for v in pred[w]:
                delta[v] += sigma[v] / sigma[w] * (1 + delta[w])
            if w != s:
                bc[w] += delta[w]
    return {v: b / 2 for v, b in bc.items()}      # 无向图去重


G = nx.karate_club_graph()
mine = brandes_betweenness(G)
ref = nx.betweenness_centrality(G, normalized=False)
print("与 NetworkX 最大差异 = %.2e" % max(abs(mine[v] - ref[v]) for v in G))
print("介数最大的 3 个节点:", sorted(mine, key=mine.get, reverse=True)[:3],
      [round(mine[v], 1) for v in sorted(mine, key=mine.get, reverse=True)[:3]])

# 作图：节点大小与颜色 ∝ Brandes 介数，标出介数最大的 3 个节点
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(6.4, 4.2))
pos = nx.spring_layout(G, seed=4)
bvals = [mine[v] for v in G]
nx.draw_networkx_edges(G, pos, ax=ax, edge_color="0.7", alpha=0.4)
nc = nx.draw_networkx_nodes(G, pos, ax=ax, node_size=[40 + 0.6 * b for b in bvals], node_color=bvals,
                            cmap="YlOrRd", edgecolors="0.4", linewidths=0.5)
top3 = sorted(mine, key=mine.get, reverse=True)[:3]
nx.draw_networkx_labels(G, pos, ax=ax, labels={v: str(v) for v in top3}, font_size=9)
fig.colorbar(nc, ax=ax, label="betweenness (unnormalized)")
ax.set_title("Brandes betweenness = NetworkX (max diff %.1e)" % max(abs(mine[v] - ref[v]) for v in G), fontsize=10)
ax.axis("off"); plt.tight_layout(); plt.show()


# %% 示例：特征向量、Katz、PageRank 与 HITS 的幂迭代实现
# 用同一个 6 节点有向小图说明谱类中心性的差别（约定 A[i, j] = 1 表示边 i -> j）：
#   特征向量中心性在有向无环部分会退化为 0；Katz 加常数项 β 解决这一问题；
#   PageRank 再按出度分摊并加随机跳转；HITS 同时给出权威值（authority）与枢纽值（hub）。
# 每种方法都用幂迭代手工实现，并与 NetworkX 核对。
# 输出：λ1 = 1（来自环 3→4→5→3）；不在环上的节点 0、1、2 特征向量中心性都为 0，
#       而在 Katz 与 PageRank 中为正，节点 0（无入边）最小；
#       HITS 中节点 0 是最强的“枢纽”，被多方指向的节点 3 是最强的“权威”。
import networkx as nx
import numpy as np

edges = [(0, 1), (0, 2), (0, 3), (1, 3), (2, 3), (3, 4), (4, 5), (5, 3), (1, 2)]
D = nx.DiGraph(edges)
nodes = sorted(D)
A = nx.to_numpy_array(D, nodelist=nodes)       # A[i, j] = 1: i -> j
N = len(nodes)


def power_iter(M, x0, n_iter=1000):
    x = x0.copy()
    for _ in range(n_iter):
        y = M @ x
        x = y / np.linalg.norm(y)
    return x


# 特征向量中心性（按入边累积）：λ x = A^T x
lam = max(abs(np.linalg.eigvals(A)))
x_eig = power_iter(A.T, np.ones(N))
print("λ1 = %.3f；特征向量中心性:" % lam, np.round(x_eig / x_eig.sum(), 3))

# Katz：x = α A^T x + β 1  =>  x = β (I - α A^T)^{-1} 1，要求 α < 1/λ1
alpha = 0.5 / lam
x_katz = np.linalg.solve(np.eye(N) - alpha * A.T, np.ones(N))
ref = nx.katz_centrality_numpy(D, alpha=alpha, beta=1.0)
print("Katz（α=%.3f）:" % alpha, np.round(x_katz / np.linalg.norm(x_katz), 3),
      " NetworkX 一致:", np.allclose(x_katz / np.linalg.norm(x_katz), [ref[v] for v in nodes]))

# PageRank：x = d A^T D_out^{-1} x + (1-d)/N；本图没有出度为 0 的节点
d = 0.85
kout = A.sum(axis=1)
P = (A / kout[:, None]).T                      # 列随机矩阵
x_pr = np.ones(N) / N
for _ in range(200):
    x_pr = d * P @ x_pr + (1 - d) / N
ref = nx.pagerank(D, alpha=d)
print("PageRank:", np.round(x_pr, 3), " NetworkX 一致:", np.allclose(x_pr, [ref[v] for v in nodes], atol=1e-6))

# HITS：a = A^T h, h = A a  =>  a ∝ A^T A a, h ∝ A A^T h
a = power_iter(A.T @ A, np.ones(N)); h = power_iter(A @ A.T, np.ones(N))
h_ref, a_ref = nx.hits(D, max_iter=1000)
print("authority:", np.round(a / a.sum(), 3), " NetworkX 一致:", np.allclose(a / a.sum(), [a_ref[v] for v in nodes], atol=1e-6))
print("hub      :", np.round(h / h.sum(), 3), " NetworkX 一致:", np.allclose(h / h.sum(), [h_ref[v] for v in nodes], atol=1e-6))

# 作图：5 种谱类中心性（各自归一化到和为 1）的分组柱状图
import matplotlib.pyplot as plt

scores = {"eigenvector": x_eig / x_eig.sum(), "Katz": x_katz / x_katz.sum(), "PageRank": x_pr,
          "authority": a / a.sum(), "hub": h / h.sum()}
fig, ax = plt.subplots(figsize=(6.4, 4.2))
w = 0.16
for j, (name, v) in enumerate(scores.items()):
    ax.bar(np.arange(N) + (j - 2) * w, v, width=w, label=name, hatch=["", "//", "", "..", "xx"][j],
           edgecolor="white" if j % 2 == 0 else "0.3")
ax.set_xticks(range(N)); ax.set_xticklabels(["node %d" % v for v in nodes])
ax.set_ylabel("score (sums to 1)"); ax.legend(fontsize=8, ncol=2)
ax.set_title("Nodes 0-2 vanish under eigenvector centrality only", fontsize=10)
plt.tight_layout(); plt.show()


# %% 示例：k 核分解（逐层剥离）
# 反复删除度 < k 的节点，直到剩余子图所有节点度 >= k，得到 k 核；节点所在最大 k 核的 k 值称为核数（coreness）。
# 这里用按当前度从小到大剥离的方法手工实现（Batagelj–Zaversnik 算法的朴素版本），与 nx.core_number 核对，
# 并打印每一层壳（k-shell）的节点数。
# 输出：空手道网络的最大核数为 4，最内核含 10 个节点（包括 0、33 等核心成员）；手工结果与 NetworkX 一致。
import networkx as nx

G = nx.karate_club_graph()


def core_number(G):
    H = G.copy()
    core, k = {}, 0
    while H.number_of_nodes() > 0:
        v, dv = min(H.degree(), key=lambda x: x[1])
        k = max(k, dv)                 # 核数单调不减
        core[v] = k
        H.remove_node(v)
    return core


mine = core_number(G)
print("与 NetworkX 一致:", mine == nx.core_number(G))
kmax = max(mine.values())
for k in range(1, kmax + 1):
    print("k-shell %d: %d 个节点" % (k, sum(1 for c in mine.values() if c == k)))
print("最内核（%d 核）成员:" % kmax, sorted(nx.k_core(G, kmax)))

# 作图：节点按核数着色，最内核节点加黑框
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(6.4, 4.2))
pos = nx.spring_layout(G, seed=4)
nx.draw_networkx_edges(G, pos, ax=ax, edge_color="0.7", alpha=0.4)
inner = set(nx.k_core(G, kmax))
nc = nx.draw_networkx_nodes(G, pos, ax=ax, node_color=[mine[v] for v in G], cmap=plt.get_cmap("Blues", kmax),
                            vmin=0.5, vmax=kmax + 0.5, node_size=[110 if v in inner else 60 for v in G],
                            edgecolors=["black" if v in inner else "0.6" for v in G])
fig.colorbar(nc, ax=ax, ticks=range(1, kmax + 1), label="coreness")
ax.set_title("k-core decomposition: %d nodes in the %d-core" % (len(inner), kmax), fontsize=10)
ax.axis("off"); plt.tight_layout(); plt.show()


# %% 示例：ER 网络的最大度与最小度（自然截断）
# 对泊松度分布，令“度 >= k_max 的期望节点数”N·P(K >= k_max) ≈ 1，“度 <= k_min 的期望节点数”≈ 1，
# 解出 k_max 与 k_min。用 Barabási《Network Science》3.B 节的设定 N = 10^9、<k> = 1000 计算，
# 再在可模拟的规模（N = 10^5, <k> = 10）上与实际生成的 ER 网络比较。
# 输出：N=10^9 时 k_max 约 1.2×10^3、k_min 约 816，都在平均度的 ±20% 以内——随机网络没有枢纽；
#       N=10^5、<k>=10 时泊松估计与模拟网络的最大度一致，最小度为 0（存在孤立节点，因为 <k> < ln N）。
import networkx as nx
import numpy as np
from scipy.stats import poisson


def natural_cutoffs(N, c):
    k = np.arange(0, int(c + 50 * np.sqrt(c) + 50))
    kmax = k[np.argmin(np.abs(N * poisson.sf(k - 1, c) - 1))]   # N·P(K >= k) ≈ 1
    kmin = k[np.argmin(np.abs(N * poisson.cdf(k, c) - 1))]      # N·P(K <= k) ≈ 1
    return kmax, kmin


print("N=1e9, <k>=1000: k_max ≈ %d, k_min ≈ %d" % natural_cutoffs(1e9, 1000))
N, c = 100_000, 10
G = nx.fast_gnp_random_graph(N, c / (N - 1), seed=1)
deg = np.array([d for _, d in G.degree()])
print("N=1e5, <k>=10: 泊松估计 k_max≈%d, k_min≈%d；模拟 k_max=%d, k_min=%d"
      % (*natural_cutoffs(N, c), deg.max(), deg.min()))

# 作图：模拟度分布与泊松分布（对数纵轴），竖线为自然截断的估计值
import matplotlib.pyplot as plt

kmax_est, kmin_est = natural_cutoffs(N, c)
ks, cnt = np.unique(deg, return_counts=True)
fig, ax = plt.subplots(figsize=(6.4, 4.2))
ax.semilogy(ks, cnt / N, "o", ms=5, label="ER simulation (N=1e5)")
kk = np.arange(0, ks.max() + 3)
ax.semilogy(kk, poisson.pmf(kk, c), "-", color="0.4", label="Poisson(<k>=10)")
ax.axhline(1 / N, color="0.6", ls=":", label="1/N")
for x, lab in [(kmax_est, "k_max est."), (kmin_est, "k_min est.")]:
    ax.axvline(x, color="#d6604d", ls="--")
    ax.text(x, 0.12, lab, rotation=90, ha="right", va="top", fontsize=8, color="#d6604d")
ax.set_xlabel("degree k"); ax.set_ylabel("P(k)"); ax.set_ylim(1e-6, 0.3); ax.legend(fontsize=8)
ax.set_title("No hubs: observed k_max = %d, k_min = %d" % (deg.max(), deg.min()), fontsize=10)
plt.tight_layout(); plt.show()


# %% 示例：ER 随机网络中巨连通分支的涌现
# N=1000，让平均度 <k> 从 0.2 增加到 4，记录最大连通分支占全部节点的比例 S，
# 并与理论曲线 S = 1 - exp(-<k> S)（用不动点迭代求解）对比。
# 输出：S 在 <k>=1 附近陡然上升，远离临界点时模拟点与理论曲线吻合；<k><1 时理论值为 0，
#       模拟值只是很小的有限规模碎片；临界点 <k>=1 处有限规模效应最强，模拟值明显高于理论极限值。
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

N = 1000
k_values = np.linspace(0.2, 4, 20)
S_sim = []
for kv in k_values:
    G = nx.fast_gnp_random_graph(N, kv / (N - 1), seed=7)
    S_sim.append(len(max(nx.connected_components(G), key=len)) / N)


def S_theory(kv, iters=200):
    S = 0.5
    for _ in range(iters):            # 不动点迭代求解 S = 1 - exp(-k S)
        S = 1 - np.exp(-kv * S)
    return S


for kv, s in zip(k_values[::4], S_sim[::4]):
    print("<k>=%.2f: 模拟 S=%.3f, 理论 S=%.3f" % (kv, s, S_theory(kv)))

plt.plot(k_values, S_sim, "o", label="simulation (N=1000)")
plt.plot(k_values, [S_theory(kv) for kv in k_values], "-", label="theory")
plt.axvline(1, ls="--", c="gray")
plt.xlabel("average degree <k>")
plt.ylabel("fraction in giant component")
plt.legend()
plt.show()


# %% 示例：ER 网络演化的四个区间
# 固定 <k>，改变 N，看最大连通分支规模 N_G 如何随 N 增长：
#   亚临界 <k>=0.5：N_G ~ ln N；临界 <k>=1：N_G ~ N^{2/3}；超临界 <k>=2：N_G ~ N（比例约 0.797）；
# 再在 N=2000 时扫描 <k>，估计“整个网络连通”的概率，验证连通阈值 <k> ≈ ln N ≈ 7.6。
# 输出：<k>=2 时 N_G/N 稳定在理论值 0.797；<k>=0.5 时 N_G/ln N 只缓慢增长（理论上有 ln ln N 修正）；
#       <k>=1 时涨落极大，N_G/N^{2/3} 在 O(1) 范围内波动；连通概率在 ln N 附近从 0 升到 1，
#       与“孤立节点数近似泊松分布”给出的 exp(-N e^{-<k>}) 相符。
import networkx as nx
import numpy as np

rng = np.random.default_rng(0)


def largest_cc(N, c, reps=5):
    sizes = []
    for _ in range(reps):
        G = nx.fast_gnp_random_graph(N, c / (N - 1), seed=int(rng.integers(1e9)))
        sizes.append(len(max(nx.connected_components(G), key=len)))
    return np.mean(sizes)


rows, conn_rows = [], []                          # 存下结果用于作图
for N in [1000, 4000, 16000, 64000]:
    a, b, c = largest_cc(N, 0.5), largest_cc(N, 1.0), largest_cc(N, 2.0)
    rows.append((N, a / np.log(N), b / N ** (2 / 3), c / N))
    print("N=%6d | <k>=0.5: N_G/lnN=%.2f | <k>=1: N_G/N^(2/3)=%.2f | <k>=2: N_G/N=%.3f"
          % (N, a / np.log(N), b / N ** (2 / 3), c / N))

N = 2000
print("ln N = %.2f" % np.log(N))
for c in [4, 6, 7, 7.6, 8, 9, 11]:
    conn = np.mean([nx.is_connected(nx.fast_gnp_random_graph(N, c / (N - 1), seed=s)) for s in range(40)])
    conn_rows.append((c, conn))
    print("<k>=%4.1f: 连通概率 %.2f（理论 exp(-N e^{-<k>}) = %.2f）" % (c, conn, np.exp(-N * np.exp(-c))))

# 作图：左为三个区间的标度比值随 N 的变化，右为连通概率随 <k> 的变化
import matplotlib.pyplot as plt

R = np.array(rows)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
for col, mk, lab in [(1, "o-", "<k>=0.5: N_G / ln N"), (2, "s--", "<k>=1: N_G / N^(2/3)"), (3, "^:", "<k>=2: N_G / N")]:
    ax1.plot(R[:, 0], R[:, col], mk, label=lab)
ax1.set_xscale("log"); ax1.set_xlabel("N"); ax1.set_ylabel("scaled giant component size"); ax1.legend(fontsize=8)
ax1.set_title("Each regime has its own scaling", fontsize=10)
cs, ps = zip(*conn_rows)
kk = np.linspace(3.5, 11.5, 100)
ax2.plot(cs, ps, "o", label="simulation (40 runs)")
ax2.plot(kk, np.exp(-N * np.exp(-kk)), "-", color="0.4", label="exp(-N e^{-<k>})")
ax2.axvline(np.log(N), color="#d6604d", ls="--", label="ln N = %.1f" % np.log(N))
ax2.set_xlabel("average degree <k>"); ax2.set_ylabel("P(connected)"); ax2.legend(fontsize=8)
ax2.set_title("Connectivity threshold at <k> ~ ln N (N = %d)" % N, fontsize=10)
plt.tight_layout(); plt.show()


# %% 示例：临界点处的分支大小分布 p_s ~ s^{-3/2}
# 在 <k>=1 的 ER 网络中统计“随机选一个节点，它所在分支的大小为 s”的概率 p_s（去掉最大分支），
# 与理论 p_s = e^{-<k>s} (<k>s)^{s-1} / s! 对比；临界点处它按 s^{-3/2} 衰减。
# 同时给出 <k>=0.5 时的平均分支大小与理论值 1/(1-<k>) = 2 的比较。
# 输出：临界点处双对数图近似斜率 -3/2 的直线；亚临界时平均分支大小接近 2。
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from scipy.special import gammaln

N = 200_000


def node_cluster_sizes(c, seed):
    G = nx.fast_gnp_random_graph(N, c / (N - 1), seed=seed)
    comps = sorted((len(cc) for cc in nx.connected_components(G)), reverse=True)
    return comps


comps = node_cluster_sizes(1.0, 2)[1:]               # 去掉最大分支
sizes, counts = np.unique(comps, return_counts=True)
p_s = sizes * counts / N                            # 节点所在分支大小为 s 的概率
theory = np.exp(-sizes * 1.0 + (sizes - 1) * np.log(sizes * 1.0) - gammaln(sizes + 1))
for s in [1, 2, 3, 5, 10]:
    i = np.where(sizes == s)[0][0]
    print("s=%2d: 模拟 p_s=%.4f, 理论 %.4f" % (s, p_s[i], theory[i]))

sub = node_cluster_sizes(0.5, 3)
print("<k>=0.5 平均分支大小（按节点计）= %.3f，理论 1/(1-<k>) = 2" % (np.sum(np.array(sub) ** 2) / N))

plt.loglog(sizes, p_s, "o", ms=3, label="simulation <k>=1")
plt.loglog(sizes, theory, "-", label="theory")
plt.loglog(sizes, 0.4 * sizes ** -1.5, "--", label="s^-3/2")
plt.xlabel("component size s")
plt.ylabel("p_s")
plt.legend()
plt.show()


# %% 示例：ER 网络平均距离随 N 的对数增长
# 固定 <k>=6，N 从 500 增加到 16000，在最大连通分支上用若干源点的 BFS 估计平均距离 <d>，
# 与 ln N / ln<k> 以及 Fronczak 等（2004）的修正公式 (ln N - γ_E)/ln<k> + 1/2 比较（γ_E 为欧拉常数）。
# 输出：<d> 随 N 对数增长；修正公式与模拟的差距明显小于粗略公式。
import networkx as nx
import numpy as np

c, gamma_E = 6.0, 0.5772156649
rng = np.random.default_rng(1)
Ns, ds = [], []                                   # 存下结果用于作图
for N in [500, 2000, 8000, 16000]:
    G = nx.fast_gnp_random_graph(N, c / (N - 1), seed=N)
    G = G.subgraph(max(nx.connected_components(G), key=len))
    src = rng.choice(list(G), size=200, replace=False)
    d = np.mean([np.mean(list(nx.single_source_shortest_path_length(G, s).values())[1:]) for s in src])
    Ns.append(N); ds.append(d)
    print("N=%5d: 模拟 <d>=%.2f | lnN/ln<k>=%.2f | 修正公式=%.2f"
          % (N, d, np.log(N) / np.log(c), (np.log(N) - gamma_E) / np.log(c) + 0.5))

# 作图：平均距离随 N（对数轴）的增长，与两条理论曲线比较
import matplotlib.pyplot as plt

nn = np.logspace(np.log10(400), np.log10(20000), 50)
fig, ax = plt.subplots(figsize=(6.4, 4.2))
ax.plot(Ns, ds, "o", ms=7, label="simulation (<k> = 6)")
ax.plot(nn, np.log(nn) / np.log(c), "--", color="0.5", label="ln N / ln<k>")
ax.plot(nn, (np.log(nn) - gamma_E) / np.log(c) + 0.5, "-", color="#d6604d", label="Fronczak et al. 2004")
ax.set_xscale("log"); ax.set_xlabel("N (log scale)"); ax.set_ylabel("average distance <d>")
ax.legend(fontsize=8); ax.set_title("<d> grows like ln N: small world in ER graphs", fontsize=10)
plt.tight_layout(); plt.show()


# %% 示例：真实网络与同规模 ER 网络的比较
# 生成与空手道网络节点数 N、边数 M 相同的 ER 网络（G(N,M) 模型），取其最大连通分支，
# 比较平均聚集系数 C 与平均路径长度 L，并给出 ER 聚集系数的理论值 C ≈ <k>/(N-1)。
# 输出：两者 L 相近，而空手道网络的 C 明显高于 ER 网络——这正是“小世界性”的含义。
# 单个随机网络有涨落，严格比较应对多个随机种子取平均（见小世界与无标度网络模型的代码示例）。
import networkx as nx

K = nx.karate_club_graph()
n, m = K.number_of_nodes(), K.number_of_edges()
R = nx.gnm_random_graph(n, m, seed=3)
R = R.subgraph(max(nx.connected_components(R), key=len))
print("空手道网络: C=%.3f, L=%.3f" % (nx.average_clustering(K), nx.average_shortest_path_length(K)))
print("ER 网络:    C=%.3f, L=%.3f（理论 C≈%.3f；最大连通分支含 %d/%d 个节点）"
      % (nx.average_clustering(R), nx.average_shortest_path_length(R), 2 * m / n / (n - 1),
         R.number_of_nodes(), n))

# 作图：空手道网络与同规模 ER 网络的 C、L 对比
import matplotlib.pyplot as plt
import numpy as np

vals = {"karate": (nx.average_clustering(K), nx.average_shortest_path_length(K)),
        "ER G(N,M)": (nx.average_clustering(R), nx.average_shortest_path_length(R))}
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
for ax, j, lab in [(ax1, 0, "average clustering C"), (ax2, 1, "average path length L")]:
    v = [vals[k][j] for k in vals]
    ax.bar(list(vals), v, color=["#d6604d", "#92c5de"], width=0.55)
    for i, x in enumerate(v):
        ax.text(i, x * 1.02, "%.3f" % x, ha="center")
    ax.set_ylabel(lab)
ax1.axhline(2 * m / n / (n - 1), color="0.4", ls="--", label="ER theory <k>/(N-1)"); ax1.legend(fontsize=8)
ax1.set_title("Karate C is %.1fx the random value" % (vals["karate"][0] / vals["ER G(N,M)"][0]), fontsize=10)
ax2.set_title("Path lengths are similar", fontsize=10)
plt.tight_layout(); plt.show()
