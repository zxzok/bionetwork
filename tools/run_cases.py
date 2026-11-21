#!/usr/bin/env python3
"""Run each real-data case once and keep its printed output and figures, so case pages show results before anyone runs them.

    taskpolicy -b nice -n 15 .venv/bin/python tools/run_cases.py [topic-ids…] [--force]

Results: build/cases/<topic>.json and build/cases/<topic>-<cell>-<k>.png (build.py copies them into dist/gallery/cases/).
A case whose source changed after its last run is shown without saved results until it is run again.
Cases run one at a time, in content/ (so data/<file> resolves), with MPLBACKEND=Agg.
"""
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
C = Path(os.environ.get("BNS_CONTENT") or ROOT / "content")
OUT = ROOT / "build" / "cases"
PY = str(ROOT / ".venv" / "bin" / "python")
sys.path.insert(0, str(ROOT / "tools"))
from check_content import cells  # noqa: E402

DRIVER = r'''
import io, json, sys, contextlib, traceback
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["PingFang SC", "Hiragino Sans GB", "Arial Unicode MS", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
plt.show = lambda *a, **k: None
cells, stem = json.load(open(sys.argv[1], encoding="utf-8")), sys.argv[2]
ns, res = {"__name__": "__main__"}, {}
for i, code in enumerate(cells):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            exec(compile(code, f"<cell {i + 1}>", "exec"), ns)
        except Exception:
            traceback.print_exc(file=buf)
            res[str(i)] = {"stdout": buf.getvalue()[-6000:], "figures": 0, "error": True}
            break
    nf = 0
    for n in plt.get_fignums()[:4]:
        plt.figure(n).savefig(f"{stem}-{i}-{nf}.png", dpi=110, bbox_inches="tight", facecolor="white")
        nf += 1
    plt.close("all")
    res[str(i)] = {"stdout": buf.getvalue()[-6000:], "figures": nf}
json.dump(res, open(stem + ".json.tmp", "w", encoding="utf-8"), ensure_ascii=False)
'''


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    force = "--force" in sys.argv
    OUT.mkdir(parents=True, exist_ok=True)
    drv = OUT / "_driver.py"
    drv.write_text(DRIVER, encoding="utf-8")
    bad = 0
    for p in sorted((C / "cases").glob("*.py")):
        tid = p.stem
        if args and tid not in args:
            continue
        h = hashlib.sha1(p.read_bytes()).hexdigest()
        meta = OUT / f"{tid}.json"
        if not force and meta.exists() and json.loads(meta.read_text(encoding="utf-8")).get("hash") == h:
            print("skip", tid)
            continue
        for old in OUT.glob(f"{tid}-*.png"):
            old.unlink()
        code = [body for kind, _, body in cells(p.read_text(encoding="utf-8")) if kind != "markdown" and body.strip()]
        src = OUT / f"_{tid}.json"
        src.write_text(json.dumps(code, ensure_ascii=False), encoding="utf-8")
        r = subprocess.run(["taskpolicy", "-b", "nice", "-n", "15", PY, str(drv), str(src), str(OUT / tid)], cwd=C,
                           capture_output=True, text=True, env={**os.environ, "MPLBACKEND": "Agg"}, timeout=1800)
        src.unlink()
        tmp = OUT / f"{tid}.json.tmp"
        if r.returncode or not tmp.exists():
            print("FAIL", tid, r.stderr[-800:])
            bad += 1
            continue
        res = json.loads(tmp.read_text(encoding="utf-8"))
        tmp.unlink()
        err = any(v.get("error") for v in res.values())
        meta.write_text(json.dumps({"hash": h, "cells": res}, ensure_ascii=False), encoding="utf-8")
        print(("ERROR in " if err else "ok ") + tid, f"{len(res)}/{len(code)} cells")
        bad += err
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
