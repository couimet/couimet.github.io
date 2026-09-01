"""Normalize cross-platform JPEG encoder drift in generated social banners.

Banner JPEGs are committed to the repo but generated with Pillow on the
developer's machine (macOS). CI regenerates them on Linux, and the two
JPEG encoders emit different bytes for the same pixels, so the repo-root
`check-generated` CI job would see false drift on every run.

Runs as that job's post-generate hook, after `make banner` and before the
git drift check.
"""

import io
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageStat
from settings import GOLDEN_RMS_THRESHOLD


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=repo, check=True, capture_output=True, text=True
    )
    return result.stdout


def repo_root() -> Path:
    return Path(git(Path.cwd(), "rev-parse", "--show-toplevel").strip())


def head_bytes(repo: Path, relpath: str) -> bytes | None:
    """Committed bytes of relpath, or None when HEAD has no such file."""
    result = subprocess.run(
        ["git", "show", f"HEAD:{relpath}"], cwd=repo, capture_output=True, check=False
    )
    if result.returncode != 0:
        return None
    return result.stdout


def pixels_match(working: bytes, committed: bytes) -> bool:
    """True when both JPEGs decode to the same RGB pixels within tolerance."""
    with (
        Image.open(io.BytesIO(working)) as working_im,
        Image.open(io.BytesIO(committed)) as committed_im,
    ):
        if working_im.size != committed_im.size:
            return False
        diff = ImageChops.difference(
            working_im.convert("RGB"), committed_im.convert("RGB")
        )
        rms_per_channel = ImageStat.Stat(diff).rms
        return all(channel <= GOLDEN_RMS_THRESHOLD for channel in rms_per_channel)


def main() -> int:
    repo = repo_root()
    banner_paths = sorted((repo / "img").glob("social-banner*.jpg"))
    share_paths = sorted((repo / "img" / "social").glob("*.jpg"))
    for path in banner_paths + share_paths:
        relpath = path.relative_to(repo).as_posix()
        committed = head_bytes(repo, relpath)
        if committed is None:
            print(f"left as-is (not in HEAD): {relpath}")
            continue
        try:
            match = pixels_match(path.read_bytes(), committed)
        except (OSError, ValueError):
            # An undecodable file means real drift; leave it for git to flag.
            match = False
        if match:
            git(repo, "checkout", "--", relpath)
            print(f"reverted (pixels match HEAD): {relpath}")
        else:
            print(f"left as-is (pixels differ from HEAD): {relpath}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
