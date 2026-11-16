"""Animated explainer: 网络分析流程与 NetworkX 实践."""
import random

import networkx as nx
import numpy as np

from common import *  # noqa: F401,F403
from kit_c import PANEL, NetView, arrow, axes, chip, clip_line, code_block, counter, fade_all, fit, grow_bars, hist_bars, parts, xlabel, ylabel

TITLE = "一项网络分析怎样做：流程、陷阱与 NetworkX 实践"

LINES = {
    # hook
    "h1": "三个基因，边上标的是相关系数。甲乙、乙丙都是零点九，很强；甲丙只有零点二，很弱。",
    "h2": "我们要看乙是不是甲和丙之间的桥梁。衡量桥梁作用的指标叫介数，它数的是有多少条最短路径经过这个节点。",
    "h3": "第一行代码，把相关系数直接当权重传进去。算出来，乙的介数是零。",
    "h4": "第二行代码，先换成距离再算。乙的介数变成了一。",
    "h4b": "【慢】同一张网络，两行代码，结论正好相反。",
    "h5": "这一期，我们把一项网络分析从头到尾走一遍，看看哪些地方容易踩坑。",
    "q0": "这一期分三部分。",
    "q1": "第一部分，网络分析的六个步骤。",
    "q2": "第二部分，读数据和算指标时的几个默认陷阱。",
    "q3": "第三部分，社团划分、零模型和作图。",
    # workflow
    "w1": "先看第一部分。第一步，提出具体的问题，比如某种疾病的相关蛋白，在互作网络里是否聚成模块。",
    "w2": "第二步，获取并清洗数据，比如统一基因的名字和编号。",
    "w2b": "数据常常来自公开数据库。画面里，是在一个蛋白质相互作用数据库中检索一组蛋白的网络。",
    "w2c": "第三步，构建网络：规定节点、边、方向、权重，以及阈值取多少。",
    "w3": "第四步，计算度、聚集系数、路径长度和中心性。第五步，做社团划分等分析，并和零模型比较。零模型，就是作为参照的随机网络。",
    "w4": "第六步，结合文献解释结果，讨论局限。每一步的选择，都要记下来。",
    "w5": "【慢】一条原则：从问题出发。下载一个数据库、画一张网络，本身还不是研究问题。",
    # reading
    "i1": "下面进入第二部分。先把数据读成图，最常见的格式是边列表：每行两个节点，代表一条边。",
    "i2": "邻接矩阵是节点乘节点的表格。每读一条边，对称的两个格子同时记为一。",
    "i3": "全部读完，每一行的和，就是这个节点的度，也就是连接数。",
    "i4": "生物网络大多很稀疏。两万个节点，稠密矩阵要约三千二百兆，稀疏格式只要约两兆。",
    "i5": "好习惯是先看数据，再算指标：打印节点数、边数、自环数和连通分支数。",
    # defaults
    "p1": "接下来是几个默认行为。自环是一条连回自己的边，它让节点的度加二。这里从三变成五。",
    "p2": "孤立点是没有边的节点。它拉低平均度，这里从二降到一点二五，还会让平均最短路径直接报错。",
    "p3": "再看方向。上面是一条调控链：有向时，中心性沿着方向递增；当成无向图，就变成首尾对称。",
    # weights
    "q1": "最隐蔽的是权重。最短路径和介数把权重当距离：越大越远。",
    "q2": "可相关系数和置信度是相似度：越大越近。直接传进去，最强的连接反而成了远路。",
    "q3": "所以要先转换。常用两种：取倒数，或者取负对数。",
    "q3b": "取倒数，零点九变成一点一一，零点二变成五。取负对数时，路径长度对应沿途相似度的乘积。",
    "q4": "模块度和节点强度把权重当强度，不需要转换。最好两种属性分开存，调用时写明用哪个。",
    # communities
    "c1": "最后是第三部分。算出指标后，常要划分社团。这是经典的空手道俱乐部网络，三十四个人。",
    "c2": "用鲁汶算法，一行代码就得到一个划分，颜色代表不同社团。",
    "c3": "它有随机性：换随机种子，划分会变。右边黄点是十个种子的模块度，模块度衡量社团内部的边比随机期望多多少。",
    "c4": "零模型是保持每个节点的度，把边随机打乱。灰色柱子是随机网络的模块度，也不算小。",
    "c5": "【慢】真实网络的模块度明显高于随机网络，才能说社团结构不是偶然。",
    # layouts
    "l1": "最后是画图。力导向布局把边当弹簧，同一张网络，换个随机种子，画出来就不一样。",
    "l2": "所以簇与簇之间的远近和相对位置，往往没有含义。",
    "l3": "谱布局用拉普拉斯矩阵的特征向量作坐标，这个矩阵由连接关系算出，结果不依赖随机种子。",
    "l4": "节点大小要让面积和数值成正比，而不是半径。否则数值差四倍，看起来差十六倍。",
    # recap
    "r1": "好，我们总结一下。",
    "r2": "第一，从具体问题出发，记录数据版本、阈值、软件版本和随机种子。",
    "r3": "第二，计算前先看数据，留意自环、孤立点、方向和权重的含义。",
    "r4": "第三，结论要和零模型比较，并在合理的分析选择下保持稳健。",
}


def tri_graph():
    G = nx.Graph()
    G.add_edge("甲", "乙", r=0.9); G.add_edge("乙", "丙", r=0.9); G.add_edge("甲", "丙", r=0.2)
    for u, v, d in G.edges(data=True):
        d["dist"] = 1 / d["r"]
    return G


class Episode(Narrated):
    LINES = LINES

    def construct(self):
        self.hook()
        self.questions()
        self.workflow()
        self.reading()
        self.defaults()
        self.weights()
        self.communities()
        self.layouts()
        self.recap()

    # ------------------------------------------------------------------ hook
    def tri(self, center=LEFT * 3.4 + DOWN * 0.2, s=1.0):
        P = {"甲": center + s * np.array([-2.0, -1.2, 0]), "乙": center + s * np.array([0, 1.6, 0]), "丙": center + s * np.array([2.0, -1.2, 0])}
        nodes = {k: VGroup(Circle(radius=0.42, color=GOLD, fill_opacity=0.25, stroke_width=3), T(k, 28)).move_to(p) for k, p in P.items()}
        G = tri_graph()
        edges, labs = {}, {}
        for u, v, d in G.edges(data=True):
            w = d["r"]
            edges[(u, v)] = Line(P[u], P[v], color=BLUE, stroke_width=2 + 8 * w, stroke_opacity=0.8).set_z_index(-1)
            mid = (P[u] + P[v]) / 2
            off = (mid - center); off = off / (np.linalg.norm(off) + 1e-9) * 0.45
            labs[(u, v)] = MathTex(f"{w}", font_size=34, color=INK).move_to(mid + off)
        return P, nodes, edges, labs

    def hook(self):
        P, nodes, edges, labs = self.tri()
        G = tri_graph()
        b_r = nx.betweenness_centrality(G, weight="r", normalized=False)["乙"]
        b_d = nx.betweenness_centrality(G, weight="dist", normalized=False)["乙"]
        with self.say("h1") as d:
            self.play(*[GrowFromCenter(n) for n in nodes.values()], run_time=0.8)
            self.play(*[Create(e) for e in edges.values()], *[FadeIn(l) for l in labs.values()], run_time=d * 0.5)
        with self.say("h2") as d:
            self.play(Indicate(nodes["乙"], color=GOLD, scale_factor=1.4), run_time=1.0)
            q = T("桥梁", 30, GOLD).next_to(nodes["乙"], UP, buff=0.2)
            self.play(FadeIn(q), run_time=0.5)
        c1 = code_block('nx.betweenness_centrality(G, weight="r")', 22).move_to(RIGHT * 3.4 + UP * 1.6)
        c2 = code_block('nx.betweenness_centrality(G, weight="dist")', 22).move_to(RIGHT * 3.4 + DOWN * 0.9)
        for c in (c1, c2):
            if c.width > 7.2:
                c.scale_to_fit_width(7.2).set_x(3.4)
        with self.say("h3") as d:
            self.play(FadeIn(c1, shift=UP * 0.2), run_time=0.8)
            path = Line(P["甲"], P["丙"], color=RED, stroke_width=10)
            self.play(Create(path), run_time=0.8)
            r1 = VGroup(T("乙的介数", 24, MUTED), T(f"{b_r:g}", 44, RED, weight=BOLD)).arrange(RIGHT, buff=0.3).next_to(c1, DOWN, buff=0.3)
            self.play(FadeIn(r1), run_time=0.6)
        with self.say("h4") as d:
            self.play(FadeOut(path), FadeIn(c2, shift=UP * 0.2), run_time=0.8)
            p2 = VGroup(Line(P["甲"], P["乙"], color=GREEN, stroke_width=10), Line(P["乙"], P["丙"], color=GREEN, stroke_width=10))
            self.play(Create(p2), run_time=1.0)
            r2 = VGroup(T("乙的介数", 24, MUTED), T(f"{b_d:g}", 44, GREEN, weight=BOLD)).arrange(RIGHT, buff=0.3).next_to(c2, DOWN, buff=0.3)
            self.play(FadeIn(r2), run_time=0.6)
        with self.say("h4b") as d:
            self.play(Indicate(r1, color=RED), Indicate(r2, color=GREEN), run_time=1.2)
        with self.say("h5") as d:
            self.play(*[m.animate.fade(0.85) for m in self.mobjects], run_time=0.8)
            self.play(Write(T("从头到尾走一遍", 56, GOLD, weight=BOLD)), run_time=1.0)
        fade_all(self)

    def questions(self):
        parts(self, "这一期分三部分", ["一  网络分析的六个步骤", "二  默认行为的陷阱", "三  社团、零模型与作图"], ["q0", "q1", "q2", "q3"])

    # ------------------------------------------------------------------ workflow
    def workflow(self):
        tag = self.chapter("一  六个步骤")
        names = ["问题", "数据", "构建", "指标", "零模型", "解释"]
        cols = [GOLD, BLUE, VIOLET, GREEN, RED, GOLD]
        xs = np.linspace(-5.6, 5.6, 6)
        ys = [0.9, -0.6, 0.9, -0.6, 0.9, -0.6]
        P = [np.array([x, y, 0]) for x, y in zip(xs, ys)]
        steps = VGroup(*[VGroup(Circle(radius=0.55, color=c, fill_opacity=0.2, stroke_width=3), T(str(i + 1), 30, c, weight=BOLD)).move_to(p)
                         for i, (p, c) in enumerate(zip(P, cols))])
        labs = VGroup(*[T(n, 26, INK).next_to(s, DOWN if y < 0 else UP, buff=0.2) for n, s, y in zip(names, steps, ys)])
        path = VMobject(stroke_color=MUTED, stroke_width=3).set_points_smoothly(P)
        path.set_z_index(-1)
        token = Dot(P[0], radius=0.14, color=WHITE)
        with self.say("w1") as d:
            self.play(FadeIn(tag), Create(path), run_time=1.0)
            self.play(GrowFromCenter(steps[0]), FadeIn(labs[0]), run_time=0.7)
            ex = T("某种疾病的相关蛋白，是否聚成模块？", 26, GOLD).move_to(DOWN * 2.6)
            self.play(FadeIn(ex), FadeIn(token), run_time=0.8)
        def go(i, rt):
            seg = VMobject().set_points_smoothly(P[i - 1:i + 1]) if False else Line(P[i - 1], P[i])
            self.play(token.animate.move_to(P[i]), GrowFromCenter(steps[i]), FadeIn(labs[i]), run_time=rt)
        with self.say("w2") as d:
            self.play(FadeOut(ex), run_time=0.4)
            go(1, 1.0)
            ex2 = T("基因名 ↔ 编号", 24, BLUE).move_to(DOWN * 2.6 + LEFT * 2.5)
            self.play(FadeIn(ex2), run_time=0.5)
        keep = [m for m in self.mobjects if m is not tag]
        self.play(*[FadeOut(m) for m in keep], run_time=0.5)
        clip_line(self, "w2b", "yt_string_tutorial_jensen.mp4", "视频：Lars Juhl Jensen · YouTube", start=30)
        self.play(*[FadeIn(m) for m in keep if m is not ex2], run_time=0.5)
        with self.say("w2c") as d:
            go(2, 1.0)
            ex3 = T("节点 · 边 · 方向 · 权重 · 阈值", 24, VIOLET).move_to(DOWN * 2.6 + RIGHT * 2.5)
            self.play(FadeIn(ex3), run_time=0.5)
        with self.say("w3") as d:
            self.play(FadeOut(ex3), run_time=0.4)
            go(3, 1.0)
            go(4, 1.0)
            nm = T("与零模型比较", 24, RED).move_to(DOWN * 2.6 + RIGHT * 2.5)
            self.play(FadeIn(nm), run_time=0.5)
        with self.say("w4") as d:
            self.play(FadeOut(nm), run_time=0.4)
            go(5, 1.0)
            log = VGroup(*[Rectangle(width=0.5, height=0.32, color=MUTED, fill_color=PANEL, fill_opacity=1, stroke_width=1.5).next_to(s, DOWN if y > 0 else UP, buff=0.15)
                           for s, y in zip(steps, ys)])
            # notebook marks under/over each step
            self.play(LaggedStart(*[FadeIn(l, shift=DOWN * 0.1) for l in log], lag_ratio=0.15), run_time=1.2)
            ll = T("记录每一步的选择", 24, MUTED).move_to(DOWN * 2.6)
            self.play(FadeIn(ll), run_time=0.5)
        with self.say("w5") as d:
            self.play(Indicate(steps[0], color=GOLD, scale_factor=1.3), run_time=1.0)
            no = VGroup(chip("下载数据库 + 画网络", MUTED, 26), T("≠", 40, RED), chip("研究问题", GOLD, 26)).arrange(RIGHT, buff=0.3).move_to(DOWN * 2.6)
            self.play(FadeOut(ll), FadeIn(no), run_time=0.8)
        fade_all(self)

    # ------------------------------------------------------------------ reading data
    def reading(self):
        tag = self.chapter("二  读入数据")
        n = 6
        E = [(0, 1), (0, 2), (1, 2), (2, 3), (3, 4), (3, 5), (4, 5)]
        names = "ABCDEF"
        lines = VGroup(*[Text(f"{names[u]}  {names[v]}", font="Menlo", font_size=26, color=INK) for u, v in E]).arrange(DOWN, aligned_edge=LEFT, buff=0.18).move_to(LEFT * 5.4 + DOWN * 0.1)
        head = Text("edges.txt", font="Menlo", font_size=22, color=MUTED).next_to(lines, UP, buff=0.3)
        s = 0.62
        cells = VGroup(*[Square(side_length=s, stroke_color=MUTED, stroke_width=1, fill_color=GOLD, fill_opacity=0) for _ in range(n * n)])
        cells.arrange_in_grid(n, n, buff=0).move_to(LEFT * 0.6 + DOWN * 0.3)
        zeros = VGroup(*[T("0", 22, MUTED).move_to(c) for c in cells])
        rl = VGroup(*[T(names[i], 22, MUTED).next_to(cells[i * n], LEFT, buff=0.15) for i in range(n)])
        cl = VGroup(*[T(names[i], 22, MUTED).next_to(cells[i], UP, buff=0.15) for i in range(n)])
        with self.say("i1") as d:
            self.play(FadeIn(tag), FadeIn(head), LaggedStart(*[FadeIn(l, shift=RIGHT * 0.2) for l in lines], lag_ratio=0.12), run_time=d * 0.6)
        with self.say("i2") as d:
            self.play(FadeIn(cells), FadeIn(zeros), FadeIn(rl), FadeIn(cl), run_time=0.7)
            for k, (u, v) in enumerate(E):
                a, b = cells[u * n + v], cells[v * n + u]
                self.play(lines[k].animate.set_color(GOLD),
                          a.animate.set_fill(opacity=0.6), b.animate.set_fill(opacity=0.6),
                          Transform(zeros[u * n + v], T("1", 22, INK).move_to(a)), Transform(zeros[v * n + u], T("1", 22, INK).move_to(b)),
                          run_time=max(0.3, d * 0.75 / len(E)))
        A = np.zeros((n, n), int)
        for u, v in E:
            A[u, v] = A[v, u] = 1
        with self.say("i3") as d:
            sums = VGroup(*[T(str(A[i].sum()), 26, GREEN, weight=BOLD).next_to(cells[i * n + n - 1], RIGHT, buff=0.3) for i in range(n)])
            kl = T("度", 24, GREEN).next_to(sums, UP, buff=0.2)
            self.play(LaggedStart(*[FadeIn(x, shift=LEFT * 0.2) for x in sums], lag_ratio=0.15), FadeIn(kl), run_time=1.4)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.6)
        with self.say("i4") as d:
            dense = 20000 ** 2 * 8 / 1e6
            ax = axes([0, 2, 1], [0, 3500, 1000], 5.0, 4.0).move_to(LEFT * 2.4 + DOWN * 0.3)
            u = ax.c2p(0, 1)[1] - ax.c2p(0, 0)[1]
            b1 = Rectangle(width=1.4, height=u * dense, fill_color=RED, fill_opacity=0.85, stroke_width=0).move_to(ax.c2p(0.5, 0), aligned_edge=DOWN)
            b2 = Rectangle(width=1.4, height=0.04, fill_color=GREEN, fill_opacity=0.9, stroke_width=0).move_to(ax.c2p(1.5, 0), aligned_edge=DOWN)
            l1 = VGroup(T("稠密矩阵", 22, MUTED), T("约 3200 MB", 26, RED, weight=BOLD)).arrange(DOWN, buff=0.08).next_to(b1, UP, buff=0.12)
            l2 = VGroup(T("稀疏格式", 22, MUTED), T("约 2 MB", 26, GREEN, weight=BOLD)).arrange(DOWN, buff=0.08).next_to(b2, UP, buff=0.12)
            nl = T("2 万个节点", 24, INK).next_to(ax, DOWN, buff=0.25)
            self.play(FadeIn(tag), Create(ax.x_axis), FadeIn(nl), run_time=0.6)
            self.play(GrowFromEdge(b1, DOWN), FadeIn(l1), run_time=1.2)
            self.play(GrowFromEdge(b2, DOWN), FadeIn(l2), run_time=0.8)
            sp = VGroup(*[Dot(radius=0.03, color=GOLD) for _ in range(1)])
            grid = VGroup(*[Square(side_length=0.12, stroke_width=0, fill_color=GOLD if random.Random(i).random() < 0.04 else "#1d2638", fill_opacity=1) for i in range(24 * 24)]).arrange_in_grid(24, 24, buff=0.02).move_to(RIGHT * 3.6 + DOWN * 0.3)
            self.play(FadeIn(grid, lag_ratio=0.001), run_time=1.0)
        code = code_block(
            'G = nx.read_edgelist("ppi.txt")\n'
            'print(G.number_of_nodes(), G.number_of_edges())\n'
            'print(nx.number_of_selfloops(G))\n'
            'print(nx.number_connected_components(G))', 20)
        code.scale_to_fit_width(min(code.width, 8.5)).move_to(DOWN * 0.2)
        with self.say("i5") as d:
            self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.5)
            self.play(FadeIn(code, shift=UP * 0.2), run_time=1.0)
            look = T("先看数据，再算指标", 32, GOLD, weight=BOLD).next_to(code, DOWN, buff=0.5)
            self.play(Write(look), run_time=1.0)
        fade_all(self)

    # ------------------------------------------------------------------ default-behaviour traps
    def defaults(self):
        tag = self.chapter("二  默认行为的陷阱")
        G = nx.Graph([(0, 1), (0, 2), (1, 2), (2, 3), (3, 4)])
        pos = {0: LEFT * 5.6 + UP * 0.6, 1: LEFT * 4.2 + UP * 1.8, 2: LEFT * 3.6 + UP * 0.2, 3: LEFT * 2.0 + UP * 0.9, 4: LEFT * 0.8 + DOWN * 0.3}
        dots = {v: Dot(pos[v], radius=0.16, color=BLUE) for v in G}
        lines = VGroup(*[Line(pos[u], pos[v], color=BLUE, stroke_width=3, stroke_opacity=0.7) for u, v in G.edges()])
        k_before = G.degree(2)
        H = G.copy(); H.add_edge(2, 2)
        k_after = H.degree(2)
        loop = Circle(radius=0.35, color=RED, stroke_width=4).move_to(pos[2] + DOWN * 0.42)
        with self.say("p1") as d:
            self.play(FadeIn(tag), Create(lines), *[GrowFromCenter(x) for x in dots.values()], run_time=1.0)
            c = counter("节点的度", str(k_before), INK).move_to(RIGHT * 3.4 + UP * 1.6)
            self.play(Indicate(dots[2], color=GOLD), FadeIn(c), run_time=0.8)
            self.play(Create(loop), Transform(c, counter("节点的度", f"{k_before} → {k_after}", RED).move_to(c)), run_time=1.0)
        avg0 = 2 * G.number_of_edges() / G.number_of_nodes()
        G2 = G.copy(); G2.add_nodes_from([5, 6, 7])
        avg1 = 2 * G2.number_of_edges() / G2.number_of_nodes()
        iso = VGroup(*[Dot(p, radius=0.16, color=MUTED) for p in (LEFT * 5.4 + DOWN * 2.2, LEFT * 3.6 + DOWN * 2.5, LEFT * 1.8 + DOWN * 2.1)])
        with self.say("p2") as d:
            self.play(FadeOut(loop), FadeOut(c), run_time=0.4)
            a0 = counter("平均度", f"{avg0:.2f}", INK).move_to(RIGHT * 2.2 + UP * 1.6)
            self.play(FadeIn(a0), run_time=0.5)
            self.play(LaggedStart(*[GrowFromCenter(x) for x in iso], lag_ratio=0.2), Transform(a0, counter("平均度", f"{avg0:.2f} → {avg1:.2f}", RED).move_to(a0)), run_time=1.0)
            try:
                nx.average_shortest_path_length(G2); msg = ""
            except nx.NetworkXError as e:
                msg = str(e)
            err = code_block(f"nx.average_shortest_path_length(G)\n# NetworkXError: {msg}", 18)
            err.scale_to_fit_width(min(err.width, 6.4)).move_to(RIGHT * 3.4 + DOWN * 0.8)
            self.play(FadeIn(err, shift=UP * 0.2), run_time=0.8)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.6)
        D = nx.DiGraph([(0, 1), (1, 2), (2, 3), (3, 4)])
        prd = nx.pagerank(D); pru = nx.pagerank(D.to_undirected())
        P = [LEFT * 5.6 + RIGHT * 1.3 * i + UP * 1.6 for i in range(5)]
        nd = VGroup(*[Dot(p, radius=0.16, color=GOLD) for p in P])
        ar = VGroup(*[arrow(P[i], P[i + 1], INK, buff=0.2, sw=3) for i in range(4)])
        ax = axes([0, 5, 1], [0, 0.4, 0.2], 5.2, 2.6, ynums=[0, 0.2, 0.4], fs=18).move_to(LEFT * 3.0 + DOWN * 1.6)
        u = ax.c2p(0, 1)[1] - ax.c2p(0, 0)[1]
        bd = VGroup(*[Rectangle(width=0.6, height=u * prd[i], fill_color=GOLD, fill_opacity=0.9, stroke_width=0).move_to(ax.c2p(i + 0.5, 0), aligned_edge=DOWN) for i in range(5)])
        bu = VGroup(*[Rectangle(width=0.6, height=u * pru[i], fill_color=BLUE, fill_opacity=0.9, stroke_width=0).move_to(ax.c2p(i + 0.5, 0), aligned_edge=DOWN) for i in range(5)])
        yl = T("中心性", 22, MUTED).next_to(ax, UP, buff=0.1)
        with self.say("p3") as d:
            self.play(FadeIn(nd), LaggedStart(*[GrowArrow(a) for a in ar], lag_ratio=0.2), run_time=1.0)
            self.play(Create(ax), FadeIn(yl), grow_bars(bd, 1.0))
            tl = T("有向：沿方向递增", 24, GOLD).move_to(RIGHT * 3.4 + DOWN * 0.6)
            self.play(FadeIn(tl), run_time=0.5)
            ul = [Line(P[i], P[i + 1], color=INK, stroke_width=3) for i in range(4)]
            self.play(*[Transform(a, l) for a, l in zip(ar, ul)], Transform(bd, bu), run_time=1.2)
            tl2 = T("无向：首尾对称", 24, BLUE).next_to(tl, DOWN, buff=0.3)
            self.play(FadeIn(tl2), run_time=0.5)
        fade_all(self)

    # ------------------------------------------------------------------ weights
    def weights(self):
        tag = self.chapter("二  权重：相似度还是距离")
        P, nodes, edges, labs = self.tri()
        with self.say("q1") as d:
            self.play(FadeIn(tag), *[FadeIn(n) for n in nodes.values()], *[Create(e) for e in edges.values()], *[FadeIn(l) for l in labs.values()], run_time=1.0)
            rule = VGroup(T("最短路径 · 介数", 26, INK), T("权重 = 距离：越大越远", 26, RED)).arrange(DOWN, buff=0.15).move_to(RIGHT * 3.4 + UP * 2.0)
            self.play(FadeIn(rule), run_time=0.8)
        with self.say("q2") as d:
            sim = VGroup(T("相关系数 · 置信度", 26, INK), T("权重 = 相似度：越大越近", 26, GREEN)).arrange(DOWN, buff=0.15).move_to(RIGHT * 3.4 + UP * 0.4)
            self.play(FadeIn(sim), run_time=0.8)
            self.play(edges[("甲", "乙")].animate.set_color(RED), edges[("乙", "丙")].animate.set_color(RED), run_time=0.6)
            far = T("被当成了远路", 24, RED).next_to(nodes["乙"], RIGHT, buff=0.3)
            self.play(FadeIn(far), run_time=0.6)
        with self.say("q3") as d:
            self.play(FadeOut(far), *[e.animate.set_color(BLUE) for e in edges.values()], run_time=0.5)
            f1 = MathTex(r"d = \frac{1}{w}", font_size=44, color=INK)
            f2 = MathTex(r"d = -\log w", font_size=44, color=INK)
            ff = VGroup(f1, f2).arrange(RIGHT, buff=1.0).move_to(RIGHT * 3.4 + DOWN * 1.3)
            self.play(Write(f1), run_time=0.8)
            self.play(Write(f2), run_time=0.8)
        with self.say("q3b") as d:
            newl = {k: MathTex(f"{1 / w:.2f}", font_size=30, color=GOLD).move_to(labs[k]) for k, w in ((("甲", "乙"), 0.9), (("乙", "丙"), 0.9), (("甲", "丙"), 0.2))}
            self.play(*[Transform(labs[k], newl[k]) for k in labs], run_time=0.8)
            prod = MathTex(r"\sum -\log w_i = -\log \prod w_i", font_size=34, color=MUTED).next_to(ff, DOWN, buff=0.35)
            self.play(FadeIn(prod), run_time=0.6)
        with self.say("q4") as d:
            self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.6)
            code = code_block('G[u][v]["sim"]  = r\nG[u][v]["dist"] = 1 / r\n\nnx.shortest_path(G, s, t, weight="dist")\nnx.community.modularity(G, parts, weight="sim")', 20)
            code.scale_to_fit_width(min(code.width, 9.0)).move_to(DOWN * 0.2)
            self.play(FadeIn(code, shift=UP * 0.2), run_time=1.0)
        fade_all(self)

    # ------------------------------------------------------------------ communities
    def communities(self):
        tag = self.chapter("三  社团与零模型")
        G = nx.karate_club_graph()
        pos = fit(nx.spring_layout(G, seed=4), (-6.4, -1.4, -3.0, 2.8))
        net = NetView(G, pos, color=MUTED, eo=0.4, rmin=0.06, rk=0.02)
        with self.say("c1") as d:
            self.play(FadeIn(tag), LaggedStart(*[GrowFromCenter(x) for x in net.dots.values()], lag_ratio=0.02),
                      LaggedStart(*[Create(e) for e in net.edges.values()], lag_ratio=0.01), run_time=d * 0.6)
        comms = nx.community.louvain_communities(G, seed=1)
        cols = [BLUE, GOLD, GREEN, VIOLET, RED, INK]
        cof = {v: cols[i % 6] for i, c in enumerate(comms) for v in c}
        code = code_block("parts = nx.community.louvain_communities(G, seed=1)", 20)
        code.scale_to_fit_width(min(code.width, 6.6)).move_to(RIGHT * 3.4 + UP * 2.5)
        with self.say("c2") as d:
            self.play(FadeIn(code, shift=UP * 0.2), run_time=0.8)
            self.play(*[net.dots[v].animate.set_color(cof[v]) for v in G], run_time=1.0)
        Qs = []
        for s in range(10):
            p = nx.community.louvain_communities(G, seed=s)
            Qs.append(nx.community.modularity(G, p))
        lo = min(Qs)
        rng = random.Random(3)
        Qr = []
        for i in range(60):
            H = G.copy()
            nx.double_edge_swap(H, nswap=3 * H.number_of_edges(), max_tries=10000, seed=100 + i)
            Qr.append(nx.community.modularity(H, nx.community.louvain_communities(H, seed=0)))
        print("Q", Qs, np.mean(Qr), max(Qr))
        ax = axes([0.2, 0.5, 0.1], [0, 20, 10], 5.4, 2.6, xnums=[0.2, 0.3, 0.4, 0.5], fs=18).move_to(RIGHT * 3.4 + DOWN * 1.6)
        xl = xlabel(ax, "模块度 Q", 20, 0.3)
        with self.say("c3") as d:
            self.play(Create(ax), FadeIn(xl), run_time=0.6)
            sd = VGroup(*[Dot(ax.c2p(q, 1.5 + 2.2 * (i % 5)), radius=0.08, color=GOLD) for i, q in enumerate(Qs)])
            for s in (2, 5):
                p = nx.community.louvain_communities(G, seed=s)
                cf = {v: cols[i % 6] for i, c in enumerate(p) for v in c}
                self.play(*[net.dots[v].animate.set_color(cf[v]) for v in G], run_time=0.6)
            self.play(LaggedStart(*[GrowFromCenter(x) for x in sd], lag_ratio=0.1), run_time=1.0)
            tl = T("10 个种子", 20, GOLD).next_to(sd, UP, buff=0.15)
            self.play(FadeIn(tl), run_time=0.4)
        bars, _ = hist_bars(ax, Qr, np.arange(0.2, 0.52, 0.02), MUTED)
        with self.say("c4") as d:
            rl = T("保度随机网络", 20, MUTED).next_to(ax, UP, buff=0.1).align_to(ax, LEFT)
            self.play(net.group.animate.fade(0.6), run_time=0.5)
            self.play(grow_bars(bars, d * 0.35), FadeIn(rl))
        with self.say("c5") as d:
            self.play(*[Indicate(x, color=GOLD) for x in sd], run_time=1.0)
            gap = Arrow(ax.c2p(np.mean(Qr), 21), ax.c2p(np.mean(Qs), 21), buff=0, color=GOLD, stroke_width=4)
            self.play(GrowArrow(gap), run_time=0.8)
        fade_all(self)

    # ------------------------------------------------------------------ layouts
    def layouts(self):
        tag = self.chapter("三  布局与作图")
        G = nx.karate_club_graph()
        comms = nx.community.louvain_communities(G, seed=1)
        cols = [BLUE, GOLD, GREEN, VIOLET, RED, INK]
        cof = {v: cols[i % 6] for i, c in enumerate(comms) for v in c}
        box = (-3.2, 3.2, -3.0, 2.6)
        lays = [fit(nx.spring_layout(G, seed=s), box) for s in (1, 7, 23)]
        net = NetView(G, lays[0], color=MUTED, eo=0.4, rmin=0.07, rk=0.02)
        for v in G:
            net.dots[v].set_color(cof[v])

        def morph(pos, rt):
            anims = [net.dots[v].animate.move_to(pos[v]) for v in G]
            anims += [Transform(e, Line(pos[u], pos[v], stroke_width=1.4, color=MUTED, stroke_opacity=0.4)) for (u, v), e in net.edges.items()]
            self.play(*anims, run_time=rt)
        sl = Text("seed = 1", font="Menlo", font_size=26, color=MUTED).to_corner(UR, buff=0.6)
        with self.say("l1") as d:
            self.play(FadeIn(tag), FadeIn(net.group), FadeIn(sl), run_time=1.0)
            for s, p in zip((7, 23), lays[1:]):
                morph(p, 1.4)
                self.play(Transform(sl, Text(f"seed = {s}", font="Menlo", font_size=26, color=MUTED).move_to(sl)), run_time=0.3)
        with self.say("l2") as d:
            self.play(*[Indicate(net.dots[v], color=cof[v], scale_factor=1.4) for v in G], run_time=1.2)
        L = nx.laplacian_matrix(G).toarray().astype(float)
        w, V = np.linalg.eigh(L)
        spec = fit({v: V[i, 1:3] for i, v in enumerate(G)}, box)
        with self.say("l3") as d:
            self.play(Transform(sl, T("谱布局", 28, GOLD).move_to(sl)), run_time=0.5)
            morph(spec, 1.6)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.6)
        with self.say("l4") as d:
            vals = [1, 4]
            cr = VGroup(*[Circle(radius=0.35 * v, color=RED, fill_opacity=0.4) for v in vals]).arrange(RIGHT, buff=0.4, aligned_edge=DOWN).move_to(LEFT * 3.2 + DOWN * 0.3)
            ca = VGroup(*[Circle(radius=0.35 * np.sqrt(v), color=GREEN, fill_opacity=0.4) for v in vals]).arrange(RIGHT, buff=0.4, aligned_edge=DOWN).move_to(RIGHT * 3.2 + DOWN * 0.3)
            ll = T("半径 ∝ 数值：看起来差 16 倍", 24, RED).next_to(cr, DOWN, buff=0.4)
            lr = T("面积 ∝ 数值：差 4 倍", 24, GREEN).next_to(ca, DOWN, buff=0.4)
            hd = T("数值：1 和 4", 28, INK).to_edge(UP, buff=1.0)
            self.play(FadeIn(hd), FadeIn(cr), FadeIn(ll), run_time=1.0)
            self.play(FadeIn(ca), FadeIn(lr), run_time=1.0)
        fade_all(self)

    # ------------------------------------------------------------------ recap
    def recap(self):
        with self.say("r1") as d:
            head = T("三个要点", 40, INK, weight=BOLD).to_edge(UP, buff=0.7)
            self.play(Write(head), run_time=0.8)
        items = [("r2", GOLD, "从问题出发，记录每一个选择"),
                 ("r3", BLUE, "先看数据：自环、孤立点、方向、权重"),
                 ("r4", GREEN, "与零模型比较，检验稳健性")]
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
