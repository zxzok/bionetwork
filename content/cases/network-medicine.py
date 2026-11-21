# %% [markdown]
# # 真实数据案例：11 种疾病的遗传关联基因在人类相互作用组中的模块、分离度与药物邻近度
#
# **问题**：（1）遗传关联基因在蛋白相互作用网络中是否聚成可观测的疾病模块？（2）哪些疾病的模块彼此重叠，哪些相互分离？（3）已批准药物的靶点是否比其他药物更靠近其适应症的疾病模块？
#
# **数据来源**
#
# - 相互作用组：STRING v12.0 人类物理相互作用子网络，保留综合分数 ≥ 700 的边，86,519 条边、10,746 个蛋白（CC BY 4.0；Szklarczyk D, et al. *Nucleic Acids Res* 2023;51:D638–D646）。
# - 疾病基因：Open Targets Platform（数据版本 26.09）中 11 种疾病的遗传关联分数（genetic_association），文件保留分数 ≥ 0.5 的基因，本案例主分析取 ≥ 0.7（CC0 1.0；Buniello A, et al. *Nucleic Acids Res* 2025;53:D1467–D1475）。
# - 药物靶点：Open Targets 汇总的 ChEMBL 作用机制靶点，17 种药物；`approved_for` 列只标出这 11 种疾病中、临床阶段为“已批准”的适应症（ChEMBL 部分为 CC BY-SA 3.0；Zdrazil B, et al. *Nucleic Acids Res* 2024;52:D1180–D1192）。
#
# 方法依次对应 [疾病模块](network-medicine.disease-modules.html)、[网络分离度](network-medicine.network-separation.html) 与 [网络邻近度](network-medicine.network-proximity.html)；度匹配的随机化见 [统计要点](network-medicine.statistical-validation.html)。最短路径用 scipy 的稀疏图广度优先搜索计算，浏览器里约需一两分钟。

# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import sparse
from scipy.sparse.csgraph import connected_components, shortest_path

plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "PingFang SC", "Heiti SC", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
rng = np.random.default_rng(14)

ppi = pd.read_csv("data/string_human_physical_v12_s700.csv")
dg = pd.read_csv("data/opentargets_disease_genes_ga.csv")
drugs = pd.read_csv("data/opentargets_drug_targets.csv").fillna("")
print("相互作用：%d 条；疾病–基因关联（GA ≥ 0.5）：%d 行；药物：%d 种" % (len(ppi), len(dg), len(drugs)))

# %% [markdown]
# ## 1 读入与清洗：取最大连通分支
#
# 邻近度与分离度都基于最短路径，所以只在最大连通分支（LCC）上计算；落在 LCC 之外的疾病基因和靶点要报告丢掉了多少。

# %%
nodes = pd.Index(sorted(set(ppi.protein1) | set(ppi.protein2)))
ix = pd.Series(np.arange(len(nodes)), index=nodes)
i, j = ix[ppi.protein1].values, ix[ppi.protein2].values
Adj = sparse.coo_matrix((np.ones(len(i)), (i, j)), shape=(len(nodes),) * 2)
Adj = ((Adj + Adj.T) > 0).astype(np.int8).tocsr()
ncomp, comp = connected_components(Adj, directed=False)
big = np.bincount(comp).argmax()
keep = np.where(comp == big)[0]
G = Adj[keep][:, keep].tocsr()
names = nodes[keep]
gid = pd.Series(np.arange(len(names)), index=names)
deg = np.asarray(G.sum(1)).ravel()
N, M = G.shape[0], G.nnz // 2
print("连通分支 %d 个；最大连通分支 %d 个节点、%d 条边，平均度 %.1f" % (ncomp, N, M, deg.mean()))

GA = 0.7
diseases = dg.drop_duplicates("disease_id").set_index("disease_id")["disease"]
dsets = {}
for did, name in diseases.items():
    g = dg[(dg.disease_id == did) & (dg.ga_score >= GA)].gene
    inn = [x for x in g if x in gid.index]
    dsets[name] = np.array(sorted(gid[inn].values))
    print("%-30s GA ≥ %.1f 的基因 %3d 个，在 LCC 中 %3d 个" % (name, GA, len(g), len(inn)))

# %% [markdown]
# ## 2 构建度分箱，用于度匹配随机化
#
# 节点按度升序排列，依次装箱，每箱至少 100 个节点；随机基因集中的每个基因都从与原基因同箱的节点中抽取。高度端的箱跨越的度范围较宽。

# %%
order = np.argsort(deg, kind="stable")
bin_of = np.empty(N, dtype=int)
bins, cur = [], []
for pos, v in enumerate(order):
    cur.append(v)
    nxt_same = pos + 1 < N and deg[order[pos + 1]] == deg[v]     # 同一度数的节点放进同一个箱
    if len(cur) >= 100 and not nxt_same:
        bins.append(np.array(cur)); cur = []
if cur:                                                          # 剩下不足 100 个的并入最后一箱
    bins[-1] = np.concatenate([bins[-1], cur])
for k_, arr in enumerate(bins):
    bin_of[arr] = k_
print("度分箱 %d 个；最高箱的度范围 %d–%d" % (len(bins), deg[bins[-1]].min(), deg[bins[-1]].max()))

def degree_matched(S):
    out = np.empty(len(S), dtype=int)
    used = set()
    for t, s in enumerate(S):
        pool = bins[bin_of[s]]
        c = rng.choice(pool)
        while c in used:
            c = rng.choice(pool)
        used.add(c); out[t] = c
    return out

# %% [markdown]
# ## 3 核心指标一：疾病模块的大小（LCC）与显著性
#
# 对每种疾病，取其基因在相互作用组中诱导的子图，记最大连通分支的大小 $S_\mathrm{LCC}$。零模型一：度匹配随机基因集（1000 次）；零模型二：从全网均匀随机抽取（不考虑度）。比较两种零模型给出的 $z$ 分数。

# %%
def lcc_size(S):
    sub = G[S][:, S]
    _, c = connected_components(sub, directed=False)
    return np.bincount(c).max() if len(S) else 0

B = 1000
rows = []
for name, S in dsets.items():
    obs = lcc_size(S)
    null_d = np.array([lcc_size(degree_matched(S)) for _ in range(B)])
    null_u = np.array([lcc_size(rng.choice(N, len(S), replace=False)) for _ in range(B)])
    rows.append({"疾病": name, "基因数": len(S), "LCC": obs,
                 "度匹配均值": null_d.mean(), "z（度匹配）": (obs - null_d.mean()) / null_d.std(),
                 "p（度匹配）": (1 + (null_d >= obs).sum()) / (B + 1),
                 "均匀均值": null_u.mean(), "z（均匀）": (obs - null_u.mean()) / null_u.std()})
mod = pd.DataFrame(rows).set_index("疾病")
pd.set_option("display.width", 200)
print(mod.round(2).to_string())
alld = np.unique(np.concatenate(list(dsets.values())))
print("\n全网平均度 %.1f；疾病基因平均度 %.1f（中位数 %d，全网中位数 %d）"
      % (deg.mean(), deg[alld].mean(), np.median(deg[alld]), np.median(deg)))

# %% [markdown]
# ## 4 核心指标二：疾病之间的网络分离度 $s_{AB}$
#
# $s_{AB}=\langle d_{AB}\rangle-\tfrac12(\langle d_{AA}\rangle+\langle d_{BB}\rangle)$。先从全部疾病基因出发做一次批量广度优先搜索，得到每个疾病基因到所有节点的距离，再按定义取最小值、求平均。$s_{AB}<0$ 表示两个模块重叠或彼此穿插，$s_{AB}>0$ 表示在网络中相互分离。同时记录两种疾病共有的基因数（Jaccard 指数）作对照。

# %%
allg = np.unique(np.concatenate(list(dsets.values())))
Dm = shortest_path(G, directed=False, unweighted=True, indices=allg)     # |allg| × N
row = pd.Series(np.arange(len(allg)), index=allg)

def d_within(S):
    sub = Dm[row[S].values][:, S].copy()
    np.fill_diagonal(sub, np.inf)
    return sub.min(1).mean()

def d_between(A_, B_):
    sub = Dm[row[A_].values][:, B_]
    return (sub.min(1).sum() + sub.min(0).sum()) / (len(A_) + len(B_))

dn = list(dsets)
dAA = {d: d_within(dsets[d]) for d in dn}
sep = pd.DataFrame(0.0, index=dn, columns=dn)
jac = pd.DataFrame(0.0, index=dn, columns=dn)
for a in dn:
    for b_ in dn:
        if a != b_:
            sep.loc[a, b_] = d_between(dsets[a], dsets[b_]) - (dAA[a] + dAA[b_]) / 2
            sa, sb = set(dsets[a]), set(dsets[b_])
            jac.loc[a, b_] = len(sa & sb) / len(sa | sb)
pairs = [(a, b_, sep.loc[a, b_], jac.loc[a, b_]) for k_, a in enumerate(dn) for b_ in dn[k_ + 1:]]
pairs = pd.DataFrame(pairs, columns=["A", "B", "s_AB", "Jaccard"]).sort_values("s_AB")
print("<d_AA>：", {d: round(v, 2) for d, v in dAA.items()})
print("\n分离度最小（最重叠）的 6 对：\n", pairs.head(6).round(3).to_string(index=False))
print("\n分离度最大的 6 对：\n", pairs.tail(6).round(3).to_string(index=False))
nz = pairs[pairs.Jaccard == 0]
print("\n没有共有基因的 %d 对中，s_AB < 0 的有 %d 对" % (len(nz), (nz.s_AB < 0).sum()))

# %% [markdown]
# ## 5 核心指标三与零模型：药物靶点到疾病模块的邻近度
#
# 最近距离 $d_c(S,T)=\frac1{|T|}\sum_{t\in T}\min_{s\in S}d(s,t)$。零模型：把靶点换成同度箱的随机节点（1000 次），得到 $z$ 分数。为了在浏览器中算得动，这里**只随机化靶点、疾病基因固定**；Guney 等（2016）的做法是两者都随机化，结论可能略有差异。

# %%
min_to = {d: Dm[row[S].values].min(0) for d, S in dsets.items()}         # 每个节点到疾病模块的最近距离
did_of = {v: k for k, v in diseases.items()}
res = []
for _, r in drugs.iterrows():
    T = np.array([gid[t] for t in r.targets.split(";") if t in gid.index])
    if len(T) == 0:
        continue
    approved = set(r.approved_for.split(";")) - {""}
    for d in dn:
        m = min_to[d]
        obs = m[T].mean()
        null = np.array([m[degree_matched(T)].mean() for _ in range(B)])
        z = (obs - null.mean()) / null.std() if null.std() > 0 else np.nan
        res.append({"药物": r.drug, "靶点数": len(T), "疾病": d, "d_c": obs, "z": z,
                    "已批准": did_of[d] in approved})
prox = pd.DataFrame(res)
print("在 LCC 中有靶点的药物：%d 种；药物–疾病对：%d 个，其中已批准适应症 %d 对"
      % (prox["药物"].nunique(), len(prox), prox["已批准"].sum()))
print(prox[prox["已批准"]].round(2).sort_values("z").to_string(index=False))
print("\n已批准对 z 的中位数 %.2f；其余对 %.2f" % (prox[prox["已批准"]].z.median(), prox[~prox["已批准"]].z.median()))
print("z < -0.15 的比例：已批准 %.2f，其余 %.2f" % ((prox[prox["已批准"]].z < -0.15).mean(), (prox[~prox["已批准"]].z < -0.15).mean()))

# %% [markdown]
# 已批准对与其余对的差别是否可能来自偶然？用置换检验：保持每种药物的已批准对数不变，在该药物的 11 种疾病中随机重新指定“已批准”，重复 2000 次，看已批准对的 $z$ 中位数有多少次不高于观测值。

# %%
obs_med = prox[prox["已批准"]].z.median()
perm = []
groups = [g_ for _, g_ in prox.groupby("药物")]
for _ in range(2000):
    zs = []
    for g_ in groups:
        k_ = int(g_["已批准"].sum())
        if k_:
            zs.extend(rng.choice(g_.z.values, k_, replace=False))
    perm.append(np.median(zs))
perm = np.array(perm)
print("观测中位数 %.2f；置换中位数的均值 %.2f；单侧 p = %.4f" % (obs_med, perm.mean(), (1 + (perm <= obs_med).sum()) / (len(perm) + 1)))

# %% [markdown]
# **靶点本身就是疾病基因吗？** 检查每个已批准对中有多少靶点同时是该疾病的遗传关联基因（距离为 0）；去掉这些重叠靶点后重新计算 $z$（若一个靶点都不剩则记为缺失）。

# %%
ov = []
for _, r in prox[prox["已批准"]].iterrows():
    T = np.array([gid[t] for t in drugs.set_index("drug").loc[r["药物"], "targets"].split(";") if t in gid.index])
    Sset = set(dsets[r["疾病"]])
    T2 = np.array([t for t in T if t not in Sset])
    m = min_to[r["疾病"]]
    if len(T2):
        null = np.array([m[degree_matched(T2)].mean() for _ in range(B)])
        z2 = (m[T2].mean() - null.mean()) / null.std() if null.std() > 0 else np.nan
    else:
        z2 = np.nan
    ov.append({"药物": r["药物"], "疾病": r["疾病"], "靶点数": len(T), "与疾病基因重叠": len(T) - len(T2),
               "z": r.z, "去掉重叠后 z": z2})
ov = pd.DataFrame(ov)
print(ov.round(2).to_string(index=False))
print("\n有重叠靶点的已批准对：%d / %d；去掉重叠后可计算的 %d 对，z 中位数 %.2f"
      % ((ov["与疾病基因重叠"] > 0).sum(), len(ov), ov["去掉重叠后 z"].notna().sum(), ov["去掉重叠后 z"].median()))

# %% [markdown]
# ## 6 作图
#
# 左：两种零模型下疾病模块的 $z$ 分数；中：疾病之间的分离度矩阵；右：已批准与其他药物–疾病对的邻近度 $z$ 分数。

# %%
fig, ax = plt.subplots(1, 3, figsize=(15, 4.6), gridspec_kw={"width_ratios": [1, 1.25, 0.8]})
o = mod.sort_values("z（度匹配）").index
yy = np.arange(len(o))
ax[0].scatter(mod.loc[o, "z（均匀）"], yy, marker="o", facecolors="none", edgecolors="#c0392b", label="均匀随机基线")
ax[0].scatter(mod.loc[o, "z（度匹配）"], yy, marker="o", color="#3b6ea8", label="度匹配基线")
ax[0].axvline(1.96, color="grey", ls="--", lw=1)
ax[0].set_yticks(yy); ax[0].set_yticklabels(o, fontsize=8)
ax[0].set_xlabel("疾病模块 LCC 的 z 分数")
ax[0].set_title("两种随机基线给出的显著性不同")
ax[0].legend(fontsize=8, loc="lower right")

oo = sep.mean().sort_values().index
lim = np.abs(sep.values).max()
im = ax[1].imshow(sep.loc[oo, oo].values, cmap="RdBu", vmin=-lim, vmax=lim)
ax[1].set_xticks(range(len(oo))); ax[1].set_xticklabels(oo, rotation=60, ha="right", fontsize=7)
ax[1].set_yticks(range(len(oo))); ax[1].set_yticklabels(oo, fontsize=7)
plt.colorbar(im, ax=ax[1], fraction=0.046, label="分离度 s_AB")
ax[1].set_title("自身免疫病之间的模块彼此重叠（s_AB < 0）")

ax[2].boxplot([prox[~prox["已批准"]].z.dropna(), prox[prox["已批准"]].z.dropna()], widths=0.5)
ax[2].set_xticks([1, 2]); ax[2].set_xticklabels(["其他对", "已批准适应症"])
for k_, flag in enumerate([False, True]):
    v = prox[prox["已批准"] == flag].z.dropna()
    ax[2].scatter(np.full(len(v), k_ + 1) + rng.uniform(-0.12, 0.12, len(v)), v, s=8, alpha=0.5, color="#3b6ea8")
ax[2].axhline(0, color="grey", lw=1)
ax[2].set_ylabel("邻近度 z 分数（越负越近）")
ax[2].set_title("已批准药物的靶点更靠近疾病模块")
plt.tight_layout()

# %% [markdown]
# **敏感性：换一个遗传关联阈值。** 把 GA 阈值从 0.7 降到 0.5（基因数大约翻倍），重新计算疾病模块的度匹配 $z$ 分数（200 次随机化）。

# %%
for name in dn:
    did = did_of[name]
    g = dg[(dg.disease_id == did) & (dg.ga_score >= 0.5)].gene
    S5 = np.array(sorted(gid[[x for x in g if x in gid.index]].values))
    obs = lcc_size(S5)
    null = np.array([lcc_size(degree_matched(S5)) for _ in range(200)])
    print("%-30s GA≥0.5：%3d 个基因，LCC %3d，z = %5.2f   （GA≥0.7 时 z = %5.2f）"
          % (name, len(S5), obs, (obs - null.mean()) / null.std(), mod.loc[name, "z（度匹配）"]))

# %% [markdown]
# ## 7 解读与局限
#
# **结果说明了什么**
#
# - **疾病模块**：11 种疾病中有 9 种的遗传关联基因在相互作用组中形成大于度匹配随机期望的连通分支（$p<0.05$），但可观测模块只包含一部分疾病基因，例如阿尔茨海默病 43 个基因中 15 个连成一片。这与 Menche 等（2015）“相互作用组不完整、可观测模块偏小”的解释一致。精神分裂症与双相障碍的基因几乎不相连，GA ≥ 0.7 时模块不显著。
# - **零模型的方向**：这里均匀随机基线给出的 $z$ 反而比度匹配基线小，因为这批遗传关联基因的平均度（13.9）低于全网（17.4）。度偏倚的方向取决于基因集本身：基因集偏向枢纽时，不考虑度会夸大显著性；偏向低度节点时则会低估。所以要用度匹配基线，而不是猜测偏倚的方向。
# - **分离度**：克罗恩病与溃疡性结肠炎重叠最多（$s_{AB}=-0.66$），其次是精神分裂症与双相障碍、类风湿关节炎与系统性红斑狼疮；阿尔茨海默病、冠状动脉疾病与炎症性疾病相互分离（$s_{AB}\approx0.7$）。在这批数据中，$s_{AB}<0$ 的疾病对都有共有基因；没有共有基因的 12 对全部 $s_{AB}>0$。
# - **药物邻近度**：已批准适应症对的 $z$ 中位数约为 −1.8，低于其他药物–疾病对（约 −0.7），置换检验 $p<0.01$。但两组分布重叠很大，单个药物–疾病对的 $z$ 不足以区分“有效”与“无效”。
#
# **局限**
#
# - **循环论证**：19 个已批准对中有 6 个的靶点本身就是该疾病的遗传关联基因（如格列本脲的 *ABCC8*/*KCNJ11* 之于 2 型糖尿病，乌司奴单抗的靶点之于炎症性肠病和银屑病），这些靶点的距离为 0，把 $z$ 拉得很低。去掉重叠靶点后 $z$ 变弱，但中位数仍约为 −1.8。严格的验证应排除重叠靶点，或使用独立来源的疾病基因。
# - **参照网络的偏倚**：STRING 物理子网络综合了实验、数据库与文本挖掘证据，研究越多的蛋白连接越多。度匹配只能部分校正这种“知识偏倚”。
# - **阈值与零模型的选择**：GA 阈值从 0.7 降到 0.5 后，精神分裂症的模块变得显著，多数疾病的 $z$ 也明显变大（基因多了，LCC 更大）。STRING 分数阈值、度分箱粒度和随机化方案（只随机化靶点还是两者都随机化）同样会改变 $z$。结论应报告这些选择下的稳定性（见 [研究问题、可复现分析与敏感性分析](reproducible-research.html) 的真实数据案例）。
# - **网络接近不等于疗效**：邻近度不含作用方向（激活还是抑制）、组织表达、剂量与毒性；它产生的是需要用人群数据和试验检验的假设，见 [验证的层次](network-medicine.validation-hierarchy.html)。
