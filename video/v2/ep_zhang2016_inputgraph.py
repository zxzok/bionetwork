"""Paper explainer: input graph (2016), the hidden geometry of controlling complex networks."""
import random

import networkx as nx
import numpy as np

from common import *  # noqa: F401,F403
from paperkit import DiNet, arrow, counter, max_matching, drivers, n_drivers, possible_inputs, input_graph

TITLE = "输入图：控制方案之间的隐藏结构"

LINES = {
    # hook
    "h1": "我们先来看一个小小的有向网络：六个节点，五条带方向的边。要控制它，最少需要三个输入节点。输入节点，就是直接施加外部信号的节点。",
    "h2": "可是选哪三个，答案不止一种。一、四、五可以；一、四、三也可以；一、四、二同样可以。",
    "h3": "注意，节点一和四每次都在，节点六却一次也没有出现。",
    "h4": "网络一大，这样的方案数会随规模指数增长，想全部列出来根本做不到。这条曲线，横轴是网络规模，纵轴是方案数。",
    "h5": "【慢】这么多方案之间有什么关系，2016年发表的一项研究，用一张新的网络回答了这个问题。",
    "p0": "这一期分三部分来讲。",
    "p1": "第一部分，两类节点，以及控制方案之间怎样互相替换。",
    "p2": "第二部分，输入图，以及它怎样解释控制模式的两极分化。",
    "p3": "第三部分，怎样用少量加边翻转一大批节点的角色，以及意义和局限。",
    # two kinds of nodes
    "q1": "先看第一部分。这项研究把驱动节点叫做输入节点。一组最少的输入节点，叫最小输入节点集，也就是一种控制方案。",
    "q1b": "本站的可控性专题里有一个交互演示。每换一个网络，橙色的边是一组最大匹配，红色是没有被匹配的节点，也就是一组输入节点。",
    "q2": "至少出现在一种方案里的节点，叫可能输入节点，画成黄色；一种方案都进不去的，叫冗余节点，画成灰色。",
    "q3": "更早的研究发现，在稠密网络里，这两类节点的比例很极端：要么几乎都能当输入，要么几乎都不能。可成因一直不清楚。",
    # exchange
    "e1": "下面看关键概念：控制邻接。匹配边，就是最大匹配里选中的边。看节点丙，它有一条匹配边指向乙，还有一条非匹配边指向甲。",
    "e2": "丙的匹配名额给了乙。这时就说，甲和乙控制邻接，它们通过同一个上家联系在一起。",
    "e3": "交换定理说：如果甲是输入节点，就把丙的匹配边从乙挪到甲上。匹配边数没变，仍然是最大匹配。",
    "e4": "于是甲被匹配了，乙失去匹配入边，成了新的输入节点。",
    "e4b": "【慢】写成式子，就是右上角这一行：新方案，等于原方案去掉甲、加上乙。它仍是一个最小输入节点集。",
    "e5": "甲一定有这样的上家。因为如果丙没有匹配出边，就能把丙指向甲这条边加进匹配，那原来的匹配就不是最大的了。",
    "e6": "每次交换只改一条匹配边、一个输入节点，是对原方案最小的改动。一个推论是：只有入度为零的节点，也就是没有任何边指向它的节点，才会出现在所有方案里。",
    # input graph
    "g1": "下面进入第二部分。把所有的控制邻接关系连成边，就得到了输入图。左边是原网络，右边是输入图。",
    "g2": "回到开头的例子。五和三控制邻接，三和二控制邻接，于是二、三、五连成一个分支。分支，就是连在一起的一团节点。",
    "g3": "从输入节点五出发，沿输入图走到的节点都能替换它，所以三和二也是可能输入节点。",
    "g4": "节点六只有一条入边，来自节点二，而节点二没有别的出边。所以，六不和任何节点控制邻接，自己单独成为一个分支。",
    "g5": "含有输入节点的分支，叫输入分支，里面的节点都是可能输入节点；不含输入节点的，叫匹配分支，里面全是冗余节点。",
    "g6": "【慢】研究还证明，分支的类型与选哪个最大匹配无关。节点的命运，由它所在的分支决定。",
    # giant component
    "b1": "到了大网络上，研究在一万个节点的无标度网络上，逐渐增加平均度，观察输入图的变化。画面是一个示意：左右两张输入图，红点是输入节点。",
    "b2": "平均度越大，最大控制分支越大，分支的数目越来越少。黄色是输入分支，灰色是匹配分支。",
    "b3": "到了稠密网络，基本只剩下一个巨分支，把大多数节点连在一起。",
    "b4": "【慢】巨分支是输入分支，多数节点都能当输入；巨分支是匹配分支，多数节点都是冗余的。这就从拓扑上，解释了那种两极分化的现象。",
    "b5": "研究统计的三十七个真实网络里，不少都有巨控制分支。比如一个酵母转录调控网络，最大分支占了百分之九十九以上。",
    # flipping
    "f1": "下面进入第三部分。既然一个分支里的节点类型相同，想改变一大批节点的类型，只需改变分支的类型。",
    "f2": "回到小例子。从一个没有匹配出边的节点，比如六，向输入节点五加一条边，就是这条绿色的边。",
    "f3": "五被匹配了。二、三、五这个分支里再也没有输入节点，变成了匹配分支，三个节点一起变成冗余节点。",
    "f4": "而且，所需的输入节点从三个减到了两个。",
    "f5": "在真实网络里效果更惊人。这张图里，绿色条的长度，是类型被改变的节点比例。亚马逊的一个商品网络，只加了极少量的边，就改变了约百分之七十六节点的类型。",
    "f6": "一个脸书社交网络，加入万分之二的边，改变了约百分之八十二；而稀疏的大肠杆菌转录网络，要加三成多的边，才改变不到百分之二。",
    "f7": "翻转之后，所需的输入节点也明显减少。一个酵母转录网络，输入节点的比例从百分之九十六，降到了不到百分之一。",
    # meaning & limits
    "m1": "对生物医学来说，这有一个直接的用处。药物靶点，就是药物直接作用的蛋白质。画面里，是关于药物和靶点的入门讲解。",
    "m1b": "如果某个蛋白没法作为药物靶点，沿着输入图找一个邻居替换它就行。你看，五无法成药，就换成三，只改动了一条匹配边。",
    "m2a": "画面里，是一个常用的蛋白质互作数据库给出的网络视图。这样的网络，都还远不完整。",
    "m2": "研究还指出，新发现的边只会让巨分支变大。所以在不完整的蛋白质网络里，说某个蛋白是冗余节点，要格外谨慎。",
    "m3": "局限方面，理论仍基于线性时不变系统和结构可控性；而在蛋白质相互作用这样的系统里，加边往往很难实现。",
    "m4": "共享邻居的两个输入节点，不能同时替换。构建完整的输入图，计算量是节点数乘以边数的量级，对超大网络偏慢，这正是后来的快速算法要解决的问题。",
    # recap
    "r1": "好，我们来总结一下。",
    "r2": "第一，控制邻接和交换定理，刻画了不同控制方案之间的替换关系。",
    "r3": "第二，输入图的分支决定节点类型，巨分支解释了控制模式的两极分化。",
    "r4": "第三，改变分支的类型，少量加边就能翻转一大批节点的角色。",
}

EX = [(1, 2), (1, 3), (4, 3), (4, 5), (2, 6)]
EXPOS = {1: (-4.0, 1.0), 2: (-2.0, 2.0), 3: (-2.0, 0.0), 4: (-4.0, -1.0), 5: (-2.0, -2.0), 6: (0.0, 2.0)}
EXM = [(1, 2), (4, 3), (2, 6)]


def ex_net(shift=ORIGIN, extra=()):
    G = nx.DiGraph(); G.add_nodes_from(sorted(EXPOS)); G.add_edges_from(EX); G.add_edges_from(extra)
    pos = {v: np.array([*p, 0]) + shift for v, p in EXPOS.items()}
    return G, pos


class Episode(Narrated):
    LINES = LINES

    def construct(self):
        self.hook()
        self.parts()
        self.kinds()
        self.exchange()
        self.inputgraph()
        self.giant()
        self.flip()
        self.meaning()
        self.recap()

    # ------------------------------------------------------------------ hook
    def hook(self):
        G, pos = ex_net(RIGHT * 2.0)
        net = DiNet(G, pos, r=0.3)
        assert n_drivers(G) == 3
        mis = [(1, 4, 5), (1, 4, 3), (1, 4, 2)]
        with self.say("h1") as d:
            self.play(FadeIn(net.group[1]), LaggedStart(*[GrowArrow(a) for a in net.arrows.values()], lag_ratio=0.15), run_time=d * 0.5)
        lab = counter("方案", "1", RED).to_corner(UR, buff=0.6)
        with self.say("h2") as d:
            self.play(FadeIn(lab), run_time=0.4)
            for i, D in enumerate(mis):
                anims = [net.fill(v, RED, 0.8) if v in D else net.reset(v) for v in G]
                self.play(*anims, Transform(lab[1], T(str(i + 1), 40, RED, weight=BOLD).move_to(lab[1])), run_time=0.6)
                self.wait(max(0.2, d / 3 - 0.8))
        with self.say("h3") as d:
            self.play(*[net.reset(v) for v in G], run_time=0.4)
            self.play(net.fill(1, RED, 0.8), net.fill(4, RED, 0.8), run_time=0.8)
            x = Cross(net.nodes[6], stroke_color=MUTED, scale_factor=0.8)
            self.play(Create(x), run_time=0.8)
        with self.say("h4") as d:
            self.play(FadeOut(x), FadeOut(net.group), FadeOut(lab), run_time=0.6)
            ax = Axes(x_range=[0, 10, 2], y_range=[0, 1, 1], x_length=7, y_length=4,
                      axis_config={"color": MUTED, "include_tip": False, "tick_size": 0}).shift(DOWN * 0.3)
            cv = ax.plot(lambda x: (np.exp(0.6 * x) - 1) / (np.exp(6) - 1), x_range=[0, 10], color=RED, stroke_width=5)
            xl = T("网络规模", 24, MUTED).next_to(ax.x_axis, DOWN, buff=0.2)
            yl = T("方案数", 24, MUTED).rotate(PI / 2).next_to(ax.y_axis, LEFT, buff=0.2)
            self.play(Create(ax), FadeIn(xl), FadeIn(yl), run_time=0.8)
            self.play(Create(cv), run_time=d * 0.45)
        with self.say("h5") as d:
            q = T("方案之间是什么关系", 46, GOLD, weight=BOLD).to_edge(UP, buff=0.6)
            self.play(VGroup(ax, cv, xl, yl).animate.fade(0.8), Write(q), run_time=1.2)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.6)

    def parts(self):
        head, items = slide("这一期分三部分", ["一  两类节点与交换定理", "二  输入图与两极分化", "三  翻转控制模式、意义与局限"])
        with self.say("p0") as d:
            self.play(FadeIn(head, shift=RIGHT * 0.3), run_time=0.6)
        for k, it in zip(("p1", "p2", "p3"), items):
            with self.say(k) as d:
                self.play(FadeIn(it, shift=RIGHT * 0.3), run_time=0.6)
        self.wait(0.6)
        self.play(FadeOut(head), FadeOut(items), run_time=0.6)

    # ------------------------------------------------------------------ kinds
    def kinds(self):
        tag = self.chapter("一 · 两类节点")
        G, pos = ex_net(RIGHT * 1.0)
        net = DiNet(G, pos, r=0.3)
        M = set(EXM)
        P = possible_inputs(G, M)
        assert P == {1, 2, 3, 4, 5}
        with self.say("q1") as d:
            self.play(FadeIn(tag), FadeIn(net.group), run_time=1.0)
            self.play(*[net.fill(v, RED, 0.8) for v in (1, 4, 5)], run_time=0.8)
            br = Brace(VGroup(net.nodes[1], net.nodes[4], net.nodes[5]), LEFT, color=RED)
            bl = T("最小输入节点集", 26, RED).next_to(br, LEFT, buff=0.15)
            self.play(GrowFromCenter(br), FadeIn(bl), run_time=0.8)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.6)
        with self.say("q1b") as d:
            self.clip_on("matching_networks_demo.mp4", "full", "本站交互演示：最大匹配与驱动节点", start=0.3)
        self.clip_off()
        with self.say("q2") as d:
            self.play(FadeIn(tag), FadeIn(net.group), run_time=0.6)
            self.play(*[net.fill(v, GOLD, 0.7) for v in P], run_time=1.0)
            self.play(net.fill(6, MUTED, 0.5), run_time=0.6)
            lg = VGroup(VGroup(Dot(color=GOLD), T("可能输入节点", 26)).arrange(RIGHT, buff=0.15),
                        VGroup(Dot(color=MUTED), T("冗余节点", 26)).arrange(RIGHT, buff=0.15)).arrange(DOWN, aligned_edge=LEFT).to_corner(UR, buff=0.6)
            self.play(FadeIn(lg), run_time=0.6)
        with self.say("q3") as d:
            self.play(FadeOut(net.group), FadeOut(lg), run_time=0.6)
            W = 4.6
            rows = VGroup()
            for nm, f in (("分布式控制", 0.92), ("集中式控制", 0.06)):
                bg = Rectangle(width=W, height=0.6, stroke_width=0, fill_color=MUTED, fill_opacity=0.45)
                fg = Rectangle(width=W * f, height=0.6, stroke_width=0, fill_color=GOLD, fill_opacity=0.9).align_to(bg, LEFT)
                rows.add(VGroup(T(nm, 28), VGroup(bg, fg)).arrange(RIGHT, buff=0.4))
            rows.arrange(DOWN, buff=0.6, aligned_edge=RIGHT).move_to(DOWN * 0.2)
            sch = T("示意", 20, MUTED).next_to(rows, DOWN, buff=0.3)
            self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in rows], lag_ratio=0.4), FadeIn(sch), run_time=d * 0.5)
            qm = T("成因不明", 40, GOLD, weight=BOLD).next_to(rows, UP, buff=0.6)
            self.play(FadeIn(qm), run_time=0.6)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.6)

    # ------------------------------------------------------------------ exchange theorem
    def exchange(self):
        tag = self.chapter("一 · 控制邻接与交换定理")
        C, A, B = UP * 1.6, LEFT * 2.0 + DOWN * 1.2, RIGHT * 2.0 + DOWN * 1.2
        mk = lambda p, s, c=BLUE: VGroup(Circle(radius=0.42, color=c, fill_color=BG, fill_opacity=1, stroke_width=4), T(s, 32)).move_to(p)
        nc, na, nb = mk(C, "丙"), mk(A, "甲"), mk(B, "乙")
        ca = arrow(C, A, 0.46, MUTED, 4); cb = arrow(C, B, 0.46, GOLD, 7)
        up = arrow(C + UP * 1.6, C, 0.46, MUTED, 3)
        with self.say("e1") as d:
            self.play(FadeIn(tag), FadeIn(VGroup(nc, na, nb)), run_time=0.8)
            self.play(GrowArrow(cb), run_time=0.8)
            ml = T("匹配边", 24, GOLD).next_to(cb.get_center(), UR, buff=0.15)
            self.play(FadeIn(ml), GrowArrow(ca), run_time=0.8)
            nl = T("非匹配边", 24, MUTED).next_to(ca.get_center(), UL, buff=0.15)
            self.play(FadeIn(nl), run_time=0.5)
        with self.say("e2") as d:
            link = DashedLine(A + RIGHT * 0.5, B + LEFT * 0.5, color=VIOLET, stroke_width=4)
            ll = T("控制邻接", 28, VIOLET).next_to(link, DOWN, buff=0.2)
            self.play(Create(link), FadeIn(ll), run_time=1.2)
        with self.say("e3") as d:
            self.play(na[0].animate.set_fill(RED, opacity=0.8).set_stroke(RED), run_time=0.8)
            self.play(cb.animate.set_color(MUTED).set_stroke(width=4), ca.animate.set_color(GOLD).set_stroke(width=7),
                      ml.animate.next_to(ca.get_center(), UL, buff=0.15), nl.animate.next_to(cb.get_center(), UR, buff=0.15), run_time=d * 0.35)
        with self.say("e4") as d:
            self.play(na[0].animate.set_fill(BG, opacity=1).set_stroke(BLUE), nb[0].animate.set_fill(RED, opacity=0.8).set_stroke(RED), run_time=1.2)
        with self.say("e4b") as d:
            sw = T("新方案 = 原方案 − 甲 + 乙", 30, RED).to_corner(UR, buff=0.6)
            self.play(Write(sw), run_time=1.2)
        with self.say("e5") as d:
            self.play(FadeOut(sw), cb.animate.set_color(GOLD).set_stroke(width=7), ca.animate.set_color(MUTED).set_stroke(width=4),
                      ml.animate.next_to(cb.get_center(), UR, buff=0.15), nl.animate.next_to(ca.get_center(), UL, buff=0.15),
                      na[0].animate.set_fill(RED, opacity=0.8).set_stroke(RED), nb[0].animate.set_fill(BG, opacity=1).set_stroke(BLUE), run_time=1.0)
            ghost = cb.copy().set_opacity(0.15)
            self.play(FadeOut(cb), FadeIn(ghost), ml.animate.set_opacity(0.2), run_time=0.6)
            self.play(ca.animate.set_color(GREEN).set_stroke(width=7), run_time=0.8)
            x = Cross(VGroup(ca, ghost), stroke_color=RED, scale_factor=0.5)
            self.play(Create(x), run_time=0.6)
            self.play(FadeOut(x), FadeIn(cb), FadeOut(ghost), ml.animate.set_opacity(1), ca.animate.set_color(MUTED).set_stroke(width=4), run_time=0.6)
        self.play(FadeOut(VGroup(nc, na, nb, ca, cb, ml, nl, link, ll)), run_time=0.6)
        with self.say("e6") as d:
            G, pos = ex_net(RIGHT * 1.0)
            net = DiNet(G, pos, r=0.3)
            self.play(FadeIn(net.group), run_time=0.8)
            rings = VGroup(*[Circle(radius=0.45, color=RED, stroke_width=4).move_to(pos[v]) for v in (1, 4)])
            self.play(net.fill(1, RED, 0.8), net.fill(4, RED, 0.8), Create(rings), run_time=1.0)
            lab = T("入度为零：每个方案都在", 28, RED).to_corner(UR, buff=0.6)
            self.play(FadeIn(lab), run_time=0.6)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.6)

    # ------------------------------------------------------------------ input graph
    def inputgraph(self):
        tag = self.chapter("二 · 输入图")
        G, pos = ex_net(LEFT * 1.5)
        net = DiNet(G, pos, r=0.3)
        M = set(EXM)
        H = input_graph(G, M)
        assert {frozenset(e) for e in H.edges()} == {frozenset((5, 3)), frozenset((3, 2))}
        comps = sorted(map(sorted, nx.connected_components(H)))
        assert [2, 3, 5] in comps and [6] in comps
        Q = {v: np.array([*p, 0]) + RIGHT * 6.3 for v, p in EXPOS.items()}
        ig = {v: VGroup(Circle(radius=0.3, color=BLUE, fill_color=BG, fill_opacity=1, stroke_width=3), T(str(v), 24)).move_to(Q[v]) for v in G}
        sep = DashedLine(UP * 3.2 + RIGHT * 0.4, DOWN * 3.4 + RIGHT * 0.4, color=MUTED, stroke_opacity=0.5)
        t1 = T("原网络", 26, MUTED).move_to([-3.5, 3.1, 0]); t2 = T("输入图", 26, GOLD).move_to([4.3, 3.1, 0])
        with self.say("g1") as d:
            self.play(FadeIn(tag), FadeIn(net.group), FadeIn(t1), run_time=1.0)
            self.play(*[net.arrows[e].animate.set_color(GOLD).set_stroke(width=6) for e in EXM], *[net.fill(v, RED, 0.8) for v in (1, 4, 5)], run_time=1.0)
            self.play(Create(sep), FadeIn(t2), *[FadeIn(x) for x in ig.values()], run_time=1.0)
        e53 = Line(Q[5], Q[3], color=VIOLET, stroke_width=6).scale(0.75)
        e32 = Line(Q[3], Q[2], color=VIOLET, stroke_width=6).scale(0.75)
        with self.say("g2") as d:
            self.play(Indicate(net.arrows[(4, 5)], color=VIOLET), Indicate(net.arrows[(4, 3)], color=GOLD), run_time=1.0)
            self.play(Create(e53), run_time=0.6)
            self.play(Indicate(net.arrows[(1, 3)], color=VIOLET), Indicate(net.arrows[(1, 2)], color=GOLD), run_time=1.0)
            self.play(Create(e32), run_time=0.6)
        with self.say("g3") as d:
            ig[5][0].set_fill(RED, opacity=0.8).set_stroke(RED)
            self.play(Flash(ig[5], color=RED), run_time=0.6)
            for v in (3, 2):
                self.play(ig[v][0].animate.set_fill(GOLD, opacity=0.7).set_stroke(GOLD), run_time=0.7)
            self.play(net.fill(3, GOLD, 0.7), net.fill(2, GOLD, 0.7), run_time=0.7)
        with self.say("g4") as d:
            self.play(Indicate(net.arrows[(2, 6)], color=GOLD), Indicate(net.nodes[6], color=MUTED), run_time=1.2)
            self.play(ig[6][0].animate.set_fill(MUTED, opacity=0.5).set_stroke(MUTED), net.fill(6, MUTED, 0.5), run_time=0.8)
        with self.say("g5") as d:
            for v in (1, 4):
                ig[v][0].set_fill(RED, opacity=0.8).set_stroke(RED)
            b1 = SurroundingRectangle(VGroup(ig[2], ig[3], ig[5]), color=GOLD, buff=0.15)
            b2 = SurroundingRectangle(ig[6], color=MUTED, buff=0.15)
            l1 = T("输入分支", 24, GOLD).next_to(b1, RIGHT, buff=0.15)
            l2 = T("匹配分支", 24, MUTED).next_to(b2, DOWN, buff=0.15)
            self.play(FadeIn(VGroup(ig[1], ig[4])), Create(b1), FadeIn(l1), run_time=1.0)
            self.play(Create(b2), FadeIn(l2), run_time=0.8)
        with self.say("g6") as d:
            self.play(Indicate(VGroup(b1, l1), color=GOLD), run_time=1.2)
            self.play(Indicate(VGroup(b2, l2), color=INK), run_time=1.2)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.6)

    # ------------------------------------------------------------------ giant component (schematic)
    def giant(self):
        tag = self.chapter("二 · 巨分支与两极分化")
        rng = np.random.default_rng(4)
        n = 42

        def panel(cx, inputs_in_giant):
            pts = []
            while len(pts) < n:
                p = np.array([cx + rng.uniform(-2.6, 2.6), rng.uniform(-2.4, 2.2), 0])
                if all(np.linalg.norm(p - q) > 0.5 for q in pts):
                    pts.append(p)
            near = sorted(((i, j) for i in range(n) for j in range(i + 1, n)), key=lambda e: np.linalg.norm(pts[e[0]] - pts[e[1]]))
            inputs = [0, 1, 2] if inputs_in_giant else [n - 1, n - 2, n - 3]
            dots = [Dot(p, radius=0.09, color=MUTED) for p in pts]
            return pts, near, inputs, dots
        L = panel(-3.4, True)
        R = panel(3.4, False)
        lines = {}

        def stage(panel_, k, ex_isolate):
            pts, near, inputs, dots = panel_
            H = nx.Graph(); H.add_nodes_from(range(n))
            es = [e for e in near if not (set(e) & ex_isolate)][:k]
            H.add_edges_from(es)
            anims = []
            for e in es:
                key = (id(panel_), e)
                if key not in lines:
                    lines[key] = Line(pts[e[0]], pts[e[1]], color=MUTED, stroke_width=2, stroke_opacity=0.6)
                    anims.append(Create(lines[key]))
            comps = list(nx.connected_components(H))
            big = max(comps, key=len)
            for c in comps:
                col = GOLD if c & set(inputs) else MUTED
                for v in c:
                    anims.append(dots[v].animate.set_color(col))
            for v in inputs:
                anims.append(dots[v].animate.set_color(RED))
            return anims, len(big) / n, len(comps)
        isoR = set(R[2])
        with self.say("b1") as d:
            self.play(FadeIn(tag), *[FadeIn(x) for x in L[3] + R[3]], run_time=1.0)
            a1, _, _ = stage(L, 18, set()); a2, _, _ = stage(R, 18, isoR)
            self.play(*a1, *a2, run_time=d * 0.4)
        with self.say("b2") as d:
            a1, f1, _ = stage(L, 40, set()); a2, f2, _ = stage(R, 40, isoR)
            self.play(*a1, *a2, run_time=d * 0.5)
        with self.say("b3") as d:
            a1, f1, c1 = stage(L, 80, set()); a2, f2, c2 = stage(R, 80, isoR)
            self.play(*a1, *a2, run_time=d * 0.5)
            assert f1 > 0.8 and f2 > 0.8
        with self.say("b4") as d:
            lt = T("巨分支 = 输入分支", 28, GOLD).move_to([-3.4, 2.9, 0])
            rt = T("巨分支 = 匹配分支", 28, MUTED).move_to([3.4, 2.9, 0])
            ls = T("多数节点可当输入", 24, GOLD).move_to([-3.4, -3.0, 0])
            rs = T("多数节点是冗余的", 24, MUTED).move_to([3.4, -3.0, 0])
            self.play(FadeOut(tag), FadeIn(lt), FadeIn(ls), run_time=1.0)
            self.play(FadeIn(rt), FadeIn(rs), run_time=1.0)
        with self.say("b5") as d:
            self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.6)
            bg = Rectangle(width=9, height=0.8, stroke_width=0, fill_color=MUTED, fill_opacity=0.4)
            fg = Rectangle(width=9 * 0.9921, height=0.8, stroke_width=0, fill_color=GOLD, fill_opacity=0.9).align_to(bg, LEFT)
            g = VGroup(bg, fg).move_to(DOWN * 0.2)
            nm = T("酵母转录调控网络：最大控制分支", 28).next_to(g, UP, buff=0.3)
            v = T("99.21%", 40, GOLD, weight=BOLD).next_to(g, DOWN, buff=0.3)
            self.play(FadeIn(nm), FadeIn(bg), run_time=0.6)
            self.play(GrowFromEdge(fg, LEFT), FadeIn(v), run_time=1.4)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.6)

    # ------------------------------------------------------------------ flipping
    def flip(self):
        tag = self.chapter("三 · 加几条边，翻转一大片")
        G, pos = ex_net(LEFT * 0.5)
        net = DiNet(G, pos, r=0.3)
        M = set(EXM)
        P = possible_inputs(G, M)
        with self.say("f1") as d:
            self.play(FadeIn(tag), FadeIn(net.group), run_time=0.8)
            self.play(*[net.arrows[e].animate.set_color(GOLD).set_stroke(width=6) for e in EXM],
                      *[net.fill(v, GOLD, 0.7) for v in P], net.fill(6, MUTED, 0.5), run_time=1.0)
            self.play(*[net.fill(v, RED, 0.8) for v in (1, 4, 5)], run_time=0.8)
            box = SurroundingRectangle(VGroup(net.nodes[2], net.nodes[3], net.nodes[5]), color=GOLD, buff=0.2)
            self.play(Create(box), run_time=0.8)
        new = arrow(pos[6], pos[5], 0.33, GREEN, 6)
        with self.say("f2") as d:
            self.play(Indicate(net.nodes[6], color=GREEN), run_time=1.0)
            self.play(GrowArrow(new), run_time=1.2)
        G2 = G.copy(); G2.add_edge(6, 5)
        M2 = max_matching(G2)
        P2 = possible_inputs(G2, M2)
        assert n_drivers(G2) == 2 and P2 == {1, 4}
        with self.say("f3") as d:
            self.play(new.animate.set_color(GOLD), net.fill(5, GOLD, 0.7), run_time=0.8)
            self.play(*[net.fill(v, MUTED, 0.5) for v in (2, 3, 5)], box.animate.set_color(MUTED), run_time=1.4)
        with self.say("f4") as d:
            c = counter("输入节点", "3 → 2", RED).to_corner(UR, buff=0.6)
            self.play(FadeIn(c), *[Indicate(net.nodes[v], color=RED) for v in (1, 4)], run_time=1.2)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.6)
        data = [("Amazon0312", "加边 0.00003%", 0.7574, "75.74%"), ("Facebook_0", "加边 0.02%", 0.8184, "81.84%"),
                ("大肠杆菌转录", "加边 34.78%", 0.0189, "1.89%")]
        rows = VGroup()
        for nm, p, f, s in data:
            bg = Rectangle(width=4.6, height=0.55, stroke_width=0, fill_color=MUTED, fill_opacity=0.3)
            fg = Rectangle(width=max(0.03, 4.6 * f), height=0.55, stroke_width=0, fill_color=GREEN, fill_opacity=0.9).align_to(bg, LEFT)
            rows.add(VGroup(T(nm, 24), T(p, 22, GOLD), VGroup(bg, fg), T(s, 26, GREEN, weight=BOLD)))
        for i, r in enumerate(rows):
            y = 0.9 - 1.1 * i
            r[0].move_to([-6.2 + r[0].width / 2, y, 0])
            r[1].move_to([-1.75, y, 0])
            r[2].move_to([2.35, y, 0])
            r[3].next_to(r[2], RIGHT, buff=0.25)
        head = T("类型被改变的节点比例", 24, MUTED).next_to(rows[0][2], UP, buff=0.35)
        with self.say("f5") as d:
            self.play(FadeIn(head), FadeIn(rows[0][:3]), run_time=0.8)
            self.play(GrowFromEdge(rows[0][2][1], LEFT), FadeIn(rows[0][3]), run_time=1.2)
        with self.say("f6") as d:
            for r in rows[1:]:
                self.play(FadeIn(r[:3]), run_time=0.6)
                self.play(GrowFromEdge(r[2][1], LEFT), FadeIn(r[3]), run_time=1.0)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.6)
        ax = Axes(x_range=[0, 2, 1], y_range=[0, 100, 50], x_length=4.0, y_length=4.0,
                  axis_config={"color": MUTED, "include_tip": False, "font_size": 22},
                  y_axis_config={"numbers_to_include": [0, 50, 100]}).move_to(DOWN * 0.2)
        yl = T("输入节点比例 (%)", 22, MUTED).rotate(PI / 2).next_to(ax.y_axis, LEFT, buff=0.3)
        tt = T("酵母转录调控网络", 28).move_to(UP * 3.0)

        def bar(x, h, c, s, lab):
            hh = max(0.02, ax.c2p(0, h)[1] - ax.c2p(0, 0)[1])
            r = Rectangle(width=1.0, height=hh, fill_color=c, fill_opacity=0.9, stroke_width=0).move_to(ax.c2p(x, 0), aligned_edge=DOWN)
            return VGroup(r, T(s, 26, c, weight=BOLD).next_to(r, UP, buff=0.1), T(lab, 24).next_to(ax.c2p(x, 0), DOWN, buff=0.2))
        with self.say("f7") as d:
            b1 = bar(0.5, 96.46, RED, "96.46%", "翻转前"); b2 = bar(1.5, 0.70, GREEN, "0.70%", "翻转后")
            self.play(Create(ax), FadeIn(yl), FadeIn(tt), run_time=0.8)
            self.play(FadeIn(b1, shift=UP * 0.2), run_time=0.8)
            self.play(FadeIn(b2, shift=UP * 0.2), run_time=0.8)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.6)

    # ------------------------------------------------------------------ meaning & limits
    def meaning(self):
        tag = self.chapter("三 · 意义与局限")
        G, pos = ex_net(LEFT * 0.5)
        net = DiNet(G, pos, r=0.3)
        with self.say("m1") as d:
            self.clip_on("yt_drug_targets_compchemist.mp4", "center", "视频：CompChemist · YouTube", start=60)
        self.clip_off()
        with self.say("m1b") as d:
            self.play(FadeIn(tag), FadeIn(net.group), run_time=0.8)
            self.play(*[net.fill(v, RED, 0.8) for v in (1, 4, 5)], run_time=0.6)
            x = Cross(net.nodes[5], stroke_color=RED, scale_factor=0.9)
            nd = T("无法成药", 24, RED).next_to(net.nodes[5], RIGHT, buff=0.2)
            self.play(Create(x), FadeIn(nd), run_time=0.8)
            self.play(net.fill(3, RED, 0.8), net.arrows[(4, 3)].animate.set_color(MUTED), net.arrows[(4, 5)].animate.set_color(GOLD).set_stroke(width=6),
                      net.reset(5), run_time=1.2)
        self.play(FadeOut(VGroup(x, nd, net.group, tag)), run_time=0.6)
        with self.say("m2a") as d:
            self.clip_on("yt_string_jensen.mp4", "center", "视频：Lars Juhl Jensen · YouTube", start=60)
        self.clip_off()
        self.add(tag)
        rng = np.random.default_rng(1)
        pts = [np.array([rng.uniform(-5, 1.5), rng.uniform(-2.5, 2.3), 0]) for _ in range(30)]
        dots = VGroup(*[Dot(p, radius=0.09, color=MUTED) for p in pts])
        with self.say("m2") as d:
            self.play(FadeIn(dots), run_time=0.6)
            g1 = [i for i in range(30) if pts[i][0] < -1.5]
            self.play(*[dots[i].animate.set_color(GOLD) for i in g1], run_time=0.8)
            newe = VGroup(*[DashedLine(pts[g1[k]], pts[j], color=GREEN) for k, j in enumerate([i for i in range(30) if i not in g1][:5])])
            self.play(Create(newe), run_time=1.0)
            self.play(*[dots[i].animate.set_color(GOLD) for i in range(30) if i not in g1][:5], run_time=0.8)
            warn = T("“冗余”要谨慎", 30, GOLD).move_to(RIGHT * 4.2 + UP * 0.5)
            self.play(FadeIn(warn), run_time=0.6)
        self.play(FadeOut(VGroup(dots, newe, warn)), run_time=0.6)
        with self.say("m3") as d:
            f = MathTex(r"\dot{\mathbf x}=A\mathbf x+B\mathbf u", font_size=56).move_to(UP * 1.0)
            self.play(Write(f), run_time=1.0)
            hard = T("在生物系统里加边很难", 30, RED).next_to(f, DOWN, buff=0.6)
            self.play(FadeIn(hard), run_time=0.8)
        with self.say("m4") as d:
            self.play(FadeOut(f), FadeOut(hard), run_time=0.5)
            clock = VGroup(Circle(radius=0.8, color=INK), Line(ORIGIN, UP * 0.6, color=INK), Line(ORIGIN, RIGHT * 0.45, color=INK)).move_to(LEFT * 2.5)
            o = MathTex(r"O(NL)", font_size=50, color=GOLD).next_to(clock, RIGHT, buff=0.8)
            self.play(Create(clock), Write(o), run_time=1.0)
            self.play(Rotate(clock[1], -2 * PI, about_point=clock[0].get_center()), run_time=d * 0.4)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.6)

    # ------------------------------------------------------------------ recap
    def recap(self):
        with self.say("r1") as d:
            head = T("三个要点", 40, INK, weight=BOLD).to_edge(UP, buff=0.7)
            self.play(Write(head), run_time=0.8)
        items = [("r2", BLUE, "控制邻接 + 交换定理：方案之间可替换"),
                 ("r3", GOLD, "输入图的分支决定节点类型"),
                 ("r4", RED, "改变分支类型，少量加边翻转大批节点")]
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
