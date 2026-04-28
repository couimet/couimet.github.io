#!/usr/bin/env bash
# Run this script ON your server after SSH-ing in.
# It downloads the latest site.zip from the GitHub Release for this repo and
# extracts it into the ouimet.info web root, creating a compressed backup first.
# Files not in the zip (charles/, sarah/, .htaccess) are left untouched.
#
# To download this script directly on the server:
#   wget -O sync-ouimet-info.sh https://raw.githubusercontent.com/couimet/couimet.github.io/main/scripts/sync-ouimet-info.sh && chmod +x sync-ouimet-info.sh
set -euo pipefail

REMOTE_PATH="$HOME/ouimet_info"
BACKUP_DIR="$HOME/ouimet_info_backups"
BACKUP_FILE="$BACKUP_DIR/$(date +%Y%m%d-%H%M%S).tar.gz"
ZIP_TMP="/tmp/ouimet_info_site.zip"
RELEASE_URL="https://github.com/couimet/couimet.github.io/releases/latest/download/site.zip"

mkdir -p "$BACKUP_DIR"

BACKUP_PARENT="$(dirname "$REMOTE_PATH")"
BACKUP_NAME="$(basename "$REMOTE_PATH")"

if [[ -d "$REMOTE_PATH" ]]; then
  echo "==> Backing up current site to $BACKUP_FILE"
  tar -czf "$BACKUP_FILE" -C "$BACKUP_PARENT" "$BACKUP_NAME"
  echo "    Backup created. To roll back:"
  echo "    rm -rf \"$REMOTE_PATH\" && tar -xzf \"$BACKUP_FILE\" -C \"$BACKUP_PARENT\""
else
  echo "==> No existing site at $REMOTE_PATH; skipping backup (first run)"
  mkdir -p "$REMOTE_PATH"
fi
echo ""

echo "==> Downloading latest site build"
wget -q --show-progress -O "$ZIP_TMP" "$RELEASE_URL"

echo "==> Extracting into $REMOTE_PATH"
unzip -o "$ZIP_TMP" -d "$REMOTE_PATH"
rm "$ZIP_TMP"

echo ""
echo "==> Done. ouimet.info web root is now up to date."
echo "    Backup kept at: $BACKUP_FILE"
