/* Site behaviour: theme toggle, progress marks, quizzes, in-browser Python (Pyodide). */
(function () {
  "use strict";
  const store = {
    get(k, d) { try { const v = localStorage.getItem("bcna:" + k); return v === null ? d : JSON.parse(v); } catch (e) { return d; } },
    set(k, v) { try { localStorage.setItem("bcna:" + k, JSON.stringify(v)); } catch (e) { /* storage unavailable */ } },
  };

  // ---------- theme ----------
  const root = document.documentElement;
  const saved = store.get("theme", null);
  if (saved) root.setAttribute("data-theme", saved);
  document.querySelectorAll(".theme-btn").forEach((b) => {
    b.addEventListener("click", () => {
      const dark = root.getAttribute("data-theme") === "dark" ||
        (!root.getAttribute("data-theme") && matchMedia("(prefers-color-scheme: dark)").matches);
      const next = dark ? "light" : "dark";
      root.setAttribute("data-theme", next);
      store.set("theme", next);
      window.dispatchEvent(new Event("themechange"));
    });
  });

  // ---------- progress marks in rail ----------
  const done = store.get("done", {});
  document.querySelectorAll(".rail a[data-lec]").forEach((a) => { if (done[a.dataset.lec]) a.classList.add("done"); });

  // ---------- quizzes ----------
  document.querySelectorAll(".quiz[data-quiz]").forEach((box) => {
    const data = window.QUIZ && window.QUIZ[box.dataset.quiz];
    if (!data) return;
    const lec = box.dataset.lec;
    const kind = box.dataset.kind;
    const key = `quiz:${lec}:${kind}`;
    const answered = store.get(key, {});
    const letters = "ABCD";
    const scoreEl = document.createElement("div");
    scoreEl.className = "score";
    function updateScore() {
      const n = Object.keys(answered).length;
      const right = Object.keys(answered).filter((i) => answered[i] === data[i].answer).length;
      scoreEl.innerHTML = `已作答 <b>${n}/${data.length}</b>，答对 <b>${right}</b>`;
      if (n === data.length) {
        const reset = document.createElement("button");
        reset.className = "btn ghost"; reset.textContent = "重做";
        reset.addEventListener("click", () => { for (const k in answered) delete answered[k]; store.set(key, {}); render(); });
        scoreEl.appendChild(reset);
        if (kind === "post" && right >= Math.ceil(data.length * 0.7)) { done[lec] = true; store.set("done", done); }
      }
    }
    function render() {
      box.innerHTML = "";
      data.forEach((q, i) => {
        const el = document.createElement("div");
        el.className = "q";
        el.innerHTML = `<div class="stem"><span>${i + 1}.</span><div>${q.q}</div></div><div class="opts"></div>`;
        const opts = el.querySelector(".opts");
        q.options.forEach((o, j) => {
          const b = document.createElement("button");
          b.className = "opt"; b.type = "button";
          b.innerHTML = `<span>${letters[j]}.</span><div>${o}</div>`;
          b.addEventListener("click", () => { answered[i] = j; store.set(key, answered); reveal(); updateScore(); });
          opts.appendChild(b);
        });
        function reveal() {
          if (!(i in answered)) return;
          opts.querySelectorAll("button").forEach((b, j) => {
            b.disabled = true;
            if (j === q.answer) b.classList.add("right");
            else if (j === answered[i]) b.classList.add("wrong");
          });
          if (!el.querySelector(".explain")) {
            const ex = document.createElement("div");
            ex.className = "explain";
            ex.innerHTML = (answered[i] === q.answer ? "<b>正确。</b>" : `<b>正确答案：${letters[q.answer]}。</b>`) + q.explain;
            el.appendChild(ex);
          }
        }
        reveal();
        box.appendChild(el);
      });
      box.appendChild(scoreEl);
      updateScore();
    }
    render();
  });

  // ---------- Python cells (Pyodide, loaded on first run) ----------
  let pyReady = null;
  const PYODIDE = "https://cdn.jsdelivr.net/pyodide/v0.27.7/full/";
  function loadScript(src) {
    return new Promise((res, rej) => { const s = document.createElement("script"); s.src = src; s.onload = res; s.onerror = () => rej(new Error("无法加载 " + src)); document.head.appendChild(s); });
  }
  function setStatus(t) { document.querySelectorAll(".py-status").forEach((e) => { e.textContent = t; }); }
  function getPy() {
    if (!pyReady) {
      pyReady = (async () => {
        setStatus("正在加载 Python 运行环境（首次约 20–40 秒）…");
        await loadScript(PYODIDE + "pyodide.js");
        const py = await window.loadPyodide({ indexURL: PYODIDE });
        setStatus("正在安装 networkx、numpy、scipy、matplotlib …");
        await py.loadPackage(["networkx", "numpy", "scipy", "matplotlib"]);
        await py.runPythonAsync(`
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt, io, base64
plt.rcParams["axes.unicode_minus"] = False
def __figs():
    out = []
    for n in plt.get_fignums():
        f = plt.figure(n); b = io.BytesIO(); f.savefig(b, format="png", dpi=90, bbox_inches="tight")
        out.append(base64.b64encode(b.getvalue()).decode())
    plt.close("all")
    return out
`);
        setStatus("Python 已就绪。注意：图中中文可能显示为方框，这是浏览器环境缺少中文字体，不影响计算。");
        return py;
      })().catch((e) => { pyReady = null; setStatus("Python 环境加载失败：" + e.message + "。可以把代码复制到本地 Jupyter 或 Colab 运行。"); throw e; });
    }
    return pyReady;
  }
  document.querySelectorAll(".cell").forEach((cell) => {
    const ta = cell.querySelector("textarea");
    const out = cell.querySelector(".out");
    const orig = ta.value;
    ta.addEventListener("keydown", (e) => {
      if (e.key === "Tab") { e.preventDefault(); const s = ta.selectionStart; ta.setRangeText("    ", s, ta.selectionEnd, "end"); }
      if ((e.ctrlKey || e.metaKey) && e.key === "Enter") { e.preventDefault(); run(); }
    });
    async function run() {
      const btn = cell.querySelector(".run");
      btn.disabled = true; out.textContent = "运行中…";
      try {
        const py = await getPy();
        let buf = "";
        py.setStdout({ batched: (s) => { buf += s + "\n"; } });
        py.setStderr({ batched: (s) => { buf += s + "\n"; } });
        await py.runPythonAsync(ta.value);
        const figs = py.globals.get("__figs")().toJs();
        out.textContent = buf || (figs.length ? "" : "（运行完成，无输出）");
        figs.forEach((b64) => { const im = new Image(); im.alt = "运行结果图"; im.src = "data:image/png;base64," + b64; out.appendChild(im); });
      } catch (e) {
        out.innerHTML = ""; const pre = document.createElement("span"); pre.className = "err"; pre.textContent = String(e.message || e).split("\n").slice(-8).join("\n"); out.appendChild(pre);
      } finally { btn.disabled = false; }
    }
    cell.querySelector(".run").addEventListener("click", run);
    const reset = cell.querySelector(".reset");
    if (reset) reset.addEventListener("click", () => { ta.value = orig; out.textContent = ""; });
    const copy = cell.querySelector(".copy");
    if (copy) copy.addEventListener("click", async () => {
      try { await navigator.clipboard.writeText(ta.value); copy.textContent = "已复制"; }
      catch (e) { ta.focus(); ta.select(); copy.textContent = "已选中，请按 Ctrl/⌘+C"; }
      setTimeout(() => { copy.textContent = "复制"; }, 2000);
    });
  });
})();

/* ---------- reader: section TOC, reading progress, notes, AI question helper ---------- */
(function () {
  "use strict";
  const lec = document.body.dataset.lec;
  const get = (k, d) => { try { const v = localStorage.getItem("bcna:" + k); return v === null ? d : JSON.parse(v); } catch (e) { return d; } };
  const set = (k, v) => { try { localStorage.setItem("bcna:" + k, JSON.stringify(v)); } catch (e) { /* unavailable */ } };

  // reading progress bar
  const bar = document.createElement("div"); bar.className = "read-progress"; document.body.appendChild(bar);
  function onScroll() { const h = document.documentElement; const p = h.scrollTop / Math.max(1, h.scrollHeight - h.clientHeight); bar.style.width = (p * 100).toFixed(1) + "%";
    if (lec && p > 0.9) { const r = get("read", {}); if (!r[lec]) { r[lec] = Date.now(); set("read", r); } } }
  addEventListener("scroll", onScroll, { passive: true }); onScroll();

  // section TOC for lecture notes
  const toc = document.querySelector(".toc[data-auto]");
  if (toc) {
    const hs = [...document.querySelectorAll("main .block > h2, #notes h2, #notes h3")].filter((h) => h.textContent.trim());
    const ol = document.createElement("ol");
    hs.forEach((h, i) => { if (!h.id) h.id = "s-" + i; const li = document.createElement("li"); li.className = h.tagName === "H3" ? "sub" : "";
      const a = document.createElement("a"); a.href = "#" + h.id; const hc = h.cloneNode(true); hc.querySelectorAll(".tag").forEach((x) => x.remove()); a.textContent = hc.textContent.trim(); li.appendChild(a); ol.appendChild(li); });
    toc.appendChild(ol);
    const links = [...toc.querySelectorAll("a")];
    const io = new IntersectionObserver((es) => { es.forEach((e) => { if (e.isIntersecting) { links.forEach((l) => l.classList.toggle("on", l.getAttribute("href") === "#" + e.target.id)); } }); }, { rootMargin: "-20% 0px -70% 0px" });
    hs.forEach((h) => io.observe(h));
  }

  // personal notes
  const notes = document.getElementById("my-notes");
  if (notes && lec) {
    notes.value = get("notes:" + lec, "");
    const st = document.getElementById("notes-status");
    let t; notes.addEventListener("input", () => { clearTimeout(t); t = setTimeout(() => { set("notes:" + lec, notes.value); if (st) st.textContent = "已保存在本浏览器 " + new Date().toLocaleTimeString(); }, 500); });
  }

  // AI question helper: compose a grounded prompt the student can paste into any AI assistant
  const MODES = {
    concept: "请作为《生物医学复杂网络分析》的概念导师，用直观例子 + 数学定义两层解释下面的内容，并指出常见误解。",
    math: "请作为数学导师，逐步引导我理解下面的推导：每一步先提示思路，等我回答后再继续，不要一次给出全部答案。",
    code: "请作为编程导师，解释下面代码的作用和可能的报错原因；先给提示，再在我要求时给出修改后的代码。",
    research: "请作为科研导师，评价下面内容涉及的研究设计、数据与统计方法，并特别检查：相关或偏相关是否被误读为因果、中心性指标是否被直接当作干预靶点、结论是否超出数据支持范围。",
  };
  const title = document.querySelector("h1") ? document.querySelector("h1").textContent.trim() : document.title;
  function compose(mode, text) {
    return `${MODES[mode]}\n\n课程：生物医学复杂网络分析 · ${title}\n来源页面：${location.href.split("#")[0]}\n\n【我想问的内容】\n${text.trim()}\n\n【我的问题】\n（在这里写下你具体不懂的地方）\n\n请区分：教材中的标准知识、原始论文的结论、以及你自己的推测；给出可核实的参考文献（作者、年份、期刊或 DOI）。`;
  }
  const askBox = document.getElementById("ask-ai");
  function showPrompt(p) {
    if (!askBox) return;
    const out = askBox.querySelector("textarea"); out.value = p; askBox.scrollIntoView({ behavior: "smooth", block: "center" }); out.focus(); out.select();
  }
  if (askBox) {
    askBox.querySelectorAll("button[data-mode]").forEach((b) => b.addEventListener("click", () => {
      const sel = String(window.getSelection() || "") || askBox.dataset.last || "（请粘贴或选中讲义中的一段文字、公式或代码）";
      showPrompt(compose(b.dataset.mode, sel));
    }));
    const cp = askBox.querySelector(".copy-prompt");
    cp.addEventListener("click", async () => { const ta = askBox.querySelector("textarea"); try { await navigator.clipboard.writeText(ta.value); cp.textContent = "已复制"; } catch (e) { ta.focus(); ta.select(); cp.textContent = "已选中，请按 Ctrl/⌘+C"; } setTimeout(() => (cp.textContent = "复制提问"), 2000); });
    // floating button on text selection inside the notes
    const fl = document.createElement("button"); fl.type = "button"; fl.className = "btn ask-float"; fl.textContent = "就这段提问"; fl.hidden = true; document.body.appendChild(fl);
    document.addEventListener("selectionchange", () => {
      const s = window.getSelection(); const txt = String(s || "").trim();
      if (!txt || txt.length < 4 || !s.rangeCount) { fl.hidden = true; return; }
      const node = s.anchorNode && (s.anchorNode.nodeType === 1 ? s.anchorNode : s.anchorNode.parentElement);
      if (!node || !node.closest(".prose, .cell, .q")) { fl.hidden = true; return; }
      const r = s.getRangeAt(0).getBoundingClientRect(); fl.style.top = (window.scrollY + r.bottom + 6) + "px"; fl.style.left = Math.max(8, Math.min(window.innerWidth - 120, r.left)) + "px"; fl.hidden = false; askBox.dataset.last = txt;
    });
    fl.addEventListener("mousedown", (e) => e.preventDefault());
    fl.addEventListener("click", () => { fl.hidden = true; showPrompt(compose(node2mode(), askBox.dataset.last)); });
    function node2mode() { const s = window.getSelection(); const n = s && s.anchorNode && (s.anchorNode.nodeType === 1 ? s.anchorNode : s.anchorNode.parentElement); if (n && n.closest(".cell")) return "code"; if (n && n.closest("math")) return "math"; return "concept"; }
  }

  // personal learning centre
  const me = document.getElementById("me-table");
  if (me) {
    const done = get("done", {}), read = get("read", {});
    me.querySelectorAll("tr[data-lec]").forEach((tr) => {
      const l = tr.dataset.lec; const ans = get(`quiz:${l}:post`, {}); const n = Object.keys(ans).length;
      const key = (window.ANSWERS || {})[l] || []; const right = Object.keys(ans).filter((i) => ans[i] === key[i]).length;
      tr.querySelector(".c-read").textContent = read[l] ? "✓" : "—";
      tr.querySelector(".c-quiz").textContent = n ? `${right}/${key.length}（已答 ${n}）` : "—";
      tr.querySelector(".c-done").innerHTML = done[l] ? '<span class="st st-ready">已过关</span>' : '<span class="st st-plan">未完成</span>';
      const nt = get("notes:" + l, ""); tr.querySelector(".c-notes").textContent = nt ? nt.slice(0, 60) + (nt.length > 60 ? "…" : "") : "—";
    });
    const all = document.getElementById("me-notes-all");
    if (all) all.addEventListener("click", async () => { const txt = [...me.querySelectorAll("tr[data-lec]")].map((tr) => { const nt = get("notes:" + tr.dataset.lec, ""); return nt ? `## ${tr.dataset.lec}\n${nt}` : ""; }).filter(Boolean).join("\n\n") || "（还没有笔记）";
      const ta = document.getElementById("me-notes-out"); ta.hidden = false; ta.value = txt; try { await navigator.clipboard.writeText(txt); all.textContent = "已复制全部笔记"; } catch (e) { ta.select(); } });
  }
})();

/* ---------- knowledge-tree drawer on narrow screens ---------- */
(function () {
  "use strict";
  const btn = document.querySelector(".menu-btn"), scrim = document.querySelector(".nav-scrim");
  if (!btn) return;
  if (!document.querySelector(".rail")) { btn.hidden = true; return; }
  const set = (open) => { document.body.classList.toggle("nav-open", open); btn.setAttribute("aria-expanded", String(open)); if (scrim) scrim.hidden = !open; };
  btn.addEventListener("click", () => set(!document.body.classList.contains("nav-open")));
  if (scrim) scrim.addEventListener("click", () => set(false));
  addEventListener("keydown", (e) => { if (e.key === "Escape") set(false); });
  // keep the current page visible inside the tree
  const cur = document.querySelector('.rail a[aria-current="page"]');
  if (cur && cur.scrollIntoView) { const r = document.querySelector(".rail"); r.scrollTop = Math.max(0, cur.offsetTop - r.clientHeight / 3); }
})();
