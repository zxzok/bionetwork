#!/usr/bin/env python3
"""Build the JupyterLite site (Pyodide kernel) into dist/lite from the notebooks build.py wrote.

    taskpolicy -b nice -n 15 .venv/bin/python tools/build_lite.py     # after build.py (or use build.py --lite)

Contents (same relative layout as the downloads, so data/<file> works unchanged):
  examples/<topic>.ipynb                    code examples of each topic
  practice/exercises-<topic>[-solution].ipynb, practice/case-<topic>.ipynb, practice/data/*
Pyodide itself loads from the jsDelivr CDN (the kernel's default); nothing of it is vendored.
Needs jupyterlite-core and jupyterlite-pyodide-kernel in .venv.
"""
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = Path(os.environ.get("BNS_DIST") or ROOT / "dist")
NB = DIST / "notebooks"
WORK = ROOT / "build" / "lite"
OUT = DIST / "lite"
JUPYTER = Path(sys.executable).with_name("jupyter")

CONFIG = {
    "LiteBuildConfig": {
        "apps": ["notebooks", "lab"],
        "no_sourcemaps": True,
        "no_unused_shared_packages": True,
    }
}
# jupyter-lite.json: simple notebook UI, no telemetry/news prompts
LITE = {
    "jupyter-lite-schema-version": 0,
    "jupyter-config-data": {
        "appName": "生物医学网络科学 · JupyterLite",
        "disabledExtensions": ["@jupyterlab/apputils-extension:announcements"],
    },
}


DATA_RE = re.compile(r"""["']data/([\w.\-]+)["']""")
# The kernel normally sees the notebook's folder through JupyterLite's service worker. Where service workers are
# unavailable (private windows, some embedded browsers) this cell copies the data files in over HTTP instead.
FETCH = """# 数据文件（JupyterLite 专用；文件已在时什么也不做）
import os, js
from pyodide.http import pyfetch
_base = str(js.location.href).split("/extensions/")[0].split("/build/")[0] + "/files/practice/data/"
os.makedirs("data", exist_ok=True)
for _f in {files!r}:
    if not os.path.exists("data/" + _f):
        _r = await pyfetch(_base + _f)
        open("data/" + _f, "wb").write(await _r.bytes())
"""


def lite_nb(src, dst):
    d = json.loads(src.read_text(encoding="utf-8"))
    d.setdefault("metadata", {})["kernelspec"] = {"name": "python", "display_name": "Python (Pyodide)", "language": "python"}
    files = sorted({f for c in d["cells"] if c["cell_type"] == "code" for f in DATA_RE.findall("".join(c["source"]))})
    if files:
        cell = {"cell_type": "code", "id": "lite-data", "execution_count": None, "outputs": [],
                "metadata": {"tags": ["lite-data"], "jupyter": {"source_hidden": True}}, "source": FETCH.format(files=files).splitlines(True)}
        d["cells"].insert(1, cell)
    dst.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")


def main():
    if not NB.exists():
        sys.exit("dist/notebooks missing: run build.py first")
    if WORK.exists():
        shutil.rmtree(WORK)
    files = WORK / "files"
    (files / "examples").mkdir(parents=True)
    (files / "practice").mkdir(parents=True)
    n = 0
    for p in sorted(NB.glob("*.ipynb")):
        sub = "practice" if p.name.startswith(("exercises-", "case-")) else "examples"
        lite_nb(p, files / sub / p.name)
        n += 1
    if (NB / "data").exists():
        shutil.copytree(NB / "data", files / "practice" / "data")
    (WORK / "jupyter_lite_config.json").write_text(json.dumps(CONFIG, indent=1), encoding="utf-8")
    (WORK / "jupyter-lite.json").write_text(json.dumps(LITE, ensure_ascii=False, indent=1), encoding="utf-8")
    if OUT.exists():
        shutil.rmtree(OUT)
    cmd = [str(JUPYTER), "lite", "build", "--lite-dir", str(WORK), "--contents", str(files), "--output-dir", str(OUT)]
    r = subprocess.run(cmd, cwd=WORK)
    if r.returncode:
        sys.exit(r.returncode)
    for junk in (".jupyterlite.doit.db",):
        for f in OUT.rglob(junk):
            f.unlink()
    size = sum(f.stat().st_size for f in OUT.rglob("*") if f.is_file())
    print(f"JupyterLite: {n} notebooks, {size / 1e6:.1f} MB in {OUT}")


if __name__ == "__main__":
    main()
