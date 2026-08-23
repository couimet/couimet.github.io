"""Validate featured-in anchor uniqueness across articles and promotions."""

import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
ARTICLES = REPO_ROOT / "_data" / "articles.yml"
PROMOTIONS = REPO_ROOT / "_data" / "promotions.yml"


def find_duplicate_featured_anchors(articles, promotions):
    """Return (anchor, sorted_projects) collisions, sorted by anchor.

    An article and a promotion sharing an anchor and a project render two
    elements with the same id="featured-in-<anchor>" on that project page
    (project-featured-in.html), which breaks the deep-link pulse and share
    buttons for the second line; per-file uniqueness is already enforced by
    the sibling validators, so only this cross-file case needs checking here.
    Entries without projects never render on a project page, so they cannot
    collide and are skipped.
    """
    article_anchors = {}
    for item in articles:
        anchor = item.get("anchor") if isinstance(item, dict) else None
        projects = item.get("projects") if isinstance(item, dict) else None
        if anchor and projects:
            article_anchors[anchor] = set(projects)

    promo_anchors = {}
    for item in promotions:
        anchor = item.get("anchor") if isinstance(item, dict) else None
        projects = item.get("projects") if isinstance(item, dict) else None
        if anchor and projects:
            promo_anchors[anchor] = set(projects)

    collisions = []
    for anchor in sorted(article_anchors.keys() & promo_anchors.keys()):
        overlapping = sorted(article_anchors[anchor] & promo_anchors[anchor])
        if overlapping:
            collisions.append((anchor, overlapping))
    return collisions


def main():
    for path, label in ((ARTICLES, "Articles"), (PROMOTIONS, "Promotions")):
        if not path.exists():
            print(f"ERROR: {label} not found: {path}", file=sys.stderr)
            sys.exit(1)

    with open(ARTICLES) as f:
        articles = yaml.safe_load(f)
    with open(PROMOTIONS) as f:
        promotions = yaml.safe_load(f)

    collisions = find_duplicate_featured_anchors(articles, promotions)
    if collisions:
        for anchor, projects in collisions:
            print(
                f"ERROR: duplicate featured-in anchor '{anchor}' on project(s): {', '.join(projects)}",
                file=sys.stderr,
            )
        sys.exit(1)

    print("OK: featured-in anchors are unique per project page")


if __name__ == "__main__":
    main()
