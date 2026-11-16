"""Paper explainer: finding all possible input nodes with one maximum matching (2017)."""
import itertools

import networkx as nx
import numpy as np

from common import *  # noqa: F401,F403
from paperkit import DiNet, arrow, counter, fit, max_matching, drivers, n_drivers, possible_inputs, sf_digraph

TITLE = "一次匹配，找出全部可能输入节点"

LINES = {
    # hook
    "h1": "我们先来想象一个任务：在一张四十多万个节点的网络里，找出所有有资格当输入节点的节点。输入节点，就是直接施加外部控制信号的节点。",
    "h2": "老办法是一个一个地检验：拿起一个节点，判断它能不能在另一种方案里成为输入节点，然后换下一个。黄框就在一格一格地往前走。",
    "h3": "这样算下来，要花十几个小时。",
    "h4": "而2017年发表的一项研究给出的算法，完成同样的任务，不到三秒。",
    "h5": "【慢】快了一万多倍。这一期，我们就来看它是怎么做到的。",
    "q0": "这一期分三部分来讲。",
    "q1": "第一部分，要找的到底是什么，也就是全部可能输入节点。",
    "q2": "第二部分，算法的核心：交替路径，以及为什么一次匹配就够了。",
    "q3": "第三部分，速度、生物网络上的结果，以及局限。",
    # possible inputs
    "c1": "先看第一部分。最大匹配，是一组尽可能多、彼此不共用起点也不共用终点的边。在一个最大匹配下，没有被匹配边指向的节点，构成一组最小输入节点集，也就是一种控制方案。",
    "c1b": "本站可控性专题的交互演示里，橙色的边是一组最大匹配，红色是输入节点。调高平均出度、换一个网络，输入节点都会跟着变。",
    "c2": "最大匹配往往不唯一，最小输入节点集也就有很多组。所有这些集合的并集，就是全部可能输入节点。这个例子里，是一到五这五个节点。",
    "c3": "知道了这个集合，才能在有约束时挑选控制方案，比如避开没法干预的蛋白。",
    "c4": "旧方法先求一个最大匹配，再对节点逐个检验，总的计算量是节点数乘以边数的量级。",
    # bipartite
    "b1": "下面进入第二部分。新算法的第一步，是把有向网络拆成二分图：每个节点分成两个点，上面一排是出端，下面一排是入端。",
    "b2": "一条从一指向二的边，就变成一的出端和二的入端之间的一条连线。",
    "b3": "在二分图上做最大匹配，就是黄色的这几条线。入端没有被匹配的节点就是输入节点，这里是一、四、五。",
    # alternating path
    "a1": "接下来，从输入节点的入端出发，沿着非匹配边、匹配边，交替着往前走。这样的路径，叫交替路径。",
    "a2": "从五的入端出发，非匹配边到四的出端，匹配边到三的入端，再经非匹配边到一的出端，匹配边到二的入端。",
    "a3": "【慢】这条交替路径经过的入端是三和二。论文的定理说，它们都是可能输入节点，而且都能替换节点五。",
    "a4": "反过来，任何交替路径都到不了的节点，就一定是冗余节点，比如这里的节点六。",
    # flip
    "f1": "定理为什么成立，我们看最短的一段：从五的入端，到三的入端。它以一条非匹配边开始，以一条匹配边结束，长度一定是偶数。",
    "f2": "把这段路径上每条边的匹配状态全部翻转。匹配边的数目不变，所以仍是最大匹配。右边的计数，三条还是三条。",
    "f3": "于是五被匹配了，路径终点的三失去匹配，成了新的输入节点。一组新的方案就出来了：一、四、三。",
    "f4": "反过来也能证明：如果一个节点在别的最大匹配里不被匹配，就一定有一条交替路径能走到它。所以，到不了的节点永远不会是输入节点。",
    # Hopcroft-Karp
    "k1": "那么，怎样快速找出所有交替路径。关键在一个经典的最大匹配算法。",
    "k2": "它一轮一轮地从所有未匹配的节点出发，搜索交替路径；找到能扩大匹配的路径，就把匹配扩大。黄色的边，就是逐步找到的匹配。",
    "k3": "【慢】到了最后一轮，再也找不到能扩大匹配的路径，算法结束。可这一轮，其实已经把从输入节点出发的交替路径全部搜了一遍。你看，搜索一层一层地铺开。",
    "k4": "只要在这一轮顺手记下到达过的入端，就得到了全部可能输入节点。在这张小网络上，结果和逐个检验完全一致。",
    "k5": "所以，总的计算量，和求一次最大匹配相同。",
    "k5b": "右下角的两个记号，前一个表示计算量和节点数乘以边数同一量级；后一个，节点数换成了它的平方根。节点数是一百万时，平方根只有一千。",
    # speed
    "s1": "下面进入第三部分，先看速度。这张图，纵轴是运行时间，每往上一格，时间乘以十。红色是旧方法，绿色是新算法。",
    "s1b": "在合成的无标度网络上，五百万个节点，新算法只用了三秒多，旧方法要六个多小时，快了约七千三百倍。",
    "s2": "网络越稠密，优势越明显。一百万个节点时，平均度从六增加到十六，加速比从三百多倍，升到四千倍左右。",
    "s3": "在真实网络上，加速可以达到一万倍的量级。",
    # biology & substitutes
    "p0": "再看生物网络。转录调控网络，记录的是基因之间谁开启、谁关闭谁。画面里，是关于基因表达调控的一段科普动画。",
    "p1": "在生物网络里，可能输入节点的比例差别很大：人类有向蛋白互作网络约为零点五九，大肠杆菌转录网络约为零点七三，一个酵母转录网络接近一。",
    "p2": "算法还顺带给出每个输入节点的替代节点集，也就是能替换它的那些节点。在一个食物网里，一组方案有十三个输入节点，它们的替代集大小各不相同。",
    "p2b": "这张图，是在一张示意网络上算出的结果。横轴是十三个输入节点，纵轴是各自替代集的大小。",
    "p3": "【慢】替代集大的输入节点更稳健：某个靶点用不了时，能很快找到备选，而且只改动一条匹配链。",
    "p3b": "画面里，是关于蛋白质作为药物靶点的一段讲解。药物靶点，就是药物直接作用的蛋白质。",
    # limits
    "l1": "最后说局限。这仍是线性时不变系统的结构可控性框架，只适用于有向网络。",
    "l2": "替代只保证单个输入节点可以换，多个同时换，可能互相冲突；加速倍数也依赖具体实现，应当理解为量级。",
    # recap
    "r1": "好，我们来总结一下。",
    "r2": "第一，一个最大匹配加上交替路径，就能找出全部可能输入节点。",
    "r3": "第二，这一步并入最大匹配算法的最后一轮，总计算量不变，大网络上快几个数量级。",
    "r4": "第三，它同时给出每个输入节点的替代集，靶点不可用时，可以快速换靶。",
}

EX = [(1, 2), (1, 3), (4, 3), (4, 5), (2, 6)]
EXPOS = {1: (-4.0, 1.0), 2: (-2.0, 2.0), 3: (-2.0, 0.0), 4: (-4.0, -1.0), 5: (-2.0, -2.0), 6: (0.0, 2.0)}
EXM = [(1, 2), (4, 3), (2, 6)]


def ex_net(shift=ORIGIN):
    G = nx.DiGraph(); G.add_nodes_from(sorted(EXPOS)); G.add_edges_from(EX)
    return G, {v: np.array([*p, 0]) + shift for v, p in EXPOS.items()}


def brute_union(G):
    nd = n_drivers(G); out = set()
    for D in itertools.combinations(sorted(G), nd):
        H = nx.DiGraph(); H.add_nodes_from(G); H.add_edges_from((u, v) for u, v in G.edges() if v not in D)
        if len(max_matching(H)) == G.number_of_nodes() - nd:
            out |= set(D)
    return out


def alt_levels(G, M):
    mout = {u: v for u, v in M}
    lvl = [[v for v in G if v not in {b for _, b in M}]]
    seen = set(lvl[0])
    while True:
        nxt = []
        for n in lvl[-1]:
            for c in G.predecessors(n):
                b = mout.get(c)
                if b is not None and b != n and b not in seen:
                    seen.add(b); nxt.append(b)
        if not nxt:
            return lvl
        lvl.append(nxt)


class Episode(Narrated):
    LINES = LINES

    def construct(self):
        self.hook()
        self.parts()
        self.possible()
        self.bipartite()
        self.altpath()
        self.flip()
        self.hk()
        self.speed()
        self.bio()
        self.limits()
        self.recap()

    # ------------------------------------------------------------------ hook
    def hook(self):
        grid = VGroup(*[Dot(radius=0.05, color=BLUE).set_opacity(0.7) for _ in range(24 * 16)]).arrange_in_grid(16, 24, buff=0.28).move_to(LEFT * 2.0)
        with self.say("h1") as d:
            self.play(FadeIn(grid, lag_ratio=0.002), run_time=d * 0.6)
            n = counter("节点", "40 万+", BLUE).move_to(RIGHT * 4.9 + UP * 2.2)
            self.play(FadeIn(n), run_time=0.6)
        cur = SurroundingRectangle(grid[0], color=GOLD, buff=0.08)
        with self.say("h2") as d:
            self.play(Create(cur), run_time=0.4)
            k = int((d - 0.8) / 0.12)
            for i in range(1, k):
                self.play(cur.animate.move_to(grid[i]), grid[i - 1].animate.set_color(GOLD).set_opacity(0.6), run_time=0.12)
        with self.say("h3") as d:
            old = counter("逐个检验", "约 13.7 小时", RED).next_to(n, DOWN, buff=0.6)
            self.play(FadeIn(old), run_time=0.8)
        with self.say("h4") as d:
            new = counter("新算法", "2.9 秒", GREEN).next_to(old, DOWN, buff=0.6)
            self.play(FadeOut(cur), grid.animate.set_color(GREEN), FadeIn(new), run_time=1.0)
        with self.say("h5") as d:
            x = T("约 17 000 倍", 52, GOLD, weight=BOLD).move_to(LEFT * 2.0)
            self.play(grid.animate.set_opacity(0.12), Write(x), run_time=1.2)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.6)

    def parts(self):
        head, items = slide("这一期分三部分", ["一  全部可能输入节点", "二  交替路径：一次匹配就够", "三  速度、生物网络与局限"])
        with self.say("q0") as d:
            self.play(FadeIn(head, shift=RIGHT * 0.3), run_time=0.6)
        for k, it in zip(("q1", "q2", "q3"), items):
            with self.say(k) as d:
                self.play(FadeIn(it, shift=RIGHT * 0.3), run_time=0.6)
        self.wait(0.6)
        self.play(FadeOut(head), FadeOut(items), run_time=0.6)

    # ------------------------------------------------------------------ possible inputs
    def possible(self):
        tag = self.chapter("一 · 全部可能输入节点")
        G, pos = ex_net(RIGHT * 1.0)
        net = DiNet(G, pos, r=0.3)
        M = set(EXM)
        U = brute_union(G)
        assert U == possible_inputs(G, M) == {1, 2, 3, 4, 5}
        with self.say("c1") as d:
            self.play(FadeIn(tag), FadeIn(net.group), run_time=0.8)
            self.play(*[net.arrows[e].animate.set_color(GOLD).set_stroke(width=6) for e in EXM], run_time=0.8)
            self.play(*[net.fill(v, RED, 0.8) for v in (1, 4, 5)], run_time=0.8)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.6)
        with self.say("c1b") as d:
            self.clip_on("matching_dense_demo.mp4", "full", "本站交互演示：最大匹配与驱动节点", start=0.3)
        self.clip_off()
        with self.say("c2") as d:
            self.play(FadeIn(tag), FadeIn(net.group), run_time=0.6)
            mis = [(1, 4, 5), (1, 4, 3), (1, 4, 2)]
            sets = VGroup(*[T("{" + "，".join(map(str, D)) + "}", 30, RED) for D in mis]).arrange(DOWN, buff=0.3).move_to(RIGHT * 4.6 + UP * 0.8)
            self.play(LaggedStart(*[FadeIn(s, shift=LEFT * 0.2) for s in sets], lag_ratio=0.3), run_time=1.5)
            un = T("并集 {1，2，3，4，5}", 30, GOLD).next_to(sets, DOWN, buff=0.5)
            self.play(FadeIn(un), *[net.fill(v, GOLD, 0.7) for v in U], run_time=1.0)
        with self.say("c3") as d:
            x = Cross(net.nodes[5], stroke_color=RED, scale_factor=0.9)
            self.play(Create(x), run_time=0.6)
            self.play(Indicate(net.nodes[3], color=GOLD), Indicate(net.nodes[2], color=GOLD), run_time=1.2)
        with self.say("c4") as d:
            self.play(FadeOut(VGroup(x, sets, un)), *[net.reset(v) for v in G], run_time=0.6)
            cur = SurroundingRectangle(net.nodes[1], color=GOLD)
            self.play(Create(cur), run_time=0.4)
            for v in (2, 3, 4, 5, 6):
                self.play(cur.animate.move_to(net.nodes[v]), run_time=0.4)
            o = MathTex(r"O(NL)", font_size=56, color=RED).move_to(RIGHT * 4.6 + UP * 0.5)
            self.play(Write(o), FadeOut(cur), run_time=0.8)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.6)

    # ------------------------------------------------------------------ bipartite
    def bp(self):
        xs = {v: -4.2 + 1.4 * (v - 1) for v in range(1, 7)}
        outp = {v: np.array([xs[v], 0.7, 0]) for v in xs}
        inp = {v: np.array([xs[v], -1.9, 0]) for v in xs}
        mk = lambda p, s, c: VGroup(Circle(radius=0.3, color=c, fill_color=BG, fill_opacity=1, stroke_width=3), T(s, 24)).move_to(p)
        on = {v: mk(outp[v], str(v), BLUE) for v in xs}
        inn = {v: mk(inp[v], str(v), VIOLET) for v in xs}
        lines = {(u, v): Line(outp[u], inp[v], color=MUTED, stroke_width=3).scale(0.82) for u, v in EX}
        lo = T("出端", 26, BLUE).next_to(on[1], LEFT, buff=0.5)
        li = T("入端", 26, VIOLET).next_to(inn[1], LEFT, buff=0.5)
        return outp, inp, on, inn, lines, VGroup(lo, li)

    def bipartite(self):
        tag = self.chapter("二 · 拆成二分图")
        G, pos = ex_net(LEFT * 1.0)
        net = DiNet(G, pos, r=0.3)
        outp, inp, on, inn, lines, lab = self.bp()
        with self.say("b1") as d:
            self.play(FadeIn(tag), FadeIn(net.group), run_time=0.8)
            self.play(net.group.animate.scale(0.55).to_corner(UR, buff=0.5).shift(DOWN * 0.3), run_time=1.0)
            self.play(*[FadeIn(x) for x in on.values()], *[FadeIn(x) for x in inn.values()], FadeIn(lab), run_time=1.2)
        with self.say("b2") as d:
            self.play(Indicate(net.arrows[(1, 2)], color=GOLD), run_time=0.8)
            self.play(Create(lines[(1, 2)].set_color(INK)), run_time=0.8)
            self.play(LaggedStart(*[Create(l) for e, l in lines.items() if e != (1, 2)], lag_ratio=0.2), lines[(1, 2)].animate.set_color(MUTED), run_time=1.4)
        with self.say("b3") as d:
            self.play(*[lines[e].animate.set_color(GOLD).set_stroke(width=6) for e in EXM], run_time=1.0)
            self.play(*[inn[v][0].animate.set_fill(RED, opacity=0.8).set_stroke(RED) for v in (1, 4, 5)], run_time=1.0)
        self.bpobjs = (outp, inp, on, inn, lines, lab, net)

    # ------------------------------------------------------------------ alternating path
    def altpath(self):
        tag = self.chapter("二 · 交替路径")
        outp, inp, on, inn, lines, lab, net = self.bpobjs
        old = [m for m in self.mobjects if isinstance(m, Text) and m not in lab and m is not tag and m.get_center()[1] > 3.2]
        path = [inp[5], outp[4], inp[3], outp[1], inp[2]]
        segs = [(4, 5), (4, 3), (1, 3), (1, 2)]
        with self.say("a1") as d:
            self.play(*[FadeOut(m) for m in old], FadeIn(tag), run_time=0.6)
            self.play(Indicate(inn[5], color=RED, scale_factor=1.4), run_time=1.0)
        walker = Dot(inp[5], radius=0.14, color=GREEN)
        trail = VGroup()
        with self.say("a2") as d:
            self.play(FadeIn(walker), run_time=0.3)
            for i, e in enumerate(segs):
                hl = Line(path[i], path[i + 1], color=GREEN, stroke_width=8).scale(0.82)
                trail.add(hl)
                self.play(walker.animate.move_to(path[i + 1]), Create(hl), run_time=(d - 0.6) / 4)
        with self.say("a3") as d:
            self.play(*[inn[v][0].animate.set_fill(GOLD, opacity=0.7).set_stroke(GOLD) for v in (3, 2)], run_time=1.0)
            sub = T("五的替代节点：三、二", 28, GOLD).to_edge(DOWN, buff=0.5)
            self.play(FadeIn(sub), run_time=0.6)
        with self.say("a4") as d:
            self.play(FadeOut(walker), run_time=0.3)
            self.play(inn[6][0].animate.set_fill(MUTED, opacity=0.5).set_stroke(MUTED), Indicate(lines[(2, 6)], color=GOLD), run_time=1.2)
            red = T("冗余", 26, MUTED).next_to(inn[6], DOWN, buff=0.2)
            self.play(FadeIn(red), run_time=0.5)
        self.altobjs = (trail, sub, red)

    # ------------------------------------------------------------------ flip
    def flip(self):
        tag = self.chapter("二 · 为什么成立：翻转")
        outp, inp, on, inn, lines, lab, net = self.bpobjs
        trail, sub, red = self.altobjs
        old = [m for m in self.mobjects if isinstance(m, Text) and m.get_center()[1] > 3.2 and m not in lab]
        with self.say("f1") as d:
            self.play(*[FadeOut(m) for m in old], FadeIn(tag), FadeOut(sub), FadeOut(red), FadeOut(trail), run_time=0.6)
            self.play(*[inn[v][0].animate.set_fill(BG, opacity=1).set_stroke(VIOLET) for v in (2, 3, 6)], run_time=0.5)
            seg = [Line(inp[5], outp[4], color=GREEN, stroke_width=9).scale(0.82), Line(outp[4], inp[3], color=GREEN, stroke_width=9).scale(0.82)]
            n1 = T("非匹配", 22, MUTED).next_to(seg[0].get_center(), RIGHT, buff=0.15)
            n2 = T("匹配", 22, GOLD).next_to(seg[1].get_center(), LEFT, buff=0.15)
            self.play(Create(seg[0]), FadeIn(n1), run_time=0.8)
            self.play(Create(seg[1]), FadeIn(n2), run_time=0.8)
        with self.say("f2") as d:
            self.play(FadeOut(VGroup(*seg, n1, n2)), run_time=0.4)
            self.play(lines[(4, 5)].animate.set_color(GOLD).set_stroke(width=6), lines[(4, 3)].animate.set_color(MUTED).set_stroke(width=3), run_time=1.4)
            c = counter("匹配边", "3 → 3", GOLD).move_to(RIGHT * 5.0 + DOWN * 0.6)
            self.play(FadeIn(c), run_time=0.6)
        with self.say("f3") as d:
            self.play(inn[5][0].animate.set_fill(BG, opacity=1).set_stroke(VIOLET), inn[3][0].animate.set_fill(RED, opacity=0.8).set_stroke(RED), run_time=1.2)
            ns = T("新方案 {1，4，3}", 30, RED).to_edge(DOWN, buff=0.5)
            self.play(FadeIn(ns), run_time=0.6)
        with self.say("f4") as d:
            self.play(Indicate(inn[6], color=MUTED), run_time=1.2)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.6)

    # ------------------------------------------------------------------ Hopcroft-Karp last round
    def hk(self):
        tag = self.chapter("二 · 并入最后一轮")
        G = nx.gnm_random_graph(16, 22, directed=True, seed=11)
        G.remove_edges_from(nx.selfloop_edges(G))
        pos = fit(nx.kamada_kawai_layout(G.to_undirected()), (-6.0, 1.2, -3.0, 2.8))
        net = DiNet(G, pos, r=0.22, labels=False)
        M = max_matching(G)
        lv = alt_levels(G, M)
        P = possible_inputs(G, M)
        U = brute_union(G)
        assert P == U == set().union(*lv), (P, U)
        assert len(U) < len(G)
        with self.say("k1") as d:
            self.play(FadeIn(tag), FadeIn(net.group), run_time=1.0)
        with self.say("k2") as d:
            Ms = sorted(M)
            for i in range(0, len(Ms), 3):
                self.play(*[net.arrows[e].animate.set_color(GOLD).set_stroke(width=5) for e in Ms[i:i + 3]], run_time=(d - 0.5) / ((len(Ms) + 2) // 3))
        with self.say("k3") as d:
            self.play(*[net.fill(v, RED, 0.8) for v in lv[0]], run_time=0.8)
            for L in lv[1:]:
                self.play(*[net.fill(v, GOLD, 0.7) for v in L], *[Flash(net.nodes[v], color=GOLD, line_length=0.12) for v in L], run_time=max(0.5, d * 0.5 / len(lv)))
        with self.say("k4") as d:
            rest = [v for v in G if v not in U]
            self.play(*[net.fill(v, MUTED, 0.45) for v in rest], run_time=0.8)
            c = counter("可能输入节点", f"{len(U)} / {len(G)}", GOLD).move_to(RIGHT * 4.2 + UP * 1.6)
            ok = T("与逐个检验一致 ✓", 26, GREEN).next_to(c, DOWN, buff=0.4)
            self.play(FadeIn(c), run_time=0.6)
            self.play(FadeIn(ok), run_time=0.6)
        with self.say("k5") as d:
            o1 = MathTex(r"O(NL)", font_size=48, color=RED)
            ar = MathTex(r"\rightarrow", font_size=48)
            o2 = MathTex(r"O(N^{1/2}L)", font_size=48, color=GREEN)
            row = VGroup(o1, ar, o2).arrange(RIGHT, buff=0.3).move_to(RIGHT * 4.1 + DOWN * 1.2)
            self.play(Write(o1), run_time=0.6)
        with self.say("k5b") as d:
            l1 = T("节点数 × 边数", 20, RED).next_to(o1, DOWN, buff=0.2)
            l2 = T("节点数的平方根 × 边数", 20, GREEN).next_to(o2, DOWN, buff=0.2)
            self.play(FadeIn(l1), run_time=0.6)
            self.play(Write(ar), Write(o2), FadeIn(l2), run_time=1.0)
            ex = T("100 万个节点：平方根 = 1000", 22, GOLD).next_to(VGroup(l1, l2), DOWN, buff=0.3)
            self.play(FadeIn(ex), run_time=0.6)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.6)

    # ------------------------------------------------------------------ speed
    def speed(self):
        tag = self.chapter("三 · 快了多少")
        ax = Axes(x_range=[0, 3, 1], y_range=[0, 5, 1], x_length=8.5, y_length=4.4,
                  axis_config={"color": MUTED, "include_tip": False, "font_size": 22}).move_to(DOWN * 0.4 + RIGHT * 0.3)
        ylabs = VGroup(*[T(s, 20, MUTED).next_to(ax.c2p(0, k), LEFT, buff=0.15) for k, s in enumerate(["1 秒", "10", "100", "1000", "1 万", "10 万"])])
        yl = T("运行时间（对数）", 22, MUTED).rotate(PI / 2).next_to(ylabs, LEFT, buff=0.2)
        data = [("500 万节点\n无标度", 24013, 3.276), ("Amazon0601", 49293, 2.886), ("Higgs_Twitter", 66445, 12.589)]

        def bar(x, t, c):
            h = ax.c2p(0, np.log10(t))[1] - ax.c2p(0, 0)[1]
            return Rectangle(width=0.8, height=max(0.03, h), fill_color=c, fill_opacity=0.9, stroke_width=0).move_to(ax.c2p(x, 0), aligned_edge=DOWN)
        groups = []
        for i, (nm, old, new) in enumerate(data):
            b1, b2 = bar(i + 0.32, old, RED), bar(i + 0.68, new, GREEN)
            lab = T(nm, 20, INK).next_to(ax.c2p(i + 0.5, 0), DOWN, buff=0.2)
            groups.append(VGroup(b1, b2, lab))
        lg = VGroup(VGroup(Square(0.25, fill_color=RED, fill_opacity=0.9, stroke_width=0), T("旧方法", 22)).arrange(RIGHT, buff=0.15),
                    VGroup(Square(0.25, fill_color=GREEN, fill_opacity=0.9, stroke_width=0), T("新算法", 22)).arrange(RIGHT, buff=0.15)
                    ).arrange(RIGHT, buff=0.5).next_to(ax, UP, buff=0.25)
        with self.say("s1") as d:
            self.play(FadeIn(tag), Create(ax), FadeIn(ylabs), FadeIn(yl), FadeIn(lg), run_time=1.0)
        with self.say("s1b") as d:
            self.play(FadeIn(groups[0][2]), GrowFromEdge(groups[0][0], DOWN), run_time=1.0)
            self.play(GrowFromEdge(groups[0][1], DOWN), run_time=0.8)
            sp = T("约 7330 倍", 26, GOLD, weight=BOLD).next_to(groups[0][1], UP, buff=0.2).shift(RIGHT * 0.6)
            self.play(FadeIn(sp), run_time=0.6)
        with self.say("s2") as d:
            dens = VGroup(T("100 万节点", 24, MUTED), T("平均度 6：315 倍", 28, INK), T("平均度 16：4097 倍", 28, GOLD)).arrange(DOWN, buff=0.2)
            box = BackgroundRectangle(dens, color=BG, fill_opacity=0.95, buff=0.25)
            VGroup(box, dens).to_corner(UR, buff=0.4).shift(DOWN * 0.9)
            self.play(FadeIn(box), FadeIn(dens[0]), FadeIn(dens[1]), run_time=0.8)
            self.play(FadeIn(dens[2], shift=UP * 0.2), run_time=0.8)
        with self.say("s3") as d:
            self.play(FadeOut(box), FadeOut(dens), run_time=0.5)
            for g in groups[1:]:
                self.play(FadeIn(g[2]), GrowFromEdge(g[0], DOWN), GrowFromEdge(g[1], DOWN), run_time=0.9)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.6)

    # ------------------------------------------------------------------ biology & substitutes
    def bio(self):
        with self.say("p0") as d:
            self.clip_on("yt_gene_regulation_amoeba.mp4", "center", "视频：Amoeba Sisters · YouTube", start=60)
        self.clip_off()
        tag = self.chapter("三 · 生物网络与替代节点")
        data = [("人类有向蛋白互作", 0.585, VIOLET), ("大肠杆菌转录", 0.730, BLUE), ("酵母转录", 0.999, GREEN)]
        rows = VGroup()
        for nm, f, c in data:
            bg = Rectangle(width=6.0, height=0.55, stroke_width=0, fill_color=MUTED, fill_opacity=0.3)
            fg = Rectangle(width=6.0 * f, height=0.55, stroke_width=0, fill_color=c, fill_opacity=0.9).align_to(bg, LEFT)
            rows.add(VGroup(T(nm, 26), VGroup(bg, fg), T(f"{f:.3f}", 26, c, weight=BOLD)))
        for i, r in enumerate(rows):
            y = 0.9 - 1.1 * i
            r[0].move_to([-5.2 + r[0].width / 2, y, 0]); r[1].move_to([0.9, y, 0]); r[2].next_to(r[1], RIGHT, buff=0.25)
        head = T("可能输入节点的比例", 24, MUTED).next_to(rows[0][1], UP, buff=0.35)
        with self.say("p1") as d:
            self.play(FadeIn(tag), FadeIn(head), run_time=0.6)
            for r in rows:
                self.play(FadeIn(r[0]), FadeIn(r[1][0]), run_time=0.4)
                self.play(GrowFromEdge(r[1][1], LEFT), FadeIn(r[2]), run_time=d * 0.2)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.6)
        S = sf_digraph(150, 2.0, 2.5, seed=5)
        M = max_matching(S)
        mout = {u: v for u, v in M}
        ins = [v for v in S if v not in {b for _, b in M} and S.in_degree(v) > 0][:13]
        sizes = []
        for m in ins:
            seen = {m}; q = [m]
            while q:
                n = q.pop()
                for c in S.predecessors(n):
                    b = mout.get(c)
                    if b is not None and b != n and b not in seen:
                        seen.add(b); q.append(b)
            sizes.append(len(seen) - 1)
        sizes = sorted(sizes, reverse=True)
        assert len(sizes) == 13 and sizes[0] > sizes[-1]
        ymax = int(np.ceil(max(sizes) / 5) * 5)
        ax = Axes(x_range=[0, 13, 1], y_range=[0, ymax, max(1, ymax // 2)], x_length=8.0, y_length=3.8,
                  axis_config={"color": MUTED, "include_tip": False, "font_size": 22},
                  y_axis_config={"numbers_to_include": [0, ymax // 2, ymax]}).move_to(DOWN * 0.5)
        xl = T("13 个输入节点", 22, MUTED).next_to(ax.x_axis, DOWN, buff=0.25)
        yl = T("替代集大小", 22, MUTED).rotate(PI / 2).next_to(ax.y_axis, LEFT, buff=0.35)
        sch = T("示意", 20, MUTED).to_corner(DR, buff=0.3)
        bars = VGroup(*[Rectangle(width=0.45, height=max(0.03, ax.c2p(0, s)[1] - ax.c2p(0, 0)[1]), fill_color=GOLD, fill_opacity=0.85,
                                  stroke_width=0).move_to(ax.c2p(i + 0.5, 0), aligned_edge=DOWN) for i, s in enumerate(sizes)])
        with self.say("p2") as d:
            pr = VGroup(*[Dot(radius=0.12, color=RED) for _ in range(13)]).arrange(RIGHT, buff=0.35).move_to(UP * 0.5)
            self.play(LaggedStart(*[GrowFromCenter(x) for x in pr], lag_ratio=0.1), run_time=1.5)
            self.play(FadeOut(pr), run_time=0.5)
        with self.say("p2b") as d:
            self.play(Create(ax), FadeIn(xl), FadeIn(yl), FadeIn(sch), run_time=1.0)
            self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.1), run_time=d * 0.5)
        with self.say("p3") as d:
            self.play(*[b.animate.set_fill(GREEN) for b in bars[:3]], run_time=1.0)
            tip = T("备选多，更稳健", 28, GREEN).next_to(bars[1], UP, buff=0.3).shift(RIGHT * 1.5)
            self.play(FadeIn(tip), run_time=0.6)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.6)
        with self.say("p3b") as d:
            self.clip_on("yt_protein_targets_chemhelp.mp4", "center", "视频：Chem Help ASAP · YouTube", start=30)
        self.clip_off()

    # ------------------------------------------------------------------ limits
    def limits(self):
        tag = self.chapter("三 · 局限")
        f = MathTex(r"\dot{\mathbf x}=A\mathbf x+B\mathbf u", font_size=56).move_to(UP * 1.2 + LEFT * 2.5)
        di = VGroup(arrow(LEFT * 0.8, RIGHT * 0.8, 0.0, INK, 5), T("只适用于有向网络", 28)).arrange(DOWN, buff=0.3).move_to(UP * 1.2 + RIGHT * 3.0)
        with self.say("l1") as d:
            self.play(FadeIn(tag), Write(f), run_time=1.2)
            self.play(FadeIn(di), run_time=0.8)
        with self.say("l2") as d:
            a = VGroup(Circle(radius=0.3, color=RED, fill_color=RED, fill_opacity=0.7), T("甲", 24)).move_to(LEFT * 3.5 + DOWN * 1.5)
            b = VGroup(Circle(radius=0.3, color=RED, fill_color=RED, fill_opacity=0.7), T("乙", 24)).move_to(LEFT * 1.5 + DOWN * 1.5)
            s = VGroup(Circle(radius=0.3, color=GOLD), T("丙", 24)).move_to(LEFT * 2.5 + DOWN * 2.8)
            l1 = DashedLine(a.get_bottom(), s.get_left(), color=GOLD); l2 = DashedLine(b.get_bottom(), s.get_right(), color=GOLD)
            q = T("同时替换可能冲突", 26, RED).next_to(s, RIGHT, buff=0.6)
            self.play(FadeIn(a), FadeIn(b), FadeIn(s), Create(l1), Create(l2), run_time=1.0)
            self.play(FadeIn(q), run_time=0.6)
            mag = T("加速倍数：看量级", 28, GOLD).move_to(RIGHT * 3.4 + DOWN * 2.0)
            self.play(FadeIn(mag), run_time=0.8)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.6)

    # ------------------------------------------------------------------ recap
    def recap(self):
        with self.say("r1") as d:
            head = T("三个要点", 40, INK, weight=BOLD).to_edge(UP, buff=0.7)
            self.play(Write(head), run_time=0.8)
        items = [("r2", BLUE, "一个最大匹配 + 交替路径 = 全部可能输入节点"),
                 ("r3", GOLD, "并入最后一轮，计算量不变，快几个数量级"),
                 ("r4", RED, "顺带给出替代集，靶点不可用时快速换靶")]
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
