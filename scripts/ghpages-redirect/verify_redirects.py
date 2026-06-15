"""Verify that every HTML file under a built site is a valid redirect stub.

Each page must carry both a `<meta http-equiv="refresh">` and a
`<link rel="canonical">` pointing at the matching path on
https://ouimet.info. The script walks the directory, derives the expected
URL from each file's path, and reports any mismatches.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path

CANONICAL_HOST = "https://ouimet.info"

# Tolerant of `0;url=...` with or without spaces around the semicolon/equals.
_REFRESH_CONTENT_RE = re.compile(
    r"^\s*0\s*;\s*url\s*=\s*(?P<url>\S+?)\s*$", re.IGNORECASE
)


@dataclass
class Failure:
    path: Path
    message: str


class _StubParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.refresh_url: str | None = None
        self.canonical_url: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "meta":
            attr_map = {k.lower(): (v or "") for k, v in attrs}
            if attr_map.get("http-equiv", "").lower() == "refresh":
                m = _REFRESH_CONTENT_RE.match(attr_map.get("content", ""))
                if m:
                    self.refresh_url = m.group("url")
        elif tag.lower() == "link":
            attr_map = {k.lower(): (v or "") for k, v in attrs}
            if attr_map.get("rel", "").lower() == "canonical":
                self.canonical_url = attr_map.get("href", "")


def expected_url_for(html_path: Path, site_dir: Path) -> str:
    rel = html_path.relative_to(site_dir)
    parts = rel.parts
    if parts[-1] == "index.html":
        if len(parts) == 1:
            path = "/"
        else:
            path = "/" + "/".join(parts[:-1]) + "/"
    else:
        path = "/" + "/".join(parts)
    return CANONICAL_HOST + path


def verify(site_dir: Path) -> list[Failure]:
    failures: list[Failure] = []
    html_files = sorted(site_dir.rglob("*.html"))
    if not html_files:
        failures.append(Failure(site_dir, "no HTML files found under site directory"))
        return failures

    for html_path in html_files:
        expected = expected_url_for(html_path, site_dir)
        parser = _StubParser()
        try:
            parser.feed(html_path.read_text(encoding="utf-8", errors="replace"))
        except Exception as exc:  # pragma: no cover - defensive
            failures.append(Failure(html_path, f"failed to parse: {exc}"))
            continue

        if parser.refresh_url is None:
            failures.append(
                Failure(html_path, "missing <meta http-equiv=\"refresh\"> tag")
            )
        elif parser.refresh_url != expected:
            failures.append(
                Failure(
                    html_path,
                    f"refresh url mismatch: expected {expected!r}, got {parser.refresh_url!r}",
                )
            )

        if parser.canonical_url is None:
            failures.append(
                Failure(html_path, "missing <link rel=\"canonical\"> tag")
            )
        elif parser.canonical_url != expected:
            failures.append(
                Failure(
                    html_path,
                    f"canonical url mismatch: expected {expected!r}, got {parser.canonical_url!r}",
                )
            )

    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "site_dir",
        nargs="?",
        default="_site",
        help="Path to the built site directory (default: _site)",
    )
    args = parser.parse_args(argv)

    site_dir = Path(args.site_dir)
    if not site_dir.is_dir():
        print(f"error: {site_dir} is not a directory", file=sys.stderr)
        return 1

    failures = verify(site_dir)
    if not failures:
        print(f"OK: all redirect stubs under {site_dir} are valid")
        return 0

    print(f"FAIL: {len(failures)} problem(s) found under {site_dir}:", file=sys.stderr)
    for f in failures:
        print(f"  {f.path}: {f.message}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
