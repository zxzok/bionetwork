"""Animated explainer: 疾病模块、网络邻近度与药物重定位."""
import random

import networkx as nx
import numpy as np

from common import *  # noqa: F401,F403
from kit_c import NetView, arrow, axes, callout, chip, clip_line, counter, fade_all, fit, grow_bars, hist_bars, parts, sf_graph, xlabel, ylabel

TITLE = "网络上的疾病与药物：疾病模块、邻近度与药物重定位"

LINES = {
    # hook
    "h1": "哮喘，是一种气道的疾病。",
    "h1b": "乳糜泻，是一种小肠的疾病。",
    "h2": "一个在呼吸道，一个在肠道，表现很不一样。可在大规模医保数据里，两者常常一起出现，这叫共病。",
    "h3": "线索在蛋白质相互作用网络里。所有已知的蛋白质相互作用合在一起，叫相互作用组。",
    "h4": "把两种病的相关基因标上去：蓝色是哮喘，黄色是乳糜泻，绿色是共有的。两片区域重叠在一起。",
    "h5": "【慢】疾病可以看作网络上一块局部的扰动；药物，也可以顺着网络找到新用途。",
    "q0": "这一期分三部分。",
    "q1": "第一部分，疾病模块：疾病基因在网络上怎样聚集。",
    "q2": "第二部分，网络邻近度：药物离疾病有多近。",
    "q3": "第三部分，验证：从网络预测，走到临床证据。",
    # disease module
    "k1": "先看第一部分。网络医学的一条基本假设：同一疾病的相关基因，倾向于聚在网络的同一片邻域。",
    "k2": "检验方法：标出疾病基因，看它们彼此相连的最大一团有多大，叫最大连通分支。这里是十四个里的十一个。",
    "k3": "再随机抽同样多的基因，每个基因的连接数和原来相近，这叫度匹配。紫色是一次随机抽样。",
    "k3b": "重复四百次，灰色柱子是随机情况下最大分支的分布。黄线是真实值，远在右边。",
    "k4": "2015年的一项研究分析了二百九十九种疾病，其中二百二十六种的基因显著聚集。",
    "k5": "比如多发性硬化：六十九个相关基因，只有十一个连成一片，可随机期望只有大约两个。",
    "k6": "【慢】互作组并不完整，可观测的模块，平均只包含约两成的已知疾病基因。",
    # separation
    "s1": "有了疾病模块，就能衡量两种疾病在网络上离得多远。蓝色和红色是两个模块。",
    "s2": "这个指标叫分离度，公式在右上角。",
    "s2b": "第一项是两组基因之间的平均最短距离；减去的第二项，是两个模块各自内部距离的平均。",
    "s2c": "也就是说，它比较的是组间距离比组内距离大多少。蓝红这一对是正的，两个模块分开。",
    "s3": "换成黄色模块，分离度是负的，两个模块重叠。这样的疾病对，只占约百分之七。",
    "s4": "【慢】模块重叠的疾病，症状更相似，共病风险也更高。哮喘和乳糜泻就是这样一对。",
    # proximity
    "d1": "下面进入第二部分。药物通过它结合的蛋白质，也就是靶点，接入同一张网络。",
    "d2": "对每个靶点，找离它最近的疾病基因，数最短路径有几步。这里每个都是一步。",
    "d3": "把这些步数取平均，就是药物和疾病模块之间的距离。",
    "d3b": "公式里，T是靶点集合，S是疾病基因集合：每个靶点取最近距离，再求平均。",
    "d4": "陷阱在这里：枢纽蛋白离谁都只有一两步。红色这个靶向枢纽的药物，距离同样很小。",
    "d5": "所以要和度匹配的随机靶点比。左边是靶向模块邻域的药物，右边是靶向枢纽的药物，灰色是随机的距离分布。",
    "d5b": "Z分数是真实距离减随机平均，再除以随机的标准差。左边约负一点九，右边约负零点七。",
    "d5c": "【慢】Z分数明显为负，才说明药物特异地靠近疾病模块。",
    # neighbourhood & combinations
    "n1": "用已知药物检验，有疗效的药物，靶点往往不在模块内部，而在模块的邻域。",
    "n2": "这个思路可以推广到两种药物的组合。",
    "n3": "六种网络构型里，只有一种和疗效相关：两药都命中疾病模块，却作用在不同邻域，叫互补暴露。",
    "n4": "两药各自覆盖一部分，合起来覆盖更多；靶点重叠的话，第二种药的增量就有限。",
    # validation
    "c1": "最后是第三部分。2018年的一项研究，用邻近度给九百多种已上市药物打分，得到数百个新的药物疾病关联。",
    "c2": "研究者挑出四个和冠心病相关的预测，在两亿两千万以上患者的医保数据里检验。",
    "c3": "两个得到支持：卡马西平和冠心病风险升高相关，羟氯喹和风险降低相关。",
    "c4": "体外实验又为后者提供了机制支持。网络预测、人群数据、机制实验，每一环都不能替代另一环。",
    # covid
    "v0": "再看一个例子。新冠病毒进入细胞以后，它的蛋白质会和许多人类蛋白质结合。",
    "v1": "2020年，研究者鉴定出新冠病毒蛋白结合的三百三十二个人类宿主蛋白，就是红色这些。",
    "v2": "另一项研究以它们为起点，用人工智能、网络扩散、邻近度三类算法，给六千多种药物打分。",
    "v3": "单一算法不稳定，把多条预测流程整合起来，排序更稳健。",
    "v4": "实验中有效的药物，大多不直接结合宿主靶点，而是作用在它们的网络邻域，就是绿色这些。",
    "v5": "【慢】但在细胞里抑制病毒，离临床有效还很远。大型随机对照试验中，羟氯喹没有降低住院患者的死亡率。",
    # recap
    "r1": "好，我们总结一下。",
    "r2": "第一，疾病基因在互作组中聚成模块，检验时要和度匹配的随机基因比。",
    "r3": "第二，网络邻近度用Z分数，衡量药物靶点是否特异地靠近疾病模块。",
    "r4": "第三，网络预测只是候选清单，要靠人群数据、实验，最终靠随机对照试验检验。",
    "r5": "这个专题的知识页面里有这个交互演示：点击节点放置药物靶点，页面会算出最近距离和Z分数。",
}


# ----------------------------------------------------------------------------- network & sets
def build():
    G = sf_graph(220, 2.3, seed=44, kmax=28)
    D = dict(nx.all_pairs_shortest_path_length(G))
    rng = random.Random(3)

    def module(seed_node, k, p_conn=0.65, exclude=()):
        """Grow a module: mostly by attaching neighbours of current members, sometimes a node two steps away."""
        S = [seed_node]
        while len(S) < k:
            if rng.random() < p_conn:
                cand = [w for v in S for w in G.neighbors(v) if w not in S and w not in exclude and G.degree(w) <= 10]
            else:
                cand = [w for v in S for w, dd in nx.single_source_shortest_path_length(G, v, cutoff=2).items()
                        if dd == 2 and w not in S and w not in exclude and G.degree(w) <= 10]
            if cand:
                S.append(rng.choice(sorted(set(cand))))
        return S
    deg = dict(G.degree())
    mids = [v for v in G if 3 <= deg[v] <= 6]
    a0 = mids[5]
    A = module(a0, 14)
    # B overlaps A: seeded at a neighbour of A
    nb = [v for v in G.neighbors(a0) if deg[v] <= 8]
    b0 = nb[0] if nb else a0
    B = A[:6] + [v for v in module(A[2], 12, exclude=set(A[6:])) if v not in A][:8]
    far = max(mids, key=lambda v: D[a0].get(v, 0))
    C = module(far, 12, p_conn=0.9)
    return G, D, A, B, C


def lcc(G, S):
    H = G.subgraph(S)
    return max((len(c) for c in nx.connected_components(H)), default=0)


def deg_matched(G, S, rng):
    deg = dict(G.degree())
    bins = {}
    for v in G:
        bins.setdefault(min(deg[v], 12), []).append(v)
    out = set()
    for s in S:
        pool = [v for v in bins[min(deg[s], 12)] if v not in out]
        out.add(rng.choice(pool))
    return list(out)


def closest(D, T, S):
    return np.mean([min(D[t].get(s, 99) for s in S) for t in T])


def inner(D, S):
    return np.mean([min(D[s].get(x, 99) for x in S if x != s) for s in S])


def sep(D, A, B):
    dab = np.mean([min(D[a].get(b, 99) for b in B) for a in A] + [min(D[b].get(a, 99) for a in A) for b in B])
    return dab - (inner(D, A) + inner(D, B)) / 2


class Episode(Narrated):
    LINES = LINES

    def construct(self):
        self.G, self.D, self.A, self.B, self.C = build()
        self.pos = fit(nx.kamada_kawai_layout(self.G), (-6.4, 0.2, -3.3, 3.0))
        self.hook()
        self.questions()
        self.modules()
        self.separation()
        self.proximity()
        self.neighbourhood()
        self.validation()
        self.covid()
        self.recap()

    def net(self, **kw):
        kw.setdefault("color", MUTED); kw.setdefault("eo", 0.3); kw.setdefault("rmin", 0.04); kw.setdefault("rk", 0.016)
        return NetView(self.G, self.pos, **kw)

    def blob(self, S, color):
        """Soft halo around a gene set: union of translucent discs."""
        return VGroup(*[Circle(radius=0.32, stroke_width=0, fill_color=color, fill_opacity=0.16).move_to(self.pos[v]) for v in S]).set_z_index(-2)

    # ------------------------------------------------------------------ hook
    def hook(self):
        a = chip("哮喘", BLUE, 34).move_to(LEFT * 4.0 + UP * 0.8)
        b = chip("乳糜泻", GOLD, 34).move_to(RIGHT * 4.0 + UP * 0.8)
        al, bl = T("呼吸道", 24, MUTED).next_to(a, DOWN, buff=0.25), T("肠道", 24, MUTED).next_to(b, DOWN, buff=0.25)
        clip_line(self, "h1", "yt_asthma_ala.mp4", "视频：American Lung Association · YouTube", start=25, min_len=5)
        clip_line(self, "h1b", "yt_celiac_niddk.mp4", "视频：NIDDK · YouTube", start=40, min_len=5)
        with self.say("h2") as d:
            self.play(FadeIn(a, shift=RIGHT * 0.3), FadeIn(al), FadeIn(b, shift=LEFT * 0.3), FadeIn(bl), run_time=0.9)
            people = VGroup(*[Dot(radius=0.07, color=MUTED).set_opacity(0.6) for _ in range(120)]).arrange_in_grid(6, 20, buff=0.12).move_to(DOWN * 2.0)
            self.play(FadeIn(people, lag_ratio=0.005), run_time=1.0)
            rng = np.random.default_rng(1)
            both = rng.choice(120, 9, replace=False)
            link = DashedLine(a.get_right(), b.get_left(), color=RED, stroke_width=4)
            cl = T("共病", 26, RED).next_to(link, UP, buff=0.15)
            self.play(*[people[i].animate.set_color(RED).set_opacity(1).scale(1.4) for i in both], Create(link), FadeIn(cl), run_time=1.2)
        net = self.net()
        with self.say("h3") as d:
            self.play(FadeOut(people), FadeOut(link), FadeOut(cl), FadeOut(al), FadeOut(bl),
                      a.animate.scale(0.7).move_to(RIGHT * 3.4 + UP * 1.2), b.animate.scale(0.7).move_to(RIGHT * 3.4 + DOWN * 0.2), run_time=1.0)
            self.play(LaggedStart(*[GrowFromCenter(x) for x in net.dots.values()], lag_ratio=0.004),
                      LaggedStart(*[Create(e) for e in net.edges.values()], lag_ratio=0.002), run_time=d * 0.6)
        with self.say("h4") as d:
            self.play(*[net.dots[v].animate.set_color(BLUE).scale(1.6) for v in self.A if v not in self.B], run_time=0.9)
            self.play(*[net.dots[v].animate.set_color(GOLD).scale(1.6) for v in self.B if v not in self.A],
                      *[net.dots[v].animate.set_color(GREEN).scale(1.6) for v in self.B if v in self.A], run_time=0.9)
            ba, bb = self.blob(self.A, BLUE), self.blob(self.B, GOLD)
            self.play(FadeIn(ba), FadeIn(bb), run_time=1.0)
        with self.say("h5") as d:
            self.play(net.group.animate.fade(0.8), ba.animate.fade(0.8), bb.animate.fade(0.8), FadeOut(a), FadeOut(b), run_time=0.8)
            q = T("疾病 = 网络上的局部扰动", 46, GOLD, weight=BOLD)
            self.play(Write(q), run_time=1.2)
        fade_all(self)

    def questions(self):
        parts(self, "这一期分三部分", ["一  疾病模块", "二  网络邻近度与药物", "三  从预测到验证"], ["q0", "q1", "q2", "q3"])

    # ------------------------------------------------------------------ disease modules
    def modules(self):
        tag = self.chapter("一  疾病模块")
        G, A = self.G, self.A
        net = self.net()
        with self.say("k1") as d:
            self.play(FadeIn(tag), FadeIn(net.group), run_time=1.0)
            self.play(*[net.dots[v].animate.set_color(BLUE).scale(1.6) for v in A], run_time=1.0)
            blob = self.blob(A, BLUE)
            self.play(FadeIn(blob), run_time=1.0)
        L = lcc(G, A)
        comp = max(nx.connected_components(G.subgraph(A)), key=len)
        with self.say("k2") as d:
            self.play(FadeOut(blob), run_time=0.4)
            self.play(*[e.animate.set_stroke(BLUE, width=4, opacity=1) for (u, v), e in net.edges.items() if u in comp and v in comp],
                      *[net.dots[v].animate.set_color(GOLD) for v in comp], run_time=1.2)
            c = counter("最大连通分支", f"{L} / {len(A)}", GOLD).move_to(RIGHT * 3.6 + UP * 2.3)
            self.play(FadeIn(c), run_time=0.6)
        rng = random.Random(5)
        rand = [lcc(G, deg_matched(G, A, rng)) for _ in range(400)]
        print("LCC", L, np.mean(rand), np.std(rand))
        ax = axes([0, 14, 2], [0, 160, 40], 5.4, 3.2, xnums=[0, 4, 8, 12], fs=20).move_to(RIGHT * 3.6 + DOWN * 1.2)
        xl = xlabel(ax, "随机基因集的最大分支", 20, 0.3)
        bars, _ = hist_bars(ax, rand, np.arange(-0.5, 14.5, 1), MUTED)
        with self.say("k3") as d:
            # show one random draw on the network
            S = deg_matched(G, A, random.Random(9))
            self.play(*[net.dots[v].animate.set_color(MUTED) for v in A],
                      *[e.animate.set_stroke(MUTED, width=1.4, opacity=0.3) for e in net.edges.values()],
                      *[net.dots[v].animate.set_color(VIOLET) for v in S], run_time=1.0)
        with self.say("k3b") as d:
            self.play(Create(ax), FadeIn(xl), run_time=0.7)
            self.play(grow_bars(bars, d * 0.35))
            rl = Line(ax.c2p(L, 0), ax.c2p(L, 150), color=GOLD, stroke_width=5)
            self.play(Create(rl), *[net.dots[v].animate.set_color(MUTED) for v in S], *[net.dots[v].animate.set_color(GOLD) for v in comp], run_time=0.8)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.6)
        with self.say("k4") as d:
            dots = VGroup(*[Dot(radius=0.075, color=MUTED) for _ in range(299)]).arrange_in_grid(13, 23, buff=0.12).move_to(LEFT * 2.2 + DOWN * 0.2)
            self.play(FadeIn(dots, lag_ratio=0.003), run_time=1.2)
            self.play(LaggedStart(*[dots[i].animate.set_color(BLUE) for i in range(226)], lag_ratio=0.003), run_time=1.4)
            c1 = counter("疾病", "299", INK).move_to(RIGHT * 4.4 + UP * 1.2)
            c2 = counter("基因显著聚集", "226", BLUE).move_to(RIGHT * 4.4 + DOWN * 0.6)
            self.play(FadeIn(c1), FadeIn(c2), run_time=0.7)
        with self.say("k5") as d:
            self.play(FadeOut(dots), FadeOut(c1), FadeOut(c2), run_time=0.5)
            ttl = T("多发性硬化", 32, INK, weight=BOLD).move_to(UP * 2.4)
            ax2 = axes([0, 3, 1], [0, 70, 20], 6.0, 3.6, ynums=[0, 20, 40, 60]).move_to(DOWN * 0.4)
            u = ax2.c2p(0, 1)[1] - ax2.c2p(0, 0)[1]
            vals = [(69, MUTED, "相关基因"), (11, GOLD, "连成一片"), (2, VIOLET, "随机期望")]
            bs = VGroup(*[Rectangle(width=1.1, height=u * v, stroke_width=0, fill_color=c, fill_opacity=0.9).move_to(ax2.c2p(i + 0.5, 0), aligned_edge=DOWN) for i, (v, c, _) in enumerate(vals)])
            ls = VGroup(*[T(s, 22, MUTED).next_to(ax2.c2p(i + 0.5, 0), DOWN, buff=0.15) for i, (_, _, s) in enumerate(vals)])
            vs = VGroup(*[T(("约 " if i == 2 else "") + str(v), 28, c, weight=BOLD).next_to(b, UP, buff=0.1) for i, ((v, c, _), b) in enumerate(zip(vals, bs))])
            self.play(FadeIn(ttl), Create(ax2), FadeIn(ls), run_time=0.8)
            self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bs], lag_ratio=0.4), LaggedStart(*[FadeIn(v) for v in vs], lag_ratio=0.4), run_time=d * 0.5)
        with self.say("k6") as d:
            self.play(*[FadeOut(m) for m in (ttl, ax2, bs, ls, vs)], run_time=0.5)
            full = Circle(radius=2.2, color=BLUE, stroke_width=3, fill_opacity=0.08).move_to(LEFT * 1.5 + DOWN * 0.2)
            seen = Sector(radius=2.2, angle=0.2 * TAU, color=BLUE, fill_opacity=0.6).move_to(full.get_center(), aligned_edge=ORIGIN)
            seen.move_arc_center_to(full.get_center())
            fl = T("已知疾病基因", 24, BLUE).next_to(full, DOWN, buff=0.2)
            sl = T("可观测的模块：约 20%", 28, BLUE, weight=BOLD).move_to(RIGHT * 3.6 + UP * 0.4)
            self.play(Create(full), FadeIn(fl), run_time=0.8)
            self.play(FadeIn(seen), FadeIn(sl), run_time=1.0)
        fade_all(self)

    # ------------------------------------------------------------------ separation
    def separation(self):
        tag = self.chapter("一  网络分离度")
        D, A, B, C = self.D, self.A, self.B, self.C
        net = self.net()
        s_ab, s_ac = sep(D, A, B), sep(D, A, C)
        print("SEP", s_ab, s_ac)
        with self.say("s1") as d:
            self.play(FadeIn(tag), FadeIn(net.group), run_time=1.0)
            self.play(*[net.dots[v].animate.set_color(BLUE).scale(1.5) for v in A],
                      *[net.dots[v].animate.set_color(RED).scale(1.5) for v in C], run_time=1.0)
            ba, bc = self.blob(A, BLUE), self.blob(C, RED)
            self.play(FadeIn(ba), FadeIn(bc), run_time=0.8)
        f = MathTex(r"s_{AB}=\langle d_{AB}\rangle-\frac{\langle d_{AA}\rangle+\langle d_{BB}\rangle}{2}", font_size=34, color=INK).move_to(RIGHT * 3.5 + UP * 2.4)
        with self.say("s2") as d:
            self.play(Write(f), run_time=d * 0.5)
        with self.say("s2b") as d:
            t1 = callout(f[0][4:9], "组间距离", DOWN, BLUE, 18, 0.08)
            t2 = callout(f[0][10:23], "组内距离的平均", DOWN, GOLD, 18, 0.08)
            self.play(Create(t1), run_time=0.8)
            self.play(Create(t2), run_time=0.8)
        with self.say("s2c") as d:
            self.play(FadeOut(t1), FadeOut(t2), run_time=0.4)
            v1 = VGroup(MathTex(rf"s = {s_ac:+.2f}", font_size=40, color=RED), T("两个模块分开", 22, RED)).arrange(DOWN, buff=0.12).move_to(RIGHT * 3.6 + UP * 0.6)
            self.play(FadeIn(v1), run_time=0.7)
        with self.say("s3") as d:
            self.play(FadeOut(bc), *[net.dots[v].animate.set_color(MUTED).scale(1 / 1.5) for v in C], run_time=0.6)
            self.play(*[net.dots[v].animate.set_color(GOLD if v not in A else GREEN).scale(1.5 if v not in A else 1.0) for v in B], run_time=0.8)
            bb = self.blob(B, GOLD)
            self.play(FadeIn(bb), run_time=0.7)
            v2 = VGroup(MathTex(rf"s = {s_ab:+.2f}", font_size=40, color=GOLD), T("两个模块重叠", 22, GOLD)).arrange(DOWN, buff=0.12).move_to(RIGHT * 3.6 + DOWN * 0.9)
            self.play(FadeIn(v2), run_time=0.6)
            pct = T("s < 0 的疾病对：约 7%", 24, MUTED).move_to(RIGHT * 3.6 + DOWN * 2.3)
            self.play(FadeIn(pct), run_time=0.5)
        with self.say("s4") as d:
            la, lb = chip("哮喘", BLUE, 24).next_to(ba, LEFT, buff=0.1).shift(UP * 0.6), chip("乳糜泻", GOLD, 24).next_to(bb, DOWN, buff=0.1)
            for c_ in (la, lb):
                if c_.get_left()[0] < -6.9:
                    c_.shift(RIGHT * (-6.9 - c_.get_left()[0]))
            self.play(FadeIn(la), FadeIn(lb), run_time=0.8)
            sym = VGroup(chip("症状更相似", INK, 24), chip("共病风险更高", RED, 24)).arrange(DOWN, buff=0.25).move_to(RIGHT * 3.6 + DOWN * 2.3)
            self.play(FadeOut(pct), FadeIn(sym, shift=UP * 0.2), run_time=0.8)
        fade_all(self)

    # ------------------------------------------------------------------ proximity
    def proximity(self):
        tag = self.chapter("二  网络邻近度")
        G, D, A = self.G, self.D, self.A
        net = self.net()
        Aset = set(A)
        ring1 = [v for v in G if v not in Aset and min(D[v].get(a, 99) for a in A) == 1 and G.degree(v) <= 5]
        rng = random.Random(2)
        T1 = rng.sample(ring1, 3)
        hubs = sorted(G, key=G.degree, reverse=True)
        T2 = [h for h in hubs if h not in Aset][:3]

        def zscore(T, reps=400, seed=1):
            r = random.Random(seed)
            obs = closest(D, T, A)
            null = [closest(D, deg_matched(G, T, r), deg_matched(G, A, r)) for _ in range(reps)]
            return obs, np.mean(null), np.std(null), null
        o1, m1, s1, n1 = zscore(T1)
        o2, m2, s2, n2 = zscore(T2)
        z1, z2 = (o1 - m1) / s1, (o2 - m2) / s2
        print("PROX", o1, m1, s1, z1, "|", o2, m2, s2, z2)
        pill = VGroup(RoundedRectangle(corner_radius=0.25, width=1.2, height=0.5, color=GREEN, fill_opacity=0.6, stroke_width=2),
                      T("药物", 20)).move_to(RIGHT * 3.0 + UP * 2.4)
        with self.say("d1") as d:
            self.play(FadeIn(tag), FadeIn(net.group), *[net.dots[v].animate.set_color(BLUE).scale(1.5) for v in A], run_time=1.2)
            self.play(FadeIn(pill), run_time=0.5)
            links = VGroup(*[DashedLine(pill.get_left(), self.pos[t], color=GREEN, stroke_width=2) for t in T1])
            self.play(Create(links), *[net.dots[t].animate.set_color(GREEN).scale(1.8) for t in T1], run_time=1.2)
        with self.say("d2") as d:
            self.play(FadeOut(links), run_time=0.4)
            labels = VGroup()
            for t in T1:
                s = min(A, key=lambda a: D[t].get(a, 99))
                path = nx.shortest_path(G, t, s)
                pl = VGroup(*[Line(self.pos[x], self.pos[y], color=GREEN, stroke_width=5) for x, y in zip(path, path[1:])])
                n_ = T(str(len(path) - 1), 24, GREEN, weight=BOLD).next_to(net.dots[t], UP, buff=0.08)
                self.play(Create(pl), FadeIn(n_), run_time=0.7)
                labels.add(pl, n_)
        with self.say("d3") as d:
            f = MathTex(r"d_c=\frac{1}{|T|}\sum_{t\in T}\min_{s\in S} d(s,t)", font_size=40, color=INK).move_to(RIGHT * 3.6 + UP * 1.0)
            self.play(Write(f), run_time=d * 0.35)
            v = MathTex(rf"d_c = {o1:.2f}", font_size=40, color=GREEN).next_to(f, DOWN, buff=0.35)
            self.play(FadeIn(v), run_time=0.6)
        with self.say("d3b") as d:
            c1_ = callout(f[0][3:12], "对所有靶点求平均", UP, GOLD, 18, 0.08)
            c2_ = callout(f[0][-12:], "最近距离", UP, GREEN, 18, 0.08)
            self.play(Create(c1_), run_time=0.8)
            self.play(Create(c2_), run_time=0.8)
        with self.say("d4") as d:
            self.play(FadeOut(c1_), FadeOut(c2_), run_time=0.4)
            self.play(FadeOut(labels), FadeOut(pill), *[net.dots[t].animate.set_color(MUTED).scale(1 / 1.8) for t in T1], run_time=0.6)
            pill2 = VGroup(RoundedRectangle(corner_radius=0.25, width=1.6, height=0.5, color=RED, fill_opacity=0.6, stroke_width=2),
                           T("枢纽药物", 20)).move_to(RIGHT * 3.0 + UP * 2.6)
            self.play(FadeIn(pill2), *[net.dots[t].animate.set_color(RED).scale(1.4) for t in T2], run_time=0.8)
            spokes = VGroup(*[Line(self.pos[h], self.pos[w], color=RED, stroke_width=2, stroke_opacity=0.8) for h in T2 for w in G.neighbors(h)])
            self.play(Create(spokes), run_time=1.0)
            v2 = MathTex(rf"d_c = {o2:.2f}", font_size=40, color=RED).next_to(v, DOWN, buff=0.3)
            self.play(FadeIn(v2), run_time=0.6)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.6)
        lo, hi = 0.0, 3.0
        edges = np.linspace(lo, hi, 25)
        ymax = int(np.ceil(max(np.histogram(n1, edges)[0].max(), np.histogram(n2, edges)[0].max()) / 50.0) * 50)
        axl = axes([lo, hi, 1], [0, ymax, ymax / 2], 5.4, 3.0, xnums=[0, 1, 2, 3], fs=20).move_to(LEFT * 3.4 + DOWN * 0.9)
        axr = axes([lo, hi, 1], [0, ymax, ymax / 2], 5.4, 3.0, xnums=[0, 1, 2, 3], fs=20).move_to(RIGHT * 3.4 + DOWN * 0.9)
        bl, _ = hist_bars(axl, n1, edges, MUTED)
        br, _ = hist_bars(axr, n2, edges, MUTED)
        hl = T("靶向模块邻域的药物", 24, GREEN).next_to(axl, UP, buff=0.9)
        hr = T("靶向枢纽的药物", 24, RED).next_to(axr, UP, buff=0.9)
        xl1, xl2 = xlabel(axl, "距离（灰色为度匹配随机）", 20, 0.3), xlabel(axr, "距离（灰色为度匹配随机）", 20, 0.3)
        with self.say("d5") as d:
            self.play(Create(axl), Create(axr), FadeIn(hl), FadeIn(hr), FadeIn(xl1), FadeIn(xl2), run_time=0.8)
            self.play(grow_bars(bl, 1.0), grow_bars(br, 1.0))
            l1 = Line(axl.c2p(o1, 0), axl.c2p(o1, ymax), color=GREEN, stroke_width=5)
            l2 = Line(axr.c2p(o2, 0), axr.c2p(o2, ymax), color=RED, stroke_width=5)
            self.play(Create(l1), Create(l2), run_time=0.8)
        with self.say("d5b") as d:
            zl = MathTex(rf"z = {z1:.1f}", font_size=40, color=GREEN).next_to(hl, DOWN, buff=0.12)
            zr = MathTex(rf"z = {z2:.1f}", font_size=40, color=RED).next_to(hr, DOWN, buff=0.12)
            self.play(FadeIn(zl), FadeIn(zr), run_time=0.6)
        with self.say("d5c") as d:
            self.play(Indicate(zl, color=GREEN, scale_factor=1.3), run_time=1.0)
        fade_all(self)

    # ------------------------------------------------------------------ neighbourhood & combinations
    def neighbourhood(self):
        tag = self.chapter("二  药物与模块的邻域")
        rng = np.random.default_rng(4)
        c0 = LEFT * 2.0 + DOWN * 0.2
        mod = VGroup(*[Dot(c0 + 1.3 * np.sqrt(rng.random()) * np.array([np.cos(t), np.sin(t), 0]), radius=0.09, color=BLUE) for t in rng.uniform(0, TAU, 22)])
        outline = Circle(radius=1.55, color=BLUE, stroke_width=3, fill_opacity=0.08).move_to(c0)
        ml = T("疾病模块", 24, BLUE).next_to(outline, UP, buff=0.15)
        inside = Dot(c0 + RIGHT * 0.2, radius=0.16, color=MUTED)
        near = [c0 + 2.05 * np.array([np.cos(a), np.sin(a), 0]) for a in (0.3, 2.4, 4.3)]
        nd = VGroup(*[Dot(p, radius=0.16, color=GREEN) for p in near])
        with self.say("n1") as d:
            self.play(FadeIn(tag), Create(outline), FadeIn(mod), FadeIn(ml), run_time=1.0)
            x_in = VGroup(inside, T("模块内部", 20, MUTED).next_to(inside, DOWN, buff=0.1))
            self.play(FadeIn(x_in), run_time=0.6)
            self.play(LaggedStart(*[GrowFromCenter(x) for x in nd], lag_ratio=0.2), run_time=0.9)
            el = T("有效药物的靶点", 24, GREEN).move_to(RIGHT * 2.8 + UP * 1.8)
            arrs = VGroup(*[arrow(el.get_left(), p, GREEN, buff=0.25, sw=2) for p in near[:1]])
            self.play(FadeIn(el), GrowArrow(arrs[0]), run_time=0.8)
        with self.say("n2") as d:
            self.play(FadeOut(x_in), FadeOut(nd), FadeOut(el), FadeOut(arrs), run_time=0.5)
            pa = chip("药物 甲", GREEN, 24).move_to(RIGHT * 3.6 + UP * 1.6)
            pb = chip("药物 乙", GOLD, 24).move_to(RIGHT * 3.6 + DOWN * 1.6)
            self.play(FadeIn(pa), FadeIn(pb), run_time=0.8)
        def cover(center_ang, color, span=1.4):
            return AnnularSector(inner_radius=0.0, outer_radius=1.55, angle=span, start_angle=center_ang - span / 2, color=color, fill_opacity=0.35).move_arc_center_to(c0)
        with self.say("n3") as d:
            ca, cb = cover(0.6, GREEN), cover(0.6 + PI, GOLD)
            ta = VGroup(*[Dot(c0 + 1.85 * np.array([np.cos(a), np.sin(a), 0]), radius=0.13, color=GREEN) for a in (0.3, 0.9)])
            tb = VGroup(*[Dot(c0 + 1.85 * np.array([np.cos(a), np.sin(a), 0]), radius=0.13, color=GOLD) for a in (0.3 + PI, 0.9 + PI)])
            self.play(FadeIn(ta), FadeIn(ca), run_time=0.8)
            self.play(FadeIn(tb), FadeIn(cb), run_time=0.8)
            lab = T("互补暴露", 32, INK, weight=BOLD).move_to(RIGHT * 3.6 + UP * 0.0)
            self.play(Write(lab), run_time=0.8)
        with self.say("n4") as d:
            ok = T("覆盖更多", 24, GREEN).next_to(lab, DOWN, buff=0.2)
            self.play(FadeIn(ok), run_time=0.5)
            self.wait(0.6)
            cb2 = cover(1.0, GOLD)
            self.play(Transform(cb, cb2), tb.animate.shift(c0 * 0).rotate(PI, about_point=c0), FadeOut(ok), run_time=1.2)
            bad = T("重叠：增量有限", 24, RED).next_to(lab, DOWN, buff=0.2)
            self.play(FadeIn(bad), run_time=0.5)
        fade_all(self)

    # ------------------------------------------------------------------ validation chain
    def validation(self):
        tag = self.chapter("三  从预测到验证")
        stages = [("网络预测", GREEN), ("人群数据", BLUE), ("机制实验", VIOLET), ("随机对照试验", GOLD)]
        chips = VGroup(*[chip(s, c, 26) for s, c in stages]).arrange(RIGHT, buff=0.7).move_to(UP * 2.4)
        arrs = VGroup(*[arrow(chips[i].get_right(), chips[i + 1].get_left(), MUTED, buff=0.08) for i in range(3)])
        with self.say("c1") as d:
            self.play(FadeIn(tag), FadeIn(chips[0]), run_time=0.8)
            cnt = counter("已上市药物", "900+", GREEN).move_to(LEFT * 4.6 + DOWN * 0.6)
            dots = VGroup(*[Dot(radius=0.05, color=GREEN).set_opacity(0.7) for _ in range(300)]).arrange_in_grid(15, 20, buff=0.08).move_to(LEFT * 1.0 + DOWN * 0.6)
            self.play(FadeIn(cnt), FadeIn(dots, lag_ratio=0.003), run_time=d * 0.4)
        with self.say("c2") as d:
            self.play(GrowArrow(arrs[0]), FadeIn(chips[1]), run_time=0.8)
            sel = VGroup(*[dots[i] for i in (17, 88, 151, 230)])
            self.play(FadeOut(VGroup(*[x for x in dots if x not in sel])), sel.animate.arrange(RIGHT, buff=0.5).move_to(LEFT * 1.0 + DOWN * 0.6).scale(3), run_time=1.2)
            c2 = counter("冠心病相关预测", "4", BLUE).move_to(cnt)
            pts = counter("医保数据", "2.2 亿+ 患者", BLUE).move_to(RIGHT * 4.0 + DOWN * 0.6)
            self.play(Transform(cnt, c2), FadeIn(pts), run_time=0.8)
        with self.say("c3") as d:
            self.play(sel[0].animate.set_color(RED), sel[1].animate.set_color(GREEN), sel[2].animate.set_color(MUTED), sel[3].animate.set_color(MUTED), run_time=0.8)
            l1 = T("卡马西平：风险升高", 24, RED).next_to(sel[0], DOWN, buff=0.4).shift(LEFT * 0.8)
            l2 = T("羟氯喹：风险降低", 24, GREEN).next_to(sel[1], DOWN, buff=1.0).shift(RIGHT * 0.4)
            self.play(FadeIn(l1), run_time=0.6)
            self.play(FadeIn(l2), run_time=0.6)
            c3 = counter("得到支持", "2 / 4", INK).move_to(RIGHT * 4.0 + DOWN * 2.4)
            self.play(FadeIn(c3), run_time=0.5)
        with self.say("c4") as d:
            self.play(GrowArrow(arrs[1]), FadeIn(chips[2]), run_time=0.8)
            self.play(Indicate(sel[1], color=GREEN), run_time=0.8)
            self.play(GrowArrow(arrs[2]), FadeIn(chips[3]), run_time=0.8)
        fade_all(self)

    # ------------------------------------------------------------------ COVID-19
    def covid(self):
        clip_line(self, "v0", "yt_sarscov2_lifecycle_maastricht.mp4", "视频：Maastricht University · YouTube", start=60)
        tag = self.chapter("三  新冠药物重定位")
        G, D = self.G, self.D
        net = self.net()
        rng = random.Random(8)
        hosts = rng.sample([v for v in G if G.degree(v) <= 6], 18)
        virus = VGroup(Circle(radius=0.55, color=RED, fill_opacity=0.3, stroke_width=3),
                       *[Line(ORIGIN, 0.8 * np.array([np.cos(a), np.sin(a), 0]), color=RED, stroke_width=3).shift(0.55 * np.array([np.cos(a), np.sin(a), 0]) * 0) for a in np.linspace(0, TAU, 11)[:-1]])
        virus[0].set_z_index(1)
        virus.move_to(RIGHT * 3.6 + UP * 2.0)
        with self.say("v1") as d:
            self.play(FadeIn(tag), FadeIn(net.group), run_time=1.0)
            self.play(GrowFromCenter(virus), run_time=0.6)
            self.play(*[net.dots[h].animate.set_color(RED).scale(1.7) for h in hosts], run_time=1.0)
            c = counter("宿主蛋白", "332", RED).move_to(RIGHT * 3.6 + UP * 0.2)
            self.play(FadeIn(c), run_time=0.5)
        algs = VGroup(chip("人工智能", VIOLET, 24), chip("网络扩散", BLUE, 24), chip("邻近度", GREEN, 24)).arrange(DOWN, buff=0.25).move_to(RIGHT * 2.6 + DOWN * 1.6)
        with self.say("v2") as d:
            self.play(FadeOut(c), virus.animate.scale(0.6).move_to(RIGHT * 5.8 + UP * 2.6), run_time=0.6)
            drugs = counter("候选药物", "6000+", INK).move_to(RIGHT * 3.6 + UP * 1.2)
            self.play(FadeIn(drugs), run_time=0.6)
            self.play(LaggedStart(*[FadeIn(a, shift=RIGHT * 0.2) for a in algs], lag_ratio=0.3), run_time=1.2)
        with self.say("v3") as d:
            agg = chip("整合排序", GOLD, 26).move_to(RIGHT * 5.4 + DOWN * 1.6)
            ars = VGroup(*[arrow(a.get_right(), agg.get_left(), MUTED, buff=0.1, sw=2) for a in algs])
            self.play(*[Wiggle(a) for a in algs], run_time=1.0)
            self.play(LaggedStart(*[GrowArrow(a) for a in ars], lag_ratio=0.2), FadeIn(agg), run_time=1.0)
        hs = set(hosts)
        nbr = [v for v in G if v not in hs and any(G.has_edge(v, h) for h in hosts)]
        eff = random.Random(4).sample(nbr, 6)
        with self.say("v4") as d:
            self.play(*[FadeOut(m) for m in (drugs, algs, ars, agg)], run_time=0.5)
            self.play(*[net.dots[v].animate.set_color(GREEN).scale(1.8) for v in eff], run_time=1.0)
            lk = VGroup(*[Line(self.pos[v], self.pos[h], color=GREEN, stroke_width=3) for v in eff for h in hosts if G.has_edge(v, h)])
            self.play(Create(lk), run_time=0.8)
            lg = VGroup(VGroup(Dot(radius=0.1, color=RED), T("宿主蛋白", 22)).arrange(RIGHT, buff=0.15),
                        VGroup(Dot(radius=0.1, color=GREEN), T("有效药物的靶点", 22)).arrange(RIGHT, buff=0.15)).arrange(DOWN, aligned_edge=LEFT).move_to(RIGHT * 3.8 + UP * 0.6)
            self.play(FadeIn(lg), run_time=0.5)
        with self.say("v5") as d:
            self.play(net.group.animate.fade(0.8), lk.animate.fade(0.8), FadeOut(lg), run_time=0.6)
            steps = VGroup(chip("细胞实验", GREEN, 26), chip("临床有效", GOLD, 26)).arrange(RIGHT, buff=2.4).move_to(RIGHT * 1.0 + UP * 0.6)
            gap = DashedLine(steps[0].get_right(), steps[1].get_left(), color=MUTED, stroke_width=3)
            gl = T("还很远", 22, MUTED).next_to(gap, UP, buff=0.1)
            self.play(FadeIn(steps[0]), Create(gap), FadeIn(gl), FadeIn(steps[1]), run_time=1.2)
            rct = VGroup(T("随机对照试验", 24, INK), T("羟氯喹未降低住院患者死亡率", 26, RED, weight=BOLD)).arrange(DOWN, buff=0.15).move_to(RIGHT * 1.0 + DOWN * 1.2)
            self.play(FadeIn(rct, shift=UP * 0.2), run_time=0.8)
        fade_all(self)

    # ------------------------------------------------------------------ recap
    def recap(self):
        with self.say("r1") as d:
            head = T("三个要点", 40, INK, weight=BOLD).to_edge(UP, buff=0.7)
            self.play(Write(head), run_time=0.8)
        items = [("r2", BLUE, "疾病模块：与度匹配随机基因比较"),
                 ("r3", GREEN, "邻近度：用 Z 分数衡量特异的靠近"),
                 ("r4", GOLD, "预测是候选清单，要逐级验证")]
        rows = VGroup()
        for i, (k, c, s) in enumerate(items):
            num = Circle(radius=0.32, color=c, fill_opacity=0.18, stroke_width=3).add(T(str(i + 1), 28, c, weight=BOLD))
            rows.add(VGroup(num, T(s, 30, INK)).arrange(RIGHT, buff=0.4))
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.55).next_to(head, DOWN, buff=0.7)
        for (k, _, _), row in zip(items, rows):
            with self.say(k) as d:
                self.play(FadeIn(row, shift=RIGHT * 0.3), run_time=0.8)
        self.wait(0.8)
        self.play(FadeOut(rows), FadeOut(head), run_time=0.6)
        with self.say("r5") as d:
            self.clip_on("proximity_demo.mp4", "full", "本站交互演示：网络邻近度", start=0.3)
            if d < 12.0:
                self.wait(12.0 - d)
        self.clip_off()
        self.wait(1.0)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=1.0)
