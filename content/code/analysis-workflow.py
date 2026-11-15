# 依赖：networkx>=3.4（forceatlas2_layout 需要 3.4 及以上）, numpy, scipy, matplotlib
# 数据：示例 1 使用代码中内嵌的一段模拟边表（模拟数据，仅用于演示方法，不代表真实相互作用）；
#       示例 2、4 使用 networkx 自带的《悲惨世界》人物共现网络（77 个节点）；
#       示例 3 使用 networkx 自带的 Zachary 空手道俱乐部网络（34 个节点，节点属性 'club' 记录真实分裂）；
#       示例 5、6 使用代码中构造的小网络（基因名仅作标签，边为示意，不代表数据库记录）；
#       示例 7、8 使用代码生成的 BA 网络与随机分块网络（SBM）；
#       示例 9 使用代码生成的模拟表达矩阵（含植入的共表达模块），完整演示从原始数据到结论的流程。
# 输入格式：真实分析中，网络通常来自一张边表（每行 "节点1 节点2 [权重]"，如 STRING 导出的
#       protein1 protein2 combined_score），可用 nx.read_edgelist 或 nx.from_pandas_edgelist 读入；
#       示例 5 演示边表、邻接矩阵、scipy 稀疏矩阵、GraphML 与 node-link JSON 之间的转换。
# 绘图：脚本中的 plt.show() 在无图形界面的环境中可改为 plt.savefig("文件名.png", dpi=200)。

# %% 示例：读入边表、按置信度过滤并取最大连通分支
# 从一段文本边表读入带 score 的网络，只保留 score >= 0.7 的边、去掉自环，再取最大连通分支。
# 输出：每一步之后的节点数与边数，以及取最大连通分支时丢弃的节点数。
# 解读：阈值和连通分支的取舍会直接改变后续所有指标，报告中应写明丢弃了多少节点。
import io
import networkx as nx

edge_text = """GENE_A GENE_B 0.95
GENE_A GENE_C 0.91
GENE_B GENE_C 0.88
GENE_C GENE_D 0.75
GENE_D GENE_E 0.72
GENE_E GENE_F 0.40
GENE_F GENE_G 0.93
GENE_G GENE_H 0.81
GENE_H GENE_F 0.77
GENE_D GENE_D 0.99
GENE_B GENE_E 0.55
GENE_I GENE_J 0.90"""

G_raw = nx.read_edgelist(io.StringIO(edge_text), data=(("score", float),))
print("原始网络：%d 个节点，%d 条边" % (G_raw.number_of_nodes(), G_raw.number_of_edges()))

G_filt = nx.Graph()
G_filt.add_edges_from((u, v, d) for u, v, d in G_raw.edges(data=True)
                      if d["score"] >= 0.7 and u != v)
print("过滤后（score >= 0.7，去自环）：%d 个节点，%d 条边" % (G_filt.number_of_nodes(), G_filt.number_of_edges()))

G_lcc = G_filt.subgraph(max(nx.connected_components(G_filt), key=len)).copy()
print("最大连通分支：%d 个节点，%d 条边（丢弃 %d 个节点：%s）" % (
    G_lcc.number_of_nodes(), G_lcc.number_of_edges(),
    G_filt.number_of_nodes() - G_lcc.number_of_nodes(),
    sorted(set(G_filt) - set(G_lcc))))

# 作图：原始网络中被保留的边（实线，宽度 ∝ score）与被过滤的边（虚线）；最大连通分支节点着色
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(6.4, 4.2))
G_draw = G_raw.copy(); G_draw.remove_edges_from(nx.selfloop_edges(G_draw))
pos = nx.spring_layout(G_draw, seed=4)
kept = [e for e in G_draw.edges() if G_filt.has_edge(*e)]
dropped = [e for e in G_draw.edges() if not G_filt.has_edge(*e)]
nx.draw_networkx_edges(G_draw, pos, edgelist=kept, ax=ax, width=[3 * G_raw.edges[e]["score"] for e in kept], edge_color="0.4")
nx.draw_networkx_edges(G_draw, pos, edgelist=dropped, ax=ax, style="dashed", edge_color="C3", alpha=0.6)
nx.draw_networkx_nodes(G_draw, pos, ax=ax, node_size=120,
                       node_color=["C0" if v in G_lcc else "0.8" for v in G_draw])
nx.draw_networkx_labels(G_draw, pos, ax=ax, labels={v: v.replace("GENE_", "") for v in G_draw}, font_size=8)
ax.set_title("Dashed red: score < 0.7 removed; blue nodes: largest component", fontsize=10); ax.axis("off")
plt.tight_layout(); plt.show()

# %% 示例：基本拓扑指标、度分布与中心性排名
# 对《悲惨世界》共现网络（按无权图处理）计算平均度、密度、平均聚集系数、传递性、平均最短路径、
# 直径和度同配系数；画出线性与双对数坐标下的度分布；列出三种中心性排名前 5 的节点。
# 解读：平均聚集系数（节点局部聚集系数的平均）与传递性（全网三角形比例）定义不同，数值也会不同；
# 不同中心性刻画的“重要”含义不同，前 5 名往往部分重合、部分不同。
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

G = nx.les_miserables_graph()
print("节点 %d，边 %d，连通：%s" % (G.number_of_nodes(), G.number_of_edges(), nx.is_connected(G)))

metrics = {
    "平均度": 2 * G.number_of_edges() / G.number_of_nodes(),
    "密度": nx.density(G),
    "平均聚集系数": nx.average_clustering(G),
    "传递性": nx.transitivity(G),
    "平均最短路径": nx.average_shortest_path_length(G),
    "直径": nx.diameter(G),
    "度同配系数": nx.degree_assortativity_coefficient(G),
}
for k, v in metrics.items():
    print("%-8s %.3f" % (k, v))

deg = np.array([d for _, d in G.degree()])
vals, counts = np.unique(deg, return_counts=True)
fig, ax = plt.subplots(1, 2, figsize=(9, 3.5))
ax[0].bar(vals, counts / counts.sum()); ax[0].set_xlabel("k"); ax[0].set_ylabel("P(k)"); ax[0].set_title("linear")
ax[1].loglog(vals, counts / counts.sum(), "o"); ax[1].set_xlabel("k"); ax[1].set_title("log-log")
plt.tight_layout(); plt.show()

def top5(cent):
    return [n for n, _ in sorted(cent.items(), key=lambda x: -x[1])[:5]]

print("度中心性 前5：", top5(nx.degree_centrality(G)))
print("介数中心性 前5：", top5(nx.betweenness_centrality(G)))
print("特征向量中心性 前5：", top5(nx.eigenvector_centrality(G, max_iter=1000)))

# %% 示例：社团发现、模块度与结果稳定性
# 在空手道俱乐部网络上运行 Louvain（固定种子）与贪心模块度算法，比较社团数和模块度 Q；
# 再用 10 个不同种子运行 Louvain，报告 Q 的范围；最后用归一化互信息（NMI）
# 把 Louvain 划分与俱乐部的真实分裂（节点属性 'club'）对照，并按社团着色画图。
# 解读：Louvain 有随机性，应固定种子以便复算，并报告多次运行的范围；NMI = 1 表示两种划分完全一致。
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

G = nx.karate_club_graph()
truth = [G.nodes[v]["club"] for v in G]

def nmi(labels_a, labels_b):
    """归一化互信息（NMI），1 表示两种划分完全一致。"""
    a = np.unique(labels_a, return_inverse=True)[1]
    b = np.unique(labels_b, return_inverse=True)[1]
    n = len(a)
    C = np.zeros((a.max() + 1, b.max() + 1))
    for i, j in zip(a, b):
        C[i, j] += 1
    P = C / n; pa = P.sum(1); pb = P.sum(0)
    nz = P > 0
    I = (P[nz] * np.log(P[nz] / np.outer(pa, pb)[nz])).sum()
    Ha = -(pa[pa > 0] * np.log(pa[pa > 0])).sum(); Hb = -(pb[pb > 0] * np.log(pb[pb > 0])).sum()
    return 2 * I / (Ha + Hb)

comms_louvain = nx.community.louvain_communities(G, seed=1)
comms_greedy = nx.community.greedy_modularity_communities(G)
for name, cs in [("Louvain", comms_louvain), ("Greedy", comms_greedy)]:
    print("%-8s 社团数 = %d, Q = %.3f" % (name, len(cs), nx.community.modularity(G, cs)))

Qs = [nx.community.modularity(G, nx.community.louvain_communities(G, seed=s)) for s in range(10)]
print("Louvain 10 个种子：Q 范围 %.3f – %.3f" % (min(Qs), max(Qs)))

label = {v: i for i, c in enumerate(comms_louvain) for v in c}
print("Louvain 与真实分裂的 NMI = %.3f" % nmi([label[v] for v in G], truth))

pos = nx.spring_layout(G, seed=3)
nx.draw_networkx(G, pos, node_color=[label[v] for v in G], cmap="tab10", node_size=200, font_size=7)
plt.axis("off"); plt.title("Louvain communities"); plt.show()

# %% 示例：与 ER 随机图和保度随机化零模型比较
# 把《悲惨世界》网络（按无权图处理）与 (a) 同 N、M 的 ER 随机图、(b) 双边交换得到的保度随机化网络
# 各生成 10 次比较：计算平均聚集系数 C、平均最短路径 L、Louvain 模块度 Q 的均值与 z 分数，
# 并以 ER 为参照计算小世界系数 sigma = (C/C_rand)/(L/L_rand)。
# 解读：z 分数衡量真实值偏离零模型分布的程度。保度零模型更严格：它的平均 C 更接近真实值，
# 聚集系数的 z 随之变小；但 z 还取决于零分布的离散程度（如 Q），不宜跨零模型直接比较 z 的大小。
# 零模型网络若不连通，只在最大连通分支上计算指标。
import numpy as np
import networkx as nx

G = nx.Graph(nx.les_miserables_graph())
for u, v in G.edges():
    G[u][v].pop("weight", None)              # 去掉权重，做无权分析
N, M = G.number_of_nodes(), G.number_of_edges()

def lcc(H):
    return H.subgraph(max(nx.connected_components(H), key=len)).copy()

def measures(H, seed=0):
    H = lcc(H)
    Q = nx.community.modularity(H, nx.community.louvain_communities(H, seed=seed))
    return nx.average_clustering(H), nx.average_shortest_path_length(H), Q

real = measures(G)
er_list, ds_list = [], []
for s in range(10):
    er_list.append(measures(nx.gnm_random_graph(N, M, seed=s), seed=s))
    H = G.copy()
    nx.double_edge_swap(H, nswap=5 * M, max_tries=100 * M, seed=s)   # 保度随机化
    ds_list.append(measures(H, seed=s))
er, ds = np.array(er_list), np.array(ds_list)

z_er = (np.array(real) - er.mean(0)) / er.std(0)
z_ds = (np.array(real) - ds.mean(0)) / ds.std(0)
sigma = (real[0] / er[:, 0].mean()) / (real[1] / er[:, 1].mean())

print("真实网络：      C = %.3f, L = %.3f, Q = %.3f" % real)
print("ER 零模型均值： C = %.3f, L = %.3f, Q = %.3f" % tuple(er.mean(0)))
print("保度零模型均值：C = %.3f, L = %.3f, Q = %.3f" % tuple(ds.mean(0)))
print("z(ER)   C, L, Q =", np.round(z_er, 1).tolist())
print("z(保度) C, L, Q =", np.round(z_ds, 1).tolist())
print("小世界系数 sigma = %.2f" % sigma)

# 作图：每个指标的真实值与两种零模型的 10 次取值
import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 3, figsize=(10, 3.6))
for j, (a, nm) in enumerate(zip(ax, ["clustering C", "path length L", "modularity Q"])):
    a.plot(np.zeros(10) + np.linspace(-0.1, 0.1, 10), er[:, j], "o", color="0.5", ms=4, label="ER")
    a.plot(np.ones(10) + np.linspace(-0.1, 0.1, 10), ds[:, j], "s", color="C0", ms=4, label="degree-preserving")
    a.axhline(real[j], color="C3", lw=2, label="observed")
    a.set_xticks([0, 1]); a.set_xticklabels(["ER", "deg.-pres."]); a.set_xlim(-0.5, 1.5); a.set_title(nm, fontsize=10)
ax[0].legend(fontsize=7)
fig.suptitle(f"Les Miserables vs null models (small-world sigma = {sigma:.2f})", fontsize=11)
plt.tight_layout(); plt.show()

# %% 示例：格式互转——边表、邻接矩阵、稀疏矩阵、GraphML 与 JSON 的往返检查
# 用同一个小网络演示五种表示之间的转换，并在每次转换后检查节点数、边数、权重与属性是否保留。
# 关键点：to_numpy_array / to_scipy_sparse_array 的行列顺序由 nodelist 决定，必须显式给出并保存；
# GraphML 只支持标量属性（字符串、数值、布尔），列表类属性要先转为字符串；读回时节点 id 一律是字符串。
# 输出：每种表示的规模、矩阵对称性、往返后边集是否一致。
import io, csv, json, tempfile, os
import numpy as np
import scipy.sparse as sp
import networkx as nx

G = nx.Graph()
G.add_weighted_edges_from([("TP53", "MDM2", 0.99), ("TP53", "EP300", 0.95), ("EP300", "CREBBP", 0.98),
                           ("MDM2", "MDM4", 0.97), ("CREBBP", "TP53", 0.90)])
G.add_node("ORPHAN1")                                    # 孤立点：边表里看不到它
nx.set_node_attributes(G, {"TP53": "tumor suppressor", "MDM2": "E3 ligase"}, "role")

# 1) 边表（CSV）：孤立点会丢失，需要另存节点表
buf = io.StringIO()
w = csv.writer(buf); w.writerow(["source", "target", "weight"])
for u, v, d in G.edges(data=True):
    w.writerow([u, v, d["weight"]])
rows = list(csv.DictReader(io.StringIO(buf.getvalue())))
G_csv = nx.Graph((r["source"], r["target"], {"weight": float(r["weight"])}) for r in rows)
print("边表往返：%d 节点 / %d 边（原图 %d 节点，孤立点丢失）" % (
    G_csv.number_of_nodes(), G_csv.number_of_edges(), G.number_of_nodes()))

# 2) 稠密与稀疏邻接矩阵：显式固定节点顺序
nodes = sorted(G)
A = nx.to_numpy_array(G, nodelist=nodes, weight="weight")
S = nx.to_scipy_sparse_array(G, nodelist=nodes, weight="weight", format="csr")
print("稠密矩阵 %s，对称：%s；CSR 非零元 %d（无向边各存两次）" % (A.shape, np.allclose(A, A.T), S.nnz))
G_mat = nx.relabel_nodes(nx.from_scipy_sparse_array(S), dict(enumerate(nodes)))
print("稀疏矩阵往返边集一致：%s" % (set(map(frozenset, G_mat.edges())) == set(map(frozenset, G.edges()))))

# 3) GraphML：保留孤立点、权重和标量属性
tmp = tempfile.mkdtemp()
path = os.path.join(tmp, "g.graphml")
nx.write_graphml(G, path)
G_gml = nx.read_graphml(path)
print("GraphML 往返：%d 节点 / %d 边，TP53 的 role = %r，权重类型 %s" % (
    G_gml.number_of_nodes(), G_gml.number_of_edges(), G_gml.nodes["TP53"].get("role"),
    type(next(iter(G_gml.edges(data=True)))[2]["weight"]).__name__))

# 4) node-link JSON：适合网页可视化（如 D3.js）和保存任意可 JSON 化的属性
data = nx.node_link_data(G, edges="links")
G_json = nx.node_link_graph(json.loads(json.dumps(data)), edges="links")
print("JSON 往返：%d 节点 / %d 边" % (G_json.number_of_nodes(), G_json.number_of_edges()))

# 5) 列表属性写 GraphML 会报错，先转成字符串
G.nodes["TP53"]["pathways"] = ["p53 signaling", "apoptosis"]
try:
    nx.write_graphml(G, path)
except Exception as e:
    print("列表属性写 GraphML 失败：%s" % type(e).__name__)
G.nodes["TP53"]["pathways"] = ";".join(G.nodes["TP53"]["pathways"])
nx.write_graphml(G, path)
print("转为分号分隔字符串后写入成功")

# 作图：显式固定 nodelist 后的加权邻接矩阵（行列标签即矩阵顺序；孤立点为全零行列）
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(5.4, 4.2))
im = ax.imshow(A, cmap="Blues", vmin=0, vmax=1)
ax.set_xticks(range(len(nodes))); ax.set_xticklabels(nodes, rotation=45, ha="right", fontsize=8)
ax.set_yticks(range(len(nodes))); ax.set_yticklabels(nodes, fontsize=8)
fig.colorbar(im, ax=ax, label="edge weight")
ax.set_title("Adjacency matrix, nodelist = sorted(G)", fontsize=10)
plt.tight_layout(); plt.show()

# %% 示例：五个常见计算陷阱——自环、重边、孤立点、有向性、权重的含义
# 每个陷阱用一个可手算的小图演示“同一个函数、不同输入表示，数值不同”。
# 解读：（1）自环使度加 2，并影响聚集系数分母；（2）MultiGraph 转 Graph 时重边被合并，权重取最后一条而非求和；
# （3）孤立点改变平均度和密度，并使平均最短路径报错；（4）有向图的 PageRank 与无向化后不同；
# （5）最短路径与介数把 weight 当作“距离”，相关系数之类的“相似度”需先取倒数或 -log 变换。
import numpy as np
import networkx as nx

# (1) 自环
G = nx.Graph([(1, 2), (2, 3), (3, 1), (3, 4)])
H = G.copy(); H.add_edge(3, 3)
print("(1) 节点3的度：无自环 %d，有自环 %d；自环数 %d" % (G.degree(3), H.degree(3), nx.number_of_selfloops(H)))
H.remove_edges_from(nx.selfloop_edges(H))

# (2) 重边：两个实验分别报告了 A–B 相互作用
M = nx.MultiGraph()
M.add_edge("A", "B", weight=1.0); M.add_edge("A", "B", weight=2.0); M.add_edge("B", "C", weight=1.0)
G_last = nx.Graph(M)                                           # 直接转换：保留其中一条的属性
G_sum = nx.Graph()
for u, v, d in M.edges(data=True):                             # 显式聚合：权重相加（或计数、取最大）
    w0 = G_sum[u][v]["weight"] if G_sum.has_edge(u, v) else 0.0
    G_sum.add_edge(u, v, weight=w0 + d["weight"])
print("(2) A–B 权重：直接转换 %.1f，显式求和 %.1f；MultiGraph 边数 %d → Graph 边数 %d" % (
    G_last["A"]["B"]["weight"], G_sum["A"]["B"]["weight"], M.number_of_edges(), G_sum.number_of_edges()))

# (3) 孤立点
G = nx.path_graph(5); G.add_nodes_from([10, 11, 12])
print("(3) 平均度：含孤立点 %.2f，去除后 %.2f；密度 %.3f vs %.3f" % (
    2 * G.number_of_edges() / G.number_of_nodes(), 2 * 4 / 5, nx.density(G), nx.density(nx.path_graph(5))))
try:
    nx.average_shortest_path_length(G)
except nx.NetworkXError as e:
    print("    平均最短路径：", e)

# (4) 有向性：调控链 TF1 → TF2 → TF3 → TF4
D = nx.DiGraph([("TF1", "TF2"), ("TF2", "TF3"), ("TF3", "TF4")])
pr_d = nx.pagerank(D); pr_u = nx.pagerank(D.to_undirected())
print("(4) PageRank（有向）：", {k: round(v, 3) for k, v in pr_d.items()})
print("    PageRank（无向化）：", {k: round(v, 3) for k, v in pr_u.items()})
print("    弱连通 %s，强连通 %s" % (nx.is_weakly_connected(D), nx.is_strongly_connected(D)))

# (5) 权重是相似度还是距离：A–B–C 两条强相关边，A–C 一条弱相关边
S = nx.Graph()
S.add_edge("A", "B", r=0.9); S.add_edge("B", "C", r=0.9); S.add_edge("A", "C", r=0.2)
for u, v, d in S.edges(data=True):
    d["dist_inv"] = 1 / d["r"]                  # 距离 = 1/相似度
    d["dist_log"] = -np.log(d["r"])             # 距离 = -log(相似度)，路径长度对应相似度乘积
print("(5) A→C 最短路径：把 r 误当距离 %s；1/r %s；-log r %s" % (
    nx.shortest_path(S, "A", "C", weight="r"), nx.shortest_path(S, "A", "C", weight="dist_inv"),
    nx.shortest_path(S, "A", "C", weight="dist_log")))
print("    B 的介数：误用 r %.2f，用 1/r %.2f" % (
    nx.betweenness_centrality(S, weight="r")["B"], nx.betweenness_centrality(S, weight="dist_inv")["B"]))

# 作图：陷阱 (4)——同一条调控链，有向与无向化后的 PageRank
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(6.4, 4.2))
tf = list(D.nodes()); x = np.arange(len(tf))
ax.bar(x - 0.2, [pr_d[v] for v in tf], 0.4, label="directed")
ax.bar(x + 0.2, [pr_u[v] for v in tf], 0.4, label="undirected")
ax.set_xticks(x); ax.set_xticklabels(tf); ax.set_ylabel("PageRank"); ax.legend()
ax.set_title("Chain TF1->TF2->TF3->TF4: direction changes the ranking", fontsize=10)
plt.tight_layout(); plt.show()

# %% 示例：大规模网络的计算策略——稀疏矩阵、近似介数与抽样偏倚
# （a）2 万节点的 BA 网络：比较稠密与 CSR 稀疏矩阵的内存，用 scipy.sparse.csgraph 求连通分支、
#     用 scipy.sparse.linalg.eigsh 求最大特征值；（b）在 2000 节点网络上比较精确介数与 k 个源点抽样的近似介数
#     （Spearman 秩相关与前 20 名重合数、耗时）；（c）随机抽取 20% 节点得到诱导子图，平均度与最大度如何变化。
# 解读：稀疏存储的内存与边数成正比；抽样介数对“前几名”的排序通常已足够稳定；
# 诱导子图的度会按抽样比例整体缩小，由子图估计的度分布不能直接代表全网络。
import time
import numpy as np
import scipy.sparse as sp
import scipy.sparse.csgraph as csg
import scipy.sparse.linalg as sla
from scipy.stats import spearmanr
import networkx as nx

# (a) 稀疏矩阵
G = nx.barabasi_albert_graph(20000, 3, seed=1)
A = nx.to_scipy_sparse_array(G, format="csr", dtype=np.float64)
dense_mb = G.number_of_nodes() ** 2 * 8 / 1e6
sparse_mb = (A.data.nbytes + A.indices.nbytes + A.indptr.nbytes) / 1e6
print("(a) N=%d, M=%d；稠密矩阵约 %.0f MB，CSR 约 %.2f MB" % (G.number_of_nodes(), G.number_of_edges(), dense_mb, sparse_mb))
deg = np.asarray(A.sum(axis=1)).ravel()
ncomp, labels = csg.connected_components(A, directed=False)
lam = sla.eigsh(A, k=1, which="LA", return_eigenvectors=False)[0]
print("    最大度 %d，连通分支 %d 个，邻接矩阵最大特征值 %.2f" % (deg.max(), ncomp, lam))

# (b) 近似介数
G2 = nx.barabasi_albert_graph(2000, 3, seed=2)
t0 = time.perf_counter(); bc = nx.betweenness_centrality(G2); t_exact = time.perf_counter() - t0
nodes = list(G2)
exact = np.array([bc[v] for v in nodes])
top_exact = set(np.argsort(-exact)[:20])
for k in (50, 200):
    t0 = time.perf_counter(); bck = nx.betweenness_centrality(G2, k=k, seed=0); t_k = time.perf_counter() - t0
    approx = np.array([bck[v] for v in nodes])
    rho = spearmanr(exact, approx).correlation
    overlap = len(top_exact & set(np.argsort(-approx)[:20]))
    print("(b) k=%3d：耗时 %.2fs（精确 %.2fs），Spearman ρ = %.3f，前20名重合 %d/20" % (k, t_k, t_exact, rho, overlap))

# (c) 节点抽样的诱导子图
rng = np.random.default_rng(3)
sub_nodes = rng.choice(G.number_of_nodes(), size=G.number_of_nodes() // 5, replace=False)
Gs = G.subgraph(sub_nodes)
d_full = np.array([d for _, d in G.degree()]); d_sub = np.array([d for _, d in Gs.degree()])
print("(c) 全网络：平均度 %.2f，最大度 %d；20%% 节点诱导子图：平均度 %.2f，最大度 %d，孤立点 %d 个" % (
    d_full.mean(), d_full.max(), d_sub.mean(), d_sub.max(), int((d_sub == 0).sum())))

# 作图：精确介数 vs 抽样近似介数（k=200）；全网络与 20% 诱导子图的度分布
import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 2, figsize=(10, 4))
ax[0].loglog(exact[exact > 0], approx[exact > 0], ".", ms=3, alpha=0.5)
lim = [exact[exact > 0].min(), exact.max()]; ax[0].plot(lim, lim, "k--", lw=1)
ax[0].set_xlabel("exact betweenness"); ax[0].set_ylabel("approximate betweenness (k=200)")
ax[0].set_title(f"Sampled betweenness ranks hubs well (rho = {rho:.2f})", fontsize=10)
for dv, lab, mk in [(d_full, "full network", "o"), (d_sub[d_sub > 0], "20% induced subgraph", "s")]:
    v_, c_ = np.unique(dv, return_counts=True)
    ax[1].loglog(v_, c_ / c_.sum(), mk, ms=3, label=lab)
ax[1].set_xlabel("degree k"); ax[1].set_ylabel("P(k)"); ax[1].legend(fontsize=8)
ax[1].set_title("Node sampling shifts degrees downward", fontsize=10)
plt.tight_layout(); plt.show()

# %% 示例：布局算法比较与布局质量的定量检查
# 在一个有 4 个植入模块的随机分块网络（SBM）上比较五种布局：spring（Fruchterman–Reingold）、
# Kamada–Kawai、谱布局、ForceAtlas2 与按模块分层的 multipartite 布局。
# 用“图距离与欧氏距离的 Spearman 相关”衡量布局对网络距离的保真程度，并计算同模块节点对与异模块节点对
# 的平均欧氏距离之比（越小说明模块在图上越分得开）。输出各布局的两项指标与一张 5 联图。
# 解读：不同布局优化不同目标，看起来“分得开”的模块可能部分是布局算法造成的，不应仅凭网络图下结论。
import numpy as np
import networkx as nx
import matplotlib
import matplotlib.pyplot as plt
from scipy.stats import spearmanr

sizes = [25, 25, 25, 25]
P = np.full((4, 4), 0.01) + np.eye(4) * 0.24
G = nx.stochastic_block_model(sizes, P.tolist(), seed=7)
G = G.subgraph(max(nx.connected_components(G), key=len)).copy()
block = {v: G.nodes[v]["block"] for v in G}
nx.set_node_attributes(G, block, "layer")

layouts = {
    "spring": nx.spring_layout(G, seed=1),
    "kamada_kawai": nx.kamada_kawai_layout(G),
    "spectral": nx.spectral_layout(G),
    "forceatlas2": nx.forceatlas2_layout(G, seed=1, max_iter=300),
    "multipartite": nx.multipartite_layout(G, subset_key="layer"),
}
nodes = list(G)
spl = dict(nx.all_pairs_shortest_path_length(G))
iu = np.triu_indices(len(nodes), 1)
gd = np.array([[spl[u][v] for v in nodes] for u in nodes])[iu]
same = np.array([[block[u] == block[v] for v in nodes] for u in nodes])[iu]

fig, axes = plt.subplots(1, 5, figsize=(16, 3.4))
for ax, (name, pos) in zip(axes, layouts.items()):
    X = np.array([pos[v] for v in nodes])
    ed = np.sqrt(((X[:, None, :] - X[None, :, :]) ** 2).sum(-1))[iu]
    rho = spearmanr(gd, ed).correlation
    ratio = ed[same].mean() / ed[~same].mean()
    print("%-13s 图距离–欧氏距离 ρ = %.2f，同模块/异模块平均距离比 = %.2f" % (name, rho, ratio))
    nx.draw_networkx(G, pos, ax=ax, node_size=25, with_labels=False, width=0.3,
                     node_color=[block[v] for v in nodes], cmap="tab10", vmin=0, vmax=9)
    ax.set_title("%s (rho=%.2f)" % (name, rho), fontsize=9); ax.axis("off")
plt.tight_layout(); plt.show()

# %% 示例：完整案例——从模拟表达矩阵到共表达模块、枢纽基因与“疾病基因是否成团”的检验
# 数据：代码生成的模拟表达矩阵（200 个基因 × 60 个样本），含 4 个由潜在因子驱动的共表达模块与 40 个噪声基因；
#       另设一个 12 个基因的“疾病基因集”（8 个来自模块 0，4 个随机）。全部为模拟数据，仅演示流程。
# 流程：质控（去除低方差基因）→ Spearman 相关 → 置换得到的相关阈值与 Benjamini–Hochberg FDR 控制 →
#       建网并报告孤立点 → Louvain 模块并与植入模块对照（ARI）→ 模块内连接度找枢纽基因 →
#       疾病基因集诱导子图最大连通分支（LCC）与度匹配随机基因集比较（经验 p 值）→ 换 FDR 水平做敏感性分析。
# 解读：结论应写成“在本网络构建方式下，疾病基因集的 LCC 显著大于度匹配随机期望，且对 FDR 水平稳健”，
#       而不是“这些基因构成致病模块”。
import numpy as np
import networkx as nx
from scipy.stats import spearmanr, norm

rng = np.random.default_rng(2026)
n_samples, mod_sizes, n_noise = 60, [40, 40, 40, 40], 40
blocks, X = [], []
for m, s in enumerate(mod_sizes):
    f = rng.normal(size=n_samples)                                  # 模块的潜在驱动因子
    load = rng.uniform(0.5, 0.9, size=s)
    X.append(load[:, None] * f[None, :] + np.sqrt(1 - load[:, None] ** 2) * rng.normal(size=(s, n_samples)))
    blocks += [m] * s
X.append(rng.normal(size=(n_noise, n_samples))); blocks += [-1] * n_noise
X = np.vstack(X) * rng.uniform(0.2, 2.0, size=(len(blocks), 1))      # 基因间表达尺度不同
X[-5:] *= 0.01                                                      # 5 个几乎不表达变化的基因
genes = np.array(["G%03d" % i for i in range(len(blocks))]); blocks = np.array(blocks)

# 1) 质控：去除方差最低的基因
keep = X.var(axis=1) > 0.01
X, genes, blocks = X[keep], genes[keep], blocks[keep]
print("1) 质控后基因数：%d（去除 %d 个低方差基因）" % (len(genes), int((~keep).sum())))

# 2) Spearman 相关与 FDR 控制（大样本近似：Fisher z 变换后用正态分布求 p 值）
R = spearmanr(X, axis=1).correlation
iu = np.triu_indices(len(genes), 1)
r = R[iu]
z = np.arctanh(np.clip(r, -0.999999, 0.999999)) * np.sqrt((n_samples - 3) / 1.06)
p = 2 * norm.sf(np.abs(z))

def bh_reject(p, q):
    order = np.argsort(p); m = len(p)
    passed = p[order] <= q * np.arange(1, m + 1) / m
    k = passed.nonzero()[0].max() + 1 if passed.any() else 0
    rej = np.zeros(m, bool); rej[order[:k]] = True
    return rej

def build(q, positive_only=True):
    rej = bh_reject(p, q) & ((r > 0) if positive_only else True)
    H = nx.Graph(); H.add_nodes_from(genes)
    H.add_weighted_edges_from((genes[i], genes[j], r_ij) for i, j, r_ij in zip(iu[0][rej], iu[1][rej], r[rej]))
    return H

G = build(0.01)
iso = [v for v in G if G.degree(v) == 0]
print("2) FDR=0.01 且 r>0：%d 条边，密度 %.3f，孤立基因 %d 个（其中噪声基因 %d 个）" % (
    G.number_of_edges(), nx.density(G), len(iso), int(sum(blocks[genes == v][0] == -1 for v in iso))))
G.remove_nodes_from(iso)

# 3) Louvain 模块与植入模块对照（调整兰德指数 ARI）
def ari(a, b):
    from math import comb
    a = np.unique(a, return_inverse=True)[1]; b = np.unique(b, return_inverse=True)[1]
    C = np.zeros((a.max() + 1, b.max() + 1), int)
    for i, j in zip(a, b): C[i, j] += 1
    s = sum(comb(int(x), 2) for x in C.ravel())
    sa = sum(comb(int(x), 2) for x in C.sum(1)); sb = sum(comb(int(x), 2) for x in C.sum(0))
    e = sa * sb / comb(len(a), 2)
    return (s - e) / (0.5 * (sa + sb) - e)

comms = nx.community.louvain_communities(G, weight="weight", seed=1)
lab = {v: k for k, c in enumerate(comms) for v in c}
nodes = list(G)
true = [blocks[genes == v][0] for v in nodes]
print("3) Louvain：%d 个模块，Q = %.3f，与植入模块 ARI = %.3f" % (
    len(comms), nx.community.modularity(G, comms, weight="weight"), ari([lab[v] for v in nodes], true)))

# 4) 模块内连接度（模块内强度）最高的基因作为候选枢纽
for k, c in enumerate(sorted(comms, key=len, reverse=True)[:4]):
    sub = G.subgraph(c)
    hub = max(sub.degree(weight="weight"), key=lambda x: x[1])
    print("4) 模块 %d（%d 个基因）枢纽：%s，模块内强度 %.1f" % (k, len(c), hub[0], hub[1]))

# 5) 疾病基因集是否成团：两种统计量（LCC 大小、集合内部边数）与度匹配随机基因集比较
mod0 = genes[blocks == 0]; others = genes[blocks != 0]
disease = list(rng.choice(mod0, 8, replace=False)) + list(rng.choice(others, 4, replace=False))

def stats(H, S):
    sub = H.subgraph([v for v in S if v in H])
    return np.array([max((len(c) for c in nx.connected_components(sub)), default=0), sub.number_of_edges()])

def degree_matched_test(H, S, n_perm=1000, n_bins=10, seed=0):
    rng_ = np.random.default_rng(seed)
    S = [v for v in S if v in H]
    deg = dict(H.degree())
    cuts = np.quantile(list(deg.values()), np.linspace(0, 1, n_bins + 1))
    bin_of = {v: min(np.searchsorted(cuts, deg[v], side="right") - 1, n_bins - 1) for v in H}
    pool = {}
    for v, b in bin_of.items(): pool.setdefault(b, []).append(v)
    obs = stats(H, S)
    null = []
    for _ in range(n_perm):
        R_ = []
        for v in S:                                     # 每个疾病基因换成同一度区间内的随机基因
            cand = [u for u in pool[bin_of[v]] if u not in R_]
            R_.append(cand[rng_.integers(len(cand))])
        null.append(stats(H, R_))
    null = np.array(null)
    pv = (1 + (null >= obs).sum(0)) / (n_perm + 1)
    return obs, null.mean(0), null.std(0), pv

obs, mu, sd, pv = degree_matched_test(G, disease)
print("5) 疾病基因集：%d 个在网络中" % sum(v in G for v in disease))
for i, name in enumerate(["LCC 大小", "内部边数"]):
    print("   %s：观测 %d，度匹配随机 %.1f ± %.1f，z = %.1f，经验 p = %.4f" % (
        name, obs[i], mu[i], sd[i], (obs[i] - mu[i]) / sd[i], pv[i]))

# 6) 敏感性分析：换 FDR 水平重建网络，两种统计量是否给出一致结论
sens = [(0.01, obs[0], mu[0], sd[0])]                    # 保存 LCC 结果用于作图
for q in (0.001, 0.05, 0.1):
    H = build(q); H.remove_nodes_from([v for v in H if H.degree(v) == 0])
    o, m_, s_, pv = degree_matched_test(H, disease, n_perm=500, seed=1)
    sens.append((q, o[0], m_[0], s_[0]))
    print("6) FDR=%.3f：%d 边；LCC %d（随机 %.1f，p=%.3f）；内部边 %d（随机 %.1f，p=%.3f）" % (
        q, H.number_of_edges(), o[0], m_[0], pv[0], o[1], m_[1], pv[1]))

# 作图：按 Louvain 模块排序的基因相关矩阵；不同 FDR 水平下疾病基因集 LCC 与度匹配随机期望
import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 2, figsize=(10, 4))
idx = {g: i for i, g in enumerate(genes)}
order = [idx[v] for c in sorted(comms, key=len, reverse=True) for v in sorted(c)]
im = ax[0].imshow(R[np.ix_(order, order)], cmap="RdBu_r", vmin=-1, vmax=1)
fig.colorbar(im, ax=ax[0], label="Spearman r"); ax[0].set_xticks([]); ax[0].set_yticks([])
ax[0].set_title("Gene correlations ordered by Louvain module", fontsize=10)
sens.sort()
qs = [s_[0] for s_ in sens]
ax[1].errorbar(qs, [s_[2] for s_ in sens], yerr=[s_[3] for s_ in sens], fmt="s--", color="0.5", capsize=3,
               label="degree-matched random (mean +/- SD)")
ax[1].plot(qs, [s_[1] for s_ in sens], "o-", color="C3", label="disease gene set")
ax[1].set_xscale("log"); ax[1].set_xlabel("FDR level q"); ax[1].set_ylabel("largest connected component size")
ax[1].set_title("Disease-module signal is robust to FDR level", fontsize=10); ax[1].legend(fontsize=8)
plt.tight_layout(); plt.show()
