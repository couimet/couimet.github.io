#!/usr/bin/env bash
# Run this script ON your server after SSH-ing in.
# It mirrors the live couimet.github.io site to your ouimet.info web root,
# creating a compressed backup first so you can roll back if needed.
#
# To download this script directly on the server:
#   wget -O sync-ouimet-info.sh https://raw.githubusercontent.com/couimet/couimet.github.io/main/scripts/sync-ouimet-info.sh && chmod +x sync-ouimet-info.sh
#
# Safe for existing server-only directories: wget only downloads files from the
# source and never deletes anything. Other files and folders are left untouched.
set -euo pipefail

REMOTE_PATH="$HOME/ouimet_info"
BACKUP_DIR="$HOME/ouimet_info_backups"
BACKUP_FILE="$BACKUP_DIR/$(date +%Y%m%d-%H%M%S).tar.gz"

mkdir -p "$BACKUP_DIR"

echo "==> Backing up current site to $BACKUP_FILE"
tar -czf "$BACKUP_FILE" -C "$HOME" ouimet_info
echo "    Backup created. To roll back:"
echo "    rm -rf $REMOTE_PATH && mkdir $REMOTE_PATH && tar -xzf $BACKUP_FILE -C $HOME"
echo ""

echo "==> Mirroring couimet.github.io into $REMOTE_PATH"
wget \
  --mirror \
  --page-requisites \
  --no-parent \
  --no-host-directories \
  --directory-prefix="$REMOTE_PATH" \
  --quiet \
  --show-progress \
  https://couimet.github.io/

echo ""
echo "==> Done. ouimet.info web root is now up to date."
echo "    Backup kept at: $BACKUP_FILE"
