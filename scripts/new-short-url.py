"""Scaffold a new short-URL registry entry.

Usage: uv run python scripts/new-short-url.py [--generate-only] [ID]

With --generate-only (no positional ID), prints a random 2-char base62 ID
that does not collide with the registry and returns without writing anything;
use it to draw an ID to hand-write into _data/short-urls.yml.

Without a flag, a random 2-char base62 ID that does not collide with the
registry is generated. Inserts a placeholder entry into _data/short-urls.yml,
keeping the file sorted alphabetically (the validator enforces the order). The
entry gets placeholder redirect_to / title / description values for the author
to fill in; then run `make sync-short-urls` to generate the matching
s/<ID>.md page (the Makefile target chains it).

bannertagline is scaffolded as a commented-out placeholder: the banner
falls back to the title, but the reminder line shows where a custom tagline
goes if the image should diverge from the card title.
"""

import random
import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = REPO_ROOT / "_data" / "short-urls.yml"

BASE62_CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
BASE62 = set(BASE62_CHARS)

KEY_RE = re.compile(r"^([A-Za-z0-9]{2}):\s*$")

PLACEHOLDER = "TODO"

# YAML 1.1 boolean scalars that PyYAML loads as bool keys. These are the only
# 2-char values affected (y/n are 1 char, true/false too long), so they are
# the complete set of IDs that cannot round-trip through _data/short-urls.yml.
RESERVED_IDS = {"on", "no", "yes", "off"}


def is_base62_id(share_id):
    """True for an exactly-2-char base62 ID."""
    return len(share_id) == 2 and all(c in BASE62 for c in share_id)


def is_reserved_id(share_id):
    """True for a YAML-reserved boolean word (any case).

    PyYAML 6 converts unquoted on/no/yes/off keys to boolean mapping keys, so
    generating or inserting one of these IDs would either collide with an
    entry the registry load turned into a bool, or insert a line that reloads
    as a bool key.
    """
    return share_id.lower() in RESERVED_IDS


def generate_share_id(registry, rng=None):
    """Return a random 2-char base62 ID not already in *registry*.

    Rejection-samples the 2-char ID space so it stays collision-free against
    the existing entries. If 64 random draws all collide (a near-full
    registry), falls back to a deterministic scan of the finite space so the
    ValueError below fires only when every ID is genuinely taken. *rng* is
    injectable for deterministic tests.
    """
    rng = rng or random
    taken = set(registry)
    for _ in range(64):
        candidate = "".join(rng.choice(BASE62_CHARS) for _ in range(2))
        if candidate not in taken and not is_reserved_id(candidate):
            return candidate
    for first in BASE62_CHARS:
        for second in BASE62_CHARS:
            candidate = first + second
            if candidate not in taken and not is_reserved_id(candidate):
                return candidate
    raise ValueError("no free 2-char short IDs left")


def insert_entry(text, share_id):
    """Return registry text with a placeholder entry inserted at the sorted spot.

    The block goes before the first existing entry whose key sorts after
    share_id, or at the end. The registry stays sorted so validate-short-urls
    passes. Raises ValueError when share_id is already present.
    """
    for line in text.splitlines():
        match = KEY_RE.match(line)
        if match and match.group(1) == share_id:
            raise ValueError(f"{share_id!r} already exists in the registry")
    lines = text.splitlines(keepends=True)
    block = (
        f"{share_id}:\n"
        f"  redirect_to: /{PLACEHOLDER}\n"
        f"  title: {PLACEHOLDER}\n"
        f"  description: {PLACEHOLDER}\n"
        f"  # bannertagline: {PLACEHOLDER} (optional; defaults to title)\n"
    )
    for index, line in enumerate(lines):
        match = KEY_RE.match(line)
        if match and match.group(1) > share_id:
            lines.insert(index, block)
            return "".join(lines)
    if lines and not lines[-1].endswith("\n"):
        lines[-1] += "\n"
    lines.append(block)
    return "".join(lines)


def main():
    args = sys.argv[1:]
    generate_only = "--generate-only" in args
    ids = [arg for arg in args if arg != "--generate-only"]
    if len(ids) > 1 or (generate_only and ids):
        print(f"usage: {sys.argv[0]} [--generate-only] [ID]", file=sys.stderr)
        sys.exit(2)
    share_id = ids[0] if ids else None

    if not REGISTRY_PATH.exists():
        print(f"ERROR: registry not found: {REGISTRY_PATH}", file=sys.stderr)
        sys.exit(1)
    with open(REGISTRY_PATH) as f:
        registry = yaml.safe_load(f) or {}

    if generate_only:
        print(generate_share_id(registry))
        return

    if share_id is None:
        share_id = generate_share_id(registry)
        print(f"Generated share ID: {share_id!r}")
    elif not is_base62_id(share_id):
        print(f"ERROR: {share_id!r} is not a 2-char base62 ID", file=sys.stderr)
        sys.exit(1)
    elif is_reserved_id(share_id):
        print(
            f"ERROR: {share_id!r} is a YAML-reserved boolean word "
            "(PyYAML would load it as a boolean key)",
            file=sys.stderr,
        )
        sys.exit(1)
    elif share_id in registry:
        print(
            f"ERROR: {share_id!r} already exists in {REGISTRY_PATH.name}",
            file=sys.stderr,
        )
        sys.exit(1)

    REGISTRY_PATH.write_text(insert_entry(REGISTRY_PATH.read_text(), share_id))
    print(f"Added placeholder entry for {share_id!r} to {REGISTRY_PATH}")
    print(
        "Fill in redirect_to, title and description; bannertagline is "
        "optional (commented out, defaults to title). "
        "Then run `make sync-short-urls`."
    )


if __name__ == "__main__":
    main()
