"""record_demo.py plus one extra action, for demos driven by clicks on the canvas (e.g. graph_matrix):
  {"canvas_click": i, "x": cx, "y": cy}   click the i-th canvas at (cx, cy) in the demo's own canvas units
  {"jsclick": i}                          press the i-th button from script (works when it is scaled off-screen)
Usage is otherwise identical to record_demo.py, with an optional 4th argument '{"width": 760, "scale": 1.5}'
so that two-canvas demos sit side by side and fit the 1080p frame.
"""
import json
import subprocess
import sys
import tempfile
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

from playwright.sync_api import sync_playwright

import record_demo as R


def main():
    name, page, actions = sys.argv[1], sys.argv[2], json.loads(sys.argv[3])
    opt = json.loads(sys.argv[4]) if len(sys.argv) > 4 else {}
    lift = R.LIFT.replace("width:560px", f"width:{opt.get('width', 560)}px")
    R.OUT.mkdir(exist_ok=True)
    srv = ThreadingHTTPServer(("127.0.0.1", 0), partial(SimpleHTTPRequestHandler, directory=str(R.DIST)))
    srv.RequestHandlerClass.log_message = lambda *a: None
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{srv.server_port}/{page}"
    with tempfile.TemporaryDirectory() as td, sync_playwright() as p:
        b = p.chromium.launch(executable_path=str(R.Path.home() / "Library/Caches/ms-playwright/chromium_headless_shell-1248/chrome-headless-shell-mac-arm64/chrome-headless-shell"))
        ctx = b.new_context(viewport={"width": 1920, "height": 1080}, device_scale_factor=1,
                            record_video_dir=td, record_video_size={"width": 1920, "height": 1080})
        pg = ctx.new_page()
        pg.goto(url, wait_until="networkidle")
        pg.wait_for_selector(".demo canvas")
        pg.evaluate(lift, opt.get('scale', 1.75))
        pg.wait_for_timeout(600)
        for a in actions:
            if "wait" in a:
                pg.wait_for_timeout(int(a["wait"] * 1000))
            elif "canvas_click" in a:
                box = pg.locator(".demo canvas").nth(a["canvas_click"]).evaluate(
                    "(c) => { const r = c.getBoundingClientRect(); return [r.left, r.top, r.width, r.height, c._w, c._h]; }")
                x0, y0, w, h, cw, ch = box
                pg.mouse.click(x0 + a["x"] / cw * w, y0 + a["y"] / ch * h)
            elif "slider" in a:
                inp = pg.locator(".demo input[type=range]").nth(a["slider"])
                v0 = float(inp.input_value()); v1 = float(a["to"]); n = max(2, int(a.get("dur", 2) * 15))
                for k in range(1, n + 1):
                    v = v0 + (v1 - v0) * k / n
                    inp.evaluate("(e, v) => { e.value = v; e.dispatchEvent(new Event('input', {bubbles:true})); }", v)
                    pg.wait_for_timeout(int(a.get("dur", 2) * 1000 / n))
            elif "select" in a:
                pg.locator(".demo select").nth(a["select"]).select_option(a["value"])
            elif "jsclick" in a:
                pg.locator(".demo button").nth(a["jsclick"]).evaluate("(e) => e.click()")
            elif "click" in a:
                pg.locator(".demo button").nth(a["click"]).click()
        pg.wait_for_timeout(400)
        vid = pg.video.path()
        ctx.close(); b.close()
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "1.2", "-i", vid, "-r", "30", "-c:v", "libx264", "-crf", "18",
                        "-pix_fmt", "yuv420p", "-an", str(R.OUT / f"{name}.mp4")], check=True)
    srv.shutdown()
    d = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(R.OUT / f"{name}.mp4")],
                       capture_output=True, text=True).stdout.strip()
    print(f"DEMO_OK media/{name}.mp4 {d}s")


if __name__ == "__main__":
    main()
