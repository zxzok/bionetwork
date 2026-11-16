"""Synthesize episodes' narration on the Mac Studio (ssh host m5) and bring the lines back into the local cache.

    remote_synth.py [--meet LOCAL_LOG LOCAL_ORDER_FILE] ep_a ep_b ...

Runs the same IndexTTS helper there (~/indextts-helper/helper.py, install at ~/语音合成/index-tts), one process
per episode and speed group, then trims silence locally exactly as common.synth does, so the cached wavs
are identical in format. Lines already in the cache are skipped.

--meet: the local synth_ep.py run processes LOCAL_ORDER_FILE's modules in order and prints one
"[tts] N lines to synthesize" per module to LOCAL_LOG. Before each module this script stops if the local run
has already reached it, so the two machines work from opposite ends and never do an episode twice.
"""
import importlib
import json
import shlex
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import common  # noqa: E402

HOST = "m5"
RPY = "~/语音合成/index-tts/.venv/bin/python"
RHELPER = "~/indextts-helper/helper.py"
RWORK = "remote_tts"  # under the remote home


def local_reached():
    """Index (in the local order) of the module the local run is working on, or -1."""
    if not MEET:
        return -1
    log, order = MEET
    n = sum(1 for l in Path(log).read_text(encoding="utf-8", errors="ignore").splitlines()
            if l.startswith("[tts]") and "lines to synthesize" in l)
    return n - 1, order


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def synth_remote(m):
    lines = importlib.import_module(m).LINES.values()
    todo = {}
    for ln in lines:
        k = common.line_key(ln)
        if not (common.CACHE / f"{k}.wav").exists():
            todo.setdefault(common.speed_of(ln), {})[k] = common.tts_text(ln)
    print(f"[{time.strftime('%H:%M')}] {m}: {sum(len(v) for v in todo.values())} lines on {HOST}", flush=True)
    for speed, items in todo.items():
        keys = list(items)
        job = f"{RWORK}/{m}_{speed}"
        with tempfile.TemporaryDirectory() as td:
            script = Path(td) / "lines.txt"
            script.write_text("\n".join(items[k] for k in keys) + "\n", encoding="utf-8")
            run(["ssh", HOST, f"rm -rf {job} && mkdir -p {job}"])
            r = run(["scp", "-q", str(script), f"{HOST}:{job}/lines.txt"])
            if r.returncode:
                raise SystemExit(f"scp failed: {r.stderr}")
            cmd = (f"cd ~/语音合成/index-tts && PYTORCH_ENABLE_MPS_FALLBACK=1 TOKENIZERS_PARALLELISM=false "
                   f"{RPY} {RHELPER} batch --voice {shlex.quote(common.VOICE)} --script ~/{job}/lines.txt "
                   f"--outdir ~/{job}/out --speed-factor {speed}")
            r = run(["ssh", HOST, cmd])
            res = [l for l in r.stdout.splitlines() if l.startswith("@@INDEXTTS_RESULT@@")]
            if r.returncode or not res:
                print(r.stderr[-3000:], file=sys.stderr)
                raise SystemExit("remote TTS failed")
            clips = json.loads(res[-1].split(" ", 1)[1])["clips"]
            out = Path(td) / "out"
            r = run(["rsync", "-a", f"{HOST}:{job}/out/", str(out) + "/"])
            if r.returncode:
                raise SystemExit(f"rsync back failed: {r.stderr}")
            for k, c in zip(keys, clips):
                subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(out / Path(c["output"]).name), "-af",
                                "silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.05,"
                                "areverse,silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.08,areverse",
                                "-ar", str(common.SR), "-ac", "1", "-sample_fmt", "s16",
                                str(common.CACHE / f"{k}.wav")], check=True)
            run(["ssh", HOST, f"rm -rf {job}"])


MEET = None
args = sys.argv[1:]
if args[:1] == ["--meet"]:
    MEET = (args[1], Path(args[2]).read_text().split())
    args = args[3:]
for m in args:
    if MEET:
        i, order = local_reached()
        if m in order and order.index(m) <= i:
            print(f"[{time.strftime('%H:%M')}] local run has reached {m}; stopping here", flush=True)
            break
    synth_remote(m)
print("REMOTE_DONE", flush=True)
