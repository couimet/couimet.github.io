"""Generate and validate s/<ID>.md share pages from the short-URL registry.

The registry (_data/short-urls.yml) is the single source of truth for the
/s/<ID> short URLs. The s/<ID>.md pages Jekyll builds are generated from it
(`make sync-short-urls`) and committed, so the share metadata (title,
description, redirect target, tagline) is written once, in the registry.

This script defaults to check mode: it verifies the registry is sorted
base62, that each entry is well-formed, and that the committed pages match
what generation would produce (catching a registry edit that was not
followed by `make sync-short-urls`). Pass --write to regenerate the pages.
"""

import re
import sys
from itertools import pairwise
from pathlib import Path

import yaml

BASE62 = set("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")

REPO_ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = REPO_ROOT / "_data" / "short-urls.yml"
SHARE_DIR = REPO_ROOT / "s"

GENERATED_HEADER = (
    "# Generated from _data/short-urls.yml. "
    "Do not edit directly. Regenerate with: make sync-short-urls"
)

# Hand-authored shareId="<ID>" and homeShareId="<ID>" attributes on heading
# anchors. The Liquid placeholders shareId="{{ shareId }}" /
# homeShareId="{{ include.homeShareId }}" and the JS reader
# getAttribute("shareId") do not match: neither has `= ` quoted alnum
# following the attribute name. The capital S in homeShareId keeps it
# distinct from the shareId pattern (regexes are case-sensitive).
SHARE_ID_RE = re.compile(r'shareId\s*=\s*["\']([A-Za-z0-9]+)["\']')
HOME_SHARE_ID_RE = re.compile(r'homeShareId\s*=\s*["\']([A-Za-z0-9]+)["\']')
SHARE_ID_PATTERNS = (SHARE_ID_RE, HOME_SHARE_ID_RE)

TEMPLATE_DIRS = ("_includes", "_layouts")


def is_base62_id(share_id):
    """True for an exactly-2-char base62 ID."""
    return len(share_id) == 2 and all(c in BASE62 for c in share_id)


def find_unsorted_ids(registry):
    """Return IDs that break the alphabetical sort, in registry order.

    An ID is out of order when it is smaller than its predecessor, so the
    first offender (not every displaced element) is reported.
    """
    ids = list(registry)
    return [id_ for prev, id_ in pairwise(ids) if id_ < prev]


def find_invalid_ids(registry):
    """Return IDs that are not exactly-2-char base62 values, in registry order."""
    return [id_ for id_ in registry if not is_base62_id(id_)]


def find_same_as_errors(registry):
    """Return errors for malformed same_as (alias) entries.

    An alias must point at an existing regular entry: the target may not
    itself be an alias (no chains), and the alias may not override
    bannertagline because it is baked into the shared banner (Q001/Q002).
    """
    errors = []
    for share_id, entry in registry.items():
        if "same_as" not in entry:
            continue
        target_id = entry["same_as"]
        if target_id not in registry:
            errors.append(
                f"entry {share_id!r}: same_as target {target_id!r} does not exist"
            )
            continue
        if "same_as" in registry[target_id]:
            errors.append(
                f"entry {share_id!r}: same_as target {target_id!r} is itself an alias"
                " (chains are not allowed)"
            )
        if "bannertagline" in entry:
            errors.append(
                f"entry {share_id!r}: same_as entries cannot override bannertagline"
                " (the shared banner bakes in the target's tagline)"
            )
    return errors


def resolve_registry(registry):
    """Apply same_as inheritance.

    Returns (resolved, banner_ids): resolved maps each ID to its effective
    entry (redirect_to, title, description, bannertagline all final) and
    banner_ids maps each ID to the entry whose /img/social/<ID>.jpg the share
    page uses. For an alias the banner owner is the same_as target, so aliases
    never get their own banner.
    """
    resolved = {}
    banner_ids = {}
    for share_id, entry in registry.items():
        if "same_as" not in entry:
            resolved[share_id] = entry
            banner_ids[share_id] = share_id
            continue
        target = registry[entry["same_as"]]
        merged = dict(target)
        merged["redirect_to"] = entry["redirect_to"]
        for key in ("title", "description"):
            if key in entry:
                merged[key] = entry[key]
        resolved[share_id] = merged
        banner_ids[share_id] = entry["same_as"]
    return resolved, banner_ids


def render_page(share_id, entry, banner_id=None):
    """Render the s/<ID>.md content the registry entry should produce.

    banner_id is the ID whose banner the page uses. It defaults to share_id
    and only differs for same_as aliases, which reuse the target's banner.
    """
    front = {
        "layout": "share",
        "redirect_to": entry["redirect_to"],
        "title": entry["title"],
        "description": entry["description"],
        "og_image": f"/img/social/{(banner_id or share_id)}.jpg",
        "bannertagline": entry.get("bannertagline") or entry["title"],
        "sitemap": False,
    }
    dumped = yaml.safe_dump(front, sort_keys=False, allow_unicode=True, width=1000)
    return f"---\n{GENERATED_HEADER}\n{dumped}---\n"


def find_stale_pages(registry, share_dir):
    """Return [(share_id, path)] for pages that differ from generation."""
    resolved, banner_ids = resolve_registry(registry)
    stale = []
    for share_id in registry:
        path = share_dir / f"{share_id}.md"
        if not path.exists() or path.read_text() != render_page(
            share_id, resolved[share_id], banner_ids[share_id]
        ):
            stale.append((share_id, path))
    return stale


def find_orphan_pages(registry, share_dir):
    """Return [(share_id, path)] for generated pages with no registry entry.

    Only files carrying the generated header are candidates, so a hand-authored
    s/*.md page is never reported or removed.
    """
    orphans = []
    for path in sorted(share_dir.glob("*.md")):
        share_id = path.stem
        if share_id in registry:
            continue
        if GENERATED_HEADER in path.read_text():
            orphans.append((share_id, path))
    return orphans


def find_shape_errors(registry):
    """Return errors for entries with a malformed shape or missing fields.

    Mirrors the _data/short-urls.schema.json contract: every entry is a
    mapping, all entries require a redirect_to, and regular entries (no
    same_as) additionally require non-empty title and description. Validating
    here keeps check mode and --write from crashing with KeyError later in
    resolve_registry/render_page.
    """
    errors = []
    for share_id, entry in registry.items():
        if not isinstance(entry, dict):
            errors.append(
                f"entry {share_id!r} is not a mapping (got {type(entry).__name__})"
            )
            continue
        redirect_to = entry.get("redirect_to")
        if not isinstance(redirect_to, str) or not redirect_to.strip():
            errors.append(f"entry {share_id!r}: redirect_to must be a non-empty string")
        if "same_as" in entry:
            continue
        for field in ("title", "description"):
            value = entry.get(field)
            if not isinstance(value, str) or not value.strip():
                errors.append(
                    f"entry {share_id!r}: {field} must be a non-empty string "
                    "on regular entries"
                )
    return errors


def registry_errors(registry):
    """Return errors that invalidate the registry (shape, sorted, base62, aliases)."""
    errors = []
    errors.extend(find_shape_errors(registry))
    for id_ in find_unsorted_ids(registry):
        errors.append(f"registry is not sorted alphabetically at ID {id_!r}")
    for id_ in find_invalid_ids(registry):
        errors.append(f"ID {id_!r} is not a 2-char base62 value")
    errors.extend(find_same_as_errors(registry))
    return errors


def check_registry(registry, share_dir):
    """Return registry-invariant errors plus stale and orphan share-page errors."""
    stale = [
        f"s/{share_id}.md is out of date (run `make sync-short-urls`)"
        for share_id, _ in find_stale_pages(registry, share_dir)
    ]
    orphans = [
        f"s/{share_id}.md is orphaned (no registry entry; "
        "run `make sync-short-urls` to remove it)"
        for share_id, _ in find_orphan_pages(registry, share_dir)
    ]
    return registry_errors(registry) + stale + orphans


def find_unknown_shortened_ids(registry, root):
    """Return [(path, line_no, share_id)] for shareId uses not in the registry.

    Templates hand-author shareId="<ID>" and homeShareId="<ID>" on
    heading anchors; copy-link.js turns the emitted attribute into the
    /s/<ID> URL, so every referenced ID must exist in the registry or the
    generated URL 404s.
    """
    unknown = []
    for dirname in TEMPLATE_DIRS:
        for path in sorted((root / dirname).rglob("*.html")):
            for lineno, line in enumerate(path.read_text().splitlines(), 1):
                for pattern in SHARE_ID_PATTERNS:
                    for match in pattern.finditer(line):
                        share_id = match.group(1)
                        if share_id not in registry:
                            unknown.append((path, lineno, share_id))
    return unknown


def write_pages(registry, share_dir):
    """Regenerate all share pages, writing only changed files."""
    resolved, banner_ids = resolve_registry(registry)
    written = []
    for share_id in registry:
        path = share_dir / f"{share_id}.md"
        expected = render_page(share_id, resolved[share_id], banner_ids[share_id])
        if not path.exists() or path.read_text() != expected:
            path.write_text(expected)
            written.append(str(path))
    return written


def main():
    write = "--write" in sys.argv
    if not REGISTRY_PATH.exists():
        print(f"ERROR: registry not found: {REGISTRY_PATH}", file=sys.stderr)
        sys.exit(1)
    with open(REGISTRY_PATH) as f:
        registry = yaml.safe_load(f) or {}
    if not isinstance(registry, dict):
        print(
            f"ERROR: {REGISTRY_PATH.name} must be a mapping of ID to entry",
            file=sys.stderr,
        )
        sys.exit(1)

    # Registry-invariant errors gate both modes; stale pages are what
    # --write repairs, so they are only checked in check mode.
    errors = registry_errors(registry)
    if errors:
        print(f"ERROR: {REGISTRY_PATH.name}", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        sys.exit(1)

    if write:
        written = write_pages(registry, SHARE_DIR)
        for path in written:
            print(f"Generated: {path}")
        orphans = find_orphan_pages(registry, SHARE_DIR)
        for _, path in orphans:
            path.unlink()
            print(f"Removed orphan: {path}")
        if not written and not orphans:
            print("All share pages are current")
        return

    stale = check_registry(registry, SHARE_DIR)
    unknown = [
        f"{path}:{lineno}: shareId {share_id!r} is not in {REGISTRY_PATH.name}"
        for path, lineno, share_id in find_unknown_shortened_ids(registry, REPO_ROOT)
    ]
    errors = stale + unknown
    if errors:
        print(f"ERROR: {REGISTRY_PATH.name}", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        sys.exit(1)
    print(f"OK: {REGISTRY_PATH.name} is valid and share pages are current")


if __name__ == "__main__":
    main()
