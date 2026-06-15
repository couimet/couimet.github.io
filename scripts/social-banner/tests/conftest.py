import os
import shutil
from pathlib import Path

from PIL import Image, ImageChops, ImageStat

FIXTURES_DIR = Path(__file__).parent / "fixtures"
GOLDEN_DIR = Path(__file__).parent / "golden"


def assert_matches_golden(actual_path, golden_path, threshold=10.0):
    # UPDATE_GOLDEN=1 promotes the actual output to the new golden. Used when
    # the banner design intentionally changes; never set in CI.
    if os.environ.get("UPDATE_GOLDEN"):
        golden_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(actual_path, golden_path)
        return
    actual = Image.open(actual_path).convert("RGB")
    golden = Image.open(golden_path).convert("RGB")
    assert actual.size == golden.size, f"size mismatch: {actual.size} vs {golden.size}"
    diff = ImageChops.difference(actual, golden)
    rms_per_channel = ImageStat.Stat(diff).rms
    assert all(c <= threshold for c in rms_per_channel), (
        f"RMS per channel {rms_per_channel} exceeds threshold {threshold}"
    )
