#!/usr/bin/env python3
"""Validate _data/promotions.yml against _data/promotions.schema.json."""

import json
import sys
from pathlib import Path

import jsonschema
from jsonschema import Draft202012Validator
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA = REPO_ROOT / "_data" / "promotions.schema.json"
FILE = REPO_ROOT / "_data" / "promotions.yml"


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

    print(f"OK: {FILE.relative_to(REPO_ROOT)} is valid")


if __name__ == "__main__":
    main()
