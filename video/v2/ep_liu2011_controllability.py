"""Paper explainer: Liu, Slotine & Barabási 2011, controllability of complex networks."""
import networkx as nx
import numpy as np

from common import *  # noqa: F401,F403
from paperkit import DiNet, arrow, counter, fit, max_matching, drivers, n_drivers, sf_digraph

TITLE = "复杂网络的可控性：最大匹配与驱动节点"

LINES = {
    # hook
    "h1": "我们先来看一个小小的调控网络。中间的枢纽基因，调控着周围六个基因。枢纽，就是连接特别多的节点。",
    "h2": "我们想把每个基因都调到各自的目标水平，也就是右边这几条短横线。可我们只能对少数几个基因，直接施加信号。",
    "h3": "很自然的想法是：控制枢纽就够了，它连着所有人。黄色箭头，就是加在枢纽上的信号。",
    "h4": "但是你看，枢纽只能发出一个信号。六个下游只能跟着同一个信号一起涨落，没法各自走到目标。",
    "h5": "【慢】最少要控制几个节点，又该控制哪些，2011年《自然》杂志上的一篇论文，给出了一个漂亮的答案。",
    "q0": "这一期分三部分来讲。",
    "q1": "第一部分，什么叫可控，以及怎样用最大匹配，算出最少的驱动节点。",
    "q2": "第二部分，驱动节点的规律：它们在哪里，数目由什么决定。",
    "q3": "第三部分，这篇论文的意义和局限。",
    # controllability
    "k1": "先看第一部分。我们先说什么叫可控。网络的线性动力学，可以写成这样一个方程。",
    "k1b": "等号左边，是每个节点状态的变化速度。右边，x是所有节点的当前状态，u是我们从外面加的信号。",
    "k2": "矩阵A记录谁影响谁，矩阵B记录信号加在哪些节点上。这些被直接加了信号的节点，叫驱动节点。",
    "k3": "【慢】可控，就是存在某种输入，能把系统从任何状态，带到任何状态。就像画面上，把这个点沿着某条路线，送到星星的位置。",
    "k4": "控制理论早有判断可控的方法。但真实网络里，矩阵中的这些权重通常不知道；节点一多，数值计算也很不稳定。",
    "k5": "所以，论文借用了结构可控性的思路：只看矩阵里哪些元素是零、哪些不是零。几乎所有权重取值下都可控，就叫结构可控。",
    # matching
    "m1": "关键一步，是把最少输入的问题，变成图论里的最大匹配问题。",
    "m2": "匹配是一组边，任意两条既不共用起点，也不共用终点。你看，这两条红色的边共用起点，那两条共用终点，都不能同时选。",
    "m3": "换句话说，每个节点最多领一条入边，也最多发一条出边。",
    "m4": "在这个小网络里，我们挑出尽可能多的匹配边，也就是最大匹配。一共六条，画成黄色。",
    "m5": "被匹配边指向的节点，叫匹配节点；没有被指向的，叫非匹配节点，画成红色。",
    "m6": "【慢】论文的最小输入定理说：最少驱动节点数，等于节点数减去最大匹配的边数，至少是一。",
    "m6b": "公式左边，是驱动节点数；括号里，是节点数减去最大匹配的边数。这个网络有八个节点、六条匹配边，八减六，等于二。",
    "m7": "非匹配节点就是驱动节点。给它们各加一个独立信号，整个网络就结构可控。",
    # paths & cycles
    "p1": "这背后的道理是这样的。最大匹配把网络拆成了几条互不相交的路径，再加上一些环。",
    "p2": "每条路径的起点，没有被谁匹配，信号只能从外面加进来，所以起点必须是驱动节点。",
    "p3": "沿着路径，信号一节一节往下传，每个节点都由它的上家单独带动。",
    "p4": "环不需要新的输入。只要从已有路径搭一条边过去，就能挂在上面一起被控制，就是这条绿色的边。",
    "p5": "最大匹配可以用经典的匹配算法高效求出，所以大型真实网络也能算。",
    "p5b": "本站的可控性专题里，有最大匹配的交互演示。把平均出度从小调大，红色的驱动节点越来越少。",
    # hubs
    "d0": "下面进入第二部分。画面里，是为这篇论文制作的一段网络数据可视化。",
    "d1": "我们先回到开头的星形网络。枢纽在匹配里只能带走一个下游，剩下五个叶子没有被匹配。",
    "d2": "所以七个节点，要六个驱动节点：枢纽本身，加上五个叶子。",
    "d3": "在更大的网络里也一样。我们在一千个节点的无标度网络上算一算。无标度网络，就是大多数节点连接很少、少数枢纽连接很多的网络。",
    "d3b": "按节点的度，也就是连接数，把节点分成三组。柱子的高度，是每组里驱动节点所占的比例。",
    "d4": "【慢】低度节点里，驱动节点占了大多数；到了枢纽这一组，比例就低得多。驱动节点倾向于避开枢纽。",
    "d4b": "原因还是匹配：一个节点只能匹配一个下游，枢纽的下游再多，也只能带动其中一个。",
    # degree distribution
    "n1": "驱动节点有多少，由什么决定，论文用空腔方法做了解析计算，又分析了基因调控、食物网、代谢、神经元等真实网络。",
    "n2": "我们来做个对照实验。左边这张图，横轴是平均度，也就是平均每个节点的连接数；纵轴是驱动节点占全部节点的比例。",
    "n3": "灰色是度分布均匀的随机网络，蓝色是度分布不均匀的无标度网络。",
    "n3b": "【慢】平均度越低、度分布越不均匀，需要的驱动节点就越多。",
    "n4": "再拿一张无标度网络做两种洗牌。右边绿色的柱子，保持每个节点的入度和出度，驱动节点比例几乎不变。",
    "n4b": "灰色的柱子是完全打乱，比例就明显变了。",
    "n5": "这正是论文的结论：驱动节点数主要由度分布决定。作者还报告，基因调控网络的驱动节点比例较高，一些社会网络则较低。",
    # meaning & limits
    "l1": "最后是第三部分。对生物医学来说，这提供了一个从网络结构出发，思考干预点的框架。",
    "l2": "但驱动节点多为低度节点，并不意味着药物就该去靶向低度基因。结构可控，不等于实际可控。",
    "l3": "可控只说明存在某种输入，不管要花多少能量和时间；而生物系统往往是非线性、多稳态的。",
    "l4": "还有一个微妙的假设。如果每个节点都有自身的动力学，就相当于每个节点都带一个自环，也就是一条指向自己的边。",
    "l5": "【慢】自环本身就能当匹配边，网络出现完美匹配，驱动节点一下子降到一个。所以，度分布决定可控性这个结论，依赖于忽略节点自身的动力学。",
    "l6": "另外，最大匹配往往不唯一。换一种匹配，驱动节点集合也跟着变。论文只给出了数目，和其中一个可行集合。",
    "l7": "2017年，有研究在线虫的神经连接图谱上，第一次用细胞消融实验，检验了网络控制的预测。画面里，是线虫运动神经元的示意动画。",
    # recap
    "r1": "好，我们来总结一下。",
    "r2": "第一，最少驱动节点数，等于节点数减去最大匹配的边数，大网络上也能高效计算。",
    "r3": "第二，驱动节点数主要由度分布决定；稀疏、不均匀的网络最难控制，驱动节点倾向于避开枢纽。",
    "r4": "第三，这些结论依赖线性和结构可控的假设，也忽略了节点自身的动力学。",
}

# the 8-node teaching network
EDGES = [(1, 2), (2, 3), (3, 4), (1, 5), (5, 6), (6, 7), (7, 5), (1, 8), (3, 8)]
POS = {1: (-5.2, 0.3), 2: (-3.4, 1.7), 3: (-1.4, 1.7), 4: (0.6, 1.7), 8: (-1.4, 0.0),
       5: (-3.4, -1.3), 6: (-2.4, -2.8), 7: (-1.2, -1.6)}
MATCH = [(1, 2), (2, 3), (3, 4), (5, 6), (6, 7), (7, 5)]


def teach_net():
    G = nx.DiGraph(); G.add_nodes_from(sorted(POS)); G.add_edges_from(EDGES)
    pos = {v: np.array([*p, 0]) for v, p in POS.items()}
    return G, pos


class Episode(Narrated):
    LINES = LINES

    def construct(self):
        self.hook()
        self.parts()
        self.controllability()
        self.matching()
        self.paths()
        self.hubs()
        self.degree()
        self.limits()
        self.recap()

    def star(self, center=LEFT * 3.2, R=2.2):
        G = nx.DiGraph()
        G.add_edges_from((0, i) for i in range(1, 7))
        pos = {0: center}
        for i in range(1, 7):
            t = PI / 2 + 2 * PI * (i - 1) / 6
            pos[i] = center + R * np.array([np.cos(t), np.sin(t), 0])
        return G, pos

    # ------------------------------------------------------------------ hook
    def hook(self):
        G, pos = self.star()
        net = DiNet(G, pos, r=0.28, labels=False, color=GREEN)
        net.circ[0].scale(1.4)
        cols = [BLUE, VIOLET, GOLD, RED, "#4fc3d1", GREEN]
        for i in range(1, 7):
            net.circ[i].set_stroke(cols[i - 1])
        ax = Axes(x_range=[0, 7, 1], y_range=[0, 1, 0.5], x_length=5.0, y_length=3.6,
                  axis_config={"color": MUTED, "include_tip": False}).move_to(RIGHT * 3.4 + DOWN * 0.2)
        yl = T("表达水平", 22, MUTED).rotate(PI / 2).next_to(ax.y_axis, LEFT, buff=0.2)
        targets = [0.8, 0.3, 0.6, 0.15, 0.9, 0.45]
        tmarks = VGroup(*[Line(ax.c2p(i + 0.6, t), ax.c2p(i + 1.4, t), color=cols[i], stroke_width=5) for i, t in enumerate(targets)])
        lvl = ValueTracker(0.05)
        bars = always_redraw(lambda: VGroup(*[Rectangle(width=0.6, height=max(0.01, ax.c2p(0, lvl.get_value())[1] - ax.c2p(0, 0)[1]),
                                                        fill_color=cols[i], fill_opacity=0.55, stroke_width=0
                                                        ).move_to(ax.c2p(i + 1, 0), aligned_edge=DOWN) for i in range(6)]))
        with self.say("h1") as d:
            self.play(FadeIn(net.group[1]), LaggedStart(*[GrowArrow(a) for a in net.arrows.values()], lag_ratio=0.1), run_time=d * 0.6)
        with self.say("h2") as d:
            self.play(Create(ax), FadeIn(yl), run_time=1.0)
            self.add(bars)
            self.play(LaggedStart(*[Create(m) for m in tmarks], lag_ratio=0.15), run_time=1.5)
            tl = T("目标", 22, INK).next_to(tmarks[4], UP, buff=0.1)
            self.play(FadeIn(tl), run_time=0.5)
        u = VGroup(arrow(pos[0] + LEFT * 1.6, pos[0], 0.42, GOLD, 5), MathTex("u", color=GOLD, font_size=40).move_to(pos[0] + LEFT * 1.8))
        with self.say("h3") as d:
            self.play(FadeIn(u), net.fill(0, GOLD, 0.6), run_time=1.0)
        with self.say("h4") as d:
            for v in (0.8, 0.3, 0.6):
                self.play(lvl.animate.set_value(v), *[net.arrows[(0, i)].animate.set_color(GOLD) for i in range(1, 7)], run_time=d * 0.22)
        with self.say("h5") as d:
            q = T("最少控制几个节点", 50, GOLD, weight=BOLD).to_edge(DOWN, buff=0.4)
            self.play(Write(q), run_time=1.2)
        self.remove(bars)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    def parts(self):
        head, items = slide("这一期分三部分", ["一  可控性与最大匹配", "二  驱动节点的规律", "三  意义与局限"])
        with self.say("q0") as d:
            self.play(FadeIn(head, shift=RIGHT * 0.3), run_time=0.6)
        for k, it in zip(("q1", "q2", "q3"), items):
            with self.say(k) as d:
                self.play(FadeIn(it, shift=RIGHT * 0.3), run_time=0.6)
        self.wait(0.6)
        self.play(FadeOut(head), FadeOut(items), run_time=0.6)

    # ------------------------------------------------------------------ controllability
    def controllability(self):
        tag = self.chapter("一 · 什么叫可控")
        eq = MathTex(r"\dot{\mathbf x}", "=", "A", r"\mathbf x", "+", "B", r"\mathbf u", font_size=72)
        with self.say("k1") as d:
            self.play(FadeIn(tag), Write(eq), run_time=d * 0.5)
        with self.say("k1b") as d:
            l0 = T("变化速度", 24, INK).next_to(eq[0], DOWN, buff=0.35)
            l3 = T("当前状态", 24, BLUE).next_to(eq[3], DOWN, buff=0.35)
            l6 = T("外部信号", 24, GOLD).next_to(eq[6], DOWN, buff=0.35)
            self.play(FadeIn(l0, shift=UP * 0.2), run_time=0.6)
            self.wait(d * 0.25)
            self.play(FadeIn(l3, shift=UP * 0.2), run_time=0.6)
            self.play(FadeIn(l6, shift=UP * 0.2), run_time=0.6)
        with self.say("k2") as d:
            self.play(FadeOut(VGroup(l0, l3, l6)), eq.animate.to_edge(UP, buff=1.0), run_time=0.8)
            la = T("谁影响谁", 24, BLUE); lb = T("信号加在哪里", 24, GOLD)
            la.next_to(eq[2], DOWN, buff=0.3); lb.next_to(eq[5], DOWN, buff=0.3).shift(RIGHT * 0.4)
            self.play(eq[2].animate.set_color(BLUE), FadeIn(la), run_time=0.6)
            self.play(eq[5].animate.set_color(GOLD), eq[6].animate.set_color(GOLD), FadeIn(lb), run_time=0.6)
        # state space: dot moved from start to target
        with self.say("k3") as d:
            a, b = LEFT * 3 + DOWN * 1.2, RIGHT * 3 + DOWN * 0.4
            s, t = Dot(a, color=BLUE, radius=0.12), Star(outer_radius=0.22, color=GOLD, fill_opacity=1).move_to(b)
            path = VMobject(color=GOLD).set_points_smoothly([a, LEFT * 1 + UP * 0.6, RIGHT * 1.2 + DOWN * 1.8, b])
            self.play(FadeOut(la), FadeOut(lb), FadeIn(s), FadeIn(t), run_time=0.6)
            self.play(MoveAlongPath(s, path), Create(path), run_time=d * 0.55)
        self.play(FadeOut(VGroup(s, t, path)), run_time=0.5)
        vals = [["0", "0.7", "0", "0"], ["0", "0", "1.3", "0"], ["-0.4", "0", "0", "2.1"], ["0", "0.9", "0", "0"]]
        M = Matrix(vals, element_to_mobject_config={"font_size": 36}, h_buff=1.3).scale(0.9).move_to(DOWN * 0.6)
        with self.say("k4") as d:
            self.play(Write(M), run_time=1.2)
            qs = [e for e, v in zip(M.get_entries(), sum(vals, [])) if v != "0"]
            self.play(*[e.animate.set_color(RED) for e in qs], run_time=0.8)
            qm = VGroup(*[T("未知", 18, RED).next_to(e, UR, buff=0.02) for e in qs])
            self.play(FadeIn(qm), run_time=0.6)
        with self.say("k5") as d:
            new = [MathTex(r"\ast" if v != "0" else "0", font_size=40, color=GOLD if v != "0" else MUTED).move_to(e)
                   for e, v in zip(M.get_entries(), sum(vals, []))]
            self.play(FadeOut(qm), *[Transform(e, n) for e, n in zip(M.get_entries(), new)], run_time=1.4)
            lab = T("只看零与非零", 30, GOLD).next_to(M, DOWN, buff=0.4)
            self.play(FadeIn(lab), run_time=0.6)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ matching
    def matching(self):
        tag = self.chapter("一 · 最大匹配")
        G, pos = teach_net()
        net = DiNet(G, pos)
        self.tn = (G, pos)
        with self.say("m1") as d:
            self.play(FadeIn(tag), FadeIn(net.group[1]), LaggedStart(*[GrowArrow(a) for a in net.arrows.values()], lag_ratio=0.08), run_time=d * 0.7)
        with self.say("m2") as d:
            self.play(net.arrows[(1, 2)].animate.set_color(RED), net.arrows[(1, 8)].animate.set_color(RED), run_time=0.8)
            x1 = T("共用起点", 26, RED).next_to(net.nodes[1], UP, buff=0.3)
            self.play(FadeIn(x1), run_time=0.5)
            self.play(net.arrows[(1, 2)].animate.set_color(MUTED), net.arrows[(1, 8)].animate.set_color(MUTED), FadeOut(x1), run_time=0.5)
            self.play(net.arrows[(1, 8)].animate.set_color(RED), net.arrows[(3, 8)].animate.set_color(RED), run_time=0.8)
            x2 = T("共用终点", 26, RED).next_to(net.nodes[8], RIGHT, buff=0.3)
            self.play(FadeIn(x2), run_time=0.5)
            self.play(net.arrows[(1, 8)].animate.set_color(MUTED), net.arrows[(3, 8)].animate.set_color(MUTED), FadeOut(x2), run_time=0.5)
        with self.say("m3") as d:
            n = net.nodes[3]
            inn = SurroundingRectangle(VGroup(net.arrows[(2, 3)]), color=GREEN, buff=0.05)
            out = SurroundingRectangle(VGroup(net.arrows[(3, 4)]), color=GREEN, buff=0.05)
            self.play(Indicate(n, color=GREEN), Create(inn), Create(out), run_time=1.4)
            self.play(FadeOut(inn), FadeOut(out), run_time=0.5)
        M = max_matching(G)
        assert len(M) == 6
        cnt = counter("匹配边", "0", GOLD).move_to(RIGHT * 4.6 + UP * 2.2)
        with self.say("m4") as d:
            self.play(FadeIn(cnt), run_time=0.4)
            for i, e in enumerate(MATCH):
                self.play(net.arrows[e].animate.set_color(GOLD).set_stroke(width=6),
                          Transform(cnt[1], T(str(i + 1), 40, GOLD, weight=BOLD).move_to(cnt[1])), run_time=(d - 0.6) / 6)
        drv = [v for v in G if v not in {b for _, b in MATCH}]
        assert sorted(drv) == [1, 8] and n_drivers(G) == 2
        with self.say("m5") as d:
            self.play(*[net.fill(v, GOLD, 0.35) for _, v in MATCH], run_time=1.0)
            self.play(*[net.fill(v, RED, 0.8) for v in drv], run_time=1.0)
        with self.say("m6") as d:
            f = MathTex(r"N_D=\max\big(N-|M^*|,\,1\big)", font_size=38).move_to(RIGHT * 4.1 + UP * 0.6)
            self.play(Write(f), run_time=1.4)
        with self.say("m6b") as d:
            f2 = MathTex(r"=8-6=2", font_size=44, color=RED).next_to(f, DOWN, buff=0.3).align_to(f, LEFT).shift(RIGHT * 0.5)
            self.play(Write(f2), run_time=1.0)
        with self.say("m7") as d:
            us = VGroup(*[VGroup(arrow(pos[v] + LEFT * 1.1 + UP * 0.5, pos[v], 0.32, RED, 4),
                                 MathTex(f"u_{i + 1}", color=RED, font_size=34).move_to(pos[v] + LEFT * 1.3 + UP * 0.7))
                          for i, v in enumerate(drv)])
            self.play(LaggedStart(*[FadeIn(u) for u in us], lag_ratio=0.3), run_time=1.4)
        self.mnet, self.us, self.mf = net, us, VGroup(f, f2, cnt)
        self.play(FadeOut(self.mf), run_time=0.6)

    # ------------------------------------------------------------------ paths & cycles
    def paths(self):
        tag = self.chapter("一 · 路径与环")
        old = [m for m in self.mobjects if isinstance(m, Text) and m is not tag]
        G, pos = self.tn
        net = self.mnet
        nonm = [e for e in G.edges() if e not in MATCH]
        with self.say("p1") as d:
            self.play(*[FadeOut(m) for m in old], FadeIn(tag), *[net.arrows[e].animate.set_opacity(0.15) for e in nonm], run_time=1.2)
            stem = SurroundingRectangle(VGroup(*[net.nodes[v] for v in (1, 2, 3, 4)]), color=BLUE, buff=0.15)
            stem2 = SurroundingRectangle(net.nodes[8], color=BLUE, buff=0.15)
            cyc = SurroundingRectangle(VGroup(*[net.nodes[v] for v in (5, 6, 7)]), color=VIOLET, buff=0.15)
            self.play(Create(stem), Create(stem2), run_time=1.0)
            self.play(Create(cyc), run_time=0.8)
            lbl = VGroup(T("路径", 26, BLUE).next_to(stem, UP, buff=0.1), T("环", 26, VIOLET).next_to(cyc, RIGHT, buff=0.15))
            self.play(FadeIn(lbl), run_time=0.5)
        with self.say("p2") as d:
            self.play(*[Indicate(self.us[i], color=RED) for i in range(2)], run_time=1.5)
        with self.say("p3") as d:
            sig = Dot(pos[1], radius=0.12, color=GOLD)
            self.play(FadeIn(sig), run_time=0.3)
            for v in (2, 3, 4):
                self.play(sig.animate.move_to(pos[v]), Flash(net.nodes[v], color=GOLD, line_length=0.15), run_time=d * 0.2)
            self.play(FadeOut(sig), run_time=0.3)
        with self.say("p4") as d:
            self.play(net.arrows[(1, 5)].animate.set_opacity(1).set_color(GREEN).set_stroke(width=6), run_time=1.0)
            sig = Dot(pos[1], radius=0.12, color=GREEN)
            self.play(FadeIn(sig), run_time=0.3)
            self.play(sig.animate.move_to(pos[5]), run_time=0.7)
            for v in (6, 7, 5):
                self.play(sig.animate.move_to(pos[v]), run_time=0.5)
            self.play(FadeOut(sig), run_time=0.3)
        with self.say("p5") as d:
            self.play(FadeOut(VGroup(stem, stem2, cyc, lbl)), run_time=0.8)
            fast = T("多项式时间", 34, GOLD, weight=BOLD).move_to(RIGHT * 4.0 + UP * 0.5)
            self.play(FadeIn(fast, shift=UP * 0.2), run_time=0.8)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)
        with self.say("p5b") as d:
            self.clip_on("matching_sweep_demo.mp4", "full", "本站交互演示：最大匹配与驱动节点", start=0.3)
        self.clip_off()

    # ------------------------------------------------------------------ hubs
    def hubs(self):
        with self.say("d0") as d:
            self.clip_on("yt_controllability_martino.mp4", "center", "视频：Mauro Martino · YouTube", start=20)
        self.clip_off()
        tag = self.chapter("二 · 驱动节点避开枢纽")
        G, pos = self.star(LEFT * 3.3, 2.1)
        net = DiNet(G, pos, r=0.28, labels=False)
        net.circ[0].scale(1.4)
        M = max_matching(G); D = drivers(G, M)
        assert len(D) == 6 and 0 in D
        with self.say("d1") as d:
            self.play(FadeIn(tag), FadeIn(net.group), run_time=1.0)
            (_, b), = M
            self.play(net.arrows[(0, b)].animate.set_color(GOLD).set_stroke(width=6), net.fill(b, GOLD, 0.4), run_time=1.0)
            self.play(*[net.fill(v, RED, 0.8) for v in D if v != 0], run_time=1.0)
        with self.say("d2") as d:
            self.play(net.fill(0, RED, 0.8), run_time=0.8)
            c = counter("驱动节点", "6 / 7", RED).move_to(RIGHT * 1.8 + UP * 1.5)
            self.play(FadeIn(c), run_time=0.6)
        self.play(FadeOut(net.group), FadeOut(c), run_time=0.6)
        N = 1000
        S = sf_digraph(N, 2, 2.2, seed=1)
        Dset = set(drivers(S, max_matching(S)))
        deg = dict(S.degree())
        grp = [("度 ≤ 2", [v for v in S if deg[v] <= 2]), ("度 3–9", [v for v in S if 3 <= deg[v] <= 9]), ("度 ≥ 10", [v for v in S if deg[v] >= 10])]
        fr = [np.mean([v in Dset for v in g]) for _, g in grp]
        assert fr[0] > 0.6 and fr[2] < 0.35 and fr[0] > fr[1] > fr[2], fr
        ax = Axes(x_range=[0, 3, 1], y_range=[0, 1, 0.5], x_length=6.5, y_length=4.0,
                  axis_config={"color": MUTED, "include_tip": False, "font_size": 24},
                  y_axis_config={"numbers_to_include": [0, 0.5, 1]}).move_to(DOWN * 0.4)
        yl = T("其中驱动节点的比例", 24, MUTED).rotate(PI / 2).next_to(ax.y_axis, LEFT, buff=0.3)
        bars = VGroup()
        for i, ((nm, g), f, c) in enumerate(zip(grp, fr, (BLUE, VIOLET, GOLD))):
            h = ax.c2p(0, f)[1] - ax.c2p(0, 0)[1]
            r = Rectangle(width=1.2, height=h, fill_color=c, fill_opacity=0.85, stroke_width=0).move_to(ax.c2p(i + 0.5, 0), aligned_edge=DOWN)
            bars.add(VGroup(r, T(nm, 24, INK).next_to(ax.c2p(i + 0.5, 0), DOWN, buff=0.2),
                            T(f"{f:.0%}", 26, c, weight=BOLD).next_to(r, UP, buff=0.1), T(f"{len(g)} 个", 20, MUTED)))
            bars[-1][3].next_to(bars[-1][1], DOWN, buff=0.08)
        with self.say("d3") as d:
            B = nx.barabasi_albert_graph(45, 1, seed=3)
            bp = fit(nx.kamada_kawai_layout(B), (-3.2, 3.2, -2.8, 2.4))
            sfnet = VGroup(VGroup(*[Line(bp[u], bp[v], color=MUTED, stroke_width=1.5, stroke_opacity=0.6) for u, v in B.edges()]),
                           VGroup(*[Dot(bp[v], radius=0.05 + 0.03 * B.degree(v), color=BLUE) for v in B]))
            self.play(FadeIn(sfnet), run_time=1.0)
            self.wait(d * 0.3)
            self.play(FadeOut(sfnet), run_time=0.5)
        with self.say("d3b") as d:
            self.play(Create(ax), FadeIn(yl), run_time=1.0)
            self.play(LaggedStart(*[FadeIn(b[1]) for b in bars], *[FadeIn(b[3]) for b in bars], lag_ratio=0.15), run_time=1.2)
        with self.say("d4") as d:
            for b in bars:
                self.play(GrowFromEdge(b[0], DOWN), FadeIn(b[2]), run_time=d * 0.2)
        with self.say("d4b") as d:
            why = T("每个节点只能匹配一个下游", 28, GOLD).to_edge(UP, buff=0.9).shift(RIGHT * 2.0)
            self.play(FadeIn(why, shift=DOWN * 0.2), Indicate(bars[2][0], color=GOLD), run_time=1.2)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ degree distribution
    def degree(self):
        tag = self.chapter("二 · 度分布决定可控性")
        icons = VGroup(*[T(s, 28, c) for s, c in (("基因调控", GREEN), ("食物网", GOLD), ("代谢", BLUE), ("神经元", VIOLET), ("互联网", INK))]
                       ).arrange(RIGHT, buff=0.6).move_to(DOWN * 0.4)
        cav = T("空腔方法：解析计算", 32, GOLD).next_to(icons, UP, buff=0.8)
        with self.say("n1") as d:
            self.play(FadeIn(tag), FadeIn(cav), run_time=1.0)
            self.play(LaggedStart(*[FadeIn(i, shift=UP * 0.2) for i in icons], lag_ratio=0.2), run_time=d * 0.5)
        self.play(FadeOut(icons), FadeOut(cav), run_time=0.6)
        N = 1000
        ks = [1, 1.5, 2, 3, 4, 6, 8]
        er = [n_drivers(nx.gnm_random_graph(N, int(k * N), directed=True, seed=1)) / N for k in ks]
        sf = [n_drivers(sf_digraph(N, k, 2.2, seed=1)) / N for k in ks]
        ax = Axes(x_range=[0, 16, 4], y_range=[0, 0.8, 0.2], x_length=6.0, y_length=4.4,
                  axis_config={"color": MUTED, "include_tip": False, "font_size": 22},
                  x_axis_config={"numbers_to_include": [0, 4, 8, 12, 16]},
                  y_axis_config={"numbers_to_include": [0, 0.2, 0.4, 0.6, 0.8]}).move_to(LEFT * 2.6 + DOWN * 0.3)
        xl = MathTex(r"\langle k\rangle", color=MUTED, font_size=32).next_to(ax.x_axis, DOWN, buff=0.35)
        yl = MathTex(r"n_D", color=MUTED, font_size=34).next_to(ax.y_axis, LEFT, buff=0.3)
        kk = [2 * k for k in ks]
        ce = ax.plot_line_graph(kk, er, line_color=MUTED, vertex_dot_radius=0.06, vertex_dot_style={"fill_color": MUTED}, stroke_width=4)
        cs = ax.plot_line_graph(kk, sf, line_color=BLUE, vertex_dot_radius=0.06, vertex_dot_style={"fill_color": BLUE}, stroke_width=4)
        le = VGroup(VGroup(Line(ORIGIN, RIGHT * 0.4, color=MUTED, stroke_width=4), T("随机网络", 22)).arrange(RIGHT, buff=0.15),
                    VGroup(Line(ORIGIN, RIGHT * 0.4, color=BLUE, stroke_width=4), T("无标度网络", 22)).arrange(RIGHT, buff=0.15)
                    ).arrange(DOWN, aligned_edge=LEFT).next_to(ax, UP, buff=0.1).align_to(ax, RIGHT)
        with self.say("n2") as d:
            self.play(Create(ax), FadeIn(xl), FadeIn(yl), run_time=d * 0.5)
        with self.say("n3") as d:
            self.play(Create(ce), FadeIn(le[0]), run_time=d * 0.4)
            self.play(Create(cs), FadeIn(le[1]), run_time=d * 0.4)
        with self.say("n3b") as d:
            self.play(Indicate(cs, color=BLUE), run_time=1.2)
        S = sf_digraph(N, 2, 2.2, seed=1)
        ins = [x for _, x in S.in_degree()]; outs = [x for _, x in S.out_degree()]
        cm = nx.DiGraph(nx.directed_configuration_model(ins, outs, seed=2)); cm.remove_edges_from(nx.selfloop_edges(cm))
        rd = nx.gnm_random_graph(N, S.number_of_edges(), directed=True, seed=2)
        v0, v1, v2 = n_drivers(S) / N, n_drivers(cm) / N, n_drivers(rd) / N
        assert abs(v0 - v1) < 0.03 and v0 - v2 > 0.2, (v0, v1, v2)
        bx = Axes(x_range=[0, 3, 1], y_range=[0, 0.8, 0.2], x_length=4.6, y_length=4.4,
                  axis_config={"color": MUTED, "include_tip": False, "font_size": 22},
                  y_axis_config={"numbers_to_include": [0, 0.2, 0.4, 0.6, 0.8]}).move_to(RIGHT * 3.9 + DOWN * 0.3)
        bars = VGroup()
        for i, (v, nm, c) in enumerate(((v0, "原网络", BLUE), (v1, "保持度", GREEN), (v2, "完全打乱", MUTED))):
            h = bx.c2p(0, v)[1] - bx.c2p(0, 0)[1]
            r = Rectangle(width=0.9, height=h, fill_color=c, fill_opacity=0.85, stroke_width=0).move_to(bx.c2p(i + 0.5, 0), aligned_edge=DOWN)
            bars.add(VGroup(r, T(nm, 22, INK).next_to(bx.c2p(i + 0.5, 0), DOWN, buff=0.2)))
        with self.say("n4") as d:
            self.play(Create(bx), FadeIn(bars[0]), run_time=1.0)
            self.play(FadeIn(bars[1], shift=UP * 0.2), run_time=0.8)
        with self.say("n4b") as d:
            self.play(FadeIn(bars[2], shift=UP * 0.2), run_time=0.8)
        with self.say("n5") as d:
            self.play(Indicate(bars[1], color=GREEN), run_time=1.2)
            tr = VGroup(T("基因调控：较高", 26, GREEN), T("部分社会网络：较低", 26, INK)).arrange(DOWN, aligned_edge=LEFT).to_corner(UR, buff=0.4)
            self.play(FadeOut(le), FadeIn(tr), run_time=1.0)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ meaning & limits
    def limits(self):
        tag = self.chapter("三 · 意义与局限")
        G, pos = teach_net()
        P = {v: p * 0.85 + LEFT * 1.6 for v, p in pos.items()}
        net = DiNet(G, P, r=0.24, fs=22)
        drug = VGroup(RoundedRectangle(width=0.9, height=0.4, corner_radius=0.2, color=GOLD, fill_color=GOLD, fill_opacity=0.5),
                      T("药", 22)).move_to(RIGHT * 3.8 + UP * 1.2)
        with self.say("l1") as d:
            self.play(FadeIn(tag), FadeIn(net.group), run_time=1.0)
            self.play(FadeIn(drug), run_time=0.6)
            self.play(drug.animate.move_to(P[1] + UP * 0.5), run_time=1.2)
        with self.say("l2") as d:
            q = T("结构可控 ≠ 实际可控", 36, RED, weight=BOLD).to_edge(DOWN, buff=0.5)
            self.play(Write(q), run_time=1.2)
        with self.say("l3") as d:
            ener = VGroup(T("未考虑：", 26, MUTED), T("控制能量", 30, GOLD), T("所需时间", 30, GOLD), T("非线性", 30, GOLD)).arrange(DOWN, buff=0.3).move_to(RIGHT * 4.6 + UP * 0.2)
            self.play(LaggedStart(*[FadeIn(e, shift=LEFT * 0.2) for e in ener], lag_ratio=0.4), run_time=d * 0.5)
        self.play(FadeOut(VGroup(q, ener, drug)), run_time=0.6)
        loops = VGroup(*[Circle(radius=0.2, color=VIOLET, stroke_width=3).move_to(P[v] + UP * 0.38 + RIGHT * 0.12) for v in G])
        with self.say("l4") as d:
            self.play(LaggedStart(*[Create(l) for l in loops], lag_ratio=0.1), run_time=d * 0.5)
        H = G.copy(); H.add_edges_from((v, v) for v in G)
        assert n_drivers(H) == 1 and n_drivers(G) == 2
        with self.say("l5") as d:
            self.play(loops.animate.set_color(GOLD), *[net.fill(v, GOLD, 0.35) for v in G], run_time=1.2)
            c = counter("驱动节点", "2 → 1", GOLD).move_to(RIGHT * 4.4 + UP * 1.2)
            self.play(FadeIn(c), run_time=0.6)
        with self.say("l6") as d:
            self.play(FadeOut(loops), FadeOut(c), *[net.reset(v) for v in G], run_time=0.8)
            A = MATCH
            B = [(1, 8), (2, 3), (3, 4), (5, 6), (6, 7), (7, 5)]
            for Ms, col in ((A, GOLD), (B, GREEN)):
                drv = [v for v in G if v not in {b for _, b in Ms}]
                anims = [a.animate.set_color(MUTED).set_stroke(width=3) for a in net.arrows.values()]
                self.play(*anims, *[net.reset(v) for v in G], run_time=0.4)
                self.play(*[net.arrows[e].animate.set_color(col).set_stroke(width=6) for e in Ms],
                          *[net.fill(v, RED, 0.8) for v in drv], run_time=1.0)
                lab = T("驱动：" + "、".join(map(str, sorted(drv))), 30, RED).move_to(RIGHT * 4.4 + (UP * 1.0 if col == GOLD else DOWN * 0.2))
                self.play(FadeIn(lab), run_time=0.5)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)
        with self.say("l7") as d:
            self.clip_on("yt_celegans_openworm.mp4", "center", "视频：OpenWorm · YouTube", start=15)
        self.clip_off()

    # ------------------------------------------------------------------ recap
    def recap(self):
        with self.say("r1") as d:
            head = T("三个要点", 40, INK, weight=BOLD).to_edge(UP, buff=0.7)
            self.play(Write(head), run_time=0.8)
        items = [("r2", BLUE, "驱动节点数 = 节点数 − 最大匹配"),
                 ("r3", GOLD, "度分布决定可控性；驱动节点避开枢纽"),
                 ("r4", RED, "前提：线性、结构可控、忽略自环")]
        rows = VGroup()
        for i, (k, c, s) in enumerate(items):
            num = Circle(radius=0.32, color=c, fill_opacity=0.18, stroke_width=3).add(T(str(i + 1), 28, c, weight=BOLD))
            rows.add(VGroup(num, T(s, 32, INK)).arrange(RIGHT, buff=0.4))
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.6).next_to(head, DOWN, buff=0.8)
        for (k, _, _), row in zip(items, rows):
            with self.say(k) as d:
                self.play(FadeIn(row, shift=RIGHT * 0.3), run_time=0.8)
        self.wait(1.0)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=1.0)
