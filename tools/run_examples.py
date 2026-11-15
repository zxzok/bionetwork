#!/usr/bin/env python3
"""Run every code example once and keep its figures and printed output for the code gallery.

    .venv/bin/python tools/run_examples.py            # only examples whose code changed
    .venv/bin/python tools/run_examples.py --force    # everything

Results go to build/gallery/<topic>-<n>.json and build/gallery/<topic>-<n>-<k>.png;
build.py copies the images into dist/gallery/ and uses the JSON for the gallery pages.
"""
import hashlib
import json
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CODE = ROOT / "content" / "code"
OUT = ROOT / "build" / "gallery"
PY = ROOT / ".venv" / "bin" / "python"

PRELUDE = r'''
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["PingFang SC", "Hiragino Sans GB", "Arial Unicode MS", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["figure.dpi"] = 110
__figs = []
def __save(*a, **k):
    for num in plt.get_fignums():
        f = plt.figure(num)
        if id(f) in {id(x) for x in __figs}:
            continue
        __figs.append(f)
plt.show = __save
import matplotlib.figure as __mf
__orig_savefig = __mf.Figure.savefig
def __savefig(self, *a, **k):
    if id(self) not in {id(x) for x in __figs}:
        __figs.append(self)
    return __orig_savefig(self, *a, **k)
__mf.Figure.savefig = __savefig
__orig_close = plt.close
def __close(*a, **k):
    __save()
    return __orig_close(*a, **k)
plt.close = __close
'''
EPILOGUE = r'''
__save()
for __i, __f in enumerate(__figs[:4]):
    __orig_savefig(__f, __OUT + "-%d.png" % __i, bbox_inches="tight", facecolor="white")
print("__NFIGS__=%d" % min(len(__figs), 4))
'''


def cells(path):
    src = path.read_text(encoding="utf-8")
    chunks = re.split(r"(?m)^# %%\s*", src)
    for ch in chunks[1:]:
        title, _, code = ch.partition("\n")
        yield re.sub(r"^示例[：:]\s*", "", title.strip()), code.strip("\n")


def run(job):
    tid, i, title, code, force = job
    stem = OUT / f"{tid}-{i}"
    meta_p = stem.with_suffix(".json")
    h = hashlib.sha1(code.encode()).hexdigest()
    if not force and meta_p.exists():
        old = json.loads(meta_p.read_text(encoding="utf-8"))
        if old.get("hash") == h:
            return f"skip {tid}-{i}"
    for old_png in OUT.glob(f"{tid}-{i}-*.png"):
        old_png.unlink()
    script = PRELUDE + f"\n__OUT = {str(stem)!r}\n" + code + "\n" + EPILOGUE
    tmp = OUT / f"_run_{tid}_{i}.py"
    tmp.write_text(script, encoding="utf-8")
    try:
        r = subprocess.run([str(PY), "-I", str(tmp)], capture_output=True, text=True, timeout=300, cwd=str(OUT))
        out, err, ok = r.stdout, r.stderr, r.returncode == 0
    except subprocess.TimeoutExpired:
        out, err, ok = "", "timeout", False
    tmp.unlink(missing_ok=True)
    m = re.search(r"__NFIGS__=(\d+)", out)
    nfig = int(m.group(1)) if m else 0
    out = re.sub(r"__NFIGS__=\d+\n?", "", out)
    lines = out.splitlines()
    if len(lines) > 60:
        lines = lines[:60] + [f"…（其余 {len(lines) - 60} 行省略）"]
    meta = {"topic": tid, "index": i, "title": title, "hash": h, "ok": ok, "figures": nfig,
            "stdout": "\n".join(lines), "stderr": "" if ok else err[-1500:]}
    meta_p.write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    return f"{'ok  ' if ok else 'FAIL'} {tid}-{i} figs={nfig}"


def main():
    force = "--force" in sys.argv
    OUT.mkdir(parents=True, exist_ok=True)
    jobs = []
    for p in sorted(CODE.glob("*.py")):
        for i, (title, code) in enumerate(cells(p)):
            jobs.append((p.stem, i, title, code, force))
    with ThreadPoolExecutor(max_workers=6) as ex:
        for msg in ex.map(run, jobs):
            print(msg, flush=True)


if __name__ == "__main__":
    main()
