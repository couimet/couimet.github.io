#!/usr/bin/env python3
"""Generate the RangeLink social banner (img/social-banner-rangelink.jpg).

Downloads the RangeLink icon from GitHub, composites it on the left
with title / tagline text on the right. Uses the same colour palette
and layout grid as the default banner via _banner_settings.
"""

import re
import sys
from io import BytesIO
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import urlopen

import yaml
from PIL import Image, ImageDraw

import settings as cfg
import utils as util

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PROJECT_FILE = REPO_ROOT / "projects" / "rangelink-extension.md"
OUT_PATH = REPO_ROOT / "img" / "social-banner-rangelink.jpg"

TEXT_MAX_W = cfg.WIDTH - cfg.TEXT_REGION_X - cfg.PADDING_H


def load_project_meta(project_md_path):
    """Parse Jekyll front matter from the project markdown file."""
    with open(project_md_path) as f:
        content = f.read()
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        print(f"No front matter found in {project_md_path}", file=sys.stderr)
        sys.exit(1)
    return yaml.safe_load(match.group(1))


def resolve_icon_url(meta):
    """Return the best-resolution icon URL from project front matter."""
    for key in ("sourceiconurl", "logourl", "iconurl"):
        url = meta.get(key)
        if url:
            return url
    print("No icon URL found in project front matter", file=sys.stderr)
    sys.exit(1)


def load_icon_bytes(url):
    if urlparse(url).scheme not in ("http", "https"):
        print(f"Refusing non-http(s) icon URL: {url}", file=sys.stderr)
        sys.exit(1)
    try:
        return urlopen(url, timeout=10).read()
    except (URLError, OSError) as exc:
        print(f"Failed to download icon from {url}: {exc}", file=sys.stderr)
        sys.exit(1)


def decode_icon(data):
    return Image.open(BytesIO(data)).convert("RGBA")


def trim_to_content(icon):
    """Crop *icon* to the bounding box of fully opaque pixels."""
    alpha = icon.split()[3]
    bbox = alpha.getbbox()
    if bbox is None:
        return icon
    return icon.crop(bbox)


def sized_icon(icon, target_size):
    """Scale *icon* so its larger dimension equals *target_size*, preserving aspect ratio."""
    icon = trim_to_content(icon)
    scale = target_size / max(icon.size)
    new_w = int(icon.width * scale)
    new_h = int(icon.height * scale)
    return icon.resize((new_w, new_h), Image.Resampling.LANCZOS)


def build_banner(project_md_path, out_path, icon_loader=load_icon_bytes):
    meta = load_project_meta(project_md_path)
    icon_url = resolve_icon_url(meta)
    icon = decode_icon(icon_loader(icon_url))
    icon = sized_icon(icon, cfg.ICON_SIZE)

    bannertitle = util.derive_bannertitle(meta)
    bannersubtitle = meta.get("bannersubtitle", "")
    bannertagline = meta.get("bannertagline") or meta.get("summary", "")

    im = Image.new("RGB", (cfg.WIDTH, cfg.HEIGHT), cfg.BG_COLOR)
    draw = ImageDraw.Draw(im)

    # Icon — centre in left region
    icon_x = cfg.PADDING_H + (cfg.LEFT_REGION_WIDTH - icon.width) // 2
    icon_y = (cfg.HEIGHT - icon.height) // 2
    if icon.mode == "RGBA":
        im.paste(icon, (icon_x, icon_y), icon.split()[3])
    else:
        im.paste(icon, (icon_x, icon_y))

    # Build line list
    name_font = util.load_font(cfg.NAME_FONT_SIZE, cfg.NAME_FONT_WEIGHT)
    title_font = util.load_font(cfg.TITLE_FONT_SIZE, cfg.TITLE_FONT_WEIGHT)
    tagline_font = util.load_font(cfg.TAGLINE_FONT_SIZE, cfg.TAGLINE_FONT_WEIGHT)

    lines = [
        (bannertitle, name_font, cfg.NAME_COLOR),
    ]
    if bannersubtitle:
        lines.append((bannersubtitle, title_font, cfg.TITLE_COLOR))
    for wrapped in util.wrap_line(bannertagline, tagline_font, draw, TEXT_MAX_W):
        lines.append((wrapped, tagline_font, cfg.TAGLINE_COLOR))

    util.draw_text_block(draw, lines)
    util.draw_watermark(draw)

    im.save(out_path, "JPEG", quality=cfg.JPG_QUALITY)
    print(f"Written: {out_path}")


def main():
    build_banner(PROJECT_FILE, OUT_PATH)


if __name__ == "__main__":
    main()
