"""Shared pieces for the explainer videos (manim animation + slides + images + video clips).

Each episode is a module video/v2/ep_<id>.py that defines TITLE, LINES (ordered narration, keyed by name)
and a Scene class `Episode(Narrated)`.

Narration: the teacher's cloned voice through IndexTTS-2.5 with the lecture-style emotion
("老师在课堂上耐心又带点兴奋地讲解…", strength 0.6). A line that starts with 【慢】 is a key point and is
spoken about 1.1x slower. Lines are cached in video/tts_idx by text + settings.
`with self.say("key"):` starts the line, runs the block's animations and pads the block to the line's length.

Media (files in video/v2/media/):
  self.image("x.jpg", box, credit)         still image (returns the mobject; animate it in yourself)
  self.clip_on("x.mp4", box, credit, start) / self.clip_off()
                                           a video clip composited by finish.py over that time span
                                           (the scene shows a dark frame + credit there; clip audio muted
                                           unless audio=True, in which case keep narration silent)
  slide(title, points)                     a clean text slide: title bar + points (animate points in one by one)
"""
import contextlib
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
from manim import *  # noqa: F401,F403
import nxcache  # noqa: F401,E402  (identical networkx layouts on macOS and Linux render workers)

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
MEDIA_DIR = HERE / "media"
CACHE = ROOT / "video" / "tts_idx"
VOICE = os.environ.get("COURSE_VOICE", "我的声音_讲解")
IDX_PY = Path.home() / "语音合成/index-tts/.venv/bin/python"
IDX_HELPER = Path.home() / ".claude/skills/indextts-tts/helper.py"
BASE = 1.0  # duration factor for ordinary lines (natural pace)
SLOW = 1.1  # duration factor for 【慢】 key-point lines
SR = 48000

# Open fonts (SIL OFL) shipped in v2/fonts and registered here, so every render machine (macOS or Linux) draws the
# same glyphs without installing anything: 思源黑体 for text, Source Code Pro for code. (Until 2026-11-17: PingFang SC
# and Menlo, Apple system fonts that may not be used on non-Apple machines.)
def _register_fonts():
    try:
        import manimpango
        for p in sorted((HERE / "fonts").glob("*.otf")):
            manimpango.register_font(str(p))
    except Exception as e:  # noqa: BLE001
        print("font registration failed:", e)


_register_fonts()
FONT = "Source Han Sans SC"
MONO = "Source Code Pro"
BG = "#10151f"
PANEL = "#18202e"
INK = "#e8ecf3"
MUTED = "#8b96a8"
BLUE = "#5b9cff"
RED = "#ff5c6c"
GOLD = "#ffc24b"
GREEN = "#4fd18b"
VIOLET = "#b48cff"
GAP = 0.75  # pause after each spoken line
GAP_KEY = 1.4  # pause after a key-point line


def T(s, size=30, color=INK, weight=NORMAL, **kw):
    return Text(s, font=FONT, font_size=size, color=color, weight=weight, **kw)


def wav_len(p):
    with wave.open(str(p)) as w:
        return w.getnframes() / w.getframerate()


# ----------------------------------------------------------------------------- narration text
MARK = re.compile(r"^【慢】")


def clean(text):
    """Text as shown in captions: markers removed."""
    return MARK.sub("", text).strip()


def speed_of(text):
    return SLOW if MARK.match(text) else BASE


def tts_text(text):
    s = clean(text)
    for a, b in (("Barabási", "巴拉巴西"), ("Erdős", "埃尔德什"), ("Rényi", "雷尼"), ("–", "-")):
        s = s.replace(a, b)
    return s


def line_key(text):
    return hashlib.sha1(f"IDX|{VOICE}|lecture0.6|{speed_of(text)}|{tts_text(text)}".encode()).hexdigest()[:16]


def synth(lines):
    """Synthesize missing lines with IndexTTS (one model load per speed group)."""
    CACHE.mkdir(parents=True, exist_ok=True)
    todo = {}
    for ln in lines:
        k = line_key(ln)
        if not (CACHE / f"{k}.wav").exists():
            todo.setdefault(speed_of(ln), {})[k] = tts_text(ln)
    print(f"[tts] {sum(len(v) for v in todo.values())} lines to synthesize", flush=True)
    for speed, items in todo.items():
        if VOICE == "fake":  # test mode: silent clips of plausible length
            for k, t in items.items():
                n = int(SR * speed * (len(t) / 4.2 + 0.3))
                with wave.open(str(CACHE / f"{k}.wav"), "wb") as w:
                    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
                    w.writeframes(np.zeros(n, np.int16).tobytes())
            continue
        with tempfile.TemporaryDirectory() as td:
            script = Path(td) / "lines.txt"
            keys = list(items)
            script.write_text("\n".join(items[k] for k in keys) + "\n", encoding="utf-8")
            env = dict(os.environ, PYTORCH_ENABLE_MPS_FALLBACK="1", TOKENIZERS_PARALLELISM="false")
            r = subprocess.run([str(IDX_PY), str(IDX_HELPER), "batch", "--voice", VOICE, "--script", str(script),
                                "--outdir", str(Path(td) / "out"), "--speed-factor", str(speed)],
                               env=env, capture_output=True, text=True, cwd=str(IDX_PY.parents[2]))
            res = [l for l in r.stdout.splitlines() if l.startswith("@@INDEXTTS_RESULT@@")]
            if r.returncode != 0 or not res:
                print(r.stderr[-3000:], file=sys.stderr)
                raise SystemExit("TTS failed")
            clips = json.loads(res[-1].split(" ", 1)[1])["clips"]
            for k, c in zip(keys, clips):
                subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", c["output"], "-af",
                                "silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.05,"
                                "areverse,silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.08,areverse",
                                "-ar", str(SR), "-ac", "1", "-sample_fmt", "s16", str(CACHE / f"{k}.wav")], check=True)
    print("[tts] done", flush=True)


# ----------------------------------------------------------------------------- media geometry
FW, FH = 14.222222, 8.0  # manim frame in scene units (16:9)
BOX = {
    "full": (-FW / 2, FW / 2, -FH / 2, FH / 2),
    "center": (-5.6, 5.6, -3.15, 3.15),
    "left": (-6.8, -0.3, -2.0, 2.4),
    "right": (0.3, 6.8, -2.0, 2.4),
}


def box_rect(box):
    x0, x1, y0, y1 = BOX[box] if isinstance(box, str) else box
    return x0, x1, y0, y1


def slide(title, points=(), size=34, accent=BLUE):
    """A clean text slide. Returns (head, items); add head, then FadeIn items one by one."""
    bar = Rectangle(width=0.12, height=0.7, fill_color=accent, fill_opacity=1, stroke_width=0)
    t = T(title, 44, INK, weight=BOLD)
    head = VGroup(bar, t).arrange(RIGHT, buff=0.3).to_corner(UL, buff=0.7)
    items = VGroup()
    for p in points:
        dot = Dot(radius=0.07, color=accent)
        items.add(VGroup(dot, T(p, size, INK)).arrange(RIGHT, buff=0.3))
    if len(items):
        items.arrange(DOWN, aligned_edge=LEFT, buff=0.45).next_to(head, DOWN, buff=0.8, aligned_edge=LEFT).shift(RIGHT * 0.4)
    return head, items


class Narrated(Scene):
    LINES: dict = {}

    def setup(self):
        self.camera.background_color = BG
        self.cues, self.clips = [], []

    def clip(self, key):
        p = CACHE / f"{line_key(self.LINES[key])}.wav"
        return p, wav_len(p)

    @contextlib.contextmanager
    def say(self, key, gap=None):
        """Start the narration line, run the block's animations, then wait out the rest of the line.
        The pause after the line is GAP, or GAP_KEY after a 【慢】 key point (time to let it sink in)."""
        if gap is None:
            gap = GAP_KEY if MARK.match(self.LINES[key]) else GAP
        p, d = self.clip(key)
        t0 = self.renderer.time
        self.cues.append((clean(self.LINES[key]), t0, d))
        self.add_sound(str(p))
        yield d
        rest = t0 + d + gap - self.renderer.time
        if rest > 0.02:
            self.wait(rest)

    # ------------------------------------------------------------------ media
    def image(self, name, box="center", credit=None):
        """An image fitted into box (not added). Credit, if given, is attached under it."""
        x0, x1, y0, y1 = box_rect(box)
        im = ImageMobject(str(MEDIA_DIR / name))
        im.scale(min((x1 - x0) / im.width, (y1 - y0) / im.height)).move_to([(x0 + x1) / 2, (y0 + y1) / 2, 0])
        if credit:
            c = T(credit, 16, MUTED).next_to(im, DOWN, buff=0.08).align_to(im, RIGHT)
            return Group(im, c)
        return im

    def clip_on(self, name, box="center", credit=None, start=0.0, audio=False):
        """Begin a video clip (composited later by finish.py) in box; returns the placeholder group."""
        x0, x1, y0, y1 = box_rect(box)
        frame = Rectangle(width=x1 - x0, height=y1 - y0, fill_color="#000000", fill_opacity=1, stroke_width=0
                          ).move_to([(x0 + x1) / 2, (y0 + y1) / 2, 0])
        g = VGroup(frame)
        if credit:
            g.add(T(credit, 16, MUTED).next_to(frame, DOWN, buff=0.08).align_to(frame, RIGHT))
            if box == "full":
                g[-1].move_to(frame.get_corner(DR) + LEFT * 1.6 + UP * 0.25)
        self.add(g)
        self._clip = dict(file=name, t0=self.renderer.time, start=start, box=[x0, x1, y0, y1], audio=audio, g=g)
        return g

    def clip_off(self, fade=0.0):
        c = self._clip
        c["t1"] = self.renderer.time
        self.remove(c.pop("g"))
        self.clips.append(c)
        self._clip = None

    def tear_down(self):
        import inspect
        out = HERE / "out" / f"{Path(inspect.getfile(type(self))).stem}.cues.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps({"cues": self.cues, "clips": self.clips}, ensure_ascii=False), encoding="utf-8")

    def chapter(self, s):
        """Small chapter tag in the corner."""
        return T(s, 22, MUTED).to_corner(UL, buff=0.45)


def write_vtt(lines, starts, durs, path):
    def ts(x):
        h, r = divmod(x, 3600); m, s = divmod(r, 60)
        return f"{int(h):02d}:{int(m):02d}:{s:06.3f}"
    out = ["WEBVTT", ""]
    for i, (ln, a, d) in enumerate(zip(lines, starts, durs), 1):
        out += [str(i), f"{ts(a)} --> {ts(a + d)}", ln, ""]
    Path(path).write_text("\n".join(out), encoding="utf-8")
