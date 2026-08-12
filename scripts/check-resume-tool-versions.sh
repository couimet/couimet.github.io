#!/usr/bin/env bash
set -euo pipefail

# Check whether pinned json2yamlresume / yamlresume versions in scripts/sync-resume.sh
# are still current on npm. Exits 1 when a newer version is available so CI can catch
# stale pins on PRs before they block post-merge deploys.
#
# npm unreachable → exit 0 (graceful fallback, not a hard block)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SYNC_SCRIPT="$SCRIPT_DIR/sync-resume.sh"

PINNED_J2Y_VERSION=$(sed -n 's/^PINNED_J2Y_VERSION="\([^"]*\)".*/\1/p' "$SYNC_SCRIPT")
PINNED_YR_VERSION=$(sed -n 's/^PINNED_YR_VERSION="\([^"]*\)".*/\1/p' "$SYNC_SCRIPT")

echo "==> Checking for newer tool versions..."

LATEST_J2Y=$(npm --fetch-retries=0 --fetch-timeout=10000 view json2yamlresume version 2>/dev/null || echo "unknown")

if [ "$LATEST_J2Y" != "unknown" ] && [ "$LATEST_J2Y" != "$PINNED_J2Y_VERSION" ]; then
  echo "ERROR: json2yamlresume is pinned at $PINNED_J2Y_VERSION but $LATEST_J2Y is available."
  echo "Update PINNED_J2Y_VERSION in scripts/sync-resume.sh after verifying compatibility:"
  echo "  https://www.npmjs.com/package/json2yamlresume"
  exit 1
fi

LATEST_YR=$(npm --fetch-retries=0 --fetch-timeout=10000 view yamlresume version 2>/dev/null || echo "unknown")

if [ "$LATEST_YR" != "unknown" ] && [ "$LATEST_YR" != "$PINNED_YR_VERSION" ]; then
  echo "ERROR: yamlresume is pinned at $PINNED_YR_VERSION but $LATEST_YR is available."
  echo "Update PINNED_YR_VERSION in scripts/sync-resume.sh after verifying compatibility:"
  echo "  https://www.npmjs.com/package/yamlresume"
  exit 1
fi

echo "  → json2yamlresume pinned at $PINNED_J2Y_VERSION, latest is $LATEST_J2Y"
echo "  → yamlresume pinned at $PINNED_YR_VERSION, latest is $LATEST_YR"
