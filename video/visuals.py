"""Animated visual library for course explainer videos.

Every visual is a class with:
    __init__(self, params, T, cues)   precompute; T = scene length (s), cues = line start times (s)
    draw(self, ax, t)                 draw the frame at time t (0..T) into the main axes area
    key(self, t)  (optional)          hashable frame key; equal keys reuse the previous frame
The renderer owns the figure chrome (header, subtitles); visuals only use the axes they get.
"""
import math
import re
import numpy as np
import networkx as nx
from matplotlib.collections import LineCollection
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle, FancyBboxPatch

INK = "#1f2a44"
MUTED = "#6b7280"
FAINT = "#d6dae3"
BLUE = "#3b5bdb"
ORANGE = "#f08c00"
RED = "#e03131"
GREEN = "#2f9e44"
PURPLE = "#7048e8"
TEAL = "#0c8599"
BG = "#fbfaf6"
PALETTE = [BLUE, ORANGE, GREEN, RED, PURPLE, TEAL, "#c2255c", "#5c940d"]


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def prog(t, T, a=0.0, b=1.0):
    """progress of t within [a*T, b*T], eased."""
    if b <= a:
        return 1.0
    return ease((t / T - a) / (b - a))


def cue_index(t, cues):
    i = 0
    for k, c in enumerate(cues):
        if t >= c - 1e-6:
            i = k
    return i


def panel(fig_ax, rect):
    """create sub-axes inside main axes area using figure-relative rect within main axes."""
    ax = fig_ax
    fig = ax.figure
    x0, y0, w, h = ax.get_position().bounds
    sub = fig.add_axes([x0 + rect[0] * w, y0 + rect[1] * h, rect[2] * w, rect[3] * h])
    return sub


def clean(ax):
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_facecolor("none")


def plot_style(ax):
    ax.set_facecolor("none")
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    for s in ["left", "bottom"]:
        ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=11)
    ax.xaxis.label.set_color(INK)
    ax.yaxis.label.set_color(INK)


def draw_graph(ax, pos, edges, node_colors, node_sizes=60, edge_colors=FAINT, edge_widths=1.2,
               zorder=2, labels=None, label_size=10, edgecolors="white"):
    nodes = list(pos.keys())
    if edges:
        segs = [(pos[u], pos[v]) for u, v in edges]
        lc = LineCollection(segs, colors=edge_colors, linewidths=edge_widths, zorder=zorder)
        ax.add_collection(lc)
    xy = np.array([pos[n] for n in nodes])
    if isinstance(node_colors, dict):
        node_colors = [node_colors[n] for n in nodes]
    if isinstance(node_sizes, dict):
        node_sizes = [node_sizes[n] for n in nodes]
    ax.scatter(xy[:, 0], xy[:, 1], c=node_colors, s=node_sizes, zorder=zorder + 1,
               edgecolors=edgecolors, linewidths=0.8)
    if labels:
        for n, lab in labels.items():
            ax.text(pos[n][0], pos[n][1], lab, ha="center", va="center", fontsize=label_size,
                    color="white", zorder=zorder + 2, fontweight="bold")


def fit_view(ax, pos, pad=0.08):
    xy = np.array(list(pos.values()))
    lo, hi = xy.min(0), xy.max(0)
    span = (hi - lo).max() * (1 + 2 * pad)
    c = (lo + hi) / 2
    ax.set_xlim(c[0] - span / 2, c[0] + span / 2)
    ax.set_ylim(c[1] - span / 2, c[1] + span / 2)
    ax.set_aspect("equal")


def circle_pos(nodes, r=1.0, start=math.pi / 2):
    n = len(nodes)
    return {v: (r * math.cos(start - 2 * math.pi * i / n), r * math.sin(start - 2 * math.pi * i / n))
            for i, v in enumerate(nodes)}


def caption(ax, text, x=0.5, y=0.02, size=15, color=INK, **kw):
    ax.text(x, y, text, transform=ax.transAxes, ha="center", va="bottom", fontsize=size, color=color, **kw)


# --------------------------------------------------------------------------- text scenes
class Title:
    def __init__(self, p, T, cues):
        self.title = p.get("title", "")
        self.sub = p.get("subtitle", "")
        rng = np.random.default_rng(3)
        G = nx.random_geometric_graph(70, 0.19, seed=4)
        self.pos = {n: (0.05 + 0.9 * x, 0.05 + 0.9 * y) for n, (x, y) in nx.get_node_attributes(G, "pos").items()}
        self.edges = list(G.edges())
        self.order = rng.permutation(len(self.edges))
        self.T = T

    def key(self, t):
        return round(min(t / 3.0, 1.0), 2)

    def draw(self, ax, t):
        clean(ax)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        k = int(len(self.edges) * min(t / 3.0, 1.0))
        es = [self.edges[i] for i in self.order[:k]]
        draw_graph(ax, self.pos, es, "#c9d3f0", 18, edge_colors="#e3e8f5", edge_widths=0.8, zorder=1)
        ax.add_patch(FancyBboxPatch((0.12, 0.32), 0.76, 0.36, boxstyle="round,pad=0.02,rounding_size=0.03",
                                    fc=(1, 1, 1, 0.93), ec=FAINT, zorder=5))
        t_ = self.title
        wlen = sum(1 if ord(ch) > 0x2e80 else 0.55 for ch in t_)
        if wlen <= 16 and "\n" not in t_:
            ax.text(0.5, 0.56, t_, ha="center", va="center", fontsize=40, color=INK, fontweight="bold", zorder=6)
        else:  # long titles: two balanced lines, smaller type, kept inside the card
            m = re.search(r"[：:]", t_)
            cut = m.end() if m and 4 <= m.end() <= len(t_) - 4 else len(t_) // 2
            lines = t_.split("\n", 1) if "\n" in t_ else [t_[:cut].strip(), t_[cut:].strip()]
            fs = 34 if max(map(len, lines)) <= 15 else 28
            ax.text(0.5, 0.60, lines[0], ha="center", va="center", fontsize=fs, color=INK, fontweight="bold", zorder=6)
            ax.text(0.5, 0.50, lines[1], ha="center", va="center", fontsize=fs, color=INK, fontweight="bold", zorder=6)
        ax.text(0.5, 0.40, self.sub, ha="center", va="center", fontsize=22, color=BLUE, zorder=6)


class Bullets:
    def __init__(self, p, T, cues):
        self.h = p.get("heading", "")
        self.items = p.get("items", [])
        n = max(len(self.items), 1)
        if len(cues) >= n:
            self.at = cues[:n]
        else:
            self.at = [T * i / n for i in range(n)]

    def key(self, t):
        return sum(1 for a in self.at if t >= a - 1e-6)

    def draw(self, ax, t):
        clean(ax)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.text(0.06, 0.9, self.h, fontsize=30, color=INK, fontweight="bold", va="center")
        ax.plot([0.06, 0.2], [0.82, 0.82], color=BLUE, lw=4, solid_capstyle="round")
        shown = self.key(t)
        n = len(self.items)
        gap = min(0.14, 0.68 / max(n, 1))
        for i, it in enumerate(self.items[:shown]):
            y = 0.70 - i * gap
            cur = i == shown - 1
            ax.add_patch(Circle((0.085, y), 0.022, transform=ax.transData, color=BLUE if cur else "#9aa8d6"))
            ax.text(0.085, y, str(i + 1), ha="center", va="center", color="white", fontsize=15, fontweight="bold")
            ax.text(0.13, y, it, va="center", fontsize=24 if cur else 22, color=INK if cur else "#4b5563",
                    fontweight="bold" if cur else "normal")


class Formula:
    def __init__(self, p, T, cues):
        self.h = p.get("heading", "")
        self.lat = p.get("latex", [])
        self.notes = p.get("notes", [])
        n = max(len(self.lat), 1)
        self.at = cues[:n] if len(cues) >= n else [T * i / n for i in range(n)]

    def key(self, t):
        return sum(1 for a in self.at if t >= a - 1e-6)

    def draw(self, ax, t):
        clean(ax)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.text(0.06, 0.9, self.h, fontsize=30, color=INK, fontweight="bold", va="center")
        ax.plot([0.06, 0.2], [0.82, 0.82], color=BLUE, lw=4, solid_capstyle="round")
        shown = self.key(t)
        n = len(self.lat)
        gap = 0.6 / max(n, 1)
        for i in range(min(shown, n)):
            y = 0.66 - i * gap
            try:
                ax.text(0.5, y, f"${self.lat[i]}$", ha="center", va="center", fontsize=34, color=INK)
            except Exception:
                ax.text(0.5, y, self.lat[i], ha="center", va="center", fontsize=26, color=INK)
            if i < len(self.notes) and self.notes[i]:
                ax.text(0.5, y - gap * 0.42, self.notes[i], ha="center", va="center", fontsize=17, color=MUTED)


# --------------------------------------------------------------------------- graph basics
class GraphAdjacency:
    def __init__(self, p, T, cues):
        self.nodes = list(range(6))
        self.edges = [(0, 1), (0, 2), (1, 2), (2, 3), (3, 4), (3, 5), (4, 5)]
        self.pos = {0: (-1, 0.6), 1: (-1, -0.6), 2: (-0.2, 0), 3: (0.7, 0), 4: (1.4, 0.65), 5: (1.4, -0.65)}
        self.T = T

    def key(self, t):
        return int(prog(t, self.T, 0.05, 0.75) * len(self.edges) * 2)

    def draw(self, ax, t):
        clean(ax)
        g = panel(ax, [0.0, 0.05, 0.48, 0.9])
        m = panel(ax, [0.55, 0.12, 0.4, 0.78])
        clean(g)
        k = self.key(t)
        done = k // 2
        cur = self.edges[done] if done < len(self.edges) and k % 2 == 1 else None
        ecol = [RED if e == cur else (INK if i < done else FAINT) for i, e in enumerate(self.edges)]
        ew = [4 if e == cur else (2.4 if i < done else 1.5) for i, e in enumerate(self.edges)]
        draw_graph(g, self.pos, self.edges, BLUE, 900, edge_colors=ecol, edge_widths=ew,
                   labels={n: str(n + 1) for n in self.nodes}, label_size=16)
        fit_view(g, self.pos, 0.15)
        A = np.zeros((6, 6))
        for i, (u, v) in enumerate(self.edges[:done + (1 if cur else 0)]):
            A[u, v] = A[v, u] = 1
        clean(m)
        m.set_xlim(-0.5, 6.5)
        m.set_ylim(6.5, -1.2)
        for i in range(6):
            m.text(i, -0.8, str(i + 1), ha="center", fontsize=14, color=MUTED)
            m.text(-0.9, i, str(i + 1), va="center", fontsize=14, color=MUTED)
            for j in range(6):
                hot = cur is not None and {i, j} == set(cur)
                fc = RED if hot else (BLUE if A[i, j] else "white")
                m.add_patch(Rectangle((j - 0.45, i - 0.45), 0.9, 0.9, fc=fc, ec=FAINT, alpha=0.9 if A[i, j] or hot else 1))
                m.text(j, i, str(int(A[i, j])), ha="center", va="center", fontsize=13,
                       color="white" if A[i, j] else MUTED)
        if done >= len(self.edges):
            deg = A.sum(1).astype(int)
            m.text(6.0, 3, "度\n" + "\n".join(str(d) for d in deg), fontsize=13, color=ORANGE, va="center")
        m.text(2.5, 7.4 - 0.4, "邻接矩阵 A（对称）", ha="center", fontsize=16, color=INK)


class PathBFS:
    def __init__(self, p, T, cues):
        G = nx.connected_watts_strogatz_graph(34, 4, 0.25, seed=7)
        self.G = G
        self.pos = nx.kamada_kawai_layout(G)
        self.dist = nx.single_source_shortest_path_length(G, 0)
        self.maxd = max(self.dist.values())
        self.apl = nx.average_shortest_path_length(G)
        self.diam = nx.diameter(G)
        self.T = T

    def key(self, t):
        return int(prog(t, self.T, 0.05, 0.8) * (self.maxd + 1.999))

    def draw(self, ax, t):
        clean(ax)
        layer = self.key(t)
        import matplotlib.cm as cm
        cols, sizes, labels = {}, {}, {}
        for n in self.G:
            d = self.dist[n]
            if d <= layer:
                cols[n] = cm.viridis(d / (self.maxd + 0.5))
                labels[n] = str(d)
            else:
                cols[n] = FAINT
            sizes[n] = 420
        ecol = [INK if max(self.dist[u], self.dist[v]) <= layer and abs(self.dist[u] - self.dist[v]) == 1 else FAINT
                for u, v in self.G.edges()]
        draw_graph(ax, self.pos, list(self.G.edges()), cols, sizes, edge_colors=ecol, labels=labels, label_size=11)
        ax.scatter(*self.pos[0], s=900, facecolors="none", edgecolors=RED, linewidths=3, zorder=6)
        fit_view(ax, self.pos, 0.05)
        txt = f"广度优先搜索：第 {min(layer, self.maxd)} 层"
        if layer > self.maxd:
            txt = f"平均最短路径长度 ≈ {self.apl:.2f}    直径 = {self.diam}"
        caption(ax, txt, y=0.0, size=18)


class Clustering:
    def __init__(self, p, T, cues):
        G = nx.Graph()
        c = 0
        nb = [1, 2, 3, 4, 5]
        G.add_edges_from((c, v) for v in nb)
        G.add_edges_from([(1, 2), (2, 3), (4, 5), (3, 6), (5, 7), (6, 7), (1, 8), (8, 9), (4, 9)])
        self.G = G
        self.pos = nx.kamada_kawai_layout(G)
        self.pos[0] = np.array([0.0, 0.0])
        self.nb = nb
        self.tri = [(1, 2), (2, 3), (4, 5)]
        self.T = T

    def key(self, t):
        return int(prog(t, self.T, 0.1, 0.75) * (len(self.tri) + 1.999))

    def draw(self, ax, t):
        clean(ax)
        g = panel(ax, [0.0, 0.0, 0.58, 1.0])
        clean(g)
        k = self.key(t)
        cols = {n: (ORANGE if n == 0 else (BLUE if n in self.nb else "#b8c0d6")) for n in self.G}
        ecol, ew = [], []
        for u, v in self.G.edges():
            if (u, v) in self.tri[:k] or (v, u) in self.tri[:k]:
                ecol.append(RED); ew.append(4)
            elif 0 in (u, v):
                ecol.append(ORANGE); ew.append(2.2)
            else:
                ecol.append(FAINT); ew.append(1.4)
        for (a, b) in self.tri[:k]:
            pts = np.array([self.pos[0], self.pos[a], self.pos[b]])
            g.fill(pts[:, 0], pts[:, 1], color=RED, alpha=0.12, zorder=1)
        draw_graph(g, self.pos, list(self.G.edges()), cols, 520, edge_colors=ecol, edge_widths=ew,
                   labels={0: "i"}, label_size=14)
        fit_view(g, self.pos, 0.1)
        kk = len(self.nb)
        e = min(k, len(self.tri))
        lines = [("节点 i 的邻居数", f"$k_i = {kk}$"),
                 ("邻居之间可能的连边", f"$k_i(k_i-1)/2 = {kk * (kk - 1) // 2}$"),
                 ("邻居之间实际的连边", f"$e_i = {e}$"),
                 ("局部聚集系数", f"$C_i = {e}/{kk * (kk - 1) // 2} = {e / (kk * (kk - 1) / 2):.2f}$")]
        for j, (a, b) in enumerate(lines):
            y = 0.8 - j * 0.19
            ax.text(0.62, y, a, transform=ax.transAxes, fontsize=17, color=MUTED)
            ax.text(0.62, y - 0.075, b, transform=ax.transAxes, fontsize=22, color=INK if j < 3 else RED)


# --------------------------------------------------------------------------- random / models
def er_graph_gnm(n, k_mean, seed):
    m = int(round(k_mean * n / 2))
    return nx.gnm_random_graph(n, m, seed=seed)


def _nominor(a):
    from matplotlib.ticker import NullFormatter
    a.xaxis.set_minor_formatter(NullFormatter()); a.yaxis.set_minor_formatter(NullFormatter())


class DegreeDist:
    def __init__(self, p, T, cues):
        N = 3000
        self.er = np.array([d for _, d in er_graph_gnm(N, 6, 1).degree()])
        self.ba = np.array([d for _, d in nx.barabasi_albert_graph(N, 3, seed=2).degree()])
        self.T = T

    def key(self, t):
        return 0 if t < 0.5 * self.T else 1

    def draw(self, ax, t):
        clean(ax)
        loglog = self.key(t)
        for i, (name, d, col) in enumerate([("ER 随机网络", self.er, BLUE), ("BA 无标度网络", self.ba, ORANGE)]):
            a = panel(ax, [0.06 + i * 0.5, 0.14, 0.4, 0.74])
            plot_style(a)
            vals, cnt = np.unique(d, return_counts=True)
            pk = cnt / cnt.sum()
            if not loglog:
                a.bar(vals, pk, color=col, width=0.9)
                a.set_xlim(0, 40)
                a.set_xlabel("度 k", fontsize=15)
                a.set_ylabel("P(k)", fontsize=15)
            else:
                a.loglog(vals, pk, "o", color=col, ms=6, alpha=0.85)
                a.set_xlabel("度 k（对数）", fontsize=15); _nominor(a)
                a.set_ylabel("P(k)（对数）", fontsize=15)
                if i == 1:
                    ks = np.logspace(np.log10(3), np.log10(vals.max()), 20)
                    a.loglog(ks, pk[vals == 3][0] * (ks / 3) ** -3, "--", color=INK, lw=1.6)
                    a.text(0.55, 0.75, r"$P(k)\sim k^{-3}$", transform=a.transAxes, fontsize=18, color=INK)
            a.set_title(f"{name}   最大度 = {d.max()}", fontsize=17, color=INK)
        caption(ax, "线性坐标" if not loglog else "双对数坐标：幂律分布是一条直线", y=0.0, size=17, color=MUTED)


class ERGrowth:
    def __init__(self, p, T, cues):
        n = 70
        self.n = n
        rng = np.random.default_rng(5)
        pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
        u = rng.random(len(pairs))
        order = np.argsort(u)
        self.pairs = [pairs[k] for k in order]
        self.u = u[order]
        self.pmax = 3.0 / n
        G = nx.Graph(self.pairs[:int(self.pmax * len(pairs))])
        G.add_nodes_from(range(n))
        self.pos = nx.spring_layout(G, seed=3, k=0.35)
        # curve from big N via union-find
        N = 3000
        M = int(3.0 * N / 2)
        rng2 = np.random.default_rng(9)
        parent = list(range(N)); size = [1] * N
        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]; x = parent[x]
            return x
        best = 1; xs = [0]; ys = [1 / N]
        for m in range(1, M + 1):
            a, b = rng2.integers(0, N, 2)
            ra, rb = find(a), find(b)
            if ra != rb:
                if size[ra] < size[rb]: ra, rb = rb, ra
                parent[rb] = ra; size[ra] += size[rb]; best = max(best, size[ra])
            if m % 15 == 0:
                xs.append(2 * m / N); ys.append(best / N)
        self.cx, self.cy = np.array(xs), np.array(ys)
        self.T = T

    def key(self, t):
        return int(prog(t, self.T, 0.03, 0.85) * 300)

    def draw(self, ax, t):
        clean(ax)
        f = self.key(t) / 300
        p = f * self.pmax
        npairs = self.n * (self.n - 1) // 2
        m = int(np.searchsorted(self.u, p))
        edges = self.pairs[:m]
        G = nx.Graph(edges); G.add_nodes_from(range(self.n))
        gc = max(nx.connected_components(G), key=len)
        g = panel(ax, [0.0, 0.05, 0.5, 0.9]); clean(g)
        cols = {v: (RED if v in gc and len(gc) > 2 else BLUE) for v in G}
        ecol = [RED if u in gc and len(gc) > 2 else "#9aa8d6" for u, v in edges]
        draw_graph(g, self.pos, edges, cols, 70, edge_colors=ecol, edge_widths=1.3)
        fit_view(g, self.pos, 0.05)
        kmean = 2 * m / self.n
        g.set_title(f"p = {p:.3f}    平均度 $\\langle k\\rangle$ = {kmean:.2f}", fontsize=17, color=INK)
        a = panel(ax, [0.6, 0.18, 0.37, 0.68]); plot_style(a)
        sel = self.cx <= max(kmean, 0.01)
        a.plot(self.cx[sel], self.cy[sel], color=RED, lw=2.5)
        a.set_xlim(0, 3); a.set_ylim(0, 1)
        a.axvline(1, color=MUTED, ls="--", lw=1.2)
        a.text(1.05, 0.9, r"$\langle k\rangle = 1$ 临界点", color=MUTED, fontsize=13)
        a.set_xlabel(r"平均度 $\langle k\rangle$", fontsize=15); a.set_ylabel("最大连通分支占比", fontsize=15)
        a.set_title("巨连通分支的涌现（N = 3000）", fontsize=15, color=INK)


class WSRewire:
    def __init__(self, p, T, cues):
        n, k = 26, 4
        self.n = n
        self.ring = [(i, (i + j) % n) for i in range(n) for j in range(1, k // 2 + 1)]
        rng = np.random.default_rng(11)
        self.u = rng.random(len(self.ring))
        self.newt = []
        for (a, b) in self.ring:
            c = int(rng.integers(0, n))
            while c == a:
                c = int(rng.integers(0, n))
            self.newt.append(c)
        self.pos = circle_pos(range(n))
        # curves
        N, K = 400, 10
        betas = np.logspace(-4, 0, 13)
        G0 = nx.watts_strogatz_graph(N, K, 0, seed=1)
        C0, L0 = nx.average_clustering(G0), nx.average_shortest_path_length(G0)
        Cs, Ls = [], []
        for b in betas:
            c = l = 0
            for s in range(2):
                G = nx.connected_watts_strogatz_graph(N, K, b, seed=s + 2)
                c += nx.average_clustering(G); l += nx.average_shortest_path_length(G)
            Cs.append(c / 2 / C0); Ls.append(l / 2 / L0)
        self.betas, self.Cs, self.Ls = betas, np.array(Cs), np.array(Ls)
        self.T = T

    def key(self, t):
        return int(prog(t, self.T, 0.05, 0.9) * 200)

    def draw(self, ax, t):
        clean(ax)
        f = self.key(t) / 200
        beta = 10 ** (-4 + 4 * f)
        edges, ecol = [], []
        for i, (a, b) in enumerate(self.ring):
            if self.u[i] < beta:
                edges.append((a, self.newt[i])); ecol.append(ORANGE)
            else:
                edges.append((a, b)); ecol.append("#8c9bc9")
        g = panel(ax, [0.0, 0.05, 0.45, 0.9]); clean(g)
        draw_graph(g, self.pos, edges, BLUE, 110, edge_colors=ecol, edge_widths=1.6)
        fit_view(g, self.pos, 0.1)
        regime = "规则网络" if beta < 0.003 else ("小世界区间" if beta < 0.3 else "接近随机网络")
        g.set_title(f"重连概率 β = {beta:.4f}   {regime}", fontsize=17, color=INK)
        a = panel(ax, [0.56, 0.18, 0.41, 0.68]); plot_style(a)
        a.semilogx(self.betas, self.Cs, "o-", color=BLUE, lw=2, label="C(β)/C(0) 聚集系数")
        a.semilogx(self.betas, self.Ls, "s-", color=RED, lw=2, label="L(β)/L(0) 平均路径")
        a.axvline(beta, color=ORANGE, lw=2)
        a.axvspan(0.003, 0.3, color=GREEN, alpha=0.08)
        a.text(0.03, 0.55, "小世界", transform=a.transAxes, fontsize=14, color=GREEN)
        a.set_ylim(0, 1.08); a.set_xlabel("重连概率 β（对数）", fontsize=15)
        a.legend(fontsize=13, frameon=False, loc="lower left")


class BAGrowth:
    def __init__(self, p, T, cues):
        N, m = 160, 2
        G = nx.barabasi_albert_graph(N, m, seed=21)
        self.G = G
        self.N = N
        self.pos = nx.spring_layout(G, seed=4, k=0.12, iterations=200)
        self.order = sorted(G.nodes())
        self.T = T

    def key(self, t):
        return 3 + int(prog(t, self.T, 0.03, 0.88) * (self.N - 3))

    def draw(self, ax, t):
        clean(ax)
        n = self.key(t)
        H = self.G.subgraph(range(n))
        deg = dict(H.degree())
        g = panel(ax, [0.0, 0.03, 0.55, 0.94]); clean(g)
        newest = n - 1
        ecol = [ORANGE if newest in e else "#9aa8d6" for e in H.edges()]
        ew = [2.6 if newest in e else 0.9 for e in H.edges()]
        sizes = {v: 20 + 18 * deg[v] for v in H}
        cols = {v: (ORANGE if v == newest else (RED if deg[v] >= 10 else BLUE)) for v in H}
        draw_graph(g, {v: self.pos[v] for v in H}, list(H.edges()), cols, sizes, edge_colors=ecol, edge_widths=ew)
        fit_view(g, self.pos, 0.03)
        g.set_title(f"节点数 N = {n}    节点大小 ∝ 度", fontsize=16, color=INK)
        a = panel(ax, [0.64, 0.18, 0.33, 0.66]); plot_style(a)
        d = np.array(list(deg.values()))
        vals, cnt = np.unique(d, return_counts=True)
        ccdf = np.array([(d >= v).mean() for v in vals])
        a.loglog(vals, ccdf, "o-", color=ORANGE, ms=5)
        a.set_xlabel("度 k", fontsize=14); a.set_ylabel("P(K ≥ k)", fontsize=14)
        a.set_title("累积度分布（双对数）", fontsize=15, color=INK)
        a.set_xlim(1.5, 60); a.set_ylim(0.005, 1.2)
        from matplotlib.ticker import NullFormatter
        a.xaxis.set_minor_formatter(NullFormatter())


# --------------------------------------------------------------------------- communities
class Community:
    def __init__(self, p, T, cues):
        G = nx.karate_club_graph()
        self.G0 = G
        self.pos = nx.spring_layout(G, seed=8)
        H = G.copy()
        self.removed = []
        self.parts = []
        ncomp = 1
        while H.number_of_edges() > 0 and ncomp < 4:
            eb = nx.edge_betweenness_centrality(H)
            e = max(eb, key=eb.get)
            H.remove_edge(*e)
            self.removed.append(e)
            comps = list(nx.connected_components(H))
            ncomp = len(comps)
            self.parts.append(comps)
        self.Q = [nx.community.modularity(G, c) for c in self.parts]
        self.T = T

    def key(self, t):
        return int(prog(t, self.T, 0.05, 0.85) * (len(self.removed) + 0.999))

    def draw(self, ax, t):
        clean(ax)
        k = self.key(t)
        g = panel(ax, [0.0, 0.03, 0.55, 0.94]); clean(g)
        rem = set(self.removed[:k])
        edges = [e for e in self.G0.edges() if e not in rem and (e[1], e[0]) not in rem]
        comps = self.parts[k - 1] if k > 0 else [set(self.G0.nodes())]
        comps = sorted(comps, key=len, reverse=True)
        col = {}
        for i, c in enumerate(comps):
            for v in c:
                col[v] = PALETTE[i % len(PALETTE)] if len(c) > 1 else "#b8c0d6"
        nxt = self.removed[k] if k < len(self.removed) else None
        ecol = [RED if nxt and set(e) == set(nxt) else "#aab4cf" for e in edges]
        ew = [4 if nxt and set(e) == set(nxt) else 1.1 for e in edges]
        draw_graph(g, self.pos, edges, col, 170, edge_colors=ecol, edge_widths=ew)
        fit_view(g, self.pos, 0.05)
        g.set_title(f"已删除边数 {k}    社团数 {len([c for c in comps if len(c) > 1])}", fontsize=16, color=INK)
        a = panel(ax, [0.64, 0.18, 0.33, 0.66]); plot_style(a)
        xs = np.arange(1, len(self.Q) + 1)
        a.plot(xs[:k], self.Q[:k], "o-", color=GREEN, lw=2)
        a.set_xlim(0, len(self.Q) + 1); a.set_ylim(-0.05, 0.5)
        a.set_xlabel("删除的边数（按边介数）", fontsize=14); a.set_ylabel("模块度 Q", fontsize=14)
        if k:
            a.set_title(f"当前 Q = {self.Q[k - 1]:.3f}", fontsize=15, color=INK)
        else:
            a.set_title("Girvan–Newman：先删“桥”", fontsize=15, color=INK)


# --------------------------------------------------------------------------- dynamics
def sir_sim(G, beta, gamma, seeds, steps, rng, removed=()):
    state = {v: 0 for v in G}
    for v in removed:
        state[v] = 3
    for s in seeds:
        state[s] = 1
    hist = [dict(state)]
    nbrs = {v: list(G[v]) for v in G}
    for _ in range(steps):
        new = dict(state)
        for v, s in state.items():
            if s == 1:
                for u in nbrs[v]:
                    if state[u] == 0 and rng.random() < beta:
                        new[u] = 1
                if rng.random() < gamma:
                    new[v] = 2
        state = new
        hist.append(dict(state))
    return hist


SIRC = {0: "#9aa8d6", 1: RED, 2: "#69db7c", 3: "#495057"}


class SIR:
    def __init__(self, p, T, cues):
        G = nx.barabasi_albert_graph(220, 2, seed=5)
        self.G = G
        self.pos = nx.spring_layout(G, seed=2, k=0.11)
        beta, gamma = p.get("beta", 0.3), p.get("gamma", 0.1)
        seed = sorted(G, key=G.degree)[len(G) // 2]
        for s_ in range(50):
            h = sir_sim(G, beta, gamma, [seed], 60, np.random.default_rng(s_))
            if sum(1 for v in h[-1].values() if v == 2) > 0.6 * len(G):
                break
        self.hist = h
        self.T = T

    def key(self, t):
        return int(prog(t, self.T, 0.05, 0.9) * (len(self.hist) - 1))

    def draw(self, ax, t):
        clean(ax)
        s = self.key(t)
        st = self.hist[s]
        g = panel(ax, [0.0, 0.03, 0.55, 0.94]); clean(g)
        draw_graph(g, self.pos, list(self.G.edges()), {v: SIRC[st[v]] for v in self.G},
                   {v: 25 + 6 * self.G.degree(v) for v in self.G}, edge_colors="#e2e6ef", edge_widths=0.7)
        fit_view(g, self.pos, 0.03)
        g.set_title(f"时间步 t = {s}", fontsize=16, color=INK)
        a = panel(ax, [0.64, 0.18, 0.33, 0.66]); plot_style(a)
        n = self.G.number_of_nodes()
        arr = np.array([[sum(1 for v in h.values() if v == c) / n for c in (0, 1, 2)] for h in self.hist[:s + 1]])
        x = np.arange(len(arr))
        for c, lab, col in [(0, "易感 S", "#5c7cfa"), (1, "感染 I", RED), (2, "恢复 R", GREEN)]:
            a.plot(x, arr[:, c], color=col, lw=2.5, label=lab)
        a.set_xlim(0, len(self.hist)); a.set_ylim(0, 1)
        a.set_xlabel("时间步", fontsize=14); a.set_ylabel("比例", fontsize=14)
        a.legend(frameon=False, fontsize=13)


class Immunization:
    def __init__(self, p, T, cues):
        G = nx.barabasi_albert_graph(200, 2, seed=8)
        self.G = G
        self.pos = nx.spring_layout(G, seed=3, k=0.12)
        q = int(0.1 * 200)
        rng = np.random.default_rng(4)
        self.rand = set(rng.choice(200, q, replace=False).tolist())
        self.hub = set(sorted(G, key=G.degree, reverse=True)[:q])
        seeds = [v for v in [199, 180, 170] if v not in self.rand | self.hub][:1]
        def final(rem, s):
            h = sir_sim(G, 0.25, 0.1, seeds, 50, np.random.default_rng(s), removed=rem)
            return h, sum(1 for v in h[-1].values() if v in (1, 2))
        fr = [final(self.rand, s)[1] for s in range(30)]
        fh = [final(self.hub, s)[1] for s in range(30)]
        self.mean_r, self.mean_h = np.mean(fr) / 200, np.mean(fh) / 200
        # show a run close to the mean for each strategy
        sr = int(np.argmin([abs(f - np.mean(fr)) for f in fr]))
        sh = int(np.argmin([abs(f - np.mean(fh)) for f in fh]))
        self.hr = final(self.rand, sr)[0]
        self.hh = final(self.hub, sh)[0]
        self.T = T

    def key(self, t):
        return int(prog(t, self.T, 0.05, 0.8) * 50) + (100 if t > 0.82 * self.T else 0)

    def draw(self, ax, t):
        clean(ax)
        k = self.key(t)
        s = min(k % 100 if k < 100 else 50, 50)
        for i, (h, title) in enumerate([(self.hr, "随机免疫 10%"), (self.hh, "免疫度最大的 10%")]):
            g = panel(ax, [0.0 + i * 0.36, 0.05, 0.34, 0.9]); clean(g)
            st = h[s]
            draw_graph(g, self.pos, [e for e in self.G.edges() if st[e[0]] != 3 and st[e[1]] != 3],
                       {v: SIRC[st[v]] for v in self.G}, {v: 14 + 4 * self.G.degree(v) for v in self.G},
                       edge_colors="#e2e6ef", edge_widths=0.6)
            fit_view(g, self.pos, 0.03)
            inf = sum(1 for v in st.values() if v in (1, 2)) / 200
            g.set_title(f"{title}\n累计感染 {inf:.0%}", fontsize=15, color=INK)
        if k >= 100:
            a = panel(ax, [0.77, 0.2, 0.2, 0.6]); plot_style(a)
            a.bar([0, 1], [self.mean_r, self.mean_h], color=[BLUE, GREEN], width=0.6)
            a.set_xticks([0, 1]); a.set_xticklabels(["随机", "枢纽"], fontsize=13)
            a.set_ylabel("平均感染规模（30 次）", fontsize=12); a.set_ylim(0, 1)
            for x, y in [(0, self.mean_r), (1, self.mean_h)]:
                a.text(x, y + 0.03, f"{y:.0%}", ha="center", fontsize=14, color=INK)


class Kuramoto:
    def __init__(self, p, T, cues):
        rng = np.random.default_rng(3)
        N = 40
        w = rng.normal(0, 0.6, N)
        th = rng.uniform(0, 2 * np.pi, N)
        steps = 900
        dt = 0.05
        self.Ks = np.linspace(0, 2.6, steps)
        hist, rs = [], []
        for i in range(steps):
            K = self.Ks[i]
            z = np.exp(1j * th).mean()
            r, psi = abs(z), np.angle(z)
            th = th + dt * (w + K * r * np.sin(psi - th))
            hist.append(th.copy()); rs.append(r)
        self.hist, self.rs, self.w = hist, np.array(rs), w
        self.steps = steps
        self.T = T

    def key(self, t):
        return int(prog(t, self.T, 0.02, 0.95) * (self.steps - 1))

    def draw(self, ax, t):
        clean(ax)
        i = self.key(t)
        th = self.hist[i]
        g = panel(ax, [0.02, 0.05, 0.42, 0.9]); clean(g)
        g.add_patch(Circle((0, 0), 1, fill=False, ec=FAINT, lw=2))
        import matplotlib.cm as cm
        cols = cm.coolwarm((self.w - self.w.min()) / (np.ptp(self.w) + 1e-9))
        g.scatter(np.cos(th), np.sin(th), c=cols, s=140, edgecolors="white", zorder=3)
        z = np.exp(1j * th).mean()
        g.add_patch(FancyArrowPatch((0, 0), (z.real, z.imag), arrowstyle="-|>", mutation_scale=22, color=INK, lw=3))
        g.set_xlim(-1.3, 1.3); g.set_ylim(-1.3, 1.3); g.set_aspect("equal")
        g.set_title(f"耦合强度 K = {self.Ks[i]:.2f}    序参量 r = {abs(z):.2f}", fontsize=16, color=INK)
        a = panel(ax, [0.56, 0.18, 0.41, 0.66]); plot_style(a)
        a.plot(self.Ks[:i + 1], self.rs[:i + 1], color=BLUE, lw=2.2)
        a.set_xlim(0, self.Ks[-1]); a.set_ylim(0, 1)
        Kc = 2 / (np.pi * (1 / (0.6 * np.sqrt(2 * np.pi))))
        a.axvline(Kc, color=MUTED, ls="--")
        a.text(Kc + 0.05, 0.9, "临界耦合 Kc", fontsize=13, color=MUTED)
        a.set_xlabel("耦合强度 K", fontsize=14); a.set_ylabel("同步程度 r", fontsize=14)


# --------------------------------------------------------------------------- control / robustness
class Control:
    def __init__(self, p, T, cues):
        D = nx.gnp_random_graph(14, 0.13, seed=12, directed=True)
        self.D = D
        self.pos = nx.kamada_kawai_layout(D.to_undirected())
        B = nx.Graph()
        top = [("o", v) for v in D]
        B.add_nodes_from(top); B.add_nodes_from(("i", v) for v in D)
        B.add_edges_from((("o", u), ("i", v)) for u, v in D.edges())
        M = nx.bipartite.hopcroft_karp_matching(B, top_nodes=top)
        self.match = [(u[1], v[1]) for u, v in M.items() if u[0] == "o"]
        matched_in = {v for _, v in self.match}
        self.drivers = [v for v in D if v not in matched_in]
        self.T = T

    def key(self, t):
        return int(prog(t, self.T, 0.08, 0.7) * (len(self.match) + 1.999))

    def draw(self, ax, t):
        clean(ax)
        k = self.key(t)
        g = panel(ax, [0.0, 0.03, 0.6, 0.94]); clean(g)
        ms = set(self.match[:k])
        for u, v in self.D.edges():
            hot = (u, v) in ms
            g.add_patch(FancyArrowPatch(self.pos[u], self.pos[v], arrowstyle="-|>", mutation_scale=16,
                                        color=ORANGE if hot else "#9aa8d6", lw=3 if hot else 1.3,
                                        shrinkA=13, shrinkB=13, zorder=2))
        show_d = k > len(self.match)
        cols = {v: (RED if show_d and v in self.drivers else BLUE) for v in self.D}
        draw_graph(g, self.pos, [], cols, 520, labels={v: str(v + 1) for v in self.D}, label_size=12)
        if show_d:
            for v in self.drivers:
                x, y = self.pos[v]
                g.add_patch(FancyArrowPatch((x - 0.28, y + 0.22), (x - 0.06, y + 0.04), arrowstyle="-|>",
                                            mutation_scale=16, color=RED, lw=2.4, zorder=4))
        fit_view(g, self.pos, 0.12)
        txt = [f"有向边数 {self.D.number_of_edges()}", f"最大匹配边数 |M*| = {min(k, len(self.match))}"]
        if show_d:
            txt.append(f"驱动节点数 N_D = N − |M*| = {len(self.drivers)}")
        for j, s in enumerate(txt):
            ax.text(0.64, 0.75 - j * 0.12, s, transform=ax.transAxes, fontsize=19, color=RED if j == 2 else INK)
        ax.text(0.64, 0.32, "橙色：匹配边\n红色：驱动节点（需外部输入）", transform=ax.transAxes, fontsize=15, color=MUTED)


def giant_curve(G, order, n_pts=40):
    N = G.number_of_nodes()
    H = G.copy()
    fs, gs = [0], [len(max(nx.connected_components(H), key=len)) / N]
    step = max(1, len(order) // n_pts)
    for i in range(0, len(order), step):
        H.remove_nodes_from(order[i:i + step])
        if H.number_of_nodes() == 0:
            fs.append(1); gs.append(0); break
        fs.append(min(1, (i + step) / N))
        gs.append(len(max(nx.connected_components(H), key=len)) / N)
    return np.array(fs), np.array(gs)


class Robustness:
    def __init__(self, p, T, cues):
        big = nx.barabasi_albert_graph(1500, 2, seed=3)
        rng = np.random.default_rng(2)
        self.fr, self.gr = giant_curve(big, list(rng.permutation(1500)))
        self.fa, self.ga = giant_curve(big, sorted(big, key=big.degree, reverse=True))
        G = nx.barabasi_albert_graph(160, 2, seed=6)
        self.G = G
        self.pos = nx.spring_layout(G, seed=1, k=0.13)
        self.att = sorted(G, key=G.degree, reverse=True)
        self.T = T

    def key(self, t):
        return int(prog(t, self.T, 0.05, 0.85) * 100)

    def draw(self, ax, t):
        clean(ax)
        f = self.key(t) / 100 * 0.5
        rem = set(self.att[:int(f * 160 * 0.6)])
        H = self.G.subgraph([v for v in self.G if v not in rem])
        gc = max(nx.connected_components(H), key=len) if H.number_of_nodes() else set()
        g = panel(ax, [0.0, 0.03, 0.5, 0.94]); clean(g)
        draw_graph(g, {v: self.pos[v] for v in H}, list(H.edges()), {v: (BLUE if v in gc else "#b8c0d6") for v in H},
                   {v: 18 + 5 * self.G.degree(v) for v in H}, edge_colors="#d0d6e6", edge_widths=0.8)
        fit_view(g, self.pos, 0.03)
        g.set_title(f"蓄意攻击：已移除度最大的 {len(rem)} 个节点", fontsize=15, color=INK)
        a = panel(ax, [0.6, 0.18, 0.37, 0.66]); plot_style(a)
        a.plot(self.fr[self.fr <= f + 1e-9], self.gr[self.fr <= f + 1e-9], color=BLUE, lw=2.5, label="随机失效")
        a.plot(self.fa[self.fa <= f + 1e-9], self.ga[self.fa <= f + 1e-9], color=RED, lw=2.5, label="蓄意攻击")
        a.set_xlim(0, 0.5); a.set_ylim(0, 1)
        a.set_xlabel("移除节点比例 f", fontsize=14); a.set_ylabel("巨连通分支占比", fontsize=14)
        a.legend(frameon=False, fontsize=13)
        a.set_title("无标度网络（N = 1500）", fontsize=15, color=INK)


# --------------------------------------------------------------------------- brain
def modular_corr(n_mod=4, per=10, n_t=300, seed=0, strength=0.9):
    rng = np.random.default_rng(seed)
    n = n_mod * per
    F = rng.normal(size=(n_t, n_mod))
    glob = rng.normal(size=(n_t, 1))
    X = np.zeros((n_t, n))
    for m in range(n_mod):
        for j in range(per):
            X[:, m * per + j] = strength * F[:, m] + 0.35 * glob[:, 0] + rng.normal(size=n_t)
    return np.corrcoef(X.T), np.repeat(np.arange(n_mod), per)


class BrainThreshold:
    def __init__(self, p, T, cues):
        self.C, self.lab = modular_corr(seed=4)
        n = self.C.shape[0]
        self.n = n
        iu = np.triu_indices(n, 1)
        self.iu = iu
        self.w = self.C[iu]
        self.pos = {}
        ang = np.linspace(np.pi / 2, np.pi / 2 - 2 * np.pi, n, endpoint=False)
        for i in range(n):
            self.pos[i] = (np.cos(ang[i]), np.sin(ang[i]))
        self.dens = np.linspace(0.6, 0.05, 40)
        self.metrics = []
        for d in self.dens:
            G, _ = self.graph(d)
            self.metrics.append((nx.average_clustering(G), nx.number_connected_components(G)))
        self.T = T

    def graph(self, d):
        k = int(round(d * len(self.w)))
        thr = np.sort(self.w)[::-1][k - 1]
        G = nx.Graph(); G.add_nodes_from(range(self.n))
        for a, b, w in zip(self.iu[0], self.iu[1], self.w):
            if w >= thr:
                G.add_edge(a, b)
        return G, thr

    def key(self, t):
        return int(prog(t, self.T, 0.05, 0.9) * (len(self.dens) - 1))

    def draw(self, ax, t):
        clean(ax)
        i = self.key(t)
        d = self.dens[i]
        G, thr = self.graph(d)
        m = panel(ax, [0.0, 0.12, 0.3, 0.76])
        M = np.where(self.C >= thr, self.C, np.nan)
        np.fill_diagonal(M, np.nan)
        m.imshow(M, cmap="Reds", vmin=0, vmax=0.8)
        m.set_xticks([]); m.set_yticks([])
        m.set_title(f"相关矩阵（阈值 r ≥ {thr:.2f}）", fontsize=14, color=INK)
        g = panel(ax, [0.31, 0.03, 0.36, 0.94]); clean(g)
        cols = [PALETTE[c] for c in self.lab]
        draw_graph(g, self.pos, list(G.edges()), cols, 90, edge_colors="#9aa8d6", edge_widths=0.6)
        fit_view(g, self.pos, 0.08)
        g.set_title(f"保留密度 {d:.0%}    边数 {G.number_of_edges()}", fontsize=15, color=INK)
        a = panel(ax, [0.75, 0.18, 0.23, 0.66]); plot_style(a)
        cs = [x[0] for x in self.metrics[:i + 1]]
        a.plot(self.dens[:i + 1], cs, color=GREEN, lw=2.5)
        a.set_xlim(0.62, 0.03); a.set_ylim(0, 1)
        a.set_xlabel("网络密度", fontsize=13); a.set_ylabel("平均聚集系数", fontsize=13)
        a.set_title(f"连通分支数 {self.metrics[i][1]}", fontsize=13, color=INK)


class DFC:
    def __init__(self, p, T, cues):
        rng = np.random.default_rng(6)
        n, L = 6, 600
        states = np.zeros(L, int)
        for s, e in [(150, 300), (420, 520)]:
            states[s:e] = 1
        X = np.zeros((L, n))
        f = rng.normal(size=(L, 2))
        for t_ in range(L):
            if states[t_] == 0:
                X[t_, :3] = f[t_, 0]; X[t_, 3:] = f[t_, 1]
            else:
                X[t_, ::2] = f[t_, 0]; X[t_, 1::2] = -0.8 * f[t_, 0]
        X += rng.normal(scale=0.8, size=X.shape)
        k = np.ones(5) / 5
        X = np.apply_along_axis(lambda c: np.convolve(c, k, mode="same"), 0, X)
        self.X, self.states, self.L, self.W = X, states, L, 60
        self.T = T

    def key(self, t):
        return int(prog(t, self.T, 0.03, 0.95) * (self.L - self.W))

    def draw(self, ax, t):
        clean(ax)
        s = self.key(t)
        a = panel(ax, [0.04, 0.5, 0.92, 0.46]); plot_style(a)
        for j in range(6):
            a.plot(self.X[:, j] / 2 + j * 2.2, color=PALETTE[j % 6], lw=1)
        a.add_patch(Rectangle((s, -1.5), self.W, 14, fc=ORANGE, alpha=0.15, ec=ORANGE, lw=2))
        a.set_yticks([]); a.set_xlim(0, self.L); a.set_xlabel("时间点（TR）", fontsize=13)
        a.set_title("6 个脑区的模拟 BOLD 信号与滑动窗口", fontsize=14, color=INK)
        m = panel(ax, [0.06, 0.0, 0.3, 0.42])
        C = np.corrcoef(self.X[s:s + self.W].T)
        m.imshow(C, cmap="RdBu_r", vmin=-1, vmax=1)
        m.set_xticks([]); m.set_yticks([])
        m.set_title("窗口内相关矩阵", fontsize=13, color=INK)
        st = int(round(self.states[s:s + self.W].mean()))
        ax.text(0.42, 0.25, f"当前窗口：连接状态 {'A' if st == 0 else 'B'}", transform=ax.transAxes,
                fontsize=20, color=BLUE if st == 0 else RED)
        ax.text(0.42, 0.13, "同一组脑区，在不同时间段\n呈现不同的连接模式", transform=ax.transAxes, fontsize=15, color=MUTED)


# --------------------------------------------------------------------------- symptom network
SYMPTOMS = ["情绪低落", "兴趣减退", "睡眠问题", "疲乏", "食欲改变", "自我否定", "注意困难", "精神运动", "自杀意念"]


class SymptomNet:
    def __init__(self, p, T, cues):
        n = 9
        P = np.eye(n)
        links = [(0, 1, .35), (0, 5, .3), (1, 3, .25), (2, 3, .4), (3, 6, .25), (5, 8, .35), (0, 8, .2),
                 (4, 2, .2), (6, 7, .2), (1, 6, .15), (4, 3, -.12)]
        for a, b, w in links:
            P[a, b] = P[b, a] = -w
        Sigma = np.linalg.inv(P)
        rng = np.random.default_rng(1)
        X = rng.multivariate_normal(np.zeros(n), Sigma, size=600)
        C = np.corrcoef(X.T)
        Pi = np.linalg.inv(np.cov(X.T))
        d = np.sqrt(np.diag(Pi))
        PC = -Pi / np.outer(d, d)
        np.fill_diagonal(PC, 0)
        np.fill_diagonal(C, 0)
        self.C, self.PC = C, PC
        self.pos = circle_pos(range(n), 1.0)
        self.T = T

    def key(self, t):
        f = t / self.T
        return 0 if f < 0.35 else (1 if f < 0.65 else 2)

    def draw(self, ax, t):
        clean(ax)
        k = self.key(t)
        W = self.C if k == 0 else self.PC
        thr = 0.08
        g = panel(ax, [0.0, 0.02, 0.55, 0.96]); clean(g)
        for i in range(9):
            for j in range(i + 1, 9):
                w = W[i, j]
                if abs(w) > thr:
                    g.plot([self.pos[i][0], self.pos[j][0]], [self.pos[i][1], self.pos[j][1]],
                           color=BLUE if w > 0 else RED, lw=abs(w) * 14, alpha=0.75, solid_capstyle="round")
        for i in range(9):
            x, y = self.pos[i]
            g.add_patch(Circle((x, y), 0.17, fc="white", ec=INK, lw=1.5, zorder=3))
            g.text(x, y, SYMPTOMS[i], ha="center", va="center", fontsize=11, zorder=4, color=INK)
        g.set_xlim(-1.3, 1.3); g.set_ylim(-1.3, 1.3); g.set_aspect("equal")
        g.set_title("相关网络：几乎处处相连" if k == 0 else "偏相关网络：控制其他症状后的直接关联",
                    fontsize=15, color=INK)
        if k == 2:
            a = panel(ax, [0.66, 0.12, 0.3, 0.76]); plot_style(a)
            strength = np.abs(self.PC).sum(1)
            o = np.argsort(strength)
            a.barh(range(9), strength[o], color=BLUE)
            a.set_yticks(range(9)); a.set_yticklabels([SYMPTOMS[i] for i in o], fontsize=12)
            a.set_xlabel("强度中心性", fontsize=13)
            a.set_title("哪个症状连接最强？", fontsize=14, color=INK)
        else:
            ax.text(0.62, 0.55, "蓝色：正关联\n红色：负关联\n线宽：关联强度", transform=ax.transAxes, fontsize=17, color=MUTED)


# --------------------------------------------------------------------------- molecular
class MotifFFL:
    def __init__(self, p, T, cues):
        dt = 0.05
        tt = np.arange(0, 30, dt)
        X = ((tt > 2) & (tt < 4)) | ((tt > 12) & (tt < 22))
        Y = np.zeros_like(tt); Z = np.zeros_like(tt)
        for i in range(1, len(tt)):
            Y[i] = Y[i - 1] + dt * (1.0 * X[i] - 0.4 * Y[i - 1])
            act = X[i] and Y[i] > 1.2
            Z[i] = Z[i - 1] + dt * (1.0 * act - 0.4 * Z[i - 1])
        self.tt, self.X, self.Y, self.Z = tt, X.astype(float), Y, Z
        self.T = T

    def key(self, t):
        return int(prog(t, self.T, 0.05, 0.9) * (len(self.tt) - 1)) // 3

    def draw(self, ax, t):
        clean(ax)
        i = min(self.key(t) * 3, len(self.tt) - 1)
        g = panel(ax, [0.0, 0.1, 0.32, 0.8]); clean(g)
        P = {"X": (0, 1), "Y": (1, 0.2), "Z": (0, -0.6)}
        on = {"X": self.X[i] > 0, "Y": self.Y[i] > 1.2, "Z": self.Z[i] > 0.4}
        for a, b in [("X", "Y"), ("Y", "Z"), ("X", "Z")]:
            g.add_patch(FancyArrowPatch(P[a], P[b], arrowstyle="-|>", mutation_scale=22, color=INK, lw=2.4,
                                        shrinkA=24, shrinkB=24))
        for k_, (x, y) in P.items():
            g.add_patch(Circle((x, y), 0.22, fc=ORANGE if on[k_] else "#c5cbe0", ec=INK, lw=1.5, zorder=3))
            g.text(x, y, k_, ha="center", va="center", fontsize=22, fontweight="bold", color="white", zorder=4)
        g.text(0.5, -1.1, "Z = X AND Y", ha="center", fontsize=16, color=MUTED)
        g.set_xlim(-0.6, 1.6); g.set_ylim(-1.3, 1.4); g.set_aspect("equal")
        g.set_title("一致型前馈环", fontsize=16, color=INK)
        for j, (sig, lab, col) in enumerate([(self.X, "输入 X", BLUE), (self.Y, "中间 Y", PURPLE), (self.Z, "输出 Z", ORANGE)]):
            a = panel(ax, [0.4, 0.68 - j * 0.3, 0.57, 0.24]); plot_style(a)
            a.plot(self.tt[:i + 1], sig[:i + 1], color=col, lw=2.5)
            a.set_xlim(0, 30); a.set_ylim(-0.1, max(sig.max(), 1) * 1.15)
            a.set_ylabel(lab, fontsize=13, rotation=0, ha="right", va="center")
            a.set_yticks([])
            if j < 2:
                a.set_xticks([])
        ax.text(0.68, 0.0, "短脉冲被过滤，持续信号才能激活 Z", transform=ax.transAxes, ha="center", fontsize=15, color=MUTED)


class PPIHubs:
    def __init__(self, p, T, cues):
        G = nx.barabasi_albert_graph(220, 2, seed=13)
        self.G = G
        self.pos = nx.spring_layout(G, seed=5, k=0.11)
        q = 22
        self.hubs = sorted(G, key=G.degree, reverse=True)[:q]
        rng = np.random.default_rng(3)
        self.rand = rng.choice(220, q, replace=False).tolist()
        self.T = T

    def key(self, t):
        f = t / self.T
        return 0 if f < 0.25 else (1 if f < 0.5 else (2 if f < 0.75 else 3))

    def draw(self, ax, t):
        clean(ax)
        k = self.key(t)
        if k <= 1:
            g = panel(ax, [0.15, 0.02, 0.7, 0.96]); clean(g)
            cols = {v: (RED if k == 1 and v in self.hubs else BLUE) for v in self.G}
            draw_graph(g, self.pos, list(self.G.edges()), cols, {v: 14 + 6 * self.G.degree(v) for v in self.G},
                       edge_colors="#d7dceb", edge_widths=0.7)
            fit_view(g, self.pos, 0.03)
            g.set_title("模拟的蛋白相互作用网络" + ("：红色为枢纽蛋白（度最大的 5%）" if k == 1 else ""), fontsize=16, color=INK)
            return
        for i, (rem, title) in enumerate([(self.rand, "随机删除 10% 的蛋白"), (self.hubs, "删除度最大的 10% 蛋白")]):
            if k == 2 and i == 1:
                continue
            g = panel(ax, [0.02 + i * 0.5, 0.02, 0.46, 0.96]); clean(g)
            H = self.G.subgraph([v for v in self.G if v not in rem])
            comps = sorted(nx.connected_components(H), key=len, reverse=True)
            col = {}
            for j, c in enumerate(comps):
                for v in c:
                    col[v] = BLUE if j == 0 else "#adb5bd"
            draw_graph(g, {v: self.pos[v] for v in H}, list(H.edges()), col, 18, edge_colors="#d7dceb", edge_widths=0.7)
            fit_view(g, self.pos, 0.03)
            g.set_title(f"{title}\n最大连通分支 {len(comps[0]) / 220:.0%}，碎片 {len(comps) - 1} 个", fontsize=15, color=INK)


class DiseaseNetwork:
    def __init__(self, p, T, cues):
        self.dis = ["乳腺癌", "卵巢癌", "结直肠癌", "2型糖尿病", "肥胖", "冠心病"]
        self.genes = ["BRCA1", "BRCA2", "TP53", "PIK3CA", "APC", "KRAS", "TCF7L2", "FTO", "PPARG", "LDLR", "APOE", "MC4R"]
        self.E = [(0, 0), (0, 1), (0, 2), (0, 3), (1, 0), (1, 1), (1, 2), (2, 2), (2, 4), (2, 5), (2, 3),
                  (3, 6), (3, 7), (3, 8), (4, 7), (4, 11), (4, 8), (5, 9), (5, 10), (5, 8)]
        self.T = T

    def key(self, t):
        f = t / self.T
        return 0 if f < 0.4 else (1 if f < 0.65 else 2)

    def draw(self, ax, t):
        clean(ax)
        k = self.key(t)
        g = panel(ax, [0.0, 0.02, 0.5, 0.96]); clean(g)
        pd_ = {i: (0, 5 - i * 1.0) for i in range(6)}
        pg = {j: (2.2, 5.5 - j * 0.55) for j in range(12)}
        shared = {2, 8}
        for d, gg in self.E:
            hot = k >= 1 and gg in shared
            g.plot([pd_[d][0], pg[gg][0]], [pd_[d][1], pg[gg][1]], color=ORANGE if hot else "#b5bfd9", lw=2.4 if hot else 1.2)
        for i, nm in enumerate(self.dis):
            g.add_patch(FancyBboxPatch((pd_[i][0] - 0.75, pd_[i][1] - 0.22), 1.5, 0.44, boxstyle="round,pad=0.02",
                                       fc=RED, ec="none", zorder=3))
            g.text(*pd_[i], nm, ha="center", va="center", color="white", fontsize=12, zorder=4)
        for j, nm in enumerate(self.genes):
            g.add_patch(Circle(pg[j], 0.2, fc=ORANGE if (k >= 1 and j in shared) else BLUE, ec="white", zorder=3))
            g.text(pg[j][0] + 0.3, pg[j][1], nm, va="center", fontsize=10, color=INK)
        g.set_xlim(-1, 3.5); g.set_ylim(-0.7, 5.9)
        g.set_title("疾病–基因二分网络", fontsize=15, color=INK)
        if k == 2:
            h = panel(ax, [0.55, 0.05, 0.43, 0.9]); clean(h)
            B = nx.Graph()
            for d, gg in self.E:
                B.add_edge(("d", d), ("g", gg))
            P = nx.bipartite.weighted_projected_graph(B, [("d", i) for i in range(6)])
            pos = circle_pos(range(6), 1)
            for (a, b, w) in P.edges(data="weight"):
                h.plot([pos[a[1]][0], pos[b[1]][0]], [pos[a[1]][1], pos[b[1]][1]], color=INK, lw=1.5 + 2 * w)
            for i in range(6):
                h.add_patch(Circle(pos[i], 0.25, fc=RED, ec="white", zorder=3))
                h.text(pos[i][0], pos[i][1] - 0.38, self.dis[i], ha="center", fontsize=13, color=INK)
            h.set_xlim(-1.5, 1.5); h.set_ylim(-1.6, 1.4); h.set_aspect("equal")
            h.set_title("投影：共享致病基因的疾病相连", fontsize=15, color=INK)


class WGCNA:
    def __init__(self, p, T, cues):
        rng = np.random.default_rng(2)
        nmod, per, ns = 3, 18, 40
        F = rng.normal(size=(ns, nmod))
        X = np.hstack([F[:, [m]] * rng.uniform(0.7, 1.2, per) + rng.normal(scale=0.9, size=(ns, per)) for m in range(nmod)])
        X = np.hstack([X, rng.normal(size=(ns, 10))])
        perm = rng.permutation(X.shape[1])
        X = X[:, perm]
        self.C = np.corrcoef(X.T)
        A = np.abs(self.C)
        from scipy.cluster.hierarchy import linkage, fcluster, leaves_list
        from scipy.spatial.distance import squareform
        self.pw = list(range(1, 13))
        self.r2 = []
        for b in self.pw:
            k = (A ** b).sum(0) - 1
            h, e = np.histogram(k, bins=10)
            mid = (e[:-1] + e[1:]) / 2
            ok = h > 0
            if ok.sum() > 2:
                c = np.polyfit(np.log10(mid[ok]), np.log10(h[ok] / h.sum()), 1)
                pred = np.polyval(c, np.log10(mid[ok]))
                y = np.log10(h[ok] / h.sum())
                r2 = 1 - ((y - pred) ** 2).sum() / ((y - y.mean()) ** 2).sum()
                self.r2.append(-np.sign(c[0]) * r2)
            else:
                self.r2.append(0)
        self.beta = 6
        Ab = A ** self.beta
        D = 1 - Ab
        np.fill_diagonal(D, 0)
        Z = linkage(squareform(D, checks=False), "average")
        self.leaves = leaves_list(Z)
        self.cl = fcluster(Z, 4, "maxclust")
        self.Ab = Ab
        self.T = T

    def key(self, t):
        f = t / self.T
        return 0 if f < 0.33 else (1 if f < 0.66 else 2)

    def draw(self, ax, t):
        clean(ax)
        k = self.key(t)
        m = panel(ax, [0.02, 0.06, 0.42, 0.88])
        if k == 0:
            m.imshow(self.C, cmap="RdBu_r", vmin=-1, vmax=1)
            m.set_title("基因两两相关矩阵（原始顺序）", fontsize=14, color=INK)
        elif k == 1:
            m.imshow(self.Ab, cmap="Reds", vmin=0, vmax=0.5)
            m.set_title(f"软阈值邻接矩阵 |r|^{self.beta}", fontsize=14, color=INK)
        else:
            o = self.leaves
            m.imshow(self.Ab[np.ix_(o, o)], cmap="Reds", vmin=0, vmax=0.5)
            for i, v in enumerate(o):
                m.add_patch(Rectangle((-3.5, i - 0.5), 2.5, 1, color=PALETTE[self.cl[v] % 8], clip_on=False))
            m.set_title("层次聚类重排 → 共表达模块", fontsize=14, color=INK)
        m.set_xticks([]); m.set_yticks([])
        a = panel(ax, [0.56, 0.2, 0.4, 0.62]); plot_style(a)
        a.plot(self.pw, self.r2, "o-", color=BLUE, lw=2)
        a.axhline(0.8, color=MUTED, ls="--")
        if k >= 1:
            a.plot([self.beta], [self.r2[self.beta - 1]], "o", ms=14, mfc="none", mec=RED, mew=3)
        a.set_xlabel("软阈值幂 β", fontsize=14); a.set_ylabel("无标度拟合 R²", fontsize=14)
        a.set_title("选择 β：使网络近似无标度", fontsize=14, color=INK)


class Proximity:
    def __init__(self, p, T, cues):
        G = nx.connected_watts_strogatz_graph(130, 4, 0.15, seed=9)
        self.G = G
        self.pos = nx.kamada_kawai_layout(G)
        rng = np.random.default_rng(1)
        center = 0
        dist = nx.single_source_shortest_path_length(G, center)
        self.dis = [v for v, d in dist.items() if d <= 2][:12]
        sp = dict(nx.all_pairs_shortest_path_length(G))
        self.sp = sp
        far = sorted(G, key=lambda v: -dist[v])
        near = [v for v, d in dist.items() if d == 3]
        self.drugA = near[:3]
        self.drugB = far[:3]

        def dc(T_, S):
            return np.mean([min(sp[t_][s] for s in S) for t_ in T_])
        self.dA, self.dB = dc(self.drugA, self.dis), dc(self.drugB, self.dis)
        null = [dc(rng.choice(130, 3, replace=False), rng.choice(130, 12, replace=False)) for _ in range(300)]
        self.null = np.array(null)
        self.zA = (self.dA - self.null.mean()) / self.null.std()
        self.zB = (self.dB - self.null.mean()) / self.null.std()
        self.T = T

    def key(self, t):
        f = t / self.T
        return 0 if f < 0.3 else (1 if f < 0.6 else 2)

    def draw(self, ax, t):
        clean(ax)
        k = self.key(t)
        g = panel(ax, [0.0, 0.02, 0.55, 0.96]); clean(g)
        col = {}
        for v in self.G:
            col[v] = RED if v in self.dis else ("#3b5bdb" if v in self.drugA else (PURPLE if v in self.drugB else "#c3c9da"))
        sz = {v: (110 if col[v] != "#c3c9da" else 25) for v in self.G}
        draw_graph(g, self.pos, list(self.G.edges()), col, sz, edge_colors="#e0e4ee", edge_widths=0.7)
        if k >= 1:
            for drug, c in [(self.drugA, BLUE), (self.drugB, PURPLE)]:
                for t_ in drug:
                    s = min(self.dis, key=lambda s_: self.sp[t_][s_])
                    path = nx.shortest_path(self.G, t_, s)
                    xy = np.array([self.pos[v] for v in path])
                    g.plot(xy[:, 0], xy[:, 1], color=c, lw=2.6, zorder=5)
        fit_view(g, self.pos, 0.03)
        g.set_title("红：疾病模块   蓝：药物 A 靶点   紫：药物 B 靶点", fontsize=14, color=INK)
        if k >= 1:
            ax.text(0.6, 0.85, f"药物 A：平均最近距离 d = {self.dA:.2f}", transform=ax.transAxes, fontsize=17, color=BLUE)
            ax.text(0.6, 0.76, f"药物 B：平均最近距离 d = {self.dB:.2f}", transform=ax.transAxes, fontsize=17, color=PURPLE)
        if k >= 2:
            a = panel(ax, [0.62, 0.14, 0.34, 0.48]); plot_style(a)
            a.hist(self.null, bins=15, color="#c3c9da")
            a.axvline(self.dA, color=BLUE, lw=3); a.axvline(self.dB, color=PURPLE, lw=3)
            a.set_xlabel("随机靶点集合的距离", fontsize=13)
            a.set_title(f"z 值：A = {self.zA:.1f}，B = {self.zB:.1f}", fontsize=14, color=INK)


UNITS = [("网络基础理论", ["L01 数学表示", "L02 结构指标", "L03 网络模型", "L04 社团结构", "-- 构建与验证"]),
         ("动力学与控制", ["L05 传播与免疫", "L06 同步", "L07 可控性"]),
         ("脑网络", ["L09 脑连接组", "L10 动态脑网络"]),
         ("症状网络", ["L11 网络精神病学"]),
         ("分子网络", ["L12 分子网络", "L13 调控推断"]),
         ("网络医学", ["L14 疾病模块与药物"]),
         ("计算方法", ["L08 分析流程", "L15 可复现研究", "L16 结果呈现"])]


class KnowledgeMap:
    """Seven knowledge domains of the handbook (not a learning sequence)."""
    def __init__(self, p, T, cues):
        self.hl = p.get("highlight", "")
        self.T = T

    def key(self, t):
        return int(prog(t, self.T, 0.0, 0.6) * len(UNITS))

    def draw(self, ax, t):
        clean(ax)
        ax.set_xlim(0, 7); ax.set_ylim(0, 4)
        shown = self.key(t)
        for i, (u, ls) in enumerate(UNITS[:max(shown, 1)]):
            x = 0.5 + i
            c = PALETTE[i % 8]
            ax.text(x, 3.75, u, ha="center", va="center", fontsize=13, color=c, fontweight="bold")
            for j, l in enumerate(ls):
                y = 3.15 - j * 0.66
                code, name = l.split(" ", 1)
                hot = self.hl and code == self.hl
                ax.add_patch(FancyBboxPatch((x - 0.44, y - 0.23), 0.88, 0.46, boxstyle="round,pad=0.02,rounding_size=0.08",
                                            fc=c if hot else "white", ec=c, lw=3 if hot else 1.6))
                ax.text(x, y, name, ha="center", va="center", fontsize=11, color="white" if hot else INK)


class SynapseMap:
    """Shared receiver neuron with input synapses from several source neurons (toy illustration).
    Sources that are connected to each other place their inputs closer together on the receiver."""
    def __init__(self, p, T, cues):
        rng = np.random.default_rng(5)
        self.T = T
        segs = []  # (x0,y0,x1,y1,depth,side)
        def grow(x, y, ang, L, d, side):
            if d > 4:
                return
            x1, y1 = x + L * math.cos(ang), y + L * math.sin(ang)
            segs.append((x, y, x1, y1, d, side))
            for j, da in enumerate((-0.5, 0.5)):
                grow(x1, y1, ang + da + rng.normal(0, 0.06), L * 0.74, d + 1, side if d else j)
        grow(0.45, -0.25, math.pi / 2, 0.42, 0, 0)
        self.segs = segs
        def pts_on(cands, n, lo=0.15, hi=0.9):
            out = []
            for k in range(n):
                x0, y0, x1, y1, _, _ = cands[k % len(cands)]
                u = rng.uniform(lo, hi)
                out.append((x0 + u * (x1 - x0), y0 + u * (y1 - y0)))
            return out
        Lt = [s_ for s_ in segs if s_[5] == 0 and s_[4] >= 2]
        Rt = [s_ for s_ in segs if s_[5] == 1 and s_[4] >= 2]
        Lt.sort(key=lambda s_: s_[2]); Rt.sort(key=lambda s_: -s_[2])
        self.syn = {"A": pts_on(Lt[:5], 8, 0.15, 0.5), "B": pts_on(Lt[:5], 8, 0.55, 0.92), "D": pts_on(Rt[:5], 8)}
        self.col = {"A": BLUE, "B": ORANGE, "D": GREEN}
        self.src = {"A": (-0.85, 1.25), "B": (-0.85, 0.75), "D": (-0.85, 0.25)}

    def key(self, t):
        return int(prog(t, self.T, 0.0, 0.95) * 60)

    def draw(self, ax, t):
        clean(ax)
        k = self.key(t) / 60
        g = panel(ax, [0.02, 0.06, 0.6, 0.88]); clean(g)
        for x0, y0, x1, y1, d, _ in self.segs:
            g.plot([x0, x1], [y0, y1], color="#8a93a8", lw=max(1.5, 7 - d * 1.3), solid_capstyle="round", zorder=1)
        g.add_patch(Circle((0.45, -0.3), 0.08, fc="#8a93a8", ec="none", zorder=2))
        g.text(0.45, -0.5, "共同接收神经元（下行神经元）", ha="center", fontsize=14, color=MUTED)
        for j, s in enumerate("ABD"):
            n_show = int(np.clip((k - 0.08 - j * 0.1) / 0.25, 0, 1) * len(self.syn[s]))
            sx, sy = self.src[s]
            g.add_patch(Circle((sx, sy), 0.07, fc=self.col[s], ec=INK, lw=1.2, zorder=3))
            g.text(sx - 0.12, sy, f"输入 {s}", ha="right", va="center", fontsize=14, color=INK)
            for (x, y) in self.syn[s][:n_show]:
                g.add_patch(Circle((x, y), 0.032, fc=self.col[s], ec="white", lw=0.8, zorder=4))
        if k > 0.55:
            a = min(1, (k - 0.55) / 0.1)
            g.add_patch(FancyArrowPatch(self.src["A"], self.src["B"], connectionstyle="arc3,rad=-0.5", arrowstyle="-|>",
                                        mutation_scale=18, color=RED, lw=2.4, alpha=a, shrinkA=10, shrinkB=10, zorder=5))
            g.text(-0.62, 1.0, "A 与 B 相连", fontsize=13, color=RED, alpha=a)
        g.set_xlim(-1.35, 1.6); g.set_ylim(-0.6, 1.75); g.set_aspect("equal")
        if k > 0.7:
            b = panel(ax, [0.68, 0.22, 0.28, 0.56]); plot_style(b)
            h = min(1, (k - 0.7) / 0.15)
            b.bar([0, 1], [0.35 * h, 0.8 * h], color=[RED, "#adb5bd"], width=0.6)
            b.set_xticks([0, 1]); b.set_xticklabels(["相连的输入对", "不相连的输入对"], fontsize=12)
            b.set_yticks([]); b.set_ylim(0, 1)
            b.set_title("输入位点之间的路径距离", fontsize=14, color=INK)
            ax.text(0.82, 0.12, "示意图，非真实数据", transform=ax.transAxes, ha="center", fontsize=12, color=MUTED)


ASSETS = __import__("pathlib").Path(__file__).resolve().parent / "assets"
_IMG_CACHE = {}


class Image:
    """Show a still image (e.g. a screenshot of a companion website) with a slow Ken Burns move.
    params: src (path under video/assets), start/end crop boxes [x0, y0, x1, y1] as fractions, caption, credit."""
    def __init__(self, p, T, cues):
        import matplotlib.image as mpimg
        src = str(ASSETS / p["src"])
        if src not in _IMG_CACHE:
            _IMG_CACHE[src] = mpimg.imread(src)
        self.img = _IMG_CACHE[src]
        self.h, self.w = self.img.shape[:2]
        self.a = p.get("start", [0, 0, 1, 1])
        self.b = p.get("end", self.a)
        self.caption = p.get("caption", "")
        self.credit = p.get("credit", "")
        self.T = T

    def key(self, t):
        return int(prog(t, self.T, 0.0, 1.0) * 120)

    def draw(self, ax, t):
        clean(ax)
        u = ease(self.key(t) / 120)
        box = [self.a[i] + (self.b[i] - self.a[i]) * u for i in range(4)]
        x0, y0, x1, y1 = box[0] * self.w, box[1] * self.h, box[2] * self.w, box[3] * self.h
        # fit the crop into the 16:9-ish panel, keeping aspect
        g = panel(ax, [0.04, 0.13 if self.caption else 0.02, 0.92, 0.85 if self.caption else 0.96]); clean(g)
        g.imshow(self.img, interpolation="lanczos", aspect="auto")
        bb = g.get_window_extent(); R = bb.width / max(bb.height, 1)
        cx, cy, w, h = (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0
        if w / h > R:
            h = w / R
        else:
            w = h * R
        w, h = min(w, self.w), min(h, self.h)
        if w / h > R:
            w = h * R
        else:
            h = w / R
        cx = min(max(cx, w / 2), self.w - w / 2); cy = min(max(cy, h / 2), self.h - h / 2)
        g.set_xlim(cx - w / 2, cx + w / 2); g.set_ylim(cy + h / 2, cy - h / 2)
        for sp in g.spines.values():
            sp.set_visible(True); sp.set_color(FAINT)
        if self.caption:
            ax.text(0.5, 0.02, self.caption, transform=ax.transAxes, ha="center", fontsize=15, color=INK)
        if self.credit:
            ax.text(0.96, 0.095, self.credit, transform=ax.transAxes, ha="right", fontsize=11, color=MUTED)


REGISTRY = {
    "image": Image,
    "synapse_map": SynapseMap,
    "title": Title, "bullets": Bullets, "formula": Formula,
    "graph_adjacency": GraphAdjacency, "path_bfs": PathBFS, "clustering": Clustering,
    "degree_dist": DegreeDist, "er_growth": ERGrowth, "ws_rewire": WSRewire, "ba_growth": BAGrowth,
    "community": Community, "sir": SIR, "immunization": Immunization, "kuramoto": Kuramoto,
    "control": Control, "robustness": Robustness, "brain_threshold": BrainThreshold, "dfc": DFC,
    "symptom_net": SymptomNet, "motif_ffl": MotifFFL, "ppi_hubs": PPIHubs,
    "disease_network": DiseaseNetwork, "wgcna": WGCNA, "proximity": Proximity, "knowledge_map": KnowledgeMap,
}
