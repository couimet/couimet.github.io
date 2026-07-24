#!/usr/bin/env python3
"""Generate the Rabbit Maximizer social banner (img/social-banner-rabbit-maximizer.jpg).

Downloads the Rabbit Maximizer icon from GitHub, composites it on the left
with title / tagline text on the right. Uses the same colour palette
and layout grid as the default banner.
"""

import sys
from io import BytesIO
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import urlopen

from PIL import Image

import settings as cfg
import utils as util

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PROJECT_FILE = REPO_ROOT / "projects" / "rabbit-maximizer.md"
OUT_PATH = REPO_ROOT / "img" / "social-banner-rabbit-maximizer.jpg"


def resolve_icon_url(meta):
    """Return the best-resolution icon URL from project front matter."""
    for key in ("sourceiconurl", "logourl", "iconurl"):
        url = meta.get(key)
        if url:
            return url
    print("No icon URL found in project front matter", file=sys.stderr)
    sys.exit(1)


def download_icon(url):
    """Download and decode an icon from *url*, returning a PIL Image."""
    if urlparse(url).scheme not in ("http", "https"):
        print(f"Refusing non-http(s) icon URL: {url}", file=sys.stderr)
        sys.exit(1)
    try:
        data = urlopen(url, timeout=10).read()
    except (URLError, OSError) as exc:
        print(f"Failed to download icon from {url}: {exc}", file=sys.stderr)
        sys.exit(1)
    return Image.open(BytesIO(data)).convert("RGBA")


def trim_to_content(icon):
    """Crop *icon* to the bounding box of fully opaque pixels."""
    alpha = icon.split()[3]
    bbox = alpha.getbbox()
    if bbox is None:
        return icon
    return icon.crop(bbox)


def main():
    meta = util.load_project_meta(PROJECT_FILE)
    icon = download_icon(resolve_icon_url(meta))
    icon = util.sized_icon(trim_to_content(icon), cfg.ICON_SIZE)
    util.compose_banner(meta, icon, OUT_PATH)


if __name__ == "__main__":
    main()
