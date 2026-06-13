import pytest
from PIL import Image, ImageDraw, ImageFont

import settings as cfg
import utils


@pytest.fixture
def draw_ctx():
    im = Image.new("RGB", (cfg.WIDTH, cfg.HEIGHT))
    return ImageDraw.Draw(im)


@pytest.fixture
def tagline_font():
    return utils.load_font(cfg.TAGLINE_FONT_SIZE, cfg.TAGLINE_FONT_WEIGHT)


def test_load_font_returns_truetype_for_both_weights():
    regular = utils.load_font(24, "regular")
    bold = utils.load_font(24, "bold")
    assert isinstance(regular, ImageFont.FreeTypeFont)
    assert isinstance(bold, ImageFont.FreeTypeFont)
    assert regular.path != bold.path


def test_wrap_line_single_word_fits_unchanged(draw_ctx, tagline_font):
    assert utils.wrap_line("hello", tagline_font, draw_ctx, 1000) == ["hello"]


def test_wrap_line_empty_input_returns_original(draw_ctx, tagline_font):
    assert utils.wrap_line("", tagline_font, draw_ctx, 1000) == [""]


def test_wrap_line_breaks_long_text(draw_ctx, tagline_font):
    text = "one two three four five six seven eight nine ten eleven twelve"
    lines = utils.wrap_line(text, tagline_font, draw_ctx, 200)
    assert len(lines) > 1
    assert " ".join(lines).split() == text.split()


def test_wrap_line_keeps_short_text_on_one_line(draw_ctx, tagline_font):
    assert utils.wrap_line("a b c", tagline_font, draw_ctx, 1000) == ["a b c"]


@pytest.mark.parametrize(
    "meta,expected",
    [
        ({"title": "RangeLink Extension"}, "RangeLink"),
        ({"title": "Test Extension"}, "Test"),
        ({"bannertitle": "Custom", "title": "X Extension"}, "Custom"),
        ({"title": "No Suffix"}, "No Suffix"),
        ({"bannertitle": "", "title": "RangeLink Extension"}, "RangeLink"),
    ],
)
def test_derive_bannertitle(meta, expected):
    assert utils.derive_bannertitle(meta) == expected
