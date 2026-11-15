const $ = id => document.getElementById(id);
const LIME = '#d8fa4b', LAVENDER = '#ada4e4', VIOLET = '#b98cf2';
const CIRCUIT = 'male:1050379364:13030:15800';   // AN19B014 → DNge006 → DNge072, the paper example
const IDS = { receiver: '15800', partner: '13030', source: '1050379364' };

// English copy lives in the HTML; Chinese replaces it in place.
const ZH = {
  skip: '跳至正文', home: 'FlyScope 首页', sections: '页面分区', menu: '菜单',
  explorerName: '连接组浏览器', explorerCaps: '连接组浏览器',
  navExplore: '探索', navCircuits: '回路', navFindings: '论文发现', navData: '数据与来源', launch: '进入探索',
  navQuestion: '问题', navPaper: '论文', language: '语言', readStudy: '阅读研究',
  authorName: '张锡哲',
  heroTitle: '网络拓扑<br>映现在<br>神经元内部。', heroLead: '神经元内部的输入位置，映照着网络中远处的连接。',
  heroKicker: '01 / 连接组浏览器', scroll: '向下滚动',
  exploreKicker: '06 / 探索', exploreTitle: '探索连接组。', exploreLead: '找到一个神经元，追踪它的连接。',
  fit: '适配选区', library: '神经元目录', search: '搜索类型或 ID', circuitsTab: '回路', allNeurons: '所有神经元',
  sensory: '感觉', visual: '视觉', ascending: '上行', descending: '下行', interneuron: '中间神经元', motor: '运动',
  selected: '已选神经元', inScene: '场景中', skeletons: '骨架', synapsePairs: '突触对', somaContext: '胞体背景',
  connectivity: '连接', connections: '连接', sharedInput: '共享输入', inputPartners: '输入伙伴', outputPartners: '输出伙伴',
  records120: '120 条记录', records80: '80 条记录', outputNote: '在浏览器中打开 DNge072，查看全部输出伙伴',
  inputOutput: '输入 + 输出', allRegions: '全部脑区', compareWith: '比较对象', factSources: '个共享来源，在 DNge072 上共 282 条输入记录',
  factShared: '共享来源输入到最近 DNge006 输入的平均路径（GNG）', factOther: '其他非 DN 输入', openOnC: 'C 上的 A + B 输入',
  morphology: '形态', connectivityTab: '连接', previewMode: '预览模式', previewLabel: '界面预览 · 示意形态',
  previewArt: '示意性接收神经元及突触位点',
  sharedKicker: '03 / 共享输入', sharedTitle: '一个接收者，多路输入。', sharedHeading: '共享输入',
  sharedStrong: '查看来源在哪里交汇。', sharedText: '比较同一接收神经元上的输入位置。与伙伴 B 共享的来源，其输入更靠近 B 的输入。',
  legend: '图例', receiverC: '接收者 C', sourceA: '来源 A', partnerB: '伙伴 B', drawingMode: '绘制模式',
  receiverView: '接收者视图', inputSites: '输入位点', paths: '路径', openShared: '打开共享输入',
  captionReceiver: '仅显示接收者 C：所有输入都落在这一棵连续的树突上。',
  captionSites: '每个点是接收者 C 上的一个输入，按来源着色。',
  captionPaths: '每条线沿 C 的树突，从来源 A 的输入走到最近的伙伴 B 输入——论文测量的正是这段距离。',
  sharedArt: '示意性接收者 C，以及来自来源 A 与伙伴 B 的输入', schematic: '示意图 · 非比例绘制',
  findingsKicker: '04 / 论文发现', findingsTitle: '追踪这一发现。', findingsLead: '从网络连接，到输入位置。',
  step1: '网络拓扑', step2: '接收神经元', step3: '输入组织', openExample: '打开论文案例', inputLocations: '输入位置',
  findingsArt: '示意性接收神经元，其中一条输入分支被高亮', schematicShort: '示意图',
  caption0: '从一个回路，走到它的接收神经元。',
  caption1: '共享来源的输入更靠近伙伴的输入：MaleCNS 中近 9.4 µm，FlyWire 中近 8.0 µm。',
  caption2: '固定 A 在 C 上的输入位置，与来源相连的伙伴仍更近：分别近 9.14 µm 与 10.15 µm。',
  caption3: '输入分布有助于预测未见过的连接：MaleCNS 中平均精度由 0.089 提升到 0.161。',
  dataTitle: '从一个神经元开始。', dataLead: '选择数据集，探索它的连接。',
  dMale: '雄性中枢 · v1.0 · 共享来源近 9.42 µm', dFlywire: '雌性脑 · v783 · 共享来源近 7.98 µm',
  dWorm: '成体 · 数据集 7 与 8 · 探索性，10 与 13 个接收者', dPlaty: '幼体投射神经元 · 样本过少，无法判断',
  paperExample: '论文案例', close: '关闭',
  sourcesKicker: '数据与来源', sourcesTitle: '公开重建数据，原样使用。',
  sourcesIntro: 'FlyScope 直接读取已发布的连接组数据，不做修改。没有采集新的动物；每个数据集代表一个个体。',
  srcMale: '一只雄性果蝇的完整中枢神经系统：接触记录（置信度 ≥ 0.5）、注释与骨架。',
  srcFlywire: '一只雌性果蝇的脑：突触、连接、匹配骨架与注释。',
  srcBanc: '脑—腹神经索网络背景与已鉴定的腹神经索输出分析。',
  srcWorm: '两个成体重建，用于探索性的位置比较。', srcPlaty: '三日龄幼体头—躯干投射群体；样本稀疏，属探索性分析。',
  sourcesNote: '本页的神经元图为示意插图；浏览器中显示的是记录到的骨架与突触坐标。', paperLabel: '论文',
  // 02 · The question
  questionKicker: '02 / 问题', questionTitle: '走进<br>节点内部。',
  questionLead: '连接图把每个神经元画成一个点。而在神经元内部，每一路输入都落在分支的某个位置。这种内部排布，是否记录着网络中别处的连接？',
  q1t: '固定一条连接。', q1: '伙伴 B 连接接收神经元 C：单向至少 5 条接触记录，反向少于 5 条。',
  q2t: '标出输入位置。', q2: '把 C 上每个来源输入沿 C 自身的分支，测量到同一脑区内最近的 B 输入。',
  q3t: '读出远处的边。', q3: '与 B 相连的来源——这条边并不经过 C——其输入更靠近 B 的输入。仅凭输入分布，就能预测未见来源的 A→B 连接。',
  netA: '来源 A', netB: '伙伴 B', netC: '接收者 C', insideC: 'C 的内部',
  lensCaption: 'A→B 这条边不经过 C，却体现在 A 与 B 落在 C 上的位置。', inputsA: '来自 A 的输入', inputsB: '来自 B 的输入', inputsOther: '其他输入',
  heldLabel: '保持不变', held1: '接收者与脑区', held2: '沿 C 自身分支的路径', held3: '拟合时留出的来源细胞',
  // 05 · Results
  resultsKicker: '05 / 结果', resultsTitle: '两个果蝇脑，同一方向。',
  resultsLead: '在 MaleCNS 与 FlyWire 中，同一关系经受住了三项逐步收紧的检验。',
  r1k: '来源之间', r1t: '共享来源更靠近', r1q: 'C 上来源输入到最近伙伴输入的平均路径：同时连接 B 的来源，对比其他所有来源。',
  r1s1: 'MaleCNS · 95% 区间 −10.52 至 −8.31', r1s2: 'FlyWire · 95% 区间 −9.27 至 −6.70',
  r1n: '在 1,079 个 MaleCNS 接收者中 82.7%、720 个 FlyWire 接收者中 80.7% 为负值；分别涉及 13,318 与 5,807 条连接。',
  r2k: '固定输入', r2t: '输入不变，伙伴不同', r2q: '固定来源 A、接收者 C 及 A 的输入；比较接收 A 输入与没有 A 输入的伙伴，各取三个参考位点。',
  r2s1: 'MaleCNS · 95% 区间 −11.21 至 −7.07', r2s2: 'FlyWire · 95% 区间 −12.15 至 −8.14',
  r2n: '922 个 MaleCNS 接收者中有 749 个、589 个 FlyWire 接收者中有 483 个呈相同顺序。',
  r3k: '未见来源', r3t: '输入分布预测连接', r3q: '依据已知接收者上的输入分布，预测 200 个测试来源的 A→B 连接；测试来源与 200 个训练来源互不重叠。',
  r3s1: 'MaleCNS · 仅用计数与大小时为 0.089', r3s2: 'FlyWire · 原为 0.069',
  r3n: '对数损失 0.184 → 0.165 与 0.142 → 0.125；分别评估 30,702 与 21,822 对。点估计来自每个样本的一次来源划分。',
  resultsAside: '在果蝇脑之外，两个成体秀丽隐杆线虫重建也给出负的来源内差值（10 与 13 个接收者）；一个阔沙蚕幼体群体样本过少，无法判断。这些都是单个样本内的关联：解剖上的机会、选择性连接，或两者兼有，都与结果相容。',
  chShared: '共享来源', chOther: '其他来源', chConn: '接收 A 输入的伙伴', chUnconn: '没有 A 输入的伙伴',
  chMaps: '加入输入分布', chBase: '仅计数与大小', chChance: '随机水平',
  // 08 · The paper
  paperKicker: '08 / 论文', paperTitle: '阅读这项研究。', manuscript: '手稿，2026', abstractLabel: '摘要',
  abstract: '神经元连接图记录了哪些细胞彼此相连，却丢弃了输入进入接收神经元的位置。我们追问：这种内部排布是否包含输入神经元彼此之间连接的信息。在两个成年果蝇连接组中，与某个下行神经元伙伴相连的来源，其输入在共享接收者上更靠近该伙伴的输入：平均路径距离差在 MaleCNS 中为 9.4 µm，在 FlyWire 中为 8.0 µm。固定来源输入位置并标准化参考位点数量后，这一关系在不同伙伴之间依然成立。随后，我们利用已知接收者上按来源标注的输入分布，预测未参与模型拟合的来源细胞之间的连接。在输入计数与接收者大小之外加入空间分布与距离特征，平均精度在 MaleCNS 中由 0.089 提升到 0.161，在 FlyWire 中由 0.069 提升到 0.114，两个数据集的概率损失也都更低。预测综合了所有符合条件的共享接收者的信息。这些结果把神经元内部的输入组织与其来源之间的连接联系起来，并表明这种空间信息可用于推断未见输入细胞之间的连接。',
  kw1: '突触组织', kw2: '连接组学', kw3: '物理网络', kw4: '下行神经元', kw5: '果蝇',
  deeper: '深入了解', d1t: '进入浏览器', d1: '165,122 个已追踪的 MaleCNS 神经元，及其突触与连接伙伴。',
  d2t: '打开论文回路', d2: 'AN19B014 → DNge006 → DNge072 在物理空间中的样子。',
  d3t: 'C 上的 A + B 输入', d3: 'DNge072 按到最近 DNge006 输入的路径着色。',
  d4t: '数据与来源', d4: 'FlyScope 读取的公开数据，原样使用。',
  cite: '引用本研究', manuscriptCite: '手稿', copyBib: '复制 BibTeX', copied: '已复制',
};
const CAPTIONS = { receiver: 'captionReceiver', sites: 'captionSites', paths: 'captionPaths' };
const EN = {
  captionReceiver: 'Receiver C alone: one continuous arbor on which every input lands.',
  captionSites: 'Each point is an input on receiver C, coloured by its source.',
  captionPaths: 'Each line follows C’s arbor from a source-A input to the nearest partner-B input: the distance the paper measures.',
  caption0: 'Move from a circuit to its receiving neuron.',
  caption1: 'Shared-source inputs lie nearer partner inputs: 9.4 µm nearer in MaleCNS, 8.0 µm in FlyWire.',
  caption2: 'With A’s inputs on C held fixed, source-connected partners stay nearer: 9.14 µm and 10.15 µm.',
  caption3: 'Input maps help predict unseen connections: average precision rises from 0.089 to 0.161 in MaleCNS.',
  chShared: 'Shared sources', chOther: 'Other sources', chConn: 'Partners receiving A', chUnconn: 'Partners without A',
  chMaps: 'With input maps', chBase: 'Counts and size only', chChance: 'Chance',
  copyBib: 'Copy BibTeX', copied: 'Copied',
};

// Results bars, to scale. Means from the paper (Figs. 1c, 2b,c, 3e); chance is the positive rate.
const CHARTS = {
  r1: { max: 80, keys: ['chShared', 'chOther'], axis: ['0', '80 µm'], fmt: v => `${v.toFixed(1)} µm`,
    rows: [['MaleCNS', 60.77, 70.18], ['FlyWire', 51.37, 59.36]] },
  r2: { max: 80, keys: ['chConn', 'chUnconn'], axis: ['0', '80 µm'], fmt: v => `${v.toFixed(1)} µm`,
    rows: [['MaleCNS', 64.40, 73.54], ['FlyWire', 62.79, 72.93]] },
  r3: { max: 0.2, keys: ['chMaps', 'chBase'], tick: 'chChance', axis: ['0', '0.2 AP'], fmt: v => v.toFixed(3),
    rows: [['MaleCNS', 0.161, 0.089, 0.043], ['FlyWire', 0.114, 0.069, 0.0308]] },
};

function initialLocale() {
  const q = new URLSearchParams(location.search).get('lang');
  if (q === 'zh' || q === 'en') return q;
  try { return localStorage.getItem('flyscope.language') === 'en' ? 'en' : 'zh'; } catch { return 'zh'; }
}
let locale = initialLocale();
const t = key => (locale === 'zh' ? ZH[key] : EN[key]) ?? key;

function href(key) {
  // The interactive browser runs on the research server; inside the handbook these links lead to the
  // explore and data sections of this page.
  return ['flywire', 'celegans', 'platynereis'].includes(key) ? '#data' : '#explore';
}

function applyLocale() {
  document.documentElement.lang = locale === 'zh' ? 'zh-CN' : 'en';
  document.title = locale === 'zh' ? 'FlyScope · 连接组浏览器' : 'FlyScope · Connectome Explorer';
  document.querySelectorAll('[data-t]').forEach(el => {
    const html = el.hasAttribute('data-t-html');
    if (el.dataset.en == null) el.dataset.en = html ? el.innerHTML : el.textContent;
    const key = el.dataset.t, value = locale === 'zh' ? (ZH[key] ?? el.dataset.en) : (EN[key] ?? el.dataset.en);
    if (html) el.innerHTML = value; else el.textContent = value;
  });
  document.querySelectorAll('[data-t-aria]').forEach(el => {
    if (el.dataset.enAria == null) el.dataset.enAria = el.getAttribute('aria-label') || '';
    el.setAttribute('aria-label', locale === 'zh' ? (ZH[el.dataset.tAria] ?? el.dataset.enAria) : el.dataset.enAria);
  });
  document.querySelectorAll('[data-href]').forEach(el => { el.href = href(el.dataset.href); });
  document.querySelectorAll('[data-lang]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.lang === locale)));
}

function setLocale(next) {
  locale = next;
  try { localStorage.setItem('flyscope.language', next); } catch { /* private mode */ }
  const url = new URL(location.href);
  url.searchParams.set('lang', next);
  history.replaceState(null, '', url.pathname + url.search + url.hash);
  applyLocale();
}

// ── Header: theme and active section follow what sits beneath it ──
function initHeader() {
  const header = $('site-header');
  const blocks = [...document.querySelectorAll('main > section, .site-footer')];
  const links = [...header.querySelectorAll('.site-nav a')];
  let ticking = false;
  function update() {
    ticking = false;
    const probe = header.offsetHeight * 0.55;
    const current = blocks.find(b => { const r = b.getBoundingClientRect(); return r.top <= probe && r.bottom > probe; }) || blocks[0];
    header.dataset.theme = current.dataset.theme || 'dark';
    header.dataset.top = String(current.dataset.top === 'true');
    links.forEach(a => { if (a.dataset.nav === current.dataset.nav) a.setAttribute('aria-current', 'true'); else a.removeAttribute('aria-current'); });
  }
  addEventListener('scroll', () => { if (!ticking) { ticking = true; requestAnimationFrame(update); } }, { passive: true });
  addEventListener('resize', update);
  update();

  const toggle = $('menu-toggle'), menu = $('mobile-menu');
  const setMenu = open => { menu.hidden = !open; toggle.setAttribute('aria-expanded', String(open)); document.body.style.overflow = open ? 'hidden' : ''; };
  toggle.addEventListener('click', () => setMenu(menu.hidden));
  menu.addEventListener('click', e => { if (e.target.closest('a')) setMenu(false); });
  addEventListener('keydown', e => { if (e.key === 'Escape' && !menu.hidden) { setMenu(false); toggle.focus(); } });
  matchMedia('(min-width: 1181px)').addEventListener('change', e => { if (e.matches) setMenu(false); });
}

// ── Schematic arbors: generated drawings in the spirit of the paper's schematic panels ──
async function initArt() {
  // Optional drawings must not block native links, language or menu controls.
  const { createNeuronArt } = await import('./neuron-art.js');
  const arts = {};
  arts.hero = createNeuronArt($('art-hero'), {
    seed: 11, style: 'dark', design: [1600, 880], reveal: true, revealMs: 2200,
    fit: { anchor: [0.84, 0.36] }, mobile: { anchor: [0.8, 0.42], zoom: 0.62 },
    soma: { x: 1336, y: 338, rx: 24, ry: 18, angle: -58 },
    primaries: [
      { angle: -47, length: 1000, width: 8.6, curve: -0.006, maxChild: 230 },
      { angle: -121, length: 720, width: 6.4, curve: 0.006, maxChild: 220 },
      { angle: -170, length: 700, width: 4.6, curve: -0.006, maxChild: 200 },
      { id: 'hl', angle: 163, length: 360, width: 3, density: 0.6, spines: 0, wiggle: 0.5, spread: 1.2, keep: 0.12, maxChild: 30 },
      { angle: 108, length: 1500, width: 10.5, curve: 0.042, maxChild: 250, maxNodes: 16000 },
      { angle: 26, length: 700, width: 5.6, curve: 0.012, maxChild: 210 },
      { angle: 66, length: 520, width: 4.2, maxChild: 190 },
      { angle: -10, length: 400, width: 3.6, maxChild: 170 },
    ],
    highlights: [{ group: 'hl', color: LIME, pulse: true, widthScale: 0.92 }],
    sites: [{ highlight: 0, count: 6, gap: 34, color: LIME, r: 4.6, minR: 3.4, siteMaxW: 3 }],
  });

  // Inside node C: A's inputs (lime) sit on branches next to B's (lavender); lines follow C's branches between them.
  arts.lens = createNeuronArt($('art-lens'), {
    seed: 41, style: 'dark', design: [300, 300], reveal: true, revealMs: 1700, mode: 'lens', weight: 0.95,
    fit: { mode: 'contain', anchor: [0.5, 0.5] },
    soma: { x: 66, y: 226, rx: 9, ry: 7, angle: -34 },
    primaries: [
      { angle: -40, length: 420, width: 4.8, curve: 0.008, maxChild: 150, density: 1.2, maxNodes: 6000 },
      { angle: -96, length: 240, width: 3.3, curve: -0.02, maxChild: 100, density: 1.2 },
      { angle: 8, length: 260, width: 3.3, curve: 0.01, maxChild: 100, density: 1.2 },
      { angle: 62, length: 110, width: 2.4 },
      { angle: 160, length: 70, width: 2 },
    ],
    sites: [
      { key: 'A', at: [150, 118], minW: 1.3, maxW: 3.4, count: 7, gap: 11, r: 3.8, minR: 2.6, color: LIME, terminals: false, siteMaxW: 1.05 },
      { key: 'B', at: [196, 150], minW: 1.3, maxW: 3.4, count: 6, gap: 11, r: 3.8, minR: 2.6, color: LAVENDER, terminals: false, siteMaxW: 1.05 },
      // Inputs from other sources land elsewhere on C.
      { at: [210, 250], minW: 1, maxW: 3, count: 5, gap: 16, r: 3.2, minR: 2.2, color: 'rgba(244,244,239,.62)', terminals: false, siteMaxW: 1.05 },
      { at: [70, 80], minW: 1, maxW: 3, count: 5, gap: 16, r: 3.2, minR: 2.2, color: 'rgba(244,244,239,.62)', terminals: false, siteMaxW: 1.05 },
    ],
    pathsIn: ['lens'], pathColor: LIME, pathWidth: 1.7,
  });

  arts.preview = createNeuronArt($('art-preview'), {
    seed: 29, style: 'dark', design: [900, 485], reveal: true, revealMs: 1600, weight: 0.92,
    fit: { mode: 'contain', anchor: [0.5, 0.5] }, mode: 'morphology',
    soma: { x: 200, y: 330, rx: 11, ry: 9, angle: -40 },
    primaries: [
      { angle: -106, length: 330, width: 4.2, curve: -0.04, maxChild: 140 },
      { angle: -20, length: 640, width: 5, curve: 0.02, density: 1.25, maxChild: 190, maxNodes: 7000 },
      { angle: -66, length: 300, width: 3.2, maxChild: 130 },
      { angle: 94, length: 170, width: 2.8 },
      { angle: 140, length: 170, width: 2.4 },
      { angle: 50, length: 190, width: 2.6 },
    ],
    sites: [
      { at: [120, 90], minW: 1.6, maxW: 4, count: 22, gap: 11, r: 3.2, minR: 2.2, color: LIME, terminals: false, siteMaxW: 1.1 },
      { at: [620, 250], minW: 1.6, maxW: 4, count: 18, gap: 11, r: 3.2, minR: 2.2, color: LIME, colors: { connectivity: LAVENDER, shared: LAVENDER }, terminals: false, siteMaxW: 1.1 },
      { at: [800, 330], minW: 1.4, maxW: 4, count: 14, gap: 11, r: 3.2, minR: 2.2, color: LIME, modes: ['morphology', 'connectivity'], terminals: false, siteMaxW: 1.1 },
    ],
    contextColor: 'rgba(200,200,194,.26)',
  });

  arts.shared = createNeuronArt($('art-shared'), {
    seed: 47, style: 'dark', design: [1600, 690], reveal: true, revealMs: 2000, mode: 'sites',
    fit: { anchor: [0.08, 0.84] }, mobile: { mode: 'contain', anchor: [0.5, 0.5] },
    soma: { x: 131, y: 578, rx: 21, ry: 16, angle: -34 },
    primaries: [
      { angle: -20, length: 1900, width: 10.5, curve: 0.002, keep: 0.12, maxChild: 290, maxNodes: 16000 },
      { angle: -118, length: 420, width: 4.6 },
      { angle: 196, length: 260, width: 3.2 },
      { angle: 112, length: 200, width: 3 },
      { angle: 40, length: 300, width: 3.4 },
    ],
    sites: [
      { key: 'A', at: [840, 300], minW: 2.4, maxW: 5.2, count: 30, gap: 14, r: 4.8, minR: 3, color: LIME, modes: ['sites', 'paths'], terminals: false, siteMaxW: 1.3 },
      { key: 'B', at: [1040, 390], minW: 2.4, maxW: 5.2, count: 26, gap: 14, r: 4.6, minR: 3, color: LAVENDER, modes: ['sites', 'paths'], terminals: false, siteMaxW: 1.3 },
    ],
    dimIn: ['paths'], pathsIn: ['paths'], pathColor: LIME,
  });

  arts.findings = createNeuronArt($('art-findings'), {
    seed: 63, style: 'light', design: [1600, 940], reveal: true, revealMs: 2000, mobileWhenPortrait: false,
    fit: { anchor: [0.36, 0.84] }, mobile: { mode: 'contain', anchor: [0.5, 0.5], zoom: 1.5, dx: -0.12 },
    soma: { x: 565, y: 790, rx: 15, ry: 11, angle: -40 },
    primaries: [
      { angle: -38, length: 1550, width: 6.4, curve: 0.004, maxChild: 280, maxNodes: 14000 },
      { angle: -78, length: 470, width: 4.2, curve: 0.01, maxChild: 200 },
      { angle: 186, length: 300, width: 3 },
      { angle: 122, length: 260, width: 2.8 },
      { angle: 72, length: 220, width: 2.4 },
    ],
    highlights: [{ at: [1010, 540], minW: 2, maxW: 3.6, color: '#cdf23e', widthScale: 1.5, widthAdd: 0.6 }],
    marker: { highlight: 0, size: 20, color: '#0e100f', target: $('inset'), tx: 0.3 },
  });

  arts.inset = createNeuronArt($('art-inset'), {
    seed: 5, style: 'dark', design: [504, 249], reveal: true, revealMs: 1300, minWidth: 1.1,
    fit: { mode: 'cover', anchor: [0.5, 0.5] },
    soma: { x: -24, y: 252, rx: 0 },
    primaries: [{ angle: -25, length: 640, width: 9.5, density: 0.5, spines: 0, wiggle: 0.7, spread: 1.15 }],
    sites: [{ count: 9, gap: 46, r: 6.2, minR: 4, color: LIME, palette: [LIME, VIOLET], siteMaxW: 9, group: 0 }],
  });

  arts.data = createNeuronArt($('art-data'), {
    seed: 81, style: 'lime', design: [1600, 712], reveal: true, revealMs: 2000, weight: 0.85,
    fit: { anchor: [0.89, 0.39] }, mobile: { anchor: [0.8, 0.3], zoom: 0.8 },
    soma: { x: 1422, y: 280, rx: 13, ry: 17, angle: 20 },
    primaries: [
      { angle: -62, length: 420, width: 3.4 },
      { angle: -146, length: 640, width: 4 },
      { angle: 154, length: 940, width: 5, curve: -0.006 },
      { angle: 102, length: 560, width: 4.2 },
      { angle: 128, length: 700, width: 4.2 },
      { angle: 14, length: 340, width: 3 },
      { angle: 58, length: 420, width: 3.2 },
    ],
  });
  return arts;
}

function initPreview(art) {
  const preview = $('preview');
  $('preview-tree').addEventListener('click', e => {
    const button = e.target.closest('button');
    if (!button) return;
    const list = button.nextElementSibling;
    if (!list) { location.href = href('explorer'); return; }
    const open = button.getAttribute('aria-expanded') !== 'true';
    button.setAttribute('aria-expanded', String(open));
    list.hidden = !open;
  });
  preview.querySelectorAll('[data-layer]').forEach(input => input.addEventListener('change', () => art.setLayer(input.dataset.layer, input.checked)));
  const modeTabs = [...document.querySelectorAll('.app-tabs [data-mode]')];
  const panelTabs = [...preview.querySelectorAll('[data-panel]')];
  function setMode(mode) {
    preview.dataset.mode = mode;
    art.setMode(mode);
    modeTabs.forEach(b => b.setAttribute('aria-selected', String(b.dataset.mode === mode)));
    const panel = mode === 'shared' ? 'shared' : 'connections';
    panelTabs.forEach(b => b.setAttribute('aria-selected', String(b.dataset.panel === panel)));
    preview.querySelectorAll('[data-panel-body]').forEach(p => { p.hidden = p.dataset.panelBody !== panel; });
  }
  modeTabs.forEach(b => b.addEventListener('click', () => setMode(b.dataset.mode)));
  panelTabs.forEach(b => b.addEventListener('click', () => setMode(b.dataset.panel === 'shared' ? 'shared' : 'connectivity')));
}

function initShared(art) {
  const buttons = [...document.querySelectorAll('[data-shared-mode]')], caption = $('shared-caption');
  buttons.forEach(b => b.addEventListener('click', () => {
    const mode = b.dataset.sharedMode;
    buttons.forEach(x => x.setAttribute('aria-pressed', String(x === b)));
    art.setMode(mode);
    caption.dataset.t = CAPTIONS[mode];
    caption.textContent = t(CAPTIONS[mode]);
  }));
}

function initFindings() {
  const steps = [...document.querySelectorAll('#finding-steps a')], caption = $('finding-caption');
  let timer = 0;
  function show(n) {
    const key = n ? `caption${n}` : 'caption0';
    steps.forEach(a => a.classList.toggle('is-active', a.dataset.step === String(n)));
    if (caption.dataset.t === key) return;
    clearTimeout(timer);
    caption.classList.add('is-changing');
    timer = setTimeout(() => { caption.dataset.t = key; caption.textContent = t(key); caption.classList.remove('is-changing'); }, 160);
  }
  steps.forEach(a => {
    a.addEventListener('mouseenter', () => show(a.dataset.step));
    a.addEventListener('focus', () => show(a.dataset.step));
  });
  $('finding-steps').addEventListener('mouseleave', () => show(0));
  $('finding-steps').addEventListener('focusout', e => { if (!e.currentTarget.contains(e.relatedTarget)) show(0); });
}

function initSources() {
  const dialog = $('sources-dialog');
  document.querySelectorAll('#open-sources, [data-open-sources]').forEach(b => b.addEventListener('click', () => dialog.showModal()));
  $('close-sources').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', e => { if (e.target === dialog) dialog.close(); });
}

function renderCharts() {
  const legend = (key, cls) => `<span><i class="${cls}"></i><span data-t="${key}">${EN[key]}</span></span>`;
  document.querySelectorAll('[data-chart]').forEach(box => {
    const c = CHARTS[box.dataset.chart];
    const bar = (v, hi, tick) => `<span class="chart__track"><span class="chart__bar${hi ? ' is-hi' : ''}" style="--v:${(v / c.max).toFixed(4)}"></span>${tick != null ? `<span class="chart__tick" style="--v:${(tick / c.max).toFixed(4)}"></span>` : ''}</span><span class="chart__val${hi ? ' is-hi' : ''}">${c.fmt(v)}</span>`;
    box.innerHTML = `<div class="chart" role="img" aria-label="${c.rows.map(r => `${r[0]}: ${c.fmt(r[1])} / ${c.fmt(r[2])}`).join('; ')}">`
      + `<p class="chart__legend">${legend(c.keys[0], 'is-hi')}${legend(c.keys[1], '')}${c.tick ? legend(c.tick, 'is-tick') : ''}</p>`
      + c.rows.map(([name, hi, lo, tick]) => `<div class="chart__group"><span class="chart__ds">${name}</span>${bar(hi, true, tick)}${bar(lo, false, tick)}</div>`).join('')
      + `<p class="chart__axis"><span>${c.axis[0]}</span><span>${c.axis[1]}</span></p></div>`;
  });
  const cards = document.querySelector('.rcards');
  if (!cards) return;
  if (!('IntersectionObserver' in window)) { cards.classList.add('is-in'); return; }
  const io = new IntersectionObserver(entries => {
    if (entries.some(e => e.isIntersecting)) { cards.classList.add('is-in'); io.disconnect(); }
  }, { threshold: 0.25 });
  io.observe(cards);
}

function initCite() {
  const button = $('copy-bibtex'), label = button.querySelector('[data-t]'), bib = $('bibtex');
  let timer = 0;
  button.addEventListener('click', async () => {
    let ok = false;
    try { await navigator.clipboard.writeText(bib.textContent); ok = true; } catch {
      // Older or insecure contexts: select the entry so it can be copied by hand.
      const range = document.createRange(); range.selectNodeContents(bib);
      const sel = getSelection(); sel.removeAllRanges(); sel.addRange(range);
      try { ok = document.execCommand('copy'); } catch { ok = false; }
    }
    if (!ok) return;
    clearTimeout(timer);
    button.classList.add('is-done'); label.textContent = t('copied');
    timer = setTimeout(() => { button.classList.remove('is-done'); label.textContent = t('copyBib'); }, 1800);
  });
}

renderCharts();
applyLocale();
document.querySelectorAll('[data-lang]').forEach(b => b.addEventListener('click', () => setLocale(b.dataset.lang)));
initHeader();
initSources();
initFindings();
initCite();
initArt().then(arts => {
  initPreview(arts.preview);
  initShared(arts.shared);
}).catch(error => {
  // The page still reads without the drawings; say so instead of failing silently.
  console.warn(error);
  document.documentElement.classList.add('no-arbor');
});
