# 生物医学网络科学 · Biomedical Network Science

一部带交互功能的生物医学网络科学在线手册，网址 https://bionetwork.xizhe.net 。纯静态网站，构建产物在 `dist/`，可直接复制到任何静态托管或 Nginx 目录，不需要数据库或后端。

## 信息架构

七个知识领域（`content/taxonomy.yaml`），每个领域下若干专题，每个专题 = 一个专题主页 + 若干知识页面：

| 领域 | 专题 |
|---|---|
| 网络基础理论 | 复杂系统与网络的数学表示 · 网络结构指标与随机图 · 小世界与无标度网络模型 · 社团结构与社区发现 · 度相关性与网络结构的高阶统计 · 网络构建与统计验证 |
| 网络动力学与控制 | 网络上的传播与免疫 · 同步与协同动力学 · 网络鲁棒性、渗流与级联失效 · 网络可控性与稳定性 |
| 脑网络与连接组 | 脑连接组：结构与功能连接 · 动态功能连接与多层脑网络 |
| 症状网络与网络精神病学 | 症状网络与网络精神病学 |
| 分子网络与基因调控 | 生物分子网络与拓扑特征 · 基因调控网络推断与共表达分析 |
| 网络医学与药物网络 | 疾病模块、网络邻近度与药物重定位 |
| 计算方法与研究规范 | 网络分析流程与 NetworkX 实践 · 研究问题、可复现分析与敏感性分析 · 结果呈现与研究前沿 |


其他栏目：可视化实验室（14 个交互演示，可导出 PNG 与参数 JSON）、计算方法与代码库、文献知识库（43 篇论文精读）、数据与软件资源库（55 个资源，每个有中文介绍页）、知识索引（全站正式定义）、站内搜索（中英文与缩写同义词扩展）、关于本站。

旧网址 `L01.html`…`L16.html` 自动跳转到对应专题；`guide.html` 跳到“关于本站”，`me.html`、`project.html` 跳到首页。

## 目录

| 路径 | 内容 |
|---|---|
| `content/taxonomy.yaml` | 领域、专题、旧讲次对应、视频与专题对应 |
| `content/topics/<id>.md` | 专题内容（格式见 `CONTENT_SPEC.md` 第 7 节；每个 `## 标题 {#id}` 生成一个知识页面） |
| `content/code/<id>.py` | 可运行的代码示例（第 8 节；构建时生成 Notebook） |
| `content/papers/*.md` | 论文精读（第 6 节） |
| `content/resources.yaml` | 数据与软件资源库 |
| `content/scripts/*.json` | 讲解视频分镜与旁白 |
| `site/apps/flyscope/`、`site/apps/sparse-control/` | 两个专题交互网站的站内副本（FlyScope 首页与 Sparse Internal Control 网站），构建时复制到 `dist/apps/`；FlyScope 的数据浏览器依赖其后端，站内版本中“进入探索”链接指向页面内的探索与数据小节 |
| `site/assets/`、`site/hero.js` | 样式、前端脚本（`site.js` 阅读器与 Python 运行、`demos.js` 交互演示、`search.js` 站内搜索） |
| `video/` | `visuals.py` 动画库，`make_video.py` 合成与渲染 |
| `build.py` | 生成网站 |
| `tools/run_examples.py` | 运行代码示例，生成代码库的输出图（`build/gallery/`） |
| `.github/workflows/pages.yml` | 推送后把 `dist/` 发布到 GitHub Pages（bionetwork.xizhe.net） |

## 常用操作

```bash
.venv/bin/python build.py
```

```bash
python3 -m http.server 8790 --directory dist
```

然后打开 http://localhost:8790 。

- **新增知识页面**：在对应 `content/topics/<id>.md` 中加一节 `## 标题 {#英文-id}`，重新构建即可；搜索、目录、上下页自动更新。
- **新增专题**：在 `taxonomy.yaml` 的 `topics` 中加一行，再写 `content/topics/<id>.md`。
- **新增资源**：在 `resources.yaml` 中加一条（字段见文件内已有条目）。
- **修改旁白后重新生成视频**（只重新合成改动过的句子）：在 `video/v2/` 中编辑对应的 `ep_<专题或论文>.py`，运行 `../../.venv/bin/python produce.py ep_<名称>`，再运行 `build.py`。

## 视频

- 共 36 集：19 个专题各一集（`T-<专题>`），17 篇论文各一集（论文编号）。脚本在 `video/v2/`：manim 动画、文字页、本站交互演示的录屏，以及 YouTube 片段（`video/v2/media/`，片段起点在 `media/offsets.json`）。
- 旁白使用本机 IndexTTS-2.5 语音合成，音色为作者本人声音（声音库中的“我的声音_讲解”），讲课语气强度 0.6，正常语速，重点句约 1.1 倍时长。按作者要求，画面与网页上都不标注合成说明，也不出现学校名称。
- 规格：1920×1080，30 fps，H.264 + AAC，响度统一到 −16 LUFS；另有 `.vtt` 字幕与 `.txt` 文字稿。
- 合成可分到另一台 Mac（ssh 主机 `m5`）：`video/v2/remote_synth.py`。旧版视频（L 系列）已移到 `video/old_v1_videos/`，不再发布。

## 部署注意

- 浏览器内 Python 从 cdn.jsdelivr.net 加载 Pyodide；若网络无法访问，可把 Pyodide 发行包放到 `dist/pyodide/` 并修改 `site/assets/js/site.js` 中的 `PYODIDE` 地址。
- 站内搜索读取 `assets/search-index.json`，需要通过网页服务器访问（直接双击 HTML 文件时搜索不可用）。
- 公式在构建时转换成 MathML，不依赖外部脚本。

## 页面设计

- **整站导航**（参照 The Turing Way）：左侧可折叠的知识树（领域 → 专题 → 知识页面，当前页高亮），右侧本页目录，顶部站内搜索；窄屏下知识树收进“☰ 目录”抽屉。
- **知识页面**（参照 Distill）：领域色顶线、阅读时间与核查日期、44rem 阅读栏、图形可用满栏宽；定义、注意、生物医学实例三种侧栏样式；页末自动汇总本页引用的 DOI。
- **交互可视化**（参照 Seeing Theory）：宽度足够时左侧说明与参数、右侧图形；每个演示嵌入对应的知识页面（对应关系见 `build.py` 的 `DEMO_SECTION`），并可导出 PNG 与参数。
- **代码库**（参照 Nilearn / NetworkX Gallery）：207 个示例按领域与专题组织为缩略图图库，每个示例有独立页面（说明、输出图、文字输出、高亮代码、浏览器内运行、Notebook 下载）。
- **首页**：知识地图（专题按领域排成环，连线为专题间的相互引用）、知识领域、从数据到结论的知识链、可视化、代码图库、文献与参考资源。

修改代码示例后，先重新运行示例生成输出图（只重跑改动过的单元），再构建网站：

```bash
.venv/bin/python tools/run_examples.py
.venv/bin/python build.py
```
