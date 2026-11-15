// Generative dendrite drawings for the FlyScope homepage.
// They are schematic illustrations, in the spirit of the paper's schematic
// panels (Figs. 1a, 2a, 3a). They are not reconstructions of named cells; the
// explorer links on the page open the real MaleCNS / FlyWire anatomy.

const DEG = Math.PI / 180;

export function seeded(seed) {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// Grow a dendritic tree in design units. Branching follows the cable budget
// that remains; widths come afterwards from the cable downstream of each point
// (thick trunks, quick narrowing at each fork, hair-fine tips).
export function growTree(spec) {
  const R = seeded(spec.seed || 1);
  const X = [], Y = [], P = [], D = [], G = [];
  const wMin = spec.minWidth ?? 0.42;
  const add = (x, y, p, g) => {
    X.push(x); Y.push(y); P.push(p); G.push(g);
    D.push(p < 0 ? 0 : D[p] + Math.hypot(x - X[p], y - Y[p]));
    return X.length - 1;
  };
  const soma = spec.soma;
  const root = add(soma.x, soma.y, -1, -1);
  const firsts = [];
  spec.primaries.forEach((pr, index) => {
    const cap = X.length + (pr.maxNodes || spec.maxNodesPerPrimary || 14000);
    const g = pr.id ?? index;
    const a = pr.angle * DEG, st = pr.start ?? 0;
    const first = add(soma.x + Math.cos(a) * st, soma.y + Math.sin(a) * st, root, g);
    firsts.push({ node: first, width: pr.width });
    const stack = [{ p: first, x: X[first], y: Y[first], a, budget: pr.length, curve: (pr.curve || 0) * DEG,
      wig: pr.wiggle ?? 1, dens: pr.density ?? 1, spines: pr.spines ?? 1, spread: pr.spread ?? 1,
      keep: pr.keep ?? 0.075, fork: pr.fork ?? 1, maxChild: pr.maxChild ?? spec.maxChild ?? 380, level: 0 }];
    while (stack.length && X.length < cap) {
      const b = stack.pop();
      let { p, x, y, a } = b, heading = a, rem = b.budget, av = 0, since = 0, side = R() < 0.5 ? -1 : 1;
      while (rem > 0 && X.length < cap) {
        const step = Math.min(8, 2.1 + rem * 0.011);
        av += (R() - 0.5) * 0.2 * b.wig; av *= 0.7;
        heading += b.curve * step * (b.level ? 0.4 : 1);
        a += av + (heading - a) * b.keep;
        x += Math.cos(a) * step; y += Math.sin(a) * step;
        p = add(x, y, p, g);
        rem -= step; since += step;
        const interval = Math.min(50, Math.max(7.5, rem * 0.19)) / b.dens;
        if (since > interval * 0.45 && R() < step / interval) {
          if (R() < 0.8) side = -side;
          const cb = Math.min(b.maxChild, rem * (0.22 + R() * 0.4)) * b.fork;
          if (cb > 3) {
            const spread = (0.34 + R() * 0.6) * b.spread;
            stack.push({ ...b, p, x, y, a: a + side * spread, budget: cb, level: b.level + 1 });
            heading -= side * spread * (b.level ? 0.16 : 0.04);
            since = 0;
          }
        }
        if (b.spines && rem < 50 && R() < (step / 9) * b.spines) {
          // Short spines give the fine arbor its soft, fuzzy edge.
          let sa = a + (R() < 0.5 ? -1 : 1) * (0.7 + R() * 0.8), sx = x, sy = y, q = p;
          const n = 1 + (R() * 2 | 0);
          for (let i = 0; i < n; i++) {
            const l = 1.5 + R() * 3; sa += (R() - 0.5) * 0.6;
            sx += Math.cos(sa) * l; sy += Math.sin(sa) * l;
            q = add(sx, sy, q, g);
          }
        }
      }
    }
  });
  const n = X.length, kids = new Uint16Array(n), cable = new Float64Array(n), W = new Float64Array(n);
  for (let i = 1; i < n; i++) kids[P[i]]++;
  for (let i = n - 1; i > 0; i--) { cable[i] += D[i] - D[P[i]]; cable[P[i]] += cable[i]; }
  const exp = spec.taper ?? 0.42;
  for (const f of firsts) {
    const k = (f.width - wMin) / Math.pow(Math.max(1, cable[f.node]), exp);
    const mask = subtreeOf({ n, P }, f.node);
    for (let i = f.node; i < n; i++) if (mask[i]) W[i] = wMin + k * Math.pow(cable[i], exp);
  }
  W[0] = soma.rx || 0;
  let maxD = 0;
  for (let i = 0; i < n; i++) if (D[i] > maxD) maxD = D[i];
  return { X, Y, W, P, D, G, kids, cable, maxD, n };
}

export function subtreeOf(tree, node) {
  const mark = new Uint8Array(tree.n);
  mark[node] = 1;
  for (let i = node + 1; i < tree.n; i++) if (mark[tree.P[i]]) mark[i] = 1;
  return mark;
}

export function nearestNode(tree, x, y, minW = 0, maxW = Infinity) {
  let best = -1, dist = Infinity;
  for (let i = 1; i < tree.n; i++) {
    const w = tree.W[i];
    if (w < minW || w > maxW) continue;
    const d = (tree.X[i] - x) ** 2 + (tree.Y[i] - y) ** 2;
    if (d < dist) { dist = d; best = i; }
  }
  return best;
}

// Choose evenly spaced synapse sites inside a subtree, preferring twig tips.
export function pickSites(tree, mask, { count = 12, gap = 18, seed = 7, terminals = true, maxW = 1.4 } = {}) {
  const R = seeded(seed), pool = [];
  for (let i = 1; i < tree.n; i++) {
    if (mask && !mask[i]) continue;
    if (tree.W[i] > maxW) continue;
    if (terminals && tree.kids[i]) continue;
    pool.push(i);
  }
  for (let i = pool.length - 1; i > 0; i--) { const j = R() * (i + 1) | 0; [pool[i], pool[j]] = [pool[j], pool[i]]; }
  const out = [];
  for (const i of pool) {
    if (out.length >= count) break;
    if (out.every(j => (tree.X[i] - tree.X[j]) ** 2 + (tree.Y[i] - tree.Y[j]) ** 2 > gap * gap)) out.push(i);
  }
  return out;
}

// Path along the arbor between two nodes, through their lowest common ancestor.
export function treePath(tree, u, v) {
  const up = [], down = [], seen = new Map();
  for (let a = u, k = 0; a >= 0; a = tree.P[a], k++) seen.set(a, k);
  let b = v;
  while (!seen.has(b)) { down.push(b); b = tree.P[b]; }
  for (let a = u; a !== b; a = tree.P[a]) up.push(a);
  up.push(b);
  const nodes = up.concat(down.reverse());
  const length = tree.D[u] + tree.D[v] - 2 * tree.D[b];
  return { nodes, length };
}

const STYLES = {
  dark: { body: '#ecebe6', rim: 'rgba(118,118,112,0.95)', hi: 'rgba(255,255,255,0.8)', soma: ['#ffffff', '#e2e1dc', '#8d8c87'], scale: 1, fine: 0.62, glow: 'rgba(216,250,75,0.55)' },
  light: { body: '#1d1f1e', soma: ['#3a3c3b', '#1d1f1e', '#0b0c0b'], scale: 0.9, fine: 0.72 },
  lime: { body: '#414c19', soma: ['#6a7431', '#465220', '#2a3109'], scale: 0.9, fine: 0.78 },
};

export function createNeuronArt(canvas, config) {
  const tree = growTree(config);
  const style = STYLES[config.style || 'dark'];
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const [DW, DH] = config.design || [1600, 1000];
  const ctx = canvas.getContext('2d');
  const state = { mode: config.mode || 'default', layers: { tree: true, sites: true, context: false, ...(config.layers || {}) }, progress: config.reveal && !reduced ? 0 : 1, visible: false };
  let view = { s: 1, ox: 0, oy: 0 }, cw = 0, ch = 0, dpr = 1, cache = null, raf = 0, started = 0, revealStart = 0;

  // Highlighted subtrees and synapse-site groups resolve once against the grown tree.
  const highlights = (config.highlights || []).map(h => {
    const node = h.group != null ? -1 : nearestNode(tree, h.at[0], h.at[1], h.minW ?? 0, h.maxW ?? Infinity);
    const mask = h.group != null ? Uint8Array.from(tree.G, g => g === h.group ? 1 : 0) : subtreeOf(tree, node);
    return { ...h, node, mask };
  });
  const taken = new Uint8Array(tree.n);
  const sites = (config.sites || []).map((s, k) => {
    let mask = null;
    if (s.highlight != null) mask = highlights[s.highlight].mask;
    else if (s.group != null) mask = Uint8Array.from(tree.G, g => g === s.group ? 1 : 0);
    else if (s.at) {
      // Each site group claims its own branch: skip nodes already claimed or whose subtree holds a claimed branch.
      let best = -1, dist = Infinity;
      for (let i = 1; i < tree.n; i++) {
        const w = tree.W[i];
        if (w < (s.minW ?? 0) || w > (s.maxW ?? Infinity) || taken[i]) continue;
        const d = (tree.X[i] - s.at[0]) ** 2 + (tree.Y[i] - s.at[1]) ** 2;
        if (d < dist) { const sub = subtreeOf(tree, i); if (!sub.some((v, j) => v && taken[j])) { dist = d; best = i; } }
      }
      mask = subtreeOf(tree, Math.max(1, best));
      mask.forEach((v, j) => { if (v) taken[j] = 1; });
    }
    const nodes = pickSites(tree, mask, { count: s.count, gap: s.gap, seed: (config.seed || 1) * 31 + k, terminals: s.terminals ?? true, maxW: s.siteMaxW ?? 1.4 });
    return { ...s, nodes };
  });
  const context = (() => {
    const R = seeded((config.seed || 1) + 991), pts = [];
    for (let i = 0; i < 220; i++) pts.push([R() * DW, R() * DH, 1.2 + R() * 2.2]);
    return pts;
  })();
  // Paths from every A site to its nearest B site along the receiving arbor.
  function sitePaths() {
    const a = sites.find(s => s.key === 'A'), b = sites.find(s => s.key === 'B');
    if (!a || !b || !b.nodes.length) return [];
    return a.nodes.map(u => b.nodes.map(v => treePath(tree, u, v)).sort((p, q) => p.length - q.length)[0]);
  }
  const paths = sitePaths();
  const pulses = (() => {
    const h = highlights.find(x => x.pulse);
    if (!h) return [];
    const tips = sites.find(s => s.highlight === highlights.indexOf(h))?.nodes || [];
    return tips.map(t => { const nodes = []; for (let a = t; a > 0; a = tree.P[a]) nodes.push(a); return { nodes, length: tree.D[t] }; });
  })();

  const px = i => tree.X[i] * view.s + view.ox;
  const py = i => tree.Y[i] * view.s + view.oy;

  function layout() {
    const r = canvas.getBoundingClientRect();
    cw = Math.max(1, r.width); ch = Math.max(1, r.height);
    dpr = Math.min(2, window.devicePixelRatio || 1);
    canvas.width = Math.round(cw * dpr); canvas.height = Math.round(ch * dpr);
    const compact = cw < 760 || (cw < 1100 && ch > cw * 0.9 && config.mobileWhenPortrait !== false);
    const fit = (compact && config.mobile) ? { ...config.fit, ...config.mobile } : (config.fit || {});
    const [ax, ay] = fit.anchor || [0.5, 0.5];
    const base = fit.mode === 'contain' ? Math.min(cw / DW, ch / DH) : fit.mode === 'width' ? cw / DW : Math.max(cw / DW, ch / DH);
    const s = base * (fit.zoom || 1);
    view = { s, ox: ax * cw - ax * DW * s + (fit.dx || 0) * cw, oy: ay * ch - ay * DH * s + (fit.dy || 0) * ch };
    cache = null;
  }

  function lineWidth(w) { return Math.max(0.55, w * view.s * style.scale * (config.weight || 1)); }

  // Width-bucketed strokes: thousands of segments become a few dozen paths.
  function strokeTree(g, cutoff, skip, color, widthFn, offset = 0, alpha = 1, fine = style.fine ?? 1) {
    const buckets = new Map();
    for (let i = 1; i < tree.n; i++) {
      const p = tree.P[i];
      if (p < 0 || tree.D[i] > cutoff || (skip && skip(i))) continue;
      const w = widthFn(tree.W[i]);
      if (w <= 0) continue;
      const key = Math.round(w * 4) / 4;
      let path = buckets.get(key);
      if (!path) { path = new Path2D(); buckets.set(key, path); }
      const o = offset * key;
      path.moveTo(px(p) + o, py(p) + o); path.lineTo(px(i) + o, py(i) + o);
    }
    g.save(); g.strokeStyle = color; g.lineCap = 'round'; g.lineJoin = 'round';
    // Hair-fine twigs recede a little, so trunks read first and the arbor gains depth.
    for (const [w, path] of buckets) { g.globalAlpha = alpha * (w < 1.3 ? fine : w < 2 ? (1 + fine) / 2 : 1); g.lineWidth = w; g.stroke(path); }
    g.restore();
  }

  function drawSoma(g, alpha) {
    const s = config.soma;
    if (!s.rx) return;
    const x = s.x * view.s + view.ox, y = s.y * view.s + view.oy, rx = s.rx * view.s, ry = (s.ry || s.rx) * view.s;
    g.save(); g.globalAlpha = alpha; g.translate(x, y); g.rotate((s.angle || 0) * DEG);
    const grad = g.createRadialGradient(-rx * 0.35, -ry * 0.45, rx * 0.1, 0, 0, Math.max(rx, ry) * 1.15);
    grad.addColorStop(0, style.soma[0]); grad.addColorStop(0.55, style.soma[1]); grad.addColorStop(1, style.soma[2]);
    g.fillStyle = grad; g.beginPath(); g.ellipse(0, 0, rx, ry, 0, 0, Math.PI * 2); g.fill();
    g.restore();
  }

  function dot(g, x, y, r, color, ring, halo) {
    if (halo) { g.save(); g.globalAlpha = 0.22; g.beginPath(); g.arc(x, y, r * 2.1, 0, Math.PI * 2); g.fillStyle = color; g.fill(); g.restore(); }
    g.beginPath(); g.arc(x, y, r, 0, Math.PI * 2); g.fillStyle = color; g.fill();
    if (ring) { g.lineWidth = Math.max(1, r * 0.28); g.strokeStyle = ring; g.stroke(); }
  }

  function siteRadius(s) { return Math.max(s.minR ?? 3, (s.r ?? 4.6) * view.s); }

  function drawScene(g, t) {
    const cutoff = tree.maxD * t, mode = state.mode, L = state.layers;
    g.setTransform(dpr, 0, 0, dpr, 0, 0);
    g.clearRect(0, 0, cw, ch);
    const dim = config.dimIn?.includes(mode) ? 0.38 : 1;
    if (L.context) for (const [x, y, r] of context) dot(g, x * view.s + view.ox, y * view.s + view.oy, Math.max(1, r * view.s), config.contextColor || 'rgba(160,160,155,.35)');
    const hiMask = new Uint8Array(tree.n);
    const activeHighlights = highlights.filter(h => !h.modes || h.modes.includes(mode));
    for (const h of activeHighlights) for (let i = 0; i < tree.n; i++) if (h.mask[i]) hiMask[i] = 1;
    const skip = i => hiMask[i];
    if (L.tree) {
      if (style.rim) strokeTree(g, cutoff, skip, style.rim, w => { const l = lineWidth(w); return l > 1.25 ? l + 0.9 : 0; }, 0, dim);
      strokeTree(g, cutoff, skip, style.body, lineWidth, 0, dim);
      if (style.hi) strokeTree(g, cutoff, skip, style.hi, w => { const l = lineWidth(w); return l > 2.6 ? l * 0.32 : 0; }, -0.42, dim);
      for (const h of activeHighlights) {
        const mask = h.mask;
        if (style.glow) { g.save(); g.shadowColor = style.glow; g.shadowBlur = 9; }
        strokeTree(g, cutoff, i => !mask[i], h.color, w => lineWidth(w) * (h.widthScale || 1) + (h.widthAdd || 0), 0, 1, 1);
        if (style.glow) g.restore();
      }
      drawSoma(g, dim);
    }
    if (config.marker && t >= 1) {
      const m = config.marker, h = m.highlight != null ? highlights[m.highlight] : null;
      const mx = h ? px(h.node) : m.at[0] * view.s + view.ox, my = h ? py(h.node) : m.at[1] * view.s + view.oy, half = Math.max(7, m.size * view.s) / 2;
      g.save(); g.strokeStyle = m.color; g.lineWidth = 1.3;
      g.strokeRect(mx - half, my - half, half * 2, half * 2);
      if (m.target) {
        const a = canvas.getBoundingClientRect(), b = m.target.getBoundingClientRect();
        if (b.width) {
          g.beginPath(); g.moveTo(mx + half * 0.7, my + half);
          g.lineTo(b.left - a.left + b.width * (m.tx ?? 0.3), b.top - a.top); g.stroke();
        }
      }
      g.restore();
    }
    if (config.pathsIn?.includes(mode) && t >= 1) {
      g.save(); g.lineCap = 'round'; g.lineJoin = 'round';
      for (const path of paths) {
        g.beginPath();
        path.nodes.forEach((n, k) => k ? g.lineTo(px(n), py(n)) : g.moveTo(px(n), py(n)));
        g.strokeStyle = config.pathColor || '#d8fa4b'; g.lineWidth = Math.max(1.4, (config.pathWidth ?? 2.6) * view.s); g.globalAlpha = 0.95; g.stroke();
      }
      g.restore();
    }
    if (L.sites) {
      const visible = sites.filter(s => !s.modes || s.modes.includes(mode));
      const pop = config.reveal && !reduced ? Math.max(0, Math.min(1, (t - 0.82) / 0.18)) : 1;
      for (const s of visible) {
        const color = s.colors?.[mode] || s.color, r = siteRadius(s) * pop;
        if (r <= 0) continue;
        s.nodes.forEach((n, k) => dot(g, px(n), py(n), r, s.palette ? s.palette[k % s.palette.length] : color, s.ring, !!style.glow));
      }
    }
  }

  function frame(now) {
    raf = 0;
    if (!cw) layout();
    if (state.progress < 1) {
      // The arbor grows from the soma only once the drawing is on screen.
      if (!state.visible) { drawScene(ctx, 0); return; }
      if (!revealStart) revealStart = now;
      const x = Math.min(1, (now - revealStart) / (config.revealMs || 1900));
      state.progress = 1 - Math.pow(1 - x, 3);
      drawScene(ctx, state.progress);
      if (state.progress < 1) { raf = requestAnimationFrame(frame); return; }
    }
    if (!cache) {
      cache = document.createElement('canvas');
      cache.width = canvas.width; cache.height = canvas.height;
      drawScene(cache.getContext('2d'), 1);
    }
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(cache, 0, 0);
    if (pulses.length && !reduced && state.visible) {
      if (!started) started = now;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      const period = 3600;
      pulses.forEach((p, k) => {
        const f = (((now - started) / period) + k / pulses.length) % 1;
        const along = p.length * f;
        // Inputs travel from the twig tip towards the soma.
        let i = 0;
        while (i < p.nodes.length - 1 && p.length - tree.D[p.nodes[i]] < along) i++;
        const n = p.nodes[i];
        const x = px(n), y = py(n), fade = Math.sin(Math.PI * f);
        const glow = ctx.createRadialGradient(x, y, 0, x, y, 14);
        glow.addColorStop(0, `rgba(216,250,75,${0.85 * fade})`); glow.addColorStop(1, 'rgba(216,250,75,0)');
        ctx.fillStyle = glow; ctx.beginPath(); ctx.arc(x, y, 14, 0, Math.PI * 2); ctx.fill();
        dot(ctx, x, y, 2.4, `rgba(244,255,200,${fade})`);
      });
      raf = requestAnimationFrame(frame);
    }
  }

  function redraw() { if (!raf) raf = requestAnimationFrame(frame); }

  const resize = new ResizeObserver(() => { layout(); redraw(); });
  resize.observe(canvas);
  if (config.marker?.target) resize.observe(config.marker.target);
  const io = new IntersectionObserver(entries => {
    for (const e of entries) {
      state.visible = e.isIntersecting;
      if (e.isIntersecting) redraw();
    }
  }, { threshold: 0.12 });
  io.observe(canvas);

  return {
    tree, sites, paths,
    setMode(mode) { state.mode = mode; cache = null; redraw(); },
    setLayer(name, on) { state.layers[name] = on; cache = null; redraw(); },
    redraw() { cache = null; redraw(); },
    destroy() { resize.disconnect(); io.disconnect(); cancelAnimationFrame(raf); },
  };
}
