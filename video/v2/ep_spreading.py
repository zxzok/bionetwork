"""Animated explainer: 网络上的传播与免疫 (SIR, epidemic threshold, immunization, superspreading)."""
import random
from collections import Counter

import networkx as nx
import numpy as np

from common import *  # noqa: F401,F403
from bhelp import NetView, fit, sf_graph, counter, axes, legend, parts_slide, recap_slide, show_clip

TITLE = "网络上的传播：枢纽、阈值与免疫"

LINES = {
    # hook
    "h1": "我们先看两张网络。每个圆点是一个人，每条线表示两个人之间有接触。这两张网络，人数一样，连线的数目也一样。",
    "h1b": "左边叫随机网络，每个人的接触数都差不多。右边叫无标度网络——大多数人接触很少，少数几个人接触极多，这几个人叫枢纽。",
    "h2": "现在放进同一种病原体。每条接触线，传染的概率都是四分之一。两边各找一个只有一个接触对象的人，作为第一个病人。",
    "h3": "先看左边。病原体只传给了一个人，就停了下来。",
    "h4": "【慢】再看右边——它一路传开，将近三分之一的人被感染。",
    "h5": "同样弱的病原体，在两张网络上，结局完全不同。这一期，我们就把其中的原因讲清楚。",
    "q0": "这一期分三部分来讲。",
    "q1": "第一部分，没有网络的时候，经典的传播模型说了什么。",
    "q2": "第二部分，网络结构怎样决定，一种病能不能流行开来。",
    "q3": "第三部分，怎样利用网络结构，去接种，去追踪。",
    # R0
    "r1": "先看第一部分。我们暂时忘掉网络，假设人群是均匀混合的——也就是说，每个人都可能碰到任何一个人。",
    "r2": "按照状态，把人分成三类：还没被感染的易感者，正在生病、能传染别人的感染者，以及康复后获得免疫的移除者。",
    "r3": "一个病人在整个病程里，平均直接传染几个人——这个数，叫基本再生数，写作 R 零。",
    "r4": "如果它等于二，就是一传二，二传四，四传八。你看左边这棵树，每一代翻一倍，很快就会暴发。",
    "r5": "如果它只有零点八，右边每一代都比上一代少，疫情会自己熄灭。",
    "r5b": "【慢】所以，基本再生数大于一，疾病可以流行；小于一，疾病会自行消失。",
    "r6": "这张图，横轴是时间，纵轴是三类人各占的比例。蓝色是易感者，红色是感染者，灰色是移除者。",
    "r6b": "基本再生数等于二的时候，算出来最终大约八成的人会被感染，就是虚线标出的这个高度。",
    "r7": "下面这行式子说的是：基本再生数，等于每次接触的传播概率，乘以接触的人数，再乘以病程的长短。",
    "r7b": "也就是说，它不是病原体固定不变的常数。接触结构一变，比如停课、居家，它就跟着变。",
    # network
    "n1": "下面进入第二部分。把传播放回网络上：病原体只能沿着连线，从感染者走到和他直接相连的人。",
    "n2": "回放开头右边那次暴发。第一个病人只有一个接触对象，可这个对象恰好是一个枢纽，就是画了黄圈的这个。",
    "n3": "枢纽一旦被感染，到下一代，病原体就到达了网络的各个角落。",
    "n4": "下面这排数字，是每一代新感染者平均有几条连接。第一代就是那个枢纽，二十四条；往后，整体越来越少。",
    "n5": "【慢】先感染枢纽，再到中等节点，最后才到边缘。这就是网络上传播的层级顺序。",
    # threshold
    "t1": "枢纽为什么这么关键。我们从一个简单的事实说起：你的朋友，平均来说，比你有更多的朋友。",
    "t2": "在这张网络里，一个人平均只有三个多接触对象。可是，沿着一条连线走到的那个人，平均有十个以上。",
    "t3": "这叫朋友悖论。病原体正是沿着连线走的，所以它总是更容易碰到枢纽。",
    "t4": "【慢】把这个想法写成公式，就是网络上的流行病阈值。传播能力超过这个阈值，疾病才能流行开来。",
    "t4b": "左边的 λ c 就是阈值。分子是连接数的平均，分母是连接数平方的平均——平方会把大的数放得更大，所以枢纽越多，分母越大，阈值越低。",
    "t5": "举个例子。下面这张图，横轴是两种网络，纵轴是阈值。平均连接数都是六，随机网络的阈值大约零点一七；一张更不均匀的网络，可能只有零点零七。",
    "t6": "【慢】对无标度网络，网络越大，连接数平方的平均就越大，阈值趋近于零。也就是说，再弱的传播能力，也可能引起大范围流行。",
    # immunization
    "i0": "最后是第三部分：干预。画面里，是世界卫生组织的疫苗接种宣传片。",
    "i1": "好，回到网络。疫苗有限，我们手里只有十三剂，要在这张网络里分出去。",
    "i2": "第一种办法，随机接种。绿色的是接种的人，他们分散在网络各处；画了红圈的几个枢纽，都没有接种。",
    "i3": "第二种办法，优先接种连接最多的人。效果最直接，可现实中，我们往往不知道谁的接触最多。",
    "i4": "第三种办法很巧妙，叫熟人免疫：随机找一个人，请他推荐一位熟人，给这位熟人接种。",
    "i5": "因为沿着连线走，更容易走到枢纽。所以这个只用局部信息的办法，也能找到不少枢纽，就是闪动的这几个。",
    "i6": "我们在两千个节点的无标度网络上，三种办法各接种一成的人，再算剩下网络的传播阈值。",
    "i6b": "这张图，横轴是三种办法，纵轴是阈值，虚线是不接种时的阈值。阈值越高，病越难流行。",
    "i7": "【慢】随机接种，阈值只升了一点；熟人免疫，阈值升到原来的两倍多；直接接种枢纽，升得最多。",
    "i7b": "这和刚才的阈值公式是一致的：拿掉枢纽，连接数平方的平均降得最快，阈值也就升得最快。",
    # superspreading
    "s0": "枢纽在真实疫情里也有对应，叫超级传播：极少数病人，传染了很多人。画面是2020年初，香港卫生部门开展接触追踪的新闻片段。",
    "s1": "一项研究分析了香港2020年初一千多例新冠感染的接触追踪数据。",
    "s2": "研究估计，百分之十九的病例，造成了百分之八十的本地传播。左边一百个点里，红色的十九个，就代表这一小部分病例。",
    "s3": "也就是说，大多数病人一个人也没有传，少数人却传给了一大群人。",
    "s4": "这带来一个追踪的办法，叫向后追踪。这是开头那次暴发的传播树，从上往下是一代一代的病例。随机挑一个病例，不查他传给了谁，而是往回查，他是被谁传染的。",
    "s5": "在这次暴发里，一个病例平均只传给了一个人左右；而它的传染源，平均传给了四个多人。",
    "s6": "【慢】所以往回追一步，更可能抓到一个超级传播者，以及他牵出的一整串病例。这还是朋友悖论在起作用。",
    # sensors
    "w1": "朋友悖论还能用来提前预警。",
    "w2": "2009年美国一所大学流感暴发时，研究者跟踪了七百多名学生。一组是随机抽取的，另一组，是被他们提名的朋友。",
    "w3": "这张图，横轴是时间，纵轴是每天新增的病例。黄色是朋友组，蓝色是随机组。",
    "w3b": "【慢】朋友组的流行进程，比随机组提前了将近十四天。",
    "w4": "不需要画出整张网络，只要监测朋友，就能更早看到疫情的苗头。",
    # recap
    "z1": "好，我们来总结一下。",
    "z2": "第一，基本再生数决定疾病能否流行，而它依赖接触结构。",
    "z3": "第二，网络越不均匀，阈值越低；无标度网络的阈值趋近于零。",
    "z4": "第三，免疫和追踪都要利用网络结构，枢纽和朋友悖论是关键。",
    "z5": "这个专题的知识页面里，有画面上的这个交互演示。先是不免疫，病原体在网络上传开了。",
    "z5b": "再改成给度最大的百分之十五接种，传播很快就停了下来。你可以亲手切换网络和免疫策略试一试。",
}

SUS, INF, REC = BLUE, RED, "#4a5262"


# ----------------------------------------------------------------------------- simulation helpers
def sir_tree(G, T, src, seed):
    """Discrete-generation SIR: each new case infects each susceptible neighbour once with probability T."""
    rng = random.Random(seed)
    parent = {src: None}
    gens = [[src]]
    cur = [src]
    while cur:
        new = []
        for u in cur:
            for w in G.neighbors(u):
                if w not in parent and rng.random() < T:
                    parent[w] = u
                    new.append(w)
        if new:
            gens.append(new)
        cur = new
    return gens, parent


def hook_graphs():
    Gs = sf_graph(160, 2.3, seed=16, kmax=40)
    N, M = Gs.number_of_nodes(), Gs.number_of_edges()
    Ge = nx.gnm_random_graph(N, M, seed=3)
    return Ge, Gs


def kc(G):
    k = np.array([d for _, d in G.degree()], float)
    return k.mean() / ((k ** 2).mean() - k.mean())


def immunize_thresholds():
    G = nx.barabasi_albert_graph(2000, 2, seed=1)
    N = G.number_of_nodes(); g = int(0.1 * N)
    rng = random.Random(1)
    r = rng.sample(list(G), g)
    t = sorted(G, key=G.degree, reverse=True)[:g]
    a = set()
    while len(a) < g:
        u = rng.choice(list(G))
        a.add(rng.choice(list(G.neighbors(u))))
    out = {"none": kc(G)}
    for name, S in (("rand", r), ("acq", list(a)), ("hub", t)):
        H = G.copy(); H.remove_nodes_from(S)
        out[name] = kc(H)
    return out


# ----------------------------------------------------------------------------- episode
class Episode(Narrated):
    LINES = LINES

    def construct(self):
        self.hook()
        parts_slide(self, ["一  经典传播模型：基本再生数", "二  网络结构与流行病阈值", "三  免疫、追踪与预警"])
        self.r0()
        self.network()
        self.threshold()
        self.immunization()
        self.superspreading()
        self.sensors()
        self.recap()

    def fade_all(self, rt=0.8):
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=rt)

    # ------------------------------------------------------------------ hook
    def hook(self):
        Ge, Gs = hook_graphs()
        Tp = 0.25
        se = sorted(Ge)[42]
        ss = sorted(Gs, key=Gs.degree)[48]
        ge, _ = sir_tree(Ge, Tp, se, 14)
        gs, ps = sir_tree(Gs, Tp, ss, 14)
        self.hook_data = (Gs, gs, ps, ss)
        ve = NetView(Ge, fit(nx.kamada_kawai_layout(Ge), (-6.5, -0.7, -2.7, 2.5)), color=SUS, eo=0.35)
        vs = NetView(Gs, fit(nx.kamada_kawai_layout(Gs), (0.7, 6.5, -2.7, 2.5)), color=SUS, eo=0.35)
        self.vs_pos = vs.pos
        le = T("随机网络", 28).move_to(LEFT * 3.6 + UP * 3.25)
        ls = T("无标度网络", 28).move_to(RIGHT * 3.6 + UP * 3.25)
        with self.say("h1") as d:
            self.play(FadeIn(ve.group), FadeIn(vs.group), run_time=d * 0.6)
        with self.say("h1b") as d:
            self.play(FadeIn(le), run_time=0.6)
            self.play(FadeIn(ls), *[Indicate(vs.dots[h], color=GOLD, scale_factor=1.8) for h in sorted(Gs, key=Gs.degree)[-4:]], run_time=1.6)
        ce = counter("感染", f"1/{Ge.number_of_nodes()}", RED, vs=32).move_to(LEFT * 3.6 + DOWN * 3.3)
        cs = counter("感染", f"1/{Gs.number_of_nodes()}", RED, vs=32).move_to(RIGHT * 3.6 + DOWN * 3.3)
        with self.say("h2") as d:
            self.play(ve.dots[se].animate.set_color(INF).scale(1.8), vs.dots[ss].animate.set_color(INF).scale(1.8),
                      run_time=1.0)
            self.play(Flash(ve.dots[se], color=RED), Flash(vs.dots[ss], color=RED), FadeIn(ce), FadeIn(cs), run_time=1.0)

        def run(view, gens, cnt, total, rt):
            done = 1
            for i in range(1, len(gens)):
                prev, new = gens[i - 1], gens[i]
                done += len(new)
                anims = [view.dots[v].animate.set_color(REC) for v in prev]
                anims += [view.dots[v].animate.set_color(INF) for v in new]
                anims.append(Transform(cnt, counter("感染", f"{done}/{total}", RED, vs=32).move_to(cnt)))
                self.play(*anims, run_time=rt)
            self.play(*[view.dots[v].animate.set_color(REC) for v in gens[-1]], run_time=0.4)

        with self.say("h3") as d:
            run(ve, ge, ce, Ge.number_of_nodes(), 0.8)
        with self.say("h4") as d:
            run(vs, gs, cs, Gs.number_of_nodes(), max(0.4, d * 0.7 / len(gs)))
        with self.say("h5") as d:
            q = T("同一种病原体，两种结局", 56, GOLD, weight=BOLD)
            self.play(*[m.animate.set_opacity(0.15) for m in (ve.group, vs.group, ce, cs, le, ls)], run_time=1.0)
            self.play(Write(q), run_time=1.2)
        self.fade_all()

    # ------------------------------------------------------------------ R0
    def r0(self):
        tag = self.chapter("一  经典模型：一传二，二传四")
        crowd = VGroup(*[Dot(radius=0.07, color=SUS) for _ in range(120)])
        rng = np.random.default_rng(3)
        for d_ in crowd:
            d_.move_to([rng.uniform(-6, 6), rng.uniform(-2.8, 2.6), 0])
        with self.say("r1") as d:
            self.play(FadeIn(tag), FadeIn(crowd, lag_ratio=0.01), run_time=1.2)
            self.play(*[d_.animate.shift([rng.uniform(-0.6, 0.6), rng.uniform(-0.5, 0.5), 0]) for d_ in crowd], run_time=d * 0.5)
        boxes = VGroup()
        for c, s, sub in ((SUS, "S", "易感者"), (INF, "I", "感染者"), (MUTED, "R", "移除者")):
            b = RoundedRectangle(corner_radius=0.15, width=2.4, height=1.4, stroke_color=c, stroke_width=3)
            lab = VGroup(T(s, 44, c, weight=BOLD), T(sub, 24, c)).arrange(DOWN, buff=0.1).move_to(b)
            boxes.add(VGroup(b, lab))
        boxes.arrange(RIGHT, buff=1.6).move_to(UP * 0.3)
        arr = VGroup(Arrow(boxes[0].get_right(), boxes[1].get_left(), buff=0.1, color=INK),
                     Arrow(boxes[1].get_right(), boxes[2].get_left(), buff=0.1, color=INK))
        with self.say("r2") as d:
            self.play(FadeOut(crowd), run_time=0.6)
            self.play(LaggedStart(*[FadeIn(b, shift=UP * 0.2) for b in boxes], lag_ratio=0.3), run_time=1.4)
            self.play(GrowArrow(arr[0]), GrowArrow(arr[1]), run_time=0.8)
        with self.say("r3") as d:
            r0 = MathTex(r"R_0", font_size=60, color=GOLD).next_to(boxes, DOWN, buff=0.8)
            self.play(Write(r0), Indicate(boxes[1], color=RED), run_time=1.4)
        self.play(FadeOut(boxes), FadeOut(arr), r0.animate.to_edge(UP, buff=0.9), run_time=0.8)

        def tree(levels, x0, color):
            rows = VGroup()
            for li, n in enumerate(levels):
                row = VGroup(*[Dot(radius=0.09, color=color) for _ in range(n)]).arrange(RIGHT, buff=0.18)
                row.move_to([x0, 1.4 - li * 1.05, 0])
                rows.add(row)
            edges = VGroup()
            for li in range(1, len(levels)):
                for j, dd in enumerate(rows[li]):
                    par = rows[li - 1][min(j // 2, len(rows[li - 1]) - 1)]
                    edges.add(Line(par.get_center(), dd.get_center(), stroke_width=1.5, color=color, stroke_opacity=0.5))
            return rows, edges
        rows, edges = tree([1, 2, 4, 8], -3.4, RED)
        lab2 = MathTex(r"R_0=2", font_size=42, color=RED).move_to([-3.4, 2.3, 0])
        nums2 = VGroup(*[T(str(n), 26, MUTED).move_to([-6.3, 1.4 - i * 1.05, 0]) for i, n in enumerate([1, 2, 4, 8])])
        with self.say("r4") as d:
            self.play(FadeIn(lab2), run_time=0.5)
            for i in range(4):
                es = [e for e in edges if abs(e.get_end()[1] - rows[i].get_center()[1]) < 0.01]
                self.play(*[Create(e) for e in es], FadeIn(rows[i], scale=0.5), FadeIn(nums2[i]), run_time=d * 0.18)
        lab8 = MathTex(r"R_0=0.8", font_size=42, color=BLUE).move_to([3.4, 2.3, 0])
        vals = [1, 0.8, 0.64, 0.51]
        drops = VGroup(*[Circle(radius=0.32 * np.sqrt(v), color=BLUE, fill_opacity=0.6, stroke_width=0).move_to([3.4, 1.4 - i * 1.05, 0])
                         for i, v in enumerate(vals)])
        nums8 = VGroup(*[T(f"{v:g}", 26, MUTED).move_to([5.9, 1.4 - i * 1.05, 0]) for i, v in enumerate(vals)])
        with self.say("r5") as d:
            self.play(FadeIn(lab8), run_time=0.5)
            self.play(LaggedStart(*[AnimationGroup(FadeIn(c, scale=0.6), FadeIn(n)) for c, n in zip(drops, nums8)], lag_ratio=0.5),
                      run_time=d * 0.6)
        with self.say("r5b") as d:
            self.play(Indicate(lab2, color=RED, scale_factor=1.3), Indicate(lab8, color=BLUE, scale_factor=1.3), run_time=1.4)
        # SIR curves for R0 = 2
        self.play(*[FadeOut(m) for m in (rows, edges, lab2, nums2, lab8, drops, nums8, r0)], run_time=0.7)
        dt, Tm = 0.05, 16
        s, i, r = 0.999, 0.001, 0.0
        ts, S, I, R = [], [], [], []
        for k in range(int(Tm / dt) + 1):
            ts.append(k * dt); S.append(s); I.append(i); R.append(r)
            ds, di = -2 * s * i, 2 * s * i - i
            s, i, r = s + ds * dt, i + di * dt, r + i * dt
        ax = axes([0, Tm, 4], [0, 1, 0.5], 8.5, 4.4, yn=[0, 0.5, 1]).shift(DOWN * 0.4 + LEFT * 0.8)
        xl = T("时间", 22, MUTED).next_to(ax.x_axis, DOWN, buff=0.3)
        cS = ax.plot_line_graph(ts, S, line_color=SUS, add_vertex_dots=False, stroke_width=5)
        cI = ax.plot_line_graph(ts, I, line_color=INF, add_vertex_dots=False, stroke_width=5)
        cR = ax.plot_line_graph(ts, R, line_color=MUTED, add_vertex_dots=False, stroke_width=5)
        lg = legend([(SUS, "易感者"), (INF, "感染者"), (MUTED, "移除者")]).to_corner(UR, buff=0.6).shift(DOWN * 0.5)
        lab = MathTex(r"R_0=2", font_size=40, color=GOLD).next_to(lg, DOWN, buff=0.4)
        with self.say("r6") as d:
            self.play(Create(ax), FadeIn(xl), FadeIn(lg), FadeIn(lab), run_time=1.0)
            self.play(Create(cS), Create(cI), Create(cR), run_time=d * 0.55, rate_func=linear)
        with self.say("r6b") as d:
            fin = DashedLine(ax.c2p(0, R[-1]), ax.c2p(Tm, R[-1]), color=GOLD)
            ft = T(f"最终约 {round(R[-1] * 100)}%", 26, GOLD).next_to(ax.c2p(Tm * 0.55, R[-1]), UP, buff=0.12)
            self.play(Create(fin), FadeIn(ft), run_time=0.8)
        with self.say("r7") as d:
            f = VGroup(MathTex(r"R_0=", font_size=44), T("传播概率", 32), MathTex(r"\times", font_size=40), T("接触数", 32, GOLD),
                       MathTex(r"\times", font_size=40), T("病程", 32)).arrange(RIGHT, buff=0.18).to_edge(DOWN, buff=0.4)
            self.play(VGroup(ax, cS, cI, cR, fin).animate.set_stroke(opacity=0.25), VGroup(xl, ft).animate.set_opacity(0.25), Write(f), run_time=1.6)
        with self.say("r7b") as d:
            self.play(Indicate(f[3], color=GOLD, scale_factor=1.3), run_time=1.0)
        self.fade_all()

    # ------------------------------------------------------------------ network SIR replay
    def network(self):
        tag = self.chapter("二  网络结构：只能沿着连线走")
        Gs, gens, parent, src = self.hook_data
        pos = fit(nx.kamada_kawai_layout(Gs), (-5.6, 5.6, -2.1, 2.9))
        v = NetView(Gs, pos, color=SUS, eo=0.35)
        with self.say("n1") as d:
            self.play(FadeIn(tag), FadeIn(v.group), run_time=1.2)
            u = random.Random(2).choice(list(Gs))
            self.play(v.dots[u].animate.set_color(INF).scale(1.6), run_time=0.5)
            nb = list(Gs.neighbors(u))
            self.play(*[(v.edges.get((u, w)) or v.edges.get((w, u))).animate.set_stroke(RED, width=4, opacity=1) for w in nb],
                      *[Indicate(v.dots[w], color=RED) for w in nb], run_time=1.0)
            self.play(*[(v.edges.get((u, w)) or v.edges.get((w, u))).animate.set_stroke(SUS, width=1.4, opacity=0.35) for w in nb],
                      v.dots[u].animate.set_color(SUS).scale(1 / 1.6), run_time=0.6)
        hub = gens[1][0]
        with self.say("n2") as d:
            self.play(v.dots[src].animate.set_color(INF).scale(1.8), run_time=0.6)
            ring = Circle(radius=v.dots[hub].radius + 0.15, color=GOLD, stroke_width=3).move_to(v.dots[hub])
            e = v.edges.get((src, hub)) or v.edges.get((hub, src))
            self.play(e.animate.set_stroke(RED, width=4, opacity=1), Create(ring), run_time=1.0)
        avg = [np.mean([Gs.degree(x) for x in g]) for g in gens[1:]]
        cells = VGroup(*[T(f"{a:.0f}" if a >= 10 else f"{a:.1f}", 26, GOLD) for a in avg]).arrange(RIGHT, buff=0.55)
        cells.to_edge(DOWN, buff=0.35)
        heads = VGroup(*[T(f"第{i + 1}代", 18, MUTED).next_to(c, UP, buff=0.1) for i, c in enumerate(cells)])

        def step(i, rt):
            prev, new = gens[i - 1], gens[i]
            anims = [v.dots[x].animate.set_color(REC) for x in prev]
            anims += [v.dots[x].animate.set_color(INF) for x in new]
            for x in new:
                ee = v.edges.get((parent[x], x)) or v.edges.get((x, parent[x]))
                anims.append(ee.animate.set_stroke(RED, width=3, opacity=0.9))
            anims += [FadeIn(cells[i - 1]), FadeIn(heads[i - 1])]
            self.play(*anims, run_time=rt)
        with self.say("n3") as d:
            step(1, 1.0)
            self.play(FadeOut(ring), run_time=0.3)
            step(2, 1.2)
        with self.say("n4") as d:
            for i in range(3, len(gens)):
                step(i, max(0.5, d * 0.6 / (len(gens) - 3)))
        with self.say("n5") as d:
            self.play(Indicate(cells[0], color=GOLD, scale_factor=1.4), run_time=0.8)
            self.play(LaggedStart(*[Indicate(c, color=GOLD, scale_factor=1.2) for c in cells[1:]], lag_ratio=0.15), run_time=1.6)
        self.fade_all()

    # ------------------------------------------------------------------ threshold
    def threshold(self):
        tag = self.chapter("二  网络结构：阈值为什么消失")
        Gs = self.hook_data[0]
        pos = fit(nx.kamada_kawai_layout(Gs), (-6.5, -0.6, -3.0, 2.8))
        v = NetView(Gs, pos, color=SUS, eo=0.3)
        k = np.array([d for _, d in Gs.degree()], float)
        kn = k.mean()
        kk = (k ** 2).mean() / k.mean()
        with self.say("t1") as d:
            self.play(FadeIn(tag), FadeIn(v.group), run_time=1.2)
            u = sorted(Gs, key=Gs.degree)[30]
            me = v.dots[u]
            self.play(me.animate.set_color(GOLD).scale(2), run_time=0.6)
            for w in Gs.neighbors(u):
                ee = v.edges.get((u, w)) or v.edges.get((w, u))
                self.play(ee.animate.set_stroke(GOLD, width=4, opacity=1), v.dots[w].animate.set_color(GREEN).scale(1.5), run_time=0.6)
        with self.say("t2") as d:
            b1 = counter("一个人平均的接触数", f"{kn:.1f}", SUS)
            b2 = counter("邻居平均的接触数", f"{kk:.1f}", GOLD)
            VGroup(b1, b2).arrange(RIGHT, buff=1.2).move_to(RIGHT * 3.6 + UP * 1.6)
            self.play(FadeIn(b1, shift=UP * 0.2), run_time=0.8)
            # walk along random edges: endpoints light up
            rng = random.Random(5)
            es = rng.sample(list(Gs.edges()), 14)
            ends = [e[rng.randrange(2)] for e in es]
            self.play(LaggedStart(*[Indicate(v.dots[x], color=GOLD, scale_factor=1.8) for x in ends], lag_ratio=0.12), run_time=d * 0.4)
            self.play(FadeIn(b2, shift=UP * 0.2), run_time=0.8)
        with self.say("t3") as d:
            par = T("朋友悖论", 34, GOLD, weight=BOLD).move_to(RIGHT * 3.6 + DOWN * 0.3)
            f0 = T("你的朋友，比你有更多的朋友", 26, INK).next_to(par, DOWN, buff=0.35)
            self.play(Write(par), run_time=0.8)
            self.play(FadeIn(f0, shift=UP * 0.2), run_time=1.0)
        with self.say("t4") as d:
            self.play(*[FadeOut(m) for m in (v.group, b1, b2, par, f0)], run_time=0.8)
            f1 = MathTex(r"\lambda_c", r"=", r"\frac{\langle k\rangle}{\langle k^2\rangle}", font_size=72)
            f1[0].set_color(RED); f1[2].set_color(GOLD)
            f1.move_to(UP * 1.6)
            self.play(Write(f1), run_time=d * 0.5)
        with self.say("t4b") as d:
            l0 = T("阈值", 26, RED).next_to(f1[0], LEFT, buff=0.35)
            ln = T("连接数的平均", 26, GOLD).next_to(f1[2], RIGHT, buff=0.4).shift(UP * 0.45)
            ld = T("连接数平方的平均", 26, GOLD).next_to(f1[2], RIGHT, buff=0.4).shift(DOWN * 0.45)
            self.play(FadeIn(l0, shift=RIGHT * 0.2), run_time=0.6)
            self.play(FadeIn(ln, shift=LEFT * 0.2), run_time=0.6)
            self.wait(d * 0.15)
            self.play(FadeIn(ld, shift=LEFT * 0.2), Indicate(f1[2], color=GOLD, scale_factor=1.1), run_time=1.0)
        self.play(FadeOut(l0), FadeOut(ln), FadeOut(ld), run_time=0.5)
        ax = axes([0, 3, 1], [0, 0.2, 0.05], 5.0, 3.0, yn=[0, 0.1, 0.2], fs=20).move_to(DOWN * 1.5)
        lc_er, lc_sf = 6 / (42 - 6), 6 / (90 - 6)

        def bar(x, h, c, lab, val):
            r = Rectangle(width=0.9, height=max(1e-3, ax.c2p(0, h)[1] - ax.c2p(0, 0)[1]), fill_color=c, fill_opacity=0.9, stroke_width=0)
            r.move_to(ax.c2p(x, 0), aligned_edge=DOWN)
            return VGroup(r, T(val, 26, c, weight=BOLD).next_to(r, UP, buff=0.08), T(lab, 22, INK).next_to(ax.c2p(x, 0), DOWN, buff=0.2))
        with self.say("t5") as d:
            k6 = T("平均连接数 = 6", 24, MUTED).next_to(ax, RIGHT, buff=0.5).shift(UP * 0.8)
            self.play(Create(ax), FadeIn(k6), run_time=0.8)
            g1 = bar(1, lc_er, MUTED, "随机网络", f"{lc_er:.2f}")
            g2 = bar(2, lc_sf, RED, "更不均匀", f"{lc_sf:.2f}")
            self.play(GrowFromEdge(g1[0], DOWN), FadeIn(g1[1:]), run_time=1.0)
            self.play(GrowFromEdge(g2[0], DOWN), FadeIn(g2[1:]), run_time=1.0)
        with self.say("t6") as d:
            self.play(*[FadeOut(m) for m in (ax, g1, g2, k6)], run_time=0.6)
            f2 = MathTex(r"N\to\infty:\quad \langle k^2\rangle\to\infty\quad\Rightarrow\quad \lambda_c\to 0", font_size=48, color=INK)
            f2.next_to(f1, DOWN, buff=1.0)
            self.play(Write(f2), run_time=d * 0.45)
            self.play(Indicate(f1[0], color=RED, scale_factor=1.3), run_time=1.0)
        self.fade_all()

    # ------------------------------------------------------------------ immunization
    def immunization(self):
        show_clip(self, "i0", "yt_who_immunization.mp4", "center", "视频：World Health Organization (WHO) · YouTube", start=20)
        tag = self.chapter("三  干预：疫苗先给谁")
        G = nx.barabasi_albert_graph(130, 2, seed=4)
        pos = fit(nx.kamada_kawai_layout(G), (-5.4, 5.4, -3.0, 2.7))
        v = NetView(G, pos, color=SUS, eo=0.3)
        g = 13
        with self.say("i1") as d:
            self.play(FadeIn(tag), FadeIn(v.group), run_time=1.2)
            shot = counter("疫苗", f"{g} 剂", GREEN, vs=32).to_corner(UR, buff=0.5)
            self.play(FadeIn(shot), run_time=0.6)

        def mark(nodes, rt):
            return [v.dots[x].animate.set_color(GREEN).scale(1.5) for x in nodes]

        def unmark(nodes):
            return [v.dots[x].animate.set_color(SUS).scale(1 / 1.5) for x in nodes]
        rnd = random.Random(3).sample(list(G), g)
        hubs = sorted(G, key=G.degree, reverse=True)[:g]
        with self.say("i2") as d:
            lab = T("随机接种", 30, GREEN).to_corner(UL, buff=0.45).shift(DOWN * 0.55)
            self.play(FadeIn(lab), LaggedStart(*mark(rnd, 1), lag_ratio=0.1), run_time=d * 0.45)
            rings = VGroup(*[Circle(radius=v.dots[h].radius + 0.13, color=RED, stroke_width=2.5).move_to(v.dots[h]) for h in hubs[:6] if h not in rnd])
            self.play(Create(rings), run_time=0.8)
        with self.say("i3") as d:
            self.play(*unmark(rnd), FadeOut(rings), Transform(lab, T("优先接种枢纽", 30, GREEN).move_to(lab, aligned_edge=LEFT)), run_time=0.8)
            self.play(LaggedStart(*mark(hubs, 1), lag_ratio=0.08), run_time=d * 0.3)
            qm = T("现实中：谁是枢纽，往往不知道", 40, GOLD, weight=BOLD).move_to(ORIGIN)
            self.play(v.group.animate.set_opacity(0.2), FadeIn(qm), run_time=0.8)
        with self.say("i4") as d:
            self.play(FadeOut(qm), v.group.animate.set_opacity(1), *[v.dots[x].animate.set_color(SUS).scale(1 / 1.5) for x in hubs],
                      Transform(lab, T("熟人免疫", 30, GREEN).move_to(lab, aligned_edge=LEFT)), run_time=0.8)
            for e in v.edges.values():
                e.set_stroke(opacity=0.3)
            rng = random.Random(8)
            picks = []
            for j in range(3):
                u = rng.choice(list(G)); w = rng.choice(list(G.neighbors(u)))
                picks.append(w)
                walker = Dot(pos[u], radius=0.11, color=GOLD)
                self.play(FadeIn(walker, scale=0.5), Indicate(v.dots[u], color=GOLD), run_time=0.5)
                self.play(walker.animate.move_to(pos[w]), run_time=0.6)
                self.play(FadeOut(walker), v.dots[w].animate.set_color(GREEN).scale(1.5), run_time=0.4)
        acq = set(picks)
        rng = random.Random(9)
        while len(acq) < g:
            u = rng.choice(list(G)); acq.add(rng.choice(list(G.neighbors(u))))
        rest = [x for x in acq if x not in picks]
        with self.say("i5") as d:
            self.play(LaggedStart(*mark(rest, 1), lag_ratio=0.1), run_time=d * 0.4)
            hit = [x for x in acq if x in hubs]
            self.play(*[Indicate(v.dots[x], color=GOLD, scale_factor=1.5) for x in hit], run_time=1.2)
        vals = immunize_thresholds()
        self.play(FadeOut(v.group), FadeOut(lab), FadeOut(shot), run_time=0.7)
        ax = axes([0, 4, 1], [0, 0.7, 0.1], 8.0, 4.4, yn=[0, 0.2, 0.4, 0.6], fs=20).shift(DOWN * 0.5)
        yl = T("剩余网络的传播阈值", 22, MUTED).rotate(PI / 2).next_to(ax.y_axis, LEFT, buff=0.35)
        base = DashedLine(ax.c2p(0, vals["none"]), ax.c2p(4, vals["none"]), color=MUTED)
        bl = T(f"未接种 {vals['none']:.2f}", 20, MUTED).next_to(ax.c2p(4, vals["none"]), UP, buff=0.08).shift(LEFT * 0.7)
        with self.say("i6") as d:
            g2k = counter("两千个节点 · 各接种一成", "三种办法", INK, vs=34)
            self.play(FadeIn(g2k), run_time=0.8)
        with self.say("i6b") as d:
            self.play(FadeOut(g2k), run_time=0.4)
            self.play(Create(ax), FadeIn(yl), run_time=1.0)
            self.play(Create(base), FadeIn(bl), run_time=0.8)
        bars = VGroup()
        for x, key, c, name in ((1, "rand", MUTED, "随机接种"), (2, "acq", GOLD, "熟人免疫"), (3, "hub", GREEN, "接种枢纽")):
            h = vals[key]
            r = Rectangle(width=1.2, height=ax.c2p(0, h)[1] - ax.c2p(0, 0)[1], fill_color=c, fill_opacity=0.9, stroke_width=0)
            r.move_to(ax.c2p(x, 0), aligned_edge=DOWN)
            bars.add(VGroup(r, T(f"{h:.2f}", 26, c, weight=BOLD).next_to(r, UP, buff=0.08), T(name, 22, INK).next_to(ax.c2p(x, 0), DOWN, buff=0.2)))
        with self.say("i7") as d:
            for b in bars:
                self.play(GrowFromEdge(b[0], DOWN), FadeIn(b[1:]), run_time=d * 0.22)
        with self.say("i7b") as d:
            self.play(Indicate(bars[2], color=GREEN, scale_factor=1.08), run_time=1.2)
        self.fade_all()

    # ------------------------------------------------------------------ superspreading
    def superspreading(self):
        show_clip(self, "s0", "yt_hk_contact_tracing.mp4", "center", "视频：Bloomberg News · YouTube", start=5)
        tag = self.chapter("三  干预：超级传播与向后追踪")
        grid = VGroup(*[Dot(radius=0.11, color=SUS) for _ in range(100)]).arrange_in_grid(10, 10, buff=0.22)
        grid.move_to(LEFT * 3.2 + DOWN * 0.2)
        with self.say("s1") as d:
            self.play(FadeIn(tag), FadeIn(grid, lag_ratio=0.01), run_time=1.4)
        top = list(range(19))
        with self.say("s2") as d:
            self.play(*[grid[i].animate.set_color(RED).scale(1.3) for i in top], run_time=1.2)
            bar = VGroup(Rectangle(width=5.0 * 0.8, height=0.6, fill_color=RED, fill_opacity=0.9, stroke_width=0),
                         Rectangle(width=5.0 * 0.2, height=0.6, fill_color=SUS, fill_opacity=0.6, stroke_width=0)).arrange(RIGHT, buff=0)
            bar.move_to(RIGHT * 3.4 + UP * 0.4)
            c1 = counter("病例", "19%", RED).move_to(RIGHT * 3.4 + UP * 2.0)
            c2 = T("造成 80% 的本地传播", 26, INK).next_to(bar, DOWN, buff=0.3)
            self.play(FadeIn(c1), run_time=0.6)
            self.play(GrowFromEdge(bar, LEFT), FadeIn(c2), run_time=1.2)
        with self.say("s3") as d:
            self.play(*[grid[i].animate.set_opacity(0.35) for i in range(19, 100)], run_time=0.8)
            self.play(LaggedStart(*[Indicate(grid[i], color=RED, scale_factor=1.6) for i in top[:6]], lag_ratio=0.15), run_time=1.4)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.6)
        # backward tracing on the hook outbreak tree
        Gs, gens, parent, src = self.hook_data
        cases = [x for g in gens for x in g]
        T_ = nx.DiGraph([(p, c) for c, p in parent.items() if p is not None])
        pos = {}
        for li, g in enumerate(gens):
            ordered = sorted(g, key=lambda x: (x != src, parent.get(x) or 0))
            # order by parent's x for a tidy tree
            if li > 0:
                ordered = sorted(g, key=lambda x: pos[parent[x]][0])
            n = len(ordered)
            w = min(12.0, 0.42 * n)
            for j, x in enumerate(ordered):
                pos[x] = np.array([-w / 2 + (j + 0.5) * w / n, 2.6 - li * 0.72, 0])
        off = Counter(p for p in parent.values() if p is not None)
        dots = {x: Dot(pos[x], radius=0.06 + 0.02 * np.sqrt(off.get(x, 0)), color=REC) for x in cases}
        lines = VGroup(*[Line(pos[p], pos[c], stroke_width=1.4, color=MUTED, stroke_opacity=0.6) for p, c in T_.edges()])
        with self.say("s4") as d:
            self.play(Create(lines), FadeIn(VGroup(*dots.values())), run_time=1.6)
            pick = sorted(gens[2], key=lambda x: off.get(x, 0))[0]
            ring = Circle(radius=0.2, color=GOLD, stroke_width=3).move_to(pos[pick])
            self.play(Create(ring), dots[pick].animate.set_color(GOLD), run_time=0.8)
            p = parent[pick]
            back = Arrow(pos[pick], pos[p], buff=0.12, color=RED, stroke_width=5)
            self.play(GrowArrow(back), dots[p].animate.set_color(RED), run_time=1.0)
        own = np.mean([off.get(c, 0) for c in cases])
        src_mean = np.mean([off[parent[c]] for c in cases if parent[c] is not None])
        self.spread_vals = (own, src_mean)
        with self.say("s5") as d:
            a = counter("一个病例平均传给", f"{own:.1f} 人", SUS, vs=34)
            b = counter("它的传染源平均传给", f"{src_mean:.1f} 人", RED, vs=34)
            VGroup(a, b).arrange(RIGHT, buff=1.4).to_edge(DOWN, buff=0.35)
            self.play(FadeIn(a, shift=UP * 0.2), run_time=0.8)
            self.wait(d * 0.2)
            self.play(FadeIn(b, shift=UP * 0.2), run_time=0.8)
        with self.say("s6") as d:
            kids = [c for c in cases if parent.get(c) == p]
            self.play(*[dots[c].animate.set_color(RED) for c in kids],
                      *[l.animate.set_stroke(RED, opacity=1, width=3) for l, (pp, cc) in zip(lines, T_.edges()) if pp == p],
                      run_time=1.4)
        self.fade_all()

    # ------------------------------------------------------------------ sensors
    def sensors(self):
        tag = self.chapter("三  干预：朋友是哨兵")
        with self.say("w1") as d:
            self.play(FadeIn(tag), run_time=0.6)
            people = VGroup(*[Dot(radius=0.12, color=SUS) for _ in range(8)]).arrange(RIGHT, buff=0.5).shift(UP * 1.6)
            self.play(FadeIn(people, lag_ratio=0.1), run_time=1.0)
        friends = VGroup(*[Dot(radius=0.16, color=GOLD).move_to(p.get_center() + DOWN * 1.2 + RIGHT * 0.15) for p in people])
        arrows = VGroup(*[Arrow(p.get_bottom(), f.get_top(), buff=0.06, color=GOLD, stroke_width=2.5, tip_length=0.15) for p, f in zip(people, friends)])
        with self.say("w2") as d:
            l1 = T("随机组", 24, SUS).next_to(people, LEFT, buff=0.4)
            l2 = T("朋友组", 24, GOLD).next_to(friends, LEFT, buff=0.4)
            self.play(FadeIn(l1), run_time=0.5)
            self.play(LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.1), LaggedStart(*[FadeIn(f) for f in friends], lag_ratio=0.1),
                      FadeIn(l2), run_time=d * 0.5)
        self.play(*[FadeOut(m) for m in (people, friends, arrows, l1, l2)], run_time=0.6)
        ax = axes([0, 100, 20], [0, 1.1, 0.5], 9.5, 4.2).shift(DOWN * 0.4)
        xl = T("时间", 22, MUTED).next_to(ax.x_axis, DOWN, buff=0.3)
        yl = T("新发病例", 22, MUTED).rotate(PI / 2).next_to(ax.y_axis, LEFT, buff=0.3)
        shift = 14
        cr = ax.plot(lambda t: np.exp(-((t - 58) / 13) ** 2), x_range=[0, 100], color=SUS, stroke_width=5)
        cf = ax.plot(lambda t: np.exp(-((t - 58 + shift) / 13) ** 2), x_range=[0, 100], color=GOLD, stroke_width=5)
        lg = legend([(GOLD, "朋友组"), (SUS, "随机组")]).to_corner(UR, buff=0.6).shift(DOWN * 0.5)
        with self.say("w3") as d:
            self.play(Create(ax), FadeIn(xl), FadeIn(yl), FadeIn(lg), run_time=0.8)
            self.play(Create(cf), Create(cr), run_time=d * 0.45, rate_func=linear)
        with self.say("w3b") as d:
            gap = DoubleArrow(ax.c2p(58 - shift, 1.04), ax.c2p(58, 1.04), buff=0, color=RED, stroke_width=4, tip_length=0.18)
            gl = T("提前 13.9 天", 26, RED).next_to(gap, UP, buff=0.1)
            self.play(GrowFromCenter(gap), FadeIn(gl), run_time=0.8)
        with self.say("w4") as d:
            self.play(Indicate(cf, color=GOLD), run_time=1.2)
        self.fade_all()

    # ------------------------------------------------------------------ recap
    def recap(self):
        recap_slide(self, ["基本再生数决定能否流行，它依赖接触结构", "网络越不均匀，阈值越低", "免疫与追踪：利用枢纽和朋友悖论"])
        with self.say("z5") as d:
            self.clip_on("sir_demo.mp4", "full", "本站交互演示：网络上的 SIR 传播与免疫", start=0.3)
        with self.say("z5b") as d:
            pass
        self.clip_off()
        self.wait(1.0)
