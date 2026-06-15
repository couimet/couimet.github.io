#!/usr/bin/env python3
"""Sort <url> blocks in a sitemap.xml by their <loc> text.

Jekyll doesn't guarantee page enumeration order, so the sitemap can produce
<url> blocks in different orders on different machines. Sorting them makes
the output deterministic for git diff.

Usage: python3 scripts/sort-sitemap.py <path-to-sitemap.xml>
"""

import sys
import xml.etree.ElementTree as ET


def sort_sitemap(path):
    ET.register_namespace("", "http://www.sitemaps.org/schemas/sitemap/0.9")
    tree = ET.parse(path)
    root = tree.getroot()
    ns = "http://www.sitemaps.org/schemas/sitemap/0.9"
    urls = root.findall(f"{{{ns}}}url")
    urls.sort(key=lambda u: u.findtext(f"{{{ns}}}loc") or "")
    root.clear()
    root.extend(urls)
    ET.indent(tree, space="  ")
    tree.write(path, encoding="UTF-8", xml_declaration=True)


if __name__ == "__main__":
    sort_sitemap(sys.argv[1])
