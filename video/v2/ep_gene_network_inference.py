"""Animated explainer: 基因调控网络推断与共表达分析 (scale, WGCNA, TOM, modules, partial correlation, evaluation)."""
import numpy as np
from scipy.cluster.hierarchy import dendrogram, fcluster, linkage
from scipy.spatial.distance import squareform

from common import *  # noqa: F401,F403
from kit_c import PANEL, arrow, axes, callout, chip, clip_line, counter, fade_all, grow_bars, parts, xlabel, ylabel

TITLE = "从“一起变化”到“谁调控谁”：基因网络推断"

LINES = {
    # hook
    "h1": "横轴是基因甲的表达量，纵轴是基因乙的表达量。每个点是一个样本，一共三十个。",
    "h2": "这些点排成一条斜线：甲高，乙也高。相关系数是零点七九。",
    "h2b": "相关系数衡量两个量是否一起升降，在负一到一之间，越接近一，越同步。",
    "h3": "很容易想到：基因甲在调控基因乙。",
    "h4": "但也可能是，甲调控丙，丙再调控乙。",
    "h4b": "还可能，甲和乙都只是跟着同一个隐藏因素在变。",
    "h5": "【慢】从一起变化，走到谁调控谁，就是基因网络推断要做的事。",
    "q0": "这一期分三部分。",
    "q1": "第一部分，网络推断难在哪里。",
    "q2": "第二部分，共表达网络分析，一步一步怎么做。",
    "q3": "第三部分，超越相关的方法，以及怎样评估结果。",
    # difficulty
    "p0": "先看第一部分。表达数据最早来自基因芯片，一块芯片能同时测出成千上万个基因的表达量。",
    "p1": "一万个基因两两配对，就有大约五千万条候选边。",
    "p2": "而样本常常只有几十个。要用几十个数字，判断五千万个关系。",
    "p3": "第二个难点是间接关联。甲调控丙，丙调控乙，甲和乙也会高度相关。",
    "p4": "第三个难点是细胞组成。组织是多种细胞的混合，某类细胞多了，它的标志基因就一起升高。",
    "p4b": "右边两根柱子一起升高，只是因为紫色细胞变多了。",
    "p5": "【慢】所以，推断出来的边首先是一个假设，不是已经证实的调控。",
    # WGCNA
    "w1": "下面进入第二部分：加权基因共表达网络分析，文献里最常用的方法之一。",
    "w1b": "它从表达矩阵出发：每一行是一个基因，每一列是一个样本。",
    "w2": "第一步，算出基因两两之间的相关系数。红色是正相关，蓝色是负相关。",
    "w3": "第二步叫软阈值：把相关系数的绝对值取一个幂次，作为连接强度。",
    "w3b": "公式里，a是连接强度，竖线里的r是相关系数，右上角的贝塔是幂次。",
    "w4": "右图横轴是相关系数的绝对值，纵轴是连接强度。贝塔越大，弱相关被压得越小。",
    "w4b": "你看左边的矩阵，取完幂次，弱相关都淡掉了，只剩强相关。",
    "w5": "贝塔用无标度拟合来选。横轴是贝塔，纵轴是拟合优度。",
    "w6": "通常取拟合优度首次达到零点八到零点九的最小值，这组数据里是三。",
    # TOM
    "t1": "第三步叫拓扑重叠：两个基因如果还共享很多邻居，关系就更可信。",
    "t1b": "公式的分子，是经由共同邻居的连接，加上直接连接；分母，取两者中较小的总连接。",
    "t1c": "所以它在零到一之间，共同邻居越多，越接近一。",
    "t2": "上面这一对，直接连接只有零点三，但共享五个邻居，拓扑重叠是零点七。",
    "t3": "【慢】下面这一对，直接连接零点九，邻居各不相同，拓扑重叠只有零点一八。",
    # modules
    "c1": "第四步，用一减拓扑重叠作距离，做层次聚类。左边是聚类树。",
    "c1b": "在红色虚线处切开，每段颜色是一个模块。灰色的基因不属于任何模块。",
    "c2": "【慢】按聚类顺序重排矩阵，对角线上出现了方块，每个方块就是一个模块。",
    "c3": "每个模块用一条曲线概括，叫模块特征基因，也就是第一主成分。",
    "c3b": "细蓝线是模块里的各个基因，黄色粗线是特征基因，抓住了它们共同的起伏。",
    "c4": "把特征基因和临床性状做相关，就知道哪个模块和疾病有关。",
    "c4b": "和特征基因最相关的基因，叫枢纽基因。",
    # beyond correlation
    "x1": "最后是第三部分。回到甲、丙、乙这条链。",
    "x2": "红柱是甲和乙的相关，很高。",
    "x2b": "偏相关，是先扣掉丙的影响，再看甲和乙剩多少关联。绿柱几乎是零。",
    "x3": "互信息也衡量关联，还能抓住非线性关系。它在每个三角形里删去最弱的边。",
    "x4": "另一种思路是回归：用转录因子预测每个靶基因，箭头越粗，作用越大。",
    "x5": "但这里的方向，其实来自事先给定的转录因子名单。",
    "x5b": "【慢】只有时间序列或扰动实验，才有机会判断谁调控谁。",
    # evaluation
    "v1": "推断准不准，要和已知的真实调控关系对照。左边是四百条候选边。",
    "v2": "真实的边通常不到百分之一。这里只有四条，就是黄色这几个。",
    "v3": "精确率，是预测的边里有多少是真的；召回率，是真的边里有多少被找到。",
    "v3b": "右图横轴是召回率，纵轴是精确率。灰色虚线是乱猜，只有百分之一左右。",
    "v3c": "【慢】所以要看曲线下的面积，并且和随机基线比。",
    "v4": "2012年一次大规模评测，比较了三十多种方法。这是示意图，每一列是一类数据。",
    "v4b": "没有一种方法处处最好，把多种方法的排序整合起来，反而最稳健。",
    "v5a": "后来有了单细胞测序，能分别测出成千上万个细胞的表达。",
    "v5": "2020年的一项评测比较了十二种单细胞方法：在真实数据上，多数方法的早期精度接近随机。",
    "v6": "所以单条边最不可靠，模块和通路层面的结论稳健得多。",
    # interpretation
    "i1": "解读模块也要小心。肿瘤数据里常有一个增殖模块，和肿瘤分级高度相关。",
    "i2": "它的枢纽往往是增殖标志物，说明的是增殖细胞多，而不是新的调控因子。",
    "i3": "想把枢纽基因说成药物靶点，至少需要扰动实验和独立数据。",
    # recap
    "r1": "好，我们总结一下。",
    "r2": "第一，共表达只是关联，调控需要方向和直接性的证据。",
    "r3": "第二，共表达网络分析的主线：软阈值、拓扑重叠、聚类、特征基因。",
    "r4": "第三，评估要和随机基线比，模块比单条边可靠。",
}

MODC = [BLUE, GREEN, GOLD, VIOLET, RED]


# ----------------------------------------------------------------------------- data
def expr(n_s=40, sizes=(70, 55, 40, 30, 20), noise=40, seed=4):
    rng = np.random.default_rng(seed)
    blocks, lab, eig = [], [], []
    for m, s in enumerate(sizes):
        e = rng.normal(size=n_s); w = rng.uniform(0.4, 1.0, s)
        blocks.append(np.outer(w, e) + rng.normal(size=(s, n_s)) * np.sqrt(1 - w[:, None] ** 2))
        lab += [m] * s; eig.append(e)
    blocks.append(rng.normal(size=(noise, n_s))); lab += [-1] * noise
    return np.vstack(blocks), np.array(lab), np.array(eig)


def sf_fit(R, b):
    A = np.abs(R) ** b; k = A.sum(1)
    h, ed = np.histogram(k, bins=10); m = (ed[:-1] + ed[1:]) / 2; p = h / h.sum()
    ok = h > 0; x, y = np.log10(m[ok]), np.log10(p[ok])
    c = np.polyfit(x, y, 1); yh = np.polyval(c, x)
    return (1 - ((y - yh) ** 2).sum() / ((y - y.mean()) ** 2).sum()) * np.sign(-c[0]), k.mean()


def tom(A):
    A = A.copy(); np.fill_diagonal(A, 0)
    L = A @ A; k = A.sum(1)
    T_ = (L + A) / (np.minimum.outer(k, k) + 1 - A)
    np.fill_diagonal(T_, 1)
    return T_


def heat_color(v):
    """v in [-1, 1] -> blue-dark-red."""
    v = float(np.clip(v, -1, 1))
    return interpolate_color(ManimColor(BG), ManimColor(RED if v > 0 else BLUE), abs(v) ** 0.8)


class Episode(Narrated):
    LINES = LINES

    def construct(self):
        self.hook()
        self.questions()
        self.difficulty()
        self.wgcna()
        self.tom_chapter()
        self.modules()
        self.beyond()
        self.evaluation()
        self.interpret()
        self.recap()

    # ------------------------------------------------------------------ hook
    def hook(self):
        rng = np.random.default_rng(2)
        a = rng.normal(size=30); c = 0.85 * a + 0.5 * rng.normal(size=30); b = 0.85 * c + 0.5 * rng.normal(size=30)
        self.chain = (a, c, b)
        r = np.corrcoef(a, b)[0, 1]
        ax = axes([0, 6, 1], [0, 6, 1], 5.0, 5.0).move_to(LEFT * 3.2 + DOWN * 0.1)
        xl, yl = xlabel(ax, "基因甲 表达量"), ylabel(ax, "基因乙 表达量")
        pts = VGroup(*[Dot(ax.c2p(x + 3, y + 3), radius=0.07, color=GOLD) for x, y in zip(a, b)])
        with self.say("h1") as d:
            self.play(Create(ax), FadeIn(xl), FadeIn(yl), run_time=1.0)
            self.play(LaggedStart(*[GrowFromCenter(p) for p in pts], lag_ratio=0.05), run_time=d * 0.5)
        with self.say("h2") as d:
            k, b0 = np.polyfit(a, b, 1)
            fitl = Line(ax.c2p(0.4, k * -2.6 + b0 + 3), ax.c2p(5.6, k * 2.6 + b0 + 3), color=RED, stroke_width=4)
            rv = MathTex(rf"r = {r:.2f}", font_size=48, color=RED).move_to(RIGHT * 3.0 + UP * 2.2)
            self.play(Create(fitl), Write(rv), run_time=1.2)
        with self.say("h2b") as d:
            self.play(Indicate(rv, color=RED), run_time=1.0)
        G = {"甲": RIGHT * 1.6 + DOWN * 0.2, "乙": RIGHT * 5.2 + DOWN * 0.2}
        nodes = {k: VGroup(Circle(radius=0.42, color=GOLD, fill_opacity=0.25, stroke_width=3), T(k, 28)).move_to(p) for k, p in G.items()}
        with self.say("h3") as d:
            self.play(*[GrowFromCenter(n) for n in nodes.values()], run_time=0.7)
            q = arrow(G["甲"], G["乙"], INK, buff=0.5)
            qm = T("调控", 26, GOLD).next_to(q, UP, buff=0.1)
            self.play(GrowArrow(q), FadeIn(qm), run_time=0.8)
        with self.say("h4") as d:
            self.play(FadeOut(q), FadeOut(qm), run_time=0.4)
            cpos = RIGHT * 3.4 + UP * 0.9
            cn = VGroup(Circle(radius=0.42, color=VIOLET, fill_opacity=0.25, stroke_width=3), T("丙", 28)).move_to(cpos)
            c1, c2 = arrow(G["甲"], cpos, INK, buff=0.5), arrow(cpos, G["乙"], INK, buff=0.5)
            self.play(GrowFromCenter(cn), GrowArrow(c1), GrowArrow(c2), run_time=1.0)
        with self.say("h4b") as d:
            hpos = RIGHT * 3.4 + DOWN * 2.3
            hn = VGroup(Circle(radius=0.42, color=MUTED, fill_opacity=0.2, stroke_width=3), T("?", 28, MUTED)).move_to(hpos)
            hd = T("隐藏因素", 22, MUTED).next_to(hn, DOWN, buff=0.12)
            h1, h2 = DashedVMobject(arrow(hpos, G["甲"], MUTED, buff=0.5)), DashedVMobject(arrow(hpos, G["乙"], MUTED, buff=0.5))
            self.play(FadeIn(hn), FadeIn(hd), Create(h1), Create(h2), run_time=1.2)
        with self.say("h5") as d:
            self.play(*[m.animate.fade(0.85) for m in self.mobjects], run_time=0.8)
            t = T("一起变化  →  谁调控谁", 54, GOLD, weight=BOLD)
            self.play(Write(t), run_time=1.0)
        fade_all(self)

    def questions(self):
        parts(self, "这一期分三部分", ["一  推断难在哪里", "二  共表达网络：一步一步", "三  超越相关与评估"], ["q0", "q1", "q2", "q3"])

    # ------------------------------------------------------------------ difficulty
    def difficulty(self):
        clip_line(self, "p0", "yt_microarray_bionetwork.mp4", "视频：BioNetwork · YouTube", start=60)
        tag = self.chapter("一  难在哪里")
        tr = ValueTracker(0)
        num = always_redraw(lambda: T(f"{int(tr.get_value()):,}", 64, GOLD, weight=BOLD).move_to(RIGHT * 2.6 + UP * 1.6))
        lab = T("候选边", 28, MUTED).move_to(RIGHT * 2.6 + UP * 2.6)
        n = 24
        grid = VGroup(*[Square(side_length=0.18, stroke_width=0, fill_color=GOLD, fill_opacity=0.0 if j <= i else 0.65)
                        for i in range(n) for j in range(n)]).arrange_in_grid(n, n, buff=0.03).move_to(LEFT * 3.6 + UP * 0.2)
        frame = SurroundingRectangle(grid, color=MUTED, buff=0.08, stroke_width=1.5)
        gl = T("10000 × 10000", 24, MUTED).next_to(frame, DOWN, buff=0.2)
        with self.say("p1") as d:
            self.play(FadeIn(tag), Create(frame), FadeIn(gl), FadeIn(lab), run_time=0.8)
            self.add(num)
            self.play(LaggedStart(*[FadeIn(s) for s in grid], lag_ratio=0.001), tr.animate.set_value(10000 * 9999 // 2), run_time=d * 0.6)
        with self.say("p2") as d:
            bar = Rectangle(width=0.15, height=0.6, fill_color=BLUE, fill_opacity=0.9, stroke_width=0).move_to(RIGHT * 1.0 + DOWN * 1.2, aligned_edge=DL)
            bl = T("几十个样本", 26, BLUE).next_to(bar, RIGHT, buff=0.25)
            big = Rectangle(width=5.0, height=0.6, stroke_color=GOLD, stroke_width=2).move_to(RIGHT * 1.0 + DOWN * 2.3, aligned_edge=DL)
            bgl = T("五千万个关系", 26, GOLD).next_to(big, DOWN, buff=0.15).align_to(big, LEFT)
            self.play(GrowFromEdge(bar, LEFT), FadeIn(bl), run_time=0.8)
            self.play(Create(big), FadeIn(bgl), run_time=0.8)
        self.remove(num)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.6)
        # indirect
        P = {"甲": LEFT * 4.8 + UP * 0.6, "丙": LEFT * 2.6 + UP * 0.6, "乙": LEFT * 0.4 + UP * 0.6}
        cols = {"甲": GOLD, "丙": VIOLET, "乙": GOLD}
        nodes = VGroup(*[VGroup(Circle(radius=0.42, color=cols[k], fill_opacity=0.25, stroke_width=3), T(k, 28)).move_to(p) for k, p in P.items()])
        a1, a2 = arrow(P["甲"], P["丙"], INK, buff=0.5), arrow(P["丙"], P["乙"], INK, buff=0.5)
        ind = ArcBetweenPoints(P["甲"] + DOWN * 0.45, P["乙"] + DOWN * 0.45, angle=PI / 2.5, color=RED, stroke_width=3)
        ind = DashedVMobject(ind)
        il = T("高相关，但不是直接调控", 22, RED).next_to(ind, DOWN, buff=0.15)
        with self.say("p3") as d:
            self.play(FadeIn(nodes), GrowArrow(a1), GrowArrow(a2), run_time=1.0)
            self.play(Create(ind), FadeIn(il), run_time=1.0)
        # cell composition
        rng = np.random.default_rng(5)
        samples = VGroup()
        fr = [0.2, 0.45, 0.75]
        for i, f in enumerate(fr):
            c0 = RIGHT * (2.0 + 1.7 * i) + UP * 1.2
            ring = Circle(radius=0.7, color=MUTED, stroke_width=2).move_to(c0)
            cells = VGroup(*[Dot(c0 + 0.5 * np.sqrt(rng.random()) * np.array([np.cos(t), np.sin(t), 0]), radius=0.07,
                                 color=VIOLET if rng.random() < f else BLUE) for t in rng.uniform(0, 2 * PI, 26)])
            samples.add(VGroup(ring, cells))
        sl = T("三个组织样本", 22, MUTED).next_to(samples, UP, buff=0.2)
        ax = axes([0, 3, 1], [0, 1, 0.5], 4.6, 2.0).move_to(RIGHT * 3.7 + DOWN * 1.6)
        u = ax.c2p(0, 1)[1] - ax.c2p(0, 0)[1]
        bars = VGroup()
        for i, f in enumerate(fr):
            for j, dx in enumerate((-0.18, 0.18)):
                h = f * (0.9 + 0.12 * j)
                bars.add(Rectangle(width=0.32, height=u * h, fill_color=VIOLET if j == 0 else GREEN, fill_opacity=0.9, stroke_width=0)
                         .move_to(ax.c2p(i + 0.5 + dx, 0), aligned_edge=DOWN))
        lg = VGroup(T("标志基因 1", 20, VIOLET), T("标志基因 2", 20, GREEN)).arrange(RIGHT, buff=0.4).next_to(ax, DOWN, buff=0.2)
        with self.say("p4") as d:
            self.play(FadeIn(samples), FadeIn(sl), run_time=1.0)
        with self.say("p4b") as d:
            self.play(Create(ax.x_axis), grow_bars(bars, 1.4), FadeIn(lg))
        with self.say("p5") as d:
            self.play(*[m.animate.fade(0.85) for m in self.mobjects if m is not tag], run_time=0.6)
            hy = T("推断的边 = 假设", 48, GOLD, weight=BOLD)
            self.play(Write(hy), run_time=1.0)
        fade_all(self)

    # ------------------------------------------------------------------ WGCNA: correlation & soft threshold
    def wgcna(self):
        tag = self.chapter("二  共表达网络：软阈值")
        X, lab, eig = expr()
        self.X, self.lab, self.eig = X, lab, eig
        R = np.corrcoef(X)
        # display subset: 8 genes from each module + 8 noise genes, shuffled
        rng = np.random.default_rng(1)
        idx = []
        for m in range(5):
            idx += list(rng.choice(np.where(lab == m)[0], 8, replace=False))
        idx += list(rng.choice(np.where(lab == -1)[0], 8, replace=False))
        idx = np.array(idx); rng.shuffle(idx)
        self.sub = idx
        n = len(idx); s = 0.115
        Rs = R[np.ix_(idx, idx)]
        cells = VGroup(*[Square(side_length=s, stroke_width=0, fill_color=heat_color(Rs[i, j]), fill_opacity=1)
                         for i in range(n) for j in range(n)]).arrange_in_grid(n, n, buff=0.006).move_to(LEFT * 3.4 + DOWN * 0.2)
        self.cells_args = (n, s)
        with self.say("w1") as d:
            self.play(FadeIn(tag), run_time=0.5)
            ttl = chip("加权基因共表达网络分析", GOLD, 32)
            self.play(FadeIn(ttl, shift=UP * 0.2), run_time=0.8)
        with self.say("w1b") as d:
            self.play(FadeOut(ttl), run_time=0.4)
            mat = VGroup(*[Line(LEFT * 0.0, RIGHT * 4.6, color=interpolate_color(ManimColor(BLUE), ManimColor(RED), rng.random()), stroke_width=3)
                           .shift(UP * (1.6 - 0.22 * i)) for i in range(14)]).move_to(ORIGIN)
            ml = T("表达矩阵：基因 × 样本", 26, MUTED).next_to(mat, UP, buff=0.3)
            self.play(LaggedStart(*[Create(l) for l in mat], lag_ratio=0.08), FadeIn(ml), run_time=d * 0.6)
        with self.say("w2") as d:
            self.play(FadeOut(mat), FadeOut(ml), run_time=0.5)
            self.play(LaggedStart(*[FadeIn(c) for c in cells], lag_ratio=0.0008), run_time=d * 0.55)
            cl = T("相关矩阵", 26, MUTED).next_to(cells, UP, buff=0.2)
            cb = VGroup(T("负相关", 20, BLUE), Rectangle(width=1.6, height=0.18, stroke_width=0).set_fill(color=[RED, BG, BLUE], opacity=1),
                        T("正相关", 20, RED)).arrange(RIGHT, buff=0.15).next_to(cells, DOWN, buff=0.25)
            self.play(FadeIn(cl), FadeIn(cb), run_time=0.6)
        ax = axes([0, 1, 0.5], [0, 1, 0.5], 4.6, 4.0, xnums=[0, 0.5, 1], ynums=[0, 0.5, 1]).move_to(RIGHT * 3.4 + DOWN * 0.2)
        xl, yl = xlabel(ax, "相关系数的绝对值"), ylabel(ax, "连接强度")
        with self.say("w3") as d:
            self.play(Create(ax), FadeIn(xl), FadeIn(yl), run_time=1.0)
            f = MathTex(r"a_{ij}=|r_{ij}|^{\beta}", font_size=44, color=INK).next_to(ax, UP, buff=0.25)
            self.play(Write(f), run_time=1.0)
            c1 = ax.plot(lambda x: x, x_range=[0, 1], color=MUTED, stroke_width=3)
            b1 = MathTex(r"\beta=1", font_size=26, color=MUTED).move_to(ax.c2p(0.45, 0.62))
            self.play(Create(c1), FadeIn(b1), run_time=0.8)
        with self.say("w3b") as d:
            ca = callout(f[0][0:3], "连接强度", DOWN, GOLD, 18, 0.08)
            cr = callout(f[0][4:9], "相关系数", DOWN, BLUE, 18, 0.08)
            cbt = callout(f[0][9], "幂次", RIGHT, RED, 18, 0.08)
            for c_ in (ca, cr, cbt):
                self.play(Create(c_), run_time=0.7)
        with self.say("w4") as d:
            self.play(FadeOut(ca), FadeOut(cr), FadeOut(cbt), run_time=0.4)
            curves = VGroup()
            for b, c, xy in ((3, BLUE, (0.66, 0.2)), (6, GOLD, (0.86, 0.15)), (12, RED, (0.97, 0.06))):
                cc = ax.plot(lambda x, b=b: x ** b, x_range=[0, 1, 0.005], color=c, stroke_width=4)
                curves.add(VGroup(cc, MathTex(rf"\beta={b}", font_size=26, color=c).move_to(ax.c2p(*xy) + LEFT * 0.25)))
            self.play(LaggedStart(*[Create(c) for c in curves], lag_ratio=0.4), run_time=d * 0.45)
        with self.say("w4b") as d:
            self.play(*[c.animate.set_fill(heat_color(np.sign(Rs.flat[k]) * abs(Rs.flat[k]) ** 3)) for k, c in enumerate(cells)], run_time=d * 0.35)
        self.play(FadeOut(VGroup(ax, xl, yl, f, c1, b1, curves)), run_time=0.6)
        bs = np.arange(1, 13)
        fits = [sf_fit(R, b) for b in bs]
        r2 = [x[0] for x in fits]; mk = [x[1] for x in fits]
        best = int(bs[np.argmax(np.array(r2) >= 0.8)])
        ax2 = axes([0, 12, 2], [0, 1, 0.5], 5.0, 4.0, xnums=[2, 4, 6, 8, 10, 12], ynums=[0, 0.5, 1]).move_to(RIGHT * 3.4 + DOWN * 0.3)
        x2, y2 = xlabel(ax2, "幂次 β"), ylabel(ax2, "无标度拟合优度")
        with self.say("w5") as d:
            self.play(Create(ax2), FadeIn(x2), FadeIn(y2), run_time=1.0)
            pts = VGroup(*[Dot(ax2.c2p(b, max(v, 0)), radius=0.07, color=INK) for b, v in zip(bs, r2)])
            self.play(LaggedStart(*[GrowFromCenter(p) for p in pts], lag_ratio=0.12), run_time=d * 0.45)
        with self.say("w6") as d:
            band = Rectangle(width=ax2.c2p(12, 0)[0] - ax2.c2p(0, 0)[0], height=ax2.c2p(0, 0.9)[1] - ax2.c2p(0, 0.8)[1],
                             fill_color=GREEN, fill_opacity=0.2, stroke_width=0).move_to(ax2.c2p(6, 0.85))
            self.play(FadeIn(band), run_time=0.7)
            pick = Circle(radius=0.18, color=GOLD, stroke_width=4).move_to(pts[best - 1])
            pl = T(f"β = {best}", 28, GOLD, weight=BOLD).move_to(ax2.c2p(8, 0.42))
            self.play(Create(pick), FadeIn(pl), run_time=0.8)
            kl = T(f"平均连接度 ≈ {mk[best - 1]:.1f}", 22, MUTED).next_to(pl, DOWN, buff=0.15)
            self.play(FadeIn(kl), run_time=0.5)
        print("BETA", best)
        self.beta = best
        self.cells = cells
        self.play(*[FadeOut(m) for m in self.mobjects if m is not cells], run_time=0.6)

    # ------------------------------------------------------------------ TOM
    def tom_chapter(self):
        tag = self.chapter("二  共表达网络：拓扑重叠")
        self.play(FadeIn(tag), self.cells.animate.set_opacity(0.0), run_time=0.6)
        self.remove(self.cells)
        i, j = LEFT * 4.6, LEFT * 1.6
        shared = [LEFT * 3.1 + UP * (1.6 - 0.8 * k) for k in range(5)]
        ni = VGroup(Circle(radius=0.35, color=GOLD, fill_opacity=0.3, stroke_width=3), T("i", 26)).move_to(i)
        nj = VGroup(Circle(radius=0.35, color=GOLD, fill_opacity=0.3, stroke_width=3), T("j", 26)).move_to(j)
        sd = VGroup(*[Dot(p, radius=0.11, color=BLUE) for p in shared])
        se = VGroup(*[Line(a, p, color=BLUE, stroke_width=2.5, stroke_opacity=0.8) for p in shared for a in (i, j)])
        ij = DashedLine(i + RIGHT * 0.35, j + LEFT * 0.35, color=MUTED, stroke_width=2)
        f = MathTex(r"\mathrm{TOM}_{ij}=\frac{\sum_u a_{iu}a_{uj}+a_{ij}}{\min(k_i,k_j)+1-a_{ij}}", font_size=40, color=INK).move_to(RIGHT * 3.4 + UP * 2.2)
        # numbers for the two toy configurations
        def tomv(a_ij, shared_w, extra_i, extra_j):
            l = sum(w * w for w in shared_w)
            ki = a_ij + sum(shared_w) + sum(extra_i); kj = a_ij + sum(shared_w) + sum(extra_j)
            return (l + a_ij) / (min(ki, kj) + 1 - a_ij)
        t_hi = tomv(0.3, [0.8] * 5, [], [])
        t_lo = tomv(0.9, [], [0.8] * 5, [0.8] * 5)
        with self.say("t1") as d:
            self.play(GrowFromCenter(ni), GrowFromCenter(nj), Create(ij), run_time=0.8)
            self.play(Write(f), run_time=d * 0.4)
        with self.say("t1b") as d:
            w, h = f.width * 0.66, f.height / 2
            nb = Rectangle(width=w, height=h, color=GOLD, stroke_width=2.5).move_to(f.get_corner(UR) + LEFT * w / 2 + DOWN * h / 2)
            db = Rectangle(width=w, height=h, color=BLUE, stroke_width=2.5).move_to(f.get_corner(DR) + LEFT * w / 2 + UP * h / 2)
            nl = T("共同邻居 + 直接连接", 18, GOLD).next_to(nb, UP, buff=0.08)
            dl_ = T("较小的总连接", 18, BLUE).next_to(db, DOWN, buff=0.08)
            self.play(Create(nb), FadeIn(nl), run_time=0.8)
            self.play(Create(db), FadeIn(dl_), run_time=0.8)
        with self.say("t1c") as d:
            self.play(FadeOut(VGroup(nb, nl, db, dl_)), run_time=0.4)
            rng01 = T("0  ≤  拓扑重叠  ≤  1", 26, INK).next_to(f, DOWN, buff=0.4)
            self.play(FadeIn(rng01), run_time=0.6)
        with self.say("t2") as d:
            self.play(FadeOut(rng01), run_time=0.3)
            self.play(LaggedStart(*[GrowFromCenter(x) for x in sd], lag_ratio=0.1), LaggedStart(*[Create(e) for e in se], lag_ratio=0.05), run_time=d * 0.4)
            v1 = VGroup(T("直接连接 0.3", 24, MUTED), T(f"拓扑重叠 ≈ {t_hi:.2f}", 28, GREEN, weight=BOLD)).arrange(DOWN, buff=0.15).move_to(RIGHT * 3.4 + UP * 0.2)
            self.play(FadeIn(v1), run_time=0.8)
        left = VGroup(ni, nj, ij, sd, se)
        with self.say("t3") as d:
            self.play(left.animate.fade(0.85), v1.animate.fade(0.7), run_time=0.5)
            a, b = LEFT * 4.6 + DOWN * 2.3, LEFT * 1.6 + DOWN * 2.3
            na = VGroup(Circle(radius=0.3, color=GOLD, fill_opacity=0.3, stroke_width=3), T("i", 22)).move_to(a)
            nb = VGroup(Circle(radius=0.3, color=GOLD, fill_opacity=0.3, stroke_width=3), T("j", 22)).move_to(b)
            e = Line(a + RIGHT * 0.3, b + LEFT * 0.3, color=RED, stroke_width=6)
            fa = VGroup(*[Line(a, a + 0.9 * np.array([np.cos(t), np.sin(t), 0]), color=BLUE, stroke_width=2) for t in np.linspace(0.6 * PI, 1.4 * PI, 5)])
            fb = VGroup(*[Line(b, b + 0.9 * np.array([np.cos(t), np.sin(t), 0]), color=VIOLET, stroke_width=2) for t in np.linspace(-0.4 * PI, 0.4 * PI, 5)])
            self.play(FadeIn(na), FadeIn(nb), Create(e), Create(fa), Create(fb), run_time=1.2)
            v2 = VGroup(T("直接连接 0.9", 24, MUTED), T(f"拓扑重叠 ≈ {t_lo:.2f}", 28, RED, weight=BOLD)).arrange(DOWN, buff=0.15).move_to(RIGHT * 3.4 + DOWN * 1.8)
            self.play(FadeIn(v2), run_time=0.8)
        fade_all(self)

    # ------------------------------------------------------------------ modules
    def modules(self):
        tag = self.chapter("二  共表达网络：模块")
        X, lab, idx = self.X, self.lab, self.sub
        Rs = np.corrcoef(X[idx])
        A = np.abs(Rs) ** self.beta
        TOM = tom(A)
        D = 1 - TOM; np.fill_diagonal(D, 0)
        Z = linkage(squareform(D, checks=False), "average")
        dn = dendrogram(Z, no_plot=True)
        order = dn["leaves"]
        cut = 0.9 * Z[-5, 2] + 0.1 * Z[-4, 2]
        cl = fcluster(Z, t=cut, criterion="distance")
        sizes = {c: (cl == c).sum() for c in set(cl)}
        big = sorted([c for c in sizes if sizes[c] >= 4], key=lambda c: -sizes[c])
        # map clusters to colours by their dominant true module (stable colouring)
        colmap = {}
        for c in big:
            tm = np.bincount(np.maximum(lab[idx][cl == c], 0) if (lab[idx][cl == c] >= 0).any() else [0]).argmax()
            colmap[c] = MODC[len(colmap) % len(MODC)]
        gcol = [colmap.get(c, MUTED) for c in cl]
        n = len(idx)
        # dendrogram drawing
        W, H0 = 5.6, 2.2
        x0, y0 = -6.2, 0.6
        maxh = Z[:, 2].max()
        dl = VGroup()
        for xs, ys in zip(dn["icoord"], dn["dcoord"]):
            pts = [np.array([x0 + (x - 5) / (10 * n - 10) * W, y0 + y / maxh * H0, 0]) for x, y in zip(xs, ys)]
            dl.add(VMobject(stroke_color=MUTED, stroke_width=1.6).set_points_as_corners(pts))
        cutl = DashedLine([x0 - 0.1, y0 + cut / maxh * H0, 0], [x0 + W + 0.1, y0 + cut / maxh * H0, 0], color=RED)
        strip = VGroup(*[Rectangle(width=W / n, height=0.28, stroke_width=0, fill_color=gcol[order[k]], fill_opacity=1)
                         .move_to([x0 + k / (n - 1) * W, y0 - 0.3, 0]) for k in range(n)])
        with self.say("c1") as d:
            self.play(FadeIn(tag), run_time=0.5)
            self.play(Create(dl), run_time=d * 0.45)
        with self.say("c1b") as d:
            self.play(Create(cutl), run_time=0.6)
            self.play(LaggedStart(*[FadeIn(s) for s in strip], lag_ratio=0.02), run_time=1.0)
        s = 0.1
        def heat(ordr):
            g = VGroup(*[Square(side_length=s, stroke_width=0, fill_color=heat_color(np.sign(Rs[a, b]) * TOM[a, b] ** 0.5 if a != b else 1), fill_opacity=1)
                         for a in ordr for b in ordr]).arrange_in_grid(n, n, buff=0.005)
            return g
        hm0 = heat(list(range(n))).move_to(RIGHT * 3.6 + DOWN * 0.3)
        hm1 = heat(order).move_to(hm0)
        with self.say("c2") as d:
            self.play(FadeIn(hm0), run_time=0.8)
            self.play(Transform(hm0, hm1), run_time=d * 0.4)
            # outline module blocks
            outlines = VGroup()
            k = 0
            while k < n:
                c = cl[order[k]]; e = k
                while e + 1 < n and cl[order[e + 1]] == c:
                    e += 1
                if c in colmap:
                    tl = hm1[k * n + k].get_corner(UL); br = hm1[e * n + e].get_corner(DR)
                    outlines.add(Rectangle(width=br[0] - tl[0], height=tl[1] - br[1], color=colmap[c], stroke_width=3).move_to((tl + br) / 2))
                k = e + 1
            self.play(LaggedStart(*[Create(o) for o in outlines], lag_ratio=0.2), run_time=1.2)
            gr = T("灰色 = 未归入模块", 20, MUTED).next_to(strip, DOWN, buff=0.2).align_to(strip, LEFT)
            self.play(FadeIn(gr), run_time=0.5)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.6)
        # eigengene of the largest true module
        m0 = 0
        genes = np.where(lab == m0)[0][:14]
        Xs = X[genes]; Xs = (Xs - Xs.mean(1, keepdims=True)) / Xs.std(1, keepdims=True)
        u, sv, vt = np.linalg.svd(Xs, full_matrices=False)
        me = vt[0] * np.sign(np.corrcoef(vt[0], Xs.mean(0))[0, 1])
        me = me / me.std()
        ns = X.shape[1]
        ax = axes([0, ns, 10], [-3, 3, 1], 7.5, 3.2).move_to(LEFT * 1.6 + UP * 0.6)
        xl = T("样本", 22, MUTED).next_to(ax, DOWN, buff=0.1)
        thin = VGroup(*[ax.plot_line_graph(np.arange(ns), g, line_color=MODC[0], add_vertex_dots=False, stroke_width=1.5).set_stroke(opacity=0.35) for g in Xs])
        bold = ax.plot_line_graph(np.arange(ns), me, line_color=GOLD, add_vertex_dots=False, stroke_width=5)
        with self.say("c3") as d:
            self.play(Create(ax.x_axis), FadeIn(xl), run_time=0.6)
        with self.say("c3b") as d:
            self.play(LaggedStart(*[Create(t) for t in thin], lag_ratio=0.05), run_time=d * 0.35)
            bl = T("模块特征基因", 26, GOLD, weight=BOLD).next_to(ax, RIGHT, buff=0.2).shift(UP * 0.8)
            self.play(Create(bold), FadeIn(bl), run_time=d * 0.3)
        # trait association (real correlations of module eigengenes with a synthetic trait driven by module 2)
        rng = np.random.default_rng(9)
        trait = 0.8 * self.eig[2] / self.eig[2].std() + 0.6 * rng.normal(size=ns)
        cors = [np.corrcoef(self.eig[m], trait)[0, 1] for m in range(5)]
        ax2 = axes([0, 5, 1], [-1, 1, 0.5], 5.6, 2.4, ynums=[-1, 0, 1], fs=18).move_to(LEFT * 1.6 + DOWN * 2.4)
        u2 = ax2.c2p(0, 1)[1] - ax2.c2p(0, 0)[1]
        bars = VGroup(*[Rectangle(width=0.7, height=abs(c) * u2, stroke_width=0, fill_color=MODC[m], fill_opacity=0.9)
                        .move_to(ax2.c2p(m + 0.5, 0), aligned_edge=DOWN if c > 0 else UP) for m, c in enumerate(cors)])
        tl = T("与临床性状的相关", 22, MUTED).next_to(ax2, RIGHT, buff=0.2)
        with self.say("c4") as d:
            self.play(VGroup(ax, xl, thin, bold, bl).animate.shift(UP * 0.6).scale(0.85), run_time=0.6)
            self.play(Create(ax2), FadeIn(tl), run_time=0.6)
            self.play(LaggedStart(*[GrowFromEdge(b, DOWN if c > 0 else UP) for b, c in zip(bars, cors)], lag_ratio=0.15), run_time=1.4)
            best = int(np.argmax(np.abs(cors)))
            self.play(Indicate(bars[best], color=WHITE), run_time=0.8)
        with self.say("c4b") as d:
            hub = chip("枢纽基因", GOLD, 24).move_to(RIGHT * 5.0 + UP * 0.2)
            self.play(FadeIn(hub, shift=LEFT * 0.2), run_time=0.6)
        fade_all(self)

    # ------------------------------------------------------------------ beyond correlation
    def beyond(self):
        tag = self.chapter("三  超越相关")
        a, c, b = self.chain
        r_ab = np.corrcoef(a, b)[0, 1]
        # partial correlation of a,b given c
        ra = a - np.polyval(np.polyfit(c, a, 1), c); rb = b - np.polyval(np.polyfit(c, b, 1), c)
        p_ab = np.corrcoef(ra, rb)[0, 1]
        P = {"甲": LEFT * 5.0 + UP * 0.8, "丙": LEFT * 3.0 + UP * 2.2, "乙": LEFT * 1.0 + UP * 0.8}
        nodes = {k: VGroup(Circle(radius=0.4, color=VIOLET if k == "丙" else GOLD, fill_opacity=0.25, stroke_width=3), T(k, 26)).move_to(p) for k, p in P.items()}
        e1, e2 = arrow(P["甲"], P["丙"], INK, buff=0.48), arrow(P["丙"], P["乙"], INK, buff=0.48)
        ab = DashedLine(P["甲"] + RIGHT * 0.45, P["乙"] + LEFT * 0.45, color=RED, stroke_width=4)
        with self.say("x1") as d:
            self.play(FadeIn(tag), *[GrowFromCenter(n) for n in nodes.values()], GrowArrow(e1), GrowArrow(e2), run_time=1.2)
            self.play(Create(ab), run_time=0.6)
        ax = axes([0, 2, 1], [0, 1, 0.5], 4.4, 3.2, ynums=[0, 0.5, 1]).move_to(RIGHT * 3.4 + UP * 0.6)
        u = ax.c2p(0, 1)[1] - ax.c2p(0, 0)[1]
        b1 = Rectangle(width=1.0, height=u * abs(r_ab), fill_color=RED, fill_opacity=0.9, stroke_width=0).move_to(ax.c2p(0.5, 0), aligned_edge=DOWN)
        b2 = Rectangle(width=1.0, height=max(u * abs(p_ab), 0.02), fill_color=GREEN, fill_opacity=0.9, stroke_width=0).move_to(ax.c2p(1.5, 0), aligned_edge=DOWN)
        l1 = VGroup(T("相关", 22), MathTex(f"{r_ab:.2f}", font_size=30, color=RED)).arrange(DOWN, buff=0.1).next_to(ax.c2p(0.5, 0), DOWN, buff=0.15)
        l2 = VGroup(T("控制丙后", 22), MathTex(f"{p_ab:.2f}", font_size=30, color=GREEN)).arrange(DOWN, buff=0.1).next_to(ax.c2p(1.5, 0), DOWN, buff=0.15)
        with self.say("x2") as d:
            self.play(Create(ax), run_time=0.6)
            self.play(GrowFromEdge(b1, DOWN), FadeIn(l1), run_time=0.8)
        with self.say("x2b") as d:
            self.play(Indicate(nodes["丙"], color=VIOLET), run_time=0.7)
            self.play(GrowFromEdge(b2, DOWN), FadeIn(l2), ab.animate.fade(0.85), run_time=0.9)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.6)
        # DPI on a triangle
        Q = [LEFT * 4.8 + DOWN * 0.2, LEFT * 1.8 + DOWN * 0.2, LEFT * 3.3 + UP * 2.2]
        tri_n = VGroup(*[Dot(q, radius=0.18, color=GOLD) for q in Q])
        ws = [(0, 2, 0.9), (2, 1, 0.8), (0, 1, 0.5)]
        tri_e = VGroup(*[Line(Q[x], Q[y], color=INK, stroke_width=2 + 6 * w) for x, y, w in ws])
        tri_l = VGroup(*[MathTex(f"{w}", font_size=30, color=MUTED).move_to((Q[x] + Q[y]) / 2 + (UP * 0.3 if x + y != 1 else DOWN * 0.35) + (LEFT * 0.3 if (x, y) == (0, 2) else RIGHT * 0.3 if (x, y) == (2, 1) else 0))
                       for x, y, w in ws])
        mi = T("互信息", 26, MUTED).move_to(LEFT * 3.3 + DOWN * 1.2)
        with self.say("x3") as d:
            self.play(FadeIn(tri_n), Create(tri_e), FadeIn(tri_l), FadeIn(mi), run_time=1.2)
            self.play(tri_e[2].animate.set_color(RED), run_time=0.6)
            self.play(FadeOut(tri_e[2]), FadeOut(tri_l[2]), run_time=0.8)
        # regression on TF list
        tfs = [RIGHT * 1.6 + UP * (1.8 - 0.9 * k) for k in range(5)]
        tgt = RIGHT * 5.0 + UP * 0.0
        tfd = VGroup(*[VGroup(Circle(radius=0.26, color=GOLD, fill_opacity=0.3, stroke_width=2.5), T(f"TF{k + 1}", 16)).move_to(p) for k, p in enumerate(tfs)])
        tg = VGroup(Circle(radius=0.36, color=GREEN, fill_opacity=0.3, stroke_width=3), T("靶基因", 18)).move_to(tgt)
        imp = [0.9, 0.15, 0.6, 0.05, 0.25]
        arr = VGroup(*[arrow(p, tgt, GOLD, buff=0.38, sw=1 + 7 * w).set_opacity(0.3 + 0.7 * w) for p, w in zip(tfs, imp)])
        tl = T("转录因子名单", 22, GOLD).next_to(tfd, UP, buff=0.25)
        with self.say("x4") as d:
            self.play(FadeIn(tfd), FadeIn(tl), FadeIn(tg), run_time=0.8)
            self.play(LaggedStart(*[GrowArrow(a) for a in arr], lag_ratio=0.15), run_time=d * 0.4)
        with self.say("x5") as d:
            self.play(Indicate(tl, color=GOLD, scale_factor=1.3), run_time=1.0)
        with self.say("x5b") as d:
            ev = VGroup(chip("时间序列", BLUE, 24), chip("扰动实验", RED, 24)).arrange(RIGHT, buff=0.4).move_to(RIGHT * 3.3 + DOWN * 2.8)
            self.play(LaggedStart(*[FadeIn(e, shift=UP * 0.2) for e in ev], lag_ratio=0.3), run_time=1.0)
        fade_all(self)

    # ------------------------------------------------------------------ evaluation
    def evaluation(self):
        tag = self.chapter("三  怎样评估")
        n = 20
        rng = np.random.default_rng(3)
        true = set(rng.choice(n * n, 4, replace=False))
        grid = VGroup(*[Square(side_length=0.2, stroke_width=0.6, stroke_color=BG, fill_color=MUTED, fill_opacity=0.35) for _ in range(n * n)])
        grid.arrange_in_grid(n, n, buff=0.02).move_to(LEFT * 3.6 + DOWN * 0.2)
        with self.say("v1") as d:
            self.play(FadeIn(tag), FadeIn(grid, lag_ratio=0.002), run_time=d * 0.5)
            gl = T("400 条候选边", 22, MUTED).next_to(grid, UP, buff=0.2)
            self.play(FadeIn(gl), run_time=0.5)
        with self.say("v2") as d:
            self.play(*[grid[k].animate.set_fill(GOLD, opacity=1).scale(1.3) for k in true], run_time=1.0)
            tl = T("真实的边：4 条 = 1%", 24, GOLD).next_to(grid, DOWN, buff=0.2)
            self.play(FadeIn(tl), run_time=0.6)
        # PR curves from simulated scores
        N, pi = 20000, 0.01
        y = rng.random(N) < pi
        def pr(score):
            o = np.argsort(-score); yy = y[o]
            tp = np.cumsum(yy); k = np.arange(1, N + 1)
            prec, rec = tp / k, tp / yy.sum()
            auc = np.sum(np.diff(np.r_[0, rec]) * prec)
            return rec, prec, auc
        good = y * 1.6 + rng.normal(size=N)
        rnd = rng.normal(size=N)
        rg, pg, ag = pr(good); rr_, pr_, ar = pr(rnd)
        ax = axes([0, 1, 0.5], [0, 0.6, 0.2], 5.2, 4.0, xnums=[0, 0.5, 1], ynums=[0, 0.2, 0.4, 0.6]).move_to(RIGHT * 3.3 + DOWN * 0.2)
        xl, yl = xlabel(ax, "召回率"), ylabel(ax, "精确率")
        sel = np.unique(np.r_[np.linspace(0, N - 1, 400).astype(int)])
        with self.say("v3") as d:
            defs = VGroup(T("精确率 = 预测中的真边 / 预测的边", 24, INK), T("召回率 = 找到的真边 / 全部真边", 24, INK)).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to(RIGHT * 3.3 + UP * 0.4)
            self.play(FadeIn(defs[0], shift=UP * 0.2), run_time=0.8)
            self.play(FadeIn(defs[1], shift=UP * 0.2), run_time=0.8)
        with self.say("v3b") as d:
            self.play(FadeOut(defs), run_time=0.4)
            self.play(Create(ax), FadeIn(xl), FadeIn(yl), run_time=1.0)
            base = DashedLine(ax.c2p(0, pi), ax.c2p(1, pi), color=MUTED, stroke_width=3)
            bl = T("随机基线", 20, MUTED).next_to(ax.c2p(0.12, pi), UP, buff=0.1)
            self.play(Create(base), FadeIn(bl), run_time=0.8)
            cg = ax.plot_line_graph(rg[sel[5:]], np.minimum(pg[sel[5:]], 0.6), line_color=GREEN, add_vertex_dots=False, stroke_width=4)
            self.play(Create(cg), run_time=d * 0.3)
        with self.say("v3c") as d:
            xs_, ys_ = rg[sel[5:]], np.minimum(pg[sel[5:]], 0.6)
            area = Polygon(*[ax.c2p(x_, y_) for x_, y_ in zip(xs_, ys_)], ax.c2p(xs_[-1], 0), ax.c2p(xs_[0], 0), stroke_width=0, fill_color=GREEN, fill_opacity=0.25)
            self.play(FadeIn(area), run_time=0.8)
            al = VGroup(T(f"曲线下面积 {ag:.2f}", 22, GREEN), T(f"随机 ≈ {pi:.2f}", 22, MUTED)).arrange(DOWN, aligned_edge=LEFT, buff=0.1).move_to(ax.c2p(0.68, 0.48))
            self.play(FadeIn(al), run_time=0.6)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.6)
        # benchmarks: many methods, none best everywhere; integration
        rng = np.random.default_rng(11)
        ds = ["模拟数据", "大肠杆菌", "酵母"]
        M = 30
        sc = rng.uniform(0.2, 1.0, (M, 3)) * np.array([1.0, 0.7, 0.35])
        ax3 = axes([0, 3, 1], [0, 1, 0.5], 6.0, 3.6).move_to(LEFT * 1.4 + DOWN * 0.4)
        ticks = VGroup(*[T(s, 22, MUTED).next_to(ax3.c2p(i + 0.5, 0), DOWN, buff=0.15) for i, s in enumerate(ds)])
        yl3 = ylabel(ax3, "相对得分")
        cols = [interpolate_color(ManimColor(BLUE), ManimColor(VIOLET), k / M) for k in range(M)]
        dots = VGroup(*[Dot(ax3.c2p(i + 0.5 + rng.uniform(-0.3, 0.3), sc[m, i]), radius=0.06, color=cols[m]).set_opacity(0.8) for m in range(M) for i in range(3)])
        with self.say("v4") as d:
            self.play(FadeIn(tag), Create(ax3), FadeIn(ticks), FadeIn(yl3), run_time=0.8)
            self.play(LaggedStart(*[GrowFromCenter(x) for x in dots], lag_ratio=0.01), run_time=d * 0.3)
            tops = [int(np.argmax(sc[:, i])) for i in range(3)]
            rings = VGroup(*[Circle(radius=0.14, color=GOLD, stroke_width=3).move_to(dots[tops[i] * 3 + i]) for i in range(3)])
            sk = T("示意图", 20, MUTED).next_to(ax3, UP, buff=0.1).align_to(ax3, LEFT)
            self.play(FadeIn(sk), run_time=0.4)
        with self.say("v4b") as d:
            self.play(Create(rings), run_time=0.8)
            integ = [np.sort(sc[:, i])[-4] * 1.02 for i in range(3)]
            star = VGroup(*[Star(n=5, outer_radius=0.17, color=GOLD, fill_opacity=1).move_to(ax3.c2p(i + 0.5, integ[i])) for i in range(3)])
            sl = VGroup(Star(n=5, outer_radius=0.14, color=GOLD, fill_opacity=1), T("整合多种方法", 22, GOLD)).arrange(RIGHT, buff=0.15).next_to(ax3, RIGHT, buff=0.3).shift(UP * 1.0)
            self.play(FadeIn(star), FadeIn(sl), run_time=0.8)
        self.play(*[FadeOut(m) for m in (ax3, ticks, yl3, dots, rings, star, sl, sk)], run_time=0.6)
        clip_line(self, "v5a", "yt_singlecell_illumina.mp4", "视频：Illumina · YouTube", start=20)
        with self.say("v5") as d:
            scale = Line(LEFT * 4.5, RIGHT * 4.5, color=MUTED, stroke_width=6).shift(DOWN * 0.6)
            lo = T("随机水平", 24, RED).next_to(scale.get_left(), DOWN, buff=0.3)
            hi = T("完美", 24, GREEN).next_to(scale.get_right(), DOWN, buff=0.3)
            tk = VGroup(Line(UP * 0.2, DOWN * 0.2, color=RED, stroke_width=5).move_to(scale.get_left()),
                        Line(UP * 0.2, DOWN * 0.2, color=GREEN, stroke_width=5).move_to(scale.get_right()))
            hd = T("真实数据上的 12 种单细胞方法", 26, INK).next_to(scale, UP, buff=1.4)
            rngb = np.random.default_rng(12)
            ms = VGroup(*[Dot(radius=0.13, color=BLUE).move_to(RIGHT * (-4.5 + rngb.uniform(0.1, 2.0)) + DOWN * 0.6 + UP * (0.3 + 0.28 * (k % 4)))
                          for k in range(12)])
            starts = [m.copy().move_to(hd.get_center() + RIGHT * (k - 5.5) * 0.45 + DOWN * 0.6) for k, m in enumerate(ms)]
            self.play(Create(scale), FadeIn(tk), FadeIn(lo), FadeIn(hi), FadeIn(hd), run_time=0.8)
            self.play(LaggedStart(*[FadeIn(s_) for s_ in starts], lag_ratio=0.05), run_time=0.6)
            self.play(*[Transform(s_, m) for s_, m in zip(starts, ms)], run_time=1.4)
        with self.say("v6") as d:
            self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.6)
            lv = VGroup(chip("单条边", RED, 28), chip("模块", GOLD, 28), chip("通路", GREEN, 28)).arrange(RIGHT, buff=0.6)
            arr = Arrow(lv[0].get_bottom() + DOWN * 0.5, lv[2].get_bottom() + DOWN * 0.5, color=GREEN, buff=0)
            al = T("越来越稳健", 24, GREEN).next_to(arr, DOWN, buff=0.15)
            self.play(LaggedStart(*[FadeIn(x, shift=UP * 0.2) for x in lv], lag_ratio=0.3), run_time=1.2)
            self.play(GrowArrow(arr), FadeIn(al), run_time=0.8)
        fade_all(self)

    # ------------------------------------------------------------------ interpretation
    def interpret(self):
        tag = self.chapter("三  解读模块")
        rng = np.random.default_rng(6)
        ns = 40
        grade = np.sort(rng.integers(1, 4, ns))
        prolif = grade / 3 + 0.25 * rng.normal(size=ns)
        ax = axes([0, ns, 10], [-0.5, 1.6, 0.5], 6.2, 3.2).move_to(LEFT * 2.6 + DOWN * 0.2)
        xl = xlabel(ax, "肿瘤样本（按分级排序）", 22, 0.2)
        gb = VGroup(*[Rectangle(width=6.2 / ns, height=0.25, stroke_width=0, fill_color=[GREEN, GOLD, RED][g - 1], fill_opacity=0.9)
                      .move_to(ax.c2p(i + 0.5, -0.5) + DOWN * 0.25) for i, g in enumerate(grade)])
        line = ax.plot_line_graph(np.arange(ns) + 0.5, prolif, line_color=VIOLET, add_vertex_dots=False, stroke_width=4)
        ll = T("增殖模块特征基因", 22, VIOLET).next_to(ax, UP, buff=0.1)
        with self.say("i1") as d:
            self.play(FadeIn(tag), Create(ax.x_axis), FadeIn(xl), FadeIn(gb), run_time=1.0)
            self.play(Create(line), FadeIn(ll), run_time=d * 0.4)
        with self.say("i2") as d:
            cells = VGroup()
            for i, f in enumerate((0.15, 0.5, 0.85)):
                c0 = RIGHT * (2.6 + 1.6 * i) + UP * 1.0
                ring = Circle(radius=0.65, color=MUTED, stroke_width=2).move_to(c0)
                ds = VGroup(*[Dot(c0 + 0.48 * np.sqrt(rng.random()) * np.array([np.cos(t), np.sin(t), 0]), radius=0.07,
                                  color=VIOLET if rng.random() < f else MUTED) for t in rng.uniform(0, 2 * PI, 24)])
                cells.add(VGroup(ring, ds))
            cl = T("增殖细胞比例升高", 24, VIOLET).next_to(cells, DOWN, buff=0.3)
            self.play(FadeIn(cells, lag_ratio=0.2), run_time=1.2)
            self.play(FadeIn(cl), run_time=0.6)
        with self.say("i3") as d:
            ev = VGroup(chip("扰动实验", RED, 26), chip("独立数据", BLUE, 26)).arrange(RIGHT, buff=0.4).move_to(RIGHT * 4.0 + DOWN * 2.2)
            hub = chip("枢纽基因 → 靶点？", GOLD, 26).next_to(ev, UP, buff=0.35)
            self.play(FadeIn(hub), run_time=0.6)
            self.play(LaggedStart(*[FadeIn(e, shift=UP * 0.2) for e in ev], lag_ratio=0.3), run_time=1.0)
        fade_all(self)

    # ------------------------------------------------------------------ recap
    def recap(self):
        with self.say("r1") as d:
            head = T("三个要点", 40, INK, weight=BOLD).to_edge(UP, buff=0.7)
            self.play(Write(head), run_time=0.8)
        items = [("r2", GOLD, "共表达是关联，调控需要方向与直接性"),
                 ("r3", BLUE, "软阈值 → 拓扑重叠 → 聚类 → 特征基因"),
                 ("r4", GREEN, "对照随机基线，模块比单条边可靠")]
        rows = VGroup()
        for i, (k, c, s) in enumerate(items):
            num = Circle(radius=0.32, color=c, fill_opacity=0.18, stroke_width=3).add(T(str(i + 1), 28, c, weight=BOLD))
            rows.add(VGroup(num, T(s, 30, INK)).arrange(RIGHT, buff=0.4))
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.6).next_to(head, DOWN, buff=0.8)
        for (k, _, _), row in zip(items, rows):
            with self.say(k) as d:
                self.play(FadeIn(row, shift=RIGHT * 0.3), run_time=0.8)
        self.wait(1.5)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=1.0)
