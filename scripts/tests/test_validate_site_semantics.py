"""Tests for validate-site-semantics.py (the built-site validator)."""

import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent


def _load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


site_semantics = _load("validate-site-semantics")

PAGE = """\
<!doctype html>
<html><head>
<title>{title}</title>
<meta property="og:description" content="{description}">
</head></html>
"""

REDIRECT_PAGE = """\
<!doctype html>
<html><head>
<meta name="robots" content="noindex">
<meta http-equiv="refresh" content="0; url={url}">
<title>{title}</title>
<meta property="og:description" content="{description}">
</head></html>
"""


class CheckDuplicateMetaTest(unittest.TestCase):
    def _write(self, root: Path, rel: str, content: str) -> None:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def _run(self, root: Path) -> list[str]:
        failures: list[str] = []
        site_semantics.check_duplicate_meta(root, failures)
        return failures

    def test_duplicate_meta_on_real_pages_is_flagged(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ("a.html", "b.html"):
                self._write(
                    root, name, PAGE.format(title="Same", description="Same desc")
                )
            failures = self._run(root)
            self.assertIn("duplicate title 'Same' on pages: a.html, b.html", failures)
            self.assertIn(
                "duplicate og:description 'Same desc' on pages: a.html, b.html",
                failures,
            )

    def test_redirect_stubs_share_meta_without_failing(self):
        # /s/<ID> share pages are noindex redirect stubs; a same_as alias may
        # reuse its target entry's title/description (e.g. the kn/lk pair).
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write(
                root,
                "a.html",
                PAGE.format(title="Same", description="Same desc"),
            )
            for name in ("s/kn.html", "s/lk.html"):
                self._write(
                    root,
                    name,
                    REDIRECT_PAGE.format(
                        url="/#anchor", title="Same", description="Same desc"
                    ),
                )
            self.assertEqual(self._run(root), [])

    def test_unique_meta_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write(root, "a.html", PAGE.format(title="One", description="D1"))
            self._write(root, "b.html", PAGE.format(title="Two", description="D2"))
            self.assertEqual(self._run(root), [])


if __name__ == "__main__":
    unittest.main()
