"""Download the approved YouTube excerpts (only the needed segment) into media/, recording each file's offset.

For each clip file referenced in clips_proposed.md: segment [start-5, start+40] s of the video (video only, <=720p).
media/offsets.json maps file -> {"offset": seconds of the original video at file t=0, "shift": manual correction}.
finish.py plays original time `start` from file time  start - offset + shift.
"""
import json
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
MEDIA = HERE / "media"
OFF = MEDIA / "offsets.json"


def proposals():
    rows = {}
    for line in (HERE / "clips_proposed.md").read_text(encoding="utf-8").splitlines():
        p = [x.strip() for x in line.split("|")]
        if len(p) >= 7 and p[0].startswith("yt_"):
            starts = [float(s) for s in p[5].replace(" ", "").split("/") if s]
            rows[p[0]] = (p[1], starts)
    return rows


def fetch(item):
    name, (vid, starts) = item
    out = MEDIA / name
    if out.exists():
        return name, None, "exists"
    a = max(0.0, min(starts) - 5)
    b = max(starts) + 40
    tmp = MEDIA / f"_dl_{name}"
    r = subprocess.run(["yt-dlp", "-q", "--no-playlist", "-f", "bv*[height<=720][ext=mp4]/bv*[height<=720]/bv*",
                        "--download-sections", f"*{a:.0f}-{b:.0f}", "--force-keyframes-at-cuts",
                        "-o", str(tmp) + ".%(ext)s", f"https://www.youtube.com/watch?v={vid}"], capture_output=True, text=True)
    got = next(iter(MEDIA.glob(f"_dl_{name}.*")), None)
    if r.returncode != 0 or got is None:
        return name, None, "FAIL " + (r.stderr.strip().splitlines() or ["?"])[-1][:160]
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(got), "-an", "-c:v", "libx264", "-crf", "20",
                    "-pix_fmt", "yuv420p", "-r", "30", str(out)], check=True)
    got.unlink()
    return name, a, "ok"


def main():
    offs = json.loads(OFF.read_text()) if OFF.exists() else {}
    todo = [(k, v) for k, v in proposals().items()]
    with ThreadPoolExecutor(4) as ex:
        for name, a, msg in ex.map(fetch, todo):
            if a is not None:
                offs[name] = {"offset": a, "shift": 0}
            print(f"{msg:6} {name}", flush=True)
    OFF.write_text(json.dumps(offs, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
