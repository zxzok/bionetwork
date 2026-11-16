"""Animated explainer: 网络从哪里来 (nodes & edges, correlation vs partial correlation, sampling error, thresholds, null models, multiple comparisons, bias & stability)."""
import random

import networkx as nx
import numpy as np

from common import *  # noqa: F401,F403
from ahelp import NetView, counter, fit, nv_edge, recap_rows, sf_graph, parts_slide

TITLE = "网络从哪里来：构建选择与统计验证"

# ---- simulated resting-state data: 30 regions in 3 systems
_rng = np.random.default_rng(11)
NREG, TT = 30, 200
SYS = np.repeat([0, 1, 2], 10)
_lat = _rng.normal(size=(3, TT))
_glob = _rng.normal(size=TT)
TS = np.array([0.9 * _lat[SYS[i]] + 0.35 * _glob + _rng.normal(size=TT) * 1.0 for i in range(NREG)])
CM = np.corrcoef(TS)
_iu = np.triu_indices(NREG, 1)


def prop_graph(C, dens):
    w = C[_iu]
    m = int(round(dens * len(w)))
    idx = np.argsort(-w)[:m]
    G = nx.Graph(); G.add_nodes_from(range(C.shape[0]))
    G.add_edges_from((int(_iu[0][i]), int(_iu[1][i])) for i in idx)
    return G


def metrics(G):
    return nx.average_clustering(G), nx.global_efficiency(G)


DENS = [0.05, 0.15, 0.30]
HOOK = [metrics(prop_graph(CM, d)) for d in DENS]

# ---- chain and collider
_r2 = np.random.default_rng(3)
_n = 2000
A = _r2.normal(size=_n); B = A + 0.7 * _r2.normal(size=_n); Cc = B + 0.7 * _r2.normal(size=_n)


def pcor(X):
    P = np.linalg.inv(np.cov(X))
    d = np.sqrt(np.diag(P))
    return -P / np.outer(d, d)


R_CHAIN = np.corrcoef([A, B, Cc]); P_CHAIN = pcor(np.array([A, B, Cc]))
X1 = _r2.normal(size=_n); X2 = _r2.normal(size=_n); X3 = X1 + X2 + 0.5 * _r2.normal(size=_n)
R_COLL = np.corrcoef([X1, X2, X3]); P_COLL = pcor(np.array([X1, X2, X3]))
assert 0.65 < R_CHAIN[0, 2] < 0.75 and abs(P_CHAIN[0, 2]) < 0.05
assert abs(R_COLL[0, 1]) < 0.05 and P_COLL[0, 1] < -0.5

# ---- null models for a disassortative network
GS = sf_graph(400, 2.3, seed=5)
R_OBS = nx.degree_assortativity_coefficient(GS)
_M = GS.number_of_edges()
R_ER = np.array([nx.degree_assortativity_coefficient(nx.gnm_random_graph(GS.number_of_nodes(), _M, seed=s)) for s in range(200)])
R_DP = []
for s in range(200):
    H = GS.copy(); nx.double_edge_swap(H, nswap=3 * _M, max_tries=10 ** 6, seed=s)
    R_DP.append(nx.degree_assortativity_coefficient(H))
R_DP = np.array(R_DP)
Z_ER = (R_OBS - R_ER.mean()) / R_ER.std()
Z_DP = (R_OBS - R_DP.mean()) / R_DP.std()
assert Z_ER < -4 and abs(Z_DP) < 1.2, (R_OBS, Z_ER, Z_DP)

LINES = {
    # hook
    "h0": "静息态功能磁共振，是让人在扫描仪里安静躺着，记录各个脑区的信号，随时间怎样起伏。",
    "h1": "左边这张图，是一份模拟的静息态数据：三十个脑区，两两之间的相关系数。颜色越红，两个脑区的信号越同步。",
    "h2": "要变成网络，得先决定保留哪些边。保留的边占全部可能边数的比例，叫密度。只保留最强的百分之五，网络是右边这个样子。",
    "h3": "保留百分之十五，再保留百分之三十。同一份数据，右上角的聚集系数和全局效率，一路在变。",
    "h3b": "全局效率，衡量的是网络整体传递信息有多快：节点之间的距离越短，效率越高。",
    "h4": "【慢】网络不是直接测出来的，而是一连串建模选择的产物。这一期要分清：哪些结构是真的，哪些是我们构建时造出来的。",
    # parts
    "q0": "这一期分三部分来讲。",
    "q1": "第一部分，网络怎样构建：节点和边的定义，以及每条边的估计误差。",
    "q2": "第二部分，阈值和零模型：阈值怎样定，指标又该和什么比较。",
    "q3": "第三部分，统计推断和可靠性：多重比较、系统偏倚和稳定性。",
    # nodes & edges
    "n1": "先看第一部分。第一个选择是节点。同一个大脑，可以划分成几十个脑区，也可以划分成几百个。",
    "n2": "研究发现，换一种划分尺度，小世界性、度分布这些指标，都会系统性地变化。所以不同研究之间，指标的绝对值很难直接比较。",
    "n3": "第二个选择是边。边至少有四种不同的性质。",
    "n4": "第一种是物理连接，比如蛋白质结合、白质纤维。第二种是统计关联，比如两个脑区信号的相关。",
    "n5": "第三种是功能关联。比如蛋白质数据库，会把实验、共表达、文本挖掘等多种证据，整合成一个综合得分。",
    "n5b": "这样得到的网络里，边的数值代表证据的强弱，而不是作用的强弱。",
    "n5c": "第四种是因果或有向关系，比如转录因子调控靶基因。",
    "n6": "【慢】它们回答的问题不同。比如在统计关联网络里，最短路径就没有明确的物理含义。",
    # correlation vs partial correlation
    "p1": "统计关联最常用的是相关系数。但相关会把间接关系也连成边。",
    "p2": "设想甲影响乙，乙影响丙，甲和丙之间并没有直接作用。",
    "p3": "可在模拟出来的数据里，右上角这张相关系数表显示，甲和丙的相关系数接近零点七。",
    "p4": "偏相关，是在控制其余所有变量之后，再看两两之间的关联。下面这张偏相关表里，甲和丙之间几乎是零，这条边就消失了。",
    "p5": "但是偏相关也有陷阱。如果甲和乙共同影响丙，甲和乙本来无关，相关系数接近零。",
    "p5b": "【慢】控制了丙之后，甲和乙反而出现了很强的负偏相关。所以偏相关更接近直接关联，但仍然不是因果。",
    # sampling error
    "s1": "第一部分的最后一个问题：每一条边都是估计出来的，带着误差。下面这条数轴是相关系数，金色虚线是真实值零点三。",
    "s2": "只有三十个样本时，蓝色的置信区间跨过了零，连正负都说不准。置信区间，就是真实值大概率所在的范围。",
    "s3": "一千个样本时，绿色的区间宽度只有零点一左右。区间宽度缩小一半，大约需要四倍的样本。",
    "s4": "【慢】要以百分之八十的把握检测出零点三的相关，大约需要八十五个样本；如果真实相关是零点一，就要将近八百个。",
    # thresholds
    "t1": "下面进入第二部分。回到开头的问题：阈值应该怎样定。",
    "t2": "先看密度的影响。这张图横轴是密度，纵轴是指标的数值。同一份数据，换一个密度，聚集系数和全局效率可以差得很远。",
    "t3": "这会带来偏差。如果患者组整体连接偏弱，用同一个绝对阈值，也就是同一个相关系数的门槛，患者的网络就更稀疏。",
    "t3b": "这时两组指标的差异，其实只是密度的差异。",
    "t4": "改用比例阈值、强制两组密度相同，又会为了凑够边数，纳入更多接近噪声的弱边，也就是红色这些边，让网络看上去更随机。",
    "t5": "【慢】稳妥的做法，是在一段密度范围上报告结果，并且在看结果之前，就定好方案。",
    # null models
    "z1": "一个指标的数值本身很少有意义。比如聚集系数零点二五，是高是低，要看和什么比。",
    "z2": "零模型，就是保留真实网络的某些性质，把其余部分随机化，生成很多参照网络。",
    "z3": "看观测值落在参照分布的什么位置。偏离了几个标准差，叫标准分数，画面上记作z。",
    "z4": "这张模拟网络的度相关系数是负零点三一，也就是异配。上面灰色的，是边数相同的随机图；观测值远在分布之外，标准分数约是负八。",
    "z5": "下面绿色的，是保持度序列的随机网络，观测值落在了分布中间。也就是说，异配的大部分，度序列本身就能解释。",
    "z5b": "【慢】零模型选什么，决定了结论的含义。",
    # multiple comparisons
    "m1": "最后是第三部分。比较患者和对照的网络时，如果逐条边检验，九十个脑区就有四千零五条边。",
    "m2": "这么多检验，即使没有任何真实差异，也会冒出一批假阳性，就是这些红线。",
    "m3": "一种办法是控制错误发现率，也就是控制在所有阳性结果里，假阳性所占的比例。",
    "m3b": "另一种是基于网络的统计：先用一个阈值挑出差异较大的边，看它们连成多大的一片。这里最大的一片有八条边。",
    "m4": "再把组别标签打乱很多次，每次只记录最大那一片的大小，作为参照分布，看真实的这一片是不是异常地大。",
    "m5": "【慢】要注意，这种方法的结论单位是整个子网络：可以说这片连接整体有差异，但不能说其中任何一条边单独显著。",
    # bias & stability
    "b1": "还有一类误差，增加样本也消除不了，那就是系统性偏倚。",
    "b2": "相互作用数据库记录的，是被研究过的相互作用。研究越多的蛋白，记录的伙伴越多，度就越高。这张示意图里，下面的柱子是发表的研究，上面的放射线是记录到的伙伴。",
    "b3": "在脑影像里，哪怕毫米级的头动，也会系统性地增强近距离脑区的相关，削弱远距离的相关。",
    "b3b": "研究者为此比较了多种去除头动影响的处理策略。",
    "b4": "最后是稳定性。有放回地重抽样被试，每次重新构建网络，看哪些边一直都在。",
    "b5": "绿色的边几乎每次都在；金色的边时有时无。强度接近阈值的边，入选与否，几乎像抛硬币。",
    "b5b": "【慢】这样的边，不应该承载重要结论。",
    # recap
    "r1": "好，我们来总结一下。",
    "r2": "第一，网络是建模选择的产物：节点、边、估计方法和阈值，都要交代清楚。",
    "r3": "第二，指标要和合适的零模型比较，并且处理好多重比较。",
    "r4": "第三，结论要经得起重抽样、换阈值和换数据的检验。",
}

SYSC = [BLUE, GREEN, GOLD]


def heat(C, size=4.2, vmin=-0.2, vmax=1.0):
    n = C.shape[0]
    c = size / n
    lo, hi = ManimColor("#1a2740"), ManimColor(RED)
    sq = VGroup()
    for i in range(n):
        for j in range(n):
            t = float(np.clip((C[i, j] - vmin) / (vmax - vmin), 0, 1))
            sq.add(Square(c, stroke_width=0, fill_color=interpolate_color(lo, hi, t), fill_opacity=1).move_to([j * c, -i * c, 0]))
    return sq


def ring(n, c, r):
    return {i: c + r * np.array([np.cos(PI / 2 - 2 * PI * i / n), np.sin(PI / 2 - 2 * PI * i / n), 0]) for i in range(n)}


class Episode(Narrated):
    LINES = LINES

    def construct(self):
        self.hook()
        parts_slide(self, "这一期分三部分", ["一  网络怎样构建：节点、边与估计误差", "二  阈值与零模型", "三  统计推断与可靠性"])
        self.nodes_edges()
        self.partial()
        self.sampling()
        self.thresholds()
        self.nulls()
        self.multiple()
        self.bias_stability()
        self.recap()

    # ------------------------------------------------------------------ hook
    def hook(self):
        hm = heat(CM).move_to([-3.6, -0.2, 0])
        pos = ring(NREG, np.array([3.4, -0.2, 0]), 2.5)
        dots = VGroup(*[Dot(pos[i], radius=0.09, color=SYSC[SYS[i]]) for i in range(NREG)])
        with self.say("h0") as d:
            self.clip_on("yt_fmri_wellcome.mp4", "center", "视频：Wellcome Centre for Human Neuroimaging · YouTube", start=30)
        self.clip_off()
        with self.say("h1") as d:
            self.play(FadeIn(hm, lag_ratio=0.0005), run_time=d * 0.5)
            self.play(FadeIn(dots), run_time=0.8)
        edges = VGroup()
        ccnt = counter("聚集系数", "", INK, vs=32).move_to([0.0, 2.9, 0])
        hdr = VGroup()

        def show(k, rt):
            G = prop_graph(CM, DENS[k])
            new = VGroup(*[Line(pos[u], pos[v], color=INK, stroke_width=1.8, stroke_opacity=0.55) for u, v in G.edges()])
            C, E = HOOK[k]
            lab = VGroup(T(f"密度 {int(DENS[k] * 100)}%", 26, GOLD),
                         T(f"聚集系数 {C:.2f}", 24, INK), T(f"全局效率 {E:.2f}", 24, INK)).arrange(DOWN, buff=0.12, aligned_edge=LEFT).to_corner(UR, buff=0.35)
            return new, lab
        with self.say("h2") as d:
            e0, l0 = show(0, 1.0)
            self.play(Create(e0), FadeIn(l0), run_time=1.4)
        with self.say("h3") as d:
            e1, l1 = show(1, 1.0)
            self.play(Transform(e0, e1), Transform(l0, l1), run_time=1.4)
            self.wait(d * 0.15)
            e2, l2 = show(2, 1.0)
            self.play(Transform(e0, e2), Transform(l0, l2), run_time=1.4)
        with self.say("h3b") as d:
            self.play(Indicate(l0[2], color=GOLD), run_time=1.2)
        with self.say("h4") as d:
            self.play(VGroup(hm, dots, e0, l0).animate.set_opacity(0.15), run_time=0.8)
            q = T("真实结构，还是构建产物", 44, GOLD, weight=BOLD)
            self.play(Write(q), run_time=1.2)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ nodes and edges
    def nodes_edges(self):
        tag = self.chapter("第一部分 · 节点与边")
        rng = np.random.default_rng(1)

        def brain(c, n, col):
            outline = Ellipse(width=4.6, height=3.4, color=MUTED, stroke_width=3).move_to(c)
            pts = []
            while len(pts) < n:
                p = c + np.array([rng.uniform(-2.1, 2.1), rng.uniform(-1.5, 1.5), 0])
                if ((p[0] - c[0]) / 2.2) ** 2 + ((p[1] - c[1]) / 1.6) ** 2 < 0.9:
                    pts.append(p)
            return VGroup(outline, VGroup(*[Dot(p, radius=0.12 if n < 50 else 0.045, color=col) for p in pts]))
        b1 = brain(np.array([-3.4, -0.2, 0]), 40, BLUE)
        b2 = brain(np.array([3.4, -0.2, 0]), 300, VIOLET)
        l1 = T("几十个脑区", 26, BLUE).next_to(b1, DOWN, buff=0.25)
        l2 = T("几百个脑区", 26, VIOLET).next_to(b2, DOWN, buff=0.25)
        with self.say("n1") as d:
            self.play(FadeIn(tag), Create(b1[0]), FadeIn(b1[1]), FadeIn(l1), run_time=1.2)
            self.play(Create(b2[0]), FadeIn(b2[1], lag_ratio=0.003), FadeIn(l2), run_time=1.4)
        with self.say("n2") as d:
            neq = T("≠", 60, GOLD, weight=BOLD).move_to([0, -0.2, 0])
            self.play(FadeIn(neq, scale=1.5), run_time=0.8)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.6)
        xs = [-5.0, -1.7, 1.7, 5.0]

        def panel(x, title, color, art):
            box = RoundedRectangle(width=3.0, height=3.4, corner_radius=0.2, stroke_color=color, stroke_width=2).move_to([x, -0.1, 0])
            t = T(title, 26, color).next_to(box, UP, buff=0.2)
            return VGroup(box, t, art.move_to([x, -0.1, 0]))
        a1 = VGroup(Circle(radius=0.45, color=BLUE, fill_opacity=0.4), Circle(radius=0.35, color=BLUE, fill_opacity=0.4).shift(RIGHT * 0.7))
        tsx = np.linspace(-1.1, 1.1, 40)
        s1 = np.sin(tsx * 4) * 0.25
        a2 = VGroup(VMobject(color=GREEN).set_points_smoothly([np.array([x, 0.45 + y, 0]) for x, y in zip(tsx, s1)]),
                    VMobject(color=GREEN).set_points_smoothly([np.array([x, -0.45 + y * 0.9 + 0.03 * np.cos(9 * x), 0]) for x, y in zip(tsx, s1)]))
        a3 = VGroup(*[Rectangle(width=0.3, height=h, fill_color=GOLD, fill_opacity=0.8, stroke_width=0) for h in (0.6, 1.2, 0.4, 0.9)]).arrange(RIGHT, buff=0.12, aligned_edge=DOWN)
        a4 = VGroup(Dot(LEFT * 0.8, radius=0.14, color=RED), Dot(RIGHT * 0.8, radius=0.14, color=RED), Arrow(LEFT * 0.7, RIGHT * 0.7, buff=0.1, color=RED))
        ps = [panel(xs[0], "物理连接", BLUE, a1), panel(xs[1], "统计关联", GREEN, a2), panel(xs[2], "功能关联", GOLD, a3), panel(xs[3], "因果 / 有向", RED, a4)]
        with self.say("n3") as d:
            self.play(LaggedStart(*[FadeIn(p[0]) for p in ps], lag_ratio=0.2), run_time=1.2)
        with self.say("n4") as d:
            self.play(FadeIn(ps[0][1:]), run_time=0.8)
            self.wait(d * 0.2)
            self.play(FadeIn(ps[1][1:]), run_time=0.8)
        with self.say("n5") as d:
            self.play(FadeIn(ps[2][1:]), run_time=0.8)
        self.play(FadeOut(VGroup(*ps)), run_time=0.5)
        with self.say("n5b") as d:
            self.clip_on("yt_string_tutorial.mp4", "center", "视频：Lars Juhl Jensen · YouTube", start=60)
        self.clip_off()
        self.play(FadeIn(VGroup(*ps[:3])), FadeIn(ps[3][0]), run_time=0.5)
        with self.say("n5c") as d:
            self.play(FadeIn(ps[3][1:]), run_time=0.8)
        with self.say("n6") as d:
            self.play(Indicate(ps[1], color=GREEN, scale_factor=1.05), run_time=1.2)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ correlation vs partial correlation
    def partial(self):
        tag = self.chapter("第一部分 · 相关与偏相关")
        P = {0: np.array([-4.2, 0.3, 0]), 1: np.array([-2.2, 2.0, 0]), 2: np.array([-0.2, 0.3, 0])}
        names = ["甲", "乙", "丙"]
        nd = [VGroup(Circle(radius=0.4, color=BLUE, fill_opacity=0.25), T(names[i], 30, INK)).move_to(P[i]) for i in range(3)]
        ar1 = Arrow(P[0], P[1], buff=0.45, color=INK); ar2 = Arrow(P[1], P[2], buff=0.45, color=INK)
        with self.say("p1") as d:
            self.play(FadeIn(tag), run_time=0.5)
            self.play(*[FadeIn(x) for x in nd], run_time=1.0)
        with self.say("p2") as d:
            self.play(GrowArrow(ar1), run_time=0.8)
            self.play(GrowArrow(ar2), run_time=0.8)
            no = Cross(Line(P[0], P[2]), stroke_color=MUTED, scale_factor=0.2)
        def mat(M, title, color):
            g = VGroup()
            for i in range(3):
                for j in range(3):
                    v = 1.0 if i == j else M[i, j]
                    t = T(f"{v:.2f}".replace("-", "−") if i != j else "—", 26, INK if i != j else MUTED)
                    t.move_to([j * 1.1, -i * 0.7, 0]); g.add(t)
            hdr = VGroup(*[T(names[j], 24, MUTED).move_to([j * 1.1, 0.7, 0]) for j in range(3)])
            rl = VGroup(*[T(names[i], 24, MUTED).move_to([-0.9, -i * 0.7, 0]) for i in range(3)])
            ttl = T(title, 26, color).move_to([1.1, 1.35, 0])
            return VGroup(g, hdr, rl, ttl)
        mc = mat(R_CHAIN, "相关", GOLD).move_to([3.8, 1.65, 0])
        ac = DashedLine(P[0], P[2], color=GOLD, stroke_width=4)
        with self.say("p3") as d:
            self.play(FadeIn(mc), run_time=0.8)
            cell = mc[0][2]
            self.play(Indicate(cell, color=GOLD, scale_factor=1.6), Create(ac), run_time=1.0)
        mp = mat(P_CHAIN, "偏相关", GREEN).move_to([3.8, -1.95, 0])
        with self.say("p4") as d:
            self.play(FadeIn(mp), run_time=0.8)
            self.play(Indicate(mp[0][2], color=GREEN, scale_factor=1.6), FadeOut(ac), run_time=1.0)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.6)
        Q = {0: np.array([-4.2, 1.8, 0]), 1: np.array([-0.2, 1.8, 0]), 2: np.array([-2.2, 0.0, 0])}
        nd2 = [VGroup(Circle(radius=0.4, color=VIOLET, fill_opacity=0.25), T(names[i], 30, INK)).move_to(Q[i]) for i in range(3)]
        b1 = Arrow(Q[0], Q[2], buff=0.45, color=INK); b2 = Arrow(Q[1], Q[2], buff=0.45, color=INK)
        vr = VGroup(T("相关", 24, GOLD), T(f"{R_COLL[0, 1]:+.2f}".replace("-", "−"), 34, GOLD, weight=BOLD)).arrange(DOWN, buff=0.1).move_to([3.0, 1.0, 0])
        vp = VGroup(T("控制丙之后的偏相关", 24, GREEN), T(f"{P_COLL[0, 1]:+.2f}".replace("-", "−"), 34, GREEN, weight=BOLD)).arrange(DOWN, buff=0.1).move_to([3.0, -1.0, 0])
        ab = DashedLine(Q[0], Q[1], color=RED, stroke_width=4)
        hd = T("甲、乙之间", 24, MUTED).move_to([3.0, 2.3, 0])
        with self.say("p5") as d:
            self.play(*[FadeIn(x) for x in nd2], GrowArrow(b1), GrowArrow(b2), run_time=1.0)
            self.play(FadeIn(hd), FadeIn(vr), run_time=0.8)
        with self.say("p5b") as d:
            self.play(FadeIn(vp), Create(ab), run_time=1.0)
            nc = T("≠ 因果", 34, RED, weight=BOLD).move_to([-2.2, -2.2, 0])
            self.play(FadeIn(nc), run_time=0.6)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ sampling error
    def sampling(self):
        tag = self.chapter("第一部分 · 每条边都有误差")
        ax = NumberLine(x_range=[-0.2, 0.8, 0.1], length=10, color=MUTED, include_numbers=True, font_size=24,
                        decimal_number_config={"num_decimal_places": 1}).move_to(DOWN * 2.2)
        true = DashedLine(ax.n2p(0.3) + UP * 4.2, ax.n2p(0.3), color=GOLD, stroke_width=3)
        zero = DashedLine(ax.n2p(0) + UP * 4.2, ax.n2p(0), color=MUTED, stroke_width=2)
        tl = T("真实相关 0.3", 24, GOLD).next_to(true, UP, buff=0.1)

        def ci(n):
            z, se = np.arctanh(0.3), 1 / np.sqrt(n - 3)
            return np.tanh(z - 1.96 * se), np.tanh(z + 1.96 * se)
        with self.say("s1") as d:
            self.play(FadeIn(tag), Create(ax), Create(true), FadeIn(tl), Create(zero), run_time=1.4)
        rows = []
        for i, n in enumerate((30, 1000)):
            lo, hi = ci(n)
            y = 1.0 - 1.6 * i
            bar = Line(ax.n2p(lo) + UP * (y + 2.2), ax.n2p(hi) + UP * (y + 2.2), color=BLUE if n == 30 else GREEN, stroke_width=8)
            cap = VGroup(*[Line(p + UP * 0.18, p + DOWN * 0.18, color=bar.get_color(), stroke_width=4) for p in (bar.get_start(), bar.get_end())])
            lab = T(f"n = {n}", 26, bar.get_color()).next_to(bar, LEFT, buff=0.3)
            if n == 30:
                lab.next_to(ax.n2p(-0.2) + UP * (y + 2.2), LEFT, buff=0.1)
            rows.append((bar, cap, lab, lo, hi))
        assert rows[0][3] < 0 and 0.09 < rows[1][4] - rows[1][3] < 0.13
        with self.say("s2") as d:
            bar, cap, lab, lo, hi = rows[0]
            self.play(FadeIn(lab), GrowFromCenter(bar), FadeIn(cap), run_time=1.2)
            self.play(Indicate(zero, color=RED), run_time=0.8)
        with self.say("s3") as d:
            bar, cap, lab, lo, hi = rows[1]
            lab.next_to(ax.n2p(-0.2) + UP * (1.0 - 1.6 + 2.2), LEFT, buff=0.1)
            self.play(FadeIn(lab), GrowFromCenter(bar), FadeIn(cap), run_time=1.2)
            w = T(f"宽 {hi - lo:.2f}", 24, GREEN).next_to(bar, DOWN, buff=0.15)
            self.play(FadeIn(w), run_time=0.6)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.6)
        from scipy.stats import norm
        need = lambda rho: (norm.ppf(0.975) + norm.ppf(0.8)) ** 2 / np.arctanh(rho) ** 2 + 3
        n3, n1 = need(0.3), need(0.1)
        assert 83 < n3 < 87 and 770 < n1 < 800
        b3 = Rectangle(width=n3 / 800 * 9, height=0.6, fill_color=BLUE, fill_opacity=0.9, stroke_width=0)
        b1 = Rectangle(width=n1 / 800 * 9, height=0.6, fill_color=VIOLET, fill_opacity=0.9, stroke_width=0)
        VGroup(b3, b1).arrange(DOWN, buff=1.0, aligned_edge=LEFT).move_to([0.6, -0.2, 0])
        t3 = T(f"真实相关 0.3：约 {round(n3)}", 26, BLUE).next_to(b3, UP, buff=0.12, aligned_edge=LEFT)
        t1 = T(f"真实相关 0.1：约 {round(n1)}", 26, VIOLET).next_to(b1, UP, buff=0.12, aligned_edge=LEFT)
        hd = T("80% 把握所需样本量", 28, INK).move_to([0, 2.5, 0])
        with self.say("s4") as d:
            self.play(FadeIn(hd), run_time=0.5)
            self.play(GrowFromEdge(b3, LEFT), FadeIn(t3), run_time=1.0)
            self.wait(d * 0.2)
            self.play(GrowFromEdge(b1, LEFT), FadeIn(t1), run_time=1.4)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ thresholds
    def thresholds(self):
        tag = self.chapter("第二部分 · 阈值")
        ds = np.linspace(0.05, 0.5, 19)
        cs, es = zip(*[metrics(prop_graph(CM, d_)) for d_ in ds])
        ax = Axes(x_range=[0, 0.5, 0.1], y_range=[0, 1, 0.5], x_length=7.5, y_length=4.2,
                  axis_config={"color": MUTED, "include_tip": False, "font_size": 22},
                  x_axis_config={"numbers_to_include": [0.1, 0.2, 0.3, 0.4, 0.5]}, y_axis_config={"numbers_to_include": [0, 0.5, 1]}).move_to([0, -0.4, 0])
        xl = T("密度", 22, MUTED).next_to(ax.x_axis, DOWN, buff=0.35)
        cC = ax.plot_line_graph(ds, cs, line_color=GREEN, vertex_dot_radius=0.05, stroke_width=4)
        cE = ax.plot_line_graph(ds, es, line_color=GOLD, vertex_dot_radius=0.05, stroke_width=4)
        lC = T("聚集系数", 24, GREEN).next_to(cC["line_graph"].get_end(), RIGHT, buff=0.15)
        lE = T("全局效率", 24, GOLD).next_to(cE["line_graph"].get_end(), RIGHT, buff=0.15)
        assert max(es) - min(es) > 0.3
        with self.say("t1") as d:
            self.play(FadeIn(tag), run_time=0.5)
            q = T("阈值怎样定", 44, GOLD, weight=BOLD)
            self.play(FadeIn(q), run_time=0.6)
            self.play(FadeOut(q), run_time=0.5)
        with self.say("t2") as d:
            self.play(Create(ax), FadeIn(xl), run_time=0.8)
            self.play(Create(cC), FadeIn(lC), run_time=1.2)
            self.play(Create(cE), FadeIn(lE), run_time=1.2)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.6)
        # patient group: same structure, weaker signal
        rng = np.random.default_rng(5)
        TP = np.array([0.75 * _lat[SYS[i]] + 0.3 * _glob + rng.normal(size=TT) for i in range(NREG)])
        CP = np.corrcoef(TP)
        tau = 0.35
        Gc = nx.Graph([(int(i), int(j)) for i, j in zip(*_iu) if CM[i, j] > tau]); Gc.add_nodes_from(range(NREG))
        Gp = nx.Graph([(int(i), int(j)) for i, j in zip(*_iu) if CP[i, j] > tau]); Gp.add_nodes_from(range(NREG))
        assert 0.25 * Gc.number_of_edges() < Gp.number_of_edges() < 0.7 * Gc.number_of_edges(), (Gc.number_of_edges(), Gp.number_of_edges())
        pc = ring(NREG, np.array([-3.4, -0.4, 0]), 2.2)
        pp = ring(NREG, np.array([3.4, -0.4, 0]), 2.2)

        def draw(G, pos):
            return VGroup(VGroup(*[Line(pos[u], pos[v], color=MUTED, stroke_width=1.2, stroke_opacity=0.5) for u, v in G.edges()]),
                          VGroup(*[Dot(pos[i], radius=0.08, color=SYSC[SYS[i]]) for i in range(NREG)]))
        vc, vp = draw(Gc, pc), draw(Gp, pp)
        lc = T(f"对照：{Gc.number_of_edges()} 条边", 26, INK).move_to([-3.4, 2.5, 0])
        lp = T(f"患者：{Gp.number_of_edges()} 条边", 26, INK).move_to([3.4, 2.5, 0])
        same = T("同一个绝对阈值", 24, GOLD).move_to([0, 3.2, 0])
        with self.say("t3") as d:
            self.play(FadeIn(same), FadeIn(vc), FadeIn(lc), run_time=1.0)
            self.play(FadeIn(vp), FadeIn(lp), run_time=1.0)
        with self.say("t3b") as d:
            self.play(Indicate(lc, color=GOLD), Indicate(lp, color=GOLD), run_time=1.2)
        m = Gc.number_of_edges()
        w = CP[_iu]
        idx = np.argsort(-w)[:m]
        Gp2 = nx.Graph([(int(_iu[0][i]), int(_iu[1][i])) for i in idx]); Gp2.add_nodes_from(range(NREG))
        extra = [e for e in Gp2.edges() if not Gp.has_edge(*e)]
        with self.say("t4") as d:
            self.play(Transform(same, T("同一个密度", 24, GOLD).move_to(same)), run_time=0.5)
            weak = VGroup(*[Line(pp[u], pp[v], color=RED, stroke_width=1.5, stroke_opacity=0.8) for u, v in extra])
            self.play(Create(weak), Transform(lp, T(f"患者：{m} 条边", 26, INK).move_to(lp)), run_time=1.6)
            wl = T("新加入的弱边", 24, RED).move_to([3.4, -3.2, 0])
            self.play(FadeIn(wl), run_time=0.5)
        with self.say("t5") as d:
            self.play(*[FadeOut(m_) for m_ in self.mobjects if m_ is not tag], run_time=0.6)
            band = VGroup(T("密度范围", 32, GOLD, weight=BOLD), T("+", 32, INK), T("预先确定方案", 32, GOLD, weight=BOLD)).arrange(RIGHT, buff=0.4)
            self.play(FadeIn(band, shift=UP * 0.2), run_time=1.0)
        self.play(*[FadeOut(m_) for m_ in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ null models
    def nulls(self):
        tag = self.chapter("第二部分 · 零模型")
        with self.say("z1") as d:
            self.play(FadeIn(tag), run_time=0.5)
            v = VGroup(T("聚集系数 = 0.25", 40, INK), T("高还是低", 40, GOLD, weight=BOLD)).arrange(DOWN, buff=0.4)
            self.play(FadeIn(v[0]), run_time=0.8)
            self.play(FadeIn(v[1]), run_time=0.8)
        self.play(FadeOut(v), run_time=0.5)
        pos = fit(nx.kamada_kawai_layout(nx.barabasi_albert_graph(40, 2, seed=1)), (-6.2, -2.0, -1.6, 1.6))
        G0 = nx.barabasi_albert_graph(40, 2, seed=1)
        v0 = NetView(G0, pos, color=BLUE, rmin=0.05, rk=0.02, eo=0.45)
        minis = []
        for s in range(6):
            H = G0.copy(); nx.double_edge_swap(H, 120, max_tries=10 ** 5, seed=s)
            p = fit(nx.kamada_kawai_layout(H), (0, 1.6, 0, 1.3))
            vv = NetView(H, p, color=MUTED, rmin=0.025, rk=0.01, ew=0.7, eo=0.4)
            vv.group.move_to([0.3 + 2.0 * (s % 3), 1.1 - 2.0 * (s // 3), 0])
            minis.append(vv.group)
        with self.say("z2") as d:
            self.play(FadeIn(v0.group), run_time=0.8)
            self.play(LaggedStart(*[TransformFromCopy(v0.group, m_) for m_ in minis], lag_ratio=0.2), run_time=d * 0.6)
        self.play(*[FadeOut(m_) for m_ in self.mobjects if m_ is not tag], run_time=0.6)
        # two null distributions for the same observed value
        lo = min(R_OBS, R_ER.min(), R_DP.min()) - 0.03
        hi = max(R_OBS, R_ER.max(), R_DP.max()) + 0.03
        def mkax(y):
            return NumberLine(x_range=[lo, hi, 0.1], length=9, color=MUTED, include_numbers=True, font_size=20,
                              numbers_to_include=[round(x, 1) for x in np.arange(np.ceil(lo * 10) / 10, hi, 0.1)],
                              decimal_number_config={"num_decimal_places": 1}).move_to([-0.6, y, 0])
        axT, axB = mkax(0.5), mkax(-2.6)

        def hist(vals, color, nl):
            bins = np.linspace(lo, hi, 50)
            h, _ = np.histogram(vals, bins)
            h = h / h.max()
            g = VGroup()
            for c_, a_, b_ in zip(h, bins[:-1], bins[1:]):
                if c_ > 0:
                    x0 = nl.n2p(a_)[0]; x1 = nl.n2p(b_)[0]
                    g.add(Rectangle(width=x1 - x0, height=1.5 * c_, fill_color=color, fill_opacity=0.8, stroke_width=0).move_to([(x0 + x1) / 2, nl.get_y(), 0], aligned_edge=DOWN))
            return g
        hE = hist(R_ER, MUTED, axT)
        hD = hist(R_DP, GREEN, axB)
        xo = axT.n2p(R_OBS)[0]
        obs = Line([xo, 2.3, 0], [xo, -2.6, 0], color=RED, stroke_width=4)
        ol = T(f"观测值 r = {R_OBS:.2f}".replace("-", "−"), 24, RED).next_to(obs, UP, buff=0.05)
        lE = T("边数相同的随机图", 24, MUTED).move_to([5.0, 1.6, 0])
        lD = T("保持度序列的随机网络", 24, GREEN).move_to([5.0, -1.5, 0])
        ax = axT
        with self.say("z3") as d:
            self.play(Create(axT), FadeIn(hE), FadeIn(lE), run_time=1.2)
            self.play(Create(obs), FadeIn(ol), run_time=0.8)
        with self.say("z4") as d:
            ze = T(f"z ≈ {Z_ER:.0f}".replace("-", "−"), 30, MUTED, weight=BOLD).next_to(lE, DOWN, buff=0.15)
            self.play(FadeIn(ze), Indicate(hE, color=MUTED), run_time=1.0)
        with self.say("z5") as d:
            self.play(Create(axB), FadeIn(hD), FadeIn(lD), run_time=1.2)
            zd = T(f"z ≈ {Z_DP:.1f}".replace("-", "−"), 30, GREEN, weight=BOLD).next_to(lD, DOWN, buff=0.15)
            self.play(FadeIn(zd), run_time=0.8)
        with self.say("z5b") as d:
            self.play(Indicate(lE, color=MUTED), Indicate(lD, color=GREEN), run_time=1.2)
        self.play(*[FadeOut(m_) for m_ in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ multiple comparisons
    def multiple(self):
        tag = self.chapter("第三部分 · 多重比较")
        n = 24
        pos = ring(n, np.array([-2.6, -0.3, 0]), 2.6)
        rng = random.Random(3)
        allE = [(i, j) for i in range(n) for j in range(i + 1, n)]
        dots = VGroup(*[Dot(pos[i], radius=0.08, color=INK) for i in range(n)])
        cnt = counter("检验次数", "4005", GOLD, vs=44).move_to([4.2, 1.6, 0])
        with self.say("m1") as d:
            self.play(FadeIn(tag), FadeIn(dots), run_time=0.8)
            faint = VGroup(*[Line(pos[i], pos[j], color=MUTED, stroke_width=0.6, stroke_opacity=0.25) for i, j in allE])
            self.play(Create(faint, lag_ratio=0.002), FadeIn(cnt), run_time=d * 0.5)
        fps = rng.sample(allE, 14)
        with self.say("m2") as d:
            fl = VGroup(*[Line(pos[i], pos[j], color=RED, stroke_width=2.5) for i, j in fps])
            self.play(LaggedStart(*[Create(x) for x in fl], lag_ratio=0.15), run_time=d * 0.6)
            lab = T("假阳性", 26, RED).move_to([4.2, -0.2, 0])
            self.play(FadeIn(lab), run_time=0.5)
        sub = [2, 3, 4, 5, 6, 7]
        clus = [(2, 3), (3, 4), (2, 5), (4, 6), (5, 7), (6, 7), (3, 6), (2, 7)]
        with self.say("m3") as d:
            fdr = T("控制错误发现率", 28, INK).move_to([4.2, -0.2, 0])
            self.play(FadeOut(lab), FadeIn(fdr), run_time=0.8)
        with self.say("m3b") as d:
            self.play(FadeOut(fdr), fl.animate.set_stroke(opacity=0.35), run_time=0.5)
            cl = VGroup(*[Line(pos[i], pos[j], color=GOLD, stroke_width=4) for i, j in clus])
            self.play(Create(cl), run_time=1.2)
            hull = Circle(radius=1.6, color=GOLD, stroke_width=2).move_to(np.mean([pos[i] for i in sub], axis=0))
            self.play(Create(hull), run_time=0.8)
            sz = counter("最大一片", f"{len(clus)} 条边", GOLD, vs=36).move_to([4.2, -0.4, 0])
            self.play(FadeIn(sz), run_time=0.6)
        # permutation null of max component size
        rnd = np.random.default_rng(2)
        null = np.clip(rnd.poisson(2.2, 300), 1, None)
        ax = Axes(x_range=[0, 10, 2], y_range=[0, 1, 1], x_length=4.2, y_length=1.6, axis_config={"color": MUTED, "include_tip": False, "font_size": 20},
                  x_axis_config={"numbers_to_include": [0, 4, 8]}, y_axis_config={"stroke_opacity": 0}).move_to([4.2, -2.4, 0])
        h = np.bincount(null, minlength=11)[:11] / np.bincount(null).max()
        hb = VGroup(*[Rectangle(width=0.32, height=1.4 * v + 0.001, fill_color=MUTED, fill_opacity=0.8, stroke_width=0).move_to(ax.c2p(k, 0), aligned_edge=DOWN)
                      for k, v in enumerate(h) if v > 0])
        mk = Line(ax.c2p(len(clus), 0), ax.c2p(len(clus), 1), color=GOLD, stroke_width=4)
        with self.say("m4") as d:
            self.play(Create(ax), run_time=0.6)
            self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in hb], lag_ratio=0.1), run_time=1.2)
            self.play(Create(mk), run_time=0.6)
            sch = T("示意", 20, MUTED).next_to(ax, DOWN, buff=0.15)
            self.play(FadeIn(sch), run_time=0.3)
        with self.say("m5") as d:
            self.play(cl.animate.set_stroke(width=6), hull.animate.set_stroke(width=4), run_time=0.8)
            one = Cross(Line(pos[3], pos[4]), stroke_color=RED, scale_factor=0.4)
            self.play(Create(one), run_time=0.6)
        self.play(*[FadeOut(m_) for m_ in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ bias & stability
    def bias_stability(self):
        tag = self.chapter("第三部分 · 偏倚与稳定性")
        with self.say("b1") as d:
            self.play(FadeIn(tag), run_time=0.5)
            t = VGroup(T("随机误差", 34, INK), T("样本越多越小", 26, GREEN), T("系统性偏倚", 34, INK), T("样本再多也不消失", 26, RED))
            g = VGroup(VGroup(t[0], t[1]).arrange(DOWN, buff=0.2), VGroup(t[2], t[3]).arrange(DOWN, buff=0.2)).arrange(RIGHT, buff=2.0)
            self.play(FadeIn(g[0]), run_time=0.8)
            self.play(FadeIn(g[1]), run_time=0.8)
        self.play(FadeOut(g), run_time=0.5)
        # study bias: papers -> recorded partners
        rng = np.random.default_rng(4)
        papers = np.array([2, 4, 6, 10, 18, 30, 55, 90])
        partners = np.round(1.2 * papers ** 0.75 + rng.uniform(0, 2, len(papers))).astype(int)
        cx = np.linspace(-4.8, 4.8, len(papers))
        prot = VGroup()
        for x, pp_, pa in zip(cx, papers, partners):
            c = Dot([x, 0.6, 0], radius=0.13, color=BLUE)
            ring_ = VGroup(*[Line([x, 0.6, 0], [x + 0.55 * np.cos(a), 0.6 + 0.55 * np.sin(a), 0], color=BLUE, stroke_width=1.5, stroke_opacity=0.7)
                             for a in np.linspace(0, 2 * PI, pa, endpoint=False)])
            stack = VGroup(*[Rectangle(width=0.36, height=0.04, fill_color=MUTED, fill_opacity=0.8, stroke_width=0) for _ in range(int(np.ceil(pp_ / 3)))]
                           ).arrange(UP, buff=0.03).move_to([x, -1.2, 0], aligned_edge=UP)
            prot.add(VGroup(ring_, c, stack))
        l1 = T("相互作用伙伴", 24, BLUE).move_to([0, 1.7, 0])
        l2 = T("发表的研究", 24, MUTED).move_to([0, -0.85, 0])
        with self.say("b2") as d:
            self.play(FadeIn(l1), FadeIn(l2), LaggedStart(*[FadeIn(p) for p in prot], lag_ratio=0.15), run_time=d * 0.6)
            sk = T("示意", 20, MUTED).to_corner(DR, buff=0.4)
            self.play(FadeIn(sk), run_time=0.3)
        self.play(*[FadeOut(m_) for m_ in self.mobjects if m_ is not tag], run_time=0.6)
        # head motion: near up, far down
        head = Ellipse(width=6.6, height=4.6, color=MUTED, stroke_width=3).move_to([-1.5, -0.3, 0])
        A0, A1, A2 = np.array([-3.6, -0.3, 0]), np.array([-2.7, 0.6, 0]), np.array([0.8, -0.6, 0])
        ds_ = VGroup(*[Dot(p, radius=0.15, color=GOLD) for p in (A0, A1, A2)])
        near = Line(A0, A1, color=GREEN, stroke_width=3); far = Line(A0, A2, color=RED, stroke_width=3)
        lab = VGroup(VGroup(T("近距离相关", 24, GREEN), T("↑", 34, GREEN, weight=BOLD)).arrange(RIGHT, buff=0.15),
                     VGroup(T("远距离相关", 24, RED), T("↓", 34, RED, weight=BOLD)).arrange(RIGHT, buff=0.15)).arrange(DOWN, buff=0.5, aligned_edge=LEFT).move_to([4.6, -0.3, 0])
        with self.say("b3") as d:
            self.play(Create(head), FadeIn(ds_), Create(near), Create(far), run_time=1.0)
            self.play(head.animate.shift(RIGHT * 0.12).rotate(0.04), rate_func=wiggle, run_time=1.0)
            self.play(near.animate.set_stroke(width=8), far.animate.set_stroke(width=1), FadeIn(lab), run_time=1.0)
        self.play(*[FadeOut(m_) for m_ in self.mobjects if m_ is not tag], run_time=0.6)
        with self.say("b3b") as d:
            self.clip_on("yt_motion_tracinnovations.mp4", "center", "视频：TracInnovations · YouTube", start=5)
        self.clip_off()
        # bootstrap edge stability
        rs = np.random.default_rng(8)
        nv, ns = 12, 80
        L = rs.normal(size=(3, ns))
        grp = np.repeat([0, 1, 2], 4)
        X = np.array([0.6 * L[grp[i]] + rs.normal(size=ns) for i in range(nv)])
        thr = 0.25
        iu = np.triu_indices(nv, 1)
        freq = np.zeros(len(iu[0]))
        B = 200
        samples = []
        for b in range(B):
            idx = rs.integers(0, ns, ns)
            C = np.corrcoef(X[:, idx])[iu]
            sel = C > thr
            freq += sel
            if b < 6:
                samples.append(sel)
        freq /= B
        pos = ring(nv, np.array([-2.4, -0.3, 0]), 2.4)
        dots = VGroup(*[Dot(pos[i], radius=0.12, color=SYSC[grp[i]]) for i in range(nv)])
        lines = [Line(pos[int(iu[0][k])], pos[int(iu[1][k])], color=INK, stroke_width=2.5) for k in range(len(iu[0]))]
        for l in lines:
            l.set_stroke(opacity=0)
        bc = counter("重抽样", "第 1 次", INK, vs=32).move_to([4.2, 1.6, 0])
        with self.say("b4") as d:
            self.play(FadeIn(dots), FadeIn(bc), *[FadeIn(l) for l in lines], run_time=0.6)
            for b, sel in enumerate(samples):
                self.play(*[l.animate.set_stroke(opacity=0.8 if s else 0.0) for l, s in zip(lines, sel)],
                          Transform(bc[1], T(f"第 {b + 1} 次", 32, INK, weight=BOLD).move_to(bc[1])), run_time=max(0.35, (d - 1.0) / 6))
        mid = (freq > 0.2) & (freq < 0.8)
        assert mid.sum() >= 3
        with self.say("b5") as d:
            self.play(*[l.animate.set_stroke(GREEN if f >= 0.8 else (GOLD if f > 0.2 else MUTED), opacity=0.9 if f > 0.2 else 0.0, width=3 if f >= 0.8 else 2)
                        for l, f in zip(lines, freq)], FadeOut(bc), run_time=1.2)
            lg = VGroup(VGroup(Line(ORIGIN, RIGHT * 0.5, color=GREEN, stroke_width=4), T("几乎每次都在", 24, INK)).arrange(RIGHT, buff=0.2),
                        VGroup(Line(ORIGIN, RIGHT * 0.5, color=GOLD, stroke_width=4), T("时有时无", 24, INK)).arrange(RIGHT, buff=0.2)
                        ).arrange(DOWN, buff=0.35, aligned_edge=LEFT).move_to([4.2, 0.2, 0])
            self.play(FadeIn(lg), run_time=0.6)
            self.play(*[Indicate(l, color=GOLD) for l, m_ in zip(lines, mid) if m_], run_time=1.0)
        with self.say("b5b") as d:
            self.play(*[l.animate.set_stroke(width=4) for l, m_ in zip(lines, mid) if m_], run_time=1.0)
        self.play(*[FadeOut(m_) for m_ in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ recap
    def recap(self):
        items = [("r2", BLUE, "网络是建模选择的产物：交代清楚"),
                 ("r3", GOLD, "和合适的零模型比，处理多重比较"),
                 ("r4", GREEN, "重抽样、换阈值、换数据检验")]
        head, rows = recap_rows(items)
        with self.say("r1") as d:
            self.play(Write(head), run_time=0.8)
        for (k, _, _), row in zip(items, rows):
            with self.say(k) as d:
                self.play(FadeIn(row, shift=RIGHT * 0.3), run_time=0.8)
        self.wait(1.5)
        self.play(*[FadeOut(m_) for m_ in self.mobjects], run_time=1.0)
