"""Generate share-page social banners (img/social/<ID>.jpg).

Reads the short-URL registry in _data/short-urls.yml and composites the
site face photo on the left with name / title / tagline text on the right,
reusing the default banner's palette and layout grid. The registry is the
single source of truth; s/<ID>.md share pages mirror it (validate-short-urls.py
enforces the agreement), and banners are drawn straight from each entry.
"""

import sys
from pathlib import Path

import settings as cfg
import utils as util
import yaml
from generate import cropped_face, load_bio

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
BIO_PATH = REPO_ROOT / "_data" / "bio.json"
REGISTRY_PATH = REPO_ROOT / "_data" / "short-urls.yml"
OUT_DIR = REPO_ROOT / "img" / "social"


def load_registry(path):
    """Load the short-URL registry as an ID -> entry dict."""
    with open(path) as f:
        return yaml.safe_load(f) or {}


def share_meta(entry, bio):
    """Build banner metadata from one registry entry.

    bannertitle/bannersubtitle default to the site name and label from
    bio.json so a share banner matches the default banner; a share that
    wants to diverge can set either via the registry later. bannertagline
    falls back to the entry title.
    """
    meta = dict(entry)
    meta.setdefault("bannertitle", bio["name"])
    meta.setdefault("bannersubtitle", bio["label"])
    meta.setdefault("bannertagline", entry["title"])
    return meta


def main():
    bio = load_bio(BIO_PATH)
    picture = bio.get("picture")
    if not picture:
        print("Missing 'picture' in bio.json basics", file=sys.stderr)
        sys.exit(1)
    face_abs = REPO_ROOT / picture.lstrip("/")
    if not face_abs.exists():
        print(f"Face photo not found: {face_abs}", file=sys.stderr)
        sys.exit(1)

    registry = load_registry(REGISTRY_PATH)
    if not registry:
        print(f"No entries in registry: {REGISTRY_PATH}", file=sys.stderr)
        sys.exit(1)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    icon = cropped_face(str(face_abs), cfg.ICON_SIZE)

    for share_id in sorted(registry):
        entry = registry[share_id]
        if "same_as" in entry:
            # Aliases reuse the target entry's banner; only banner owners
            # get a file (validate-short-urls.py resolves og_image to the
            # same_as target).
            continue
        meta = share_meta(entry, bio)
        out_path = OUT_DIR / f"{share_id}.jpg"
        util.compose_banner(meta, icon, out_path)


if __name__ == "__main__":
    main()
