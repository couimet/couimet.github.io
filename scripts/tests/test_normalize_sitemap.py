import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "normalize-sitemap.py"
NS = "http://www.sitemaps.org/schemas/sitemap/0.9"

UNSORTED = """<?xml version='1.0' encoding='UTF-8'?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://ouimet.info/projects/</loc>
  </url>
  <url>
    <loc>https://ouimet.info/</loc>
  </url>
  <url>
    <loc>https://ouimet.info/articles/</loc>
    <lastmod>2026-06-06T13:56:13-04:00</lastmod>
  </url>
</urlset>
"""


def _run(*args):
    subprocess.run(["python3", str(SCRIPT), *args], check=True)


def _locs(path):
    tree = ET.parse(path)
    root = tree.getroot()
    return [u.findtext(f"{{{NS}}}loc") for u in root.findall(f"{{{NS}}}url")]


def _lastmods(path):
    tree = ET.parse(path)
    root = tree.getroot()
    return [u.findtext(f"{{{NS}}}lastmod") for u in root.findall(f"{{{NS}}}url")]


class NormalizeSitemapTest(unittest.TestCase):
    def test_sort_orders_urls_by_loc(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
            f.write(UNSORTED)
        try:
            _run(f.name)
            self.assertEqual(
                _locs(f.name),
                [
                    "https://ouimet.info/",
                    "https://ouimet.info/articles/",
                    "https://ouimet.info/projects/",
                ],
            )
        finally:
            Path(f.name).unlink()

    def test_default_preserves_lastmod(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
            f.write(UNSORTED)
        try:
            _run(f.name)
            self.assertEqual(
                _lastmods(f.name),
                [None, "2026-06-06T13:56:13-04:00", None],
            )
        finally:
            Path(f.name).unlink()

    def test_strip_lastmod_removes_all_lastmod_tags(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
            f.write(UNSORTED)
        try:
            _run("--strip-lastmod", f.name)
            self.assertEqual(_lastmods(f.name), [None, None, None])
        finally:
            Path(f.name).unlink()

    def test_idempotent(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
            f.write(UNSORTED)
        try:
            _run(f.name)
            first = Path(f.name).read_text()
            _run(f.name)
            second = Path(f.name).read_text()
            self.assertEqual(first, second)
        finally:
            Path(f.name).unlink()


if __name__ == "__main__":
    unittest.main()
