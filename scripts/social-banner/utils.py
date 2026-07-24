"""Shared rendering helpers for social banner generation scripts."""

import re
import sys
from io import BytesIO
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import urlopen

import yaml
from PIL import Image, ImageDraw, ImageFont

import settings as cfg

MAX_ICON_BYTES = 10 * 1024 * 1024  # 10 MB


def load_project_meta(project_md_path):
    """Parse Jekyll front matter from a project markdown file."""
    with open(project_md_path) as f:
        content = f.read()
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        print(f"No front matter found in {project_md_path}", file=sys.stderr)
        sys.exit(1)
    return yaml.safe_load(match.group(1))


def sized_icon(icon, target_size):
    """Scale *icon* so its larger dimension equals *target_size*, preserving aspect ratio."""
    scale = target_size / max(icon.size)
    new_w = int(icon.width * scale)
    new_h = int(icon.height * scale)
    return icon.resize((new_w, new_h), Image.Resampling.LANCZOS)


def resolve_icon_url(meta):
    """Return the best-resolution icon URL from project front matter."""
    for key in ("sourceiconurl", "logourl", "iconurl"):
        url = meta.get(key)
        if url:
            return url
    print("No icon URL found in project front matter", file=sys.stderr)
    sys.exit(1)


def download_icon(url):
    """Download and decode an icon from *url*, returning a PIL Image.

    Only http/https schemes are allowed. The response is capped at
    MAX_ICON_BYTES before passing bytes to Image.open.
    """
    if urlparse(url).scheme not in ("http", "https"):
        print(f"Refusing non-http(s) icon URL: {url}", file=sys.stderr)
        sys.exit(1)
    try:
        with urlopen(url, timeout=10) as resp:
            data = resp.read(MAX_ICON_BYTES + 1)
            if len(data) > MAX_ICON_BYTES:
                print(f"Icon exceeds {MAX_ICON_BYTES} byte limit: {url}", file=sys.stderr)
                sys.exit(1)
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


def load_font(size, weight="regular"):
    path = cfg.FONT_BOLD if weight == "bold" else cfg.FONT_REGULAR
    return ImageFont.truetype(path, size)


def derive_bannertitle(meta):
    return meta.get("bannertitle") or meta.get("title", "").removesuffix(" Extension")


def wrap_line(text, font, draw, max_width):
    """Break *text* into lines that each fit within *max_width*."""
    if not text:
        return []
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = f"{current} {word}".strip()
        if draw.textbbox((0, 0), trial, font=font)[2] <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_text_block(draw, lines, start_y=None):
    """Draw a list of (text, font, color) tuples, vertically centred.

    Returns the y coordinate after the last line (bottom of text block).
    If *start_y* is None the block is centred on the canvas.
    """
    line_heights = [draw.textbbox((0, 0), t, font=f)[3] for t, f, _ in lines]
    spacings = [cfg.LINE_SPACING] * (len(lines) - 1)
    total_h = sum(line_heights) + sum(spacings)

    y = start_y if start_y is not None else (cfg.HEIGHT - total_h) // 2

    for i, (text, font, color) in enumerate(lines):
        bbox = draw.textbbox((0, 0), text, font=font)
        draw.text((cfg.TEXT_REGION_X, y), text, font=font, fill=color)
        y += (bbox[3] - bbox[1])
        if i < len(lines) - 1:
            y += cfg.LINE_SPACING

    return y


def compose_banner(meta, icon, out_path):
    """Composite a project social banner: icon on the left, text on the right.

    *meta* is the parsed Jekyll front matter dict.
    *icon* is a PIL Image already scaled to cfg.ICON_SIZE.
    *out_path* is the destination JPEG path.
    """
    from PIL import Image, ImageDraw

    bannertitle = derive_bannertitle(meta)
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
    name_font = load_font(cfg.NAME_FONT_SIZE, cfg.NAME_FONT_WEIGHT)
    title_font = load_font(cfg.TITLE_FONT_SIZE, cfg.TITLE_FONT_WEIGHT)
    tagline_font = load_font(cfg.TAGLINE_FONT_SIZE, cfg.TAGLINE_FONT_WEIGHT)
    text_max_w = cfg.WIDTH - cfg.TEXT_REGION_X - cfg.PADDING_H

    lines = [
        (bannertitle, name_font, cfg.NAME_COLOR),
    ]
    if bannersubtitle:
        lines.append((bannersubtitle, title_font, cfg.TITLE_COLOR))
    for wrapped in wrap_line(bannertagline, tagline_font, draw, text_max_w):
        lines.append((wrapped, tagline_font, cfg.TAGLINE_COLOR))

    draw_text_block(draw, lines)
    draw_watermark(draw)

    im.save(out_path, "JPEG", quality=cfg.JPG_QUALITY)
    print(f"Written: {out_path}")


def draw_watermark(draw):
    font = load_font(cfg.WATERMARK_FONT_SIZE, "regular")
    bbox = draw.textbbox((0, 0), cfg.WATERMARK_TEXT, font=font)
    wm_w = bbox[2] - bbox[0]
    wm_h = bbox[3] - bbox[1]
    draw.text(
        (cfg.WIDTH - cfg.WATERMARK_MARGIN - wm_w,
         cfg.HEIGHT - cfg.WATERMARK_MARGIN - wm_h),
        cfg.WATERMARK_TEXT,
        font=font,
        fill=cfg.WATERMARK_COLOR,
    )
