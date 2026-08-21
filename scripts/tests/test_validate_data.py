import importlib.util
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent


def _load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


articles = _load("validate-articles")
promotions = _load("validate-promotions")
featured = _load("validate-featured-in")

UNIQUE = [{"anchor": "a"}, {"anchor": "b"}, {"anchor": "c"}]
DUPES = [{"anchor": "a"}, {"anchor": "b"}, {"anchor": "a"}, {"anchor": "c"}]


class TestValidateArticles(unittest.TestCase):
    def test_no_duplicates(self):
        self.assertEqual(articles.find_duplicate_anchors(UNIQUE), [])

    def test_duplicates_reported_once(self):
        self.assertEqual(articles.find_duplicate_anchors(DUPES), ["a"])

    def test_missing_anchor_ignored(self):
        self.assertEqual(articles.find_duplicate_anchors([{"anchor": "a"}, {}]), [])

    def test_non_dict_items_ignored(self):
        self.assertEqual(articles.find_duplicate_anchors(["junk", {"anchor": "a"}]), [])


class TestValidatePromotions(unittest.TestCase):
    def test_no_duplicates(self):
        self.assertEqual(promotions.find_duplicate_anchors(UNIQUE), [])

    def test_duplicates_reported_once(self):
        self.assertEqual(promotions.find_duplicate_anchors(DUPES), ["a"])

    def test_missing_anchor_ignored(self):
        self.assertEqual(
            promotions.find_duplicate_anchors([{"anchor": "a"}, {"anchor": None}]),
            [],
        )


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


if __name__ == "__main__":
    unittest.main()
