"""Helpers for the paper-explainer episodes (directed graphs, matchings, input graphs)."""
import networkx as nx
import numpy as np

from common import *  # noqa: F401,F403
from ep_robustness import fit, spread, counter  # noqa: F401


def arrow(a, b, r=0.16, color=MUTED, sw=3, op=1.0, tip=0.16):
    a, b = np.array(a, float), np.array(b, float)
    d = b - a
    L = np.linalg.norm(d) + 1e-9
    u = d / L
    return Arrow(a + u * r, b - u * r, buff=0, stroke_width=sw, color=color, tip_length=tip,
                 max_tip_length_to_length_ratio=0.45, max_stroke_width_to_length_ratio=20).set_opacity(op)


class DiNet:
    """Directed network drawn with labelled (or plain) circles and arrows."""

    def __init__(self, G, pos, r=0.26, color=BLUE, labels=True, ecolor=MUTED, sw=3, fs=24, tip=0.16):
        self.G, self.pos, self.r = G, pos, r
        self.nodes, self.circ = {}, {}
        for v in G:
            c = Circle(radius=r, color=color, fill_color=BG, fill_opacity=1, stroke_width=3).move_to(pos[v])
            g = VGroup(c)
            if labels:
                g.add(T(str(v), fs, INK).move_to(pos[v]))
            self.nodes[v], self.circ[v] = g, c
        self.arrows = {(u, v): arrow(pos[u], pos[v], r + 0.03, ecolor, sw, tip=tip) for u, v in G.edges()}
        self.group = VGroup(VGroup(*self.arrows.values()), VGroup(*self.nodes.values()))

    def fill(self, v, col, op=0.85):
        return self.circ[v].animate.set_fill(col, opacity=op).set_stroke(col)

    def reset(self, v, col=BLUE):
        return self.circ[v].animate.set_fill(BG, opacity=1).set_stroke(col)


def max_matching(G):
    """Maximum matching of a directed graph as a set of edges (u, v)."""
    B = nx.Graph()
    outs = [("o", u) for u in G]
    B.add_nodes_from(outs, bipartite=0)
    B.add_nodes_from([("i", v) for v in G], bipartite=1)
    B.add_edges_from((("o", u), ("i", v)) for u, v in G.edges())
    M = nx.bipartite.hopcroft_karp_matching(B, top_nodes=outs)
    return {(a[1], b[1]) for a, b in M.items() if a[0] == "o"}


def drivers(G, M):
    hit = {v for _, v in M}
    return [v for v in G if v not in hit] or [next(iter(G))]


def n_drivers(G):
    return max(G.number_of_nodes() - len(max_matching(G)), 1)


def possible_inputs(G, M):
    """All possible input nodes: in-ends reachable by alternating paths from unmatched in-ends."""
    mout = {u: v for u, v in M}
    start = [v for v in G if v not in {b for _, b in M}]
    seen = set(start)
    q = list(start)
    while q:
        n = q.pop()
        for c in G.predecessors(n):          # non-matching edge n_in -- c_out
            if mout.get(c) not in (None, n):
                b = mout[c]                    # matching edge c_out -- b_in
                if b not in seen:
                    seen.add(b); q.append(b)
    return seen


def input_graph(G, M):
    """Control-adjacency graph: a ~ b if c->a is non-matching and c->b is matching."""
    H = nx.Graph(); H.add_nodes_from(G)
    mout = {u: v for u, v in M}
    for c, b in mout.items():
        for a in G.successors(c):
            if a != b:
                H.add_edge(a, b)
    return H


def sf_digraph(n, k, gamma=3.0, seed=0):
    """Directed static-model scale-free network (Goh et al.) with average total out-degree k."""
    rng = np.random.default_rng(seed)
    a = 1 / (gamma - 1)
    w = np.arange(1, n + 1) ** (-a); w /= w.sum()
    m = int(k * n)
    src = rng.choice(n, size=3 * m, p=w)
    dst = rng.choice(n, size=3 * m, p=rng.permutation(w))
    G = nx.DiGraph(); G.add_nodes_from(range(n))
    for s, d in zip(src, dst):
        if s != d:
            G.add_edge(int(s), int(d))
            if G.number_of_edges() >= m:
                break
    return G
