# 大模型 Skill 入门：原理、开发与应用

## 目录

- [什么是 Skill](#什么是-skill)
- [Skill 的运行原理](#skill-的运行原理)
- [Skill 的定义结构](#skill-的定义结构)
- [权限模型](#权限模型)
- [案例解析：从零构建一套数据处理 Skill 体系](#案例解析从零构建一套数据处理-skill-体系)
- [开发你的第一个 Skill](#开发你的第一个-skill)
- [进阶：Skill 体系设计](#进阶skill-体系设计)
- [常见问题与最佳实践](#常见问题与最佳实践)

---

## 什么是 Skill

### 定义

Skill 是 Claude Code 提供的一种能力封装机制。它将一段**结构化的指令模板**与**工具权限声明**打包在一起，使大模型能够以可复用、可管控的方式执行特定任务。

用更直白的话说：Skill 就是你写给大模型的"标准操作手册"——告诉它在面对某类任务时应该怎么做、可以用什么工具、输入输出是什么格式。

### Skill 不是什么

| 常见误解 | 实际情况 |
|---------|---------|
| Skill 是一段可执行代码 | Skill 本身是一份 Markdown 文档，描述的是"如何做"，而非"做什么" |
| Skill 需要专门的运行时 | Skill 依托 Claude Code 环境运行，不需要额外的框架或服务 |
| Skill 等同于 API 接口 | Skill 是面向大模型的指令，不是面向程序的接口 |

### Skill vs 直接对话

不使用 Skill 时，你需要每次都向大模型详细描述：

> "请用 Python 脚本处理 data 目录下的 Excel 文件，读取 C 列的数据，按照缓存中的映射关系填充距离信息，输出格式是 `名称-数值km`，如果找不到就标记为 `名称-?km`……"

使用 Skill 后，你只需要说：

> "填充这个文件的距离数据"

大模型会自动匹配到对应的 Skill，按照预定义的流程执行。

### 核心价值

```
[人类意图] --匹配--> [Skill 指令模板] --驱动--> [工具调用] --产出--> [结果]
```

1. **消除重复沟通** —— 将反复出现的操作流程固化为标准模板
2. **降低出错概率** —— 参数、路径、格式都已在模板中约定
3. **权限可控** —— 每个 Skill 声明了自己能使用的工具范围
4. **可组合** —— 多个 Skill 可以串联成完整的工作流

---

## Skill 的运行原理

### 触发机制

Skill 的触发有两种方式：

**1. 斜杠命令（显式触发）**

用户在对话中输入 `/skill-name`，Claude Code 直接加载对应的 Skill 定义并执行。

```
用户: /fill-distances data/summary/billing.xlsx
      ↓
Claude Code: 加载 .claude/skills/fill-distances/SKILL.md
      ↓
大模型: 按照 SKILL.md 中的指令执行任务
```

**2. 自然语言匹配（隐式触发）**

用户用自然语言描述需求，Claude Code 根据各 Skill 的 `description` 字段自动匹配最相关的 Skill。

```
用户: "帮我把这个对账单的距离信息补全"
      ↓
Claude Code: 匹配到 fill-distances 的 description
      ↓
大模型: 加载并执行该 Skill
```

### 执行流程

```
                    .claude/skills/
                    ├── skill-a/
                    │   └── SKILL.md     ←── 指令模板
                    ├── skill-b/
                    │   └── SKILL.md
                    └── skill-c/
                        ├── SKILL.md
                        └── scripts/     ←── 配套脚本（可选）
                            └── process.py


    [用户输入]
        │
        ▼
    [Skill 匹配] ── 读取 SKILL.md 中的 description
        │
        ▼
    [权限检查] ── 核对 allowed-tools 与 settings.local.json
        │
        ▼
    [指令注入] ── SKILL.md 的内容作为上下文注入大模型
        │
        ▼
    [大模型推理] ── 根据指令模板决定具体的工具调用
        │
        ▼
    [工具执行] ── 调用 Bash / Read / Edit 等工具
        │
        ▼
    [结果返回] ── 向用户展示执行结果
```

关键点：**SKILL.md 本身不被"执行"，而是作为提示词注入大模型的上下文**。大模型根据这份指令文档，结合用户的具体输入，自主决定调用哪些工具、传入什么参数。

### 与普通 Prompt 的区别

| 维度 | 普通 Prompt | Skill |
|------|------------|-------|
| 持久性 | 一次性，用完即弃 | 持久化为文件，跨会话复用 |
| 权限控制 | 无独立权限声明 | 通过 `allowed-tools` 声明工具白名单 |
| 可发现性 | 不可发现 | 通过 `/` 命令或自然语言自动匹配 |
| 结构化程度 | 自由文本 | 有标准的 frontmatter + 正文结构 |
| 可分发性 | 不可分发 | 随项目仓库分发，团队共享 |

---

## Skill 的定义结构

一个 Skill 的最小单元是一个目录，包含一个 `SKILL.md` 文件：

```
.claude/skills/
└── my-skill/
    └── SKILL.md
```

### SKILL.md 的结构

SKILL.md 由两部分组成：**frontmatter（元数据）** 和 **正文（指令模板）**。

```markdown
---
name: my-skill
description: 一句话描述这个 Skill 做什么，用于自动匹配。
allowed-tools: Bash(python:*), Read
---

# Skill 标题

正文部分：详细的执行指令。
```

### Frontmatter 字段

```yaml
---
name: skill-name           # 标识符，用于 /skill-name 触发
description: ...           # 描述，用于自然语言匹配和用户提示
allowed-tools: Tool1, Tool2  # 该 Skill 被允许使用的工具列表
---
```

**name**

Skill 的唯一标识。命名规范：
- 使用 `kebab-case`（小写字母 + 短横线）
- 简洁、有动词性（如 `fill-distances`、`extract-stores`、`update-cache`）
- 避免过于宽泛的名称（如 `process-data`）

**description**

一段自然语言描述，核心作用有二：
1. 当用户输入自然语言时，Claude Code 依据此字段做语义匹配
2. 在 Skill 列表中作为说明展示给用户

好的 description 应当包含：
- 动作（做什么）
- 对象（处理什么）
- 关键特征词（帮助匹配）

```yaml
# 好的 description
description: Fill distance information into billing Excel files using cached data.
             Supports multiple regions. Automatically detects region from file path.

# 不好的 description
description: Process data files.
```

**allowed-tools**

声明该 Skill 可以使用的工具，格式为逗号分隔的工具列表，支持通配符：

```yaml
# 允许执行任意 python 命令和读取文件
allowed-tools: Bash(python:*), Read

# 允许执行特定虚拟环境中的 python 和激活虚拟环境
allowed-tools: Bash(python:*), Bash(source .venv/bin/activate*), Bash(.venv/bin/python:*), Read

# 仅允许读取文件（只读 Skill）
allowed-tools: Read, Glob, Grep
```

### 正文：指令模板的编写

正文是 SKILL.md 的核心，建议包含以下几个部分：

**1. 用法说明（Usage）**

明确触发条件和调用命令：

```markdown
## Usage

When the user asks to fill distances or complete billing data with distances:

\```bash
.venv/bin/python scripts/fill_data.py <excel_file> [options]
\```
```

`When the user asks to...` 这个句式很重要——它告诉大模型在什么场景下应该执行这个 Skill。

**2. 参数说明（Parameters）**

列出所有参数及其默认值：

```markdown
### Parameters

- `excel_file`: 待处理的 Excel 文件路径（必填）
- `region`: 区域标识符，可选值为 `region-a` 或 `region-b`（可选，默认从路径自动检测）
- `output`: 输出文件路径（可选，默认在原文件名基础上追加后缀）
```

**3. 工作原理（How It Works）**

描述内部逻辑，帮助大模型理解整个流程：

```markdown
## How It Works

1. **Load Cache**: Read cached mapping data from JSON file
2. **Detect Region**: Determine processing rules from file path
3. **Process Records**: For each record in the Excel file:
   - Skip rows already processed
   - Look up mapping from cache
   - Apply formatting rules
4. **Save**: Write results back to Excel
```

**4. 示例（Examples）**

提供具体的调用示例，这是最能指导大模型行为的部分：

```markdown
## Examples

### Basic usage - auto-detect settings

\```bash
.venv/bin/python scripts/fill_data.py data/summary/billing_0119.xlsx
\```

### Specify region manually

\```bash
.venv/bin/python scripts/fill_data.py /tmp/billing.xlsx region-a
\```
```

**5. 输出说明（Output）**

描述预期的输出格式和统计信息：

```markdown
## Output Example

\```
Processing complete:
  Total records: 245
  Matched: 243 (99.2%)
  Unmatched: 2 (0.8%)
\```
```

**6. 注意事项（Notes）**

补充约束条件和边界情况：

```markdown
## Important Notes

- In-place modification: The file is modified directly
- Idempotent: Can run multiple times safely
- Rows already processed will be skipped
```

---

## 权限模型

### 双层权限控制

Skill 的工具调用受到两层权限控制：

```
层级 1: SKILL.md 的 allowed-tools
    ↓ 取交集
层级 2: settings.local.json 的 permissions.allow
    ↓
最终可用工具集
```

**SKILL.md 的 `allowed-tools`**（Skill 层）

定义该 Skill 声明需要使用的工具。这是 Skill 作者的意图表达。

**settings.local.json 的 `permissions.allow`**（项目层）

定义整个项目中允许 Claude Code 使用的工具。这是项目管理者的安全策略。

### settings.local.json 示例

```json
{
  "permissions": {
    "allow": [
      "Bash(python:*)",
      "Bash(.venv/bin/python:*)",
      "Bash(source .venv/bin/activate*)",
      "Bash(git commit:*)",
      "Bash(git push:*)",
      "Skill(fill-distances)",
      "Skill(extract-stores)",
      "Skill(update-cache)"
    ]
  }
}
```

注意 `Skill(skill-name)` 条目——这表示允许用户通过斜杠命令触发该 Skill。没有在此声明的 Skill 在触发时会弹出确认提示。

### 权限设计原则

**最小权限**：每个 Skill 只声明自己真正需要的工具。

```yaml
# 好：只声明必要的工具
allowed-tools: Bash(.venv/bin/python:*), Read

# 不好：过于宽泛
allowed-tools: Bash(*), Read, Edit, Write, Glob, Grep
```

**工具通配符的层次**：

```yaml
Bash(python:*)              # 允许执行任意 python 命令
Bash(.venv/bin/python:*)    # 只允许虚拟环境中的 python
Bash(python scripts/a.py:*) # 只允许执行特定脚本
```

通配符粒度越细，安全性越高，但灵活性越低。根据实际需求选择合适的粒度。

---

## 案例解析：从零构建一套数据处理 Skill 体系

下面以一个真实的数据处理项目为原型（已隐去具体业务数据），展示如何设计和实现一套完整的 Skill 体系。

### 业务背景

某物流公司需要定期处理配送对账单，核心流程包括：

1. 从每日运单中**提取门店名称**
2. 将门店名称**填入月度对账单** Excel
3. 根据缓存的路线数据**填充配送距离**
4. 处理完成后**更新距离缓存**以供后续复用
5. 某些场景下需要**转换对账单格式**

每个环节都涉及固定的输入输出格式、特定的 Python 脚本、以及明确的业务规则。这正是 Skill 的理想应用场景。

### 设计思路

#### Step 1：识别可封装的任务单元

从日常工作流中提炼出**独立、可复用、有明确边界**的操作：

```
日常操作                         →  Skill 候选
─────────────────────────────────────────────────
"提取这周的门店数据"               →  extract-stores
"把门店名填到对账单里"             →  fill-stores
"把距离信息补全"                  →  fill-distances
"把新的距离存到缓存里"             →  update-cache
"把这个文件转成标准模板格式"        →  convert-format
```

#### Step 2：确定每个 Skill 的边界

好的 Skill 应当满足：
- **单一职责** —— 一个 Skill 只做一件事
- **输入输出明确** —— 什么格式进、什么格式出
- **幂等性** —— 重复执行不会产生错误结果

```
extract-stores
  输入: 一组每日运单 Excel 文件
  输出: 一个结构化的 txt 文件（按日期和车辆分组）
  幂等: 是（重新提取只是覆盖输出文件）

fill-stores
  输入: 空白对账单 Excel + 门店 txt 文件
  输出: 新的对账单 Excel（门店已填入）
  幂等: 是（生成的是新文件）

fill-distances
  输入: 已填门店的对账单 Excel
  输出: 原 Excel 文件中门店名追加距离后缀
  幂等: 是（已有距离后缀的行会被跳过）

update-cache
  输入: 已填距离的对账单 Excel
  输出: 更新后的距离缓存 JSON
  幂等: 是（已存在的距离对不会重复添加）
```

#### Step 3：设计 Skill 之间的流转关系

```
[extract-stores]
       │ 输出 txt
       ▼
[fill-stores]
       │ 输出带门店的 Excel
       ▼
[fill-distances]
       │ 输出带距离的 Excel
       ▼
  ┌────┴────┐
  │ 人工校验 │  ← 检查 -?km 标记，手动补全
  └────┬────┘
       ▼
[update-cache]
       │ 更新 JSON 缓存
       ▼
  下一轮复用
```

每个 Skill 独立运行，通过文件（Excel / txt / JSON）传递数据。这种松耦合设计使得：
- 任意环节可以单独重跑
- 中间结果可以人工检查和修正
- 新 Skill 可以方便地插入流程

#### Step 4：实现 Skill

以 `fill-distances` 为例，展示完整的实现过程。

**目录结构：**

```
.claude/skills/fill-distances/
├── SKILL.md                    # Skill 定义文件
└── scripts/
    └── fill_distances.py       # 配套 Python 脚本
```

**SKILL.md 编写：**

```markdown
---
name: fill-distances
description: Fill distance information into billing Excel files
  using cached data. Supports multiple regions. Automatically
  detects region and uses appropriate cache.
allowed-tools: Bash(python:*), Bash(.venv/bin/python:*), Read
---

# Fill Distances to Billing Data

## Usage

When the user asks to fill distances or complete billing
data with distances:

\```bash
.venv/bin/python .claude/skills/fill-distances/scripts/fill_distances.py \
  <excel_file> [cache_json] [region]
\```

### Parameters

- `excel_file`: Billing Excel file path (required)
- `cache_json`: Distance cache JSON path (optional, defaults to region cache)
- `region`: Region identifier (optional, auto-detected from path)

## How It Works

1. Load distance cache from JSON
2. Detect region from file path
3. For each route in Excel:
   - Skip rows already containing distance info
   - First stop: look up warehouse-to-first-stop distance
   - Subsequent stops: look up stop-to-stop distance
4. Append `-XXkm` suffix to each store name, or `-?km` if not found
5. Save modified Excel

## Examples

### Auto-detect region

\```bash
.venv/bin/python .claude/skills/fill-distances/scripts/fill_distances.py \
  data/region-a/summary/billing_0119.xlsx
\```

### Manual region

\```bash
.venv/bin/python .claude/skills/fill-distances/scripts/fill_distances.py \
  /tmp/billing.xlsx data/region-a/cache/distances.json region-a
\```

## Important Notes

- In-place modification
- Idempotent (processed rows are skipped)
- Reports match/miss statistics after completion
```

**配套脚本的关键设计：**

脚本并非 Skill 的必要组成，但在以下情况下推荐将逻辑封装为独立脚本：

| 场景 | 是否需要脚本 | 原因 |
|------|------------|------|
| 简单的文件操作 | 否 | 大模型可直接用内置工具完成 |
| 复杂的数据处理 | 是 | 逻辑过多，纯 Prompt 难以可靠执行 |
| 需要精确控制格式 | 是 | Excel 单元格合并、样式等操作需要代码 |
| 涉及模糊匹配 | 是 | 名称归一化等逻辑用代码更可靠 |

本案例中，距离填充涉及多级模糊匹配（精确匹配 -> 括号归一化 -> 激进归一化 -> 模糊搜索），这类逻辑适合固化为 Python 脚本，而非让大模型每次即兴发挥。

### 使用效果对比

**无 Skill 时的对话：**

```
用户: 帮我把 billing_0119.xlsx 的距离填上，
      用 distances.json 里的缓存数据，
      注意起点是固定的仓库地址，
      第一行是仓库到首站距离，
      后面每行是上一站到下一站的距离，
      格式是"名称-距离km"，找不到的标记"名称-?km"，
      已经有距离的行跳过，
      括号要做全角半角兼容……

大模型: (需要理解所有规则后执行)
```

**有 Skill 时的对话：**

```
用户: /fill-distances data/summary/billing_0119.xlsx

大模型: (自动加载 SKILL.md，按预定流程执行)
```

或者更自然地：

```
用户: 把这个对账单的距离补全

大模型: (匹配到 fill-distances skill，自动执行)
```

---

## 开发你的第一个 Skill

### 第一步：创建目录和文件

```bash
mkdir -p .claude/skills/my-first-skill
touch .claude/skills/my-first-skill/SKILL.md
```

### 第二步：编写 SKILL.md

从最小可用版本开始：

```markdown
---
name: my-first-skill
description: Count lines of code in the project, grouped by file type.
allowed-tools: Bash(find:*), Bash(wc:*)
---

# Count Lines of Code

## Usage

When the user asks to count lines of code or get project statistics:

\```bash
find . -name "*.py" -not -path "./.venv/*" | xargs wc -l | sort -rn
\```

Summarize results by file type and total.
```

### 第三步：测试

在 Claude Code 中直接输入 `/my-first-skill` 或用自然语言触发：

```
用户: 统计一下项目的代码量
```

### 第四步：迭代完善

根据实际使用中遇到的问题，逐步补充：
- 增加参数支持（如指定目录、文件类型）
- 添加边界情况处理
- 补充更多示例
- 如果逻辑变复杂，抽取为独立脚本

### 检查清单

在发布一个 Skill 之前，对照以下清单：

```
[ ] name 使用 kebab-case，简洁且有动词性
[ ] description 包含动作、对象和关键词
[ ] allowed-tools 遵循最小权限原则
[ ] Usage 部分说明了触发条件（When the user asks to...）
[ ] Parameters 部分列出了所有参数及默认值
[ ] Examples 部分提供了至少一个可直接复制执行的示例
[ ] Notes 部分说明了幂等性、副作用等关键行为
[ ] 如有配套脚本，脚本放在 skills/<name>/scripts/ 下
```

---

## 进阶：Skill 体系设计

### 单 Skill vs Skill 体系

当你的工作流包含多个步骤时，面临一个设计选择：

**方案 A：一个大 Skill 包办一切**

```yaml
name: process-all
description: Extract, fill, compute, and update everything.
```

**方案 B：多个小 Skill 各司其职**

```yaml
name: extract-data      # 步骤 1
name: fill-data          # 步骤 2
name: compute-values     # 步骤 3
name: update-cache       # 步骤 4
```

推荐方案 B，原因：

| 维度 | 大 Skill | 小 Skill 体系 |
|------|---------|--------------|
| 调试 | 难以定位问题 | 可逐步排查 |
| 灵活性 | 只能全量执行 | 可按需组合 |
| 人工介入 | 无法中途干预 | 每个环节可检查/修正 |
| 复用性 | 不可复用 | 单个 Skill 可独立使用 |
| 可维护性 | 修改影响全局 | 改一个不影响其他 |

### Skill 间的数据传递

Skill 之间通过文件系统传递数据，常见模式：

**1. 链式传递**

```
Skill A 输出文件 → Skill B 读取同一文件

extract-stores 输出 stores.txt
    → fill-stores 读取 stores.txt + 模板.xlsx，输出 filled.xlsx
        → fill-distances 读取 filled.xlsx，原地修改
```

**2. 共享缓存**

```
多个 Skill 读写同一个缓存文件

fill-distances   ← 读取 ← cache/distances.json
update-cache     → 写入 → cache/distances.json
```

**3. 约定路径**

```
通过目录约定而非参数传递来关联数据

data/<region>/details/     → extract-stores 的输入目录
data/<region>/summary/     → fill-stores 的输出目录
data/<region>/cache/       → 共享缓存目录
```

### 配套脚本的组织

当多个 Skill 共享业务逻辑时，推荐提取公共模块：

```
项目根目录/
├── scripts/
│   ├── core/              # 核心业务逻辑（被 Skill 脚本调用）
│   │   ├── extract.py
│   │   ├── fill.py
│   │   └── cache.py
│   └── utils/             # 通用工具函数
│       └── common.py      # 名称归一化、格式解析等
├── .claude/skills/
│   ├── skill-a/
│   │   ├── SKILL.md
│   │   └── scripts/
│   │       └── run_a.py   # 调用 scripts/core/ 中的逻辑
│   └── skill-b/
│       ├── SKILL.md
│       └── scripts/
│           └── run_b.py
```

这样做的好处：
- Skill 脚本保持薄层，只负责参数解析和调用
- 核心逻辑集中管理，避免重复
- 可以脱离 Skill 直接调用核心脚本进行调试

---

## 常见问题与最佳实践

### 1. Skill 应该写多详细？

**原则：假设阅读者是一个聪明但对你的项目一无所知的人。**

- 业务规则（如"第一行距离是起点到首站"）：必须详细写明
- 通用编程知识（如"如何读取 JSON 文件"）：不必赘述
- 文件路径和格式：必须明确给出
- 边界情况（如"已处理的行会被跳过"）：应当说明

### 2. description 写不好怎么办？

试着回答这个问题：**"用户会说什么话来触发这个 Skill？"**

把这些话的关键词都放进 description 里：

```yaml
# 用户可能说：
# "填充距离" / "补全距离" / "把距离加上" / "fill distances"

description: Fill distance information into billing Excel files
  using cached data. Supports auto-detection.
```

### 3. 什么时候该用脚本，什么时候让大模型直接操作？

```
复杂度低 + 格式宽松  → 让大模型直接用内置工具
复杂度高 + 格式严格  → 封装为 Python 脚本
涉及精确计算/匹配   → 封装为脚本
涉及 Excel 样式操作  → 封装为脚本
一次性操作          → 不需要 Skill
反复出现的操作       → 封装为 Skill
```

### 4. Skill 的版本管理

Skill 定义文件（SKILL.md）和配套脚本都应纳入版本控制：

```bash
git add .claude/skills/
git commit -m "Add fill-distances skill"
```

这样做的好处：
- 团队成员 clone 仓库后即可使用所有 Skill
- Skill 的变更有迹可循
- 可以在不同分支上实验 Skill 的修改

### 5. Skill 失败了怎么排查？

排查步骤：

1. **检查 SKILL.md 的 allowed-tools** —— 是否声明了所需的工具？
2. **检查 settings.local.json** —— 项目层是否放行了对应的工具？
3. **手动执行配套脚本** —— 脱离 Skill 直接运行，确认脚本本身没有问题
4. **检查 description** —— 如果是自然语言触发失败，可能是匹配不上
5. **查看大模型的输出** —— 大模型会解释它的执行过程和遇到的问题

---

## 总结

Skill 的本质是一种**面向大模型的标准操作程序（SOP）**。它利用了大模型的语言理解和工具调用能力，将人类编写的操作手册转化为可自动执行的工作流。

```
传统自动化:  人类 → 编写代码 → 计算机执行
Skill 模式:  人类 → 编写指令文档 → 大模型理解并执行
```

这种模式的独特之处在于：指令文档是用自然语言编写的，大模型能够在执行过程中进行推理和判断，处理模板中未预见的边界情况。这既保留了自动化的效率，又具备了一定的灵活性。

开发 Skill 的核心心法：

1. **从重复工作中提炼** —— 做过两次以上的操作就值得封装
2. **保持单一职责** —— 一个 Skill 只解决一个问题
3. **让示例说话** —— Examples 比长篇描述更有效
4. **最小权限** —— 只声明必要的工具
5. **文件传递** —— Skill 之间通过文件松耦合
