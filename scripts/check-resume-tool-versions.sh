#!/usr/bin/env bash
set -euo pipefail

# Check whether the pinned json2yamlresume / yamlresume versions in
# resume-tools.versions are still current on npm. On PR/feature branches (any
# GITHUB_REF_NAME other than main) a newer version is a hard error (exit 1) so
# stale pins surface during review. On main it is a non-blocking warning
# (exit 0) so a stale pin never blocks post-merge deploys.
#
# npm unreachable → exit 0 (graceful fallback, not a hard block)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Pinned versions come from the same file sync-resume.sh sources.
source "$SCRIPT_DIR/../resume-tools.versions"

echo "==> Checking for newer tool versions..."

LATEST_J2Y=$(npm --fetch-retries=0 --fetch-timeout=10000 view json2yamlresume version 2>/dev/null || echo "unknown")

if [ "$LATEST_J2Y" != "unknown" ] && [ "$LATEST_J2Y" != "$PINNED_J2Y_VERSION" ]; then
  if [ "${GITHUB_REF_NAME:-}" = "main" ]; then
    echo "WARNING: json2yamlresume is pinned at $PINNED_J2Y_VERSION but $LATEST_J2Y is available on main."
    echo "WARNING: This is not blocking the deploy. Bump the pin in resume-tools.versions via a PR."
  else
    echo "ERROR: json2yamlresume is pinned at $PINNED_J2Y_VERSION but $LATEST_J2Y is available."
    echo "Update PINNED_J2Y_VERSION in resume-tools.versions after verifying compatibility:"
    echo "  https://www.npmjs.com/package/json2yamlresume"
    exit 1
  fi
fi

LATEST_YR=$(npm --fetch-retries=0 --fetch-timeout=10000 view yamlresume version 2>/dev/null || echo "unknown")

if [ "$LATEST_YR" != "unknown" ] && [ "$LATEST_YR" != "$PINNED_YR_VERSION" ]; then
  if [ "${GITHUB_REF_NAME:-}" = "main" ]; then
    echo "WARNING: yamlresume is pinned at $PINNED_YR_VERSION but $LATEST_YR is available on main."
    echo "WARNING: This is not blocking the deploy. Bump the pin in resume-tools.versions via a PR."
  else
    echo "ERROR: yamlresume is pinned at $PINNED_YR_VERSION but $LATEST_YR is available."
    echo "Update PINNED_YR_VERSION in resume-tools.versions after verifying compatibility:"
    echo "  https://www.npmjs.com/package/yamlresume"
    exit 1
  fi
fi

echo "  → json2yamlresume pinned at $PINNED_J2Y_VERSION, latest is $LATEST_J2Y"
echo "  → yamlresume pinned at $PINNED_YR_VERSION, latest is $LATEST_YR"
