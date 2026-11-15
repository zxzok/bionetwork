/* Site search: Chinese/English terms with synonym expansion. Index built by build.py. */
(function () {
  "use strict";
  const input = document.getElementById("sq"), list = document.getElementById("sres"), count = document.getElementById("scount"), kindsBox = document.getElementById("skinds");
  let DATA = null, kind = "";
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  function expand(q) {
    const terms = new Set([q]);
    (DATA.syn || []).forEach((g) => { if (g.some((w) => w.toLowerCase() === q || (q.length > 1 && w.toLowerCase().includes(q)))) g.forEach((w) => terms.add(w.toLowerCase())); });
    return [...terms];
  }
  function score(it, words) {
    const t = it.t.toLowerCase(), x = (it.x || "").toLowerCase(), s = (it.s || "").toLowerCase();
    let sc = 0;
    for (const group of words) {
      let best = 0;
      for (const w of group) {
        if (!w) continue;
        if (t === w) best = Math.max(best, 100);
        else if (t.includes(w)) best = Math.max(best, 60);
        else if (s.includes(w)) best = Math.max(best, 25);
        else if (x.includes(w)) best = Math.max(best, 12);
      }
      if (!best) return 0;
      sc += best;
    }
    const boost = { "专题": 8, "术语": 6, "知识页面": 4, "论文": 2 }[it.k] || 0;
    return sc + boost;
  }
  function snippet(it, words) {
    const src = it.x || it.s || "";
    const flat = words.flat().filter(Boolean);
    const low = src.toLowerCase();
    let pos = -1;
    for (const w of flat) { pos = low.indexOf(w); if (pos >= 0) break; }
    if (pos < 0) return esc(it.s || "");
    const a = Math.max(0, pos - 40), piece = src.slice(a, pos + 90);
    let h = esc(piece);
    flat.forEach((w) => { if (w.length > 0) h = h.replace(new RegExp(w.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "gi"), (m) => "<mark>" + m + "</mark>"); });
    return (a ? "…" : "") + h + "…";
  }
  function run() {
    const q = input.value.trim().toLowerCase();
    try { history.replaceState(null, "", q ? "?q=" + encodeURIComponent(q) : "search.html"); } catch (e) { /* ignore */ }
    if (!q) { list.innerHTML = ""; count.textContent = ""; kindsBox.innerHTML = ""; return; }
    const words = q.split(/\s+/).map(expand);
    let hits = DATA.items.map((it) => [score(it, words), it]).filter((p) => p[0] > 0).sort((a, b) => b[0] - a[0]);
    const kinds = {};
    hits.forEach(([, it]) => { kinds[it.k] = (kinds[it.k] || 0) + 1; });
    kindsBox.innerHTML = ['<button class="btn ghost" data-k="" aria-pressed="' + (!kind) + '">全部 ' + hits.length + "</button>"]
      .concat(Object.keys(kinds).map((k) => '<button class="btn ghost" data-k="' + esc(k) + '" aria-pressed="' + (kind === k) + '">' + esc(k) + " " + kinds[k] + "</button>")).join("");
    kindsBox.querySelectorAll("button").forEach((b) => b.addEventListener("click", () => { kind = b.dataset.k; run(); }));
    if (kind) hits = hits.filter(([, it]) => it.k === kind);
    count.textContent = hits.length ? "" : "没有找到结果。试试更短的词，或英文术语。";
    list.innerHTML = hits.slice(0, 80).map(([, it]) => '<li><a href="' + esc(it.u) + '"><span class="rk">' + esc(it.k) + "</span><b>" + esc(it.t) + '</b><span class="rd">' + esc(it.d || "") +
      '</span></a><p>' + snippet(it, words) + "</p></li>").join("");
  }
  fetch("assets/search-index.json").then((r) => r.json()).then((d) => {
    DATA = d;
    const q = new URLSearchParams(location.search).get("q") || "";
    input.value = q; run();
    let t; input.addEventListener("input", () => { clearTimeout(t); t = setTimeout(run, 120); });
    input.focus();
  }).catch(() => { count.textContent = "搜索索引加载失败：请通过网页服务器（而不是直接双击文件）打开本站。"; });
})();
