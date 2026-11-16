"""Paper explainer: 癌症维持基因（控制枢纽）."""
import random

import networkx as nx
import numpy as np

from common import *  # noqa: F401,F403
from ep_robustness import fit, counter
from fctrl import DiNet, kuhn, drivers, possible_heads, possible_tails, control_hubs

TITLE = "癌症维持基因：所有控制方案都绕不开的节点"

LINES = {
    # hook
    "h1": "先看一张网络。每个圆圈是癌细胞里的一个基因，箭头表示一个基因调控另一个。",
    "h2": "要控制整张网络，需要从几个节点输入信号。这些节点叫驱动节点，标成了黄色。",
    "h3": "但驱动节点的选法不止一种。你看，换一个方案，黄色的节点就变了。",
    "h4": "把所有方案里的驱动节点合在一起——这张小网络里，一半的节点都上了名单。",
    "h5": "在真实的癌症网络里，这份名单有好几千个基因，不可能同时干预。",
    "h6": "【慢】这项研究要找的，是不管选哪种方案，角色都不变的那一小批节点。",
    # parts
    "q0": "这一期分四部分。",
    "q1": "第一部分，控制路径和控制枢纽。",
    "q2": "第二部分，膀胱癌网络里的癌症维持基因。",
    "q3": "第三部分，临床和实验证据。",
    "q4": "第四部分，意义和局限。",
    # control paths
    "p1": "先看第一部分。最简单的情形：三个基因排成一条链，甲调控乙，乙调控丙。",
    "p2": "信号从甲输入，沿着箭头传到乙，再传到丙。",
    "p2b": "在这条路径上，甲是头，丙是尾，乙在中间。",
    "p3": "一般的网络，会被拆成好几条这样的控制路径。每条路径的头，就是一个驱动节点。",
    "p3b": "怎么拆，由最大匹配决定：挑出尽量多的箭头，每个节点最多被一条挑中的箭头指向。挑中的就是黄边。",
    "p4": "好，现在给甲再加一个下游基因，叫它丁。",
    "p5": "挑中的箭头还是两条，却出现了第二种方案：甲连向丁，乙没了上游，自己变成了头。",
    "p6": "【慢】在所有控制方案中，都位于路径中间的节点，叫作控制枢纽。",
    "p6b": "乙有时是头，所以它不是控制枢纽。",
    # algorithm
    "a1": "注意，控制方案往往多到无法一一列出，枚举全部方案极其困难。",
    "a2": "这项研究换了个思路：一个节点既不可能当头，也不可能当尾，就只能在中间。",
    "a3": "所有可能的头，就是所有方案中驱动节点的并集，已有算法能一次求出，就是蓝色节点。",
    "a4": "把所有箭头反过来——反向网络的头，就是原网络的尾，画成了绿色圆圈。",
    "a5": "剩下的节点，既当不了头，也当不了尾，它们就是控制枢纽。这里是三个红色节点。",
    "a6": "下方这个式子说的就是：控制枢纽，等于全部节点，去掉可能的头，再去掉可能的尾。",
    "a6b": "【慢】这只需要多项式时间，计算量不会爆炸，绕开了枚举所有方案的难题。",
    # bladder cancer network
    "b0": "下面进入第二部分，以膀胱癌为例。画面是膀胱癌组织在显微镜下的样子。",
    "b1": "研究从五个通路数据库出发，以九十五个膀胱癌相关基因为起点，一圈圈往外找调控伙伴。",
    "b2": "得到一张网络：七千零三十个基因，十万三千多条有向边。",
    "b3": "几乎所有基因连成一整团，叫巨连通分支，占百分之九十九点二。所以它更接近一张泛癌网络。",
    "b4": "下面每根条的长度，是占全部基因的比例。一个控制方案，就有三千一百一十五个驱动基因。",
    "b5": "所有方案合在一起，驱动基因多达五千零五十二个，占七成以上。",
    "b6": "【慢】而控制枢纽只有六百六十个，不到一成。这项研究把它们叫作癌症维持基因。",
    "b7": "度，就是连接数。维持基因的平均度约为九十六，其他基因不到三十。",
    "b7b": "通路，是一组协同工作的基因。右边是细胞周期和p53两条通路，里面的基因全部是维持基因。",
    # sensitive keepers
    "s1": "不过，并不是所有维持基因都同样牢固。",
    "s2": "回到小网络。删掉指向这个红色枢纽的一条边，它就能当头了，失去了枢纽身份。",
    "s3": "删一条边，好比药物阻断一对蛋白的相互作用。这样的维持基因，叫敏感维持基因。",
    "s4": "六百六十个维持基因里，有一百七十三个是敏感的，大约四分之一，就是这些黄色方块。",
    "s5": "左边红柱，是其他维持基因的平均连接度；右边黄柱是敏感维持基因的，不到一半。",
    "s6": "它们自身的突变和表达不突出，邻居却更活跃，所以只看突变频率，很容易漏掉。",
    # clinic
    "c1": "下面进入第三部分。先把敏感维持基因，和人类蛋白网络里的不可或缺基因取交集，得到三十五个基因。",
    "c2": "其中三十个连着治疗靶点，二十七个连着免疫基因，二十六个直接连着驱动基因。",
    "c3": "再看临床数据。横轴是这三十五个基因里有几个发生改变，纵轴是中位生存期，也就是一半患者能活过的时间。",
    "c3b": "四百一十一例膀胱癌样本里，三十五个基因都没改变的患者，中位生存期约二十八个月。",
    "c4": "有一个、两个、三个以上改变的患者，中位生存期依次变长，最长超过一百个月。",
    "c5": "【慢】注意，这只是相关性，不能说明改变这些基因会延长生存。",
    # experiments
    "e0": "然后是实验。敲低，是用一小段核糖核酸，把某个基因的表达降下来。画面是原理动画。",
    "e1": "研究在两种膀胱癌细胞里，分别敲低六个候选基因。右边两列是增殖和迁移。",
    "e1b": "增殖，是细胞分裂变多，像画面里这样一分为二；迁移，是细胞移动的能力。",
    "e2": "绿色向下箭头表示减弱。敲低三个基因后，增殖都显著下降；除了一个基因，迁移也都减弱。",
    "e3": "移植瘤，是把癌细胞种到小鼠身上长成的肿瘤。敲低其中一个基因后，肿瘤明显更小、更轻。",
    "e4": "也有反方向的结果：敲低一个基因，反而促进增殖和迁移。还有两个基因，效果因细胞系而异。",
    "e5": "【慢】而且六个基因里有两个是已知驱动基因。所以它们是候选靶点，还不是疗法。",
    # meaning & limits
    "l1": "最后是第四部分。左边山谷是正常状态，右边是癌变状态，小球是细胞。驱动基因把它推过去，维持基因把它留在那里。",
    "l2": "控制枢纽不必枚举就能求出，数量又少，给靶点筛选提供了一个小得多的候选池。",
    "l3": "局限有三点。第一，网络是泛癌的，没有去掉膀胱癌里不存在的边。",
    "l4": "第二，基因表达、表观修饰和肿瘤微环境，都还没有进入模型。",
    "l5": "第三，扰动维持基因让细胞离开癌变状态，目前还是模型推论，需要机制研究支持。",
    # recap
    "r0": "好，我们来总结一下。",
    "r1": "第一，所有方案中都在路径中间的节点，叫控制枢纽，不必枚举就能求出。",
    "r2": "第二，膀胱癌网络里，控制枢纽只有六百六十个，其中一百七十三个是敏感的。",
    "r3": "第三，临床和实验证据有正有负，它们还只是候选靶点。",
    "r4": "结构可控性这一页有这个交互演示：红色是驱动节点，橙色边是一组最大匹配。拖动平均出度，驱动节点的数量会跟着变。",
}

GSEED = 70
SCHEME_SEEDS = (0, 1, 5)


def demo_graph():
    return nx.gnm_random_graph(14, 20, seed=GSEED, directed=True)


def mark(c, color, op=0.85):
    return c.animate.set_fill(color, opacity=op, family=False).set_stroke(color, family=False)


class Episode(Narrated):
    LINES = LINES

    def construct(self):
        self.hook()
        self.parts()
        self.paths()
        self.algorithm()
        self.bladder()
        self.sensitive()
        self.clinic()
        self.experiments()
        self.meaning()
        self.recap()

    # ------------------------------------------------------------------ helpers
    def demo(self, box=(-4.6, 4.6, -3.1, 2.7), r=0.2):
        G = demo_graph()
        pos = fit(nx.kamada_kawai_layout(G), box)
        return G, DiNet(G, pos, r=r, color=BLUE, ecolor=MUTED, ew=2.6, eo=0.7)

    def scheme(self, G, net, match, dcolor=GOLD):
        anims = []
        drv = set(drivers(G, match))
        for v, c in net.nodes.items():
            anims.append(c.animate.set_fill(dcolor if v in drv else BG, opacity=0.9 if v in drv else 1)
                         .set_stroke(dcolor if v in drv else BLUE))
        mset = {(u, v) for v, u in match.items()}
        for e, ln in net.edges.items():
            anims.append(ln.animate.set_color(dcolor if e in mset else MUTED)
                         .set_stroke(width=4.5 if e in mset else 2.6, opacity=1 if e in mset else 0.45))
        return anims

    def clear(self, rt=0.8, keep=None):
        self.play(*[FadeOut(m) for m in self.mobjects if m is not keep], run_time=rt)

    # ------------------------------------------------------------------ hook
    def hook(self):
        G, net = self.demo()
        with self.say("h1") as d:
            self.play(LaggedStart(*[GrowFromCenter(c) for c in net.nodes.values()], lag_ratio=0.05), run_time=d * 0.4)
            self.play(LaggedStart(*[Create(e) for e in net.edges.values()], lag_ratio=0.05), run_time=d * 0.45)
        ms = []
        for s in SCHEME_SEEDS:
            o = list(G); random.Random(s).shuffle(o)
            ms.append(kuhn(G, o))
        lab = counter("驱动节点", f"{len(drivers(G, ms[0]))} 个", GOLD).to_corner(UR, buff=0.5)
        with self.say("h2") as d:
            self.play(*self.scheme(G, net, ms[0]), run_time=1.4)
            self.play(FadeIn(lab), run_time=0.6)
        tag = T("方案 1", 26, GOLD).next_to(lab, DOWN, buff=0.3)
        with self.say("h3") as d:
            self.play(FadeIn(tag), run_time=0.4)
            for i in (1, 2):
                self.wait(d * 0.12)
                self.play(*self.scheme(G, net, ms[i]), Transform(tag, T(f"方案 {i + 1}", 26, GOLD).move_to(tag)), run_time=1.2)
        heads = possible_heads(G)
        with self.say("h4") as d:
            self.play(*[c.animate.set_fill(GOLD, opacity=0.9 if v in heads else 0).set_stroke(GOLD if v in heads else BLUE)
                        for v, c in net.nodes.items()],
                      *[e.animate.set_color(MUTED).set_stroke(width=2.6, opacity=0.45) for e in net.edges.values()],
                      Transform(tag, T("所有方案合计", 26, GOLD).move_to(tag)),
                      Transform(lab, counter("驱动节点", f"{len(heads)} / {G.number_of_nodes()}", GOLD).move_to(lab)), run_time=1.6)
        with self.say("h5") as d:
            big = counter("真实癌症网络", "几千个基因", RED).to_corner(DR, buff=0.6)
            self.play(net.group.animate.scale(0.8).shift(LEFT * 1.2), FadeIn(big, shift=UP * 0.2), run_time=1.4)
        with self.say("h6") as d:
            q = T("找出角色永远不变的节点", 48, INK, weight=BOLD)
            self.play(net.group.animate.set_opacity(0.12), FadeOut(lab), FadeOut(tag), FadeOut(big), run_time=1.0)
            self.play(Write(q), run_time=1.6)
        self.clear()

    def parts(self):
        head, items = slide("这一期分四部分", ["一  控制路径与控制枢纽", "二  膀胱癌网络里的维持基因", "三  临床与实验证据", "四  意义与局限"])
        with self.say("q0") as d:
            self.play(FadeIn(head, shift=RIGHT * 0.3), run_time=0.6)
        for k, it in zip(("q1", "q2", "q3", "q4"), items):
            with self.say(k) as d:
                self.play(FadeIn(it, shift=RIGHT * 0.3), run_time=0.6)
        self.wait(0.6)
        self.play(FadeOut(head), FadeOut(items), run_time=0.6)

    # ------------------------------------------------------------------ control paths
    def paths(self):
        tag = self.chapter("一  控制路径与控制枢纽")
        P = {"甲": np.array([-4, 1.2, 0]), "乙": np.array([0, 1.2, 0]), "丙": np.array([4, 1.2, 0]), "丁": np.array([-1.6, -1.6, 0])}
        C = nx.DiGraph([("甲", "乙"), ("乙", "丙")])
        net = DiNet(C, P, r=0.45, color=BLUE, ecolor=MUTED, ew=4, labels={k: k for k in P}, lsize=34, tip=0.28)
        with self.say("p1") as d:
            self.play(FadeIn(tag), *[GrowFromCenter(net.nodes[v]) for v in C], run_time=1.0)
            self.play(*[Create(e) for e in net.edges.values()], run_time=1.0)
        role = {}
        with self.say("p2") as d:
            pulse = Dot(P["甲"] + LEFT * 1.6, radius=0.12, color=GOLD)
            self.play(FadeIn(pulse), run_time=0.3)
            self.play(pulse.animate.move_to(P["甲"]), run_time=0.5)
            self.play(pulse.animate.move_to(P["乙"]), net.edge("甲", "乙").animate.set_color(GOLD), run_time=0.8)
            self.play(pulse.animate.move_to(P["丙"]), net.edge("乙", "丙").animate.set_color(GOLD), run_time=0.8)
            self.play(FadeOut(pulse), run_time=0.3)
        with self.say("p2b") as d:
            for v, s, c in (("甲", "头", GOLD), ("乙", "中间", RED), ("丙", "尾", GREEN)):
                role[v] = T(s, 28, c).next_to(net.nodes[v], DOWN, buff=0.3)
            self.play(LaggedStart(*[FadeIn(x, shift=UP * 0.2) for x in role.values()], lag_ratio=0.3), mark(net.nodes["甲"], GOLD, 0.35),
                      mark(net.nodes["乙"], RED, 0.35), run_time=1.6)
        # whole network with its control paths
        chain = VGroup(net.group, *role.values())
        with self.say("p3") as d:
            self.play(chain.animate.scale(0.55).to_edge(UP, buff=0.6), run_time=0.8)
            G, big = self.demo(box=(-4.0, 4.0, -3.5, 0.9), r=0.16)
            o = list(G); random.Random(SCHEME_SEEDS[0]).shuffle(o)
            self.play(FadeIn(big.group), run_time=0.8)
        with self.say("p3b") as d:
            self.play(*self.scheme(G, big, kuhn(G, o)), run_time=1.4)
            self.play(*[Indicate(big.edges[(u, v)], color=GOLD) for v, u in kuhn(G, o).items()], run_time=1.4)
        with self.say("p4") as d:
            self.play(FadeOut(big.group), chain.animate.scale(1 / 0.55).move_to(ORIGIN + UP * 0.0), run_time=1.0)
            C.add_edge("甲", "丁")
            net2 = DiNet(C, P, r=0.45, color=BLUE, ecolor=MUTED, ew=4, labels={k: k for k in P}, lsize=34, tip=0.28)
            # re-use the existing chain mobjects; only add the new node + arrow
            dn = net2.nodes["丁"].move_to(net.nodes["甲"].get_center() + (P["丁"] - P["甲"]))
            ad = DiNet(nx.DiGraph([("甲", "丁")]), {"甲": net.nodes["甲"].get_center(), "丁": dn.get_center()}, r=0.45, ew=4, tip=0.28).edge("甲", "丁")
            self.play(GrowFromCenter(dn), Create(ad), run_time=1.0)
        with self.say("p5") as d:
            s1 = T("方案一", 28, GOLD).to_corner(UR, buff=0.6)
            self.play(FadeIn(s1), run_time=0.5)
            self.wait(d * 0.15)
            new_roles = {"甲": T("头", 28, GOLD), "乙": T("头", 28, GOLD), "丙": T("尾", 28, GREEN)}
            self.play(net.edge("甲", "乙").animate.set_color(MUTED).set_stroke(opacity=0.35), ad.animate.set_color(GOLD),
                      mark(net.nodes["乙"], GOLD, 0.35),
                      *[Transform(role[v], new_roles[v].move_to(role[v])) for v in role],
                      Transform(s1, T("方案二", 28, GOLD).move_to(s1)), run_time=1.6)
            self.play(Indicate(net.nodes["乙"], color=GOLD, scale_factor=1.25), run_time=1.0)
        with self.say("p6") as d:
            defn = VGroup(T("控制枢纽", 36, RED, weight=BOLD), T("在所有方案中都位于路径中间", 28, INK)).arrange(DOWN, buff=0.2).move_to([3.4, -1.9, 0])
            self.play(FadeIn(defn, shift=UP * 0.2), run_time=1.0)
        with self.say("p6b") as d:
            x = Cross(net.nodes["乙"], stroke_color=RED, scale_factor=0.8)
            self.play(Create(x), run_time=0.8)
        self.clear()

    # ------------------------------------------------------------------ algorithm
    def algorithm(self):
        tag = self.chapter("一  控制路径与控制枢纽")
        with self.say("a1") as d:
            cards = VGroup(*[RoundedRectangle(corner_radius=0.1, width=1.3, height=1.0, stroke_color=MUTED, stroke_width=2,
                                              fill_color="#182133", fill_opacity=1) for _ in range(24)])
            for i, c in enumerate(cards):
                c.move_to(np.array([-5.25 + (i % 8) * 1.5, 1.6 - (i // 8) * 1.3, 0]))
                c.add(T(f"方案 {i + 1}", 18, MUTED).move_to(c))
            dots = T("……", 40, MUTED).next_to(cards, DOWN, buff=0.3)
            self.play(FadeIn(tag), LaggedStart(*[FadeIn(c, shift=DOWN * 0.2) for c in cards], lag_ratio=0.06), run_time=d * 0.6)
            self.play(FadeIn(dots), run_time=0.5)
        G, net = self.demo(box=(-4.2, 4.2, -3.0, 2.6))
        with self.say("a2") as d:
            self.play(FadeOut(cards), FadeOut(dots), run_time=0.6)
            self.play(FadeIn(net.group), run_time=1.0)
            rule = VGroup(T("不可能当头", 28, BLUE), T("+", 28, MUTED), T("不可能当尾", 28, GREEN), T("→", 28, MUTED), T("只能在中间", 28, RED)
                          ).arrange(RIGHT, buff=0.25).to_edge(DOWN, buff=0.35)
            self.play(FadeIn(rule, lag_ratio=0.2), run_time=1.6)
        heads, tails, hubs = possible_heads(G), possible_tails(G), control_hubs(G)
        with self.say("a3") as d:
            self.play(*[mark(net.nodes[v], BLUE, 0.85) for v in heads], run_time=1.2)
            hl = T("可能的头", 26, BLUE).to_corner(UR, buff=0.5)
            self.play(FadeIn(hl), run_time=0.5)
        with self.say("a4") as d:
            flips = []
            for (u, v), ln in net.edges.items():
                flips.append(ln.animate.rotate(PI))
            self.play(*flips, run_time=1.4)
            rev = T("箭头反向", 26, MUTED).next_to(hl, DOWN, buff=0.25)
            self.play(FadeIn(rev), *[net.nodes[v].animate.set_stroke(GREEN, width=7) for v in tails], run_time=1.2)
            self.play(*[ln.animate.rotate(PI) for ln in net.edges.values()], FadeOut(rev), run_time=1.2)
            tl = T("可能的尾", 26, GREEN).next_to(hl, DOWN, buff=0.25)
            self.play(FadeIn(tl), run_time=0.5)
        with self.say("a5") as d:
            others = [v for v in G if v not in hubs]
            self.play(*[net.nodes[v].animate.set_opacity(0.18) for v in others],
                      *[e.animate.set_stroke(opacity=0.2) for e in net.edges.values()], run_time=1.0)
            self.play(*[net.nodes[v].animate.set_fill(RED, opacity=0.9).set_stroke(RED, width=4).scale(1.3) for v in hubs], run_time=1.0)
            cl = T("控制枢纽", 26, RED).next_to(tl, DOWN, buff=0.25)
            self.play(FadeIn(cl), run_time=0.5)
        with self.say("a6") as d:
            f = VGroup(T("控制枢纽", 30, RED), T("=", 30, INK), T("全部节点", 30, INK), T("−", 30, INK),
                       T("可能的头", 30, BLUE), T("−", 30, INK), T("可能的尾", 30, GREEN)).arrange(RIGHT, buff=0.2)
            f.move_to(rule).set_x(-1.4)
            box = SurroundingRectangle(f, color=MUTED, buff=0.18, corner_radius=0.1)
            poly = T("多项式时间", 30, GOLD, weight=BOLD).next_to(box, RIGHT, buff=0.3)
            self.play(FadeOut(rule), run_time=0.4)
            self.play(FadeIn(f, lag_ratio=0.15), Create(box), run_time=1.4)
        with self.say("a6b") as d:
            self.play(FadeIn(poly, shift=UP * 0.2), run_time=0.6)
        self.clear()

    # ------------------------------------------------------------------ bladder cancer network
    def bladder(self):
        tag = self.chapter("二  膀胱癌网络里的维持基因")
        rng = np.random.default_rng(3)
        n = 420
        P = np.c_[rng.uniform(-6.3, 6.3, n), rng.uniform(-3.2, 2.6, n)]
        G = nx.random_geometric_graph(n, 0.09, pos={i: (P[i] + [6.3, 3.2]) / [12.6, 5.8] for i in range(n)}, seed=3)
        dots = VGroup(*[Dot([*P[i], 0], radius=0.035, color=MUTED).set_opacity(0.5) for i in range(n)])
        seeds = list(rng.choice(n, 12, replace=False))
        with self.say("b0") as d:
            self.clip_on("yt_bladder_histology.mp4", "center", "视频：Pathweb Teacher · YouTube", start=40)
        self.clip_off()
        with self.say("b1") as d:
            self.play(FadeIn(tag), FadeIn(dots, lag_ratio=0.002), run_time=1.2)
            self.play(*[dots[s].animate.set_color(RED).set_opacity(1).scale(2.2) for s in seeds], run_time=0.8)
            dist = nx.multi_source_dijkstra_path_length(G, seeds, weight=None)
            maxd = max(dist.values())
            waves = [[v for v, k in dist.items() if k == step] for step in range(1, maxd + 1)]
            per = max(0.12, d * 0.45 / max(1, len(waves)))
            for w in waves:
                self.play(*[dots[v].animate.set_color(BLUE).set_opacity(0.95) for v in w], run_time=per)
        with self.say("b2") as d:
            c1 = counter("基因", "7030", BLUE)
            c2 = counter("有向边", "103360", BLUE)
            row = VGroup(c1, c2).arrange(RIGHT, buff=1.4).to_edge(DOWN, buff=0.35)
            bg = BackgroundRectangle(row, color=BG, fill_opacity=0.85, buff=0.2)
            self.play(FadeIn(bg), FadeIn(row, shift=UP * 0.2), run_time=1.0)
        with self.say("b3") as d:
            gc = counter("巨连通分支", "99.2% 的节点", GOLD).to_corner(UR, buff=0.5)
            gbg = BackgroundRectangle(gc, color=BG, fill_opacity=0.85, buff=0.15)
            self.play(dots.animate.set_color(GOLD), FadeIn(gbg), FadeIn(gc), run_time=1.4)
        self.clear(0.6, keep=tag)
        # bars
        W = 9.0
        x0 = -3.2
        rows = [("一个方案的驱动基因", 3115, 44.3, GOLD), ("所有方案的驱动基因", 5052, 71.9, VIOLET), ("控制枢纽", 660, 9.4, RED)]
        frame = Rectangle(width=W, height=0.0, stroke_width=0)
        objs = []
        for i, (name, k, pct, c) in enumerate(rows):
            y = 1.6 - i * 1.6
            track = Rectangle(width=W * 0.95, height=0.7, stroke_color=MUTED, stroke_width=1.5).move_to([x0 + W * 0.95 / 2, y, 0])
            bar = Rectangle(width=W * 0.95 * pct / 100, height=0.7, fill_color=c, fill_opacity=0.9, stroke_width=0).move_to(track, aligned_edge=LEFT)
            lab = T(name, 26, INK).next_to(track, LEFT, buff=0.3)
            val = T(f"{k}  ({pct}%)", 28, c, weight=BOLD).next_to(bar, RIGHT, buff=0.25)
            objs.append((track, bar, lab, val))
        allg = VGroup(*[VGroup(*o) for o in objs])
        shift = -allg.get_center()[0]
        for o in objs:
            for m in o:
                m.shift(RIGHT * shift)
        for key, (track, bar, lab, val) in zip(("b4", "b5", "b6"), objs):
            with self.say(key) as d:
                self.play(FadeIn(lab), Create(track), run_time=0.6)
                self.play(GrowFromEdge(bar, LEFT), run_time=1.2)
                self.play(FadeIn(val), run_time=0.4)
        with self.say("b7") as d:
            ckg = T("癌症维持基因", 30, RED, weight=BOLD).next_to(objs[2][1], DOWN, buff=0.35).align_to(objs[2][1], LEFT)
            self.play(FadeIn(ckg), run_time=0.6)
            self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.6)
            k1 = counter("维持基因平均度", "96.4", RED)
            k2 = counter("其他基因平均度", "29.4", MUTED)
            krow = VGroup(k1, k2).arrange(RIGHT, buff=1.0).move_to(LEFT * 3.3)
            self.play(FadeIn(k1, shift=UP * 0.2), FadeIn(k2, shift=UP * 0.2), run_time=0.9)
        with self.say("b7b") as d:
            rings = VGroup()
            for j, name in enumerate(("细胞周期", "p53")):
                ctr = np.array([1.8 + j * 3.2, 0, 0])
                ring = VGroup(*[Dot(ctr + 1.1 * np.array([np.cos(t), np.sin(t), 0]), radius=0.1, color=MUTED)
                                for t in np.linspace(0, TAU, 14, endpoint=False)])
                rings.add(VGroup(ring, T(name, 26, INK).move_to(ctr)))
            self.play(FadeIn(rings), run_time=0.7)
            self.play(*[d_.animate.set_color(RED) for r in rings for d_ in r[0]], run_time=1.0)
            full = T("100% 是维持基因", 28, RED).next_to(rings, DOWN, buff=0.4)
            self.play(FadeIn(full), run_time=0.5)
        self.clear()

    # ------------------------------------------------------------------ sensitive keepers
    def sensitive(self):
        tag = self.chapter("二  膀胱癌网络里的维持基因")
        G, net = self.demo(box=(-4.2, 4.2, -3.0, 2.6))
        hubs = control_hubs(G)
        for v in hubs:
            net.nodes[v].set_fill(RED, opacity=0.9).set_stroke(RED)
        with self.say("s1") as d:
            self.play(FadeIn(tag), FadeIn(net.group), run_time=1.2)
        hub, e = 4, (0, 4)
        H = G.copy(); H.remove_edge(*e)
        assert hub in hubs and hub not in control_hubs(H)
        with self.say("s2") as d:
            self.play(Indicate(net.nodes[hub], color=RED, scale_factor=1.4), run_time=0.9)
            self.play(net.edges[e].animate.set_color(RED).set_stroke(width=6, opacity=1), run_time=0.6)
            sc = Cross(net.edges[e], stroke_color=RED, scale_factor=0.5)
            self.play(Create(sc), run_time=0.5)
            self.play(FadeOut(net.edges[e]), FadeOut(sc), run_time=0.6)
            role = "头" if hub in possible_heads(H) else "尾"
            self.play(net.nodes[hub].animate.set_fill(BLUE, opacity=0.85).set_stroke(BLUE), run_time=0.8)
            lost = T(f"可以当{role}了", 26, BLUE).next_to(net.nodes[hub], UP, buff=0.2)
            self.play(FadeIn(lost), run_time=0.4)
        with self.say("s3") as d:
            pill = VGroup(RoundedRectangle(corner_radius=0.25, width=1.3, height=0.5, fill_color=GREEN, fill_opacity=0.9, stroke_width=0),
                          T("药物", 22, BG, weight=BOLD)).arrange(ORIGIN)
            pill[1].move_to(pill[0])
            mid = (net.pos[0] + net.pos[4]) / 2
            pill.move_to(mid + UP * 1.5)
            self.play(FadeIn(pill, shift=DOWN * 0.3), FadeOut(lost), run_time=0.7)
            self.play(pill.animate.move_to(mid), run_time=0.7)
            name = T("敏感维持基因", 30, GOLD, weight=BOLD).to_corner(UR, buff=0.5)
            self.play(FadeIn(name), net.nodes[hub].animate.set_stroke(GOLD, width=7), run_time=0.8)
        self.clear(0.6, keep=tag)
        with self.say("s4") as d:
            sq = VGroup(*[Square(side_length=0.15, stroke_width=0, fill_color=RED, fill_opacity=0.8) for _ in range(660)])
            sq.arrange_in_grid(rows=20, cols=33, buff=0.04).move_to(LEFT * 1.6)
            self.play(FadeIn(sq, lag_ratio=0.001), run_time=1.2)
            self.play(*[s.animate.set_fill(GOLD, opacity=1) for s in sq[:173]], run_time=1.0)
            lab = VGroup(counter("维持基因", "660", RED), counter("其中敏感", "173 (26.2%)", GOLD)).arrange(DOWN, buff=0.5).next_to(sq, RIGHT, buff=0.7)
            self.play(FadeIn(lab, shift=LEFT * 0.2), run_time=0.8)
        with self.say("s5") as d:
            self.play(FadeOut(sq), FadeOut(lab), run_time=0.6)
            base = -1.6
            b1 = Rectangle(width=1.4, height=3.6, fill_color=RED, fill_opacity=0.8, stroke_width=0).move_to([-2, base, 0], aligned_edge=DOWN)
            b2 = Rectangle(width=1.4, height=1.55, fill_color=GOLD, fill_opacity=0.9, stroke_width=0).move_to([1, base, 0], aligned_edge=DOWN)
            axis = Line([-3.4, base, 0], [2.4, base, 0], color=MUTED)
            l1 = T("其他维持基因", 24, INK).next_to(b1, DOWN, buff=0.25)
            l2 = T("敏感维持基因", 24, INK).next_to(b2, DOWN, buff=0.25)
            yl = T("平均连接度", 24, MUTED).move_to([-0.5, 2.6, 0])
            self.play(Create(axis), FadeIn(yl), GrowFromEdge(b1, DOWN), FadeIn(l1), run_time=1.0)
            self.play(GrowFromEdge(b2, DOWN), FadeIn(l2), run_time=1.0)
            half = DashedLine([0.1, base + 1.8, 0], [1.9, base + 1.8, 0], color=MUTED)
            hl = T("一半", 22, MUTED).next_to(half, RIGHT, buff=0.15)
            self.play(Create(half), FadeIn(hl), run_time=0.6)
            bars = VGroup(b1, b2, axis, l1, l2, yl, half, hl)
        with self.say("s6") as d:
            self.play(bars.animate.scale(0.6).to_edge(LEFT, buff=0.6), run_time=0.8)
            ctr = np.array([3.0, 0, 0])
            nbr = [ctr + 2.0 * np.array([np.cos(t), np.sin(t), 0]) for t in np.linspace(0, TAU, 7, endpoint=False) + 0.3]
            ls = VGroup(*[Line(ctr, p, color=MUTED, stroke_width=2) for p in nbr])
            nd = VGroup(*[Dot(p, radius=0.2, color=MUTED) for p in nbr])
            c = Dot(ctr, radius=0.28, color=GOLD)
            self.play(Create(ls), FadeIn(nd), FadeIn(c), run_time=0.9)
            self.play(*[x.animate.set_color(RED).scale(1.3) for x in nd], run_time=0.9)
            t1 = T("自身：突变、表达不突出", 22, GOLD).next_to(c, DOWN, buff=2.5)
            t2 = T("邻居：改变和表达更高", 22, RED).next_to(t1, DOWN, buff=0.15)
            self.play(FadeIn(t1), FadeIn(t2), run_time=0.8)
        self.clear()

    # ------------------------------------------------------------------ clinical association
    def clinic(self):
        tag = self.chapter("三  临床与实验证据")
        with self.say("c1") as d:
            a = Circle(radius=1.6, color=GOLD, fill_opacity=0.12).shift(LEFT * 1.0)
            b = Circle(radius=1.6, color=BLUE, fill_opacity=0.12).shift(RIGHT * 1.0)
            la = T("敏感维持基因", 24, GOLD).next_to(a, UP, buff=0.2).shift(LEFT * 0.6)
            lb = T("不可或缺基因", 24, BLUE).next_to(b, UP, buff=0.2).shift(RIGHT * 0.6)
            self.play(FadeIn(tag), Create(a), Create(b), FadeIn(la), FadeIn(lb), run_time=1.4)
            k = T("35", 48, INK, weight=BOLD).move_to(ORIGIN)
            inter = Intersection(a, b, color=INK, fill_opacity=0.35, stroke_width=0)
            self.play(FadeIn(inter), Write(k), run_time=1.0)
        with self.say("c2") as d:
            venn = VGroup(a, b, la, lb, k, inter)
            self.play(venn.animate.scale(0.6).to_edge(LEFT, buff=0.6), run_time=0.8)
            cs = VGroup(counter("连着治疗靶点", "30 / 35", GREEN), counter("连着免疫基因", "27 / 35", VIOLET),
                        counter("直接连着驱动基因", "26 / 35", GOLD)).arrange(DOWN, buff=0.45).move_to(RIGHT * 2.6)
            self.play(LaggedStart(*[FadeIn(c, shift=LEFT * 0.2) for c in cs], lag_ratio=0.35), run_time=d * 0.6)
        self.play(FadeOut(venn), FadeOut(cs), run_time=0.6)
        ax = Axes(x_range=[0, 4, 1], y_range=[0, 120, 20], x_length=8, y_length=4.4,
                  axis_config={"color": MUTED, "include_tip": False, "font_size": 22},
                  y_axis_config={"numbers_to_include": [0, 40, 80, 120]}, x_axis_config={"include_ticks": False}).shift(DOWN * 0.5 + RIGHT * 0.5)
        yl = T("中位生存期（月）", 22, MUTED).rotate(PI / 2).next_to(ax.y_axis, LEFT, buff=0.35)
        xl = T("35 个基因中发生改变的个数", 22, MUTED).next_to(ax.x_axis, DOWN, buff=0.7)
        data = [("0 个", 28.41, MUTED), ("1 个", 59.31, BLUE), ("2 个", 66.41, BLUE), ("≥3 个", 104.65, GREEN)]

        def bar(i, h, c, lab):
            x = 0.5 + i
            r = Rectangle(width=1.2, height=ax.c2p(0, h)[1] - ax.c2p(0, 0)[1], fill_color=c, fill_opacity=0.9, stroke_width=0)
            r.move_to(ax.c2p(x, 0), aligned_edge=DOWN)
            v = T(f"{h:.2f}", 24, c).next_to(r, UP, buff=0.1)
            l = T(lab, 22, INK).next_to(ax.c2p(x, 0), DOWN, buff=0.2)
            return r, v, l
        bars = [bar(i, h, c, lab) for i, (lab, h, c) in enumerate(data)]
        with self.say("c3") as d:
            n = counter("膀胱癌样本", "411 例", INK).to_corner(UR, buff=0.5)
            self.play(Create(ax), FadeIn(yl), FadeIn(xl), FadeIn(n), run_time=1.2)
            self.play(Indicate(xl), run_time=1.0)
            self.play(Indicate(yl), run_time=1.0)
        with self.say("c3b") as d:
            r, v, l = bars[0]
            self.play(GrowFromEdge(r, DOWN), FadeIn(l), run_time=0.9)
            self.play(FadeIn(v), run_time=0.4)
        with self.say("c4") as d:
            for r, v, l in bars[1:]:
                self.play(GrowFromEdge(r, DOWN), FadeIn(l), run_time=0.8)
                self.play(FadeIn(v), run_time=0.3)
        with self.say("c5") as d:
            w = T("相关 ≠ 因果", 40, RED, weight=BOLD).move_to(ax.c2p(1.3, 100))
            bgw = BackgroundRectangle(w, color=BG, fill_opacity=0.9, buff=0.15)
            self.play(FadeIn(bgw), Write(w), run_time=1.2)
        self.clear()

    # ------------------------------------------------------------------ experiments
    def experiments(self):
        tag = self.chapter("三  临床与实验证据")
        genes = ["RPS6KA3", "FGFR3", "CDH2", "EP300", "FN1", "caspase-1"]
        prol = ["down", "down", "down", "mix", "mix", "up"]
        migr = ["down", "down", "down", "down", "down", "up"]
        known = {"FGFR3", "EP300"}
        x_gene, x_p, x_m = -3.6, 0.6, 2.8
        ys = [1.9 - i * 0.78 for i in range(6)]
        head = VGroup(T("增殖", 28, MUTED).move_to([x_p, 2.75, 0]), T("迁移", 28, MUTED).move_to([x_m, 2.75, 0]))
        names = VGroup(*[T(g, 28, INK).move_to([x_gene, y, 0]) for g, y in zip(genes, ys)])

        def sym(kind, pos):
            if kind == "down":
                return Arrow(pos + UP * 0.28, pos + DOWN * 0.28, color=GREEN, buff=0, stroke_width=6, max_tip_length_to_length_ratio=0.45)
            if kind == "up":
                return Arrow(pos + DOWN * 0.28, pos + UP * 0.28, color=RED, buff=0, stroke_width=6, max_tip_length_to_length_ratio=0.45)
            return T("因细胞系而异", 22, GOLD).move_to(pos)
        P = [sym(k, np.array([x_p, y, 0])) for k, y in zip(prol, ys)]
        M = [sym(k, np.array([x_m, y, 0])) for k, y in zip(migr, ys)]
        with self.say("e0") as d:
            self.clip_on("yt_rnai_nature.mp4", "center", "视频：Nature Video · YouTube", start=70)
        self.clip_off()
        with self.say("e1") as d:
            self.play(FadeIn(tag), FadeIn(head), LaggedStart(*[FadeIn(n, shift=RIGHT * 0.2) for n in names], lag_ratio=0.15), run_time=d * 0.6)
        grid0 = list(self.mobjects)
        self.remove(*grid0)
        with self.say("e1b") as d:
            self.clip_on("yt_cancer_mitosis.mp4", "center", "视频：Garvan Institute of Medical Research · YouTube", start=4)
        self.clip_off()
        self.add(*grid0)
        with self.say("e2") as d:
            self.play(*[GrowArrow(P[i]) for i in range(3)], run_time=1.0)
            self.play(*[GrowArrow(M[i]) for i in range(5)], run_time=1.0)
        with self.say("e3") as d:
            grid = VGroup(head, names, *P[:3], *M[:5])
            self.play(grid.animate.set_opacity(0.25), run_time=0.5)
            t1 = Ellipse(width=1.9, height=1.4, color=RED, fill_opacity=0.5).move_to([-1.6, -0.4, 0])
            t2 = Ellipse(width=1.9, height=1.4, color=RED, fill_opacity=0.5).move_to([2.0, -0.4, 0])
            l1 = T("对照", 26, INK).next_to(t1, DOWN, buff=0.4)
            l2 = T("敲低 RPS6KA3", 26, INK).next_to(t2, DOWN, buff=0.4).align_to(l1, UP)
            self.play(GrowFromCenter(t1), GrowFromCenter(t2), FadeIn(l1), FadeIn(l2), run_time=1.0)
            self.play(t2.animate.scale(0.5), run_time=1.4)
            mouse = VGroup(t1, t2, l1, l2)
        with self.say("e4") as d:
            self.play(FadeOut(mouse), grid.animate.set_opacity(1), run_time=0.6)
            self.play(GrowArrow(P[5]), GrowArrow(M[5]), names[5].animate.set_color(RED), run_time=1.0)
            self.play(FadeIn(P[3]), FadeIn(P[4]), names[3].animate.set_color(GOLD), names[4].animate.set_color(GOLD), run_time=1.0)
        with self.say("e5") as d:
            tags = VGroup(*[T("已知驱动基因", 20, MUTED).next_to(names[genes.index(g)], LEFT, buff=0.25) for g in known])
            self.play(FadeIn(tags), run_time=0.8)
            self.wait(d * 0.2)
            verdict = T("候选靶点，不是疗法", 32, GOLD, weight=BOLD).to_edge(DOWN, buff=0.3)
            self.play(Write(verdict), run_time=1.2)
        self.clear()

    # ------------------------------------------------------------------ meaning & limits
    def meaning(self):
        tag = self.chapter("四  意义与局限")
        ax = Axes(x_range=[0, 10], y_range=[0, 3], x_length=11, y_length=3.6, axis_config={"stroke_opacity": 0}).shift(DOWN * 0.6)

        def U(x):
            return 1.5 - 0.9 * np.cos(2 * PI * (x - 2.2) / 5.6) + 0.04 * (x - 5) ** 2
        land = ax.plot(U, x_range=[0.3, 9.7], color=MUTED, stroke_width=4)
        xn, xc = 2.2, 7.8
        ball = Dot(ax.c2p(xn, U(xn)) + UP * 0.2, radius=0.2, color=BLUE)
        ln = T("正常状态", 24, BLUE).next_to(ax.c2p(xn, U(xn)), DOWN, buff=0.35)
        lc = T("癌变状态", 24, RED).next_to(ax.c2p(xc, U(xc)), DOWN, buff=0.35)
        with self.say("l1") as d:
            self.play(FadeIn(tag), Create(land), FadeIn(ln), FadeIn(lc), FadeIn(ball), run_time=1.2)
            path = ax.plot(U, x_range=[xn, xc]).shift(UP * 0.2)
            dl = T("驱动基因：推过去", 24, GOLD).move_to(ax.c2p(3.4, 3.1))
            self.play(FadeIn(dl), MoveAlongPath(ball, path), run_time=1.8)
            self.play(ball.animate.set_color(RED), run_time=0.4)
            walls = VGroup(*[Line(ax.c2p(xc + s, U(xc + s)), ax.c2p(xc + s, U(xc + s)) + UP * 1.0, color=RED, stroke_width=6) for s in (-1.3, 1.3)])
            kl = T("维持基因：把它留在这里", 24, RED).next_to(walls, UP, buff=0.2)
            self.play(Create(walls), FadeIn(kl), run_time=1.0)
        with self.say("l2") as d:
            self.play(*[FadeOut(m) for m in (land, ln, lc, ball, dl, walls, kl)], run_time=0.6)
            fun = VGroup()
            for i, (k, c, w) in enumerate(((7030, MUTED, 9), (5052, VIOLET, 6.5), (660, RED, 1.6))):
                r = RoundedRectangle(corner_radius=0.15, width=w, height=0.8, fill_color=c, fill_opacity=0.35, stroke_color=c)
                r.add(T(str(k), 30, INK, weight=BOLD).move_to(r))
                fun.add(r)
            fun.arrange(DOWN, buff=0.35)
            names = VGroup(T("全部基因", 22, MUTED), T("所有驱动基因", 22, VIOLET), T("维持基因", 22, RED))
            for nm, r in zip(names, fun):
                nm.next_to(r, LEFT, buff=0.3)
            names.shift(LEFT * 0.0)
            for nm, r in zip(names, fun):
                self.play(FadeIn(r, shift=DOWN * 0.2), FadeIn(nm), run_time=0.7)
        with self.say("l3") as d:
            self.play(FadeOut(fun), FadeOut(names), run_time=0.6)
            G, net = self.demo(box=(-4.0, 4.0, -3.0, 2.6))
            self.play(FadeIn(net.group), run_time=0.8)
            ghost = [e for i, e in enumerate(net.edges.values()) if i % 4 == 1]
            self.play(*[e.animate.set_color(GOLD).set_stroke(opacity=1, width=4) for e in ghost], run_time=0.8)
            gl = T("在膀胱癌里可能不存在的边", 24, GOLD).to_edge(DOWN, buff=0.3)
            self.play(FadeIn(gl), *[e.animate.set_stroke(opacity=0.25) for e in ghost], run_time=1.0)
        with self.say("l4") as d:
            self.play(FadeOut(gl), net.group.animate.scale(0.6).shift(DOWN * 0.9), run_time=0.8)
            layers = VGroup()
            for i, (s, c) in enumerate((("基因表达", BLUE), ("表观修饰", VIOLET), ("肿瘤微环境", GREEN))):
                p = Polygon([-3.2, 0, 0], [2.2, 0, 0], [3.2, 0.7, 0], [-2.2, 0.7, 0], color=c, fill_opacity=0.12, stroke_width=2)
                p.add(T(s, 22, c).move_to(p))
                p.move_to([0, 1.0 + i * 0.85, 0])
                layers.add(p)
            self.play(LaggedStart(*[FadeIn(l, shift=DOWN * 0.2) for l in layers], lag_ratio=0.3), run_time=1.4)
            miss = T("尚未纳入", 26, MUTED).next_to(layers, RIGHT, buff=0.3)
            self.play(layers.animate.set_opacity(0.3), FadeIn(miss), run_time=0.8)
        with self.say("l5") as d:
            self.play(FadeOut(layers), FadeOut(miss), FadeOut(net.group), run_time=0.6)
            land2 = ax.plot(U, x_range=[0.3, 9.7], color=MUTED, stroke_width=4)
            ball2 = Dot(ax.c2p(xc, U(xc)) + UP * 0.2, radius=0.2, color=RED)
            self.play(Create(land2), FadeIn(ball2), run_time=0.8)
            q = T("扰动维持基因 → 离开癌变状态", 30, GOLD).move_to(UP * 2.4)
            back = ax.plot(U, x_range=[xc - 1.8, xc]).shift(UP * 0.2).reverse_points()
            self.play(FadeIn(q), run_time=0.6)
            self.play(MoveAlongPath(ball2, back), run_time=1.0, rate_func=there_and_back)
            hyp = T("模型推论，待机制研究检验", 24, MUTED).next_to(q, DOWN, buff=0.25)
            self.play(FadeIn(hyp), run_time=0.6)
        self.wait(0.8)
        self.clear(1.0)

    # ------------------------------------------------------------------ recap
    def recap(self):
        head, items = slide("小结", ["控制枢纽：所有方案中都在路径中间", "膀胱癌网络：660 个维持基因，173 个敏感", "证据有正有负：仍是候选靶点"], accent=RED)
        with self.say("r0") as d:
            self.play(FadeIn(head, shift=RIGHT * 0.3), run_time=0.6)
        for k, it in zip(("r1", "r2", "r3"), items):
            with self.say(k) as d:
                self.play(FadeIn(it, shift=RIGHT * 0.3), run_time=0.6)
        self.wait(0.6)
        self.play(FadeOut(head), FadeOut(items), run_time=0.6)
        with self.say("r4") as d:
            self.clip_on("matching_density.mp4", "full", "本站交互演示：驱动节点", start=0.3)
        self.wait(max(0.05, 14.0 - (self.renderer.time - self._clip['t0'])))
        self.clip_off()
        self.wait(1.0)
