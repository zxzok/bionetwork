"""(agentE variant: adds {"prox": "remove"|"near", "n": k} for the proximity demo canvas.)
Screen-record one of the site's own interactive demos (dist/), for use as a clip in an episode.

    record_demo.py <name> <page.html> '<actions json>'
      e.g. record_demo.py attack_demo robustness.targeted-attack.html \
           '[{"wait":1.5},{"select":0,"value":"er"},{"wait":2},{"slider":0,"to":3,"dur":4}]'

The demo on the page is lifted into a full-screen dark frame and scaled up; the recording is saved as
video/v2/media/<name>.mp4 (1920x1080, 30 fps). Actions:
  {"wait": s}
  {"slider": i, "to": v, "dur": s}      move the i-th range input smoothly to v over s seconds
  {"select": i, "value": v}             choose an option of the i-th <select>
  {"click": i}                          press the i-th button
"""
import json
import subprocess
import sys
import tempfile
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
DIST = HERE.parents[1] / "dist"
OUT = HERE / "media"

LIFT = """(scale) => {
  document.documentElement.dataset.theme = 'dark'; window.dispatchEvent(new Event('themechange'));
  const demo = document.querySelector('.demo');
  const wrap = document.createElement('div');
  wrap.style.cssText = 'position:fixed;inset:0;z-index:99999;background:#10151f;display:flex;align-items:center;justify-content:center;overflow:hidden';
  const inner = document.createElement('div');
  inner.style.cssText = `transform:scale(${scale});transform-origin:center center;width:560px;color:#e8ecf3;font-size:15px`;
  inner.appendChild(demo); wrap.appendChild(inner); document.body.appendChild(wrap);
  document.body.style.overflow = 'hidden';
}"""

BLOBS = """(arg) => {
  const cv = document.querySelector('.demo canvas'); const g = cv.getContext('2d'); const W = cv.width, H = cv.height;
  const d = g.getImageData(0, 0, W, H).data; const cs = getComputedStyle(document.documentElement);
  const hex = (h) => { h = h.trim().replace('#',''); if (h.length===3) h = h.split('').map(c=>c+c).join(''); return [0,2,4].map(i=>parseInt(h.substr(i,2),16)); };
  const tgt = hex(cs.getPropertyValue(arg.v)); const seen = new Uint8Array(W*H); const out = [];
  const ok = (i) => Math.abs(d[4*i]-tgt[0]) + Math.abs(d[4*i+1]-tgt[1]) + Math.abs(d[4*i+2]-tgt[2]) < 40 && d[4*i+3] > 200;
  for (let i = 0; i < W*H; i++) { if (seen[i] || !ok(i)) continue; const q=[i]; seen[i]=1; let sx=0, sy=0, n=0;
    for (let k=0;k<q.length;k++){ const p=q[k], x=p%W, y=(p/W)|0; sx+=x; sy+=y; n++;
      for (const [dx,dy] of [[1,0],[-1,0],[0,1],[0,-1]]) { const xx=x+dx, yy=y+dy; if (xx<0||yy<0||xx>=W||yy>=H) continue; const j=yy*W+xx; if(!seen[j]&&ok(j)){seen[j]=1;q.push(j);} } }
    if (n >= arg.min) out.push([sx/n, sy/n, n]); }
  const r = cv.getBoundingClientRect(); return out.map(([x,y,n]) => [r.left + x/W*r.width, r.top + y/H*r.height, n]);
}"""


def prox(pg, a):
    if a["prox"] == "remove":
        for x, y, _ in pg.evaluate(BLOBS, {"v": "--accent", "min": 25})[: a.get("n", 3)]:
            pg.mouse.click(x, y); pg.wait_for_timeout(int(a.get("gap", 0.8) * 1000))
    else:
        red = pg.evaluate(BLOBS, {"v": "--bad", "min": 25})
        cx = sum(p[0] for p in red) / len(red); cy = sum(p[1] for p in red) / len(red)
        grey = pg.evaluate(BLOBS, {"v": "--ink-2", "min": 6})
        far = a["prox"] == "far"
        grey.sort(key=lambda p: (p[0] - cx) ** 2 + (p[1] - cy) ** 2, reverse=far)
        done = 0
        for x, y, _ in grey:
            if not far and min((x - p[0]) ** 2 + (y - p[1]) ** 2 for p in red) < 15 ** 2:
                continue
            before = pg.locator(".demo .readout").inner_text()
            pg.mouse.click(x, y); pg.wait_for_timeout(150)
            if pg.locator(".demo .readout").inner_text() != before:
                done += 1; pg.wait_for_timeout(int(a.get("gap", 0.8) * 1000))
            if done >= a.get("n", 3):
                break


def main():
    name, page, actions = sys.argv[1], sys.argv[2], json.loads(sys.argv[3])
    OUT.mkdir(exist_ok=True)
    srv = ThreadingHTTPServer(("127.0.0.1", 0), partial(SimpleHTTPRequestHandler, directory=str(DIST)))
    srv.RequestHandlerClass.log_message = lambda *a: None
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{srv.server_port}/{page}"
    with tempfile.TemporaryDirectory() as td, sync_playwright() as p:
        b = p.chromium.launch(executable_path=str(Path.home() / "Library/Caches/ms-playwright/chromium_headless_shell-1248/chrome-headless-shell-mac-arm64/chrome-headless-shell"))
        ctx = b.new_context(viewport={"width": 1920, "height": 1080}, device_scale_factor=1,
                            record_video_dir=td, record_video_size={"width": 1920, "height": 1080})
        pg = ctx.new_page()
        pg.goto(url, wait_until="networkidle")
        pg.wait_for_selector(".demo canvas")
        # render the canvas at high resolution before scaling it up
        pg.evaluate(LIFT, 1.75)
        pg.wait_for_timeout(600)
        t_start = 0.0
        for a in actions:
            if "wait" in a:
                pg.wait_for_timeout(int(a["wait"] * 1000))
            elif "slider" in a:
                inp = pg.locator(".demo input[type=range]").nth(a["slider"])
                v0 = float(inp.input_value()); v1 = float(a["to"]); n = max(2, int(a.get("dur", 2) * 15))
                for k in range(1, n + 1):
                    v = v0 + (v1 - v0) * k / n
                    inp.evaluate("(e, v) => { e.value = v; e.dispatchEvent(new Event('input', {bubbles:true})); }", v)
                    pg.wait_for_timeout(int(a.get("dur", 2) * 1000 / n))
            elif "select" in a:
                pg.locator(".demo select").nth(a["select"]).select_option(a["value"])
            elif "prox" in a:
                prox(pg, a)
            elif "click" in a:
                pg.locator(".demo button").nth(a["click"]).click()
        pg.wait_for_timeout(400)
        vid = pg.video.path()
        ctx.close(); b.close()
        # drop the first moments (page load before the demo was lifted)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "1.2", "-i", vid, "-r", "30", "-c:v", "libx264", "-crf", "18",
                        "-pix_fmt", "yuv420p", "-an", str(OUT / f"{name}.mp4")], check=True)
    srv.shutdown()
    d = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(OUT / f"{name}.mp4")],
                       capture_output=True, text=True).stdout.strip()
    print(f"DEMO_OK media/{name}.mp4 {d}s")


if __name__ == "__main__":
    main()
