# %% [markdown]
# # 酵母蛋白质相互作用网络：重尾度分布、度异配、中心性–致死性与蓄意攻击
#
# 本案例把[生物分子网络与拓扑特征](molecular-networks.html)专题的核心问题放到真实数据上：一张由实验证据构建的酿酒酵母蛋白质相互作用（PPI）网络是否重尾、是否“无标度”？枢纽之间是否倾向于不相连？Jeong 等（2001）的“中心性–致死性”规律在今天的数据里还成立吗，它对证据阈值敏感吗？
#
# **1. 数据来源**
#
# - 相互作用：STRING v12.0（Szklarczyk 等, 2023）酿酒酵母（物种编号 4932）的完整证据通道文件，许可证 CC BY 4.0。文件 `data/yeast_string_v12_experimental.csv` 只保留**本物种直接实验证据**通道 `experiments` ≥ 400 的蛋白对（不含从其他物种转移来的证据，也不含共表达、文本挖掘等功能关联通道）。
# - 必需性：酵母基因组数据库（SGD，CC BY 4.0）的表型注释中，来自酵母全基因组缺失研究 Giaever 等（2002, *Nature*）的结果：缺失突变体 “inviable” 记为必需（1），“viable” 记为非必需（0），该研究未注释的记为缺失。文件 `data/yeast_genes_essentiality.csv`。
# - 下载日期 2026-11-20，处理步骤见 `data/SOURCES.md`。
# - 注意：STRING 的 `experiments` 通道整合了多种实验类型（如酵母双杂交、亲和纯化–质谱等），边既可能是直接二元结合，也可能是共复合物关系（见[相互作用组图谱](molecular-networks.ppi-mapping.html)）。
#
# %% [markdown]
# ## 2. 读入与清洗
#
# 检查重复边与自环，把必需性标签对上节点，并看 400/700/900 三个阈值下网络的规模。主分析用 ≥ 700（STRING 所说的“高置信度”分数段），其余两个阈值做敏感性分析。
#
# %%
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from scipy.optimize import minimize

edges = pd.read_csv("data/yeast_string_v12_experimental.csv")
genes = pd.read_csv("data/yeast_genes_essentiality.csv")
print("边表 %d 行；重复蛋白对 %d；自环 %d" % (len(edges), edges.duplicated(["orf1", "orf2"]).sum(), (edges.orf1 == edges.orf2).sum()))
ess = dict(zip(genes.orf, genes.essential))
name = dict(zip(genes.orf, genes.gene))
print("基因表 %d 个 ORF：必需 %d，非必需 %d，未注释 %d"
      % (len(genes), (genes.essential == 1).sum(), (genes.essential == 0).sum(), genes.essential.isna().sum()))


def build(th):
    e = edges[edges.experiments >= th]
    return nx.from_pandas_edgelist(e, "orf1", "orf2")


nets = {th: build(th) for th in (400, 700, 900)}
for th, H in nets.items():
    gc = max(nx.connected_components(H), key=len)
    print("experiments ≥ %d：%5d 个蛋白，%6d 条边，平均度 %.1f，最大连通分支 %d 个蛋白"
          % (th, H.number_of_nodes(), H.number_of_edges(), 2 * H.number_of_edges() / H.number_of_nodes(), len(gc)))

# %% [markdown]
# ## 3. 构网
#
# 主网络取 experiments ≥ 700 的最大连通分支。
#
# %%
G0 = nets[700]
G = G0.subgraph(max(nx.connected_components(G0), key=len)).copy()
deg = dict(G.degree())
k = np.array(list(deg.values()))
print("主网络：%d 个蛋白，%d 条边；度的中位数 %d，均值 %.1f，最大 %d" % (G.number_of_nodes(), G.number_of_edges(), np.median(k), k.mean(), k.max()))
hubs = sorted(deg, key=deg.get, reverse=True)[:10]
print("度最高的 10 个蛋白：", ", ".join("%s(%d)" % (name.get(h, h), deg[h]) for h in hubs))
lab = np.array([ess.get(v, np.nan) for v in G])
print("主网络中有必需性注释的蛋白 %d 个，其中必需 %.1f%%" % (np.sum(~np.isnan(lab)), 100 * np.nanmean(lab)))

# %% [markdown]
# ## 4. 核心指标
#
# ### 4.1 度分布：重尾，但是“幂律”吗？
#
# 画互补累积分布（CCDF）。对 $k\ge k_{\min}$ 的尾部用离散幂律的近似最大似然估计指数 $\hat\alpha=1+n\big/\sum\ln\!\big(k_i/(k_{\min}-\tfrac12)\big)$，并按 Clauset 等的做法选使 KS 距离最小的 $k_{\min}$（推导见[数学推导与算法](molecular-networks.derivations.html)）。再用同一尾部数据拟合离散化的对数正态分布，比较两者的对数似然。
#
# %%
def fit_powerlaw(k, kmin):
    t = k[k >= kmin]
    a = 1 + len(t) / np.sum(np.log(t / (kmin - 0.5)))
    ks_ = np.arange(kmin, t.max() + 1)
    emp = np.array([(t >= x).mean() for x in ks_])
    mod = (ks_ / kmin) ** (1 - a)
    return a, np.max(np.abs(emp - mod)), len(t)


cands = [m for m in range(2, 60) if (k >= m).sum() >= 100]
fits = [(m,) + fit_powerlaw(k, m) for m in cands]
kmin, alpha, D, n_tail = min(fits, key=lambda r: r[2])
print("最佳 k_min = %d：尾部 %d 个蛋白，α = %.2f，KS 距离 %.3f" % (kmin, n_tail, alpha, D))

tail = k[k >= kmin].astype(float)
support = np.arange(kmin, 5000)
from scipy.special import zeta
from scipy.stats import norm
ll_pl = -alpha * np.log(tail).sum() - len(tail) * np.log(zeta(alpha, kmin))


def ll_lognorm(par):
    mu, s = par[0], abs(par[1]) + 1e-6
    cdf = norm.cdf((np.log(support + 0.5) - mu) / s) - norm.cdf((np.log(support - 0.5) - mu) / s)
    pmf = cdf / cdf.sum()
    return -np.sum(np.log(pmf[(tail - kmin).astype(int)] + 1e-300))


res = minimize(ll_lognorm, [np.log(tail).mean(), np.log(tail).std()], method="Nelder-Mead")
ll_ln = -res.fun
print("尾部对数似然：幂律 %.1f，对数正态 %.1f，差（对数正态 − 幂律）%.1f" % (ll_pl, ll_ln, ll_ln - ll_pl))

# %% [markdown]
# ### 4.2 聚集、路径与度相关
#
# 平均聚集系数、平均最短路径长度（从 300 个随机起点做广度优先搜索估计）和度同配系数 $r$。
#
# %%
C = nx.average_clustering(G)
rng = np.random.default_rng(3)
nodes = list(G)
src = rng.choice(len(nodes), 300, replace=False)
Ls = []
for s in src:
    dist = nx.single_source_shortest_path_length(G, nodes[s])
    Ls.extend(v for v in dist.values() if v > 0)
L = np.mean(Ls)
r = nx.degree_assortativity_coefficient(G)
print("C = %.3f，L ≈ %.2f，度同配系数 r = %.3f" % (C, L, r))

# %% [markdown]
# ### 4.3 中心性–致死性
#
# 仿照 Jeong 等（2001）按度分组统计必需比例，再做逻辑回归：必需 ~ $\log k$。
#
# %%
df = pd.DataFrame({"orf": nodes, "k": [deg[v] for v in nodes], "ess": [ess.get(v, np.nan) for v in nodes]}).dropna()
bins = [(1, 5), (6, 15), (16, 50), (51, 10 ** 6)]
print("度区间     蛋白数  占比    必需比例")
for lo, hi in bins:
    m = (df.k >= lo) & (df.k <= hi)
    print("%4d–%-6s %5d  %5.1f%%   %5.1f%%" % (lo, "∞" if hi > 10 ** 5 else hi, m.sum(), 100 * m.mean(), 100 * df.ess[m].mean()))


def logit_fit(x, y):
    Xd = np.column_stack([np.ones_like(x), x])
    b = np.zeros(2)
    for _ in range(50):                       # 牛顿–拉弗森（IRLS）
        pr = 1 / (1 + np.exp(-Xd @ b))
        H = Xd.T @ (Xd * (pr * (1 - pr))[:, None])
        step = np.linalg.solve(H, Xd.T @ (y - pr))
        b += step
        if np.max(np.abs(step)) < 1e-10:
            break
    se = np.sqrt(np.diag(np.linalg.inv(H)))
    return b, se


b, se = logit_fit(np.log(df.k.to_numpy(float)), df.ess.to_numpy(float))
print("逻辑回归：log k 的系数 %.3f（SE %.3f），度每翻一倍，必需的优势比 × %.2f" % (b[1], se[1], np.exp(b[1] * np.log(2))))

# 枢纽是谁？按 STRING 首选基因名粗分：RPL*/RPS* 为胞质核糖体蛋白
df["gene"] = df.orf.map(name).fillna("")
df["ribo"] = df.gene.str.match(r"^RP[LS]\d")
big = df.k > 50
print("度 > 50 的 %d 个蛋白中，核糖体蛋白 %d 个（%.0f%%）"
      % (big.sum(), (big & df.ribo).sum(), 100 * (big & df.ribo).mean() / big.mean()))
print("  其中核糖体蛋白必需比例 %.1f%%，非核糖体蛋白 %.1f%%"
      % (100 * df.ess[big & df.ribo].mean(), 100 * df.ess[big & ~df.ribo].mean()))
paralog = df[df.ribo & df.gene.str.match(r"^RP[LS]\d+[AB]$")]
print("  名称以 A/B 结尾（成对旁系同源基因）的核糖体蛋白 %d 个，必需比例 %.1f%%" % (len(paralog), 100 * paralog.ess.mean()))

# %% [markdown]
# ## 5. 与零模型比较
#
# **(a) 度保持随机网络**（Maslov–Sneppen 边交换，5 个样本）：真实网络的聚集系数和度同配系数是否超出“只由度序列决定”的预期？
#
# **(b) 标签置换**：把必需性标签在有注释的蛋白之间随机打乱 1000 次，检验两件事——必需蛋白的平均度是否高于随机预期；必需蛋白之间的边是否多于随机预期（必需蛋白在网络中聚集）。
#
# **(c) 证据阈值敏感性**：在 400、700、900 三个阈值的网络上重复逻辑回归。
#
# %%
Cr, rr = [], []
for s in range(5):
    H = G.copy()
    nx.double_edge_swap(H, nswap=5 * H.number_of_edges(), max_tries=10 ** 7, seed=20 + s)
    Cr.append(nx.average_clustering(H))
    rr.append(nx.degree_assortativity_coefficient(H))
print("(a) 度保持随机网络：C_rand = %.3f ± %.3f（真实 %.3f）；r_rand = %.3f ± %.3f（真实 %.3f）"
      % (np.mean(Cr), np.std(Cr), C, np.mean(rr), np.std(rr), r))

ann = df.set_index("orf").ess
ann_nodes = ann.index.to_numpy()
ann_lab = ann.to_numpy().astype(int)
kk = df.set_index("orf").k.loc[ann_nodes].to_numpy()
pos = {v: i for i, v in enumerate(ann_nodes)}
eu = np.array([(pos[u], pos[v]) for u, v in G.edges() if u in pos and v in pos])


def stats(labels):
    return kk[labels == 1].mean() - kk[labels == 0].mean(), np.sum(labels[eu[:, 0]] * labels[eu[:, 1]])


obs_dk, obs_ee = stats(ann_lab)
perm = np.array([stats(rng.permutation(ann_lab)) for _ in range(1000)])
print("(b) 必需与非必需蛋白的平均度差 %.1f；置换零分布均值 %.2f，p = %.4f"
      % (obs_dk, perm[:, 0].mean(), (np.sum(perm[:, 0] >= obs_dk) + 1) / 1001))
print("    必需–必需边 %d 条；置换期望 %.0f ± %.0f，富集倍数 %.2f，p = %.4f"
      % (obs_ee, perm[:, 1].mean(), perm[:, 1].std(), obs_ee / perm[:, 1].mean(), (np.sum(perm[:, 1] >= obs_ee) + 1) / 1001))

print("(c) 阈值敏感性：")
for th, H in nets.items():
    d_ = pd.DataFrame({"k": [H.degree(v) for v in H], "ess": [ess.get(v, np.nan) for v in H]}).dropna()
    bb, ss = logit_fit(np.log(d_.k.to_numpy(float)), d_.ess.to_numpy(float))
    print("    ≥ %d：%d 个有注释蛋白，必需比例 %.1f%%，log k 系数 %.3f（SE %.3f）"
          % (th, len(d_), 100 * d_.ess.mean(), bb[1], ss[1]))

# %% [markdown]
# ### 5.1 随机删除与蓄意攻击
#
# 按度从高到低删除节点（每次重算度的“自适应攻击”太慢，这里按初始度排序），与随机删除比较最大连通分支的相对大小。
#
# %%
def giant_curve(G, order, fracs):
    out = []
    Nn = G.number_of_nodes()
    for f in fracs:
        H = G.copy()
        H.remove_nodes_from(order[:int(f * Nn)])
        out.append(len(max(nx.connected_components(H), key=len)) / Nn if H.number_of_nodes() else 0)
    return np.array(out)


fracs = np.array([0, 0.02, 0.05, 0.1, 0.15, 0.2, 0.3])
attack = giant_curve(G, sorted(G, key=deg.get, reverse=True), fracs)
rand = giant_curve(G, list(rng.permutation(list(G))), fracs)
for f, a_, r_ in zip(fracs, attack, rand):
    print("删除 %4.0f%%：随机删除后巨分支 %.2f，攻击枢纽后 %.2f" % (100 * f, r_, a_))

# %% [markdown]
# ## 6. 作图
#
# %%
fig, ax = plt.subplots(1, 3, figsize=(15, 4))
ks = np.sort(np.unique(k))
ax[0].loglog(ks, [(k >= x).mean() for x in ks], "o", ms=3, label="data")
xx = np.arange(kmin, k.max() + 1)
ax[0].loglog(xx, (k >= kmin).mean() * (xx / kmin) ** (1 - alpha), "r-", label="power law, alpha=%.2f" % alpha)
ax[0].set_xlabel("degree k")
ax[0].set_ylabel("P(K >= k)")
ax[0].legend()
ax[0].set_title("Degree CCDF (experiments >= 700)")
lbl = ["1-5", "6-15", "16-50", ">50"]
fr = [df.ess[(df.k >= lo) & (df.k <= hi)].mean() for lo, hi in bins]
ax[1].bar(lbl, fr, color="gray")
ax[1].axhline(df.ess.mean(), color="k", ls="--")
ax[1].set_xlabel("degree bin")
ax[1].set_ylabel("fraction essential")
ax[1].set_title("Centrality-lethality")
ax[2].plot(fracs, rand, "o-", label="random removal")
ax[2].plot(fracs, attack, "s-", label="hub attack")
ax[2].set_xlabel("fraction removed")
ax[2].set_ylabel("giant component / N")
ax[2].legend()
ax[2].set_title("Robustness")
plt.tight_layout()

# %% [markdown]
# ## 7. 解读与局限
#
# **结果**
#
# 1. **重尾、有枢纽，但“严格幂律”证据不足。** 度从 1 到两百多，中位数只有 6。尾部可以拟合出一个幂律指数，但离散对数正态分布对同一尾部的对数似然明显更高，这与 Broido & Clauset（2019）的结论一致：说“重尾、存在枢纽”是稳妥的，说“无标度”需要更强的证据。
# 2. **度最高的 10 个蛋白全是核糖体蛋白。** 共复合物证据（如亲和纯化–质谱）会把一个大复合物的成员两两连起来；核糖体由许多蛋白组成，于是在网络中形成一个巨大的稠密团，成员的度都在 200 以上。这直接造成了两个“反教科书”的结果：
#    - 聚集系数约为度保持随机网络的 3.7 倍，而度同配系数 $r\approx0.57$，**强烈同配**——与早期 Y2H 数据报告的度异配（Maslov & Sneppen, 2002）方向相反。随机网络的 $r$ 为负，说明这种同配不是度序列本身决定的，而是大复合物内部“高度节点连高度节点”的结果。专题页提醒过，度相关这类性质对数据来源非常敏感（Batada 等, 2006）。
#    - **蓄意攻击并不比随机删除破坏性大多少。** 度最高的节点挤在同一个团里，删掉它们只是拆掉了这个团，并不切断网络其余部分之间的联系。“重尾网络对攻击枢纽脆弱”的经典结论（见[网络鲁棒性](robustness.html)）依赖于枢纽分散地连接各个部分；枢纽集中在一个模块时，结论不再成立。
# 3. **中心性–致死性大体成立，但不是单调的。** 必需比例从度 1–5 组的约 16% 升到 16–50 组的约 53%，逻辑回归中 $\log k$ 的系数在三个阈值下都显著为正；但度 > 50 的一组反而下降。这一组中约四分之一是核糖体蛋白，它们的必需比例只有约 17%，而同组非核糖体蛋白约 54%；这些核糖体蛋白绝大多数由成对的旁系同源基因编码（如 RPS4A/RPS4B，必需比例约 5%），单个拷贝缺失常可由另一个拷贝补偿。网络位置之外，基因重复这类**网络以外的**因素同样决定必需性。
# 4. **必需蛋白彼此聚集**：必需–必需边约为标签置换期望的 2.4 倍。这与“必需复合物/模块”解释相容——必需蛋白集中在内部连接稠密的复合物中，成员的度天然较高（Zotenko 等, 2008）；也与 Yu 等（2008）观察到的必需蛋白聚集一致。本数据没有复合物注释，无法像专题页建议的那样在控制复合物后检验度的独立作用（练习 L12 的任务 5 用模拟数据演示了这种混杂）。
# 5. **阈值改变网络的组成。** 阈值从 400 提到 900，网络从约 4900 个蛋白缩到约 2200 个，必需比例从 22% 升到 35%：高分证据更多地落在研究充分、常为必需的蛋白上。$\log k$ 的系数随阈值变化，说明效应量本身不是一个与数据处理无关的常数。
#
# **局限**
#
# - STRING 的 `experiments` 通道混合了二元与共复合物证据；共复合物数据会人为制造大量三角形和高连接的“枢纽”（本例的核糖体），正是这一点让度与必需性在复合物层面混杂。只用二元（如 Y2H）证据重做，结论可能不同。
# - 用基因名前缀识别核糖体蛋白只是粗略做法，可靠的复合物注释应来自专门的数据库。
# - 研究偏倚：被研究得多的蛋白有更多实验记录，度被系统抬高；本案例没有文献数等协变量可供控制。
# - 必需性只来自一项实验（Giaever 等, 2002）和一种培养条件；条件特异的必需性未纳入。
# - 幂律与对数正态的比较只用了似然差，没有做 Vuong 检验或 bootstrap 拟合优度检验；$k_{\min}$ 的选择也会改变指数估计。
# - 攻击按初始度排序，没有每步重算度，会略微低估自适应攻击的破坏力。
#