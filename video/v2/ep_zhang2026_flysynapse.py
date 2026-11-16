"""Paper explainer: 共同接收者上的突触位置预测输入神经元之间的连接."""
import networkx as nx
import numpy as np

from common import *  # noqa: F401,F403
from ep_robustness import counter

TITLE = "突触落在哪里：从共同接收者读出看不见的连接"

LINES = {
    # hook
    "h1": "连接组，是一个神经系统里所有神经元和连接的地图。通常，每个神经元被画成一个点，连接就是点之间的边。",
    "h2": "但真实的神经元，是一棵伸展的树。输入信号通过突触，落在不同的枝条上。",
    "h2b": "画面里，是一个成年果蝇大脑的完整连接组，每一条细线，都是一个神经元。",
    "h3": "同样来自两个输入、同样多的突触，可以挤在同一根小枝上，也可以分散在相距很远的分支上。",
    "h4": "可在连接图里，这两种情况一模一样，位置的信息就被丢掉了。",
    "h5": "【慢】这项研究要检验的是：输入落在哪里，能告诉我们网络里别处的连接。",
    # parts
    "k0": "这一期分四部分。",
    "k1": "第一部分，三细胞的问题设定，以及距离怎么量。",
    "k2": "第二部分，两个逐步收紧的检验。",
    "k3": "第三部分，用位置信息预测从没见过的连接。",
    "k4": "第四部分，意义和局限。",
    # three cells
    "t1": "先看第一部分。三个细胞：输入源甲和乙，都向同一个接收神经元丙发出连接。右边是丙的树突，也就是它接收输入的枝条。",
    "t2": "能看到的，是丙的树突上，哪些突触来自甲，标成黄色；哪些来自乙，标成紫色。",
    "t2b": "在电子显微镜重建出的神经元上，每个突触的位置都能被一一标出来，就像画面里这样。",
    "t3": "真正关心的，是甲到乙这条连接。注意，它的两个端点都不在丙身上。",
    "t4": "如果甲到乙存在，三条边就构成一个前馈环。这项研究要做的，是只看丙身上的输入分布，去读出这条看不见的边。",
    "t4b": "前馈环是一种常见的网络基序。网络基序这一页有画面上的交互演示：在基因调控里，前馈环能过滤掉太短的输入脉冲。",
    "t5": "一条连接，至少要有五条接触记录才算存在。这个阈值贯穿整项研究。",
    "t6": "接收者选的是果蝇的下行神经元。它们从脑一直延伸到腹神经索，身份可以辨认，输入又很丰富。",
    "t6b": "下行神经元把大脑的指令传给控制腿的神经，比如让果蝇开始走路。画面里，是果蝇大脑和身体的三维重建。",
    # distance
    "p1": "然后是距离。这里不用直线距离，而是沿着神经元的骨架，也就是树的中轴线，走过的最短路径，就是这条绿色的路。",
    "p2": "骨架本身就是一棵树。所以这其实就是网络里的最短路径问题，只不过边长是真实的物理长度。",
    "p3": "对甲的每一个输入位置，找到离它最近的乙输入，量出这段路径，就是这些黄色的路。",
    "p4": "写成公式，就是右上角这个式子。",
    "p4b": "x 是甲的一个输入位置；P 是乙落在丙上的所有输入位置。在这些位置里取最近的一个，量沿骨架的距离。",
    # first test
    "r1": "下面进入第二部分，第一个检验。先固定一条连接：乙连向丙，两者都是下行神经元。",
    "r2": "再把丙的其他输入源分成两组：同时也连向乙的，叫共享源，标成黄色；不连向乙的，叫其他源，标成灰色。",
    "r3": "比较的是：哪一组的输入，离乙的输入更近。画面是示意。",
    "r4": "这张图，每组柱子的高度是平均路径距离。在第一个连接组的一万三千多条连接里，共享源是六十点八微米，其他源是七十点二微米，近了九点四微米。",
    "r5": "在独立重建的第二个连接组里，是五十一点四对五十九点四，近了八微米，方向一致。",
    "r6": "按接收者来看，八成以上是这个方向。注意，也有红色这部分相反的例子。",
    "r7": "举一个具体的环路。在咽下神经节里，十二个共享源的输入，平均距离是十点七微米，其他输入是十九微米。",
    # second test
    "c1": "但不同的源，本来就可能落在接收者的不同位置。所以第二个检验，把甲在丙上的输入完全固定，就是这些黄点。",
    "c2": "只换伙伴：紫色是收到甲连接的伙伴，青色是完全没收到甲连接的伙伴。",
    "c3": "还有一个隐蔽的偏差：伙伴在丙上的位点越多，最近距离自然就越小。你看，位点从两个加到十六个，最近距离一直在缩短。",
    "c4": "所以把参照位点统一成三个，用右上角这个式子来算。",
    "c4b": "【慢】它的意思是：从伙伴的所有位点里任取三个，求最近距离；再对所有三点组合取平均。这样，位点多少就不再影响比较。",
    "c5": "这样比较，在第一个连接组里，相连伙伴近了九点一四微米，九百二十二个接收者中，有七百四十九个方向一致。",
    "c6": "在第二个连接组里，近了十点一五微米，五百八十九个接收者中，有四百八十三个一致。",
    # prediction
    "m1": "下面进入第三部分，预测。用两百个源细胞之间的连接训练模型，再用另外两百个、完全不重叠的细胞来测试。",
    "m2": "左边的计数模型，只用四个特征，比如各自给丙多少输入、丙有多大；右边的空间模型，再加入距离和离散度，一共二十个特征。",
    "m3": "连接很稀疏。测试集里真正相连的，也就是正例，只占百分之三到四。",
    "m3b": "平均精度，衡量的是把候选连接按预测概率排序以后，排在前面的有多少是真的。随机排序时，它约等于正例的比例。",
    "m4": "这张图，纵轴是平均精度，虚线是随机水平。第一个连接组里，加入空间特征后，从零点零八九升到零点一六一。",
    "m5": "第二个连接组，从零点零六九升到零点一一四。",
    "m6": "不过，每个连接组只做了一次划分，这个对比没有给出置信区间。",
    # meaning & limits
    "l1": "最后是第四部分。这项研究提醒我们：哪怕在突触级的连接组里，把神经元压缩成一个点，也会丢掉信息。",
    "l2": "在脑影像的网络分析里，节点是脑区。节点内部的空间组织，同样可能携带连接的线索。",
    "l3": "局限也要看清。第一，这是一篇还在投稿中的稿件，尚未经过同行评审。",
    "l4": "第二，相关不等于因果。三个细胞的枝条在同一区域交汇，既容易形成连接，也会让输入靠近。",
    "l5": "第三，每个果蝇连接组只来自一只动物；线虫数据方向相同，但接收者很少；另一种海洋蠕虫的幼虫只有四条连接，方向也不一致。",
    "l6": "【慢】一句话：神经元不是一个点，输入落在哪里，也反映着网络的结构。",
    # recap
    "z0": "好，我们来总结一下。",
    "z1": "第一，相连的输入源，它们的输入在共同接收者上靠得更近，两个果蝇连接组方向一致。",
    "z2": "第二，固定输入位置、统一参照位点数以后，这个关系依然存在。",
    "z3": "第三，加入位置信息，能改善对从没见过的神经元之间连接的预测。",
}

A_COL, B_COL, O_COL, BP_COL = GOLD, VIOLET, MUTED, "#4fc3d9"


# ----------------------------------------------------------------------------- neuron trees
def make_tree(seed, root=(0, -3.0), length=1.5, depth=4, spread=0.72, seg=0.22, up=PI / 2):
    """Random branching skeleton. Returns graph (node -> pos), list of (start, end) branch node ranges, leaf-branch ids."""
    rng = np.random.default_rng(seed)
    G = nx.Graph()
    G.add_node(0, pos=np.array([*root, 0.0]), br=0)
    branches = []

    def grow(parent, ang, L, lvl, bid):
        n = max(2, int(L / seg))
        prev = parent
        p = G.nodes[parent]["pos"]
        ids = []
        for i in range(n):
            ang_i = ang + rng.normal(0, 0.08)
            q = p + L / n * np.array([np.cos(ang_i), np.sin(ang_i), 0])
            k = G.number_of_nodes()
            G.add_node(k, pos=q, br=bid)
            G.add_edge(prev, k, w=np.linalg.norm(q - p))
            prev, p = k, q
            ids.append(k)
        branches.append(ids)
        if lvl < depth:
            for s in (-1, 1):
                grow(prev, ang + s * spread * rng.uniform(0.6, 1.2), L * rng.uniform(0.6, 0.78), lvl + 1, len(branches))
    grow(0, up, length * 1.25, 1, 0)
    return G, branches


def tree_mob(G, color=INK, width=4, op=0.85):
    pos = nx.get_node_attributes(G, "pos")
    return VGroup(*[Line(pos[u], pos[v], color=color, stroke_width=width, stroke_opacity=op) for u, v in G.edges()])


def subtree_nodes(G, branches, bid):
    """All nodes in branch bid and its descendants (branch bid's first node defines the cut)."""
    first = branches[bid][0]
    H = G.copy()
    # parent of first node = smaller-index neighbour not in the branch
    par = min(G.neighbors(first))
    H.remove_edge(par, first)
    return nx.node_connected_component(H, first)


def nearest(G, src, targets):
    d = nx.single_source_dijkstra_path_length(G, src, weight="w")
    t = min(targets, key=lambda x: d[x])
    return t, d[t]


class Episode(Narrated):
    LINES = LINES

    def construct(self):
        self.hook()
        self.parts()
        self.three()
        self.distance()
        self.first_test()
        self.second_test()
        self.prediction()
        self.meaning()
        self.recap()

    def clear(self, rt=0.8, keep=None):
        self.play(*[FadeOut(m) for m in self.mobjects if m is not keep], run_time=rt)

    def syn(self, G, nodes, col, r=0.075):
        pos = nx.get_node_attributes(G, "pos")
        return VGroup(*[Dot(pos[v], radius=r, color=col) for v in nodes])

    # ------------------------------------------------------------------ hook
    def hook(self):
        rng = np.random.default_rng(1)
        G = nx.connected_watts_strogatz_graph(24, 4, 0.3, seed=2)
        P = nx.spring_layout(G, seed=1)
        pos = {v: np.array([P[v][0] * 4.5, P[v][1] * 2.8, 0]) for v in G}
        dots = {v: Dot(pos[v], radius=0.12, color=BLUE) for v in G}
        ed = VGroup(*[Line(pos[u], pos[v], color=MUTED, stroke_width=2, stroke_opacity=0.6) for u, v in G.edges()])
        with self.say("h1") as d:
            self.play(LaggedStart(*[GrowFromCenter(x) for x in dots.values()], lag_ratio=0.03), run_time=d * 0.4)
            self.play(Create(ed), run_time=d * 0.4)
        c = min(G, key=lambda v: np.linalg.norm(pos[v]))
        T0, br = make_tree(5, root=(0, -3.1), length=1.5, depth=4)
        tree = tree_mob(T0, BLUE, 4)
        with self.say("h2") as d:
            self.play(*[FadeOut(x) for v, x in dots.items() if v != c], FadeOut(ed), run_time=0.8)
            self.play(dots[c].animate.move_to([0, -3.1, 0]), run_time=0.6)
            self.play(Create(tree), FadeOut(dots[c]), run_time=d * 0.5)
            leaves = [b[-1] for b in br][-12:]
            sy = self.syn(T0, leaves[::2], GOLD)
            self.play(LaggedStart(*[FadeIn(s, scale=0.5) for s in sy], lag_ratio=0.1), run_time=1.0)
        keep = list(self.mobjects)
        self.remove(*keep)
        with self.say("h2b") as d:
            self.clip_on("yt_fly_connectome_cambridge.mp4", "center", "视频：Cambridge University · YouTube", start=5)
        self.clip_off()
        self.add(*keep)
        # two receivers: clustered vs spread
        TL, bL = make_tree(5, root=(-3.4, -3.1), length=1.2, depth=4, seg=0.1)
        TR, bR = make_tree(5, root=(3.4, -3.1), length=1.2, depth=4, seg=0.1)
        left, right = tree_mob(TL, INK, 3, 0.7), tree_mob(TR, INK, 3, 0.7)
        sub = sorted(subtree_nodes(TL, bL, 2))
        rngs = np.random.default_rng(3)
        aL = rngs.choice(sub, 4, replace=False); bLn = rngs.choice([x for x in sub if x not in aL], 4, replace=False)
        allR = list(TR.nodes)[5:]
        s1 = sorted(subtree_nodes(TR, bR, 2)); s2 = sorted(subtree_nodes(TR, bR, 9))
        aR = rngs.choice(s1, 4, replace=False); bRn = rngs.choice(s2, 4, replace=False)
        with self.say("h3") as d:
            self.play(FadeOut(tree), FadeOut(sy), run_time=0.6)
            self.play(Create(left), Create(right), run_time=1.2)
            self.play(FadeIn(self.syn(TL, aL, A_COL)), FadeIn(self.syn(TL, bLn, B_COL)),
                      FadeIn(self.syn(TR, aR, A_COL)), FadeIn(self.syn(TR, bRn, B_COL)), run_time=1.0)
            l1 = T("挤在一起", 26, INK).move_to([-3.4, 3.3, 0]); l2 = T("分散很远", 26, INK).move_to([3.4, 3.3, 0])
            self.play(FadeIn(l1), FadeIn(l2), run_time=0.6)
        with self.say("h4") as d:
            self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.6)

            def mini(cx):
                A = Circle(radius=0.3, color=A_COL, fill_color=BG, fill_opacity=1).move_to([cx - 1.0, 1.2, 0]).add(T("甲", 24, A_COL).move_to([cx - 1.0, 1.2, 0]))
                B = Circle(radius=0.3, color=B_COL, fill_color=BG, fill_opacity=1).move_to([cx + 1.0, 1.2, 0]).add(T("乙", 24, B_COL).move_to([cx + 1.0, 1.2, 0]))
                C = Circle(radius=0.3, color=INK, fill_color=BG, fill_opacity=1).move_to([cx, -0.6, 0]).add(T("丙", 24, INK).move_to([cx, -0.6, 0]))
                a1 = Arrow(A.get_center(), C.get_center(), buff=0.35, color=MUTED, stroke_width=4)
                a2 = Arrow(B.get_center(), C.get_center(), buff=0.35, color=MUTED, stroke_width=4)
                return VGroup(a1, a2, A, B, C)
            m1, m2 = mini(-3.4), mini(3.4)
            eq = T("=", 60, INK).move_to([0, 0.3, 0])
            self.play(FadeIn(m1), FadeIn(m2), run_time=1.0)
            self.play(Write(eq), run_time=0.6)
        with self.say("h5") as d:
            self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.6)
            q = T("输入的位置，可能藏着别处的连接", 44, INK, weight=BOLD)
            self.play(Write(q), run_time=1.6)
        self.clear()

    def parts(self):
        head, items = slide("这一期分四部分", ["一  三个细胞与路径距离", "二  两个检验", "三  预测没见过的连接", "四  意义与局限"])
        with self.say("k0") as d:
            self.play(FadeIn(head, shift=RIGHT * 0.3), run_time=0.6)
        for k, it in zip(("k1", "k2", "k3", "k4"), items):
            with self.say(k) as d:
                self.play(FadeIn(it, shift=RIGHT * 0.3), run_time=0.6)
        self.wait(0.6)
        self.play(FadeOut(head), FadeOut(items), run_time=0.6)

    def recap(self):
        head, items = slide("小结", ["相连输入源的输入，在接收者上更靠近", "固定输入、统一参照位点后依然成立", "位置信息改善对新细胞连接的预测"], accent=VIOLET)
        with self.say("z0") as d:
            self.play(FadeIn(head, shift=RIGHT * 0.3), run_time=0.6)
        for k, it in zip(("z1", "z2", "z3"), items):
            with self.say(k) as d:
                self.play(FadeIn(it, shift=RIGHT * 0.3), run_time=0.6)
        self.wait(1.0)
        self.play(FadeOut(head), FadeOut(items), run_time=0.8)

    # ------------------------------------------------------------------ three cells
    def three(self):
        tag = self.chapter("一  三个细胞与路径距离")
        Pa, Pb, Pc = np.array([-4.6, 1.8, 0]), np.array([-4.6, -1.4, 0]), np.array([-1.6, 0.2, 0])

        def node(p, s, c):
            return Circle(radius=0.42, color=c, stroke_width=4, fill_color=BG, fill_opacity=1).move_to(p).add(T(s, 30, c).move_to(p))
        A, B, C = node(Pa, "甲", A_COL), node(Pb, "乙", B_COL), node(Pc, "丙", INK)
        ac = Arrow(Pa, Pc, buff=0.5, color=A_COL, stroke_width=5)
        bc = Arrow(Pb, Pc, buff=0.5, color=B_COL, stroke_width=5)
        TC, bC = make_tree(11, root=(3.4, -3.2), length=1.5, depth=4, seg=0.1)
        tree = tree_mob(TC, INK, 3.5, 0.8)
        rng = np.random.default_rng(4)
        allv = list(TC.nodes)[6:]
        sideA = sorted(subtree_nodes(TC, bC, 1))
        aN = list(rng.choice(sideA, 6, replace=False))
        bN = list(rng.choice([v for v in sideA if v not in aN], 5, replace=False))
        with self.say("t1") as d:
            self.play(FadeIn(tag), GrowFromCenter(A), GrowFromCenter(B), GrowFromCenter(C), run_time=1.0)
            self.play(GrowArrow(ac), GrowArrow(bc), run_time=1.0)
            self.play(Create(tree), run_time=1.2)
            cl = T("丙的树突", 24, MUTED).next_to(tree, DOWN, buff=0.05).shift(RIGHT * 1.8)
            self.play(FadeIn(cl), run_time=0.4)
        sa, sb = self.syn(TC, aN, A_COL, 0.09), self.syn(TC, bN, B_COL, 0.09)
        with self.say("t2") as d:
            self.play(LaggedStart(*[TransformFromCopy(Dot(Pc, radius=0.09, color=A_COL), s) for s in sa], lag_ratio=0.1), run_time=1.4)
            self.play(LaggedStart(*[TransformFromCopy(Dot(Pc, radius=0.09, color=B_COL), s) for s in sb], lag_ratio=0.1), run_time=1.4)
        keep = list(self.mobjects)
        self.remove(*keep)
        with self.say("t2b") as d:
            self.clip_on("yt_janelia_synapses.mp4", "center", "视频：HHMI Janelia Research Campus · YouTube", start=8)
        self.clip_off()
        self.add(*keep)
        with self.say("t3") as d:
            ab = DashedLine(Pa + DOWN * 0.45, Pb + UP * 0.45, color=GREEN, stroke_width=5).add_tip(tip_length=0.22, tip_width=0.2)
            qm = T("?", 40, GREEN, weight=BOLD).next_to(ab, LEFT, buff=0.2)
            self.play(Create(ab), FadeIn(qm), run_time=1.2)
        with self.say("t4") as d:
            tri = Polygon(Pa, Pb, Pc, color=GREEN, fill_opacity=0.08, stroke_width=0)
            ffl = T("前馈环", 30, GREEN, weight=BOLD).move_to([-2.4, 2.9, 0])
            self.play(FadeIn(tri), FadeIn(ffl), run_time=1.0)
            self.play(Indicate(sa, color=A_COL), Indicate(sb, color=B_COL), run_time=1.4)
        keep = list(self.mobjects)
        self.remove(*keep)
        with self.say("t4b") as d:
            self.clip_on("ffl_pulse.mp4", "full", "本站交互演示：前馈环", start=0.3)
        self.wait(max(0.05, 14.0 - (self.renderer.time - self._clip['t0'])))
        self.clip_off()
        self.add(*keep)
        with self.say("t5") as d:
            recs = VGroup(*[RoundedRectangle(corner_radius=0.05, width=0.35, height=0.5, fill_color=GREEN, fill_opacity=0.8, stroke_width=0) for _ in range(5)]).arrange(RIGHT, buff=0.1)
            lab = T("≥ 5 条接触记录", 26, GREEN)
            g = VGroup(recs, lab).arrange(RIGHT, buff=0.3).move_to([-3.2, -2.9, 0])
            self.play(LaggedStart(*[FadeIn(r, shift=UP * 0.2) for r in recs], lag_ratio=0.2), FadeIn(lab), run_time=1.4)
        with self.say("t6") as d:
            self.play(*[FadeOut(m) for m in (A, B, C, ac, bc, ab, qm, tri, ffl, g)], run_time=0.6)
            # schematic fly: brain + ventral nerve cord with descending neuron
            brain = Ellipse(width=3.6, height=2.0, color=MUTED, stroke_width=3).move_to([-3.4, 1.6, 0])
            vnc = RoundedRectangle(corner_radius=0.4, width=1.2, height=3.0, color=MUTED, stroke_width=3).move_to([-3.4, -1.6, 0])
            dn = VGroup(Dot([-3.4, 1.6, 0], radius=0.12, color=INK), Line([-3.4, 1.6, 0], [-3.4, -2.6, 0], color=INK, stroke_width=4))
            lb = T("脑", 24, MUTED).next_to(brain, LEFT, buff=0.2)
            lv = T("腹神经索", 24, MUTED).next_to(vnc, LEFT, buff=0.2)
            ld = T("下行神经元", 26, INK, weight=BOLD).next_to(dn, RIGHT, buff=0.3).shift(UP * 0.3)
            self.play(Create(brain), Create(vnc), FadeIn(lb), FadeIn(lv), run_time=1.0)
            self.play(Create(dn), FadeIn(ld), run_time=1.0)
        keep = list(self.mobjects)
        self.remove(*keep)
        with self.say("t6b") as d:
            self.clip_on("yt_fly_connectome_cambridge.mp4", "center", "视频：Cambridge University · YouTube", start=24)
        self.clip_off()
        self.add(*keep)
        self.clear()

    # ------------------------------------------------------------------ path distance
    def distance(self):
        tag = self.chapter("一  三个细胞与路径距离")
        TC, bC = make_tree(11, root=(0, -3.2), length=1.6, depth=4, seg=0.1)
        pos = nx.get_node_attributes(TC, "pos")
        tree = tree_mob(TC, INK, 3.5, 0.75)
        L1 = sorted(subtree_nodes(TC, bC, 1)); L2 = sorted(subtree_nodes(TC, bC, len(bC) // 2 + 1))
        u = max(L1, key=lambda v: pos[v][1]); w = max(L2, key=lambda v: pos[v][1])
        with self.say("p1") as d:
            self.play(FadeIn(tag), Create(tree), run_time=1.2)
            du, dw = Dot(pos[u], radius=0.12, color=A_COL), Dot(pos[w], radius=0.12, color=B_COL)
            self.play(FadeIn(du), FadeIn(dw), run_time=0.5)
            st = DashedLine(pos[u], pos[w], color=MUTED, stroke_width=3)
            sl = T("直线", 24, MUTED).next_to(st, UP, buff=0.1)
            self.play(Create(st), FadeIn(sl), run_time=0.8)
            path = nx.shortest_path(TC, u, w, weight="w")
            pl = VMobject(color=GREEN, stroke_width=7).set_points_as_corners([pos[v] for v in path])
            walker = Dot(pos[u], radius=0.1, color=GREEN)
            self.play(Create(pl), MoveAlongPath(walker, pl), run_time=d * 0.4)
            gl = T("沿骨架的路径", 24, GREEN).next_to(pos[path[len(path) // 2]], RIGHT, buff=0.3)
            self.play(FadeIn(gl), run_time=0.4)
        with self.say("p2") as d:
            self.play(*[FadeOut(m) for m in (st, sl, walker)], run_time=0.4)
            nodes = VGroup(*[Dot(pos[v], radius=0.04, color=BLUE) for v in TC])
            self.play(FadeIn(nodes, lag_ratio=0.005), run_time=1.0)
            gr = T("一棵树：边长 = 物理长度", 26, BLUE).to_corner(UR, buff=0.5)
            self.play(FadeIn(gr), run_time=0.6)
        rng = np.random.default_rng(7)
        side = sorted(subtree_nodes(TC, bC, 1))
        aN = list(rng.choice(list(TC.nodes)[8:], 6, replace=False))
        bN = list(rng.choice([v for v in side if v not in aN], 4, replace=False))
        with self.say("p3") as d:
            self.play(FadeOut(pl), FadeOut(gl), FadeOut(du), FadeOut(dw), FadeOut(nodes), run_time=0.5)
            sa, sb = self.syn(TC, aN, A_COL, 0.1), self.syn(TC, bN, B_COL, 0.1)
            self.play(FadeIn(sa), FadeIn(sb), run_time=0.6)
            per = max(0.4, d * 0.6 / len(aN))
            paths = VGroup()
            for a in aN:
                t, _ = nearest(TC, a, bN)
                p = nx.shortest_path(TC, a, t, weight="w")
                if len(p) < 2:
                    continue
                pm = VMobject(color=A_COL, stroke_width=5, stroke_opacity=0.8).set_points_as_corners([pos[v] for v in p])
                paths.add(pm)
                self.play(Create(pm), run_time=per)
        with self.say("p4") as d:
            f = MathTex(r"d_{BC}(x)=\min_{y\in P_{BC}} d_C(x,y)", font_size=44, color=INK).to_corner(UR, buff=0.5).shift(DOWN * 0.7)
            bg = BackgroundRectangle(f, color=BG, fill_opacity=0.9, buff=0.12)
            self.play(FadeOut(gr), FadeIn(bg), Write(f), run_time=1.4)
        with self.say("p4b") as d:
            n1 = T("x：甲的一个输入位置    P：乙在丙上的输入", 20, MUTED).next_to(f, DOWN, buff=0.2)
            self.play(FadeIn(n1), run_time=0.6)
            self.play(Indicate(f, color=GOLD), run_time=1.2)
        self.clear()

    # ------------------------------------------------------------------ first test
    def first_test(self):
        tag = self.chapter("二  两个检验")
        Pb, Pc = np.array([-5.2, 1.6, 0]), np.array([-5.2, -1.4, 0])
        B = Circle(radius=0.38, color=B_COL, stroke_width=4).move_to(Pb).add(T("乙", 26, B_COL).move_to(Pb))
        C = Circle(radius=0.38, color=INK, stroke_width=4).move_to(Pc).add(T("丙", 26, INK).move_to(Pc))
        bc = Arrow(Pb, Pc, buff=0.45, color=B_COL, stroke_width=5)
        TC, bC = make_tree(23, root=(1.6, -3.2), length=1.5, depth=4, seg=0.1)
        tree = tree_mob(TC, INK, 3, 0.7)
        with self.say("r1") as d:
            self.play(FadeIn(tag), GrowFromCenter(B), GrowFromCenter(C), run_time=0.8)
            self.play(GrowArrow(bc), Create(tree), run_time=1.4)
        srcs = VGroup(*[Circle(radius=0.22, color=c, stroke_width=3).move_to([-3.4, 2.6 - i * 0.62, 0]) for i, c in enumerate([A_COL] * 4 + [O_COL] * 5)])
        rng = np.random.default_rng(9)
        side = sorted(subtree_nodes(TC, bC, 1))
        far = [v for v in list(TC.nodes)[10:] if v not in side]
        bN = list(rng.choice(side, 5, replace=False))
        aN = list(rng.choice([v for v in side if v not in bN], 7, replace=False))
        oN = list(rng.choice(far, 9, replace=False))
        with self.say("r2") as d:
            self.play(LaggedStart(*[GrowFromCenter(s) for s in srcs], lag_ratio=0.08), run_time=1.0)
            toB = VGroup(*[Arrow(s.get_center(), Pb, buff=0.4, color=A_COL, stroke_width=2.5, max_tip_length_to_length_ratio=0.08) for s in srcs[:4]])
            self.play(Create(toB), run_time=1.0)
            l1 = T("共享源", 24, A_COL).next_to(srcs[0], RIGHT, buff=0.25)
            l2 = T("其他源", 24, O_COL).next_to(srcs[5], RIGHT, buff=0.25)
            self.play(FadeIn(l1), FadeIn(l2), run_time=0.6)
        sa, sb, so = self.syn(TC, aN, A_COL, 0.09), self.syn(TC, bN, B_COL, 0.11), self.syn(TC, oN, O_COL, 0.09)
        with self.say("r3") as d:
            self.play(FadeIn(sb), run_time=0.6)
            self.play(FadeIn(sa), FadeIn(so), run_time=0.8)
            ring = Circle(radius=1.0, color=GREEN, stroke_width=3).move_to(VGroup(sa, sb).get_center())
            ring.surround(VGroup(sa, sb), buffer_factor=1.15)
            sch = T("示意", 20, MUTED).to_corner(DR, buff=0.4)
            self.play(Create(ring), FadeIn(sch), run_time=1.0)
        self.clear(0.6, keep=tag)
        # bar comparison
        ax_y0 = -2.6
        H = 0.055

        def pair(cx, a, b, name, n, diff):
            r1 = Rectangle(width=1.0, height=a * H, fill_color=A_COL, fill_opacity=0.9, stroke_width=0).move_to([cx - 0.6, ax_y0, 0], aligned_edge=DOWN)
            r2 = Rectangle(width=1.0, height=b * H, fill_color=O_COL, fill_opacity=0.9, stroke_width=0).move_to([cx + 0.6, ax_y0, 0], aligned_edge=DOWN)
            v1 = T(f"{a:.1f}", 24, A_COL).next_to(r1, UP, buff=0.1)
            v2 = T(f"{b:.1f}", 24, O_COL).next_to(r2, UP, buff=0.1)
            nm = VGroup(T(name, 26, INK), T(n, 20, MUTED)).arrange(DOWN, buff=0.1).next_to([cx, ax_y0, 0], DOWN, buff=0.2)
            df = T(diff, 30, GREEN, weight=BOLD).move_to([cx, ax_y0 + b * H + 0.9, 0])
            return VGroup(r1, r2), VGroup(v1, v2), nm, df
        base = Line([-5.5, ax_y0, 0], [5.5, ax_y0, 0], color=MUTED)
        key = VGroup(VGroup(Square(0.25, fill_color=A_COL, fill_opacity=0.9, stroke_width=0), T("共享源", 22, INK)).arrange(RIGHT, buff=0.12),
                     VGroup(Square(0.25, fill_color=O_COL, fill_opacity=0.9, stroke_width=0), T("其他源", 22, INK)).arrange(RIGHT, buff=0.12),
                     T("平均路径距离 (μm)", 22, MUTED)).arrange(RIGHT, buff=0.5).to_edge(UP, buff=0.5).shift(RIGHT * 1.5)
        p1 = pair(-3.0, 60.77, 70.18, "MaleCNS", "13,318 条连接", "−9.4 μm")
        p2 = pair(3.0, 51.37, 59.36, "FlyWire", "5,807 条连接", "−8.0 μm")
        with self.say("r4") as d:
            self.play(Create(base), FadeIn(key), FadeIn(p1[2]), run_time=0.8)
            self.play(*[GrowFromEdge(r, DOWN) for r in p1[0]], run_time=1.2)
            self.play(FadeIn(p1[1]), run_time=0.5)
            self.play(FadeIn(p1[3], shift=DOWN * 0.2), run_time=0.6)
        with self.say("r5") as d:
            self.play(FadeIn(p2[2]), *[GrowFromEdge(r, DOWN) for r in p2[0]], run_time=1.2)
            self.play(FadeIn(p2[1]), FadeIn(p2[3], shift=DOWN * 0.2), run_time=0.8)
        with self.say("r6") as d:
            self.play(*[FadeOut(m) for m in (base, key, *p1, *p2)], run_time=0.6)
            rows = VGroup()
            for name, pct in (("MaleCNS", 82.7), ("FlyWire", 80.7)):
                tr = Rectangle(width=8, height=0.6, stroke_color=MUTED, stroke_width=1.5)
                fl = Rectangle(width=8 * pct / 100, height=0.6, fill_color=GREEN, fill_opacity=0.85, stroke_width=0).move_to(tr, aligned_edge=LEFT)
                rest = Rectangle(width=8 * (1 - pct / 100), height=0.6, fill_color=RED, fill_opacity=0.6, stroke_width=0).move_to(tr, aligned_edge=RIGHT)
                rows.add(VGroup(T(name, 24, INK).next_to(tr, LEFT, buff=0.3), tr, fl, rest, T(f"{pct}%", 24, BG, weight=BOLD).move_to(fl)))
            rows.arrange(DOWN, buff=0.6).shift(RIGHT * 0.6)
            hd = T("接收者中：共享源更近的比例", 24, MUTED).next_to(rows, UP, buff=0.5)
            self.play(FadeIn(hd), *[FadeIn(r[0]) for r in rows], *[Create(r[1]) for r in rows], run_time=0.8)
            self.play(*[GrowFromEdge(r[2], LEFT) for r in rows], *[FadeIn(r[4]) for r in rows], run_time=1.0)
            self.play(*[FadeIn(r[3]) for r in rows], run_time=0.6)
            rl = T("反例", 22, RED).next_to(rows[1][3], DOWN, buff=0.15)
            self.play(FadeIn(rl), run_time=0.4)
        with self.say("r7") as d:
            self.play(*[FadeOut(m) for m in (rows, hd, rl)], run_time=0.5)
            P = {"AN19B014": np.array([-4.2, 1.6, 0]), "DNge006": np.array([-4.2, -1.4, 0]), "DNge072": np.array([-1.2, 0.1, 0])}
            cols = {"AN19B014": A_COL, "DNge006": B_COL, "DNge072": INK}
            circ = VGroup(*[VGroup(Dot(p, radius=0.16, color=cols[k]), T(k, 20, cols[k]).next_to(p, {"AN19B014": UP, "DNge006": DOWN, "DNge072": RIGHT}[k], buff=0.2)) for k, p in P.items()])
            arr = VGroup(Arrow(P["AN19B014"], P["DNge006"], buff=0.25, color=MUTED, stroke_width=3),
                         Arrow(P["AN19B014"], P["DNge072"], buff=0.25, color=MUTED, stroke_width=3),
                         Arrow(P["DNge006"], P["DNge072"], buff=0.25, color=MUTED, stroke_width=3))
            self.play(FadeIn(circ), Create(arr), run_time=1.0)
            gng = T("咽下神经节", 24, MUTED).move_to([-2.7, 2.9, 0])
            self.play(FadeIn(gng), run_time=0.4)
            bars = VGroup()
            for i, (v, c, nm) in enumerate(((10.7, A_COL, "12 个共享源"), (19.0, O_COL, "其他输入"))):
                r = Rectangle(width=v * 0.25, height=0.6, fill_color=c, fill_opacity=0.9, stroke_width=0).move_to([1.0, 0.8 - i * 1.2, 0], aligned_edge=LEFT)
                bars.add(VGroup(r, T(f"{v} μm", 24, c).next_to(r, RIGHT, buff=0.15), T(nm, 22, INK).next_to(r, UP, buff=0.1, aligned_edge=LEFT)))
            hd = T("到最近 DNge006 输入的平均距离", 20, MUTED).next_to(bars, UP, buff=0.35).align_to(bars, LEFT)
            self.play(FadeIn(hd), *[GrowFromEdge(b[0], LEFT) for b in bars], *[FadeIn(b[2]) for b in bars], run_time=1.2)
            self.play(*[FadeIn(b[1]) for b in bars], run_time=0.5)
        self.clear()

    # ------------------------------------------------------------------ second test
    def second_test(self):
        tag = self.chapter("二  两个检验")
        TC, bC = make_tree(31, root=(0, -3.3), length=1.5, depth=4, seg=0.1)
        pos = nx.get_node_attributes(TC, "pos")
        tree = tree_mob(TC, INK, 3, 0.7)
        rng = np.random.default_rng(12)
        sideL = sorted(subtree_nodes(TC, bC, 1)); sideR = [v for v in list(TC.nodes)[8:] if v not in sideL]
        aN = list(rng.choice(sideL, 5, replace=False))
        bN = list(rng.choice([v for v in sideL if v not in aN], 4, replace=False))
        bpN = list(rng.choice(sideR, 4, replace=False))
        sa = self.syn(TC, aN, A_COL, 0.1)
        with self.say("c1") as d:
            self.play(FadeIn(tag), Create(tree), run_time=1.2)
            self.play(FadeIn(sa), run_time=0.6)
            lock = T("甲的输入：固定不动", 24, A_COL).to_corner(UR, buff=0.5)
            self.play(FadeIn(lock), run_time=0.5)
        sb, sbp = self.syn(TC, bN, B_COL, 0.1), self.syn(TC, bpN, BP_COL, 0.1)
        with self.say("c2") as d:
            self.play(FadeIn(sb), run_time=0.7)
            l1 = T("相连伙伴", 24, B_COL).next_to(lock, DOWN, buff=0.3, aligned_edge=RIGHT)
            self.play(FadeIn(l1), run_time=0.4)
            self.play(FadeIn(sbp), run_time=0.7)
            l2 = T("零输入伙伴", 24, BP_COL).next_to(l1, DOWN, buff=0.2, aligned_edge=RIGHT)
            self.play(FadeIn(l2), run_time=0.4)
        # site-count bias: nearest distance from one fixed A input as partner sites grow
        x = aN[0]
        dist = nx.single_source_dijkstra_path_length(TC, x, weight="w")
        pool = sorted([v for v in list(TC.nodes)[8:] if v != x], key=lambda v: rng.random())
        with self.say("c3") as d:
            self.play(FadeOut(sb), FadeOut(sbp), FadeOut(l1), FadeOut(l2), sa.animate.set_opacity(0.3), run_time=0.5)
            xd = Dot(pos[x], radius=0.13, color=A_COL)
            self.play(FadeIn(xd), run_time=0.3)
            cnt = counter("伙伴位点数", "2", BP_COL).to_corner(UR, buff=0.5).shift(DOWN * 0.9)
            nd = counter("最近距离（示意）", "", INK).next_to(cnt, DOWN, buff=0.3)
            shown = VGroup()
            for k in (2, 6, 16):
                sites = pool[:k]
                near = min(dist[v] for v in sites)
                new = self.syn(TC, sites, BP_COL, 0.09)
                c2 = counter("伙伴位点数", str(k), BP_COL).move_to(cnt)
                n2 = counter("最近距离（示意）", f"{near:.1f}", INK).move_to(nd)
                if k == 2:
                    self.play(FadeIn(new), FadeIn(c2), FadeIn(n2), run_time=0.8)
                else:
                    self.play(Transform(shown, new), Transform(cnt_m, c2), Transform(nd_m, n2), run_time=0.8)
                    continue
                shown, cnt_m, nd_m = new, c2, n2
            self.add(shown)
        with self.say("c4") as d:
            self.play(FadeOut(shown), FadeOut(cnt_m), FadeOut(nd_m), FadeOut(xd), FadeOut(lock), run_time=0.5)
            f = MathTex(r"\tilde d(x,B)=\sum_{\ell=1}^{n-2}\frac{\binom{n-\ell}{2}}{\binom{n}{3}}\,d_{(\ell)}", font_size=44, color=INK)
            f.to_corner(UR, buff=0.5).shift(DOWN * 0.5)
            bg = BackgroundRectangle(f, color=BG, fill_opacity=0.9, buff=0.12)
            n3 = T("任取 3 个位点时，最近距离的期望", 22, MUTED).next_to(f, DOWN, buff=0.2)
            self.play(FadeIn(bg), Write(f), run_time=1.6)
        with self.say("c4b") as d:
            self.play(FadeIn(n3), run_time=0.5)
            self.play(Indicate(f, color=GOLD), run_time=1.2)
        self.clear(0.6, keep=tag)

        def stack(name, k, n, diff, y):
            tr = Rectangle(width=8, height=0.7, stroke_color=MUTED, stroke_width=1.5).move_to([0.6, y, 0])
            fl = Rectangle(width=8 * k / n, height=0.7, fill_color=GREEN, fill_opacity=0.85, stroke_width=0).move_to(tr, aligned_edge=LEFT)
            lab = T(name, 24, INK).next_to(tr, LEFT, buff=0.3)
            val = T(f"{k} / {n}", 24, BG, weight=BOLD).move_to(fl)
            df = T(diff, 26, GREEN, weight=BOLD).next_to(tr, UP, buff=0.12).align_to(tr, RIGHT)
            return VGroup(lab, tr), fl, val, df
        s1 = stack("MaleCNS", 749, 922, "相连伙伴近 9.14 μm", 0.8)
        s2 = stack("FlyWire", 483, 589, "相连伙伴近 10.15 μm", -1.4)
        hd = T("接收者中：相连伙伴更近的个数", 24, MUTED).move_to([0.6, 2.6, 0])
        with self.say("c5") as d:
            self.play(FadeIn(hd), FadeIn(s1[0]), run_time=0.6)
            self.play(GrowFromEdge(s1[1], LEFT), run_time=1.0)
            self.play(FadeIn(s1[2]), FadeIn(s1[3]), run_time=0.6)
        with self.say("c6") as d:
            self.play(FadeIn(s2[0]), GrowFromEdge(s2[1], LEFT), run_time=1.0)
            self.play(FadeIn(s2[2]), FadeIn(s2[3]), run_time=0.6)
        self.clear()

    # ------------------------------------------------------------------ prediction
    def prediction(self):
        tag = self.chapter("三  预测没见过的连接")
        rng = np.random.default_rng(2)
        tr = VGroup(*[Dot(radius=0.07, color=BLUE) for _ in range(200)]).arrange_in_grid(rows=10, cols=20, buff=0.12).move_to([-3.4, 0.6, 0])
        te = VGroup(*[Dot(radius=0.07, color=GOLD) for _ in range(200)]).arrange_in_grid(rows=10, cols=20, buff=0.12).move_to([3.4, 0.6, 0])
        with self.say("m1") as d:
            self.play(FadeIn(tag), FadeIn(tr, lag_ratio=0.003), run_time=1.0)
            lt = T("训练：200 个源细胞", 24, BLUE).next_to(tr, DOWN, buff=0.3)
            self.play(FadeIn(lt), run_time=0.4)
            self.play(FadeIn(te, lag_ratio=0.003), run_time=1.0)
            le = T("测试：另外 200 个", 24, GOLD).next_to(te, DOWN, buff=0.3)
            wall = DashedLine([0, 2.3, 0], [0, -1.6, 0], color=MUTED)
            self.play(FadeIn(le), Create(wall), run_time=0.6)
        with self.say("m2") as d:
            self.play(*[FadeOut(m) for m in (tr, te, lt, le, wall)], run_time=0.5)
            c1 = VGroup(T("计数模型", 30, MUTED, weight=BOLD), T("4 个特征", 24, MUTED)).arrange(DOWN, buff=0.15)
            c2 = VGroup(T("空间模型", 30, GREEN, weight=BOLD), T("20 个特征", 24, GREEN)).arrange(DOWN, buff=0.15)
            f1 = VGroup(*[RoundedRectangle(corner_radius=0.05, width=0.32, height=0.32, fill_color=MUTED, fill_opacity=0.8, stroke_width=0) for _ in range(4)]).arrange(RIGHT, buff=0.08)
            f2 = VGroup(*[RoundedRectangle(corner_radius=0.05, width=0.32, height=0.32, fill_color=MUTED if i < 4 else GREEN, fill_opacity=0.8, stroke_width=0)
                          for i in range(20)]).arrange_in_grid(rows=2, cols=10, buff=0.08)
            col1 = VGroup(c1, f1).arrange(DOWN, buff=0.35).move_to([-3.4, 0.4, 0])
            col2 = VGroup(c2, f2).arrange(DOWN, buff=0.35).move_to([2.8, 0.4, 0])
            self.play(FadeIn(col1), run_time=0.8)
            self.play(FadeIn(col2[0]), LaggedStart(*[FadeIn(x, scale=0.5) for x in f2], lag_ratio=0.05), run_time=1.6)
            ex = T("输入数、接收者大小  ＋  距离、离散度", 22, MUTED).to_edge(DOWN, buff=0.7)
            self.play(FadeIn(ex), run_time=0.5)
        with self.say("m3") as d:
            self.play(FadeOut(col1), FadeOut(col2), FadeOut(ex), run_time=0.5)
            n = 50
            cells = VGroup(*[Square(0.2, stroke_width=0, fill_color=MUTED, fill_opacity=0.35) for _ in range(n)]).arrange(RIGHT, buff=0.04).move_to([0.3, 1.0, 0])
            pos_idx = [7, 29]  # ~4%
            for i in pos_idx:
                cells[i].set_fill(GREEN, opacity=1)
            lab = T("候选连接，按预测概率排序 →（示意）", 22, MUTED).next_to(cells, UP, buff=0.25)
            self.play(FadeIn(cells, lag_ratio=0.01), FadeIn(lab), run_time=1.0)
            base = VGroup(counter("测试集正例比例", "4.30%  ·  3.08%", GREEN)).next_to(cells, DOWN, buff=0.6)
            self.play(FadeIn(base), run_time=0.6)
        with self.say("m3b") as d:
            rnd = T("随机排序：平均精度 ≈ 正例比例", 24, INK).next_to(base, DOWN, buff=0.4)
            self.play(FadeIn(rnd), run_time=0.6)
            self.play(*[Indicate(cells[i], color=GREEN, scale_factor=1.6) for i in pos_idx], run_time=1.2)
        self.play(*[FadeOut(m) for m in (cells, lab, base, rnd)], run_time=0.5)
        ax = Axes(x_range=[0, 2, 1], y_range=[0, 0.2, 0.05], x_length=8, y_length=4.4,
                  axis_config={"color": MUTED, "include_tip": False, "font_size": 20}, x_axis_config={"include_ticks": False},
                  y_axis_config={"numbers_to_include": [0, 0.05, 0.1, 0.15, 0.2], "decimal_number_config": {"num_decimal_places": 2}}).shift(DOWN * 0.4 + RIGHT * 0.4)
        yl = T("平均精度", 22, MUTED).rotate(PI / 2).next_to(ax.y_axis, LEFT, buff=0.5)

        def bars(x, a, b, rnd, name):
            w = 0.5
            r1 = Rectangle(width=w, height=ax.c2p(0, a)[1] - ax.c2p(0, 0)[1], fill_color=MUTED, fill_opacity=0.9, stroke_width=0).move_to(ax.c2p(x - 0.17, 0), aligned_edge=DOWN)
            r2 = Rectangle(width=w, height=ax.c2p(0, b)[1] - ax.c2p(0, 0)[1], fill_color=GREEN, fill_opacity=0.9, stroke_width=0).move_to(ax.c2p(x + 0.17, 0), aligned_edge=DOWN)
            v1 = T(f"{a:.3f}", 22, MUTED).next_to(r1, UP, buff=0.08)
            v2 = T(f"{b:.3f}", 22, GREEN).next_to(r2, UP, buff=0.08)
            rl = DashedLine(ax.c2p(x - 0.4, rnd), ax.c2p(x + 0.4, rnd), color=GOLD, stroke_width=3)
            nm = T(name, 24, INK).next_to(ax.c2p(x, 0), DOWN, buff=0.2)
            return r1, r2, v1, v2, rl, nm
        b1 = bars(0.5, 0.089, 0.161, 0.043, "MaleCNS")
        b2 = bars(1.5, 0.069, 0.114, 0.0308, "FlyWire")
        key = VGroup(VGroup(Square(0.22, fill_color=MUTED, fill_opacity=0.9, stroke_width=0), T("计数模型", 20, INK)).arrange(RIGHT, buff=0.1),
                     VGroup(Square(0.22, fill_color=GREEN, fill_opacity=0.9, stroke_width=0), T("空间模型", 20, INK)).arrange(RIGHT, buff=0.1),
                     VGroup(DashedLine(ORIGIN, RIGHT * 0.4, color=GOLD), T("随机水平", 20, INK)).arrange(RIGHT, buff=0.1)).arrange(RIGHT, buff=0.4).to_edge(UP, buff=0.5).shift(RIGHT * 1.5)
        with self.say("m4") as d:
            self.play(Create(ax), FadeIn(yl), FadeIn(key), FadeIn(b1[5]), run_time=1.0)
            self.play(Create(b1[4]), GrowFromEdge(b1[0], DOWN), FadeIn(b1[2]), run_time=0.9)
            self.play(GrowFromEdge(b1[1], DOWN), FadeIn(b1[3]), run_time=0.9)
        with self.say("m5") as d:
            self.play(FadeIn(b2[5]), Create(b2[4]), GrowFromEdge(b2[0], DOWN), FadeIn(b2[2]), run_time=0.9)
            self.play(GrowFromEdge(b2[1], DOWN), FadeIn(b2[3]), run_time=0.9)
        with self.say("m6") as d:
            nb = T("单次划分 · 无置信区间", 26, GOLD).move_to(ax.c2p(1.0, 0.19))
            bg = BackgroundRectangle(nb, color=BG, fill_opacity=0.9, buff=0.1)
            self.play(FadeIn(bg), FadeIn(nb), run_time=0.8)
        self.clear()

    # ------------------------------------------------------------------ meaning & limits
    def meaning(self):
        tag = self.chapter("四  意义与局限")
        TC, bC = make_tree(5, root=(-3.2, -3.0), length=1.3, depth=4, seg=0.1)
        tree = tree_mob(TC, BLUE, 3.5)
        pt = Dot([3.2, 0, 0], radius=0.25, color=BLUE)
        with self.say("l1") as d:
            self.play(FadeIn(tag), Create(tree), run_time=1.2)
            arr = Arrow([-0.6, 0, 0], [2.6, 0, 0], color=MUTED)
            self.play(GrowArrow(arr), TransformFromCopy(tree, pt), run_time=1.4)
            lost = T("位置信息丢失", 24, RED).next_to(arr, UP, buff=0.15)
            self.play(FadeIn(lost), run_time=0.5)
        with self.say("l2") as d:
            self.play(*[FadeOut(m) for m in (tree, arr, lost, pt)], run_time=0.5)
            brain = Ellipse(width=6.0, height=4.2, color=MUTED, stroke_width=3)
            regions = VGroup(*[Circle(radius=0.55, color=c, fill_opacity=0.25).move_to(p) for c, p in
                               ((BLUE, [-1.6, 0.8, 0]), (GREEN, [1.5, 0.9, 0]), (VIOLET, [-1.2, -1.0, 0]), (GOLD, [1.4, -1.0, 0]))])
            links = VGroup(*[Line(regions[i].get_center(), regions[j].get_center(), color=MUTED, stroke_width=3).set_z_index(-1)
                             for i, j in ((0, 1), (0, 2), (1, 3), (2, 3), (0, 3))])
            self.play(Create(brain), FadeIn(regions), Create(links), run_time=1.2)
            inner = VGroup(*[Dot(regions[0].get_center() + 0.32 * np.array([np.cos(t), np.sin(t), 0]), radius=0.05, color=INK) for t in np.linspace(0, TAU, 7)])
            self.play(regions[0].animate.scale(1.6), run_time=0.6)
            inner.move_to(regions[0])
            self.play(FadeIn(inner, lag_ratio=0.1), run_time=0.8)
            ql = T("节点内部的空间组织", 24, INK).next_to(brain, DOWN, buff=0.3)
            self.play(FadeIn(ql), run_time=0.5)
        with self.say("l3") as d:
            self.play(*[FadeOut(m) for m in (brain, regions, links, inner, ql)], run_time=0.5)
            stamp = VGroup(RoundedRectangle(corner_radius=0.15, width=4.6, height=1.3, stroke_color=GOLD, stroke_width=4),
                           T("在投稿 · 未经同行评审", 32, GOLD, weight=BOLD))
            stamp[1].move_to(stamp[0])
            self.play(FadeIn(stamp, scale=1.3), run_time=0.8)
        with self.say("l4") as d:
            self.play(stamp.animate.scale(0.6).to_corner(UR, buff=0.5), run_time=0.6)
            region = Circle(radius=1.3, color=GREEN, fill_opacity=0.12, stroke_width=2).move_to([0, -0.2, 0])
            rl = T("同一区域交汇", 22, GREEN).next_to(region, DOWN, buff=0.15)
            a = Line([-4.5, 1.8, 0], [0.4, 0.0, 0], color=A_COL, stroke_width=5)
            b = Line([-4.0, -2.4, 0], [0.2, -0.5, 0], color=B_COL, stroke_width=5)
            c = Line([4.5, 2.2, 0], [-0.3, -0.3, 0], color=INK, stroke_width=5)
            self.play(Create(a), Create(b), Create(c), FadeIn(region), FadeIn(rl), run_time=1.4)
            two = VGroup(T("甲 → 乙 的连接", 24, INK), T("输入在丙上靠近", 24, INK)).arrange(DOWN, buff=0.2).move_to([4.0, -1.6, 0])
            self.play(FadeIn(two), run_time=0.6)
            cc = T("可能的共同原因", 28, GOLD, weight=BOLD).move_to([4.0, -0.4, 0])
            self.play(FadeIn(cc), run_time=0.5)
        with self.say("l5") as d:
            self.play(*[FadeOut(m) for m in (region, rl, a, b, c, two, cc)], run_time=0.5)
            cards = VGroup()
            for name, note, col in (("果蝇 MaleCNS", "1 只动物", GREEN), ("果蝇 FlyWire", "1 只动物", GREEN),
                                    ("线虫", "10 和 13 个接收者", GOLD), ("环节动物幼虫", "4 条连接，方向不一", RED)):
                r = RoundedRectangle(corner_radius=0.12, width=2.9, height=1.5, stroke_color=col, stroke_width=2.5, fill_color="#182133", fill_opacity=1)
                g = VGroup(T(name, 24, col), T(note, 20, MUTED)).arrange(DOWN, buff=0.15).move_to(r)
                cards.add(VGroup(r, g))
            cards.arrange(RIGHT, buff=0.3).shift(DOWN * 0.2)
            self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.2) for c in cards], lag_ratio=0.3), run_time=d * 0.6)
        with self.say("l6") as d:
            self.play(FadeOut(cards), FadeOut(stamp), run_time=0.5)
            TC, bC = make_tree(11, root=(0, -3.2), length=1.5, depth=4, seg=0.1)
            tree = tree_mob(TC, BLUE, 3.5)
            rng = np.random.default_rng(4)
            side = sorted(subtree_nodes(TC, bC, 1))
            aN = list(rng.choice(side, 5, replace=False)); bN = list(rng.choice([v for v in side if v not in aN], 4, replace=False))
            self.play(Create(tree), run_time=1.2)
            self.play(FadeIn(self.syn(TC, aN, A_COL, 0.1)), FadeIn(self.syn(TC, bN, B_COL, 0.1)), run_time=0.8)
        self.wait(0.8)
        self.clear(1.0)
