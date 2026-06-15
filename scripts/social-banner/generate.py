#!/usr/bin/env python3
"""Generate the default social banner (img/social-banner.jpg).

Reads _data/bio.json, composites the face photo (circular crop)
on the left with name / title / tagline text on the right.
"""

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

import settings as cfg
import utils as util

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
BIO_PATH = REPO_ROOT / "_data" / "bio.json"
OUT_PATH = REPO_ROOT / "img" / "social-banner.jpg"

TEXT_MAX_W = cfg.WIDTH - cfg.TEXT_REGION_X - cfg.PADDING_H


def load_bio(bio_path):
    with open(bio_path) as f:
        return json.load(f)["basics"]


def cropped_face(face_path, size):
    src = Image.open(face_path).convert("RGB")
    scale = size / min(src.size)
    new_w = int(src.width * scale)
    new_h = int(src.height * scale)
    src = src.resize((new_w, new_h), Image.Resampling.LANCZOS)
    left = (new_w - size) // 2
    top = (new_h - size) // 2
    src = src.crop((left, top, left + size, top + size))
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size, size), fill=255)
    canvas = Image.new("RGB", (size, size), cfg.BG_COLOR)
    canvas.paste(src, mask=mask)
    return canvas


def build_banner(bio_path, face_path, out_path):
    bio = load_bio(bio_path)

    name = bio["name"]
    title = bio["label"]
    tagline = bio.get("summarySocialBanner", "")

    im = Image.new("RGB", (cfg.WIDTH, cfg.HEIGHT), cfg.BG_COLOR)
    draw = ImageDraw.Draw(im)

    face = cropped_face(str(face_path), cfg.FACE_SIZE)
    face_y = (cfg.HEIGHT - cfg.FACE_SIZE) // 2
    im.paste(face, (cfg.FACE_X, face_y))

    # Build line list
    name_font = util.load_font(cfg.NAME_FONT_SIZE, cfg.NAME_FONT_WEIGHT)
    title_font = util.load_font(cfg.TITLE_FONT_SIZE, cfg.TITLE_FONT_WEIGHT)
    tagline_font = util.load_font(cfg.TAGLINE_FONT_SIZE, cfg.TAGLINE_FONT_WEIGHT)

    lines = [
        (name, name_font, cfg.NAME_COLOR),
        (title, title_font, cfg.TITLE_COLOR),
    ]
    for wrapped in util.wrap_line(tagline, tagline_font, draw, TEXT_MAX_W):
        lines.append((wrapped, tagline_font, cfg.TAGLINE_COLOR))

    util.draw_text_block(draw, lines)
    util.draw_watermark(draw)

    im.save(out_path, "JPEG", quality=cfg.JPG_QUALITY)
    print(f"Written: {out_path}")


def main():
    bio = load_bio(BIO_PATH)
    picture = bio.get("picture")
    if not picture:
        print("Missing 'picture' in bio.json basics", file=sys.stderr)
        sys.exit(1)
    face_abs = REPO_ROOT / picture.lstrip("/")
    if not face_abs.exists():
        print(f"Face photo not found: {face_abs}", file=sys.stderr)
        sys.exit(1)
    build_banner(BIO_PATH, face_abs, OUT_PATH)


if __name__ == "__main__":
    main()
