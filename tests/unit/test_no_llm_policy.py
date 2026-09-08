"""Unit tests for strict No-LLM architectural policy enforcement."""

import pytest
from app.core.no_llm_policy import scan_directory_for_no_llm_violations, FORBIDDEN_PACKAGES


def test_no_llm_violations_in_app(tmp_path):
    """Verifies that app directory has zero forbidden LLM packages or endpoints."""
    violations = scan_directory_for_no_llm_violations("app")
    assert len(violations) == 0, f"Found No-LLM violations in app: {violations}"


def test_scanner_catches_forbidden_import(tmp_path):
    """Verifies scanner catches forbidden import in dummy file."""
    bad_file = tmp_path / "bad_code.py"
    bad_file.write_text("import openai\nprint('hello')", encoding="utf-8")

    violations = scan_directory_for_no_llm_violations(str(tmp_path))
    assert len(violations) >= 1
    assert any("openai" in msg for _, _, msg in violations)


def test_scanner_catches_forbidden_endpoint(tmp_path):
    """Verifies scanner catches forbidden endpoint URL in string literal."""
    bad_file = tmp_path / "bad_endpoint.py"
    bad_file.write_text("URL = 'https://api.anthropic.com/v1/messages'\n", encoding="utf-8")

    violations = scan_directory_for_no_llm_violations(str(tmp_path))
    assert len(violations) >= 1
    assert any("api.anthropic.com" in msg for _, _, msg in violations)
