"""Paper explainer: Watts & Strogatz 1998, small-world networks."""
import networkx as nx
import numpy as np

from paperhelp import *  # noqa: F401,F403

TITLE = "小世界：几条捷径如何让世界变小"
LINES = {
    # hook
    "h1": "设想一群人围坐成一圈。每个点是一个人，每条线表示两个人互相认识。每个人，只认识左右最近的几个人。",
    "h2": "现在，要把一条消息从顶上这个人，传到正对面。只能一个接一个地转手——黄色这条路，要走八步。",
    "h3": "好，我们只把其中三条关系，随机改接到远处，就是这三条红线。",
    "h4": "同样这两个人，现在传话只要三步了。",
    "h5": "可是每个人身边的小圈子，几乎没变。右边这个数叫聚集系数，后面会细讲，它只从零点五降到了零点四六。",
    "h6": "【慢】改动这么少，世界却一下子变小了。1998年，《自然》杂志上一篇只有三页的论文，把这件事讲清楚了。",
    "h7": "其实，人们很早就注意到世界很小。社会学里有个说法，叫六度分隔：任意两个人之间，往往只隔着几个熟人。",
    "q0": "这一期分三部分来讲。",
    "q1": "第一部分，两个极端，以及连接它们的随机重连模型。",
    "q2": "第二部分，小世界的核心结果——两条曲线，和它背后的道理。",
    "q3": "第三部分，真实网络、传播和同步，最后说说这项研究的局限。",
    # two extremes
    "e1": "先看第一部分。在1998年以前，研究网络上的动力学，人们手里只有两种连接方式。",
    "e2": "左边是第一种，规则网格。每个点只连着身边最近的几个点。邻居的邻居往往也是邻居，所以有很多三角形，就是这些蓝色的小三角。",
    "e2b": "可是要从一头走到另一头，得走很多步，就像这条黄色的路。",
    "e3": "右边是第二种，随机图，连线是随便撒上去的。你看，任意两点几步就能走到，可三角形几乎没有。",
    "e4": "我们用两个数来衡量。第一个叫聚集系数，写作大写的C。意思是，你的两个朋友，彼此也是朋友的可能性有多大。",
    "e4b": "第二个叫特征路径长度，写作大写的L，就是任意两个点之间，平均要走几步。你看，网格的C高，L也长；随机图正好反过来。",
    "e5": "【慢】真实网络，很可能落在这两个极端之间。这篇论文要做的，就是把这片中间地带量出来。",
    # rewiring model
    "w1": "两位作者的办法很简单。从环形网格出发，顺着圆圈，依次检查每一条边。",
    "w2": "每检查一条边，就以一个概率p，把它的一端改接到随机选出的节点上。p叫作重连概率。黄色的线，就是改接出来的捷径。",
    "w3": "p等于零，什么都不改，还是原来的网格。p等于一，每条边都改接，就接近随机图。",
    "w4": "真正有意思的，是中间这一大片地带，也就是p很小、但又不为零的时候。",
    # curves
    "c1": "下面进入第二部分。我们在场景里，重做原文的实验：一千个节点，每个节点连十个邻居。",
    "c2": "先看坐标。横轴是重连概率p，取了对数，从万分之一一直到一。纵轴是L和C，都除以了p等于零时的值，所以都从一开始。",
    "c3": "先看黄色的点，它是路径长度。重连概率才千分之一，它就已经明显往下掉了。",
    "c4": "【慢】到了百分之一，路径长度只剩原来的不到五分之一。",
    "c5": "再看绿色的点，它是聚集系数。这时候，它还保留着百分之九十七。",
    "c6": "中间这一段，路径已经很短，聚类还很高。这就是小世界。",
    "c7": "原文给小世界下的判据，写成式子就是这两句。",
    "c7b": "第一句说，路径长度L，和同样大小的随机图差不多。第二句说，聚集系数C，远远大于随机图。两个条件要同时满足。",
    "d1": "本站的知识页面里，有这个实验的交互演示。滑块往右拖，重连概率变大，圆圈里的捷径越来越多。",
    "d2": "下面这张图里，红色的路径曲线先掉下去，蓝色的聚类曲线很久才跟着下降。这和刚才的实验是一致的。",
    # mechanism
    "m1": "两条曲线差这么多，原因在捷径上。我们只加一条捷径来看。",
    "m1b": "节点的颜色，表示它离顶上这个节点有几步远。蓝色近，红色远。",
    "m2": "现在加一条捷径，从顶上直接连到正对面。你看，对面一整片都变成了蓝色，很多节点之间的距离，一下子缩短了。",
    "m3": "而对聚集系数来说，改掉一条边，只拆掉了附近这几个三角形。",
    "m4": "【慢】也就是说，一条捷径对全局距离影响很大，对局部聚类影响很小。所以p很小时，L已经骤降，C却几乎不动。",
    # real networks
    "r1": "最后是第三部分。作者检查了三张真实网络：电影演员合作网、美国西部电网，还有秀丽隐杆线虫的神经网络。",
    "r2": "上面一行是路径长度。彩色柱子是真实网络，灰色柱子是同样规模的随机图。你看，每一对都差不多高。",
    "r3": "下面一行是聚集系数。真实网络都高出许多，演员网甚至高出了将近三千倍。",
    "r4": "秀丽隐杆线虫是一种很小的线虫，它的神经连接，被研究者一条一条地画了出来。画面里就是这种线虫。",
    "r4b": "回到表格。线虫只有二百八十二个神经元。聚集系数是零点二八，同样规模的随机图，只有零点零五。",
    "r5": "作者特别强调，这三张网络，并不是挑出来的。",
    # spreading
    "s1": "接着看这种结构对传播的影响。两张网上各放一个感染源，每一步，感染都传给所有邻居。",
    "s2": "左边是规则网格。感染像水波一样，一圈一圈慢慢往外推。",
    "s3": "右边只多了四条捷径。感染顺着捷径跳到远处，很快就多点开花。下面的数字，是传到全网用了几步。",
    "s4": "原文发现，传遍全体需要的时间，和路径长度的曲线几乎是同一个形状。黄色是路径长度，红色是传遍全体的步数，两条线几乎贴在一起。",
    "s5": "【慢】对传染病来说，这意味着：少量远距离的接触，就足以让疫情迅速扩散。",
    "s5b": "作者还发现，小世界连接下的振子，几乎和全连接一样容易同步。振子，可以想成一群各自打拍子的节拍器。",
    "s6": "后来，大量研究报告，人脑的结构网络和功能网络，也具有小世界性。",
    # limits
    "l1": "下面说说局限。第一，这个模型里，节点的连接数都挤在平均值附近。蓝色柱子就是它的分布，没有枢纽。",
    "l2": "而真实网络里，常有连接极多的枢纽，就像黄色这条长尾巴。第二年的增长与优先连接模型，补上了这一块。",
    "l3": "第二，原文的判断是定性的。后来，人们定义了小世界系数，就是这个式子。",
    "l3b": "分子是聚集系数比随机图高出多少倍，分母是路径长度比随机图长出多少倍。大于一，就算小世界。但它依赖零模型和网络密度，大网络几乎都会大于一。",
    "l4": "在脑网络里，这一点尤其要小心。同一份数据，换一个阈值，保留不同密度的连接，小世界系数就跟着变。所以比较两组人时，必须控制密度。",
    # recap
    "z1": "好，我们来总结一下。",
    "z2": "第一，少量随机捷径，就能让路径长度骤降，而聚集系数几乎不变。",
    "z3": "第二，演员网、电网和线虫神经网络，都同时具有高聚类和短路径。",
    "z4": "第三，小世界结构让传播和同步都变快；但判断是不是小世界，要小心零模型和网络密度。",
}

SEEDS = (0, 1)


def lattice(n, k):
    return nx.watts_strogatz_graph(n, k, 0)


class Episode(Narrated):
    LINES = LINES

    def construct(self):
        self.hook()
        parts(self, "q0", ["q1", "q2", "q3"], "这一期分三部分",
              ["一  两个极端与随机重连", "二  两条曲线和背后的道理", "三  真实网络、传播与局限"])
        self.extremes()
        self.model()
        self.curves()
        self.demo()
        self.mechanism()
        self.real()
        self.spreading()
        self.limits()
        recap(self, "z1", [("z2", BLUE, "少量捷径：路径骤降，聚类不变"),
                           ("z3", GREEN, "真实网络：高聚类 + 短路径"),
                           ("z4", GOLD, "传播与同步更快，判据看零模型")])

    # ------------------------------------------------------------------ helpers
    def ring_view(self, G, pos, color=BLUE, r=0.08, ew=2.0, eo=0.6, short=GOLD, base=None):
        """Dots + straight edges; edges not in `base` lattice drawn as shortcuts."""
        dots = {v: Dot(pos[v], radius=r, color=color) for v in G}
        edges = {}
        for u, v in G.edges():
            sc = base is not None and not base.has_edge(u, v)
            edges[(u, v)] = Line(pos[u], pos[v], stroke_width=ew + (1 if sc else 0), color=short if sc else color,
                                 stroke_opacity=1 if sc else eo)
        return dots, edges, VGroup(VGroup(*edges.values()), VGroup(*dots.values()))

    @staticmethod
    def ekey(edges, u, v):
        return edges.get((u, v), edges.get((v, u)))

    # ------------------------------------------------------------------ hook
    def hook(self):
        n = 30
        G0 = lattice(n, 4)
        pos = ring_pos(n, 3.2, LEFT * 2.2 + DOWN * 0.2)
        dots, edges, grp = self.ring_view(G0, pos)
        src, dst = 0, 15
        with self.say("h1"):
            self.play(LaggedStart(*[GrowFromCenter(d) for d in dots.values()], lag_ratio=0.03), run_time=1.6)
            self.play(LaggedStart(*[Create(e) for e in edges.values()], lag_ratio=0.02), run_time=1.6)
        p0 = nx.shortest_path(G0, src, dst)
        steps = counter("传话步数", str(len(p0) - 1), GOLD).move_to(RIGHT * 4.6 + UP * 1.4)
        with self.say("h2"):
            self.play(dots[src].animate.set_color(GOLD).scale(1.8), dots[dst].animate.set_color(GOLD).scale(1.8), run_time=0.8)
            path_l = VGroup(*[Line(pos[a], pos[b], color=GOLD, stroke_width=6) for a, b in zip(p0, p0[1:])])
            self.play(Create(path_l), run_time=2.4, rate_func=linear)
            self.play(FadeIn(steps), run_time=0.6)
        # three shortcuts
        G1 = G0.copy()
        swaps = [((2, 4), (2, 13)), ((20, 22), (20, 8)), ((26, 28), (26, 6))]
        for old, new in swaps:
            G1.remove_edge(*old); G1.add_edge(*new)
        new_lines = {new: Line(pos[new[0]], pos[new[1]], color=RED, stroke_width=4) for _, new in swaps}
        with self.say("h3"):
            self.play(FadeOut(path_l), run_time=0.5)
            for old, new in swaps:
                e = self.ekey(edges, *old)
                self.play(Transform(e, new_lines[new]), run_time=0.9)
        p1 = nx.shortest_path(G1, src, dst)
        with self.say("h4"):
            path2 = VGroup(*[Line(pos[a], pos[b], color=GOLD, stroke_width=7) for a, b in zip(p1, p1[1:])])
            self.play(Create(path2), run_time=1.4, rate_func=linear)
            self.play(Transform(steps, counter("传话步数", f"{len(p0) - 1} → {len(p1) - 1}", GOLD).move_to(steps)), run_time=0.8)
        c0, c1 = nx.average_clustering(G0), nx.average_clustering(G1)
        cc = counter("小圈子（聚集系数）", f"{c0:.2f} → {c1:.2f}", GREEN).move_to(RIGHT * 4.6 + DOWN * 0.8)
        with self.say("h5"):
            v = 10
            tri = VGroup(*[Polygon(pos[v], pos[a], pos[b], fill_color=GREEN, fill_opacity=0.35, stroke_width=0)
                           for a, b in [(8, 9), (9, 11), (11, 12), (9, 10)] if G1.has_edge(a, b) or True][:3])
            self.play(FadeIn(tri), Indicate(dots[v], color=GREEN), run_time=1.0)
            self.play(FadeIn(cc), run_time=0.8)
        with self.say("h6"):
            q = T("改动很少，世界变小", 40, GOLD, weight=BOLD).move_to(RIGHT * 4.4 + DOWN * 2.6)
            self.play(Write(q), run_time=1.0)
        clip_lines(self, "yt_six_degrees_veritasium.mp4", ["h7"], "视频：Veritasium · YouTube", start=20)

    # ------------------------------------------------------------------ two extremes
    def extremes(self):
        tag = self.chapter("一  两个极端")
        n = 24
        Gl = lattice(n, 4)
        m = Gl.number_of_edges()
        seed = next(s for s in range(100) if nx.is_connected(nx.gnm_random_graph(n, m, seed=s)))
        Gr = nx.gnm_random_graph(n, m, seed=seed)
        pl = ring_pos(n, 2.3, LEFT * 3.6 + DOWN * 0.3)
        pr = ring_pos(n, 2.3, RIGHT * 3.6 + DOWN * 0.3)
        dl, el, gl = self.ring_view(Gl, pl, BLUE)
        dr, er, gr = self.ring_view(Gr, pr, VIOLET, eo=0.5)
        tl = T("规则网格", 28).next_to(gl, UP, buff=0.35)
        tr = T("随机图", 28).next_to(gr, UP, buff=0.35)
        with self.say("e1"):
            self.play(FadeIn(tag), FadeIn(tl), FadeIn(tr), run_time=0.8)
            yr = T("1998 年以前", 34, MUTED).move_to(DOWN * 0.3)
            self.play(FadeIn(yr), run_time=0.6)
        self.play(FadeOut(yr), run_time=0.4)
        with self.say("e2"):
            self.play(FadeIn(tl), Create(gl), run_time=1.6)
            tris = VGroup(*[Polygon(pl[i], pl[(i + 1) % n], pl[(i + 2) % n], fill_color=BLUE, fill_opacity=0.35, stroke_width=0)
                            for i in range(0, n, 3)])
            self.play(LaggedStart(*[FadeIn(t) for t in tris], lag_ratio=0.15), run_time=1.4)
        with self.say("e2b"):
            far = VGroup(*[Line(pl[a], pl[b], color=GOLD, stroke_width=6) for a, b in zip(*(lambda p: (p, p[1:]))(nx.shortest_path(Gl, 0, 12)))])
            self.play(Create(far), run_time=1.4)
        with self.say("e3"):
            self.play(FadeIn(tr), Create(gr), run_time=1.6)
            pr_ = nx.shortest_path(Gr, 0, 12)
            near = VGroup(*[Line(pr[a], pr[b], color=GOLD, stroke_width=6) for a, b in zip(pr_, pr_[1:])])
            self.play(Create(near), run_time=1.0)

        def stats(G, ref):
            return VGroup(MathTex(rf"C = {nx.average_clustering(G):.2f}", font_size=36, color=GREEN),
                          MathTex(rf"L = {nx.average_shortest_path_length(G):.1f}", font_size=36, color=GOLD)
                          ).arrange(RIGHT, buff=0.6).next_to(ref, DOWN, buff=0.3)
        with self.say("e4"):
            sl, sr = stats(Gl, gl), stats(Gr, gr)
            self.play(FadeIn(sl[0]), FadeIn(sr[0]), run_time=0.8)
        with self.say("e4b"):
            self.play(FadeIn(sl[1]), FadeIn(sr[1]), run_time=0.8)
        with self.say("e5"):
            q = T("中间地带", 30, GOLD, weight=BOLD).move_to(DOWN * 0.3)
            dbl = DoubleArrow(LEFT * 0.9, RIGHT * 0.9, color=GOLD, buff=0).next_to(q, DOWN, buff=0.2)
            self.play(FadeIn(q, scale=0.5), GrowFromCenter(dbl), run_time=1.0)
        clear(self)

    # ------------------------------------------------------------------ rewiring model
    def model(self):
        tag = self.chapter("一  随机重连")
        n, k, p = 36, 4, 0.12
        base = lattice(n, k)
        pos = ring_pos(n, 3.0, DOWN * 0.2)
        dots, edges, grp = self.ring_view(base, pos)
        with self.say("w1"):
            self.play(FadeIn(tag), FadeIn(grp), run_time=1.2)
            arc = Arc(radius=3.55, start_angle=PI / 2, angle=-2 * PI, color=MUTED, stroke_width=3).shift(DOWN * 0.2)
            arc.add_tip(tip_length=0.25)
            self.play(Create(arc), run_time=1.6)
        rng = np.random.default_rng(5)
        G = base.copy()
        rewires = []
        for (u, v) in sorted(base.edges(), key=lambda e: (min(e), max(e))):
            if rng.random() < p:
                cand = [w for w in range(n) if w != u and not G.has_edge(u, w)]
                w = int(rng.choice(cand))
                G.remove_edge(u, v); G.add_edge(u, w)
                rewires.append(((u, v), (u, w)))
        with self.say("w2") as d:
            pl = MathTex(r"p", "=", f"{p}", font_size=44, color=GOLD).to_corner(UR, buff=0.6)
            self.play(Write(pl), FadeOut(arc), run_time=0.6)
            for old, new in rewires:
                e = self.ekey(edges, *old)
                self.play(Indicate(e, color=RED, scale_factor=1.0), run_time=0.25)
                self.play(Transform(e, Line(pos[new[0]], pos[new[1]], color=GOLD, stroke_width=3)), run_time=max(0.3, d * 0.6 / len(rewires) - 0.25))
        mid = VGroup(grp.copy())
        self.remove(grp); self.add(mid)
        # three panels
        G1 = nx.watts_strogatz_graph(n, k, 1.0, seed=3)
        pa, pb = ring_pos(n, 1.7, LEFT * 4.6 + DOWN * 0.2), ring_pos(n, 1.7, RIGHT * 4.6 + DOWN * 0.2)
        _, _, ga = self.ring_view(base, pa, r=0.05, ew=1.4)
        _, _, gb = self.ring_view(G1, pb, VIOLET, r=0.05, ew=1.4, eo=0.5)
        la = MathTex(r"p=0", font_size=38).next_to(ga, DOWN, buff=0.3)
        lb = MathTex(r"p=1", font_size=38).next_to(gb, DOWN, buff=0.3)
        with self.say("w3"):
            self.play(mid.animate.scale(1.7 / 3.0).move_to(DOWN * 0.2), pl.animate.scale(0.85).move_to(DOWN * 2.45), run_time=1.0)
            self.play(FadeIn(ga), Write(la), run_time=1.0)
            self.play(FadeIn(gb), Write(lb), run_time=1.0)
            lab_a = T("规则", 26, BLUE).next_to(ga, UP, buff=0.3)
            lab_b = T("随机", 26, VIOLET).next_to(gb, UP, buff=0.3)
            self.play(FadeIn(lab_a), FadeIn(lab_b), run_time=0.6)
        with self.say("w4"):
            box = SurroundingRectangle(VGroup(mid, pl), color=GOLD, buff=0.25, corner_radius=0.2)
            lab_m = T("中间地带", 26, GOLD).next_to(box, UP, buff=0.15)
            self.play(Create(box), FadeIn(lab_m), run_time=1.2)
        clear(self)

    # ------------------------------------------------------------------ curves
    def curves(self):
        tag = self.chapter("二  两条曲线")
        n, k = 1000, 10
        G0 = lattice(n, k)
        L0, C0 = nx.average_shortest_path_length(G0), nx.average_clustering(G0)
        ecc0 = max(nx.single_source_shortest_path_length(G0, 0).values())
        ps = np.logspace(-4, 0, 17)
        Ls, Cs, Ts = [], [], []
        for p in ps:
            l, c, t = [], [], []
            for s in SEEDS:
                G = nx.connected_watts_strogatz_graph(n, k, p, seed=s)
                l.append(nx.average_shortest_path_length(G)); c.append(nx.average_clustering(G))
                t.append(np.mean([max(nx.single_source_shortest_path_length(G, v).values()) for v in (0, 250, 500, 750)]))
            Ls.append(np.mean(l) / L0); Cs.append(np.mean(c) / C0); Ts.append(np.mean(t) / ecc0)
        self.ws = (ps, Ls, Cs, Ts)
        i2 = int(np.argmin(abs(ps - 0.01)))
        print(f"[ws] L(.001)={Ls[4]:.3f} L(.01)={Ls[i2]:.3f} C(.01)={Cs[i2]:.3f}")
        ax = log_axes([-4, 0], [0, 1], 9.0, 4.8).shift(DOWN * 0.3 + LEFT * 0.4)
        yt = VGroup(*[MathTex(f"{v:g}", font_size=28, color=MUTED).next_to(ax.P(-4, v), LEFT, buff=0.15) for v in (0, 0.5, 1)])
        xt = log_labels(ax, "x", [-4, -3, -2, -1, 0])
        xl = xlabel("重连概率 p（对数）", ax, buff=0.75)
        lg = legend([(GOLD, "路径长度 L(p)/L(0)"), (GREEN, "聚集系数 C(p)/C(0)")]).to_corner(UR, buff=0.5).shift(DOWN * 0.5)
        with self.say("c1"):
            self.play(FadeIn(tag), run_time=0.6)
            cap = T("n = 1000，每个节点 10 个邻居", 26, MUTED).next_to(ax, UP, buff=0.3)
            self.play(FadeIn(cap), run_time=0.8)
        with self.say("c2"):
            self.play(Create(ax), FadeIn(xt), FadeIn(yt), FadeIn(xl), run_time=1.4)
            self.play(FadeIn(lg), run_time=0.8)
        lx = np.log10(ps)
        ldots = [Dot(ax.P(x, y), radius=0.07, color=GOLD) for x, y in zip(lx, Ls)]
        cdots = [Dot(ax.P(x, y), radius=0.07, color=GREEN) for x, y in zip(lx, Cs)]
        with self.say("c3"):
            self.play(FadeOut(cap), LaggedStart(*[FadeIn(d, scale=0.5) for d in ldots[:5]], lag_ratio=0.3), run_time=1.6)
            self.play(Indicate(ldots[4], color=RED, scale_factor=2), run_time=0.8)
        with self.say("c4"):
            self.play(LaggedStart(*[FadeIn(d, scale=0.5) for d in ldots[5:]], lag_ratio=0.15), run_time=1.6)
            vline = DashedLine(ax.P(-2, 0), ax.P(-2, 1), color=MUTED)
            lv = T(f"{Ls[i2]:.2f}", 26, GOLD, weight=BOLD).next_to(ldots[i2], UR, buff=0.12).shift(RIGHT * 0.15)
            self.play(Create(vline), FadeIn(lv), run_time=0.8)
        with self.say("c5"):
            self.play(LaggedStart(*[FadeIn(d, scale=0.5) for d in cdots], lag_ratio=0.08), run_time=1.8)
            cv = T(f"{Cs[i2]:.0%}", 26, GREEN, weight=BOLD).next_to(cdots[i2], UP, buff=0.15)
            self.play(FadeIn(cv), Indicate(cdots[i2], color=GREEN, scale_factor=2), run_time=0.8)
        with self.say("c6"):
            zone = Rectangle(width=ax.P(-1, 0)[0] - ax.P(-2.7, 0)[0], height=ax.y_length, stroke_width=0,
                             fill_color=GOLD, fill_opacity=0.14).move_to(ax.P(-1.85, 0.5))
            zl = T("小世界", 30, GOLD, weight=BOLD).move_to(zone.get_bottom() + UP * 0.35)
            self.play(FadeIn(zone), FadeIn(zl), run_time=1.0)
        clear(self, keep=[tag])
        f = VGroup(MathTex(r"L \approx L_{\mathrm{random}}", font_size=60, color=GOLD),
                   MathTex(r"C \gg C_{\mathrm{random}}", font_size=60, color=GREEN)).arrange(DOWN, buff=0.7).shift(LEFT * 1.5)
        with self.say("c7"):
            self.play(Write(f[0]), run_time=1.0)
            self.play(Write(f[1]), run_time=1.0)
        with self.say("c7b"):
            l1 = T("路径：与随机图差不多", 28, GOLD).next_to(f[0], RIGHT, buff=0.6)
            self.play(FadeIn(l1, shift=LEFT * 0.2), run_time=0.6)
            self.wait(1.5)
            l2 = T("聚类：远大于随机图", 28, GREEN).next_to(f[1], RIGHT, buff=0.6)
            self.play(FadeIn(l2, shift=LEFT * 0.2), run_time=0.6)
        clear(self)

    def demo(self):
        clip_lines(self, "ws_demo.mp4", ["d1", "d2"], "本站交互演示：Watts–Strogatz 重连", start=0.5, box="full")

    # ------------------------------------------------------------------ mechanism
    def mechanism(self):
        tag = self.chapter("二  一条捷径的威力")
        n = 60
        G0 = lattice(n, 4)
        pos = ring_pos(n, 3.0, LEFT * 3.0 + DOWN * 0.3)
        dots, edges, grp = self.ring_view(G0, pos, MUTED, r=0.09, eo=0.5)
        G1 = G0.copy(); G1.remove_edge(30, 32); G1.add_edge(0, 30)

        def dcol(G):
            d = nx.single_source_shortest_path_length(G, 0)
            mx = max(nx.single_source_shortest_path_length(G0, 0).values())
            return {v: interpolate_color(ManimColor(BLUE), ManimColor(RED), d[v] / mx) for v in G}
        with self.say("m1"):
            self.play(FadeIn(tag), FadeIn(grp), run_time=1.0)
            c = dcol(G0)
            self.play(*[dots[v].animate.set_color(c[v]) for v in G0], run_time=1.0)
            bar = VGroup(*[Rectangle(width=0.25, height=0.18, stroke_width=0, fill_opacity=1,
                                     fill_color=interpolate_color(ManimColor(BLUE), ManimColor(RED), i / 9)) for i in range(10)]).arrange(RIGHT, buff=0)
            bl = VGroup(T("近", 22, BLUE).next_to(bar, LEFT, buff=0.1), T("远", 22, RED).next_to(bar, RIGHT, buff=0.1))
            leg = VGroup(bar, bl).next_to(grp, DOWN, buff=0.25)
        with self.say("m1b"):
            self.play(FadeIn(leg), run_time=0.6)
        sc = Line(pos[0], pos[30], color=GOLD, stroke_width=5)
        L0, L1 = nx.average_shortest_path_length(G0), nx.average_shortest_path_length(G1)
        C0, C1 = nx.average_clustering(G0), nx.average_clustering(G1)
        with self.say("m2"):
            self.play(FadeOut(self.ekey(edges, 30, 32)), Create(sc), run_time=1.2)
            c = dcol(G1)
            self.play(*[dots[v].animate.set_color(c[v]) for v in G1], run_time=1.6)
            k1 = counter("平均路径长度", f"{L0:.1f} → {L1:.1f}", GOLD).move_to(RIGHT * 3.8 + UP * 1.3)
            self.play(FadeIn(k1), run_time=0.8)
        with self.say("m3"):
            lost = [t for t in ([30, 31, 32], [29, 30, 32], [30, 32, 33]) if True]
            tri = VGroup(*[Polygon(*[pos[x] for x in t], fill_color=RED, fill_opacity=0.5, stroke_width=0) for t in lost])
            self.play(FadeIn(tri), run_time=0.8)
            self.play(tri.animate.set_opacity(0.0), run_time=0.8)
            k2 = counter("聚集系数", f"{C0:.3f} → {C1:.3f}", GREEN).move_to(RIGHT * 3.8 + DOWN * 0.6)
            self.play(FadeIn(k2), run_time=0.8)
        print(f"[ws] one shortcut: L {L0:.2f}->{L1:.2f}, C {C0:.3f}->{C1:.3f}")
        with self.say("m4"):
            p1 = T(f"路径 −{(1 - L1 / L0) * 100:.0f}%", 34, GOLD, weight=BOLD)
            p2 = T(f"聚类 −{(1 - C1 / C0) * 100:.0f}%", 34, GREEN, weight=BOLD)
            VGroup(p1, p2).arrange(RIGHT, buff=0.8).move_to(RIGHT * 3.8 + DOWN * 2.4)
            self.play(FadeIn(p1, shift=UP * 0.2), run_time=0.8)
            self.play(FadeIn(p2, shift=UP * 0.2), run_time=0.8)
        clear(self)

    # ------------------------------------------------------------------ real networks
    def real(self):
        tag = self.chapter("三  三张真实网络")
        data = [("演员合作网", "n = 225226", 3.65, 2.99, 0.79, 0.00027, BLUE),
                ("西部电网", "n = 4941", 18.7, 12.4, 0.080, 0.005, GOLD),
                ("线虫神经网络", "n = 282", 2.65, 2.25, 0.28, 0.05, GREEN)]
        xs = [-4.2, 0.4, 5.0]
        heads, Lrow, Crow = VGroup(), VGroup(), VGroup()
        rowL = T("路径长度 L", 24, MUTED).move_to(LEFT * 6.0 + UP * 0.4)
        rowC = T("聚集系数 C", 24, MUTED).move_to(LEFT * 6.0 + DOWN * 2.2)
        hmax = 1.6

        def pair(x, y0, a, b, col, fmt):
            m = max(a, b)
            ra = Rectangle(width=0.7, height=hmax * a / m, fill_color=col, fill_opacity=0.9, stroke_width=0)
            rb = Rectangle(width=0.7, height=max(hmax * b / m, 0.02), fill_color=MUTED, fill_opacity=0.7, stroke_width=0)
            ra.move_to([x - 0.45, y0, 0], aligned_edge=DOWN); rb.move_to([x + 0.45, y0, 0], aligned_edge=DOWN)
            ta = T(fmt(a), 22, col).next_to(ra, UP, buff=0.08)
            tb = T(fmt(b), 22, MUTED).next_to(rb, UP, buff=0.08)
            return VGroup(ra, rb, ta, tb)
        for (name, nn, L, Lr, C, Cr, col), x in zip(data, xs):
            heads.add(VGroup(T(name, 28, col, weight=BOLD), T(nn, 20, MUTED)).arrange(DOWN, buff=0.1).move_to([x, 3.0, 0]))
            Lrow.add(pair(x, -0.3, L, Lr, col, lambda v: f"{v:g}"))
            Crow.add(pair(x, -2.9, C, Cr, col, lambda v: f"{v:g}"))
        key = VGroup(Square(0.22, fill_color=INK, fill_opacity=0.9, stroke_width=0), T("真实", 20),
                     Square(0.22, fill_color=MUTED, fill_opacity=0.7, stroke_width=0), T("同规模随机图", 20)
                     ).arrange(RIGHT, buff=0.12).to_edge(DOWN, buff=0.2)
        heads.shift(DOWN * 0.25)
        with self.say("r1"):
            self.play(FadeIn(tag), run_time=0.5)
            self.play(LaggedStart(*[FadeIn(h, shift=DOWN * 0.2) for h in heads], lag_ratio=0.4), run_time=2.0)
            self.play(FadeIn(key), FadeOut(tag), run_time=0.6)
        with self.say("r2"):
            self.play(FadeIn(rowL), LaggedStart(*[FadeIn(g, shift=UP * 0.2) for g in Lrow], lag_ratio=0.3), run_time=1.8)
        with self.say("r3"):
            self.play(FadeIn(rowC), LaggedStart(*[FadeIn(g, shift=UP * 0.2) for g in Crow], lag_ratio=0.3), run_time=1.8)
            x3k = T("≈ 2900 倍", 26, RED, weight=BOLD).next_to(Crow[0], RIGHT, buff=0.05).shift(UP * 0.6)
            self.play(FadeIn(x3k), run_time=0.6)
        keep = [m for m in self.mobjects]
        self.play(*[FadeOut(m) for m in keep], run_time=0.5)
        with self.say("r4"):
            self.clip_on("yt_worm_connectome_einstein.mp4", "center", "视频：Albert Einstein College of Medicine · YouTube", start=30)
        self.clip_off()
        self.play(*[FadeIn(m) for m in keep], run_time=0.5)
        with self.say("r4b"):
            box = SurroundingRectangle(VGroup(heads[2], Lrow[2], Crow[2]), color=GREEN, buff=0.2, corner_radius=0.15)
            self.play(Create(box), VGroup(heads[:2], Lrow[:2], Crow[:2], x3k).animate.set_opacity(0.3), run_time=1.0)
        with self.say("r5"):
            self.play(FadeOut(box), VGroup(heads[:2], Lrow[:2], Crow[:2], x3k).animate.set_opacity(1), run_time=1.0)
        clear(self)

    # ------------------------------------------------------------------ spreading
    def spreading(self):
        tag = self.chapter("三  传播与同步")
        n = 80
        Ga = lattice(n, 4)
        Gb = Ga.copy()
        for old, new in [((10, 12), (10, 47)), ((30, 32), (30, 70)), ((52, 54), (52, 20)), ((66, 68), (66, 3))]:
            Gb.remove_edge(*old); Gb.add_edge(*new)
        pa, pb = ring_pos(n, 2.5, LEFT * 3.6 + DOWN * 0.4), ring_pos(n, 2.5, RIGHT * 3.6 + DOWN * 0.4)
        da, _, ga = self.ring_view(Ga, pa, MUTED, r=0.07, eo=0.4)
        db, _, gb = self.ring_view(Gb, pb, MUTED, r=0.07, eo=0.4, base=Ga)
        ta = T("规则网格", 26).next_to(ga, UP, buff=0.3)
        tb = T("加 4 条捷径", 26, GOLD).next_to(gb, UP, buff=0.3)
        with self.say("s1"):
            self.play(FadeIn(tag), FadeIn(ga), FadeIn(gb), FadeIn(ta), FadeIn(tb), run_time=1.2)
            self.play(da[0].animate.set_color(RED).scale(1.6), db[0].animate.set_color(RED).scale(1.6), run_time=0.6)
        wa = nx.single_source_shortest_path_length(Ga, 0)
        wb = nx.single_source_shortest_path_length(Gb, 0)
        Ta, Tb = max(wa.values()), max(wb.values())
        ca = counter("步数", "0", RED).next_to(ga, DOWN, buff=0.15)
        cb = counter("步数", "0", RED).next_to(gb, DOWN, buff=0.15)
        self.add(ca, cb)

        def step(t):
            an = [da[v].animate.set_color(RED) for v, d in wa.items() if d == t]
            an += [db[v].animate.set_color(RED) for v, d in wb.items() if d == t]
            if t <= Ta:
                an.append(Transform(ca, counter("步数", str(t), RED).move_to(ca)))
            if t <= Tb:
                an.append(Transform(cb, counter("步数", str(t), RED).move_to(cb)))
            return an
        with self.say("s2") as d:
            for t in range(1, Tb + 1):
                self.play(*step(t), run_time=d * 0.85 / Tb)
        with self.say("s3") as d:
            for t in range(Tb + 1, Ta + 1):
                self.play(*step(t), run_time=d * 0.85 / max(1, Ta - Tb))
        print(f"[ws] spread steps lattice {Ta} shortcut {Tb}")
        clear(self, keep=[tag])
        ps, Ls, Cs, Ts = self.ws
        ax = log_axes([-4, 0], [0, 1], 8.0, 4.4).shift(DOWN * 0.3 + LEFT * 0.6)
        yt = VGroup(*[MathTex(f"{v:g}", font_size=28, color=MUTED).next_to(ax.P(-4, v), LEFT, buff=0.15) for v in (0, 0.5, 1)])
        xt = log_labels(ax, "x", [-4, -3, -2, -1, 0])
        xl = xlabel("重连概率 p", ax, buff=0.75)
        lx = np.log10(ps)
        cl = pline(ax, lx, Ls, GOLD, 5)
        ct = pline(ax, lx, Ts, RED, 4)
        lg = legend([(GOLD, "路径长度"), (RED, "传遍全体的步数")]).to_corner(UR, buff=0.5).shift(DOWN * 0.5)
        with self.say("s4") as d:
            self.play(Create(ax), FadeIn(xt), FadeIn(yt), FadeIn(xl), run_time=1.0)
            self.play(Create(cl), FadeIn(lg[0]), run_time=d * 0.3)
            self.play(Create(ct), FadeIn(lg[1]), run_time=d * 0.3)
        with self.say("s5"):
            self.play(Indicate(ct, color=RED), run_time=1.2)
        with self.say("s5b"):
            osc = VGroup(*[Arrow(ORIGIN, 0.5 * np.array([np.cos(a), np.sin(a), 0]), buff=0, color=VIOLET, stroke_width=4)
                           .shift(RIGHT * (i * 0.55)) for i, a in enumerate(np.linspace(0, 5, 6))]).next_to(lg, DOWN, buff=0.6)
            self.play(FadeIn(osc), run_time=0.6)
            self.play(*[a.animate.rotate(-np.linspace(0, 5, 6)[i] + PI / 3, about_point=a.get_start()) for i, a in enumerate(osc)], run_time=1.8)
        clear(self, keep=[tag])
        with self.say("s6"):
            hemi = VGroup(Ellipse(width=4.2, height=5.0, color=MUTED, stroke_width=3).shift(LEFT * 2.0),
                          Ellipse(width=4.2, height=5.0, color=MUTED, stroke_width=3).shift(RIGHT * 2.0)).shift(DOWN * 0.3)
            Gs = nx.connected_watts_strogatz_graph(46, 4, 0.12, seed=4)
            ps_ = {}
            for i in range(46):
                a = 2 * PI * i / 46
                ps_[i] = np.array([3.0 * np.cos(a), 2.0 * np.sin(a) - 0.3, 0])
            dd, ee, gg = self.ring_view(Gs, ps_, BLUE, r=0.07, base=lattice(46, 4))
            self.play(Create(hemi), run_time=1.0)
            self.play(FadeIn(gg), run_time=1.2)
        clear(self)

    # ------------------------------------------------------------------ limits
    def limits(self):
        tag = self.chapter("三  局限")
        Gw = nx.watts_strogatz_graph(2000, 10, 0.1, seed=1)
        Gb = nx.barabasi_albert_graph(2000, 5, seed=1)
        ax = plain_axes([0, 60, 10], [0, 0.4, 0.1], 9.0, 4.2, xnums=[0, 10, 20, 30, 40, 50, 60], ynums=[0.1, 0.2, 0.3, 0.4]).shift(DOWN * 0.4)
        xl = xlabel("度 k", ax)
        yl = ylabel("比例", ax)

        def hist(G, col):
            deg = np.array([d for _, d in G.degree()])
            bars = VGroup()
            for kk in range(1, 61):
                f = (deg == kk).mean()
                if f > 0:
                    bars.add(Rectangle(width=ax.x_length / 60 * 0.9, height=max(ax.y_length * f / 0.4, 0.01), fill_color=col,
                                       fill_opacity=0.8, stroke_width=0).move_to(ax.c2p(kk, 0), aligned_edge=DOWN))
            return bars, deg.max()
        hw, _ = hist(Gw, BLUE)
        hb, kmax = hist(Gb, GOLD)
        with self.say("l1"):
            self.play(FadeIn(tag), Create(ax), FadeIn(xl), FadeIn(yl), run_time=1.0)
            self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in hw], lag_ratio=0.05), run_time=1.6)
            lw = T("小世界模型", 26, BLUE).next_to(ax.c2p(10, 0.38), RIGHT)
            self.play(FadeIn(lw), run_time=0.5)
        with self.say("l2"):
            self.play(hw.animate.set_opacity(0.25), run_time=0.5)
            self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in hb], lag_ratio=0.02), run_time=1.6)
            arr = Arrow(ax.c2p(52, 0.12), ax.c2p(58, 0.02), color=GOLD, buff=0)
            lb = T(f"尾巴一直延伸到 k = {kmax}", 24, GOLD).next_to(arr, UP, buff=0.1).shift(LEFT * 0.8)
            self.play(GrowArrow(arr), FadeIn(lb), run_time=0.8)
        clear(self, keep=[tag])
        # sigma depends on density: threshold a weighted brain-like matrix
        rng = np.random.default_rng(3)
        n = 60
        P = rng.random((n, 2))
        D = np.linalg.norm(P[:, None] - P[None], axis=2)
        W = np.exp(-D / 0.25) + 0.25 * rng.random((n, n)); W = (W + W.T) / 2; np.fill_diagonal(W, 0)
        iu = np.triu_indices(n, 1)
        order = np.argsort(-W[iu])

        def thr(dens):
            G = nx.Graph(); G.add_nodes_from(range(n))
            m = int(dens * len(order))
            G.add_edges_from(zip(iu[0][order[:m]], iu[1][order[:m]]))
            G = G.subgraph(max(nx.connected_components(G), key=len)).copy()
            R = nx.gnm_random_graph(G.number_of_nodes(), G.number_of_edges(), seed=1)
            R = R.subgraph(max(nx.connected_components(R), key=len)).copy()
            s = (nx.average_clustering(G) / nx.average_clustering(R)) / (nx.average_shortest_path_length(G) / nx.average_shortest_path_length(R))
            return G, s
        sig = MathTex(r"\sigma=\frac{C/C_{\mathrm{rand}}}{L/L_{\mathrm{rand}}}", font_size=52).move_to(UP * 2.0)
        with self.say("l3"):
            self.play(Write(sig), run_time=1.2)
        with self.say("l3b"):
            num = T("聚类比随机图高几倍", 24, GREEN).next_to(sig, RIGHT, buff=0.4).shift(UP * 0.35)
            den = T("路径比随机图长几倍", 24, GOLD).next_to(sig, RIGHT, buff=0.4).shift(DOWN * 0.35)
            self.play(FadeIn(num), run_time=0.6)
            self.play(FadeIn(den), run_time=0.6)
            nb = T("依赖零模型与网络密度", 26, MUTED).next_to(sig, DOWN, buff=0.3)
            self.play(FadeIn(nb), run_time=0.6)
        pos = {i: np.array([P[i, 0] * 3.2, P[i, 1] * 2.6, 0]) for i in range(n)}
        panels = VGroup()
        for j, dens in enumerate((0.05, 0.1, 0.2)):
            G, s = thr(dens)
            off = np.array([-4.6 + 4.6 * j - 1.6, -3.3, 0])
            dots = VGroup(*[Dot(pos[v] + off, radius=0.045, color=BLUE) for v in range(n)])
            ed = VGroup(*[Line(pos[u] + off, pos[v] + off, stroke_width=0.8, color=BLUE, stroke_opacity=0.4) for u, v in G.edges()])
            lab = VGroup(T(f"密度 {int(dens * 100)}%", 22, MUTED), MathTex(rf"\sigma \approx {s:.1f}", font_size=34, color=GOLD)
                         ).arrange(RIGHT, buff=0.3).next_to(VGroup(dots), DOWN, buff=0.15)
            panels.add(VGroup(ed, dots, lab))
        with self.say("l4"):
            self.play(VGroup(sig, nb, num, den).animate.scale(0.75).shift(UP * 0.8), run_time=0.6)
            self.play(LaggedStart(*[FadeIn(p) for p in panels], lag_ratio=0.4), run_time=2.4)
        clear(self)
