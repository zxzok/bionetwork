# 依赖：networkx>=3, numpy, scipy, matplotlib
# 数据：全部为代码中直接写出或随机生成的示例网络（七桥多重图、玩具 PPI 边列表、玩具调控网络、
#       虚构的药物–靶点二分网络、符号网络、多层网络与超图、短 DNA 序列），
#       基因、蛋白、药物与序列仅作演示，不代表真实的相互作用数据。文件读写示例只写入临时目录。

# %% 示例：哥尼斯堡七桥问题与欧拉路径
# 4 块陆地 A、B、C、D 由 7 座桥相连；两块陆地之间可能有不止一座桥，所以用多重图 MultiGraph。
# 计算每个节点的度与奇数度节点个数，用 Euler 判据（奇数度节点数为 0 或 2）判断是否存在欧拉路径。
# 输出：度为 A=5, B=3, C=3, D=3；奇数度节点 4 个；不存在欧拉路径。
# 再加一座连接 B 与 C 的桥后，B、C 变为偶数度，奇数度节点降为 2 个，欧拉路径随之存在。
import networkx as nx

bridges = [("A", "B"), ("A", "B"), ("A", "C"), ("A", "C"), ("A", "D"), ("B", "D"), ("C", "D")]

for label, edge_list in [("原始七桥", bridges), ("加一座 B–C 桥", bridges + [("B", "C")])]:
    G = nx.MultiGraph()
    G.add_edges_from(edge_list)
    n_odd = sum(1 for _, d in G.degree() if d % 2 == 1)
    print("【%s】节点的度: %s" % (label, dict(G.degree())))
    print("  奇数度节点个数: %d" % n_odd)
    print("  按 Euler 判据，存在欧拉路径吗？", n_odd in (0, 2))
    print("  NetworkX 的判断:", nx.has_eulerian_path(G))

# 作图：两种情形并排，奇数度节点标红；多重边用不同弧度的曲线区分
import matplotlib.pyplot as plt
from collections import Counter

xy = {"A": (0, 0), "B": (1, 1), "C": (1, -1), "D": (2, 0)}
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
for ax, (label, edge_list) in zip(axes, [("original 7 bridges", bridges), ("add a B-C bridge", bridges + [("B", "C")])]):
    G = nx.MultiGraph(edge_list)
    for (u, v), m in Counter(tuple(sorted(e)) for e in edge_list).items():
        for j in range(m):
            rad = 0 if m == 1 else (-0.25 + 0.5 * j / (m - 1))
            ax.annotate("", xy=xy[v], xytext=xy[u], arrowprops=dict(arrowstyle="-", color="0.5",
                        lw=1.6, connectionstyle="arc3,rad=%.2f" % rad))
    for n, (x, y) in xy.items():
        odd = G.degree(n) % 2 == 1
        ax.scatter(x, y, s=700, color="#d6604d" if odd else "#4393c3", zorder=3)
        ax.text(x, y, "%s\nk=%d" % (n, G.degree(n)), ha="center", va="center", color="white", fontsize=9, zorder=4)
    n_odd = sum(d % 2 for _, d in G.degree())
    ax.set_title("%s: %d odd nodes, Euler path = %s" % (label, n_odd, nx.has_eulerian_path(G)), fontsize=10)
    ax.set_xlim(-0.4, 2.4); ax.set_ylim(-1.4, 1.4); ax.axis("off")
plt.tight_layout(); plt.show()


# %% 示例：从边列表构造邻接矩阵
# 把一个玩具蛋白质相互作用网络的边列表转换为邻接矩阵 A（numpy 数组），
# 并验证无向图的三条基本性质：A 对称；度 = 行和；度之和 = 2 × 边数。
# 输出中 TP53 的度最大（与 6 个蛋白相连）；最后用 NetworkX 核对度并计算网络密度。
import networkx as nx
import numpy as np

edges = [("TP53", "MDM2"), ("TP53", "EP300"), ("MDM2", "MDM4"), ("TP53", "MDM4"),
         ("EP300", "CREBBP"), ("TP53", "CREBBP"), ("ATM", "TP53"), ("ATM", "CHEK2"),
         ("CHEK2", "TP53")]
nodes = sorted({u for e in edges for u in e})
idx = {name: i for i, name in enumerate(nodes)}
N = len(nodes)

A = np.zeros((N, N), dtype=int)
for u, v in edges:
    A[idx[u], idx[v]] = A[idx[v], idx[u]] = 1

print("节点顺序:", nodes)
print(A)
print("对称吗？", np.array_equal(A, A.T))
deg = A.sum(axis=1)
print("各节点的度:", dict(zip(nodes, deg.tolist())))
print("度之和 = %d, 2 × 边数 = %d" % (deg.sum(), 2 * len(edges)))

G = nx.Graph(edges)
print("NetworkX 给出的度:", dict(G.degree()))
print("网络密度 = %.3f" % nx.density(G))

# 作图：左为邻接矩阵热图，右为网络布局（节点大小与颜色 ∝ 度）
import matplotlib.pyplot as plt

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.2))
ax1.imshow(A, cmap="Greys", vmin=0, vmax=1.6)
ax1.set_xticks(range(N)); ax1.set_xticklabels(nodes, rotation=60, fontsize=8)
ax1.set_yticks(range(N)); ax1.set_yticklabels(nodes, fontsize=8)
ax1.set_title("Adjacency matrix A (symmetric)")
pos = nx.spring_layout(G, seed=2)
nx.draw_networkx_edges(G, pos, ax=ax2, edge_color="0.6", alpha=0.6)
nc = nx.draw_networkx_nodes(G, pos, ax=ax2, nodelist=nodes, node_size=[120 * d for d in deg],
                            node_color=deg, cmap="YlOrRd", vmin=0, edgecolors="0.4")
nx.draw_networkx_labels(G, {n: (x, y + 0.13) for n, (x, y) in pos.items()}, ax=ax2, font_size=8)
ax2.margins(0.15)
fig.colorbar(nc, ax=ax2, label="degree k")
ax2.set_title("TP53 is the hub (k = %d)" % deg.max()); ax2.axis("off")
plt.tight_layout(); plt.show()


# %% 示例：有向网络的入度与出度
# 一个玩具基因调控网络：边 X -> Y 表示转录因子 X 调控基因 Y。
# 有向图的邻接矩阵一般不对称；入度 = 被多少个调控者调控，出度 = 调控多少个靶基因。
# 输出：邻接矩阵不对称；出度最大的“主调控因子”是 TF1（出度 4）。
# 注意 TF3 -> g3 与 g3 -> TF3 构成一个长度为 2 的反馈环（feedback loop），只有有向表示才能区分它。
import networkx as nx
import numpy as np

reg = [("TF1", "TF2"), ("TF1", "TF3"), ("TF1", "g1"), ("TF2", "g1"), ("TF2", "g2"),
       ("TF3", "g2"), ("TF3", "g3"), ("TF1", "g4"), ("g3", "TF3")]
D = nx.DiGraph(reg)
order = sorted(D.nodes())
A = nx.to_numpy_array(D, nodelist=order, dtype=int)
print("节点顺序:", order)
print(A)
print("对称吗？", np.array_equal(A, A.T))

in_deg = dict(D.in_degree())
out_deg = dict(D.out_degree())
master = max(out_deg, key=out_deg.get)
print("入度:", in_deg)
print("出度:", out_deg)
print("主调控因子: %s（出度 %d）" % (master, out_deg[master]))
print("长度为 2 的反馈环:", [c for c in nx.simple_cycles(D) if len(c) == 2])

# 作图：有向网络，节点大小 ∝ 出度，反馈环的两条边标红
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(6.4, 4.2))
pos = {"TF1": (0, 2), "TF2": (-1, 1), "TF3": (1, 1), "g1": (-1.5, 0), "g2": (-0.5, 0), "g3": (0.5, 0), "g4": (1.5, 0)}
loop = {("TF3", "g3"), ("g3", "TF3")}
nx.draw_networkx_edges(D, pos, ax=ax, edgelist=[e for e in D.edges() if e not in loop], edge_color="0.55",
                       arrows=True, arrowsize=14, node_size=900)
nx.draw_networkx_edges(D, pos, ax=ax, edgelist=list(loop), edge_color="#d6604d", width=2, arrows=True,
                       arrowsize=14, node_size=900, connectionstyle="arc3,rad=0.2")
nx.draw_networkx_nodes(D, pos, ax=ax, node_size=[300 + 150 * out_deg[n] for n in D],
                       node_color=["#f4a582" if n.startswith("TF") else "#92c5de" for n in D])
nx.draw_networkx_labels(D, pos, ax=ax, font_size=8)
ax.set_title("Master regulator %s (out-degree %d); red = feedback loop" % (master, out_deg[master]), fontsize=10)
ax.axis("off"); plt.tight_layout(); plt.show()


# %% 示例：二分网络的投影——药物–靶点到药物–药物
# 一个虚构的药物–靶点二分网络（药物 D1–D5，靶点 T1–T6）。
# 投影到药物一侧：两种药物共享靶点就连边，边权 = 共享靶点数（等价于 B B^T 的非对角元）。
# 输出按共享靶点数从大到小列出药物对，并画出投影网络（边宽 ∝ 共享靶点数）。
# 共享靶点多的药物对是药物重定位的候选线索之一；矩阵计算与 NetworkX 的结果一致。
import networkx as nx
import numpy as np
from networkx.algorithms import bipartite
import matplotlib.pyplot as plt

drug_target = [("D1", "T1"), ("D1", "T2"), ("D2", "T2"), ("D2", "T3"), ("D3", "T1"),
               ("D3", "T2"), ("D3", "T4"), ("D4", "T5"), ("D5", "T5"), ("D5", "T6"), ("D4", "T6")]
drugs = sorted({d for d, _ in drug_target})
targets = sorted({t for _, t in drug_target})
B = nx.Graph()
B.add_nodes_from(drugs, bipartite=0)
B.add_nodes_from(targets, bipartite=1)
B.add_edges_from(drug_target)
print("是二分图吗？", bipartite.is_bipartite(B))

P = bipartite.weighted_projected_graph(B, drugs)
for u, v, w in sorted(P.edges(data="weight"), key=lambda x: -x[2]):
    print("%s - %s 共享靶点数 = %d" % (u, v, w))

# 用关联矩阵核对：P = B B^T
Bmat = bipartite.biadjacency_matrix(B, row_order=drugs, column_order=targets).toarray()
PP = Bmat @ Bmat.T
print("B B^T（对角元为各药物的靶点数）:")
print(PP)

pos = nx.spring_layout(P, seed=0)
widths = [2 * w for _, _, w in P.edges(data="weight")]
nx.draw(P, pos, with_labels=True, width=widths, node_color="#9ecae1")
plt.title("drug projection (edge width = shared targets)")
plt.show()


# %% 示例：邻接矩阵的乘方——游走、共同邻居与三角形
# 对正文中的 4 蛋白例子（a–b、a–c、b–c、c–d）计算 A^2 与 A^3。
# (A^r)_ij 是从 i 到 j 的长度为 r 的游走条数：A^2 的对角元等于度，非对角元等于共同邻居数；
# tr(A^3)/6 是三角形数。最后用 NetworkX 的 common_neighbors 与 triangles 核对。
# 输出：A^2 对角元 [2 2 3 1]；a 与 d 的共同邻居数 1；三角形数 1（a–b–c）。
import networkx as nx
import numpy as np

nodes = ["a", "b", "c", "d"]
G = nx.Graph([("a", "b"), ("a", "c"), ("b", "c"), ("c", "d")])
A = nx.to_numpy_array(G, nodelist=nodes, dtype=int)
A2 = A @ A
A3 = A2 @ A
print("A^2 =\n", A2)
print("A^3 =\n", A3)
print("A^2 的对角元:", np.diag(A2), " 度:", [G.degree(v) for v in nodes])
print("a 与 d 的共同邻居数 (A^2)_ad =", A2[0, 3],
      "；NetworkX:", len(list(nx.common_neighbors(G, "a", "d"))))
print("三角形数 tr(A^3)/6 =", np.trace(A3) // 6,
      "；NetworkX:", sum(nx.triangles(G).values()) // 3)

# 有向情形：(A^r)_ij 只计沿箭头方向的游走
D = nx.DiGraph([("TF1", "TF2"), ("TF2", "g"), ("TF1", "g")])
order = ["TF1", "TF2", "g"]
Ad = nx.to_numpy_array(D, nodelist=order, dtype=int)   # NetworkX 约定：行 = 起点，列 = 终点
print("有向图中 TF1 经两步到达 g 的路径数 =", (Ad @ Ad)[0, 2], "（TF1→TF2→g，前馈环的间接支路）")

# 作图：A、A^2、A^3 三个热图，格子里标出游走条数
import matplotlib.pyplot as plt

fig, axes = plt.subplots(1, 3, figsize=(10, 3.6))
for ax, (name, Mx) in zip(axes, [("A", A), ("A^2 (diag = degree)", A2), ("A^3 (tr/6 = %d triangle)" % (np.trace(A3) // 6), A3)]):
    ax.imshow(Mx, cmap="Blues")
    for i in range(4):
        for j in range(4):
            ax.text(j, i, Mx[i, j], ha="center", va="center",
                    color="white" if Mx[i, j] > Mx.max() / 2 else "black")
    ax.set_xticks(range(4)); ax.set_xticklabels(nodes); ax.set_yticks(range(4)); ax.set_yticklabels(nodes)
    ax.set_title(name, fontsize=10)
plt.tight_layout(); plt.show()


# %% 示例：关联矩阵、度矩阵与拉普拉斯矩阵
# 构造无定向关联矩阵 B、定向关联矩阵 ∇、度矩阵 D 与拉普拉斯矩阵 L = D − A，核对两个恒等式：
# B B^T = D + A，∇ ∇^T = L。再计算 L 的特征值（正文手算结果 0, 1, 3, 4）、归一化拉普拉斯的特征值，
# 并验证“零特征值的重数 = 连通分支数”：删去 c–d 后图分成两块，零特征值变为 2 个。
import networkx as nx
import numpy as np

nodes = ["a", "b", "c", "d"]
edges = [("a", "b"), ("a", "c"), ("b", "c"), ("c", "d")]
G = nx.Graph(edges)
A = nx.to_numpy_array(G, nodelist=nodes)
Dm = np.diag(A.sum(axis=1))
L = Dm - A

B = nx.incidence_matrix(G, nodelist=nodes, edgelist=edges, oriented=False).toarray()
Nab = nx.incidence_matrix(G, nodelist=nodes, edgelist=edges, oriented=True).toarray()
print("关联矩阵 B（行 = 节点，列 = 边）:\n", B.astype(int))
print("B B^T == D + A ?", np.allclose(B @ B.T, Dm + A))
print("∇ ∇^T == L ?", np.allclose(Nab @ Nab.T, L))
print("L =\n", L.astype(int))
print("L 的特征值:", np.round(np.linalg.eigvalsh(L), 4), " 之和 = 2M =", int(np.trace(L)))

x = np.array([1.0, -1.0, 0.0, 0.0])
print("L x（x = (1,-1,0,0)）=", L @ x, "→ 特征值 3 的特征向量")
print("二次型 x^T L x =", x @ L @ x, "= Σ(x_i - x_j)^2 =",
      sum((x[nodes.index(u)] - x[nodes.index(v)]) ** 2 for u, v in edges))

Ln = nx.normalized_laplacian_matrix(G, nodelist=nodes).toarray()
print("归一化拉普拉斯的特征值（落在 [0, 2]）:", np.round(np.linalg.eigvalsh(Ln), 4))

G2 = G.copy()
G2.remove_edge("c", "d")
L2 = nx.laplacian_matrix(G2, nodelist=nodes).toarray()
ev2 = np.linalg.eigvalsh(L2)
print("删去 c–d 后 L 的特征值:", np.round(ev2, 4),
      "；零特征值个数 =", int(np.sum(np.isclose(ev2, 0))),
      "；连通分支数 =", nx.number_connected_components(G2))

# 作图：三组特征值谱，零特征值的个数 = 连通分支数
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(6.4, 4.2))
spectra = [("L, connected", np.linalg.eigvalsh(L), "o"), ("normalized L", np.linalg.eigvalsh(Ln), "s"),
           ("L, c-d removed", ev2, "^")]
for row, (name, ev, mk) in enumerate(spectra):
    ax.scatter(ev, [row] * len(ev), marker=mk, s=80, label=name, zorder=3)
    vals, mult = np.unique(np.round(np.abs(ev), 2), return_counts=True)
    for e, m in zip(vals, mult):
        ax.annotate("%.2f" % e + (" (x%d)" % m if m > 1 else ""), (e, row), textcoords="offset points",
                    xytext=(0, 9), ha="center", fontsize=8)
ax.axvline(0, color="0.6", ls="--", lw=1)
ax.set_yticks(range(3)); ax.set_yticklabels([s[0] for s in spectra]); ax.set_ylim(-0.6, 2.7)
ax.set_xlabel("eigenvalue")
ax.set_title("Number of zero eigenvalues = number of components")
plt.tight_layout(); plt.show()


# %% 示例：稀疏存储——边列表、CSR 与稠密矩阵的内存比较
# 生成一个 N = 20000、平均度约 10 的随机稀疏网络（模拟一个蛋白质组规模的网络），
# 比较稠密 float64 邻接矩阵（只按 N^2 × 8 字节计算，不实际分配）与 CSR 稀疏矩阵的内存，
# 并展示 CSR 的三个数组如何直接给出邻居列表和度。
# 输出：密度约 5e-4；稠密矩阵约 3.2 GB，CSR 只有约 2–3 MB；indptr 差分即为度。
import networkx as nx
import numpy as np
import scipy.sparse as sp

N, k_mean = 20000, 10
G = nx.gnm_random_graph(N, N * k_mean // 2, seed=1)
M = G.number_of_edges()
print("N = %d, M = %d, 密度 = %.2e" % (N, M, nx.density(G)))

S = nx.to_scipy_sparse_array(G, format="csr", dtype=np.float64)
dense_bytes = N * N * 8
csr_bytes = S.data.nbytes + S.indices.nbytes + S.indptr.nbytes
print("稠密矩阵约需 %.1f GB；CSR 实际占用 %.2f MB（%.0f 倍差距）"
      % (dense_bytes / 1e9, csr_bytes / 1e6, dense_bytes / csr_bytes))

i = 0
nbrs = S.indices[S.indptr[i]:S.indptr[i + 1]]
print("节点 0 的邻居（来自 CSR）:", sorted(nbrs.tolist()))
print("NetworkX 给出的邻居:      ", sorted(G.neighbors(0)))
deg_csr = np.diff(S.indptr)
print("CSR 中 indptr 的差分就是度：与 NetworkX 一致吗？",
      np.array_equal(deg_csr, np.array([d for _, d in sorted(G.degree())])))

# 手工从边列表构造 CSR（正文“算法 3”），与 SciPy 的结果比较
u = np.array([e[0] for e in G.edges()] + [e[1] for e in G.edges()])
v = np.array([e[1] for e in G.edges()] + [e[0] for e in G.edges()])
count = np.bincount(u, minlength=N)
indptr = np.concatenate([[0], np.cumsum(count)])
pos = indptr[:-1].copy()
indices = np.empty(len(u), dtype=np.int64)
for a, b in zip(u, v):
    indices[pos[a]] = b
    pos[a] += 1
S2 = sp.csr_array((np.ones(len(u)), indices, indptr), shape=(N, N))
print("手工 CSR 与 SciPy CSR 相同吗？", (abs(S2 - S)).sum() == 0)

# 作图：左为三种存储方式的内存（对数轴），右为从 CSR 的 indptr 差分得到的度分布
import matplotlib.pyplot as plt

edge_bytes = 2 * M * 8                      # 边列表：每条边两个 int64
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
mem = {"dense float64": dense_bytes, "CSR": csr_bytes, "edge list (int64)": edge_bytes}
ax1.bar(list(mem), [b / 1e6 for b in mem.values()], color=["#b2182b", "#2166ac", "#92c5de"])
ax1.set_yscale("log"); ax1.set_ylabel("memory (MB, log scale)")
for i, b in enumerate(mem.values()):
    ax1.text(i, b / 1e6 * 1.3, "%.3g MB" % (b / 1e6), ha="center", fontsize=9)
ax1.set_title("N = %d: dense is %.0fx larger than CSR" % (N, dense_bytes / csr_bytes), fontsize=10)
ks, cnt = np.unique(deg_csr, return_counts=True)
ax2.bar(ks, cnt / N, color="#4393c3")
ax2.set_xlabel("degree k = diff(indptr)"); ax2.set_ylabel("fraction of nodes")
ax2.set_title("Degree distribution read from CSR (mean %.1f)" % deg_csr.mean(), fontsize=10)
plt.tight_layout(); plt.show()


# %% 示例：网络文件格式——边列表、GML 与 GraphML 的读写差异
# 构造一个带节点属性（类型）、边属性（置信度）和一个孤立节点的小型 PPI 网络，
# 分别写成边列表、GML 和 GraphML（存放在临时目录，运行结束后自动删除），再读回比较。
# 输出：边列表读回后丢失了孤立节点 BRCA2 和节点属性；GML 与 GraphML 完整保留节点、边及属性。
# 同时演示：同一对节点在边列表中出现两次时，读成 Graph 会被合并为一条边。
import os
import tempfile
import networkx as nx

G = nx.Graph()
G.add_node("TP53", kind="TF")
G.add_node("MDM2", kind="E3 ligase")
G.add_node("CHEK2", kind="kinase")
G.add_node("BRCA2", kind="repair")          # 孤立节点：没有检测到相互作用
G.add_edge("TP53", "MDM2", score=0.999)
G.add_edge("TP53", "CHEK2", score=0.980)

with tempfile.TemporaryDirectory() as tmp:
    p_el, p_gml, p_gx = (os.path.join(tmp, f) for f in ("ppi.edgelist", "ppi.gml", "ppi.graphml"))
    nx.write_edgelist(G, p_el, data=["score"])
    nx.write_gml(G, p_gml)
    nx.write_graphml(G, p_gx)
    print("边列表文件内容:")
    print(open(p_el).read())
    print("GraphML 文件前 6 行:")
    print("".join(open(p_gx).readlines()[:6]))

    G_el = nx.read_edgelist(p_el, data=[("score", float)])
    G_gml = nx.read_gml(p_gml)
    G_gx = nx.read_graphml(p_gx)
    for name, H in [("原始", G), ("边列表", G_el), ("GML", G_gml), ("GraphML", G_gx)]:
        print("%-6s 节点数 %d，边数 %d，BRCA2 在吗？%s，TP53 的属性: %s"
              % (name, H.number_of_nodes(), H.number_of_edges(), "BRCA2" in H, H.nodes["TP53"]))

    # 重复边：同一对蛋白在两个实验中各报告一次
    with open(os.path.join(tmp, "dup.tsv"), "w") as f:
        f.write("TP53\tMDM2\t0.7\nTP53\tMDM2\t0.9\n")
    Hg = nx.read_edgelist(os.path.join(tmp, "dup.tsv"), delimiter="\t", data=[("w", float)])
    Hm = nx.read_edgelist(os.path.join(tmp, "dup.tsv"), delimiter="\t", data=[("w", float)],
                          create_using=nx.MultiGraph)
    print("读成 Graph：边数 %d，权重 %s（只保留了后一条）" % (Hg.number_of_edges(), Hg["TP53"]["MDM2"]))
    print("读成 MultiGraph：边数 %d" % Hm.number_of_edges())


# %% 示例：符号网络与结构平衡
# 一个带激活（+1）与抑制（−1）的玩具调控网络（按无向符号图检查平衡）。
# 结构平衡等价于：可以把节点分成两组，使组内边全为正、组间边全为负。
# 用广度优先搜索做“带符号的二着色”判断平衡，并列出每个环的符号（边符号之积）。
# 输出：第一张图平衡，分组为 {A, B} 与 {C, D}；把 B–C 改为正号后出现负环，不再平衡。
import networkx as nx
from collections import deque


def balance_partition(G):
    """返回 (是否平衡, 节点到组别 0/1 的映射)。正边要求同组，负边要求异组。"""
    side = {}
    for s in G.nodes():
        if s in side:
            continue
        side[s] = 0
        q = deque([s])
        while q:
            u = q.popleft()
            for v in G.neighbors(u):
                want = side[u] if G[u][v]["sign"] > 0 else 1 - side[u]
                if v not in side:
                    side[v] = want
                    q.append(v)
                elif side[v] != want:
                    return False, side
    return True, side


def cycle_signs(G):
    out = []
    for cyc in nx.cycle_basis(G):
        s = 1
        for i in range(len(cyc)):
            s *= G[cyc[i]][cyc[(i + 1) % len(cyc)]]["sign"]
        out.append((cyc, s))
    return out


signed = [("A", "B", +1), ("C", "D", +1), ("A", "C", -1), ("B", "D", -1), ("B", "C", -1)]
for label, edges in [("原网络", signed),
                     ("把 B–C 改为 +1", [e if e[:2] != ("B", "C") else ("B", "C", +1) for e in signed])]:
    G = nx.Graph()
    for u, v, s in edges:
        G.add_edge(u, v, sign=s)
    ok, side = balance_partition(G)
    print("【%s】结构平衡？%s" % (label, ok))
    if ok:
        print("  两组:", sorted(v for v in side if side[v] == 0), sorted(v for v in side if side[v] == 1))
    for cyc, s in cycle_signs(G):
        print("  环 %s 的符号 = %+d" % ("–".join(cyc), s))

# 作图：绿色实线 = 正边，红色虚线 = 负边；平衡时节点按两组着色
import matplotlib.pyplot as plt

xy = {"A": (0, 1), "B": (1, 1), "C": (0, 0), "D": (1, 0)}
variants = [("original", signed), ("B-C set to +1", [e if e[:2] != ("B", "C") else ("B", "C", +1) for e in signed])]
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
for ax, (label, edges) in zip(axes, variants):
    G = nx.Graph()
    for u, v, s in edges:
        G.add_edge(u, v, sign=s)
    ok, side = balance_partition(G)
    for sgn, col, ls in [(1, "#1b7837", "-"), (-1, "#b2182b", "--")]:
        nx.draw_networkx_edges(G, xy, ax=ax, edgelist=[(u, v) for u, v, s in G.edges(data="sign") if s == sgn],
                               edge_color=col, style=ls, width=2.5)
    colors = [("#fdb863" if side.get(n) == 0 else "#b2abd2") if ok else "0.8" for n in G]
    nx.draw_networkx_nodes(G, xy, ax=ax, node_color=colors, node_size=700)
    nx.draw_networkx_labels(G, xy, ax=ax)
    ax.set_title("%s: balanced = %s" % (label, ok)); ax.axis("off")
    ax.set_xlim(-0.3, 1.3); ax.set_ylim(-0.3, 1.3)
plt.tight_layout(); plt.show()


# %% 示例：多层网络的超邻接矩阵与超图的表示
# (1) 两层多重网络：同一组 4 个神经元，层 1 为化学突触（有向），层 2 为电突触（无向），
#     层间耦合 ω 连接同一神经元的两个副本，拼成 8×8 的超邻接矩阵；对比“各层相加”的聚合矩阵。
# (2) 超图：3 个蛋白复合物作为超边，用关联矩阵 H 表示；团展开得到加权图 H H^T（去掉对角元），
#     并展示两个不同的超图团展开后完全相同——团展开会丢失信息。
import networkx as nx
import numpy as np

order = ["n1", "n2", "n3", "n4"]
chem = nx.DiGraph([("n1", "n2"), ("n2", "n3"), ("n3", "n4")])
gap = nx.Graph()
gap.add_nodes_from(order)                    # n3 没有电突触，但仍是该层的节点
gap.add_edges_from([("n1", "n2"), ("n2", "n4")])
A1 = nx.to_numpy_array(chem, nodelist=order)
A2 = nx.to_numpy_array(gap, nodelist=order)
omega = 0.5
I = np.eye(len(order))
supra = np.block([[A1, omega * I], [omega * I, A2]])
print("超邻接矩阵（8×8，左上 = 化学突触层，右下 = 电突触层）:")
print(supra)
print("聚合矩阵 A1 + A2（无法区分 n1–n2 之间是哪种突触）:")
print(A1 + A2)

# 超图：节点 P1..P5，超边 = 复合物
nodes = ["P1", "P2", "P3", "P4", "P5"]
complexes = {"C1": ["P1", "P2", "P3"], "C2": ["P3", "P4"], "C3": ["P4", "P5"]}
H = np.array([[1 if p in members else 0 for members in complexes.values()] for p in nodes])
print("超图关联矩阵 H（行 = 蛋白，列 = 复合物）:")
print(H)
W = H @ H.T
np.fill_diagonal(W, 0)
print("团展开的加权邻接矩阵 H H^T（去对角）:")
print(W)

# 另一个超图：P1–P2、P2–P3、P1–P3 是三个两两复合物，而不是一个三元复合物
H_alt = np.array([[1, 0, 1, 0, 0], [1, 1, 0, 0, 0], [0, 1, 1, 1, 0], [0, 0, 0, 1, 1], [0, 0, 0, 0, 1]])
W_alt = H_alt @ H_alt.T
np.fill_diagonal(W_alt, 0)
print("“三个二元复合物”的团展开与“一个三元复合物”的团展开相同吗？", np.array_equal(W, W_alt))

# 作图：左为超邻接矩阵（虚线分隔两层与层间耦合块），右为两个超图共同的团展开矩阵
import matplotlib.pyplot as plt

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.2))
im = ax1.imshow(supra, cmap="Blues", vmin=0, vmax=1)
ax1.axhline(3.5, color="#d6604d", ls="--"); ax1.axvline(3.5, color="#d6604d", ls="--")
labs = [n + "(chem)" for n in order] + [n + "(gap)" for n in order]
ax1.set_xticks(range(8)); ax1.set_xticklabels(labs, rotation=60, fontsize=7)
ax1.set_yticks(range(8)); ax1.set_yticklabels(labs, fontsize=7)
ax1.set_title("Supra-adjacency (omega = %.1f off-diagonal)" % omega, fontsize=10)
fig.colorbar(im, ax=ax1, fraction=0.046)
ax2.imshow(W, cmap="Oranges", vmin=0, vmax=2)
for i in range(5):
    for j in range(5):
        ax2.text(j, i, W[i, j], ha="center", va="center")
ax2.set_xticks(range(5)); ax2.set_xticklabels(nodes); ax2.set_yticks(range(5)); ax2.set_yticklabels(nodes)
ax2.set_title("Clique expansion H H^T: identical for both hypergraphs = %s" % np.array_equal(W, W_alt), fontsize=9)
plt.tight_layout(); plt.show()


# %% 示例：用欧拉路径做 de Bruijn 图序列组装，并核对几条图论基本定理
# (1) 把一段 DNA 序列切成长度 k = 4 的重叠片段（k-mer），每个 k-mer 是一条从前 3 个碱基指向后
#     3 个碱基的有向边；拼回原序列就是在这张有向多重图中寻找欧拉路径。
# (2) 在随机图上核对：握手定理、二分图 ⇔ 无奇环、N 个节点的树恰有 N − 1 条边。
# 输出：重建的序列与原序列相同；三条定理的核对结果均为 True。
import networkx as nx

seq = "ATGGCGTGCAATGGCA"
k = 4
kmers = [seq[i:i + k] for i in range(len(seq) - k + 1)]
dbg = nx.MultiDiGraph()
for km in kmers:
    dbg.add_edge(km[:-1], km[1:])
print("k-mer 数 = 边数 =", dbg.number_of_edges(), "；(k-1)-mer 节点数 =", dbg.number_of_nodes())
print("存在欧拉路径吗？", nx.has_eulerian_path(dbg))
path = list(nx.eulerian_path(dbg))
rebuilt = path[0][0] + "".join(v[-1] for _, v in path)
print("重建序列:", rebuilt)
print("与原序列相同吗？", rebuilt == seq,
      "（序列含重复片段时，欧拉路径可能不唯一，此时组装结果存在歧义）")

G = nx.gnm_random_graph(200, 600, seed=7)
print("握手定理 Σk = 2M：", sum(d for _, d in G.degree()) == 2 * G.number_of_edges())

# 二分图 ⇔ 无奇环：环空间的基中若全是偶环，则所有环都是偶环（偶数条边的对称差仍为偶数）
T = nx.random_labeled_tree(50, seed=3)
for name, H in [("6 节点环", nx.cycle_graph(6)), ("5 节点环", nx.cycle_graph(5)), ("随机树", T), ("随机图", G)]:
    odd = any(len(c) % 2 == 1 for c in nx.cycle_basis(H))
    print("%-6s 二分图？%-5s 存在奇数环？%-5s 判据成立？%s" % (name, nx.is_bipartite(H), odd, nx.is_bipartite(H) == (not odd)))

print("树：N = %d，M = %d，M == N − 1？%s" % (T.number_of_nodes(), T.number_of_edges(),
                                         T.number_of_edges() == T.number_of_nodes() - 1))

# 作图：de Bruijn 图，边按欧拉路径的经过顺序着色（浅 → 深）
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(6.4, 4.2))
pos = nx.kamada_kawai_layout(nx.DiGraph(dbg))
step = {}
for t, (u, v) in enumerate(path):
    step.setdefault((u, v), []).append(t)
simple = list(step)
nx.draw_networkx_edges(dbg, pos, ax=ax, edgelist=simple, edge_color=[min(step[e]) for e in simple],
                       edge_cmap=plt.cm.viridis, width=2, arrows=True, arrowsize=14, node_size=800,
                       connectionstyle="arc3,rad=0.12")
nx.draw_networkx_nodes(dbg, pos, ax=ax, node_color="#f7f7f7", edgecolors="0.4", node_size=800)
nx.draw_networkx_labels(dbg, pos, ax=ax, font_size=7)
ax.set_title("de Bruijn graph (k = %d); Euler path rebuilds sequence: %s" % (k, rebuilt == seq), fontsize=10)
ax.axis("off"); plt.tight_layout(); plt.show()
