"""Animated explainer: 网络的几把尺子 (degree distribution, distance, clustering, centrality, ER random graph as null model)."""
import random

import networkx as nx
import numpy as np

from common import *  # noqa: F401,F403
from ahelp import NetView, counter, edge_line, fit, nv_edge, recap_rows, parts_slide

TITLE = "网络的几把尺子：度、距离、聚集与随机图"

# ---- the hook pair: same N, same M, very different degree distributions
GB = nx.barabasi_albert_graph(120, 2, seed=2)
GE = nx.gnm_random_graph(120, GB.number_of_edges(), seed=2)
KB = np.array([d for _, d in GB.degree()])
KE = np.array([d for _, d in GE.degree()])
assert nx.is_connected(GE) and KB.max() == 34 and KE.max() == 9
assert (KB <= 3).mean() > 0.5

LINES = {
    # hook
    "h1": "我们先看两张蛋白质网络，左边一张，右边一张。它们的节点一样多，边也一样多。",
    "h1b": "每个节点平均连着几条边，叫平均度。所以这两张网络的平均度完全相同，都是三点九。",
    "h2": "如果只报告平均度，它们看上去就是同一种网络。",
    "h3": "现在，把每个节点按连接数放大。差别马上就出来了：右边藏着几个连接极多的节点，叫枢纽。",
    "h4": "敲掉右边最大的那个枢纽，一下子断掉三十四个相互作用。",
    "h4b": "【慢】而左边，不管敲掉谁，最多只断九个。",
    "h5": "所以一个数字远远不够。要描述网络的结构，需要几把不同的尺子。",
    # parts
    "q0": "这一期分三部分来讲。",
    "q1": "第一部分，三把基本的尺子：度分布、距离和聚集系数。",
    "q2": "第二部分，中心性，也就是怎样衡量一个节点重不重要。",
    "q3": "第三部分，随机图：判断一张真实网络特殊在哪里的参照尺。",
    # degree distribution
    "d1": "先看第一部分。第一把尺子是度分布。度，就是一个节点的连接数。",
    "d1b": "度分布，是随机挑一个节点，它的度等于某个值的概率。",
    "d1c": "下面两张图，横轴是度，纵轴是概率。左边是网络甲，右边是网络乙，也就是开头那两张网络。",
    "d2": "网络甲的度，集中在平均值附近，分布只有一个峰。",
    "d3": "网络乙不一样。大多数节点只有两三个连接，分布却拖着一条长长的尾巴，这叫重尾分布。",
    "d4": "一个简单的判断办法，是看最大度是平均度的几倍。",
    "d4b": "【慢】网络甲是两倍多，网络乙将近九倍。",
    # distance
    "p1": "第二把尺子是距离。两个节点之间的距离，就是从一个走到另一个，最少要走几步。",
    "p2": "算距离的办法叫广度优先搜索：从这个金色的节点出发，像水波一样，一层一层往外扩。",
    "p3": "同一种颜色的节点，离出发点的距离相同。把所有节点对的距离取平均，就是平均路径长度。这张网络大约是五步。",
    "p4": "再看一个更一般的规律。在随机网络里，从一个节点出发——",
    "p5": "第一步能到达平均度那么多个节点，第二步是平均度的平方，第三步是立方。增长得非常快。",
    "p6": "【慢】所以平均距离，大约等于节点数的对数，除以平均度的对数。",
    "p6b": "公式里，分子是节点总数取对数，分母是平均度取对数。对数增长得很慢。",
    "p7": "所以，就算有几十亿个节点，平均距离也只有几步到十几步。",
    # clustering
    "c1": "第三把尺子叫聚集系数。它衡量一个节点的两个邻居之间是不是也相连，就像你的两个朋友，是不是也是朋友。",
    "c2": "这个金色节点有四个邻居。四个邻居之间，最多可以连六条边，就是这些虚线。",
    "c3": "实际只连了三条，就是绿色的这三条。",
    "c3b": "【慢】聚集系数，等于实际的边数，除以最多可能的边数。这里是三除以六，等于零点五。",
    "c4": "聚集系数高，说明网络里三角形多，节点喜欢抱成小团。",
    # centrality
    "z1": "下面进入第二部分：中心性，也就是衡量节点重要程度的指标。重要，有好几种不同的含义。",
    "z2": "最简单的是度中心性，只看直接的邻居有多少。按这个标准，最重要的是两个团里，连接最多的这两个节点。",
    "z3": "但是看中间这个金色的节点。它只有两条边，却是两个团之间唯一的通道。",
    "z4": "两团之间的最短路径，全都要经过它。经过一个节点的最短路径越多，它的介数中心性就越高。",
    "z4b": "【慢】介数高的节点，就是网络的瓶颈。",
    "z5": "有研究发现，在有向的转录调控网络里，这种瓶颈节点，比连接多的枢纽更能预测一个基因是不是必需的。",
    "z6": "在脑网络里，节点是脑区。度高的枢纽脑区，常位于楔前叶、后扣带回和额顶联合皮层等区域。",
    # ER
    "e0": "最后是第三部分。有了尺子，还需要一个参照。最常用的参照，是数学家埃尔德什和雷尼研究的随机图。",
    "e1": "参照的意思是：如果连接完全随机，这些指标应该是多少。",
    "e2": "随机图的规则很简单：每一对节点，都以同样的概率，独立地决定连不连边。",
    "e3": "下面四张小图，从左到右，平均度越来越大。平均度小于一时，网络只是一堆零散的碎片。",
    "e4": "平均度越过一以后，最大的那一团迅速长大，叫巨连通分支，就是金色的这一团。",
    "e5": "平均度超过节点数的对数，这里大约是四，几乎所有节点都连成了一体。",
    "e6": "再看随机图的度分布。横轴是度，纵轴是概率。灰色柱子来自一张三千个节点的随机图，金色曲线是泊松分布。",
    "e6b": "【慢】它紧紧围在平均值附近，几乎不会出现枢纽。",
    # real vs random
    "v1": "现在拿一张真实网络，和同样规模的随机图比一比。这是一个约一亿八千万用户的即时通信网络。",
    "v2": "上面两根条，是平均路径长度。真实网络是六点六，随机图大约是七，几乎一样。",
    "v3": "下面两根条，是聚集系数，用的是对数刻度。真实网络是零点一一，随机图只有一亿分之八。",
    "v3b": "【慢】两者相差了大约六个数量级。",
    "v4": "度分布也是这样：真实网络有重尾和枢纽，随机图没有。",
    "v5": "所以随机图是一个零模型，也就是不带任何特殊结构的参照。真实网络偏离它的地方，才是值得解释的结构。",
    # recap
    "r1": "好，我们来总结一下。",
    "r2": "第一，只看平均度不够，要看完整的度分布。",
    "r3": "第二，距离、聚集系数和中心性，从不同角度刻画网络，各自回答不同的问题。",
    "r4": "第三，任何指标都要和零模型比，偏离随机的部分才有意义。",
    "r5": "这个专题的知识页面里，有画面上的这个交互演示。拖动连边概率，就能看到巨连通分支怎样突然出现。",
}


def bars(ax, ks, color, w=0.8):
    vals, cnt = np.unique(ks, return_counts=True)
    p = cnt / cnt.sum()
    g = VGroup()
    for k, h in zip(vals, p):
        x0, y0 = ax.c2p(k - w / 2, 0)[:2]
        x1, y1 = ax.c2p(k + w / 2, h)[:2]
        g.add(Rectangle(width=x1 - x0, height=max(y1 - y0, 0.01), fill_color=color, fill_opacity=0.85, stroke_width=0)
              .move_to([(x0 + x1) / 2, y0, 0], aligned_edge=DOWN))
    return g


class Episode(Narrated):
    LINES = LINES

    def construct(self):
        self.hook()
        parts_slide(self, "这一期分三部分", ["一  三把尺子：度分布、距离、聚集系数", "二  中心性：哪个节点重要", "三  随机图：一把参照尺"])
        self.degree_dist()
        self.distance()
        self.clustering()
        self.centrality()
        self.er()
        self.real_vs_random()
        self.recap()

    # ------------------------------------------------------------------ hook
    def hook(self):
        ve = NetView(GE, fit(nx.kamada_kawai_layout(GE), (-6.6, -0.6, -3.0, 2.4)), color=GREEN, rmin=0.06, rk=0.0, eo=0.4)
        vb = NetView(GB, fit(nx.kamada_kawai_layout(GB), (0.6, 6.6, -3.0, 2.4)), color=BLUE, rmin=0.06, rk=0.0, eo=0.4)
        self.views = (ve, vb)
        kk = KB.mean()
        ce = counter("平均度", f"{kk:.1f}", GREEN, vs=34).move_to([-3.6, 3.1, 0])
        cb = counter("平均度", f"{kk:.1f}", BLUE, vs=34).move_to([3.6, 3.1, 0])
        with self.say("h1") as d:
            self.play(FadeIn(ve.group), FadeIn(vb.group), run_time=d * 0.5)
        with self.say("h1b") as d:
            self.play(FadeIn(ce), FadeIn(cb), run_time=0.8)
        with self.say("h2") as d:
            eq = T("=", 54, GOLD, weight=BOLD).move_to([0, 3.0, 0])
            self.play(FadeIn(eq, scale=1.5), run_time=0.8)

        with self.say("h3") as d:
            self.play(*[ve.dots[v].animate.scale(0.6 + 0.35 * KE[v] ** 0.7) for v in GE],
                      *[vb.dots[v].animate.scale(0.6 + 0.35 * KB[v] ** 0.7) for v in GB], run_time=d * 0.5)
            hubs = sorted(GB, key=GB.degree, reverse=True)[:4]
            self.play(*[Indicate(vb.dots[h], color=GOLD, scale_factor=1.3) for h in hubs], run_time=1.2)
        hb = max(GB, key=GB.degree)
        he = max(GE, key=GE.degree)
        with self.say("h4") as d:
            eb = [e for e in vb.edges if hb in e]
            self.play(*[vb.edges[e].animate.set_stroke(RED, width=3, opacity=1) for e in eb], vb.dots[hb].animate.set_color(RED), run_time=1.0)
            self.play(*[vb.edges[e].animate.set_stroke(opacity=0) for e in eb], vb.dots[hb].animate.set_opacity(0), run_time=0.8)
            nb = counter("断掉", f"{KB[hb]} 条", RED, vs=34).move_to([3.6, -3.4, 0])
            self.play(FadeIn(nb), run_time=0.6)
        with self.say("h4b") as d:
            ee = [e for e in ve.edges if he in e]
            self.play(*[ve.edges[e].animate.set_stroke(RED, width=3, opacity=1) for e in ee], ve.dots[he].animate.set_color(RED), run_time=1.0)
            self.play(*[ve.edges[e].animate.set_stroke(opacity=0) for e in ee], ve.dots[he].animate.set_opacity(0), run_time=0.8)
            ne = counter("断掉", f"{KE[he]} 条", RED, vs=34).move_to([-3.6, -3.4, 0])
            self.play(FadeIn(ne), run_time=0.6)
        with self.say("h5") as d:
            self.play(FadeOut(VGroup(ve.group, vb.group, ce, cb, eq, nb, ne)), run_time=1.0)
            rulers = VGroup(*[VGroup(Rectangle(width=4.2, height=0.5, color=c, fill_color=c, fill_opacity=0.2, stroke_width=2),
                                     *[Line([-2.1 + 0.42 * i, 0.25, 0], [-2.1 + 0.42 * i, 0.25 - (0.25 if i % 5 else 0.4), 0], color=c, stroke_width=2) for i in range(1, 10)])
                              for c in (BLUE, GOLD, GREEN)]).arrange(DOWN, buff=0.4)
            self.play(LaggedStart(*[FadeIn(r, shift=RIGHT) for r in rulers], lag_ratio=0.3), run_time=1.4)
        self.play(FadeOut(rulers), run_time=0.6)

    # ------------------------------------------------------------------ degree distribution
    def degree_dist(self):
        tag = self.chapter("第一部分 · 度分布")

        def mk(x, K, color, xmax):
            ax = Axes(x_range=[0, xmax, 5], y_range=[0, 0.45, 0.2], x_length=5.4, y_length=3.6,
                      axis_config={"color": MUTED, "include_tip": False, "font_size": 22},
                      x_axis_config={"numbers_to_include": list(range(0, xmax + 1, 10))},
                      y_axis_config={"numbers_to_include": [0, 0.2, 0.4]}).move_to([x, -0.3, 0])
            xl = T("度", 22, MUTED).next_to(ax.x_axis, DOWN, buff=0.35)
            return ax, xl, bars(ax, K, color, w=0.8)
        axe, xle, be = mk(-3.5, KE, GREEN, 35)
        axb, xlb, bb = mk(3.5, KB, BLUE, 35)
        yl = T("概率", 22, MUTED).rotate(PI / 2).next_to(axe.y_axis, LEFT, buff=0.35)
        te = T("网络甲", 26, GREEN).next_to(axe, UP, buff=0.3)
        tb = T("网络乙", 26, BLUE).next_to(axb, UP, buff=0.3)
        with self.say("d1") as d:
            self.play(FadeIn(tag), run_time=0.6)
            dg = VGroup(Dot(radius=0.18, color=BLUE), *[Line(ORIGIN, 1.0 * np.array([np.cos(a), np.sin(a), 0]), color=MUTED) for a in (0.3, 1.9, 3.5, 5.0)])
            for l_ in dg[1:]:
                l_.add(Dot(l_.get_end(), radius=0.08, color=MUTED))
            dl_ = T("度 = 4", 30, GOLD).next_to(dg, RIGHT, buff=0.4)
            self.play(FadeIn(dg), FadeIn(dl_), run_time=1.0)
        with self.say("d1b") as d:
            self.play(FadeOut(dg), FadeOut(dl_), run_time=0.5)
            dd_ = VGroup(T("度分布", 36, GOLD, weight=BOLD), T("随机挑一个节点，它的度等于 k 的概率", 28, INK)).arrange(DOWN, buff=0.3)
            self.play(FadeIn(dd_, shift=UP * 0.2), run_time=0.8)
        self.play(FadeOut(dd_), run_time=0.4)
        with self.say("d1c") as d:
            self.play(Create(axe), Create(axb), FadeIn(xle), FadeIn(xlb), FadeIn(yl), FadeIn(te), FadeIn(tb), run_time=1.4)
        with self.say("d2") as d:
            self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in be], lag_ratio=0.08), run_time=d * 0.6)
        with self.say("d3") as d:
            self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bb], lag_ratio=0.05), run_time=d * 0.5)
            tail = Arrow(axb.c2p(12, 0.12), axb.c2p(31, 0.05), color=GOLD, buff=0, stroke_width=4)
            tl = T("长尾", 26, GOLD).next_to(tail, UP, buff=0.05)
            self.play(GrowArrow(tail), FadeIn(tl), run_time=0.9)
        km = KB.mean()
        with self.say("d4") as d:
            def marks(ax, K, c):
                m = DashedLine(ax.c2p(km, 0), ax.c2p(km, 0.42), color=INK, stroke_width=2)
                M = DashedLine(ax.c2p(K.max(), 0), ax.c2p(K.max(), 0.42), color=RED, stroke_width=2)
                r = T(f"{K.max() / km:.1f} 倍", 32, RED, weight=BOLD).move_to(ax.c2p(24, 0.34))
                return m, M, r
            m1, M1, r1 = marks(axe, KE, GREEN)
            m2, M2, r2 = marks(axb, KB, BLUE)
            self.play(FadeOut(tail), FadeOut(tl), Create(m1), Create(m2), run_time=0.7)
            self.play(Create(M1), Create(M2), run_time=0.8)
        with self.say("d4b") as d:
            self.play(FadeIn(r1), run_time=0.8)
            self.play(FadeIn(r2), run_time=0.8)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ distance / BFS
    def distance(self):
        tag = self.chapter("第一部分 · 距离")
        G = nx.random_geometric_graph(110, 0.17, seed=8)
        G = nx.convert_node_labels_to_integers(G.subgraph(max(nx.connected_components(G), key=len)).copy(), label_attribute="o")
        raw = {v: np.array(G.nodes[v]["pos"]) for v in G}
        P = np.array(list(raw.values())); lo, hi = P.min(0), P.max(0)
        pos = {v: np.array([-6.0 + 12.0 * (p[0] - lo[0]) / (hi[0] - lo[0]), -3.2 + 6.0 * (p[1] - lo[1]) / (hi[1] - lo[1]), 0]) for v, p in raw.items()}
        net = NetView(G, pos, color=MUTED, rmin=0.07, rk=0.0, eo=0.35)
        src = min(G, key=lambda v: np.linalg.norm(pos[v][:2] - np.array([-4.5, -1.5])))
        dist = nx.single_source_shortest_path_length(G, src)
        layers = {}
        for v, dd in dist.items():
            layers.setdefault(dd, []).append(v)
        cols = [GOLD, RED, VIOLET, BLUE, GREEN]
        with self.say("p1") as d:
            self.play(FadeIn(tag), FadeIn(net.group), run_time=1.2)
            a, b = src, max(dist, key=dist.get)
            path = nx.shortest_path(G, a, b)
            pl = VMobject(color=GOLD, stroke_width=5).set_points_as_corners([pos[v] for v in path])
            self.play(Create(pl), run_time=d * 0.5)
            self.play(FadeOut(pl), run_time=0.5)
        D = max(layers)
        with self.say("p2") as d:
            self.play(net.dots[src].animate.set_color(GOLD).scale(1.8), run_time=0.5)
            rt = max(0.25, (d - 1.0) / D)
            for k in range(1, D + 1):
                c = cols[k % len(cols)]
                self.play(*[net.dots[v].animate.set_color(c) for v in layers[k]],
                          *[net.edges[e].animate.set_stroke(c, opacity=0.7) for e in net.edges if dist[e[0]] + dist[e[1]] == 2 * k - 1],
                          run_time=rt)
        L = nx.average_shortest_path_length(G)
        assert 4.6 < L < 5.4, L
        with self.say("p3") as d:
            ring = VGroup(*[Circle(radius=0.17, color=WHITE, stroke_width=2).move_to(pos[v]) for v in layers[3]])
            self.play(Create(ring), run_time=0.8)
            self.play(FadeOut(ring), run_time=0.4)
            c = counter("平均路径长度", f"{L:.1f} 步", GOLD, vs=40)
            box = BackgroundRectangle(c, fill_color=BG, fill_opacity=0.9, buff=0.2)
            VGroup(box, c).to_corner(UR, buff=0.4)
            self.play(FadeIn(box), FadeIn(c), run_time=0.8)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.6)
        # branching picture: k, k^2, k^3
        k = 3
        root = Dot(ORIGIN + LEFT * 3.0, radius=0.12, color=GOLD)
        levels = [[root.get_center()]]
        objs = VGroup(root)
        lines = VGroup()
        for lvl in range(1, 4):
            r = 1.0 * lvl
            n = k ** lvl
            pts = [root.get_center() + r * np.array([np.cos(a), np.sin(a), 0]) for a in np.linspace(0, 2 * PI, n, endpoint=False) + 0.2 * lvl]
            levels.append(pts)
            for i, p in enumerate(pts):
                parent = levels[lvl - 1][i // k]
                lines.add(Line(parent, p, color=MUTED, stroke_width=1.5, stroke_opacity=0.6))
                objs.add(Dot(p, radius=0.07, color=[GOLD, RED, VIOLET, BLUE][lvl]))
        cnts = VGroup(*[MathTex(s, font_size=44, color=c) for s, c in ((r"\langle k\rangle", RED), (r"\langle k\rangle^2", VIOLET), (r"\langle k\rangle^3", BLUE))]
                      ).arrange(DOWN, buff=0.5, aligned_edge=LEFT).move_to([2.2, 0.8, 0])
        stepl = VGroup(*[T(f"第 {i} 步", 26, MUTED).next_to(cnts[i - 1], LEFT, buff=0.4) for i in (1, 2, 3)])
        with self.say("p4") as d:
            self.play(FadeIn(root, scale=2), run_time=0.8)
        with self.say("p5") as d:
            idx = 1
            for lvl in range(1, 4):
                n = k ** lvl
                seg = lines[sum(k ** j for j in range(1, lvl)): sum(k ** j for j in range(1, lvl + 1))]
                dots = objs[idx: idx + n]; idx += n
                self.play(Create(seg), FadeIn(dots), FadeIn(cnts[lvl - 1]), FadeIn(stepl[lvl - 1]), run_time=max(0.6, d * 0.25))
        f = MathTex(r"\langle d\rangle \approx", r"{\ln N", r"\over", r"\ln \langle k\rangle}", font_size=56, color=GOLD).move_to([2.6, -2.0, 0])
        with self.say("p6") as d:
            self.play(Write(f), run_time=1.4)
        with self.say("p6b") as d:
            ln1 = T("节点总数取对数", 24, INK).next_to(f, RIGHT, buff=0.4).shift(UP * 0.4)
            ln2 = T("平均度取对数", 24, INK).next_to(f, RIGHT, buff=0.4).shift(DOWN * 0.4)
            a1 = Arrow(ln1.get_left(), f[1].get_right(), buff=0.1, color=INK, stroke_width=2.5, max_tip_length_to_length_ratio=0.25)
            a2 = Arrow(ln2.get_left(), f[3].get_right(), buff=0.1, color=INK, stroke_width=2.5, max_tip_length_to_length_ratio=0.25)
            self.play(FadeIn(ln1), GrowArrow(a1), run_time=0.7)
            self.play(FadeIn(ln2), GrowArrow(a2), run_time=0.7)
        with self.say("p7") as d:
            self.play(Circumscribe(f, color=GOLD), run_time=1.2)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ clustering
    def clustering(self):
        tag = self.chapter("第一部分 · 聚集系数")
        c = np.array([-2.2, -2.2, 0])
        nb = [c + 3.6 * np.array([np.cos(a), np.sin(a), 0]) for a in np.radians([150, 115, 65, 30])]
        center = Dot(c, radius=0.22, color=GOLD)
        nd = [Dot(p, radius=0.18, color=BLUE) for p in nb]
        spokes = [Line(c, p, color=MUTED, stroke_width=4) for p in nb]
        allpairs = [(i, j) for i in range(4) for j in range(i + 1, 4)]
        ghost = {e: DashedLine(nb[e[0]], nb[e[1]], color=MUTED, stroke_width=2, dash_length=0.12).set_opacity(0.6) for e in allpairs}
        real = [(0, 1), (1, 2), (2, 3)]
        with self.say("c1") as d:
            self.play(FadeIn(tag), GrowFromCenter(center), run_time=0.8)
            self.play(*[Create(s) for s in spokes], *[GrowFromCenter(x) for x in nd], run_time=1.2)
        with self.say("c2") as d:
            self.play(LaggedStart(*[Create(g) for g in ghost.values()], lag_ratio=0.2), run_time=1.6)
            mx = counter("最多", "6 条", MUTED, vs=40).move_to([3.4, 1.2, 0])
            self.play(FadeIn(mx), run_time=0.6)
        with self.say("c3") as d:
            solid = [Line(nb[i], nb[j], color=GREEN, stroke_width=6) for i, j in real]
            self.play(LaggedStart(*[Create(s) for s in solid], lag_ratio=0.3), run_time=1.4)
            tris = [Polygon(c, nb[i], nb[j], stroke_width=0, fill_color=GREEN, fill_opacity=0.18) for i, j in real]
            self.play(*[FadeIn(t) for t in tris], run_time=0.6)
        with self.say("c3b") as d:
            f = MathTex(r"C = \frac{3}{6} = 0.5", font_size=56, color=GREEN).move_to([3.4, -0.8, 0])
            self.play(Write(f), run_time=1.0)
            fl = VGroup(T("实际的边", 22, GREEN), T("最多可能的边", 22, MUTED)).arrange(DOWN, buff=0.75).next_to(f, RIGHT, buff=0.3)
            self.play(FadeIn(fl), run_time=0.6)
        with self.say("c4") as d:
            self.play(*[Indicate(t, color=GREEN) for t in tris], run_time=1.2)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ centrality
    def centrality(self):
        tag = self.chapter("第二部分 · 中心性")
        rng = random.Random(5)
        G = nx.Graph()
        L = nx.gnm_random_graph(10, 24, seed=3)
        R = nx.gnm_random_graph(10, 24, seed=4)
        G.add_edges_from(L.edges())
        G.add_edges_from((u + 10, v + 10) for u, v in R.edges())
        b = 20
        G.add_edge(0, b)
        G.add_edge(b, 10)
        assert nx.is_connected(G) and G.degree(b) == 2
        pl = fit(nx.kamada_kawai_layout(L), (-6.2, -2.4, -2.2, 2.0))
        pr = fit(nx.kamada_kawai_layout(R), (2.4, 6.2, -2.2, 2.0))
        pos = {**pl, **{v + 10: p for v, p in pr.items()}, b: np.array([0, -0.1, 0])}
        net = NetView(G, pos, color=BLUE, rmin=0.09, rk=0.0, eo=0.45)
        with self.say("z1") as d:
            self.play(FadeIn(tag), FadeIn(net.group), run_time=d * 0.5)
        deg = dict(G.degree())
        top = [max(range(10), key=deg.get), max(range(10, 20), key=deg.get)]
        with self.say("z2") as d:
            self.play(*[net.dots[v].animate.scale(0.6 + 0.25 * deg[v]) for v in G], run_time=1.2)
            self.play(*[Indicate(net.dots[v], color=GOLD, scale_factor=1.3) for v in top], run_time=1.0)
            self.play(*[net.dots[v].animate.scale(1 / (0.6 + 0.25 * deg[v])) for v in G], run_time=0.8)
        with self.say("z3") as d:
            self.play(net.dots[b].animate.set_color(GOLD).scale(2.0), run_time=0.8)
            self.play(nv_edge(net, 0, b).animate.set_stroke(GOLD, width=4, opacity=1), nv_edge(net, b, 10).animate.set_stroke(GOLD, width=4, opacity=1), run_time=0.8)
        bc = nx.betweenness_centrality(G)
        with self.say("z4") as d:
            pairs = [(rng.randrange(10), rng.randrange(10, 20)) for _ in range(6)]
            for s, t in pairs:
                p = nx.shortest_path(G, s, t)
                pth = VMobject(color=RED, stroke_width=4).set_points_as_corners([pos[v] for v in p])
                self.play(Create(pth), run_time=0.35)
                self.play(FadeOut(pth), run_time=0.2)
        with self.say("z4b") as d:
            self.play(net.dots[b].animate.scale(1.4), run_time=0.8)
            lab = T("瓶颈", 30, GOLD, weight=BOLD).next_to(net.dots[b], DOWN, buff=0.3)
            self.play(FadeIn(lab), run_time=0.6)
        with self.say("z5") as d:
            self.play(Circumscribe(net.dots[b], color=GOLD, shape=Circle), run_time=1.4)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.8)
        with self.say("z6") as d:
            self.clip_on("yt_tractography_usc.mp4", "center", "视频：USC Stevens Neuroimaging and Informatics Institute · YouTube", start=30)
        self.clip_off()
        self.play(FadeOut(tag), run_time=0.5)

    # ------------------------------------------------------------------ ER
    def er(self):
        tag = self.chapter("第三部分 · 随机图")
        N = 60
        rng = random.Random(2)
        Gf = nx.gnm_random_graph(N, int(6 * N / 2), seed=11)
        order = list(Gf.edges()); rng.shuffle(order)
        base = nx.spring_layout(Gf, seed=2, k=0.5, iterations=200)
        xs = [-5.1, -1.7, 1.7, 5.1]
        ks = [0.6, 1.0, 2.0, 6.0]
        panels = []
        for x, k in zip(xs, ks):
            H = nx.empty_graph(N); H.add_edges_from(order[: int(k * N / 2)])
            pos = fit(base, (x - 1.5, x + 1.5, -1.9, 1.3))
            g = set(max(nx.connected_components(H), key=len))
            big = len(g) > 0.2 * N
            dots = VGroup(*[Dot(pos[v], radius=0.05, color=GOLD if (big and v in g) else MUTED) for v in H])
            eds = VGroup(*[Line(pos[u], pos[v], stroke_width=1.1, color=GOLD if (big and u in g) else MUTED, stroke_opacity=0.6) for u, v in H.edges()])
            lab = MathTex(r"\langle k\rangle=%g" % k, font_size=34, color=INK).move_to([x, 2.0, 0])
            panels.append((VGroup(eds, dots), lab))
        with self.say("e0") as d:
            self.play(FadeIn(tag), run_time=0.4)
            self.clip_on("yt_erdos_trailer.mp4", "center", "视频：Zala Films · YouTube", start=3)
        self.clip_off()
        with self.say("e1") as d:
            q = T("参照：完全随机时，指标是多少", 36, INK)
            self.play(FadeIn(q), run_time=1.0)
        with self.say("e2") as d:
            self.play(FadeOut(q), run_time=0.5)
            pr = MathTex(r"p", font_size=40, color=GOLD).move_to([0, -3.0, 0])
            demo_n = VGroup(*[Dot([-1.2 + 0.6 * i, -2.3, 0], radius=0.08, color=MUTED) for i in range(5)])
            self.play(FadeIn(demo_n), run_time=0.5)
            prs = [(0, 2), (1, 4), (0, 3), (2, 3)]
            arcs = [ArcBetweenPoints(demo_n[i].get_center(), demo_n[j].get_center(), angle=-1.0, color=GOLD, stroke_width=2) for i, j in prs]
            self.play(LaggedStart(*[Create(a) for a in arcs], lag_ratio=0.3), FadeIn(pr), run_time=1.6)
            self.play(FadeOut(VGroup(demo_n, *arcs, pr)), run_time=0.5)
        with self.say("e3") as d:
            self.play(FadeIn(panels[0][1]), FadeIn(panels[0][0]), run_time=1.2)
        with self.say("e4") as d:
            self.play(FadeIn(panels[1][1]), FadeIn(panels[1][0]), run_time=1.0)
            self.play(FadeIn(panels[2][1]), FadeIn(panels[2][0]), run_time=1.0)
        with self.say("e5") as d:
            self.play(FadeIn(panels[3][1]), FadeIn(panels[3][0]), run_time=1.2)
            lnN = MathTex(r"\ln %d \approx %.1f" % (N, np.log(N)), font_size=30, color=MUTED).next_to(panels[3][0], DOWN, buff=0.3)
            self.play(FadeIn(lnN), run_time=0.6)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.6)
        # Poisson degree distribution of a large ER graph
        Gb = nx.gnm_random_graph(3000, 9000, seed=1)
        K = np.array([d_ for _, d_ in Gb.degree()])
        ax = Axes(x_range=[0, 16, 2], y_range=[0, 0.2, 0.1], x_length=8, y_length=4,
                  axis_config={"color": MUTED, "include_tip": False, "font_size": 22},
                  x_axis_config={"numbers_to_include": list(range(0, 17, 4))},
                  y_axis_config={"numbers_to_include": [0, 0.1, 0.2]}).shift(DOWN * 0.4)
        xl = T("度", 22, MUTED).next_to(ax.x_axis, DOWN, buff=0.35)
        bs = bars(ax, K, MUTED, w=0.8)
        from math import factorial
        pois = ax.plot_line_graph(list(range(0, 17)), [np.exp(-6) * 6 ** k / factorial(k) for k in range(17)],
                                  line_color=GOLD, add_vertex_dots=True, vertex_dot_radius=0.06, stroke_width=4)
        yl_ = T("概率", 22, MUTED).rotate(PI / 2).next_to(ax.y_axis, LEFT, buff=0.35)
        with self.say("e6") as d:
            self.play(Create(ax), FadeIn(xl), FadeIn(yl_), run_time=0.8)
            self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bs], lag_ratio=0.05), run_time=1.4)
            self.play(Create(pois), run_time=1.2)
        with self.say("e6b") as d:
            self.play(Indicate(pois, color=GOLD), run_time=1.2)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ real vs random
    def real_vs_random(self):
        tag = self.chapter("第三部分 · 真实网络与随机图")
        users = counter("用户", "约 1.8 亿", INK, vs=44).move_to(UP * 1.2)
        with self.say("v1") as d:
            self.play(FadeIn(tag), FadeIn(users), run_time=1.0)
            rng = np.random.default_rng(2)
            sky = VGroup(*[Dot([rng.uniform(-6.5, 6.5), rng.uniform(-3.4, 0.2), 0], radius=0.025, color=BLUE).set_opacity(rng.uniform(0.3, 0.9)) for _ in range(300)])
            self.play(FadeIn(sky, lag_ratio=0.003), run_time=1.4)
        self.play(FadeOut(sky), FadeOut(users), run_time=0.6)
        # path length: linear bars
        hdr = VGroup(T("真实网络", 26, BLUE), T("随机图", 26, MUTED)).arrange(DOWN, buff=0.5, aligned_edge=RIGHT)
        def pair_bars(y, a, b, scale, title, la, lb):
            t = T(title, 28, INK).move_to([-4.2, y + 0.9, 0], aligned_edge=LEFT)
            r1 = Rectangle(width=a * scale, height=0.4, fill_color=BLUE, fill_opacity=0.9, stroke_width=0).move_to([-2.4, y + 0.3, 0], aligned_edge=LEFT)
            r2 = Rectangle(width=b * scale, height=0.4, fill_color=MUTED, fill_opacity=0.9, stroke_width=0).move_to([-2.4, y - 0.3, 0], aligned_edge=LEFT)
            n1 = T("真实", 22, BLUE).next_to(r1, LEFT, buff=0.2).align_to([-2.6, 0, 0], RIGHT)
            n2 = T("随机", 22, MUTED).next_to(r2, LEFT, buff=0.2).align_to([-2.6, 0, 0], RIGHT)
            v1 = T(la, 26, BLUE, weight=BOLD).next_to(r1, RIGHT, buff=0.2)
            v2 = T(lb, 26, MUTED, weight=BOLD).next_to(r2, RIGHT, buff=0.2)
            return t, r1, r2, VGroup(n1, n2), v1, v2
        t, r1, r2, ns, v1, v2 = pair_bars(1.4, 6.6, 7.0, 0.8, "平均路径长度", "6.6", "约 7")
        with self.say("v2") as d:
            self.play(FadeIn(t), FadeIn(ns), run_time=0.6)
            self.play(GrowFromEdge(r1, LEFT), GrowFromEdge(r2, LEFT), run_time=1.0)
            self.play(FadeIn(v1), FadeIn(v2), run_time=0.6)
        # clustering on a log axis 1e-8 .. 1
        y = -1.6
        ax = NumberLine(x_range=[-8, 0, 1], length=8.4, color=MUTED, include_numbers=False).move_to([1.8, y - 0.85, 0])
        ticks = VGroup(*[MathTex(r"10^{%d}" % e, font_size=24, color=MUTED).next_to(ax.n2p(e), DOWN, buff=0.15) for e in range(-8, 1, 2)])
        t3 = T("聚集系数（对数刻度）", 28, INK).move_to([-4.2, y + 1.5, 0], aligned_edge=LEFT)
        xr = ax.n2p(np.log10(0.11))[0]
        xe = ax.n2p(np.log10(8e-8))[0]
        x0 = ax.n2p(-8)[0]
        c1 = Rectangle(width=xr - x0, height=0.4, fill_color=BLUE, fill_opacity=0.9, stroke_width=0).move_to([x0, y + 0.3, 0], aligned_edge=LEFT)
        c2 = Rectangle(width=max(xe - x0, 0.03), height=0.4, fill_color=MUTED, fill_opacity=0.9, stroke_width=0).move_to([x0, y - 0.3, 0], aligned_edge=LEFT)
        cv1 = T("0.11", 26, BLUE, weight=BOLD).next_to(c1, RIGHT, buff=0.2)
        cv2 = MathTex(r"8\times10^{-8}", font_size=32, color=MUTED).next_to(c2, RIGHT, buff=0.2)
        n3 = VGroup(T("真实", 22, BLUE).move_to([x0 - 0.5, y + 0.3, 0]), T("随机", 22, MUTED).move_to([x0 - 0.5, y - 0.3, 0]))
        with self.say("v3") as d:
            self.play(FadeIn(t3), Create(ax), FadeIn(ticks), FadeIn(n3), run_time=1.0)
            self.play(GrowFromEdge(c1, LEFT), FadeIn(c2), run_time=1.2)
            self.play(FadeIn(cv1), FadeIn(cv2), run_time=0.6)
        with self.say("v3b") as d:
            br = BraceBetweenPoints([xe, y + 0.6, 0], [xr, y + 0.6, 0], UP, color=GOLD)
            bl = T("约 6 个数量级", 26, GOLD).next_to(br, UP, buff=0.05)
            self.play(GrowFromCenter(br), FadeIn(bl), run_time=0.8)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.6)
        # degree distributions again: callback to the hook pair
        ve, vb = self.views
        ve2 = NetView(GE, fit(nx.kamada_kawai_layout(GE), (-6.4, -0.8, -2.7, 2.2)), color=MUTED, rmin=0.04, rk=0.03, eo=0.35)
        vb2 = NetView(GB, fit(nx.kamada_kawai_layout(GB), (0.8, 6.4, -2.7, 2.2)), color=BLUE, rmin=0.04, rk=0.03, eo=0.35)
        la = T("随机图", 28, MUTED).move_to([-3.6, 2.75, 0])
        lb = T("有枢纽的网络", 28, BLUE).move_to([3.6, 2.75, 0])
        with self.say("v4") as d:
            self.play(FadeIn(ve2.group), FadeIn(la), run_time=1.0)
            self.play(FadeIn(vb2.group), FadeIn(lb), run_time=1.0)
        with self.say("v5") as d:
            self.play(ve2.group.animate.set_opacity(0.25), run_time=0.8)
            dev = T("偏离零模型 → 值得解释", 34, GOLD, weight=BOLD).move_to([0, -3.3, 0])
            self.play(FadeIn(dev, shift=UP * 0.2), run_time=0.8)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ recap
    def recap(self):
        items = [("r2", BLUE, "看完整的度分布，不只看平均度"),
                 ("r3", GOLD, "距离、聚集、中心性：各回答一个问题"),
                 ("r4", GREEN, "和零模型比，偏离随机才有意义")]
        head, rows = recap_rows(items)
        with self.say("r1") as d:
            self.play(Write(head), run_time=0.8)
        for (k, _, _), row in zip(items, rows):
            with self.say(k) as d:
                self.play(FadeIn(row, shift=RIGHT * 0.3), run_time=0.8)
        self.wait(0.8)
        self.play(FadeOut(rows), FadeOut(head), run_time=0.6)
        with self.say("r5") as d:
            self.clip_on("er_demo.mp4", "full", "本站交互演示：ER 随机图与巨连通分支", start=0.3)
            if d < 12.2:
                self.wait(12.3 - d)
        self.clip_off()
        self.wait(1.0)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=1.0)
