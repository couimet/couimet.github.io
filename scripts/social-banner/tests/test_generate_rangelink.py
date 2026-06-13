import pytest
from PIL import Image

import settings as cfg
from generate_rangelink import build_banner

from conftest import FIXTURES_DIR, GOLDEN_DIR, assert_matches_golden


@pytest.fixture
def fake_icon_loader():
    icon_bytes = (FIXTURES_DIR / "icon.png").read_bytes()
    return lambda _url: icon_bytes


def test_build_banner_writes_valid_jpeg_matching_golden(tmp_path, fake_icon_loader):
    out_path = tmp_path / "banner-rangelink.jpg"

    build_banner(
        project_md_path=FIXTURES_DIR / "rangelink.md",
        out_path=out_path,
        icon_loader=fake_icon_loader,
    )

    assert out_path.exists()
    with Image.open(out_path) as im:
        assert im.format == "JPEG"
        assert im.size == (cfg.WIDTH, cfg.HEIGHT)

    assert_matches_golden(out_path, GOLDEN_DIR / "banner-rangelink.jpg")


def test_build_banner_uses_title_fallback_when_bannertitle_missing(tmp_path, fake_icon_loader):
    project_md = tmp_path / "no-bannertitle.md"
    project_md.write_text(
        '---\n'
        'title: "Test Extension"\n'
        'summary: "fallback summary"\n'
        'sourceiconurl: "https://example.invalid/icon.png"\n'
        '---\n'
    )
    out_path = tmp_path / "banner-fallback.jpg"

    build_banner(
        project_md_path=project_md,
        out_path=out_path,
        icon_loader=fake_icon_loader,
    )

    assert out_path.exists()
    with Image.open(out_path) as im:
        assert im.size == (cfg.WIDTH, cfg.HEIGHT)
