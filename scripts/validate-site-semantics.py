"""Validate a built _site/ directory against deployment-target expectations.

Two Jekyll deployments build this repo:

- ouimet.info: the canonical site. robots.txt must allow crawling and
  sitemap.xml must reference https://ouimet.info URLs.
- github.io: a redirect shell. robots.txt must block crawlers, sitemap.xml is
  removed from the build, and every page must be a redirect stub.

Usage:
    uv run python scripts/validate-site-semantics.py --target ouimet.info
    uv run python scripts/validate-site-semantics.py --target github.io --site-dir _site
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

TARGET_OUIMET = "ouimet.info"
TARGET_GH_PAGES = "github.io"

CANONICAL_HOST = "https://ouimet.info"

# Pages both deployments must produce. sitemap.xml is handled separately:
# required for ouimet.info, forbidden for github.io.
EXPECTED_PAGES = [
    "404.html",
    "index.html",
    "resume.html",
    "robots.txt",
    "projects/network-nudge.html",
    "projects/rabbit-maximizer.html",
    "projects/rangelink-extension.html",
    "articles/index.html",
    "projects/index.html",
]

# Patterns that must never appear in rendered HTML.
DEV_PATTERNS = ("localhost", "127.0.0.1", "http://")
LIQUID_PATTERNS = ("{{", "{%")


ROBOTS_DISALLOW = "Disallow: /"


def _has_canonical_origin(url: str) -> bool:
    """Return True if *url* has scheme+netloc matching CANONICAL_HOST."""
    parsed = urlparse(url.strip())
    return f"{parsed.scheme}://{parsed.netloc}" == CANONICAL_HOST


class _PageParser(HTMLParser):
    """Extract the title, canonical URL, and og:description from one page."""

    def __init__(self) -> None:
        super().__init__()
        self.title: str | None = None
        self.canonical: str | None = None
        self.og_description: str | None = None
        self.has_redirect_refresh: bool = False
        self._in_title = False
        self._title_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {k.lower(): (v or "") for k, v in attrs}
        if tag.lower() == "title":
            self._in_title = True
            self._title_parts = []
        elif tag.lower() == "link" and attr_map.get("rel", "").lower() == "canonical":
            self.canonical = attr_map.get("href") or None
        elif (
            tag.lower() == "meta"
            and attr_map.get("property", "").lower() == "og:description"
        ):
            self.og_description = attr_map.get("content") or None
        elif (
            tag.lower() == "meta"
            and attr_map.get("http-equiv", "").lower() == "refresh"
            and attr_map.get("content", "").strip()
        ):
            self.has_redirect_refresh = True

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self._title_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self._in_title = False
            self.title = "".join(self._title_parts).strip() or None


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def parse_page(path: Path) -> _PageParser:
    parser = _PageParser()
    parser.feed(read_text(path))
    return parser


def check_html_patterns(site_dir: Path, failures: list[str]) -> None:
    """Flag dev/localhost URLs and unrendered Liquid in every HTML file."""
    for html_path in sorted(site_dir.rglob("*.html")):
        rel = html_path.relative_to(site_dir)
        content = read_text(html_path)
        for pattern in DEV_PATTERNS:
            if pattern in content:
                failures.append(f"{rel}: contains {pattern!r} (dev/localhost URL)")
        for pattern in LIQUID_PATTERNS:
            if pattern in content:
                failures.append(f"{rel}: contains unrendered Liquid {pattern!r}")


def check_expected_pages(site_dir: Path, target: str, failures: list[str]) -> None:
    for rel in EXPECTED_PAGES:
        if not (site_dir / rel).exists():
            failures.append(f"missing expected page: {rel}")
    sitemap = site_dir / "sitemap.xml"
    if target == TARGET_OUIMET:
        if not sitemap.exists():
            failures.append("missing expected page: sitemap.xml")
    elif sitemap.exists():
        failures.append(
            "sitemap.xml must not exist in the github.io build "
            "(crawlers are blocked by robots.txt)"
        )


def check_duplicate_meta(site_dir: Path, failures: list[str]) -> None:
    """Flag titles, canonical URLs, and og:descriptions shared across pages.

    Redirect stubs are exempt: they are noindex, sitemap-excluded, and bounce
    visitors immediately, so duplicate meta on them has no SEO effect. The
    /s/<ID> share pages rely on this — a same_as alias intentionally reuses its
    target entry's title, description, and banner while redirecting elsewhere.
    """
    titles: dict[str, list[str]] = defaultdict(list)
    canonicals: dict[str, list[str]] = defaultdict(list)
    descriptions: dict[str, list[str]] = defaultdict(list)
    for html_path in sorted(site_dir.rglob("*.html")):
        rel = str(html_path.relative_to(site_dir))
        page = parse_page(html_path)
        if page.has_redirect_refresh:
            continue
        if page.title:
            titles[page.title].append(rel)
        if page.canonical:
            canonicals[page.canonical].append(rel)
        if page.og_description:
            descriptions[page.og_description].append(rel)

    for label, groups in (
        ("title", titles),
        ("canonical URL", canonicals),
        ("og:description", descriptions),
    ):
        for value, pages in groups.items():
            if len(pages) > 1:
                failures.append(
                    f"duplicate {label} {value!r} on pages: {', '.join(pages)}"
                )


def check_target_specific(site_dir: Path, target: str, failures: list[str]) -> None:
    robots_path = site_dir / "robots.txt"
    if robots_path.is_file():
        robots = read_text(robots_path)
        if target == TARGET_OUIMET:
            if ROBOTS_DISALLOW in robots:
                failures.append(
                    "robots.txt must not disallow crawlers for ouimet.info "
                    f"(found {ROBOTS_DISALLOW!r})"
                )
        elif ROBOTS_DISALLOW not in robots:
            failures.append(
                "robots.txt must contain 'Disallow: /' for the github.io redirect shell"
            )

    if target == TARGET_OUIMET:
        sitemap = site_dir / "sitemap.xml"
        if sitemap.is_file():
            for loc in re.findall(r"<loc>(.*?)</loc>", read_text(sitemap)):
                loc = loc.strip()
                if not _has_canonical_origin(loc):
                    failures.append(
                        f"sitemap.xml URL {loc!r} does not have origin {CANONICAL_HOST}"
                    )
        for html_path in sorted(site_dir.rglob("*.html")):
            page = parse_page(html_path)
            if page.canonical and not _has_canonical_origin(page.canonical):
                rel = html_path.relative_to(site_dir)
                failures.append(
                    f"{rel}: canonical URL {page.canonical!r} does not have origin "
                    f"{CANONICAL_HOST}"
                )
    else:
        for html_path in sorted(site_dir.rglob("*.html")):
            if not parse_page(html_path).has_redirect_refresh:
                rel = html_path.relative_to(site_dir)
                failures.append(
                    f'{rel}: missing redirect stub (no <meta http-equiv="refresh"> element)'
                )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--target",
        required=True,
        choices=(TARGET_OUIMET, TARGET_GH_PAGES),
        help="Deployment target to validate against",
    )
    parser.add_argument(
        "--site-dir",
        default="_site",
        help="Path to the built site directory (default: _site)",
    )
    args = parser.parse_args(argv)

    site_dir = Path(args.site_dir)
    if not site_dir.is_dir():
        print(f"error: {site_dir} is not a directory", file=sys.stderr)
        return 1

    failures: list[str] = []
    check_html_patterns(site_dir, failures)
    check_expected_pages(site_dir, args.target, failures)
    check_duplicate_meta(site_dir, failures)
    check_target_specific(site_dir, args.target, failures)

    if not failures:
        print(f"OK: {site_dir} ({args.target}) passes all checks")
        return 0

    print(
        f"FAIL: {len(failures)} problem(s) found under {site_dir} ({args.target}):",
        file=sys.stderr,
    )
    for message in failures:
        print(f"  {message}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
