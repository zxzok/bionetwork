"""Animated explainer: 网络何时崩溃 (robustness, percolation, cascades)."""
import random

import networkx as nx
import numpy as np

from common import *  # noqa: F401,F403

TITLE = "网络何时崩溃：渗流、攻击与级联失效"

LINES = {
    # hook
    "h1": "我们先来看一张网络。每个圆点是一个节点，比如一个蛋白质；每条线是一条边，表示两个蛋白质之间有相互作用。",
    "h2": "好，我们来做一个小实验：随机拿掉一些节点，看看这张网络会怎么样。",
    "h3": "现在拿掉了两成的节点。你看，蓝色的这一大块，仍然连在一起，网络的主体还在。",
    "h4": "接下来换一种拿法。这一次，专门挑连接最多的那几个节点，就是画了红圈的这几个。",
    "h5": "【慢】只拿掉百分之五——整张网络，就碎成了很多互不相连的小块。",
    "h6": "同一张网络，面对随机故障很稳，面对有针对的攻击却很脆弱。这一期，我们就把其中的原因讲清楚。",
    "q0": "这一期分三部分来讲。",
    "q1": "第一部分，网络在什么条件下会碎裂。",
    "q2": "第二部分，枢纽为什么既是盾牌，也是软肋。",
    "q3": "第三部分，当故障会传染时，网络怎样一步步崩溃。",
    # percolation
    "p1": "先看第一部分。我们从一个更简单的情形开始：把一堆点随机地连起来。",
    "p2": "右边这张图，横轴是平均每个点连了几条边，纵轴是最大的那一团占全部点的比例。一开始边很少，到处都是零散的小碎片。",
    "p3": "边慢慢增加，小碎片开始合并成稍大的团。",
    "p4": "注意看——当平均每个点连上一条边的时候，最大的那一团突然变大，曲线开始往上冲。",
    "p5": "【慢】这种突然的变化，叫作渗流相变。平均每个点一条边，就是它的临界点。",
    "p6": "把这个过程倒过来，就是网络的故障：节点一个个被删掉，删到超过某个比例，最大的那一团就消失了。",
    # Molloy-Reed
    "m1": "那么，这个临界比例由什么决定。我们用一个直观的办法来想。",
    "m2": "从一个节点出发，沿着一条边走到它的邻居。然后数一数：除了刚才来的那条边，这个邻居还有几条边可以继续往外走。",
    "m3": "如果平均下来，每到一个邻居，都还有不止一条路可以走，扩散就能一直进行下去，最大的那一团就存在。",
    "m4": "这里有个关键：沿着边走到的邻居，往往是连接比较多的节点。在这张网络里，节点平均有不到三条边，而邻居们平均有五条以上。",
    "m5": "【慢】把这个想法写成公式，就是莫洛伊和里德的判据：这个比值要大于二。",
    "m5b": "分母是连接数的平均。分子是连接数平方的平均——平方会把大的数放得更大，所以连接特别多的枢纽，会把这个比值大大抬高。",
    "m6": "随机删掉节点，这个比值会慢慢变小。它降到二的那一刻，就是网络崩溃的临界点。下面这个公式，给出了对应的删除比例。",
    # scale-free
    "s1": "下面进入第二部分。先比较两种网络。左边是随机网络，每个节点的连接数都差不多。",
    "s2": "右边是无标度网络。大多数节点只有一两条边，少数几个枢纽却有几十条，就是这几个闪动的大点。",
    "s3": "【慢】算一下刚才那个比值：随机网络大约是三点七，无标度网络超过八。比值越大，网络越能扛住随机删除。",
    "s4": "我们来做一个实验，用四千多个节点的网络。横轴是删掉节点的比例，纵轴是最大的那一团还剩多少。",
    "s5": "灰色曲线，是随机网络遇到随机故障。删到八成左右，曲线落到零，网络彻底碎了。",
    "s6": "蓝色曲线，是无标度网络遇到随机故障。它下降得很慢，后面拖着一条长尾巴，几乎撑到最后。",
    "s7": "红色曲线，是同一张无标度网络，但这次按连接数从多到少去删。不到百分之十，曲线就掉到了底。",
    "s8": "【慢】所以，枢纽是一把双刃剑：随机故障很难碰到它们，网络因此很稳；可一旦专门攻击它们，网络很快就瓦解。",
    # yeast
    "y0": "这个规律在生物学里也看得到。画面里，是正在出芽繁殖的酵母细胞。",
    "y1": "2001年，《自然》杂志上的一项研究，画出了酵母的蛋白质互作网络，再逐个比对：敲除哪些蛋白质，细胞会死。",
    "y2": "大多数蛋白质只有几个互作伙伴。敲除这样的蛋白质，细胞通常还能活下来。",
    "y3": "统计下来，互作伙伴不超过五个的蛋白质里，只有大约百分之二十一是必需的，也就是一敲除，细胞就会死。",
    "y4": "【慢】而在互作伙伴超过十五个的枢纽蛋白里，这个比例升到了百分之六十二。",
    "y5": "这和刚才的网络实验是一致的：细胞能承受很多随机突变，可枢纽一旦被破坏，往往是致命的。",
    # cascades
    "c1": "最后是第三部分。前面我们假设，一个节点坏了不会影响别人。可在电网这样的系统里，一个节点倒下，它承担的负荷会转给邻居。",
    "c2": "看这张小网络。每个节点都在承担一些负荷。绿色表示还有余量，越接近黄色，越接近它能承受的上限。",
    "c3": "现在，左边这个节点失效了，变成红色。它的负荷平均分给了周围的邻居。",
    "c4": "有几个邻居本来就快到上限，一下子被压垮，也变成红色，又把负荷推给下一圈。",
    "c5": "【慢】就这样一轮接一轮，一个局部的小故障，放大成了整张网络的崩溃。这就是级联失效。",
    "c5b": "研究者用同样的思路，模拟了整个北美电网。他们发现，大约百分之十一的输电线路，容易被卷进这样的级联。",
    "c6": "再看一个真实的例子。2003年8月14日，北美发生大停电，起点只是俄亥俄州几条输电线路的故障。",
    "c6b": "故障一路扩散，最终大约五千万人失去电力。纽约街头，很多人只能步行回家。",
    "c7": "【慢】所以，在负荷会转移的系统里，关键不是多连几条线，而是给每个节点留出足够的冗余容量。",
    # brain
    "b1": "这个道理也适用于大脑。大脑由多个功能模块组成，模块之间靠少数枢纽区域相连。",
    "b2": "脑卒中，是一片脑组织突然缺血受损。如果受损的是某个模块内部的普通区域，影响通常只限于一种功能。",
    "b3": "【慢】但如果受损的恰好是连接多个模块的枢纽，模块之间就断了联系，影响会波及好几种认知功能。",
    # recap
    "r1": "好，我们来总结一下。",
    "r2": "第一，网络什么时候碎裂，由渗流阈值决定；阈值取决于连接数平方的平均，和连接数平均的比值。",
    "r3": "第二，枢纽让无标度网络能扛住随机故障，也让它在针对枢纽的攻击面前格外脆弱。",
    "r4": "第三，当负荷会转移时，小故障会级联放大，所以冗余容量非常关键。",
    "r5": "这个专题的知识页面里，有画面上的这个交互演示。你可以切换网络类型，亲手对比随机删除和定向攻击。",
}


# ----------------------------------------------------------------------------- helpers
def sf_graph(n, gamma, seed, kmax=None):
    rng = np.random.default_rng(seed)
    k = np.floor((1 - rng.random(n)) ** (-1 / (gamma - 1))).astype(int)
    if kmax:
        k = np.minimum(k, kmax)
    if k.sum() % 2:
        k[0] += 1
    G = nx.Graph(nx.configuration_model(k, seed=seed))
    G.remove_edges_from(nx.selfloop_edges(G))
    G = G.subgraph(max(nx.connected_components(G), key=len)).copy()
    return nx.convert_node_labels_to_integers(G)


def spread(pos, power=0.5):
    """Even out density: map each node's radius to its rank, so hubs' crowds and stray leaves both fit."""
    P = np.array(list(pos.values()), float); c = P.mean(0); d = P - c
    r = np.linalg.norm(d, axis=1) + 1e-9
    rank = (np.argsort(np.argsort(r)) + 1) / len(r)
    return {v: c + d[i] / r[i] * rank[i] ** power for i, v in enumerate(pos)}


def fit(pos, box):
    """Scale a networkx layout into box = (xmin, xmax, ymin, ymax) in scene units."""
    pos = spread(pos)
    P = np.array(list(pos.values()))
    lo, hi = P.min(0), P.max(0)
    x0, x1, y0, y1 = box
    s = min((x1 - x0) / (hi[0] - lo[0] + 1e-9), (y1 - y0) / (hi[1] - lo[1] + 1e-9))
    c = (lo + hi) / 2
    mid = np.array([(x0 + x1) / 2, (y0 + y1) / 2])
    return {v: np.array([*((p - c) * s + mid), 0]) for v, p in pos.items()}


def giant(G, removed=()):
    H = G.subgraph([v for v in G if v not in removed])
    if H.number_of_nodes() == 0:
        return set()
    return set(max(nx.connected_components(H), key=len))


class NetView:
    def __init__(self, G, pos, color=BLUE, rmin=0.045, rk=0.022, ew=1.4, eo=0.45):
        self.G, self.pos, self.color, self.eo = G, pos, color, eo
        self.dots = {v: Dot(pos[v], radius=rmin + rk * np.sqrt(G.degree(v)), color=color) for v in G}
        self.edges = {e: Line(pos[e[0]], pos[e[1]], stroke_width=ew, color=color, stroke_opacity=eo) for e in G.edges()}
        self.group = VGroup(VGroup(*self.edges.values()), VGroup(*self.dots.values()))

    def state(self, removed=(), hl=None):
        """Animations that show `removed` gone, the giant component in colour and fragments grey."""
        g = giant(self.G, removed)
        hl = hl or self.color
        anims = []
        for v, d in self.dots.items():
            if v in removed:
                anims.append(d.animate.set_opacity(0))
            elif v in g:
                anims.append(d.animate.set_color(hl).set_opacity(1))
            else:
                anims.append(d.animate.set_color(MUTED).set_opacity(0.8))
        for (u, v), e in self.edges.items():
            if u in removed or v in removed:
                anims.append(e.animate.set_stroke(opacity=0))
            elif u in g:
                anims.append(e.animate.set_stroke(hl, opacity=self.eo))
            else:
                anims.append(e.animate.set_stroke(MUTED, opacity=0.3))
        return anims

    def flash(self, nodes):
        return [self.dots[v].animate.set_color(RED).scale(1.6) for v in nodes]


def counter(label, value, color=INK):
    return VGroup(T(label, 26, MUTED), T(value, 40, color, weight=BOLD)).arrange(DOWN, buff=0.12)


# ----------------------------------------------------------------------------- episode
class Episode(Narrated):
    LINES = LINES

    def construct(self):
        self.hook()
        self.questions()
        self.percolation()
        self.molloy_reed()
        self.scale_free()
        self.yeast()
        self.cascade()
        self.blackout()
        self.brain()
        self.recap()

    # ------------------------------------------------------------------ hook
    def hook(self):
        G = sf_graph(160, 2.3, seed=11, kmax=30)
        pos = fit(nx.kamada_kawai_layout(G), (-6.2, 6.2, -3.4, 3.4))
        net = NetView(G, pos)
        self.net0 = (G, pos)
        with self.say("h1") as d:
            self.play(LaggedStart(*[GrowFromCenter(x) for x in net.dots.values()], lag_ratio=0.01), run_time=d * 0.45)
            self.play(LaggedStart(*[Create(e) for e in net.edges.values()], lag_ratio=0.004), run_time=d * 0.4)
        n = G.number_of_nodes()
        rnd = random.Random(4).sample(list(G), int(0.2 * n))
        lab = counter("已删除", "0%").to_corner(UR, buff=0.5)
        with self.say("h2") as d:
            self.play(FadeIn(lab), run_time=0.5)
        with self.say("h3") as d:
            done = []
            for i, chunk in enumerate(np.array_split(rnd, 4)):
                chunk = list(chunk)
                self.play(*net.flash(chunk), run_time=0.35)
                done += chunk
                new = counter("已删除", f"{round(len(done) / n * 100)}%").move_to(lab)
                self.play(*net.state(done), Transform(lab, new), run_time=0.55)
            g = giant(G, done)
            self.play(*[net.dots[v].animate.scale(1.25) for v in g], rate_func=there_and_back, run_time=1.0)
        # reset and attack
        with self.say("h4") as d:
            self.play(*net.state(()), *[x.animate.scale(1 / 1.6) for v, x in net.dots.items() if v in done],
                      Transform(lab, counter("已删除", "0%").move_to(lab)), run_time=1.2)
            hubs = sorted(G, key=G.degree, reverse=True)[: max(1, round(0.05 * n))]
            rings = VGroup(*[Circle(radius=net.dots[h].radius + 0.12, color=RED, stroke_width=3).move_to(net.dots[h]) for h in hubs])
            self.play(LaggedStart(*[Create(r) for r in rings], lag_ratio=0.2), run_time=1.6)
        with self.say("h5") as d:
            self.play(*net.flash(hubs), FadeOut(rings), run_time=0.6)
            self.play(*net.state(hubs, hl=GOLD), Transform(lab, counter("已删除", "5%", RED).move_to(lab)), run_time=1.6)
        with self.say("h6") as d:
            q = T("同一张网络，两种结局", 56, GOLD, weight=BOLD)
            self.play(net.group.animate.set_opacity(0.15), FadeOut(lab), run_time=1.0)
            self.play(Write(q), run_time=1.2)
        self.play(FadeOut(q), FadeOut(net.group), run_time=0.8)

    def questions(self):
        head, items = slide("这一期分三部分", ["一  网络何时碎裂：渗流阈值", "二  枢纽：既是盾牌，也是软肋", "三  故障会传染：级联失效"])
        with self.say("q0") as d:
            self.play(FadeIn(head, shift=RIGHT * 0.3), run_time=0.6)
        for k, it in zip(("q1", "q2", "q3"), items):
            with self.say(k) as d:
                self.play(FadeIn(it, shift=RIGHT * 0.3), run_time=0.6)
        self.wait(0.8)
        self.play(FadeOut(head), FadeOut(items), run_time=0.6)

    # ------------------------------------------------------------------ percolation
    def percolation(self):
        tag = self.chapter("一  渗流：大团何时出现")
        N, kfin = 220, 3.0
        rng = random.Random(7)
        G = nx.gnm_random_graph(N, int(kfin * N / 2), seed=7)
        edges = list(G.edges()); rng.shuffle(edges)
        pos = fit(nx.spring_layout(G, seed=3, k=0.25, iterations=200), (-6.6, -0.6, -3.3, 3.0))
        H = nx.empty_graph(N)
        dots = {v: Dot(pos[v], radius=0.05, color=MUTED) for v in range(N)}
        ax = Axes(x_range=[0, 3, 1], y_range=[0, 1, 0.5], x_length=5.2, y_length=3.6,
                  axis_config={"color": MUTED, "include_tip": False, "font_size": 24},
                  x_axis_config={"numbers_to_include": [0, 1, 2, 3]},
                  y_axis_config={"numbers_to_include": [0, 0.5, 1]}).shift(RIGHT * 3.6 + DOWN * 0.3)
        xl = MathTex(r"\langle k\rangle", color=MUTED, font_size=32).next_to(ax.x_axis, DOWN, buff=0.35)
        yl = T("最大团簇占比", 22, MUTED).rotate(PI / 2).next_to(ax.y_axis, LEFT, buff=0.35)

        def S_of(k):
            s = 0.5
            for _ in range(200):
                s = 1 - np.exp(-k * s)
            return s if k > 1 else 0.0
        curve = ax.plot(S_of, x_range=[0, 3, 0.01], color=GOLD, stroke_width=4, use_smoothing=False)
        tracker = ValueTracker(0)
        mark = always_redraw(lambda: Dot(ax.c2p(tracker.get_value(), S_of(tracker.get_value())), color=GOLD, radius=0.08))

        with self.say("p1") as d:
            self.play(FadeIn(tag), LaggedStart(*[FadeIn(x) for x in dots.values()], lag_ratio=0.003), run_time=d * 0.6)
        lines = {}

        def grow_to(k, rt):
            m = int(k * N / 2)
            new = edges[H.number_of_edges(): m]
            H.add_edges_from(new)
            g = set(max(nx.connected_components(H), key=len))
            big = len(g) > 0.08 * N
            for e in new:
                lines[e] = Line(pos[e[0]], pos[e[1]], stroke_width=1.3, color=MUTED, stroke_opacity=0.5)
            anims = [Create(lines[e]) for e in new]
            for v, x in dots.items():
                anims.append(x.animate.set_color(GOLD if (big and v in g) else MUTED))
            for (u, v), l in lines.items():
                if l not in [lines[e] for e in new]:
                    anims.append(l.animate.set_stroke(GOLD if (big and u in g) else MUTED, opacity=0.6 if (big and u in g) else 0.4))
            self.play(*anims, tracker.animate.set_value(k), run_time=rt)

        with self.say("p2") as d:
            self.play(Create(ax), FadeIn(xl), FadeIn(yl), run_time=1.2)
            self.add(mark)
            grow_to(0.3, d * 0.5)
        with self.say("p3") as d:
            grow_to(0.6, d * 0.4); grow_to(0.85, d * 0.4)
        with self.say("p4") as d:
            grow_to(1.0, d * 0.25)
            grow_to(1.3, d * 0.25); grow_to(1.7, d * 0.25)
        with self.say("p5") as d:
            crit = DashedLine(ax.c2p(1, 0), ax.c2p(1, 1), color=RED)
            cl = MathTex(r"\langle k\rangle = 1", color=RED, font_size=30).next_to(ax.c2p(1, 1), UP, buff=0.1)
            grow_to(2.2, d * 0.3)
            self.play(Create(crit), Write(cl), Create(curve), run_time=d * 0.4)
        with self.say("p6") as d:
            grow_to(3.0, d * 0.3)
            arrow = Arrow(ax.c2p(2.9, 0.15), ax.c2p(1.2, 0.15), color=RED, buff=0)
            rev = T("故障 = 倒放", 26, RED).next_to(arrow, UP, buff=0.1)
            self.play(GrowArrow(arrow), FadeIn(rev), run_time=d * 0.3)
        self.remove(mark)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ Molloy-Reed
    def molloy_reed(self):
        tag = self.chapter("一  一个直观判据")
        G = sf_graph(70, 2.3, seed=21, kmax=14)
        pos = fit(nx.kamada_kawai_layout(G), (-6.4, -0.4, -3.2, 3.2))
        net = NetView(G, pos, eo=0.35)
        with self.say("m1") as d:
            self.play(FadeIn(tag), FadeIn(net.group), run_time=1.2)
        # a low-degree start node next to the biggest hub
        hub = max(G, key=G.degree)
        a = min(G.neighbors(hub), key=G.degree)
        walker = Dot(pos[a], radius=0.11, color=GOLD)
        with self.say("m2") as d:
            self.play(Indicate(net.dots[a], color=GOLD, scale_factor=1.8), FadeIn(walker), run_time=1.0)
            self.play(walker.animate.move_to(pos[hub]), net.edges.get((a, hub), net.edges.get((hub, a))).animate.set_stroke(GOLD, width=4, opacity=1), run_time=1.2)
            outs = [w for w in G.neighbors(hub) if w != a]
            glow = [net.edges.get((hub, w), net.edges.get((w, hub))) for w in outs]
            self.play(LaggedStart(*[e.animate.set_stroke(GREEN, width=3.5, opacity=1) for e in glow], lag_ratio=0.12), run_time=d * 0.35)
            cnt = counter("还有几条路", str(len(outs)), GREEN).move_to(RIGHT * 3.4 + UP * 2.2)
            self.play(FadeIn(cnt), run_time=0.6)
        with self.say("m3") as d:
            br = VGroup(T("平均出口数", 34), MathTex(r"> 1", font_size=44, color=INK)).arrange(RIGHT, buff=0.2).move_to(RIGHT * 3.4 + UP * 0.6)
            self.play(Write(br), run_time=1.2)
        kn = np.mean([d_ for _, d_ in G.degree()])
        kk = np.mean([G.degree(w) for u, v in G.edges() for w in (u, v)])
        with self.say("m4") as d:
            b1 = counter("节点平均度", f"{kn:.1f}", BLUE)
            b2 = counter("邻居平均度", f"{kk:.1f}", GOLD)
            row = VGroup(b1, b2).arrange(RIGHT, buff=1.0).move_to(RIGHT * 3.4 + DOWN * 1.2)
            self.play(FadeIn(b1, shift=UP * 0.2), run_time=0.8)
            self.wait(d * 0.35)
            self.play(FadeIn(b2, shift=UP * 0.2), run_time=0.8)
        with self.say("m5") as d:
            f1 = MathTex(r"\kappa=\frac{\langle k^2\rangle}{\langle k\rangle}", r">", r"2", font_size=64, color=INK)
            f1[0].set_color(GOLD)
            self.play(FadeOut(net.group), FadeOut(walker), FadeOut(cnt), FadeOut(br), FadeOut(row), run_time=0.8)
            self.play(Write(f1), run_time=d * 0.5)
        with self.say("m5b") as d:
            num = T("连接数平方的平均", 26, GOLD).next_to(f1, UR, buff=0.2).shift(LEFT * 1.2)
            den = T("连接数的平均", 26, BLUE).next_to(f1, DR, buff=0.2).shift(LEFT * 1.2)
            self.play(FadeIn(den, shift=UP * 0.2), run_time=0.6)
            self.wait(d * 0.2)
            self.play(FadeIn(num, shift=DOWN * 0.2), run_time=0.6)
        self.play(FadeOut(num), FadeOut(den), run_time=0.5)
        with self.say("m6") as d:
            f2 = MathTex(r"f_c = 1-\frac{1}{\kappa-1}", font_size=58, color=RED).next_to(f1, DOWN, buff=0.8)
            self.play(f1.animate.shift(UP * 1.0), run_time=0.6)
            f2.next_to(f1, DOWN, buff=0.8)
            self.play(Write(f2), run_time=d * 0.45)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ scale-free vs random
    def scale_free(self):
        tag = self.chapter("二  枢纽的两面")
        Ge = nx.gnm_random_graph(90, 120, seed=5)
        Ge = Ge.subgraph(max(nx.connected_components(Ge), key=len)).copy()
        Gs = sf_graph(110, 2.2, seed=9, kmax=40)
        ve = NetView(Ge, fit(nx.kamada_kawai_layout(Ge), (-6.6, -0.8, -2.9, 2.6)), color=MUTED, eo=0.5)
        vs = NetView(Gs, fit(nx.kamada_kawai_layout(Gs), (0.8, 6.6, -2.9, 2.6)), color=BLUE, eo=0.45)
        le = T("随机网络", 28, INK).move_to(LEFT * 3.7 + UP * 3.2)
        ls = T("无标度网络", 28, INK).move_to(RIGHT * 3.7 + UP * 3.2)
        with self.say("s1") as d:
            self.play(FadeIn(tag), FadeIn(le), FadeIn(ve.group), run_time=d * 0.5)
        with self.say("s2") as d:
            self.play(FadeIn(ls), FadeIn(vs.group), run_time=1.2)
            top = sorted(Gs, key=Gs.degree, reverse=True)[:4]
            self.play(*[Indicate(vs.dots[h], color=GOLD, scale_factor=1.5) for h in top], run_time=1.4)
        def kappa(G):
            k = np.array([x for _, x in G.degree()])
            return (k ** 2).mean() / k.mean()
        with self.say("s3") as d:
            ke = MathTex(rf"\kappa \approx {kappa(Ge):.1f}", font_size=40, color=MUTED).next_to(ve.group, DOWN, buff=0.15)
            ks = MathTex(rf"\kappa \approx {kappa(Gs):.1f}", font_size=40, color=GOLD).next_to(vs.group, DOWN, buff=0.15)
            self.play(Write(ke), run_time=0.8)
            self.play(Write(ks), run_time=0.8)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.8)
        # simulation curves
        Gs = sf_graph(5000, 2.2, seed=5, kmax=1200)
        N = Gs.number_of_nodes()
        Ger = nx.gnm_random_graph(N, Gs.number_of_edges(), seed=5)
        rng = np.random.default_rng(1)
        fs = np.linspace(0, 1, 41)

        def sweep(G, order):
            out = []
            for f in fs:
                H = G.copy(); H.remove_nodes_from(order[: int(f * N)])
                out.append(max((len(c) for c in nx.connected_components(H)), default=0) / N)
            return out
        r = list(rng.permutation(N))
        y_er, y_sf = sweep(Ger, r), sweep(Gs, r)
        att = sorted(Gs, key=Gs.degree, reverse=True)
        fa = np.linspace(0, 0.12, 25)
        y_at = []
        for f in fa:
            H = Gs.copy(); H.remove_nodes_from(att[: int(f * N)])
            y_at.append(max(len(c) for c in nx.connected_components(H)) / N)
        ax = Axes(x_range=[0, 1, 0.2], y_range=[0, 1, 0.5], x_length=9, y_length=4.8,
                  axis_config={"color": MUTED, "include_tip": False, "font_size": 24},
                  x_axis_config={"numbers_to_include": [0, 0.2, 0.4, 0.6, 0.8, 1]},
                  y_axis_config={"numbers_to_include": [0, 0.5, 1]}).shift(DOWN * 0.4 + LEFT * 0.6)
        xl = T("删除节点的比例", 24, MUTED).next_to(ax.x_axis, DOWN, buff=0.4)
        yl = T("最大连通分支", 24, MUTED).rotate(PI / 2).next_to(ax.y_axis, LEFT, buff=0.35)

        def line(xs, ys, c):
            return ax.plot_line_graph(xs, ys, line_color=c, add_vertex_dots=False, stroke_width=5)
        c_er, c_sf, c_at = line(fs, y_er, MUTED), line(fs, y_sf, BLUE), line(fa, y_at, RED)
        lg = VGroup(*[VGroup(Line(ORIGIN, RIGHT * 0.5, color=c, stroke_width=5), T(s, 22, INK)).arrange(RIGHT, buff=0.15)
                      for c, s in ((MUTED, "随机网络 · 随机故障"), (BLUE, "无标度 · 随机故障"), (RED, "无标度 · 攻击枢纽"))]
                    ).arrange(DOWN, aligned_edge=LEFT, buff=0.2).to_corner(UR, buff=0.5).shift(DOWN * 0.6)
        with self.say("s4") as d:
            self.play(Create(ax), FadeIn(xl), FadeIn(yl), run_time=d * 0.5)
        with self.say("s5") as d:
            self.play(Create(c_er), FadeIn(lg[0]), run_time=d * 0.75, rate_func=linear)
        with self.say("s6") as d:
            self.play(Create(c_sf), FadeIn(lg[1]), run_time=d * 0.75, rate_func=linear)
        with self.say("s7") as d:
            self.play(Create(c_at), FadeIn(lg[2]), run_time=d * 0.5, rate_func=linear)
            zone = ax.get_area(ax.plot(lambda x: 1, x_range=[0, 0.1]), x_range=[0, 0.1], color=RED, opacity=0.18)
            self.play(FadeIn(zone), run_time=0.8)
        with self.say("s8") as d:
            self.play(Indicate(c_sf, color=BLUE), run_time=1.0)
            self.play(Indicate(c_at, color=RED), run_time=1.0)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ yeast
    def yeast(self):
        tag = self.chapter("二  酵母的蛋白质网络")
        cell = Ellipse(width=6.0, height=4.6, color=GREEN, stroke_width=4).shift(LEFT * 3.2 + DOWN * 0.2)
        G = sf_graph(60, 2.3, seed=31, kmax=14)
        net = NetView(G, fit(nx.kamada_kawai_layout(G), (-5.6, -0.8, -1.9, 1.6)), color=GREEN, eo=0.4)
        with self.say("y0") as d:
            self.clip_on("yt_yeast_timelapse.mp4", "center", "视频：Wolfe Lab · YouTube", start=2)
        self.clip_off()
        with self.say("y1") as d:
            self.play(FadeIn(tag), Create(cell), run_time=1.2)
            self.play(FadeIn(net.group), run_time=1.2)
        leaf = min(G, key=G.degree)
        hub = max(G, key=G.degree)
        ok = T("存活", 30, GREEN, weight=BOLD).next_to(cell, DOWN, buff=0.25)
        with self.say("y2") as d:
            x = Cross(net.dots[leaf], stroke_color=RED, scale_factor=2.5)
            self.play(Create(x), net.dots[leaf].animate.set_opacity(0), run_time=0.9)
            self.play(FadeIn(ok), cell.animate.set_stroke(GREEN), run_time=0.8)
        ax = Axes(x_range=[0, 3, 1], y_range=[0, 80, 20], x_length=5.2, y_length=4.2,
                  axis_config={"color": MUTED, "include_tip": False, "font_size": 22},
                  y_axis_config={"numbers_to_include": [0, 20, 40, 60, 80]}).shift(RIGHT * 3.6 + DOWN * 0.2)
        yl = T("必需蛋白比例 (%)", 22, MUTED).rotate(PI / 2).next_to(ax.y_axis, LEFT, buff=0.35)

        def bar(x, h, c, lab):
            r = Rectangle(width=1.1, height=0.001, fill_color=c, fill_opacity=0.9, stroke_width=0).move_to(ax.c2p(x, 0), aligned_edge=DOWN)
            tgt = Rectangle(width=1.1, height=ax.c2p(0, h)[1] - ax.c2p(0, 0)[1], fill_color=c, fill_opacity=0.9, stroke_width=0).move_to(ax.c2p(x, 0), aligned_edge=DOWN)
            v = T(f"{h}%", 30, c, weight=BOLD).next_to(tgt, UP, buff=0.1)
            l = T(lab, 22, INK).next_to(ax.c2p(x, 0), DOWN, buff=0.25)
            return r, tgt, v, l
        with self.say("y3") as d:
            self.play(Create(ax), FadeIn(yl), run_time=1.0)
            r1, t1, v1, l1 = bar(1, 21, BLUE, "≤5 个伙伴")
            self.add(r1); self.play(Transform(r1, t1), FadeIn(l1), run_time=1.0); self.play(FadeIn(v1), run_time=0.4)
        with self.say("y4") as d:
            r2, t2, v2, l2 = bar(2, 62, RED, ">15 个伙伴")
            self.add(r2); self.play(Transform(r2, t2), FadeIn(l2), run_time=1.2); self.play(FadeIn(v2), run_time=0.4)
        with self.say("y5") as d:
            dead = T("致死", 30, RED, weight=BOLD).move_to(ok)
            x2 = Cross(net.dots[hub], stroke_color=RED, scale_factor=1.6)
            self.play(Create(x2), *net.state([hub, leaf], hl=GREEN), run_time=1.0)
            self.play(Transform(ok, dead), cell.animate.set_stroke(RED), net.group.animate.set_opacity(0.35), run_time=1.0)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ cascade
    def cascade(self):
        tag = self.chapter("三  级联失效")
        G = nx.triangular_lattice_graph(5, 10)
        G = nx.convert_node_labels_to_integers(G, label_attribute="xy")
        pos = fit({v: np.array(G.nodes[v]["xy"], float) + np.array([0.5 * (G.nodes[v]["xy"][1] % 2), 0]) for v in G}, (-6.0, 6.0, -2.8, 2.6))
        rng = np.random.default_rng(2)
        load = {v: float(rng.uniform(0.55, 0.88)) for v in G}
        cap = 1.0
        start = min(G, key=lambda v: np.linalg.norm(pos[v][:2] - np.array([-3.5, 0.0])))
        # simulate load redistribution rounds
        failed, rounds, L = set(), [], dict(load)
        front = {start}
        while front:
            rounds.append(sorted(front))
            failed |= front
            nxt = set()
            for v in front:
                alive = [w for w in G.neighbors(v) if w not in failed]
                for w in alive:
                    L[w] += L[v] / len(alive)
            for w in G:
                if w not in failed and L[w] > cap:
                    nxt.add(w)
            front = nxt
            if len(rounds) > 12:
                break
        self.cas = (len(failed), G.number_of_nodes())
        cmap = lambda x: interpolate_color(ManimColor(GREEN), ManimColor(GOLD), np.clip((x - 0.55) / 0.4, 0, 1))
        dots = {v: Dot(pos[v], radius=0.13, color=cmap(load[v])) for v in G}
        edges = VGroup(*[Line(pos[u], pos[v], stroke_width=1.5, color=MUTED, stroke_opacity=0.5) for u, v in G.edges()])
        with self.say("c1") as d:
            self.play(FadeIn(tag), Create(edges), LaggedStart(*[GrowFromCenter(x) for x in dots.values()], lag_ratio=0.01), run_time=d * 0.6)
        with self.say("c2") as d:
            self.play(LaggedStart(*[Indicate(dots[v], scale_factor=1.4, color=dots[v].get_color()) for v in random.Random(1).sample(list(G), 12)], lag_ratio=0.1), run_time=d * 0.6)
        cur = dict(load)
        dead = set()

        def round_anims(i):
            group = rounds[i]
            anims = []
            for v in group:
                dead.add(v)
                anims.append(dots[v].animate.set_color(RED).scale(1.3))
            # neighbours absorb load
            for v in group:
                alive = [w for w in G.neighbors(v) if w not in dead]
                for w in alive:
                    cur[w] += cur[v] / len(alive)
            for w in G:
                if w not in dead:
                    anims.append(dots[w].animate.set_color(cmap(cur[w])))
            return anims
        with self.say("c3") as d:
            self.play(Flash(dots[start], color=RED, line_length=0.35), *round_anims(0), run_time=1.2)
        with self.say("c4") as d:
            k = max(1, (len(rounds) - 1) // 2)
            for i in range(1, 1 + k):
                if i < len(rounds):
                    self.play(*round_anims(i), run_time=max(0.5, d * 0.7 / k))
        with self.say("c5") as d:
            rest = list(range(1 + k, len(rounds)))
            for i in rest:
                self.play(*round_anims(i), run_time=max(0.4, d * 0.6 / max(1, len(rest))))
            share = counter("失效节点", f"{len(dead)}/{G.number_of_nodes()}", RED).to_corner(UR, buff=0.5)
            self.play(FadeIn(share), run_time=0.6)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)
        with self.say("c5b") as d:
            self.clip_on("yt_grid_cascade_motter.mp4", "center", "视频：T. Nishikawa & A. E. Motter · YouTube", start=56)
        self.clip_off()

    def blackout(self):
        rng = np.random.default_rng(4)
        pts = []
        while len(pts) < 520:
            p = np.array([rng.uniform(-6.6, 6.6), rng.uniform(-3.4, 3.0), 0])
            # denser "cities" around a few centres
            if rng.random() < 0.12 or min(np.linalg.norm(p[:2] - c) for c in ([-2.5, 0.6], [1.8, 1.2], [3.6, -0.8], [-0.4, -1.6])) < 1.3:
                pts.append(p)
        lights = VGroup(*[Dot(p, radius=rng.uniform(0.02, 0.05), color=GOLD).set_opacity(rng.uniform(0.5, 1)) for p in pts])
        origin = np.array([-2.0, 0.2, 0])
        date = T("2003 年 8 月 14 日", 34, INK, weight=BOLD).to_corner(UL, buff=0.5)
        with self.say("c6") as d:
            self.play(FadeIn(lights, lag_ratio=0.002), FadeIn(date), run_time=1.6)
            self.play(Flash(origin, color=RED, line_length=0.5, num_lines=12), run_time=0.8)
            order = sorted(range(len(pts)), key=lambda i: np.linalg.norm(pts[i] - origin) + rng.uniform(0, 1.5))
            dark = [lights[i] for i in order[: int(0.8 * len(pts))]]
            self.play(LaggedStart(*[x.animate.set_opacity(0.06) for x in dark], lag_ratio=0.004), run_time=d * 0.5)
        with self.say("c6b") as d:
            self.play(FadeOut(date), lights.animate.set_opacity(0.05), run_time=0.4)
            self.clip_on("yt_blackout_bloomberg.mp4", "center", "视频：Bloomberg Television · YouTube", start=44)
            self.wait(d * 0.5)
            self.clip_off()
            self.clip_on("yt_blackout_bloomberg.mp4", "center", "视频：Bloomberg Television · YouTube", start=91)
        self.clip_off()
        with self.say("c7") as d:
            bar_full = Rectangle(width=8.0, height=0.8, stroke_color=INK, stroke_width=2)
            used = Rectangle(width=5.2, height=0.8, fill_color=GREEN, fill_opacity=0.9, stroke_width=0).align_to(bar_full, LEFT)
            reserve = Rectangle(width=2.8, height=0.8, fill_color=BLUE, fill_opacity=0.5, stroke_width=0).next_to(used, RIGHT, buff=0)
            lab = VGroup(T("日常负荷", 30, GREEN).next_to(used, DOWN, buff=0.15), T("冗余容量", 30, BLUE).next_to(reserve, DOWN, buff=0.15))
            g = VGroup(bar_full, used, reserve, lab).move_to(ORIGIN)
            self.play(lights.animate.set_opacity(0.03), run_time=0.8)
            self.play(Create(bar_full), FadeIn(used), run_time=0.8)
            self.play(FadeIn(reserve, shift=RIGHT * 0.3), FadeIn(lab), run_time=0.8)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ brain
    def brain(self):
        tag = self.chapter("三  脑网络中的枢纽")
        cols = [BLUE, GREEN, VIOLET, GOLD]
        centers = [np.array(c) for c in ([-3.2, 1.5], [3.2, 1.5], [-3.2, -1.9], [3.2, -1.9])]
        G = nx.Graph()
        rng = random.Random(3)
        pos = {}
        for m, c in enumerate(centers):
            sub = nx.connected_watts_strogatz_graph(12, 4, 0.2, seed=m)
            p = nx.circular_layout(sub)
            for v in sub:
                G.add_node((m, v), mod=m)
                pos[(m, v)] = np.array([*(c + 1.05 * np.array(p[v])), 0])
            G.add_edges_from(((m, u), (m, v)) for u, v in sub.edges())
        hub = ("h", 0)
        G.add_node(hub, mod=-1)
        pos[hub] = np.array([0, -0.2, 0])
        for m in range(4):
            for v in rng.sample(range(12), 2):
                G.add_edge(hub, (m, v))
        G.add_edge((0, 3), (1, 9)); G.add_edge((2, 1), (3, 7))
        dots = {v: Dot(pos[v], radius=0.1 if v != hub else 0.2, color=cols[G.nodes[v]["mod"]] if v != hub else RED) for v in G}
        edges = {e: Line(pos[e[0]], pos[e[1]], stroke_width=1.6, color=MUTED, stroke_opacity=0.5) for e in G.edges()}
        with self.say("b1") as d:
            self.play(FadeIn(tag), *[Create(e) for e in edges.values()], *[GrowFromCenter(x) for x in dots.values()], run_time=d * 0.6)
        with self.say("b2") as d:
            self.clip_on("yt_stroke_britannica.mp4", "center", "视频：Encyclopaedia Britannica · YouTube", start=31)
            self.wait(d * 0.45)
            self.clip_off()
            v0 = (0, 6)
            self.play(Flash(dots[v0], color=RED), dots[v0].animate.set_opacity(0.1),
                      *[e.animate.set_stroke(opacity=0.05) for e_, e in edges.items() if v0 in e_], run_time=1.0)
            ring = Circle(radius=1.5, color=cols[0], stroke_width=3).move_to(centers[0].tolist() + [0])
            self.play(Create(ring), run_time=0.8)
            self.play(FadeOut(ring), run_time=0.5)
        with self.say("b3") as d:
            self.play(Flash(dots[hub], color=RED, line_length=0.4), dots[hub].animate.set_opacity(0.1),
                      *[e.animate.set_stroke(RED, opacity=0.9) for e_, e in edges.items() if hub in e_], run_time=1.2)
            self.play(*[e.animate.set_stroke(opacity=0.0) for e_, e in edges.items() if hub in e_], run_time=0.8)
            rings = VGroup(*[Circle(radius=1.5, color=cols[m], stroke_width=3).move_to([*centers[m], 0]) for m in range(4)])
            self.play(LaggedStart(*[Create(r) for r in rings], lag_ratio=0.2), run_time=1.4)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ recap
    def recap(self):
        with self.say("r1") as d:
            head = T("三个要点", 40, INK, weight=BOLD).to_edge(UP, buff=0.7)
            self.play(Write(head), run_time=0.8)
        items = [
            ("r2", BLUE, "渗流阈值由 ⟨k²⟩/⟨k⟩ 决定"),
            ("r3", GOLD, "枢纽：抗随机故障，怕定向攻击"),
            ("r4", RED, "负荷转移 → 级联，冗余是关键"),
        ]
        rows = VGroup()
        for i, (k, c, s) in enumerate(items):
            num = Circle(radius=0.32, color=c, fill_opacity=0.18, stroke_width=3).add(T(str(i + 1), 28, c, weight=BOLD))
            row = VGroup(num, T(s, 32, INK)).arrange(RIGHT, buff=0.4)
            rows.add(row)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.6).next_to(head, DOWN, buff=0.8)
        for (k, _, _), row in zip(items, rows):
            with self.say(k) as d:
                self.play(FadeIn(row, shift=RIGHT * 0.3), run_time=0.8)
        self.wait(0.8)
        self.play(FadeOut(rows), FadeOut(head), run_time=0.6)
        with self.say("r5") as d:
            self.clip_on("attack_demo.mp4", "full", "本站交互演示：随机失效与蓄意攻击", start=0.3)
            if d < 10.4:
                self.wait(10.5 - d)
        self.clip_off()
        self.wait(1.0)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=1.0)
