"""Animated explainer: 生物分子网络与拓扑特征 (data, study bias, hubs & lethality, diseasome, motifs, FFL)."""
import random

import networkx as nx
import numpy as np

from common import *  # noqa: F401,F403
from kit_c import (PANEL, NetView, arrow, axes, callout, chip, clip_line, counter, fade_all, fit, grow_bars, hist_bars, inhib, parts, sf_graph, waffle,
                   xlabel, ylabel)

TITLE = "细胞里的网络：枢纽、疾病基因与网络基序"

LINES = {
    # hook
    "h1": "细胞外的信号，来了又走。有的只闪一下，有的会持续很久。",
    "h1b": "上面的黄线是输入信号，下面的绿线是一个基因的表达量。",
    "h2": "先来一个短暂的信号。它一闪而过——基因没有反应。",
    "h3": "再来一个同样强的信号，持续得久一点。基因开启了。",
    "h4": "【慢】细胞没有时钟，却分得清哪个是噪声，哪个是真信号。",
    "h5": "秘密藏在分子之间的连线方式里。这一期，我们走进细胞内部的网络。",
    "q0": "这一期分三部分。",
    "q1": "第一部分，数据：边是怎么测出来的。",
    "q2": "第二部分，结构：枢纽、必需基因和疾病基因在哪里。",
    "q3": "第三部分，功能：几个基因组成的小电路。",
    # data
    "d0": "先看第一部分。细胞里，蛋白质不断被合成，又彼此结合、分工协作。",
    "d1": "第一张网络是蛋白质相互作用网络：两个蛋白结合，就连一条边，没有方向。",
    "d2": "第二张是转录调控网络。转录因子是一类蛋白质，它结合在基因前面的开关区域，叫启动子。",
    "d2b": "画面里，一个蛋白质正沿着双螺旋滑动，寻找结合的位置。",
    "d2c": "这种边有方向：从转录因子指向靶基因。绿色箭头是激活，红色平头线是抑制。",
    "d3": "蛋白之间的边，第一种测法叫酵母双杂交，一次只检验两个蛋白能不能直接结合。",
    "d3b": "你看：A和B直接接触，测到了；A和D不接触，测不到。",
    "d4": "第二种方法叫亲和纯化质谱：用诱饵蛋白A，把整个复合物都拉下来。",
    "d5": "拉下来的蛋白都和A连边。注意这条红线——A和D并没有直接接触。",
    "d5b": "【慢】同样叫一条边，含义可能不一样。",
    "d6": "人类约有两万个蛋白编码基因。常用的互作组，整理了十四万多条相互作用。",
    "d7": "可它远不完整。2020年的一张系统性图谱，报告了约五万三千条两两直接结合的相互作用。",
    "d7b": "这大约是此前高质量整理数据的四倍。黄色虚线，代表还没测到的边。",
    # study bias
    "b1": "还有一个陷阱，叫研究偏倚：越热门的基因，被报道的相互作用越多。",
    "b2": "我们模拟一下。每个蛋白真实的伙伴数差不多，颜色越亮，越热门。",
    "b3": "可冷门蛋白之间的边，大多没人去测，就淡掉了。",
    "b4": "右图横轴是研究热度，纵轴是度，也就是连接数。灰点是真实的度。",
    "b5": "黄点是观测到的度，它跟着热度一起上升。热门蛋白看起来就成了枢纽。",
    "b6": "【慢】所以，疾病基因度高，可能只是因为它们被研究得多。",
    # hubs & lethality
    "e1": "下面进入第二部分。2001年，一项研究把酵母的蛋白质互作网络和基因敲除实验放在一起看。",
    "e1b": "必需基因，就是一敲除细胞就会死的基因。红色就是这样的基因。",
    "e2": "伙伴不超过五个的蛋白，占了绝大多数，其中约百分之二十一是必需的。",
    "e3": "【慢】伙伴超过十五个的枢纽，不到百分之一，其中约百分之六十二是必需的。",
    "e4": "这个规律很稳健，解释却有几种。第一种：拿掉枢纽，网络就碎了。",
    "e5": "第二种：少数相互作用本身是必需的，伙伴越多，越可能碰上一条。",
    "e6": "第三种：必需基因集中在复合物里，复合物内部连接密，成员的度天然就高。",
    "e6b": "核糖体就是这样的复合物，它是细胞制造蛋白质的机器。",
    "e7": "我们模拟第三种情形。横轴是度，纵轴是必需蛋白的比例。",
    "e7b": "单独看，度越高，蓝柱越高。",
    "e8": "但按复合物分开看，红线和灰线都是平的——度和必需性的关系消失了。",
    "e9": "【慢】一个稳健的相关，可以对应几种不同的机制。",
    # diseasome
    "g1": "再看疾病基因。2007年，一项研究把已知的疾病和致病基因连成一张网络。",
    "g1b": "左边一列是疾病，右边一列是基因，疾病和它的致病基因相连。",
    "g2": "两种疾病共享一个致病基因，就连一条边。你看，黄色的癌症聚在了一起。",
    "g3": "放回互作网络里看：红色的必需基因多是枢纽，在中央。",
    "g3b": "【慢】蓝色的遗传病基因，大多不是枢纽，分布在外围。",
    "g4": "因为严重破坏枢纽的突变，往往在胚胎期就致死，成不了遗传病。",
    "g5": "癌症由体细胞突变引起，不受这个限制。黄色的癌症基因更靠近中心。",
    # motifs
    "m1": "最后是第三部分。我们把镜头拉近，只看三个节点。",
    "m2": "X调控Y，X和Y又一起调控Z。这个结构叫前馈环。",
    "m3": "左边是一张模拟的调控网络，亮起来的边组成了前馈环。",
    "m3b": "前馈环多，也可能只是因为有些节点连接多，所以要和随机网络比。",
    "m4": "随机化时，每个节点进来和出去的边数都不变，只交换连接对象。",
    "m5": "打乱两百次，灰色柱子就是随机网络里前馈环数量的分布。",
    "m6": "黄色竖线是真实网络的数量，远远落在右边。",
    "m6b": "这个公式叫Z分数：分子是真实数量减随机平均，分母是随机的标准差。",
    "m6c": "也就是偏离随机多少个标准差。这里大于五，远超随机波动。",
    "m7": "【慢】显著多于随机网络的小子图，就叫网络基序。",
    # FFL
    "f1": "回到开头。左边是前馈环，Z要表达，需要X和Y同时在场。",
    "f1b": "右边三条曲线，是X、Y、Z随时间的变化。红色虚线是Y的阈值。",
    "f2": "长脉冲来了，X立刻激活，Y慢慢积累，越过阈值，Z才开启。",
    "f3": "短脉冲时，Y还没到阈值，信号就结束了，Z不响应。",
    "f4": "【慢】这个小电路是一个持续性检测器，能过滤掉噪声。",
    "f7": "不过，结构不能唯一决定功能，参数变了，行为也会变。",
    # recap
    "r1": "好，我们总结一下。",
    "r2": "第一，边的含义取决于测量方法，还带着研究偏倚。",
    "r3": "第二，枢纽和致死性的相关很稳健，机制却有几种解释。",
    "r4": "第三，网络基序像电路元件，前馈环能过滤噪声。",
    "r5": "这个专题的知识页面里有这个交互演示，拖动脉冲长度，看短脉冲怎样被过滤。",
}


# ----------------------------------------------------------------------------- simulations
def ffl_sim(pulses, T=12.0, dt=0.01, K=0.5):
    """Coherent type-1 FFL with AND gate. Returns t, X, Y, Z."""
    t = np.arange(0, T + dt, dt)
    X = np.zeros_like(t)
    for a, b in pulses:
        X[(t >= a) & (t < b)] = 1.0
    Y = np.zeros_like(t); Z = np.zeros_like(t)
    for i in range(1, len(t)):
        Y[i] = Y[i - 1] + dt * (X[i - 1] - Y[i - 1])
        on = X[i - 1] > 0.5 and Y[i - 1] > K
        Z[i] = Z[i - 1] + dt * ((1.0 if on else 0.0) - Z[i - 1])
    return t, X, Y, Z


def motif_graph():
    rng = random.Random(0)
    nt, N, ne, nf = 20, 90, 55, 10
    G = nx.DiGraph(); G.add_nodes_from(range(N))
    while G.number_of_edges() < ne:
        G.add_edge(rng.choice(range(nt)), rng.randrange(nt, N))
    for _ in range(nf):
        x, y = rng.sample(range(nt), 2); z = rng.randrange(nt, N)
        G.add_edges_from([(x, y), (x, z), (y, z)])
    return G


def ffls(G):
    out = []
    for x in G:
        for y in G.successors(x):
            for z in G.successors(y):
                if z != x and G.has_edge(x, z):
                    out.append((x, y, z))
    return out


def swap_once(H, E, rng):
    while True:
        i, j = rng.sample(range(len(E)), 2)
        (a, b), (c, d) = E[i], E[j]
        if len({a, b, c, d}) < 4 or H.has_edge(a, d) or H.has_edge(c, b):
            continue
        H.remove_edge(a, b); H.remove_edge(c, d); H.add_edge(a, d); H.add_edge(c, b)
        E[i], E[j] = (a, d), (c, b)
        return (a, b), (c, d), (a, d), (c, b)


def randomize(G, n, rng):
    H = G.copy(); E = list(H.edges())
    for _ in range(n):
        swap_once(H, E, rng)
    return H


# ----------------------------------------------------------------------------- episode
class Episode(Narrated):
    LINES = LINES

    def construct(self):
        self.hook()
        self.questions()
        self.data()
        self.bias()
        self.lethality()
        self.diseasome()
        self.motifs()
        self.ffl()
        self.recap()

    # ------------------------------------------------------------------ hook
    def pulse_axes(self, y_top=1.6):
        a1 = axes([0, 12, 2], [0, 1.2, 1], 9.5, 1.5)
        a2 = axes([0, 12, 2], [0, 1.2, 1], 9.5, 1.5)
        a1.move_to(RIGHT * 1.0 + UP * y_top); a2.move_to(RIGHT * 1.0 + UP * (y_top - 2.6))
        l1 = T("输入信号", 24, GOLD).next_to(a1, LEFT, buff=0.35)
        l2 = T("基因表达", 24, GREEN).next_to(a2, LEFT, buff=0.35)
        tl = T("时间", 22, MUTED).next_to(a2.x_axis, DOWN, buff=0.2).align_to(a2, RIGHT)
        return a1, a2, VGroup(l1, l2, tl)

    def trace(self, ax, t, y, lo, hi, color):
        m = (t >= lo) & (t <= hi)
        return ax.plot_line_graph(t[m], y[m], line_color=color, add_vertex_dots=False, stroke_width=4)

    def hook(self):
        t, X, Y, Z = ffl_sim([(1.0, 1.5), (5.0, 9.0)])
        self.sim = (t, X, Y, Z)
        a1, a2, labs = self.pulse_axes()
        with self.say("h1") as d:
            self.play(Create(a1), Create(a2), run_time=d * 0.5)
        with self.say("h1b") as d:
            self.play(FadeIn(labs[0]), Indicate(a1, color=GOLD, scale_factor=1.02), run_time=1.0)
            self.play(FadeIn(labs[1]), Indicate(a2, color=GREEN, scale_factor=1.02), run_time=1.0)
            self.play(FadeIn(labs[2]), run_time=0.5)
        with self.say("h2") as d:
            x1, z1 = self.trace(a1, t, X, 0, 4, GOLD), self.trace(a2, t, Z, 0, 4, GREEN)
            self.play(Create(x1), Create(z1), run_time=d * 0.7, rate_func=linear)
            q = T("没反应", 26, MUTED).next_to(a2.c2p(1.3, 0), UP, buff=0.35)
            self.play(FadeIn(q), run_time=0.5)
        with self.say("h3") as d:
            x2, z2 = self.trace(a1, t, X, 4, 12, GOLD), self.trace(a2, t, Z, 4, 12, GREEN)
            self.play(Create(x2), Create(z2), run_time=d * 0.75, rate_func=linear)
            on = T("开启", 26, GREEN).next_to(a2.c2p(7.5, 1.0), UP, buff=0.12)
            self.play(FadeIn(on), run_time=0.5)
        with self.say("h4") as d:
            br1 = BraceBetweenPoints(a1.c2p(1.0, 1.1), a1.c2p(1.5, 1.1), UP, color=RED)
            br2 = BraceBetweenPoints(a1.c2p(5.0, 1.1), a1.c2p(9.0, 1.1), UP, color=GREEN)
            self.play(GrowFromCenter(br1), GrowFromCenter(br2), run_time=1.0)
            clock = T("噪声被过滤，信号被保留", 48, GOLD, weight=BOLD).move_to(DOWN * 3.0)
            self.play(Write(clock), run_time=d * 0.35)
        with self.say("h5") as d:
            self.play(*[FadeOut(m) for m in self.mobjects], run_time=1.0)
            G = sf_graph(120, 2.3, seed=12, kmax=20)
            net = NetView(G, fit(nx.kamada_kawai_layout(G), (-6.0, 6.0, -3.3, 3.3)), color=GREEN, eo=0.35)
            self.play(LaggedStart(*[GrowFromCenter(x) for x in net.dots.values()], lag_ratio=0.01),
                      LaggedStart(*[Create(e) for e in net.edges.values()], lag_ratio=0.004), run_time=d * 0.6)
        self.play(FadeOut(net.group), run_time=0.8)

    def questions(self):
        parts(self, "这一期分三部分", ["一  数据：边从哪里来", "二  结构：枢纽、必需基因与疾病基因", "三  功能：网络基序"], ["q0", "q1", "q2", "q3"])

    # ------------------------------------------------------------------ data sources
    def data(self):
        tag = self.chapter("一  数据：边从哪里来")
        clip_line(self, "d0", "yt_dna_to_protein.mp4", "视频：yourgenome · YouTube", start=95)
        # PPI: two proteins dock
        pa = Circle(radius=0.75, color=BLUE, fill_opacity=0.35).move_to(LEFT * 5.2 + UP * 0.6)
        pb = RegularPolygon(6, radius=0.6, color=VIOLET, fill_opacity=0.35).move_to(LEFT * 1.8 + UP * 0.6)
        la, lb = T("蛋白 A", 24).next_to(pa, DOWN), T("蛋白 B", 24).next_to(pb, DOWN)
        with self.say("d1") as d:
            self.play(FadeIn(tag), FadeIn(pa), FadeIn(pb), FadeIn(la), FadeIn(lb), run_time=1.0)
            self.play(pb.animate.move_to(LEFT * 3.88 + UP * 0.6), lb.animate.next_to(LEFT * 3.88 + UP * 0.0, DOWN, buff=0.1),
                      run_time=1.2)
            ga, gb = Dot(RIGHT * 2.0 + UP * 0.6, radius=0.16, color=BLUE), Dot(RIGHT * 4.6 + UP * 0.6, radius=0.16, color=VIOLET)
            e = Line(ga.get_center(), gb.get_center(), color=INK, stroke_width=4)
            eq = MathTex(r"\Rightarrow", font_size=60, color=MUTED).move_to(RIGHT * 0.0 + UP * 0.6)
            self.play(FadeIn(eq), GrowFromCenter(ga), GrowFromCenter(gb), run_time=0.8)
            self.play(Create(e), run_time=0.8)
            lab = T("无向", 24, MUTED).next_to(e, UP, buff=0.25)
            self.play(FadeIn(lab), run_time=0.5)
        top = VGroup(pa, pb, la, lb, ga, gb, e, eq, lab)
        with self.say("d2") as d:
            self.play(top.animate.scale(0.6).shift(UP * 1.6), run_time=0.8)
            dna = Line(LEFT * 6.0 + DOWN * 1.8, LEFT * 0.5 + DOWN * 1.8, color=MUTED, stroke_width=6)
            gene = Rectangle(width=1.6, height=0.5, color=GREEN, fill_opacity=0.5).move_to(LEFT * 2.0 + DOWN * 1.8)
            gl = T("靶基因", 22).next_to(gene, DOWN, buff=0.15)
            tf = Ellipse(width=1.2, height=0.7, color=GOLD, fill_opacity=0.5).move_to(LEFT * 4.6 + DOWN * 0.3)
            tfl = T("转录因子", 22, GOLD).next_to(tf, UP, buff=0.1)
            self.play(Create(dna), FadeIn(gene), FadeIn(gl), FadeIn(tf), FadeIn(tfl), run_time=1.0)
            self.play(tf.animate.move_to(LEFT * 4.0 + DOWN * 1.45), tfl.animate.next_to(LEFT * 4.0 + DOWN * 1.1, UP, buff=0.1), run_time=0.9)
            prom = T("启动子", 22, GOLD).next_to(LEFT * 4.0 + DOWN * 1.8, DOWN, buff=0.2)
            self.play(FadeIn(prom), run_time=0.5)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.6)
        clip_line(self, "d2b", "yt_tf_slide_dna_hhmi.mp4", "视频：HHMI BioInteractive · YouTube", start=20)
        with self.say("d2c") as d:
            n1, n2, n3 = Dot(RIGHT * 2.0 + DOWN * 0.9, radius=0.16, color=GOLD), Dot(RIGHT * 4.6 + DOWN * 0.9, radius=0.16, color=GREEN), Dot(RIGHT * 4.6 + DOWN * 2.6, radius=0.16, color=GREEN)
            n0 = Dot(RIGHT * 2.0 + DOWN * 2.6, radius=0.16, color=GOLD)
            act = arrow(n1.get_center(), n2.get_center(), GREEN, buff=0.2)
            rep = inhib(n0.get_center(), n3.get_center(), RED, buff=0.2)
            al = T("激活", 22, GREEN).next_to(act, UP, buff=0.12)
            rl = T("抑制", 22, RED).next_to(rep, UP, buff=0.12)
            self.play(FadeIn(n1), FadeIn(n2), GrowArrow(act), FadeIn(al), run_time=0.9)
            self.play(FadeIn(n0), FadeIn(n3), Create(rep), FadeIn(rl), run_time=0.9)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.8)
        # Y2H vs AP-MS on the same complex
        P = {"A": np.array([0, 0, 0]), "B": np.array([-0.95, 0.55, 0]), "C": np.array([0.95, 0.55, 0]), "D": np.array([1.9, 0.0, 0])}
        cols = {"A": GOLD, "B": BLUE, "C": VIOLET, "D": GREEN}

        def complex_at(c):
            g = VGroup(*[Circle(radius=0.55, color=cols[k], fill_opacity=0.35, stroke_width=3).move_to(P[k] + c) for k in P])
            g.add(*[T(k, 26).move_to(P[k] + c) for k in P])
            return g
        cl, cr = LEFT * 4.4 + UP * 1.0, RIGHT * 2.0 + UP * 1.0
        cxl, cxr = complex_at(cl), complex_at(cr)
        hl = T("酵母双杂交", 28, INK).move_to(LEFT * 3.5 + UP * 2.8)
        hr = T("亲和纯化质谱", 28, INK).move_to(RIGHT * 2.9 + UP * 2.8)
        sep = DashedLine(UP * 3.0, DOWN * 3.4, color=MUTED, stroke_opacity=0.4).shift(RIGHT * 0.2)
        G0 = {k: P[k] * 1.0 for k in P}

        def gnode(k, c):
            return VGroup(Dot(G0[k] + c, radius=0.14, color=cols[k]), T(k, 20, MUTED).next_to(G0[k] + c, DOWN, buff=0.12))
        bl, br = LEFT * 4.4 + DOWN * 2.0, RIGHT * 2.0 + DOWN * 2.0
        with self.say("d3") as d:
            self.play(FadeIn(hl), FadeIn(cxl), Create(sep), run_time=1.0)
            pairs = [("A", "B", True), ("A", "C", True), ("C", "D", True), ("A", "D", False), ("B", "D", False)]
            nodes_l = VGroup(*[gnode(k, bl) for k in P])
            self.play(FadeIn(nodes_l), run_time=0.6)
            ok_edges = VGroup()
            for u, v, ok in pairs:
                probe = DashedLine(P[u] + cl, P[v] + cl, color=GREEN if ok else RED, stroke_width=4)
                mark = T("✓" if ok else "✗", 30, GREEN if ok else RED, weight=BOLD).move_to((P[u] + P[v]) / 2 + cl + UP * 0.35)
                self.play(Create(probe), FadeIn(mark), run_time=0.35)
                if ok:
                    ln = Line(G0[u] + bl, G0[v] + bl, color=INK, stroke_width=3)
                    ok_edges.add(ln)
                    self.play(Create(ln), FadeOut(probe), FadeOut(mark), run_time=0.3)
                else:
                    self.play(FadeOut(probe), FadeOut(mark), run_time=0.3)
        with self.say("d3b") as d:
            self.play(Indicate(VGroup(cxl[0], cxl[1]), color=GREEN), run_time=1.0)
            self.play(Indicate(VGroup(cxl[0], cxl[3]), color=RED), run_time=1.0)
            self.play(Indicate(ok_edges, color=GOLD), run_time=1.0)
        with self.say("d4") as d:
            self.play(FadeIn(hr), FadeIn(cxr), run_time=0.8)
            bait = Circle(radius=0.68, color=GOLD, stroke_width=6).move_to(P["A"] + cr)
            hook = Line(P["A"] + cr + UP * 0.68, P["A"] + cr + UP * 1.5, color=GOLD, stroke_width=5)
            self.play(Create(bait), Create(hook), run_time=0.8)
            self.play(cxr.animate.shift(UP * 0.35), bait.animate.shift(UP * 0.35), hook.animate.shift(UP * 0.35), run_time=0.9)
            nodes_r = VGroup(*[gnode(k, br) for k in P])
            self.play(FadeIn(nodes_r), run_time=0.5)
        with self.say("d5") as d:
            spokes = VGroup(*[Line(G0["A"] + br, G0[k] + br, color=INK, stroke_width=3) for k in "BCD"])
            self.play(LaggedStart(*[Create(s) for s in spokes], lag_ratio=0.3), run_time=1.2)
            self.play(spokes[2].animate.set_color(RED).set_stroke(width=5), Indicate(nodes_r[3], color=RED), run_time=1.0)
            why = T("A 与 D 并不接触", 22, RED).next_to(spokes[2], DOWN, buff=0.5)
            self.play(FadeIn(why), run_time=0.6)
        with self.say("d5b") as d:
            self.play(Indicate(ok_edges, color=GOLD), Indicate(spokes, color=GOLD), run_time=1.4)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.8)
        # scale & incompleteness
        G = sf_graph(160, 2.3, seed=41, kmax=24)
        pos = fit(nx.kamada_kawai_layout(G), (-6.4, -0.6, -3.2, 2.9))
        net = NetView(G, pos, color=BLUE, eo=0.4, rmin=0.035, rk=0.015)
        with self.say("d6") as d:
            self.play(FadeIn(net.group), run_time=1.2)
            c1 = counter("蛋白编码基因", "约 2 万", INK).move_to(RIGHT * 2.0 + UP * 2.2)
            c2 = counter("已整理的相互作用", "14 万+", BLUE).move_to(RIGHT * 5.0 + UP * 2.2)
            self.play(FadeIn(c1, shift=UP * 0.2), run_time=0.7)
            self.play(FadeIn(c2, shift=UP * 0.2), run_time=0.7)
        rng = random.Random(5)
        nodes = list(G)
        miss = []
        while len(miss) < 90:
            u, v = rng.sample(nodes, 2)
            if not G.has_edge(u, v) and np.linalg.norm(pos[u] - pos[v]) < 1.6:
                miss.append(DashedLine(pos[u], pos[v], color=GOLD, stroke_width=1.6, dash_length=0.06).set_opacity(0.8))
        with self.say("d7") as d:
            self.play(LaggedStart(*[Create(m) for m in miss[:40]], lag_ratio=0.02), run_time=d * 0.35)
        with self.say("d7b") as d:
            self.play(LaggedStart(*[Create(m) for m in miss[40:]], lag_ratio=0.02), run_time=1.2)
            ax = axes([0, 2.6, 1], [0, 5, 1], 4.4, 3.0).move_to(RIGHT * 3.5 + DOWN * 1.2)
            u = ax.c2p(0, 1)[1] - ax.c2p(0, 0)[1]
            b1 = Rectangle(width=1.0, height=u * 1, fill_color=MUTED, fill_opacity=0.9, stroke_width=0).move_to(ax.c2p(0.7, 0), aligned_edge=DOWN)
            b2 = Rectangle(width=1.0, height=u * 4, fill_color=GOLD, fill_opacity=0.9, stroke_width=0).move_to(ax.c2p(1.9, 0), aligned_edge=DOWN)
            l1 = T("此前整理", 20, MUTED).next_to(b1, DOWN, buff=0.15)
            l2 = T("2020 年图谱", 20, GOLD).next_to(b2, DOWN, buff=0.15)
            v2 = T("约 5.3 万 · 4 倍", 24, GOLD, weight=BOLD).next_to(b2, UP, buff=0.12)
            self.play(Create(ax.x_axis), GrowFromEdge(b1, DOWN), FadeIn(l1), run_time=0.8)
            self.play(GrowFromEdge(b2, DOWN), FadeIn(l2), run_time=1.0)
            self.play(FadeIn(v2), run_time=0.5)
        fade_all(self)

    # ------------------------------------------------------------------ study bias
    def bias(self):
        tag = self.chapter("一  数据：研究偏倚")
        N = 130
        G = nx.gnm_random_graph(N, 3 * N, seed=8)
        rng = np.random.default_rng(3)
        att = np.exp(rng.normal(0, 1.0, N))
        c = 0.35
        det = {e: rng.random() < 1 - np.exp(-c * att[e[0]] * att[e[1]]) for e in G.edges()}
        Gobs = nx.Graph(); Gobs.add_nodes_from(G); Gobs.add_edges_from([e for e, k in det.items() if k])
        pos = fit(nx.kamada_kawai_layout(G), (-6.6, -0.8, -3.2, 2.9))
        heat = np.clip((np.log(att) + 1.6) / 3.2, 0, 1)
        colr = {v: interpolate_color(ManimColor("#3a4560"), ManimColor(GOLD), heat[v]) for v in G}
        dots = {v: Dot(pos[v], radius=0.07, color=colr[v]) for v in G}
        lines = {e: Line(pos[e[0]], pos[e[1]], stroke_width=1.2, color=MUTED, stroke_opacity=0.35) for e in G.edges()}
        with self.say("b1") as d:
            self.play(FadeIn(tag), run_time=0.6)
            hot = T("热门基因", 30, GOLD, weight=BOLD).move_to(RIGHT * 3.4 + UP * 1.0)
            papers = VGroup(*[Rectangle(width=0.35, height=0.45, color=INK, stroke_width=1.5, fill_color=PANEL, fill_opacity=1) for _ in range(9)])
            papers.arrange_in_grid(3, 3, buff=0.08).next_to(hot, DOWN, buff=0.3)
            self.play(FadeIn(hot), LaggedStart(*[FadeIn(p, shift=DOWN * 0.2) for p in papers], lag_ratio=0.1), run_time=d * 0.5)
        with self.say("b2") as d:
            self.play(FadeOut(hot), FadeOut(papers), run_time=0.5)
            self.play(LaggedStart(*[GrowFromCenter(x) for x in dots.values()], lag_ratio=0.01),
                      LaggedStart(*[Create(l) for l in lines.values()], lag_ratio=0.002), run_time=d * 0.55)
        with self.say("b3") as d:
            self.play(*[l.animate.set_stroke(opacity=0.04) for e, l in lines.items() if not det[e]],
                      *[l.animate.set_stroke(GOLD, opacity=0.7, width=1.6) for e, l in lines.items() if det[e]], run_time=d * 0.5)
            self.play(*[dots[v].animate.scale(0.6 + 0.25 * np.sqrt(Gobs.degree(v))) for v in G], run_time=d * 0.3)
        kt = np.array([G.degree(v) for v in range(N)]); ko = np.array([Gobs.degree(v) for v in range(N)])
        from scipy.stats import spearmanr
        rho_t, rho_o = spearmanr(att, kt)[0], spearmanr(att, ko)[0]
        ax = axes([0, 5.5, 1], [0, 16, 4], 5.0, 4.0, ynums=[0, 4, 8, 12, 16]).move_to(RIGHT * 3.9 + DOWN * 0.6)
        xl, yl = xlabel(ax, "研究热度（对数）"), ylabel(ax, "度")
        with self.say("b4") as d:
            self.play(Create(ax), FadeIn(xl), FadeIn(yl), run_time=0.8)
            pt = VGroup(*[Dot(ax.c2p(np.log(att[v]) + 2.5, kt[v]), radius=0.045, color=MUTED).set_opacity(0.7) for v in range(N)])
            po = VGroup(*[Dot(ax.c2p(np.log(att[v]) + 2.5, ko[v]), radius=0.05, color=GOLD) for v in range(N)])
            lt = T(f"真实度  ρ = {rho_t:.2f}", 22, MUTED).next_to(ax, UP, buff=0.45).align_to(ax, LEFT).shift(RIGHT * 0.4)
            lo = T(f"观测度  ρ = {rho_o:.2f}", 22, GOLD).next_to(lt, DOWN, buff=0.15).align_to(lt, LEFT)
            self.play(LaggedStart(*[FadeIn(p) for p in pt], lag_ratio=0.005), FadeIn(lt), run_time=d * 0.3)
        with self.say("b5") as d:
            self.play(LaggedStart(*[TransformFromCopy(a, b) for a, b in zip(pt, po)], lag_ratio=0.005), FadeIn(lo), run_time=d * 0.45)
        with self.say("b6") as d:
            self.play(*[m.animate.fade(0.85) for m in list(dots.values()) + list(lines.values())], run_time=0.8)
            warn = T("度高 ≠ 更重要", 34, RED, weight=BOLD).move_to(LEFT * 3.7 + UP * 0.0)
            self.play(Write(warn), run_time=1.0)
        fade_all(self)

    # ------------------------------------------------------------------ hubs & lethality
    def lethality(self):
        tag = self.chapter("二  结构：枢纽与致死")
        G = sf_graph(110, 2.3, seed=17, kmax=22)
        net = NetView(G, fit(nx.kamada_kawai_layout(G), (-6.4, 6.4, -3.1, 2.9)), color=GREEN, eo=0.35)
        with self.say("e1") as d:
            self.play(FadeIn(tag), FadeIn(net.group), run_time=1.2)
            yl = T("酵母  1870 个蛋白", 26, MUTED).to_corner(UR, buff=0.5)
            self.play(FadeIn(yl), run_time=0.6)
        with self.say("e1b") as d:
            ess = [v for v in sorted(G, key=G.degree, reverse=True)[:12]]
            self.play(*[net.dots[v].animate.set_color(RED) for v in ess], run_time=1.0)
            el = T("红色：必需基因", 24, RED).next_to(yl, DOWN, buff=0.2).align_to(yl, RIGHT)
            self.play(FadeIn(el), run_time=0.5)
        w1, w2 = waffle(21), waffle(62)
        w1.move_to(LEFT * 3.3 + DOWN * 0.3); w2.move_to(RIGHT * 3.3 + DOWN * 0.3)
        t1 = T("≤ 5 个伙伴", 28, INK).next_to(w1, UP, buff=0.35)
        t2 = T("> 15 个伙伴", 28, INK).next_to(w2, UP, buff=0.35)
        s1 = T("必需  21%", 30, RED, weight=BOLD).next_to(w1, DOWN, buff=0.3)
        s2 = T("必需  62%", 30, RED, weight=BOLD).next_to(w2, DOWN, buff=0.3)
        with self.say("e2") as d:
            self.play(FadeOut(net.group), FadeOut(yl), FadeOut(el), run_time=0.6)
            self.play(FadeIn(t1), LaggedStart(*[GrowFromCenter(x) for x in w1], lag_ratio=0.01), run_time=1.2)
            self.play(FadeIn(s1), run_time=0.6)
        with self.say("e3") as d:
            self.play(FadeIn(t2), LaggedStart(*[GrowFromCenter(x) for x in w2], lag_ratio=0.01), run_time=1.2)
            self.play(FadeIn(s2), run_time=0.6)
            self.play(Indicate(s2, color=RED), run_time=0.8)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.6)
        # explanation 1: fragmentation
        G2 = sf_graph(70, 2.2, seed=23, kmax=16)
        n2 = NetView(G2, fit(nx.kamada_kawai_layout(G2), (-6.0, 0.0, -2.9, 2.6)), color=GREEN, eo=0.4)
        l1 = chip("网络碎裂", GREEN).move_to(RIGHT * 3.4 + UP * 2.0)
        with self.say("e4") as d:
            self.play(FadeIn(n2.group), FadeIn(l1), run_time=0.9)
            hubs = sorted(G2, key=G2.degree, reverse=True)[:3]
            self.play(*n2.flash(hubs), run_time=0.5)
            self.play(*n2.state(hubs, hl=GREEN), run_time=1.2)
        # explanation 2: essential interaction
        with self.say("e5") as d:
            self.play(FadeOut(n2.group), run_time=0.5)
            hub = Dot(LEFT * 3.0, radius=0.22, color=GREEN)
            ang = np.linspace(0, 2 * PI, 13)[:-1]
            leaves = VGroup(*[Dot(LEFT * 3.0 + 1.9 * np.array([np.cos(a), np.sin(a), 0]), radius=0.1, color=GREEN) for a in ang])
            sp = VGroup(*[Line(hub.get_center(), l.get_center(), color=GREEN, stroke_width=2, stroke_opacity=0.6) for l in leaves])
            l2 = chip("必需相互作用", RED).move_to(RIGHT * 3.4 + UP * 0.6)
            self.play(FadeIn(sp), FadeIn(leaves), FadeIn(hub), FadeIn(l2), run_time=1.0)
            self.play(sp[4].animate.set_stroke(RED, width=6, opacity=1), leaves[4].animate.set_color(RED), run_time=0.8)
            self.play(Flash(sp[4].get_center(), color=RED), run_time=0.7)
        star = VGroup(hub, leaves, sp)
        # explanation 3: essential complexes
        with self.say("e6") as d:
            self.play(FadeOut(star), run_time=0.5)
            rng = np.random.default_rng(1)
            big = [LEFT * 3.4 + UP * 0.2 + 1.3 * np.array([np.cos(a), np.sin(a), 0]) * rng.uniform(0.3, 1) for a in np.linspace(0, 2 * PI, 11)[:-1]]
            bigd = VGroup(*[Dot(p, radius=0.11, color=RED) for p in big])
            bige = VGroup(*[Line(big[i], big[j], color=RED, stroke_width=1.6, stroke_opacity=0.5) for i in range(10) for j in range(i + 1, 10) if rng.random() < 0.7])
            smalls = VGroup()
            for c in (LEFT * 5.8 + DOWN * 2.2, LEFT * 1.2 + DOWN * 2.3, LEFT * 1.0 + UP * 2.3):
                ps = [c + 0.45 * np.array([np.cos(a), np.sin(a), 0]) for a in np.linspace(0, 2 * PI, 4)[:-1]]
                smalls.add(*[Line(ps[i], ps[(i + 1) % 3], color=MUTED, stroke_width=1.6) for i in range(3)], *[Dot(p, radius=0.1, color=MUTED) for p in ps])
            l3 = chip("必需复合物", GOLD).move_to(RIGHT * 3.4 + DOWN * 0.8)
            bl = T("核糖体这类复合物", 22, RED).next_to(bigd, UP, buff=0.25)
            self.play(Create(bige), FadeIn(bigd), FadeIn(bl), FadeIn(smalls), FadeIn(l3), run_time=1.4)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.6)
        clip_line(self, "e6b", "yt_ribosome_wehi.mp4", "视频：WEHI · YouTube", start=5)
        # simulation: essentiality decided by complex
        rng = np.random.default_rng(7)
        deg, ess, cess = [], [], []
        for _ in range(500):
            s = int(rng.integers(3, 26))
            ce = rng.random() < s / 30
            for _ in range(s):
                deg.append(rng.binomial(s - 1, 0.6) + rng.poisson(1.0))
                ess.append(rng.random() < (0.85 if ce else 0.06)); cess.append(ce)
        deg, ess, cess = map(np.array, (deg, ess, cess))
        bins = [(0, 4), (5, 9), (10, 14), (15, 99)]
        names = ["0–4", "5–9", "10–14", "≥15"]

        def frac(mask):
            return [ess[mask & (deg >= a) & (deg <= b)].mean() for a, b in bins]
        allf, ef, nf = frac(np.ones_like(ess)), frac(cess), frac(~cess)
        ax = axes([0, 4, 1], [0, 1, 0.5], 7.5, 4.2, ynums=[0, 0.5, 1]).move_to(DOWN * 0.3 + RIGHT * 0.3)
        xl, yl = xlabel(ax, "度"), ylabel(ax, "必需蛋白比例")
        ticks = VGroup(*[T(n, 22, MUTED).next_to(ax.c2p(i + 0.5, 0), DOWN, buff=0.15) for i, n in enumerate(names)])
        xl.next_to(ticks, DOWN, buff=0.15)
        with self.say("e7") as d:
            self.play(Create(ax), FadeIn(xl), FadeIn(yl), FadeIn(ticks), run_time=1.0)
            u = ax.c2p(0, 1)[1] - ax.c2p(0, 0)[1]
            bars = VGroup(*[Rectangle(width=1.2, height=u * f, fill_color=BLUE, fill_opacity=0.8, stroke_width=0).move_to(ax.c2p(i + 0.5, 0), aligned_edge=DOWN) for i, f in enumerate(allf)])
        with self.say("e7b") as d:
            self.play(grow_bars(bars, d * 0.5))
        with self.say("e8") as d:
            self.play(bars.animate.set_opacity(0.2), run_time=0.6)
            xs = [i + 0.5 for i in range(4)]
            le = ax.plot_line_graph(xs, ef, line_color=RED, vertex_dot_radius=0.08, vertex_dot_style={"color": RED}, stroke_width=5)
            ln = ax.plot_line_graph(xs, nf, line_color=MUTED, vertex_dot_radius=0.08, vertex_dot_style={"color": MUTED}, stroke_width=5)
            tl = T("必需复合物的成员", 22, RED).next_to(ax.c2p(4, ef[-1]), RIGHT, buff=0.1).shift(UP * 0.25)
            tn = T("其他复合物的成员", 22, MUTED).next_to(ax.c2p(4, nf[-1]), RIGHT, buff=0.1).shift(UP * 0.25)
            if tl.get_right()[0] > 7: tl.shift(LEFT * (tl.get_right()[0] - 6.9)); tn.shift(LEFT * (tn.get_right()[0] - 6.9))
            self.play(Create(le), FadeIn(tl), run_time=d * 0.3)
            self.play(Create(ln), FadeIn(tn), run_time=d * 0.3)
        with self.say("e9") as d:
            grp = VGroup(ax, xl, yl, ticks, bars, le, ln, tl, tn)
            self.play(grp.animate.fade(0.85), run_time=0.6)
            row = VGroup(chip("网络碎裂", GREEN), chip("必需相互作用", RED), chip("必需复合物", GOLD)).arrange(RIGHT, buff=0.5).move_to(UP * 0.6)
            q = T("相关  ≠  机制", 40, INK, weight=BOLD).next_to(row, DOWN, buff=0.7)
            self.play(LaggedStart(*[FadeIn(r, shift=UP * 0.2) for r in row], lag_ratio=0.3), run_time=1.4)
            self.play(Write(q), run_time=1.0)
        fade_all(self)

    # ------------------------------------------------------------------ diseasome
    def diseasome(self):
        tag = self.chapter("二  结构：疾病基因在哪里")
        cls = [GOLD] * 3 + [VIOLET] * 3 + [BLUE] * 3
        genes = 11
        links = [(0, 0), (0, 1), (1, 1), (1, 2), (2, 2), (2, 0), (3, 4), (3, 5), (4, 5), (4, 6), (5, 6), (6, 7), (7, 8), (7, 9),
                 (8, 9), (8, 10), (2, 4), (5, 7)]
        dpos = [np.array([-4.2, 2.1 - 0.58 * i, 0]) for i in range(9)]
        gpos = [np.array([0.0, 2.3 - 0.48 * j, 0]) for j in range(genes)]
        dd = VGroup(*[Dot(p, radius=0.17, color=c) for p, c in zip(dpos, cls)])
        gg = VGroup(*[Square(side_length=0.24, color=INK, fill_opacity=0.8).move_to(p) for p in gpos])
        ee = VGroup(*[Line(dpos[i], gpos[j], color=MUTED, stroke_width=1.6, stroke_opacity=0.6) for i, j in links])
        hd, hg = T("疾病", 26, INK).next_to(dd, UP, buff=0.25), T("基因", 26, INK).next_to(gg, UP, buff=0.25).align_to(T("疾病", 26).next_to(dd, UP, buff=0.25), UP)
        legend = VGroup(*[VGroup(Dot(radius=0.1, color=c), T(s, 22, INK)).arrange(RIGHT, buff=0.15)
                          for c, s in ((GOLD, "癌症"), (VIOLET, "神经系统疾病"), (BLUE, "代谢疾病"))]).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        legend.to_corner(UR, buff=0.5).shift(DOWN * 0.5)
        with self.say("g1") as d:
            self.play(FadeIn(tag), run_time=0.5)
            self.play(FadeIn(dd), FadeIn(hd), FadeIn(gg), FadeIn(hg), FadeIn(legend), run_time=1.0)
        with self.say("g1b") as d:
            self.play(Indicate(dd, scale_factor=1.05), run_time=0.8)
            self.play(Indicate(gg, scale_factor=1.05), run_time=0.8)
            self.play(LaggedStart(*[Create(e) for e in ee], lag_ratio=0.08), run_time=d * 0.35)
            nums = VGroup(T("1284 种疾病", 22, MUTED).next_to(dd, DOWN, buff=0.25), T("1777 个基因", 22, MUTED).next_to(gg, DOWN, buff=0.25))
            self.play(FadeIn(nums), run_time=0.5)
        # projection
        P = nx.Graph(); P.add_nodes_from(range(9))
        for j in range(genes):
            ds = [i for i, g in links if g == j]
            P.add_edges_from((a, b) for k, a in enumerate(ds) for b in ds[k + 1:])
        ppos = fit(nx.spring_layout(P, seed=2, k=0.9), (-2.0, 3.4, -2.6, 2.4))
        pe = VGroup(*[Line(ppos[a], ppos[b], color=INK, stroke_width=3, stroke_opacity=0.7) for a, b in P.edges()])
        with self.say("g2") as d:
            self.play(FadeOut(gg), FadeOut(hg), FadeOut(ee), FadeOut(nums), FadeOut(hd), run_time=0.8)
            self.play(*[dd[i].animate.move_to(ppos[i]) for i in range(9)], run_time=1.4)
            self.play(LaggedStart(*[Create(e) for e in pe], lag_ratio=0.1), run_time=d * 0.3)
            ring = Circle(radius=1.0, color=GOLD, stroke_width=3).move_to(np.mean([ppos[i] for i in range(3)], axis=0))
            self.play(Create(ring), run_time=0.8)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.6)
        # core-periphery picture
        G = sf_graph(150, 2.2, seed=29, kmax=30)
        order = sorted(G, key=G.degree, reverse=True)
        rng = np.random.default_rng(2)
        pos = {}
        for r, v in enumerate(order):
            rad = 0.35 + 3.0 * np.sqrt(r / len(order))
            a = rng.uniform(0, 2 * PI)
            pos[v] = np.array([rad * np.cos(a) * 1.25, rad * np.sin(a), 0]) + LEFT * 1.6 + DOWN * 0.3
        net = NetView(G, pos, color=MUTED, eo=0.18, rmin=0.04, rk=0.018)
        essential = order[:12]
        disease = [v for v in order[60:] if rng.random() < 0.3][:22]
        cancer = order[8:22:2]
        lg = VGroup(*[VGroup(Dot(radius=0.1, color=c), T(s, 22, INK)).arrange(RIGHT, buff=0.15)
                      for c, s in ((RED, "必需基因"), (BLUE, "遗传病基因"), (GOLD, "癌症基因"))]).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        lg.to_corner(UR, buff=0.6).shift(DOWN * 0.6)
        with self.say("g3") as d:
            self.play(FadeIn(net.group), run_time=1.0)
            self.play(*[net.dots[v].animate.set_color(RED) for v in essential], FadeIn(lg[0]), run_time=0.9)
        with self.say("g3b") as d:
            self.play(*[net.dots[v].animate.set_color(BLUE).scale(1.3) for v in disease], FadeIn(lg[1]), run_time=0.9)
        with self.say("g4") as d:
            h = essential[0]
            x = Cross(net.dots[h], stroke_color=RED, scale_factor=2.2)
            lab = T("胚胎期致死", 26, RED, weight=BOLD).next_to(lg, DOWN, buff=0.6)
            self.play(Create(x), Flash(net.dots[h], color=RED), FadeIn(lab), run_time=1.2)
        with self.say("g5") as d:
            self.play(FadeOut(x), FadeOut(lab), *[net.dots[v].animate.set_color(GOLD).scale(1.3) for v in cancer], FadeIn(lg[2]), run_time=1.2)
            self.play(*[Indicate(net.dots[v], color=GOLD) for v in cancer], run_time=1.0)
        fade_all(self)

    # ------------------------------------------------------------------ motifs
    def motifs(self):
        tag = self.chapter("三  功能：网络基序")
        # the FFL pattern
        X, Y, Z = UP * 1.4, DOWN * 0.2 + RIGHT * 1.4, DOWN * 1.8
        nd = {k: VGroup(Circle(radius=0.38, color=GOLD, fill_opacity=0.3, stroke_width=3), T(k, 30)).move_to(p) for k, p in (("X", X), ("Y", Y), ("Z", Z))}
        a1, a2, a3 = arrow(X, Y, INK, buff=0.45), arrow(Y, Z, INK, buff=0.45), arrow(X, Z, INK, buff=0.45)
        with self.say("m1") as d:
            self.play(FadeIn(tag), run_time=0.5)
            self.play(*[GrowFromCenter(v) for v in nd.values()], run_time=1.0)
        with self.say("m2") as d:
            self.play(GrowArrow(a1), run_time=0.7)
            self.play(GrowArrow(a2), GrowArrow(a3), run_time=0.9)
            nm = T("前馈环", 34, GOLD, weight=BOLD).next_to(VGroup(*nd.values()), RIGHT, buff=1.0)
            self.play(FadeIn(nm), run_time=0.6)
        motif = VGroup(*nd.values(), a1, a2, a3, nm)
        self.play(motif.animate.scale(0.45).move_to(RIGHT * 5.6 + UP * 2.3), run_time=0.8)
        # real directed network with planted FFLs
        G = motif_graph()
        real = ffls(G)
        pos = fit(nx.kamada_kawai_layout(G.to_undirected()), (-6.4, -0.8, -3.2, 2.8))
        dots = {v: Dot(pos[v], radius=0.07 if v >= 20 else 0.1, color=GOLD if v < 20 else BLUE) for v in G}
        def edge_line(u, v, color=MUTED, op=0.55):
            return Arrow(pos[u], pos[v], buff=0.09, stroke_width=1.6, color=color, tip_length=0.1,
                         max_tip_length_to_length_ratio=0.3, max_stroke_width_to_length_ratio=20).set_opacity(op)
        edges = {e: edge_line(*e) for e in G.edges()}
        lg = VGroup(VGroup(Dot(radius=0.1, color=GOLD), T("转录因子", 22)).arrange(RIGHT, buff=0.15),
                    VGroup(Dot(radius=0.07, color=BLUE), T("靶基因", 22)).arrange(RIGHT, buff=0.15)).arrange(DOWN, aligned_edge=LEFT).move_to(LEFT * 5.7 + DOWN * 3.3)
        with self.say("m3") as d:
            self.play(FadeIn(VGroup(*edges.values())), LaggedStart(*[GrowFromCenter(x) for x in dots.values()], lag_ratio=0.01), FadeIn(lg), run_time=d * 0.4)
            hl = set(e for x, y, z in real for e in ((x, y), (y, z), (x, z)))
            self.play(*[edges[e].animate.set_color(GOLD).set_opacity(1) for e in hl], run_time=1.0)
            c_real = counter("真实网络中的前馈环", str(len(real)), GOLD).move_to(RIGHT * 2.2 + UP * 2.3)
            self.play(FadeIn(c_real), run_time=0.6)
        with self.say("m3b") as d:
            hubs_ = sorted(G, key=G.out_degree, reverse=True)[:4]
            self.play(*[Indicate(dots[h], color=GOLD, scale_factor=2.0) for h in hubs_], run_time=1.2)
        with self.say("m4") as d:
            self.play(*[edges[e].animate.set_color(MUTED).set_opacity(0.55) for e in hl], run_time=0.5)
            rng = random.Random(1)
            H = G.copy(); E = list(H.edges())
            for _ in range(3):
                (a, b), (c, dd_), (n1, n2), (n3, n4) = swap_once(H, E, rng)
                e1, e2 = edges.pop((a, b)), edges.pop((c, dd_))
                ne1, ne2 = edge_line(a, dd_, RED, 1), edge_line(c, b, RED, 1)
                self.play(e1.animate.set_color(RED).set_opacity(1), e2.animate.set_color(RED).set_opacity(1), run_time=0.35)
                self.play(Transform(e1, ne1), Transform(e2, ne2), run_time=0.7)
                self.play(e1.animate.set_color(MUTED).set_opacity(0.55), e2.animate.set_color(MUTED).set_opacity(0.55), run_time=0.3)
                edges[(a, dd_)], edges[(c, b)] = e1, e2
        rng = random.Random(1)
        rs = [len(ffls(randomize(G, 600, rng))) for _ in range(200)]
        mu, sd = np.mean(rs), np.std(rs)
        z = (len(real) - mu) / sd
        ax = axes([0, 14, 2], [0, 70, 20], 5.4, 3.0, xnums=[0, 4, 8, 12], fs=20).move_to(RIGHT * 3.4 + DOWN * 1.6)
        xl = xlabel(ax, "前馈环数量", 20, 0.3)
        bars, cnt = hist_bars(ax, rs, np.arange(-0.5, 14.5, 1), MUTED)
        with self.say("m5") as d:
            self.play(Create(ax), FadeIn(xl), run_time=0.8)
            self.play(grow_bars(bars, d * 0.4))
        with self.say("m6") as d:
            rl = Line(ax.c2p(len(real), 0), ax.c2p(len(real), 62), color=GOLD, stroke_width=5)
            self.play(Create(rl), run_time=0.8)
        with self.say("m6b") as d:
            zf = MathTex(r"Z=\frac{N_{\mathrm{real}}-\langle N_{\mathrm{rand}}\rangle}{\sigma_{\mathrm{rand}}}", font_size=34, color=INK).move_to(RIGHT * 3.0 + UP * 0.55)
            self.play(Write(zf), run_time=d * 0.3)
            zv = MathTex(rf"\approx {z:.1f}", font_size=40, color=GOLD).next_to(zf, RIGHT, buff=0.15)
            if zv.get_right()[0] > 6.9:
                VGroup(zf, zv).shift(LEFT * (zv.get_right()[0] - 6.9))
            num = callout(zf[0][2:-6], "真实 − 随机平均", UP, GOLD, 18, 0.08)
            den = callout(zf[0][-5:], "随机的标准差", DOWN, BLUE, 18, 0.08)
            self.play(Create(num), run_time=0.8)
            self.play(Create(den), run_time=0.8)
        with self.say("m6c") as d:
            self.play(FadeOut(num), FadeOut(den), run_time=0.4)
            self.play(FadeIn(zv), Indicate(rl, color=GOLD), run_time=1.0)
        print("MOTIF_Z", z)
        with self.say("m7") as d:
            self.play(*[m.animate.fade(0.85) for m in list(edges.values()) + list(dots.values())], run_time=0.6)
            word = T("网络基序", 54, GOLD, weight=BOLD).move_to(LEFT * 3.6)
            self.play(Write(word), run_time=1.0)
        fade_all(self)

    # ------------------------------------------------------------------ FFL as persistence detector
    def ffl(self):
        tag = self.chapter("三  功能：前馈环")
        X, Y, Z = LEFT * 5.0 + UP * 1.6, LEFT * 3.6 + UP * 0.0, LEFT * 5.0 + DOWN * 1.6
        cX, cY, cZ = GOLD, VIOLET, GREEN
        nd = {k: VGroup(Circle(radius=0.38, color=c, fill_opacity=0.3, stroke_width=3), T(k, 30)).move_to(p)
              for k, p, c in (("X", X, cX), ("Y", Y, cY), ("Z", Z, cZ))}
        a1, a2, a3 = arrow(X, Y, INK, buff=0.45), arrow(Y, Z, INK, buff=0.45), arrow(X, Z, INK, buff=0.45)
        gate = T("X 且 Y", 24, INK).next_to(nd["Z"], DOWN, buff=0.25)
        t, Xs, Ys, Zs = self.sim
        axs = [axes([0, 12, 2], [0, 1.2, 1], 8.0, 1.25).move_to(RIGHT * 2.3 + UP * (2.0 - 1.85 * i)) for i in range(3)]
        labs = VGroup(*[T(s, 24, c).next_to(a, LEFT, buff=0.25) for s, c, a in (("X", cX, axs[0]), ("Y", cY, axs[1]), ("Z", cZ, axs[2]))])
        thr = DashedLine(axs[1].c2p(0, 0.5), axs[1].c2p(12, 0.5), color=RED, stroke_width=2.5)
        thl = T("阈值", 20, RED).next_to(thr, RIGHT, buff=0.1)
        with self.say("f1") as d:
            self.play(FadeIn(tag), *[GrowFromCenter(v) for v in nd.values()], run_time=1.0)
            self.play(GrowArrow(a1), GrowArrow(a2), GrowArrow(a3), FadeIn(gate), run_time=1.0)
        with self.say("f1b") as d:
            self.play(*[Create(a) for a in axs], FadeIn(labs), run_time=1.0)
            self.play(Create(thr), FadeIn(thl), run_time=0.8)
        def tr(i, y, lo, hi, c):
            return self.trace(axs[i], t, y, lo, hi, c)
        with self.say("f2") as d:
            parts = [tr(0, Xs, 4, 12, cX), tr(1, Ys, 4, 12, cY), tr(2, Zs, 4, 12, cZ)]
            self.play(*[Create(p) for p in parts], run_time=d * 0.7, rate_func=linear)
            tc = 5.0 + np.log(2)
            dl = DashedLine(axs[1].c2p(tc, 0.5), axs[2].c2p(tc, 0), color=MUTED, stroke_width=2)
            dlab = T("延迟", 20, MUTED).next_to(axs[2].c2p(5.3, 0.0), DOWN, buff=0.1)
            self.play(Create(dl), FadeIn(dlab), run_time=0.6)
        with self.say("f3") as d:
            sp = [tr(0, Xs, 0, 4, cX), tr(1, Ys, 0, 4, cY), tr(2, Zs, 0, 4, cZ)]
            self.play(*[Create(p) for p in sp], run_time=d * 0.45, rate_func=linear)
            no = T("未越过阈值", 20, RED).next_to(axs[1].c2p(1.4, 0.45), UP, buff=0.05)
            self.play(FadeIn(no), Indicate(sp[2], color=RED), run_time=1.0)
        with self.say("f4") as d:
            filt = T("持续性检测器", 40, GOLD, weight=BOLD).move_to(LEFT * 4.4 + DOWN * 3.1)
            self.play(Write(filt), run_time=1.2)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.6)
        with self.say("f7") as d:
            q = T("结构  ≠  功能", 48, INK, weight=BOLD)
            self.play(Write(q), run_time=1.0)
        fade_all(self)

    # ------------------------------------------------------------------ recap
    def recap(self):
        with self.say("r1") as d:
            head = T("三个要点", 40, INK, weight=BOLD).to_edge(UP, buff=0.7)
            self.play(Write(head), run_time=0.8)
        items = [("r2", BLUE, "边的含义取决于测量方法，还带着研究偏倚"),
                 ("r3", GOLD, "枢纽与致死：相关稳健，机制有争议"),
                 ("r4", GREEN, "基序是电路元件：前馈环过滤噪声")]
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
            self.clip_on("ffl_demo.mp4", "full", "本站交互演示：前馈环的滤波作用", start=0.3)
            if d < 16.5:
                self.wait(16.5 - d)
        self.clip_off()
        self.wait(1.0)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=1.0)
