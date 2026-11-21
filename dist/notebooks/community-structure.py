# 依赖：networkx（leiden_communities 需较新版本；本站环境为 3.7）, numpy, scipy, matplotlib
# 数据：Zachary 空手道俱乐部网络（NetworkX 内置 karate_club_graph()；节点属性 "club" 记录
#       分裂后每个成员所在的一派，"Mr. Hi" 为教练一派）。此处去掉边权，按无权网络计算。
#       另有“两个三角形 + 一条桥”等手写小网络，以及由代码生成的 ER 随机网络、随机块模型（SBM）、
#       LFR 基准网络、团环（ring of cliques）和时变多层网络。所有随机数据均固定种子，可复现。

# %% 示例：按定义计算模块度
# 用按社团求和的公式 Q = Σ_c [ l_c/m - (d_c / 2m)^2 ]（l_c：社团内部边数；d_c：社团度之和）计算：
#   (a) “两个三角形 + 一条桥”的小网络按两个三角形划分时的 Q（手算约 0.357）；
#   (b) 空手道俱乐部按真实分裂的两派划分时的 Q。
# 输出：按定义计算的结果与 nx.community.modularity 一致。
import networkx as nx


def my_modularity(G, communities):
    m = G.number_of_edges()
    Q = 0.0
    for c in communities:
        l_c = G.subgraph(c).number_of_edges()
        d_c = sum(d for _, d in G.degree(c))
        Q += l_c / m - (d_c / (2 * m)) ** 2
    return Q


H = nx.Graph([(1, 2), (2, 3), (1, 3), (4, 5), (5, 6), (4, 6), (3, 4)])
parts_H = [{1, 2, 3}, {4, 5, 6}]

K = nx.karate_club_graph()
G = nx.Graph(K.edges())                       # 去掉边权，按无权网络计算
club = [{n for n in K if K.nodes[n]["club"] == "Mr. Hi"},
        {n for n in K if K.nodes[n]["club"] != "Mr. Hi"}]

print("两个三角形: 按定义 Q=%.3f, NetworkX=%.3f" % (my_modularity(H, parts_H), nx.community.modularity(H, parts_H)))
print("两个三角形放在同一社团: Q=%.3f" % my_modularity(H, [set(H)]))
print("空手道真实两派: 按定义 Q=%.3f, NetworkX=%.3f" % (my_modularity(G, club), nx.community.modularity(G, club)))

# 作图：两个网络按给定划分着色，标题给出 Q
import matplotlib.pyplot as plt

fig, axes = plt.subplots(1, 2, figsize=(10, 4))
for ax, (net, parts, name, seed) in zip(axes, [(H, parts_H, "two triangles + bridge", 0), (G, club, "karate club, true factions", 4)]):
    lab = {v: i for i, c in enumerate(parts) for v in c}
    pos = nx.spring_layout(net, seed=seed)
    nx.draw_networkx_edges(net, pos, ax=ax, edge_color="0.6", alpha=0.5)
    nx.draw_networkx_nodes(net, pos, ax=ax, node_size=300 if net is H else 90,
                           node_color=["#fdb863" if lab[v] == 0 else "#8073ac" for v in net], edgecolors="0.3")
    if net is H:
        nx.draw_networkx_labels(net, pos, ax=ax, font_size=9)
    ax.set_title("%s: Q = %.3f" % (name, my_modularity(net, parts)), fontsize=10); ax.axis("off")
plt.tight_layout(); plt.show()


# %% 示例：Girvan–Newman 算法
# 对空手道网络运行 Girvan–Newman（反复删除边介数最大的边，每次删边后重新计算边介数），
# 记录每一层划分的社团数与模块度，选出 Q 最大的一层；再把第一次分裂（2 个社团）与真实两派比较。
# 输出：Q 在 5 个社团时达到最大（约 0.40）；第一次分裂只有个别节点与真实分派不同。
import networkx as nx
import matplotlib.pyplot as plt

K = nx.karate_club_graph()
G = nx.Graph(K.edges())
truth = {n: K.nodes[n]["club"] for n in K}

levels = []                                   # [(社团数, Q, 划分), ...]
for comms in nx.community.girvan_newman(G):
    comms = [set(c) for c in comms]
    levels.append((len(comms), nx.community.modularity(G, comms), comms))
    if len(comms) >= 10:
        break

for n_c, q, _ in levels:
    print("社团数 %2d  Q = %.3f" % (n_c, q))
best = max(levels, key=lambda x: x[1])
print("最佳：%d 个社团，Q = %.3f" % (best[0], best[1]))
first = levels[0][2]
side_hi = first[0] if 0 in first[0] else first[1]           # 教练 0 号所在的一侧
wrong = [n for n in G if (n in side_hi) != (truth[n] == "Mr. Hi")]
print("第一次分裂中与真实分派不一致的节点:", wrong)

plt.plot([x[0] for x in levels], [x[1] for x in levels], "o-")
plt.xlabel("number of communities")
plt.ylabel("modularity Q")
plt.title("Girvan–Newman on karate club")
plt.show()


# %% 示例：Louvain、分辨率参数与随机网络的模块度
# (a) 用 Louvain 在不同分辨率参数 γ 下划分空手道网络，观察社团数和（γ=1 时的）Q 的变化；
# (b) 生成 20 个与空手道网络节点数、边数相同的 ER 随机网络，同样用 Louvain 求 Q，计算真实网络 Q 的 z 分数。
# 输出：γ 越大社团越多；没有真实社团的随机网络 Q 约 0.35，真实网络约 0.42，绝对差距并不大，
#       说明 Q 的绝对值不能单独证明社团结构显著，需要与零模型的分布比较（z 分数）。
# 更严格的零模型是保持度序列的随机网络（nx.double_edge_swap），用法见小世界与无标度网络模型的代码示例。
import networkx as nx
import numpy as np

K = nx.karate_club_graph()
G = nx.Graph(K.edges())
n, m = G.number_of_nodes(), G.number_of_edges()

n_comm = []                                    # 存下结果用于作图
for gamma in [0.5, 1.0, 1.5, 2.0]:
    comms = nx.community.louvain_communities(G, resolution=gamma, seed=1)
    n_comm.append(len(comms))
    print("γ=%.1f: %d 个社团, Q(γ=1) = %.3f" % (gamma, len(comms), nx.community.modularity(G, comms)))

Q_real = nx.community.modularity(G, nx.community.louvain_communities(G, seed=1))

Q_rand = []
for s in range(20):
    R = nx.gnm_random_graph(n, m, seed=s)
    Q_rand.append(nx.community.modularity(R, nx.community.louvain_communities(R, seed=s)))
Q_rand = np.array(Q_rand)
print("真实网络 Q = %.3f；随机网络 Q = %.3f ± %.3f" % (Q_real, Q_rand.mean(), Q_rand.std()))
print("z 分数 = %.1f" % ((Q_real - Q_rand.mean()) / Q_rand.std()))

# 作图：左为社团数随分辨率 γ 的变化；右为随机网络 Q 的分布与真实网络 Q
import matplotlib.pyplot as plt

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
ax1.plot([0.5, 1.0, 1.5, 2.0], n_comm, "o-")
ax1.set_xlabel("resolution gamma"); ax1.set_ylabel("number of communities")
ax1.set_title("Higher resolution -> more communities", fontsize=10)
ax2.hist(Q_rand, bins=8, color="#92c5de", edgecolor="white", label="ER graphs (20)")
ax2.axvline(Q_real, color="#d6604d", lw=2, label="karate club")
ax2.set_xlabel("modularity Q (Louvain)"); ax2.set_ylabel("count"); ax2.legend(fontsize=8)
ax2.set_title("Random graphs also reach Q ~ %.2f; z = %.1f" % (Q_rand.mean(), (Q_real - Q_rand.mean()) / Q_rand.std()), fontsize=10)
plt.tight_layout(); plt.show()


# %% 示例：谱方法——模块度矩阵的主特征向量
# 构造模块度矩阵 B = A - k k^T / 2m，求最大特征值对应的特征向量 u，
# 按 u 分量的正负号把节点分成两组（谱二分），计算 Q，并与真实两派比较。
# |u_i| 很小的节点处于两组“之间”，归属最不确定。
# 输出：最大特征值为正（网络可分）；只靠一次特征分解，就几乎完全复现了俱乐部的分裂。
import networkx as nx
import numpy as np

K = nx.karate_club_graph()
G = nx.Graph(K.edges())
nodes = sorted(G.nodes())
A = nx.to_numpy_array(G, nodelist=nodes)
k = A.sum(axis=1)
m = A.sum() / 2

B = A - np.outer(k, k) / (2 * m)
vals, vecs = np.linalg.eigh(B)              # 特征值按升序排列
u = vecs[:, -1]
print("最大特征值 β1 = %.3f；B 的行和最大绝对值 = %.1e" % (vals[-1], np.abs(B.sum(axis=1)).max()))

part = [{n for n, x in zip(nodes, u) if x >= 0}, {n for n, x in zip(nodes, u) if x < 0}]
print("两组大小:", [len(p) for p in part], " Q = %.3f" % nx.community.modularity(G, part))
side_hi = part[0] if 0 in part[0] else part[1]
wrong = [n for n in nodes if (n in side_hi) != (K.nodes[n]["club"] == "Mr. Hi")]
print("与真实分派不一致的节点:", wrong)
print("|u| 最小的 3 个节点（处于两派“中间”）:", [nodes[i] for i in np.argsort(np.abs(u))[:3]])

# 作图：左为主特征向量各分量（按真实派别着色）；右为按符号二分的网络
import matplotlib.pyplot as plt

hi = np.array([K.nodes[n]["club"] == "Mr. Hi" for n in nodes])
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
order = np.argsort(u)
ax1.bar(range(len(nodes)), u[order], color=np.where(hi[order], "#fdb863", "#8073ac"))
ax1.axhline(0, color="0.3", lw=0.8)
ax1.set_xlabel("nodes sorted by u_i"); ax1.set_ylabel("leading eigenvector u_i")
ax1.plot([], [], "s", color="#fdb863", label="Mr. Hi"); ax1.plot([], [], "s", color="#8073ac", label="Officer")
ax1.legend(fontsize=8); ax1.set_title("Sign of u splits the club (beta1 = %.2f)" % vals[-1], fontsize=10)
pos = nx.spring_layout(G, seed=4)
nx.draw_networkx_edges(G, pos, ax=ax2, edge_color="0.7", alpha=0.4)
nx.draw_networkx_nodes(G, pos, ax=ax2, nodelist=nodes, node_color=u, cmap="PuOr", vmin=-np.abs(u).max(),
                       vmax=np.abs(u).max(), node_size=90, edgecolors=["red" if n in wrong else "0.4" for n in nodes])
ax2.set_title("Node colour = u_i; Q = %.3f, misassigned: %s" % (nx.community.modularity(G, part), wrong), fontsize=10)
ax2.axis("off"); plt.tight_layout(); plt.show()


# %% 示例：划分空间有多大——Bell 数与小网络上的穷举最优模块度
# 节点数为 N 的网络共有 Bell 数 B_N 种划分；只考虑等分二分也有 C(N, N/2)/2 种。
# 先打印这些数随 N 的增长，再在一个 10 节点网络上穷举全部 B_10 = 115975 种划分，
# 找到精确的最大模块度划分，并与 Louvain（多个随机种子）的结果比较。
# 输出：N=50 时划分数超过 10^47，穷举不可行；在小网络上 Louvain 达到或接近精确最优。
from math import comb
import networkx as nx
import numpy as np


def bell_numbers(n_max):
    """用 Bell 三角形计算 B_0..B_{n_max}。"""
    row, bells = [1], [1]
    for _ in range(n_max):
        new = [row[-1]]
        for x in row:
            new.append(new[-1] + x)
        row = new
        bells.append(row[0])
    return bells


B = bell_numbers(50)
for N in [6, 10, 20, 50]:
    print("N=%2d  Bell 数 B_N = %.3e   等分二分数 = %.3e" % (N, B[N], comb(N, N // 2) / 2))


def set_partitions(n):
    """以“受限增长串”枚举 {0..n-1} 的全部划分：label[0]=0，label[i] ≤ max(label[:i])+1。"""
    labels = [0] * n

    def rec(i, mx):
        if i == n:
            yield labels
            return
        for c in range(mx + 2):
            labels[i] = c
            yield from rec(i + 1, max(mx, c))

    yield from rec(1, 0)


G = nx.Graph([(0, 1), (0, 2), (1, 2), (2, 3), (3, 4), (3, 5), (4, 5), (5, 6),
              (6, 7), (6, 8), (7, 8), (8, 9), (7, 9), (1, 4), (0, 9)])
n = G.number_of_nodes()
A = nx.to_numpy_array(G, nodelist=range(n))
k = A.sum(1)
m = A.sum() / 2
Bmat = A - np.outer(k, k) / (2 * m)

best_q, best_lab, count = -1.0, None, 0
for lab in set_partitions(n):
    count += 1
    lab_arr = np.array(lab)
    q = Bmat[lab_arr[:, None] == lab_arr[None, :]].sum() / (2 * m)
    if q > best_q + 1e-12:
        best_q, best_lab = q, lab_arr.copy()
print("穷举了 %d 种划分（应等于 B_10 = %d）" % (count, B[10]))
print("精确最大模块度 Q* = %.4f，最优划分标签:" % best_q, best_lab.tolist())

q_louvain = [nx.community.modularity(G, nx.community.louvain_communities(G, seed=s)) for s in range(20)]
print("Louvain 20 个种子：Q 最大 %.4f，最小 %.4f" % (max(q_louvain), min(q_louvain)))

# 作图：左为划分数随 N 的增长（对数纵轴）；右为 10 节点网络的精确最优划分
import matplotlib.pyplot as plt

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
Ns = np.arange(2, 51)
ax1.semilogy(Ns, [float(B[N]) for N in Ns], "-", label="Bell number B_N (all partitions)")
ax1.semilogy(Ns, [comb(N, N // 2) / 2 for N in Ns], "--", label="balanced bisections")
ax1.set_xlabel("number of nodes N"); ax1.set_ylabel("count (log scale)"); ax1.legend(fontsize=8)
ax1.set_title("Partition space explodes: B_50 = %.1e" % B[50], fontsize=10)
pos = nx.spring_layout(G, seed=1)
nx.draw_networkx_edges(G, pos, ax=ax2, edge_color="0.6", alpha=0.5)
nx.draw_networkx_nodes(G, pos, ax=ax2, nodelist=range(n), node_color=best_lab, cmap="Set2", node_size=300, edgecolors="0.3")
nx.draw_networkx_labels(G, pos, ax=ax2, font_size=9)
ax2.set_title("Exact optimum Q* = %.4f; best Louvain Q = %.4f" % (best_q, max(q_louvain)), fontsize=10); ax2.axis("off")
plt.tight_layout(); plt.show()


# %% 示例：划分之间的比较——NMI、ARI 与信息变差（VI）
# 不依赖 scikit-learn，直接由列联表（contingency table）计算三种指标：
#   NMI = 2 I(X;Y) / [H(X)+H(Y)]，ARI（Hubert–Arabie 校正），VI = H(X)+H(Y)-2I(X;Y)（以 bit 计）。
# (a) 手算例：6 个节点，真实划分 {0,1,2}{3,4,5}，检测划分把节点 2 错放到第二组；
# (b) “随机划分”基线：把节点随机分成很多小组时 NMI 仍明显大于 0，ARI 则接近 0。
# 输出：(a) NMI≈0.48、ARI≈0.32、VI=1 bit；(b) 随机划分组数越多，NMI 的“虚高”越明显，这是用 ARI 或校正 NMI 的理由。
import numpy as np


def contingency(x, y):
    xs, xi = np.unique(x, return_inverse=True)
    ys, yi = np.unique(y, return_inverse=True)
    T = np.zeros((len(xs), len(ys)))
    np.add.at(T, (xi, yi), 1)
    return T


def entropy(p):
    p = p[p > 0]
    return -(p * np.log2(p)).sum()


def nmi_vi(x, y):
    T = contingency(x, y)
    P = T / T.sum()
    hx, hy, hxy = entropy(P.sum(1)), entropy(P.sum(0)), entropy(P.ravel())
    mi = hx + hy - hxy
    nmi = 2 * mi / (hx + hy) if hx + hy > 0 else 1.0
    return nmi, hx + hy - 2 * mi


def ari(x, y):
    T = contingency(x, y)
    c2 = lambda v: v * (v - 1) / 2
    s_ij, s_a, s_b, n2 = c2(T).sum(), c2(T.sum(1)).sum(), c2(T.sum(0)).sum(), c2(T.sum())
    expected = s_a * s_b / n2
    return (s_ij - expected) / (0.5 * (s_a + s_b) - expected)


truth = [0, 0, 0, 1, 1, 1]
found = [0, 0, 1, 1, 1, 1]
nmi, vi = nmi_vi(truth, found)
print("(a) NMI = %.3f, ARI = %.3f, VI = %.3f bit" % (nmi, ari(truth, found), vi))

rng = np.random.default_rng(0)
n = 200
truth = np.repeat([0, 1, 2, 3], n // 4)
baseline = []                                  # 存下结果用于作图
for q in [4, 20, 50]:
    vals = [(nmi_vi(truth, rng.integers(0, q, n))[0], ari(truth, rng.integers(0, q, n))) for _ in range(50)]
    vals = np.array(vals)
    print("(b) 随机划分为 %2d 组: 平均 NMI = %.3f, 平均 ARI = %+.3f" % (q, vals[:, 0].mean(), vals[:, 1].mean()))
    baseline.append((q, vals[:, 0].mean(), vals[:, 1].mean()))

# 作图：随机划分与 4 组真实划分比较时的 NMI 与 ARI
import matplotlib.pyplot as plt

qs, nmis, aris = zip(*baseline)
x = np.arange(len(qs))
fig, ax = plt.subplots(figsize=(6.4, 4.2))
ax.bar(x - 0.18, nmis, 0.36, color="#4393c3", label="NMI")
ax.bar(x + 0.18, aris, 0.36, color="#d6604d", label="ARI")
for i in range(len(qs)):
    ax.text(i - 0.18, nmis[i] + 0.005, "%.3f" % nmis[i], ha="center", fontsize=9)
    ax.text(i + 0.18, max(aris[i], 0) + 0.005, "%.3f" % aris[i], ha="center", fontsize=9)
ax.axhline(0, color="0.3", lw=0.8)
ax.set_xticks(x); ax.set_xticklabels(["random, %d groups" % q for q in qs])
ax.set_ylabel("similarity to true partition"); ax.legend(fontsize=8)
ax.set_title("NMI inflates for random partitions; ARI stays ~0", fontsize=10)
plt.tight_layout(); plt.show()


# %% 示例：随机块模型与可检测性阈值
# 用两组等大的种植划分模型（planted partition SBM）生成稀疏网络：组内连边概率 c_in/n，组间 c_out/n，
# 平均度 c = (c_in + c_out)/2 固定为 5。理论（Decelle 等 2011）给出：当 |c_in - c_out| ≤ 2√c 时，
# 任何算法都无法以优于随机猜测的准确率恢复分组。这里用 Bethe Hessian 谱方法
# H(r) = (r²-1)I - rA + D，r = √c（Saade 等 2014）与模块度矩阵谱二分恢复分组，
# 用“重叠度” overlap = 2·(正确比例) - 1（0 为随机猜测，1 为完全恢复）衡量。
# 输出：overlap 在阈值（Δc/2√c = 1）附近由约 0 开始上升；模块度谱方法在稀疏网络上通常更差。
import networkx as nx
import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import LinearOperator, eigsh

n, c = 4000, 5.0
half = n // 2
truth = np.r_[np.zeros(half, int), np.ones(half, int)]
thr = 2 * np.sqrt(c)


def overlap(labels):
    acc = (labels == truth).mean()
    return 2 * max(acc, 1 - acc) - 1


curve = []                                            # 存下结果用于作图
for ratio in [0.5, 0.9, 1.1, 1.5, 2.0]:
    dc = ratio * thr                                  # Δc = c_in - c_out
    c_in, c_out = c + dc / 2, c - dc / 2
    res_bh, res_mod = [], []
    for seed in range(3):
        G = nx.stochastic_block_model([half, half], [[c_in / n, c_out / n], [c_out / n, c_in / n]], seed=seed)
        A = nx.to_scipy_sparse_array(G, nodelist=range(n), format="csr", dtype=float)
        k = np.asarray(A.sum(1)).ravel()
        r = np.sqrt(k.mean())
        H = (r ** 2 - 1) * sp.identity(n) - r * A + sp.diags(k)
        vals, vecs = eigsh(H, k=2, which="SA")
        v = vecs[:, np.argsort(vals)[1]]               # 第二小特征值的特征向量
        res_bh.append(overlap((v > 0).astype(int)))
        # 模块度矩阵 B = A - k k^T/2m 的主特征向量（隐式矩阵乘法，不显式构造稠密 B）
        m2 = k.sum()
        Bop = LinearOperator((n, n), matvec=lambda x: A @ x - k * (k @ x) / m2, dtype=float)
        _, u = eigsh(Bop, k=1, which="LA")
        res_mod.append(overlap((u[:, 0] > 0).astype(int)))
    print("Δc/2√c = %.1f  (c_in=%.2f, c_out=%.2f)  overlap: Bethe Hessian %.2f, 模块度谱 %.2f"
          % (ratio, c_in, c_out, np.mean(res_bh), np.mean(res_mod)))
    curve.append((ratio, np.mean(res_bh), np.mean(res_mod)))

# 作图：overlap 随 Δc/2√c 的变化，竖线为可检测性阈值
import matplotlib.pyplot as plt

rs, ob, om = zip(*curve)
fig, ax = plt.subplots(figsize=(6.4, 4.2))
ax.plot(rs, ob, "o-", label="Bethe Hessian")
ax.plot(rs, om, "s--", label="modularity matrix")
ax.axvline(1, color="0.5", ls=":", label="detectability threshold")
ax.set_xlabel("(c_in - c_out) / (2 sqrt(c))"); ax.set_ylabel("overlap (0 = chance, 1 = perfect)")
ax.set_ylim(-0.05, 1.05); ax.legend(fontsize=8)
ax.set_title("Sparse SBM (n = %d, c = %.0f): recovery starts at the threshold" % (n, c), fontsize=10)
plt.tight_layout(); plt.show()


# %% 示例：标准 SBM 与度修正 SBM（DC-SBM）在空手道网络上的最大似然划分
# Karrer 与 Newman（2011）把块模型参数用最大似然估计消去后，得到只依赖划分的目标函数：
#   标准 SBM：  L = Σ_rs m_rs log[ m_rs / (n_r n_s) ]
#   DC-SBM：    L = Σ_rs m_rs log[ m_rs / (κ_r κ_s) ]
# m_rs 为组 r、s 之间的边数（r=s 时计两次），n_r 为组内节点数，κ_r 为组内度之和。
# 用“随机初始化 + 逐点移动的贪心爬山”在 K=2 下各做 200 次重启，取似然最大的划分，与真实两派比较。
# 输出：DC-SBM 的最优划分与真实两派基本一致；标准 SBM 的最优划分倾向于把高度节点与低度节点分开。
import networkx as nx
import numpy as np

K = nx.karate_club_graph()
G = nx.Graph(K.edges())
n = G.number_of_nodes()
A = nx.to_numpy_array(G, nodelist=range(n))
deg = A.sum(1)
truth = np.array([0 if K.nodes[i]["club"] == "Mr. Hi" else 1 for i in range(n)])


def xlogy(x, y):
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(x > 0, x * np.log(x / y), 0.0)


def loglik(z, kind, K=2):
    Z = np.eye(K)[z]
    M = Z.T @ A @ Z                                # m_rs，对角线为组内边数的 2 倍
    size = Z.T @ (deg if kind == "dc" else np.ones(n))
    return xlogy(M, np.outer(size, size)).sum()


def fit(kind, restarts=200, K=2, seed=0):
    rng = np.random.default_rng(seed)
    best_L, best_z = -np.inf, None
    for _ in range(restarts):
        z = rng.integers(0, K, n)
        L = loglik(z, kind, K)
        improved = True
        while improved:
            improved = False
            for i in rng.permutation(n):
                old = z[i]
                for r in range(K):
                    if r == old:
                        continue
                    z[i] = r
                    L_new = loglik(z, kind, K)
                    if L_new > L + 1e-10:
                        L, old, improved = L_new, r, True
                z[i] = old
        if L > best_L:
            best_L, best_z = L, z.copy()
    return best_L, best_z


fits = {}                                       # 存下结果用于作图
for kind, name in [("sbm", "标准 SBM"), ("dc", "DC-SBM")]:
    L, z = fit(kind)
    fits[kind] = z
    agree = max((z == truth).mean(), (z != truth).mean())
    mean_deg = [deg[z == r].mean() for r in range(2)]
    print("%s: logL = %.2f，与真实两派一致的比例 = %.2f，两组大小 %s，两组平均度 %.1f / %.1f"
          % (name, L, agree, np.bincount(z).tolist(), *mean_deg))
print("真实两派在两种模型下的 logL：SBM %.2f，DC-SBM %.2f" % (loglik(truth, "sbm"), loglik(truth, "dc")))

# 作图：两种模型的最优划分（颜色 = 推断的组，节点大小 ∝ 度，红框 = 与真实派别不一致）
import matplotlib.pyplot as plt

pos = nx.spring_layout(G, seed=4)
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
for ax, (kind, name) in zip(axes, [("sbm", "standard SBM"), ("dc", "degree-corrected SBM")]):
    z = fits[kind]
    zz = z if (z == truth).mean() >= 0.5 else 1 - z         # 对齐标签
    nx.draw_networkx_edges(G, pos, ax=ax, edge_color="0.7", alpha=0.4)
    nx.draw_networkx_nodes(G, pos, ax=ax, nodelist=range(n), node_size=20 + 8 * deg,
                           node_color=["#fdb863" if g == 0 else "#8073ac" for g in zz],
                           edgecolors=["red" if a != b else "0.4" for a, b in zip(zz, truth)])
    ax.set_title("%s: agreement with factions = %.2f" % (name, (zz == truth).mean()), fontsize=10)
    ax.axis("off")
plt.tight_layout(); plt.show()


# %% 示例：Infomap 的目标函数——两层映射方程（map equation）
# 对无向无权网络，随机游走的稳态访问概率 p_α = k_α / 2m；模块 i 的退出概率 q_i = (i 的外连边数)/2m。
# 两层映射方程（Rosvall 与 Bergstrom 2008）给出描述一步游走所需的平均码长（bit）：
#   L(M) = plogp(Σq_i) - 2 Σ plogp(q_i) - Σ_α plogp(p_α) + Σ_i plogp(q_i + Σ_{α∈i} p_α)，plogp(x)=x·log2 x。
# (a) 比较空手道网络的几种划分（单一模块、真实两派、Louvain 划分）的 L；
# (b) 在“K5 团组成的环”上比较“每个团一个模块”与“相邻两团合并”两种划分的 Q 与 L。
# 输出：(a) L 越小代表划分越能压缩游走的描述；(b) 团足够多时 Q 偏好合并（分辨率极限），
#       而映射方程在这一构造下仍偏好把每个团分开。
import networkx as nx
import numpy as np


def plogp(x):
    x = np.asarray(x, float)
    return np.where(x > 0, x * np.log2(np.where(x > 0, x, 1)), 0.0)


def map_equation(G, communities):
    m2 = 2 * G.number_of_edges()
    label = {v: i for i, c in enumerate(communities) for v in c}
    p = np.array([G.degree(v) / m2 for v in G])
    q = np.zeros(len(communities))
    pin = np.zeros(len(communities))
    for v in G:
        pin[label[v]] += G.degree(v) / m2
    for u, v in G.edges():
        if label[u] != label[v]:
            q[label[u]] += 1 / m2
            q[label[v]] += 1 / m2
    return float(plogp(q.sum()) - 2 * plogp(q).sum() - plogp(p).sum() + plogp(q + pin).sum())


K = nx.karate_club_graph()
G = nx.Graph(K.edges())
club = [{v for v in K if K.nodes[v]["club"] == "Mr. Hi"}, {v for v in K if K.nodes[v]["club"] != "Mr. Hi"}]
louv = nx.community.louvain_communities(G, seed=1)
for name, part in [("单一模块", [set(G)]), ("真实两派", club), ("Louvain(%d 个)" % len(louv), louv)]:
    print("(a) %-12s Q = %.3f   L = %.3f bit" % (name, nx.community.modularity(G, part), map_equation(G, part)))

ring = []                                           # 存下结果用于作图
for n_c in [10, 30, 60]:
    R = nx.ring_of_cliques(n_c, 5)                  # 第 j 个团为节点 5j..5j+4
    single = [set(range(5 * j, 5 * j + 5)) for j in range(n_c)]
    pairs = [single[j] | single[j + 1] for j in range(0, n_c, 2)]
    print("(b) %2d 个 K5: 每团一模块 Q=%.4f L=%.3f | 两两合并 Q=%.4f L=%.3f"
          % (n_c, nx.community.modularity(R, single), map_equation(R, single),
             nx.community.modularity(R, pairs), map_equation(R, pairs)))
    ring.append((n_c, nx.community.modularity(R, single), nx.community.modularity(R, pairs),
                 map_equation(R, single), map_equation(R, pairs)))

# 作图：团环上“每团一模块”与“两两合并”的 Q（越大越好）和 L（越小越好）
import matplotlib.pyplot as plt

r = np.array(ring)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
for ax, j, lab in [(ax1, 1, "modularity Q (higher is better)"), (ax2, 3, "map equation L, bits (lower is better)")]:
    ax.plot(r[:, 0], r[:, j], "o-", label="one module per clique")
    ax.plot(r[:, 0], r[:, j + 1], "s--", label="adjacent cliques merged")
    ax.set_xlabel("number of K5 cliques in the ring"); ax.set_ylabel(lab); ax.legend(fontsize=8)
ax1.set_title("Q prefers merging for many cliques (resolution limit)", fontsize=10)
ax2.set_title("Map equation keeps cliques separate", fontsize=10)
plt.tight_layout(); plt.show()


# %% 示例：Leiden 算法、连通性检查与常数 Potts 模型（CPM）
# (a) 在 LFR 基准网络上用 Louvain 与 Leiden（目标函数取模块度）各运行 10 个种子，
#     比较 Q 的均值与范围，并检查每个社团的诱导子图是否连通（Leiden 在理论上保证连通，Louvain 不保证）。
# (b) 在“K5 团组成的环”上比较模块度（γ=1）与 CPM（分辨率 γ=0.5）：
#     CPM 的质量函数 H = Σ_c [ e_c - γ·n_c(n_c-1)/2 ] 不含全网边数 m，不受分辨率极限影响。
# 输出：(a) 两者 Q 接近、Leiden 略高或相当，均无不连通社团（不连通是 Louvain 的最坏情形，而非常态）；
#       (b) 团数增加到 30、60 时模块度开始合并相邻团，CPM 始终给出每团一个社团。
# 注意：networkx 的 leiden_communities 默认 metric="cpm"、resolution=1，对无权网络几乎只得到孤点，用模块度时须显式指定。
import networkx as nx
import numpy as np

G = nx.LFR_benchmark_graph(1000, 2.5, 1.5, 0.4, average_degree=10, max_degree=50,
                           min_community=20, max_community=100, seed=1)
G.remove_edges_from(nx.selfloop_edges(G))
q_runs = {}                                      # 存下结果用于作图
for name, algo in [("Louvain", lambda s: nx.community.louvain_communities(G, seed=s)),
                   ("Leiden ", lambda s: nx.community.leiden_communities(G, metric="modularity", seed=s))]:
    qs, n_disc, n_c = [], 0, []
    q_runs[name.strip()] = qs
    for s in range(10):
        comms = algo(s)
        qs.append(nx.community.modularity(G, comms))
        n_c.append(len(comms))
        n_disc += sum(not nx.is_connected(G.subgraph(c)) for c in comms)
    print("(a) %s: Q = %.4f [%.4f, %.4f]，社团数 %d–%d，不连通社团总数 %d"
          % (name, np.mean(qs), min(qs), max(qs), min(n_c), max(n_c), n_disc))

ring_counts = []
for n_c in [10, 30, 60]:
    R = nx.ring_of_cliques(n_c, 5)
    mod = nx.community.louvain_communities(R, seed=0)
    cpm = nx.community.leiden_communities(R, metric="cpm", resolution=0.5, seed=0)
    print("(b) %2d 个 K5：模块度(Louvain) 得 %2d 个社团；CPM(γ=0.5, Leiden) 得 %2d 个社团" % (n_c, len(mod), len(cpm)))
    ring_counts.append((n_c, len(mod), len(cpm)))

# 作图：左为 10 个种子下 Louvain 与 Leiden 的 Q；右为团环上两种目标函数找到的社团数
import matplotlib.pyplot as plt

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
for i, (name, qs) in enumerate(q_runs.items()):
    ax1.scatter(np.full(len(qs), i) + np.linspace(-0.12, 0.12, len(qs)), qs, s=40, alpha=0.8)
    ax1.hlines(np.mean(qs), i - 0.25, i + 0.25, color="0.3")
ax1.set_xticks(range(len(q_runs))); ax1.set_xticklabels(list(q_runs)); ax1.set_xlim(-0.6, 1.6)
ax1.set_ylabel("modularity Q (10 seeds)"); ax1.set_title("LFR benchmark (N = 1000, mu = 0.4)", fontsize=10)
rc = np.array(ring_counts)
ax2.plot(rc[:, 0], rc[:, 0], ":", color="0.6", label="true number of cliques")
ax2.plot(rc[:, 0], rc[:, 1], "o-", label="modularity (Louvain)")
ax2.plot(rc[:, 0], rc[:, 2], "s--", label="CPM gamma=0.5 (Leiden)")
ax2.set_xlabel("number of K5 cliques"); ax2.set_ylabel("communities found"); ax2.legend(fontsize=8)
ax2.set_title("CPM has no resolution limit", fontsize=10)
plt.tight_layout(); plt.show()


# %% 示例：多分辨率扫描与共识聚类
# (a) 在空手道网络上扫描分辨率 γ，每个 γ 运行 Louvain 50 次，记录社团数的中位数与“划分稳定性”
#     （50 个划分两两之间 ARI 的平均值）；稳定性高的 γ 区间提示较稳健的尺度。
# (b) 共识聚类（Lancichinetti 与 Fortunato 2012）：在 γ=1 下运行 50 次，得到共识矩阵
#     D_ij = 节点 i、j 被分到同一社团的比例；删去 D_ij < τ（τ=0.5）的元素，以 D 为加权网络再运行 Louvain，
#     重复直到 D 只含 0 和 1。最终得到一个稳定的共识划分。
# 输出：(a) γ≈0.5 时划分最稳定（两个社团）；γ 增大后社团变多、近似等价的划分增多，稳定性下降；
#       (b) 共识划分的社团数与 Q，以及各节点的“归属一致度”。
import itertools
import networkx as nx
import numpy as np


def ari(x, y):
    xs, xi = np.unique(x, return_inverse=True)
    ys, yi = np.unique(y, return_inverse=True)
    T = np.zeros((len(xs), len(ys)))
    np.add.at(T, (xi, yi), 1)
    c2 = lambda v: v * (v - 1) / 2
    s_ij, s_a, s_b, n2 = c2(T).sum(), c2(T.sum(1)).sum(), c2(T.sum(0)).sum(), c2(T.sum())
    e = s_a * s_b / n2
    den = 0.5 * (s_a + s_b) - e
    return 1.0 if den == 0 else (s_ij - e) / den


def labels(comms, n):
    lab = np.empty(n, int)
    for i, c in enumerate(comms):
        lab[list(c)] = i
    return lab


K = nx.karate_club_graph()
G = nx.Graph(K.edges())
n = G.number_of_nodes()

scan = []                                      # 存下结果用于作图
for gamma in [0.3, 0.5, 0.8, 1.0, 1.5, 2.5]:
    labs = [labels(nx.community.louvain_communities(G, resolution=gamma, seed=s), n) for s in range(50)]
    stab = np.mean([ari(a, b) for a, b in itertools.combinations(labs, 2)])
    scan.append((gamma, np.median([l.max() + 1 for l in labs]), stab))
    print("(a) γ=%.1f  社团数中位数 %d  平均两两 ARI = %.3f" % (gamma, np.median([l.max() + 1 for l in labs]), stab))


def consensus_matrix(H, runs=50, seed0=0):
    D = np.zeros((n, n))
    for s in range(runs):
        lab = labels(nx.community.louvain_communities(H, weight="weight", seed=seed0 + s), n)
        D += lab[:, None] == lab[None, :]
    return D / runs


D = consensus_matrix(G)
first = D.copy()
for it in range(20):
    if np.all((D == 0) | (D == 1)):
        break
    W = np.where(D >= 0.5, D, 0.0)
    np.fill_diagonal(W, 0)
    H = nx.from_numpy_array(W)
    D = consensus_matrix(H, seed0=100 * (it + 1))
comms = [set(c) for c in nx.connected_components(nx.from_numpy_array(np.where(D == 1, 1, 0) - np.eye(n)))]
print("(b) 迭代 %d 轮后收敛：%d 个社团，Q = %.3f" % (it, len(comms), nx.community.modularity(G, comms)))
lab = labels(comms, n)
agree = np.array([first[i, lab == lab[i]].mean() for i in range(n)])
print("    第一轮共识矩阵中归属一致度最低的 5 个节点:", np.argsort(agree)[:5].tolist(),
      np.round(np.sort(agree)[:5], 2).tolist())

# 作图：左为稳定性随 γ 的变化（标注社团数中位数）；右为按共识划分排序的第一轮共识矩阵
import matplotlib.pyplot as plt

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.2))
g_, nc_, st_ = zip(*scan)
ax1.plot(g_, st_, "o-")
for x, y, c_ in zip(g_, st_, nc_):
    ax1.annotate("%d comm." % c_, (x, y), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=8)
ax1.set_xlabel("resolution gamma"); ax1.set_ylabel("mean pairwise ARI (50 runs)"); ax1.set_ylim(0, 1.1)
ax1.set_title("Partition stability across resolutions", fontsize=10)
order = np.argsort(lab, kind="stable")
im = ax2.imshow(first[np.ix_(order, order)], cmap="viridis", vmin=0, vmax=1)
fig.colorbar(im, ax=ax2, label="co-assignment frequency")
ax2.set_title("Consensus matrix (gamma = 1), %d final communities" % len(comms), fontsize=10)
ax2.set_xlabel("nodes (sorted by consensus community)")
plt.tight_layout(); plt.show()


# %% 示例：LFR 基准网络上的算法比较
# LFR 基准（Lancichinetti、Fortunato 与 Radicchi 2008）生成度分布与社团大小都服从幂律的网络，
# 混合参数 μ 为每个节点连向社团外部的边所占比例。μ 越大社团越难识别。
# 对 μ = 0.1–0.7 各生成网络，比较 Louvain、Leiden（模块度）、贪心模块度（CNM）、标签传播四种算法
# 与种植划分之间的 NMI。（NMI 采用算术平均归一化，与前面示例的定义相同。）
# 输出：μ≤0.3 时 Louvain、Leiden、标签传播的 NMI 接近 1，贪心模块度较早下降（倾向于合并小社团）；
#       标签传播在 μ 较大时可能整体塌缩为一个社团（NMI=0）；μ≥0.6 时所有算法都接近失效。
#       这里每个 μ 只生成一个网络、只用一个种子，数值会随种子波动，正式比较应多次重复取平均。
import networkx as nx
import numpy as np


def nmi(x, y):
    xs, xi = np.unique(x, return_inverse=True)
    ys, yi = np.unique(y, return_inverse=True)
    T = np.zeros((len(xs), len(ys)))
    np.add.at(T, (xi, yi), 1)
    P = T / T.sum()
    H = lambda p: -(p[p > 0] * np.log2(p[p > 0])).sum()
    hx, hy = H(P.sum(1)), H(P.sum(0))
    return 2 * (hx + hy - H(P.ravel())) / (hx + hy)


def labels(comms, nodes):
    lab = {v: i for i, c in enumerate(comms) for v in c}
    return np.array([lab[v] for v in nodes])


algos = {
    "Louvain": lambda G: nx.community.louvain_communities(G, seed=0),
    "Leiden": lambda G: nx.community.leiden_communities(G, metric="modularity", seed=0),
    "贪心模块度": lambda G: nx.community.greedy_modularity_communities(G),
    "标签传播": lambda G: nx.community.asyn_lpa_communities(G, seed=0),
}
print("μ    " + "  ".join("%8s" % a for a in algos))
table = []                                         # 存下结果用于作图
for mu in [0.1, 0.3, 0.4, 0.5, 0.6, 0.7]:
    G = nx.LFR_benchmark_graph(1000, 2.5, 1.5, mu, average_degree=20, max_degree=50,
                               min_community=20, max_community=100, seed=3)
    G.remove_edges_from(nx.selfloop_edges(G))
    nodes = list(G)
    truth_sets = {frozenset(G.nodes[v]["community"]) for v in G}
    truth = labels(truth_sets, nodes)
    row = [nmi(truth, labels(list(f(G)), nodes)) for f in algos.values()]
    print("%.1f  " % mu + "  ".join("%8.3f" % r for r in row))
    table.append([mu] + row)

# 作图：四种算法的 NMI 随混合参数 μ 的变化
import matplotlib.pyplot as plt

tb = np.array(table)
fig, ax = plt.subplots(figsize=(6.4, 4.2))
for j, (lab, mk) in enumerate(zip(["Louvain", "Leiden", "greedy modularity (CNM)", "label propagation"],
                                  ["o-", "s--", "^-.", "D:"])):
    ax.plot(tb[:, 0], tb[:, j + 1], mk, label=lab)
ax.set_xlabel("mixing parameter mu"); ax.set_ylabel("NMI with planted partition")
ax.set_ylim(-0.05, 1.05); ax.legend(fontsize=8)
ax.set_title("LFR benchmark (N = 1000): detection fails as mu grows", fontsize=10)
plt.tight_layout(); plt.show()


# %% 示例：节点在社团中的角色——模块内度 z 分数与参与系数 P
# Guimerà 与 Amaral（2005）用两个量刻画节点角色：
#   模块内度 z 分数 z_i = (κ_i - mean κ_{s_i}) / std κ_{s_i}，κ_i 为 i 连向本社团的边数；
#   参与系数 P_i = 1 - Σ_s (k_is / k_i)^2，k_is 为 i 连向社团 s 的边数。
# z ≥ 2.5 记为枢纽，再按 P 划分 7 种角色（R1–R7）。这里在空手道网络的 Louvain 划分上计算。
# 输出：管理者（33）与教练（0）的 z 最高（约 2.1–2.3），但在只有 34 个节点的网络里达不到 z ≥ 2.5 的枢纽门槛，
#       按原始阈值都被归为 R2——说明这套阈值是为大网络设计的；P 较高的节点连向多个社团，是“连接者”。
import networkx as nx
import numpy as np

K = nx.karate_club_graph()
G = nx.Graph(K.edges())
comms = nx.community.louvain_communities(G, seed=1)
lab = {v: i for i, c in enumerate(comms) for v in c}

kappa = {v: sum(lab[u] == lab[v] for u in G[v]) for v in G}
z = {}
for c in comms:
    vals = np.array([kappa[v] for v in c], float)
    sd = vals.std() if vals.std() > 0 else 1.0
    for v in c:
        z[v] = (kappa[v] - vals.mean()) / sd
P = {}
for v in G:
    k_is = np.bincount([lab[u] for u in G[v]], minlength=len(comms))
    P[v] = 1 - ((k_is / G.degree(v)) ** 2).sum()


def role(zv, pv):
    if zv < 2.5:
        return "R1 极端外围" if pv <= 0.05 else "R2 外围" if pv <= 0.62 else "R3 非枢纽连接者" if pv <= 0.80 else "R4 非枢纽无归属"
    return "R5 局部枢纽" if pv <= 0.30 else "R6 连接枢纽" if pv <= 0.75 else "R7 无归属枢纽"


print("社团数 %d" % len(comms))
for v in sorted(G, key=lambda x: -z[x])[:5]:
    print("节点 %2d  度 %2d  z = %5.2f  P = %.2f  %s" % (v, G.degree(v), z[v], P[v], role(z[v], P[v])))
print("参与系数最高的 3 个节点:", [(v, round(float(P[v]), 2)) for v in sorted(G, key=lambda x: -P[x])[:3]])

# 作图：z–P 角色平面，虚线为 Guimerà–Amaral 的角色边界
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(6.4, 4.2))
ax.scatter([P[v] for v in G], [z[v] for v in G], c=[lab[v] for v in G], cmap="Set2", s=[20 + 5 * G.degree(v) for v in G],
           edgecolors="0.3")
for v in sorted(G, key=lambda x: -z[x])[:3] + sorted(G, key=lambda x: -P[x])[:2]:
    ax.annotate(str(v), (P[v], z[v]), textcoords="offset points", xytext=(5, 3), fontsize=9)
ax.axhline(2.5, color="#d6604d", ls="--", lw=1)
for x in [0.05, 0.62, 0.80]:
    ax.axvline(x, color="0.6", ls=":", lw=1)
ax.set_xlabel("participation coefficient P"); ax.set_ylabel("within-module degree z")
ax.set_title("Node roles: no node reaches the hub threshold z = 2.5", fontsize=10)
plt.tight_layout(); plt.show()


# %% 示例：重叠社团——团渗流（CFinder）与连边聚类（link communities）
# (a) 团渗流：k=3 时，共享一条边（2 个节点）的三角形相互“相邻”，相邻三角形的并构成一个 3-团社团。
#     统计空手道网络中 3-团、4-团社团的数目、大小，以及同时属于多个社团的节点。
# (b) 连边聚类（Ahn、Bagrow 与 Lehmann 2010）：对共享一个端点 k 的两条边 (i,k)、(j,k)，
#     相似度 S = |N+(i) ∩ N+(j)| / |N+(i) ∪ N+(j)|（N+ 为包含自身的邻居集）；对边做单连接层次聚类，
#     在使“划分密度” D 最大的高度切树。每条边只属于一个社团，节点因而可属于多个社团。
# 输出：(a) k=3 时一个 25 节点的大社团覆盖了大部分网络，节点 0、31 同属两个社团；k=4 时大部分节点不属于任何社团，
#       说明 k 的选择决定了“社团”有多严格；(b) 约三分之二的节点属于 ≥2 个连边社团，0、32、33 等枢纽参与最多。
import networkx as nx
import numpy as np
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial.distance import squareform

K = nx.karate_club_graph()
G = nx.Graph(K.edges())

for k in [3, 4]:
    cs = [set(c) for c in nx.community.k_clique_communities(G, k)]
    member = {v: sum(v in c for c in cs) for v in G}
    print("(a) k=%d：%d 个社团，大小 %s；未被覆盖节点 %d 个；重叠节点 %s"
          % (k, len(cs), sorted(len(c) for c in cs), sum(x == 0 for x in member.values()),
             [v for v, x in member.items() if x > 1]))

edges = [tuple(sorted(e)) for e in G.edges()]
M = len(edges)
nb = {v: set(G[v]) | {v} for v in G}
dist = np.ones((M, M))
for a in range(M):
    for b in range(a + 1, M):
        shared = set(edges[a]) & set(edges[b])
        if len(shared) == 1:
            k_ = shared.pop()
            i = edges[a][0] if edges[a][1] == k_ else edges[a][1]
            j = edges[b][0] if edges[b][1] == k_ else edges[b][1]
            dist[a, b] = dist[b, a] = 1 - len(nb[i] & nb[j]) / len(nb[i] | nb[j])
np.fill_diagonal(dist, 0)
Z = linkage(squareform(dist, checks=False), method="single")


def partition_density(lab):
    D = 0.0
    for c in np.unique(lab):
        es = [edges[t] for t in np.where(lab == c)[0]]
        m_c, n_c = len(es), len({v for e in es for v in e})
        if n_c > 2:
            D += m_c * (m_c - (n_c - 1)) / ((n_c - 2) * (n_c - 1))
    return 2 * D / M


best = max(((partition_density(fcluster(Z, h, "distance")), h) for h in np.unique(Z[:, 2])), key=lambda x: x[0])
lab = fcluster(Z, best[1], "distance")
node_comms = {v: len({lab[t] for t, e in enumerate(edges) if v in e}) for v in G}
sizes = np.bincount(lab)[1:]
print("(b) 最大划分密度 D = %.3f（切割高度 %.3f）；含 ≥2 条边的连边社团 %d 个"
      % (best[0], best[1], (sizes >= 2).sum()))
counts = np.bincount(list(node_comms.values()))
print("    节点所属连边社团数的分布:", {i: int(c) for i, c in enumerate(counts) if c})
print("    参与社团最多的节点:", sorted(G, key=lambda v: -node_comms[v])[:4])

# 作图：边按连边社团着色，节点颜色与大小 ∝ 所属连边社团数
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(6.4, 4.4))
pos = nx.spring_layout(G, seed=4)
big = {c for c in np.unique(lab) if (lab == c).sum() >= 2}
ecol = [plt.cm.tab20(sorted(big).index(lab[t]) % 20) if lab[t] in big else (0.8, 0.8, 0.8, 1) for t in range(M)]
nx.draw_networkx_edges(G, pos, ax=ax, edgelist=edges, edge_color=ecol, width=2)
nc = nx.draw_networkx_nodes(G, pos, ax=ax, node_color=[node_comms[v] for v in G], cmap="Greys", vmin=0,
                            node_size=[30 + 20 * node_comms[v] for v in G], edgecolors="0.3")
nx.draw_networkx_labels(G, pos, ax=ax, labels={v: str(v) for v in sorted(G, key=lambda v: -node_comms[v])[:4]}, font_size=8,
                        font_color="white")
fig.colorbar(nc, ax=ax, label="number of link communities")
ax.set_title("Link communities (D = %.3f): hubs belong to many" % best[0], fontsize=10)
ax.axis("off"); plt.tight_layout(); plt.show()


# %% 示例：时变网络的多层模块度与节点灵活性
# 构造 6 个时间层、40 个节点的时变网络：前 3 层节点 0–19 与 20–39 各成一组；
# 后 3 层节点 0–7 “换队”加入第二组。按 Mucha 等（2010）的多层模块度构造超邻接模块度矩阵：
#   B = blockdiag( A_s - γ k_s k_s^T / 2m_s ) + ω·(相邻层中同一节点之间的耦合)，Q = Σ B_{ij} δ(g_i,g_j) / 2μ，
# 并用一个通用的 Louvain 式“局部移动 + 聚合”算法（适用于任意对称矩阵 B，类似 GenLouvain）最大化 Q。
# 节点灵活性 = 该节点在相邻层之间改变社团归属的次数 / (层数 - 1)。
# 输出：ω 适中时，换队的 0–7 号节点灵活性约为 1/5，其余节点为 0；
#       ω 很小时各层几乎独立划分、标签在层间可能“乱跳”；ω 很大时各层被迫取相同划分，换队被掩盖。
import networkx as nx
import numpy as np

N, T, gamma = 40, 6, 1.0
rng = np.random.default_rng(0)
layers = []
for s in range(T):
    g = np.r_[np.zeros(20, int), np.ones(20, int)]
    if s >= 3:
        g[:8] = 1
    P = np.where(g[:, None] == g[None, :], 0.4, 0.03)
    A = np.triu(rng.random((N, N)) < P, 1).astype(float)
    layers.append(A + A.T)


def supra_B(omega):
    n = N * T
    B = np.zeros((n, n))
    for s, A in enumerate(layers):
        k = A.sum(1)
        B[s * N:(s + 1) * N, s * N:(s + 1) * N] = A - gamma * np.outer(k, k) / k.sum()
    for s in range(T - 1):
        idx = np.arange(N)
        B[s * N + idx, (s + 1) * N + idx] = omega
        B[(s + 1) * N + idx, s * N + idx] = omega
    return B


def louvain_on_B(B, seed=0):
    """对任意对称矩阵 B 最大化 Σ_ij B_ij δ(g_i,g_j)：局部移动 + 聚合，直到不再变化。"""
    rng = np.random.default_rng(seed)
    n = B.shape[0]
    member = np.arange(n)                         # 原始节点 → 当前超节点
    Bc = B.copy()
    while True:
        m = Bc.shape[0]
        g = np.arange(m)
        moved_any, improved = False, True
        while improved:
            improved = False
            for i in rng.permutation(m):
                Bi = Bc[i].copy()
                Bi[i] = 0
                gain = np.bincount(g, weights=Bi, minlength=m)   # 连向各社团的 B 之和（不含自身）
                best = np.argmax(gain)
                if gain[best] > gain[g[i]] + 1e-12:
                    g[i] = best
                    improved = moved_any = True
        if not moved_any:
            break
        _, g = np.unique(g, return_inverse=True)
        Z = np.eye(g.max() + 1)[g]
        Bc = Z.T @ Bc @ Z
        member = g[member]
    return member


lab_by_omega = {}                                 # 存下结果用于作图
for omega in [0.05, 1.0, 20.0]:
    B = supra_B(omega)
    lab = louvain_on_B(B).reshape(T, N)          # lab[s, i]：节点 i 在第 s 层的社团
    two_mu = sum(A.sum() for A in layers) + 2 * omega * N * (T - 1)
    Q = B[lab.ravel()[:, None] == lab.ravel()[None, :]].sum() / two_mu
    flex = (lab[1:] != lab[:-1]).mean(0)
    print("ω=%-5g Q=%.3f  社团总数 %d  灵活性均值：换队节点 %.2f，其余节点 %.2f"
          % (omega, Q, len(np.unique(lab)), flex[:8].mean(), flex[8:].mean()))
    lab_by_omega[omega] = (lab, flex)

# 作图：每个 ω 下节点（列）× 时间层（行）的社团标签，下方小条为节点灵活性
import matplotlib.pyplot as plt

fig, axes = plt.subplots(2, 3, figsize=(12, 4), gridspec_kw={"height_ratios": [4, 1]}, sharex=True)
for j, (omega, (lab, flex)) in enumerate(lab_by_omega.items()):
    _, relab = np.unique(lab, return_inverse=True)
    axes[0, j].imshow(relab.reshape(T, N), aspect="auto", cmap="tab10", interpolation="nearest")
    axes[0, j].axvline(7.5, color="white", ls="--", lw=1)
    axes[0, j].set_title("omega = %g: %d communities" % (omega, len(np.unique(lab))), fontsize=10)
    axes[0, j].set_ylabel("layer (time)")
    axes[1, j].bar(range(N), flex, color="#d6604d", width=1)
    axes[1, j].set_ylim(0, 1); axes[1, j].set_xlabel("node (0-7 switch team)")
axes[1, 0].set_ylabel("flexibility")
plt.tight_layout(); plt.show()
