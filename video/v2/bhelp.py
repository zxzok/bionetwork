"""Small helpers shared by the dynamics / brain / symptom episodes (spreading, synchronization, controllability,
brain-connectome, dynamic-brain-networks, symptom-networks)."""
import networkx as nx
import numpy as np

from common import *  # noqa: F401,F403
from ep_robustness import NetView, fit, giant, sf_graph  # noqa: F401


def counter(label, value, color=INK, vs=40, ls=24):
    return VGroup(T(label, ls, MUTED), T(value, vs, color, weight=BOLD)).arrange(DOWN, buff=0.12)


def heat(M, side=3.0, lo=-1.0, hi=1.0, neg=BLUE, pos=RED, mid=BG):
    """A matrix drawn as coloured squares (diverging colour map)."""
    M = np.asarray(M, float)
    n = M.shape[0]
    c = side / n
    g = VGroup()
    for i in range(n):
        for j in range(M.shape[1]):
            g.add(Square(c, stroke_width=0, fill_opacity=1, fill_color=hcol(M[i, j], lo, hi, neg, pos, mid))
                  .move_to([j * c, -i * c, 0]))
    g.move_to(ORIGIN)
    frame = Rectangle(width=c * M.shape[1], height=c * n, stroke_color=MUTED, stroke_width=1.2).move_to(g)
    return VGroup(g, frame)


def hcol(x, lo=-1.0, hi=1.0, neg=BLUE, pos=RED, mid=BG):
    t = float(np.clip((x - lo) / (hi - lo), 0, 1)) * 2 - 1
    if t >= 0:
        return interpolate_color(ManimColor(mid), ManimColor(pos), t)
    return interpolate_color(ManimColor(mid), ManimColor(neg), -t)


def recolor_heat(hm, M, lo=-1.0, hi=1.0, neg=BLUE, pos=RED, mid=BG):
    sq = hm[0]
    M = np.asarray(M, float)
    n, m = M.shape
    return [sq[i * m + j].animate.set_fill(hcol(M[i, j], lo, hi, neg, pos, mid)) for i in range(n) for j in range(m)]


def axes(xr, yr, xl, yl, xn=None, yn=None, fs=22, tip=False):
    return Axes(x_range=xr, y_range=yr, x_length=xl, y_length=yl,
                axis_config={"color": MUTED, "include_tip": tip, "font_size": fs},
                x_axis_config={"numbers_to_include": xn or []},
                y_axis_config={"numbers_to_include": yn or []})


def legend(items, size=22):
    return VGroup(*[VGroup(Line(ORIGIN, RIGHT * 0.5, color=c, stroke_width=5), T(s, size, INK)).arrange(RIGHT, buff=0.15)
                    for c, s in items]).arrange(DOWN, aligned_edge=LEFT, buff=0.2)


def arrow_between(p, q, r1=0.12, r2=0.12, color=MUTED, sw=3, tip=0.18, **kw):
    p, q = np.array(p, float), np.array(q, float)
    d = q - p
    u = d / (np.linalg.norm(d) + 1e-9)
    return Arrow(p + u * r1, q - u * r2, buff=0, color=color, stroke_width=sw, tip_length=tip,
                 max_tip_length_to_length_ratio=0.35, **kw)


def clear(scene, keep=()):
    scene.play(*[FadeOut(m) for m in scene.mobjects if m not in keep], run_time=0.8)


def parts_slide(scene, points, keys=("q0", "q1", "q2", "q3"), title="这一期分三部分"):
    """The 'parts of this episode' slide: title with the first key, then one point per following key."""
    head, items = slide(title, points)
    with scene.say(keys[0]):
        scene.play(FadeIn(head, shift=RIGHT * 0.3), run_time=0.6)
    for k, it in zip(keys[1:], items):
        with scene.say(k):
            scene.play(FadeIn(it, shift=RIGHT * 0.3), run_time=0.6)
    scene.wait(0.6)
    scene.play(FadeOut(head), FadeOut(items), run_time=0.6)


def recap_slide(scene, points, keys=("z1", "z2", "z3", "z4"), title="小结"):
    head, items = slide(title, points, size=30, accent=GOLD)
    with scene.say(keys[0]):
        scene.play(FadeIn(head, shift=RIGHT * 0.3), run_time=0.6)
    for k, it in zip(keys[1:], items):
        with scene.say(k):
            scene.play(FadeIn(it, shift=RIGHT * 0.3), run_time=0.6)
    scene.wait(0.6)
    scene.play(FadeOut(head), FadeOut(items), run_time=0.6)


def show_clip(scene, key, name, box, credit, start=0.0, min_len=0.0, keys_after=()):
    """Play a clip under narration line `key` (and optional following lines); everything else is cleared first."""
    if scene.mobjects:
        scene.play(*[FadeOut(m) for m in scene.mobjects], run_time=0.5)
    with scene.say(key) as d:
        scene.clip_on(name, box, credit, start=start)
        if d < min_len:
            scene.wait(min_len - d)
    for k in keys_after:
        with scene.say(k):
            pass
    scene.clip_off()
