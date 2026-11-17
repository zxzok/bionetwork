/* 课程视频: playlist player with per-episode progress (stored only in this browser). */
(function () {
  const dataEl = document.getElementById("cv-data");
  const video = document.getElementById("cv-video");
  if (!dataEl || !video) return;
  const DATA = JSON.parse(dataEl.textContent);
  const KEY = "bcna:lectures";
  const load = () => { try { return JSON.parse(localStorage.getItem(KEY)) || {}; } catch (e) { return {}; } };
  const save = (v) => { try { localStorage.setItem(KEY, JSON.stringify(v)); } catch (e) { /* storage unavailable */ } };
  const prefs = () => { try { return JSON.parse(localStorage.getItem(KEY + ":prefs")) || {}; } catch (e) { return {}; } };
  const savePrefs = (p) => { try { localStorage.setItem(KEY + ":prefs", JSON.stringify(p)); } catch (e) { /* unavailable */ } };
  let prog = load();
  let pref = Object.assign({ rate: 1, auto: true }, prefs());

  const eps = [];
  DATA.series.forEach((s) => s.episodes.forEach((e) => { if (e.ready) eps.push(Object.assign({ series: s }, e)); }));
  const byId = Object.fromEntries(eps.map((e) => [e.id, e]));
  const fmt = (t) => { t = Math.round(t || 0); const h = Math.floor(t / 3600), m = Math.floor((t % 3600) / 60), s = t % 60;
    return (h ? h + ":" + String(m).padStart(2, "0") : m) + ":" + String(s).padStart(2, "0"); };
  const $ = (q, r) => (r || document).querySelector(q);
  const $$ = (q, r) => Array.from((r || document).querySelectorAll(q));

  let cur = null;
  let pendingSeek = 0;

  function frac(id) { const p = prog[id]; const e = byId[id]; if (!p || !e) return 0; return p.done ? 1 : Math.min(1, (p.t || 0) / (e.duration || 1)); }

  function paintProgress() {
    $$(".cv-ep-in[data-ep]").forEach((a) => {
      const id = a.dataset.ep, f = frac(id);
      a.closest(".cv-ep").classList.toggle("done", !!(prog[id] && prog[id].done));
      a.querySelector(".cv-bar i").style.width = (f * 100).toFixed(1) + "%";
    });
    DATA.series.forEach((s) => {
      const r = s.episodes.filter((e) => e.ready);
      const done = r.filter((e) => prog[e.id] && prog[e.id].done).length;
      const avg = r.length ? r.reduce((a, e) => a + frac(e.id), 0) / r.length : 0;
      const tab = $(`.cv-tab[data-series="${s.n}"] .cv-meter i`);
      if (tab) tab.style.width = (avg * 100).toFixed(1) + "%";
      const p = $(`[data-prog="${s.n}"]`);
      if (p) p.textContent = r.length ? `已看完 ${done} / ${r.length} 集` : "";
    });
  }

  function showSeries(n) {
    $$(".cv-tab").forEach((t) => t.setAttribute("aria-selected", String(t.dataset.series === String(n))));
    $$(".cv-pl").forEach((p) => { p.hidden = p.dataset.series !== String(n); });
  }

  function play(id, opts) {
    const e = byId[id];
    if (!e) return;
    opts = opts || {};
    const same = cur && cur.id === id;
    cur = e;
    showSeries(e.series.n);
    $$(".cv-ep").forEach((li) => li.classList.toggle("on", !!$(`[data-ep="${id}"]`, li)));
    if (!same) {
      video.pause();
      video.poster = `media/lectures/${id}.jpg`;
      video.innerHTML = "";
      const src = document.createElement("source"); src.src = e.src; src.type = "video/mp4";
      const tr = document.createElement("track"); tr.kind = "captions"; tr.srclang = "zh"; tr.label = "中文字幕"; tr.src = `media/lectures/${id}.vtt`;
      video.append(src, tr);
      video.load();
      const p = prog[id];
      pendingSeek = p && !p.done && p.t > 5 ? p.t : 0;
    }
    video.playbackRate = pref.rate;
    // info panel
    $(".cv-where").innerHTML = `<b>第 ${e.series.n} 讲 · 第 ${e.ep} 集</b><span>${fmt(e.duration)}</span>`;
    $(".cv-title").textContent = e.full_title || e.title;
    const meta = [];
    if (e.ppt) meta.push(`对应课件第 ${e.ppt} 页`);
    if (e.content) meta.push(e.content);
    $(".cv-meta").textContent = meta.join("　·　");
    $(".cv-meta").hidden = !meta.length;
    $(".cv-points p").textContent = e.points || "";
    $(".cv-points").hidden = !e.points;
    const tr = $(".cv-tr");
    tr.open = false; tr.dataset.id = id; $(".cv-tr-body").innerHTML = "";
    $$('[data-step]').forEach((b) => {
      const i = eps.indexOf(e) + Number(b.dataset.step);
      b.disabled = i < 0 || i >= eps.length;
    });
    if (!opts.nohash && location.hash !== "#" + id) history.replaceState(null, "", "#" + id);
    document.title = `${e.title} · 第 ${e.series.n} 讲 · 课程视频 · 生物医学网络科学`;
    if (opts.scroll) $(".cv-stage").scrollIntoView({ behavior: "smooth", block: "start" });
    if (opts.autoplay) video.play().catch(() => { /* needs a user gesture */ });
    $(".cv-resume").hidden = true;
  }

  video.addEventListener("loadedmetadata", () => {
    if (pendingSeek) { video.currentTime = pendingSeek; pendingSeek = 0; }
    video.playbackRate = pref.rate;
  });
  let lastSave = 0;
  video.addEventListener("timeupdate", () => {
    if (!cur || !video.duration) return;
    const now = Date.now();
    if (now - lastSave < 3000) return;
    lastSave = now;
    const p = prog[cur.id] || {};
    p.t = video.currentTime;
    if (video.currentTime / video.duration > 0.92) p.done = true;
    p.at = now;
    prog[cur.id] = p; prog._last = cur.id; save(prog); paintProgress();
  });
  video.addEventListener("ended", () => {
    if (!cur) return;
    prog[cur.id] = Object.assign(prog[cur.id] || {}, { done: true, t: 0, at: Date.now() }); save(prog); paintProgress();
    const i = eps.indexOf(cur);
    if (pref.auto && i + 1 < eps.length) play(eps[i + 1].id, { autoplay: true });
  });

  // transcript, loaded when opened
  $(".cv-tr").addEventListener("toggle", (ev) => {
    const d = ev.currentTarget, body = $(".cv-tr-body");
    if (!d.open || body.childElementCount) return;
    fetch(`media/lectures/${d.dataset.id}.txt`).then((r) => r.ok ? r.text() : Promise.reject())
      .then((t) => { body.innerHTML = ""; t.split(/\n+/).filter((x) => x.trim()).forEach((x) => { const p = document.createElement("p"); p.textContent = x; body.append(p); }); })
      .catch(() => { body.textContent = "文字稿暂时无法加载。"; });
  });

  // controls
  $$(".cv-tab").forEach((t) => t.addEventListener("click", () => {
    const n = Number(t.dataset.series);
    const s = DATA.series.find((x) => x.n === n);
    const r = s.episodes.filter((e) => e.ready);
    const next = r.find((e) => !(prog[e.id] && prog[e.id].done)) || r[0];
    showSeries(n);
    if (next && (!cur || cur.series.n !== n)) play(next.id);
  }));
  document.addEventListener("click", (ev) => {
    const a = ev.target.closest("a[data-ep]");
    if (!a) return;
    ev.preventDefault();
    play(a.dataset.ep, { autoplay: true, scroll: !a.closest(".cv-side") || window.innerWidth < 1000 });
  });
  $$("[data-step]").forEach((b) => b.addEventListener("click", () => {
    const i = eps.indexOf(cur) + Number(b.dataset.step);
    if (eps[i]) play(eps[i].id, { autoplay: true });
  }));
  const rateBtns = $$(".cv-speed button");
  const paintRate = () => rateBtns.forEach((b) => b.setAttribute("aria-pressed", String(Number(b.dataset.rate) === pref.rate)));
  rateBtns.forEach((b) => b.addEventListener("click", () => { pref.rate = Number(b.dataset.rate); video.playbackRate = pref.rate; savePrefs(pref); paintRate(); }));
  video.addEventListener("ratechange", () => { if (video.playbackRate !== pref.rate) { pref.rate = video.playbackRate; savePrefs(pref); paintRate(); } });
  const auto = $("#cv-auto");
  auto.checked = pref.auto;
  auto.addEventListener("change", () => { pref.auto = auto.checked; savePrefs(pref); });
  paintRate();

  document.addEventListener("keydown", (ev) => {
    if (ev.target.closest("input, textarea, select, [contenteditable]") || ev.metaKey || ev.ctrlKey || ev.altKey) return;
    const k = ev.key;
    if (k === " " && ev.target !== video && !ev.target.closest("button, a, summary")) { ev.preventDefault(); video.paused ? video.play() : video.pause(); }
    else if ((k === "ArrowRight" || k === "ArrowLeft") && ev.target !== video) { ev.preventDefault(); video.currentTime = Math.max(0, video.currentTime + (k === "ArrowRight" ? 10 : -10)); }
    else if (k === "n" || k === "N") { const i = eps.indexOf(cur); if (eps[i + 1]) play(eps[i + 1].id, { autoplay: true }); }
  });

  window.addEventListener("hashchange", () => { const id = location.hash.slice(1); if (byId[id] && (!cur || cur.id !== id)) play(id, { scroll: true }); });

  // start: the episode in the link, otherwise the first one, with a "continue" prompt for the last one watched
  const fromHash = location.hash.slice(1);
  if (byId[fromHash]) play(fromHash);
  else {
    const last = byId[prog._last];
    if (last && prog[last.id] && (prog[last.id].t > 5 || prog[last.id].done)) {
      const p = prog[last.id];
      const i = eps.indexOf(last);
      const target = p.done && eps[i + 1] ? eps[i + 1] : last;
      const box = $(".cv-resume");
      $(".cv-resume-t", box).innerHTML = p.done && target !== last
        ? `上次看完了 <b>第 ${last.series.n} 讲 第 ${last.ep} 集 ${last.title}</b>，下一集是 <b>${target.title}</b>`
        : `上次看到 <b>第 ${last.series.n} 讲 第 ${last.ep} 集 ${last.title}</b> 的 ${fmt(p.t)}`;
      const a = $("a", box);
      a.href = "#" + target.id;
      a.addEventListener("click", (ev) => { ev.preventDefault(); play(target.id, { autoplay: true, scroll: true }); });
      play(target.id, { nohash: true });
      box.hidden = false;
    } else play(eps[0].id, { nohash: true });
  }
  paintProgress();
})();
