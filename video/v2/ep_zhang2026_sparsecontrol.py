"""Paper explainer: 语言模型的稀疏内部控制."""
import numpy as np

from common import *  # noqa: F401,F403
from ep_robustness import counter

TITLE = "稀疏内部控制：在语言模型里只按住几处"

LINES = {
    # hook
    "h0": "大语言模型，是一个根据前文、一个词一个词预测下文的程序。画面里，是它工作原理的一段动画。",
    "h1": "训练好的模型，内部是一层又一层的计算。这里每个点，代表模型内部的一个计算位置。参数已经全部冻结，不再改动。",
    "h2": "现在，我们只想改变它的一种行为，比如让回答的情绪更积极。右边的表盘，就代表这种行为。",
    "h3": "这项研究借用网络控制里驱动节点的想法：只在模型内部按住少数几处，就是这三个黄圈。表盘就转过去了。",
    "h4": "这样的控制要满足三点：局部，只改目标行为；可逆，撤掉就恢复；有选择，别的行为尽量不受影响。",
    "h5": "【慢】这项研究把这个问题，叫作稀疏内部控制。",
    # parts
    "k0": "这一期分四部分。",
    "k1": "第一部分，控制节点是什么，以及为什么要联合挑选。",
    "k2": "第二部分，两种挑选方法，和六个评价轴。",
    "k3": "第三部分，哪些结论成立，哪些不成立。",
    "k4": "第四部分，意义和局限。",
    # nodes
    "n0": "先看第一部分。在结构可控性里，驱动节点是施加输入信号的节点。结构可控性这一页的交互演示里，红色的就是驱动节点。",
    "n1": "在模型里，候选的控制节点不是图里的一个点，而是一个站点，加上一个干预方向。站点，就是某一层、某个位置算出来的激活，也就是蓝色这个向量。",
    "n2": "干预，是在模型推理的时候，给这个站点的激活加上一个补丁。画面下方是它的式子。",
    "n2b": "左边是原来的激活；加号后面，是干预方向，乘以强度贝塔。强度越大，绿色的结果向量偏得越多。",
    "n3": "参数从头到尾不动。把强度调回零，模型就恢复原样。",
    "n4": "代价有两部分：一是在多少处打补丁，叫稀疏度；二是补丁有多强，叫干预能量，是各个强度按权重平方后加起来。",
    # joint
    "j1": "下面看怎么挑节点。每个候选节点，对目标行为都有一个一阶效应，也就是轻轻推一下，目标行为跟着变多少，画成一个箭头。所有箭头放在一起，叫效应字典。",
    "j2": "黄色箭头，是我们想要的行为位移。右上角的式子说：目标位移，约等于效应字典乘以一组强度。",
    "j3": "右边列出了每个候选单独打的分。如果挑分数最高的两个，它们方向几乎重合，要凑到目标，强度得非常大，还要互相抵消，能量约四十九。",
    "j4": "换成方向互补的两个候选，不大的强度就够了，能量约三。",
    "j5": "【慢】所以驱动节点要联合挑选，不能简单按分数取前几名。字典只负责提议，最后必须在真实模型上验证。",
    # selectors
    "s1": "下面进入第二部分。第一种挑法叫驱动节点正交匹配追踪：每一步，加入最能解释剩余位移的候选。你看，黄色的剩余位移一步步缩短。",
    "s2": "它适合每个样本都有各自目标的任务，比如间接宾语识别，和多选题。",
    "s3": "第二种是覆盖式选择。右边每个圆圈是一条提示。候选能把某条提示往正确方向推，就得分；提示一旦被覆盖，就不再重复计分。",
    "s4": "所以它偏好能覆盖更多新提示的候选，适合情感、拒答这类，要求同一干预在许多提示上一致起作用的任务。",
    # axes
    "e1": "能把目标推过去，还不等于是一个可用的控制手段。这项研究用六个评价轴，各自排除一种失败。",
    "e2": "可达：名义强度下，能不能推到目标。反转：反向施加，能不能沿原路退回来。",
    "e3": "剂量响应：加大强度，效果是否单调增加。反馈：固定这组节点，只调总剂量，能不能追踪不同的目标值。",
    "e4": "保持：无关提示上的输出变化够不够小。复用：搬到新的提示上，还管不管用。",
    # positive
    "r1": "下面进入第三部分。实验从一个小型语言模型，一直做到四十亿参数的模型。最多八个驱动节点，就能明显移动目标行为。",
    "r2": "归一化残差，是离目标还差多少，占所需位移的比例，越低越好。在间接宾语识别上，它是零点三八六；同样预算的随机挑选是一点四三。",
    "r3": "闭环调节时，二十四个目标端点全部命中，平均只需要不到四次评估。",
    "r4": "多选题用逐样本方向时，人文题命中了四十八个端点中的四十六个。固定站点、在新题目上重新拟合强度，平均恢复百分之九十九点二。",
    # negative
    "x1": "但如果连强度也冻结，直接搬到新题目上，人文题平均只恢复百分之二点一。也就是说，站点能迁移，干预本身却不能直接搬用。",
    "x2": "改用训练均值的冻结方向做反馈，人文题只命中四十八个端点中的八个。",
    "x3": "【慢】拒答任务的剂量响应完全单调，正式的反转检验却全部失败。单向有效，不等于可逆。",
    "x4": "在三十二道无关题目上，输出分布的平均变化，只在八个种子中的四个达标。种子，就是一次随机重复。",
    # meaning
    "l1": "最后是第四部分。这和药物干预很像：我们也希望靶点少、可以撤销、副作用小。",
    "l1b": "药物怎样作用于靶点，药理学里有专门的研究。画面是一段药效学的科普。",
    "l2": "六轴协议提醒我们，靶点能推动指标还不够，还要问剂量响应、能否反向、能否在新患者身上复用，以及对其他通路的影响。",
    "l3": "局限也要看清。第一，任务和模型有限；读数只用了首个生成的词；逐样本方向还用到了测试对的信息。",
    "l4": "第二，实验里用的是普通岭回归，没有强制能量约束，所以没有建立完整的联合证书。这也不是线性系统意义上的完全可控。",
    "l5": "【慢】一句话：少数几处内部干预确实能推动行为，但哪些控制性质成立，要一轴一轴地检验。",
    # recap
    "z0": "好，我们来总结一下。",
    "z1": "第一，控制节点是站点加方向，干预是推理时的补丁，强度归零就恢复。",
    "z2": "第二，节点要联合挑选，因为方向重合的高分候选，需要很大的能量。",
    "z3": "第三，可达和反馈调节成立，冻结复用、反转和保持并不总是成立。",
}

Q = np.array([2.0, 1.2])
CANDS = {"g1": np.array([1.7, 1.3]), "g2": np.array([1.78, 1.3]), "g3": np.array([1.4, -0.3]), "g4": np.array([0.2, 1.3]),
         "g5": np.array([-0.6, 0.9]), "g6": np.array([0.9, -1.0])}


def layered(n_layers=6, per=7, x0=-5.0, x1=5.0, h=4.6, seed=1):
    rng = np.random.default_rng(seed)
    xs = np.linspace(x0, x1, n_layers)
    pts = [[np.array([x, (j - (per - 1) / 2) * h / (per - 1), 0]) for j in range(per)] for x in xs]
    edges = []
    for i in range(n_layers - 1):
        for a in range(per):
            for b in range(per):
                if rng.random() < 0.35:
                    edges.append((pts[i][a], pts[i + 1][b]))
    return pts, edges


class Episode(Narrated):
    LINES = LINES

    def construct(self):
        self.hook()
        self.parts()
        self.nodes()
        self.joint()
        self.selectors()
        self.axes6()
        self.positive()
        self.negative()
        self.meaning()
        self.recap()

    def clear(self, rt=0.8, keep=None):
        self.play(*[FadeOut(m) for m in self.mobjects if m is not keep], run_time=rt)

    def gauge(self, center, val=0.0, label="情绪"):
        arc = Arc(radius=1.0, start_angle=PI, angle=-PI, color=MUTED, stroke_width=6).move_arc_center_to(center)
        cold = Arc(radius=1.0, start_angle=PI, angle=-PI / 2, color=BLUE, stroke_width=6).move_arc_center_to(center)
        warm = Arc(radius=1.0, start_angle=PI / 2, angle=-PI / 2, color=GOLD, stroke_width=6).move_arc_center_to(center)
        tr = ValueTracker(val)
        needle = always_redraw(lambda: Line(center, center + 0.9 * np.array([np.cos(PI / 2 - tr.get_value() * PI / 2), np.sin(PI / 2 - tr.get_value() * PI / 2), 0]),
                                            color=INK, stroke_width=5))
        lab = T(label, 22, MUTED).next_to(center, DOWN, buff=0.2)
        return VGroup(cold, warm, lab), needle, tr

    # ------------------------------------------------------------------ hook
    def hook(self):
        pts, edges = layered(x1=3.0)
        dots = VGroup(*[Dot(p, radius=0.11, color=BLUE) for L in pts for p in L])
        lines = VGroup(*[Line(a, b, color=MUTED, stroke_width=1.2, stroke_opacity=0.35) for a, b in edges])
        lock = VGroup(RoundedRectangle(corner_radius=0.08, width=0.5, height=0.4, color=MUTED, fill_opacity=0.0, stroke_width=3),
                      Arc(radius=0.17, start_angle=0, angle=PI, color=MUTED, stroke_width=3).shift(UP * 0.2))
        lock.move_to([-5.0, 3.0, 0])
        lt = T("参数冻结", 22, MUTED).next_to(lock, RIGHT, buff=0.2)
        with self.say("h0") as d:
            self.clip_on("yt_3b1b_llm.mp4", "center", "视频：3Blue1Brown · YouTube", start=60)
        self.clip_off()
        with self.say("h1") as d:
            self.play(LaggedStart(*[FadeIn(x, scale=0.5) for x in dots], lag_ratio=0.01), run_time=d * 0.4)
            self.play(Create(lines), run_time=d * 0.3)
            self.play(FadeIn(lock), FadeIn(lt), run_time=0.5)
        gfix, needle, tr = self.gauge(np.array([5.2, -0.2, 0]), 0.0)
        with self.say("h2") as d:
            self.play(FadeIn(gfix), FadeIn(needle), run_time=0.8)
            arrow = Arrow([3.3, -0.1, 0], [4.2, -0.1, 0], color=MUTED, buff=0)
            self.play(GrowArrow(arrow), run_time=0.5)
            self.play(tr.animate.set_value(-0.5), run_time=0.8)
        sites = [(1, 2), (2, 5), (4, 3)]
        with self.say("h3") as d:
            rings = VGroup(*[Circle(radius=0.24, color=GOLD, stroke_width=4).move_to(pts[i][j]) for i, j in sites])
            self.play(dots.animate.set_opacity(0.5), LaggedStart(*[Create(r) for r in rings], lag_ratio=0.3), run_time=1.4)
            self.play(*[dots[i * 7 + j].animate.set_color(GOLD).set_opacity(1) for i, j in sites], tr.animate.set_value(0.7), run_time=1.4)
        with self.say("h4") as d:
            icons = VGroup(T("局部", 30, GOLD, weight=BOLD), T("可逆", 30, GREEN, weight=BOLD), T("有选择", 30, BLUE, weight=BOLD)).arrange(RIGHT, buff=1.0).to_edge(DOWN, buff=0.35)
            self.play(FadeIn(icons[0], shift=UP * 0.2), run_time=0.6)
            self.play(FadeIn(icons[1], shift=UP * 0.2), tr.animate.set_value(-0.5), *[dots[i * 7 + j].animate.set_color(BLUE) for i, j in sites], run_time=1.0)
            self.play(tr.animate.set_value(0.7), *[dots[i * 7 + j].animate.set_color(GOLD) for i, j in sites], run_time=0.8)
            self.play(FadeIn(icons[2], shift=UP * 0.2), run_time=0.6)
        with self.say("h5") as d:
            name = T("稀疏内部控制", 52, INK, weight=BOLD)
            bg = BackgroundRectangle(name, color=BG, fill_opacity=0.9, buff=0.25)
            self.play(FadeIn(bg), Write(name), run_time=1.4)
        self.remove(needle)
        self.clear()

    # ------------------------------------------------------------------ nodes
    def parts(self):
        head, items = slide("这一期分四部分", ["一  控制节点与联合挑选", "二  挑选方法与评价", "三  成立与不成立", "四  意义与局限"])
        with self.say("k0") as d:
            self.play(FadeIn(head, shift=RIGHT * 0.3), run_time=0.6)
        for k, it in zip(("k1", "k2", "k3", "k4"), items):
            with self.say(k) as d:
                self.play(FadeIn(it, shift=RIGHT * 0.3), run_time=0.6)
        self.wait(0.6)
        self.play(FadeOut(head), FadeOut(items), run_time=0.6)

    def recap(self):
        head, items = slide("小结", ["站点加方向；推理时补丁，强度归零即恢复", "联合挑选：方向重合的高分候选很费能量", "可达、反馈成立；冻结复用、反转、保持不总成立"], accent=GOLD)
        with self.say("z0") as d:
            self.play(FadeIn(head, shift=RIGHT * 0.3), run_time=0.6)
        for k, it in zip(("z1", "z2", "z3"), items):
            with self.say(k) as d:
                self.play(FadeIn(it, shift=RIGHT * 0.3), run_time=0.6)
        self.wait(1.0)
        self.play(FadeOut(head), FadeOut(items), run_time=0.8)

    def nodes(self):
        with self.say("n0") as d:
            self.clip_on("matching_density.mp4", "full", "本站交互演示：驱动节点", start=0.3)
        self.wait(max(0.05, 12.0 - (self.renderer.time - self._clip['t0'])))
        self.clip_off()
        tag = self.chapter("一  控制节点与联合挑选")
        pts, edges = layered(x0=-6.0, x1=-1.0, h=4.0, per=6)
        dots = VGroup(*[Dot(p, radius=0.09, color=BLUE).set_opacity(0.6) for L in pts for p in L])
        lines = VGroup(*[Line(a, b, color=MUTED, stroke_width=1, stroke_opacity=0.25) for a, b in edges])
        site = pts[3][2]
        with self.say("n1") as d:
            self.play(FadeIn(tag), FadeIn(lines), FadeIn(dots), run_time=1.0)
            ring = Circle(radius=0.25, color=GOLD, stroke_width=4).move_to(site)
            self.play(Create(ring), run_time=0.6)
            O = np.array([2.2, -1.6, 0])
            box = RoundedRectangle(corner_radius=0.15, width=6.0, height=5.0, stroke_color=GOLD, stroke_width=2).move_to([3.2, 0.2, 0])
            zoom = VGroup(DashedLine(ring.get_right(), box.get_left() + UP * 1.0, color=GOLD, stroke_width=2),
                          DashedLine(ring.get_right(), box.get_left() + DOWN * 1.0, color=GOLD, stroke_width=2))
            self.play(Create(zoom), Create(box), run_time=0.8)
            h = Arrow(O, O + np.array([2.6, 1.2, 0]), buff=0, color=BLUE, stroke_width=6)
            hl = MathTex(r"h_s(x)", font_size=40, color=BLUE).next_to(h.get_end(), RIGHT, buff=0.1)
            st = T("站点：某层、某个位置的激活", 22, MUTED).next_to(box.get_top(), DOWN, buff=0.2)
            self.play(GrowArrow(h), FadeIn(hl), FadeIn(st), run_time=1.0)
            u = Arrow(O, O + np.array([-0.3, 1.0, 0]), buff=0, color=GOLD, stroke_width=6)
            ul = MathTex(r"u_v", font_size=40, color=GOLD).next_to(u.get_end(), LEFT, buff=0.1)
            dl = T("干预方向", 22, GOLD).next_to(ul, LEFT, buff=0.15)
            self.play(GrowArrow(u), FadeIn(ul), FadeIn(dl), run_time=0.8)
        beta = ValueTracker(0.0)
        tip = O + np.array([2.6, 1.2, 0])
        add = always_redraw(lambda: Arrow(tip, tip + beta.get_value() * np.array([-0.3, 1.0, 0]), buff=0, color=GOLD, stroke_width=5,
                                          max_tip_length_to_length_ratio=0.3) if beta.get_value() > 0.02 else VectorizedPoint(tip))
        res = always_redraw(lambda: Arrow(O, tip + beta.get_value() * np.array([-0.3, 1.0, 0]), buff=0, color=GREEN, stroke_width=6)
                            if beta.get_value() > 0.02 else VectorizedPoint(O))
        bl = always_redraw(lambda: MathTex(r"\beta=%.1f" % beta.get_value(), font_size=36, color=INK).move_to(box.get_corner(DR) + np.array([-1.0, 0.4, 0])))
        with self.say("n2") as d:
            f = MathTex(r"h_s(x)\leftarrow h_s(x)+\beta_v\,u_v(x)", font_size=42, color=INK).next_to(box, DOWN, buff=0.25)
            self.play(Write(f), run_time=1.2)
        with self.say("n2b") as d:
            self.add(add, res, bl)
            self.play(Indicate(f[0][0:5], color=BLUE), run_time=1.0)
            self.play(beta.animate.set_value(1.6), run_time=1.6)
        with self.say("n3") as d:
            self.play(beta.animate.set_value(0.0), run_time=1.6)
            back = T("β = 0：恢复原模型", 26, GREEN).move_to(box.get_bottom() + UP * 0.45 + LEFT * 1.0)
            self.play(FadeIn(back), run_time=0.6)
        with self.say("n4") as d:
            self.remove(add, res, bl)
            self.play(*[FadeOut(m) for m in (box, zoom, h, hl, st, u, ul, dl, back, f)], run_time=0.6)
            more = [pts[1][4], pts[4][1]]
            rr = VGroup(*[Circle(radius=0.25, color=GOLD, stroke_width=4).move_to(p) for p in more])
            self.play(Create(rr), run_time=0.8)
            c1 = VGroup(T("补丁数（稀疏度）", 26, INK), T("3 处", 34, GOLD, weight=BOLD)).arrange(DOWN, buff=0.15).move_to([3.0, 1.2, 0])
            c2 = VGroup(T("干预能量", 26, INK), MathTex(r"E(\beta)=\beta^\top W\beta", font_size=44, color=GOLD)).arrange(DOWN, buff=0.2).move_to([3.0, -1.2, 0])
            self.play(FadeIn(c1, shift=UP * 0.2), run_time=0.8)
            self.play(FadeIn(c2, shift=UP * 0.2), run_time=0.8)
        self.clear()

    # ------------------------------------------------------------------ joint selection
    def joint(self):
        tag = self.chapter("一  控制节点与联合挑选")
        O = np.array([-0.8, 0.0, 0]); s = 0.5

        def P(v):
            return O + s * np.array([v[0], v[1], 0])
        axes = VGroup(Line(O + LEFT * 4.3, O + RIGHT * 3.6, color=MUTED, stroke_width=2, stroke_opacity=0.6),
                      Line(O + DOWN * 3.2, O + UP * 3.4, color=MUTED, stroke_width=2, stroke_opacity=0.6))
        cols = {"g1": RED, "g2": RED, "g3": GREEN, "g4": GREEN, "g5": MUTED, "g6": MUTED}
        arrs = {k: Arrow(O, P(v), buff=0, color=cols[k], stroke_width=5, max_tip_length_to_length_ratio=0.15) for k, v in CANDS.items()}
        labs = {k: MathTex(k.replace("g", "g_"), font_size=30, color=cols[k]).next_to(P(v), UR if v[1] >= 0 else DR, buff=0.05) for k, v in CANDS.items()}
        qa = Arrow(O, P(Q), buff=0, color=GOLD, stroke_width=7, max_tip_length_to_length_ratio=0.12)
        ql = MathTex("q", font_size=40, color=GOLD).next_to(P(Q), RIGHT, buff=0.12)
        with self.say("j1") as d:
            self.play(FadeIn(tag), FadeIn(axes), run_time=0.6)
            self.play(LaggedStart(*[GrowArrow(a) for a in arrs.values()], lag_ratio=0.15), *[FadeIn(l) for l in labs.values()], run_time=1.6)
            dict_l = T("效应字典 G", 26, INK).to_corner(UR, buff=0.5)
            self.play(FadeIn(dict_l), run_time=0.5)
        with self.say("j2") as d:
            self.play(GrowArrow(qa), FadeIn(ql), run_time=1.0)
            f = MathTex(r"q\approx G\beta", font_size=48, color=GOLD).next_to(dict_l, DOWN, buff=0.3)
            self.play(Write(f), run_time=1.0)
        scores = {k: float(v @ Q / np.linalg.norm(Q)) for k, v in CANDS.items()}

        def solve(a, b):
            M = np.c_[CANDS[a], CANDS[b]]
            return np.linalg.solve(M, Q)
        with self.say("j3") as d:
            sc = VGroup(*[T(f"{k}: {scores[k]:.2f}", 22, cols[k]) for k in sorted(scores, key=lambda k: -scores[k])]).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
            sc.next_to(f, DOWN, buff=0.35).align_to(f, RIGHT)
            sh = T("单独打分", 20, MUTED).next_to(sc, UP, buff=0.1)
            VGroup(sh, sc).shift(DOWN * 0.15)
            self.play(FadeIn(sh), FadeIn(sc), run_time=0.8)
            b1, b2 = solve("g1", "g2")
            p1 = P(b1 * CANDS["g1"]); p2 = p1 + s * np.array([*(b2 * CANDS["g2"]), 0])
            l1 = Arrow(O, p1, buff=0, color=RED, stroke_width=4, max_tip_length_to_length_ratio=0.05)
            l2 = Arrow(p1, p2, buff=0, color=RED, stroke_width=4, max_tip_length_to_length_ratio=0.05)
            self.play(*[a.animate.set_opacity(0.25) for k, a in arrs.items() if k not in ("g1", "g2")], run_time=0.5)
            self.play(GrowArrow(l1), run_time=0.8)
            self.play(GrowArrow(l2), run_time=0.8)
            e12 = b1 ** 2 + b2 ** 2
            t12 = VGroup(T("选 g1、g2", 24, RED), MathTex(r"\beta=(%.1f,\ %.1f)" % (b1, b2), font_size=32, color=RED),
                         T(f"能量 ≈ {e12:.0f}", 26, RED, weight=BOLD)).arrange(DOWN, buff=0.12).move_to([4.2, -0.9, 0])
            self.play(FadeIn(t12), run_time=0.6)
        with self.say("j4") as d:
            b3, b4 = solve("g3", "g4")
            p3 = P(b3 * CANDS["g3"]); p4 = p3 + s * np.array([*(b4 * CANDS["g4"]), 0])
            l3 = Arrow(O, p3, buff=0, color=GREEN, stroke_width=5, max_tip_length_to_length_ratio=0.1)
            l4 = Arrow(p3, p4, buff=0, color=GREEN, stroke_width=5, max_tip_length_to_length_ratio=0.1)
            self.play(l1.animate.set_opacity(0.2), l2.animate.set_opacity(0.2), *[arrs[k].animate.set_opacity(1 if k in ("g3", "g4") else 0.25) for k in arrs], run_time=0.5)
            self.play(GrowArrow(l3), run_time=0.7)
            self.play(GrowArrow(l4), run_time=0.7)
            e34 = b3 ** 2 + b4 ** 2
            t34 = VGroup(T("选 g3、g4", 24, GREEN), MathTex(r"\beta=(%.1f,\ %.1f)" % (b3, b4), font_size=32, color=GREEN),
                         T(f"能量 ≈ {e34:.0f}", 26, GREEN, weight=BOLD)).arrange(DOWN, buff=0.12).next_to(t12, DOWN, buff=0.4)
            self.play(FadeIn(t34), run_time=0.6)
        with self.say("j5") as d:
            msg = T("联合挑选，而不是按分数取前几名", 28, GOLD, weight=BOLD).move_to([-2.2, -3.55, 0])
            bgm = BackgroundRectangle(msg, color=BG, fill_opacity=0.9, buff=0.1)
            self.play(FadeIn(bgm), Write(msg), run_time=1.4)
            ver = T("→ 在真实模型上验证", 24, INK).next_to(msg, RIGHT, buff=0.4)
            self.play(FadeIn(ver), run_time=0.6)
        self.clear()

    # ------------------------------------------------------------------ selectors
    def selectors(self):
        tag = self.chapter("二  挑选方法与评价")
        O = np.array([-5.4, -1.6, 0]); s = 1.35

        def P(v):
            return O + s * np.array([v[0], v[1], 0])
        cols = {k: MUTED for k in CANDS}
        arrs = {k: Arrow(O, P(v), buff=0, color=MUTED, stroke_width=4, max_tip_length_to_length_ratio=0.15) for k, v in CANDS.items()}
        G = np.c_[[CANDS[k] for k in CANDS]].T
        keys = list(CANDS)
        r = Q.copy(); sel = []
        steps = []
        for _ in range(2):
            corr = [abs(CANDS[k] @ r) / np.linalg.norm(CANDS[k]) if k not in sel else -1 for k in keys]
            k = keys[int(np.argmax(corr))]
            sel.append(k)
            M = np.c_[[CANDS[x] for x in sel]].T
            b, *_ = np.linalg.lstsq(M, Q, rcond=None)
            r = Q - M @ b
            steps.append((k, r.copy()))
        res = Arrow(O, P(Q), buff=0, color=GOLD, stroke_width=7, max_tip_length_to_length_ratio=0.12)
        rl = T("剩余位移", 22, GOLD).next_to(P(Q), UP, buff=0.12)
        with self.say("s1") as d:
            self.play(FadeIn(tag), *[GrowArrow(a) for a in arrs.values()], run_time=1.0)
            self.play(GrowArrow(res), FadeIn(rl), run_time=0.8)
            cur = Q.copy()
            for i, (k, rr) in enumerate(steps):
                self.play(arrs[k].animate.set_color(GREEN).set_stroke(width=6), run_time=0.6)
                new = Arrow(O, P(rr), buff=0, color=GOLD, stroke_width=7, max_tip_length_to_length_ratio=0.3) if np.linalg.norm(rr) > 0.05 else Dot(O, radius=0.1, color=GOLD)
                nrl = T(f"第 {i + 1} 步后：剩 {np.linalg.norm(rr) / np.linalg.norm(Q) * 100:.0f}%", 22, GOLD).move_to([-2.0, 2.8 - i * 0.5, 0])
                self.play(Transform(res, new), FadeIn(nrl), *([FadeOut(rl)] if i == 0 else []), run_time=0.9)
        with self.say("s2") as d:
            tk = VGroup(T("逐样本目标", 26, GREEN, weight=BOLD), T("间接宾语识别 · 多选题", 22, INK)).arrange(DOWN, buff=0.15).move_to([-1.6, -3.3, 0])
            self.play(FadeIn(tk), run_time=0.8)
        # coverage
        rng = np.random.default_rng(6)
        prompts = VGroup(*[Circle(radius=0.2, color=MUTED, stroke_width=3) for _ in range(16)]).arrange_in_grid(rows=4, cols=4, buff=0.35).move_to([3.4, 0.6, 0])
        cover = {"c1": [0, 1, 2, 4, 5], "c2": [1, 2, 5, 6], "c3": [9, 10, 13, 14, 15, 11], "c4": [3, 7, 8, 12], "c5": [0, 4, 8, 12]}
        cands = VGroup(*[VGroup(Square(0.4, color=BLUE, stroke_width=3), T(k, 18, BLUE)) for k in cover]).arrange(RIGHT, buff=0.25).next_to(prompts, DOWN, buff=0.5)
        for c in cands:
            c[1].move_to(c[0])
        with self.say("s3") as d:
            self.play(FadeIn(prompts, lag_ratio=0.05), FadeIn(cands), run_time=1.0)
            lab = T("提示", 22, MUTED).next_to(prompts, UP, buff=0.2)
            self.play(FadeIn(lab), run_time=0.3)
            covered = set()
            names = list(cover)
            for step in range(3):
                gain = {k: len(set(v) - covered) for k, v in cover.items()}
                k = max(gain, key=gain.get)
                i = names.index(k)
                new = set(cover[k]) - covered
                self.play(cands[i][0].animate.set_fill(BLUE, opacity=0.6), *[prompts[j].animate.set_fill(GREEN, opacity=0.8).set_stroke(GREEN) for j in new],
                          *[Indicate(prompts[j], color=MUTED, scale_factor=1.1) for j in set(cover[k]) & covered], run_time=0.9)
                covered |= new
        with self.say("s4") as d:
            tk2 = VGroup(T("群体级目标", 26, BLUE, weight=BOLD), T("情感 · 拒答", 22, INK)).arrange(DOWN, buff=0.15).next_to(cands, DOWN, buff=0.35)
            self.play(FadeIn(tk2), run_time=0.8)
            cv = T(f"已覆盖 {len(covered)} / 16", 24, GREEN).next_to(lab, RIGHT, buff=0.6)
            self.play(FadeIn(cv), run_time=0.5)
        self.clear()

    # ------------------------------------------------------------------ six axes
    def axes6(self):
        tag = self.chapter("二  挑选方法与评价")
        names = [("可达", GOLD), ("反转", VIOLET), ("剂量响应", BLUE), ("反馈", GREEN), ("保持", RED), ("复用", INK)]
        panels = VGroup()
        for n, c in names:
            r = RoundedRectangle(corner_radius=0.15, width=3.8, height=2.6, stroke_color=c, stroke_width=2.5, fill_color="#182133", fill_opacity=1)
            t = T(n, 26, c, weight=BOLD).next_to(r.get_top(), DOWN, buff=0.15)
            panels.add(VGroup(r, t))
        panels.arrange_in_grid(rows=2, cols=3, buff=(0.4, 0.4)).shift(DOWN * 0.3)

        def ctr(i):
            return panels[i][0].get_center() + DOWN * 0.25
        with self.say("e1") as d:
            self.play(FadeIn(tag), LaggedStart(*[FadeIn(p, shift=UP * 0.2) for p in panels], lag_ratio=0.12), run_time=d * 0.6)
            self.play(panels.animate.set_opacity(0.3), run_time=0.5)
        # 1 reach & 2 reversal
        c0, c1 = ctr(0), ctr(1)
        st0 = Dot(c0 + LEFT * 1.2, color=INK); tg0 = Circle(radius=0.2, color=GOLD).move_to(c0 + RIGHT * 1.2)
        ar0 = Arrow(c0 + LEFT * 1.2, c0 + RIGHT * 1.0, buff=0, color=GOLD)
        ar1a = Arrow(c1 + LEFT * 1.2 + UP * 0.25, c1 + RIGHT * 1.2 + UP * 0.25, buff=0, color=VIOLET)
        ar1b = Arrow(c1 + RIGHT * 1.2 + DOWN * 0.25, c1 + LEFT * 1.2 + DOWN * 0.25, buff=0, color=VIOLET)
        with self.say("e2") as d:
            self.play(panels[0].animate.set_opacity(1), run_time=0.3)
            self.play(FadeIn(st0), Create(tg0), GrowArrow(ar0), run_time=1.0)
            self.wait(d * 0.15)
            self.play(panels[1].animate.set_opacity(1), run_time=0.3)
            self.play(GrowArrow(ar1a), run_time=0.7)
            self.play(GrowArrow(ar1b), run_time=0.7)
        # 3 dose & 4 feedback
        c2, c3 = ctr(2), ctr(3)
        xs = np.linspace(-1.3, 1.3, 6)
        dose = VGroup(*[Dot(c2 + np.array([x, -0.7 + (i / 5) * 1.3, 0]), radius=0.08, color=BLUE) for i, x in enumerate(xs)])
        dl = VGroup(Line(c2 + np.array([-1.5, -0.85, 0]), c2 + np.array([1.5, -0.85, 0]), color=MUTED, stroke_width=2),
                    T("剂量 γ", 18, MUTED).move_to(c2 + np.array([1.1, -1.05, 0])))
        tgts = VGroup(*[DashedLine(c3 + np.array([-1.4, y, 0]), c3 + np.array([1.4, y, 0]), color=GREEN, stroke_width=2) for y in (-0.6, 0.0, 0.6)])
        fb = Dot(c3 + np.array([0, -0.9, 0]), radius=0.1, color=GREEN)
        with self.say("e3") as d:
            self.play(panels[2].animate.set_opacity(1), FadeIn(dl), run_time=0.3)
            self.play(LaggedStart(*[FadeIn(x, scale=0.5) for x in dose], lag_ratio=0.2), run_time=1.2)
            self.wait(d * 0.15)
            self.play(panels[3].animate.set_opacity(1), Create(tgts), FadeIn(fb), run_time=0.6)
            for y in (-0.6, 0.6, 0.0):
                self.play(fb.animate.move_to(c3 + np.array([0, y, 0])), run_time=0.5)
        # 5 preservation & 6 reuse
        c4, c5 = ctr(4), ctr(5)
        hv = [0.3, 0.7, 1.0, 0.6, 0.25]
        h1 = VGroup(*[Rectangle(width=0.22, height=v, fill_color=MUTED, fill_opacity=0.8, stroke_width=0) for v in hv]).arrange(RIGHT, buff=0.04, aligned_edge=DOWN)
        h2 = VGroup(*[Rectangle(width=0.22, height=v * 1.03, fill_color=RED, fill_opacity=0.8, stroke_width=0) for v in hv]).arrange(RIGHT, buff=0.04, aligned_edge=DOWN)
        hh = VGroup(h1, h2).arrange(RIGHT, buff=0.4, aligned_edge=DOWN).move_to(c4 + DOWN * 0.1)
        hb = VGroup(T("干预前", 16, MUTED).next_to(h1, DOWN, buff=0.08), T("干预后", 16, RED).next_to(h2, DOWN, buff=0.08))
        b_old = RoundedRectangle(corner_radius=0.08, width=1.0, height=0.7, color=MUTED).move_to(c5 + LEFT * 0.9).add(T("旧提示", 16, MUTED).move_to(c5 + LEFT * 0.9))
        b_new = RoundedRectangle(corner_radius=0.08, width=1.0, height=0.7, color=INK).move_to(c5 + RIGHT * 0.9).add(T("新提示", 16, INK).move_to(c5 + RIGHT * 0.9))
        ar5 = Arrow(b_old.get_right(), b_new.get_left(), buff=0.1, color=INK)
        with self.say("e4") as d:
            self.play(panels[4].animate.set_opacity(1), FadeIn(h1), FadeIn(hb[0]), run_time=0.6)
            self.play(FadeIn(h2), FadeIn(hb[1]), run_time=0.8)
            self.wait(d * 0.1)
            self.play(panels[5].animate.set_opacity(1), FadeIn(b_old), FadeIn(b_new), run_time=0.6)
            self.play(GrowArrow(ar5), run_time=0.7)
            sub = T("重拟合复用 / 冻结复用", 16, MUTED).next_to(ar5, DOWN, buff=0.45)
            self.play(FadeIn(sub), run_time=0.4)
        self.clear()

    # ------------------------------------------------------------------ positive results
    def positive(self):
        tag = self.chapter("三  成立与不成立")
        with self.say("r1") as d:
            models = VGroup(*[VGroup(RoundedRectangle(corner_radius=0.12, width=w, height=w * 0.75, stroke_color=BLUE, stroke_width=2.5, fill_color="#182133", fill_opacity=1),
                                     T(n, 20, BLUE)) for w, n in ((1.4, "GPT-2 small"), (2.0, "Qwen3-1.7B"), (2.6, "Qwen3-4B"))]).arrange(RIGHT, buff=0.6, aligned_edge=DOWN)
            for m in models:
                m[1].move_to(m[0])
            models.shift(UP * 0.6)
            self.play(FadeIn(tag), LaggedStart(*[FadeIn(m, shift=UP * 0.2) for m in models], lag_ratio=0.3), run_time=1.6)
            k8 = counter("驱动节点", "≤ 8 个", GOLD).next_to(models, DOWN, buff=0.6)
            self.play(FadeIn(k8), run_time=0.6)
        with self.say("r2") as d:
            self.play(FadeOut(models), FadeOut(k8), run_time=0.5)
            base = -2.2; Hs = 2.6
            b1 = Rectangle(width=1.4, height=0.386 * Hs, fill_color=GREEN, fill_opacity=0.9, stroke_width=0).move_to([-1.2, base, 0], aligned_edge=DOWN)
            b2 = Rectangle(width=1.4, height=1.430 * Hs, fill_color=MUTED, fill_opacity=0.9, stroke_width=0).move_to([1.2, base, 0], aligned_edge=DOWN)
            ax = Line([-2.6, base, 0], [2.6, base, 0], color=MUTED)
            v1 = T("0.386", 26, GREEN).next_to(b1, UP, buff=0.1); v2 = T("1.430", 26, MUTED).next_to(b2, UP, buff=0.1)
            l1 = T("Driver-OMP", 22, INK).next_to(b1, DOWN, buff=0.2); l2 = T("随机支持集", 22, INK).next_to(b2, DOWN, buff=0.2)
            hd = T("间接宾语识别 · 归一化残差（越低越好）", 24, MUTED).to_edge(UP, buff=0.9)
            self.play(FadeIn(hd), Create(ax), FadeIn(l1), FadeIn(l2), run_time=0.6)
            self.play(GrowFromEdge(b1, DOWN), GrowFromEdge(b2, DOWN), run_time=1.2)
            self.play(FadeIn(v1), FadeIn(v2), run_time=0.5)
            g1 = VGroup(b1, b2, ax, v1, v2, l1, l2, hd)
        with self.say("r3") as d:
            self.play(FadeOut(g1), run_time=0.5)
            ticks = VGroup(*[Circle(radius=0.22, color=GREEN, stroke_width=3) for _ in range(24)]).arrange_in_grid(rows=3, cols=8, buff=0.25).shift(UP * 0.4)
            self.play(FadeIn(ticks, lag_ratio=0.03), run_time=0.8)
            self.play(LaggedStart(*[t.animate.set_fill(GREEN, opacity=0.85) for t in ticks], lag_ratio=0.05), run_time=1.4)
            c = VGroup(counter("目标端点命中", "24 / 24", GREEN), counter("平均评估次数", "3.96", INK)).arrange(RIGHT, buff=1.2).next_to(ticks, DOWN, buff=0.5)
            self.play(FadeIn(c), run_time=0.6)
        with self.say("r4") as d:
            self.play(FadeOut(ticks), FadeOut(c), run_time=0.5)
            grid = VGroup(*[Circle(radius=0.16, color=GREEN, stroke_width=2.5) for _ in range(48)]).arrange_in_grid(rows=4, cols=12, buff=0.16).move_to([-2.6, 0.6, 0])
            self.play(FadeIn(grid, lag_ratio=0.02), run_time=0.7)
            self.play(*[grid[i].animate.set_fill(GREEN, opacity=0.85) for i in range(46)], run_time=1.0)
            ca = counter("人文题 · 逐样本方向", "46 / 48", GREEN).next_to(grid, DOWN, buff=0.4)
            self.play(FadeIn(ca), run_time=0.5)
            tr = Rectangle(width=0.9, height=3.6, stroke_color=MUTED, stroke_width=1.5).move_to([3.6, 0.0, 0])
            fl = Rectangle(width=0.9, height=3.6 * 0.992, fill_color=GREEN, fill_opacity=0.85, stroke_width=0).move_to(tr, aligned_edge=DOWN)
            cb = counter("重拟合复用", "99.2%", GREEN).next_to(tr, DOWN, buff=0.3)
            self.play(Create(tr), GrowFromEdge(fl, DOWN), FadeIn(cb), run_time=1.2)
            self.pos_reuse = VGroup(tr, fl, cb)
        self.clear()

    # ------------------------------------------------------------------ negative results
    def negative(self):
        tag = self.chapter("三  成立与不成立")
        with self.say("x1") as d:
            items = []
            for i, (v, c, n) in enumerate(((99.2, GREEN, "重拟合复用"), (2.1, RED, "冻结复用"))):
                x = -1.4 + i * 2.8
                tr = Rectangle(width=1.2, height=4.0, stroke_color=MUTED, stroke_width=1.5).move_to([x, -0.2, 0])
                fl = Rectangle(width=1.2, height=max(0.02, 4.0 * v / 100), fill_color=c, fill_opacity=0.85, stroke_width=0).move_to(tr, aligned_edge=DOWN)
                lab = VGroup(T(n, 24, INK), T(f"{v}%", 30, c, weight=BOLD)).arrange(DOWN, buff=0.1).next_to(tr, DOWN, buff=0.25)
                items.append((tr, fl, lab))
            hd = T("人文题：搬到新题目后的平均恢复", 24, MUTED).to_edge(UP, buff=0.9)
            self.play(FadeIn(tag), FadeIn(hd), *[Create(t) for t, _, _ in items], *[FadeIn(l) for _, _, l in items], run_time=0.8)
            self.play(GrowFromEdge(items[0][1], DOWN), run_time=1.0)
            self.play(GrowFromEdge(items[1][1], DOWN), run_time=1.0)
            note = VGroup(T("站点能迁移", 26, GREEN), T("干预本身不能直接搬", 26, RED)).arrange(DOWN, buff=0.2).move_to([4.6, 0.2, 0])
            self.play(FadeIn(note), run_time=0.8)
            g = VGroup(hd, note, *[m for it in items for m in it])
        with self.say("x2") as d:
            self.play(FadeOut(g), run_time=0.5)
            ga = VGroup(*[Circle(radius=0.14, color=GREEN, stroke_width=2.5) for _ in range(48)]).arrange_in_grid(rows=4, cols=12, buff=0.13)
            gb = VGroup(*[Circle(radius=0.14, color=RED, stroke_width=2.5) for _ in range(48)]).arrange_in_grid(rows=4, cols=12, buff=0.13)
            for i in range(46):
                ga[i].set_fill(GREEN, opacity=0.85)
            VGroup(ga, gb).arrange(RIGHT, buff=1.0).shift(UP * 0.4)
            la = counter("逐样本方向", "46 / 48", GREEN).next_to(ga, DOWN, buff=0.35)
            lb = counter("训练均值的冻结方向", "8 / 48", RED).next_to(gb, DOWN, buff=0.35)
            self.play(FadeIn(ga), FadeIn(la), FadeIn(gb), run_time=0.8)
            self.play(*[gb[i].animate.set_fill(RED, opacity=0.85) for i in range(8)], FadeIn(lb), run_time=1.0)
            g = VGroup(ga, gb, la, lb)
        with self.say("x3") as d:
            self.play(FadeOut(g), run_time=0.5)
            ax = Axes(x_range=[0, 4, 1], y_range=[0, 4, 1], x_length=4.5, y_length=3.4, axis_config={"color": MUTED, "include_tip": False}).move_to([-3.2, -0.2, 0])
            xl = T("剂量", 20, MUTED).next_to(ax.x_axis, DOWN, buff=0.2)
            yl = T("拒答倾向", 20, MUTED).rotate(PI / 2).next_to(ax.y_axis, LEFT, buff=0.2)
            curve = ax.plot(lambda x: 0.4 + 0.8 * x, x_range=[0, 4], color=GOLD, stroke_width=5)
            self.play(Create(ax), FadeIn(xl), FadeIn(yl), run_time=0.8)
            self.play(Create(curve), run_time=1.0)
            mono = T("单调：48 / 48 格", 22, GOLD).next_to(ax, UP, buff=0.2)
            self.play(FadeIn(mono), run_time=0.4)
            p0 = np.array([2.2, -0.2, 0])
            fwd = Arrow(p0, p0 + RIGHT * 2.6, buff=0, color=GOLD, stroke_width=6)
            back = Arrow(p0 + RIGHT * 2.6 + DOWN * 0.6, p0 + DOWN * 0.6, buff=0, color=VIOLET, stroke_width=6)
            self.play(GrowArrow(fwd), run_time=0.6)
            self.play(GrowArrow(back), run_time=0.6)
            x = Cross(back, stroke_color=RED, scale_factor=0.5)
            rv = T("反转：两种模式各 24 格全部失败", 22, RED).next_to(back, DOWN, buff=0.3)
            self.play(Create(x), FadeIn(rv), run_time=0.8)
            g = VGroup(ax, xl, yl, curve, mono, fwd, back, x, rv)
        with self.say("x4") as d:
            self.play(FadeOut(g), run_time=0.5)
            seeds = VGroup(*[Circle(radius=0.35, color=MUTED, stroke_width=3) for _ in range(8)]).arrange(RIGHT, buff=0.35).shift(UP * 0.3)
            self.play(FadeIn(seeds, lag_ratio=0.1), run_time=0.8)
            self.play(*[seeds[i].animate.set_fill(GREEN, opacity=0.8).set_stroke(GREEN) for i in range(4)], run_time=0.8)
            c = counter("平均 KL < 0.001 的种子（32 道无关题）", "4 / 8", GREEN).next_to(seeds, DOWN, buff=0.5)
            self.play(FadeIn(c), run_time=0.6)
        self.clear()

    # ------------------------------------------------------------------ meaning & limits
    def meaning(self):
        tag = self.chapter("四  意义与局限")
        pill = VGroup(RoundedRectangle(corner_radius=0.35, width=1.8, height=0.7, fill_color=GREEN, fill_opacity=0.9, stroke_width=0),
                      T("药物", 26, BG, weight=BOLD))
        pill[1].move_to(pill[0])
        pill.move_to([-4.0, 0.3, 0])
        rng = np.random.default_rng(3)
        npts = [np.array([rng.uniform(-1.6, 3.6), rng.uniform(-2.2, 2.4), 0]) for _ in range(18)]
        net = VGroup(*[Line(npts[i], npts[j], color=MUTED, stroke_width=1.5, stroke_opacity=0.5) for i in range(18) for j in range(i + 1, 18)
                       if np.linalg.norm(npts[i] - npts[j]) < 1.7], *[Dot(p, radius=0.09, color=BLUE) for p in npts])
        with self.say("l1") as d:
            self.play(FadeIn(tag), FadeIn(pill), FadeIn(net), run_time=1.0)
            tg = [npts[2], npts[9]]
            rr = VGroup(*[Circle(radius=0.25, color=GOLD, stroke_width=4).move_to(p) for p in tg])
            self.play(Create(rr), *[Create(DashedLine(pill.get_right(), p, color=GREEN, stroke_width=2)) for p in tg], run_time=1.2)
        keep = list(self.mobjects)
        self.remove(*keep)
        with self.say("l1b") as d:
            self.clip_on("yt_pharmacodynamics.mp4", "center", "视频：Professor Dave Explains · YouTube", start=60)
        self.clip_off()
        self.add(*keep)
        with self.say("l2") as d:
            self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.5)
            pairs = [("可达", "能推动指标", GOLD), ("剂量响应", "加药量，效果单调", BLUE), ("反转", "能否撤回", VIOLET),
                     ("复用", "新患者上还有效", INK), ("保持", "其他通路少受影响", RED), ("反馈", "能否按目标调量", GREEN)]
            rows = VGroup(*[VGroup(T(a, 26, c, weight=BOLD), T("→", 26, MUTED), T(b, 26, INK)).arrange(RIGHT, buff=0.3) for a, b, c in pairs])
            rows.arrange_in_grid(rows=3, cols=2, buff=(0.8, 0.5), col_alignments="ll").shift(DOWN * 0.1)
            self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in rows], lag_ratio=0.25), run_time=d * 0.6)
        with self.say("l3") as d:
            self.play(FadeOut(rows), run_time=0.5)
            seq = VGroup(*[RoundedRectangle(corner_radius=0.08, width=1.0, height=0.6, stroke_color=MUTED, stroke_width=2) for _ in range(6)]).arrange(RIGHT, buff=0.12).shift(UP * 0.8)
            seq[0].set_stroke(GOLD, width=4)
            fl = T("只读首个生成词元", 24, GOLD).next_to(seq[0], DOWN, buff=0.3).align_to(seq[0], LEFT)
            self.play(FadeIn(seq), run_time=0.6)
            self.play(FadeIn(fl), seq[1:].animate.set_opacity(0.25), run_time=0.7)
            pv = T("逐样本方向 ← 用到测试对的信息", 24, RED).next_to(fl, DOWN, buff=0.5).align_to(fl, LEFT)
            self.play(FadeIn(pv), run_time=0.6)
        with self.say("l4") as d:
            self.play(FadeOut(seq), FadeOut(fl), FadeOut(pv), run_time=0.5)
            cert = VGroup(T("目标", 28, GREEN), T("保持", 28, RED), T("能量", 28, GOLD)).arrange(RIGHT, buff=0.8)
            box = SurroundingRectangle(cert, color=MUTED, buff=0.35, corner_radius=0.15)
            ttl = T("联合证书", 26, MUTED).next_to(box, UP, buff=0.15)
            gp = VGroup(cert, box, ttl).shift(UP * 0.6)
            self.play(FadeIn(gp), run_time=0.8)
            x = Cross(cert[2], stroke_color=RED, scale_factor=1.2)
            nb = T("能量约束未强制 → 证书不完整", 24, RED).next_to(box, DOWN, buff=0.3)
            self.play(Create(x), FadeIn(nb), run_time=0.9)
            lin = T("≠ 线性系统意义上的完全可控", 26, INK).next_to(nb, DOWN, buff=0.4)
            self.play(FadeIn(lin), run_time=0.6)
        with self.say("l5") as d:
            self.play(*[FadeOut(m) for m in self.mobjects if m is not tag], run_time=0.5)
            names = [("可达", GOLD), ("反转", VIOLET), ("剂量", BLUE), ("反馈", GREEN), ("保持", RED), ("复用", INK)]
            hexa = VGroup(*[VGroup(Circle(radius=0.55, color=c, stroke_width=3), T(n, 24, c)) for n, c in names])
            for i, h in enumerate(hexa):
                a = PI / 2 - i * TAU / 6
                h.move_to(2.2 * np.array([np.cos(a), np.sin(a), 0]) + DOWN * 0.2)
            core = Dot(DOWN * 0.2, radius=0.2, color=GOLD)
            self.play(FadeIn(core), run_time=0.4)
            for h in hexa:
                self.play(FadeIn(h, scale=0.6), Create(Line(core.get_center(), h.get_center(), color=MUTED, stroke_width=1.5).set_z_index(-1)), run_time=0.4)
        self.wait(0.8)
        self.clear(1.0)
