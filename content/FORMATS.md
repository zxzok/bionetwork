# 题库、练习与真实数据案例的源文件格式

本文件规定 content/quizzes、content/exercises、content/cases 三类源文件的写法。build.py 据此生成网页、学生版和答案版笔记本，以及可在浏览器中运行的 JupyterLite 笔记本。`tools/check_content.py` 用来校验这些文件，所有源文件都必须通过它。

## 1. 题库：content/quizzes/<ID>.json

<ID> 可以是 L01…L16（16 个讲次页，对应各专题），也可以是 V1…V6（6 讲课程视频，题目只考视频里讲过的内容）。

```json
{
  "pre":  [ 题目, … ],          // 课前 3–5 题，只有 L 讲次需要
  "post": [ 题目, … ]           // 课后约 20–25 题
}
```

每道题都有以下字段：
- `q`：题干。可以用 $…$ 写行内公式。
- `type`：题型，取值为 `"single"`（默认）、`"multi"`、`"tf"`、`"numeric"` 或 `"code"`。
- `level`：难度，1 为基础概念，2 为理解与应用，3 为计算或综合分析。
- `explain`：解析。说明为什么对、常见错误错在哪，提到选项时用字母。
- `see`：可选，知识页文件名（如 `"community-structure.modularity.html"`），页面上会显示为“复习”链接。

各题型的写法：
- `single`：给出 `options`（4 个）；`answer` 是正确项的下标，从 0 开始。
- `multi`：给出 `options`（4–5 个）；`answer` 是下标列表，例如 `[0, 2]`。至少一个正确，不能全部正确。
- `tf`：判断题，`answer` 为 `true` 或 `false`，不需要 `options`。
- `numeric`：计算题。`answer` 填数值，`tol` 填允许的绝对误差，`unit` 可选。题干必须给全计算所需的数据。
- `code`：读代码选输出。`code` 字段放一段完整、可直接运行的 Python 代码，用 networkx、numpy 等写成；再给 `options` 和 `answer`（与 single 相同）。正确选项必须和这段代码的实际运行输出完全一致，check_content.py 会实际运行它。

出题规范：
- 每题只考一个知识点。
- 干扰项要来自真实的常见误解，不要用明显荒谬的选项。
- 同一套题里，正确答案在 A–D 之间大致均匀分布，不要集中在某一项。
- 所有数字都必须能从站内内容或可复算的计算中得到，不得编造。

## 2. 练习：content/exercises/<L01…L16>.py

练习文件用 `# %%` 分隔成格。每个任务由以下几格组成：

```python
# %% [markdown] task 1: 任务标题
# 任务说明（Markdown，每行以 "# " 开头）。写清要做什么、用到哪个知识点、期望看到什么。
# 提示：……（可选，会折叠显示）

# %% setup
# 可选。这一格的代码学生版和答案版共用，例如导入库、载入数据、写好的辅助函数。

# %% starter
# 学生版起始代码：保留结构，关键处写 TODO，并给变量赋占位值（如 None）。

# %% solution
# 参考答案：完整可运行。网页上默认折叠。

# %% check
# 自动核对：用 assert 检查学生算出的变量，并给出中文提示，例如
# assert abs(Q - 0.371) < 0.01, "模块度应约为 0.37，检查是否用了总边数 m"
print("✓ 任务 1 通过")
```

规则：
- 运行顺序为“setup → solution → check”，整个文件从头到尾必须能跑通。check_content.py 用答案版运行，并确认每个 check 格都打印了 ✓。
- check 只能检查 starter 里约定好的变量名，不能依赖 solution 内部的中间变量。
- 涉及随机性时必须固定种子。check 的容差要足够宽，保证正确的不同写法也能通过。
- 每讲 4–6 个任务，难度递进。最后一个任务是开放的小分析：check 只检查形状或范围，不检查具体数值。
- 只能使用 numpy、scipy、networkx、pandas、matplotlib，这些库都能在浏览器（Pyodide）中运行。不要联网下载；需要数据时使用 content/data/ 下的文件，代码里一律写相对路径 `data/<文件名>`（校验在 content/ 目录下运行，JupyterLite 里也是同样的目录结构）。
- 画图用 matplotlib，不要调用 plt.show()。

## 3. 真实数据案例：content/cases/<topic-id>.py，数据放在 content/data/

案例文件的格式与练习相同：用 `# %% [markdown]` 写说明，用 `# %%` 写代码，不需要 starter、solution 和 check 格。每个案例是一次完整分析：

1. 数据来源；
2. 读入与清洗；
3. 构网；
4. 计算该专题的核心指标；
5. 与零模型比较；
6. 作图；
7. 解读结果和局限。

数据要求：
- 必须是公开、可再分发的，例如 CC0、CC BY、公有领域，或明确允许教学再分发的。
- 压缩后不超过 5 MB。
- 放在 content/data/<名字>.csv（或 .txt、.gml），并在 content/data/SOURCES.md 里写明来源 URL、许可证、引用和下载日期。
- 案例开头的 markdown 也要写出处。
- 不可再分发的数据（如 HCP、UK Biobank）不要使用。
