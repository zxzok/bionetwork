"""Animated explainer: 度相关性 (edge sampling, k_nn, assortativity r, structural cutoff, rich club, k-core, dynamics)."""
import random

import networkx as nx
import numpy as np

from common import *  # noqa: F401,F403
from ahelp import NetView, counter, fit, log_axes, nv_edge, recap_rows, parts_slide

TITLE = "度相关性：枢纽和谁相连"


def xbs(G, assort, iters, seed, keep_connected=False):
    """Xulvi-Brunet–Sokolov degree-preserving rewiring towards (dis)assortative mixing."""
    G = G.copy(); rng = random.Random(seed); E = list(G.edges()); deg = dict(G.degree())
    for _ in range(iters):
        i, j = rng.sample(range(len(E)), 2)
        (a, b), (c, d) = E[i], E[j]
        ns = [a, b, c, d]
        if len(set(ns)) < 4:
            continue
        ns.sort(key=lambda x: deg[x])
        p, q = ((ns[3], ns[2]), (ns[1], ns[0])) if assort else ((ns[3], ns[0]), (ns[2], ns[1]))
        if G.has_edge(*p) or G.has_edge(*q):
            continue
        G.remove_edge(a, b); G.remove_edge(c, d); G.add_edge(*p); G.add_edge(*q)
        if keep_connected and not nx.is_connected(G):
            G.remove_edge(*p); G.remove_edge(*q); G.add_edge(a, b); G.add_edge(c, d)
            continue
        E[i], E[j] = p, q
    return G


# small pair (hook + dynamics)
B0 = nx.barabasi_albert_graph(60, 2, seed=3)
GA = xbs(B0, True, 400, 1, keep_connected=True)
GD = xbs(B0, False, 400, 1, keep_connected=True)
assert sorted(d for _, d in GA.degree()) == sorted(d for _, d in GD.degree())
HUBS = sorted(B0, key=B0.degree, reverse=True)[:4]


def giant_frac(G, removed):
    H = G.copy(); H.remove_nodes_from(removed)
    return len(max(nx.connected_components(H), key=len)) / G.number_of_nodes()


FA, FD = giant_frac(GA, HUBS), giant_frac(GD, HUBS)
assert 0.9 < FA < 1.0 and 0.7 < FD < 0.8, (FA, FD)
assert round(nx.degree_assortativity_coefficient(GD), 2) == -0.65
# friendship paradox
GF = nx.barabasi_albert_graph(2000, 2, seed=1)
KF = np.array([d for _, d in GF.degree()])
KMEAN, KNN = KF.mean(), (KF ** 2).mean() / KF.mean()
assert 3.9 < KMEAN < 4.1 and 11.0 < KNN < 12.0
# structural disassortativity
_rng = np.random.default_rng(5)
_k = np.minimum(np.floor((1 - _rng.random(5000)) ** (-1 / 1.2)).astype(int), 4999)
if _k.sum() % 2:
    _k[0] += 1
_M = nx.configuration_model(_k, seed=5)
_dm = dict(_M.degree())
_x = [d for u, v, _ in _M.edges(keys=True) for d in (_dm[u], _dm[v])]
_y = [d for u, v, _ in _M.edges(keys=True) for d in (_dm[v], _dm[u])]
R_MULTI = float(np.corrcoef(_x, _y)[0, 1])
_S = nx.Graph(_M); _S.remove_edges_from(nx.selfloop_edges(_S))
R_SIMPLE = nx.degree_assortativity_coefficient(_S)
assert abs(R_MULTI) < 0.03 and -0.17 < R_SIMPLE < -0.11, (R_MULTI, R_SIMPLE)

LINES = {
    # hook
    "h1": "先看这两张网络。节点的度，就是它的连接数。两张网络里，每个节点的度一模一样，所以度分布完全相同。",
    "h2": "可是看看金色的枢纽，也就是连接最多的几个节点。左边的枢纽彼此相连，抱成一团；右边的枢纽互不相连，各自带着一群小节点。",
    "h3": "所以，度分布只告诉我们每个节点有几条边，却没说这些边连向谁。",
    "h4": "【慢】谁和谁相连的统计规律，就是度相关性。它会改变疾病怎样传播、网络怎样崩溃。",
    # parts
    "q0": "这一期分三部分来讲。",
    "q1": "第一部分，边连向谁：怎样描述和度量度相关。",
    "q2": "第二部分，观察到的度相关，有多少只是结构约束造成的。",
    "q3": "第三部分，更高层的结构，富人俱乐部和核分解，以及度相关对网络过程的影响。",
    # edge sampling
    "f1": "先看第一部分。我们先做个小实验：随机挑一个节点，记下它的度。",
    "f2": "现在换一种挑法：随机挑一条边，再看它一端的节点。",
    "f3": "中心这个节点有九条边，被抽中的机会就是九份；外面的小节点只有一条边，机会只有一份。所以沿着边找到的，往往是高度节点。",
    "f4": "这就是友谊悖论：平均来说，你的朋友拥有的朋友，比你多。",
    "f4b": "在一张两千个节点的网络里，节点的平均度是四，而沿着边走到的邻居，平均度接近十二。",
    "f5": "【慢】所以判断度相关，基线不是平均度，而是这个偏高的邻居平均度。",
    # k_nn
    "k1": "接下来，把度相同的节点放在一起，算出它们邻居的平均度。这张图横轴是节点的度，纵轴是邻居的平均度，两条轴都是对数刻度。",
    "k2": "灰色曲线是平的：高度节点和低度节点的邻居差不多。这样的网络叫中性网络。",
    "k3": "蓝色曲线往上走，说明枢纽连枢纽，叫同配。",
    "k3b": "绿色曲线往下走，说明枢纽连小节点，叫异配。",
    "k4": "这三条曲线来自同一个度序列，只是边的连法不同。",
    # r
    "r1": "还可以把它压缩成一个数。把每条边两端节点的度配成一对，画成左边的散点图：横轴是一端的度，纵轴是另一端的度。",
    "r1b": "这些点的相关系数，就叫度相关系数。正数是同配，负数是异配。开头那张异配网络，是负零点六五。",
    "r2": "星形网络是最极端的异配：中心连的全是叶子，相关系数是负一。",
    "r3": "真实网络里，物理学家合作网是正零点三六，演员合作网是正零点二一。社会网络多是同配的。",
    "r4": "而酵母蛋白质相互作用网络是负零点一六，大肠杆菌代谢网络是负零点二四。生物网络多是异配的。",
    # structural cutoff
    "c1": "下面进入第二部分。生物网络的异配，是不是一定来自生物学，需要检验。",
    "c1b": "比如早期的酵母蛋白质网络，很多来自酵母双杂交实验：用一个蛋白作诱饵，去筛选和它结合的猎物蛋白。",
    "c2": "先看一个纯粹由结构造成的效应。设想一个三百个节点、四百五十条边的网络，里面有两个枢纽，度分别是五十五和四十六。",
    "c3": "如果完全随机配对，它们之间应该有大约二点八条边。",
    "c3b": "公式里，分子是两个枢纽的度相乘，分母是边数的两倍。",
    "c3c": "【慢】可在简单图里，两个节点之间最多只能有一条边。",
    "c4": "多出来的边只好连到别处，大多连到低度节点上。网络就这样被迫变得异配，这叫结构性异配。",
    "c5": "在一张五千个节点的模拟无标度网络里，允许重边时，相关系数接近零；合并成简单图，就变成了负零点一四。",
    "c6": "所以要用保持度序列的随机网络作零模型，也就是作比较的参照：每次交换两条边的端点，每个节点的度不变，连法被打乱。",
    "c7": "按这种检验，早期酵母蛋白质网络和代谢网络的异配，大部分能由度分布本身解释；社会网络的同配，却解释不了。",
    # rich club
    "rc1": "最后是第三部分。先看最顶层：度最高的那些节点之间，连得紧不紧。这叫富人俱乐部。",
    "rc1b": "右边是富人俱乐部系数：分子是这些高度节点之间实际的边数，乘以二；分母是它们之间最多可能的边数。",
    "rc2": "麻烦在于，高度节点即使随机连边，彼此相连的机会也更大。所以必须除以保度随机网络的值。比值大于一，才算富人俱乐部。",
    "rc3a": "结构脑网络，是用弥散磁共振追踪白质纤维，再把脑区连起来得到的网络。",
    "rc3": "2011年的一项研究，在二十一名健康人的结构脑网络中发现，楔前叶、额上回、丘脑、海马等脑区，组成了明显的富人俱乐部。",
    "rc4": "而在蛋白质相互作用网络里，这个比值低于一，高度蛋白之间的连接，反而少于随机预期。",
    # k-core
    "p1": "另一种找核心的办法，叫核分解，像剥洋葱一样，一层一层地剥。",
    "p2": "先删掉度为一的节点。删完以后，有的邻居度也变成了一，接着删，直到剩下的每个节点都至少有两条边。",
    "p3": "再要求至少三条、四条、五条。每个节点最后留在哪一层，就是它的核数。右边的颜色，表示核数。",
    "p4": "【慢】核数衡量的是，节点嵌在多稠密的子图里。你看圈出的这个节点，连着八条边，核数却只有一。",
    "p5": "研究发现，从单个节点出发的传播能走多远，核数往往比度预测得更好；在酵母蛋白质网络里，越靠内层的核，必需蛋白的比例越高。",
    # dynamics
    "d1": "度相关还会改变网络上发生的过程。把开头那两张网络，都拿掉度最高的四个节点。",
    "d2": "同配网络里，枢纽彼此冗余，最大的那一团还剩九成多；异配网络里，每个枢纽都带走一批只连着它的小节点，只剩七成多。",
    "d3": "传播也一样：同配网络里，高度节点相互感染，形成病原体的储库，让疾病在整体稀疏时也能持续。",
    # recap
    "z1": "好，我们来总结一下。",
    "z2": "第一，度分布之后，还要看边连向谁：同配还是异配，可以用邻居平均度或度相关系数来刻画。",
    "z3": "第二，异配和富人俱乐部，都要和保持度序列的随机网络比较，排除结构本身的约束。",
    "z4": "第三，度相关会改变网络的鲁棒性、传播和核心结构；解读之前，先确认网络是怎样构建的。",
}


def knn_curve(G, nb=14):
    k = dict(G.degree())
    knn = nx.average_neighbor_degree(G)
    ks = np.array([k[v] for v in G]); kn = np.array([knn[v] for v in G])
    edges = np.unique(np.floor(np.logspace(np.log10(ks.min()), np.log10(ks.max() + 1), nb)).astype(int))
    xs, ys = [], []
    for a, b in zip(edges[:-1], edges[1:]):
        m = (ks >= a) & (ks < b)
        if m.sum() >= 3:
            xs.append(np.log10(ks[m].mean())); ys.append(np.log10(kn[m].mean()))
    return np.array(xs), np.array(ys)


class Episode(Narrated):
    LINES = LINES

    def construct(self):
        self.hook()
        parts_slide(self, "这一期分三部分", ["一  边连向谁：同配与异配", "二  结构约束与零模型", "三  富人俱乐部、核分解与网络过程"])
        self.edge_sampling()
        self.knn()
        self.r_coef()
        self.structural()
        self.rich_club()
        self.kcore()
        self.dynamics()
        self.recap()

    # ------------------------------------------------------------------ hook
    def views(self, color_a=BLUE, color_d=GREEN):
        va = NetView(GA, fit(nx.kamada_kawai_layout(GA), (-6.4, -0.8, -2.9, 2.3)), color=color_a, rmin=0.05, rk=0.035, eo=0.4)
        vd = NetView(GD, fit(nx.kamada_kawai_layout(GD), (0.8, 6.4, -2.9, 2.3)), color=color_d, rmin=0.05, rk=0.035, eo=0.4)
        return va, vd

    def hook(self):
        va, vd = self.views()
        with self.say("h1") as d:
            self.play(FadeIn(va.group), FadeIn(vd.group), run_time=1.4)
            eq = T("度序列相同", 30, INK).move_to([0, 3.1, 0])
            self.play(FadeIn(eq), run_time=0.6)
        with self.say("h2") as d:
            hh = [(u, v) for u, v in GA.edges() if u in HUBS and v in HUBS]
            self.play(*[va.dots[h].animate.set_color(GOLD) for h in HUBS], *[vd.dots[h].animate.set_color(GOLD) for h in HUBS], run_time=0.8)
            self.play(*[nv_edge(va, u, v).animate.set_stroke(GOLD, width=4, opacity=1) for u, v in hh], run_time=1.0)
            fans = [(u, v) for u, v in GD.edges() if (u in HUBS) != (v in HUBS)]
            self.play(*[nv_edge(vd, u, v).animate.set_stroke(GOLD, width=2.5, opacity=0.9) for u, v in fans], run_time=1.0)
            la = T("枢纽连枢纽", 26, BLUE).next_to(va.group, DOWN, buff=0.15)
            ld = T("枢纽连小节点", 26, GREEN).next_to(vd.group, DOWN, buff=0.15)
            self.play(FadeIn(la), FadeIn(ld), run_time=0.6)
        with self.say("h3") as d:
            self.play(Indicate(eq, color=GOLD), run_time=1.0)
        with self.say("h4") as d:
            q = T("边连向谁", 54, GOLD, weight=BOLD)
            self.play(VGroup(va.group, vd.group, la, ld, eq).animate.set_opacity(0.15), run_time=0.8)
            self.play(Write(q), run_time=1.0)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ edge sampling
    def edge_sampling(self):
        tag = self.chapter("第一部分 · 沿着边去抽样")
        G = nx.star_graph(9)
        G.add_edges_from([(1, 10), (3, 11), (5, 12)])
        pos = fit(nx.kamada_kawai_layout(G), (-5.8, -0.6, -2.8, 2.4))
        v = NetView(G, pos, color=BLUE, rmin=0.08, rk=0.04, eo=0.5)
        hub = 0
        with self.say("f1") as d:
            self.play(FadeIn(tag), FadeIn(v.group), run_time=1.0)
            rng = random.Random(4)
            for _ in range(4):
                x = rng.choice(list(G))
                self.play(Indicate(v.dots[x], color=GOLD, scale_factor=2.0), run_time=0.45)
        with self.say("f2") as d:
            rng = random.Random(6)
            E = list(G.edges())
            for _ in range(5):
                e = rng.choice(E)
                end = e[rng.randrange(2)]
                ln = nv_edge(v, *e)
                self.play(ln.animate.set_stroke(GOLD, width=5, opacity=1), Indicate(v.dots[end], color=GOLD, scale_factor=2.0), run_time=0.5)
                self.play(ln.animate.set_stroke(BLUE, width=1.4, opacity=0.5), run_time=0.15)
        with self.say("f3") as d:
            self.play(*[nv_edge(v, *e).animate.set_stroke(GOLD, width=4, opacity=1) for e in G.edges(hub)], run_time=1.0)
            k = counter("中心节点的边", f"{G.degree(hub)} 条", GOLD).move_to([-3.2, -3.2, 0])
            self.play(v.group.animate.shift(UP * 0.4), FadeIn(k), run_time=0.8)
        ax = Axes(x_range=[0, 14, 2], y_range=[0, 1, 1], x_length=5.6, y_length=0.01, axis_config={"color": MUTED, "include_tip": False, "font_size": 22},
                  x_axis_config={"numbers_to_include": [0, 4, 8, 12]}).move_to([3.4, -0.6, 0])
        m1 = Triangle(color=BLUE, fill_opacity=1).scale(0.15).rotate(PI).next_to(ax.c2p(KMEAN, 0), UP, buff=0.05)
        m2 = Triangle(color=GOLD, fill_opacity=1).scale(0.15).rotate(PI).next_to(ax.c2p(KNN, 0), UP, buff=0.05)
        t1 = counter("节点平均度", f"{KMEAN:.1f}", BLUE, vs=34).next_to(m1, UP, buff=0.15)
        t2 = counter("邻居平均度", f"{KNN:.1f}", GOLD, vs=34).next_to(m2, UP, buff=0.15)
        with self.say("f4") as d:
            self.play(Create(ax), run_time=0.6)
            self.play(FadeIn(m1), FadeIn(t1), run_time=0.8)
        with self.say("f4b") as d:
            self.play(FadeIn(m2), FadeIn(t2), run_time=0.8)
            arr = Arrow(ax.c2p(KMEAN, 0) + DOWN * 0.4, ax.c2p(KNN, 0) + DOWN * 0.4, buff=0.05, color=GOLD)
            self.play(GrowArrow(arr), run_time=0.6)
        with self.say("f5") as d:
            self.play(Circumscribe(t2, color=GOLD), run_time=1.2)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ k_nn
    def knn(self):
        tag = self.chapter("第一部分 · 邻居平均度")
        B = nx.barabasi_albert_graph(3000, 2, seed=2)
        A = xbs(B, True, 60000, 1)
        D = xbs(B, False, 60000, 1)
        Nn = B.copy(); nx.double_edge_swap(Nn, 30000, max_tries=10 ** 6, seed=1)
        grp, la = log_axes((0, 2), (0, 2), xl=6.4, yl=4.6)
        grp.move_to([-0.6, -0.4, 0])
        xl = T("节点的度", 22, MUTED).next_to(grp, DOWN, buff=0.1)
        yl = T("邻居平均度", 22, MUTED).rotate(PI / 2).next_to(grp, LEFT, buff=0.15)

        def curve(G, c):
            xs, ys = knn_curve(G)
            return la.plot_line_graph(xs, ys, line_color=c, vertex_dot_radius=0.06, stroke_width=4)
        cn, ca, cd = curve(Nn, MUTED), curve(A, BLUE), curve(D, GREEN)
        lab = lambda s, c, cv: T(s, 26, c).next_to(cv["line_graph"].get_end(), RIGHT, buff=0.2)
        with self.say("k1") as d:
            self.play(FadeIn(tag), FadeIn(grp), FadeIn(xl), FadeIn(yl), run_time=1.2)
        with self.say("k2") as d:
            self.play(Create(cn), run_time=1.4)
            self.play(FadeIn(lab("中性", MUTED, cn)), run_time=0.5)
        with self.say("k3") as d:
            self.play(Create(ca), run_time=1.2)
            self.play(FadeIn(lab("同配", BLUE, ca)), run_time=0.4)
        with self.say("k3b") as d:
            self.play(Create(cd), run_time=1.2)
            self.play(FadeIn(lab("异配", GREEN, cd)), run_time=0.4)
        with self.say("k4") as d:
            note = T("同一个度序列", 28, GOLD).move_to([4.6, 2.6, 0])
            self.play(FadeIn(note), run_time=0.8)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ r
    def r_coef(self):
        tag = self.chapter("第一部分 · 度相关系数")
        G = GD
        k = dict(G.degree())
        km_ = int(np.ceil((max(k.values()) + 1) / 5) * 5)
        ax = Axes(x_range=[0, km_, 5], y_range=[0, km_, 5], x_length=4.6, y_length=4.6,
                  axis_config={"color": MUTED, "include_tip": False, "font_size": 20},
                  x_axis_config={"numbers_to_include": list(range(5, km_ + 1, 5))}, y_axis_config={"numbers_to_include": list(range(5, km_ + 1, 5))}).move_to([-3.4, -0.4, 0])
        xl = T("一端的度", 22, MUTED).next_to(ax.x_axis, DOWN, buff=0.35)
        yl = T("另一端的度", 22, MUTED).rotate(PI / 2).next_to(ax.y_axis, LEFT, buff=0.35)
        rng = np.random.default_rng(0)
        pts = VGroup(*[Dot(ax.c2p(k[u] + rng.uniform(-0.2, 0.2), k[v] + rng.uniform(-0.2, 0.2)), radius=0.05, color=GREEN).set_opacity(0.7)
                       for a, b in G.edges() for u, v in ((a, b), (b, a))])
        rv = nx.degree_assortativity_coefficient(G)
        with self.say("r1") as d:
            self.play(FadeIn(tag), Create(ax), FadeIn(xl), FadeIn(yl), run_time=1.0)
            self.play(LaggedStart(*[FadeIn(p) for p in pts], lag_ratio=0.01), run_time=d * 0.4)
        with self.say("r1b") as d:
            rr = MathTex(r"r = %.2f" % rv, font_size=40, color=GREEN).next_to(ax, UP, buff=0.2)
            self.play(FadeIn(rr), run_time=0.6)
        S = nx.star_graph(6)
        sp = fit(nx.circular_layout(range(1, 7)) | {0: np.zeros(2)}, (1.6, 4.6, -1.6, 1.4))
        sv = NetView(S, sp, color=GOLD, rmin=0.08, rk=0.03, eo=0.7)
        with self.say("r2") as d:
            self.play(FadeIn(sv.group), run_time=0.8)
            rs = MathTex(r"r=-1", font_size=46, color=GOLD).next_to(sv.group, DOWN, buff=0.4)
            self.play(Write(rs), run_time=0.8)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.6)
        nl = NumberLine(x_range=[-0.3, 0.4, 0.1], length=11, color=MUTED, include_numbers=True, font_size=24,
                        decimal_number_config={"num_decimal_places": 1}).move_to(DOWN * 0.4)
        zero = DashedLine(nl.n2p(0) + UP * 2.4, nl.n2p(0) + DOWN * 0.3, color=MUTED)
        data = [("物理学合作", 0.363, BLUE, 1), ("演员合作", 0.208, BLUE, 0), ("酵母蛋白质", -0.156, GREEN, 0), ("大肠杆菌代谢", -0.240, GREEN, 1)]

        def mark(name, x, c, lvl):
            dt = Dot(nl.n2p(x), radius=0.12, color=c)
            lb = VGroup(T(name, 24, c), T(f"{x:+.2f}".replace("-", "−"), 26, c, weight=BOLD)).arrange(DOWN, buff=0.08).next_to(dt, UP, buff=0.3 + 1.1 * lvl)
            ln = Line(dt.get_center(), lb.get_bottom(), color=c, stroke_width=1.5)
            return VGroup(dt, ln, lb)
        with self.say("r3") as d:
            self.play(Create(nl), Create(zero), run_time=1.0)
            self.play(FadeIn(mark(*data[0])), run_time=0.7)
            self.play(FadeIn(mark(*data[1])), run_time=0.7)
            sa = T("同配", 30, BLUE, weight=BOLD).next_to(nl.n2p(0.3), DOWN, buff=0.7)
            self.play(FadeIn(sa), run_time=0.5)
        with self.say("r4") as d:
            self.play(FadeIn(mark(*data[2])), run_time=0.7)
            self.play(FadeIn(mark(*data[3])), run_time=0.7)
            sd = T("异配", 30, GREEN, weight=BOLD).next_to(nl.n2p(-0.2), DOWN, buff=0.7)
            self.play(FadeIn(sd), run_time=0.5)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ structural cutoff
    def structural(self):
        tag = self.chapter("第二部分 · 结构性异配")
        with self.say("c1") as d:
            self.play(FadeIn(tag), run_time=0.5)
            q = T("异配一定来自生物学：需要检验", 40, GOLD, weight=BOLD)
            self.play(FadeIn(q), run_time=0.8)
            self.play(FadeOut(q), run_time=0.5)
        with self.say("c1b") as d:
            self.clip_on("yt_y2h_jove.mp4", "center", "视频：JoVE (Journal of Visualized Experiments) · YouTube", start=15)
        self.clip_off()
        a, b = np.array([-2.2, 0.4, 0]), np.array([2.2, 0.4, 0])
        ha = Dot(a, radius=0.35, color=GOLD); hb = Dot(b, radius=0.32, color=GOLD)
        la = T("55", 26, BG, weight=BOLD).move_to(a); lb = T("46", 26, BG, weight=BOLD).move_to(b)
        sa = VGroup(*[Line(a, a + 1.3 * np.array([np.cos(t), np.sin(t), 0]), color=GOLD, stroke_width=1.5, stroke_opacity=0.6)
                      for t in np.linspace(PI * 0.55, PI * 1.45, 18)])
        sb = VGroup(*[Line(b, b + 1.3 * np.array([np.cos(t), np.sin(t), 0]), color=GOLD, stroke_width=1.5, stroke_opacity=0.6)
                      for t in np.linspace(-PI * 0.45, PI * 0.45, 15)])
        info = T("300 个节点 · 450 条边", 26, MUTED).move_to([0, 2.6, 0])
        with self.say("c2") as d:
            self.play(FadeIn(info), GrowFromCenter(ha), GrowFromCenter(hb), FadeIn(la), FadeIn(lb), run_time=1.0)
            self.play(Create(sa), Create(sb), run_time=1.2)
        exp = MathTex(r"\frac{k\,k'}{2L}=\frac{55\times46}{900}\approx 2.8", font_size=42, color=INK).move_to([0, -1.6, 0])
        arcs = VGroup(*[ArcBetweenPoints(a, b, angle=t, color=RED, stroke_width=3) for t in (-0.5, 0.0, 0.5)])
        with self.say("c3") as d:
            self.play(Write(exp), run_time=1.2)
        with self.say("c3b") as d:
            n_ = T("两个枢纽的度相乘", 22, INK).next_to(exp, RIGHT, buff=0.3).shift(UP * 0.35)
            d_ = T("边数的两倍", 22, INK).next_to(exp, RIGHT, buff=0.3).shift(DOWN * 0.35)
            self.play(FadeIn(n_), Indicate(exp[0][0:3], color=GOLD), run_time=0.8)
            self.play(FadeIn(d_), Indicate(exp[0][4:6], color=GOLD), run_time=0.8)
        with self.say("c3c") as d:
            self.play(FadeOut(n_), FadeOut(d_), run_time=0.3)
            self.play(Create(arcs), run_time=1.0)
            self.play(FadeOut(arcs[0]), FadeOut(arcs[2]), arcs[1].animate.set_color(GREEN), run_time=0.8)
            one = T("最多 1 条", 28, GREEN).next_to(arcs[1], UP, buff=0.15)
            self.play(FadeIn(one), run_time=0.5)
        rng = np.random.default_rng(1)
        leaves = [np.array([rng.uniform(-1.4, 1.4), rng.uniform(-3.2, -2.6), 0]) for _ in range(4)]
        ld = VGroup(*[Dot(p, radius=0.07, color=BLUE) for p in leaves])
        rl = VGroup(*[Line(a if i % 2 else b, p, color=GOLD, stroke_width=2.5) for i, p in enumerate(leaves)])
        with self.say("c4") as d:
            self.play(FadeOut(exp), run_time=0.4)
            self.play(FadeIn(ld), Create(rl), run_time=1.2)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.6)
        c1 = counter("允许重边", f"r = {R_MULTI:+.2f}".replace("-", "−"), MUTED, vs=40).move_to([-3.2, 0.6, 0])
        c2 = counter("合并成简单图", f"r = {R_SIMPLE:+.2f}".replace("-", "−"), GREEN, vs=40).move_to([3.2, 0.6, 0])
        ar = Arrow(c1.get_right(), c2.get_left(), buff=0.4, color=MUTED)
        hd = T("模拟无标度网络 · 5000 个节点", 26, MUTED).move_to([0, 2.4, 0])
        with self.say("c5") as d:
            self.play(FadeIn(hd), FadeIn(c1), run_time=0.8)
            self.play(GrowArrow(ar), FadeIn(c2), run_time=0.9)
        self.play(*[FadeOut(m) for m in (c1, c2, ar, hd)], run_time=0.5)
        # double-edge swap
        P = {0: [-2.6, 0.9], 1: [-0.6, 0.9], 2: [-2.6, -1.1], 3: [-0.6, -1.1]}
        P = {k_: np.array([*v, 0]) + LEFT * 0.4 for k_, v in P.items()}
        dots = VGroup(*[Dot(p, radius=0.15, color=BLUE) for p in P.values()])
        e1 = Line(P[0], P[1], color=INK, stroke_width=5); e2 = Line(P[2], P[3], color=INK, stroke_width=5)
        with self.say("c6") as d:
            self.play(FadeIn(dots), Create(e1), Create(e2), run_time=0.8)
            self.play(Transform(e1, Line(P[0], P[3], color=GOLD, stroke_width=5)), Transform(e2, Line(P[2], P[1], color=GOLD, stroke_width=5)), run_time=1.2)
            kl = VGroup(*[T("1", 24, MUTED).next_to(P[i], LEFT if i in (0, 2) else RIGHT, buff=0.2) for i in range(4)])
            self.play(FadeIn(kl), run_time=0.5)
            many = T("× 很多次", 30, GOLD).move_to([3.0, -0.1, 0])
            self.play(FadeIn(many), run_time=0.6)
        with self.say("c7") as d:
            self.play(FadeOut(VGroup(dots, e1, e2, kl, many)), run_time=0.5)
            tab = VGroup(
                VGroup(T("蛋白质 / 代谢网络的异配", 28, GREEN), T("大部分可由度分布解释", 28, INK)).arrange(DOWN, buff=0.15),
                VGroup(T("社会网络的同配", 28, BLUE), T("度分布解释不了", 28, INK)).arrange(DOWN, buff=0.15)).arrange(RIGHT, buff=1.2)
            self.play(FadeIn(tab[0]), run_time=0.8)
            self.play(FadeIn(tab[1]), run_time=0.8)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ rich club
    def rich_club(self):
        tag = self.chapter("第三部分 · 富人俱乐部")
        f = MathTex(r"\phi(k)=\frac{2E_{>k}}{N_{>k}(N_{>k}-1)}", font_size=46, color=INK).move_to([3.4, 1.8, 0])
        G = nx.barabasi_albert_graph(70, 2, seed=8)
        rich = sorted(G, key=G.degree, reverse=True)[:7]
        for i, u in enumerate(rich):
            for w in rich[i + 1:]:
                if (i + rich.index(w)) % 2 == 0:
                    G.add_edge(u, w)
        pos = fit(nx.kamada_kawai_layout(G), (-6.4, -0.6, -3.0, 2.6))
        v = NetView(G, pos, color=MUTED, rmin=0.05, rk=0.03, eo=0.35)
        with self.say("rc1") as d:
            self.play(FadeIn(tag), FadeIn(v.group), run_time=1.0)
            self.play(*[v.dots[u].animate.set_color(GOLD) for u in rich],
                      *[nv_edge(v, a, b).animate.set_stroke(GOLD, width=3, opacity=1) for a, b in G.edges() if a in rich and b in rich], run_time=1.2)
        with self.say("rc1b") as d:
            self.play(Write(f), run_time=1.0)
            fn_ = T("高度节点之间实际的边数 × 2", 20, INK).next_to(f, UP, buff=0.2)
            fd_ = T("它们之间最多可能的边数", 20, INK).next_to(f, DOWN, buff=0.2)
            self.play(FadeIn(fn_), run_time=0.5)
            self.play(FadeIn(fd_), run_time=0.5)
        self.play(FadeOut(fn_), FadeOut(fd_), run_time=0.4)
        with self.say("rc2") as d:
            nf = MathTex(r"\rho(k)=\frac{\phi(k)}{\phi_{\mathrm{ran}}(k)}", font_size=46, color=GOLD).next_to(f, DOWN, buff=0.6)
            self.play(Write(nf), run_time=1.2)
            g1 = MathTex(r"\rho>1", font_size=40, color=GOLD).next_to(nf, DOWN, buff=0.5)
            self.play(FadeIn(g1), run_time=0.6)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.6)
        brain = Ellipse(width=8.4, height=5.4, color=MUTED, stroke_width=3).shift(DOWN * 0.3)
        rng = np.random.default_rng(3)
        others = VGroup(*[Dot([rng.uniform(-3.6, 3.6), rng.uniform(-2.6, 2.0), 0], radius=0.06, color=MUTED) for _ in range(70)])
        others = VGroup(*[d_ for d_ in others if (d_.get_x() / 4.0) ** 2 + ((d_.get_y() + 0.3) / 2.6) ** 2 < 1])
        hubs = [("楔前叶", [0.9, 0.9]), ("额上回", [-2.4, 1.0]), ("丘脑", [0.0, -0.6]), ("海马", [1.6, -1.4]), ("顶上皮层", [2.4, 1.2]), ("壳核", [-1.2, -1.2])]
        hd = [Dot([*p, 0], radius=0.16, color=GOLD) for _, p in hubs]
        hl = VGroup(*[T(n, 22, GOLD).next_to(hd[i], UP, buff=0.1) for i, (n, _) in enumerate(hubs)])
        hx = VGroup(*[Line(hd[i].get_center(), hd[j].get_center(), color=GOLD, stroke_width=2.5, stroke_opacity=0.8)
                      for i in range(len(hd)) for j in range(i + 1, len(hd))])
        info = T("2011 · 21 名健康被试", 24, MUTED).to_corner(UR, buff=0.45)
        with self.say("rc3a") as d:
            self.clip_on("yt_hubs_whitaker.mp4", "center", "视频：Kirstie Whitaker · YouTube", start=5)
        self.clip_off()
        with self.say("rc3") as d:
            self.play(Create(brain), FadeIn(others), FadeIn(info), run_time=1.0)
            self.play(*[GrowFromCenter(x) for x in hd], FadeIn(hl), run_time=1.0)
            self.play(Create(hx), run_time=1.4)
        with self.say("rc4") as d:
            self.play(FadeOut(VGroup(brain, others, *hd, hl, hx, info)), run_time=0.6)
            ax = NumberLine(x_range=[0, 2, 0.5], length=7, color=MUTED, include_numbers=False, include_ticks=False).move_to(DOWN * 0.6)
            onel = T("1", 26, INK).next_to(ax.n2p(1), DOWN, buff=0.2)
            one = DashedLine(ax.n2p(1) + UP * 1.6, ax.n2p(1) + DOWN * 0.2, color=INK)
            m1 = VGroup(Dot(ax.n2p(1.6), radius=0.14, color=GOLD), T("脑结构网络", 24, GOLD)).arrange(UP, buff=0.2)
            m1.shift(ax.n2p(1.6) - m1[0].get_center())
            m2 = VGroup(Dot(ax.n2p(0.6), radius=0.14, color=GREEN), T("蛋白质网络", 24, GREEN)).arrange(UP, buff=0.2)
            m2.shift(ax.n2p(0.6) - m2[0].get_center())
            rl = MathTex(r"\rho", font_size=40, color=MUTED).next_to(ax, RIGHT, buff=0.3)
            sk = VGroup(T("少于随机", 22, MUTED).next_to(ax.n2p(0.5), DOWN, buff=0.25), T("多于随机", 22, MUTED).next_to(ax.n2p(1.5), DOWN, buff=0.25))
            self.play(Create(ax), Create(one), FadeIn(onel), FadeIn(rl), FadeIn(sk), FadeIn(m1), run_time=1.0)
            self.play(FadeIn(m2, shift=LEFT * 0.3), run_time=0.8)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ k-core
    def kcore(self):
        tag = self.chapter("第三部分 · 核分解")
        rng = random.Random(4)
        G = nx.complete_graph(6)
        for n_, m_ in ((16, 3), (16, 2)):
            for _ in range(n_):
                new = G.number_of_nodes()
                G.add_edges_from((new, t) for t in rng.sample(list(G), m_))
        for _ in range(10):
            new = G.number_of_nodes()
            G.add_edge(new, rng.choice(list(G)))
        h = G.number_of_nodes()
        G.add_edges_from([(h, 8)] + [(h, h + 1 + i) for i in range(7)])
        core = nx.core_number(G)
        pos = fit(nx.kamada_kawai_layout(G), (-6.0, 1.6, -3.2, 2.7))
        v = NetView(G, pos, color=BLUE, rmin=0.06, rk=0.03, eo=0.45)
        cols = {1: MUTED, 2: BLUE, 3: GREEN, 4: GOLD, 5: RED, 6: VIOLET}
        with self.say("p1") as d:
            self.play(FadeIn(tag), FadeIn(v.group), run_time=1.2)
        H = G.copy()
        legend = VGroup()

        def peel(k, rt):
            rounds = []
            while True:
                rm = [u for u in H if H.degree(u) < k]
                if not rm:
                    break
                rounds.append(rm); H.remove_nodes_from(rm)
            for rm in rounds:
                self.play(*[v.dots[u].animate.set_color(cols[k - 1]).set_opacity(0.35) for u in rm],
                          *[e.animate.set_stroke(opacity=0.08) for (a, b), e in v.edges.items() if a in rm or b in rm], run_time=rt)
            return len(rounds)
        with self.say("p2") as d:
            peel(2, 0.6)
        maxk = max(core.values())
        with self.say("p3") as d:
            for k in range(3, maxk + 1):
                peel(k, 0.45)
            self.play(*[v.dots[u].animate.set_color(cols[min(maxk, 6)]).scale(1.3) for u in H], run_time=0.6)
            for k in sorted(set(core.values())):
                legend.add(VGroup(Dot(radius=0.09, color=cols[min(k, 6)]), T(f"核数 {k}", 22, INK)).arrange(RIGHT, buff=0.15))
            legend.arrange(DOWN, aligned_edge=LEFT, buff=0.2).move_to([4.6, 0.4, 0])
            self.play(FadeIn(legend), run_time=0.6)
        hubk = max(G, key=lambda u: (G.degree(u), -core[u]))
        with self.say("p4") as d:
            self.play(*[v.dots[u].animate.set_color(cols[min(core[u], 6)]).set_opacity(1) for u in G],
                      *[e.animate.set_stroke(opacity=0.45) for e in v.edges.values()], run_time=1.0)
            low = [u for u in G if G.degree(u) >= 4 and core[u] <= 2]
            if low:
                u = max(low, key=G.degree)
                assert G.degree(u) == 8 and core[u] == 1
                self.play(Circumscribe(v.dots[u], color=GOLD, shape=Circle), run_time=1.0)
                lab = T(f"度 {G.degree(u)}，核数 {core[u]}", 24, GOLD).next_to(v.dots[u], DOWN, buff=0.2)
                self.play(FadeIn(lab), run_time=0.5)
        self.low_hub_found = bool(low)
        with self.say("p5") as d:
            inner = [u for u in G if core[u] == maxk]
            self.play(*[Indicate(v.dots[u], color=RED, scale_factor=1.6) for u in inner], run_time=1.2)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ dynamics
    def dynamics(self):
        tag = self.chapter("第三部分 · 对鲁棒性与传播的影响")
        va, vd = self.views()
        la = T("同配", 28, BLUE).move_to([-3.6, 2.75, 0])
        ld = T("异配", 28, GREEN).move_to([3.6, 2.75, 0])
        with self.say("d1") as d:
            self.play(FadeIn(tag), FadeIn(va.group), FadeIn(vd.group), FadeIn(la), FadeIn(ld), run_time=1.2)
            self.play(*va.flash(HUBS), *vd.flash(HUBS), run_time=0.8)
        ca = counter("最大连通部分", f"{FA:.0%}", BLUE, vs=36).move_to([-3.6, -3.35, 0])
        cd = counter("最大连通部分", f"{FD:.0%}", GREEN, vs=36).move_to([3.6, -3.35, 0])
        with self.say("d2") as d:
            self.play(*va.state(HUBS, hl=BLUE), *vd.state(HUBS, hl=GREEN), run_time=1.6)
            self.play(FadeIn(ca), FadeIn(cd), run_time=0.8)
        with self.say("d3") as d:
            self.play(FadeOut(VGroup(vd.group, ld, cd, ca)), *va.state((), hl=BLUE), run_time=0.8)
            hubsA = sorted(GA, key=GA.degree, reverse=True)[:8]
            self.play(*[va.dots[h].animate.set_color(RED).scale(1.3) for h in hubsA],
                      *[nv_edge(va, a, b).animate.set_stroke(RED, width=3, opacity=1) for a, b in GA.edges() if a in hubsA and b in hubsA], run_time=1.2)
            res = T("储库", 32, RED, weight=BOLD).move_to([2.6, 0, 0])
            self.play(FadeIn(res), run_time=0.6)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ recap
    def recap(self):
        items = [("z2", BLUE, "边连向谁：同配 / 异配"),
                 ("z3", GOLD, "和保度随机网络比较"),
                 ("z4", GREEN, "影响鲁棒性、传播与核心")]
        head, rows = recap_rows(items)
        with self.say("z1") as d:
            self.play(Write(head), run_time=0.8)
        for (k, _, _), row in zip(items, rows):
            with self.say(k) as d:
                self.play(FadeIn(row, shift=RIGHT * 0.3), run_time=0.8)
        self.wait(1.5)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=1.0)
