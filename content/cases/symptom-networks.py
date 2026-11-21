# %% [markdown]
# # 美国成人 PHQ-9 抑郁症状网络：多分格相关、EBICglasso、中心性稳定性与性别比较
#
# 本案例用一个具有全国代表性抽样设计的公开调查数据，完整地估计一次截面症状网络，并按[症状网络与网络精神病学](symptom-networks.html)专题的建议检查它：输入矩阵的选择、正则化、强度与预期影响、节点可预测性、病例删除 bootstrap 的 CS 系数、置换得到的“空网络”基线，以及男女之间的网络比较检验（NCT）。
#
# **1. 数据来源**
#
# - 美国疾病控制与预防中心国家卫生统计中心（CDC/NCHS）的全国健康与营养调查 NHANES 2017–2018 周期：抑郁筛查问卷 DPQ_J 与人口学文件 DEMO_J。美国联邦政府作品，属公有领域。下载日期 2026-11-20。
# - 问卷是 PHQ-9（Kroenke 等, 2001）：过去两周内 9 种症状出现的频率，0 = 完全没有，1 = 有几天，2 = 一半以上的天数，3 = 几乎每天。NHANES 对 18 岁及以上成人施测。
# - 文件 `data/nhanes_phq9_2017_2018.csv` 只保留 9 个条目都有 0–3 有效回答的 5,068 人，以及性别和年龄（处理见 `data/SOURCES.md`）。
#
# | 列名 | 条目内容（简称） |
# |---|---|
# | PHQ1 | 做事缺乏兴趣或乐趣（兴趣减退） |
# | PHQ2 | 情绪低落、沮丧或绝望 |
# | PHQ3 | 入睡困难、睡不安稳或睡眠过多（睡眠） |
# | PHQ4 | 感觉疲倦或没有活力（疲乏） |
# | PHQ5 | 食欲不振或吃太多（食欲） |
# | PHQ6 | 觉得自己很糟、失败，或让自己或家人失望（自我评价低） |
# | PHQ7 | 注意力难以集中（注意力） |
# | PHQ8 | 动作或说话缓慢，或烦躁坐立不安（精神运动） |
# | PHQ9 | 有不如死掉或伤害自己的念头（自杀意念） |
#
# %% [markdown]
# ## 2. 读入与清洗
#
# 先看每个条目的分布。一般人群样本中多数人得 0 分，条目越“重”越偏态；自杀意念条目尤其如此。偏态会影响相关的估计，也会影响中心性（方差小的条目相关被压低）。
#
# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from scipy.stats import norm, multivariate_normal, spearmanr
from scipy.optimize import minimize_scalar

d = pd.read_csv("data/nhanes_phq9_2017_2018.csv")
items = [f"PHQ{i}" for i in range(1, 10)]
short = ["兴趣", "情绪", "睡眠", "疲乏", "食欲", "自评", "注意", "运动", "自杀"]
X = d[items].to_numpy(int)
n, p = X.shape
print("样本量 %d；男 %d、女 %d；年龄 %d–%d 岁" % (n, (d.sex == 1).sum(), (d.sex == 2).sum(), d.age.min(), d.age.max()))
total = X.sum(1)
print("PHQ-9 总分均值 %.2f；总分 ≥ 10（常用的中度及以上阈值）占 %.1f%%" % (total.mean(), 100 * (total >= 10).mean()))
dist = pd.DataFrame([np.bincount(X[:, j], minlength=4) / n for j in range(p)], index=items, columns=["0", "1", "2", "3"])
dist["均值"] = X.mean(0)
dist["标准差"] = X.std(0)
print(dist.round(3).to_string())

# %% [markdown]
# ## 3. 构网：多分格相关 + EBICglasso
#
# **输入矩阵。** 条目是 4 级有序变量，专题页推荐用**多分格相关**：假设每个条目背后有一个连续的正态变量被 3 个阈值切成 4 段，用每对条目的 4×4 列联表做最大似然估计相关（下面的实现先由边际比例定阈值，再一维搜索 $\rho$）。作为对照也计算 Spearman 相关。
#
# **估计网络。** 图形 LASSO 对精度矩阵的非对角元做 $\ell_1$ 惩罚，$\lambda$ 在 $[0.01\lambda_{\max},\lambda_{\max}]$ 的对数网格上由 EBIC（$\gamma=0.5$）选择；实现与专题[代码示例](symptom-networks.html#code)中的 EBICglasso 单元相同，只是改为直接接收相关矩阵。
#
# %%
def polychoric_pair(x, y, cats=4):
    def thresholds(v):
        c = np.cumsum(np.bincount(v, minlength=cats))[:-1] / len(v)
        return norm.ppf(np.clip(c, 1e-6, 1 - 1e-6))
    a, b = thresholds(x), thresholds(y)
    tab = np.zeros((cats, cats))
    np.add.at(tab, (x, y), 1)
    pts = np.array([(ai, bj) for ai in a for bj in b])

    def nll(r):
        F = np.zeros((cats + 1, cats + 1))
        F[cats, :] = np.r_[0, norm.cdf(b), 1]
        F[:, cats] = np.r_[0, norm.cdf(a), 1]
        F[1:cats, 1:cats] = multivariate_normal.cdf(pts, mean=[0, 0], cov=[[1, r], [r, 1]]).reshape(cats - 1, cats - 1)
        P = F[1:, 1:] - F[:-1, 1:] - F[1:, :-1] + F[:-1, :-1]
        return -(tab * np.log(np.clip(P, 1e-12, None))).sum()

    return minimize_scalar(nll, bounds=(-0.99, 0.99), method="bounded", options={"xatol": 1e-4}).x


def polychoric(X):
    q = X.shape[1]
    R = np.eye(q)
    for i in range(q):
        for j in range(i + 1, q):
            R[i, j] = R[j, i] = polychoric_pair(X[:, i], X[:, j])
    w, V = np.linalg.eigh(R)                 # 逐对估计不保证正定，必要时做最小的特征值修正
    if w.min() < 1e-6:
        R = V @ np.diag(np.clip(w, 1e-6, None)) @ V.T
        R = R / np.sqrt(np.outer(np.diag(R), np.diag(R)))
    return R


def glasso(S, lam, W0=None, max_iter=200, tol=1e-5):
    """图形 LASSO（块坐标下降，对角元不惩罚）。返回精度矩阵估计 Θ 与协方差估计 W。"""
    q = S.shape[0]
    W = S.copy() if W0 is None else W0.copy()
    B = np.zeros((q, q))
    for _ in range(max_iter):
        W_old = W.copy()
        for j in range(q):
            idx = np.arange(q) != j
            W11, s12, beta = W[np.ix_(idx, idx)], S[idx, j], B[idx, j].copy()
            for _ in range(100):
                beta_old = beta.copy()
                for k in range(q - 1):
                    r = s12[k] - W11[k] @ beta + W11[k, k] * beta[k]
                    beta[k] = np.sign(r) * max(abs(r) - lam, 0) / W11[k, k]
                if np.max(np.abs(beta - beta_old)) < tol:
                    break
            B[idx, j] = beta
            W[idx, j] = W[j, idx] = W11 @ beta
        if np.mean(np.abs(W - W_old)) < tol:
            break
    Theta = np.zeros((q, q))
    for j in range(q):
        idx = np.arange(q) != j
        t22 = 1.0 / (W[j, j] - W[idx, j] @ B[idx, j])
        Theta[j, j] = t22
        Theta[idx, j] = -B[idx, j] * t22
    return (Theta + Theta.T) / 2, W


def ebic_glasso(S, n_obs, gamma=0.5, n_lambda=40, ratio=0.01):
    q = S.shape[0]
    lam_max = np.max(np.abs(S - np.eye(q)))
    best, W = None, None
    for lam in np.exp(np.linspace(np.log(lam_max), np.log(ratio * lam_max), n_lambda)):
        K, W = glasso(S, lam, W0=W)
        E = int(np.sum(np.abs(K[np.triu_indices(q, 1)]) > 1e-8))
        loglik = np.linalg.slogdet(K)[1] - np.trace(S @ K)
        ebic = -n_obs * loglik + E * np.log(n_obs) + 4 * gamma * E * np.log(q)
        if best is None or ebic < best[0]:
            best = (ebic, lam, K)
    _, lam, K = best
    dK = np.sqrt(np.diag(K))
    P = -K / np.outer(dK, dK)
    np.fill_diagonal(P, 0)
    P[np.abs(P) < 1e-8] = 0
    return P, lam


iu = np.triu_indices(p, 1)
R_poly = polychoric(X)
R_spear = spearmanr(X).statistic
print("多分格相关 vs Spearman：平均 %.3f vs %.3f；两者逐对相关 %.3f"
      % (R_poly[iu].mean(), R_spear[iu].mean(), np.corrcoef(R_poly[iu], R_spear[iu])[0, 1]))

P_net, lam = ebic_glasso(R_poly, n)
P_sp, lam_sp = ebic_glasso(R_spear, n)
print("EBICglasso（多分格）：λ = %.4f，非零边 %d / %d，最大边权 %.3f"
      % (lam, int((P_net[iu] != 0).sum()), len(iu[0]), P_net[iu].max()))
print("EBICglasso（Spearman）：非零边 %d；两种输入的边权相关 %.3f"
      % (int((P_sp[iu] != 0).sum()), np.corrcoef(P_net[iu], P_sp[iu])[0, 1]))
top = np.argsort(P_net[iu])[::-1][:5]
print("最强的 5 条边：")
for t in top:
    i, j = iu[0][t], iu[1][t]
    print("  %s（%s）– %s（%s）：%.3f" % (items[i], short[i], items[j], short[j], P_net[i, j]))
neg = [(items[i], items[j], round(P_net[i, j], 3)) for i, j in zip(*iu) if P_net[i, j] < 0]
print("负边：", neg if neg else "无")

# %% [markdown]
# ## 4. 核心指标：强度、预期影响与可预测性
#
# - 强度 $s_i=\sum_j|w_{ij}|$，预期影响 $\mathrm{EI}_i=\sum_j w_{ij}$（没有负边时二者相同）；
# - 节点可预测性 $R^2_i=1-1/K_{ii}$，其中 $K$ 是多分格相关矩阵的逆（未正则化），表示该症状能被其余 8 个症状线性解释的比例（见[混合图模型与可预测性](symptom-networks.mixed-graphical-models.html)）。
#
# %%
strength = np.abs(P_net).sum(1)
ei = P_net.sum(1)
R2 = 1 - 1 / np.diag(np.linalg.inv(R_poly))
tab = pd.DataFrame({"条目": short, "强度": strength, "EI": ei, "可预测性R2": R2, "标准差": X.std(0)}, index=items)
print(tab.sort_values("强度", ascending=False).round(3).to_string())
rho_sd = spearmanr(strength, X.std(0)).statistic
print("强度与条目标准差的 Spearman 相关：%.2f（9 个条目，仅作描述）" % rho_sd)

# %% [markdown]
# ## 5. 与零模型比较，以及估计的稳定性
#
# **(a) 置换得到的“空网络”。** 把每个条目在被试之间独立打乱，破坏条目之间的一切关联但保留每个条目的分布，再走同样的流程。正确的流程应当几乎给出空网络；它告诉我们第 3 节的边不是估计方法“凭空制造”的。
#
# **(b) 病例删除 bootstrap。** 按 Epskamp 等（2018）的思路，随机删去 10%–70% 的被试，重新估计网络并计算强度，与全样本强度做相关。CS 系数 = 在 95% 的重抽样中相关仍 ≥ 0.7 时可以删去的最大比例（见[抽样不确定性](symptom-networks.stability.html)）。为控制运行时间，每个比例只做 30 次。
#
# **(c) 网络比较检验（NCT）。** 男女分别估计网络，计算结构不变性统计量 $M$（边差的最大绝对值）和全局强度差 $S$；把性别标签随机置换 100 次得到零分布（见[网络比较](symptom-networks.network-comparison.html)）。
#
# %%
rng = np.random.default_rng(11)
Xperm = np.column_stack([rng.permutation(X[:, j]) for j in range(p)])
P_null, _ = ebic_glasso(spearmanr(Xperm).statistic, n)
print("(a) 置换数据的 EBICglasso：非零边 %d 条，最大 |边权| %.3f" % (int((P_null[iu] != 0).sum()), np.abs(P_null[iu]).max()))

drop_props = [0.1, 0.3, 0.5, 0.7]
cs_rows = []
for prop in drop_props:
    m = int(round(n * (1 - prop)))
    cors = []
    for b in range(30):
        idx = rng.choice(n, m, replace=False)
        Pb, _ = ebic_glasso(polychoric(X[idx]), m, n_lambda=20)
        cors.append(spearmanr(np.abs(Pb).sum(1), strength).statistic)
    cors = np.array(cors)
    cs_rows.append((prop, np.percentile(cors, 5), np.mean(cors >= 0.7)))
    print("(b) 删去 %.0f%%：强度与全样本相关的第 5 百分位 %.3f；相关 ≥ 0.7 的比例 %.2f" % (100 * prop, cs_rows[-1][1], cs_rows[-1][2]))
ok = [prop for prop, _, frac in cs_rows if frac >= 0.95]
cs = max(ok) if ok else 0.0
print("    强度的 CS 系数（在所试比例中）≈ %.1f" % cs)

male, female = (d.sex == 1).to_numpy(), (d.sex == 2).to_numpy()


def nct_stats(Xa, Xb):
    Pa, _ = ebic_glasso(polychoric(Xa), len(Xa), n_lambda=20)
    Pb, _ = ebic_glasso(polychoric(Xb), len(Xb), n_lambda=20)
    return np.abs(Pa[iu] - Pb[iu]).max(), abs(np.abs(Pa[iu]).sum() - np.abs(Pb[iu]).sum()), Pa, Pb


M_obs, S_obs, P_m, P_f = nct_stats(X[male], X[female])
perm_M, perm_S = [], []
for b in range(100):
    lab = rng.permutation(male)
    Mb, Sb, _, _ = nct_stats(X[lab], X[~lab])
    perm_M.append(Mb)
    perm_S.append(Sb)
pM = (np.sum(np.array(perm_M) >= M_obs) + 1) / 101
pS = (np.sum(np.array(perm_S) >= S_obs) + 1) / 101
k = int(np.argmax(np.abs(P_m[iu] - P_f[iu])))
print("(c) 男 %d 人、女 %d 人。M = %.3f（p = %.3f），差别最大的边 %s–%s：男 %.3f，女 %.3f"
      % (male.sum(), female.sum(), M_obs, pM, items[iu[0][k]], items[iu[1][k]], P_m[iu][k], P_f[iu][k]))
print("    全局强度：男 %.3f，女 %.3f，S = %.3f（p = %.3f）"
      % (np.abs(P_m[iu]).sum(), np.abs(P_f[iu]).sum(), S_obs, pS))
print("    女性 PHQ-9 总分均值 %.2f，男性 %.2f" % (total[female].mean(), total[male].mean()))

# %% [markdown]
# ## 6. 作图
#
# %%
G = nx.Graph()
G.add_nodes_from(range(p))
for i, j in zip(*iu):
    if P_net[i, j] != 0:
        G.add_edge(i, j, weight=P_net[i, j])
pos = nx.circular_layout(G)
fig, ax = plt.subplots(1, 3, figsize=(15, 4.5))
widths = [8 * abs(G[u][v]["weight"]) for u, v in G.edges()]
colors = ["tab:blue" if G[u][v]["weight"] > 0 else "tab:red" for u, v in G.edges()]
nx.draw_networkx_nodes(G, pos, ax=ax[0], node_size=500, node_color=plt.cm.Greys(0.2 + 0.6 * R2))
nx.draw_networkx_edges(G, pos, ax=ax[0], width=widths, edge_color=colors)
nx.draw_networkx_labels(G, pos, {i: items[i].replace("PHQ", "") for i in range(p)}, ax=ax[0], font_size=9)
ax[0].set_title("PHQ-9 network (EBICglasso, polychoric)\nnode shade = predictability")
ax[0].axis("off")
order = np.argsort(strength)
ax[1].barh(range(p), strength[order], color="gray")
ax[1].set_yticks(range(p))
ax[1].set_yticklabels([items[i] for i in order])
ax[1].set_xlabel("strength")
ax[1].set_title("Strength centrality")
ax[2].plot([0] + drop_props, [1] + [r[1] for r in cs_rows], "o-")
ax[2].axhline(0.7, color="gray", ls="--")
ax[2].set_xlabel("proportion of cases dropped")
ax[2].set_ylabel("5th percentile of correlation")
ax[2].set_ylim(0, 1.02)
ax[2].set_title("Case-dropping bootstrap (strength)")
plt.tight_layout()

# %% [markdown]
# ## 7. 解读与局限
#
# **结果**
#
# 1. **输入矩阵的选择改变边权的大小，但几乎不改变结构。** 多分格相关的平均值（约 0.57）远高于 Spearman 相关（约 0.35）：大量 0 分把秩相关压低了。两种输入得到的 EBICglasso 网络都保留了 36 条可能边中的 33 条，边权的相关约 0.9。样本量大时 EBIC 选出的 $\lambda$ 很小，网络相当稠密。
# 2. **最强的边连接内容相近或理论上相邻的条目**：兴趣减退–情绪低落（PHQ-9 的两个核心条目）、睡眠–疲乏、情绪低落–自我评价低、自我评价低–自杀意念。两条很弱的负边都与自杀意念有关。
# 3. **强度最高的是情绪低落，但其余条目的强度彼此接近。** 可预测性在 0.46（食欲）到 0.75（情绪低落）之间：睡眠、食欲这类把“增多/减少”两个方向合在一个条目里的症状，被其余症状解释得最少。自杀意念的标准差最小，强度却居中偏上——多分格相关部分纠正了“方差小、相关被压低”的问题，但它的估计也最不稳定。
# 4. **置换数据得到空网络**，说明这些边不是正则化流程制造的。
# 5. **中心性排序并不像样本量暗示的那样稳定。** 约 5000 人的样本，强度的 CS 系数在所试比例中只有约 0.3，刚过 0.25 的最低建议、低于 0.5 的理想值。原因是除情绪低落外，各条目的强度相差很小，删去部分被试后排序就会互换。样本大不等于排序可靠，CS 系数必须报告。
# 6. **男女网络没有可检测的差异**：结构不变性和全局强度两项置换检验都不显著。差别最大的一条边（自我评价低–注意力）在两组间相差约 0.16，但这种量级的差异在随机分组中也很常见。女性平均症状更重，严重程度分布的差别本身就可能改变相关的大小，解释任何差异时都要考虑这一点。
#
# **不能这样解读**：“情绪低落强度最高，所以它是抑郁的核心、应优先干预。”截面网络描述的是人与人之间的条件关联，边是无向的；中心性不等于干预靶点（见[横断面统计依赖与因果作用](symptom-networks.dependence-vs-causation.html)）。
#
# **局限**
#
# - 这是一般人群样本，多数人几乎没有症状；网络结构由“0 分与 1 分之间”的差异主导，不能直接推广到临床样本。临床样本的入组标准又会截断严重程度，压低相关。
# - 没有使用 NHANES 的抽样权重和复杂抽样设计，结果描述的是这 5,068 名受访者，而不是严格意义上的美国成人总体。
# - 多分格相关假设每个条目背后是正态变量；自杀意念条目约 97% 为 0，它的相关与边权估计最不稳定。
# - PHQ-9 的睡眠、食欲、精神运动条目各把两个相反方向的症状合在一个条目里，这会削弱它们与其他症状的关联。
# - bootstrap 与置换次数都很少（30 次、100 次），只为演示流程；正式分析应各做 1000 次以上，并在每次重抽样时完整重复调参。
#