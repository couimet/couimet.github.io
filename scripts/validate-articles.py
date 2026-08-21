"""Validate _data/articles.yml against _data/articles.schema.json."""

import json
import sys
from pathlib import Path

import jsonschema
import yaml
from jsonschema import Draft202012Validator

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA = REPO_ROOT / "_data" / "articles.schema.json"
FILE = REPO_ROOT / "_data" / "articles.yml"


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
    for path, label in ((SCHEMA, "Schema"), (FILE, "YAML file")):
        if not path.exists():
            print(f"ERROR: {label} not found: {path}", file=sys.stderr)
            sys.exit(1)

    with open(SCHEMA) as f:
        schema = json.load(f)
    with open(FILE) as f:
        data = yaml.safe_load(f)

    try:
        jsonschema.validate(
            data, schema, format_checker=Draft202012Validator.FORMAT_CHECKER
        )
    except jsonschema.ValidationError as e:
        print(f"ERROR: {FILE.name} — {e.message}", file=sys.stderr)
        sys.exit(1)

    duplicates = find_duplicate_anchors(data)
    if duplicates:
        print(
            f"ERROR: duplicate anchor(s) in {FILE.name}: {', '.join(duplicates)}",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"OK: {FILE.relative_to(REPO_ROOT)} is valid")


if __name__ == "__main__":
    main()
