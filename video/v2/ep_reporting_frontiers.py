"""Animated explainer: 结果呈现与研究前沿 (figures, network plots, degree plots, higher-order, temporal, GNN, causality)."""
import random

import networkx as nx
import numpy as np

from common import *  # noqa: F401,F403
from kit_c import NetView, arrow, axes, chip, clip_line, counter, fade_all, fit, grow_bars, hist_bars, parts, xlabel, ylabel

TITLE = "把结果讲清楚：图表呈现与网络科学前沿"

LINES = {
    # hook
    "h1": "这是一张有八百个节点的网络图，学术报告里经常能见到这样的图。",
    "h2": "密密麻麻一团毛线，看不出模块，也看不出枢纽。",
    "h3": "同样的数据，把节点按社团排序，画成邻接矩阵：行和列都是节点，有边的格子点亮。对角线上，一个个方块就出来了。",
    "h4": "【慢】同一份结果，换一种画法，信息量天差地别。",
    "h5": "这一期，我们谈怎样可信地呈现结果，再看看网络方法正在往哪里走。",
    "o0": "这一期分三部分。",
    "o1": "第一部分，结果图和网络图怎样画。",
    "o2": "第二部分，三个前沿方向：高阶相互作用、时间网络和图神经网络。",
    "o3": "第三部分，模型的解释和因果证据。",
    # a good figure
    "g0": "先看第一部分。无论写论文还是做报告，结果最后都要变成图，讲给别人听。",
    "g1": "第一个原则：每张图回答一个问题，图的标题直接写结论。",
    "g2": "第二个原则：指标不能单独给。比如这张网络的平均聚集系数是零点四二。聚集系数，衡量一个节点的邻居之间彼此相连的程度。",
    "g2b": "单看这个数，看不出它是高还是低。",
    "g3": "加上参照：灰色柱子是保度随机网络的聚集系数，挤在最左边；黄线是真实值。",
    "g4": "再标出不确定性，比如Z分数。这里大约是九十七，远远超出随机波动。",
    "g4b": "【慢】一张好的结果图，至少有三样东西：观测值、参照、不确定性。",
    # network plots
    "n1": "网络图也有陷阱。力导向布局依赖随机初值，两组各画一次，同一个节点位置不同，读者没法对照。",
    "n2": "办法是固定种子、保存坐标，两组用同一套位置。",
    "n3": "布局里挨得近，不代表连接多。左边两个模块挨着，之间零条边；右边那个离得远，却有四条。",
    "n3b": "【慢】图上看到的结构，要靠定量分析来支持。",
    "n4": "颜色也要小心：连续变量用感知均匀的渐变，避免彩虹色，也不要只靠红绿区分。",
    # degree plots
    "d1": "度分布怎么画。左图是线性分箱的直方图，横轴是度，纵轴是节点数。尾部只剩零星几根柱子，噪声很大。",
    "d2": "右图是互补累积分布：纵轴是度不小于k的节点所占的比例，两个轴都取对数。尾部平滑多了。",
    "d3": "不过，双对数图上像一条直线，并不能证明就是幂律。",
    # higher-order
    "o1b": "下面进入第二部分。第一个前沿方向，是高阶相互作用。普通网络只表示两两关系。",
    "o2b": "可是，三个蛋白组成一个复合物，和三对蛋白各自两两结合，投影成网络，都是同一个三角形。",
    "o3b": "超图和单纯复形，能把三者同时作用表示成一个整体，比如一个实心的三角形。",
    "o4b": "这会改变动力学。有研究发现，三体感染率足够大时，流行病的爆发会从连续变化变成突然跳变。画面是示意图。",
    # temporal
    "t0": "第二个方向是时间网络。现实中的接触，是随时间出现又消失的。",
    "t1": "看一个例子：甲在时刻一接触乙，乙在时刻二接触丙。",
    "t2": "信息可以从甲传到丙。但从丙出发，到乙时已经是时刻二，甲乙那条边早就过去了，所以传不回甲。",
    "t3": "【慢】把接触聚合成静态网络，三个人看起来彼此可达，传播范围就被高估了。",
    # GNN
    "x0": "第三个方向是图神经网络，一类专门处理网络数据的机器学习模型。",
    "x1": "它的基本操作叫消息传递：每个节点从邻居那里收集信息，更新自己的表示。",
    "x2": "每多一层，节点就多看到一步邻域：蓝色是第一层能看到的，绿色是第二层。",
    "x3": "可层数一多，各节点的表示越来越像。右图横轴是层数，纵轴是节点之间的差异，降得很快，这叫过平滑。所以一般只用两到三层。",
    "x4": "评估也要小心：按边随机划分训练集和测试集，相似的药物可能已在训练集里，性能会被高估。还要和简单方法比较。",
    # causality
    "y1": "最后是第三部分。模型找出它依赖的子图，只说明模型学到了什么，那可能来自数据偏倚，而不是生物机制。",
    "y2": "相关、偏相关、共表达网络的边，都不能直接告诉我们，干预一个节点会发生什么。",
    "y3": "【慢】最直接的因果证据，来自干预实验：基因敲除、基因扰动、药物处理、脑刺激。",
    # recap
    "r1": "好，我们总结一下。",
    "r2": "第一，每张结果图都要同时给出观测值、参照和不确定性。",
    "r3": "第二，网络图要固定布局，结论来自定量分析，而不是图上的样子。",
    "r4": "第三，方法再新，节点和边怎样定义、和什么比较，这些老问题依然存在。",
}


def density_image(A, order, bins=160, color=(255, 194, 75)):
    n = len(order)
    B = A[np.ix_(order, order)]
    k = n // bins
    D = B[: k * bins, : k * bins].reshape(bins, k, bins, k).sum((1, 3)) / (k * k)
    D = np.clip(D / max(D.max() * 0.5, 1e-9), 0, 1) ** 0.6
    bg = np.array([16, 21, 31], float); fg = np.array(color, float)
    img = (bg[None, None, :] * (1 - D[..., None]) + fg[None, None, :] * D[..., None]).astype(np.uint8)
    im = ImageMobject(img)
    im.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
    return im


class Episode(Narrated):
    LINES = LINES

    def construct(self):
        self.hook()
        self.parts_slide()
        self.good_figure()
        self.network_plots()
        self.degree_plots()
        self.higher_order()
        self.temporal()
        self.gnn()
        self.causality()
        self.recap()

    # ------------------------------------------------------------------ hook
    def hook(self):
        sizes = [100] * 8
        G = nx.random_partition_graph(sizes, 0.06, 0.006, seed=3)
        n = G.number_of_nodes()
        pos = fit(nx.spring_layout(G, seed=1, iterations=12), (-6.4, 0.4, -3.4, 3.4))
        lines = VGroup(*[Line(pos[u], pos[v], stroke_width=0.6, color=BLUE, stroke_opacity=0.25) for u, v in G.edges()])
        dots = VGroup(*[Dot(pos[v], radius=0.025, color=BLUE) for v in G])
        with self.say("h1") as d:
            self.play(FadeIn(dots, lag_ratio=0.001), run_time=1.0)
            self.play(Create(lines, lag_ratio=0.0005), run_time=d * 0.5)
            c = counter("节点", str(n), INK).move_to(RIGHT * 4.0 + UP * 2.0)
            self.play(FadeIn(c), run_time=0.5)
        with self.say("h2") as d:
            q = T("看不出模块和枢纽", 36, MUTED, weight=BOLD).move_to(RIGHT * 4.0 + DOWN * 0.2)
            self.play(Write(q), run_time=1.0)
        A = nx.to_numpy_array(G, nodelist=range(n))
        rng = np.random.default_rng(2)
        perm = rng.permutation(n)
        part = G.graph["partition"]
        order = [v for blk in part for v in sorted(blk)]
        im0 = density_image(A, perm).set_height(5.4).move_to(RIGHT * 3.6 + DOWN * 0.2)
        im1 = density_image(A, order).set_height(5.4).move_to(im0)
        fr = SurroundingRectangle(im0, color=MUTED, buff=0.02, stroke_width=1.5)
        with self.say("h3") as d:
            self.play(FadeOut(q), FadeOut(c), run_time=0.4)
            self.play(FadeIn(im0), Create(fr), run_time=1.0)
            lab = T("按社团排序", 24, GOLD).next_to(fr, UP, buff=0.15)
            self.play(FadeIn(lab), run_time=0.4)
            self.play(FadeOut(im0), FadeIn(im1), run_time=1.6)
        with self.say("h4") as d:
            self.play(VGroup(dots, lines).animate.fade(0.8), run_time=0.8)
            q2 = T("画法决定了你能看到什么", 34, GOLD, weight=BOLD).move_to(LEFT * 3.0)
            self.play(Write(q2), run_time=1.2)
        with self.say("h5") as d:
            self.play(Indicate(q2, color=GOLD), run_time=1.0)
        fade_all(self)

    def parts_slide(self):
        parts(self, "这一期分三部分", ["一  结果图与网络图", "二  三个前沿方向", "三  解释与因果"], ["o0", "o1", "o2", "o3"])

    # ------------------------------------------------------------------ a good result figure
    def good_figure(self):
        clip_line(self, "g0", "yt_conference_talk_stachniss.mp4", "视频：Cyrill Stachniss · YouTube", start=20)
        tag = self.chapter("一  一张好的结果图")
        bad = T("图 2  度分布图", 30, MUTED).move_to(UP * 1.2)
        good = T("图 2  这张网络的聚集程度远高于随机网络", 30, INK).move_to(UP * 1.2)
        with self.say("g1") as d:
            self.play(FadeIn(tag), FadeIn(bad), run_time=0.8)
            x = Cross(bad, stroke_color=RED, scale_factor=1.1)
            self.play(Create(x), run_time=0.6)
            self.play(FadeOut(x), Transform(bad, good), run_time=1.0)
        G = nx.connected_watts_strogatz_graph(200, 8, 0.15, seed=4)
        C = nx.average_clustering(G)
        rs = []
        for i in range(120):
            H = G.copy(); nx.double_edge_swap(H, nswap=2 * H.number_of_edges(), max_tries=20000, seed=i)
            rs.append(nx.average_clustering(H))
        mu, sd = np.mean(rs), np.std(rs)
        z = (C - mu) / sd
        print("CLUST", C, mu, sd, z)
        with self.say("g2") as d:
            self.play(FadeOut(bad), run_time=0.4)
            big = T(f"{C:.2f}", 96, GOLD, weight=BOLD).move_to(UP * 0.2)
            lab = T("平均聚集系数", 28, MUTED).next_to(big, UP, buff=0.3)
            self.play(FadeIn(lab), Write(big), run_time=1.0)
        with self.say("g2b") as d:
            q = T("缺少参照", 36, INK).next_to(big, DOWN, buff=0.4)
            self.play(FadeIn(q), run_time=0.6)
        hi = max(C, max(rs)) * 1.15
        edges = np.linspace(0, round(hi, 1) + 0.1, 61)
        ytop = int(np.ceil(np.histogram(rs, bins=edges)[0].max() * 1.1 / 10) * 10)  # y-limit from the data
        ax = axes([0, round(hi, 1) + 0.1, 0.1], [0, ytop, ytop], 9.0, 3.6, xnums=list(np.round(np.arange(0, hi + 0.1, 0.1), 1)), fs=20).move_to(DOWN * 0.8)
        xl = xlabel(ax, "平均聚集系数", 22, 0.3)
        bars, _ = hist_bars(ax, rs, edges, MUTED)
        with self.say("g3") as d:
            self.play(FadeOut(q), lab.animate.scale(0.7).move_to(UP * 2.6 + RIGHT * 3.5), big.animate.scale(0.45).move_to(UP * 2.0 + RIGHT * 3.5), run_time=0.8)
            self.play(Create(ax), FadeIn(xl), run_time=0.8)
            self.play(grow_bars(bars, 1.2))
            rl = Line(ax.c2p(C, 0), ax.c2p(C, ytop * 0.9), color=GOLD, stroke_width=5)
            self.play(Create(rl), run_time=0.6)
            nl = T("保度随机网络", 22, MUTED).next_to(bars, UP, buff=0.15).align_to(bars, LEFT).shift(RIGHT * 0.15)
            self.play(FadeIn(nl), run_time=0.4)
        with self.say("g4") as d:
            zl = MathTex(rf"z \approx {z:.0f}", font_size=44, color=GOLD).next_to(rl, LEFT, buff=0.3).shift(UP * 0.8)
            self.play(Write(zl), run_time=0.8)
        with self.say("g4b") as d:
            three = VGroup(chip("观测值", GOLD, 26), chip("参照", MUTED, 26), chip("不确定性", BLUE, 26)).arrange(RIGHT, buff=0.5).move_to(UP * 1.6 + LEFT * 2.6)
            self.play(LaggedStart(*[FadeIn(t, shift=DOWN * 0.2) for t in three], lag_ratio=0.3), run_time=1.2)
        fade_all(self)

    # ------------------------------------------------------------------ network plot pitfalls
    def network_plots(self):
        tag = self.chapter("一  网络图的陷阱")
        G = nx.random_partition_graph([12, 12, 12, 12], 0.35, 0.03, seed=5)
        part = G.graph["partition"]
        cols = [BLUE, GOLD, GREEN, VIOLET]
        cof = {v: cols[i] for i, blk in enumerate(part) for v in blk}
        H = G.copy()
        rng = random.Random(2)
        for _ in range(6):
            u, v = rng.sample(list(G), 2); H.add_edge(u, v)
        pl = fit(nx.spring_layout(G, seed=1), (-6.4, -0.8, -2.8, 2.4))
        pr = fit(nx.spring_layout(H, seed=9), (0.8, 6.4, -2.8, 2.4))
        nl = NetView(G, pl, color=MUTED, eo=0.35, rmin=0.08, rk=0.0)
        nr = NetView(H, pr, color=MUTED, eo=0.35, rmin=0.08, rk=0.0)
        for v in G:
            nl.dots[v].set_color(cof[v]); nr.dots[v].set_color(cof[v])
        tl, tr = T("对照组", 26).move_to(LEFT * 3.6 + UP * 3.0), T("患者组", 26).move_to(RIGHT * 3.6 + UP * 3.0)
        with self.say("n1") as d:
            self.play(FadeIn(tag), FadeIn(tl), FadeIn(tr), FadeIn(nl.group), FadeIn(nr.group), run_time=1.2)
            v0 = 0
            self.play(Indicate(nl.dots[v0], color=RED, scale_factor=2.5), Indicate(nr.dots[v0], color=RED, scale_factor=2.5), run_time=1.0)
        shift = RIGHT * 7.2
        pr2 = {v: pl[v] + shift for v in H}
        with self.say("n2") as d:
            anims = [nr.dots[v].animate.move_to(pr2[v]) for v in H]
            anims += [Transform(e, Line(pr2[u], pr2[v], stroke_width=1.4, color=MUTED, stroke_opacity=0.35)) for (u, v), e in nr.edges.items()]
            self.play(*anims, run_time=1.6)
            ok = T("同一套坐标", 24, GREEN).move_to(DOWN * 3.2)
            self.play(FadeIn(ok), run_time=0.5)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.6)
        # proximity in layout != connectivity
        Q = nx.random_partition_graph([14, 14, 14], 0.4, 0.0, seed=8)
        Q.add_edge(3, 30); Q.add_edge(5, 33); Q.add_edge(20, 40); Q.add_edge(18, 37)
        cen = {0: np.array([-3.6, 0.6]), 1: np.array([-1.6, 0.6]), 2: np.array([2.8, 0.6])}
        rq = np.random.default_rng(3)
        bl = {v: i for i, blk in enumerate(Q.graph["partition"]) for v in blk}
        pq = {v: np.array([*(cen[bl[v]] + rq.normal(0, 0.45, 2)), 0]) for v in Q}
        nq = NetView(Q, pq, color=MUTED, eo=0.4, rmin=0.08, rk=0.0)
        for v in Q:
            nq.dots[v].set_color([BLUE, GOLD, GREEN][bl[v]])
        between = lambda a, b: sum(1 for u, v in Q.edges() if {bl[u], bl[v]} == {a, b})
        with self.say("n3") as d:
            self.play(FadeIn(nq.group), run_time=1.0)
            b1 = Brace(VGroup(nq.dots[0], nq.dots[14]), DOWN, color=MUTED)
            l1 = T(f"挨得近：之间 {between(0, 1)} 条边", 22, BLUE).next_to(b1, DOWN, buff=0.15).shift(LEFT * 0.3)
            self.play(FadeIn(l1), run_time=0.6)
            l2 = T(f"离得远：之间 {between(1, 2) + between(0, 2)} 条边", 22, GREEN).move_to([2.8, -1.8, 0])
            self.play(FadeIn(l2), run_time=0.6)
            self.play(*[e.animate.set_stroke(RED, width=4, opacity=1) for (u, v), e in nq.edges.items() if bl[u] != bl[v]], run_time=0.8)
        print("BETWEEN", between(0, 1), between(1, 2) + between(0, 2))
        with self.say("n3b") as d:
            self.play(Indicate(l1, color=BLUE), Indicate(l2, color=GREEN), run_time=1.2)
        with self.say("n4") as d:
            self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.5)
            rainbow = Rectangle(width=6.0, height=0.6, stroke_width=0).set_fill(color=[RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE], opacity=1).move_to(UP * 1.2)
            vir = Rectangle(width=6.0, height=0.6, stroke_width=0).set_fill(color=["#440154", "#3b528b", "#21918c", "#5ec962", "#fde725"], opacity=1).move_to(DOWN * 0.6)
            l1 = T("彩虹色", 24, RED).next_to(rainbow, LEFT, buff=0.3)
            l2 = T("感知均匀", 24, GREEN).next_to(vir, LEFT, buff=0.3)
            x = Cross(rainbow, stroke_color=RED, scale_factor=0.6).scale([0.4, 1, 1])
            self.play(FadeIn(rainbow), FadeIn(l1), run_time=0.8)
            self.play(Create(x), FadeIn(vir), FadeIn(l2), run_time=1.0)
            rg = VGroup(Dot(radius=0.2, color="#d62728"), Dot(radius=0.2, color="#2ca02c"), T("只靠红绿区分：不可取", 24, MUTED)).arrange(RIGHT, buff=0.3).move_to(DOWN * 2.3)
            self.play(FadeIn(rg), run_time=0.6)
        fade_all(self)

    # ------------------------------------------------------------------ degree plots
    def degree_plots(self):
        tag = self.chapter("一  度分布怎么画")
        G = nx.barabasi_albert_graph(3000, 2, seed=6)
        k = np.array([d for _, d in G.degree()])
        kmax = k.max()
        edges = np.arange(0, 162, 4)
        ystep = int(np.ceil(np.histogram(np.minimum(k, 159), bins=edges)[0].max() * 1.05 / 3 / 100) * 100)  # y-limit from the data
        ax = axes([0, 160, 40], [0, 3 * ystep, ystep], 5.2, 3.8, xnums=[0, 40, 80, 120, 160], ynums=[ystep, 2 * ystep, 3 * ystep], fs=18).move_to(LEFT * 3.2 + DOWN * 0.3)
        # axis label above the y-axis (horizontal) so it stays inside the frame
        xl, yl = xlabel(ax, "度", 22, 0.3), T("节点数", 22, MUTED).next_to(ax, UP, buff=0.15).align_to(ax.y_axis.numbers, LEFT)
        bars, cnt = hist_bars(ax, np.minimum(k, 159), edges, BLUE)
        with self.say("d1") as d:
            self.play(FadeIn(tag), Create(ax), FadeIn(xl), FadeIn(yl), run_time=0.8)
            self.play(grow_bars(bars, 1.4))
            tail = SurroundingRectangle(VGroup(*[b for b in bars if b.get_center()[0] > ax.c2p(40, 0)[0]]), color=RED, buff=0.1)
            self.play(Create(tail), run_time=0.6)
        ks = np.unique(k)
        ccdf = np.array([(k >= x).mean() for x in ks])
        ax2 = axes([0, 3, 1], [-3.5, 0, 1], 5.0, 3.8, fs=18).move_to(RIGHT * 3.4 + DOWN * 0.3)
        xt = VGroup(*[MathTex(f"10^{i}", font_size=24, color=MUTED).next_to(ax2.c2p(i, -3.5), DOWN, buff=0.12) for i in range(4)])
        yt = VGroup(*[MathTex(f"10^{{{i}}}", font_size=24, color=MUTED).next_to(ax2.c2p(0, i), LEFT, buff=0.12) for i in (-3, -2, -1, 0)])
        xl2 = T("度 k", 22, MUTED).next_to(xt, DOWN, buff=0.15)
        yl2 = MathTex(r"P(K\geq k)", font_size=28, color=MUTED).next_to(ax2, UP, buff=0.1).align_to(ax2, LEFT)
        pts = VGroup(*[Dot(ax2.c2p(np.log10(x), max(np.log10(c), -3.5)), radius=0.04, color=GOLD) for x, c in zip(ks, ccdf)])
        with self.say("d2") as d:
            self.play(Create(ax2), FadeIn(xt), FadeIn(yt), FadeIn(xl2), FadeIn(yl2), run_time=1.0)
            self.play(LaggedStart(*[GrowFromCenter(p) for p in pts], lag_ratio=0.02), run_time=d * 0.4)
        with self.say("d3") as d:
            fitl = Line(ax2.c2p(0.3, np.log10((k >= 2).mean())), ax2.c2p(2.3, np.log10((k >= 2).mean()) - 2.0 * 2), color=RED, stroke_width=3)
            fitl = DashedLine(ax2.c2p(np.log10(2), 0), ax2.c2p(np.log10(2) + 1.75, -3.5), color=RED, stroke_width=3)
            self.play(Create(fitl), run_time=0.8)
            w = T("像直线 ≠ 幂律", 30, RED, weight=BOLD).move_to(RIGHT * 4.2 + UP * 2.5)
            self.play(Write(w), run_time=0.8)
        fade_all(self)

    # ------------------------------------------------------------------ higher-order interactions
    def higher_order(self):
        tag = self.chapter("二  高阶相互作用")
        def tri(c, filled, col):
            P = [c + np.array([np.cos(a), np.sin(a), 0]) * 1.0 for a in (PI / 2, PI / 2 + TAU / 3, PI / 2 + 2 * TAU / 3)]
            poly = Polygon(*P, color=col, stroke_width=4, fill_opacity=0.45 if filled else 0)
            return VGroup(poly, *[Dot(p, radius=0.16, color=col) for p in P]), P
        with self.say("o1b") as d:
            a, b = Dot(LEFT * 1.2, radius=0.18, color=BLUE), Dot(RIGHT * 1.2, radius=0.18, color=BLUE)
            l = Line(a.get_center(), b.get_center(), color=BLUE, stroke_width=4)
            self.play(FadeIn(tag), GrowFromCenter(a), GrowFromCenter(b), Create(l), run_time=1.0)
            pw = T("两两关系", 26, MUTED).next_to(l, DOWN, buff=0.4)
            self.play(FadeIn(pw), run_time=0.5)
        self.play(FadeOut(VGroup(a, b, l, pw)), run_time=0.4)
        # complex vs three pairs
        lc, rc = LEFT * 4.2 + UP * 1.0, RIGHT * 0.2 + UP * 1.0
        blobs = VGroup(*[Circle(radius=0.48, color=c, fill_opacity=0.35).move_to(lc + 0.42 * np.array([np.cos(t), np.sin(t), 0])) for c, t in ((BLUE, PI / 2), (GOLD, PI / 2 + TAU / 3), (GREEN, PI / 2 + 2 * TAU / 3))])
        cl = T("一个三元复合物", 22, INK).next_to(blobs, DOWN, buff=0.3)
        pairs = VGroup()
        for i, (c1, c2) in enumerate(((BLUE, GOLD), (GOLD, GREEN), (GREEN, BLUE))):
            g = VGroup(Circle(radius=0.25, color=c1, fill_opacity=0.35), Circle(radius=0.25, color=c2, fill_opacity=0.35)).arrange(RIGHT, buff=0.0)
            pairs.add(g)
        pairs.arrange(RIGHT, buff=0.35).move_to(rc)
        pl = T("三对两两结合", 22, INK).next_to(pairs, DOWN, buff=0.45)
        t1, _ = tri(LEFT * 4.2 + DOWN * 2.0, False, INK); t2, _ = tri(RIGHT * 0.2 + DOWN * 2.0, False, INK)
        t1.scale(0.7); t2.scale(0.7)
        with self.say("o2b") as d:
            self.play(FadeIn(blobs), FadeIn(cl), run_time=0.8)
            self.play(FadeIn(pairs), FadeIn(pl), run_time=0.8)
            self.play(TransformFromCopy(blobs, t1), TransformFromCopy(pairs, t2), run_time=1.2)
            eq = T("=", 48, RED, weight=BOLD).move_to(LEFT * 2.0 + DOWN * 2.0)
            self.play(FadeIn(eq), run_time=0.4)
        with self.say("o3b") as d:
            ft, _ = tri(LEFT * 4.2 + DOWN * 2.0, True, GOLD); ft.scale(0.7)
            self.play(Transform(t1, ft), Transform(eq, T("≠", 48, GOLD, weight=BOLD).move_to(eq)), run_time=1.2)
            hl = T("超图 · 单纯复形", 28, GOLD, weight=BOLD).move_to(RIGHT * 4.6 + DOWN * 2.0)
            self.play(FadeIn(hl), run_time=0.6)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.6)
        with self.say("o4b") as d:
            ax = axes([0, 1, 0.5], [0, 1, 0.5], 6.0, 3.8).move_to(DOWN * 0.3)
            xl, yl = xlabel(ax, "两两感染率", 22, 0.3), ylabel(ax, "感染比例", 22)
            cont = ax.plot(lambda x: 0 if x < 0.4 else 0.9 * (1 - np.exp(-(x - 0.4) * 4)), x_range=[0, 1, 0.005], color=BLUE, stroke_width=4, use_smoothing=False)
            jump = VGroup(ax.plot(lambda x: 0, x_range=[0, 0.55], color=RED, stroke_width=4),
                          DashedLine(ax.c2p(0.55, 0), ax.c2p(0.55, 0.62), color=RED),
                          ax.plot(lambda x: 0.62 + 0.3 * (1 - np.exp(-(x - 0.55) * 5)), x_range=[0.55, 1, 0.005], color=RED, stroke_width=4))
            lg = VGroup(T("没有三体作用：连续", 22, BLUE), T("三体感染率大：突然跳变", 22, RED)).arrange(DOWN, aligned_edge=LEFT, buff=0.15).next_to(ax, RIGHT, buff=0.2).shift(UP * 1.0)
            sk = T("示意图", 20, MUTED).next_to(ax, UP, buff=0.1).align_to(ax, LEFT)
            self.play(Create(ax), FadeIn(xl), FadeIn(yl), FadeIn(sk), run_time=0.8)
            self.play(Create(cont), FadeIn(lg[0]), run_time=1.2)
            self.play(Create(jump), FadeIn(lg[1]), run_time=1.4)
        fade_all(self)

    # ------------------------------------------------------------------ temporal networks
    def temporal(self):
        clip_line(self, "t0", "yt_temporal_epidemic_dsl.mp4", "视频：Dynamical Systems Laboratory · YouTube", start=5)
        tag = self.chapter("二  时间网络")
        P = {"甲": LEFT * 4.0 + UP * 0.6, "乙": LEFT * 0.0 + UP * 0.6, "丙": RIGHT * 4.0 + UP * 0.6}
        nodes = {k: VGroup(Circle(radius=0.45, color=GOLD, fill_opacity=0.2, stroke_width=3), T(k, 28)).move_to(p) for k, p in P.items()}
        tl = NumberLine(x_range=[0, 3, 1], length=8, color=MUTED, include_numbers=False).move_to(DOWN * 2.2)
        tn = VGroup(*[T(f"时刻 {i}", 20, MUTED).next_to(tl.n2p(i), DOWN, buff=0.15) for i in (1, 2)])
        e1 = Line(P["甲"], P["乙"], color=BLUE, stroke_width=6).set_z_index(-1)
        e2 = Line(P["乙"], P["丙"], color=BLUE, stroke_width=6).set_z_index(-1)
        m1 = Dot(tl.n2p(1), radius=0.12, color=BLUE); m2 = Dot(tl.n2p(2), radius=0.12, color=BLUE)
        with self.say("t1") as d:
            self.play(FadeIn(tag), *[GrowFromCenter(n) for n in nodes.values()], Create(tl), FadeIn(tn), run_time=1.0)
            self.play(Create(e1), FadeIn(m1), run_time=0.8)
            self.play(e1.animate.set_stroke(opacity=0.25), run_time=0.4)
            self.play(Create(e2), FadeIn(m2), run_time=0.8)
            self.play(e2.animate.set_stroke(opacity=0.25), run_time=0.4)
        with self.say("t2") as d:
            tok = Dot(P["甲"], radius=0.16, color=GREEN)
            self.play(FadeIn(tok), run_time=0.3)
            self.play(tok.animate.move_to(P["乙"]), e1.animate.set_stroke(GREEN, opacity=1), run_time=0.8)
            self.play(tok.animate.move_to(P["丙"]), e2.animate.set_stroke(GREEN, opacity=1), run_time=0.8)
            ok = T("甲 → 丙  可达", 24, GREEN).move_to(UP * 2.4 + LEFT * 2.5)
            self.play(FadeIn(ok), run_time=0.4)
            tok2 = Dot(P["丙"], radius=0.16, color=RED)
            self.play(FadeIn(tok2), e1.animate.set_stroke(BLUE, opacity=0.25), e2.animate.set_stroke(BLUE, opacity=0.25), run_time=0.4)
            self.play(tok2.animate.move_to(P["乙"]), run_time=0.8)
            no = T("丙 → 甲  不可达：时刻 1 的边已经过去", 24, RED).move_to(UP * 2.4 + RIGHT * 2.2)
            self.play(FadeIn(no), Wiggle(tok2), run_time=0.8)
        with self.say("t3") as d:
            self.play(FadeOut(tok), FadeOut(tok2), FadeOut(ok), FadeOut(no), FadeOut(m1), FadeOut(m2), FadeOut(tl), FadeOut(tn), run_time=0.5)
            self.play(e1.animate.set_stroke(INK, opacity=1), e2.animate.set_stroke(INK, opacity=1), run_time=0.6)
            st = T("聚合成静态网络：三人彼此可达", 26, GOLD).move_to(DOWN * 1.4)
            self.play(FadeIn(st), run_time=0.6)
            over = T("传播范围被高估", 30, RED, weight=BOLD).next_to(st, DOWN, buff=0.4)
            self.play(Write(over), run_time=0.8)
        fade_all(self)

    # ------------------------------------------------------------------ graph neural networks
    def gnn(self):
        clip_line(self, "x0", "yt_gnn_cs224w_stanford.mp4", "视频：Stanford Online · YouTube", start=60)
        tag = self.chapter("二  图神经网络")
        G = nx.karate_club_graph()
        pos = fit(nx.spring_layout(G, seed=4), (-6.4, -0.8, -3.0, 2.8))
        net = NetView(G, pos, color=MUTED, eo=0.35, rmin=0.09, rk=0.0)
        c = 0
        with self.say("x1") as d:
            self.play(FadeIn(tag), FadeIn(net.group), run_time=1.0)
            self.play(net.dots[c].animate.set_color(GOLD).scale(1.6), run_time=0.5)
            msgs = [Dot(pos[w], radius=0.07, color=BLUE) for w in G.neighbors(c)]
            self.play(*[m.animate.move_to(pos[c]) for m in msgs], run_time=1.2)
            self.remove(*msgs)
            self.play(Flash(net.dots[c], color=GOLD), run_time=0.6)
        hop = nx.single_source_shortest_path_length(G, c)
        with self.say("x2") as d:
            for h, col in ((1, BLUE), (2, GREEN)):
                self.play(*[net.dots[v].animate.set_color(col) for v, dd in hop.items() if dd == h], run_time=0.8)
                lab = T(f"第 {h} 层", 24, col).move_to(RIGHT * 2.8 + UP * (2.4 - 0.5 * h))
                self.play(FadeIn(lab), run_time=0.4)
        # over-smoothing: repeated neighbourhood averaging of random features
        rng = np.random.default_rng(3)
        n = G.number_of_nodes()
        A = nx.to_numpy_array(G) + np.eye(n)
        Pm = A / A.sum(1, keepdims=True)
        x = rng.normal(size=n)
        layers = [x]
        for _ in range(16):
            layers.append(Pm @ layers[-1])
        spread_ = [np.std(l) for l in layers]
        print("SMOOTH", [round(s, 3) for s in spread_[:9]])

        def cmap(v, lo=-2.0, hi=2.0):
            t = np.clip((v - lo) / (hi - lo), 0, 1)
            return interpolate_color(ManimColor(BLUE), ManimColor(RED), t)
        ax = axes([0, 16, 4], [0, 1.2, 0.5], 5.0, 3.0, xnums=[0, 4, 8, 12, 16], ynums=[0, 0.5, 1], fs=18).move_to(RIGHT * 3.6 + DOWN * 1.0)
        xl, yl = xlabel(ax, "层数", 20, 0.3), ylabel(ax, "节点表示的差异", 20)
        curve = ax.plot_line_graph(list(range(17)), list(np.array(spread_) / spread_[0]), line_color=GOLD, vertex_dot_radius=0.05, vertex_dot_style={"color": GOLD}, stroke_width=4)
        with self.say("x3") as d:
            self.play(*[FadeOut(m) for m in self.mobjects if isinstance(m, Text) and m is not tag], run_time=0.3)
            self.play(*[net.dots[v].animate.set_color(cmap(layers[0][v])).scale(1 / 1.6 if v == c else 1) for v in G], Create(ax), FadeIn(xl), FadeIn(yl), run_time=1.0)
            lt = T("第 0 层", 24, INK).move_to(RIGHT * 3.6 + UP * 2.4)
            self.add(lt)
            for L in (1, 2, 4, 8, 16):
                self.play(*[net.dots[v].animate.set_color(cmap(layers[L][v])) for v in G],
                          Transform(lt, T(f"第 {L} 层", 24, INK).move_to(lt)), run_time=0.55)
            self.play(Create(curve), run_time=1.0)
            band = Rectangle(width=ax.c2p(3, 0)[0] - ax.c2p(2, 0)[0], height=ax.c2p(0, 1.2)[1] - ax.c2p(0, 0)[1],
                             fill_color=GREEN, fill_opacity=0.2, stroke_width=0).move_to(ax.c2p(2.5, 0.6))
            self.play(FadeIn(band), run_time=0.5)
        with self.say("x4") as d:
            self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.5)
            dr = [Dot(radius=0.13, color=c_) for c_ in (BLUE, BLUE, VIOLET)]
            train = VGroup(*[VGroup(Square(side_length=0.3, color=GREEN, fill_opacity=0.5), T(f"药物 {s}", 22)).arrange(RIGHT, buff=0.2) for s in ("甲", "甲′")]).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
            tb = VGroup(T("训练集", 26, GREEN), train).arrange(DOWN, buff=0.3).move_to(LEFT * 3.4 + UP * 0.6)
            test = VGroup(Square(side_length=0.3, color=GOLD, fill_opacity=0.5), T("药物 甲″", 22)).arrange(RIGHT, buff=0.2)
            teb = VGroup(T("测试集", 26, GOLD), test).arrange(DOWN, buff=0.3).move_to(RIGHT * 2.0 + UP * 0.6)
            self.play(FadeIn(tb), FadeIn(teb), run_time=0.8)
            sim = DashedLine(train.get_right(), test.get_left(), color=RED, stroke_width=3)
            sl = T("几乎一样", 22, RED).next_to(sim, UP, buff=0.1)
            self.play(Create(sim), FadeIn(sl), run_time=0.8)
            leak = T("性能被高估", 28, RED, weight=BOLD).move_to(DOWN * 1.6 + LEFT * 0.6)
            base = chip("与简单方法比较", INK, 24).next_to(leak, DOWN, buff=0.4)
            self.play(Write(leak), run_time=0.8)
            self.play(FadeIn(base, shift=UP * 0.2), run_time=0.6)
        fade_all(self)

    # ------------------------------------------------------------------ interpretability & causality
    def causality(self):
        tag = self.chapter("三  解释与因果")
        G = nx.random_partition_graph([10, 10, 10], 0.4, 0.05, seed=11)
        pos = fit(nx.spring_layout(G, seed=2), (-6.2, -1.2, -2.8, 2.6))
        net = NetView(G, pos, color=MUTED, eo=0.35, rmin=0.08, rk=0.0)
        sub = list(range(10, 16))
        with self.say("y1") as d:
            self.play(FadeIn(tag), FadeIn(net.group), run_time=1.0)
            self.play(*[net.dots[v].animate.set_color(GOLD).scale(1.4) for v in sub],
                      *[e.animate.set_stroke(GOLD, width=3, opacity=1) for (u, v), e in net.edges.items() if u in sub and v in sub], run_time=1.0)
            tl = chip("模型依赖的子图", GOLD, 24).move_to(RIGHT * 3.4 + UP * 2.0)
            a = arrow(tl.get_bottom(), RIGHT * 2.0 + UP * 0.2, MUTED)
            opts = VGroup(chip("可能是生物机制", GREEN, 24), chip("也可能是数据偏倚", RED, 24)).arrange(RIGHT, buff=0.3).move_to(RIGHT * 3.4 + DOWN * 0.2)
            self.play(FadeIn(tl), run_time=0.5)
            self.play(FadeIn(opts, shift=UP * 0.2), run_time=0.8)
        with self.say("y2") as d:
            self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.5)
            steps = VGroup(chip("关联", MUTED, 28), chip("预测", BLUE, 28), chip("干预", GOLD, 28)).arrange(RIGHT, buff=1.2).move_to(UP * 1.2)
            arrs = VGroup(*[arrow(steps[i].get_right(), steps[i + 1].get_left(), MUTED, buff=0.1) for i in range(2)])
            self.play(LaggedStart(*[FadeIn(s, shift=RIGHT * 0.2) for s in steps], lag_ratio=0.3), LaggedStart(*[GrowArrow(a) for a in arrs], lag_ratio=0.3), run_time=1.4)
        with self.say("y3") as d:
            ex = VGroup(*[chip(s, GOLD, 22) for s in ("基因敲除", "基因扰动", "药物处理", "脑刺激")]).arrange(RIGHT, buff=0.3).next_to(steps, DOWN, buff=1.0)
            self.play(LaggedStart(*[FadeIn(e, shift=UP * 0.2) for e in ex], lag_ratio=0.2), run_time=1.2)
        fade_all(self)

    # ------------------------------------------------------------------ recap
    def recap(self):
        with self.say("r1") as d:
            head = T("三个要点", 40, INK, weight=BOLD).to_edge(UP, buff=0.7)
            self.play(Write(head), run_time=0.8)
        items = [("r2", GOLD, "结果图：观测值 + 参照 + 不确定性"),
                 ("r3", BLUE, "固定布局，结论来自定量分析"),
                 ("r4", GREEN, "新方法也要回答：节点、边、与什么比较")]
        rows = VGroup()
        for i, (k, c, s) in enumerate(items):
            num = Circle(radius=0.32, color=c, fill_opacity=0.18, stroke_width=3).add(T(str(i + 1), 28, c, weight=BOLD))
            rows.add(VGroup(num, T(s, 30, INK)).arrange(RIGHT, buff=0.4))
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.6).next_to(head, DOWN, buff=0.8)
        for (k, _, _), row in zip(items, rows):
            with self.say(k) as d:
                self.play(FadeIn(row, shift=RIGHT * 0.3), run_time=0.8)
        self.wait(1.5)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=1.0)
