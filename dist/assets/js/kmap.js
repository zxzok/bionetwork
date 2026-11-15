/* Home page knowledge map: topics on a ring grouped by knowledge domain; curves are cross-references
   between topic texts (only the strong ones until a topic is hovered). Click a topic to open it. */
(function () {
  "use strict";
  const cv = document.getElementById("kmap");
  if (!cv || !window.KMAP) return;
  const g = cv.getContext("2d");
  const data = window.KMAP;
  const css = (n) => getComputedStyle(document.documentElement).getPropertyValue(n).trim() || "#888";
  const font = () => getComputedStyle(document.body).fontFamily;
  const N = data.nodes.length;
  const idx = {}; data.nodes.forEach((n, i) => { idx[n.id] = i; });
  const E = data.edges.filter((e) => e[0] in idx && e[1] in idx).map((e) => [idx[e[0]], idx[e[1]], e[2]]);
  const nbr = data.nodes.map(() => new Set());
  E.forEach(([a, b]) => { nbr[a].add(b); nbr[b].add(a); });
  const doms = [...new Set(data.nodes.map((n) => n.d))];
  const SHORT = { "复杂系统与网络的数学表示": "网络的数学表示", "网络结构指标与随机图": "结构指标与随机图", "小世界与无标度网络模型": "小世界与无标度",
    "度相关性与网络结构的高阶统计": "度相关性", "网络鲁棒性、渗流与级联失效": "鲁棒性与级联失效", "脑连接组：结构与功能连接": "脑连接组",
    "动态功能连接与多层脑网络": "动态脑网络", "症状网络与网络精神病学": "症状网络", "生物分子网络与拓扑特征": "分子网络",
    "基因调控网络推断与共表达分析": "基因网络推断", "疾病模块、网络邻近度与药物重定位": "网络医学", "网络分析流程与 NetworkX 实践": "分析流程",
    "研究问题、可复现分析与敏感性分析": "可复现研究", "结果呈现与研究前沿": "结果呈现与前沿", "网络构建与统计验证": "网络构建与验证",
    "网络上的传播与免疫": "传播与免疫", "同步与协同动力学": "同步", "网络可控性与稳定性": "可控性", "社团结构与社区发现": "社团结构" };

  // ---- ring layout: domains as arcs, small gaps between domains
  const order = [];
  doms.forEach((d) => data.nodes.forEach((n, i) => { if (n.d === d) order.push(i); }));
  const gap = 0.45, slots = N + gap * doms.length;
  const ANG = new Array(N);
  { let pos = gap / 2, last = null;
    order.forEach((i) => { if (last !== null && data.nodes[i].d !== last) pos += gap; ANG[i] = -Math.PI / 2 + (pos / slots) * Math.PI * 2; pos += 1; last = data.nodes[i].d; }); }
  const wmax = Math.max(1, ...E.map((e) => e[2]));
  const strong = E.map((e) => e[2]).sort((a, b) => b - a)[Math.min(E.length - 1, Math.round(N * 1.6))] || 1;

  let W = 0, H = 0, RAD = 100, CX = 0, CY = 0, hover = -1;
  const R = data.nodes.map((n) => 4.5 + Math.sqrt(n.n) * 1.5);
  const xy = (i) => [CX + Math.cos(ANG[i]) * RAD, CY + Math.sin(ANG[i]) * RAD];
  function size() {
    const r = cv.getBoundingClientRect(), d = window.devicePixelRatio || 1;
    W = r.width; H = r.width * 3 / 4; cv.width = W * d; cv.height = H * d; g.setTransform(d, 0, 0, d, 0, 0);
    CX = W * 0.5; CY = H * 0.5; RAD = Math.min(W * 0.27, H * 0.34); draw();
  }
  function draw() {
    const line = css("--ink-3"), ink = css("--ink"), ink2 = css("--ink-2"), sheet = css("--sheet");
    g.clearRect(0, 0, W, H);
    // edges
    E.forEach(([a, b, w]) => {
      const on = hover >= 0 && (a === hover || b === hover);
      if (!on && (hover >= 0 || w < strong)) return;
      const [x1, y1] = xy(a), [x2, y2] = xy(b);
      g.strokeStyle = on ? css("--d-" + data.nodes[hover].d) : line;
      g.globalAlpha = on ? 0.75 : 0.18 + 0.32 * (w / wmax);
      g.lineWidth = on ? 1 + 2.4 * (w / wmax) : 0.6 + 1.6 * (w / wmax);
      g.beginPath(); g.moveTo(x1, y1);
      g.quadraticCurveTo(CX + (x1 + x2 - 2 * CX) * 0.12, CY + (y1 + y2 - 2 * CY) * 0.12, x2, y2); g.stroke();
    });
    // domain arcs
    doms.forEach((dm) => {
      const ids = order.filter((i) => data.nodes[i].d === dm);
      const a0 = ANG[ids[0]] - 0.09, a1 = ANG[ids[ids.length - 1]] + 0.09;
      g.globalAlpha = hover >= 0 && data.nodes[hover].d !== dm ? 0.3 : 0.9;
      g.strokeStyle = css("--d-" + dm); g.lineWidth = 3; g.lineCap = "round";
      g.beginPath(); g.arc(CX, CY, RAD + 13, a0, a1); g.stroke();
    });
    // nodes
    data.nodes.forEach((n, i) => {
      const [x, y] = xy(i), dim = hover >= 0 && i !== hover && !nbr[hover].has(i);
      g.globalAlpha = dim ? 0.25 : 1;
      g.fillStyle = css("--d-" + n.d); g.beginPath(); g.arc(x, y, R[i] + (i === hover ? 2 : 0), 0, 7); g.fill();
      g.lineWidth = 2; g.strokeStyle = sheet; g.stroke();
    });
    // labels, radial
    data.nodes.forEach((n, i) => {
      const dim = hover >= 0 && i !== hover && !nbr[hover].has(i);
      const c = Math.cos(ANG[i]), sn = Math.sin(ANG[i]);
      const lx = CX + c * (RAD + 24), ly = CY + sn * (RAD + 24);
      g.globalAlpha = dim ? 0.3 : 1; g.fillStyle = i === hover ? ink : ink2;
      g.font = (i === hover ? "600 " : "") + "12.5px " + font(); g.textBaseline = "middle";
      g.textAlign = c < -0.2 ? "right" : c > 0.2 ? "left" : "center";
      g.fillText(i === hover ? n.t : (SHORT[n.t] || n.t), lx, ly + (Math.abs(c) <= 0.2 ? sn * 7 : 0));
    });
    g.globalAlpha = 1; g.textAlign = "left";
    if (hover >= 0) {
      g.font = "12px " + font(); g.fillStyle = ink2;
      g.fillText(`${data.nodes[hover].n} 个知识页面 · 与 ${nbr[hover].size} 个专题相互引用`, 14, 22);
    }
  }
  function pick(ev) {
    const r = cv.getBoundingClientRect(), x = ev.clientX - r.left, y = ev.clientY - r.top;
    let best = -1, bd = 1e9;
    data.nodes.forEach((n, i) => {
      const [nx, ny] = xy(i); let d = Math.hypot(nx - x, ny - y);
      const lx = CX + Math.cos(ANG[i]) * (RAD + 40), ly = CY + Math.sin(ANG[i]) * (RAD + 40);
      d = Math.min(d, Math.hypot(lx - x, ly - y) * 0.9);
      if (d < 26 && d < bd) { bd = d; best = i; }
    });
    return best;
  }
  cv.addEventListener("mousemove", (ev) => { const h = pick(ev); if (h !== hover) { hover = h; cv.style.cursor = h >= 0 ? "pointer" : "default"; draw(); } });
  cv.addEventListener("mouseleave", () => { hover = -1; draw(); });
  cv.addEventListener("click", (ev) => { const h = pick(ev); if (h >= 0) location.href = data.nodes[h].id + ".html"; });
  addEventListener("resize", size);
  new MutationObserver(draw).observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
  size();
})();
