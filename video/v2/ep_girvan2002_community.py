"""Paper explainer: Girvan & Newman 2002, community structure via edge betweenness."""
import networkx as nx
import numpy as np

from paperhelp import *  # noqa: F401,F403

TITLE = "社团发现：从最繁忙的边下刀"
LINES = {
    # hook
    "h1": "这是一个空手道俱乐部，有三十四名成员。每个点是一个人，两个人平时有来往，就连一条线。",
    "h2": "后来，俱乐部的管理者和教练闹翻了，俱乐部一分为二。蓝色和金色，就是后来的两派。",
    "h3": "现在把颜色抹掉。我们的问题是：只看这张关系网，不知道任何内情，能不能找出这条裂缝。",
    "h4": "【慢】2002年，《美国国家科学院院刊》上的一篇论文，给出了一个漂亮的办法。",
    "q0": "这一期分三部分来讲。",
    "q1": "第一部分，什么是社团，以及找社团边界的工具——边介数。",
    "q2": "第二部分，论文的算法，以及它在空手道俱乐部和人工网络上的检验。",
    "q3": "第三部分，生物网络里的应用，最后说说局限。",
    # communities
    "c1": "先看第一部分。网络里常有这样的结构：节点分成若干组，组内连得密，组间连得稀。这就叫社团。",
    "c2": "社交网络里的兴趣群体，代谢网络里的功能模块，引文网络里的研究方向，都属于社团。",
    "c3": "当时的标准做法，叫层次聚类：从最相似的一对节点开始，一步步往上合并成一个个圈子。",
    "c4": "可它有个毛病：只有一条边的边缘节点，和谁都不太像，常常被孤立在外面，就是这个红圈里的点。",
    "c5": "【慢】两位作者把思路倒了过来：不去找社团的核心，而去找社团之间的边界，再把边界一条条拆掉。",
    # edge betweenness
    "b1": "边界怎么找。想象每两个节点之间，都要沿着最短的路线互相拜访，黄色的小点就是来回走动的人。",
    "b2": "两个社团之间只有两条边。所有跨社团的路线，都得挤过这两座桥。",
    "b3": "数一数每条边上经过多少条最短路径，就是这条边的边介数。线越粗，经过的路径越多。上面这座桥是二十四，下面这座是十二。",
    "b4": "如果一对节点之间，有好几条一样短的路，就把这一对的份额平分。从A到D有两条路，每条各算二分之一。",
    "b4b": "写成式子就是右上角这样。分母是从s到t一共有几条最短路，分子是其中经过边e的有几条。把所有节点对加起来，就是边e的边介数。",
    # algorithm
    "a1": "下面进入第二部分，看算法。第一步，算出所有边的边介数；第二步，删掉最大的那一条。",
    "a2": "第三步，重新计算，再删最大的。一直重复下去，网络就沿着社团边界，一层层裂开。",
    "a3": "重新计算这一步，非常关键。看这个例子，两个社团之间有两座桥。",
    "a4": "一开始，最短路径大多挤在上面这座桥上，分数是二十四；下面这座只有十二，是它的一半。",
    "a5": "【慢】删掉上面那座之后重新计算，所有跨社团的路线都改走下面。它的分数从十二涨到三十六，成了新的最高。",
    "a6": "也就是说，一次性算好再按顺序删，只能保证至少有一座桥分数高；每删一条就重算，剩下的桥才会一座座显露出来。",
    # karate
    "k1": "回到空手道俱乐部。我们在场景里，一条一条删掉边介数最高的边，右上角是删掉的条数。",
    "k2": "删到第十一条，网络第一次裂成了两块，就是蓝色和金色。",
    "k3": "和真实的分裂对比，三十四人里只有两人分错，就是画红圈的3号和9号。原文报告的结果里，只分错了3号一人。",
    "k4": "继续删下去，把每一次分裂都记下来，就得到右边这棵层次树。圆圈里的数字，是这一块有几个人。",
    "g1": "本站的知识页面里，有空手道俱乐部的交互演示。它用模块度给每种分组打分——模块度后面会细讲。先把所有人归为一组，模块度是零。",
    "g2": "按俱乐部真实的分裂来分组，模块度约为零点三七。再点贪心优化，让算法自己找分组，分数还能再高一点。",
    # planted test
    "t1": "作者还在人工网络上做了检验：一百二十八个节点，分成四个社团，每个节点平均有十六条边。",
    "t2": "社团之间的连边越多，社团就越模糊。原文发现，只要每个节点的社团间连边不超过六条，几乎所有节点都能归对。",
    "t3": "我们取每个节点平均四条社团间连边，跑一遍算法。你看，四个社团被完整地分了出来，归类正确率百分之百。",
    # biology
    "f1": "最后是第三部分，回到标题里的生物网络。论文分析了切萨皮克湾的食物网，有三十三个主要的物种类群。",
    "f1b": "切萨皮克湾是美国东部的一个大河口。画面里，就是那里水中的生物。",
    "f2": "这张示意图里，每一行是一个营养级，也就是食物链上的一层。算法把食物网分成了两个大小相近的社团，大体对应浮游生物和底栖生物。",
    "f3": "【慢】注意，每个社团都跨越了好几个营养级。也就是说，社团是按栖息环境形成的，而不是按谁吃谁的层级。",
    "f4": "同样的思路，后来被广泛用于在细胞网络里，寻找功能模块和疾病模块。",
    # limits
    "l1": "下面说说局限。这篇论文留下了两个问题。第一，层次树该切在哪一层，原文没有给出客观标准。",
    "l2": "两年后提出的模块度，给每一种切法打分，选分数最高的那一层。这张图横轴是删掉的边数，纵轴是模块度。在空手道网络上，它挑中的是删掉二十四条边之后的划分。",
    "l3": "第二，速度太慢。每删一条边，都要把边介数重算一遍。在稀疏网络上，总时间大约和节点数的三次方成正比。",
    "l4": "后来，更快的方法陆续出现。人们还发现，模块度有分辨率极限，可能把小社团合并；真实的社团，也可能彼此重叠。",
    # recap
    "z1": "好，我们来总结一下。",
    "z2": "第一，社团之间的少数边，承载了大量最短路径，所以边介数很高。",
    "z3": "第二，反复删除边介数最大的边，并且每次都重算，网络就会沿着社团边界裂开。",
    "z4": "第三，结果是一棵层次树。切在哪里、算得太慢，这两个问题催生了模块度和更快的算法。",
}

COLS = [BLUE, GOLD, GREEN, VIOLET, RED]


def bridge_graph():
    G = nx.Graph()
    pts = {}
    base = {0: (-1.5, 1.0), 1: (-2.6, 1.9), 2: (-3.9, 1.0), 3: (-3.6, -0.5), 4: (-2.2, -0.5), 5: (-1.6, -1.9)}
    for side, sg in (("a", -1), ("b", 1)):
        for i in range(5):
            for j in range(i + 1, 5):
                G.add_edge(f"{side}{i}", f"{side}{j}")
        G.add_edge(f"{side}5", f"{side}3"); G.add_edge(f"{side}5", f"{side}4")
        for i, (x, y) in base.items():
            pts[f"{side}{i}"] = np.array([x * -sg if sg > 0 else x, y, 0]) if sg > 0 else np.array([x, y, 0])
    for i, (x, y) in base.items():
        pts[f"b{i}"] = np.array([-x, y, 0])
    G.add_edge("a0", "b0"); G.add_edge("a5", "b5")
    return G, pts


def eb(G):
    return nx.edge_betweenness_centrality(G, normalized=False)


class Episode(Narrated):
    LINES = LINES

    def construct(self):
        self.K = nx.karate_club_graph()
        self.kpos = fit(nx.kamada_kawai_layout(self.K), (-6.0, 0.6, -3.2, 2.8))
        self.hook()
        parts(self, "q0", ["q1", "q2", "q3"], "这一期分三部分",
              ["一  社团与边介数", "二  算法与检验", "三  生物网络与局限"])
        self.communities()
        self.betweenness()
        self.algorithm()
        self.karate()
        clip_lines(self, "modularity_gn_demo.mp4", ["g1", "g2"], "本站交互演示：给空手道俱乐部分组", start=0.3, box="full")
        self.planted()
        self.foodweb()
        self.limits()
        recap(self, "z1", [("z2", GOLD, "社团间的桥：边介数高"),
                           ("z3", RED, "反复删最大，每次重算"),
                           ("z4", BLUE, "层次树 → 模块度与快速算法")])

    # ------------------------------------------------------------------ hook
    def hook(self):
        K, pos = self.K, self.kpos
        pos = {v: p + RIGHT * 2.7 for v, p in pos.items()}
        net = NetView(K, pos, color=MUTED, rmin=0.07, rk=0.02, eo=0.5)
        with self.say("h1"):
            self.play(LaggedStart(*[GrowFromCenter(d) for d in net.dots.values()], lag_ratio=0.03), run_time=1.6)
            self.play(LaggedStart(*[Create(e) for e in net.edges.values()], lag_ratio=0.02), run_time=1.6)
        club = {v: K.nodes[v]["club"] for v in K}
        with self.say("h2"):
            self.play(*[net.dots[v].animate.set_color(BLUE if club[v] == "Mr. Hi" else GOLD) for v in K], run_time=1.2)
            self.play(*[net.dots[v].animate.shift((LEFT if club[v] == "Mr. Hi" else RIGHT) * 0.5) for v in K],
                      *[e.animate.set_stroke(opacity=0.12) for (a, b), e in net.edges.items() if club[a] != club[b]], run_time=1.2)
        with self.say("h3"):
            self.play(*[net.dots[v].animate.set_color(MUTED).shift((RIGHT if club[v] == "Mr. Hi" else LEFT) * 0.5) for v in K],
                      *[e.animate.set_stroke(opacity=0.5) for e in net.edges.values()], run_time=1.2)
            q = T("找出这条裂缝", 40, GOLD, weight=BOLD).to_edge(DOWN, buff=0.35)
            self.play(FadeIn(q), run_time=0.8)
        with self.say("h4"):
            self.play(net.group.animate.set_opacity(0.3), run_time=1.0)
        clear(self)

    # ------------------------------------------------------------------ communities
    def communities(self):
        tag = self.chapter("一  社团与边界")
        sizes = [9, 9, 9]
        G = nx.random_partition_graph(sizes, 0.55, 0.012, seed=5)
        G = G.subgraph(max(nx.connected_components(G), key=len)).copy()
        part = {v: i for i, blk in enumerate(G.graph["partition"]) for v in blk}
        leaf = max(G) + 1
        anchor = [v for v in G if part[v] == 0][0]
        G.add_edge(leaf, anchor); part[leaf] = 0
        H = G.copy(); H.remove_node(leaf)
        pos = fit(nx.spring_layout(H, seed=3, k=0.6), (-4.6, 4.6, -2.8, 2.4))
        cen = {i: np.mean([pos[v] for v in H if part[v] == i], axis=0) for i in range(3)}
        rad = {i: np.percentile([np.linalg.norm(pos[v] - cen[i]) for v in H if part[v] == i], 80) + 0.3 for i in range(3)}
        d = cen[0] - np.mean([cen[i] for i in range(3)], axis=0); d = d / (np.linalg.norm(d) + 1e-9)
        anchor = min((v for v in H if part[v] == 0), key=lambda v: -np.dot(pos[v] - cen[0], d))
        G.remove_edge(leaf, [w for w in G[leaf]][0]); G.add_edge(leaf, anchor)
        pos[leaf] = cen[0] + d * (rad[0] + 0.6)
        net = NetView(G, pos, color=MUTED, rmin=0.09, rk=0.0, eo=0.5)
        with self.say("c1"):
            self.play(FadeIn(tag), FadeIn(net.group), run_time=1.2)
            self.play(*[net.dots[v].animate.set_color(COLS[part[v]]) for v in G],
                      *[e.animate.set_stroke(COLS[part[a]], opacity=0.7) for (a, b), e in net.edges.items() if part[a] == part[b]], run_time=1.2)
        with self.say("c2"):
            labs = ["兴趣群体", "功能模块", "研究方向"]
            ts = VGroup(*[T(l, 24, COLS[i]).next_to(VGroup(*[net.dots[v] for v in G if part[v] == i]), UP, buff=0.15) for i, l in enumerate(labs)])
            self.play(LaggedStart(*[FadeIn(t) for t in ts], lag_ratio=0.3), run_time=1.4)
        with self.say("c3"):
            self.play(FadeOut(ts), *[net.dots[v].animate.set_color(MUTED) for v in G], *[e.animate.set_stroke(MUTED, opacity=0.5) for e in net.edges.values()], run_time=0.8)
            hulls = VGroup(*[Circle(radius=rad[i], color=COLS[i], stroke_width=3).move_to(cen[i]) for i in range(3)])
            self.play(LaggedStart(*[Create(h) for h in hulls], lag_ratio=0.4), run_time=1.8)
        with self.say("c4"):
            ring = Circle(radius=0.25, color=RED, stroke_width=4).move_to(net.dots[leaf])
            lt = T("被孤立", 24, RED).next_to(ring, DOWN, buff=0.1)
            self.play(Create(ring), FadeIn(lt), net.dots[leaf].animate.set_color(RED), run_time=1.0)
        with self.say("c5"):
            self.play(FadeOut(hulls), FadeOut(ring), FadeOut(lt), run_time=0.6)
            cut = [e for (a, b), e in net.edges.items() if part[a] != part[b]]
            self.play(*[e.animate.set_stroke(RED, width=4, opacity=1) for e in cut], *[net.dots[v].animate.set_color(COLS[part[v]]) for v in G], run_time=1.0)
            self.play(*[e.animate.set_stroke(opacity=0) for e in cut], run_time=1.2)
        clear(self)

    # ------------------------------------------------------------------ edge betweenness
    def betweenness(self):
        tag = self.chapter("一  边介数")
        G, pos = bridge_graph()
        pos = {v: p + DOWN * 0.2 for v, p in pos.items()}
        net = NetView(G, pos, color=BLUE, rmin=0.11, rk=0.0, ew=2, eo=0.6)
        with self.say("b1") as d:
            self.play(FadeIn(tag), FadeIn(net.group), run_time=1.0)
            rng = np.random.default_rng(1)
            nodes = list(G)
            trips = []
            for _ in range(10):
                a, b = rng.choice(nodes, 2, replace=False)
                if a[0] == b[0]:
                    b = ("b" if a[0] == "a" else "a") + b[1]
                trips.append(nx.shortest_path(G, a, b))
            walkers = [Dot(pos[p[0]], radius=0.08, color=GOLD) for p in trips]
            self.play(LaggedStart(*[MoveAlongPath(w, VMobject().set_points_as_corners([pos[v] for v in p])) for w, p in zip(walkers, trips)],
                                  lag_ratio=0.15), run_time=d * 0.6)
            self.play(*[FadeOut(w) for w in walkers], run_time=0.3)
        b = eb(G)
        mx = max(b.values())
        with self.say("b2"):
            e1, e2 = net.edges[("a0", "b0")], net.edges[("a5", "b5")]
            self.play(Indicate(e1, color=GOLD, scale_factor=1.0), Indicate(e2, color=GOLD, scale_factor=1.0), run_time=1.2)
            self.play(e1.animate.set_stroke(GOLD, opacity=1), e2.animate.set_stroke(GOLD, opacity=1), run_time=0.6)
        with self.say("b3"):
            self.play(*[e.animate.set_stroke(width=1.5 + 10 * b[k] / mx) for k, e in net.edges.items()], run_time=1.4)
            labs = VGroup(*[T(f"{b[k]:g}", 22, GOLD if k in (("a0", "b0"), ("a5", "b5")) else MUTED).move_to(net.edges[k].get_center() + UP * 0.25)
                            for k in [("a0", "b0"), ("a5", "b5"), ("a0", "a1"), ("b3", "b4")]])
            self.play(FadeIn(labs), run_time=0.8)
        clear(self, keep=[tag])
        sq = {"A": LEFT * 2 + DOWN * 0.3, "B": UP * 1.4 + DOWN * 0.3, "C": DOWN * 2.0, "D": RIGHT * 2 + DOWN * 0.3}
        dots = VGroup(*[VGroup(Dot(p, radius=0.2, color=BLUE), T(k, 22, BG, weight=BOLD).move_to(p)) for k, p in sq.items()])
        ls = {k: Line(sq[k[0]], sq[k[1]], color=BLUE, stroke_width=4) for k in ("AB", "BD", "AC", "CD")}
        with self.say("b4"):
            self.play(*[Create(l) for l in ls.values()], FadeIn(dots), run_time=1.0)
            self.play(ls["AB"].animate.set_color(GOLD), ls["BD"].animate.set_color(GOLD), run_time=0.6)
            self.play(ls["AC"].animate.set_color(GREEN), ls["CD"].animate.set_color(GREEN), run_time=0.6)
            h = VGroup(*[MathTex(r"\tfrac12", font_size=40, color=GOLD if k in ("AB", "BD") else GREEN).move_to(ls[k].get_center() + (UP if k in ("AB", "BD") else DOWN) * 0.4 + (LEFT if k[0] == "A" else RIGHT) * 0.3)
                         for k in ls])
            self.play(FadeIn(h), run_time=0.6)
        with self.say("b4b"):
            f = MathTex(r"B(e)=\sum_{s\neq t}\frac{\sigma_{st}(e)}{\sigma_{st}}", font_size=44).to_corner(UR, buff=0.6).shift(DOWN * 0.4)
            self.play(Write(f), run_time=1.2)
            fl = VGroup(T("分母：s 到 t 的最短路条数", 20, MUTED), T("分子：其中经过边 e 的条数", 20, GOLD),
                        T("求和：所有节点对加起来", 20, BLUE)).arrange(DOWN, aligned_edge=LEFT, buff=0.15).next_to(f, DOWN, buff=0.3)
            for x in fl:
                self.play(FadeIn(x, shift=UP * 0.1), run_time=0.5)
                self.wait(0.8)
        clear(self)

    # ------------------------------------------------------------------ algorithm
    def algorithm(self):
        tag = self.chapter("二  删边，重算，再删边")
        boxes = VGroup(*[VGroup(RoundedRectangle(corner_radius=0.2, width=3.0, height=0.9, stroke_color=c, stroke_width=3), T(t, 26, c))
                         for t, c in (("计算边介数", BLUE), ("删掉最大的边", RED), ("重新计算", GOLD))])
        for bx in boxes:
            bx[1].move_to(bx[0])
        boxes[0].move_to(UP * 1.6); boxes[1].move_to(RIGHT * 3.0 + DOWN * 1.2); boxes[2].move_to(LEFT * 3.0 + DOWN * 1.2)
        ar = [Arrow(boxes[0].get_right(), boxes[1].get_top(), color=MUTED, buff=0.15, path_arc=-0.6),
              Arrow(boxes[1].get_left(), boxes[2].get_right(), color=MUTED, buff=0.15),
              Arrow(boxes[2].get_top(), boxes[1].get_top() + LEFT * 0.6, color=GOLD, buff=0.15, path_arc=-1.0)]
        steps, loop = boxes, VGroup(*ar)
        with self.say("a1"):
            self.play(FadeIn(tag), FadeIn(boxes[0], shift=DOWN * 0.2), run_time=0.8)
            self.play(GrowArrow(ar[0]), FadeIn(boxes[1]), run_time=0.9)
        with self.say("a2"):
            self.play(GrowArrow(ar[1]), FadeIn(boxes[2]), run_time=0.9)
            self.play(Create(ar[2]), run_time=0.8)
            self.play(Indicate(boxes[1], color=RED), Indicate(boxes[2], color=GOLD), run_time=1.0)
        self.play(FadeOut(steps), FadeOut(loop), run_time=0.5)
        G, pos = bridge_graph()
        pos = {v: p + DOWN * 0.3 for v, p in pos.items()}
        net = NetView(G, pos, color=BLUE, rmin=0.11, rk=0.0, ew=2, eo=0.6)
        e1, e2 = ("a0", "b0"), ("a5", "b5")
        with self.say("a3"):
            self.play(FadeIn(net.group), run_time=1.0)
            self.play(net.edges[e1].animate.set_stroke(GOLD, width=5, opacity=1), net.edges[e2].animate.set_stroke(GOLD, width=5, opacity=1), run_time=0.8)
        b0 = eb(G)
        top3 = sorted((x for x in b0 if x not in (e1, e2)), key=lambda k: -b0[k])[0]
        l1 = T(f"{b0[e1]:g}", 30, RED, weight=BOLD).next_to(net.edges[e1], UP, buff=0.15)
        l2 = T(f"{b0[e2]:g}", 30, GOLD, weight=BOLD).next_to(net.edges[e2], DOWN, buff=0.15)
        with self.say("a4"):
            self.play(FadeIn(l1), net.edges[e1].animate.set_stroke(RED, width=8), run_time=0.8)
            self.play(FadeIn(l2), run_time=0.8)
        G.remove_edge(*e1)
        b1 = eb(G)
        print(f"[gn] bridge {b0[e1]:g}/{b0[e2]:g} -> {b1[e2]:g}; max other after {max(v for k, v in b1.items() if k != e2):g}")
        with self.say("a5"):
            self.play(FadeOut(net.edges[e1]), FadeOut(l1), run_time=0.8)
            nl2 = T(f"{b0[e2]:g} → {b1[e2]:g}", 30, RED, weight=BOLD).move_to(l2)
            self.play(Transform(l2, nl2), net.edges[e2].animate.set_stroke(RED, width=8), run_time=1.0)
        with self.say("a6"):
            self.play(FadeOut(net.edges[e2]), FadeOut(l2), run_time=0.8)
            self.play(*[net.dots[v].animate.set_color(BLUE if v[0] == "a" else GOLD) for v in G], run_time=0.8)
        clear(self)

    # ------------------------------------------------------------------ karate
    def karate(self):
        tag = self.chapter("二  空手道俱乐部")
        K, pos = self.K, self.kpos
        net = NetView(K, pos, color=MUTED, rmin=0.07, rk=0.02, eo=0.5)
        H = K.copy()
        removed = []
        while nx.number_connected_components(H) == 1:
            b = eb(H)
            e = max(b, key=b.get)
            H.remove_edge(*e); removed.append(e)
        print(f"[gn] first split after {len(removed)} removals")
        cs = sorted(nx.connected_components(H), key=len)
        club = {v: K.nodes[v]["club"] for v in K}

        def key(a, b):
            return (a, b) if (a, b) in net.edges else (b, a)
        cnt = counter("已删除", "0", RED).move_to(RIGHT * 4.4 + UP * 1.6)
        with self.say("k1"):
            self.play(FadeIn(tag), FadeIn(net.group), FadeIn(cnt), run_time=1.0)
        with self.say("k2") as d:
            rt = (d - 0.6) / len(removed)
            for i, e in enumerate(removed):
                ed = net.edges[key(*e)]
                self.play(ed.animate.set_stroke(RED, width=5, opacity=1), Transform(cnt, counter("已删除", str(i + 1), RED).move_to(cnt)), run_time=rt * 0.5)
                self.play(FadeOut(ed), run_time=rt * 0.5)
            col = {}
            for i, c in enumerate(cs):
                hi = sum(club[v] == "Mr. Hi" for v in c) > len(c) / 2
                for v in c:
                    col[v] = BLUE if hi else GOLD
            self.play(*[net.dots[v].animate.set_color(col[v]) for v in K], run_time=0.6)
        wrong = [v for v in K if (col[v] == BLUE) != (club[v] == "Mr. Hi")]
        print(f"[gn] misclassified (1-indexed): {[v + 1 for v in wrong]}")
        with self.say("k3"):
            lg = VGroup(T("算法分出的两块：蓝 / 金", 22, INK), T("圈出的：与真实派别不符", 22, RED)).arrange(DOWN, aligned_edge=LEFT, buff=0.15).move_to(RIGHT * 4.4 + DOWN * 0.2)
            self.play(FadeIn(lg), run_time=0.6)
            rings = VGroup(*[Circle(radius=0.26, color=RED, stroke_width=4).move_to(net.dots[v]) for v in wrong])
            nums = VGroup(*[T(f"{v + 1}号", 22, RED).next_to(net.dots[v], UR, buff=0.12) for v in wrong])
            self.play(Create(rings), FadeIn(nums), run_time=1.0)
        # dendrogram of further splits
        gen = nx.community.girvan_newman(K)
        levels = [[set(K)]] + [list(next(gen)) for _ in range(4)]
        with self.say("k4") as d:
            self.play(FadeOut(VGroup(lg, rings, nums, cnt)), run_time=0.5)
            tree = VGroup()
            ys = [2.6, 1.3, 0.0, -1.3, -2.6]
            xpos = {}
            prev = []
            for li, lev in enumerate(levels):
                px = {}
                for c in lev:
                    px[frozenset(c)] = xpos[next(pp for pp in prev if frozenset(c) <= pp)] if prev else 0
                lev = sorted(lev, key=lambda c: (px[frozenset(c)], np.mean([pos[v][0] for v in c])))
                n = len(lev)
                cur = []
                for j, c in enumerate(lev):
                    x = 1.8 + 4.8 * (j + 0.5) / n
                    fc = frozenset(c)
                    xpos[fc] = x
                    cur.append(fc)
                    node = VGroup(Circle(radius=0.12 + 0.03 * np.sqrt(len(c)), color=INK, fill_opacity=0.15, stroke_width=2),
                                  T(str(len(c)), 18, INK)).move_to([x, ys[li], 0])
                    tree.add(node)
                    if li:
                        par = next(pp for pp in prev if fc <= pp)
                        tree.add(Line([xpos[par], ys[li - 1] - 0.25, 0], [x, ys[li] + 0.25, 0], color=MUTED, stroke_width=2))
                prev = cur
            self.play(Create(tree), run_time=d * 0.7)
        clear(self)

    # ------------------------------------------------------------------ planted
    def planted(self):
        tag = self.chapter("二  人工网络检验")
        zout = 4
        rng = np.random.default_rng(zout)
        G = nx.Graph(); G.add_nodes_from(range(128))
        pin, pout = (16 - zout) / 31, zout / 96
        for i in range(128):
            for j in range(i + 1, 128):
                if rng.random() < (pin if i // 32 == j // 32 else pout):
                    G.add_edge(i, j)
        H = G.copy(); removed = []
        while nx.number_connected_components(H) < 4:
            b = eb(H); e = max(b, key=b.get); H.remove_edge(*e); removed.append(e)
        found = list(nx.connected_components(H))
        correct = sum(np.bincount([v // 32 for v in c], minlength=4).max() for c in found) / 128
        print(f"[gn] planted zout={zout}: {len(removed)} removals, correct {correct:.2f}")
        pos = fit(nx.spring_layout(G, seed=2, iterations=200), (-6.2, 1.2, -3.0, 2.6))
        net = NetView(G, pos, color=MUTED, rmin=0.05, rk=0.0, ew=0.7, eo=0.25)
        with self.say("t1"):
            self.play(FadeIn(tag), FadeIn(net.group), run_time=1.4)
            info = VGroup(T("128 个节点", 26), T("4 个社团", 26), T("平均度 16", 26)).arrange(DOWN, aligned_edge=LEFT, buff=0.25).move_to(RIGHT * 4.2 + UP * 1.4)
            self.play(FadeIn(info), run_time=0.8)
        with self.say("t2"):
            self.play(*[net.dots[v].animate.set_color(COLS[v // 32]) for v in G], run_time=1.0)
            orig = T("原文：社团间连边 ≤ 6 时几乎全对", 22, GOLD).next_to(info, DOWN, buff=0.5)
            self.play(FadeIn(orig), run_time=0.8)
        with self.say("t3") as d:
            z = T(f"这里：平均 {zout} 条社团间连边", 24, INK).next_to(orig, DOWN, buff=0.4)
            self.play(FadeIn(z), *[net.dots[v].animate.set_color(MUTED) for v in G], run_time=0.8)
            chunks = np.array_split(np.arange(len(removed)), 4)
            for ch in chunks:
                self.play(*[FadeOut(net.edges[removed[i]] if removed[i] in net.edges else net.edges[removed[i][::-1]]) for i in ch], run_time=0.4)
            fc = {}
            for c in found:
                maj = np.bincount([v // 32 for v in c], minlength=4).argmax()
                for v in c:
                    fc[v] = COLS[maj]
            self.play(*[net.dots[v].animate.set_color(fc[v]) for v in G], run_time=0.8)
            acc = counter("归类正确", f"{correct:.0%}", GREEN).next_to(z, DOWN, buff=0.4)
            self.play(FadeIn(acc), run_time=0.6)
        clear(self)

    # ------------------------------------------------------------------ food web
    def foodweb(self):
        tag = self.chapter("三  切萨皮克湾食物网")
        rng = np.random.default_rng(3)
        cols_x = {0: -2.0, 1: 2.4}
        nodes = {}
        idx = 0
        layout = {0: [3, 5, 5, 3], 1: [3, 5, 6, 3]}
        for side in (0, 1):
            for lvl, cnt in enumerate(layout[side]):
                for j in range(cnt):
                    nodes[idx] = (side, lvl, np.array([cols_x[side] + (j - (cnt - 1) / 2) * 0.7, -2.4 + lvl * 1.45, 0]))
                    idx += 1
        G = nx.Graph(); G.add_nodes_from(nodes)
        for u in nodes:
            for v in nodes:
                if u < v and abs(nodes[u][1] - nodes[v][1]) == 1:
                    same = nodes[u][0] == nodes[v][0]
                    if rng.random() < (0.45 if same else 0.04):
                        G.add_edge(u, v)
        print(f"[gn] food web schematic nodes {len(nodes)}")
        dots = {v: Dot(nodes[v][2], radius=0.11, color=MUTED) for v in nodes}
        edges = VGroup(*[Line(nodes[u][2], nodes[v][2], color=MUTED, stroke_width=1.4, stroke_opacity=0.5) for u, v in G.edges()])
        lv = VGroup(*[T(f"营养级 {i + 1}", 20, MUTED).move_to([-5.6, -2.4 + i * 1.45, 0]) for i in range(4)])
        with self.say("f1"):
            self.play(FadeIn(tag), Create(edges), *[GrowFromCenter(d) for d in dots.values()], run_time=1.6)
            self.play(FadeIn(lv), run_time=0.6)
            cap = T("示意图", 20, MUTED).to_corner(DR, buff=0.3)
            self.play(FadeIn(cap), run_time=0.4)
        keep = list(self.mobjects)
        self.play(*[FadeOut(m) for m in keep], run_time=0.5)
        with self.say("f1b"):
            self.clip_on("yt_chesapeake_food_cbp.mp4", "center", "视频：Chesapeake Bay Program · YouTube", start=15)
        self.clip_off()
        self.play(*[FadeIn(m) for m in keep], run_time=0.5)
        with self.say("f2"):
            self.play(*[dots[v].animate.set_color(BLUE if nodes[v][0] == 0 else GREEN) for v in nodes], run_time=1.0)
            hb = SurroundingRectangle(VGroup(*[dots[v] for v in nodes if nodes[v][0] == 0]), color=BLUE, buff=0.25, corner_radius=0.3)
            hg = SurroundingRectangle(VGroup(*[dots[v] for v in nodes if nodes[v][0] == 1]), color=GREEN, buff=0.25, corner_radius=0.3)
            tb = T("浮游", 28, BLUE).next_to(hb, UP, buff=0.1)
            tg = T("底栖", 28, GREEN).next_to(hg, UP, buff=0.1)
            self.play(Create(hb), Create(hg), FadeIn(tb), FadeIn(tg), run_time=1.2)
        with self.say("f3"):
            bands = VGroup(*[Rectangle(width=9.6, height=0.9, stroke_width=0, fill_color=GOLD, fill_opacity=0.08).move_to([0.2, -2.4 + i * 1.45, 0]) for i in range(4)])
            self.play(FadeIn(bands), run_time=0.8)
            self.play(Indicate(lv, color=GOLD), run_time=1.0)
        clear(self, keep=[tag])
        with self.say("f4"):
            P = nx.random_partition_graph([10, 10, 10], 0.5, 0.03, seed=8)
            part = {v: i for i, blk in enumerate(P.graph["partition"]) for v in blk}
            pp = fit(nx.spring_layout(P, seed=1, k=0.6), (-4.0, 4.0, -2.8, 2.4))
            vn = NetView(P, pp, color=MUTED, rmin=0.09, rk=0.0, eo=0.4)
            self.play(FadeIn(vn.group), run_time=1.0)
            cl = [GREEN, VIOLET, RED]
            self.play(*[vn.dots[v].animate.set_color(cl[part[v]]) for v in P], run_time=1.0)
            mod = T("疾病模块", 26, RED).next_to(VGroup(*[vn.dots[v] for v in P if part[v] == 2]), DOWN, buff=0.2)
            self.play(FadeIn(mod), run_time=0.6)
        clear(self)

    # ------------------------------------------------------------------ limits
    def limits(self):
        tag = self.chapter("三  局限")
        K = self.K
        H = K.copy(); Qs = []
        for i in range(K.number_of_edges()):
            Qs.append(nx.community.modularity(K, list(nx.connected_components(H))))
            b = eb(H); e = max(b, key=b.get); H.remove_edge(*e)
        best = int(np.argmax(Qs))
        H = K.copy()
        for i in range(best):
            b = eb(H); e = max(b, key=b.get); H.remove_edge(*e)
        ncom = nx.number_connected_components(H)
        print(f"[gn] best Q {max(Qs):.3f} after {best} removals, {ncom} communities")
        with self.say("l1"):
            tree = VGroup(*[Line([0, 2 - i * 0.9, 0], [x, 1.1 - i * 0.9, 0], color=MUTED, stroke_width=3) for i in range(4) for x in (-1.6 + 0.5 * i, 1.6 - 0.5 * i)]).shift(LEFT * 3)
            cut = DashedLine(LEFT * 5.6, LEFT * 0.4, color=GOLD).shift(UP * 0.3)
            q = T("切在哪一层", 30, GOLD).next_to(cut, RIGHT, buff=0.3)
            self.play(FadeIn(tag), Create(tree), run_time=1.2)
            self.play(Create(cut), FadeIn(q), run_time=0.8)
            self.play(cut.animate.shift(DOWN * 1.2), q.animate.shift(DOWN * 1.2), run_time=1.0)
        clear(self, keep=[tag])
        ax = plain_axes([0, 78, 10], [0, 0.45, 0.1], 8.4, 4.4, xnums=[0, 20, 40, 60], ynums=[0, 0.2, 0.4]).shift(DOWN * 0.3 + LEFT * 0.6)
        xl = xlabel("已删除的边数", ax)
        yl = ylabel("模块度 Q", ax)
        cv = ax.plot_line_graph(list(range(len(Qs))), Qs, line_color=BLUE, add_vertex_dots=False, stroke_width=4)
        with self.say("l2"):
            self.play(Create(ax), FadeIn(xl), FadeIn(yl), run_time=1.0)
            self.play(Create(cv), run_time=2.0, rate_func=linear)
            pk = Dot(ax.c2p(best, Qs[best]), radius=0.11, color=GOLD)
            pl = T(f"删掉 {best} 条边 · {ncom} 个社团 · Q = {Qs[best]:.2f}", 24, GOLD).next_to(pk, UR, buff=0.15)
            self.play(FadeIn(pk, scale=2), FadeIn(pl), run_time=0.8)
        clear(self, keep=[tag])
        with self.say("l3"):
            f1 = VGroup(T("算一次全部边介数", 30), MathTex(r"O(mn)", font_size=48)).arrange(RIGHT, buff=0.4)
            f2 = VGroup(T("稀疏网络上的总时间", 30, RED), MathTex(r"O(n^3)", font_size=48, color=RED)).arrange(RIGHT, buff=0.4)
            VGroup(f1, f2).arrange(DOWN, buff=0.6).shift(UP * 0.4)
            self.play(Write(f1), run_time=1.2)
            self.play(Write(f2), run_time=1.2)
        clear(self, keep=[tag])
        with self.say("l4"):
            ring = VGroup()
            cl_pos = [np.array([2.6 * np.cos(a), 2.2 * np.sin(a) - 0.3, 0]) for a in np.linspace(0, 2 * PI, 9)[:-1]]
            for c in cl_pos:
                g = VGroup(*[Dot(c + 0.35 * np.array([np.cos(t), np.sin(t), 0]), radius=0.08, color=BLUE) for t in np.linspace(0, 2 * PI, 5)[:-1]])
                ring.add(g)
            links = VGroup(*[Line(cl_pos[i], cl_pos[(i + 1) % 8], color=MUTED, stroke_width=2, stroke_opacity=0.6) for i in range(8)])
            self.play(FadeIn(links), FadeIn(ring), run_time=1.0)
            merged = Ellipse(width=2.4, height=1.6, color=RED, stroke_width=4).move_to((cl_pos[0] + cl_pos[1]) / 2).rotate(np.arctan2(*(cl_pos[1] - cl_pos[0])[[1, 0]]))
            ml = T("被合并", 24, RED).next_to(merged, RIGHT, buff=0.1)
            self.play(Create(merged), FadeIn(ml), run_time=1.0)
            ov = VGroup(Circle(radius=0.9, color=GREEN, stroke_width=3).move_to(cl_pos[4] + RIGHT * 0.3),
                        Circle(radius=0.9, color=GOLD, stroke_width=3).move_to(cl_pos[4] + LEFT * 0.5))
            ol = T("重叠", 24, GOLD).next_to(ov, DOWN, buff=0.1)
            self.play(Create(ov), FadeIn(ol), run_time=1.0)
        clear(self)
