#!/usr/bin/env python3
"""Generate the Rabbit Maximizer social banner (img/social-banner-rabbit-maximizer.jpg).

Downloads the Rabbit Maximizer icon from GitHub, composites it on the left
with title / tagline text on the right. Uses the same colour palette
and layout grid as the default banner.
"""

from pathlib import Path

import settings as cfg
import utils as util

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PROJECT_FILE = REPO_ROOT / "projects" / "rabbit-maximizer.md"
OUT_PATH = REPO_ROOT / "img" / "social-banner-rabbit-maximizer.jpg"


def main():
    meta = util.load_project_meta(PROJECT_FILE)
    icon = util.download_icon(util.resolve_icon_url(meta))
    icon = util.sized_icon(util.trim_to_content(icon), cfg.ICON_SIZE)
    util.compose_banner(meta, icon, OUT_PATH)


if __name__ == "__main__":
    main()
