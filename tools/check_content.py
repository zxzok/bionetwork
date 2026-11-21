#!/usr/bin/env python3
"""Validate quizzes, exercises and data cases (format: content/FORMATS.md).

    .venv/bin/python tools/check_content.py [quizzes|exercises|cases] [IDs…]

quizzes   : schema, answer ranges, answer balance, "see" targets exist, and every "code" question is run and must print its correct option
exercises : task structure (starter/solution/check per task), data files exist, and each file runs setup → solution → check
            top to bottom; every check cell must print a ✓
cases     : data files exist, are listed in content/data/SOURCES.md and are ≤ 5 MB gzipped; each case runs top to bottom
Runs at low priority with MPLBACKEND=Agg. Exit code 1 if anything fails.
"""
import collections
import gzip
import io
import json
import os
import re
import subprocess
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
C = Path(os.environ.get("BNS_CONTENT") or ROOT / "content")   # override for testing only
PY = str(ROOT / ".venv" / "bin" / "python")
os.environ["MPLBACKEND"] = "Agg"


def cells(src):
    """[(kind, title, code)] from a '# %%' file; kind = markdown|setup|starter|solution|check|code."""
    out = []
    for block in re.split(r"(?m)^# %%", src)[1:]:
        head, _, body = block.partition("\n")
        h = head.strip()
        if h.startswith("[markdown]"):
            out.append(("markdown", h[len("[markdown]"):].strip(), body))
        else:
            kind = h.split()[0] if h.split() and h.split()[0] in ("setup", "starter", "solution", "check") else "code"
            out.append((kind, h, body))
    return out


def run_py(code, cwd):
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as f:
        f.write(code)
    r = subprocess.run(["taskpolicy", "-b", "nice", "-n", "15", PY, f.name], capture_output=True, text=True, cwd=cwd, timeout=900)
    os.unlink(f.name)
    return r


def see_ok(see):
    """'topic.html' or 'topic.section.html' must exist in content/topics."""
    name = see.split("#")[0]
    if not name.endswith(".html"):
        return False
    tid, _, sec = name[:-5].partition(".")
    tp = C / "topics" / f"{tid}.md"
    if not tp.exists():
        return name.startswith(("paper-", "r-")) or name in ("lab.html", "code.html", "glossary.html", "resources.html")
    return not sec or re.search(r"(?m)^## .*\{#" + re.escape(sec) + r"\}\s*$", tp.read_text(encoding="utf-8")) is not None


DATA_RE = re.compile(r"""["']data/([\w.\-]+)["']""")


def check_data_refs(p, src, sources=False):
    errs = []
    srcmd = (C / "data" / "SOURCES.md").read_text(encoding="utf-8") if (C / "data" / "SOURCES.md").exists() else ""
    for f in sorted(set(DATA_RE.findall(src))):
        fp = C / "data" / f
        if not fp.exists():
            errs.append(f"{p.name}: data/{f} not found in content/data/")
            continue
        if sources and f not in srcmd:
            errs.append(f"{p.name}: data/{f} is not described in content/data/SOURCES.md")
        if len(gzip.compress(fp.read_bytes())) > 5e6:
            errs.append(f"{p.name}: data/{f} is over 5 MB gzipped")
    return errs


def check_quiz(p):
    errs = []
    if not re.fullmatch(r"L(0[1-9]|1[0-6])|V[1-6]", p.stem):
        errs.append(f"{p.name}: file name must be L01…L16 or V1…V6")
    d = json.loads(p.read_text(encoding="utf-8"))
    pos = collections.Counter()
    for sec, qs in d.items():
        if not isinstance(qs, list):
            continue
        for i, q in enumerate(qs):
            tag = f"{p.stem}.{sec}[{i}]"
            t = q.get("type", "single")
            for k in ("q", "explain"):
                if not q.get(k):
                    errs.append(f"{tag}: missing {k}")
            if q.get("level") not in (1, 2, 3):
                errs.append(f"{tag}: level must be 1/2/3")
            if q.get("see") and not see_ok(str(q["see"])):
                errs.append(f"{tag}: see {q['see']!r} is not a page of the site (topic.html or topic.section-id.html)")
            if t in ("single", "code"):
                o = q.get("options") or []
                if len(o) != 4 or len(set(o)) != 4 or not isinstance(q.get("answer"), int) or not 0 <= q["answer"] < 4:
                    errs.append(f"{tag}: single/code needs 4 distinct options and answer 0..3")
                else:
                    pos["ABCD"[q["answer"]]] += 1
            elif t == "multi":
                o, a = q.get("options") or [], q.get("answer")
                if not (4 <= len(o) <= 5 and isinstance(a, list) and 1 <= len(a) < len(o) and all(isinstance(x, int) and 0 <= x < len(o) for x in a)):
                    errs.append(f"{tag}: multi needs 4–5 options and a proper subset as answer")
            elif t == "tf":
                if not isinstance(q.get("answer"), bool):
                    errs.append(f"{tag}: tf answer must be true/false")
            elif t == "numeric":
                if not isinstance(q.get("answer"), (int, float)) or not isinstance(q.get("tol"), (int, float)):
                    errs.append(f"{tag}: numeric needs answer and tol")
            else:
                errs.append(f"{tag}: unknown type {t}")
            if t == "code" and q.get("code") and isinstance(q.get("answer"), int) and len(q.get("options") or []) == 4:
                r = run_py(q["code"], ROOT)
                got = r.stdout.strip()
                want = str(q["options"][q["answer"]]).strip()
                if r.returncode or got != want:
                    errs.append(f"{tag}: code output {got!r} != correct option {want!r} {r.stderr[-200:]}")
    if pos and len(pos) >= 1 and sum(pos.values()) >= 8 and max(pos.values()) > 0.45 * sum(pos.values()):
        errs.append(f"{p.stem}: answers unbalanced {dict(pos)}")
    return errs


def check_structure(p, cs):
    """Each '[markdown] task N: …' cell is followed by starter, solution and check cells."""
    errs, task = [], None
    seen = []
    for kind, title, _ in cs + [("markdown", "task end", "")]:
        if kind == "markdown" and re.match(r"task\s*\d+", title, re.I):
            if task is not None:
                miss = [k for k in ("starter", "solution", "check") if k not in seen]
                if miss:
                    errs.append(f"{p.name}: {task} has no {'/'.join(miss)} cell")
            task, seen = title, []
        elif kind != "markdown":
            seen.append(kind)
    if task is None:
        errs.append(f"{p.name}: no '# %% [markdown] task N: title' cells (format: content/FORMATS.md)")
    return errs


def check_ex(p, kinds=("setup", "solution", "check", "code")):
    src = p.read_text(encoding="utf-8")
    cs = cells(src)
    code = "\n".join(c for k, _, c in cs if k in kinds)
    errs = check_data_refs(p, src, sources="check" not in kinds)
    if "check" in kinds:
        errs += check_structure(p, cs)
    r = run_py(code, C)   # data files are read as "data/<file>" (same layout in JupyterLite)
    if r.returncode:
        errs.append(f"{p.name}: error\n{r.stderr[-1500:]}")
    n_check = sum(1 for k, _, _ in cs if k == "check")
    if "check" in kinds and r.stdout.count("✓") < n_check:
        errs.append(f"{p.name}: {r.stdout.count('✓')}/{n_check} checks printed ✓")
    if "check" in kinds and n_check == 0:
        errs.append(f"{p.name}: no check cells (format: content/FORMATS.md)")
    return errs


def main():
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    ids = set(sys.argv[2:])
    errs = []
    if what in ("all", "quizzes"):
        for p in sorted((C / "quizzes").glob("*.json")):
            if not ids or p.stem in ids:
                errs += check_quiz(p)
    if what in ("all", "exercises"):
        for p in sorted((C / "exercises").glob("L*.py")):
            if not ids or p.stem in ids:
                errs += check_ex(p)
    if what in ("all", "cases"):
        for p in sorted((C / "cases").glob("*.py")) if (C / "cases").exists() else []:
            if not ids or p.stem in ids:
                errs += check_ex(p, kinds=("code", "setup"))
    print("\n".join(errs) if errs else "ALL OK")
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
