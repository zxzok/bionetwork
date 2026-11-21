"""Animated explainer: 社团结构 (weak ties, modularity, Girvan-Newman, Louvain/Leiden, detectability, biomedical modules)."""
import networkx as nx
import numpy as np
from networkx.algorithms.community import louvain_communities, modularity

from common import *  # noqa: F401,F403
from ahelp import NetView, counter, fit, nv_edge, recap_rows, parts_slide

TITLE = "社团结构：网络里的抱团与分组"

KAR = nx.karate_club_graph()
CLUB = {v: KAR.nodes[v]["club"] == "Mr. Hi" for v in KAR}


def gn_split(G):
    H = G.copy(); removed = []
    while nx.number_connected_components(H) == 1:
        eb = nx.edge_betweenness_centrality(H)
        e = max(eb, key=eb.get)
        H.remove_edge(*e); removed.append(e)
    side = nx.node_connected_component(H, 0)
    wrong = [v for v in G if (v in side) != CLUB[v]]
    return removed, side, wrong


GN_REMOVED, GN_SIDE, GN_WRONG = gn_split(KAR)
assert len(GN_WRONG) == 2

ER = nx.gnm_random_graph(100, 200, seed=0)
ER = nx.convert_node_labels_to_integers(ER.subgraph(max(nx.connected_components(ER), key=len)).copy())
ER_P = louvain_communities(ER, seed=1)
ER_Q = modularity(ER, ER_P)
assert 0.45 < ER_Q < 0.55

LINES = {
    # hook: karate club
    "h1": "上世纪七十年代，一位人类学家观察了一个大学空手道俱乐部：三十四名成员，七十八对朋友关系。",
    "h1b": "画面上，每个点是一名成员，每条线表示两个人是朋友。",
    "h2": "观察期间，教练和俱乐部的管理者闹翻了。俱乐部最终分裂成了两派。",
    "h3": "我们想做的，是只看谁和谁是朋友，就事先猜出每个人会站到哪一边。",
    "h4": "后来人们发现，单凭朋友关系，算法就能把两派分得八九不离十。蓝色是教练这一派，红色是管理者那一派。",
    "h5": "【慢】网络里这种内部抱团、彼此稀疏的节点群，就叫社团。",
    # parts
    "q0": "这一期分三部分来讲。",
    "q1": "第一部分，社团为什么存在，以及把网络分成社团有多难。",
    "q2": "第二部分，怎样找社团：模块度，和几种常用的算法。",
    "q3": "第三部分，找到的社团可不可信，以及它在生物医学里的用处。",
    # weak ties
    "g1": "先看第一部分。1973年，社会学家格兰诺维特，研究人们是怎样找到工作的。",
    "g1b": "他发现，帮上忙的，多是普通熟人，而不是亲密朋友。",
    "g1c": "画面上，左边蓝色圈子里，金色的这个人是你；右边绿色圈子里有一份工作的消息，沿着这条虚线，也就是一条熟人关系，传了过来。",
    "g2": "原因在结构里。如果两个人都是你的好朋友，他们很可能也互相认识。所以强关系，总是嵌在三角形里。",
    "g3": "这样一来，亲密朋友往往在同一个圈子里，知道的消息高度重叠。",
    "g4": "而熟人更可能是连接不同圈子的桥，能带来圈子外的新信息。",
    "g5": "【慢】于是网络呈现出这样的图景：内部紧密的社团，靠少数几条弱关系相互连接。",
    # partitions
    "n1": "怎样把节点分成社团。最直接的想法，是把所有分法都试一遍。你看，五个节点，就能换出很多种分法。",
    "n2": "下面这张图，横轴是节点数，纵轴是分法的数目，用对数刻度。灰线是二的节点数次方，金线是全部分法的数目。",
    "n2b": "【慢】分法的数目，增长得比指数还快：十个节点，有十一万多种分法；二十个节点，就超过五十万亿种。",
    "n3": "所以只能靠一个打分标准，再加上聪明的搜索。",
    # modularity
    "m1": "下面进入第二部分：怎样找社团。最常用的打分标准叫模块度。思路是：社团内部的边，应该比随机情况下预期的更多。",
    "m2": "随机预期这样算：保持每个节点的度不变，把边全部打乱重连。两个节点之间预期的边数，正比于它们度的乘积。",
    "m3": "【慢】模块度，就是实际落在社团内部的边的比例，减去随机情况下，预期落在内部的比例。",
    "m3b": "看公式：绿色这一项，是社团内部的边数，除以总边数；金色这一项，是社团里所有节点的度加起来、除以总度数，再平方，也就是随机情况下的预期。",
    "m4": "看一个例子：两个三角形，中间一条边相连。按两个三角形来分，模块度约为零点三六。",
    "m5": "全部放在一组，模块度是零；每个点单独一组，模块度是负的。",
    "m6": "但是要小心：在一张完全随机的网络上，也能找到模块度不低的划分。",
    "m7": "这张随机网络没有任何真实的社团，算法照样找到了模块度接近零点五的划分。所以模块度，必须和随机网络比较。",
    # Girvan-Newman
    "b1": "怎样找到好的划分。一种思路是反过来：一条一条拆掉社团之间的桥。",
    "b2": "社团之间边很少，两边节点之间的最短路径，都得挤过这几条边。经过一条边的最短路径数，叫边介数。画面上，越红、越粗的边，边介数越高。",
    "b3": "每次删掉边介数最高的那条边，重新计算，再删。",
    "b4": "空手道俱乐部的网络很快裂成了两块。和真实的两派一比，只有画了圈的两个人，被分到了另一侧。",
    "b5": "缺点是每删一条边都要重算一遍，只适合几千个节点以内的网络。",
    # Louvain / Leiden
    "v1": "大网络常用另一种更快的办法。开始时，每个节点自成一组，所以颜色各不相同。",
    "v2": "依次检查每个节点：如果把它搬到邻居的组里，能让模块度增加，就搬过去。你看右边的模块度，一路涨了上来。",
    "v3": "等没有节点再动，就把每个组压缩成一个大节点，在缩小的网络上重复。",
    "v4": "这就是卢万算法。几百万个节点的网络，它也能很快处理。",
    "v5": "不过，它可能产生内部连接很差、甚至断开的社团。后来的莱顿算法加了一步细化，保证每个社团都是连通的。",
    # detectability
    "d1": "最后是第三部分：找到的社团可不可信。先看一种情况：社团真的存在，但信号很弱。",
    "d2": "我们用随机块模型来生成网络：先把节点分成两组，组内连边的机会大，组间连边的机会小。两个参数，c_in管组内，c_out管组间，平均度就是它们的平均值。",
    "d2a": "左边，c_in是九点五，c_out是零点五，平均度是五。两个社团一目了然。",
    "d3": "右边，组间连边变多了：c_in是七点二，c_out是二点八，平均度还是五。",
    "d3b": "折算到每个节点，平均大约三点六条组内的边、一点四条组间的边。组内仍是组间的两倍多，两个社团却已经混成一团。",
    "d4": "【慢】理论证明：组内和组间的差距低于某个阈值时，任何算法都无法比随机猜测做得更好。",
    "d4b": "公式左边，是c_in和c_out的差；右边，是组数乘以平均度的平方根。右边这个例子，差是四点四，阈值是二倍根号五，约四点四七，正好落在阈值以下。",
    "d5": "所以，算法没找到社团，不等于网络里没有社团结构。不是算法不够好，而是信息本身不够。",
    # biomedical
    "s1": "在生物医学里，社团往往对应功能单元，比如蛋白质网络里的复合物和通路。",
    "s2": "在静息态脑功能网络中，社团划分和视觉、躯体运动、默认模式等已知的功能系统高度对应。",
    "s2b": "静息态，就是人躺在扫描仪里安静休息、不做任务的状态。",
    "s3": "单细胞分析里，研究者先把相似的细胞连成近邻图，再运行莱顿或卢万算法，来定义细胞簇。",
    "s4": "这时，分辨率参数直接决定分出几类。调低一些，得到四个大类。",
    "s4b": "调高一些，大类被拆成了十三个小类。",
    "s5": "【慢】所以报告社团时，要检验它是否显著、是否稳定，并写清用了什么参数。",
    # recap
    "r1": "好，我们来总结一下。",
    "r2": "第一，社团是内部紧密、彼此稀疏的节点群；模块度把它和随机预期作比较。",
    "r3": "第二，随机网络也会被分出社团，所以结果要做显著性和稳定性检验。",
    "r4": "第三，信号太弱时，社团无法被检测；参数的选择，决定了你看到的尺度。",
    "r5": "这个专题的知识页面里，有画面上的这个交互演示。依次点击按钮，可以比较全部归为一组、随机分组、贪心优化和真实分裂的模块度。",
}

PAL = [BLUE, GOLD, GREEN, VIOLET, RED, "#4fc3d1", "#f08bd0", "#c0d84f", "#ff9f5a", "#8fa8ff"]


class Episode(Narrated):
    LINES = LINES

    def construct(self):
        self.hook()
        parts_slide(self, "这一期分三部分", ["一  社团为什么存在，划分有多难", "二  怎样找社团：模块度与算法", "三  结果可信吗：可检测性与应用"])
        self.weak_ties()
        self.partitions()
        self.modularity_ch()
        self.girvan_newman()
        self.louvain()
        self.detectability()
        self.biomed()
        self.recap()

    # ------------------------------------------------------------------ hook
    def hook(self):
        G = KAR
        pos = fit(nx.kamada_kawai_layout(G), (-5.8, 5.8, -3.3, 2.9))
        self.kpos = pos
        net = NetView(G, pos, color=MUTED, rmin=0.08, rk=0.03, eo=0.45)
        c1 = counter("成员", "34", INK, vs=36).to_corner(UR, buff=0.4)
        c2 = counter("朋友关系", "78", INK, vs=36).next_to(c1, DOWN, buff=0.3)
        with self.say("h1") as d:
            self.play(LaggedStart(*[GrowFromCenter(x) for x in net.dots.values()], lag_ratio=0.03), run_time=d * 0.35)
            self.play(FadeIn(c1), FadeIn(c2), run_time=0.8)
        with self.say("h1b") as d:
            self.play(LaggedStart(*[Create(e) for e in net.edges.values()], lag_ratio=0.01), run_time=d * 0.6)
        with self.say("h2") as d:
            self.play(net.dots[0].animate.set_color(BLUE).scale(1.5), net.dots[33].animate.set_color(RED).scale(1.5), run_time=1.0)
            l0 = T("教练", 24, BLUE).next_to(net.dots[0], DOWN, buff=0.15)
            l33 = T("管理者", 24, RED).next_to(net.dots[33], UP, buff=0.15)
            self.play(FadeIn(l0), FadeIn(l33), run_time=0.6)
            bolt = Line(pos[0], pos[33], color=GOLD, stroke_width=4).set_opacity(0.0)
            self.play(Flash(net.dots[0], color=GOLD), Flash(net.dots[33], color=GOLD), run_time=0.8)
        with self.say("h3") as d:
            qs = VGroup(*[T("?", 22, GOLD, weight=BOLD).next_to(net.dots[v], UR, buff=0.0) for v in G if v not in (0, 33)])
            self.play(LaggedStart(*[FadeIn(q, scale=1.5) for q in qs], lag_ratio=0.03), run_time=d * 0.5)
        with self.say("h4") as d:
            self.play(FadeOut(qs), run_time=0.5)
            self.play(*[net.dots[v].animate.set_color(BLUE if CLUB[v] else RED) for v in G],
                      *[e.animate.set_stroke(BLUE if (CLUB[u] and CLUB[w]) else RED if (not CLUB[u] and not CLUB[w]) else MUTED,
                                             opacity=0.55 if CLUB[u] == CLUB[w] else 0.25) for (u, w), e in net.edges.items()], run_time=1.6)
        with self.say("h5") as d:
            self.play(*[Indicate(VGroup(*[net.dots[v] for v in KAR if CLUB[v] == side]), color=c, scale_factor=1.05)
                        for side, c in ((True, BLUE), (False, RED))], run_time=1.4)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ weak ties
    def weak_ties(self):
        tag = self.chapter("第一部分 · 弱关系与社团")
        cA, cB = np.array([-3.4, -0.2, 0]), np.array([3.4, -0.2, 0])
        pa = [cA + 1.4 * np.array([np.cos(a), np.sin(a), 0]) for a in np.linspace(0, 2 * PI, 6, endpoint=False) + 0.3]
        pb = [cB + 1.4 * np.array([np.cos(a), np.sin(a), 0]) for a in np.linspace(0, 2 * PI, 6, endpoint=False) + 0.2]
        you = pa[0]
        da = [Dot(p, radius=0.14, color=BLUE) for p in pa]
        db = [Dot(p, radius=0.14, color=GREEN) for p in pb]
        da[0].set_color(GOLD).scale(1.3)
        sa = [(0, 1), (0, 5), (1, 5), (1, 2), (2, 3), (3, 4), (4, 5), (2, 5), (0, 2)]
        sb = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0), (0, 2), (3, 5), (1, 4)]
        la = [Line(pa[i], pa[j], color=BLUE, stroke_width=6, stroke_opacity=0.7) for i, j in sa]
        lb = [Line(pb[i], pb[j], color=GREEN, stroke_width=6, stroke_opacity=0.7) for i, j in sb]
        weak = DashedLine(pa[0], pb[3], color=GOLD, stroke_width=2.5)
        yr = T("1973", 28, MUTED).to_corner(UR, buff=0.5)
        job = VGroup(RoundedRectangle(width=1.0, height=0.7, corner_radius=0.1, color=GOLD, fill_opacity=0.2), T("工作", 22, GOLD)).move_to(pb[3] + RIGHT * 1.3)
        with self.say("g1") as d:
            self.play(FadeIn(tag), FadeIn(yr), run_time=1.0)
        with self.say("g1b") as d:
            self.clip_on("yt_granovetter_stanford.mp4", "center", "视频：Stanford Center on Poverty and Inequality · YouTube", start=20)
        self.clip_off()
        with self.say("g1c") as d:
            self.play(*[GrowFromCenter(x) for x in da + db], run_time=1.0)
            self.play(*[Create(l) for l in la + lb], run_time=1.2)
            self.play(Create(weak), FadeIn(job), run_time=1.0)
            pkt = Dot(pb[3], radius=0.1, color=GOLD)
            self.play(MoveAlongPath(pkt, Line(pb[3], pa[0])), run_time=1.2)
            self.remove(pkt)
        with self.say("g2") as d:
            tri = Polygon(pa[0], pa[1], pa[5], stroke_width=0, fill_color=BLUE, fill_opacity=0.35)
            self.play(Indicate(la[0], color=GOLD), Indicate(la[1], color=GOLD), run_time=0.9)
            self.play(Create(la[2].copy().set_color(GOLD)), FadeIn(tri), run_time=0.9)
        with self.say("g3") as d:
            bub = Circle(radius=1.85, color=BLUE, stroke_width=3).move_to(cA)
            self.play(Create(bub), run_time=1.0)
        with self.say("g4") as d:
            self.play(weak.animate.set_stroke(width=5), Indicate(weak, color=GOLD), run_time=1.2)
            br = T("桥", 30, GOLD, weight=BOLD).next_to(weak.get_center(), UP, buff=0.25)
            self.play(FadeIn(br), run_time=0.6)
        with self.say("g5") as d:
            bubB = Circle(radius=1.85, color=GREEN, stroke_width=3).move_to(cB)
            self.play(Create(bubB), run_time=1.0)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ partitions
    def partitions(self):
        tag = self.chapter("第一部分 · 分法有多少")
        n = 5
        pts = [np.array([-1.6 + 0.8 * i, 1.6, 0]) for i in range(n)]
        dots = VGroup(*[Dot(p, radius=0.14, color=INK) for p in pts])
        parts = [[0, 0, 1, 1, 2], [0, 1, 0, 1, 1], [0, 0, 0, 1, 1], [0, 1, 2, 3, 4], [0, 0, 1, 2, 2], [0, 1, 1, 1, 0]]
        with self.say("n1") as d:
            self.play(FadeIn(tag), FadeIn(dots), run_time=0.8)
            for pp in parts:
                self.play(*[dots[i].animate.set_color(PAL[c]) for i, c in enumerate(pp)], run_time=0.35)
                self.wait(0.15)
        ax = Axes(x_range=[0, 22, 5], y_range=[0, 15, 5], x_length=8, y_length=3.6,
                  axis_config={"color": MUTED, "include_tip": False, "font_size": 22},
                  x_axis_config={"numbers_to_include": [5, 10, 15, 20]}).move_to([0, -1.4, 0])
        yt = VGroup(*[MathTex(r"10^{%d}" % e, font_size=24, color=MUTED).next_to(ax.c2p(0, e), LEFT, buff=0.12) for e in (5, 10, 15)])
        xl = T("节点数", 22, MUTED).next_to(ax.x_axis, DOWN, buff=0.35)
        bell = [1, 1]
        from math import comb
        for k in range(1, 22):
            bell.append(sum(comb(k, j) * bell[j] for j in range(k + 1)))
        # bell[n] = B_n
        assert bell[10] == 115975
        ns = list(range(1, 22))
        curve = ax.plot_line_graph(ns, [np.log10(bell[i]) for i in ns], line_color=GOLD, vertex_dot_radius=0.05, stroke_width=4)
        exp2 = ax.plot_line_graph(ns, [i * np.log10(2) for i in ns], line_color=MUTED, add_vertex_dots=False, stroke_width=3)
        el = MathTex(r"2^N", font_size=32, color=MUTED).next_to(ax.c2p(21, 21 * np.log10(2)), RIGHT, buff=0.1)
        with self.say("n2") as d:
            self.play(dots.animate.shift(UP * 0.8).scale(0.8), Create(ax), FadeIn(yt), FadeIn(xl), run_time=1.0)
            self.play(Create(exp2), FadeIn(el), run_time=0.8)
            self.play(Create(curve), run_time=d * 0.3, rate_func=linear)
        with self.say("n2b") as d:
            b10 = T("115975", 26, GOLD, weight=BOLD).next_to(ax.c2p(10, np.log10(bell[10])), UL, buff=0.1)
            b20 = MathTex(r"5.2\times10^{13}", font_size=34, color=GOLD).next_to(ax.c2p(20, np.log10(bell[20])), UL, buff=0.1)
            self.play(FadeIn(b10), run_time=0.5)
            self.play(FadeIn(b20), run_time=0.5)
        with self.say("n3") as d:
            self.play(Indicate(curve, color=GOLD), run_time=1.2)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ modularity
    def modularity_ch(self):
        tag = self.chapter("第二部分 · 模块度")
        f = MathTex(r"Q=\sum_c\Big[", r"\frac{l_c}{m}", r"-", r"\Big(\frac{d_c}{2m}\Big)^2", r"\Big]", font_size=54, color=INK).move_to(UP * 1.6)
        with self.say("m1") as d:
            self.play(FadeIn(tag), run_time=0.5)
            a, b = Dot(LEFT * 1.2 + DOWN * 1.0, radius=0.16, color=BLUE), Dot(RIGHT * 1.2 + DOWN * 1.0, radius=0.16, color=BLUE)
            act = Line(a.get_center(), b.get_center(), color=INK, stroke_width=4)
            self.play(FadeIn(a), FadeIn(b), Create(act), run_time=1.0)
            vs = T("实际  vs  随机预期", 30, INK).move_to(DOWN * 2.2)
            self.play(FadeIn(vs), run_time=0.8)
        with self.say("m2") as d:
            # stubs: degree 3 and degree 2
            sa = VGroup(*[Line(a.get_center(), a.get_center() + 0.6 * np.array([np.cos(t), np.sin(t), 0]), color=GOLD, stroke_width=3) for t in (2.0, 3.1, 4.2)])
            sb = VGroup(*[Line(b.get_center(), b.get_center() + 0.6 * np.array([np.cos(t), np.sin(t), 0]), color=GOLD, stroke_width=3) for t in (0.6, -0.6)])
            self.play(FadeOut(act), Create(sa), Create(sb), run_time=1.0)
            pe = MathTex(r"\frac{k_i k_j}{2m}", font_size=50, color=GOLD).move_to(UP * 0.4)
            self.play(Write(pe), run_time=1.0)
            self.play(Wiggle(sa), Wiggle(sb), run_time=1.0)
        with self.say("m3") as d:
            self.play(FadeOut(VGroup(a, b, sa, sb, vs, pe)), run_time=0.5)
            self.play(Write(f), run_time=1.4)
        with self.say("m3b") as d:
            self.play(f[1].animate.set_color(GREEN), run_time=0.5)
            t1_ = T("社团内部边数 ÷ 总边数", 24, GREEN).next_to(f[1], DOWN, buff=0.5).shift(LEFT * 1.6)
            self.play(FadeIn(t1_), run_time=0.5)
            self.wait(d * 0.2)
            self.play(f[3].animate.set_color(GOLD), run_time=0.5)
            t2_ = T("随机情况下的预期", 24, GOLD).next_to(f[3], DOWN, buff=0.9).shift(RIGHT * 1.0)
            self.play(FadeIn(t2_), run_time=0.5)
        self.play(FadeOut(t1_), FadeOut(t2_), run_time=0.4)
        # two triangles example
        P = [np.array(p) for p in ([-3.2, -0.6, 0], [-4.4, -2.2, 0], [-2.0, -2.2, 0], [2.0, -0.6, 0], [0.8, -2.2, 0], [3.2, -2.2, 0])]
        P = [p + RIGHT * 0.6 for p in P]
        E = [(0, 1), (1, 2), (0, 2), (3, 4), (4, 5), (3, 5), (0, 3)]
        G = nx.Graph(E)
        dots = [Dot(p, radius=0.16, color=INK) for p in P]
        lines = [Line(P[u], P[v], color=MUTED, stroke_width=4) for u, v in E]
        q2 = modularity(G, [{0, 1, 2}, {3, 4, 5}])
        q1 = modularity(G, [set(range(6))])
        q6 = modularity(G, [{i} for i in range(6)])
        qbox = counter("Q", f"{q2:.2f}", GOLD, vs=44).move_to([5.2, -1.4, 0])
        with self.say("m4") as d:
            self.play(f.animate.scale(0.75).move_to(UP * 2.2), run_time=0.6)
            self.play(*[GrowFromCenter(x) for x in dots], *[Create(l) for l in lines], run_time=1.0)
            self.play(*[dots[i].animate.set_color(BLUE if i < 3 else GREEN) for i in range(6)], run_time=0.8)
            self.play(FadeIn(qbox), run_time=0.6)
        with self.say("m5") as d:
            self.play(*[x.animate.set_color(GOLD) for x in dots], Transform(qbox[1], T(f"{q1:.0f}", 44, GOLD, weight=BOLD).move_to(qbox[1])), run_time=1.0)
            self.wait(0.5)
            self.play(*[x.animate.set_color(PAL[i]) for i, x in enumerate(dots)],
                      Transform(qbox[1], T(f"{q6:.2f}".replace("-", "−"), 44, RED, weight=BOLD).move_to(qbox[1])), run_time=1.0)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.6)
        # random network with "communities"
        pos = fit(nx.spring_layout(ER, seed=2, iterations=200), (-6.2, 2.4, -3.3, 2.9))
        net = NetView(ER, pos, color=MUTED, rmin=0.07, rk=0, eo=0.4)
        with self.say("m6") as d:
            self.play(FadeIn(net.group), run_time=1.0)
            lab = T("完全随机", 30, MUTED).move_to([4.6, 1.6, 0])
            self.play(FadeIn(lab), run_time=0.6)
        comm = {v: i for i, c in enumerate(ER_P) for v in c}
        with self.say("m7") as d:
            self.play(*[net.dots[v].animate.set_color(PAL[comm[v] % len(PAL)]) for v in ER], run_time=1.4)
            qb = counter("模块度", f"{ER_Q:.2f}", GOLD, vs=48).move_to([4.6, -0.4, 0])
            self.play(FadeIn(qb), run_time=0.8)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ Girvan-Newman
    def girvan_newman(self):
        tag = self.chapter("第二部分 · 拆桥：边介数")
        G = KAR
        pos = self.kpos
        net = NetView(G, pos, color=INK, rmin=0.08, rk=0.03, eo=0.45)
        with self.say("b1") as d:
            self.play(FadeIn(tag), FadeIn(net.group), run_time=1.0)
        eb = nx.edge_betweenness_centrality(G)
        mx = max(eb.values())
        with self.say("b2") as d:
            self.play(*[e.animate.set_stroke(interpolate_color(ManimColor(MUTED), ManimColor(RED), eb[k] / mx), width=1 + 7 * eb[k] / mx, opacity=0.4 + 0.6 * eb[k] / mx)
                        for k, e in net.edges.items()], run_time=d * 0.5)
        with self.say("b3") as d:
            for e in GN_REMOVED[:4]:
                ln = nv_edge(net, *e)
                self.play(ln.animate.set_color(GOLD).set_stroke(width=8), run_time=0.3)
                self.play(FadeOut(ln), run_time=0.3)
        with self.say("b4") as d:
            for e in GN_REMOVED[4:]:
                self.play(FadeOut(nv_edge(net, *e)), run_time=0.22)
            self.play(*[net.dots[v].animate.set_color(BLUE if v in GN_SIDE else RED) for v in G],
                      *[e.animate.set_stroke(MUTED, width=1.4, opacity=0.45) for k, e in net.edges.items() if k not in GN_REMOVED and (k[1], k[0]) not in GN_REMOVED],
                      run_time=1.0)
            rings = VGroup(*[Circle(radius=0.3, color=GOLD, stroke_width=4).move_to(pos[v]) for v in GN_WRONG])
            self.play(Create(rings), run_time=0.8)
            wl = counter("与真实两派不同", f"{len(GN_WRONG)} 人", GOLD, vs=36).to_corner(UR, buff=0.4)
            self.play(FadeIn(wl), run_time=0.6)
        with self.say("b5") as d:
            cost = T("每一步：重算全部边介数", 28, MUTED).to_edge(DOWN, buff=0.4)
            self.play(FadeIn(cost), run_time=0.8)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ Louvain / Leiden
    def louvain(self):
        tag = self.chapter("第二部分 · 卢万与莱顿")
        G = nx.planted_partition_graph(3, 8, 0.7, 0.04, seed=5)
        G = nx.convert_node_labels_to_integers(G.subgraph(max(nx.connected_components(G), key=len)).copy())
        pos = fit(nx.spring_layout(G, seed=4, iterations=200), (-6.0, 1.0, -3.2, 2.8))
        net = NetView(G, pos, color=MUTED, rmin=0.11, rk=0, eo=0.4)
        lab = {v: v for v in G}
        q = counter("模块度", f"{modularity(G, [{v} for v in G]):.2f}", GOLD, vs=40).move_to([4.3, 1.4, 0])
        with self.say("v1") as d:
            self.play(FadeIn(tag), FadeIn(net.group), run_time=1.0)
            self.play(*[net.dots[v].animate.set_color(PAL[v % len(PAL)]) for v in G], FadeIn(q), run_time=1.0)
        # one pass of local moving (greedy, deterministic order)
        rng = np.random.default_rng(1)
        order = list(G)
        m2 = 2 * G.number_of_edges()
        k = dict(G.degree())

        def tot(c):
            return sum(k[u] for u in G if lab[u] == c)

        def gain(v, c):
            kin = sum(1 for u in G.neighbors(v) if lab[u] == c)
            return kin / (m2 / 2) - tot(c) * k[v] / (m2 ** 2 / 2)
        moves = []
        changed = True
        while changed:
            changed = False
            for v in order:
                old = lab[v]; lab[v] = -1
                cands = {lab[u] for u in G.neighbors(v)} | {old}
                best = max(cands, key=lambda c: gain(v, c))
                if gain(v, best) > gain(v, old) + 1e-12:
                    lab[v] = best; moves.append((v, best)); changed = True
                else:
                    lab[v] = old
        part = {}
        for v, c in lab.items():
            part.setdefault(c, set()).add(v)
        Qf = modularity(G, list(part.values()))
        cmap = {c: PAL[i % len(PAL)] for i, c in enumerate(sorted(part, key=lambda c: min(part[c])))}
        with self.say("v2") as d:
            rt = max(0.12, (d - 0.5) / max(1, len(moves)))
            for v, c in moves:
                self.play(net.dots[v].animate.set_color(PAL[c % len(PAL)]), run_time=rt)
            self.play(*[net.dots[v].animate.set_color(cmap[lab[v]]) for v in G],
                      Transform(q[1], T(f"{Qf:.2f}", 40, GOLD, weight=BOLD).move_to(q[1])), run_time=0.6)
        cs = list(part.values())
        cen = [np.mean([pos[v] for v in c], axis=0) for c in cs]
        sup = [Dot(cen[i], radius=0.18 + 0.03 * len(c), color=cmap[lab[next(iter(c))]]) for i, c in enumerate(cs)]
        with self.say("v3") as d:
            anims = []
            for i, c in enumerate(cs):
                for v in c:
                    anims.append(net.dots[v].animate.move_to(cen[i]))
            self.play(*anims, *[e.animate.put_start_and_end_on(cen[[j for j, c in enumerate(cs) if u in c][0]], cen[[j for j, c in enumerate(cs) if w in c][0]] + 1e-3)
                                for (u, w), e in net.edges.items()], run_time=1.6)
            self.play(*[FadeIn(s) for s in sup], *[FadeOut(net.dots[v]) for v in G], run_time=0.8)
        with self.say("v4") as d:
            fast = T("百万级节点", 30, GOLD, weight=BOLD).move_to([4.3, -0.6, 0])
            self.play(FadeIn(fast), run_time=0.8)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.6)
        # badly connected community and the refinement fix
        L = [np.array(p) for p in ([-5.0, 0.8, 0], [-5.6, -0.4, 0], [-4.4, -0.4, 0], [-1.6, 0.8, 0], [-2.2, -0.4, 0], [-1.0, -0.4, 0])]
        bridge = np.array([-3.3, 1.6, 0])
        dl = [Dot(p, radius=0.15, color=BLUE) for p in L]
        db = Dot(bridge, radius=0.15, color=BLUE)
        ed = [(0, 1), (1, 2), (0, 2), (3, 4), (4, 5), (3, 5)]
        ll = [Line(L[u], L[v], color=MUTED, stroke_width=3) for u, v in ed]
        lb = [Line(bridge, L[0], color=MUTED, stroke_width=3), Line(bridge, L[3], color=MUTED, stroke_width=3)]
        other = Dot(bridge + UP * 1.0 + RIGHT * 1.6, radius=0.15, color=GOLD)
        hull = RoundedRectangle(width=6.0, height=3.0, corner_radius=0.4, color=BLUE, stroke_width=2).move_to([-3.3, 0.5, 0])
        with self.say("v5") as d:
            self.play(*[FadeIn(x) for x in dl + [db, other]], *[Create(x) for x in ll + lb], Create(hull), run_time=1.0)
            self.play(db.animate.set_color(GOLD).move_to(bridge + UP * 0.6 + RIGHT * 1.0), FadeOut(lb[0]), FadeOut(lb[1]), run_time=1.0)
            warn = T("断开的社团", 26, RED).next_to(hull, DOWN, buff=0.2)
            self.play(hull.animate.set_color(RED), FadeIn(warn), run_time=0.8)
            h1 = RoundedRectangle(width=2.4, height=2.0, corner_radius=0.3, color=GREEN, stroke_width=3).move_to([-5.0, 0.2, 0])
            h2 = RoundedRectangle(width=2.4, height=2.0, corner_radius=0.3, color=GREEN, stroke_width=3).move_to([-1.6, 0.2, 0])
            ok = T("细化后：各自连通", 26, GREEN).move_to(warn)
            self.play(ReplacementTransform(hull, VGroup(h1, h2)), Transform(warn, ok), *[dl[i].animate.set_color(GREEN) for i in range(6)], run_time=1.2)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ detectability
    def detectability(self):
        tag = self.chapter("第三部分 · 可检测性")
        n = 160

        def sbm(cin, cout, seed):
            # the site's definition: connection probabilities c_in/n and c_out/n, mean degree c = (c_in + c_out) / 2
            p = [[cin / n, cout / n], [cout / n, cin / n]]
            G = nx.stochastic_block_model([n // 2, n // 2], p, seed=seed)
            return G
        with self.say("d1") as d:
            self.play(FadeIn(tag), run_time=0.6)
            q = T("社团存在，但信号很弱", 38, INK)
            self.play(FadeIn(q), run_time=1.0)
            self.play(FadeOut(q), run_time=0.6)
        Gs = sbm(9.5, 0.5, 3)
        Gw = sbm(7.2, 2.8, 3)
        ps = fit(nx.spring_layout(Gs, seed=1, iterations=200), (-6.3, -0.7, -2.0, 2.4))
        pw = fit(nx.spring_layout(Gw, seed=1, iterations=200), (0.7, 6.3, -2.0, 2.4))
        col = lambda v: BLUE if v < n // 2 else GOLD
        vs = NetView(Gs, ps, color=MUTED, rmin=0.06, rk=0, eo=0.25)
        vw = NetView(Gw, pw, color=MUTED, rmin=0.06, rk=0, eo=0.25)
        for v in Gs:
            vs.dots[v].set_color(col(v)); vw.dots[v].set_color(col(v))
        ls = VGroup(MathTex(r"c_{\mathrm{in}}=9.5,\ \ c_{\mathrm{out}}=0.5", font_size=34, color=INK)).next_to(vs.group, UP, buff=0.45)
        lw = VGroup(MathTex(r"c_{\mathrm{in}}=7.2,\ \ c_{\mathrm{out}}=2.8", font_size=34, color=INK)).next_to(vw.group, UP, buff=0.45)
        hdr = VGroup(T("随机块模型参数 · 两组 · 平均度", 22, MUTED),
                     MathTex(r"c=(c_{\mathrm{in}}+c_{\mathrm{out}})/2=5", font_size=30, color=MUTED)).arrange(RIGHT, buff=0.2).move_to([1.2, 3.5, 0])
        pn = T("每个节点约 3.6 条组内边 · 1.4 条组间边", 18, MUTED).next_to(lw, DOWN, buff=0.06)
        with self.say("d2") as d:
            self.play(FadeIn(hdr), run_time=1.0)
            self.play(FadeIn(vs.group), run_time=1.4)
        with self.say("d2a") as d:
            self.play(FadeIn(ls), run_time=0.8)
        with self.say("d3") as d:
            self.play(FadeIn(vw.group), FadeIn(lw), run_time=1.4)
        with self.say("d3b") as d:
            self.play(FadeIn(pn), run_time=0.8)
        with self.say("d4") as d:
            th = MathTex(r"|c_{\mathrm{in}}-c_{\mathrm{out}}| \le q\sqrt{c}", font_size=46, color=GOLD)
            bg = BackgroundRectangle(th, fill_color=BG, fill_opacity=0.92, buff=0.25)
            g = VGroup(bg, th).move_to([0, -3.1, 0])
            self.play(FadeIn(bg), Write(th), run_time=1.4)
        with self.say("d4b") as d:
            val = MathTex(r"7.2-2.8=4.4 \;<\; 2\sqrt{5}\approx 4.47", font_size=34, color=INK).next_to(g, UP, buff=0.1)
            bgv = BackgroundRectangle(val, fill_color=BG, fill_opacity=0.92, buff=0.12)
            self.play(FadeIn(bgv), FadeIn(val), run_time=0.8)
        with self.say("d5") as d:
            self.play(Indicate(vw.group, color=GOLD, scale_factor=1.03), run_time=1.2)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ biomedical
    def biomed(self):
        tag = self.chapter("第三部分 · 生物医学中的社团")
        # protein complexes: dense blobs on a sparse background
        rng = np.random.default_rng(2)
        G = nx.planted_partition_graph(4, 7, 0.85, 0.02, seed=2)
        pos = fit(nx.spring_layout(G, seed=3, iterations=200), (-5.6, 5.6, -3.0, 2.6))
        net = NetView(G, pos, color=MUTED, rmin=0.09, rk=0, eo=0.4)
        with self.say("s1") as d:
            self.play(FadeIn(tag), FadeIn(net.group), run_time=1.0)
            hulls = []
            for i in range(4):
                c = [v for v in G if v // 7 == i]
                hulls.append(SurroundingRectangle(VGroup(*[net.dots[v] for v in c]), color=PAL[i], corner_radius=0.3, buff=0.2))
            self.play(*[net.dots[v].animate.set_color(PAL[v // 7]) for v in G], *[Create(h) for h in hulls], run_time=1.4)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.6)
        # schematic brain with functional systems
        brain = Ellipse(width=8.6, height=5.6, color=MUTED, stroke_width=3).shift(DOWN * 0.2)
        systems = [("视觉", BLUE, [-3.0, -0.4]), ("躯体运动", GREEN, [0.2, 1.6]), ("默认模式", GOLD, [2.4, -0.5]), ("额顶控制", VIOLET, [-0.6, -1.6])]
        groups = VGroup()
        for name, c, ctr in systems:
            ctr = np.array([*ctr, 0])
            ds = VGroup(*[Dot(ctr + np.array([rng.normal(0, 0.45), rng.normal(0, 0.35), 0]), radius=0.07, color=c) for _ in range(14)])
            groups.add(VGroup(ds, T(name, 24, c).next_to(ds, DOWN, buff=0.1)))
        with self.say("s2") as d:
            self.play(Create(brain), run_time=0.8)
            self.play(LaggedStart(*[FadeIn(g) for g in groups], lag_ratio=0.3), run_time=d * 0.6)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.6)
        with self.say("s2b") as d:
            self.clip_on("yt_rsfmri_monash.mp4", "center", "视频：Monash Biomedical Imaging · YouTube", start=2)
        self.clip_off()
        # single-cell kNN graph, Louvain at two resolutions
        r7 = np.random.default_rng(7)
        centers = [(-3.2, 1.0), (-2.4, -1.0), (0.2, 0.9), (0.9, -1.2), (3.3, 0.6), (3.1, -1.5)]
        X = np.vstack([np.array(c) + r7.normal(0, 0.45, (26, 2)) for c in centers])
        K = nx.Graph()
        from scipy.spatial import cKDTree
        tr = cKDTree(X)
        for i, x in enumerate(X):
            for j in tr.query(x, 9)[1][1:]:
                K.add_edge(i, int(j))
        p = {i: np.array([X[i, 0] * 1.05, X[i, 1] * 1.05 - 0.2, 0]) for i in range(len(X))}
        dots = {i: Dot(p[i], radius=0.06, color=MUTED) for i in K}
        eds = VGroup(*[Line(p[u], p[v], color=MUTED, stroke_width=1, stroke_opacity=0.35) for u, v in K.edges()])
        lo = louvain_communities(K, resolution=0.05, seed=1)
        hi = louvain_communities(K, resolution=3.0, seed=1)
        assert len(lo) == 4 and len(hi) == 13, (len(lo), len(hi))
        rl = counter("分辨率", "低", INK, vs=34).to_corner(UR, buff=0.4)
        nc = counter("细胞簇", str(len(lo)), GOLD, vs=34).next_to(rl, DOWN, buff=0.3)
        with self.say("s3") as d:
            self.play(FadeIn(VGroup(*dots.values())), run_time=0.8)
            self.play(Create(eds), run_time=1.2)
        with self.say("s4") as d:
            self.play(*[dots[v].animate.set_color(PAL[i]) for i, c in enumerate(lo) for v in c], FadeIn(rl), FadeIn(nc), run_time=1.2)
        with self.say("s4b") as d:
            self.play(*[dots[v].animate.set_color(PAL[i % len(PAL)]) for i, c in enumerate(hi) for v in c],
                      Transform(rl[1], T("高", 34, INK, weight=BOLD).move_to(rl[1])),
                      Transform(nc[1], T(str(len(hi)), 34, GOLD, weight=BOLD).move_to(nc[1])), run_time=1.2)
        with self.say("s5") as d:
            chk = VGroup(*[T(s, 28, INK) for s in ("✓ 显著性", "✓ 稳定性", "✓ 参数")]).arrange(RIGHT, buff=0.8).to_edge(DOWN, buff=0.35)
            bg = BackgroundRectangle(chk, fill_color=BG, fill_opacity=0.9, buff=0.15)
            self.play(FadeIn(bg), LaggedStart(*[FadeIn(c) for c in chk], lag_ratio=0.3), run_time=1.4)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ recap
    def recap(self):
        items = [("r2", BLUE, "社团：内部紧密，与随机预期比较"),
                 ("r3", GOLD, "随机网络也能被分组：要做显著性与稳定性检验"),
                 ("r4", GREEN, "信号弱则不可检测；参数决定尺度")]
        head, rows = recap_rows(items)
        with self.say("r1") as d:
            self.play(Write(head), run_time=0.8)
        for (k, _, _), row in zip(items, rows):
            with self.say(k) as d:
                self.play(FadeIn(row, shift=RIGHT * 0.3), run_time=0.8)
        self.wait(0.8)
        self.play(FadeOut(rows), FadeOut(head), run_time=0.6)
        with self.say("r5") as d:
            self.clip_on("modularity_demo.mp4", "full", "本站交互演示：模块度与社团划分", start=0.3)
            if d < 12.6:
                self.wait(12.7 - d)
        self.clip_off()
        self.wait(1.0)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=1.0)
