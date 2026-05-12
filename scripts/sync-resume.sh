#!/usr/bin/env bash
set -euo pipefail

# Convert resume.json (JSON Resume) → resume.yml (YAMLResume) → resume-full.html
# Usage: ./scripts/sync-resume.sh
# Requires: Docker

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "==> Converting resume.json → resume.yml (json2yamlresume)"
docker run --rm -t \
  --user "$(id -u):$(id -g)" \
  -e HOME=/tmp \
  -v "$REPO_ROOT:/work" \
  -w /work \
  node:22-alpine \
  sh -c "echo '  → Running json2yamlresume...' && npx --yes json2yamlresume@0.12.3 resume.json resume.yml"

echo "==> Building resume-full.html (yamlresume)"
docker run --rm -t \
  --user "$(id -u):$(id -g)" \
  -e HOME=/tmp \
  -v "$REPO_ROOT:/work" \
  -w /work \
  node:22-alpine \
  sh -c "echo '  → Running yamlresume build...' && npx --yes yamlresume@0.12.3 build resume.yml --no-pdf -o /tmp/out && cp /tmp/out/resume.html resume-full.html"

echo "==> Done: resume.yml and resume-full.html generated"
