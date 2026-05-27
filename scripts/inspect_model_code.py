#!/usr/bin/env python3
"""Inspect model code and emit an adapter planning report.

This script uses Python's AST only. It does not import project code, so it is
safe to run before dependencies are installed.
"""
from __future__ import annotations

import argparse
import ast
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def dotted_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = dotted_name(node.value)
        return f"{base}.{node.attr}" if base else node.attr
    if isinstance(node, ast.Subscript):
        return dotted_name(node.value)
    if isinstance(node, ast.Call):
        return dotted_name(node.func)
    return ""


def function_args(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> list[str]:
    args = [arg.arg for arg in fn.args.args]
    if fn.args.vararg:
        args.append("*" + fn.args.vararg.arg)
    if fn.args.kwarg:
        args.append("**" + fn.args.kwarg.arg)
    return args


def class_info(cls: ast.ClassDef) -> dict[str, Any]:
    methods = []
    for item in cls.body:
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
            methods.append({
                "name": item.name,
                "args": function_args(item),
                "lineno": item.lineno,
            })
    bases = [dotted_name(base) for base in cls.bases if dotted_name(base)]
    is_torch_module = any(base.endswith("nn.Module") or base.endswith("Module") for base in bases)
    return {
        "name": cls.name,
        "lineno": cls.lineno,
        "bases": bases,
        "is_possible_torch_module": is_torch_module,
        "methods": methods,
    }


def inspect_file(path: Path, root: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    try:
        tree = ast.parse(text, filename=str(path))
    except SyntaxError as exc:
        return {"path": path.as_posix(), "syntax_error": str(exc)}

    imports = []
    classes = []
    functions = []
    has_main_guard = False
    argparse_used = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            imports.extend(f"{module}.{alias.name}".strip(".") for alias in node.names)
        elif isinstance(node, ast.ClassDef):
            classes.append(class_info(node))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not isinstance(getattr(node, "parent", None), ast.ClassDef):
                functions.append({"name": node.name, "args": function_args(node), "lineno": node.lineno})
        elif isinstance(node, ast.If):
            test = ast.dump(node.test)
            if "__name__" in test and "__main__" in test:
                has_main_guard = True
        elif isinstance(node, ast.Attribute):
            if dotted_name(node).startswith("argparse."):
                argparse_used = True
        elif isinstance(node, ast.Name):
            if node.id == "argparse":
                argparse_used = True

    rel = path.relative_to(root).as_posix() if path.is_relative_to(root) else path.as_posix()
    return {
        "path": rel,
        "imports": sorted(set(imports)),
        "classes": classes,
        "functions": functions,
        "has_main_guard": has_main_guard,
        "argparse_used": argparse_used,
    }


def attach_parents(tree: ast.AST) -> None:
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            setattr(child, "parent", parent)


def inspect_file_with_parents(path: Path, root: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    try:
        tree = ast.parse(text, filename=str(path))
    except SyntaxError as exc:
        return {"path": path.as_posix(), "syntax_error": str(exc)}
    attach_parents(tree)

    imports = []
    classes = []
    functions = []
    has_main_guard = False
    argparse_used = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            imports.extend(f"{module}.{alias.name}".strip(".") for alias in node.names)
        elif isinstance(node, ast.ClassDef):
            classes.append(class_info(node))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not isinstance(getattr(node, "parent", None), ast.ClassDef):
                functions.append({"name": node.name, "args": function_args(node), "lineno": node.lineno})
        elif isinstance(node, ast.If):
            test = ast.dump(node.test)
            if "__name__" in test and "__main__" in test:
                has_main_guard = True
        elif isinstance(node, ast.Attribute):
            if dotted_name(node).startswith("argparse."):
                argparse_used = True
        elif isinstance(node, ast.Name):
            if node.id == "argparse":
                argparse_used = True

    rel = path.relative_to(root).as_posix() if path.is_relative_to(root) else path.as_posix()
    return {
        "path": rel,
        "imports": sorted(set(imports)),
        "classes": classes,
        "functions": functions,
        "has_main_guard": has_main_guard,
        "argparse_used": argparse_used,
    }


def suggest_candidates(files: list[dict[str, Any]]) -> list[dict[str, str]]:
    candidates = []
    for file_info in files:
        path = file_info.get("path", "")
        for cls in file_info.get("classes", []):
            if cls.get("is_possible_torch_module") or any(m.get("name") == "forward" for m in cls.get("methods", [])):
                candidates.append({
                    "kind": "model_class",
                    "path": path,
                    "name": cls["name"],
                    "reason": "class resembles a model or defines forward",
                })
        for fn in file_info.get("functions", []):
            lowered = fn["name"].lower()
            if lowered in {"train", "fit", "evaluate", "test", "predict", "main", "build_model", "create_model"}:
                candidates.append({
                    "kind": "entry_function",
                    "path": path,
                    "name": fn["name"],
                    "reason": "function name looks like an experiment entrypoint",
                })
        if file_info.get("has_main_guard"):
            candidates.append({
                "kind": "script_entrypoint",
                "path": path,
                "name": "__main__",
                "reason": "file has a command-line main guard",
            })
    return candidates


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--code-dir", default="code")
    parser.add_argument("--output", default="docs/model_code_inventory.json")
    args = parser.parse_args()

    root = Path(".").resolve()
    code_dir = Path(args.code_dir)
    files = []
    if code_dir.exists():
        for path in sorted(code_dir.rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            files.append(inspect_file_with_parents(path.resolve(), root))

    report = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "code_dir": args.code_dir,
        "file_count": len(files),
        "files": files,
        "adapter_candidates": suggest_candidates(files),
        "next_step": "Use this report plus docs/model_adapter_spec.md to generate or revise a project-specific adapter.",
    }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote model code inventory to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
