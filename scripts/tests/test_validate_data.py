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


if __name__ == "__main__":
    unittest.main()
