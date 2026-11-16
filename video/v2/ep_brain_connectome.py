"""Animated explainer: 脑连接组 (SC/FC/EC, building networks, thresholds, small world, hubs, rich club)."""
import random

import networkx as nx
import numpy as np

from common import *  # noqa: F401,F403
from bhelp import NetView, fit, counter, axes, legend, heat, recolor_heat, parts_slide, recap_slide, show_clip

TITLE = "脑连接组：结构连接与功能连接"

LINES = {
    # hook
    "h1": "我们先看两个脑区，在安静休息时的活动。右边这两条曲线，是它们的信号随时间的起伏。",
    "h1b": "它们一起起伏，相关系数在零点六左右。相关系数衡量两条曲线同步的程度：一表示完全同步，零表示毫无关系。",
    "h2": "很多人会以为，这两个脑区之间，一定有一根神经纤维直接相连。其实不一定。",
    "h3": "它们可能都在接收第三个脑区的输入，只是被同一个源头带动了。",
    "h4": "所以，脑网络里的一条边意味着什么，网络又是怎样从影像里构建出来的，都需要讲清楚。这一期就来讲这些。",
    "q0": "这一期分三部分来讲。",
    "q1": "第一部分，三种不同的连接，以及怎样从影像构建脑网络。",
    "q2": "第二部分，阈值的陷阱：一个看似技术性的选择，怎样改变结论。",
    "q3": "第三部分，怎样解读脑网络：小世界、枢纽和富人俱乐部。",
    # three connectivities
    "c1": "先看第一部分。在以厘米为单位的脑区尺度上，连接有三种不同的含义。",
    "c2": "结构连接，是解剖上的道路网，也就是脑区之间的白质纤维束。它用弥散磁共振和纤维追踪重建出来，相对稳定。",
    "c2b": "画面是用纤维追踪重建出来的全脑白质纤维。",
    "c3": "功能连接，是两个脑区的信号一起波动的程度，最常用皮尔逊相关。打个比方，它就像两个路口车流量的同步程度。",
    "c3b": "这类信号来自功能磁共振，它记录的是脑区血氧水平随时间的变化。画面是一段介绍功能磁共振的视频。",
    "c4": "下面这条路说明了问题：两个不相邻的路口，可能因为同一条主干道而车流同步，也可能因为都受早高峰驱动。",
    "c5": "有效连接更进一步，问的是谁影响谁，带有方向，需要借助因果模型来估计。",
    "c6": "【慢】所以请记住：功能连接不等于结构连接，更不等于因果。",
    # building
    "b1": "构建脑网络的第一步，是用脑图谱把大脑划分成几十到几百个脑区，作为节点。这里画了二十四个，颜色表示它们大致属于四个区域。",
    "b2": "第二步，估计每对脑区之间的连接强度。在功能网络里，就是两两计算信号的相关。这两条信号算出来的相关，写在下面。",
    "b3": "所有相关排成一张表，就是连接矩阵。第几行第几列，就是第几个脑区和第几个脑区之间的相关。颜色越红，相关越强。",
    "b4": "第三步，决定保留全部权重，还是设一个阈值，变成只有连和不连的二值网络。这里保留相关大于零点三的边。",
    "b4b": "之后，才轮到我们熟悉的网络指标，比如聚集系数、路径长度和模块度。",
    "b5": "【慢】这里的每一步，都是研究者的选择；而每一个选择，都会影响最后的数字。",
    # thresholds
    "t1": "下面进入第二部分，阈值。我们逐步提高阈值，只保留相关大于阈值的边。",
    "t1b": "右边这张图，横轴是阈值。白线是网络密度，也就是实际的边数占所有可能边数的比例；绿线是聚集系数；黄线是全局效率，衡量信息在全网传递得有多快。",
    "t2": "阈值越高，保留的边越少，密度一路下降，聚集系数和全局效率也跟着变。",
    "t3": "【慢】几乎所有网络指标，都随密度变化。这就带来了一个陷阱。",
    "t4": "假设患者组的功能连接整体偏弱一点。用同一个阈值零点三，患者的网络更稀疏，密度从零点三一降到零点二三，全局效率也从零点四六降到零点三七。",
    "t5": "可这个效率降低，可能只是密度降低的副产品，而不是网络组织真的变了。",
    "t6": "比较稳妥的做法，是扫描一段密度范围，比较整条曲线。下面这张图，横轴是密度，纵轴是全局效率。",
    "t6b": "在相同的密度下比较，两组的差别就小多了。另一个办法，是直接分析加权网络。无论用哪种方案，都要在分析之前确定。",
    # small world
    "s1": "最后是第三部分，怎样解读脑网络。大脑既要局部分工，又要全局整合。",
    "s2": "左边是规则的格子网络。聚集系数很高，也就是邻居之间彼此相连的比例高；可平均路径很长，从一个节点到另一个节点要走很多步。",
    "s2b": "右边是完全随机的网络：路径很短，聚集却很低。",
    "s3": "中间这张，只重连了少量的边，就同时得到了较高的聚集和较短的路径。这就是小世界。",
    "s3b": "【慢】人脑网络正好呈现这样的结构：高聚集对应局部分工，短路径对应全局整合。",
    "s4": "衡量整合，常用全局效率。式子的意思是：对所有脑区对，取它们之间距离的倒数，再求平均。",
    "s4b": "断开的脑区对，距离是无穷大，倒数就记为零，不会让平均值发散。",
    # hubs
    "p1": "识别枢纽时，只看连接数并不总是可靠。这里有三个模块，左边是一个大模块。",
    "p2": "黄色这个脑区，有十二条连接，可它的邻居全在同一个大模块里。它只是模块内部的枢纽。",
    "p3": "红色这个脑区，只有六条连接，却均匀地连向三个模块。",
    "p4": "参与系数衡量的正是这一点。式子的意思是：先算每个模块分到它连接的比例，平方后加起来，再用一去减。",
    "p4b": "【慢】连接集中在一个模块，参与系数是零；分得越均匀，越接近上限。黄色是零，红色是零点六七，正好是三个模块时的上限。",
    # rich club
    "r1": "2011年的一项研究发现，人脑结构网络里的枢纽之间，彼此连接得格外紧密，这叫富人俱乐部。中间这六个黄点，代表俱乐部成员。",
    "r2": "成员包括楔前叶、额上回、顶上皮层，以及皮层下的海马、壳核和丘脑。",
    "r3": "判断富人俱乐部，一定要和保持连接数不变的随机网络比较，因为枢纽天然就更容易相连。",
    "r3b": "在这张示意网络里，枢纽之间的连边密度是一，而随机打乱后，平均只有零点五九。",
    "r4": "这些枢纽之间的连接数量不多，却承载了大量最短路径，就像城市之间的高速公路。红线是几条最短路径，都经过俱乐部。",
    "r4b": "统计下来，这张网络里百分之八十三的最短路径，都要经过俱乐部内部的连边。",
    "r5": "代价是，这些长距离连接在布线和代谢上都很昂贵。后续研究据此提出，高代价的枢纽，可能更容易在疾病中受累。",
    # recap
    "z1": "好，我们来总结一下。",
    "z2": "第一，功能连接是统计相关，不是解剖连接，更不是因果。",
    "z3": "第二，图谱和阈值都会改变指标，方案要在分析之前确定。",
    "z4": "第三，判断枢纽要结合参与系数等多种指标，并和合适的随机网络比较。",
    "z5": "这个专题的知识页面里，有画面上的这个交互演示。先拖动保留密度，网络从稀疏慢慢变密。",
    "z5b": "再切换成绝对阈值。同一份数据，换一种阈值方式，得到的网络就不一样了。",
}

N_REG, N_MOD = 24, 4
MODC = [BLUE, GREEN, VIOLET, GOLD]


def sim_fc(seed=1, noise=1.0, T=300):
    rng = np.random.default_rng(seed)
    lat = rng.normal(0, 1, (N_MOD, T)); glob = rng.normal(0, 1, T)
    X = np.zeros((N_REG, T))
    for i in range(N_REG):
        m = i * N_MOD // N_REG
        X[i] = 0.9 * lat[m] + 0.35 * lat[(m + 1) % N_MOD] + 0.4 * glob + noise * rng.normal(0, 1, T)
    return X, np.corrcoef(X)


def binarize(C, th):
    G = nx.Graph(); G.add_nodes_from(range(len(C)))
    G.add_edges_from((i, j) for i in range(len(C)) for j in range(i + 1, len(C)) if C[i, j] > th)
    return G


def smooth_noise(rng, T, w=6):
    return np.convolve(rng.normal(0, 1, T + 3 * w), np.ones(w) / w, "valid")[:T]


def brain_outline(scale=1.0):
    """A simple side-view brain silhouette made of a few arcs."""
    pts = [(-2.9, -0.3), (-2.8, 0.8), (-2.2, 1.7), (-1.0, 2.2), (0.4, 2.25), (1.7, 1.9), (2.7, 1.1), (3.0, 0.0),
           (2.6, -0.9), (1.6, -1.3), (0.9, -1.1), (0.3, -1.6), (-0.6, -1.5), (-1.6, -1.2), (-2.5, -1.0), (-2.9, -0.3)]
    m = VMobject(color=MUTED, stroke_width=3).set_points_smoothly([np.array([x, y, 0]) * scale for x, y in pts])
    return m


def region_pos(center, scale=1.0):
    rng = np.random.default_rng(11)
    lobes = [(-1.7, 0.6), (-0.2, 1.3), (1.4, 0.9), (1.3, -0.4)]
    P = []
    for i in range(N_REG):
        m = i * N_MOD // N_REG
        a = 2 * np.pi * (i % 6) / 6 + 0.3 * m
        r = 0.5 + 0.12 * rng.random()
        P.append(np.array([lobes[m][0] + r * np.cos(a), lobes[m][1] + r * np.sin(a) * 0.8, 0]) * scale + center)
    return P


class Episode(Narrated):
    LINES = LINES

    def construct(self):
        self.hook()
        parts_slide(self, ["一  三种连接与网络构建", "二  阈值的陷阱", "三  解读脑网络：小世界、枢纽、富人俱乐部"])
        self.three()
        self.build()
        self.threshold()
        self.smallworld()
        self.hubs()
        self.richclub()
        self.recap()

    def fade_all(self, rt=0.8, keep=()):
        self.play(*[FadeOut(m) for m in self.mobjects if m not in keep], run_time=rt)

    # ------------------------------------------------------------------ hook
    def hook(self):
        rng = np.random.default_rng(3); Tn = 200
        s = smooth_noise(rng, Tn)
        a = s + 0.75 * smooth_noise(rng, Tn)
        b = s + 0.75 * smooth_noise(rng, Tn)
        r = np.corrcoef(a, b)[0, 1]
        self.hook_r = r
        brain = brain_outline(0.9).move_to(LEFT * 3.6 + UP * 0.2)
        pA, pB, pC = LEFT * 5.0 + UP * 0.6, LEFT * 2.4 + UP * 0.9, LEFT * 3.6 + DOWN * 0.6
        A = Dot(pA, radius=0.16, color=BLUE); B = Dot(pB, radius=0.16, color=GOLD)
        la = T("脑区甲", 22, BLUE).next_to(A, UP, buff=0.12); lb = T("脑区乙", 22, GOLD).next_to(B, UP, buff=0.12)

        def trace(y, y0, c):
            xs = np.linspace(0.2, 6.6, len(y))
            return VMobject(color=c, stroke_width=3).set_points_smoothly([np.array([x, y0 + 0.35 * v, 0]) for x, v in zip(xs, y)][::2])
        ta, tb = trace(a, 1.1, BLUE), trace(b, -1.1, GOLD)
        with self.say("h1") as d:
            self.play(Create(brain), FadeIn(A), FadeIn(B), FadeIn(la), FadeIn(lb), run_time=1.0)
            self.play(Create(ta), Create(tb), run_time=d * 0.55, rate_func=linear)
        with self.say("h1b") as d:
            rl = MathTex(rf"r={r:.2f}", font_size=44, color=INK).move_to(RIGHT * 3.4 + DOWN * 2.6)
            self.play(Write(rl), run_time=0.6)
        with self.say("h2") as d:
            q = DashedLine(pA, pB, color=INK, dash_length=0.1)
            qm = T("纤维？", 26, GOLD).next_to(q, UP, buff=0.05)
            self.play(Create(q), FadeIn(qm), run_time=1.0)
        C = Dot(pC, radius=0.16, color=RED)
        lc = T("脑区丙", 22, RED).next_to(C, DOWN, buff=0.12)
        with self.say("h3") as d:
            self.play(FadeOut(q), FadeOut(qm), FadeIn(C), FadeIn(lc), run_time=0.8)
            arr = VGroup(Arrow(pC, pA, buff=0.2, color=RED, stroke_width=4), Arrow(pC, pB, buff=0.2, color=RED, stroke_width=4))
            self.play(GrowArrow(arr[0]), GrowArrow(arr[1]), run_time=0.8)
            self.play(Flash(C, color=RED), Indicate(A, color=RED), Indicate(B, color=RED), run_time=1.0)
        with self.say("h4") as d:
            qq = T("一条边，可能有不同的含义", 46, GOLD, weight=BOLD).to_edge(DOWN, buff=0.4)
            self.play(*[m.animate.set_stroke(opacity=0.3) for m in (ta, tb)], Write(qq), run_time=1.2)
        self.fade_all()

    # ------------------------------------------------------------------ three kinds
    def three(self):
        tag = self.chapter("一  三种连接")
        cols = [("结构连接", BLUE), ("功能连接", GOLD), ("有效连接", RED)]
        heads = VGroup(*[T(s, 32, c, weight=BOLD) for s, c in cols]).arrange(RIGHT, buff=2.6).to_edge(UP, buff=1.0)
        with self.say("c1") as d:
            self.play(FadeIn(tag), LaggedStart(*[FadeIn(h, shift=DOWN * 0.2) for h in heads], lag_ratio=0.3), run_time=1.4)
        # structural: fibre bundles
        x0 = heads[0].get_center()[0]
        fibers = VGroup(*[ArcBetweenPoints(np.array([x0 - 1.6, y, 0]), np.array([x0 + 1.6, y + 0.3, 0]), angle=-0.6 + 0.12 * k,
                                           color=BLUE, stroke_width=2.5, stroke_opacity=0.8) for k, y in enumerate(np.linspace(-0.6, 0.6, 7))])
        ends = VGroup(Dot([x0 - 1.6, 0, 0], radius=0.18, color=BLUE), Dot([x0 + 1.6, 0.3, 0], radius=0.18, color=BLUE))
        with self.say("c2") as d:
            self.play(FadeIn(ends), LaggedStart(*[Create(f) for f in fibers], lag_ratio=0.1), run_time=d * 0.5)
            self.play(FadeIn(T("弥散磁共振 + 纤维追踪", 20, MUTED).next_to(VGroup(fibers, ends), DOWN, buff=0.5)), run_time=0.6)
        keep = list(self.mobjects)
        show_clip(self, "c2b", "yt_tractography_exploredti.mp4", "center", "视频：ExploreDTI · YouTube", start=0, min_len=6)
        self.play(*[FadeIn(m) for m in keep], run_time=0.6)
        # functional: two traffic counters
        x1 = heads[1].get_center()[0]
        rng = np.random.default_rng(5)
        s = smooth_noise(rng, 120)
        y1, y2 = s + 0.5 * smooth_noise(rng, 120), s + 0.5 * smooth_noise(rng, 120)
        tr = VGroup(*[VMobject(color=GOLD, stroke_width=2.5).set_points_smoothly(
            [np.array([x1 - 1.6 + 3.2 * i / 119, y0 + 0.3 * v, 0]) for i, v in enumerate(yy)][::2]) for yy, y0 in ((y1, 0.6), (y2, -0.5))])
        with self.say("c3") as d:
            self.play(Create(tr[0]), Create(tr[1]), run_time=d * 0.5, rate_func=linear)
            self.play(FadeIn(T("皮尔逊相关", 20, MUTED).next_to(tr, DOWN, buff=0.5)), run_time=0.6)
        keep = list(self.mobjects)
        show_clip(self, "c3b", "yt_fmri_wellcome.mp4", "center", "视频：Wellcome Centre for Human Neuroimaging · YouTube", start=40, min_len=7)
        self.play(*[FadeIn(m) for m in keep], run_time=0.6)
        # city analogy below
        with self.say("c4") as d:
            road = Line(LEFT * 5.5, RIGHT * 5.5, color=MUTED, stroke_width=10).shift(DOWN * 2.6)
            i1, i2 = Dot(LEFT * 2.0 + DOWN * 2.6, radius=0.18, color=GOLD), Dot(RIGHT * 2.0 + DOWN * 2.6, radius=0.18, color=GOLD)
            cars = VGroup(*[Rectangle(width=0.3, height=0.14, fill_color=INK, fill_opacity=1, stroke_width=0).move_to(LEFT * (5.5 - 0.7 * k) + DOWN * 2.6) for k in range(6)])
            self.play(FadeIn(road), FadeIn(i1), FadeIn(i2), FadeIn(cars), run_time=0.8)
            self.play(cars.animate.shift(RIGHT * 6.5), Indicate(i1, color=GOLD), Indicate(i2, color=GOLD), run_time=d * 0.5, rate_func=linear)
            rush = T("早高峰", 22, RED).next_to(road, UP, buff=0.15)
            self.play(FadeIn(rush), run_time=0.5)
        x2 = heads[2].get_center()[0]
        e1, e2 = Dot([x2 - 1.2, 0, 0], radius=0.2, color=RED), Dot([x2 + 1.2, 0, 0], radius=0.2, color=RED)
        ea = Arrow(e1.get_center(), e2.get_center(), buff=0.25, color=RED, stroke_width=6)
        with self.say("c5") as d:
            self.play(FadeIn(e1), FadeIn(e2), GrowArrow(ea), run_time=1.0)
            self.play(FadeIn(T("因果模型", 20, MUTED).next_to(VGroup(e1, e2), DOWN, buff=0.6)), run_time=0.6)
        with self.say("c6") as d:
            f = VGroup(T("功能连接", 34, GOLD), MathTex(r"\neq", font_size=48), T("结构连接", 34, BLUE), MathTex(r"\neq", font_size=48), T("因果", 34, RED)).arrange(RIGHT, buff=0.3)
            self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.6)
            self.play(Write(f), run_time=1.4)
        self.fade_all()

    # ------------------------------------------------------------------ building
    def build(self):
        tag = self.chapter("一  从影像到网络")
        brain = brain_outline(1.0).move_to(LEFT * 3.4 + UP * 0.3)
        P = region_pos(brain.get_center() + LEFT * 0.0, 1.0)
        dots = VGroup(*[Dot(p, radius=0.11, color=MODC[i * N_MOD // N_REG]) for i, p in enumerate(P)])
        with self.say("b1") as d:
            self.play(FadeIn(tag), Create(brain), run_time=1.0)
            self.play(LaggedStart(*[GrowFromCenter(x) for x in dots], lag_ratio=0.05), run_time=d * 0.5)
        X, C = sim_fc()
        self.C = C
        # two time series pulled out
        i, j = 1, 9
        xs = np.linspace(0.6, 6.4, 120)
        ts = VGroup(*[VMobject(color=c, stroke_width=2.5).set_points_smoothly([np.array([x, y0 + 0.22 * v, 0]) for x, v in zip(xs, X[k][:120])][::2])
                      for k, c, y0 in ((i, MODC[0], 1.2), (j, MODC[1], -0.4))])
        with self.say("b2") as d:
            self.play(Indicate(dots[i], scale_factor=2), Indicate(dots[j], scale_factor=2), run_time=0.8)
            self.play(Create(ts[0]), Create(ts[1]), run_time=d * 0.45, rate_func=linear)
            rv = MathTex(rf"r={C[i, j]:.2f}", font_size=40).move_to(RIGHT * 3.5 + DOWN * 1.6)
            self.play(Write(rv), run_time=0.6)
        hm = heat(C, side=4.2, lo=-0.2, hi=1.0).move_to(RIGHT * 3.4 + DOWN * 0.1)
        with self.say("b3") as d:
            self.play(FadeOut(ts), FadeOut(rv), run_time=0.5)
            self.play(FadeIn(hm[0], lag_ratio=0.002), Create(hm[1]), run_time=d * 0.5)
            cell = Square(hm[0][0].width, color=INK, stroke_width=3).move_to(hm[0][i * N_REG + j])
            self.play(Create(cell), run_time=0.5)
        G = binarize(C, 0.3)
        edges = VGroup(*[Line(P[u], P[v], stroke_width=1.5, color=INK, stroke_opacity=0.4) for u, v in G.edges()])
        with self.say("b4") as d:
            self.play(FadeOut(cell), run_time=0.3)
            self.play(*recolor_heat(hm, (C > 0.3).astype(float) * 0.9, lo=-0.2, hi=1.0), run_time=1.2)
            self.play(Create(edges), run_time=1.2)
        with self.say("b4b") as d:
            mt = VGroup(T("聚集系数", 22, MUTED), T("路径长度", 22, MUTED), T("模块度", 22, MUTED)).arrange(RIGHT, buff=0.5).next_to(hm, DOWN, buff=0.35)
            self.play(FadeIn(mt, lag_ratio=0.3), run_time=0.9)
        with self.say("b5") as d:
            steps = VGroup(*[T(s, 26, GOLD) for s in ("图谱", "→", "连接强度", "→", "阈值", "→", "指标")]).arrange(RIGHT, buff=0.25).to_edge(DOWN, buff=0.3)
            self.play(FadeOut(mt), FadeIn(steps, lag_ratio=0.15), run_time=1.4)
        self.brain_P = P
        self.fade_all()

    # ------------------------------------------------------------------ threshold trap
    def threshold(self):
        tag = self.chapter("二  阈值的陷阱")
        C = self.C
        P = [p + RIGHT * 0.2 for p in region_pos(LEFT * 3.6 + UP * 0.3, 1.0)]
        brain = brain_outline(1.0).move_to(LEFT * 3.6 + UP * 0.3)
        dots = VGroup(*[Dot(p, radius=0.1, color=MODC[i * N_MOD // N_REG]) for i, p in enumerate(P)])
        ths = np.round(np.arange(0.05, 0.61, 0.05), 2)
        dens, clus, eff = [], [], []
        for th in ths:
            G = binarize(C, th)
            dens.append(nx.density(G)); clus.append(nx.average_clustering(G)); eff.append(nx.global_efficiency(G))
        ax = axes([0, 0.6, 0.1], [0, 1, 0.5], 5.4, 3.8, xn=[0, 0.2, 0.4, 0.6], yn=[0, 0.5, 1]).move_to(RIGHT * 3.4 + DOWN * 0.4)
        xl = T("阈值", 22, MUTED).next_to(ax.x_axis, DOWN, buff=0.35)
        lg = legend([(INK, "密度"), (GREEN, "聚集系数"), (GOLD, "全局效率")], 20).next_to(ax, UP, buff=0.25)
        tv = ValueTracker(0.05)

        def edges_for(th):
            G = binarize(C, th)
            return VGroup(*[Line(P[u], P[v], stroke_width=1.3, color=INK, stroke_opacity=0.35) for u, v in G.edges()])
        ed = always_redraw(lambda: edges_for(tv.get_value()))
        thl = always_redraw(lambda: VGroup(T("阈值", 24, MUTED), DecimalNumber(tv.get_value(), num_decimal_places=2, font_size=34, color=INK)).arrange(RIGHT, buff=0.2).move_to(LEFT * 3.4 + DOWN * 2.8))
        with self.say("t1") as d:
            self.play(FadeIn(tag), FadeIn(brain), FadeIn(dots), run_time=0.8)
            self.add(ed, thl)
        with self.say("t1b") as d:
            self.play(Create(ax), FadeIn(xl), run_time=1.0)
            self.play(FadeIn(lg, lag_ratio=0.5), run_time=d * 0.5)
        cd = ax.plot_line_graph(ths, dens, line_color=INK, add_vertex_dots=False, stroke_width=4)
        cc = ax.plot_line_graph(ths, clus, line_color=GREEN, add_vertex_dots=False, stroke_width=4)
        ce = ax.plot_line_graph(ths, eff, line_color=GOLD, add_vertex_dots=False, stroke_width=4)
        with self.say("t2") as d:
            self.play(tv.animate.set_value(0.6), Create(cd), Create(cc), Create(ce), run_time=d * 0.85, rate_func=linear)
        with self.say("t3") as d:
            self.play(tv.animate.set_value(0.3), run_time=1.2)
            vl = DashedLine(ax.c2p(0.3, 0), ax.c2p(0.3, 1), color=RED)
            self.play(Create(vl), run_time=0.6)
        self.remove(ed, thl)
        self.fade_all(keep=(tag,))
        # patients vs controls at the same threshold
        _, Cp = sim_fc(seed=1, noise=1.3)
        Gc, Gp = binarize(C, 0.3), binarize(Cp, 0.3)
        Pl = [p + RIGHT * 0.0 for p in region_pos(LEFT * 3.6 + UP * 0.6, 0.95)]
        Pr = [p for p in region_pos(RIGHT * 3.0 + UP * 0.6, 0.95)]

        def draw(G, Pp, col):
            return VGroup(brain_outline(0.95).move_to(np.mean(Pp, axis=0) + LEFT * 0.0),
                          VGroup(*[Line(Pp[u], Pp[v], stroke_width=1.3, color=col, stroke_opacity=0.45) for u, v in G.edges()]),
                          VGroup(*[Dot(p, radius=0.08, color=col) for p in Pp]))
        nc, npat = draw(Gc, Pl, BLUE), draw(Gp, Pr, RED)
        lc = T("对照组", 28, BLUE).next_to(nc, UP, buff=0.2)
        lp = T("患者组", 28, RED).next_to(npat, UP, buff=0.2)
        stats = [(nx.density(G), nx.global_efficiency(G)) for G in (Gc, Gp)]
        self.trap_vals = stats
        with self.say("t4") as d:
            self.play(FadeIn(nc), FadeIn(lc), run_time=1.0)
            self.play(FadeIn(npat), FadeIn(lp), run_time=1.0)
            k1 = VGroup(counter("密度", f"{stats[0][0]:.2f}", BLUE, vs=32), counter("全局效率", f"{stats[0][1]:.2f}", BLUE, vs=32)).arrange(RIGHT, buff=0.6).next_to(nc, DOWN, buff=0.4)
            k2 = VGroup(counter("密度", f"{stats[1][0]:.2f}", RED, vs=32), counter("全局效率", f"{stats[1][1]:.2f}", RED, vs=32)).arrange(RIGHT, buff=0.6).next_to(npat, DOWN, buff=0.4)
            self.play(FadeIn(k1), FadeIn(k2), run_time=1.0)
        with self.say("t5") as d:
            self.play(Indicate(k2[0], color=RED, scale_factor=1.3), run_time=1.0)
            arr = Arrow(k2[0].get_right(), k2[1].get_left(), buff=0.05, color=GOLD, stroke_width=4)
            self.play(GrowArrow(arr), Indicate(k2[1], color=RED, scale_factor=1.3), run_time=1.0)
        self.fade_all(keep=(tag,))
        with self.say("t6") as d:
            ax2 = axes([0, 0.5, 0.1], [0, 1, 0.5], 7.0, 3.6, xn=[0.1, 0.2, 0.3, 0.4], yn=[0, 0.5, 1]).shift(DOWN * 0.3)
            xl2 = T("网络密度", 22, MUTED).next_to(ax2.x_axis, DOWN, buff=0.35)
            ds = np.linspace(0.05, 0.4, 8)

            def eff_at(Cm, dd):
                iu = np.triu_indices(N_REG, 1); v = np.sort(Cm[iu])[::-1]; k = int(dd * len(v))
                return nx.global_efficiency(binarize(Cm, v[k - 1] - 1e-9))
            band = ax2.get_area(ax2.plot(lambda x: 1, x_range=[0.05, 0.4]), x_range=[0.05, 0.4], color=GOLD, opacity=0.12)
            c1 = ax2.plot_line_graph(ds, [eff_at(C, x) for x in ds], line_color=BLUE, add_vertex_dots=False, stroke_width=4)
            c2 = ax2.plot_line_graph(ds, [eff_at(Cp, x) for x in ds], line_color=RED, add_vertex_dots=False, stroke_width=4)
            lg2 = legend([(BLUE, "对照组"), (RED, "患者组")], 20).next_to(ax2, RIGHT, buff=0.3)
            yl2 = T("全局效率", 22, MUTED).rotate(PI / 2).next_to(ax2.y_axis, LEFT, buff=0.3)
            self.play(Create(ax2), FadeIn(xl2), FadeIn(yl2), FadeIn(band), FadeIn(lg2), run_time=1.0)
            self.wait(0.1)
        with self.say("t6b") as d:
            self.play(Create(c1), Create(c2), run_time=d * 0.5)
        self.fade_all()

    # ------------------------------------------------------------------ small world
    def smallworld(self):
        tag = self.chapter("三  解读：分离与整合")
        n = 36
        nets = [nx.watts_strogatz_graph(n, 6, 0.0), nx.connected_watts_strogatz_graph(n, 6, 0.05, seed=1),
                nx.connected_watts_strogatz_graph(n, 6, 1.0, seed=3)]
        titles = ["规则", "小世界", "随机"]
        xs = [-4.5, 0, 4.5]
        groups = []
        for G, x, t in zip(nets, xs, titles):
            pos = {i: np.array([x + 1.6 * np.cos(2 * np.pi * i / n + PI / 2), 0.4 + 1.6 * np.sin(2 * np.pi * i / n + PI / 2), 0]) for i in range(n)}
            g = VGroup(VGroup(*[Line(pos[u], pos[v], stroke_width=1.2, color=BLUE, stroke_opacity=0.5) for u, v in G.edges()]),
                       VGroup(*[Dot(pos[i], radius=0.07, color=BLUE) for i in range(n)]))
            lab = T(t, 28).move_to([x, 2.6, 0])
            cs = VGroup(counter("聚集系数", f"{nx.average_clustering(G):.2f}", GREEN, vs=30),
                        counter("平均路径", f"{nx.average_shortest_path_length(G):.1f}", GOLD, vs=30)).arrange(RIGHT, buff=0.4).move_to([x, -2.3, 0])
            groups.append((g, lab, cs))
        self.sw_vals = [(nx.average_clustering(G), nx.average_shortest_path_length(G)) for G in nets]
        with self.say("s1") as d:
            self.play(FadeIn(tag), run_time=0.5)
            self.play(FadeIn(groups[1][0]), FadeIn(groups[1][1]), run_time=1.2)
        with self.say("s2") as d:
            self.play(FadeIn(groups[0][0]), FadeIn(groups[0][1]), FadeIn(groups[0][2]), run_time=1.2)
        with self.say("s2b") as d:
            self.play(FadeIn(groups[2][0]), FadeIn(groups[2][1]), FadeIn(groups[2][2]), run_time=1.2)
        with self.say("s3") as d:
            self.play(FadeIn(groups[1][2]), run_time=1.0)
        with self.say("s3b") as d:
            self.play(Indicate(groups[1][2], color=GOLD), run_time=1.2)
        with self.say("s4") as d:
            self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.6)
            f = MathTex(r"E_{\text{glob}}=\frac{1}{N(N-1)}\sum_{i\neq j}\frac{1}{d_{ij}}", font_size=60)
            self.play(Write(f), run_time=1.6)
            fl = VGroup(T("所有脑区对", 22, MUTED).next_to(f, DOWN, buff=0.3).shift(LEFT * 0.4),
                        T("距离的倒数", 22, GOLD).next_to(f, RIGHT, buff=0.3))
            self.play(FadeIn(fl), run_time=0.8)
        with self.say("s4b") as d:
            note = MathTex(r"d_{ij}=\infty\ \Rightarrow\ \frac{1}{d_{ij}}=0", font_size=40, color=GOLD).next_to(f, DOWN, buff=1.0)
            self.play(FadeIn(note), run_time=0.8)
        self.fade_all()

    # ------------------------------------------------------------------ hubs: participation coefficient
    def hubs(self):
        tag = self.chapter("三  解读：谁是枢纽")
        G = nx.Graph(); mod = {}
        sizes = [12, 6, 6]
        centers = [np.array([-3.0, 0.2, 0]), np.array([2.2, 1.6, 0]), np.array([2.2, -1.8, 0])]
        pos = {}
        idx = 0; members = []
        for m, (s, c) in enumerate(zip(sizes, centers)):
            ms = []
            for k in range(s):
                a = 2 * np.pi * k / s
                rr = 1.9 if m == 0 else 1.0
                pos[idx] = c + rr * np.array([np.cos(a), np.sin(a) * (0.8 if m == 0 else 1), 0]); mod[idx] = m; ms.append(idx); idx += 1
            members.append(ms)
        r = random.Random(2)
        for ms in members:
            for i in ms:
                for j in ms:
                    if i < j and r.random() < 0.35:
                        G.add_edge(i, j)
        hubA = idx; pos[hubA] = centers[0]; mod[hubA] = 0
        for j in members[0]:
            G.add_edge(hubA, j)
        hubB = idx + 1; pos[hubB] = np.array([-0.1, -0.2, 0]); mod[hubB] = 0
        for j in members[0][:2] + members[1][:2] + members[2][:2]:
            G.add_edge(hubB, j)
        cols = {0: BLUE, 1: GREEN, 2: VIOLET}
        dots = {v: Dot(pos[v], radius=0.09, color=cols[mod[v]]) for v in G}
        dots[hubA].scale(1.8); dots[hubB].scale(1.5)
        lines = {e: Line(pos[e[0]], pos[e[1]], stroke_width=1.3, color=MUTED, stroke_opacity=0.35) for e in G.edges()}

        def P(v):
            k = G.degree(v)
            return 1 - sum((sum(1 for w in G.neighbors(v) if mod[w] == s) / k) ** 2 for s in range(3))
        self.pc = (G.degree(hubA), P(hubA), G.degree(hubB), P(hubB))
        with self.say("p1") as d:
            self.play(FadeIn(tag), *[Create(l) for l in lines.values()], *[FadeIn(x) for x in dots.values()], run_time=1.4)
        with self.say("p2") as d:
            es = [l for e, l in lines.items() if hubA in e]
            self.play(*[l.animate.set_stroke(GOLD, width=3, opacity=1) for l in es], dots[hubA].animate.set_color(GOLD), run_time=1.0)
            ca = VGroup(counter("度", str(G.degree(hubA)), GOLD, vs=30), counter("参与系数", f"{P(hubA):.2f}", GOLD, vs=30)).arrange(RIGHT, buff=0.4).move_to(LEFT * 3.0 + DOWN * 2.9)
            self.play(FadeIn(ca[0]), run_time=0.6)
        with self.say("p3") as d:
            es = [l for e, l in lines.items() if hubB in e]
            self.play(*[l.animate.set_stroke(RED, width=3, opacity=1) for l in es], dots[hubB].animate.set_color(RED), run_time=1.0)
            cb = VGroup(counter("度", str(G.degree(hubB)), RED, vs=30), counter("参与系数", f"{P(hubB):.2f}", RED, vs=30)).arrange(RIGHT, buff=0.4).move_to(RIGHT * 4.6 + DOWN * 0.1)
            self.play(FadeIn(cb[0]), run_time=0.6)
        with self.say("p4") as d:
            f = MathTex(r"P_i=1-\sum_{s}\left(\frac{k_{is}}{k_i}\right)^2", font_size=44).to_edge(UP, buff=0.5).shift(RIGHT * 2.0)
            self.play(Write(f), run_time=1.4)
        with self.say("p4b") as d:
            self.play(FadeIn(ca[1]), FadeIn(cb[1]), run_time=0.8)
        self.fade_all()

    # ------------------------------------------------------------------ rich club
    def richclub(self):
        tag = self.chapter("三  解读：富人俱乐部")
        names = ["楔前叶", "额上回", "顶上皮层", "海马", "壳核", "丘脑"]
        h = len(names)
        G = nx.Graph()
        hp = {i: np.array([1.5 * np.cos(2 * np.pi * i / h + PI / 2), 1.3 * np.sin(2 * np.pi * i / h + PI / 2), 0]) + DOWN * 0.2 for i in range(h)}
        G.add_edges_from((i, j) for i in range(h) for j in range(i + 1, h))
        pos = dict(hp)
        r = random.Random(4)
        n_per = 7
        idx = h
        for i in range(h):
            base = 2 * np.pi * i / h + PI / 2
            local = []
            for k in range(n_per):
                a = base + (k - (n_per - 1) / 2) * 0.13
                pos[idx] = np.array([3.4 * np.cos(a) * 1.55, 2.9 * np.sin(a) * 1.0, 0]) * 0.92 + DOWN * 0.2
                G.add_edge(i, idx); local.append(idx); idx += 1
            for a_, b_ in zip(local, local[1:]):
                G.add_edge(a_, b_)
        # a few local cross links between neighbouring groups
        for i in range(h):
            G.add_edge(h + i * n_per + n_per - 1, h + ((i + 1) % h) * n_per)
        club = set(range(h))
        dots = {v: Dot(pos[v], radius=0.16 if v in club else 0.07, color=GOLD if v in club else BLUE) for v in G}
        lines = {e: Line(pos[e[0]], pos[e[1]], stroke_width=3 if (e[0] in club and e[1] in club) else 1.2,
                         color=GOLD if (e[0] in club and e[1] in club) else MUTED, stroke_opacity=0.9 if (e[0] in club and e[1] in club) else 0.4)
                 for e in G.edges()}
        labs = VGroup(*[T(names[i], 20, GOLD).next_to(dots[i], (hp[i] - DOWN * 0.2) / (np.linalg.norm(hp[i] - DOWN * 0.2) + 1e-9) * 0 + UP, buff=0.12) for i in range(h)])
        with self.say("r1") as d:
            self.play(FadeIn(tag), *[Create(l) for e, l in lines.items() if not (e[0] in club and e[1] in club)],
                      *[FadeIn(dots[v]) for v in G], run_time=1.4)
            self.play(*[Create(l) for e, l in lines.items() if e[0] in club and e[1] in club], run_time=1.2)
        with self.say("r2") as d:
            self.play(LaggedStart(*[FadeIn(l) for l in labs], lag_ratio=0.25), run_time=d * 0.6)
        # normalized rich club coefficient vs a degree-preserving null
        k = 7
        def phi(Gx):
            S = [v for v in Gx if Gx.degree(v) > k]
            if len(S) < 2:
                return 0.0
            return 2 * Gx.subgraph(S).number_of_edges() / (len(S) * (len(S) - 1))
        ph = phi(G)
        nulls = []
        for s in range(20):
            Hn = G.copy()
            nx.double_edge_swap(Hn, nswap=4 * Hn.number_of_edges(), max_tries=10 ** 5, seed=s)
            nulls.append(phi(Hn))
        self.rc = (ph, np.mean(nulls))
        with self.say("r3") as d:
            self.play(labs.animate.set_opacity(0.3), run_time=0.4)
            c1 = counter("枢纽之间的连边密度", f"{ph:.2f}", GOLD, vs=32)
            c2 = counter("保度随机网络", f"{np.mean(nulls):.2f}", MUTED, vs=32)
            VGroup(c1, c2).arrange(DOWN, buff=0.4).to_corner(UR, buff=0.4)
        with self.say("r3b") as d:
            self.play(FadeIn(c1), run_time=0.8)
            self.play(FadeIn(c2), run_time=0.8)
        # share of shortest paths using a club-club edge
        per = [v for v in G if v not in club]
        tot = use = 0
        for i_, a_ in enumerate(per):
            for b_ in per[i_ + 1:]:
                p = nx.shortest_path(G, a_, b_)
                tot += 1
                use += any(p[t] in club and p[t + 1] in club for t in range(len(p) - 1))
        share = use / tot
        self.rc_share = share
        with self.say("r4") as d:
            pr = [(h + 3, h + 4 * n_per + 3), (h + 1 * n_per + 5, h + 3 * n_per + 2), (h + 5 * n_per + 1, h + 2 * n_per + 4)]
            for a_, b_ in pr:
                p = nx.shortest_path(G, a_, b_)
                path = VMobject(color=RED, stroke_width=5).set_points_as_corners([pos[x] for x in p])
                self.play(Create(path), run_time=0.8)
                self.play(FadeOut(path), run_time=0.3)
        with self.say("r4b") as d:
            c3 = counter("经过俱乐部连边的最短路径", f"{share * 100:.0f}%", RED, vs=32).to_corner(DR, buff=0.4)
            self.play(FadeIn(c3), run_time=0.8)
        with self.say("r5") as d:
            self.play(*[l.animate.set_stroke(RED) for e, l in lines.items() if e[0] in club and e[1] in club], run_time=1.0)
            self.play(*[dots[v].animate.set_color(RED) for v in club], run_time=0.8)
        self.fade_all()

    # ------------------------------------------------------------------ recap
    def recap(self):
        recap_slide(self, ["功能连接 ≠ 结构连接 ≠ 因果", "图谱和阈值会改变指标，事先确定方案", "枢纽：参与系数 + 合适的随机网络比较"])
        with self.say("z5") as d:
            self.clip_on("threshold_demo.mp4", "full", "本站交互演示：脑网络阈值敏感性", start=0.3)
        with self.say("z5b") as d:
            pass
        self.clip_off()
        self.wait(1.0)
