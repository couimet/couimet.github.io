#!/usr/bin/env bash
set -euo pipefail

# Convert resume.json (JSON Resume) → resume.yml (YAMLResume) → resume-full.html
# Usage: ./scripts/sync-resume.sh
# Requires: Docker (required), npm (optional, for version-check; skipped gracefully if absent)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PINNED_J2Y_VERSION="0.14.2"
PINNED_YR_VERSION="0.14.2"

if [ "${SKIP_VERSION_CHECK:-}" = "true" ]; then
  echo "==> Skipping version check (SKIP_VERSION_CHECK=true)"
else
  "$SCRIPT_DIR/check-resume-tool-versions.sh"
fi

echo "==> Converting resume.json → resume.yml (json2yamlresume)"
docker run --rm -t \
  -e HOST_UID="$(id -u)" \
  -e HOST_GID="$(id -g)" \
  -e HOME=/tmp \
  -v "$REPO_ROOT:/work" \
  -w /work \
  node:22-alpine \
  sh -c "apk add --no-cache jq >/dev/null 2>&1 && \
    echo '  → Stripping internal-only fields...' && \
    jq 'del(.basics.keywordSubTag) | walk(if type == \"object\" then with_entries(select(.key | startswith(\"docx\") | not)) else . end)' resume.json > /tmp/clean-resume.json && \
    echo '  → Running json2yamlresume...' && \
    npx --yes json2yamlresume@$PINNED_J2Y_VERSION /tmp/clean-resume.json resume.yml && \
    echo '  → Patching country code for yamlresume compatibility...' && \
    sed -i 's/^    country: CA$/    country: Canada/' resume.yml && \
    chown \$HOST_UID:\$HOST_GID resume.yml"

echo "==> Building resume-full.html (yamlresume)"
docker run --rm -t \
  -e HOST_UID="$(id -u)" \
  -e HOST_GID="$(id -g)" \
  -e HOME=/tmp \
  -v "$REPO_ROOT:/work" \
  -w /work \
  node:22-alpine \
  sh -c "echo '  → Running yamlresume build...' && npx --yes yamlresume@$PINNED_YR_VERSION build resume.yml --no-pdf -o /tmp/out && cp /tmp/out/resume.html resume-full.html && chown \$HOST_UID:\$HOST_GID resume-full.html"

echo "==> Done: resume.yml and resume-full.html generated"
