# %% [markdown]
# # 真实数据案例：把 STRING 的证据通道当作多重网络，并用谱嵌入做链接预测
#
# **问题**：STRING 给每对蛋白的关联打一个综合分数，但它由不同证据合成：实验、整理数据库、文献共现（文本挖掘）、共表达。把每种证据当作一层，同一组基因就构成一个 [多重网络](reporting-frontiers.multilayer-networks.html)。各层是在重复同一信息，还是各有侧重？哪一层最“偏爱”把同一疾病的基因连起来——这是生物学信号，还是文献知识的偏倚？最后，用 [拉普拉斯特征映射](reporting-frontiers.network-embedding.html) 做链接预测，并与无需训练的共同邻居基线比较；整个案例也示范 [结果图表](reporting-frontiers.figures.html) 的写法：标题写结论、总有对照、展示不确定性。
#
# **数据来源**
#
# - STRING API v12.5 网络（species = 9606，综合分数 ≥ 0.4），节点是 Open Targets Platform（数据版本 26.09）11 种疾病中遗传关联分数 ≥ 0.7 的 724 个基因；每对基因给出 experiments、database、textmining、coexpression 四个证据通道分数（STRING：CC BY 4.0，Szklarczyk D, et al. *Nucleic Acids Res* 2023;51:D638–D646）。
# - 疾病–基因对应：Open Targets Platform（CC0 1.0；Buniello A, et al. *Nucleic Acids Res* 2025;53:D1467–D1475）。

# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from scipy.sparse.csgraph import connected_components
from scipy.linalg import eigh

plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "PingFang SC", "Heiti SC", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
rng = np.random.default_rng(16)

mc = pd.read_csv("data/string_multichannel_disease_genes_v12_5.csv")
dg = pd.read_csv("data/opentargets_disease_genes_ga.csv")
dg = dg[dg.ga_score >= 0.7]
print("基因对：%d；疾病–基因关联：%d 条，涉及 %d 个基因" % (len(mc), len(dg), dg.gene.nunique()))

# %% [markdown]
# ## 1 读入与清洗
#
# 节点集合取全部 724 个疾病基因（包括在 STRING 中没有任何边的基因）。每个通道分数 ≥ 0.4 记为该层的一条边。注意 STRING 的通道分数与综合分数都经过了“去除随机期望”的校准，四个通道并不是独立测量。

# %%
genes = np.array(sorted(dg.gene.unique()))
gi = pd.Series(np.arange(len(genes)), index=genes)
mc = mc[mc.gene_a.isin(gi.index) & mc.gene_b.isin(gi.index)]
LAYERS = {"实验": "experiments", "数据库": "database", "文本挖掘": "textmining", "共表达": "coexpression"}
TH = 0.4
n = len(genes)
A = {}
for name, col in LAYERS.items():
    e = mc[mc[col] >= TH]
    M = np.zeros((n, n), dtype=np.int8)
    M[gi[e.gene_a].values, gi[e.gene_b].values] = 1
    A[name] = M | M.T
agg = np.zeros((n, n), dtype=np.int8)
for M in A.values():
    agg |= M
for name, M in list(A.items()) + [("聚合（任一层）", agg)]:
    k = M.sum(1)
    print("%-10s 边 %5d  有边的基因 %3d  平均度 %.2f" % (name, M.sum() // 2, (k > 0).sum(), k.mean()))

# %% [markdown]
# ## 2 多重网络的结构：边重叠、跨层度相关与多重参与系数
#
# - 边重叠：两层边集合的 Jaccard 指数；
# - 跨层度相关：同一基因在两层的度的斯皮尔曼相关；
# - 多重参与系数 $P_i=\frac{L}{L-1}\big[1-\sum_\alpha (k_i^{[\alpha]}/o_i)^2\big]$，接近 1 表示连接均匀分布在各层，接近 0 表示集中于一层。

# %%
names = list(A)
iu = np.triu_indices(n, 1)
E = {k: A[k][iu].astype(bool) for k in names}
jac = pd.DataFrame(np.eye(len(names)), index=names, columns=names)
dcor = jac.copy()
for a in names:
    for b in names:
        if a != b:
            jac.loc[a, b] = (E[a] & E[b]).sum() / (E[a] | E[b]).sum()
            dcor.loc[a, b] = stats.spearmanr(A[a].sum(1), A[b].sum(1))[0]
print("边重叠（Jaccard）：\n", jac.round(2).to_string())
print("\n跨层度相关（斯皮尔曼）：\n", dcor.round(2).to_string())

K = np.column_stack([A[k].sum(1) for k in names]).astype(float)
o = K.sum(1)
L_ = len(names)
P = np.full(n, np.nan)
P[o > 0] = L_ / (L_ - 1) * (1 - ((K[o > 0] / o[o > 0, None]) ** 2).sum(1))
print("\n多重参与系数：中位数 %.2f；只在一层有边（P = 0）的基因 %d 个" % (np.nanmedian(P), (P == 0).sum()))
only = {k: int(((K[:, j] > 0) & (K.sum(1) == K[:, j])).sum()) for j, k in enumerate(names)}
print("只在某一层有边的基因数：", only)

# %% [markdown]
# ## 3 核心指标：各层把“同一疾病的基因”连起来的程度，与零模型比较
#
# 同病边比例：一条边的两端基因至少共有一种疾病，就记为同病边。零模型：保持每层网络不变，打乱基因与疾病的对应（每种疾病的基因数不变，1000 次），得到同病边比例的零分布与 $z$ 分数。若某层的 $z$ 特别高，要追问：是这类证据更能捕捉疾病机制，还是这类证据本身就来自“研究同一种疾病的论文”？

# %%
dis_of = dg.groupby("gene").disease_id.apply(set)
dlist = sorted(dg.disease_id.unique())
Dmat = np.zeros((n, len(dlist)), dtype=np.int8)
for g, ds in dis_of.items():
    for d in ds:
        Dmat[gi[g], dlist.index(d)] = 1
sizes = Dmat.sum(0)

def same_frac(M, Dm):
    share = (Dm @ Dm.T) > 0
    e = M[iu].astype(bool)
    return share[iu][e].mean()

def random_labels():
    # 每种疾病随机抽同样数目的基因；基因可以属于多种疾病，与原数据一致
    R = np.zeros_like(Dmat)
    for j, s in enumerate(sizes):
        R[rng.choice(n, s, replace=False), j] = 1
    return R

nulls = [random_labels() for _ in range(1000)]
hom = []
for name, M in list(A.items()) + [("聚合", agg)]:
    obs = same_frac(M, Dmat)
    nd = np.array([same_frac(M, R) for R in nulls])
    hom.append({"层": name, "边数": int(M.sum() // 2), "同病边比例": obs, "零模型均值": nd.mean(),
                "零模型 95% 区间": (np.quantile(nd, 0.025), np.quantile(nd, 0.975)), "z": (obs - nd.mean()) / nd.std()})
hom = pd.DataFrame(hom).set_index("层")
print(hom.round(3).to_string())

# %% [markdown]
# ## 4 前沿方法：谱嵌入的链接预测，与简单基线比较
#
# 在聚合网络的最大连通分支上，随机留出 10% 的边作测试集，**先删边、再嵌入**，避免信息泄漏。嵌入用归一化拉普拉斯 $\mathcal L = I - D^{-1/2}AD^{-1/2}$ 的最小非平凡 $d=16$ 个特征向量（等价于求解 $Ly=\lambda Dy$ 后再做尺度变换），打分为嵌入向量的余弦相似度；基线为共同邻居数与 Adamic–Adar 指数。负样本从训练图中不相连的基因对里等量随机抽取。重复 5 次随机划分，报告 AUROC 的均值与范围。

# %%
_, comp = connected_components(agg, directed=False)
lcc = np.where(comp == np.bincount(comp).argmax())[0]
G0 = agg[np.ix_(lcc, lcc)].astype(float)
m = len(lcc)
print("聚合网络 LCC：%d 个基因、%d 条边" % (m, int(G0.sum() // 2)))

def auroc(pos, neg):
    return stats.mannwhitneyu(pos, neg).statistic / (len(pos) * len(neg))

def spectral_embed(Atr, d=16):
    deg = Atr.sum(1)
    dinv = np.where(deg > 0, 1 / np.sqrt(np.maximum(deg, 1e-12)), 0)
    Ln = np.eye(len(Atr)) - dinv[:, None] * Atr * dinv[None, :]
    w, V = eigh(Ln)
    Y = V[:, 1:d + 1] * dinv[:, None]          # 去掉平凡特征向量，换回 Ly = λDy 的解
    return Y / np.maximum(np.linalg.norm(Y, axis=1, keepdims=True), 1e-12)

ui, uj = np.triu_indices(m, 1)
is_edge = G0[ui, uj] > 0
eidx = np.where(is_edge)[0]
lp = []
for rep in range(5):
    test = rng.choice(eidx, len(eidx) // 10, replace=False)
    Atr = G0.copy()
    Atr[ui[test], uj[test]] = Atr[uj[test], ui[test]] = 0
    non = np.where(Atr[ui, uj] == 0)[0]
    non = np.setdiff1d(non, test)
    neg = rng.choice(non, len(test), replace=False)
    Y = spectral_embed(Atr)
    CN = Atr @ Atr
    kk = Atr.sum(1)
    AA = (Atr / np.log(np.maximum(kk, 2))[None, :]) @ Atr
    def score(S, idx):
        return S[ui[idx], uj[idx]]
    cos = Y @ Y.T
    lp.append({"划分": rep, "谱嵌入（余弦）": auroc(score(cos, test), score(cos, neg)),
               "共同邻居": auroc(score(CN, test), score(CN, neg)), "Adamic–Adar": auroc(score(AA, test), score(AA, neg))})
lp = pd.DataFrame(lp).set_index("划分")
print(lp.round(3).to_string())
print("\n均值：", lp.mean().round(3).to_dict())

# %% [markdown]
# ## 5 作图：一图一结论
#
# 左：层间边重叠（结构上的冗余程度）；中：各层同病边比例与零模型 95% 区间；右：链接预测 AUROC（点为 5 次划分，横线为均值）。每个子图的标题都写结论，而不是写“热图”“柱状图”。

# %%
fig, ax = plt.subplots(1, 3, figsize=(14, 4.2))
im = ax[0].imshow(jac.values, cmap="Blues", vmin=0, vmax=1)
ax[0].set_xticks(range(len(names))); ax[0].set_xticklabels(names)
ax[0].set_yticks(range(len(names))); ax[0].set_yticklabels(names)
for a_ in range(len(names)):
    for b_ in range(len(names)):
        ax[0].text(b_, a_, "%.2f" % jac.values[a_, b_], ha="center", va="center",
                   color="white" if jac.values[a_, b_] > 0.6 else "black", fontsize=9)
plt.colorbar(im, ax=ax[0], fraction=0.046, label="边重叠（Jaccard）")
ax[0].set_title("四种证据之间的边重叠都不高")

hh = hom.drop("聚合")
y = np.arange(len(hh))
lo = [v[0] for v in hh["零模型 95% 区间"]]
hi = [v[1] for v in hh["零模型 95% 区间"]]
ax[1].hlines(y, lo, hi, color="grey", lw=6, alpha=0.4, label="零模型 95% 区间")
ax[1].scatter(hh["同病边比例"], y, color="#3b6ea8", zorder=3, label="观测值")
ax[1].set_yticks(y); ax[1].set_yticklabels(hh.index)
ax[1].set_xlabel("两端基因共有疾病的边所占比例")
ax[1].legend(fontsize=8, loc="lower right")
ax[1].set_title("各层都富集同病边，比例在 0.36–0.49 之间")

cols = list(lp.columns)
for c_, col in enumerate(cols):
    ax[2].scatter(np.full(len(lp), c_) + rng.uniform(-0.08, 0.08, len(lp)), lp[col], color="#3b6ea8", s=18)
    ax[2].hlines(lp[col].mean(), c_ - 0.25, c_ + 0.25, color="#c0392b")
ax[2].set_xticks(range(len(cols))); ax[2].set_xticklabels(cols)
ax[2].axhline(0.5, color="grey", ls="--", lw=1)
ax[2].set_ylabel("测试边 AUROC")
ax[2].set_title("16 维谱嵌入不如共同邻居类基线")
plt.tight_layout()

# %% [markdown]
# ## 6 解读与局限
#
# **结果说明了什么**
#
# - 四种证据之间的边重叠都很低（Jaccard 不超过 0.12），跨层度相关为中等程度的正相关（实验、数据库、文本挖掘三层之间约 0.5）：同一个基因在一层里度高，在另一层里往往度也高，但具体连到谁，各层差别很大。文本挖掘层的边数是实验层的 5 倍，140 个基因只在一层有边，其中 99 个只出现在文本挖掘层。综合分数会掩盖这些差别；多重网络的表示把“边从哪种证据来”保留下来。
# - 各层的同病边比例（0.36–0.49）都远高于打乱疾病标签的零模型（约 0.21）。文本挖掘层的 $z$ 最大，但它的同病边比例与共表达层相近；$z$ 的差别主要来自边数（边越多，零分布越窄）。比较不同大小的层时，应比较效应量（比例及其区间），而不是 $z$。另外，文献共现本身就来自“研究同一种疾病的论文”，文本挖掘层把同病基因连起来，有相当一部分是知识的回声而不是独立的生物学证据；用这类网络去“发现”疾病基因之间的联系，存在循环论证的风险。
# - 链接预测中，16 维谱嵌入的 AUROC 约 0.81，低于共同邻居和 Adamic–Adar（约 0.91），而且在 5 次划分之间波动更大。这个网络有很强的局部聚集（文本挖掘层把同一篇文献里的基因连成团），共同邻居恰好擅长捕捉这种结构。报告嵌入或图神经网络方法时，必须在同一划分下给出简单基线；“AUROC 0.8”本身不说明方法有用。
#
# **局限**
#
# - 节点只是 724 个疾病基因，不是全部蛋白：层的结构受到节点选择的强烈影响，不能外推到整个相互作用组。
# - 通道阈值 0.4 是常用的“中等置信度”，换阈值会改变边数和各层的相对大小；跨层比较时更稳妥的做法是在每层取相同数目的最强边。
# - 链接预测的负样本是随机的非边，大多是“容易的负例”；测试边与训练边来自同一快照，不能代表对未来新发现关联的预测能力。按时间划分（用旧版本预测新版本新增的边）更接近实际用途。
# - 嵌入只用了一阶邻近关系；node2vec、多层嵌入或图神经网络可能表现不同，但上述评估原则不变。
