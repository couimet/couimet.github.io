"""Generate share-page social banners (img/social/<ID>.jpg).

Reads the short-URL registry in _data/short-urls.yml and composites a
banner per regular (non-alias) entry. A share that targets a project page
(/projects/<slug>.html) whose front matter declares its own custom social
banner reuses that project's icon and banner title/subtitle, with the
entry's bannertagline as the drawn tagline and an optional per-entry
bannersubtitle overriding the project's own subtitle; every other share
gets the default personal card (site face photo with name / title /
tagline). The
registry is the single source of truth; s/<ID>.md share pages mirror it
(validate-short-urls.py enforces the agreement), and banners are drawn
straight from each entry.
"""

import re
import sys
from pathlib import Path

import settings as cfg
import utils as util
import yaml
from generate import cropped_face, load_bio
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
BIO_PATH = REPO_ROOT / "_data" / "bio.json"
REGISTRY_PATH = REPO_ROOT / "_data" / "short-urls.yml"
OUT_DIR = REPO_ROOT / "img" / "social"

# A registry redirect_to of the form /projects/<slug>.html[#anchor] points at
# a Jekyll project page; the matching projects/<slug>.md may carry its own
# social banner front matter (banner fields plus an icon URL).
PROJECT_PAGE_RE = re.compile(r"^/projects/([A-Za-z0-9._-]+)\.html(?:#.*)?$")
PROJECT_DIR = REPO_ROOT / "projects"
ICON_URL_KEYS = ("sourceiconurl", "logourl", "iconurl")


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


def project_banner_meta(entry, project_dir=PROJECT_DIR):
    """Return the project front matter when *entry* targets a project page
    that declares its own custom social banner, else None.

    The redirect_to form /projects/<slug>.html[#anchor] maps to
    projects/<slug>.md under *project_dir*; a project counts as
    banner-carrying when it declares an icon URL and a banner
    title/subtitle. Shares targeting any other path (career changelog
    anchors, home aliases) draw the default personal card.
    """
    match = PROJECT_PAGE_RE.match(entry["redirect_to"])
    if not match:
        return None
    project_file = project_dir / f"{match.group(1)}.md"
    if not project_file.exists():
        return None
    meta = util.load_project_meta(project_file)
    has_icon = any(meta.get(key) for key in ICON_URL_KEYS)
    has_banner = "bannertitle" in meta or "bannersubtitle" in meta
    if not (has_icon and has_banner):
        return None
    return meta


def project_share_meta(entry, project_meta):
    """Build the banner metadata for a project-branded share entry.

    The title comes from the project's own banner (its identity); the subtitle
    defaults to the project's subtitle but a localized entry may override it
    with its own bannersubtitle, so the per-locale share line can render in
    the share's own language while the untranslated brand title stays put. The
    drawn tagline is the entry's bannertagline, which defaults to the entry
    title, so the per-template share line differentiates the banners.
    """
    meta = dict(project_meta)
    meta["bannertagline"] = entry.get("bannertagline") or entry["title"]
    if entry.get("bannersubtitle"):
        meta["bannersubtitle"] = entry["bannersubtitle"]
    return meta


def project_icon(meta):
    """Return the project banner icon sized for the share banner.

    A repo-local path (leading '/') is opened from disk untrimmed, matching
    generate_network_nudge; a remote http(s) icon is downloaded and trimmed
    to its content box, matching generate_rabbit_maximizer/generate_rangelink.
    """
    for key in ICON_URL_KEYS:
        url = meta.get(key)
        if not url:
            continue
        if url.startswith("/"):
            path = REPO_ROOT / url.lstrip("/")
            if not path.exists():
                print(f"Icon not found: {path}", file=sys.stderr)
                sys.exit(1)
            icon = Image.open(path).convert("RGBA")
            return util.sized_icon(icon, cfg.ICON_SIZE)
        icon = util.download_icon(url)
        return util.sized_icon(util.trim_to_content(icon), cfg.ICON_SIZE)
    print("No icon URL found in project front matter", file=sys.stderr)
    sys.exit(1)


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
        out_path = OUT_DIR / f"{share_id}.jpg"
        project_meta = project_banner_meta(entry)
        if project_meta is None:
            meta = share_meta(entry, bio)
            left_icon = icon
        else:
            meta = project_share_meta(entry, project_meta)
            left_icon = project_icon(project_meta)
        util.compose_banner(meta, left_icon, out_path)


if __name__ == "__main__":
    main()
