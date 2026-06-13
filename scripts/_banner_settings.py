from pathlib import Path

"""Shared settings for social banner generation scripts.

Both generate-social-banner.py and generate-social-banner-rangelink.py
import this module so colours, fonts, layout, and watermark stay in sync.
"""

# ── Dimensions ──────────────────────────────────────────────────────────────

WIDTH = 1200
HEIGHT = 630

# ── Colour palette (light, matches Bootstrap default theme) ──────────────────

BG_COLOR = "#ffffff"
NAME_COLOR = "#212529"          # near-black, matches body text
TITLE_COLOR = "#495057"         # dark gray
TAGLINE_COLOR = "#6c757d"       # muted gray
WATERMARK_COLOR = "#6c757d"     # muted gray, readable on white
DIVIDER_COLOR = "#dee2e6"       # thin rule between face/icon and text

# ── Layout grid ─────────────────────────────────────────────────────────────

LEFT_REGION_WIDTH = 440          # px — face photo or project icon lives here
TEXT_REGION_X = LEFT_REGION_WIDTH + 60  # where text starts
TEXT_REGION_MAX_WIDTH = 640      # max text width before wrapping
PADDING_H = 80                   # horizontal margin from edges
PADDING_V = 60                   # vertical margin from edges

# ── Font stack ──────────────────────────────────────────────────────────────

FONT_REGULAR = str(Path(__file__).resolve().parent / "fonts" / "OpenSans-Regular.ttf")
FONT_BOLD = str(Path(__file__).resolve().parent / "fonts" / "OpenSans-Bold.ttf")
NAME_FONT_SIZE = 56
NAME_FONT_WEIGHT = "bold"
TITLE_FONT_SIZE = 32
TITLE_FONT_WEIGHT = "regular"
TAGLINE_FONT_SIZE = 24
TAGLINE_FONT_WEIGHT = "regular"
WATERMARK_FONT_SIZE = 16

# Line spacing between the three text lines (px gap, not leading)
LINE_SPACING = 16

# ── Face photo styling ──────────────────────────────────────────────────────

FACE_SIZE = 320                  # diameter of circular crop (px)
FACE_X = PADDING_H + (LEFT_REGION_WIDTH - FACE_SIZE) // 2  # centred in left region

# ── Project icon styling (for RangeLink-style banners) ──────────────────────

ICON_SIZE = FACE_SIZE            # match face photo size for consistency
ICON_X = PADDING_H + (LEFT_REGION_WIDTH - ICON_SIZE) // 2

# ── Watermark ───────────────────────────────────────────────────────────────

WATERMARK_TEXT = "ouimet.info"
WATERMARK_MARGIN = 30            # px from bottom-right corner

# ── Output ──────────────────────────────────────────────────────────────────

JPG_QUALITY = 92
