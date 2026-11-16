"""Paper explainer: 动态网络的自适应控制（少换驱动节点）."""
import random

import networkx as nx
import numpy as np

from common import *  # noqa: F401,F403
from ep_robustness import fit, counter
from fctrl import DiNet, kuhn, drivers

TITLE = "动态网络的自适应控制：少换驱动节点"

LINES = {
    # hook
    "h1": "细胞里的分子相互作用、人与人之间的接触，连边都在不停地变化。你看，这张网络的边在变。",
    "h1b": "画面里，是细胞内部分子活动的一段动画。这些相互作用，时刻都在形成和断开。",
    "h2": "要控制这样的网络，每一刻都得选出驱动节点，也就是施加控制信号的节点，在它们身上装上控制器。",
    "h3": "网络只变了一点点。可如果每一刻都独立重新计算，控制器就会搬来搬去。",
    "h4": "每搬一次家，都是一笔额外的代价。右上角记着搬家的次数。",
    "h5": "【慢】这项研究要做的，就是在网络变化的同时，尽量少搬几次家。",
    # parts
    "k0": "这一期分四部分。",
    "k1": "第一部分，为什么驱动节点可以少换，以及怎样衡量换掉的代价。",
    "k2": "第二部分，两条选点原则，和据此设计的修补算法。",
    "k3": "第三部分，算法的效果。",
    "k4": "第四部分，意义和局限。",
    # non-unique
    "u1": "先看第一部分。回顾一下：最大匹配，是挑出尽量多的箭头，每个节点最多被一条挑中的箭头指向。没有被指向的节点，就是驱动节点。",
    "u2": "看这个小例子：甲同时指向乙和丙。可每个节点最多发出一条挑中的箭头，所以只能挑其中一条。",
    "u3": "挑甲到丙，驱动节点就是甲和乙；挑甲到乙，驱动节点就是甲和丙。",
    "u4": "两种方案大小一样，都能控制网络，成员却不同。",
    "u5": "【慢】所以，如果上一刻用的是甲和乙，这一刻继续用甲和乙，就一个都不用换。",
    # online
    "o1": "网络在一串时刻里的样子，叫快照。已有的时序网络控制方法，大多假设所有快照事先都知道。",
    "o2": "但在真实场景里，我们只能看到过去和现在。箭头指的是现在，后面的快照还是未知的。",
    "o3": "这项研究把额外控制代价写成画面上的式子。",
    "o3b": "竖线里，是这一刻的驱动节点去掉上一刻的驱动节点，也就是新加入的成员个数。求和号，把从第二个时刻到最后一个时刻的个数都加起来。",
    "o4": "目标是在每一刻都保证可控的前提下，让这个代价尽量小。这个问题在计算上非常困难，所以采用启发式方法，也就是不保证最优、但快而实用的办法。",
    # principles
    "q1": "下面进入第二部分。第一条原则是稳定性：历史上连边多、连边又变化少的节点，更适合当驱动节点。绿色节点就是这样，红色节点的连边变来变去。",
    "q2": "稳定性由画面上的公式计算。",
    "q2b": "蓝色这一项，是前后两个时刻，这个节点的邻边有多少是相同的；绿色这一项，是节点的度，也就是连接数。两者相乘，再把最近几个时刻加起来。",
    "q3": "第二条原则是一致性：尽量沿用上一刻已经在用的驱动节点，就是这几个黄色的。",
    "q4": "两条原则合成一个指标，就是这个式子。",
    "q4b": "黄色这一项：上一刻是驱动节点，就加上两倍的窗口长度；不是，就加零。绿色这一项，是刚才的稳定性。",
    "q5": "【慢】稳定性的得分，最高也到不了两倍窗口长度。所以老驱动节点的得分，一定高于其他节点，一致性永远优先。",
    # algorithm
    "a1": "有了指标，算法分三步。第一步，拿上一刻的最大匹配，删掉已经消失的匹配边，就是变红的这两条。",
    "a2": "第二步，给当前网络里的每个节点算出指标，标在节点下方。",
    "a3": "第三步，从得分低的节点开始，逐个寻找增广路径，也就是能把匹配再扩大一条边的路径。绿圈表示找到了，红圈表示没找到。",
    "a4": "得分高的节点排在最后，最容易保持没被指向，也就是继续当驱动节点。",
    "a5": "从旧匹配出发，网络只变一点的时候，需要修补的地方也很少。这里只新加入了一个驱动节点。",
    # results
    "s1": "下面进入第三部分。先用一个小模拟看看效果：六十个节点的网络，每一步随机改动一小部分连边，一共二十五个时刻。",
    "s2": "右边这张图，横轴是时刻，纵轴是累计的额外控制代价。灰色是每一刻独立重新计算，蓝色是自适应方法。",
    "s3": "蓝色曲线始终不高于灰色，到最后少换了六次驱动节点。",
    "s4": "这项研究在一千八百六十个合成动态网络上做了系统测试。下面每根条，是两种方法的代价之比，越短越好。变化较慢的网络上，代价几乎减半。",
    "s5": "两种方法的代价之比，在无标度网络上平均是零点七二，在随机网络上是零点八四。",
    "s6": "在二十个真实的动态网络上，平均比值是零点八一，变化慢的网络能降到零点五。",
    "s7": "【慢】网络剧烈变化时，指标失效，算法退化成普通的最大匹配，不会比基线更差。",
    # meaning
    "l1": "最后是第四部分。在生物医学里，细胞内的分子网络、按时间窗切分的脑功能网络，都可以看成一串快照。",
    "l1b": "比如经颅磁刺激，就是在头皮外用磁场刺激特定的脑区。画面里是这种治疗的介绍。",
    "l2": "在变化的脑网络上选刺激位点，少切换的方案也许更可行。但要注意，这项研究本身的实验，并没有使用生物数据。",
    "l3": "局限也要说清楚。第一，这是启发式算法，还没有和全局最优相比的理论保证。",
    "l4": "第二，代价只统计新加入的驱动节点，没有区分不同节点的实际干预成本；整个框架仍建立在线性结构可控性之上。",
    "l5": "回到开头那张网络。用自适应方法，同样三次变化，控制器只搬了三次家。",
    # recap
    "z0": "好，我们来总结一下。",
    "z1": "第一，最小驱动节点集往往不唯一，这给了我们少换人的自由。",
    "z2": "第二，按一致性优先、稳定性其次的指标，修补上一刻的匹配，就能少换驱动节点。",
    "z3": "第三，网络变化越慢，节省越多；剧烈变化时，至少不比基线差。",
    "z4": "结构可控性这一页有画面上的交互演示。每点一次换一个网络，红色的驱动节点就整个换一批，这正是自适应控制要避免的情形。",
}

HSEED = 58


def snaps(N, M, T, r, seed):
    rng = random.Random(seed)
    G = nx.gnm_random_graph(N, M, seed=seed, directed=True)
    out = [G.copy()]
    for _ in range(T - 1):
        E = list(G.edges())
        for e in rng.sample(E, max(1, int(r * len(E)))):
            G.remove_edge(*e)
        while G.number_of_edges() < M:
            u, v = rng.randrange(N), rng.randrange(N)
            if u != v and not G.has_edge(u, v):
                G.add_edge(u, v)
        out.append(G.copy())
    return out


def nbr_edges(G, v):
    return set(G.in_edges(v)) | set(G.out_edges(v))


def sigma(G, P, N):
    s = {}
    for v in G:
        a, b = nbr_edges(G, v), nbr_edges(P, v)
        J = len(a & b) / len(a | b) if a | b else 0.0
        s[v] = J * G.degree(v) / (N - 1)
    return s


def run_ac(S, l=3):
    """Adaptive control vs independent maximum matching; returns cumulative ECC curves."""
    N = S[0].number_of_nodes()
    sig, cA, cB, DA = [], [0], [0], []
    prevM = prevD = prevB = None
    for t, G in enumerate(S):
        sig.append({v: 0.0 for v in G} if t == 0 else sigma(G, S[t - 1], N))
        stb = {v: sum(x[v] for x in sig[-l:]) for v in G}
        if prevM is None:
            M = kuhn(G, list(G))
        else:
            part = {v: u for v, u in prevM.items() if G.has_edge(u, v)}
            q = {v: 2 * l * (v in prevD) + stb[v] for v in G}
            M = kuhn(G, sorted(G, key=lambda v: q[v]), start=part)
        D = set(drivers(G, M))
        B = set(drivers(G, kuhn(G, list(G))))
        if prevD is not None:
            cA.append(cA[-1] + len(D - prevD)); cB.append(cB[-1] + len(B - prevB))
        prevM, prevD, prevB = M, D, B
        DA.append(D)
    return cA, cB, DA


def mm_random(G, s):
    o = list(G); random.Random(s).shuffle(o)
    return kuhn(G, o)


class Episode(Narrated):
    LINES = LINES

    def construct(self):
        self.hook()
        self.parts()
        self.nonunique()
        self.online()
        self.principles()
        self.algorithm()
        self.results()
        self.meaning()
        self.recap()

    def clear(self, rt=0.8, keep=None):
        self.play(*[FadeOut(m) for m in self.mobjects if m is not keep], run_time=rt)

    # ------------------------------------------------------------------ shared demo
    def demo_setup(self, box=(-4.6, 4.6, -3.1, 2.7)):
        S = snaps(14, 18, 4, 0.12, HSEED)
        U = nx.DiGraph(); [U.add_edges_from(G.edges()) for G in S]; U.add_nodes_from(range(14))
        pos = fit(nx.kamada_kawai_layout(U.to_undirected()), box)
        return S, U, pos

    def snapshot(self, U, G, pos, r=0.2):
        """Arrows for all edges ever present; those absent in G are invisible."""
        net = DiNet(U, pos, r=r, color=BLUE, ecolor=MUTED, ew=2.4, eo=0.7)
        for e, ln in net.edges.items():
            if not G.has_edge(*e):
                ln.set_stroke(opacity=0); ln.tip.set_fill(opacity=0).set_stroke(opacity=0)
        return net

    def to_snapshot(self, net, G, color=MUTED, op=0.7):
        anims = []
        for e, ln in net.edges.items():
            on = G.has_edge(*e)
            anims.append(ln.animate.set_color(color).set_stroke(width=2.4, opacity=op if on else 0).set_fill(opacity=op if on else 0))
        return anims

    def ctrl(self, p):
        return Square(side_length=0.2, fill_color=GOLD, fill_opacity=1, stroke_width=0).move_to(np.array(p) + np.array([0.24, 0.24, 0]))

    def step(self, net, S, D, pos, ctr, cnt, tl, t, rt, col):
        old, new = D[t - 1], D[t]
        gone, come = sorted(old - new), sorted(new - old)
        anims = self.to_snapshot(net, S[t])
        for v in gone:
            if come:
                w = come.pop(0)
                c = ctr.pop(v); ctr[w] = c
                anims.append(c.animate.move_to(self.ctrl(pos[w]).get_center()))
            else:
                anims.append(FadeOut(ctr.pop(v)))
        for w in come:
            ctr[w] = self.ctrl(pos[w]); anims.append(FadeIn(ctr[w]))
        for v, c in net.nodes.items():
            anims.append(c.animate.set_fill(GOLD if v in new else BG, opacity=0.5 if v in new else 1).set_stroke(GOLD if v in new else BLUE))
        self.moves += len(new - old)
        anims.append(Transform(cnt, counter("控制器搬家", f"{self.moves} 次", col).move_to(cnt)))
        anims.append(Transform(tl, T(f"时刻 {t + 1}", 26, MUTED).move_to(tl)))
        self.play(*anims, run_time=rt)

    # ------------------------------------------------------------------ hook
    def hook(self):
        S, U, pos = self.demo_setup()
        net = self.snapshot(U, S[0], pos)
        with self.say("h1") as d:
            self.play(FadeIn(net.group), run_time=1.0)
            for G in (S[1], S[2], S[0]):
                self.play(*self.to_snapshot(net, G), run_time=0.8)
        self.remove(net.group)
        with self.say("h1b") as d:
            self.clip_on("yt_inner_life_cell.mp4", "center", "视频：XVIVO Scientific Animation · YouTube", start=30)
        self.clip_off()
        self.add(net.group)
        D = [set(drivers(G, mm_random(G, i))) for i, G in enumerate(S)]
        ctr = {v: self.ctrl(pos[v]) for v in D[0]}
        with self.say("h2") as d:
            self.play(*[net.nodes[v].animate.set_fill(GOLD, opacity=0.5).set_stroke(GOLD) for v in D[0]], run_time=0.8)
            self.play(LaggedStart(*[FadeIn(c, shift=DOWN * 0.2) for c in ctr.values()], lag_ratio=0.15), run_time=1.2)
        self.moves = 0
        cnt = counter("控制器搬家", "0 次", RED).to_corner(UR, buff=0.5)
        tl = T("时刻 1", 26, MUTED).to_corner(UL, buff=0.45)

        def step(t, rt=1.4):
            self.step(net, S, D, pos, ctr, cnt, tl, t, rt, RED)
        with self.say("h3") as d:
            self.play(FadeIn(tl), run_time=0.4)
            step(1)
            self.wait(0.3)
            step(2)
        with self.say("h4") as d:
            self.play(FadeIn(cnt), run_time=0.4)
            step(3)
            self.play(Indicate(cnt, color=RED), run_time=0.8)
        with self.say("h5") as d:
            q = T("变化之中，尽量少搬家", 48, INK, weight=BOLD)
            bg = BackgroundRectangle(q, color=BG, fill_opacity=0.85, buff=0.25)
            self.play(net.group.animate.set_opacity(0.2), *[c.animate.set_opacity(0.3) for c in ctr.values()], FadeOut(tl), run_time=0.8)
            self.play(FadeIn(bg), Write(q), run_time=1.4)
        self.clear()

    def parts(self):
        head, items = slide("这一期分四部分", ["一  只看过去，少换驱动节点", "二  指标与修补算法", "三  效果", "四  意义与局限"])
        with self.say("k0") as d:
            self.play(FadeIn(head, shift=RIGHT * 0.3), run_time=0.6)
        for k, it in zip(("k1", "k2", "k3", "k4"), items):
            with self.say(k) as d:
                self.play(FadeIn(it, shift=RIGHT * 0.3), run_time=0.6)
        self.wait(0.6)
        self.play(FadeOut(head), FadeOut(items), run_time=0.6)

    def recap(self):
        head, items = slide("小结", ["最小驱动节点集不唯一：可以少换人", "一致性优先、稳定性其次，修补旧匹配", "变化越慢越省；剧变时不差于基线"], accent=GOLD)
        with self.say("z0") as d:
            self.play(FadeIn(head, shift=RIGHT * 0.3), run_time=0.6)
        for k, it in zip(("z1", "z2", "z3"), items):
            with self.say(k) as d:
                self.play(FadeIn(it, shift=RIGHT * 0.3), run_time=0.6)
        self.wait(0.6)
        self.play(FadeOut(head), FadeOut(items), run_time=0.6)
        with self.say("z4") as d:
            self.clip_on("matching_switch.mp4", "full", "本站交互演示：驱动节点", start=0.3)
        self.wait(max(0.05, 11.5 - (self.renderer.time - self._clip['t0'])))
        self.clip_off()
        self.wait(1.0)

    # ------------------------------------------------------------------ non-unique MDS
    def nonunique(self):
        tag = self.chapter("一  只看过去，少换驱动节点")
        P = {"甲": np.array([-2.0, 0.3, 0]), "乙": np.array([2.0, 1.6, 0]), "丙": np.array([2.0, -1.0, 0])}
        G = nx.DiGraph([("甲", "乙"), ("甲", "丙")])
        net = DiNet(G, P, r=0.45, color=BLUE, ew=4, labels={k: k for k in P}, lsize=34, tip=0.28)
        with self.say("u1") as d:
            self.play(FadeIn(tag), *[GrowFromCenter(c) for c in net.nodes.values()], run_time=1.0)
            self.play(*[Create(e) for e in net.edges.values()], run_time=1.0)
        with self.say("u2") as d:
            self.play(Indicate(net.edge("甲", "乙"), color=GOLD), Indicate(net.edge("甲", "丙"), color=GOLD), run_time=1.2)
            one = T("只能选一条", 28, GOLD).move_to([0, -2.4, 0])
            self.play(FadeIn(one), run_time=0.6)
        s1 = T("方案一", 30, GOLD).move_to([-4.6, 2.6, 0])

        def show(matched, drv, label):
            anims = [net.edge(*matched).animate.set_color(GOLD).set_stroke(width=6, opacity=1)]
            other = ("甲", "乙") if matched == ("甲", "丙") else ("甲", "丙")
            anims.append(net.edge(*other).animate.set_color(MUTED).set_stroke(width=4, opacity=0.5))
            for v, c in net.nodes.items():
                anims.append(c.animate.set_fill(GOLD if v in drv else BG, opacity=0.5 if v in drv else 1, family=False).set_stroke(GOLD if v in drv else BLUE, family=False))
            anims.append(Transform(s1, T(label, 30, GOLD).move_to(s1)))
            return anims
        with self.say("u3") as d:
            self.play(FadeOut(one), FadeIn(s1), *show(("甲", "丙"), {"甲", "乙"}, "方案一"), run_time=1.2)
            self.wait(d * 0.3)
            self.play(*show(("甲", "乙"), {"甲", "丙"}, "方案二"), run_time=1.2)
        with self.say("u4") as d:
            c1 = VGroup(T("方案一：{甲, 乙}", 28, INK), T("方案二：{甲, 丙}", 28, INK)).arrange(DOWN, buff=0.25).move_to([-3.6, -2.4, 0])
            self.play(FadeIn(c1), run_time=0.8)
            sz = T("大小都是 2", 28, GOLD).next_to(c1, RIGHT, buff=0.8)
            self.play(FadeIn(sz), run_time=0.6)
        with self.say("u5") as d:
            self.play(*show(("甲", "丙"), {"甲", "乙"}, "上一刻"), run_time=1.0)
            self.play(Transform(s1, T("这一刻", 30, GOLD).move_to(s1)), run_time=0.6)
            zero = counter("需要更换", "0 个", GREEN).to_corner(UR, buff=0.5)
            self.play(FadeIn(zero), run_time=0.6)
        self.clear()

    # ------------------------------------------------------------------ online setting
    def online(self):
        tag = self.chapter("一  只看过去，少换驱动节点")
        S = snaps(10, 13, 6, 0.2, 3)
        frames = VGroup()
        for t, G in enumerate(S):
            box = RoundedRectangle(corner_radius=0.12, width=1.9, height=1.9, stroke_color=MUTED, stroke_width=1.5)
            pos = fit(nx.circular_layout(range(10)), (-0.75, 0.75, -0.75, 0.75))
            g = VGroup(*[Line(pos[u], pos[v], color=BLUE, stroke_width=1.5, stroke_opacity=0.8) for u, v in G.edges()],
                       *[Dot(pos[v], radius=0.05, color=INK) for v in G])
            frames.add(VGroup(box, g.move_to(box), T(f"G{t + 1}", 20, MUTED).next_to(box, DOWN, buff=0.12)))
        frames.arrange(RIGHT, buff=0.25).move_to(UP * 0.6)
        with self.say("o1") as d:
            self.play(FadeIn(tag), LaggedStart(*[FadeIn(f, shift=RIGHT * 0.2) for f in frames], lag_ratio=0.2), run_time=d * 0.6)
            allk = Brace(frames, DOWN, color=GOLD)
            al = T("全部事先已知", 26, GOLD).next_to(allk, DOWN, buff=0.15)
            self.play(GrowFromCenter(allk), FadeIn(al), run_time=0.7)
        with self.say("o2") as d:
            now = 2
            nowl = Arrow(frames[now].get_top() + UP * 0.8, frames[now].get_top() + UP * 0.1, color=GREEN, buff=0)
            nt = T("现在", 24, GREEN).next_to(nowl, UP, buff=0.1)
            self.play(FadeOut(allk), FadeOut(al), GrowArrow(nowl), FadeIn(nt), run_time=0.8)
            qs = VGroup(*[T("?", 60, MUTED).move_to(frames[i][0]) for i in range(now + 1, len(frames))])
            self.play(*[frames[i][1].animate.set_opacity(0.08) for i in range(now + 1, len(frames))], FadeIn(qs), run_time=1.2)
        with self.say("o3") as d:
            self.play(VGroup(frames, nowl, nt, qs).animate.scale(0.7).to_edge(UP, buff=0.9), run_time=0.8)
            f = MathTex(r"\mathrm{ECC}=\sum_{i=2}^{T}\,\big|\,D_i - D_{i-1}\big|", font_size=60, color=INK).shift(DOWN * 0.6)
            self.play(Write(f), run_time=d * 0.5)
        with self.say("o3b") as d:
            br = Brace(f, DOWN, color=GOLD)
            bl = T("这一刻新加入的驱动节点", 26, GOLD).next_to(br, DOWN, buff=0.15)
            self.play(GrowFromCenter(br), FadeIn(bl), run_time=0.8)
            self.play(Indicate(f[0][4:8], color=GOLD), run_time=1.2)
        with self.say("o4") as d:
            cons = T("约束：每个 Dᵢ 都是当前快照的最小驱动节点集", 26, MUTED).next_to(bl, DOWN, buff=0.4)
            self.play(FadeIn(cons), run_time=0.8)
            mn = T("最小化", 30, GREEN, weight=BOLD).next_to(f, LEFT, buff=0.3)
            self.play(FadeIn(mn, shift=RIGHT * 0.2), run_time=0.6)
            heur = T("启发式", 30, GOLD, weight=BOLD).next_to(f, RIGHT, buff=0.4)
            self.play(FadeIn(heur), run_time=0.6)
        self.clear()

    # ------------------------------------------------------------------ principles
    def principles(self):
        tag = self.chapter("二  指标与修补算法")
        # two nodes over three snapshots: one stable hub, one flickering node
        cols = VGroup()
        rng = np.random.default_rng(4)
        for t in range(3):
            c = np.array([-3.6 + t * 3.6, 0.4, 0])
            box = RoundedRectangle(corner_radius=0.15, width=3.2, height=3.6, stroke_color=MUTED, stroke_width=1.5).move_to(c)
            a = c + np.array([-0.7, 0.7, 0]); b = c + np.array([0.7, -0.9, 0])
            na = [a + 0.9 * np.array([np.cos(x), np.sin(x), 0]) for x in np.linspace(0, TAU, 5, endpoint=False)]
            ea = VGroup(*[Line(a, p, color=GREEN, stroke_width=3) for p in na])
            pick = rng.choice(5, 2, replace=False)
            nb = [b + 0.75 * np.array([np.cos(x), np.sin(x), 0]) for x in np.linspace(0, TAU, 5, endpoint=False) + 0.4]
            eb = VGroup(*[Line(b, nb[i], color=RED, stroke_width=3) for i in pick])
            g = VGroup(box, ea, eb, *[Dot(p, radius=0.07, color=MUTED) for p in na + nb], Dot(a, radius=0.16, color=GREEN), Dot(b, radius=0.16, color=RED),
                       T(f"t{'−' + str(2 - t) if t < 2 else ''}", 22, MUTED).next_to(box, UP, buff=0.1))
            cols.add(g)
        with self.say("q1") as d:
            self.play(FadeIn(tag), LaggedStart(*[FadeIn(c) for c in cols], lag_ratio=0.4), run_time=d * 0.55)
            ls = VGroup(T("稳定：连边多、变化少", 24, GREEN), T("不稳定：连边少、变来变去", 24, RED)).arrange(RIGHT, buff=1.0).to_edge(DOWN, buff=0.4)
            self.play(FadeIn(ls), run_time=0.8)
        with self.say("q2") as d:
            self.play(FadeOut(cols), FadeOut(ls), run_time=0.5)
            f1 = MathTex(r"\sigma_t(v)=", r"S_t(v)", r"\cdot", r"DC_t(v)", font_size=52, color=INK).shift(UP * 1.4)
            f1[1].set_color(BLUE); f1[3].set_color(GREEN)
            n1 = T("前后邻边的相似度", 22, BLUE).next_to(f1[1], DOWN, buff=0.3)
            n2 = T("度", 22, GREEN).next_to(f1[3], DOWN, buff=0.3)
            self.play(Write(f1), run_time=1.2)
        with self.say("q2b") as d:
            self.play(FadeIn(n1), run_time=0.6)
            self.wait(d * 0.2)
            self.play(FadeIn(n2), run_time=0.6)
            f2 = MathTex(r"stb_t(v)=\sum_{\text{last } l}\sigma(v)", font_size=46, color=INK).shift(DOWN * 0.9)
            self.play(Write(f2), run_time=1.2)
        with self.say("q3") as d:
            self.play(*[FadeOut(m) for m in (f1, n1, n2)], f2.animate.scale(0.7).to_corner(UR, buff=0.5), run_time=0.7)
            dots = VGroup(*[Dot(radius=0.2, color=MUTED) for _ in range(8)]).arrange(RIGHT, buff=0.6).shift(UP * 0.4)
            for i in (1, 4, 6):
                dots[i].set_color(GOLD)
            pl = T("上一刻的驱动节点", 24, GOLD).next_to(dots, DOWN, buff=0.4)
            self.play(FadeIn(dots), FadeIn(pl), run_time=0.8)
            self.play(*[Indicate(dots[i], color=GOLD, scale_factor=1.6) for i in (1, 4, 6)], run_time=1.0)
        with self.say("q4") as d:
            self.play(FadeOut(dots), FadeOut(pl), run_time=0.5)
            f3 = MathTex(r"q_v=", r"2l\cdot P_{t-1}(v)", r"+", r"stb_t(v)", font_size=58, color=INK).shift(UP * 1.2)
            f3[1].set_color(GOLD); f3[3].set_color(GREEN)
            self.play(Write(f3), run_time=1.4)
        with self.say("q4b") as d:
            n3 = T("上一刻是驱动节点：加 2l，否则加 0", 22, GOLD).next_to(f3[1], DOWN, buff=0.3)
            n4 = T("稳定性", 22, GREEN).next_to(f3[3], DOWN, buff=0.3)
            self.play(FadeIn(n3), run_time=0.6)
            self.wait(d * 0.3)
            self.play(FadeIn(n4), run_time=0.6)
        with self.say("q5") as d:
            nl = NumberLine(x_range=[0, 4, 1], length=9, color=MUTED, include_numbers=False).shift(DOWN * 1.4)
            labs = VGroup(*[MathTex(s, font_size=34, color=MUTED).next_to(nl.n2p(i), DOWN, buff=0.2) for i, s in ((0, "0"), (2, "2l"), (4, "4l"))])
            band1 = Rectangle(width=nl.n2p(2)[0] - nl.n2p(0)[0], height=0.4, fill_color=GREEN, fill_opacity=0.4, stroke_width=0).move_to((nl.n2p(0) + nl.n2p(2)) / 2 + UP * 0.35)
            band2 = Rectangle(width=nl.n2p(2)[0] - nl.n2p(0)[0], height=0.4, fill_color=GOLD, fill_opacity=0.5, stroke_width=0).move_to((nl.n2p(2) + nl.n2p(4)) / 2 + UP * 0.35)
            t1 = T("其他节点", 22, GREEN).next_to(band1, UP, buff=0.12)
            t2 = T("老驱动节点", 22, GOLD).next_to(band2, UP, buff=0.12)
            self.play(Create(nl), FadeIn(labs), run_time=0.8)
            self.play(FadeIn(band1), FadeIn(t1), run_time=0.7)
            self.play(FadeIn(band2, shift=RIGHT * 0.5), FadeIn(t2), run_time=0.9)
        self.clear()

    # ------------------------------------------------------------------ algorithm
    def algorithm(self):
        tag = self.chapter("二  指标与修补算法")
        S, U, pos = self.demo_setup(box=(-4.4, 4.4, -3.1, 2.4))
        G0, G1 = S[0], S[1]
        M0 = kuhn(G0, list(G0))
        D0 = set(drivers(G0, M0))
        net = self.snapshot(U, G0, pos)
        for v, u in M0.items():
            net.edges[(u, v)].set_color(GOLD).set_stroke(width=4.5, opacity=1)
        for v in D0:
            net.nodes[v].set_fill(GOLD, opacity=0.5).set_stroke(GOLD)
        step = T("上一刻的匹配", 26, GOLD).to_corner(UR, buff=0.5)
        vanished = [(u, v) for v, u in M0.items() if not G1.has_edge(u, v)]
        part = {v: u for v, u in M0.items() if G1.has_edge(u, v)}
        with self.say("a1") as d:
            self.play(FadeIn(tag), FadeIn(net.group), FadeIn(step), run_time=1.0)
            others = [e for e in net.edges if e not in [(u, v) for v, u in M0.items()]]
            self.play(*[net.edges[e].animate.set_stroke(opacity=0.7 if G1.has_edge(*e) else 0).set_fill(opacity=0.7 if G1.has_edge(*e) else 0) for e in others],
                      Transform(step, T("网络变了", 26, INK).to_corner(UR, buff=0.5)), run_time=1.0)
            self.play(*[net.edges[e].animate.set_color(RED).set_stroke(width=6) for e in vanished], run_time=0.6)
            self.play(*[net.edges[e].animate.set_stroke(opacity=0).set_fill(opacity=0) for e in vanished],
                      Transform(step, T("删去消失的匹配边", 26, RED).to_corner(UR, buff=0.5)), run_time=0.8)
        N, l = 14, 3
        sig1 = sigma(G1, G0, N)
        q = {v: 2 * l * (v in D0) + sig1[v] for v in G1}
        with self.say("a2") as d:
            qt = VGroup(*[T(f"{q[v]:.1f}", 18, GOLD if v in D0 else INK).next_to(net.nodes[v], DOWN, buff=0.05) for v in G1])
            self.play(Transform(step, T("计算指标 q", 26, INK).to_corner(UR, buff=0.5)), LaggedStart(*[FadeIn(x) for x in qt], lag_ratio=0.05), run_time=1.6)
        # step-by-step augmentation
        order = sorted(G1, key=lambda v: q[v])
        match = dict(part)
        used = {u: v for v, u in match.items()}
        history = []

        def aug(v, seen):
            for u in G1.predecessors(v):
                if u in seen:
                    continue
                seen.add(u)
                if u not in used or aug(used[u], seen):
                    match[v] = u; used[u] = v
                    return True
            return False
        for v in order:
            if v not in match:
                ok = aug(v, set())
                history.append((v, ok, dict(match)))
        D1 = set(drivers(G1, match))

        def show_match(m):
            ms = {(u, v) for v, u in m.items()}
            anims = []
            for e, ln in net.edges.items():
                if not G1.has_edge(*e):
                    continue
                anims.append(ln.animate.set_color(GOLD if e in ms else MUTED).set_stroke(width=4.5 if e in ms else 2.4, opacity=1 if e in ms else 0.6))
            return anims
        with self.say("a3") as d:
            self.play(Transform(step, T("从低分到高分，补全匹配", 26, INK).to_corner(UR, buff=0.5)), run_time=0.6)
            per = max(0.35, d * 0.6 / max(1, len(history)))
            for v, ok, m in history:
                ring = Circle(radius=0.3, color=GREEN if ok else RED, stroke_width=4).move_to(pos[v])
                self.play(Create(ring), *show_match(m), run_time=per * 0.6)
                self.play(FadeOut(ring), run_time=per * 0.4)
        with self.say("a4") as d:
            anims = [c.animate.set_fill(GOLD if v in D1 else BG, opacity=0.5 if v in D1 else 1).set_stroke(GOLD if v in D1 else BLUE) for v, c in net.nodes.items()]
            self.play(*anims, run_time=1.0)
            self.play(*[Indicate(net.nodes[v], color=GOLD, scale_factor=1.4) for v in D1], run_time=1.0)
        with self.say("a5") as d:
            nnew = len(D1 - D0)
            c1 = counter("新加入的驱动节点", f"{nnew} 个", GREEN).to_corner(UR, buff=0.5).shift(DOWN * 0.9)
            self.play(FadeIn(c1), run_time=0.8)
        self.clear()

    # ------------------------------------------------------------------ results
    def results(self):
        tag = self.chapter("三  效果")
        T_ = 25
        S = snaps(60, 90, T_, 0.03, 0)
        cA, cB, _ = run_ac(S)
        self.ecc = (cA[-1], cB[-1])
        G = S[0]
        pos = fit(nx.spring_layout(G.to_undirected(), seed=2), (-6.2, -1.2, -2.6, 2.2))
        dots = VGroup(*[Dot(pos[v], radius=0.05, color=INK) for v in G])
        lines = {e: Line(pos[e[0]], pos[e[1]], color=BLUE, stroke_width=1.2, stroke_opacity=0.6) for e in G.edges()}
        with self.say("s1") as d:
            self.play(FadeIn(tag), FadeIn(VGroup(*lines.values())), FadeIn(dots), run_time=1.0)
            for t in (1, 2, 3):
                newl = VGroup(*[Line(pos[u], pos[v], color=BLUE, stroke_width=1.2, stroke_opacity=0.6) for u, v in S[t].edges()])
                old = VGroup(*lines.values())
                self.play(Transform(old, newl), run_time=0.7)
            cn = counter("节点 · 时刻", "60 · 25", INK).next_to(dots, DOWN, buff=0.3)
            self.play(FadeIn(cn), run_time=0.4)
        ymax = int(np.ceil(max(cB) / 10) * 10)
        ax = Axes(x_range=[0, T_, 5], y_range=[0, ymax, 10], x_length=6, y_length=4.2,
                  axis_config={"color": MUTED, "include_tip": False, "font_size": 20},
                  x_axis_config={"numbers_to_include": [0, 5, 10, 15, 20, 25]},
                  y_axis_config={"numbers_to_include": list(range(0, ymax + 1, 10))}).shift(RIGHT * 3.3 + DOWN * 0.2)
        xl = T("时刻", 20, MUTED).next_to(ax.x_axis, DOWN, buff=0.4)
        yl = T("累计额外控制代价", 20, MUTED).rotate(PI / 2).next_to(ax.y_axis, LEFT, buff=0.4)
        xs = list(range(1, T_ + 1))
        lb = ax.plot_line_graph(xs, cB, line_color=MUTED, add_vertex_dots=False, stroke_width=5)
        la = ax.plot_line_graph(xs, cA, line_color=BLUE, add_vertex_dots=False, stroke_width=5)
        with self.say("s2") as d:
            self.play(Create(ax), FadeIn(xl), FadeIn(yl), run_time=1.0)
            self.play(Create(lb), run_time=d * 0.35, rate_func=linear)
            self.play(Create(la), run_time=d * 0.35, rate_func=linear)
        with self.say("s3") as d:
            tb = T(f"独立重算 {cB[-1]}", 22, MUTED).next_to(ax.c2p(T_, cB[-1]), UP, buff=0.12).shift(LEFT * 0.6)
            ta = T(f"自适应 {cA[-1]}", 22, BLUE).next_to(ax.c2p(T_, cA[-1]), DOWN, buff=0.15).shift(LEFT * 0.6)
            self.play(FadeIn(tb), FadeIn(ta), run_time=0.8)
            self.play(Indicate(la, color=BLUE), run_time=1.0)
        self.clear(0.6, keep=tag)
        # paper results: ratio bars
        rows = [("变化慢的合成网络", None, BLUE), ("无标度网络 平均", 0.72, BLUE), ("随机网络 平均", 0.84, BLUE),
                ("20 个真实网络 平均", 0.81, GREEN), ("变化慢的真实网络", 0.50, GREEN)]
        W = 7.0
        x0 = -1.6
        base = DashedLine([x0 + W, 2.5, 0], [x0 + W, -2.9, 0], color=MUTED)
        bl = T("基线 = 1", 22, MUTED).next_to(base, UP, buff=0.1)
        hd = T("代价之比（自适应 / 独立重算）", 24, MUTED).move_to([0.0, 3.0, 0])
        bars = []
        for i, (name, v, c) in enumerate(rows):
            y = 1.8 - i * 1.05
            lab = T(name, 24, INK).move_to([x0 - 0.3, y, 0], aligned_edge=RIGHT)
            if v is None:
                bar = Rectangle(width=W * 0.5, height=0.5, fill_color=c, fill_opacity=0.85, stroke_width=0).move_to([x0, y, 0], aligned_edge=LEFT)
                val = T("几乎减半", 24, c).next_to(bar, RIGHT, buff=0.2)
            else:
                bar = Rectangle(width=W * v, height=0.5, fill_color=c, fill_opacity=0.85, stroke_width=0).move_to([x0, y, 0], aligned_edge=LEFT)
                val = T(f"{v:.2f}", 24, c).next_to(bar, RIGHT, buff=0.2)
            bars.append(VGroup(lab, bar, val))
        with self.say("s4") as d:
            n = counter("合成动态网络", "1860 个", INK).to_corner(DR, buff=0.5)
            self.play(FadeIn(n), FadeIn(hd), Create(base), FadeIn(bl), run_time=1.0)
            self.play(FadeIn(bars[0][0]), GrowFromEdge(bars[0][1], LEFT), FadeIn(bars[0][2]), run_time=1.0)
        with self.say("s5") as d:
            self.play(FadeOut(n), run_time=0.3)
            for b in bars[1:3]:
                self.play(FadeIn(b[0]), GrowFromEdge(b[1], LEFT), FadeIn(b[2]), run_time=0.9)
        with self.say("s6") as d:
            for b in bars[3:]:
                self.play(FadeIn(b[0]), GrowFromEdge(b[1], LEFT), FadeIn(b[2]), run_time=0.9)
        with self.say("s7") as d:
            fast = VGroup(T("剧烈变化", 24, INK).move_to([x0 - 0.3, -3.35, 0], aligned_edge=RIGHT))
            fb = Rectangle(width=W, height=0.4, fill_color=MUTED, fill_opacity=0.6, stroke_width=0).move_to([x0, -3.35, 0], aligned_edge=LEFT)
            fv = T("≈ 1", 24, MUTED).next_to(fb, RIGHT, buff=0.2)
            self.play(VGroup(*bars, hd, base, bl).animate.shift(UP * 0.25), run_time=0.5)
            self.play(FadeIn(fast), GrowFromEdge(fb, LEFT), FadeIn(fv), run_time=1.2)
            nw = T("不会比基线更差", 26, GOLD).next_to(fv, UP, buff=0.25).shift(LEFT * 0.4)
            self.play(FadeIn(nw), run_time=0.6)
        self.clear()

    # ------------------------------------------------------------------ meaning & limits
    def meaning(self):
        tag = self.chapter("四  意义与局限")
        rng = np.random.default_rng(8)
        frames = VGroup()
        base = [np.array([np.cos(t) * 0.75 * (1 + 0.15 * np.sin(3 * t)), np.sin(t) * 0.6, 0]) for t in np.linspace(0, TAU, 10, endpoint=False)]
        for k in range(4):
            box = RoundedRectangle(corner_radius=0.15, width=2.4, height=2.0, stroke_color=MUTED, stroke_width=1.5)
            pairs = [(i, j) for i in range(10) for j in range(i + 1, 10) if rng.random() < 0.22]
            g = VGroup(*[Line(base[i], base[j], color=VIOLET, stroke_width=2, stroke_opacity=0.7) for i, j in pairs],
                       *[Dot(p, radius=0.06, color=INK) for p in base]).move_to(box)
            frames.add(VGroup(box, g, T(f"时间窗 {k + 1}", 20, MUTED).next_to(box, DOWN, buff=0.12)))
        frames.arrange(RIGHT, buff=0.35).shift(UP * 0.5)
        with self.say("l1") as d:
            self.play(FadeIn(tag), LaggedStart(*[FadeIn(f, shift=RIGHT * 0.2) for f in frames], lag_ratio=0.3), run_time=d * 0.6)
        keep = list(self.mobjects)
        self.remove(*keep)
        with self.say("l1b") as d:
            self.clip_on("yt_tms_ucdavis.mp4", "center", "视频：UC Davis Health · YouTube", start=40)
        self.clip_off()
        self.add(*keep)
        with self.say("l2") as d:
            stim = VGroup(*[Star(n=5, outer_radius=0.16, color=GOLD, fill_opacity=1).move_to(f[1][-1 - 3].get_center()) for f in frames])
            self.play(LaggedStart(*[FadeIn(s, scale=0.5) for s in stim], lag_ratio=0.2), run_time=1.2)
            same = T("少切换的刺激位点", 26, GOLD).next_to(frames, DOWN, buff=0.6)
            self.play(FadeIn(same), run_time=0.6)
            nb = T("这项研究的实验未使用生物数据", 24, MUTED).next_to(same, DOWN, buff=0.3)
            self.play(FadeIn(nb), run_time=0.6)
        with self.say("l3") as d:
            self.play(*[FadeOut(m) for m in (frames, stim, same, nb)], run_time=0.5)
            ax = Axes(x_range=[0, 10], y_range=[0, 4], x_length=8, y_length=3.4, axis_config={"color": MUTED, "include_tip": False}).shift(DOWN * 0.4)
            curve = ax.plot(lambda x: 2.0 + 0.8 * np.sin(1.3 * x) + 0.5 * np.cos(2.9 * x), x_range=[0.2, 9.8], color=MUTED, stroke_width=3)
            xopt = 0.2 + np.argmin([2.0 + 0.8 * np.sin(1.3 * x) + 0.5 * np.cos(2.9 * x) for x in np.linspace(0.2, 9.8, 400)]) * 9.6 / 399
            fx = lambda x: 2.0 + 0.8 * np.sin(1.3 * x) + 0.5 * np.cos(2.9 * x)
            here = Dot(ax.c2p(1.3, fx(1.3)), color=BLUE, radius=0.12)
            best = Dot(ax.c2p(xopt, fx(xopt)), color=GREEN, radius=0.12)
            self.play(Create(ax), Create(curve), run_time=1.0)
            hl = T("启发式找到的解", 22, BLUE).next_to(here, UP, buff=0.2)
            bl = T("全局最优", 22, GREEN).next_to(best, DOWN, buff=0.2)
            self.play(FadeIn(here), FadeIn(hl), run_time=0.6)
            gap = T("与最优差多少：没有理论保证", 26, GOLD).to_edge(UP, buff=1.0)
            self.play(FadeIn(best), FadeIn(bl), FadeIn(gap), run_time=0.8)
        with self.say("l4") as d:
            self.play(*[FadeOut(m) for m in (ax, curve, here, best, hl, bl, gap)], run_time=0.5)
            items = VGroup()
            for c, cost in ((BLUE, 1), (GREEN, 1), (VIOLET, 1)):
                items.add(VGroup(Dot(radius=0.3, color=c), T(f"代价 = {cost}", 26, INK)).arrange(DOWN, buff=0.2))
            items.arrange(RIGHT, buff=1.4).shift(UP * 0.5)
            self.play(FadeIn(items, lag_ratio=0.2), run_time=1.0)
            real = VGroup(T("真实干预成本可能各不相同", 26, GOLD), MathTex(r"\dot{x}=A x+B u", font_size=40, color=MUTED)).arrange(DOWN, buff=0.4).next_to(items, DOWN, buff=0.7)
            self.play(FadeIn(real[0]), run_time=0.6)
            self.play(Write(real[1]), run_time=1.0)
        with self.say("l5") as d:
            self.play(FadeOut(items), FadeOut(real), run_time=0.5)
            S, U, pos = self.demo_setup()
            _, _, D = run_ac(S)
            net = self.snapshot(U, S[0], pos)
            for v in D[0]:
                net.nodes[v].set_fill(GOLD, opacity=0.5).set_stroke(GOLD)
            ctr = {v: self.ctrl(pos[v]) for v in D[0]}
            self.moves = 0
            cnt = counter("控制器搬家", "0 次", GREEN).to_corner(UR, buff=0.5)
            tl = T("时刻 1", 26, MUTED).next_to(tag, DOWN, buff=0.3, aligned_edge=LEFT)
            self.play(FadeIn(net.group), *[FadeIn(c) for c in ctr.values()], FadeIn(cnt), FadeIn(tl), run_time=1.0)
            for t in (1, 2, 3):
                self.step(net, S, D, pos, ctr, cnt, tl, t, 1.1, GREEN)
        self.wait(0.8)
        self.clear(1.0)
