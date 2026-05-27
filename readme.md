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
