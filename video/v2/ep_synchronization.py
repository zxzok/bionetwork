"""Animated explainer: 同步与协同动力学 (Kuramoto model, order parameter, network thresholds, Laplacian, consensus)."""
import colorsys
import random

import networkx as nx
import numpy as np
from scipy.stats import norm

from common import *  # noqa: F401,F403
from bhelp import NetView, fit, counter, axes, legend, parts_slide, recap_slide, show_clip

TITLE = "同步：从摆钟、萤火虫到心跳"

LINES = {
    # hook
    "h1": "1665年，惠更斯注意到一件怪事。挂在同一根横梁上的两只摆钟，过一段时间，摆动会变得严格反相——一只往左，另一只就往右。",
    "h2": "原因是横梁微小的振动。它把两只钟悄悄地连在了一起，物理上叫作耦合。",
    "h2b": "画面是研究者在实验室里，重现的惠更斯摆钟实验。",
    "h3": "东南亚的某些萤火虫也是这样。一开始各闪各的，慢慢地，整群一起明灭。",
    "h3b": "这是真实的萤火虫群，在夜色里同步闪光。",
    "h4": "心脏里的起搏细胞、大脑里的神经元，也都在做类似的事。",
    "h5": "一群节奏各不相同的个体，没有指挥，也能变得步调一致。这一期，我们就把其中的道理讲清楚。",
    "pa0": "这一期分三部分来讲。",
    "pa1": "第一部分，怎样度量同步，同步又是怎样突然出现的。",
    "pa2": "第二部分，网络结构怎样影响同步。",
    "pa3": "第三部分，心脏、生物钟和大脑里的同步。",
    # order parameter
    "o1": "先看第一部分。我们把问题简化：每个周期性变化的个体，叫一个振荡器。只用一个相位来描述它，就是单位圆上转圈的一个点。",
    "o2": "每个点有自己的固有频率，也就是没人干扰时转圈的快慢。下面的色条表示：蓝色转得慢，红色转得快。",
    "o3": "1975年，藏本提出了一个极简的模型，写在右上角：每个振荡器，都被其他振荡器拉向它们的相位。",
    "o3b": "等号左边，是相位变化的速度。右边第一项，是它自己的固有频率；第二项，是其他所有振荡器对它的拉力之和。",
    "o4": "落后的被拉快一点，领先的被拉慢一点。拉力的大小由 K 决定，K 叫耦合强度。",
    "o5": "同步的程度，可以这样度量：把所有点的位置取平均，得到它们的质心，就是这个黄色的点。",
    "o6": "【慢】质心到圆心的距离，叫序参量，写作 r。相位均匀散开时，r 接近零；完全同步时，r 等于一。",
    "o6b": "右边的式子就是质心的定义：把每个点看成从圆心指向它的箭头，所有箭头加起来，再除以总数。得到的箭头有多长，r 就是多少。",
    # phase transition
    "p1": "现在让这群振荡器动起来。上面的 K 是耦合强度，下面的 r 是序参量。先把耦合调得很弱。",
    "p2": "大家各转各的，序参量只在一个很小的值附近波动。",
    "p3": "把耦合调过某个临界值。一大部分振荡器聚到了一起，形成一个步调一致的团，叫同步簇。",
    "p4": "注意画了圈的这几个。它们的固有频率特别快或特别慢，仍然在圆上独自漂移。",
    "p5": "右边这张图，横轴是耦合强度，纵轴是序参量。过了红色虚线标出的临界点，曲线迅速上升。",
    "p5b": "【慢】这种突然的转变，叫同步相变。",
    "p6": "理论上，临界耦合可以写成上面这个式子。",
    "p6b": "分母里的 g 零，是固有频率分布在中心处的高度。左边这条绿色曲线，就是频率的分布。",
    "p6c": "分布越扁，频率越分散，中心高度越低，临界耦合就越大。也就是说，频率越分散，越难同步。",
    # network threshold
    "q1": "下面进入第二部分。把振荡器放到网络上，每个节点只和自己的邻居耦合。节点的颜色，表示它的相位。",
    "q2": "这时，临界耦合等于一个常数，乘以连接数的平均，再除以连接数平方的平均。",
    "q2b": "式子里，K 零是刚才全连接时的临界值。分子是连接数的平均；分母是连接数平方的平均，枢纽会把它抬得很高。",
    "q3": "【慢】这和传播里的流行病阈值，形式完全一样。连接数越不均匀，阈值越低。",
    "q4": "我们在平均连接数相同的随机网络和无标度网络上，各做一次模拟。横轴是耦合强度，纵轴是序参量。",
    "q5": "蓝色是无标度网络。它的曲线更早离开零附近，因为枢纽先和邻居同步，再把同步扩散出去。",
    "q6": "不过耦合变大以后，灰色的随机网络反而追了上来。开始同步，和完全同步，是两个不同的问题。",
    # eigenratio
    "e1": "下面看完全同步。对完全相同的振荡器，同步能不能稳住，答案藏在一个叫拉普拉斯矩阵的东西里。",
    "e1b": "拉普拉斯矩阵写作 L，等于 D 减 A。A 记录谁和谁相连，D 记录每个节点的连接数。",
    "e2": "这个矩阵有一组特征值，可以理解成描述它的一组特征数字。最大的特征值，除以第二小的特征值，叫特征值比。",
    "e2b": "【慢】特征值比越小，网络越容易稳定地同步。",
    "e3": "看这个二十四个节点的环，特征值比将近六十。我们往里加捷径，也就是直接连到远处节点的线。",
    "e4": "第一条捷径，比值反而略升了一点。再多加几条，它降到了原来的一半以下。",
    "e5": "这就是小世界结构利于同步的原因：长程的捷径，让远处的节点可以直接对表。",
    "e6": "反过来，在刚才那两张网络里，无标度网络的特征值比，是随机网络的两倍左右。枢纽抬高了最大特征值，完全同步反而更难。",
    # consensus & hierarchy
    "c1": "如果每个节点只有一个数值，不断向邻居看齐，就得到共识动力学。圈里的数字，就是每个节点的数值。",
    "c2": "在连通的网络上，大家最终都会到达初始值的平均，这里是五。",
    "c3": "收敛有多快，由第二小特征值决定，它也叫代数连通度。",
    "c3b": "左边五个点连成一条链，它约为零点三八；右边五个点两两相连，它等于五。",
    "c4": "我们从头再放一遍。右边两两相连的这一组，达成共识要快十几倍。",
    "c5": "如果网络里有明显的社团，也就是内部连接紧、彼此之间连接少的几群节点，同步会分层出现。",
    "c6": "右边的图，横轴是时间。绿色是社团内部的同步程度，黄色是全网的同步程度。",
    "c6b": "【慢】先是每个社团内部步调一致，然后社团之间，才慢慢对齐。",
    # biology
    "b1": "最后是第三部分。心脏的节律，来自窦房结里许多起搏细胞的相互牵引，而不是某一个细胞说了算。",
    "b1b": "画面是实验室里培养的心肌细胞，它们在培养皿里自发地跳动。",
    "b2": "主生物钟在下丘脑的视交叉上核，大约有两万个神经元。",
    "b3": "把它们分散培养，单个神经元仍保持近二十四小时的节律，但相位彼此独立。左边的小钟，指针各指一方。",
    "b3b": "在完整的组织里，它们彼此耦合，整体节律才精确一致，就像右边这组小钟。",
    "b4": "在帕金森病中，基底节环路里贝塔频段的同步异常增强，与运动迟缓有关。上下两条线，是正常和同步增强的信号示意。",
    "b5": "【慢】所以对大脑来说，同步不是越强越好，关键是分离与整合之间的平衡。",
    # recap
    "z1": "好，我们来总结一下。",
    "z2": "第一，序参量是相位质心的长度；耦合超过临界值，系统进入部分同步。",
    "z3": "第二，连接数越不均匀，同步越早开始；但完全同步能不能稳住，要看拉普拉斯矩阵的特征值。",
    "z4": "第三，在生命系统里，同步过强或过弱，都可能意味着疾病。",
    "z5": "这个专题的知识页面里，有画面上的这个交互演示。先把耦合强度调到零，各个振荡器各转各的。",
    "z5b": "再慢慢把耦合调大。你看，它们逐渐聚成一团，下面的序参量曲线也跟着升了上去。",
}


def hue(theta, s=0.65, v=1.0):
    r, g, b = colorsys.hsv_to_rgb((theta % (2 * np.pi)) / (2 * np.pi), s, v)
    return ManimColor.from_rgb((r, g, b))


def freq_color(w, wmax):
    t = float(np.clip((w + wmax) / (2 * wmax), 0, 1))
    if t < 0.5:
        return interpolate_color(ManimColor(BLUE), ManimColor(GREEN), t * 2)
    return interpolate_color(ManimColor(GREEN), ManimColor(RED), (t - 0.5) * 2)


def kuramoto_net(G, K, w, th0, T, dt=0.05, record=False):
    idx = {v: i for i, v in enumerate(G)}
    E = np.array([(idx[u], idx[v]) for u, v in G.edges()])
    th = th0.copy(); traj = [th.copy()]; rs = []
    for s in range(int(T / dt)):
        d = np.sin(th[E[:, 1]] - th[E[:, 0]]); f = np.zeros_like(th)
        np.add.at(f, E[:, 0], d); np.add.at(f, E[:, 1], -d)
        th = th + dt * (w + K * f)
        if record:
            traj.append(th.copy())
        if s * dt > T / 2:
            rs.append(abs(np.exp(1j * th).mean()))
    return (np.array(traj) if record else None), float(np.mean(rs)) if rs else 0.0


def threshold_nets():
    Gb = nx.barabasi_albert_graph(300, 2, seed=2)
    Ge = nx.gnm_random_graph(300, Gb.number_of_edges(), seed=2)
    return Gb, Ge


def eigenratio(G):
    L = nx.laplacian_matrix(G).toarray().astype(float)
    ev = np.sort(np.linalg.eigvalsh(L))
    return ev[-1] / ev[1]


class Ring:
    """N phase oscillators drawn on a unit circle, with the centroid (order parameter) arrow."""

    def __init__(self, w, center, R=2.3, seed=0):
        self.w, self.c, self.R = np.asarray(w, float), np.array(center, float), R
        self.th = np.random.default_rng(seed).uniform(0, 2 * np.pi, len(w))
        wm = np.abs(self.w).max()
        self.circle = Circle(radius=R, color=MUTED, stroke_width=2).move_to(self.c)
        self.dots = VGroup(*[Dot(radius=0.085, color=freq_color(x, wm)) for x in self.w])
        self.cdot = Dot(radius=0.1, color=GOLD)
        self.cline = Line(self.c, self.c + RIGHT * 0.01, color=GOLD, stroke_width=5)
        self.place(self.th)

    def p(self, th):
        return self.c + self.R * np.array([np.cos(th), np.sin(th), 0])

    def z(self, th):
        return np.exp(1j * th).mean()

    def place(self, th):
        for d, t in zip(self.dots, th):
            d.move_to(self.p(t))
        z = self.z(th)
        end = self.c + self.R * np.array([z.real, z.imag, 0])
        if np.linalg.norm(end - self.c) < 0.01:
            end = self.c + RIGHT * 0.01
        self.cline.put_start_and_end_on(self.c, end)
        self.cdot.move_to(end)

    def simulate(self, K, T, dt=0.02):
        traj = [self.th.copy()]
        th = self.th.copy()
        for _ in range(int(T / dt)):
            z = self.z(th)
            th = th + dt * (self.w + K * abs(z) * np.sin(np.angle(z) - th))
            traj.append(th.copy())
        self.th = th
        return np.array(traj)

    def anim(self, traj, extra=None):
        mob = VGroup(self.dots, self.cline, self.cdot)

        def upd(m, a):
            i = min(len(traj) - 1, int(a * (len(traj) - 1)))
            self.place(traj[i])
            if extra:
                extra(traj[i])
        return UpdateFromAlphaFunc(mob, upd, rate_func=linear)


class Episode(Narrated):
    LINES = LINES

    def construct(self):
        self.hook()
        parts_slide(self, ["一  度量同步：序参量与同步相变", "二  网络结构与同步", "三  生命中的节律"], keys=("pa0", "pa1", "pa2", "pa3"))
        self.order()
        self.transition()
        self.network()
        self.eigen()
        self.consensus()
        self.biology()
        self.recap()

    def fade_all(self, rt=0.8, keep=()):
        self.play(*[FadeOut(m) for m in self.mobjects if m not in keep], run_time=rt)

    # ------------------------------------------------------------------ hook
    def hook(self):
        beam = Line(LEFT * 4.2, RIGHT * 4.2, color=INK, stroke_width=8).shift(UP * 2.4)
        piv = [np.array([-2.0, 2.4, 0]), np.array([2.0, 2.4, 0])]
        L = 3.0
        rods = VGroup(*[Line(p, p + DOWN * L, color=MUTED, stroke_width=4) for p in piv])
        bobs = VGroup(Dot(radius=0.3, color=BLUE), Dot(radius=0.3, color=GOLD))
        for b, r in zip(bobs, rods):
            b.move_to(r.get_end())
        year = T("1665", 34, MUTED).to_corner(UL, buff=0.5)
        Om, A = 2 * np.pi / 1.6, 0.42

        def pend(delta_of_a, t0, dur):
            def upd(m, a):
                t = t0 + a * dur
                ph = [Om * t, Om * t + delta_of_a(a)]
                wob = 0.03 * np.sin(Om * t) * (1 - abs(np.cos(delta_of_a(a) / 2)))
                beam.move_to(UP * 2.4 + RIGHT * wob)
                for k in range(2):
                    ang = A * np.sin(ph[k])
                    p0 = piv[k] + RIGHT * wob
                    end = p0 + L * np.array([np.sin(ang), -np.cos(ang), 0])
                    rods[k].put_start_and_end_on(p0, end)
                    bobs[k].move_to(end)
            return UpdateFromAlphaFunc(VGroup(beam, rods, bobs), upd, rate_func=linear, run_time=dur)
        with self.say("h1") as d:
            self.play(FadeIn(year), Create(beam), FadeIn(rods), FadeIn(bobs), run_time=0.8)
            dur = d - 0.6
            self.play(pend(lambda a: 0.7 + (np.pi - 0.7) * (1 - np.exp(-4 * a)) / (1 - np.exp(-4)), 0, dur))
        with self.say("h2") as d:
            hl = SurroundingRectangle(beam, color=GOLD, buff=0.12)
            self.play(Create(hl), pend(lambda a: np.pi, 0, 1.4))
            self.play(FadeOut(hl), pend(lambda a: np.pi, 1.4, max(0.5, d - 2.2)))
        show_clip(self, "h2b", "yt_huygens_clocks.mp4", "center", "视频：Jonatan Peña Ramirez · YouTube", start=5, min_len=6)
        # fireflies
        rng = np.random.default_rng(7)
        n = 46
        pts = [np.array([rng.uniform(-6, 6), rng.uniform(-3, 3), 0]) for _ in range(n)]
        flies = VGroup(*[Dot(p, radius=0.09, color=GOLD) for p in pts])
        glows = VGroup(*[Dot(p, radius=0.28, color=GOLD).set_opacity(0.25) for p in pts])
        w = rng.normal(2 * np.pi * 0.7, 0.35, n)
        th = rng.uniform(0, 2 * np.pi, n)

        def bright(t):
            return ((1 + np.cos(t)) / 2) ** 10

        def run_flies(K, dur):
            nonlocal th
            dt = 1 / 30
            traj = [th.copy()]
            for _ in range(int(dur / dt)):
                z = np.exp(1j * th).mean()
                th = th + dt * (w + K * abs(z) * np.sin(np.angle(z) - th))
                traj.append(th.copy())
            traj = np.array(traj)

            def upd(m, a):
                i = min(len(traj) - 1, int(a * (len(traj) - 1)))
                b = bright(traj[i])
                for f, g, x in zip(flies, glows, b):
                    f.set_opacity(0.08 + 0.92 * x)
                    g.set_opacity(0.3 * x)
            return UpdateFromAlphaFunc(VGroup(flies, glows), upd, rate_func=linear, run_time=dur)
        flies.set_opacity(0.1); glows.set_opacity(0)
        self.add(glows, flies)
        with self.say("h3") as d:
            self.play(run_flies(0.0, d * 0.35))
            self.play(run_flies(2.5, d * 0.65))
        show_clip(self, "h3b", "yt_fireflies_natgeo.mp4", "center", "视频：National Geographic · YouTube", start=30, min_len=6)
        self.add(glows, flies)
        with self.say("h4") as d:
            self.play(run_flies(2.5, d))
        with self.say("h5") as d:
            q = T("没有指挥，也能步调一致", 54, GOLD, weight=BOLD)
            self.play(run_flies(2.5, 1.2))
            self.play(FadeOut(flies), FadeOut(glows), Write(q), run_time=1.2)
        self.play(FadeOut(q), run_time=0.6)

    # ------------------------------------------------------------------ order parameter
    def order(self):
        tag = self.chapter("一  度量同步：序参量")
        N = 40
        w = norm.ppf((np.arange(N) + 0.5) / N)
        ring = Ring(w, LEFT * 2.6 + DOWN * 0.2, seed=1)
        with self.say("o1") as d:
            self.play(FadeIn(tag), Create(ring.circle), run_time=1.0)
            one = ring.dots[N // 2]
            self.play(FadeIn(one), run_time=0.4)
            t0 = ring.th[N // 2]
            self.play(UpdateFromAlphaFunc(one, lambda m, a: m.move_to(ring.p(t0 + 2 * np.pi * a)), rate_func=linear), run_time=d * 0.5)
            ring.th[N // 2] = t0 + 2 * np.pi
        with self.say("o2") as d:
            self.play(FadeIn(ring.dots), run_time=0.6)
            sc = VGroup(T("慢", 24, BLUE), Rectangle(width=2.6, height=0.18, stroke_width=0, fill_opacity=1)
                        .set_color_by_gradient(BLUE, GREEN, RED), T("快", 24, RED)).arrange(RIGHT, buff=0.2)
            sc.next_to(ring.circle, DOWN, buff=0.35)
            traj = ring.simulate(0.0, d - 1.0)
            self.play(ring.anim(traj), FadeIn(sc), run_time=d - 1.0)
        eq = MathTex(r"\frac{d\theta_i}{dt}", r"=", r"\omega_i", r"+", r"\frac{K}{N}\sum_j \sin(\theta_j-\theta_i)", font_size=44)
        eq.move_to(RIGHT * 3.4 + UP * 1.9)
        eq[2].set_color(GREEN); eq[4].set_color(GOLD)
        with self.say("o3") as d:
            traj = ring.simulate(0.0, d)
            self.play(ring.anim(traj), Write(eq, run_time=min(2.5, d * 0.6)), run_time=d)
        with self.say("o3b") as d:
            b1 = Brace(eq[0], DOWN, color=INK); t1 = T("相位变化的速度", 20).next_to(b1, DOWN, buff=0.08).shift(RIGHT * 0.2)
            b2 = Brace(eq[2], DOWN, color=GREEN); t2 = T("固有频率", 20, GREEN).next_to(b2, DOWN, buff=0.08).shift(DOWN * 0.42 + RIGHT * 0.5)
            b3 = Brace(eq[4], DOWN, color=GOLD); t3 = T("其他振荡器的拉力", 20, GOLD).next_to(b3, DOWN, buff=0.08)
            traj = ring.simulate(0.0, d)
            self.play(ring.anim(traj), Succession(AnimationGroup(GrowFromCenter(b1), FadeIn(t1)), Wait(0.6),
                                                   AnimationGroup(GrowFromCenter(b2), FadeIn(t2)), Wait(0.6),
                                                   AnimationGroup(GrowFromCenter(b3), FadeIn(t3)), run_time=min(4.5, d * 0.8)), run_time=d)
        self.play(*[FadeOut(x) for x in (b1, t1, b2, t2, b3, t3)], run_time=0.4)
        with self.say("o4") as d:
            kl = VGroup(MathTex("K", font_size=44, color=GOLD), T("耦合强度", 26, GOLD)).arrange(RIGHT, buff=0.2).next_to(eq, DOWN, buff=0.4)
            traj = ring.simulate(1.2, d)
            self.play(ring.anim(traj), FadeIn(kl, run_time=1.0), run_time=d)
        # static examples of r
        with self.say("o5") as d:
            traj = ring.simulate(1.2, 1.0)
            self.play(ring.anim(traj), run_time=1.0)
            self.add(ring.cline, ring.cdot)
            self.play(FadeIn(ring.cline), FadeIn(ring.cdot), Flash(ring.cdot, color=GOLD), run_time=1.0)
        rdef = MathTex(r"r\,e^{i\psi}=\frac{1}{N}\sum_j e^{i\theta_j}", font_size=44).move_to(RIGHT * 3.4 + DOWN * 0.9)
        rv = DecimalNumber(abs(ring.z(ring.th)), num_decimal_places=2, font_size=44, color=GOLD)
        rlab = VGroup(MathTex("r=", font_size=44, color=GOLD), rv).arrange(RIGHT, buff=0.1).next_to(rdef, DOWN, buff=0.4)
        with self.say("o6") as d:
            self.play(Write(rdef), FadeIn(rlab), run_time=1.0)
            traj = ring.simulate(0.0, 0.1)
            spread_th = np.linspace(0, 2 * np.pi, N, endpoint=False)
            tight = np.full(N, 0.6) + np.linspace(-0.12, 0.12, N)
            start = ring.th.copy()

            def morph(a_from, a_to, dur):
                def upd(m, a):
                    th = a_from + (a_to - a_from) * smooth(a)
                    ring.place(th)
                    rv.set_value(abs(ring.z(th)))
                return UpdateFromAlphaFunc(VGroup(ring.dots, ring.cline, ring.cdot, rv), upd, run_time=dur)
            # unwrap so dots travel the short way
            tgt = spread_th + 2 * np.pi * np.round((start - spread_th) / (2 * np.pi))
            self.play(morph(start, tgt, 1.6))
            self.wait(0.6)
            tgt2 = tight + 2 * np.pi * np.round((tgt - tight) / (2 * np.pi))
            self.play(morph(tgt, tgt2, 1.6))
        with self.say("o6b") as d:
            bl = Brace(rdef, UP, color=GOLD); tl_ = T("所有箭头的平均", 20, GOLD).next_to(bl, UP, buff=0.08)
            arrows = VGroup(*[Line(ring.c, dd.get_center(), color=MUTED, stroke_width=1.2) for dd in ring.dots])
            self.play(FadeOut(eq), FadeOut(kl), Create(arrows), run_time=1.0)
            self.play(GrowFromCenter(bl), FadeIn(tl_), run_time=0.8)
            self.play(Indicate(ring.cline, color=GOLD), run_time=1.0)
        self.fade_all()

    # ------------------------------------------------------------------ transition
    def transition(self):
        tag = self.chapter("一  度量同步：同步相变")
        N = 60
        w = norm.ppf((np.arange(N) + 0.5) / N)
        ring = Ring(w, LEFT * 3.3 + DOWN * 0.1, R=2.4, seed=3)
        rv = DecimalNumber(abs(ring.z(ring.th)), num_decimal_places=2, font_size=40, color=GOLD)
        rl = VGroup(MathTex("r=", font_size=40, color=GOLD), rv).arrange(RIGHT, buff=0.1).next_to(ring.circle, DOWN, buff=0.25)
        kv = DecimalNumber(0.5, num_decimal_places=1, font_size=40, color=INK)
        kl = VGroup(MathTex("K=", font_size=40), kv).arrange(RIGHT, buff=0.1).next_to(ring.circle, UP, buff=0.2)

        def ex(th):
            rv.set_value(abs(np.exp(1j * th).mean()))
        with self.say("p1") as d:
            self.play(FadeIn(tag), Create(ring.circle), FadeIn(ring.dots), FadeIn(ring.cline), FadeIn(ring.cdot), FadeIn(rl), FadeIn(kl), run_time=1.2)
            self.play(ring.anim(ring.simulate(0.5, d - 1.4), ex), run_time=d - 1.4)
        with self.say("p2") as d:
            self.play(ring.anim(ring.simulate(0.5, d), ex), run_time=d)
        with self.say("p3") as d:
            self.play(kv.animate.set_value(2.5), ring.anim(ring.simulate(1.5, 0.8), ex), run_time=0.8)
            self.play(ring.anim(ring.simulate(2.5, d - 0.8), ex), run_time=d - 0.8)
        with self.say("p4") as d:
            drift = [0, 1, N - 2, N - 1]
            rings = VGroup(*[Circle(radius=0.2, color=INK, stroke_width=2).move_to(ring.dots[i]) for i in drift])
            for r_, i in zip(rings, drift):
                r_.add_updater(lambda m, i=i: m.move_to(ring.dots[i]))
            self.add(rings)
            self.play(ring.anim(ring.simulate(2.5, d), ex), run_time=d)
            for r_ in rings:
                r_.clear_updaters()
            self.remove(rings)
        # r(K) curve, mean field with N=500
        Nb = 500
        wb = norm.ppf((np.arange(Nb) + 0.5) / Nb)
        rng = np.random.default_rng(4)
        Ks = np.arange(0, 4.01, 0.2)
        rs = []
        for K in Ks:
            th = rng.uniform(0, 2 * np.pi, Nb); acc = []
            for s in range(800):
                z = np.exp(1j * th).mean()
                th = th + 0.05 * (wb + K * abs(z) * np.sin(np.angle(z) - th))
                if s > 400:
                    acc.append(abs(z))
            rs.append(np.mean(acc))
        ax = axes([0, 4, 1], [0, 1, 0.5], 5.2, 3.6, xn=[0, 1, 2, 3, 4], yn=[0, 0.5, 1]).move_to(RIGHT * 3.6 + DOWN * 0.2)
        xl = MathTex("K", font_size=34, color=MUTED).next_to(ax.x_axis, DOWN, buff=0.3)
        yl = MathTex("r", font_size=34, color=MUTED).next_to(ax.y_axis, LEFT, buff=0.3)
        curve = ax.plot_line_graph(Ks, rs, line_color=GOLD, add_vertex_dots=False, stroke_width=5)
        kc = 2 / (np.pi * norm.pdf(0))
        with self.say("p5") as d:
            self.play(Create(ax), FadeIn(xl), FadeIn(yl), ring.anim(ring.simulate(2.5, 1.2), ex), run_time=1.2)
            self.play(Create(curve), ring.anim(ring.simulate(2.5, d * 0.5), ex), run_time=d * 0.5)
            crit = DashedLine(ax.c2p(kc, 0), ax.c2p(kc, 1), color=RED)
            cl = MathTex("K_c", font_size=34, color=RED).next_to(ax.c2p(kc, 1), UP, buff=0.1)
            self.play(Create(crit), FadeIn(cl), ring.anim(ring.simulate(2.5, 1.0), ex), run_time=1.0)
        with self.say("p5b") as d:
            self.play(Indicate(curve, color=GOLD), ring.anim(ring.simulate(2.5, d), ex), run_time=d)
        with self.say("p6") as d:
            f = MathTex(r"K_c=\frac{2}{\pi\, g(0)}", font_size=50, color=RED).next_to(ax, UP, buff=0.5).shift(LEFT * 0.4)
            self.play(Write(f), ring.anim(ring.simulate(2.5, 1.4), ex), run_time=1.4)
        with self.say("p6b") as d:
            self.play(*[FadeOut(m) for m in (ring.circle, ring.dots, ring.cline, ring.cdot, rl, kl)], run_time=0.6)
            ia = axes([-3, 3, 1], [0, 0.9, 0.3], 4.6, 2.6).move_to(LEFT * 3.4 + DOWN * 0.6)
            il = VGroup(T("固有频率的分布", 22, GREEN), MathTex("g(\\omega)", font_size=30, color=GREEN)).arrange(RIGHT, buff=0.15).next_to(ia, UP, buff=0.3)
            narrow = ia.plot(lambda x: 0.8 * np.exp(-(x / 0.6) ** 2), x_range=[-3, 3], color=GREEN, stroke_width=4)
            wide = ia.plot(lambda x: 0.32 * np.exp(-(x / 1.5) ** 2), x_range=[-3, 3], color=GREEN, stroke_width=4)
            mark = Dot(ia.c2p(0, 0.8), color=RED, radius=0.08)
            self.play(Create(ia), FadeIn(il), Create(narrow), FadeIn(mark), run_time=1.0)
            gl0 = T("中心高度 g(0)", 20, RED).next_to(mark, RIGHT, buff=0.15)
            self.play(FadeIn(gl0), Indicate(f, color=RED), run_time=1.0)
        with self.say("p6c") as d:
            self.play(Transform(narrow, wide), mark.animate.move_to(ia.c2p(0, 0.32)), gl0.animate.next_to(ia.c2p(0, 0.32), RIGHT, buff=0.25),
                      run_time=max(1.0, d * 0.5))
        self.fade_all()

    # ------------------------------------------------------------------ network threshold
    def network(self):
        tag = self.chapter("二  网络结构：同步阈值")
        G = nx.barabasi_albert_graph(70, 2, seed=5)
        pos = fit(nx.kamada_kawai_layout(G), (-6.4, -0.6, -3.0, 2.8))
        v = NetView(G, pos, color=MUTED, eo=0.3)
        rng = np.random.default_rng(5)
        w = rng.normal(0, 0.4, G.number_of_nodes())
        th0 = rng.uniform(0, 2 * np.pi, G.number_of_nodes())
        nodes = list(G)

        def color_run(traj, dur):
            def upd(m, a):
                i = min(len(traj) - 1, int(a * (len(traj) - 1)))
                for j, x in enumerate(nodes):
                    v.dots[x].set_color(hue(traj[i, j]))
            return UpdateFromAlphaFunc(VGroup(*v.dots.values()), upd, rate_func=linear, run_time=dur)
        with self.say("q1") as d:
            self.play(FadeIn(tag), FadeIn(v.group), run_time=1.0)
            traj, _ = kuramoto_net(G, 0.25, w + 1.5, th0, d - 1.0, dt=1 / 15, record=True)
            self.play(color_run(traj, d - 1.0))
        th1 = traj[-1]
        with self.say("q2") as d:
            f = MathTex(r"K_c", r"=", r"K_0\,", r"\frac{\langle k\rangle}{\langle k^2\rangle}", font_size=60).move_to(RIGHT * 3.4 + UP * 1.6)
            f[0].set_color(GOLD); f[3].set_color(GOLD)
            traj, _ = kuramoto_net(G, 0.25, w + 1.5, th1, d, dt=1 / 15, record=True)
            self.play(Write(f, run_time=1.6), color_run(traj, d))
        th1 = traj[-1]
        with self.say("q2b") as d:
            labs = VGroup(VGroup(MathTex("K_0", font_size=34), T("全连接时的临界值", 22)).arrange(RIGHT, buff=0.2),
                          VGroup(MathTex(r"\langle k\rangle", font_size=34, color=GOLD), T("连接数的平均", 22, GOLD)).arrange(RIGHT, buff=0.2),
                          VGroup(MathTex(r"\langle k^2\rangle", font_size=34, color=GOLD), T("连接数平方的平均", 22, GOLD)).arrange(RIGHT, buff=0.2)
                          ).arrange(DOWN, aligned_edge=LEFT, buff=0.3).next_to(f, DOWN, buff=0.6)
            traj, _ = kuramoto_net(G, 0.25, w + 1.5, th1, d, dt=1 / 15, record=True)
            self.play(Succession(*[FadeIn(x, shift=UP * 0.2) for x in labs], lag_ratio=1.0, run_time=min(3.0, d * 0.6)), color_run(traj, d))
        th1 = traj[-1]
        self.play(FadeOut(labs), run_time=0.4)
        with self.say("q3") as d:
            g = MathTex(r"\lambda_c", r"=", r"\frac{\langle k\rangle}{\langle k^2\rangle}", font_size=60).next_to(f, DOWN, buff=0.8)
            g[0].set_color(RED); g[2].set_color(GOLD)
            ttl = T("传播阈值", 24, RED).next_to(g, DOWN, buff=0.2)
            traj, _ = kuramoto_net(G, 0.25, w + 1.5, th1, d, dt=1 / 15, record=True)
            self.play(Write(g, run_time=1.2), FadeIn(ttl, run_time=1.2), color_run(traj, d))
            self.play(Indicate(f[3], color=GOLD), Indicate(g[2], color=GOLD), run_time=1.0)
        self.fade_all()
        Gb, Ge = threshold_nets()
        rng = np.random.default_rng(0)
        w = rng.normal(0, 1, 300); w -= w.mean()
        th0 = rng.uniform(0, 2 * np.pi, 300)
        Ks = np.arange(0, 1.01, 0.05)
        th0s = [np.random.default_rng(s_).uniform(0, 2 * np.pi, 300) for s_ in range(3)]
        rb = [np.mean([kuramoto_net(Gb, K, w, t_, 60)[1] for t_ in th0s]) for K in Ks]
        re = [np.mean([kuramoto_net(Ge, K, w, t_, 60)[1] for t_ in th0s]) for K in Ks]
        self.sync_curves = (Ks, rb, re)
        tag = self.chapter("二  网络结构：同步阈值")
        ax = axes([0, 1, 0.2], [0, 1, 0.5], 8.6, 4.6, xn=[0, 0.2, 0.4, 0.6, 0.8, 1.0], yn=[0, 0.5, 1]).shift(DOWN * 0.4 + LEFT * 0.6)
        xl = T("耦合强度", 22, MUTED).next_to(ax.x_axis, DOWN, buff=0.4)
        yl = T("序参量", 22, MUTED).rotate(PI / 2).next_to(ax.y_axis, LEFT, buff=0.35)
        lg = legend([(BLUE, "无标度网络"), (MUTED, "随机网络")]).to_corner(UR, buff=0.5).shift(DOWN * 0.6)
        cb = ax.plot_line_graph(Ks, rb, line_color=BLUE, add_vertex_dots=False, stroke_width=5)
        ce = ax.plot_line_graph(Ks, re, line_color=MUTED, add_vertex_dots=False, stroke_width=5)
        with self.say("q4") as d:
            self.play(FadeIn(tag), Create(ax), FadeIn(xl), FadeIn(yl), FadeIn(lg), run_time=d * 0.5)
        with self.say("q5") as d:
            self.play(Create(ce), Create(cb), run_time=d * 0.6, rate_func=linear)
            zone = ax.get_area(ax.plot(lambda x: 1, x_range=[0.1, 0.4]), x_range=[0.1, 0.4], color=BLUE, opacity=0.15)
            self.play(FadeIn(zone), run_time=0.8)
        with self.say("q6") as d:
            zone2 = ax.get_area(ax.plot(lambda x: 1, x_range=[0.7, 1.0]), x_range=[0.7, 1.0], color=MUTED, opacity=0.15)
            self.play(FadeOut(zone), FadeIn(zone2), run_time=1.0)
        self.fade_all()

    # ------------------------------------------------------------------ eigenratio
    def eigen(self):
        tag = self.chapter("二  网络结构：完全同步")
        n = 24
        G = nx.cycle_graph(n)
        pos = {i: np.array([2.6 * np.cos(2 * np.pi * i / n + PI / 2), 2.6 * np.sin(2 * np.pi * i / n + PI / 2), 0]) + LEFT * 3.0 + DOWN * 0.3
               for i in range(n)}
        dots = VGroup(*[Dot(pos[i], radius=0.1, color=BLUE) for i in range(n)])
        edges = VGroup(*[Line(pos[u], pos[v], color=BLUE, stroke_opacity=0.6, stroke_width=2) for u, v in G.edges()])
        f = MathTex(r"L=D-A", font_size=46).move_to(RIGHT * 3.2 + UP * 2.2)
        f2 = MathTex(r"\frac{\mu_N}{\mu_2}", font_size=60, color=GOLD).move_to(RIGHT * 3.0 + UP * 0.2)
        with self.say("e1") as d:
            self.play(FadeIn(tag), Create(edges), FadeIn(dots), run_time=1.2)
        with self.say("e1b") as d:
            self.play(Write(f), run_time=1.0)
            fl = VGroup(T("A：谁和谁相连", 20, MUTED), T("D：每个节点的连接数", 20, MUTED)).arrange(DOWN, aligned_edge=LEFT, buff=0.12).next_to(f, DOWN, buff=0.2)
            self.play(FadeIn(fl), run_time=0.8)
        with self.say("e2") as d:
            self.play(Write(f2), run_time=1.2)
            fl2 = VGroup(T("最大特征值", 20, GOLD).next_to(f2, RIGHT, buff=0.3).shift(UP * 0.4),
                         T("第二小特征值", 20, GOLD).next_to(f2, RIGHT, buff=0.3).shift(DOWN * 0.4))
            self.play(FadeIn(fl2), run_time=0.8)
        with self.say("e2b") as d:
            lab = T("越小越容易同步", 26, GOLD).next_to(f2, DOWN, buff=0.3)
            self.play(FadeIn(lab), run_time=0.6)
        er0 = eigenratio(G)
        cnt = counter("特征值比", f"{er0:.1f}", GOLD, vs=46).move_to(RIGHT * 3.2 + DOWN * 1.6)
        with self.say("e3") as d:
            self.play(FadeOut(lab), FadeIn(cnt), run_time=0.8)
        r = random.Random(1)
        added, vals = [], []
        for _ in range(6):
            while True:
                u, v_ = r.sample(range(n), 2)
                if not G.has_edge(u, v_) and min(abs(u - v_), n - abs(u - v_)) > n // 5:
                    break
            G.add_edge(u, v_); added.append((u, v_)); vals.append(eigenratio(G))
        self.eig_vals = (er0, vals)
        with self.say("e4") as d:
            for (u, v_), val in zip(added, vals):
                sc = Line(pos[u], pos[v_], color=GOLD, stroke_width=3)
                self.play(Create(sc), Transform(cnt, counter("特征值比", f"{val:.1f}", GOLD, vs=46).move_to(cnt)), run_time=max(0.6, d * 0.8 / 6))
        with self.say("e5") as d:
            self.play(LaggedStart(*[Indicate(x, color=GOLD) for x in dots], lag_ratio=0.03), run_time=d * 0.5)
        self.fade_all(keep=(tag,))
        Gb, Ge = threshold_nets()
        Ge = Ge.subgraph(max(nx.connected_components(Ge), key=len)).copy()
        vb = NetView(Gb, fit(nx.kamada_kawai_layout(Gb), (0.8, 6.4, -2.6, 2.2)), color=BLUE, rmin=0.025, rk=0.012, ew=0.7, eo=0.3)
        ve = NetView(Ge, fit(nx.kamada_kawai_layout(Ge), (-6.4, -0.8, -2.6, 2.2)), color=MUTED, rmin=0.025, rk=0.012, ew=0.7, eo=0.3)
        ce = counter("随机网络", f"{eigenratio(Ge):.0f}", MUTED, vs=40).move_to(LEFT * 3.6 + DOWN * 3.2)
        cb = counter("无标度网络", f"{eigenratio(Gb):.0f}", BLUE, vs=40).move_to(RIGHT * 3.6 + DOWN * 3.2)
        self.eig_het = (eigenratio(Ge), eigenratio(Gb))
        with self.say("e6") as d:
            self.play(FadeIn(ve.group), FadeIn(vb.group), run_time=1.2)
            self.play(FadeIn(ce), FadeIn(cb), run_time=0.8)
            hubs = sorted(Gb, key=Gb.degree, reverse=True)[:5]
            self.play(*[Indicate(vb.dots[h], color=GOLD, scale_factor=2.0) for h in hubs], run_time=1.4)
        self.fade_all()

    # ------------------------------------------------------------------ consensus & hierarchy
    def consensus(self):
        tag = self.chapter("二  网络结构：共识与分层")
        x0 = np.array([9.0, 2.0, 6.0, 1.0, 7.0])
        Pp = [LEFT * 5.6 + RIGHT * 1.15 * i + UP * 0.4 for i in range(5)]
        Pc = [RIGHT * 3.4 + UP * 0.4 + 1.6 * np.array([np.cos(PI / 2 + 2 * PI * i / 5), np.sin(PI / 2 + 2 * PI * i / 5), 0]) for i in range(5)]
        Gp, Gc = nx.path_graph(5), nx.complete_graph(5)

        def make(Pts, Gr):
            circ = VGroup(*[Circle(radius=0.36, color=INK, stroke_width=2, fill_opacity=1, fill_color=hcolor(x)).move_to(p) for p, x in zip(Pts, x0)])
            nums = VGroup(*[DecimalNumber(x, num_decimal_places=1, font_size=26, color=BG).move_to(p) for p, x in zip(Pts, x0)])
            ed = VGroup(*[Line(Pts[u], Pts[v], color=MUTED, stroke_width=2.5, buff=0.36) for u, v in Gr.edges()])
            return circ, nums, ed

        def hcolor(x):
            return interpolate_color(ManimColor(BLUE), ManimColor(GOLD), np.clip((x - 1) / 8, 0, 1))
        cp, npn, ep = make(Pp, Gp)
        cc, ncn, ec = make(Pc, Gc)
        with self.say("c1") as d:
            self.play(FadeIn(tag), Create(ep), FadeIn(cp), FadeIn(npn), run_time=1.2)
            self.play(Create(ec), FadeIn(cc), FadeIn(ncn), run_time=1.2)

        def evolve(Gr, circ, nums):
            L = nx.laplacian_matrix(Gr).toarray().astype(float)
            ev, V = np.linalg.eigh(L)
            c0 = V.T @ x0

            def upd(m, a):
                t = 8 * a
                x = V @ (np.exp(-ev * t) * c0)
                for c_, n_, val in zip(circ, nums, x):
                    c_.set_fill(hcolor(val))
                    n_.set_value(val)
            return UpdateFromAlphaFunc(VGroup(circ, nums), upd, rate_func=linear), ev[1]
        mean = counter("初始平均", f"{x0.mean():.1f}", GOLD, vs=36).to_edge(DOWN, buff=0.4)
        with self.say("c2") as d:
            a1, mu_p = evolve(Gp, cp, npn)
            a2, mu_c = evolve(Gc, cc, ncn)
            self.play(FadeIn(mean), run_time=0.6)
            self.play(a1, a2, run_time=d - 0.8)
        with self.say("c3") as d:
            ac = VGroup(MathTex(r"\mu_2", font_size=40, color=GOLD), T("第二小特征值 · 代数连通度", 24, GOLD)).arrange(RIGHT, buff=0.2).to_edge(UP, buff=0.9)
            self.play(FadeIn(ac), run_time=0.8)
        with self.say("c3b") as d:
            l1 = MathTex(rf"\mu_2\approx {mu_p:.2f}", font_size=40, color=BLUE).next_to(VGroup(*cp), DOWN, buff=0.6)
            l2 = MathTex(rf"\mu_2={mu_c:.0f}", font_size=40, color=GOLD).next_to(VGroup(*cc), DOWN, buff=0.35)
            self.play(Write(l1), run_time=1.0)
            self.wait(d * 0.3)
            self.play(Write(l2), run_time=1.0)
        with self.say("c4") as d:
            # replay from the start
            for c_, n_, x in zip(list(cp) + list(cc), list(npn) + list(ncn), list(x0) * 2):
                c_.set_fill(hcolor(x)); n_.set_value(x)
            a1, _ = evolve(Gp, cp, npn)
            a2, _ = evolve(Gc, cc, ncn)
            ratio = T(f"快约 {mu_c / mu_p:.0f} 倍", 30, GOLD).next_to(l2, RIGHT, buff=0.4)
            self.play(a1, a2, run_time=d - 1.2)
            self.play(FadeIn(ratio), run_time=0.6)
        self.fade_all(keep=(tag,))
        # hierarchical sync on a 4-module network
        G = nx.Graph(); r = random.Random(1)
        for m in range(4):
            for i in range(10):
                for j in range(i + 1, 10):
                    if r.random() < 0.6:
                        G.add_edge(m * 10 + i, m * 10 + j)
        for m in range(4):
            for _ in range(2):
                G.add_edge(m * 10 + r.randrange(10), ((m + 1) % 4) * 10 + r.randrange(10))
        centers = [np.array(c) for c in ([-4.8, 1.3, 0], [-1.8, 1.3, 0], [-1.8, -1.7, 0], [-4.8, -1.7, 0])]
        pos = {}
        for m in range(4):
            for i in range(10):
                a = 2 * np.pi * i / 10
                pos[m * 10 + i] = centers[m] + 0.95 * np.array([np.cos(a), np.sin(a), 0])
        G = nx.convert_node_labels_to_integers(G, ordering="sorted")
        dots = {v: Dot(pos[v], radius=0.1, color=MUTED) for v in sorted(G)}
        ed = VGroup(*[Line(pos[u], pos[v], color=MUTED, stroke_width=1.2, stroke_opacity=0.35) for u, v in G.edges()])
        Gs = nx.Graph(); Gs.add_nodes_from(range(40)); Gs.add_edges_from(G.edges())
        rng = np.random.default_rng(2)
        th0 = rng.uniform(0, 2 * np.pi, 40)
        traj, _ = kuramoto_net(Gs, 0.3, np.zeros(40), th0, 40, dt=0.05, record=True)
        tt = np.arange(len(traj)) * 0.05
        rw = [np.mean([abs(np.exp(1j * th[m * 10:m * 10 + 10]).mean()) for m in range(4)]) for th in traj]
        rg = [abs(np.exp(1j * th).mean()) for th in traj]
        ax = axes([0, 40, 10], [0, 1, 0.5], 5.4, 3.6, yn=[0, 0.5, 1]).move_to(RIGHT * 3.6 + DOWN * 0.2)
        xl = T("时间", 22, MUTED).next_to(ax.x_axis, DOWN, buff=0.3)
        lg = legend([(GREEN, "社团内部"), (GOLD, "全网")]).next_to(ax, UP, buff=0.3)
        cw = ax.plot_line_graph(tt[::4], rw[::4], line_color=GREEN, add_vertex_dots=False, stroke_width=4)
        cg = ax.plot_line_graph(tt[::4], rg[::4], line_color=GOLD, add_vertex_dots=False, stroke_width=4)
        with self.say("c5") as d:
            self.play(Create(ed), FadeIn(VGroup(*dots.values())), Create(ax), FadeIn(xl), FadeIn(lg), run_time=d * 0.6)
            for v in dots:
                dots[v].set_color(hue(th0[v]))
        with self.say("c6") as d:
            vt = ValueTracker(0)

            def upd(m, a):
                i = min(len(traj) - 1, int(a * (len(traj) - 1)))
                for v, dd in dots.items():
                    dd.set_color(hue(traj[i, v]))
            self.play(UpdateFromAlphaFunc(VGroup(*dots.values()), upd, rate_func=linear), Create(cw, rate_func=linear),
                      Create(cg, rate_func=linear), run_time=d)
        with self.say("c6b") as d:
            self.play(Indicate(cw, color=GREEN), run_time=1.0)
            self.play(Indicate(cg, color=GOLD), run_time=1.0)
        self.fade_all()

    # ------------------------------------------------------------------ biology
    def biology(self):
        tag = self.chapter("三  生命中的节律")
        heart = VGroup(*[Dot(radius=0.12, color=RED) for _ in range(30)]).arrange_in_grid(5, 6, buff=0.28).move_to(LEFT * 3.2)
        rng = np.random.default_rng(1)
        w = rng.normal(2 * np.pi * 0.9, 0.5, 30)
        th = rng.uniform(0, 2 * np.pi, 30)
        lab = T("窦房结", 28, RED).next_to(heart, UP, buff=0.4)

        def beat(K, dur):
            nonlocal th
            dt = 1 / 30; tr = [th.copy()]
            for _ in range(int(dur / dt)):
                z = np.exp(1j * th).mean()
                th = th + dt * (w + K * abs(z) * np.sin(np.angle(z) - th)); tr.append(th.copy())
            tr = np.array(tr)

            def upd(m, a):
                i = min(len(tr) - 1, int(a * (len(tr) - 1)))
                for dd, t in zip(heart, tr[i]):
                    dd.set_opacity(0.15 + 0.85 * ((1 + np.cos(t)) / 2) ** 6)
            return UpdateFromAlphaFunc(heart, upd, rate_func=linear, run_time=dur)
        with self.say("b1") as d:
            self.play(FadeIn(tag), FadeIn(heart), FadeIn(lab), run_time=1.0)
            self.play(beat(0.0, d * 0.3))
            self.play(beat(4.0, d * 0.5))
        # SCN: dispersed vs tissue, 24h clocks as phase arrows
        show_clip(self, "b1b", "yt_cardiomyocytes_beating.mp4", "center", "视频：Charles River Labs · YouTube", start=1, min_len=7)
        self.add(tag)
        n = 16
        rng = np.random.default_rng(3)
        ph = rng.uniform(0, 2 * np.pi, n)

        def clocks(center, phases, color):
            g = VGroup()
            for i, p in enumerate(phases):
                c = center + np.array([(i % 4 - 1.5) * 0.9, (1.5 - i // 4) * 0.9, 0])
                circ = Circle(radius=0.36, color=color, stroke_width=2)
                hand = Line(ORIGIN, 0.3 * np.array([np.cos(p), np.sin(p), 0]), color=color, stroke_width=3)
                g.add(VGroup(circ, hand).move_to(c).shift(0 * RIGHT))
                hand.put_start_and_end_on(c, c + 0.3 * np.array([np.cos(p), np.sin(p), 0]))
            return g
        left = clocks(LEFT * 3.4 + DOWN * 0.3, ph, BLUE)
        right = clocks(RIGHT * 3.4 + DOWN * 0.3, np.full(n, PI / 2) + rng.normal(0, 0.08, n), GOLD)
        with self.say("b2") as d:
            c = counter("视交叉上核", "约 2 万个神经元", GOLD, vs=36).move_to(UP * 0.3)
            self.play(FadeIn(c), run_time=1.0)
        with self.say("b3") as d:
            self.play(c.animate.scale(0.7).to_edge(UP, buff=0.9), run_time=0.6)
            l1 = T("分散培养：相位各异", 24, BLUE).next_to(left, DOWN, buff=0.3)
            l2 = T("完整组织：节律一致", 24, GOLD).next_to(right, DOWN, buff=0.3)
            self.play(FadeIn(left), FadeIn(l1), run_time=1.0)
        with self.say("b3b") as d:
            self.play(FadeIn(right), FadeIn(l2), run_time=1.0)
        self.fade_all(keep=(tag,))
        # Parkinson beta synchrony: two traces
        ax_l = Line(LEFT * 6, RIGHT * 6, color=MUTED, stroke_width=1).shift(UP * 1.0)
        ax_r = Line(LEFT * 6, RIGHT * 6, color=MUTED, stroke_width=1).shift(DOWN * 1.8)
        t = np.linspace(0, 12, 900)
        rng = np.random.default_rng(5)
        noise = np.convolve(rng.normal(0, 1, 900), np.ones(5) / 5, mode="same")
        y1 = 0.25 * noise + 0.15 * np.sin(2 * np.pi * 2.0 * t)
        y2 = 0.25 * noise * 0.5 + 0.7 * np.sin(2 * np.pi * 2.0 * t) * (0.7 + 0.3 * np.sin(0.5 * t))
        tr1 = VMobject(color=BLUE, stroke_width=2.5).set_points_smoothly([ax_l.get_start() + RIGHT * x + UP * y for x, y in zip(t, y1)][::3])
        tr2 = VMobject(color=RED, stroke_width=2.5).set_points_smoothly([ax_r.get_start() + RIGHT * x + UP * y for x, y in zip(t, y2)][::3])
        l1 = T("正常", 24, BLUE).next_to(ax_l, UP, buff=0.6).to_edge(LEFT, buff=0.8)
        l2 = T("帕金森病：贝塔频段同步增强", 24, RED).next_to(ax_r, UP, buff=0.9).to_edge(LEFT, buff=0.8)
        sk = T("示意", 20, MUTED).to_corner(DR, buff=0.4)
        with self.say("b4") as d:
            self.play(FadeIn(l1), FadeIn(sk), Create(tr1), run_time=d * 0.35, rate_func=linear)
            self.play(FadeIn(l2), Create(tr2), run_time=d * 0.45, rate_func=linear)
        with self.say("b5") as d:
            self.play(*[FadeOut(m) for m in (tr1, tr2, l1, l2, ax_l, ax_r, sk)], run_time=0.6)
            bal = VGroup(T("分离", 36, BLUE), Line(LEFT * 1.6, RIGHT * 1.6, color=INK, stroke_width=5), T("整合", 36, GOLD)).arrange(RIGHT, buff=0.3)
            tri = Triangle(color=INK, fill_opacity=1).scale(0.25).next_to(bal[1], DOWN, buff=0)
            g = VGroup(bal, tri).move_to(ORIGIN)
            self.play(FadeIn(g), run_time=0.8)
            self.play(Rotate(bal, 0.12, about_point=tri.get_top()), run_time=0.7)
            self.play(Rotate(bal, -0.24, about_point=tri.get_top()), run_time=0.9)
            self.play(Rotate(bal, 0.12, about_point=tri.get_top()), run_time=0.7)
        self.fade_all()

    # ------------------------------------------------------------------ recap
    def recap(self):
        recap_slide(self, ["序参量 r：超过临界耦合，进入部分同步", "连接越不均匀，同步越早开始；完全同步看特征值", "同步过强或过弱，都可能意味着疾病"])
        with self.say("z5") as d:
            self.clip_on("kuramoto_demo.mp4", "full", "本站交互演示：Kuramoto 同步", start=0.3)
        with self.say("z5b") as d:
            pass
        self.clip_off()
        self.wait(1.0)
