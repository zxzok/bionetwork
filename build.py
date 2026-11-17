#!/usr/bin/env python3
"""Build 生物医学网络科学 (Biomedical Network Science) into dist/.

    .venv/bin/python build.py

Content sources
  content/taxonomy.yaml      domains, topics, video mapping
  content/topics/<id>.md     topic home + knowledge pages (one per ## section)
  content/code/<id>.py       runnable code examples
  content/papers/*.md        paper explainers
  content/resources.yaml     data & software library
Old lecture URLs (L01.html ...) are kept as redirects to the new topic pages.
"""
import html
import json
import re
import shutil
import subprocess
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
DIST = ROOT / "dist"
SITE = "生物医学网络科学"
SITE_EN = "Biomedical Network Science"

TAX = yaml.safe_load((CONTENT / "taxonomy.yaml").read_text(encoding="utf-8"))
DOMAINS = TAX["domains"]
DOM = {d["id"]: d for d in DOMAINS}
TOPICS_META = TAX["topics"]
TOPIC_IDS = [t["id"] for t in TOPICS_META]
TMETA = {t["id"]: t for t in TOPICS_META}
LEGACY = {t["legacy"]: t["id"] for t in TOPICS_META if t.get("legacy")}
VIDEOS = TAX.get("videos", {})
TOPIC_ONLY = {"overview", "related", "references", "resources", "questions"}
TOPIC_ONLY_TITLES = {"概述", "关联知识", "核心文献", "延伸资源", "开放问题"}

DEMO_INFO = {  # demo id -> (topic, title)
    "graph_matrix": ("network-basics", "图与邻接矩阵"), "er": ("network-metrics", "ER 随机图与巨连通分支"),
    "ws": ("network-models", "Watts–Strogatz 重连"), "ba": ("network-models", "BA 优先连接"),
    "modularity": ("community-structure", "模块度与社团划分"), "sir": ("spreading", "网络上的 SIR 传播与免疫"),
    "kuramoto": ("synchronization", "Kuramoto 同步"), "matching": ("controllability", "最大匹配、驱动节点与 Kalman 秩检验"),
    "attack": ("robustness", "随机失效与蓄意攻击"), "brain_threshold": ("brain-connectome", "脑网络阈值敏感性"),
    "dfc": ("dynamic-brain-networks", "滑动窗口动态功能连接"), "symptom": ("symptom-networks", "相关与偏相关症状网络"),
    "ffl": ("molecular-networks", "前馈环的滤波作用"), "proximity": ("network-medicine", "网络邻近度与疾病模块"),
}

LOGO = ('<svg width="26" height="26" viewBox="0 0 26 26" aria-hidden="true"><g stroke="currentColor" stroke-width="1.6" opacity=".55">'
        '<line x1="6" y1="7" x2="18" y2="5"/><line x1="6" y1="7" x2="13" y2="19"/><line x1="18" y1="5" x2="13" y2="19"/><line x1="18" y1="5" x2="22" y2="15"/>'
        '<line x1="13" y1="19" x2="22" y2="15"/></g><circle cx="6" cy="7" r="3" fill="#3047c2"/><circle cx="18" cy="5" r="2.4" fill="#3047c2"/>'
        '<circle cx="13" cy="19" r="4" fill="#d9661f"/><circle cx="22" cy="15" r="2.2" fill="#3047c2"/></svg>')
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Noto+Serif+SC:wght@600;700&display=swap">')
E = html.escape


# ----------------------------------------------------------------------------- markdown helpers
def pandoc(md, mathml=True):
    args = ["pandoc", "-f", "markdown+fenced_divs+pipe_tables+tex_math_dollars+header_attributes-implicit_figures", "-t", "html5"]
    if mathml:
        args.append("--mathml")
    r = subprocess.run(args, input=md, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(r.stderr)
    out = r.stdout
    out = re.sub(r"<table>", '<div class="table-wrap"><table>', out).replace("</table>", "</table></div>")
    out = re.sub(r'<a href="(https?://[^"]+)"', r'<a href="\1" target="_blank" rel="noopener"', out)
    return out


def front(path):
    txt = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", txt, re.S)
    return (yaml.safe_load(m.group(1)) or {}, m.group(2)) if m else ({}, txt)


def ttitle(tid):
    return TMETA[tid]["title"] if tid in TMETA else tid


def delecture(md):
    """Safety net: turn any leftover lecture references into topic references."""
    def link(m):
        lid = f"L{int(m.group(1)):02d}"
        tid = LEGACY.get(lid)
        return f"[{ttitle(tid)}]({tid}.html)" if tid else m.group(0)
    md = re.sub(r"\[第\s*(\d+)\s*讲[^\]]*\]\(L\d\d\.html[^)]*\)", link, md)
    md = re.sub(r"\]\(L(\d\d)\.html(#[^)]*)?\)", lambda m: f"]({LEGACY.get('L' + m.group(1), 'index')}.html)", md)

    def plain(m):
        tid = LEGACY.get(f"L{int(m.group(1)):02d}")
        return f"“{ttitle(tid)}”" if tid else m.group(0)
    md = re.sub(r"第\s*(\d{1,2})\s*讲", plain, md)
    md = md.replace("本课程团队", "").replace("课程团队", "")
    md = clean_sites(md)
    md = md.replace("## 与课程的联系", "## 关联知识")
    return md


SITE_MAP = {"https://flyscope.xizhe.net/": "apps/flyscope/index.html", "https://flyscope.xizhe.net": "apps/flyscope/index.html",
            "https://sparsecontrol.xizhe.net/": "apps/sparse-control/index.html", "https://sparsecontrol.xizhe.net": "apps/sparse-control/index.html"}


def clean_sites(md):
    for a, c in SITE_MAP.items():
        md = md.replace(a, c)
    md = re.sub(r"\]\(https://github\.com/zxzok/sparse-internal-control[^)]*\)", "](apps/sparse-control/index.html)", md)
    md = md.replace("（本站作者团队开发）", "").replace("（本站作者开发）", "").replace("，本站作者开发", "").replace("本站作者开发", "")
    return md


def split_sections(body):
    """'## Title {#id}' -> [(title, id, text)]"""
    parts = re.split(r"(?m)^## (.+)$", body)
    out = []
    for i in range(1, len(parts), 2):
        head = parts[i].strip()
        m = re.match(r"(.*?)\s*\{#([\w-]+)\}\s*$", head)
        title, sid = (m.group(1).strip(), m.group(2)) if m else (head, re.sub(r"[^\w-]+", "-", head).strip("-").lower() or f"s{i}")
        out.append((title, sid, parts[i + 1]))
    return out


def plain_text(md, n=None):
    t = re.sub(r"```.*?```", " ", md, flags=re.S)
    t = re.sub(r"\$\$.*?\$\$", " ", t, flags=re.S)
    t = re.sub(r"\$[^$\n]*\$", " ", t)
    t = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", t)
    t = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", t)
    t = re.sub(r"[*`_]", "", t)
    t = re.sub(r"<[^>]+>|:::.*|\{[#.][^}]*\}|[#>|]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t[:n] if n else t


# ----------------------------------------------------------------------------- content loading
def load_topics():
    topics = {}
    for t in TOPICS_META:
        p = CONTENT / "topics" / f"{t['id']}.md"
        if not p.exists():
            continue
        meta, body = front(p)
        meta = {**t, **meta}
        secs = split_sections(delecture(body))
        meta["_secs"] = secs
        meta["_articles"] = [(ti, si, tx) for ti, si, tx in secs if si not in TOPIC_ONLY and ti not in TOPIC_ONLY_TITLES]
        meta["_special"] = {si if si in TOPIC_ONLY else {"概述": "overview", "关联知识": "related", "核心文献": "references",
                            "延伸资源": "resources", "开放问题": "questions"}[ti]: tx
                            for ti, si, tx in secs if si in TOPIC_ONLY or ti in TOPIC_ONLY_TITLES}
        topics[t["id"]] = meta
    return topics


def load_papers():
    out = []
    d = CONTENT / "papers"
    for p in sorted(d.glob("*.md")):
        meta, body = front(p)
        meta.setdefault("id", p.stem)
        meta["_body"] = delecture(body)
        meta["topics"] = [LEGACY[l] for l in (meta.get("lectures") or []) if l in LEGACY]
        doms = []
        for t in meta["topics"]:
            dm = TMETA[t]["domain"]
            if dm not in doms:
                doms.append(dm)
        meta["domains"] = doms
        out.append(meta)
    out.sort(key=lambda x: (0 if not x.get("own") else 1, int(x.get("year") or 0)))
    return out


def load_resources():
    p = CONTENT / "resources.yaml"
    if not p.exists():
        return []
    data = yaml.safe_load(p.read_text(encoding="utf-8")) or []
    data = data if isinstance(data, list) else data.get("resources", [])
    out = []
    for r in data:
        r = {k: (clean_sites(v) if isinstance(v, str) else v) for k, v in r.items()}
        r["url"] = SITE_MAP.get(str(r.get("url", "")), r.get("url", ""))
        out.append(r)
    return out


def code_cells(tid):
    p = CONTENT / "code" / f"{tid}.py"
    if not p.exists():
        return "", []
    src = p.read_text(encoding="utf-8")
    chunks = re.split(r"(?m)^# %%\s*", src)
    pre = chunks[0].strip()
    cells = []
    for ch in chunks[1:]:
        title, _, code = ch.partition("\n")
        title = re.sub(r"^示例[：:]\s*", "", title.strip())
        cells.append((title, code.strip("\n")))
    return pre, cells


# ----------------------------------------------------------------------------- page chrome
NAV = [("index.html", "首页", "home"), ("courses.html", "课程视频", "courses"), ("domains.html", "知识领域", "domains"), ("lab.html", "可视化实验室", "lab"),
       ("code.html", "代码库", "code"), ("papers.html", "文献", "papers"), ("resources.html", "数据与软件", "resources"),
       ("glossary.html", "知识索引", "glossary")]


def head(title, desc=""):
    full = title if title == SITE else f"{title} · {SITE}"
    return (f'<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">'
            f'<meta name="claude:viewport-fit-sides" content="cover"><title>{E(full)}</title>'
            f'<meta name="description" content="{E(desc)}">{FONTS}<link rel="stylesheet" href="assets/css/site.css">'
            '<script>try{var t=localStorage.getItem("bcna:theme");if(t)document.documentElement.setAttribute("data-theme",JSON.parse(t))}catch(e){}</script>')


def topbar(active):
    nav = "".join(f'<a href="{h}"{" aria-current=\"page\"" if k == active else ""}>{t}</a>' for h, t, k in NAV)
    return (f'<header class="topbar"><div class="topbar-inner">'
            '<button class="menu-btn" type="button" aria-label="打开知识目录" aria-expanded="false">☰ 目录</button>'
            f'<a class="brand" href="index.html">{LOGO}<span>{SITE}<small>{SITE_EN}</small></span></a>'
            f'<nav class="topnav" aria-label="主导航">{nav}</nav>'
            '<form class="top-search" action="search.html" role="search"><input type="search" name="q" placeholder="搜索概念、算法、论文…" aria-label="站内搜索"></form>'
            '<button class="theme-btn" type="button" aria-label="切换深浅色">◐</button></div></header>')


def rail(topics, cur_topic=None, cur_sec=None, cur_domain=None):
    if cur_topic and not cur_domain:
        cur_domain = TMETA[cur_topic]["domain"]
    out = ['<nav class="rail tree" aria-label="知识体系">']
    for d in DOMAINS:
        ts = [t for t in TOPIC_IDS if TMETA[t]["domain"] == d["id"]]
        op = " open" if cur_domain == d["id"] else ""
        out.append(f'<details class="dom-{d["id"]}"{op}><summary>{E(d["title"])}</summary><ol>')
        out.append(f'<li><a href="d-{d["id"]}.html"{" aria-current=\"page\"" if cur_domain == d["id"] and not cur_topic and cur_sec == "domain" else ""}>领域概览</a></li>')
        for t in ts:
            cur = ' aria-current="page"' if t == cur_topic and not cur_sec else ""
            out.append(f'<li><a href="{t}.html"{cur}>{E(ttitle(t))}</a>')
            if t == cur_topic and t in topics:
                out.append('<ol class="sub">')
                for i, (ti, si, _) in enumerate(topics[t]["_articles"], 1):
                    c2 = ' aria-current="page"' if si == cur_sec else ""
                    out.append(f'<li><a href="{t}.{si}.html"{c2}><span class="n">{i:02d}</span>{E(ti)}</a></li>')
                out.append("</ol>")
            out.append("</li>")
        out.append("</ol></details>")
    out.append('<div class="tree-links"><a href="index.html">首页</a><a href="lab.html">可视化实验室</a><a href="code.html">计算方法与代码库</a>'
               '<a href="papers.html">文献知识库</a><a href="resources.html">数据与软件</a><a href="glossary.html">知识索引</a>'
               '<a href="courses.html">课程视频</a><a href="search.html">站内搜索</a><a href="about.html">关于本站</a></div>')
    out.append("</nav>")
    return "".join(out)


TOPICS = {}


def write_page(name, title, desc, active, body, topic=None, sec=None, scripts=("site.js",), with_rail=True, body_attr="", domain=None):
    sc = "".join(f'<script src="assets/js/{s}"></script>' for s in scripts)
    dom = domain or (TMETA[topic]["domain"] if topic in TMETA else None)
    cls = f' class="dom-{dom}"' if dom else ""
    shell = (f'<div class="shell">{rail(TOPICS, topic, sec, dom)}<main id="main">{body}</main></div><div class="nav-scrim" hidden></div>' if with_rail
             else f'<div class="shell wide"><main id="main">{body}</main></div>')
    foot = ('<footer class="site"><div><b>' + SITE + '</b><span>' + SITE_EN + '</span>'
            '<a href="courses.html">课程视频</a><a href="domains.html">知识领域</a><a href="lab.html">可视化实验室</a><a href="code.html">代码库</a><a href="papers.html">文献</a>'
            '<a href="resources.html">数据与软件</a><a href="glossary.html">知识索引</a><a href="about.html">关于本站</a></div></footer>')
    page = (f'<!doctype html><html lang="zh-CN"><head>{head(title, desc)}</head><body{cls}{body_attr}>{topbar(active)}{shell}{foot}{sc}</body></html>')
    (DIST / name).write_text(page, encoding="utf-8")
    return page


def redirect(name, target, label):
    (DIST / name).write_text(f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>{E(label)}</title>'
                             f'<meta http-equiv="refresh" content="0; url={target}"><link rel="canonical" href="{target}"></head>'
                             f'<body><p>本页已移至 <a href="{target}">{E(label)}</a>。</p></body></html>', encoding="utf-8")


# ----------------------------------------------------------------------------- shared blocks
def reading_minutes(md):
    n = len(re.sub(r"\s", "", plain_text(md)))
    return max(1, round(n / 450))


def appendix_refs(html_text):
    """Distill-style appendix: every DOI cited on the page, in order of first appearance."""
    seen, items = set(), []
    for m in re.finditer(r'<a href="(https?://(?:dx\.)?doi\.org/[^"]+)"[^>]*>(.*?)</a>', html_text):
        u = m.group(1)
        if u in seen:
            continue
        seen.add(u)
        # nearest preceding text gives the citation context
        start = html_text.rfind("<li", 0, m.start())
        ctx = re.sub(r"<[^>]+>", "", html_text[start:m.start()] if start > m.start() - 400 and start >= 0 else "")
        ctx = re.sub(r"\s+", " ", ctx).strip()[-120:]
        items.append((ctx, u))
    if not items:
        return ""
    lis = "".join(f'<li>{E(c) + " " if c else ""}<a href="{E(u)}" target="_blank" rel="noopener">{E(u.split("doi.org/")[-1])}</a></li>' for c, u in items)
    return f'<aside class="appendix"><h2>本页引用的文献</h2><ol>{lis}</ol></aside>'


DEMO_SECTION = {"graph_matrix": ("network-basics", "adjacency-matrix"), "er": ("network-metrics", "er-evolution"),
                "ws": ("network-models", "watts-strogatz"), "ba": ("network-models", "barabasi-albert"),
                "modularity": ("community-structure", "modularity"), "sir": ("spreading", "immunization"),
                "kuramoto": ("synchronization", "kuramoto-model"), "matching": ("controllability", "structural-controllability"),
                "attack": ("robustness", "targeted-attack"), "brain_threshold": ("brain-connectome", "thresholding"),
                "dfc": ("dynamic-brain-networks", "sliding-window"), "symptom": ("symptom-networks", "gaussian-graphical-model"),
                "ffl": ("molecular-networks", "network-motifs"), "proximity": ("network-medicine", "network-proximity")}


def place_demo(html_body, demo_id):
    """Insert an interactive figure after the first definition box, otherwise after the second paragraph."""
    fig = f'<div class="demo" data-demo="{demo_id}"></div>'
    m = re.search(r'<div class="callout-def">.*?</div>', html_body, re.S)
    if m:
        return html_body[:m.end()] + fig + html_body[m.end():]
    ps = [mm.end() for mm in re.finditer(r"</p>", html_body)]
    pos = ps[1] if len(ps) > 1 else (ps[0] if ps else len(html_body))
    return html_body[:pos] + fig + html_body[pos:]


def video_html(vid):
    vdir = DIST / "media" / "videos"
    if not (vdir / f"{vid}.mp4").exists():
        return ""
    meta = json.loads((vdir / f"{vid}.json").read_text(encoding="utf-8")) if (vdir / f"{vid}.json").exists() else {}
    dur = meta.get("duration", 0)
    tr = (vdir / f"{vid}.txt").read_text(encoding="utf-8") if (vdir / f"{vid}.txt").exists() else ""
    tp = "".join(f"<p>{E(p)}</p>" for p in tr.split("\n\n") if p.strip())
    return (f'<div class="video-main"><video controls preload="metadata" playsinline poster="media/videos/{vid}.jpg">'
            f'<source src="media/videos/{vid}.mp4" type="video/mp4"><track kind="captions" srclang="zh" label="中文字幕" src="media/videos/{vid}.vtt"></video>'
            f'<div class="video-meta"><strong>{E(meta.get("title", ""))}</strong><span>{int(dur // 60)} 分 {int(dur % 60)} 秒</span></div>'
            + (f'<details class="transcript"><summary>文字稿</summary>{tp}</details>' if tp else "") + '</div>')


def videos_block(tid):
    vids = [v for v in VIDEOS.get(tid, []) if (DIST / "media" / "videos" / f"{v}.mp4").exists()]
    if not vids:
        return ""
    main, rest = vids[0], vids[1:]
    out = [f'<section class="block" id="video"><h2><span class="tag">VIDEO</span>讲解视频</h2>{video_html(main)}']
    if rest:
        out.append('<ul class="vlist">')
        for v in rest:
            m = json.loads((DIST / "media" / "videos" / f"{v}.json").read_text(encoding="utf-8"))
            d = m.get("duration", 0)
            out.append(f'<li style="grid-template-columns:minmax(0,1fr)"><details><summary style="cursor:pointer">{E(m.get("title", v))} '
                       f'<span class="vtype">· {int(d // 60)} 分 {int(d % 60)} 秒</span></summary>{video_html(v)}</details></li>')
        out.append("</ul>")
    out.append("</section>")
    return "".join(out)


GALLERY = ROOT / "build" / "gallery"


def ex_meta(tid, i):
    p = GALLERY / f"{tid}-{i}.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def gcard(tid, i, title, show_topic=False):
    m = ex_meta(tid, i)
    if m.get("figures"):
        thumb = f'<img src="gallery/{tid}-{i}-0.png" alt="" loading="lazy">'
    else:
        txt = (m.get("stdout") or "").strip().splitlines()[:9]
        thumb = f'<pre>{E(chr(10).join(txt)) if txt else "（文字输出）"}</pre>'
    sub = f'<small>{E(ttitle(tid))}</small>' if show_topic else ""
    return f'<a class="gcard" href="ex-{tid}-{i}.html"><span class="thumb">{thumb}</span><span class="gt">{E(title)}{sub}</span></a>'


def code_block(tid, compact=False):
    pre, cells = code_cells(tid)
    if not cells:
        return ""
    cards = "".join(gcard(tid, i, t) for i, (t, _) in enumerate(cells))
    return (f'<section class="block" id="code"><h2><span class="tag">CODE</span>计算实现</h2>'
            f'<p class="small">{len(cells)} 个完整可运行的 Python 示例，每个都给出代码、输出图和解读；可在浏览器中直接运行，或下载 '
            f'<a href="notebooks/{tid}.ipynb" download>Jupyter Notebook</a> · <a href="notebooks/{tid}.py" download>Python 脚本</a>。</p>'
            f'<div class="gallery">{cards}</div></section>')


def demos_block(meta):
    ds = [d for d in (meta.get("demos") or []) if d in DEMO_INFO]
    if not ds:
        return ""
    return ('<section class="block" id="demos"><h2><span class="tag">INTERACTIVE</span>交互可视化</h2>'
            + "".join(f'<div class="demo" data-demo="{d}"></div>' for d in ds) + "</section>")


def paper_card(p):
    own = p.get("own")
    tlinks = " ".join(f'<a href="{t}.html">{E(ttitle(t))}</a>' for t in p.get("topics", []))
    vid = (DIST / "media" / "videos" / f'{p["id"]}.mp4').exists()
    badges = ((f'<span class="pbadge">{"研究论文" if own else "经典"}</span>')
              + "".join(f'<span class="pbadge dm">{E(DOM[d]["title"])}</span>' for d in p.get("domains", [])[:2])
              + ('<span class="pbadge vid">▶ 视频</span>' if vid else ""))
    return (f'<article class="pcard" data-own="{1 if own else 0}" data-dom="{" ".join(p.get("domains", []))}" '
            f'data-k="{E((str(p.get("title", "")) + str(p.get("title_zh", "")) + " ".join(map(str, p.get("keywords") or []))).lower())}">'
            f'<div class="pmeta">{badges}<span>{E(str(p.get("venue", "")))} · {p.get("year", "")}</span></div>'
            f'<h3><a href="paper-{p["id"]}.html">{E(str(p.get("title_zh") or p.get("title")))}</a></h3>'
            f'<p class="porig">{E(str(p.get("title", "")))}<br><span>{E(str(p.get("authors", "")))}</span></p>'
            f'<p class="psum">{E(str(p.get("summary", "")))}</p>'
            f'<div class="plec small">相关专题：{tlinks}</div></article>')


def topic_card(tid, show_articles=True):
    t = TOPICS.get(tid)
    m = TMETA[tid]
    arts = ""
    if t and show_articles:
        arts = "<ol class='artlist'>" + "".join(f'<li><a href="{tid}.{si}.html">{E(ti)}</a></li>' for ti, si, _ in t["_articles"][:8]) + "</ol>"
    summ = E(str((t or {}).get("summary", ""))) if t else "内容整理中。"
    return (f'<div class="tcard"><h3><a href="{tid}.html">{E(m["title"])}</a></h3><p class="en">{E(m.get("en", ""))}</p>'
            f'<p class="d">{summ}</p>{arts}</div>')


# ----------------------------------------------------------------------------- topic and article pages
def doc_head(crumbs, eyebrow, title, dek="", meta=(), extra=""):
    cr = ' <span class="sep">/</span> '.join(crumbs)
    mt = "".join(f"<div><dt>{E(k)}</dt><dd>{v}</dd></div>" for k, v in meta if v)
    return (f'<header class="doc-head"><nav class="crumb">{cr}</nav><div class="eyebrow" style="margin-top:14px">{eyebrow}</div>'
            f'<h1>{E(title)}</h1>' + (f'<p class="dek">{dek}</p>' if dek else "") + (f'<dl class="doc-meta">{mt}</dl>' if mt else "") + extra + "</header>")


def build_topic(tid, papers, resources):
    t = TOPICS[tid]
    d = DOM[t["domain"]]
    sp = t["_special"]
    arts = t["_articles"]
    kws = "".join(f'<span class="chip">{E(str(k))}</span>' for k in (t.get("keywords") or [])[:14])
    mins = sum(reading_minutes(tx) for _, _, tx in arts)
    nvid = len([v for v in VIDEOS.get(tid, []) if (DIST / "media" / "videos" / f"{v}.mp4").exists()])
    ncode = len(code_cells(tid)[1])
    meta = [("知识页面", f"{len(arts)} 页"), ("阅读", f"约 {mins} 分钟"), ("讲解视频", f"{nvid} 段" if nvid else ""),
            ("代码示例", f"{ncode} 个" if ncode else "")]
    b = [doc_head([f'<a href="domains.html">知识领域</a>', f'<a href="d-{d["id"]}.html">{E(d["title"])}</a>'],
                  f'<b>{E(d["en"])}</b><span>{E(t.get("en", ""))}</span>', t["title"], E(str(t.get("summary", ""))), meta,
                  f'<div class="chips">{kws}</div>')]
    if sp.get("overview"):
        b.append(f'<section class="block prose" id="overview">{pandoc(sp["overview"])}</section>')
    if arts:
        items = "".join(f'<a class="art" href="{tid}.{si}.html"><span class="no">{i:02d}</span><span class="t">{E(ti)}</span>'
                        f'<span class="d">{E(plain_text(tx, 90))}…</span></a>' for i, (ti, si, tx) in enumerate(arts, 1))
        b.append(f'<section class="block" id="pages"><h2><span class="tag">Contents</span>知识页面</h2><div class="arts">{items}</div></section>')
    b.append(videos_block(tid))
    b.append(demos_block(t))
    b.append(code_block(tid))
    if sp.get("related"):
        b.append(f'<section class="block prose" id="related"><h2><span class="tag">Links</span>关联知识</h2>{pandoc(sp["related"])}</section>')
    ps = [p for p in papers if tid in p.get("topics", [])]
    if ps:
        b.append(f'<section class="block" id="papers"><h2><span class="tag">Papers</span>论文精读</h2><div class="pgrid">{"".join(paper_card(p) for p in ps)}</div></section>')
    if sp.get("references"):
        b.append(f'<section class="block prose" id="references"><h2><span class="tag">References</span>核心文献</h2>{pandoc(sp["references"])}</section>')
    rs = [r for r in resources if tid in (r.get("topics") or [])]
    if rs:
        b.append('<section class="block" id="data"><h2><span class="tag">Data &amp; tools</span>相关数据与软件</h2><div class="rgrid">'
                 + "".join(res_card(r) for r in rs) + "</div></section>")
    if sp.get("resources"):
        b.append(f'<section class="block prose" id="resources"><h2><span class="tag">Further</span>延伸资源</h2>{pandoc(sp["resources"])}</section>')
    if sp.get("questions"):
        b.append(f'<section class="block prose" id="questions"><h2><span class="tag">Open questions</span>开放问题</h2>{pandoc(sp["questions"])}</section>')
    content = f'<div class="lec-grid"><article style="min-width:0">{"".join(b)}</article><aside class="toc" data-auto aria-label="本页目录"><b>本页目录</b></aside></div>'
    scripts = ("site.js", "demos.js") if t.get("demos") else ("site.js",)
    write_page(f"{tid}.html", t["title"], f"{t['title']}：{t.get('summary', '')}", "domains", content, tid, scripts=scripts)


def build_articles(tid, papers):
    t = TOPICS[tid]
    d = DOM[t["domain"]]
    arts = t["_articles"]
    demos_here = {sec: dm for dm, (tt, sec) in DEMO_SECTION.items() if tt == tid}
    for i, (ti, si, tx) in enumerate(arts):
        prev = arts[i - 1] if i > 0 else None
        nxt = arts[i + 1] if i + 1 < len(arts) else None
        pager = ('<nav class="pager">'
                 + (f'<a href="{tid}.{prev[1]}.html"><small>上一页</small>{E(prev[0])}</a>' if prev else f'<a href="{tid}.html"><small>专题主页</small>{E(t["title"])}</a>')
                 + (f'<a href="{tid}.{nxt[1]}.html"><small>下一页</small>{E(nxt[0])}</a>' if nxt else f'<a href="{tid}.html"><small>回到专题</small>{E(t["title"])}</a>') + "</nav>")
        body_html = pandoc(tx)
        scripts = ("site.js",)
        if si in demos_here:
            body_html = place_demo(body_html, demos_here[si])
            scripts = ("site.js", "demos.js")
        rel = []
        others = [dm for dm in (t.get("demos") or []) if dm in DEMO_INFO and dm != demos_here.get(si)]
        if others:
            rel.append("交互可视化：" + "、".join(f'<a href="lab.html#{dm}">{E(DEMO_INFO[dm][1])}</a>' for dm in others))
        _, cells = code_cells(tid)
        if cells:
            rel.append("代码示例：" + "、".join(f'<a href="ex-{tid}-{j}.html">{E(ct)}</a>' for j, (ct, _) in enumerate(cells[:4])))
        ps = [p for p in papers if tid in p.get("topics", [])][:4]
        if ps:
            rel.append("论文精读：" + "、".join(f'<a href="paper-{p["id"]}.html">{E(str(p.get("title_zh") or p.get("title")))}</a>' for p in ps))
        relh = ('<section class="block related-box"><h2>继续阅读</h2><ul>' + "".join(f"<li>{r}</li>" for r in rel) + "</ul></section>") if rel else ""
        first = re.split(r"(?<=[。！？])", plain_text(tx, 400))[0]
        dek = E(first) if 18 <= len(first) <= 160 else ""
        head_html = doc_head([f'<a href="d-{d["id"]}.html">{E(d["title"])}</a>', f'<a href="{tid}.html">{E(t["title"])}</a>'],
                             f'<b>{E(t["title"])}</b><span>{i + 1:02d} / {len(arts):02d}</span>', ti, "",
                             [("所属专题", f'<a href="{tid}.html">{E(t["title"])}</a>'), ("阅读", f"约 {reading_minutes(tx)} 分钟")])
        body = f'{head_html}<section class="block prose" id="notes">{body_html}</section>{appendix_refs(body_html)}{relh}{pager}'
        content = f'<div class="lec-grid"><article style="min-width:0">{body}</article><aside class="toc" data-auto aria-label="本页目录"><b>本页目录</b></aside></div>'
        write_page(f"{tid}.{si}.html", f"{ti}", f"{t['title']} · {ti}", "domains", content, tid, si, scripts=scripts)


# ----------------------------------------------------------------------------- domain pages
def build_domains(papers, resources):
    cards = []
    for d in DOMAINS:
        ts = [t for t in TOPIC_IDS if TMETA[t]["domain"] == d["id"]]
        npg = sum(len(TOPICS[t]["_articles"]) for t in ts if t in TOPICS)
        cards.append(f'<a class="dcard dom-{d["id"]}" href="d-{d["id"]}.html"><span class="en">{E(d["en"])}</span><b>{E(d["title"])}</b>'
                     f'<span class="d">{E(d["desc"])}</span><span class="ts">{" · ".join(E(ttitle(t)) for t in ts)}</span>'
                     f'<span class="cnt">{len(ts)} 个专题 · {npg} 个知识页面</span></a>')
    body = (doc_head(['<a href="index.html">首页</a>'], "<b>Knowledge domains</b>", "知识领域",
                     "七个相互关联的知识领域构成本站的知识体系。它们不是需要按顺序学习的单元：每个专题都同时连接理论、可视化、代码、论文与数据，可以从任何一个入口进入。")
            + f'<div class="dgrid">{"".join(cards)}</div>')
    write_page("domains.html", "知识领域", "生物医学网络科学的知识体系", "domains", body)
    for d in DOMAINS:
        ts = [t for t in TOPIC_IDS if TMETA[t]["domain"] == d["id"]]
        ps = [p for p in papers if d["id"] in p.get("domains", [])]
        rs = [r for r in resources if d["id"] in (r.get("domain") or [])]
        demos = [dm for dm, (t, _) in DEMO_INFO.items() if TMETA[t]["domain"] == d["id"]]
        exs = [(t, i, ct) for t in ts for i, (ct, _) in enumerate(code_cells(t)[1]) if ex_meta(t, i).get("figures")][:8]
        b = [doc_head(['<a href="domains.html">知识领域</a>'], f'<b>{E(d["en"])}</b>', d["title"], E(d["desc"])),
             f'<section class="block"><h2><span class="tag">Topics</span>专题</h2><div class="tgrid">{"".join(topic_card(t) for t in ts)}</div></section>']
        if demos:
            b.append('<section class="block"><h2><span class="tag">Interactive</span>交互可视化</h2><div class="labgrid">'
                     + "".join(f'<a class="labitem" href="lab.html#{dm}"><b>{E(DEMO_INFO[dm][1])}</b><span>{E(ttitle(DEMO_INFO[dm][0]))}</span></a>' for dm in demos)
                     + "</div></section>")
        if exs:
            b.append(f'<section class="block"><h2><span class="tag">Code</span>代码示例</h2><div class="gallery">{"".join(gcard(t, i, ct, True) for t, i, ct in exs)}</div>'
                     f'<p class="small"><a href="code.html#{d["id"]}">本领域的全部代码示例 →</a></p></section>')
        if ps:
            b.append(f'<section class="block"><h2><span class="tag">Papers</span>论文精读</h2><div class="pgrid">{"".join(paper_card(p) for p in ps)}</div></section>')
        if rs:
            b.append(f'<section class="block"><h2><span class="tag">Data &amp; tools</span>数据与软件</h2><div class="rgrid">{"".join(res_card(r) for r in rs)}</div></section>')
        write_page(f"d-{d['id']}.html", d["title"], d["desc"], "domains", "".join(b), sec="domain", domain=d["id"])


def topic_graph():
    """Topics as a network: edges are cross-references between topic texts."""
    w = {}
    for tid, t in TOPICS.items():
        txt = "".join(tx for _, _, tx in t["_secs"])
        for m in re.finditer(r"\]\(([a-z-]+)(?:\.[a-z0-9-]+)?\.html", txt):
            o = m.group(1)
            if o in TOPICS and o != tid:
                k = tuple(sorted((tid, o)))
                w[k] = w.get(k, 0) + 1
    nodes = [{"id": t, "t": TOPICS[t]["title"], "d": TMETA[t]["domain"], "n": len(TOPICS[t]["_articles"])} for t in TOPIC_IDS if t in TOPICS]
    edges = [[a, b, c] for (a, b), c in w.items()]
    return {"nodes": nodes, "edges": edges}


def build_index(papers):
    dom_cards = []
    for d in DOMAINS:
        ts = [t for t in TOPIC_IDS if TMETA[t]["domain"] == d["id"]]
        dom_cards.append(f'<div class="dcard dom-{d["id"]}"><a class="dhead" href="d-{d["id"]}.html"><span class="en">{E(d["en"])}</span><b>{E(d["title"])}</b>'
                         f'<span class="d">{E(d["short"])}</span></a><ul>' + "".join(f'<li><a href="{t}.html">{E(ttitle(t))}</a></li>' for t in ts) + "</ul></div>")
    feat_ids = ("watts1998_smallworld", "barabasi1999_scaling", "liu2011_controllability", "bullmore2009_brain", "borsboom2013_psychopathology", "menche2015_interactome")
    feat = [p for p in papers if p["id"] in feat_ids]
    lab_items = "".join(f'<a class="labitem" href="lab.html#{dm}"><b>{E(DEMO_INFO[dm][1])}</b><span>{E(ttitle(DEMO_INFO[dm][0]))}</span></a>'
                        for dm in ("ws", "ba", "modularity", "sir", "kuramoto", "matching", "attack", "brain_threshold", "symptom", "proximity"))
    gal = []
    for t in ("network-models", "community-structure", "robustness", "synchronization", "brain-connectome", "symptom-networks", "gene-network-inference", "network-medicine"):
        for i, (ct, _) in enumerate(code_cells(t)[1]):
            if ex_meta(t, i).get("figures"):
                gal.append(gcard(t, i, ct, True))
                break
    legend = "".join(f'<span class="dom-{d["id"]}">{E(d["title"])}</span>' for d in DOMAINS)
    graph = json.dumps(topic_graph(), ensure_ascii=False).replace("</", "<\\/")
    tags = "".join(f'<a href="search.html?q={q}">{q}</a>' for q in ("模块度", "functional connectivity", "驱动节点", "WGCNA", "渗流", "PageRank", "网络邻近度", "EBICglasso"))
    body = f"""
<section class="hero"><div><div class="kicker">Biomedical Network Science · 在线手册</div>
<h1>从网络结构<br>到生物医学系统</h1>
<p class="lead">复杂网络的理论、动力学与控制，以及脑网络、症状网络、分子网络和网络医学中的研究方法：数据怎样得到、网络怎样构建、算法怎样使用、结果怎样解释、结论有哪些证据支持。</p>
<form class="hero-search" action="search.html" role="search"><input type="search" name="q" placeholder="搜索概念、算法、论文、数据集" aria-label="站内搜索"><button class="btn" type="submit">搜索</button></form>
<div class="hero-tags">试试：{tags}</div></div>
<figure class="kmap" style="margin:0"><canvas id="kmap" width="720" height="540" aria-label="本站知识专题之间的关联网络"></canvas><div class="kmap-legend">{legend}</div>
<figcaption class="kmap-cap">知识地图：节点是专题，连线是专题之间的相互引用。点击节点进入专题。</figcaption></figure></section>
<section class="home-sec"><span class="tag">Domains</span><h2>知识领域</h2><p class="small">七个相互关联的领域，从网络的数学表示到网络医学。</p><div class="dgrid">{"".join(dom_cards)}</div></section>
{courses_home()}
<section class="home-sec"><span class="tag">From data to conclusions</span><h2>每个生物医学领域的完整知识链</h2>
<p class="small">脑网络、症状网络、分子网络与网络医学的专题都沿着同一条链展开。</p>
<div class="chain"><div><i>01</i><b>数据怎样得到</b><span>影像、量表、表达谱、相互作用数据库，以及各自的偏倚。</span></div>
<div><i>02</i><b>网络怎样构建</b><span>节点与边的定义、连接估计、阈值与加权。<a href="network-construction.html">→</a></span></div>
<div><i>03</i><b>算法怎样使用</b><span>拓扑指标、社团、动力学、可控性与推断算法。</span></div>
<div><i>04</i><b>结果怎样解释</b><span>零模型、置换检验、稳定性与敏感性分析。</span></div>
<div><i>05</i><b>证据是否充分</b><span>相关与因果、外部验证、可复现与报告规范。<a href="reproducible-research.html">→</a></span></div></div></section>
<section class="home-sec"><span class="tag">Interactive</span><h2>交互式科学可视化</h2><p class="small">改变参数，观察网络结构与动力学怎样随之变化；每个可视化都嵌在相应的知识页面中，也可以导出图片与参数。</p>
<div class="labgrid">{lab_items}</div><p class="small" style="margin-top:12px"><a href="lab.html">进入可视化实验室 →</a></p></section>
<section class="home-sec"><span class="tag">Code gallery</span><h2>计算方法与代码库</h2><p class="small">每个算法都有完整、可运行的 Python 示例，附输出图与解读。</p>
<div class="gallery">{"".join(gal)}</div><p class="small" style="margin-top:12px"><a href="code.html">浏览全部代码示例 →</a></p></section>
<section class="home-sec"><span class="tag">Literature</span><h2>文献知识库</h2><p class="small">按科学主题组织的论文精读：研究问题、设计、方法、结论、证据与局限。</p>
<div class="pgrid">{"".join(paper_card(p) for p in feat)}</div><p class="small" style="margin-top:12px"><a href="papers.html">按主题检索全部论文 →</a></p></section>
<section class="home-sec"><span class="tag">Reference</span><h2>数据、软件与术语</h2><div class="entry3">
<a href="resources.html"><b>数据与软件资源库</b><span>脑影像、量表、分子相互作用、药物与疾病数据库，以及分析软件的中文介绍。</span></a>
<a href="glossary.html"><b>知识索引</b><span>中英文术语、定义与公式，连接到对应的理论、可视化与论文。</span></a>
<a href="search.html"><b>站内搜索</b><span>支持中英文与常见缩写，同时检索专题、知识页面、论文、代码与数据。</span></a></div></section>
<script>window.KMAP={graph};</script><script src="assets/js/kmap.js"></script>"""
    return write_page("index.html", SITE, "生物医学网络科学：复杂网络理论、动力学与控制，以及脑网络、症状网络、分子网络与网络医学", "home", body, with_rail=False)


def build_lab():
    parts = ['<div class="lec-head"><h1>交互式科学可视化实验室</h1><p class="lead">改变参数、观察结果、理解机制。每个可视化都对应一个知识专题，'
             '可以导出当前图像（PNG）与参数（JSON）。脑网络、症状网络与网络医学的可视化使用模拟数据，只用于说明方法，不代表任何真实人群或疾病结论。</p></div>']
    for d in DOMAINS:
        demos = [dm for dm, (t, _) in DEMO_INFO.items() if TMETA[t]["domain"] == d["id"]]
        if not demos:
            continue
        parts.append(f'<section class="block"><h2><span class="tag">{E(d["en"].upper())}</span>{E(d["title"])}</h2>')
        for dm in demos:
            t = DEMO_INFO[dm][0]
            parts.append(f'<p class="small" id="{dm}" style="margin:18px 0 -8px">对应专题：<a href="{t}.html">{E(ttitle(t))}</a></p><div class="demo" data-demo="{dm}"></div>')
        parts.append("</section>")
    parts.append('<section class="block"><h2><span class="tag">CONNECTOMES · AI</span>专题交互网站</h2>'
                 '<div class="ext-card"><div><b>FlyScope · 果蝇连接组浏览器</b><p class="small" style="margin:6px 0 0">基于 MaleCNS 与 FlyWire 两个成年果蝇全脑连接组：'
                 '连接图之外，神经元内部的输入位置也记录着网络中远处的连接。配套阅读：<a href="paper-zhang2026_flysynapse.html">论文精读</a> · <a href="brain-connectome.html">脑连接组</a></p></div>'
                 '<a class="btn" href="apps/flyscope/index.html" style="text-decoration:none;white-space:nowrap">进入 FlyScope →</a></div>'
                 '<div class="ext-card" style="margin-top:12px"><div><b>Sparse Internal Control · 语言模型的稀疏内部控制</b><p class="small" style="margin:6px 0 0">把“选少数驱动节点控制系统”的思想用到大语言模型内部：'
                 '理论、六轴评价协议与讲解视频。配套阅读：<a href="paper-zhang2026_sparsecontrol.html">论文精读</a> · <a href="controllability.html">网络可控性与稳定性</a></p></div>'
                 '<a class="btn" href="apps/sparse-control/index.html" style="text-decoration:none;white-space:nowrap">进入网站 →</a></div></section>')
    write_page("lab.html", "交互式科学可视化实验室", "网络模型、结构指标与动力学的交互可视化", "lab", "".join(parts), scripts=("site.js", "demos.js"))


# ----------------------------------------------------------------------------- code library
TOOLKITS = [
    ("NetworkX", "https://networkx.org/documentation/stable/", "Python 通用图算法库：图的构建、最短路径、中心性、社团、匹配、随机图模型。", "pip install networkx"),
    ("igraph（python-igraph / R igraph）", "https://python.igraph.org/", "C 内核的大规模网络分析库，Leiden、Infomap 等社团算法。", "pip install igraph"),
    ("Brain Connectivity Toolbox（bctpy）", "https://github.com/aestrivex/bctpy", "脑网络拓扑指标的标准实现（MATLAB 原版与 Python 移植）。", "pip install bctpy"),
    ("Nilearn", "https://nilearn.github.io/stable/", "fMRI 时间序列提取、图谱、功能连接矩阵估计与可视化。", "pip install nilearn"),
    ("qgraph / bootnet（R）", "https://cran.r-project.org/package=bootnet", "心理与症状网络的估计、可视化与 bootstrap 稳定性分析。", 'install.packages(c("qgraph","bootnet"))'),
    ("WGCNA（R）", "https://cran.r-project.org/package=WGCNA", "加权基因共表达网络分析：软阈值、拓扑重叠、模块与性状关联。", 'install.packages("WGCNA")'),
]


def ex_description(code):
    """Leading comment lines of an example cell become its prose description."""
    lines = []
    for ln in code.splitlines():
        if ln.startswith("#"):
            lines.append(ln.lstrip("#").strip())
        elif ln.strip() == "":
            if lines:
                lines.append("")
        else:
            break
    return "\n".join(lines).strip()


def build_code(notebook_rows):
    groups, total = [], 0
    for d in DOMAINS:
        ts = [t for t in TOPIC_IDS if TMETA[t]["domain"] == d["id"] and code_cells(t)[1]]
        if not ts:
            continue
        sec = [f'<section class="block dom-{d["id"]}" id="{d["id"]}"><h2><span class="tag">{E(d["en"])}</span>{E(d["title"])}</h2>']
        for t in ts:
            cells = code_cells(t)[1]
            total += len(cells)
            sec.append(f'<div class="gallery-group"><h3><a href="{t}.html">{E(ttitle(t))}</a></h3><p class="small">{len(cells)} 个示例 · '
                       f'<a href="notebooks/{t}.ipynb" download>Notebook</a> · <a href="notebooks/{t}.py" download>.py</a></p>'
                       f'<div class="gallery">{"".join(gcard(t, i, ct) for i, (ct, _) in enumerate(cells))}</div></div>')
        sec.append("</section>")
        groups.append("".join(sec))
    tk = "".join(f'<div class="tcard"><h3><a href="{u}" target="_blank" rel="noopener">{E(n)} ↗</a></h3><p class="d">{E(dd)}</p><p class="small"><code>{E(c)}</code></p></div>'
                 for n, u, dd, c in TOOLKITS)
    body = (doc_head(['<a href="index.html">首页</a>'], "<b>Code gallery</b>", "计算方法与代码库",
                     f"{total} 个完整、可运行的 Python 示例，按知识领域与专题组织。每个示例给出输入数据格式、关键参数、代码、输出图与解读，可在浏览器中直接运行，也可以下载为 Jupyter Notebook。")
            + '<section class="block prose"><h2><span class="tag">Setup</span>本地环境</h2><p>Python 3.10 及以上：<code>pip install networkx numpy scipy pandas matplotlib jupyterlab</code>；'
              '脑网络另装 <code>nilearn bctpy</code>；症状网络可用 R 的 qgraph、bootnet。画图出现中文方框时，在代码开头加 '
              '<code>plt.rcParams["font.sans-serif"] = ["PingFang SC", "Microsoft YaHei", "SimHei"]</code>。</p></section>'
            + "".join(groups)
            + f'<section class="block"><h2><span class="tag">Toolkits</span>常用工具包</h2><div class="tgrid">{tk}</div></section>')
    write_page("code.html", "计算方法与代码库", "生物医学网络分析的可运行 Python 示例", "code", body)
    # one page per example (Nilearn / NetworkX gallery style)
    for t in TOPIC_IDS:
        cells = code_cells(t)[1]
        for i, (ct, code) in enumerate(cells):
            m = ex_meta(t, i)
            desc = ex_description(code)
            figs = "".join(f'<img src="gallery/{t}-{i}-{k}.png" alt="{E(ct)}：输出图 {k + 1}" loading="lazy">' for k in range(m.get("figures", 0)))
            out = (m.get("stdout") or "").strip()
            prev = cells[i - 1] if i > 0 else None
            nxt = cells[i + 1] if i + 1 < len(cells) else None
            pager = ('<nav class="pager">'
                     + (f'<a href="ex-{t}-{i - 1}.html"><small>上一个示例</small>{E(prev[0])}</a>' if prev else f'<a href="code.html#{TMETA[t]["domain"]}"><small>代码库</small>{E(ttitle(t))}</a>')
                     + (f'<a href="ex-{t}-{i + 1}.html"><small>下一个示例</small>{E(nxt[0])}</a>' if nxt else f'<a href="{t}.html"><small>回到专题</small>{E(ttitle(t))}</a>') + "</nav>")
            rows = min(30, max(10, code.count("\n") + 2))
            body = (doc_head([f'<a href="code.html">代码库</a>', f'<a href="code.html#{TMETA[t]["domain"]}">{E(DOM[TMETA[t]["domain"]]["title"])}</a>',
                              f'<a href="{t}.html">{E(ttitle(t))}</a>'], f'<b>Example</b><span>{i + 1:02d} / {len(cells):02d}</span>', ct, "",
                             [("所属专题", f'<a href="{t}.html">{E(ttitle(t))}</a>'), ("下载", f'<a href="notebooks/{t}.ipynb" download>Notebook</a> · <a href="notebooks/{t}.py" download>.py</a>')])
                    + (f'<section class="block prose">{pandoc(desc)}</section>' if desc else "")
                    + (f'<section class="block"><h2><span class="tag">Output</span>输出图</h2><div class="ex-figs">{figs}</div></section>' if figs else "")
                    + (f'<section class="block"><h2><span class="tag">Output</span>文字输出</h2><pre class="ex-out">{E(out)}</pre></section>' if out else "")
                    + f'<section class="block prose"><h2><span class="tag">Code</span>代码</h2>{pandoc(chr(96) * 3 + "python" + chr(10) + code + chr(10) + chr(96) * 3)}</section>'
                    + f'<section class="block"><h2><span class="tag">Run</span>在浏览器中运行</h2><p class="small">首次加载 Python 环境约需 20–40 秒；可以修改参数后重新运行。</p>'
                      f'<div class="cell"><div class="cell-head"><h3>{E(ct)}</h3><div><button class="btn run" type="button">运行</button> '
                      f'<button class="btn ghost reset" type="button">还原</button> <button class="btn ghost copy" type="button">复制</button></div></div>'
                      f'<textarea id="{t}-cell{i}" rows="{rows}" spellcheck="false" aria-label="{E(ct)} 代码">{E(code)}</textarea><div class="out" aria-live="polite"></div></div></section>'
                    + pager)
            write_page(f"ex-{t}-{i}.html", ct, f"{ttitle(t)} · 代码示例：{ct}", "code", body, t, sec="code")


def build_notebooks():
    nb = DIST / "notebooks"
    if nb.exists():
        shutil.rmtree(nb)
    nb.mkdir()
    rows = []
    for tid in TOPIC_IDS:
        p = CONTENT / "code" / f"{tid}.py"
        if not p.exists():
            continue
        shutil.copy(p, nb / f"{tid}.py")
        pre, cells = code_cells(tid)
        doc_cells = [{"cell_type": "markdown", "metadata": {}, "source": [f"# {ttitle(tid)}：代码示例\n\n", f"来自《{SITE}》（{SITE_EN}）。\n"]}]
        if pre:
            doc_cells.append({"cell_type": "markdown", "metadata": {}, "source": [pre.replace("# ", "")]})
        for t, code in cells:
            doc_cells.append({"cell_type": "markdown", "metadata": {}, "source": [f"## {t}"]})
            doc_cells.append({"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": code.splitlines(True)})
        doc = {"cells": doc_cells, "metadata": {"kernelspec": {"name": "python3", "display_name": "Python 3", "language": "python"},
               "language_info": {"name": "python"}}, "nbformat": 4, "nbformat_minor": 5}
        (nb / f"{tid}.ipynb").write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
        rows.append((tid, [t for t, _ in cells]))
    return rows


# ----------------------------------------------------------------------------- papers
def build_papers(papers):
    keep = {f"paper-{p['id']}.html" for p in papers}
    for f in DIST.glob("paper-*.html"):
        if f.name not in keep:
            f.unlink()
    for i, p in enumerate(papers):
        build_paper(p, i, papers)
    dom_btns = "".join(f'<button class="btn ghost" data-dom="{d["id"]}" aria-pressed="false">{E(d["title"])}</button>' for d in DOMAINS
                       if any(d["id"] in p["domains"] for p in papers))
    body = (f'<div class="lec-head"><h1>文献知识库</h1><p class="lead">按科学主题检索的论文精读：每篇解释研究问题、研究设计、核心方法、主要结论、证据强度与局限，'
            f'并链接到对应的理论专题。收录奠定这一领域的经典论文与近年的代表性研究。</p>'
            f'<div class="pfilters"><button class="btn ghost" data-f="all" aria-pressed="true">全部</button><button class="btn ghost" data-f="classic" aria-pressed="false">经典论文</button>'
            f'<button class="btn ghost" data-f="own" aria-pressed="false">近年研究</button></div>'
            f'<div class="pfilters">{dom_btns}<input class="filter" id="paper-filter" type="search" placeholder="题名、方法或关键词" aria-label="搜索论文"></div></div>'
            f'<div class="pgrid" id="plist">{"".join(paper_card(p) for p in papers)}</div>'
            '<script>(function(){var mode="all",dom="",q="";function apply(){document.querySelectorAll("#plist .pcard").forEach(function(c){'
            'var ok=(mode==="all"||(mode==="own")===(c.dataset.own==="1"))&&(!dom||c.dataset.dom.split(" ").indexOf(dom)>=0)&&(!q||c.dataset.k.indexOf(q)>=0||c.textContent.toLowerCase().indexOf(q)>=0);c.hidden=!ok})}'
            'document.querySelectorAll(".pfilters [data-f]").forEach(function(b){b.addEventListener("click",function(){mode=b.dataset.f;document.querySelectorAll(".pfilters [data-f]").forEach(function(x){x.setAttribute("aria-pressed",x===b)});apply()})});'
            'document.querySelectorAll(".pfilters [data-dom]").forEach(function(b){b.addEventListener("click",function(){dom=dom===b.dataset.dom?"":b.dataset.dom;document.querySelectorAll(".pfilters [data-dom]").forEach(function(x){x.setAttribute("aria-pressed",x.dataset.dom===dom)});apply()})});'
            'document.getElementById("paper-filter").addEventListener("input",function(e){q=e.target.value.trim().toLowerCase();apply()})})();</script>')
    write_page("papers.html", "文献知识库", "生物医学网络科学经典论文与研究论文精读", "papers", body)


def build_paper(p, idx, papers):
    p = dict(p)
    if p.get("site"):
        p["site"] = SITE_MAP.get(str(p["site"]), p["site"])
    p.pop("code", None)
    if str(p.get("url", "")).startswith("https://flyscope") or str(p.get("url", "")).startswith("https://sparsecontrol"):
        p["url"] = SITE_MAP.get(str(p["url"]), "")
    pid = p["id"]
    doi = str(p.get("doi") or "").strip()
    link, label = (f"https://doi.org/{doi}", f"DOI: {doi}") if doi else ((str(p.get("url") or ""), "原文链接") if p.get("url") else ("", ""))
    video = ""
    if (DIST / "media" / "videos" / f"{pid}.mp4").exists():
        video = f'<section class="block" id="video"><h2><span class="tag">VIDEO</span>讲解视频</h2>{video_html(pid)}</section>'
    tl = "、".join(f'<a href="{t}.html">{E(ttitle(t))}</a>' for t in p.get("topics", []))
    kws = "".join(f'<span class="chip">{E(str(k))}</span>' for k in (p.get("keywords") or []))
    btns = ""
    if p.get("site") or p.get("code"):
        btns = ('<p style="margin:14px 0 0;display:flex;flex-wrap:wrap;gap:8px">'
                + (f'<a class="btn" href="{E(str(p["site"]))}" style="text-decoration:none">进入配套交互网站 →</a>' if p.get("site") else "")
                + (f'<a class="btn ghost" href="{E(str(p["code"]))}" target="_blank" rel="noopener" style="text-decoration:none">代码与数据（GitHub）↗</a>' if p.get("code") else "") + "</p>")
    doms = " · ".join(E(DOM[d]["title"]) for d in p.get("domains", []))
    headh = (f'<div class="lec-head"><nav class="crumb"><a href="papers.html">文献知识库</a>{" › " + doms if doms else ""}</nav>'
             f'<div class="eyebrow"><b>{"研究论文" if p.get("own") else "经典论文"}</b><span>难度：{E(str(p.get("level", "")))}</span></div>'
             f'<h1>{E(str(p.get("title_zh") or p.get("title")))}</h1><p class="porig big">{E(str(p.get("title", "")))}</p>'
             f'<p class="small">{E(str(p.get("authors", "")))} · <i>{E(str(p.get("venue", "")))}</i> {p.get("year", "")}'
             + (f' · <a href="{E(link)}" target="_blank" rel="noopener">{E(label)}</a>' if link else "") + f'</p><div class="chips">{kws}</div>{btns}'
             f'<div class="objectives"><h2>一句话</h2><p style="margin:0">{E(str(p.get("summary", "")))}</p>'
             f'<p class="small" style="margin:8px 0 0">相关专题：{tl}</p></div></div>')
    prev_p = papers[idx - 1] if idx > 0 else None
    next_p = papers[idx + 1] if idx + 1 < len(papers) else None
    pager = ('<nav class="pager">'
             + (f'<a href="paper-{prev_p["id"]}.html">← {E(str(prev_p.get("title_zh") or prev_p.get("title")))}</a>' if prev_p else '<a href="papers.html">← 文献知识库</a>')
             + (f'<a href="paper-{next_p["id"]}.html">{E(str(next_p.get("title_zh") or next_p.get("title")))} →</a>' if next_p else '<a href="papers.html">文献知识库 →</a>') + "</nav>")
    content = (f'<div class="lec-grid"><div style="min-width:0">{headh}{video}<section class="block prose" id="notes">{pandoc(p["_body"])}</section>{pager}</div>'
               f'<aside class="toc" data-auto aria-label="本页目录"><b>本页目录</b></aside></div>')
    write_page(f"paper-{pid}.html", str(p.get("title_zh") or p.get("title")), f"论文精读：{p.get('title', '')}", "papers", content,
               (p.get("topics") or [None])[0])


# ----------------------------------------------------------------------------- resources
KIND_ORDER = ["数据库", "数据集", "脑图谱", "软件/工具包", "交互网站"]


def res_card(r):
    doms = " ".join(r.get("domain") or [])
    return (f'<a class="rcard" href="r-{r["id"]}.html" data-dom="{doms}" data-k="{E((r.get("name", "") + " " + r.get("summary", "")).lower())}">'
            f'<span class="kind">{E(str(r.get("kind", "")))}</span><b>{E(str(r.get("name", "")))}</b><span class="d">{E(str(r.get("summary", "")))}</span></a>')


def build_resources(resources):
    if not resources:
        write_page("resources.html", "数据与软件资源库", "", "resources", '<div class="lec-head"><h1>数据与软件资源库</h1><p class="lead">整理中。</p></div>')
        return
    btns = "".join(f'<button class="btn ghost" data-dom="{d["id"]}" aria-pressed="false">{E(d["title"])}</button>' for d in DOMAINS
                   if any(d["id"] in (r.get("domain") or []) for r in resources))
    groups = []
    kinds = KIND_ORDER + sorted({str(r.get("kind", "")) for r in resources} - set(KIND_ORDER))
    for k in kinds:
        rs = [r for r in resources if str(r.get("kind", "")) == k]
        if rs:
            groups.append(f'<section class="block rgroup"><h2>{E(k)}</h2><div class="rgrid">{"".join(res_card(r) for r in rs)}</div></section>')
    body = (f'<div class="lec-head"><h1>数据与软件资源库</h1><p class="lead">生物医学网络研究常用的公共数据、数据库、脑图谱与分析软件。每个资源都有中文介绍：'
            f'适合回答的研究问题、数据类型、获取方式、访问限制、相关工具与引用要求。</p>'
            f'<div class="pfilters">{btns}<input class="filter" id="res-filter" type="search" placeholder="名称或用途" aria-label="筛选资源"></div></div>{"".join(groups)}'
            '<script>(function(){var dom="",q="";function apply(){document.querySelectorAll(".rcard").forEach(function(c){c.hidden=!((!dom||c.dataset.dom.split(" ").indexOf(dom)>=0)&&(!q||c.dataset.k.indexOf(q)>=0))});'
            'document.querySelectorAll(".rgroup").forEach(function(s){s.hidden=!s.querySelector(".rcard:not([hidden])")})}'
            'document.querySelectorAll(".pfilters [data-dom]").forEach(function(b){b.addEventListener("click",function(){dom=dom===b.dataset.dom?"":b.dataset.dom;document.querySelectorAll(".pfilters [data-dom]").forEach(function(x){x.setAttribute("aria-pressed",x.dataset.dom===dom)});apply()})});'
            'document.getElementById("res-filter").addEventListener("input",function(e){q=e.target.value.trim().toLowerCase();apply()})})();</script>')
    write_page("resources.html", "数据与软件资源库", "生物医学网络研究的数据库、数据集与软件", "resources", body)
    fields = [("questions", "适合的研究问题"), ("data", "数据类型"), ("access", "获取方式"), ("limits", "访问限制与许可"), ("tools", "相关工具与格式"), ("cite", "引用要求")]
    for r in resources:
        rows = "".join(f"<tr><th>{lab}</th><td>{pandoc(str(r[k])) if r.get(k) else '—'}</td></tr>" for k, lab in fields)
        tl = "、".join(f'<a href="{t}.html">{E(ttitle(t))}</a>' for t in (r.get("topics") or []) if t in TMETA)
        doms = " · ".join(f'<a href="d-{d}.html">{E(DOM[d]["title"])}</a>' for d in (r.get("domain") or []) if d in DOM)
        body = (f'<div class="lec-head"><nav class="crumb"><a href="resources.html">数据与软件资源库</a> › {E(str(r.get("kind", "")))}</nav><h1>{E(str(r["name"]))}</h1>'
                f'<p class="lead">{E(str(r.get("summary", "")))}</p><p>' + (f'<a class="btn" href="{E(str(r.get("url", "")))}" style="text-decoration:none">进入站内页面 →</a>' if str(r.get("url", "")).startswith("apps/") else f'<a class="btn" href="{E(str(r.get("url", "")))}" target="_blank" rel="noopener" style="text-decoration:none">访问官方网站 ↗</a>') + '</p>'
                f'<p class="small">领域：{doms}{"　相关专题：" + tl if tl else ""}</p></div>'
                f'<div class="prose" style="max-width:none"><div class="table-wrap"><table class="kv"><tbody>{rows}</tbody></table></div></div>')
        write_page(f"r-{r['id']}.html", str(r["name"]), str(r.get("summary", "")), "resources", body)


# ----------------------------------------------------------------------------- knowledge index (glossary) & search
def collect_terms():
    items = []
    for tid, t in TOPICS.items():
        for ti, si, tx in t["_articles"]:
            for m in re.finditer(r"::: \{\.callout-def\}\n(.*?)\n:::", tx, re.S):
                txt = m.group(1).strip()
                for para in re.split(r"\n\s*\n", txt):
                    h = re.match(r"\*\*(.+?)\*\*\s*[（(]([^）)]{2,60})[）)]", para) or re.match(r"\*\*(.+?)\*\*", para)
                    if not h:
                        continue
                    name = h.group(1).strip("：: ")
                    en = h.group(2).strip() if h.lastindex and h.lastindex >= 2 and re.search(r"[A-Za-z]", h.group(2) or "") else ""
                    items.append({"name": name, "en": en, "md": para, "topic": tid, "sec": si, "sectitle": ti})
    seen, out = set(), []
    for it in items:
        if it["name"] in seen or len(it["name"]) > 30:
            continue
        seen.add(it["name"])
        out.append(it)
    return out


def build_glossary(terms, papers):
    conv = []
    if terms:
        md = "\n\n".join(f"::: {{#g{i}}}\n{t['md']}\n:::" for i, t in enumerate(terms))
        out = pandoc(md)
        for i in range(len(terms)):
            m = re.search(rf'<div id="g{i}">(.*?)</div>\s*(?=<div id="g{i + 1}">|$)', out, re.S)
            conv.append(m.group(1) if m else E(terms[i]["md"]))
    cards = []
    for t, c in zip(terms, conv):
        key = t["name"].lower()
        ps = [p for p in papers if t["topic"] in p.get("topics", []) and (key in json.dumps(p.get("keywords") or [], ensure_ascii=False).lower())][:3]
        demos = [dm for dm in (TOPICS[t["topic"]].get("demos") or []) if dm in DEMO_INFO][:2]
        links = [f'定义见 <a href="{t["topic"]}.{t["sec"]}.html">{E(ttitle(t["topic"]))} · {E(t["sectitle"])}</a>']
        if demos:
            links.append("可视化：" + "、".join(f'<a href="lab.html#{d}">{E(DEMO_INFO[d][1])}</a>' for d in demos))
        if ps:
            links.append("论文：" + "、".join(f'<a href="paper-{p["id"]}.html">{E(str(p.get("title_zh") or p.get("title")))}</a>' for p in ps))
        dm = TMETA[t["topic"]]["domain"]
        cards.append(f'<div class="term" id="{E(t["name"])}" data-dom="{dm}" data-k="{E((t["name"] + " " + t["en"]).lower())}"><div class="term-dom">{E(DOM[dm]["title"])}</div>{c}'
                     f'<p class="src small">{"<br>".join(links)}</p></div>')
    btns = "".join(f'<button class="btn ghost" data-dom="{d["id"]}" aria-pressed="false">{E(d["title"])}</button>' for d in DOMAINS)
    body = (f'<div class="lec-head"><h1>知识索引</h1><p class="lead">全站的正式定义、数学表达与中英文术语，每条都链接到定义所在的知识页面，以及相关的可视化与论文。'
            f'需要跨专题查找时，用<a href="search.html">站内搜索</a>（支持英文术语与缩写）。</p>'
            f'<div class="pfilters">{btns}<input class="filter" id="gloss-filter" type="search" placeholder="例如：模块度、clustering、驱动节点" aria-label="筛选术语"></div></div>'
            f'<div class="gloss" id="gloss">{"".join(cards)}</div>'
            '<script>(function(){var dom="",q="";function apply(){document.querySelectorAll("#gloss .term").forEach(function(t){t.hidden=!((!dom||t.dataset.dom===dom)&&(!q||t.textContent.toLowerCase().indexOf(q)>=0))})}'
            'document.querySelectorAll(".pfilters [data-dom]").forEach(function(b){b.addEventListener("click",function(){dom=dom===b.dataset.dom?"":b.dataset.dom;document.querySelectorAll(".pfilters [data-dom]").forEach(function(x){x.setAttribute("aria-pressed",x.dataset.dom===dom)});apply()})});'
            'document.getElementById("gloss-filter").addEventListener("input",function(e){q=e.target.value.trim().toLowerCase();apply()});'
            'if(location.hash){var el=document.getElementById(decodeURIComponent(location.hash.slice(1)));if(el)el.classList.add("hit")}})();</script>')
    write_page("glossary.html", "知识索引", "生物医学网络科学术语、定义与公式索引", "glossary", body)


SYNONYMS = [["功能连接", "functional connectivity", "FC"], ["结构连接", "structural connectivity", "SC"], ["蛋白质相互作用", "protein-protein interaction", "PPI"],
            ["基因调控网络", "gene regulatory network", "GRN"], ["加权基因共表达网络分析", "WGCNA"], ["动态功能连接", "dynamic functional connectivity", "dFC"],
            ["弥散磁共振", "diffusion MRI", "dMRI", "DTI"], ["功能磁共振", "fMRI", "BOLD"], ["基于网络的统计", "network-based statistic", "NBS"],
            ["最小驱动节点集", "minimum driver node set", "MDS", "驱动节点"], ["高斯图模型", "Gaussian graphical model", "GGM", "偏相关网络"],
            ["模块度", "modularity", "Q"], ["聚集系数", "clustering coefficient", "transitivity"], ["中心性", "centrality"], ["零模型", "null model", "空模型"],
            ["小世界", "small-world", "small world"], ["无标度", "scale-free", "power law", "幂律"], ["可控性", "controllability"], ["同步", "synchronization", "Kuramoto"],
            ["网络邻近度", "network proximity"], ["药物重定位", "drug repurposing", "drug repositioning"], ["相互作用组", "interactome"]]


def build_search(papers, resources, terms):
    idx = []
    for tid, t in TOPICS.items():
        syn = " ".join(map(str, (t.get("synonyms") or []) + (t.get("keywords") or [])))
        idx.append({"t": t["title"], "u": f"{tid}.html", "k": "专题", "d": DOM[t["domain"]]["title"], "s": str(t.get("summary", "")),
                    "x": (t.get("en", "") + " " + syn + " " + plain_text(t["_special"].get("overview", ""), 600))})
        for ti, si, tx in t["_articles"]:
            idx.append({"t": ti, "u": f"{tid}.{si}.html", "k": "知识页面", "d": t["title"], "s": plain_text(tx, 110), "x": plain_text(tx, 4000)})
    for p in papers:
        idx.append({"t": str(p.get("title_zh") or p.get("title")), "u": f"paper-{p['id']}.html", "k": "论文", "d": f'{p.get("venue", "")} {p.get("year", "")}',
                    "s": str(p.get("summary", "")), "x": f'{p.get("title", "")} {p.get("authors", "")} {" ".join(map(str, p.get("keywords") or []))} ' + plain_text(p["_body"], 1500)})
    for r in resources:
        idx.append({"t": str(r.get("name")), "u": f"r-{r['id']}.html", "k": "数据与软件", "d": str(r.get("kind", "")), "s": str(r.get("summary", "")),
                    "x": " ".join(str(r.get(k, "")) for k in ("questions", "data", "tools"))})
    for t in terms:
        idx.append({"t": t["name"], "u": f"glossary.html#{t['name']}", "k": "术语", "d": ttitle(t["topic"]), "s": plain_text(t["md"], 110), "x": t["en"]})
    for dm, (tid, ti) in DEMO_INFO.items():
        idx.append({"t": ti, "u": f"lab.html#{dm}", "k": "可视化", "d": ttitle(tid), "s": "交互式可视化", "x": ""})
    for tid in TOPIC_IDS:
        for t, _ in code_cells(tid)[1]:
            idx.append({"t": t, "u": f"{tid}.html#code", "k": "代码", "d": ttitle(tid), "s": "可运行的 Python 示例", "x": ""})
    for ser in lectures_data()["series"]:
        for e in ser["episodes"]:
            if e["ready"]:
                idx.append({"t": e["full_title"] or e["title"], "u": f"courses.html#{e['id']}", "k": "课程视频", "d": f"第 {ser['n']} 讲 {ser['title']} · 第 {e['ep']} 集",
                            "s": e["points"] or e["content"], "x": e["content"] + " " + e["points"]})
    (DIST / "assets" / "search-index.json").write_text(json.dumps({"items": idx, "syn": SYNONYMS}, ensure_ascii=False), encoding="utf-8")
    body = ('<div class="lec-head"><h1>站内搜索</h1><form class="hero-search" role="search" onsubmit="return false"><input id="sq" type="search" '
            'placeholder="概念、算法、论文、数据集；支持英文与缩写，如 FC、PPI、modularity" aria-label="搜索"></form><p class="small" id="scount"></p></div>'
            '<div class="kinds" id="skinds"></div><ol class="results" id="sres"></ol><script src="assets/js/search.js"></script>')
    write_page("search.html", "站内搜索", "搜索生物医学网络科学的概念、算法、论文与数据", "", body)


# ----------------------------------------------------------------------------- lecture videos (courses.html)
def hms(sec, long=False):
    sec = int(round(sec or 0))
    h, m, s = sec // 3600, sec % 3600 // 60, sec % 60
    if long:
        return (f"{h} 小时 " if h else "") + f"{m} 分"
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def lectures_data():
    f = CONTENT / "lectures.json"
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {"series": []}


def courses_home():
    cards = []
    for s in lectures_data()["series"]:
        r = [e for e in s["episodes"] if e["ready"]]
        if not r:
            continue
        cards.append(f'<a class="cv-hcard" href="courses.html#{r[0]["id"]}"><img src="media/lectures/{r[0]["id"]}.jpg" alt="" loading="lazy" width="320" height="180">'
                     f'<span class="cv-tab-n">第 {s["n"]} 讲</span><b>{E(s["title"])}</b><small>{len(r)} 集 · {hms(sum(e.get("duration") or 0 for e in r), True)}</small></a>')
    if not cards:
        return ""
    return ('<section class="home-sec"><span class="tag">Lecture videos</span><h2>课程视频</h2><p class="small">按讲次组织的系列讲解，每集七到十二分钟，配中文字幕和文字稿。</p>'
            f'<div class="cv-hgrid">{"".join(cards)}</div><p class="small" style="margin-top:12px"><a href="courses.html">进入课程视频 →</a></p></section>')


def build_courses():
    """课程视频: the lecture series, one player with a per-lesson playlist (data: content/lectures.json, see tools/lectures.py)."""
    f = CONTENT / "lectures.json"
    if not f.exists():
        return
    data = json.loads(f.read_text(encoding="utf-8"))
    series = [s for s in data["series"] if s["episodes"]]
    ready = [e for s in series for e in s["episodes"] if e["ready"]]
    total = sum(e.get("duration") or 0 for e in ready)
    first = next((s for s in series if any(e["ready"] for e in s["episodes"])), series[0])
    e0 = next(e for e in first["episodes"] if e["ready"])

    def ep_item(s, e):
        n = f'<span class="cv-num">{e["ep"]:02d}</span>'
        if not e["ready"]:
            return (f'<li class="cv-ep soon"><span class="cv-ep-in">{n}<span class="cv-thumb blank" aria-hidden="true"></span>'
                    f'<span class="cv-ep-t">{E(e["title"])}<small>制作中</small></span></span></li>')
        return (f'<li class="cv-ep"><a class="cv-ep-in" href="#{e["id"]}" data-ep="{e["id"]}">{n}'
                f'<span class="cv-thumb"><img src="media/lectures/{e["id"]}.jpg" alt="" loading="lazy" width="320" height="180"><span class="cv-bar"><i></i></span></span>'
                f'<span class="cv-ep-t">{E(e["title"])}<small>{hms(e["duration"])}<span class="cv-done" aria-label="已看完">已看完</span></small></span></a></li>')

    tabs = []
    for s in series:
        r = [e for e in s["episodes"] if e["ready"]]
        dur = sum(e.get("duration") or 0 for e in r)
        stat = f'{len(r)} 集 · {hms(dur, True)}' + (f' · 另有 {len(s["episodes"]) - len(r)} 集制作中' if len(r) < len(s["episodes"]) else "")
        tabs.append(f'<button class="cv-tab" type="button" role="tab" data-series="{s["n"]}" aria-selected="{"true" if s is first else "false"}"'
                    f'{" disabled" if not r else ""}><span class="cv-tab-n">第 {s["n"]} 讲</span><b>{E(s["title"])}</b>'
                    f'<small>{stat}</small><span class="cv-meter" aria-hidden="true"><i></i></span></button>')

    lists = []
    for s in series:
        rel = "".join(f'<a href="{t}.html">{E(ttitle(t))}</a>' for t in s["topics"] if t in TMETA)
        lists.append(f'<div class="cv-pl" data-series="{s["n"]}"{"" if s is first else " hidden"}>'
                     f'<div class="cv-pl-head"><span class="cv-pl-n">第 {s["n"]} 讲 · {E(s["en"])}</span><h2>{E(s["title"])}</h2>'
                     f'<p>{E(s["dek"])}</p><p class="cv-pl-prog" data-prog="{s["n"]}"></p></div>'
                     f'<ol class="cv-eps">{"".join(ep_item(s, e) for e in s["episodes"])}</ol>'
                     + (f'<div class="cv-rel"><b>配套阅读</b>{rel}</div>' if rel else "") + '</div>')

    syl = []
    for s in series:
        rows = []
        for e in s["episodes"]:
            what = e["content"] or e["points"]
            t = (f'<a href="#{e["id"]}" data-ep="{e["id"]}">{E(e["full_title"] or e["title"])}</a>' if e["ready"] else E(e["full_title"] or e["title"]))
            rows.append(f'<tr><td class="cv-c-n">{e["ep"]}</td><td class="cv-c-t">{t}</td><td class="cv-c-w">{E(what)}</td>'
                        f'<td class="cv-c-p">{E(e["ppt"])}</td><td class="cv-c-d">{hms(e["duration"]) if e["ready"] else "制作中"}</td></tr>')
        syl.append(f'<h3 id="syllabus-{s["n"]}"><span>第 {s["n"]} 讲</span>{E(s["title"])}</h3><div class="table-wrap"><table class="cv-syl">'
                   '<thead><tr><th>集</th><th>标题</th><th>内容</th><th>课件页</th><th>时长</th></tr></thead>'
                   f'<tbody>{"".join(rows)}</tbody></table></div>')

    body = f"""<header class="doc-head cv-head"><div class="eyebrow"><b>课程视频</b><span>Lecture videos</span></div>
<h1>课程视频</h1>
<p class="dek">按讲次组织的系列讲解。每讲分成若干短集，每集七到十二分钟，配中文字幕和文字稿，可以按自己的节奏观看、暂停和回看。</p>
<dl class="doc-meta"><div><dt>讲次</dt><dd>{len(series)} 讲</dd></div><div><dt>已上线</dt><dd>{len(ready)} 集</dd></div>
<div><dt>总时长</dt><dd>{hms(total, True)}</dd></div><div><dt>字幕</dt><dd>中文字幕 · 文字稿</dd></div></dl></header>
<div class="cv-resume" hidden><span class="cv-resume-t"></span><a class="cv-btn primary" href="#">继续观看</a></div>
<div class="cv-tabs" role="tablist" aria-label="讲次">{"".join(tabs)}</div>
<section class="cv-stage" aria-label="播放器">
<div class="cv-main">
<div class="cv-frame"><video id="cv-video" controls preload="metadata" playsinline poster="media/lectures/{e0["id"]}.jpg">
<source src="{E(e0["src"])}" type="video/mp4"><track kind="captions" srclang="zh" label="中文字幕" src="media/lectures/{e0["id"]}.vtt"></video></div>
<div class="cv-bar-row">
<div class="cv-step"><button class="cv-btn" type="button" data-step="-1">‹ 上一集</button><button class="cv-btn" type="button" data-step="1">下一集 ›</button></div>
<div class="cv-speed" role="group" aria-label="播放速度"><span>速度</span>{"".join(f'<button type="button" data-rate="{r}"{" aria-pressed=\"true\"" if r == 1 else ""}>{r:g}×</button>' for r in (0.75, 1, 1.25, 1.5, 2))}</div>
<div class="cv-speed cv-voice" role="group" aria-label="旁白声音" hidden><span>旁白</span><button type="button" data-voice="0" aria-pressed="true">原声</button><button type="button" data-voice="1">纪录片男声</button></div>
<label class="cv-toggle"><input type="checkbox" id="cv-auto" checked> 自动播放下一集</label>
</div>
<article class="cv-info">
<div class="eyebrow cv-where"><b>第 {first["n"]} 讲 · 第 {e0["ep"]} 集</b><span>{hms(e0["duration"])}</span></div>
<h2 class="cv-title">{E(e0["full_title"])}</h2>
<p class="cv-meta"></p>
<div class="cv-points"><b>本集要点</b><p>{E(e0["points"])}</p></div>
<details class="cv-tr"><summary>文字稿</summary><div class="cv-tr-body"></div></details>
<p class="cv-keys small">键盘：空格 播放/暂停 · ← → 后退/前进 10 秒 · N 下一集</p>
</article>
</div>
<aside class="cv-side">{"".join(lists)}</aside>
</section>
<section class="block cv-syllabus" id="syllabus"><h2><span class="tag">SYLLABUS</span>全部讲次与分集</h2>{"".join(syl)}</section>
<script type="application/json" id="cv-data">{json.dumps(data, ensure_ascii=False).replace("</", "<\\/")}</script>"""
    write_page("courses.html", "课程视频", f"{SITE}系列讲解视频：{'、'.join(s['title'] for s in series)}，共 {len(ready)} 集，配中文字幕与文字稿",
               "courses", body, scripts=("site.js", "courses.js"), with_rail=False)


# ----------------------------------------------------------------------------- about & redirects
def build_about():
    body = f"""<div class="lec-head"><h1>关于本站</h1><p class="lead">{SITE}（{SITE_EN}）是一部带有交互功能的生物医学网络科学在线手册。</p></div>
<section class="block prose"><h2>内容如何组织</h2><p>内容按科学知识的内在结构组织为七个领域：网络基础理论、网络动力学与控制、脑网络与连接组、症状网络与网络精神病学、分子网络与基因调控、网络医学与药物网络、计算方法与研究规范。
每个领域包含若干专题；每个专题有一个主页（概述、视频、交互可视化、代码、论文与文献）和若干深入的知识页面。</p>
<p>对每个生物医学领域，本站尽量提供一条完整的知识链：数据怎样得到、网络怎样构建、算法怎样使用、结果怎样解释、结论有哪些证据支持。</p></section>
<section class="block prose"><h2>怎样使用</h2><ul><li>从<a href="domains.html">知识领域</a>进入，或在页面顶部直接<a href="search.html">搜索</a>概念、算法、论文和数据集（支持中英文与常见缩写）。</li>
<li><a href="courses.html">课程视频</a>按讲次组织系列讲解，可以从头系统地看；每集配中文字幕和文字稿。</li>
<li><a href="glossary.html">知识索引</a>汇集各专题的正式定义与公式。</li><li><a href="lab.html">可视化实验室</a>中的图形可以导出为 PNG 与参数文件，用于阅读和讨论。</li>
<li><a href="code.html">代码库</a>中的示例可在浏览器中直接运行，也可下载为 Notebook。</li></ul></section>
<section class="block prose"><h2>内容来源</h2><p>理论内容依据原始论文、经典综述和官方技术文档写成，每处引用都给出 DOI。外部资源版权归原作者，本站仅提供链接与介绍。发现错误欢迎指正。</p></section>"""
    write_page("about.html", "关于本站", f"{SITE}的内容组织与使用说明", "", body)


def build_redirects():
    for lid, tid in LEGACY.items():
        redirect(f"{lid}.html", f"{tid}.html", ttitle(tid))
    for name in ("guide.html", "me.html", "project.html"):
        redirect(name, "about.html" if name == "guide.html" else "index.html", SITE)


# ----------------------------------------------------------------------------- main
def main():
    global TOPICS
    DIST.mkdir(exist_ok=True)
    (DIST / "CNAME").write_text("bionetwork.xizhe.net\n")
    if (DIST / "assets").exists():
        shutil.rmtree(DIST / "assets")
    shutil.copytree(ROOT / "site" / "assets", DIST / "assets")
    if (DIST / "apps").exists():
        shutil.rmtree(DIST / "apps")
    shutil.copytree(ROOT / "site" / "apps", DIST / "apps")
    if (DIST / "media" / "lectures").exists():
        shutil.rmtree(DIST / "media" / "lectures")
    if (ROOT / "site" / "lectures").exists():
        shutil.copytree(ROOT / "site" / "lectures", DIST / "media" / "lectures")
    TOPICS = load_topics()
    papers = load_papers()
    resources = load_resources()
    gdir = DIST / "gallery"
    if gdir.exists():
        shutil.rmtree(gdir)
    gdir.mkdir()
    for png in (ROOT / "build" / "gallery").glob("*.png"):
        shutil.copy(png, gdir / png.name)
    for f in DIST.glob("*.html"):  # remove pages from older builds
        if not f.name.startswith(("paper-",)):
            f.unlink()
    for tid in TOPICS:
        print("topic", tid, len(TOPICS[tid]["_articles"]), flush=True)
        build_topic(tid, papers, resources)
        build_articles(tid, papers)
    build_domains(papers, resources)
    build_index(papers)
    build_lab()
    rows = build_notebooks()
    build_code(rows)
    build_papers(papers)
    build_resources(resources)
    terms = collect_terms()
    build_glossary(terms, papers)
    build_search(papers, resources, terms)
    build_about()
    build_courses()
    build_redirects()
    print(f"done: {len(TOPICS)} topics, {sum(len(t['_articles']) for t in TOPICS.values())} pages, {len(papers)} papers, {len(resources)} resources, {len(terms)} terms")


if __name__ == "__main__":
    main()
