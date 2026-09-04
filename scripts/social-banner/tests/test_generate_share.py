"""Tests for generate_share project-branded share banners."""

import json

import generate_share
import settings as cfg
import utils as util
from conftest import FIXTURES_DIR, GOLDEN_DIR, assert_matches_golden
from PIL import Image

# A registry entry pointing at a Network Nudge template hash on the app page.
NN_ENTRY = {
    "redirect_to": "/projects/network-nudge.html#direct-application",
    "title": "Network Nudge",
    "description": "Direct cold application. You found a role and want to reach the hiring manager or talent team directly.",
    "bannertagline": "Reach the hiring manager directly",
}
# A registry entry pointing at a career changelog anchor (default personal card).
CHANGELOG_ENTRY = {
    "redirect_to": "/career/changelog/#changelog-9-0-0",
    "title": "New role at Procurify",
    "description": "Staff Backend Software Developer on the Platform team.",
}


def load_fixture_icon():
    """Load the test fixture icon, scaled for the banner."""
    path = FIXTURES_DIR / "icon.png"
    icon = Image.open(path).convert("RGBA")
    return util.sized_icon(icon, cfg.ICON_SIZE)


def load_fixture_bio():
    with open(FIXTURES_DIR / "bio.json") as f:
        return json.load(f)["basics"]


def test_project_banner_meta_targets_project_page():
    meta = generate_share.project_banner_meta(NN_ENTRY, FIXTURES_DIR)
    assert meta is not None
    assert meta["bannertitle"] == "Network Nudge"


def test_project_banner_meta_ignores_non_project_redirect():
    assert generate_share.project_banner_meta(CHANGELOG_ENTRY, FIXTURES_DIR) is None


def test_project_banner_meta_none_for_missing_project(tmp_path):
    entry = {"redirect_to": "/projects/does-not-exist.html"}
    assert generate_share.project_banner_meta(entry, tmp_path) is None


def test_project_banner_meta_none_when_project_lacks_banner(tmp_path):
    (tmp_path / "plain.md").write_text(
        "---\ntitle: Plain\nsummary: no banner here.\n---\n"
    )
    entry = {"redirect_to": "/projects/plain.html"}
    assert generate_share.project_banner_meta(entry, tmp_path) is None


def test_project_share_meta_keeps_branding_and_sets_entry_tagline():
    project_meta = {
        "bannertitle": "Network Nudge",
        "bannersubtitle": "Outreach Message Builder",
        "bannertagline": "Pick a template, fill in the blanks, copy.",
    }
    meta = generate_share.project_share_meta(NN_ENTRY, project_meta)
    assert meta["bannertitle"] == "Network Nudge"
    assert meta["bannersubtitle"] == "Outreach Message Builder"
    assert meta["bannertagline"] == "Reach the hiring manager directly"


def test_project_share_meta_tagline_defaults_to_entry_title():
    project_meta = {"bannertitle": "Network Nudge"}
    entry = {"title": "Network Nudge", "redirect_to": "/projects/network-nudge.html#x"}
    meta = generate_share.project_share_meta(entry, project_meta)
    assert meta["bannertagline"] == "Network Nudge"


def test_project_share_meta_keeps_project_subtitle_when_entry_has_none():
    project_meta = {
        "bannertitle": "Network Nudge",
        "bannersubtitle": "Outreach Message Builder",
    }
    entry = {
        "title": "Network Nudge",
        "redirect_to": "/projects/network-nudge.html#fr--x",
    }
    meta = generate_share.project_share_meta(entry, project_meta)
    assert meta["bannersubtitle"] == "Outreach Message Builder"


def test_project_share_meta_entry_bannersubtitle_overrides_project():
    project_meta = {
        "bannertitle": "Network Nudge",
        "bannersubtitle": "Outreach Message Builder",
    }
    entry = {
        "title": "Network Nudge",
        "redirect_to": "/projects/network-nudge.html#fr--x",
        "bannersubtitle": "Générateur de messages d'approche",
    }
    meta = generate_share.project_share_meta(entry, project_meta)
    assert meta["bannersubtitle"] == "Générateur de messages d'approche"


def test_project_share_meta_ignores_blank_entry_bannersubtitle():
    project_meta = {
        "bannertitle": "Network Nudge",
        "bannersubtitle": "Outreach Message Builder",
    }
    entry = {
        "title": "Network Nudge",
        "redirect_to": "/projects/network-nudge.html#fr--x",
        "bannersubtitle": "",
    }
    meta = generate_share.project_share_meta(entry, project_meta)
    assert meta["bannersubtitle"] == "Outreach Message Builder"


def test_share_meta_defaults_to_bio_and_title_tagline():
    bio = load_fixture_bio()
    meta = generate_share.share_meta(CHANGELOG_ENTRY, bio)
    assert meta["bannertitle"] == bio["name"]
    assert meta["bannersubtitle"] == bio["label"]
    assert meta["bannertagline"] == CHANGELOG_ENTRY["title"]


def test_share_meta_respects_entry_bannertagline():
    bio = load_fixture_bio()
    entry = dict(CHANGELOG_ENTRY, bannertagline="custom tagline")
    meta = generate_share.share_meta(entry, bio)
    assert meta["bannertagline"] == "custom tagline"


def test_compose_project_share_writes_valid_jpeg_matching_golden(tmp_path):
    out_path = tmp_path / "banner-share-nudge.jpg"
    project_meta = util.load_project_meta(FIXTURES_DIR / "network-nudge.md")
    meta = generate_share.project_share_meta(NN_ENTRY, project_meta)
    icon = load_fixture_icon()

    util.compose_banner(meta, icon, out_path)

    assert out_path.exists()
    with Image.open(out_path) as im:
        assert im.format == "JPEG"
        assert im.size == (cfg.WIDTH, cfg.HEIGHT)

    assert_matches_golden(out_path, GOLDEN_DIR / "banner-share-network-nudge.jpg")
