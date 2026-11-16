"""Paper explainer: Pastor-Satorras & Vespignani 2001, epidemic spreading in scale-free networks."""
import networkx as nx
import numpy as np

from paperhelp import *  # noqa: F401,F403

TITLE = "无标度网络上的流行病：阈值为何消失"
LINES = {
    # hook
    "h1": "先看这张图。横轴是有效传染率，就是病原体传给别人的速度，和病人痊愈的速度之比。纵轴是长时间以后，人群中还有多少人处在感染状态。",
    "h1b": "经典流行病学有一条铁律：每种传染病，都有一个阈值，就是这条红色虚线。",
    "h2": "传染率高于阈值，感染扩散开来，长期存在，就是黄色曲线往上走的部分。低于阈值，感染很快消失。",
    "h3": "这也是接种疫苗的理论基础：只要把有效传染率，压到阈值以下就行。",
    "h4": "可是，计算机病毒的数据却不是这样。它们长期在极低的水平上流行，既不爆发，也不消亡，就是底下这条紫色的带子。",
    "h5": "按经典理论，这就要求每种病毒的传染率，都恰好卡在阈值上方一点点，也就是红色这条窄缝。这几乎不可能。",
    "h6": "【慢】2001年，两位物理学家在一篇论文里，给出了另一种解释。",
    "q0": "这一期分三部分来讲。",
    "q1": "第一部分，计算机病毒的谜题，和论文用到的传播模型。",
    "q2": "第二部分，模拟实验，以及按度分组的计算，看阈值为什么会消失。",
    "q3": "第三部分，这对接种策略意味着什么，最后说说局限。",
    # virus data
    "v1": "先看第一部分。作者分析了1996年到2000年间报告的病毒流行数据，计算每类病毒在一段时间后，仍然存活的概率。",
    "v2": "这张示意图，横轴是月份，纵轴是存活概率。最初两个月急剧下降，之后呈指数式的长尾。引导区病毒和宏病毒的特征寿命，大约是十四个月。",
    "v3": "这远远长于杀毒软件发布所需的时间。作者注意到，病毒多靠电子邮件传播，接触结构接近互联网，而互联网的度分布是重尾的，少数节点连接极多。",
    "v3b": "画面里，是那个年代一次著名的电子邮件病毒事件的报道。",
    # SIS
    "m1": "作者用的模型，叫易感、感染、再易感。左边是易感，右边是感染。感染的节点痊愈之后，又会重新变成易感。",
    "m2": "每一步，感染者以速率纽传给邻居，以速率德尔塔痊愈。两者之比，就是有效传染率，写作兰姆达。",
    "n0": "我们先把几个名词说清楚。",
    "n1": "有效传染率兰姆达：传染速率除以痊愈速率。",
    "n2": "流行率：长时间以后，处在感染状态的节点比例。",
    "n3": "流行病阈值：流行率从零变成正数的那个传染率。",
    # experiment
    "e1": "下面进入第二部分，我们来做个实验。两张网络都是两万个节点、平均度都是六。左边每个节点的度都一样；右边是无标度网络，少数节点连接极多。",
    "e2": "横轴是有效传染率，纵轴是流行率，也就是长时间以后，仍处在感染状态的节点比例。",
    "e3": "灰色的点，是度都一样的网络。它有一个清楚的阈值：传染率低于这条虚线，感染全部灭绝。",
    "e4": "红色的点，是无标度网络。在虚线左边，传染率已经低了一大截，感染依然存活，只是流行率越来越低。",
    "e5": "原文在最多八百五十万个节点的网络上模拟。流行率随传染率减小，呈指数式衰减，却始终没有出现有限的阈值。",
    # heterogeneous mean field
    "g1": "这背后的原因，作者是这样算的：把度相同的节点归为一组，分别追踪每一组的感染比例。左边每一列是一组，红点是被感染的。",
    "g2": "每一组感染比例的变化，可以写成这个式子。",
    "g2b": "右边第一项，减去肉k，是痊愈的人。第二项是新感染：度k越大、传染率越高、还没被感染的越多，新感染就越多。最后的西塔，是一条边指向感染者的概率。",
    "g3": "西塔怎么算，就是下面这个式子。",
    "g3b": "它的意思是：沿着一条边走过去，碰到度为k的节点，概率正比于k乘以这类节点的占比。所以连接越多的枢纽，越容易被碰到。",
    "g4": "稳态时，度越大的组，感染比例越高。这张柱状图，是刚才模拟里每组的感染比例。枢纽被感染的比例，比只有三个邻居的节点高出十倍以上。",
    "g5": "对无标度网络解出来，流行率是这样一个指数形式。",
    "g5b": "式子里的m，是网络构造时每个新节点带来的边数。e的负的一除以m兰姆达次方，在兰姆达很小时非常小，但永远大于零。右下角这条曲线就是它。",
    "g6": "【慢】只要传染率大于零，流行率就大于零。也就是说，流行病阈值为零。",
    # hub keeps it alive
    "k1": "直观地看，中间这个大点是一个枢纽，连着很多邻居。哪怕每次传染的概率很小，总有某个邻居会把它重新感染。",
    "k2": "【慢】枢纽又把病原体传回给邻居。感染就这样围着枢纽来回打转，一直续命下去。",
    # immunization
    "i1": "最后是第三部分。随机接种疫苗，相当于随机拿掉一些节点。左边随机拿掉百分之十，剩下的网络依然高度不均。",
    "i2": "右边是另一种做法：优先给连接最多的百分之十接种。",
    "i3": "在两万个节点的模拟里，随机接种之后，流行率从百分之二十二降到百分之十八，感染还在流行。优先接种枢纽，流行率降到了零。",
    "i4": "这篇论文直接引出了目标免疫和熟人免疫等策略：找到枢纽，优先保护。性接触网络常被当作重尾接触的例子，这个思路在那里尤其重要。",
    "u1": "本站的知识页面里，有传播的交互演示。注意，它用的是更简单的易感、感染、恢复模型，恢复后不再被感染。",
    "u2": "先不免疫，感染很快扩散开来。再选择免疫度最大的百分之十五，重新开始传播，感染几乎传不出去。这和刚才的模拟是一致的。",
    # limits
    "l1": "下面说说局限。第一，阈值为零是网络无限大时的结论。真实网络是有限的，阈值是小，而不是零。有限网络的阈值，可以用这个式子估计。",
    "l1b": "分子是连接数的平均，分母是连接数平方的平均。枢纽越多，分母越大，阈值越小。对我们这张两万节点的网络，大约是零点零五。",
    "l2": "第二，按度分组，把同一度的节点看成完全一样，忽略了具体的连边。在固定的网络上，阈值约为邻接矩阵最大特征值的倒数。",
    "l3": "第三，人类接触网络是否真的无标度，还有争议。左边的性接触网络高度不均；右边日常面对面的接触，异质性要小得多。",
    # recap
    "z1": "好，我们来总结一下。",
    "z2": "第一，计算机病毒长期低水平流行，和经典阈值理论相矛盾。",
    "z3": "第二，在度分布高度异质的网络上，枢纽让流行病阈值趋于零。",
    "z4": "第三，随机接种不够，要优先保护枢纽；而真实网络的阈值是小，但不为零。",
}

DELTA = 0.5  # recovery probability per step; effective rate lambda = beta / DELTA


def sis(A, lam, steps=500, avg=200, seed=0, alive=None):
    """Discrete-time SIS on sparse adjacency A. Returns (mean prevalence over last `avg` steps, per-node infected fraction)."""
    rng = np.random.default_rng(seed)
    N = A.shape[0]
    beta = lam * DELTA
    x = rng.random(N) < 0.3
    if alive is not None:
        x &= alive
    acc = np.zeros(N)
    rho = []
    for t in range(steps):
        p = A @ x.astype(np.float32)
        inf = rng.random(N) < 1 - (1 - beta) ** p
        if alive is not None:
            inf &= alive
        rec = rng.random(N) < DELTA
        x = (x & ~rec) | (~x & inf)
        if t >= steps - avg:
            acc += x; rho.append(x.mean())
        if not x.any():
            return 0.0, acc / avg
    return float(np.mean(rho)), acc / avg


class Episode(Narrated):
    LINES = LINES

    def construct(self):
        N = 20000
        self.Gb = nx.barabasi_albert_graph(N, 3, seed=2)
        self.Gr = nx.random_regular_graph(6, N, seed=2)
        self.Ab = nx.to_scipy_sparse_array(self.Gb, format="csr", dtype=np.float32)
        self.Ar = nx.to_scipy_sparse_array(self.Gr, format="csr", dtype=np.float32)
        self.hook()
        parts(self, "q0", ["q1", "q2", "q3"], "这一期分三部分",
              ["一  病毒之谜与传播模型", "二  模拟实验与按度分组", "三  接种策略与局限"])
        self.virus()
        self.model()
        show_slide(self, ["n0", "n1", "n2", "n3"], "三个名词",
                   ["有效传染率 λ：传染速率 ÷ 痊愈速率", "流行率 ρ：长期处于感染的节点比例", "流行病阈值：ρ 从零变为正的那个 λ"])
        self.experiment()
        self.meanfield()
        self.hubs()
        self.immunize()
        clip_lines(self, "sir_demo.mp4", ["u1", "u2"], "本站交互演示：网络上的 SIR 传播", start=0.3, box="full")
        self.limits()
        recap(self, "z1", [("z2", BLUE, "病毒长期低水平流行之谜"),
                           ("z3", RED, "异质网络：阈值趋于零"),
                           ("z4", GREEN, "优先保护枢纽；有限网络阈值小而非零")])

    # ------------------------------------------------------------------ hook
    def hook(self):
        lc = 0.25
        ax = plain_axes([0, 1, 0.25], [0, 1, 0.5], 8.4, 4.6).shift(DOWN * 0.3)
        xl = xlabel("有效传染率", ax)
        yl = ylabel("长期感染比例", ax)
        cl = ax.plot(lambda x: max(0.0, 1 - lc / x) if x > 0 else 0, x_range=[0.01, 1, 0.005], color=GOLD, stroke_width=5, use_smoothing=False)
        with self.say("h1"):
            self.play(Create(ax), FadeIn(xl), FadeIn(yl), run_time=1.2)
        with self.say("h1b"):
            th = DashedLine(ax.c2p(lc, 0), ax.c2p(lc, 1), color=RED)
            tl = T("阈值", 26, RED).next_to(ax.c2p(lc, 1), UP, buff=0.1)
            self.play(Create(th), FadeIn(tl), run_time=1.0)
        with self.say("h2"):
            self.play(Create(cl), run_time=2.2, rate_func=linear)
            die = T("消亡", 26, BLUE).move_to(ax.c2p(0.12, 0.2))
            spr = T("流行", 26, GOLD).move_to(ax.c2p(0.7, 0.85))
            self.play(FadeIn(die), FadeIn(spr), run_time=0.6)
        with self.say("h3"):
            arr = Arrow(ax.c2p(0.6, 0.12), ax.c2p(0.15, 0.12), color=GREEN, buff=0)
            vl = T("接种", 26, GREEN).next_to(arr, UP, buff=0.08)
            self.play(GrowArrow(arr), FadeIn(vl), run_time=1.2)
        with self.say("h4"):
            self.play(FadeOut(arr), FadeOut(vl), run_time=0.4)
            band = Rectangle(width=ax.x_length, height=0.18, stroke_width=0, fill_color=VIOLET, fill_opacity=0.35).move_to(ax.c2p(0.5, 0.03))
            bl = T("计算机病毒：长期、低水平", 24, VIOLET).next_to(band, UP, buff=0.1).shift(RIGHT * 1.5)
            self.play(FadeIn(band), FadeIn(bl), run_time=1.2)
        with self.say("h5"):
            sl = Rectangle(width=ax.c2p(0.28, 0)[0] - ax.c2p(lc, 0)[0], height=ax.y_length, stroke_width=0,
                           fill_color=RED, fill_opacity=0.25).move_to(ax.c2p((lc + 0.28) / 2, 0.5))
            q = T("恰好卡在阈值上方", 26, RED).next_to(sl, RIGHT, buff=0.15).shift(UP * 1.2)
            self.play(FadeIn(sl), FadeIn(q), run_time=1.0)
        with self.say("h6"):
            self.play(*[m.animate.set_opacity(0.25) for m in self.mobjects], run_time=1.0)
            nt = T("另一种解释", 44, GOLD, weight=BOLD)
            self.play(FadeIn(nt), run_time=0.8)
        clear(self)

    # ------------------------------------------------------------------ virus data
    def virus(self):
        tag = self.chapter("一  病毒之谜")
        ax = plain_axes([0, 48, 12], [0, 1, 0.5], 7.6, 4.2, xnums=[0, 12, 24, 36, 48], ynums=[0, 0.5, 1]).shift(LEFT * 2.2 + DOWN * 0.4)
        xl = xlabel("时间（月）", ax)
        yl = ylabel("存活概率", ax)
        tau = 14.0

        def Ps(t):
            return 1 - 0.45 * t / 2 if t < 2 else 0.55 * np.exp(-(t - 2) / tau)
        c = ax.plot(Ps, x_range=[0, 48, 0.1], color=BLUE, stroke_width=5, use_smoothing=False)
        with self.say("v1"):
            self.play(FadeIn(tag), Create(ax), FadeIn(xl), FadeIn(yl), run_time=1.4)
            sub = T("1996 — 2000 · 病毒流行报告（示意）", 22, MUTED).next_to(ax, UP, buff=0.3)
            self.play(FadeIn(sub), run_time=0.6)
        with self.say("v2"):
            self.play(Create(c), run_time=2.4, rate_func=linear)
            br = DoubleArrow(ax.c2p(2, 0.62), ax.c2p(16, 0.62), color=GOLD, buff=0)
            bl = T("特征寿命 ≈ 14 个月", 24, GOLD).next_to(br, UP, buff=0.1).shift(RIGHT * 0.8)
            self.play(GrowFromCenter(br), FadeIn(bl), run_time=1.0)
        G = sf_graph(70, 2.2, seed=7, kmax=18)
        net = NetView(G, fit(nx.kamada_kawai_layout(G), (2.4, 6.6, -2.6, 2.4)), color=VIOLET, eo=0.4)
        with self.say("v3"):
            self.play(FadeIn(net.group), run_time=1.2)
            env = VGroup(*[Rectangle(width=0.32, height=0.22, color=GOLD, stroke_width=2).add(
                Line([-0.16, 0.11, 0], [0, -0.02, 0], color=GOLD, stroke_width=2), Line([0.16, 0.11, 0], [0, -0.02, 0], color=GOLD, stroke_width=2))
                for _ in range(3)])
            hub = max(G, key=G.degree)
            nbs = list(G[hub])[:3]
            for e, w in zip(env, nbs):
                e.move_to(net.dots[hub])
            self.play(*[e.animate.move_to(net.dots[w]) for e, w in zip(env, nbs)], run_time=1.2)
            self.play(Indicate(net.dots[hub], color=RED, scale_factor=1.6), run_time=0.8)
        clip_lines(self, "yt_lovebug_zdnet.mp4", ["v3b"], "视频：ZDNET · YouTube", start=60)

    # ------------------------------------------------------------------ SIS
    def model(self):
        tag = self.chapter("一  易感—感染—易感")
        S = Circle(radius=0.6, color=BLUE, fill_opacity=0.25).shift(LEFT * 2.2 + UP * 0.6)
        I = Circle(radius=0.6, color=RED, fill_opacity=0.25).shift(RIGHT * 2.2 + UP * 0.6)
        St, It = T("易感", 30, BLUE).move_to(S), T("感染", 30, RED).move_to(I)
        a1 = CurvedArrow(S.get_top() + RIGHT * 0.2, I.get_top() + LEFT * 0.2, angle=-PI / 3, color=RED)
        a2 = CurvedArrow(I.get_bottom() + LEFT * 0.2, S.get_bottom() + RIGHT * 0.2, angle=-PI / 3, color=GREEN)
        l1 = MathTex(r"\nu", font_size=40, color=RED).next_to(a1, UP, buff=0.1)
        l2 = MathTex(r"\delta", font_size=40, color=GREEN).next_to(a2, DOWN, buff=0.1)
        t1 = T("传染", 22, RED).next_to(l1, RIGHT, buff=0.15)
        t2 = T("痊愈", 22, GREEN).next_to(l2, RIGHT, buff=0.15)
        with self.say("m1"):
            self.play(FadeIn(tag), FadeIn(S), FadeIn(St), FadeIn(I), FadeIn(It), run_time=1.0)
            self.play(Create(a1), Create(a2), run_time=1.4)
        with self.say("m2"):
            self.play(Write(l1), FadeIn(t1), run_time=0.8)
            self.play(Write(l2), FadeIn(t2), run_time=0.8)
            f = MathTex(r"\lambda=\frac{\nu}{\delta}", font_size=56, color=GOLD).shift(DOWN * 2.4)
            self.play(Write(f), run_time=1.0)
        clear(self)

    # ------------------------------------------------------------------ experiment
    def experiment(self):
        tag = self.chapter("二  亲手做实验")
        lams = [0.04, 0.06, 0.08, 0.1, 0.12, 0.14, 0.16, 0.18, 0.2, 0.24, 0.28, 0.32, 0.36, 0.4]
        rb, rr = [], []
        for lam in lams:
            rb.append(sis(self.Ab, lam)[0]); rr.append(sis(self.Ar, lam)[0])
        print("[ps] ba", [round(x, 3) for x in rb]); print("[ps] rr", [round(x, 3) for x in rr])
        # per-degree prevalence for chapter 4
        _, per = sis(self.Ab, 0.1, seed=3)
        deg = np.array([d for _, d in self.Gb.degree()])
        cls = [(3, 4, "3"), (4, 10, "4–9"), (10, 30, "10–29"), (30, 100, "30–99"), (100, 10 ** 6, "≥100")]
        self.rhok = [(lab, float(per[(deg >= a) & (deg < b)].mean())) for a, b, lab in cls]
        print("[ps] rho_k", self.rhok, "ratio", self.rhok[-1][1] / self.rhok[0][1])
        ax = plain_axes([0, 0.4, 0.1], [0, 0.6, 0.2], 8.6, 4.6, xnums=[0, 0.1, 0.2, 0.3, 0.4], ynums=[0, 0.2, 0.4, 0.6]).shift(DOWN * 0.3 + LEFT * 0.6)
        xl = xlabel("有效传染率 λ", ax)
        yl = ylabel("稳态感染比例", ax)
        # icons of the two networks
        G1 = nx.random_regular_graph(3, 24, seed=1)
        G2 = nx.barabasi_albert_graph(24, 1, seed=1)
        i1 = NetView(G1, fit(nx.kamada_kawai_layout(G1), (-5.6, -2.2, -2.0, 1.6)), color=MUTED, rmin=0.06, rk=0.0)
        i2 = NetView(G2, fit(nx.kamada_kawai_layout(G2), (2.2, 5.6, -2.0, 1.6)), color=RED, rmin=0.04, rk=0.04)
        c1 = T("度都一样", 26, MUTED).next_to(i1.group, UP, buff=0.3)
        c2 = T("无标度", 26, RED).next_to(i2.group, UP, buff=0.3)
        with self.say("e1"):
            self.play(FadeIn(tag), FadeIn(i1.group), FadeIn(c1), run_time=1.0)
            self.play(FadeIn(i2.group), FadeIn(c2), run_time=1.0)
            cap = T("各 20000 个节点 · 平均度 6", 24, MUTED).to_edge(DOWN, buff=0.5)
            self.play(FadeIn(cap), run_time=0.6)
        with self.say("e2"):
            self.play(FadeOut(VGroup(i1.group, i2.group, c1, c2, cap)), run_time=0.6)
            self.play(Create(ax), FadeIn(xl), FadeIn(yl), run_time=1.4)
        dr = VGroup(*[Dot(ax.c2p(l, r), radius=0.08, color=MUTED) for l, r in zip(lams, rr)])
        db = VGroup(*[Dot(ax.c2p(l, r), radius=0.08, color=RED) for l, r in zip(lams, rb)])
        lr = ax.plot_line_graph(lams, rr, line_color=MUTED, add_vertex_dots=False, stroke_width=3)
        lb = ax.plot_line_graph(lams, rb, line_color=RED, add_vertex_dots=False, stroke_width=3)
        lg = legend([(MUTED, "度都一样"), (RED, "无标度")]).to_corner(UR, buff=0.5).shift(DOWN * 0.5)
        lc_r = next(l for l, r in zip(lams, rr) if r > 0)
        with self.say("e3"):
            self.play(LaggedStart(*[FadeIn(d, scale=0.5) for d in dr], lag_ratio=0.1), Create(lr), FadeIn(lg[0]), run_time=2.0)
            th = DashedLine(ax.c2p(lc_r - 0.02, 0), ax.c2p(lc_r - 0.02, 0.6), color=MUTED)
            self.play(Create(th), run_time=0.6)
        with self.say("e4"):
            self.play(LaggedStart(*[FadeIn(d, scale=0.5) for d in db], lag_ratio=0.1), Create(lb), FadeIn(lg[1]), run_time=2.0)
            zone = Rectangle(width=ax.c2p(lc_r - 0.02, 0)[0] - ax.c2p(0.05, 0)[0], height=ax.y_length * 0.4, stroke_width=0,
                             fill_color=RED, fill_opacity=0.12).move_to(ax.c2p((0.05 + lc_r - 0.02) / 2, 0.12))
            self.play(FadeIn(zone), run_time=0.6)
        with self.say("e5"):
            note = T("原文：最多 850 万个节点，没有有限阈值", 24, INK).next_to(lg, DOWN, buff=0.4).align_to(lg, RIGHT)
            self.play(FadeIn(note), run_time=0.8)
            self.play(Indicate(VGroup(*db[:4]), color=RED, scale_factor=1.5), run_time=1.2)
        clear(self)

    # ------------------------------------------------------------------ mean field
    def meanfield(self):
        tag = self.chapter("二  按度分组")
        cols = [(3, 12), (6, 8), (15, 5), (40, 3), (100, 1)]
        groups = VGroup()
        for i, (k, cnt) in enumerate(cols):
            g = VGroup(*[Dot(radius=0.06 + 0.035 * np.sqrt(k / 3), color=BLUE) for _ in range(cnt)]).arrange(DOWN, buff=0.12)
            groups.add(VGroup(g, MathTex(f"k={k}", font_size=28, color=MUTED)).arrange(DOWN, buff=0.25))
        groups.arrange(RIGHT, buff=0.6, aligned_edge=DOWN).move_to(LEFT * 3.6 + DOWN * 0.3)
        with self.say("g1"):
            self.play(FadeIn(tag), LaggedStart(*[FadeIn(g, shift=UP * 0.2) for g in groups], lag_ratio=0.2), run_time=1.6)
            frac = [0.08, 0.15, 0.3, 0.6, 1.0]
            an = []
            for g, f in zip(groups, frac):
                dots = g[0]
                for j, d in enumerate(dots):
                    if j < max(1, round(f * len(dots))) and (f >= 0.15 or j == 0):
                        an.append(d.animate.set_color(RED))
            self.play(*an, run_time=1.0)
        e1 = MathTex(r"\partial_t\rho_k=-\rho_k+\lambda k(1-\rho_k)\,\Theta", font_size=40).move_to(RIGHT * 3.4 + UP * 1.8)
        e2 = MathTex(r"\Theta=\frac{\sum_k kP(k)\rho_k}{\sum_s sP(s)}", font_size=40).next_to(e1, DOWN, buff=0.6)
        with self.say("g2"):
            self.play(Write(e1), run_time=1.6)
        with self.say("g2b"):
            g = e1[0]
            for sl, c, lab in ((slice(5, 8), GREEN, "痊愈"), (slice(8, len(g) - 1), RED, "新感染"), (slice(len(g) - 1, len(g)), BLUE, "边指向感染者")):
                r = SurroundingRectangle(g[sl], color=c, buff=0.06)
                t = T(lab, 20, c).next_to(r, UP, buff=0.08)
                self.play(Create(r), FadeIn(t), run_time=0.6)
                self.wait(1.0)
                self.play(FadeOut(r), FadeOut(t), run_time=0.3)
        with self.say("g3"):
            self.play(Write(e2), run_time=1.6)
        with self.say("g3b"):
            r = SurroundingRectangle(e2[0][2:9], color=GOLD, buff=0.06)
            t = T("度 × 占比", 20, GOLD).next_to(e2, RIGHT, buff=0.2)
            self.play(Create(r), FadeIn(t), run_time=0.6)
            self.play(Indicate(groups[-1], color=GOLD, scale_factor=1.2), run_time=1.0)
        clear(self, keep=[tag])
        ax = plain_axes([0, 5.5, 1], [0, 1, 0.25], 7.0, 4.2, ynums=[0, 0.5, 1]).shift(LEFT * 2.2 + DOWN * 0.4)
        yl = ylabel("该组感染比例", ax)
        mx = max(r for _, r in self.rhok)
        top = 1.0 if mx > 0.5 else 0.5
        if top == 0.5:
            ax = plain_axes([0, 5.5, 1], [0, 0.5, 0.25], 7.0, 4.2, ynums=[0, 0.25, 0.5]).shift(LEFT * 2.2 + DOWN * 0.4)
            yl = ylabel("该组感染比例", ax)
        bars = VGroup()
        for i, (lab, r) in enumerate(self.rhok):
            b = Rectangle(width=0.8, height=max(0.02, ax.c2p(0, r)[1] - ax.c2p(0, 0)[1]), fill_color=interpolate_color(ManimColor(BLUE), ManimColor(RED), i / 4),
                          fill_opacity=0.9, stroke_width=0).move_to(ax.c2p(i + 1, 0), aligned_edge=DOWN)
            bars.add(VGroup(b, T(lab, 20, MUTED).next_to(ax.c2p(i + 1, 0), DOWN, buff=0.15), T(f"{r:.2f}", 20, INK).next_to(b, UP, buff=0.08)))
        xl = T("节点的度", 22, MUTED).next_to(ax.x_axis, DOWN, buff=0.6)
        with self.say("g4"):
            self.play(Create(ax), FadeIn(yl), FadeIn(xl), run_time=1.0)
            self.play(LaggedStart(*[FadeIn(b, shift=UP * 0.2) for b in bars], lag_ratio=0.25), run_time=2.0)
            cap = T("模拟 · λ = 0.1", 22, MUTED).next_to(ax, UP, buff=0.2)
            self.play(FadeIn(cap), run_time=0.5)
        with self.say("g5"):
            f = MathTex(r"\rho\approx 2\,e^{-1/(m\lambda)}", font_size=56, color=GOLD).move_to(RIGHT * 4.2 + UP * 1.6)
            self.play(Write(f), run_time=1.4)
        with self.say("g5b"):
            mlab = T("m：每个新节点带来的边数", 20, MUTED).next_to(f, DOWN, buff=0.15)
            self.play(FadeIn(mlab), run_time=0.5)
            ax2 = plain_axes([0, 0.25, 0.1], [0, 0.6, 0.3], 3.6, 2.2, xnums=[0, 0.1, 0.2]).move_to(RIGHT * 4.3 + DOWN * 1.9)
            cv = ax2.plot(lambda l: 2 * np.exp(-1 / (3 * l)) if l > 0.005 else 0, x_range=[0.005, 0.25, 0.005], color=GOLD, stroke_width=4)
            al = MathTex(r"\lambda", font_size=30, color=MUTED).next_to(ax2.x_axis, RIGHT, buff=0.1)
            ml = MathTex(r"m=3", font_size=28, color=MUTED).next_to(ax2, UP, buff=0.1)
            self.play(Create(ax2), FadeIn(al), FadeIn(ml), Create(cv), run_time=1.6)
        with self.say("g6"):
            self.play(FadeOut(mlab), run_time=0.3)
            z = MathTex(r"\lambda_c=0", font_size=48, color=RED).next_to(f, DOWN, buff=0.25)
            self.play(Write(z), run_time=0.8)
        clear(self)

    # ------------------------------------------------------------------ hubs keep it alive
    def hubs(self):
        tag = self.chapter("二  枢纽续命")
        n = 16
        pos = {0: ORIGIN + DOWN * 0.3}
        for i in range(1, n + 1):
            a = 2 * PI * i / n
            pos[i] = np.array([2.7 * np.cos(a), 2.7 * np.sin(a) - 0.3, 0])
        dots = {v: Dot(pos[v], radius=0.32 if v == 0 else 0.13, color=BLUE) for v in pos}
        edges = VGroup(*[Line(pos[0], pos[i], color=MUTED, stroke_width=2, stroke_opacity=0.6) for i in range(1, n + 1)])
        rng = np.random.default_rng(6)
        state = {v: False for v in pos}
        state[0] = True
        seq = []
        for t in range(14):
            new = dict(state)
            for i in range(1, n + 1):
                if state[i] and rng.random() < 0.5:
                    new[i] = False
                if not state[i] and state[0] and rng.random() < 0.18:
                    new[i] = True
            if state[0] and rng.random() < 0.5:
                new[0] = False
            if not state[0] and any(state[i] for i in range(1, n + 1)) and rng.random() < 0.9:
                new[0] = True
            state = new
            seq.append(dict(state))

        def show(st, rt):
            self.play(*[dots[v].animate.set_color(RED if st[v] else BLUE) for v in dots], run_time=rt)
        with self.say("k1") as d:
            self.play(FadeIn(tag), Create(edges), *[GrowFromCenter(x) for x in dots.values()], run_time=1.0)
            self.play(dots[0].animate.set_color(RED), run_time=0.4)
            for st in seq[:7]:
                show(st, (d - 1.6) / 7)
        with self.say("k2") as d:
            for st in seq[7:]:
                show(st, (d - 0.5) / 7)
        clear(self)

    # ------------------------------------------------------------------ immunization
    def immunize(self):
        tag = self.chapter("三  怎么接种")
        N = self.Ab.shape[0]
        deg = np.array([d for _, d in self.Gb.degree()])
        rng = np.random.default_rng(9)
        lam = 0.2
        rnd = np.ones(N, bool); rnd[rng.choice(N, N // 10, replace=False)] = False
        tgt = np.ones(N, bool); tgt[np.argsort(-deg)[: N // 10]] = False
        r0 = sis(self.Ab, lam, seed=4)[0]
        r1 = sis(self.Ab, lam, seed=4, alive=rnd)[0]
        r2 = sis(self.Ab, lam, seed=4, alive=tgt)[0]
        print(f"[ps] immunize none {r0:.3f} random {r1:.3f} targeted {r2:.3f}")
        G = sf_graph(90, 2.3, seed=17, kmax=18)
        pl = fit(nx.kamada_kawai_layout(G), (-6.4, -1.0, -2.2, 2.3))
        pr = {v: p + RIGHT * 7.4 for v, p in pl.items()}
        a, b = NetView(G, pl, color=RED, eo=0.4), NetView(G, pr, color=RED, eo=0.4)
        ta = T("随机接种 10%", 26, BLUE).next_to(a.group, UP, buff=0.3)
        tb = T("优先接种枢纽 10%", 26, GREEN).next_to(b.group, UP, buff=0.3)
        with self.say("i1"):
            self.play(FadeIn(tag), FadeIn(a.group), run_time=1.0)
            rs = list(np.random.default_rng(2).choice(list(G), 9, replace=False))
            self.play(FadeIn(ta), *[a.dots[v].animate.set_color(BLUE).scale(1.4) for v in rs], run_time=1.0)
            self.play(*a.state(rs, hl=RED), run_time=1.0)
        hs = sorted(G, key=G.degree, reverse=True)[:9]
        with self.say("i2"):
            self.play(FadeIn(b.group), FadeIn(tb), run_time=1.0)
            self.play(*[b.dots[v].animate.set_color(GREEN).scale(1.4) for v in hs], run_time=1.0)
            self.play(*b.state(hs, hl=RED), run_time=1.0)
        with self.say("i3"):
            ka = counter("稳态感染比例（两万节点模拟）", f"{r0:.0%} → {r1:.0%}", RED).next_to(a.group, DOWN, buff=0.1)
            kb = counter("稳态感染比例（两万节点模拟）", f"{r0:.0%} → {r2:.0%}", GREEN).next_to(b.group, DOWN, buff=0.1)
            self.play(FadeIn(ka), run_time=0.8)
            self.play(FadeIn(kb), *[x.animate.set_color(MUTED) for x in b.dots.values()], *[e.animate.set_stroke(MUTED) for e in b.edges.values()], run_time=1.0)
        with self.say("i4"):
            self.play(Indicate(tb, color=GREEN), run_time=1.0)
            self.play(*[Indicate(b.dots[h], color=GREEN) for h in hs[:4]], run_time=1.0)
        clear(self)

    # ------------------------------------------------------------------ limits
    def limits(self):
        tag = self.chapter("三  局限")
        k = np.array([d for _, d in self.Gb.degree()], float)
        lc = k.mean() / (k ** 2).mean()
        from scipy.sparse.linalg import eigsh
        Lmax = float(eigsh(self.Ab.astype(float), k=1, which="LA")[0][0])
        with self.say("l1"):
            f1 = MathTex(r"\lambda_c=\frac{\langle k\rangle}{\langle k^2\rangle}", font_size=56).shift(UP * 1.6 + LEFT * 2.6)
            v1 = MathTex(rf"\approx {lc:.2f}", font_size=48, color=GOLD).next_to(f1, RIGHT, buff=0.3)
            n1 = T("两万节点的无标度网络", 22, MUTED).next_to(VGroup(f1, v1), DOWN, buff=0.25)
            self.play(FadeIn(tag), Write(f1), run_time=1.2)
            self.play(FadeIn(v1), FadeIn(n1), run_time=0.8)
        with self.say("l1b"):
            nn = T("分子：连接数的平均", 22, BLUE).next_to(f1, RIGHT, buff=2.2).shift(UP * 0.3)
            dd = T("分母：连接数平方的平均", 22, GOLD).next_to(nn, DOWN, buff=0.2).align_to(nn, LEFT)
            self.play(FadeIn(nn), run_time=0.5)
            self.play(FadeIn(dd), run_time=0.5)
        with self.say("l2"):
            f2 = MathTex(r"\lambda_c\approx\frac{1}{\Lambda_{\max}}", font_size=56).shift(DOWN * 1.2 + LEFT * 2.6)
            v2 = MathTex(rf"\approx {1 / Lmax:.2f}", font_size=48, color=GOLD).next_to(f2, RIGHT, buff=0.3)
            l2 = T("固定网络（邻接矩阵最大特征值）", 22, MUTED).next_to(VGroup(f2, v2), DOWN, buff=0.25)
            self.play(Write(f2), run_time=1.2)
            self.play(FadeIn(v2), FadeIn(l2), run_time=0.8)
        clear(self, keep=[tag])
        G1 = sf_graph(80, 2.1, seed=3, kmax=30)
        G2 = nx.connected_watts_strogatz_graph(80, 4, 0.3, seed=3)
        v1 = NetView(G1, fit(nx.kamada_kawai_layout(G1), (-6.2, -1.0, -2.6, 2.0)), color=RED, eo=0.4)
        v2 = NetView(G2, fit(nx.kamada_kawai_layout(G2), (1.0, 6.2, -2.6, 2.0)), color=BLUE, eo=0.4)
        t1 = T("性接触：高度不均", 26, RED).next_to(v1.group, UP, buff=0.3)
        t2 = T("面对面接触：较均匀", 26, BLUE).next_to(v2.group, UP, buff=0.3)
        with self.say("l3"):
            self.play(FadeIn(v1.group), FadeIn(t1), run_time=1.2)
            self.play(FadeIn(v2.group), FadeIn(t2), run_time=1.2)
            q = T("是否无标度，仍有争议", 28, GOLD).to_edge(DOWN, buff=0.4)
            self.play(FadeIn(q), run_time=0.6)
        clear(self)
