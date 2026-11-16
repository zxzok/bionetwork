"""Shared helpers for the theory-domain episodes (network basics, metrics, models, communities, correlations, construction)."""
import networkx as nx
import numpy as np

from common import *  # noqa: F401,F403
from ep_robustness import NetView, fit, giant, sf_graph  # noqa: F401


def counter(label, value, color=INK, vs=40, ls=24):
    return VGroup(T(label, ls, MUTED), T(value, vs, color, weight=BOLD)).arrange(DOWN, buff=0.12)


class Grid(VGroup):
    """A small matrix drawn as a grid of cells, so single entries can be lit up and changed."""

    def __init__(self, vals, cell=0.55, size=26, labels=None, color=INK, fmt=None, **kw):
        super().__init__(**kw)
        vals = np.asarray(vals)
        n, m = vals.shape
        self.n, self.m, self.cell, self.size, self.fmt = n, m, cell, size, fmt or (lambda x: f"{x:g}")
        self.boxes = [[Square(cell, stroke_color=MUTED, stroke_width=1.2, stroke_opacity=0.6, fill_color=BG, fill_opacity=1)
                       .move_to([j * cell, -i * cell, 0]) for j in range(m)] for i in range(n)]
        self.nums = [[self._num(vals[i, j], color).move_to(self.boxes[i][j]) for j in range(m)] for i in range(n)]
        self.add(VGroup(*[b for r in self.boxes for b in r]), VGroup(*[t for r in self.nums for t in r]))
        self.rlab = VGroup(); self.clab = VGroup()
        if labels is not None:
            rl, cl = labels if isinstance(labels, tuple) else (labels, labels)
            self.rlab = VGroup(*[T(str(s), size - 2, MUTED).next_to(self.boxes[i][0], LEFT, buff=0.15) for i, s in enumerate(rl)])
            self.clab = VGroup(*[T(str(s), size - 2, MUTED).next_to(self.boxes[0][j], UP, buff=0.12) for j, s in enumerate(cl)])
            self.add(self.rlab, self.clab)

    def _num(self, x, color):
        c = color if x != 0 else MUTED
        return T(self.fmt(x), self.size, c)

    def set_num(self, i, j, x, color=GOLD):
        """Animation that replaces entry (i, j)."""
        new = T(self.fmt(x), self.size, color).move_to(self.boxes[i][j])
        old = self.nums[i][j]
        self.nums[i][j] = new
        return Transform(old, new)

    def hl(self, i, j, color=GOLD, op=0.35):
        return self.boxes[i][j].animate.set_fill(color, opacity=op)


def edge_line(p, q, r=0.0, color=MUTED, w=3, op=0.8, arrow=False, angle=0.0):
    """Line or arc between two points, shortened by r at each end."""
    p, q = np.array(p, float), np.array(q, float)
    d = q - p; u = d / (np.linalg.norm(d) + 1e-9)
    a, b = p + u * r, q - u * r
    if arrow:
        return Arrow(a, b, buff=0, color=color, stroke_width=w, max_tip_length_to_length_ratio=0.18, tip_length=0.22)
    if angle:
        return ArcBetweenPoints(a, b, angle=angle, color=color, stroke_width=w, stroke_opacity=op)
    return Line(a, b, color=color, stroke_width=w, stroke_opacity=op)


def node(p, label=None, color=BLUE, r=0.28, size=26, fill=0.25):
    c = Circle(radius=r, color=color, stroke_width=3, fill_color=color, fill_opacity=fill).move_to(p)
    if label is None:
        return c
    return VGroup(c, T(str(label), size, INK, weight=BOLD).move_to(p))


def fade_all(scene, rt=0.8, keep=()):
    ms = [m for m in scene.mobjects if m not in keep]
    if ms:
        scene.play(*[FadeOut(m) for m in ms], run_time=rt)


def recap_rows(items, head_text="三个要点"):
    head = T(head_text, 40, INK, weight=BOLD).to_edge(UP, buff=0.7)
    rows = VGroup()
    for i, (_, c, s) in enumerate(items):
        num = Circle(radius=0.32, color=c, fill_opacity=0.18, stroke_width=3).add(T(str(i + 1), 28, c, weight=BOLD))
        rows.add(VGroup(num, T(s, 32, INK)).arrange(RIGHT, buff=0.4))
    rows.arrange(DOWN, aligned_edge=LEFT, buff=0.6).next_to(head, DOWN, buff=0.8)
    return head, rows


def nv_edge(view, u, v):
    return view.edges.get((u, v), view.edges.get((v, u)))


class LogAx:
    """Wraps Axes so that callers pass log10 coordinates while the axis lines sit at the bottom/left edges."""

    def __init__(self, ax, x0, y0):
        self.ax, self.x0, self.y0 = ax, x0, y0
        self.x_axis, self.y_axis = ax.x_axis, ax.y_axis

    def c2p(self, x, y):
        return self.ax.c2p(x - self.x0, y - self.y0)

    def plot_line_graph(self, xs, ys, **kw):
        return self.ax.plot_line_graph(np.asarray(xs) - self.x0, np.asarray(ys) - self.y0, **kw)


def log_axes(xlog=(0, 3), ylog=(-5, 0), xl=6.0, yl=4.2, fs=24):
    """Axes in log10 coordinates with 10^n tick labels. Returns (group, LogAx)."""
    ax = Axes(x_range=[0, xlog[1] - xlog[0], 1], y_range=[0, ylog[1] - ylog[0], 1], x_length=xl, y_length=yl,
              axis_config={"color": MUTED, "include_tip": False})
    la = LogAx(ax, xlog[0], ylog[0])
    xt = VGroup(*[MathTex(r"10^{%d}" % e, font_size=fs, color=MUTED).next_to(la.c2p(e, ylog[0]), DOWN, buff=0.15)
                  for e in range(xlog[0], xlog[1] + 1)])
    yt = VGroup(*[MathTex(r"10^{%d}" % e, font_size=fs, color=MUTED).next_to(la.c2p(xlog[0], e), LEFT, buff=0.15)
                  for e in range(ylog[0], ylog[1] + 1)])
    return VGroup(ax, xt, yt), la


def logbin(ks, nb=18):
    """Log-binned degree distribution: returns (log10 k, log10 p) for non-empty bins."""
    ks = np.asarray(ks); ks = ks[ks > 0]
    edges = np.unique(np.floor(np.logspace(0, np.log10(ks.max() + 1), nb)).astype(int))
    xs, ys = [], []
    for a, b in zip(edges[:-1], edges[1:]):
        c = ((ks >= a) & (ks < b)).sum()
        if c:
            xs.append(np.log10(np.sqrt(a * (b - 1 + 1e-9)) if b - a > 1 else a))
            ys.append(np.log10(c / len(ks) / (b - a)))
    return np.array(xs), np.array(ys)


def parts_slide(scene, title, points, keys=("q0", "q1", "q2", "q3", "q4", "q5")):
    """The 'this episode has N parts' slide: title with the first key, then one point per following key."""
    head, items = slide(title, points)
    with scene.say(keys[0]):
        scene.play(FadeIn(head, shift=RIGHT * 0.3), run_time=0.6)
    for k, it in zip(keys[1:], items):
        with scene.say(k):
            scene.play(FadeIn(it, shift=RIGHT * 0.3), run_time=0.6)
    scene.wait(0.8)
    scene.play(FadeOut(head), FadeOut(items), run_time=0.6)
