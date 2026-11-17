#!/usr/bin/env python3
"""Publish the lecture video series (课程视频) to the site.

    .venv/bin/python tools/lectures.py            # scan, encode new episodes, upload, write the manifest
    .venv/bin/python tools/lectures.py --no-upload

Source: ../课程视频/<series>/NN_<title>.mp4 (public edition only; 课堂版/ is never published),
with NN_<title>.vtt/.txt/.jpg beside it, 分集大纲.md (episode table) and 讲稿/epNN.md ("本集要点").
Each episode is re-encoded for streaming (720p H.264, faststart) into video/lectures_web/ and uploaded as an
asset of the GitHub release RELEASE_TAG; small files (captions, transcript, poster) go to site/lectures/ and are
served by the site itself. Episodes listed in the outline but not yet rendered appear as "制作中".
Writes content/lectures.json, which build.py turns into courses.html.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT.parent / "课程视频"
WEB = ROOT / "video" / "lectures_web"
SMALL = ROOT / "site" / "lectures"
MANIFEST = ROOT / "content" / "lectures.json"
REPO = "zxzok/bionetwork"
RELEASE_TAG = "lecture-videos"
URL = f"https://github.com/{REPO}/releases/download/{RELEASE_TAG}/"

SERIES = [
    {"n": 1, "dir": "绪论", "title": "绪论", "en": "Introduction",
     "dek": "什么是网络，生物医学为什么需要网络：从蚂蚁、神经元到疾病和药物，看见系统背后的连接。",
     "topics": ["network-basics"]},
    {"n": 2, "dir": "图论", "title": "图论基础", "en": "Graph theory",
     "dek": "从哥尼斯堡七桥出发，学会用图描述网络：邻接矩阵、路径与连通、度、距离与聚集。",
     "topics": ["network-basics", "network-metrics"]},
    {"n": 3, "dir": "网络模型", "title": "网络模型", "en": "Network models",
     "dek": "随机网络、小世界与无标度：用模型回答“真实网络的这些数字正常吗”。",
     "topics": ["network-metrics", "network-models", "robustness"]},
    {"n": 4, "dir": "社团发现", "title": "社团发现", "en": "Community detection",
     "dek": "弱关系、社团与模块度：从社会网络到蛋白质复合物和脑功能网络。",
     "topics": ["community-structure"]},
]


def outline(d):
    """Episode rows of 分集大纲.md: {ep: {title, ppt, content}}."""
    rows = {}
    f = SRC / d / "分集大纲.md"
    if not f.exists():
        return rows
    for line in f.read_text(encoding="utf-8").splitlines():
        p = [x.strip() for x in line.strip().strip("|").split("|")]
        if len(p) >= 3 and p[0].isdigit() and not re.match(r"^\d+:\d+$", p[1]):
            rows.setdefault(int(p[0]), {"title": p[1], "ppt": p[2], "content": p[3] if len(p) > 3 else ""})
    return rows


def keypoints(d, ep):
    f = SRC / d / "讲稿" / f"ep{ep:02d}.md"
    if not f.exists():
        return ""
    m = re.search(r"本集要点[：:]\s*(.+)", f.read_text(encoding="utf-8"))
    return m.group(1).strip() if m else ""


def duration(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                       capture_output=True, text=True)
    try:
        return round(float(r.stdout.strip()), 1)
    except ValueError:
        return None


def encode(src, out):
    if out.exists() and out.stat().st_mtime >= src.stat().st_mtime:
        return
    tmp = out.with_suffix(".part.mp4")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(src), "-vf", "scale=1280:-2", "-c:v", "libx264", "-preset", "medium",
                    "-crf", "25", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", str(tmp)], check=True)
    tmp.rename(out)


def poster(src, out):
    if out.exists() and out.stat().st_mtime >= src.stat().st_mtime:
        return
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(src), "-vf", "scale=640:-2", "-q:v", "4", str(out)], check=True)


def released():
    r = subprocess.run(["gh", "release", "view", RELEASE_TAG, "-R", REPO, "--json", "assets"], capture_output=True, text=True)
    if r.returncode:
        subprocess.run(["gh", "release", "create", RELEASE_TAG, "-R", REPO, "--title", "课程视频",
                        "--notes", "《生物医学网络科学》网站“课程视频”栏目的视频文件。"], check=True)
        return {}
    return {a["name"]: a["size"] for a in json.loads(r.stdout)["assets"]}


def main():
    upload = "--no-upload" not in sys.argv
    WEB.mkdir(parents=True, exist_ok=True)
    SMALL.mkdir(parents=True, exist_ok=True)
    have = released() if upload else {}
    old = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {}
    old_eps = {e["id"]: e for s in old.get("series", []) for e in s["episodes"]}
    series = []
    for s in SERIES:
        rows = outline(s["dir"])
        files = {int(m.group(1)): p for p in sorted((SRC / s["dir"]).glob("[0-9][0-9]_*.mp4"))
                 if (m := re.match(r"(\d\d)_", p.name)) and p.with_suffix(".vtt").exists()}
        eps = []
        for ep in sorted(set(rows) | set(files)):
            eid = f"L{s['n']}-{ep:02d}"
            row = rows.get(ep, {})
            src = files.get(ep)
            title = src.stem.split("_", 1)[1] if src else row.get("title", "")
            e = {"id": eid, "ep": ep, "title": title, "full_title": row.get("title", title), "ppt": row.get("ppt", ""),
                 "content": row.get("content", ""), "points": keypoints(s["dir"], ep), "ready": False}
            if src:
                web = WEB / f"{eid}.mp4"
                print(f"{eid} {title}: encoding", flush=True)
                encode(src, web)
                for ext in ("vtt", "txt"):
                    (SMALL / f"{eid}.{ext}").write_bytes(src.with_suffix(f".{ext}").read_bytes())
                poster(src.with_suffix(".jpg"), SMALL / f"{eid}.jpg")
                size = web.stat().st_size
                if upload and have.get(web.name) != size:
                    print(f"{eid}: uploading {size / 1e6:.0f} MB", flush=True)
                    subprocess.run(["gh", "release", "upload", RELEASE_TAG, str(web), "-R", REPO, "--clobber"], check=True)
                    have[web.name] = size
                if have.get(web.name) == size or (not upload and old_eps.get(eid, {}).get("ready")):
                    e.update(ready=True, duration=duration(web), size=size, src=URL + web.name)
            eps.append(e)
        series.append({k: s[k] for k in ("n", "title", "en", "dek", "topics")} | {"episodes": eps})
        print(f"第{s['n']}课 {s['title']}: {sum(e['ready'] for e in eps)}/{len(eps)} ready", flush=True)
    MANIFEST.write_text(json.dumps({"release": URL, "series": series}, ensure_ascii=False, indent=1), encoding="utf-8")
    print("wrote", MANIFEST.relative_to(ROOT))


if __name__ == "__main__":
    main()
