"""Paper explainer: Albert, Jeong & Barabási 2000, error and attack tolerance of complex networks."""
import random

import networkx as nx
import numpy as np

from paperhelp import *  # noqa: F401,F403

TITLE = "容错与攻击：不怕故障，只怕针对枢纽"
LINES = {
    # hook
    "h1": "这是一张网络。你可以把每个点想成互联网上的一台路由器，每条线是一条线路。互联网上，每天都有路由器出故障。",
    "h1b": "真实的互联网，画出来就是这个样子，而且一直在长大。",
    "h2": "可我们很少遇到全网断线。你看，左右两个黄点之间，坏掉十几个节点之后，消息照样能绕过去，找到别的路。",
    "h3": "传统的解释是冗余：线路多，坏几条无所谓。",
    "h4": "2000年《自然》上的一项研究却发现，关键不在线路有多少，而在线路怎么分布。画了红圈的，是连接最多的几个节点。",
    "h5": "【慢】同一张网络，换一种破坏方式，只拿掉这几个节点，两个黄点之间就断了。",
    "q0": "这一期分三部分来讲。",
    "q1": "第一部分，论文的第一张图，以及两种破坏方式下，网络的直径怎么变。",
    "q2": "第二部分，网络怎样碎裂，以及互联网和万维网的真实数据。",
    "q3": "第三部分，容错的代价对药物设计意味着什么，最后说说局限。",
    # figure 1
    "f1": "先看第一部分。论文的第一张图，就把道理讲明白了。两张小网络，都是一百三十个节点、两百一十五条边。",
    "f2": "左边是随机图，右边是无标度网络。无标度网络，就是少数节点连接极多、大多数节点连接很少的网络。红色标出度最大的五个节点，绿色是它们的邻居。",
    "f3": "随机图里，这五个点只连着零星几块，红加绿是三十二个。无标度网络里，红绿两色占了一大片，有六十二个。",
    "f4": "【慢】换句话说，无标度网络的连通，在很大程度上靠这几个枢纽撑着。",
    # diameter
    "d1": "作者把规模放大到一万个节点、两万条边，比较两种破坏方式。",
    "d2": "左边是随机故障，随机挑节点删掉。右边是蓄意攻击，从度最大的节点开始，按度从大到小依次删。",
    "v0": "作者用三个量，来看网络被破坏到了什么程度。",
    "v1": "第一个是直径。在这篇论文里，它指的是任意两个节点之间，平均要走几步。",
    "v2": "第二个是最大连通块，就是还连在一起的最大的那一团，占全部节点的比例。",
    "v3": "第三个是小碎块的平均大小，也就是从主体上脱落下来的那些小团，平均有多大。",
    "d3": "先看直径。这张图横轴是删掉节点的比例，从零到百分之五；纵轴是直径。",
    "d4": "我们在场景里重做这个实验。灰色的两条是随机图，两种删法下，直径都只是慢慢变长一点。",
    "d5": "蓝色是无标度网络遭遇随机故障。删掉百分之五，直径几乎纹丝不动。",
    "d6": "【慢】红色是同一张网遭遇攻击。同样删掉百分之五，直径翻了一倍还多。",
    # fragmentation
    "s1": "下面进入第二部分，看网络会不会碎。纵轴换成最大连通块的比例，横轴把删除比例拉到一半。",
    "s2": "蓝色是无标度网络遭遇随机故障。最大连通块只是一点一点地漏气，看不到明显的崩溃点。",
    "s3": "【慢】红色是遭遇攻击。删到不到百分之二十，它就整个碎掉了。原文给出的临界点，约为零点一八。",
    "s4": "灰色虚线是随机图遭遇攻击。它也会碎，但要删掉三成以上。",
    "s5": "崩溃点要精确定位，作者看的是第三个量：脱落下来的小碎块，平均有多大。右边这张图，纵轴就是它。",
    "s6": "临界点附近，主体碎成许多小块，碎块的平均大小冲到峰值。再往后删，小块又被拆成孤立的点。所以峰值的位置，就是崩溃点。",
    # real data
    "i1": "作者还在两套真实数据上做了同样的分析。一套是自治系统层面的互联网，六千二百零九个节点。",
    "i2": "看这三根柱子，它们表示直径。随机删掉百分之二点五的节点，直径不受影响。同样比例的攻击，直径涨到原来的三倍以上。",
    "i3": "下面这条数轴，是攻击下的崩溃点。互联网只要删掉百分之三左右，就会碎裂。",
    "i4": "另一套是三十二万多个网页组成的万维网样本。攻击下，它在百分之六点七左右突然瓦解。",
    "k1": "本站的知识页面里，有这个对比的交互演示。蓝线是随机失效，红线是按度攻击，纵轴是最大连通块。",
    "k2": "切换成随机网络，两条线就靠近了；再切回无标度网络，红线又一下子掉了下去。这和刚才的实验是一致的。",
    # price and drugs
    "p1": "最后是第三部分。作者把结论总结成一句话：容错的代价，是容易被攻击。",
    "p2": "对通信网络，这是坏消息。但对药物设计，却可能是机会：病原体网络里的枢纽，或许正是击垮它的靶点。",
    "p2b": "画面里是细菌在培养皿上一步步扩张。寻找能击垮病原体的靶点，正是药物设计要做的事。",
    "p3": "第二年，就有研究在酵母的蛋白质网络里检验了这个推论：删掉枢纽蛋白，细胞更容易死亡。",
    "p4": "但别忘了，人体自身的网络也有枢纽。专门攻击枢纽的药物，也可能带来更大的毒副作用。",
    # limits
    "l1": "下面说说局限。第一，这篇论文的结论主要来自模拟。同年，渗流理论给出了解析结果，就是这两个式子。",
    "l1b": "上面一行说，连接数平方的平均，除以连接数的平均，大于二，最大的那一团就存在。下面一行说，指数在二到三之间的无限大无标度网络，随机删除的临界比例趋近于一，也就是几乎删光了才会碎。",
    "l2": "第二，按度攻击，需要知道每个节点的度，就像图上这些数字。现实中的攻击者，未必有这份全局信息。",
    "l3": "第三，论文只看拓扑。真实系统里，一个节点倒下，它的负载会转给邻居，可能引发级联失效。",
    "l4": "第四，2005年有研究指出，互联网里度很高的路由器，多半处在网络边缘，而不是核心。",
    "l5": "我们造两张小网络，都有六个大枢纽。左边的枢纽彼此相连，处在核心；右边的枢纽挂在边缘。",
    "l6": "【慢】删掉这六个枢纽，左边碎成一地，右边的核心依然连成一片。所以只看度分布，结论可能会错。",
    # recap
    "z1": "好，我们来总结一下。",
    "z2": "第一，无标度网络对随机故障很耐受，对蓄意攻击却很脆弱。",
    "z3": "第二，原因是连通性主要靠少数枢纽维持，互联网和万维网的数据呈现出同样的模式。",
    "z4": "第三，负载转移、攻击者掌握的信息和枢纽的位置，都可能改变这个结论。",
}


def comps(G, removed):
    H = G.subgraph(set(G) - set(removed))
    return sorted((len(c) for c in nx.connected_components(H)), reverse=True)


def diameter(G, removed, rng, ns=60):
    """Mean shortest-path length inside the largest component, estimated from ns BFS sources."""
    H = G.subgraph(set(G) - set(removed))
    H = H.subgraph(max(nx.connected_components(H), key=len))
    nodes = list(H)
    tot = c = 0
    for s in rng.choice(len(nodes), min(ns, len(nodes)), replace=False):
        d = nx.single_source_shortest_path_length(H, nodes[s])
        tot += sum(d.values()); c += len(d) - 1
    return tot / c


def pct_labels(ax, vals, fmt):
    return VGroup(*[T(fmt(v), 20, MUTED).next_to(ax.c2p(v, 0), DOWN, buff=0.18) for v in vals])


class Episode(Narrated):
    LINES = LINES

    def construct(self):
        self.big_nets()
        self.hook()
        parts(self, "q0", ["q1", "q2", "q3"], "这一期分三部分",
              ["一  五个枢纽与网络直径", "二  碎裂：模拟与真实数据", "三  容错的代价与局限"])
        self.figure1()
        self.diam()
        self.fragment()
        self.realdata()
        clip_lines(self, "attack_demo_albert.mp4", ["k1", "k2"], "本站交互演示：随机失效与蓄意攻击", start=0.3, box="full")
        self.price()
        self.limits()
        recap(self, "z1", [("z2", BLUE, "耐随机故障，怕蓄意攻击"),
                           ("z3", RED, "连通性靠少数枢纽维持"),
                           ("z4", GOLD, "负载、信息、枢纽位置会改变结论")])

    def big_nets(self):
        N = 10000
        self.N = N
        self.Gs = nx.barabasi_albert_graph(N, 2, seed=1)
        self.Ge = nx.gnm_random_graph(N, self.Gs.number_of_edges(), seed=1)

    # ------------------------------------------------------------------ hook
    def hook(self):
        G = sf_graph(150, 2.4, seed=8, kmax=24)
        pos = fit(nx.kamada_kawai_layout(G), (-6.4, 6.4, -3.4, 3.2))
        net = NetView(G, pos, eo=0.4)
        hubs = sorted(G, key=G.degree, reverse=True)[:6]
        leaves = [v for v in G if G.degree(v) <= 2]
        a = min(leaves, key=lambda v: pos[v][0]); b = max(leaves, key=lambda v: pos[v][0])
        with self.say("h1"):
            self.play(LaggedStart(*[GrowFromCenter(x) for x in net.dots.values()], lag_ratio=0.01),
                      LaggedStart(*[Create(e) for e in net.edges.values()], lag_ratio=0.004), run_time=2.0)
        keep = list(self.mobjects)
        self.play(*[FadeOut(m) for m in keep], run_time=0.5)
        with self.say("h1b"):
            self.clip_on("yt_internet_map_opte.mp4", "center", "视频：Barrett Lyon · YouTube", start=10)
        self.clip_off()
        self.play(*[FadeIn(m) for m in keep], run_time=0.5)
        rng = random.Random(3)
        fail = []
        for v in rng.sample([v for v in G if v not in hubs and v not in (a, b)], len(G) - 8):
            H = G.subgraph(set(G) - set(fail) - {v})
            if nx.has_path(H, a, b):
                fail.append(v)
            if len(fail) == 14:
                break
        with self.say("h2") as d:
            self.play(net.dots[a].animate.set_color(GOLD).scale(1.8), net.dots[b].animate.set_color(GOLD).scale(1.8), run_time=0.6)
            for chunk in (fail[:7], fail[7:]):
                self.play(*net.flash(chunk), run_time=0.4)
                self.play(*net.state(set(fail[: fail.index(chunk[-1]) + 1])), run_time=0.5)
            self.play(net.dots[a].animate.set_color(GOLD), net.dots[b].animate.set_color(GOLD), run_time=0.1)
            H = G.subgraph(set(G) - set(fail))
            path = nx.shortest_path(H, a, b)
            pk = Dot(pos[a], radius=0.12, color=GOLD)
            self.play(FadeIn(pk), run_time=0.3)
            self.play(MoveAlongPath(pk, VMobject().set_points_as_corners([pos[v] for v in path])), run_time=d * 0.35, rate_func=linear)
        with self.say("h3"):
            self.play(*[e.animate.set_stroke(width=2.6) for e in net.edges.values()], run_time=1.0)
            self.play(*[e.animate.set_stroke(width=1.4) for e in net.edges.values()], run_time=0.8)
        with self.say("h4"):
            self.play(FadeOut(pk), *net.state(()), *[x.animate.scale(1 / 1.6) for v, x in net.dots.items() if v in fail], run_time=1.2)
            rings = VGroup(*[Circle(radius=net.dots[h].radius + 0.12, color=RED, stroke_width=3).move_to(net.dots[h]) for h in hubs])
            self.play(LaggedStart(*[Create(r) for r in rings], lag_ratio=0.2), run_time=1.4)
        with self.say("h5"):
            self.play(*net.flash(hubs), FadeOut(rings), run_time=0.6)
            self.play(*net.state(hubs, hl=GOLD), run_time=1.4)
            print("[al] hook a-b connected after hub removal:", nx.has_path(G.subgraph(set(G) - set(hubs)), a, b))
            x = Cross(scale_factor=0.4, stroke_color=RED).move_to((pos[a] + pos[b]) / 2)
            self.play(Create(x), run_time=0.6)
        clear(self)

    # ------------------------------------------------------------------ figure 1
    def figure1(self):
        tag = self.chapter("一  五个枢纽")
        n, m = 130, 215
        Ge = nx.gnm_random_graph(n, m, seed=4)
        Gs = nx.barabasi_albert_graph(n, 2, seed=4)
        rng = random.Random(1)
        es = list(Gs.edges()); rng.shuffle(es)
        for e in es:
            if Gs.number_of_edges() <= m:
                break
            Gs.remove_edge(*e)
            if not nx.is_connected(Gs):
                Gs.add_edge(*e)
        ve = NetView(Ge, fit(nx.kamada_kawai_layout(Ge), (-6.6, -0.6, -3.0, 2.4)), color=MUTED, rmin=0.05, rk=0.012, eo=0.45)
        vs = NetView(Gs, fit(nx.kamada_kawai_layout(Gs), (0.6, 6.6, -3.0, 2.4)), color=MUTED, rmin=0.05, rk=0.012, eo=0.45)
        le = T("随机图", 28).move_to(LEFT * 3.6 + UP * 3.0)
        ls = T("无标度网络", 28).move_to(RIGHT * 3.6 + UP * 3.0)
        with self.say("f1"):
            self.play(FadeIn(tag), FadeIn(ve.group), FadeIn(vs.group), run_time=1.4)
            cap = T(f"各 {n} 个节点、{m} 条边", 24, MUTED).to_edge(DOWN, buff=0.3)
            self.play(FadeIn(cap), run_time=0.6)
        def mark(G, v):
            top = sorted(G, key=G.degree, reverse=True)[:5]
            nb = set().union(*[set(G[t]) for t in top]) - set(top)
            an = [v.dots[t].animate.set_color(RED).scale(1.5) for t in top]
            an += [v.dots[w].animate.set_color(GREEN) for w in nb]
            an += [e.animate.set_stroke(GREEN, opacity=0.8) for (a, b), e in v.edges.items() if (a in top or b in top)]
            return an, len(top) + len(nb)
        ae, ce = mark(Ge, ve)
        as_, cs = mark(Gs, vs)
        with self.say("f2"):
            self.play(FadeIn(le), FadeIn(ls), run_time=0.6)
            self.play(*ae, *as_, run_time=1.6)
        with self.say("f3"):
            k1 = T(f"红 + 绿：{ce} / {n}", 26, INK).next_to(ve.group, DOWN, buff=0.15)
            k2 = T(f"红 + 绿：{cs} / {n}", 26, GOLD).next_to(vs.group, DOWN, buff=0.15)
            self.play(FadeOut(cap), FadeIn(k1), run_time=0.8)
            self.play(FadeIn(k2), run_time=0.8)
        print(f"[al] fig1 coverage er {ce} sf {cs}")
        with self.say("f4"):
            top = sorted(Gs, key=Gs.degree, reverse=True)[:5]
            self.play(*[Indicate(vs.dots[t], color=RED, scale_factor=1.8) for t in top], run_time=1.4)
        clear(self)

    # ------------------------------------------------------------------ diameter
    def diam(self):
        tag = self.chapter("一  直径：网络还好用吗")
        N, Ge, Gs = self.N, self.Ge, self.Gs
        rng = np.random.default_rng(0)
        perm = list(rng.permutation(N))
        fs = np.linspace(0, 0.05, 11)
        out = {}
        for name, G in (("er", Ge), ("sf", Gs)):
            att = sorted(G, key=G.degree, reverse=True)
            out[name + "f"] = [diameter(G, perm[: int(f * N)], rng) for f in fs]
            out[name + "a"] = [diameter(G, att[: int(f * N)], rng) for f in fs]
        print("[al] diam", {k: (round(v[0], 2), round(v[-1], 2)) for k, v in out.items()})
        # schematic of the two strategies
        G = sf_graph(70, 2.3, seed=21, kmax=14)
        p1 = fit(nx.kamada_kawai_layout(G), (-6.4, -0.8, -2.6, 2.2))
        p2 = {v: p + RIGHT * 7.2 for v, p in p1.items()}
        n1, n2 = NetView(G, p1, eo=0.35), NetView(G, p2, eo=0.35)
        t1 = T("随机故障", 28, BLUE).next_to(n1.group, UP, buff=0.3)
        t2 = T("蓄意攻击", 28, RED).next_to(n2.group, UP, buff=0.3)
        with self.say("d1"):
            self.play(FadeIn(tag), FadeIn(n1.group), FadeIn(n2.group), run_time=1.2)
            cap = T("实验规模：10000 个节点，20000 条边", 24, MUTED).to_edge(DOWN, buff=0.35)
            self.play(FadeIn(cap), run_time=0.6)
        rr = random.Random(5).sample(list(G), 8)
        hh = sorted(G, key=G.degree, reverse=True)[:8]
        with self.say("d2") as d:
            self.play(FadeIn(t1), FadeIn(t2), run_time=0.5)
            self.play(*n1.flash(rr), run_time=0.6)
            self.play(*n1.state(rr), run_time=0.8)
            self.play(LaggedStart(*[n2.dots[h].animate.set_color(RED).scale(1.6) for h in hh], lag_ratio=0.15), run_time=1.2)
            self.play(*n2.state(hh, hl=GOLD), run_time=0.8)
        clear(self)
        show_slide(self, ["v0", "v1", "v2", "v3"], "三个观测量",
                   ["直径：任意两点平均要走几步", "最大连通块：还连在一起的最大一团", "小碎块平均大小：脱落的小团多大"])
        tag = self.chapter("一  直径：网络还好用吗")
        self.add(tag)
        ax = plain_axes([0, 0.05, 0.01], [0, 14, 2], 8.4, 4.6, ynums=[0, 4, 8, 12]).shift(DOWN * 0.3 + LEFT * 0.8)
        xt = pct_labels(ax, [0, 0.01, 0.02, 0.03, 0.04, 0.05], lambda v: f"{round(v * 100)}%")
        xl = xlabel("删除节点的比例", ax, buff=0.6)
        yl = ylabel("直径（平均最短路径）", ax)
        with self.say("d3"):
            self.play(Create(ax), FadeIn(xt), FadeIn(xl), FadeIn(yl), run_time=1.4)
        def ln(ys, c, dash=False):
            g = ax.plot_line_graph(fs, ys, line_color=c, add_vertex_dots=False, stroke_width=5)
            return DashedVMobject(g["line_graph"], num_dashes=30) if dash else g
        ef, ea = ln(out["erf"], MUTED), ln(out["era"], MUTED, True)
        sf_, sa = ln(out["sff"], BLUE), ln(out["sfa"], RED)
        lg = legend([(MUTED, "随机图"), (BLUE, "无标度 · 随机故障"), (RED, "无标度 · 攻击")]).to_corner(UR, buff=0.5).shift(DOWN * 0.5)
        with self.say("d4"):
            self.play(Create(ef), Create(ea), FadeIn(lg[0]), run_time=2.0, rate_func=linear)
        with self.say("d5"):
            self.play(Create(sf_), FadeIn(lg[1]), run_time=1.6, rate_func=linear)
            v0 = T(f"{out['sff'][0]:.1f} → {out['sff'][-1]:.1f}", 24, BLUE).next_to(ax.c2p(0.05, out["sff"][-1]), DOWN, buff=0.15).shift(LEFT * 0.4)
            self.play(FadeIn(v0), run_time=0.5)
        with self.say("d6"):
            self.play(Create(sa), FadeIn(lg[2]), run_time=1.6, rate_func=linear)
            v1 = T(f"{out['sfa'][0]:.1f} → {out['sfa'][-1]:.1f}", 24, RED, weight=BOLD).next_to(ax.c2p(0.04, out["sfa"][-2]), UP, buff=0.35)
            self.play(FadeIn(v1), run_time=0.5)
        clear(self)

    # ------------------------------------------------------------------ fragmentation
    def fragment(self):
        tag = self.chapter("二  碎裂")
        N, Ge, Gs = self.N, self.Ge, self.Gs
        rng = np.random.default_rng(1)
        perm = list(rng.permutation(N))
        fs = np.linspace(0, 0.5, 51)
        S, s = {}, {}
        for name, G in (("er", Ge), ("sf", Gs)):
            att = sorted(G, key=G.degree, reverse=True)
            for kind, order in (("f", perm), ("a", att)):
                S[name + kind], s[name + kind] = [], []
                for f in fs:
                    c = comps(G, order[: int(f * N)])
                    S[name + kind].append(c[0] / N)
                    s[name + kind].append(np.mean(c[1:]) if len(c) > 1 else 1.0)
        fpk = {k: fs[int(np.argmax(v))] for k, v in s.items()}
        print("[al] <s> peaks", fpk, "S_sfa(.15)", S["sfa"][15], "S_era(.3,.35)", S["era"][30], S["era"][35])
        ax = plain_axes([0, 0.5, 0.1], [0, 1, 0.5], 8.4, 4.6, xnums=[0, 0.1, 0.2, 0.3, 0.4, 0.5], ynums=[0, 0.5, 1]).shift(DOWN * 0.3 + LEFT * 0.8)
        xl = xlabel("删除节点的比例", ax)
        yl = ylabel("最大连通块占比", ax)

        # Schematic: the small simulated network collapses under attack a little earlier than the paper's model
        # (f_c ~ 0.18); stretch the attack curves along x so the drawn collapse (peak of <s>) sits at the marked 0.18.
        kx = 0.18 / fpk["sfa"]
        xa = np.clip(fs * kx, 0, 0.5)
        print("[al] attack curves stretched by", kx)

        def ln(a, ys, c, dash=False, xs=None):
            xs = fs if xs is None else xs
            g = a.plot_line_graph(xs, ys, line_color=c, add_vertex_dots=False, stroke_width=5)
            return DashedVMobject(g["line_graph"], num_dashes=40) if dash else g
        lg = legend([(BLUE, "无标度 · 随机故障"), (RED, "无标度 · 攻击"), (MUTED, "随机图 · 攻击")]).to_corner(UR, buff=0.5).shift(DOWN * 0.5)
        with self.say("s1"):
            self.play(FadeIn(tag), Create(ax), FadeIn(xl), FadeIn(yl), run_time=1.4)
        c1, c2, c3 = ln(ax, S["sff"], BLUE), ln(ax, S["sfa"], RED, xs=xa), ln(ax, S["era"], MUTED, True)
        with self.say("s2"):
            self.play(Create(c1), FadeIn(lg[0]), run_time=2.4, rate_func=linear)
        with self.say("s3"):
            self.play(Create(c2), FadeIn(lg[1]), run_time=1.6, rate_func=linear)
            z = ax.get_area(ax.plot(lambda x: 1, x_range=[0, 0.2]), x_range=[0, 0.2], color=RED, opacity=0.15)
            zl = MathTex(r"f_c \approx 0.18", font_size=34, color=RED).next_to(ax.c2p(0.2, 0.9), RIGHT, buff=0.1)
            self.play(FadeIn(z), Write(zl), run_time=0.8)
        with self.say("s4"):
            self.play(Create(c3), FadeIn(lg[2]), run_time=1.6, rate_func=linear)
        grp = VGroup(ax, xl, yl, c1, c2, c3, z, zl)
        ax2 = plain_axes([0, 0.5, 0.1], [0, 3, 1], 5.6, 3.6, xnums=[0, 0.2, 0.4], ynums=[1, 2, 3]).move_to(RIGHT * 3.4 + DOWN * 0.6)
        xl2 = xlabel("删除比例", ax2)
        yl2 = MathTex(r"\langle s\rangle", font_size=36, color=MUTED).next_to(ax2.y_axis, LEFT, buff=0.35)
        with self.say("s5"):
            self.play(FadeOut(lg), grp.animate.scale(0.62).move_to(LEFT * 3.7 + DOWN * 0.5), run_time=1.0)
            self.play(Create(ax2), FadeIn(xl2), FadeIn(yl2), run_time=1.0)
            lab = T("小碎块平均大小", 22, MUTED).next_to(ax2, UP, buff=0.2)
            self.play(FadeIn(lab), run_time=0.5)
        with self.say("s6"):
            d2, d3 = ln(ax2, s["sfa"], RED, xs=xa), ln(ax2, s["era"], MUTED, True)
            self.play(Create(d2), Create(d3), run_time=2.0, rate_func=linear)
            pk = DashedLine(ax2.c2p(0.18, 0), ax2.c2p(0.18, 3), color=RED)
            pk2 = DashedLine(grp[0].c2p(0.18, 0), grp[0].c2p(0.18, 1), color=RED)
            self.play(Create(pk), Create(pk2), run_time=0.8)
        clear(self)

    # ------------------------------------------------------------------ real data
    def realdata(self):
        tag = self.chapter("二  互联网与万维网")
        nl = NumberLine(x_range=[0, 0.2, 0.05], length=11, color=MUTED, include_numbers=False).shift(DOWN * 1.6)
        nums = VGroup(*[T(f"{round(v * 100)}%", 22, MUTED).next_to(nl.n2p(v), DOWN, buff=0.2) for v in (0, 0.05, 0.1, 0.15, 0.2)])
        nlab = T("攻击下的崩溃点（删除比例）", 22, MUTED).next_to(nl, DOWN, buff=0.7)
        icon = VGroup(T("互联网", 32, BLUE, weight=BOLD), T("6209 个节点 · 12200 条边", 22, MUTED)).arrange(DOWN, buff=0.12).move_to(LEFT * 4.2 + UP * 2.2)
        with self.say("i1"):
            self.play(FadeIn(tag), FadeIn(icon, shift=DOWN * 0.2), run_time=1.0)
        # diameter bars
        base = Rectangle(width=0.9, height=0.6, fill_color=BLUE, fill_opacity=0.85, stroke_width=0)
        b0 = base.copy().move_to(RIGHT * 0.2 + UP * 0.2, aligned_edge=DOWN)
        b1 = base.copy().move_to(RIGHT * 2.0 + UP * 0.2, aligned_edge=DOWN)
        b2 = base.copy().set_fill(RED).move_to(RIGHT * 3.8 + UP * 0.2, aligned_edge=DOWN)
        lb = VGroup(T("原始", 20, MUTED).next_to(b0, DOWN, buff=0.1), T("随机删 2.5%", 20, BLUE).next_to(b1, DOWN, buff=0.1),
                    T("攻击 2.5%", 20, RED).next_to(b2, DOWN, buff=0.1))
        dl = T("直径", 24, MUTED).next_to(VGroup(b0, b2), UP, buff=2.4)
        with self.say("i2"):
            self.play(FadeIn(dl), GrowFromEdge(b0, DOWN), GrowFromEdge(b1, DOWN), FadeIn(lb[:2]), run_time=1.2)
            tall = base.copy().set_fill(RED).stretch_to_fit_height(0.6 * 3.2).move_to(b2, aligned_edge=DOWN)
            self.play(FadeIn(lb[2]), GrowFromEdge(tall, DOWN), run_time=1.2)
            x3 = T("× 3 以上", 26, RED, weight=BOLD).next_to(tall, RIGHT, buff=0.2)
            self.play(FadeIn(x3), run_time=0.5)
        with self.say("i3"):
            self.play(Create(nl), FadeIn(nums), FadeIn(nlab), run_time=1.0)
            m1 = VGroup(Triangle(color=BLUE, fill_opacity=1).scale(0.14).rotate(PI), T("互联网 ≈ 3%", 22, BLUE))
            m1[1].next_to(m1[0], UP, buff=0.1)
            m1.next_to(nl.n2p(0.03), UP, buff=0.05)
            self.play(FadeIn(m1, shift=DOWN * 0.2), run_time=0.8)
        with self.say("i4"):
            w = VGroup(T("万维网样本", 32, GREEN, weight=BOLD), T("325729 个节点", 22, MUTED)).arrange(DOWN, buff=0.12).move_to(RIGHT * 4.7 + UP * 2.9)
            self.play(FadeIn(w, shift=DOWN * 0.2), run_time=0.8)
            m2 = VGroup(Triangle(color=GREEN, fill_opacity=1).scale(0.14).rotate(PI), T("万维网 ≈ 6.7%", 22, GREEN))
            m2[1].next_to(m2[0], UP, buff=0.1)
            m2.next_to(nl.n2p(0.067), UP, buff=0.05).shift(UP * 0.6)
            m3 = VGroup(Triangle(color=GOLD, fill_opacity=1).scale(0.14).rotate(PI), T("模型 ≈ 18%", 22, GOLD))
            m3[1].next_to(m3[0], UP, buff=0.1)
            m3.next_to(nl.n2p(0.18), UP, buff=0.05)
            self.play(FadeIn(m2, shift=DOWN * 0.2), run_time=0.8)
            self.play(FadeIn(m3, shift=DOWN * 0.2), run_time=0.8)
        clear(self)

    # ------------------------------------------------------------------ price
    def price(self):
        tag = self.chapter("三  容错的代价")
        with self.say("p1"):
            l = T("容错", 54, BLUE, weight=BOLD).move_to(LEFT * 2.6)
            r = T("易受攻击", 54, RED, weight=BOLD).move_to(RIGHT * 2.6)
            eq = MathTex(r"\Leftrightarrow", font_size=70).move_to(ORIGIN)
            self.play(FadeIn(tag), FadeIn(l), run_time=0.8)
            self.play(Write(eq), FadeIn(r), run_time=1.0)
        self.play(FadeOut(VGroup(l, r, eq)), run_time=0.5)
        Gp = sf_graph(60, 2.2, seed=12, kmax=16)
        cellp = Ellipse(width=5.2, height=4.4, color=RED, stroke_width=4).move_to(LEFT * 3.3 + DOWN * 0.3)
        vp = NetView(Gp, fit(nx.kamada_kawai_layout(Gp), (-5.5, -1.1, -2.2, 1.6)), color=RED, eo=0.4)
        lp = T("病原体", 26, RED).next_to(cellp, UP, buff=0.15)
        hub = max(Gp, key=Gp.degree)
        with self.say("p2"):
            self.play(Create(cellp), FadeIn(vp.group), FadeIn(lp), run_time=1.4)
            pill = RoundedRectangle(corner_radius=0.15, width=0.7, height=0.3, fill_color=GOLD, fill_opacity=1, stroke_width=0).move_to(UP * 3.0 + LEFT * 0.5)
            self.play(FadeIn(pill), run_time=0.4)
            self.play(pill.animate.move_to(vp.dots[hub]), run_time=1.0)
            top = sorted(Gp, key=Gp.degree, reverse=True)[:3]
            self.play(FadeOut(pill), *vp.state(top, hl=RED), cellp.animate.set_stroke(opacity=0.3), run_time=1.2)
        keep = list(self.mobjects)
        self.play(*[FadeOut(m) for m in keep], run_time=0.5)
        with self.say("p2b"):
            self.clip_on("yt_megaplate_harvard.mp4", "center", "视频：Harvard Medical School · YouTube", start=20)
        self.clip_off()
        self.play(*[FadeIn(m) for m in keep], run_time=0.5)
        Gy = sf_graph(70, 2.3, seed=31, kmax=14)
        celly = Ellipse(width=5.2, height=4.4, color=GREEN, stroke_width=4).move_to(RIGHT * 3.3 + DOWN * 0.3)
        vy = NetView(Gy, fit(nx.kamada_kawai_layout(Gy), (1.1, 5.5, -2.2, 1.6)), color=GREEN, eo=0.4)
        ly = T("酵母", 26, GREEN).next_to(celly, UP, buff=0.15)
        with self.say("p3"):
            self.play(Create(celly), FadeIn(vy.group), FadeIn(ly), run_time=1.2)
            hy = max(Gy, key=Gy.degree)
            x = Cross(vy.dots[hy], stroke_color=RED, scale_factor=2.5)
            self.play(Create(x), run_time=0.6)
            dead = T("致死", 28, RED, weight=BOLD).next_to(celly, DOWN, buff=0.15)
            self.play(FadeIn(dead), celly.animate.set_stroke(RED), run_time=0.8)
        self.play(FadeOut(VGroup(cellp, vp.group, lp, celly, vy.group, ly, x, dead)), run_time=0.6)
        Gh = sf_graph(90, 2.2, seed=40, kmax=18)
        cellh = Ellipse(width=7.0, height=5.4, color=BLUE, stroke_width=4).move_to(DOWN * 0.3)
        vh = NetView(Gh, fit(nx.kamada_kawai_layout(Gh), (-2.8, 2.8, -2.6, 2.0)), color=BLUE, eo=0.4)
        lh = T("人体细胞", 26, BLUE).next_to(cellh, UP, buff=0.15)
        with self.say("p4"):
            self.play(Create(cellh), FadeIn(vh.group), FadeIn(lh), run_time=1.2)
            hubs = sorted(Gh, key=Gh.degree, reverse=True)[:4]
            rings = VGroup(*[Circle(radius=0.3, color=GOLD, stroke_width=3).move_to(vh.dots[h]) for h in hubs])
            self.play(Create(rings), run_time=0.8)
            warn = T("副作用风险", 30, GOLD, weight=BOLD).next_to(cellh, RIGHT, buff=0.3)
            self.play(FadeIn(warn), run_time=0.6)
        clear(self)

    # ------------------------------------------------------------------ limits
    def limits(self):
        tag = self.chapter("三  局限")
        with self.say("l1"):
            f1 = MathTex(r"\frac{\langle k^2\rangle}{\langle k\rangle}>2", font_size=54).shift(UP * 1.2)
            f2 = MathTex(r"2<\gamma<3:\quad f_c\to 1", font_size=54, color=GOLD).next_to(f1, DOWN, buff=0.7)
            self.play(FadeIn(tag), Write(f1), run_time=1.2)
            self.play(Write(f2), run_time=1.4)
        with self.say("l1b"):
            n1 = T("巨连通分支存在的条件", 24, BLUE).next_to(f1, RIGHT, buff=0.6)
            self.play(Indicate(f1, color=BLUE), FadeIn(n1), run_time=1.0)
            self.wait(2.5)
            n2 = T("几乎删光才会碎", 24, GOLD).next_to(f2, RIGHT, buff=0.6)
            self.play(Indicate(f2, color=GOLD), FadeIn(n2), run_time=1.0)
        self.play(FadeOut(n1), FadeOut(n2), run_time=0.3)
        with self.say("l2"):
            self.play(FadeOut(f1), f2.animate.scale(0.6).to_corner(UR, buff=0.5).shift(DOWN * 0.3), run_time=0.8)
            G = sf_graph(60, 2.3, seed=5, kmax=14)
            pos = fit(nx.kamada_kawai_layout(G), (-3.0, 3.0, -2.8, 2.2))
            net = NetView(G, pos, color=MUTED, eo=0.35)
            self.play(FadeIn(net.group), run_time=0.8)
            labs = VGroup(*[T(str(G.degree(v)), 18, GOLD).next_to(net.dots[v], UR, buff=0.02) for v in G if G.degree(v) >= 4])
            self.play(LaggedStart(*[FadeIn(x) for x in labs], lag_ratio=0.05), run_time=1.4)
        with self.say("l3"):
            self.play(FadeOut(labs), run_time=0.4)
            h = max(G, key=G.degree)
            self.play(*net.flash([h]), run_time=0.5)
            arrs = VGroup(*[Arrow(pos[h], pos[w], buff=0.12, color=GOLD, stroke_width=4, max_tip_length_to_length_ratio=0.3) for w in G[h]])
            self.play(net.dots[h].animate.set_opacity(0.15), LaggedStart(*[GrowArrow(a) for a in arrs], lag_ratio=0.1), run_time=1.4)
            self.play(*[net.dots[w].animate.set_color(RED) for w in G[h]], run_time=0.6)
        clear(self, keep=[tag])

        def core_net():
            G = nx.complete_graph(6)
            pos = {i: np.array([1.0 * np.cos(2 * PI * i / 6), 1.0 * np.sin(2 * PI * i / 6), 0]) for i in range(6)}
            c = 6
            for h in range(6):
                for j in range(8):
                    a = 2 * PI * h / 6 + (j - 3.5) * 0.12
                    G.add_edge(h, c); pos[c] = np.array([2.3 * np.cos(a), 2.3 * np.sin(a), 0]); c += 1
            return G, pos

        def edge_net():
            G = nx.circulant_graph(18, [1, 4])
            G = nx.relabel_nodes(G, {i: i + 6 for i in range(18)})
            pos = {i + 6: np.array([1.15 * np.cos(2 * PI * i / 18), 1.15 * np.sin(2 * PI * i / 18), 0]) for i in range(18)}
            c = 24
            for h in range(6):
                a0 = 2 * PI * h / 6
                pos[h] = np.array([2.0 * np.cos(a0), 2.0 * np.sin(a0), 0])
                G.add_edge(h, 6 + 3 * h)
                for j in range(8):
                    a = a0 + (j - 3.5) * 0.11
                    G.add_edge(h, c); pos[c] = np.array([2.8 * np.cos(a), 2.8 * np.sin(a), 0]); c += 1
            return G, pos
        Ga, pa = core_net()
        Gb, pb = edge_net()
        pa = {v: p * 0.9 + LEFT * 3.5 + DOWN * 0.1 for v, p in pa.items()}
        pb = {v: p * 0.82 + RIGHT * 3.5 + DOWN * 0.1 for v, p in pb.items()}
        va = NetView(Ga, pa, color=BLUE, rmin=0.05, rk=0.03, eo=0.5)
        vb = NetView(Gb, pb, color=BLUE, rmin=0.05, rk=0.03, eo=0.5)
        ta = T("枢纽在核心", 26).move_to(LEFT * 3.5 + UP * 3.0)
        tb = T("枢纽在边缘", 26).move_to(RIGHT * 3.5 + UP * 3.0)
        with self.say("l4"):
            router = VGroup(*[RoundedRectangle(corner_radius=0.12, width=1.1, height=0.6, stroke_color=MUTED, stroke_width=3) for _ in range(5)]).arrange(RIGHT, buff=0.5)
            hi = VGroup(router[0].copy().set_stroke(GOLD, 5), T("边缘", 22, GOLD).next_to(router[0], DOWN, buff=0.2))
            hi2 = VGroup(router[4].copy().set_stroke(GOLD, 5), T("边缘", 22, GOLD).next_to(router[4], DOWN, buff=0.2))
            yr = T("2005", 30, GOLD).next_to(router, UP, buff=0.4)
            self.play(FadeIn(router), FadeIn(yr), run_time=0.8)
            self.play(Create(hi), Create(hi2), run_time=0.8)
        with self.say("l5"):
            self.play(FadeOut(VGroup(router, hi, hi2, yr)), run_time=0.4)
            self.play(FadeIn(va.group), FadeIn(ta), run_time=1.0)
            self.play(FadeIn(vb.group), FadeIn(tb), run_time=1.0)
            self.play(*[Indicate(va.dots[h], color=RED) for h in range(6)], *[Indicate(vb.dots[h], color=RED) for h in range(6)], run_time=1.0)
        Sa = comps(Ga, range(6))[0] / Ga.number_of_nodes()
        Sb = comps(Gb, range(6))[0] / Gb.number_of_nodes()
        print(f"[al] doyle Sa {Sa:.2f} Sb {Sb:.2f}")
        with self.say("l6"):
            self.play(*va.flash(range(6)), *vb.flash(range(6)), run_time=0.6)
            self.play(*va.state(range(6), hl=GOLD), *vb.state(range(6), hl=GOLD), run_time=1.4)
            ka = counter("最大连通块", f"{Sa:.0%}", RED).next_to(va.group, DOWN, buff=0.05)
            kb = counter("最大连通块", f"{Sb:.0%}", GOLD).next_to(vb.group, DOWN, buff=0.05)
            self.play(FadeIn(ka), FadeIn(kb), run_time=0.6)
        clear(self)
