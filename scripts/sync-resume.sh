#!/usr/bin/env bash
set -euo pipefail

# Convert resume.json (JSON Resume) → resume.yml (YAMLResume) → resume-full.html
# Usage: ./scripts/sync-resume.sh
# Requires: Docker

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PINNED_J2Y_VERSION="0.13.1"
PINNED_YR_VERSION="0.13.1"

echo "==> Checking for newer tool versions..."

LATEST_J2Y=$(npm view json2yamlresume version 2>/dev/null || echo "unknown")
LATEST_YR=$(npm view yamlresume version 2>/dev/null || echo "unknown")

if [ "$LATEST_J2Y" != "unknown" ] && [ "$LATEST_J2Y" != "$PINNED_J2Y_VERSION" ]; then
  echo "ERROR: json2yamlresume is pinned at $PINNED_J2Y_VERSION but $LATEST_J2Y is available."
  echo "Update PINNED_J2Y_VERSION in scripts/sync-resume.sh after verifying compatibility:"
  echo "  https://www.npmjs.com/package/json2yamlresume"
  exit 1
fi

if [ "$LATEST_YR" != "unknown" ] && [ "$LATEST_YR" != "$PINNED_YR_VERSION" ]; then
  echo "ERROR: yamlresume is pinned at $PINNED_YR_VERSION but $LATEST_YR is available."
  echo "Update PINNED_YR_VERSION in scripts/sync-resume.sh after verifying compatibility:"
  echo "  https://www.npmjs.com/package/yamlresume"
  exit 1
fi

echo "==> Converting resume.json → resume.yml (json2yamlresume)"
docker run --rm -t \
  --user "$(id -u):$(id -g)" \
  -e HOME=/tmp \
  -v "$REPO_ROOT:/work" \
  -w /work \
  node:22-alpine \
  sh -c "echo '  → Running json2yamlresume...' && npx --yes json2yamlresume@$PINNED_J2Y_VERSION resume.json resume.yml && echo '  → Patching country code for yamlresume compatibility...' && sed -i 's/^    country: CA$/    country: Canada/' resume.yml"

echo "==> Building resume-full.html (yamlresume)"
docker run --rm -t \
  --user "$(id -u):$(id -g)" \
  -e HOME=/tmp \
  -v "$REPO_ROOT:/work" \
  -w /work \
  node:22-alpine \
  sh -c "echo '  → Running yamlresume build...' && npx --yes yamlresume@$PINNED_YR_VERSION build resume.yml --no-pdf -o /tmp/out && cp /tmp/out/resume.html resume-full.html"

echo "==> Done: resume.yml and resume-full.html generated"
