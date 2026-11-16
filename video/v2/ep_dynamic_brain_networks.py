"""Animated explainer: 动态功能连接与多层脑网络 (sliding windows, states, sampling noise, null models, flexibility)."""
import numpy as np

from common import *  # noqa: F401,F403
from bhelp import counter, axes, legend, heat, recolor_heat, parts_slide, recap_slide, show_clip

TITLE = "动态功能连接：在变的是大脑，还是噪声"

LINES = {
    # hook
    "h1": "做一次静息态扫描，也就是让被试安静地躺在磁共振里，什么任务也不做。通常会把十分钟左右的信号，平均成一个连接矩阵。",
    "h1b": "这些信号叫血氧信号：脑区活动时，局部的血流和血氧会跟着变化。画面是一段介绍这种信号的视频。",
    "h2": "可是这十分钟里，大脑会走神、会犯困、会回忆。连接很可能并不是一成不变的。",
    "h3": "换一种算法：用一个短的时间窗，沿着时间滑动，每个位置算一个矩阵。你看，矩阵就闪烁起来了。",
    "h4": "但再看这两条信号。它们的真实相关，从头到尾都是零点三，就是绿色虚线。可窗口里算出来的相关，也就是红线，一样在上下跳。",
    "h5": "所以，我们看到的变化，可能来自大脑，也可能只是噪声。这一期，就来讲怎样把两者分开。",
    "q0": "这一期分三部分来讲。",
    "q1": "第一部分，怎样测量随时间变化的连接。",
    "q2": "第二部分，怎样判断这种变化是真的，而不是噪声。",
    "q3": "第三部分，多层网络，以及这些指标离临床还有多远。",
    # sliding window
    "w1": "先看第一部分。最直接的方法是滑动窗口：取一段固定长度的时间窗，就是这个红框，在窗内计算两个脑区的相关。",
    "w2": "然后把窗口往后挪一步，再算一次。下面这张图，横轴是时间，纵轴是窗口相关。相关就变成了一条随时间变化的曲线。",
    "w3": "对所有脑区两两这样做，每个窗口得到一个连接矩阵，整次扫描就变成了一串矩阵。",
    "w4": "要注意，数据量看起来暴增，可它们都是从同一段信号里算出来的，独立的信息并没有增加。",
    # states
    "k1": "把所有窗口的矩阵拿去聚类，也就是把相似的矩阵归成一组，就得到几种反复出现的连接模式，叫连接状态。这里每个点是一个窗口。",
    "k2": "2014年，艾伦等人用这种方法，在四百多名被试中报告了七个连接状态。",
    "k3": "按时间顺序排下来，就是一条状态序列。由此可以算出每个状态的占时比例、平均停留时间和切换次数。",
    "k4": "比如这条十个窗口的序列。状态一，占了一半的时间。",
    "k4b": "状态一出现了两段，一段长三，一段长二，平均停留二点五个窗口。",
    "k4c": "整条序列在黄色竖线处切换，一共三次。",
    # sampling noise
    "n1": "下面进入第二部分。窗口内的相关，只是用少量样本做出的估计。",
    "n2": "这两条信号的真实相关一直是零点三。下面这张图的纵轴是窗口相关，做过一种叫费舍尔变换的处理，让波动的大小更容易比较。",
    "n2b": "窗长三十个时间点时，它的标准误大约是零点一九。右上角的式子说的是：标准误，等于一，除以窗长减三的平方根。",
    "n3": "理论上，大约百分之九十五的窗口，会落在真值上下零点三八这条绿色带子里。这次模拟是百分之九十七。",
    "n3b": "【慢】也就是说，来回摆动，本身并不说明连接在变。",
    "n4": "而脑血氧信号自相关很强，有效样本更少。把信号换成平滑的，也就是黄线，跑出带子的窗口，从百分之三变成了三成多。",
    "n5": "所以窗长的选择，本质上是一种取舍：短窗时间分辨率高，长窗估计更可靠。",
    # null model
    "f1": "要证明动态是真的，必须先构造一个平稳的零模型，也就是一份没有真实动态、其他性质都相同的对照数据。",
    "f2": "常用的是相位随机化：给所有通道加上同一组随机相位。这样保留了每条信号的频率成分和静态相关，只打乱随时间的变化。",
    "f3": "生成两百份替代数据，各算一遍窗口相关的波动大小，就得到灰色的这个分布。横轴是波动的大小。",
    "f4": "【慢】只有真实数据的波动明显超出这个分布，才说明存在动态连接。这组真的在切换的数据，红色箭头，就远远落在了外面。",
    "f5": "还要记住两点。第一，聚类总会给出你指定数目的状态，哪怕数据完全是平稳的噪声。这里就被分成了四组。",
    "f5b": "第二，头动和打瞌睡也会改变连接，必须作为混杂因素来控制。",
    # multilayer
    "m1": "最后是第三部分。多层网络，把每个时间窗当作一层，同一个脑区在相邻层之间相连，就是这条虚线。",
    "m2": "在多层网络上划分模块，就能追踪每个脑区在不同时刻属于哪个模块。蓝色是模块 A，黄色是模块 B。",
    "m3": "灵活性，就是它更换模块的频率。这个脑区在六个窗口里，相邻的五对中，变了两对。",
    "m3b": "【慢】所以它的灵活性，是五分之二，也就是零点四。",
    "m4": "一项运动学习研究发现，一次扫描中的灵活性，能够预测下一次扫描中的学习量。这里画的是这个关系的示意。",
    # clinic
    "c1": "接下来看，这些指标离临床应用还有多远。",
    "c1b": "画面是一段关于用静息态脑扫描辅助诊断的报道。",
    "c2": "这张图，横轴是某个网络指标。蓝色是对照组，红色是患者组，各三百人。两组的平均值，也就是两条虚线，确实有差别。",
    "c2b": "可个体的分布大量重叠。组间差异显著，并不意味着能诊断某一个具体的病人。",
    "c3": "很多网络指标的重测信度只是中等，动态指标往往更低。重测信度，就是同一个人测两次，结果有多一致。",
    "c4": "【慢】所以，这类结论需要更长的扫描、更大的样本，以及独立数据的验证。",
    # recap
    "z1": "好，我们来总结一下。",
    "z2": "第一，滑动窗口加聚类，是动态连接最常用的分析范式。",
    "z3": "第二，任何动态结论，都要和平稳零模型比较，并控制头动和觉醒程度。",
    "z4": "第三，多层网络把时间纳入同一个框架，但信度决定了它们离临床有多远。",
    "z5": "这个专题的知识页面里，有画面上的这个交互演示。先拖动窗口位置，下面的窗口相关跟着起伏。",
    "z5b": "再改变窗口长度。窗口越短，曲线抖得越厉害；窗口越长，曲线越平滑。",
}

SC = [BLUE, GOLD, GREEN]  # state colours


def pair(rng, T, r, smooth=1):
    a = rng.normal(0, 1, T + smooth * 3)
    b = r * a + np.sqrt(1 - r * r) * rng.normal(0, 1, T + smooth * 3)
    if smooth > 1:
        k = np.ones(smooth) / smooth
        a, b = np.convolve(a, k, "valid"), np.convolve(b, k, "valid")
    return a[:T], b[:T]


def wincorr(a, b, w):
    return np.array([np.corrcoef(a[t:t + w], b[t:t + w])[0, 1] for t in range(len(a) - w)])


def switching_data(seed=2, R=6, blocks=(0, 1, 0, 2, 1, 2, 0), L=70):
    """R regions whose correlation pattern switches between three states."""
    rng = np.random.default_rng(seed)
    pats = []
    for s in range(3):
        g = np.zeros(R)
        if s == 0:
            g[:3] = 1; g[3:] = -0.2
        elif s == 1:
            g[::2] = 1; g[1::2] = 0.0
        else:
            g[3:] = 1; g[:3] = 0.2
        pats.append(g)
    X, lab = [], []
    for s in blocks:
        f = rng.normal(0, 1, L)
        X.append(np.outer(pats[s], f) * 1.1 + rng.normal(0, 1, (R, L)))
        lab += [s] * L
    return np.hstack(X), np.array(lab)


def kmeans(V, k, seed=0, it=50):
    rng = np.random.default_rng(seed)
    C = V[rng.choice(len(V), k, replace=False)]
    for _ in range(it):
        lab = np.argmin(((V[:, None, :] - C[None]) ** 2).sum(-1), 1)
        C = np.array([V[lab == j].mean(0) if np.any(lab == j) else C[j] for j in range(k)])
    return lab, C


def phase_surrogate(X, rng):
    F = np.fft.rfft(X, axis=1)
    ph = rng.uniform(0, 2 * np.pi, F.shape[1]); ph[0] = 0
    if X.shape[1] % 2 == 0:
        ph[-1] = 0
    return np.fft.irfft(F * np.exp(1j * ph)[None, :], n=X.shape[1], axis=1)


def trace(y, x0, x1, y0, amp, color, sw=2.5):
    xs = np.linspace(x0, x1, len(y))
    step = max(1, len(y) // 160)
    return VMobject(color=color, stroke_width=sw).set_points_smoothly([np.array([x, y0 + amp * v, 0]) for x, v in zip(xs, y)][::step])


class Episode(Narrated):
    LINES = LINES

    def construct(self):
        self.hook()
        parts_slide(self, ["一  测量动态连接：滑动窗口与连接状态", "二  是大脑在变，还是噪声在变", "三  多层网络，以及离临床还有多远"])
        self.window()
        self.states()
        self.noise()
        self.null()
        self.multilayer()
        self.clinic()
        self.recap()

    def fade_all(self, rt=0.8, keep=()):
        self.play(*[FadeOut(m) for m in self.mobjects if m not in keep], run_time=rt)

    # ------------------------------------------------------------------ hook
    def hook(self):
        X, lab = switching_data()
        self.X, self.lab = X, lab
        R, Tn = X.shape
        sigs = VGroup(*[trace(X[i] / 3, -6.5, -0.6, 2.4 - i * 0.95, 0.35, SC[i // 3] if i < 6 else INK, 1.6) for i in range(R)])
        hm = heat(np.corrcoef(X), side=3.4).move_to(RIGHT * 3.6 + UP * 0.2)
        with self.say("h1") as d:
            self.play(Create(sigs), run_time=d * 0.5, rate_func=linear)
            br = Brace(sigs, RIGHT, color=MUTED)
            self.play(GrowFromCenter(br), FadeIn(hm), run_time=1.0)
            lab10 = T("平均成一个矩阵", 22, MUTED).next_to(hm, DOWN, buff=0.3)
            self.play(FadeIn(lab10), run_time=0.5)
        keep = list(self.mobjects)
        show_clip(self, "h1b", "yt_bold_usc.mp4", "center", "视频：USC Stevens Neuroimaging and Informatics Institute · YouTube", start=5, min_len=7)
        self.play(*[FadeIn(m) for m in keep], run_time=0.6)
        with self.say("h2") as d:
            self.play(Indicate(hm, color=GOLD, scale_factor=1.05), run_time=1.2)
        w = 40
        box = Rectangle(width=(5.9 * w / Tn), height=sigs.height + 0.3, color=GOLD, stroke_width=3).move_to(sigs, aligned_edge=LEFT)
        with self.say("h3") as d:
            self.play(FadeOut(br), FadeOut(lab10), Create(box), run_time=0.6)
            steps = 10
            starts = np.linspace(0, Tn - w, steps).astype(int)
            for s in starts:
                M = np.corrcoef(X[:, s:s + w])
                x = sigs.get_left()[0] + 5.9 * s / Tn
                self.play(box.animate.move_to([x + box.width / 2, box.get_center()[1], 0]), *recolor_heat(hm, M), run_time=max(0.35, (d - 0.8) / steps))
        self.play(FadeOut(sigs), FadeOut(box), FadeOut(hm), run_time=0.6)
        rng = np.random.default_rng(1)
        a, b = pair(rng, 400, 0.3)
        r = wincorr(a, b, 30)
        ta, tb = trace(a[:300], -6.4, 6.4, 2.2, 0.28, BLUE), trace(b[:300], -6.4, 6.4, 0.9, 0.28, GOLD)
        ax = axes([0, 300, 50], [-0.4, 1, 0.5], 12.6, 2.4, yn=[0, 0.5, 1], fs=18).move_to(DOWN * 2.0)
        truth = DashedLine(ax.c2p(0, 0.3), ax.c2p(300, 0.3), color=GREEN)
        tl = T("真实相关 0.3", 20, GREEN).next_to(ax.c2p(300, 0.3), UP, buff=0.08).shift(LEFT * 0.8)
        cr = ax.plot_line_graph(np.arange(270), r[:270], line_color=RED, add_vertex_dots=False, stroke_width=3)
        with self.say("h4") as d:
            self.play(Create(ta), Create(tb), Create(ax), run_time=1.2)
            self.play(Create(truth), FadeIn(tl), run_time=0.6)
            self.play(Create(cr), run_time=d * 0.55, rate_func=linear)
        with self.say("h5") as d:
            q = T("变化，可能来自大脑，也可能来自噪声", 40, GOLD, weight=BOLD)
            self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.6)
            self.play(Write(q), run_time=1.2)
        self.fade_all(0.6)

    # ------------------------------------------------------------------ sliding window
    def window(self):
        tag = self.chapter("一  测量：滑动窗口")
        X, lab = self.X, self.lab
        Tn = X.shape[1]
        i, j = 0, 2
        sa = trace(X[i] / 3, -6.4, 6.4, 2.3, 0.35, BLUE, 2)
        sb = trace(X[j] / 3, -6.4, 6.4, 1.1, 0.35, GOLD, 2)
        w = 40
        r = np.array([np.corrcoef(X[i, t:t + w], X[j, t:t + w])[0, 1] for t in range(Tn - w)])
        ax = axes([0, Tn, 70], [-0.5, 1, 0.5], 12.8, 2.6, yn=[0, 0.5, 1], fs=18).move_to(DOWN * 1.9)
        yl = T("窗口相关", 20, MUTED).next_to(ax, UP, buff=0.05).align_to(ax, LEFT)
        wpx = 12.8 * w / Tn
        box = Rectangle(width=wpx, height=2.1, color=RED, stroke_width=3).move_to([-6.4 + wpx / 2, 1.7, 0])
        tv = ValueTracker(0)
        curve = always_redraw(lambda: ax.plot_line_graph(np.arange(int(tv.get_value()) + 1) + w / 2, r[:int(tv.get_value()) + 1],
                                                         line_color=RED, add_vertex_dots=False, stroke_width=3))
        rv = always_redraw(lambda: MathTex(rf"r={r[int(tv.get_value())]:.2f}", font_size=34, color=RED).next_to(box, UP, buff=0.08))
        with self.say("w1") as d:
            self.play(FadeIn(tag), Create(sa), Create(sb), run_time=1.4)
            self.play(Create(box), run_time=0.6)
            self.add(rv)
            self.play(Create(ax), FadeIn(yl), run_time=0.8)
        self.add(curve)
        with self.say("w2") as d:
            box.add_updater(lambda m: m.move_to([-6.4 + 12.8 * tv.get_value() / Tn + wpx / 2, 1.7, 0]))
            self.play(tv.animate.set_value(len(r) - 1), run_time=d * 0.9, rate_func=linear)
            box.clear_updaters()
        self.remove(curve, rv)
        self.fade_all(keep=(tag,))
        # many matrices
        with self.say("w3") as d:
            mats = VGroup()
            for k_, s in enumerate(np.linspace(0, Tn - w, 12).astype(int)):
                hmk = heat(np.corrcoef(X[:, s:s + w]), side=1.3)
                hmk.move_to(LEFT * 5.0 + RIGHT * 0.55 * k_ + UP * (1.2 - 0.25 * k_))
                mats.add(hmk)
            self.play(LaggedStart(*[FadeIn(m_, shift=RIGHT * 0.3) for m_ in mats], lag_ratio=0.15), run_time=d * 0.7)
        with self.say("w4") as d:
            c1 = counter("窗口相关值", "成千上万", GOLD, vs=36).move_to(RIGHT * 3.4 + UP * 1.0)
            c2 = counter("独立信息", "没有增加", RED, vs=36).move_to(RIGHT * 3.4 + DOWN * 1.2)
            self.play(FadeIn(c1), run_time=0.8)
            self.play(FadeIn(c2), run_time=0.8)
        self.fade_all()

    # ------------------------------------------------------------------ states
    def states(self):
        tag = self.chapter("一  测量：连接状态")
        X, lab = self.X, self.lab
        R, Tn = X.shape
        w = 40
        starts = np.arange(0, Tn - w, 5)
        iu = np.triu_indices(R, 1)
        V = np.array([np.corrcoef(X[:, s:s + w])[iu] for s in starts])
        kl, Cc = kmeans(V, 3, seed=1)
        # order clusters by first appearance
        order = []
        for x in kl:
            if x not in order:
                order.append(x)
        remap = {o: i for i, o in enumerate(order)}
        kl = np.array([remap[x] for x in kl])
        Cc = Cc[order]
        rng = np.random.default_rng(0)
        pts = []
        cen = [np.array([-4.6, 1.5, 0]), np.array([-0.9, -1.0, 0]), np.array([2.6, 1.5, 0])]
        dots = VGroup()
        for k_ in kl:
            p = np.array([rng.uniform(-6, 6), rng.uniform(-3, 3), 0])
            dots.add(Dot(p, radius=0.06, color=MUTED))
            pts.append(cen[k_] + np.array([rng.normal(0, 0.5), rng.normal(0, 0.4), 0]))
        with self.say("k1") as d:
            self.play(FadeIn(tag), FadeIn(dots, lag_ratio=0.01), run_time=1.2)
            self.play(*[dt.animate.move_to(p).set_color(SC[k_]) for dt, p, k_ in zip(dots, pts, kl)], run_time=d * 0.5)
        mats = VGroup()
        for s in range(3):
            M = np.eye(R)
            M[iu] = Cc[s]; M[(iu[1], iu[0])] = Cc[s]
            mats.add(heat(M, side=1.2).next_to(cen[s], RIGHT, buff=0.9))
        with self.say("k2") as d:
            self.play(LaggedStart(*[FadeIn(m_) for m_ in mats], lag_ratio=0.3), run_time=1.2)
            c = VGroup(counter("被试", "405", INK, vs=34), counter("连接状态", "7", GOLD, vs=34)).arrange(RIGHT, buff=0.8).to_edge(DOWN, buff=0.25)
            yr = T("2014", 26, MUTED).next_to(c, LEFT, buff=0.6)
            self.play(FadeIn(c), FadeIn(yr), run_time=0.8)
        self.fade_all(keep=(tag,))
        # state time line from the real clustering
        ws = 12.0 / len(kl)
        bar = VGroup(*[Rectangle(width=ws, height=0.6, fill_color=SC[k_], fill_opacity=0.9, stroke_width=0).move_to([-6 + ws * (i + 0.5), 1.8, 0]) for i, k_ in enumerate(kl)])
        bl = T("聚类得到的状态序列", 22, MUTED).next_to(bar, UP, buff=0.2)
        with self.say("k3") as d:
            self.play(FadeIn(bl), LaggedStart(*[FadeIn(b) for b in bar], lag_ratio=0.02), run_time=d * 0.6)
        seq = [1, 1, 1, 2, 2, 1, 1, 3, 3, 3]
        cells = VGroup(*[VGroup(Square(0.8, fill_color=SC[s - 1], fill_opacity=0.85, stroke_color=BG, stroke_width=3), T(str(s), 30, BG, weight=BOLD))
                         for s in seq]).arrange(RIGHT, buff=0).move_to(DOWN * 0.4)
        with self.say("k4") as d:
            self.play(FadeIn(cells, lag_ratio=0.1), run_time=1.0)
            ones = [cells[i] for i, s in enumerate(seq) if s == 1]
            occ = counter("状态一占时", "5/10 = 0.5", BLUE, vs=30)
            dw = counter("平均停留", "(3+2)/2 = 2.5", BLUE, vs=30)
            sw = counter("切换次数", "3", GOLD, vs=30)
            VGroup(occ, dw, sw).arrange(RIGHT, buff=1.0).to_edge(DOWN, buff=0.5)
            self.play(*[Indicate(c_, color=BLUE, scale_factor=1.15) for c_ in ones], FadeIn(occ), run_time=1.2)
        with self.say("k4b") as d:
            b1 = Brace(VGroup(cells[0], cells[2]), UP, color=BLUE); b2 = Brace(VGroup(cells[5], cells[6]), UP, color=BLUE)
            self.play(GrowFromCenter(b1), GrowFromCenter(b2), FadeIn(dw), run_time=1.2)
        with self.say("k4c") as d:
            marks = VGroup(*[Line(UP * 0.5, DOWN * 0.5, color=GOLD, stroke_width=5).move_to((cells[i].get_right() + cells[i + 1].get_left()) / 2)
                             for i in range(9) if seq[i] != seq[i + 1]])
            self.play(Create(marks), FadeIn(sw), run_time=1.0)
        self.fade_all()

    # ------------------------------------------------------------------ sampling noise
    def noise(self):
        tag = self.chapter("二  噪声也会“动”")
        rng = np.random.default_rng(1)
        a, b = pair(rng, 400, 0.3)
        w = 30
        z = np.arctanh(wincorr(a, b, w))
        a2, b2 = pair(rng, 400, 0.3, smooth=6)
        z2 = np.arctanh(wincorr(a2, b2, w))
        z0 = np.arctanh(0.3)
        f1 = np.mean(np.abs(z - z0) < 0.38); f2 = np.mean(np.abs(z2 - z0) < 0.38)
        self.noise_vals = (f1, f2)
        ta, tb = trace(a[:300], -6.4, 6.4, 2.3, 0.25, BLUE, 2), trace(b[:300], -6.4, 6.4, 1.2, 0.25, GOLD, 2)
        with self.say("n1") as d:
            self.play(FadeIn(tag), Create(ta), Create(tb), run_time=d * 0.6)
        ax = axes([0, 370, 50], [-0.6, 1.4, 0.5], 12.2, 3.0, yn=[0, 0.5, 1], fs=18).move_to(DOWN * 1.6)
        yl = T("窗口相关（费舍尔 z）", 20, MUTED).next_to(ax, UP, buff=0.05).to_edge(LEFT, buff=0.6)
        truth = DashedLine(ax.c2p(0, z0), ax.c2p(370, z0), color=GREEN)
        band = Polygon(ax.c2p(0, z0 - 0.38), ax.c2p(370, z0 - 0.38), ax.c2p(370, z0 + 0.38), ax.c2p(0, z0 + 0.38),
                       stroke_width=0, fill_color=GREEN, fill_opacity=0.15)
        c1 = ax.plot_line_graph(np.arange(len(z)), z, line_color=RED, add_vertex_dots=False, stroke_width=2.5)
        with self.say("n2") as d:
            self.play(FadeOut(ta), FadeOut(tb), Create(ax), FadeIn(yl), Create(truth), run_time=1.0)
        with self.say("n2b") as d:
            f = MathTex(r"\mathrm{SE}(z)\approx\frac{1}{\sqrt{w-3}}=\frac{1}{\sqrt{27}}\approx 0.19", font_size=36).to_corner(UR, buff=0.4).shift(DOWN * 0.3)
            self.play(Write(f), run_time=1.4)
        with self.say("n3") as d:
            self.play(FadeIn(band), run_time=0.6)
            self.play(Create(c1), run_time=d * 0.4, rate_func=linear)
            k1 = counter("落在带内", f"{f1 * 100:.0f}%", GREEN, vs=36).move_to(UP * 1.6 + LEFT * 3.5)
            self.play(FadeIn(k1), run_time=0.6)
        with self.say("n3b") as d:
            self.play(Indicate(band, color=GREEN), run_time=1.2)
        c2 = ax.plot_line_graph(np.arange(len(z2)), z2, line_color=GOLD, add_vertex_dots=False, stroke_width=2.5)
        with self.say("n4") as d:
            self.play(c1.animate.set_stroke(opacity=0.25), run_time=0.5)
            self.play(Create(c2), run_time=d * 0.45, rate_func=linear)
            k2 = counter("平滑信号 · 带外", f"{(1 - f2) * 100:.0f}%", GOLD, vs=36).move_to(UP * 1.6 + RIGHT * 0.4)
            k1b = counter("独立样本 · 带外", f"{(1 - f1) * 100:.0f}%", GREEN, vs=36).move_to(k1)
            self.play(Transform(k1, k1b), FadeIn(k2), run_time=0.8)
        self.fade_all(keep=(tag,))
        with self.say("n5") as d:
            line = Line(LEFT * 4, RIGHT * 4, color=MUTED, stroke_width=4)
            l1 = T("短窗：时间分辨率高", 26, BLUE).next_to(line, UP, buff=0.4).align_to(line, LEFT)
            l2 = T("长窗：估计更可靠", 26, GOLD).next_to(line, DOWN, buff=0.4).align_to(line, RIGHT)
            knob = Dot(line.get_center(), radius=0.18, color=RED)
            self.play(Create(line), FadeIn(l1), FadeIn(l2), FadeIn(knob), run_time=1.0)
            self.play(knob.animate.move_to(line.get_left()), run_time=1.0)
            self.play(knob.animate.move_to(line.get_right()), run_time=1.4)
            self.play(knob.animate.move_to(line.get_center()), run_time=0.8)
        self.fade_all()

    # ------------------------------------------------------------------ null model
    def null(self):
        tag = self.chapter("二  平稳零模型")
        X = self.X
        R, Tn = X.shape
        w = 40

        def stat(Y):
            iu = np.triu_indices(R, 1)
            V = np.array([np.corrcoef(Y[:, s:s + w])[iu] for s in range(0, Tn - w, 4)])
            return V.std(0).mean()
        rng = np.random.default_rng(3)
        sur = [stat(phase_surrogate(X, rng)) for _ in range(200)]
        real = stat(X)
        self.null_vals = (real, float(np.mean(sur)), float(np.max(sur)))
        a, b = X[0], X[3]
        Y = phase_surrogate(X, np.random.default_rng(9))
        ta, tb = trace(a / 3, -6.4, -0.6, 1.8, 0.4, BLUE, 2), trace(b / 3, -6.4, -0.6, 0.4, 0.4, GOLD, 2)
        sa, sb = trace(Y[0] / 3, 0.6, 6.4, 1.8, 0.4, BLUE, 2), trace(Y[3] / 3, 0.6, 6.4, 0.4, 0.4, GOLD, 2)
        l1 = T("原始数据", 24).move_to(LEFT * 3.5 + UP * 2.9)
        l2 = T("相位随机化", 24).move_to(RIGHT * 3.5 + UP * 2.9)
        with self.say("f1") as d:
            self.play(FadeIn(tag), FadeIn(l1), Create(ta), Create(tb), run_time=d * 0.7)
        with self.say("f2") as d:
            arr = Arrow(LEFT * 0.5 + UP * 1.1, RIGHT * 0.5 + UP * 1.1, buff=0, color=INK)
            self.play(GrowArrow(arr), FadeIn(l2), run_time=0.6)
            self.play(Create(sa), Create(sb), run_time=d * 0.4)
            keep = VGroup(T("保留：功率谱、静态相关", 22, GREEN), T("打乱：随时间的变化", 22, RED)).arrange(DOWN, buff=0.2).move_to(DOWN * 1.2)
            self.play(FadeIn(keep), run_time=0.8)
        self.fade_all(keep=(tag,))
        lo, hi = min(sur) * 0.95, max(real, max(sur)) * 1.05
        bins = np.linspace(lo, hi, 26)
        hcount, _ = np.histogram(sur, bins)
        ax = axes([lo, hi, (hi - lo) / 5], [0, max(hcount) * 1.15, max(1, int(max(hcount) / 3))], 10.0, 4.4).shift(DOWN * 0.5)
        xl = T("窗口相关的波动大小", 22, MUTED).next_to(ax.x_axis, DOWN, buff=0.3)
        bars = VGroup()
        for k_, c in enumerate(hcount):
            if c == 0:
                continue
            x0, x1 = bins[k_], bins[k_ + 1]
            bars.add(Rectangle(width=ax.c2p(x1, 0)[0] - ax.c2p(x0, 0)[0], height=ax.c2p(0, c)[1] - ax.c2p(0, 0)[1],
                               fill_color=MUTED, fill_opacity=0.7, stroke_width=1, stroke_color=BG).move_to(ax.c2p((x0 + x1) / 2, 0), aligned_edge=DOWN))
        with self.say("f3") as d:
            self.play(Create(ax), FadeIn(xl), run_time=0.8)
            self.play(LaggedStart(*[GrowFromEdge(b_, DOWN) for b_ in bars], lag_ratio=0.05), run_time=d * 0.6)
            nl = T("200 份替代数据", 22, MUTED).next_to(bars, UP, buff=0.2)
            self.play(FadeIn(nl), run_time=0.5)
        with self.say("f4") as d:
            rl = Arrow(ax.c2p(real, max(hcount) * 1.0), ax.c2p(real, 0), buff=0, color=RED, stroke_width=6)
            rt = T("真实数据", 24, RED).next_to(rl, UP, buff=0.1)
            self.play(GrowArrow(rl), FadeIn(rt), run_time=1.0)
            self.play(Indicate(rt, color=RED), run_time=0.8)
        self.fade_all(keep=(tag,))
        with self.say("f5") as d:
            rng = np.random.default_rng(4)
            pts = VGroup(*[Dot([rng.normal(0, 1.6), rng.normal(0, 1.1), 0], radius=0.06, color=MUTED) for _ in range(160)]).shift(LEFT * 2.5)
            self.play(FadeIn(pts), run_time=0.6)
            P = np.array([p.get_center()[:2] for p in pts])
            lab, _ = kmeans(P, 4, seed=2)
            cols = [BLUE, GOLD, GREEN, VIOLET]
            self.play(*[p.animate.set_color(cols[l_]) for p, l_ in zip(pts, lab)], run_time=1.0)
            k4 = counter("平稳的噪声", "也被分成 4 个“状态”", GOLD, vs=30).move_to(RIGHT * 3.8 + UP * 0.8)
            conf = T("头动 · 嗜睡", 28, RED).move_to(RIGHT * 3.8 + DOWN * 1.0)
            self.play(FadeIn(k4), run_time=0.6)
        with self.say("f5b") as d:
            self.play(FadeIn(conf), run_time=0.6)
        self.fade_all()

    # ------------------------------------------------------------------ multilayer
    def multilayer(self):
        tag = self.chapter("三  多层网络与灵活性")
        L = 6
        seq = ["A", "A", "B", "B", "B", "A"]
        layers = VGroup()
        tracked = []
        rng = np.random.default_rng(2)
        base_pts = [np.array([np.cos(a), 0.45 * np.sin(a), 0]) * 1.1 for a in np.linspace(0, 2 * np.pi, 8, endpoint=False)]
        for l in range(L):
            c = np.array([-5.4 + 2.15 * l, 0.6 - 0.15 * l, 0])
            plate = Polygon(c + np.array([-1.0, -0.9, 0]), c + np.array([0.7, -0.9, 0]), c + np.array([1.1, 0.9, 0]), c + np.array([-0.6, 0.9, 0]),
                            stroke_color=MUTED, stroke_width=1.5, fill_color="#182133", fill_opacity=0.6)
            pts = [c + p * 0.75 for p in base_pts]
            # module A = BLUE (left half), module B = GOLD (right half); tracked node index 0
            dots = VGroup(*[Dot(p, radius=0.06, color=BLUE if k in (2, 3, 4, 5) else GOLD) for k, p in enumerate(pts)])
            tr = Dot(c, radius=0.11, color=BLUE if seq[l] == "A" else GOLD)
            tracked.append(tr)
            ed = VGroup(*[Line(pts[u], pts[v], stroke_width=1, color=MUTED, stroke_opacity=0.5) for u, v in ((2, 3), (3, 4), (4, 5), (6, 7), (7, 0), (0, 1), (1, 6))])
            ed2 = VGroup(*[Line(c, pts[k], stroke_width=1.2, color=MUTED, stroke_opacity=0.5) for k in ((3, 4) if seq[l] == "A" else (7, 0))])
            layers.add(VGroup(plate, ed, ed2, dots, tr))
        inter = VGroup(*[DashedLine(tracked[l].get_center(), tracked[l + 1].get_center(), color=INK, stroke_width=2, dash_length=0.08) for l in range(L - 1)])
        tl = VGroup(*[T(f"窗口{l + 1}", 18, MUTED).next_to(layers[l][0], DOWN, buff=0.15) for l in range(L)])
        with self.say("m1") as d:
            self.play(FadeIn(tag), LaggedStart(*[FadeIn(x[0]) for x in layers], lag_ratio=0.15), FadeIn(tl), run_time=1.4)
            self.play(*[FadeIn(x[1:4]) for x in layers], run_time=1.0)
            for x in layers:
                x[4].set_color(INK)
            self.play(*[FadeIn(x[4]) for x in layers], Create(inter), run_time=1.0)
        with self.say("m2") as d:
            self.play(*[layers[l][4].animate.set_color(BLUE if seq[l] == "A" else GOLD) for l in range(L)], run_time=1.2)
            letters = VGroup(*[T(s, 30, BLUE if s == "A" else GOLD, weight=BOLD).next_to(tl[l], DOWN, buff=0.2) for l, s in enumerate(seq)])
            self.play(FadeIn(letters, lag_ratio=0.15), run_time=1.0)
        with self.say("m3") as d:
            chg = [l for l in range(L - 1) if seq[l] != seq[l + 1]]
            self.play(*[inter[l].animate.set_color(RED).set_stroke(width=4) for l in chg], run_time=1.0)
        with self.say("m3b") as d:
            f = MathTex(r"f=\frac{2}{5}=0.4", font_size=48, color=RED).to_edge(DOWN, buff=0.4)
            self.play(Write(f), run_time=1.2)
        with self.say("m4") as d:
            self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.6)
            ax = axes([0, 1, 0.5], [0, 1, 0.5], 4.6, 3.4).move_to(ORIGIN + DOWN * 0.2)
            xl = T("第一次扫描的灵活性", 22, MUTED).next_to(ax.x_axis, DOWN, buff=0.25)
            yl = T("下一次的学习量", 22, MUTED).rotate(PI / 2).next_to(ax.y_axis, LEFT, buff=0.25)
            arr = Arrow(ax.c2p(0.15, 0.2), ax.c2p(0.85, 0.8), buff=0, color=GOLD, stroke_width=6)
            self.play(Create(ax), FadeIn(xl), FadeIn(yl), run_time=0.8)
            self.play(GrowArrow(arr), run_time=1.0)
            sk = T("示意", 20, MUTED).next_to(ax, RIGHT, buff=0.2)
            self.play(FadeIn(sk), run_time=0.4)
        self.fade_all()

    # ------------------------------------------------------------------ clinic
    def clinic(self):
        with self.say("c1") as d:
            q = T("组间差异，不等于个体诊断", 40, GOLD, weight=BOLD)
            self.play(Write(q), run_time=1.2)
        show_clip(self, "c1b", "yt_resting_state_naturemed.mp4", "center", "视频：NatureMedicineVideos · YouTube", start=10, min_len=7)
        tag = self.chapter("三  离临床还有多远")
        self.play(FadeIn(tag), run_time=0.4)
        rng = np.random.default_rng(6)
        g1 = rng.normal(0, 1, 300); g2 = rng.normal(0.35, 1, 300)
        bins = np.linspace(-3.5, 4, 31)
        h1, _ = np.histogram(g1, bins); h2, _ = np.histogram(g2, bins)
        ax = axes([-3.5, 4, 1], [0, max(h1.max(), h2.max()) * 1.2, 10], 10, 4.2).shift(DOWN * 0.6)

        def hist(h, c):
            g = VGroup()
            for k_, n in enumerate(h):
                if n == 0:
                    continue
                g.add(Rectangle(width=ax.c2p(bins[k_ + 1], 0)[0] - ax.c2p(bins[k_], 0)[0], height=ax.c2p(0, n)[1] - ax.c2p(0, 0)[1],
                                fill_color=c, fill_opacity=0.45, stroke_width=0).move_to(ax.c2p((bins[k_] + bins[k_ + 1]) / 2, 0), aligned_edge=DOWN))
            return g
        H1, H2 = hist(h1, BLUE), hist(h2, RED)
        m1 = DashedLine(ax.c2p(g1.mean(), 0), ax.c2p(g1.mean(), h1.max() * 1.15), color=BLUE)
        m2 = DashedLine(ax.c2p(g2.mean(), 0), ax.c2p(g2.mean(), h1.max() * 1.15), color=RED)
        lg = legend([(BLUE, "对照组 300 人"), (RED, "患者组 300 人")]).to_corner(UR, buff=0.5).shift(DOWN * 0.4)
        xl = T("某个网络指标", 22, MUTED).next_to(ax.x_axis, DOWN, buff=0.3)
        with self.say("c2") as d:
            self.play(Create(ax), FadeIn(xl), FadeIn(lg), run_time=0.8)
            self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in H1], lag_ratio=0.02), LaggedStart(*[GrowFromEdge(b, DOWN) for b in H2], lag_ratio=0.02), run_time=d * 0.4)
            self.play(Create(m1), Create(m2), run_time=0.8)
        with self.say("c2b") as d:
            ov = T("大量重叠", 30, GOLD, weight=BOLD).move_to(ax.c2p(0.2, h1.max() * 1.05))
            self.play(FadeIn(ov), run_time=0.8)
        with self.say("c3") as d:
            self.remove(ov)
            self.play(*[FadeOut(m) for m in (H1, H2, m1, m2, lg, xl, ax)], run_time=0.6)
            bars = VGroup()
            for k_, (nm, h, c) in enumerate((("静态指标", 2.4, BLUE), ("动态指标", 1.3, GOLD))):
                r_ = Rectangle(width=1.6, height=h, fill_color=c, fill_opacity=0.9, stroke_width=0).move_to([-1.6 + 3.2 * k_, -2.2, 0], aligned_edge=DOWN)
                bars.add(VGroup(r_, T(nm, 24, c).next_to(r_, DOWN, buff=0.15)))
            tt = T("重测信度（示意）", 24, MUTED).move_to(UP * 1.4)
            self.play(FadeIn(tt), *[GrowFromEdge(b[0], DOWN) for b in bars], *[FadeIn(b[1]) for b in bars], run_time=1.2)
        with self.say("c4") as d:
            self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.6)
            row = VGroup(T("更长的扫描", 30, BLUE), T("更大的样本", 30, GOLD), T("独立数据验证", 30, GREEN)).arrange(RIGHT, buff=0.9)
            self.play(LaggedStart(*[FadeIn(x, shift=UP * 0.2) for x in row], lag_ratio=0.3), run_time=1.6)
        self.fade_all()

    # ------------------------------------------------------------------ recap
    def recap(self):
        recap_slide(self, ["滑动窗口 + 聚类：最常用的范式", "与平稳零模型比较，控制头动和觉醒", "多层网络纳入时间；信度决定临床距离"])
        with self.say("z5") as d:
            self.clip_on("dfc_demo.mp4", "full", "本站交互演示：滑动窗口动态功能连接", start=0.3)
        with self.say("z5b") as d:
            pass
        self.clip_off()
        self.wait(1.0)
