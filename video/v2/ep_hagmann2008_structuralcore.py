"""Paper explainer: Hagmann et al. 2008, the structural core of human cerebral cortex."""
import random

import networkx as nx
import numpy as np
from matplotlib.path import Path as MPath

from common import *  # noqa: F401,F403
from paperkit import fit, counter

TITLE = "大脑皮层的结构核心"

LINES = {
    # hook
    "h1": "我们先来看一张大脑的示意图。皮层上的各个区域，靠白质里的纤维束彼此相连，织成一张巨大的布线图。",
    "h2": "在这张图里，是否存在一个中心——一群区域，彼此紧密相连，又和四面八方都有联系。黄圈在找的，就是这样的地方。",
    "h3": "如果存在，它在哪里，它和大脑安静时的自发活动又有什么关系，这就是这一期要讲的问题。",
    "h4": "【慢】2008年发表的一项研究，第一次在整个皮层的高分辨率尺度上，回答了这些问题。",
    "q0": "这一期分四部分来讲。",
    "q1": "第一部分，怎样把一个人的大脑扫描，变成一张网络。",
    "q2": "第二部分，怎样在这张网络里找到结构核心。",
    "q3": "第三部分，纤维连接和大脑的自发活动之间的关系。",
    "q4": "第四部分，这项研究的意义和局限。",
    # pipeline
    "s1": "先看第一部分。研究只有五名被试，都是健康的右利手男性。",
    "s1b": "每人都做了弥散谱成像。弥散成像，是用磁共振测量水分子沿神经纤维扩散的方向，来推断纤维的走向；弥散谱成像还能分辨交叉的纤维。",
    "s2": "第一步，按解剖标志，把皮层分成六十六个区域。",
    "s2b": "再把它们细分成九百九十八个小区，每个大约一点五平方厘米。这些小区，就是网络的节点。",
    "s3": "第二步，在全脑追踪纤维。画面里，是一个人脑纤维追踪的三维重建。",
    "s3b": "统计每一对小区之间有多少纤维相连，就得到了网络的边。",
    "s4": "纤维密度还要按纤维长度和小区面积做校正。最后得到一个加权的连接矩阵：每一行、每一列是一个区域，越亮的格子，表示连接越强。",
    "s5": "注意，这张网络只包含皮层，不含丘脑这样的皮层下结构。",
    # k-core
    "k1": "下面进入第二部分，找核心。一个直观的工具，叫k核分解。",
    "k2": "先删掉所有只剩一条连接的节点。删完以后，又会冒出新的只剩一条连接的节点，那就接着删。右上角的数字，是当前的门槛。",
    "k3": "然后把门槛提高到二、三、四，一层一层往里剥，就像剥洋葱。",
    "k4": "【慢】一个节点能留到第几层，就是它的核数。颜色从蓝到红，核数越来越高。",
    "k5": "看画了红圈的这个节点。它自己有九条连接，可邻居都孤零零的，第一层就被剥掉了。",
    "k5b": "也就是说，核数高，说明节点身处一个彼此密集相连的群体，而不只是自己连接多。",
    "k6": "在每名被试的网络里，剥到核数二十左右，网络就被剥光了；而最内层的成员，在五个人身上高度一致。",
    # core
    "c1": "作者把度、强度、介数、效率等六项指标的排名综合起来。强度，是一个节点所有连接的权重之和；介数，衡量有多少条最短路径经过它。",
    "c1b": "在各项上都排得靠前的区域，就是这几格黄色，它们被称为结构核心。",
    "c2": "结果是八个解剖亚区，左右两侧都有，集中在大脑的后内侧和顶叶。画面是大脑的内侧面，黄色就是核心的大致位置。",
    "c3": "右边列出了这八个亚区：后扣带皮层、楔前叶、楔叶、旁中央小叶、扣带峡部，还有颞上沟岸，以及顶上和顶下皮层。",
    "c4": "这些区域不只是内部连得紧，还是模块之间的枢纽。模块，就是内部连接紧密的一群区域。画面上每种颜色是一个模块，中间的黄点是核心。",
    "c5": "【慢】把核心合成一个模块来看，模块之间的连接权重，有七成以上都与核心相连。",
    # structure-function
    "f1": "下面进入第三部分，看纤维连接和静息态功能连接之间的关系。",
    "f2": "静息态功能连接，是指人安静躺着时，两个脑区的信号随时间起伏的同步程度。上下两条曲线起伏越一致，功能连接就越强。",
    "f2c": "本站的脑网络专题里，有一个功能连接的阈值演示，用的是模拟数据。拖动保留比例，网络和度最高的脑区都会跟着变。",
    "f3": "好，回到这项研究。左边这张散点图，横轴是两个区域之间的纤维密度，纵轴是它们的功能相关，每个点是一对区域。注意，这是示意数据。",
    "f3b": "你看，纤维连接越强，功能相关通常也越强。",
    "f4": "以楔前叶和后扣带为例，决定系数达到零点五三；把六十六个区域在五人中取平均，达到零点六二。",
    "f4b": "【慢】决定系数，就是r的平方。它说的是：功能相关的高低，有多大比例能由纤维密度来解释。零点六二，就是六成左右。",
    "f5": "作者还指出，结构核心和默认模式网络在位置上明显重叠。默认模式网络，是人安静、不做任务时最活跃的一组脑区。",
    "f5b": "画面上，黄色是结构核心，紫色是默认模式网络。所以，结构核心可能是自发活动得以整合的解剖基础。",
    # why it matters
    "b1": "最后是第四部分。先说意义。这项研究从扫描到连接矩阵的流程，后来成了构建脑网络的范本。",
    "b1b": "它的散点图，也成了结构功能耦合研究的起点。",
    "b2": "在临床研究里，一个常见的假设是：核心和枢纽一旦受损，影响会远远超出局部。",
    "b3": "在一张示意网络上试一试。右边的柱子是全局效率，它衡量网络里任意两点之间平均有多容易到达。",
    "b3b": "拿掉同样多的节点：随机拿掉，效率几乎不变；拿掉核心，效率下降得多得多。",
    # limits
    "l1": "再说局限。首先，样本只有五名男性。这是方法学示范，不是人群推断。",
    "l2": "其次，纤维追踪会产生假连接，也会漏掉真连接，长程连接尤其容易被低估。核心的边界，也依赖算法和分区。",
    "l3": "第三，网络只含皮层。后来加入皮层下区域的研究发现，海马、壳核和丘脑，也属于高度互连的富人俱乐部，也就是枢纽之间彼此紧密相连的那一群。",
    "l4": "最后，结构和功能只是相关。两个区域没有直接纤维，也可能借助间接通路，表现出很强的功能相关。",
    "l5": "另外，静息态分析中回归全局信号这一步，至今仍有争议。",
    # recap
    "r1": "好，我们来总结一下。",
    "r2": "第一，高分辨率的弥散成像，把整个皮层变成了一张可以分析的网络。",
    "r3": "第二，后内侧和顶叶区域构成结构核心，也是模块之间的枢纽。",
    "r4": "第三，纤维连接越强，静息态功能相关通常越强；但样本小，而且只是相关。",
}

OUT = [(-3.2, 0.2), (-3.0, 1.2), (-2.3, 2.0), (-1.2, 2.5), (0.2, 2.6), (1.5, 2.4), (2.6, 1.8), (3.2, 0.9),
       (3.3, -0.1), (2.9, -0.8), (2.2, -1.1), (1.4, -1.0), (0.9, -1.5), (0.0, -1.7), (-1.0, -1.6), (-1.8, -1.2),
       (-2.6, -0.8), (-3.1, -0.4)]


def brain(scale=1.0, shift=ORIGIN, color=MUTED):
    pts = [np.array([x, y, 0]) * scale + shift for x, y in OUT]
    v = VMobject(color=color, stroke_width=4).set_points_smoothly(pts + [pts[0]])
    cb = Ellipse(width=1.5 * scale, height=0.8 * scale, color=color, stroke_width=3).move_to(np.array([2.3, -1.45, 0]) * scale + shift)
    return VGroup(v, cb)


def inside(n, scale, shift, seed=0, margin=0.88):
    P = MPath(np.array(OUT) * margin)
    rng = np.random.default_rng(seed)
    pts = []
    while len(pts) < n:
        p = rng.uniform([-3.3, -1.8], [3.4, 2.7])
        if P.contains_point(p):
            pts.append(np.array([*p, 0]) * scale + shift)
    return pts


def person(col=INK, s=1.0):
    head = Circle(radius=0.18 * s, color=col, stroke_width=3)
    body = Arc(radius=0.32 * s, start_angle=0, angle=PI, color=col, stroke_width=3).next_to(head, DOWN, buff=0.06 * s)
    return VGroup(head, body)


def scatter_xy(n, r2, seed):
    rng = np.random.default_rng(seed)
    x = rng.gamma(2.0, 1.0, n); x = (x - x.mean()) / x.std()
    e = rng.normal(size=n); e -= e.mean(); e -= (e @ x) / (x @ x) * x; e /= e.std()
    r = np.sqrt(r2)
    y = r * x + np.sqrt(1 - r2) * e
    x = (x - x.min()) / (x.max() - x.min()); y = (y - y.min()) / (y.max() - y.min())
    return x, y


def core_net():
    """Modules around a dense core; core bridges most inter-module traffic."""
    G = nx.Graph()
    rng = random.Random(2)
    mods = 5
    for m in range(mods):
        sub = nx.connected_watts_strogatz_graph(12, 4, 0.1, seed=m)
        G.add_nodes_from(((m, v) for v in sub), mod=m)
        G.add_edges_from(((m, u), (m, v)) for u, v in sub.edges())
    core = [("c", i) for i in range(8)]
    G.add_nodes_from(core, mod=-1)
    for i in range(8):
        for j in range(i + 1, 8):
            if rng.random() < 0.75:
                G.add_edge(core[i], core[j])
    for m in range(mods):
        for c in rng.sample(core, 4):
            G.add_edge(c, (m, rng.randrange(12)))
    G.add_edge((0, 3), (1, 8)); G.add_edge((2, 5), (3, 1))
    return G, core


class Episode(Narrated):
    LINES = LINES

    def construct(self):
        self.hook()
        self.parts()
        self.pipeline()
        self.kcore()
        self.core()
        self.structfunc()
        self.matters()
        self.limits()
        self.recap()

    # ------------------------------------------------------------------ hook
    def hook(self):
        sc, sh = 1.6, DOWN * 0.4
        b = brain(sc, sh)
        P = inside(90, sc, sh, seed=1)
        dots = VGroup(*[Dot(p, radius=0.06, color=BLUE) for p in P])
        rng = np.random.default_rng(3)
        fibers = VGroup()
        for _ in range(110):
            i, j = rng.choice(len(P), 2, replace=False)
            if np.linalg.norm(P[i] - P[j]) > 4.5:
                continue
            mid = (P[i] + P[j]) / 2 + np.array([0, -0.4, 0]) * rng.uniform(0.2, 1.0)
            fibers.add(CubicBezier(P[i], mid, mid, P[j], stroke_width=1.3, color=GREEN).set_stroke(opacity=0.45))
        with self.say("h1") as d:
            self.play(Create(b), run_time=1.5)
            self.play(FadeIn(dots, lag_ratio=0.02), run_time=1.2)
            self.play(LaggedStart(*[Create(f) for f in fibers], lag_ratio=0.02), run_time=d * 0.5)
        with self.say("h2") as d:
            ring = Circle(radius=0.9, color=GOLD, stroke_width=4).move_to(P[0])
            self.play(Create(ring), run_time=0.8)
            for k in (5, 17, 40):
                self.play(ring.animate.move_to(P[k]), run_time=d * 0.18)
        with self.say("h3") as d:
            q = T("寻找中心", 56, GOLD, weight=BOLD)
            self.play(VGroup(b, fibers).animate.set_stroke(opacity=0.12), dots.animate.set_opacity(0.15), FadeOut(ring), run_time=0.8)
            self.play(Write(q), run_time=1.0)
        with self.say("h4") as d:
            self.play(FadeOut(q), run_time=0.8)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.6)

    def parts(self):
        head, items = slide("这一期分四部分", ["一  从扫描到网络", "二  寻找结构核心", "三  结构连接与自发活动", "四  意义与局限"])
        with self.say("q0") as d:
            self.play(FadeIn(head, shift=RIGHT * 0.3), run_time=0.6)
        for k, it in zip(("q1", "q2", "q3", "q4"), items):
            with self.say(k) as d:
                self.play(FadeIn(it, shift=RIGHT * 0.3), run_time=0.6)
        self.wait(0.6)
        self.play(FadeOut(head), FadeOut(items), run_time=0.6)

    # ------------------------------------------------------------------ pipeline
    def pipeline(self):
        tag = self.chapter("一 · 从扫描到布线图")
        people = VGroup(*[person(BLUE) for _ in range(5)]).arrange(RIGHT, buff=0.45).move_to(UP * 0.4)
        n5 = T("5 人", 34, BLUE, weight=BOLD).next_to(people, DOWN, buff=0.4)
        with self.say("s1") as d:
            self.play(FadeIn(tag), LaggedStart(*[FadeIn(p) for p in people], lag_ratio=0.15), run_time=1.5)
            self.play(FadeIn(n5), run_time=0.6)
        sc, sh = 1.0, LEFT * 3.4 + DOWN * 0.2
        b = brain(sc, sh)
        rng = np.random.default_rng(5)
        with self.say("s1b") as d:
            self.play(FadeOut(people), FadeOut(n5), Create(b), run_time=1.2)
            # water diffusing along a fibre: little dots streaming along a curve
            path = CubicBezier(sh + LEFT * 2.0 + UP * 0.6, sh + LEFT * 0.5 + DOWN * 0.8, sh + RIGHT * 0.6 + UP * 1.2, sh + RIGHT * 2.2 + UP * 0.3)
            fib = path.copy().set_stroke(GREEN, 4)
            self.play(Create(fib), run_time=1.0)
            ms = VGroup(*[Dot(radius=0.05, color=BLUE).move_to(path.point_from_proportion(t)) for t in np.linspace(0.05, 0.95, 9)])
            self.play(FadeIn(ms), run_time=0.5)
            self.play(*[m.animate.move_to(path.point_from_proportion(min(0.99, t + 0.1))) for m, t in zip(ms, np.linspace(0.05, 0.95, 9))],
                      run_time=d * 0.3, rate_func=linear)
            self.play(FadeOut(ms), FadeOut(fib), run_time=0.5)
        P = inside(160, sc, sh, seed=4, margin=0.9)
        cuts = VGroup()
        for x in np.linspace(-2.6, 2.6, 7):
            cuts.add(Line([x + sh[0] - 0.3 * rng.uniform(), 2.4 * sc + sh[1], 0], [x + sh[0] + 0.3 * rng.uniform(), -1.4 + sh[1], 0],
                          color=MUTED, stroke_width=1.5, stroke_opacity=0.6))
        cuts.add(Line([-3.0 + sh[0], 0.6 + sh[1], 0], [3.1 + sh[0], 0.4 + sh[1], 0], color=MUTED, stroke_width=1.5, stroke_opacity=0.6))
        rois = VGroup(*[Dot(p, radius=0.045, color=BLUE) for p in P])
        c66 = counter("区域", "66", MUTED).move_to(RIGHT * 2.2 + UP * 1.4)
        c998 = counter("小区", "998", BLUE).move_to(RIGHT * 4.6 + UP * 1.4)
        with self.say("s2") as d:
            self.play(Create(cuts), run_time=1.2)
            self.play(FadeIn(c66), run_time=0.5)
        with self.say("s2b") as d:
            self.play(FadeIn(rois, lag_ratio=0.01), run_time=d * 0.4)
            self.play(FadeIn(c998), run_time=0.5)
        with self.say("s3") as d:
            self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.5)
            self.clip_on("yt_tractography_usc.mp4", "center", "视频：USC Stevens Neuroimaging and Informatics Institute · YouTube", start=10)
        self.clip_off()
        fib = VGroup()
        for _ in range(140):
            i, j = rng.choice(len(P), 2, replace=False)
            dd = np.linalg.norm(P[i] - P[j])
            if dd > 3.0 or rng.random() < dd / 4:
                continue
            mid = (P[i] + P[j]) / 2 + np.array([0, -0.3, 0]) * rng.uniform(0.2, 1)
            fib.add(CubicBezier(P[i], mid, mid, P[j], stroke_width=1.2, color=GREEN).set_stroke(opacity=0.5))
        with self.say("s3b") as d:
            self.play(FadeIn(tag), FadeIn(b), FadeIn(rois), run_time=0.6)
            self.play(LaggedStart(*[Create(f) for f in fib], lag_ratio=0.02), run_time=d * 0.6)
        G, _ = core_net()
        order = sorted(G, key=lambda v: (G.nodes[v]["mod"] if G.nodes[v]["mod"] >= 0 else 2.5, str(v)))
        A = nx.to_numpy_array(G, nodelist=order)
        W = A * np.random.default_rng(1).uniform(0.3, 1.0, A.shape); W = np.maximum(W, W.T)
        base = np.array([16, 21, 31]); hot = np.array([255, 194, 75])
        img = (base + (hot - base) * W[..., None]).astype(np.uint8)
        im = ImageMobject(img).set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
        im.height = 3.6
        im.move_to(RIGHT * 3.4 + DOWN * 0.8)
        frame = SurroundingRectangle(im, color=MUTED, buff=0.02, stroke_width=1.5)
        with self.say("s4") as d:
            ar = Arrow(LEFT * 0.2 + DOWN * 0.8, RIGHT * 1.3 + DOWN * 0.8, color=MUTED, buff=0)
            self.play(GrowArrow(ar), FadeIn(im), Create(frame), run_time=1.5)
            lab = T("加权连接矩阵", 24, MUTED).next_to(frame, UP, buff=0.15)
            self.play(FadeIn(lab), run_time=0.6)
        with self.say("s5") as d:
            sub = Ellipse(width=1.1, height=0.6, color=RED, stroke_width=3).move_to(sh + np.array([0.3, 0.1, 0]))
            x = Cross(sub, stroke_color=RED, stroke_width=4, scale_factor=0.6)
            sl = T("皮层下", 22, RED).next_to(sub, DOWN, buff=0.1)
            self.play(Create(sub), FadeIn(sl), run_time=0.8)
            self.play(Create(x), run_time=0.6)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ k-core
    def kcore(self):
        tag = self.chapter("二 · 剥洋葱：k 核分解")
        rng = random.Random(7)
        G = nx.Graph()
        core = list(range(9))
        for i in core:
            for j in core:
                if i < j and rng.random() < 0.8:
                    G.add_edge(i, j)
        nid = 9
        mid = []
        for _ in range(12):
            for c in rng.sample(core, 3):
                G.add_edge(nid, c)
            mid.append(nid); nid += 1
        for i in range(0, 12, 2):
            G.add_edge(mid[i], mid[i + 1])
        for _ in range(14):  # dangling chains
            a = rng.choice(mid + core); G.add_edge(nid, a)
            if rng.random() < 0.5:
                G.add_edge(nid + 1, nid); nid += 1
            nid += 1
        star = nid; G.add_edge(star, rng.choice(mid)); nid += 1
        for _ in range(8):
            G.add_edge(nid, star); nid += 1
        cn = nx.core_number(G)
        kmax = max(cn.values())
        pos = fit(nx.kamada_kawai_layout(G), (-6.2, 3.0, -3.3, 3.0))
        dots = {v: Dot(pos[v], radius=0.1, color=BLUE) for v in G}
        edges = {e: Line(pos[e[0]], pos[e[1]], stroke_width=1.6, color=MUTED, stroke_opacity=0.55) for e in G.edges()}
        with self.say("k1") as d:
            self.play(FadeIn(tag), *[Create(e) for e in edges.values()], *[GrowFromCenter(x) for x in dots.values()], run_time=d * 0.7)
        alive = set(G)
        cols = [MUTED, BLUE, GREEN, VIOLET, GOLD, RED, RED, RED, RED]
        lab = counter("门槛 k", "2", GOLD).move_to(RIGHT * 5.0 + UP * 1.6)

        def peel(k, budget):
            steps = []
            while True:
                H = G.subgraph(alive)
                rm = [v for v in alive if H.degree(v) < k]
                if not rm:
                    break
                steps.append(rm); alive.difference_update(rm)
            for rm in steps:
                anims = [dots[v].animate.set_opacity(0.12) for v in rm]
                anims += [e.animate.set_stroke(opacity=0.06) for (a, b), e in edges.items() if a in rm or b in rm]
                self.play(*anims, run_time=max(0.35, budget / max(1, len(steps))))
            return steps
        with self.say("k2") as d:
            self.play(FadeIn(lab), run_time=0.5)
            peel(2, d * 0.7)
        with self.say("k3") as d:
            for k in range(3, kmax + 2):
                self.play(Transform(lab[1], T(str(k), 40, GOLD, weight=BOLD).move_to(lab[1])), run_time=0.3)
                peel(k, d * 0.7 / kmax)
        with self.say("k4") as d:
            self.play(*[dots[v].animate.set_opacity(1).set_color(cols[min(cn[v], 8)]) for v in G],
                      *[e.animate.set_stroke(opacity=0.5) for e in edges.values()], FadeOut(lab), run_time=1.5)
            leg = VGroup(*[VGroup(Dot(radius=0.1, color=cols[k]), T(f"核数 {k}", 22, INK)).arrange(RIGHT, buff=0.15)
                           for k in range(1, kmax + 1)]).arrange(DOWN, aligned_edge=LEFT, buff=0.18).move_to(RIGHT * 5.2 + UP * 0.6)
            self.play(FadeIn(leg), run_time=0.8)
        with self.say("k5") as d:
            assert G.degree(star) == 9 and cn[star] == 1
            ring = Circle(radius=0.3, color=RED, stroke_width=4).move_to(dots[star])
            self.play(Create(ring), run_time=0.8)
            dl = T("9 条连接，核数 1", 24, RED).move_to(RIGHT * 5.2 + DOWN * 1.6)
            self.play(FadeIn(dl), run_time=0.6)
        with self.say("k5b") as d:
            inner = [v for v in G if cn[v] == kmax]
            self.play(FadeOut(ring), FadeOut(dl), *[Indicate(dots[v], color=cols[kmax], scale_factor=1.6) for v in inner], run_time=1.5)
        with self.say("k6") as d:
            self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.8)
            people = VGroup(*[person(INK, 0.9) for _ in range(5)]).arrange(RIGHT, buff=1.0).move_to(DOWN * 1.8)
            onions = VGroup()
            for p in people:
                on = VGroup(*[Circle(radius=0.75 - 0.15 * i, color=cols[i + 1], stroke_width=3) for i in range(4)])
                on.add(Dot(radius=0.12, color=GOLD))
                onions.add(on.next_to(p, UP, buff=0.4))
            c20 = counter("被剥光时的核数", "约 20", GOLD).to_edge(UP, buff=0.9)
            self.play(FadeIn(people), LaggedStart(*[GrowFromCenter(o) for o in onions], lag_ratio=0.15), run_time=1.6)
            self.play(FadeIn(c20), *[Indicate(o[-1], color=GOLD, scale_factor=2) for o in onions], run_time=1.4)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ the core
    def core(self):
        tag = self.chapter("二 · 核心在后内侧")
        names = ["度", "强度", "介数", "效率", "…"]
        rng = np.random.default_rng(2)
        cols = VGroup()
        for i, nm in enumerate(names):
            h = T(nm, 26, MUTED)
            bars = VGroup(*[Rectangle(width=1.0, height=0.22, stroke_width=0, fill_color=BLUE, fill_opacity=0.25) for _ in range(10)]
                          ).arrange(DOWN, buff=0.08)
            cols.add(VGroup(h, bars).arrange(DOWN, buff=0.25))
        cols.arrange(RIGHT, buff=0.5).move_to(DOWN * 0.2)
        top = [0, 1, 2]
        with self.say("c1") as d:
            self.play(FadeIn(tag), LaggedStart(*[FadeIn(c) for c in cols], lag_ratio=0.15), run_time=1.5)
        with self.say("c1b") as d:
            anims = []
            for c in cols[:4]:
                for k in top:
                    anims.append(c[1][k].animate.set_fill(GOLD, opacity=0.9))
            self.play(LaggedStart(*anims, lag_ratio=0.05), run_time=d * 0.45)
        self.play(FadeOut(cols), run_time=0.6)
        # medial view
        sc, sh = 1.45, LEFT * 1.4 + DOWN * 0.3
        b = brain(sc, sh)
        cc = Arc(radius=1.9 * sc, start_angle=PI * 0.18, angle=PI * 0.62, color=MUTED, stroke_width=6).move_to(sh + np.array([0.1, 0.35, 0]) * sc)
        mtag = T("内侧面", 24, MUTED).next_to(b, DOWN, buff=0.15)
        blob_pts = [np.array([x, y, 0]) * sc + sh for x, y in [(0.9, 1.0), (1.4, 1.9), (2.2, 1.7), (2.7, 1.0), (2.4, 0.3), (1.6, 0.25), (1.0, 0.5)]]
        blob = VMobject(color=GOLD, fill_color=GOLD, fill_opacity=0.45, stroke_width=3).set_points_smoothly(blob_pts + [blob_pts[0]])
        with self.say("c2") as d:
            self.play(Create(b), Create(cc), FadeIn(mtag), run_time=1.4)
            self.play(DrawBorderThenFill(blob), run_time=1.4)
            lr = T("左右两侧", 26, GOLD).next_to(blob, UP, buff=0.3)
            self.play(FadeIn(lr), run_time=0.6)
        regions = ["后扣带皮层", "楔前叶", "楔叶", "旁中央小叶", "扣带峡部", "颞上沟岸", "顶上皮层", "顶下皮层"]
        tags = VGroup(*[T(s, 24, GOLD) for s in regions]).arrange(DOWN, aligned_edge=LEFT, buff=0.17).move_to(RIGHT * 5.2 + DOWN * 0.1)
        with self.say("c3") as d:
            self.play(FadeOut(lr), LaggedStart(*[FadeIn(t, shift=LEFT * 0.2) for t in tags], lag_ratio=0.25), run_time=d * 0.8)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.7)
        # modules + core
        G, core = core_net()
        mcol = [BLUE, GREEN, VIOLET, RED, "#4fc3d1"]
        pos = {}
        for m in range(5):
            ang = PI / 2 + 2 * PI * m / 5
            cen = 2.55 * np.array([np.cos(ang) * 1.45, np.sin(ang), 0]) + DOWN * 0.15
            sub = [v for v in G if G.nodes[v]["mod"] == m]
            for i, v in enumerate(sub):
                t = 2 * PI * i / len(sub)
                pos[v] = cen + 0.62 * np.array([np.cos(t), np.sin(t), 0])
        for i, v in enumerate(core):
            t = 2 * PI * i / len(core)
            pos[v] = 0.75 * np.array([np.cos(t), np.sin(t), 0]) + DOWN * 0.15
        dots = {v: Dot(pos[v], radius=0.08 if G.nodes[v]["mod"] >= 0 else 0.12,
                       color=mcol[G.nodes[v]["mod"]] if G.nodes[v]["mod"] >= 0 else GOLD) for v in G}
        inter = lambda e: G.nodes[e[0]]["mod"] != G.nodes[e[1]]["mod"]
        edges = {e: Line(pos[e[0]], pos[e[1]], stroke_width=1.4, color=MUTED, stroke_opacity=0.45) for e in G.edges()}
        self.cnet = (G, core, pos)
        with self.say("c4") as d:
            self.play(*[Create(e) for e in edges.values()], *[GrowFromCenter(x) for x in dots.values()], run_time=d * 0.6)
        with self.say("c5") as d:
            hl = [e for e in G.edges() if inter(e) and ("c" in (e[0][0], e[1][0]))]
            other = [e for e in G.edges() if inter(e) and e not in hl]
            self.play(*[edges[e].animate.set_stroke(GOLD, width=2.6, opacity=0.95) for e in hl],
                      *[edges[e].animate.set_stroke(INK, width=2.2, opacity=0.8) for e in other],
                      *[edges[e].animate.set_stroke(opacity=0.12) for e in G.edges() if not inter(e)], run_time=1.5)
            big = counter("模块间连接权重", "七成以上与核心相连", GOLD, ).scale(0.85).to_corner(DR, buff=0.4)
            self.play(FadeIn(big), run_time=0.8)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ structure-function
    def structfunc(self):
        tag = self.chapter("三 · 结构预测功能")
        t = np.linspace(0, 12, 300)
        rng = np.random.default_rng(4)
        base = np.convolve(rng.normal(size=300), np.ones(15) / 15, mode="same")
        s1 = base + 0.08 * rng.normal(size=300); s2 = base + 0.08 * rng.normal(size=300)
        ax1 = Axes(x_range=[0, 12, 2], y_range=[-0.6, 0.6, 0.3], x_length=9, y_length=1.3, axis_config={"color": MUTED, "include_tip": False}).move_to(UP * 1.2)
        ax2 = ax1.copy().move_to(DOWN * 0.7)
        c1 = ax1.plot_line_graph(t, np.clip(s1, -0.6, 0.6), line_color=BLUE, add_vertex_dots=False, stroke_width=3)
        c2 = ax2.plot_line_graph(t, np.clip(s2, -0.6, 0.6), line_color=VIOLET, add_vertex_dots=False, stroke_width=3)
        la = T("脑区甲", 24, BLUE).next_to(ax1, LEFT, buff=0.2); lb = T("脑区乙", 24, VIOLET).next_to(ax2, LEFT, buff=0.2)
        with self.say("f1") as d:
            self.play(FadeIn(tag), run_time=0.6)
            b = brain(0.7, ORIGIN)
            self.play(Create(b), run_time=1.2)
            self.play(FadeOut(b), run_time=0.6)
        with self.say("f2") as d:
            self.play(FadeIn(ax1), FadeIn(ax2), FadeIn(la), FadeIn(lb), run_time=0.8)
            self.play(Create(c1), Create(c2), run_time=d * 0.6, rate_func=linear)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.6)
        with self.say("f2c") as d:
            self.clip_on("brain_threshold_demo.mp4", "full", "本站交互演示：脑网络阈值实验（模拟数据）", start=0.3)
        self.clip_off()
        self.add(tag)
        panels = VGroup()
        stats = []
        for k, (r2, n, name, seed) in enumerate(((0.53, 220, "楔前叶与后扣带", 3), (0.62, 160, "66 区 · 5 人平均", 5))):
            x, y = scatter_xy(n, r2, seed)
            got = np.corrcoef(x, y)[0, 1] ** 2
            assert abs(got - r2) < 0.005
            ax = Axes(x_range=[0, 1, 0.5], y_range=[0, 1, 0.5], x_length=4.6, y_length=3.6,
                      axis_config={"color": MUTED, "include_tip": False}).move_to([-3.3 + 6.6 * k, -0.3, 0])
            pts = VGroup(*[Dot(ax.c2p(a, b_), radius=0.035, color=GOLD if k else GREEN).set_opacity(0.8) for a, b_ in zip(x, y)])
            xl = T("纤维密度", 22, MUTED).next_to(ax.x_axis, DOWN, buff=0.2)
            yl = T("功能相关", 22, MUTED).rotate(PI / 2).next_to(ax.y_axis, LEFT, buff=0.2)
            ttl = T(name, 26, INK).next_to(ax, UP, buff=0.35)
            st = MathTex(rf"r^2={got:.2f}", font_size=40, color=GOLD if k else GREEN).move_to(ax.c2p(0.28, 0.88))
            panels.add(VGroup(ax, xl, yl, ttl)); stats.append((pts, st))
        demo = T("示意数据", 20, MUTED).to_edge(DOWN, buff=0.3)
        with self.say("f3") as d:
            self.play(FadeIn(panels[0]), FadeIn(demo), run_time=0.8)
            self.play(LaggedStart(*[FadeIn(p) for p in stats[0][0]], lag_ratio=0.01), run_time=d * 0.5)
        with self.say("f3b") as d:
            ax0 = panels[0][0]
            trend = Line(ax0.c2p(0.05, 0.12), ax0.c2p(0.95, 0.85), color=INK, stroke_width=3)
            self.play(Create(trend), run_time=1.2)
        with self.say("f4") as d:
            self.play(Write(stats[0][1]), run_time=0.8)
            self.play(FadeIn(panels[1]), LaggedStart(*[FadeIn(p) for p in stats[1][0]], lag_ratio=0.01), run_time=d * 0.4)
            self.play(Write(stats[1][1]), run_time=0.8)
        with self.say("f4b") as d:
            exp = T("约六成可由纤维密度解释", 26, GOLD).next_to(panels[1], DOWN, buff=0.15)
            self.play(Indicate(stats[1][1], color=GOLD), FadeIn(exp), run_time=1.2)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.6)
        with self.say("f5") as d:
            self.clip_on("yt_dmn_2minneuro.mp4", "center", "视频：Neuroscientifically Challenged · YouTube", start=30)
        self.clip_off()
        with self.say("f5b") as d:
            self.add(tag)
            sc, sh = 1.3, DOWN * 0.3
            b = brain(sc, sh)
            pts = [np.array([x, y, 0]) * sc + sh for x, y in [(0.9, 1.0), (1.4, 1.9), (2.2, 1.7), (2.7, 1.0), (2.4, 0.3), (1.6, 0.25), (1.0, 0.5)]]
            core = VMobject(color=GOLD, fill_color=GOLD, fill_opacity=0.4).set_points_smoothly(pts + [pts[0]])
            dpts = [np.array([x, y, 0]) * sc + sh for x, y in [(0.7, 0.8), (1.3, 2.1), (2.5, 1.9), (2.9, 0.8), (2.2, 0.0), (1.2, 0.1)]]
            dmn = VMobject(color=VIOLET, fill_color=VIOLET, fill_opacity=0.3).set_points_smoothly(dpts + [dpts[0]])
            front = Ellipse(width=1.2, height=0.9, color=VIOLET, fill_color=VIOLET, fill_opacity=0.3).move_to(np.array([-2.3, 0.6, 0]) * sc + sh)
            lg = VGroup(VGroup(Square(0.25, fill_color=GOLD, fill_opacity=0.6, stroke_width=0), T("结构核心", 24)).arrange(RIGHT, buff=0.15),
                        VGroup(Square(0.25, fill_color=VIOLET, fill_opacity=0.5, stroke_width=0), T("默认模式网络", 24)).arrange(RIGHT, buff=0.15)
                        ).arrange(DOWN, aligned_edge=LEFT).to_corner(UR, buff=0.6)
            self.play(Create(b), run_time=1.0)
            self.play(FadeIn(core), FadeIn(lg[0]), run_time=0.8)
            self.play(FadeIn(dmn), FadeIn(front), FadeIn(lg[1]), run_time=1.0)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ why it matters
    def matters(self):
        tag = self.chapter("四 · 为什么重要")
        steps = ["扫描", "分区", "追踪", "矩阵", "网络"]
        chips = VGroup(*[VGroup(RoundedRectangle(width=1.6, height=0.8, corner_radius=0.12, color=BLUE), T(s, 28)) for s in steps]
                       ).arrange(RIGHT, buff=0.55).move_to(UP * 0.3)
        arrs = VGroup(*[Arrow(chips[i].get_right(), chips[i + 1].get_left(), buff=0.06, color=MUTED, stroke_width=3) for i in range(4)])
        with self.say("b1") as d:
            self.play(FadeIn(tag), LaggedStart(*[FadeIn(c, shift=RIGHT * 0.2) for c in chips], lag_ratio=0.2), run_time=1.6)
            self.play(LaggedStart(*[GrowArrow(a) for a in arrs], lag_ratio=0.2), run_time=1.0)
        with self.say("b1b") as d:
            cp = T("结构–功能耦合研究", 28, GOLD).next_to(chips, DOWN, buff=0.8)
            ar2 = Arrow(chips.get_bottom() + DOWN * 0.05, cp.get_top(), color=GOLD, buff=0.08)
            self.play(GrowArrow(ar2), FadeIn(cp), run_time=1.0)
        self.play(FadeOut(chips), FadeOut(arrs), FadeOut(ar2), FadeOut(cp), run_time=0.6)
        G, core, pos = self.cnet
        rng = random.Random(1)
        noncore = [v for v in G if v not in core]
        e0 = nx.global_efficiency(G)
        ec = nx.global_efficiency(G.subgraph([v for v in G if v not in core]))
        er = np.mean([nx.global_efficiency(G.subgraph([v for v in G if v not in set(rng.sample(noncore, len(core)))])) for _ in range(30)])
        assert (e0 - ec) > 3 * (e0 - er), (e0, ec, er)
        P = {v: p * 0.62 + LEFT * 3.3 + DOWN * 0.1 for v, p in pos.items()}
        dots = {v: Dot(P[v], radius=0.06, color=GOLD if v in core else BLUE) for v in G}
        edges = {e: Line(P[e[0]], P[e[1]], stroke_width=1.2, color=MUTED, stroke_opacity=0.45) for e in G.edges()}
        with self.say("b2") as d:
            self.play(*[Create(e) for e in edges.values()], *[GrowFromCenter(x) for x in dots.values()], run_time=1.4)
            self.play(*[Flash(dots[v], color=RED, line_length=0.15) for v in core], *[dots[v].animate.set_color(RED) for v in core], run_time=1.2)
        ax = Axes(x_range=[0, 3, 1], y_range=[0, 0.5, 0.25], x_length=4.6, y_length=3.6,
                  axis_config={"color": MUTED, "include_tip": False, "font_size": 22},
                  y_axis_config={"numbers_to_include": [0, 0.25, 0.5]}).move_to(RIGHT * 3.4 + DOWN * 0.2)
        yl = T("全局效率", 22, MUTED).rotate(PI / 2).next_to(ax.y_axis, LEFT, buff=0.3)

        def bar(x, h, c, s):
            top = ax.c2p(x, h)[1] - ax.c2p(0, 0)[1]
            r = Rectangle(width=0.9, height=top, fill_color=c, fill_opacity=0.9, stroke_width=0).move_to(ax.c2p(x, 0), aligned_edge=DOWN)
            return VGroup(r, T(s, 22, INK).next_to(ax.c2p(x, 0), DOWN, buff=0.2))
        bs = [bar(0.5, e0, BLUE, "完整"), bar(1.5, er, MUTED, "随机拿掉"), bar(2.5, ec, RED, "拿掉核心")]
        with self.say("b3") as d:
            self.play(Create(ax), FadeIn(yl), FadeIn(bs[0]), run_time=1.0)
        with self.say("b3b") as d:
            self.play(FadeIn(bs[1], shift=UP * 0.2), run_time=0.8)
            self.play(*[d_.animate.set_opacity(0.1) for v, d_ in dots.items() if v in core],
                      *[e.animate.set_stroke(opacity=0.03) for (a, b), e in edges.items() if a in core or b in core], run_time=1.0)
            self.play(FadeIn(bs[2], shift=UP * 0.2), run_time=0.8)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ limits
    def limits(self):
        tag = self.chapter("四 · 局限")
        five = VGroup(*[person(GOLD, 0.8) for _ in range(5)]).arrange(RIGHT, buff=0.3).move_to(LEFT * 3.6)
        crowd = VGroup(*[person(MUTED, 0.45) for _ in range(60)]).arrange_in_grid(6, 10, buff=0.15).move_to(RIGHT * 3.0)
        with self.say("l1") as d:
            self.play(FadeIn(tag), FadeIn(five), run_time=1.0)
            self.play(FadeIn(crowd, lag_ratio=0.01), run_time=1.4)
            ne = T("≠", 60, RED).move_to(LEFT * 0.3)
            self.play(FadeIn(ne), run_time=0.5)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.6)
        sc, sh = 1.4, DOWN * 0.3
        b = brain(sc, sh)
        P = inside(40, sc, sh, seed=8)
        dots = VGroup(*[Dot(p, radius=0.06, color=BLUE) for p in P])
        rng = np.random.default_rng(9)
        ok, fp, fn = VGroup(), VGroup(), VGroup()
        for k in range(36):
            i, j = rng.choice(len(P), 2, replace=False)
            mid = (P[i] + P[j]) / 2 + DOWN * 0.3
            c = CubicBezier(P[i], mid, mid, P[j], stroke_width=2, color=GREEN)
            (fp if k < 5 else ok).add(c)
        far = sorted(((i, j) for i in range(len(P)) for j in range(len(P)) if i < j), key=lambda e: -np.linalg.norm(P[e[0]] - P[e[1]]))[:4]
        for i, j in far:
            mid = (P[i] + P[j]) / 2 + UP * 0.6
            fn.add(DashedVMobject(CubicBezier(P[i], mid, mid, P[j], stroke_width=2.5, color=GOLD), num_dashes=20))
        with self.say("l2") as d:
            self.play(Create(b), FadeIn(dots), Create(ok), Create(fp), run_time=1.4)
            self.play(fp.animate.set_color(RED), run_time=0.8)
            self.play(Create(fn), run_time=1.2)
            lg = VGroup(T("假连接", 24, RED), T("漏掉的长程连接", 24, GOLD)).arrange(DOWN, aligned_edge=LEFT).to_corner(UR, buff=0.6)
            self.play(FadeIn(lg), run_time=0.6)
        with self.say("l3") as d:
            self.play(FadeOut(VGroup(ok, fp, fn, lg)), dots.animate.set_opacity(0.3), run_time=0.8)
            subs = VGroup(*[Ellipse(width=w, height=h, color=c, fill_color=c, fill_opacity=0.5).move_to(np.array([x, y, 0]) * sc + sh)
                            for x, y, w, h, c in ((0.2, 0.3, 0.9, 0.55, RED), (-0.6, 0.0, 0.7, 0.45, VIOLET), (0.6, -0.6, 0.9, 0.35, GREEN))])
            nm = VGroup(T("丘脑", 22, RED), T("壳核", 22, VIOLET), T("海马", 22, GREEN))
            for n_, s_ in zip(nm, subs):
                n_.next_to(s_, DOWN, buff=0.05)
            self.play(LaggedStart(*[GrowFromCenter(s) for s in subs], lag_ratio=0.25), FadeIn(nm), run_time=1.6)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.6)
        A, C, B = LEFT * 3.5 + DOWN * 0.5, UP * 1.6, RIGHT * 3.5 + DOWN * 0.5
        nd = VGroup(*[VGroup(Circle(radius=0.38, color=BLUE, fill_color=BG, fill_opacity=1), T(s, 28)).move_to(p)
                      for p, s in ((A, "甲"), (C, "丙"), (B, "乙"))])
        f1 = Line(A, C, color=GREEN, stroke_width=5).scale(0.8); f2 = Line(C, B, color=GREEN, stroke_width=5).scale(0.8)
        fc = DashedLine(A + RIGHT * 0.4, B + LEFT * 0.4, color=VIOLET, stroke_width=4)
        with self.say("l4") as d:
            self.play(FadeIn(nd), Create(f1), Create(f2), run_time=1.2)
            nf = VGroup(T("无直接纤维", 24, MUTED), T("功能相关强", 24, VIOLET)).arrange(DOWN).next_to(fc, DOWN, buff=0.3)
            self.play(Create(fc), FadeIn(nf), run_time=1.2)
            dot = Dot(A, color=GOLD, radius=0.1)
            self.play(MoveAlongPath(dot, VMobject().set_points_as_corners([A, C, B])), run_time=d * 0.35)
            self.play(FadeOut(dot), run_time=0.3)
        with self.say("l5") as d:
            gsr = T("全局信号回归：仍有争议", 34, GOLD, weight=BOLD).to_edge(DOWN, buff=0.5)
            self.play(VGroup(nd, f1, f2, fc, nf).animate.set_opacity(0.25), FadeIn(gsr), run_time=1.0)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ recap
    def recap(self):
        with self.say("r1") as d:
            head = T("三个要点", 40, INK, weight=BOLD).to_edge(UP, buff=0.7)
            self.play(Write(head), run_time=0.8)
        items = [("r2", BLUE, "弥散谱成像 → 998 个小区的皮层网络"),
                 ("r3", GOLD, "后内侧与顶叶 = 结构核心、模块枢纽"),
                 ("r4", RED, "结构连接预测功能连接，但样本小、只是相关")]
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
