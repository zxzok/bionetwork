# %% [markdown]
# # 医院病区接触网络上的传播：流行阈值、时间顺序与重点人群干预
#
# 本案例用法国里昂一家大学医院老年科病区的可穿戴传感器接触数据，完整做一次接触网络上的传播分析：把逐 20 秒的接触记录合并成接触事件，构建以累积接触时长为边权的静态网络，计算异质平均场与淬火平均场阈值，在加权网络上用键渗流模拟 SIR，在真实时间顺序上模拟 SI 传播，并与保度随机化网络、打乱时间戳的时间网络两类零模型比较，最后比较“重点干预高接触医护人员”与“随机干预”的效果。所用定义与[度异质性与流行病阈值](spreading.epidemic-threshold.html)、[接触网络：数据与结构](spreading.contact-networks.html)、[时间网络与阵发性](spreading.temporal-networks.html)、[免疫策略](spreading.immunization.html)一致。
#
# ## 1. 数据来源
#
# - 数据集：SocioPatterns “Hospital ward dynamic contact network”，<http://www.sociopatterns.org/datasets/hospital-ward-dynamic-contact-network/>（2026-11-20 下载 `hospital_lyon_contacts.dat.gz`，解压后原样保存为 `data/hospital_lyon_contacts.tsv`，未做删减）。
# - 研究：Vanhems P, Barrat A, Cattuto C, Pinton J-F, Khanafer N, Régis C, et al.（2013）Estimating potential infection transmission routes in hospital wards using wearable proximity sensors. *PLoS ONE* 8(9): e73970，DOI [10.1371/journal.pone.0073970](https://doi.org/10.1371/journal.pone.0073970)。
# - 许可证：数据页声明按 Creative Commons 署名–非商业性使用–相同方式共享（CC BY-NC-SA 3.0）向公众发布。本课程网站是非商业的教学用途，再分发时保留署名并沿用同一许可证；使用者也须遵守这些条件。致谢 SocioPatterns 合作组（<http://www.sociopatterns.org>）。
# - 内容：2010 年 12 月 6 日（周一）13:00 至 12 月 10 日（周五）14:00，46 名医护人员与 29 名患者佩戴近距离传感器（空间分辨率约 1.5 米、时间分辨率 20 秒）。每行 `t i j Si Sj` 表示 $i$ 与 $j$ 在区间 $[t-20\,\mathrm{s},t]$ 内处于接触状态；身份 NUR 为护士与护理员，PAT 为患者，MED 为医生，ADM 为行政人员。

# %% [markdown]
# ## 2. 读入与清洗
#
# 原始文件的一行只是“某个 20 秒内两人在接触”。原文把同一对人**连续**的 20 秒记录算作一次接触（contact），所以清洗分三步：把无向对 $(i,j)$ 统一成 $i<j$；检查自环、重复行和身份是否前后一致；按对排序后，与上一条记录相隔正好 20 秒的记录并入同一次接触。合并后的接触次数可以与原文报告的 14 037 次直接核对。

# %%
import time
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

t0 = time.time()
raw = pd.read_csv("data/hospital_lyon_contacts.tsv", sep="\t", header=None, names=["t", "i", "j", "Si", "Sj"])
print("原始记录（20 秒时间片）:", len(raw), "行；t 的范围 %d–%d 秒" % (raw.t.min(), raw.t.max()))
print("自环 %d 行，完全重复 %d 行" % ((raw.i == raw.j).sum(), raw.duplicated().sum()))

# 每个人的身份必须唯一
roles = pd.concat([raw[["i", "Si"]].set_axis(["id", "role"], axis=1),
                   raw[["j", "Sj"]].set_axis(["id", "role"], axis=1)]).drop_duplicates()
assert roles.id.is_unique, "同一个人出现了两种身份"
role = dict(zip(roles.id, roles.role))
print("参与者 %d 人：" % len(role), roles.role.value_counts().to_dict())

df = raw.copy()
df["a"] = df[["i", "j"]].min(axis=1)
df["b"] = df[["i", "j"]].max(axis=1)
df = df.sort_values(["a", "b", "t"]).reset_index(drop=True)
same_pair = (df.a == df.a.shift()) & (df.b == df.b.shift())
df["new_contact"] = ~(same_pair & (df.t - df.t.shift() == 20))
contacts = df[df.new_contact].copy()
contacts["duration"] = df.groupby(df.new_contact.cumsum()).size().to_numpy() * 20
print("合并后的接触事件: %d 次（原文报告 14 037 次）" % len(contacts))
print("单次接触时长中位数 %d 秒，最长 %d 秒" % (contacts.duration.median(), contacts.duration.max()))

# 接触按身份组合分类
pair = contacts.apply(lambda r: "-".join(sorted([role[r.a], role[r.b]])), axis=1)
tab = pair.value_counts()
print("\n按身份组合统计的接触次数（占比）：")
print((tab.astype(str) + "  (" + (100 * tab / tab.sum()).round(1).astype(str) + "%)").to_string())
is_hcw = lambda x: role[x] != "PAT"
both_hcw = contacts.a.map(is_hcw) & contacts.b.map(is_hcw)
print("两名医护人员之间（NUR/MED/ADM 任意组合）: %.1f%%" % (100 * both_hcw.mean()))

# 按数据页给出的起始时刻（周一 13:00）把 t 换算为钟点，统计 7:00–20:00（原文的“白天”）的接触
hour = ((contacts.t - 20) / 3600 + 13) % 24
print("7:00–20:00 之间开始的接触: %.1f%%" % (100 * ((hour >= 7) & (hour < 20)).mean()))

# %% [markdown]
# 合并后的接触次数正好是 14 037 次，与原文一致，说明“连续 20 秒记录并为一次接触”的规则与原文相同。护士之间（NUR–NUR）的接触 5 310 次，占 38%，即原文摘要中“38%”所指的那一类；若把医生、护士、行政人员都算作医护人员，医护人员之间的接触约占 73%。按假定的时钟换算，约 94% 的接触发生在白天，与原文的 94.1% 接近（钟点换算的起点有几十秒的不确定，所以不追求逐条相同）。

# %% [markdown]
# ## 3. 构网
#
# 把 4 天的接触累积成一张无向加权网络：节点是 75 名参与者，边 $(i,j)$ 表示两人至少接触过一次，边权 $w_{ij}$ 是**累积接触时长**（秒）。专题页指出累积暴露时间越长，传播概率越高，常用 $T_{ij}=1-e^{-\beta w_{ij}}$ 把边权换成传播性。同时保留逐条记录的时间序列，用于后面的时间网络模拟。

# %%
w = df.groupby(["a", "b"]).size() * 20          # 每对人的累积接触秒数
ids = sorted(role)
idx = {p: n for n, p in enumerate(ids)}
N = len(ids)
G = nx.Graph()
G.add_nodes_from(range(N))
for (a, b), sec in w.items():
    G.add_edge(idx[a], idx[b], weight=float(sec))
roles_arr = np.array([role[p] for p in ids])
k = np.array([d for _, d in G.degree()], dtype=float)
s = np.array([d for _, d in G.degree(weight="weight")], dtype=float)
print("N = %d，L = %d 条边，密度 %.3f，连通: %s" % (N, G.number_of_edges(), nx.density(G), nx.is_connected(G)))
print("<k> = %.2f，<k^2> = %.1f，k 的范围 %d–%d" % (k.mean(), (k**2).mean(), k.min(), k.max()))
print("边权（累积秒数）中位数 %.0f，均值 %.0f，最大 %.0f" % (np.median(list(w)), w.mean(), w.max()))
print("平均聚集系数 %.3f" % nx.average_clustering(G))
for r in ["NUR", "MED", "ADM", "PAT"]:
    m = roles_arr == r
    print("  %s：%2d 人，平均度 %.1f，平均累积接触 %.1f 小时" % (r, m.sum(), k[m].mean(), s[m].mean() / 3600))

# %% [markdown]
# ## 4. 核心指标
#
# **（1）阈值。** 异质平均场（HMF）给出 SIR 阈值 $T_c=\langle k\rangle/(\langle k^2\rangle-\langle k\rangle)$，淬火平均场（QMF）给出 $\lambda_c=1/\Lambda_{\max}$（$\Lambda_{\max}$ 为邻接矩阵最大特征值）。这里的“传播强度”指每条边的传播性，所以只用无权网络。
#
# **（2）加权网络上的 SIR。** 按专题页推导 B，若感染期固定，SIR 的最终感染集合等于“每条边以概率 $T_{ij}$ 保留后，含初始感染者的连通分支”（键渗流）。取 $\beta=1/3600\ \mathrm{s}^{-1}$，即累积接触 1 小时的一对人传播概率为 $1-e^{-1}\approx0.63$；对每个种子做多次渗流，得到按种子身份分组的平均最终规模。$\beta$ 是为演示设定的，不是某种病原体的估计值。
#
# **（3）接触集中度。** 原文报告 6 名医护人员占了所有涉及患者的接触的 42%；这里按“医护–患者接触次数”排序重算这一比例。

# %%
rng = np.random.default_rng(2026)
A = nx.to_numpy_array(G, nodelist=range(N), weight=None)
lam_max = np.linalg.eigvalsh(A).max()
Tc_hmf = k.mean() / ((k**2).mean() - k.mean())
print("HMF: T_c = <k>/(<k^2>-<k>) = %.4f" % Tc_hmf)
print("QMF: 1/Lambda_max = %.4f （Lambda_max = %.2f）" % (1 / lam_max, lam_max))

beta = 1 / 3600
eu = np.array([e[:2] for e in G.edges(data=True)])
Tij = 1 - np.exp(-beta * np.array([d["weight"] for *_, d in G.edges(data=True)]))
print("传播性 T_ij：中位数 %.3f，超过 0.5 的边占 %.1f%%" % (np.median(Tij), 100 * (Tij > 0.5).mean()))

def percolation_labels(keep):
    """保留 keep 为真的边后，返回每个节点所在连通分支的编号与分支大小。"""
    H = nx.Graph(); H.add_nodes_from(range(N)); H.add_edges_from(eu[keep])
    lab = np.empty(N, int); size = {}
    for c, comp in enumerate(nx.connected_components(H)):
        lab[list(comp)] = c; size[c] = len(comp)
    return lab, size

def sir_final_sizes(Tij, runs=300, removed=()):
    """对每个种子估计平均最终感染比例（不含被移除者）；removed 中的节点不参与传播。"""
    removed = np.zeros(N, bool) if len(removed) == 0 else np.isin(np.arange(N), removed)
    ok_edge = ~(removed[eu[:, 0]] | removed[eu[:, 1]])
    out = np.zeros(N); pat_hits = np.zeros(N)
    for _ in range(runs):
        lab, size = percolation_labels((rng.random(len(Tij)) < Tij) & ok_edge)
        sz = np.array([size[c] for c in lab])
        out += sz
        pat_cnt = np.bincount(lab, weights=(roles_arr == "PAT") & ~removed, minlength=lab.max() + 1)
        pat_hits += pat_cnt[lab]
    out[removed] = np.nan; pat_hits[removed] = np.nan
    return out / runs / N, pat_hits / runs

final, pat_inf = sir_final_sizes(Tij)
print("\n平均最终规模（以全部 75 人计），按种子身份：")
for r in ["NUR", "MED", "ADM", "PAT"]:
    m = roles_arr == r
    print("  种子为 %s：%.3f（被感染的患者平均 %.1f 人）" % (r, final[m].mean(), pat_inf[m].mean()))

# 接触集中度：每名医护人员参与的医护–患者接触次数
hp = contacts[(contacts.a.map(role) == "PAT") ^ (contacts.b.map(role) == "PAT")]
hcw_of = np.where(hp.a.map(role) == "PAT", hp.b, hp.a)
cnt = pd.Series(hcw_of).value_counts()
n_pat_contacts = int(((contacts.a.map(role) == "PAT") | (contacts.b.map(role) == "PAT")).sum())
print("\n涉及患者的接触共 %d 次；接触患者最多的 6 名医护人员（%s）占其中 %.1f%%（原文 42%%）"
      % (n_pat_contacts, ", ".join(role[p] for p in cnt.index[:6]), 100 * cnt.iloc[:6].sum() / n_pat_contacts))

# %% [markdown]
# 这张网络非常稠密（75 人中平均每人与约 30 人接触过），度分布并不重尾，HMF 与 QMF 阈值几乎相同，都只有约 0.027：只看“有没有接触过”，几乎任何传播性都能越过阈值。真正区分风险的是**接触时长**：边权中位数只有 160 秒，按 $\beta=1/3600$ 换算的传播性中位数约 0.04，只有约 4% 的边传播性超过 0.5。以医生或护士为种子的平均最终规模最大，以行政人员或患者为种子时较小；患者之间几乎不直接接触（PAT–PAT 只有 97 次），病原体主要靠医护人员在患者之间“带”过去。按接触次数重算，接触患者最多的 6 名医护人员（都是护士）占涉及患者的接触的 38.5%，与原文的 42% 接近但不相同，差别可能来自计数口径（原文的具体算法未在数据页说明），这里不强求一致。

# %% [markdown]
# ## 5. 与零模型比较
#
# 两个问题需要不同的零模型：
#
# - **结构**：传播规模是不是“只由度序列和边权分布决定”？比较两种随机化：（a）**只打乱边权**：拓扑不变，把累积时长随机重新分给各条边；（b）**保度换边 + 打乱边权**：双边交换保持每个人的接触人数，再随机分配边权。
# - **时间**：真实的接触时间顺序是否改变传播？在逐条 20 秒记录上模拟离散时间 SI：每条记录中，若一方已感染，另一方以 $p=1-e^{-\beta\cdot 20\,\mathrm{s}}$ 被感染，所有种子在第一条记录的时刻引入。零模型有两种，都保留每对人的累积接触时长（因而静态加权网络完全相同）：（c）**时间戳不变、记录随机重排**：保留每个 20 秒时间片的接触总数（昼夜节律），破坏“谁在什么时候接触”；（d）**时间均匀化**：把每条记录放到 4 天内均匀随机的时刻，连昼夜节律也一并破坏。

# %%
# 5a 结构零模型
def shuffle_weights(G, seed, swap):
    H = G.copy()
    if swap:
        nx.double_edge_swap(H, nswap=10 * H.number_of_edges(), max_tries=10**6, seed=seed)
    ws = np.random.default_rng(seed).permutation([d["weight"] for *_, d in G.edges(data=True)])
    for (u, v), x in zip(H.edges(), ws):
        H[u][v]["weight"] = x
    return H

eu_real, Tij_real = eu, Tij
null_res = {}
for name, swap in [("(a) weights shuffled", False), ("(b) rewired + weights shuffled", True)]:
    C_, lam_, fin_ = [], [], []
    for sd in range(10):
        H = shuffle_weights(G, sd, swap)
        C_.append(nx.average_clustering(H))
        lam_.append(np.linalg.eigvalsh(nx.to_numpy_array(H, nodelist=range(N), weight=None)).max())
        eu = np.array([e[:2] for e in H.edges()])
        Th = 1 - np.exp(-beta * np.array([d["weight"] for *_, d in H.edges(data=True)]))
        fin_.append(sir_final_sizes(Th, runs=60)[0].mean())
    null_res[name] = (C_, lam_, fin_)
eu, Tij = eu_real, Tij_real
print("%-32s %10s %12s %14s" % ("", "clustering", "Lambda_max", "SIR final size"))
print("%-32s %10.3f %12.2f %14.3f" % ("real", nx.average_clustering(G), lam_max, final.mean()))
for name, (C_, lam_, fin_) in null_res.items():
    print("%-32s %10.3f %12.2f %8.3f ± %.3f" % (name, np.mean(C_), np.mean(lam_), np.mean(fin_), np.std(fin_)))

# 静态网络中最“重”的边在哪些身份之间
top_edges = sorted(G.edges(data="weight"), key=lambda e: -e[2])[:50]
print("累积时长最长的 50 条边的身份组合:",
      pd.Series(["-".join(sorted([roles_arr[u], roles_arr[v]])) for u, v, _ in top_edges]).value_counts().to_dict())

# 5b 时间网络上的 SI
rec = raw.sort_values("t")
ti = rec.t.to_numpy(); ii = rec.i.map(idx).to_numpy(); jj = rec.j.map(idx).to_numpy()
p = 1 - np.exp(-beta * 20)

def temporal_si(ti, ii, jj, reps=4, seed=0):
    """所有种子各重复 reps 次，同时推进；返回每次运行中每个节点的感染时刻（未感染为 inf）。"""
    r = np.random.default_rng(seed)
    seeds = np.repeat(np.arange(N), reps)
    R = len(seeds)
    tinf = np.full((R, N), np.inf)
    tinf[np.arange(R), seeds] = ti[0]
    inf = np.zeros((R, N), bool); inf[np.arange(R), seeds] = True
    for t, a, b in zip(ti, ii, jj):
        ia, ib = inf[:, a], inf[:, b]
        hit = r.random(R) < p
        new_b = ia & ~ib & hit
        new_a = ib & ~ia & hit
        if new_b.any():
            inf[new_b, b] = True; tinf[new_b, b] = t
        if new_a.any():
            inf[new_a, a] = True; tinf[new_a, a] = t
    return seeds, tinf

seeds, tinf_real = temporal_si(ti, ii, jj, seed=1)
tinf_c, tinf_d = [], []
for sd in range(3):
    order = np.random.default_rng(200 + sd).permutation(len(ti))          # (c) 时间戳不变，记录随机重排
    tinf_c.append(temporal_si(ti, ii[order], jj[order], seed=10 + sd)[1])
    tu = np.sort(np.random.default_rng(300 + sd).uniform(ti[0], ti[-1], len(ti)))
    tu[0] = ti[0]                                                          # (d) 时间均匀化
    tinf_d.append(temporal_si(tu, ii[order], jj[order], seed=20 + sd)[1])
tinf_c, tinf_d = np.vstack(tinf_c), np.vstack(tinf_d)

grid = np.linspace(ti[0], ti[-1], 300)
prev = {name: np.array([(tf <= g).mean() for g in grid])
        for name, tf in [("real order", tinf_real), ("(c) records reshuffled", tinf_c), ("(d) uniform times", tinf_d)]}
print("\n时间网络 SI（p = %.4f / 20 s）：" % p)
for name, tf in [("real order", tinf_real), ("(c) records reshuffled", tinf_c), ("(d) uniform times", tinf_d)]:
    reach = np.isfinite(tf).mean(axis=1)
    msg = []
    for frac in (0.1, 0.25):
        pv = prev[name]
        msg.append("达到 %.0f%%：%s" % (100 * frac, "%.1f 小时" % ((grid[np.argmax(pv >= frac)] - ti[0]) / 3600) if pv.max() >= frac else "未达到"))
    print("  %-24s 4 天末平均感染比例 %.3f ± %.3f（标准误）；平均患病率%s"
          % (name, reach.mean(), reach.std() / np.sqrt(len(reach)), "，".join(msg)))

# %% [markdown]
# **干预情景**：同样只干预 6 人（占医护人员的 13%），比较三种选择：按累积接触时长最高的 6 名医护人员、随机 6 名医护人员、“熟人提名”（随机选一名患者，取与其累积接触最长的医护人员，直到选满 6 人）。被干预者视为不再参与传播（相当于专题页中的“删点”），指标是以随机患者为种子时，被感染的其他患者人数。

# %%
hcw = np.where(roles_arr != "PAT")[0]
pats = np.where(roles_arr == "PAT")[0]
top6 = hcw[np.argsort(-s[hcw])[:6]]

def acquaintance(seed):
    r = np.random.default_rng(seed); chosen = []
    while len(chosen) < 6:
        pt = r.choice(pats)
        nb = [(G[pt][v]["weight"], v) for v in G[pt] if roles_arr[v] != "PAT" and v not in chosen]
        if nb:
            chosen.append(max(nb)[1])
    return np.array(chosen)

def other_patients_infected(removed, runs=150):
    _, ph = sir_final_sizes(Tij, runs=runs, removed=removed)
    return np.nanmean(ph[pats]) - 1           # 减去作为种子的那名患者

base = other_patients_infected(())
res = {"none": [base], "top-6 HCW": [other_patients_infected(top6)]}
res["random 6 HCW"] = [other_patients_infected(np.random.default_rng(300 + i).choice(hcw, 6, replace=False)) for i in range(8)]
res["acquaintance 6"] = [other_patients_infected(acquaintance(400 + i)) for i in range(8)]
print("被干预的 6 名高接触医护人员身份:", roles_arr[top6].tolist())
for key, v in res.items():
    print("  %-15s 以患者为种子时，平均另有 %.2f 名患者被感染" % (key, np.mean(v)))

# %% [markdown]
# ## 6. 作图
#
# 左上：按身份组合的接触次数矩阵；右上：度与累积接触时长的分布（按身份着色）；左下：时间网络 SI 的平均患病率曲线，真实时间顺序与两种时间零模型 (c)、(d) 对比，灰色竖带为夜间（20:00–7:00）；右下：三种干预策略下“另有多少患者被感染”。

# %%
fig, axes = plt.subplots(2, 2, figsize=(11, 8.5))
cls = ["NUR", "MED", "ADM", "PAT"]
M = np.zeros((4, 4))
for (a, b) in zip(contacts.a, contacts.b):
    x, y = cls.index(role[a]), cls.index(role[b])
    M[x, y] += 1
    if x != y:
        M[y, x] += 1
ax = axes[0, 0]
im = ax.imshow(M, cmap="viridis")
ax.set_xticks(range(4)); ax.set_xticklabels(cls); ax.set_yticks(range(4)); ax.set_yticklabels(cls)
for x in range(4):
    for y in range(4):
        ax.text(y, x, "%d" % M[x, y], ha="center", va="center", color="w" if M[x, y] < M.max() / 2 else "k", fontsize=9)
ax.set_title("Number of contacts between classes"); fig.colorbar(im, ax=ax, shrink=0.8)

ax = axes[0, 1]
for r, c in zip(cls, ["C0", "C1", "C2", "C3"]):
    m = roles_arr == r
    ax.scatter(k[m], s[m] / 3600, c=c, label=r, s=30, alpha=0.8)
ax.set_xlabel("degree k (number of distinct contacts)"); ax.set_ylabel("strength (hours of contact)")
ax.set_yscale("log"); ax.legend(); ax.set_title("Degree vs cumulative contact time")

ax = axes[1, 0]
hrs = (grid - grid[0]) / 3600
for (name, pv), ls in zip(prev.items(), ["-", "--", ":"]):
    ax.plot(hrs, pv, lw=2, ls=ls, label=name)
for d in range(5):
    lo, hi = 20 + 24 * d - 13, 31 + 24 * d - 13
    ax.axvspan(max(lo, 0), min(hi, hrs[-1]), color="0.85", zorder=0)
ax.set_xlabel("hours since Monday 13:00"); ax.set_ylabel("mean fraction infected")
ax.set_title("Temporal SI on the ward"); ax.legend()

ax = axes[1, 1]
names = list(res)
ax.bar(range(len(names)), [np.mean(res[n]) for n in names],
       yerr=[np.std(res[n]) for n in names], color=["0.6", "C3", "C0", "C2"], capsize=4)
ax.set_xticks(range(len(names))); ax.set_xticklabels(names, rotation=15)
ax.set_ylabel("other patients infected (patient seed)"); ax.set_title("Removing 6 HCWs from transmission")
plt.tight_layout()
print("运行时间 %.1f 秒" % (time.time() - t0))

# %% [markdown]
# ## 7. 解读与局限
#
# **结果。**
#
# 1. 合并规则复现了原文的 14 037 次接触和护士之间（NUR–NUR）38% 的比例，说明数据读入正确。医护人员之间的接触约占全部接触的 73%，护士是网络的核心，患者之间几乎不直接接触。
# 2. 静态网络很稠密，HMF 与 QMF 阈值都只有约 0.027。这不是“阈值为零”的无标度效应：度分布并不重尾，只是 4 天内多数医护人员碰到过大多数人。专题页提醒，重尾度分布不是接触网络的普遍性质，不能不加检验地套用无标度结论；本例的低阈值来自高密度，而决定传播风险的是接触时长的高度不均。
# 3. 结构零模型给出了最清楚的信号：**拓扑几乎不起作用，边权放在哪里才起作用**。保度换边几乎不改变聚集系数、$\Lambda_{\max}$ 和最终规模（(a) 与 (b) 只差约 0.01），而只把边权随机重分配，平均最终规模就从约 0.60 升到约 0.82。原因是真实数据中长时间接触集中在同一班组内部的固定搭档之间（最长的 50 条边中 42 条是护士–护士或医生–医生），感染者反复与已经被感染的同伴接触，这些时间对传播是“浪费”的——与专题页“团内的重复接触浪费传播机会”的说法一致。把同样多的接触时长随机撒到各条边上，会高估传播。
# 4. 在本例的参数下，时间顺序对 4 天末的感染比例影响很小：真实顺序、记录重排、时间均匀化三者相差约 0.01，在模拟误差量级。差别出现在早期：种子在周一 13:00 引入，几小时后进入夜间，真实数据（和保留昼夜节律的 (c)）中传播在夜里几乎停止，均匀化的 (d) 则更早达到 10% 的患病率。也就是说，昼夜节律主要改变**时程**，对最终规模的影响取决于观察窗口与病程长短；对更短病程或更短窗口的问题，不能用静态网络代替时间网络（专题页[时间网络与阵发性](spreading.temporal-networks.html)）。
# 5. 只干预接触时长最多的 6 名医护人员（5 名护士、1 名医生），患者之间的传播从平均另有约 11.8 人被感染降到约 6.8 人；随机干预 6 人只降到约 10.9 人；只用局部信息的“熟人提名”（问患者“谁照顾你最多”）降到约 8.6 人，介于二者之间。这与原文“少数医护人员可能成为超级传播者”的提示和专题页关于目标免疫、熟人免疫的讨论一致。
#
# **局限。**
#
# - 传感器只记录佩戴者之间约 1.5 米内的面对面接触，不包括器械、环境表面和未佩戴者（访客、其他病区人员），也无法区分接触类型（护理操作还是交谈）。
# - 只有一个病区、4 天的数据；$\beta$、固定感染期、时间网络上用 SI 而非 SIR，都是演示性假设，模拟的最终规模不代表任何真实病原体的院内感染率，结论 4 尤其依赖 $\beta$ 与观察窗口。
# - 键渗流映射假设感染期对所有人相同；若感染期因人而异，同一感染者的各条边不再独立（专题页推导 B）。
# - “干预”被简化为把人从网络中完全移除；手卫生、防护用品等实际措施只降低传播性，不会让传播概率降为零。
# - 数据许可证为 CC BY-NC-SA 3.0：可在非商业教学中再分发，但不能用于商业用途，衍生数据须沿用同一许可证。
