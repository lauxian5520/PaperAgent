# Writing Rules

Use this file for outline, drafting, revision, LaTeX export, and final paper packaging.

## Positioning

Write a rigorous, evidence-based technical paper. The goal is to produce a submission-ready draft, not to guarantee acceptance.

## Core paper principles

- Sushi, not curry: focus on 1-2 core ideas.
- Figure 1 should communicate the central contribution.
- State contributions clearly in Abstract and Introduction.
- Match claims to evidence.
- Include limitations honestly.
- Include enough detail for reproducibility.

## Required structure

Use the target conference template and maintain files under `paper/mypaper/`:

```text
paper/mypaper/
├── main.tex
├── sections/
│   ├── introduction.tex
│   ├── related_work.tex
│   ├── method.tex
│   ├── experiments.tex
│   ├── results.tex
│   ├── discussion.tex
│   ├── limitations.tex
│   └── conclusion.tex
└── figures/
```

Recommended paper sections:

- Abstract
- Introduction
- Related Work
- Method
- Experiments
- Results
- Discussion
- Limitations
- Conclusion
- References
- Appendix

## Length guidance

Word counts are heuristics; final compliance is determined by compiled LaTeX page count.

Recommended main-body depth:

- Abstract: 150-250 words
- Introduction: 800-1000 words
- Related Work: 600-800 words
- Method: 1000-1500 words
- Experiments: 800-1200 words
- Results: 600-800 words
- Discussion: 400-600 words
- Limitations: 200-300 words
- Conclusion: 200-300 words

Do not use filler to meet length. Expand only by adding real research gap analysis, technical detail, experimental detail, or evidence-based discussion.

## Figure and table rules

- Every figure must be generated from real data or clearly marked as conceptual.
- For conceptual figures, store the prompt as a LaTeX comment next to the figure placeholder.
- For data figures, save the script and source data.
- Tables must be reproducible from `results/`.

## Claims discipline

Before writing a claim, ask:

1. Is this claim supported by a citation or experiment result?
2. Is the cited paper actually about this claim?
3. Does the experiment log contain the number used in the text?
4. Is the uncertainty, variance, or limitation disclosed?

If the answer is no, revise or remove the claim.

## LaTeX rules

- Use the venue template under `paper/venue_template/`.
- Keep section files small and named by section.
- Avoid unresolved placeholders.
- Compile before final delivery.
- Do not manually edit generated result numbers unless they are traceable to results.

## Review readiness

Before final quality gate:

```bash
python scripts/check_placeholders.py docs paper code results paper_config.yaml AGENTS.md
python scripts/check_claims_against_results.py
python scripts/validate_bib.py
python scripts/count_tex_words.py
bash scripts/compile_latex.sh
```
