"""Validate cross-item anchor uniqueness in a YAML data file."""

import sys
from pathlib import Path

import yaml


def find_duplicate_anchors(items):
    """Return anchors that appear more than once, sorted.

    JSON Schema has no keyword for cross-item uniqueness, so this is checked
    here: duplicate anchors would produce duplicate page ids, silently breaking
    the deep-link pulse for the second line.
    """
    seen = {}
    for item in items:
        anchor = item.get("anchor") if isinstance(item, dict) else None
        if anchor:
            seen[anchor] = seen.get(anchor, 0) + 1
    return sorted(anchor for anchor, count in seen.items() if count > 1)


def main():
    if len(sys.argv) != 2:
        print(
            "Usage: uv run python scripts/validate-anchors.py <data.yml>",
            file=sys.stderr,
        )
        sys.exit(1)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"ERROR: YAML file not found: {path}", file=sys.stderr)
        sys.exit(1)

    with open(path) as f:
        data = yaml.safe_load(f)

    duplicates = find_duplicate_anchors(data)
    if duplicates:
        print(
            f"ERROR: {path.name} — duplicate anchor(s) in {path.name}: {', '.join(duplicates)}",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"OK: {path} is valid")


if __name__ == "__main__":
    main()
