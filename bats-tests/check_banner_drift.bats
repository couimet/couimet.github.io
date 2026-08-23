#!/usr/bin/env bats

# Tests for scripts/social-banner/check_banner_drift.py

setup() {
  REPO_ROOT="$(cd "$(dirname "$BATS_TEST_DIRNAME")" && pwd)"
  CHECK_SCRIPT="$REPO_ROOT/scripts/social-banner/check_banner_drift.py"
  PYTHON="uv run --project $REPO_ROOT python"

  WORK="$BATS_TEST_TMPDIR/repo"
  mkdir -p "$WORK/img"
  cd "$WORK"
  git init -q
  git config user.email "bats@example.com"
  git config user.name "BATS"
  git config commit.gpgsign false
}

# --- Helpers ---

# Write an 8x8 JPEG. "baseline" and "progressive" encode the same pixels to
# different bytes, mimicking the macOS-vs-Linux encoder drift seen in CI.
make_jpeg() {
  local path="$1" mode="$2" colour="$3"
  $PYTHON - "$path" "$mode" "$colour" <<'PYEOF'
import sys
from PIL import Image

path, mode, colour = sys.argv[1:4]
Image.new("RGB", (8, 8), colour).save(
    path, "JPEG", quality=92, progressive=(mode == "progressive")
)
PYEOF
}

commit_banner() {
  make_jpeg "img/social-banner.jpg" baseline red
  git add img
  git commit -qm "add banner"
}

run_check() {
  run $PYTHON "$CHECK_SCRIPT"
}

# --- Tests ---

@test "reverts a banner with identical pixels despite byte drift" {
  commit_banner
  make_jpeg "img/social-banner.jpg" progressive red

  run_check
  [ "$status" -eq 0 ]
  [[ "$output" == *"reverted (pixels match HEAD): img/social-banner.jpg"* ]]
  [ -z "$(git status --porcelain img/)" ]
}

@test "reverts a banner whose pixels differ only within tolerance" {
  commit_banner
  # One pixel off by 1 in one channel — far below the RMS threshold.
  $PYTHON - "img/social-banner.jpg" <<'PYEOF'
import sys
from PIL import Image

path = sys.argv[1]
im = Image.open(path)
im.putpixel((0, 0), (254, 0, 0))
im.save(path, "JPEG", quality=92)
PYEOF

  run_check
  [ "$status" -eq 0 ]
  [[ "$output" == *"reverted (pixels match HEAD): img/social-banner.jpg"* ]]
  [ -z "$(git status --porcelain img/)" ]
}

@test "leaves a banner with genuinely different pixels in place" {
  commit_banner
  make_jpeg "img/social-banner.jpg" baseline blue

  run_check
  [ "$status" -eq 0 ]
  [[ "$output" == *"left as-is (pixels differ from HEAD): img/social-banner.jpg"* ]]
  [[ "$(git status --porcelain img/)" == *" M img/social-banner.jpg"* ]]
}

@test "reverts drifted banners while real drift stays flagged" {
  make_jpeg "img/social-banner.jpg" baseline red
  make_jpeg "img/social-banner-rangelink.jpg" baseline red
  git add img
  git commit -qm "add banners"

  make_jpeg "img/social-banner.jpg" progressive red
  make_jpeg "img/social-banner-rangelink.jpg" baseline blue

  run_check
  [ "$status" -eq 0 ]
  [[ "$output" == *"reverted (pixels match HEAD): img/social-banner.jpg"* ]]
  [[ "$output" == *"left as-is (pixels differ from HEAD): img/social-banner-rangelink.jpg"* ]]
  [[ "$(git status --porcelain img/)" == *" M img/social-banner-rangelink.jpg"* ]]
  [[ "$(git status --porcelain img/)" != *"social-banner.jpg"* ]]
}

@test "leaves untracked banners alone" {
  commit_banner
  make_jpeg "img/social-banner-extra.jpg" baseline green

  run_check
  [ "$status" -eq 0 ]
  [[ "$output" == *"left as-is (not in HEAD): img/social-banner-extra.jpg"* ]]
  [[ "$(git status --porcelain img/)" == *"?? img/social-banner-extra.jpg"* ]]
}
