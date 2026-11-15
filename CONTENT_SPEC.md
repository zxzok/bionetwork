# 课程网站内容规范（所有内容作者必须遵守）

课程：《生物医学复杂网络分析》，面向生物医学工程硕士/博士研究生的自学网站。依据：
- 教学大纲：`../2025/论文/2025生物医学复杂网络分析课程教学大纲.docx`（可用 `pandoc -t plain` 读取）
- 总体规划（含 80 段视频清单）：`../在线课程网站规划/总体规划_v0.1.md`
- 已核验的外部资源清单（若存在）：`../在线课程网站规划/资源清单_理论篇_L1-8.md`、`../在线课程网站规划/资源清单_应用篇_L9-14与数据集.md`
- 现有课件文字可从 `../2025/*.pptx` 提取（zip 内 ppt/slides/slideN.xml 的 `<a:t>` 文本）

每讲交付 4 个文件，`NN` 为两位讲次号（01–16）：

| 文件 | 内容 |
|---|---|
| `content/lectures/LNN.md` | 讲义页面（Pandoc Markdown + YAML 头） |
| `content/quizzes/LNN.json` | 进门自测 3 题 + 出门测验 10 题 |
| `content/exercises/LNN.py` | 浏览器内可运行的 Python 练习（Pyodide） |
| `content/scripts/LNN.json` | 本讲“核心讲解”视频的分镜与旁白（教师本人声音合成） |

写作要求：简体中文，学术准确，面向有生物医学背景、数学和编程基础不一的研究生；术语首次出现给英文；不编造数据、引用、DOI 或链接（不确定就不写）；不写“众所周知”之类空话。

---

## 1. 讲义 `LNN.md`

```markdown
---
id: L03
title: 小世界网络与无标度网络
unit: 单元二 · 网络模型
hours: 3.5            # 预计学习小时数（含视频、练习）
prereq: [L02]
objectives:           # 直接取自大纲该讲 4 条教学目标，可轻度精炼
  - ...
keywords: [小世界, 无标度, 优先连接, 幂律]
demos: [ws, ba]       # 本讲页面嵌入的交互演示 id（见第 5 节清单），可为空 []
---

## 导学
（150–300 字：这一讲解决什么问题，与上一讲/下一讲的关系，建议学习顺序和时间分配）

## 1 xxx
（核心概念分 3–6 个小节，总计约 3000–5000 字。公式用 $...$ / $$...$$（KaTeX）。
每个小节至少有一个直观例子；关键定义用 ::: {.callout-def} ::: 包起来；
需要提醒的易错点用 ::: {.callout-warn} :::；生物医学例子用 ::: {.callout-bio} :::）

## 生物医学视角
（300–600 字，把本讲概念落到真实生物医学研究上，引用经典文献时写作者+年份+期刊，DOI 只写你确定的）

## 常见误区
（3–5 条，编号列表，每条“误区 → 正解”）

## 文献导读
（2–3 篇核心文献：每篇写 背景 / 核心发现 / 读的时候注意什么 / 1 个思考题。用三级标题 ### 作者 年份：题目）

## 拓展资源
（表格：| 类型 | 资源 | 说明 |，5–8 条；链接只用资源清单中已核验过的或 doi.org 链接；YouTube 资源注明“需境外网络”）

## 讨论题
（2 道开放题，鼓励联系自己的研究方向）
```

Callout 语法（Pandoc fenced div）：
```markdown
::: {.callout-def}
**聚集系数**：……
:::
```

## 2. 测验 `LNN.json`

```json
{
  "pre": [ {"q": "题干", "options": ["A","B","C","D"], "answer": 1, "explain": "解析"} ],
  "post": [ ... 10 题 ... ]
}
```
- `answer` 为 0 起始下标。单选题，4 个选项。
- 出门 10 题覆盖：概念辨析 ≥4、计算/估算 ≥2、结果解读或错误分析 ≥2、生物医学情境 ≥2。
- 解析要说明为什么对、其他选项错在哪里（1–3 句）。题干可用 $...$ 公式。

## 3. 练习 `LNN.py`

在浏览器 Pyodide 中运行，仅可使用：`networkx`、`numpy`、`scipy`、`matplotlib`（图会被自动显示）、标准库。不能读本地文件、不能联网；数据在代码里生成或用 networkx 自带图（如 `nx.karate_club_graph()`、`nx.les_miserables_graph()`、`nx.florentine_families_graph()`）。

格式：一个文件含 2–4 个任务，用注释分隔：
```python
# %% 任务1：标题
# 说明（中文，2–5 行注释：要做什么、期望看到什么）
import networkx as nx
G = nx.watts_strogatz_graph(200, 6, 0.1, seed=1)
# TODO: 计算平均聚集系数，赋值给 C
C = None
print("C =", C)

# %% 任务2：……
```
- 每个任务可以独立运行（任务内自己 import 和建图）。
- 用 `# TODO` 标出学生要改的地方，但保证**原样运行也不报错**（用 None 判断给出提示，例如 `if C is None: print("提示：……")`）。
- 再在文件末尾给参考答案：`# %% 参考答案（先自己做！）`，其后是完整可运行的答案代码。
- 计算量要小（单任务 < 3 秒）。
- 第 9–14 讲涉及 fMRI、表达谱等，用 numpy 生成**模拟数据**并在注释中说明“模拟数据，仅用于演示方法”。

## 4. 视频脚本 `LNN.json`

每讲一段“核心讲解”视频，时长 4–6 分钟，**旁白总字数 1000–1500 字**，由教师本人声音（语音合成）朗读。

```json
{
  "id": "L03-core",
  "title": "小世界与无标度：两种改变我们认识网络的模型",
  "scenes": [
    {"visual": "title", "params": {"title": "小世界与无标度", "subtitle": "第3讲 核心讲解"},
     "lines": ["大家好，这一讲……", "……"]},
    {"visual": "bullets", "params": {"heading": "本讲要回答的三个问题", "items": ["……","……","……"]},
     "lines": ["第一个问题……", "第二个……", "第三个……"]},
    {"visual": "ws_rewire", "params": {}, "lines": ["……"]}
  ]
}
```
旁白写作规则（关系到合成效果）：
- `lines` 每个元素是一句话，15–45 个汉字，以句号/问号/感叹号结尾。一句一句合成，句子就是字幕单元。
- 口语化、第一人称（“我们”“大家”），像老师面对面讲解；不要念公式符号，改说法：“平均度 k 拔”不好，写“平均度”；“C 除以 C 随机”写“实际聚集系数与随机网络聚集系数之比”。
- 英文人名、模型名可保留（Watts、Strogatz、Barabási 写作“巴拉巴西”），缩写尽量配中文：“SIR 模型”可以。
- 数字用阿拉伯数字即可。不要括号、不要引号嵌套、不要 emoji。
- `bullets` 场景：`items` 数量建议与 `lines` 数量相同（第 i 条在第 i 句开始时出现）；items 每条 ≤ 18 字。
- 结构建议：开场 title（2–3 句）→ 问题引入 → 2–4 个核心动画场景 → 生物医学例子 → 小结 bullets → 结尾提示去做练习和测验。
- 6–10 个场景，每个场景 2–8 句。

可用的 `visual`（只能用这些，参数都可省略）：

| visual | 画面 | params |
|---|---|---|
| `title` | 标题卡 | `title`, `subtitle` |
| `bullets` | 标题 + 要点逐条出现 | `heading`, `items` |
| `formula` | 标题 + 1–3 行公式逐行出现（matplotlib mathtext，支持 `\frac`, `\sum`, `\langle k \rangle`, 上下标, 希腊字母；不支持 `\text`、`\begin`） | `heading`, `latex`（列表，不含 $）, `notes`（与公式一一对应的中文说明，可选） |
| `graph_adjacency` | 小图与邻接矩阵对照，逐条边高亮 | — |
| `path_bfs` | 从源点做广度优先搜索，逐层着色，显示距离 | — |
| `clustering` | 选中一个节点，高亮其邻居间的三角形，显示局部聚集系数 | — |
| `degree_dist` | ER 与 BA 网络的度分布，线性坐标→双对数坐标 | — |
| `er_growth` | ER 随机图 p 逐渐增大，巨连通分支涌现 | — |
| `ws_rewire` | 环形规则网络按 β 重连，右侧 C(β)/C(0) 与 L(β)/L(0) 曲线 | — |
| `ba_growth` | BA 网络逐步生长，节点大小∝度，右侧度分布 | — |
| `community` | 空手道俱乐部网络，Girvan–Newman 逐步删边，社团着色，显示模块度 Q | — |
| `sir` | 网络上 SIR 传播，节点着色 + 右侧 S/I/R 曲线 | `beta`, `gamma` 可选 |
| `immunization` | 随机免疫 vs 目标免疫（枢纽）对比，传播规模 | — |
| `kuramoto` | 圆上的振子相位，耦合强度增大时同步，右侧序参量 r(t) | — |
| `control` | 有向网络最大匹配，未被匹配的节点标为驱动节点 | — |
| `robustness` | 随机删点 vs 攻击枢纽，巨分支比例曲线 | — |
| `brain_threshold` | 模拟脑区相关矩阵，阈值逐步提高，网络变稀疏，显示密度与平均聚集系数 | — |
| `dfc` | 模拟 BOLD 时间序列，滑动窗口内相关矩阵随时间变化 | — |
| `symptom_net` | 9 个抑郁症状节点（中文标签），偏相关边，边宽∝强度，中心性条形图 | — |
| `motif_ffl` | 前馈环 X→Y→Z、X→Z 示意，右侧信号脉冲时 Z 的延迟响应 | — |
| `ppi_hubs` | 无标度“蛋白网络”，枢纽节点标红，删除枢纽后网络碎裂 | — |
| `disease_network` | 疾病–基因二分网络投影为疾病网络（Goh 2007 思路的玩具示例） | — |
| `wgcna` | 模拟表达谱→相关矩阵→软阈值→层次聚类→模块着色 | — |
| `proximity` | 网络上的疾病模块与药物靶点，最短路径距离与邻近度 | — |
| `knowledge_map` | 16 讲课程知识地图，按单元着色，可高亮当前讲 | `highlight`（如 "L03"） |

## 5. 交互演示 id（用于讲义 YAML 的 `demos`）

| id | 演示 | 建议讲次 |
|---|---|---|
| `graph_matrix` | 点击添加/删除边，图与邻接矩阵、度序列联动 | L02 |
| `er` | ER 随机图：拖动 p，看巨连通分支与平均度 | L02, L03 |
| `ws` | WS 重连：拖动 β，看网络与 C/L 曲线 | L03 |
| `ba` | BA 生长：逐步加点，度分布双对数图 | L03 |
| `modularity` | 空手道俱乐部：点击节点改分组，实时模块度 Q | L04 |
| `sir` | 网络上 SIR：选网络类型、传染率、恢复率、免疫策略 | L05 |
| `kuramoto` | Kuramoto：拖动耦合强度 K，看相位与序参量 r | L06 |
| `attack` | 随机失效 vs 蓄意攻击：巨分支曲线 | L07 |
| `matching` | 有向网络最大匹配与驱动节点 | L07 |
| `brain_threshold` | 模拟脑网络：拖动阈值，看密度、聚集系数、枢纽排序 | L09 |
| `dfc` | 滑动窗口动态功能连接：拖动窗口位置与长度 | L10 |
| `symptom` | 症状网络：相关 vs 偏相关切换，强度中心性 | L11 |
| `ffl` | 前馈环：调输入脉冲长度，看 Z 的响应（滤波作用） | L12 |
| `proximity` | 药物靶点与疾病模块的网络邻近度 | L14 |

第 1、8、13、15、16 讲可以不放演示，或复用上面的（如 L08 用 `graph_matrix`、`modularity`）。

---

## 6. 论文精读 `content/papers/<pid>.md`

`<pid>` 用 `作者姓年份_关键词`，全小写 ASCII，如 `zhang2016_inputgraph`、`watts1998_smallworld`。

```markdown
---
id: zhang2016_inputgraph
title: "Input graph: the hidden geometry in controlling complex networks"   # 论文原题
title_zh: 输入图：控制复杂网络的隐藏几何结构                                 # 中文译名
authors: "Zhang X, Lv T, Pu Y"          # 作者 ≤6 位，多则加 et al.
venue: Scientific Reports
year: 2016
doi: 10.1038/srep38209                  # 必须经 Crossref 核验；没有就留空 ""
url: ""                                  # 无 DOI 时（如 arXiv）给官方链接
own: true                               # 是否为本课程教师团队的论文
track: 网络控制理论                       # 分组，见下方清单
lectures: [L07]                          # 与哪些讲次相关（1–3 个）
level: 进阶                               # 入门 / 进阶 / 研究
keywords: [输入图, 最大匹配, 驱动节点]
summary: 一句话（≤60 字）：这篇论文解决了什么问题、得到了什么。
---

## 一句话看懂
## 研究背景与问题
## 核心思想与方法          # 关键定义、公式（$...$）、算法步骤；用 callout-def 框出核心定义
## 主要发现               # 3–6 条，每条有具体数字或结论，只写论文中真实出现的内容
## 怎样读这篇论文          # 建议阅读顺序、关键图表各说明什么、可以跳过什么
## 局限与后续工作          # 客观指出假设与局限；本团队论文写后续工作与相互关系
## 与课程的联系            # 联系到哪一讲的哪个概念（链接写成 [第7讲](L07.html)）
## 思考题                 # 2–4 道开放题
```

篇幅 1500–3000 字。只依据论文原文（教师论文已提取全文）或已核验的摘要写作；数字、数据集、样本量必须出自原文，不确定就不写。不要大段翻译原文，用自己的话讲解。

track 取值：`经典奠基`、`网络控制理论`、`生物网络的控制`、`传播与溯源`、`脑网络与精神疾病`。

### 论文讲解视频 `content/scripts/<pid>.json`

格式同第 4 节，`title` 写中文译名，第一个场景 `{"visual":"title","params":{"title":"...","subtitle":"论文精读 · 期刊 年份"}}`。约 30–45 句，旁白第一人称可用“我们团队”。只用第 4 节已有的 visual。

---

## 7. 知识专题 `content/topics/<id>.md`（2026-11 改版后的主体内容）

网站定位已改为“生物医学网络科学在线手册”：按科学知识结构组织，不再是课程。领域与专题清单见 `content/taxonomy.yaml`。旧讲义 `content/lectures/LNN.md` 保留不动，作为迁移来源。

### 禁止出现
讲次编号（第 N 讲、本讲、这一讲、上一讲、下一讲、前几讲）、学分学时、建议用时、学习路线、课程/课程项目/考核/评分/作业/测验/练习任务/讨论区/同学/中期与终期汇报、学校与学院名称、“AI 语音合成”“字幕已嵌入”之类说明。“本课程团队”改为“本站作者团队”。

### 文件格式
```markdown
---
id: controllability                 # 与 taxonomy.yaml 一致
title: 网络可控性与稳定性
en: Network controllability and stability
domain: dynamics
legacy: L07
summary: 一句话（≤70 字）说明这个专题研究什么问题
keywords: [可控性, 结构可控性, 最大匹配, 驱动节点]
synonyms: [controllability, driver node, 驱动节点集, MDS]   # 中英文同义词与缩写，供站内搜索
demos: [matching, attack]           # 交互演示 id（沿用旧讲义 YAML）
reviewed: 2026-11-14                # 最后核查日期
---

## 概述 {#overview}
（学术背景：这一专题对应什么研究对象与科学问题；与其他专题的关系；200–500 字）

## 线性系统的可控性 {#linear-controllability}
（知识页面：定义与理论、数学与算法、示例。可含 ### 小节、公式、callout）

## ……（若干知识页面，每个 ## 一页，顺序即阅读顺序）

## 数学推导与算法 {#derivations}
## 研究前沿与开放问题 {#frontiers}
## 生物医学应用 {#biomedical}
## 适用范围与常见误用 {#limitations}

## 关联知识 {#related}       # 以下四节显示在专题主页，不单独成页
## 核心文献 {#references}
## 延伸资源 {#resources}
## 开放问题 {#questions}
```
- 每个 `##` 必须带 `{#英文-短横线-id}`；除“概述、关联知识、核心文献、延伸资源、开放问题”外，每个 `##` 生成一个独立知识页面。
- 链接其他专题写成 `[网络结构指标与随机图](network-metrics.html)`，链接某个知识页面写成 `[最大匹配](controllability.structural-controllability.html)`（专题 id + “.” + 节 id）。链接论文精读写 `[Liu 2011](paper-liu2011_controllability.html)`。
- “关联知识”列出 3–8 条：相关理论专题、在其他生物医学领域中的应用，每条一句说明。
- 公式、callout（`::: {.callout-def}` / `.callout-warn` / `.callout-bio`）、表格写法同第 1 节。

## 8. 代码示例 `content/code/<topic-id>.py`

不是练习：每个单元都是完整可运行、带输出说明的示例。
```python
# 依赖：networkx>=3, numpy, scipy, matplotlib
# 数据：……（输入格式说明；示例数据用代码生成或来自 networkx 内置数据集）

# %% 示例：用 Kalman 秩判据检验可控性
# 说明这段代码做什么、关键参数、输出如何解读（2–5 行注释）
import numpy as np
...
```
每个 `# %% 示例：` 单元必须能独立运行（不依赖其他单元的变量），不得有 TODO。
