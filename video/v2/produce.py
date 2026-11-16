"""Produce finished episodes: voice synthesis (one model load), 1080p render, finishing, copy into dist.

    produce.py ep_spreading ep_watts1998_smallworld ...     (or: produce.py --all)
Writes dist/media/videos/<stem>.{mp4,vtt,txt,jpg,json}; topic episodes get stem T-<topic>, papers keep the paper id.
"""
import importlib
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from common import ROOT, synth  # noqa: E402

PY = ROOT / ".venv" / "bin"
MEDIA = Path(os.environ.get("V2_MEDIA", "/private/tmp/claude-501/-Users-xizhezhang-work-6--Teaching--------------/"
                            "c79803e2-a8e2-464d-8e1e-5ba25303a34a/scratchpad/manimhq"))
DIST = ROOT / "dist" / "media" / "videos"


def stem_of(mod):
    import yaml
    tid = mod[3:].replace("_", "-")
    topics = {t["id"] for t in yaml.safe_load((ROOT / "content/taxonomy.yaml").read_text(encoding="utf-8"))["topics"]}
    return f"T-{tid}" if tid in topics else mod[3:]


def main():
    mods = sorted(p.stem for p in HERE.glob("ep_*.py")) if "--all" in sys.argv else [a for a in sys.argv[1:] if not a.startswith("-")]
    lines = []
    for m in mods:
        lines += list(importlib.import_module(m).LINES.values())
    synth(lines)
    for m in mods:
        stem = stem_of(m)
        r = subprocess.run([str(PY / "manim"), "--resolution", "1920,1080", "--frame_rate", "30", "--media_dir", str(MEDIA / m),
                            f"{m}.py", "Episode"], cwd=HERE, capture_output=True, text=True)
        mp4 = next((MEDIA / m).rglob("Episode.mp4"), None)
        if r.returncode != 0 or mp4 is None:
            print(f"RENDER_FAIL {m}\n{r.stderr[-2000:]}", flush=True)
            continue
        out = HERE / "out" / stem
        f = subprocess.run([str(PY / "python"), "finish.py", str(mp4), str(HERE / "out" / f"{m}.cues.json"), str(out)],
                           cwd=HERE, capture_output=True, text=True)
        print(f.stdout.strip() or f"FINISH_FAIL {m} {f.stderr[-800:]}", flush=True)
        if f.returncode == 0:
            bad = subprocess.run(["ffmpeg", "-v", "error", "-i", f"{out}.mp4", "-f", "null", "-"], capture_output=True, text=True).stderr
            if bad.strip():
                print(f"DECODE_ERR {m}", flush=True)
                continue
            for ext in ("mp4", "vtt", "txt", "jpg"):
                (DIST / f"{stem}.{ext}").write_bytes(Path(f"{out}.{ext}").read_bytes())
            dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                        f"{out}.mp4"], capture_output=True, text=True).stdout)
            mod = importlib.import_module(m)
            (DIST / f"{stem}.json").write_text(json.dumps({"id": stem, "title": getattr(mod, "TITLE", stem),
                                                           "duration": round(dur, 1), "voice": "我的声音_讲解"},
                                                          ensure_ascii=False), encoding="utf-8")
            print(f"DELIVERED {stem}", flush=True)


if __name__ == "__main__":
    main()
