"""Paper explainer: 症状网络的模块控制（最小支配集）."""
import itertools

import networkx as nx
import numpy as np

from common import *  # noqa: F401,F403
from ep_robustness import fit, counter

TITLE = "症状群之间谁控制谁：模块控制网络"

LINES = {
    # hook
    "h1": "失眠、压力大、情绪低落、容易紧张——这些问题，常常一起出现在同一个人身上。",
    "h1b": "网络精神病学把症状看成彼此影响、相互维持的一张网。画面里，是这种思路的一段介绍。",
    "h2": "症状网络里，问卷的每个条目是一个节点；两个条目之间有关联，就连一条边。",
    "h3": "常见的做法，是找连接最多的那个中心症状。但临床上，很少只针对一个问卷条目去干预。",
    "h4": "我们干预的，往往是一类问题，比如睡眠、压力，或者焦虑。这样的一类症状，叫症状群。",
    "h5": "【慢】所以这项研究要回答：症状群和症状群之间，在结构上，是谁控制着谁。",
    # parts
    "q0": "这一期分四部分。",
    "q1": "第一部分，怎样从问卷数据得到症状网络和症状群。",
    "q2": "第二部分，用支配集来刻画控制，再算出症状群之间的控制强度。",
    "q3": "第三部分，真实数据的结果，以及结果稳不稳定。",
    "q4": "第四部分，意义和局限。",
    # data
    "n1": "先看第一部分。数据来自两千七百七十三名大学新生，他们填写了抑郁、焦虑、失眠和压力四个量表。",
    "n1b": "画面里是一段新闻报道：大学生的焦虑和抑郁，近年来很受关注。",
    "n2": "四个量表一共三十七个条目，每个条目变成网络里的一个节点，颜色表示它来自哪个量表。",
    "n2b": "边用偏相关来定义。偏相关，就是控制住其他所有条目之后，两个条目之间还剩下的那部分关联。",
    "n2c": "症状网络这一页有画面上的交互演示。你看，换成普通相关，几乎处处有边；偏相关只留下直接的关联。",
    "n3": "这样估计出的网络，有二百五十四条边，密度零点四。密度，是实际的边占所有可能的边的比例。",
    "n4": "再用社区发现算法，把联系紧密的条目分到一组。三十七个条目，分成了六个症状模块，也就是六个症状群。",
    "n5": "睡眠、负性压力和正性压力，叫非情绪模块；抑郁和焦虑，叫情绪模块；还有一个模块，只有自杀意念这一条。",
    # dominating set
    "d1": "下面进入第二部分。这是一张无向网络。这项研究用支配集来描述控制。",
    "d2": "选中一个节点，它能控制自己和所有邻居。这一片，就叫它的控制区域。",
    "d3": "选中的几个节点，控制区域合起来覆盖了整张网络，它们就构成一个支配集。",
    "d4": "节点最少的支配集，叫最小支配集。网络不大的时候，可以从一个节点开始，逐个组合去试。",
    "d5": "注意，最小支配集往往不止一个。这张小网络就有三个，大小完全一样。",
    "d6": "支配集只看节点和它一步之内的邻居，不依赖长路径，正适合边只是统计关联的症状网络。",
    # module control strength
    "m1": "现在把模块加进来。在一个最小支配集里，模块甲的驱动节点合起来，就是模块甲的控制区域，画成了蓝色光晕。",
    "m2": "模块控制强度，就是模块乙的节点里，有多大比例落进了这个控制区域。右上角是它的公式。",
    "m2b": "【慢】分子，是模块甲的控制区域和模块乙重叠的节点数；分母，是模块乙的节点总数。这里是五个里有三个。",
    "m3": "反过来算，模块乙控制模块甲，是七个里有两个。两个方向不一样，原本无向的网络，就有了方向。",
    "m4": "把它在所有最小支配集上取平均，就得到平均模块控制强度。右边列出了三个方案和平均值。",
    "m5": "以模块为节点，平均控制强度为边权，画出来，就是一张有向的模块控制网络。",
    # results
    "r1": "下面进入第三部分，回到真实数据。这张症状网络，一共有二十七个最小支配集。",
    "r2": "三十七个条目里，有二十四个至少在一个最小支配集里当过驱动节点。",
    "r3": "这是真实的模块控制网络。最强的一条边，是睡眠模块指向正性压力模块，平均控制强度零点五八六。",
    "r4": "其次是正性压力指向焦虑，零点四九七；睡眠指向抑郁，零点四四四。",
    "r5": "而抑郁指向负性压力，只有零点零一九。",
    "r6": "【慢】总体来看，非情绪模块向外的控制更强，情绪模块更多处在被控制的位置。",
    # control frequency
    "f1": "再看单个条目。控制频率，是一个条目在所有最小支配集里当驱动节点的比例。左边是条目名，右边的条越长，频率越高。",
    "f2": "排第一的，是自杀意念这一条。它出现在全部二十七个最小支配集里。",
    "f3": "中心性，是衡量节点在网络里有多重要的指标，比如连接数。自杀意念所在的模块，各种中心性都排在最后。",
    "f4": "原因在支配集的规则里：连接很少的节点，要么自己被选中，要么它仅有的几个邻居之一被选中。",
    "f5": "【慢】所以控制频率高，反映的是网络结构的约束，不等于临床上更重要。",
    # stability
    "b1": "最后检查稳定性。做法是随机抽取百分之八十的样本，重新估计网络，重复一千次。",
    "b2": "全样本的边数和最小支配集个数，都落在一千次重抽样的百分之九十五区间里。多数重抽样网络，也是六个模块。",
    "b3": "右边这张图，横轴是保留的样本比例，纵轴是和全样本结果的相关。样本少于一半时，平均控制频率的相关降到零点五以下。",
    # meaning & limits
    "l1": "最后是第四部分。对临床来说，这提示干预也许可以从症状群入手。睡眠和压力模块，在结构上处于更强的控制位置。",
    "l1b": "睡眠和情绪本来就关系密切。画面里，是一段讲睡眠怎样影响情绪的科普视频。",
    "l2": "但要小心。这是一次横断面调查，也就是每个人只在一个时间点测一次，网络描述的是人群里的关联，不是个体体内的因果。",
    "l3": "结构上的控制，也不等于先治好睡眠，情绪就一定改善。这需要纵向追踪和干预研究来检验。",
    "l4": "另外，支配集只看有没有边，很强的边和极弱的边作用相同；关联又取了绝对值，正负号也丢掉了。",
    "l5": "【慢】所以，模块控制给出的是一个值得检验的假设，而不是结论。",
    # recap
    "z0": "好，我们来总结一下。",
    "z1": "第一，这项研究把症状网络从单个条目，升到了症状群的尺度。",
    "z2": "第二，用最小支配集刻画控制，再在所有方案上平均，得到有方向的模块控制网络。",
    "z3": "第三，睡眠和压力模块在结构上控制更强，但这需要纵向数据和干预研究来检验。",
}

# module layout: DRM 0-6, SRM 7-14 (7 = PHQ sleep item), SUM 15, ARM 16-22, NSM 23-29, PSM 30-36 (schematic split)
MODS = {"DRM": list(range(0, 7)), "SRM": list(range(7, 15)), "SUM": [15], "ARM": list(range(16, 23)),
        "NSM": list(range(23, 30)), "PSM": list(range(30, 37))}
MNAME = {"DRM": "抑郁", "SRM": "睡眠", "SUM": "自杀意念", "ARM": "焦虑", "NSM": "负性压力", "PSM": "正性压力"}
PINK = "#ff8fb3"
MCOL = {"DRM": RED, "SRM": GREEN, "SUM": PINK, "ARM": GOLD, "NSM": VIOLET, "PSM": BLUE}
SCALE = {}
for v in list(range(0, 8)) + [15]:
    SCALE[v] = "PHQ"
for v in range(8, 15):
    SCALE[v] = "ISI"
for v in range(16, 23):
    SCALE[v] = "GAD"
for v in range(23, 37):
    SCALE[v] = "PSS"
SCOL = {"PHQ": RED, "GAD": GOLD, "ISI": GREEN, "PSS": VIOLET}
MCENTER = {"SRM": (-4.3, 1.1), "NSM": (0.0, 1.5), "PSM": (4.3, 1.1), "DRM": (-3.2, -2.0), "SUM": (0.0, -1.0), "ARM": (3.2, -2.0)}


def symptom_graph():
    rng = np.random.default_rng(5)
    mod = {v: m for m, vs in MODS.items() for v in vs}
    pairs = list(itertools.combinations(range(37), 2))
    w = np.array([1.0 if mod[u] == mod[v] else 0.3 for u, v in pairs])
    pick = rng.choice(len(pairs), 254, replace=False, p=w / w.sum())
    G = nx.Graph(); G.add_nodes_from(range(37))
    G.add_edges_from(pairs[i] for i in pick)
    return G, mod


def cluster_pos(rad=0.85):
    pos = {}
    for m, vs in MODS.items():
        c = np.array([*MCENTER[m], 0.0])
        if len(vs) == 1:
            pos[vs[0]] = c
            continue
        for i, v in enumerate(vs):
            t = TAU * i / len(vs) + 0.3
            pos[v] = c + rad * np.array([np.cos(t), np.sin(t), 0])
    return pos


def toy():
    G = nx.random_partition_graph([7, 5], 0.5, 0.12, seed=143)
    return nx.Graph(G)


def mdsets(G):
    V = list(G)
    for k in range(1, len(V) + 1):
        out = [S for S in itertools.combinations(V, k) if set().union(*[set(G[v]) | {v} for v in S]) == set(V)]
        if out:
            return out


def area(G, S):
    return set().union(*[set(G[v]) | {v} for v in S]) if S else set()


class Episode(Narrated):
    LINES = LINES

    def construct(self):
        self.hook()
        self.parts()
        self.data()
        self.domset()
        self.mcs()
        self.results()
        self.frequency()
        self.stability()
        self.meaning()
        self.recap()

    def clear(self, rt=0.8, keep=None):
        self.play(*[FadeOut(m) for m in self.mobjects if m is not keep], run_time=rt)

    def draw(self, G, pos, colors, r=0.09, eo=0.18, ew=1.0):
        dots = {v: Dot(pos[v], radius=r, color=colors[v]) for v in G}
        edges = {e: Line(pos[e[0]], pos[e[1]], stroke_width=ew, color=MUTED, stroke_opacity=eo) for e in G.edges()}
        return dots, edges, VGroup(VGroup(*edges.values()), VGroup(*dots.values()))

    # ------------------------------------------------------------------ hook
    def hook(self):
        words = [("失眠", GREEN, (-3.2, 1.4)), ("压力大", VIOLET, (2.8, 1.8)), ("情绪低落", RED, (-2.4, -1.6)), ("容易紧张", GOLD, (3.0, -1.2))]
        ws = VGroup(*[T(s, 36, c, weight=BOLD).move_to([*p, 0]) for s, c, p in words])
        links = VGroup(*[Line(ws[i].get_center(), ws[j].get_center(), color=MUTED, stroke_width=3, stroke_opacity=0.6).set_z_index(-1)
                         for i, j in ((0, 1), (0, 2), (1, 2), (1, 3), (2, 3), (0, 3))])
        with self.say("h1") as d:
            self.play(LaggedStart(*[FadeIn(w, scale=0.8) for w in ws], lag_ratio=0.35), run_time=d * 0.5)
            self.play(Create(links), run_time=d * 0.3)
        self.play(FadeOut(ws), FadeOut(links), run_time=0.5)
        with self.say("h1b") as d:
            self.clip_on("yt_network_psych_wellcome.mp4", "center", "视频：Wellcome · YouTube", start=8)
        self.clip_off()
        G, mod = symptom_graph()
        rng = np.random.default_rng(2)
        pos0 = fit(nx.spring_layout(G, seed=4, k=0.6), (-6.0, 6.0, -3.3, 3.0))
        dots, edges, net = self.draw(G, pos0, {v: INK for v in G})
        with self.say("h2") as d:
            self.play(LaggedStart(*[GrowFromCenter(x) for x in dots.values()], lag_ratio=0.02), run_time=1.2)
            self.play(LaggedStart(*[Create(e) for e in edges.values()], lag_ratio=0.002), run_time=d * 0.4)
        hub = max(G, key=G.degree)
        with self.say("h3") as d:
            ring = Circle(radius=0.3, color=GOLD, stroke_width=4).move_to(pos0[hub])
            self.play(dots[hub].animate.set_color(GOLD).scale(2), Create(ring),
                      *[edges[e].animate.set_stroke(GOLD, opacity=0.7, width=2) for e in edges if hub in e], run_time=1.2)
            lab = T("中心症状", 28, GOLD).next_to(ring, UP, buff=0.15)
            self.play(FadeIn(lab), run_time=0.5)
            self.wait(d * 0.2)
            x = Cross(ring, stroke_color=RED, scale_factor=1.0)
            self.play(Create(x), run_time=0.7)
        pos1 = cluster_pos()
        with self.say("h4") as d:
            self.play(FadeOut(ring), FadeOut(lab), FadeOut(x), run_time=0.4)
            self.play(*[dots[v].animate.move_to(pos1[v]).set_color(MCOL[mod[v]]).scale(1 if v != hub else 0.5) for v in G],
                      *[e.animate.put_start_and_end_on(pos1[u], pos1[w]).set_stroke(MUTED, opacity=0.12, width=1) for (u, w), e in edges.items()],
                      run_time=2.2)
            hulls = VGroup(*[Circle(radius=1.2 if len(vs) > 1 else 0.45, color=MCOL[m], stroke_width=2.5).move_to([*MCENTER[m], 0])
                             for m, vs in MODS.items()])
            self.play(Create(hulls), run_time=0.8)
        with self.say("h5") as d:
            arr = VGroup(
                CurvedArrow(np.array([-3.2, 0.2, 0]), np.array([-2.9, -0.8, 0]), color=INK, angle=-0.6),
                CurvedArrow(np.array([1.0, 0.6, 0]), np.array([2.4, -0.9, 0]), color=INK, angle=-0.6),
                CurvedArrow(np.array([-1.0, 1.5, 0]), np.array([-3.0, 1.9, 0]), color=INK, angle=0.6))
            self.play(net.animate.set_opacity(0.35), LaggedStart(*[Create(a) for a in arr], lag_ratio=0.3), run_time=1.6)
            q = T("症状群之间的控制关系", 52, INK, weight=BOLD)
            bg = BackgroundRectangle(q, color=BG, fill_opacity=0.85, buff=0.2)
            self.play(FadeIn(bg), Write(q), run_time=1.2)
        self.clear()

    def parts(self):
        head, items = slide("这一期分四部分", ["一  症状网络与症状群", "二  支配集与模块控制", "三  结果与稳定性", "四  意义与局限"])
        with self.say("q0") as d:
            self.play(FadeIn(head, shift=RIGHT * 0.3), run_time=0.6)
        for k, it in zip(("q1", "q2", "q3", "q4"), items):
            with self.say(k) as d:
                self.play(FadeIn(it, shift=RIGHT * 0.3), run_time=0.6)
        self.wait(0.6)
        self.play(FadeOut(head), FadeOut(items), run_time=0.6)

    def recap(self):
        head, items = slide("小结", ["从单个条目升到症状群", "最小支配集 → 有向的模块控制网络", "睡眠、压力模块控制更强：待纵向检验"], accent=GREEN)
        with self.say("z0") as d:
            self.play(FadeIn(head, shift=RIGHT * 0.3), run_time=0.6)
        for k, it in zip(("z1", "z2", "z3"), items):
            with self.say(k) as d:
                self.play(FadeIn(it, shift=RIGHT * 0.3), run_time=0.6)
        self.wait(1.0)
        self.play(FadeOut(head), FadeOut(items), run_time=0.8)

    # ------------------------------------------------------------------ data
    def data(self):
        tag = self.chapter("一  症状网络与症状群")
        cards = VGroup()
        for name, k, sc in (("抑郁量表", 9, "PHQ"), ("焦虑量表", 7, "GAD"), ("失眠量表", 7, "ISI"), ("压力量表", 14, "PSS")):
            r = RoundedRectangle(corner_radius=0.15, width=2.7, height=1.4, stroke_color=SCOL[sc], stroke_width=2.5, fill_color="#182133", fill_opacity=1)
            g = VGroup(T(name, 28, SCOL[sc]), T(f"{k} 个条目", 24, MUTED)).arrange(DOWN, buff=0.15).move_to(r)
            cards.add(VGroup(r, g))
        cards.arrange(RIGHT, buff=0.35).shift(UP * 0.4)
        with self.say("n1") as d:
            n = counter("大学新生", "2773 人", INK).to_edge(UP, buff=0.9)
            self.play(FadeIn(tag), FadeIn(n), run_time=0.8)
            self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.2) for c in cards], lag_ratio=0.25), run_time=d * 0.5)
        keep1 = list(self.mobjects)
        self.remove(*keep1)
        with self.say("n1b") as d:
            self.clip_on("yt_college_mh_abc10.mp4", "center", "视频：ABC10 · YouTube", start=6)
        self.clip_off()
        self.add(*keep1)
        G, mod = symptom_graph()
        pos0 = fit(nx.spring_layout(G, seed=4, k=0.6), (-6.0, 6.0, -3.3, 2.4))
        dots, edges, net = self.draw(G, pos0, {v: SCOL[SCALE[v]] for v in G})
        with self.say("n2") as d:
            order = {"PHQ": 0, "GAD": 1, "ISI": 2, "PSS": 3}
            starts = [d_.copy().move_to(cards[order[SCALE[v]]].get_center()).set_opacity(0) for v, d_ in dots.items()]
            self.play(FadeOut(n), run_time=0.3)
            self.play(LaggedStart(*[Transform(s, dots[v]) for s, v in zip(starts, dots)], lag_ratio=0.02),
                      cards.animate.set_opacity(0.0), run_time=1.8)
            self.remove(*starts); self.add(*dots.values()); self.remove(cards)
            c37 = counter("条目", "37", INK).to_corner(UR, buff=0.4)
            self.play(FadeIn(c37), run_time=0.5)
        with self.say("n2b") as d:
            pc = VGroup(T("偏相关", 30, GOLD, weight=BOLD), T("控制其他条目后，剩下的直接关联", 24, INK)).arrange(DOWN, buff=0.15).to_edge(DOWN, buff=0.3)
            bgp = BackgroundRectangle(pc, color=BG, fill_opacity=0.9, buff=0.15)
            self.play(FadeIn(bgp), FadeIn(pc), run_time=0.8)
        keep2 = list(self.mobjects)
        self.remove(*keep2)
        with self.say("n2c") as d:
            self.clip_on("symptom_pcor.mp4", "full", "本站交互演示：相关与偏相关", start=0.3)
        self.wait(max(0.05, 15.0 - (self.renderer.time - self._clip['t0'])))
        self.clip_off()
        self.add(*[m for m in keep2 if m not in (bgp, pc)])
        with self.say("n3") as d:
            self.play(LaggedStart(*[Create(e) for e in edges.values()], lag_ratio=0.003), run_time=d * 0.45)
            self.bring_to_front(*dots.values())
            c2 = VGroup(counter("边", "254", INK), counter("密度", "0.40", INK)).arrange(DOWN, buff=0.3).next_to(c37, DOWN, buff=0.3)
            self.play(FadeIn(c2), run_time=0.6)
        pos1 = cluster_pos()
        with self.say("n4") as d:
            self.play(FadeOut(c37), FadeOut(c2), run_time=0.4)
            self.play(*[dots[v].animate.move_to(pos1[v]).set_color(MCOL[mod[v]]) for v in G],
                      *[e.animate.put_start_and_end_on(pos1[u], pos1[w]).set_stroke(opacity=0.12) for (u, w), e in edges.items()],
                      run_time=2.2)
            c6 = counter("症状模块", "6", INK).to_corner(UR, buff=0.4)
            self.play(FadeIn(c6), run_time=0.5)
        with self.say("n5") as d:
            labs = VGroup()
            for m in MODS:
                c = np.array([*MCENTER[m], 0])
                off = UP * 1.15 if MCENTER[m][1] > 0 else DOWN * 1.15
                if m == "SUM":
                    off = DOWN * 0.45
                labs.add(T(MNAME[m], 26, MCOL[m], weight=BOLD).move_to(c + off))
            for keys in (("SRM", "NSM", "PSM"), ("DRM", "ARM"), ("SUM",)):
                idx = [list(MODS).index(k) for k in keys]
                self.play(*[FadeIn(labs[i], shift=UP * 0.1) for i in idx], run_time=0.7)
                self.wait(d * 0.15)
        self.clear()

    # ------------------------------------------------------------------ dominating set
    def domset(self, chapter=True):
        tag = self.chapter("二  支配集与模块控制")
        G = toy()
        pos = fit(nx.kamada_kawai_layout(G), (-4.5, 4.5, -3.0, 2.6))
        dots, edges, net = self.draw(G, pos, {v: MUTED for v in G}, r=0.2, eo=0.6, ew=2.5)
        with self.say("d1") as d:
            self.play(FadeIn(tag), FadeIn(net), run_time=1.2)
        D = mdsets(G)
        S0 = D[0]

        def cover(S, col=BLUE):
            a = area(G, S)
            anims = []
            for v, x in dots.items():
                if v in S:
                    anims.append(x.animate.set_color(col).set_opacity(1).scale_to_fit_width(0.56))
                elif v in a:
                    anims.append(x.animate.set_color(col).set_opacity(0.45).scale_to_fit_width(0.4))
                else:
                    anims.append(x.animate.set_color(MUTED).set_opacity(1).scale_to_fit_width(0.4))
            for (u, w), e in edges.items():
                on = (u in S) or (w in S)
                anims.append(e.animate.set_stroke(col if on else MUTED, opacity=0.9 if on else 0.35, width=3.5 if on else 2.5))
            return anims
        with self.say("d2") as d:
            self.play(*cover([S0[0]]), run_time=1.2)
            halo = Circle(radius=0.32, color=INK, stroke_width=3).move_to(pos[S0[0]])
            self.play(Create(halo), run_time=0.6)
        with self.say("d3") as d:
            self.play(FadeOut(halo), *cover(S0[:2]), run_time=1.0)
            self.play(*cover(S0), run_time=1.0)
            ok = T("全部覆盖", 28, BLUE).to_corner(UR, buff=0.5)
            self.play(FadeIn(ok), run_time=0.5)
        with self.say("d4") as d:
            self.play(FadeOut(ok), *cover([]), run_time=0.6)
            tries = counter("尝试组合大小", "1", INK).to_corner(UR, buff=0.5)
            self.play(FadeIn(tries), run_time=0.4)
            for k in range(1, len(S0) + 1):
                combos = list(itertools.combinations(list(G), k))[:: max(1, len(list(itertools.combinations(list(G), k))) // 3)][:3]
                self.play(Transform(tries, counter("尝试组合大小", str(k), INK).move_to(tries)), run_time=0.3)
                for S in combos:
                    self.play(*cover(S, MUTED if k < len(S0) else BLUE), run_time=0.35)
            self.play(*cover(S0), Transform(tries, counter("最小支配集大小", str(len(S0)), BLUE).move_to(tries)), run_time=0.6)
        with self.say("d5") as d:
            cnt = counter("最小支配集", f"{len(D)} 个", GOLD).next_to(tries, DOWN, buff=0.4)
            self.play(FadeIn(cnt), run_time=0.5)
            for S in D[1:] + D[:1]:
                self.play(*cover(S, GOLD), run_time=0.9)
                self.wait(0.3)
        with self.say("d6") as d:
            u = S0[0]
            nb = list(G[u])
            ring = VGroup(*[Circle(radius=0.3, color=INK, stroke_width=3).move_to(pos[w]) for w in nb])
            self.play(*cover([u], BLUE), FadeOut(cnt), FadeOut(tries), run_time=0.8)
            self.play(Create(ring), run_time=0.8)
            one = T("只看一步之内的邻居", 28, INK).to_edge(DOWN, buff=0.3)
            self.play(FadeIn(one), run_time=0.6)
        self.clear()

    # ------------------------------------------------------------------ module control strength
    def mcs(self):
        tag = self.chapter("二  支配集与模块控制")
        G = toy()
        A, B = set(range(7)), set(range(7, 12))
        P = nx.kamada_kawai_layout(G)
        pos = fit(P, (-4.2, 4.2, -2.6, 2.4))
        cm = {v: BLUE if v in A else GOLD for v in G}
        dots, edges, net = self.draw(G, pos, cm, r=0.2, eo=0.5, ew=2.5)
        D = mdsets(G)
        S = D[0]
        la = T("模块甲 (A)", 28, BLUE).to_corner(UL, buff=0.45).shift(DOWN * 0.6)
        lb = T("模块乙 (B)", 28, GOLD).next_to(la, DOWN, buff=0.2, aligned_edge=LEFT)
        with self.say("m1") as d:
            self.play(FadeIn(tag), FadeIn(net), FadeIn(la), FadeIn(lb), run_time=1.0)
            drA = [v for v in S if v in A]
            rings = VGroup(*[Circle(radius=0.34, color=INK, stroke_width=4).move_to(pos[v]) for v in S])
            self.play(Create(rings), run_time=0.8)
            acA = area(G, drA)
            halos = VGroup(*[Circle(radius=0.3, color=BLUE, fill_opacity=0.35, stroke_width=0).move_to(pos[v]) for v in acA])
            self.play(FadeIn(halos), *[dots[v].animate.set_opacity(0.3) for v in G if v not in acA], run_time=1.2)
        with self.say("m2") as d:
            hit = sorted(acA & B)
            self.play(*[Indicate(dots[v], color=GOLD, scale_factor=1.8) for v in hit], run_time=1.2)
            f = MathTex(r"\mathrm{MCS}_{A\to B}=\frac{|AC_A\cap V_B|}{|V_B|}", r"=\frac{%d}{%d}" % (len(hit), len(B)),
                        font_size=40, color=INK).to_corner(UR, buff=0.4).shift(DOWN * 0.3)
            f[0].set_color(BLUE)
            bgf = BackgroundRectangle(f, color=BG, fill_opacity=0.9, buff=0.12)
            self.play(FadeIn(bgf), Write(f), run_time=1.4)
        with self.say("m2b") as d:
            num = T("甲的控制区域 ∩ 乙", 22, BLUE).next_to(f, DOWN, buff=0.25).align_to(f, LEFT).shift(RIGHT * 1.6)
            den = T("乙的节点总数", 22, GOLD).next_to(num, DOWN, buff=0.15).align_to(num, LEFT)
            nb = BackgroundRectangle(VGroup(num, den), color=BG, fill_opacity=0.9, buff=0.1)
            self.play(FadeIn(nb), FadeIn(num), run_time=0.7)
            self.play(FadeIn(den), run_time=0.7)
            self.play(Indicate(f[1], color=GOLD), run_time=1.0)
        self.play(FadeOut(num), FadeOut(den), FadeOut(nb), run_time=0.4)
        with self.say("m3") as d:
            drB = [v for v in S if v in B]
            acB = area(G, drB)
            hitB = sorted(acB & A)
            halosB = VGroup(*[Circle(radius=0.3, color=GOLD, fill_opacity=0.35, stroke_width=0).move_to(pos[v]) for v in acB])
            self.play(FadeOut(halos), *[dots[v].animate.set_opacity(1 if v in acB else 0.3) for v in G], FadeIn(halosB), run_time=1.0)
            self.play(*[Indicate(dots[v], color=BLUE, scale_factor=1.8) for v in hitB], run_time=1.0)
            f2 = MathTex(r"\mathrm{MCS}_{B\to A}=", r"\frac{%d}{%d}" % (len(hitB), len(A)), font_size=40, color=INK).next_to(f, DOWN, buff=0.3, aligned_edge=LEFT)
            f2[0].set_color(GOLD)
            bgf2 = BackgroundRectangle(f2, color=BG, fill_opacity=0.9, buff=0.12)
            self.play(FadeIn(bgf2), Write(f2), run_time=1.0)
        # averaging over all minimum dominating sets
        def mcs_val(S, X, Y):
            return len(area(G, [v for v in S if v in X]) & Y) / len(Y)
        ab = [mcs_val(S_, A, B) for S_ in D]
        ba = [mcs_val(S_, B, A) for S_ in D]
        with self.say("m4") as d:
            self.play(FadeOut(halosB), FadeOut(rings), FadeOut(f), FadeOut(f2), FadeOut(bgf), FadeOut(bgf2),
                      *[x.animate.set_opacity(1) for x in dots.values()], run_time=0.6)
            rows = VGroup()
            for i, S_ in enumerate(D):
                rows.add(T(f"方案 {i + 1}：   A→B {ab[i]:.2f}    B→A {ba[i]:.2f}", 24, INK))
            rows.arrange(DOWN, aligned_edge=LEFT, buff=0.2).to_corner(UR, buff=0.4).shift(DOWN * 0.4)
            for i, S_ in enumerate(D):
                rs = VGroup(*[Circle(radius=0.34, color=INK, stroke_width=4).move_to(pos[v]) for v in S_])
                self.play(FadeIn(rs), FadeIn(rows[i]), run_time=0.5)
                self.play(FadeOut(rs), run_time=0.3)
            avg = T(f"平均：   A→B {np.mean(ab):.2f}    B→A {np.mean(ba):.2f}", 24, GOLD, weight=BOLD).next_to(rows, DOWN, buff=0.3, aligned_edge=LEFT)
            line = Line(avg.get_left(), avg.get_right(), color=MUTED, stroke_width=1).next_to(avg, UP, buff=0.12)
            self.play(Create(line), FadeIn(avg), run_time=0.8)
            self.amcs = (np.mean(ab), np.mean(ba))
        with self.say("m5") as d:
            ca, cb = np.array([-2.8, -0.4, 0]), np.array([2.0, -0.4, 0])
            self.play(*[dots[v].animate.move_to(ca if v in A else cb).set_opacity(0) for v in G],
                      *[e.animate.set_stroke(opacity=0) for e in edges.values()], FadeOut(rows), FadeOut(line), run_time=1.2)
            na = Circle(radius=0.9, color=BLUE, fill_opacity=0.25).move_to(ca).add(T("A", 40, BLUE).move_to(ca))
            nb = Circle(radius=0.7, color=GOLD, fill_opacity=0.25).move_to(cb).add(T("B", 40, GOLD).move_to(cb))
            self.play(GrowFromCenter(na), GrowFromCenter(nb), FadeOut(avg), run_time=0.8)
            a1 = CurvedArrow(ca + np.array([0.6, 0.7, 0]), cb + np.array([-0.5, 0.55, 0]), angle=-0.8, color=BLUE, stroke_width=2 + 14 * self.amcs[0])
            a2 = CurvedArrow(cb + np.array([-0.5, -0.55, 0]), ca + np.array([0.6, -0.7, 0]), angle=-0.8, color=GOLD, stroke_width=2 + 14 * self.amcs[1])
            t1 = T(f"{self.amcs[0]:.2f}", 28, BLUE).next_to(a1, UP, buff=0.1)
            t2 = T(f"{self.amcs[1]:.2f}", 28, GOLD).next_to(a2, DOWN, buff=0.1)
            self.play(Create(a1), FadeIn(t1), run_time=0.9)
            self.play(Create(a2), FadeIn(t2), run_time=0.9)
        self.clear()

    # ------------------------------------------------------------------ real results
    def results(self):
        tag = self.chapter("三  结果与稳定性")
        with self.say("r1") as d:
            cards = VGroup(*[RoundedRectangle(corner_radius=0.08, width=0.9, height=0.6, stroke_color=BLUE, stroke_width=2,
                                              fill_color="#182133", fill_opacity=1) for _ in range(27)])
            cards.arrange_in_grid(rows=3, cols=9, buff=0.18).shift(UP * 0.6)
            self.play(FadeIn(tag), LaggedStart(*[FadeIn(c, scale=0.7) for c in cards], lag_ratio=0.05), run_time=d * 0.6)
            c27 = counter("最小支配集", "27 个", BLUE).next_to(cards, DOWN, buff=0.5)
            self.play(FadeIn(c27), run_time=0.5)
        with self.say("r2") as d:
            self.play(FadeOut(cards), FadeOut(c27), run_time=0.5)
            items = VGroup(*[Dot(radius=0.16, color=MUTED) for _ in range(37)]).arrange_in_grid(rows=3, cols=13, buff=0.32).shift(UP * 0.4)
            self.play(FadeIn(items, lag_ratio=0.02), run_time=0.8)
            self.play(*[items[i].animate.set_color(BLUE) for i in range(24)], run_time=1.0)
            c24 = counter("当过驱动节点的条目", "24 / 37", BLUE).next_to(items, DOWN, buff=0.5)
            self.play(FadeIn(c24), run_time=0.5)
        self.play(FadeOut(items), FadeOut(c24), run_time=0.5)
        RC = {"SRM": (-4.5, 1.4), "PSM": (0.0, 1.9), "NSM": (4.5, 1.4), "DRM": (-2.6, -2.0), "ARM": (2.2, -2.0), "SUM": (5.2, -2.0)}
        cen = {m: np.array([*RC[m], 0]) for m in MODS}
        nodes = {}
        for m in MODS:
            r = 0.78 if m != "SUM" else 0.52
            c = Circle(radius=r, color=MCOL[m], fill_opacity=0.22, stroke_width=3).move_to(cen[m])
            c.add(T(MNAME[m], 22 if m != "SUM" else 17, MCOL[m], weight=BOLD).move_to(cen[m]))
            nodes[m] = c
        self.play(LaggedStart(*[GrowFromCenter(n) for n in nodes.values()], lag_ratio=0.1), run_time=1.0)

        def link(a, b, w, col, ang=0.0, prop=0.5, off=0.35):
            p, q = cen[a], cen[b]
            dvec = (q - p) / np.linalg.norm(q - p)
            ra, rb = nodes[a].width / 2, nodes[b].width / 2
            ar = CurvedArrow(p + dvec * (ra + 0.08), q - dvec * (rb + 0.08), angle=ang, color=col, stroke_width=2 + 16 * w, tip_length=0.25)
            t = T(f"{w:.3f}", 26, col, weight=BOLD)
            mid = ar.point_from_proportion(prop)
            nrm = np.array([-dvec[1], dvec[0], 0])
            t.move_to(mid + nrm * off * (1 if ang >= 0 else -1))
            bg = BackgroundRectangle(t, color=BG, fill_opacity=0.85, buff=0.06)
            return ar, VGroup(bg, t)
        a1 = link("SRM", "PSM", 0.586, GREEN, -0.35)
        a2 = link("PSM", "ARM", 0.497, BLUE, -0.3, off=0.75)
        a3 = link("SRM", "DRM", 0.444, GREEN, 0.3)
        a4 = link("DRM", "NSM", 0.019, RED, 0.0, prop=0.22)
        with self.say("r3") as d:
            self.play(Create(a1[0]), run_time=1.2)
            self.play(FadeIn(a1[1]), run_time=0.5)
        with self.say("r4") as d:
            self.play(Create(a2[0]), FadeIn(a2[1]), run_time=1.2)
            self.play(Create(a3[0]), FadeIn(a3[1]), run_time=1.2)
        with self.say("r5") as d:
            self.play(Create(a4[0]), FadeIn(a4[1]), run_time=1.2)
        with self.say("r6") as d:
            out_m, in_m = ("SRM", "NSM", "PSM"), ("DRM", "ARM")
            self.play(*[nodes[m].animate.scale(1.18) for m in out_m], run_time=0.8)
            ol = T("向外控制更强", 26, INK).move_to([0, 3.0, 0])
            il = T("更多被控制", 26, INK).move_to([0, -3.4, 0])
            self.play(FadeIn(ol), *[nodes[m].animate.scale(1 / 1.18) for m in out_m], run_time=0.8)
            self.play(FadeIn(il), *[Indicate(nodes[m], color=MCOL[m], scale_factor=1.15) for m in in_m], run_time=1.0)
        self.clear()

    # ------------------------------------------------------------------ control frequency
    def frequency(self):
        tag = self.chapter("三  结果与稳定性")
        data = [("自杀意念 (PHQ9)", 1.000, PINK), ("失眠第4条 (ISI4)", 0.778, GREEN), ("压力第2条 (PSS2)", 0.444, BLUE),
                ("压力第7条 (PSS7)", 0.370, VIOLET), ("焦虑第6条 (GAD6)", 0.222, GOLD)]
        W = 4.5
        rows = VGroup()
        for name, v, c in data:
            lab = T(name, 24, INK)
            bar = Rectangle(width=W * v, height=0.45, fill_color=c, fill_opacity=0.9, stroke_width=0)
            val = T(f"{v:.3f}", 24, c)
            rows.add(VGroup(lab, bar, val))
        for i, r in enumerate(rows):
            r[0].move_to([-3.6, 1.8 - i * 0.85, 0], aligned_edge=RIGHT).shift(RIGHT * 0.0)
            r[0].align_to(np.array([-2.6, 0, 0]), RIGHT)
            r[1].next_to(r[0], RIGHT, buff=0.3)
            r[1].align_to(np.array([-2.3, 0, 0]), LEFT)
            r[2].next_to(r[1], RIGHT, buff=0.2)
        with self.say("f1") as d:
            hd = T("控制频率", 28, MUTED).move_to([0.0, 2.7, 0])
            self.play(FadeIn(tag), FadeIn(hd), run_time=0.6)
            for r in rows:
                self.play(FadeIn(r[0]), GrowFromEdge(r[1], LEFT), FadeIn(r[2]), run_time=0.45)
        with self.say("f2") as d:
            box = SurroundingRectangle(rows[0], color=PINK, buff=0.12)
            self.play(Create(box), run_time=0.8)
            tt = T("27 / 27", 30, PINK, weight=BOLD).next_to(rows[0], DOWN, buff=0.1).align_to(rows[0][2], LEFT).shift(RIGHT * 0.0)
            tt.next_to(box, RIGHT, buff=0.2)
            self.play(FadeIn(tt), run_time=0.5)
        with self.say("f3") as d:
            self.play(*[FadeOut(m) for m in (rows, box, tt, hd)], run_time=0.6)
            # schematic: a weakly connected node beside a dense cluster
            rng = np.random.default_rng(1)
            cl = [np.array([1.0 + 1.3 * np.cos(t), 0.2 + 1.3 * np.sin(t), 0]) for t in np.linspace(0, TAU, 8, endpoint=False)]
            cd = VGroup(*[Dot(p, radius=0.17, color=MUTED) for p in cl])
            ce = VGroup(*[Line(cl[i], cl[j], color=MUTED, stroke_width=1.5, stroke_opacity=0.5) for i in range(8) for j in range(i + 1, 8) if rng.random() < 0.6])
            lone = Dot([-3.4, 0.2, 0], radius=0.22, color=PINK)
            le = VGroup(Line(lone.get_center(), cl[4], color=MUTED, stroke_width=2), Line(lone.get_center(), cl[3], color=MUTED, stroke_width=2))
            lt = T("自杀意念", 26, PINK).next_to(lone, UP, buff=0.25)
            self.play(Create(ce), FadeIn(cd), Create(le), FadeIn(lone), FadeIn(lt), run_time=1.2)
            low = T("中心性：最低", 26, MUTED).next_to(lone, DOWN, buff=0.35)
            self.play(FadeIn(low), run_time=0.6)
        with self.say("f4") as d:
            ring = Circle(radius=0.36, color=INK, stroke_width=4).move_to(lone)
            self.play(Create(ring), lone.animate.set_color(PINK), run_time=0.8)
            opt = T("要么自己被选", 24, INK).next_to(ring, LEFT, buff=0.2).shift(UP * 0.0)
            opt.next_to(low, DOWN, buff=0.3)
            self.play(FadeIn(opt), run_time=0.5)
            self.play(FadeOut(ring), run_time=0.3)
            rings2 = VGroup(*[Circle(radius=0.3, color=INK, stroke_width=4).move_to(cl[i]) for i in (3, 4)])
            opt2 = T("要么邻居之一被选", 24, INK).next_to(rings2, DOWN, buff=0.6)
            self.play(Create(rings2), FadeIn(opt2), run_time=0.9)
        with self.say("f5") as d:
            ne = T("控制频率高  ≠  临床更重要", 36, GOLD, weight=BOLD).to_edge(DOWN, buff=0.4)
            bgn = BackgroundRectangle(ne, color=BG, fill_opacity=0.9, buff=0.12)
            self.play(FadeIn(bgn), Write(ne), run_time=1.2)
        self.clear()

    # ------------------------------------------------------------------ stability
    def stability(self):
        tag = self.chapter("三  结果与稳定性")
        ppl = VGroup(*[Dot(radius=0.09, color=MUTED) for _ in range(200)]).arrange_in_grid(rows=10, cols=20, buff=0.18).shift(LEFT * 1.2 + UP * 0.2)
        rng = np.random.default_rng(3)
        with self.say("b1") as d:
            self.play(FadeIn(tag), FadeIn(ppl, lag_ratio=0.003), run_time=1.0)
            it = counter("重抽样", "第 1 次", INK).next_to(ppl, RIGHT, buff=0.6)
            self.play(FadeIn(it), run_time=0.3)
            for k, lab in enumerate(("第 1 次", "第 2 次", "第 3 次", "第 1000 次")):
                pick = set(rng.choice(200, 160, replace=False))
                self.play(*[p.animate.set_color(BLUE if i in pick else MUTED).set_opacity(1 if i in pick else 0.25) for i, p in enumerate(ppl)],
                          Transform(it, counter("重抽样", lab, INK).move_to(it)), run_time=0.6)
            pct = T("每次 80% 的样本", 24, BLUE).next_to(it, DOWN, buff=0.35)
            self.play(FadeIn(pct), run_time=0.4)
        with self.say("b2") as d:
            self.play(FadeOut(ppl), FadeOut(it), FadeOut(pct), run_time=0.5)
            rows = VGroup()
            for name in ("边数", "最小支配集个数"):
                ln = Line(LEFT * 2.5, RIGHT * 2.5, color=MUTED)
                br = VGroup(Line(LEFT * 1.4 + UP * 0.2, LEFT * 1.4 + DOWN * 0.2, color=BLUE, stroke_width=4),
                            Line(RIGHT * 1.6 + UP * 0.2, RIGHT * 1.6 + DOWN * 0.2, color=BLUE, stroke_width=4),
                            Line(LEFT * 1.4, RIGHT * 1.6, color=BLUE, stroke_width=6, stroke_opacity=0.5))
                dot = Dot(RIGHT * 0.2, radius=0.13, color=GOLD)
                lab = T(name, 26, INK).next_to(ln, LEFT, buff=0.4)
                rows.add(VGroup(lab, ln, br, dot))
            rows.arrange(DOWN, buff=0.9, aligned_edge=RIGHT).move_to(UP * 0.3)
            key = VGroup(VGroup(Line(ORIGIN, RIGHT * 0.5, color=BLUE, stroke_width=6), T("重抽样 95% 区间", 22, BLUE)).arrange(RIGHT, buff=0.15),
                         VGroup(Dot(radius=0.1, color=GOLD), T("全样本", 22, GOLD)).arrange(RIGHT, buff=0.15)).arrange(RIGHT, buff=0.6).to_edge(DOWN, buff=0.9)
            for r in rows:
                self.play(FadeIn(r[0]), Create(r[1]), Create(r[2]), run_time=0.6)
                self.play(GrowFromCenter(r[3]), run_time=0.4)
            self.play(FadeIn(key), run_time=0.4)
            m6 = T("多数重抽样网络：6 个模块", 26, INK).next_to(key, UP, buff=0.35)
            self.play(FadeIn(m6), run_time=0.5)
        with self.say("b3") as d:
            self.play(FadeOut(rows), FadeOut(key), FadeOut(m6), run_time=0.5)
            ax = Axes(x_range=[0, 100, 10], y_range=[0, 1, 0.5], x_length=8, y_length=4,
                      axis_config={"color": MUTED, "include_tip": False, "font_size": 22},
                      x_axis_config={"numbers_to_include": [10, 50, 100]}, y_axis_config={"numbers_to_include": [0, 0.5, 1]}).shift(DOWN * 0.3)
            xl = T("保留的样本比例 (%)", 22, MUTED).next_to(ax.x_axis, DOWN, buff=0.45)
            yl = T("与全样本结果的相关", 22, MUTED).rotate(PI / 2).next_to(ax.y_axis, LEFT, buff=0.4)
            self.play(Create(ax), FadeIn(xl), FadeIn(yl), run_time=1.0)
            zone = Polygon(ax.c2p(0, 0), ax.c2p(50, 0), ax.c2p(50, 0.5), ax.c2p(0, 0.5), color=RED, fill_opacity=0.18, stroke_width=0)
            h5 = DashedLine(ax.c2p(0, 0.5), ax.c2p(100, 0.5), color=RED)
            zl = T("平均控制频率：样本少于一半时低于 0.5", 22, RED).next_to(ax.c2p(52, 0.25), RIGHT, buff=0.1)
            self.play(FadeIn(zone), Create(h5), FadeIn(zl), run_time=1.2)
            h8 = DashedLine(ax.c2p(0, 0.8), ax.c2p(100, 0.8), color=GREEN)
            sl = T("节点强度：只留 10% 仍高于 0.8", 22, GREEN).next_to(ax.c2p(52, 0.9), RIGHT, buff=0.1)
            self.play(Create(h8), FadeIn(sl), run_time=1.0)
        self.clear()

    # ------------------------------------------------------------------ meaning & limits
    def meaning(self):
        tag = self.chapter("四  意义与局限")
        cen = {"SRM": np.array([-3.0, 0.8, 0]), "PSM": np.array([3.0, 0.8, 0]), "DRM": np.array([-1.6, -1.6, 0]), "ARM": np.array([1.6, -1.6, 0])}
        nodes = {m: Circle(radius=0.65, color=MCOL[m], fill_opacity=0.22).move_to(c).add(T(MNAME[m], 26, MCOL[m], weight=BOLD).move_to(c)) for m, c in cen.items()}
        with self.say("l1") as d:
            self.play(FadeIn(tag), *[GrowFromCenter(n) for n in nodes.values()], run_time=1.0)
            arrows = VGroup(Arrow(cen["SRM"], cen["DRM"], buff=0.7, color=GREEN), Arrow(cen["SRM"], cen["PSM"], buff=0.7, color=GREEN),
                            Arrow(cen["PSM"], cen["ARM"], buff=0.7, color=BLUE))
            self.play(LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.3), run_time=1.4)
            self.play(Indicate(nodes["SRM"], color=GREEN), Indicate(nodes["PSM"], color=BLUE), run_time=1.0)
        keep3 = list(self.mobjects)
        self.remove(*keep3)
        with self.say("l1b") as d:
            self.clip_on("yt_sleep_emotion_ted.mp4", "center", "视频：TED · YouTube", start=25)
        self.clip_off()
        self.add(*keep3)
        with self.say("l2") as d:
            grp = VGroup(*nodes.values(), arrows)
            self.play(grp.animate.scale(0.55).to_edge(LEFT, buff=0.5), run_time=0.8)
            crowd = VGroup(*[Dot(radius=0.07, color=MUTED) for _ in range(60)]).arrange_in_grid(rows=6, cols=10, buff=0.2).move_to(RIGHT * 2.0 + UP * 0.6)
            snap = T("一个时间点 · 一群人", 26, INK).next_to(crowd, DOWN, buff=0.35)
            self.play(FadeIn(crowd, lag_ratio=0.01), FadeIn(snap), run_time=1.0)
            nc = T("关联 ≠ 个体内的因果", 30, RED, weight=BOLD).next_to(snap, DOWN, buff=0.35)
            self.play(Write(nc), run_time=1.0)
        with self.say("l3") as d:
            self.play(FadeOut(crowd), FadeOut(snap), FadeOut(nc), run_time=0.5)
            tl = Arrow(LEFT * 1.0, RIGHT * 5.6, color=MUTED, buff=0).shift(DOWN * 0.2)
            ticks = VGroup(*[Line(UP * 0.12, DOWN * 0.12, color=MUTED).move_to(tl.point_from_proportion(t)) for t in (0.1, 0.4, 0.7)])
            tlab = T("纵向追踪 · 干预试验", 26, GOLD).next_to(tl, UP, buff=0.35)
            self.play(GrowArrow(tl), FadeIn(ticks), run_time=0.9)
            self.play(FadeIn(tlab), run_time=0.6)
            self.wait(d * 0.2)
        with self.say("l4") as d:
            self.play(FadeOut(tl), FadeOut(ticks), FadeOut(tlab), FadeOut(grp), run_time=0.5)
            a1, b1 = np.array([-4.5, 1.0, 0]), np.array([-1.5, 1.0, 0])
            a2, b2 = np.array([-4.5, -1.0, 0]), np.array([-1.5, -1.0, 0])
            e1 = VGroup(Line(a1, b1, color=INK, stroke_width=12), Dot(a1, radius=0.2, color=BLUE), Dot(b1, radius=0.2, color=BLUE))
            e2 = VGroup(Line(a2, b2, color=INK, stroke_width=1, stroke_opacity=0.5), Dot(a2, radius=0.2, color=BLUE), Dot(b2, radius=0.2, color=BLUE))
            w1 = T("1.568", 24, INK).next_to(e1, UP, buff=0.15)
            w2 = T("0.0002", 24, MUTED).next_to(e2, UP, buff=0.15)
            self.play(FadeIn(e1), FadeIn(e2), FadeIn(w1), FadeIn(w2), run_time=0.9)
            eq = VGroup(T("支配集眼里：", 26, MUTED), T("都是 “有边”", 30, GOLD, weight=BOLD)).arrange(DOWN, buff=0.15).move_to([1.2, 0, 0])
            br = Brace(VGroup(e1, e2), RIGHT, color=MUTED)
            self.play(GrowFromCenter(br), FadeIn(eq), run_time=0.9)
            sg = VGroup(T("+0.3", 30, GREEN), T("−0.3", 30, RED), T("→", 30, MUTED), T("0.3", 30, INK)).arrange(RIGHT, buff=0.25).move_to([4.6, 0, 0])
            sg[0].shift(UP * 0.3); sg[1].shift(DOWN * 0.3)
            self.play(FadeIn(sg), run_time=0.8)
        with self.say("l5") as d:
            self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.6)
            G, mod = symptom_graph()
            pos1 = cluster_pos(0.6)
            pos1 = {v: p * np.array([0.75, 0.8, 1]) for v, p in pos1.items()}
            dots, edges, net = self.draw(G, pos1, {v: MCOL[mod[v]] for v in G}, r=0.07, eo=0.1)
            self.play(FadeIn(net), run_time=0.8)
            hyp = T("值得检验的假设", 40, GOLD, weight=BOLD).to_edge(DOWN, buff=0.4)
            self.play(Write(hyp), run_time=1.2)
        self.wait(0.8)
        self.clear(1.0)
