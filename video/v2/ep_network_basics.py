"""Animated explainer: 把系统写成图 (graphs, adjacency and Laplacian matrices, bipartite projection, sparsity)."""
import networkx as nx
import numpy as np

from common import *  # noqa: F401,F403
from ahelp import Grid, counter, edge_line, fade_all, node, recap_rows, fit, NetView, parts_slide

TITLE = "把系统写成图：节点、边与矩阵"

LINES = {
    # hook
    "h0": "这个故事发生在十八世纪的哥尼斯堡，一座有很多桥的城市。",
    "h1": "我们把地图画简单一点。一条河，把城市分成了四块陆地；七座桥，把它们连在一起。",
    "h2": "当地人有个消遣：每座桥恰好走一次，把全城走遍。",
    "h3": "我们来试一条路线。你看，走着走着，总有一座桥被落下——就是这座红色的桥。",
    "h4": "【慢】要弄清楚的是：是路线没找对，还是这件事根本做不到。",
    # parts
    "q0": "这一期分三部分来讲。",
    "q1": "第一部分，欧拉怎样把地图变成网络，以及网络里的边有哪些种类。",
    "q2": "第二部分，怎样用矩阵来表示网络，并且用矩阵做计算。",
    "q3": "第三部分，生物医学里常见的二分网络，以及真实网络的稀疏性。",
    # Euler
    "e1": "先看第一部分。欧拉的做法，是把地图上的细节统统扔掉。",
    "e2": "每块陆地缩成一个点，叫作节点；每座桥变成一条线，叫作边。",
    "e3": "陆地多大、桥有多长，都不重要了。剩下的，只有谁和谁相连。",
    "e4": "现在数一数，每个点连着几条线。这个数，叫作节点的度，也就是它的连接数。",
    "e4b": "四个点的度，分别是五、三、三、三。",
    "e5": "一笔走下去，每路过一个点，都要一进一出，也就是成对地用掉两条线。",
    "e6": "所以，除了起点和终点，其余点的度都必须是偶数。也就是说，度是奇数的点，最多只能有两个。",
    "e7": "【慢】七桥图里，四个点的度全是奇数。所以答案是：不可能。",
    "e8": "这是图论的起点，也是网络思维的核心：结构本身，就限制了系统能做什么。",
    # same graph, different systems
    "g1": "下面看，节点和边能描述什么。这张小图有四个节点、四条边，它可以是四个相互结合的蛋白质。",
    "g2": "也可以是四个脑区，或者一位患者身上，相互牵连的四个症状。",
    "g2b": "比如脑区之间的连接，可以用弥散磁共振，追踪大脑里的白质纤维束来测量。",
    "g3": "边也有不同的性质。蛋白质之间的结合是相互的，用没有方向的线表示，叫无向边。",
    "g4": "转录因子调控靶基因，作用有方向，用带箭头的线表示，叫有向边。",
    "g5": "脑区之间的功能连接有强有弱，可以给每条边一个数值，叫加权边。",
    "g5b": "调控有激活，也有抑制，就给边带上正号或负号，叫符号边。",
    "g6": "【慢】选什么做节点、什么做边，其实就是在选你要回答的科学问题。",
    # adjacency matrix
    "a1": "下面进入第二部分。要让计算机处理网络，最常用的办法，是写成一张表，叫邻接矩阵。",
    "a2": "左边是刚才的小网络，节点编号一到四。右边这张表，行和列都对应这四个节点。",
    "a2b": "规则很简单：两个节点之间有边，对应的格子就填一；没有边，就填零。",
    "a3": "比如一号和二号相连。所以第一行第二列是一，第二行第一列也是一。",
    "a4": "无向网络的邻接矩阵总是对称的。沿着这条对角线翻折，两边完全一样。",
    "a5": "把一行的数加起来，就是这个节点的度。三号连了三条边，它那一行的和就是三。",
    "a6": "【慢】所有节点的度加起来是八，正好是边数四的两倍。因为每条边有两个端点，被数了两次。",
    # powers
    "w1": "邻接矩阵还能做运算。把它和自己相乘，就得到右边这张新表。",
    "w1b": "新表里的每个数，表示两个节点之间，走两步的路线一共有几条。",
    "w2": "比如一号到四号。走两步，只能经过三号，只有这一条路，所以这个格子是一。",
    "w3": "也就是说，它数的是两个节点的共同邻居。共同邻居的数目，是预测新连接最简单的线索。",
    "w4": "再乘一次，得到走三步的路线数。注意对角线上的这四个数。",
    "w4b": "把它们加起来，再除以六，就是网络里三角形的个数。这里是一个，就是一、二、三号组成的三角形。",
    "w4c": "为什么除以六：每个三角形有三个顶点，从每个顶点出发，可以顺着绕一圈，也可以倒着绕一圈，所以一共被数了六次。",
    # Laplacian
    "l1": "再介绍一个重要的矩阵。先把每个节点的度，放在对角线上，得到一张表，叫度矩阵。",
    "l1b": "【慢】用度矩阵减去邻接矩阵，就是拉普拉斯矩阵。",
    "l1c": "看公式：左边这一项是度矩阵，右边这一项是邻接矩阵。所以对角线上是每个节点的度，有边的位置是负一。",
    "l1d": "这样一来，拉普拉斯矩阵每一行加起来，都正好是零。",
    "l2": "它的一个用处是描述扩散。想象每个节点上有一些热量，热量沿着边，从高处流向低处。这个扩散过程，就由拉普拉斯矩阵控制。",
    "l3": "这个思路已经用在医学里。有研究用这样的扩散模型，描述痴呆中的病理沿白质网络扩散，预测的萎缩分布，和患者的影像有显著对应。",
    "l4": "拉普拉斯矩阵还有一组特殊的数，叫特征值。这里不讲怎么算，只看它能告诉我们什么。这张小图的特征值是零、一、三、四。",
    "l4b": "【慢】规律是：零出现几次，网络就分成几块。这里零只出现一次，说明整张图是连在一起的。",
    "l5": "现在切断三号和四号之间的边。网络分成了两块，零就出现了两次。",
    # bipartite
    "b1": "最后是第三部分。生物医学里有一类很常见的网络：节点分成两类，边只连接不同类的节点，叫二分网络。",
    "b2": "比如药物和靶点。左边是三种药物，右边是四个靶点。每条线，表示这种药作用于这个靶点。",
    "b3": "如果两种药物作用于同一个靶点，就在它们之间连一条边，这叫投影。你看，药一和药二共用了靶点二，所以它们相连。",
    "b4": "人类疾病网络就是这样来的。2007年的一项研究，把一千二百八十四种疾病，和一千七百七十七个致病基因，连成一张二分网络。",
    "b4b": "再投影到疾病这一侧：两种疾病只要有共同的致病基因，就连一条边。",
    "b5": "但是，投影会丢掉信息。左边，是三种药物共用一个靶点；右边，是三种药物两两各共用一个不同的靶点。",
    "b5c": "【慢】两种情况完全不同，投影之后，却是同一个三角形。所以能直接分析二分网络时，最好不要急着投影。",
    # sparsity
    "s1": "第三部分的另一个问题，是网络的规模。设想一个有两万个蛋白质的网络，它的邻接矩阵，一共有四亿个格子。",
    "s2": "可如果只有二十万条边，填了一的格子只占大约千分之一，其余全是零。这样的网络，叫稀疏网络。",
    "s3": "真实网络几乎都是稀疏的。所以大网络通常存成边列表：每一行只记一条边，写下它两端的节点。",
    "s4": "看一个例子：一个七十万名演员的合作网络，存成稠密矩阵，要大约四太字节；存成边列表，只要几百兆。",
    # recap
    "r1": "好，我们来总结一下。",
    "r2": "第一，网络把系统抽象成节点和边，答案只取决于谁和谁相连。",
    "r3": "第二，邻接矩阵和拉普拉斯矩阵，让我们能用代数，算出度、路线数和连通性这些性质。",
    "r4": "第三，节点和边怎么选，决定了这张网络能回答什么问题。",
    "r5": "这个专题的知识页面里，有画面上的这个交互演示。依次点击两个节点，就能添加或删除它们之间的边，邻接矩阵和度序列会跟着变化。",
}

LAND = "#33503f"
WATER = "#1c3554"
BRIDGE = "#c9a26b"
# small example graph used throughout: nodes 1..4, edges 1-2, 1-3, 2-3, 3-4
EX_E = [(0, 1), (0, 2), (1, 2), (2, 3)]
EX_P = [np.array(p) for p in ([-1.0, 1.0, 0], [1.0, 1.0, 0], [0.0, -0.3, 0], [0.0, -2.0, 0])]


def ex_adj():
    A = np.zeros((4, 4), int)
    for u, v in EX_E:
        A[u, v] = A[v, u] = 1
    return A


class ExGraph(VGroup):
    def __init__(self, shift=ORIGIN, scale=1.0, color=BLUE, edges=EX_E):
        super().__init__()
        self.P = [p * scale + shift for p in EX_P]
        self.nodes = [node(p, i + 1, color, r=0.3 * scale ** 0.5, size=int(26 * scale ** 0.5)) for i, p in enumerate(self.P)]
        self.lines = {e: edge_line(self.P[e[0]], self.P[e[1]], r=0.3 * scale ** 0.5, color=MUTED, w=4) for e in edges}
        self.add(VGroup(*self.lines.values()), VGroup(*self.nodes))


class Episode(Narrated):
    LINES = LINES

    def construct(self):
        self.hook()
        self.parts()
        self.euler()
        self.languages()
        self.adjacency()
        self.powers()
        self.laplacian()
        self.bipartite()
        self.sparse()
        self.recap()

    # ------------------------------------------------------------------ hook
    def hook(self):
        water = Rectangle(width=15, height=3.4, fill_color=WATER, fill_opacity=1, stroke_width=0)
        north = Rectangle(width=15, height=2.4, fill_color=LAND, fill_opacity=1, stroke_width=0).next_to(water, UP, buff=0)
        south = Rectangle(width=15, height=2.4, fill_color=LAND, fill_opacity=1, stroke_width=0).next_to(water, DOWN, buff=0)
        A = Ellipse(width=5.0, height=1.6, fill_color=LAND, fill_opacity=1, stroke_width=0).move_to([-2.6, 0, 0])
        D = Ellipse(width=3.2, height=1.7, fill_color=LAND, fill_opacity=1, stroke_width=0).move_to([3.7, 0, 0])
        lands = VGroup(north, south, A, D)
        bpts = [((-4.0, 0.3), (-4.0, 1.9)), ((-1.2, 0.3), (-1.2, 1.9)), ((-4.0, -0.3), (-4.0, -1.9)),
                ((-1.2, -0.3), (-1.2, -1.9)), ((-0.4, 0), (2.4, 0)), ((3.7, 0.5), (3.7, 1.9)), ((3.7, -0.5), (3.7, -1.9))]
        bridges = [Line([*a, 0], [*b, 0], color=BRIDGE, stroke_width=16) for a, b in bpts]
        with self.say("h0") as d:
            self.clip_on("yt_konigsberg_teded.mp4", "center", "视频：TED-Ed · YouTube", start=20)
        self.clip_off()
        with self.say("h1") as d:
            self.play(FadeIn(water), FadeIn(north), FadeIn(south), run_time=1.0)
            self.play(FadeIn(A), FadeIn(D), run_time=0.8)
            self.play(LaggedStart(*[Create(b) for b in bridges], lag_ratio=0.25), run_time=d * 0.5)
        # walker path: C -b0-> A -b2-> B -b3-> A -b1-> C -b5-> D -b4-> A ; b6 left over
        path = [(-4, 2.6), (-4, 0), (-4, -2.6), (-1.2, -2.6), (-1.2, 0), (-1.2, 2.6), (3.7, 2.6), (3.7, 0), (-0.4, 0)]
        used = [0, 2, None, 3, 1, None, 5, 4]
        walker = Dot([*path[0], 0], radius=0.16, color=GOLD)
        with self.say("h2") as d:
            self.play(FadeIn(walker, scale=2), run_time=0.6)
            for i in range(3):
                anims = [walker.animate.move_to([*path[i + 1], 0])]
                if used[i] is not None:
                    anims.append(bridges[used[i]].animate.set_color(GOLD))
                self.play(*anims, run_time=0.55)
        with self.say("h3") as d:
            for i in range(3, len(path) - 1):
                anims = [walker.animate.move_to([*path[i + 1], 0])]
                if used[i] is not None:
                    anims.append(bridges[used[i]].animate.set_color(GOLD))
                self.play(*anims, run_time=0.5)
            self.play(bridges[6].animate.set_color(RED).set_stroke(width=22), rate_func=there_and_back, run_time=0.8)
            self.play(bridges[6].animate.set_color(RED), run_time=0.3)
        with self.say("h4") as d:
            q = T("走得通，还是走不通", 44, GOLD, weight=BOLD).move_to([0.6, 2.6, 0])
            self.play(FadeIn(q, scale=0.5), run_time=0.8)
        self.play(FadeOut(q), FadeOut(walker), *[b.animate.set_color(BRIDGE) for b in bridges], run_time=0.6)
        self.km = (water, lands, bridges, A, D, north, south)
        self.play(*[m.animate.set_opacity(0.0) for m in (water, *lands, *bridges)], run_time=0.6)
        self.remove(water, *lands, *bridges)

    def parts(self):
        parts_slide(self, "这一期分三部分", ["一  从七桥到网络：节点、边和边的种类", "二  用矩阵表示网络、做计算", "三  二分网络与稀疏性"])
        water, lands, bridges, A, D, north, south = self.km
        for m in (water, *lands, *bridges):
            m.set_opacity(1)
        self.play(FadeIn(water), FadeIn(lands), *[FadeIn(b) for b in bridges], run_time=0.8)

    # ------------------------------------------------------------------ Euler
    def euler(self):
        water, lands, bridges, A, D, north, south = self.km
        tag = self.chapter("第一部分 · 欧拉的抽象")
        P = {"A": np.array([-2.6, 0, 0]), "C": np.array([0, 2.6, 0]), "B": np.array([0, -2.6, 0]), "D": np.array([3.7, 0, 0])}
        with self.say("e1") as d:
            self.play(FadeIn(tag), water.animate.set_fill(opacity=0.25), lands.animate.set_fill(opacity=0.35), run_time=d * 0.6)
        dots = {k: Dot(p, radius=0.22, color=BLUE) for k, p in P.items()}
        E = [("A", "C", 0.45), ("A", "C", -0.45), ("A", "B", -0.45), ("A", "B", 0.45), ("A", "D", 0), ("D", "C", 0), ("D", "B", 0)]
        arcs = [edge_line(P[u], P[v], color=INK, w=4, angle=a) for u, v, a in E]
        with self.say("e2") as d:
            self.play(Transform(A, dots["A"]), Transform(D, dots["D"]),
                      Transform(north, dots["C"]), Transform(south, dots["B"]), run_time=1.4)
            self.play(*[Transform(b, a) for b, a in zip(bridges, arcs)], run_time=1.4)
        with self.say("e3") as d:
            self.play(FadeOut(water), run_time=1.0)
        lab_pos = {"A": LEFT, "C": UP, "B": DOWN, "D": RIGHT}
        deg = {"A": 5, "B": 3, "C": 3, "D": 3}
        dl = {k: T(str(deg[k]), 40, GOLD, weight=BOLD).next_to(P[k], lab_pos[k], buff=0.3) for k in P}
        with self.say("e4") as d:
            self.play(Indicate(A, color=GOLD, scale_factor=1.6), *[Indicate(bridges[i], color=GOLD) for i in range(5)], run_time=1.4)
        with self.say("e4b") as d:
            self.play(LaggedStart(*[FadeIn(dl[k], scale=1.4) for k in ("A", "C", "B", "D")], lag_ratio=0.5), run_time=d * 0.7)
        with self.say("e5") as d:
            # pair up the edges at A
            self.play(bridges[0].animate.set_color(GREEN), bridges[2].animate.set_color(GREEN), run_time=0.9)
            self.play(bridges[1].animate.set_color(VIOLET), bridges[3].animate.set_color(VIOLET), run_time=0.9)
            self.play(bridges[4].animate.set_color(RED), run_time=0.7)
        with self.say("e6") as d:
            rule = T("奇数度的点 ≤ 2 个", 34, INK).move_to([3.6, -1.6, 0])
            self.play(FadeIn(rule, shift=UP * 0.2), run_time=1.0)
        with self.say("e7") as d:
            self.play(*[A.animate.set_color(RED), D.animate.set_color(RED), north.animate.set_color(RED), south.animate.set_color(RED)],
                      *[x.animate.set_color(RED) for x in dl.values()], run_time=1.0)
            no = T("不可能", 44, RED, weight=BOLD).move_to([3.6, -2.5, 0])
            self.play(Write(no), run_time=0.8)
        with self.say("e8") as d:
            self.wait(0.5)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ languages
    def languages(self):
        tag = self.chapter("第一部分 · 同一张图，不同的系统")
        g = ExGraph(shift=UP * 0.4)
        names = [["蛋白", "蛋白", "蛋白", "蛋白"], ["脑区", "脑区", "脑区", "脑区"], ["失眠", "疲劳", "情绪低落", "注意力差"]]
        cols = [BLUE, VIOLET, GOLD]
        dirs = [LEFT, RIGHT, LEFT, DOWN]

        def labels(k):
            return VGroup(*[T(s, 24, cols[k]).next_to(g.P[i], dirs[i], buff=0.45) for i, s in enumerate(names[k])])
        with self.say("g1") as d:
            self.play(FadeIn(tag), FadeIn(g), run_time=1.2)
            L = labels(0)
            self.play(FadeIn(L), *[n[0].animate.set_color(BLUE) for n in g.nodes], run_time=1.0)
        with self.say("g2") as d:
            for k in (1, 2):
                L2 = labels(k)
                self.play(Transform(L, L2), *[n[0].animate.set_color(cols[k]).set_fill(cols[k], 0.25) for n in g.nodes], run_time=1.0)
                self.wait(0.8)
        self.play(FadeOut(L), FadeOut(g), run_time=0.6)
        with self.say("g2b") as d:
            self.clip_on("yt_tractography_usc.mp4", "center", "视频：USC Stevens Neuroimaging and Informatics Institute · YouTube", start=10)
        self.clip_off()
        # four edge types
        xs = [-4.8, -1.6, 1.6, 4.8]
        a, b = np.array([-0.9, 0, 0]), np.array([0.9, 0, 0])

        def pair(x, ca=BLUE, cb=BLUE):
            return VGroup(Dot(a + RIGHT * x, radius=0.16, color=ca), Dot(b + RIGHT * x, radius=0.16, color=cb))
        p1 = VGroup(pair(xs[0]), Line(a + RIGHT * xs[0], b + RIGHT * xs[0], color=INK, stroke_width=4))
        l1 = T("无向：蛋白结合", 24, INK).next_to(p1, DOWN, buff=0.6)
        p2 = VGroup(pair(xs[1], GOLD, BLUE), Arrow(a + RIGHT * xs[1], b + RIGHT * xs[1], buff=0.18, color=INK, stroke_width=4))
        l2 = T("有向：转录调控", 24, INK).next_to(p2, DOWN, buff=0.6)
        p3 = VGroup(VGroup(Dot([xs[2] - 0.9, 0.5, 0], radius=0.14, color=VIOLET), Dot([xs[2] + 0.9, 0.5, 0], radius=0.14, color=VIOLET),
                           Line([xs[2] - 0.9, 0.5, 0], [xs[2] + 0.9, 0.5, 0], color=INK, stroke_width=9)),
                    VGroup(Dot([xs[2] - 0.9, -0.5, 0], radius=0.14, color=VIOLET), Dot([xs[2] + 0.9, -0.5, 0], radius=0.14, color=VIOLET),
                           Line([xs[2] - 0.9, -0.5, 0], [xs[2] + 0.9, -0.5, 0], color=INK, stroke_width=2)))
        l3 = T("加权：功能连接", 24, INK).next_to(p3, DOWN, buff=0.4)
        up = VGroup(Dot([xs[3] - 0.9, 0.5, 0], radius=0.14, color=GOLD), Dot([xs[3] + 0.9, 0.5, 0], radius=0.14, color=BLUE),
                    Arrow([xs[3] - 0.9, 0.5, 0], [xs[3] + 0.9, 0.5, 0], buff=0.16, color=GREEN, stroke_width=4),
                    T("+", 30, GREEN, weight=BOLD).move_to([xs[3], 0.85, 0]))
        hb = Line([xs[3] - 0.75, -0.5, 0], [xs[3] + 0.72, -0.5, 0], color=RED, stroke_width=4)
        bar = Line([xs[3] + 0.72, -0.7, 0], [xs[3] + 0.72, -0.3, 0], color=RED, stroke_width=5)
        dn = VGroup(Dot([xs[3] - 0.9, -0.5, 0], radius=0.14, color=GOLD), Dot([xs[3] + 0.9, -0.5, 0], radius=0.14, color=BLUE), hb, bar,
                    T("−", 30, RED, weight=BOLD).move_to([xs[3], -0.15, 0]))
        p4 = VGroup(up, dn)
        l4 = T("符号：激活 / 抑制", 24, INK).next_to(p4, DOWN, buff=0.4)
        for l in (l1, l2):
            l.align_to(l3, UP)
        with self.say("g3") as d:
            self.play(FadeIn(p1), FadeIn(l1), run_time=1.0)
        with self.say("g4") as d:
            self.play(FadeIn(p2[0]), GrowArrow(p2[1]), FadeIn(l2), run_time=1.0)
        with self.say("g5") as d:
            self.play(FadeIn(p3), FadeIn(l3), run_time=1.0)
        with self.say("g5b") as d:
            self.play(FadeIn(p4), FadeIn(l4), run_time=1.0)
        with self.say("g6") as d:
            self.play(Indicate(VGroup(l1, l2, l3, l4), color=GOLD, scale_factor=1.05), run_time=1.4)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ adjacency matrix
    def adjacency(self):
        tag = self.chapter("第二部分 · 邻接矩阵")
        g = ExGraph(shift=LEFT * 4.2 + UP * 0.5)
        A = ex_adj()
        G = Grid(np.zeros((4, 4), int), cell=0.8, size=32, labels=[1, 2, 3, 4]).move_to(RIGHT * 1.6 + DOWN * 0.1)
        for r in G.nums:
            for t in r:
                t.set_opacity(0)
        with self.say("a1") as d:
            self.play(FadeIn(tag), FadeIn(g), run_time=1.0)
            self.play(FadeIn(G), run_time=1.0)
        with self.say("a2") as d:
            self.play(Indicate(G.rlab, color=GOLD), Indicate(G.clab, color=GOLD), run_time=1.2)
        with self.say("a2b") as d:
            self.play(LaggedStart(*[G.nums[i][j].animate.set_opacity(1) for i in range(4) for j in range(4)], lag_ratio=0.03), run_time=1.2)
        with self.say("a3") as d:
            self.play(g.lines[(0, 1)].animate.set_color(GOLD).set_stroke(width=7), g.nodes[0][0].animate.set_color(GOLD),
                      g.nodes[1][0].animate.set_color(GOLD), run_time=0.6)
            self.play(G.hl(0, 1), G.set_num(0, 1, 1), run_time=0.7)
            self.play(G.hl(1, 0), G.set_num(1, 0, 1), run_time=0.7)
            self.play(g.lines[(0, 1)].animate.set_color(MUTED).set_stroke(width=4), g.nodes[0][0].animate.set_color(BLUE),
                      g.nodes[1][0].animate.set_color(BLUE), G.boxes[0][1].animate.set_fill(BG, 1), G.boxes[1][0].animate.set_fill(BG, 1),
                      run_time=0.4)
            for (u, v) in EX_E[1:]:
                self.play(Indicate(g.lines[(u, v)], color=GOLD), G.set_num(u, v, 1, INK), G.set_num(v, u, 1, INK), run_time=0.5)
            for i in range(4):
                for j in range(4):
                    if A[i, j]:
                        G.nums[i][j].set_color(INK)
        with self.say("a4") as d:
            diag = DashedLine(G.boxes[0][0].get_corner(UL), G.boxes[3][3].get_corner(DR), color=GOLD, stroke_width=3)
            self.play(Create(diag), run_time=0.8)
            pairs = [(i, j) for i in range(4) for j in range(4) if i < j and A[i, j]]
            self.play(*[G.hl(i, j, BLUE, 0.35) for i, j in pairs], *[G.hl(j, i, BLUE, 0.35) for i, j in pairs], run_time=0.9)
            self.play(*[G.boxes[i][j].animate.set_fill(BG, 1) for i, j in pairs], *[G.boxes[j][i].animate.set_fill(BG, 1) for i, j in pairs],
                      FadeOut(diag), run_time=0.6)
        sums = VGroup(*[T(str(A[i].sum()), 32, GOLD, weight=BOLD).next_to(G.boxes[i][3], RIGHT, buff=0.55) for i in range(4)])
        sh = T("度", 26, GOLD).next_to(sums[0], UP, buff=0.3)
        with self.say("a5") as d:
            row = SurroundingRectangle(VGroup(*G.boxes[2]), color=GOLD, buff=0.04)
            self.play(Create(row), Indicate(g.nodes[2], color=GOLD), run_time=0.8)
            self.play(FadeIn(sh), FadeIn(sums[2], shift=RIGHT * 0.3), run_time=0.7)
            self.play(FadeOut(row), LaggedStart(*[FadeIn(sums[i]) for i in (0, 1, 3)], lag_ratio=0.3), run_time=1.0)
        with self.say("a6") as d:
            tot = MathTex(r"2+2+3+1=8=2\times 4", font_size=40, color=INK).next_to(G, DOWN, buff=0.55).shift(RIGHT * 0.3)
            self.play(Write(tot), run_time=1.4)
        self.play(FadeOut(tot), FadeOut(sums), FadeOut(sh), FadeOut(G), run_time=0.6)
        self.g = g

    # ------------------------------------------------------------------ matrix powers
    def powers(self):
        tag = self.chapter("第二部分 · 矩阵相乘：数路线")
        g = self.g
        A = ex_adj()
        A2, A3 = A @ A, A @ A @ A
        G2 = Grid(A2, cell=0.8, size=32, labels=[1, 2, 3, 4]).move_to(RIGHT * 1.6 + DOWN * 0.1)
        lab = MathTex(r"A^2", font_size=48, color=GOLD).next_to(G2, UP, buff=0.5)
        with self.say("w1") as d:
            self.play(FadeIn(tag), run_time=0.5)
            self.play(FadeIn(G2), Write(lab), run_time=1.4)
        with self.say("w1b") as d:
            self.play(Indicate(G2, color=GOLD, scale_factor=1.03), run_time=1.2)
        with self.say("w2") as d:
            self.play(G2.hl(0, 3), run_time=0.6)
            walker = Dot(g.P[0], radius=0.13, color=GOLD)
            e1 = edge_line(g.P[0], g.P[2], r=0.3, color=GOLD, w=7)
            e2 = edge_line(g.P[2], g.P[3], r=0.3, color=GOLD, w=7)
            self.play(FadeIn(walker), run_time=0.3)
            self.play(walker.animate.move_to(g.P[2]), Create(e1), run_time=0.8)
            self.play(walker.animate.move_to(g.P[3]), Create(e2), run_time=0.8)
            self.play(Indicate(G2.nums[0][3], color=GOLD, scale_factor=1.6), run_time=0.8)
        with self.say("w3") as d:
            ring = Circle(radius=0.45, color=GREEN, stroke_width=5).move_to(g.P[2])
            self.play(Create(ring), FadeOut(walker), run_time=0.8)
            cn = T("共同邻居", 26, GREEN).next_to(ring, RIGHT, buff=0.2)
            self.play(FadeIn(cn), run_time=0.6)
        self.play(FadeOut(ring), FadeOut(cn), FadeOut(e1), FadeOut(e2), G2.boxes[0][3].animate.set_fill(BG, 1), run_time=0.5)
        G3 = Grid(A3, cell=0.8, size=32, labels=[1, 2, 3, 4]).move_to(G2)
        lab3 = MathTex(r"A^3", font_size=48, color=GOLD).move_to(lab)
        with self.say("w4") as d:
            self.play(ReplacementTransform(G2, G3), Transform(lab, lab3), run_time=1.0)
            self.play(*[G3.hl(i, i) for i in range(4)], run_time=0.6)
        tr = MathTex(r"\frac{%d+%d+%d+%d}{6}=%d" % (A3[0, 0], A3[1, 1], A3[2, 2], A3[3, 3], np.trace(A3) // 6),
                     font_size=40, color=INK).next_to(G3, DOWN, buff=0.45)
        with self.say("w4b") as d:
            self.play(Write(tr), run_time=1.2)
            tri = Polygon(g.P[0], g.P[1], g.P[2], color=GOLD, fill_color=GOLD, fill_opacity=0.3, stroke_width=0)
            self.play(FadeIn(tri), run_time=0.8)
        with self.say("w4c") as d:
            arc1 = CurvedArrow(g.P[0] + RIGHT * 0.35 + DOWN * 0.1, g.P[1] + LEFT * 0.35 + DOWN * 0.1, angle=-0.8, color=GREEN)
            arc2 = CurvedArrow(g.P[1] + LEFT * 0.35 + UP * 0.25, g.P[0] + RIGHT * 0.35 + UP * 0.25, angle=-0.8, color=VIOLET)
            six = T("3 个顶点 × 2 个方向 = 6", 26, GOLD).next_to(tr, DOWN, buff=0.3)
            self.play(Create(arc1), run_time=0.8)
            self.play(Create(arc2), run_time=0.8)
            self.play(FadeIn(six), run_time=0.6)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ Laplacian
    def laplacian(self):
        tag = self.chapter("第二部分 · 拉普拉斯矩阵")
        A = ex_adj()
        L = np.diag(A.sum(1)) - A
        GL = Grid(L, cell=0.72, size=28, labels=[1, 2, 3, 4], fmt=lambda x: f"{x:d}" if x >= 0 else f"−{-x:d}").move_to(LEFT * 0.4 + DOWN * 0.1)
        eq = MathTex(r"L", r"=", r"D", r"-", r"A", font_size=56, color=INK).next_to(GL, UP, buff=0.45)
        eq[2].set_color(GOLD); eq[4].set_color(BLUE)
        zs = VGroup(*[T("0", 30, GREEN, weight=BOLD).next_to(GL.boxes[i][3], RIGHT, buff=0.55) for i in range(4)])
        zh = T("行和", 24, GREEN).next_to(zs[0], UP, buff=0.3)
        GD = Grid(np.diag(A.sum(1)), cell=0.72, size=28, labels=[1, 2, 3, 4]).move_to(GL)
        with self.say("l1") as d:
            self.play(FadeIn(tag), FadeIn(GD), run_time=1.0)
            self.play(*[GD.hl(i, i) for i in range(4)], run_time=0.8)
        with self.say("l1b") as d:
            self.play(ReplacementTransform(GD, GL), Write(eq), run_time=1.4)
        with self.say("l1c") as d:
            ld = T("度矩阵", 24, GOLD).move_to(eq[2].get_center() + UP * 0.95 + LEFT * 0.9)
            la = T("邻接矩阵", 24, BLUE).move_to(eq[4].get_center() + UP * 0.95 + RIGHT * 1.0)
            ad = Arrow(ld.get_bottom(), eq[2].get_top(), buff=0.08, color=GOLD, stroke_width=3, max_tip_length_to_length_ratio=0.3)
            aa = Arrow(la.get_bottom(), eq[4].get_top(), buff=0.08, color=BLUE, stroke_width=3, max_tip_length_to_length_ratio=0.3)
            self.play(FadeIn(ld), GrowArrow(ad), run_time=0.7)
            self.play(FadeIn(la), GrowArrow(aa), run_time=0.7)
            self.play(*[GL.hl(i, i, GOLD) for i in range(4)], run_time=0.6)
            self.play(*[GL.hl(i, j, BLUE) for i in range(4) for j in range(4) if A[i, j]], run_time=0.6)
        with self.say("l1d") as d:
            self.play(FadeIn(zh), LaggedStart(*[FadeIn(z) for z in zs], lag_ratio=0.2), run_time=1.2)
        self.play(FadeOut(VGroup(GL, eq, zs, zh, ld, la, ad, aa)), run_time=0.6)
        # diffusion on a small spatial network
        H = nx.random_geometric_graph(46, 0.3, seed=4)
        H = H.subgraph(max(nx.connected_components(H), key=len)).copy()
        H = nx.convert_node_labels_to_integers(H)
        raw = {v: np.array(H.nodes[v]["pos"]) for v in H}
        P = np.array(list(raw.values())); lo, hi = P.min(0), P.max(0)
        pos = {v: np.array([-5.6 + 11.2 * (p[0] - lo[0]) / (hi[0] - lo[0]), -3.0 + 5.6 * (p[1] - lo[1]) / (hi[1] - lo[1]), 0]) for v, p in raw.items()}
        LH = nx.laplacian_matrix(H).toarray().astype(float)
        w, V = np.linalg.eigh(LH)
        src = min(H, key=lambda v: pos[v][0])
        x0 = np.zeros(len(H)); x0[src] = 1.0
        cold, hot = ManimColor("#2a3a55"), ManimColor(RED)

        def heat(t):
            x = V @ (np.exp(-w * t) * (V.T @ x0))
            return x / max(x.max(), 1e-9)
        edges = VGroup(*[Line(pos[u], pos[v], color=MUTED, stroke_width=1.5, stroke_opacity=0.4) for u, v in H.edges()])
        dots = [Dot(pos[v], radius=0.12, color=cold) for v in H]
        tt = ValueTracker(0.0)
        for v, dt in enumerate(dots):
            dt.add_updater(lambda m, v=v: m.set_color(interpolate_color(cold, hot, float(np.clip(heat(tt.get_value())[v] ** 0.5, 0, 1)))))
        with self.say("l2") as d:
            self.play(Create(edges), *[FadeIn(x) for x in dots], run_time=1.0)
            self.play(tt.animate.set_value(0.02), run_time=0.4)
            self.play(tt.animate.set_value(6.0), run_time=d - 1.6, rate_func=lambda s: s ** 2)
        with self.say("l3") as d:
            self.play(tt.animate.set_value(0.0), run_time=0.8)
            self.play(tt.animate.set_value(10.0), run_time=d * 0.7, rate_func=lambda s: s ** 2)
        for x in dots:
            x.clear_updaters()
        self.play(FadeOut(edges), *[FadeOut(x) for x in dots], run_time=0.6)
        # eigenvalues
        g = ExGraph(shift=LEFT * 3.6 + UP * 0.5)
        ev = np.round(np.linalg.eigvalsh(L)).astype(int)
        L2 = L.copy(); L2[2, 3] = L2[3, 2] = 0; L2[2, 2] -= 1; L2[3, 3] -= 1
        ev2 = np.round(np.linalg.eigvalsh(L2)).astype(int)

        def evrow(vals):
            cells = VGroup(*[T(str(x), 44, GOLD if x == 0 else INK, weight=BOLD) for x in vals]).arrange(RIGHT, buff=0.6)
            return cells
        head = T("特征值", 28, MUTED).move_to(RIGHT * 2.8 + UP * 1.4)
        r1 = evrow(ev).next_to(head, DOWN, buff=0.45)
        with self.say("l4") as d:
            self.play(FadeIn(g), FadeIn(head), run_time=0.8)
            self.play(LaggedStart(*[FadeIn(x, shift=UP * 0.2) for x in r1], lag_ratio=0.3), run_time=1.4)
        with self.say("l4b") as d:
            self.play(Circumscribe(r1[0], color=GOLD), run_time=1.0)
        with self.say("l5") as d:
            cut = Cross(g.lines[(2, 3)], stroke_color=RED, scale_factor=0.5)
            self.play(Create(cut), run_time=0.6)
            self.play(FadeOut(g.lines[(2, 3)]), FadeOut(cut), g.nodes[3].animate.shift(DOWN * 0.3 + RIGHT * 0.6), run_time=0.8)
            r2 = evrow(ev2).move_to(r1)
            self.play(Transform(r1, r2), run_time=1.0)
            self.play(Circumscribe(VGroup(r1[0], r1[1]), color=GOLD), run_time=1.0)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ bipartite
    def bipartite(self):
        tag = self.chapter("第三部分 · 二分网络与投影")
        B = np.array([[1, 1, 0, 0], [0, 1, 1, 0], [0, 0, 0, 1]])
        dp = [np.array([-4.2, 1.6 - 1.6 * i, 0]) for i in range(3)]
        tp = [np.array([-1.0, 2.1 - 1.4 * j, 0]) for j in range(4)]
        drugs = [VGroup(Square(0.55, color=GOLD, fill_color=GOLD, fill_opacity=0.25, stroke_width=3).move_to(p),
                        T(f"药{i + 1}", 22, INK).move_to(p)) for i, p in enumerate(dp)]
        targs = [VGroup(Circle(radius=0.3, color=GREEN, fill_color=GREEN, fill_opacity=0.25, stroke_width=3).move_to(p),
                        T(f"靶{j + 1}", 20, INK).move_to(p)) for j, p in enumerate(tp)]
        bl = {(i, j): edge_line(dp[i], tp[j], r=0.32, color=MUTED, w=3) for i in range(3) for j in range(4) if B[i, j]}
        with self.say("b1") as d:
            self.play(FadeIn(tag), LaggedStart(*[FadeIn(x) for x in drugs], lag_ratio=0.2), run_time=1.0)
            self.play(LaggedStart(*[FadeIn(x) for x in targs], lag_ratio=0.2), run_time=1.0)
        with self.say("b2") as d:
            self.play(LaggedStart(*[Create(l) for l in bl.values()], lag_ratio=0.2), run_time=1.6)
        # projection onto drugs
        pp = [np.array([3.0, 1.4, 0]), np.array([5.0, 1.4, 0]), np.array([4.0, -0.6, 0])]
        pd = [VGroup(Square(0.55, color=GOLD, fill_color=GOLD, fill_opacity=0.25, stroke_width=3).move_to(p),
                     T(f"药{i + 1}", 22, INK).move_to(p)) for i, p in enumerate(pp)]
        pe = edge_line(pp[0], pp[1], r=0.32, color=GOLD, w=5)
        arrow = Arrow(LEFT * 0.2, RIGHT * 1.4, color=MUTED).move_to([1.0, 0.4, 0])
        with self.say("b3") as d:
            self.play(bl[(0, 1)].animate.set_color(GOLD).set_stroke(width=5), bl[(1, 1)].animate.set_color(GOLD).set_stroke(width=5),
                      Indicate(targs[1], color=GOLD), run_time=1.0)
            self.play(GrowArrow(arrow), *[FadeIn(x) for x in pd], run_time=0.9)
            self.play(Create(pe), run_time=0.7)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.6)
        # disease network numbers
        c1 = counter("疾病", "1284 种", BLUE, vs=48).move_to(LEFT * 3.2 + UP * 0.4)
        c2 = counter("致病基因", "1777 个", GREEN, vs=48).move_to(RIGHT * 3.2 + UP * 0.4)
        yr = T("2007", 30, MUTED).move_to(UP * 2.4)
        rng = np.random.default_rng(3)
        dl = VGroup(*[Dot([rng.uniform(-5, -1.4), rng.uniform(-3.2, -1.4), 0], radius=0.05, color=BLUE) for _ in range(40)])
        gl = VGroup(*[Dot([rng.uniform(1.4, 5), rng.uniform(-3.2, -1.4), 0], radius=0.05, color=GREEN) for _ in range(50)])
        links = VGroup(*[Line(dl[rng.integers(40)].get_center(), gl[rng.integers(50)].get_center(), stroke_width=0.8,
                              color=MUTED, stroke_opacity=0.35) for _ in range(70)])
        with self.say("b4") as d:
            self.play(FadeIn(yr), FadeIn(c1), FadeIn(c2), run_time=1.0)
            self.play(FadeIn(dl), FadeIn(gl), run_time=0.8)
            self.play(Create(links, lag_ratio=0.02), run_time=d * 0.35)
        with self.say("b4b") as d:
            self.play(FadeOut(gl), FadeOut(c2), links.animate.set_stroke(opacity=0.1), run_time=0.8)
            dd = [dl[i].get_center() for i in range(40)]
            proj = VGroup(*[Line(dd[i], dd[j], color=BLUE, stroke_width=1.2, stroke_opacity=0.6) for i, j in
                            [(int(a), int(b)) for a, b in np.random.default_rng(4).integers(0, 40, (30, 2)) if a != b]])
            self.play(FadeOut(links), Create(proj), run_time=1.4)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.6)
        # information loss: two different bipartite graphs, same projection

        def bip(x0, edges, ntar):
            ds = [np.array([x0 - 1.2 + 1.2 * i, 1.6, 0]) for i in range(3)]
            ts = [np.array([x0 - 0.6 * (ntar - 1) + 1.2 * j, 0.0, 0]) for j in range(ntar)]
            g = VGroup(*[Square(0.45, color=GOLD, fill_color=GOLD, fill_opacity=0.25, stroke_width=3).move_to(p) for p in ds],
                       *[Circle(radius=0.24, color=GREEN, fill_color=GREEN, fill_opacity=0.25, stroke_width=3).move_to(p) for p in ts],
                       *[edge_line(ds[i], ts[j], r=0.26, color=MUTED, w=3) for i, j in edges])
            tri = VGroup(*[edge_line(a, b, r=0.26, color=GOLD, w=4) for a, b in
                           ((ds[0] + DOWN * 3.2, ds[1] + DOWN * 3.2 + UP * 0.9), (ds[1] + DOWN * 3.2 + UP * 0.9, ds[2] + DOWN * 3.2),
                            (ds[0] + DOWN * 3.2, ds[2] + DOWN * 3.2))],
                         *[Square(0.45, color=GOLD, fill_color=GOLD, fill_opacity=0.25, stroke_width=3).move_to(p) for p in
                           (ds[0] + DOWN * 3.2, ds[1] + DOWN * 3.2 + UP * 0.9, ds[2] + DOWN * 3.2)])
            return g, tri
        gA, tA = bip(-3.4, [(0, 0), (1, 0), (2, 0)], 1)
        gB, tB = bip(3.4, [(0, 0), (1, 0), (1, 1), (2, 1), (2, 2), (0, 2)], 3)
        eqs = T("=", 60, GOLD, weight=BOLD).move_to([0, -2.4, 0])
        with self.say("b5") as d:
            self.play(FadeIn(gA), run_time=0.8)
            self.wait(d * 0.3)
            self.play(FadeIn(gB), run_time=0.8)
        with self.say("b5c") as d:
            self.play(TransformFromCopy(gA, tA), TransformFromCopy(gB, tB), run_time=1.4)
            self.play(FadeIn(eqs, scale=1.5), run_time=0.6)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ sparsity
    def sparse(self):
        tag = self.chapter("第三部分 · 稀疏性")
        sq = Square(5.6, stroke_color=INK, stroke_width=2).move_to(LEFT * 2.6 + DOWN * 0.3)
        dim = T("20000 × 20000", 28, MUTED).next_to(sq, UP, buff=0.2)
        cells = counter("格子", "4 亿", INK, vs=44).move_to(RIGHT * 3.6 + UP * 1.4)
        with self.say("s1") as d:
            self.play(FadeIn(tag), Create(sq), FadeIn(dim), run_time=1.2)
            self.play(FadeIn(cells), run_time=0.8)
        rng = np.random.default_rng(5)
        n = 140
        pts = []
        for _ in range(n):
            x, y = rng.uniform(-2.7, 2.7, 2)
            pts += [(x, y), (-y, -x)]  # symmetric about the diagonal
        nz = VGroup(*[Square(0.06, stroke_width=0, fill_color=GOLD, fill_opacity=1).move_to(sq.get_center() + np.array([x, y, 0])) for x, y in pts])
        frac = counter("非零", "约千分之一", GOLD, vs=44).move_to(RIGHT * 3.6 + DOWN * 0.6)
        with self.say("s2") as d:
            self.play(LaggedStart(*[FadeIn(p) for p in nz], lag_ratio=0.01), run_time=1.6)
            self.play(FadeIn(frac), run_time=0.8)
        el = VGroup(*[Text(s, font="Source Code Pro", font_size=26, color=INK) for s in ("P1    P7", "P1    P12", "P2    P9", "P3    P7", "P4    P15", "⋯")]
                    ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        box = SurroundingRectangle(el, color=MUTED, buff=0.3, corner_radius=0.12)
        elg = VGroup(box, el).move_to(RIGHT * 3.6 + DOWN * 0.2)
        elh = T("边列表", 26, MUTED).next_to(box, UP, buff=0.2)
        with self.say("s3") as d:
            self.play(FadeOut(cells), FadeOut(frac), run_time=0.5)
            self.play(FadeIn(box), FadeIn(elh), LaggedStart(*[FadeIn(x, shift=LEFT * 0.3) for x in el], lag_ratio=0.2), run_time=1.6)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.6)
        # storage bars
        b1 = Rectangle(width=10.0, height=0.8, fill_color=RED, fill_opacity=0.85, stroke_width=0)
        b2 = Rectangle(width=0.02, height=0.8, fill_color=GREEN, fill_opacity=1, stroke_width=0)
        VGroup(b1, b2).arrange(DOWN, aligned_edge=LEFT, buff=1.1).move_to(DOWN * 0.3 + RIGHT * 0.3)
        t1 = T("稠密矩阵  约 4 TB", 28, INK).next_to(b1, UP, buff=0.15, aligned_edge=LEFT)
        t2 = T("边列表  几百 MB", 28, INK).next_to(b2, UP, buff=0.15, aligned_edge=LEFT)
        head = T("七十万名演员的合作网络", 28, MUTED).move_to(UP * 2.4)
        with self.say("s4") as d:
            self.play(FadeIn(head), run_time=0.6)
            self.play(GrowFromEdge(b1, LEFT), FadeIn(t1), run_time=1.2)
            self.play(FadeIn(b2), FadeIn(t2), run_time=0.8)
            self.play(Indicate(b2, color=GREEN, scale_factor=3), run_time=0.8)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ recap
    def recap(self):
        items = [("r2", BLUE, "节点 + 边：只看谁和谁相连"),
                 ("r3", GOLD, "邻接矩阵、拉普拉斯矩阵：用代数算结构"),
                 ("r4", GREEN, "怎么选节点和边 = 选科学问题")]
        head, rows = recap_rows(items)
        with self.say("r1") as d:
            self.play(Write(head), run_time=0.8)
        for (k, _, _), row in zip(items, rows):
            with self.say(k) as d:
                self.play(FadeIn(row, shift=RIGHT * 0.3), run_time=0.8)
        self.wait(0.8)
        self.play(FadeOut(rows), FadeOut(head), run_time=0.6)
        with self.say("r5") as d:
            self.clip_on("graph_matrix_demo.mp4", "full", "本站交互演示：图与邻接矩阵", start=0.3)
            if d < 10.6:
                self.wait(10.7 - d)
        self.clip_off()
        self.wait(1.0)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=1.0)
