#!/usr/bin/env bash
set -euo pipefail

python scripts/validate_config.py
python scripts/check_placeholders.py docs paper code results paper_config.yaml AGENTS.md
python scripts/check_results_schema.py
python scripts/validate_bib.py
python scripts/count_tex_words.py
python scripts/check_claims_against_results.py

if [ -f paper/mypaper/main.tex ]; then
  bash scripts/compile_latex.sh || echo "WARNING: LaTeX compile failed or LaTeX is not installed."
fi
