#!/usr/bin/env bash
set -euo pipefail

PAPER_DIR="${1:-paper/mypaper}"
MAIN="${2:-main.tex}"

if [ ! -d "$PAPER_DIR" ]; then
  echo "Missing paper directory: $PAPER_DIR" >&2
  exit 1
fi

cd "$PAPER_DIR"

if [ ! -f "$MAIN" ]; then
  echo "Missing LaTeX main file: $PAPER_DIR/$MAIN" >&2
  exit 1
fi

if command -v latexmk >/dev/null 2>&1; then
  latexmk -pdf -interaction=nonstopmode -halt-on-error "$MAIN"
elif command -v pdflatex >/dev/null 2>&1; then
  pdflatex -interaction=nonstopmode -halt-on-error "$MAIN"
  if [ -f "references.bib" ] && command -v bibtex >/dev/null 2>&1; then
    bibtex "${MAIN%.tex}" || true
    pdflatex -interaction=nonstopmode -halt-on-error "$MAIN"
    pdflatex -interaction=nonstopmode -halt-on-error "$MAIN"
  fi
else
  echo "No LaTeX engine found. Install latexmk or pdflatex." >&2
  exit 1
fi
