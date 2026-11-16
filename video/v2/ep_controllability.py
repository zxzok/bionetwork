"""Animated explainer: 网络可控性与稳定性 (Kalman, maximum matching, driver nodes, control cores, energy, May)."""
import itertools

import networkx as nx
import numpy as np
from networkx.algorithms import bipartite

from common import *  # noqa: F401,F403
from bhelp import NetView, fit, counter, axes, arrow_between, parts_slide, recap_slide, show_clip

TITLE = "控制一个网络需要几个开关"

LINES = {
    # hook
    "h1": "我们先看细胞里的一小段调控网络。上面这个是转录因子——一种开关蛋白，能调控别的基因。它同时调控着下面两个基因。",
    "h1b": "画面是转录过程的动画：基因上的信息，被一段段抄写下来，再去指导蛋白质的合成。",
    "h2": "我们想把细胞从疾病状态推回健康状态：让左边的基因升高，右边的基因降低。绿色虚线，就是目标。",
    "h3": "直觉上，应该抓住连接最多的那个节点。我们就在转录因子上，施加一个外部输入，也就是这个红色箭头。",
    "h4": "可无论输入怎么变，两个基因总是同涨同落，永远到不了目标。",
    "h5": "所以，控制一个网络，开关的数目和位置都有讲究。这一期，我们就把这件事讲清楚。",
    "q0": "这一期分三部分来讲。",
    "q1": "第一部分，什么叫可控，怎样判断。",
    "q2": "第二部分，怎样只看网络结构，找出最少需要的开关。",
    "q3": "第三部分，控制要付出多大代价，以及两种不同的稳定。",
    # linear system
    "l1": "先看第一部分。我们把网络写成一个线性方程。x 是所有节点的状态，A 描述节点之间谁影响谁，B 说明外部输入加在哪些节点上。",
    "l1b": "等号左边，是状态变化的速度。它由两部分组成：网络内部的相互影响，加上外部的输入。",
    "l2": "【慢】如果能把系统从任意状态，推到任意目标状态，就说它是可控的。直接接收输入的节点，叫驱动节点。",
    "l3": "先看一条链：输入推动第一个节点，它再推第二个，第二个再推第三个。下面三根柱子，是三个节点的状态，它们可以各自摆到不同的位置。一个输入就够了。",
    "l4": "再看星形：两个下游节点，收到的是同一个信号的不同倍数。右边的柱子里，第三根永远是第二根的两倍，状态被锁在一个平面里。",
    "l5": "卡尔曼判据把这件事写成矩阵：把 B、A 乘 B、A 的平方乘 B 依次排开，排出的矩阵满秩，就可控。",
    "l5b": "秩，可以理解成这个矩阵里有几个真正独立的方向。星形这里，第三列全是零，秩只有二，比节点数三少，所以不可控。",
    "l6": "可真实生物网络的权重常常未知，网络一大，这个计算也很难做。",
    # matching
    "m1": "下面进入第二部分。2011年，《自然》杂志上的一项研究给出了一个漂亮的办法：只看网络的连接结构，把找驱动节点变成一个匹配问题。",
    "m2": "匹配，是一组有向边，任意两条既不共享起点，也不共享终点。黄色这两条可以同时选；红色这条和上面那条共享起点，就不行。",
    "m3": "边数最多的匹配，叫最大匹配，就是这些黄色的边。被匹配边指向的节点，叫匹配节点，涂成了蓝色。",
    "m4": "没有被匹配的节点，涂成红色，就是必须直接施加输入的驱动节点。",
    "m4b": "右边的式子说：驱动节点数，等于节点总数，减去最大匹配的边数。这里九个节点，七条匹配边，所以需要两个驱动节点。",
    "m5": "【慢】每条匹配边，是控制信号传递链上的一环。网络被拆成几条互不相交的路径，每条路径的起点，都需要一个输入。",
    "m6": "回到星形：中心只能匹配一个下游，另一个下游只能单独驱动，所以一共需要两个输入。",
    # drivers vs hubs
    "d1": "这个方法带来了几个反直觉的结论。第一，驱动节点往往不是枢纽，也就是连接最多的节点。红色是驱动节点，画了黄圈的是枢纽。",
    "d2": "在一千个节点的无标度网络上，驱动节点平均只有三条左右的连接，而全网平均是六条。",
    "d3": "因为一个枢纽虽然能影响很多下游，却只能和其中一个匹配。剩下的下游，都得另找输入。",
    "d4": "第二，网络越稀疏，越难控制。这张图，横轴是平均连接数，纵轴是驱动节点的比例。在随机网络里，平均连接数一增加，驱动节点的比例就迅速下降。",
    "d5": "【慢】第三，连接越不均匀，越难控制。平均连接数同样是三，无标度网络需要的驱动节点，是随机网络的好几倍。",
    "d6": "基因调控网络里，许多靶基因只接受调控，不调控别人，所以需要的驱动节点比例相对较高。",
    # non-uniqueness, control cores
    "u1": "还有一个细节：最大匹配往往不唯一。",
    "u2": "换一种匹配，驱动节点就换了一批，但数目始终不变，右上角一直是二。",
    "u3": "于是，一个节点在所有可能的方案里扮演什么角色，就成了后续研究的问题。研究者提出了输入图和交换定理，不用一一列举，就能找出所有可能的驱动节点。",
    "u4": "进一步，把控制方案看成一组控制路径。有些节点，在任何方案里都位于路径中间，负责传递信号——它们叫控制核心点，就是黄色的这些。",
    "u5": "在一张七千多个基因的调控网络里，一个控制方案就要四成多的基因作驱动，所有方案合起来超过七成，而控制核心点不到一成。",
    "u6": "候选少得多，更适合作为药物靶点的筛选起点。当然，这些都是计算预测，还需要实验验证。",
    # energy
    "g1": "最后是第三部分。理论上可控，不代表实际上容易控制。",
    "g2": "这张小网络，只在一个节点上施加输入，系统依然可控。我们来算一算，把状态推向不同方向，各需要多少能量。",
    "g3": "右边每根柱子，代表一个方向的可达程度，越往下越难推动。纵轴是对数刻度，标出的每一档，相差一万倍。",
    "g3b": "【慢】最容易推动的方向和最难推动的方向，所需能量相差十个数量级以上。",
    "g4": "脑网络研究也遇到了这个问题：单个脑区理论上能控制全脑，但所需的能量大到几乎不可能实现。",
    "g5": "对大脑施加输入，临床上的一种方式是深部脑刺激：把电极植入脑内，用电脉冲刺激特定的区域。",
    # stability
    "s1": "下面要区分两种稳定。第一种叫结构鲁棒性：删掉一些节点以后，网络还连不连通。灰色的是被切断的碎片。",
    "s2": "第二种叫动力学稳定性：状态受到小扰动以后，能不能回到原来的平衡。就像碗底的小球，推一下，它还会滚回来。",
    "s3": "1972年，生态学家梅研究了随机构造的大系统。判断是否稳定，要看描述这个系统的雅可比矩阵，它的特征值是否都落在虚轴左边。",
    "s3b": "这张图是复平面，横轴是特征值的实部，纵轴是虚部。红线是虚轴，左边的绿色区域代表稳定。",
    "s4": "物种少、连接稀的时候，这些黄点，也就是特征值，都在左边，系统稳定。",
    "s5": "规模越大、连接越密，这团特征值散得越开。一旦越过虚轴，变成红色，系统就失稳了。",
    "s5b": "梅给出的条件写在右下角：相互作用的强度，乘以物种数和连接概率乘积的平方根，要小于一。",
    "s6": "【慢】真实的生物系统并非随机构造。它们靠模块化、冗余和负反馈，在复杂中保持了稳定。",
    # recap
    "z1": "好，我们来总结一下。",
    "z2": "第一，结构可控性只看连接结构，最大匹配之外的节点，就是驱动节点。",
    "z3": "第二，驱动节点往往避开枢纽，稀疏而不均匀的网络更难控制。",
    "z4": "第三，可控不等于容易控制；结构鲁棒和动力学稳定，也要分开来看。",
    "z5": "这个专题的知识页面里，有画面上的这个交互演示。滑块调的是平均出度，也就是平均每个节点指出去几条边。",
    "z5b": "平均出度小的时候，红色的驱动节点很多；连接变密以后，驱动节点就少了。",
}

DRV = RED


def max_matching(D):
    """Maximum matching of a directed graph (as a set of edges) via the bipartite out/in split."""
    outs = [("o", u) for u in D]
    B = nx.Graph()
    B.add_nodes_from(outs, bipartite=0)
    B.add_nodes_from([("i", v) for v in D], bipartite=1)
    B.add_edges_from((("o", u), ("i", v)) for u, v in D.edges())
    M = bipartite.hopcroft_karp_matching(B, top_nodes=outs)
    return {(a[1], b[1]) for a, b in M.items() if a[0] == "o"}


def drivers_of(D, M):
    matched = {v for _, v in M}
    dr = [v for v in D if v not in matched]
    return dr if dr else [next(iter(D))]


def all_max_matchings(D):
    E = list(D.edges())
    best = len(max_matching(D))
    out = []
    for comb in itertools.combinations(E, best):
        if len({u for u, _ in comb}) == best and len({v for _, v in comb}) == best:
            out.append(set(comb))
    return out


def sf_dir(N, g, seed, kavg=3):
    rng = np.random.default_rng(seed)
    w = np.arange(1, N + 1) ** (-1 / (g - 1)); w /= w.sum()
    D = nx.DiGraph(); D.add_nodes_from(range(N))
    m = int(kavg * N)
    a = rng.choice(N, size=3 * m, p=w); b = rng.choice(N, size=3 * m, p=rng.permutation(w))
    for u, v in zip(a, b):
        if u != v:
            D.add_edge(int(u), int(v))
        if D.number_of_edges() >= m:
            break
    return D


# small hand-made directed network for the matching chapter
SMALL_E = [(0, 1), (0, 2), (0, 3), (1, 4), (2, 4), (3, 5), (4, 6), (5, 6), (6, 7), (5, 8), (8, 7), (2, 3), (1, 2)]
SMALL_P = {0: (-5.4, 0.3), 1: (-3.6, 1.8), 2: (-3.6, 0.3), 3: (-3.6, -1.2), 4: (-1.6, 1.0), 5: (-1.6, -1.6),
           6: (0.4, 0.2), 7: (2.0, 1.2), 8: (0.4, -2.2)}


class Episode(Narrated):
    LINES = LINES

    def construct(self):
        self.hook()
        parts_slide(self, ["一  什么叫可控：线性系统与卡尔曼判据", "二  最大匹配：最少的开关在哪里", "三  控制的代价与两种稳定"])
        self.linear()
        self.matching()
        self.hubs()
        self.cores()
        self.energy()
        self.stability()
        self.recap()

    def fade_all(self, rt=0.8, keep=()):
        self.play(*[FadeOut(m) for m in self.mobjects if m not in keep], run_time=rt)

    # ------------------------------------------------------------------ hook
    def hook(self):
        P = [UP * 2.4, LEFT * 2.4 + UP * 0.2, RIGHT * 2.4 + UP * 0.2]
        nodes = VGroup(*[Circle(radius=0.42, color=c, fill_opacity=0.25, stroke_width=3).move_to(p)
                         for c, p in zip((GOLD, BLUE, BLUE), P)])
        names = VGroup(T("转录因子", 22, GOLD).next_to(nodes[0], UP, buff=0.15),
                       T("基因甲", 22, BLUE).next_to(nodes[1], LEFT, buff=0.15),
                       T("基因乙", 22, BLUE).next_to(nodes[2], RIGHT, buff=0.15))
        ar = VGroup(arrow_between(P[0], P[1], 0.45, 0.45, INK), arrow_between(P[0], P[2], 0.45, 0.45, INK))
        # level bars under the two genes
        base = [P[1] + DOWN * 2.2, P[2] + DOWN * 2.2]
        zero = VGroup(*[Line(b + LEFT * 0.6, b + RIGHT * 0.6, color=MUTED) for b in base])
        bars = VGroup(*[Rectangle(width=0.6, height=0.01, fill_color=BLUE, fill_opacity=0.9, stroke_width=0).move_to(b, aligned_edge=DOWN) for b in base])
        tgt = VGroup(DashedLine(base[0] + UP * 1.1 + LEFT * 0.6, base[0] + UP * 1.1 + RIGHT * 0.6, color=GREEN),
                     DashedLine(base[1] + DOWN * 0.8 + LEFT * 0.6, base[1] + DOWN * 0.8 + RIGHT * 0.6, color=GREEN))
        tl = VGroup(T("目标：升高", 20, GREEN).next_to(tgt[0], LEFT, buff=0.15), T("目标：降低", 20, GREEN).next_to(tgt[1], RIGHT, buff=0.15))
        with self.say("h1") as d:
            self.play(LaggedStart(*[GrowFromCenter(n) for n in nodes], lag_ratio=0.2), FadeIn(names), run_time=1.2)
            self.play(GrowArrow(ar[0]), GrowArrow(ar[1]), run_time=0.8)
            self.play(Create(zero), run_time=0.5)
        keep = [m for m in self.mobjects]
        show_clip(self, "h1b", "yt_transcription_dnalc.mp4", "center", "视频：DNA Learning Center · YouTube", start=20, min_len=7)
        self.play(*[FadeIn(m) for m in keep], run_time=0.6)
        with self.say("h2") as d:
            self.play(Create(tgt), FadeIn(tl), run_time=1.2)
        inp = Arrow(P[0] + UP * 0.6 + LEFT * 2.0, P[0] + LEFT * 0.45 + UP * 0.1, buff=0, color=RED, stroke_width=6)
        ul = MathTex("u(t)", font_size=36, color=RED).next_to(inp.get_start(), LEFT, buff=0.1)
        with self.say("h3") as d:
            self.play(GrowArrow(inp), FadeIn(ul), Indicate(nodes[0], color=GOLD), run_time=1.2)

        def drive(dur, f):
            def upd(m, a):
                s = f(a)
                for i, (b, k) in enumerate(zip(base, (1.0, 0.7))):
                    h = s * k
                    bars[i].stretch_to_fit_height(max(0.01, abs(h)))
                    bars[i].move_to(b, aligned_edge=DOWN if h >= 0 else UP)
                nodes[0].set_fill(opacity=0.25 + 0.5 * abs(np.tanh(s)))
            return UpdateFromAlphaFunc(bars, upd, run_time=dur, rate_func=linear)
        self.add(bars)
        with self.say("h4") as d:
            self.play(drive(d, lambda a: 1.4 * np.sin(2 * np.pi * 1.5 * a) * (0.6 + 0.4 * a)))
            x = Cross(tgt[1], stroke_color=RED, scale_factor=0.6)
            self.play(Create(x), run_time=0.5)
        with self.say("h5") as d:
            q = T("开关的数目和位置，都有讲究", 48, GOLD, weight=BOLD)
            self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.6)
            self.play(Write(q), run_time=1.2)
        self.fade_all()

    # ------------------------------------------------------------------ linear system
    def linear(self):
        tag = self.chapter("一  什么叫可控")
        eq = MathTex(r"\dot{\mathbf x}", "=", "A", r"\mathbf x", "+", "B", r"\mathbf u", font_size=64)
        eq[2].set_color(BLUE); eq[5].set_color(RED)
        eq.move_to(UP * 1.2)
        la = T("谁影响谁", 24, BLUE).next_to(eq[2], DOWN, buff=0.5)
        lb = T("输入加在哪", 24, RED).next_to(eq[5], DOWN, buff=0.5)
        with self.say("l1") as d:
            self.play(FadeIn(tag), Write(eq), run_time=1.4)
            self.play(FadeIn(la, shift=UP * 0.2), run_time=0.6)
            self.play(FadeIn(lb, shift=UP * 0.2), run_time=0.6)
        with self.say("l1b") as d:
            b0 = Brace(eq[0], UP, color=INK); t0 = T("状态变化的速度", 22).next_to(b0, UP, buff=0.08)
            b1 = Brace(eq[2:4], UP, color=BLUE); t1 = T("内部相互影响", 22, BLUE).next_to(b1, UP, buff=0.08)
            b2 = Brace(eq[5:7], UP, color=RED); t2 = T("外部输入", 22, RED).next_to(b2, UP, buff=0.08)
            self.play(GrowFromCenter(b0), FadeIn(t0), run_time=0.7)
            self.play(GrowFromCenter(b1), FadeIn(t1), run_time=0.7)
            self.play(GrowFromCenter(b2), FadeIn(t2), run_time=0.7)
        self.play(*[FadeOut(x) for x in (b0, t0, b1, t1, b2, t2)], run_time=0.4)
        with self.say("l2") as d:
            s0 = Dot(LEFT * 3 + DOWN * 1.8, color=MUTED, radius=0.12)
            s1 = Dot(RIGHT * 3 + DOWN * 1.8, color=GREEN, radius=0.12)
            path = ArcBetweenPoints(s0.get_center(), s1.get_center(), angle=-PI / 3, color=GOLD)
            self.play(FadeIn(s0), FadeIn(s1), FadeIn(T("任意状态", 22, MUTED).next_to(s0, DOWN)), FadeIn(T("任意目标", 22, GREEN).next_to(s1, DOWN)), run_time=0.8)
            mover = Dot(s0.get_center(), color=GOLD, radius=0.1)
            self.play(MoveAlongPath(mover, path), Create(path), run_time=1.6)
        self.fade_all(keep=(tag,))

        # chain vs star with 3D-ish state as three bars
        def tri(P, E, title, x0):
            nd = VGroup(*[Circle(radius=0.3, color=INK, stroke_width=2.5).move_to(p) for p in P])
            nums = VGroup(*[T(str(i + 1), 24).move_to(p) for i, p in enumerate(P)])
            ar = VGroup(*[arrow_between(P[u], P[v], 0.33, 0.33, MUTED) for u, v in E])
            inp = Arrow(P[0] + LEFT * 1.0 + UP * 0.6, P[0] + LEFT * 0.3, buff=0, color=RED, stroke_width=5)
            tt = T(title, 28).move_to([x0, 2.9, 0])
            return VGroup(tt, ar, nd, nums, inp)
        Pc = [np.array([x, 1.2, 0]) for x in (-5.4, -3.9, -2.4)]
        Ps = [np.array([2.6, 1.2, 0]), np.array([4.4, 2.0, 0]), np.array([4.4, 0.4, 0])]
        chain = tri(Pc, [(0, 1), (1, 2)], "链", -3.9)
        star = tri(Ps, [(0, 1), (0, 2)], "星", 3.6)

        def state_bars(x0):
            base = np.array([x0, -2.8, 0])
            bs = VGroup(*[Rectangle(width=0.5, height=0.01, fill_color=c, fill_opacity=0.9, stroke_width=0).move_to(base + RIGHT * (i - 1) * 0.8, aligned_edge=DOWN)
                          for i, c in enumerate((GOLD, BLUE, GREEN))])
            ln = Line(base + LEFT * 1.4, base + RIGHT * 1.4, color=MUTED)
            lab = VGroup(*[MathTex(f"x_{i + 1}", font_size=26, color=MUTED).next_to(base + RIGHT * (i - 1) * 0.8, DOWN, buff=0.12) for i in range(3)])
            return bs, VGroup(ln, lab), base

        bc, gc, basec = state_bars(-3.9)
        bs_, gs, bases = state_bars(3.6)

        def setb(bs, base, hs):
            for i, (b, h) in enumerate(zip(bs, hs)):
                b.stretch_to_fit_height(max(0.01, abs(h)))
                b.move_to(base + RIGHT * (i - 1) * 0.8, aligned_edge=DOWN if h >= 0 else UP)
        with self.say("l3") as d:
            self.play(FadeIn(chain), Create(gc), run_time=1.0)
            self.add(bc)
            # independent wiggles: different shapes reachable
            seq = [(1.2, 0.0, 0.0), (0.4, 1.0, 0.0), (-0.6, 0.2, 1.2), (0.8, -0.9, 0.5), (0.3, 1.1, -0.8)]
            for hs in seq:
                prev = [b.height * (1 if b.get_bottom()[1] >= basec[1] - 1e-3 else -1) for b in bc]
                self.play(UpdateFromAlphaFunc(bc, lambda m, a, hs=hs, prev=prev: setb(bc, basec, [p + (h - p) * smooth(a) for p, h in zip(prev, hs)])),
                          run_time=max(0.5, (d - 1.2) / len(seq)))
        with self.say("l4") as d:
            self.play(FadeIn(star), Create(gs), run_time=1.0)
            self.add(bs_)
            seq = [(1.0, 0.0, 0.0), (0.2, 0.8, 1.6), (-0.6, -0.5, -1.0), (0.5, 0.6, 1.2)]
            for hs in seq:
                prev = [b.height * (1 if b.get_bottom()[1] >= bases[1] - 1e-3 else -1) for b in bs_]
                self.play(UpdateFromAlphaFunc(bs_, lambda m, a, hs=hs, prev=prev: setb(bs_, bases, [p + (h - p) * smooth(a) for p, h in zip(prev, hs)])),
                          run_time=max(0.5, (d - 1.2) / len(seq)))
            lock = MathTex("x_3 = 2x_2", font_size=34, color=RED).next_to(gs, RIGHT, buff=0.2).shift(UP * 0.5)
            self.play(FadeIn(lock), run_time=0.4)
        self.fade_all(keep=(tag,))
        with self.say("l5") as d:
            k = MathTex(r"\mathcal C=[\,B,\ AB,\ A^2B\,]", font_size=52).move_to(UP * 2.0)
            M = MathTex(r"\begin{pmatrix}1&0&0\\0&1&0\\0&2&0\end{pmatrix}", font_size=52).move_to(LEFT * 1.2 + DOWN * 0.4)
            r = MathTex(r"\operatorname{rank}=2<3", font_size=48, color=RED).next_to(M, RIGHT, buff=0.8)
            self.play(Write(k), run_time=1.2)
            self.play(FadeIn(M), run_time=1.0)
            col3 = SurroundingRectangle(M, color=RED, buff=0.05).stretch_to_fit_width(0.5).move_to(M.get_right() + LEFT * 0.55)
        with self.say("l5b") as d:
            self.play(Create(col3), run_time=0.8)
            self.play(Write(r), run_time=1.0)
        with self.say("l6") as d:
            big = MathTex(r"N=10^4", font_size=44, color=MUTED).to_edge(DOWN, buff=0.8)
            qs = T("权重常常未知", 32, GOLD).next_to(big, UP, buff=0.3)
            self.play(VGroup(k, M, r, col3).animate.set_opacity(0.3), FadeIn(qs), FadeIn(big), run_time=1.2)
        self.fade_all()

    # ------------------------------------------------------------------ matching
    def matching(self):
        tag = self.chapter("二  最大匹配：驱动节点")
        D = nx.DiGraph(SMALL_E)
        P = {v: np.array([*SMALL_P[v], 0]) + RIGHT * 0.9 for v in D}
        nd = {v: Circle(radius=0.28, color=INK, stroke_width=2.5, fill_color=BG, fill_opacity=1).move_to(P[v]) for v in D}
        ar = {e: arrow_between(P[e[0]], P[e[1]], 0.3, 0.3, MUTED, sw=2.5) for e in D.edges()}
        with self.say("m1") as d:
            self.play(FadeIn(tag), LaggedStart(*[GrowFromCenter(c) for c in nd.values()], lag_ratio=0.08), run_time=1.2)
            self.play(LaggedStart(*[GrowArrow(a) for a in ar.values()], lag_ratio=0.06), run_time=1.4)
        M = max_matching(D)
        drv = drivers_of(D, M)
        self.match = (D, M, drv)
        # m2: show a valid pair and an invalid pair
        with self.say("m2") as d:
            ok = [(0, 1), (2, 4)]
            self.play(*[ar[e].animate.set_color(GOLD).set_stroke(width=5) for e in ok], run_time=0.8)
            bad = [(0, 1), (0, 2)]
            self.play(ar[(0, 2)].animate.set_color(RED).set_stroke(width=5), run_time=0.6)
            x = Cross(nd[0], stroke_color=RED, scale_factor=1.3)
            self.play(Create(x), run_time=0.5)
            self.play(FadeOut(x), *[ar[e].animate.set_color(MUTED).set_stroke(width=2.5) for e in set(ok + bad)], run_time=0.6)
        with self.say("m3") as d:
            self.play(LaggedStart(*[ar[e].animate.set_color(GOLD).set_stroke(width=5) for e in M], lag_ratio=0.15), run_time=d * 0.45)
            self.play(*[nd[v].animate.set_fill(BLUE, opacity=0.6) for _, v in M], run_time=0.8)
        mcount = counter("最大匹配", f"{len(M)} 条边", GOLD, vs=32).move_to(RIGHT * 5.3 + UP * 2.2)
        with self.say("m4") as d:
            self.play(FadeIn(mcount), run_time=0.6)
            inps = VGroup(*[Arrow(P[v] + LEFT * 0.9 + UP * 0.7, P[v] + LEFT * 0.25 + UP * 0.2, buff=0, color=DRV, stroke_width=5) for v in drv])
            self.play(*[nd[v].animate.set_fill(DRV, opacity=0.8) for v in drv], LaggedStart(*[GrowArrow(a) for a in inps], lag_ratio=0.2), run_time=1.2)
            nd_c = counter("驱动节点", f"{len(drv)} 个", DRV, vs=32).next_to(mcount, DOWN, buff=0.4)
            self.play(FadeIn(nd_c), run_time=0.8)
        with self.say("m4b") as d:
            f = MathTex(r"N_D=N-|M^*|", font_size=36).next_to(nd_c, DOWN, buff=0.4)
            fx = MathTex(r"2=9-7", font_size=36, color=GOLD).next_to(f, DOWN, buff=0.3)
            self.play(Write(f), run_time=1.0)
            self.play(Write(fx), run_time=0.8)
        # m5: decompose into paths
        Hm = nx.DiGraph(list(M)); Hm.add_nodes_from(D)
        paths = []
        for s in drv:
            p = [s]
            while list(Hm.successors(p[-1])):
                p.append(next(iter(Hm.successors(p[-1]))))
            paths.append(p)
        cols = [RED, GREEN, VIOLET, BLUE]
        with self.say("m5") as d:
            self.play(*[a.animate.set_opacity(0.15) for e, a in ar.items() if e not in M], run_time=0.6)
            for p, c in zip(paths, cols):
                es = [ar[(p[i], p[i + 1])] for i in range(len(p) - 1)]
                self.play(*[e.animate.set_color(c) for e in es], *[nd[v].animate.set_stroke(c, width=5) for v in p], run_time=max(0.6, d * 0.6 / len(paths)))
        self.fade_all(keep=(tag,))
        with self.say("m6") as d:
            Ps = [LEFT * 1.5, RIGHT * 1.2 + UP * 1.3, RIGHT * 1.2 + DOWN * 1.3]
            c = VGroup(*[Circle(radius=0.32, color=INK, stroke_width=2.5).move_to(p) for p in Ps])
            a1 = arrow_between(Ps[0], Ps[1], 0.35, 0.35, GOLD, sw=5)
            a2 = arrow_between(Ps[0], Ps[2], 0.35, 0.35, MUTED, sw=2.5)
            self.play(FadeIn(c), GrowArrow(a1), GrowArrow(a2), run_time=1.0)
            self.play(c[0].animate.set_fill(DRV, opacity=0.8), c[2].animate.set_fill(DRV, opacity=0.8), c[1].animate.set_fill(BLUE, opacity=0.6), run_time=0.8)
            two = counter("驱动节点", "2 个", DRV, vs=36).move_to(RIGHT * 4.2)
            self.play(FadeIn(two), run_time=0.6)
        self.fade_all()

    # ------------------------------------------------------------------ drivers avoid hubs
    def hubs(self):
        tag = self.chapter("二  最大匹配：驱动节点躲开枢纽")
        Ds = sf_dir(60, 2.3, 3, kavg=1.6)
        Ds.remove_nodes_from([v for v in list(Ds) if Ds.degree(v) == 0])
        U = Ds.to_undirected()
        pos = fit(nx.kamada_kawai_layout(U), (-6.4, -0.6, -3.0, 2.7))
        deg = dict(Ds.degree())
        dots = {v: Dot(pos[v], radius=0.05 + 0.025 * np.sqrt(deg[v]), color=BLUE) for v in Ds}
        arrs = VGroup(*[arrow_between(pos[u], pos[v], dots[u].radius, dots[v].radius + 0.02, MUTED, sw=1.5, tip=0.1).set_opacity(0.6) for u, v in Ds.edges()])
        Ms = max_matching(Ds)
        dr = drivers_of(Ds, Ms)
        with self.say("d1") as d:
            self.play(FadeIn(tag), FadeIn(arrs), FadeIn(VGroup(*dots.values())), run_time=1.2)
            self.play(*[dots[v].animate.set_color(DRV) for v in dr], run_time=1.0)
            hubs = sorted(Ds, key=deg.get, reverse=True)[:3]
            rings = VGroup(*[Circle(radius=dots[h].radius + 0.12, color=GOLD, stroke_width=3).move_to(dots[h]) for h in hubs])
            self.play(Create(rings), run_time=0.8)
        Db = sf_dir(1000, 2.5, 1)
        Mb = max_matching(Db)
        drb = drivers_of(Db, Mb)
        degb = dict(Db.degree())
        kd, ka = np.mean([degb[v] for v in drb]), np.mean(list(degb.values()))
        with self.say("d2") as d:
            c1 = counter("驱动节点的平均度", f"{kd:.1f}", DRV, vs=40)
            c2 = counter("全网平均度", f"{ka:.1f}", BLUE, vs=40)
            VGroup(c1, c2).arrange(DOWN, buff=0.7).move_to(RIGHT * 3.6)
            self.play(FadeIn(c1, shift=UP * 0.2), run_time=0.8)
            self.play(FadeIn(c2, shift=UP * 0.2), run_time=0.8)
        with self.say("d3") as d:
            h = hubs[0]
            outs = list(Ds.successors(h))
            ea = [a for a, (u, v) in zip(arrs, Ds.edges()) if u == h]
            self.play(*[a.animate.set_color(GOLD).set_opacity(1) for a in ea], run_time=0.8)
            mt = [a for a, (u, v) in zip(arrs, Ds.edges()) if u == h and (u, v) in Ms]
            self.play(*[a.animate.set_color(GREEN).set_stroke(width=4) for a in mt], run_time=0.8)
        self.fade_all(keep=(tag,))
        # n_D vs <k> for directed ER
        N = 1000
        ks = [1, 1.5, 2, 2.5, 3, 4, 5, 6]
        nds = []
        for k in ks:
            nds.append(np.mean([len(drivers_of(G, max_matching(G))) / N for G in
                                (nx.gnm_random_graph(N, int(k * N), seed=s, directed=True) for s in range(2))]))
        ax = axes([0, 6, 1], [0, 0.6, 0.2], 6.4, 4.2, xn=[0, 2, 4, 6], yn=[0, 0.2, 0.4, 0.6]).move_to(LEFT * 2.6 + DOWN * 0.3)
        xl = T("平均度", 22, MUTED).next_to(ax.x_axis, DOWN, buff=0.35)
        yl = T("驱动节点比例", 22, MUTED).rotate(PI / 2).next_to(ax.y_axis, LEFT, buff=0.35)
        cv = ax.plot_line_graph(ks, nds, line_color=BLUE, add_vertex_dots=True, vertex_dot_radius=0.06, stroke_width=4)
        with self.say("d4") as d:
            self.play(Create(ax), FadeIn(xl), FadeIn(yl), run_time=1.0)
            self.play(Create(cv), run_time=d * 0.5)
        Ge = nx.gnm_random_graph(N, 3 * N, seed=1, directed=True)
        n_er = len(drivers_of(Ge, max_matching(Ge))) / N
        n_sf = len(drb) / N
        self.ctrl_vals = (kd, ka, n_er, n_sf)
        with self.say("d5") as d:
            b = axes([0, 3, 1], [0, 0.4, 0.1], 3.6, 3.6, yn=[0, 0.2, 0.4]).move_to(RIGHT * 4.0 + DOWN * 0.3)
            self.play(Create(b), run_time=0.6)
            for x, val, c, nm in ((1, n_er, MUTED, "随机网络"), (2, n_sf, DRV, "无标度")):
                r = Rectangle(width=0.8, height=b.c2p(0, val)[1] - b.c2p(0, 0)[1], fill_color=c, fill_opacity=0.9, stroke_width=0).move_to(b.c2p(x, 0), aligned_edge=DOWN)
                self.play(GrowFromEdge(r, DOWN), FadeIn(T(f"{val * 100:.0f}%", 24, c, weight=BOLD).next_to(r, UP, buff=0.08)),
                          FadeIn(T(nm, 20).next_to(b.c2p(x, 0), DOWN, buff=0.15)), run_time=1.0)
            kk = T("平均度都是 3", 20, MUTED).next_to(b, UP, buff=0.2)
            self.play(FadeIn(kk), run_time=0.5)
        self.fade_all(keep=(tag,))
        with self.say("d6") as d:
            tf = Circle(radius=0.32, color=GOLD, fill_opacity=0.3).move_to(UP * 1.6)
            tgts = VGroup(*[Circle(radius=0.22, color=BLUE, fill_opacity=0.3).move_to([x, -1.2, 0]) for x in np.linspace(-4, 4, 7)])
            arrs2 = VGroup(*[arrow_between(tf.get_center(), t.get_center(), 0.34, 0.26, MUTED, sw=2) for t in tgts])
            self.play(GrowFromCenter(tf), LaggedStart(*[GrowArrow(a) for a in arrs2], lag_ratio=0.08), FadeIn(tgts), run_time=1.4)
            self.play(*[t.animate.set_fill(DRV, opacity=0.7) for t in tgts[1:]], tf.animate.set_fill(DRV, opacity=0.7), run_time=1.0)
            lab = T("只接受调控的靶基因", 24, BLUE).next_to(tgts, DOWN, buff=0.4)
            self.play(FadeIn(lab), run_time=0.6)
        self.fade_all()

    # ------------------------------------------------------------------ non-uniqueness & control cores
    def cores(self):
        tag = self.chapter("二  最大匹配：控制核心点")
        D = nx.DiGraph(SMALL_E)
        P = {v: np.array([*SMALL_P[v], 0]) + RIGHT * 1.6 for v in D}
        nd = {v: Circle(radius=0.28, color=INK, stroke_width=2.5, fill_color=BG, fill_opacity=1).move_to(P[v]) for v in D}
        ar = {e: arrow_between(P[e[0]], P[e[1]], 0.3, 0.3, MUTED, sw=2.5) for e in D.edges()}
        allm = all_max_matchings(D)
        sets = {}
        for m in allm:
            sets.setdefault(tuple(sorted(drivers_of(D, m))), m)
        keys = list(sets)
        self.n_driver_sets = len(keys)

        def show(m):
            dr = set(drivers_of(D, m))
            anims = [a.animate.set_color(GOLD if e in m else MUTED).set_stroke(width=5 if e in m else 2.5) for e, a in ar.items()]
            anims += [c.animate.set_fill(DRV if v in dr else BLUE, opacity=0.8 if v in dr else 0.4) for v, c in nd.items()]
            return anims
        cnt = counter("驱动节点数", str(len(keys[0])), DRV, vs=40).to_corner(UR, buff=0.6).shift(DOWN * 0.4)
        with self.say("u1") as d:
            self.play(FadeIn(tag), *[FadeIn(c) for c in nd.values()], *[FadeIn(a) for a in ar.values()], run_time=1.0)
            self.play(*show(sets[keys[0]]), FadeIn(cnt), run_time=1.0)
        with self.say("u2") as d:
            for k in keys[1:4]:
                self.play(*show(sets[k]), run_time=max(0.8, d * 0.8 / 3))
        self.fade_all(keep=(tag,))
        # control paths: head / middle / tail
        with self.say("u3") as d:
            ig = T("输入图  ·  交换定理", 36, GOLD, weight=BOLD).move_to(UP * 0.4)
            sub = T("所有可能的驱动节点", 26, INK).next_to(ig, DOWN, buff=0.35)
            self.play(Write(ig), run_time=1.2)
            self.play(FadeIn(sub, shift=UP * 0.2), run_time=0.8)
        self.play(FadeOut(ig), FadeOut(sub), run_time=0.5)
        with self.say("u4") as d:
            xs = np.linspace(-4.5, 4.5, 6)
            rows = VGroup()
            for j, yy in enumerate((1.4, 0.0, -1.4)):
                pts = [np.array([x, yy, 0]) for x in xs]
                circ = VGroup(*[Circle(radius=0.22, color=INK, stroke_width=2).move_to(p) for p in pts])
                arr = VGroup(*[arrow_between(pts[i], pts[i + 1], 0.24, 0.24, MUTED, sw=2.5) for i in range(5)])
                circ[0].set_fill(DRV, opacity=0.8)
                rows.add(VGroup(arr, circ))
            self.play(FadeIn(rows), run_time=1.0)
            mids = VGroup(*[r[1][k] for r in rows for k in (2, 3)])
            self.play(*[m.animate.set_fill(GOLD, opacity=0.9) for m in mids], run_time=1.0)
            lh = T("头", 22, DRV).next_to(rows[0][1][0], UP, buff=0.15)
            lm = T("始终在中间：控制核心点", 22, GOLD).next_to(VGroup(rows[0][1][2], rows[0][1][3]), UP, buff=0.15)
            lt = T("尾", 22, MUTED).next_to(rows[0][1][5], UP, buff=0.15)
            self.play(FadeIn(lh), FadeIn(lm), FadeIn(lt), run_time=0.8)
        self.fade_all(keep=(tag,))
        ax = axes([0, 4, 1], [0, 80, 20], 8.0, 4.4, yn=[0, 20, 40, 60, 80], fs=20).shift(DOWN * 0.5 + LEFT * 0.3)
        yl = T("占全部基因的比例 (%)", 22, MUTED).rotate(PI / 2).next_to(ax.y_axis, LEFT, buff=0.35)
        net = T("7030 个基因的调控网络", 24, MUTED).next_to(ax, UP, buff=0.3)
        with self.say("u5") as d:
            self.play(Create(ax), FadeIn(yl), FadeIn(net), run_time=0.8)
            for x, val, c, nm in ((1, 44.3, BLUE, "一个方案的\n驱动基因"), (2, 71.9, VIOLET, "所有方案\n合计"), (3, 9.4, GOLD, "控制\n核心点")):
                r = Rectangle(width=1.3, height=ax.c2p(0, val)[1] - ax.c2p(0, 0)[1], fill_color=c, fill_opacity=0.9, stroke_width=0).move_to(ax.c2p(x, 0), aligned_edge=DOWN)
                self.play(GrowFromEdge(r, DOWN), FadeIn(T(f"{val}%", 26, c, weight=BOLD).next_to(r, UP, buff=0.08)),
                          FadeIn(T(nm, 20).next_to(ax.c2p(x, 0), DOWN, buff=0.2)), run_time=max(0.8, d * 0.22))
        with self.say("u6") as d:
            note = T("计算预测，需实验验证", 24, MUTED).to_corner(UR, buff=0.5).shift(DOWN * 0.6)
            self.play(FadeIn(note), run_time=0.8)
        self.fade_all()

    # ------------------------------------------------------------------ control energy
    def energy(self):
        tag = self.chapter("三  控制的代价")
        n = 8
        G = nx.connected_watts_strogatz_graph(n, 4, 0.3, seed=1)
        A = nx.to_numpy_array(G)
        A = A / (1 + np.linalg.svd(A, compute_uv=False)[0])
        b = np.zeros((n, 1)); b[0] = 1
        W = np.zeros((n, n)); Mp = np.eye(n)
        for _ in range(2000):
            W += Mp @ b @ b.T @ Mp.T; Mp = A @ Mp
        ev = np.sort(np.abs(np.linalg.eigvalsh(W)))[::-1]
        lg = np.log10(ev)
        self.energy_span = lg[0] - lg[-1]
        pos = fit(nx.circular_layout(G), (-6.2, -2.4, -1.8, 1.8), even=False) if False else \
            {v: np.array([-4.3 + 1.6 * np.cos(2 * np.pi * v / n), 0.0 + 1.6 * np.sin(2 * np.pi * v / n), 0]) for v in G}
        v = NetView(G, pos, color=BLUE, rmin=0.12, rk=0.0, ew=2, eo=0.5)
        with self.say("g1") as d:
            self.play(FadeIn(tag), FadeIn(v.group), run_time=1.2)
        with self.say("g2") as d:
            inp = Arrow(pos[0] + RIGHT * 1.3 + UP * 0.7, pos[0] + RIGHT * 0.2, buff=0, color=DRV, stroke_width=6)
            self.play(GrowArrow(inp), v.dots[0].animate.set_color(DRV), run_time=1.0)
        ax = axes([0, n + 1, 1], [-11, 0, 2], 6.0, 4.6, fs=20).move_to(RIGHT * 2.0 + DOWN * 0.2)
        ylab = VGroup(*[MathTex(f"10^{{{k}}}", font_size=24, color=MUTED).next_to(ax.c2p(0, k), LEFT, buff=0.12) for k in (0, -4, -8)])
        title = T("各方向的可达程度", 22, MUTED).next_to(ax, UP, buff=0.25)
        bars = VGroup()
        for i, x in enumerate(lg):
            top = ax.c2p(i + 1, 0); bot = ax.c2p(i + 1, x)
            bars.add(Rectangle(width=0.45, height=max(0.02, top[1] - bot[1]), fill_color=interpolate_color(ManimColor(GREEN), ManimColor(RED), i / (n - 1)),
                               fill_opacity=0.9, stroke_width=0).move_to(top, aligned_edge=UP))
        with self.say("g3") as d:
            self.play(Create(ax), FadeIn(ylab), FadeIn(title), run_time=0.8)
            self.play(LaggedStart(*[GrowFromEdge(bb, UP) for bb in bars], lag_ratio=0.15), run_time=d * 0.5)
        with self.say("g3b") as d:
            br = BraceBetweenPoints(ax.c2p(n + 0.5, 0), ax.c2p(n + 0.5, lg[-1]), direction=RIGHT, color=GOLD)
            bt = T(f"{self.energy_span:.0f} 个\n数量级", 22, GOLD).next_to(br, RIGHT, buff=0.1)
            self.play(GrowFromCenter(br), FadeIn(bt), run_time=0.8)
        self.fade_all(keep=(tag,))
        with self.say("g4") as d:
            brain = Ellipse(width=6.0, height=4.0, color=VIOLET, stroke_width=3)
            rng = np.random.default_rng(3)
            pts = [np.array([rng.uniform(-2.5, 2.5), rng.uniform(-1.5, 1.5), 0]) for _ in range(40)]
            pts = [p for p in pts if (p[0] / 2.8) ** 2 + (p[1] / 1.8) ** 2 < 1]
            rd = VGroup(*[Dot(p, radius=0.07, color=VIOLET) for p in pts])
            self.play(Create(brain), FadeIn(rd), run_time=1.0)
            self.play(rd[0].animate.set_color(DRV).scale(2), Flash(rd[0], color=DRV), run_time=0.8)
            self.play(LaggedStart(*[x.animate.set_color(GOLD) for x in rd[1:]], lag_ratio=0.05), run_time=1.2)
            cost = T("能量 → 极大", 30, RED).next_to(brain, DOWN, buff=0.3)
            self.play(FadeIn(cost), run_time=0.6)
        self.fade_all()

    # ------------------------------------------------------------------ stability
    def stability(self):
        show_clip(self, "g5", "yt_dbs_utsw.mp4", "center", "视频：UT Southwestern Medical Center · YouTube", start=30, min_len=7)
        tag = self.chapter("三  两种稳定")
        G = nx.barabasi_albert_graph(60, 2, seed=2)
        pos = fit(nx.kamada_kawai_layout(G), (-6.2, -1.0, -2.6, 2.6))
        v = NetView(G, pos, color=BLUE, eo=0.35)
        with self.say("s1") as d:
            self.play(FadeIn(tag), FadeIn(v.group), run_time=1.0)
            rm = list(np.random.default_rng(1).choice(60, 12, replace=False))
            self.play(*v.state(rm), run_time=1.4)
        with self.say("s2") as d:
            ax = Axes(x_range=[-2, 2], y_range=[0, 2], x_length=4.6, y_length=2.6, axis_config={"include_ticks": False, "color": MUTED}).move_to(RIGHT * 3.6 + DOWN * 0.6)
            well = ax.plot(lambda x: 0.45 * x ** 2 + 0.05, x_range=[-1.9, 1.9], color=GREEN, stroke_width=4)
            ball = Dot(ax.c2p(0, 0.05) + UP * 0.15, radius=0.15, color=GOLD)
            self.play(Create(well), FadeIn(ball), run_time=0.8)
            self.play(ball.animate.move_to(ax.c2p(1.2, 0.45 * 1.44 + 0.05) + UP * 0.15), run_time=0.6)
            self.play(ball.animate.move_to(ax.c2p(0, 0.05) + UP * 0.15), run_time=1.0, rate_func=there_and_back_with_pause if False else smooth)
        self.fade_all(keep=(tag,))
        pl = ComplexPlane(x_range=[-4, 2, 1], y_range=[-3, 3, 1], x_length=7.2, y_length=6.0,
                          background_line_style={"stroke_color": MUTED, "stroke_opacity": 0.15}).shift(LEFT * 1.6 + DOWN * 0.3)
        im = Line(pl.c2p(0, -3), pl.c2p(0, 3), color=RED, stroke_width=3)
        stab = pl.get_area if False else Rectangle(width=pl.c2p(0, 0)[0] - pl.c2p(-4, 0)[0], height=6.0, fill_color=GREEN, fill_opacity=0.07, stroke_width=0).move_to(pl.c2p(-2, 0))
        rng = np.random.default_rng(1)
        sigma = 0.4

        def cloud(N, C):
            J = -np.eye(N) + (rng.random((N, N)) < C) * rng.normal(0, sigma, (N, N))
            np.fill_diagonal(J, -1)
            ev = np.linalg.eigvals(J)
            dots = VGroup(*[Dot(pl.c2p(z.real, z.imag), radius=0.045, color=RED if z.real > 0 else GOLD) for z in ev])
            ring = Circle(radius=sigma * np.sqrt(N * C) * (pl.c2p(1, 0)[0] - pl.c2p(0, 0)[0]), color=MUTED, stroke_width=1.5).move_to(pl.c2p(-1, 0))
            lab = VGroup(counter("物种数", str(N), INK, vs=34), counter("连接概率", f"{C}", INK, vs=34)).arrange(DOWN, buff=0.4).move_to(RIGHT * 4.6 + UP * 0.6)
            return dots, ring, lab, ev.real.max()
        with self.say("s3") as d:
            self.play(FadeIn(stab), Create(pl), run_time=1.0)
            self.play(Create(im), run_time=0.6)
            il = T("虚轴", 22, RED).next_to(pl.c2p(0, 3), RIGHT, buff=0.1).shift(DOWN * 0.3)
            sl = T("稳定", 24, GREEN).move_to(pl.c2p(-3.3, 1.6))
            self.play(FadeIn(il), run_time=0.6)
        with self.say("s3b") as d:
            xl = T("实部", 20, MUTED).next_to(pl.c2p(2, 0), DOWN, buff=0.1)
            yl = T("虚部", 20, MUTED).next_to(pl.c2p(0, 2.7), LEFT, buff=0.12)
            self.play(FadeIn(xl), FadeIn(yl), Indicate(im, color=RED), run_time=1.0)
            self.play(FadeIn(sl), Indicate(stab, color=GREEN), run_time=1.0)
        c1 = cloud(20, 0.2)
        with self.say("s4") as d:
            self.play(FadeIn(c1[0], lag_ratio=0.05), Create(c1[1]), FadeIn(c1[2]), run_time=1.6)
        c2 = cloud(80, 0.2)
        c3 = cloud(160, 0.25)
        self.may_vals = (c1[3], c2[3], c3[3])
        with self.say("s5") as d:
            self.play(Transform(c1[0], c2[0]), Transform(c1[1], c2[1]), Transform(c1[2], c2[2]), run_time=d * 0.4)
            self.play(Transform(c1[0], c3[0]), Transform(c1[1], c3[1]), Transform(c1[2], c3[2]), run_time=d * 0.4)
        with self.say("s5b") as d:
            f = MathTex(r"\sigma\sqrt{NC}<1", font_size=52, color=GOLD).to_edge(DOWN, buff=0.5).shift(RIGHT * 4.2)
            fl = VGroup(T("σ：相互作用强度", 20, GOLD), T("N：物种数  C：连接概率", 20, GOLD)).arrange(DOWN, aligned_edge=LEFT, buff=0.1).next_to(f, UP, buff=0.25)
            self.play(Write(f), run_time=1.2)
            self.play(FadeIn(fl), run_time=0.8)
        with self.say("s6") as d:
            self.play(Indicate(f, color=GOLD), run_time=1.2)
        self.fade_all()

    # ------------------------------------------------------------------ recap
    def recap(self):
        recap_slide(self, ["最大匹配之外的节点，就是驱动节点", "驱动节点避开枢纽；稀疏、不均匀的网络更难控制", "可控不等于容易控制；两种稳定要分开看"])
        with self.say("z5") as d:
            self.clip_on("matching_demo.mp4", "full", "本站交互演示：最大匹配、驱动节点与 Kalman 秩检验", start=0.3)
        with self.say("z5b") as d:
            pass
        self.clip_off()
        self.wait(1.0)
