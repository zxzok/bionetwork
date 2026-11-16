"""Paper explainer: Menche et al. 2015, disease relationships through the incomplete interactome."""
import random

import networkx as nx
import numpy as np

from common import *  # noqa: F401,F403
from paperkit import fit, counter

TITLE = "不完整的相互作用组与疾病之间的关系"

LINES = {
    # hook
    "h1": "我们先来看两种疾病，以及和它们相关的基因。左边是疾病甲的基因，右边是疾病乙的基因。",
    "h2": "过去常用的办法，是看两种疾病有没有共享基因。这两种疾病，一个共同的基因都没有。按这个办法，看不出它们有关系。",
    "h3": "可基因的产物是蛋白质，蛋白质之间还在相互作用。我们把这些基因，放回蛋白质互作网络里看。",
    "h4": "【慢】你看，两组基因一个都不重合，在网络里却紧紧挨在一起。",
    "h5": "2015年，《科学》杂志上的一项研究，就从网络上的距离出发，重新刻画了疾病之间的关系。",
    "q0": "这一期分三部分来讲。",
    "q1": "第一部分，在一张残缺的网络地图上，疾病模块在什么条件下能被看见。",
    "q2": "第二部分，怎样用网络距离衡量两种疾病的远近，以及这个距离能预测什么。",
    "q3": "第三部分，超越共享基因、走向药物，以及这项研究的局限。",
    # module + incompleteness
    "a0": "先看第一部分。画面里，是网络医学研究者制作的一段疾病网络可视化。",
    "a1": "研究的出发点，是疾病模块假说。相互作用组，就是细胞里所有蛋白质相互作用组成的网络。假说认为，同一种疾病的相关基因，在这张网络里不是随机散布，而是聚在一个局部区域。",
    "a1b": "红色的这一片，就是一个疾病模块。",
    "a2": "研究整合了多种实验证据，得到一万三千多个蛋白之间的十四万多条相互作用，又整理出两百九十九种疾病。",
    "a3": "可这张地图远不完整。研究引用的估计是，高通量方法只覆盖了不到两成的潜在相互作用。",
    "a4": "我们把大部分边拿掉，只留两成。原本连成一片的疾病模块，就碎成了好几块。",
    "a5": "【慢】疾病基因在已知网络里能连成的最大一块，叫作可观测模块。这里是黄色的这几个点。",
    # percolation
    "b1": "模块碎到什么程度还能被看见，研究借用了渗流理论。渗流理论，研究的是边逐渐增多或减少时，网络在什么时候连成一片。",
    "b2": "看这个模块。右上角是观测到的边的比例。比例越低，模块越碎。",
    "b2b": "研究推出了这样一个关系。公式左边，是临界的观测比例；右边的分母，是模块里基因的个数。",
    "b2c": "也就是说，模块要保持连通，观测比例必须高于这个临界值；而临界值大致和模块大小成反比。模块越大，越不怕边缺失。",
    "b3": "我们做个模拟，边只保留两成。这张图，横轴是疾病基因数，纵轴是可观测模块的大小。基因少的模块几乎全碎；基因数过了某个门槛，可观测模块才迅速长大。",
    "b4": "据此，研究预测在当时的数据下，相关基因少于二十五个左右的疾病，模块会碎到无法观测，就是灰色的这一段。",
    "b5": "以多发性硬化为例。画面里，是一段关于这种疾病的简短科普动画。",
    "b5b": "多发性硬化的六十九个相关基因里，只有十一个连成了可观测模块，就是中间黄色的这一团。",
    "b6": "随机预期只有两个左右，Z分数是五点八。Z分数，衡量的是真实结果比随机平均多出几个标准差，所以这里的聚集远超随机。",
    "b7": "整体上，可观测模块平均只包含约两成的疾病基因。但两百九十九种疾病里，有两百二十六种表现出显著的聚集，就是这些红色的方块。",
    # separation
    "s1": "下面进入第二部分。有了模块，就可以衡量两种疾病在网络上的远近。研究定义了网络分离度。",
    "s2": "先看疾病内部。对每个红色的疾病蛋白，找到最近的另一个红色蛋白，数一数要走几步，再取平均。",
    "s3": "再看两种疾病之间。对每个蛋白，找到另一种疾病最近的蛋白，数一数要走几步，同样取平均。",
    "s4": "【慢】用疾病之间的距离，减去两种疾病内部距离的平均，就是分离度。",
    "s4b": "公式里，减号前面，是两种疾病之间的平均距离；减号后面，是两种疾病各自内部距离的平均。",
    "s5": "分离度小于零，说明两个模块在网络上重叠；大于零，说明它们彼此分开。这里蓝色和红色分开，紫色和红色重叠。",
    # predictions
    "c1": "大多数疾病对在网络上是分开的。只有约百分之七的疾病对，分离度小于零。",
    "c2": "关键在于，网络上的远近，能预测疾病在生物学和临床上的相似程度。下面四张示意图，横轴都是从重叠到分开，纵轴是相似程度。",
    "c3": "从重叠到分离，功能注释的相似性下降约两个数量级，症状相似性下降约一个数量级。",
    "c4": "在七十种组织里，重叠疾病对的共表达，约为分离疾病对的两倍；分离之后，降到随机水平。",
    "c5": "研究还用约三千万名六十五岁以上美国医保人群的病史，计算了共病风险：重叠时，相对风险在十以上；分离时，降到一左右。",
    "c5b": "相对风险，是两种病同时出现的实际频率，比随机预期高出多少倍。",
    # beyond shared genes
    "g1": "下面进入第三部分。更有意思的是，百分之五十九的疾病对没有任何共享基因，可其中有七百一十七对，模块在网络上是重叠的。",
    "g2": "反过来，共享基因的疾病对里，有百分之八十七在网络上是分开的。",
    "g3": "【慢】所以，共享基因和网络距离，说的并不是同一件事。",
    # drugs & limits
    "x1": "同一团队后来把这种网络距离用到了药物上，提出了药物与疾病的网络邻近度。药物靶点，就是药物直接作用的蛋白质。",
    "x2": "计算药物每个靶点到疾病模块的最近距离，再和随机挑选的靶点比较，看这个药物是不是离疾病格外近。蓝色是近的靶点，紫色是远的靶点。",
    "x2b": "本站有网络邻近度的交互演示。我们先拿掉原来的靶点，再在疾病模块旁边点上新的靶点，下方的最近距离和z值会随之更新。",
    "x3": "之后，这个思路又延伸到药物组合的网络配置和新冠药物重定位，把网络医学推向了转化应用。",
    "x4": "当然也有局限。相互作用组和疾病基因都偏向研究热点；不同类型的相互作用，被合并成了无向边。",
    "x5": "二十五这个门槛，依赖当时的覆盖率。基因少的疾病，在这个框架里没法可靠分析。",
    "x6": "分离度基于最短路径，对枢纽很敏感。后续工作也比较了基于扩散和随机游走的距离。",
    # recap
    "r1": "好，我们来总结一下。",
    "r2": "第一，只要疾病基因足够多，在不完整的相互作用组里，疾病模块仍然能被观测到。",
    "r3": "第二，两种疾病在网络上越近，共表达、症状和共病就越相似。",
    "r4": "第三，即使没有共享基因，网络距离也能揭示疾病之间的联系。",
}


def ball(G, s, n):
    return list(nx.bfs_tree(G, s).nodes())[:n]


def separation(D, A, B):
    dAA = np.mean([min(D[a][x] for x in A if x != a) for a in A])
    dBB = np.mean([min(D[a][x] for x in B if x != a) for a in B])
    dAB = np.mean([min(D[a][x] for x in B) for a in A] + [min(D[b][x] for x in A) for b in B])
    return dAA, dBB, dAB, dAB - (dAA + dBB) / 2


class Episode(Narrated):
    LINES = LINES

    def construct(self):
        self.G = nx.powerlaw_cluster_graph(220, 2, 0.4, seed=3)
        self.pos = fit(nx.kamada_kawai_layout(self.G), (-6.3, 6.3, -3.4, 3.1))
        self.hook()
        self.parts()
        self.modules()
        self.percolation()
        self.separation_ch()
        self.predictions()
        self.shared()
        self.drugs()
        self.recap()

    def netview(self, pos=None, r=0.05, eo=0.3):
        G = self.G; pos = pos or self.pos
        dots = {v: Dot(pos[v], radius=r, color=MUTED) for v in G}
        edges = {e: Line(pos[e[0]], pos[e[1]], stroke_width=1.0, color=MUTED, stroke_opacity=eo) for e in G.edges()}
        return dots, edges

    # ------------------------------------------------------------------ hook
    def hook(self):
        G, pos = self.G, self.pos
        deg = dict(G.degree())
        seed = sorted(G, key=lambda v: (abs(deg[v] - 5), v))[0]
        region = ball(G, seed, 16)
        A, B = region[0::2], region[1::2]
        dA = VGroup(RoundedRectangle(width=2.2, height=0.8, corner_radius=0.15, color=RED), T("疾病甲", 28, RED)).move_to(LEFT * 2.6 + UP * 2.4)
        dB = VGroup(RoundedRectangle(width=2.2, height=0.8, corner_radius=0.15, color=BLUE), T("疾病乙", 28, BLUE)).move_to(RIGHT * 2.6 + UP * 2.4)
        gA = {v: Dot(LEFT * 2.6 + RIGHT * (i - 3.5) * 0.55 + DOWN * 0.6, radius=0.11, color=RED) for i, v in enumerate(A)}
        gB = {v: Dot(RIGHT * 2.6 + RIGHT * (i - 3.5) * 0.55 + DOWN * 0.6, radius=0.11, color=BLUE) for i, v in enumerate(B)}
        lA = VGroup(*[Line(dA.get_bottom(), d.get_center(), color=RED, stroke_width=1.5, stroke_opacity=0.6) for d in gA.values()])
        lB = VGroup(*[Line(dB.get_bottom(), d.get_center(), color=BLUE, stroke_width=1.5, stroke_opacity=0.6) for d in gB.values()])
        with self.say("h1") as d:
            self.play(FadeIn(dA), FadeIn(dB), run_time=1.0)
            self.play(*[GrowFromCenter(x) for x in gA.values()], *[GrowFromCenter(x) for x in gB.values()], Create(lA), Create(lB), run_time=1.4)
            q = T("关系", 40, GOLD, weight=BOLD).move_to(UP * 2.4)
            self.play(FadeIn(q), run_time=0.6)
        with self.say("h2") as d:
            gap = DashedLine(dA.get_right(), dB.get_left(), color=MUTED)
            nos = T("共享基因：0", 30, MUTED).next_to(gap, DOWN, buff=0.9)
            self.play(FadeOut(q), Create(gap), FadeIn(nos), run_time=1.2)
        dots, edges = self.netview()
        for v in A:
            dots[v].set_color(RED).scale(1.8)
        for v in B:
            dots[v].set_color(BLUE).scale(1.8)
        with self.say("h3") as d:
            self.play(FadeOut(VGroup(dA, dB, lA, lB, gap, nos)), run_time=0.8)
            self.play(*[Transform(gA[v], dots[v]) for v in A], *[Transform(gB[v], dots[v]) for v in B], run_time=1.6)
            rest = [x for v, x in dots.items() if v not in region]
            self.play(LaggedStart(*[Create(e) for e in edges.values()], lag_ratio=0.002), FadeIn(VGroup(*rest)), run_time=d * 0.35)
        with self.say("h4") as d:
            inner = [e for e in G.edges() if e[0] in region and e[1] in region]
            self.play(*[edges[e].animate.set_stroke(GOLD, width=3, opacity=1) for e in inner], run_time=1.2)
            xs = [pos[v][0] for v in region]; ys = [pos[v][1] for v in region]
            ring = Ellipse(width=max(xs) - min(xs) + 0.7, height=max(ys) - min(ys) + 0.7, color=GOLD, stroke_width=4).move_to(
                [(max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2, 0])
            self.play(Create(ring), run_time=1.0)
        with self.say("h5") as d:
            self.play(*[x.animate.fade(0.85) for x in self.mobjects], run_time=1.0)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.6)

    def parts(self):
        head, items = slide("这一期分三部分", ["一  残缺的地图上，疾病模块何时可见", "二  网络分离度及其预测", "三  超越共享基因、走向药物与局限"])
        with self.say("q0") as d:
            self.play(FadeIn(head, shift=RIGHT * 0.3), run_time=0.6)
        for k, it in zip(("q1", "q2", "q3"), items):
            with self.say(k) as d:
                self.play(FadeIn(it, shift=RIGHT * 0.3), run_time=0.6)
        self.wait(0.6)
        self.play(FadeOut(head), FadeOut(items), run_time=0.6)

    # ------------------------------------------------------------------ modules & incompleteness
    def modules(self):
        with self.say("a0") as d:
            self.clip_on("yt_network_medicine_martino.mp4", "center", "视频：Mauro Martino · YouTube", start=10)
        self.clip_off()
        tag = self.chapter("一 · 疾病模块与残缺的地图")
        G, pos = self.G, self.pos
        dots, edges = self.netview()
        deg = dict(G.degree())
        seed = sorted(G, key=lambda v: (abs(deg[v] - 4), -v))[3]
        mod = ball(G, seed, 20)
        with self.say("a1") as d:
            self.play(FadeIn(tag), FadeIn(VGroup(*edges.values())), FadeIn(VGroup(*dots.values())), run_time=1.2)
        with self.say("a1b") as d:
            self.play(LaggedStart(*[dots[v].animate.set_color(RED).scale(1.8) for v in mod], lag_ratio=0.05), run_time=d * 0.4)
            self.play(*[edges[e].animate.set_stroke(RED, width=2.5, opacity=0.9) for e in G.edges() if e[0] in mod and e[1] in mod], run_time=1.0)
        nums = VGroup(counter("蛋白", "13 460", INK), counter("相互作用", "141 296", INK), counter("疾病", "299", RED)).arrange(DOWN, buff=0.35)
        box = BackgroundRectangle(nums, color=BG, fill_opacity=0.9, buff=0.25)
        VGroup(box, nums).to_corner(UR, buff=0.3).shift(DOWN * 0.3)
        with self.say("a2") as d:
            self.play(FadeIn(box), LaggedStart(*[FadeIn(n, shift=LEFT * 0.2) for n in nums], lag_ratio=0.3), run_time=d * 0.6)
        self.play(FadeOut(box), FadeOut(nums), run_time=0.5)
        rng = random.Random(2)
        keep = {e for e in G.edges() if rng.random() < 0.2}
        cov = counter("已知覆盖", "< 20%", GOLD).to_corner(UR, buff=0.4).shift(DOWN * 0.3)
        with self.say("a3") as d:
            self.play(FadeIn(cov), run_time=0.6)
            self.play(Indicate(cov, color=GOLD), run_time=1.2)
        gone = [e for e in G.edges() if e not in keep]
        with self.say("a4") as d:
            self.play(*[edges[e].animate.set_stroke(opacity=0.04) for e in gone], run_time=d * 0.6)
        H = G.edge_subgraph(keep).copy(); H.add_nodes_from(G)
        sub = H.subgraph(mod)
        lcc = max(nx.connected_components(sub), key=len)
        with self.say("a5") as d:
            self.play(*[dots[v].animate.set_color(GOLD) for v in lcc], *[dots[v].animate.set_opacity(0.5) for v in mod if v not in lcc], run_time=1.2)
            c = counter("可观测模块", f"{len(lcc)} / {len(mod)}", GOLD).move_to(cov)
            self.play(Transform(cov, c), run_time=0.8)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ percolation
    def percolation(self):
        tag = self.chapter("一 · 渗流：模块何时看得见")
        with self.say("b1") as d:
            # one module, observed at decreasing coverage
            M = nx.gnp_random_graph(24, 0.3, seed=4)
            P = fit(nx.spring_layout(M, seed=1), (-2.5, 2.5, -2.2, 2.2))
            dts = VGroup(*[Dot(P[v], radius=0.1, color=RED) for v in M])
            es = {e: Line(P[e[0]], P[e[1]], color=RED, stroke_width=2, stroke_opacity=0.7) for e in M.edges()}
            self.play(FadeIn(tag), FadeIn(dts), *[Create(e) for e in es.values()], run_time=d * 0.6)
        with self.say("b2") as d:
            rng = random.Random(3)
            order = list(M.edges()); rng.shuffle(order)
            lab = counter("观测比例", "100%", GOLD).to_corner(UR, buff=0.5).shift(DOWN * 0.4)
            self.play(FadeIn(lab), run_time=0.4)
            for frac in (0.6, 0.35, 0.15):
                cut = order[int(frac * len(order)):]
                self.play(*[es[e].animate.set_stroke(opacity=0.03) for e in cut],
                          Transform(lab[1], T(f"{int(frac * 100)}%", 40, GOLD, weight=BOLD).move_to(lab[1])), run_time=d * 0.15)
        with self.say("b2b") as d:
            f = MathTex(r"p_c", r"\sim", r"\frac{1}{m}", font_size=54, color=GOLD).move_to([4.2, 0.4, 0])
            self.play(Write(f), run_time=1.0)
            l1 = T("临界观测比例", 22, GOLD).next_to(f[0], DOWN, buff=0.45).shift(LEFT * 0.5)
            l2 = T("模块的基因数", 22, BLUE).next_to(f[2], DOWN, buff=0.15).shift(RIGHT * 0.3)
            self.play(FadeIn(l1), run_time=0.6)
            self.wait(d * 0.25)
            self.play(FadeIn(l2), run_time=0.6)
        with self.say("b2c") as d:
            inv = T("成反比", 28, GOLD).next_to(VGroup(l1, l2), DOWN, buff=0.4)
            self.play(FadeIn(inv, shift=UP * 0.2), Indicate(f, color=GOLD), run_time=1.2)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.6)
        rng = np.random.default_rng(0)
        ms = [5, 10, 15, 20, 25, 30, 40, 50, 60, 80, 100, 130, 160]
        S = []
        for m in ms:
            S.append(np.mean([max(len(c) for c in nx.connected_components(nx.gnp_random_graph(m, 0.04, seed=int(rng.integers(1e9)))))
                              for _ in range(60)]))
        assert S[3] < 8 and S[-1] > 140, S
        ax = Axes(x_range=[0, 160, 40], y_range=[0, 160, 40], x_length=7.5, y_length=4.6,
                  axis_config={"color": MUTED, "include_tip": False, "font_size": 22},
                  x_axis_config={"numbers_to_include": [0, 40, 80, 120, 160]},
                  y_axis_config={"numbers_to_include": [0, 40, 80, 120, 160]}).shift(DOWN * 0.4 + LEFT * 0.8)
        xl = T("疾病基因数", 24, MUTED).next_to(ax.x_axis, DOWN, buff=0.4)
        yl = T("可观测模块大小", 24, MUTED).rotate(PI / 2).next_to(ax.y_axis, LEFT, buff=0.35)
        curve = ax.plot_line_graph(ms, S, line_color=RED, vertex_dot_radius=0.06, vertex_dot_style={"fill_color": RED}, stroke_width=4)
        with self.say("b3") as d:
            self.play(Create(ax), FadeIn(xl), FadeIn(yl), run_time=1.2)
            self.play(Create(curve), run_time=d * 0.55, rate_func=linear)
        with self.say("b4") as d:
            nc = DashedLine(ax.c2p(25, 0), ax.c2p(25, 160), color=GOLD)
            nl = MathTex(r"N_c\approx 25", color=GOLD, font_size=36).next_to(ax.c2p(25, 160), RIGHT, buff=0.15).shift(DOWN * 0.2)
            zone = Rectangle(width=ax.c2p(25, 0)[0] - ax.c2p(0, 0)[0], height=ax.c2p(0, 160)[1] - ax.c2p(0, 0)[1],
                             fill_color=MUTED, fill_opacity=0.15, stroke_width=0).move_to(ax.c2p(0, 0), aligned_edge=DL)
            self.play(Create(nc), Write(nl), FadeIn(zone), run_time=1.4)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.6)
        # multiple sclerosis: 69 genes, 11 connected
        rs = np.random.default_rng(5)
        pts = []
        while len(pts) < 58:
            p = np.array([rs.uniform(-6.0, 1.0), rs.uniform(-3.0, 2.6), 0])
            if np.linalg.norm(p[:2] - np.array([-2.4, -0.2])) > 1.5 and all(np.linalg.norm(p - q) > 0.45 for q in pts):
                pts.append(p)
        cl = nx.random_labeled_tree(11, seed=2) if hasattr(nx, "random_labeled_tree") else nx.random_tree(11, seed=2)
        cl.add_edges_from([(0, 5), (2, 8)])
        cp = fit(nx.kamada_kawai_layout(cl), (-3.3, -1.5, -1.1, 0.7))
        iso = VGroup(*[Dot(p, radius=0.08, color=RED).set_opacity(0.55) for p in pts])
        cld = VGroup(*[Dot(cp[v], radius=0.1, color=GOLD) for v in cl])
        cle = VGroup(*[Line(cp[a], cp[b], color=GOLD, stroke_width=2.5) for a, b in cl.edges()])
        with self.say("b5") as d:
            self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.5)
            self.clip_on("yt_ms_2minneuro.mp4", "center", "视频：Neuroscientifically Challenged · YouTube", start=20)
        self.clip_off()
        with self.say("b5b") as d:
            self.add(tag)
            self.play(FadeIn(iso, lag_ratio=0.02), FadeIn(cld.copy().set_color(RED).set_opacity(0.55)), run_time=1.4)
            c1 = counter("多发性硬化", "11 / 69", GOLD).move_to(RIGHT * 4.3 + UP * 1.6)
            self.play(Create(cle), FadeIn(cld), FadeIn(c1), run_time=1.4)
        with self.say("b6") as d:
            c2 = counter("随机预期", "约 2 ± 1", MUTED).next_to(c1, DOWN, buff=0.5)
            c3 = MathTex(r"z = 5.8", font_size=48, color=GOLD).next_to(c2, DOWN, buff=0.5)
            self.play(FadeIn(c2), run_time=0.8)
            self.play(Write(c3), run_time=0.8)
        with self.say("b7") as d:
            self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.6)
            waffle = VGroup(*[Square(0.32, stroke_width=0, fill_color=RED if i < 226 else MUTED, fill_opacity=0.85) for i in range(299)]
                            ).arrange_in_grid(13, 23, buff=0.05).move_to(DOWN * 0.3 + LEFT * 1.0)
            self.play(LaggedStart(*[FadeIn(s) for s in waffle], lag_ratio=0.003), run_time=d * 0.45)
            lab = VGroup(T("226 / 299", 40, RED, weight=BOLD), T("显著聚集", 26, INK)).arrange(DOWN, buff=0.15).next_to(waffle, RIGHT, buff=0.5)
            self.play(FadeIn(lab), run_time=0.6)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ separation
    def separation_ch(self):
        tag = self.chapter("二 · 网络分离度")
        G = nx.connected_watts_strogatz_graph(40, 4, 0.15, seed=7)
        P = fit(nx.kamada_kawai_layout(G), (-6.2, 1.0, -3.2, 2.8))
        D = dict(nx.all_pairs_shortest_path_length(G))
        A = [0, 2, 4, 37]
        B = [7, 9, 12, 14]
        dAA, dBB, dAB, sAB = separation(D, A, B)
        dots = {v: Dot(P[v], radius=0.08, color=MUTED) for v in G}
        edges = {e: Line(P[e[0]], P[e[1]], stroke_width=1.4, color=MUTED, stroke_opacity=0.4) for e in G.edges()}
        with self.say("s1") as d:
            self.play(FadeIn(tag), FadeIn(VGroup(*edges.values())), FadeIn(VGroup(*dots.values())), run_time=1.0)
            self.play(*[dots[v].animate.set_color(RED).scale(1.8) for v in A], *[dots[v].animate.set_color(BLUE).scale(1.8) for v in B], run_time=1.0)

        def path_line(a, b, col):
            p = nx.shortest_path(G, a, b)
            return VMobject(color=col, stroke_width=5).set_points_as_corners([P[x] for x in p])
        with self.say("s2") as d:
            ls = []
            for a in A:
                b = min((x for x in A if x != a), key=lambda x: D[a][x])
                ls.append(path_line(a, b, RED))
            self.play(LaggedStart(*[Create(l) for l in ls], lag_ratio=0.3), run_time=d * 0.5)
            fA = MathTex(r"\langle d_{AA}\rangle", f"={dAA:.2f}", font_size=40, color=RED).move_to(RIGHT * 4.2 + UP * 2.0)
            self.play(Write(fA), run_time=0.8)
            self.play(*[FadeOut(l) for l in ls], run_time=0.4)
        with self.say("s3") as d:
            ls = []
            for a in A + B:
                other = B if a in A else A
                b = min(other, key=lambda x: D[a][x])
                ls.append(path_line(a, b, GOLD))
            fB = MathTex(r"\langle d_{BB}\rangle", f"={dBB:.2f}", font_size=40, color=BLUE).next_to(fA, DOWN, buff=0.3)
            self.play(Write(fB), LaggedStart(*[Create(l) for l in ls], lag_ratio=0.15), run_time=d * 0.5)
            fAB = MathTex(r"\langle d_{AB}\rangle", f"={dAB:.2f}", font_size=40, color=GOLD).next_to(fB, DOWN, buff=0.3)
            self.play(Write(fAB), run_time=0.8)
            self.play(*[FadeOut(l) for l in ls], run_time=0.4)
        with self.say("s4") as d:
            f = MathTex(r"s_{AB}=", r"\langle d_{AB}\rangle", r"-", r"\frac{\langle d_{AA}\rangle+\langle d_{BB}\rangle}{2}", font_size=34).next_to(fAB, DOWN, buff=0.5)
            f.shift(RIGHT * (4.0 - f.get_center()[0]))
            self.play(Write(f), run_time=d * 0.5)
        with self.say("s4b") as d:
            left, right = f[1], f[3]
            b1 = SurroundingRectangle(left, color=GOLD, buff=0.05); b2 = SurroundingRectangle(right, color=BLUE, buff=0.05)
            t1 = T("之间", 22, GOLD).next_to(b1, UP, buff=0.1); t2 = T("内部的平均", 22, BLUE).next_to(b2, UP, buff=0.1)
            self.play(Create(b1), FadeIn(t1), run_time=0.8)
            self.wait(d * 0.2)
            self.play(Create(b2), FadeIn(t2), run_time=0.8)
            self.play(FadeOut(VGroup(b1, b2, t1, t2)), run_time=0.5)
            val = MathTex(rf"s_{{AB}} = {sAB:.2f}", font_size=44, color=GOLD).next_to(f, DOWN, buff=0.35)
            assert sAB > 0
            self.play(Write(val), run_time=0.8)
        with self.say("s5") as d:
            C = [2, 4, 37, 1, 3]
            _, _, _, sAC = separation(D, A, C)
            assert sAC < 0
            self.play(*[dots[v].animate.set_color(MUTED).scale(1 / 1.8) for v in B], FadeOut(VGroup(fB, fAB)), run_time=0.6)
            ring = [Circle(radius=0.2, color=VIOLET, stroke_width=4).move_to(P[v]) for v in C]
            self.play(*[Create(r) for r in ring], run_time=0.8)
            v2 = MathTex(rf"s_{{AC}} = {sAC:.2f}", font_size=44, color=VIOLET).next_to(val, DOWN, buff=0.3)
            self.play(Write(v2), run_time=0.8)
            l1 = T("< 0 重叠", 28, VIOLET).next_to(v2, RIGHT, buff=0.25)
            l0 = T("> 0 分开", 28, GOLD).next_to(val, RIGHT, buff=0.25)
            grp = VGroup(val, v2, l0, l1)
            if grp.get_right()[0] > 6.5:
                grp.shift(LEFT * (grp.get_right()[0] - 6.5))
            self.play(FadeIn(l0), FadeIn(l1), run_time=0.6)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ predictions
    def predictions(self):
        tag = self.chapter("二 · 网络距离预测相似")
        bar = VGroup(Rectangle(width=10, height=0.5, stroke_width=0, fill_color=GOLD, fill_opacity=0.85),
                     Rectangle(width=0.75, height=0.5, stroke_width=0, fill_color=VIOLET, fill_opacity=0.95)).move_to(UP * 0.2)
        bar[1].align_to(bar[0], LEFT)
        l1 = T("重叠 约 7%", 26, VIOLET).next_to(bar[1], DOWN, buff=0.25).align_to(bar[0], LEFT)
        l2 = T("分开", 26, GOLD).next_to(bar[0], DOWN, buff=0.25).align_to(bar[0], RIGHT)
        tt = T("所有疾病对", 26, MUTED).next_to(bar, UP, buff=0.25)
        with self.say("c1") as d:
            self.play(FadeIn(tag), FadeIn(tt), GrowFromEdge(bar[0], LEFT), run_time=1.2)
            self.play(FadeIn(bar[1]), FadeIn(l1), FadeIn(l2), run_time=0.8)
        with self.say("c2") as d:
            self.play(FadeOut(VGroup(bar, l1, l2, tt)), run_time=0.8)
        specs = [("功能注释相似性", "降约两个数量级", GREEN, lambda x: 0.92 * np.exp(-2.6 * x) + 0.05),
                 ("症状相似性", "降约一个数量级", BLUE, lambda x: 0.85 * np.exp(-1.8 * x) + 0.08),
                 ("组织共表达", "约 2 倍 → 随机水平", VIOLET, lambda x: 0.35 + 0.5 / (1 + np.exp(8 * (x - 0.45)))),
                 ("共病相对风险", "≥ 10 → 约 1", RED, lambda x: 0.12 + 0.8 / (1 + np.exp(7 * (x - 0.4))))]
        panels = VGroup()
        for i, (nm, note, c, fn) in enumerate(specs):
            ax = Axes(x_range=[0, 1, 1], y_range=[0, 1, 1], x_length=4.2, y_length=1.9,
                      axis_config={"color": MUTED, "include_tip": False, "stroke_width": 2, "tick_size": 0})
            cv = ax.plot(fn, x_range=[0, 1], color=c, stroke_width=4)
            t1 = T(nm, 24, c).next_to(ax, UP, buff=0.1).align_to(ax, LEFT)
            t2 = T(note, 22, INK).move_to(ax.c2p(0.68, 0.8))
            ends = VGroup(T("重叠", 18, MUTED).next_to(ax.c2p(0, 0), DOWN, buff=0.1),
                          T("分开", 18, MUTED).next_to(ax.c2p(1, 0), DOWN, buff=0.1))
            panels.add(VGroup(ax, cv, t1, t2, ends))
        panels.arrange_in_grid(2, 2, buff=(1.0, 0.8)).move_to(DOWN * 0.2)
        sch = T("示意", 20, MUTED).to_corner(DR, buff=0.3)
        with self.say("c3") as d:
            self.play(FadeIn(sch), *[FadeIn(VGroup(p[0], p[2], p[4])) for p in panels[:2]], run_time=0.8)
            for p in panels[:2]:
                self.play(Create(p[1]), FadeIn(p[3]), run_time=d * 0.3)
        with self.say("c4") as d:
            p = panels[2]
            self.play(FadeIn(VGroup(p[0], p[2], p[4])), run_time=0.6)
            self.play(Create(p[1]), FadeIn(p[3]), run_time=d * 0.5)
        with self.say("c5") as d:
            p = panels[3]
            self.play(FadeIn(VGroup(p[0], p[2], p[4])), run_time=0.6)
            self.wait(d * 0.2)
            self.play(Create(p[1]), FadeIn(p[3]), run_time=d * 0.4)
        with self.say("c5b") as d:
            rr = T("相对风险 = 实际同病频率 ÷ 随机预期", 24, RED).next_to(panels[3], DOWN, buff=0.15)
            self.play(Indicate(panels[3][1], color=RED), FadeIn(rr), run_time=1.2)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ beyond shared genes
    def shared(self):
        tag = self.chapter("三 · 超越共享基因")
        W = 11.0
        no = Rectangle(width=W * 0.59, height=1.0, stroke_width=0, fill_color=MUTED, fill_opacity=0.5)
        yes = Rectangle(width=W * 0.41, height=1.0, stroke_width=0, fill_color=BLUE, fill_opacity=0.5)
        row = VGroup(no, yes).arrange(RIGHT, buff=0).move_to(UP * 0.8)
        tn = T("不共享基因 59%", 26, INK).next_to(no, UP, buff=0.2)
        ty = T("共享基因 41%", 26, BLUE).next_to(yes, UP, buff=0.2)
        with self.say("g1") as d:
            self.play(FadeIn(tag), GrowFromEdge(no, LEFT), FadeIn(tn), run_time=1.2)
            sliver = Rectangle(width=0.35, height=1.0, stroke_width=0, fill_color=VIOLET, fill_opacity=0.95).align_to(no, RIGHT).align_to(no, UP)
            sl = T("其中 717 对：网络上重叠", 26, VIOLET).next_to(no, DOWN, buff=0.3).align_to(no, RIGHT)
            self.play(FadeIn(sliver), FadeIn(sl), run_time=1.0)
        with self.say("g2") as d:
            self.play(GrowFromEdge(yes, LEFT), FadeIn(ty), run_time=1.0)
            sep = Rectangle(width=yes.width * 0.87, height=1.0, stroke_width=0, fill_color=GOLD, fill_opacity=0.85).align_to(yes, RIGHT).align_to(yes, UP)
            st = T("87% 网络上分开", 26, GOLD).next_to(yes, DOWN, buff=0.3).align_to(yes, RIGHT)
            self.play(GrowFromEdge(sep, RIGHT), FadeIn(st), run_time=1.2)
        with self.say("g3") as d:
            ne = MathTex(r"\neq", font_size=72, color=RED)
            pair = VGroup(T("共享基因", 36, BLUE), ne, T("网络距离", 36, GOLD)).arrange(RIGHT, buff=0.4).move_to(DOWN * 2.2)
            self.play(FadeIn(pair), run_time=1.0)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ drugs & limits
    def drugs(self):
        tag = self.chapter("三 · 走向药物，以及局限")
        G = self.G
        pos = {v: p * 0.62 + LEFT * 2.3 + DOWN * 0.2 for v, p in self.pos.items()}
        dots, edges = self.netview(pos, r=0.04, eo=0.25)
        deg = dict(G.degree())
        seed = sorted(G, key=lambda v: (abs(deg[v] - 4), -v))[3]
        mod = ball(G, seed, 14)
        Dm = nx.multi_source_dijkstra_path_length(G, mod)
        near = sorted((v for v in G if Dm[v] == 1), key=lambda v: -deg[v])[:3]
        far = sorted((v for v in G if Dm[v] >= 3), key=lambda v: v)[:3]
        with self.say("x1") as d:
            self.play(FadeIn(tag), FadeIn(VGroup(*edges.values())), FadeIn(VGroup(*dots.values())), run_time=1.0)
            self.play(*[dots[v].animate.set_color(RED).scale(2) for v in mod], run_time=1.0)
            self.play(*[dots[v].animate.set_color(BLUE).scale(2.6) for v in near], *[dots[v].animate.set_color(VIOLET).scale(2.6) for v in far], run_time=1.0)
        with self.say("x2") as d:
            ls = []
            for v, c in [(x, BLUE) for x in near] + [(x, VIOLET) for x in far]:
                tgt = min(mod, key=lambda m: nx.shortest_path_length(G, v, m))
                p = nx.shortest_path(G, v, tgt)
                ls.append(VMobject(color=c, stroke_width=4).set_points_as_corners([pos[x] for x in p]))
            self.play(LaggedStart(*[Create(l) for l in ls], lag_ratio=0.2), run_time=d * 0.4)
            lg = VGroup(VGroup(Dot(color=BLUE), T("药物一的靶点：近", 24)).arrange(RIGHT, buff=0.15),
                        VGroup(Dot(color=VIOLET), T("药物二的靶点：远", 24)).arrange(RIGHT, buff=0.15),
                        VGroup(Dot(color=RED), T("疾病模块", 24)).arrange(RIGHT, buff=0.15)).arrange(DOWN, aligned_edge=LEFT).move_to(RIGHT * 4.6 + UP * 1.5)
            self.play(FadeIn(lg), run_time=0.6)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.6)
        with self.say("x2b") as d:
            self.clip_on("proximity_demo.mp4", "full", "本站交互演示：网络邻近度", start=0.3)
        self.clip_off()
        with self.say("x3") as d:
            self.add(tag)
            chips = VGroup(*[VGroup(RoundedRectangle(width=3.4, height=0.9, corner_radius=0.12, color=c), T(s, 30, c))
                             for s, c in (("药物邻近度", BLUE), ("药物组合", GREEN), ("新冠药物重定位", GOLD))]).arrange(RIGHT, buff=0.5).move_to(UP * 0.2)
            for ch in chips:
                ch[1].move_to(ch[0])
            self.play(LaggedStart(*[FadeIn(c, shift=LEFT * 0.2) for c in chips], lag_ratio=0.3), run_time=d * 0.5)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.6)
        # limits
        G2 = nx.barabasi_albert_graph(60, 2, seed=4)
        P2 = fit(nx.kamada_kawai_layout(G2), (-6.0, 0.0, -3.0, 2.8))
        dg = dict(G2.degree())
        d2 = {v: Dot(P2[v], radius=0.05 + 0.03 * np.sqrt(dg[v]), color=MUTED) for v in G2}
        e2 = VGroup(*[Line(P2[a], P2[b], stroke_width=1.2, color=MUTED, stroke_opacity=0.4) for a, b in G2.edges()])
        hot = sorted(G2, key=lambda v: -dg[v])[:6]
        with self.say("x4") as d:
            self.play(FadeIn(e2), FadeIn(VGroup(*d2.values())), run_time=1.0)
            self.play(*[d2[v].animate.set_color(GOLD) for v in hot], run_time=1.0)
            hl = T("研究热点", 26, GOLD).move_to(RIGHT * 3.4 + UP * 2.0)
            self.play(FadeIn(hl), run_time=0.5)
        with self.say("x5") as d:
            th = VGroup(T("门槛 25", 30, GOLD), T("随覆盖率而变", 24, MUTED)).arrange(DOWN, buff=0.15).move_to(RIGHT * 3.4 + UP * 0.4)
            self.play(FadeIn(th), run_time=0.8)
        with self.say("x6") as d:
            a, b = sorted(G2, key=lambda v: dg[v])[:2]
            p = nx.shortest_path(G2, a, b)
            pl = VMobject(color=RED, stroke_width=5).set_points_as_corners([P2[x] for x in p])
            self.play(Create(pl), *[Indicate(d2[x], color=RED) for x in p if x in hot], run_time=1.4)
            alt = VGroup(T("扩散", 26, BLUE), T("随机游走", 26, BLUE)).arrange(RIGHT, buff=0.4).move_to(RIGHT * 3.4 + DOWN * 1.4)
            self.play(FadeIn(alt), run_time=0.8)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ recap
    def recap(self):
        with self.say("r1") as d:
            head = T("三个要点", 40, INK, weight=BOLD).to_edge(UP, buff=0.7)
            self.play(Write(head), run_time=0.8)
        items = [("r2", BLUE, "基因够多，残缺网络中仍可见疾病模块"),
                 ("r3", GOLD, "网络上越近，共表达、症状、共病越相似"),
                 ("r4", RED, "不共享基因，网络距离仍能揭示联系")]
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
