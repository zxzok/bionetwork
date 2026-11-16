"""Helpers for the paper-explainer episodes on network control (directed graphs, matchings)."""
import networkx as nx
import numpy as np

from common import *  # noqa: F401,F403


# ----------------------------------------------------------------------------- matching
def kuhn(G, order, start=None):
    """Maximum matching of the bipartite out/in copies of digraph G.

    Returns dict match[v] = u meaning matched edge u->v (v's in-copy matched).
    Augments from unmatched in-copies in the given order, starting from a partial matching `start`.
    """
    match = dict(start or {})          # v (in) -> u (out)
    used = {u: v for v, u in match.items()}  # u (out) -> v (in)

    def aug(v, seen):
        for u in G.predecessors(v):
            if u in seen:
                continue
            seen.add(u)
            if u not in used or aug(used[u], seen):
                match[v] = u
                used[u] = v
                return True
        return False

    for v in order:
        if v not in match:
            aug(v, set())
    return match


def drivers(G, match):
    return [v for v in G if v not in match]


def mm_size(G):
    return len(kuhn(G, list(G)))


def possible_heads(G):
    """Nodes that are drivers (in-copy unmatched) in at least one maximum matching."""
    n = mm_size(G)
    out = []
    for v in G:
        H = G.copy(); H.remove_edges_from(list(G.in_edges(v)))
        if mm_size(H) == n:
            out.append(v)
    return out


def possible_tails(G):
    return possible_heads(G.reverse(copy=True))


def control_hubs(G):
    h, t = set(possible_heads(G)), set(possible_tails(G))
    return [v for v in G if v not in h and v not in t]


# ----------------------------------------------------------------------------- drawing
class DiNet:
    """Directed network: circles + arrows (arrows stop at the node boundary)."""

    def __init__(self, G, pos, r=0.16, color=BLUE, ecolor=MUTED, ew=2.4, eo=0.8, labels=None, lsize=26, tip=0.16):
        self.G, self.pos, self.r = G, pos, r
        self.nodes = {}
        for v in G:
            c = Circle(radius=r, color=color, stroke_width=3, fill_color=BG, fill_opacity=1).move_to(pos[v])
            if labels and v in labels:
                c.add(T(labels[v], lsize, INK).move_to(pos[v]))
            self.nodes[v] = c
        self.edges = {e: self.arrow(e[0], e[1], ecolor, ew, eo, tip) for e in G.edges()}
        self.group = VGroup(VGroup(*self.edges.values()), VGroup(*self.nodes.values()))

    def arrow(self, u, v, color=MUTED, ew=2.4, eo=0.8, tip=0.16):
        a, b = np.array(self.pos[u]), np.array(self.pos[v])
        d = (b - a) / (np.linalg.norm(b - a) + 1e-9)
        ln = Line(a + d * (self.r + 0.03), b - d * (self.r + 0.03), color=color, stroke_width=ew, stroke_opacity=eo)
        ln.add_tip(tip_length=tip, tip_width=tip * 0.9)
        ln.tip.set_fill(color, opacity=eo)
        return ln

    def edge(self, u, v):
        return self.edges.get((u, v))

    def recolor_edge(self, u, v, color, width=None, opacity=1.0):
        e = self.edges[(u, v)]
        a = e.animate.set_stroke(color, width=width or e.get_stroke_width(), opacity=opacity)
        return a


def tipcolor(line, color, opacity=1.0):
    """Set colour of a Line with tip (stroke + tip fill)."""
    line.set_stroke(color, opacity=opacity)
    line.tip.set_fill(color, opacity=opacity).set_stroke(color, opacity=opacity)
    return line
