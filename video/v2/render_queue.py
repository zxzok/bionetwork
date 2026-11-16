"""Render episodes as soon as all their narration lines are synthesized (runs alongside synthesis).

    render_queue.py ep_a ep_b ...     (default: all ep_*.py)
"""
import importlib
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import common  # noqa: E402

mods = [a for a in sys.argv[1:]] or sorted(p.stem for p in HERE.glob("ep_*.py"))
pending = list(mods)
while pending:
    for m in list(pending):
        lines = importlib.import_module(m).LINES.values()
        if all((common.CACHE / f"{common.line_key(t)}.wav").exists() for t in lines):
            r = subprocess.run([sys.executable, "produce.py", m], cwd=HERE, capture_output=True, text=True)
            print(f"[{time.strftime('%H:%M')}] {m}: " + " | ".join(l for l in r.stdout.splitlines() if not l.startswith("[tts]"))
                  + (f" ERR {r.stderr[-400:]}" if r.returncode else ""), flush=True)
            pending.remove(m)
    time.sleep(60)
print("ALL_RENDERED", flush=True)
