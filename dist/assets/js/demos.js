/* Interactive demos. Each demo mounts into <div class="demo" data-demo="id">. Plain canvas, no libraries. */
(function () {
  "use strict";
  // ------------------------------------------------------------------ helpers
  const css = (n) => getComputedStyle(document.documentElement).getPropertyValue(n).trim() || "#888";
  const C = () => ({ ink: css("--ink"), ink2: css("--ink-2"), line: css("--line"), acc: css("--accent"), hub: css("--hub"),
    bio: css("--bio"), bad: css("--bad"), ok: css("--ok"), paper: css("--paper"), sheet: css("--sheet") });
  const PAL = ["#3b5bdb", "#e8590c", "#2f9e44", "#c2255c", "#7048e8", "#0c8599"];
  function rng(seed) { let s = seed >>> 0 || 1; return () => { s ^= s << 13; s >>>= 0; s ^= s >> 17; s ^= s << 5; s >>>= 0; return s / 4294967296; }; }
  function gauss(r) { let u = 0, v = 0; while (u === 0) u = r(); v = r(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); }
  function canvas(parent, w, h) {
    const c = document.createElement("canvas"); const d = window.devicePixelRatio || 1;
    c.width = w * d; c.height = h * d; c.style.width = w + "px"; c.style.aspectRatio = w + "/" + h;
    const g = c.getContext("2d"); g.scale(d, d); c._w = w; c._h = h; parent.appendChild(c); return [c, g];
  }
  function el(tag, attrs, html) { const e = document.createElement(tag); Object.assign(e, attrs || {}); if (html !== undefined) e.innerHTML = html; return e; }
  function slider(parent, label, min, max, step, val, fmt, on) {
    const id = "s" + Math.random().toString(36).slice(2, 8);
    const lab = el("label", {}, `${label} `); const inp = el("input", { type: "range", min, max, step, value: val, id });
    const ro = el("span", { className: "readout" }); lab.htmlFor = id; lab.appendChild(inp); lab.appendChild(ro); parent.appendChild(lab);
    const upd = () => { ro.textContent = fmt(+inp.value); on(+inp.value); }; inp.addEventListener("input", upd); ro.textContent = fmt(+val);
    return inp;
  }
  function button(parent, text, on, ghost) { const b = el("button", { type: "button", className: "btn" + (ghost ? " ghost" : "") }, text); b.addEventListener("click", on); parent.appendChild(b); return b; }
  function controls(root) { const d = el("div", { className: "controls" }); root.appendChild(d); return d; }
  function adjFrom(n, edges) { const a = Array.from({ length: n }, () => []); edges.forEach(([u, v]) => { a[u].push(v); a[v].push(u); }); return a; }
  function bfs(adj, s) { const d = new Array(adj.length).fill(-1); d[s] = 0; const q = [s]; for (let i = 0; i < q.length; i++) { const u = q[i]; for (const v of adj[u]) if (d[v] < 0) { d[v] = d[u] + 1; q.push(v); } } return d; }
  function comps(adj, alive) { const n = adj.length, lab = new Array(n).fill(-1); let k = 0; for (let s = 0; s < n; s++) { if (lab[s] >= 0 || (alive && !alive[s])) continue; const q = [s]; lab[s] = k; for (let i = 0; i < q.length; i++) for (const v of adj[q[i]]) if (lab[v] < 0 && (!alive || alive[v])) { lab[v] = k; q.push(v); } k++; } return lab; }
  function giantSet(adj, alive) { const lab = comps(adj, alive); const cnt = {}; lab.forEach((l) => { if (l >= 0) cnt[l] = (cnt[l] || 0) + 1; }); let best = -1, bs = 0; for (const l in cnt) if (cnt[l] > bs) { bs = cnt[l]; best = +l; } return [lab.map((l) => l === best), bs]; }
  function clustering(adj) { let s = 0; const n = adj.length; for (let i = 0; i < n; i++) { const nb = adj[i], k = nb.length; if (k < 2) continue; const set = new Set(nb); let e = 0; for (const u of nb) for (const v of adj[u]) if (set.has(v)) e++; s += e / (k * (k - 1)); } return s / n; }
  function avgPath(adj) { let tot = 0, cnt = 0; for (let s = 0; s < adj.length; s++) { const d = bfs(adj, s); for (const x of d) if (x > 0) { tot += x; cnt++; } } return cnt ? tot / cnt : 0; }
  function ring(n, k) { const e = []; for (let i = 0; i < n; i++) for (let j = 1; j <= k / 2; j++) e.push([i, (i + j) % n]); return e; }
  function wsEdges(n, k, beta, r) { const set = new Set(); const key = (a, b) => (a < b ? a + "," + b : b + "," + a); const base = ring(n, k); base.forEach(([a, b]) => set.add(key(a, b)));
    const out = []; for (const [a, b] of base) { if (r() < beta) { let c, t = 0; do { c = Math.floor(r() * n); t++; } while ((c === a || set.has(key(a, c))) && t < 50); if (t < 50) { set.delete(key(a, b)); set.add(key(a, c)); out.push([a, c]); continue; } } out.push([a, b]); } return out; }
  function baEdges(n, m, r) { const e = [], targets = []; for (let i = 0; i <= m; i++) for (let j = 0; j < i; j++) { e.push([i, j]); targets.push(i, j); }
    for (let v = m + 1; v < n; v++) { const ch = new Set(); while (ch.size < m) ch.add(targets[Math.floor(r() * targets.length)]); for (const u of ch) { e.push([v, u]); targets.push(v, u); } } return e; }
  function erEdges(n, kmean, r) { const p = kmean / (n - 1), e = []; for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++) if (r() < p) e.push([i, j]); return e; }
  function layout(n, edges, w, h, iters, seed, init) {
    const r = rng(seed || 7); const P = init ? init.map((p) => [...p]) : Array.from({ length: n }, () => [w * (0.15 + 0.7 * r()), h * (0.15 + 0.7 * r())]);
    const k = Math.sqrt((w * h) / n) * 0.75; let t = w / 10;
    for (let it = 0; it < iters; it++) {
      const D = P.map(() => [0, 0]);
      for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++) { let dx = P[i][0] - P[j][0], dy = P[i][1] - P[j][1]; let d = Math.hypot(dx, dy) || 0.01; const f = (k * k) / d; dx /= d; dy /= d; D[i][0] += dx * f; D[i][1] += dy * f; D[j][0] -= dx * f; D[j][1] -= dy * f; }
      for (const [a, b] of edges) { let dx = P[a][0] - P[b][0], dy = P[a][1] - P[b][1]; const d = Math.hypot(dx, dy) || 0.01; const f = (d * d) / k; dx /= d; dy /= d; D[a][0] -= dx * f; D[a][1] -= dy * f; D[b][0] += dx * f; D[b][1] += dy * f; }
      for (let i = 0; i < n; i++) { const d = Math.hypot(D[i][0], D[i][1]) || 1; P[i][0] += (D[i][0] / d) * Math.min(d, t); P[i][1] += (D[i][1] / d) * Math.min(d, t); P[i][0] += (w / 2 - P[i][0]) * 0.01; P[i][1] += (h / 2 - P[i][1]) * 0.01; }
      t *= 0.96;
    }
    // fit
    let x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity; P.forEach(([x, y]) => { x0 = Math.min(x0, x); x1 = Math.max(x1, x); y0 = Math.min(y0, y); y1 = Math.max(y1, y); });
    const s = Math.min((w - 30) / (x1 - x0 || 1), (h - 30) / (y1 - y0 || 1)); return P.map(([x, y]) => [15 + (x - x0) * s + (w - 30 - (x1 - x0) * s) / 2, 15 + (y - y0) * s + (h - 30 - (y1 - y0) * s) / 2]);
  }
  function circ(n, w, h, rr) { const R = rr || Math.min(w, h) * 0.42; return Array.from({ length: n }, (_, i) => [w / 2 + R * Math.cos(-Math.PI / 2 + (2 * Math.PI * i) / n), h / 2 + R * Math.sin(-Math.PI / 2 + (2 * Math.PI * i) / n)]); }
  function drawNet(g, P, edges, opt) {
    const c = C(); opt = opt || {};
    g.lineWidth = opt.lw || 1; edges.forEach((e, i) => { g.strokeStyle = (opt.ecol && opt.ecol(e, i)) || c.line; g.beginPath(); g.moveTo(...P[e[0]]); g.lineTo(...P[e[1]]); g.stroke(); });
    P.forEach((p, i) => { if (opt.hide && opt.hide(i)) return; g.fillStyle = (opt.ncol && opt.ncol(i)) || c.acc; g.beginPath(); g.arc(p[0], p[1], (opt.size && opt.size(i)) || 4, 0, 7); g.fill(); });
  }
  function clear(g, cv) { g.clearRect(0, 0, cv._w, cv._h); }
  function axes(g, x, y, w, h, xr, yr, opt) {
    const c = C(); opt = opt || {}; g.strokeStyle = c.ink2; g.lineWidth = 1; g.beginPath(); g.moveTo(x, y); g.lineTo(x, y + h); g.lineTo(x + w, y + h); g.stroke();
    g.fillStyle = c.ink2; g.font = "11px sans-serif"; g.textAlign = "center";
    if (opt.xl) g.fillText(opt.xl, x + w / 2, y + h + 26); g.save(); g.translate(x - 30, y + h / 2); g.rotate(-Math.PI / 2); if (opt.yl) g.fillText(opt.yl, 0, 0); g.restore();
    const fx = (v) => x + ((opt.logx ? Math.log10(v) : v) - xr[0]) / (xr[1] - xr[0]) * w; const fy = (v) => y + h - ((opt.logy ? Math.log10(v) : v) - yr[0]) / (yr[1] - yr[0]) * h;
    (opt.xt || []).forEach((t) => { g.fillText(String(t), fx(t), y + h + 13); }); g.textAlign = "right"; (opt.yt || []).forEach((t) => { g.fillText(String(t), x - 4, fy(t) + 4); });
    return [fx, fy];
  }
  function line(g, pts, fx, fy, col, lw) { g.strokeStyle = col; g.lineWidth = lw || 2; g.beginPath(); pts.forEach(([a, b], i) => (i ? g.lineTo(fx(a), fy(b)) : g.moveTo(fx(a), fy(b)))); g.stroke(); }
  function txt(g, s, x, y, col, size, align) { g.fillStyle = col || C().ink; g.font = (size || 13) + "px sans-serif"; g.textAlign = align || "left"; g.fillText(s, x, y); }

  const D = {};

  // ------------------------------------------------------------------ graph_matrix
  D.graph_matrix = (root) => {
    const n = 7; let edges = [[0, 1], [1, 2], [0, 2], [2, 3], [3, 4], [4, 5], [5, 6], [6, 3]]; let sel = -1;
    const row = el("div", { className: "demo-row" }); root.appendChild(row);
    const [cv, g] = canvas(row, 320, 280); const [cm, gm] = canvas(row, 300, 280);
    const P = circ(n, 320, 280, 110);
    const ro = el("p", { className: "readout" }); root.appendChild(ro);
    function has(a, b) { return edges.findIndex(([u, v]) => (u === a && v === b) || (u === b && v === a)); }
    function draw() {
      const c = C(); clear(g, cv); clear(gm, cm);
      drawNet(g, P, edges, { lw: 2.2, ecol: () => c.ink2, size: () => 14, ncol: (i) => (i === sel ? c.hub : c.acc) });
      P.forEach((p, i) => txt(g, String(i + 1), p[0], p[1] + 4, "#fff", 12, "center"));
      const s = 32, x0 = 50, y0 = 30;
      for (let i = 0; i < n; i++) { txt(gm, String(i + 1), x0 + i * s + s / 2, y0 - 8, c.ink2, 12, "center"); txt(gm, String(i + 1), x0 - 10, y0 + i * s + s / 2 + 4, c.ink2, 12, "right");
        for (let j = 0; j < n; j++) { const on = has(i, j) >= 0; gm.fillStyle = on ? c.acc : c.sheet; gm.strokeStyle = c.line; gm.fillRect(x0 + j * s, y0 + i * s, s - 2, s - 2); gm.strokeRect(x0 + j * s, y0 + i * s, s - 2, s - 2); txt(gm, on ? "1" : "0", x0 + j * s + s / 2 - 1, y0 + i * s + s / 2 + 4, on ? "#fff" : c.ink2, 12, "center"); } }
      const deg = Array.from({ length: n }, (_, i) => edges.filter((e) => e.includes(i)).length);
      ro.textContent = `边数 E = ${edges.length}    度序列 = [${deg.join(", ")}]    平均度 = ${(2 * edges.length / n).toFixed(2)}    度之和 = ${deg.reduce((a, b) => a + b, 0)} = 2E`;
    }
    cv.addEventListener("click", (ev) => { const b = cv.getBoundingClientRect(); const x = (ev.clientX - b.left) * cv._w / b.width, y = (ev.clientY - b.top) * cv._h / b.height;
      const i = P.findIndex((p) => Math.hypot(p[0] - x, p[1] - y) < 18); if (i < 0) { sel = -1; draw(); return; }
      if (sel < 0) sel = i; else if (sel === i) sel = -1; else { const k = has(sel, i); if (k >= 0) edges.splice(k, 1); else edges.push([sel, i]); sel = -1; } draw(); });
    draw(); window.addEventListener("themechange", draw);
  };

  // ------------------------------------------------------------------ er
  D.er = (root) => {
    const n = 90, r = rng(3); const U = []; for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++) U.push([i, j, r()]);
    const P = Array.from({ length: n }, () => [20 + 340 * r(), 20 + 260 * r()]);
    const ctl = controls(root); const row = el("div", { className: "demo-row" }); root.appendChild(row);
    const [cv, g] = canvas(row, 380, 300); const [cp, gp] = canvas(row, 300, 300); const ro = el("p", { className: "readout" }); root.appendChild(ro);
    const curve = []; for (let k = 0; k <= 60; k++) { const p = (k / 60) * 4 / (n - 1); const e = U.filter((u) => u[2] < p); curve.push([(2 * e.length) / n, giantSet(adjFrom(n, e))[1] / n]); }
    let pval = 0.5 / (n - 1);
    function draw() { const c = C(); const e = U.filter((u) => u[2] < pval); const adj = adjFrom(n, e); const [gs, sz] = giantSet(adj);
      clear(g, cv); drawNet(g, P, e, { ecol: (ed) => (gs[ed[0]] && sz > 2 ? c.hub : c.line), ncol: (i) => (gs[i] && sz > 2 ? c.hub : c.acc), size: () => 4 });
      clear(gp, cp); const [fx, fy] = axes(gp, 45, 15, 235, 235, [0, 4], [0, 1], { xl: "平均度 ⟨k⟩", yl: "巨分支占比", xt: [0, 1, 2, 3, 4], yt: [0, 0.5, 1] });
      line(gp, curve, fx, fy, c.ink2, 1.5); const km = (2 * e.length) / n; gp.fillStyle = c.hub; gp.beginPath(); gp.arc(fx(km), fy(sz / n), 6, 0, 7); gp.fill();
      gp.setLineDash([4, 4]); gp.strokeStyle = c.ink2; gp.beginPath(); gp.moveTo(fx(1), fy(0)); gp.lineTo(fx(1), fy(1)); gp.stroke(); gp.setLineDash([]);
      ro.textContent = `p = ${pval.toFixed(4)}   边数 = ${e.length}   ⟨k⟩ = ${km.toFixed(2)}   最大连通分支 = ${sz}/${n}`; }
    slider(ctl, "连边概率 p", 0, 4 / (n - 1), 0.0005, pval, (v) => v.toFixed(4), (v) => { pval = v; draw(); });
    draw(); window.addEventListener("themechange", draw);
  };

  // ------------------------------------------------------------------ ws
  D.ws = (root) => {
    const n = 40, k = 4; const ctl = controls(root); const row = el("div", { className: "demo-row" }); root.appendChild(row);
    const [cv, g] = canvas(row, 320, 300); const [cp, gp] = canvas(row, 320, 300); const ro = el("p", { className: "readout" }); root.appendChild(ro);
    const P = circ(n, 320, 300, 125);
    const N2 = 120, K2 = 6, bs = [0.0001, 0.0003, 0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 1];
    const a0 = adjFrom(N2, ring(N2, K2)); const C0 = clustering(a0), L0 = avgPath(a0);
    const curve = bs.map((b) => { let cc = 0, ll = 0; for (let s = 0; s < 3; s++) { const a = adjFrom(N2, wsEdges(N2, K2, b, rng(11 + s))); cc += clustering(a); ll += avgPath(a); } return [b, cc / 3 / C0, ll / 3 / L0]; });
    let lb = -2, seed = 5;
    function draw() { const c = C(); const beta = Math.pow(10, lb); const e = wsEdges(n, k, beta, rng(seed)); const base = new Set(ring(n, k).map(([a, b]) => a + "," + b));
      clear(g, cv); drawNet(g, P, e, { lw: 1.4, ecol: ([a, b]) => (base.has(a + "," + b) || base.has(b + "," + a) ? c.ink2 : c.hub), size: () => 4.5 });
      const adj = adjFrom(n, e); const cc = clustering(adj); const [, gsz] = giantSet(adj); const L = gsz === n ? avgPath(adj) : NaN;
      clear(gp, cp); const [fx, fy] = axes(gp, 45, 15, 255, 240, [-4, 0], [0, 1.05], { logx: true, xl: "重连概率 β（对数）", yl: "相对值", xt: [0.0001, 0.001, 0.01, 0.1, 1], yt: [0, 0.5, 1] });
      line(gp, curve.map((d) => [d[0], d[1]]), fx, fy, c.acc, 2.2); line(gp, curve.map((d) => [d[0], d[2]]), fx, fy, c.bad, 2.2);
      gp.strokeStyle = c.hub; gp.lineWidth = 2; gp.beginPath(); gp.moveTo(fx(beta), fy(0)); gp.lineTo(fx(beta), fy(1.05)); gp.stroke();
      txt(gp, "C(β)/C(0)", 230, 40, c.acc, 12); txt(gp, "L(β)/L(0)", 230, 200, c.bad, 12);
      ro.textContent = `β = ${beta.toFixed(4)}   本图 N=${n}, K=${k}：聚集系数 C = ${cc.toFixed(3)}   平均路径 L = ${isNaN(L) ? "（不连通）" : L.toFixed(2)}   右图为 N=${N2} 网络 3 次平均`; }
    slider(ctl, "log₁₀ β", -4, 0, 0.05, lb, (v) => "β = " + Math.pow(10, v).toFixed(4), (v) => { lb = v; draw(); });
    button(ctl, "换一组随机数", () => { seed++; draw(); }, true);
    draw(); window.addEventListener("themechange", draw);
  };

  // ------------------------------------------------------------------ ba
  D.ba = (root) => {
    const ctl = controls(root); const row = el("div", { className: "demo-row" }); root.appendChild(row);
    const [cv, g] = canvas(row, 360, 320); const [cp, gp] = canvas(row, 280, 320); const ro = el("p", { className: "readout" }); root.appendChild(ro);
    let r, edges, targets, P, n, m = 2, timer = null;
    function reset() { r = rng(Date.now() % 1000 + 1); edges = [[0, 1], [1, 2], [0, 2]]; targets = [0, 1, 1, 2, 0, 2]; n = 3; P = [[180, 140], [160, 180], [200, 180]]; draw(); }
    function add(k) { for (let t = 0; t < k; t++) { const ch = new Set(); while (ch.size < m) ch.add(targets[Math.floor(r() * targets.length)]); const nb = [...ch];
        P.push([P[nb[0]][0] + (r() - 0.5) * 30, P[nb[0]][1] + (r() - 0.5) * 30]); nb.forEach((u) => { edges.push([n, u]); targets.push(n, u); }); n++; }
      P = layout(n, edges, 360, 320, 25, 1, P); draw(); }
    function draw() { const c = C(); const deg = new Array(n).fill(0); edges.forEach(([a, b]) => { deg[a]++; deg[b]++; });
      clear(g, cv); drawNet(g, P, edges, { ecol: (e) => (e[0] === n - 1 ? c.hub : c.line), size: (i) => 2.5 + Math.sqrt(deg[i]) * 1.6, ncol: (i) => (i === n - 1 ? c.hub : deg[i] >= 12 ? c.bad : c.acc) });
      clear(gp, cp); const kmax = Math.max(...deg); const [fx, fy] = axes(gp, 45, 15, 215, 255, [0, 2], [-2.5, 0], { logx: true, logy: true, xl: "度 k（对数）", yl: "P(K ≥ k)（对数）", xt: [1, 10, 100], yt: [0.01, 0.1, 1] });
      const ks = [...new Set(deg)].sort((a, b) => a - b); const pts = ks.map((k) => [k, deg.filter((d) => d >= k).length / n]).filter((p) => p[1] >= 0.003);
      gp.fillStyle = c.hub; pts.forEach(([k, p]) => { gp.beginPath(); gp.arc(fx(k), fy(p), 3, 0, 7); gp.fill(); });
      ro.textContent = `节点数 ${n}   边数 ${edges.length}   最大度 ${kmax}   橙色：最新加入的节点及其连边；红色：度 ≥ 12 的枢纽`; }
    button(ctl, "加 1 个节点", () => add(1)); button(ctl, "加 20 个", () => add(20), true);
    const auto = button(ctl, "自动生长", () => { if (timer) { clearInterval(timer); timer = null; auto.textContent = "自动生长"; return; } auto.textContent = "暂停"; timer = setInterval(() => { if (n >= 300) { clearInterval(timer); timer = null; auto.textContent = "自动生长"; return; } add(3); }, 120); }, true);
    button(ctl, "重置", () => { if (timer) { clearInterval(timer); timer = null; auto.textContent = "自动生长"; } reset(); }, true);
    reset(); add(40); window.addEventListener("themechange", draw);
  };

  // ------------------------------------------------------------------ modularity (karate club)
  const KARATE = [[0,1],[0,2],[0,3],[0,4],[0,5],[0,6],[0,7],[0,8],[0,10],[0,11],[0,12],[0,13],[0,17],[0,19],[0,21],[0,31],[1,2],[1,3],[1,7],[1,13],[1,17],[1,19],[1,21],[1,30],[2,3],[2,7],[2,8],[2,9],[2,13],[2,27],[2,28],[2,32],[3,7],[3,12],[3,13],[4,6],[4,10],[5,6],[5,10],[5,16],[6,16],[8,30],[8,32],[8,33],[9,33],[13,33],[14,32],[14,33],[15,32],[15,33],[18,32],[18,33],[19,33],[20,32],[20,33],[22,32],[22,33],[23,25],[23,27],[23,29],[23,32],[23,33],[24,25],[24,27],[24,31],[25,31],[26,29],[26,33],[27,33],[28,31],[28,33],[29,32],[29,33],[30,32],[30,33],[31,32],[31,33],[32,33]];
  const KARATE_SPLIT = [0,0,0,0,0,0,0,0,1,1,0,0,0,0,1,1,0,0,1,0,1,0,1,1,1,1,1,1,1,1,1,1,1,1];
  function modularity(n, edges, grp) { const m = edges.length, deg = new Array(n).fill(0); edges.forEach(([a, b]) => { deg[a]++; deg[b]++; });
    let q = 0; edges.forEach(([a, b]) => { if (grp[a] === grp[b]) q += 1; }); q /= m; const tot = {}; deg.forEach((d, i) => { tot[grp[i]] = (tot[grp[i]] || 0) + d; }); for (const k in tot) q -= Math.pow(tot[k] / (2 * m), 2); return q; }
  D.modularity = (root) => {
    const n = 34; const ctl = controls(root); const [cv, g] = canvas(root, 520, 360); const ro = el("p", { className: "readout" }); root.appendChild(ro);
    const P = layout(n, KARATE, 520, 360, 300, 4); let grp = new Array(n).fill(0); const K = 3;
    function draw() { const c = C(); clear(g, cv); drawNet(g, P, KARATE, { ecol: ([a, b]) => (grp[a] === grp[b] ? c.ink2 : c.line), size: () => 9, ncol: (i) => PAL[grp[i]] });
      P.forEach((p, i) => txt(g, String(i + 1), p[0], p[1] + 4, "#fff", 10, "center"));
      const q = modularity(n, KARATE, grp); ro.textContent = `模块度 Q = ${q.toFixed(3)}   （点击节点切换分组；俱乐部真实分裂的 Q ≈ ${modularity(n, KARATE, KARATE_SPLIT).toFixed(3)}）`; }
    cv.addEventListener("click", (ev) => { const b = cv.getBoundingClientRect(); const x = (ev.clientX - b.left) * cv._w / b.width, y = (ev.clientY - b.top) * cv._h / b.height;
      const i = P.findIndex((p) => Math.hypot(p[0] - x, p[1] - y) < 12); if (i >= 0) { grp[i] = (grp[i] + 1) % K; draw(); } });
    button(ctl, "全部归为一组", () => { grp = new Array(n).fill(0); draw(); }, true);
    button(ctl, "俱乐部真实分裂", () => { grp = [...KARATE_SPLIT]; draw(); }, true);
    button(ctl, "随机分组", () => { const r = rng(Date.now() % 997 + 1); grp = grp.map(() => Math.floor(r() * 2)); draw(); }, true);
    button(ctl, "贪心优化（Louvain 第一阶段）", () => { let improved = true, it = 0; while (improved && it < 20) { improved = false; it++; for (let i = 0; i < n; i++) { let best = grp[i], bq = modularity(n, KARATE, grp); for (let k = 0; k < 4; k++) { const old = grp[i]; grp[i] = k; const q = modularity(n, KARATE, grp); if (q > bq + 1e-9) { bq = q; best = k; improved = true; } grp[i] = old; } grp[i] = best; } } draw(); });
    draw(); window.addEventListener("themechange", draw);
  };

  // ------------------------------------------------------------------ sir
  D.sir = (root) => {
    const n = 220; const ctl = controls(root); const row = el("div", { className: "demo-row" }); root.appendChild(row);
    const [cv, g] = canvas(row, 360, 320); const [cp, gp] = canvas(row, 280, 320); const ro = el("p", { className: "readout" }); root.appendChild(ro);
    let type = "ba", beta = 0.2, gamma = 0.1, imm = "none", net, P, st, hist, timer = null;
    const sel = el("select"); sel.innerHTML = '<option value="ba">无标度网络（BA）</option><option value="er">随机网络（ER）</option>'; const lab = el("label", {}, "网络 "); lab.appendChild(sel); ctl.appendChild(lab);
    const sel2 = el("select"); sel2.innerHTML = '<option value="none">不免疫</option><option value="rand">随机免疫 15%</option><option value="hub">免疫度最大的 15%</option>'; const lab2 = el("label", {}, "免疫策略 "); lab2.appendChild(sel2); ctl.appendChild(lab2);
    function build() { const r = rng(9); const e = type === "ba" ? baEdges(n, 2, r) : erEdges(n, 4, r); net = adjFrom(n, e); net.edges = e; P = layout(n, e, 360, 320, 120, 3); start(); }
    function start() { if (timer) clearInterval(timer); timer = null; st = new Array(n).fill(0); const order = [...Array(n).keys()];
      const q = Math.round(0.15 * n); if (imm === "hub") order.sort((a, b) => net[b].length - net[a].length).slice(0, q).forEach((v) => (st[v] = 3)); if (imm === "rand") { const r = rng(4); order.sort(() => r() - 0.5).slice(0, q).forEach((v) => (st[v] = 3)); }
      let s0 = Math.floor(n * 0.6); while (st[s0] === 3) s0++; st[s0] = 1; hist = [count()]; draw(); }
    function count() { const c = [0, 0, 0, 0]; st.forEach((s) => c[s]++); return c.map((x) => x / n); }
    function step() { const r = Math.random; const nx = [...st]; for (let v = 0; v < n; v++) if (st[v] === 1) { for (const u of net[v]) if (st[u] === 0 && r() < beta) nx[u] = 1; if (r() < gamma) nx[v] = 2; } st = nx; hist.push(count()); draw(); if (!st.includes(1)) { clearInterval(timer); timer = null; } }
    function draw() { const c = C(); const col = [c.ink2, c.bad, c.ok, c.line]; clear(g, cv);
      drawNet(g, P, net.edges, { ecol: (e) => (st[e[0]] === 3 || st[e[1]] === 3 ? "transparent" : c.line), ncol: (i) => col[st[i]], size: (i) => 2 + Math.sqrt(net[i].length) * 1.2 });
      clear(gp, cp); const T = Math.max(60, hist.length); const [fx, fy] = axes(gp, 40, 15, 225, 255, [0, T], [0, 1], { xl: "时间步", yl: "比例", xt: [0, T], yt: [0, 0.5, 1] });
      [[0, c.ink2, "S"], [1, c.bad, "I"], [2, c.ok, "R"]].forEach(([k, col2, lb]) => { line(gp, hist.map((h, i) => [i, h[k]]), fx, fy, col2, 2); txt(gp, lb, 250, 30 + k * 16, col2, 12); });
      const last = hist[hist.length - 1]; ro.textContent = `传染率 β = ${beta.toFixed(2)}  恢复率 γ = ${gamma.toFixed(2)}  当前感染 ${(last[1] * 100).toFixed(0)}%  累计感染 ${((last[1] + last[2]) * 100).toFixed(0)}%  免疫 ${(last[3] * 100).toFixed(0)}%`; }
    slider(ctl, "β", 0.02, 0.6, 0.01, beta, (v) => v.toFixed(2), (v) => { beta = v; draw(); });
    slider(ctl, "γ", 0.02, 0.5, 0.01, gamma, (v) => v.toFixed(2), (v) => { gamma = v; draw(); });
    button(ctl, "开始传播", () => { if (!st.includes(1)) start(); if (!timer) timer = setInterval(step, 160); });
    button(ctl, "重置", start, true);
    sel.addEventListener("change", () => { type = sel.value; build(); }); sel2.addEventListener("change", () => { imm = sel2.value; start(); });
    build(); window.addEventListener("themechange", draw);
  };

  // ------------------------------------------------------------------ kuramoto
  D.kuramoto = (root) => {
    const N = 60, r = rng(2); const w = Array.from({ length: N }, () => gauss(r) * 0.5); let th = Array.from({ length: N }, () => r() * 2 * Math.PI); let K = 0.4; const rs = [];
    const ctl = controls(root); const row = el("div", { className: "demo-row" }); root.appendChild(row);
    const [cv, g] = canvas(row, 300, 300); const [cp, gp] = canvas(row, 340, 300); const ro = el("p", { className: "readout" }); root.appendChild(ro);
    slider(ctl, "耦合强度 K", 0, 2.5, 0.05, K, (v) => v.toFixed(2), (v) => { K = v; });
    button(ctl, "打乱相位", () => { th = th.map(() => Math.random() * 2 * Math.PI); }, true);
    let raf; const vis = () => !document.hidden;
    function frame() { const c = C(); for (let s = 0; s < 4; s++) { let sx = 0, sy = 0; th.forEach((t) => { sx += Math.cos(t); sy += Math.sin(t); }); const R = Math.hypot(sx, sy) / N, psi = Math.atan2(sy, sx); th = th.map((t, i) => t + 0.05 * (w[i] + K * R * Math.sin(psi - t))); }
      let sx = 0, sy = 0; th.forEach((t) => { sx += Math.cos(t); sy += Math.sin(t); }); const R = Math.hypot(sx, sy) / N; rs.push(R); if (rs.length > 300) rs.shift();
      clear(g, cv); g.strokeStyle = c.line; g.lineWidth = 2; g.beginPath(); g.arc(150, 150, 115, 0, 7); g.stroke();
      th.forEach((t, i) => { const hue = 220 - ((w[i] + 1.2) / 2.4) * 200; g.fillStyle = `hsl(${hue},70%,52%)`; g.beginPath(); g.arc(150 + 115 * Math.cos(t), 150 + 115 * Math.sin(t), 5.5, 0, 7); g.fill(); });
      g.strokeStyle = c.ink; g.lineWidth = 3; g.beginPath(); g.moveTo(150, 150); g.lineTo(150 + 115 * sx / N, 150 + 115 * sy / N); g.stroke();
      clear(gp, cp); const [fx, fy] = axes(gp, 40, 15, 285, 245, [0, 300], [0, 1], { xl: "时间", yl: "序参量 r", yt: [0, 0.5, 1] }); line(gp, rs.map((v, i) => [i, v]), fx, fy, c.acc, 2);
      const Kc = (2 / Math.PI) * 0.5 * Math.sqrt(2 * Math.PI); ro.textContent = `K = ${K.toFixed(2)}   r = ${R.toFixed(2)}   理论临界耦合 Kc ≈ ${Kc.toFixed(2)}（无穷大全连接网络、高斯频率分布）`;
      raf = requestAnimationFrame(frame); }
    const io = new IntersectionObserver((es) => { es.forEach((e) => { if (e.isIntersecting && vis()) { if (!raf) raf = requestAnimationFrame(frame); } else { cancelAnimationFrame(raf); raf = null; } }); }); io.observe(root);
  };

  // ------------------------------------------------------------------ attack
  D.attack = (root) => {
    const ctl = controls(root); const [cp, gp] = canvas(root, 520, 320); const ro = el("p", { className: "readout" }); root.appendChild(ro);
    let type = "ba"; const sel = el("select"); sel.innerHTML = '<option value="ba">无标度网络（BA，N=1000）</option><option value="er">随机网络（ER，N=1000）</option>'; const lab = el("label", {}, "网络 "); lab.appendChild(sel); ctl.appendChild(lab);
    function curve(adj, order) { const n = adj.length, alive = new Array(n).fill(true), out = [[0, giantSet(adj, alive)[1] / n]]; const step = 20; for (let i = 0; i < n * 0.6; i += step) { order.slice(i, i + step).forEach((v) => (alive[v] = false)); out.push([(i + step) / n, giantSet(adj, alive)[1] / n]); } return out; }
    function draw() { const c = C(); const r = rng(5); const n = 1000; const e = type === "ba" ? baEdges(n, 2, r) : erEdges(n, 4, r); const adj = adjFrom(n, e);
      const rand = [...Array(n).keys()].sort(() => r() - 0.5); const hub = [...Array(n).keys()].sort((a, b) => adj[b].length - adj[a].length);
      const cr = curve(adj, rand), ca = curve(adj, hub); clear(gp, cp);
      const [fx, fy] = axes(gp, 50, 15, 440, 255, [0, 0.6], [0, 1], { xl: "移除节点比例 f", yl: "巨连通分支占比", xt: [0, 0.2, 0.4, 0.6], yt: [0, 0.5, 1] });
      line(gp, cr, fx, fy, c.acc, 2.5); line(gp, ca, fx, fy, c.bad, 2.5); txt(gp, "随机失效", 400, 40, c.acc, 13); txt(gp, "蓄意攻击（按度）", 400, 58, c.bad, 13);
      const at = (cv2, f) => cv2.find((p) => p[0] >= f) || cv2[cv2.length - 1]; ro.textContent = `移除 10% 节点后巨分支：随机 ${(at(cr, 0.1)[1] * 100).toFixed(0)}%，攻击 ${(at(ca, 0.1)[1] * 100).toFixed(0)}%`; }
    sel.addEventListener("change", () => { type = sel.value; draw(); }); draw(); window.addEventListener("themechange", draw);
  };

  // ------------------------------------------------------------------ matching / driver nodes
  D.matching = (root) => {
    const ctl = controls(root); const [cv, g] = canvas(root, 520, 340); const ro = el("p", { className: "readout" }); root.appendChild(ro);
    let n = 14, E, P, M, seed = 12, dens = 1.6;
    function gen() { const r = rng(seed); E = []; const set = new Set(); const m = Math.round(dens * n); while (E.length < m) { const a = Math.floor(r() * n), b = Math.floor(r() * n); if (a !== b && !set.has(a + ">" + b)) { set.add(a + ">" + b); E.push([a, b]); } }
      P = layout(n, E, 520, 340, 250, seed); const out = Array.from({ length: n }, () => []); E.forEach(([a, b]) => out[a].push(b)); const matchR = new Array(n).fill(-1);
      function aug(u, seen) { for (const v of out[u]) { if (seen[v]) continue; seen[v] = true; if (matchR[v] < 0 || aug(matchR[v], seen)) { matchR[v] = u; return true; } } return false; }
      for (let u = 0; u < n; u++) aug(u, new Array(n).fill(false)); M = new Set(); matchR.forEach((u, v) => { if (u >= 0) M.add(u + ">" + v); }); draw(); }
    function arrow(x1, y1, x2, y2, col, lw) { const a = Math.atan2(y2 - y1, x2 - x1); const sx = x1 + 13 * Math.cos(a), sy = y1 + 13 * Math.sin(a), ex = x2 - 14 * Math.cos(a), ey = y2 - 14 * Math.sin(a);
      g.strokeStyle = col; g.fillStyle = col; g.lineWidth = lw; g.beginPath(); g.moveTo(sx, sy); g.lineTo(ex, ey); g.stroke(); g.beginPath(); g.moveTo(ex, ey); g.lineTo(ex - 9 * Math.cos(a - 0.4), ey - 9 * Math.sin(a - 0.4)); g.lineTo(ex - 9 * Math.cos(a + 0.4), ey - 9 * Math.sin(a + 0.4)); g.fill(); }
    function draw() { const c = C(); clear(g, cv); const matchedIn = new Set([...M].map((s) => +s.split(">")[1])); const drivers = [...Array(n).keys()].filter((v) => !matchedIn.has(v));
      E.forEach(([a, b]) => arrow(...P[a], ...P[b], M.has(a + ">" + b) ? c.hub : c.line, M.has(a + ">" + b) ? 3 : 1.4));
      P.forEach((p, i) => { g.fillStyle = drivers.includes(i) ? c.bad : c.acc; g.beginPath(); g.arc(p[0], p[1], 11, 0, 7); g.fill(); txt(g, String(i + 1), p[0], p[1] + 4, "#fff", 11, "center"); });
      const D0 = drivers.length ? drivers : [0];
      const rk = kalmanRank(D0), rk2 = D0.length > 1 ? kalmanRank(D0.slice(1)) : null;
      ro.innerHTML = `N = ${n}，有向边 ${E.length} 条，最大匹配 |M*| = ${M.size}，驱动节点 N<sub>D</sub> = max(N − |M*|, 1) = ${D0.length}（红色）。橙色边为一组最大匹配。<br>` +
        `给边随机赋权后检验 Kalman 秩：用这 ${D0.length} 个驱动节点，rank[B, AB, …, A<sup>N−1</sup>B] = ${rk}/${n}` + (rk2 !== null ? `；去掉其中一个驱动节点后秩 = ${rk2}/${n}` : "") +
        `。结构可控性只依赖连边结构，对“几乎所有”权重成立；某一组具体参数仍需用 Kalman 判据单独检验。`; }
    function kalmanRank(drv) { const r = rng(seed * 7 + 1); const A = Array.from({ length: n }, () => new Array(n).fill(0)); E.forEach(([a, b]) => { A[b][a] = 0.3 + r(); });
      let cols = drv.map((d) => { const v = new Array(n).fill(0); v[d] = 1; return v; }); const all = [...cols];
      for (let k = 1; k < n; k++) { cols = cols.map((v) => { const w = A.map((row) => row.reduce((s2, x, j) => s2 + x * v[j], 0)); const nr = Math.hypot(...w) || 1; return w.map((x) => x / nr); }); all.push(...cols); }
      const Mx = all.map((c) => [...c]); let rank = 0; const used = new Array(Mx.length).fill(false);
      for (let row = 0; row < n; row++) { let best = -1, bv = 1e-9; for (let c = 0; c < Mx.length; c++) if (!used[c] && Math.abs(Mx[c][row]) > bv) { bv = Math.abs(Mx[c][row]); best = c; }
        if (best < 0) continue; used[best] = true; rank++; for (let c = 0; c < Mx.length; c++) if (c !== best) { const f = Mx[c][row] / Mx[best][row]; if (f) for (let j = 0; j < n; j++) Mx[c][j] -= f * Mx[best][j]; } }
      return rank; }
    slider(ctl, "平均出度", 0.6, 3, 0.1, dens, (v) => v.toFixed(1), (v) => { dens = v; gen(); });
    button(ctl, "换一个网络", () => { seed++; gen(); }, true); gen(); window.addEventListener("themechange", draw);
  };

  // ------------------------------------------------------------------ brain_threshold
  function modularData(seed) { const r = rng(seed), nm = 4, per = 10, T = 200, n = nm * per; const X = Array.from({ length: n }, () => new Array(T));
    for (let t = 0; t < T; t++) { const F = Array.from({ length: nm }, () => gauss(r)); const G = gauss(r); for (let i = 0; i < n; i++) X[i][t] = 0.9 * F[Math.floor(i / per)] + 0.35 * G + gauss(r); }
    return [corr(X), Array.from({ length: n }, (_, i) => Math.floor(i / per))]; }
  function corr(X) { const n = X.length, T = X[0].length; const Z = X.map((x) => { const m = x.reduce((a, b) => a + b, 0) / T; const s = Math.sqrt(x.reduce((a, b) => a + (b - m) ** 2, 0) / T) || 1; return x.map((v) => (v - m) / s); });
    return Z.map((a) => Z.map((b) => a.reduce((s, v, k) => s + v * b[k], 0) / T)); }
  const REGIONS = ["视觉", "感觉运动", "默认模式", "额顶控制"];
  D.brain_threshold = (root) => {
    const [Cm, lab] = modularData(4); const n = Cm.length; const pairs = []; for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++) pairs.push([i, j, Cm[i][j]]); pairs.sort((a, b) => b[2] - a[2]);
    const ctl = controls(root); const row = el("div", { className: "demo-row" }); root.appendChild(row); const [cm, gm] = canvas(row, 250, 250); const [cv, g] = canvas(row, 300, 300); const ro = el("p", { className: "readout" }); root.appendChild(ro);
    const P = circ(n, 300, 300, 108).map(([x, y]) => [x + 20, y + 8]); let dens = 0.15, mode = "prop";
    const sel = el("select"); sel.innerHTML = '<option value="prop">比例阈值（保留最强的一部分边）</option><option value="abs">绝对阈值（r ≥ 0.3）</option>'; const l2 = el("label", {}, "阈值方式 "); l2.appendChild(sel); ctl.appendChild(l2);
    function draw() { const c = C(); const keep = mode === "prop" ? pairs.slice(0, Math.max(1, Math.round(dens * pairs.length))) : pairs.filter((p) => p[2] >= 0.3);
      const thr = keep[keep.length - 1][2]; const adj = adjFrom(n, keep); const cc = clustering(adj); const nc = new Set(comps(adj)).size;
      clear(gm, cm); const s = 240 / n; for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) { const v = Cm[i][j]; if (i === j) continue; const on = v >= thr; gm.fillStyle = on ? `rgba(224,49,49,${Math.min(1, Math.max(0.15, v))})` : c.paper; gm.fillRect(5 + j * s, 5 + i * s, s, s); }
      clear(g, cv); drawNet(g, P, keep, { ecol: ([a, b]) => (lab[a] === lab[b] ? "rgba(59,91,219,.45)" : "rgba(232,89,12,.55)"), ncol: (i) => PAL[lab[i]], size: (i) => 3 + adj[i].length * 0.35 });
      REGIONS.forEach((nm, k) => txt(g, nm, 10, 16 + k * 15, PAL[k], 12));
      const hubs = [...Array(n).keys()].sort((a, b) => adj[b].length - adj[a].length).slice(0, 3).map((i) => `${REGIONS[lab[i]]}-${(i % 10) + 1}`);
      ro.textContent = `密度 ${(keep.length / pairs.length * 100).toFixed(1)}%   阈值 r ≥ ${thr.toFixed(2)}   平均聚集系数 ${cc.toFixed(3)}   连通分支 ${nc}   度最高的脑区：${hubs.join("、")}`; }
    slider(ctl, "保留密度", 0.02, 0.5, 0.01, dens, (v) => (v * 100).toFixed(0) + "%", (v) => { dens = v; if (mode === "prop") draw(); });
    sel.addEventListener("change", () => { mode = sel.value; draw(); }); draw(); window.addEventListener("themechange", draw);
  };

  // ------------------------------------------------------------------ dfc
  D.dfc = (root) => {
    const r = rng(6), n = 6, L = 600; const st = Array.from({ length: L }, (_, t) => ((t >= 150 && t < 300) || (t >= 420 && t < 520) ? 1 : 0)); const X = Array.from({ length: n }, () => new Array(L));
    for (let t = 0; t < L; t++) { const f0 = gauss(r), f1 = gauss(r); for (let i = 0; i < n; i++) { const base = st[t] === 0 ? (i < 3 ? f0 : f1) : (i % 2 === 0 ? f0 : -0.8 * f0); X[i][t] = base + 0.8 * gauss(r); } }
    for (let i = 0; i < n; i++) { const y = [...X[i]]; for (let t = 2; t < L - 2; t++) X[i][t] = (y[t - 2] + y[t - 1] + y[t] + y[t + 1] + y[t + 2]) / 5; }
    const ctl = controls(root); const [cv, g] = canvas(root, 560, 200); const row = el("div", { className: "demo-row" }); root.appendChild(row); const [cm, gm] = canvas(row, 200, 200); const [cp, gp] = canvas(row, 340, 200); const ro = el("p", { className: "readout" }); root.appendChild(ro);
    let pos = 100, W = 60;
    function draw() { const c = C(); clear(g, cv); g.fillStyle = "rgba(232,89,12,.15)"; g.fillRect(10 + pos / L * 540, 0, W / L * 540, 200);
      for (let i = 0; i < n; i++) { g.strokeStyle = PAL[i]; g.lineWidth = 1; g.beginPath(); for (let t = 0; t < L; t++) { const x = 10 + t / L * 540, y = 18 + i * 31 - X[i][t] * 8; t ? g.lineTo(x, y) : g.moveTo(x, y); } g.stroke(); }
      const seg = X.map((x) => x.slice(pos, pos + W)); const Cw = corr(seg); clear(gm, cm); const s = 180 / n;
      for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) { const v = Cw[i][j]; gm.fillStyle = v >= 0 ? `rgba(224,49,49,${Math.abs(v)})` : `rgba(59,91,219,${Math.abs(v)})`; gm.fillRect(10 + j * s, 10 + i * s, s - 1, s - 1); }
      const series = []; for (let p = 0; p + W <= L; p += 5) { const a = X[0].slice(p, p + W), b = X[1].slice(p, p + W); series.push([p, corr([a, b])[0][1]]); }
      clear(gp, cp); const [fx, fy] = axes(gp, 40, 10, 285, 150, [0, L - W], [-1, 1], { xl: "窗口起点", yl: "脑区1–2 相关", xt: [0, 270, 540], yt: [-1, 0, 1] }); line(gp, series, fx, fy, c.acc, 1.8);
      gp.fillStyle = c.hub; gp.beginPath(); gp.arc(fx(pos), fy(Cw[0][1]), 5, 0, 7); gp.fill();
      ro.textContent = `窗口 [${pos}, ${pos + W})，长度 ${W} 个时间点   脑区1–2 相关 r = ${Cw[0][1].toFixed(2)}   真实状态：${st[pos + W / 2 | 0] ? "B" : "A"}（数据为模拟）`; }
    slider(ctl, "窗口位置", 0, L - 20, 5, pos, (v) => String(v), (v) => { pos = Math.min(v, L - W); draw(); });
    slider(ctl, "窗口长度", 15, 150, 5, W, (v) => String(v), (v) => { W = v; pos = Math.min(pos, L - W); draw(); });
    draw(); window.addEventListener("themechange", draw);
  };

  // ------------------------------------------------------------------ symptom
  const SYM = ["情绪低落", "兴趣减退", "睡眠问题", "疲乏", "食欲改变", "自我否定", "注意困难", "精神运动", "自杀意念"];
  function inv(A) { const n = A.length, M = A.map((r, i) => [...r, ...Array.from({ length: n }, (_, j) => (i === j ? 1 : 0))]);
    for (let c = 0; c < n; c++) { let p = c; for (let r = c + 1; r < n; r++) if (Math.abs(M[r][c]) > Math.abs(M[p][c])) p = r; [M[c], M[p]] = [M[p], M[c]]; const d = M[c][c]; for (let j = 0; j < 2 * n; j++) M[c][j] /= d;
      for (let r = 0; r < n; r++) if (r !== c) { const f = M[r][c]; for (let j = 0; j < 2 * n; j++) M[r][j] -= f * M[c][j]; } } return M.map((r) => r.slice(n)); }
  function chol(S) { const n = S.length, L = S.map(() => new Array(n).fill(0)); for (let i = 0; i < n; i++) for (let j = 0; j <= i; j++) { let s = S[i][j]; for (let k = 0; k < j; k++) s -= L[i][k] * L[j][k]; L[i][j] = i === j ? Math.sqrt(s) : s / L[j][j]; } return L; }
  D.symptom = (root) => {
    const n = 9; const Pm = Array.from({ length: n }, (_, i) => Array.from({ length: n }, (_, j) => (i === j ? 1 : 0)));
    [[0, 1, .35], [0, 5, .3], [1, 3, .25], [2, 3, .4], [3, 6, .25], [5, 8, .35], [0, 8, .2], [4, 2, .2], [6, 7, .2], [1, 6, .15], [4, 3, -.12]].forEach(([a, b, w]) => { Pm[a][b] = Pm[b][a] = -w; });
    const S = inv(Pm), L = chol(S), r = rng(1); let N = 500;
    const ctl = controls(root); const row = el("div", { className: "demo-row" }); root.appendChild(row); const [cv, g] = canvas(row, 340, 320); const [cb, gb] = canvas(row, 260, 320); const ro = el("p", { className: "readout" }); root.appendChild(ro);
    let mode = "pcor", W;
    function sample() { const X = Array.from({ length: n }, () => []); for (let s = 0; s < N; s++) { const z = Array.from({ length: n }, () => gauss(r)); for (let i = 0; i < n; i++) { let v = 0; for (let k = 0; k <= i; k++) v += L[i][k] * z[k]; X[i].push(v); } }
      const Cm = corr(X); const Pi = inv(Cm); const Pc = Pi.map((row2, i) => row2.map((v, j) => (i === j ? 0 : -v / Math.sqrt(Pi[i][i] * Pi[j][j])))); W = { cor: Cm.map((row2, i) => row2.map((v, j) => (i === j ? 0 : v))), pcor: Pc }; draw(); }
    const P = circ(n, 340, 320, 118);
    function draw() { const c = C(); const M = W[mode]; clear(g, cv);
      for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++) { const v = M[i][j]; if (Math.abs(v) < 0.05) continue; g.strokeStyle = v > 0 ? "rgba(59,91,219,.75)" : "rgba(224,49,49,.8)"; g.lineWidth = Math.abs(v) * 14; g.beginPath(); g.moveTo(...P[i]); g.lineTo(...P[j]); g.stroke(); }
      P.forEach((p, i) => { g.fillStyle = c.sheet; g.strokeStyle = c.ink; g.lineWidth = 1.2; g.beginPath(); g.arc(p[0], p[1], 25, 0, 7); g.fill(); g.stroke(); txt(g, SYM[i], p[0], p[1] + 4, c.ink, 10.5, "center"); });
      const str = M.map((row2) => row2.reduce((a, b) => a + Math.abs(b), 0)); const o = [...Array(n).keys()].sort((a, b) => str[a] - str[b]); const mx = Math.max(...str);
      clear(gb, cb); o.forEach((i, k) => { const y = 300 - k * 32; gb.fillStyle = c.acc; gb.fillRect(80, y - 18, (str[i] / mx) * 165, 20); txt(gb, SYM[i], 74, y - 3, c.ink, 12, "right"); txt(gb, str[i].toFixed(2), 84 + (str[i] / mx) * 165, y - 3, c.ink2, 11); });
      const ne = M.flat().filter((v) => Math.abs(v) >= 0.05).length / 2; ro.textContent = `${mode === "cor" ? "相关" : "偏相关"}网络：|权重| ≥ 0.05 的边 ${ne} 条（共 36 对），样本量 N = ${N}（模拟数据）。右：强度中心性。`; }
    const sel = el("select"); sel.innerHTML = '<option value="pcor">偏相关（控制其余 7 个症状）</option><option value="cor">零阶相关</option>'; const l = el("label", {}, "边的定义 "); l.appendChild(sel); ctl.appendChild(l);
    sel.addEventListener("change", () => { mode = sel.value; draw(); });
    slider(ctl, "样本量", 60, 2000, 20, N, (v) => String(v), (v) => { N = v; });
    button(ctl, "重新抽样", sample, true); sample(); window.addEventListener("themechange", draw);
  };

  // ------------------------------------------------------------------ ffl
  D.ffl = (root) => {
    const ctl = controls(root); const [cp, gp] = canvas(root, 560, 300); const ro = el("p", { className: "readout" }); root.appendChild(ro); let pulse = 2;
    function draw() { const c = C(); const dt = 0.05, T = 30; const t0 = 3; const X = [], Y = [], Z = [], Zs = []; let y = 0, z = 0, zs = 0;
      for (let t = 0; t < T; t += dt) { const x = t > t0 && t < t0 + pulse ? 1 : 0; y += dt * (x - 0.4 * y); z += dt * ((x && y > 1.2 ? 1 : 0) - 0.4 * z); zs += dt * (x - 0.4 * zs); X.push([t, x]); Y.push([t, y / 2.5]); Z.push([t, z / 2.5]); Zs.push([t, zs / 2.5]); }
      clear(gp, cp); const [fx, fy] = axes(gp, 45, 15, 490, 240, [0, T], [0, 1.1], { xl: "时间", yl: "表达水平（相对）", xt: [0, 10, 20, 30], yt: [0, 0.5, 1] });
      line(gp, X, fx, fy, c.ink2, 1.5); line(gp, Y, fx, fy, "#7048e8", 2); line(gp, Zs, fx, fy, c.line, 2); line(gp, Z, fx, fy, c.hub, 2.8);
      txt(gp, "输入 X", 470, 30, c.ink2, 12); txt(gp, "中间 Y", 470, 46, "#7048e8", 12); txt(gp, "Z（简单调控）", 470, 62, c.ink2, 12); txt(gp, "Z（前馈环，AND）", 470, 78, c.hub, 12);
      const zmax = Math.max(...Z.map((p) => p[1])); ro.textContent = `输入脉冲长度 ${pulse.toFixed(1)}：前馈环输出 Z 峰值 ${zmax.toFixed(2)}，简单调控峰值 ${Math.max(...Zs.map((p) => p[1])).toFixed(2)}。短脉冲被过滤，这就是“持续性检测器”。`; }
    slider(ctl, "输入脉冲长度", 0.5, 15, 0.5, pulse, (v) => v.toFixed(1), (v) => { pulse = v; draw(); }); draw(); window.addEventListener("themechange", draw);
  };

  // ------------------------------------------------------------------ proximity
  D.proximity = (root) => {
    const n = 120; const e = wsEdges(n, 4, 0.12, rng(9)); const adj = adjFrom(n, e); const P = layout(n, e, 540, 360, 250, 9);
    const d0 = bfs(adj, 0); const dis = [...Array(n).keys()].filter((v) => d0[v] <= 2).slice(0, 10); const dist = [...Array(n).keys()].map((v) => bfs(adj, v));
    let tg = new Set([...Array(n).keys()].filter((v) => d0[v] === 3).slice(0, 3));
    const r = rng(2); const null_ = []; for (let s = 0; s < 400; s++) { const T = [...Array(n).keys()].sort(() => r() - 0.5).slice(0, 3), S = [...Array(n).keys()].sort(() => r() - 0.5).slice(0, dis.length); null_.push(T.reduce((a, t) => a + Math.min(...S.map((x) => dist[t][x])), 0) / 3); }
    const mu = null_.reduce((a, b) => a + b, 0) / null_.length, sd = Math.sqrt(null_.reduce((a, b) => a + (b - mu) ** 2, 0) / null_.length);
    const [cv, g] = canvas(root, 540, 360); const ro = el("p", { className: "readout" }); root.appendChild(ro);
    function draw() { const c = C(); clear(g, cv); drawNet(g, P, e, { ecol: () => c.line, ncol: (i) => (dis.includes(i) ? c.bad : tg.has(i) ? c.acc : c.ink2), size: (i) => (dis.includes(i) || tg.has(i) ? 7 : 3.5) });
      const T = [...tg]; if (!T.length) { ro.textContent = "点击节点选择药物靶点（蓝色）。红色是疾病模块。"; return; }
      const dc = T.reduce((a, t) => a + Math.min(...dis.map((s) => dist[t][s])), 0) / T.length; const z = (dc - mu) / sd;
      ro.textContent = `药物靶点 ${T.length} 个   最近距离 d_c = ${dc.toFixed(2)}   随机靶点集合的均值 ${mu.toFixed(2)} ± ${sd.toFixed(2)}   z = ${z.toFixed(2)} ${z < -1.5 ? "（显著接近疾病模块）" : ""}   随机对照固定为 3 个靶点，点击节点增删靶点`; }
    cv.addEventListener("click", (ev) => { const b = cv.getBoundingClientRect(); const x = (ev.clientX - b.left) * cv._w / b.width, y = (ev.clientY - b.top) * cv._h / b.height; const i = P.findIndex((p) => Math.hypot(p[0] - x, p[1] - y) < 9);
      if (i >= 0 && !dis.includes(i)) { tg.has(i) ? tg.delete(i) : tg.add(i); draw(); } });
    draw(); window.addEventListener("themechange", draw);
  };

  // ------------------------------------------------------------------ mount
  const TITLES = { graph_matrix: ["图与邻接矩阵", "依次点击两个节点即可添加或删除它们之间的边，观察矩阵和度序列如何同步变化。"],
    er: ["ER 随机图与巨连通分支", "拖动 p：当平均度越过 1，最大连通分支（橙色）会突然“长大”，这是一个相变。"],
    ws: ["Watts–Strogatz 重连", "β 从 0.0001 增大到 1：注意平均路径 L 先下降，而聚集系数 C 在很宽的区间内几乎不变，这就是小世界区间。"],
    ba: ["BA 优先连接", "不断加入新节点，每个新节点连到 2 个已有节点，连接概率与其度成正比。观察枢纽如何出现，以及双对数坐标下的直线。"],
    modularity: ["模块度：给空手道俱乐部分组", "点击节点改变分组，看模块度 Q 如何变化；再试试“贪心优化”。"],
    sir: ["网络上的 SIR 传播", "比较无标度网络和随机网络的传播，再比较随机免疫和免疫枢纽的效果。"],
    kuramoto: ["Kuramoto 同步", "增大耦合强度 K，振子从各自转动变成成群同步；箭头长度就是序参量 r。"],
    attack: ["随机失效与蓄意攻击", "按度从大到小移除节点（蓄意攻击）与随机移除对比；切换网络类型看看差别。"],
    matching: ["最大匹配与驱动节点", "结构可控性：驱动节点 = 没有被匹配边指向的节点。调节平均出度，看稀疏网络为什么需要更多驱动节点；下方再用 Kalman 秩判据对随机赋权的系统做数值检验。注意：这里的最大匹配方法（Liu 2011）与基于最小支配集的控制方法是两种不同的框架。"],
    brain_threshold: ["脑网络阈值实验（模拟数据）", "同一个功能连接矩阵，换一个阈值，网络指标与“枢纽脑区”就可能改变。"],
    dfc: ["滑动窗口动态功能连接（模拟数据）", "拖动窗口：同一对脑区在不同时间段的相关可正可负；窗口太短则估计噪声大。"],
    symptom: ["症状网络：相关与偏相关（模拟数据）", "零阶相关几乎全连接；偏相关只保留控制其他症状后的直接关联。改变样本量，看边和中心性排序是否稳定。"],
    ffl: ["前馈环的滤波作用", "一致型前馈环（AND 逻辑）只响应持续足够久的输入。调节脉冲长度试试。"],
    proximity: ["网络邻近度：药物靶点与疾病模块", "点击节点放置药物靶点，计算最近距离 d_c 并与随机靶点集合比较（z 值）。"] };
  document.querySelectorAll(".demo[data-demo]").forEach((root) => {
    const id = root.dataset.demo; const f = D[id]; if (!f) return; const t = TITLES[id] || [id, ""];
    root.appendChild(el("h3", {}, t[0])); root.appendChild(el("p", { className: "hint" }, t[1]));
    try { f(root); } catch (e) { root.appendChild(el("p", { className: "hint" }, "演示加载失败：" + e.message)); }
    // export: PNG of the canvases + JSON of the parameters and readouts
    const bar = el("div", { className: "demo-export" });
    const png = el("button", { className: "btn ghost", type: "button" }, "导出图片 PNG");
    const js = el("button", { className: "btn ghost", type: "button" }, "导出参数与读数 JSON");
    png.addEventListener("click", () => {
      const cs = [...root.querySelectorAll("canvas")]; if (!cs.length) return;
      const W = Math.max(...cs.map((c) => c.width)), H = cs.reduce((s, c) => s + c.height, 0);
      const out = document.createElement("canvas"); out.width = W; out.height = H; const g = out.getContext("2d");
      g.fillStyle = getComputedStyle(document.body).backgroundColor || "#fff"; g.fillRect(0, 0, W, H);
      let y = 0; cs.forEach((c) => { g.drawImage(c, 0, y); y += c.height; });
      const a = document.createElement("a"); a.href = out.toDataURL("image/png"); a.download = id + ".png"; a.click();
    });
    js.addEventListener("click", () => {
      const params = {}; root.querySelectorAll("input, select").forEach((x, i) => { const k = x.name || x.id || (x.closest("label") ? x.closest("label").textContent.trim().slice(0, 24) : "p" + i); params[k] = x.type === "checkbox" ? x.checked : x.value; });
      const readouts = [...root.querySelectorAll(".readout, .stat, output, .val")].map((x) => x.textContent.trim()).filter(Boolean);
      const blob = new Blob([JSON.stringify({ demo: id, title: t[0], exported: new Date().toISOString(), params, readouts }, null, 2)], { type: "application/json" });
      const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = id + ".json"; a.click();
    });
    bar.appendChild(png); bar.appendChild(js); root.appendChild(bar);
    const inner = el("div", { className: "demo-inner" }); while (root.firstChild) inner.appendChild(root.firstChild); root.appendChild(inner);
  });
  window.BCNA_DEMOS = D;
})();
