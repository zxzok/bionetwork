"""Animated explainer: 研究问题、可复现分析与敏感性分析."""
import random

import networkx as nx
import numpy as np
from scipy.stats import norm

from common import *  # noqa: F401,F403
from kit_c import PANEL, NetView, arrow, axes, callout, chip, clip_line, code_block, counter, fade_all, fit, grow_bars, hist_bars, parts, xlabel, ylabel

TITLE = "你的结论可靠吗：研究问题、可复算与敏感性分析"

LINES = {
    # hook
    "h0": "这是功能磁共振扫描。它能记录大脑各个区域，随时间变化的活动信号。",
    "h1": "2020年的一项研究，把同一份脑影像数据，交给七十个独立的研究团队，检验同样九个事先确定的假设。",
    "h2": "结果，没有两个团队选择了完全相同的分析流程。每一条线，代表一个团队的流程。",
    "h3": "对同一个假设，有的团队得到显著，是绿点；有的不显著，是红点。分歧相当大。",
    "h4": "【慢】数据一样，结论却不一样。结论可能来自数据，也可能来自分析选择。",
    "o0": "这一期分三部分。",
    "o1": "第一部分，一个好问题，和一份可以复算的分析。",
    "o2": "第二部分，随机性和分析选择怎样影响结论。",
    "o3": "第三部分，替代解释和样本量。",
    # research question
    "q1": "先看第一部分。拿一个数据库去分析阿尔茨海默病，这只是一个方向，还不是问题。",
    "q2": "好问题要说清：节点是什么，边是什么，数据来自哪个库、哪个版本。",
    "q3": "还要说清目的：描述、比较、预测，还是解释机制。目的不同，需要的证据也不同。",
    "q4": "最好事先写下判断标准。灰色柱子是度匹配随机基因的分布；疾病基因的连接要超过这条线，才算支持假设。",
    "q5": "【慢】最后检查：如果只看单个基因也能回答，就不需要网络。",
    # reproducible
    "c0": "第一部分的另一半，是可复算。科学界一直在讨论可重复性：别人重做一遍，能不能得到同样的结果。",
    "c1": "可复算的意思是：同样的数据和代码，别人能得到同样的结果。这是一条完整的链：原始数据、脚本、结果、图表。",
    "c2": "原始数据只读，不手工修改。数据库的版本号和下载日期，写进说明文件。",
    "c3": "关键数字要由脚本产生。在图形界面里点出来的结果，很难被别人重现。",
    "c4": "软件版本也要记下来，同一个算法在不同版本里可能不一样。用版本控制管理代码，每完成一步提交一次。",
    "c5": "完成之前，从原始数据出发完整跑一遍，确认所有图表都能重新生成。",
    # seeds
    "s1": "下面进入第二部分。很多网络算法带有随机性，比如社团检测和随机化检验。随机性分两层处理。",
    "s2": "第一层是可复算：记录并固定随机种子，再跑一次，结果完全相同。",
    "s3": "第二层是稳健：结论不能依赖某一个种子。换五十个种子，模块度在一个范围里波动，社团数从五个到八个。",
    "s4": "还有蒙特卡洛误差。上面是经验P值的公式：b是随机网络里，统计量不小于观测值的次数；B是随机网络的总数。",
    "s4b": "它的标准误约为根号下P乘一减P再除以B。真实P值是零点零四时，用一百个随机网络，标准误约零点零二，不少估计跑到了零点零五右边。",
    "s5": "【慢】用一千个随机网络，标准误降到零点零零六左右。随机网络的数目和种子，都要事先确定。",
    # threshold
    "t1": "再看分析选择。这是同一个相关矩阵，我们逐步提高阈值，只保留最强的那部分边。",
    "t2": "网络越来越稀疏。画圈的是连接最多的三个节点，阈值一变，它们也在换。",
    "t3": "右图横轴是密度，蓝线是平均度，黄线是平均聚集系数，都随阈值而变。所以要扫描一段区间，画成曲线来报告。",
    "t4": "本站的脑网络专题里，有一个阈值实验的交互演示。拖动保留密度，网络和枢纽脑区都会跟着变。",
    # multiverse
    "m1": "把这个想法推广：每个分析环节都有几种合理选择，把所有组合都跑一遍，叫多元宇宙分析。",
    "m2": "比如三种边的定义，乘四个密度，再乘两个指标，就是二十四个宇宙。",
    "m3": "把每个宇宙的组间差异从小到大排起来，就是设定曲线。下面的方块，标出每个宇宙用了哪些选择。",
    "m4": "【慢】它回答的是：结论对哪些选择敏感。",
    # alternatives
    "a1": "最后是第三部分，替代解释。第一条要查的，是两组网络的密度是否相同。",
    "a2": "这两组都是随机网络，没有结构差别，只是右边边多一些，聚集系数和路径长度就跟着变了。",
    "a3": "第二，查度匹配。第三，查混杂因素：头动、批次、细胞组成，可能同时影响网络和结果。",
    "a4": "第四，检验了多少节点和指标，要做多重比较校正。第五，不能用同一份数据，既挑选特征，又检验它们。",
    # sample size
    "n1": "再看样本量。十五个节点的网络，就有一百零五条边，每一条都要估计。",
    "n2": "单条边需要多少样本，可以用费舍尔变换来估算，公式在这里。",
    "n2b": "分子是两个正态分位数之和，分别对应显著性水平和统计功效；分母是相关系数的费舍尔变换；k是控制的变量个数。",
    "n2c": "要以八成功效检出零点二的相关，大约需要一百九十四个样本。",
    "n3": "【慢】如果要对所有边做多重比较校正，再用偏相关控制其他变量，就要四百七十多个。",
    # recap
    "r1": "好，我们总结一下。",
    "r2": "第一，好问题要说清比较对象和判断标准。",
    "r3": "第二，好分析要能从原始数据一键重跑，种子和版本都有记录。",
    "r4": "第三，好结论要在合理的分析选择范围内都成立。",
}


def n_edge(rho, alpha=0.05, power=0.8, k=0):
    z = norm.ppf(1 - alpha / 2) + norm.ppf(power)
    return (z / np.arctanh(rho)) ** 2 + 3 + k


def sim_data(n_s=60, p=24, seed=1, shift=0.0):
    rng = np.random.default_rng(seed)
    f = rng.normal(size=(3, n_s))
    load = np.zeros((p, 3))
    for i in range(p):
        load[i, i % 3] = rng.uniform(0.3, 0.8) + shift
    X = load @ f + rng.normal(size=(p, n_s))
    return X


def thr_graph(C, dens):
    p = C.shape[0]
    iu = np.triu_indices(p, 1)
    vals = C[iu]
    m = max(1, int(round(dens * len(vals))))
    idx = np.argsort(-vals)[:m]
    G = nx.Graph(); G.add_nodes_from(range(p))
    G.add_edges_from(zip(iu[0][idx], iu[1][idx]))
    return G


class Episode(Narrated):
    LINES = LINES

    def construct(self):
        self.hook()
        self.parts_slide()
        self.question()
        self.recompute()
        self.seeds()
        self.threshold()
        self.multiverse()
        self.alternatives()
        self.sample_size()
        self.recap()

    # ------------------------------------------------------------------ hook
    def hook(self):
        db = VGroup(Ellipse(width=1.4, height=0.45, color=BLUE, fill_opacity=0.5),
                    Rectangle(width=1.4, height=1.2, color=BLUE, fill_opacity=0.25, stroke_width=0),
                    Ellipse(width=1.4, height=0.45, color=BLUE, fill_opacity=0.5)).move_to(LEFT * 5.8)
        db[0].shift(UP * 0.6); db[2].shift(DOWN * 0.6)
        dl = T("同一份数据", 24, BLUE).next_to(db, DOWN, buff=0.3)
        rng = np.random.default_rng(3)
        ends = [np.array([4.6, y, 0]) for y in np.linspace(3.2, -3.2, 70)]
        paths = VGroup()
        for e in ends:
            mid1 = np.array([-2.5, rng.uniform(-2.5, 2.5), 0]); mid2 = np.array([1.2, (mid1[1] + e[1]) / 2 + rng.uniform(-0.6, 0.6), 0])
            paths.add(VMobject(stroke_color=MUTED, stroke_width=1.2, stroke_opacity=0.6).set_points_smoothly([db.get_right(), mid1, mid2, e]))
        res = rng.random(70) < 0.5
        tips = VGroup(*[Dot(e + RIGHT * 0.18, radius=0.06, color=GREEN if r else RED) for e, r in zip(ends, res)])
        clip_line(self, "h0", "yt_fmri_wellcome.mp4", "视频：Wellcome Centre for Human Neuroimaging · YouTube", start=40)
        with self.say("h1") as d:
            self.play(FadeIn(db), FadeIn(dl), run_time=0.8)
            self.play(LaggedStart(*[Create(p) for p in paths], lag_ratio=0.01), run_time=d * 0.6)
            c = counter("团队", "70", INK).move_to(RIGHT * 6.0 + UP * 3.0)
        with self.say("h2") as d:
            self.play(*[p.animate.set_stroke(interpolate_color(ManimColor(BLUE), ManimColor(VIOLET), rng.random()), opacity=0.8) for p in paths], run_time=1.2)
            tag = T("没有两条完全相同的流程", 26, INK).move_to(UP * 3.4 + LEFT * 0.5)
            self.play(FadeIn(tag), run_time=0.6)
        with self.say("h3") as d:
            self.play(LaggedStart(*[GrowFromCenter(t) for t in tips], lag_ratio=0.015), run_time=d * 0.5)
            lg = VGroup(VGroup(Dot(radius=0.08, color=GREEN), T("显著", 22)).arrange(RIGHT, buff=0.12),
                        VGroup(Dot(radius=0.08, color=RED), T("不显著", 22)).arrange(RIGHT, buff=0.12)).arrange(DOWN, aligned_edge=LEFT).move_to(RIGHT * 6.0 + DOWN * 3.3)
            self.play(FadeIn(lg), run_time=0.5)
        with self.say("h4") as d:
            self.play(*[m.animate.fade(0.85) for m in self.mobjects], run_time=0.8)
            q = VGroup(T("数据", 50, BLUE, weight=BOLD), T("还是", 36, INK), T("分析选择", 50, GOLD, weight=BOLD)).arrange(RIGHT, buff=0.4)
            self.play(Write(q), run_time=1.2)
        fade_all(self)

    def parts_slide(self):
        parts(self, "这一期分三部分", ["一  好问题与可复算的分析", "二  随机性与分析选择", "三  替代解释与样本量"], ["o0", "o1", "o2", "o3"])

    # ------------------------------------------------------------------ research question
    def question(self):
        tag = self.chapter("一  一个好问题")
        fuzzy = VGroup(chip("数据库", MUTED, 28), T("+", 36, MUTED), chip("阿尔茨海默病", MUTED, 28)).arrange(RIGHT, buff=0.3).move_to(UP * 0.4)
        with self.say("q1") as d:
            self.play(FadeIn(tag), FadeIn(fuzzy, shift=UP * 0.2), run_time=1.0)
            no = T("方向 ≠ 问题", 32, RED, weight=BOLD).next_to(fuzzy, DOWN, buff=0.6)
            self.play(Write(no), run_time=0.8)
        target = VGroup(*[Circle(radius=r, color=GOLD, stroke_width=3 if r < 1 else 2).set_stroke(opacity=1 - 0.25 * i) for i, r in enumerate((0.4, 0.9, 1.4))]).move_to(LEFT * 4.2 + DOWN * 0.2)
        parts = VGroup(chip("节点 = ?", BLUE, 24), chip("边 = ?", VIOLET, 24), chip("数据库 · 版本", GREEN, 24)).arrange(DOWN, buff=0.3).move_to(LEFT * 0.6 + DOWN * 0.2)
        with self.say("q2") as d:
            self.play(FadeOut(no), FadeOut(fuzzy), run_time=0.5)
            self.play(Create(target), run_time=0.8)
            self.play(LaggedStart(*[FadeIn(p, shift=LEFT * 0.2) for p in parts], lag_ratio=0.3), run_time=1.2)
        kinds = VGroup(*[chip(s, c, 26) for s, c in (("描述", BLUE), ("比较", GREEN), ("预测", GOLD), ("机制", RED))]).arrange(DOWN, buff=0.3).move_to(RIGHT * 3.0 + DOWN * 0.2)
        with self.say("q3") as d:
            self.play(LaggedStart(*[FadeIn(k, shift=LEFT * 0.2) for k in kinds], lag_ratio=0.25), run_time=1.4)
            self.play(Indicate(kinds[1], color=GREEN), run_time=0.8)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.6)
        rng = np.random.default_rng(2)
        null = rng.normal(4, 1.3, 400)
        ax = axes([0, 12, 2], [0, 120, 40], 6.4, 3.4, xnums=[0, 4, 8, 12], fs=20).move_to(DOWN * 0.6)
        bars, _ = hist_bars(ax, null, np.arange(0, 12.5, 0.5), MUTED)
        xl = xlabel(ax, "疾病基因之间的连接（灰色为度匹配随机基因）", 22, 0.3)
        with self.say("q4") as d:
            pre = T("事先写下判断标准", 30, GOLD, weight=BOLD).to_edge(UP, buff=0.9)
            self.play(FadeIn(pre), Create(ax), FadeIn(xl), run_time=0.8)
            self.play(grow_bars(bars, 1.0))
            thr = DashedLine(ax.c2p(np.percentile(null, 95), 0), ax.c2p(np.percentile(null, 95), 110), color=GOLD)
            sup = T("高于这里才算支持", 22, GOLD).next_to(thr, UP, buff=0.05).shift(RIGHT * 1.0)
            self.play(Create(thr), FadeIn(sup), run_time=0.8)
        with self.say("q5") as d:
            self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.5)
            single = VGroup(*[Dot(radius=0.14, color=BLUE) for _ in range(6)]).arrange(RIGHT, buff=0.4).move_to(LEFT * 3.2)
            G = nx.cycle_graph(6); G.add_edges_from([(0, 3), (1, 4)])
            pos = {v: RIGHT * 3.2 + 1.2 * np.array([np.cos(v * TAU / 6), np.sin(v * TAU / 6), 0]) for v in G}
            netv = VGroup(*[Line(pos[u], pos[v], color=BLUE, stroke_width=2) for u, v in G.edges()], *[Dot(pos[v], radius=0.14, color=BLUE) for v in G])
            l1, l2 = T("单个基因", 26, INK).next_to(single, DOWN, buff=0.5), T("网络", 26, INK).next_to(netv, DOWN, buff=0.4)
            q = T("只看单个基因就能回答  →  不需要网络", 32, GOLD, weight=BOLD).to_edge(UP, buff=1.0)
            self.play(FadeIn(single), FadeIn(l1), FadeIn(netv), FadeIn(l2), run_time=1.0)
            self.play(Write(q), run_time=1.0)
        fade_all(self)

    # ------------------------------------------------------------------ reproducible computation
    def recompute(self):
        clip_line(self, "c0", "yt_reproducibility_nature.mp4", "视频：nature video · YouTube", start=10)
        tag = self.chapter("一  可复算")
        names = [("原始数据", BLUE), ("脚本", GREEN), ("结果", VIOLET), ("图表", GOLD)]
        boxes = VGroup(*[chip(s, c, 28) for s, c in names]).arrange(RIGHT, buff=1.0).move_to(UP * 0.8)
        arrs = VGroup(*[arrow(boxes[i].get_right(), boxes[i + 1].get_left(), MUTED, buff=0.1) for i in range(3)])
        with self.say("c1") as d:
            self.play(FadeIn(tag), LaggedStart(*[FadeIn(b, shift=RIGHT * 0.2) for b in boxes], lag_ratio=0.25), run_time=1.4)
            self.play(LaggedStart(*[GrowArrow(a) for a in arrs], lag_ratio=0.25), run_time=1.0)
        lock = VGroup(RoundedRectangle(corner_radius=0.05, width=0.42, height=0.32, color=BLUE, fill_opacity=0.8),
                      Arc(radius=0.14, start_angle=0, angle=PI, color=BLUE, stroke_width=4).shift(UP * 0.2)).next_to(boxes[0], UP, buff=0.2)
        with self.say("c2") as d:
            self.play(FadeIn(lock, shift=DOWN * 0.1), run_time=0.6)
            hand = T("手工修改", 24, RED).next_to(boxes[0], DOWN, buff=0.6)
            x = Cross(hand, stroke_color=RED, scale_factor=1.2)
            self.play(FadeIn(hand), run_time=0.5)
            self.play(Create(x), run_time=0.5)
            readme = chip("README：版本 · 下载日期", MUTED, 22).next_to(lock, LEFT, buff=0.3)
            if readme.get_left()[0] < -6.9:
                readme.shift(RIGHT * (-6.9 - readme.get_left()[0]) + UP * 0.6)
            self.play(FadeIn(readme), run_time=0.6)
        with self.say("c3") as d:
            self.play(FadeOut(hand), FadeOut(x), run_time=0.4)
            click = VGroup(Rectangle(width=1.8, height=1.1, color=MUTED, stroke_width=2), T("点击", 22, MUTED)).next_to(boxes[2], DOWN, buff=0.8)
            ca = DashedVMobject(arrow(click.get_top(), boxes[2].get_bottom(), RED, buff=0.1))
            self.play(FadeIn(click), Create(ca), run_time=0.8)
            q = T("无法重现", 24, RED).next_to(click, RIGHT, buff=0.2)
            self.play(FadeIn(q), run_time=0.4)
            self.play(Indicate(boxes[1], color=GREEN), run_time=0.8)
        with self.say("c4") as d:
            self.play(FadeOut(click), FadeOut(ca), FadeOut(q), run_time=0.4)
            ver = chip("Python 3.x · networkx 3.x", MUTED, 20).next_to(boxes[1], DOWN, buff=0.4)
            self.play(FadeIn(ver), run_time=0.6)
            line = Line(LEFT * 6.0 + DOWN * 2.4, RIGHT * 6.0 + DOWN * 2.4, color=MUTED, stroke_width=2)
            commits = VGroup(*[Dot(LEFT * 6.0 + RIGHT * 1.5 * i + DOWN * 2.4, radius=0.12, color=GREEN) for i in range(9)])
            self.play(Create(line), run_time=0.5)
            self.play(LaggedStart(*[GrowFromCenter(c) for c in commits], lag_ratio=0.2), run_time=d * 0.35)
        with self.say("c5") as d:
            sweep = Dot(boxes[0].get_center(), radius=0.18, color=WHITE)
            self.play(FadeIn(sweep), run_time=0.3)
            for b in boxes[1:]:
                self.play(sweep.animate.move_to(b.get_center()), Indicate(b, scale_factor=1.15), run_time=0.7)
            ok = T("一键重跑", 30, GOLD, weight=BOLD).next_to(boxes, UP, buff=0.9).shift(RIGHT * 2)
            self.play(FadeOut(sweep), FadeIn(ok), run_time=0.6)
        fade_all(self)

    # ------------------------------------------------------------------ seeds & Monte Carlo error
    def seeds(self):
        tag = self.chapter("二  随机种子")
        G = nx.planted_partition_graph(6, 18, 0.28, 0.035, seed=4)
        pos = fit(nx.spring_layout(G, seed=2), (-6.4, -1.2, -3.0, 2.6))
        net = NetView(G, pos, color=MUTED, eo=0.35, rmin=0.06, rk=0.012)
        cols = [BLUE, GOLD, GREEN, VIOLET, RED, INK, "#7fd3e0", "#e08fd0"]

        def colour(seed):
            p = nx.community.louvain_communities(G, seed=seed)
            cf = {v: cols[i % len(cols)] for i, c in enumerate(sorted(p, key=lambda c: min(c))) for v in c}
            return p, [net.dots[v].animate.set_color(cf[v]) for v in G]
        with self.say("s1") as d:
            self.play(FadeIn(tag), FadeIn(net.group), run_time=1.0)
            _, an = colour(0)
            self.play(*an, run_time=1.0)
        with self.say("s2") as d:
            code = code_block("nx.community.louvain_communities(G, seed=42)", 20)
            code.scale_to_fit_width(min(code.width, 6.0)).move_to(RIGHT * 3.6 + UP * 2.4)
            self.play(FadeIn(code, shift=UP * 0.2), run_time=0.8)
            self.play(*colour(42)[1], run_time=0.8)
            same = T("再跑一次：完全相同", 24, GREEN).next_to(code, DOWN, buff=0.3)
            self.play(Indicate(net.group, color=None, scale_factor=1.02), FadeIn(same), run_time=0.8)
        Q, K = [], []
        for s in range(50):
            p = nx.community.louvain_communities(G, seed=s)
            Q.append(nx.community.modularity(G, p)); K.append(len(p))
        print("SEEDS", min(Q), max(Q), sorted(set(K)))
        qlo, qhi = np.floor(min(Q) * 100) / 100 - 0.01, np.ceil(max(Q) * 100) / 100 + 0.01
        ax = axes([qlo, qhi, 0.01], [0, 1, 1], 5.2, 1.2, fs=18).move_to(RIGHT * 3.6 + DOWN * 0.3)
        nums = VGroup(*[MathTex(f"{x:.2f}", font_size=22, color=MUTED).next_to(ax.c2p(x, 0), DOWN, buff=0.15) for x in (qlo, qhi)])
        xl = T("模块度", 22, MUTED).next_to(ax, DOWN, buff=0.45)
        rng = np.random.default_rng(1)
        strip = VGroup(*[Dot(ax.c2p(q, 0.25 + 0.6 * rng.random()), radius=0.06, color=GOLD).set_opacity(0.8) for q in Q])
        with self.say("s3") as d:
            self.play(FadeOut(same), run_time=0.3)
            for s in (3, 11):
                self.play(*colour(s)[1], run_time=0.6)
            self.play(Create(ax.x_axis), FadeIn(nums), FadeIn(xl), LaggedStart(*[GrowFromCenter(x) for x in strip], lag_ratio=0.03), run_time=d * 0.35)
            kc = T(f"社团数：{min(K)} 到 {max(K)}" if min(K) != max(K) else f"社团数：{min(K)}", 24, INK).next_to(xl, DOWN, buff=0.3)
            self.play(FadeIn(kc), run_time=0.5)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.6)
        # Monte Carlo error of empirical p values
        p_true = 0.04
        rng = np.random.default_rng(5)
        ph1 = (rng.binomial(100, p_true, 40) + 1) / 101
        ph2 = (rng.binomial(1000, p_true, 40) + 1) / 1001
        se1, se2 = np.sqrt(p_true * (1 - p_true) / 100), np.sqrt(p_true * (1 - p_true) / 1000)
        ax1 = axes([0, 0.1, 0.05], [0, 1, 1], 8.0, 1.0, xnums=[0, 0.05, 0.1], fs=20).move_to(UP * 0.6 + RIGHT * 0.6)
        ax2 = axes([0, 0.1, 0.05], [0, 1, 1], 8.0, 1.0, xnums=[0, 0.05, 0.1], fs=20).move_to(DOWN * 1.9 + RIGHT * 0.6)
        l1 = VGroup(T("100 个随机网络", 24, INK), T(f"标准误 ≈ {se1:.3f}", 22, RED)).arrange(DOWN, buff=0.1).next_to(ax1, LEFT, buff=0.3)
        l2 = VGroup(T("1000 个随机网络", 24, INK), T(f"标准误 ≈ {se2:.3f}", 22, GREEN)).arrange(DOWN, buff=0.1).next_to(ax2, LEFT, buff=0.3)
        f = MathTex(r"\hat p=\frac{b+1}{B+1},\quad \mathrm{SE}\approx\sqrt{p(1-p)/B}", font_size=38, color=INK).to_edge(UP, buff=1.0)
        cut1 = DashedLine(ax1.c2p(0.05, 0), ax1.c2p(0.05, 1.1), color=GOLD); cut2 = DashedLine(ax2.c2p(0.05, 0), ax2.c2p(0.05, 1.1), color=GOLD)
        tr1 = DashedLine(ax1.c2p(p_true, 0), ax1.c2p(p_true, 1.1), color=MUTED); tr2 = DashedLine(ax2.c2p(p_true, 0), ax2.c2p(p_true, 1.1), color=MUTED)
        d1 = VGroup(*[Dot(ax1.c2p(min(x, 0.1), 0.2 + 0.7 * rng.random()), radius=0.06, color=RED if x >= 0.05 else INK) for x in ph1])
        d2 = VGroup(*[Dot(ax2.c2p(min(x, 0.1), 0.2 + 0.7 * rng.random()), radius=0.06, color=RED if x >= 0.05 else INK) for x in ph2])
        with self.say("s4") as d:
            self.play(FadeIn(tag), Write(f), run_time=1.0)
            cb_ = callout(f[0][3:4], "b：不小于观测值的次数", UP, GOLD, 18, 0.08)
            cB = callout(f[0][7:8], "B：随机网络总数", DOWN, BLUE, 18, 0.08)
            self.play(Create(cb_), run_time=0.7)
            self.play(Create(cB), run_time=0.7)
        with self.say("s4b") as d:
            self.play(FadeOut(cb_), FadeOut(cB), run_time=0.4)
            self.play(Create(ax1), FadeIn(l1[0]), Create(cut1), Create(tr1), run_time=0.8)
            self.play(LaggedStart(*[GrowFromCenter(x) for x in d1], lag_ratio=0.04), run_time=d * 0.35)
            self.play(FadeIn(l1[1]), run_time=0.5)
        with self.say("s5") as d:
            self.play(Create(ax2), FadeIn(l2[0]), Create(cut2), Create(tr2), run_time=0.8)
            self.play(LaggedStart(*[GrowFromCenter(x) for x in d2], lag_ratio=0.04), run_time=d * 0.3)
            self.play(FadeIn(l2[1]), run_time=0.5)
        fade_all(self)

    # ------------------------------------------------------------------ threshold sensitivity
    def threshold(self):
        tag = self.chapter("二  阈值敏感性")
        X = sim_data(p=30, seed=7)
        C = np.corrcoef(X); np.fill_diagonal(C, 0)
        dens = [0.30, 0.20, 0.12, 0.06]
        Gs = [thr_graph(C, d_) for d_ in dens]
        pos = fit(nx.spring_layout(Gs[1], seed=3), (-6.4, -1.0, -3.0, 2.6))
        G0 = Gs[0]
        dots = {v: Dot(pos[v], radius=0.1, color=BLUE) for v in G0}
        allE = set(map(tuple, map(sorted, G0.edges())))
        lines = {e: Line(pos[e[0]], pos[e[1]], color=BLUE, stroke_width=1.6, stroke_opacity=0.5) for e in allE}
        sweep = np.linspace(0.04, 0.32, 15)
        kk = [2 * thr_graph(C, d_).number_of_edges() / 30 for d_ in sweep]
        cc = [nx.average_clustering(thr_graph(C, d_)) for d_ in sweep]
        ax = axes([0, 0.35, 0.1], [0, 1, 0.5], 5.0, 3.2, xnums=[0.1, 0.2, 0.3], ynums=[0, 0.5, 1], fs=20).move_to(RIGHT * 3.6 + DOWN * 0.8)
        xl = xlabel(ax, "密度（阈值从高到低）", 20, 0.3)
        tl = T("阈值", 24, MUTED).move_to(RIGHT * 2.2 + UP * 2.6)
        tv = T(f"保留最强的 {int(dens[0] * 100)}% 的边", 24, GOLD).next_to(tl, RIGHT, buff=0.3)

        def hubs(G):
            return [v for v, _ in sorted(G.degree(), key=lambda x: (-x[1], x[0]))[:3]]
        hub_rings = VGroup(*[Circle(radius=0.2, color=GOLD, stroke_width=3).move_to(pos[h]) for h in hubs(G0)])
        with self.say("t1") as d:
            self.play(FadeIn(tag), *[GrowFromCenter(x) for x in dots.values()], *[Create(l) for l in lines.values()], run_time=1.2)
            self.play(FadeIn(tl), FadeIn(tv), Create(hub_rings), run_time=0.8)
        with self.say("t2") as d:
            for d_, G in zip(dens[1:], Gs[1:]):
                keep = set(map(tuple, map(sorted, G.edges())))
                nr = VGroup(*[Circle(radius=0.2, color=GOLD, stroke_width=3).move_to(pos[h]) for h in hubs(G)])
                self.play(*[l.animate.set_stroke(opacity=0) for e, l in lines.items() if e not in keep],
                          Transform(tv, T(f"保留最强的 {int(round(d_ * 100))}% 的边", 24, GOLD).move_to(tv, aligned_edge=LEFT)),
                          Transform(hub_rings, nr), run_time=max(0.6, d * 0.22))
        with self.say("t3") as d:
            self.play(Create(ax), FadeIn(xl), run_time=0.8)
            kmax = max(kk)
            c1 = ax.plot_line_graph(sweep, np.array(kk) / kmax, line_color=BLUE, vertex_dot_radius=0.05, vertex_dot_style={"color": BLUE}, stroke_width=4)
            c2 = ax.plot_line_graph(sweep, cc, line_color=GOLD, vertex_dot_radius=0.05, vertex_dot_style={"color": GOLD}, stroke_width=4)
            lg = VGroup(T("平均度（相对值）", 20, BLUE), T("平均聚集系数", 20, GOLD)).arrange(DOWN, aligned_edge=LEFT, buff=0.1).next_to(ax, UP, buff=0.1).align_to(ax, RIGHT)
            self.play(Create(c1), Create(c2), FadeIn(lg), run_time=d * 0.4)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.6)
        self.remove(tag)
        with self.say("t4") as d:
            self.clip_on("threshold_demo.mp4", "full", "本站交互演示：脑网络阈值实验", start=0.3)
            if d < 16.5:
                self.wait(16.5 - d)
        self.clip_off()

    # ------------------------------------------------------------------ multiverse
    def multiverse(self):
        tag = self.chapter("二  多元宇宙与设定曲线")
        root = np.array([-5.6, 0, 0])
        L1 = [np.array([-3.4, y, 0]) for y in (2.0, 0, -2.0)]
        L2 = [np.array([-0.6, y, 0]) for y in np.linspace(2.7, -2.7, 12)]
        L3 = [np.array([2.6, y, 0]) for y in np.linspace(2.9, -2.9, 24)]
        e1 = VGroup(*[Line(root, p, color=BLUE, stroke_width=2) for p in L1])
        e2 = VGroup(*[Line(L1[i // 4], L2[i], color=VIOLET, stroke_width=1.6) for i in range(12)])
        e3 = VGroup(*[Line(L2[i // 2], L3[i], color=GOLD, stroke_width=1.2) for i in range(24)])
        leaves = VGroup(*[Dot(p, radius=0.06, color=GOLD) for p in L3])
        labs = VGroup(T("边的定义 ×3", 22, BLUE).move_to([-3.4, -3.55, 0]), T("密度 ×4", 22, VIOLET).move_to([-0.6, -3.55, 0]),
                      T("指标 ×2", 22, GOLD).move_to([2.6, -3.55, 0]))
        with self.say("m1") as d:
            self.play(FadeIn(tag), GrowFromCenter(Dot(root, radius=0.12, color=INK)), run_time=0.6)
            self.play(Create(e1), FadeIn(labs[0]), run_time=1.0)
            self.play(Create(e2), FadeIn(labs[1]), run_time=1.0)
            self.play(Create(e3), FadeIn(leaves), FadeIn(labs[2]), run_time=1.0)
        with self.say("m2") as d:
            eq = MathTex(r"3\times4\times2=24", font_size=52, color=GOLD).move_to(RIGHT * 5.0 + DOWN * 0.2)
            self.play(Write(eq), run_time=1.0)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.6)
        # real specification curve on simulated two-group data
        XA = sim_data(n_s=60, p=24, seed=11, shift=0.0)
        XB = sim_data(n_s=60, p=24, seed=12, shift=0.08)
        from scipy.stats import kendalltau, spearmanr

        def cmat(X, kind):
            if kind == 0:
                return np.corrcoef(X)
            if kind == 1:
                return spearmanr(X.T)[0]
            P = np.linalg.pinv(np.cov(X)); dd = np.sqrt(np.diag(P))
            return -P / np.outer(dd, dd)
        specs = []
        for k in range(3):
            CA, CB = cmat(XA, k), cmat(XB, k)
            for a in (CA, CB):
                np.fill_diagonal(a, 0)
            for dn in (0.05, 0.10, 0.15, 0.20):
                GA, GB = thr_graph(CA, dn), thr_graph(CB, dn)
                for mtr in range(2):
                    f = nx.average_clustering if mtr == 0 else nx.global_efficiency
                    specs.append((f(GB) - f(GA), k, dn, mtr))
        specs.sort(key=lambda x: x[0])
        print("SPEC", [round(s[0], 3) for s in specs])
        eff = np.array([s[0] for s in specs])
        lim = max(abs(eff.min()), abs(eff.max())) * 1.15
        ax = axes([0, 24, 4], [-lim, lim, lim], 9.6, 2.6, fs=18).move_to(UP * 1.4 + RIGHT * 0.6)
        zero = DashedLine(ax.c2p(0, 0), ax.c2p(24, 0), color=MUTED)
        yl = T("组间差异", 22, MUTED).rotate(PI / 2).next_to(ax, LEFT, buff=0.15)
        pts = VGroup(*[Dot(ax.c2p(i + 0.5, e), radius=0.07, color=GOLD if e > 0 else BLUE) for i, e in enumerate(eff)])
        rows = ["皮尔逊", "斯皮尔曼", "偏相关", "密度 5%", "10%", "15%", "20%", "聚集系数", "全局效率"]
        rowy = [-0.6 - 0.32 * r for r in range(len(rows))]
        rl = VGroup(*[T(s, 18, MUTED).move_to([ax.c2p(0, 0)[0] - 0.75, y, 0]) for s, y in zip(rows, rowy)])
        marks = VGroup()
        for i, (_, k, dn, mtr) in enumerate(specs):
            x = ax.c2p(i + 0.5, 0)[0]
            for r in (k, 3 + [0.05, 0.10, 0.15, 0.20].index(dn), 7 + mtr):
                marks.add(Square(side_length=0.2, stroke_width=0, fill_color=[BLUE, BLUE, BLUE, VIOLET, VIOLET, VIOLET, VIOLET, GOLD, GOLD][r], fill_opacity=0.9).move_to([x, rowy[r], 0]))
        grid = VGroup(*[Line([ax.c2p(0, 0)[0], y, 0], [ax.c2p(24, 0)[0], y, 0], color=MUTED, stroke_width=0.5, stroke_opacity=0.3) for y in rowy])
        with self.say("m3") as d:
            self.play(Create(ax.y_axis), Create(zero), FadeIn(yl), run_time=0.6)
            self.play(LaggedStart(*[GrowFromCenter(p) for p in pts], lag_ratio=0.04), run_time=d * 0.3)
            self.play(FadeIn(rl), FadeIn(grid), LaggedStart(*[FadeIn(m) for m in marks], lag_ratio=0.005), run_time=d * 0.3)
        with self.say("m4") as d:
            npos, nneg = int((eff > 1e-9).sum()), int((eff < -1e-9).sum())
            nz = 24 - npos - nneg
            s = T(f"{npos} 个宇宙为正，{nneg} 个为负" + (f"，{nz} 个几乎为零" if nz else ""), 24, INK).next_to(ax, UP, buff=0.15)
            self.play(FadeIn(s), run_time=0.6)
            self.play(Indicate(rl[0:3], color=BLUE), run_time=0.8)
            self.play(Indicate(rl[7:9], color=GOLD), run_time=0.8)
        fade_all(self)

    # ------------------------------------------------------------------ alternative explanations
    def alternatives(self):
        tag = self.chapter("三  替代解释")
        n = 40
        Ga, Gb = nx.gnp_random_graph(n, 0.08, seed=3), nx.gnp_random_graph(n, 0.16, seed=4)
        pa = fit(nx.circular_layout(Ga), (-6.4, -3.6, -1.6, 1.6)); pb = fit(nx.circular_layout(Gb), (-2.8, 0.0, -1.6, 1.6))
        na = NetView(Ga, pa, color=BLUE, eo=0.4, rmin=0.05, rk=0.0); nb = NetView(Gb, pb, color=GOLD, eo=0.4, rmin=0.05, rk=0.0)
        la = T(f"密度 {nx.density(Ga):.2f}", 22, BLUE).next_to(na.group, DOWN, buff=0.3)
        lb = T(f"密度 {nx.density(Gb):.2f}", 22, GOLD).next_to(nb.group, DOWN, buff=0.3)
        with self.say("a1") as d:
            self.play(FadeIn(tag), FadeIn(na.group), FadeIn(nb.group), run_time=1.0)
            self.play(FadeIn(la), FadeIn(lb), run_time=0.6)

        def apl(G):
            H = G.subgraph(max(nx.connected_components(G), key=len))
            return nx.average_shortest_path_length(H)
        ca, cb = nx.average_clustering(Ga), nx.average_clustering(Gb)
        la_, lb_ = apl(Ga), apl(Gb)
        ax = axes([0, 2, 1], [0, 0.3, 0.1], 2.4, 2.6, ynums=[0, 0.1, 0.2, 0.3], fs=16).move_to(RIGHT * 2.6 + DOWN * 0.2)
        ax2 = axes([0, 2, 1], [0, 4, 1], 2.4, 2.6, ynums=[0, 2, 4], fs=16).move_to(RIGHT * 5.6 + DOWN * 0.2)
        u1 = ax.c2p(0, 1)[1] - ax.c2p(0, 0)[1]; u2 = ax2.c2p(0, 1)[1] - ax2.c2p(0, 0)[1]
        bars = VGroup(*[Rectangle(width=0.6, height=u1 * v, stroke_width=0, fill_color=c, fill_opacity=0.9).move_to(ax.c2p(i + 0.5, 0), aligned_edge=DOWN) for i, (v, c) in enumerate(((ca, BLUE), (cb, GOLD)))],
                      *[Rectangle(width=0.6, height=u2 * v, stroke_width=0, fill_color=c, fill_opacity=0.9).move_to(ax2.c2p(i + 0.5, 0), aligned_edge=DOWN) for i, (v, c) in enumerate(((la_, BLUE), (lb_, GOLD)))])
        t1, t2 = T("聚集系数", 22, MUTED).next_to(ax, UP, buff=0.2), T("路径长度", 22, MUTED).next_to(ax2, UP, buff=0.2)
        with self.say("a2") as d:
            self.play(Create(ax), Create(ax2), FadeIn(t1), FadeIn(t2), run_time=0.8)
            self.play(grow_bars(bars, 1.4))
            same = T("都是随机网络", 24, INK).next_to(VGroup(la, lb), DOWN, buff=0.4)
            self.play(FadeIn(same), run_time=0.6)
        with self.say("a3") as d:
            self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.5)
            lens = VGroup(Circle(radius=1.0, color=INK, stroke_width=6), Line(ORIGIN, DR * 0.9, color=INK, stroke_width=10).shift(DR * 0.95)).move_to(ORIGIN)
            self.play(Create(lens), run_time=0.8)
            items = [("密度相同？", UP * 2.4 + LEFT * 3.6), ("度匹配？", UP * 2.4 + RIGHT * 3.6), ("混杂因素？", LEFT * 4.6)]
            chips = VGroup(*[chip(s, c, 26).move_to(p) for (s, p), c in zip(items, (BLUE, GREEN, GOLD))])
            chips[0].set_opacity(0.5)
            self.play(FadeIn(chips[0]), run_time=0.3)
            self.play(FadeIn(chips[1], shift=DOWN * 0.2), run_time=0.7)
            conf = T("头动 · 批次 · 细胞组成", 22, GOLD).next_to(chips[2], DOWN, buff=0.2)
            self.play(FadeIn(chips[2], shift=RIGHT * 0.2), FadeIn(conf), run_time=0.8)
        with self.say("a4") as d:
            c4 = chip("多重比较？", VIOLET, 26).move_to(RIGHT * 4.6)
            c5 = chip("同一份数据既挑又检？", RED, 26).move_to(DOWN * 2.5)
            self.play(FadeIn(c4, shift=LEFT * 0.2), run_time=0.8)
            self.play(FadeIn(c5, shift=UP * 0.2), run_time=0.8)
        fade_all(self)

    # ------------------------------------------------------------------ sample size
    def sample_size(self):
        tag = self.chapter("三  样本量")
        p = 15
        edges = p * (p - 1) // 2
        G = nx.complete_graph(p)
        pos = {v: LEFT * 3.6 + 2.1 * np.array([np.cos(v * TAU / p), np.sin(v * TAU / p), 0]) + DOWN * 0.2 for v in G}
        lines = VGroup(*[Line(pos[u], pos[v], color=BLUE, stroke_width=1, stroke_opacity=0.5) for u, v in G.edges()])
        dots = VGroup(*[Dot(pos[v], radius=0.1, color=BLUE) for v in G])
        with self.say("n1") as d:
            self.play(FadeIn(tag), FadeIn(dots), run_time=0.6)
            self.play(LaggedStart(*[Create(l) for l in lines], lag_ratio=0.01), run_time=d * 0.45)
            c = counter("15 个节点", f"{edges} 条边", BLUE).move_to(RIGHT * 3.6 + UP * 2.2)
            self.play(FadeIn(c), run_time=0.6)
        n1 = n_edge(0.2)
        n2 = n_edge(0.2, alpha=0.05 / edges, k=p - 2)
        print("NSIZE", n1, n2)
        f = MathTex(r"n\approx\left(\frac{z_{1-\alpha/2}+z_{1-\beta}}{\operatorname{artanh}\rho}\right)^2+3+k", font_size=36, color=INK).move_to(RIGHT * 3.4 + UP * 0.6)
        ax = axes([0, 2, 1], [0, 500, 250], 4.4, 2.6, ynums=[0, 250, 500], fs=18).move_to(RIGHT * 3.6 + DOWN * 2.0)
        u = ax.c2p(0, 1)[1] - ax.c2p(0, 0)[1]
        b1 = Rectangle(width=1.0, height=u * n1, stroke_width=0, fill_color=GREEN, fill_opacity=0.9).move_to(ax.c2p(0.5, 0), aligned_edge=DOWN)
        b2 = Rectangle(width=1.0, height=u * n2, stroke_width=0, fill_color=RED, fill_opacity=0.9).move_to(ax.c2p(1.5, 0), aligned_edge=DOWN)
        v1 = T(f"{int(np.ceil(n1))}", 24, GREEN, weight=BOLD).next_to(b1, UP, buff=0.08)
        v2 = T(f"{int(np.ceil(n2))}", 24, RED, weight=BOLD).next_to(b2, UP, buff=0.08)
        s1 = T("单条边", 20, MUTED).next_to(ax.c2p(0.5, 0), DOWN, buff=0.12)
        s2 = T("校正 + 偏相关", 20, MUTED).next_to(ax.c2p(1.5, 0), DOWN, buff=0.12)
        with self.say("n2") as d:
            self.play(c.animate.scale(0.8).move_to(RIGHT * 3.6 + UP * 2.6), Write(f), run_time=d * 0.35)
        with self.say("n2b") as d:
            k1 = callout(f[0][3:14], "显著性水平 + 统计功效", UP, GOLD, 18, 0.06)
            k2 = callout(f[0][15:22], "相关系数的变换", DOWN, BLUE, 18, 0.06)
            k3 = callout(f[0][-1], "控制的变量数", DOWN, GREEN, 18, 0.06)
            for k_ in (k1, k2, k3):
                self.play(Create(k_), run_time=0.7)
        with self.say("n2c") as d:
            self.play(FadeOut(k1), FadeOut(k2), FadeOut(k3), run_time=0.4)
            self.play(Create(ax), FadeIn(s1), GrowFromEdge(b1, DOWN), run_time=1.0)
            self.play(FadeIn(v1), run_time=0.5)
        with self.say("n3") as d:
            self.play(FadeIn(s2), GrowFromEdge(b2, DOWN), run_time=1.2)
            self.play(FadeIn(v2), run_time=0.5)
        fade_all(self)

    # ------------------------------------------------------------------ recap
    def recap(self):
        with self.say("r1") as d:
            head = T("三个要点", 40, INK, weight=BOLD).to_edge(UP, buff=0.7)
            self.play(Write(head), run_time=0.8)
        items = [("r2", GOLD, "好问题：说清比较对象和判断标准"),
                 ("r3", BLUE, "好分析：从原始数据一键重跑"),
                 ("r4", GREEN, "好结论：在合理的分析选择下都成立")]
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
