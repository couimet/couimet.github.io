"""Scaffold a new short-URL registry entry.

Usage: uv run python scripts/new-short-url.py [ID]

Without ID, a random base62 ID that does not collide with the registry is
generated (2 chars, falling back to 3 only if every 2-char ID is taken).
Inserts a placeholder entry into _data/short-urls.yml, keeping the file
sorted alphabetically (the validator enforces the order). The entry gets
placeholder redirect_to / title / description values for the author to fill
in; then run `make sync-short-urls` to generate the matching s/<ID>.md page
(the Makefile target chains it).

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

KEY_RE = re.compile(r"^([A-Za-z0-9]{2,3}):\s*$")

PLACEHOLDER = "TODO"


def is_base62_id(share_id):
    """True for a 2-3 char base62 ID (2 chars now; 3 is the superset)."""
    return 2 <= len(share_id) <= 3 and all(c in BASE62 for c in share_id)


def generate_share_id(registry, rng=None):
    """Return a random base62 ID not already in *registry*.

    Prefers a 2-char ID and only falls back to 3 chars when every 2-char ID
    is taken. Rejection-samples the ID space so it stays collision-free
    against the existing entries. *rng* is injectable for deterministic tests.
    """
    rng = rng or random
    taken = set(registry)
    for length in (2, 3):
        if len(taken) >= len(BASE62_CHARS) ** length:
            continue
        for _ in range(64):
            candidate = "".join(rng.choice(BASE62_CHARS) for _ in range(length))
            if candidate not in taken:
                return candidate
    raise ValueError("no free short IDs left")


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
    if len(sys.argv) > 2:
        print(f"usage: {sys.argv[0]} [ID]", file=sys.stderr)
        sys.exit(2)
    share_id = sys.argv[1] if len(sys.argv) == 2 else None

    if not REGISTRY_PATH.exists():
        print(f"ERROR: registry not found: {REGISTRY_PATH}", file=sys.stderr)
        sys.exit(1)
    with open(REGISTRY_PATH) as f:
        registry = yaml.safe_load(f) or {}

    if share_id is None:
        share_id = generate_share_id(registry)
        print(f"Generated share ID: {share_id!r}")
    elif not is_base62_id(share_id):
        print(f"ERROR: {share_id!r} is not a 2-3 char base62 ID", file=sys.stderr)
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
