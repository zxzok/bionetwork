"""Finish a rendered episode: composite video clips, loudness to -16 LUFS, H.264/AAC faststart, .vtt, poster.

    finish.py <manim mp4> <cues.json> <out stem>
"""
import json
import subprocess
import sys
from pathlib import Path

from common import FH, FW, MEDIA_DIR, write_vtt

src, cues_p, stem = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
stem.parent.mkdir(parents=True, exist_ok=True)
data = json.loads(cues_p.read_text(encoding="utf-8"))
if isinstance(data, list):  # old format: cues only
    data = {"cues": data, "clips": []}
cues, clips = data["cues"], data["clips"]

W, H = map(int, subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                                "-of", "csv=p=0:s=x", str(src)], capture_output=True, text=True).stdout.strip().split("x"))
px = lambda x: (x + FW / 2) * W / FW
py = lambda y: (FH / 2 - y) * H / FH

OFFS = json.loads((MEDIA_DIR / "offsets.json").read_text()) if (MEDIA_DIR / "offsets.json").exists() else {}
inputs = ["-i", str(src)]
filt, vlast, alast = [], "[0:v]", "[0:a]"
amix = []
for i, c in enumerate(clips, 1):
    x0, x1, y0, y1 = c["box"]
    bw, bh = int(round(px(x1) - px(x0))) // 2 * 2, int(round(py(y0) - py(y1))) // 2 * 2
    bx, by = int(round(px(x0))), int(round(py(y1)))
    dur = c["t1"] - c["t0"]
    o = OFFS.get(c["file"], {"offset": 0, "shift": 0})
    st = max(0.0, c["start"] - o["offset"] + o.get("shift", 0))
    inputs += ["-ss", f'{st:.3f}', "-t", f"{dur:.3f}", "-i", str(MEDIA_DIR / c["file"])]
    # fit inside the box (letterbox on black), hold the last frame if the clip is shorter than the span
    filt.append(f"[{i}:v]scale={bw}:{bh}:force_original_aspect_ratio=decrease,pad={bw}:{bh}:(ow-iw)/2:(oh-ih)/2:color=black,"
                f"fps=30,tpad=stop_mode=clone:stop_duration={dur:.3f},trim=duration={dur:.3f},"
                f"setpts=PTS-STARTPTS+{c['t0']:.3f}/TB[c{i}]")
    filt.append(f"{vlast}[c{i}]overlay={bx}:{by}:eof_action=pass:enable='between(t,{c['t0']:.3f},{c['t1']:.3f})'[v{i}]")
    vlast = f"[v{i}]"
    if c.get("audio"):
        ms = int(c["t0"] * 1000)
        filt.append(f"[{i}:a]atrim=duration={dur:.3f},asetpts=PTS-STARTPTS,adelay={ms}|{ms}[a{i}]")
        amix.append(f"[a{i}]")
if amix:
    filt.append(f"{alast}{''.join(amix)}amix=inputs={1 + len(amix)}:normalize=0[am]")
    alast = "[am]"
filt.append(f"{alast}loudnorm=I=-16:TP=-1.5:LRA=11[aout]")
cmd = ["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(filt),
       "-map", vlast if clips else "0:v", "-map", "[aout]",
       "-c:v", "libx264", "-crf", "21", "-preset", "medium", "-pix_fmt", "yuv420p",
       "-c:a", "aac", "-b:a", "128k", "-ar", "48000", "-movflags", "+faststart", f"{stem}.mp4"]
subprocess.run(cmd, check=True)
write_vtt([x[0] for x in cues], [x[1] for x in cues], [x[2] for x in cues], f"{stem}.vtt")
Path(f"{stem}.txt").write_text("\n".join(x[0] for x in cues) + "\n", encoding="utf-8")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "9", "-i", f"{stem}.mp4", "-frames:v", "1", "-q:v", "3",
                "-vf", "scale=1280:-1", f"{stem}.jpg"], check=True)
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f"{stem}.mp4"],
                           capture_output=True, text=True).stdout)
print(f"VIDEO_OK {stem}.mp4 {dur:.0f}s")
