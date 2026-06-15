"""Tests for verify_redirects.py."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from verify_redirects import CANONICAL_HOST, expected_url_for, verify


FIXTURES = Path(__file__).parent / "fixtures"


def _write(site: Path, rel_path: str, content: str) -> Path:
    p = site / rel_path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return p


def test_happy_path() -> None:
    failures = verify(FIXTURES)
    assert failures == [], f"unexpected failures: {failures}"


def test_missing_meta_refresh(tmp_path: Path) -> None:
    site = tmp_path / "_site"
    site.mkdir()
    content = (FIXTURES / "resume.html").read_text(encoding="utf-8")
    content = re.sub(r'<meta http-equiv="refresh"[^>]*>', "", content)
    bad = _write(site, "resume.html", content)

    failures = verify(site)
    assert any(f.path == bad and "refresh" in f.message for f in failures), failures


def test_missing_noscript_link(tmp_path: Path) -> None:
    site = tmp_path / "_site"
    site.mkdir()
    content = (FIXTURES / "resume.html").read_text(encoding="utf-8")
    content = re.sub(r"<noscript>.*?</noscript>", "", content, flags=re.DOTALL)
    bad = _write(site, "resume.html", content)

    failures = verify(site)
    assert any(f.path == bad and "noscript" in f.message for f in failures), failures


def test_wrong_noscript_url(tmp_path: Path) -> None:
    site = tmp_path / "_site"
    site.mkdir()
    wrong_url = f"{CANONICAL_HOST}/wrong.html"
    content = (FIXTURES / "resume.html").read_text(encoding="utf-8")
    content = re.sub(
        r"(<noscript>.*?<a\s+)href=\"[^\"]*\"",
        rf'\1href="{wrong_url}"',
        content,
        flags=re.DOTALL,
    )
    bad = _write(site, "resume.html", content)

    failures = verify(site)
    assert any(f.path == bad and "noscript" in f.message for f in failures), failures


def test_wrong_host(tmp_path: Path) -> None:
    site = tmp_path / "_site"
    site.mkdir()
    content = (FIXTURES / "index.html").read_text(encoding="utf-8")
    content = content.replace(CANONICAL_HOST, "https://wrong.example.com")
    bad = _write(site, "index.html", content)

    failures = verify(site)
    assert any(f.path == bad and "mismatch" in f.message for f in failures), failures
    assert any("wrong.example.com" in f.message for f in failures), failures


def test_wrong_path(tmp_path: Path) -> None:
    site = tmp_path / "_site"
    site.mkdir()
    content = (FIXTURES / "projects/index.html").read_text(encoding="utf-8")
    content = content.replace(f"{CANONICAL_HOST}/projects/", f"{CANONICAL_HOST}/bar/")
    bad = _write(site, "projects/index.html", content)

    failures = verify(site)
    messages = [f.message for f in failures if f.path == bad]
    assert messages, f"no failures for {bad}: {failures}"
    assert any("/projects/" in m and "/bar/" in m for m in messages), messages


def test_path_mapping() -> None:
    assert expected_url_for(FIXTURES / "index.html", FIXTURES) == f"{CANONICAL_HOST}/"
    assert (
        expected_url_for(FIXTURES / "resume.html", FIXTURES)
        == f"{CANONICAL_HOST}/resume.html"
    )
    assert (
        expected_url_for(FIXTURES / "projects/index.html", FIXTURES)
        == f"{CANONICAL_HOST}/projects/"
    )
    assert (
        expected_url_for(FIXTURES / "projects/rangelink-extension.html", FIXTURES)
        == f"{CANONICAL_HOST}/projects/rangelink-extension.html"
    )


def test_deeply_nested_path_mapping(tmp_path: Path) -> None:
    site = tmp_path / "_site"
    site.mkdir()
    deep_index = _write(site, "foo/bar/index.html", "")
    deep_flat = _write(site, "foo/bar.html", "")

    assert expected_url_for(deep_index, site) == f"{CANONICAL_HOST}/foo/bar/"
    assert expected_url_for(deep_flat, site) == f"{CANONICAL_HOST}/foo/bar.html"


def test_empty_site_dir(tmp_path: Path) -> None:
    site = tmp_path / "_site"
    site.mkdir()
    failures = verify(site)
    assert failures, "expected failure for empty site directory"
    assert any("no HTML files" in f.message for f in failures), failures


def test_content_without_space_after_semicolon(tmp_path: Path) -> None:
    """`content="0;url=..."` (no space) should still be accepted."""
    site = tmp_path / "_site"
    site.mkdir()
    content = (FIXTURES / "index.html").read_text(encoding="utf-8")
    content = content.replace('content="0; url=', 'content="0;url=')
    _write(site, "index.html", content)

    failures = verify(site)
    assert failures == [], f"unexpected failures: {failures}"


def test_case_insensitive_http_equiv(tmp_path: Path) -> None:
    site = tmp_path / "_site"
    site.mkdir()
    content = (FIXTURES / "index.html").read_text(encoding="utf-8")
    content = content.replace('http-equiv="refresh"', 'HTTP-EQUIV="REFRESH"')
    _write(site, "index.html", content)

    failures = verify(site)
    assert failures == [], f"unexpected failures: {failures}"
