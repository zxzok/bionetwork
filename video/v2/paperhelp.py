"""Shared helpers for the paper-explainer episodes (ep_<paper>.py)."""
import networkx as nx
import numpy as np

from common import *  # noqa: F401,F403
from ep_robustness import NetView, fit, giant, sf_graph, counter  # noqa: F401


def ring_pos(n, r=3.0, center=ORIGIN, start=PI / 2):
    c = np.array(center, float)
    return {i: c + r * np.array([np.cos(start - 2 * PI * i / n), np.sin(start - 2 * PI * i / n), 0]) for i in range(n)}


def plain_axes(xr, yr, xl, yl, xnums=None, ynums=None, fs=22):
    return Axes(x_range=xr, y_range=yr, x_length=xl, y_length=yl,
                axis_config={"color": MUTED, "include_tip": False, "font_size": fs},
                x_axis_config={"numbers_to_include": xnums or []},
                y_axis_config={"numbers_to_include": ynums or []})


def log_axes(xr, yr, xl, yl, fs=22):
    """Axes whose ranges may be negative (log10 values) but whose axes sit at the lower-left corner.
    Use ax.P(x, y) instead of ax.c2p; ticks are placed at every integer."""
    ox, oy = xr[0], yr[0]
    ax = Axes(x_range=[0, xr[1] - ox, 1], y_range=[0, yr[1] - oy, 1], x_length=xl, y_length=yl,
              axis_config={"color": MUTED, "include_tip": False, "font_size": fs})
    ax.ox, ax.oy = ox, oy
    ax.P = lambda x, y: ax.c2p(x - ox, y - oy)
    return ax


def log_labels(ax, axis, exps, fs=24, fmt=None):
    """Tick labels 10^e for a log-scaled axis (values are log10); ax from log_axes."""
    P = getattr(ax, "P", ax.c2p)
    x0 = getattr(ax, "ox", ax.x_range[0]); y0 = getattr(ax, "oy", ax.y_range[0])
    g = VGroup()
    for e in exps:
        s = fmt(e) if fmt else rf"10^{{{e}}}"
        t = MathTex(s, font_size=fs + 6, color=MUTED)
        if axis == "x":
            t.next_to(P(e, y0), DOWN, buff=0.18)
        else:
            t.next_to(P(x0, e), LEFT, buff=0.18)
        g.add(t)
    return g


def pline(ax, xs, ys, color, sw=4):
    """Polyline through data points in log_axes coordinates."""
    return VMobject(color=color, stroke_width=sw).set_points_as_corners([ax.P(x, y) for x, y in zip(xs, ys)])


def ylabel(s, ax, size=22, buff=0.35):
    return T(s, size, MUTED).rotate(PI / 2).next_to(ax.y_axis, LEFT, buff=buff)


def xlabel(s, ax, size=22, buff=0.4):
    return T(s, size, MUTED).next_to(ax.x_axis, DOWN, buff=buff)


def legend(items, size=22):
    return VGroup(*[VGroup(Line(ORIGIN, RIGHT * 0.5, color=c, stroke_width=5), T(s, size, INK)).arrange(RIGHT, buff=0.15)
                    for c, s in items]).arrange(DOWN, aligned_edge=LEFT, buff=0.18)


def recap(scene, head_key, items, head="三个要点"):
    """items: [(line_key, colour, short text)]"""
    with scene.say(head_key):
        h = T(head, 40, INK, weight=BOLD).to_edge(UP, buff=0.7)
        scene.play(Write(h), run_time=0.8)
    rows = VGroup()
    for i, (_, c, s) in enumerate(items):
        num = Circle(radius=0.32, color=c, fill_opacity=0.18, stroke_width=3).add(T(str(i + 1), 28, c, weight=BOLD))
        rows.add(VGroup(num, T(s, 32, INK)).arrange(RIGHT, buff=0.4))
    rows.arrange(DOWN, aligned_edge=LEFT, buff=0.6).next_to(h, DOWN, buff=0.8)
    for (k, _, _), row in zip(items, rows):
        with scene.say(k):
            scene.play(FadeIn(row, shift=RIGHT * 0.3), run_time=0.8)
    scene.wait(1.0)
    scene.play(*[FadeOut(m) for m in scene.mobjects], run_time=1.0)


def clear(scene, keep=(), rt=0.8):
    ms = [m for m in scene.mobjects if m not in keep]
    if ms:
        scene.play(*[FadeOut(m) for m in ms], run_time=rt)


def logbin(deg, nb=14):
    """Log-binned degree distribution: returns (log10 k, log10 P(k)) for non-empty bins."""
    deg = np.asarray(deg)
    deg = deg[deg > 0]
    edges = np.unique(np.floor(np.logspace(0, np.log10(deg.max() + 1), nb)).astype(int))
    xs, ys = [], []
    for a, b in zip(edges[:-1], edges[1:]):
        c = ((deg >= a) & (deg < b)).sum()
        if c:
            xs.append(np.log10(np.sqrt(a * (b - 1)) if b - 1 > a else a))
            ys.append(np.log10(c / len(deg) / (b - a)))
    return np.array(xs), np.array(ys)


def parts(scene, head_key, item_keys, title, points, accent=BLUE):
    """Parts slide after the hook: title with head_key, then one point per narration line."""
    head, items = slide(title, points, accent=accent)
    with scene.say(head_key):
        scene.play(FadeIn(head, shift=RIGHT * 0.3), run_time=0.6)
    for k, it in zip(item_keys, items):
        with scene.say(k):
            scene.play(FadeIn(it, shift=RIGHT * 0.3), run_time=0.6)
    scene.wait(0.6)
    scene.play(FadeOut(head), FadeOut(items), run_time=0.6)


def show_slide(scene, keys, title, points, accent=BLUE):
    """A text slide: first key brings the title, each further key one point."""
    head, items = slide(title, points, accent=accent)
    with scene.say(keys[0]):
        scene.play(FadeIn(head, shift=RIGHT * 0.3), run_time=0.6)
        if len(keys) == len(points):
            scene.play(FadeIn(items[0], shift=RIGHT * 0.3), run_time=0.6)
    rest = keys[1:]
    its = items[1:] if len(keys) == len(points) else items
    for k, it in zip(rest, its):
        with scene.say(k):
            scene.play(FadeIn(it, shift=RIGHT * 0.3), run_time=0.6)
    scene.wait(0.6)
    scene.play(FadeOut(head), FadeOut(items), run_time=0.6)


def clip_lines(scene, name, keys, credit, start=0.0, box="center", min_len=None):
    """Play a clip under one or more narration lines (clears the screen first)."""
    clear(scene, rt=0.5)
    first = True
    for k in keys:
        with scene.say(k) as d:
            if first:
                scene.clip_on(name, box, credit, start=start)
                first = False
    if min_len:
        scene.wait(0.1)
    scene.clip_off()
