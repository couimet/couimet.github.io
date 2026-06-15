"""Tests for verify_redirects.py."""

from __future__ import annotations

from pathlib import Path

import pytest

from verify_redirects import CANONICAL_HOST, expected_url_for, verify


def _stub(url: str) -> str:
    return (
        "<!doctype html><html><head>"
        f'<meta http-equiv="refresh" content="0; url={url}">'
        f'<link rel="canonical" href="{url}">'
        "</head><body></body></html>"
    )


def _write(site: Path, rel_path: str, content: str) -> Path:
    p = site / rel_path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return p


def test_happy_path(tmp_path: Path) -> None:
    site = tmp_path / "_site"
    site.mkdir()
    _write(site, "index.html", _stub(f"{CANONICAL_HOST}/"))
    _write(site, "resume.html", _stub(f"{CANONICAL_HOST}/resume.html"))
    _write(site, "projects/index.html", _stub(f"{CANONICAL_HOST}/projects/"))

    failures = verify(site)
    assert failures == [], f"unexpected failures: {failures}"


def test_missing_meta_refresh(tmp_path: Path) -> None:
    site = tmp_path / "_site"
    site.mkdir()
    _write(site, "index.html", _stub(f"{CANONICAL_HOST}/"))
    bad = _write(
        site,
        "resume.html",
        (
            "<!doctype html><html><head>"
            f'<link rel="canonical" href="{CANONICAL_HOST}/resume.html">'
            "</head><body></body></html>"
        ),
    )

    failures = verify(site)
    assert any(f.path == bad and "refresh" in f.message for f in failures), failures


def test_wrong_host(tmp_path: Path) -> None:
    site = tmp_path / "_site"
    site.mkdir()
    bad = _write(site, "index.html", _stub("https://wrong.example.com/"))

    failures = verify(site)
    assert any(f.path == bad and "mismatch" in f.message for f in failures), failures
    assert any("wrong.example.com" in f.message for f in failures), failures


def test_wrong_path(tmp_path: Path) -> None:
    site = tmp_path / "_site"
    site.mkdir()
    bad = _write(site, "foo/index.html", _stub(f"{CANONICAL_HOST}/bar/"))

    failures = verify(site)
    messages = [f.message for f in failures if f.path == bad]
    # Both refresh and canonical should flag the mismatch and mention expected + actual.
    assert messages, f"no failures for {bad}: {failures}"
    assert any("/foo/" in m and "/bar/" in m for m in messages), messages


def test_path_mapping(tmp_path: Path) -> None:
    site = tmp_path / "_site"
    site.mkdir()
    root_index = _write(site, "index.html", "")
    nested_index = _write(site, "foo/index.html", "")
    flat = _write(site, "foo.html", "")

    assert expected_url_for(root_index, site) == f"{CANONICAL_HOST}/"
    assert expected_url_for(nested_index, site) == f"{CANONICAL_HOST}/foo/"
    assert expected_url_for(flat, site) == f"{CANONICAL_HOST}/foo.html"


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
    url = f"{CANONICAL_HOST}/"
    _write(
        site,
        "index.html",
        (
            "<!doctype html><html><head>"
            f'<meta http-equiv="refresh" content="0;url={url}">'
            f'<link rel="canonical" href="{url}">'
            "</head><body></body></html>"
        ),
    )
    failures = verify(site)
    assert failures == [], f"unexpected failures: {failures}"


def test_case_insensitive_http_equiv(tmp_path: Path) -> None:
    site = tmp_path / "_site"
    site.mkdir()
    url = f"{CANONICAL_HOST}/"
    _write(
        site,
        "index.html",
        (
            "<!doctype html><html><head>"
            f'<meta HTTP-EQUIV="REFRESH" content="0; url={url}">'
            f'<link rel="canonical" href="{url}">'
            "</head><body></body></html>"
        ),
    )
    failures = verify(site)
    assert failures == [], f"unexpected failures: {failures}"
