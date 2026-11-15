# 依赖：networkx>=3, numpy, scipy, matplotlib
# 数据：全部使用合成网络与模拟的“疾病基因”“药物靶点”，仅用于演示方法，不代表任何真实蛋白、疾病或药物。
#   合成“相互作用组”：1000 个节点的 BA 无标度网络（无向图，节点 = 蛋白，边 = 相互作用）；
#   疾病模块：从一个种子出发沿网络生长出的 25 个节点，其中只有 20 个“已知”（模拟疾病基因列表不完整）。
#   DIAMOnD 与网络传播两个示例另用 2000 个节点的 BA 网络，在 60 个节点间额外加边“埋入”一个模块，只公开其中 30 个；
#   药物组合示例用 1500 个节点的 BA 网络；链路预测示例用 Watts–Strogatz 网络与分块二分网络。
#   真实分析中，相互作用组可读入为边列表（nx.read_edgelist），疾病基因与药物靶点为节点 id 列表。

# %% 示例：疾病基因是否聚成模块（最大连通分支 + 度匹配随机基线）
# 计算疾病基因诱导子图的最大连通分支（LCC）大小，与 300 组“度匹配”的随机基因集比较，得到 z 分数。
# 度匹配：把节点按度从小到大装箱（每箱至少 40 个节点），随机集合中每个基因都从原基因所在的度箱中无放回抽取。
# 输出解读：疾病基因的 LCC 明显大于随机期望（z 远大于 2），支持“疾病模块”。
# 若改为从全网均匀抽取随机基因，随机集合的度偏低、更难相连，z 会被人为抬高。
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

def make_network(seed=14):
    G = nx.barabasi_albert_graph(1000, 2, seed=seed)
    rng = np.random.default_rng(seed)
    # 从一个中等度数的种子出发，每步把“与当前模块连边最多”的邻居之一加入，得到一个局部聚集的疾病模块
    start = int(rng.choice([n for n in G if 4 <= G.degree(n) <= 8]))
    module = {start}
    while len(module) < 25:
        frontier = {v for u in module for v in G[u]} - module
        score = {v: sum(1 for u in G[v] if u in module) for v in frontier}
        best = max(score.values())
        cand = sorted(v for v in frontier if score[v] == best)
        module.add(int(rng.choice(cand)))
    # 模拟“数据不完整”：随机丢掉模块中 5 个基因的身份（只知道 20 个疾病基因）
    known = sorted(rng.choice(sorted(module), size=20, replace=False).tolist())
    return G, known

def degree_bins(G, min_bin=40):
    """按度从小到大排列节点，相邻度值合并，直到每个箱至少有 min_bin 个节点。返回 节点 -> 箱内节点列表。"""
    by_deg = {}
    for n, d in G.degree():
        by_deg.setdefault(d, []).append(n)
    bins, cur = [], []
    for d in sorted(by_deg):
        cur += by_deg[d]
        if len(cur) >= min_bin:
            bins.append(cur); cur = []
    if cur:
        bins[-1] += cur
    return {n: b for b in bins for n in b}

def lcc_size(G, nodes):
    H = G.subgraph(nodes)
    return max(len(c) for c in nx.connected_components(H)) if len(H) else 0

def sample_matched(rng, nodes, node2bin):
    """为 nodes 中每个节点从其度箱中抽一个替身，整体不重复。"""
    chosen = set()
    for n in nodes:
        pool = [v for v in node2bin[n] if v not in chosen]
        chosen.add(int(rng.choice(pool)))
    return sorted(chosen)

G, disease = make_network()
node2bin = degree_bins(G)
rng = np.random.default_rng(0)

obs = lcc_size(G, disease)
rand_sizes = [lcc_size(G, sample_matched(rng, disease, node2bin)) for _ in range(300)]
mu, sd = np.mean(rand_sizes), np.std(rand_sizes)
p_emp = (1 + sum(s >= obs for s in rand_sizes)) / (len(rand_sizes) + 1)
print(f"观察 LCC = {obs}，度匹配随机期望 = {mu:.1f} ± {sd:.1f}，z = {(obs - mu) / sd:.1f}，经验 p = {p_emp:.3f}")

plt.figure(figsize=(5, 3))
plt.hist(rand_sizes, bins=range(0, max(rand_sizes + [obs]) + 2), color="gray", alpha=0.7, label="degree-matched random")
plt.axvline(obs, color="r", label="disease genes")
plt.xlabel("largest connected component size"); plt.ylabel("count"); plt.legend(); plt.tight_layout(); plt.show()

# %% 示例：药物–疾病网络邻近度（最近距离 d_c + 度匹配 z 分数）
# 定义：d_c(S, T) = 平均_{t ∈ T} min_{s ∈ S} d(s, t)，S 为疾病基因，T 为药物靶点。
# 比较两种“药物”：药物 A 的 3 个靶点紧挨疾病模块（中等度数）；药物 B 的 3 个靶点是全网度最大的枢纽。
# 对每种药物用 500 组度匹配随机靶点集合计算 z 分数（为简洁起见，这里只对靶点做度匹配抽样，
# 完整做法还应同时对疾病基因做度匹配抽样，见“数学推导与算法”中的算法 1）。
# 输出解读：药物 B 的原始距离也很短（枢纽离谁都近），但与同度数随机靶点相比 z 接近 0；
# 药物 A 的 z 明显为负，说明它“特异地”靠近疾病模块。
# 靶点只有 3 个、距离是小整数时，d_c 的零分布离散且偏斜，z 与经验 p 值可能给出不同强度的结论，
# 此时应以经验 p 值为主，并在大量药物–疾病对上做多重比较校正。
import networkx as nx
import numpy as np

def make_network(seed=14):
    G = nx.barabasi_albert_graph(1000, 2, seed=seed)
    rng = np.random.default_rng(seed)
    start = int(rng.choice([n for n in G if 4 <= G.degree(n) <= 8]))
    module = {start}
    while len(module) < 25:
        frontier = {v for u in module for v in G[u]} - module
        score = {v: sum(1 for u in G[v] if u in module) for v in frontier}
        best = max(score.values())
        cand = sorted(v for v in frontier if score[v] == best)
        module.add(int(rng.choice(cand)))
    known = sorted(rng.choice(sorted(module), size=20, replace=False).tolist())
    return G, known

def degree_bins(G, min_bin=40):
    by_deg = {}
    for n, d in G.degree():
        by_deg.setdefault(d, []).append(n)
    bins, cur = [], []
    for d in sorted(by_deg):
        cur += by_deg[d]
        if len(cur) >= min_bin:
            bins.append(cur); cur = []
    if cur:
        bins[-1] += cur
    return {n: b for b in bins for n in b}

G, disease = make_network()
node2bin = degree_bins(G)

# 一次多源 BFS 得到每个节点到最近疾病基因的距离（把所有疾病基因同时作为起点）
dist = nx.multi_source_dijkstra_path_length(G, set(disease))
N = G.number_of_nodes()
min_to_disease = np.array([dist.get(v, np.inf) for v in range(N)])

# 药物 A：3 个“不是已知疾病基因、但与疾病基因直接相邻”的中等度数节点
nbrs = sorted({v for s in disease for v in G[s]} - set(disease))
drug_A = [v for v in nbrs if 3 <= G.degree(v) <= 10][:3]
# 药物 B：全网度最大的 3 个枢纽（排除疾病基因）
drug_B = [v for v, _ in sorted(G.degree(), key=lambda x: -x[1]) if v not in disease][:3]

def closest(targets):
    return float(np.mean(min_to_disease[list(targets)]))

def null_dc(targets, n_rand=500, seed=1):
    """度匹配随机靶点集合的 d_c 零分布。"""
    r = np.random.default_rng(seed)
    return np.array([closest([int(r.choice(node2bin[t])) for t in targets]) for _ in range(n_rand)])

def proximity_z(targets, n_rand=500, seed=1):
    obs = closest(targets)
    rand = null_dc(targets, n_rand, seed)
    p = (1 + np.sum(rand <= obs)) / (n_rand + 1)
    return obs, (obs - rand.mean()) / rand.std(), p

for name, T in [("药物A（贴近模块）", drug_A), ("药物B（枢纽靶点）", drug_B)]:
    d, z, p = proximity_z(T)
    print(f"{name}：靶点度 = {[G.degree(t) for t in T]}，d_c = {d:.2f}，z = {z:.2f}，经验 p = {p:.3f}")

import matplotlib.pyplot as plt
fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
for ax, T, title in zip(axes, [drug_A, drug_B], ["drug A (targets next to module)", "drug B (hub targets)"]):
    rand = null_dc(T); d, z, _ = proximity_z(T)
    ax.hist(rand, bins=np.arange(-1 / 6, rand.max() + 0.5, 1 / 3), color="0.65", edgecolor="white",
            label="degree-matched random targets")
    ax.axvline(d, color="C3", lw=2, label=f"observed d_c = {d:.2f} (z = {z:.1f})")
    ax.set_xlabel("closest distance d_c to disease genes"); ax.set_title(title); ax.legend(fontsize=8)
axes[0].set_ylabel("count")
plt.tight_layout(); plt.show()

# %% 示例：两个疾病模块的网络分离度 s_AB
# 定义（Menche 等 2015）：s_AB = <d_AB> − (<d_AA> + <d_BB>) / 2，
# 其中 <d_AA> 是 A 中每个基因到 A 中其他基因的最短距离的平均，<d_AB> 是 A、B 间对称的“最近距离”平均
# （共有基因的距离为 0）。构造与疾病 A 部分重叠的疾病 B，以及远离 A 的疾病 C，比较 s_AB 与 s_AC。
# 输出解读：s_AB < 0（模块重叠），s_AC > 0（模块分离）。
import networkx as nx
import numpy as np

G = nx.barabasi_albert_graph(1000, 2, seed=14)
deg = dict(G.degree())
rng = np.random.default_rng(3)

def grow(G, start, size, maxdeg=15):
    """从 start（一个节点或节点列表）出发，每步加入与模块连边最多的邻居（不纳入度 > maxdeg 的枢纽）。"""
    module = set(start) if isinstance(start, list) else {start}
    while len(module) < size:
        frontier = {v for u in module for v in G[u] if deg[v] <= maxdeg} - module
        score = {v: sum(1 for u in G[v] if u in module) for v in frontier}
        best = max(score.values())
        module.add(int(rng.choice(sorted(v for v in frontier if score[v] == best))))
    return sorted(module)

def mean_within(A, sp):
    return np.mean([min(sp[a][b] for b in A if b != a) for a in A])

def mean_between(A, B, sp):
    dab = [min(sp[a][b] for b in B) for a in A]   # 若 a 也在 B 中，距离为 0
    dba = [min(sp[b][a] for a in A) for b in B]
    return np.mean(dab + dba)

seeds = [n for n in G if 4 <= deg[n] <= 8]
A = grow(G, seeds[0], 20)
B = grow(G, A[:12], 20)                                    # 以 A 的 12 个基因为起点生长，与 A 部分重叠
spA = {a: nx.single_source_shortest_path_length(G, a) for a in A}
to_A = {n: min(spA[a][n] for a in A) for n in G}           # 每个节点到 A 的最近距离
far = max(seeds, key=lambda n: to_A[n])                    # 离 A 最远的候选种子
C = grow(G, far, 20)
sp = {s: nx.single_source_shortest_path_length(G, s) for s in set(A) | set(B) | set(C)}

def separation(A, B):
    return mean_between(A, B, sp) - (mean_within(A, sp) + mean_within(B, sp)) / 2

for name, X in [("B（重叠）", B), ("C（远离）", C)]:
    print(f"A 与 {name}：共享基因 {len(set(A) & set(X))} 个，s = {separation(A, X):.2f}")

import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(6.4, 4.2))
parts = ["<d_AA>", "<d_XX>", "<d_AX>", "s_AX"]
for k, (X, lab, h) in enumerate([(B, "X = B (overlapping)", ""), (C, "X = C (distant)", "//")]):
    v = [mean_within(A, sp), mean_within(X, sp), mean_between(A, X, sp), separation(A, X)]
    ax.bar(np.arange(4) + (k - 0.5) * 0.38, v, 0.38, hatch=h, color=["C0", "C1"][k], alpha=0.85, label=lab)
ax.axhline(0, color="k", lw=0.8); ax.set_xticks(range(4)); ax.set_xticklabels(parts)
ax.set_ylabel("mean shortest distance (hops)")
ax.set_title("Network separation: s_AB < 0 (overlap), s_AC > 0 (separated)"); ax.legend()
plt.tight_layout(); plt.show()

# %% 示例：DIAMOnD 疾病模块扩展（连接显著性 + 逐步加入）
# DIAMOnD（Ghiassian 等 2015）：对每个候选节点，计算“在 N 个节点、s0 个种子的网络中，一个度为 k 的节点
# 至少有 ks 个种子邻居”的超几何尾概率 p，每步把 p 最小的节点并入种子集合，然后重新计算。
# 这里在合成网络中埋入一个 60 个节点的“真实疾病模块”，只公开其中 30 个作为已知疾病基因（种子），
# 看 DIAMOnD 前 30 个加入的节点中能找回多少个隐藏的模块成员，并与两个朴素基线比较：
# “种子邻居数 ks 最多”与“节点度最大”。输出解读：连接显著性同时考虑 ks 与 k，
# 不会像 ks 排序那样偏爱枢纽，也不会像度排序那样与模块无关。
import networkx as nx
import numpy as np
from scipy.stats import hypergeom

def planted_module_network(n=2000, m=2, size=60, seed=7):
    """BA 网络 + 在一个随机节点集合内额外加边，形成一个比背景更紧密、但不是孤立团的模块。"""
    rng = np.random.default_rng(seed)
    G = nx.barabasi_albert_graph(n, m, seed=seed)
    module = rng.choice([v for v in G if G.degree(v) <= 6], size=size, replace=False).tolist()
    for _ in range(90):                      # 模块内加 90 条边（平均每个成员多约 3 条）
        u, v = rng.choice(module, size=2, replace=False)
        G.add_edge(int(u), int(v))
    known = sorted(rng.choice(module, size=size // 2, replace=False).tolist())
    hidden = sorted(set(module) - set(known))
    return G, known, hidden

def diamond(G, seeds, n_add, alpha=1):
    """返回按加入顺序排列的 n_add 个节点。alpha>1 时把每个种子计作 alpha 份（原文的种子加权）。"""
    N = G.number_of_nodes()
    S = set(seeds)
    added = []
    for _ in range(n_add):
        s0 = len(seeds) * alpha + (len(S) - len(seeds))          # 加权后的种子数
        Nw = N + (alpha - 1) * len(seeds)
        cand = {v for u in S for v in G[u]} - S
        best, best_p = None, 2.0
        for v in sorted(cand):
            ks_orig = sum(1 for u in G[v] if u in seeds)
            ks = alpha * ks_orig + sum(1 for u in G[v] if u in S and u not in seeds)
            k = G.degree(v) + (alpha - 1) * ks_orig
            p = hypergeom.sf(ks - 1, Nw, s0, k)                    # P(X >= ks)
            if p < best_p:
                best, best_p = v, p
        S.add(best); added.append(best)
    return added

G, known, hidden = planted_module_network()
n_add = 30
d_order = diamond(G, set(known), n_add)
cand = {v for u in known for v in G[u]} - set(known)
ks_order = sorted(cand, key=lambda v: (-sum(1 for u in G[v] if u in known), v))[:n_add]
deg_order = sorted(set(G) - set(known), key=lambda v: (-G.degree(v), v))[:n_add]

H = set(hidden)
for name, order in [("DIAMOnD", d_order), ("种子邻居数 ks", ks_order), ("度", deg_order)]:
    hits = [sum(1 for v in order[:k] if v in H) for k in (10, 20, 30)]
    print(f"{name:10s} 前10/20/30 个候选中隐藏模块成员数：{hits}（共 {len(H)} 个隐藏成员）")
print("DIAMOnD 前 30 个候选的平均度：", np.mean([G.degree(v) for v in d_order]).round(1),
      "；ks 排序前 30 个的平均度：", np.mean([G.degree(v) for v in ks_order]).round(1))

import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 2, figsize=(11, 4.4))
for order, lab, st in [(d_order, "DIAMOnD", "o-"), (ks_order, "most seed neighbours ks", "s--"), (deg_order, "highest degree", "^:")]:
    ax[0].plot(range(1, n_add + 1), np.cumsum([v in H for v in order]), st, ms=3, label=lab)
ax[0].set_xlabel("number of candidates added"); ax[0].set_ylabel("hidden module members recovered")
ax[0].set_title("Recovery of the hidden module"); ax[0].legend()
nodes = set(known) | H | set(d_order)                     # 种子、隐藏成员与 DIAMOnD 候选的诱导子图
Gs = G.subgraph(nodes); pos = nx.spring_layout(Gs, seed=1, k=0.35)
groups = [(known, "C0", "seed (known disease gene)"), ([v for v in d_order if v in H], "C3", "DIAMOnD hit (hidden member)"),
          ([v for v in d_order if v not in H], "C1", "DIAMOnD candidate, not in module"),
          ([v for v in H if v not in d_order], "0.8", "hidden member, missed")]
nx.draw_networkx_edges(Gs, pos, ax=ax[1], edge_color="0.6", alpha=0.4)
for vs, c, lab in groups:
    nx.draw_networkx_nodes(Gs, pos, nodelist=vs, node_color=c, node_size=60, ax=ax[1], label=lab)
ax[1].set_title("Disease module in the network (first 30 DIAMOnD nodes)"); ax[1].axis("off")
ax[1].legend(fontsize=7, loc="lower left", frameon=False)
plt.tight_layout(); plt.show()

# %% 示例：网络传播——带重启随机游走（RWR）与热扩散的参数、度偏倚与去偏
# 用同一个埋入模块的合成网络：30 个已知疾病基因作种子，按传播分数给其余节点排序，
# 看前 30 名中有多少隐藏的模块成员（召回）。比较 RWR 的重启概率 r 与热扩散的时间 t，
# 并计算分数与节点度的 Spearman 相关：r 越小 / t 越大，传播越“全局”，分数越接近度（平稳分布）。
# 最后用 200 组度匹配随机种子把 RWR 分数转成 z 分数，演示“去度偏倚”。
# 输出解读：中等参数时召回最好；过度扩散后排名被枢纽占据；z 分数排序降低了与度的相关。
import networkx as nx
import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import expm_multiply, spsolve
from scipy.stats import spearmanr

def planted_module_network(n=2000, m=2, size=60, seed=7):
    rng = np.random.default_rng(seed)
    G = nx.barabasi_albert_graph(n, m, seed=seed)
    module = rng.choice([v for v in G if G.degree(v) <= 6], size=size, replace=False).tolist()
    for _ in range(90):
        u, v = rng.choice(module, size=2, replace=False)
        G.add_edge(int(u), int(v))
    known = sorted(rng.choice(module, size=size // 2, replace=False).tolist())
    return G, known, sorted(set(module) - set(known))

G, known, hidden = planted_module_network()
N = G.number_of_nodes()
A = nx.to_scipy_sparse_array(G, nodelist=range(N), format="csc", dtype=float)
deg = np.asarray(A.sum(axis=0)).ravel()
W = A @ sp.diags(1.0 / deg)                      # 列随机矩阵 W = A D^{-1}
I = sp.identity(N, format="csc")
L_rw = I - W                                      # 随机游走拉普拉斯（作用在概率分布上）

def p0_of(seeds):
    p = np.zeros(N); p[list(seeds)] = 1.0 / len(seeds); return p

def rwr(seeds, r):
    # 闭式解 p* = r (I - (1-r) W)^{-1} p0；稀疏线性方程组求解
    return spsolve((I - (1 - r) * W).tocsc(), r * p0_of(seeds))

def heat(seeds, t):
    # 热扩散 p(t) = exp(-t L_rw) p0，总量守恒
    return expm_multiply(-t * L_rw, p0_of(seeds))

def evaluate(score, seeds, top=30):
    rest = np.array(sorted(set(range(N)) - set(seeds)))
    order = rest[np.argsort(-score[rest], kind="stable")]
    hits = len(set(order[:top].tolist()) & set(hidden))
    rho = spearmanr(score[rest], deg[rest]).statistic
    return hits, rho

sweep = {"RWR": [], "heat": []}
print("RWR：")
for r in [0.05, 0.2, 0.5, 0.8]:
    h, rho = evaluate(rwr(known, r), known)
    print(f"  r = {r:4.2f}：前30名中隐藏成员 {h:2d} 个；分数与度的 Spearman ρ = {rho:.2f}")
    sweep["RWR"].append((f"r={r}", h, rho))
print("热扩散：")
for t in [0.5, 2, 5, 20]:
    h, rho = evaluate(heat(known, t), known)
    print(f"  t = {t:4.1f}：前30名中隐藏成员 {h:2d} 个；分数与度的 Spearman ρ = {rho:.2f}")
    sweep["heat"].append((f"t={t}", h, rho))

# 去度偏倚：r 较小时，用度匹配随机种子集构造每个节点的零分布
r = 0.05
by_deg = {}
for v in range(N):
    by_deg.setdefault(int(deg[v]), []).append(v)
bins, cur = [], []
for d in sorted(by_deg):
    cur += by_deg[d]
    if len(cur) >= 50: bins.append(cur); cur = []
if cur: bins[-1] += cur
node2bin = {v: b for b in bins for v in b}
rng = np.random.default_rng(0)
obs = rwr(known, r)
null = np.array([rwr([int(rng.choice(node2bin[s])) for s in known], r) for _ in range(200)])
z = (obs - null.mean(0)) / (null.std(0) + 1e-12)
h_raw, rho_raw = evaluate(obs, known)
h_z, rho_z = evaluate(z, known)
print(f"r = {r}：原始分数 前30命中 {h_raw}，ρ(度) = {rho_raw:.2f}；度匹配 z 分数 前30命中 {h_z}，ρ(度) = {rho_z:.2f}")

import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 2, figsize=(10, 4))
for (name, rows), st, off, ha in zip(sweep.items(), ["o-", "s--"], [(-4, 6), (5, -11)], ["right", "left"]):
    ax[0].plot([x[2] for x in rows], [x[1] for x in rows], st, label=name)
    for lab, h, rho in rows:
        ax[0].annotate(lab, (rho, h), textcoords="offset points", xytext=off, ha=ha, fontsize=7)
ax[0].plot(rho_z, h_z, "*", ms=14, color="C3", label=f"RWR r={r}, degree-matched z")
ax[0].set_xlabel("Spearman ρ(score, degree)"); ax[0].set_ylabel("hidden members in top 30"); ax[0].set_ylim(-1.5, 17)
ax[0].set_title("Over-diffusion ranks hubs, not the module"); ax[0].legend(fontsize=8)
rest = np.array(sorted(set(range(N)) - set(known))); hid = np.isin(rest, hidden)
ax[1].scatter(deg[rest], obs[rest], s=8, color="0.7", alpha=0.5, label="non-seed nodes")
ax[1].scatter(deg[rest][hid], obs[rest][hid], s=40, color="C3", label="hidden module members")
ax[1].set_xscale("log"); ax[1].set_yscale("log")
ax[1].set_xlabel("degree"); ax[1].set_ylabel(f"RWR score (r = {r})")
ax[1].set_title("Raw propagation scores track degree"); ax[1].legend(fontsize=8)
plt.tight_layout(); plt.show()

# %% 示例：药物组合的网络构型（两药分离度 + 各自与疾病模块的邻近度）
# 思路来自 Cheng、Kovács 与 Barabási（2019）：对药物对 (A, B) 与疾病 D，看三个量：
#   s_AB：两药靶点集合的网络分离度（<0 重叠，>=0 分离）；
#   z_AD、z_BD：各药靶点与疾病模块的邻近度 z 分数（度匹配随机靶点，z < 0 视为“命中”模块邻域）。
# 构造一个由两个相邻子模块组成的疾病模块，以及三种组合：
#   组合 1：两药各靶向一个子模块（互补暴露）；组合 2：两药靶向同一子模块（重叠暴露）；
#   组合 3：一药靶向疾病模块，另一药靶向远处（单一暴露）。
# 输出解读：只有组合 1 同时满足 s_AB >= 0 且两药都邻近疾病模块。阈值在这里为演示而设，真实分析需按原文校准。
import networkx as nx
import numpy as np

G = nx.barabasi_albert_graph(1500, 2, seed=21)
deg = dict(G.degree())
rng = np.random.default_rng(5)

def grow(start, size, maxdeg=12):
    mod = {start}
    while len(mod) < size:
        fr = {v for u in mod for v in G[u] if deg[v] <= maxdeg} - mod
        sc = {v: sum(1 for u in G[v] if u in mod) for v in fr}
        b = max(sc.values())
        mod.add(int(rng.choice(sorted(v for v in fr if sc[v] == b))))
    return mod

sp_all = dict(nx.all_pairs_shortest_path_length(G))
mid = [v for v in G if 3 <= deg[v] <= 8]
a0 = mid[0]
b0 = next(v for v in mid if sp_all[a0][v] == 4)          # 两个子模块的起点相距 4 步
far0 = max(mid, key=lambda v: sp_all[a0][v])               # 远处起点
sub1, sub2 = grow(a0, 15), grow(b0, 15)
disease = sorted(sub1 | sub2)

def pick(module, k=4, avoid=()):
    pool = sorted(set(module) - set(disease) - set(avoid)) or sorted(set(module) - set(avoid))
    return sorted(rng.choice(pool, size=k, replace=False).tolist())

ring1 = {v for u in sub1 for v in G[u]} | sub1               # 子模块 1 及其一步邻域
ring2 = {v for u in sub2 for v in G[u]} | sub2
far = grow(far0, 15)
drug = {"A1": pick(ring1), "B1": pick(ring2),
        "A2": pick(ring1), "B2": None, "A3": pick(ring2), "B3": pick(far)}
drug["B2"] = pick(ring1, avoid=drug["A2"])

def d_within(X):
    return np.mean([min(sp_all[x][y] for y in X if y != x) for x in X])
def d_between(X, Y):
    return np.mean([min(sp_all[x][y] for y in Y) for x in X] + [min(sp_all[y][x] for x in X) for y in Y])
def separation(X, Y):
    return d_between(X, Y) - (d_within(X) + d_within(Y)) / 2

by = {}
for v, d in deg.items(): by.setdefault(d, []).append(v)
bins, cur = [], []
for d in sorted(by):
    cur += by[d]
    if len(cur) >= 50: bins.append(cur); cur = []
if cur: bins[-1] += cur
node2bin = {v: b for b in bins for v in b}

def proximity_z(T, S, n_rand=300):
    dc = lambda T_, S_: np.mean([min(sp_all[t][s] for s in S_) for t in T_])
    obs = dc(T, S)
    rand = [dc([int(rng.choice(node2bin[t])) for t in T], [int(rng.choice(node2bin[s])) for s in S])
            for _ in range(n_rand)]
    return (obs - np.mean(rand)) / np.std(rand)

combo = []
for i, label in [(1, "组合1（拟互补暴露）"), (2, "组合2（拟重叠暴露）"), (3, "组合3（拟单一暴露）")]:
    A, B = drug[f"A{i}"], drug[f"B{i}"]
    sAB, zA, zB = separation(A, B), proximity_z(A, disease), proximity_z(B, disease)
    hitA, hitB = zA < -1, zB < -1
    if hitA and hitB:
        kind = "互补暴露" if sAB >= 0 else "重叠暴露"
    elif hitA or hitB:
        kind = "单一/间接暴露"
    else:
        kind = "非暴露/独立作用"
    print(f"{label}：s_AB = {sAB:5.2f}，z_AD = {zA:5.2f}，z_BD = {zB:5.2f} → 判为 {kind}")
    combo.append((sAB, zA, zB))

import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(6.4, 4.2))
vals = np.array(combo); x = np.arange(3)
for k, (lab, c, h) in enumerate([("s_AB (drug–drug separation)", "0.5", ""), ("z_AD", "C0", "//"), ("z_BD", "C1", "..")]):
    ax.bar(x + (k - 1) * 0.26, vals[:, k], 0.26, color=c, hatch=h, label=lab)
ax.axhline(0, color="k", lw=0.8); ax.axhline(-1, color="C3", ls="--", lw=1, label="z = -1 (proximal to disease)")
ax.set_xticks(x); ax.set_xticklabels(["combo 1\n(complementary)", "combo 2\n(overlapping)", "combo 3\n(single)"])
ax.set_ylabel("value"); ax.set_title("Complementary exposure: s_AB ≥ 0 and both z < -1"); ax.legend(fontsize=8)
plt.tight_layout(); plt.show()

# %% 示例：链路预测——共同邻居、资源分配与长度为 3 的路径（L3）
# 随机隐藏 10% 的边作为测试集，用剩余网络为“测试边”和等量“非边”打分，计算 AUROC。
# 指标：CN = |Γ(u)∩Γ(v)|；RA = Σ_{w∈Γ(u)∩Γ(v)} 1/k_w；
#       L3 = Σ_{u-a-b-v} 1/sqrt(k_a k_b)（Kovács 等 2019：蛋白通过互补界面相互作用时，
#       “我的邻居的邻居的邻居”更可能是我的伙伴，而不是“我的邻居的邻居”）。
# 两个合成网络：三角闭合强的 Watts–Strogatz（社交式），以及没有三角闭合偏好的分块二分网络（同组节点共享伙伴、彼此不相连，模拟互补界面）。
# 输出解读：在三角形多的网络中三种指标都很好；在分块二分网络中测试边两端没有共同邻居，CN/RA 的 AUROC
# 不高于 0.5（同侧非边反而可能有共同邻居），L3 明显更好。哪种启发式合适取决于网络的连接机制。
import networkx as nx
import numpy as np

def auroc(pos, neg):
    s = np.concatenate([pos, neg]); y = np.r_[np.ones(len(pos)), np.zeros(len(neg))]
    order = np.argsort(s, kind="mergesort"); ranks = np.empty(len(s)); ranks[order] = np.arange(1, len(s) + 1)
    for val in np.unique(s):                       # 并列取平均秩
        idx = s == val; ranks[idx] = ranks[idx].mean()
    n1, n0 = len(pos), len(neg)
    return (ranks[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)

def scores(G, pairs):
    k = dict(G.degree()); out = {"CN": [], "RA": [], "L3": []}
    for u, v in pairs:
        cn = set(G[u]) & set(G[v])
        out["CN"].append(len(cn))
        out["RA"].append(sum(1.0 / k[w] for w in cn))
        l3 = 0.0
        for a in G[u]:
            for b in G[a]:
                if b != u and G.has_edge(b, v) and a != v:
                    l3 += 1.0 / np.sqrt(k[a] * k[b])
        out["L3"].append(l3)
    return {m: np.array(x) for m, x in out.items()}

def experiment(G, name, seed=0):
    rng = np.random.default_rng(seed)
    edges = list(G.edges())
    test_idx = rng.choice(len(edges), size=len(edges) // 10, replace=False)
    test = [edges[i] for i in test_idx]
    Gtr = G.copy(); Gtr.remove_edges_from(test)
    nodes = list(G); neg = set()
    while len(neg) < len(test):
        u, v = rng.choice(nodes, 2, replace=False)
        if not G.has_edge(u, v): neg.add((int(u), int(v)))
    sp_, sn_ = scores(Gtr, test), scores(Gtr, list(neg))
    res = {m: auroc(sp_[m], sn_[m]) for m in ["CN", "RA", "L3"]}
    print(name + "：" + "，".join(f"{m} AUROC = {res[m]:.2f}" for m in res))
    return res

res_ws = experiment(nx.connected_watts_strogatz_graph(1000, 10, 0.1, seed=1), "Watts–Strogatz（三角闭合强）")
# 分块二分网络：左右各 500 个节点、各分 10 组，左组 i 主要连右组 i（模拟“互补界面”：同组蛋白共享伙伴但彼此不连）
rng = np.random.default_rng(2)
B = nx.Graph(); B.add_nodes_from(range(1000))
for u in range(500):
    for v in range(500, 1000):
        same = (u // 50) == ((v - 500) // 50)
        if rng.random() < (0.12 if same else 0.002):
            B.add_edge(u, v)
B = B.subgraph(max(nx.connected_components(B), key=len)).copy()
res_bp = experiment(B, "分块二分网络（无三角形）")

import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(6.4, 4.2))
x = np.arange(2)
for k, (m, c, h) in enumerate([("CN", "0.7", ""), ("RA", "0.45", "//"), ("L3", "C0", "")]):
    ax.bar(x + (k - 1) * 0.26, [res_ws[m], res_bp[m]], 0.26, color=c, hatch=h, label=m)
ax.axhline(0.5, color="k", ls="--", lw=1, label="random (0.5)")
ax.set_xticks(x); ax.set_xticklabels(["Watts–Strogatz\n(many triangles)", "block bipartite\n(complementary)"])
ax.set_ylabel("AUROC on hidden edges"); ax.set_ylim(0, 1.05)
ax.set_title("L3 works when partners share partners, not each other"); ax.legend(fontsize=8, ncol=2)
plt.tight_layout(); plt.show()
