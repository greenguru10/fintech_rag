#!/usr/bin/env python
"""Static verification script to enforce zero generative LLMs."""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.no_llm_policy import scan_directory_for_no_llm_violations


def main():
    root = Path(__file__).resolve().parent.parent
    app_dir = str(root / "app")
    scripts_dir = str(root / "scripts")

    print(f"Scanning '{app_dir}' and '{scripts_dir}' for No-LLM policy violations...")
    app_violations = scan_directory_for_no_llm_violations(app_dir)
    script_violations = scan_directory_for_no_llm_violations(scripts_dir)

    all_violations = app_violations + script_violations

    if all_violations:
        print("\n[FAILED] Strict No-LLM Policy Violations Found:")
        for file_path, line, msg in all_violations:
            print(f"  - {file_path}:{line} -> {msg}")
        sys.exit(1)
    else:
        print("\n[PASSED] No forbidden LLM packages, endpoints, or imports detected!")
        sys.exit(0)


if __name__ == "__main__":
    main()
