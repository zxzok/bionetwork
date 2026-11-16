"""Paper explainer: Newman 2006, modularity and the spectral method for community detection."""
import networkx as nx
import numpy as np

from paperhelp import *  # noqa: F401,F403

TITLE = "模块度与谱方法：用一个特征向量切开网络"
LINES = {
    # hook
    "h1": "这还是空手道俱乐部的关系网。给它划分社团，最直接的想法是：让组和组之间的连线尽量少。左上角数的，就是组间连线有几条。",
    "h2": "可是，如果只看这一条，最好的答案永远是：把所有人都放进同一组。这样组间连线是零。",
    "h3": "这显然不是我们想要的。好的划分，需要一个新的标准。",
    "h4": "【慢】2006年的一篇论文，把这个问题变成了一道漂亮的线性代数题。",
    "h4b": "论文的作者纽曼，是研究网络的物理学家。画面里是他在一次学术活动上的对谈。",
    "p0": "这一期分三部分来讲。",
    "p1": "第一部分，模块度矩阵，以及怎样把划分社团变成求特征向量。",
    "p2": "第二部分，在空手道俱乐部上检验，以及这个方法会拒绝划分的性质。",
    "p3": "第三部分，和其他算法的比较，在生物网络里的用处，最后说说局限。",
    # modularity matrix
    "q1": "先看第一部分。关键是换一把尺子：好的划分，不是组间边少，而是组内的边，比随机期望的多。",
    "q2": "左边两个大黄点，连接都很多，就算随便连，它们之间也很可能有边。右边两个蓝色小点，连接都很少，它们连在一起，才更说明问题。",
    "q3": "那么，随机期望是多少。在保持每个节点度不变的随机网络里，两点之间的期望边数，写出来是这样。",
    "q3b": "k_i和k_j是两个节点的度，m是网络的总边数。也就是说，两个度相乘，再除以总边数的两倍。度都大的两个点，期望就高。",
    "q4": "用实际连边，减去这个期望，就得到模块度矩阵，记作B。",
    "q4b": "A_ij是实际有没有边，有边是一，没边是零。B_ij为正，说明这两点连得比随机预期更紧；为负，说明更疏远。",
    "q5": "把空手道俱乐部的三个矩阵画出来。每一行、每一列是一个成员。左边是实际连边，中间是随机期望，右边是它们的差。",
    "q6": "按真实的两派排好顺序。差值矩阵里，对角线上的两块，大多是金色的正数；两块之间，大多是紫色的负数。",
    # quadratic form
    "s1": "现在给每个节点贴一个标签，正一或者负一，表示它分到哪一组。把所有标签排成一列，就是向量s。",
    "s2": "模块度Q，就可以写成这个式子。",
    "s2b": "两个节点分到同一组，s_i乘s_j等于一，B_ij被加进来；分到不同组，等于负一，B_ij被减掉。所以同组的正值越多，Q越大。前面的四m分之一，只是为了归一。",
    "s3": "如果标签可以取任意实数，让Q最大的，正是B的最大特征值对应的那个特征向量，叫主特征向量。",
    "s3b": "这一行的意思是：B乘以u_1，等于一个数乘以u_1。这个数贝塔一，就是最大的特征值。",
    "s4": "【慢】可标签只能取正负一。作者用了一个简单的近似：看主特征向量每个分量的正负号来分组。",
    # karate
    "k1": "下面进入第二部分。我们在场景里，对空手道俱乐部算出这个特征向量。右边每根柱子，是一个成员的分量，横轴是成员编号。",
    "k2": "正的分到蓝色一组，负的分到金色一组。只要一次计算。",
    "k3": "和实际分裂对比，三十四人里三十三人分对。唯一的分歧是9号，他的分量几乎为零，正好落在两派的边界上。原文报告的结果，与实际分裂完全一致。",
    "k4": "分量绝对值最大的两个人，是画了白圈的1号和34号，正是两派的领头人。",
    "g1": "本站的知识页面里，有给空手道俱乐部分组的交互演示，下面一行显示模块度。先全部归为一组，模块度是零。",
    "g2": "随机分组，模块度接近零，甚至是负的。按真实的分裂分组，模块度约为零点三七。最后让贪心优化来找，分数还能再高一点。",
    # indivisible
    "r1": "这个谱方法有三个好性质。",
    "v1": "第一，不需要事先规定每组有多大。",
    "v2": "第二，它会拒绝划分：网络不该分的时候，它就不分。",
    "v3": "第三，分量的大小有意义：绝对值大的节点，对模块度贡献大；接近零的节点，处在两个社团的边界上。",
    "r2": "我们看第二条。左边是一个完全图，人人互相连接。下面这条数轴上的点，是它的模块度矩阵的特征值，一个正的也没有。所以算法把所有人留在同一组。",
    "r3": "右边是两个团，中间只连一条边。它的特征值里，出现了正数，网络就该分。作者把左边这种网络称为不可分的，并把社团定义为不可分的子图。",
    "r4": "要分出更多社团，就反复二分。每次对一个子图g，用的是这个广义的模块度矩阵。",
    "r4b": "它在原来的B上，把对角线减去一项。这样做，保证优化的始终是原网络的模块度。某次划分不再让模块度提高，也就是德尔塔Q不大于零，就停下来。",
    "r5": "空手道俱乐部这样一路分下去，停在四个社团，模块度约为零点四二。",
    # comparison
    "c1": "最后是第三部分。作者在六个真实网络上，和当时的其他算法做了比较，本文方法的模块度都更高。",
    "c2": "以约两万七千个节点的凝聚态物理合作网络为例：贪心算法是零点六六八，极值优化是零点六七九，本文方法达到零点七二三。",
    "c3": "在一千二百二十五个政治博客组成的网络里，最优划分恰好是两个社团：一组百分之九十七是保守派，另一组百分之九十三是自由派。",
    "c4": "最大的那个合作网络，在当时的个人计算机上，大约二十分钟就能算完。",
    # biology
    "b1": "在生物网络里，这类方法常被用来寻找基因共表达模块和蛋白质功能模块。",
    "b1b": "基因共表达网络，是把表达模式相似的基因连起来。画面里，是一段讲解这种模块分析的课程。",
    "b2": "能拒绝划分，在这里尤其重要；否则在没有结构的数据里，也会硬找出社团来。",
    "b3": "节点的颜色，是它在主特征向量里的分量。分量接近零的，就是画了黄圈的这些，处在两个模块的交界处。这些边界上的蛋白扮演什么角色，同样值得研究。",
    # limits
    "l1": "下面说说局限。模块度本身也有陷阱。我们生成一张完全随机的网络，大约一千个节点，没有任何社团结构。",
    "l2": "【慢】可优化出来的模块度，依然有零点五多。也就是说，高模块度本身，不能证明网络里真有社团。",
    "l3": "模块度还有分辨率极限，大网络中规模太小的社团可能被合并。它的地形上，还有许多得分相近、结构却差别很大的高原，就是这几个红点。",
    "l4": "后来，更快的算法把规模推到了上亿个节点；随机块模型等统计推断方法，则能做模型选择，并给出不确定性。",
    # recap
    "z1": "好，我们来总结一下。",
    "z2": "第一，模块度衡量的是，组内连边比随机期望多出多少。",
    "z3": "第二，按主特征向量的正负号二分，又快又好；没有正特征值，就说明网络不该再分。",
    "z4": "第三，模块度有分辨率极限，随机网络的模块度也可能很高。",
}


def mod_matrix(G, nodes=None):
    nodes = list(G) if nodes is None else nodes
    A = nx.to_numpy_array(G, nodelist=nodes, weight=None)
    k = A.sum(1); m = k.sum() / 2
    return A, np.outer(k, k) / (2 * m), A - np.outer(k, k) / (2 * m), m


def heat(M, size, cmap):
    img = np.zeros((M.shape[0], M.shape[1], 3), np.uint8)
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            img[i, j] = cmap(M[i, j])
    im = ImageMobject(img)
    im.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
    im.height = size
    return im


def hexrgb(c):
    c = ManimColor(c).to_rgb()
    return np.array(c) * 255


def lerp(a, b, t):
    return (hexrgb(a) * (1 - t) + hexrgb(b) * t).astype(np.uint8)


class Episode(Narrated):
    LINES = LINES

    def construct(self):
        K = nx.karate_club_graph()
        self.K = K
        self.kpos = fit(nx.kamada_kawai_layout(K), (-6.4, -0.6, -3.0, 2.7))
        A, P, B, m = mod_matrix(K)
        w, V = np.linalg.eigh(B)
        u = V[:, -1]
        if u[0] < 0:
            u = -u
        self.u, self.B, self.m = u, B, m
        self.club = np.array([1 if K.nodes[v]["club"] == "Mr. Hi" else -1 for v in K])
        self.hook()
        parts(self, "p0", ["p1", "p2", "p3"], "这一期分三部分",
              ["一  模块度矩阵与谱方法", "二  空手道俱乐部与拒绝划分", "三  比较、应用与局限"])
        self.matrix()
        self.quadratic()
        self.karate()
        clip_lines(self, "modularity_nm_demo.mp4", ["g1", "g2"], "本站交互演示：给空手道俱乐部分组", start=0.3, box="full")
        self.indivisible()
        self.compare()
        self.biology()
        self.limits()
        recap(self, "z1", [("z2", GOLD, "模块度：比随机期望多出的组内边"),
                           ("z3", BLUE, "主特征向量的正负号二分"),
                           ("z4", RED, "分辨率极限；随机网络也可高分")])

    # ------------------------------------------------------------------ hook
    def hook(self):
        K = self.K
        pos = {v: p + RIGHT * 3.0 for v, p in self.kpos.items()}
        net = NetView(K, pos, color=MUTED, rmin=0.07, rk=0.02, eo=0.5)
        rng = np.random.default_rng(3)
        part = {v: (0 if pos[v][0] < 3.0 else 1) for v in K}

        def cut(pt):
            return sum(pt[a] != pt[b] for a, b in K.edges())
        cnt = counter("组间连线", str(cut(part)), RED).to_corner(UL, buff=0.6).shift(DOWN * 0.6)
        with self.say("h1"):
            self.play(FadeIn(net.group), run_time=1.0)
            self.play(*[net.dots[v].animate.set_color(BLUE if part[v] == 0 else GOLD) for v in K], FadeIn(cnt), run_time=1.0)
            p2 = {v: (0 if pos[v][1] > -0.2 else 1) for v in K}
            self.play(*[net.dots[v].animate.set_color(BLUE if p2[v] == 0 else GOLD) for v in K],
                      Transform(cnt, counter("组间连线", str(cut(p2)), RED).move_to(cnt)), run_time=1.0)
        with self.say("h2"):
            p3 = {v: 0 for v in K}
            self.play(*[net.dots[v].animate.set_color(BLUE) for v in K],
                      Transform(cnt, counter("组间连线", "0", RED).move_to(cnt)), run_time=1.2)
            best = T("“最优”", 34, RED, weight=BOLD).next_to(cnt, DOWN, buff=0.4)
            self.play(FadeIn(best), run_time=0.6)
        with self.say("h3"):
            x = Cross(best, stroke_color=RED)
            self.play(Create(x), run_time=0.6)
            q = T("需要新的标准", 34, GOLD).to_edge(DOWN, buff=0.4)
            self.play(FadeIn(q), run_time=0.8)
        with self.say("h4"):
            self.play(net.group.animate.set_opacity(0.25), run_time=1.0)
        clip_lines(self, "yt_newman_oxford.mp4", ["h4b"], "视频：Oxford Internet Institute · YouTube", start=300)

    # ------------------------------------------------------------------ modularity matrix
    def matrix(self):
        tag = self.chapter("一  比随机期望多多少")
        with self.say("q1"):
            a = T("组间边少", 40, MUTED).shift(UP * 0.8 + LEFT * 3)
            b = T("组内边比随机期望多", 40, GOLD, weight=BOLD).shift(DOWN * 0.6 + RIGHT * 1.5)
            self.play(FadeIn(tag), FadeIn(a), run_time=0.8)
            self.play(a.animate.set_opacity(0.3), FadeIn(b, shift=LEFT * 0.3), Create(Line(a.get_left(), a.get_right(), color=RED, stroke_width=4)), run_time=1.2)
        clear(self, keep=[tag])
        with self.say("q2"):
            h1, h2 = Dot(LEFT * 4.6 + UP * 0.9, radius=0.42, color=GOLD), Dot(LEFT * 1.8 + UP * 0.9, radius=0.42, color=GOLD)
            sp = VGroup(*[Line(h.get_center(), h.get_center() + 0.95 * np.array([np.cos(t), np.sin(t), 0]), color=GOLD, stroke_width=2, stroke_opacity=0.5)
                          for h in (h1, h2) for t in np.linspace(0, 2 * PI, 13)[:-1]])
            e1 = DashedLine(h1.get_right(), h2.get_left(), color=GOLD)
            l1 = T("很可能相连", 24, GOLD).next_to(e1, DOWN, buff=0.45)
            s1, s2 = Dot(RIGHT * 2.0 + UP * 0.9, radius=0.14, color=BLUE), Dot(RIGHT * 4.8 + UP * 0.9, radius=0.14, color=BLUE)
            e2 = Line(s1.get_center(), s2.get_center(), color=BLUE, stroke_width=4)
            l2 = T("相连更说明问题", 24, BLUE).next_to(e2, DOWN, buff=0.45)
            self.play(FadeIn(sp), FadeIn(h1), FadeIn(h2), Create(e1), FadeIn(l1), run_time=1.4)
            self.play(FadeIn(s1), FadeIn(s2), Create(e2), FadeIn(l2), run_time=1.2)
        with self.say("q3"):
            f = MathTex(r"P_{ij}=\frac{k_i\,k_j}{2m}", font_size=58).shift(DOWN * 2.0)
            self.play(Write(f), run_time=1.4)
        with self.say("q3b"):
            fl = VGroup(T("k_i, k_j：两点的度", 22, GOLD), T("m：总边数", 22, MUTED)).arrange(DOWN, aligned_edge=LEFT, buff=0.15).next_to(f, RIGHT, buff=0.6)
            self.play(FadeIn(fl[0]), run_time=0.5)
            self.play(FadeIn(fl[1]), run_time=0.5)
        with self.say("q4"):
            self.play(FadeOut(VGroup(h1, h2, sp, e1, l1, s1, s2, e2, l2, fl)), f.animate.move_to(UP * 0.8), run_time=0.8)
            fb = MathTex(r"B_{ij}=A_{ij}-\frac{k_i\,k_j}{2m}", font_size=58, color=GOLD).next_to(f, DOWN, buff=0.7)
            self.play(Write(fb), run_time=1.4)
        with self.say("q4b"):
            ta = T("A_ij：实际有边为 1，没边为 0", 22, BLUE).next_to(fb, DOWN, buff=0.5)
            tb = T("B_ij > 0：比随机更紧；B_ij < 0：更疏远", 22, GOLD).next_to(ta, DOWN, buff=0.2)
            self.play(FadeIn(ta), run_time=0.5)
            self.wait(1.0)
            self.play(FadeIn(tb), run_time=0.5)
        clear(self, keep=[tag])
        order = sorted(range(34), key=lambda i: (-self.club[i], -self.u[i]))
        A, P, B, _ = mod_matrix(self.K, order)
        vmax = abs(B).max()
        hA = heat(A, 3.4, lambda x: lerp(BG, BLUE, x))
        hP = heat(P, 3.4, lambda x: lerp(BG, MUTED, min(1, x / P.max())))
        hB = heat(B, 3.4, lambda x: lerp(BG, GOLD, min(1, x / 0.6)) if x > 0 else lerp(BG, VIOLET, min(1, -x / 0.6)))
        Group(hA, hP, hB).arrange(RIGHT, buff=1.0).shift(DOWN * 0.3)
        ops = VGroup(MathTex("-", font_size=60).move_to((hA.get_right() + hP.get_left()) / 2),
                     MathTex("=", font_size=60).move_to((hP.get_right() + hB.get_left()) / 2))
        labs = VGroup(T("实际连边 A", 24, BLUE).next_to(hA, UP, buff=0.25), T("随机期望", 24, MUTED).next_to(hP, UP, buff=0.25),
                      T("模块度矩阵 B", 24, GOLD).next_to(hB, UP, buff=0.25))
        with self.say("q5"):
            self.play(FadeIn(hA), FadeIn(labs[0]), run_time=0.9)
            self.play(FadeIn(ops[0]), FadeIn(hP), FadeIn(labs[1]), run_time=0.9)
            self.play(FadeIn(ops[1]), FadeIn(hB), FadeIn(labs[2]), run_time=0.9)
        n1 = int((self.club == 1).sum())
        cell = hB.height / 34
        with self.say("q6"):
            tl = hB.get_corner(UL)
            r1 = Rectangle(width=cell * n1, height=cell * n1, color=GOLD, stroke_width=3).move_to(tl + np.array([cell * n1 / 2, -cell * n1 / 2, 0]))
            r2 = Rectangle(width=cell * (34 - n1), height=cell * (34 - n1), color=GOLD, stroke_width=3).move_to(
                tl + np.array([cell * (n1 + (34 - n1) / 2), -cell * (n1 + (34 - n1) / 2), 0]))
            self.play(Create(r1), Create(r2), run_time=1.0)
            key = VGroup(Square(0.25, fill_color=GOLD, fill_opacity=1, stroke_width=0), T("正", 22), Square(0.25, fill_color=VIOLET, fill_opacity=1, stroke_width=0), T("负", 22)
                         ).arrange(RIGHT, buff=0.15).next_to(hB, DOWN, buff=0.3)
            self.play(FadeIn(key), run_time=0.6)
        clear(self)

    # ------------------------------------------------------------------ quadratic form
    def quadratic(self):
        tag = self.chapter("一  一道特征值题")
        net = NetView(self.K, self.kpos, color=MUTED, rmin=0.07, rk=0.02, eo=0.4)
        with self.say("s1"):
            self.play(FadeIn(tag), FadeIn(net.group), run_time=1.0)
            s = MathTex(r"\mathbf s=(+1,\,-1,\,+1,\,\dots,\,-1)^{\mathsf T}", font_size=40).move_to(RIGHT * 3.5 + UP * 2.2)
            self.play(Write(s), *[net.dots[v].animate.set_color(BLUE if self.club[v] > 0 else GOLD) for v in self.K], run_time=1.2)
        with self.say("s2"):
            q = MathTex(r"Q=\frac{1}{4m}\,\mathbf s^{\mathsf T} B\,\mathbf s", font_size=52, color=GOLD).next_to(s, DOWN, buff=0.6)
            self.play(Write(q), run_time=1.4)
        with self.say("s2b"):
            qa = T("同组：s_i s_j = 1，B_ij 加进来", 22, BLUE).next_to(q, DOWN, buff=0.35)
            qb = T("异组：s_i s_j = −1，B_ij 减掉", 22, GOLD).next_to(qa, DOWN, buff=0.15).align_to(qa, LEFT)
            self.play(net.group.animate.set_opacity(0.2), FadeIn(qa), run_time=0.6)
            self.wait(1.0)
            self.play(FadeIn(qb), run_time=0.6)
        self.play(FadeOut(qa), FadeOut(qb), net.group.animate.set_opacity(1), run_time=0.4)
        with self.say("s3"):
            e = MathTex(r"B\,\mathbf u_1=\beta_1\mathbf u_1", font_size=46).next_to(q, DOWN, buff=0.6)
            el = T("最大特征值", 22, MUTED).next_to(e, DOWN, buff=0.15)
            self.play(Write(e), FadeIn(el), run_time=1.4)
        with self.say("s3b"):
            self.play(Indicate(e, color=GOLD), run_time=1.2)
        with self.say("s4"):
            sg = MathTex(r"s_i=\operatorname{sign}(u_{1,i})", font_size=50, color=BLUE).next_to(el, DOWN, buff=0.5)
            self.play(Write(sg), run_time=1.4)
        clear(self)

    # ------------------------------------------------------------------ karate
    def karate(self):
        tag = self.chapter("二  空手道俱乐部")
        K, u = self.K, self.u
        net = NetView(K, self.kpos, color=MUTED, rmin=0.07, rk=0.02, eo=0.4)
        ax = plain_axes([0, 35, 5], [-0.4, 0.4, 0.2], 6.4, 4.8, ynums=[-0.4, -0.2, 0, 0.2, 0.4]).move_to(RIGHT * 3.4 + DOWN * 0.3)
        bars = {}
        for v in K:
            h = u[v]
            r = Rectangle(width=0.13, height=max(abs(ax.c2p(0, h)[1] - ax.c2p(0, 0)[1]), 0.01), fill_color=MUTED, fill_opacity=0.9, stroke_width=0)
            r.move_to(ax.c2p(v + 1, 0), aligned_edge=DOWN if h > 0 else UP)
            bars[v] = r
        xl = T("成员编号", 22, MUTED).next_to(ax, DOWN, buff=0.2)
        with self.say("k1"):
            self.play(FadeIn(tag), FadeIn(net.group), Create(ax), FadeIn(xl), run_time=1.2)
            self.play(LaggedStart(*[GrowFromEdge(bars[v], DOWN if u[v] > 0 else UP) for v in K], lag_ratio=0.04), run_time=2.0)
        col = {v: BLUE if u[v] > 0 else GOLD for v in K}
        with self.say("k2"):
            self.play(*[bars[v].animate.set_color(col[v]) for v in K], run_time=0.8)
            self.play(*[net.dots[v].animate.set_color(col[v]) for v in K], run_time=1.0)
        s = np.sign(u)
        wrong = [v for v in K if s[v] != self.club[v]]
        print(f"[nm] spectral mismatches (1-indexed) {[v + 1 for v in wrong]}, top |u| {[int(v) + 1 for v in np.argsort(-abs(u))[:2]]}")
        with self.say("k3"):
            rings = VGroup(*[Circle(radius=0.26, color=RED, stroke_width=4).move_to(net.dots[v]) for v in wrong])
            nums = VGroup(*[T(f"{v + 1}号", 22, RED).next_to(net.dots[v], UR, buff=0.12) for v in wrong])
            br = VGroup(*[SurroundingRectangle(bars[v], color=RED, buff=0.08) for v in wrong])
            self.play(Create(rings), FadeIn(nums), Create(br), run_time=1.0)
        top = list(np.argsort(-abs(u))[:2])
        with self.say("k4"):
            self.play(FadeOut(rings), FadeOut(nums), FadeOut(br), run_time=0.4)
            r2 = VGroup(*[Circle(radius=0.32, color=INK, stroke_width=4).move_to(net.dots[v]) for v in top])
            n2 = VGroup(*[T(f"{v + 1}号", 24, INK).next_to(net.dots[v], DOWN, buff=0.2) for v in top])
            b2 = VGroup(*[SurroundingRectangle(bars[v], color=INK, buff=0.08) for v in top])
            self.play(Create(r2), FadeIn(n2), Create(b2), run_time=1.0)
        clear(self)

    # ------------------------------------------------------------------ indivisible
    def indivisible(self):
        show_slide(self, ["r1", "v1", "v2", "v3"], "谱方法的三个好性质",
                   ["不需要事先规定组的大小", "会拒绝划分：不该分就不分", "分量大小有意义：接近零的在边界上"], accent=GOLD)
        tag = self.chapter("二  会拒绝划分")
        self.play(FadeIn(tag), run_time=0.4)

        def eig_line(G, center, col):
            _, _, B, _ = mod_matrix(G)
            ev = np.linalg.eigvalsh(B)
            nl = NumberLine(x_range=[-2, 4, 1], length=5.4, color=MUTED, include_numbers=True, font_size=24).move_to(center)
            pts = VGroup(*[Dot(nl.n2p(x), radius=0.07, color=col).shift(UP * 0.22) for x in ev])
            lab = MathTex(r"\beta", font_size=30, color=MUTED).next_to(nl, RIGHT, buff=0.2)
            return VGroup(nl, lab), pts, ev.max()
        Kc = nx.complete_graph(8)
        pc = ring_pos(8, 1.5, LEFT * 3.6 + UP * 0.8)
        vc = NetView(Kc, pc, color=BLUE, rmin=0.12, rk=0.0, eo=0.6)
        lc, ptc, mc = eig_line(Kc, LEFT * 3.6 + DOWN * 2.0, BLUE)
        print(f"[nm] clique max eig {mc:.3f}")
        with self.say("r2"):
            self.play(FadeIn(vc.group), run_time=1.0)
            self.play(Create(lc[0]), FadeIn(lc[1]), FadeIn(ptc), run_time=1.2)
            z = T("没有正特征值", 24, BLUE).next_to(lc, DOWN, buff=0.15)
            self.play(FadeIn(z), run_time=0.6)
        G2 = nx.disjoint_union(nx.complete_graph(5), nx.complete_graph(5)); G2.add_edge(0, 5)
        p2 = {**{i: RIGHT * 2.5 + UP * 0.8 + 0.9 * np.array([np.cos(2 * PI * i / 5 + PI), np.sin(2 * PI * i / 5 + PI), 0]) for i in range(5)},
              **{i + 5: RIGHT * 4.9 + UP * 0.8 + 0.9 * np.array([np.cos(2 * PI * i / 5), np.sin(2 * PI * i / 5), 0]) for i in range(5)}}
        v2 = NetView(G2, p2, color=GOLD, rmin=0.12, rk=0.0, eo=0.6)
        l2, pt2, m2 = eig_line(G2, RIGHT * 3.6 + DOWN * 2.0, GOLD)
        with self.say("r3"):
            self.play(FadeIn(v2.group), run_time=1.0)
            self.play(Create(l2[0]), FadeIn(l2[1]), FadeIn(pt2), run_time=1.2)
            pos_ = T("有正特征值 → 分", 24, GOLD).next_to(l2, DOWN, buff=0.15)
            ind = T("不可分", 30, BLUE, weight=BOLD).next_to(vc.group, UP, buff=0.25)
            self.play(FadeIn(pos_), FadeIn(ind), run_time=0.8)
        clear(self, keep=[tag])
        with self.say("r4"):
            f = MathTex(r"B^{(g)}_{ij}=B_{ij}-\delta_{ij}\sum_{l\in g}B_{il}", font_size=52).shift(UP * 1.2)
            self.play(Write(f), run_time=1.6)
        with self.say("r4b"):
            r = SurroundingRectangle(f[0][-12:], color=GOLD, buff=0.08)
            rl = T("对角线减去的一项", 22, GOLD).next_to(r, UP, buff=0.15)
            self.play(Create(r), FadeIn(rl), run_time=0.8)
            self.wait(1.5)
            st = VGroup(MathTex(r"\Delta Q\le 0", font_size=48, color=RED), T("就停", 30, RED)).arrange(RIGHT, buff=0.3).next_to(f, DOWN, buff=0.8)
            self.play(FadeIn(st), run_time=0.8)
        clear(self, keep=[tag])
        B, m = self.B, self.m

        def split(g):
            Bg = B[np.ix_(g, g)].copy(); Bg -= np.diag(Bg.sum(1))
            w, V = np.linalg.eigh(Bg)
            if w[-1] <= 1e-9:
                return None
            s = np.where(V[:, -1] > 0, 1, -1)
            if s @ Bg @ s / (4 * m) <= 1e-9:
                return None
            return [[g[i] for i in range(len(g)) if s[i] > 0], [g[i] for i in range(len(g)) if s[i] < 0]]
        parts, done = [list(range(34))], []
        while parts:
            p = parts.pop(); r = split(p)
            if r:
                parts += r
            else:
                done.append(p)
        Q = nx.community.modularity(self.K, done)
        print(f"[nm] recursive bisection sizes {[len(d) for d in done]} Q {Q:.3f}")
        cols = [BLUE, GOLD, GREEN, VIOLET, RED, INK]
        net = NetView(self.K, {v: p + RIGHT * 2.5 for v, p in self.kpos.items()}, color=MUTED, rmin=0.07, rk=0.02, eo=0.4)
        with self.say("r5"):
            self.play(FadeIn(net.group), run_time=0.8)
            self.play(*[net.dots[v].animate.set_color(cols[i]) for i, d in enumerate(done) for v in d], run_time=1.2)
            qq = counter(f"{len(done)} 个社团", f"Q ≈ {Q:.2f}", GOLD).to_corner(UR, buff=0.6).shift(DOWN * 0.6)
            self.play(FadeIn(qq), run_time=0.6)
        clear(self)

    # ------------------------------------------------------------------ comparison
    def compare(self):
        tag = self.chapter("三  和其他算法比一比")
        data = [("贪心算法", 0.668, MUTED), ("极值优化", 0.679, VIOLET), ("本文方法", 0.723, GOLD)]
        ax = plain_axes([0, 4, 1], [0, 0.8, 0.2], 6.4, 4.4, ynums=[0, 0.2, 0.4, 0.6, 0.8]).move_to(LEFT * 2.6 + DOWN * 0.4)
        yl = ylabel("模块度 Q", ax)
        cap = T("凝聚态物理合作网络 · 约 2.7 万节点", 24, MUTED).next_to(ax, UP, buff=0.3)
        bars = VGroup()
        for i, (n, q, c) in enumerate(data):
            r = Rectangle(width=1.1, height=ax.c2p(0, q)[1] - ax.c2p(0, 0)[1], fill_color=c, fill_opacity=0.9, stroke_width=0).move_to(ax.c2p(i + 1, 0), aligned_edge=DOWN)
            bars.add(VGroup(r, T(n, 22, INK).next_to(r, DOWN, buff=0.15), T(f"{q:.3f}", 24, c, weight=BOLD).next_to(r, UP, buff=0.1)))
        with self.say("c1"):
            self.play(FadeIn(tag), Create(ax), FadeIn(yl), FadeIn(cap), run_time=1.2)
            six = T("六个网络 · 本文方法均最高", 24, GOLD).to_corner(UR, buff=0.6).shift(DOWN * 0.5)
            self.play(FadeIn(six), run_time=0.6)
        with self.say("c2") as d:
            for b in bars:
                self.play(GrowFromEdge(b[0], DOWN), FadeIn(b[1]), run_time=d * 0.18)
                self.play(FadeIn(b[2]), run_time=0.4)
        # political blogs
        tot = 2.8

        def stack(n, frac, main, other, x, lab):
            h1 = tot * n / 638 * frac
            h2 = tot * n / 638 * (1 - frac)
            r1 = Rectangle(width=1.2, height=h1, fill_color=main, fill_opacity=0.9, stroke_width=0)
            r2 = Rectangle(width=1.2, height=h2, fill_color=other, fill_opacity=0.9, stroke_width=0)
            r1.move_to([x, -2.4, 0], aligned_edge=DOWN); r2.next_to(r1, UP, buff=0)
            t = VGroup(T(f"{n} 个", 22, INK), T(lab, 24, main, weight=BOLD)).arrange(DOWN, buff=0.08).next_to(VGroup(r1, r2), UP, buff=0.15)
            return VGroup(r1, r2, t)
        sA = stack(638, 0.97, RED, BLUE, 3.0, "97% 保守派")
        sB = stack(587, 0.93, BLUE, RED, 5.2, "93% 自由派")
        with self.say("c3"):
            pb = T("政治博客网络 · 1225 个", 24, MUTED).move_to(RIGHT * 4.1 + UP * 2.4)
            self.play(FadeOut(six), FadeIn(pb), run_time=0.6)
            self.play(FadeIn(sA, shift=UP * 0.2), run_time=0.9)
            self.play(FadeIn(sB, shift=UP * 0.2), run_time=0.9)
        with self.say("c4"):
            self.play(FadeOut(VGroup(sA, sB, pb)), run_time=0.5)
            clock = VGroup(Circle(radius=1.0, color=INK, stroke_width=4), Line(ORIGIN, UP * 0.75, color=INK, stroke_width=4),
                           Line(ORIGIN, RIGHT * 0.5, color=GOLD, stroke_width=4)).move_to(RIGHT * 4.0 + UP * 0.4)
            self.play(Create(clock), run_time=0.8)
            self.play(Rotate(clock[1], angle=-2 * PI / 3, about_point=clock[0].get_center()), run_time=1.0)
            cl = T("≈ 20 分钟", 30, GOLD).next_to(clock, DOWN, buff=0.3)
            self.play(FadeIn(cl), run_time=0.5)
        clear(self)

    # ------------------------------------------------------------------ biology
    def biology(self):
        tag = self.chapter("三  回到生物网络")
        G = nx.random_partition_graph([16, 16], 0.38, 0.04, seed=11)
        G = G.subgraph(max(nx.connected_components(G), key=len)).copy()
        G = nx.convert_node_labels_to_integers(G)
        pos = fit(nx.spring_layout(G, seed=4, k=0.5), (-5.6, 5.6, -2.9, 2.5))
        net = NetView(G, pos, color=MUTED, rmin=0.11, rk=0.0, eo=0.4)
        _, _, B, _ = mod_matrix(G)
        u = np.linalg.eigh(B)[1][:, -1]
        u = u / abs(u).max()
        with self.say("b1"):
            self.play(FadeIn(tag), FadeIn(net.group), run_time=1.2)
            self.play(*[net.dots[v].animate.set_color(interpolate_color(ManimColor(GREEN), ManimColor(VIOLET), (u[v] + 1) / 2)) for v in G], run_time=1.2)
        keep = list(self.mobjects)
        self.play(*[FadeOut(m) for m in keep], run_time=0.5)
        with self.say("b1b"):
            self.clip_on("yt_wgcna_bioinformagician.mp4", "center", "视频：Bioinformagician · YouTube", start=30)
        self.clip_off()
        self.play(*[FadeIn(m) for m in keep], run_time=0.5)
        with self.say("b2"):
            ok = T("该分才分", 30, GOLD, weight=BOLD).to_edge(DOWN, buff=0.35)
            self.play(FadeIn(ok), run_time=0.8)
        edge = [v for v in G if abs(u[v]) < 0.25]
        with self.say("b3"):
            self.play(FadeOut(ok), run_time=0.3)
            rings = VGroup(*[Circle(radius=0.25, color=GOLD, stroke_width=4).move_to(net.dots[v]) for v in edge])
            lab = T("分量接近零：边界节点", 24, GOLD).to_edge(DOWN, buff=0.35)
            self.play(Create(rings), FadeIn(lab), run_time=1.2)
        clear(self)

    # ------------------------------------------------------------------ limits
    def limits(self):
        tag = self.chapter("三  局限")
        R = nx.gnm_random_graph(1000, 2000, seed=1)
        R = R.subgraph(max(nx.connected_components(R), key=len)).copy()
        com = nx.community.louvain_communities(R, seed=1)
        Q = nx.community.modularity(R, com)
        print(f"[nm] random graph Q {Q:.3f} with {len(com)} communities, n={R.number_of_nodes()}")
        pos = fit(nx.spring_layout(R, seed=2, iterations=60), (-6.2, 0.6, -3.0, 2.6))
        net = NetView(R, pos, color=MUTED, rmin=0.03, rk=0.0, ew=0.5, eo=0.25)
        cols = [BLUE, GOLD, GREEN, VIOLET, RED, INK, "#5ad1d1", "#ff9f6b"]
        with self.say("l1"):
            self.play(FadeIn(tag), FadeIn(net.group), run_time=1.6)
            cap = T("随机图 · 约 1000 个节点", 24, MUTED).move_to(RIGHT * 3.8 + UP * 1.6)
            self.play(FadeIn(cap), run_time=0.6)
        with self.say("l2"):
            self.play(*[net.dots[v].animate.set_color(cols[i % len(cols)]) for i, c in enumerate(com) for v in c], run_time=1.6)
            qq = counter("优化出的模块度", f"Q ≈ {Q:.2f}", RED).next_to(cap, DOWN, buff=0.5)
            self.play(FadeIn(qq), run_time=0.6)
        clear(self, keep=[tag])
        ax = plain_axes([0, 10, 1], [0, 1, 0.5], 9.0, 3.6).shift(DOWN * 0.6)
        xl = T("不同的划分", 22, MUTED).next_to(ax, DOWN, buff=0.2)
        yl = ylabel("Q", ax)
        land = ax.plot(lambda x: 0.55 + 0.18 * np.exp(-((x - 2.5) ** 2) / 0.4) + 0.17 * np.exp(-((x - 5.0) ** 2) / 0.5)
                       + 0.18 * np.exp(-((x - 7.6) ** 2) / 0.35) - 0.4 * np.exp(-((x - 0.2) ** 2) / 0.8), x_range=[0, 10, 0.02], color=GOLD, stroke_width=4)
        with self.say("l3"):
            self.play(Create(ax), FadeIn(xl), FadeIn(yl), run_time=0.8)
            self.play(Create(land), run_time=1.6)
            pk = VGroup(*[Dot(ax.c2p(x, land.underlying_function(x)), radius=0.1, color=RED) for x in (2.5, 5.0, 7.6)])
            pl = T("得分相近，结构不同", 24, RED).next_to(ax.c2p(5.0, 0.9), UP, buff=0.1)
            self.play(FadeIn(pk), FadeIn(pl), run_time=0.8)
        clear(self, keep=[tag])
        with self.say("l4"):
            tl = NumberLine(x_range=[2006, 2012, 1], length=9, color=MUTED, include_numbers=False).shift(DOWN * 0.4)
            ys = VGroup(*[T(str(y), 22, MUTED).next_to(tl.n2p(y), DOWN, buff=0.2) for y in (2006, 2008, 2011)])
            m0 = VGroup(Dot(tl.n2p(2006), color=GOLD), T("谱方法", 24, GOLD).next_to(tl.n2p(2006), UP, buff=0.3))
            m1 = VGroup(Dot(tl.n2p(2008), color=GREEN), T("快速算法：上亿节点", 24, GREEN).next_to(tl.n2p(2008), UP, buff=0.3))
            m2 = VGroup(Dot(tl.n2p(2011), color=BLUE), T("随机块模型：统计推断", 24, BLUE).next_to(tl.n2p(2011), UP, buff=0.9))
            self.play(Create(tl), FadeIn(ys), FadeIn(m0), run_time=1.0)
            self.play(FadeIn(m1), run_time=0.8)
            self.play(FadeIn(m2), run_time=0.8)
        clear(self)
