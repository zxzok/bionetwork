"""Animated explainer: 小世界与无标度 (Watts-Strogatz, power laws, Barabási-Albert, duplication-divergence, fitness, identification)."""
import random

import networkx as nx
import numpy as np

from common import *  # noqa: F401,F403
from ahelp import NetView, counter, fit, log_axes, logbin, nv_edge, recap_rows, sf_graph, parts_slide

TITLE = "小世界与无标度：捷径、枢纽与优先连接"

# ---- Watts-Strogatz curve, N=1000, K=10 (computed once at import)
WS_B = np.logspace(-4, 0, 13)
_G0 = nx.watts_strogatz_graph(1000, 10, 0, seed=1)
WS_C0, WS_L0 = nx.average_clustering(_G0), nx.average_shortest_path_length(_G0)
WS_C, WS_L = [], []
for _b in WS_B:
    _g = nx.connected_watts_strogatz_graph(1000, 10, _b, seed=1)
    WS_C.append(nx.average_clustering(_g) / WS_C0)
    WS_L.append(nx.average_shortest_path_length(_g) / WS_L0)
_i01 = int(np.argmin(abs(WS_B - 0.01)))
assert 0.15 < WS_L[_i01] < 0.25 and WS_C[_i01] > 0.95, (WS_L[_i01], WS_C[_i01])

LINES = {
    # hook: Milgram
    "h0": "我们从一个关于熟人关系的实验讲起。",
    "h1": "1967年，一位社会心理学家请一群普通人，把一封信转交给远在波士顿的一位陌生人。",
    "h2": "规则是：每个人只能把信寄给自己直呼其名的熟人，再由熟人继续往下传。",
    "h3": "最终送到的六十四封信，平均只转手了大约六次。这就是六度分隔这个说法的由来。",
    "h4": "【慢】可是，你朋友的朋友，很多本来就是你的朋友。圈子这么抱团，路径照样这么短——这正是这一期要解释的现象。",
    # parts
    "q0": "这一期分三部分来讲。",
    "q1": "第一部分，小世界：高聚类和短路径，怎样同时存在。",
    "q2": "第二部分，无标度：长尾和枢纽，是从哪里来的。",
    "q3": "第三部分，怎样判断一张真实网络，是不是小世界、是不是无标度。",
    # lattice vs random
    "l1": "先看第一部分。我们从两个极端说起。左边是规则网格：节点排成一圈，每个节点只和左右最近的几个邻居相连。",
    "l2": "邻居的邻居，大多也是邻居，所以聚集系数很高。聚集系数，就是一个节点的邻居之间，互相连着的比例。",
    "l2b": "可要走到圆环对面，只能一步一步挪过去。从这个点出发，要走六步。",
    "l3": "右边是随机网络。边是随机连的，两三步就能到达对面；但邻居之间，几乎互不相识。",
    "l4": "看具体的数。一千个节点、每个节点十条边时，规则网格平均要走大约五十步，随机网络只要三步左右。",
    "l4b": "【慢】聚集系数却反过来：规则网格是零点六七，随机网络只有零点零一。",
    "l5": "真实网络却两头都占。1998年，沃茨和斯特罗加茨比较了三张真实网络：演员合作网、电网，和线虫的神经网络。",
    "l5b": "这张表是它们的聚集系数。金色是真实网络，灰色是同样规模的随机网络。真实网络的路径和随机网络差不多短，聚集系数却高出一到三个数量级。",
    # WS model
    "w1": "他们的模型很简单：从规则网格出发，把每条边以一个小概率，改连到随机选的节点上。这个概率，叫重连概率。",
    "w2": "改连几条边，就出现了几条横跨圆环的捷径。",
    "w3": "看右边的平均路径。一条捷径，能让一大片区域之间的路径同时变短。路径长度是全局量，对捷径非常敏感。",
    "w4": "而聚集系数是局部量。一条边被改连，只破坏它附近的几个三角形，所以只降了一点。",
    "w5": "现在把两条曲线画在一起。横轴是重连概率，用对数刻度，从万分之一到一；纵轴是相对于规则网格的比值。",
    "w6": "金色曲线是平均路径，绿色曲线是聚集系数。注意看——只重连百分之一的边，平均路径就降到原来的五分之一左右，聚集系数却几乎没动。",
    "w7": "【慢】两条曲线之间这段宽阔的区间，就是小世界：高聚类和短路径，同时存在。",
    "w8": "一句话：破坏聚类需要大量随机性，制造捷径只需要一点随机性。",
    "w9": "这个专题的知识页面里，有画面上的交互演示。拖动重连概率，左边的圆环会长出捷径，右边的两条曲线一起变化。",
    # C. elegans
    "n0": "沃茨和斯特罗加茨用到的生物学例子，是一种很小的线虫，叫秀丽隐杆线虫。画面里就是这种线虫。",
    "n1": "它只有三百零二个神经元，是第一个被完整绘出接线图的动物神经系统。",
    "n2": "下面左边一组柱子是平均路径：线虫是二点六五，同规模的随机网络是二点二五。",
    "n2b": "右边一组是聚集系数：线虫是零点二八，随机网络只有零点零五。",
    "n3": "【慢】对神经系统来说，高聚类让局部回路各司其职，短路径让信息几步就能传遍整个神经系统。",
    "n4": "不过，小世界模型里，每个节点的度，也就是连接数，都差不多，没有枢纽。真实网络还有另一个特征，下面就来看。",
    # power laws
    "t1": "下面进入第二部分。1999年前后，研究者在万维网、论文引用、演员合作网里，都看到了同一种度分布。",
    "t1b": "度分布，就是随机挑一个节点，它的度等于某个值的概率。",
    "t2": "先用普通坐标画。横轴是度，纵轴是概率。它是一个贴着纵轴的尖峰，加上一条几乎看不见的长尾巴。",
    "t3": "换成双对数坐标，也就是两条轴都按十倍、十倍地标刻度。这时候，它近似一条下倾的直线。",
    "t3b": "【慢】这种分布，叫幂律分布。公式左边，是度取某个值的概率；右边，是这个度的负若干次方。",
    "t3c": "这个次方叫度指数，常见在二到三之间。度指数越小，尾巴拖得越长。",
    "t4": "作为对比，灰色曲线是随机网络的泊松分布：在平均值附近有个峰，然后迅速掉下悬崖。",
    "t5": "在幂律网络里，随便抽一个节点，它的度可能是二，也可能是两千。没有一个典型的大小，所以叫无标度网络。",
    # BA
    "b0": "研究这类网络的物理学家里，有一位叫巴拉巴西。",
    "b1": "1999年，他和阿尔伯特提出了一个只有两个要素的模型，用来解释枢纽从哪里来。",
    "b2": "第一个要素是增长：网络不断加入新节点，每个新节点带着两条边。",
    "b3": "第二个要素是优先连接：新节点更愿意连向已经连接很多的节点。",
    "b3b": "右上角的公式说的就是这个：新节点连向某个节点的概率，等于这个节点的度，除以所有节点的度之和。度越大，被连上的机会越大。",
    "b4": "这就像被引用多的论文，更容易被看到、被继续引用。富者愈富。",
    "b5": "越早加入的节点，积累的连接越多。你看，最大的几个枢纽，正是最早到的那几个。",
    "b6": "在两万个节点的模型网络里统计度分布。双对数坐标上，是一条直线，斜率大约是负三。",
    "x1": "两个要素缺一不可。如果只有增长，新节点随机挑选连接对象，就会得到红色这些点。",
    "x2": "尾巴很快掉了下去，变成指数分布，枢纽消失了。",
    "b7": "知识页面里也有这个模型的演示。网络一个节点一个节点地长大；右边是双对数坐标下的度分布，红色的大节点是枢纽。",
    # duplication & fitness
    "gd1": "可是蛋白质并不会主动挑选热门伙伴。在生物网络里，优先连接可能来自基因复制。",
    "gd2": "一个基因被复制，新拷贝起初和原来一模一样，继承了全部的相互作用伙伴。",
    "gd3": "随后两个拷贝慢慢分化，新拷贝丢掉其中一部分相互作用。",
    "q4": "关键在于：度大的蛋白，邻居多；邻居被复制的机会也多，所以它更容易获得新边。",
    "q4b": "【慢】不需要任何全局信息，效果上就是优先连接。",
    "q5": "另一个扩展是适应度，也就是每个节点与生俱来的吸引力。公式里，连接的概率，正比于适应度乘以度。",
    "q6": "看这两条增长曲线，横轴是时间，纵轴是度。灰色节点早早加入；金色节点晚到，但适应度更高，最后反超了它。",
    # identification
    "c1": "最后是第三部分：怎样判断一张真实网络，是不是小世界、是不是无标度。",
    "c2": "小世界常用小世界系数。分子，是聚集系数比随机网络高出的倍数；分母，是路径比随机网络长出的倍数。",
    "c2b": "【慢】这个比值大于一，就算有小世界性。",
    "c3": "但零模型的选择会决定结论。零模型，就是拿来比较的随机网络。最好用保持每个节点度不变的随机网络：像这样交换两条边的端点，度不变，连法被打乱。",
    "c4": "判断幂律，最不可靠的做法，是在双对数直方图上拟合直线。左边这些红点，尾部计数太少，噪声极大。",
    "c5": "更好的做法，是画右边这种累积分布，再用最大似然估计和似然比检验，和其他分布比一比。",
    "c6": "2019年的一项研究，用这套严格标准，检验了近千个真实网络，发现严格意义上的无标度网络是少数。",
    "c7": "比较稳妥的说法是：重尾和枢纽普遍存在，但确切的分布形状和来源，需要逐个检验。",
    # recap
    "r1": "好，我们来总结一下。",
    "r2": "第一，少量随机捷径，就能让高度抱团的网络变成小世界。",
    "r3": "第二，增长加优先连接，会产生枢纽和长尾；基因复制，是它在生物学里的一种来源。",
    "r4": "第三，是不是小世界、是不是无标度，都要和合适的零模型比，并且用严格的统计检验。",
    "r5": "刚才的两个交互演示，都在这个专题的知识页面里，你可以自己动手试一试。",
}


def ring_pos(n, c, r, phase=PI / 2):
    return {i: c + r * np.array([np.cos(phase - 2 * PI * i / n), np.sin(phase - 2 * PI * i / n), 0]) for i in range(n)}


def ba_degrees(N, m, seed):
    return np.array([d for _, d in nx.barabasi_albert_graph(N, m, seed=seed).degree()])


def growth_uniform(N, m, seed):
    """Growth without preferential attachment (Barabási's model A)."""
    rng = np.random.default_rng(seed)
    k = np.zeros(N, int); k[: m + 1] = m
    for t in range(m + 1, N):
        tg = rng.choice(t, m, replace=False)
        k[tg] += 1; k[t] = m
    return k


def fitness_tracks(N=4000, m=2, late=100, seed=3, early=1):
    rng = np.random.default_rng(seed)
    eta = rng.uniform(0, 1, N); eta[late] = 1.0
    k = np.zeros(N); k[:3] = 2
    a, b, ts = [], [], []
    for t in range(3, N):
        w = eta[:t] * k[:t]
        tg = rng.choice(t, m, replace=False, p=w / w.sum())
        k[tg] += 1; k[t] = m
        ts.append(t); a.append(k[early]); b.append(k[late] if t >= late else np.nan)
    return np.array(ts), np.array(a), np.array(b), eta[early]


class Episode(Narrated):
    LINES = LINES

    def construct(self):
        self.hook()
        parts_slide(self, "这一期分三部分", ["一  小世界：高聚类与短路径", "二  无标度：长尾与枢纽从哪里来", "三  怎样判断一张真实网络"])
        self.extremes()
        self.ws()
        self.worm()
        self.powerlaw()
        self.ba()
        self.duplication()
        self.identify()
        self.recap()

    # ------------------------------------------------------------------ hook
    def hook(self):
        rng = np.random.default_rng(1)
        pts = [np.array([rng.uniform(-6.4, 6.4), rng.uniform(-3.2, 2.8), 0]) for _ in range(260)]
        crowd = VGroup(*[Dot(p, radius=0.045, color=MUTED).set_opacity(0.6) for p in pts])
        src = np.array([-5.4, -1.6, 0]); dst = np.array([5.4, 1.4, 0])
        a = Dot(src, radius=0.12, color=GOLD); b = Dot(dst, radius=0.12, color=RED)
        la = T("内布拉斯加", 24, GOLD).next_to(a, DOWN, buff=0.2)
        lb = T("波士顿", 24, RED).next_to(b, UP, buff=0.2)
        yr = T("1967", 30, MUTED).to_corner(UR, buff=0.5)
        with self.say("h0") as d:
            self.clip_on("yt_six_degrees_veritasium.mp4", "center", "视频：Veritasium · YouTube", start=60)
        self.clip_off()
        with self.say("h1") as d:
            self.play(FadeIn(crowd, lag_ratio=0.002), FadeIn(yr), run_time=1.4)
            self.play(FadeIn(a, scale=2), FadeIn(la), run_time=0.7)
            self.play(FadeIn(b, scale=2), FadeIn(lb), run_time=0.7)
        letter = VGroup(Rectangle(width=0.36, height=0.24, color=INK, fill_color=INK, fill_opacity=0.9, stroke_width=1),
                        Polygon([-0.18, 0.12, 0], [0, 0, 0], [0.18, 0.12, 0], color=BG, stroke_width=1.5)).move_to(src + UP * 0.3)
        hops = [src + (dst - src) * f + np.array([0, s, 0]) for f, s in ((0.18, 1.4), (0.36, -0.8), (0.52, 1.2), (0.68, -0.4), (0.85, 0.9))] + [dst]
        cnt = counter("转手", "0", GOLD, vs=40).move_to([-4.8, 2.4, 0])
        with self.say("h2") as d:
            self.play(FadeIn(letter), FadeIn(cnt), run_time=0.6)
            for i, h in enumerate(hops[:2]):
                self.play(letter.animate.move_to(h + UP * 0.3), Transform(cnt[1], T(str(i + 1), 40, GOLD, weight=BOLD).move_to(cnt[1])), run_time=0.6)
                self.add(Dot(h, radius=0.08, color=GOLD))
        trail = [src] + hops
        with self.say("h3") as d:
            for i, h in enumerate(hops[2:], start=2):
                self.play(letter.animate.move_to(h + UP * 0.3), Transform(cnt[1], T(str(i + 1), 40, GOLD, weight=BOLD).move_to(cnt[1])), run_time=0.5)
                if i < len(hops) - 1:
                    self.add(Dot(h, radius=0.08, color=GOLD))
            path = VMobject(color=GOLD, stroke_width=3).set_points_as_corners(trail)
            self.play(Create(path), run_time=1.0)
            six = T("六度分隔", 40, GOLD, weight=BOLD).move_to([0, -2.9, 0])
            self.play(FadeIn(six, shift=UP * 0.2), run_time=0.6)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)
        # tight friend circle
        G = nx.complete_graph(7); G.remove_edges_from([(1, 4), (2, 5), (3, 6), (2, 6)])
        pos = ring_pos(7, ORIGIN, 1.8)
        you = 0
        dots = {v: Dot(pos[v], radius=0.16, color=GOLD if v == you else BLUE) for v in G}
        eds = {e: Line(pos[e[0]], pos[e[1]], color=MUTED, stroke_width=2.5, stroke_opacity=0.6) for e in G.edges()}
        with self.say("h4") as d:
            self.play(*[GrowFromCenter(x) for x in dots.values()], *[Create(e) for e in eds.values()], run_time=1.2)
            tris = [Polygon(pos[0], pos[u], pos[v], stroke_width=0, fill_color=GREEN, fill_opacity=0.15)
                    for u, v in G.edges() if u and v and G.has_edge(0, u) and G.has_edge(0, v)]
            self.play(LaggedStart(*[FadeIn(t) for t in tris], lag_ratio=0.1), run_time=1.6)
            q = T("圈子抱团，路径照样很短", 40, GOLD, weight=BOLD).move_to([0, -3.0, 0])
            self.play(Write(q), run_time=1.0)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ lattice vs random
    def extremes(self):
        tag = self.chapter("第一部分 · 两个极端")
        n = 24
        L = nx.watts_strogatz_graph(n, 4, 0)
        R = nx.gnm_random_graph(n, L.number_of_edges(), seed=6)
        while not nx.is_connected(R):
            R = nx.gnm_random_graph(n, L.number_of_edges(), seed=random.Random(len(R.edges())).randint(0, 999))
        pl = ring_pos(n, np.array([-3.5, -0.3, 0]), 2.3)
        pr = ring_pos(n, np.array([3.5, -0.3, 0]), 2.3)
        vl = NetView(L, pl, color=BLUE, rmin=0.09, rk=0, ew=3, eo=0.7)
        vr = NetView(R, pr, color=VIOLET, rmin=0.09, rk=0, ew=2.2, eo=0.6)
        tl = T("规则网格", 28, BLUE).move_to([-3.5, 2.6, 0])
        tr = T("随机网络", 28, VIOLET).move_to([3.5, 2.6, 0])
        with self.say("l1") as d:
            self.play(FadeIn(tag), FadeIn(tl), *[GrowFromCenter(x) for x in vl.dots.values()], run_time=1.0)
            self.play(LaggedStart(*[Create(e) for e in vl.edges.values()], lag_ratio=0.03), run_time=d * 0.45)
        with self.say("l2") as d:
            tri = Polygon(pl[0], pl[1], pl[2], stroke_width=0, fill_color=GREEN, fill_opacity=0.35)
            self.play(FadeIn(tri), run_time=0.6)
        path = nx.shortest_path(L, 0, n // 2)
        assert len(path) - 1 == 6
        with self.say("l2b") as d:
            walker = Dot(pl[0], radius=0.14, color=GOLD)
            self.play(FadeIn(walker), run_time=0.3)
            for v in path[1:]:
                self.play(walker.animate.move_to(pl[v]), run_time=0.35)
            st = T(f"{len(path) - 1} 步", 28, GOLD).move_to([-3.5, -0.3, 0])
            self.play(FadeIn(st), run_time=0.5)
        with self.say("l3") as d:
            self.play(FadeIn(tr), FadeIn(vr.group), run_time=1.0)
            pr_path = nx.shortest_path(R, 0, n // 2)
            w2 = Dot(pr[0], radius=0.14, color=GOLD)
            self.play(FadeIn(w2), run_time=0.3)
            for v in pr_path[1:]:
                self.play(w2.animate.move_to(pr[v]), run_time=0.35)
            st2 = T(f"{len(pr_path) - 1} 步", 28, GOLD).move_to([3.5, -0.3, 0])
            self.play(FadeIn(st2), run_time=0.5)
        with self.say("l4") as d:
            self.play(*[FadeOut(m) for m in (vl.group, vr.group, walker, w2, st, st2, tri)], run_time=0.8)
            hdr = T("N = 1000，每个节点 10 条边", 26, MUTED).move_to([0, 1.7, 0])
            cl = VGroup(counter("平均路径", "≈ 50 步", BLUE), counter("聚集系数", "0.67", BLUE)).arrange(DOWN, buff=0.5).move_to([-3.5, -0.6, 0])
            cr = VGroup(counter("平均路径", "≈ 3 步", VIOLET), counter("聚集系数", "0.01", VIOLET)).arrange(DOWN, buff=0.5).move_to([3.5, -0.6, 0])
            self.play(FadeIn(hdr), run_time=0.5)
            self.play(FadeIn(cl[0]), FadeIn(cr[0]), run_time=0.9)
        with self.say("l4b") as d:
            self.play(FadeIn(cl[1]), FadeIn(cr[1]), run_time=0.9)
        with self.say("l5") as d:
            self.play(FadeOut(VGroup(hdr, cl, cr, tl, tr)), run_time=0.6)
            rows = [("演员合作", "0.79", "0.00027"), ("电网", "0.080", "0.005"), ("线虫神经", "0.28", "0.05")]
            tab = VGroup()
            head = VGroup(T("", 24), T("真实 C", 26, GOLD), T("随机 C", 26, MUTED))
            for r in [head] + [(T(a, 26, INK), T(b, 30, GOLD, weight=BOLD), T(c, 30, MUTED)) for a, b, c in rows]:
                tab.add(VGroup(*r))
            for i, row in enumerate(tab):
                for j, x in enumerate(row):
                    x.move_to([-3.2 + 3.4 * j, 1.2 - 1.0 * i, 0])
            yr = T("1998", 30, MUTED).move_to([0, 2.5, 0])
            self.play(FadeIn(yr), run_time=0.6)
            self.play(LaggedStart(*[FadeIn(r[0], shift=UP * 0.2) for r in tab[1:]], lag_ratio=0.4), run_time=1.6)
        with self.say("l5b") as d:
            self.play(FadeIn(tab[0]), *[FadeIn(r[1:]) for r in tab[1:]], run_time=1.2)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ WS
    def ws(self):
        tag = self.chapter("第一部分 · 小世界模型")
        n = 30
        G = nx.watts_strogatz_graph(n, 4, 0)
        c = np.array([-3.4, -0.3, 0])
        pos = ring_pos(n, c, 2.5)
        v = NetView(G, pos, color=BLUE, rmin=0.08, rk=0, ew=3, eo=0.7)
        Lc = counter("平均路径", f"{nx.average_shortest_path_length(G):.1f}", GOLD).move_to([3.4, 1.6, 0])
        Cc = counter("聚集系数", f"{nx.average_clustering(G):.2f}", GREEN).move_to([3.4, -0.9, 0])
        with self.say("w1") as d:
            self.play(FadeIn(tag), FadeIn(v.group), run_time=1.0)
            self.play(FadeIn(Lc), FadeIn(Cc), run_time=0.8)
        rewires = [((0, 1), 15), ((7, 8), 22), ((20, 21), 4)]
        H = G.copy()
        news = []
        with self.say("w2") as d:
            for (a, b), t in rewires:
                e = nv_edge(v, a, b)
                self.play(e.animate.set_color(RED).set_stroke(width=4, opacity=1), run_time=0.4)
                H.remove_edge(a, b); H.add_edge(a, t)
                ne = Line(pos[a], pos[t], color=GOLD, stroke_width=3.5)
                news.append(ne)
                self.play(Transform(e, ne), run_time=0.7)
        with self.say("w3") as d:
            self.play(Transform(Lc[1], T(f"{nx.average_shortest_path_length(H):.1f}", 40, GOLD, weight=BOLD).move_to(Lc[1])), run_time=1.0)
            self.play(*[Indicate(nv_edge(v, a, b), color=GOLD) for (a, b), _ in rewires], run_time=1.2)
        with self.say("w4") as d:
            self.play(Transform(Cc[1], T(f"{nx.average_clustering(H):.2f}", 40, GREEN, weight=BOLD).move_to(Cc[1])), run_time=1.0)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.6)
        # the classic curves
        ax = Axes(x_range=[-4, 0, 1], y_range=[0, 1, 0.5], x_length=9, y_length=4.6,
                  axis_config={"color": MUTED, "include_tip": False, "font_size": 24},
                  y_axis_config={"numbers_to_include": [0, 0.5, 1]}).shift(DOWN * 0.3)
        xt = VGroup(*[MathTex(r"10^{%d}" % e, font_size=26, color=MUTED).next_to(ax.c2p(e, 0), DOWN, buff=0.15) for e in range(-4, 1)])
        xl = T("重连概率（对数刻度）", 24, MUTED).next_to(xt, DOWN, buff=0.2)
        xs = np.log10(WS_B)
        cC = ax.plot_line_graph(xs, WS_C, line_color=GREEN, vertex_dot_radius=0.06, stroke_width=4)
        cL = ax.plot_line_graph(xs, WS_L, line_color=GOLD, vertex_dot_radius=0.06, stroke_width=4)
        lgC = T("聚集系数（相对值）", 24, GREEN).move_to(ax.c2p(-1.0, 1.12))
        lgL = T("平均路径（相对值）", 24, GOLD).move_to(ax.c2p(-3.2, 0.3))
        with self.say("w5") as d:
            self.play(Create(ax), FadeIn(xt), FadeIn(xl), run_time=1.2)
        with self.say("w6") as d:
            self.play(Create(cL), FadeIn(lgL), run_time=d * 0.35, rate_func=linear)
            self.play(Create(cC), FadeIn(lgC), run_time=d * 0.35, rate_func=linear)
            mk = DashedLine(ax.c2p(-2, 0), ax.c2p(-2, 1), color=INK, stroke_width=2)
            self.play(Create(mk), Indicate(cL["vertex_dots"][_i01], color=GOLD, scale_factor=2.5), run_time=0.8)
        with self.say("w7") as d:
            zone = Rectangle(width=ax.c2p(-1, 0)[0] - ax.c2p(-3, 0)[0], height=4.6, fill_color=BLUE, fill_opacity=0.15, stroke_width=0
                             ).move_to(ax.c2p(-2, 0.5))
            zl = T("小世界", 30, BLUE, weight=BOLD).move_to(ax.c2p(-2, 0.75))
            self.play(FadeIn(zone), FadeOut(mk), FadeIn(zl), run_time=1.0)
        with self.say("w8") as d:
            self.play(Indicate(cL, color=GOLD), run_time=1.0)
            self.play(Indicate(cC, color=GREEN), run_time=1.0)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)
        with self.say("w9") as d:
            self.clip_on("ws_demo.mp4", "full", "本站交互演示：Watts–Strogatz 重连", start=0.3)
            if d < 12.8:
                self.wait(12.9 - d)
        self.clip_off()

    # ------------------------------------------------------------------ C. elegans
    def worm(self):
        tag = self.chapter("第一部分 · 线虫的神经网络")
        body = VMobject(color=GREEN, stroke_width=4)
        xs = np.linspace(-5.5, 5.5, 80)
        top = [np.array([x, 0.25 * np.sin(x * 0.9) + 0.55 * np.sqrt(max(0, 1 - (x / 5.6) ** 2)), 0]) for x in xs]
        bot = [np.array([x, 0.25 * np.sin(x * 0.9) - 0.55 * np.sqrt(max(0, 1 - (x / 5.6) ** 2)), 0]) for x in xs[::-1]]
        body.set_points_smoothly(top + bot + [top[0]])
        body.shift(UP * 1.6)
        rng = np.random.default_rng(4)
        neu = VGroup()
        while len(neu) < 302:
            x = rng.uniform(-5.3, 5.3); h = 0.5 * np.sqrt(max(0, 1 - (x / 5.6) ** 2))
            y = 0.25 * np.sin(x * 0.9) + rng.uniform(-h, h)
            neu.add(Dot([x, y + 1.6, 0], radius=0.03, color=GOLD).set_opacity(0.85))
        cnt = counter("神经元", "302", GOLD).move_to([0, -0.2, 0])
        with self.say("n0") as d:
            self.clip_on("yt_celegans_mit.mp4", "center", "视频：Massachusetts Institute of Technology (MIT) · YouTube", start=0)
        self.clip_off()
        with self.say("n1") as d:
            self.play(FadeIn(tag), Create(body), run_time=1.2)
            self.play(LaggedStart(*[FadeIn(x) for x in neu], lag_ratio=0.004), FadeIn(cnt), run_time=d * 0.5)

        def pair(x, a, b, sc, title, la, lb):
            base = -3.3
            r1 = Rectangle(width=0.9, height=a * sc, fill_color=GOLD, fill_opacity=0.9, stroke_width=0).move_to([x - 0.6, base, 0], aligned_edge=DOWN)
            r2 = Rectangle(width=0.9, height=b * sc, fill_color=MUTED, fill_opacity=0.9, stroke_width=0).move_to([x + 0.6, base, 0], aligned_edge=DOWN)
            v1 = T(la, 24, GOLD, weight=BOLD).next_to(r1, UP, buff=0.1)
            v2 = T(lb, 24, MUTED, weight=BOLD).next_to(r2, UP, buff=0.1)
            t = T(title, 24, INK).move_to([x - 2.2, base + 0.9, 0])
            return VGroup(t, r1, r2, v1, v2)
        p1 = pair(-2.2, 2.65, 2.25, 0.5, "平均路径", "2.65", "2.25")
        p2 = pair(3.6, 0.28, 0.05, 5.0, "聚集系数", "0.28", "0.05")
        lg = VGroup(VGroup(Square(0.25, fill_color=GOLD, fill_opacity=0.9, stroke_width=0), T("线虫", 22, INK)).arrange(RIGHT, buff=0.12),
                    VGroup(Square(0.25, fill_color=MUTED, fill_opacity=0.9, stroke_width=0), T("随机网络", 22, INK)).arrange(RIGHT, buff=0.12)
                    ).arrange(RIGHT, buff=0.4).move_to([0.6, -0.4, 0])
        with self.say("n2") as d:
            self.play(FadeOut(cnt), FadeIn(lg), run_time=0.5)
            self.play(FadeIn(p1[0]), GrowFromEdge(p1[1], DOWN), GrowFromEdge(p1[2], DOWN), FadeIn(p1[3]), FadeIn(p1[4]), run_time=1.2)
        with self.say("n2b") as d:
            self.play(FadeIn(p2[0]), GrowFromEdge(p2[1], DOWN), GrowFromEdge(p2[2], DOWN), FadeIn(p2[3]), FadeIn(p2[4]), run_time=1.2)
        with self.say("n3") as d:
            self.play(Indicate(p2[1], color=GOLD), run_time=1.0)
            self.play(Indicate(p1[1], color=GOLD), run_time=1.0)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.6)
        Gw = nx.connected_watts_strogatz_graph(40, 4, 0.1, seed=3)
        pos = ring_pos(40, np.array([0, -0.2, 0]), 2.6)
        vw = NetView(Gw, pos, color=BLUE, rmin=0.06, rk=0.025, eo=0.5)
        with self.say("n4") as d:
            self.play(FadeIn(vw.group), run_time=1.0)
            self.play(LaggedStart(*[Indicate(x, color=GOLD, scale_factor=1.3) for x in list(vw.dots.values())[::3]], lag_ratio=0.05), run_time=1.6)
            qm = T("没有枢纽", 44, GOLD, weight=BOLD).move_to([0, -0.2, 0])
            self.play(FadeIn(qm), run_time=0.6)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ power laws
    def powerlaw(self):
        tag = self.chapter("第二部分 · 长尾与无标度")
        Gs = sf_graph(20000, 2.3, seed=7)
        Ks = np.array([d for _, d in Gs.degree()])
        km = Ks.mean()
        Ge = nx.gnm_random_graph(len(Ks), int(Ks.sum() / 2), seed=7)
        Ke = np.array([d for _, d in Ge.degree()])
        lbl = VGroup(*[T(s, 24, MUTED) for s in ("万维网", "论文引用", "演员合作")]).arrange(RIGHT, buff=0.8).move_to([0, 2.6, 0])
        # linear axes
        ax = Axes(x_range=[0, 60, 10], y_range=[0, 0.7, 0.1], x_length=8, y_length=4,
                  axis_config={"color": MUTED, "include_tip": False, "font_size": 22},
                  x_axis_config={"numbers_to_include": [0, 20, 40, 60]}, y_axis_config={"numbers_to_include": [0, 0.2, 0.4, 0.6]}).shift(DOWN * 0.6)
        vals, cnt = np.unique(Ks, return_counts=True)
        p = cnt / cnt.sum()
        sel = vals <= 60
        lin = ax.plot_line_graph(vals[sel], p[sel], line_color=BLUE, add_vertex_dots=False, stroke_width=4)
        with self.say("t1") as d:
            self.play(FadeIn(tag), LaggedStart(*[FadeIn(x, shift=DOWN * 0.2) for x in lbl], lag_ratio=0.3), run_time=1.4)
        with self.say("t1b") as d:
            self.play(Indicate(lbl, color=GOLD), run_time=1.0)
        xl0 = T("度", 22, MUTED).next_to(ax.x_axis, DOWN, buff=0.35)
        yl0 = T("概率", 22, MUTED).rotate(PI / 2).next_to(ax.y_axis, LEFT, buff=0.35)
        with self.say("t2") as d:
            self.play(Create(ax), FadeIn(xl0), FadeIn(yl0), run_time=0.8)
            self.play(Create(lin), run_time=1.4)
        self.play(FadeOut(VGroup(ax, lin, xl0, yl0)), run_time=0.5)
        grp, la = log_axes((0, 3), (-5, 0), xl=6.4, yl=4.4)
        grp.shift(DOWN * 0.6)
        xs, ys = logbin(Ks)
        pts = VGroup(*[Dot(la.c2p(x, y), radius=0.07, color=BLUE) for x, y in zip(xs, ys) if y > -5.2])
        xl = T("度", 22, MUTED).next_to(la.x_axis, DOWN, buff=0.6)
        yl = T("概率", 22, MUTED).rotate(PI / 2).next_to(la.y_axis, LEFT, buff=0.7)
        with self.say("t3") as d:
            self.play(FadeIn(grp), FadeIn(xl), FadeIn(yl), run_time=1.0)
            self.play(LaggedStart(*[FadeIn(x, scale=1.5) for x in pts], lag_ratio=0.1), run_time=1.6)
            sl = Line(la.c2p(xs[1], ys[1]) + (la.c2p(xs[1], ys[1]) - la.c2p(xs[-2], ys[-2])) * 0.12,
                      la.c2p(xs[-2], ys[-2]) - (la.c2p(xs[1], ys[1]) - la.c2p(xs[-2], ys[-2])) * 0.12, color=BLUE, stroke_width=2, stroke_opacity=0.6)
            self.play(Create(sl), run_time=0.8)
        fm = MathTex(r"P(k)", r"\sim", r"k^{-\gamma}", font_size=48, color=BLUE).move_to(la.c2p(2.2, -0.8))
        with self.say("t3b") as d:
            self.play(Write(fm), run_time=1.0)
            fa = T("度取某个值的概率", 22, INK).next_to(fm[0], DOWN, buff=0.45).shift(RIGHT * 0.5)
            fb = T("度的负若干次方", 22, INK).next_to(fm[2], UP, buff=0.35).shift(RIGHT * 0.4)
            self.play(FadeIn(fa, shift=UP * 0.1), run_time=0.6)
            self.play(FadeIn(fb, shift=DOWN * 0.1), run_time=0.6)
        with self.say("t3c") as d:
            self.play(Indicate(fm[2], color=GOLD, scale_factor=1.3), run_time=1.0)
            ns = MathTex(r"\gamma \approx 2\sim3", font_size=40, color=GOLD).next_to(fm, DOWN, buff=1.0)
            self.play(FadeIn(ns), FadeOut(fa), run_time=0.8)
        from math import lgamma
        ke = np.arange(1, 30)
        ppo = [(-km + k * np.log(km) - lgamma(k + 1)) / np.log(10) for k in ke]
        po = la.plot_line_graph(np.log10(ke)[np.array(ppo) > -5], np.array(ppo)[np.array(ppo) > -5], line_color=MUTED, add_vertex_dots=False, stroke_width=4)
        pol = T("泊松", 26, MUTED).move_to(la.c2p(1.45, -4.2))
        with self.say("t4") as d:
            self.play(Create(po), FadeIn(pol), run_time=d * 0.6)
        with self.say("t5") as d:
            hub = Dot(la.c2p(xs[-1], ys[-1]), radius=0.07, color=GOLD)
            self.play(Indicate(pts[-1], color=GOLD, scale_factor=2.5), Indicate(pts[0], color=GOLD, scale_factor=2.5), run_time=1.2)
            self.play(Indicate(ns, color=GOLD), run_time=0.8)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ BA
    def ba(self):
        tag = self.chapter("第二部分 · 优先连接")
        N, m = 70, 2
        G = nx.barabasi_albert_graph(N, m, seed=4)
        # reconstruct the arrival order: networkx adds node t with its m edges at step t
        pos = fit(nx.kamada_kawai_layout(G), (-6.4, 2.4, -3.3, 2.6))
        order_edges = {t: [e for e in G.edges(t) if e[1] < t] for t in range(N)}
        H = nx.Graph(); H.add_nodes_from(range(m + 1))
        for t in range(m + 1):
            for u, w in order_edges[t]:
                H.add_edge(t, w)
        dots = {v: Dot(pos[v], radius=0.07, color=BLUE) for v in G}
        lines = {}

        def rad(k):
            return 0.05 + 0.03 * np.sqrt(k)
        with self.say("b0") as d:
            self.clip_on("yt_bigthink_barabasi.mp4", "center", "视频：Big Think · YouTube", start=5)
        self.clip_off()
        with self.say("b1") as d:
            self.play(FadeIn(tag), run_time=0.6)
            q = T("两个要素：增长 + 优先连接", 40, GOLD, weight=BOLD).move_to([0, 0, 0])
            self.play(FadeIn(q), run_time=0.8)
            self.play(FadeOut(q), run_time=0.6)
            for v in range(m + 1):
                self.add(dots[v])
            for u, w in H.edges():
                lines[(u, w)] = Line(pos[u], pos[w], color=MUTED, stroke_width=1.5, stroke_opacity=0.6)
                self.add(lines[(u, w)])

        def add_node(t, rt):
            H.add_node(t)
            new = []
            for u, w in order_edges[t]:
                H.add_edge(t, w)
                lines[(t, w)] = Line(pos[t], pos[w], color=GOLD, stroke_width=2.5)
                new.append(lines[(t, w)])
            anims = [GrowFromCenter(dots[t])] + [Create(l) for l in new]
            anims += [dots[w].animate.set(width=2 * rad(H.degree(w))) for _, w in order_edges[t]]
            self.play(*anims, run_time=rt)
            self.play(*[l.animate.set_stroke(MUTED, width=1.5, opacity=0.6) for l in new], run_time=rt * 0.3)
        t = m + 1
        with self.say("b2") as d:
            for _ in range(4):
                add_node(t, 0.5); t += 1
        with self.say("b3") as d:
            for _ in range(5):
                add_node(t, 0.45); t += 1
        pf = MathTex(r"\Pi_i", r"=", r"{k_i", r"\over", r"\sum_j k_j}", font_size=50, color=GOLD).move_to([4.6, 1.6, 0])
        with self.say("b3b") as d:
            self.play(Write(pf), run_time=1.0)
            p1_ = T("连向它的概率", 20, INK).next_to(pf[0], DOWN, buff=0.5)
            p2_ = T("它的度", 20, INK).next_to(pf[2], RIGHT, buff=0.35)
            p3_ = T("所有节点的度之和", 20, INK).next_to(pf[4], DOWN, buff=0.3)
            self.play(FadeIn(p1_), run_time=0.5)
            self.play(FadeIn(p2_), run_time=0.5)
            self.play(FadeIn(p3_), run_time=0.5)
        self.play(FadeOut(VGroup(p1_, p2_, p3_)), run_time=0.4)
        with self.say("b4") as d:
            while t < 40:
                add_node(t, 0.18); t += 1
        with self.say("b5") as d:
            while t < N:
                add_node(t, 0.12); t += 1
            old = sorted(G, key=G.degree, reverse=True)[:3]
            self.play(*[Indicate(dots[v], color=GOLD, scale_factor=1.6) for v in old], run_time=1.0)
            ages = VGroup(*[T(f"第 {v + 1} 个", 22, GOLD).next_to(dots[v], UR, buff=0.05) for v in old])
            self.play(FadeIn(ages), run_time=0.6)
        self.play(*[FadeOut(m_) for m_ in self.mobjects if m_ is not tag], run_time=0.6)
        grp, la = log_axes((0, 3), (-6, 0), xl=6.6, yl=4.6)
        grp.shift(DOWN * 0.5)
        xl = T("度", 22, MUTED).next_to(la.x_axis, DOWN, buff=0.6)
        K = ba_degrees(20000, 2, seed=1)
        xs, ys = logbin(K)
        pts = VGroup(*[Dot(la.c2p(x, y), radius=0.07, color=BLUE) for x, y in zip(xs, ys) if y > -6.2])
        slope, icpt = np.polyfit(xs[1:-2], ys[1:-2], 1)
        x0, x1 = 0.2, 2.6
        ref = DashedLine(la.c2p(x0, icpt + slope * x0), la.c2p(x1, icpt + slope * x1), color=GOLD, stroke_width=3)
        rl = T(f"斜率 ≈ {slope:.1f}", 30, GOLD).move_to(la.c2p(2.3, -1.3))
        assert -3.4 < slope < -2.6, slope
        lg = VGroup(Dot(radius=0.07, color=BLUE), T("增长 + 优先连接", 24, BLUE)).arrange(RIGHT, buff=0.15).move_to(la.c2p(2.3, -0.3))
        with self.say("b6") as d:
            self.play(FadeIn(grp), FadeIn(xl), run_time=1.0)
            self.play(LaggedStart(*[FadeIn(p, scale=1.5) for p in pts], lag_ratio=0.1), FadeIn(lg), run_time=1.6)
            self.play(Create(ref), FadeIn(rl), run_time=1.0)
        KA = growth_uniform(20000, 2, seed=1)
        xa, ya = logbin(KA, nb=24)
        pa = VGroup(*[Dot(la.c2p(x, y), radius=0.07, color=RED) for x, y in zip(xa, ya) if y > -6.2])
        lgA = VGroup(Dot(radius=0.07, color=RED), T("只有增长", 24, RED)).arrange(RIGHT, buff=0.15).next_to(lg, DOWN, buff=0.25, aligned_edge=LEFT)
        with self.say("x1") as d:
            self.play(FadeOut(rl), FadeIn(lgA), run_time=0.8)
        with self.say("x2") as d:
            self.play(LaggedStart(*[FadeIn(p, scale=1.5) for p in pa], lag_ratio=0.1), run_time=1.6)
            self.play(Indicate(pa[-1], color=RED, scale_factor=2), run_time=0.8)
        self.play(*[FadeOut(m_) for m_ in self.mobjects], run_time=0.8)
        with self.say("b7") as d:
            self.clip_on("ba_demo.mp4", "full", "本站交互演示：BA 优先连接", start=0.3)
            if d < 12.8:
                self.wait(12.9 - d)
        self.clip_off()

    # ------------------------------------------------------------------ duplication & fitness
    def duplication(self):
        tag = self.chapter("第二部分 · 基因复制与适应度")
        G = nx.Graph([(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (1, 2), (3, 6), (4, 7), (5, 8), (6, 9), (2, 10), (8, 11), (6, 7)])
        pos = fit(nx.kamada_kawai_layout(G), (-5.6, 0.4, -2.8, 2.4))
        v = NetView(G, pos, color=GREEN, rmin=0.11, rk=0.02, eo=0.55)
        with self.say("gd1") as d:
            self.play(FadeIn(tag), FadeIn(v.group), run_time=1.2)
        x = 6
        nbrs = list(G.neighbors(x))
        px = pos[x] + np.array([0.9, -0.6, 0])
        copy = Dot(px, radius=0.11 + 0.02 * np.sqrt(len(nbrs)), color=GOLD)
        inh = {w: Line(px, pos[w], color=GOLD, stroke_width=3) for w in nbrs}
        with self.say("gd2") as d:
            self.play(Indicate(v.dots[x], color=GOLD, scale_factor=1.6), run_time=0.8)
            self.play(TransformFromCopy(v.dots[x], copy), run_time=0.8)
            self.play(LaggedStart(*[Create(l) for l in inh.values()], lag_ratio=0.3), run_time=1.2)
        lost = nbrs[:2]
        with self.say("gd3") as d:
            self.play(*[inh[w].animate.set_color(RED) for w in lost], run_time=0.6)
            self.play(*[FadeOut(inh[w]) for w in lost], run_time=0.8)
            self.play(*[inh[w].animate.set_color(MUTED).set_stroke(width=2) for w in nbrs if w not in lost], run_time=0.5)
        hub = 0
        with self.say("q4") as d:
            self.play(v.dots[hub].animate.set_color(BLUE).scale(1.3), run_time=0.6)
            hn = list(G.neighbors(hub))
            self.play(LaggedStart(*[Indicate(v.dots[w], color=GOLD, scale_factor=1.6) for w in hn], lag_ratio=0.15), run_time=1.4)
            w = 4
            pw = pos[w] + np.array([0.0, 0.85, 0])
            c2 = Dot(pw, radius=0.12, color=GOLD)
            e2 = Line(pw, pos[hub], color=BLUE, stroke_width=4)
            self.play(TransformFromCopy(v.dots[w], c2), run_time=0.7)
            self.play(Create(e2), v.dots[hub].animate.scale(1.2), run_time=0.8)
            k = counter("枢纽的度", f"{G.degree(hub)} → {G.degree(hub) + 1}", BLUE).move_to([4.2, 1.0, 0])
            self.play(FadeIn(k), run_time=0.6)
        with self.say("q4b") as d:
            pa_ = T("= 优先连接", 34, GOLD, weight=BOLD).next_to(k, DOWN, buff=0.5)
            self.play(FadeIn(pa_), run_time=0.8)
        self.play(*[FadeOut(m_) for m_ in self.mobjects if m_ is not tag], run_time=0.6)
        ts, a, b, eta_e = fitness_tracks()
        assert b[-1] > a[-1]
        ymax = float(np.ceil(max(np.nanmax(a), np.nanmax(b)) / 10) * 10)
        ax = Axes(x_range=[0, 4000, 1000], y_range=[0, ymax, 10], x_length=8.5, y_length=4.4,
                  axis_config={"color": MUTED, "include_tip": False, "font_size": 22},
                  y_axis_config={"numbers_to_include": list(range(0, int(ymax) + 1, 10))}).shift(DOWN * 0.4)
        xl = T("时间（加入的节点数）", 22, MUTED).next_to(ax.x_axis, DOWN, buff=0.3)
        yl = T("度", 22, MUTED).next_to(ax.y_axis, UP, buff=0.15)
        sel = np.arange(0, len(ts), 20)
        ca = ax.plot_line_graph(ts[sel], a[sel], line_color=MUTED, add_vertex_dots=False, stroke_width=4)
        okb = sel[~np.isnan(b[sel])]
        cb = ax.plot_line_graph(ts[okb], b[okb], line_color=GOLD, add_vertex_dots=False, stroke_width=4)
        with self.say("q5") as d:
            fm = MathTex(r"\Pi_i \propto", r"\eta_i", r"\, k_i", font_size=50, color=GOLD).move_to([-1.0, 2.8, 0])
            self.play(Write(fm), run_time=1.0)
            fl_ = VGroup(T("适应度", 22, INK).next_to(fm[1], DOWN, buff=0.15), T("度", 22, INK).next_to(fm[2], DOWN, buff=0.15))
            fl_[1].align_to(fl_[0], DOWN).shift(RIGHT * 0.15)
            self.play(FadeIn(fl_[0]), Indicate(fm[1]), run_time=0.6)
            self.play(FadeIn(fl_[1]), Indicate(fm[2]), run_time=0.6)
            self.play(Create(ax), FadeIn(xl), FadeIn(yl), run_time=1.0)
        with self.say("q6") as d:
            self.play(Create(ca), run_time=d * 0.3, rate_func=linear)
            self.play(Create(cb), run_time=d * 0.35, rate_func=linear)
            la_ = T("早到", 24, MUTED).next_to(ax.c2p(ts[-1], a[-1]), RIGHT, buff=0.15)
            lb_ = T("晚到、适应度高", 24, GOLD).next_to(ax.c2p(ts[-1], b[-1]), UP, buff=0.15).shift(LEFT * 0.8)
            self.play(FadeIn(la_), FadeIn(lb_), run_time=0.6)
        self.play(*[FadeOut(m_) for m_ in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ identification
    def identify(self):
        tag = self.chapter("第三部分 · 怎样判断")
        with self.say("c1") as d:
            q = VGroup(T("是不是小世界", 40, BLUE, weight=BOLD), T("是不是无标度", 40, GOLD, weight=BOLD)).arrange(RIGHT, buff=1.6)
            self.play(FadeIn(tag), FadeIn(q, shift=UP * 0.2), run_time=1.0)
        sig = MathTex(r"\sigma=\frac{C/C_{\mathrm{rand}}}{L/L_{\mathrm{rand}}}", r">1", font_size=60, color=INK)
        sig[0].set_color(BLUE)
        with self.say("c2") as d:
            self.play(FadeOut(q), run_time=0.5)
            self.play(Write(sig[0]), run_time=1.4)
            s1_ = T("聚集系数高出的倍数", 22, INK).next_to(sig[0], UR, buff=0.1).shift(LEFT * 0.5)
            s2_ = T("路径长出的倍数", 22, INK).next_to(sig[0], DR, buff=0.1).shift(LEFT * 0.5)
            self.play(FadeIn(s1_), run_time=0.5)
            self.play(FadeIn(s2_), run_time=0.5)
        with self.say("c2b") as d:
            self.play(Write(sig[1]), run_time=0.8)
        self.play(FadeOut(s1_), FadeOut(s2_), run_time=0.4)
        with self.say("c3") as d:
            self.play(sig.animate.shift(UP * 1.4), run_time=0.6)
            # degree-preserving double edge swap
            P = {0: [-2.4, -0.4], 1: [-0.8, -0.4], 2: [-2.4, -1.9], 3: [-0.8, -1.9]}
            P = {k: np.array([*v, 0]) for k, v in P.items()}
            ds = VGroup(*[Dot(p, radius=0.13, color=BLUE) for p in P.values()])
            e1 = Line(P[0], P[1], color=INK, stroke_width=4); e2 = Line(P[2], P[3], color=INK, stroke_width=4)
            ar = Arrow(LEFT * 0.4, RIGHT * 0.4, color=MUTED).move_to([0.6, -1.15, 0])
            Q = {k: p + RIGHT * 4.0 for k, p in P.items()}
            ds2 = VGroup(*[Dot(p, radius=0.13, color=BLUE) for p in Q.values()])
            f1 = Line(Q[0], Q[3], color=GOLD, stroke_width=4); f2 = Line(Q[2], Q[1], color=GOLD, stroke_width=4)
            lab = T("保持每个节点的度", 26, MUTED).move_to([0.6, -2.8, 0])
            self.play(FadeIn(ds), Create(e1), Create(e2), run_time=0.8)
            self.play(GrowArrow(ar), FadeIn(ds2), Create(f1), Create(f2), FadeIn(lab), run_time=1.2)
        self.play(*[FadeOut(m_) for m_ in self.mobjects if m_ is not tag], run_time=0.6)
        # noisy histogram vs CCDF
        Gs = sf_graph(3000, 2.5, seed=3)
        K = np.array([d_ for _, d_ in Gs.degree()])
        vals, cnt = np.unique(K, return_counts=True)
        gl, la = log_axes((0, 2), (-4, 0), xl=4.6, yl=3.6, fs=22)
        gl.move_to([-3.4, -0.6, 0])
        hist = VGroup(*[Dot(la.c2p(np.log10(k), np.log10(c / len(K))), radius=0.06, color=RED) for k, c in zip(vals, cnt) if k <= 100])
        gr, lb = log_axes((0, 2), (-4, 0), xl=4.6, yl=3.6, fs=22)
        gr.move_to([3.6, -0.6, 0])
        cc = np.array([(K >= k).mean() for k in vals])
        ccdf = VGroup(*[Dot(lb.c2p(np.log10(k), np.log10(c)), radius=0.06, color=GREEN) for k, c in zip(vals, cc) if k <= 100 and c >= 1e-4])
        t1 = T("直方图", 26, RED).next_to(gl, UP, buff=0.3)
        t2 = T("累积分布", 26, GREEN).next_to(gr, UP, buff=0.3)
        with self.say("c4") as d:
            self.play(FadeIn(gl), FadeIn(t1), run_time=0.8)
            self.play(LaggedStart(*[FadeIn(p) for p in hist], lag_ratio=0.02), run_time=1.4)
            tail = SurroundingRectangle(VGroup(*[p for p in hist if p.get_center()[0] > la.c2p(1.2, 0)[0]]), color=RED, buff=0.1)
            self.play(Create(tail), run_time=0.8)
        with self.say("c5") as d:
            self.play(FadeIn(gr), FadeIn(t2), run_time=0.8)
            self.play(LaggedStart(*[FadeIn(p) for p in ccdf], lag_ratio=0.02), run_time=1.4)
            mle = T("最大似然 + 似然比检验", 26, GREEN).move_to([3.6, -3.4, 0])
            self.play(FadeIn(mle), run_time=0.6)
        self.play(*[FadeOut(m_) for m_ in self.mobjects if m_ is not tag], run_time=0.6)
        grid = VGroup(*[Square(0.13, stroke_width=0, fill_color=MUTED, fill_opacity=0.7) for _ in range(40 * 24)]).arrange_in_grid(24, 40, buff=0.05)
        grid.move_to(DOWN * 0.2)
        hdr = T("近千个真实网络", 30, INK).next_to(grid, UP, buff=0.3)
        yr = T("2019", 28, MUTED).to_corner(UR, buff=0.5)
        with self.say("c6") as d:
            self.play(FadeIn(yr), FadeIn(hdr), FadeIn(grid, lag_ratio=0.001), run_time=1.6)
        with self.say("c7") as d:
            self.play(grid.animate.set_opacity(0.15), run_time=0.6)
            a1 = T("重尾、有枢纽：普遍", 34, GOLD, weight=BOLD).move_to(UP * 0.5)
            a2 = T("确切形状与来源：逐个检验", 34, INK).move_to(DOWN * 0.6)
            self.play(FadeIn(a1, shift=UP * 0.2), run_time=0.8)
            self.play(FadeIn(a2, shift=UP * 0.2), run_time=0.8)
        self.play(*[FadeOut(m_) for m_ in self.mobjects], run_time=0.8)

    # ------------------------------------------------------------------ recap
    def recap(self):
        items = [("r2", BLUE, "少量捷径 → 小世界"),
                 ("r3", GOLD, "增长 + 优先连接 → 枢纽与长尾"),
                 ("r4", GREEN, "和零模型比，用严格的统计检验")]
        head, rows = recap_rows(items)
        with self.say("r1") as d:
            self.play(Write(head), run_time=0.8)
        for (k, _, _), row in zip(items, rows):
            with self.say(k) as d:
                self.play(FadeIn(row, shift=RIGHT * 0.3), run_time=0.8)
        with self.say("r5") as d:
            self.play(rows.animate.set_opacity(0.4), run_time=0.6)
            ring_ = None
            G = nx.watts_strogatz_graph(24, 4, 0)
            pos = ring_pos(24, np.array([0, -2.75, 0]), 0.85)
            v = NetView(G, pos, color=BLUE, rmin=0.04, rk=0, ew=1.0, eo=0.6)
            self.play(FadeIn(v.group), run_time=0.6)
            e = nv_edge(v, 0, 1)
            self.play(Transform(e, Line(pos[0], pos[12], color=GOLD, stroke_width=2)), run_time=0.8)
            e = nv_edge(v, 6, 7)
            self.play(Transform(e, Line(pos[6], pos[18], color=GOLD, stroke_width=2)), run_time=0.8)
        self.wait(1.0)
        self.play(*[FadeOut(m_) for m_ in self.mobjects], run_time=1.0)
