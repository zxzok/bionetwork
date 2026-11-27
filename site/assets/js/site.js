/* Site behaviour: theme toggle, progress marks, quizzes (5 types), in-browser Python (Pyodide) for examples, exercises and cases. */
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

  // ---------- progress marks (rail, topic cards, lecture quiz panels) ----------
  const done = store.get("done", {});
  function markDone() {
    document.querySelectorAll("a[data-lec], summary[data-lec]").forEach((a) => { if (a.dataset.lec && done[a.dataset.lec]) a.classList.add("done"); });
  }
  markDone();

  // ---------- quizzes: single, multi, tf, numeric, code (data: window.QUIZ, built from content/quizzes) ----------
  const LEVEL = { 1: "基础", 2: "应用", 3: "综合" };
  const TYPE = { single: "单选", multi: "多选", tf: "判断", numeric: "计算", code: "读代码" };
  const letters = "ABCDEFGH";
  function isRight(q, v) {
    if (v === undefined || v === null) return false;
    if (q.t === "multi") return Array.isArray(v) && v.length === q.a.length && q.a.every((x) => v.includes(x));
    if (q.t === "numeric") return typeof v === "number" && Math.abs(v - q.a) <= (q.tol || 0) + 1e-9 * Math.max(1, Math.abs(q.a));
    return v === q.a;
  }
  function answerText(q) {
    if (q.t === "multi") return q.a.map((i) => letters[i]).join("、");
    if (q.t === "tf") return q.a ? "正确" : "错误";
    if (q.t === "numeric") return `${q.a}${q.u ? " " + q.u : ""}${q.tol ? `（允许误差 ±${q.tol}）` : ""}`;
    return letters[q.a];
  }
  function parseNum(s) {
    s = String(s).trim().replace(/，/g, ",").replace(/−/g, "-").replace(/\s+/g, "");
    if (/^-?\d+,\d+$/.test(s)) s = s.replace(",", ".");
    if (/%$/.test(s)) return NaN;
    const m = s.match(/^-?(\d+\.?\d*|\.\d+)(e-?\d+)?$/i);
    return m ? Number(s) : NaN;
  }
  document.querySelectorAll(".quiz[data-quiz]").forEach((box) => {
    const data = window.QUIZ && window.QUIZ[box.dataset.quiz];
    if (!data) return;
    const lec = box.dataset.lec, kind = box.dataset.kind;
    const key = `quiz:${lec}:${kind}`;
    const answered = store.get(key, {});
    const scoreEl = document.createElement("div");
    scoreEl.className = "score";
    function save() { store.set(key, answered); }
    function updateScore() {
      const ids = Object.keys(answered).filter((i) => data[i]);
      const right = ids.filter((i) => isRight(data[i], answered[i])).length;
      const per = {};
      data.forEach((q, i) => { if (!q.lv) return; const p = per[q.lv] || (per[q.lv] = [0, 0, 0]); p[2]++; if (i in answered) { p[1]++; if (isRight(q, answered[i])) p[0]++; } });
      const lv = Object.keys(per).sort().map((l) => `${LEVEL[l]} ${per[l][0]}/${per[l][2]}`).join(" · ");
      const pct = ids.length ? Math.round((100 * right) / ids.length) : 0;
      scoreEl.innerHTML = `<div class="score-main">已作答 <b>${ids.length}/${data.length}</b>，答对 <b>${right}</b>` +
        (ids.length ? `<span class="score-pct">${pct}%</span>` : "") + `</div>` + (lv ? `<div class="score-lv small">按难度答对：${lv}</div>` : "") +
        `<div class="score-bar" aria-hidden="true"><i style="width:${(100 * right) / data.length}%"></i><i class="miss" style="width:${(100 * (ids.length - right)) / data.length}%"></i></div>`;
      if (ids.length === data.length) {
        const pass = right >= Math.ceil(data.length * 0.7);
        const msg = document.createElement("p");
        msg.className = "score-msg " + (pass ? "ok" : "");
        msg.textContent = pass ? "全部完成，答对七成以上。" : "全部完成。可以复习答错题目的“复习”链接后重做。";
        scoreEl.appendChild(msg);
        if (kind === "post" && pass && !done[lec]) { done[lec] = true; store.set("done", done); markDone(); }
        const wrong = ids.filter((i) => !isRight(data[i], answered[i]));
        if (wrong.length) {
          const redo = document.createElement("button");
          redo.className = "btn ghost"; redo.type = "button"; redo.textContent = `只重做答错的 ${wrong.length} 题`;
          redo.addEventListener("click", () => { wrong.forEach((i) => delete answered[i]); save(); render(); box.querySelector(".q:not(.answered)")?.scrollIntoView({ behavior: "smooth", block: "center" }); });
          scoreEl.appendChild(redo);
        }
      }
      if (ids.length) {
        const reset = document.createElement("button");
        reset.className = "btn ghost"; reset.type = "button"; reset.textContent = "全部重做";
        reset.addEventListener("click", () => { for (const k in answered) delete answered[k]; save(); render(); });
        scoreEl.appendChild(reset);
      }
    }
    function render() {
      box.innerHTML = "";
      data.forEach((q, i) => {
        const el = document.createElement("div");
        el.className = "q";
        el.id = `${box.dataset.quiz}-${i + 1}`;
        const badges = `<span class="qtype">${TYPE[q.t] || "单选"}</span>` + (q.lv ? `<span class="qlv lv${q.lv}">${LEVEL[q.lv]}</span>` : "");
        el.innerHTML = `<div class="qmeta">${badges}</div><div class="stem"><span>${i + 1}.</span><div>${q.q}</div></div>` + (q.c ? `<div class="qcode">${q.c}</div>` : "") + `<div class="opts"></div>`;
        const opts = el.querySelector(".opts");
        const answer = (v) => { answered[i] = v; save(); reveal(); updateScore(); };
        if (q.t === "tf") {
          opts.classList.add("tf");
          [[true, "正确"], [false, "错误"]].forEach(([v, t]) => {
            const b = document.createElement("button");
            b.className = "opt"; b.type = "button"; b.dataset.v = String(v);
            b.innerHTML = `<span>${v ? "✓" : "✗"}</span><div>${t}</div>`;
            b.addEventListener("click", () => answer(v));
            opts.appendChild(b);
          });
        } else if (q.t === "numeric") {
          opts.classList.add("num");
          const id = el.id + "-in";
          opts.innerHTML = `<label class="sr-only" for="${id}">答案</label><input id="${id}" type="text" inputmode="decimal" autocomplete="off" placeholder="填写数值">` +
            (q.u ? `<span class="unit">${q.u}</span>` : "") + `<button class="btn" type="button">提交</button><span class="num-msg small" aria-live="polite"></span>`;
          const inp = opts.querySelector("input"), msg = opts.querySelector(".num-msg");
          const submit = () => { const v = parseNum(inp.value); if (!Number.isFinite(v)) { msg.textContent = "请填写一个数，例如 0.37 或 -2 或 1e-3"; return; } msg.textContent = ""; answer(v); };
          opts.querySelector("button").addEventListener("click", submit);
          inp.addEventListener("keydown", (e) => { if (e.key === "Enter") { e.preventDefault(); submit(); } });
        } else {
          const multi = q.t === "multi";
          if (multi) opts.classList.add("multi");
          (q.o || []).forEach((o, j) => {
            const b = document.createElement("button");
            b.className = "opt"; b.type = "button";
            if (multi) b.setAttribute("aria-pressed", "false");
            b.innerHTML = `<span>${letters[j]}.</span><div>${o}</div>`;
            b.addEventListener("click", () => {
              if (!multi) return answer(j);
              b.setAttribute("aria-pressed", String(b.getAttribute("aria-pressed") !== "true"));
              sub.disabled = !opts.querySelector('[aria-pressed="true"]');
            });
            opts.appendChild(b);
          });
          var sub;
          if (multi) {
            const row = document.createElement("div");
            row.className = "multi-row";
            row.innerHTML = `<span class="small">多选题：选出所有正确项后提交。</span>`;
            sub = document.createElement("button");
            sub.className = "btn"; sub.type = "button"; sub.textContent = "提交"; sub.disabled = true;
            sub.addEventListener("click", () => answer([...opts.querySelectorAll(".opt")].map((b, j) => (b.getAttribute("aria-pressed") === "true" ? j : -1)).filter((j) => j >= 0)));
            row.appendChild(sub);
            el.appendChild(row);
          }
        }
        function reveal() {
          if (!(i in answered)) return;
          const v = answered[i], ok = isRight(q, v);
          el.classList.add("answered", ok ? "is-right" : "is-wrong");
          el.querySelectorAll("button, input").forEach((b) => { b.disabled = true; });
          const row = el.querySelector(".multi-row"); if (row) row.hidden = true;
          if (q.t === "tf") {
            opts.querySelectorAll(".opt").forEach((b) => { const bv = b.dataset.v === "true"; if (bv === q.a) b.classList.add("right"); else if (bv === v) b.classList.add("wrong"); });
          } else if (q.t === "numeric") {
            const inp = opts.querySelector("input"); inp.value = String(v); inp.classList.add(ok ? "right" : "wrong");
          } else {
            const chosen = q.t === "multi" ? (Array.isArray(v) ? v : []) : [v];
            const truth = q.t === "multi" ? q.a : [q.a];
            opts.querySelectorAll(".opt").forEach((b, j) => {
              if (truth.includes(j)) b.classList.add(chosen.includes(j) || q.t !== "multi" ? "right" : "missed");
              else if (chosen.includes(j)) b.classList.add("wrong");
              b.setAttribute("aria-pressed", String(chosen.includes(j)));
            });
          }
          if (!el.querySelector(".explain")) {
            const ex = document.createElement("div");
            ex.className = "explain";
            const head = ok ? "<b class=\"ok\">✓ 正确。</b>" : `<b class="no">✗ 正确答案：${answerText(q)}。</b>`;
            ex.innerHTML = head + `<div>${q.x || ""}</div>` + (q.see ? `<p class="see"><a href="${q.see}">复习：${q.st || "相关知识页面"} →</a></p>` : "");
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
  const PYODIDE = "https://cdn.jsdelivr.net/pyodide/v314.0.6/full/";   // same build as JupyterLite (networkx 3.6.1)
  function loadScript(src) {
    return new Promise((res, rej) => { const s = document.createElement("script"); s.src = src; s.onload = res; s.onerror = () => rej(new Error("无法加载 " + src)); document.head.appendChild(s); });
  }
  function setStatus(t) { document.querySelectorAll(".py-status").forEach((e) => { e.textContent = t; }); }
  const EX = (() => { const el = document.getElementById("ex-data"); try { return el ? JSON.parse(el.textContent) : null; } catch (e) { return null; } })();
  let dataReady = null;
  function loadData(py) {   // data/<file> used by exercises and cases -> Pyodide FS, same relative path as in the notebooks
    if (!dataReady) {
      dataReady = (async () => {
        const files = (EX && EX.files) || [];
        if (!files.length) return;
        setStatus(`正在载入数据文件 ${files.join("、")} …`);
        const dir = py.FS.cwd() + "/data";   // FS calls need absolute paths; Python sees it as data/<file>
        py.FS.mkdirTree(dir);
        for (const f of files) {
          const r = await fetch("data/" + encodeURIComponent(f));
          if (!r.ok) throw new Error("无法下载数据文件 data/" + f);
          py.FS.writeFile(dir + "/" + f, new Uint8Array(await r.arrayBuffer()));
        }
      })().catch((e) => { dataReady = null; throw new Error(e.message || "数据文件写入失败（" + (e.name || e) + "）"); });
    }
    return dataReady;
  }
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
plt.show = lambda *a, **k: None
def __figs():
    out = []
    for n in plt.get_fignums():
        f = plt.figure(n); b = io.BytesIO(); f.savefig(b, format="png", dpi=90, bbox_inches="tight")
        out.append(base64.b64encode(b.getvalue()).decode())
    plt.close("all")
    return out
`);
        await loadData(py);
        setStatus("Python 已就绪。注意：图中中文可能显示为方框，这是浏览器环境缺少中文字体，不影响计算。");
        return py;
      })().catch((e) => { pyReady = null; setStatus("Python 环境加载失败：" + e.message + "。可以下载 Notebook 在本地 Jupyter 中运行。"); throw e; });
    }
    return pyReady;
  }
  // run one piece of code; returns {out, figs, err}
  async function pyRun(py, code) {
    let buf = "";
    py.setStdout({ batched: (s) => { buf += s + "\n"; } });
    py.setStderr({ batched: (s) => { buf += s + "\n"; } });
    let err = null;
    try {
      await py.loadPackagesFromImports(code, { messageCallback: () => {}, errorCallback: () => {} });
      await py.runPythonAsync(code);
    } catch (e) { err = String(e.message || e); }
    return { out: buf, err };
  }
  function errTail(msg) {
    const lines = msg.trim().split("\n");
    const i = lines.map((l) => /^\s*File "<exec>"/.test(l)).lastIndexOf(true);
    return (i >= 0 ? lines.slice(i) : lines.slice(-6)).join("\n");
  }
  function showFigs(py, out) {
    const figs = py.globals.get("__figs")().toJs();
    figs.forEach((b64) => { const im = new Image(); im.alt = "运行结果图"; im.src = "data:image/png;base64," + b64; out.appendChild(im); });
    return figs.length;
  }
  const setupDone = new Set();   // exercise tasks whose setup already ran in this session
  const seq = [...document.querySelectorAll(".seq-cell")];
  const seqDone = new Set();
  document.querySelectorAll(".cell").forEach((cell) => {
    const ta = cell.querySelector("textarea");
    const out = cell.querySelector(".out");
    const res = cell.querySelector(".ex-result");
    const orig = ta.value;
    const task = cell.dataset.task !== undefined && EX ? Number(cell.dataset.task) : null;
    ta.addEventListener("keydown", (e) => {
      if (e.key === "Tab") { e.preventDefault(); const s = ta.selectionStart; ta.setRangeText("    ", s, ta.selectionEnd, "end"); }
      if ((e.ctrlKey || e.metaKey) && e.key === "Enter") { e.preventDefault(); run(); }
    });
    function showErr(msg) { const sp = document.createElement("span"); sp.className = "err"; sp.textContent = errTail(msg); out.appendChild(sp); }
    async function run() {
      const btn = cell.querySelector(".run");
      btn.disabled = true; out.textContent = "运行中…"; if (res) { res.className = "ex-result"; res.textContent = ""; }
      try {
        const py = await getPy();
        await loadData(py);
        // cases: earlier cells that have not run yet run first, in order
        if (cell.classList.contains("seq-cell")) {
          for (const c of seq) { if (c === cell) break; if (!seqDone.has(c)) await c._run(); }
        }
        let text = "", ok = true;
        if (task !== null) {
          for (let j = 0; j < task; j++) {   // setups of earlier tasks, once
            const s = EX.tasks[j] && EX.tasks[j].setup;
            if (s && !setupDone.has(j)) { const r = await pyRun(py, s); if (r.err) { text += r.out; out.textContent = text; showErr(r.err); return; } setupDone.add(j); }
          }
          const s = EX.tasks[task].setup;
          if (s) { const r = await pyRun(py, s); text += r.out; if (r.err) { out.textContent = text; showErr(r.err); return; } setupDone.add(task); }
        }
        const r = await pyRun(py, ta.value);
        text += r.out;
        out.textContent = "";
        if (r.err) { out.textContent = text; showErr(r.err); ok = false; if (res) { res.className = "ex-result bad"; res.textContent = "✗ 你的代码运行出错，见下方的报错信息。"; } }
        else if (task !== null && EX.tasks[task].check) {
          const c = await pyRun(py, EX.tasks[task].check);
          if (c.err) {
            const m = c.err.match(/AssertionError:?\s*([\s\S]*)$/);
            const hint = m ? m[1].trim() : "";
            res.className = "ex-result bad";
            res.textContent = m ? "✗ 还没通过" + (hint ? "：" + hint : "。") : "✗ 核对时出错：" + errTail(c.err).split("\n").slice(-1)[0];
          } else {
            res.className = "ex-result ok";
            res.textContent = (c.out.trim().split("\n").filter((l) => l.includes("✓")).join("\n")) || "✓ 通过";
          }
        }
        if (ok) { out.textContent = text; const n = showFigs(py, out); if (!text && !n) out.textContent = "（运行完成，无输出）"; seqDone.add(cell); }
        else showFigs(py, document.createElement("div"));
      } catch (e) {
        out.innerHTML = ""; showErr(String(e.message || e));
      } finally { btn.disabled = false; }
    }
    cell._run = run;
    cell.querySelector(".run").addEventListener("click", run);
    const reset = cell.querySelector(".reset");
    if (reset) reset.addEventListener("click", () => { ta.value = orig; out.textContent = ""; if (res) { res.className = "ex-result"; res.textContent = ""; } });
    const copy = cell.querySelector(".copy");
    if (copy) copy.addEventListener("click", async () => {
      try { await navigator.clipboard.writeText(ta.value); copy.textContent = "已复制"; }
      catch (e) { ta.focus(); ta.select(); copy.textContent = "已选中，请按 Ctrl/⌘+C"; }
      setTimeout(() => { copy.textContent = "复制"; }, 2000);
    });
  });
  document.querySelectorAll(".run-all").forEach((b) => b.addEventListener("click", async () => {
    b.disabled = true;
    try { seqDone.clear(); for (const c of seq) await c._run(); } finally { b.disabled = false; }
  }));
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
      const a = document.createElement("a"); a.href = "#" + h.id; const hc = h.cloneNode(true); hc.querySelectorAll(".tag").forEach((x) => x.remove()); a.textContent = h.dataset.toc || hc.textContent.trim(); li.appendChild(a); ol.appendChild(li); });
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

// list filters (papers, resources, glossary): a search button, Enter to search, and a live result count
(() => {
  document.querySelectorAll(".pfilters input.filter[data-items]").forEach((inp) => {
    const box = document.createElement("div"); box.className = "fsearch";
    inp.replaceWith(box); box.appendChild(inp);
    const go = document.createElement("button"); go.type = "button"; go.className = "btn"; go.textContent = "搜索";
    box.appendChild(go);
    const out = document.createElement("p"); out.className = "fcount"; out.setAttribute("aria-live", "polite");
    box.closest(".lec-head, .pfilters").appendChild(out);
    const items = () => [...document.querySelectorAll(inp.dataset.items)];
    const total = items().length;
    const count = () => setTimeout(() => {
      const n = items().filter((x) => !x.hidden).length;
      out.textContent = n === total ? `共 ${total} 条` : n ? `显示 ${n} / ${total} 条` : "没有匹配的条目，换个关键词或取消筛选试试";
    }, 0);
    const run = () => { inp.dispatchEvent(new Event("input", { bubbles: true })); count(); };
    go.addEventListener("click", run);
    inp.addEventListener("keydown", (e) => { if (e.key === "Enter") { e.preventDefault(); run(); } });
    inp.addEventListener("input", count);
    document.querySelectorAll(".pfilters button[data-f], .pfilters button[data-dom]").forEach((b) => b.addEventListener("click", count));
    count();
  });
})();
