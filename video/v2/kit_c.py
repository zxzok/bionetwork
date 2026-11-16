"""Small drawing helpers for the topic episodes ep_molecular_networks … ep_reporting_frontiers."""
import networkx as nx
import numpy as np

from common import *  # noqa: F401,F403
from ep_robustness import NetView, counter, fit, giant, sf_graph, spread  # noqa: F401

PANEL = "#182133"


def axes(xr, yr, xl, yl, xnums=None, ynums=None, fs=22, **kw):
    return Axes(x_range=xr, y_range=yr, x_length=xl, y_length=yl,
                axis_config={"color": MUTED, "include_tip": False, "font_size": fs},
                x_axis_config={"numbers_to_include": xnums or []},
                y_axis_config={"numbers_to_include": ynums or []}, **kw)


def xlabel(ax, s, size=22, buff=0.35):
    return T(s, size, MUTED).next_to(ax.x_axis, DOWN, buff=buff)


def ylabel(ax, s, size=22, buff=0.3):
    return T(s, size, MUTED).rotate(PI / 2).next_to(ax.y_axis, LEFT, buff=buff)


def hist_bars(ax, values, edges, color=MUTED, opacity=0.75):
    """Bars of a histogram in axis coordinates (y = counts)."""
    cnt, _ = np.histogram(values, bins=edges)
    bars = VGroup()
    for c, a, b in zip(cnt, edges[:-1], edges[1:]):
        if c == 0:
            continue
        p0, p1 = ax.c2p(a, 0), ax.c2p(b, c)
        bars.add(Rectangle(width=p1[0] - p0[0], height=max(p1[1] - p0[1], 0.001), stroke_width=0.8, stroke_color=BG,
                           fill_color=color, fill_opacity=opacity).move_to(p0, aligned_edge=DL))
    return bars, cnt


def grow_bars(bars, rt=1.2):
    return LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.05, run_time=rt)


def code_block(s, size=20, width=None):
    c = Code(code_string=s, language="python", formatter_style="monokai", add_line_numbers=False, background="window",
             background_config={"stroke_color": MUTED, "fill_color": PANEL, "corner_radius": 0.15},
             paragraph_config={"font": "Menlo", "font_size": size})
    if width:
        c.scale_to_fit_width(width)
    return c


def box(mob, color=MUTED, buff=0.25, fill=PANEL):
    return SurroundingRectangle(mob, color=color, buff=buff, corner_radius=0.15, stroke_width=1.5,
                                fill_color=fill, fill_opacity=0.9)


def chip(s, color=INK, size=26, fill=PANEL):
    t = T(s, size, color)
    r = RoundedRectangle(corner_radius=0.15, width=t.width + 0.5, height=t.height + 0.35, stroke_color=color,
                         stroke_width=2, fill_color=fill, fill_opacity=1)
    return VGroup(r, t.move_to(r))


def arrow(a, b, color=MUTED, buff=0.12, sw=3, tip=0.2):
    return Arrow(a, b, buff=buff, color=color, stroke_width=sw, max_tip_length_to_length_ratio=0.25,
                 tip_length=tip)


def inhib(a, b, color=RED, buff=0.12, sw=3):
    """Flat-headed repression arrow a ⊣ b."""
    a, b = np.array(a, float), np.array(b, float)
    d = (b - a) / np.linalg.norm(b - a)
    s, e = a + d * buff, b - d * (buff + 0.02)
    n = np.array([-d[1], d[0], 0])
    return VGroup(Line(s, e, color=color, stroke_width=sw), Line(e - n * 0.14, e + n * 0.14, color=color, stroke_width=sw + 1))


def waffle(k, n=100, cols=10, on=RED, off=MUTED, r=0.09, gap=0.25):
    dots = VGroup(*[Dot(radius=r, color=on if i < k else off).set_opacity(1 if i < k else 0.45) for i in range(n)])
    dots.arrange_in_grid(rows=n // cols, cols=cols, buff=gap - 2 * r)
    return dots


def fade_all(scene, rt=0.8, keep=()):
    ms = [m for m in scene.mobjects if m not in keep]
    if ms:
        scene.play(*[FadeOut(m) for m in ms], run_time=rt)


def parts(scene, title, items, keys, accent=BLUE):
    """The 'this episode in N parts' slide: head with keys[0], then one item per following key."""
    head, its = slide(title, items, accent=accent)
    with scene.say(keys[0]):
        scene.play(FadeIn(head, shift=RIGHT * 0.3), run_time=0.6)
    for k, it in zip(keys[1:], its):
        with scene.say(k):
            scene.play(FadeIn(it, shift=RIGHT * 0.3), run_time=0.6)
    scene.wait(0.6)
    scene.play(FadeOut(head), FadeOut(its), run_time=0.6)


def callout(mob, text, direction=DOWN, color=GOLD, size=22, buff=0.15):
    """Box around part of a formula plus a short label next to it."""
    r = SurroundingRectangle(mob, color=color, buff=0.06, stroke_width=2.5)
    t = T(text, size, color).next_to(r, direction, buff=buff)
    return VGroup(r, t)


def clip_line(scene, key, name, credit, start=0.0, box="center", min_len=None):
    """Play one narration line over a video clip (screen should be clear inside the box)."""
    with scene.say(key) as d:
        scene.clip_on(name, box, credit, start=start)
        if min_len and d < min_len:
            scene.wait(min_len - d)
    scene.clip_off()
