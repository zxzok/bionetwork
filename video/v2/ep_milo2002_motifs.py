"""Paper explainer: Milo et al. 2002, network motifs."""
import random

import networkx as nx
import numpy as np

from common import *  # noqa: F401,F403
from paperkit import arrow, fit, counter

TITLE = "网络基序：复杂网络的简单构件"

LINES = {
    # hook
    "h1": "我们先来看一张网络。每个圆点是一个基因，每个箭头表示一个基因调控另一个基因。这是一张示意的基因调控网络。",
    "h2": "注意这三个点。甲调控乙，甲和乙又一起调控丙。这个小图案，叫前馈环。",
    "h3": "在这张网络里，前馈环一共出现了十九次。",
    "h4": "十九次是多是少，单看这个数字，判断不了。要和随便连起来的网络比一比，才知道。",
    "h5": "【慢】2002年，《科学》杂志上的一篇论文，把这种比较变成了一套通用的方法。这一期，我们就来讲这篇论文。",
    "q0": "这一期分三部分来讲。",
    "q1": "第一部分，怎样判断一个小图案出现得特别多。",
    "q2": "第二部分，不同领域的网络，各有哪些常见的小图案，它们可能起什么作用。",
    "q3": "第三部分，这个方法的局限。",
    # 13 triads
    "a1": "先看第一部分。我们从最小的单位开始，也就是三个节点。",
    "a1b": "只要三个点连成一片，带方向的连法一共只有十三种。屏幕上就是这十三种。",
    "a2": "你看，有的是一条链，有的是一个点指向两个点，有的是三个点首尾相接，绕成一个环。",
    "a3": "开头看到的前馈环，就是画了方框的这一种。",
    "a4": "方法的第一步，是把网络里每三个节点的组合都数一遍。每种连法下面的数字，就是它在这张网络里出现的次数。",
    # null model
    "n1": "但是，出现得多，不一定说明它特别。",
    "n1b": "这里要用到一个词：度。一个节点的度，就是它的连接数。度大的节点，比如左边这个连出六条边的点，自然会卷进很多小图案。",
    "n2": "所以，要和随机网络比。关键在于，随机网络要怎么造。",
    "n3": "论文的做法是交换连线。随机挑两条边，把它们的终点互换。你看，甲指向乙、丙指向丁，换成了甲指向丁、丙指向乙。",
    "n4": "【慢】这样换完，每个节点连进来几条边、连出去几条边，都和原来一样。变的，只是连接的对象。",
    "n4b": "也就是说，这种随机网络保留了每个节点的度，只打乱了谁连谁。用来对照的随机网络，叫作零模型。",
    "n5": "把开头那张网络这样交换很多次，再数一数前馈环。右上角的数字，明显少了。",
    # Z score
    "z1": "一次洗牌说明不了什么。我们洗三百次，每次都数一数前馈环。",
    "z1b": "这张直方图，横轴是一张随机网络里前馈环的个数，纵轴是有多少张随机网络得到了这个个数。",
    "z2": "白色虚线是随机网络的平均值，只有八次左右。",
    "z3": "黄色竖线是真实网络的十九次。你看，它落在了整个分布的最右边。",
    "z4": "【慢】把这个差距标准化，就得到Z分数。",
    "z4b": "分子是真实的计数，减去随机网络的平均计数。分母是随机计数的标准差，也就是随机结果通常会波动多少。",
    "z4c": "所以，Z分数说的是：真实计数比随机平均，多出了几个标准差。",
    "z5": "这里大约是三点五。富集明显、随机网络又很少能达到真实计数的小图案，就叫网络基序。",
    # domains
    "d1": "下面进入第二部分。论文把这套方法，用在了好几个领域的网络上。",
    "d2": "第一类是转录调控网络，也就是基因之间谁调控谁。画面里，是细菌中一组基因被开启和关闭的示意动画。",
    "d2b": "在大肠杆菌和酵母的转录调控网络里，前馈环和双扇形都显著富集。双扇形，就是两个调控者共同调控两个靶点。",
    "d3": "线虫的神经元网络，同样富集前馈环。一个由分子组成，一个由神经元组成，线路的风格却很接近。",
    "d4": "食物网就不一样了。这里富集的是捕食链和双平行结构，前馈环并不突出。",
    "d5": "电子电路里，也有和功能对应的基序，其中一部分和生物的信息处理网络相近。",
    "d6": "【慢】作者因此提出，基序也许能给网络分出类别，是理解网络的基本构件。",
    # function
    "f1": "结构上的富集，在功能上意味着什么，后来的理论和实验工作给出了一个漂亮的答案。画面里，是这篇论文的作者之一阿隆，在课堂上讲解前馈环。",
    "f2": "设想这样一种情形：丙要打开，必须甲和乙同时到位，而乙要等甲积累一段时间，才能升起来。",
    "f2b": "右边三条曲线，横轴是时间，纵轴分别是甲、乙、丙的水平。中间这条虚线，是乙起作用需要达到的水平。",
    "f3": "先看第一次输入。甲只闪了一下，乙还没升到虚线，甲就消失了。所以，丙一直没有打开。",
    "f4": "再看第二次输入。甲持续得足够久，乙越过了虚线，丙才打开。",
    "f4b": "【慢】也就是说，这个小线路像一个过滤器——滤掉短暂的噪声，只响应持续的信号。",
    "f5": "要强调的是，这个功能来自后续研究，并不是这篇论文本身的结论。",
    "f5b": "本站有这个过滤作用的交互演示。先把输入脉冲调短，输出几乎不动；再把脉冲拉长，输出就升起来了。",
    "f6": "对生物医学来说，基序让我们能从局部线路的角度，去读转录调控网络和神经连接图谱。",
    # limits
    "l1": "最后是第三部分，局限。第一点，基序是否显著，永远是相对于某个零模型而言的。",
    "l1b": "你看公式里，随机平均和标准差，都来自零模型。换一个零模型，这两个数就会变。",
    "l2": "举个例子。在有空间位置的网络里，离得近的节点更容易相连。上面这条网络，每个点只和附近的点相连。这种局部聚集，本身就会制造很多前馈环。",
    "l3": "如果零模型只保持度，交换时就会拉出红色这样的远距离连线，空间结构被打乱了。这时，Z分数高达八十多。",
    "l4": "换成只在近处交换连线的零模型，Z分数降到十几。同一个计数，结论的强弱差了好几倍。",
    "l5": "第二点，结构上富集，不等于有某种功能。第三点，调控网络和神经连接图谱都不完整，缺失的边会改变计数。",
    # recap
    "r1": "好，我们来总结一下。",
    "r2": "第一，基序是比随机网络出现得显著更多的小图案；比较时，随机网络要保持每个节点的度。",
    "r3": "第二，调控网络和神经元网络都富集前馈环，食物网的基序则不同。",
    "r4": "第三，显著性取决于零模型，结构上的富集也不等于功能。",
}

# 13 connected triad classes (triadic census codes) on nodes 0 (top), 1 (left), 2 (right)
TRIADS = [
    ("021C", [(1, 0), (0, 2)]), ("021D", [(0, 1), (0, 2)]), ("021U", [(1, 0), (2, 0)]),
    ("111D", [(0, 1), (1, 0), (2, 0)]), ("111U", [(0, 1), (1, 0), (0, 2)]),
    ("030T", [(0, 1), (0, 2), (1, 2)]), ("030C", [(0, 1), (1, 2), (2, 0)]),
    ("201", [(0, 1), (1, 0), (0, 2), (2, 0)]), ("120D", [(0, 1), (0, 2), (1, 2), (2, 1)]),
    ("120U", [(1, 0), (2, 0), (1, 2), (2, 1)]), ("120C", [(1, 0), (0, 2), (1, 2), (2, 1)]),
    ("210", [(0, 1), (1, 0), (0, 2), (1, 2), (2, 1)]), ("300", [(0, 1), (1, 0), (0, 2), (2, 0), (1, 2), (2, 1)]),
]

ZF = r"Z=\frac{N_{\mathrm{real}}-\langle N_{\mathrm{rand}}\rangle}{\sigma_{\mathrm{rand}}}"


def frac_parts(f):
    """Numerator and denominator glyphs of a single fraction in MathTex f (split at the fraction bar)."""
    gl = list(f[0])
    bar = max(gl[2:], key=lambda g: g.width - 3 * g.height)
    y = bar.get_center()[1]
    num = sorted([g for g in gl[2:] if g is not bar and g.get_center()[1] > y], key=lambda g: g.get_center()[0])
    den = [g for g in gl[2:] if g is not bar and g.get_center()[1] < y]
    return VGroup(*num), VGroup(*den)


def glyph(edges, s=0.5, col=INK, ecol=MUTED, pts=None, r=0.08):
    """Small motif drawing; mutual pairs are drawn as two offset arrows."""
    pts = pts or [UP * s * 0.8, DL * s * 0.7 + LEFT * s * 0.25, DR * s * 0.7 + RIGHT * s * 0.25]
    g = VGroup()
    es = set(edges)
    for u, v in edges:
        a, b = np.array(pts[u], float), np.array(pts[v], float)
        off = np.zeros(3)
        if (v, u) in es:
            d = (b - a) / np.linalg.norm(b - a)
            off = np.array([-d[1], d[0], 0]) * 0.06
        g.add(arrow(a + off, b + off, r + 0.02, ecol, 2.5, tip=0.12))
    g.add(*[Dot(p, radius=r, color=col) for p in pts])
    return g


def ffls(G):
    out = []
    for x, y in G.edges():
        for z in set(G.successors(x)) & set(G.successors(y)):
            if z in (x, y):
                continue
            if G.has_edge(y, x) or G.has_edge(z, x) or G.has_edge(z, y):
                continue
            out.append((x, y, z))
    return out


def swap(G, n, rng, ok=None):
    H = G.copy(); E = list(H.edges()); t = done = 0
    while done < n and t < n * 20:
        t += 1
        i, j = rng.sample(range(len(E)), 2); (a, b), (c, d) = E[i], E[j]
        if len({a, b, c, d}) < 4 or H.has_edge(a, d) or H.has_edge(c, b):
            continue
        if ok and not (ok(a, d) and ok(c, b)):
            continue
        H.remove_edge(a, b); H.remove_edge(c, d); H.add_edge(a, d); H.add_edge(c, b)
        E[i], E[j] = (a, d), (c, b); done += 1
    return H


def hooknet(seed=2):
    rng = random.Random(seed); G = nx.DiGraph(); n = 36; G.add_nodes_from(range(n))
    for _ in range(12):
        x, y, z = rng.sample(range(n), 3); G.add_edges_from([(x, y), (x, z), (y, z)])
    while G.number_of_edges() < 70:
        a, b = rng.sample(range(n), 2)
        if not G.has_edge(b, a):
            G.add_edge(a, b)
    G.remove_nodes_from([v for v in list(G) if G.degree(v) == 0])
    return G


class Episode(Narrated):
    LINES = LINES

    def construct(self):
        self.G = hooknet()
        self.hook()
        self.parts()
        self.triads()
        self.null()
        self.zscore()
        self.domains()
        self.function()
        self.limits()
        self.recap()

    def draw(self, G, box=(-6.3, 6.3, -3.4, 3.2)):
        pos = fit(nx.kamada_kawai_layout(G.to_undirected()), box)
        dots = {v: Dot(pos[v], radius=0.09, color=BLUE) for v in G}
        arr = {e: arrow(pos[e[0]], pos[e[1]], 0.12, MUTED, 2.2, op=0.75, tip=0.13) for e in G.edges()}
        return pos, dots, arr

    # ------------------------------------------------------------------ hook
    def hook(self):
        G = self.G
        pos, dots, arr = self.draw(G)
        self.pos = pos
        with self.say("h1") as d:
            self.play(LaggedStart(*[GrowFromCenter(x) for x in dots.values()], lag_ratio=0.02), run_time=d * 0.35)
            self.play(LaggedStart(*[GrowArrow(a) for a in arr.values()], lag_ratio=0.01), run_time=d * 0.45)
        F = ffls(G)
        assert len(F) == nx.triadic_census(G)["030T"] == 19, len(F)
        x, y, z = F[0]
        tri = [(x, y), (x, z), (y, z)]
        with self.say("h2") as d:
            self.play(*[arr[e].animate.set_color(GOLD).set_opacity(1) for e in tri],
                      *[dots[v].animate.set_color(GOLD).scale(1.6) for v in (x, y, z)], run_time=1.0)
            labs = VGroup(*[T(s, 24, GOLD).next_to(dots[v], UR, buff=0.04) for s, v in zip("甲乙丙", (x, y, z))])
            self.play(FadeIn(labs), run_time=0.6)
            self.wait(d * 0.4)
            self.play(FadeOut(labs), *[arr[e].animate.set_color(MUTED).set_opacity(0.75) for e in tri],
                      *[dots[v].animate.set_color(BLUE).scale(1 / 1.6) for v in (x, y, z)], run_time=0.6)
        lab = counter("前馈环", "0", GOLD).to_corner(UR, buff=0.4)
        bgbox = BackgroundRectangle(lab, color=BG, fill_opacity=0.85, buff=0.15)
        with self.say("h3") as d:
            self.play(FadeIn(bgbox), FadeIn(lab), run_time=0.4)
            step = (d - 0.6) / len(F)
            for i, (a, b, c) in enumerate(F):
                es = [(a, b), (a, c), (b, c)]
                self.play(*[arr[e].animate.set_color(GOLD).set_opacity(1) for e in es],
                          Transform(lab[1], T(str(i + 1), 40, GOLD, weight=BOLD).move_to(lab[1])), run_time=max(0.12, step))
        with self.say("h4") as d:
            q = T("要和随机网络比", 54, GOLD, weight=BOLD)
            self.play(*[a.animate.set_opacity(0.15) for a in arr.values()], *[x.animate.set_opacity(0.15) for x in dots.values()], run_time=0.8)
            self.play(Write(q), run_time=1.0)
        with self.say("h5") as d:
            self.play(FadeOut(q), run_time=0.6)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    def parts(self):
        head, items = slide("这一期分三部分", ["一  怎样判断小图案出现得特别多", "二  不同网络的常见小图案与功能", "三  方法的局限"])
        with self.say("q0") as d:
            self.play(FadeIn(head, shift=RIGHT * 0.3), run_time=0.6)
        for k, it in zip(("q1", "q2", "q3"), items):
            with self.say(k) as d:
                self.play(FadeIn(it, shift=RIGHT * 0.3), run_time=0.6)
        self.wait(0.6)
        self.play(FadeOut(head), FadeOut(items), run_time=0.6)

    # ------------------------------------------------------------------ 13 triads
    def triads(self):
        tag = self.chapter("一 · 十三种三节点构型")
        cen = nx.triadic_census(self.G)
        cells = VGroup(*[glyph(es, 0.5) for _, es in TRIADS])
        top = VGroup(*cells[:7]).arrange(RIGHT, buff=0.75)
        bot = VGroup(*cells[7:]).arrange(RIGHT, buff=0.75)
        VGroup(top, bot).arrange(DOWN, buff=1.3).move_to(UP * 0.4)
        three = VGroup(*[Dot(p, radius=0.14, color=BLUE) for p in (UP * 0.8, DL * 0.7 + LEFT * 0.3, DR * 0.7 + RIGHT * 0.3)])
        with self.say("a1") as d:
            self.play(FadeIn(tag), LaggedStart(*[GrowFromCenter(x) for x in three], lag_ratio=0.3), run_time=1.2)
        with self.say("a1b") as d:
            self.play(FadeOut(three), LaggedStart(*[FadeIn(c, scale=0.6) for c in cells], lag_ratio=0.12), run_time=d * 0.6)
        with self.say("a2") as d:
            for i in (0, 1, 6):
                self.play(Indicate(cells[i], color=BLUE, scale_factor=1.3), run_time=d * 0.22)
        ffl = cells[5]
        with self.say("a3") as d:
            box = SurroundingRectangle(ffl, color=GOLD, buff=0.15)
            self.play(Create(box), ffl.animate.set_color(GOLD), run_time=1.0)
        with self.say("a4") as d:
            nums = VGroup()
            for c, (code, _) in zip(cells, TRIADS):
                nums.add(T(str(cen[code]), 30, GOLD if code == "030T" else INK, weight=BOLD).next_to(c, DOWN, buff=0.3))
            self.play(LaggedStart(*[FadeIn(n, shift=UP * 0.2) for n in nums], lag_ratio=0.1), run_time=d * 0.6)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ null model
    def null(self):
        tag = self.chapter("一 · 保持度不变的洗牌")
        hubpos = LEFT * 3.0
        leaves = [hubpos + 1.8 * np.array([np.cos(t), np.sin(t), 0]) for t in np.linspace(-0.9, 0.9, 6)]
        hub = Dot(hubpos, radius=0.16, color=BLUE)
        ls = VGroup(*[Dot(p, radius=0.1, color=BLUE) for p in leaves])
        ars = VGroup(*[arrow(hubpos, p, 0.18, MUTED, 3) for p in leaves])
        pairs = VGroup(*[arrow(leaves[i], leaves[i + 1], 0.13, GOLD, 2.5) for i in range(5)])
        with self.say("n1") as d:
            self.play(FadeIn(tag), FadeIn(hub), FadeIn(ls), LaggedStart(*[GrowArrow(a) for a in ars], lag_ratio=0.1), run_time=1.5)
        with self.say("n1b") as d:
            dl = T("度 = 6", 30, BLUE).next_to(hub, LEFT, buff=0.3)
            self.play(FadeIn(dl), Indicate(hub, color=BLUE), run_time=1.0)
            self.wait(d * 0.25)
            self.play(LaggedStart(*[GrowArrow(a) for a in pairs], lag_ratio=0.2), run_time=d * 0.35)
        with self.say("n2") as d:
            self.play(FadeOut(VGroup(hub, ls, ars, pairs, dl)), run_time=0.8)
        P = {"甲": LEFT * 2.2 + UP * 1.2, "乙": RIGHT * 2.2 + UP * 1.2, "丙": LEFT * 2.2 + DOWN * 1.4, "丁": RIGHT * 2.2 + DOWN * 1.4}
        nd = {k: VGroup(Circle(radius=0.32, color=BLUE, fill_color=BG, fill_opacity=1), T(k, 26)).move_to(p) for k, p in P.items()}
        e1 = arrow(P["甲"], P["乙"], 0.35, INK, 4); e2 = arrow(P["丙"], P["丁"], 0.35, INK, 4)
        tags = {k: T(s, 22, GREEN).next_to(nd[k], LEFT if k in "甲丙" else RIGHT, buff=0.2)
                for k, s in (("甲", "出 1"), ("丙", "出 1"), ("乙", "入 1"), ("丁", "入 1"))}
        with self.say("n3") as d:
            self.play(*[FadeIn(x) for x in nd.values()], GrowArrow(e1), GrowArrow(e2), run_time=1.0)
            self.play(e1.animate.set_color(GOLD), e2.animate.set_color(GOLD), run_time=0.6)
            self.wait(d * 0.3)
            f1 = arrow(P["甲"], P["丁"], 0.35, GOLD, 4); f2 = arrow(P["丙"], P["乙"], 0.35, GOLD, 4)
            self.play(Transform(e1, f1), Transform(e2, f2), run_time=d * 0.25)
        with self.say("n4") as d:
            self.play(*[FadeIn(t) for t in tags.values()], run_time=0.8)
            self.play(*[Indicate(t, color=GREEN) for t in tags.values()], run_time=1.2)
        with self.say("n4b") as d:
            zm = T("零模型 = 保留度、打乱连接的随机网络", 30, GOLD).to_edge(DOWN, buff=0.6)
            self.play(FadeIn(zm, shift=UP * 0.2), run_time=0.8)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.6)
        G = self.G
        H = swap(G, 300, random.Random(5))
        pos = self.pos
        arr = {e: arrow(pos[e[0]], pos[e[1]], 0.12, MUTED, 2.2, op=0.75, tip=0.13) for e in G.edges()}
        dots = VGroup(*[Dot(pos[v], radius=0.09, color=BLUE) for v in G])
        allg = VGroup(VGroup(*arr.values()), dots).scale(0.9).shift(DOWN * 0.2)
        idx = {v: i for i, v in enumerate(G)}
        newarr = {e: arrow(dots[idx[e[0]]].get_center(), dots[idx[e[1]]].get_center(), 0.11, MUTED, 2.0, op=0.75, tip=0.12)
                  for e in H.edges()}
        with self.say("n5") as d:
            self.play(FadeIn(allg), run_time=0.8)
            gone = [arr[e] for e in G.edges() if not H.has_edge(*e)]
            new = [newarr[e] for e in H.edges() if not G.has_edge(*e)]
            self.play(*[a.animate.set_color(RED) for a in gone], run_time=0.6)
            self.play(*[FadeOut(a) for a in gone], *[GrowArrow(a) for a in new], run_time=1.4)
            for e in list(newarr):
                if G.has_edge(*e):
                    newarr[e] = arr[e]
            F = ffls(H)
            for (a, b, c) in F:
                for e in [(a, b), (a, c), (b, c)]:
                    newarr[e].set_color(GOLD).set_opacity(1)
            lab = counter("前馈环", str(len(F)), GOLD).to_corner(UR, buff=0.4)
            self.play(FadeIn(lab), *[Indicate(newarr[e], color=GOLD) for (a, b, c) in F for e in [(a, b), (a, c), (b, c)]], run_time=1.4)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ Z score
    def zscore(self):
        tag = self.chapter("一 · 多出来多少：Z 分数")
        G = self.G
        rng = random.Random(1)
        r = np.array([len(ffls(swap(G, 300, rng))) for _ in range(300)])
        real = len(ffls(G))
        mu, sd = r.mean(), r.std()
        Z = (real - mu) / sd
        assert 7.5 <= mu < 8.5 and abs(Z - 3.5) < 0.15, (mu, Z)
        cnt = np.bincount(r, minlength=24)
        ymax = int(np.ceil(cnt.max() / 10) * 10)
        ax = Axes(x_range=[0, 24, 4], y_range=[0, ymax, ymax // 2], x_length=9.5, y_length=3.7,
                  axis_config={"color": MUTED, "include_tip": False, "font_size": 24},
                  x_axis_config={"numbers_to_include": list(range(0, 25, 4))},
                  y_axis_config={"numbers_to_include": [0, ymax // 2, ymax]}).shift(DOWN * 1.0)
        xl = T("一张随机网络里前馈环的个数", 24, MUTED).next_to(ax.x_axis, DOWN, buff=0.45)
        yl = T("网络数", 24, MUTED).rotate(PI / 2).next_to(ax.y_axis, LEFT, buff=0.3)
        bars = VGroup()
        for k in range(len(cnt)):
            if cnt[k] == 0:
                continue
            h = ax.c2p(0, cnt[k])[1] - ax.c2p(0, 0)[1]
            bars.add(Rectangle(width=ax.c2p(1, 0)[0] - ax.c2p(0, 0)[0] - 0.04, height=h, fill_color=BLUE, fill_opacity=0.8,
                               stroke_width=0).move_to(ax.c2p(k, 0), aligned_edge=DOWN))
        with self.say("z1") as d:
            self.play(FadeIn(tag), run_time=0.6)
            sh = VGroup(*[glyph([(0, 1), (0, 2), (1, 2)], 0.3, col=BLUE) for _ in range(8)]).arrange(RIGHT, buff=0.5).move_to(UP * 0.5)
            self.play(LaggedStart(*[FadeIn(s, shift=DOWN * 0.3) for s in sh], lag_ratio=0.15), run_time=d * 0.5)
            self.play(FadeOut(sh), run_time=0.5)
        with self.say("z1b") as d:
            self.play(Create(ax), FadeIn(xl), FadeIn(yl), run_time=1.2)
            self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.08), run_time=d * 0.5)
        with self.say("z2") as d:
            ml = DashedLine(ax.c2p(mu, 0), ax.c2p(mu, ymax), color=INK)
            mt = T(f"平均 {mu:.1f}", 24, INK).next_to(ml, UP, buff=0.1)
            self.play(Create(ml), FadeIn(mt), run_time=1.0)
        with self.say("z3") as d:
            rl = Line(ax.c2p(real, 0), ax.c2p(real, ymax), color=GOLD, stroke_width=5)
            rt = T(f"真实网络 {real}", 26, GOLD, weight=BOLD).next_to(rl, UP, buff=0.1)
            self.play(Create(rl), FadeIn(rt), run_time=1.2)
            self.play(Indicate(rt, color=GOLD), run_time=1.0)
        f = MathTex(ZF, font_size=50, color=INK).move_to([0.6, 2.6, 0])
        with self.say("z4") as d:
            self.play(Write(f), run_time=d * 0.6)
        with self.say("z4b") as d:
            num, den = frac_parts(f)
            b1 = SurroundingRectangle(num, color=GOLD, buff=0.06); b2 = SurroundingRectangle(den, color=BLUE, buff=0.06)
            l1 = T("真实 − 随机平均", 22, GOLD).next_to(b1, RIGHT, buff=0.25)
            l2 = T("随机的波动幅度", 22, BLUE).next_to(b2, RIGHT, buff=0.25)
            self.play(Create(b1), FadeIn(l1), run_time=0.8)
            self.wait(d * 0.3)
            self.play(Create(b2), FadeIn(l2), run_time=0.8)
        with self.say("z4c") as d:
            self.play(FadeOut(VGroup(b1, b2, l1, l2)), run_time=0.5)
            mean = T("多出几个标准差", 28, GOLD).next_to(f, RIGHT, buff=0.4)
            self.play(FadeIn(mean, shift=LEFT * 0.2), run_time=0.8)
        with self.say("z5") as d:
            zt = MathTex(rf"Z \approx {Z:.1f}", font_size=48, color=GOLD).move_to(mean)
            self.play(FadeOut(mean), Write(zt), run_time=1.0)
            mot = T("网络基序", 34, GOLD, weight=BOLD).next_to(zt, DOWN, buff=0.25)
            self.play(FadeIn(mot, shift=UP * 0.2), run_time=0.8)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ domains
    def domains(self):
        tag = self.chapter("二 · 每类网络都有自己的积木")
        sq = [UL * 0.45, UR * 0.45, DL * 0.45, DR * 0.45]
        bifan = glyph([(0, 2), (0, 3), (1, 2), (1, 3)], pts=[sq[0] + UP * 0.1, sq[1] + UP * 0.1, sq[2] + DOWN * 0.1, sq[3] + DOWN * 0.1])
        ffl = lambda: glyph([(0, 1), (0, 2), (1, 2)], 0.55)
        chain = glyph([(0, 1), (1, 2)], pts=[UP * 0.7, ORIGIN, DOWN * 0.7])
        bipar = glyph([(0, 1), (0, 2), (1, 3), (2, 3)], pts=[UP * 0.7, LEFT * 0.5, RIGHT * 0.5, DOWN * 0.7])
        cols = [("基因调控", GREEN), ("神经元", VIOLET), ("食物网", GOLD), ("电子电路", BLUE)]
        xs = [-4.8, -1.6, 1.6, 4.8]
        heads = VGroup(*[T(s, 30, c, weight=BOLD).move_to([x, 2.6, 0]) for (s, c), x in zip(cols, xs)])
        with self.say("d1") as d:
            self.play(FadeIn(tag), LaggedStart(*[FadeIn(h, shift=DOWN * 0.2) for h in heads], lag_ratio=0.2), run_time=d * 0.6)
        with self.say("d2") as d:
            self.play(FadeOut(heads), FadeOut(tag), run_time=0.5)
            self.clip_on("yt_lac_operon_ndsu.mp4", "center", "视频：NDSU Virtual Cell Animations · YouTube", start=40)
        self.clip_off()
        g1 = ffl().move_to([xs[0], 1.0, 0]); g2 = bifan.move_to([xs[0], -1.2, 0])
        n1 = T("前馈环", 22, MUTED).next_to(g1, DOWN, buff=0.15); n2 = T("双扇形", 22, MUTED).next_to(g2, DOWN, buff=0.15)
        with self.say("d2b") as d:
            self.play(FadeIn(tag), FadeIn(heads), run_time=0.6)
            self.play(FadeIn(g1), FadeIn(n1), run_time=0.8)
            self.wait(d * 0.25)
            self.play(FadeIn(g2), FadeIn(n2), run_time=0.8)
            self.play(Indicate(g2, color=GREEN), run_time=1.0)
        g3 = ffl().move_to([xs[1], 1.0, 0]); n3 = T("前馈环", 22, MUTED).next_to(g3, DOWN, buff=0.15)
        with self.say("d3") as d:
            self.play(TransformFromCopy(g1, g3), FadeIn(n3), run_time=1.2)
            link = DoubleArrow(g1.get_right() + RIGHT * 0.1, g3.get_left() + LEFT * 0.1, color=GOLD, buff=0, tip_length=0.15)
            self.play(GrowFromCenter(link), run_time=0.8)
        g4 = chain.move_to([xs[2], 1.0, 0]); g5 = bipar.move_to([xs[2], -1.2, 0])
        n4 = T("捕食链", 22, MUTED).next_to(g4, DOWN, buff=0.15); n5 = T("双平行", 22, MUTED).next_to(g5, DOWN, buff=0.15)
        with self.say("d4") as d:
            self.play(FadeIn(g4), FadeIn(n4), run_time=0.8)
            self.play(FadeIn(g5), FadeIn(n5), run_time=0.8)
            nf = ffl().set_opacity(0.3).move_to([xs[2], -3.05, 0]).scale(0.6)
            cr = Cross(nf, stroke_color=RED, stroke_width=4)
            self.play(FadeIn(nf), Create(cr), run_time=0.8)
        chip = VGroup(RoundedRectangle(width=1.4, height=1.0, corner_radius=0.1, color=BLUE),
                      *[Line([-0.9, y, 0], [-0.7, y, 0], color=BLUE) for y in (-0.3, 0, 0.3)],
                      *[Line([0.7, y, 0], [0.9, y, 0], color=BLUE) for y in (-0.3, 0, 0.3)]).move_to([xs[3], 1.0, 0])
        part = T("部分与左侧相近", 22, MUTED).next_to(chip, DOWN, buff=0.3)
        with self.say("d5") as d:
            self.play(Create(chip), run_time=1.0)
            self.play(FadeIn(part), run_time=0.6)
        with self.say("d6") as d:
            b1 = SurroundingRectangle(VGroup(heads[0], heads[1], g2, n2, g3), color=GREEN, buff=0.25)
            b2 = SurroundingRectangle(VGroup(heads[2], g5, n5), color=GOLD, buff=0.25)
            self.play(Create(b1), run_time=0.9)
            self.play(Create(b2), run_time=0.9)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ FFL as filter
    def function(self):
        with self.say("f1") as d:
            self.clip_on("yt_alon_ffl_lecture.mp4", "center", "视频：Alon Lab · YouTube", start=300)
        self.clip_off()
        tag = self.chapter("二 · 前馈环过滤短暂信号")
        pts = [UP * 1.3, DOWN * 0.1 + LEFT * 1.0, DOWN * 1.5 + RIGHT * 0.2]
        P = [np.array(p) + LEFT * 5.0 for p in pts]
        cols = [BLUE, VIOLET, GOLD]
        nodes = VGroup(*[VGroup(Circle(radius=0.36, color=c, fill_color=BG, fill_opacity=1, stroke_width=4), T(s, 28, c)).move_to(p)
                         for p, c, s in zip(P, cols, "甲乙丙")])
        ars = VGroup(arrow(P[0], P[1], 0.4, INK, 4), arrow(P[0], P[2], 0.4, INK, 4), arrow(P[1], P[2], 0.4, INK, 4))
        andl = T("且", 26, GOLD, weight=BOLD).move_to(P[2] + RIGHT * 0.75 + UP * 0.35)
        dt = 0.01
        ts = np.arange(0, 12, dt)
        X = ((ts > 1) & (ts < 1.7)) | ((ts > 5) & (ts < 9.5))
        Y = np.zeros_like(ts); Zs = np.zeros_like(ts)
        for i in range(1, len(ts)):
            Y[i] = Y[i - 1] + dt * (X[i - 1] - Y[i - 1]) / 1.0
            on = X[i - 1] and Y[i - 1] > 0.6
            Zs[i] = Zs[i - 1] + dt * (on - Zs[i - 1]) / 0.6
        axs, curves = VGroup(), []
        for k, (arr_, c, s) in enumerate(((X.astype(float), BLUE, "甲"), (Y, VIOLET, "乙"), (Zs, GOLD, "丙"))):
            ax = Axes(x_range=[0, 12, 2], y_range=[0, 1.1, 1], x_length=8.2, y_length=1.5,
                      axis_config={"color": MUTED, "include_tip": False, "stroke_width": 2}).move_to([1.9, 2.0 - 2.15 * k, 0])
            lab = T(s, 28, c, weight=BOLD).next_to(ax, LEFT, buff=0.25)
            axs.add(VGroup(ax, lab))
            curves.append((ax, arr_, c))
        tl = T("时间 →", 22, MUTED).next_to(curves[2][0], DOWN, buff=0.1).align_to(curves[2][0], RIGHT)
        thr = DashedLine(curves[1][0].c2p(0, 0.6), curves[1][0].c2p(12, 0.6), color=MUTED, stroke_width=2)

        def trace(i0, i1):
            out = []
            for ax, arr_, c in curves:
                idx = np.arange(i0, i1, 5)
                out.append(ax.plot_line_graph(ts[idx], arr_[idx], line_color=c, add_vertex_dots=False, stroke_width=4))
            return out
        cut = int(3.5 / dt)
        with self.say("f2") as d:
            self.play(FadeIn(tag), FadeIn(nodes), LaggedStart(*[GrowArrow(a) for a in ars], lag_ratio=0.2), run_time=1.5)
            self.play(FadeIn(andl), Indicate(nodes[2], color=GOLD), run_time=1.0)
        with self.say("f2b") as d:
            self.play(FadeIn(axs), FadeIn(tl), run_time=1.0)
            self.play(Create(thr), run_time=0.8)
        with self.say("f3") as d:
            tr = trace(0, cut)
            self.play(*[Create(t) for t in tr], run_time=d * 0.75, rate_func=linear)
        with self.say("f4") as d:
            tr2 = trace(cut - 5, len(ts))
            self.play(*[Create(t) for t in tr2], run_time=d * 0.8, rate_func=linear)
        with self.say("f4b") as d:
            self.play(nodes[2][0].animate.set_fill(GOLD, opacity=0.6), run_time=0.8)
        with self.say("f5") as d:
            note = T("后续研究的发现", 26, MUTED).to_edge(DOWN, buff=0.25).shift(LEFT * 4.6)
            self.play(FadeIn(note), run_time=0.8)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.6)
        with self.say("f5b") as d:
            self.clip_on("ffl_pulse_demo.mp4", "full", "本站交互演示：前馈环的滤波作用", start=0.3)
        self.clip_off()
        with self.say("f6") as d:
            self.add(tag)
            tiles = VGroup(*[glyph([(0, 1), (0, 2), (1, 2)], 0.35, col=GREEN) for _ in range(12)]).arrange_in_grid(3, 4, buff=0.9)
            self.play(LaggedStart(*[FadeIn(t, scale=0.5) for t in tiles], lag_ratio=0.08), run_time=d * 0.5)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ limits
    def limits(self):
        tag = self.chapter("三 · 显著是相对的")
        rs = np.random.default_rng(3); n = 150; x = np.sort(rs.uniform(0, 30, n))
        S = nx.DiGraph(); S.add_nodes_from(range(n))
        for i in range(n):
            for j in range(i + 1, n):
                if abs(x[i] - x[j]) < 0.9 and rs.random() < 0.8:
                    S.add_edge(i, j) if rs.random() < 0.5 else S.add_edge(j, i)
        real = len(ffls(S))
        rng = random.Random(1)
        r1 = np.array([len(ffls(swap(S, 1500, rng))) for _ in range(100)])
        r2 = np.array([len(ffls(swap(S, 1500, rng, ok=lambda a, b: abs(x[a] - x[b]) < 0.9))) for _ in range(100)])
        z1 = (real - r1.mean()) / r1.std(); z2 = (real - r2.mean()) / r2.std()
        assert 80 <= z1 < 90 and 10 <= z2 < 20, (z1, z2)
        m = 30
        xs = np.linspace(-6.0, 6.0, m)
        ys = np.random.default_rng(2).uniform(-0.5, 0.5, m)
        P = [np.array([a, b + 0.9, 0]) for a, b in zip(xs, ys)]
        dots = VGroup(*[Dot(p, radius=0.08, color=BLUE) for p in P])
        loc = [(i, j) for i in range(m) for j in range(i + 1, min(m, i + 3)) if (i * 7 + j) % 5 != 0]
        loc = [(i, j) if (i + j) % 3 else (j, i) for i, j in loc]
        la = VGroup(*[arrow(P[a], P[b], 0.1, MUTED, 2, tip=0.1) for a, b in loc])
        f = MathTex(ZF, font_size=50)
        with self.say("l1") as d:
            self.play(FadeIn(tag), Write(f), run_time=1.2)
        with self.say("l1b") as d:
            num, den = frac_parts(f)
            b1 = SurroundingRectangle(num[-7:], color=GOLD); b2 = SurroundingRectangle(den, color=GOLD)
            lz = T("都来自零模型", 26, GOLD).next_to(f, RIGHT, buff=0.4)
            self.play(Create(b1), Create(b2), FadeIn(lz), run_time=1.0)
            self.wait(d * 0.4)
            self.play(FadeOut(VGroup(f, b1, b2, lz)), run_time=0.6)
        with self.say("l2") as d:
            self.play(FadeIn(dots), LaggedStart(*[GrowArrow(a) for a in la], lag_ratio=0.03), run_time=d * 0.6)
        rr = random.Random(4)
        far = []
        for _ in range(10):
            a, b = rr.sample(range(m), 2)
            if abs(a - b) > 6:
                far.append(arrow(P[a], P[b], 0.1, RED, 2, tip=0.1))
        farg = VGroup(*far)
        c1 = VGroup(T("只保持度", 28, RED), MathTex(rf"Z\approx {z1:.0f}", font_size=44, color=RED)).arrange(DOWN, buff=0.2).move_to([-3.2, -2.1, 0])
        c2 = VGroup(T("再保持空间邻近", 28, GREEN), MathTex(rf"Z\approx {z2:.0f}", font_size=44, color=GREEN)).arrange(DOWN, buff=0.2).move_to([3.2, -2.1, 0])
        with self.say("l3") as d:
            self.play(LaggedStart(*[GrowArrow(a) for a in far], lag_ratio=0.1), la.animate.set_opacity(0.3), run_time=1.6)
            self.play(FadeIn(c1, shift=UP * 0.2), run_time=0.8)
        with self.say("l4") as d:
            self.play(FadeOut(farg), la.animate.set_opacity(1), run_time=1.0)
            self.play(FadeIn(c2, shift=UP * 0.2), run_time=0.8)
        with self.say("l5") as d:
            miss = [la[i] for i in range(0, len(la), 4)]
            self.play(FadeOut(VGroup(c1, c2)), run_time=0.5)
            fx = T("结构富集 ≠ 功能", 30, GOLD).move_to(DOWN * 1.6)
            self.play(FadeIn(fx), run_time=0.6)
            self.wait(d * 0.25)
            self.play(*[a.animate.set_color(RED).set_opacity(0.25) for a in miss], run_time=1.0)
            self.play(*[FadeOut(a) for a in miss], run_time=0.8)
        self.play(*[FadeOut(m_) for m_ in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ recap
    def recap(self):
        with self.say("r1") as d:
            head = T("三个要点", 40, INK, weight=BOLD).to_edge(UP, buff=0.7)
            self.play(Write(head), run_time=0.8)
        items = [("r2", BLUE, "基序 = 相对保度随机网络的显著富集"),
                 ("r3", GOLD, "调控与神经元共享前馈环，食物网不同"),
                 ("r4", RED, "显著性依赖零模型；富集 ≠ 功能")]
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
