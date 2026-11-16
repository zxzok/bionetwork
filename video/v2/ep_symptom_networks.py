"""Animated explainer: 症状网络与网络精神病学 (network theory, hysteresis, partial correlation, glasso, centrality)."""
import networkx as nx
import numpy as np

from common import *  # noqa: F401,F403
from bhelp import counter, axes, legend, arrow_between, parts_slide, recap_slide, show_clip

TITLE = "症状网络：当症状彼此维持"

LINES = {
    # hook
    "h1": "我们先看几个常见的症状。失眠让人疲乏，疲乏让人注意力变差，注意力差又会加重自我否定。",
    "h2": "传统观点认为，这些症状背后有一个共同的原因，也就是一个潜在的疾病。就像肺炎，导致了发热和咳嗽。",
    "h3": "网络观点则认为，症状之间直接相互作用，彼此维持。",
    "h3b": "画面是一段介绍用网络分析改进精神疾病诊断的短片。",
    "h4": "抑郁，可能不是一个藏在背后的病因，而是一张症状互相拉扯的网。这一期，我们就沿着这个思路来讲。",
    "q0": "这一期分三部分来讲。",
    "q1": "第一部分，网络理论：症状怎样彼此维持。",
    "q2": "第二部分，怎样从数据里估计症状网络。",
    "q3": "第三部分，怎样解读症状网络：中心性与模块控制。",
    # heterogeneity
    "d1": "先看第一部分。一项研究分析了三千七百多名抑郁症门诊患者的症状。左边每一行是一个病人，红色格子表示他有这个症状。",
    "d2": "他们一共出现了一千零三十种不同的症状组合，最常见的一种，也只占很小的比例。",
    "d3": "这种异质性提示，把所有人归入同一个潜在实体，可能丢掉了大量信息。",
    # hysteresis
    "y1": "网络理论认为，当症状之间连得足够紧，一个外部诱因激活的症状，会沿着网络扩散开来。",
    "y1b": "这一理论的代表人物之一是博斯布姆。画面是他介绍网络理论的讲座片段。",
    "y2": "我们做一个简单的模拟：九个症状，先逐渐加大外部压力，再慢慢撤掉。右边这张图，横轴是外部压力，纵轴是被激活的症状个数。",
    "y3": "蓝线是连接弱的网络。激活的症状随压力平滑增减，压力撤了，症状也就退了。",
    "y4": "红线是连接强的网络。压力过了某个点，症状几乎全部被激活。",
    "y4b": "可压力降回原处，它却卡在高位，要降得更低，才能恢复。",
    "y5": "【慢】这就是滞后：健康和疾病，可能是同一个系统的两个稳定状态。",
    # partial correlation
    "p1": "下面进入第二部分：怎样从数据里估计症状网络。直接用相关系数连边，会出问题。",
    "p2": "设失眠和疲乏的相关是零点五，疲乏和注意力差也是零点五，失眠和注意力差是零点二五。",
    "p3": "相关网络会在失眠和注意力差之间画一条边，就是这条红线。可它们的关联，完全来自疲乏。",
    "p4": "偏相关，就是控制了其余所有症状之后，两个症状之间还剩下的关联。这样一来，红线变成了零，另外两条边约为零点四五。",
    "p5": "偏相关可以直接从协方差矩阵的逆矩阵算出来，这就是高斯图模型。",
    "p5b": "式子里，K 是协方差矩阵的逆，也叫精度矩阵。两个症状的偏相关，等于 K 里对应的那一格取负号，再除以两个对角元乘积的平方根。",
    # glasso
    "g1": "但样本有限时，样本偏相关会出现许多小而非零的虚假边。",
    "g2": "这是一个模拟。左边是真实的网络，只有十一条边。",
    "g2b": "右边是用三百个样本估计出的偏相关。三十六对症状的偏相关，全都不为零。",
    "g3": "常用的做法是图形套索：在估计时加一个惩罚项，就是上面这个式子，它把弱边压缩为零。惩罚的强度，通常用扩展贝叶斯信息准则来选择。",
    "g4": "压缩之后只剩十三条边，十一条真实的边全都保留了下来。",
    "g5": "【慢】但要注意，被压缩为零的边，不一定真的不存在，可能只是样本不够。",
    # centrality
    "c1": "最后是第三部分，怎样解读。得到网络之后，最常报告的是强度中心性，也就是与一个症状相连的所有边权绝对值之和。",
    "c2": "比如疲乏和三个邻居的偏相关，是零点三、零点二和负零点一。取绝对值再相加，强度就是零点六。",
    "c3": "早期研究常把最中心的症状，解释为最佳治疗靶点。这个推论要非常小心。",
    "c4": "第一，截面数据描述的是人与人之间的关联，不等于某个人体内的因果过程。",
    "c4b": "第二，两个条目内容几乎相同，比如入睡困难和早醒，也会互相抬高中心性。",
    "c5": "第三，中心性排序在小样本里很不稳定，要用逐步删掉被试的自助法来检验。这张图，横轴是删掉的被试比例，纵轴是和全样本排序的相关。",
    "c5b": "删掉之后，排序相关仍在零点七以上，能删掉的最大比例，就叫稳定性系数。",
    "c6": "在这个模拟里，三百人时稳定性系数是零点四，一百人时只有零点一，低于建议的零点二五。",
    # module control
    "m1": "最后介绍一项研究，它把网络控制理论用到了症状网络上。",
    "m2": "研究分析了两千七百多名大学新生的抑郁、焦虑、失眠和压力量表，一共三十七个条目。",
    "m3": "网络划分出六个症状模块，研究者在模块尺度上，计算模块之间的平均控制强度。",
    "m4": "【慢】结果发现，不直接描述情绪的模块，对情绪模块的控制强度最高；情绪模块，更容易被其他模块控制。",
    "m5": "控制作用最强的几个条目，来自失眠量表和压力量表。",
    "m5b": "当然，这是截面数据的结构分析，还需要纵向和干预研究来检验。",
    # recap
    "z1": "好，我们来总结一下。",
    "z2": "第一，症状网络把疾病看作症状相互作用形成的稳定状态。",
    "z3": "第二，网络通常用正则化的偏相关来估计，而不是简单的相关。",
    "z4": "第三，中心性只是统计描述，不能直接当作治疗靶点，稳定性必须报告。",
    "z5": "这个专题的知识页面里，有画面上的这个交互演示。先看偏相关网络；切换到零阶相关，也就是普通的相关，边一下子变多了。",
    "z5b": "再切回偏相关，改变样本量，重新抽样。你可以亲手比较，样本多少对估计出的网络有什么影响。",
}

SYM = ["情绪低落", "兴趣减退", "睡眠问题", "疲乏", "食欲改变", "自我否定", "注意力差", "迟缓烦躁", "消极念头"]
TRUE_E = [(0, 1), (1, 2), (2, 3), (3, 4), (0, 4), (1, 5), (5, 6), (6, 7), (7, 8), (2, 6), (3, 8)]


def true_net():
    K = np.eye(9)
    for i, j in TRUE_E:
        K[i, j] = K[j, i] = -0.36
    S = np.linalg.inv(K)
    d = np.sqrt(np.diag(S))
    return S / np.outer(d, d)


def pcor(K):
    d = np.sqrt(np.diag(K))
    P = -K / np.outer(d, d)
    np.fill_diagonal(P, 0)
    return P


def glasso(S, lam, rho=1.0, it=2000):
    """Graphical lasso by ADMM (diagonal not penalised)."""
    p = len(S); Z = np.eye(p); U = np.zeros((p, p))
    for _ in range(it):
        ev, Q = np.linalg.eigh(rho * (Z - U) - S)
        th = (ev + np.sqrt(ev ** 2 + 4 * rho)) / (2 * rho)
        Th = Q @ np.diag(th) @ Q.T
        A = Th + U
        Z = np.sign(A) * np.maximum(np.abs(A) - lam / rho, 0)
        np.fill_diagonal(Z, np.diag(A))
        U = U + Th - Z
    return Z


def strength(X):
    return np.abs(pcor(np.linalg.inv(np.corrcoef(X.T)))).sum(0)


def cs_coef(X, seed=0, B=100):
    rng = np.random.default_rng(seed)
    n = len(X); s0 = strength(X); out = 0.0
    for f in np.arange(0.1, 0.8, 0.1):
        ok = 0
        for _ in range(B):
            idx = rng.choice(n, int(n * (1 - f)), replace=False)
            ok += np.corrcoef(strength(X[idx]), s0)[0, 1] >= 0.7
        if ok / B >= 0.95:
            out = round(f, 1)
        else:
            break
    return out


def hyst(w, A, Ss, b=-3.0):
    p = np.zeros(len(A)); out = []; states = []
    for S in Ss:
        for _ in range(200):
            p = 1 / (1 + np.exp(-(b + S + w * A @ p)))
        out.append(p.sum()); states.append(p.copy())
    return np.array(out), states


def sym_pos(center=ORIGIN, r=2.3):
    return [center + r * np.array([np.cos(PI / 2 - 2 * PI * i / 9), np.sin(PI / 2 - 2 * PI * i / 9), 0]) for i in range(9)]


class Episode(Narrated):
    LINES = LINES

    def construct(self):
        self.hook()
        parts_slide(self, ["一  网络理论：症状彼此维持", "二  估计症状网络：偏相关与图形套索", "三  解读：中心性与模块控制"])
        self.hetero()
        self.hysteresis()
        self.partial()
        self.glasso_ch()
        self.centrality()
        self.module()
        self.recap()

    def fade_all(self, rt=0.8, keep=()):
        self.play(*[FadeOut(m) for m in self.mobjects if m not in keep], run_time=rt)

    def node(self, s, p, c=BLUE, size=24):
        circ = RoundedRectangle(corner_radius=0.25, width=1.7, height=0.62, stroke_color=c, stroke_width=2.5, fill_color=BG, fill_opacity=1)
        return VGroup(circ, T(s, size, c)).move_to(p)

    # ------------------------------------------------------------------ hook
    def hook(self):
        names = ["失眠", "疲乏", "注意力差", "自我否定"]
        P = [LEFT * 4.8 + UP * 0.6, LEFT * 1.6 + UP * 0.6, RIGHT * 1.6 + UP * 0.6, RIGHT * 4.8 + UP * 0.6]
        nodes = [self.node(s, p) for s, p in zip(names, P)]
        arrs = [Arrow(P[i] + RIGHT * 0.85, P[i + 1] + LEFT * 0.85, buff=0.05, color=GOLD, stroke_width=5) for i in range(3)]
        with self.say("h1") as d:
            self.play(FadeIn(nodes[0], scale=0.8), run_time=0.6)
            for i in range(3):
                self.play(GrowArrow(arrs[i]), FadeIn(nodes[i + 1], scale=0.8), run_time=max(0.6, (d - 1.0) / 3))
        allg = VGroup(*nodes, *arrs)
        with self.say("h2") as d:
            self.play(allg.animate.scale(0.75).shift(DOWN * 1.8), run_time=0.8)
            latent = Circle(radius=0.65, color=RED, fill_opacity=0.2, stroke_width=3).move_to(UP * 2.0)
            ll = T("潜在疾病", 24, RED).move_to(latent)
            self.play(FadeOut(VGroup(*arrs)), GrowFromCenter(latent), FadeIn(ll), run_time=1.0)
            down = VGroup(*[Arrow(latent.get_bottom(), n.get_top(), buff=0.1, color=RED, stroke_width=4) for n in nodes])
            self.play(LaggedStart(*[GrowArrow(a) for a in down], lag_ratio=0.15), run_time=1.2)
            tt = T("共同原因模型", 26, RED).next_to(latent, RIGHT, buff=0.5)
            self.play(FadeIn(tt), run_time=0.5)
        with self.say("h3") as d:
            self.play(FadeOut(down), FadeOut(latent), FadeOut(ll), FadeOut(tt), run_time=0.6)
            Pn = [n.get_center() for n in nodes]
            links = VGroup(*[DoubleArrow(Pn[i] + RIGHT * 0.7, Pn[i + 1] + LEFT * 0.7, buff=0.05, color=GOLD, stroke_width=4, tip_length=0.15) for i in range(3)])
            extra = VGroup(CurvedDoubleArrow(Pn[0] + UP * 0.3, Pn[2] + UP * 0.3, angle=-0.6, color=GOLD, stroke_width=3, tip_length=0.15),
                           CurvedDoubleArrow(Pn[1] + DOWN * 0.3, Pn[3] + DOWN * 0.3, angle=-0.6, color=GOLD, stroke_width=3, tip_length=0.15))
            self.play(LaggedStart(*[GrowFromCenter(l) for l in links], lag_ratio=0.2), run_time=1.0)
            self.play(Create(extra), run_time=1.0)
            tn = T("网络模型", 26, GOLD).move_to(UP * 1.8)
            self.play(FadeIn(tn), run_time=0.5)
        keep = list(self.mobjects)
        show_clip(self, "h3b", "yt_network_mental_wellcome.mp4", "center", "视频：Wellcome · YouTube", start=5, min_len=6)
        self.play(*[FadeIn(m) for m in keep], run_time=0.6)
        with self.say("h4") as d:
            q = T("一张症状互相拉扯的网", 52, GOLD, weight=BOLD).move_to(UP * 0.6)
            self.play(FadeOut(tn), Write(q), run_time=1.2)
        self.fade_all()

    # ------------------------------------------------------------------ heterogeneity
    def hetero(self):
        tag = self.chapter("一  网络理论：一千种抑郁")
        rng = np.random.default_rng(3)
        rows = VGroup()
        for r in range(14):
            prof = rng.random(9) < rng.uniform(0.35, 0.8)
            rows.add(VGroup(*[Square(0.32, stroke_width=1, stroke_color=BG, fill_color=RED if x else "#26303f", fill_opacity=1) for x in prof]).arrange(RIGHT, buff=0.03))
        rows.arrange(DOWN, buff=0.06).move_to(LEFT * 3.0 + DOWN * 0.2)
        hdr = VGroup(*[T(str(i + 1), 16, MUTED) for i in range(9)])
        for h, s in zip(hdr, rows[0]):
            h.next_to(s, UP, buff=0.1)
        hl = T("9 个症状", 20, MUTED).next_to(hdr, UP, buff=0.12)
        with self.say("d1") as d:
            self.play(FadeIn(tag), FadeIn(hdr), FadeIn(hl), run_time=0.6)
            self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in rows], lag_ratio=0.1), run_time=d * 0.6)
            c1 = counter("抑郁症门诊患者", "3703 名", INK, vs=40).move_to(RIGHT * 3.4 + UP * 1.2)
            self.play(FadeIn(c1), run_time=0.6)
        with self.say("d2") as d:
            c2 = counter("不同的症状组合", "1030 种", RED, vs=48).move_to(RIGHT * 3.4 + DOWN * 1.0)
            self.play(FadeIn(c2, scale=0.8), run_time=1.0)
            self.play(LaggedStart(*[Indicate(r, color=GOLD, scale_factor=1.04) for r in rows], lag_ratio=0.05), run_time=1.6)
        with self.say("d3") as d:
            one = Circle(radius=0.5, color=MUTED, stroke_width=3).move_to(rows)
            self.play(rows.animate.set_opacity(0.3), run_time=0.6)
            self.play(Create(one), run_time=0.6)
            self.play(one.animate.scale(0.3).set_opacity(0.2), run_time=1.2)
        self.fade_all()

    # ------------------------------------------------------------------ hysteresis
    def hysteresis(self):
        show_clip(self, "y1b", "yt_borsboom_vgct.mp4", "center", "视频：VGCt · YouTube", start=20, min_len=6)
        tag = self.chapter("一  网络理论：网络会“卡住”")
        G = nx.random_regular_graph(4, 9, seed=1)
        A = nx.to_numpy_array(G)
        P = sym_pos(LEFT * 3.8 + DOWN * 0.2, 2.0)
        dots = [Dot(P[i], radius=0.22, color=MUTED) for i in range(9)]
        ed = VGroup(*[Line(P[u], P[v], color=MUTED, stroke_width=2, stroke_opacity=0.5) for u, v in G.edges()])
        with self.say("y1") as d:
            self.play(FadeIn(tag), Create(ed), *[FadeIn(x) for x in dots], run_time=1.2)
            seq = [0]
            for u, v in nx.bfs_edges(G, 0):
                seq.append(v)
            self.play(LaggedStart(*[dots[i].animate.set_color(RED) for i in seq], lag_ratio=0.25), run_time=d * 0.45)
            self.play(*[x.animate.set_color(MUTED) for x in dots], run_time=0.6)
        up = np.linspace(-1, 4, 51)
        Ss = np.r_[up, up[::-1]]
        weak, sw = hyst(0.3, A, Ss)
        strong, ss = hyst(1.2, A, Ss)
        ax = axes([-1, 4, 1], [0, 9, 3], 5.6, 4.0, xn=None, yn=[0, 3, 6, 9]).move_to(RIGHT * 3.4 + DOWN * 0.3)
        xl = T("外部压力", 22, MUTED).next_to(ax.x_axis, DOWN, buff=0.3)
        yl = T("激活的症状数", 22, MUTED).rotate(PI / 2).next_to(ax.y_axis, LEFT, buff=0.3)
        lg = legend([(BLUE, "连接弱"), (RED, "连接强")], 20).next_to(ax, UP, buff=0.2)
        with self.say("y2") as d:
            self.play(Create(ax), FadeIn(xl), FadeIn(yl), run_time=1.0)
            self.play(FadeIn(lg), run_time=0.5)

        def sweep(vals, states, color, dur, k0=0, k1=None):
            k1 = len(Ss) - 1 if k1 is None else k1
            path = VMobject(color=color, stroke_width=4)
            path.set_points_as_corners([ax.c2p(Ss[k0], vals[k0]), ax.c2p(Ss[k0], vals[k0]) + RIGHT * 1e-3])
            pts = [ax.c2p(s, v) for s, v in zip(Ss, vals)]

            def upd(m, a):
                k = max(k0 + 1, k0 + int(a * (k1 - k0)))
                m.set_points_as_corners(pts[k0:k + 1])
                for x, pv in zip(dots, states[k]):
                    x.set_color(interpolate_color(ManimColor(MUTED), ManimColor(RED), float(pv)))
            self.add(path)
            return UpdateFromAlphaFunc(path, upd, rate_func=linear, run_time=dur)
        with self.say("y3") as d:
            for e in ed:
                e.set_stroke(width=1.2, opacity=0.3)
            self.play(sweep(weak, sw, BLUE, d * 0.85))
        with self.say("y4") as d:
            self.play(*[e.animate.set_stroke(width=4.5, opacity=0.9) for e in ed], run_time=0.6)
            self.play(sweep(strong, ss, RED, d - 1.0, 0, 50))
        with self.say("y4b") as d:
            self.play(sweep(strong, ss, RED, d * 0.85, 50, len(Ss) - 1))
        with self.say("y5") as d:
            k_up = np.argmax(np.diff(strong[:51]))
            k_dn = 51 + np.argmin(np.diff(strong[51:]))
            a1 = Arrow(ax.c2p(Ss[k_up] - 0.5, 4.5), ax.c2p(Ss[k_up] - 0.5, 7.0), buff=0, color=GOLD, stroke_width=4)
            a2 = Arrow(ax.c2p(Ss[k_dn] - 0.4, 6.5), ax.c2p(Ss[k_dn] - 0.4, 3.5), buff=0, color=GOLD, stroke_width=4)
            hl = T("滞后", 30, GOLD, weight=BOLD).move_to(ax.c2p(2.6, 3.0))
            self.play(GrowArrow(a1), GrowArrow(a2), FadeIn(hl), run_time=1.2)
        self.fade_all()

    # ------------------------------------------------------------------ partial correlation
    def partial(self):
        tag = self.chapter("二  估计：相关还是偏相关")
        P = [LEFT * 3.0 + UP * 1.3, ORIGIN + UP * 1.3 + RIGHT * 0.0, RIGHT * 3.0 + UP * 1.3]
        P = [LEFT * 3.4 + DOWN * 0.6, UP * 1.8, RIGHT * 3.4 + DOWN * 0.6]
        names = ["失眠", "疲乏", "注意力差"]
        nodes = [self.node(s, p, GOLD if i == 1 else BLUE, 26) for i, (s, p) in enumerate(zip(names, P))]
        with self.say("p1") as d:
            self.play(FadeIn(tag), *[FadeIn(n, scale=0.8) for n in nodes], run_time=1.0)
        r = {(0, 1): 0.5, (1, 2): 0.5, (0, 2): 0.25}

        def edge(i, j, w, c=INK):
            a, b = P[i], P[j]
            u = (b - a) / np.linalg.norm(b - a)
            ln = Line(a + u * 0.95, b - u * 0.95, color=c, stroke_width=2 + 12 * abs(w))
            lab = T(f"{0.0 if abs(w) < 0.005 else w:.2f}", 24, c).move_to((a + b) / 2 + np.array([-u[1], u[0], 0]) * 0.35)
            return VGroup(ln, lab)
        es = {k: edge(*k, v) for k, v in r.items()}
        with self.say("p2") as d:
            for k in [(0, 1), (1, 2), (0, 2)]:
                self.play(Create(es[k][0]), FadeIn(es[k][1]), run_time=max(0.8, d * 0.25))
        with self.say("p3") as d:
            self.play(es[(0, 2)][0].animate.set_color(RED), es[(0, 2)][1].animate.set_color(RED), run_time=0.8)
            self.play(Indicate(nodes[1], color=GOLD, scale_factor=1.2), run_time=1.0)
        C = np.array([[1, 0.5, 0.25], [0.5, 1, 0.5], [0.25, 0.5, 1]])
        Pc = pcor(np.linalg.inv(C))
        self.pc3 = Pc
        with self.say("p4") as d:
            lab = T("偏相关", 30, GOLD, weight=BOLD).to_corner(UR, buff=0.6)
            self.play(FadeIn(lab), run_time=0.5)
            new = {k: edge(*k, Pc[k], GOLD if k != (0, 2) else RED) for k in r}
            self.play(Transform(es[(0, 2)][1], new[(0, 2)][1]), es[(0, 2)][0].animate.set_stroke(opacity=0.0), run_time=1.0)
            self.play(Transform(es[(0, 1)], new[(0, 1)]), Transform(es[(1, 2)], new[(1, 2)]), run_time=1.0)
        with self.say("p5") as d:
            f = MathTex(r"\rho_{ij\cdot\text{rest}}=-\frac{K_{ij}}{\sqrt{K_{ii}K_{jj}}},\qquad K=\Sigma^{-1}", font_size=44).to_edge(DOWN, buff=0.4)
            self.play(Write(f), run_time=1.6)
        with self.say("p5b") as d:
            fl = VGroup(T("K：协方差矩阵的逆（精度矩阵）", 22, GOLD), T("分子：对应的那一格取负号", 22, GOLD), T("分母：两个对角元乘积的平方根", 22, GOLD)
                        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15).next_to(f, UP, buff=0.35)
            self.play(VGroup(*nodes, es[(0, 1)], es[(1, 2)], es[(0, 2)][1]).animate.shift(UP * 0.6).set_opacity(0.3), es[(0, 2)][0].animate.shift(UP * 0.6), run_time=0.6)
            self.play(FadeIn(fl, lag_ratio=0.5), run_time=d * 0.5)
        self.fade_all()

    # ------------------------------------------------------------------ glasso
    def glasso_ch(self):
        tag = self.chapter("二  估计：图形套索")
        Sig = true_net()
        rng = np.random.default_rng(2)
        X = rng.multivariate_normal(np.zeros(9), Sig, 300)
        C = np.corrcoef(X.T)
        Ps = pcor(np.linalg.inv(C))
        Z = glasso(C, 0.5)
        Pg = pcor(Z)
        iu = [(i, j) for i in range(9) for j in range(i + 1, 9)]
        est = {(i, j) for i, j in iu if abs(Z[i, j]) > 1e-3}
        self.gl = (sum(abs(Ps[i, j]) > 1e-6 for i, j in iu), len(est), len(est & set(TRUE_E)))
        PL = sym_pos(LEFT * 3.6 + DOWN * 0.3, 2.3)
        PR = sym_pos(RIGHT * 3.6 + DOWN * 0.3, 2.3)

        def net(Pp, W, keys, scale=9):
            lines = VGroup(*[Line(Pp[i], Pp[j], stroke_width=max(0.6, scale * abs(W[i, j])), color=BLUE if W[i, j] > 0 else RED,
                                  stroke_opacity=0.85) for i, j in keys])
            dots = VGroup(*[Dot(p, radius=0.13, color=INK) for p in Pp])
            labs = VGroup(*[T(SYM[k], 16, MUTED).move_to(Pp[k] + (Pp[k] - np.mean(Pp, 0)) / 2.3 * 0.45) for k in range(9)])
            return VGroup(lines, dots, labs)
        Kt = np.linalg.inv(Sig)
        truth = net(PL, pcor(Kt), TRUE_E)
        tl = T("真实网络（模拟）", 24).next_to(truth, UP, buff=0.25)
        with self.say("g1") as d:
            self.play(FadeIn(tag), FadeIn(truth), FadeIn(tl), run_time=1.2)
        samp = net(PR, Ps, iu)
        sl = T("样本偏相关", 24).next_to(samp, UP, buff=0.25)
        with self.say("g2") as d:
            k1 = counter("真实的边", f"{len(TRUE_E)} 条", GREEN, vs=30).next_to(truth, DOWN, buff=0.2)
            self.play(FadeIn(k1), run_time=0.6)
        with self.say("g2b") as d:
            self.play(FadeIn(samp), FadeIn(sl), run_time=1.2)
            k2 = counter("非零的偏相关", f"{self.gl[0]} 对", RED, vs=30).next_to(samp, DOWN, buff=0.2)
            self.play(FadeIn(k2), run_time=0.6)
        gnet = net(PR, Pg, sorted(est), scale=14)
        with self.say("g3") as d:
            gl = T("图形套索", 24, GOLD).move_to(sl)
            pen = MathTex(r"\lambda\sum_{i\neq j}|K_{ij}|", font_size=40, color=GOLD).move_to(UP * 3.0 + RIGHT * 0.2)
            self.play(Write(pen), run_time=1.0)
            self.play(Transform(samp, gnet), Transform(sl, gl), run_time=d * 0.5)
        with self.say("g4") as d:
            k3 = counter("保留的边", f"{self.gl[1]} 条，含真实 {self.gl[2]} 条", GOLD, vs=30).move_to(k2)
            self.play(Transform(k2, k3), run_time=0.8)
        with self.say("g5") as d:
            note = T("被压缩为零 ≠ 一定不存在", 28, RED).to_edge(DOWN, buff=0.15)
            self.play(FadeOut(k1), FadeOut(k2), run_time=0.4)
            self.play(FadeIn(note), run_time=0.8)
        self.fade_all()

    # ------------------------------------------------------------------ centrality
    def centrality(self):
        tag = self.chapter("三  解读：中心性不等于靶点")
        c = ORIGIN + LEFT * 2.8
        center = self.node("疲乏", c, GOLD, 28)
        nb = [("睡眠问题", 0.30, c + UP * 2.0 + LEFT * 2.2), ("注意力差", 0.20, c + UP * 2.0 + RIGHT * 2.2), ("食欲改变", -0.10, c + DOWN * 2.2)]
        parts = VGroup()
        for s, w, p in nb:
            n = self.node(s, p, BLUE, 22)
            u = (p - c) / np.linalg.norm(p - c)
            ln = Line(c + u * 0.7, p - u * 0.7, stroke_width=3 + 14 * abs(w), color=BLUE if w > 0 else RED)
            lab = T(f"{w:+.2f}", 24, BLUE if w > 0 else RED).next_to(ln.get_center(), np.array([-u[1], u[0], 0]), buff=0.15)
            parts.add(VGroup(ln, n, lab))
        with self.say("c1") as d:
            self.play(FadeIn(tag), FadeIn(center), run_time=0.6)
            self.play(LaggedStart(*[FadeIn(p_) for p_ in parts], lag_ratio=0.3), run_time=1.4)
            f = MathTex(r"s_i=\sum_j |w_{ij}|", font_size=48).move_to(RIGHT * 3.6 + UP * 1.6)
            self.play(Write(f), run_time=1.0)
        with self.say("c2") as d:
            calc = MathTex(r"0.30+0.20+|-0.10|=0.60", font_size=40, color=GOLD).next_to(f, DOWN, buff=0.6)
            self.play(*[Indicate(p_[2], color=GOLD) for p_ in parts], run_time=1.0)
            self.play(Write(calc), run_time=1.2)
        with self.say("c3") as d:
            tgt = T("最中心 = 最佳靶点", 34, RED, weight=BOLD).move_to(RIGHT * 3.4 + DOWN * 1.4)
            self.play(Write(tgt), run_time=1.0)
            x = Cross(tgt, stroke_color=RED, scale_factor=0.9)
            self.play(Create(x), run_time=0.6)
        self.fade_all(keep=(tag,))
        with self.say("c4") as d:
            crowd = VGroup(*[Dot(radius=0.08, color=BLUE) for _ in range(60)]).arrange_in_grid(6, 10, buff=0.25).move_to(LEFT * 3.4 + UP * 0.4)
            l1 = T("人与人之间", 24, BLUE).next_to(crowd, DOWN, buff=0.3)
            person = Circle(radius=0.9, color=GOLD).move_to(RIGHT * 0.6 + UP * 0.4)
            l2 = T("个体内的因果", 24, GOLD).next_to(person, DOWN, buff=0.3)
            ne = MathTex(r"\neq", font_size=60).move_to((crowd.get_right() + person.get_left()) / 2)
            self.play(FadeIn(crowd), FadeIn(l1), run_time=0.8)
            self.play(Write(ne), Create(person), FadeIn(l2), run_time=1.0)
        with self.say("c4b") as d:
            twin = VGroup(self.node("入睡困难", RIGHT * 4.6 + UP * 1.0, BLUE, 22), self.node("早醒", RIGHT * 4.6 + DOWN * 0.4, BLUE, 22))
            tl = Line(twin[0].get_bottom(), twin[1].get_top(), stroke_width=10, color=BLUE)
            self.play(FadeIn(twin), Create(tl), run_time=1.0)
            ov = T("内容重叠", 22, RED).next_to(twin, DOWN, buff=0.3)
            self.play(FadeIn(ov), run_time=0.5)
        self.fade_all(keep=(tag,))
        Sig = true_net()
        X3 = np.random.default_rng(1).multivariate_normal(np.zeros(9), Sig, 300)
        X1 = np.random.default_rng(1).multivariate_normal(np.zeros(9), Sig, 100)
        cs3, cs1 = cs_coef(X3), cs_coef(X1)
        self.cs = (cs3, cs1)
        fr = np.arange(0.1, 0.8, 0.1)

        def curve_vals(X, seed=0, B=60):
            rng = np.random.default_rng(seed); s0 = strength(X); n = len(X); out = []
            for f_ in fr:
                cc = [np.corrcoef(strength(X[rng.choice(n, int(n * (1 - f_)), replace=False)]), s0)[0, 1] for _ in range(B)]
                out.append(np.quantile(cc, 0.05))
            return out
        y3, y1 = np.clip(curve_vals(X3), 0, 1), np.clip(curve_vals(X1), 0, 1)
        ax = axes([0, 0.8, 0.1], [0, 1, 0.5], 7.6, 4.0, xn=[0.1, 0.3, 0.5, 0.7], yn=[0, 0.5, 1]).shift(DOWN * 0.5 + LEFT * 1.8)
        xl = T("删掉的被试比例", 22, MUTED).next_to(ax.x_axis, DOWN, buff=0.35)
        yl = T("与全样本排序的相关", 20, MUTED).rotate(PI / 2).next_to(ax.y_axis, LEFT, buff=0.3)
        th = DashedLine(ax.c2p(0, 0.7), ax.c2p(0.8, 0.7), color=MUTED)
        tht = T("0.7", 20, MUTED).next_to(ax.c2p(0.8, 0.7), RIGHT, buff=0.1)
        c3 = ax.plot_line_graph(fr, y3, line_color=BLUE, vertex_dot_radius=0.05, stroke_width=4)
        c1 = ax.plot_line_graph(fr, y1, line_color=RED, vertex_dot_radius=0.05, stroke_width=4)
        lg = legend([(BLUE, "300 人"), (RED, "100 人")], 22).to_corner(UR, buff=0.5).shift(DOWN * 0.5)
        with self.say("c5") as d:
            self.play(Create(ax), FadeIn(xl), FadeIn(yl), Create(th), FadeIn(tht), FadeIn(lg), run_time=1.2)
            self.play(Create(c3), Create(c1), run_time=d * 0.5)
        with self.say("c5b") as d:
            self.play(Indicate(th, color=GOLD), Indicate(tht, color=GOLD), run_time=1.2)
        with self.say("c6") as d:
            k = VGroup(counter("稳定性系数 · 300 人", f"{cs3:.1f}", BLUE, vs=34), counter("稳定性系数 · 100 人", f"{cs1:.1f}", RED, vs=34),
                       counter("建议至少", "0.25", MUTED, vs=34)).arrange(DOWN, buff=0.35).to_edge(RIGHT, buff=0.4).shift(DOWN * 1.0)
            self.play(FadeOut(lg), LaggedStart(*[FadeIn(x_) for x_ in k], lag_ratio=0.3), run_time=1.6)
        self.fade_all()

    # ------------------------------------------------------------------ module control
    def module(self):
        tag = self.chapter("三  解读：模块之间的控制")
        with self.say("m1") as d:
            self.play(FadeIn(tag), run_time=0.5)
            scales = VGroup(*[self.node(s, ORIGIN, c, 24) for s, c in (("抑郁", RED), ("焦虑", VIOLET), ("失眠", BLUE), ("压力", GREEN))]).arrange(RIGHT, buff=0.5).move_to(UP * 1.6)
            self.play(LaggedStart(*[FadeIn(s_, shift=DOWN * 0.2) for s_ in scales], lag_ratio=0.2), run_time=d * 0.5)
        with self.say("m2") as d:
            c1 = counter("大学新生", "2773 名", INK, vs=36)
            c2 = counter("量表条目", "37 个", INK, vs=36)
            VGroup(c1, c2).arrange(RIGHT, buff=1.4).move_to(DOWN * 0.6)
            self.play(FadeIn(c1), run_time=0.7)
            self.play(FadeIn(c2), run_time=0.7)
        self.fade_all(keep=(tag,))
        rng = np.random.default_rng(5)
        centers = [np.array(p) for p in ([-4.6, 1.4, 0], [-4.6, -1.6, 0], [-2.2, -0.1, 0], [2.6, 1.3, 0], [2.6, -1.5, 0], [-2.2, 2.5, 0])]
        sizes = [7, 6, 6, 9, 7, 2]
        emo = [False, False, False, True, True, None]
        mods = VGroup()
        for ccen, n, e in zip(centers, sizes, emo):
            col = RED if e else (BLUE if e is False else MUTED)
            pts = [ccen + np.array([rng.normal(0, 0.35), rng.normal(0, 0.3), 0]) for _ in range(n)]
            ring = Circle(radius=0.85, color=col, stroke_width=2.5, fill_color=col, fill_opacity=0.08).move_to(ccen)
            mods.add(VGroup(ring, VGroup(*[Dot(p, radius=0.07, color=col) for p in pts])))
        with self.say("m3") as d:
            self.play(LaggedStart(*[FadeIn(m_) for m_ in mods], lag_ratio=0.15), run_time=d * 0.5)
            six = counter("症状模块", "6 个", INK, vs=32).to_corner(UR, buff=0.5)
            self.play(FadeIn(six), run_time=0.6)
        with self.say("m4") as d:
            ln = T("非情绪模块", 26, BLUE).next_to(mods[1], DOWN, buff=0.15)
            le = T("情绪模块", 26, RED).next_to(mods[4], DOWN, buff=0.15)
            self.play(FadeIn(ln), FadeIn(le), run_time=0.6)
            big = VGroup(*[Arrow(mods[i][0].get_right(), mods[j][0].get_left(), buff=0.1, color=GOLD, stroke_width=7)
                           for i, j in ((0, 3), (2, 3), (2, 4), (1, 4))])
            back = Arrow(mods[3][0].get_bottom() + LEFT * 0.4, mods[2][0].get_right() + DOWN * 0.3, buff=0.1, color=MUTED, stroke_width=2, tip_length=0.15)
            self.play(LaggedStart(*[GrowArrow(a) for a in big], lag_ratio=0.2), run_time=1.6)
            self.play(GrowArrow(back), run_time=0.6)
            sk = T("示意", 20, MUTED).to_corner(DR, buff=0.4)
            self.play(FadeIn(sk), run_time=0.3)
        with self.say("m5") as d:
            self.play(FadeOut(mods), FadeOut(ln), FadeOut(le), FadeOut(big), FadeOut(back), FadeOut(sk), run_time=0.6)
            items = VGroup(*[self.node(s, ORIGIN, c, 22) for s, c in (("失眠量表 第4条", BLUE), ("压力量表 第2条", GREEN), ("压力量表 第7条", GREEN))])
            for it_ in items:
                it_[0].stretch_to_fit_width(2.8)
            items.arrange(RIGHT, buff=0.4).move_to(UP * 0.2)
            self.play(LaggedStart(*[FadeIn(i_, scale=0.8) for i_ in items], lag_ratio=0.3), run_time=1.4)
        with self.say("m5b") as d:
            cav = T("截面数据 · 需要纵向和干预研究检验", 24, MUTED).next_to(items, DOWN, buff=0.6)
            self.play(FadeIn(cav), run_time=0.8)
        self.fade_all()

    # ------------------------------------------------------------------ recap
    def recap(self):
        recap_slide(self, ["疾病 = 症状相互作用形成的稳定状态", "用正则化偏相关估计，而非简单相关", "中心性 ≠ 靶点；必须报告稳定性"])
        with self.say("z5") as d:
            self.clip_on("symptom_demo.mp4", "full", "本站交互演示：相关与偏相关症状网络", start=0.3)
        with self.say("z5b") as d:
            pass
        self.clip_off()
        self.wait(1.0)
