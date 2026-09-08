"""Strict enforcement of No-LLM architectural policy.

This application explicitly bans generative LLMs, external cloud LLM endpoints,
and generative AI libraries.
"""

import ast
import os
from pathlib import Path
from typing import List, Tuple

FORBIDDEN_PACKAGES = {
    "openai",
    "anthropic",
    "google.generativeai",
    "google.genai",
    "langchain_openai",
    "langchain_anthropic",
    "litellm",
    "ollama",
    "transformers.pipeline",
    "cohere",
    "mistralai",
}

FORBIDDEN_ENDPOINT_PATTERNS = [
    "openai.com",
    "api.anthropic.com",
    "generativelanguage.googleapis.com",
    "api.cohere.ai",
    "api.mistral.ai",
    "api.together.xyz",
    "api.groq.com",
]


class ImportScanner(ast.NodeVisitor):
    def __init__(self, filename: str):
        self.filename = filename
        self.violations: List[Tuple[str, int, str]] = []

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            for forbidden in FORBIDDEN_PACKAGES:
                if alias.name == forbidden or alias.name.startswith(forbidden + "."):
                    self.violations.append(
                        (self.filename, node.lineno, f"Forbidden import: '{alias.name}'")
                    )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module:
            for forbidden in FORBIDDEN_PACKAGES:
                if node.module == forbidden or node.module.startswith(forbidden + "."):
                    self.violations.append(
                        (self.filename, node.lineno, f"Forbidden from-import: '{node.module}'")
                    )
        self.generic_visit(node)


def scan_directory_for_no_llm_violations(root_dir: str) -> List[Tuple[str, int, str]]:
    """Recursively scans Python files in root_dir for forbidden imports and endpoint strings."""
    violations: List[Tuple[str, int, str]] = []
    root_path = Path(root_dir)

    for py_file in root_path.rglob("*.py"):
        # Skip the policy file itself and virtual environments
        if py_file.name in {"no_llm_policy.py", "verify_no_llm.py"}:
            continue
        if any(part.startswith((".", "venv", "env")) for part in py_file.parts):
            continue

        try:
            content = py_file.read_text(encoding="utf-8")
        except Exception:
            continue

        # Check endpoints in string literals
        for endpoint in FORBIDDEN_ENDPOINT_PATTERNS:
            if endpoint in content:
                violations.append(
                    (str(py_file), 1, f"Forbidden LLM endpoint pattern detected: '{endpoint}'")
                )

        # AST inspection
        try:
            tree = ast.parse(content, filename=str(py_file))
            scanner = ImportScanner(str(py_file))
            scanner.visit(tree)
            violations.extend(scanner.violations)
        except Exception as e:
            violations.append((str(py_file), 1, f"AST parsing failure: {e}"))

    return violations


def validate_no_llm_policy(app_dir: str) -> None:
    """Raises RuntimeError if any LLM violation is detected in the application code."""
    violations = scan_directory_for_no_llm_violations(app_dir)
    if violations:
        report = "\n".join(f"- {f}:{line} -> {msg}" for f, line, msg in violations)
        raise RuntimeError(f"Strict No-LLM Policy Violations detected:\n{report}")
