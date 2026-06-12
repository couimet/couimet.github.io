"""Shared rendering helpers for social banner generation scripts.

Imported by generate-social-banner.py and generate-social-banner-rangelink.py.
"""

from PIL import ImageDraw, ImageFont

import _banner_settings as cfg


def load_font(size, weight="regular"):
    path = cfg.FONT_BOLD if weight == "bold" else cfg.FONT_REGULAR
    return ImageFont.truetype(path, size)


def wrap_line(text, font, draw, max_width):
    """Break *text* into lines that each fit within *max_width*."""
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
    return lines if lines else [text]


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
