"""Paper explainer: Barabási & Albert 1999, emergence of scaling (preferential attachment)."""
import networkx as nx
import numpy as np
from scipy import stats

from paperhelp import *  # noqa: F401,F403

TITLE = "无标度网络：枢纽从哪里来"
LINES = {
    # hook
    "h1": "先说一个词：度。一个节点的度，就是它有几条连接。左边这张图，横轴是度，纵轴是有这个度的节点占多少。",
    "h1b": "这是一张连线全靠随机撒上去的网络。你看，每个节点的度都差不多，挤在平均值六附近。",
    "h2": "按这个分布，出现一个度是平均值十倍的节点，概率小到几乎为零。",
    "h3": "可是上世纪九十年代末，人们第一次拿到万维网、演员合作网这样的大网络。里面到处是这样的枢纽，就是右边这些大点。",
    "h3b": "万维网，就是我们每天浏览的网页，靠超链接连在一起。它从九十年代起飞速长大。",
    "h4": "【慢】这些枢纽从哪里来，1999年《科学》杂志上的一篇论文，给出了一个简单得惊人的答案。",
    "q0": "这一期分三部分来讲。",
    "q1": "第一部分，真实网络的长尾分布，也就是幂律。",
    "q2": "第二部分，产生幂律的机制：增长加优先连接，以及两个对照实验。",
    "q3": "第三部分，回到生物网络，再说说这篇论文受到的质疑。",
    # long tail
    "o1": "先看第一部分，长尾是怎么被发现的。这张图横轴是度，纵轴是概率。在普通坐标里，这种分布几乎贴着横轴，尾巴根本看不清。",
    "o2": "把两个坐标轴都取对数，这些点就近似排成了一条直线。",
    "o3": "【慢】双对数坐标下的直线，意味着一种叫幂律的分布，写出来是这样。",
    "o3b": "左边的P(k)，是一个节点的度等于k的概率。右边是k的负伽马次方，伽马叫幂律指数。伽马越大，直线越陡，枢纽越少。",
    "o4": "右边这几条线，是作者测到的指数。演员合作网的伽马约为二点三，万维网的入度约为二点一，论文引用网络约为三。",
    "o5": "规模较小的美国西部电网，近似为四。所以指数大致落在二点一到四之间。",
    # two ingredients
    "g1": "下面进入第二部分。作者指出，之前的模型都忽略了真实网络的两个共同特点。",
    "g2": "第一是增长：网络不断有新节点加入，就像新演员、新网页、新论文。黄色的点，就是刚加进来的。",
    "g3": "第二是优先连接：新节点更愿意连向那些已经连接很多的节点。",
    "g4": "连到某个节点的概率，写出来就是这个式子。",
    "g4b": "分子是这个节点的度，分母是全网所有节点的度加起来。也就是说，度越大，被连上的机会越大。",
    "g5": "就像抽奖。下面这根彩条，每一段代表一个节点，段越长，它手里的奖券越多。",
    "g6": "让网络这样一步一步长大，枢纽就自己冒了出来。",
    "d1": "本站的知识页面里，有这个过程的交互演示。按下自动生长，网络不断加入新节点，红色的大点是枢纽。",
    "d2": "下面这张小图，是双对数坐标下的度分布。网络越长越大，这些点也越来越接近一条直线。",
    # rich get richer
    "r1": "我们在一张长到两万个节点的网络里，跟踪三个节点：第五个、第五十个、第五百个加入的节点，看它们的度怎么变化。",
    "r2": "横轴是时间，纵轴是度，都取了对数。你看，三条线都近似平行于这条虚线，斜率是二分之一。也就是说，度随时间的平方根增长。",
    "r3": "【慢】越早加入的节点，起跑越早，度就越大。这就是富者愈富。",
    "r4": "把度当作连续变量，可以写出平均场方程，解出来正好是平方根。",
    "r4b": "第一行说，一个节点的度增长得有多快，和它现在的度成正比，和时间成反比。第二行是解：t_i是它加入的时刻，加入越早，t_i越小，度越大。",
    "r5": "再假设节点在时间上均匀加入，就推出了第三行的度分布。",
    "r5b": "【慢】它和k的三次方成反比，所以指数伽马等于三。注意，这个三和m无关，m是每个新节点带来的边数。",
    # reproduce
    "p1": "我们来验证一下。让网络长到两万个节点，每个新节点带三条边，画出度分布。",
    "p2": "双对数坐标下，度分布果然是一条直线。拟合出的斜率，接近负三。",
    "p3": "再换一张五千个节点的网络，蓝色方块和黄色圆点几乎重合，分布形状不随网络规模改变。原文模拟得到的指数是二点九。",
    # both needed
    "a1": "两个要素是不是缺一不可，作者做了两个对照实验来检验。",
    "a2": "第一个对照只保留增长，新节点均匀随机地连接。你看绿色的点，在双对数坐标里很快弯了下去。这是指数分布，没有长尾。",
    "a3": "第二个对照只保留优先连接：节点数固定不变，只往里加边。",
    "a4": "边越加越多，富者愈富撑不了多久。最后所有节点两两相连，变成了完全图。",
    "a5": "作者还发现，如果连接概率不是和度成正比，而是和度的某个幂次成正比，只有幂次恰好为一，才会出现标度律。",
    # biology
    "b1": "最后是第三部分，回到生物网络。蛋白质相互作用网络里，也有少数和大量伙伴结合的枢纽蛋白。",
    "b1b": "画面里是一个常用的蛋白质相互作用数据库。研究者输入一个蛋白质，就能看到它和哪些蛋白质相连。",
    "b2": "但能产生长尾的机制不止一种。对蛋白质网络来说，基因复制再分化，是另一种解释。",
    "b3": "一个基因复制之后，新拷贝继承了原来的相互作用，就是黄色的虚线。随后在演化中，丢掉其中一部分。",
    "b4": "本文提出的枢纽概念，直接引出了后来关于网络鲁棒性和蛋白质致死性的研究。",
    # limits
    "l1": "再说质疑。原文的指数，是在双对数图上画直线拟合出来的。今天看来，统计上不够严格。",
    "l2": "比如这组紫色的点，其实来自对数正态分布，不是幂律。可在一段范围里，它看起来也挺像一条直线。",
    "l3": "2009年，有研究提出了最大似然估计加拟合优度检验的流程。2019年用它检验了近千个网络，发现严格的无标度网络是少数。",
    "l4": "模型本身也过于简化。它只能给出等于三的指数；聚集系数随着网络变大趋于零，就是右边这条绿线；它也解释不了后来者居上。",
    "l5": "【慢】所以要区分重尾和严格幂律。能产生幂律，也不等于真实网络就是这样生成的。",
    # recap
    "z1": "好，我们来总结一下。",
    "z2": "第一，许多真实网络的度分布有长尾，少数枢纽连接极多。",
    "z3": "第二，增长加优先连接，就能长出幂律，指数等于三，两个要素缺一不可。",
    "z4": "第三，严格幂律需要认真检验，重尾和无标度不是一回事。",
}


def grow_ba(N, m, seed, uniform=False, track=(), times=()):
    """Growth with preferential (or uniform) attachment. Returns degree array, edge list, and tracked degree histories."""
    rng = np.random.default_rng(seed)
    deg = np.zeros(N, int)
    edges = []
    rep = []
    for u in range(m + 1):
        for v in range(u):
            edges.append((u, v)); deg[u] += 1; deg[v] += 1; rep += [u, v]
    hist = {i: [] for i in track}
    times = set(times)
    for t in range(m + 1, N):
        tg = set()
        while len(tg) < m:
            tg.add(int(rng.integers(t)) if uniform else rep[int(rng.integers(len(rep)))])
        for v in tg:
            edges.append((t, v)); deg[t] += 1; deg[v] += 1; rep += [t, v]
        if t in times:
            for i in track:
                hist[i].append((t, deg[i]))
    return deg, edges, hist


class Episode(Narrated):
    LINES = LINES

    def construct(self):
        self.hook()
        parts(self, "q0", ["q1", "q2", "q3"], "这一期分三部分",
              ["一  长尾：真实网络的幂律", "二  增长 + 优先连接", "三  生物网络与质疑"])
        self.tail()
        self.ingredients()
        self.rich()
        self.reproduce()
        self.controls()
        self.biology()
        self.limits()
        recap(self, "z1", [("z2", BLUE, "真实网络：长尾与枢纽"),
                           ("z3", GOLD, "增长 + 优先连接 → γ = 3"),
                           ("z4", RED, "重尾 ≠ 严格幂律")])

    # ------------------------------------------------------------------ hook
    def hook(self):
        N, kbar = 2000, 6
        Ge = nx.gnm_random_graph(N, N * kbar // 2, seed=1)
        deg = np.array([d for _, d in Ge.degree()])
        ax = plain_axes([0, 70, 10], [0, 0.2, 0.1], 7.0, 3.6, xnums=[0, 10, 20, 30, 40, 50, 60, 70], ynums=[0.1, 0.2]).shift(LEFT * 2.6 + DOWN * 0.6)
        xl = xlabel("度 k（连接数）", ax)
        yl = ylabel("比例", ax)
        bars = VGroup()
        for k in range(0, 20):
            f = (deg == k).mean()
            if f > 0:
                bars.add(Rectangle(width=ax.x_length / 70 * 0.85, height=ax.y_length * f / 0.2, fill_color=BLUE, fill_opacity=0.85,
                                   stroke_width=0).move_to(ax.c2p(k, 0), aligned_edge=DOWN))
        with self.say("h1"):
            self.play(Create(ax), FadeIn(xl), FadeIn(yl), run_time=1.0)
        with self.say("h1b"):
            self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.08), run_time=2.0)
            mk = DashedLine(ax.c2p(kbar, 0), ax.c2p(kbar, 0.19), color=GOLD)
            avg = T("平均 6", 22, GOLD).next_to(mk, UP, buff=0.05)
            self.play(Create(mk), FadeIn(avg), run_time=0.8)
        p = stats.poisson.sf(59, kbar)
        ex = int(np.floor(np.log10(p)))
        with self.say("h2"):
            arr = Arrow(ax.c2p(60, 0.12), ax.c2p(60, 0.005), color=RED, buff=0)
            lab = MathTex(rf"P(k\ge 60)\approx 10^{{{ex}}}", font_size=36, color=RED).next_to(arr, UP, buff=0.1)
            self.play(GrowArrow(arr), Write(lab), run_time=1.2)
        G = nx.barabasi_albert_graph(160, 2, seed=3)
        pos = fit(nx.kamada_kawai_layout(G), (1.6, 6.6, -3.0, 2.6))
        net = NetView(G, pos, color=GOLD, rmin=0.035, rk=0.03, ew=1.0, eo=0.35)
        with self.say("h3"):
            self.play(VGroup(ax, xl, yl, bars, mk, avg, arr, lab).animate.scale(0.7).to_edge(LEFT, buff=0.4), run_time=0.8)
            self.play(FadeIn(net.group), run_time=1.4)
            hubs = sorted(G, key=G.degree, reverse=True)[:4]
            self.play(*[Indicate(net.dots[h], color=RED, scale_factor=1.6) for h in hubs], run_time=1.4)
        keep = list(self.mobjects)
        self.play(*[FadeOut(m) for m in keep], run_time=0.5)
        with self.say("h3b"):
            self.clip_on("yt_www_history_cern.mp4", "center", "视频：CERN · YouTube", start=40)
        self.clip_off()
        self.play(*[FadeIn(m) for m in keep], run_time=0.5)
        with self.say("h4"):
            q = T("枢纽从哪里来", 40, RED, weight=BOLD).move_to(RIGHT * 4.1 + DOWN * 0.2)
            self.play(net.group.animate.set_opacity(0.2), FadeIn(q, scale=0.5), run_time=1.0)
        clear(self)

    # ------------------------------------------------------------------ long tail
    def tail(self):
        tag = self.chapter("一  长尾与幂律")
        deg, _, _ = grow_ba(20000, 3, seed=7)
        lx, ly = logbin(deg, 16)
        ax1 = plain_axes([0, 300, 100], [0, 0.12, 0.06], 8.0, 4.6, xnums=[0, 100, 200, 300], ynums=[0, 0.06, 0.12]).shift(DOWN * 0.3)
        xl1 = xlabel("度 k", ax1)
        yl1 = ylabel("P(k)", ax1)
        pts_lin = VGroup(*[Dot(ax1.c2p(min(10 ** x, 299), 10 ** y), radius=0.07, color=BLUE) for x, y in zip(lx, ly)])
        with self.say("o1"):
            self.play(FadeIn(tag), Create(ax1), FadeIn(xl1), FadeIn(yl1), run_time=1.2)
            self.play(LaggedStart(*[FadeIn(d, scale=0.5) for d in pts_lin], lag_ratio=0.1), run_time=1.6)
            zoom = Ellipse(width=6.6, height=0.6, color=RED).move_to(ax1.c2p(165, 0.002))
            self.play(Create(zoom), run_time=0.8)
        ax2 = log_axes([0, 3], [-7, 0], 6.4, 4.6).shift(LEFT * 1.6 + DOWN * 0.3)
        xt = log_labels(ax2, "x", [0, 1, 2, 3])
        yt = log_labels(ax2, "y", [-6, -4, -2, 0])
        xl2 = xlabel("度 k（对数）", ax2, buff=0.7)
        yl2 = ylabel("P(k)（对数）", ax2, buff=0.9)
        pts_log = VGroup(*[Dot(ax2.P(x, y), radius=0.07, color=BLUE) for x, y in zip(lx, ly)])
        with self.say("o2"):
            self.play(FadeOut(zoom), run_time=0.4)
            self.play(ReplacementTransform(ax1, ax2), ReplacementTransform(xl1, xl2), ReplacementTransform(yl1, yl2),
                      ReplacementTransform(pts_lin, pts_log), FadeIn(xt), FadeIn(yt), run_time=2.0)
            sl, ic = np.polyfit(lx[2:-2], ly[2:-2], 1)
            fitl = DashedLine(ax2.P(0.3, sl * 0.3 + ic), ax2.P(2.8, sl * 2.8 + ic), color=GOLD)
            self.play(Create(fitl), run_time=1.0)
        with self.say("o3"):
            f = MathTex(r"P(k)", r"\sim", r"k^{-\gamma}", font_size=54, color=GOLD).move_to(RIGHT * 4.3 + UP * 2.0)
            self.play(Write(f), run_time=1.4)
        with self.say("o3b"):
            la = T("度为 k 的概率", 22, BLUE).next_to(f[0], DOWN, buff=0.5).shift(LEFT * 0.8)
            lb = T("γ：幂律指数", 22, RED).next_to(f[2], DOWN, buff=0.5).shift(RIGHT * 0.4)
            aa = Arrow(la.get_top(), f[0].get_bottom(), buff=0.08, color=BLUE, stroke_width=3)
            ab = Arrow(lb.get_top(), f[2].get_bottom(), buff=0.08, color=RED, stroke_width=3)
            self.play(FadeIn(la), GrowArrow(aa), run_time=0.6)
            self.wait(1.2)
            self.play(FadeIn(lb), GrowArrow(ab), run_time=0.6)
        self.play(FadeOut(VGroup(la, lb, aa, ab)), run_time=0.4)
        # exponents of real networks as slopes in a small inset
        data = [("万维网（入度）", 2.1, BLUE), ("演员合作网", 2.3, GREEN), ("引文网络", 3.0, VIOLET), ("西部电网", 4.0, MUTED)]
        ax3 = log_axes([0, 1], [-4, 0], 2.4, 3.2).move_to(RIGHT * 1.0 + DOWN * 1.0)
        rows = VGroup()
        lines = VGroup()
        for name, g, c in data:
            lines.add(Line(ax3.P(0, 0), ax3.P(1, -g), color=c, stroke_width=4))
            rows.add(VGroup(Line(ORIGIN, RIGHT * 0.4, color=c, stroke_width=5), T(name, 20, INK),
                            MathTex(rf"\gamma\approx{g:g}", font_size=30, color=c)).arrange(RIGHT, buff=0.15))
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.18).next_to(ax3, RIGHT, buff=0.25)
        with self.say("o4"):
            self.play(VGroup(ax2, xt, yt, xl2, yl2, pts_log, fitl).animate.scale(0.7).to_edge(LEFT, buff=0.3), run_time=0.8)
            self.play(Create(ax3), run_time=0.6)
            for i in range(3):
                self.play(Create(lines[i]), FadeIn(rows[i]), run_time=0.9)
        with self.say("o5"):
            self.play(Create(lines[3]), FadeIn(rows[3]), run_time=0.9)
        clear(self)

    # ------------------------------------------------------------------ ingredients
    def ingredients(self):
        tag = self.chapter("二  增长与优先连接")
        N, m = 46, 2
        rng = np.random.default_rng(4)
        deg = np.zeros(N, int)
        G = nx.complete_graph(3)
        deg[:3] = 2
        steps = []
        for t in range(3, N):
            p = deg[:t] / deg[:t].sum()
            tg = rng.choice(t, size=m, replace=False, p=p)
            steps.append((t, [int(x) for x in tg]))
            for v in tg:
                G.add_edge(t, int(v)); deg[v] += 1
            deg[t] = m
        pos = fit(nx.kamada_kawai_layout(G), (-6.4, -0.4, -3.2, 2.8))
        rad = lambda k: 0.05 + 0.03 * np.sqrt(k)
        dots, lines = {}, []
        cur = {v: 2 for v in range(3)}
        for v in range(3):
            dots[v] = Dot(pos[v], radius=rad(2), color=BLUE)
        init = [Line(pos[u], pos[v], stroke_width=1.6, color=BLUE, stroke_opacity=0.5) for u, v in [(0, 1), (1, 2), (0, 2)]]

        def add(i, rt):
            t, tg = steps[i]
            d = Dot(pos[t], radius=rad(m), color=GOLD)
            ls = [Line(pos[t], pos[v], stroke_width=1.6, color=GOLD, stroke_opacity=0.9) for v in tg]
            self.play(FadeIn(d, scale=1.6), *[Create(l) for l in ls], run_time=rt * 0.6)
            for v in tg:
                cur[v] += 1
            cur[t] = m
            self.play(d.animate.set_color(BLUE), *[l.animate.set_stroke(BLUE, opacity=0.5) for l in ls],
                      *[dots[v].animate.scale_to_fit_width(2 * rad(cur[v])) for v in tg], run_time=rt * 0.4)
            dots[t] = d
        with self.say("g1"):
            self.play(FadeIn(tag), *[GrowFromCenter(d) for d in dots.values()], *[Create(l) for l in init], run_time=1.2)
        with self.say("g2") as dd:
            n2 = 5
            for i in range(n2):
                add(i, dd * 0.8 / n2)
        with self.say("g3") as dd:
            n3 = 4
            for i in range(n2, n2 + n3):
                add(i, dd * 0.8 / n3)
        done = n2 + n3
        # lottery bar with current degrees
        nodes = sorted(cur, key=lambda v: -cur[v])
        tot = sum(cur.values())
        W = 5.4
        segs = VGroup()
        x = 0
        cols = [RED, GOLD, GREEN, VIOLET, BLUE]
        for j, v in enumerate(nodes):
            w = W * cur[v] / tot
            segs.add(Rectangle(width=w, height=0.6, fill_color=cols[j % 5], fill_opacity=0.85, stroke_color=BG, stroke_width=1.5)
                     .move_to([3.6 - W / 2 + x + w / 2, -0.6, 0]))
            x += w
        with self.say("g4"):
            f = MathTex(r"\Pi(k_i)=\frac{k_i}{\sum_j k_j}", font_size=50).move_to(RIGHT * 3.6 + UP * 1.6)
            self.play(Write(f), run_time=1.4)
            self.play(LaggedStart(*[FadeIn(s) for s in segs], lag_ratio=0.05), run_time=1.2)
            top = nodes[0]
            br = Brace(segs[0], DOWN, color=RED)
            bl = T("度最大的节点", 20, RED).next_to(br, DOWN, buff=0.1)
            link = DashedLine(dots[top].get_center(), segs[0].get_top(), color=RED, stroke_width=2)
        with self.say("g4b"):
            num = T("分子：这个节点的度", 22, GOLD)
            den = T("分母：全网度的总和", 22, MUTED)
            VGroup(num, den).arrange(RIGHT, buff=0.5).next_to(f, DOWN, buff=0.35)
            self.play(FadeIn(num), run_time=0.5)
            self.play(FadeIn(den), run_time=0.5)
            self.play(GrowFromCenter(br), FadeIn(bl), Create(link), run_time=0.8)
        with self.say("g5"):
            ptr = Triangle(color=INK, fill_opacity=1).scale(0.14).rotate(PI).next_to(segs, UP, buff=0.05).align_to(segs, LEFT)
            self.play(FadeIn(ptr), run_time=0.3)
            for xx in (0.85, 0.15, 0.35, 0.05):
                self.play(ptr.animate.set_x(3.6 - W / 2 + W * xx), run_time=0.45)
        with self.say("g6") as dd:
            self.play(FadeOut(VGroup(f, segs, br, bl, link, ptr, num, den)), run_time=0.5)
            rest = list(range(done, len(steps)))
            for i in rest:
                add(i, max(0.12, (dd * 0.85 - 0.5) / len(rest)))
            hubs = sorted(cur, key=lambda v: -cur[v])[:3]
            self.play(*[Indicate(dots[h], color=RED, scale_factor=1.5) for h in hubs], run_time=0.8)
        clip_lines(self, "ba_demo.mp4", ["d1", "d2"], "本站交互演示：BA 优先连接", start=0.5, box="full")

    # ------------------------------------------------------------------ rich get richer
    def rich(self):
        tag = self.chapter("二  富者愈富")
        times = np.unique(np.logspace(1, np.log10(19999), 40).astype(int))
        track = (5, 50, 500)
        _, _, hist = grow_ba(20000, 2, seed=11, track=track, times=times)
        ax = log_axes([1, 4.4], [0, 2.8], 6.4, 4.6).shift(LEFT * 3.0 + DOWN * 0.4)
        xt = log_labels(ax, "x", [1, 2, 3, 4])
        yt = log_labels(ax, "y", [0, 1, 2])
        xl = xlabel("时间 t（对数）", ax, buff=0.7)
        yl = ylabel("度 k（对数）", ax, buff=0.8)
        cols = [RED, GOLD, BLUE]
        curves, labs = VGroup(), VGroup()
        for (i, c) in zip(track, cols):
            h = [(np.log10(t), np.log10(k)) for t, k in hist[i] if t > i]
            curves.add(pline(ax, [a for a, _ in h], [b for _, b in h], c, 4))
            labs.add(T(f"第 {i} 个加入", 22, c).next_to(ax.P(*h[-1]), RIGHT, buff=0.1))
        with self.say("r1"):
            self.play(FadeIn(tag), Create(ax), FadeIn(xt), FadeIn(yt), FadeIn(xl), FadeIn(yl), run_time=1.2)
            for c, l in zip(curves, labs):
                self.play(Create(c), FadeIn(l), run_time=1.0, rate_func=linear)
        with self.say("r2"):
            ref = DashedLine(ax.P(1.2, 0.2), ax.P(4.2, 1.7), color=INK, stroke_width=3)
            rl = T("斜率 1/2", 24, INK).next_to(ax.P(2.6, 0.9), DR, buff=0.05)
            self.play(Create(ref), FadeIn(rl), run_time=1.2)
        with self.say("r3"):
            self.play(Indicate(labs[0], color=RED), Indicate(curves[0], color=RED), run_time=1.4)
        with self.say("r4"):
            f1 = MathTex(r"\frac{\partial k_i}{\partial t}=\frac{k_i}{2t}", font_size=44).move_to(RIGHT * 4.7 + UP * 1.9)
            f2 = MathTex(r"k_i(t)=m\left(\frac{t}{t_i}\right)^{1/2}", font_size=44, color=GOLD).next_to(f1, DOWN, buff=0.5)
            self.play(Write(f1), run_time=1.2)
            self.play(Write(f2), run_time=1.2)
        with self.say("r4b"):
            sr = SurroundingRectangle(f1, color=BLUE, buff=0.1)
            self.play(Create(sr), run_time=0.6)
            self.wait(2.0)
            self.play(sr.animate.become(SurroundingRectangle(f2, color=GOLD, buff=0.1)), run_time=0.6)
        self.play(FadeOut(sr), run_time=0.3)
        with self.say("r5"):
            f3 = MathTex(r"P(k)=\frac{2m^2}{k^3}", font_size=50, color=RED).next_to(f2, DOWN, buff=0.5)
            g = MathTex(r"\gamma=3", font_size=44, color=RED).next_to(f3, DOWN, buff=0.35)
            self.play(Write(f3), run_time=1.4)
        with self.say("r5b"):
            self.play(FadeIn(g), Indicate(f3, color=RED), run_time=1.0)
        clear(self)

    # ------------------------------------------------------------------ reproduce
    def reproduce(self):
        tag = self.chapter("二  亲手复现")
        d1, _, _ = grow_ba(20000, 3, seed=2)
        d2, _, _ = grow_ba(5000, 3, seed=3)
        x1, y1 = logbin(d1, 16)
        x2, y2 = logbin(d2, 14)
        sel = (x1 > np.log10(5)) & (x1 < np.log10(d1.max()) - 0.3)
        sl, ic = np.polyfit(x1[sel], y1[sel], 1)
        print(f"[ba] fitted slope {sl:.2f}")
        self.ba_pts = (x1, y1)
        ax = log_axes([0, 3], [-7, 0], 7.6, 5.0).shift(LEFT * 1.0 + DOWN * 0.3)
        xt = log_labels(ax, "x", [0, 1, 2, 3])
        yt = log_labels(ax, "y", [-6, -4, -2, 0])
        xl = xlabel("度 k", ax, buff=0.7)
        yl = ylabel("P(k)", ax, buff=0.9)
        p1 = VGroup(*[Dot(ax.P(x, y), radius=0.08, color=GOLD) for x, y in zip(x1, y1)])
        p2 = VGroup(*[Square(0.14, color=BLUE, stroke_width=3).move_to(ax.P(x, y)) for x, y in zip(x2, y2)])
        with self.say("p1"):
            self.play(FadeIn(tag), Create(ax), FadeIn(xt), FadeIn(yt), FadeIn(xl), FadeIn(yl), run_time=1.2)
            cap = T("N = 20000，m = 3", 26, GOLD).to_corner(UR, buff=0.6).shift(DOWN * 0.4)
            self.play(FadeIn(cap), LaggedStart(*[FadeIn(d, scale=0.5) for d in p1], lag_ratio=0.1), run_time=1.8)
        with self.say("p2"):
            fl = DashedLine(ax.P(0.4, sl * 0.4 + ic), ax.P(2.9, sl * 2.9 + ic), color=RED)
            st = T(f"斜率 ≈ {sl:.1f}", 28, RED).next_to(cap, DOWN, buff=0.4)
            self.play(Create(fl), Write(st), run_time=1.4)
        with self.say("p3"):
            cap2 = T("N = 5000", 26, BLUE).next_to(st, DOWN, buff=0.4)
            self.play(FadeIn(cap2), LaggedStart(*[FadeIn(d) for d in p2], lag_ratio=0.1), run_time=1.6)
            orig = VGroup(T("原文", 24, MUTED), MathTex(r"\gamma=2.9\pm0.1", font_size=36)).arrange(RIGHT, buff=0.2).next_to(cap2, DOWN, buff=0.5)
            self.play(FadeIn(orig), run_time=0.8)
        self.repro_axes = ax
        clear(self)

    # ------------------------------------------------------------------ controls
    def controls(self):
        tag = self.chapter("二  缺一不可")
        x1, y1 = self.ba_pts
        dA, _, _ = grow_ba(20000, 3, seed=5, uniform=True)
        xa, ya = logbin(dA, 16)
        ax = log_axes([0, 3], [-7, 0], 6.6, 4.6).shift(LEFT * 2.6 + DOWN * 0.4)
        xt = log_labels(ax, "x", [0, 1, 2, 3])
        yt = log_labels(ax, "y", [-6, -4, -2, 0])
        xl = xlabel("度 k", ax, buff=0.7)
        pB = VGroup(*[Dot(ax.P(x, y), radius=0.07, color=GOLD) for x, y in zip(x1, y1)])
        pA = VGroup(*[Dot(ax.P(x, y), radius=0.08, color=GREEN) for x, y in zip(xa, ya) if y > -7])
        lg = legend([(GOLD, "增长 + 优先连接"), (GREEN, "模型 A：只增长")]).next_to(ax, RIGHT, buff=0.3).shift(UP * 1.4)
        with self.say("a1"):
            self.play(FadeIn(tag), Create(ax), FadeIn(xt), FadeIn(yt), FadeIn(xl), run_time=1.2)
            self.play(FadeIn(pB), FadeIn(lg[0]), run_time=0.8)
        with self.say("a2"):
            self.play(LaggedStart(*[FadeIn(d, scale=0.5) for d in pA], lag_ratio=0.12), FadeIn(lg[1]), run_time=2.0)
            curve = VMobject(color=GREEN, stroke_width=3).set_points_smoothly([d.get_center() for d in pA])
            self.play(Create(curve), run_time=1.0)
        clear(self, keep=[tag])
        # model B: fixed nodes, preferential edges until complete
        n = 14
        pos = ring_pos(n, 2.6, DOWN * 0.3)
        dots = {v: Dot(pos[v], radius=0.12, color=VIOLET) for v in range(n)}
        rng = np.random.default_rng(2)
        G = nx.empty_graph(n)
        order = []
        while G.number_of_edges() < n * (n - 1) // 2:
            u = int(rng.integers(n))
            k = np.array([G.degree(v) + 1 for v in range(n)], float); k[u] = 0
            v = int(rng.choice(n, p=k / k.sum()))
            if not G.has_edge(u, v):
                G.add_edge(u, v); order.append((u, v))
        tot = len(order)
        cnt = counter("边数", f"0 / {tot}", VIOLET).to_corner(UR, buff=0.6).shift(DOWN * 0.4)
        lb = T("模型 B：节点固定，只加边", 26, VIOLET).to_edge(DOWN, buff=0.35)
        with self.say("a3"):
            self.play(*[GrowFromCenter(d) for d in dots.values()], FadeIn(lb), FadeIn(cnt), run_time=1.2)
            first = order[:20]
            self.play(LaggedStart(*[Create(Line(pos[u], pos[v], color=VIOLET, stroke_width=1.5, stroke_opacity=0.6)) for u, v in first], lag_ratio=0.1),
                      Transform(cnt, counter("边数", f"20 / {tot}", VIOLET).move_to(cnt)), run_time=1.6)
        with self.say("a4") as d:
            chunks = np.array_split(np.arange(20, tot), 5)
            done = 20
            for ch in chunks:
                done += len(ch)
                self.play(*[Create(Line(pos[order[i][0]], pos[order[i][1]], color=VIOLET, stroke_width=1.5, stroke_opacity=0.6)) for i in ch],
                          Transform(cnt, counter("边数", f"{done} / {tot}", VIOLET).move_to(cnt)), run_time=d * 0.75 / 5)
            full = T("完全图", 30, RED, weight=BOLD).next_to(cnt, DOWN, buff=0.3)
            self.play(FadeIn(full), run_time=0.5)
        clear(self, keep=[tag])
        with self.say("a5"):
            f = MathTex(r"\Pi(k)\sim k^{\alpha}", font_size=60).shift(UP * 1.0)
            self.play(Write(f), run_time=1.0)
            nl = NumberLine(x_range=[0, 2, 0.5], length=7, color=MUTED, include_numbers=True, font_size=28).shift(DOWN * 1.2)
            al = MathTex(r"\alpha", font_size=36, color=MUTED).next_to(nl, RIGHT, buff=0.3)
            self.play(Create(nl), FadeIn(al), run_time=0.8)
            mk = Dot(nl.n2p(1), radius=0.14, color=GOLD)
            ml = T("只有这里出现标度律", 24, GOLD).next_to(mk, UP, buff=0.3)
            self.play(FadeIn(mk, scale=2), FadeIn(ml), run_time=0.8)
        clear(self)

    # ------------------------------------------------------------------ biology
    def biology(self):
        tag = self.chapter("三  回到生物网络")
        G = sf_graph(80, 2.3, seed=31, kmax=18)
        net = NetView(G, fit(nx.kamada_kawai_layout(G), (-6.4, -0.8, -2.9, 2.6)), color=GREEN, eo=0.4)
        with self.say("b1"):
            self.play(FadeIn(tag), FadeIn(net.group), run_time=1.4)
            hubs = sorted(G, key=G.degree, reverse=True)[:3]
            self.play(*[Indicate(net.dots[h], color=GOLD, scale_factor=1.6) for h in hubs], run_time=1.2)
        # duplication-divergence on the right
        c = np.array([3.4, -0.2, 0])
        a = c + LEFT * 0.7
        nb = [c + 2.0 * np.array([np.cos(t), np.sin(t), 0]) for t in np.linspace(0.6 * PI, 1.9 * PI, 5)]
        nb = [p + RIGHT * 0.4 for p in nb]
        A = Dot(a, radius=0.16, color=GREEN)
        Ns = VGroup(*[Dot(p, radius=0.11, color=MUTED) for p in nb])
        Es = VGroup(*[Line(a, p, color=GREEN, stroke_width=2.5) for p in nb])
        keep = list(self.mobjects)
        self.play(*[FadeOut(m) for m in keep], run_time=0.5)
        with self.say("b1b"):
            self.clip_on("yt_string_ppi_jensen.mp4", "center", "视频：Lars Juhl Jensen · YouTube", start=60)
        self.clip_off()
        self.play(*[FadeIn(m) for m in keep], run_time=0.5)
        with self.say("b2"):
            self.play(net.group.animate.set_opacity(0.3), run_time=0.5)
            self.play(FadeIn(A), FadeIn(Ns), Create(Es), run_time=1.2)
        b = a + RIGHT * 1.4 + UP * 0.9
        with self.say("b3"):
            B = A.copy()
            self.play(B.animate.move_to(b).set_color(GOLD), run_time=0.9)
            Eb = VGroup(*[DashedLine(b, p, color=GOLD, stroke_width=2.5) for p in nb])
            self.play(Create(Eb), run_time=0.9)
            self.play(FadeOut(Eb[1]), FadeOut(Eb[3]), FadeOut(Eb[4]), run_time=0.9)
        with self.say("b4"):
            self.play(FadeOut(VGroup(A, B, Ns, Es, Eb[0], Eb[2])), net.group.animate.set_opacity(1), run_time=0.8)
            hubs = sorted(G, key=G.degree, reverse=True)[:3]
            rings = VGroup(*[Circle(radius=0.3, color=RED, stroke_width=3).move_to(net.dots[h]) for h in hubs])
            self.play(Create(rings), run_time=0.8)
            arrs = VGroup(T("鲁棒性", 30, GOLD), T("致死性", 30, RED)).arrange(DOWN, buff=0.7).move_to(RIGHT * 3.6)
            ar = VGroup(*[Arrow(RIGHT * 0.2, x.get_left() + LEFT * 0.1, color=MUTED, buff=0.1) for x in arrs])
            self.play(FadeIn(arrs), *[GrowArrow(x) for x in ar], run_time=1.0)
        clear(self)

    # ------------------------------------------------------------------ limits
    def limits(self):
        tag = self.chapter("三  局限与争议")
        rng = np.random.default_rng(1)
        s = np.ceil(rng.lognormal(1.2, 1.1, 20000)).astype(int)
        lx, ly = logbin(s, 16)
        ax = log_axes([0, 3], [-7, 0], 6.6, 4.6).shift(LEFT * 2.6 + DOWN * 0.4)
        xt = log_labels(ax, "x", [0, 1, 2, 3])
        yt = log_labels(ax, "y", [-6, -4, -2, 0])
        xl = xlabel("k", ax, buff=0.7)
        pts = VGroup(*[Dot(ax.P(x, y), radius=0.08, color=VIOLET) for x, y in zip(lx, ly) if y > -7])
        with self.say("l1"):
            self.play(FadeIn(tag), Create(ax), FadeIn(xt), FadeIn(yt), FadeIn(xl), run_time=1.2)
            self.play(LaggedStart(*[FadeIn(d, scale=0.5) for d in pts], lag_ratio=0.1), run_time=1.4)
        with self.say("l2"):
            sel = (lx > 0.9) & (lx < 2.2)
            sl, ic = np.polyfit(lx[sel], ly[sel], 1)
            fl = DashedLine(ax.P(0.8, sl * 0.8 + ic), ax.P(2.4, sl * 2.4 + ic), color=GOLD)
            self.play(Create(fl), run_time=1.0)
            tl = T("对数正态", 28, VIOLET, weight=BOLD).next_to(ax, RIGHT, buff=0.4).shift(UP * 1.6)
            self.play(FadeIn(tl), run_time=0.6)
        with self.say("l3"):
            tline = NumberLine(x_range=[2008, 2020, 1], length=5.2, color=MUTED).move_to(RIGHT * 3.9 + DOWN * 0.2)
            m1 = VGroup(Dot(tline.n2p(2009), color=GOLD), T("2009", 22, GOLD).next_to(tline.n2p(2009), DOWN, buff=0.2),
                        T("最大似然 + 拟合优度", 20, GOLD).next_to(tline.n2p(2009), UP, buff=0.25).shift(RIGHT * 0.6))
            m2 = VGroup(Dot(tline.n2p(2019), color=RED), T("2019", 22, RED).next_to(tline.n2p(2019), DOWN, buff=0.2),
                        T("近千个网络：严格无标度是少数", 20, RED).next_to(tline.n2p(2019), DOWN, buff=0.7).shift(LEFT * 1.4))
            self.play(Create(tline), run_time=0.6)
            self.play(FadeIn(m1), run_time=0.8)
            self.wait(1.5)
            self.play(FadeIn(m2), run_time=0.8)
        clear(self, keep=[tag])
        Ns = [100, 300, 1000, 3000, 10000]
        Cs = [nx.average_clustering(nx.barabasi_albert_graph(n, 3, seed=1)) for n in Ns]
        ax2 = log_axes([2, 4], [0, 0.2], 5.4, 3.4).move_to(RIGHT * 2.6 + DOWN * 0.6)
        xt2 = log_labels(ax2, "x", [2, 3, 4])
        xl2 = xlabel("网络规模 N", ax2, buff=0.7)
        yl2 = ylabel("聚集系数", ax2)
        cc = VGroup(pline(ax2, np.log10(Ns), Cs, GREEN, 4), *[Dot(ax2.P(x, y), radius=0.07, color=GREEN) for x, y in zip(np.log10(Ns), Cs)])
        yt2 = VGroup(*[MathTex(f"{v:g}", font_size=28, color=MUTED).next_to(ax2.P(2, v), LEFT, buff=0.15) for v in (0, 0.1, 0.2)])
        g3 = MathTex(r"\gamma \equiv 3", font_size=60, color=GOLD).move_to(LEFT * 4.2 + UP * 0.6)
        late = T("解释不了后来者居上", 28, RED).next_to(g3, DOWN, buff=0.8)
        with self.say("l4"):
            self.play(Write(g3), run_time=0.8)
            self.play(Create(ax2), FadeIn(xt2), FadeIn(yt2), FadeIn(xl2), FadeIn(yl2), Create(cc), run_time=1.6)
            self.play(FadeIn(late), run_time=0.6)
        with self.say("l5"):
            self.play(FadeOut(VGroup(g3, late, ax2, xt2, yt2, xl2, yl2, cc)), run_time=0.6)
            big = VGroup(T("重尾", 56, BLUE, weight=BOLD), MathTex(r"\neq", font_size=80), T("严格幂律", 56, GOLD, weight=BOLD)).arrange(RIGHT, buff=0.5)
            self.play(FadeIn(big, shift=UP * 0.3), run_time=1.0)
        clear(self)
