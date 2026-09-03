import contextlib
import importlib.util
import io
import random
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml

SCRIPTS = Path(__file__).resolve().parent.parent


def _load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


anchors = _load("validate-anchors")
featured = _load("validate-featured-in")
short_urls = _load("validate-short-urls")
new_short_url = _load("new-short-url")


class _SequenceRng:
    """Injected rng whose choice() returns the next value from *values*."""

    def __init__(self, values):
        self._values = list(values)

    def choice(self, seq):
        return self._values.pop(0)


UNIQUE = [{"anchor": "a"}, {"anchor": "b"}, {"anchor": "c"}]
DUPES = [{"anchor": "a"}, {"anchor": "b"}, {"anchor": "a"}, {"anchor": "c"}]


class TestValidateAnchors(unittest.TestCase):
    def test_no_duplicates(self):
        self.assertEqual(anchors.find_duplicate_anchors(UNIQUE), [])

    def test_duplicates_reported_once(self):
        self.assertEqual(anchors.find_duplicate_anchors(DUPES), ["a"])

    def test_missing_anchor_ignored(self):
        self.assertEqual(anchors.find_duplicate_anchors([{"anchor": "a"}, {}]), [])

    def test_none_anchor_ignored(self):
        self.assertEqual(
            anchors.find_duplicate_anchors([{"anchor": "a"}, {"anchor": None}]),
            [],
        )

    def test_non_dict_items_ignored(self):
        self.assertEqual(anchors.find_duplicate_anchors(["junk", {"anchor": "a"}]), [])


class TestValidateFeaturedIn(unittest.TestCase):
    def test_no_shared_anchors(self):
        self.assertEqual(
            featured.find_duplicate_featured_anchors(
                [{"anchor": "a", "projects": ["p1"]}],
                [{"anchor": "b", "projects": ["p1"]}],
            ),
            [],
        )

    def test_shared_anchor_disjoint_projects(self):
        self.assertEqual(
            featured.find_duplicate_featured_anchors(
                [{"anchor": "a", "projects": ["p1"]}],
                [{"anchor": "a", "projects": ["p2"]}],
            ),
            [],
        )

    def test_shared_anchor_overlapping_projects(self):
        self.assertEqual(
            featured.find_duplicate_featured_anchors(
                [{"anchor": "a", "projects": ["p1"]}],
                [{"anchor": "a", "projects": ["p1"]}],
            ),
            [("a", ["p1"])],
        )

    def test_overlapping_projects_sorted(self):
        self.assertEqual(
            featured.find_duplicate_featured_anchors(
                [{"anchor": "a", "projects": ["p2", "p1"]}],
                [{"anchor": "a", "projects": ["p3", "p1", "p2"]}],
            ),
            [("a", ["p1", "p2"])],
        )

    def test_multiple_collisions_sorted_by_anchor(self):
        self.assertEqual(
            featured.find_duplicate_featured_anchors(
                [
                    {"anchor": "b", "projects": ["p1"]},
                    {"anchor": "a", "projects": ["p1"]},
                ],
                [
                    {"anchor": "b", "projects": ["p1"]},
                    {"anchor": "a", "projects": ["p1"]},
                ],
            ),
            [("a", ["p1"]), ("b", ["p1"])],
        )

    def test_missing_projects_cannot_collide(self):
        self.assertEqual(
            featured.find_duplicate_featured_anchors(
                [{"anchor": "a", "projects": ["p1"]}], [{"anchor": "a"}]
            ),
            [],
        )

    def test_missing_anchor_cannot_collide(self):
        self.assertEqual(
            featured.find_duplicate_featured_anchors(
                [{"projects": ["p1"]}], [{"anchor": "a", "projects": ["p1"]}]
            ),
            [],
        )

    def test_non_dict_items_ignored(self):
        self.assertEqual(
            featured.find_duplicate_featured_anchors(["junk", None], ["junk"]),
            [],
        )


SHARE_ENTRY = {
    "redirect_to": "/#changelog-9-0-0",
    "title": "New role at Procurify",
    "description": "Staff Backend Software Developer on the Platform team at Procurify. Entry 9.0.0 in the career changelog.",
    "bannertagline": "New role at Procurify",
}

ALIAS_ENTRY = {
    "same_as": "kn",
    "redirect_to": "/#changelog-9-0-0",
}


def frontmatter(content):
    """Parse the YAML front matter out of a generated s/<ID>.md file."""
    _, front, _ = content.split("---", 2)
    return yaml.safe_load(front)


class TestValidateShortUrls(unittest.TestCase):
    def test_is_base62_id_accepts_two_char(self):
        self.assertTrue(short_urls.is_base62_id("kn"))
        self.assertTrue(short_urls.is_base62_id("0a"))
        self.assertTrue(short_urls.is_base62_id("Z9"))

    def test_is_base62_id_rejects_three_char(self):
        self.assertFalse(short_urls.is_base62_id("kn1"))

    def test_is_base62_id_rejects_wrong_length(self):
        self.assertFalse(short_urls.is_base62_id("k"))
        self.assertFalse(short_urls.is_base62_id("kna0"))

    def test_is_base62_id_rejects_special_chars(self):
        self.assertFalse(short_urls.is_base62_id("k-"))
        self.assertFalse(short_urls.is_base62_id("k_"))
        self.assertFalse(short_urls.is_base62_id(".."))

    def test_unsorted_ids_reported(self):
        self.assertEqual(short_urls.find_unsorted_ids({"b": {}, "a": {}}), ["a"])
        self.assertEqual(short_urls.find_unsorted_ids({"a": {}, "b": {}}), [])
        self.assertEqual(
            short_urls.find_unsorted_ids({"z": {}, "a": {}, "m": {}}), ["a"]
        )

    def test_invalid_ids_reported(self):
        self.assertEqual(
            short_urls.find_invalid_ids({"kn": {}, "a-": {}, "kn1": {}}),
            ["a-", "kn1"],
        )

    def test_render_page_round_trips_entry(self):
        content = short_urls.render_page("kn", SHARE_ENTRY)
        self.assertTrue(content.startswith("---\n"))
        self.assertTrue(content.rstrip().endswith("---"))
        meta = frontmatter(content)
        self.assertEqual(meta["layout"], "share")
        self.assertEqual(meta["redirect_to"], SHARE_ENTRY["redirect_to"])
        self.assertEqual(meta["title"], SHARE_ENTRY["title"])
        self.assertEqual(meta["description"], SHARE_ENTRY["description"])
        self.assertEqual(meta["og_image"], "/img/social/kn.jpg")
        self.assertEqual(meta["bannertagline"], SHARE_ENTRY["bannertagline"])
        self.assertFalse(meta["sitemap"])

    def test_render_page_bannertagline_falls_back_to_title(self):
        entry = dict(SHARE_ENTRY)
        del entry["bannertagline"]
        meta = frontmatter(short_urls.render_page("kn", entry))
        self.assertEqual(meta["bannertagline"], entry["title"])

    def test_find_stale_pages_current(self):
        with tempfile.TemporaryDirectory() as tmp:
            share_dir = Path(tmp)
            (share_dir / "kn.md").write_text(short_urls.render_page("kn", SHARE_ENTRY))
            self.assertEqual(
                short_urls.find_stale_pages({"kn": SHARE_ENTRY}, share_dir), []
            )

    def test_find_stale_pages_different(self):
        with tempfile.TemporaryDirectory() as tmp:
            share_dir = Path(tmp)
            (share_dir / "kn.md").write_text("---\nlayout: share\n---\n")
            stale = short_urls.find_stale_pages({"kn": SHARE_ENTRY}, share_dir)
            self.assertEqual(stale, [("kn", share_dir / "kn.md")])

    def test_find_stale_pages_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            stale = short_urls.find_stale_pages({"kn": SHARE_ENTRY}, Path(tmp))
            self.assertEqual(stale, [("kn", Path(tmp) / "kn.md")])

    def test_write_pages_writes_changed_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            share_dir = Path(tmp)
            page = share_dir / "kn.md"
            page.write_text("stale")
            written = short_urls.write_pages({"kn": SHARE_ENTRY}, share_dir)
            self.assertEqual(written, [str(page)])
            self.assertEqual(
                page.read_text(), short_urls.render_page("kn", SHARE_ENTRY)
            )
            self.assertEqual(short_urls.write_pages({"kn": SHARE_ENTRY}, share_dir), [])

    def test_check_registry_reports_unsorted(self):
        with tempfile.TemporaryDirectory() as tmp:
            errors = short_urls.check_registry(
                {"b": SHARE_ENTRY, "a": SHARE_ENTRY}, Path(tmp)
            )
            self.assertTrue(any("sorted alphabetically" in e for e in errors))

    def test_find_orphan_pages_detects_generated_page_without_entry(self):
        with tempfile.TemporaryDirectory() as tmp:
            share_dir = Path(tmp)
            header = short_urls.GENERATED_HEADER
            (share_dir / "kn.md").write_text(header + "\nlayout: share\n")
            (share_dir / "zz.md").write_text(header + "\nlayout: share\n")
            orphans = short_urls.find_orphan_pages({"kn": SHARE_ENTRY}, share_dir)
            self.assertEqual([share_id for share_id, _ in orphans], ["zz"])

    def test_find_orphan_pages_ignores_hand_authored_page(self):
        with tempfile.TemporaryDirectory() as tmp:
            share_dir = Path(tmp)
            (share_dir / "zz.md").write_text("layout: share\n")
            self.assertEqual(short_urls.find_orphan_pages({}, share_dir), [])

    def test_check_registry_reports_orphan_pages(self):
        with tempfile.TemporaryDirectory() as tmp:
            share_dir = Path(tmp)
            (share_dir / "zz.md").write_text(
                short_urls.GENERATED_HEADER + "\nlayout: share\n"
            )
            errors = short_urls.check_registry({"kn": SHARE_ENTRY}, share_dir)
            self.assertTrue(any("zz.md is orphaned" in e for e in errors))

    def test_registry_errors_flags_missing_title(self):
        errors = short_urls.registry_errors({"kn": {"redirect_to": "/k"}})
        self.assertTrue(any("title must be a non-empty string" in e for e in errors))

    def test_registry_errors_flags_non_dict_entry(self):
        errors = short_urls.registry_errors({"kn": "foo"})
        self.assertTrue(any("not a mapping" in e for e in errors))

    def test_registry_errors_flags_missing_redirect_to_on_alias(self):
        errors = short_urls.registry_errors(
            {"kn": SHARE_ENTRY, "lk": {"same_as": "kn"}}
        )
        self.assertTrue(any("redirect_to" in e for e in errors))

    def test_registry_errors_accepts_valid_regular_and_alias(self):
        registry = {
            "kn": SHARE_ENTRY,
            "lk": {"same_as": "kn", "redirect_to": "/l"},
        }
        self.assertEqual(short_urls.registry_errors(registry), [])

    def test_registry_errors_does_not_report_stale_pages(self):
        self.assertEqual(short_urls.registry_errors({"kn": SHARE_ENTRY}), [])

    def test_same_as_errors_valid_alias(self):
        registry = {"kn": SHARE_ENTRY, "lk": ALIAS_ENTRY}
        self.assertEqual(short_urls.find_same_as_errors(registry), [])
        self.assertEqual(short_urls.registry_errors(registry), [])

    def test_same_as_target_missing_reported(self):
        registry = {"kn": SHARE_ENTRY, "lk": {"same_as": "zz", "redirect_to": "/"}}
        errors = short_urls.find_same_as_errors(registry)
        self.assertEqual(len(errors), 1)
        self.assertIn("same_as target 'zz' does not exist", errors[0])

    def test_same_as_chain_rejected(self):
        registry = {
            "kn": SHARE_ENTRY,
            "lk": ALIAS_ENTRY,
            "ml": {"same_as": "lk", "redirect_to": "/"},
        }
        errors = short_urls.find_same_as_errors(registry)
        self.assertTrue(any("is itself an alias" in e for e in errors))

    def test_same_as_bannertagline_override_rejected(self):
        registry = {
            "kn": SHARE_ENTRY,
            "lk": dict(ALIAS_ENTRY, bannertagline="Some other tagline"),
        }
        errors = short_urls.find_same_as_errors(registry)
        self.assertTrue(any("cannot override bannertagline" in e for e in errors))

    def test_render_page_alias_inherits_target_banner(self):
        resolved, banner_ids = short_urls.resolve_registry(
            {"kn": SHARE_ENTRY, "lk": ALIAS_ENTRY}
        )
        meta = frontmatter(
            short_urls.render_page("lk", resolved["lk"], banner_ids["lk"])
        )
        self.assertEqual(meta["og_image"], "/img/social/kn.jpg")
        self.assertEqual(meta["title"], SHARE_ENTRY["title"])
        self.assertEqual(meta["description"], SHARE_ENTRY["description"])
        self.assertEqual(meta["bannertagline"], SHARE_ENTRY["bannertagline"])
        self.assertEqual(meta["redirect_to"], ALIAS_ENTRY["redirect_to"])

    def test_render_page_alias_local_overrides(self):
        alias = dict(ALIAS_ENTRY, title="Local title", description="Local desc")
        resolved, banner_ids = short_urls.resolve_registry(
            {"kn": SHARE_ENTRY, "lk": alias}
        )
        meta = frontmatter(
            short_urls.render_page("lk", resolved["lk"], banner_ids["lk"])
        )
        self.assertEqual(meta["title"], "Local title")
        self.assertEqual(meta["description"], "Local desc")
        self.assertEqual(meta["bannertagline"], SHARE_ENTRY["bannertagline"])
        self.assertEqual(meta["og_image"], "/img/social/kn.jpg")

    def test_find_stale_pages_resolves_alias(self):
        registry = {"kn": SHARE_ENTRY, "lk": ALIAS_ENTRY}
        with tempfile.TemporaryDirectory() as tmp:
            share_dir = Path(tmp)
            resolved, banner_ids = short_urls.resolve_registry(registry)
            (share_dir / "kn.md").write_text(
                short_urls.render_page("kn", resolved["kn"], banner_ids["kn"])
            )
            (share_dir / "lk.md").write_text(
                short_urls.render_page("lk", resolved["lk"], banner_ids["lk"])
            )
            self.assertEqual(short_urls.find_stale_pages(registry, share_dir), [])

    def test_find_stale_pages_alias_with_own_banner_is_stale(self):
        # A stale lk.md referencing its own banner (/img/social/lk.jpg) must be
        # flagged and rewritten to the target's banner.
        registry = {"kn": SHARE_ENTRY, "lk": ALIAS_ENTRY}
        with tempfile.TemporaryDirectory() as tmp:
            share_dir = Path(tmp)
            resolved, banner_ids = short_urls.resolve_registry(registry)
            (share_dir / "kn.md").write_text(
                short_urls.render_page("kn", resolved["kn"], banner_ids["kn"])
            )
            (share_dir / "lk.md").write_text(
                "---\nlayout: share\nog_image: /img/social/lk.jpg\n---\n"
            )
            stale = short_urls.find_stale_pages(registry, share_dir)
            self.assertEqual(stale, [("lk", share_dir / "lk.md")])

    def test_write_pages_alias_uses_target_banner(self):
        registry = {"kn": SHARE_ENTRY, "lk": ALIAS_ENTRY}
        with tempfile.TemporaryDirectory() as tmp:
            share_dir = Path(tmp)
            written = short_urls.write_pages(registry, share_dir)
            self.assertEqual(len(written), 2)
            meta = frontmatter((share_dir / "lk.md").read_text())
            self.assertEqual(meta["og_image"], "/img/social/kn.jpg")

    def test_share_ids_known(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inc = root / "_includes" / "career"
            inc.mkdir(parents=True)
            (inc / "changelog.html").write_text(
                '<h2 id="a">{% include heading-anchor.html id="a" shareId="kn" %}</h2>\n'
            )
            self.assertEqual(
                short_urls.find_unknown_shortened_ids({"kn": SHARE_ENTRY}, root), []
            )

    def test_share_ids_unknown_reported_with_location(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inc = root / "_includes" / "career"
            inc.mkdir(parents=True)
            path = inc / "changelog.html"
            path.write_text(
                '<h2 id="a">{% include heading-anchor.html id="a" shareId="kn" %}</h2>\n'
                '<h2 id="b">{% include heading-anchor.html id="b" shareId="zz" %}</h2>\n'
            )
            self.assertEqual(
                short_urls.find_unknown_shortened_ids({"kn": SHARE_ENTRY}, root),
                [(path, 2, "zz")],
            )

    def test_home_share_ids_unknown_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inc = root / "_includes" / "career"
            inc.mkdir(parents=True)
            path = inc / "changelog.html"
            path.write_text(
                '<h2 id="a">{% include heading-anchor.html id="a" shareId="kn" homeShareId="lk" %}</h2>\n'
            )
            self.assertEqual(
                short_urls.find_unknown_shortened_ids({"kn": SHARE_ENTRY}, root),
                [(path, 1, "lk")],
            )

    def test_share_ids_ignores_js_and_liquid(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inc = root / "_includes"
            inc.mkdir(parents=True)
            (inc / "copy-link.html").write_text(
                'var url = anchor.getAttribute("shareId");\n'
            )
            (inc / "heading-anchor.html").write_text(
                'shareId="{{ include.shareId }}"\n'
                'homeShareId="{{ include.homeShareId }}"\n'
            )
            (inc / "footer.html").write_text("<p>plain 🔗</p>\n")
            self.assertEqual(
                short_urls.find_unknown_shortened_ids({"kn": SHARE_ENTRY}, root), []
            )


REGISTRY_TEXT = (
    "# header comment\n"
    "\n"
    "kn:\n"
    "  redirect_to: /career/changelog/#changelog-9-0-0\n"
    "  title: New role at Procurify\n"
    "  description: A role.\n"
    "lk:\n"
    "  same_as: kn\n"
    "  redirect_to: /#changelog-9-0-0\n"
)


class TestNewShortUrl(unittest.TestCase):
    def test_is_base62_id(self):
        self.assertTrue(new_short_url.is_base62_id("kn"))
        self.assertTrue(new_short_url.is_base62_id("0a"))
        self.assertTrue(new_short_url.is_base62_id("Z9"))
        self.assertFalse(new_short_url.is_base62_id("k"))
        self.assertFalse(new_short_url.is_base62_id("kna0"))

    def test_insert_entry_keeps_registry_sorted(self):
        text = new_short_url.insert_entry(REGISTRY_TEXT, "aa")
        self.assertLess(text.index("aa:"), text.index("kn:"))
        text = new_short_url.insert_entry(REGISTRY_TEXT, "zz")
        self.assertGreater(text.index("zz:"), text.index("lk:"))

    def test_insert_entry_preserves_comment_block(self):
        text = new_short_url.insert_entry(REGISTRY_TEXT, "aa")
        self.assertTrue(text.startswith("# header comment\n"))

    def test_insert_entry_writes_placeholder_block(self):
        text = new_short_url.insert_entry(REGISTRY_TEXT, "aa")
        block = text.split("aa:", 1)[1].split("kn:", 1)[0]
        self.assertIn("redirect_to: /TODO", block)
        self.assertIn("title: TODO", block)
        self.assertIn("description: TODO", block)

    def test_insert_entry_comments_out_bannertagline(self):
        text = new_short_url.insert_entry(REGISTRY_TEXT, "aa")
        block = text.split("aa:", 1)[1].split("kn:", 1)[0]
        self.assertIn("# bannertagline: TODO", block)

    def test_insert_entry_rejects_duplicate(self):
        with self.assertRaises(ValueError):
            new_short_url.insert_entry(REGISTRY_TEXT, "kn")

    def test_insert_entry_middle_position_keeps_neighbors(self):
        text = new_short_url.insert_entry(REGISTRY_TEXT, "km")
        self.assertLess(text.index("km:"), text.index("kn:"))
        self.assertLess(text.index("kn:"), text.index("lk:"))

    def test_generate_share_id_avoids_existing(self):
        registry = {"kn": {}, "lk": {}}
        for _ in range(20):
            share_id = new_short_url.generate_share_id(registry)
            self.assertTrue(new_short_url.is_base62_id(share_id))
            self.assertNotIn(share_id, registry)

    def test_is_reserved_id_rejects_yaml_boolean_words(self):
        for share_id in ("on", "no", "yes", "off", "ON", "No", "YeS", "OFF"):
            self.assertTrue(new_short_url.is_reserved_id(share_id))

    def test_is_reserved_id_accepts_ordinary_ids(self):
        for share_id in ("ab", "on1", "zz", "kn"):
            self.assertFalse(new_short_url.is_reserved_id(share_id))

    def test_generate_share_id_rejects_reserved_candidate(self):
        # An injected rng that first yields "on" (a YAML-reserved word) must be
        # skipped so generation returns the next non-reserved candidate.
        registry = {"kn": {}, "lk": {}}
        rng = _SequenceRng("onab")
        share_id = new_short_url.generate_share_id(registry, rng=rng)
        self.assertEqual(share_id, "ab")

    def test_generate_share_id_avoids_reserved_ids(self):
        registry = {"kn": {}, "lk": {}}
        for _ in range(200):
            share_id = new_short_url.generate_share_id(registry)
            self.assertFalse(new_short_url.is_reserved_id(share_id))

    def test_generate_share_id_always_two_chars(self):
        registry = {"kn": {}, "lk": {}}
        for _ in range(20):
            self.assertEqual(len(new_short_url.generate_share_id(registry)), 2)

    def test_generate_share_id_deterministic_with_rng(self):
        registry = {"kn": {}, "lk": {}}
        rng = random.Random(7)
        first = new_short_url.generate_share_id(registry, rng=rng)
        rng = random.Random(7)
        second = new_short_url.generate_share_id(registry, rng=rng)
        self.assertEqual(first, second)

    def test_generate_share_id_exhausted_two_char_space_raises(self):
        # Every 2-char ID taken: generator must raise ValueError.
        registry = {}
        for a in new_short_url.BASE62_CHARS:
            for b in new_short_url.BASE62_CHARS:
                registry[a + b] = {}
        with self.assertRaises(ValueError):
            new_short_url.generate_share_id(registry)

    def test_main_generate_only_prints_valid_id_and_leaves_registry(self):
        # --generate-only must not touch the registry file: stdout carries a
        # bare, valid 2-char ID drawn from the real registry.
        original = new_short_url.REGISTRY_PATH.read_text()
        out = io.StringIO()
        with mock.patch.object(
            sys, "argv", ["new-short-url.py", "--generate-only"]
        ), contextlib.redirect_stdout(out):
            new_short_url.main()
        share_id = out.getvalue().strip()
        self.assertTrue(new_short_url.is_base62_id(share_id))
        self.assertNotIn(share_id, yaml.safe_load(original) or {})
        self.assertEqual(new_short_url.REGISTRY_PATH.read_text(), original)


if __name__ == "__main__":
    unittest.main()
