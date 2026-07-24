"""Tests for generate_network_nudge banner rendering."""

import pytest
from PIL import Image

import settings as cfg
import utils as util

from conftest import FIXTURES_DIR, GOLDEN_DIR, assert_matches_golden


def load_fixture_icon():
    """Load the test fixture icon, scaled for the banner."""
    path = FIXTURES_DIR / "icon.png"
    icon = Image.open(path).convert("RGBA")
    return util.sized_icon(icon, cfg.ICON_SIZE)


def test_compose_banner_writes_valid_jpeg_matching_golden(tmp_path):
    out_path = tmp_path / "banner-network-nudge.jpg"
    meta = util.load_project_meta(FIXTURES_DIR / "network-nudge.md")
    icon = load_fixture_icon()

    util.compose_banner(meta, icon, out_path)

    assert out_path.exists()
    with Image.open(out_path) as im:
        assert im.format == "JPEG"
        assert im.size == (cfg.WIDTH, cfg.HEIGHT)

    assert_matches_golden(out_path, GOLDEN_DIR / "banner-network-nudge.jpg")


def test_compose_banner_uses_summary_fallback_when_bannertagline_missing(tmp_path):
    project_md = tmp_path / "no-tagline.md"
    project_md.write_text(
        "---\n"
        'title: "Network Nudge"\n'
        'summary: "fallback summary text"\n'
        "---\n"
    )
    out_path = tmp_path / "banner-fallback.jpg"
    meta = util.load_project_meta(project_md)
    icon = load_fixture_icon()

    util.compose_banner(meta, icon, out_path)

    assert out_path.exists()
    with Image.open(out_path) as im:
        assert im.size == (cfg.WIDTH, cfg.HEIGHT)

    assert_matches_golden(out_path, GOLDEN_DIR / "banner-network-nudge-fallback.jpg")
