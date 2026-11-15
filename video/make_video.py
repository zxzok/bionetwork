#!/usr/bin/env python3
"""Narrated explainer videos from content/scripts/LNN.json.

  make_video.py tts L03 L04 ...     synthesize all missing narration lines (one model load)
  make_video.py render L03          build dist/media/videos/L03-core.mp4 (+ .vtt, .jpg)
  make_video.py all L03 ...         tts then render

Narration uses the teacher's own cloned voice (VoxCPM2, voice '我的声音_讲解').
No on-frame AI label (removed at the teacher's request; the web pages state it).
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

sys.path.insert(0, str(Path(__file__).parent))
import visuals as V  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "video" / "tts_cache"
OUT = ROOT / "dist" / "media" / "videos"
VOICE = os.environ.get("COURSE_VOICE", "我的声音_讲解")
VOX_PY = Path.home() / "语音合成/VoxCPM/.venv/bin/python"
VOX_HELPER = Path.home() / ".claude/skills/voxcpm-tts/helper.py"
SR = 48000
FPS = 15
W, H = 1280, 720
GAP_LINE, GAP_SCENE, LEAD, TAIL = 0.32, 0.75, 0.6, 1.4
COURSE = "生物医学网络科学"
AI_LABEL = "旁白：教师本人音色 · AI 语音合成"

plt.rcParams.update({
    "font.sans-serif": ["PingFang SC", "Hiragino Sans GB", "Heiti SC", "DejaVu Sans"],
    "font.family": "sans-serif",
    "axes.unicode_minus": False,
    "mathtext.fontset": "stix",
})


def tts_text(s):
    s = s.strip()
    s = s.replace("Barabási", "巴拉巴西").replace("Erdős", "埃尔德什").replace("Rényi", "雷尼")
    s = s.replace("–", "-").replace("—", "，")
    return s


def line_key(text):
    return hashlib.sha1(f"{VOICE}|{tts_text(text)}".encode()).hexdigest()[:16]


def load_script(lid):
    return json.loads((ROOT / "content/scripts" / f"{lid}.json").read_text(encoding="utf-8"))


def topic_title(lid):
    """New site: videos are labelled by knowledge topic, not lecture number."""
    import yaml
    tax = yaml.safe_load((ROOT / "content" / "taxonomy.yaml").read_text(encoding="utf-8"))
    for t in tax["topics"]:
        if t.get("legacy") == lid:
            return t["title"]
    return ""


def lecture_title(lid):
    p = ROOT / "content/lectures" / f"{lid}.md"
    if p.exists():
        m = re.search(r"^title:\s*(.+)$", p.read_text(encoding="utf-8"), re.M)
        if m:
            return m.group(1).strip().strip('"')
    return ""


# ----------------------------------------------------------------------------- TTS
def synthesize(lids):
    CACHE.mkdir(parents=True, exist_ok=True)
    todo = []
    for lid in lids:
        for sc in load_script(lid)["scenes"]:
            for ln in sc["lines"]:
                k = line_key(ln)
                if not (CACHE / f"{k}.wav").exists() and k not in [x[0] for x in todo]:
                    todo.append((k, tts_text(ln)))
    print(f"[tts] {len(todo)} lines to synthesize", flush=True)
    if not todo:
        return
    if VOICE == "fake":  # test mode: silent clips of plausible length
        for k, t in todo:
            n = int(SR * len(t) / 4.5)
            with wave.open(str(CACHE / f"{k}.wav"), "wb") as w:
                w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
                w.writeframes(np.zeros(n, np.int16).tobytes())
        return
    with tempfile.TemporaryDirectory() as td:
        script = Path(td) / "lines.txt"
        script.write_text("\n".join(t for _, t in todo) + "\n", encoding="utf-8")
        outdir = Path(td) / "out"
        env = dict(os.environ, PYTORCH_ENABLE_MPS_FALLBACK="1", TOKENIZERS_PARALLELISM="false")
        r = subprocess.run([str(VOX_PY), str(VOX_HELPER), "batch", "--voice", VOICE, "--script", str(script),
                            "--outdir", str(outdir)], env=env, capture_output=True, text=True)
        res = [l for l in r.stdout.splitlines() if l.startswith("@@VOXCPM_RESULT@@")]
        if r.returncode != 0 or not res:
            print(r.stderr[-3000:], file=sys.stderr)
            raise SystemExit("TTS failed")
        clips = json.loads(res[-1].split(" ", 1)[1])["clips"]
        for (k, _), c in zip(todo, clips):
            # normalise to 48 kHz mono s16 and trim leading/trailing silence
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", c["output"], "-af",
                            "silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.05,"
                            "areverse,silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.08,areverse",
                            "-ar", str(SR), "-ac", "1", "-sample_fmt", "s16", str(CACHE / f"{k}.wav")], check=True)
    print("[tts] done", flush=True)


def read_wav(p):
    with wave.open(str(p)) as w:
        return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768


# ----------------------------------------------------------------------------- timeline
def build_timeline(script):
    t = LEAD
    scenes, audio, cues = [], [], []
    for sc in script["scenes"]:
        start = t
        starts = []
        for i, ln in enumerate(sc["lines"]):
            a = read_wav(CACHE / f"{line_key(ln)}.wav")
            starts.append(t - start)
            audio.append((t, a))
            dur = len(a) / SR
            cues.append((t, t + dur, ln))
            t += dur + (GAP_LINE if i < len(sc["lines"]) - 1 else 0)
        t += GAP_SCENE
        scenes.append({"start": start, "end": t, "spec": sc, "cues": starts})
    total = t + TAIL - GAP_SCENE
    scenes[-1]["end"] = total
    buf = np.zeros(int(total * SR) + SR)
    for t0, a in audio:
        i = int(t0 * SR)
        buf[i:i + len(a)] += a
    return scenes, buf[: int(total * SR)], cues, total


def split_cue(a, b, text, maxlen=24):
    if len(text) <= maxlen:
        return [(a, b, text)]
    parts = [p for p in re.split(r"(?<=[，、；：,;:])", text) if p]
    out, cur = [], ""
    for p in parts:
        if len(cur) + len(p) > maxlen and cur:
            out.append(cur); cur = p
        else:
            cur += p
    if cur:
        out.append(cur)
    if len(out) == 1:
        h = len(text) // 2
        out = [text[:h], text[h:]]
    total = sum(len(x) for x in out)
    res, t = [], a
    for x in out:
        d = (b - a) * len(x) / total
        res.append((t, t + d, x)); t += d
    return res


def vtt_time(s):
    h, rem = divmod(s, 3600)
    m, sec = divmod(rem, 60)
    return f"{int(h):02d}:{int(m):02d}:{sec:06.3f}"


# ----------------------------------------------------------------------------- render
def chrome(fig, header_left, sub, frac):
    fig.patch.set_facecolor(V.BG)
    top = fig.add_axes([0, 0.9, 1, 0.1]); V.clean(top); top.set_xlim(0, 1); top.set_ylim(0, 1)
    top.add_patch(Rectangle((0, 0.93), frac, 0.07, color=V.BLUE))
    top.text(0.03, 0.45, header_left, fontsize=17, color=V.INK, va="center", fontweight="bold")
    top.text(0.97, 0.45, COURSE, fontsize=14, color=V.MUTED, va="center", ha="right")
    top.plot([0.03, 0.97], [0.02, 0.02], color=V.FAINT, lw=1)
    bot = fig.add_axes([0, 0, 1, 0.13]); V.clean(bot); bot.set_xlim(0, 1); bot.set_ylim(0, 1)
    if sub:
        wpx = min(0.9, 0.032 * len(sub) + 0.06)
        bot.add_patch(FancyBboxPatch((0.5 - wpx / 2, 0.2), wpx, 0.6, boxstyle="round,pad=0.01,rounding_size=0.05",
                                     fc=(0.12, 0.16, 0.27, 0.86), ec="none"))
        bot.text(0.5, 0.5, sub, fontsize=23, color="white", ha="center", va="center")
    return fig.add_axes([0.03, 0.14, 0.94, 0.75])


def render(lid):
    script = load_script(lid)
    if not re.fullmatch(r"L\d\d(-\d+)?", lid):  # paper explainer, e.g. zhang2016_inputgraph
        name = lid
        header = f"论文精读 · {script.get('title', lid)}"
    else:
        title = topic_title(lid[:3])
        name = f"{lid}-core" if len(lid) == 3 else lid
        header = title or script.get("title", lid)
        if len(lid) > 3:
            header = f"{title} · {script.get('title', '')}" if title else script.get("title", "")
    scenes, audio, cues, total = build_timeline(script)
    subcues = [c for a, b, txt in cues for c in split_cue(a, b, txt)]
    OUT.mkdir(parents=True, exist_ok=True)
    vis = []
    for s in scenes:
        cls = V.REGISTRY.get(s["spec"]["visual"], V.Bullets)
        vis.append(cls(s["spec"].get("params", {}) or {}, s["end"] - s["start"], s["cues"]))
    with tempfile.TemporaryDirectory() as td:
        wav = Path(td) / "a.wav"
        with wave.open(str(wav), "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
            w.writeframes((np.clip(audio, -1, 1) * 32767).astype(np.int16).tobytes())
        mp4 = OUT / f"{name}.mp4"
        ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba",
                               "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", str(wav),
                               "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-c:v", "libx264", "-preset", "medium",
                               "-crf", "23", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
                               "-movflags", "+faststart", "-shortest", str(mp4)], stdin=subprocess.PIPE)
        fig = plt.figure(figsize=(W / 100, H / 100), dpi=100)
        nframes = int(total * FPS)
        prev_key, prev_buf = None, None
        si, ci = 0, 0
        for f in range(nframes):
            t = f / FPS
            while si < len(scenes) - 1 and t >= scenes[si]["end"]:
                si += 1
            sub = ""
            for a, b, txt in subcues:
                if a <= t < b + 0.15:
                    sub = txt; break
            v = vis[si]
            lt = t - scenes[si]["start"]
            vk = v.key(lt) if hasattr(v, "key") else f
            key = (si, vk, sub, int(t / total * 200))
            if key != prev_key:
                fig.clf()
                ax = chrome(fig, header, sub, t / total)
                v.draw(ax, lt)
                fig.canvas.draw()
                prev_buf = bytes(fig.canvas.buffer_rgba())
                prev_key = key
                if f == int(2.5 * FPS):
                    fig.savefig(OUT / f"{name}.jpg", dpi=50, facecolor=V.BG)
            ff.stdin.write(prev_buf)
            if f % (FPS * 30) == 0:
                print(f"[{lid}] {t:6.1f}/{total:.1f}s", flush=True)
        ff.stdin.close()
        ff.wait()
        plt.close(fig)
    vtt = ["WEBVTT", ""]
    for i, (a, b, txt) in enumerate(subcues, 1):
        vtt += [str(i), f"{vtt_time(a)} --> {vtt_time(b)}", txt, ""]
    (OUT / f"{name}.vtt").write_text("\n".join(vtt), encoding="utf-8")
    transcript = "\n\n".join("".join(sc["lines"]) for sc in script["scenes"])
    (OUT / f"{name}.txt").write_text(transcript, encoding="utf-8")
    meta = {"id": script.get("id", f"{lid}-core"), "title": script.get("title", ""), "duration": round(total, 1),
            "voice": VOICE, "ai_voice": True}
    (OUT / f"{name}.json").write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
    print(f"VIDEO_OK {mp4} {total:.1f}s", flush=True)


if __name__ == "__main__":
    cmd, lids = sys.argv[1], sys.argv[2:]
    if cmd in ("tts", "all"):
        synthesize(lids)
    if cmd in ("render", "all"):
        for lid in lids:
            render(lid)
