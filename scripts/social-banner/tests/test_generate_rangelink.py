"""Tests for generate_rangelink banner rendering."""

import pytest
from PIL import Image

import settings as cfg
import utils as util

from conftest import FIXTURES_DIR, GOLDEN_DIR, assert_matches_golden


@pytest.fixture
def fake_icon_bytes():
    return (FIXTURES_DIR / "icon.png").read_bytes()


def icon_from_fixture(icon_bytes):
    """Load the fixture icon through the same trim + scale pipeline as main()."""
    from io import BytesIO

    icon = Image.open(BytesIO(icon_bytes)).convert("RGBA")
    return util.sized_icon(util.trim_to_content(icon), cfg.ICON_SIZE)


def test_compose_banner_writes_valid_jpeg_matching_golden(tmp_path, fake_icon_bytes):
    out_path = tmp_path / "banner-rangelink.jpg"
    meta = util.load_project_meta(FIXTURES_DIR / "rangelink.md")
    icon = icon_from_fixture(fake_icon_bytes)

    util.compose_banner(meta, icon, out_path)

    assert out_path.exists()
    with Image.open(out_path) as im:
        assert im.format == "JPEG"
        assert im.size == (cfg.WIDTH, cfg.HEIGHT)

    assert_matches_golden(out_path, GOLDEN_DIR / "banner-rangelink.jpg")


def test_compose_banner_uses_title_fallback_when_bannertitle_missing(tmp_path, fake_icon_bytes):
    project_md = tmp_path / "no-bannertitle.md"
    project_md.write_text(
        "---\n"
        'title: "Test Extension"\n'
        'summary: "fallback summary"\n'
        'sourceiconurl: "https://example.invalid/icon.png"\n'
        "---\n"
    )
    out_path = tmp_path / "banner-fallback.jpg"
    meta = util.load_project_meta(project_md)
    icon = icon_from_fixture(fake_icon_bytes)

    util.compose_banner(meta, icon, out_path)

    assert out_path.exists()
    with Image.open(out_path) as im:
        assert im.size == (cfg.WIDTH, cfg.HEIGHT)

    assert_matches_golden(out_path, GOLDEN_DIR / "banner-rangelink-fallback.jpg")
