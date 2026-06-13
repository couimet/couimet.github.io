from PIL import Image

import settings as cfg
from generate import build_banner

from conftest import FIXTURES_DIR, GOLDEN_DIR, assert_matches_golden


def test_build_banner_writes_valid_jpeg_matching_golden(tmp_path):
    out_path = tmp_path / "banner.jpg"

    build_banner(
        bio_path=FIXTURES_DIR / "bio.json",
        face_path=FIXTURES_DIR / "face.jpg",
        out_path=out_path,
    )

    assert out_path.exists()
    with Image.open(out_path) as im:
        assert im.format == "JPEG"
        assert im.size == (cfg.WIDTH, cfg.HEIGHT)

    assert_matches_golden(out_path, GOLDEN_DIR / "banner.jpg")
