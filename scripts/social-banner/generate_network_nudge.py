#!/usr/bin/env python3
"""Generate the Network Nudge social banner (img/social-banner-network-nudge.jpg).

Reads the project icon from the local micro-projects assets directory,
composites it with banner text from the Jekyll front matter.
"""

import sys
from pathlib import Path

from PIL import Image

import settings as cfg
import utils as util

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PROJECT_FILE = REPO_ROOT / "projects" / "network-nudge.md"
OUT_PATH = REPO_ROOT / "img" / "social-banner-network-nudge.jpg"


def resolve_icon(meta):
    """Return a PIL Image loaded from the local icon path in front matter."""
    for key in ("sourceiconurl", "logourl", "iconurl"):
        url = meta.get(key)
        if url:
            path = REPO_ROOT / url.lstrip("/")
            if not path.exists():
                print(f"Icon not found: {path}", file=sys.stderr)
                sys.exit(1)
            return Image.open(path).convert("RGBA")
    print("No icon URL found in project front matter", file=sys.stderr)
    sys.exit(1)


def main():
    meta = util.load_project_meta(PROJECT_FILE)
    icon = util.sized_icon(resolve_icon(meta), cfg.ICON_SIZE)
    util.compose_banner(meta, icon, OUT_PATH)


if __name__ == "__main__":
    main()
