"""Make networkx layouts identical on every render machine (imported by common.py).

Force-directed layouts iterate on floating-point sums, so Linux/x86 and macOS/arm64 drift apart and the same scene
draws its network differently. This module wraps the iterative layout functions of networkx:

  macOS : compute as usual and store the result in v2/layout_cache/<key>.json (key = hash of the function, the graph's
          nodes and edges in order, and every argument, including the seed or the state of a seed generator);
  Linux : read the stored result; a missing key raises LayoutCacheMiss (never computes).
  NXCACHE_MODE=compute|read|off overrides the platform default.

A seed passed as np.random.Generator / RandomState (or seed=None, which uses numpy's global state) is advanced to the
state it had after the real call, so later random draws in the scene are the same everywhere.
With NXCACHE_EP=<ep_module> set, the keys used and the hashes of the scene's source files are written at exit to
layout_cache/_ep/<ep_module>.json; farm_manifest.py --layouts-ok checks it before a Linux render.
"""
import atexit
import hashlib
import json
import os
import platform
import sys
from pathlib import Path

import networkx as nx
import numpy as np

V2 = Path(__file__).resolve().parent
DIR = V2 / "layout_cache"
MODE = os.environ.get("NXCACHE_MODE") or ("read" if platform.system() == "Linux" else "compute")
WRAP = ["spring_layout", "fruchterman_reingold_layout", "kamada_kawai_layout", "spectral_layout",
        "forceatlas2_layout", "arf_layout"]
USED = []


class LayoutCacheMiss(RuntimeError):
    pass


def _canon(x):
    if isinstance(x, np.random.Generator):
        return ["Generator", _canon(x.bit_generator.state)]
    if isinstance(x, np.random.RandomState):
        return ["RandomState", _canon(x.get_state(legacy=False))]
    if isinstance(x, np.ndarray):
        return ["nd", list(x.shape), [repr(float(v)) for v in x.ravel()]]
    if isinstance(x, (np.floating, float)):
        return repr(float(x))
    if isinstance(x, (np.integer, int, bool)) or x is None or isinstance(x, str):
        return x
    if isinstance(x, dict):
        return [["k", repr(k), _canon(v)] for k, v in x.items()]
    if isinstance(x, (list, tuple)):
        return [_canon(v) for v in x]
    if isinstance(x, (set, frozenset)):
        return sorted(repr(v) for v in x)
    return repr(x)


def _rng_of(seed):
    """The generator whose state the call consumes (so it can be restored on a cache hit)."""
    if isinstance(seed, (np.random.Generator, np.random.RandomState)):
        return seed
    if seed is None:
        return np.random.mtrand._rand
    return None


def _get_state(r):
    return r.bit_generator.state if isinstance(r, np.random.Generator) else r.get_state(legacy=False)


def _set_state(r, st):
    if isinstance(r, np.random.Generator):
        r.bit_generator.state = st
    else:
        st = dict(st); st["state"] = dict(st["state"]); st["state"]["key"] = np.array(st["state"]["key"], dtype=np.uint32)
        r.set_state(st)


def _jsonable(st):
    return json.loads(json.dumps(st, default=lambda o: o.tolist() if isinstance(o, np.ndarray) else int(o)))


def _has_seed(fn):
    import inspect
    try:
        return "seed" in inspect.signature(fn).parameters
    except (TypeError, ValueError):
        return True


def _wrap(name, fn):
    takes_seed = _has_seed(fn)

    def layout(G, *args, **kw):
        nodes = list(G)
        seed = kw.get("seed")
        rng = _rng_of(seed) if takes_seed and not args[5:6] else None
        spec = [name, nx.__version__, G.is_directed(), [repr(v) for v in nodes],
                [[repr(u), repr(v), _canon(d)] for u, v, d in G.edges(data=True)],
                _canon(list(args)), _canon(sorted(kw.items(), key=lambda kv: kv[0])),
                _canon(_get_state(rng)) if rng is not None else None]
        key = hashlib.sha1(json.dumps(spec, ensure_ascii=False).encode()).hexdigest()[:20]
        USED.append(key)
        f = DIR / f"{key}.json"
        if MODE == "read":
            if not f.exists():
                raise LayoutCacheMiss(f"{name}: no cached layout {key} for this graph ({len(nodes)} nodes). "
                                      "Fill it on a Mac (farm_fill_layouts.sh) or render this episode on a Mac.")
            d = json.loads(f.read_text())
            if rng is not None and d.get("rng_after") is not None:
                _set_state(rng, d["rng_after"])
            return {v: np.array(p, dtype=float) for v, p in zip(nodes, d["pos"])}
        pos = fn(G, *args, **kw)
        if not f.exists():
            DIR.mkdir(parents=True, exist_ok=True)
            d = {"fn": name, "pos": [[float(c) for c in np.asarray(pos[v]).ravel()] for v in nodes],
                 "rng_after": _jsonable(_get_state(rng)) if rng is not None else None}
            tmp = f.with_suffix(f".tmp{os.getpid()}")
            tmp.write_text(json.dumps(d)); os.replace(tmp, f)
        # use exactly the stored numbers, as Linux will
        d = json.loads(f.read_text())
        return {v: np.array(p, dtype=float) for v, p in zip(nodes, d["pos"])}
    layout.__wrapped__ = fn
    layout._nxcache = True
    layout.__name__ = name
    return layout


if MODE != "off":
    for _n in WRAP:
        _f = getattr(nx, _n, None)
        if _f is not None and not getattr(_f, "_nxcache", False):
            setattr(nx, _n, _wrap(_n, _f))
            if hasattr(nx, "drawing") and hasattr(nx.drawing, "layout") and hasattr(nx.drawing.layout, _n):
                setattr(nx.drawing.layout, _n, getattr(nx, _n))


def source_hashes():
    """sha1 of the scene source files that can change a layout (not narration, footage list or captions)."""
    out = {}
    for m in list(sys.modules.values()):
        f = getattr(m, "__file__", None)
        if not f:
            continue
        p = Path(f).resolve()
        if p.suffix == ".py" and p.parent in (V2, V2 / "intro") and not p.stem.startswith("lines_") \
                and p.stem not in ("nxcache", "farm_manifest", "footage", "voice_idx", "clip_insert"):
            out[p.relative_to(V2).as_posix()] = hashlib.sha1(p.read_bytes()).hexdigest()
    return out


@atexit.register
def _write_episode_marker():
    ep = os.environ.get("NXCACHE_EP")
    if not ep or MODE != "compute" or Path(sys.argv[0]).name != "manim":   # only the scene-rendering process
        return
    try:
        (DIR / "_ep").mkdir(parents=True, exist_ok=True)
        f = DIR / "_ep" / f"{ep}.json"
        tmp = f.with_suffix(f".tmp{os.getpid()}")
        tmp.write_text(json.dumps({"keys": sorted(set(USED)), "src": source_hashes()}, indent=0))
        os.replace(tmp, f)
    except Exception as e:  # never break a render over the marker
        print("nxcache marker failed:", e, file=sys.stderr)
