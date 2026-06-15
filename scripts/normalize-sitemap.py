#!/usr/bin/env python3
"""Normalize a sitemap.xml for deterministic git tracking and comparison.

- Sorts <url> blocks by <loc> (Jekyll doesn't guarantee enumeration order).
- Strips namespace clutter (xmlns:xsi, xsi:schemaLocation).
- Optionally strips <lastmod> for comparison (--strip-lastmod).

The snapshot keeps <lastmod> so the tracked file reflects the real output shape.
CI verification strips it from both sides before diffing since filesystem mtime
varies between machines.

Usage:
  python3 scripts/normalize-sitemap.py <path>                 # sort, keep lastmod
  python3 scripts/normalize-sitemap.py --strip-lastmod <path> # sort, strip lastmod
"""

import argparse
import xml.etree.ElementTree as ET

NS = "http://www.sitemaps.org/schemas/sitemap/0.9"


def normalize(path, strip_lastmod=False):
    ET.register_namespace("", NS)
    tree = ET.parse(path)
    root = tree.getroot()
    urls = root.findall(f"{{{NS}}}url")
    urls.sort(key=lambda u: u.findtext(f"{{{NS}}}loc") or "")
    if strip_lastmod:
        for url in urls:
            for lm in url.findall(f"{{{NS}}}lastmod"):
                url.remove(lm)
    root.clear()
    root.extend(urls)
    ET.indent(tree, space="  ")
    tree.write(path, encoding="UTF-8", xml_declaration=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--strip-lastmod", action="store_true")
    parser.add_argument("path")
    args = parser.parse_args()
    normalize(args.path, strip_lastmod=args.strip_lastmod)
