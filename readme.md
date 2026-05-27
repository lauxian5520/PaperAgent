# Codex 顶会论文研究 Agent 模板

这是一个可移植到 Codex / coding agent 项目中的论文研究流水线模板。它由一份精简的 `AGENTS.md`、若干阶段化参考规则、可执行检查脚本和模板文件组成，适合 Codex 长期执行的仓库级 agent 配置。

它适合用于：

- AI/ML 论文项目的研究规划、实验实现、结果整理和 LaTeX 写作。
- 强制执行“真实文献、真实实验、真实引用、真实证据”的项目纪律。
- 将大型论文流程拆成可验证、可回滚、可人工审批的阶段。

它不应该被理解为“一键保证顶会录用”的工具。顶会论文是否成立仍然取决于研究问题、方法新颖性、实验强度、基线公平性、写作质量和人工审查。

## 文件结构

```text
.
├── AGENTS.md                         # Codex 仓库级入口指令
├── paper_config.yaml                 # 项目配置，使用前必须填写
├── paper_config.example.yaml         # 配置样例
├── PROGRESS.md                       # 进度记录，可从 templates/ 复制或直接使用
├── references/                       # 长规则，按需读取，避免污染上下文
│   ├── pipeline.md
│   ├── experiment_rules.md
│   ├── literature_rules.md
│   ├── writing_rules.md
│   ├── evidence_gate.md
│   ├── prompt_templates.md
│   └── legacy_original_AGENTS.md     # 原始长版 AGENTS，仅用于追溯，不建议每次加载
├── scripts/                          # 可执行检查和辅助脚本
│   ├── validate_config.py
│   ├── check_placeholders.py
│   ├── check_results_schema.py
│   ├── check_claims_against_results.py
│   ├── validate_bib.py
│   ├── count_tex_words.py
│   ├── literature_collect_openalex.py
│   ├── make_stage_plan.py
│   ├── compile_latex.sh
│   └── run_all_checks.sh
├── templates/                        # 阶段计划、进度、审稿和 schema 模板
├── docs/                             # 你的论文构想、实验构想和相关工作问题
├── code/                             # 实验代码
├── data/                             # 实验数据
├── results/                          # 实验结果、日志、图表中间数据
├── plans/                            # 每个阶段开始前的计划
└── paper/
    ├── venue_template/               # 目标会议 LaTeX 模板
    └── mypaper/                      # 论文主目录
```

## 安装方式

### 方式 A：作为新论文项目使用

解压后直接进入目录：

```bash
cd codex-topconf-paper-agent
```

然后编辑：

```bash
paper_config.yaml
```

把所有 `REPLACE_ME` 替换成你的真实项目配置。

### 方式 B：复制到已有论文仓库

在已有仓库根目录解压或复制本模板中的这些文件：

```text
AGENTS.md
paper_config.yaml
references/
scripts/
templates/
```

如果已有 `AGENTS.md`，先备份：

```bash
cp AGENTS.md AGENTS.backup.md
```

再合并或替换。


### 方式 C：用 bootstrap 脚本安装到已有仓库

也可以先解压本模板，然后执行：

```bash
python scripts/bootstrap_agent.py --target /path/to/your/repo
```

默认不会覆盖已有文件；如果确认要覆盖，使用：

```bash
python scripts/bootstrap_agent.py --target /path/to/your/repo --force
```

## 第一次配置

1. 填写 `paper_config.yaml`。
2. 把你的论文构想放到 `docs/`，至少建议包括：
   - `docs/paper_idea.md`
   - `docs/experiment_plan.md`
   - `docs/literature_and_questions.md`
3. 把目标会议模板放到 `paper/venue_template/`。
4. 初始化进度文件：

```bash
cp templates/PROGRESS.template.md PROGRESS.md
```

5. 运行配置检查：

```bash
python scripts/validate_config.py
```

配置通过后，再让 Codex 开始执行阶段任务。

## 推荐的第一条 Codex 指令

不要一开始就要求 Codex 完成整篇论文。建议先做 readiness check：

```text
Follow AGENTS.md strictly.

Read paper_config.yaml, PROGRESS.md, docs/, and only the necessary references.
Validate whether this repository is ready for the paper pipeline.
Do not write the paper yet.
Check missing files, unresolved placeholders, path validity, unclear constraints, and missing LaTeX template files.
Create plans/readiness_check.md and update PROGRESS.md.
Stop after the readiness report.
```

## 推荐的阶段化执行方式

### 阶段 A：研究定义

```text
Follow AGENTS.md strictly.

Run stages 1-2 only: TOPIC_INIT and PROBLEM_DECOMPOSE.
Read paper_config.yaml and docs/*.md.
Create plans/stage_A_research_definition.md.
Write outputs to docs/research_definition.md.
Update PROGRESS.md.
Stop after completing stage 2.
```

### 阶段 B：文献发现

```text
Follow AGENTS.md strictly.

Run stages 3-6 only.
Use real literature retrieval sources where available.
Do not invent citations.
Save retrieved metadata to results/literature_candidates.jsonl.
Save screened papers to results/literature_shortlist.json.
Save knowledge cards to docs/knowledge_cards.md.
Update PROGRESS.md.
Stop before synthesis.
```

### 阶段 D/E：实验设计和 pilot

```text
Follow AGENTS.md strictly.

Run experiment design and pilot only.
Do not run the full experiment.
Create a small pilot that estimates runtime and validates metrics.
Write pilot outputs to results/pilot_results.json.
Update PROGRESS.md.
Stop and summarize whether full execution is feasible.
```

### 阶段 G：论文写作

```text
Follow AGENTS.md strictly.

Draft the paper outline and only the Introduction section.
Use only verified citations and actual experiment outputs.
Do not invent results.
Write to paper/mypaper/sections/introduction.tex.
Update PROGRESS.md.
```

## 常用检查命令

```bash
python scripts/validate_config.py
python scripts/check_placeholders.py docs paper code results paper_config.yaml AGENTS.md
python scripts/check_results_schema.py
python scripts/validate_bib.py
python scripts/count_tex_words.py
python scripts/check_claims_against_results.py
bash scripts/run_all_checks.sh
```

## 文献检索脚本

本模板包含一个可选的 OpenAlex 检索脚本：

```bash
python scripts/literature_collect_openalex.py --query "your topic" --from-year 2020 --max-results 50 --output results/literature_candidates.jsonl
```

它只负责从真实 API 抓取候选文献。LLM 可以筛选和总结这些文献，但不能凭空生成论文元数据。

## 重要原则

- `AGENTS.md` 应保持短小。长规则放在 `references/`。
- `paper_config.yaml` 是唯一的项目变量来源。
- 每个阶段都要先写计划，再执行，再验证，再更新 `PROGRESS.md`。
- 文献候选必须来自真实 API 或真实网页，不允许 LLM 生成“看起来真实”的论文。
- 所有定量结论必须能追溯到 `results/` 或实验日志。
- 所有引用必须能追溯到 DOI、arXiv、Semantic Scholar、OpenAlex 或真实 URL。
- 在质量门控前必须运行 evidence gate。

## 典型失败模式

1. 直接要求 Codex “自动完成整篇顶会论文”。这会导致任务过大、证据失控和引用幻觉。
2. 没有填写 `paper_config.yaml`。这会让占位符进入论文。
3. 没有真实运行实验，却让模型写 Results。
4. 让模型生成文献列表，而不是从真实 API 检索。
5. 缺少消融实验或强基线，却宣称方法有效。

## 推荐工作流

```text
readiness check
→ stage A: topic and problem decomposition
→ stage B: real literature retrieval and screening
→ stage C: synthesis and hypotheses
→ stage D: experiment design and pilot
→ human gate
→ stage E: full experiments
→ evidence gate
→ stage G: paper drafting
→ peer review and revision
→ final quality gate
```

这个模板的核心目标不是让 agent “替你做科研判断”，而是让 agent 在你监督下稳定完成重复、繁琐、可验证的工程化科研任务。

## 需要你自己填写或准备的内容

在让 agent 开始正式实验、文献检索或论文写作之前，你需要先补齐下面这些内容。可以把它理解为“把你的科研项目交接给 agent 的输入清单”。如果这些内容没有准备好，agent 应该停止，而不是凭空猜测研究问题、数据集、baseline 或实验结果。

### 1. `paper_config.yaml`：项目总配置

这是整个项目最重要的配置文件，也是 agent 启动时最先读取的文件。你需要把其中所有 `REPLACE_ME` 替换成真实信息。

你需要填写：

- `project_name`：项目名称，用于标识这篇论文或实验项目。
- `paper.title`：论文暂定标题，可以后续修改，但不要留空。
- `paper.target_conference`：目标会议或期刊，例如 `ICLR 2027`、`NeurIPS 2026`。
- `paper.deadline`：投稿截止时间，建议写清楚时区。
- `research.topic_short_name`：研究主题短名，方便生成文件名和实验名。
- `research.topic_description`：研究问题的具体描述，越具体越好。
- `research.primary_claim`：你希望通过实验验证的核心论断。
- `research.domains`：研究领域，例如 machine learning、drug discovery、computer vision、NLP。
- `research.core_contributions`：你认为论文可能包含的贡献点，例如方法贡献、理论分析、实验评估。
- `paths.source_repo`：已有模型代码所在路径。如果代码就在本项目中，可以写 `.` 或 `code`。
- `paths.docs_repo`：文档路径，通常写 `docs`。
- `paths.examples_repo`：示例代码或参考实现路径，没有可以写 `examples`，但应确保路径含义清楚。
- `paths.latex_template`：目标会议 LaTeX 模板路径，默认是 `paper/venue_template`。
- `paths.paper_dir`：论文正文路径，默认是 `paper/mypaper`。
- `paths.results_dir`：实验结果路径，默认是 `results`。
- `paths.code_dir`：实验代码路径，默认是 `code`。
- `paths.data_dir`：数据集路径，默认是 `data`。
- `constraints`：文献数量、实验条件数量、是否允许未验证引用、是否允许 synthetic results 等约束。
- `compute_budget`：总运行时间、单次运行时间、是否必须 pilot、预算停止阈值。
- `submission`：是否匿名、是否包含 reproducibility statement、是否包含 acknowledgements。

你要做什么：

1. 打开 `paper_config.yaml`。
2. 删除所有 `REPLACE_ME`。
3. 用真实项目路径和真实研究信息替换。
4. 运行：

```bash
python scripts/validate_config.py
python scripts/check_placeholders.py paper_config.yaml
```

### 2. `docs/paper_idea.md`：你的论文想法

这个文件用于告诉 agent：你到底想研究什么，为什么这个问题重要，你的方法大概是什么。

你需要填写：

- 研究背景：这个问题属于哪个方向，为什么值得研究。
- 目标场景：模型最终服务于什么任务、用户或应用场景。
- 核心技术 idea：你的模型结构、关键模块、训练目标或算法流程。
- 相比已有方法的不足：你认为 prior work 没有解决什么问题。
- 预期贡献：方法、理论、系统、实验或数据贡献。
- 风险和弱点：你已经预见到的失败点，例如数据规模小、baseline 强、计算成本高。

你要做什么：

1. 用自然语言完整写出你的 idea。
2. 如果已有模型结构图、公式、伪代码或模块说明，把路径或内容写进去。
3. 不要写“效果一定更好”这类未经实验验证的结论，只写“希望验证”的假设。

### 3. `docs/experiment_plan.md`：实验计划

这是让 agent 进入实验设计和代码实现前最关键的文件。它应该明确告诉 agent：数据在哪里、模型入口在哪里、要对比谁、用什么指标评估。

你需要填写：

- `Task`：任务类型，例如分类、回归、检索、生成、预测、排序、优化、表征学习。
- `Datasets`：每个数据集的名称、路径、格式、字段含义、train/val/test 划分方式。
- `Proposed Model`：你的模型结构、代码入口、主要类名、输入输出、loss、训练方式。
- `Baselines`：需要对比的 baseline 模型，包括论文、代码链接、本地路径或需要 agent 实现的说明。
- `Metrics`：主指标和辅助指标，例如 Accuracy、F1、AUROC、RMSE、MAE、Recall@K。
- `Ablations`：消融项，例如去掉某个模块、替换 encoder、替换 loss、关闭某个训练策略。
- `Downstream Tasks`：下游任务设置，如果你的方法需要验证迁移、泛化或实际应用价值。
- `Compute Budget`：GPU/CPU、显存、最大训练时长、是否允许完整训练。
- `Expected Failure Modes`：你认为最可能失败的地方，例如过拟合、数据泄漏、baseline 难复现。

你要做什么：

1. 把已下载数据集的真实路径写清楚。
2. 把已有模型代码的入口写清楚，例如 `code/train.py`、`code/models/my_model.py`。
3. 明确哪些 baseline 已有代码，哪些需要 agent 补充实现。
4. 明确 pilot 该跑多小，例如一个数据子集、一个 seed、一个 epoch。

### 4. `docs/literature_and_questions.md`：文献和审稿问题

这个文件用于约束文献检索和 baseline 选择，避免 agent 随机找一批不相关论文。

你需要填写：

- 已知相关论文：标题、arXiv、DOI、GitHub 或 BibTeX。
- 最接近的 prior work：哪些方法最可能被审稿人拿来比较。
- 必须比较的 baseline：经典方法、近期强方法、领域标准方法。
- 审稿人可能质疑的问题：新颖性、有效性、公平性、泛化性、复杂度等。
- 必须引用的方向：例如某类方法、某个数据集、某个 benchmark。
- 潜在 novelty threat：哪些已有工作可能和你的 idea 接近。

你要做什么：

1. 把你已经知道的论文先列出来。
2. 明确哪些 baseline 是“必须比较”，哪些是“可选比较”。
3. 如果你不确定 baseline 是否合适，让 agent 先做文献发现和筛选，不要直接进入实验。

### 5. `code/`：模型和实验代码

这个目录放可执行实验代码。你可以把已有代码复制到这里，也可以在 `paper_config.yaml` 中把 `paths.source_repo` 指向外部代码仓库。

建议准备：

```text
code/
  models/
  datasets/
  baselines/
  train.py
  evaluate.py
  run_experiments.py
  summarize_results.py
```

你需要提供或说明：

- 模型定义在哪里。
- 数据加载逻辑在哪里。
- 训练入口命令是什么。
- 测试入口命令是什么。
- 配置文件格式是什么。
- 是否已有 baseline 实现。
- 运行代码需要哪些依赖。

你要做什么：

1. 放入已有模型代码，或写清楚外部仓库路径。
2. 确保代码能用一个最小命令跑通。
3. 如果还没有训练脚本，让 agent 先生成 pilot 版本，不要直接要求完整实验。

### 6. `data/`：数据集

这个目录放本地数据集。agent 不应该猜测数据格式，因此你必须在 `docs/experiment_plan.md` 中解释数据内容。

建议准备：

```text
data/
  dataset_a/
    train.csv
    val.csv
    test.csv
  dataset_b/
    raw/
    processed/
```

你需要说明：

- 每个文件是什么。
- 每一列或每个字段的含义。
- 标签字段在哪里。
- 是否已有固定 train/val/test split。
- 是否允许 agent 生成预处理文件。
- 数据是否可以公开，论文中能否直接说明来源。

你要做什么：

1. 把数据放入 `data/` 或在配置中写外部路径。
2. 写清楚数据格式和划分方式。
3. 如果数据很大，提供一个小样本或说明如何运行 pilot。

### 7. `paper/venue_template/`：会议模板

这个目录放目标会议的 LaTeX 模板。当前模板目录只是占位，正式写作前需要替换成真实会议模板。

你需要准备：

- 官方 LaTeX class/style 文件。
- 官方示例 tex。
- bibliography style 文件。
- 会议要求说明，例如页数、匿名规则、补充材料规则。

你要做什么：

1. 从目标会议官网下载模板。
2. 放到 `paper/venue_template/`。
3. 在 `paper_config.yaml` 中确认 `paper.target_conference` 和 `paths.latex_template` 正确。

### 8. `paper/mypaper/references.bib`：真实引用

这个文件放论文最终使用的 BibTeX。agent 可以帮你整理，但引用必须来自真实来源。

你需要准备：

- 已知论文的 BibTeX。
- 数据集论文或 benchmark 论文引用。
- baseline 方法引用。
- 工具库或框架引用，如果目标会议要求。

你要做什么：

1. 不要手写虚构 BibTeX。
2. 优先从 arXiv、DOI、OpenAlex、Semantic Scholar、出版社页面或官方仓库获取。
3. 运行：

```bash
python scripts/validate_bib.py
```

### 9. `results/`：真实实验结果

这个目录不需要你手工编造内容。它应该由实验脚本生成，或者由 agent 在真实运行后写入。

你需要确保：

- pilot 结果保存到 `results/pilot_results.json` 或等价文件。
- full experiment 结果保存为 JSON、JSONL 或 CSV。
- 每次实验记录命令、seed、时间、硬件、软件版本、数据集、模型配置、指标、日志和失败信息。
- 论文中的定量结论都能追溯到这里。

你要做什么：

1. 不要手工填写最终指标。
2. 如果已有历史实验结果，把原始日志、配置和结果文件放进 `results/`。
3. 让 agent 先检查结果格式，再写 Results。

### 10. `PROGRESS.md`：进度和决策记录

这个文件记录当前阶段、关键输出、证据文件和风险。agent 每完成一个阶段都应该更新。

你需要关注：

- 当前 stage 是否正确。
- 是否已经通过 human gate。
- 哪些结果已经有证据。
- 哪些风险还没有解决。

你要做什么：

1. 第一次使用时可以从 `templates/PROGRESS.template.md` 初始化。
2. 每次阶段完成后检查 agent 是否更新了它。
3. 如果你人工批准进入 full experiment、修改研究假设或改变 compute budget，也应该记录在这里。

## 最小交接清单

如果你已经有 idea、模型结构和数据集，最少需要完成下面这些文件和目录：

```text
paper_config.yaml
docs/paper_idea.md
docs/experiment_plan.md
docs/literature_and_questions.md
code/
data/
paper/venue_template/
```

完成后先运行：

```bash
python scripts/validate_config.py
python scripts/check_placeholders.py paper_config.yaml docs paper
```

通过后，再让 agent 执行实验设计和 pilot，而不是直接跑完整实验：

```text
Follow AGENTS.md strictly.

Run experiment design and pilot only.
Read paper_config.yaml, docs/paper_idea.md, docs/experiment_plan.md, and references/experiment_rules.md.
Inspect code/ and data/.
Create plans/experiment_design_and_pilot.md.
Write final experiment design to docs/final_experiment_design.md.
Generate or adapt runnable experiment code under code/.
Run one small pilot condition only.
Save pilot output to results/pilot_results.json.
Update PROGRESS.md.
Stop before full experiments.
```
